"""Dummy HAL implementation for Phase 1 testing."""

from src.contracts.enums import (
    CommandLifecycleState,
    ErrorClass,
    EstopOrigin,
    EstopStateName,
    HALCommandResultStatus,
    LockPolicy,
    ProcessLifecycleState,
    ReleaseAuthority,
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
    HardwareInterlockEvent,
    MutexZone,
    ProcessCommand,
    ProcessResult,
    ProcessState,
    SlotDescriptor,
    SlotState,
    ZoneState,
)
from src.hal.hal_interface import HalInterface


_DUMMY_TIMESTAMP = "1970-01-01T00:00:00Z"


class DummyHal(HalInterface):
    """Dummy HAL implementation for Phase 1 testing."""

    def get_environment_manifest(self) -> EnvironmentManifest:
        slot = SlotDescriptor(
            slot_id="dummy-slot",
            display_name="Dummy Sandbox Slot",
            resource_class=ResourceClass.SANDBOX_ENVIRONMENT,
            capabilities=["dummy"],
            mutex_group="dummy-group",
            physical_zones=["dummy-zone"],
            physical_actuation=False,
            compute_capable=False,
            sandbox_capable=True,
            max_command_timeout_s=10.0,
            max_process_duration_s=10.0,
            max_parameter_payload_bytes=1024,
            supported_process_modes=["START", "MONITOR", "HOLD", "ABORT"],
        )

        zone = MutexZone(
            zone_id="dummy-zone",
            display_name="Dummy Zone",
            member_slots=["dummy-slot"],
            lock_policy=LockPolicy.EXCLUSIVE,
            dynamic_lock_required=False,
            estop_relevant=False,
            max_hold_time_s=10.0,
        )

        return EnvironmentManifest(
            environment_id="dummy-environment",
            environment_version="0.2.0",
            schema_version="hal-0.2.0",
            slots=[slot],
            mutex_zones=[zone],
            capabilities=["dummy"],
            estop_mechanism="software",
            max_command_timeout_s=10.0,
            default_lease_ttl_s=60.0,
            heartbeat_interval_s=5.0,
            supported_security_modes=[
                SecurityMode.SANDBOX,
                SecurityMode.DEV_SANDBOX_ONLY,
            ],
            supported_resource_classes=[
                ResourceClass.SANDBOX_ENVIRONMENT,
            ],
        )

    def get_slot_state(self, slot_id: str) -> SlotState:
        return SlotState(
            slot_id=slot_id,
            status=SlotStatus.FREE,
        )

    def get_zone_state(self, zone_id: str) -> ZoneState:
        return ZoneState(
            zone_id=zone_id,
            status=ZoneStatus.FREE,
            lock_policy=LockPolicy.EXCLUSIVE,
        )

    def execute_command(self, command: HALCommand) -> HALCommandResult:
        return HALCommandResult(
            command_id=command.command_id,
            status=HALCommandResultStatus.DENIED,
            error_code="LEASE_INVALID",
            error_class=ErrorClass.OPERATIONAL,
            slot_state=SlotState(
                slot_id=command.slot_id,
                status=SlotStatus.FREE,
            ),
        )

    def start_process(self, process_command: ProcessCommand) -> ProcessResult:
        return ProcessResult(
            process_id=process_command.process_id,
            slot_id=process_command.slot_id,
            process_state=ProcessLifecycleState.FAULT,
            error_code="PROCESS_INVALID",
            error_class=ErrorClass.OPERATIONAL,
        )

    def monitor_process(self, process_id: str) -> ProcessResult:
        return ProcessResult(
            process_id=process_id,
            slot_id="unknown",
            process_state=ProcessLifecycleState.UNKNOWN,
            error_code="RECOVERY_UNSAFE",
            error_class=ErrorClass.OPERATIONAL,
        )

    def hold_process(self, process_id: str) -> ProcessResult:
        return ProcessResult(
            process_id=process_id,
            slot_id="unknown",
            process_state=ProcessLifecycleState.UNKNOWN,
            error_code="RECOVERY_UNSAFE",
            error_class=ErrorClass.OPERATIONAL,
        )

    def resume_process(self, process_id: str, resume_token: str) -> ProcessResult:
        return ProcessResult(
            process_id=process_id,
            slot_id="unknown",
            process_state=ProcessLifecycleState.UNKNOWN,
            error_code="RECOVERY_UNSAFE",
            error_class=ErrorClass.OPERATIONAL,
        )

    def abort_process(self, process_id: str) -> ProcessResult:
        return ProcessResult(
            process_id=process_id,
            slot_id="unknown",
            process_state=ProcessLifecycleState.UNKNOWN,
            error_code="RECOVERY_UNSAFE",
            error_class=ErrorClass.OPERATIONAL,
        )

    def release_stage(
        self,
        process_id: str,
        stage_id: str,
        release_authority: ReleaseAuthority,
    ) -> ProcessResult:
        return ProcessResult(
            process_id=process_id,
            slot_id="unknown",
            process_state=ProcessLifecycleState.WAITING_FOR_RELEASE,
            error_code="STAGE_RELEASE_DENIED",
            error_class=ErrorClass.OPERATIONAL,
        )

    def report_estop(self, reason: str, trigger_source: str) -> EstopState:
        return EstopState(
            state=EstopStateName.ACTIVE,
            origin=EstopOrigin.SOFTWARE,
            reason=reason,
            trigger_source=trigger_source,
            reset_policy="MANUAL",
        )

    def report_hardware_interlock(
        self,
        interlock_event: HardwareInterlockEvent,
    ) -> EstopState:
        return EstopState(
            state=EstopStateName.LATCHED,
            origin=EstopOrigin.HARDWARE_INTERLOCK,
            hardware_interlock_id=interlock_event.interlock_source,
            physical_reset_required=True,
            safe_state_verified=False,
            inspection_required=True,
            reason="HARDWARE_INTERLOCK_TRIGGERED",
            trigger_source=interlock_event.interlock_source,
            affected_slots=[interlock_event.slot_id],
            reset_policy="MANUAL",
        )

    def get_estop_state(self) -> EstopState:
        return EstopState(
            state=EstopStateName.NORMAL,
            origin=EstopOrigin.SOFTWARE,
            reset_policy="NONE",
        )

    def reconcile_slot_state(self, slot_id: str) -> SlotState:
        return SlotState(
            slot_id=slot_id,
            status=SlotStatus.ERROR,
            last_error="RECOVERY_UNSAFE",
        )

    def reconcile_process_state(self, process_id: str) -> ProcessState:
        return ProcessState(
            process_id=process_id,
            slot_id="unknown",
            lease_ref="unknown",
            process_state=ProcessLifecycleState.UNKNOWN,
            last_error="RECOVERY_UNSAFE",
        )

    def get_command_status(self, command_id: str) -> HALCommandStatus:
        return HALCommandStatus(
            command_id=command_id,
            lifecycle_state=CommandLifecycleState.RECEIVED,
            attempts=0,
            last_update_at=_DUMMY_TIMESTAMP,
        )
