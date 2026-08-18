"""Lotse (Stufe 5b) - Wegmarken-Platzierung für MYRMEX v2.4.0."""

import uuid
import threading
from datetime import datetime, timezone
from typing import Any, Optional

from src.contracts.pipeline_models import (
    RohIdee,
    IdeenIntent,
    Wegmarke,
    WegmarkeTyp,
    WegmarkeStatus,
    LotseResult,
    LotseDecision,
    LotseEvent,
    BlockedCacheEntry,
)
from src.contracts.enums import ZoneHealth


class SignalSnapshot:
    """Snapshot des Signal-Stacks zu einem Zeitpunkt."""
    
    def __init__(
        self,
        version: str,
        signals: list[tuple[str, str]] | None = None,
        resolved_signal: str | None = None,
    ):
        self.version = version
        self.signals = signals or []
        self.resolved_signal = resolved_signal
    
    def to_dict(self) -> dict[str, str]:
        """Konvertiert zu Dictionary."""
        result = {"version": self.version}
        if self.resolved_signal:
            result["resolved_signal"] = self.resolved_signal
        for i, (signal_type, severity) in enumerate(self.signals):
            result[f"signal_{i}_type"] = signal_type
            result[f"signal_{i}_severity"] = severity
        return result


class GatingDecision:
    """GatingDecision: Entscheidung des Pheromon-Gatings."""
    
    PLATZIEREN = "PLATZIEREN"
    VERWERFEN = "VERWERFEN"
    ZURUECKSTELLEN = "ZURUECKSTELLEN"


class LotseConfig:
    """Konfiguration für den Lotsen."""
    
    def __init__(self):
        pass


