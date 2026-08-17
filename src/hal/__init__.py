"""HAL package for MYRMEX v2.4.0 / HAL v0.2.0."""

from typing import Protocol, runtime_checkable

from src.contracts.hal_models import (
    EnvironmentManifest,
    EstopState,
    HALCommand,
    HALCommandResult,
    HALCommandStatus,
    HardwareInterlockEvent,
    ProcessCommand,
    ProcessResult,
    ProcessState,
    SlotState,
    ZoneState,
)


@runtime_checkable
class HALInterface(Protocol):
    """HAL interface for MYRMEX v2.4.0 / HAL v0.2.0."""

    def get_environment_manifest(self) -> EnvironmentManifest:
        """Return the environment manifest."""
        ...

    def get_slot_state(self, slot_id: str) -> SlotState:
        """Get state of a specific slot."""
        ...

    def get_zone_state(self, zone_id: str) -> ZoneState:
        """Get state of a specific zone."""
        ...

    def get_process_state(self, process_id: str) -> ProcessState:
        """Get state of a specific process."""
        ...

    def submit_command(self, command: HALCommand) -> HALCommandResult:
        """Submit a HAL command for execution."""
        ...

    def submit_process(self, process: ProcessCommand) -> ProcessResult:
        """Submit a process command for execution."""
        ...

    def get_command_status(self, command_id: str) -> HALCommandStatus:
        """Get status of a specific command."""
        ...

    def get_estop_state(self) -> EstopState:
        """Get current E-Stop state."""
        ...

    def acknowledge_estop(self, acknowledged_by: str) -> EstopState:
        """Acknowledge an E-Stop event."""
        ...

    def handle_interlock_event(self, event: HardwareInterlockEvent) -> None:
        """Handle a hardware interlock event."""
        ...
