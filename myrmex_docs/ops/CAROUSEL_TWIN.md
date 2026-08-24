# 📄 specs/CAROUSEL_TWIN.md — v1.0.0

---

| Feld | Wert |
|---|---|
| Dateiname | specs/CAROUSEL_TWIN.md |
| Version | 1.0.0 |
| Status | BINDEND nach Freigabe |
| System | MYRMEX v2.4.0 + Questor v0.2.3 + HAL v0.2.0 + Gremium Strategic Layer v1.0.2 |
| Schicht | Layer 1 (specs/) — referenziert foundation/ |
| Baut auf | CHARTER 1.0.0, CONTRACTS 1.2.1-twin.1, HAL.md 1.1.0-atlas-hyb.1, DIGITAL-TWIN-SEM-1.0.0 |
| Konfliktregel | CHARTER > CONTRACTS > HAL.md > dieses Dokument |
| Datum | 21. August 2026 |

---

## §0 Geltung und Änderungsregeln

Dieses Dokument definiert:
- Die Hardware-Spezifikation des Karussell-MVP (Schicht 0/1)
- Die HAL-Slot-Definitionen und Capabilities
- Das Digital-Twin-Modell (3-Schichten-Architektur)
- Das erste Experiment: Fluorescein-Photobleaching
- Die Integration in das MYRMEX-System

Regel: Dieses Dokument referenziert Verträge aus `CONTRACTS.md` und Sicherheitsregeln aus `CHARTER.md`.
Es definiert keine neuen Sicherheitsregeln.
Konfliktregel: Bei Widersprüchen gilt `CHARTER.md` > `CONTRACTS.md` > `HAL.md` > dieses Dokument.

---

## §1 Hardware-Übersicht

### §1.1 Systembeschreibung

Das Karussell-MVP ist ein 3D-gedrucktes Laborautomatisierungssystem mit:
- **1 rotierender Plattform** (Schrittmotor + Zahnkranz)
- **Einweg-Petrischalen** (Ø 35 mm, transparent, UV-durchlässig)
- **4 modularen Stationen** (an festen Positionen um das Karussell)
- **Keiner aktiven Heizung** (Raumtemperatur-Prozesse)
- **Keiner geschlossener Flüssigkeitsführung** (offene Petrischale)

### §1.2 Stationen-Übersicht

| Station | Position | Funktion | Aktorik | Sensorik |
|---|---|---|---|---|
| S1 | 0° | Probenzugabe | Peristaltische Pumpe | Volumen-Sensor (optional) |
| S2 | 90° | Mischen | Servo (Kipp-Mechanismus) | — |
| S3 | 180° | UV-Belichtung | UV-LED (365 nm) | Timer |
| S4 | 270° | Fluoreszenz-Messung | LED (488 nm) + Kamera | CMOS-Kamera + Filter |

### §1.3 Mechanische Parameter

| Parameter | Wert | Einheit |
|---|---|---|
| Karussell-Durchmesser | 200 | mm |
| Schalen-Durchmesser | 35 | mm |
| Schalen-Volumen (max) | 5 | mL |
| Rotationszeit (eine Position) | 3.0 | s |
| Rotationszeit (vollständige Umdrehung) | 12.0 | s |
| Positioniergenauigkeit | ±0.5 | mm |
| Kippwinkel (Mischen) | 15–30 | ° |
| Kippfrequenz (Mischen) | 0.5–2.0 | Hz |

### §1.4 Sicherheitsrelevante Aspekte

| Aspekt | Maßnahme | CHARTER-Referenz |
|---|---|---|
| UV-Strahlung (365 nm) | Geschlossenes Gehäuse mit Interlock-Schalter | SR-09 |
| Bewegliche Teile (Karussell) | Schrittmotor mit Endschalter | SR-09 |
| Chemikalien (Fluorescein, NaOH) | Einweg-Schale, keine Wiederverwendung | SR-10 |
| Elektrische Sicherheit | Niederspannung (12V/5V) | SR-09 |

---

## §2 HAL-Slot-Definitionen

### §2.1 EnvironmentManifest

```python
EnvironmentManifest(
    environment_id="carousel-v1",
    environment_version="1.0.0",
    schema_version="1.1.0-atlas-hyb.1",
    estop_mechanism="SOFTWARE",
    max_command_timeout_s=60.0,
    default_lease_ttl_s=300.0,
    heartbeat_interval_s=5.0,
    supported_security_modes=["NORMAL", "SANDBOX", "DEV_SANDBOX_ONLY", "RECOVERY"],
    supported_resource_classes=["LAB_ACTUATOR"],
    slots=[...],       # → §2.2
    mutex_zones=[...], # → §2.3
    capabilities=[...], # → §2.4
)
```

