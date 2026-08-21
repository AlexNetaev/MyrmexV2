# 📜 CONTRACTS — DATENVERTRÄGE UND ZUSTANDSMASCHINEN

| Feld | Wert |
| :--- | :--- |
| **Dateiname** | `foundation/CONTRACTS.md` |
| **Version** | 1.0.0 (New Architecture) |
| **Status** | **BINDEND** — Alle Datenverträge des Systems |
| **System** | MYRMEX v2.4.0 + Questor v0.2.3 + HAL v0.2.0 |
| **Geltung** | Single Source of Truth für alle Pydantic-Modelle und Zustandsmaschinen |
| **Datum** | 21. August 2026 |

---

## 0. Geltung und Änderungsregeln

Dieses Dokument definiert **alle** Datenverträge des Systems.

**Regel:** Kein anderes Dokument darf Datenverträge definieren oder ändern.
Wenn ein Modul-Dokument (specs/) einen neuen Vertrag benötigt, muss es einen
**Änderungsantrag** an dieses Dokument stellen. Die Änderung wird hier eingearbeitet.

**Referenz:** Alle anderen Dokumente verweisen auf dieses Dokument:
→ `CONTRACTS §2.1: ResearchPackage`
→ `CONTRACTS §7.1: Questor-Zustandsmaschine`

---

## §1 Paket-Verträge

### §1.1 ResearchPackage

```python
ResearchPackage:
    package_id: str                          # ^[A-Za-z0-9._-]{1,128}$
    source_wegmarke: str
    source_wegmarke_version: Optional[str]
    atlas_version_ref: str                   # Pass-Through, kein LLM-Zugriff
    ziel: str                                # Freitext, max 1024 Zeichen
    materials_or_resources: list[str]
    parameter_bounds: dict[str, tuple[float, float]]
    routing_graph: RoutingGraph
    gefahren_mitigationen: list[str]
    kontext: PackageKontext
    dimension_expansion_approval: Optional[str]
    override_requested: bool
    limits: dict[str, float]
    expected_side_effects_or_failure_modes: list[str]
    domain_metadata: dict[str, Any]
    questor_spec: Optional[QuestorSpec]
    planning_hints: Optional[PlanningHints]  # ← NEU: Vertraglich verankert
```

**Pflichtfelder für Validierung:**
- `routing_graph.max_loop_iterations`: int, Pflicht
- `routing_graph.branch_condition_timeout`: float, Pflicht
- `parameter_bounds`: min < max, keine NaN, keine Infinity

**Sonderregel `planning_hints`:**
```python
PlanningHints:
    preferred_strategy: Optional[str]
    initial_parameters: Optional[dict[str, float]]
    priority_parameters: Optional[list[str]]
    known_constraints: Optional[list[str]]
    expected_optimum_region: Optional[dict[str, tuple[float, float]]]
    hinweis_text: Optional[str]              # Freitext, max 512 Zeichen, Injection-Scan
```

### §1.2 QuestorSpec

```python
QuestorSpec:
    spec_version: str                        # "0.2.3"
    autonomy_level: STRICT | GUIDED | ADAPTIVE
    objective_type: Optional[ObjectiveType]
    clarity_threshold: float                 # 0.0–1.0
    allowed_capabilities: list[str]          # ← KORRIGIERT: list[str] statt list[Capability]
    allowed_loop_templates: list[str]
    budget: BudgetSpec
    fallback_policy: list[FallbackRule]
    llm_usage: LLMUsagePolicy
    blackbox_policy: BlackboxPolicy
    initial_trail_policy: TrailPolicy
    operational_metrics_export: allowed | forbidden
```

**Korrektur-Hinweis:** `allowed_capabilities` ist `list[str]`, NICHT `list[Capability]`.
Der Typ `Capability` existiert nicht. Die strukturierten Metadaten kommen aus der
CapabilityRegistry (`specs/QUESTOR.md §11`), nicht aus dem QuestorSpec.

**Sichere Defaults (wenn `questor_spec` fehlt):**
```python
DefaultQuestorSpec:
    spec_version: "0.2.3"
    autonomy_level: STRICT
    objective_type: null
    clarity_threshold: 0.9
    allowed_capabilities: []                 # Leer = KEINE Capability erlaubt (fail-closed)
    allowed_loop_templates: []               # Leer = KEIN Template erlaubt (fail-closed)
    budget:
        max_duration_s: 3600
        max_energy_budget: 1.0
        max_retry_count: 2
        max_llm_calls: 3
    fallback_policy:
        - SANDBOX_IF_UNCLEAR
        - ABORT_IF_NO_SAFE_MODE
    llm_usage:
        advisor_only: true
        max_calls: 3
        timeout_s: 30
        reject_unverified_safety_claims: true
    blackbox_policy:
        write_local: true
        transfer_to_gremium: false
        redaction_level: STRONG
    initial_trail_policy:
        create_trails: false
        require_evidence: true
    operational_metrics_export: allowed
```

### §1.3 QuestorDispatchEnvelope

```python
QuestorDispatchEnvelope:
    dispatch_id: str
    zyklus_id: str                           # ^[A-Za-z0-9._-]{1,128}$
    attempt_id: int                          # 0 <= attempt_id <= 999999
    package: ResearchPackage
    gate_record_ref: str                     # ← PFLICHTFELD
    gate_mode: Optional[NORMAL | FRACTURE_DIAGNOSIS | HIGH_RISK_OVERRIDE | SANDBOX]
    lease_grants: list[LeaseGrant]
    execution_environment_ref: Optional[str]
    dispatch_mode: NORMAL | RETRY | RECOVERY
    security_mode: NORMAL | SANDBOX | DEV_SANDBOX_ONLY | RECOVERY
    dispatch_timestamp: str                  # ISO-8601
    idempotency_key: str                     # Kanonisch gebildet
```

