"""Slot Manager for MYRMEX v2.4.0 Resource Governor."""

from datetime import datetime, timezone
from threading import Lock
from typing import Optional

from pydantic import BaseModel, Field

from src.contracts.enums import SlotStatus


class Slot(BaseModel):
    """Slot: Ein physischer oder logischer Ressourcen-Slot."""

    model_config = {"extra": "forbid"}

    slot_id: str = Field(..., min_length=1)
    state: SlotStatus = SlotStatus.FREE
    current_lease_id: str | None = None
    last_state_change_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    estop_suspended_at: str | None = None
    maintenance_reason: str | None = None
    offline_reason: str | None = None


class SlotManager:
    """
    SlotManager: Verwaltet Slot-Zustände und atomare Lease-Vergabe.
    
    Regel 2: Slot-Mutex ist atomar (Compare-and-Set).
    Zwei Pakete können nicht denselben Slot gleichzeitig belegen.
    """

    def __init__(self) -> None:
        self._slots: dict[str, Slot] = {}
        self._lock = Lock()

    def register_slot(self, slot_id: str) -> bool:
        """Registriert einen neuen Slot im FREE-Zustand."""
        with self._lock:
            if slot_id in self._slots:
                return False
            self._slots[slot_id] = Slot(slot_id=slot_id, state=SlotStatus.FREE)
            return True

    def get_slot_state(self, slot_id: str) -> SlotStatus | None:
        """Gibt den aktuellen Zustand eines Slots zurück."""
        with self._lock:
            if slot_id not in self._slots:
                return None
            return self._slots[slot_id].state

    def get_slot(self, slot_id: str) -> Slot | None:
        """Gibt den Slot zurück oder None wenn nicht existiert."""
        with self._lock:
            return self._slots.get(slot_id)

    def try_acquire_slot(self, slot_id: str, lease_id: str) -> bool:
        """
        Atomare Lease-Vergabe (Compare-and-Set).
        
        Nur erfolgreich, wenn Slot aktuell FREE ist.
        Zwei gleichzeitige Anfragen → nur eine erfolgreich.
        """
        with self._lock:
            if slot_id not in self._slots:
                return False
            
            slot = self._slots[slot_id]
            if slot.state != SlotStatus.FREE:
                return False
            
            # Atomar: Prüfe und setze in einer Operation
            slot.state = SlotStatus.RESERVED
            slot.current_lease_id = lease_id
            slot.last_state_change_at = datetime.now(timezone.utc).isoformat()
            return True

    def release_slot(self, slot_id: str, lease_id: str) -> bool:
        """
        Slot-Freigabe.
        
        Nur der aktuelle Mieter kann freigeben.
        """
        with self._lock:
            if slot_id not in self._slots:
                return False
            
            slot = self._slots[slot_id]
            if slot.current_lease_id != lease_id:
                return False
            
            slot.state = SlotStatus.FREE
            slot.current_lease_id = None
            slot.last_state_change_at = datetime.now(timezone.utc).isoformat()
            return True

    def activate_slot(self, slot_id: str, lease_id: str) -> bool:
        """Setzt Slot von RESERVED auf ACTIVE."""
        with self._lock:
            if slot_id not in self._slots:
                return False
            
            slot = self._slots[slot_id]
            if slot.current_lease_id != lease_id or slot.state != SlotStatus.RESERVED:
                return False
            
            slot.state = SlotStatus.ACTIVE
            slot.last_state_change_at = datetime.now(timezone.utc).isoformat()
            return True

    def suspend_slot_for_estop(self, slot_id: str) -> bool:
        """
        ESTOP-Behandlung: Setzt Slot auf ESTOP_SUSPENDED.
        
        Regel 4: ESTOP suspendiert betroffene Slots.
        """
        with self._lock:
            if slot_id not in self._slots:
                return False
            
            slot = self._slots[slot_id]
            if slot.state == SlotStatus.OFFLINE or slot.state == SlotStatus.MAINTENANCE:
                return False
            
            previous_state = slot.state
            slot.state = SlotStatus.ESTOP_SUSPENDED
            slot.estop_suspended_at = datetime.now(timezone.utc).isoformat()
            slot.last_state_change_at = datetime.now(timezone.utc).isoformat()
            return True

    def reset_slot_after_estop(self, slot_id: str, authorized_by: str) -> bool:
        """
        ESTOP-Reset: Setzt Slot zurück nach ESTOP.
        
        Nur mit expliziter Autorisierung.
        """
        with self._lock:
            if slot_id not in self._slots:
                return False
            
            slot = self._slots[slot_id]
            if slot.state != SlotStatus.ESTOP_SUSPENDED:
                return False
            
            # Nach Reset: Slot geht auf FREE (kann neu vergeben werden)
            slot.state = SlotStatus.FREE
            slot.current_lease_id = None
            slot.estop_suspended_at = None
            slot.last_state_change_at = datetime.now(timezone.utc).isoformat()
            return True

    def set_slot_maintenance(self, slot_id: str, reason: str) -> bool:
        """Setzt Slot auf MAINTENANCE."""
        with self._lock:
            if slot_id not in self._slots:
                return False
            
            slot = self._slots[slot_id]
            slot.state = SlotStatus.MAINTENANCE
            slot.maintenance_reason = reason
            slot.last_state_change_at = datetime.now(timezone.utc).isoformat()
            return True

    def set_slot_offline(self, slot_id: str, reason: str) -> bool:
        """Setzt Slot auf OFFLINE."""
        with self._lock:
            if slot_id not in self._slots:
                return False
            
            slot = self._slots[slot_id]
            slot.state = SlotStatus.OFFLINE
            slot.offline_reason = reason
            slot.last_state_change_at = datetime.now(timezone.utc).isoformat()
            return True

    def list_slots(self) -> list[str]:
        """Listet alle registrierten Slot-IDs."""
        with self._lock:
            return list(self._slots.keys())

    def list_slots_by_state(self, state: SlotStatus) -> list[str]:
        """Listet alle Slots in einem bestimmten Zustand."""
        with self._lock:
            return [
                slot_id for slot_id, slot in self._slots.items()
                if slot.state == state
            ]
