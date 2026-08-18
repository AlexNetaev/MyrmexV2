"""Tests für den Kartographen - Seed-Zonen (Regel 4)."""

import pytest
from datetime import datetime, timezone

from src.contracts.atlas_models import WissensKristall
from src.contracts.enums import DimensionStatus, ZoneHealth
from src.gremium.kartograph import Kartograph


def _create_crystal_with_unknown(
    kristall_id: str = "k-001",
    unknown_dims: list[str] | None = None,
) -> WissensKristall:
    """Helper zum Erstellen von Kristallen mit UNKNOWN-Dimensionen."""
    now = datetime.now(timezone.utc).isoformat()
    
    koordinaten = {"x": 1.0, "y": 2.0}
    dimension_status = {"x": DimensionStatus.KNOWN, "y": DimensionStatus.KNOWN}
    
    if unknown_dims:
        for dim in unknown_dims:
            koordinaten[dim] = 0.0  # Platzhalter
            dimension_status[dim] = DimensionStatus.UNKNOWN
    
    return WissensKristall(
        kristall_id=kristall_id,
        source_package_id="pkg-001",
        source_zyklus_id="zyklus-001",
        questor_instance_id="questor-test",
        koordinaten=koordinaten,
        dimension_status=dimension_status,
        kristall_daten={},
        confirmation_count=1,
        decay=1.0,
        source_trust=1.0,
        half_life_s=3600.0,
        created_at=now,
        last_updated_at=now,
    )


def test_seed_zone_created_at_three_unknown_crystals():
    """Regel 4: >= 3 Kristalle mit UNKNOWN → Seed-Zone."""
    kartograph = Kartograph()

    crystals = [
        _create_crystal_with_unknown("k-001", unknown_dims=["z"]),
        _create_crystal_with_unknown("k-002", unknown_dims=["z"]),
        _create_crystal_with_unknown("k-003", unknown_dims=["z"]),
    ]

    update = kartograph.strukturieren(crystals)

    assert update is not None
    # Mindestens eine Zone sollte als Seed-Zone markiert sein
    seed_zones = [z for z in update.new_zones if getattr(z, 'seed_zone', False)]
    assert len(seed_zones) >= 1


def test_seed_zone_not_created_below_three():
    """Regel 4: < 3 Kristalle mit UNKNOWN → keine Seed-Zone."""
    kartograph = Kartograph()

    crystals = [
        _create_crystal_with_unknown("k-001", unknown_dims=["z"]),
        _create_crystal_with_unknown("k-002", unknown_dims=["z"]),
    ]

    update = kartograph.strukturieren(crystals)

    assert update is not None
    # Keine Seed-Zone bei weniger als 3 UNKNOWN-Kristallen
    seed_zones = [z for z in update.new_zones if getattr(z, 'seed_zone', False)]
    assert len(seed_zones) == 0


def test_seed_zone_has_marker():
    """Seed-Zone hat seed_zone=true und zone_health=STABIL."""
    kartograph = Kartograph()

    crystals = [
        _create_crystal_with_unknown("k-001", unknown_dims=["z"]),
        _create_crystal_with_unknown("k-002", unknown_dims=["z"]),
        _create_crystal_with_unknown("k-003", unknown_dims=["z"]),
    ]

    update = kartograph.strukturieren(crystals)

    assert update is not None
    seed_zones = [z for z in update.new_zones if getattr(z, 'seed_zone', False)]
    
    assert len(seed_zones) >= 1
    for zone in seed_zones:
        assert zone.seed_zone is True
        assert zone.zone_health == ZoneHealth.STABIL
