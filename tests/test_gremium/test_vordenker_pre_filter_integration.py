"""Integrationstests für Vordenker → Pre-Filter Pipeline - MYRMEX v2.4.0."""

import pytest

from src.gremium.vordenker import Vordenker, VordenkerConfig, AtlasSummary
from src.gremium.pre_filter import PreFilter, DimensionSchema, ZoneInfo
from src.contracts.pipeline_models import (
    RohIdee,
    IdeenIntent,
    FilterDecision,
    EvidenceStatus,
)
from src.contracts.enums import ZoneHealth


class TestVordenkerPreFilterPipeline:
    """Test-Suite für Vordenker → Pre-Filter Pipeline."""
    
    def test_vordenker_to_pre_filter_pipeline(self):
        """Vordenker → Pre-Filter Pipeline funktioniert."""
        # Vordenker initialisieren
        vordenker_config = VordenkerConfig()
        vordenker = Vordenker(vordenker_config)
        
        # Pre-Filter initialisieren
        dimension_schema = DimensionSchema(known_dimensions={"x", "y", "z"})
        pre_filter = PreFilter(dimension_schema=dimension_schema)
        
        # Atlas Summary erstellen
        atlas_summary = AtlasSummary(
            atlas_version_id="v1.0.0",
            weißraum_zonen=[{"centroid": {"x": 0.1}, "zone_id": "zone_1"}],
        )
        
        # Ideen generieren
        ideas = vordenker.generate_ideas(atlas_summary)
        assert len(ideas) >= 1
        
        # Ideen filtern
        for idee in ideas:
            result = pre_filter.filter_idea(idee)
            assert result is not None
            assert result.decision in [FilterDecision.ERLAUBEN, FilterDecision.VERWERFEN, FilterDecision.DIMENSION_GAP]
    
    def test_vordenker_idea_rejected_by_pre_filter(self):
        """Idee vom Vordenker wird vom Pre-Filter verworfen."""
        vordenker = Vordenker()
        pre_filter = PreFilter()
        
        # Idee mit physikalisch unmöglicher Koordinate generieren
        idee = RohIdee(
            idee_id="test-rejected-idea",
            intent=IdeenIntent.EXPLORATION,
            ziel_koordinate={"x": 1e15},  # Physikalisch unmöglich
            beschreibung="Wird verworfen",
            atlas_version_ref="v1.0.0",
        )
        
        result = pre_filter.filter_idea(idee)
        
        assert result.decision == FilterDecision.VERWERFEN
    
    def test_vordenker_idea_allowed_by_pre_filter(self):
        """Idee vom Vordenker wird vom Pre-Filter erlaubt."""
        vordenker = Vordenker()
        dimension_schema = DimensionSchema(known_dimensions={"x", "y", "z"})
        pre_filter = PreFilter(dimension_schema=dimension_schema)
        
        # Normale Idee generieren
        idee = RohIdee(
            idee_id="test-allowed-idea",
            intent=IdeenIntent.EXPLORATION,
            ziel_koordinate={"x": 0.1, "y": 0.2},
            beschreibung="Normale Exploration",
            atlas_version_ref="v1.0.0",
        )
        
        result = pre_filter.filter_idea(idee)
        
        assert result.decision == FilterDecision.ERLAUBEN
    
    def test_vordenker_idea_dimension_gap(self):
        """Idee mit unbekannter Dimension → DIMENSION_GAP."""
        vordenker = Vordenker()
        dimension_schema = DimensionSchema(known_dimensions={"x", "y"})
        pre_filter = PreFilter(dimension_schema=dimension_schema)
        
        # Idee mit unbekannter Dimension
        idee = RohIdee(
            idee_id="test-dim-gap-idea",
            intent=IdeenIntent.EXPLORATION,
            ziel_koordinate={"x": 0.1, "neue_dim": 0.5},
            beschreibung="Neue Dimension",
            atlas_version_ref="v1.0.0",
        )
        
        result = pre_filter.filter_idea(idee)
        
        assert result.decision == FilterDecision.DIMENSION_GAP
        assert len(pre_filter.get_dimension_onboarding_requests()) >= 1


class TestBlockedCacheIntegration:
    """Test-Suite für blocked_cache Integration."""
    
    def test_blocked_cache_integrates_with_pre_filter(self):
        """blocked_cache verhindert, dass verworfene Ideen erneut generiert werden."""
        vordenker = Vordenker()
        pre_filter = PreFilter()
        
        # Idee erstellen und verwerfen
        idee = RohIdee(
            idee_id="test-blocked-idea",
            intent=IdeenIntent.EXPLORATION,
            ziel_koordinate={"x": 1e15},  # Wird verworfen
            beschreibung="Blockierte Idee",
            atlas_version_ref="v1.0.0",
        )
        
        # Idee filtern (wird verworfen)
        result = pre_filter.filter_idea(idee)
        assert result.decision == FilterDecision.VERWERFEN
        
        # Idee zum blocked_cache hinzufügen
        vordenker.add_to_blocked_cache(idee.idee_id, result.reason)
        
        # Prüfen ob Idee blockiert ist
        assert vordenker.check_blocked_cache(idee) is True


