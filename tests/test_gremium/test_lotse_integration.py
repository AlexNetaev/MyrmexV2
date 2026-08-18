"""Integrationstests für Lotse - MYRMEX v2.4.0."""

import pytest
from unittest.mock import Mock

from src.gremium.lotse import Lotse, LotseWorkerPool, SignalSnapshot
from src.gremium.vordenker import Vordenker, VordenkerConfig, AtlasSummary
from src.gremium.pre_filter import PreFilter, FilterDecision
from src.contracts.pipeline_models import (
    RohIdee,
    IdeenIntent,
    GefahrenHypothese,
    EvidenceStatus,
    LotseDecision as LotseDecisionEnum,
    WegmarkeTyp,
)
from src.contracts.enums import ZoneHealth


class MockSignalRegistry:
    """Mock Signal Registry für Tests."""
    
    def __init__(self, signals_by_coordinate: dict | None = None):
        self.signals_by_coordinate = signals_by_coordinate or {}
    
    def resolve_signal(self, koordinate: dict[str, float]) -> str:
        key = str(sorted(koordinate.items()))
        return self.signals_by_coordinate.get(key, "WHITE")
    
    def get_signal_snapshot(self, koordinate: dict[str, float]) -> SignalSnapshot:
        signal = self.resolve_signal(koordinate)
        severity = "WHITE"
        if "RED" in signal:
            severity = "RED"
        elif "GREEN" in signal:
            severity = "GREEN"
        
        return SignalSnapshot(
            version="v1",
            signals=[("SIGNAL", severity)],
            resolved_signal=signal,
        )


class MockAtlas:
    """Mock Atlas für Tests."""
    
    def __init__(self, atlas_version_id: str = "atlas_v1", zones: dict | None = None):
        self.atlas_version_id = atlas_version_id
        self.zones = zones or {}
    
    def get_zone_for_coordinate(self, koordinate: dict[str, float]) -> any:
        key = str(sorted(koordinate.items()))
        zone_data = self.zones.get(key, {"zone_id": "default", "zone_health": ZoneHealth.STABIL})
        
        class Zone:
            zone_id = zone_data.get("zone_id", "default")
            zone_health = zone_data.get("zone_health", ZoneHealth.STABIL)
        
        return Zone()


def create_test_idee(
    idee_id: str = "test_idee_1",
    intent: IdeenIntent = IdeenIntent.EXPLORATION,
    ziel_koordinate: dict[str, float] | None = None,
    fracture_diagnosis_budget: float | None = None,
) -> RohIdee:
    """Erstellt eine Test-Idee."""
    idee = RohIdee(
        idee_id=idee_id,
        intent=intent,
        ziel_koordinate=ziel_koordinate or {"x": 0.5, "y": 0.5},
        beschreibung="Test Idee",
        gefahren_hypothese=GefahrenHypothese(
            beschreibung="Keine bekannten Gefahren",
            evidence_status=EvidenceStatus.HYPOTHETISCH,
            referenzen=[],
        ),
        proposed_dimensions=[],
        atlas_version_ref="atlas_v1",
    )
    if fracture_diagnosis_budget is not None:
        idee.fracture_diagnosis_budget = fracture_diagnosis_budget
    return idee


def test_pre_filter_to_lotse_pipeline():
    """Pre-Filter → Lotse Pipeline funktioniert."""
    pre_filter = PreFilter()
    lotse = Lotse()
    
    idee = create_test_idee()
    
    # Pre-Filter prüft Idee
    filter_result = pre_filter.filter_idea(idee)
    assert filter_result.decision == FilterDecision.ERLAUBEN
    
    # Lotse platziert Wegmarke
    signal_registry = MockSignalRegistry()
    atlas = MockAtlas()
    
    result = lotse.place_waypoint(idee, signal_registry, atlas)
    assert result.decision == LotseDecisionEnum.PLATZIEREN
    assert result.wegmarke is not None


def test_vordenker_to_lotse_full_pipeline():
    """Vordenker → Pre-Filter → Lotse Pipeline funktioniert."""
    vordenker = Vordenker()
    pre_filter = PreFilter()
    lotse = Lotse()
    
    # Atlas Summary erstellen
    atlas_summary = AtlasSummary(
        atlas_version_id="atlas_v1",
        weißraum_anteil=0.5,
        weißraum_zonen=[{"centroid": {"x": 0.5, "y": 0.5}, "zone_id": "zone_1"}],
    )
    
    # Vordenker generiert Ideen
    ideen = vordenker.generate_ideas(atlas_summary)
    assert len(ideen) > 0
    
    idee = ideen[0]
    
    # Pre-Filter prüft Idee
    filter_result = pre_filter.filter_idea(idee)
    assert filter_result.decision == FilterDecision.ERLAUBEN
    
    # Lotse platziert Wegmarke
    signal_registry = MockSignalRegistry()
    atlas = MockAtlas()
    
    result = lotse.place_waypoint(idee, signal_registry, atlas)
    assert result.decision == LotseDecisionEnum.PLATZIEREN