### §2.2 SlotDescriptors

#### S1: Probenzugabe (Dispense)

```python
SlotDescriptor(
    slot_id="carousel-dispense",
    display_name="Karussell Station 1: Probenzugabe",
    resource_class=ResourceClass.LAB_ACTUATOR,
    capabilities=["pump.dispense"],
    mutex_group="carousel-position",
    physical_zones=["carousel-zone-s1"],
    physical_actuation=True,
    compute_capable=False,
    sandbox_capable=False,
    requires_path_reservation=False,
    max_concurrent_commands=1,
    estop_controllable=True,
    max_command_timeout_s=60.0,
    max_process_duration_s=120.0,
    max_parameter_payload_bytes=4096,
    supported_process_modes=["START"],
)
```

#### S2: Mischen (Swirl)

```python
SlotDescriptor(
    slot_id="carousel-mix",
    display_name="Karussell Station 2: Mischen",
    resource_class=ResourceClass.LAB_ACTUATOR,
    capabilities=["carousel.swirl"],
    mutex_group="carousel-position",
    physical_zones=["carousel-zone-s2"],
    physical_actuation=True,
    compute_capable=False,
    sandbox_capable=False,
    requires_path_reservation=False,
    max_concurrent_commands=1,
    estop_controllable=True,
    max_command_timeout_s=120.0,
    max_process_duration_s=300.0,
    max_parameter_payload_bytes=4096,
    supported_process_modes=["START"],
)
```

#### S3: UV-Belichtung

```python
SlotDescriptor(
    slot_id="carousel-uv",
    display_name="Karussell Station 3: UV-Belichtung",
    resource_class=ResourceClass.LAB_ACTUATOR,
    capabilities=["uv.expose"],
    mutex_group="carousel-position",
    physical_zones=["carousel-zone-s3"],
    physical_actuation=True,
    compute_capable=False,
    sandbox_capable=False,
    requires_path_reservation=False,
    max_concurrent_commands=1,
    estop_controllable=True,
    max_command_timeout_s=3600.0,
    max_process_duration_s=3600.0,
    max_parameter_payload_bytes=4096,
    supported_process_modes=["START", "MONITOR", "ABORT"],
)
```

#### S4: Fluoreszenz-Messung

```python
SlotDescriptor(
    slot_id="carousel-fluorometer",
    display_name="Karussell Station 4: Fluoreszenz-Messung",
    resource_class=ResourceClass.LAB_ACTUATOR,
    capabilities=["fluorometer.measure", "camera.capture"],
    mutex_group="carousel-position",
    physical_zones=["carousel-zone-s4"],
    physical_actuation=False,  # Nur Messung, keine Aktorik
    compute_capable=False,
    sandbox_capable=False,
    requires_path_reservation=False,
    max_concurrent_commands=1,
    estop_controllable=True,
    max_command_timeout_s=30.0,
    max_process_duration_s=60.0,
    max_parameter_payload_bytes=4096,
    supported_process_modes=["START"],
)
```

### §2.3 MutexZone

```python
MutexZone(
    zone_id="carousel-rotation",
    slots=[
        "carousel-dispense",
        "carousel-mix",
        "carousel-uv",
        "carousel-fluorometer",
    ],
    lock_policy=LockPolicy.EXCLUSIVE,
)
```

**Regel:** Nur eine Station kann gleichzeitig aktiv sein. Das Karussell muss sich an der richtigen Position befinden, bevor eine Station aktiviert wird.

### §2.4 Capabilities

| Capability-ID | Station | Parameter | physical_actuation |
|---|---|---|---|
| `carousel.rotate` | Transport | `target_position: int` (0–3) | True |
| `pump.dispense` | S1 | `volume_ml: float`, `flow_rate_ml_min: float` | True |
| `carousel.swirl` | S2 | `duration_s: float`, `intensity: str` | True |
| `uv.expose` | S3 | `duration_s: float`, `intensity_percent: float` | True |
| `fluorometer.measure` | S4 | `excitation_nm: int`, `emission_nm: int`, `exposure_ms: int` | False |
| `camera.capture` | S4 | `exposure_ms: int`, `gain: float` | False |
| `carousel.discard` | Transport | — | True |

---

## §3 Capability-Definitionen (Questor-Registry)

### §3.1 `carousel.rotate`