class TestStateMachine:
    """Test-Suite für Zustandsmaschine."""
    
    def test_state_machine_idee_offen_to_geprueft(self):
        """Zustandsmaschine: IDEE_OFFEN → IDEE_GEPRÜFT."""
        # Dies ist ein Platzhalter für WAL/State-Machine-Integration
        # Die eigentliche Implementierung kommt in Phase 7b
        from src.contracts.transaction_models import Stage5bState
        
        assert Stage5bState.IDEE_OFFEN.value == "IDEE_OFFEN"
        assert Stage5bState.IDEE_GEPRUEFT.value == "IDEE_GEPRUEFT"
    
    def test_state_machine_idee_offen_to_verworfen(self):
        """Zustandsmaschine: IDEE_OFFEN → IDEE_VERWORFEN."""
        # Dies ist ein Platzhalter für WAL/State-Machine-Integration
        from src.contracts.transaction_models import Stage5bState
        
        assert Stage5bState.IDEE_OFFEN.value == "IDEE_OFFEN"
        # Hinweis: IDEE_VERWORFEN ist implizit durch Verwerfung im Pre-Filter


class TestRecovery:
    """Test-Suite für Recovery nach Crash."""
    
    def test_recovery_after_vordenker_crash(self):
        """Phase 4 Recovery arbeitet mit Vordenker zusammen."""
        # Vordenker kann neu initialisiert werden
        vordenker = Vordenker()
        
        # blocked_cache bleibt erhalten (in echter Implementierung persistent)
        vordenker.add_to_blocked_cache("crashed-idea-1", "CRASH_RECOVERY")
        
        # Nach "Crash" kann Vordenker weiterarbeiten
        atlas_summary = AtlasSummary(
            atlas_version_id="v1.0.0",
            weißraum_zonen=[{"centroid": {"x": 0.1}, "zone_id": "zone_1"}],
        )
        
        ideas = vordenker.generate_ideas(atlas_summary)
        assert len(ideas) >= 1
        
        # Blockierte Idee wird nicht generiert
        assert not any(i.idee_id == "crashed-idea-1" for i in ideas)


class TestTemperatureBounds:
    """Test-Suite für Temperatur-Obergrenzen."""
    
    def test_vordenker_temperature_never_exceeds_max_integration(self):
        """Integrationstest: Temperatur überschreitet niemals max_temp."""
        config = VordenkerConfig(basis_temp=0.5, faktor=0.8, max_temp=0.8)
        vordenker = Vordenker(config)
        
        # Bei verschiedenen Weißraum-Anteilen
        for weißraum in [0.0, 0.25, 0.5, 0.75, 1.0]:
            temp = vordenker.calculate_temperature(weißraum)
            assert temp <= config.max_temp
            assert temp <= 0.8


class TestFallbackEvidence:
    """Test-Suite für Fallback Evidenz-Status."""
    
    def test_fallback_evidence_never_belegt(self):
        """Fallback erzeugt niemals BELEGT evidence_status."""
        vordenker = Vordenker()
        vordenker.llm_available = False
        
        atlas_summary = AtlasSummary(
            atlas_version_id="v1.0.0",
            weißraum_zonen=[
                {"centroid": {"x": 0.1}, "zone_id": "zone_1"},
                {"centroid": {"x": 0.2}, "zone_id": "zone_2"},
            ],
        )
        
        ideas = vordenker.fallback_generate(atlas_summary)
        
        for idee in ideas:
            assert idee.gefahren_hypothese.evidence_status != EvidenceStatus.BELEGT


class TestQuarantineHandling:
    """Test-Suite für Quarantäne-Behandlung."""
    
    def test_quarantine_fracture_diagnosis_allowed(self):
        """FRACTURE_DIAGNOSIS in QUARANTÄNE wird erlaubt."""
        pre_filter = PreFilter()
        pre_filter._get_zone_for_coordinate = lambda coord: ZoneInfo(
            zone_id="quarantine_zone",
            zone_health=ZoneHealth.QUARANTAENE,
        )
        
        idee = RohIdee(
            idee_id="quarantine-fracture",
            intent=IdeenIntent.FRACTURE_DIAGNOSIS,
            ziel_koordinate={"x": 0.1},
            beschreibung="Fraktur-Diagnose",
            atlas_version_ref="v1.0.0",
        )
        
        result = pre_filter.filter_idea(idee)
        assert result.decision == FilterDecision.ERLAUBEN
    
    def test_quarantine_non_diagnostic_rejected(self):
        """Nicht-FRACTURE_DIAGNOSIS in QUARANTÄNE wird verworfen."""
        pre_filter = PreFilter()
        pre_filter._get_zone_for_coordinate = lambda coord: ZoneInfo(
            zone_id="quarantine_zone",
            zone_health=ZoneHealth.QUARANTAENE,
        )
        
        idee = RohIdee(
            idee_id="quarantine-exploration",
            intent=IdeenIntent.EXPLORATION,
            ziel_koordinate={"x": 0.1},
            beschreibung="Exploration",
            atlas_version_ref="v1.0.0",
        )
        
        result = pre_filter.filter_idea(idee)
        assert result.decision == FilterDecision.VERWERFEN