def test_lotse_blocked_cache_prevents_replacement():
    """Verworfene Wegmarke wird nicht erneut platziert."""
    blocked_cache = {}
    lotse = Lotse(blocked_cache=blocked_cache)
    
    idee = create_test_idee()
    
    # Erste Platzierung mit RED Signal → Verwerfung
    signal_registry = MockSignalRegistry({"[('x', 0.5), ('y', 0.5)]": "RED"})
    atlas = MockAtlas()
    
    result1 = lotse.place_waypoint(idee, signal_registry, atlas)
    assert result1.decision == LotseDecisionEnum.VERWERFEN
    assert idee.idee_id in blocked_cache
    
    # Idee ist jetzt im blocked_cache


def test_lotse_state_machine_geprueft_to_platziert():
    """Zustandsmaschine: IDEE_GEPRÜFT → WEGMARKE_PLATZIERT."""
    lotse = Lotse()
    idee = create_test_idee()
    
    signal_registry = MockSignalRegistry()
    atlas = MockAtlas()
    
    result = lotse.place_waypoint(idee, signal_registry, atlas)
    
    assert result.decision == LotseDecisionEnum.PLATZIEREN
    assert len(lotse.lotse_events) > 0
    
    event = lotse.lotse_events[0]
    assert event.decision == LotseDecisionEnum.PLATZIEREN


def test_lotse_state_machine_geprueft_to_verworfen():
    """Zustandsmaschine: IDEE_GEPRÜFT → IDEE_VERWORFEN."""
    lotse = Lotse()
    idee = create_test_idee()
    
    signal_registry = MockSignalRegistry({"[('x', 0.5), ('y', 0.5)]": "RED"})
    atlas = MockAtlas()
    
    result = lotse.place_waypoint(idee, signal_registry, atlas)
    
    assert result.decision == LotseDecisionEnum.VERWERFEN
    assert len(lotse.lotse_events) > 0
    
    event = lotse.lotse_events[0]
    assert event.decision == LotseDecisionEnum.VERWERFEN


def test_lotse_recovery_after_crash():
    """Phase 4 Recovery arbeitet mit Lotse zusammen."""
    # Lotse kann Events protokollieren und wiederherstellen
    lotse = Lotse()
    idee = create_test_idee()
    
    signal_registry = MockSignalRegistry()
    atlas = MockAtlas()
    
    result = lotse.place_waypoint(idee, signal_registry, atlas)
    
    # Events können abgerufen werden (für Recovery)
    events = lotse.get_lotse_events()
    assert len(events) > 0
    assert events[0].idee_id == idee.idee_id


def test_lotse_with_signal_registry():
    """Lotse liest korrekt aus Signal-Registry."""
    lotse = Lotse()
    idee = create_test_idee()
    
    # Signal-Registry mit RED Signal
    signal_registry = MockSignalRegistry({"[('x', 0.5), ('y', 0.5)]": "RED"})
    atlas = MockAtlas()
    
    result = lotse.place_waypoint(idee, signal_registry, atlas)
    
    # RED Signal sollte zur Verwerfung führen
    assert result.decision == LotseDecisionEnum.VERWERFEN


def test_lotse_with_atlas_zones():
    """Lotse liest korrekt aus Atlas-Zonen."""
    lotse = Lotse()
    idee = create_test_idee()
    
    # Atlas mit QUARANTÄNE-Zone
    atlas = MockAtlas()
    atlas.zones = {
        "[('x', 0.5), ('y', 0.5)]": {"zone_id": "quarantine", "zone_health": ZoneHealth.QUARANTAENE}
    }
    
    signal_registry = MockSignalRegistry()
    
    # EXPLORATION in QUARANTÄNE sollte verworfen werden
    result = lotse.place_waypoint(idee, signal_registry, atlas)
    
    assert result.decision == LotseDecisionEnum.VERWERFEN
    assert "QUARANTINE" in result.reason.upper()