```yaml
capability_id: carousel.rotate
version: "1.0"
schema_version: "1.0"
domain: general
display_name: "Karussell-Rotation"
description: "Dreht das Karussell zur Zielposition"
hal_capability_ref: carousel.rotate
parameter_schema:
  target_position:
    type: INTEGER
    required: true
    min: 0
    max: 3
    description: "Zielposition (0=S1, 1=S2, 2=S3, 3=S4)"
requires_physical_actuation: true
allowed_security_modes: [NORMAL, SANDBOX, DEV_SANDBOX_ONLY]
requires_lease: true
requires_dimension_approval: false
cost_estimate:
  time_cost_s: 3.0
  reagent_cost: 0.0
  compute_cost: 0.0
  energy_cost: 0.01
max_timeout_s: 15.0
max_concurrent_executions: 1
deprecated: false
```

### §3.2 `pump.dispense`

```yaml
capability_id: pump.dispense
version: "1.0"
schema_version: "1.0"
domain: chemie
display_name: "Peristaltische Pumpe: Dispensierung"
description: "Gibt Flüssigkeit in die Petrischale ab"
hal_capability_ref: pump.dispense
parameter_schema:
  volume_ml:
    type: FLOAT
    required: true
    min: 0.1
    max: 10.0
    unit: mL
    description: "Zielvolumen"
  flow_rate_ml_min:
    type: FLOAT
    required: true
    min: 0.1
    max: 5.0
    unit: mL/min
    description: "Flussrate"
requires_physical_actuation: true
allowed_security_modes: [NORMAL, SANDBOX, DEV_SANDBOX_ONLY]
requires_lease: true
requires_dimension_approval: false
cost_estimate:
  time_cost_s: 30.0
  reagent_cost: 0.05
  compute_cost: 0.0
  energy_cost: 0.01
max_timeout_s: 60.0
max_concurrent_executions: 1
deprecated: false
```

### §3.3 `carousel.swirl`

```yaml
capability_id: carousel.swirl
version: "1.0"
schema_version: "1.0"
domain: general
display_name: "Karussell: Schwenken/Mischen"
description: "Mischt die Probe durch Kippen der Petrischale"
hal_capability_ref: carousel.swirl
parameter_schema:
  duration_s:
    type: FLOAT
    required: true
    min: 5.0
    max: 300.0
    unit: s
    description: "Mischdauer"
  intensity:
    type: ENUM
    required: true
    values: [LOW, MEDIUM, HIGH]
    description: "Mischintensität"
requires_physical_actuation: true
allowed_security_modes: [NORMAL, SANDBOX, DEV_SANDBOX_ONLY]
requires_lease: true
requires_dimension_approval: false
cost_estimate:
  time_cost_s: 30.0
  reagent_cost: 0.0
  compute_cost: 0.0
  energy_cost: 0.01
max_timeout_s: 300.0
max_concurrent_executions: 1
deprecated: false
```

### §3.4 `uv.expose`

```yaml
capability_id: uv.expose
version: "1.0"
schema_version: "1.0"
domain: chemie
display_name: "UV-Belichtung (365 nm)"
description: "Belichtet die Probe mit UV-Licht"
hal_capability_ref: uv.expose
parameter_schema:
  duration_s:
    type: FLOAT
    required: true
    min: 10.0
    max: 3600.0
    unit: s
    description: "Belichtungsdauer"
  intensity_percent:
    type: FLOAT
    required: true
    min: 10.0
    max: 100.0
    unit: "%"
    description: "UV-Intensität"
requires_physical_actuation: true
allowed_security_modes: [NORMAL, SANDBOX, DEV_SANDBOX_ONLY]
requires_lease: true
requires_dimension_approval: false
cost_estimate:
  time_cost_s: 60.0
  reagent_cost: 0.0
  compute_cost: 0.0
  energy_cost: 0.05
max_timeout_s: 3600.0
max_concurrent_executions: 1
deprecated: false
```

### §3.5 `fluorometer.measure`

```yaml
capability_id: fluorometer.measure
version: "1.0"
schema_version: "1.0"
domain: physik
display_name: "Fluoreszenz-Messung"
description: "Misst die Fluoreszenz-Intensität der Probe"
hal_capability_ref: fluorometer.measure
parameter_schema:
  excitation_nm:
    type: INTEGER
    required: true
    min: 300
    max: 700
    unit: nm
    description: "Anregungswellenlänge"
  emission_nm:
    type: INTEGER
    required: true
    min: 350
    max: 800
    unit: nm
    description: "Emissionswelllänge"
  exposure_ms:
    type: INTEGER
    required: true
    min: 10
    max: 5000
    unit: ms
    description: "Belichtungszeit der Kamera"
requires_physical_actuation: false
allowed_security_modes: [NORMAL, SANDBOX, DEV_SANDBOX_ONLY]
requires_lease: true
requires_dimension_approval: false
cost_estimate:
  time_cost_s: 10.0
  reagent_cost: 0.0
  compute_cost: 0.01
  energy_cost: 0.01
max_timeout_s: 30.0
max_concurrent_executions: 1
deprecated: false
```

