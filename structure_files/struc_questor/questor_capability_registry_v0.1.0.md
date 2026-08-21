# 🧭 QUESTOR-INTERNA: THEMA 2 — CAPABILITY-REGISTRY
## Formale Definition, Registrierung und Laufzeit-Validierung von Capabilities

| Feld | Wert |
|---|---|
| Dateiname | `questor_capability_registry_v0.1.0.md` |
| Version | 0.1.0 |
| System | MYRMEX v2.4.0 + Questor v0.2.3 |
| Status | Arbeitsstand — Architektur-Spezifikation, keine Implementierungsfreigabe |
| Bezug | `structure_questor_interna_v0.4.0.md`, Teil L |
| | `structure_standalone_v2.4.0.md` v1.1.1 (kanonisch) |
| | `structure_hal_v0.2.0.md` |
| Sprache | Deutsch |
| Modus | Dry-Run / Spezifikation |

---

## 0. Dokumentenhierarchie und Geltung

```
1. structure_standalone_v2.4.0.md v1.1.1                    ← kanonisch
2. structure_hal_v0.2.0.md                                   ← HAL-Vertrag
3. structure_questor_interna_v0.4.0.md                       ← Questor-Interna GESAMT
4. diese Datei: questor_capability_registry_v0.1.0.md        ← Detail: Capability-Registry
5. structure_standalone_questor_v0.2.3.md                    ← unterstützend
```

Bei Widersprüchen gilt die kanonische Hauptreferenz.

Dieses Dokument ist Teil L der Questor-Interna-Gesamtspezifikation.
Es ist eigenständig lesbar, setzt aber Grundkenntnisse der Questor-Architektur voraus.

---

## 1. Kritische Analyse des Bestehenden

### 1.1 Was bereits referenziert wird

Die Capability-Registry wird an mehreren Stellen referenziert, aber **nirgends definiert**:

| Stelle | Referenz | Problem |
|---|---|---|
| `structure_standalone_v2.4.0.md` §7.2 | `QuestorSpec.allowed_capabilities: list[Capability]` | **Typ `Capability` existiert nicht.** Nie definiert. |
| `structure_standalone_v2.4.0.md` §9.3 | `EnvironmentManifest.capabilities: list[str]` | HAL nutzt rohe Strings, keine Struktur. |
| `structure_standalone_v2.4.0.md` §9.3 | `SlotDescriptor.capabilities: list[str]` | HAL nutzt rohe Strings. |
| `structure_questor_interna_v0.3.0.md` §12 | `Nur Templates, deren required_capabilities verfügbar sind` | **Prüffunktion nicht definiert.** |
| `structure_questor_interna_v0.3.0.md` §17 | `capabilities_available(loop_instance, context.hal_manifest)` | **Funktion existiert nicht.** |
| `structure_questor_interna_v0.3.0.md` §20 | `LoopTemplate.required_capabilities: list[str]` | Strings ohne Validierung. |
| `structure_questor_interna_v0.3.0.md` §21 | `LoopStep.capability: Optional[str]` | String ohne Validierung. |
| Repository-Struktur | `src/questor/capability_registry.py` | **Datei existiert im Strukturbaum, aber keine Spezifikation.** |

### 1.2 Identifizierte Probleme

| # | Problem | Schweregrad | Begründung |
|---|---|---|---|
| P1 | **Der Typ `Capability` wird in `QuestorSpec.allowed_capabilities` referenziert, ist aber nirgends definiert.** | **KRITISCH** | Pydantic kann das Modell nicht validieren. Implementierung blockiert. |
| P2 | **Die Funktion `capabilities_available()` wird im PolicyEvaluator aufgerufen, ist aber nie definiert.** | **KRITISCH** | PolicyEvaluator kann nicht implementiert werden. |
| P3 | **HAL-Capabilities sind rohe Strings ohne Parameter-Schema.** Ein Template kann `required_capabilities: ["pipette.transfer"]` angeben, aber es gibt keine Definition, welche Parameter `pipette.transfer` erwartet. | **KRITISCH** | HAL-Bridge kann keine HALCommands bauen, weil die Parameter-Validierung fehlt. |
| P4 | **Keine Prüfung, ob eine Template-Capability überhaupt im HAL-Manifest existiert.** Ein Template könnte eine Capability anfordern, die kein Slot bereitstellt. | Hoch | Loop Selection würde ein nicht ausführbares Template wählen. |
| P5 | **Keine Security-Mode-Einschränkung pro Capability.** Eine Capability wie `reactor.heat_to_500C` sollte in `SANDBOX` nicht erlaubt sein. | Hoch | Sicherheitslücke. |
| P6 | **Keine Kosten-Schätzung pro Capability.** Das Kostenmodell (Zeit + Reagenzien + Compute) braucht Capability-spezifische Kosten. | Mittel | Budget-Prüfung ungenau. |
| P7 | **Keine Versionierung von Capabilities.** Wenn sich eine Capability ändert (z.B. neuer Parameter), gibt es keine Kompatibilitätsprüfung. | Mittel | Upgrade-Risiko. |
| P8 | **Keine Capability-zu-Slot-Zuordnung.** QuestCompass weiß nicht, welcher Slot welche Capability bereitstellt. | Hoch | Loop Selection kann keine Slot-Zuordnung durchführen. |
| P9 | **`LoopStep.capability` ist `Optional[str]`.** Bei `step_type = HAL_COMMAND` MUSS eine Capability gesetzt sein, aber das wird nicht erzwungen. | Mittel | Vertragliche Lücke. |
| P10 | **Keine Definition, was bei unbekannter Capability passiert.** Fail-Closed-Punkt fehlt. | Hoch | Implementierungsunklarheit. |

### 1.3 Fazit der Analyse

Die Capability-Registry ist ein **kritisches fehlendes Bindeglied** zwischen:
- **Templates** (die Capabilities anfordern)
- **HAL-Manifest** (das Capabilities bereitstellt)
- **PolicyEvaluator** (der Capabilities prüft)
- **HAL-Bridge** (die Capabilities in HALCommands übersetzt)

Ohne diese Registry kann Questor **nicht prüfen, ob ein Template ausführbar ist**. Die Implementierung ist blockiert.

---

## 2. Formale Definition: Capability-Registry

### 2.1 Zweck

Die Capability-Registry ist das **zentrale Verzeichnis aller bekannten Capabilities** in Questor. Sie:

1. Definiert, was eine Capability ist (Struktur, Parameter, Constraints).
2. Bildet Capability-IDs auf HAL-Capability-Strings ab.
3. Stellt Validierungsfunktionen für PolicyEvaluator, Loop Selection und HAL-Bridge bereit.
4. Definiert Security-Mode-Einschränkungen pro Capability.
5. Liefert Parameter-Schemas für die HAL-Bridge.
6. Liefert Kosten-Schätzungen für das Budget-Tracking.

### 2.2 Position in der Architektur

