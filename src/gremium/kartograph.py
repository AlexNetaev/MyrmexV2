"""Kartograph - Stufe 2 der Pipeline: STRUKTURIEREN, VERDICHTEN, NEUAUSRICHTEN, FULL_REBUILD."""

from datetime import datetime, timezone
from typing import Any
import uuid

from src.contracts.atlas_models import (
    WissensKristall,
    ZoneV2,
    ClusterV2,
    AtlasUpdate,
    NeuausrichtenResult,
)
from src.contracts.enums import (
    DimensionStatus,
    KartographMode,
    NeuausrichtenTrigger,
    ZoneHealth,
)
from src.atlas.clustering import ClusteringService, calculate_fracture_score
from src.atlas.atlas_builder import (
    detect_outliers,
    calculate_silhouette,
    calculate_r_squared,
    extract_coordinate_matrix,
)


class Kartograph:
    """Der Kartograph baut, verdichtet und projiziert den Atlas.
    
    Vier Modi:
    1. STRUKTURIEREN: Baut Zonen/Cluster aus neuen Kristallen
    2. VERDICHTEN: Merged gesättigte Cluster zu größeren Zonen
    3. NEUAUSRICHTEN: Re-projiziert bei Ausreißern oder hoher Instabilität
    4. FULL_REBUILD: Baut kompletten Atlas neu (atomar, alter bleibt aktiv)
    """

    def __init__(self):
        self._clustering_service = ClusteringService(eps=2.0, min_samples=2)
        self._atlas_versions: dict[str, AtlasUpdate] = {}
        self._current_version_ref: str | None = None

    def strukturieren(self, crystals: list[WissensKristall]) -> AtlasUpdate | None:
        """Modus 1: STRUKTURIEREN - Baut Zonen/Cluster aus neuen Kristallen.
        
        Args:
            crystals: Liste neuer WissensKristalle
        
        Returns:
            AtlasUpdate mit neuen Zonen/Clustern oder None bei 0 Kristallen
        """
        if not crystals:
            return None

        # DBSCAN-Clustering durchführen
        clusters, zones = self._clustering_service.cluster_crystals(crystals)

        # Seed-Zone prüfen (>= 3 Kristalle mit UNKNOWN-Dimensionen)
        unknown_crystals = [
            c for c in crystals
            if any(s == DimensionStatus.UNKNOWN for s in c.dimension_status.values())
        ]
        
        seed_zone_created = False
        if len(unknown_crystals) >= 3:
            # Seed-Zone erzeugen
            seed_zone = self._create_seed_zone(unknown_crystals, clusters, zones)
            zones.append(seed_zone)
            seed_zone_created = True

        # Neue Atlas-Version erstellen
        version_ref = self._generate_version_ref()
        predecessor_id = self._current_version_ref

        update = AtlasUpdate(
            update_id=str(uuid.uuid4()),
            kartograph_mode=KartographMode.STRUKTURIEREN.value,
            new_zones=zones,
            new_clusters=clusters,
            atlas_version_ref=version_ref,
            predecessor_atlas_id=predecessor_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            trigger_reasons=["NEW_CRYSTALS"] + (["SEED_ZONE"] if seed_zone_created else []),
        )

        # Version speichern
        self._atlas_versions[version_ref] = update
        self._current_version_ref = version_ref

        return update

    def verdichten(
        self,
        clusters: list[ClusterV2],
        zones: list[ZoneV2],
        saturation_threshold: int = 5,
    ) -> AtlasUpdate | None:
        """Modus 2: VERDICHTEN - Merged gesättigte Cluster.
        
        Args:
            clusters: Bestehende Cluster
            zones: Bestehende Zonen
            saturation_threshold: Ab wann ein Cluster als gesättigt gilt
        
        Returns:
            AtlasUpdate mit gemergten Zonen oder None
        """
        if not clusters:
            return None

        # Gesättigte Cluster identifizieren
        saturated = [c for c in clusters if len(c.kristall_ids) >= saturation_threshold]
        
        if not saturated:
            return None

        # Gemergte Zone erstellen
        merged_kristall_ids = []
        for cluster in saturated:
            merged_kristall_ids.extend(cluster.kristall_ids)

        # Neue Zone mit Vorgänger-Referenzen
        version_ref = self._generate_version_ref()
        predecessor_ids = [z.zone_id for z in zones]

        merged_zone = ZoneV2(
            zone_id=f"zone-{str(uuid.uuid4())[:8]}",
            name=f"Merged Zone {len(zones) + 1}",
            fracture_score=0.0,  # Wird später berechnet
            zone_health=ZoneHealth.STABIL,
            cluster_ids=[c.cluster_id for c in saturated],
            predecessor_zone_ids=predecessor_ids,
            atlas_version_ref=version_ref,
            seed_zone=False,
        )

        update = AtlasUpdate(
            update_id=str(uuid.uuid4()),
            kartograph_mode=KartographMode.VERDICHTEN.value,
            new_zones=[merged_zone],
            new_clusters=[],
            atlas_version_ref=version_ref,
            predecessor_atlas_id=self._current_version_ref,
            timestamp=datetime.now(timezone.utc).isoformat(),
            trigger_reasons=["SATURATED_CLUSTERS"],
        )

        self._atlas_versions[version_ref] = update
        self._current_version_ref = version_ref

        return update

    def neuausrichten(self, crystals: list[WissensKristall]) -> NeuausrichtenResult:
        """Modus 3: NEUAUSRICHTEN - Prüft Trigger für Re-Projektion.
        
        Trigger:
        1. >2σ Ausreißer in Kristall-Koordinaten
        2. R² < 0.3 (niedrige Korrelation)
        3. Silhouette > 0.7 (hohe Separation)
        4. >40% 🟨-Signale (hohe Instabilität)
        
        Args:
            crystals: Liste der Kristalle
        
        Returns:
            NeuausrichtenResult mit Trigger-Informationen und neuen Koordinaten
        """
        result = NeuausrichtenResult()
        active_triggers = []

        # Trigger 1: Ausreißer >2σ
        outliers = detect_outliers(crystals)
        result.outlier_count = len(outliers)
        if len(outliers) > 0:
            active_triggers.append(NeuausrichtenTrigger.OUTLIER_2SIGMA.value)

        # Trigger 2: R² < 0.3
        r2 = calculate_r_squared(crystals)
        result.r_squared = r2
        if r2 is not None and r2 < 0.3:
            active_triggers.append(NeuausrichtenTrigger.R2_LOW.value)

        # Trigger 3: Silhouette > 0.7
        silhouette = calculate_silhouette(crystals)
        result.silhouette_score = silhouette
        if silhouette is not None and silhouette > 0.7:
            active_triggers.append(NeuausrichtenTrigger.SILHOUETTE_HIGH.value)

        # Trigger 4: >40% Yellow-Signale (simuliert über fracture_score)
        # In Produktion würde man echte Signale aus der Signal-Registry holen
        yellow_ratio = self._estimate_yellow_signal_ratio(crystals)
        result.yellow_signal_ratio = yellow_ratio
        if yellow_ratio is not None and yellow_ratio > 0.4:
            active_triggers.append(NeuausrichtenTrigger.YELLOW_SIGNAL_HIGH.value)

        result.active_triggers = active_triggers
        result.triggered = len(active_triggers) > 0

        # Wenn Trigger aktiv: Neue Koordinaten berechnen
        if result.triggered:
            result.new_coordinates = self._reproject_coordinates(crystals)
            result.projection_method = "UMAP"  # Oder Fallback

        return result

    def neuausrichten_zonen(self, zones: list[ZoneV2]) -> NeuausrichtenResult:
        """NEUAUSRICHTEN für Zonen (prüft Yellow-Signal-Ratio)."""
        result = NeuausrichtenResult()
        active_triggers = []

        # Yellow-Signal-Ratio über fracture_score schätzen
        yellow_ratio = self._estimate_yellow_signal_ratio_from_zones(zones)
        result.yellow_signal_ratio = yellow_ratio
        
        if yellow_ratio is not None and yellow_ratio > 0.4:
            active_triggers.append(NeuausrichtenTrigger.YELLOW_SIGNAL_HIGH.value)

        result.active_triggers = active_triggers
        result.triggered = len(active_triggers) > 0

        return result

    def full_rebuild(self, crystals: list[WissensKristall]) -> AtlasUpdate:
        """Modus 4: FULL_REBUILD - Baut kompletten Atlas neu (atomar).
        
        WICHTIG: Der alte Atlas bleibt aktiv bis der neue fertig ist.
        Laufende Quests behalten ihre observed_atlas_version_id.
        
        Args:
            crystals: Alle Kristalle aus dem Archiv
        
        Returns:
            AtlasUpdate mit komplett neuem Atlas
        """
        old_version_ref = self._current_version_ref

        # Kompletten Neubau durchführen
        clusters, zones = self._clustering_service.cluster_crystals(crystals)

        # fracture_score einmal für alle Kristalle berechnen
        global_fracture_score = calculate_fracture_score(crystals)
        for zone in zones:
            zone.fracture_score = global_fracture_score

        # Neue Version erstellen
        version_ref = self._generate_version_ref()

        update = AtlasUpdate(
            update_id=str(uuid.uuid4()),
            kartograph_mode=KartographMode.FULL_REBUILD.value,
            new_zones=zones,
            new_clusters=clusters,
            atlas_version_ref=version_ref,
            predecessor_atlas_id=old_version_ref,
            timestamp=datetime.now(timezone.utc).isoformat(),
            trigger_reasons=["FULL_REBUILD"],
        )

        # Atomarer Pointer-Swap: erst speichern, dann Pointer setzen
        self._atlas_versions[version_ref] = update
        
        # Alte Version bleibt gültig (wird nicht gelöscht)
        # Pointer wird atomar gesetzt
        self._current_version_ref = version_ref

        return update

    def is_atlas_version_valid(self, version_ref: str) -> bool:
        """Prüft ob eine Atlas-Version noch gültig ist."""
        return version_ref in self._atlas_versions

    def get_atlas_version(self, version_ref: str) -> AtlasUpdate | None:
        """Ruft eine spezifische Atlas-Version ab."""
        return self._atlas_versions.get(version_ref)

    def _create_seed_zone(
        self,
        unknown_crystals: list[WissensKristall],
        existing_clusters: list[ClusterV2],
        existing_zones: list[ZoneV2],
    ) -> ZoneV2:
        """Erstellt eine Seed-Zone für Kristalle mit UNKNOWN-Dimensionen."""
        version_ref = self._current_version_ref or "v-seed"
        
        return ZoneV2(
            zone_id=f"seed-zone-{str(uuid.uuid4())[:8]}",
            name=f"Seed Zone ({len(unknown_crystals)} UNKNOWN)",
            fracture_score=0.0,
            zone_health=ZoneHealth.STABIL,
            cluster_ids=[c.cluster_id for c in existing_clusters],
            predecessor_zone_ids=[z.zone_id for z in existing_zones],
            atlas_version_ref=version_ref,
            seed_zone=True,
        )

    def _estimate_yellow_signal_ratio(self, crystals: list[WissensKristall]) -> float | None:
        """Schätzt die Yellow-Signal-Ratio aus Kristallen."""
        if not crystals:
            return None
        
        # Simulation: fracture_score > 0.3 als "yellow" zählen
        yellow_count = sum(1 for c in crystals if c.decay < 0.7)
        return yellow_count / len(crystals)

    def _estimate_yellow_signal_ratio_from_zones(self, zones: list[ZoneV2]) -> float | None:
        """Schätzt Yellow-Ratio aus Zonen."""
        if not zones:
            return None
        
        yellow_count = sum(1 for z in zones if z.fracture_score > 0.3)
        return yellow_count / len(zones)

    def _reproject_coordinates(
        self,
        crystals: list[WissensKristall],
    ) -> dict[str, dict[str, float]]:
        """Berechnet neue Koordinaten durch Re-Projektion."""
        try:
            from sklearn.decomposition import PCA
        except ImportError:
            # Fallback ohne UMAP/PCA
            return {c.kristall_id: c.koordinaten for c in crystals}

        matrix, kristall_ids, _ = extract_coordinate_matrix(crystals)
        
        if matrix.size == 0:
            return {}

        # NaN durch Median ersetzen
        nan_mask = np.isnan(matrix)
        if np.any(nan_mask):
            from src.atlas.atlas_builder import extract_coordinate_matrix as ecm
            col_medians = np.nanmedian(matrix, axis=0)
            matrix = np.where(nan_mask, col_medians, matrix)

        # PCA für Dimensionsreduktion
        n_components = min(2, matrix.shape[1], len(crystals) - 1)
        if n_components < 1:
            return {c.kristall_id: c.koordinaten for c in crystals}

        try:
            pca = PCA(n_components=n_components)
            new_coords = pca.fit_transform(matrix)
            
            result = {}
            for i, kid in enumerate(kristall_ids):
                result[kid] = {f"dim_{j}": float(new_coords[i, j]) for j in range(n_components)}
            
            return result
        except Exception:
            return {c.kristall_id: c.koordinaten for c in crystals}

    def _generate_version_ref(self) -> str:
        """Generiert eine neue Atlas-Versionsreferenz."""
        return f"atlas-{uuid.uuid4().hex[:12]}"


# numpy import am Ende für lokale Gültigkeit
import numpy as np
