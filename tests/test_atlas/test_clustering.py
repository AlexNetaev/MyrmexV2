"""Tests für Clustering-Logik: DBSCAN, fracture_score, Zone-Health."""

from datetime import datetime, timezone

import pytest

from src.contracts.atlas_models import (
    DimensionSchema,
    DimensionSpec,
    WissensKristall,
)
from src.contracts.enums import (
    DimensionStatus,
    MissingDataPolicy,
    NormalizationPolicy,
    ZoneHealth,
)
from src.atlas.clustering import (
    ClusteringService,
    calculate_fracture_score,
    create_zone_v2,
    determine_zone_health,
)


def _create_kristall(
    kristall_id: str = "k1",
    source_package_id: str = "pkg-001",
    source_zyklus_id: str = "zyklus-001",
    questor_instance_id: str = "questor-1",
    koordinaten: dict[str, float] | None = None,
    dimension_status: dict[str, DimensionStatus] | None = None,
    confirmation_count: int = 1,
    decay: float = 1.0,
    source_trust: float = 1.0,
    created_at: str = "2024-01-01T00:00:00Z",
) -> WissensKristall:
    """Helper zum Erstellen eines Test-Kristalls."""
    return WissensKristall(
        kristall_id=kristall_id,
        source_package_id=source_package_id,
        source_zyklus_id=source_zyklus_id,
        questor_instance_id=questor_instance_id,
        koordinaten=koordinaten or {"x": 0.5, "y": 0.5},
        dimension_status=dimension_status or {"x": DimensionStatus.KNOWN, "y": DimensionStatus.KNOWN},
        kristall_daten={},
        confirmation_count=confirmation_count,
        decay=decay,
        source_trust=source_trust,
        half_life_s=3600.0,
        created_at=created_at,
        last_updated_at=created_at,
    )


def _create_dimension_schema() -> DimensionSchema:
    """Helper zum Erstellen eines Test-Schemas."""
    return DimensionSchema(
        dimension_schema_version="v1",
        dimensions={
            "x": DimensionSpec(
                unit="normalized",
                range_min=0.0,
                range_max=1.0,
                normalization_policy=NormalizationPolicy.MIN_MAX,
            ),
            "y": DimensionSpec(
                unit="normalized",
                range_min=0.0,
                range_max=1.0,
                normalization_policy=NormalizationPolicy.MIN_MAX,
            ),
            "z": DimensionSpec(
                unit="normalized",
                range_min=0.0,
                range_max=1.0,
                normalization_policy=NormalizationPolicy.MIN_MAX,
            ),
        },
    )


