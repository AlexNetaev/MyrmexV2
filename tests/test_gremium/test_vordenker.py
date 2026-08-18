"""Tests für Vordenker (Stufe 4) - MYRMEX v2.4.0."""

import pytest
from unittest.mock import MagicMock

from src.gremium.vordenker import Vordenker, VordenkerConfig, AtlasSummary
from src.contracts.pipeline_models import (
    RohIdee,
    IdeenIntent,
    GefahrenHypothese,
    EvidenceStatus,
)


class TestVordenkerGeneratesIdeas:
    """Test-Suite für Ideen-Generierung."""
    
    def test_vordenker_generates_ideas(self):
        """Vordenker generiert 1-5 Ideen."""
        config = VordenkerConfig(max_ideas_per_call=5)
        vordenker = Vordenker(config)
        
        atlas_summary = AtlasSummary(
            atlas_version_id="v1.0.0",
            weißraum_anteil=0.5,
            weißraum_zonen=[
                {"centroid": {"x": 0.1}, "zone_id": "zone_1"},
                {"centroid": {"x": 0.2}, "zone_id": "zone_2"},
                {"centroid": {"x": 0.3}, "zone_id": "zone_3"},
            ],
        )
        
        ideas = vordenker.generate_ideas(atlas_summary)
        
        assert len(ideas) >= 1
        assert len(ideas) <= 5
    
    def test_vordenker_generates_at_least_one_idea(self):
        """Vordenker generiert mindestens eine Idee auch ohne Weißraum-Zonen."""
        config = VordenkerConfig()
        vordenker = Vordenker(config)
        
        atlas_summary = AtlasSummary(
            atlas_version_id="v1.0.0",
            weißraum_anteil=0.0,
            weißraum_zonen=[],
        )
        
        ideas = vordenker.generate_ideas(atlas_summary)
        
        assert len(ideas) >= 1


class TestVordenkerAdaptiveTemperature:
    """Test-Suite für adaptive Temperatur."""
    
    def test_vordenker_adaptive_temperature(self):
        """Regel 1: Temperatur ist adaptiv."""
        config = VordenkerConfig(basis_temp=0.3, faktor=0.5, max_temp=0.8)
        vordenker = Vordenker(config)
        
        # Bei weißraum_anteil=0.0
        temp_0 = vordenker.calculate_temperature(0.0)
        assert temp_0 == 0.3  # basis_temp
        
        # Bei weißraum_anteil=0.5
        temp_05 = vordenker.calculate_temperature(0.5)
        assert temp_05 == 0.3 + (0.5 * 0.5)  # 0.55
        
        # Bei weißraum_anteil=1.0
        temp_1 = vordenker.calculate_temperature(1.0)
        assert temp_1 == 0.3 + (1.0 * 0.5)  # 0.8
    
    def test_vordenker_temperature_has_upper_bound(self):
        """Regel 1 (KRITISCH): Temperatur hat harte Obergrenze max_temp."""
        config = VordenkerConfig(basis_temp=0.3, faktor=0.7, max_temp=0.8)
        vordenker = Vordenker(config)
        
        # Auch bei hohem weißraum_anteil darf max_temp nicht überschritten werden
        temp = vordenker.calculate_temperature(1.0)
        assert temp <= config.max_temp
    
    def test_vordenker_temperature_never_exceeds_max(self):
        """Regel 1: Auch bei weißraum_anteil=1.0 wird max_temp nicht überschritten."""
        config = VordenkerConfig(basis_temp=0.5, faktor=0.8, max_temp=0.8)
        vordenker = Vordenker(config)
        
        # Selbst wenn basis + (1.0 * faktor) > max_temp
        temp = vordenker.calculate_temperature(1.0)
        assert temp == config.max_temp  # Muss genau max_temp sein (gecappt)
        assert temp <= config.max_temp
    
    def test_vordenker_temperature_clamped_to_max(self):
        """Temperatur wird bei max_temp gecapped."""
        config = VordenkerConfig(basis_temp=0.6, faktor=0.5, max_temp=0.8)
        vordenker = Vordenker(config)
        
        # 0.6 + (1.0 * 0.5) = 1.1, aber max_temp ist 0.8
        temp = vordenker.calculate_temperature(1.0)
        assert temp == 0.8


