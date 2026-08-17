"""HAL interface for MYRMEX v2.4.0 / HAL v0.2.0."""

from abc import ABC, abstractmethod

from src.contracts.enums import ReleaseAuthority
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


class HalInterface(ABC):
    @abstractmethod
    def get_environment_manifest(self) -> EnvironmentManifest:
        raise NotImplementedError

    @abstractmethod
    def get_slot_state(self, slot_id: str) -> SlotState:
        raise NotImplementedError

    @abstractmethod
    def get_zone_state(self, zone_id: str) -> ZoneState:
        raise NotImplementedError

    @abstractmethod
    def execute_command(self, command: HALCommand) -> HALCommandResult:
        raise NotImplementedError

    @abstractmethod
    def start_process(self, process_command: ProcessCommand) -> ProcessResult:
        raise NotImplementedError

    @abstractmethod
    def monitor_process(self, process_id: str) -> ProcessResult:
        raise NotImplementedError

    @abstractmethod
    def hold_process(self, process_id: str) -> ProcessResult:
        raise NotImplementedError

    @abstractmethod
    def resume_process(self, process_id: str, resume_token: str) -> ProcessResult:
        raise NotImplementedError

    @abstractmethod
    def abort_process(self, process_id: str) -> ProcessResult:
        raise NotImplementedError

    @abstractmethod
    def release_stage(
        self,
        process_id: str,
        stage_id: str,
        release_authority: ReleaseAuthority,
    ) -> ProcessResult:
        raise NotImplementedError

    @abstractmethod
    def report_estop(self, reason: str, trigger_source: str) -> EstopState:
        raise NotImplementedError

    @abstractmethod
    def report_hardware_interlock(
        self,
        interlock_event: HardwareInterlockEvent,
    ) -> EstopState:
        raise NotImplementedError

    @abstractmethod
    def get_estop_state(self) -> EstopState:
        raise NotImplementedError

    @abstractmethod
    def reconcile_slot_state(self, slot_id: str) -> SlotState:
        raise NotImplementedError

    @abstractmethod
    def reconcile_process_state(self, process_id: str) -> ProcessState:
        raise NotImplementedError

    @abstractmethod
    def get_command_status(self, command_id: str) -> HALCommandStatus:
        raise NotImplementedError