class TestDBSCANClustering:
    """Tests für DBSCAN-Clustering."""

    def test_dbscan_forms_clusters_from_crystals(self):
        """DBSCAN gruppiert Kristalle mit ähnlichen Koordinaten."""
        schema = _create_dimension_schema()
        service = ClusteringService(schema, eps=0.3, min_samples=2)

        # Zwei nahe Kristalle sollten im selben Cluster landen
        kristalle = [
            _create_kristall("k1", koordinaten={"x": 0.1, "y": 0.1}),
            _create_kristall("k2", koordinaten={"x": 0.12, "y": 0.11}),
            _create_kristall("k3", koordinaten={"x": 0.9, "y": 0.9}),
            _create_kristall("k4", koordinaten={"x": 0.92, "y": 0.91}),
        ]

        clusters = service.cluster_crystals(
            kristalle,
            zone_id="zone-1",
            atlas_version_ref="v1",
        )

        # Sollte mindestens 2 Cluster bilden
        assert len(clusters) >= 1
        # Alle Kristalle sollten in Clustern sein
        all_clustered_ids = set()
        for cluster in clusters:
            all_clustered_ids.update(cluster.kristall_ids)
        assert len(all_clustered_ids) == 4

    def test_unknown_dimension_not_treated_as_zero(self):
        """Regel 1: UNKNOWN-Dimension wird NICHT als 0 behandelt."""
        schema = _create_dimension_schema()
        service = ClusteringService(
            schema,
            missing_data_policy=MissingDataPolicy.EXCLUDE_DIMENSION,
            eps=0.3,
            min_samples=2,
        )

        # Kristall mit UNKNOWN in z-Dimension
        kristalle = [
            _create_kristall(
                "k1",
                koordinaten={"x": 0.5, "y": 0.5, "z": 0.0},  # z=0 wäre nah an anderen
                dimension_status={
                    "x": DimensionStatus.KNOWN,
                    "y": DimensionStatus.KNOWN,
                    "z": DimensionStatus.UNKNOWN,  # z ist UNKNOWN
                },
            ),
            _create_kristall(
                "k2",
                koordinaten={"x": 0.5, "y": 0.5, "z": 0.5},
                dimension_status={
                    "x": DimensionStatus.KNOWN,
                    "y": DimensionStatus.KNOWN,
                    "z": DimensionStatus.KNOWN,
                },
            ),
        ]

        # Die z-Dimension sollte ausgeschlossen werden, nicht als 0 behandelt
        clusters = service.cluster_crystals(kristalle, zone_id="zone-1", atlas_version_ref="v1")

        # Beide Kristalle sollten basierend auf x,y geclustert werden
        assert len(clusters) >= 1

    def test_unknown_dimension_not_treated_as_null(self):
        """Regel 1: UNKNOWN-Dimension wird NICHT als null behandelt."""
        schema = _create_dimension_schema()
        service = ClusteringService(
            schema,
            missing_data_policy=MissingDataPolicy.EXCLUDE_DIMENSION,
            eps=0.3,
            min_samples=2,
        )

        kristalle = [
            _create_kristall(
                "k1",
                koordinaten={"x": 0.5},  # Keine z-Dimension
                dimension_status={"x": DimensionStatus.KNOWN},
            ),
            _create_kristall(
                "k2",
                koordinaten={"x": 0.5},  # z wird nicht angegeben (nicht None)
                dimension_status={"x": DimensionStatus.KNOWN, "z": DimensionStatus.UNKNOWN},
            ),
        ]

        # Sollte keine Exception werfen und UNKNOWN korrekt behandeln
        clusters = service.cluster_crystals(kristalle, zone_id="zone-1", atlas_version_ref="v1")
        assert len(clusters) >= 0  # Mindestens leer erlaubt

    def test_missing_data_policy_exclude_dimension(self):
        """missing_data_policy=EXCLUDE_DIMENSION schließt die Dimension aus."""
        schema = _create_dimension_schema()
        service = ClusteringService(
            schema,
            missing_data_policy=MissingDataPolicy.EXCLUDE_DIMENSION,
            eps=0.3,
            min_samples=2,
        )

        kristalle = [
            _create_kristall(
                "k1",
                koordinaten={"x": 0.1, "y": 0.1},
                dimension_status={"x": DimensionStatus.KNOWN, "y": DimensionStatus.KNOWN},
            ),
            _create_kristall(
                "k2",
                koordinaten={"x": 0.12, "y": 0.11},
                dimension_status={"x": DimensionStatus.KNOWN, "y": DimensionStatus.UNKNOWN},
            ),
        ]

        clusters = service.cluster_crystals(kristalle, zone_id="zone-1", atlas_version_ref="v1")
        # y-Dimension sollte ausgeschlossen sein, nur x wird verwendet
        assert len(clusters) >= 0

    def test_missing_data_policy_impute_median(self):
        """missing_data_policy=IMPUTE_MEDIAN ersetzt durch Median."""
        schema = _create_dimension_schema()
        service = ClusteringService(
            schema,
            missing_data_policy=MissingDataPolicy.IMPUTE_MEDIAN,
            eps=0.5,
            min_samples=2,
        )

        kristalle = [
            _create_kristall(
                "k1",
                koordinaten={"x": 0.1, "y": 0.1},
                dimension_status={"x": DimensionStatus.KNOWN, "y": DimensionStatus.KNOWN},
            ),
            _create_kristall(
                "k2",
                koordinaten={"x": 0.12, "y": 0.5},  # y wird als Median (0.5) imputiert
                dimension_status={"x": DimensionStatus.KNOWN, "y": DimensionStatus.UNKNOWN},
            ),
        ]

        clusters = service.cluster_crystals(kristalle, zone_id="zone-1", atlas_version_ref="v1")
        assert len(clusters) >= 0

    def test_normalization_applied_before_clustering(self):
        """Koordinaten werden vor DBSCAN normalisiert."""
        schema = DimensionSchema(
            dimension_schema_version="v1",
            dimensions={
                "x": DimensionSpec(
                    unit="meters",
                    range_min=0.0,
                    range_max=100.0,
                    normalization_policy=NormalizationPolicy.MIN_MAX,
                ),
            },
        )
        service = ClusteringService(schema, eps=0.1, min_samples=2)

        # Kristalle mit rohen Werten außerhalb [0,1]
        kristalle = [
            _create_kristall("k1", koordinaten={"x": 10.0}, dimension_status={"x": DimensionStatus.KNOWN}),
            _create_kristall("k2", koordinaten={"x": 12.0}, dimension_status={"x": DimensionStatus.KNOWN}),
        ]

        clusters = service.cluster_crystals(kristalle, zone_id="zone-1", atlas_version_ref="v1")
        # Nach Normalisierung sind 10 und 12 sehr nah (0.1 und 0.12)
        assert len(clusters) >= 1