**Pflichtregeln:**
- `gate_record_ref` ist Pflicht → fehlt: `PACKAGE_INVALID`, `OPERATIONAL`
- `gate_mode` darf nicht im Widerspruch zum Gate Record stehen
- `lease_grants` müssen konsistent sein
- `security_mode` muss zu Gate und Leases passen
- `attempt_id`: 0–999999, keine führenden Nullen in kanonischer Form

### §1.4 RoutingGraph

```python
RoutingGraph:
    nodes: list[RoutingNode]
    edges: list[RoutingEdge]
    max_loop_iterations: int                 # Pflicht
    branch_condition_timeout: float          # Pflicht, Sekunden
```

---

## §2 Ergebnis-Verträge

### §2.1 QuestorErgebnisPaket

```python
QuestorErgebnisPaket:
    package_id: str                          # ^[A-Za-z0-9._-]{1,128}$
    zyklus_id: str                           # ^[A-Za-z0-9._-]{1,128}$
    attempt_id: int                          # 0 <= attempt_id <= 999999
    idempotency_key: str                     # Kanonisch: package_id:zyklus_id:attempt_id
    questor_instance_id: str
    sequence_number: int                     # Monoton pro questor_instance_id
    observed_atlas_version_id: str           # Pass-Through
    status: erfolgreich | fehlgeschlagen | abgebrochen
    abbruch_grund: Optional[str]             # Pflicht bei fehlgeschlagen/abgebrochen
    abbruch_klasse: OPERATIONAL | SCIENTIFIC | SAFETY  # Pflichtfeld
    routing_checkpoint: RoutingCheckpoint
    ergebnis_daten: ErgebnisDaten
    validierung: GuardianValidierung
    kristall_kandidaten: list[KristallKandidat]
    gefahren_beobachtet: list[str]
    signale_fuer_atlas: list[SignalEvent]
    vollstaendig_flag: bool                  # IMMER true
    rohdaten_checksumme: str                 # SHA256
    questor_metadata: Optional[QuestorMetadata]
```

**Semantik `abbruch_klasse`:**
| Status | `abbruch_grund` | `abbruch_klasse` |
| :--- | :--- | :--- |
| `erfolgreich` | `null` | `OPERATIONAL` |
| `fehlgeschlagen` | Pflicht | Pflicht |
| `abgebrochen` | Pflicht | Pflicht |

**Kritische Regel:** `abbruch_klasse` ist eine **Ergebnisklasse**, keine wörtliche Abbruchklasse.
Bei Erfolg ist `abbruch_grund = null` und `abbruch_klasse = OPERATIONAL`.

**Keine freien Zusatzfelder:** Alle zusätzlichen Daten gehören in `questor_metadata`.

### §2.2 QuestorMetadata

```python
QuestorMetadata:
    questor_version: str
    policy_version: str
    local_audit: Optional[LocalAuditRef]
    operational_metrics: Optional[OperationalMetrics]
    template_feedback: Optional[TemplateFeedback]
```

**Regeln:**
- `questor_metadata` erzeugt **keine** Kristalle oder Signale
- `operational_metrics` dürfen **nur** operational verwendet werden
- `local_audit` enthält **keine** Blackbox-Inhalte

### §2.3 LocalAuditRef

```python
LocalAuditRef:
    blackbox_id: str
    manifest_checksum: str
    blackbox_digest: str
    redaction_level: NONE | BASIC | STRONG
    retention_class: NORMAL | SAFETY_HOLD | DEVELOPMENT_HOLD
    access_policy_summary: str
```

**Regeln:**
- Kein Pfad, der automatisch vom Gremium gelesen wird
- Keine Übergabe der Blackbox selbst
- Nur Referenz, Digest und Policy-Zusammenfassung

### §2.4 OperationalMetrics

```python
OperationalMetrics:
    oom_count: int
    timeout_count: int
    lease_wait_time_s: float
    lease_denied_count: int
    lease_queued_timeout_count: int
    capability_retry_count: int
    hal_command_duplicate_blocked_count: int
    llm_advice_rejected_count: int
    llm_advice_timeout_count: int
    branch_condition_unresolved_count: int
    recovery_attempts: int
    recovery_lock_denied_count: int
    health_alert_count: int                  # ← NEU aus Health-Monitoring
    health_restart_count: int                # ← NEU aus Health-Monitoring
```

**Regel:** Rein operational. Keine wissenschaftliche Interpretation.

---

## §3 HAL-Verträge

### §3.1 EnvironmentManifest

```python
EnvironmentManifest:
    environment_id: str
    environment_version: str
    schema_version: str
    slots: list[SlotDescriptor]
    mutex_zones: list[MutexZone]
    capabilities: list[str]                  # ← Rohe Strings
    estop_mechanism: str
    max_command_timeout_s: float
    default_lease_ttl_s: float
    heartbeat_interval_s: float
    supported_security_modes: list[str]
    supported_resource_classes: list[str]
```

### §3.2 SlotDescriptor

```python
SlotDescriptor:
    slot_id: str
    display_name: Optional[str]
    resource_class: LAB_ACTUATOR | COMPUTE_NODE | SIMULATION_ENVIRONMENT | SANDBOX_ENVIRONMENT | HYBRID_SLOT
    capabilities: list[str]                  # ← Rohe Strings
    mutex_group: str
    physical_zones: list[str]
    physical_actuation: bool
    compute_capable: bool
    sandbox_capable: bool
    kinematic_collision_class: Optional[str]
    requires_path_reservation: bool
    max_concurrent_commands: int             # Default: 1
    estop_controllable: bool
    max_command_timeout_s: float
    max_process_duration_s: float
    max_parameter_payload_bytes: int
    supported_process_modes: list[str]
    accelerator_type: Optional[str]
    accelerator_count: int
    accelerator_memory_gb: Optional[float]
    supported_runtimes: list[str]
```

### §3.3 HALCommand