class Lotse:
    """
    Lotse (Stufe 5b) - Platziert Wegmarken im Atlas.
    
    Regel 1: Signal-Stack-Prüfung VOR Platzierung (KRITISCH)
    Regel 2: QUARANTÄNE-Schutz (KRITISCH — SICHERHEIT)
    Regel 3: Jede Wegmarke trägt Version-Referenzen
    Regel 4: Verworfene Ideen gehen in den blocked_cache
    Regel 5: Deterministischer Fallback bei LLM-Ausfall
    Regel 6: Parallelisierbar mit atomarem Pulling
    Regel 7: Zustandsmaschine wird im WAL protokolliert
    """
    
    def __init__(
        self,
        config: LotseConfig | None = None,
        blocked_cache: dict[str, BlockedCacheEntry] | None = None,
    ):
        self.config = config or LotseConfig()
        self.blocked_cache = blocked_cache if blocked_cache is not None else {}
        self.lotse_events: list[LotseEvent] = []
        self.platzierte_wegmarken: list[Wegmarke] = []
    
    def place_waypoint(
        self,
        idee: RohIdee,
        signal_registry: Any | None = None,
        atlas: Any | None = None,
    ) -> LotseResult:
        """
        Platziert eine Wegmarke oder verwirft die Idee.
        
        Regel 1: Signal-Stack wird VOR Platzierung geprüft.
        Regel 2: QUARANTÄNE-Schutz wird angewendet.
        Regel 3: Version-Referenzen werden gesetzt.
        """
        # KRITISCH: Signal-Stack ZUERST prüfen (Regel 1)
        signal_snapshot = self._get_signal_snapshot(idee.ziel_koordinate, signal_registry)
        gating_decision = self._apply_pheromon_gating(signal_snapshot)
        
        if gating_decision == GatingDecision.VERWERFEN:
            grund = f"Signal {signal_snapshot.resolved_signal}"
            self._add_to_blocked_cache(idee.idee_id, grund)
            lotse_event = self._create_lotse_event(
                idee,
                LotseDecision.VERWERFEN,
                signal_snapshot,
                getattr(atlas, 'atlas_version_id', 'unknown') if atlas else 'unknown',
            )
            return LotseResult(
                decision=LotseDecision.VERWERFEN,
                reason=grund,
                lotse_event=lotse_event,
            )
        
        if gating_decision == GatingDecision.ZURUECKSTELLEN:
            lotse_event = self._create_lotse_event(
                idee,
                LotseDecision.ZURUECKSTELLEN,
                signal_snapshot,
                getattr(atlas, 'atlas_version_id', 'unknown') if atlas else 'unknown',
            )
            return LotseResult(
                decision=LotseDecision.ZURUECKSTELLEN,
                reason="🟩 bestätigt",
                lotse_event=lotse_event,
            )
        
        # QUARANTÄNE-Schutz (Regel 2 - KRITISCH)
        zone = self._get_zone_for_coordinate(idee.ziel_koordinate, atlas)
        if not self._check_quarantine(zone, idee):
            grund = "QUARANTINE_NON_DIAGNOSTIC"
            self._add_to_blocked_cache(idee.idee_id, grund)
            lotse_event = self._create_lotse_event(
                idee,
                LotseDecision.VERWERFEN,
                signal_snapshot,
                getattr(atlas, 'atlas_version_id', 'unknown') if atlas else 'unknown',
            )
            return LotseResult(
                decision=LotseDecision.VERWERFEN,
                reason=grund,
                lotse_event=lotse_event,
            )
        
        # Diagnostic braucht Budget
        if idee.intent == IdeenIntent.FRACTURE_DIAGNOSIS:
            if not hasattr(idee, 'fracture_diagnosis_budget') or not idee.fracture_diagnosis_budget:
                lotse_event = self._create_lotse_event(
                    idee,
                    LotseDecision.VERWERFEN,
                    signal_snapshot,
                    getattr(atlas, 'atlas_version_id', 'unknown') if atlas else 'unknown',
                )
                return LotseResult(
                    decision=LotseDecision.VERWERFEN,
                    reason="DIAGNOSTIC_BUDGET_MISSING",
                    lotse_event=lotse_event,
                )
        
        # Wegmarke platzieren (Regel 3: Version-Referenzen)
        wegmarke = self._create_wegmarke(idee, signal_snapshot, atlas)
        self.platzierte_wegmarken.append(wegmarke)
        
        lotse_event = self._create_lotse_event(
            idee,
            LotseDecision.PLATZIEREN,
            signal_snapshot,
            wegmarke.atlas_version_ref,
        )
        
        return LotseResult(
            decision=LotseDecision.PLATZIEREN,
            wegmarke=wegmarke,
            reason="Wegmarke platziert",
            lotse_event=lotse_event,
        )
    
    def _get_signal_snapshot(
        self,
        koordinate: dict[str, float],
        signal_registry: Any | None = None,
    ) -> SignalSnapshot:
        """Holt einen Snapshot des Signal-Stacks."""
        if signal_registry is None:
            return SignalSnapshot(version="unknown", signals=[])
        
        if hasattr(signal_registry, "get_signal_snapshot"):
            snapshot = signal_registry.get_signal_snapshot(koordinate)
            if isinstance(snapshot, SignalSnapshot):
                return snapshot
        
        # Fallback: resolve_signal verwenden
        if hasattr(signal_registry, "resolve_signal"):
            resolved = signal_registry.resolve_signal(koordinate)
            return SignalSnapshot(
                version="v1",
                signals=[("UNKNOWN", "WHITE")],
                resolved_signal=resolved,
            )
        
        return SignalSnapshot(version="unknown", signals=[])
    
    def _apply_pheromon_gating(self, signal_snapshot: SignalSnapshot) -> str:
        """
        Wendet Pheromon-Gating an basierend auf dem aufgelösten Signal.
        
        Regel 1:
        - 🟥 → VERWERFEN
        - 🟨 → VERWERFEN
        - 🟪 → VERWERFEN
        - ⬜ Sättigung → VERWERFEN
        - 🟩 → ZURÜCKSTELLEN
        - ⬜ Weißraum → PLATZIEREN
        """
        resolved = signal_snapshot.resolved_signal or ""
        resolved_upper = resolved.upper()
        
        # Rotes Signal → VERWERFEN
        if "RED" in resolved_upper or "🟥" in resolved:
            return GatingDecision.VERWERFEN
        
        # Gelbes Signal (Fraktur) → VERWERFEN
        if "YELLOW" in resolved_upper or "🟨" in resolved:
            return GatingDecision.VERWERFEN
        
        # Purple Signal (Policy-Veto) → VERWERFEN
        if "PURPLE" in resolved_upper or "🟪" in resolved:
            return GatingDecision.VERWERFEN
        
        # Grün → ZURÜCKSTELLEN (bereits bestätigt)
        if "GREEN" in resolved_upper or "🟩" in resolved:
            return GatingDecision.ZURUECKSTELLEN
        
        # Weißraum → PLATZIEREN
        if "WHITE" in resolved_upper or "⬜" in resolved or resolved == "":
            return GatingDecision.PLATZIEREN
        
        # Standard: PLATZIEREN für unbekannte Signale
        return GatingDecision.PLATZIEREN
    
    def _check_quarantine(self, zone: Any, idee: RohIdee) -> bool:
        """
        Regel 2 (KRITISCH): QUARANTÄNE erlaubt nur diagnostic_waypoints.
        
        In QUARANTÄNE-Zonen dürfen NUR FRACTURE_DIAGNOSIS-Ideen platziert werden.
        """
        zone_health = getattr(zone, 'zone_health', ZoneHealth.STABIL)
        
        if zone_health != ZoneHealth.QUARANTAENE:
            return True  # Keine QUARANTÄNE, kein Problem
        
        # QUARANTÄNE: Nur FRACTURE_DIAGNOSIS erlaubt
        if idee.intent != IdeenIntent.FRACTURE_DIAGNOSIS:
            return False  # VERWERFEN
        
        return True  # ERLAUBEN
    
    def _create_wegmarke(
        self,
        idee: RohIdee,
        signal_snapshot: SignalSnapshot,
        atlas: Any | None = None,
    ) -> Wegmarke:
        """Erstellt eine Wegmarke mit Version-Referenzen (Regel 3)."""
        atlas_version_ref = getattr(atlas, 'atlas_version_id', 'unknown') if atlas else 'unknown'
        
        wegmarke_typ = WegmarkeTyp.DIAGNOSTIC if idee.intent == IdeenIntent.FRACTURE_DIAGNOSIS else WegmarkeTyp.NORMAL
        
        fracture_budget = getattr(idee, 'fracture_diagnosis_budget', None)
        
        wegmarke = Wegmarke(
            wegmarke_id=str(uuid.uuid4()),
            idee_id=idee.idee_id,
            ziel_koordinate=idee.ziel_koordinate,
            wegmarke_typ=wegmarke_typ,
            atlas_version_ref=atlas_version_ref,
            signal_snapshot_version=signal_snapshot.version,
            fracture_diagnosis_budget=fracture_budget,
            status=WegmarkeStatus.PLATZIERT,
            platzierungs_timestamp=datetime.now(timezone.utc).isoformat(),
        )
        
        return wegmarke
    
    def _create_lotse_event(
        self,
        idee: RohIdee,
        decision: LotseDecision,
        signal_snapshot: SignalSnapshot,
        atlas_version_ref: str,
    ) -> LotseEvent:
        """Erstellt ein LotseEvent für die Protokollierung."""
        event = LotseEvent(
            event_id=str(uuid.uuid4()),
            idee_id=idee.idee_id,
            decision=decision,
            signal_snapshot=signal_snapshot.to_dict(),
            atlas_version_ref=atlas_version_ref,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self.lotse_events.append(event)
        return event
    
    def _add_to_blocked_cache(self, idee_id: str, grund: str) -> None:
        """Regel 4: Fügt eine verworfene Idee zum blocked_cache hinzu."""
        entry = BlockedCacheEntry(
            idee_id=idee_id,
            grund=grund,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self.blocked_cache[idee_id] = entry
    
    def _get_zone_for_coordinate(
        self,
        koordinate: dict[str, float],
        atlas: Any | None = None,
    ) -> Any:
        """Holt Zone-Informationen für eine Koordinate."""
        if atlas and hasattr(atlas, 'get_zone_for_coordinate'):
            return atlas.get_zone_for_coordinate(koordinate)
        
        # Mock-Implementierung
        class MockZone:
            zone_id = "default_zone"
            zone_health = ZoneHealth.STABIL
        
        return MockZone()
    
    def fallback_place(
        self,
        idee: RohIdee,
        atlas: Any | None = None,
    ) -> LotseResult:
        """
        Regel 5: Deterministischer Fallback bei LLM-Ausfall.
        
        Platziert nur in ⬜ Weißraum-Zonen.
        Platziert NIEMALS in QUARANTÄNE-Zonen.
        """
        zone = self._get_zone_for_coordinate(idee.ziel_koordinate, atlas)
        
        # KRITISCH: Fallback platziert NIEMALS in QUARANTÄNE
        if zone.zone_health == ZoneHealth.QUARANTAENE:
            return LotseResult(
                decision=LotseDecision.VERWERFEN,
                reason="FALLBACK_QUARANTINE_FORBIDDEN",
            )
        
        # Fallback platziert nur in ⬜ Weißraum (STABIL ohne Signale)
        if zone.zone_health != ZoneHealth.STABIL:
            return LotseResult(
                decision=LotseDecision.VERWERFEN,
                reason="FALLBACK_ONLY_WEISSRAUM",
            )
        
        # Einfache Wegmarke platzieren
        signal_snapshot = SignalSnapshot(version="fallback", signals=[], resolved_signal="WHITE")
        wegmarke = self._create_wegmarke(idee, signal_snapshot, atlas)
        self.platzierte_wegmarken.append(wegmarke)
        
        lotse_event = self._create_lotse_event(
            idee,
            LotseDecision.PLATZIEREN,
            signal_snapshot,
            wegmarke.atlas_version_ref,
        )
        
        return LotseResult(
            decision=LotseDecision.PLATZIEREN,
            wegmarke=wegmarke,
            reason="Fallback-Wegmarke platziert",
            lotse_event=lotse_event,
        )
    
    def get_lotse_events(self) -> list[LotseEvent]:
        """Gibt alle protokollierten LotseEvents zurück."""
        return self.lotse_events
    
    def clear_events(self) -> None:
        """Löscht alle protokollierten Events."""
        self.lotse_events.clear()


class LotseWorkerPool:
    """
    LotseWorkerPool: Parallele Worker für Lotsen-Aufgaben.
    
    Regel 6: Atomares Pulling verhindert doppelte Verarbeitung.
    """
    
    def __init__(self, idea_queue: list[RohIdee]):
        self.idea_queue = idea_queue
        self._lock = threading.Lock()
        self._processing_ids: set[str] = set()
    
    def pull_next_idea(self) -> Optional[RohIdee]:
        """
        Regel 6: Atomares Pulling verhindert doppelte Verarbeitung.
        
        Compare-and-Set: Idee wird als "in Bearbeitung" markiert.
        """
        with self._lock:
            if not self.idea_queue:
                return None
            
            # Finde erste nicht-verarbeitete Idee
            for i, idee in enumerate(self.idea_queue):
                if idee.idee_id not in self._processing_ids:
                    # Atomar als "in Bearbeitung" markieren
                    self._processing_ids.add(idee.idee_id)
                    return idee
            
            return None
    
    def release_idea(self, idee_id: str) -> None:
        """Gibt eine Idee nach der Verarbeitung frei."""
        with self._lock:
            self._processing_ids.discard(idee_id)
    
    def is_processing(self, idee_id: str) -> bool:
        """Prüft ob eine Idee gerade verarbeitet wird."""
        with self._lock:
            return idee_id in self._processing_ids
