"""Tests für Lotse QUARANTÄNE-Schutz - MYRMEX v2.4.0."""

import pytest
from unittest.mock import Mock

from src.gremium.lotse import Lotse, SignalSnapshot
from src.contracts.pipeline_models import (
    RohIdee,
    IdeenIntent,
    GefahrenHypothese,
    EvidenceStatus,
    LotseDecision as LotseDecisionEnum,
)
from src.contracts.enums import ZoneHealth


class MockAtlas:
    """Mock Atlas für Tests."""
    
    def __init__(self, atlas_version_id: str = "atlas_v1", zones: dict | None = None):
        self.atlas_version_id = atlas_version_id
        self.zones = zones or {}
    
    def get_zone_for_coordinate(self, koordinate: dict[str, float]) -> any:
        """Gibt die Zone für eine Koordinate zurück."""
        key = str(sorted(koordinate.items()))
        zone_data = self.zones.get(key, {"zone_id": "default", "zone_health": ZoneHealth.STABIL})
        
        class Zone:
            zone_id = zone_data.get("zone_id", "default")
            zone_health = zone_data.get("zone_health", ZoneHealth.STABIL)
        
        return Zone()


class MockSignalRegistry:
    """Mock Signal Registry für Tests."""
    
    def resolve_signal(self, koordinate: dict[str, float]) -> str:
        return "WHITE"
    
    def get_signal_snapshot(self, koordinate: dict[str, float]) -> SignalSnapshot:
        return SignalSnapshot(
            version="v1",
            signals=[("SIGNAL", "WHITE")],
            resolved_signal="WHITE",
        )


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


def test_lotse_quarantine_allows_diagnostic_only():
    """Regel 2 (KRITISCH): QUARANTÄNE erlaubt nur diagnostic_waypoints."""
    lotse = Lotse()
    
    # FRACTURE_DIAGNOSIS-Idee mit Budget
    idee = create_test_idee(
        intent=IdeenIntent.FRACTURE_DIAGNOSIS,
        fracture_diagnosis_budget=100.0,
    )
    
    # Mock Atlas mit QUARANTÄNE-Zone
    quarantine_atlas = MockAtlas()
    quarantine_atlas.zones = {
        "[('x', 0.5), ('y', 0.5)]": {"zone_id": "quarantine_zone", "zone_health": ZoneHealth.QUARANTAENE}
    }
    
    signal_registry = MockSignalRegistry()
    
    result = lotse.place_waypoint(idee, signal_registry, quarantine_atlas)
    
    # FRACTURE_DIAGNOSIS mit Budget sollte erlaubt sein
    assert result.decision == LotseDecisionEnum.PLATZIEREN
    assert result.wegmarke is not None
    assert result.wegmarke.wegmarke_typ.value == "DIAGNOSTIC"


def test_lotse_quarantine_rejects_normal_waypoint():
    """Regel 2 (KRITISCH): QUARANTÄNE verwirft normale Wegmarken."""
    lotse = Lotse()
    
    # Normale EXPLORATION-Idee
    idee = create_test_idee(intent=IdeenIntent.EXPLORATION)
    
    # Mock Atlas mit QUARANTÄNE-Zone
    quarantine_atlas = MockAtlas()
    quarantine_atlas.zones = {
        "[('x', 0.5), ('y', 0.5)]": {"zone_id": "quarantine_zone", "zone_health": ZoneHealth.QUARANTAENE}
    }
    
    signal_registry = MockSignalRegistry()
    
    result = lotse.place_waypoint(idee, signal_registry, quarantine_atlas)
    
    # Normale Wegmarke in QUARANTÄNE sollte verworfen werden
    assert result.decision == LotseDecisionEnum.VERWERFEN
    assert "QUARANTINE" in result.reason.upper()