---

## §4 Digital-Twin-Modell

### §4.1 Architektur-Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│  SCHICHT 1: Discrete Event Simulation (DES)                 │
│  → Karussell-Rotation, Stations-Sequenzierung, Timing       │
│  → "WANN passiert WAS an WELCHER Station?"                  │
├─────────────────────────────────────────────────────────────┤
│  SCHICHT 2: Lumped-Parameter-Modelle (ODEs)                 │
│  → Photobleaching, Fluoreszenz, Pumpen, Mischen             │
│  → "WIE verändert sich die Probe an jeder Station?"         │
├─────────────────────────────────────────────────────────────┤
│  SCHICHT 3: Stochastische Rauschmodelle                     │
│  → Messrauschen, Pipettier-Ungenauigkeit, LED-Drift         │
│  → "WAS sieht der Sensor WIRKLICH?"                         │
└─────────────────────────────────────────────────────────────┘
```

### §4.2 DigitalTwinModel (CONTRACTS §6.10.19)

```python
DigitalTwinModel(
    twin_model_id="carousel-fluorescein-photobleaching-v1",
    display_name="Karussell v1 — Fluorescein-Photobleaching",
    domain="chemie",
    model_artifact_ref="data/twins/carousel_photobleaching_v1_sim.py",
    model_version="1.0.0",
    parameter_schema_ref="data/twins/carousel_photobleaching_v1_params.yaml",
    calibration_method="sim_vs_real_fluorescence_decay",
    last_calibration_at=None,  # Noch nicht kalibriert
    calibration_history=[],
    divergence_threshold=0.10,
    drift_score=0.0,
    validity=None,
    created_at="2026-08-21T00:00:00Z",
    updated_at="2026-08-21T00:00:00Z",
)
```

### §4.3 Schicht 1: DES — Karussell-Skelett

```python
class CarouselDES:
    """
    Discrete Event Simulation des Karussells.
    Modelliert: Rotationszeit, Stations-Sequenzierung, Prozessdauer.
    """
    ROTATION_TIME_S = 3.0
    STATION_COUNT = 4

    def simulate_cycle(self, protocol: list[StationAction]) -> CycleResult:
        """
        Simuliert einen vollständigen Messzyklus.
        protocol = [Dispense(...), Swirl(...), UV(...), Measure(...)]
        """
        total_time_s = 0.0
        sample_state = SampleState()

        for action in protocol:
            # Rotation zur Station
            total_time_s += self.ROTATION_TIME_S
            # Prozess an der Station
            station_result = action.execute(sample_state)
            sample_state.update(station_result)
            total_time_s += station_result.duration_s

        return CycleResult(
            total_time_s=total_time_s,
            final_state=sample_state,
        )
```

### §4.4 Schicht 2: ODEs — Photobleaching-Kinetik

```python
class PhotobleachingODE:
    """
    Lumped-Parameter-Modell für Fluorescein-Photobleaching.
    dF/dt = -k_bleach * I_uv * F
    → Exponentieller Zerfall der Fluoreszenz
    """

    # Kalibrierbare Parameter
    K_BLEACH = 1.2e-3       # s⁻¹ (pro UV-Einheit)
    QUANTUM_YIELD = 0.92    # Fluorescein
    EPSILON = 83000.0       # M⁻¹cm⁻¹ (Extinktionskoeffizient)
    PATH_LENGTH_CM = 0.3    # cm (Schalenhöhe)

    def simulate_bleaching(
        self,
        concentration_uM: float,
        uv_duration_s: float,
        uv_intensity_percent: float,
        ph: float,
    ) -> FluorescenceResult:
        """
        Berechnet die Fluoreszenz-Intensität nach UV-Belichtung.
        """
        # pH-abhängiger Extinktionskoeffizient
        # Fluorescein: pKa ≈ 6.4
        pKa = 6.4
        epsilon_eff = self.EPSILON / (1 + 10**(pKa - ph))

        # Initiale Fluoreszenz (vereinfacht)
        F0 = concentration_uM * 1e-6 * self.QUANTUM_YIELD * epsilon_eff * self.PATH_LENGTH_CM

        # Photobleaching-Rate
        I_uv = uv_intensity_percent / 100.0
        k = self.K_BLEACH * I_uv

        # Exponentieller Zerfall
        import math
        F_t = F0 * math.exp(-k * uv_duration_s)

        return FluorescenceResult(
            initial_fluorescence=F0,
            final_fluorescence=F_t,
            decay_fraction=1.0 - (F_t / F0) if F0 > 0 else 0.0,
        )

    def simulate_fluorescence_signal(
        self,
        concentration_uM: float,
        ph: float,
        excitation_nm: int = 488,
        emission_nm: int = 520,
    ) -> float:
        """
        Berechnet das erwartete Fluoreszenz-Signal (Photonenzählung).
        """
        pKa = 6.4
        epsilon_eff = self.EPSILON / (1 + 10**(pKa - ph))

        # Vereinfachtes Signal-Modell
        signal_photons = (
            concentration_uM * 1e-6
            * self.QUANTUM_YIELD
            * epsilon_eff
            * self.PATH_LENGTH_CM
            * 1e6  # Skalierung auf Photonenzählung
        )
        return signal_photons
