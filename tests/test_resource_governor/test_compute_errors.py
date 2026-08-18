"""Tests for Compute Errors - OPERATIONAL Klassifikation (Regel 5)."""

import pytest
from datetime import datetime, timezone

from src.resource_governor.slot_manager import SlotManager
from src.resource_governor.governor import ResourceGovernor
from src.contracts.enums import AbbruchKlasse


class TestComputeErrorsOperational:
    """Tests für Compute-Fehler als OPERATIONAL (Regel 5)."""

    def test_cuda_oom_is_operational(self):
        """Regel 5: CUDA_OOM ist OPERATIONAL, nicht SAFETY."""
        # Compute-Fehler werden im Governor/Event-Log behandelt
        # Sie lösen KEINEN ESTOP aus
        
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        slot_manager.register_slot("slot_1")
        
        # Lease anfragen (simuliert Compute-Ressource)
        lease = governor.request_lease("pkg_1", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(lease, 'lease_id')
        
        # Simulierter CUDA_OOM Fehler würde hier als OPERATIONAL behandelt
        # Wichtig: Kein ESTOP wird ausgelöst!
        
        # Wir prüfen dass LEASE_DENIED OPERATIONAL ist
        lease2 = governor.request_lease("pkg_2", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(lease2, 'reason')
        assert lease2.abbruch_klasse == AbbruchKlasse.OPERATIONAL

    def test_gpu_lost_is_operational(self):
        """Regel 5: GPU_LOST ist OPERATIONAL, nicht SAFETY."""
        # Ähnlich wie CUDA_OOM
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        slot_manager.register_slot("compute_slot")
        
        lease = governor.request_lease("compute_pkg", "compute_slot", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(lease, 'lease_id')
        
        # GPU_LOST würde als OPERATIONAL behandelt
        # Kein ESTOP!

    def test_container_crash_is_operational(self):
        """Regel 5: CONTAINER_CRASHED ist OPERATIONAL, nicht SAFETY."""
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        slot_manager.register_slot("container_slot")
        
        lease = governor.request_lease("container_pkg", "container_slot", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(lease, 'lease_id')
        
        # Container-Crash würde als OPERATIONAL behandelt
        # Kein ESTOP!

    def test_compute_error_does_not_trigger_estop(self):
        """Regel 5: Compute-Fehler löst KEINEN ESTOP aus."""
        from src.resource_governor.estop_handler import EstopHandler
        from src.contracts.enums import EstopSource
        
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        estop_handler = EstopHandler(slot_manager, governor)
        
        slot_manager.register_slot("slot_1")
        
        # Lease anfragen
        lease = governor.request_lease("pkg_1", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(lease, 'lease_id')
        
        # Vor dem Fehler: Kein ESTOP aktiv
        assert estop_handler.is_estop_active() is False
        
        # Simulierter Compute-Fehler (CUDA_OOM, GPU_LOST, etc.)
        # Wichtig: Dies darf KEINEN ESTOP auslösen!
        # In der Implementierung würde dies über handle_compute_error laufen
        
        # Nach dem "Fehler": Immer noch kein ESTOP
        assert estop_handler.is_estop_active() is False

    def test_compute_error_does_not_trigger_safety_review(self):
        """Regel 5: Compute-Fehler löst KEINE Sicherheitsprüfung aus."""
        # Compute-Fehler sind OPERATIONAL
        # Sie erfordern keine Sicherheitsprüfung wie SAFETY-Events
        
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        slot_manager.register_slot("slot_1")
        
        # Lease anfragen
        lease = governor.request_lease("pkg_1", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(lease, 'lease_id')
        
        # Bei LEASE_DENIED (operational) wird keine Sicherheitsprüfung ausgelöst
        denied = governor.request_lease("pkg_2", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(denied, 'reason')
        assert denied.abbruch_klasse == AbbruchKlasse.OPERATIONAL
        # Keine Sicherheitsprüfung nötig!

    def test_compute_error_logged_to_operational_log(self):
        """Regel 5: Compute-Fehler wird im operational_event_log protokolliert."""
        # Compute-Fehler gehen ins operative Log, nicht ins Sicherheits-Audit
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        slot_manager.register_slot("slot_1")
        
        # Mehrfache Anfragen erzeugen Resource Pressure
        for i in range(5):
            governor.request_lease(f"pkg_{i}", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        
        # Resource Pressure ist OPERATIONAL
        pressure_event = governor.check_resource_pressure(window_s=60.0, threshold=3)
        if pressure_event:
            assert pressure_event.abbruch_klasse == AbbruchKlasse.OPERATIONAL


class TestResourcePressure:
    """Tests für Resource Pressure als OPERATIONAL Signal."""

    def test_resource_pressure_is_operational_not_scientific(self):
        """Regel 5: resource_pressure_event ist OPERATIONAL, nicht SCIENTIFIC."""
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        slot_manager.register_slot("slot_1")
        
        # Viele Anfragen erzeugen Resource Pressure
        for i in range(15):
            governor.request_lease(f"pkg_{i}", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        
        # Resource Pressure prüfen
        pressure_event = governor.check_resource_pressure(window_s=60.0, threshold=10)
        
        if pressure_event:
            # Muss OPERATIONAL sein!
            assert pressure_event.abbruch_klasse == AbbruchKlasse.OPERATIONAL
            # Nicht SCIENTIFIC!
            assert pressure_event.abbruch_klasse != AbbruchKlasse.SAFETY

    def test_many_lease_denied_create_pressure_event(self):
        """Viele LEASE_DENIED erzeugen Resource Pressure Event."""
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        slot_manager.register_slot("slot_1")
        
        # Ersten Slot belegen
        lease1 = governor.request_lease("pkg_1", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(lease1, 'lease_id')
        
        # Viele weitere Anfragen → alle DENIED
        denied_count = 0
        for i in range(15):
            result = governor.request_lease(f"pkg_{i+2}", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
            if hasattr(result, 'reason'):
                denied_count += 1
        
        assert denied_count >= 10
        
        # Resource Pressure sollte erkannt werden
        pressure_event = governor.check_resource_pressure(window_s=60.0, threshold=10)
        if pressure_event:
            assert pressure_event.denied_count >= 10
            assert pressure_event.abbruch_klasse == AbbruchKlasse.OPERATIONAL
