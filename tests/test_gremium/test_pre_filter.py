"""Tests für Pre-Filter (Stufe 5a) - MYRMEX v2.4.0."""

import pytest

from src.gremium.pre_filter import PreFilter, DimensionSchema, SignalStack, ZoneInfo
from src.contracts.pipeline_models import (
    RohIdee,
    IdeenIntent,
    GefahrenHypothese,
    EvidenceStatus,
    FilterDecision,
)
from src.contracts.enums import ZoneHealth


class MockSignalRegistry:
    """Mock Signal Registry für Tests."""
    
    def __init__(self, signals_dict: dict | None = None):
        self.signals_dict = signals_dict or {}
    
    def get_signal_stack(self, koordinate: dict[str, float]) -> SignalStack:
        """Gibt SignalStack für Koordinate zurück."""
        key = str(sorted(koordinate.items()))
        signals = self.signals_dict.get(key, [])
        return SignalStack(signals)


class TestPreFilterNormalIdea:
    """Test-Suite für normale Ideen."""
    
    def test_pre_filter_allows_normal_idea(self):
        """Normale Idee ohne Probleme → ERLAUBEN."""
        pre_filter = PreFilter()
        
        idee = RohIdee(
            idee_id="test-idea-1",
            intent=IdeenIntent.EXPLORATION,
            ziel_koordinate={"x": 0.1, "y": 0.2},
            beschreibung="Normale Exploration",
            atlas_version_ref="v1.0.0",
        )
        
        result = pre_filter.filter_idea(idee)
        
        assert result.decision == FilterDecision.ERLAUBEN
        assert result.reason == "NORMAL"


class TestPreFilterRedSignal:
    """Test-Suite für rote Signale."""
    
    def test_pre_filter_rejects_red_signal(self):
        """🟥-Signal an Zielkoordinate → VERWERFEN."""
        dimension_schema = DimensionSchema(known_dimensions={"x", "y", "z"})
        pre_filter = PreFilter(dimension_schema=dimension_schema)
        
        idee = RohIdee(
            idee_id="test-idea-red",
            intent=IdeenIntent.EXPLORATION,
            ziel_koordinate={"x": 0.1},
            beschreibung="Idee mit rotem Signal",
            atlas_version_ref="v1.0.0",
        )
        
        # Mock Signal Registry mit rotem Signal
        signal_registry = MockSignalRegistry({
            "[('x', 0.1)]": [("SCIENTIFIC", "RED")],
        })
        
        result = pre_filter.filter_idea(idee, signal_registry)
        
        assert result.decision == FilterDecision.VERWERFEN
        assert result.reason == "RED_SIGNAL"


class TestPreFilterPhysicalImpossible:
    """Test-Suite für physikalische Unmöglichkeit."""
    
    def test_pre_filter_rejects_physical_impossible(self):
        """Physikalische Unmöglichkeit → VERWERFEN."""
        pre_filter = PreFilter()
        
        idee = RohIdee(
            idee_id="test-idea-impossible",
            intent=IdeenIntent.EXPLORATION,
            ziel_koordinate={"x": 1e15},  # Unrealistisch großer Wert
            beschreibung="Physikalisch unmöglich",
            atlas_version_ref="v1.0.0",
        )
        
        result = pre_filter.filter_idea(idee)
        
        assert result.decision == FilterDecision.VERWERFEN
        assert result.reason == "PHYSICAL_IMPOSSIBLE"