```python
HALCommand:
    command_id: str                          # Deterministisch erzeugt
    idempotency_key: str                     # command_id:lease_ref:slot_id
    lease_ref: str
    slot_id: str
    capability: str                          # ← Roher String
    operation: str
    parameters: dict[str, Any]
    parameter_schema_ref: Optional[str]
    parameter_schema_version: Optional[str]
    parameter_checksum: Optional[str]        # SHA256
    payload_artifact_ref: Optional[str]
    timeout_s: float                         # Kommando-Timeout (NICHT Prozess-Dauer!)
    dispatch_mode: NORMAL | RETRY | RECOVERY
    security_mode: NORMAL | SANDBOX | DEV_SANDBOX_ONLY | RECOVERY
    request_source: QUESTOR | MAINTENANCE | TEST
    correlation_id: Optional[str]
```

### §3.4 ProcessCommand

```python
ProcessCommand:
    process_id: str                          # Deterministisch erzeugt
    device_job_id: Optional[str]
    lease_ref: str
    slot_id: str
    capability: str
    operation: str
    parameters: dict[str, Any]
    parameter_schema_ref: Optional[str]
    parameter_schema_version: Optional[str]
    parameter_checksum: Optional[str]
    payload_artifact_ref: Optional[str]
    process_mode: START | MONITOR | RESUME | HOLD | ABORT | RELEASE_STAGE
    expected_process_duration_s: Optional[float]  # Prozess-Dauer (NICHT Kommando-Timeout!)
    process_recipe_ref: Optional[str]
    process_recipe_checksum: Optional[str]
    on_lease_expiry_policy: SAFE_HOLD | ABORT_TO_SAFE_STATE | CONTINUE_PASSIVE_SAFE | REQUIRES_RECONCILE
    stage_release_policy: Optional[StageReleasePolicy]
    timeout_s: float                         # Kommando-Timeout
    dispatch_mode: NORMAL | RETRY | RECOVERY
    security_mode: NORMAL | SANDBOX | DEV_SANDBOX_ONLY | RECOVERY
    request_source: QUESTOR | MAINTENANCE | TEST
    correlation_id: Optional[str]
```

**Kritische Trennung:**
- `timeout_s`: Kommando-Timeout (RPC-Aufruf, Sekunden)
- `expected_process_duration_s`: Prozess-Dauer (physikalisch, Sekunden bis Tage)

### §3.5 HALCommandResult

```python
HALCommandResult:
    command_id: str
    status: SUCCESS | DENIED | TIMEOUT | ESTOP | INTERLOCK | ERROR |
            DUPLICATE_BLOCKED | LEASE_INVALID | LEASE_EXPIRED |
            SLOT_UNAVAILABLE | ZONE_LOCK_UNAVAILABLE
    error_code: Optional[str]
    error_class: Optional[OPERATIONAL | SAFETY]
    slot_state: SlotState
    started_at: Optional[str]
    finished_at: Optional[str]
    receipt_checksum: Optional[str]
    operational_metrics: Optional[dict[str, float]]
```

### §3.6 ProcessResult

```python
ProcessResult:
    process_id: str
    device_job_id: Optional[str]
    slot_id: str
    process_state: PENDING | RUNNING | PAUSED | SAFE_HOLD |
                   WAITING_FOR_RELEASE | COMPLETED | ABORTED | FAULT | UNKNOWN
    current_stage: Optional[str]
    error_code: Optional[str]
    error_class: Optional[OPERATIONAL | SAFETY]
    started_at: Optional[str]
    finished_at: Optional[str]
    elapsed_time_s: Optional[float]
    resume_token: Optional[str]
    resume_allowed: bool
    operational_metrics: Optional[dict[str, float]]
```

### §3.7 SlotState

```python
SlotState:
    slot_id: str
    status: FREE | RESERVED | ACTIVE | ERROR | ESTOP_SUSPENDED | INTERLOCKED | MAINTENANCE | OFFLINE
    device_reachable: bool
    interlock_latched: bool
    interlock_source: Optional[str]
    safe_state_verified: bool
    manual_reset_required: bool
    current_lease_ref: Optional[str]
    current_process_id: Optional[str]
    heartbeat_expires_at: Optional[str]
    last_error: Optional[str]
    last_command_id: Optional[str]
    last_state_change_at: str
```

### §3.8 ZoneState

```python
ZoneState:
    zone_id: str
    status: FREE | LOCKED | PATH_RESERVED | ESTOP_SUSPENDED | INTERLOCKED | MAINTENANCE
    current_holder_slot_id: Optional[str]
    lock_policy: EXCLUSIVE | SINGLE_OCCUPANT | PATH_RESERVATION | CONTAINER_LOCK
    lock_expires_at: Optional[str]
    last_state_change_at: str
```

### §3.9 ProcessState

```python
ProcessState:
    process_id: str
    device_job_id: Optional[str]
    slot_id: str
    lease_ref: str
    process_state: PENDING | RUNNING | PAUSED | SAFE_HOLD |
                   WAITING_FOR_RELEASE | COMPLETED | ABORTED | FAULT | UNKNOWN
    current_stage: Optional[str]
    started_at: Optional[str]
    expected_duration_s: Optional[float]
    elapsed_time_s: Optional[float]
    resume_token: Optional[str]
    resume_allowed: bool
    safe_hold_active: bool
    manual_release_required: bool
    last_state_change_at: str
    last_error: Optional[str]
```

### §3.10 EstopState

```python
EstopState:
    state: NORMAL | ACTIVE | LATCHED | TEST
    origin: SOFTWARE | HARDWARE_INTERLOCK | EXTERNAL_SAFETY_CHAIN
    hardware_interlock_id: Optional[str]
    physical_reset_required: bool
    safe_state_verified: bool
    inspection_required: bool
    reason: Optional[str]
    trigger_source: Optional[str]
    affected_slots: list[str]
    affected_zones: list[str]
    suspended_leases: list[str]
    timestamp: str
    reset_policy: str
    acknowledged_by: Optional[str]
```

