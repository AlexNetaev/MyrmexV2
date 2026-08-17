"""Tests for Dummy HAL implementation."""

import pytest

from src.contracts.enums import (
    CommandLifecycleState,
    EstopOrigin,
    EstopStateName,
    HALCommandResultStatus,
    LockPolicy,
    ProcessLifecycleState,
    ResourceClass,
    SlotStatus,
)
from src.contracts.hal_models import HALCommand, HardwareInterlockEvent, ProcessCommand
from src.hal.dummy_hal import DummyHAL


class TestDummyHALInitialization:
    """Test DummyHAL initialization."""

    def test_default_manifest(self):
        hal = DummyHAL()
        manifest = hal.get_environment_manifest()
        assert manifest.environment_id == "dummy-env-001"
        assert manifest.environment_version == "0.1.0"
        assert len(manifest.slots) == 3

    def test_initial_slot_states(self):
        hal = DummyHAL()
        for slot in hal.get_environment_manifest().slots:
            state = hal.get_slot_state(slot.slot_id)
            assert state.slot_id == slot.slot_id
            assert state.status == SlotStatus.FREE

    def test_initial_zone_states(self):
        hal = DummyHAL()
        for zone in hal.get_environment_manifest().mutex_zones:
            state = hal.get_zone_state(zone.zone_id)
            assert state.zone_id == zone.zone_id
            assert state.status.value == "FREE"


class TestDummyHALSlotOperations:
    """Test DummyHAL slot operations."""

    def test_get_valid_slot_state(self):
        hal = DummyHAL()
        state = hal.get_slot_state("slot-lab-001")
        assert state.slot_id == "slot-lab-001"
        assert state.status == SlotStatus.FREE

    def test_get_invalid_slot_state(self):
        hal = DummyHAL()
        with pytest.raises(ValueError, match="Unknown slot_id"):
            hal.get_slot_state("nonexistent-slot")


class TestDummyHALZoneOperations:
    """Test DummyHAL zone operations."""

    def test_get_valid_zone_state(self):
        hal = DummyHAL()
        state = hal.get_zone_state("zone-lab-001")
        assert state.zone_id == "zone-lab-001"
        assert state.lock_policy == LockPolicy.EXCLUSIVE

    def test_get_invalid_zone_state(self):
        hal = DummyHAL()
        with pytest.raises(ValueError, match="Unknown zone_id"):
            hal.get_zone_state("nonexistent-zone")


class TestDummyHALCommandSubmission:
    """Test DummyHAL command submission."""

    def test_submit_command_success(self):
        hal = DummyHAL()
        cmd = HALCommand(
            command_id="cmd-test-001",
            idempotency_key="key-test-001",
            lease_ref="lease-test-001",
            slot_id="slot-lab-001",
            capability="move_to",
            operation="execute",
            timeout_s=30.0,
        )
        result = hal.submit_command(cmd)
        assert result.command_id == "cmd-test-001"
        assert result.status == HALCommandResultStatus.SUCCESS

    def test_submit_command_updates_status(self):
        hal = DummyHAL()
        cmd = HALCommand(
            command_id="cmd-test-002",
            idempotency_key="key-test-002",
            lease_ref="lease-test-002",
            slot_id="slot-compute-001",
            capability="compute",
            operation="execute",
            timeout_s=60.0,
        )
        hal.submit_command(cmd)
        status = hal.get_command_status("cmd-test-002")
        assert status.command_id == "cmd-test-002"
        assert status.lifecycle_state == CommandLifecycleState.SUCCESS

    def test_get_invalid_command_status(self):
        hal = DummyHAL()
        with pytest.raises(ValueError, match="Unknown command_id"):
            hal.get_command_status("nonexistent-command")


class TestDummyHALProcessSubmission:
    """Test DummyHAL process submission."""

    def test_submit_process_success(self):
        hal = DummyHAL()
        proc = ProcessCommand(
            process_id="proc-test-001",
            lease_ref="lease-test-003",
            slot_id="slot-compute-001",
            capability="compute",
            operation="run_job",
            process_mode="START",
            timeout_s=300.0,
        )
        result = hal.submit_process(proc)
        assert result.process_id == "proc-test-001"
        assert result.process_state == ProcessLifecycleState.RUNNING

    def test_submit_process_creates_state(self):
        hal = DummyHAL()
        proc = ProcessCommand(
            process_id="proc-test-002",
            device_job_id="job-001",
            lease_ref="lease-test-004",
            slot_id="slot-sandbox-001",
            capability="simulate",
            operation="run_simulation",
            process_mode="START",
            timeout_s=600.0,
        )
        hal.submit_process(proc)
        state = hal.get_process_state("proc-test-002")
        assert state.process_id == "proc-test-002"
        assert state.process_state == ProcessLifecycleState.RUNNING

    def test_get_invalid_process_state(self):
        hal = DummyHAL()
        with pytest.raises(ValueError, match="Unknown process_id"):
            hal.get_process_state("nonexistent-process")


class TestDummyHALEstopOperations:
    """Test DummyHAL E-Stop operations."""

    def test_initial_estop_state(self):
        hal = DummyHAL()
        state = hal.get_estop_state()
        assert state.state == EstopStateName.NORMAL
        assert state.origin == EstopOrigin.SOFTWARE

    def test_acknowledge_estop(self):
        hal = DummyHAL()
        state = hal.acknowledge_estop("test-user")
        assert state.acknowledged_by == "test-user"

    def test_handle_interlock_event(self):
        hal = DummyHAL()
        event = HardwareInterlockEvent(
            slot_id="slot-lab-001",
            interlock_source="emergency_button",
        )
        # Should not raise
        hal.handle_interlock_event(event)


class TestDummyHALInterfaceCompliance:
    """Test that DummyHAL implements HALInterface correctly."""

    def test_has_required_methods(self):
        hal = DummyHAL()
        # Check all required methods exist
        assert hasattr(hal, "get_environment_manifest")
        assert hasattr(hal, "get_slot_state")
        assert hasattr(hal, "get_zone_state")
        assert hasattr(hal, "get_process_state")
        assert hasattr(hal, "submit_command")
        assert hasattr(hal, "submit_process")
        assert hasattr(hal, "get_command_status")
        assert hasattr(hal, "get_estop_state")
        assert hasattr(hal, "acknowledge_estop")
        assert hasattr(hal, "handle_interlock_event")
