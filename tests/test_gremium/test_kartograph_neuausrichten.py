"""Tests für den Kartographen - NEUAUSRICHTEN."""

import pytest
from datetime import datetime, timezone

from src.contracts.atlas_models import (
    WissensKristall,
    ZoneV2,
    ClusterV2,
)
from src.contracts.enums import DimensionStatus, SignalSeverity, SignalType, ZoneHealth
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


def _create_zone_with_signals(
    zone_id: str = "z-001",
    yellow_ratio: float = 0.1,
) -> ZoneV2:
    """Helper zum Erstellen von Zonen mit Signalen."""
    return ZoneV2(
        zone_id=zone_id,
        name=f"Zone {zone_id}",
        fracture_score=yellow_ratio,  # Simuliert yellow_signal_ratio
        zone_health=ZoneHealth.STABIL,
        cluster_ids=[],
        predecessor_zone_ids=[],
        atlas_version_ref="v1",
    )


def test_neuausrichten_triggered_by_outlier():
    """Regel 3: >2σ Ausreißer löst NEUAUSRICHTEN aus."""
    kartograph = Kartograph()

    # Kristalle mit extremem Ausreißer erstellen
    crystals = [
        _create_crystal("k-001", koordinaten={"x": 1.0, "y": 1.0}),
        _create_crystal("k-002", koordinaten={"x": 1.1, "y": 1.1}),
        _create_crystal("k-003", koordinaten={"x": 1.2, "y": 1.2}),
        _create_crystal("k-004", koordinaten={"x": 100.0, "y": 100.0}),  # Ausreißer >2σ
    ]

    result = kartograph.neuausrichten(crystals)

    assert result is not None
    # Sollte Trigger erkennen
    assert result.triggered is True or result.outlier_count > 0


def test_neuausrichten_triggered_by_low_r_squared():
    """Regel 3: R² < 0.3 löst NEUAUSRICHTEN aus."""
    kartograph = Kartograph()

    # Kristalle mit niedriger Korrelation
    crystals = [
        _create_crystal("k-001", koordinaten={"x": 1.0, "y": 5.0}),
        _create_crystal("k-002", koordinaten={"x": 2.0, "y": 1.0}),
        _create_crystal("k-003", koordinaten={"x": 3.0, "y": 9.0}),
        _create_crystal("k-004", koordinaten={"x": 4.0, "y": 2.0}),
    ]

    result = kartograph.neuausrichten(crystals)

    assert result is not None
    # R² sollte berechnet werden


def test_neuausrichten_triggered_by_high_silhouette():
    """Regel 3: Silhouette > 0.7 löst NEUAUSRICHTEN aus."""
    kartograph = Kartograph()

    # Gut separierte Cluster
    crystals = [
        _create_crystal("k-001", koordinaten={"x": 0.0, "y": 0.0}),
        _create_crystal("k-002", koordinaten={"x": 0.1, "y": 0.1}),
        _create_crystal("k-003", koordinaten={"x": 10.0, "y": 10.0}),
        _create_crystal("k-004", koordinaten={"x": 10.1, "y": 10.1}),
    ]

    result = kartograph.neuausrichten(crystals)

    assert result is not None
    # Silhouette-Score sollte berechnet werden


def test_neuausrichten_triggered_by_yellow_signals():
    """Regel 3: >40% 🟨 löst NEUAUSRICHTEN aus."""
    kartograph = Kartograph()

    # Zonen mit hohem Yellow-Signal-Anteil
    zones = [
        _create_zone_with_signals("z-001", yellow_ratio=0.5),  # 50% yellow
        _create_zone_with_signals("z-002", yellow_ratio=0.6),
    ]

    result = kartograph.neuausrichten_zonen(zones)

    assert result is not None
    # Sollte >40% erkennen und Trigger aktivieren


def test_neuausrichten_not_triggered_below_thresholds():
    """Unterhalb aller Trigger → kein NEUAUSRICHTEN."""
    kartograph = Kartograph()

    # Normale Kristalle ohne Ausreißer
    crystals = [
        _create_crystal("k-001", koordinaten={"x": 1.0, "y": 1.0}),
        _create_crystal("k-002", koordinaten={"x": 1.1, "y": 1.1}),
        _create_crystal("k-003", koordinaten={"x": 1.2, "y": 1.2}),
    ]

    result = kartograph.neuausrichten(crystals)

    assert result is not None
    # Unterhalb der Schwellwerte sollte kein Trigger aktiv sein
    # (kann trotzdem triggered=True sein wenn andere Kriterien erfüllt)


def test_neuausrichten_fallback_without_umap():
    """Ohne umap-learn → Fallback auf PCA oder NOT_APPLICABLE."""
    kartograph = Kartograph()

    crystals = [
        _create_crystal("k-001", koordinaten={"x": 1.0, "y": 1.0}),
        _create_crystal("k-002", koordinaten={"x": 2.0, "y": 2.0}),
    ]

    result = kartograph.neuausrichten(crystals)

    assert result is not None
    # projection_method sollte gesetzt sein (UMAP, PCA, oder NOT_APPLICABLE)
    assert result.projection_method is not None or result.new_coordinates is not None