```

### §4.5 Schicht 3: Rauschmodelle

```python
class CarouselNoiseModel:
    """
    Stochastische Rauschmodelle für den Karussell-Twin.
    """

    # Kalibrierbare Parameter
    CAMERA_READ_NOISE = 5.0       # e⁻ (RMS)
    CAMERA_DARK_CURRENT = 0.1     # e⁻/s
    PIPETTE_CV_PERCENT = 2.0      # % (Coefficient of Variation)
    LED_INTENSITY_DRIFT = 0.5     # % pro Stunde
    UV_INTENSITY_DRIFT = 1.0      # % pro Stunde

    def apply_camera_noise(self, signal_photons: float) -> float:
        """Poisson-Rauschen + Read-Noise + Dark Current."""
        import numpy as np
        poisson_noise = np.random.poisson(max(0, int(signal_photons)))
        read_noise = np.random.normal(0, self.CAMERA_READ_NOISE)
        return max(0, poisson_noise + read_noise)

    def apply_pipette_noise(self, volume_target_ml: float) -> float:
        """Normalverteilung für Pipettier-Ungenauigkeit."""
        import numpy as np
        sigma = self.PIPETTE_CV_PERCENT / 100.0 * volume_target_ml
        return np.random.normal(volume_target_ml, sigma)

    def apply_uv_drift(self, intensity_percent: float, elapsed_hours: float) -> float:
        """Langzeit-Drift der UV-LED."""
        import numpy as np
        drift = np.random.normal(0, self.UV_INTENSITY_DRIFT * elapsed_hours)
        return max(0, intensity_percent + drift)
