"""Tests for HAL contract models."""

import pytest
from pydantic import ValidationError

from src.contracts.enums import (
    CommandLifecycleState,
    DispatchMode,
    ErrorClass,
    EstopOrigin,
    EstopStateName,
    HALCommandResultStatus,
    LockPolicy,
    ProcessLifecycleState,
    ProcessMode,
    ResourceClass,
    SecurityMode,
    SlotStatus,
    ZoneStatus,
)
from src.contracts.hal_models import (
    EnvironmentManifest,
    EstopState,
    HALCommand,
    HALCommandResult,
    HALCommandStatus,
    MutexZone,
    ProcessCommand,
    ProcessResult,
    ProcessState,
    SlotDescriptor,
    SlotState,
    ZoneState,
)


class TestSlotDescriptor:
    """Test SlotDescriptor model."""

    def test_minimal_slot_descriptor(self):
        sd = SlotDescriptor(
            slot_id="slot-001",
            resource_class=ResourceClass.LAB_ACTUATOR,
        )
        assert sd.mutex_group == "default"
        assert sd.physical_actuation is False
        assert sd.compute_capable is False

    def test_compute_slot_descriptor(self):
        sd = SlotDescriptor(
            slot_id="slot-compute-001",
            resource_class=ResourceClass.COMPUTE_NODE,
            compute_capable=True,
            capabilities=["compute", "train"],
            supported_runtimes=["python", "cuda"],
        )
        assert sd.compute_capable is True
        assert len(sd.capabilities) == 2


class TestMutexZone:
    """Test MutexZone model."""

    def test_minimal_mutex_zone(self):
        mz = MutexZone(
            zone_id="zone-001",
            lock_policy=LockPolicy.EXCLUSIVE,
        )
        assert mz.member_slots == []
        assert mz.dynamic_lock_required is False

    def test_zone_with_members(self):
        mz = MutexZone(
            zone_id="zone-lab-001",
            member_slots=["slot-lab-001", "slot-lab-002"],
            lock_policy=LockPolicy.PATH_RESERVATION,
            estop_relevant=True,
        )
        assert len(mz.member_slots) == 2
        assert mz.estop_relevant is True


class TestEnvironmentManifest:
    """Test EnvironmentManifest model."""

    def test_minimal_manifest(self):
        em = EnvironmentManifest(
            environment_id="env-001",
            environment_version="0.1.0",
            schema_version="0.2.0",
            estop_mechanism="software_estop",
            max_command_timeout_s=300.0,
            default_lease_ttl_s=600.0,
            heartbeat_interval_s=30.0,
        )
        assert em.slots == []
        assert em.mutex_zones == []
        assert em.capabilities == []

    def test_full_manifest(self):
        em = EnvironmentManifest(
            environment_id="env-full-001",
            environment_version="1.0.0",
            schema_version="0.2.0",
            slots=[
                SlotDescriptor(
                    slot_id="slot-001",
                    resource_class=ResourceClass.LAB_ACTUATOR,
                )
            ],
            mutex_zones=[
                MutexZone(
                    zone_id="zone-001",
                    lock_policy=LockPolicy.EXCLUSIVE,
                )
            ],
            capabilities=["move_to", "measure"],
            estop_mechanism="hardware_interlock",
            max_command_timeout_s=600.0,
            default_lease_ttl_s=1200.0,
            heartbeat_interval_s=60.0,
            supported_security_modes=[SecurityMode.NORMAL],
            supported_resource_classes=[ResourceClass.LAB_ACTUATOR],
        )
        assert len(em.slots) == 1
        assert len(em.mutex_zones) == 1


class TestSlotState:
    """Test SlotState model."""

    def test_default_slot_state(self):
        ss = SlotState(
            slot_id="slot-001",
            status=SlotStatus.FREE,
        )
        assert ss.device_reachable is True
        assert ss.interlock_latched is False
        assert ss.safe_state_verified is False

    def test_active_slot_state(self):
        ss = SlotState(
            slot_id="slot-001",
            status=SlotStatus.ACTIVE,
            current_lease_ref="lease-001",
            current_process_id="process-001",
        )
        assert ss.status == SlotStatus.ACTIVE
        assert ss.current_lease_ref == "lease-001"


class TestZoneState:
    """Test ZoneState model."""

    def test_free_zone_state(self):
        zs = ZoneState(
            zone_id="zone-001",
            status=ZoneStatus.FREE,
            lock_policy=LockPolicy.EXCLUSIVE,
        )
        assert zs.current_holder_slot_id is None
        assert zs.lock_expires_at is None

    def test_locked_zone_state(self):
        zs = ZoneState(
            zone_id="zone-001",
            status=ZoneStatus.LOCKED,
            lock_policy=LockPolicy.EXCLUSIVE,
            current_holder_slot_id="slot-001",
            lock_expires_at="2024-01-01T01:00:00Z",
        )
        assert zs.status == ZoneStatus.LOCKED
        assert zs.current_holder_slot_id == "slot-001"


class TestProcessState:
    """Test ProcessState model."""

    def test_running_process_state(self):
        ps = ProcessState(
            process_id="process-001",
            slot_id="slot-001",
            lease_ref="lease-001",
            process_state=ProcessLifecycleState.RUNNING,
        )
        assert ps.process_state == ProcessLifecycleState.RUNNING
        assert ps.resume_allowed is False

    def test_paused_process_with_resume(self):
        ps = ProcessState(
            process_id="process-002",
            slot_id="slot-001",
            lease_ref="lease-002",
            process_state=ProcessLifecycleState.PAUSED,
            resume_token="resume-token-abc",
            resume_allowed=True,
        )
        assert ps.resume_allowed is True
        assert ps.resume_token == "resume-token-abc"


