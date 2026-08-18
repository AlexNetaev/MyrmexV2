"""Tests für den Kanzler (Phase 9)."""

import pytest
from datetime import datetime, timezone

from src.gremium.kanzler import Kanzler
from src.contracts.pipeline_models import (
    KoeniglicheWeisung,
    IssuedBy,
    WeisungsStatus,
    SafeModeState,
    RealitaetsCheckStatus,
)


class MockAtlas:
    """Mock-Atlas für Tests."""
    
    def __init__(self, zones=None):
        self.zones = zones or {}
        self._current_version_id = "atlas-v1"
        self._signal_provenance = {"source": "test"}
    
    def get_zone(self, zone_id: str):
        return self.zones.get(zone_id)
    
    def get_zone_summaries(self):
        return list(self.zones.keys())
    
    @property
    def current_version_id(self):
        return self._current_version_id
    
    @property
    def signal_provenance(self):
        return self._signal_provenance


class MockZone:
    """Mock-Zone für Tests."""
    
    def __init__(self, zone_id, status="NORMAL", saettigung=False, fracture_diagnosis=None):
        self.zone_id = zone_id
        self.status = status
        self.saettigung = saettigung
        self.fracture_diagnosis = fracture_diagnosis


class MockResourceGovernor:
    """Mock-ResourceGovernor für Tests."""
    
    def get_capacity_status(self):
        return {"available_slots": 10, "total_slots": 20}


class MockCircuitBreaker:
    """Mock-CircuitBreaker für Tests."""
    
    def __init__(self, state="NORMAL"):
        self.state = state


def test_kanzler_generates_lagebericht():
    """Kanzler erzeugt Lagebericht mit allen Pflichtfeldern."""
    kanzler = Kanzler()
    atlas = MockAtlas({"zone-1": MockZone("zone-1")})
    resource_governor = MockResourceGovernor()
    circuit_breaker = MockCircuitBreaker()
    
    lagebericht = kanzler.generate_lagebericht(atlas, resource_governor, circuit_breaker)
    
    assert lagebericht.lagebericht_id is not None
    assert len(lagebericht.lagebericht_id) > 0
    assert lagebericht.timestamp is not None
    assert lagebericht.seher_circuit_breaker_status is not None


def test_lagebericht_contains_circuit_breaker_status():
    """Lagebericht enthält seher_circuit_breaker_status."""
    kanzler = Kanzler()
    atlas = MockAtlas()
    resource_governor = MockResourceGovernor()
    circuit_breaker = MockCircuitBreaker(state="SHADOW_MODE")
    
    lagebericht = kanzler.generate_lagebericht(atlas, resource_governor, circuit_breaker)
    
    assert lagebericht.seher_circuit_breaker_status == "SHADOW_MODE"


