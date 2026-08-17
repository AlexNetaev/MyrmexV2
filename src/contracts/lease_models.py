"""Lease models for MYRMEX v2.4.0."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.contracts.enums import OnLeaseExpiryPolicy, ResourceClass, SlotStatus


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

    on_expiry_policy: OnLeaseExpiryPolicy = OnLeaseExpiryPolicy.SAFE_HOLD

    constraints: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LeaseStatus(BaseModel):
    """LeaseStatus: Der aktuelle Status einer Lease."""

    model_config = ConfigDict(extra="forbid")

    lease_id: str = Field(..., min_length=1)
    slot_id: str | None = None
    package_id: str | None = None

    status: SlotStatus

    granted_at: str = Field(..., min_length=1)
    expires_at: str | None = None
    remaining_ttl_s: float | None = Field(default=None, ge=0.0)

    is_active: bool = False
    is_expired: bool = False
    is_suspended: bool = False

    suspension_reason: str | None = None
    last_heartbeat_at: str | None = None

    on_expiry_policy: OnLeaseExpiryPolicy | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
