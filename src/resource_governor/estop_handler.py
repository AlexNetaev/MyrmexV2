"""ESTOP Handler for MYRMEX v2.4.0 Resource Governor."""

from datetime import datetime, timezone
from threading import Lock
import uuid

from src.contracts.enums import AbbruchKlasse, EstopSource, LeaseStatusName
from src.contracts.lease_models import EstopEvent
from src.resource_governor.slot_manager import SlotManager
from src.resource_governor.governor import ResourceGovernor


class EstopHandler:
    """
    EstopHandler: Verarbeitet ESTOP-Ereignisse.
    
    Regel 1 (KRITISCH): ESTOP ≠ LEASE_DENIED
    - ESTOP = SAFETY (physikalische Gefahr)
    - LEASE_DENIED = OPERATIONAL (Ressource belegt)
    """

    def __init__(
        self,
        slot_manager: SlotManager,
        governor: ResourceGovernor,
    ) -> None:
        self._slot_manager = slot_manager
        self._governor = governor
        self._estop_events: dict[str, EstopEvent] = {}
        self._current_estop_id: str | None = None
        self._lock = Lock()

    def trigger_estop(self, reason: str, source: EstopSource) -> EstopEvent:
        """
        Löst ESTOP aus.
        
        ESTOP ist SAFETY, nicht OPERATIONAL!
        - Alle betroffenen Leases → ESTOP_SUSPENDED
        - Alle betroffenen Slots → ESTOP_SUSPENDED
        """
        with self._lock:
            estop_id = f"estop_{uuid.uuid4().hex[:12]}"
            now = datetime.now(timezone.utc).isoformat()
            
            # Alle Slots ermitteln und suspendieren
            affected_slots = []
            all_slot_ids = self._slot_manager.list_slots()
            for slot_id in all_slot_ids:
                slot_state = self._slot_manager.get_slot_state(slot_id)
                if slot_state and slot_state not in (
                    slot_state.__class__.OFFLINE,
                    slot_state.__class__.MAINTENANCE,
                ):
                    if self._slot_manager.suspend_slot_for_estop(slot_id):
                        affected_slots.append(slot_id)
            
            # Alle aktiven Leases ermitteln und suspendieren
            affected_leases = []
            for slot_id in affected_slots:
                lease_ids = self._governor.get_affected_leases_for_slot(slot_id)
                for lease_id in lease_ids:
                    if self._governor.suspend_lease_for_estop(lease_id):
                        affected_leases.append(lease_id)
            
            # ESTOP-Event erstellen
            estop_event = EstopEvent(
                estop_id=estop_id,
                reason=reason,
                source=source,
                affected_leases=affected_leases,
                affected_slots=affected_slots,
                timestamp=now,
                abbruch_klasse=AbbruchKlasse.SAFETY,  # WICHTIG: SAFETY, nicht OPERATIONAL!
            )
            
            self._estop_events[estop_id] = estop_event
            self._current_estop_id = estop_id
            
            return estop_event

    def reset_estop(self, estop_id: str, authorized_by: str) -> bool:
        """
        Setzt ESTOP zurück.
        
        Nur mit expliziter Autorisierung!
        Nach Reset: Prüfe ob wartende Pakete fortgesetzt werden können.
        """
        with self._lock:
            if estop_id not in self._estop_events:
                return False
            
            estop_event = self._estop_events[estop_id]
            if estop_event.reset_at is not None:
                # Bereits zurückgesetzt
                return False
            
            # Reset durchführen
            estop_event.reset_authorized_by = authorized_by
            estop_event.reset_at = datetime.now(timezone.utc).isoformat()
            
            # Alle betroffenen Slots zurücksetzen
            for slot_id in estop_event.affected_slots:
                self._slot_manager.reset_slot_after_estop(slot_id, authorized_by)
            
            # Aktuelle ESTOP-ID löschen
            if self._current_estop_id == estop_id:
                self._current_estop_id = None
            
            return True

    def get_current_estop(self) -> EstopEvent | None:
        """Gibt den aktuellen ESTOP zurück oder None."""
        with self._lock:
            if self._current_estop_id is None:
                return None
            return self._estop_events.get(self._current_estop_id)

    def get_estop_event(self, estop_id: str) -> EstopEvent | None:
        """Gibt ein spezifisches ESTOP-Event zurück."""
        with self._lock:
            return self._estop_events.get(estop_id)

    def check_gefahren_mitigationen(
        self,
        package_gefahren_mitigationen: list[str],
        estop_reason: str,
    ) -> bool:
        """
        Prüft ob gefahren_mitigationen den ESTOP-Grund abdecken.
        
        Nach ESTOP-Reset: Können wartende Pakete fortgesetzt werden?
        - Ja → Paket kann fortgesetzt werden
        - Nein → Paket wird sicher abgebrochen
        """
        # Einfache Heuristik: Wenn mitigationen leer sind, decken sie nichts ab
        if not package_gefahren_mitigationen:
            return False
        
        # Prüfe ob ESTOP-Reason in Mitigationen abgedeckt ist
        estop_reason_lower = estop_reason.lower()
        for mitigation in package_gefahren_mitigationen:
            mitigation_lower = mitigation.lower()
            if estop_reason_lower in mitigation_lower or mitigation_lower in estop_reason_lower:
                return True
        
        # Conservative: Wenn keine Übereinstimmung, dann nicht abgedeckt
        return False

    def is_estop_active(self) -> bool:
        """Prüft ob aktuell ein ESTOP aktiv ist."""
        with self._lock:
            return self._current_estop_id is not None

    def list_estop_events(self) -> list[str]:
        """Listet alle ESTOP-Event-IDs."""
        with self._lock:
            return list(self._estop_events.keys())