class TestPreFilterUnknownDimension:
    """Test-Suite für unbekannte Dimensionen (KRITISCH)."""
    
    def test_pre_filter_unknown_dimension_is_gap_not_reject(self):
        """Regel 2 (KRITISCH): Unbekannte Dimension → DIMENSION_GAP, NICHT VERWERFEN."""
        # Nur x und y sind bekannt, nicht "neue_dimension"
        dimension_schema = DimensionSchema(known_dimensions={"x", "y", "z"})
        pre_filter = PreFilter(dimension_schema=dimension_schema)
        
        idee = RohIdee(
            idee_id="test-idea-unknown-dim",
            intent=IdeenIntent.EXPLORATION,
            ziel_koordinate={"x": 0.1, "neue_dimension": 0.5},  # unbekannt!
            beschreibung="Idee mit unbekannter Dimension",
            atlas_version_ref="v1.0.0",
        )
        
        result = pre_filter.filter_idea(idee)
        
        # KRITISCH: Nicht VERWERFEN, sondern DIMENSION_GAP
        assert result.decision == FilterDecision.DIMENSION_GAP
        assert "neue_dimension" in result.reason
        assert result.decision != FilterDecision.VERWERFEN
    
    def test_pre_filter_dimension_gap_creates_onboarding_request(self):
        """Regel 2: DIMENSION_GAP erzeugt dimension_onboarding_request."""
        dimension_schema = DimensionSchema(known_dimensions={"x", "y"})
        pre_filter = PreFilter(dimension_schema=dimension_schema)
        
        idee = RohIdee(
            idee_id="test-idea-onboarding",
            intent=IdeenIntent.EXPLORATION,
            ziel_koordinate={"x": 0.1, "unbekannt": 0.5},
            beschreibung="Idee benötigt Onboarding",
            atlas_version_ref="v1.0.0",
        )
        
        result = pre_filter.filter_idea(idee)
        
        assert result.decision == FilterDecision.DIMENSION_GAP
        assert len(pre_filter.get_dimension_onboarding_requests()) >= 1
        
        request = pre_filter.get_dimension_onboarding_requests()[0]
        assert request.dimension == "unbekannt"
        assert request.package_id == idee.idee_id


class TestPreFilterFractureDiagnosis:
    """Test-Suite für FRACTURE_DIAGNOSIS in QUARANTÄNE."""
    
    def test_pre_filter_fracture_diagnosis_in_quarantine_allowed(self):
        """Regel 3: FRACTURE_DIAGNOSIS in QUARANTÄNE → ERLAUBEN."""
        pre_filter = PreFilter()
        
        # Mock _get_zone_for_coordinate um QUARANTAENE zurückzugeben
        original_get_zone = pre_filter._get_zone_for_coordinate
        pre_filter._get_zone_for_coordinate = lambda coord: ZoneInfo(
            zone_id="quarantine_zone",
            zone_health=ZoneHealth.QUARANTAENE,
        )
        
        idee = RohIdee(
            idee_id="test-idea-fracture",
            intent=IdeenIntent.FRACTURE_DIAGNOSIS,
            ziel_koordinate={"x": 0.1},
            beschreibung="Fraktur-Diagnose in Quarantäne",
            atlas_version_ref="v1.0.0",
        )
        
        result = pre_filter.filter_idea(idee)
        
        assert result.decision == FilterDecision.ERLAUBEN
        assert result.reason == "FRACTURE_DIAGNOSIS"
    
    def test_pre_filter_non_fracture_in_quarantine_rejected(self):
        """Regel 3: Nicht-FRACTURE_DIAGNOSIS in QUARANTÄNE → VERWERFEN."""
        pre_filter = PreFilter()
        
        # Mock _get_zone_for_coordinate um QUARANTAENE zurückzugeben
        pre_filter._get_zone_for_coordinate = lambda coord: ZoneInfo(
            zone_id="quarantine_zone",
            zone_health=ZoneHealth.QUARANTAENE,
        )
        
        idee = RohIdee(
            idee_id="test-idea-non-fracture",
            intent=IdeenIntent.EXPLORATION,  # Nicht FRACTURE_DIAGNOSIS!
            ziel_koordinate={"x": 0.1},
            beschreibung="Exploration in Quarantäne",
            atlas_version_ref="v1.0.0",
        )
        
        result = pre_filter.filter_idea(idee)
        
        assert result.decision == FilterDecision.VERWERFEN
        assert result.reason == "QUARANTINE_NON_DIAGNOSTIC"


class TestPreFilterSaturated:
    """Test-Suite für Sättigung."""
    
    def test_pre_filter_rejects_saturated_zone(self):
        """⬜ Sättigung an Zielkoordinate → VERWERFEN."""
        pre_filter = PreFilter()
        
        # Mock _is_saturated um True zurückzugeben
        pre_filter._is_saturated = lambda coord: True
        
        idee = RohIdee(
            idee_id="test-idea-saturated",
            intent=IdeenIntent.EXPLORATION,
            ziel_koordinate={"x": 0.1},
            beschreibung="Gesättigte Zone",
            atlas_version_ref="v1.0.0",
        )
        
        result = pre_filter.filter_idea(idee)
        
        assert result.decision == FilterDecision.VERWERFEN
        assert result.reason == "SATURATED"


