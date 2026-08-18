"""Tests for Zone Manager."""

import pytest
from datetime import datetime, timezone, timedelta

from src.resource_governor.zone_manager import ZoneManager, ZoneState


class TestZoneLock:
    """Tests für Zonen-Lock-Funktionalität."""

    def test_zone_lock_when_free(self):
        """Zone FREE → Lock erfolgreich."""
        manager = ZoneManager()
        manager.register_zone("zone_1")
        
        response = manager.request_zone_lock(
            zone_id="zone_1",
            slot_id="slot_1",
            lease_ref="lease_123",
            lock_policy="EXCLUSIVE",
            hold_time_s=60.0,
        )
        
        assert response.status == "GRANTED"
        assert response.lock_id is not None
        assert response.lock_expires_at is not None
        assert manager.get_zone_state("zone_1") == "LOCKED"

    def test_zone_lock_when_locked_fails(self):
        """Zone LOCKED → Lock schlägt fehl."""
        manager = ZoneManager()
        manager.register_zone("zone_1")
        
        # Erster Lock erfolgreich
        response1 = manager.request_zone_lock(
            zone_id="zone_1",
            slot_id="slot_1",
            lease_ref="lease_123",
        )
        assert response1.status == "GRANTED"
        
        # Zweiter Lock muss fehlschlagen
        response2 = manager.request_zone_lock(
            zone_id="zone_1",
            slot_id="slot_2",
            lease_ref="lease_456",
        )
        assert response2.status == "DENIED"
        assert response2.error_code == "ZONE_LOCK_UNAVAILABLE"

    def test_zone_mutex_prevents_concurrent_access(self):
        """Regel 1: Zwei Geräte können nicht gleichzeitig in derselben Zone agieren."""
        manager = ZoneManager()
        manager.register_zone("zone_1")
        
        # Gerät 1 lockt Zone
        response1 = manager.request_zone_lock(
            zone_id="zone_1",
            slot_id="slot_1",
            lease_ref="lease_1",
        )
        assert response1.status == "GRANTED"
        
        # Gerät 2 versucht gleichen Zugriff → muss abgelehnt werden
        response2 = manager.request_zone_lock(
            zone_id="zone_1",
            slot_id="slot_2",
            lease_ref="lease_2",
        )
        assert response2.status == "DENIED"
        
        # Zone ist immer noch von Gerät 1 gehalten
        zone = manager.get_zone("zone_1")
        assert zone.current_holder_slot_id == "slot_1"
        assert zone.current_holder_lease_ref == "lease_1"

    def test_zone_lock_release_by_owner_only(self):
        """Nur der aktuelle Inhaber kann freigeben."""
        manager = ZoneManager()
        manager.register_zone("zone_1")
        
        # Zone locken
        manager.request_zone_lock(
            zone_id="zone_1",
            slot_id="slot_1",
            lease_ref="lease_123",
        )
        
        # Falscher Owner versucht Freigabe → muss fehlschlagen
        released_wrong = manager.release_zone_lock(
            zone_id="zone_1",
            slot_id="slot_2",  # Falscher Slot
            lease_ref="lease_123",
        )
        assert released_wrong is False
        
        # Richtiger Owner gibt frei → muss erfolgreich sein
        released_correct = manager.release_zone_lock(
            zone_id="zone_1",
            slot_id="slot_1",
            lease_ref="lease_123",
        )
        assert released_correct is True
        assert manager.get_zone_state("zone_1") == "FREE"


