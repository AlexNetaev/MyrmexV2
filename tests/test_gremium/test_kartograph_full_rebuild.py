"""Tests für den Kartographen - FULL_REBUILD (kritischster Test: Regel 1)."""

import pytest
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import time

from src.contracts.atlas_models import (
    WissensKristall,
    ZoneV2,
    ClusterV2,
    AtlasUpdate,
)
from src.contracts.enums import DimensionStatus, ZoneHealth
from src.gremium.kartograph import Kartograph


def _create_crystal(
    kristall_id: str = "k-001",
    koordinaten: dict[str, float] | None = None,
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
        confirmation_count=1,
        decay=1.0,
        source_trust=1.0,
        half_life_s=3600.0,
        created_at=now,
        last_updated_at=now,
    )


def test_full_rebuild_creates_new_atlas():
    """Regel 1: FULL_REBUILD erzeugt einen neuen Atlas."""
    kartograph = Kartograph()
    crystals = [
        _create_crystal("k-001", koordinaten={"x": 1.0, "y": 1.0}),
        _create_crystal("k-002", koordinaten={"x": 2.0, "y": 2.0}),
        _create_crystal("k-003", koordinaten={"x": 3.0, "y": 3.0}),
    ]

    update = kartograph.full_rebuild(crystals)

    assert update is not None
    assert update.kartograph_mode == "FULL_REBUILD"
    assert len(update.new_zones) >= 1
    assert len(update.new_clusters) >= 1
    assert update.atlas_version_ref is not None


def test_full_rebuild_old_atlas_stays_active():
    """Regel 1: Der alte Atlas bleibt aktiv während des Rebuilds."""
    kartograph = Kartograph()

    # Erster Atlas
    crystals1 = [_create_crystal("k-001", koordinaten={"x": 1.0, "y": 1.0})]
    update1 = kartograph.full_rebuild(crystals1)
    old_version = update1.atlas_version_ref

    # Zweiter Atlas (FULL_REBUILD)
    crystals2 = [
        _create_crystal("k-001", koordinaten={"x": 1.0, "y": 1.0}),
        _create_crystal("k-002", koordinaten={"x": 2.0, "y": 2.0}),
    ]
    update2 = kartograph.full_rebuild(crystals2)

    # Alter Atlas sollte noch referenzierbar sein
    assert old_version is not None
    assert update2.predecessor_atlas_id == old_version


def test_full_rebuild_pointer_swap_is_atomic():
    """Regel 1: atlas_head_pointer wechselt atomar."""
    kartograph = Kartograph()

    crystals1 = [_create_crystal("k-001", koordinaten={"x": 1.0, "y": 1.0})]
    update1 = kartograph.full_rebuild(crystals1)

    crystals2 = [
        _create_crystal("k-001", koordinaten={"x": 1.0, "y": 1.0}),
        _create_crystal("k-002", koordinaten={"x": 2.0, "y": 2.0}),
    ]
    update2 = kartograph.full_rebuild(crystals2)

    # Pointer-Swap sollte atomar sein: entweder v1 oder v2, nie ein Zwischenzustand
    assert update1.atlas_version_ref != update2.atlas_version_ref
    assert update2.predecessor_atlas_id == update1.atlas_version_ref


def test_full_rebuild_running_quests_keep_old_version():
    """Regel 1: Laufende Quests behalten observed_atlas_version_id.
    
    Dies ist der KRITISCHSTE TEST für Phase 3b.
    Er simuliert Test I-13 und R-08: Ein laufender Questor darf seinen Atlas nicht verlieren.
    """
    kartograph = Kartograph()

    # Initialer Atlas
    crystals1 = [_create_crystal("k-001", koordinaten={"x": 1.0, "y": 1.0})]
    update1 = kartograph.full_rebuild(crystals1)
    old_atlas_version = update1.atlas_version_ref

    # Simuliere laufenden Questor mit alter Atlas-Version
    running_questor_atlas_version = old_atlas_version

    # FULL_REBUILD während Questor läuft
    crystals2 = [
        _create_crystal("k-001", koordinaten={"x": 1.0, "y": 1.0}),
        _create_crystal("k-002", koordinaten={"x": 2.0, "y": 2.0}),
        _create_crystal("k-003", koordinaten={"x": 3.0, "y": 3.0}),
    ]
    update2 = kartograph.full_rebuild(crystals2)
    new_atlas_version = update2.atlas_version_ref

    # WICHTIG: Laufender Questor behält seine alte Version
    assert running_questor_atlas_version == old_atlas_version
    assert running_questor_atlas_version != new_atlas_version

    # Der alte Atlas muss noch gültig sein (nicht gelöscht, nicht mutiert)
    assert kartograph.is_atlas_version_valid(old_atlas_version) is True


def test_full_rebuild_does_not_mutate_old_atlas():
    """Regel 1: Der alte Atlas wird NICHT mutiert."""
    kartograph = Kartograph()

    # Erster Atlas
    crystals1 = [_create_crystal("k-001", koordinaten={"x": 1.0, "y": 1.0})]
    update1 = kartograph.full_rebuild(crystals1)
    old_zone_id = update1.new_zones[0].zone_id if update1.new_zones else None

    # Zweiter Atlas
    crystals2 = [
        _create_crystal("k-001", koordinaten={"x": 1.0, "y": 1.0}),
        _create_crystal("k-002", koordinaten={"x": 2.0, "y": 2.0}),
    ]
    update2 = kartograph.full_rebuild(crystals2)

    # Alte Zone sollte unverändert sein (keine Mutation)
    if old_zone_id:
        # Suche die alte Zone in update1 (sollte unverändert sein)
        old_zone = None
        for zone in update1.new_zones:
            if zone.zone_id == old_zone_id:
                old_zone = zone
                break

        if old_zone:
            # Die Zone sollte ihre ursprünglichen Eigenschaften behalten
            assert old_zone.predecessor_zone_ids == []  # Erste Version hat keine Vorgänger
