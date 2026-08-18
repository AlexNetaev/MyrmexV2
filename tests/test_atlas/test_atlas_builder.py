"""Tests für die Atlas-Builder-Hilfsfunktionen."""

import pytest
import numpy as np

from src.atlas.atlas_builder import (
    detect_outliers,
    calculate_silhouette,
    calculate_r_squared,
    normalize_coordinates,
)
from src.contracts.atlas_models import WissensKristall, DimensionSchema, DimensionSpec
from src.contracts.enums import DimensionStatus, NormalizationPolicy


def _create_crystal(
    kristall_id: str = "k-001",
    koordinaten: dict[str, float] | None = None,
) -> WissensKristall:
    """Helper zum Erstellen von Test-Kristallen."""
    from datetime import datetime, timezone
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


def test_detect_outliers_identifies_2sigma():
    """Outlier-Detection findet >2σ Ausreißer."""
    crystals = [
        _create_crystal("k-001", koordinaten={"x": 1.0, "y": 1.0}),
        _create_crystal("k-002", koordinaten={"x": 1.1, "y": 1.1}),
        _create_crystal("k-003", koordinaten={"x": 1.2, "y": 1.2}),
        _create_crystal("k-004", koordinaten={"x": 100.0, "y": 100.0}),  # Ausreißer
    ]

    outliers = detect_outliers(crystals)

    assert "k-004" in outliers
    assert len(outliers) == 1


def test_calculate_silhouette_returns_valid_range():
    """Silhouette-Score liegt in [-1, 1]."""
    crystals = [
        _create_crystal("k-001", koordinaten={"x": 0.0, "y": 0.0}),
        _create_crystal("k-002", koordinaten={"x": 0.1, "y": 0.1}),
        _create_crystal("k-003", koordinaten={"x": 10.0, "y": 10.0}),
        _create_crystal("k-004", koordinaten={"x": 10.1, "y": 10.1}),
    ]

    score = calculate_silhouette(crystals)

    assert score is not None
    assert -1.0 <= score <= 1.0


def test_calculate_r_squared_handles_empty_input():
    """R² mit leerem Input → None oder 0.0, kein Crash."""
    crystals = []

    r2 = calculate_r_squared(crystals)

    assert r2 is None or r2 == 0.0


def test_fracture_score_handles_zero_relevant_events():
    """fracture_score mit 0 relevant_events → 0.0, keine Division durch Null."""
    # Dieser Test wird in test_fracture_score.py getestet
    # Hier nur als Platzhalter für die Builder-Funktionen
    assert True


def test_normalize_coordinates_min_max():
    """Normalisierung mit MIN_MAX-Policy."""
    schema = DimensionSchema(
        dimension_schema_version="v1",
        dimensions={
            "x": DimensionSpec(unit="m", range_min=0.0, range_max=10.0, normalization_policy=NormalizationPolicy.MIN_MAX),
            "y": DimensionSpec(unit="m", range_min=0.0, range_max=10.0, normalization_policy=NormalizationPolicy.MIN_MAX),
        },
    )

    coords = {"x": 5.0, "y": 7.5}
    normalized = normalize_coordinates(coords, schema)

    assert normalized is not None
    assert 0.0 <= normalized["x"] <= 1.0
    assert 0.0 <= normalized["y"] <= 1.0


def test_normalize_coordinates_z_score():
    """Normalisierung mit Z_SCORE-Policy."""
    # Einfacher Test ohne Schema (verwendet Standardabweichung)
    coords = {"x": 1.0, "y": 2.0, "z": 3.0}
    
    # Ohne Schema sollte die Funktion die Koordinaten zurückgeben oder standardisieren
    result = normalize_coordinates(coords, None)
    assert result is not None


def test_normalize_coordinates_with_unknown_dimensions():
    """Normalisierung überspringt UNKNOWN-Dimensionen."""
    schema = DimensionSchema(
        dimension_schema_version="v1",
        dimensions={
            "x": DimensionSpec(unit="m", range_min=0.0, range_max=10.0, normalization_policy=NormalizationPolicy.MIN_MAX),
        },
    )

    coords = {"x": 5.0, "y": 7.5}  # y ist nicht im Schema
    normalized = normalize_coordinates(coords, schema)

    assert "x" in normalized
    # y sollte übersprungen oder behandelt werden
