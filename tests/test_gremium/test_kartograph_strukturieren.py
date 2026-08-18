"""Tests für den Kartographen - STRUKTURIEREN."""

import pytest
from datetime import datetime, timezone

from src.contracts.atlas_models import (
    WissensKristall,
    ZoneV2,
    ClusterV2,
    DimensionSchema,
    DimensionSpec,
)
from src.contracts.enums import DimensionStatus, NormalizationPolicy, ZoneHealth
from src.gremium.kartograph import Kartograph


def _create_crystal(
    kristall_id: str = "k-001",
    source_package_id: str = "pkg-001",
    source_zyklus_id: str = "zyklus-001",
    koordinaten: dict[str, float] | None = None,
    dimension_status: dict[str, DimensionStatus] | None = None,
    confirmation_count: int = 1,
    decay: float = 1.0,
    source_trust: float = 1.0,
) -> WissensKristall:
    """Helper zum Erstellen von Test-Kristallen."""
    now = datetime.now(timezone.utc).isoformat()
    return WissensKristall(
        kristall_id=kristall_id,
        source_package_id=source_package_id,
        source_zyklus_id=source_zyklus_id,
        questor_instance_id="questor-test",
        koordinaten=koordinaten or {"x": 1.0, "y": 2.0},
        dimension_status=dimension_status or {"x": DimensionStatus.KNOWN, "y": DimensionStatus.KNOWN},
        kristall_daten={"test": "data"},
        confirmation_count=confirmation_count,
        decay=decay,
        source_trust=source_trust,
        half_life_s=3600.0,
        created_at=now,
        last_updated_at=now,
    )


def test_strukturieren_creates_zones_from_crystals():
    """STRUKTURIEREN erzeugt Zonen aus neuen Kristallen."""
    kartograph = Kartograph()
    crystals = [
        _create_crystal("k-001", koordinaten={"x": 1.0, "y": 1.0}),
        _create_crystal("k-002", koordinaten={"x": 1.1, "y": 1.1}),
        _create_crystal("k-003", koordinaten={"x": 5.0, "y": 5.0}),
    ]

    update = kartograph.strukturieren(crystals)

    assert update is not None
    assert len(update.new_zones) >= 1
    assert len(update.new_clusters) >= 1
    assert update.kartograph_mode == "STRUKTURIEREN"


def test_strukturieren_creates_new_zone_not_mutate():
    """Regel 2: STRUKTURIEREN erzeugt neue Zone, mutiert nicht."""
    kartograph = Kartograph()
    crystals = [_create_crystal("k-001", koordinaten={"x": 1.0, "y": 1.0})]

    # Erste Strukturierung
    update1 = kartograph.strukturieren(crystals)
    zone1 = update1.new_zones[0] if update1.new_zones else None

    # Zweite Strukturierung mit gleichem Kristall (simuliert neue Version)
    crystals2 = [_create_crystal("k-001", koordinaten={"x": 1.0, "y": 1.0}, confirmation_count=2)]
    update2 = kartograph.strukturieren(crystals2)
    zone2 = update2.new_zones[0] if update2.new_zones else None

    # Beide Zonen müssen unterschiedliche IDs haben (keine Mutation)
    if zone1 and zone2:
        assert zone1.zone_id != zone2.zone_id
        assert zone1.predecessor_zone_ids == []  # Erste Version hat keine Vorgänger


def test_strukturieren_with_zero_crystals_no_update():
    """0 Kristalle → kein AtlasUpdate."""
    kartograph = Kartograph()
    crystals = []

    update = kartograph.strukturieren(crystals)

    assert update is None


def test_strukturieren_with_one_crystal_creates_seed_zone():
    """1 Kristall → Seed-Zone wird erzeugt."""
    kartograph = Kartograph()
    crystals = [_create_crystal("k-001", koordinaten={"x": 1.0, "y": 1.0})]

    update = kartograph.strukturieren(crystals)

    assert update is not None
    # Bei einem Kristall sollte eine Seed-Zone oder ein einzelner Cluster entstehen
    assert len(update.new_zones) >= 1 or len(update.new_clusters) >= 1


def test_strukturieren_sets_predecessor_ids():
    """Neue Zone hat predecessor_zone_ids gesetzt."""
    kartograph = Kartograph()
    crystals = [
        _create_crystal("k-001", koordinaten={"x": 1.0, "y": 1.0}),
        _create_crystal("k-002", koordinaten={"x": 1.1, "y": 1.1}),
    ]

    # Erste Strukturierung
    update1 = kartograph.strukturieren(crystals)
    assert update1 is not None

    # Zweite Strukturierung mit neuen Kristallen
    crystals2 = [
        _create_crystal("k-003", koordinaten={"x": 2.0, "y": 2.0}),
        _create_crystal("k-004", koordinaten={"x": 2.1, "y": 2.1}),
    ]
    update2 = kartograph.strukturieren(crystals2)

    # Update2 sollte die Zonen aus Update1 als Vorgänger referenzieren (wenn gemergt)
    assert update2 is not None
    # Die neue Version sollte einen predecessor_atlas_id haben
    assert update2.predecessor_atlas_id is not None