```
                    ┌──────────────────────────────┐
                    │      LoopRegistry             │
                    │  (data/questor_templates/)    │
                    │  → required_capabilities      │
                    └──────────────┬───────────────┘
                                   │
                                   │ "Brauche ich diese Capabilities?"
                                   ▼
                    ┌──────────────────────────────┐
                    │     CAPABILITY REGISTRY       │
                    │  (data/questor_capabilities/) │
                    │                               │
                    │  ┌─────────────────────────┐ │
                    │  │ CapabilityDefinition    │ │
                    │  │  → parameter_schema     │ │
                    │  │  → security_modes       │ │
                    │  │  → cost_estimate        │ │
                    │  │  → hal_capability_ref   │ │
                    │  └─────────────────────────┘ │
                    └──────┬──────────┬────────────┘
                           │          │
              ┌────────────┘          └────────────┐
              │                                    │
              ▼                                    ▼
   ┌────────────────────┐              ┌────────────────────┐
   │  PolicyEvaluator   │              │    HAL-Bridge      │
   │  → GO / VETO       │              │  → HALCommand      │
   └────────────────────┘              └────────┬───────────┘
                                                │
                                                ▼
                                     ┌────────────────────┐
                                     │   HAL Interface    │
                                     │   → SlotDescriptor │
                                     │   → capabilities   │
                                     └────────────────────┘
```

### 2.3 Grundprinzipien

| Prinzip | Bedeutung |
|---|---|
| **Deterministisch** | Capability-Prüfung ist immer deterministisch. Kein LLM. |
| **Fail-Closed** | Unbekannte Capability → VETO. Keine Ausführung. |
| **Read-Only** | Registry wird beim Start geladen und ist während der Ausführung unveränderlich. |
| **HAL-Kompatibel** | Capability-IDs sind Strings, die mit HAL `capabilities: list[str]` kompatibel sind. |
| **Questor-Intern** | Die Registry gehört zu Questor, nicht zu HAL. HAL kennt nur Strings. |

---

## 3. Datenverträge

### 3.1 CapabilityDefinition

```yaml
CapabilityDefinition:
  capability_id: str              # Eindeutiger String, z.B. "pipette.transfer"
  version: str                    # Semantisch, z.B. "1.0"
  schema_version: str             # Schema-Version der Registry, z.B. "0.3.1"
  domain: str                     # "general" | "chemie" | "biologie" | "ml" | "physik"
  display_name: str               # Menschenlesbarer Name
  description: str                # Beschreibung der Capability
  
  # HAL-Mapping
  hal_capability_ref: str         # Der String, den HAL im Manifest führt
                                  # MUSS mit einem Eintrag in EnvironmentManifest.capabilities
                                  # oder SlotDescriptor.capabilities übereinstimmen
  
  # Parameter
  parameter_schema: dict[str, ParameterDefinition]
  required_parameters: list[str]  # Pflichtfelder
  optional_parameters: list[str]  # Optionale Felder
  
  # Sicherheit
  requires_physical_actuation: bool   # True = physische Wirkung
  allowed_security_modes: list[str]   # NORMAL | SANDBOX | DEV_SANDBOX_ONLY | RECOVERY
  requires_lease: bool                # True = Lease erforderlich (immer true bei HAL)
  requires_dimension_approval: bool   # True = dimension_expansion_approval nötig
  
  # Kosten
  cost_estimate:
    time_cost_s: float            # Geschätzte Zeit pro Ausführung
    reagent_cost: float           # Normiert 0.0–1.0
    compute_cost: float           # Normiert 0.0–1.0
    energy_cost: float
  
  # Constraints
  max_timeout_s: float            # Maximaler Timeout für diese Capability
  max_concurrent_executions: int  # Wie viele gleichzeitige Ausführungen
  
  # Metadaten
  created_by: str
  created_at: str
  last_modified: str
  deprecated: bool                # True = Capability ist veraltet
  deprecated_reason: Optional[str]
  successor_capability: Optional[str]  # Nachfolger bei Deprecation
```

### 3.2 ParameterDefinition

```yaml
ParameterDefinition:
  name: str                       # Parametername, z.B. "volume_ml"
  type: FLOAT | INT | STRING | BOOL | ENUM | ARRAY | OBJECT
  required: bool
  default: Optional[Any]          # Nur wenn required = false
  min_value: Optional[float]      # Für FLOAT/INT
  max_value: Optional[float]      # Für FLOAT/INT
  min_length: Optional[int]       # Für STRING/ARRAY
  max_length: Optional[int]       # Für STRING/ARRAY
  enum_values: Optional[list[str]]  # Für ENUM
  pattern: Optional[str]          # Regex für STRING
  description: str
  unit: Optional[str]             # z.B. "ml", "nm", "°C"
```

### 3.3 CapabilityRegistry (Gesamtstruktur)

```yaml
CapabilityRegistry:
  registry_version: str           # z.B. "0.3.1"
  schema_version: str             # z.B. "0.3.1"
  loaded_at: str                  # ISO-8601 Zeitstempel
  source_path: str                # "data/questor_capabilities/"
  capabilities: dict[str, CapabilityDefinition]  # Key = capability_id
  capability_count: int
  domains: list[str]              # Alle vertretenen Domänen
  integrity_hash: str             # SHA256 über alle Capability-Dateien
```

### 3.4 CapabilityCheckResult

```yaml
CapabilityCheckResult:
  status: AVAILABLE | UNAVAILABLE | UNKNOWN | SECURITY_RESTRICTED | DEPRECATED
  capability_id: str
  reason: Optional[str]
  available_slots: list[str]      # Slot-IDs, die diese Capability bereitstellen
  security_mode_compatible: bool
  parameter_validation_errors: list[str]
  warnings: list[str]
```

### 3.5 Korrektur: QuestorSpec.allowed_capabilities

**KRITISCHE ÄNDERUNG:** Der Typ `list[Capability]` in `QuestorSpec.allowed_capabilities` muss korrigiert werden.

**Vorher (fehlerhaft):**
```yaml
QuestorSpec:
  allowed_capabilities: list[Capability]  # Typ existiert nicht!
```

**Nachher (korrigiert):**
```yaml
QuestorSpec:
  allowed_capabilities: list[str]  # Capability-IDs als Strings
```

**Begründung:** HAL verwendet `capabilities: list[str]`. Templates verwenden `required_capabilities: list[str]`. Die Konsistenz erfordert `list[str]`. Die strukturierten Metadaten kommen aus der CapabilityRegistry, nicht aus dem QuestorSpec.

---

## 4. Registrierung und Speicherung

### 4.1 Dateistruktur