class TestVordenkerIdeaAttributes:
    """Test-Suite für Ideen-Attribute."""
    
    def test_vordenker_idea_has_intent(self):
        """Jede Idee hat einen intent (EXPLORATION, VERFEINERUNG, etc.)."""
        config = VordenkerConfig()
        vordenker = Vordenker(config)
        
        atlas_summary = AtlasSummary(
            atlas_version_id="v1.0.0",
            weißraum_zonen=[{"centroid": {"x": 0.1}, "zone_id": "zone_1"}],
        )
        
        ideas = vordenker.generate_ideas(atlas_summary)
        
        for idee in ideas:
            assert hasattr(idee, "intent")
            assert idee.intent in [IdeenIntent.EXPLORATION, IdeenIntent.VERFEINERUNG, IdeenIntent.FRACTURE_DIAGNOSIS, IdeenIntent.MITIGATION]
    
    def test_vordenker_idea_has_gefahren_hypothese(self):
        """Jede Idee hat eine gefahren_hypothese."""
        config = VordenkerConfig()
        vordenker = Vordenker(config)
        
        atlas_summary = AtlasSummary(
            atlas_version_id="v1.0.0",
            weißraum_zonen=[{"centroid": {"x": 0.1}, "zone_id": "zone_1"}],
        )
        
        ideas = vordenker.generate_ideas(atlas_summary)
        
        for idee in ideas:
            assert hasattr(idee, "gefahren_hypothese")
            assert isinstance(idee.gefahren_hypothese, GefahrenHypothese)
    
    def test_vordenker_gefahren_hypothese_evidence_status(self):
        """gefahren_hypothese hat evidence_status (BELEGT, HYPOTHETISCH, UNBEKANNT)."""
        config = VordenkerConfig()
        vordenker = Vordenker(config)
        
        atlas_summary = AtlasSummary(
            atlas_version_id="v1.0.0",
            weißraum_zonen=[{"centroid": {"x": 0.1}, "zone_id": "zone_1"}],
        )
        
        ideas = vordenker.generate_ideas(atlas_summary)
        
        for idee in ideas:
            assert hasattr(idee.gefahren_hypothese, "evidence_status")
            assert idee.gefahren_hypothese.evidence_status in [
                EvidenceStatus.BELEGT,
                EvidenceStatus.HYPOTHETISCH,
                EvidenceStatus.UNBEKANNT,
            ]
    
    def test_vordenker_idea_has_atlas_version_ref(self):
        """Jede Idee hat atlas_version_ref."""
        config = VordenkerConfig()
        vordenker = Vordenker(config)
        
        atlas_summary = AtlasSummary(
            atlas_version_id="v1.0.0",
            weißraum_zonen=[{"centroid": {"x": 0.1}, "zone_id": "zone_1"}],
        )
        
        ideas = vordenker.generate_ideas(atlas_summary)
        
        for idee in ideas:
            assert hasattr(idee, "atlas_version_ref")
            assert idee.atlas_version_ref == "v1.0.0"


class TestVordenkerBlockedCache:
    """Test-Suite für blocked_cache."""
    
    def test_vordenker_blocked_cache_prevents_duplicates(self):
        """Regel 4: blocked_cache verhindert doppelte Ideen."""
        config = VordenkerConfig()
        vordenker = Vordenker(config)
        
        idee = RohIdee(
            idee_id="test-idea-1",
            intent=IdeenIntent.EXPLORATION,
            ziel_koordinate={"x": 0.1},
            beschreibung="Test Idee",
            atlas_version_ref="v1.0.0",
        )
        
        # Idee zum blocked_cache hinzufügen
        vordenker.add_to_blocked_cache(idee.idee_id, "TEST_BLOCK")
        
        # Prüfen ob Idee blockiert ist
        assert vordenker.check_blocked_cache(idee) is True
    
    def test_vordenker_blocked_cache_add(self):
        """Regel 4: Verworfene Ideen werden zum blocked_cache hinzugefügt."""
        config = VordenkerConfig()
        vordenker = Vordenker(config)
        
        idee_id = "test-idea-2"
        grund = "RED_SIGNAL"
        
        vordenker.add_to_blocked_cache(idee_id, grund)
        
        assert idee_id in vordenker.blocked_cache
        assert vordenker.blocked_cache[idee_id].grund == grund