### §3.11 HardwareInterlockEvent

```python
HardwareInterlockEvent:
    timestamp: str
    slot_id: str
    interlock_source: str
    severity: SAFETY                         # Immer SAFETY
    affected_commands: list[str]
    suspended_leases: list[str]
    latch_until_manual_reset: bool
    physical_reset_required: bool
    device_reachable: bool
    safe_state_verified: bool
```

### §3.12 HAL-Interface (16 Funktionen)

```python
class HALInterface(Protocol):
    def get_environment_manifest(self) -> EnvironmentManifest: ...
    def get_slot_state(self, slot_id: str) -> SlotState: ...
    def get_zone_state(self, zone_id: str) -> ZoneState: ...
    def execute_command(self, command: HALCommand) -> HALCommandResult: ...
    def start_process(self, process_command: ProcessCommand) -> ProcessResult: ...
    def monitor_process(self, process_id: str) -> ProcessResult: ...
    def hold_process(self, process_id: str) -> ProcessResult: ...
    def resume_process(self, process_id: str, resume_token: str) -> ProcessResult: ...
    def abort_process(self, process_id: str) -> ProcessResult: ...
    def release_stage(self, process_id: str, stage_id: str, release_authority: str) -> ProcessResult: ...
    def report_estop(self, reason: str, trigger_source: str) -> EstopState: ...
    def report_hardware_interlock(self, interlock_event: HardwareInterlockEvent) -> EstopState: ...
    def get_estop_state(self) -> EstopState: ...
    def reconcile_slot_state(self, slot_id: str) -> SlotState: ...
    def reconcile_process_state(self, process_id: str) -> ProcessState: ...
    def get_command_status(self, command_id: str) -> HALCommandStatus: ...
```

---

## §4 Lease- und Gate-Verträge

### §4.1 LeaseGrant

```python
LeaseGrant:
    lease_id: str                            # Pflicht
    granted_at: str                          # Pflicht, ISO-8601
    resource_class: str
    slot_id: str
    ttl_seconds: float
    on_expiry_policy: RETURN | EXTEND | RELEASE
    execution_flags: dict[str, bool]         # Default: alle False
```

### §4.2 LeaseStatus

```python
LeaseStatus:
    status: ACTIVE | EXPIRED | SUSPENDED | RETURNED
    is_active: bool                          # Computed
    is_expired: bool                         # Computed
    suspension_reason: Optional[str]
    remaining_ttl: float                     # Nicht-negativ
```

### §4.3 PathLease

```python
PathLease:
    path_id: str
    reserved_slots: list[str]                # Atomare Reservierung
    start_time: str
    end_time: str
    zone_mutex_refs: list[str]
```

**Regel:** Pfad-Lease ist atomar: alle oder keine Slots. Keine partielle Reservierung.

### §4.4 GateRecord

```python
GateRecord:
    gate_id: str                             # Pflicht
    package_id: str                          # Pflicht
    zyklus_id: str                           # Pflicht
    mode: NORMAL | FRACTURE_DIAGNOSIS | HIGH_RISK_OVERRIDE | SANDBOX
    richter_result: PASS | FAIL
    seher_result: PASS | VETO | TEMP_SUSPENDED
    circuit_breaker_state: CLOSED | OPEN | HALF_OPEN
    appeal_status: PENDING | GRANTED | DENIED
    allowed_security_modes: list[str]        # Für Security-Mode-Prüfung
    signature: str                           # Digitale Signatur
```

### §4.5 StageReleasePolicy

```python
StageReleasePolicy:
    stages: list[StageRelease]

StageRelease:
    stage_id: str
    release_required: bool
    release_authority: QUESTOR | SAFETY_PROCESS | HUMAN | KANZLER
    auto_start_allowed: bool
    max_wait_time_s: Optional[float]
```

---

## §5 Questor-Interna-Verträge

### §5.1 LoopTemplate

```python
LoopTemplate:
    template_id: str
    template_version: str                    # Semantisch (Major.Minor)
    schema_version: str
    domain: str                              # chemie, biologie, ml, physik
    created_by: str
    created_at: str
    last_modified: str
    objective_types: list[ObjectiveType]
    description: str
    required_capabilities: list[str]         # ← Rohe Strings
    required_slot_count: int
    requires_physical_actuation: bool
    requires_long_running_process: bool
    is_recovery_template: bool               # ← NEU: Default false
    steps: list[LoopStep]
    max_internal_iterations: int
    parameter_schema: dict[str, ParameterDefinition]
    termination_conditions: list[TerminationCondition]
    on_step_failure: ABORT_LOOP | SKIP_STEP | RETRY_STEP
    max_step_retries: int
    estimated_cost:
        total_time_s: float
        total_reagent_cost: float            # Normiert 0.0–1.0
        total_compute_cost: float
        total_energy_cost: float
```

**Neues Feld `is_recovery_template`:**
- Default: `false`
- Wenn `security_mode = RECOVERY`: Nur Templates mit `is_recovery_template = true` sind erlaubt
- Recovery-Templates dürfen keine `requires_physical_actuation = true` haben

### §5.2 LoopStep

```python
LoopStep:
    step_id: str
    step_type: HAL_COMMAND | PROCESS_COMMAND | MEASURE | WAIT | EVALUATE
    capability: Optional[str]                # ← Bedingte Pflicht
    operation: Optional[str]
    process_mode: Optional[str]
    parameters: dict[str, Any]
    depends_on: list[str]
    branch_condition: Optional[BranchCondition]
    on_true_next: Optional[str]
    on_false_next: Optional[str]
    timeout_s: float
    parameter_schema_ref: Optional[str]
    parameter_schema_version: Optional[str]
    payload_artifact_ref: Optional[str]
    process_recipe_ref: Optional[str]
    process_recipe_checksum: Optional[str]
    cost:
        time_cost_s: float
        reagent_cost: float
        compute_cost: float
        energy_cost: float
```

