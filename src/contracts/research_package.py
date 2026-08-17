from typing import Any

from pydantic import BaseModel, ConfigDict, Field


ID_PATTERN = r"^[A-Za-z0-9._-]{1,128}$"


class RoutingNode(BaseModel):
    """RoutingNode: Ein Knoten im Routing-Graph."""

    model_config = ConfigDict(extra="forbid")

    node_id: str = Field(..., min_length=1)
    node_type: str = Field(..., min_length=1)

    capabilities_required: list[str] = Field(default_factory=list)
    successor_nodes: list[str] = Field(default_factory=list)

    branch_condition: str | None = None
    timeout_s: float | None = Field(default=None, gt=0.0)

    metadata: dict[str, Any] = Field(default_factory=dict)


class PackageKontext(BaseModel):
    """PackageKontext: Kontextinformationen für ein ResearchPackage."""

    model_config = ConfigDict(extra="forbid")

    kontext_id: str = Field(..., min_length=1)
    parent_package_id: str | None = None
    related_packages: list[str] = Field(default_factory=list)

    domain: str | None = None
    tags: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)


class RoutingGraph(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_loop_iterations: int = Field(..., gt=0)
    branch_condition_timeout: float = Field(..., gt=0.0)

    nodes: list[RoutingNode] = Field(default_factory=list)
    entry_node_id: str | None = None


class ResearchPackage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    package_id: str = Field(
        ...,
        pattern=ID_PATTERN,
        min_length=1,
        max_length=128,
    )
    source_wegmarke: str = Field(..., min_length=1)
    source_wegmarke_version: str | None = None
    atlas_version_ref: str = Field(..., min_length=1)
    ziel: str = Field(..., min_length=1)

    materials_or_resources: list[str] = Field(default_factory=list)
    parameter_bounds: dict[str, tuple[float, float]] = Field(default_factory=dict)
    routing_graph: RoutingGraph

    gefahren_mitigationen: list[str] = Field(default_factory=list)
    kontext: PackageKontext | None = None

    dimension_expansion_approval: str | None = None
    override_requested: bool = False

    limits: dict[str, float] = Field(default_factory=dict)
    expected_side_effects_or_failure_modes: list[str] = Field(default_factory=list)
    domain_metadata: dict[str, Any] = Field(default_factory=dict)

    questor_spec: dict[str, Any] | None = None
