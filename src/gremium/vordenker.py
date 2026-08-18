"""Vordenker (Stufe 4) - Ideen-Generierung für MYRMEX v2.4.0."""

import uuid
from datetime import datetime, timezone
from typing import Any

from src.contracts.pipeline_models import (
    RohIdee,
    IdeenIntent,
    GefahrenHypothese,
    EvidenceStatus,
    BlockedCacheEntry,
)


class AtlasSummary:
    """Zusammenfassung des Atlas für den Vordenker."""
    
    def __init__(
        self,
        atlas_version_id: str,
        weißraum_anteil: float = 0.0,
        bekannte_zonen: list[dict[str, Any]] | None = None,
        weißraum_zonen: list[dict[str, Any]] | None = None,
    ):
        self.atlas_version_id = atlas_version_id
        self.weißraum_anteil = max(0.0, min(1.0, weißraum_anteil))
        self.bekannte_zonen = bekannte_zonen or []
        self.weißraum_zonen = weißraum_zonen or []
    
    def get_weissraum_zones(self) -> list[dict[str, Any]]:
        """Gibt die Weißraum-Zonen zurück."""
        return self.weißraum_zonen


class VordenkerConfig:
    """Konfiguration für den Vordenker."""
    
    def __init__(
        self,
        basis_temp: float = 0.3,
        faktor: float = 0.5,
        max_temp: float = 0.8,
        high_watermark: int = 100,
        low_watermark: int = 20,
        max_ideas_per_call: int = 5,
    ):
        self.basis_temp = basis_temp
        self.faktor = faktor
        self.max_temp = max_temp
        self.high_watermark = high_watermark
        self.low_watermark = low_watermark
        self.max_ideas_per_call = max_ideas_per_call