**Bedingte Pflicht für `capability`:**
- Bei `step_type = HAL_COMMAND`: `capability` ist **Pflicht**
- Bei `step_type = PROCESS_COMMAND`: `capability` ist **Pflicht**
- Bei `step_type = WAIT`: `capability` ist **verboten** (muss `None` sein)
- Bei `step_type = EVALUATE`: `capability` ist **verboten** (muss `None` sein)
- Bei `step_type = MEASURE`: `capability` ist optional

### §5.3 ExpeditionLedger

```python
ExpeditionLedger:
    ledger_id: str
    package_id: str
    zyklus_id: str
    attempt_id: int
    questor_instance_id: str
    genesis_hash: str
    genesis_timestamp: str
    state: PLANNING | EXECUTING | EVALUATING | FINALIZING | DONE | ABORTED
    current_loop_index: int
    current_step_index: int
    iteration_count: int
    entries: list[LedgerEntry]
    accumulated_cost: AccumulatedCost
    last_checkpoint: LedgerCheckpoint
    wal_position: int
    access_level: READ_WRITE | READ_ONLY
    finalized_at: Optional[str]
    archive_path: Optional[str]
```

### §5.4 WAL-Eintrag

```python
WALEntry:
    wal_id: int
    timestamp: str
    entry_type: LEDGER_ENTRY | CHECKPOINT | HAL_COMMAND_SENT |
                HAL_COMMAND_RESULT | PROCESS_STATE_CHANGED |
                COST_UPDATE | STATE_CHANGE | ERROR | RECOVERY_START |
                SHUTDOWN_CHECKPOINT
    package_id: str
    zyklus_id: str
    attempt_id: int
    payload: dict[str, Any]
    status: PENDING | COMMITTED | ROLLED_BACK
```

### §5.5 KristallKandidat

```python
KristallKandidat:
    kristall_id: str
    typ: str                                 # z.B. "kinetik_optimum"
    loop_template: str                       # Welcher Loop wurde verwendet
    loop_parameter: dict[str, Any]           # Mit welchen Einstellungen
    wert: dict[str, Any]                     # Was war das Ergebnis
    konfidenz: float                         # 0.0–1.0
    ziel_erreicht: bool
    ist_diagnostic: bool
    cluster_integration: bool
```

**Definition:** Der Kristallkandidat ist der **verwendete Loop** mit den jeweiligen
Einstellungen und dem Ergebnis — NICHT der Messwert allein.

### §5.6 SignalEvent

```python
SignalEvent:
    signal_typ: str                          # 🟥 🟨 🟪 🟩 ⬜
    zone_ref: str
    timestamp: str
    source_package_id: str
    konfidenz: float
```

---

## §6 Querschnitts-Verträge

### §6.1 SanitizationConfig

```python
SanitizationConfig:
    version: str
    max_input_length_chars: int              # Default: 4096
    max_output_length_chars: int             # Default: 2048
    injection_patterns: list[str]
    injection_action: REJECT | STRIP | QUARANTINE
    field_whitelist: dict[str, FieldRule]
    output_schema: dict[str, Any]
    safety_claim_keywords: list[str]
    audit_enabled: bool                      # Default: true
    fallback_on_error: DETERMINISTIC
```

### §6.2 SanitizationResult

```python
SanitizationResult:
    status: ACCEPTED | REJECTED | DEGRADED
    sanitized_payload: dict[str, Any]
    rejected_fields: list[str]
    injection_detected: bool
    injection_details: Optional[str]
    warnings: list[str]
    original_hash: str
    sanitized_hash: str
```

### §6.3 LLMOutputValidation

```python
LLMOutputValidation:
    status: VALID | INVALID | SAFETY_REJECT | PARSE_ERROR | TIMEOUT
    parsed_output: Optional[dict[str, Any]]
    constraint_violations: list[str]
    safety_claims_detected: list[str]
    raw_output_hash: str
    validation_timestamp: str
    fallback_applied: bool
    fallback_reason: Optional[str]
```

### §6.4 CapabilityDefinition

```python
CapabilityDefinition:
    capability_id: str                       # z.B. "pipette.transfer"
    version: str
    schema_version: str
    domain: str
    display_name: str
    description: str
    hal_capability_ref: str                  # Muss mit HAL-Manifest übereinstimmen
    parameter_schema: dict[str, ParameterDefinition]
    required_parameters: list[str]
    optional_parameters: list[str]
    requires_physical_actuation: bool
    allowed_security_modes: list[str]
    requires_lease: bool
    requires_dimension_approval: bool
    cost_estimate:
        time_cost_s: float
        reagent_cost: float
        compute_cost: float
        energy_cost: float
    max_timeout_s: float
    max_concurrent_executions: int
    created_by: str
    created_at: str
    last_modified: str
    deprecated: bool
    deprecated_reason: Optional[str]
    successor_capability: Optional[str]
```

### §6.5 CapabilityCheckResult

```python
CapabilityCheckResult:
    status: AVAILABLE | UNAVAILABLE | UNKNOWN | SECURITY_RESTRICTED | DEPRECATED
    capability_id: str
    reason: Optional[str]
    available_slots: list[str]
    security_mode_compatible: bool
    parameter_validation_errors: list[str]
    warnings: list[str]
```

### §6.6 TrailPolicy

```python
TrailPolicy:
    create_trails: bool                      # Default: false
    detail_level: MINIMAL | STANDARD | FULL
    require_evidence: bool                   # Default: true
    include_llm_advice_summary: bool
    include_rejected_alternatives: bool
    include_parameter_snapshots: bool
    max_trails_per_package: int              # Default: 1000
    max_trail_map_size_mb: float             # Default: 10.0
    redaction_level: NONE | BASIC | STRONG
```

### §6.7 HealthMonitorConfig

