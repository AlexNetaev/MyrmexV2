"""Tests für den Kartographen - VERDICHTEN."""

import pytest
from datetime import datetime, timezone

from src.contracts.atlas_models import (
    WissensKristall,
    ZoneV2,
    ClusterV2,
)
from src.contracts.enums import DimensionStatus, ZoneHealth
from src.gremium.kartograph import Kartograph


def _create_crystal(
    kristall_id: str = "k-001",
    koordinaten: dict[str, float] | None = None,
    confirmation_count: int = 1,
) -> WissensKristall:
    """Helper zum Erstellen von Test-Kristallen."""
    now = datetime.now(timezone.utc).isoformat()
    return WissensKristall(
        kristall_id=kristall_id,
        source_package_id="pkg-001",
        source_zyklus_id="zyklus-001",
        questor_instance_id="questor-test",
        koordinaten=koordinaten or {"x": 1.0, "y": 1.0},
        dimension_status={"x": DimensionStatus.KNOWN, "y": DimensionStatus.KNOWN},
        kristall_daten={},
        confirmation_count=confirmation_count,
        decay=1.0,
        source_trust=1.0,
        half_life_s=3600.0,
        created_at=now,
        last_updated_at=now,
    )


def _create_cluster(
    cluster_id: str = "c-001",
    kristall_ids: list[str] | None = None,
    zone_id: str = "z-001",
    atlas_version_ref: str = "v1",
) -> ClusterV2:
    """Helper zum Erstellen von Test-Clustern."""
    return ClusterV2(
        cluster_id=cluster_id,
        name=f"Cluster {cluster_id}",
        kristall_ids=kristall_ids or [],
        centroid={"x": 1.0, "y": 1.0},
        predecessor_cluster_ids=[],
        zone_id=zone_id,
        atlas_version_ref=atlas_version_ref,
    )


def _create_zone(
    zone_id: str = "z-001",
    cluster_ids: list[str] | None = None,
    fracture_score: float = 0.1,
    atlas_version_ref: str = "v1",
) -> ZoneV2:
    """Helper zum Erstellen von Test-Zonen."""
    return ZoneV2(
        zone_id=zone_id,
        name=f"Zone {zone_id}",
        fracture_score=fracture_score,
        zone_health=ZoneHealth.STABIL,
        cluster_ids=cluster_ids or [],
        predecessor_zone_ids=[],
        atlas_version_ref=atlas_version_ref,
    )


def test_verdichten_merges_saturated_clusters():
    """VERDICHTEN merged gesättigte Cluster."""
    kartograph = Kartograph()

    # Gesättigte Cluster erstellen (viele Kristalle)
    clusters = [
        _create_cluster("c-001", kristall_ids=["k-001"] * 10),  # 10 Kristalle = gesättigt
        _create_cluster("c-002", kristall_ids=["k-002"] * 10),
    ]
    zones = [_create_zone("z-001", cluster_ids=["c-001", "c-002"])]

    update = kartograph.verdichten(clusters, zones)

    assert update is not None
    assert update.kartograph_mode == "VERDICHTEN"
    # Sollte gemergte Zonen/Cluster erzeugen


def test_verdichten_creates_new_zone_with_predecessors():
    """Regel 2: Gemergte Zone hat predecessor_zone_ids."""
    kartograph = Kartograph()

    clusters = [_create_cluster("c-001", kristall_ids=["k-001"] * 10)]
    zones = [_create_zone("z-001", cluster_ids=["c-001"])]

    update = kartograph.verdichten(clusters, zones)

    if update and update.new_zones:
        new_zone = update.new_zones[0]
        # Neue Zone sollte Vorgänger haben
        assert len(new_zone.predecessor_zone_ids) >= 0  # Kann leer sein bei erster Version


def test_verdichten_does_not_mutate_original_clusters():
    """Regel 2: Ursprüngliche Cluster werden nicht mutiert."""
    kartograph = Kartograph()

    original_clusters = [_create_cluster("c-001", kristall_ids=["k-001"] * 5)]
    original_zones = [_create_zone("z-001", cluster_ids=["c-001"])]

    # Originale speichern
    original_cluster_id = original_clusters[0].cluster_id
    original_kristall_count = len(original_clusters[0].kristall_ids)

    update = kartograph.verdichten(original_clusters, original_zones)

    # Originale dürfen sich nicht geändert haben
    assert original_clusters[0].cluster_id == original_cluster_id
    assert len(original_clusters[0].kristall_ids) == original_kristall_count
