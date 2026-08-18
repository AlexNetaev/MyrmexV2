"""Clustering-Logik für Atlas: DBSCAN, fracture_score, Zone-Health."""

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

import numpy as np
from sklearn.cluster import DBSCAN

from src.contracts.atlas_models import (
    ClusterV2,
    DimensionSchema,
    DimensionSpec,
    WissensKristall,
    ZoneV2,
)
from src.contracts.enums import (
    DimensionStatus,
    MissingDataPolicy,
    NormalizationPolicy,
    ZoneHealth,
)


class ClusteringService:
    """Service für DBSCAN-Clustering auf Kristall-Koordinaten."""

    def __init__(
        self,
        dimension_schema: DimensionSchema | None = None,
        missing_data_policy: MissingDataPolicy = MissingDataPolicy.EXCLUDE_DIMENSION,
        eps: float = 0.5,
        min_samples: int = 2,
    ):
        self.dimension_schema = dimension_schema
        self.missing_data_policy = missing_data_policy
        self.eps = eps
        self.min_samples = min_samples

    def _get_known_dimensions(
        self, kristalle: list[WissensKristall]
    ) -> list[str]:
        """Ermittle Dimensionen, die bei allen Kristallen KNOWN sind."""
        if not kristalle:
            return []

        all_dims = set(kristalle[0].koordinaten.keys())
        for kristall in kristalle[1:]:
            all_dims &= set(kristall.koordinaten.keys())

        known_dims = []
        for dim in all_dims:
            is_known_all = all(
                kristall.dimension_status.get(dim, DimensionStatus.UNKNOWN)
                == DimensionStatus.KNOWN
                for kristall in kristalle
            )
            if is_known_all:
                known_dims.append(dim)

        return sorted(known_dims)

    def _normalize_coordinate(
        self,
        value: float,
        dim: str,
        spec: DimensionSpec,
    ) -> float:
        """Normalisiere einen Koordinatenwert gemäß DimensionSpec."""
        if spec.normalization_policy == NormalizationPolicy.NONE:
            return value

        if spec.normalization_policy == NormalizationPolicy.MIN_MAX:
            if spec.range_min is None or spec.range_max is None:
                return value
            range_span = spec.range_max - spec.range_min
            if range_span == 0:
                return 0.0
            normalized = (value - spec.range_min) / range_span
            return max(0.0, min(1.0, normalized))

        if spec.normalization_policy == NormalizationPolicy.Z_SCORE:
            # Für Z-Score benötigen wir Mean/Std aus dem Schema oder defaults
            # Hier vereinfacht: Annahme range_min/max als ±3σ
            if spec.range_min is None or spec.range_max is None:
                return value
            mean = (spec.range_min + spec.range_max) / 2
            std = (spec.range_max - spec.range_min) / 6
            if std == 0:
                return 0.0
            return (value - mean) / std

        return value

    def _build_feature_matrix(
        self,
        kristalle: list[WissensKristall],
        dimensions: list[str],
    ) -> tuple[np.ndarray, dict[int, str]]:
        """Baue Feature-Matrix für DBSCAN.

        Returns:
            Tuple aus (Matrix, Mapping von Index zu Kristall-ID).
        """
        if not kristalle or not dimensions:
            return np.array([]).reshape(0, 0), {}

        matrix_rows = []
        index_to_kristall = {}

        for idx, kristall in enumerate(kristalle):
            row = []
            skip_kristall = False

            for dim in dimensions:
                if dim not in kristall.koordinaten:
                    skip_kristall = True
                    break

                status = kristall.dimension_status.get(dim, DimensionStatus.UNKNOWN)
                if status != DimensionStatus.KNOWN:
                    if self.missing_data_policy == MissingDataPolicy.SEPARATE_CLUSTER:
                        # Bei SEPARATE_CLUSTER: UNKNOWN wird als extrem weit entfernt markiert
                        row.append(float("inf"))
                    elif self.missing_data_policy == MissingDataPolicy.IMPUTE_MEDIAN:
                        # Median-Imputation: hier vereinfacht als 0.5
                        row.append(0.5)
                    else:  # EXCLUDE_DIMENSION
                        # Diese Dimension wird nicht verwendet (bereits gefiltert)
                        pass
                        continue

                else:
                    value = kristall.koordinaten[dim]
                    if self.dimension_schema and self.dimension_schema.dimensions:
                        spec = self.dimension_schema.dimensions.get(dim)
                        if spec:
                            value = self._normalize_coordinate(value, dim, spec)
                    row.append(value)

            if not skip_kristall and row:
                matrix_rows.append(row)
                index_to_kristall[len(matrix_rows) - 1] = kristall.kristall_id

        if not matrix_rows:
            return np.array([]).reshape(0, len(dimensions)), {}

        matrix = np.array(matrix_rows)
        # Ersetze inf durch einen großen Wert für DBSCAN
        matrix = np.where(np.isinf(matrix), 1e10, matrix)

        return matrix, index_to_kristall

    def cluster_crystals(
        self,
        kristalle: list[WissensKristall],
        zone_id: str | None = None,
        atlas_version_ref: str | None = None,
        predecessor_cluster_ids: list[str] | None = None,
    ) -> tuple[list[ClusterV2], list[ZoneV2]]:
        """Führe DBSCAN-Clustering auf Kristallen durch.

        Args:
            kristalle: Liste der Kristalle zum Clustern.
            zone_id: ID der Zone, der die Cluster angehören (optional).
            atlas_version_ref: Version des Atlas (optional).
            predecessor_cluster_ids: Vorgänger-Cluster für Versionierung.

        Returns:
            Tuple aus (Liste von ClusterV2, Liste von ZoneV2).
        """
        if not kristalle:
            return [], []

        # Default-Werte setzen falls nicht angegeben
        if zone_id is None:
            zone_id = f"zone-{len(kristalle)}"
        if atlas_version_ref is None:
            from datetime import datetime, timezone
            atlas_version_ref = f"v-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

        # Ermittle bekannte Dimensionen
        known_dims = self._get_known_dimensions(kristalle)

        # Falls SEPARATE_CLUSTER, behandle UNKNOWN separat
        unknown_kristalle = []
        known_kristalle = []

        if self.missing_data_policy == MissingDataPolicy.SEPARATE_CLUSTER:
            for k in kristalle:
                has_unknown = any(
                    k.dimension_status.get(d, DimensionStatus.UNKNOWN)
                    == DimensionStatus.UNKNOWN
                    for d in k.koordinaten.keys()
                )
                if has_unknown:
                    unknown_kristalle.append(k)
                else:
                    known_kristalle.append(k)
        else:
            known_kristalle = kristalle

        clusters: list[ClusterV2] = []

        # Cluster für bekannte Kristalle
        if known_kristalle and known_dims:
            matrix, idx_to_kid = self._build_feature_matrix(known_kristalle, known_dims)

            if matrix.size > 0 and matrix.shape[0] > 0:
                dbscan = DBSCAN(eps=self.eps, min_samples=self.min_samples)
                labels = dbscan.fit_predict(matrix)

                # Gruppiere Kristalle nach Label
                label_to_kristalle: dict[int, list[WissensKristall]] = {}
                for idx, label in enumerate(labels):
                    if label == -1:  # Noise
                        continue
                    if label not in label_to_kristalle:
                        label_to_kristalle[label] = []
                    kristall_id = idx_to_kid.get(idx)
                    if kristall_id:
                        kristall = next(
                            (k for k in known_kristalle if k.kristall_id == kristall_id),
                            None,
                        )
                        if kristall:
                            label_to_kristalle[label].append(kristall)

                # Erstelle Cluster-Objekte
                for label, kristalle_in_cluster in label_to_kristalle.items():
                    kristall_ids = [k.kristall_id for k in kristalle_in_cluster]
                    centroid = self._compute_centroid(kristalle_in_cluster, known_dims)

                    cluster = ClusterV2(
                        cluster_id=f"cluster-{zone_id}-{label}",
                        name=f"Cluster {label}",
                        zone_id=zone_id,
                        kristall_ids=kristall_ids,
                        centroid=centroid,
                        predecessor_cluster_ids=predecessor_cluster_ids or [],
                        atlas_version_ref=atlas_version_ref,
                    )
                    clusters.append(cluster)

        # Separate Cluster für UNKNOWN-Kristalle
        if unknown_kristalle and self.missing_data_policy == MissingDataPolicy.SEPARATE_CLUSTER:
            unknown_cluster = ClusterV2(
                cluster_id=f"cluster-{zone_id}-unknown",
                name="Unknown Dimension Cluster",
                zone_id=zone_id,
                kristall_ids=[k.kristall_id for k in unknown_kristalle],
                centroid={},
                predecessor_cluster_ids=predecessor_cluster_ids or [],
                atlas_version_ref=atlas_version_ref,
            )
            clusters.append(unknown_cluster)

        # Zone erstellen die alle Cluster enthält
        from src.contracts.atlas_models import ZoneV2
        from src.contracts.enums import ZoneHealth
        
        zone = ZoneV2(
            zone_id=zone_id,
            name=f"Zone {zone_id}",
            fracture_score=0.0,
            zone_health=ZoneHealth.STABIL,
            cluster_ids=[c.cluster_id for c in clusters],
            predecessor_zone_ids=[],
            atlas_version_ref=atlas_version_ref,
            seed_zone=False,
        )

        return clusters, [zone]

    def _compute_centroid(
        self,
        kristalle: list[WissensKristall],
        dimensions: list[str],
    ) -> dict[str, float]:
        """Berechne Centroid eines Clusters."""
        if not kristalle or not dimensions:
            return {}

        centroid = {}
        for dim in dimensions:
            values = [k.koordinaten.get(dim, 0.0) for k in kristalle if dim in k.koordinaten]
            if values:
                centroid[dim] = float(np.mean(values))

        return centroid


