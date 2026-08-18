"""Resource Governor for MYRMEX v2.4.0."""

from datetime import datetime, timezone, timedelta
from threading import Lock
from typing import Optional
import uuid

from src.contracts.enums import AbbruchKlasse, LeaseStatusName
from src.contracts.lease_models import (
    EstopEvent,
    LeaseDenied,
    LeaseGrant,
    LeaseStatus,
    ResourcePressureEvent,
)
from src.resource_governor.slot_manager import SlotManager, SlotStatus


class GovernorLease:
    """Interne Lease-Repräsentation für den Governor."""

    def __init__(
        self,
        lease_id: str,
        package_id: str,
        slot_id: str,
        ttl_s: float,
        heartbeat_interval_s: float,
    ) -> None:
        self.lease_id = lease_id
        self.package_id = package_id
        self.slot_id = slot_id
        self.ttl_s = ttl_s
        self.heartbeat_interval_s = heartbeat_interval_s
        self.status = LeaseStatusName.REQUESTED
        self.granted_at: str | None = None
        self.expires_at: str | None = None
        self.last_heartbeat_at: str | None = None
        self.created_at = datetime.now(timezone.utc)

    def to_status(self) -> LeaseStatus:
        """Konvertiert zu LeaseStatus für externe Nutzung."""
        now = datetime.now(timezone.utc)
        remaining_ttl = None
        if self.expires_at:
            expires = datetime.fromisoformat(self.expires_at)
            remaining = (expires - now).total_seconds()
            remaining_ttl = max(0.0, remaining)

        return LeaseStatus(
            lease_id=self.lease_id,
            slot_id=self.slot_id,
            package_id=self.package_id,
            status=self.status,
            granted_at=self.granted_at,
            expires_at=self.expires_at,
            remaining_ttl_s=remaining_ttl,
            is_active=self.status == LeaseStatusName.ACTIVE,
            is_expired=self.status == LeaseStatusName.EXPIRED,
            is_suspended=self.status == LeaseStatusName.ESTOP_SUSPENDED,
            suspension_reason="ESTOP" if self.status == LeaseStatusName.ESTOP_SUSPENDED else None,
            last_heartbeat_at=self.last_heartbeat_at,
        )