```
data/questor_capabilities/
  ├── _registry.yaml              # Registry-Metadaten
  ├── general/
  │   ├── pipette.transfer.yaml
  │   ├── spectrometer.measure_absorbance.yaml
  │   ├── incubator.set_temperature.yaml
  │   └── balance.weigh.yaml
  ├── chemie/
  │   ├── reactor.mix.yaml
  │   ├── reactor.heat.yaml
  │   ├── ph_meter.measure.yaml
  │   └── chromatograph.separate.yaml
  ├── biologie/
  │   ├── cell_culture.incubate.yaml
  │   ├── microscope.image.yaml
  │   ├── centrifuge.spin.yaml
  │   └── uv_crosslink.expose.yaml
  ├── ml/
  │   ├── gpu.train.yaml
  │   ├── gpu.predict.yaml
  │   └── cpu.preprocess.yaml
  └── physik/
      ├── sensor.measure.yaml
      ├── actuator.move.yaml
      └── laser.calibrate.yaml
```

### 4.2 `_registry.yaml` (Metadaten)

```yaml
registry_version: "0.3.1"
schema_version: "0.3.1"
created_by: "system_integrator"
created_at: "2025-07-15T00:00:00Z"
last_modified: "2025-07-15T00:00:00Z"
domains:
  - general
  - chemie
  - biologie
  - ml
  - physik
```

### 4.3 Beispiel: `pipette.transfer.yaml`

```yaml
capability_id: "pipette.transfer"
version: "1.0"
schema_version: "0.3.1"
domain: "general"
display_name: "Pipetten-Transfer"
description: >
  Transferiert ein definiertes Volumen Flüssigkeit von einer
  Quellposition zu einer Zielposition.

hal_capability_ref: "pipette.transfer"

parameter_schema:
  volume_ml:
    type: FLOAT
    required: true
    min_value: 0.001
    max_value: 1000.0
    description: "Zu transferierendes Volumen in Millilitern"
    unit: "ml"
  source_well:
    type: STRING
    required: true
    min_length: 1
    max_length: 64
    pattern: "^[A-Za-z0-9_-]+$"
    description: "Quellposition (Well-ID oder Behälter-Referenz)"
  target_well:
    type: STRING
    required: true
    min_length: 1
    max_length: 64
    pattern: "^[A-Za-z0-9_-]+$"
    description: "Zielposition (Well-ID oder Behälter-Referenz)"
  aspirate_speed_ul_s:
    type: FLOAT
    required: false
    default: 100.0
    min_value: 1.0
    max_value: 1000.0
    description: "Aspirationsgeschwindigkeit in µL/s"
    unit: "µL/s"
  dispense_speed_ul_s:
    type: FLOAT
    required: false
    default: 100.0
    min_value: 1.0
    max_value: 1000.0
    description: "Dispensiergeschwindigkeit in µL/s"
    unit: "µL/s"

required_parameters:
  - volume_ml
  - source_well
  - target_well

optional_parameters:
  - aspirate_speed_ul_s
  - dispense_speed_ul_s

requires_physical_actuation: true
allowed_security_modes:
  - NORMAL
  - SANDBOX
requires_lease: true
requires_dimension_approval: false

cost_estimate:
  time_cost_s: 5.0
  reagent_cost: 0.01
  compute_cost: 0.0
  energy_cost: 0.001

max_timeout_s: 30.0
max_concurrent_executions: 1

created_by: "system_integrator"
created_at: "2025-07-15T00:00:00Z"
last_modified: "2025-07-15T00:00:00Z"
deprecated: false
deprecated_reason: null
successor_capability: null
```

### 4.4 Beispiel: `gpu.train.yaml`

```yaml
capability_id: "gpu.train"
version: "1.0"
schema_version: "0.3.1"
domain: "ml"
display_name: "GPU-Training"
description: >
  Führt ein ML-Training auf einer GPU aus.

hal_capability_ref: "gpu.train"

parameter_schema:
  model_architecture:
    type: STRING
    required: true
    min_length: 1
    max_length: 128
    description: "Modellarchitektur oder Referenz auf Modell-Definition"
  dataset_ref:
    type: STRING
    required: true
    min_length: 1
    max_length: 256
    description: "Referenz auf das Trainingsdataset"
  epochs:
    type: INT
    required: true
    min_value: 1
    max_value: 10000
    description: "Anzahl der Trainingsepochen"
  batch_size:
    type: INT
    required: false
    default: 32
    min_value: 1
    max_value: 4096
    description: "Batch-Größe"
  learning_rate:
    type: FLOAT
    required: false
    default: 0.001
    min_value: 0.0000001
    max_value: 10.0
    description: "Lernrate"
  accelerator_type:
    type: ENUM
    required: false
    default: "any"
    enum_values:
      - "any"
      - "nvidia_a100"
      - "nvidia_h100"
      - "amd_mi300"
    description: "GPU-Typ"

required_parameters:
  - model_architecture
  - dataset_ref
  - epochs

optional_parameters:
  - batch_size
  - learning_rate
  - accelerator_type

requires_physical_actuation: false
allowed_security_modes:
  - NORMAL
  - SANDBOX
  - DEV_SANDBOX_ONLY
requires_lease: true
requires_dimension_approval: false

cost_estimate:
  time_cost_s: 3600.0
  reagent_cost: 0.0
  compute_cost: 0.8
  energy_cost: 0.5

max_timeout_s: 86400.0
max_concurrent_executions: 1

created_by: "system_integrator"
created_at: "2025-07-15T00:00:00Z"
last_modified: "2025-07-15T00:00:00Z"
deprecated: false
deprecated_reason: null
successor_capability: null
```

### 4.5 Ladeprozess

```
QUESTOR-START:
  1. _registry.yaml lesen
  2. Alle .yaml-Dateien aus data/questor_capabilities/ laden
  3. Jede Datei gegen das CapabilityDefinition-Schema validieren
  4. Prüfen: capability_id eindeutig?
  5. Prüfen: hal_capability_ref gesetzt?
  6. Prüfen: parameter_schema konsistent?
  7. Prüfen: allowed_security_modes ⊆ {NORMAL, SANDBOX, DEV_SANDBOX_ONLY, RECOVERY}?
  8. Integritäts-Hash berechnen
  9. Registry als READ-ONLY sperren
  
  Bei FEHLER:
  → Questor startet NICHT
  → Fehler wird protokolliert
  → Questor-Prozess beendet sich mit Fehlercode
```

**Kritische Regel:** Die Registry wird **einmalig beim Start** geladen. Es gibt **keine Laufzeit-Registrierung**. Änderungen erfordern einen Neustart.

---

## 5. Laufzeit-Validierung

### 5.1 Die drei Prüfebenen

Die Capability-Validierung erfolgt in **drei Ebenen**, die ALLE bestanden werden müssen.

