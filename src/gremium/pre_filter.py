"""Pre-Filter (Stufe 5a) - Deterministische Ideen-Prüfung für MYRMEX v2.4.0."""

import uuid
from datetime import datetime, timezone
from typing import Any

from src.contracts.pipeline_models import (
    RohIdee,
    FilterResult,
    FilterDecision,
    FilterEvent,
    DimensionOnboardingRequest,
    OnboardingStatus,
)
from src.contracts.enums import ZoneHealth


class SignalStack:
    """Repräsentiert den Signal-Stack an einer Koordinate."""
    
    def __init__(self, signals: list[tuple[str, str]] | None = None):
        # signals: list of (signal_type, severity) tuples
        self.signals = signals or []
    
    def has_red_signal(self) -> bool:
        """Prüft ob ein rotes Signal vorhanden ist."""
        for signal_type, severity in self.signals:
            if severity == "RED":
                return True
        return False
    
    def has_yellow_fracture(self) -> bool:
        """Prüft ob ein gelbes Fraktur-Signal vorhanden ist."""
        for signal_type, severity in self.signals:
            if severity == "YELLOW" and signal_type == "FRACTURE":
                return True
        return False
    
    def to_dict(self) -> dict[str, str]:
        """Konvertiert zu Dictionary für snapshot."""
        result = {}
        for i, (signal_type, severity) in enumerate(self.signals):
            result[f"signal_{i}_type"] = signal_type
            result[f"signal_{i}_severity"] = severity
        return result


class DimensionSchema:
    """Schema für bekannte Dimensionen."""
    
    def __init__(self, known_dimensions: set[str] | None = None):
        self.known_dimensions = known_dimensions or {"x", "y", "z"}
    
    def has_dimension(self, dim: str) -> bool:
        """Prüft ob eine Dimension bekannt ist."""
        return dim in self.known_dimensions
    
    def add_dimension(self, dim: str) -> None:
        """Fügt eine Dimension hinzu."""
        self.known_dimensions.add(dim)


class ZoneInfo:
    """Informationen über eine Zone."""
    
    def __init__(
        self,
        zone_id: str,
        zone_health: ZoneHealth = ZoneHealth.STABIL,
        centroid: dict[str, float] | None = None,
    ):
        self.zone_id = zone_id
        self.zone_health = zone_health
        self.centroid = centroid or {}


class PreFilterConfig:
    """Konfiguration für den Pre-Filter."""
    
    def __init__(self):
        pass