class Vordenker:
    """
    Vordenker (Stufe 4) - Generiert Forschungsideen.
    
    Regel 1: Adaptive Temperatur hat eine Obergrenze
    Regel 4: blocked_cache verhindert Duplikate
    Regel 6: Deterministischer Fallback bei LLM-Ausfall
    Regel 7: High/Low-Watermarks für den Ideen-Puffer
    """
    
    def __init__(self, config: VordenkerConfig | None = None):
        self.config = config or VordenkerConfig()
        self.blocked_cache: dict[str, BlockedCacheEntry] = {}
        self.ideen_puffer: list[RohIdee] = []
        self.llm_available = True  # Kann auf False gesetzt werden für Fallback
    
    def calculate_temperature(self, weißraum_anteil: float) -> float:
        """
        Regel 1: Adaptive Temperatur mit harter Obergrenze.
        
        temperatur = basis + (weißraum_anteil × faktor)
        temperatur = min(temperatur, max_temp)
        """
        weißraum_anteil = max(0.0, min(1.0, weißraum_anteil))
        temperatur = self.config.basis_temp + (weißraum_anteil * self.config.faktor)
        # KRITISCH: Harte Obergrenze
        return min(temperatur, self.config.max_temp)
    
    def check_blocked_cache(self, idee: RohIdee) -> bool:
        """Regel 4: Prüft ob eine Idee im blocked_cache ist."""
        return idee.idee_id in self.blocked_cache
    
    def add_to_blocked_cache(self, idee_id: str, grund: str) -> None:
        """Regel 4: Fügt eine Idee zum blocked_cache hinzu."""
        entry = BlockedCacheEntry(
            idee_id=idee_id,
            grund=grund,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self.blocked_cache[idee_id] = entry
    
    def generate_ideas(
        self,
        atlas_summary: AtlasSummary,
        kontext: dict[str, Any] | None = None,
    ) -> list[RohIdee]:
        """
        Generiert 1-5 Ideen pro Aufruf.
        
        Regel 7: High/Low-Watermarks beachten.
        Regel 6: Bei LLM-Ausfall Fallback verwenden.
        """
        # Regel 7: High-Watermark prüfen
        if len(self.ideen_puffer) >= self.config.high_watermark:
            return []  # Keine neuen Ideen bei vollem Puffer
        
        # Regel 6: Fallback wenn LLM nicht verfügbar
        if not self.llm_available:
            ideas = self.fallback_generate(atlas_summary)
        else:
            # Mock-LLM-Generierung (deterministisch für Tests)
            ideas = self._mock_llm_generate(atlas_summary, kontext or {})
        
        # Ideen filtern (blocked_cache) und Puffer füllen
        filtered_ideas = []
        for idee in ideas:
            if not self.check_blocked_cache(idee):
                filtered_ideas.append(idee)
                self.ideen_puffer.append(idee)
        
        return filtered_ideas
    
    def _mock_llm_generate(
        self,
        atlas_summary: AtlasSummary,
        kontext: dict[str, Any],
    ) -> list[RohIdee]:
        """Mock-LLM-Generierung für Testphase."""
        ideas = []
        num_ideas = min(
            self.config.max_ideas_per_call,
            max(1, len(atlas_summary.weißraum_zonen)),
        )
        
        for i in range(num_ideas):
            zone = atlas_summary.weißraum_zonen[i % len(atlas_summary.weißraum_zonen)] if atlas_summary.weißraum_zonen else {"centroid": {"x": i * 0.1}, "zone_id": f"zone_{i}"}
            
            idee = RohIdee(
                idee_id=str(uuid.uuid4()),
                intent=IdeenIntent.EXPLORATION,
                ziel_koordinate=zone.get("centroid", {"x": i * 0.1}),
                beschreibung=f"Erkunde Zone {zone.get('zone_id', f'unknown_{i}')}",
                gefahren_hypothese=GefahrenHypothese(
                    beschreibung="Unbekanntes Gebiet",
                    evidence_status=EvidenceStatus.HYPOTHETISCH,
                    referenzen=[],
                ),
                proposed_dimensions=[],
                atlas_version_ref=atlas_summary.atlas_version_id,
            )
            ideas.append(idee)
        
        return ideas if ideas else [self._create_fallback_exploration_idea(atlas_summary)]
    
    def fallback_generate(self, atlas_summary: AtlasSummary) -> list[RohIdee]:
        """
        Regel 6: Deterministischer Fallback bei LLM-Ausfall.
        
        Generiert einfache, regelbasierte Ideen.
       证据_status ist immer HYPOTHETISCH oder UNBEKANNT, nie BELEGT.
        """
        ideas = []
        weißraum_zonen = atlas_summary.get_weissraum_zones()
        
        # Max 3 Ideen generieren
        for i, zone in enumerate(weißraum_zonen[:3]):
            idee = RohIdee(
                idee_id=str(uuid.uuid4()),
                intent=IdeenIntent.EXPLORATION,
                ziel_koordinate=zone.get("centroid", {"x": i * 0.1}),
                beschreibung=f"Erkunde Weißraum-Zone {zone.get('zone_id', f'unknown_{i}')}",
                gefahren_hypothese=GefahrenHypothese(
                    beschreibung="Unbekanntes Gebiet",
                    evidence_status=EvidenceStatus.UNBEKANNT,  # NIEMALS BELEGT!
                    referenzen=[],
                ),
                proposed_dimensions=[],
                atlas_version_ref=atlas_summary.atlas_version_id,
            )
            ideas.append(idee)
        
        # Falls keine Weißraum-Zonen, erstelle Standard-Exploration
        if not ideas:
            ideas.append(self._create_fallback_exploration_idea(atlas_summary))
        
        return ideas
    
    def _create_fallback_exploration_idea(self, atlas_summary: AtlasSummary) -> RohIdee:
        """Erstellt eine einfache Fallback-Explorationsidee."""
        return RohIdee(
            idee_id=str(uuid.uuid4()),
            intent=IdeenIntent.EXPLORATION,
            ziel_koordinate={"x": 0.5, "y": 0.5},
            beschreibung="Erkunde zentrale Weißraum-Zone",
            gefahren_hypothese=GefahrenHypothese(
                beschreibung="Standard-Exploration",
                evidence_status=EvidenceStatus.HYPOTHETISCH,
                referenzen=[],
            ),
            proposed_dimensions=[],
            atlas_version_ref=atlas_summary.atlas_version_id,
        )
    
    def clear_buffer_below_low_watermark(self) -> None:
        """Regel 7: Puffer unter Low-Watermark leeren."""
        while len(self.ideen_puffer) > self.config.low_watermark:
            self.ideen_puffer.pop(0)
    
    def should_generate_more(self) -> bool:
        """Regel 7: Prüft ob neue Ideen generiert werden sollen."""
        return len(self.ideen_puffer) < self.config.low_watermark