```
EBENE 1: REGISTRY-CHECK (Questor-intern)
  → Ist die Capability in der CapabilityRegistry bekannt?
  → Ist die Capability nicht deprecated?
  → Ergebnis: KNOWN oder UNKNOWN

EBENE 2: HAL-CHECK (HAL-Manifest)
  → Ist die Capability im EnvironmentManifest.capabilities vorhanden?
  → Gibt es mindestens einen Slot, der die Capability bereitstellt?
  → Ist der Slot im aktuellen security_mode nutzbar?
  → Ergebnis: AVAILABLE oder UNAVAILABLE

EBENE 3: PACKAGE-CHECK (QuestorSpec)
  → Ist die Capability in QuestorSpec.allowed_capabilities?
  → Wenn allowed_capabilities leer ist: KEINE Capability erlaubt (fail-closed)
  → Ergebnis: ALLOWED oder FORBIDDEN
```

**Regel:** Alle drei Ebenen müssen positiv sein. Wenn eine Ebene fehlschlägt, ist die Capability NICHT verfügbar.

### 5.2 Funktion: `check_capability`

```python
def check_capability(
    capability_id: str,
    registry: CapabilityRegistry,
    hal_manifest: EnvironmentManifest,
    questor_spec: QuestorSpec,
    security_mode: str
) -> CapabilityCheckResult:
    
    # EBENE 1: Registry-Check
    if capability_id not in registry.capabilities:
        return CapabilityCheckResult(
            status=UNKNOWN,
            capability_id=capability_id,
            reason=f"Capability '{capability_id}' ist nicht in der Registry",
            available_slots=[],
            security_mode_compatible=False,
            parameter_validation_errors=[],
            warnings=[]
        )
    
    cap_def = registry.capabilities[capability_id]
    
    if cap_def.deprecated:
        return CapabilityCheckResult(
            status=DEPRECATED,
            capability_id=capability_id,
            reason=f"Capability '{capability_id}' ist deprecated: {cap_def.deprecated_reason}",
            available_slots=[],
            security_mode_compatible=False,
            parameter_validation_errors=[],
            warnings=[f"Nachfolger: {cap_def.successor_capability}"]
        )
    
    # EBENE 2: HAL-Check
    available_slots = []
    for slot in hal_manifest.slots:
        if cap_def.hal_capability_ref in slot.capabilities:
            if security_mode in cap_def.allowed_security_modes:
                available_slots.append(slot.slot_id)
    
    if not available_slots:
        return CapabilityCheckResult(
            status=UNAVAILABLE,
            capability_id=capability_id,
            reason=f"Kein Slot stellt '{capability_id}' im Modus '{security_mode}' bereit",
            available_slots=[],
            security_mode_compatible=False,
            parameter_validation_errors=[],
            warnings=[]
        )
    
    # EBENE 3: Package-Check
    if capability_id not in questor_spec.allowed_capabilities:
        return CapabilityCheckResult(
            status=SECURITY_RESTRICTED,
            capability_id=capability_id,
            reason=f"Capability '{capability_id}' ist nicht in allowed_capabilities",
            available_slots=available_slots,
            security_mode_compatible=True,
            parameter_validation_errors=[],
            warnings=[]
        )
    
    # ALLE CHECKS BESTANDEN
    return CapabilityCheckResult(
        status=AVAILABLE,
        capability_id=capability_id,
        reason=None,
        available_slots=available_slots,
        security_mode_compatible=True,
        parameter_validation_errors=[],
        warnings=[]
    )
```

### 5.3 Funktion: `capabilities_available` (PolicyEvaluator)

Dies ist die Funktion, die im PolicyEvaluator (§17 der Questor-Interna v0.3.0) referenziert wird und bisher fehlt:

```python
def capabilities_available(
    loop_instance: LoopInstance,
    hal_manifest: EnvironmentManifest,
    registry: CapabilityRegistry,
    questor_spec: QuestorSpec,
    security_mode: str
) -> bool:
    """
    Prüft, ob ALLE Capabilities eines Loops verfügbar sind.
    Returns: True wenn alle verfügbar, False wenn auch nur eine fehlt.
    """
    for step in loop_instance.steps:
        if step.capability is None:
            if step.step_type in (WAIT, EVALUATE):
                continue
            return False
        
        result = check_capability(
            capability_id=step.capability,
            registry=registry,
            hal_manifest=hal_manifest,
            questor_spec=questor_spec,
            security_mode=security_mode
        )
        
        if result.status != AVAILABLE:
            return False
    
    return True
```

### 5.4 Funktion: `validate_parameters`

```python
def validate_parameters(
    capability_id: str,
    parameters: dict[str, Any],
    registry: CapabilityRegistry
) -> list[str]:
    """
    Validiert Parameter gegen das Capability-Schema.
    Returns: Liste der Validierungsfehler (leer = alles OK).
    """
    errors = []
    
    if capability_id not in registry.capabilities:
        return [f"UNKNOWN_CAPABILITY: {capability_id}"]
    
    cap_def = registry.capabilities[capability_id]
    schema = cap_def.parameter_schema
    
    # Pflichtfelder prüfen
    for req_param in cap_def.required_parameters:
        if req_param not in parameters:
            errors.append(f"MISSING_REQUIRED_PARAMETER: {req_param}")
    
    # Jeden übergebenen Parameter prüfen
    for param_name, param_value in parameters.items():
        if param_name not in schema:
            errors.append(f"UNKNOWN_PARAMETER: {param_name}")
            continue
        
        param_def = schema[param_name]
        
        # Typ-Prüfung
        if param_def.type == FLOAT:
            if not isinstance(param_value, (int, float)):
                errors.append(f"TYPE_MISMATCH: {param_name} erwartet FLOAT")
                continue
            if param_value != param_value:  # NaN-Check
                errors.append(f"NAN_PARAMETER: {param_name}")
                continue
            if param_value == float('inf') or param_value == float('-inf'):
                errors.append(f"INFINITY_PARAMETER: {param_name}")
                continue
            if param_def.min_value is not None and param_value < param_def.min_value:
                errors.append(f"BELOW_MIN: {param_name} < {param_def.min_value}")
            if param_def.max_value is not None and param_value > param_def.max_value:
                errors.append(f"ABOVE_MAX: {param_name} > {param_def.max_value}")
        
        elif param_def.type == INT:
            if not isinstance(param_value, int):
                errors.append(f"TYPE_MISMATCH: {param_name} erwartet INT")
                continue
            if param_def.min_value is not None and param_value < param_def.min_value:
                errors.append(f"BELOW_MIN: {param_name} < {param_def.min_value}")
            if param_def.max_value is not None and param_value > param_def.max_value:
                errors.append(f"ABOVE_MAX: {param_name} > {param_def.max_value}")
        
        elif param_def.type == STRING:
            if not isinstance(param_value, str):
                errors.append(f"TYPE_MISMATCH: {param_name} erwartet STRING")
                continue
            if param_def.min_length and len(param_value) < param_def.min_length:
                errors.append(f"TOO_SHORT: {param_name}")
            if param_def.max_length and len(param_value) > param_def.max_length:
                errors.append(f"TOO_LONG: {param_name}")
            if param_def.pattern and not re.match(param_def.pattern, param_value):
                errors.append(f"PATTERN_MISMATCH: {param_name}")
        
        elif param_def.type == BOOL:
            if not isinstance(param_value, bool):
                errors.append(f"TYPE_MISMATCH: {param_name} erwartet BOOL")
        
        elif param_def.type == ENUM:
            if param_value not in param_def.enum_values:
                errors.append(f"INVALID_ENUM: {param_name} = '{param_value}' nicht in {param_def.enum_values}")
        
        elif param_def.type == ARRAY:
            if not isinstance(param_value, list):
                errors.append(f"TYPE_MISMATCH: {param_name} erwartet ARRAY")
                continue
            if param_def.min_length and len(param_value) < param_def.min_length:
                errors.append(f"TOO_SHORT: {param_name}")
            if param_def.max_length and len(param_value) > param_def.max_length:
                errors.append(f"TOO_LONG: {param_name}")
    
    return errors
```