class TestPreFilterDeterministic:
    """Test-Suite für Determinismus."""
    
    def test_pre_filter_is_deterministic(self):
        """Regel 3: Pre-Filter ist deterministisch (kein LLM, kein Zufall)."""
        pre_filter = PreFilter()
        
        idee = RohIdee(
            idee_id="test-idea-deterministic",
            intent=IdeenIntent.EXPLORATION,
            ziel_koordinate={"x": 0.1},
            beschreibung="Deterministische Idee",
            atlas_version_ref="v1.0.0",
        )
        
        # Mehrmals filtern - Ergebnis muss immer gleich sein
        results = [pre_filter.filter_idea(idee) for _ in range(5)]
        
        # Alle Entscheidungen müssen gleich sein
        decisions = [r.decision for r in results]
        reasons = [r.reason for r in results]
        
        assert all(d == decisions[0] for d in decisions)
        assert all(r == reasons[0] for r in reasons)


class TestPreFilterLogging:
    """Test-Suite für Protokollierung."""
    
    def test_pre_filter_logs_filter_event(self):
        """Regel 5: Jede Entscheidung wird als filter_event protokolliert."""
        pre_filter = PreFilter()
        
        idee = RohIdee(
            idee_id="test-idea-log",
            intent=IdeenIntent.EXPLORATION,
            ziel_koordinate={"x": 0.1},
            beschreibung="Protokollierte Idee",
            atlas_version_ref="v1.0.0",
        )
        
        result = pre_filter.filter_idea(idee)
        
        assert result.filter_event is not None
        assert result.filter_event.idee_id == idee.idee_id
        assert result.filter_event.decision == result.decision
        assert len(pre_filter.get_filter_events()) == 1
    
    def test_pre_filter_filter_event_has_signal_snapshot(self):
        """filter_event enthält signal_snapshot zum Zeitpunkt der Prüfung."""
        pre_filter = PreFilter()
        
        idee = RohIdee(
            idee_id="test-idea-snapshot",
            intent=IdeenIntent.EXPLORATION,
            ziel_koordinate={"x": 0.1},
            beschreibung="Idee mit Snapshot",
            atlas_version_ref="v1.0.0",
        )
        
        result = pre_filter.filter_idea(idee)
        
        assert hasattr(result.filter_event, "signal_snapshot")
        assert isinstance(result.filter_event.signal_snapshot, dict)
        assert hasattr(result.filter_event, "timestamp")
        assert result.filter_event.timestamp is not None


class TestPreFilterIntegration:
    """Integrationstests für Pre-Filter."""
    
    def test_pre_filter_idea_geprueft_written_to_wal(self):
        """IDEE_GEPRÜFT wird im WAL protokolliert."""
        # Platzhalter für WAL-Integration
        pre_filter = PreFilter()
        
        idee = RohIdee(
            idee_id="test-idea-wal",
            intent=IdeenIntent.EXPLORATION,
            ziel_koordinate={"x": 0.1},
            beschreibung="WAL-Idee",
            atlas_version_ref="v1.0.0",
        )
        
        result = pre_filter.filter_idea(idee)
        
        assert result.decision == FilterDecision.ERLAUBEN
        assert result.filter_event is not None
    
    def test_pre_filter_idea_verworfen_written_to_wal(self):
        """IDEE_VERWORFEN wird im WAL protokolliert."""
        # Platzhalter für WAL-Integration
        pre_filter = PreFilter()
        
        idee = RohIdee(
            idee_id="test-idea-rejected",
            intent=IdeenIntent.EXPLORATION,
            ziel_koordinate={"x": 1e15},  # Physikalisch unmöglich
            beschreibung="Verworfene Idee",
            atlas_version_ref="v1.0.0",
        )
        
        result = pre_filter.filter_idea(idee)
        
        assert result.decision == FilterDecision.VERWERFEN
        assert result.filter_event is not None