```

### §4.6 Kalibrierbare Parameter (Übersicht)

| Parameter | Schicht | Bedeutung | Literaturwert | Kalibrierbar? |
|---|---|---|---|---|
| `K_BLEACH` | ODE | Photobleaching-Rate | ~10⁻³ s⁻¹ | ✅ |
| `QUANTUM_YIELD` | ODE | Quantenausbeute Fluorescein | 0.92 | ✅ |
| `EPSILON` | ODE | Extinktionskoeffizient | 83 000 M⁻¹cm⁻¹ | ✅ |
| `PATH_LENGTH_CM` | ODE | Optische Pfadlänge | 0.3 cm | ✅ |
| `CAMERA_READ_NOISE` | Rauschen | Kamera-Rauschen | ~5 e⁻ | ✅ |
| `PIPETTE_CV_PERCENT` | Rauschen | Pipettier-Ungenauigkeit | 2% CV | ✅ |
| `LED_INTENSITY_DRIFT` | Rauschen | LED-Drift | 0.5%/h | ✅ |
| `UV_INTENSITY_DRIFT` | Rauschen | UV-Drift | 1%/h | ✅ |
| `ROTATION_TIME_S` | DES | Rotationszeit | 3.0 s | ✅ |

---

## §5 Experiment: Fluorescein-Photobleaching

### §5.1 Chemischer Hintergrund

**Reaktion:** Fluorescein + UV (365 nm) → Photobleaching (irreversibel)

```
Fluorescein (fluoreszierend) + hν → Photoprodukte (nicht-fluoreszierend)
```

**Messgröße:** Fluoreszenz-Intensität bei 520 nm (Anregung 488 nm)
**Erwartung:** Exponentieller Abfall der Fluoreszenz mit UV-Dauer

### §5.2 Parameter-Raum (für Atlas/ML-Optimierung)

| Dimension | Typ | Bereich | Einheit | Beschreibung |
|---|---|---|---|---|
| `fluorescein_conc` | kontinuierlich | 1–50 | µM | Fluorescein-Konzentration |
| `uv_duration` | kontinuierlich | 10–600 | s | UV-Belichtungsdauer |
| `uv_intensity` | kontinuierlich | 10–100 | % | UV-Intensität |
| `ph_value` | kontinuierlich | 7–13 | pH | pH-Wert der Lösung |
| `measure_delay` | kontinuierlich | 0–300 | s | Verzögerung vor Messung |

### §5.3 ObjectiveFamily (für Atlas)

```python
ObjectiveFamily(
    objective_family_id="fluorescein-photobleaching-v1",
    name="Fluorescein Photobleaching Optimierung",
    metrics=[
        MetricDefinition(
            metric_id="fluorescence_decay_rate",
            display_name="Fluoreszenz-Zerfallsrate",
            direction=MetricDirection.MAXIMIZE,
            weight=0.6,
            tolerance=0.05,
            unit="fraction/s",
        ),
        MetricDefinition(
            metric_id="signal_to_noise",
            display_name="Signal-zu-Rausch-Verhältnis",
            direction=MetricDirection.MAXIMIZE,
            weight=0.4,
            tolerance=1.0,
            unit="dB",
        ),
    ],
    constraints=[
        MetricConstraint(
            metric_id="fluorescein_conc",
            operator=ConstraintOperator.LE,
            value=50.0,  # Nicht zu konzentriert (Inner-Filter-Effekt)
        ),
    ],
    priority_mode=PriorityMode.WEIGHTED_SUM,
)
```

### §5.4 Ablauf auf dem Karussell

```
ZYKLUS 1: Probenzugabe
  ├─ carousel.rotate(target_position=0)     # Zur Station S1
  ├─ pump.dispense(volume_ml=2.0, flow_rate_ml_min=1.0)
  │   → Fluorescein-Lösung (variable Konzentration)
  └─ pump.dispense(volume_ml=0.5, flow_rate_ml_min=0.5)
      → NaOH-Lösung (pH-Einstellung)

ZYKLUS 2: Mischen
  ├─ carousel.rotate(target_position=1)     # Zur Station S2
  └─ carousel.swirl(duration_s=15, intensity=MEDIUM)
      → Homogenisierung

ZYKLUS 3: UV-Belichtung
  ├─ carousel.rotate(target_position=2)     # Zur Station S3
  └─ uv.expose(duration_s=variable, intensity_percent=variable)
      → Photobleaching läuft ab

ZYKLUS 4: Fluoreszenz-Messung
  ├─ carousel.rotate(target_position=3)     # Zur Station S4
  └─ fluorometer.measure(excitation_nm=488, emission_nm=520, exposure_ms=100)
      → Fluoreszenz-Intensität wird gemessen

ZYKLUS 5: Entsorgung
  └─ carousel.discard()
      → Einweg-Schale wird verworfen
```

### §5.5 LoopTemplate (Questor)

```yaml
template_id: fluorescein_photobleaching_v1
template_version: "1.0"
schema_version: "1.0"
domain: chemie
created_by: SYSTEM_INTEGRATOR
created_at: "2026-08-21T00:00:00Z"
last_modified: "2026-08-21T00:00:00Z"
objective_types: [OPTIMIZE, EXPLORE, VALIDATE]
description: "Fluorescein-Photobleaching auf dem Karussell-MVP"
required_capabilities:
  - carousel.rotate
  - pump.dispense
  - carousel.swirl
  - uv.expose
  - fluorometer.measure