---

## 6. Capability-zu-Slot-Zuordnung

### 6.1 Funktion: `get_slots_for_capability`

```python
def get_slots_for_capability(
    capability_id: str,
    registry: CapabilityRegistry,
    hal_manifest: EnvironmentManifest,
    security_mode: str
) -> list[str]:
    """
    Gibt die Slot-IDs zurück, die eine Capability bereitstellen.
    """
    if capability_id not in registry.capabilities:
        return []
    
    cap_def = registry.capabilities[capability_id]
    matching_slots = []
    
    for slot in hal_manifest.slots:
        if cap_def.hal_capability_ref in slot.capabilities:
            if security_mode in cap_def.allowed_security_modes:
                matching_slots.append(slot.slot_id)
    
    return matching_slots
```

### 6.2 Funktion: `get_all_capabilities_for_slot`

```python
def get_all_capabilities_for_slot(
    slot_id: str,
    registry: CapabilityRegistry,
    hal_manifest: EnvironmentManifest
) -> list[str]:
    """
    Gibt alle Capability-IDs zurück, die ein Slot bereitstellt.
    """
    for slot in hal_manifest.slots:
        if slot.slot_id == slot_id:
            result = []
            for hal_cap in slot.capabilities:
                for cap_id, cap_def in registry.capabilities.items():
                    if cap_def.hal_capability_ref == hal_cap:
                        result.append(cap_id)
            return result
    return []
```

### 6.3 Slot-Auswahl-Strategie

Wenn mehrere Slots eine Capability bereitstellen, wählt QuestCompass deterministisch:

```
PRIORITÄT 1: Slot mit dem wenigsten aktuellen Auslastung
PRIORITÄT 2: Slot mit der kürzesten Warteschlange
PRIORITÄT 3: Slot mit der niedrigsten slot_id (lexikographisch)
```

**Regel:** Die Auswahl ist deterministisch. Kein Zufall, kein LLM.

---

## 7. Security-Mode-Einschränkungen

### 7.1 Matrix

| Capability-Typ | NORMAL | SANDBOX | DEV_SANDBOX_ONLY | RECOVERY |
|---|---|---|---|---|
| `requires_physical_actuation = true` | ✅ | ❌ | ❌ | ❌ |
| `requires_physical_actuation = false` | ✅ | ✅ | ✅ | ❌ |
| `requires_dimension_approval = true` | ✅ (mit Approval) | ❌ | ❌ | ❌ |

### 7.2 Regeln

| Regel | Beschreibung |
|---|---|
| SEC-1 | Wenn `requires_physical_actuation = true` UND `security_mode != NORMAL` → Capability ist NICHT verfügbar. |
| SEC-2 | Wenn `requires_dimension_approval = true` UND `dimension_expansion_approval` fehlt → Capability ist NICHT verfügbar für physische Ausführung. |
| SEC-3 | Wenn `security_mode = RECOVERY` → Keine neuen Capabilities, nur `reconcile_*`. |
| SEC-4 | Wenn `allowed_security_modes` der Capability den aktuellen `security_mode` nicht enthält → Capability ist NICHT verfügbar. |
| SEC-5 | Wenn `QuestorSpec.allowed_capabilities` leer ist → KEINE Capability ist verfügbar (fail-closed Default). |

---

## 8. Zustandsmaschine: Capability-Lifecycle

```
                 ┌──────────────┐
                 │  YAML-DATEI  │
                 │  (Dateisystem)│
                 └──────┬───────┘
                        │ Questor-Start
                        ▼
                 ┌──────────────┐
                 │   LOADING    │
                 └──────┬───────┘
                        │
              ┌─────────┴─────────┐
              │                   │
         VALID             INVALID
              │                   │
              ▼                   ▼
       ┌──────────┐       ┌──────────────┐
       │  ACTIVE  │       │ START_FAILED │──► Questor startet nicht
       │(READ-ONLY)│      └──────────────┘
       └────┬─────┘
            │
            │ Während Ausführung
            ▼
     ┌──────────────────┐
     │  QUERY (read)    │
     │  check_capability│
     │  validate_params │
     │  get_slots       │
     └──────────────────┘
            │
            │ Questor-Shutdown
            ▼
     ┌──────────────┐
     │  UNLOADED    │
     └──────────────┘
```

**Regel:** Es gibt keinen `UPDATE`-Zustand. Die Registry ist entweder `LOADING`, `ACTIVE` oder `UNLOADED`. Änderungen erfordern einen Neustart.

---

## 9. Fehlerbehandlung

| Fehler | Ursache | Aktion | Fehlerklasse |
|---|---|---|---|
| `CAPABILITY_UNKNOWN` | Capability nicht in Registry | VETO im PolicyEvaluator, Template wird gefiltert | OPERATIONAL |
| `CAPABILITY_DEPRECATED` | Capability ist deprecated | VETO, Warning mit Nachfolger | OPERATIONAL |
| `CAPABILITY_NOT_IN_HAL` | Capability nicht im HAL-Manifest | VETO, Template wird gefiltert | OPERATIONAL |
| `CAPABILITY_NOT_ALLOWED` | Capability nicht in allowed_capabilities | VETO, Template wird gefiltert | OPERATIONAL |
| `CAPABILITY_SECURITY_MISMATCH` | Security-Mode nicht erlaubt | VETO, Template wird gefiltert | OPERATIONAL |
| `CAPABILITY_PARAM_MISSING` | Pflichtparameter fehlt | HAL-Bridge sendet nicht, VETO | OPERATIONAL |
| `CAPABILITY_PARAM_INVALID` | Parameter außerhalb Bounds | HAL-Bridge sendet nicht, VETO | OPERATIONAL |
| `CAPABILITY_PARAM_NAN` | Parameter ist NaN | Fail-Closed, Abbruch | OPERATIONAL |
| `CAPABILITY_PARAM_INFINITY` | Parameter ist Infinity | Fail-Closed, Abbruch | OPERATIONAL |
| `CAPABILITY_REGISTRY_CORRUPT` | Registry-Datei ist korrupt | Questor startet nicht | OPERATIONAL |
| `CAPABILITY_REGISTRY_HASH_MISMATCH` | Integritäts-Hash stimmt nicht | Questor startet nicht | OPERATIONAL |
| `CAPABILITY_NO_SLOT_AVAILABLE` | Kein Slot verfügbar (alle belegt) | Warten oder operational abbrechen | OPERATIONAL |