```python
HealthMonitorConfig:
    heartbeat_interval_s: float              # Default: 5.0
    heartbeat_file_path: str                 # Default: "data/questor_queue/health.json"
    watchdog_check_interval_s: float         # Default: 10.0
    state_duration_limits: dict[str, float]  # -1 = kein Limit
    memory_limit_mb: float                   # Default: 2048.0
    cpu_limit_percent: float                 # Default: 90.0
    progress_check_interval_s: float         # Default: 300.0
    external_monitor_interval_s: float       # Default: 30.0
    heartbeat_stale_threshold_s: float       # Default: 15.0
    package_processing_timeout_s: float      # Default: 86400.0
    alert_cooldown_s: float                  # Default: 300.0
    max_consecutive_alerts: int              # Default: 5
```

### §6.8 ShutdownConfig

```python
ShutdownConfig:
    graceful_shutdown_timeout_s: float       # Default: 60.0
    hal_command_wait_timeout_s: float        # Default: 30.0
    process_hold_timeout_s: float            # Default: 30.0
    result_build_timeout_s: float            # Default: 10.0
    wal_flush_timeout_s: float               # Default: 5.0
    shutdown_flag_path: str                  # Default: "data/questor_queue/shutdown.flag"
    poll_shutdown_flag_interval_s: float     # Default: 5.0
```

### §6.9 Queue-Dateiformate

**Envelope-Datei** (`pending/`, `processing/`):
```json
{
    "schema_version": "0.3.1",
    "file_type": "ENVELOPE",
    "written_by": "DISPATCHER",
    "written_at": "ISO-8601",
    "envelope": { /* QuestorDispatchEnvelope */ }
}
```

**Result-Datei** (`completed/`, `failed/`):
```json
{
    "schema_version": "0.3.1",
    "file_type": "RESULT",
    "written_by": "QUESTOR",
    "written_at": "ISO-8601",
    "result": { /* QuestorErgebnisPaket */ }
}
```

**Registry** (`registry.json`):
```json
{
    "schema_version": "0.3.1",
    "last_updated": "ISO-8601",
    "last_updated_by": "QUESTOR",
    "package_count": 3,
    "packages": {
        "<idempotency_key>": {
            "status": "PENDING | PROCESSING | COMPLETED | FAILED | DELETED",
            "dispatch_timestamp": "ISO-8601",
            "security_mode": "NORMAL",
            "gate_mode": "NORMAL",
            "delete_requested": false
        }
    }
}
```

**Dateinamen-Konvention:**
```
file_name = idempotency_key.replace(":", "_")
```

---

## §7 Zustandsmaschinen

### §7.1 Questor-Zustandsmaschine (11 Zustände)

| Zustand | Bedeutung | Dauer |
| :--- | :--- | :--- |
| `IDLE` | Wartet auf Envelope | Unbegrenzt |
| `RECEIVING` | Envelope empfangen, wird geprüft | Millisekunden |
| `VALIDATING` | Formale Validierung | Millisekunden |
| `PLANNING` | Loop-Auswahl | Sekunden |
| `EXECUTING` | Loop wird ausgeführt | Sekunden bis Tage |
| `EVALUATING` | Ergebnis prüfen | Sekunden |
| `WAITING_FOR_RELEASE` | Manuelle Freigabe nötig | Stunden bis Tage |
| `SAFE_HOLD` | Prozess sicher angehalten | Stunden |
| `RECOVERING` | Nach Crash: Zustand klären | Sekunden bis Minuten |
| `FINALIZING` | Ergebnis wird gebaut | Millisekunden |
| `DONE` | Ergebnis übergeben | Terminal |

**Übergangstabelle (kritische Übergänge):**

| Von | Nach | Auslöser |
| :--- | :--- | :--- |
| `IDLE` | `RECEIVING` | Envelope empfangen |
| `RECEIVING` | `VALIDATING` | Envelope akzeptiert |
| `RECEIVING` | `FINALIZING` | `DIRECT_PACKAGE_FORBIDDEN` |
| `VALIDATING` | `PLANNING` | Validierung bestanden |
| `VALIDATING` | `FINALIZING` | `PACKAGE_INVALID` |
| `PLANNING` | `EXECUTING` | Plan erstellt, PolicyEvaluator GO |
| `PLANNING` | `FINALIZING` | `NO_APPLICABLE_TEMPLATE` / `ABORT_IF_UNCLEAR` |
| `EXECUTING` | `EVALUATING` | Alle Steps ausgeführt |
| `EXECUTING` | `FINALIZING` | ESTOP / Interlock / Budget erschöpft |
| `EXECUTING` | `WAITING_FOR_RELEASE` | Stufe braucht Freigabe |
| `EXECUTING` | `SAFE_HOLD` | Lease-Expiry mit SAFE_HOLD-Policy |
| `EXECUTING` | `RECOVERING` | Crash / OOM |
| `EVALUATING` | `FINALIZING` | Ziel erreicht / nicht erreichbar / Budget erschöpft |
| `EVALUATING` | `PLANNING` | Ziel nicht erreicht + Budget übrig |
| `WAITING_FOR_RELEASE` | `EXECUTING` | Freigabe erteilt |
| `WAITING_FOR_RELEASE` | `FINALIZING` | Freigabe verweigert / Timeout |
| `SAFE_HOLD` | `RECOVERING` | Questor startet neu |
| `SAFE_HOLD` | `FINALIZING` | Abbruch gewünscht |
| `RECOVERING` | `EXECUTING` | Zustand sicher, Resume möglich |
| `RECOVERING` | `FINALIZING` | `RECOVERY_UNSAFE` |
| `FINALIZING` | `DONE` | Ergebnis übergeben |
| `DONE` | `IDLE` | Immer |