class TestVordenkerFallback:
    """Test-Suite für deterministischen Fallback."""
    
    def test_vordenker_fallback_when_llm_unavailable(self):
        """Regel 6: Deterministischer Fallback bei LLM-Ausfall."""
        config = VordenkerConfig()
        vordenker = Vordenker(config)
        vordenker.llm_available = False  # LLM nicht verfügbar
        
        atlas_summary = AtlasSummary(
            atlas_version_id="v1.0.0",
            weißraum_zonen=[
                {"centroid": {"x": 0.1}, "zone_id": "zone_1"},
                {"centroid": {"x": 0.2}, "zone_id": "zone_2"},
            ],
        )
        
        ideas = vordenker.generate_ideas(atlas_summary)
        
        assert len(ideas) >= 1
        # Fallback sollte immer funktionieren
    
    def test_vordenker_fallback_never_belegt_evidence(self):
        """Regel 6: Fallback erzeugt NIEMALS evidence_status=BELEGT."""
        config = VordenkerConfig()
        vordenker = Vordenker(config)
        vordenker.llm_available = False  # LLM nicht verfügbar
        
        atlas_summary = AtlasSummary(
            atlas_version_id="v1.0.0",
            weißraum_zonen=[
                {"centroid": {"x": 0.1}, "zone_id": "zone_1"},
            ],
        )
        
        ideas = vordenker.fallback_generate(atlas_summary)
        
        for idee in ideas:
            assert idee.gefahren_hypothese.evidence_status != EvidenceStatus.BELEGT
            assert idee.gefahren_hypothese.evidence_status in [
                EvidenceStatus.HYPOTHETISCH,
                EvidenceStatus.UNBEKANNT,
            ]


class TestVordenkerWatermarks:
    """Test-Suite für High/Low-Watermarks."""
    
    def test_vordenker_high_watermark_stops_generation(self):
        """Regel 7: Bei High-Watermark werden keine neuen Ideen generiert."""
        config = VordenkerConfig(high_watermark=5, low_watermark=2)
        vordenker = Vordenker(config)
        
        # Puffer füllen bis high_watermark
        for i in range(5):
            idee = RohIdee(
                idee_id=f"idea-{i}",
                intent=IdeenIntent.EXPLORATION,
                ziel_koordinate={"x": 0.1},
                beschreibung=f"Idee {i}",
                atlas_version_ref="v1.0.0",
            )
            vordenker.ideen_puffer.append(idee)
        
        # Jetzt sollte keine neue Idee generiert werden
        atlas_summary = AtlasSummary(
            atlas_version_id="v1.0.0",
            weißraum_zonen=[{"centroid": {"x": 0.1}, "zone_id": "zone_1"}],
        )
        
        ideas = vordenker.generate_ideas(atlas_summary)
        assert len(ideas) == 0
    
    def test_vordenker_low_watermark_resumes_generation(self):
        """Regel 7: Bei Low-Watermark wird die Generierung fortgesetzt."""
        config = VordenkerConfig(high_watermark=10, low_watermark=3)
        vordenker = Vordenker(config)
        
        # Puffer unter low_watermark
        for i in range(2):
            idee = RohIdee(
                idee_id=f"idea-{i}",
                intent=IdeenIntent.EXPLORATION,
                ziel_koordinate={"x": 0.1},
                beschreibung=f"Idee {i}",
                atlas_version_ref="v1.0.0",
            )
            vordenker.ideen_puffer.append(idee)
        
        # Jetzt sollten neue Ideen generiert werden
        atlas_summary = AtlasSummary(
            atlas_version_id="v1.0.0",
            weißraum_zonen=[{"centroid": {"x": 0.1}, "zone_id": "zone_1"}],
        )
        
        ideas = vordenker.generate_ideas(atlas_summary)
        assert len(ideas) >= 1


class TestVordenkerIntegration:
    """Integrationstests für Vordenker."""
    
    def test_vordenker_idea_written_to_wal(self):
        """IDEE_OFFEN wird im WAL protokolliert."""
        # Dies ist ein Platzhalter für WAL-Integrationstests
        # Die eigentliche WAL-Integration kommt in Phase 7b
        config = VordenkerConfig()
        vordenker = Vordenker(config)
        
        atlas_summary = AtlasSummary(
            atlas_version_id="v1.0.0",
            weißraum_zonen=[{"centroid": {"x": 0.1}, "zone_id": "zone_1"}],
        )
        
        ideas = vordenker.generate_ideas(atlas_summary)
        
        assert len(ideas) >= 1
        assert ideas[0].status == "OFFEN"
