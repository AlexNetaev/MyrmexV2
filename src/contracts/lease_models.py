"""Lease models for MYRMEX v2.4.0."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.contracts.enums import (
    AbbruchKlasse,
    EstopSource,
    LeaseStatusName,
    OnLeaseExpiryPolicy,
    ResourceClass,
    SlotStatus,
)


class MutexZone(BaseModel):
    """MutexZone: Eine physische Zone mit Mutex-Eigenschaften."""

    model_config = ConfigDict(extra="forbid")

    zone_id: str = Field(..., min_length=1)
    member_slots: list[str] = Field(default_factory=list)
    lock_policy: str = "EXCLUSIVE"  # EXCLUSIVE, SINGLE_OCCUPANT, PATH_RESERVATION, CONTAINER_LOCK
    dynamic_lock_required: bool = True
    estop_relevant: bool = True
    max_hold_time_s: float = Field(default=300.0, gt=0.0)


class ZoneState(BaseModel):
    """ZoneState: Der aktuelle Zustand einer Zone."""

    model_config = ConfigDict(extra="forbid")

    zone_id: str = Field(..., min_length=1)
    status: str = "FREE"  # FREE, LOCKED, PATH_RESERVED, ESTOP_SUSPENDED, INTERLOCKED, MAINTENANCE
    current_holder_slot_id: str | None = None
    lock_policy: str | None = None
    lock_expires_at: str | None = None
    last_state_change_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ZoneLockResponse(BaseModel):
    """ZoneLockResponse: Antwort auf eine Zonen-Lock-Anfrage."""

    model_config = ConfigDict(extra="forbid")

    zone_id: str = Field(..., min_length=1)
    status: str = "GRANTED"  # GRANTED, DENIED, TIMEOUT
    lock_id: str | None = None
    lock_expires_at: str | None = None
    error_code: str | None = None


class PathLeaseGrant(BaseModel):
    """PathLeaseGrant: Eine gewährte Pfad-Lease."""

    model_config = ConfigDict(extra="forbid")

    path_lease_id: str = Field(..., min_length=1)
    package_id: str = Field(..., min_length=1)
    slot_ids: list[str] = Field(..., min_length=1)
    zone_locks: list[str] = Field(default_factory=list)
    ttl_s: float = Field(..., gt=0.0)
    granted_at: str = Field(..., min_length=1)
    expires_at: str | None = None


class PathLeaseDenied(BaseModel):
    """PathLeaseDenied: Abgelehnte Pfad-Lease-Anfrage."""

    model_config = ConfigDict(extra="forbid")

    package_id: str = Field(..., min_length=1)
    slot_ids: list[str] = Field(..., min_length=1)
    reason: str = Field(..., min_length=1)
    blocking_slot_id: str | None = None
    retry_after_s: float | None = Field(default=None, ge=0.0)
    abbruch_klasse: AbbruchKlasse = AbbruchKlasse.OPERATIONAL


class HardwareInterlockEvent(BaseModel):
    """HardwareInterlockEvent: Ein Hardware-Interlock-Ereignis."""

    model_config = ConfigDict(extra="forbid")

    interlock_id: str = Field(..., min_length=1)
    slot_id: str = Field(..., min_length=1)
    zone_id: str | None = None
    interlock_source: str = Field(..., min_length=1)
    severity: AbbruchKlasse = AbbruchKlasse.SAFETY
    physical_reset_required: bool = True
    device_reachable: bool = False
    safe_state_verified: bool = False
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ComputeResourceRequest(BaseModel):
    """ComputeResourceRequest: Anfrage für Compute-Ressourcen."""

    model_config = ConfigDict(extra="forbid")

    resource_bundle_ref: str | None = None
    accelerators: list[str] = Field(default_factory=list)
    cpu_cores: int = Field(default=1, ge=1)
    memory_gb: float = Field(default=1.0, gt=0.0)


class LeaseGrant(BaseModel):
    """LeaseGrant: Eine gewährte Lease für eine Ressource."""

    model_config = ConfigDict(extra="forbid")

    lease_id: str = Field(..., min_length=1)
    slot_id: str | None = None
    path_id: str | None = None
    package_id: str | None = None

    resource_class: ResourceClass | None = None

    physical_execution_allowed: bool = False
    sandbox_execution_allowed: bool = False
    compute_execution_allowed: bool = False

    granted_at: str = Field(..., min_length=1)
    expires_at: str | None = None
    ttl_seconds: float | None = Field(default=None, gt=0.0)
    heartbeat_interval_s: float | None = Field(default=None, gt=0.0)

    on_expiry_policy: OnLeaseExpiryPolicy = OnLeaseExpiryPolicy.SAFE_HOLD

    constraints: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LeaseDenied(BaseModel):
    """LeaseDenied: Abgelehnte Lease-Anfrage."""

    model_config = ConfigDict(extra="forbid")

    package_id: str = Field(..., min_length=1)
    slot_id: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=1)
    retry_after_s: float | None = Field(default=None, ge=0.0)
    abbruch_klasse: AbbruchKlasse = AbbruchKlasse.OPERATIONAL
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class LeaseStatus(BaseModel):
    """LeaseStatus: Der aktuelle Status einer Lease."""

    model_config = ConfigDict(extra="forbid")

    lease_id: str = Field(..., min_length=1)
    slot_id: str | None = None
    package_id: str | None = None

    status: LeaseStatusName = Field(..., description="Der aktuelle Status der Lease")

    granted_at: str | None = None
    expires_at: str | None = None
    remaining_ttl_s: float | None = Field(default=None, ge=0.0)

    is_active: bool = False
    is_expired: bool = False
    is_suspended: bool = False

    suspension_reason: str | None = None
    last_heartbeat_at: str | None = None
    last_state_change_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    on_expiry_policy: OnLeaseExpiryPolicy | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EstopEvent(BaseModel):
    """EstopEvent: Ein ESTOP-Ereignis."""

    model_config = ConfigDict(extra="forbid")

    estop_id: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=1)
    source: EstopSource
    affected_leases: list[str] = Field(default_factory=list)
    affected_slots: list[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    abbruch_klasse: AbbruchKlasse = AbbruchKlasse.SAFETY
    reset_authorized_by: str | None = None
    reset_at: str | None = None


class ResourcePressureEvent(BaseModel):
    """ResourcePressureEvent: Operatives Signal bei Ressourcenknappheit."""

    model_config = ConfigDict(extra="forbid")

    event_type: str = "RESOURCE_PRESSURE"
    slot_id: str | None = None
    denied_count: int = Field(..., ge=0)
    window_s: float = Field(..., gt=0.0)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    abbruch_klasse: AbbruchKlasse = AbbruchKlasse.OPERATIONAL
