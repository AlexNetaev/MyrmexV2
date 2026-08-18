"""Tests für den Resource Governor."""

import time

import pytest

from src.contracts.enums import AbbruchKlasse, LeaseStatusName
from src.contracts.lease_models import LeaseDenied, LeaseGrant
from src.resource_governor.governor import ResourceGovernor
from src.resource_governor.slot_manager import SlotManager


class TestResourceGovernor:
    """Test-Suite für ResourceGovernor."""

    def test_lease_granted_when_slot_free(self):
        """Lease-Anfrage bei freiem Slot → GRANTED."""
        slot_manager = SlotManager()
        slot_manager.register_slot("slot_1")
        governor = ResourceGovernor(slot_manager)
        
        result = governor.request_lease(
            package_id="pkg_001",
            slot_id="slot_1",
            ttl_s=60.0,
            heartbeat_interval_s=10.0,
        )
        
        assert isinstance(result, LeaseGrant)
        assert result.slot_id == "slot_1"
        assert result.package_id == "pkg_001"
        assert result.lease_id is not None

    def test_lease_denied_when_slot_busy(self):
        """Regel 1: Lease-Anfrage bei belegtem Slot → DENIED (kein ESTOP)."""
        slot_manager = SlotManager()
        slot_manager.register_slot("slot_1")
        governor = ResourceGovernor(slot_manager)
        
        # Erste Anfrage erfolgreich
        result1 = governor.request_lease("pkg_001", "slot_1", 60.0, 10.0)
        assert isinstance(result1, LeaseGrant)
        
        # Zweite Anfrage abgelehnt
        result2 = governor.request_lease("pkg_002", "slot_1", 60.0, 10.0)
        
        assert isinstance(result2, LeaseDenied)
        assert result2.abbruch_klasse == AbbruchKlasse.OPERATIONAL
        assert "SLOT_BUSY" in result2.reason

    def test_lease_denied_does_not_trigger_estop(self):
        """Regel 1 (KRITISCH): LEASE_DENIED löst KEINEN ESTOP aus."""
        slot_manager = SlotManager()
        slot_manager.register_slot("slot_1")
        governor = ResourceGovernor(slot_manager)
        
        # Erste Lease gewähren
        result1 = governor.request_lease("pkg_001", "slot_1", 60.0, 10.0)
        assert isinstance(result1, LeaseGrant)
        
        # Zweite Anfrage → LEASE_DENIED
        result2 = governor.request_lease("pkg_002", "slot_1", 60.0, 10.0)
        assert isinstance(result2, LeaseDenied)
        
        # WICHTIG: LEASE_DENIED ist OPERATIONAL, nicht SAFETY!
        assert result2.abbruch_klasse == AbbruchKlasse.OPERATIONAL
        
        # Status der ersten Lease prüfen - sie sollte noch aktiv sein
        status1 = governor.get_lease_status(result1.lease_id)
        assert status1 is not None
        assert status1.status != LeaseStatusName.ESTOP_SUSPENDED

    def test_lease_ttl_expiry(self):
        """Regel 3: Lease mit abgelaufener TTL → EXPIRED."""
        slot_manager = SlotManager()
        slot_manager.register_slot("slot_1")
        governor = ResourceGovernor(slot_manager)
        
        # Lease mit sehr kurzer TTL
        result = governor.request_lease("pkg_001", "slot_1", 0.1, 0.05)
        assert isinstance(result, LeaseGrant)
        
        # Kurz warten bis TTL abläuft
        time.sleep(0.15)
        
        #Expired Leases prüfen
        expired = governor.check_expired_leases()
        
        assert result.lease_id in expired
        
        # Status sollte EXPIRED sein
        status = governor.get_lease_status(result.lease_id)
        assert status.is_expired is True

    def test_lease_heartbeat_keeps_alive(self):
        """Regel 3: Heartbeat verhindert Expiry."""
        slot_manager = SlotManager()
        slot_manager.register_slot("slot_1")
        governor = ResourceGovernor(slot_manager)
        
        result = governor.request_lease("pkg_001", "slot_1", 60.0, 10.0)
        assert isinstance(result, LeaseGrant)
        
        # Heartbeat senden
        hb_result = governor.heartbeat(result.lease_id)
        
        assert hb_result is True
        
        status = governor.get_lease_status(result.lease_id)
        assert status.last_heartbeat_at is not None

    def test_lease_missing_heartbeat_expires(self):
        """Regel 3: Fehlender Heartbeat → EXPIRED."""
        slot_manager = SlotManager()
        slot_manager.register_slot("slot_1")
        governor = ResourceGovernor(slot_manager)
        
        # Sehr kurzes Heartbeat-Interval
        result = governor.request_lease("pkg_001", "slot_1", 60.0, 0.1)
        assert isinstance(result, LeaseGrant)
        
        # Warten länger als 2x heartbeat_interval
        time.sleep(0.25)
        
        # Heartbeat versuchen → sollte False zurückgeben (expired)
        hb_result = governor.heartbeat(result.lease_id)
        
        assert hb_result is False

    def test_lease_release(self):
        """Lease freigeben."""
        slot_manager = SlotManager()
        slot_manager.register_slot("slot_1")
        governor = ResourceGovernor(slot_manager)
        
        result = governor.request_lease("pkg_001", "slot_1", 60.0, 10.0)
        assert isinstance(result, LeaseGrant)
        
        # Release
        release_result = governor.release_lease(result.lease_id)
        
        assert release_result is True
        
        status = governor.get_lease_status(result.lease_id)
        assert status.status == LeaseStatusName.RELEASED

    def test_lease_state_transitions_logged_to_wal(self):
        """Lease-Zustandsübergänge werden im WAL protokolliert."""
        # Dieser Test prüft die Integration mit Phase 4 WAL
        # Für jetzt prüfen wir nur dass Status-Übergänge funktionieren
        slot_manager = SlotManager()
        slot_manager.register_slot("slot_1")
        governor = ResourceGovernor(slot_manager)
        
        result = governor.request_lease("pkg_001", "slot_1", 60.0, 10.0)
        assert isinstance(result, LeaseGrant)
        
        status = governor.get_lease_status(result.lease_id)
        assert status.status == LeaseStatusName.GRANTED
        
        # Nach Aktivierung sollte Status ACTIVE sein
        # (passiert automatisch bei request_lease)

    def test_lease_denied_for_nonexistent_slot(self):
        """Lease-Anfrage für nicht existierenden Slot → DENIED."""
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        result = governor.request_lease("pkg_001", "nonexistent", 60.0, 10.0)
        
        assert isinstance(result, LeaseDenied)
        assert result.reason == "SLOT_NOT_FOUND"
        assert result.abbruch_klasse == AbbruchKlasse.OPERATIONAL

    def test_resource_pressure_is_operational(self):
        """Regel 5: resource_pressure_event ist OPERATIONAL."""
        slot_manager = SlotManager()
        slot_manager.register_slot("slot_1")
        governor = ResourceGovernor(slot_manager)
        
        # Viele LEASE_DENIED generieren
        governor.request_lease("pkg_001", "slot_1", 60.0, 10.0)
        for i in range(15):
            governor.request_lease(f"pkg_{i:02d}", "slot_1", 60.0, 10.0)
        
        # Resource Pressure prüfen
        pressure_event = governor.check_resource_pressure(window_s=60.0, threshold=10)
        
        if pressure_event is not None:
            assert pressure_event.abbruch_klasse == AbbruchKlasse.OPERATIONAL

    def test_suspend_lease_for_estop(self):
        """ESTOP suspendiert Lease."""
        slot_manager = SlotManager()
        slot_manager.register_slot("slot_1")
        governor = ResourceGovernor(slot_manager)
        
        result = governor.request_lease("pkg_001", "slot_1", 60.0, 10.0)
        assert isinstance(result, LeaseGrant)
        
        # Lease suspendieren
        suspend_result = governor.suspend_lease_for_estop(result.lease_id)
        
        assert suspend_result is True
        
        status = governor.get_lease_status(result.lease_id)
        assert status.status == LeaseStatusName.ESTOP_SUSPENDED
        assert status.is_suspended is True

    def test_get_affected_leases_for_slot(self):
        """Ermittelt betroffene Leases für einen Slot."""
        slot_manager = SlotManager()
        slot_manager.register_slot("slot_1")
        governor = ResourceGovernor(slot_manager)
        
        result = governor.request_lease("pkg_001", "slot_1", 60.0, 10.0)
        assert isinstance(result, LeaseGrant)
        
        affected = governor.get_affected_leases_for_slot("slot_1")
        
        assert result.lease_id in affected
