"""Atlas-Builder-Hilfsfunktionen für den Kartographen."""

from typing import Any
import numpy as np

from src.contracts.atlas_models import WissensKristall, DimensionSchema


def extract_coordinate_matrix(
    crystals: list[WissensKristall],
    dimension_schema: DimensionSchema | None = None,
) -> tuple[np.ndarray, list[str], list[str]]:
    """Extrahiert eine Koordinaten-Matrix aus Kristallen.
    
    Returns:
        Tuple aus (Matrix, kristall_ids, dimension_names)
    """
    if not crystals:
        return np.array([]), [], []

    # Alle Dimensionen sammeln
    all_dims = set()
    for crystal in crystals:
        all_dims.update(crystal.koordinaten.keys())

    dimension_names = sorted(all_dims)
    kristall_ids = [c.kristall_id for c in crystals]

    # Matrix aufbauen
    rows = []
    for crystal in crystals:
        row = []
        for dim in dimension_names:
            if dim in crystal.koordinaten:
                # UNKNOWN-Dimensionen als NaN markieren
                status = crystal.dimension_status.get(dim)
                if status and str(status) == "UNKNOWN":
                    row.append(np.nan)
                else:
                    row.append(crystal.koordinaten[dim])
            else:
                row.append(np.nan)
        rows.append(row)

    return np.array(rows), kristall_ids, dimension_names


def detect_outliers(crystals: list[WissensKristall], sigma_threshold: float = 2.0) -> list[str]:
    """Erkennt Ausreißer >2σ in den Kristall-Koordinaten.
    
    Args:
        crystals: Liste der WissensKristalle
        sigma_threshold: Schwellwert für Standardabweichungen (default: 2.0)
    
    Returns:
        Liste der kristall_ids von Ausreißern
    """
    if len(crystals) < 3:
        return []

    matrix, kristall_ids, _ = extract_coordinate_matrix(crystals)

    if matrix.size == 0:
        return []

    # Mittelwert und Std pro Dimension berechnen (ignoriert NaN)
    mean = np.nanmean(matrix, axis=0)
    std = np.nanstd(matrix, axis=0)

    # Ausreißer erkennen
    outlier_ids = []
    for i, crystal in enumerate(crystals):
        row = matrix[i]
        # Prüfen ob irgendeine Dimension ein Ausreißer ist
        if np.any(std > 0):
            z_scores = np.abs((row - mean) / std)
            if np.any(z_scores > sigma_threshold):
                outlier_ids.append(crystal.kristall_id)

    return outlier_ids


def calculate_silhouette(crystals: list[WissensKristall]) -> float | None:
    """Berechnet den Silhouette-Score für die Kristall-Cluster.
    
    Args:
        crystals: Liste der WissensKristalle
    
    Returns:
        Silhouette-Score in [-1, 1] oder None bei zu wenigen Kristallen
    """
    try:
        from sklearn.cluster import KMeans
        from sklearn.metrics import silhouette_score
    except ImportError:
        return None

    if len(crystals) < 2:
        return None

    matrix, _, _ = extract_coordinate_matrix(crystals)

    if matrix.size == 0 or len(crystals) < 2:
        return None

    # NaN durch Median ersetzen für Silhouette-Berechnung
    nan_mask = np.isnan(matrix)
    if np.any(nan_mask):
        col_medians = np.nanmedian(matrix, axis=0)
        matrix = np.where(nan_mask, col_medians, matrix)

    # Einfaches Clustering mit k=2 für Silhouette
    n_clusters = min(2, len(crystals))
    if n_clusters < 2:
        return None

    try:
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=1)
        labels = kmeans.fit_predict(matrix)
        score = silhouette_score(matrix, labels)
        return float(score)
    except Exception:
        return None


def calculate_r_squared(crystals: list[WissensKristall]) -> float | None:
    """Berechnet R² (Bestimmtheitsmaß) für die Kristall-Koordinaten.
    
    Args:
        crystals: Liste der WissensKristalle
    
    Returns:
        R²-Wert in [0, 1] oder None bei zu wenigen Kristallen
    """
    if len(crystals) < 3:
        return None

    matrix, _, _ = extract_coordinate_matrix(crystals)

    if matrix.size == 0 or len(crystals) < 3:
        return None

    # Einfache lineare Regression zwischen ersten zwei Dimensionen
    if matrix.shape[1] < 2:
        return None

    # NaN entfernen
    valid_mask = ~np.any(np.isnan(matrix[:, :2]), axis=1)
    x = matrix[valid_mask, 0]
    y = matrix[valid_mask, 1]

    if len(x) < 3:
        return None

    # Lineare Regression
    try:
        coeffs = np.polyfit(x, y, 1)
        y_pred = np.polyval(coeffs, x)
        
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        
        if ss_tot == 0:
            return 1.0
        
        r2 = 1 - (ss_res / ss_tot)
        return float(max(0.0, min(1.0, r2)))
    except Exception:
        return None


def normalize_coordinates(
    coords: dict[str, float],
    schema: DimensionSchema | None,
) -> dict[str, float]:
    """Normalisiert Koordinaten gemäß Schema.
    
    Args:
        coords: Koordinaten-Dictionary
        schema: Dimension-Schema oder None
    
    Returns:
        Normalisierte Koordinaten
    """
    if not schema:
        return coords.copy()

    result = {}
    for dim, value in coords.items():
        if dim not in schema.dimensions:
            # Dimension nicht im Schema → überspringen oder unverändert übernehmen
            result[dim] = value
            continue

        spec = schema.dimensions[dim]
        
        if spec.normalization_policy.value == "MIN_MAX":
            if spec.range_min is not None and spec.range_max is not None:
                range_size = spec.range_max - spec.range_min
                if range_size > 0:
                    result[dim] = (value - spec.range_min) / range_size
                else:
                    result[dim] = 0.5
            else:
                result[dim] = value
        elif spec.normalization_policy.value == "Z_SCORE":
            # Z-Score benötigt Statistik über alle Daten → hier vereinfacht
            result[dim] = value  # Placeholder
        else:
            result[dim] = value

    return result