**Kritische Regel:** ALLE Capability-Fehler sind `OPERATIONAL`. Ein Capability-Fehler ist NIEMALS ein `SAFETY`-Ereignis und NIEMALS ein `SCIENTIFIC`-Ereignis.

---

## 10. Edge Cases

| # | Edge Case | Erwartetes Verhalten |
|---|---|---|
| EC-1 | Ein Template fordert `required_capabilities: ["pipette.transfer"]`, aber die Registry enthält nur `"pipette.aspirate"` und `"pipette.dispense"` (feinere Granularität). | `CAPABILITY_UNKNOWN`. Das Template wird gefiltert. QuestCompass sucht ein alternatives Template. Wenn kein Template verfügbar: `NO_APPLICABLE_TEMPLATE`. |
| EC-2 | `QuestorSpec.allowed_capabilities = []` (Default, fail-closed). Ein Template fordert Capabilities. | ALLE Capabilities sind `CAPABILITY_NOT_ALLOWED`. Kein Template ist ausführbar. `NO_APPLICABLE_TEMPLATE`. Das ist das ERWARTETE Verhalten für den Default. |
| EC-3 | Eine Capability ist in der Registry, aber `deprecated = true` mit `successor_capability = "pipette.transfer_v2"`. | `CAPABILITY_DEPRECATED`. Das Template wird gefiltert. Warning wird protokolliert. QuestCompass sucht ein Template, das den Nachfolger nutzt. |
| EC-4 | Zwei Slots bieten dieselbe Capability. Slot A ist `ACTIVE`, Slot B ist `FREE`. | QuestCompass wählt Slot B (FREE). Die Auswahl ist deterministisch: FREE > ACTIVE. |
| EC-5 | Ein LoopStep hat `step_type = HAL_COMMAND` aber `capability = None`. | `CAPABILITY_PARAM_MISSING`. Der Loop ist ungültig. PolicyEvaluator gibt VETO. |
| EC-6 | Eine Capability hat `requires_physical_actuation = true`, aber `security_mode = SANDBOX`. | `CAPABILITY_SECURITY_MISMATCH`. Die Capability ist nicht verfügbar. Kein physischer Zugriff. |
| EC-7 | Ein Parameter hat den Wert `NaN` (z.B. `volume_ml = NaN`). | `CAPABILITY_PARAM_NAN`. Fail-Closed. Der HALCommand wird NICHT gesendet. |
| EC-8 | Die Registry-Datei `pipette.transfer.yaml` enthält einen YAML-Syntax-Fehler. | `CAPABILITY_REGISTRY_CORRUPT`. Questor startet NICHT. Fehler wird protokolliert. |
| EC-9 | Zwei Registry-Dateien definieren dieselbe `capability_id = "pipette.transfer"`. | `CAPABILITY_REGISTRY_CORRUPT` (Duplikat). Questor startet NICHT. |
| EC-10 | Die `hal_capability_ref` in der Registry ist `"pipette.transfer"`, aber das HAL-Manifest enthält nur `"pipette_transfer"` (Unterstrich statt Punkt). | `CAPABILITY_NOT_IN_HAL`. Die Capability ist nicht verfügbar. Das Template wird gefiltert. |
| EC-11 | Ein Template fordert 5 Capabilities. 4 sind verfügbar, 1 nicht. | Das Template wird gefiltert (ALL-OR-NOTHING). Ein Template ist nur ausführbar, wenn ALLE Capabilities verfügbar sind. |
| EC-12 | `security_mode = RECOVERY`. Ein Template fordert Capabilities. | Alle Capabilities sind `CAPABILITY_SECURITY_MISMATCH`. In RECOVERY werden keine neuen Capabilities ausgeführt, nur `reconcile_*`. |

---

## 11. Sicherheitsregeln (Fail-Closed-Punkte)

| # | Regel | Fail-Closed-Aktion |
|---|---|---|
| S1 | Wenn die Registry nicht geladen werden kann | Questor startet nicht. Kein Paket wird verarbeitet. |
| S2 | Wenn eine Capability nicht in der Registry ist | VETO. Template wird gefiltert. |
| S3 | Wenn `allowed_capabilities` leer ist | KEINE Capability ist erlaubt. Kein Template ist ausführbar. |
| S4 | Wenn eine Capability deprecated ist | VETO. Kein Fallback auf die alte Capability. |
| S5 | Wenn der Security-Mode nicht passt | VETO. Keine physische Ausführung. |
| S6 | Wenn ein Pflichtparameter fehlt | HAL-Bridge sendet NICHT. VETO. |
| S7 | Wenn ein Parameter NaN oder Infinity ist | Fail-Closed. Abbruch. |
| S8 | Wenn `requires_dimension_approval = true` und Approval fehlt | Keine physische Ausführung. Sandbox erlaubt, wenn konfiguriert. |
| S9 | Wenn die HAL-Capability-Referenz nicht im Manifest ist | VETO. Template wird gefiltert. |
| S10 | Wenn der Integritäts-Hash der Registry nicht stimmt | Questor startet nicht. Manipulationsverdacht. |

---

## 12. Integration mit bestehenden Komponenten

### 12.1 QuestCompass (Loop Selection, Schritt 1)

```
SCHRITT 1: VERFÜGBARE TEMPLATES FILTERN
  ├── Nur Templates aus QuestorSpec.allowed_loop_templates
  ├── Nur Templates, die den objective_type unterstützen
  ├── Nur Templates, deren required_capabilities verfügbar sind  ← HIER
  ├── Nur Templates, deren estimated_total_cost <= Restbudget
  └── Nur Templates, deren required_slot_count <= verfügbare Slots
```

Die CapabilityRegistry wird in Schritt 1 aufgerufen:

```python
for template in available_templates:
    all_caps_available = True
    for cap_id in template.required_capabilities:
        result = check_capability(cap_id, registry, hal_manifest, questor_spec, security_mode)
        if result.status != AVAILABLE:
            all_caps_available = False
            break
    if not all_caps_available:
        template wird gefiltert
```

### 12.2 PolicyEvaluator (Schritt 3)

```python
# 3. Capability-Prüfung
if not capabilities_available(loop_instance, hal_manifest, registry, questor_spec, security_mode):
    return VETO("CAPABILITY_UNAVAILABLE")
```

### 12.3 HAL-Bridge (Übersetzung)

Die HAL-Bridge nutzt die CapabilityRegistry für:

1. **Parameter-Validierung** vor dem Senden:
```python
errors = validate_parameters(step.capability, step.parameters, registry)
if errors:
    → HALCommand wird NICHT gesendet
    → BridgeResult.status = OPERATIONAL_ABORT
    → Fehler werden protokolliert
```

