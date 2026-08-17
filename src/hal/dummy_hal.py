"""Dummy HAL implementation for Phase 1 testing."""

from typing import Any

from src.contracts.enums import (
    CommandLifecycleState,
    ErrorClass,
    EstopOrigin,
    EstopStateName,
    HALCommandResultStatus,
    LockPolicy,
    ProcessLifecycleState,
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
from src.hal import HALInterface


class DummyHAL(HALInterface):
    """Dummy HAL implementation for Phase 1 testing."""

    def __init__(self) -> None:
        self._environment_manifest = self._create_default_manifest()
        self._slot_states: dict[str, SlotState] = {}
        self._zone_states: dict[str, ZoneState] = {}
        self._process_states: dict[str, ProcessState] = {}
        self._command_statuses: dict[str, HALCommandStatus] = {}
        self._estop_state = EstopState(
            state=EstopStateName.NORMAL,
            origin=EstopOrigin.SOFTWARE,
        )

        # Initialize default slot and zone states
        for slot in self._environment_manifest.slots:
            self._slot_states[slot.slot_id] = SlotState(
                slot_id=slot.slot_id,
                status=SlotStatus.FREE,
            )
        for zone in self._environment_manifest.mutex_zones:
            self._zone_states[zone.zone_id] = ZoneState(
                zone_id=zone.zone_id,
                status=ZoneStatus.FREE,
                lock_policy=zone.lock_policy,
            )

    def _create_default_manifest(self) -> EnvironmentManifest:
        """Create a default environment manifest for testing."""
        return EnvironmentManifest(
            environment_id="dummy-env-001",
            environment_version="0.1.0",
            schema_version="0.2.0",
            slots=[
                SlotDescriptor(
                    slot_id="slot-lab-001",
                    display_name="Lab Actuator Slot 1",
                    resource_class=ResourceClass.LAB_ACTUATOR,
                    capabilities=["move_to", "measure"],
                    physical_actuation=True,
                ),
                SlotDescriptor(
                    slot_id="slot-compute-001",
                    display_name="Compute Node 1",
                    resource_class=ResourceClass.COMPUTE_NODE,
                    capabilities=["compute"],
                    compute_capable=True,
                ),
                SlotDescriptor(
                    slot_id="slot-sandbox-001",
                    display_name="Sandbox Environment 1",
                    resource_class=ResourceClass.SANDBOX_ENVIRONMENT,
                    capabilities=["simulate"],
                    sandbox_capable=True,
                ),
            ],
            mutex_zones=[
                MutexZone(
                    zone_id="zone-lab-001",
                    member_slots=["slot-lab-001"],
                    lock_policy=LockPolicy.EXCLUSIVE,
                ),
            ],
            capabilities=["move_to", "measure", "compute", "simulate"],
            estop_mechanism="software_estop",
            max_command_timeout_s=300.0,
            default_lease_ttl_s=600.0,
            heartbeat_interval_s=30.0,
            supported_security_modes=[SecurityMode.NORMAL, SecurityMode.SANDBOX],
            supported_resource_classes=[
                ResourceClass.LAB_ACTUATOR,
                ResourceClass.COMPUTE_NODE,
                ResourceClass.SANDBOX_ENVIRONMENT,
            ],
        )

    def get_environment_manifest(self) -> EnvironmentManifest:
        """Return the environment manifest."""
        return self._environment_manifest

    def get_slot_state(self, slot_id: str) -> SlotState:
        """Get state of a specific slot."""
        if slot_id not in self._slot_states:
            raise ValueError(f"Unknown slot_id: {slot_id}")
        return self._slot_states[slot_id]

    def get_zone_state(self, zone_id: str) -> ZoneState:
        """Get state of a specific zone."""
        if zone_id not in self._zone_states:
            raise ValueError(f"Unknown zone_id: {zone_id}")
        return self._zone_states[zone_id]

    def get_process_state(self, process_id: str) -> ProcessState:
        """Get state of a specific process."""
        if process_id not in self._process_states:
            raise ValueError(f"Unknown process_id: {process_id}")
        return self._process_states[process_id]

    def submit_command(self, command: HALCommand) -> HALCommandResult:
        """Submit a HAL command for execution (dummy)."""
        slot_state = self.get_slot_state(command.slot_id)

        result = HALCommandResult(
            command_id=command.command_id,
            status=HALCommandResultStatus.SUCCESS,
            slot_state=slot_state,
        )

        self._command_statuses[command.command_id] = HALCommandStatus(
            command_id=command.command_id,
            lifecycle_state=CommandLifecycleState.SUCCESS,
        )

        return result

    def submit_process(self, process: ProcessCommand) -> ProcessResult:
        """Submit a process command for execution (dummy)."""
        process_state = ProcessState(
            process_id=process.process_id,
            device_job_id=process.device_job_id,
            slot_id=process.slot_id,
            lease_ref=process.lease_ref,
            process_state=ProcessLifecycleState.RUNNING,
        )
        self._process_states[process.process_id] = process_state

        return ProcessResult(
            process_id=process.process_id,
            device_job_id=process.device_job_id,
            slot_id=process.slot_id,
            process_state=ProcessLifecycleState.RUNNING,
        )

    def get_command_status(self, command_id: str) -> HALCommandStatus:
        """Get status of a specific command."""
        if command_id not in self._command_statuses:
            raise ValueError(f"Unknown command_id: {command_id}")
        return self._command_statuses[command_id]

    def get_estop_state(self) -> EstopState:
        """Get current E-Stop state."""
        return self._estop_state

    def acknowledge_estop(self, acknowledged_by: str) -> EstopState:
        """Acknowledge an E-Stop event (dummy)."""
        self._estop_state.acknowledged_by = acknowledged_by
        return self._estop_state

    def handle_interlock_event(self, event: HardwareInterlockEvent) -> None:
        """Handle a hardware interlock event (dummy)."""
        pass
