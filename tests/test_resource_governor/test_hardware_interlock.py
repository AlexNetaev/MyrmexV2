"""Tests for Hardware Interlock - SAFETY Klassifikation."""

import pytest
from datetime import datetime, timezone, timedelta
import time

from src.resource_governor.slot_manager import SlotManager
from src.resource_governor.governor import ResourceGovernor
from src.resource_governor.estop_handler import EstopHandler
from src.resource_governor.zone_manager import ZoneManager
from src.contracts.enums import AbbruchKlasse, EstopSource


class TestHardwareInterlockSafety:
    """Tests für Hardware-Interlock als SAFETY (Regel 4)."""

    def test_hardware_interlock_is_safety(self):
        """Regel 4: Hardware-Interlock ist SAFETY, nicht OPERATIONAL."""
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        estop_handler = EstopHandler(slot_manager, governor)
        
        # Slot registrieren
        slot_manager.register_slot("slot_1")
        
        # Lease anfragen
        lease = governor.request_lease("pkg_1", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(lease, 'lease_id')
        
        # Hardware-Interlock auslösen
        # Hinweis: trigger_hardware_interlock muss noch implementiert werden
        # Für jetzt testen wir mit trigger_estop
        estop_event = estop_handler.trigger_estop(
            reason="HARDWARE_INTERLOCK_SIMULATED",
            source=EstopSource.HARDWARE_INTERLOCK,
        )
        
        # Muss SAFETY sein!
        assert estop_event.abbruch_klasse == AbbruchKlasse.SAFETY

    def test_hardware_interlock_suspends_leases(self):
        """Regel 4: Hardware-Interlock setzt Leases auf ESTOP_SUSPENDED."""
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        estop_handler = EstopHandler(slot_manager, governor)
        
        # Slot registrieren
        slot_manager.register_slot("slot_1")
        
        # Lease anfragen
        lease = governor.request_lease("pkg_1", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(lease, 'lease_id')
        
        # Hardware-Interlock auslösen
        estop_event = estop_handler.trigger_estop(
            reason="HARDWARE_INTERLOCK",
            source=EstopSource.HARDWARE_INTERLOCK,
        )
        
        # Lease muss suspendiert sein
        lease_status = governor.get_lease_status(lease.lease_id)
        assert lease_status is not None
        assert lease_status.is_suspended is True

    def test_hardware_interlock_sets_zone_interlocked(self):
        """Regel 4: Hardware-Interlock setzt Zone auf INTERLOCKED."""
        zone_manager = ZoneManager()
        zone_manager.register_zone("zone_1")
        
        # Zone locken
        zone_manager.request_zone_lock(
            zone_id="zone_1",
            slot_id="slot_1",
            lease_ref="lease_123",
        )
        assert zone_manager.get_zone_state("zone_1") == "LOCKED"
        
        # Hardware-Interlock auslösen
        interlocked = zone_manager.suspend_zone_for_interlock(
            zone_id="zone_1",
            interlock_source="PRESSURE_SENSOR",
        )
        assert interlocked is True
        assert zone_manager.get_zone_state("zone_1") == "INTERLOCKED"

    def test_hardware_interlock_sets_slot_interlocked(self):
        """Regel 4: Hardware-Interlock setzt Slot auf INTERLOCKED."""
        # Slots haben aktuell nur ESTOP_SUSPENDED, nicht INTERLOCKED
        # Dies wird in der Implementierung hinzugefügt
        slot_manager = SlotManager()
        slot_manager.register_slot("slot_1")
        
        # Slot belegen
        slot_manager.try_acquire_slot("slot_1", "lease_123")
        slot_manager.activate_slot("slot_1", "lease_123")
        
        # ESTOP auslösen (simuliert Interlock)
        suspended = slot_manager.suspend_slot_for_estop("slot_1")
        assert suspended is True
        
        state = slot_manager.get_slot_state("slot_1")
        assert state == state.__class__.ESTOP_SUSPENDED

    def test_hardware_interlock_requires_physical_reset(self):
        """Regel 4: Hardware-Interlock erfordert physischen Reset."""
        zone_manager = ZoneManager()
        zone_manager.register_zone("zone_1")
        
        # Zone locken und Interlock auslösen
        zone_manager.request_zone_lock(zone_id="zone_1", slot_id="slot_1", lease_ref="lease_123")
        zone_manager.suspend_zone_for_interlock("zone_1", "PRESSURE_SENSOR")
        
        # Reset OHNE physischen Reset → muss fehlschlagen
        reset_no_physical = zone_manager.reset_zone_after_interlock(
            "zone_1",
            authorized_by="operator_1",
            physical_reset=False,
        )
        assert reset_no_physical is False
        assert zone_manager.get_zone_state("zone_1") == "INTERLOCKED"
        
        # Reset MIT physischem Reset → muss erfolgreich sein
        reset_physical = zone_manager.reset_zone_after_interlock(
            "zone_1",
            authorized_by="operator_1",
            physical_reset=True,
        )
        assert reset_physical is True
        assert zone_manager.get_zone_state("zone_1") == "FREE"

    def test_hardware_interlock_not_software_resettable(self):
        """Regel 4: Hardware-Interlock kann NICHT per Software zurückgesetzt werden."""
        zone_manager = ZoneManager()
        zone_manager.register_zone("zone_1")
        
        # Zone locken und Interlock auslösen
        zone_manager.request_zone_lock(zone_id="zone_1", slot_id="slot_1", lease_ref="lease_123")
        zone_manager.suspend_zone_for_interlock("zone_1", "PRESSURE_SENSOR")
        
        # Versuchter Software-Reset (physical_reset=False) → muss fehlschlagen
        software_reset = zone_manager.reset_zone_after_interlock(
            "zone_1",
            authorized_by="operator_1",
            physical_reset=False,  # Kein physischer Reset!
        )
        assert software_reset is False
        
        # Zone muss immer noch INTERLOCKED sein
        assert zone_manager.get_zone_state("zone_1") == "INTERLOCKED"

    def test_software_estop_is_not_hardware_interlock(self):
        """Software-ESTOP ist NICHT dasselbe wie Hardware-Interlock."""
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        estop_handler = EstopHandler(slot_manager, governor)
        
        # Slot registrieren
        slot_manager.register_slot("slot_1")
        
        # Software-ESTOP auslösen
        software_estop = estop_handler.trigger_estop(
            reason="SOFTWARE_ESTOP",
            source=EstopSource.SAFETY_MONITOR,  # Software-Quelle
        )
        
        # Ist SAFETY, aber kein Hardware-Interlock
        assert software_estop.abbruch_klasse == AbbruchKlasse.SAFETY
        assert software_estop.source == EstopSource.SAFETY_MONITOR

    def test_software_estop_allows_software_reset(self):
        """Software-ESTOP kann per Software zurückgesetzt werden (mit Autorisierung)."""
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        estop_handler = EstopHandler(slot_manager, governor)
        
        # Slot registrieren
        slot_manager.register_slot("slot_1")
        
        # Software-ESTOP auslösen
        estop_handler.trigger_estop(
            reason="SOFTWARE_ESTOP",
            source=EstopSource.SAFETY_MONITOR,
        )
        
        # Reset mit Autorisierung (kein physischer Reset nötig)
        reset = estop_handler.reset_estop(
            estop_handler._current_estop_id,
            authorized_by="operator_1",
        )
        assert reset is True
        
        # ESTOP muss zurückgesetzt sein
        assert estop_handler.get_current_estop() is None


class TestInterlockVsEstop:
    """Tests zum Unterschied zwischen Interlock und ESTOP."""

    def test_interlock_harder_than_estop(self):
        """INTERLOCKED ist härter als ESTOP_SUSPENDED."""
        zone_manager = ZoneManager()
        zone_manager.register_zone("zone_1")
        
        # Zone locken
        zone_manager.request_zone_lock(zone_id="zone_1", slot_id="slot_1", lease_ref="lease_123")
        
        # Erst ESTOP
        zone_manager.suspend_zone_for_estop("zone_1")
        assert zone_manager.get_zone_state("zone_1") == "ESTOP_SUSPENDED"
        
        # Zurücksetzen
        zone_manager.reset_zone_after_estop("zone_1", "operator_1")
        assert zone_manager.get_zone_state("zone_1") == "FREE"
        
        # Jetzt Interlock
        zone_manager.request_zone_lock(zone_id="zone_1", slot_id="slot_1", lease_ref="lease_123")
        zone_manager.suspend_zone_for_interlock("zone_1", "SENSOR")
        assert zone_manager.get_zone_state("zone_1") == "INTERLOCKED"
        
        # Wichtig: Interlock kann nicht mit ESTOP-Reset zurückgesetzt werden
        reset_estop = zone_manager.reset_zone_after_estop("zone_1", "operator_1")
        assert reset_estop is False  # Weil Zone INTERLOCKED, nicht ESTOP_SUSPENDED
        
        # Nur physischer Reset funktioniert
        reset_physical = zone_manager.reset_zone_after_interlock(
            "zone_1",
            "operator_1",
            physical_reset=True,
        )
        assert reset_physical is True