**Invarianten:**
1. Questor ist immer in genau EINEM Zustand
2. `FINALIZING` erzeugt IMMER ein vollständiges `questor_ergebnis_paket`
3. `DONE` → `IDLE` ist der einzige Rückkehrpfad
4. `EXECUTING` ist der einzige Zustand mit HAL-Kommandos
5. `RECOVERING` darf nur `reconcile_*` aufrufen

### §7.2 HAL-Slot-Zustandsmaschine

| Zustand | Bedeutung |
| :--- | :--- |
| `FREE` | Slot verfügbar |
| `RESERVED` | Slot reserviert |
| `ACTIVE` | Slot aktiv |
| `ERROR` | Fehlerzustand |
| `ESTOP_SUSPENDED` | ESTOP aktiv |
| `INTERLOCKED` | Hardware-Interlock aktiv |
| `MAINTENANCE` | Wartung |
| `OFFLINE` | Nicht erreichbar |

**Harte Regel für `INTERLOCKED`:**
- Kein `execute_command()`
- Keine automatische Reconciliation auf `FREE`
- `safe_state_verified` muss `true` sein
- `physical_reset_required` muss erfüllt sein

### §7.3 HAL-Prozess-Zustandsmaschine

| Zustand | Bedeutung |
| :--- | :--- |
| `PENDING` | Prozess wartet |
| `RUNNING` | Prozess läuft |
| `PAUSED` | Prozess pausiert |
| `SAFE_HOLD` | Prozess sicher angehalten |
| `WAITING_FOR_RELEASE` | Wartet auf manuelle Freigabe |
| `COMPLETED` | Erfolgreich abgeschlossen |
| `ABORTED` | Abgebrochen |
| `FAULT` | Fehler |
| `UNKNOWN` | Zustand unklar (nach Crash) |

### §7.4 Queue-Paket-Lebenszyklus

```
DISPATCH → PENDING → PROCESSING → COMPLETED / FAILED → RECEIVED → ARCHIVED → CLEANED
                  ↘ DELETED (nur aus PENDING möglich)
```

### §7.5 Shutdown-Phasen

```
SIGNAL_RECEIVED → DRAINING → FINALIZING → TERMINATED
```

### §7.6 Health-Monitoring-Zustände

| Zustand | Bedeutung |
| :--- | :--- |
| `HEALTHY` | Normal |
| `DEGRADED` | Einschränkungen |
| `UNHEALTHY` | Nicht korrekt |
| `DEAD` | Nicht erreichbar |

---

## §8 Idempotenz-Kanon

### §8.1 Paket-Idempotenz

```
idempotency_key = package_id + ":" + zyklus_id + ":" + attempt_id
```

**Regeln:**
- `package_id` und `zyklus_id`: `^[A-Za-z0-9._-]{1,128}$`
- `attempt_id`: Integer, 0–999999, keine führenden Nullen
- Keine Whitespace
- Maximale Länge: 264 Zeichen

**Testvektoren (gültig):**
```
pkg-001:zyklus-014:0
pkg-001:zyklus-014:2
abc.def_1:zyklus-99:10
```

**Testvektoren (ungültig):**
```
pkg 001:zyklus-014:2        ← Whitespace
pkg/001:zyklus-014:2        ← Ungültiges Zeichen
pkg-001:zyklus-014:02       ← Führende Null
pkg-001:zyklus-014:         ← Leer
pkg-001:zyklus-014:1000000  ← Außerhalb Bereich
```

### §8.2 HAL-Kommando-Idempotenz

```
hal_idempotency_key = command_id:lease_ref:slot_id
hal_process_idempotency_key = process_id:lease_ref:slot_id
```

### §8.3 Deterministische ID-Erzeugung

```python
command_id  = f"cmd-{package_id}-{step_id}-{attempt_id}"
process_id  = f"proc-{package_id}-{step_id}-{attempt_id}"
questor_instance_id = f"qi-{package_id}-{sha256(f'{package_id}:{zyklus_id}:{attempt_id}')[:8]}"
```

---

## §9 Fehlermodell

### §9.1 Fehlerklassen

| Klasse | Bedeutung | Wissenschaftliches Signal? |
| :--- | :--- | :--- |
| `OPERATIONAL` | Prozessfehler, Crash, Timeout, Lease-Problem | **Nein** |
| `SCIENTIFIC` | Wissenschaftliche Zielverfehlung | Ja, als Vorschlag |
| `SAFETY` | Sicherheitsverletzung, ESTOP | Ja, mit Sicherheitsprüfung |

### §9.2 Operationale Fehler (HAL)

```
LEASE_INVALID, LEASE_EXPIRED, LEASE_REVOKED, SLOT_BUSY, SLOT_UNAVAILABLE,
ZONE_LOCK_UNAVAILABLE, COMMAND_TIMEOUT, PROCESS_TIMEOUT, DEVICE_UNAVAILABLE,
OOM, COMPUTE_OOM, CUDA_OOM, GPU_LOST, SCHEDULER_REJECTED, NODE_UNAVAILABLE,
CONTAINER_OOM_KILLED, CONTAINER_CRASHED, HAL_INTERNAL_ERROR,
DUPLICATE_COMMAND_BLOCKED, COMMAND_INVALID, PARAMETER_INVALID,
PARAMETER_SCHEMA_UNKNOWN, PARAMETER_CHECKSUM_MISMATCH,
PHYSICAL_EXECUTION_FORBIDDEN, COMPUTE_EXECUTION_FORBIDDEN,
RECOVERY_UNSAFE, RESUME_TOKEN_INVALID, STAGE_RELEASE_DENIED
```

### §9.3 Sicherheitsfehler (HAL)

```
ESTOP_RECEIVED, HARDWARE_INTERLOCK_TRIGGERED, EXTERNAL_SAFETY_CHAIN_TRIGGERED,
SAFETY_LIMIT_VIOLATION, UNSAFE_SLOT_STATE, UNSAFE_ZONE_STATE,
PHYSICAL_INTERLOCK_TRIGGERED, SAFETY_RESET_REQUIRED
```

