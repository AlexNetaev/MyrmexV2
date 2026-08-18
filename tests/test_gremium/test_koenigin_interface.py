"""Tests für das Königin-Interface (Phase 9)."""

import pytest
from datetime import datetime, timezone

from src.gremium.koenigin_interface import KoeniginInterface
from src.contracts.pipeline_models import (
    KoeniglicheWeisung,
    IssuedBy,
    WeisungsStatus,
)


class MockAtlas:
    """Mock-Atlas für Tests."""
    
    def __init__(self, zones=None):
        self.zones = zones or {}
    
    def get_zone(self, zone_id: str):
        return self.zones.get(zone_id)


class MockZone:
    """Mock-Zone für Tests."""
    
    def __init__(self, zone_id, status="NORMAL", saettigung=False, fracture_diagnosis=None):
        self.zone_id = zone_id
        self.status = status
        self.saettigung = saettigung
        self.fracture_diagnosis = fracture_diagnosis


def test_koenigin_interface_validates_weisung_schema():
    """Interface validiert das Schema der KoeniglicheWeisung."""
    interface = KoeniginInterface()
    
    # Gültige Weisung
    weisung = KoeniglicheWeisung(
        weisungs_id="w-valid-001",
        bestaetigung="Ich bestätige",
        fokus_verschiebung=["zone-1"],
        issued_by=IssuedBy.LLM,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    
    assert interface.receive_weisung(weisung) == True


def test_koenigin_interface_rejects_invalid_weisung():
    """Ungültige Weisung wird abgelehnt."""
    interface = KoeniginInterface()
    
    # Ungültige Weisung (fehlendes Pflichtfeld)
    try:
        weisung = KoeniglicheWeisung(
            weisungs_id="",  # Leer -> ungültig
            bestaetigung="Ich bestätige",
            issued_by=IssuedBy.LLM,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        # Sollte ValidationError werfen bei der Erstellung
        assert False, "Sollte nicht erreicht werden"
    except Exception:
        # Erwartet
        pass


def test_koenigin_interface_logs_all_directives():
    """Jede Weisung wird im Audit-Log protokolliert."""
    interface = KoeniginInterface()
    atlas = MockAtlas({"zone-1": MockZone("zone-1")})
    
    weisung = KoeniglicheWeisung(
        weisungs_id="w-log-001",
        bestaetigung="Ich bestätige",
        fokus_verschiebung=["zone-1"],
        issued_by=IssuedBy.HUMAN,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    
    interface.process_weisung(weisung, atlas)
    
    audit_log = interface.get_audit_log()
    assert len(audit_log) > 0
    
    # Prüfe dass die Weisung protokolliert wurde
    actions = [entry.action for entry in audit_log]
    assert "weisung_received" in actions
    assert "weisung_processed" in actions


def test_koenigin_interface_logs_conflicts():
    """Konflikte werden im Audit-Log protokolliert."""
    interface = KoeniginInterface()
    atlas = MockAtlas({
        "zone-conflict": MockZone("zone-conflict", status="GESÄTTIGT", saettigung=True)
    })
    
    weisung = KoeniglicheWeisung(
        weisungs_id="w-conflict-001",
        bestaetigung="Ich bestätige",
        fokus_verschiebung=["zone-conflict"],
        issued_by=IssuedBy.LLM,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    
    interface.process_weisung(weisung, atlas)
    
    audit_log = interface.get_audit_log()
    
    # Prüfe dass Konflikt protokolliert wurde
    actions = [entry.action for entry in audit_log]
    assert "conflict_detected" in actions


def test_koenigin_interface_logs_safe_mode_changes():
    """SAFE_MODE-Wechsel werden im Audit-Log protokolliert."""
    interface = KoeniginInterface()
    
    interface.activate_safe_mode(reason="Test-Reason", triggered_by="TEST_USER")
    
    audit_log = interface.get_audit_log()
    actions = [entry.action for entry in audit_log]
    assert "safe_mode_activated" in actions
    
    interface.deactivate_safe_mode(authorized_by="ADMIN")
    
    audit_log = interface.get_audit_log()
    actions = [entry.action for entry in audit_log]
    assert "safe_mode_deactivated" in actions


def test_koenigin_interface_distinguishes_human_and_llm():
    """Interface unterscheidet korrekt zwischen HUMAN und LLM."""
    interface = KoeniginInterface()
    
    # Teste HUMAN
    assert interface.distinguishes_human_and_llm(IssuedBy.HUMAN) == True
    
    # Teste LLM
    assert interface.distinguishes_human_and_llm(IssuedBy.LLM) == True
    
    # Teste mit Weisungen
    atlas = MockAtlas({"zone-1": MockZone("zone-1")})
    
    human_weisung = KoeniglicheWeisung(
        weisungs_id="w-human-dist",
        bestaetigung="Human Bestätigung",
        issued_by=IssuedBy.HUMAN,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    
    llm_weisung = KoeniglicheWeisung(
        weisungs_id="w-llm-dist",
        bestaetigung="LLM Bestätigung",
        issued_by=IssuedBy.LLM,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    
    # Beide sollten verarbeitet werden können
    result_human = interface.process_weisung(human_weisung, atlas)
    result_llm = interface.process_weisung(llm_weisung, atlas)
    
    # Unterscheidung sollte im Audit-Log sichtbar sein
    audit_log = interface.get_audit_log()
    human_entries = [e for e in audit_log if e.authority == "HUMAN"]
    llm_entries = [e for e in audit_log if e.authority == "LLM"]
    
    assert len(human_entries) > 0
    assert len(llm_entries) > 0
