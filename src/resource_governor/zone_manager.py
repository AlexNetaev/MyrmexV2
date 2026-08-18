"""Zone Manager for MYRMEX v2.4.0 Resource Governor."""

from datetime import datetime, timezone, timedelta
from threading import Lock
from typing import Optional
import uuid

from pydantic import BaseModel, Field

from src.contracts.enums import SlotStatus


class ZoneState(BaseModel):
    """ZoneState: Der aktuelle Zustand einer Zone."""

    model_config = {"extra": "forbid"}

    zone_id: str = Field(..., min_length=1)
    status: str = "FREE"  # FREE, LOCKED, PATH_RESERVED, ESTOP_SUSPENDED, INTERLOCKED, MAINTENANCE
    current_holder_slot_id: str | None = None
    current_holder_lease_ref: str | None = None
    lock_policy: str | None = None  # EXCLUSIVE, SINGLE_OCCUPANT, PATH_RESERVATION, CONTAINER_LOCK
    lock_expires_at: str | None = None
    last_state_change_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    interlock_source: str | None = None


class ZoneLockResponse(BaseModel):
    """ZoneLockResponse: Antwort auf eine Zonen-Lock-Anfrage."""

    model_config = {"extra": "forbid"}

    zone_id: str = Field(..., min_length=1)
    status: str = "GRANTED"  # GRANTED, DENIED, TIMEOUT
    lock_id: str | None = None
    lock_expires_at: str | None = None
    error_code: str | None = None