### §9.4 Abbruchgründe (Questor)

| Abbruchgrund | Klasse |
| :--- | :--- |
| `PACKAGE_INVALID` | OPERATIONAL |
| `DIRECT_PACKAGE_FORBIDDEN` | OPERATIONAL |
| `GATE_MISSING` | OPERATIONAL |
| `NO_APPLICABLE_TEMPLATE` | OPERATIONAL |
| `ABORT_IF_UNCLEAR` | OPERATIONAL |
| `LEASE_QUEUED_TIMEOUT` | OPERATIONAL |
| `ROUTING_LOOP_TIMEOUT` | OPERATIONAL |
| `BUDGET_EXHAUSTED` | OPERATIONAL |
| `TARGET_NOT_REACHED` | SCIENTIFIC |
| `TARGET_NOT_REACHABLE` | SCIENTIFIC |
| `ESTOP_RECEIVED` | SAFETY |
| `HARDWARE_INTERLOCK_TRIGGERED` | SAFETY |
| `GRACEFUL_SHUTDOWN` | OPERATIONAL |
| `RECOVERY_UNSAFE` | OPERATIONAL |

---

## §10 Enums

```python
class ObjectiveType(str, Enum):
    OPTIMIZE = "OPTIMIZE"
    EXPLORE = "EXPLORE"
    VALIDATE = "VALIDATE"
    DIAGNOSE = "DIAGNOSE"
    SIMULATE_ONLY = "SIMULATE_ONLY"
    CLARIFY = "CLARIFY"

class AutonomyLevel(str, Enum):
    STRICT = "STRICT"
    GUIDED = "GUIDED"
    ADAPTIVE = "ADAPTIVE"

class SecurityMode(str, Enum):
    NORMAL = "NORMAL"
    SANDBOX = "SANDBOX"
    DEV_SANDBOX_ONLY = "DEV_SANDBOX_ONLY"
    RECOVERY = "RECOVERY"

class GateMode(str, Enum):
    NORMAL = "NORMAL"
    FRACTURE_DIAGNOSIS = "FRACTURE_DIAGNOSIS"
    HIGH_RISK_OVERRIDE = "HIGH_RISK_OVERRIDE"
    SANDBOX = "SANDBOX"

class AbbruchKlasse(str, Enum):
    OPERATIONAL = "OPERATIONAL"
    SCIENTIFIC = "SCIENTIFIC"
    SAFETY = "SAFETY"

class StepType(str, Enum):
    HAL_COMMAND = "HAL_COMMAND"
    PROCESS_COMMAND = "PROCESS_COMMAND"
    MEASURE = "MEASURE"
    WAIT = "WAIT"
    EVALUATE = "EVALUATE"

class ProcessMode(str, Enum):
    START = "START"
    MONITOR = "MONITOR"
    RESUME = "RESUME"
    HOLD = "HOLD"
    ABORT = "ABORT"
    RELEASE_STAGE = "RELEASE_STAGE"

class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    DEAD = "DEAD"

class WatchdogStatus(str, Enum):
    OK = "OK"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class DecisionType(str, Enum):
    OBJECTIVE_ANALYSIS = "OBJECTIVE_ANALYSIS"
    OBJECTIVE_CLARIFICATION = "OBJECTIVE_CLARIFICATION"
    LOOP_SELECTION = "LOOP_SELECTION"
    PARAMETER_CHOICE = "PARAMETER_CHOICE"
    EVALUATION = "EVALUATION"
    RE_PLAN = "RE_PLAN"
    LLM_ADVICE_ACCEPTED = "LLM_ADVICE_ACCEPTED"
    LLM_ADVICE_REJECTED = "LLM_ADVICE_REJECTED"
    POLICY_VETO = "POLICY_VETO"
    SAFETY_CHECK = "SAFETY_CHECK"
    EARLY_ABORT = "EARLY_ABORT"
    SANITIZATION_QUARANTINE = "SANITIZATION_QUARANTINE"
    SANITIZATION_REJECT = "SANITIZATION_REJECT"
    CAPABILITY_CHECK = "CAPABILITY_CHECK"
    SECURITY_MODE_CHECK = "SECURITY_MODE_CHECK"
    SHUTDOWN_INITIATED = "SHUTDOWN_INITIATED"
    HEALTH_ALERT = "HEALTH_ALERT"
```

---

## §11 Korrekturen gegenüber alten Dokumenten

| # | Korrektur | Quelle (alt) | Status |
| :--- | :--- | :--- | :--- |
| 1 | `QuestorSpec.allowed_capabilities`: `list[Capability]` → `list[str]` | v2.4.0 §7.2, Capability-Registry §3.5 | ✅ Eingearbeitet |
| 2 | `planning_hints` als optionales Feld in `ResearchPackage` | Sanitization P5, QuestCompass §18 | ✅ Eingearbeitet |
| 3 | `LoopTemplate.is_recovery_template: bool` (Default: false) | Security-Mode §4.2, Q1 | ✅ Eingearbeitet |
| 4 | `LoopStep.capability`: Pflicht bei HAL_COMMAND/PROCESS_COMMAND | Capability-Registry Q7 | ✅ Eingearbeitet |
| 5 | `health_alert_count` / `health_restart_count` in OperationalMetrics | Health-Monitoring Q6 | ✅ Eingearbeitet |
| 6 | `GateRecord.allowed_security_modes: list[str]` | Security-Mode §3 | ✅ Eingearbeitet |
| 7 | `TrailPolicy` als vollständiger Vertrag | Trail-Map §3.1 | ✅ Eingearbeitet |

---

## §12 Dokumentenhierarchie

Dieses Dokument steht in der Schicht `foundation/` und wird von allen
`specs/`- und `ops/`-Dokumenten referenziert.

**Regel:** Änderungen an Verträgen in diesem Dokument erfordern eine
Versionsänderung und eine Überprüfung aller referenzierenden Dokumente.