class TestZoneEstop:
    """Tests für ESTOP-Behandlung in Zonen."""

    def test_zone_estop_sets_estop_suspended(self):
        """ESTOP setzt Zone auf ESTOP_SUSPENDED."""
        manager = ZoneManager()
        manager.register_zone("zone_1")
        
        # Zone locken
        manager.request_zone_lock(
            zone_id="zone_1",
            slot_id="slot_1",
            lease_ref="lease_123",
        )
        assert manager.get_zone_state("zone_1") == "LOCKED"
        
        # ESTOP auslösen
        suspended = manager.suspend_zone_for_estop("zone_1")
        assert suspended is True
        assert manager.get_zone_state("zone_1") == "ESTOP_SUSPENDED"

    def test_zone_interlock_sets_interlocked(self):
        """Regel 4: Hardware-Interlock setzt Zone auf INTERLOCKED (härter als ESTOP_SUSPENDED)."""
        manager = ZoneManager()
        manager.register_zone("zone_1")
        
        # Zone locken
        manager.request_zone_lock(
            zone_id="zone_1",
            slot_id="slot_1",
            lease_ref="lease_123",
        )
        assert manager.get_zone_state("zone_1") == "LOCKED"
        
        # Hardware-Interlock auslösen
        interlocked = manager.suspend_zone_for_interlock(
            zone_id="zone_1",
            interlock_source="PRESSURE_SENSOR",
        )
        assert interlocked is True
        assert manager.get_zone_state("zone_1") == "INTERLOCKED"
        
        # Interlock-Source muss gespeichert sein
        zone = manager.get_zone("zone_1")
        assert zone.interlock_source == "PRESSURE_SENSOR"

    def test_zone_lock_unavailable_is_operational(self):
        """Regel 1: ZONE_LOCK_UNAVAILABLE ist OPERATIONAL, nicht SAFETY."""
        manager = ZoneManager()
        manager.register_zone("zone_1")
        
        # Zone locken
        manager.request_zone_lock(
            zone_id="zone_1",
            slot_id="slot_1",
            lease_ref="lease_123",
        )
        
        # Zweiter Lock-Versuch → DENIED mit ZONE_LOCK_UNAVAILABLE
        response = manager.request_zone_lock(
            zone_id="zone_1",
            slot_id="slot_2",
            lease_ref="lease_456",
        )
        
        assert response.status == "DENIED"
        assert response.error_code == "ZONE_LOCK_UNAVAILABLE"
        # Wichtig: Dies ist ein OPERATIONAL-Fehler, kein SAFETY-Fehler!
        # (Die Klassifikation erfolgt im Governor/ESTOP-Handler)


class TestZoneReset:
    """Tests für Zone-Reset nach ESTOP/Interlock."""

    def test_zone_estop_reset_requires_authorization(self):
        """ESTOP-Reset erfordert Autorisierung."""
        manager = ZoneManager()
        manager.register_zone("zone_1")
        
        # Zone locken und ESTOP auslösen
        manager.request_zone_lock(zone_id="zone_1", slot_id="slot_1", lease_ref="lease_123")
        manager.suspend_zone_for_estop("zone_1")
        assert manager.get_zone_state("zone_1") == "ESTOP_SUSPENDED"
        
        # Reset mit Autorisierung
        reset = manager.reset_zone_after_estop("zone_1", authorized_by="operator_1")
        assert reset is True
        assert manager.get_zone_state("zone_1") == "FREE"

    def test_zone_interlock_requires_physical_reset(self):
        """Regel 4: Hardware-Interlock erfordert physischen Reset."""
        manager = ZoneManager()
        manager.register_zone("zone_1")
        
        # Zone locken und Interlock auslösen
        manager.request_zone_lock(zone_id="zone_1", slot_id="slot_1", lease_ref="lease_123")
        manager.suspend_zone_for_interlock("zone_1", "PRESSURE_SENSOR")
        assert manager.get_zone_state("zone_1") == "INTERLOCKED"
        
        # Reset OHNE physischen Reset → muss fehlschlagen
        reset_no_physical = manager.reset_zone_after_interlock(
            "zone_1",
            authorized_by="operator_1",
            physical_reset=False,
        )
        assert reset_no_physical is False
        assert manager.get_zone_state("zone_1") == "INTERLOCKED"
        
        # Reset MIT physischem Reset → muss erfolgreich sein
        reset_physical = manager.reset_zone_after_interlock(
            "zone_1",
            authorized_by="operator_1",
            physical_reset=True,
        )
        assert reset_physical is True
        assert manager.get_zone_state("zone_1") == "FREE"


class TestZoneExpiry:
    """Tests für Lock-Expiry."""

    def test_expired_lock_is_released(self):
        """Abgelaufene Locks werden freigegeben."""
        manager = ZoneManager()
        manager.register_zone("zone_1")
        
        # Zone mit sehr kurzer Hold-Time locken
        manager.request_zone_lock(
            zone_id="zone_1",
            slot_id="slot_1",
            lease_ref="lease_123",
            hold_time_s=0.1,  # 100ms
        )
        assert manager.get_zone_state("zone_1") == "LOCKED"
        
        # Warten bis Lock abläuft
        import time
        time.sleep(0.2)
        
        # Expiry prüfen
        expired = manager.check_expired_locks()
        assert "zone_1" in expired
        assert manager.get_zone_state("zone_1") == "FREE"