2. **Capability-Mapping** für den HALCommand:
```python
cap_def = registry.capabilities[step.capability]
hal_command = HALCommand(
    capability=cap_def.hal_capability_ref,  # HAL-String
    operation=step.operation,
    parameters=step.parameters,
    ...
)
```

3. **Timeout-Bestimmung**:
```python
timeout_s = min(step.timeout_s, cap_def.max_timeout_s)
```

### 12.4 LoopTemplate-Erstellung

Wenn ein Domain-Experte ein Template erstellt, muss er die Capabilities aus der Registry referenzieren. Die Template-Validierung prüft:

```
Für jede Capability in template.required_capabilities:
  → Ist sie in der Registry? → NEIN: Template ist ungültig
  → Ist sie nicht deprecated? → NEIN: Template ist ungültig (Warning)
```

### 12.5 ExpeditionLedger

Jede Capability-Prüfung wird als Ledger-Eintrag protokolliert:

```yaml
LedgerEntry:
  entry_type: CAPABILITY_CHECK
  payload:
    capability_id: "pipette.transfer"
    check_result: AVAILABLE
    available_slots: ["slot-roboter-1"]
    security_mode: NORMAL
    parameter_errors: []
  previous_hash: ...
  entry_hash: ...
```

### 12.6 Result-Builder

Der Result-Builder übernimmt `capability_retry_count` in die `OperationalMetrics`. Diese Metrik zählt, wie oft eine Capability nicht verfügbar war und ein Retry versucht wurde.

### 12.7 Trail-Map (Thema 6)

Capability-Checks werden als Trails protokolliert:

| DecisionType | Trigger |
|---|---|
| `CAPABILITY_CHECK` | Capability wurde geprüft |

### 12.8 Security-Mode (Thema 3)

Die Capability-Registry interagiert mit dem Security-Mode-Modul über `allowed_security_modes` pro Capability.

---

## 13. Validierung durch konkretes Beispiel

### 13.1 Szenario: Chemie-Kinetik mit Pipetten-Transfer und Spektrometer

**Input:**

```yaml
# Template: optimize_loop_v1.yaml
template_id: "chemie_optimize_v1"
required_capabilities:
  - "pipette.transfer"
  - "spectrometer.measure_absorbance"
steps:
  - step_id: "step_1"
    step_type: HAL_COMMAND
    capability: "pipette.transfer"
    operation: "execute"
    parameters:
      volume_ml: 5.0
      source_well: "A1"
      target_well: "B2"
  - step_id: "step_2"
    step_type: HAL_COMMAND
    capability: "spectrometer.measure_absorbance"
    operation: "execute"
    parameters:
      wavelength_nm: 450.0
      path_length_mm: 10.0

# QuestorSpec
questor_spec:
  allowed_capabilities:
    - "pipette.transfer"
    - "spectrometer.measure_absorbance"
  allowed_loop_templates:
    - "chemie_optimize_v1"

# HAL-Manifest
environment_manifest:
  capabilities:
    - "pipette.transfer"
    - "spectrometer.measure_absorbance"
    - "incubator.set_temperature"
  slots:
    - slot_id: "slot-roboter-1"
      capabilities:
        - "pipette.transfer"
      physical_actuation: true
    - slot_id: "slot-spektrometer-1"
      capabilities:
        - "spectrometer.measure_absorbance"
      physical_actuation: true

# Security-Mode
security_mode: NORMAL
```

### 13.2 Capability-Check-Durchlauf

**Schritt 1: Registry-Check für `pipette.transfer`**
- In Registry? → JA
- Deprecated? → NEIN
- → KNOWN

**Schritt 2: HAL-Check für `pipette.transfer`**
- `hal_capability_ref = "pipette.transfer"`
- Im Manifest? → JA
- Slot `slot-roboter-1` hat `"pipette.transfer"` → JA
- Security-Mode `NORMAL` in `allowed_security_modes`? → JA
- → AVAILABLE, Slot: `slot-roboter-1`

**Schritt 3: Package-Check für `pipette.transfer`**
- In `allowed_capabilities`? → JA
- → ALLOWED

**Ergebnis: `pipette.transfer` → AVAILABLE**

---

**Schritt 1: Registry-Check für `spectrometer.measure_absorbance`**
- In Registry? → JA
- Deprecated? → NEIN
- → KNOWN

**Schritt 2: HAL-Check für `spectrometer.measure_absorbance`**
- `hal_capability_ref = "spectrometer.measure_absorbance"`
- Im Manifest? → JA
- Slot `slot-spektrometer-1` hat `"spectrometer.measure_absorbance"` → JA
- Security-Mode `NORMAL` in `allowed_security_modes`? → JA
- → AVAILABLE, Slot: `slot-spektrometer-1`

**Schritt 3: Package-Check für `spectrometer.measure_absorbance`**
- In `allowed_capabilities`? → JA
- → ALLOWED

**Ergebnis: `spectrometer.measure_absorbance` → AVAILABLE**

---

**Schritt 4: Parameter-Validierung für `pipette.transfer` (step_1)**
- `volume_ml = 5.0` → FLOAT, in [0.001, 1000.0] → OK
- `source_well = "A1"` → STRING, Länge 2, Pattern `^[A-Za-z0-9_-]+$` → OK
- `target_well = "B2"` → STRING, Länge 2, Pattern → OK
- Pflichtfelder: `volume_ml`, `source_well`, `target_well` → alle vorhanden → OK
- → Keine Fehler

**Schritt 5: Parameter-Validierung für `spectrometer.measure_absorbance` (step_2)**
- `wavelength_nm = 450.0` → FLOAT, in [100.0, 1100.0] → OK
- `path_length_mm = 10.0` → FLOAT, in [0.1, 100.0] → OK
- Pflichtfelder: `wavelength_nm`, `path_length_mm` → alle vorhanden → OK
- → Keine Fehler

**Schritt 6: HALCommand-Erzeugung**
```python
# Step 1
hal_command_1 = HALCommand(
    command_id="cmd-pkg-001-step_1-0",
    idempotency_key="cmd-pkg-001-step_1-0:lease-123:slot-roboter-1",
    lease_ref="lease-123",
    slot_id="slot-roboter-1",
    capability="pipette.transfer",
    operation="execute",
    parameters={"volume_ml": 5.0, "source_well": "A1", "target_well": "B2"},
    timeout_s=min(30.0, 30.0),
    dispatch_mode="NORMAL",
    security_mode="NORMAL",
    request_source="QUESTOR"
)

# Step 2
hal_command_2 = HALCommand(
    command_id="cmd-pkg-001-step_2-0",
    idempotency_key="cmd-pkg-001-step_2-0:lease-123:slot-spektrometer-1",
    lease_ref="lease-123",
    slot_id="slot-spektrometer-1",
    capability="spectrometer.measure_absorbance",
    operation="execute",
    parameters={"wavelength_nm": 450.0, "path_length_mm": 10.0},
    timeout_s=min(30.0, 60.0),
    dispatch_mode="NORMAL",
    security_mode="NORMAL",
    request_source="QUESTOR"
)
```