def calculate_fracture_score(
    kristalle: list[WissensKristall],
    current_time: datetime | None = None,
) -> float:
    """Berechne fracture_score für eine Zone basierend auf Kristallen.

    fracture_score = Summe(gewichteter instabil_events) / Summe(gewichteter relevant_events)
    gewicht = alter_decay × confirmation_factor × source_trust

    Args:
        kristalle: Liste der Kristalle in der Zone.
        current_time: Aktuelle Zeit für Alter-Berechnung.

    Returns:
        fracture_score zwischen 0.0 und 1.0.
    """
    if not kristalle:
        return 0.0

    if current_time is None:
        current_time = datetime.now(timezone.utc)

    weighted_instabil = 0.0
    weighted_relevant = 0.0

    for kristall in kristalle:
        # Alter in Sekunden
        created_at_str = kristall.created_at.replace("Z", "+00:00")
        created_at = datetime.fromisoformat(created_at_str)
        # Stelle sicher, dass beide timezone-aware sind
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        age_seconds = (current_time - created_at).total_seconds()
        age_seconds = max(0.0, age_seconds)

        # alter_decay aus der Signal-Registry (hier über decay-Feld)
        alter_decay = kristall.decay

        # confirmation_factor: steigt mit confirmation_count, max bei 3
        confirmation_factor = min(kristall.confirmation_count, 3) / 3.0

        # source_trust
        source_trust = kristall.source_trust

        # Gewicht
        weight = alter_decay * confirmation_factor * source_trust

        # Zähle als relevantes Event
        weighted_relevant += weight

        # Prüfe ob instabil (hier: niedrige confirmation oder hoher decay)
        is_instabil = kristall.confirmation_count < 3 or kristall.decay < 0.5

        if is_instabil:
            weighted_instabil += weight

    if weighted_relevant == 0:
        return 0.0

    score = weighted_instabil / weighted_relevant
    return min(1.0, max(0.0, score))