required_slot_count: 4
requires_physical_actuation: true
requires_long_running_process: false
is_recovery_template: false
steps:
  - step_id: rotate_to_dispense
    step_type: HAL_COMMAND
    capability: carousel.rotate
    operation: ROTATE_TO_POSITION
    parameters: {target_position: 0}
    timeout_s: 15.0
    cost: {time_cost_s: 3.0, reagent_cost: 0.0, compute_cost: 0.0, energy_cost: 0.01}

  - step_id: dispense_fluorescein
    step_type: HAL_COMMAND
    capability: pump.dispense
    operation: DISPENSE
    parameters:
      volume_ml: "{{fluorescein_volume_ml}}"
      flow_rate_ml_min: 1.0
    timeout_s: 60.0
    cost: {time_cost_s: 30.0, reagent_cost: 0.05, compute_cost: 0.0, energy_cost: 0.01}

  - step_id: rotate_to_mix
    step_type: HAL_COMMAND
    capability: carousel.rotate
    operation: ROTATE_TO_POSITION
    parameters: {target_position: 1}
    timeout_s: 15.0
    cost: {time_cost_s: 3.0, reagent_cost: 0.0, compute_cost: 0.0, energy_cost: 0.01}

  - step_id: swirl_mix
    step_type: HAL_COMMAND
    capability: carousel.swirl
    operation: SWIRL
    parameters:
      duration_s: 15.0
      intensity: MEDIUM
    timeout_s: 120.0
    cost: {time_cost_s: 15.0, reagent_cost: 0.0, compute_cost: 0.0, energy_cost: 0.01}

  - step_id: rotate_to_uv
    step_type: HAL_COMMAND
    capability: carousel.rotate
    operation: ROTATE_TO_POSITION
    parameters: {target_position: 2}
    timeout_s: 15.0
    cost: {time_cost_s: 3.0, reagent_cost: 0.0, compute_cost: 0.0, energy_cost: 0.01}

  - step_id: uv_expose
    step_type: HAL_COMMAND
    capability: uv.expose
    operation: EXPOSE
    parameters:
      duration_s: "{{uv_duration_s}}"
      intensity_percent: "{{uv_intensity_percent}}"
    timeout_s: 3600.0
    cost: {time_cost_s: 60.0, reagent_cost: 0.0, compute_cost: 0.0, energy_cost: 0.05}

  - step_id: rotate_to_measure
    step_type: HAL_COMMAND
    capability: carousel.rotate
    operation: ROTATE_TO_POSITION
    parameters: {target_position: 3}
    timeout_s: 15.0
    cost: {time_cost_s: 3.0, reagent_cost: 0.0, compute_cost: 0.0, energy_cost: 0.01}

  - step_id: measure_fluorescence
    step_type: HAL_COMMAND
    capability: fluorometer.measure
    operation: MEASURE
    parameters:
      excitation_nm: 488
      emission_nm: 520
      exposure_ms: 100
    timeout_s: 30.0
    cost: {time_cost_s: 10.0, reagent_cost: 0.0, compute_cost: 0.01, energy_cost: 0.01}

  - step_id: evaluate_result
    step_type: EVALUATE
    timeout_s: 5.0
    cost: {time_cost_s: 1.0, reagent_cost: 0.0, compute_cost: 0.0, energy_cost: 0.0}

max_internal_iterations: 1
termination_conditions:
  - condition_id: all_steps_completed
    metric: null
    operator: null
    threshold: null
on_step_failure: ABORT_LOOP
max_step_retries: 1
estimated_cost:
  total_time_s: 180.0
  total_reagent_cost: 0.05
  total_compute_cost: 0.01
  total_energy_cost: 0.12
