"""Tests für den Slot Manager."""

import threading
import time

import pytest

from src.contracts.enums import SlotStatus
from src.resource_governor.slot_manager import Slot, SlotManager


class TestSlotManager:
    """Test-Suite für SlotManager."""

    def test_slot_acquire_when_free(self):
        """Slot FREE → acquire erfolgreich."""
        manager = SlotManager()
        manager.register_slot("slot_1")
        
        result = manager.try_acquire_slot("slot_1", "lease_123")
        
        assert result is True
        assert manager.get_slot_state("slot_1") == SlotStatus.RESERVED

    def test_slot_acquire_when_busy_fails(self):
        """Slot ACTIVE → acquire schlägt fehl."""
        manager = SlotManager()
        manager.register_slot("slot_1")
        manager.try_acquire_slot("slot_1", "lease_123")
        manager.activate_slot("slot_1", "lease_123")
        
        result = manager.try_acquire_slot("slot_1", "lease_456")
        
        assert result is False
        assert manager.get_slot_state("slot_1") == SlotStatus.ACTIVE

    def test_slot_mutex_is_atomic(self):
        """Regel 2: Zwei gleichzeitige acquire → nur eine erfolgreich."""
        manager = SlotManager()
        manager.register_slot("slot_1")
        
        results = []
        
        def acquire_with_lease(lease_id: str):
            result = manager.try_acquire_slot("slot_1", lease_id)
            results.append((lease_id, result))
        
        threads = [
            threading.Thread(target=acquire_with_lease, args=("lease_A",)),
            threading.Thread(target=acquire_with_lease, args=("lease_B",)),
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Nur eine sollte erfolgreich sein
        success_count = sum(1 for _, r in results if r)
        assert success_count == 1
        
        # Der andere sollte fehlschlagen
        fail_count = sum(1 for _, r in results if not r)
        assert fail_count == 1

    def test_slot_release_by_owner(self):
        """Nur der aktuelle Mieter kann freigeben."""
        manager = SlotManager()
        manager.register_slot("slot_1")
        manager.try_acquire_slot("slot_1", "lease_123")
        
        result = manager.release_slot("slot_1", "lease_123")
        
        assert result is True
        assert manager.get_slot_state("slot_1") == SlotStatus.FREE

    def test_slot_release_by_non_owner_fails(self):
        """Ein anderer kann nicht freigeben."""
        manager = SlotManager()
        manager.register_slot("slot_1")
        manager.try_acquire_slot("slot_1", "lease_123")
        
        result = manager.release_slot("slot_1", "lease_456")
        
        assert result is False
        assert manager.get_slot_state("slot_1") == SlotStatus.RESERVED

    def test_slot_estop_suspend(self):
        """Regel 4: ESTOP setzt Slot auf ESTOP_SUSPENDED."""
        manager = SlotManager()
        manager.register_slot("slot_1")
        manager.try_acquire_slot("slot_1", "lease_123")
        manager.activate_slot("slot_1", "lease_123")
        
        result = manager.suspend_slot_for_estop("slot_1")
        
        assert result is True
        assert manager.get_slot_state("slot_1") == SlotStatus.ESTOP_SUSPENDED

    def test_slot_estop_reset_requires_authorization(self):
        """ESTOP-Reset nur mit Autorisierung."""
        manager = SlotManager()
        manager.register_slot("slot_1")
        manager.try_acquire_slot("slot_1", "lease_123")
        manager.suspend_slot_for_estop("slot_1")
        
        result = manager.reset_slot_after_estop("slot_1", "authorized_by_human")
        
        assert result is True
        assert manager.get_slot_state("slot_1") == SlotStatus.FREE

    def test_slot_not_found_returns_none(self):
        """Nicht existierender Slot gibt None zurück."""
        manager = SlotManager()
        
        result = manager.get_slot_state("nonexistent")
        
        assert result is None

    def test_register_duplicate_slot_fails(self):
        """Duplizierter Slot kann nicht registriert werden."""
        manager = SlotManager()
        manager.register_slot("slot_1")
        
        result = manager.register_slot("slot_1")
        
        assert result is False

    def test_list_slots(self):
        """Listet alle Slots."""
        manager = SlotManager()
        manager.register_slot("slot_1")
        manager.register_slot("slot_2")
        manager.register_slot("slot_3")
        
        slots = manager.list_slots()
        
        assert len(slots) == 3
        assert set(slots) == {"slot_1", "slot_2", "slot_3"}

    def test_list_slots_by_state(self):
        """Listet Slots nach Zustand."""
        manager = SlotManager()
        manager.register_slot("slot_1")
        manager.register_slot("slot_2")
        manager.try_acquire_slot("slot_1", "lease_123")
        
        free_slots = manager.list_slots_by_state(SlotStatus.FREE)
        reserved_slots = manager.list_slots_by_state(SlotStatus.RESERVED)
        
        assert free_slots == ["slot_2"]
        assert reserved_slots == ["slot_1"]

    def test_set_slot_maintenance(self):
        """Setzt Slot auf MAINTENANCE."""
        manager = SlotManager()
        manager.register_slot("slot_1")
        
        result = manager.set_slot_maintenance("slot_1", "Scheduled maintenance")
        
        assert result is True
        assert manager.get_slot_state("slot_1") == SlotStatus.MAINTENANCE

    def test_set_slot_offline(self):
        """Setzt Slot auf OFFLINE."""
        manager = SlotManager()
        manager.register_slot("slot_1")
        
        result = manager.set_slot_offline("slot_1", "Hardware failure")
        
        assert result is True
        assert manager.get_slot_state("slot_1") == SlotStatus.OFFLINE

    def test_estop_suspend_fails_for_offline_slot(self):
        """ESTOP-Suspend funktioniert nicht für OFFLINE Slots."""
        manager = SlotManager()
        manager.register_slot("slot_1")
        manager.set_slot_offline("slot_1", "Hardware failure")
        
        result = manager.suspend_slot_for_estop("slot_1")
        
        assert result is False
        assert manager.get_slot_state("slot_1") == SlotStatus.OFFLINE

    def test_estop_suspend_fails_for_maintenance_slot(self):
        """ESTOP-Suspend funktioniert nicht für MAINTENANCE Slots."""
        manager = SlotManager()
        manager.register_slot("slot_1")
        manager.set_slot_maintenance("slot_1", "Scheduled")
        
        result = manager.suspend_slot_for_estop("slot_1")
        
        assert result is False
        assert manager.get_slot_state("slot_1") == SlotStatus.MAINTENANCE

    def test_activate_slot_only_from_reserved(self):
        """Activate nur von RESERVED möglich."""
        manager = SlotManager()
        manager.register_slot("slot_1")
        
        # Von FREE aus kann nicht aktiviert werden
        result = manager.activate_slot("slot_1", "lease_123")
        assert result is False
        
        # Erst reservieren
        manager.try_acquire_slot("slot_1", "lease_123")
        
        # Jetzt aktivieren
        result = manager.activate_slot("slot_1", "lease_123")
        assert result is True
        assert manager.get_slot_state("slot_1") == SlotStatus.ACTIVE
