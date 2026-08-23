# 📜 ÄNDERUNGSANTRAG `DIGITAL-TWIN-SEM-1.0.0` FÜR `CONTRACTS.md`

## 1. ERWEITERUNG DER ENUMS (§10)

Wir benötigen drei neue Enum-Werte, um den Twin, die Divergenz und die Kalibrierung semantisch sauber vom normalen Forschungsbetrieb zu trennen.

```python
class NodeType(str, Enum):
    HYPOTHESIS = "HYPOTHESIS"
    CRYSTAL = "CRYSTAL"
    FRONTIER_ANCHOR = "FRONTIER_ANCHOR"
    ZONE_ANCHOR = "ZONE_ANCHOR"
    DIMENSION_REF = "DIMENSION_REF"
    DIGITAL_TWIN = "DIGITAL_TWIN"  # ← NEU: Der digitale Zwilling als Modell-Knoten

class EvidenceKind(str, Enum):
    CONFIRMATION = "CONFIRMATION"
    CONTRADICTION = "CONTRADICTION"
    EXPLORATORY_COVERAGE = "EXPLORATORY_COVERAGE"
    DIAGNOSTIC_CLARIFICATION = "DIAGNOSTIC_CLARIFICATION"
    NEGATIVE_KNOWLEDGE = "NEGATIVE_KNOWLEDGE"
    POLICY_BLOCK = "POLICY_BLOCK"
    TWIN_DIVERGENCE = "TWIN_DIVERGENCE"  # ← NEU: Sim-vs-Real-Abweichung

class DiagnosticOutcomeType(str, Enum):
    CONFIRMS_CONTRADICTION = "CONFIRMS_CONTRADICTION"
    EXPLAINS_CONTRADICTION = "EXPLAINS_CONTRADICTION"
    RESOLVES_CONTRADICTION = "RESOLVES_CONTRADICTION"
    INCONCLUSIVE = "INCONCLUSIVE"
    TWIN_DRIFT_CONFIRMED = "TWIN_DRIFT_CONFIRMED"  # ← NEU: Twin weicht von der Realität ab
    TWIN_CALIBRATED = "TWIN_CALIBRATED"            # ← NEU: Twin wurde neu kalibriert
```

---

## 2. NEUE VERTRÄGE (§6.10.19 & §6.10.20)

### §6.10.19 `DigitalTwinModel`
Dies ist die Payload für einen `AtlasNode` mit `node_type = DIGITAL_TWIN`. Sie beschreibt den Zustand des Zwillings, seine Parameter und seinen Drift.

```python
class DigitalTwinModel(BaseModel):
    twin_model_id: str
    display_name: str
    domain: str
    
    # Das eigentliche Modell-Artefakt (z.B. eine ONNX-Datei, ein PyTorch-Checkpoint 
    # oder ein Satz physikalischer Gleichungen im Archiv)
    model_artifact_ref: str
    model_version: str
    
    # Schema, das Questor an HAL übergibt, um die Simulation zu parametrisieren
    parameter_schema_ref: Optional[str] = None
    
    # Kalibrierung
    calibration_method: Optional[str] = None
    last_calibration_at: Optional[str] = None
    calibration_history: list[str] = []  # Referenzen auf vergangene Kalibrierungs-Pakete
    
    # Drift & Validity
    divergence_threshold: float = 0.10   # Ab wann gilt der Twin als "drifted"? (0.0-1.0)
    drift_score: float = 0.0             # 0.0 = perfekt kalibriert, 1.0 = maximaler Drift
    validity: Optional[ValidityWindow] = None
    
    created_at: str
    updated_at: str
```

### §6.10.20 `TwinDivergenceReport`
Dieser Bericht wird **ausschließlich vom Kartographen** erzeugt, wenn ein Sim-Kristall und ein Real-Kristall verglichen werden. Er ist die Grundlage für den Kalibrierungs-Loop.

```python
class TwinDivergenceReport(BaseModel):
    divergence_id: str
    twin_node_ref: str
    sim_kristall_ref: str      # Referenz auf den Kristallkandidaten mit evidence_class = SIMULATION
    real_kristall_ref: str     # Referenz auf den Kristallkandidaten mit evidence_class = PHYSICAL_EXPERIMENT
    
    # Abweichung pro Metrik im metric_vector (z.B. {"yield": 0.15, "purity": 0.02})
    metric_deviations: dict[str, float] = {}
    
    # Aggregierte Abweichung (deterministisch berechnet vom Kartographen)
    overall_divergence_score: float  # 0.0-1.0
    
    tolerance_breached: bool
    calibration_required: bool
    
    created_at: str
```

---

## 3. ERWEITERUNG BESTEHENDER VERTRÄGE

### §1.1 `ResearchPackage`
Questor muss wissen, *welches* Twin-Modell er in der Simulation laden soll. Dieses Feld ist Pass-Through (wie `atlas_expectation_ref`).

```python
class ResearchPackage(BaseModel):
    # ... bestehende Felder ...
    
    # ── DIGITAL-TWIN-SEM-1.0.0: Neues optionales Feld ──
    digital_twin_ref: Optional[str] = None
```