class TestHALCommand:
    """Test HALCommand model."""

    def test_minimal_command(self):
        cmd = HALCommand(
            command_id="cmd-001",
            idempotency_key="key-001",
            lease_ref="lease-001",
            slot_id="slot-001",
            capability="move_to",
            operation="execute",
            timeout_s=30.0,
        )
        assert cmd.dispatch_mode == DispatchMode.NORMAL
        assert cmd.security_mode == SecurityMode.NORMAL
        assert cmd.request_source.value == "QUESTOR"

    def test_command_with_parameters(self):
        cmd = HALCommand(
            command_id="cmd-002",
            idempotency_key="key-002",
            lease_ref="lease-002",
            slot_id="slot-002",
            capability="measure",
            operation="execute",
            parameters={"target_position": [1.0, 2.0, 3.0]},
            timeout_s=60.0,
        )
        assert len(cmd.parameters) == 1

    def test_command_with_schema_requires_checksum(self):
        with pytest.raises(ValidationError) as exc_info:
            HALCommand(
                command_id="cmd-003",
                idempotency_key="key-003",
                lease_ref="lease-003",
                slot_id="slot-003",
                capability="compute",
                operation="execute",
                parameter_schema_ref="schema-v1",
                timeout_s=30.0,
            )
        assert "PARAMETER_INVALID" in str(exc_info.value)

    def test_command_with_schema_and_checksum_valid(self):
        cmd = HALCommand(
            command_id="cmd-004",
            idempotency_key="key-004",
            lease_ref="lease-004",
            slot_id="slot-004",
            capability="compute",
            operation="execute",
            parameter_schema_ref="schema-v1",
            parameter_checksum="sha256-abc123",
            timeout_s=30.0,
        )
        assert cmd.parameter_schema_ref == "schema-v1"
        assert cmd.parameter_checksum == "sha256-abc123"


class TestHALCommandResult:
    """Test HALCommandResult model."""

    def test_success_result(self):
        slot_state = SlotState(slot_id="slot-001", status=SlotStatus.FREE)
        result = HALCommandResult(
            command_id="cmd-001",
            status=HALCommandResultStatus.SUCCESS,
            slot_state=slot_state,
        )
        assert result.error_code is None
        assert result.error_class is None

    def test_error_result(self):
        slot_state = SlotState(slot_id="slot-001", status=SlotStatus.ERROR)
        result = HALCommandResult(
            command_id="cmd-002",
            status=HALCommandResultStatus.ERROR,
            error_code="EXECUTION_FAILED",
            error_class=ErrorClass.OPERATIONAL,
            slot_state=slot_state,
        )
        assert result.error_code == "EXECUTION_FAILED"
        assert result.error_class == ErrorClass.OPERATIONAL


class TestProcessCommand:
    """Test ProcessCommand model."""

    def test_minimal_process_command(self):
        pc = ProcessCommand(
            process_id="process-001",
            lease_ref="lease-001",
            slot_id="slot-001",
            capability="compute",
            operation="run_job",
            process_mode=ProcessMode.START,
            timeout_s=300.0,
        )
        assert pc.on_lease_expiry_policy.value == "SAFE_HOLD"
        assert pc.stage_release_policy is None

    def test_process_command_with_schema_validation(self):
        with pytest.raises(ValidationError):
            ProcessCommand(
                process_id="process-002",
                lease_ref="lease-002",
                slot_id="slot-002",
                capability="measure",
                operation="execute",
                process_mode=ProcessMode.START,
                parameter_schema_ref="schema-v1",
                timeout_s=60.0,
            )


class TestProcessResult:
    """Test ProcessResult model."""

    def test_running_process_result(self):
        pr = ProcessResult(
            process_id="process-001",
            slot_id="slot-001",
            process_state=ProcessLifecycleState.RUNNING,
        )
        assert pr.process_state == ProcessLifecycleState.RUNNING
        assert pr.resume_allowed is False

    def test_completed_process_result(self):
        pr = ProcessResult(
            process_id="process-002",
            slot_id="slot-002",
            process_state=ProcessLifecycleState.COMPLETED,
            elapsed_time_s=120.5,
        )
        assert pr.process_state == ProcessLifecycleState.COMPLETED
        assert pr.elapsed_time_s == 120.5


class TestEstopState:
    """Test EstopState model."""

    def test_normal_estop_state(self):
        es = EstopState(
            state=EstopStateName.NORMAL,
            origin=EstopOrigin.SOFTWARE,
        )
        assert es.physical_reset_required is False
        assert es.acknowledged_by is None

    def test_active_estop_state(self):
        es = EstopState(
            state=EstopStateName.ACTIVE,
            origin=EstopOrigin.HARDWARE_INTERLOCK,
            hardware_interlock_id="interlock-001",
            physical_reset_required=True,
            reason="Emergency button pressed",
        )
        assert es.state == EstopStateName.ACTIVE
        assert es.physical_reset_required is True


class TestHALCommandStatus:
    """Test HALCommandStatus model."""

    def test_initial_command_status(self):
        cs = HALCommandStatus(
            command_id="cmd-001",
            lifecycle_state=CommandLifecycleState.RECEIVED,
        )
        assert cs.attempts == 0
        assert cs.last_error is None

    def test_executing_command_status(self):
        cs = HALCommandStatus(
            command_id="cmd-002",
            lifecycle_state=CommandLifecycleState.EXECUTING,
            attempts=1,
        )
        assert cs.lifecycle_state == CommandLifecycleState.EXECUTING
        assert cs.attempts == 1