class ResourceGovernor:
    """
    ResourceGovernor: Verwaltet Leases und Ressourcen-Zuteilung.
    
    Regel 1: ESTOP ≠ LEASE_DENIED (KRITISCH — SICHERHEIT)
    - ESTOP = Physikalische Gefahr → SAFETY
    - LEASE_DENIED = Ressource belegt → OPERATIONAL
    """

    def __init__(self, slot_manager: SlotManager) -> None:
        self._slot_manager = slot_manager
        self._leases: dict[str, GovernorLease] = {}
        self._lock = Lock()
        self._lease_denied_counts: dict[str, list[float]] = {}  # slot_id -> timestamps

    def request_lease(
        self,
        package_id: str,
        slot_id: str,
        ttl_s: float,
        heartbeat_interval_s: float,
    ) -> LeaseGrant | LeaseDenied:
        """
        Lease-Anfrage.
        
        Prüft Slot-Verfügbarkeit via Slot-Manager.
        Bei Erfolg: GRANTED mit lease_id.
        Bei Konflikt: DENIED mit Grund (OPERATIONAL, kein ESTOP!).
        """
        with self._lock:
            # Prüfe Slot-Verfügbarkeit
            slot_state = self._slot_manager.get_slot_state(slot_id)
            
            if slot_state is None:
                # Slot existiert nicht
                return LeaseDenied(
                    package_id=package_id,
                    slot_id=slot_id,
                    reason="SLOT_NOT_FOUND",
                    retry_after_s=None,
                    abbruch_klasse=AbbruchKlasse.OPERATIONAL,
                )
            
            if slot_state != SlotStatus.FREE:
                # Slot belegt → LEASE_DENIED (OPERATIONAL, kein ESTOP!)
                # WICHTIG: Hier KEINEN ESTOP auslösen!
                self._record_lease_denied(slot_id)
                retry_after = self._estimate_wait_time(slot_id)
                return LeaseDenied(
                    package_id=package_id,
                    slot_id=slot_id,
                    reason=f"SLOT_BUSY ({slot_state.value})",
                    retry_after_s=retry_after,
                    abbruch_klasse=AbbruchKlasse.OPERATIONAL,
                )
            
            # Slot frei → Lease gewähren
            lease_id = f"lease_{uuid.uuid4().hex[:12]}"
            now = datetime.now(timezone.utc)
            expires_at = (now + timedelta(seconds=ttl_s)).isoformat()
            
            # Atomare Slot-Vergabe
            if not self._slot_manager.try_acquire_slot(slot_id, lease_id):
                # Race condition: Slot wurde zwischenzeitlich vergeben
                self._record_lease_denied(slot_id)
                return LeaseDenied(
                    package_id=package_id,
                    slot_id=slot_id,
                    reason="SLOT_BUSY (RACE_CONDITION)",
                    retry_after_s=1.0,
                    abbruch_klasse=AbbruchKlasse.OPERATIONAL,
                )
            
            # Lease erstellen
            lease = GovernorLease(
                lease_id=lease_id,
                package_id=package_id,
                slot_id=slot_id,
                ttl_s=ttl_s,
                heartbeat_interval_s=heartbeat_interval_s,
            )
            lease.status = LeaseStatusName.GRANTED
            lease.granted_at = now.isoformat()
            lease.expires_at = expires_at
            lease.last_heartbeat_at = now.isoformat()
            
            self._leases[lease_id] = lease
            
            # Slot auf ACTIVE setzen
            self._slot_manager.activate_slot(slot_id, lease_id)
            
            return LeaseGrant(
                lease_id=lease_id,
                slot_id=slot_id,
                package_id=package_id,
                granted_at=now.isoformat(),
                expires_at=expires_at,
                ttl_seconds=ttl_s,
                heartbeat_interval_s=heartbeat_interval_s,
            )

    def heartbeat(self, lease_id: str) -> bool:
        """
        Heartbeat: Aktualisiert last_heartbeat_at.
        
        Wenn now - last_heartbeat_at > heartbeat_interval_s * 2 → Lease EXPIRED.
        """
        with self._lock:
            if lease_id not in self._leases:
                return False
            
            lease = self._leases[lease_id]
            if lease.status not in (LeaseStatusName.GRANTED, LeaseStatusName.ACTIVE):
                return False
            
            now = datetime.now(timezone.utc)
            
            # Prüfe ob vorheriger Heartbeat noch im erlaubten Fenster war
            if lease.heartbeat_interval_s > 0 and lease.last_heartbeat_at is not None:
                max_interval = lease.heartbeat_interval_s * 2
                last_hb = datetime.fromisoformat(lease.last_heartbeat_at)
                if (now - last_hb).total_seconds() > max_interval:
                    # Heartbeat zu spät → Lease expired
                    self._expire_lease(lease_id)
                    return False
            
            # Heartbeat aktualisieren
            lease.last_heartbeat_at = now.isoformat()
            return True

    def check_expired_leases(self) -> list[str]:
        """
        Findet alle Leases mit abgelaufener TTL.
        
        Markiert sie als EXPIRED.
        """
        expired = []
        now = datetime.now(timezone.utc)
        
        with self._lock:
            for lease_id, lease in list(self._leases.items()):
                if lease.status not in (LeaseStatusName.GRANTED, LeaseStatusName.ACTIVE):
                    continue
                
                if lease.expires_at:
                    expires = datetime.fromisoformat(lease.expires_at)
                    if now > expires:
                        self._expire_lease(lease_id)
                        expired.append(lease_id)
        
        return expired

    def release_lease(self, lease_id: str) -> bool:
        """Gibt eine Lease frei."""
        with self._lock:
            if lease_id not in self._leases:
                return False
            
            lease = self._leases[lease_id]
            if lease.status not in (LeaseStatusName.GRANTED, LeaseStatusName.ACTIVE):
                return False
            
            # Slot freigeben
            if lease.slot_id:
                self._slot_manager.release_slot(lease.slot_id, lease_id)
            
            lease.status = LeaseStatusName.RELEASED
            return True

    def suspend_lease_for_estop(self, lease_id: str) -> bool:
        """Setzt Lease auf ESTOP_SUSPENDED."""
        with self._lock:
            if lease_id not in self._leases:
                return False
            
            lease = self._leases[lease_id]
            if lease.status not in (LeaseStatusName.GRANTED, LeaseStatusName.ACTIVE):
                return False
            
            lease.status = LeaseStatusName.ESTOP_SUSPENDED
            return True

    def get_lease_status(self, lease_id: str) -> LeaseStatus | None:
        """Gibt den Status einer Lease zurück."""
        with self._lock:
            if lease_id not in self._leases:
                return None
            return self._leases[lease_id].to_status()

    def get_affected_leases_for_slot(self, slot_id: str) -> list[str]:
        """Gibt alle Lease-IDs zurück, die einen Slot betreffen."""
        with self._lock:
            return [
                lease_id for lease_id, lease in self._leases.items()
                if lease.slot_id == slot_id and lease.status in (
                    LeaseStatusName.GRANTED,
                    LeaseStatusName.ACTIVE,
                    LeaseStatusName.ESTOP_SUSPENDED,
                )
            ]

    def _expire_lease(self, lease_id: str) -> None:
        """Markiert Lease als EXPIRED und gibt Slot frei."""
        lease = self._leases[lease_id]
        lease.status = LeaseStatusName.EXPIRED
        
        if lease.slot_id:
            self._slot_manager.release_slot(lease.slot_id, lease_id)

    def _record_lease_denied(self, slot_id: str) -> None:
        """Recorded LEASE_DENIED für Resource Pressure Detection."""
        now = datetime.now(timezone.utc).timestamp()
        if slot_id not in self._lease_denied_counts:
            self._lease_denied_counts[slot_id] = []
        self._lease_denied_counts[slot_id].append(now)
        
        # Alte Einträge bereinigen (älter als 60s)
        cutoff = now - 60.0
        self._lease_denied_counts[slot_id] = [
            ts for ts in self._lease_denied_counts[slot_id] if ts > cutoff
        ]

    def _estimate_wait_time(self, slot_id: str) -> float | None:
        """Schätzt Wartezeit basierend auf Lease-Dauer."""
        # Einfache Schätzung: 5 Sekunden Default
        return 5.0

    def check_resource_pressure(self, window_s: float = 60.0, threshold: int = 10) -> ResourcePressureEvent | None:
        """
        Prüft auf Resource Pressure.
        
        Regel 5: resource_pressure_event ist OPERATIONAL, nicht SCIENTIFIC.
        """
        now = datetime.now(timezone.utc).timestamp()
        cutoff = now - window_s
        
        with self._lock:
            for slot_id, timestamps in self._lease_denied_counts.items():
                recent_count = sum(1 for ts in timestamps if ts > cutoff)
                if recent_count >= threshold:
                    return ResourcePressureEvent(
                        slot_id=slot_id,
                        denied_count=recent_count,
                        window_s=window_s,
                        abbruch_klasse=AbbruchKlasse.OPERATIONAL,
                    )
        
        return None