```

---

## §6 Atlas-Zonen (Initial)

### §6.1 Zonen-Definition

| Zone-ID | Beschreibung | Dimensionen | Initialzustand |
|---|---|---|---|
| `conc-low` | Niedrige Konzentration (1–10 µM) | `fluorescein_conc` | UNEXPLORED |
| `conc-mid` | Mittlere Konzentration (10–30 µM) | `fluorescein_conc` | UNEXPLORED |
| `conc-high` | Hohe Konzentration (30–50 µM) | `fluorescein_conc` | UNEXPLORED |
| `uv-short` | Kurze UV-Belichtung (10–60 s) | `uv_duration` | UNEXPLORED |
| `uv-mid` | Mittlere UV-Belichtung (60–300 s) | `uv_duration` | UNEXPLORED |
| `uv-long` | Lange UV-Belichtung (300–600 s) | `uv_duration` | UNEXPLORED |

### §6.2 FrontierEngine-Trigger

Nach jedem Experiment wird die FrontierEngine aktualisiert:
- Weißraum-Zonen → `WEISSRAUM`-Frontier
- Zonen mit hohem `uncertainty_score` → `DEEP_UNCERTAIN`-Frontier
- Zonen mit niedrigem `fracture_score` und hoher `support_confidence` → `LOW_COST_FRONTIER`

---

## §7 Sicherheitsregeln (Karussell-spezifisch)

| # | Regel | CHARTER-Referenz |
|---|---|---|
| K-01 | UV-Belichtung nur bei geschlossenem Gehäuse (Interlock) | SR-09 |
| K-02 | Karussell-Stop bei geöffnetem Gehäuse | SR-09 |
| K-03 | Keine UV-Belichtung > 3600 s ohne menschliche Freigabe | SR-11 |
| K-04 | NaOH-Konzentration ≤ 0.1 M (Sicherheitsgrenze) | SR-10 |
| K-05 | Einweg-Schale wird nach jedem Experiment verworfen | SR-10 |
| K-06 | Fluorescein-Konzentration ≤ 50 µM (Inner-Filter-Effekt) | SR-10 |
| K-07 | ESTOP stoppt Karussell UND UV-LED sofort | SR-09 |
| K-08 | Keine physische Ausführung in SANDBOX-Modus | SR-35 |

---

## §8 Dummy-HAL-Konfiguration

### §8.1 Simulationsverhalten

Für Tests ohne echte Hardware (SANDBOX / DEV_SANDBOX_ONLY):

```python
class CarouselDummyHAL:
    """
    Dummy-HAL für das Karussell-MVP.
    Simuliert alle Stationen deterministisch.
    """

    def execute_command(self, command: HALCommand) -> HALCommandResult:
        if command.capability == "carousel.rotate":
            return self._simulate_rotation(command)
        elif command.capability == "pump.dispense":
            return self._simulate_dispense(command)
        elif command.capability == "carousel.swirl":
            return self._simulate_swirl(command)
        elif command.capability == "uv.expose":
            return self._simulate_uv(command)
        elif command.capability == "fluorometer.measure":
            return self._simulate_measurement(command)
        else:
            return HALCommandResult(
                command_id=command.command_id,
                status="ERROR",
                error_code="UNKNOWN_CAPABILITY",
                error_class="OPERATIONAL",
            )

    def _simulate_measurement(self, command: HALCommand) -> HALCommandResult:
        """
        Simuliert eine Fluoreszenz-Messung.
        Verwendet das Twin-Modell für die Signalberechnung.
        """
        # Twin-Modell aufrufen
        twin = PhotobleachingODE()
        signal = twin.simulate_fluorescence_signal(
            concentration_uM=self._current_concentration,
            ph=self._current_ph,
        )
        # Rauschen anwenden
        noise = CarouselNoiseModel()
        noisy_signal = noise.apply_camera_noise(signal)

        return HALCommandResult(
            command_id=command.command_id,
            status="SUCCESS",
            slot_state=SlotState(slot_id="carousel-fluorometer", status="FREE", ...),
            operational_metrics={"fluorescence_photons": noisy_signal},
        )
```

### §8.2 Simulierbare Fehlermodi

Der Dummy-HAL muss folgende Fehler simulieren können:
- `COMMAND_TIMEOUT` (UV-Belichtung dauert zu lange)
- `SLOT_UNAVAILABLE` (Station ist besetzt)
- `PARAMETER_INVALID` (Volumen außerhalb Bounds)
- `ESTOP` (Not-Aus)

---

## §9 Implementierungsphasen

| Phase | Aufgabe | Dauer | Abhängigkeit |
|---|---|---|---|
| C-1 | HAL-Slots + MutexZone definieren | 1 Tag | CONTRACTS §3 |
| C-2 | Capability-Registry (7 Capabilities) | 1 Tag | C-1 |
| C-3 | Dummy-HAL implementieren | 2 Tage | C-1, C-2 |
| C-4 | Twin-Modell (ODE + Rauschen) | 2 Tage | C-1 |
| C-5 | LoopTemplate (fluorescein_photobleaching_v1) | 1 Tag | C-2 |
| C-6 | End-to-End-Test (SANDBOX) | 2 Tage | C-3, C-4, C-5 |
| C-7 | Erste echte Messung (Station S4) | 1 Tag | C-6, Hardware |
| **Gesamt** | | **~10 Tage** | |

---

## §10 Dokumentenhierarchie

Dieses Dokument steht in der Schicht `specs/` und referenziert:
- `foundation/CHARTER.md` für Sicherheitsregeln (CHARTER §SR-XX)
- `foundation/CONTRACTS.md` für Datenverträge (CONTRACTS §3, §5, §6.10.19–20)
- `specs/HAL.md` für HAL-Spezifikation
- `specs/QUESTOR.md` für Questor-LoopTemplates und Capability-Registry
- `specs/GREMIUM.md` für Atlas-Zonen und FrontierEngine
- `specs/GREMIUM_STRATEGY.md` für Achsen-Steuerung und Briefing

Regel: Änderungen an Karussell-Modulen in diesem Dokument erfordern eine Versionsänderung und eine Überprüfung der referenzierten Dokumente.