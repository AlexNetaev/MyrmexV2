"""Atlas models for MYRMEX v2.4.0 - minimal structure for Phase 2."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.contracts.enums import (
    DimensionStatus,
    EventType,
    MissingDataPolicy,
    NormalizationPolicy,
    SignalSeverity,
    SignalType,
    ZoneHealth,
)


class SignalEvent(BaseModel):
    """SignalEvent: Ein Ereignis im Atlas-System."""

    model_config = ConfigDict(extra="forbid")

    signal_id: str = Field(..., min_length=1)
    signal_type: SignalType
    source_package_id: str | None = None
    source_zyklus_id: str | None = None

    timestamp: str = Field(..., min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)

    severity: SignalSeverity = SignalSeverity.WHITE
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


class WissensKristall(BaseModel):
    """WissensKristall: Ein validierter wissenschaftlicher Kristall aus Questor-Ergebnissen."""

    model_config = ConfigDict(extra="forbid")

    kristall_id: str = Field(..., min_length=1)
    source_package_id: str = Field(..., min_length=1)
    source_zyklus_id: str = Field(..., min_length=1)
    questor_instance_id: str = Field(..., min_length=1)

    koordinaten: dict[str, float] = Field(default_factory=dict)
    dimension_status: dict[str, DimensionStatus] = Field(default_factory=dict)

    kristall_daten: dict[str, Any] = Field(default_factory=dict)
    confirmation_count: int = Field(default=1, ge=0)
    decay: float = Field(default=1.0, ge=0.0)
    source_trust: float = Field(default=1.0, ge=0.0, le=1.0)
    half_life_s: float = Field(default=3600.0, gt=0.0)

    created_at: str = Field(..., min_length=1)
    last_updated_at: str = Field(..., min_length=1)


class OperationalEvent(BaseModel):
    """OperationalEvent: Ein operatives Ereignis (kein wissenschaftliches Signal)."""

    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(..., min_length=1)
    event_type: EventType = EventType.OPERATIONAL_EVENT

    source_package_id: str | None = None
    source_zyklus_id: str | None = None
    questor_instance_id: str | None = None

    timestamp: str = Field(..., min_length=1)
    event_data: dict[str, Any] = Field(default_factory=dict)

    error_code: str | None = None
    abbruch_grund: str | None = None


class AtlasSnapshot(BaseModel):
    """AtlasSnapshot: Periodischer Snapshot des Atlas-Zustands."""

    model_config = ConfigDict(extra="forbid")

    snapshot_id: str = Field(..., min_length=1)
    atlas_head_pointer: str = Field(..., min_length=1)

    timestamp: str = Field(..., min_length=1)
    total_events: int = Field(..., ge=0)
    total_crystals: int = Field(..., ge=0)

    checksum: str = Field(..., min_length=1)


class DimensionSpec(BaseModel):
    """DimensionSpec: Spezifikation einer Dimension im Schema."""

    model_config = ConfigDict(extra="forbid")

    unit: str = Field(..., min_length=1)
    range_min: float | None = None
    range_max: float | None = None
    normalization_policy: NormalizationPolicy = NormalizationPolicy.MIN_MAX


class DimensionSchema(BaseModel):
    """DimensionSchema: Schema für Koordinaten-Normalisierung."""

    model_config = ConfigDict(extra="forbid")

    dimension_schema_version: str = Field(..., min_length=1)
    dimensions: dict[str, DimensionSpec] = Field(default_factory=dict)


class ZoneV2(Zone):
    """ZoneV2: Versionierte Zone mit fracture_score und predecessor_ids."""

    model_config = ConfigDict(extra="forbid")

    fracture_score: float = Field(default=0.0, ge=0.0, le=1.0)
    zone_health: ZoneHealth = ZoneHealth.STABIL

    cluster_ids: list[str] = Field(default_factory=list)
    predecessor_zone_ids: list[str] = Field(default_factory=list)

    atlas_version_ref: str = Field(..., min_length=1)

    manual_override: ZoneHealth | None = None


class ClusterV2(Cluster):
    """ClusterV2: Versionierter Cluster mit predecessor_ids."""

    model_config = ConfigDict(extra="forbid")

    kristall_ids: list[str] = Field(default_factory=list)
    centroid: dict[str, float] = Field(default_factory=dict)

    predecessor_cluster_ids: list[str] = Field(default_factory=list)

    zone_id: str = Field(..., min_length=1)
    atlas_version_ref: str = Field(..., min_length=1)
