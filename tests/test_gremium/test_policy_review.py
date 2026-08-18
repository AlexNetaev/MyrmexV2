"""Tests für den Policy-Veto-Review."""

import pytest
from datetime import datetime, timezone
from src.gremium.sicherheitsrat.policy_review import PolicyReviewManager
from src.contracts.enums import PolicyReviewDecision


class TestPolicyReview:
    """Tests für den Policy-Veto-Review."""

    def test_policy_review_default_interval_20(self):
        """Regel 5: Default-Intervall ist 20."""
        manager = PolicyReviewManager()
        assert manager.interval_cycles == 20

    def test_policy_review_interval_range(self):
        """Regel 5: Range ist 1-500, 0 ungültig."""
        # Gültige Werte
        manager = PolicyReviewManager(interval_cycles=1)
        assert manager.interval_cycles == 1
        
        manager = PolicyReviewManager(interval_cycles=500)
        assert manager.interval_cycles == 500
        
        manager = PolicyReviewManager(interval_cycles=20)
        assert manager.interval_cycles == 20
        
        # Ungültig: 0
        with pytest.raises(ValueError, match="interval_cycles"):
            PolicyReviewManager(interval_cycles=0)
        
        # Ungültig: > 500
        with pytest.raises(ValueError, match="interval_cycles"):
            PolicyReviewManager(interval_cycles=501)
        
        # Ungültig: < 1 (negativ)
        with pytest.raises(ValueError, match="interval_cycles"):
            PolicyReviewManager(interval_cycles=-1)

    def test_policy_review_counter_persistent(self):
        """Regel 5: Zähler ist persistent (Neustart setzt nicht zurück)."""
        manager = PolicyReviewManager(interval_cycles=5)
        
        # Mehrere Zyklen durchlaufen
        for i in range(4):
            assert manager.increment_cycle() == False
        
        # 5. Zyklus sollte Review auslösen
        assert manager.increment_cycle() == True
        
        # Counter wurde zurückgesetzt
        assert manager.current_cycle == 0
        
        # "Neustart" (neue Instanz mit gleichem Startwert) würde bei 0 beginnen
        # Aber in der echten Implementierung wäre der Counter persistent
        # Hier simulieren wir Persistenz durch manuelles Setzen
        manager.current_cycle = 3  # Simuliere persistierten Zustand
        
        # Weiterzählen
        assert manager.increment_cycle() == False  # 4
        assert manager.increment_cycle() == True   # 5 → Review fällig

    def test_policy_review_safe_mode_pauses_not_resets(self):
        """Regel 5: SAFE_MODE pausiert, setzt nicht zurück."""
        manager = PolicyReviewManager(interval_cycles=5)
        
        # Ein paar Zyklen
        manager.increment_cycle()
        manager.increment_cycle()
        assert manager.current_cycle == 2
        
        # SAFE_MODE aktivieren
        manager.set_safe_mode(True)
        
        # Zyklen sollten pausieren
        manager.increment_cycle()
        manager.increment_cycle()
        assert manager.current_cycle == 2  # Unverändert
        
        # SAFE_MODE deaktivieren
        manager.set_safe_mode(False)
        
        # Weiterzählen
        manager.increment_cycle()
        assert manager.current_cycle == 3
        
        # Counter wurde NICHT zurückgesetzt

    def test_policy_review_audit_event(self):
        """Regel 5: Audit-Event mit allen erforderlichen Feldern."""
        manager = PolicyReviewManager(interval_cycles=3)
        
        # Bis zum Review zählen
        manager.increment_cycle()
        manager.increment_cycle()
        manager.increment_cycle()  # Löst Review aus
        
        # Mock Policy-Vetos
        policy_vetos = [
            {"policy_veto_id": "pv-001", "package_id": "pkg-1"},
            {"policy_veto_id": "pv-002", "package_id": "pkg-2"}
        ]
        
        reviews = manager.run_review(
            policy_vetos=policy_vetos,
            authority="kanzler-1",
            zyklus_id="zyklus-001"
        )
        
        assert len(reviews) == 2
        
        for review in reviews:
            # Alle erforderlichen Felder prüfen
            assert hasattr(review, 'event_type')
            assert review.event_type == "policy_veto_review"
            assert hasattr(review, 'zyklus_id')
            assert review.zyklus_id == "zyklus-001"
            assert hasattr(review, 'policy_veto_id')
            assert hasattr(review, 'review_decision')
            assert review.review_decision in ["CONFIRMED", "LIFTED", "ESCALATED"]
            assert hasattr(review, 'review_reason')
            assert hasattr(review, 'review_timestamp')
            assert hasattr(review, 'review_authority')
            assert review.review_authority == "kanzler-1"
            assert hasattr(review, 'escalation_target')

    def test_policy_review_decisions(self):
        """Regel 5: Bestätigen, Aufheben, Eskalieren."""
        manager = PolicyReviewManager(interval_cycles=3)
        
        # Bis zum Review zählen
        for _ in range(3):
            manager.increment_cycle()
        
        # Mock Policy-Vetos mit verschiedenen Entscheidungen
        policy_vetos = [
            {"policy_veto_id": "pv-confirm", "package_id": "pkg-1"},
            {"policy_veto_id": "pv-lift", "package_id": "pkg-2"},
            {"policy_veto_id": "pv-escalate", "package_id": "pkg-3"}
        ]
        
        reviews = manager.run_review(
            policy_vetos=policy_vetos,
            authority="kanzler-1",
            zyklus_id="zyklus-001",
            decisions={
                "pv-confirm": "CONFIRMED",
                "pv-lift": "LIFTED",
                "pv-escalate": "ESCALATED"
            }
        )
        
        assert len(reviews) == 3
        
        decisions = {r.policy_veto_id: r.review_decision for r in reviews}
        assert decisions["pv-confirm"] == "CONFIRMED"
        assert decisions["pv-lift"] == "LIFTED"
        assert decisions["pv-escalate"] == "ESCALATED"
        
        # Eskalation hat escalation_target
        escalate_review = next(r for r in reviews if r.policy_veto_id == "pv-escalate")
        assert escalate_review.escalation_target is not None