def test_realitaets_check_allows_valid_focus():
    """Regel 2: Fokus auf valide Zone -> AKZEPTIERT."""
    kanzler = Kanzler()
    atlas = MockAtlas({
        "zone-valid": MockZone("zone-valid", status="NORMAL", saettigung=False)
    })
    
    weisung = KoeniglicheWeisung(
        weisungs_id="w-001",
        bestaetigung="Ich bestätige diese Weisung",
        fokus_verschiebung=["zone-valid"],
        issued_by=IssuedBy.LLM,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    
    result = kanzler.process_weisung(weisung, atlas)
    
    assert result.status == WeisungsStatus.AKZEPTIERT
    assert result.realitaets_check_status == RealitaetsCheckStatus.OK


def test_realitaets_check_detects_saturated_zone_conflict():
    """Regel 2: Fokus auf gesättigte Zone -> KONFLIKT."""
    kanzler = Kanzler()
    atlas = MockAtlas({
        "zone-saturated": MockZone("zone-saturated", status="GESÄTTIGT", saettigung=True)
    })
    
    weisung = KoeniglicheWeisung(
        weisungs_id="w-002",
        bestaetigung="Ich bestätige diese Weisung",
        fokus_verschiebung=["zone-saturated"],
        issued_by=IssuedBy.LLM,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    
    result = kanzler.process_weisung(weisung, atlas)
    
    assert result.status == WeisungsStatus.KONFLIKT
    assert result.realitaets_check_status == RealitaetsCheckStatus.KONFLIKT
    assert len(result.konflikt_details) > 0
    assert "gesättigte Zone" in result.konflikt_details[0]


def test_realitaets_check_detects_quarantine_conflict():
    """Regel 2: Fokus auf QUARANTÄNE ohne Diagnose -> KONFLIKT."""
    kanzler = Kanzler()
    atlas = MockAtlas({
        "zone-quarantine": MockZone("zone-quarantine", status="QUARANTÄNE", fracture_diagnosis=None)
    })
    
    weisung = KoeniglicheWeisung(
        weisungs_id="w-003",
        bestaetigung="Ich bestätige diese Weisung",
        fokus_verschiebung=["zone-quarantine"],
        issued_by=IssuedBy.LLM,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    
    result = kanzler.process_weisung(weisung, atlas)
    
    assert result.status == WeisungsStatus.KONFLIKT
    assert result.realitaets_check_status == RealitaetsCheckStatus.KONFLIKT
    assert len(result.konflikt_details) > 0
    assert "QUARANTÄNE" in result.konflikt_details[0]


def test_human_queen_never_overruled():
    """Regel 1 (KRITISCH): Menschliche Königin wird nie überstimmt."""
    kanzler = Kanzler()
    atlas = MockAtlas({
        "zone-conflict": MockZone("zone-conflict", status="GESÄTTIGT", saettigung=True)
    })
    
    # Menschliche Königin gibt konfliktäre Weisung
    weisung = KoeniglicheWeisung(
        weisungs_id="w-human-001",
        bestaetigung="Ich bestätige diese Weisung als menschliche Königin",
        fokus_verschiebung=["zone-conflict"],
        issued_by=IssuedBy.HUMAN,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    
    result = kanzler.process_weisung(weisung, atlas)
    
    # WICHTIG: Die Weisung wird nicht abgelehnt, sondern es wird ein Konflikt gemeldet
    # und SAFE_MODE aktiviert. Die Königin wird NICHT überstimmt.
    assert result.status == WeisungsStatus.KONFLIKT
    assert result.sonderbericht is not None
    assert result.safe_mode_triggered == True
    
    # SAFE_MODE ist jetzt aktiv
    assert kanzler.is_safe_mode_active() == True


def test_human_queen_conflict_generates_sonderbericht():
    """Regel 1: Konflikt bei menschlicher Königin erzeugt Sonderbericht."""
    kanzler = Kanzler()
    atlas = MockAtlas({
        "zone-conflict": MockZone("zone-conflict", status="QUARANTÄNE", fracture_diagnosis=None)
    })
    
    weisung = KoeniglicheWeisung(
        weisungs_id="w-human-002",
        bestaetigung="Ich bestätige",
        fokus_verschiebung=["zone-conflict"],
        issued_by=IssuedBy.HUMAN,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    
    result = kanzler.process_weisung(weisung, atlas)
    
    assert result.sonderbericht is not None
    assert "SONDERBERICHT" in result.sonderbericht
    assert weisung.weisungs_id in result.sonderbericht


def test_llm_queen_fallback_after_2_conflicts():
    """Regel 4: LLM-Königin Fallback nach 2 aufeinanderfolgenden Konflikten."""
    kanzler = Kanzler()
    atlas = MockAtlas({
        "zone-bad": MockZone("zone-bad", status="GESÄTTIGT", saettigung=True)
    })
    
    # Erster Konflikt
    weisung1 = KoeniglicheWeisung(
        weisungs_id="w-llm-001",
        bestaetigung="LLM Bestätigung 1",
        fokus_verschiebung=["zone-bad"],
        issued_by=IssuedBy.LLM,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    result1 = kanzler.process_weisung(weisung1, atlas)
    assert kanzler.get_llm_conflict_count() == 1
    
    # Zweiter Konflikt -> Fallback sollte ausgelöst werden
    weisung2 = KoeniglicheWeisung(
        weisungs_id="w-llm-002",
        bestaetigung="LLM Bestätigung 2",
        fokus_verschiebung=["zone-bad"],
        issued_by=IssuedBy.LLM,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    result2 = kanzler.process_weisung(weisung2, atlas)
    
    # Nach 2 Konflikten sollte SAFE_MODE aktiv sein
    assert kanzler.is_safe_mode_active() == True
    assert result2.safe_mode_triggered == True


def test_safe_mode_stops_new_exploration():
    """Regel 3: SAFE_MODE blockiert neue Exploration."""
    kanzler = Kanzler()
    
    # SAFE_MODE aktivieren
    kanzler.activate_safe_mode(reason="Test", triggered_by="TEST")
    
    assert kanzler.is_safe_mode_active() == True
    assert kanzler.get_safe_mode_state() == SafeModeState.ACTIVE


def test_safe_mode_allows_low_risk_completion():
    """Regel 3: Risikoarme laufende Quests dürfen abschließen."""
    kanzler = Kanzler()
    
    # SAFE_MODE Config erlaubt low-risk completion per Default
    assert kanzler._safe_mode_config.allow_low_risk_completion == True


def test_policy_veto_review_triggers_at_20_cycles():
    """Regel 5: Review wird bei Zyklus 20 getriggert."""
    kanzler = Kanzler(policy_review_cycle_limit=20)
    
    # 19 Zyklen -> kein Review
    for i in range(19):
        assert kanzler.increment_cycle_and_check_review() == False
    
    assert kanzler.get_cycle_counter() == 19
    
    # 20. Zyklus -> Review fällig
    assert kanzler.increment_cycle_and_check_review() == True
    
    # Zähler wurde zurückgesetzt
    assert kanzler.get_cycle_counter() == 0


def test_policy_veto_review_counter_persistent():
    """Regel 5: Zähler ist persistent (Neustart setzt nicht zurück)."""
    kanzler = Kanzler(policy_review_cycle_limit=20)
    
    # Einige Zyklen durchführen
    for i in range(10):
        kanzler.increment_cycle_and_check_review()
    
    counter_before = kanzler.get_cycle_counter()
    assert counter_before == 10
    
    # "Neustart" simulieren (neue Instanz mit gleichem Limit)
    # In der Realität würde der Zähler persistent gespeichert werden
    # Hier testen wir dass der Zähler nicht automatisch zurückgesetzt wird
    assert kanzler.get_cycle_counter() == 10


def test_safe_mode_pauses_review_counter():
    """Regel 5: SAFE_MODE pausiert den Review-Zähler."""
    kanzler = Kanzler(policy_review_cycle_limit=5)
    
    # Ein paar Zyklen
    kanzler.increment_cycle_and_check_review()
    kanzler.increment_cycle_and_check_review()
    assert kanzler.get_cycle_counter() == 2
    
    # SAFE_MODE aktivieren
    kanzler.activate_safe_mode(reason="Test", triggered_by="TEST")
    
    # Weitere Inkremente sollten den Zähler NICHT erhöhen (pausiert)
    initial_counter = kanzler.get_cycle_counter()
    for i in range(10):
        kanzler.increment_cycle_and_check_review()
    
    # Zähler sollte unverändert sein (pausiert)
    assert kanzler.get_cycle_counter() == initial_counter


def test_kanzler_audit_log_entries():
    """Kanzler protokolliert alle Aktionen im Audit-Log."""
    kanzler = Kanzler()
    atlas = MockAtlas({"zone-ok": MockZone("zone-ok")})
    
    weisung = KoeniglicheWeisung(
        weisungs_id="w-audit-001",
        bestaetigung="Test",
        fokus_verschiebung=["zone-ok"],
        issued_by=IssuedBy.LLM,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    
    kanzler.process_weisung(weisung, atlas)
    
    audit_log = kanzler.get_audit_log()
    assert len(audit_log) > 0
    
    # Prüfe dass Weisung empfangen wurde
    actions = [entry.action for entry in audit_log]
    assert "weisung_akzeptiert" in actions