class PreFilter:
    """
    Pre-Filter (Stufe 5a) - Deterministische Prüfung von Forschungsideen.
    
    Regel 2: UNKNOWN-Dimensionen als DIMENSION_GAP, nicht hart verwerfen
    Regel 3: Pre-Filter ist deterministisch (kein LLM)
    Regel 5: Jede Entscheidung wird protokolliert
    """
    
    def __init__(
        self,
        dimension_schema: DimensionSchema | None = None,
        config: PreFilterConfig | None = None,
    ):
        self.dimension_schema = dimension_schema or DimensionSchema()
        self.config = config or PreFilterConfig()
        self.filter_events: list[FilterEvent] = []
        self.dimension_onboarding_requests: list[DimensionOnboardingRequest] = []
    
    def filter_idea(
        self,
        idee: RohIdee,
        signal_registry: Any | None = None,
    ) -> FilterResult:
        """
        Prüft eine Idee und gibt FilterResult zurück.
        
        Prüfregeln:
        - 🟥-Signal an Zielkoordinate → VERWERFEN (RED_SIGNAL)
        - Physikalische Unmöglichkeit → VERWERFEN (PHYSICAL_IMPOSSIBLE)
        - Unbekannte Dimension → DIMENSION_GAP (NICHT hart verwerfen!)
        - 🟨-Fraktur + intent=FRACTURE_DIAGNOSIS → ERLAUBEN (FRACTURE_DIAGNOSIS)
        - ⬜ Sättigung an Zielkoordinate → VERWERFEN (SATURATED)
        - Sonst → ERLAUBEN
        """
        # Regel 2 (KRITISCH): UNKNOWN-Dimensionen sind DIMENSION_GAP, nicht VERWERFEN
        for dim in idee.ziel_koordinate.keys():
            if not self.dimension_schema.has_dimension(dim):
                # NICHT: return FilterResult(decision="VERWERFEN", ...)
                # SONDERN:
                onboarding_request = self._create_dimension_onboarding_request(
                    dim, idee.idee_id
                )
                filter_event = self._create_filter_event(
                    idee,
                    FilterDecision.DIMENSION_GAP,
                    f"Dimension '{dim}' ist unbekannt",
                    {},
                )
                return FilterResult(
                    decision=FilterDecision.DIMENSION_GAP,
                    reason=f"Dimension '{dim}' ist unbekannt",
                    filter_event=filter_event,
                )
        
        # Signal-Stack prüfen
        signal_stack = self._get_signal_stack(idee.ziel_koordinate, signal_registry)
        
        # 🟥-Signal prüfen
        if signal_stack.has_red_signal():
            filter_event = self._create_filter_event(
                idee,
                FilterDecision.VERWERFEN,
                "RED_SIGNAL",
                signal_stack.to_dict(),
            )
            return FilterResult(
                decision=FilterDecision.VERWERFEN,
                reason="RED_SIGNAL",
                filter_event=filter_event,
            )
        
        # FRACTURE_DIAGNOSIS in QUARANTÄNE prüfen
        zone = self._get_zone_for_coordinate(idee.ziel_koordinate)
        if zone.zone_health == ZoneHealth.QUARANTAENE:
            if idee.intent.value == "FRACTURE_DIAGNOSIS":
                filter_event = self._create_filter_event(
                    idee,
                    FilterDecision.ERLAUBEN,
                    "FRACTURE_DIAGNOSIS",
                    signal_stack.to_dict(),
                )
                return FilterResult(
                    decision=FilterDecision.ERLAUBEN,
                    reason="FRACTURE_DIAGNOSIS",
                    filter_event=filter_event,
                )
            else:
                filter_event = self._create_filter_event(
                    idee,
                    FilterDecision.VERWERFEN,
                    "QUARANTINE_NON_DIAGNOSTIC",
                    signal_stack.to_dict(),
                )
                return FilterResult(
                    decision=FilterDecision.VERWERFEN,
                    reason="QUARANTINE_NON_DIAGNOSTIC",
                    filter_event=filter_event,
                )
        
        # Physikalische Unmöglichkeit prüfen
        if self._is_physical_impossible(idee):
            filter_event = self._create_filter_event(
                idee,
                FilterDecision.VERWERFEN,
                "PHYSICAL_IMPOSSIBLE",
                signal_stack.to_dict(),
            )
            return FilterResult(
                decision=FilterDecision.VERWERFEN,
                reason="PHYSICAL_IMPOSSIBLE",
                filter_event=filter_event,
            )
        
        # Sättigung prüfen
        if self._is_saturated(idee.ziel_koordinate):
            filter_event = self._create_filter_event(
                idee,
                FilterDecision.VERWERFEN,
                "SATURATED",
                signal_stack.to_dict(),
            )
            return FilterResult(
                decision=FilterDecision.VERWERFEN,
                reason="SATURATED",
                filter_event=filter_event,
            )
        
        # Standard: ERLAUBEN
        filter_event = self._create_filter_event(
            idee,
            FilterDecision.ERLAUBEN,
            "NORMAL",
            signal_stack.to_dict(),
        )
        return FilterResult(
            decision=FilterDecision.ERLAUBEN,
            reason="NORMAL",
            filter_event=filter_event,
        )
    
    def _create_filter_event(
        self,
        idee: RohIdee,
        decision: FilterDecision,
        reason: str,
        signal_snapshot: dict[str, str],
    ) -> FilterEvent:
        """Erstellt ein FilterEvent für die Protokollierung."""
        event = FilterEvent(
            event_id=str(uuid.uuid4()),
            idee_id=idee.idee_id,
            decision=decision,
            reason=reason,
            timestamp=datetime.now(timezone.utc).isoformat(),
            signal_snapshot=signal_snapshot,
        )
        self.filter_events.append(event)
        return event
    
    def _create_dimension_onboarding_request(
        self,
        dimension: str,
        idee_id: str,
    ) -> DimensionOnboardingRequest:
        """Erstellt einen DimensionOnboardingRequest."""
        request = DimensionOnboardingRequest(
            onboarding_request_id=str(uuid.uuid4()),
            dimension=dimension,
            package_id=idee_id,  # Wird später durch echte package_id ersetzt
            reason=f"Unbekannte Dimension '{dimension}' in Idee {idee_id}",
            status=OnboardingStatus.PENDING,
        )
        self.dimension_onboarding_requests.append(request)
        return request
    
    def _get_signal_stack(
        self,
        koordinate: dict[str, float],
        signal_registry: Any | None = None,
    ) -> SignalStack:
        """Holt den Signal-Stack für eine Koordinate."""
        if signal_registry is None:
            return SignalStack([])
        
        # Signal Registry API aufrufen (Mock für Tests)
        if hasattr(signal_registry, "get_signal_stack"):
            signals = signal_registry.get_signal_stack(koordinate)
            if isinstance(signals, SignalStack):
                return signals
            return SignalStack(signals)
        
        return SignalStack([])
    
    def _get_zone_for_coordinate(
        self,
        koordinate: dict[str, float],
    ) -> ZoneInfo:
        """Holt Zone-Informationen für eine Koordinate."""
        # Mock-Implementierung - wird durch echte Atlas-Integration ersetzt
        return ZoneInfo(zone_id="default_zone", zone_health=ZoneHealth.STABIL)
    
    def _is_physical_impossible(self, idee: RohIdee) -> bool:
        """Prüft physikalische Unmöglichkeit."""
        # Mock-Implementierung - kann erweitert werden
        # Beispiel: Koordinaten außerhalb des physikalisch Möglichen
        for coord_value in idee.ziel_koordinate.values():
            if abs(coord_value) > 1e10:  # Unrealistisch große Werte
                return True
        return False
    
    def _is_saturated(self, koordinate: dict[str, float]) -> bool:
        """Prüft Sättigung an einer Koordinate."""
        # Mock-Implementierung - wird durch echte Atlas-Daten ersetzt
        return False
    
    def get_filter_events(self) -> list[FilterEvent]:
        """Gibt alle protokollierten FilterEvents zurück."""
        return self.filter_events
    
    def get_dimension_onboarding_requests(self) -> list[DimensionOnboardingRequest]:
        """Gibt alle DimensionOnboardingRequests zurück."""
        return self.dimension_onboarding_requests
    
    def clear_events(self) -> None:
        """Löscht alle protokollierten Events."""
        self.filter_events.clear()
        self.dimension_onboarding_requests.clear()