def determine_zone_health(
    fracture_score: float,
    schwelle_instabil: float = 0.3,
    schwelle_quarantaene: float = 0.7,
    manual_override: ZoneHealth | None = None,
) -> ZoneHealth:
    """Bestimme Zone-Health basierend auf fracture_score.

    Args:
        fracture_score: Berechneter fracture_score.
        schwelle_instabil: Schwelle für INSTABIL.
        schwelle_quarantaene: Schwelle für QUARANTAENE.
        manual_override: Manuelle Überschreibung.

    Returns:
        ZoneHealth-Wert.
    """
    # Manuelles Override hat höchste Priorität
    if manual_override is not None:
        return manual_override

    if fracture_score >= schwelle_quarantaene:
        return ZoneHealth.QUARANTAENE

    if fracture_score >= schwelle_instabil:
        return ZoneHealth.INSTABIL

    return ZoneHealth.STABIL


def create_zone_v2(
    zone_id: str,
    name: str,
    kristalle: list[WissensKristall],
    cluster_ids: list[str],
    atlas_version_ref: str,
    predecessor_zone_ids: list[str] | None = None,
    schwelle_instabil: float = 0.3,
    schwelle_quarantaene: float = 0.7,
    manual_override: ZoneHealth | None = None,
) -> ZoneV2:
    """Erstelle eine ZoneV2 mit berechnetem fracture_score und zone_health.

    Args:
        zone_id: ID der Zone.
        name: Name der Zone.
        kristalle: Kristalle in der Zone.
        cluster_ids: IDs der zugehörigen Cluster.
        atlas_version_ref: Atlas-Version.
        predecessor_zone_ids: Vorgänger-Zonen für Versionierung.
        schwelle_instabil: Schwelle für INSTABIL.
        schwelle_quarantaene: Schwelle für QUARANTAENE.
        manual_override: Manuelle Überschreibung.

    Returns:
        ZoneV2-Objekt.
    """
    fracture_score = calculate_fracture_score(kristalle)
    zone_health = determine_zone_health(
        fracture_score,
        schwelle_instabil,
        schwelle_quarantaene,
        manual_override,
    )

    return ZoneV2(
        zone_id=zone_id,
        name=name,
        fracture_score=fracture_score,
        zone_health=zone_health,
        cluster_ids=cluster_ids,
        predecessor_zone_ids=predecessor_zone_ids or [],
        atlas_version_ref=atlas_version_ref,
        manual_override=manual_override,
    )
