"""Atlas models for MYRMEX v2.4.0 - minimal structure for Phase 2."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SignalEvent(BaseModel):
    """SignalEvent: Ein Ereignis im Atlas-System."""

    model_config = ConfigDict(extra="forbid")

    signal_id: str = Field(..., min_length=1)
    signal_type: str = Field(..., min_length=1)
    source_package_id: str | None = None
    source_zyklus_id: str | None = None

    timestamp: str = Field(..., min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)

    severity: str = Field(default="INFO", min_length=1)
    acknowledged: bool = False


class Zone(BaseModel):
    """Zone: Eine logische oder physische Zone im Atlas."""

    model_config = ConfigDict(extra="forbid")

    zone_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: str | None = None

    parent_zone_id: str | None = None
    child_zones: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)
    constraints: list[str] = Field(default_factory=list)


class Cluster(BaseModel):
    """Cluster: Eine Gruppierung von Zonen oder Ressourcen."""

    model_config = ConfigDict(extra="forbid")

    cluster_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: str | None = None

    member_zones: list[str] = Field(default_factory=list)
    member_resources: list[str] = Field(default_factory=list)

    capacity: dict[str, float] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
