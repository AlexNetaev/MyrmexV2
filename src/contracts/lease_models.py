"""Lease models for MYRMEX v2.4.0."""

from datetime import datetime
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
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


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
    last_state_change_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

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
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
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
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    abbruch_klasse: AbbruchKlasse = AbbruchKlasse.OPERATIONAL