### 13.3 Ergebnis

Beide Capabilities sind verfügbar. Die Parameter sind gültig. Die HALCommands können gesendet werden. Das Template `chemie_optimize_v1` ist ausführbar.

---

## 14. Offene Fragen und Risiken

| # | Frage / Risiko | Schweregrad | Empfehlung |
|---|---|---|---|
| Q1 | **Wer erstellt die Capability-Definitionen?** Templates werden vom Domain-Experten erstellt. Capabilities sollten vom System-Integrator erstellt werden, da sie HAL-Mapping und Parameter-Schemas definieren. | Hoch | Klare Rollentrennung: System-Integrator erstellt Capabilities, Domain-Experte erstellt Templates. |
| Q2 | **Wie wird die Registry versioniert?** Wenn eine Capability geändert wird (z.B. neuer Parameter), muss die Version erhöht werden. Aber wie wird die Kompatibilität mit alten Templates geprüft? | Mittel | Für v0.3.1: Keine automatische Kompatibilitätsprüfung. Major-Versionsänderung = Template muss aktualisiert werden. |
| Q3 | **Was passiert, wenn HAL eine Capability hat, die nicht in der Questor-Registry ist?** Das ist erlaubt. HAL kann mehr Capabilities haben als Questor kennt. Questor ignoriert unbekannte HAL-Capabilities. | Niedrig | Kein Fehler. Questor nutzt nur die Capabilities, die er kennt. |
| Q4 | **Was passiert, wenn die Registry eine Capability definiert, die HAL nicht hat?** Das ist ein Konfigurationsfehler. Die Capability ist in der Registry, aber kein Slot stellt sie bereit. | Mittel | Beim Start prüfen: Registry-Capabilities gegen HAL-Manifest abgleichen. Warning für fehlende Capabilities. |
| Q5 | **Sollten Capabilities hierarchisch sein?** Z.B. `pipette.*` als Oberbegriff für `pipette.transfer`, `pipette.aspirate`, `pipette.dispense`. | Mittel | Für v0.3.1: NEIN. Keine Hierarchie. Jede Capability ist atomar. Hierarchie kann in v0.4.0 ergänzt werden. |
| Q6 | **Wie wird die Registry getestet?** Es gibt keine Test-Suite für die Registry. | Hoch | Mindestens 22 Unit-Tests für die Registry (siehe Thema 8: Test-Strategie). |
| Q7 | **`LoopStep.capability` ist `Optional[str]`.** Bei `HAL_COMMAND` und `PROCESS_COMMAND` MUSS es gesetzt sein. Bei `WAIT` und `EVALUATE` DARF es nicht gesetzt sein. | Mittel | Pydantic-Validator im LoopStep-Modell: `capability` ist Pflicht bei `HAL_COMMAND` und `PROCESS_COMMAND`, verboten bei `WAIT` und `EVALUATE`. |

---

## 15. Zusammenfassung der Spezifikation

| Aspekt | Definition |
|---|---|
| **Modulname** | `capability_registry.py` |
| **Position** | `src/questor/capability_registry.py` |
| **Datenquelle** | `data/questor_capabilities/` (YAML-Dateien) |
| **Laden** | Beim Questor-Start, einmalig, read-only |
| **Typ-Korrektur** | `QuestorSpec.allowed_capabilities: list[str]` (statt `list[Capability]`) |
| **Prüfebenen** | 3: Registry-Check → HAL-Check → Package-Check |
| **Parameter-Validierung** | Pro Capability, typsicher, NaN/Infinity-Prüfung |
| **Security-Mode** | Pro Capability definiert, zur Laufzeit geprüft |
| **Slot-Zuordnung** | Deterministisch, aus HAL-Manifest abgeleitet |
| **Fehlerbehandlung** | Immer OPERATIONAL, nie SAFETY, nie SCIENTIFIC |
| **Fail-Closed** | Unbekannt → VETO. Deprecated → VETO. Leer → VETO. |
| **Integration** | QuestCompass, PolicyEvaluator, HAL-Bridge, Ledger, Trail-Map |

---

## 16. Kritische Bewertung der eigenen Spezifikation

**Stärken:**
- Klare dreistufige Prüfkette (Registry → HAL → Package)
- Parameter-Validierung pro Capability mit NaN/Infinity-Schutz
- Security-Mode-Einschränkungen pro Capability
- Deterministische Slot-Zuordnung
- Fail-Closed an allen kritischen Punkten
- Kompatibel mit HAL-String-basierten Capabilities
- Zwei vollständige Beispiele (pipette.transfer, gpu.train)

**Schwächen:**
- Keine Capability-Hierarchie (bewusst für v0.3.1)
- Keine automatische Kompatibilitätsprüfung bei Versionsänderungen
- Keine Laufzeit-Registrierung (bewusst, aber einschränkend)
- Die Registry muss manuell mit dem HAL-Manifest synchronisiert werden

**Empfehlung:** Die Spezifikation ist implementierungsreif, ABER:
1. `QuestorSpec.allowed_capabilities` muss von `list[Capability]` auf `list[str]` korrigiert werden.
2. `LoopStep.capability` muss bei `HAL_COMMAND` und `PROCESS_COMMAND` als Pflichtfeld validiert werden.
3. Die Registry-Dateien müssen vor der Implementierung erstellt werden (mindestens für die 4 Domänen-Beispiele aus Teil E der Questor-Interna).
4. Die Funktion `capabilities_available()` muss implementiert werden, da sie im PolicyEvaluator referenziert wird.

---

## 17. Kreuzreferenzen

| Referenz | Beziehung |
|---|---|
| `structure_questor_interna_v0.4.0.md`, Teil L | Dieses Dokument IST Teil L |
| `structure_standalone_v2.4.0.md` §7.2 | `QuestorSpec.allowed_capabilities` muss korrigiert werden |
| `structure_standalone_v2.4.0.md` §9.3 | HAL `capabilities: list[str]` ist die Basis |
| `structure_hal_v0.2.0.md` §8.2 | `SlotDescriptor.capabilities: list[str]` |
| `questor_sanitization_v0.1.0.md` | Sanitization prüft keine Capabilities direkt |
| `questor_security_mode_v0.1.0.md` | Security-Mode-Einschränkungen pro Capability |
| `questor_trail_map_v0.1.0.md` | Capability-Checks werden als Trails protokolliert |
| `questor_test_strategy_v0.1.0.md` | 22 Unit-Tests (U-CAP-01 bis U-CAP-22) |
| `questor_implementation_plan_v0.1.0.md` | Phase Q2 (2-3 Tage) |
| `structure_questor_interna_v0.3.0.md` §17 | `capabilities_available()` wird im PolicyEvaluator referenziert |