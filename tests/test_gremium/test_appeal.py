"""Tests für den Berufungsprozess (Appeal)."""

import pytest
from datetime import datetime, timezone
from src.gremium.sicherheitsrat.appeal import AppealManager, AppealDecision
from src.contracts.pipeline_models import SeherVeto
from src.contracts.enums import SeherDecision, RichterResult, AppealStatus


class TestAppeal:
    """Tests für den Berufungsprozess."""

    def test_appeal_created_on_richter_pass_seher_veto(self):
        """Regel 4: Richter PASS + Seher VETO → DISPUTED → Appeal."""
        manager = AppealManager()
        
        seher_veto = SeherVeto(
            veto_grund="Gefahr erkannt",
            confidence=0.85,
            evidence_refs=["evidence_1"],
            policy_ref="POL-001"
        )
        
        appeal = manager.create_appeal(
            package_id="pkg-123",
            seher_veto=seher_veto,
            richter_result=RichterResult.RICHTER_PASS
        )
        
        assert appeal is not None
        assert appeal.package_id == "pkg-123"
        assert appeal.status == AppealStatus.DISPUTED
        assert appeal.seher_veto == seher_veto

    def test_appeal_granted_releases_package(self):
        """Regel 4: APPEAL_GRANTED → Paket wird freigegeben."""
        manager = AppealManager()
        
        seher_veto = SeherVeto(
            veto_grund="Gefahr erkannt",
            confidence=0.85,
            evidence_refs=["evidence_1"],
            policy_ref="POL-001"
        )
        
        appeal = manager.create_appeal(
            package_id="pkg-123",
            seher_veto=seher_veto,
            richter_result=RichterResult.RICHTER_PASS
        )
        
        resolution = manager.resolve_appeal(
            appeal_id=appeal.appeal_id,
            decision=AppealDecision.APPEAL_GRANTED,
            reason="Gefahr widerlegt",
            resolved_by="kanzler-1"
        )
        
        assert resolution.decision == AppealDecision.APPEAL_GRANTED
        assert resolution.reason == "Gefahr widerlegt"
        # Paket ist freigegeben (wird im Gate-Flow behandelt)

    def test_appeal_granted_counts_as_false_block(self):
        """Regel 4: APPEAL_GRANTED wird als false_block gezählt."""
        manager = AppealManager()
        
        false_blocks = []
        def record_false_block(pkg_id):
            false_blocks.append(pkg_id)
        
        manager.set_false_block_callback(record_false_block)
        
        seher_veto = SeherVeto(
            veto_grund="Gefahr erkannt",
            confidence=0.85,
            evidence_refs=["evidence_1"],
            policy_ref="POL-001"
        )
        
        appeal = manager.create_appeal(
            package_id="pkg-123",
            seher_veto=seher_veto,
            richter_result=RichterResult.RICHTER_PASS
        )
        
        resolution = manager.resolve_appeal(
            appeal_id=appeal.appeal_id,
            decision=AppealDecision.APPEAL_GRANTED,
            reason="Falsche Blockade",
            resolved_by="kanzler-1"
        )
        
        assert resolution.decision == AppealDecision.APPEAL_GRANTED
        assert "pkg-123" in false_blocks  # False-Block wurde gezählt

    def test_veto_confirmed_writes_policy_veto_not_red(self):
        """Regel 4 (KRITISCH): VETO_CONFIRMED → 🟪 POLICY_VETO, NICHT 🟥."""
        manager = AppealManager()
        
        policy_vetos_written = []
        def write_policy_veto(package_id, veto_grund, policy_ref):
            policy_vetos_written.append({
                "package_id": package_id,
                "veto_grund": veto_grund,
                "policy_ref": policy_ref,
                "signal_type": "🟪"  # NICHT 🟥
            })
        
        manager.set_policy_veto_callback(write_policy_veto)
        
        seher_veto = SeherVeto(
            veto_grund="Policy-Verstoß",
            confidence=0.95,
            evidence_refs=["evidence_1", "evidence_2"],
            policy_ref="POL-001"
        )
        
        appeal = manager.create_appeal(
            package_id="pkg-456",
            seher_veto=seher_veto,
            richter_result=RichterResult.RICHTER_PASS
        )
        
        resolution = manager.resolve_appeal(
            appeal_id=appeal.appeal_id,
            decision=AppealDecision.VETO_CONFIRMED,
            reason="Policy-Verstoß bestätigt",
            resolved_by="kanzler-1"
        )
        
        assert resolution.decision == AppealDecision.VETO_CONFIRMED
        assert len(policy_vetos_written) == 1
        assert policy_vetos_written[0]["signal_type"] == "🟪"  # NICHT 🟥

    def test_high_risk_override_requires_positive_refutation(self):
        """Regel 4: HIGH_RISK_OVERRIDE nur bei positiver Widerlegung."""
        manager = AppealManager()
        
        seher_veto = SeherVeto(
            veto_grund="Hohe Gefahr",
            confidence=0.9,
            evidence_refs=["evidence_1"],
            policy_ref="POL-HIGH-RISK"
        )
        
        appeal = manager.create_appeal(
            package_id="pkg-789",
            seher_veto=seher_veto,
            richter_result=RichterResult.RICHTER_PASS,
            gate_mode="HIGH_RISK_OVERRIDE"
        )
        
        # Ohne positive Widerlegung sollte es fehlschlagen
        result = manager.resolve_appeal_with_override(
            appeal_id=appeal.appeal_id,
            positive_refutation="",  # Leer → ungültig
            resolved_by="kanzler-1"
        )
        
        assert result == "HIGH_RISK_OVERRIDE_DENIED"

    def test_high_risk_override_without_refutation_denied(self):
        """Regel 4: Ohne Widerlegung → HIGH_RISK_OVERRIDE_DENIED."""
        manager = AppealManager()
        
        seher_veto = SeherVeto(
            veto_grund="Hohe Gefahr",
            confidence=0.9,
            evidence_refs=["evidence_1"],
            policy_ref="POL-HIGH-RISK"
        )
        
        appeal = manager.create_appeal(
            package_id="pkg-789",
            seher_veto=seher_veto,
            richter_result=RichterResult.RICHTER_PASS,
            gate_mode="HIGH_RISK_OVERRIDE"
        )
        
        # Versuch ohne Widerlegung
        result = manager.resolve_appeal_with_override(
            appeal_id=appeal.appeal_id,
            positive_refutation=None,
            resolved_by="kanzler-1"
        )
        
        assert result == "HIGH_RISK_OVERRIDE_DENIED"