### §6.10.3 `ReproducibilityContext`
Damit jeder Kristallkandidat nachvollziehbar macht, mit welchem Twin-Modell er erzeugt wurde.

```python
class ReproducibilityContext(BaseModel):
    # ... bestehende Felder ...
    
    # ── DIGITAL-TWIN-SEM-1.0.0: Neue optionale Felder ──
    digital_twin_ref: Optional[str] = None
    twin_model_version: Optional[str] = None
```

### §6.10.8 `AtlasNode`
Der Twin-Knoten braucht eine direkte Verbindung zu seiner Modell-Payload.

```python
class AtlasNode(BaseModel):
    # ... bestehende Felder ...
    
    # ── DIGITAL-TWIN-SEM-1.0.0: Neues optionales Feld ──
    twin_model: Optional[DigitalTwinModel] = None
```

### §6.10.11 `DiagnosticResolution`
Der Kalibrierungs-Loop wird als `DiagnosticResolution` abgebildet.

```python
class DiagnosticResolution(BaseModel):
    # ... bestehende Felder ...
    
    # ── DIGITAL-TWIN-SEM-1.0.0: Neues optionales Feld ──
    twin_divergence_report_ref: Optional[str] = None
```

---

## 4. SEMANTIK-REGELN FÜR DEN DIGITALEN ZWILLING

Diese Regeln müssen in `CONTRACTS.md` (und später in `GREMIUM.md`) als bindende Bestimmungen aufgenommen werden:

### Regel 1: Sim-Kristall vs. Real-Kristall
| Typ | `evidence_class` | Erlaubte `node_type`-Aktualisierung |
|---|---|---|
| **Sim-Kristall** | `SIMULATION` oder `SANDBOX` | Darf **nur** `DIGITAL_TWIN`-Knoten aktualisieren. Darf **niemals** einen `CRYSTAL`-Knoten erzeugen. |
| **Real-Kristall** | `PHYSICAL_EXPERIMENT` | Darf `CRYSTAL`, `HYPOTHESIS` und `DIGITAL_TWIN`-Knoten aktualisieren. |
| **Kalibrierungs-Kristall** | `COMPUTE_EVALUATION` | Darf **nur** `DIGITAL_TWIN`-Knoten aktualisieren (neue Parameter, `drift_score` senken). |

### Regel 2: Divergenz-Berechnung (Deterministisch)
Der Kartograph berechnet den `TwinDivergenceReport`, wenn er zwei Kristallkandidaten mit demselben `objective_family_ref` und demselben `digital_twin_ref` empfängt:
1. Extrahiere `metric_vector` aus Sim-Kristall und Real-Kristall.
2. Berechne pro Metrik die relative Abweichung: `dev = abs(sim - real) / max(abs(real), epsilon)`.
3. `overall_divergence_score = mean(dev)` über alle gemeinsamen Metriken.
4. Wenn `overall_divergence_score > twin_model.divergence_threshold`:
   - Setze `tolerance_breached = true`
   - Setze `calibration_required = true`
   - Erhöhe den `drift_score` des Twin-Knotens.

### Regel 3: Kalibrierungs-Loop als `DIAGNOSE`-Workflow
1. Wenn `calibration_required = true`, erzeugt die `FrontierEngine` einen `FrontierCandidate` mit:
   - `frontier_type = DIAGNOSTIC_FRONTIER`
   - `suggested_objective_type = DIAGNOSE`
   - `suggested_gate_mode = FRACTURE_DIAGNOSIS`
   - `digital_twin_ref = twin_node_ref`
2. Der Quartiermeister baut ein `ResearchPackage` mit:
   - `objective_type = DIAGNOSE`
   - `digital_twin_ref = twin_node_ref`
   - `security_mode = SANDBOX` oder `DEV_SANDBOX_ONLY` (Kalibrierung ist Compute, keine Physik!)
3. Questor führt den Kalibrierungs-Lauf aus (z.B. Gradient Descent auf die Twin-Parameter) und liefert einen `Kalibrierungs-Kristall` mit `evidence_class = COMPUTE_EVALUATION`.
4. Der Kartograph aktualisiert den `DIGITAL_TWIN`-Knoten:
   - `model_version` wird erhöht.
   - `drift_score` wird zurückgesetzt (oder reduziert).
   - `last_calibration_at` wird aktualisiert.
   - `DiagnosticResolution.outcome = TWIN_CALIBRATED`.

### Regel 4: Validity-Regeln
- Ein `DIGITAL_TWIN`-Knoten mit `drift_score > divergence_threshold` wird vom Kartographen als `DEGRADED` markiert.
- Ein `DIGITAL_TWIN`-Knoten in `quarantine_mode` darf **nicht** für normale `EXPLORE`- oder `OPTIMIZE`-Pakete verwendet werden, sondern nur für `DIAGNOSE` (Kalibrierung).
- Wenn `validity.valid_until` abgelaufen ist, wird der Twin automatisch als `DEGRADED` markiert und erfordert eine Re-Kalibrierung.