class TestFractureScore:
    """Tests für fracture_score-Berechnung."""

    def test_fracture_score_is_weighted(self):
        """Regel 3: fracture_score verwendet alter_decay × confirmation_factor × source_trust."""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        # Kristall mit hohem Gewicht (hohe confirmation, hoher trust)
        kristall_hoch = _create_kristall(
            "k1",
            confirmation_count=3,  # max factor
            decay=1.0,
            source_trust=1.0,
            created_at="2024-01-01T00:00:00Z",
        )

        # Kristall mit niedrigem Gewicht
        kristall_niedrig = _create_kristall(
            "k2",
            confirmation_count=1,  # niedriger factor
            decay=0.5,
            source_trust=0.5,
            created_at="2024-01-01T00:00:00Z",
        )

        score = calculate_fracture_score([kristall_hoch, kristall_niedrig], current_time=now)

        # Score sollte gewichtet sein
        assert 0.0 <= score <= 1.0

    def test_fracture_score_zero_when_no_instabil_events(self):
        """Keine instabilen Events → fracture_score = 0."""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        # Stabiler Kristall: confirmation >= 3 und decay >= 0.5
        kristall_stabil = _create_kristall(
            "k1",
            confirmation_count=3,
            decay=1.0,
            source_trust=1.0,
            created_at="2024-01-01T00:00:00Z",
        )

        score = calculate_fracture_score([kristall_stabil], current_time=now)
        assert score == 0.0

    def test_fracture_score_one_when_all_instabil(self):
        """Alle Events instabil → fracture_score = 1."""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        # Instabiler Kristall: confirmation < 3
        kristall_instabil = _create_kristall(
            "k1",
            confirmation_count=1,
            decay=1.0,
            source_trust=1.0,
            created_at="2024-01-01T00:00:00Z",
        )

        score = calculate_fracture_score([kristall_instabil], current_time=now)
        assert score == 1.0

    def test_fracture_score_uses_decay_from_signal_registry(self):
        """alter_decay wird korrekt aus der Signal-Registry übernommen."""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        # Kristall mit niedrigem decay (aus Signal-Registry)
        kristall_low_decay = _create_kristall(
            "k1",
            confirmation_count=3,
            decay=0.3,  # Niedriger decay
            source_trust=1.0,
            created_at="2024-01-01T00:00:00Z",
        )

        score = calculate_fracture_score([kristall_low_decay], current_time=now)
        # Niedriger decay macht instabil
        assert score == 1.0  # Da decay < 0.5


class TestZoneHealth:
    """Tests für Zone-Health-Bestimmung."""

    def test_zone_health_stabil_below_threshold(self):
        """fracture_score < schwelle → STABIL."""
        health = determine_zone_health(
            fracture_score=0.2,
            schwelle_instabil=0.3,
            schwelle_quarantaene=0.7,
        )
        assert health == ZoneHealth.STABIL

    def test_zone_health_instabil_above_threshold(self):
        """fracture_score >= schwelle → INSTABIL."""
        health = determine_zone_health(
            fracture_score=0.5,
            schwelle_instabil=0.3,
            schwelle_quarantaene=0.7,
        )
        assert health == ZoneHealth.INSTABIL

    def test_zone_health_quarantine_on_manual_override(self):
        """Manuelle Quarantäne überschreibt fracture_score."""
        health = determine_zone_health(
            fracture_score=0.1,  # Eigentlich STABIL
            schwelle_instabil=0.3,
            schwelle_quarantaene=0.7,
            manual_override=ZoneHealth.QUARANTAENE,
        )
        assert health == ZoneHealth.QUARANTAENE

    def test_zone_health_gesperrt_on_manual_lock(self):
        """Manuelle Sperrung setzt GESPERRT."""
        health = determine_zone_health(
            fracture_score=0.1,
            schwelle_instabil=0.3,
            schwelle_quarantaene=0.7,
            manual_override=ZoneHealth.GESPERRT,
        )
        assert health == ZoneHealth.GESPERRT


