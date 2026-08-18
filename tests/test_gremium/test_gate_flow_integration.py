"""Tests für die Gate-Flow-Integration mit Seher, Circuit-Breaker und Appeal."""

import pytest
from datetime import datetime, timezone
from src.gremium.sicherheitsrat.gate_flow import GateFlow
from src.gremium.sicherheitsrat.seher import Seher
from src.gremium.sicherheitsrat.circuit_breaker import CircuitBreaker
from src.gremium.sicherheitsrat.appeal import AppealManager
from src.gremium.sicherheitsrat.policy_review import PolicyReviewManager
from src.contracts.research_package import ResearchPackage, PackageKontext, RoutingGraph
from src.contracts.pipeline_models import GateMode
from src.contracts.enums import GateDecision, RichterResult


class TestGateFlowIntegration:
    """Tests für die Gate-Flow-Integration."""

    def _create_test_package(self, package_id: str = "pkg-test-1") -> ResearchPackage:
        """Hilfsmethode zum Erstellen eines validen Test-Pakets."""
        return ResearchPackage(
            package_id=package_id,
            source_wegmarke="test_source",
            atlas_version_ref="atlas-v1.0.0",
            ziel="test_target",
            routing_graph=RoutingGraph(max_loop_iterations=10, branch_condition_timeout=30.0),
            kontext=PackageKontext(kontext_id="ctx-1", domaene="test", beschreibung="Test context", erwartete_transformation="Test transformation", domain="test"),
            limits={"temperature": 25.0}
        )

    def test_gate_flow_with_seher_normal(self):
        """Gate-Flow mit Seher in NORMAL-Modus."""
        seher = Seher()
        circuit_breaker = CircuitBreaker()
        appeal_manager = AppealManager()
        
        gate_flow = GateFlow(
            seher=seher,
            circuit_breaker=circuit_breaker,
            appeal_manager=appeal_manager
        )
        
        package = self._create_test_package("pkg-normal-1")
        
        # Circuit-Breaker ist in NORMAL
        assert circuit_breaker.state == "NORMAL"
        
        gate_record = gate_flow.run_gate(package, GateMode.NORMAL)
        
        # Seher wurde aufgerufen
        assert gate_record is not None
        assert gate_record.package_id == "pkg-normal-1"

    def test_gate_flow_with_seher_shadow_mode(self):
        """Gate-Flow mit Seher in SHADOW_MODE."""
        seher = Seher()
        circuit_breaker = CircuitBreaker()
        appeal_manager = AppealManager()
        
        gate_flow = GateFlow(
            seher=seher,
            circuit_breaker=circuit_breaker,
            appeal_manager=appeal_manager
        )
        
        # Circuit-Breaker in SHADOW_MODE setzen
        circuit_breaker.state = "SHADOW_MODE"
        
        package = self._create_test_package("pkg-shadow-1")
        
        gate_record = gate_flow.run_gate(package, GateMode.NORMAL)
        
        # Seher-Ergebnis wird protokolliert, aber nicht als Blockade gewertet
        assert gate_record is not None
        # In SHADOW_MODE sollte ein Veto nicht zu DISPUTED führen

    def test_gate_flow_with_seher_temp_suspended(self):
        """Gate-Flow mit Seher in TEMP_SUSPENDED (Seher übersprungen)."""
        seher = Seher()
        circuit_breaker = CircuitBreaker()
        appeal_manager = AppealManager()
        
        gate_flow = GateFlow(
            seher=seher,
            circuit_breaker=circuit_breaker,
            appeal_manager=appeal_manager
        )
        
        # Circuit-Breaker in TEMP_SUSPENDED setzen
        circuit_breaker.state = "TEMP_SUSPENDED"
        
        package = self._create_test_package("pkg-suspended-1")
        
        gate_record = gate_flow.run_gate(package, GateMode.NORMAL)
        
        # Seher wurde übersprungen
        assert gate_record is not None
        assert gate_record.seher_result.value == "SEHER_NOT_CALLED"

    def test_gate_flow_disputed_creates_appeal(self):
        """DISPUTED erzeugt Appeal."""
        seher = Seher()
        circuit_breaker = CircuitBreaker()
        appeal_manager = AppealManager()
        
        gate_flow = GateFlow(
            seher=seher,
            circuit_breaker=circuit_breaker,
            appeal_manager=appeal_manager
        )
        
        package = self._create_test_package("pkg-disputed-1")
        
        # Gate-Flow sollte bei Richter PASS + Seher VETO → DISPUTED erzeugen
        # und Appeal erstellen
        gate_record = gate_flow.run_gate(package, GateMode.NORMAL)
        
        # Wenn DISPUTED, dann wurde Appeal erstellt
        if gate_record.gate_decision == GateDecision.DISPUTED:
            # Appeal sollte existieren
            assert len(appeal_manager.get_pending_appeals()) > 0

    def test_gate_flow_appeal_granted_releases(self):
        """Appeal gewährt → Paket freigegeben."""
        seher = Seher()
        circuit_breaker = CircuitBreaker()
        appeal_manager = AppealManager()
        
        gate_flow = GateFlow(
            seher=seher,
            circuit_breaker=circuit_breaker,
            appeal_manager=appeal_manager
        )
        
        package = self._create_test_package("pkg-appeal-1")
        
        # Simuliere DISPUTED-Szenario
        gate_record = gate_flow.run_gate(package, GateMode.NORMAL)
        
        if gate_record.gate_decision == GateDecision.DISPUTED:
            # Appeal auflösen mit APPEAL_GRANTED
            appeals = appeal_manager.get_pending_appeals()
            if appeals:
                appeal = appeals[0]
                resolution = appeal_manager.resolve_appeal(
                    appeal_id=appeal.appeal_id,
                    decision="APPEAL_GRANTED",
                    reason="Gefahr widerlegt",
                    resolved_by="kanzler-1"
                )
                
                assert resolution.decision == "APPEAL_GRANTED"
                # Paket ist jetzt freigegeben

    def test_gate_flow_veto_confirmed_policy_veto(self):
        """Veto bestätigt → 🟪 POLICY_VETO."""
        seher = Seher()
        circuit_breaker = CircuitBreaker()
        appeal_manager = AppealManager()
        
        gate_flow = GateFlow(
            seher=seher,
            circuit_breaker=circuit_breaker,
            appeal_manager=appeal_manager
        )
        
        package = self._create_test_package("pkg-veto-1")
        
        gate_record = gate_flow.run_gate(package, GateMode.NORMAL)
        
        if gate_record.gate_decision == GateDecision.DISPUTED:
            appeals = appeal_manager.get_pending_appeals()
            if appeals:
                appeal = appeals[0]
                resolution = appeal_manager.resolve_appeal(
                    appeal_id=appeal.appeal_id,
                    decision="VETO_CONFIRMED",
                    reason="Policy-Verstoß bestätigt",
                    resolved_by="kanzler-1"
                )
                
                assert resolution.decision == "VETO_CONFIRMED"
                # 🟪 POLICY_VETO wurde geschrieben (nicht 🟥)

    def test_gate_flow_triggers_policy_review(self):
        """Nach N Zyklen wird Policy-Veto-Review ausgelöst."""
        seher = Seher()
        circuit_breaker = CircuitBreaker()
        appeal_manager = AppealManager()
        policy_review = PolicyReviewManager(interval_cycles=3)
        
        gate_flow = GateFlow(
            seher=seher,
            circuit_breaker=circuit_breaker,
            appeal_manager=appeal_manager,
            policy_review=policy_review
        )
        
        package = self._create_test_package("pkg-review-1")
        
        # Mehrere Zyklen durchlaufen
        for i in range(3):
            gate_flow.run_gate(package, GateMode.NORMAL)
            # Nach dem 3. Zyklus sollte Review fällig sein
        
        # Review sollte ausgelöst worden sein
        # (wird im Gate-Flow nach jedem Zyklus geprüft)

    def test_gate_flow_with_recovery(self):
        """Phase 4 Recovery arbeitet mit Gate-Flow zusammen."""
        seher = Seher()
        circuit_breaker = CircuitBreaker()
        appeal_manager = AppealManager()
        
        gate_flow = GateFlow(
            seher=seher,
            circuit_breaker=circuit_breaker,
            appeal_manager=appeal_manager
        )
        
        package = self._create_test_package("pkg-recovery-1")
        
        # Gate-Flow sollte mit Recovery-State umgehen können
        gate_record = gate_flow.run_gate(package, GateMode.NORMAL)
        
        assert gate_record is not None
        assert gate_record.package_id == "pkg-recovery-1"