def test_lotse_quarantine_diagnostic_requires_budget():
    """Regel 2: diagnostic_waypoint benötigt fracture_diagnosis_budget."""
    lotse = Lotse()
    
    # FRACTURE_DIAGNOSIS-Idee OHNE Budget
    idee = create_test_idee(
        intent=IdeenIntent.FRACTURE_DIAGNOSIS,
        fracture_diagnosis_budget=None,
    )
    
    # Mock Atlas mit QUARANTÄNE-Zone
    quarantine_atlas = MockAtlas()
    quarantine_atlas.zones = {
        "[('x', 0.5), ('y', 0.5)]": {"zone_id": "quarantine_zone", "zone_health": ZoneHealth.QUARANTAENE}
    }
    
    signal_registry = MockSignalRegistry()
    
    result = lotse.place_waypoint(idee, signal_registry, quarantine_atlas)
    
    # Ohne Budget sollte verworfen werden
    assert result.decision == LotseDecisionEnum.VERWERFEN
    assert "BUDGET" in result.reason.upper()


def test_lotse_quarantine_diagnostic_without_budget_rejected():
    """Regel 2: diagnostic_waypoint ohne Budget wird verworfen."""
    lotse = Lotse()
    
    # FRACTURE_DIAGNOSIS-Idee mit Budget = 0
    idee = create_test_idee(
        intent=IdeenIntent.FRACTURE_DIAGNOSIS,
        fracture_diagnosis_budget=0,
    )
    
    # Mock Atlas mit QUARANTÄNE-Zone
    quarantine_atlas = MockAtlas()
    quarantine_atlas.zones = {
        "[('x', 0.5), ('y', 0.5)]": {"zone_id": "quarantine_zone", "zone_health": ZoneHealth.QUARANTAENE}
    }
    
    signal_registry = MockSignalRegistry()
    
    result = lotse.place_waypoint(idee, signal_registry, quarantine_atlas)
    
    # Mit Budget = 0 sollte verworfen werden
    assert result.decision == LotseDecisionEnum.VERWERFEN


def test_lotse_quarantine_fracture_diagnosis_intent_allowed():
    """Regel 2: intent=FRACTURE_DIAGNOSIS in QUARANTÄNE → ERLAUBEN."""
    lotse = Lotse()
    
    # FRACTURE_DIAGNOSIS-Idee mit Budget
    idee = create_test_idee(
        intent=IdeenIntent.FRACTURE_DIAGNOSIS,
        fracture_diagnosis_budget=50.0,
    )
    
    # Mock Atlas mit QUARANTÄNE-Zone
    quarantine_atlas = MockAtlas()
    quarantine_atlas.zones = {
        "[('x', 0.5), ('y', 0.5)]": {"zone_id": "quarantine_zone", "zone_health": ZoneHealth.QUARANTAENE}
    }
    
    signal_registry = MockSignalRegistry()
    
    result = lotse.place_waypoint(idee, signal_registry, quarantine_atlas)
    
    # FRACTURE_DIAGNOSIS sollte erlaubt sein
    assert result.decision == LotseDecisionEnum.PLATZIEREN


def test_lotse_quarantine_exploration_intent_rejected():
    """Regel 2: intent=EXPLORATION in QUARANTÄNE → VERWERFEN."""
    lotse = Lotse()
    
    # EXPLORATION-Idee
    idee = create_test_idee(intent=IdeenIntent.EXPLORATION)
    
    # Mock Atlas mit QUARANTÄNE-Zone
    quarantine_atlas = MockAtlas()
    quarantine_atlas.zones = {
        "[('x', 0.5), ('y', 0.5)]": {"zone_id": "quarantine_zone", "zone_health": ZoneHealth.QUARANTAENE}
    }
    
    signal_registry = MockSignalRegistry()
    
    result = lotse.place_waypoint(idee, signal_registry, quarantine_atlas)
    
    # EXPLORATION in QUARANTÄNE sollte verworfen werden
    assert result.decision == LotseDecisionEnum.VERWERFEN
    assert "QUARANTINE" in result.reason.upper()