class ZoneManager:
    """
    ZoneManager: Verwaltet Zonen-Zustände und Mutex-Locks.
    
    Regel 1: Zonen-Mutex verhindert Kollisionen in geteilten Räumen.
    Zwei Geräte dürfen nicht gleichzeitig in derselben physischen Zone agieren.
    """

    def __init__(self) -> None:
        self._zones: dict[str, ZoneState] = {}
        self._lock = Lock()

    def register_zone(
        self,
        zone_id: str,
        member_slots: list[str] | None = None,
        lock_policy: str = "EXCLUSIVE",
        max_hold_time_s: float = 300.0,
    ) -> bool:
        """Registriert eine neue Zone im FREE-Zustand."""
        with self._lock:
            if zone_id in self._zones:
                return False
            
            self._zones[zone_id] = ZoneState(
                zone_id=zone_id,
                status="FREE",
                lock_policy=lock_policy,
            )
            return True

    def get_zone_state(self, zone_id: str) -> str | None:
        """Gibt den aktuellen Zustand einer Zone zurück."""
        with self._lock:
            if zone_id not in self._zones:
                return None
            return self._zones[zone_id].status

    def get_zone(self, zone_id: str) -> ZoneState | None:
        """Gibt die Zone zurück oder None wenn nicht existiert."""
        with self._lock:
            return self._zones.get(zone_id)

    def request_zone_lock(
        self,
        zone_id: str,
        slot_id: str,
        lease_ref: str,
        lock_policy: str = "EXCLUSIVE",
        hold_time_s: float = 300.0,
    ) -> ZoneLockResponse:
        """
        Zonen-Lock-Anfrage.
        
        Bei Erfolg: Zone → LOCKED oder PATH_RESERVED
        Bei Konflikt: ZONE_LOCK_UNAVAILABLE (OPERATIONAL, kein ESTOP)
        """
        with self._lock:
            if zone_id not in self._zones:
                return ZoneLockResponse(
                    zone_id=zone_id,
                    status="DENIED",
                    error_code="ZONE_NOT_FOUND",
                )
            
            zone = self._zones[zone_id]
            
            # Prüfe ob Zone verfügbar ist
            if zone.status not in ("FREE",):
                # Zone belegt → DENIED (OPERATIONAL, kein ESTOP!)
                return ZoneLockResponse(
                    zone_id=zone_id,
                    status="DENIED",
                    error_code="ZONE_LOCK_UNAVAILABLE",
                )
            
            # Lock gewähren
            lock_id = f"zone_lock_{uuid.uuid4().hex[:12]}"
            now = datetime.now(timezone.utc)
            expires_at = (now + timedelta(seconds=hold_time_s)).isoformat()
            
            zone.status = "LOCKED" if lock_policy != "PATH_RESERVATION" else "PATH_RESERVED"
            zone.current_holder_slot_id = slot_id
            zone.current_holder_lease_ref = lease_ref
            zone.lock_policy = lock_policy
            zone.lock_expires_at = expires_at
            zone.last_state_change_at = now.isoformat()
            
            return ZoneLockResponse(
                zone_id=zone_id,
                status="GRANTED",
                lock_id=lock_id,
                lock_expires_at=expires_at,
            )

    def release_zone_lock(
        self,
        zone_id: str,
        slot_id: str,
        lease_ref: str,
    ) -> bool:
        """
        Zonen-Lock-Freigabe.
        
        Nur der aktuelle Inhaber kann freigeben.
        """
        with self._lock:
            if zone_id not in self._zones:
                return False
            
            zone = self._zones[zone_id]
            
            # Nur der aktuelle Inhaber kann freigeben
            if zone.current_holder_slot_id != slot_id or zone.current_holder_lease_ref != lease_ref:
                return False
            
            # Zone freigeben
            zone.status = "FREE"
            zone.current_holder_slot_id = None
            zone.current_holder_lease_ref = None
            zone.lock_policy = None
            zone.lock_expires_at = None
            zone.last_state_change_at = datetime.now(timezone.utc).isoformat()
            
            return True

    def suspend_zone_for_estop(self, zone_id: str) -> bool:
        """
        ESTOP-Behandlung: Setzt Zone auf ESTOP_SUSPENDED.
        """
        with self._lock:
            if zone_id not in self._zones:
                return False
            
            zone = self._zones[zone_id]
            
            # Nicht suspendieren wenn OFFLINE oder MAINTENANCE
            if zone.status in ("OFFLINE", "MAINTENANCE", "INTERLOCKED"):
                return False
            
            zone.status = "ESTOP_SUSPENDED"
            zone.last_state_change_at = datetime.now(timezone.utc).isoformat()
            
            return True

    def suspend_zone_for_interlock(self, zone_id: str, interlock_source: str) -> bool:
        """
        Hardware-Interlock-Behandlung: Setzt Zone auf INTERLOCKED.
        
        INTERLOCKED ist härter als ESTOP_SUSPENDED!
        Erfordert physischen Reset.
        """
        with self._lock:
            if zone_id not in self._zones:
                return False
            
            zone = self._zones[zone_id]
            
            # Nicht suspendieren wenn OFFLINE oder MAINTENANCE
            if zone.status in ("OFFLINE", "MAINTENANCE"):
                return False
            
            zone.status = "INTERLOCKED"
            zone.interlock_source = interlock_source
            zone.last_state_change_at = datetime.now(timezone.utc).isoformat()
            
            return True

    def reset_zone_after_estop(self, zone_id: str, authorized_by: str) -> bool:
        """Setzt Zone nach ESTOP zurück."""
        with self._lock:
            if zone_id not in self._zones:
                return False
            
            zone = self._zones[zone_id]
            
            if zone.status != "ESTOP_SUSPENDED":
                return False
            
            zone.status = "FREE"
            zone.current_holder_slot_id = None
            zone.current_holder_lease_ref = None
            zone.lock_policy = None
            zone.lock_expires_at = None
            zone.last_state_change_at = datetime.now(timezone.utc).isoformat()
            
            return True

    def reset_zone_after_interlock(self, zone_id: str, authorized_by: str, physical_reset: bool = True) -> bool:
        """
        Setzt Zone nach Hardware-Interlock zurück.
        
        Erfordert physischen Reset (physical_reset=True)!
        """
        with self._lock:
            if zone_id not in self._zones:
                return False
            
            zone = self._zones[zone_id]
            
            if zone.status != "INTERLOCKED":
                return False
            
            # Hardware-Interlock erfordert physischen Reset
            if not physical_reset:
                return False
            
            zone.status = "FREE"
            zone.interlock_source = None
            zone.current_holder_slot_id = None
            zone.current_holder_lease_ref = None
            zone.lock_policy = None
            zone.lock_expires_at = None
            zone.last_state_change_at = datetime.now(timezone.utc).isoformat()
            
            return True

    def set_zone_maintenance(self, zone_id: str, reason: str) -> bool:
        """Setzt Zone auf MAINTENANCE."""
        with self._lock:
            if zone_id not in self._zones:
                return False
            
            zone = self._zones[zone_id]
            zone.status = "MAINTENANCE"
            zone.last_state_change_at = datetime.now(timezone.utc).isoformat()
            
            return True

    def set_zone_offline(self, zone_id: str, reason: str) -> bool:
        """Setzt Zone auf OFFLINE."""
        with self._lock:
            if zone_id not in self._zones:
                return False
            
            zone = self._zones[zone_id]
            zone.status = "OFFLINE"
            zone.last_state_change_at = datetime.now(timezone.utc).isoformat()
            
            return True

    def check_expired_locks(self) -> list[str]:
        """Prüft auf abgelaufene Locks und gibt sie frei."""
        expired = []
        now = datetime.now(timezone.utc)
        
        with self._lock:
            for zone_id, zone in list(self._zones.items()):
                if zone.status in ("LOCKED", "PATH_RESERVED") and zone.lock_expires_at:
                    expires = datetime.fromisoformat(zone.lock_expires_at)
                    if now > expires:
                        # Lock abgelaufen → Zone freigeben
                        zone.status = "FREE"
                        zone.current_holder_slot_id = None
                        zone.current_holder_lease_ref = None
                        zone.lock_policy = None
                        zone.lock_expires_at = None
                        zone.last_state_change_at = now.isoformat()
                        expired.append(zone_id)
        
        return expired

    def list_zones(self) -> list[str]:
        """Listet alle registrierten Zone-IDs."""
        with self._lock:
            return list(self._zones.keys())

    def list_zones_by_state(self, state: str) -> list[str]:
        """Listet alle Zonen in einem bestimmten Zustand."""
        with self._lock:
            return [
                zone_id for zone_id, zone in self._zones.items()
                if zone.status == state
            ]
