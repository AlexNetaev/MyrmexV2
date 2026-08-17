from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.contracts.enums import (
    CommandLifecycleState,
    DispatchMode,
    ErrorClass,
    EstopOrigin,
    EstopStateName,
    HALCommandResultStatus,
    LockPolicy,
    OnLeaseExpiryPolicy,
    ProcessLifecycleState,
    ProcessMode,
    ReleaseAuthority,
    RequestSource,
    ResourceClass,
    SecurityMode,
    SlotStatus,
    ZoneStatus,
)


_DEFAULT_TIMESTAMP = "1970-01-01T00:00:00Z"


class SlotDescriptor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slot_id: str = Field(..., min_length=1)
    display_name: str | None = None
    resource_class: ResourceClass

    capabilities: list[str] = Field(default_factory=list)
    mutex_group: str = Field(default="default", min_length=1)
    physical_zones: list[str] = Field(default_factory=list)

    physical_actuation: bool = False
    compute_capable: bool = False
    sandbox_capable: bool = False

    kinematic_collision_class: str | None = None
    requires_path_reservation: bool = False

    max_concurrent_commands: int = Field(default=1, ge=1)
    estop_controllable: bool = True

    max_command_timeout_s: float = Field(default=0.0, ge=0.0)
    max_process_duration_s: float = Field(default=0.0, ge=0.0)
    max_parameter_payload_bytes: int = Field(default=0, ge=0)

    supported_process_modes: list[str] = Field(default_factory=list)

    accelerator_type: str | None = None
    accelerator_count: int = Field(default=0, ge=0)
    accelerator_memory_gb: float | None = None
    supported_runtimes: list[str] = Field(default_factory=list)


class MutexZone(BaseModel):
    model_config = ConfigDict(extra="forbid")

    zone_id: str = Field(..., min_length=1)
    display_name: str | None = None
    member_slots: list[str] = Field(default_factory=list)
    lock_policy: LockPolicy

    dynamic_lock_required: bool = False
    estop_relevant: bool = False
    max_hold_time_s: float = Field(default=0.0, ge=0.0)


class EnvironmentManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    environment_id: str = Field(..., min_length=1)
    environment_version: str = Field(..., min_length=1)
    schema_version: str = Field(..., min_length=1)

    slots: list[SlotDescriptor] = Field(default_factory=list)
    mutex_zones: list[MutexZone] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)

    estop_mechanism: str = Field(..., min_length=1)

    max_command_timeout_s: float = Field(..., gt=0.0)
    default_lease_ttl_s: float = Field(..., gt=0.0)
    heartbeat_interval_s: float = Field(..., gt=0.0)

    supported_security_modes: list[SecurityMode] = Field(default_factory=list)
    supported_resource_classes: list[ResourceClass] = Field(default_factory=list)


class SlotState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slot_id: str = Field(..., min_length=1)
    status: SlotStatus

    device_reachable: bool = True
    interlock_latched: bool = False
    interlock_source: str | None = None

    safe_state_verified: bool = False
    manual_reset_required: bool = False

    current_lease_ref: str | None = None
    current_process_id: str | None = None
    heartbeat_expires_at: str | None = None

    last_error: str | None = None
    last_command_id: str | None = None
    last_state_change_at: str = Field(default=_DEFAULT_TIMESTAMP)


class ZoneState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    zone_id: str = Field(..., min_length=1)
    status: ZoneStatus

    current_holder_slot_id: str | None = None
    lock_policy: LockPolicy
    lock_expires_at: str | None = None

    last_state_change_at: str = Field(default=_DEFAULT_TIMESTAMP)


class ProcessState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    process_id: str = Field(..., min_length=1)
    device_job_id: str | None = None
    slot_id: str = Field(..., min_length=1)
    lease_ref: str = Field(..., min_length=1)

    process_state: ProcessLifecycleState

    current_stage: str | None = None
    started_at: str | None = None
    expected_duration_s: float | None = Field(default=None, ge=0.0)
    elapsed_time_s: float | None = Field(default=None, ge=0.0)

    resume_token: str | None = None
    resume_allowed: bool = False
    safe_hold_active: bool = False
    manual_release_required: bool = False

    last_state_change_at: str = Field(default=_DEFAULT_TIMESTAMP)
    last_error: str | None = None


class HALCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: str = Field(..., min_length=1)
    idempotency_key: str = Field(..., min_length=1)
    lease_ref: str = Field(..., min_length=1)
    slot_id: str = Field(..., min_length=1)

    capability: str = Field(..., min_length=1)
    operation: str = Field(..., min_length=1)

    parameters: dict[str, Any] = Field(default_factory=dict)

    parameter_schema_ref: str | None = None
    parameter_schema_version: str | None = None
    parameter_checksum: str | None = None
    payload_artifact_ref: str | None = None

    timeout_s: float = Field(..., gt=0.0)

    dispatch_mode: DispatchMode = DispatchMode.NORMAL
    security_mode: SecurityMode = SecurityMode.NORMAL
    request_source: RequestSource = RequestSource.QUESTOR
    correlation_id: str | None = None

    @model_validator(mode="after")
    def _validate_parameter_schema(self) -> "HALCommand":
        if self.parameter_schema_ref is not None and self.parameter_checksum is None:
            raise ValueError("PARAMETER_INVALID")
        return self


class StageRelease(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stage_id: str = Field(..., min_length=1)
    release_required: bool = True
    release_authority: ReleaseAuthority = ReleaseAuthority.SAFETY_PROCESS_OR_HUMAN
    auto_start_allowed: bool = False
    max_wait_time_s: float | None = Field(default=None, ge=0.0)


class StageReleasePolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stages: list[StageRelease] = Field(default_factory=list)


class ProcessCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    process_id: str = Field(..., min_length=1)
    device_job_id: str | None = None

    lease_ref: str = Field(..., min_length=1)
    slot_id: str = Field(..., min_length=1)

    capability: str = Field(..., min_length=1)
    operation: str = Field(..., min_length=1)

    parameters: dict[str, Any] = Field(default_factory=dict)

    parameter_schema_ref: str | None = None
    parameter_schema_version: str | None = None
    parameter_checksum: str | None = None
    payload_artifact_ref: str | None = None

    process_mode: ProcessMode

    expected_process_duration_s: float | None = Field(default=None, gt=0.0)
    process_recipe_ref: str | None = None
    process_recipe_checksum: str | None = None

    on_lease_expiry_policy: OnLeaseExpiryPolicy = OnLeaseExpiryPolicy.SAFE_HOLD
    stage_release_policy: StageReleasePolicy | None = None

    timeout_s: float = Field(..., gt=0.0)

    dispatch_mode: DispatchMode = DispatchMode.NORMAL
    security_mode: SecurityMode = SecurityMode.NORMAL
    request_source: RequestSource = RequestSource.QUESTOR
    correlation_id: str | None = None

    @model_validator(mode="after")
    def _validate_parameter_schema(self) -> "ProcessCommand":
        if self.parameter_schema_ref is not None and self.parameter_checksum is None:
            raise ValueError("PARAMETER_INVALID")
        return self


class HALCommandResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: str = Field(..., min_length=1)
    status: HALCommandResultStatus

    error_code: str | None = None
    error_class: ErrorClass | None = None

    slot_state: SlotState

    started_at: str | None = None
    finished_at: str | None = None
    receipt_checksum: str | None = None

    operational_metrics: dict[str, float] | None = None


class ProcessResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    process_id: str = Field(..., min_length=1)
    device_job_id: str | None = None
    slot_id: str = Field(..., min_length=1)

    process_state: ProcessLifecycleState
    current_stage: str | None = None

    error_code: str | None = None
    error_class: ErrorClass | None = None

    started_at: str | None = None
    finished_at: str | None = None
    elapsed_time_s: float | None = Field(default=None, ge=0.0)

    resume_token: str | None = None
    resume_allowed: bool = False

    operational_metrics: dict[str, float] | None = None


class EstopState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: EstopStateName
    origin: EstopOrigin

    hardware_interlock_id: str | None = None

    physical_reset_required: bool = False
    safe_state_verified: bool = False
    inspection_required: bool = False

    reason: str | None = None
    trigger_source: str | None = None

    affected_slots: list[str] = Field(default_factory=list)
    affected_zones: list[str] = Field(default_factory=list)
    suspended_leases: list[str] = Field(default_factory=list)

    timestamp: str = Field(default=_DEFAULT_TIMESTAMP)
    reset_policy: str = Field(default="MANUAL", min_length=1)
    acknowledged_by: str | None = None


class HardwareInterlockEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timestamp: str = Field(default=_DEFAULT_TIMESTAMP)
    slot_id: str = Field(..., min_length=1)
    interlock_source: str = Field(..., min_length=1)

    severity: ErrorClass = ErrorClass.SAFETY

    affected_commands: list[str] = Field(default_factory=list)
    suspended_leases: list[str] = Field(default_factory=list)

    latch_until_manual_reset: bool = True
    physical_reset_required: bool = True
    device_reachable: bool = False
    safe_state_verified: bool = False


class HALCommandStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: str = Field(..., min_length=1)
    lifecycle_state: CommandLifecycleState

    attempts: int = Field(default=0, ge=0)
    last_error: str | None = None
    last_update_at: str = Field(default=_DEFAULT_TIMESTAMP)