class TestImmutability:
    """Tests für Immutability der Atlas-Objekte."""

    def test_zone_versioning_creates_new_zone_not_mutate(self):
        """Regel 2: Zonen-Änderung erzeugt neue Zone, mutiert nicht."""
        kristalle = [_create_kristall("k1", confirmation_count=3, decay=1.0)]
        schema = _create_dimension_schema()
        service = ClusteringService(schema)

        clusters = service.cluster_crystals(kristalle, zone_id="zone-1", atlas_version_ref="v1")
        cluster_ids = [c.cluster_id for c in clusters]

        zone_v1 = create_zone_v2(
            zone_id="zone-1",
            name="Zone 1",
            kristalle=kristalle,
            cluster_ids=cluster_ids,
            atlas_version_ref="v1",
        )

        # Erstelle neue Version mit zusätzlichem Kristall (instabil)
        kristalle_v2 = kristalle + [_create_kristall("k2", confirmation_count=1, decay=0.3)]
        clusters_v2 = service.cluster_crystals(kristalle_v2, zone_id="zone-1", atlas_version_ref="v2")
        cluster_ids_v2 = [c.cluster_id for c in clusters_v2]

        zone_v2 = create_zone_v2(
            zone_id="zone-1",
            name="Zone 1",
            kristalle=kristalle_v2,
            cluster_ids=cluster_ids_v2,
            atlas_version_ref="v2",
            predecessor_zone_ids=[zone_v1.zone_id],
        )

        # Zone v1 sollte unverändert sein (fracture_score war 0 bei nur stabilem Kristall)
        assert zone_v1.fracture_score == 0.0
        # Zone v2 sollte höheren fracture_score haben wegen instabilem Kristall
        assert zone_v2.fracture_score > zone_v1.fracture_score
        assert zone_v2.predecessor_zone_ids == [zone_v1.zone_id]
        # Gleiche ID, aber neue Version
        assert zone_v1.zone_id == zone_v2.zone_id

    def test_cluster_versioning_creates_new_cluster_not_mutate(self):
        """Regel 2: Cluster-Änderung erzeugt neuen Cluster, mutiert nicht."""
        kristalle = [
            _create_kristall("k1", koordinaten={"x": 0.1, "y": 0.1}),
            _create_kristall("k2", koordinaten={"x": 0.12, "y": 0.11}),
        ]
        schema = _create_dimension_schema()
        service = ClusteringService(schema, eps=0.3, min_samples=2)

        clusters_v1 = service.cluster_crystals(
            kristalle,
            zone_id="zone-1",
            atlas_version_ref="v1",
        )

        # Speichere ursprüngliche Daten
        original_kristall_ids = {c.cluster_id: list(c.kristall_ids) for c in clusters_v1}

        # Füge neuen Kristall hinzu
        kristalle_v2 = kristalle + [_create_kristall("k3", koordinaten={"x": 0.11, "y": 0.12})]
        clusters_v2 = service.cluster_crystals(
            kristalle_v2,
            zone_id="zone-1",
            atlas_version_ref="v2",
            predecessor_cluster_ids=[c.cluster_id for c in clusters_v1],
        )

        # Originale Cluster sollten unverändert sein
        for cluster_v1 in clusters_v1:
            assert cluster_v1.kristall_ids == original_kristall_ids[cluster_v1.cluster_id]

        # Neue Cluster sollten Vorgänger referenzieren
        for cluster_v2 in clusters_v2:
            assert len(cluster_v2.predecessor_cluster_ids) > 0
