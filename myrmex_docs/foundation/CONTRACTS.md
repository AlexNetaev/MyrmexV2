# 📜 CONTRACTS — DATENVERTRÄGE UND ZUSTANDSMASCHINEN

| Feld | Wert |
| --- | --- |
| Dateiname | `foundation/CONTRACTS.md` |
| Version | `1.2.1-twin.1` |
| Status | `ÄNDERUNGSANTRAG DIGITAL-TWIN-SEM-1.0.0 — nach Freigabe BINDEND` |
| System | `MYRMEX v2.4.0 + Questor v0.2.3 + HAL v0.2.0 + Gremium Strategic Layer v1.0.0` |
| Geltung | `Single Source of Truth für alle Pydantic-Modelle und Zustandsmaschinen` |
| Datum | `21. August 2026` |

---

## 0. Geltung und Änderungsregeln

Dieses Dokument definiert alle Datenverträge des Systems.

Regel: Kein anderes Dokument darf Datenverträge definieren oder ändern.

Wenn ein Modul-Dokument (`specs/`) einen neuen Vertrag benötigt, muss es einen Änderungsantrag an dieses Dokument stellen. Die Änderung wird hier eingearbeitet.

Referenz: Alle anderen Dokumente verweisen auf dieses Dokument:

→ `CONTRACTS §2.1: ResearchPackage`  
→ `CONTRACTS §7.1: Questor-Zustandsmaschine`

---

## §0.1 Änderungsantrag ATLAS-HYB-1.0.0 — Atlas-Hybrid-Erweiterung

Dieser Änderungsantrag führt die Datenverträge für das Atlas-Hybrid-System ein.

Das Atlas-Hybrid-System erweitert den Atlas um:

1. Evidence-Semantik  
2. Qualitäts- und Reproduktionsmetadaten  
3. Typed Dimensions und ZoneGeometry  
4. Atlas-Knoten und Atlas-Kanten  
5. Objective Families für Multi-Objective-Forschung  
6. DiagnosticResolution  
7. SafetyConstraints  
8. ExclusionConstraints  
9. FrontierCandidates  
10. ResearchTopics  
11. ExplorationPolicy  
12. AtlasHybridConfig  

Regeln:

- Dieser Änderungsantrag definiert keine neuen Sicherheitsregeln.
- Dieser Änderungsantrag ändert keine CHARTER-Regeln.
- Questor erhält keine Schreibrechte in Atlas oder Archiv.
- HAL erhält keine wissenschaftliche Interpretation.
- Alle neuen Felder sind optional oder haben sichere Defaults.
- Bestehende Verträge bleiben rückwärtskompatibel.
- Wenn neue Felder fehlen, gilt das bisherige Verhalten.

---

## §0.2 Änderungsantrag STRAT-1.0.0 — Strategic-Layer-Integration

Dieser Änderungsantrag führt die Datenverträge für den Gremium Strategic Layer (Cognitive Observatory) ein.

Der Strategic Layer erweitert das Gremium um:
- 4-Achsen-ControlState (Safety, Resource, Research, Governance)
- StrategicBriefing und StrategicDirective
- DirectiveTranslationTable-Verträge
- Mission-Verträge (ResearchManifest, ObjectiveFamilySeed)
- Governance-Verträge (HumanResponseFile, HumanDirective, RoyalLog)
- Forschungs-Verträge (ScientificHypothesis, DimensionOnboardingRequest)
- Report-Verträge (FinalScientificReport)
- StrategicLayerConfig

Regeln:
- Dieser Änderungsantrag definiert keine neuen Sicherheitsregeln.
- Dieser Änderungsantrag ändert keine CHARTER-Regeln.
- Questor erhält keine Kenntnis von Strategic-Layer-Verträgen (→ CHARTER §SR-04).
- HAL erhält keine Kenntnis von Strategic-Layer-Verträgen.
- Alle neuen Felder sind optional oder haben sichere Defaults.
- Bestehende Verträge bleiben rückwärtskompatibel.
- Konfliktregel: CHARTER > dieses Dokument > GREMIUM_STRATEGY.md.

---

## §0.3 Änderungsantrag DIGITAL-TWIN-SEM-1.0.0 — Digital-Twin-Verträge

Dieser Änderungsantrag führt die Datenverträge für das Digital-Twin-System ein.

Das Digital-Twin-System erweitert den Atlas um:
- Digital-Twin-Knoten (`NodeType.DIGITAL_TWIN`)
- Divergenz-Erkennung zwischen Sim- und Real-Kristallen
- Kalibrierungs-Loop als DIAGNOSE-Workflow
- Twin-Modell-Verwaltung (Version, Drift, Validity)

Regeln:
- Dieser Änderungsantrag definiert keine neuen Sicherheitsregeln.
- Dieser Änderungsantrag ändert keine CHARTER-Regeln.
- Questor erhält keine Schreibrechte in Atlas oder Archiv.
- Questor darf `digital_twin_ref` nicht als LLM-Kontext verwenden.
- HAL erhält keine wissenschaftliche Interpretation.
- Alle neuen Felder sind optional oder haben sichere Defaults.
- Bestehende Verträge bleiben rückwärtskompatibel.
- Sim-Evidenz darf keine physischen Kristalle bestätigen (→ CHARTER §SR-08, GREMIUM §6.7).

---

# §1 Paket-Verträge

## §1.1 ResearchPackage

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

    # ── ATLAS-HYB-1.0.0: Neue optionale Atlas-Hybrid-Felder ──
    atlas_expectation_ref: Optional[str]
    objective_family_ref: Optional[str]
    frontier_candidate_ref: Optional[str]
```

Pflichtfelder für Validierung:

- `routing_graph.max_loop_iterations`: `int`, Pflicht
- `routing_graph.branch_condition_timeout`: `float`, Pflicht
- `parameter_bounds`: `min < max`, keine `NaN`, keine `Infinity`

Sonderregel `planning_hints`:

```python
PlanningHints:
    preferred_strategy: Optional[str]
    initial_parameters: Optional[dict[str, float]]
    priority_parameters: Optional[list[str]]
    known_constraints: Optional[list[str]]
    expected_optimum_region: Optional[dict[str, tuple[float, float]]]
    hinweis_text: Optional[str]              # Freitext, max 512 Zeichen, Injection-Scan
```

Sonderregeln ATLAS-HYB-1.0.0 für ResearchPackage:

- `atlas_expectation_ref` ist eine Referenz auf eine Atlas-Hypothese, einen Atlas-Knoten oder eine Erwartung.
- `atlas_expectation_ref` ist Pass-Through für Questor.
- Questor darf `atlas_expectation_ref` nicht als LLM-Kontext verwenden.
- Questor darf `atlas_expectation_ref` nicht verwenden, um direkt auf den Atlas zuzugreifen.
- `objective_family_ref` verweist auf eine `ObjectiveFamily` gemäß `§6.10.10`.
- `frontier_candidate_ref` verweist auf einen `FrontierCandidate` gemäß `§6.10.14`.
- Alle drei Felder sind optional.
- Wenn `atlas_expectation_ref` fehlt, darf daraus keine Bestätigung abgeleitet werden.

---

## §1.2 QuestorSpec

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

Korrektur-Hinweis:

`allowed_capabilities` ist `list[str]`, NICHT `list[Capability]`.

Der Typ `Capability` existiert nicht. Die strukturierten Metadaten kommen aus der CapabilityRegistry (`specs/QUESTOR.md §11`), nicht aus dem QuestorSpec.

Sichere Defaults (wenn `questor_spec` fehlt):

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

---

## §1.3 QuestorDispatchEnvelope

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

Pflichtregeln:

- `gate_record_ref` ist Pflicht → fehlt: `PACKAGE_INVALID`, `OPERATIONAL`
- `gate_mode` darf nicht im Widerspruch zum Gate Record stehen
- `lease_grants` müssen konsistent sein
- `security_mode` muss zu Gate und Leases passen
- `attempt_id`: `0–999999`, keine führenden Nullen in kanonischer Form

---

## §1.4 RoutingGraph

```python
RoutingGraph:
    nodes: list[RoutingNode]
    edges: list[RoutingEdge]
    max_loop_iterations: int                 # Pflicht
    branch_condition_timeout: float          # Pflicht, Sekunden
```

---

# §2 Ergebnis-Verträge

## §2.1 QuestorErgebnisPaket

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

Semantik `abbruch_klasse`:

| Status | `abbruch_grund` | `abbruch_klasse` |
| :--- | :--- | :--- |
| `erfolgreich` | `null` | `OPERATIONAL` |
| `fehlgeschlagen` | Pflicht | Pflicht |
| `abgebrochen` | Pflicht | Pflicht |

Kritische Regel:

`abbruch_klasse` ist eine Ergebnisklasse, keine wörtliche Abbruchklasse.

Bei Erfolg ist `abbruch_grund = null` und `abbruch_klasse = OPERATIONAL`.

Keine freien Zusatzfelder: Alle zusätzlichen Daten gehören in `questor_metadata`.

---

## §2.2 QuestorMetadata

```python
QuestorMetadata:
    questor_version: str
    policy_version: str
    local_audit: Optional[LocalAuditRef]
    operational_metrics: Optional[OperationalMetrics]
    template_feedback: Optional[TemplateFeedback]
```

Regeln:

- `questor_metadata` erzeugt keine Kristalle oder Signale
- `operational_metrics` dürfen nur operational verwendet werden
- `local_audit` enthält keine Blackbox-Inhalte

---

## §2.3 LocalAuditRef

```python
LocalAuditRef:
    blackbox_id: str
    manifest_checksum: str
    blackbox_digest: str
    redaction_level: NONE | BASIC | STRONG
    retention_class: NORMAL | SAFETY_HOLD | DEVELOPMENT_HOLD
    access_policy_summary: str
```

Regeln:

- Kein Pfad, der automatisch vom Gremium gelesen wird
- Keine Übergabe der Blackbox selbst
- Nur Referenz, Digest und Policy-Zusammenfassung

---

## §2.4 OperationalMetrics

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

Regel: Rein operational. Keine wissenschaftliche Interpretation.

---

# §3 HAL-Verträge

## §3.1 EnvironmentManifest

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

---

## §3.2 SlotDescriptor

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

---

## §3.3 HALCommand

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

---

## §3.4 ProcessCommand

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

Kritische Trennung:

- `timeout_s`: Kommando-Timeout (RPC-Aufruf, Sekunden)
- `expected_process_duration_s`: Prozess-Dauer (physikalisch, Sekunden bis Tage)

---

## §3.5 HALCommandResult

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

---

## §3.6 ProcessResult

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

---

## §3.7 SlotState

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

---

## §3.8 ZoneState

```python
ZoneState:
    zone_id: str
    status: FREE | LOCKED | PATH_RESERVED | ESTOP_SUSPENDED | INTERLOCKED | MAINTENANCE
    current_holder_slot_id: Optional[str]
    lock_policy: EXCLUSIVE | SINGLE_OCCUPANT | PATH_RESERVATION | CONTAINER_LOCK
    lock_expires_at: Optional[str]
    last_state_change_at: str
```

---

## §3.9 ProcessState

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

---

## §3.10 EstopState

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

---

## §3.11 HardwareInterlockEvent

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

---

## §3.12 HAL-Interface (16 Funktionen)

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

# §4 Lease- und Gate-Verträge

## §4.1 LeaseGrant

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

---

## §4.2 LeaseStatus

```python
LeaseStatus:
    status: ACTIVE | EXPIRED | SUSPENDED | RETURNED
    is_active: bool                          # Computed
    is_expired: bool                         # Computed
    suspension_reason: Optional[str]
    remaining_ttl: float                     # Nicht-negativ
```

---

## §4.3 PathLease

```python
PathLease:
    path_id: str
    reserved_slots: list[str]                # Atomare Reservierung
    start_time: str
    end_time: str
    zone_mutex_refs: list[str]
```

Regel: Pfad-Lease ist atomar: alle oder keine Slots. Keine partielle Reservierung.

---

## §4.4 GateRecord

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

---

## §4.5 StageReleasePolicy

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

# §5 Questor-Interna-Verträge

## §5.1 LoopTemplate

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

Neues Feld `is_recovery_template`:

- Default: `false`
- Wenn `security_mode = RECOVERY`: Nur Templates mit `is_recovery_template = true` sind erlaubt
- Recovery-Templates dürfen keine `requires_physical_actuation = true` haben

---

## §5.2 LoopStep

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

Bedingte Pflicht für `capability`:

- Bei `step_type = HAL_COMMAND`: `capability` ist Pflicht
- Bei `step_type = PROCESS_COMMAND`: `capability` ist Pflicht
- Bei `step_type = WAIT`: `capability` ist verboten (muss `None` sein)
- Bei `step_type = EVALUATE`: `capability` ist verboten (muss `None` sein)
- Bei `step_type = MEASURE`: `capability` ist optional

---

## §5.3 ExpeditionLedger

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

---

## §5.4 WAL-Eintrag

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

---

## §5.5 KristallKandidat

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

    # ── ATLAS-HYB-1.0.0: Neue optionale Atlas-Hybrid-Felder ──
    expectation_ref: Optional[str]
    confirms_expectation: Optional[bool]
    evidence_class: Optional[EvidenceClass]
    metric_vector: Optional[dict[str, float]]
    evidence_quality: Optional[EvidenceQuality]
    reproducibility_ref: Optional[str]
```

Definition:

Der Kristallkandidat ist der verwendete Loop mit den jeweiligen Einstellungen und dem Ergebnis — NICHT der Messwert allein.

Sonderregeln ATLAS-HYB-1.0.0 für KristallKandidat:

- `expectation_ref` referenziert die Atlas-Erwartung, gegen die das Ergebnis bewertet wurde.
- `confirms_expectation` beschreibt, ob das Ergebnis die Erwartung bestätigt oder widerlegt.
- `confirms_expectation = None` bedeutet: keine sichere Zuordnung möglich.
- `evidence_class` beschreibt die Herkunftsklasse der Evidenz.
- `metric_vector` kann mehrere Zielgrößen enthalten, z. B. `yield`, `purity`, `latency`, `energy`.
- `evidence_quality` beschreibt statistische Qualität und Vertrauensmetadaten.
- `reproducibility_ref` verweist auf einen `ReproducibilityContext` gemäß `§6.10.3`.
- Wenn `ist_diagnostic = true`, darf der Kristall nicht automatisch in normale Cluster integriert werden.
- Wenn `cluster_integration = false`, bleibt der Kristall diagnostisch.

---

## §5.6 SignalEvent

```python
SignalEvent:
    signal_typ: str                          # 🟥 🟨 🟪 🟩 ⬜
    zone_ref: str
    timestamp: str
    source_package_id: str
    konfidenz: float

    # ── ATLAS-HYB-1.0.0: Neue optionale Atlas-Hybrid-Felder ──
    evidence_kind: Optional[EvidenceKind]
    evidence_class: Optional[EvidenceClass]
    expectation_ref: Optional[str]
    observation_direction: Optional[ObservationDirection]
    is_diagnostic: bool = False
    is_policy: bool = False
    quality: Optional[EvidenceQuality]
    validity: Optional[ValidityWindow]
    physical_time_s: Optional[float]
    node_ref: Optional[str]
```

Sonderregeln ATLAS-HYB-1.0.0 für SignalEvent:

- `signal_typ` bleibt das primäre Signal-Symbol.
- `evidence_kind` beschreibt die fachliche Semantik des Signals.
- Wenn `evidence_kind` fehlt, darf der Kartograph die Semantik deterministisch ableiten.
- Solange `evidence_kind` nicht sicher abgeleitet wurde, darf kein Kristall aus dem Signal erzeugt werden.
- `evidence_class` beschreibt die Herkunft der Evidenz.
- `expectation_ref` referenziert die getestete Atlas-Erwartung.
- `observation_direction` beschreibt, ob die Beobachtung eine Erwartung bestätigt, widerlegt oder neutral ist.
- `is_diagnostic = true` markiert diagnostische Evidenz.
- Diagnostische Signale dürfen nicht automatisch als wissenschaftliche Conflict-Energie gezählt werden.
- `is_policy = true` markiert Governance- oder Policy-bezogene Signale.
- Policy-Signale dürfen nicht automatisch als wissenschaftlicher Widerspruch gezählt werden.
- `quality` enthält statistische Qualität.
- `validity` enthält zeitliche Gültigkeit.
- `physical_time_s` kann reale Prozesszeit abbilden, unabhängig von Gremium-Zyklen.
- `node_ref` kann einen Atlas-Knoten referenzieren.

---

# §6 Querschnitts-Verträge

## §6.1 SanitizationConfig

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

---

## §6.2 SanitizationResult

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

---

## §6.3 LLMOutputValidation

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

---

## §6.4 CapabilityDefinition

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

---

## §6.5 CapabilityCheckResult

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

---

## §6.6 TrailPolicy

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

---

## §6.7 HealthMonitorConfig

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

---

## §6.8 ShutdownConfig

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

---

## §6.9 Queue-Dateiformate

Envelope-Datei (`pending/`, `processing/`):

```json
{
    "schema_version": "0.3.1",
    "file_type": "ENVELOPE",
    "written_by": "DISPATCHER",
    "written_at": "ISO-8601",
    "envelope": { /* QuestorDispatchEnvelope */ }
}
```

Result-Datei (`completed/`, `failed/`):

```json
{
    "schema_version": "0.3.1",
    "file_type": "RESULT",
    "written_by": "QUESTOR",
    "written_at": "ISO-8601",
    "result": { /* QuestorErgebnisPaket */ }
}
```

Registry (`registry.json`):

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

Dateinamen-Konvention:

```python
file_name = idempotency_key.replace(":", "_")
```

---

## §6.10 Atlas-Hybrid-Querschnittsverträge

Dieser Abschnitt definiert die Datenverträge des Atlas-Hybrid-Systems.

Regeln:

- Diese Verträge beschreiben Atlas-, Frontier-, Diagnose- und Governance-Zustände.
- Diese Verträge begründen keine Schreibrechte für Questor.
- Questor darf diese Verträge nicht verwenden, um direkt in den Atlas zu schreiben.
- HAL darf diese Verträge nicht wissenschaftlich interpretieren.
- Die Schreibrechte liegen ausschließlich beim Gremium, insbesondere bei Archivar und Kartograph.

---

### §6.10.1 EvidenceQuality

```python
EvidenceQuality:
    source_confidence: float                 # 0.0–1.0
    statistical_confidence: Optional[float]  # 0.0–1.0
    sample_size: int = 1
    replicate_count: int = 1
    variance: Optional[float]
    measurement_uncertainty: Optional[float]
    method_class: Optional[str]
    batch_id: Optional[str]
```

Regeln für EvidenceQuality:

- `source_confidence` muss im Bereich `[0.0, 1.0]` liegen.
- `statistical_confidence`, falls gesetzt, muss im Bereich `[0.0, 1.0]` liegen.
- `sample_size` muss `>= 0` sein.
- `replicate_count` muss `>= 0` sein.
- `variance`, falls gesetzt, muss `>= 0` sein.
- `measurement_uncertainty`, falls gesetzt, muss `>= 0` sein.
- `batch_id` kann Batch- oder Chargeneffekte abbilden.

---

### §6.10.2 ValidityWindow

```python
ValidityWindow:
    valid_from: Optional[str]                # ISO-8601
    valid_until: Optional[str]               # ISO-8601
    expiry_policy: ExpiryPolicy = ExpiryPolicy.DECAY
```

Regeln für ValidityWindow:

- Wenn `valid_from` und `valid_until` gesetzt sind, muss `valid_until` nach `valid_from` liegen.
- `expiry_policy = DECAY` bedeutet: Wissen zerfällt über Zeit.
- `expiry_policy = EXPIRE` bedeutet: Wissen wird nach `valid_until` ungültig.
- `expiry_policy = REVIEW_REQUIRED` bedeutet: Wissen muss nach Ablauf geprüft werden.

---

### §6.10.3 ReproducibilityContext

```python
ReproducibilityContext:
    reproducibility_id: str
    artifact_refs: list[str] = []
    environment_ref: Optional[str] = None
    code_version: Optional[str] = None
    dataset_version: Optional[str] = None
    seed_list: list[int] = []
    calibration_ref: Optional[str] = None
    measurement_protocol: Optional[str] = None
    batch_id: Optional[str] = None
    created_at: str
```

Regeln für ReproducibilityContext:

- `artifact_refs` kann Datensätze, Modelle, Dateien, Proben oder Messreihen referenzieren.
- `environment_ref` kann eine Umgebung, Maschine, Runtime oder Laboraufbau referenzieren.
- `seed_list` ist besonders für ML- und Simulations-Evidenz relevant.
- `calibration_ref` ist besonders für physikalische Messungen relevant.
- `batch_id` ist besonders für biologische und chemische Chargen relevant.

---

### §6.10.4 TypedDimension

```python
TypedDimension:
    dimension_id: str
    display_name: str
    domain: str
    value_type: DimensionValueType
    unit: Optional[str] = None
    value_range: Optional[tuple[float, float]] = None
    categories: Optional[list[str]] = None
    ordinal_levels: Optional[list[str]] = None
    parent_dimension: Optional[str] = None
    approved: bool = False
    onboarding_request_ref: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    created_at: str
    updated_at: str
```

Regeln für TypedDimension:

- `dimension_id` muss eindeutig sein.
- Wenn `value_type = CONTINUOUS` oder `DISCRETE`, sollte `value_range` gesetzt sein.
- Wenn `value_type = CATEGORICAL`, sollte `categories` gesetzt sein.
- Wenn `value_type = ORDINAL`, sollte `ordinal_levels` gesetzt sein.
- Wenn `approved = false`, darf die Dimension nicht für physische Exploration verwendet werden.
- Neue Dimensionen erfordern weiterhin die bestehenden Freigabe- und Approval-Regeln.

---

### §6.10.5 ConditionalRule

```python
ConditionalRule:
    rule_id: str
    if_dimension: str
    if_value: Any
    then_continuous_bounds: dict[str, tuple[float, float]] = {}
    then_categorical_constraints: dict[str, list[str]] = {}
```

Regeln für ConditionalRule:

- `if_dimension` referenziert eine Dimension.
- `if_value` ist der Wert, der die Bedingung auslöst.
- `then_continuous_bounds` definiert erlaubte kontinuierliche Bereiche unter dieser Bedingung.
- `then_categorical_constraints` definiert erlaubte kategorische Werte unter dieser Bedingung.

---

### §6.10.6 ZoneGeometry

```python
ZoneGeometry:
    continuous_bounds: dict[str, tuple[float, float]] = {}
    categorical_constraints: dict[str, list[str]] = {}
    conditional_rules: list[ConditionalRule] = []
```

Regeln für ZoneGeometry:

- `continuous_bounds` enthält kontinuierliche Dimensionsbereiche.
- `categorical_constraints` enthält erlaubte kategorische Werte.
- `conditional_rules` enthalten bedingte Einschränkungen.
- Eine Zone ist nur dann gültig, wenn ihre Geometrie konsistent ist.
- Leere Geometrie ist nicht automatisch eine gültige Forschungsregion.

---

### §6.10.7 AtlasZoneSummary

```python
AtlasZoneSummary:
    zone_id: str
    parent_zone_id: Optional[str] = None
    dimension_refs: list[str] = []
    geometry: ZoneGeometry
    health_state: ZoneHealthState = ZoneHealthState.UNEXPLORED
    quarantine_mode: bool = False
    full_rebuild_required: bool = False
    locked: bool = False
    locked_reason: Optional[str] = None
    coverage_score: float = 0.0
    evidence_mass: float = 0.0
    support_energy: float = 0.0
    conflict_energy: float = 0.0
    diagnostic_energy: float = 0.0
    policy_energy: float = 0.0
    fracture_score: Optional[float] = None
    support_confidence: float = 0.0
    uncertainty_score: float = 1.0
    crystallization_progress: float = 0.0
    diagnostic_budget: int = 0
    cluster_id: Optional[str] = None
    atlas_version: str
    created_at: str
    last_modified: str
```

Regeln für AtlasZoneSummary:

- `fracture_score` darf `None` sein, wenn `evidence_mass` unter der minimalen Evidenzschwelle liegt.
- Wenn `evidence_mass` zu niedrig ist, muss `health_state` auf `UNEXPLORED` oder `EXPLORED_INCONCLUSIVE` gesetzt werden.
- `locked = true` überschreibt Frontier-Freigaben.
- `quarantine_mode = true` erlaubt nur diagnostische Aktionen, sofern Budget und Gate-Modus passen.
- `full_rebuild_required = true` erfordert einen atomaren Neuaufbau oder kontrollierte Eskalation.
- `coverage_score`, `support_energy`, `conflict_energy`, `diagnostic_energy` und `policy_energy` müssen `>= 0` sein.
- `fracture_score`, falls gesetzt, muss im Bereich `[0.0, 1.0]` liegen.
- `support_confidence`, falls berechnet, muss im Bereich `[0.0, 1.0]` liegen.
- `uncertainty_score` muss im Bereich `[0.0, 1.0]` liegen.

---

### §6.10.8 AtlasNode

```python
AtlasNode:
    node_id: str
    node_type: NodeType
    zone_ref: str
    position: dict[str, Any] = {}
    topic_refs: list[str] = []

    # Energiekonten
    support_energy: float = 0.0
    conflict_energy: float = 0.0
    diagnostic_energy: float = 0.0
    coverage_energy: float = 0.0
    evidence_mass: float = 0.0

    # Scores
    support_confidence: float = 0.0
    fracture_score: Optional[float] = None
    uncertainty_score: float = 1.0
    crystallization_progress: float = 0.0

    # Kristallisation
    crystallized: bool = False
    crystallized_at: Optional[str] = None
    ist_diagnostic: bool = False
    cluster_integration: bool = True

    # Beziehungen
    edge_ids: list[str] = []

    # Herkunft und Reproduzierbarkeit
    source_package_ids: list[str] = []
    reproducibility_ref: Optional[str] = None
    validity: Optional[ValidityWindow] = None

    # Metadaten
    created_at: str
    updated_at: str
```

Regeln für AtlasNode:

- `node_id` muss eindeutig sein.
- `position` darf kontinuierliche, diskrete, kategorische oder ordinale Werte enthalten.
- `evidence_mass` ist die Summe aus `support_energy` und `conflict_energy`.
- `fracture_score` darf `None` sein, wenn zu wenig Evidenz vorhanden ist.
- Wenn `node_type = CRYSTAL`, sollte `crystallized = true` sein.
- Wenn `ist_diagnostic = true`, sollte `cluster_integration = false` sein.
- Diagnostic-Knoten dürfen nicht automatisch in normale Cluster integriert werden.

---

### §6.10.9 AtlasEdge

```python
AtlasEdge:
    edge_id: str
    source_node_id: str
    target_node_id: str
    edge_type: EdgeType
    weight: float = 1.0
    evidence_refs: list[str] = []
    created_at: str
    updated_at: str
```

Regeln für AtlasEdge:

- `edge_id` muss eindeutig sein.
- `source_node_id` und `target_node_id` müssen existierende Atlas-Knoten referenzieren.
- `weight` muss `>= 0` sein.
- `evidence_refs` sollen die Evidenz referenzieren, aus der die Kante abgeleitet wurde.
- `EXPLAINS`-Kanten dürfen nur mit nachvollziehbarer DiagnosticResolution oder Governance-Freigabe erzeugt werden.

---

### §6.10.10 ObjectiveFamily

```python
MetricDefinition:
    metric_id: str
    display_name: Optional[str] = None
    direction: MetricDirection
    weight: float = 1.0
    tolerance: Optional[float] = None
    unit: Optional[str] = None


MetricConstraint:
    metric_id: str
    operator: ConstraintOperator
    value: Optional[float] = None
    range: Optional[tuple[float, float]] = None


ObjectiveFamily:
    objective_family_id: str
    name: str
    metrics: list[MetricDefinition] = []
    constraints: list[MetricConstraint] = []
    priority_mode: PriorityMode = PriorityMode.WEIGHTED_SUM
    created_at: str
    updated_at: str
```

Regeln für ObjectiveFamily:

- `objective_family_id` muss eindeutig sein.
- Wenn `priority_mode = PARETO`, dürfen mehrere Zielgrößen gleichrangig behandelt werden.
- Wenn `priority_mode = WEIGHTED_SUM`, sollten Gewichte in `MetricDefinition.weight` gesetzt sein.
- Wenn `priority_mode = LEXICOGRAPHIC`, ist die Reihenfolge der Metriken relevant.
- Zielkonflikte zwischen Metriken sind keine automatischen Widersprüche im Atlas.

---

### §6.10.11 DiagnosticResolution

```python
DiagnosticResolution:
    resolution_id: str
    zone_ref: str
    waypoint_ref: Optional[str] = None
    outcome: DiagnosticOutcomeType
    affected_node_ids: list[str] = []
    affected_evidence_ids: list[str] = []
    uncertainty_reduction: float = 0.0
    recommended_action: str
    review_authority: str
    review_timestamp: str
    created_at: str
```

Regeln für DiagnosticResolution:

- `resolution_id` muss eindeutig sein.
- `outcome` muss einem `DiagnosticOutcomeType` entsprechen.
- `EXPLAINS_CONTRADICTION` und `RESOLVES_CONTRADICTION` erfordern eine nachvollziehbare `review_authority`.
- `review_authority` darf keine LLM-Endentscheidung sein.
- DiagnosticResolution darf keine Evidenz löschen.
- DiagnosticResolution darf nur Gewichte, Zustände oder Kanten ändern, nicht die Append-Only-Historie.
- `uncertainty_reduction` muss im Bereich `[0.0, 1.0]` liegen.

---

### §6.10.12 SafetyConstraint

```python
SafetyConstraint:
    constraint_id: str
    zone_ref: Optional[str] = None
    dimension_ref: Optional[str] = None
    node_ref: Optional[str] = None
    hazard_class: str
    severity: SeverityLevel
    source_event_ref: str
    active: bool = True
    requires_manual_clearance: bool = True
    cleared_by: Optional[str] = None
    cleared_at: Optional[str] = None
    created_at: str
```

Regeln für SafetyConstraint:

- `constraint_id` muss eindeutig sein.
- Wenn `active = true`, darf keine normale Frontier freigegeben werden.
- SafetyConstraints unterliegen keinem automatischen Decay.
- `requires_manual_clearance = true` erfordert eine explizite Freigabe.
- `cleared_by` und `cleared_at` dürfen nur bei tatsächlicher Aufhebung gesetzt werden.
- SafetyConstraints ersetzen keine ESTOP- oder Interlock-Regeln.

---

### §6.10.13 ExclusionConstraint

```python
ExclusionConstraint:
    constraint_id: str
    scope: ScopeType
    zone_ref: Optional[str] = None
    node_ref: Optional[str] = None
    geometry: Optional[ZoneGeometry] = None
    reason: str
    evidence_refs: list[str] = []
    hard_limit: bool = True
    created_at: str
```

Regeln für ExclusionConstraint:

- `constraint_id` muss eindeutig sein.
- `hard_limit = true` bedeutet: Die Region darf nicht normal exploriert werden.
- `hard_limit = false` bedeutet: Die Region ist nur mit erhöhter Vorsicht oder Diagnostik zu betreten.
- `reason` muss nachvollziehbar sein.
- `evidence_refs` sollen die Herkunft der Einschränkung belegen.

---

### §6.10.14 FrontierCandidate

```python
FrontierRationale:
    why_here: str
    supporting_evidence: list[str] = []
    contradicting_evidence: list[str] = []
    expected_outcome: str
    risk_notes: list[str] = []


ResourceContext:
    estimated_time_s: Optional[float] = None
    estimated_reagent_cost: Optional[float] = None
    estimated_compute_cost: Optional[float] = None
    estimated_energy_cost: Optional[float] = None
    required_capabilities: list[str] = []
    lease_requirements: list[str] = []
    slot_requirements: list[str] = []


FrontierCandidate:
    candidate_id: str
    frontier_type: FrontierType
    zone_ref: str
    geometry: ZoneGeometry
    topic_refs: list[str] = []

    # Scores
    frontier_score: float
    novelty_score: float
    promise_score: float
    information_gain_score: float
    connectivity_score: float
    cluster_relevance_score: float
    uncertainty_score: float
    risk_score: float

    # Ressourcen
    resource_context: ResourceContext

    # Sicherheit
    safety_status: SafetyStatus
    active_safety_constraints: list[str] = []

    # Empfehlung
    suggested_objective_type: ObjectiveType
    suggested_gate_mode: GateMode
    required_capabilities: list[str] = []

    # Begründung
    rationale: FrontierRationale

    # Lebenszyklus
    expires_at: Optional[str] = None
    created_at: str
```

Regeln für FrontierCandidate:

- `candidate_id` muss eindeutig sein.
- `frontier_score`, `novelty_score`, `promise_score`, `information_gain_score`, `connectivity_score`, `cluster_relevance_score`, `uncertainty_score` und `risk_score` müssen im Bereich `[0.0, 1.0]` liegen.
- Wenn `safety_status = BLOCKED`, darf der FrontierCandidate nicht für normale Exploration verwendet werden.
- Wenn aktive SafetyConstraints existieren, muss `safety_status` mindestens `RESTRICTED` sein.
- Bei aktiven harten SafetyConstraints muss `safety_status = BLOCKED` sein.
- `rationale` muss maschinenlesbar und nachvollziehbar sein.
- FrontierCandidates sind Empfehlungen, keine Ausführungsfreigaben.

---

### §6.10.15 DiagnosticWaypoint

```python
DiagnosticWaypoint:
    waypoint_id: str
    source_idee: str
    zone_ref: str
    geometry: ZoneGeometry
    intent: ObjectiveType = ObjectiveType.DIAGNOSE
    required_gate_mode: GateMode = GateMode.FRACTURE_DIAGNOSIS
    budget_cost: int = 1
    atlas_version_ref: str
    frontier_candidate_ref: Optional[str] = None
    expectation_ref: Optional[str] = None
    status: WaypointStatus = WaypointStatus.PLATZIERT
    created_at: str
```

Regeln für DiagnosticWaypoint:

- `waypoint_id` muss eindeutig sein.
- `intent` muss `DIAGNOSE` sein.
- `required_gate_mode` muss `FRACTURE_DIAGNOSIS` sein.
- `budget_cost` muss `>= 1` sein.
- DiagnosticWaypoints dürfen nur platziert werden, wenn Diagnose-Budget vorhanden ist.

---

### §6.10.16 ResearchTopic

```python
StopCondition:
    condition_id: str
    metric: StopMetric
    operator: StopOperator
    threshold: float
    window_cycles: Optional[int] = None


ResearchTopic:
    topic_id: str
    name: str
    description: Optional[str] = None
    priority: float = 0.5
    parent_goal: Optional[str] = None
    related_dimensions: list[str] = []
    related_zones: list[str] = []
    related_clusters: list[str] = []
    objective_family_ref: Optional[str] = None
    budget_class: BudgetClass = BudgetClass.MEDIUM
    state: ResearchTopicState = ResearchTopicState.PROPOSED
    stop_conditions: list[StopCondition] = []
    created_at: str
    updated_at: str
```

Regeln für ResearchTopic:

- `topic_id` muss eindeutig sein.
- `priority` muss im Bereich `[0.0, 1.0]` liegen.
- `state` muss einem `ResearchTopicState` entsprechen.
- `stop_conditions` definieren, wann ein Thema als saturiert oder blockiert gilt.
- Ein Thema darf nicht eigenmächtig durch eine LLM als aktiv oder saturiert gesetzt werden.

---

### §6.10.17 ExplorationPolicy

```python
FrontierScoreWeights:
    novelty: float = 0.20
    promise: float = 0.25
    information_gain: float = 0.20
    connectivity: float = 0.10
    cluster_relevance: float = 0.10
    cost: float = 0.10
    risk: float = 0.05


ExplorationPolicy:
    policy_id: str
    exploitation_weight: float = 0.60
    exploration_weight: float = 0.25
    diagnostic_weight: float = 0.15
    max_frontiers_per_cycle: int = 10
    topic_commitment_cycles: int = 3
    cooldown_after_failure_cycles: int = 1
    budget_allocation: dict[str, float] = {}
    score_weights: Optional[FrontierScoreWeights] = None
    set_by: str
    created_at: str
    updated_at: str
```

Regeln für ExplorationPolicy:

- `policy_id` muss eindeutig sein.
- `exploitation_weight`, `exploration_weight` und `diagnostic_weight` sollten zusammen ungefähr `1.0` ergeben.
- `max_frontiers_per_cycle` muss `>= 0` sein.
- `topic_commitment_cycles` muss `>= 0` sein.
- `cooldown_after_failure_cycles` muss `>= 0` sein.
- Die ExplorationPolicy wird durch Kanzler, Königin oder einen autorisierten Governance-Prozess gesetzt.
- Die ExplorationPolicy darf nicht durch eine LLM final entschieden werden.

---

### §6.10.18 AtlasHybridConfig

```python
AtlasHybridConfig:
    min_evidence_mass: float = 0.20
    epsilon: float = 0.001
    k_conf: float = 1.0
    k_evidence: float = 2.0

    # Decay
    signal_decay_lambda: float = 0.08
    signal_ttl_cycles: int = 50

    # Zone Health
    degraded_threshold: float = 0.30
    quarantine_threshold: float = 0.60
    full_rebuild_threshold: float = 0.85
    healthy_support_confidence: float = 0.70

    # Kristallisation
    crystallization_threshold: float = 1.0
    min_confirmations: int = 3
    interrupt_window: int = 5
    max_fracture_for_crystallization: float = 0.30

    # Diagnostik
    diagnostic_budget_default: int = 3

    # Frontier
    frontier_activation_threshold: float = 0.40
    max_frontier_candidates_per_zone: int = 5
```

Regeln für AtlasHybridConfig:

- Alle Schwellwerte müssen deterministisch geprüft werden.
- `epsilon` muss `> 0` sein.
- `min_evidence_mass` muss `>= 0` sein.
- `degraded_threshold < quarantine_threshold < full_rebuild_threshold` muss gelten.
- `min_confirmations` muss `>= 1` sein.
- `interrupt_window` muss `>= 1` sein.
- `diagnostic_budget_default` muss `>= 0` sein.
- Diese Konfiguration ersetzt keine Gate-, Lease- oder Sicherheitsregeln.

---

### §6.10.19 DigitalTwinModel

```python
class DigitalTwinModel(BaseModel):
    twin_model_id: str
    display_name: str
    domain: str
    # Das eigentliche Modell-Artefakt (z.B. ONNX-Datei, PyTorch-Checkpoint,
    # oder ein Satz physikalischer Gleichungen im Archiv)
    model_artifact_ref: str
    model_version: str
    # Schema, das Questor an HAL übergibt, um die Simulation zu parametrisieren
    parameter_schema_ref: Optional[str] = None
    # Kalibrierung
    calibration_method: Optional[str] = None
    last_calibration_at: Optional[str] = None
    calibration_history: list[str] = []  # Referenzen auf Kalibrierungs-Pakete
    # Drift & Validity
    divergence_threshold: float = 0.10   # Ab wann gilt der Twin als \"drifted\"? (0.0–1.0)
    drift_score: float = 0.0             # 0.0 = perfekt kalibriert, 1.0 = maximaler Drift
    validity: Optional[ValidityWindow] = None
    created_at: str
    updated_at: str
```

Regeln für DigitalTwinModel:
- `twin_model_id` muss eindeutig sein.
- `divergence_threshold` muss im Bereich `(0.0, 1.0]` liegen.
- `drift_score` muss im Bereich `[0.0, 1.0]` liegen.
- `model_artifact_ref` referenziert ein Artefakt im Archiv (z.B. eine ONNX-Datei oder ein physikalisches Gleichungsset).
- `calibration_history` enthält Referenzen auf vergangene Kalibrierungs-Pakete (append-only).
- `validity` kann genutzt werden, um die Gültigkeit des Twin-Modells zeitlich zu begrenzen.
- Ein Twin mit `drift_score > divergence_threshold` wird als DEGRADED markiert.
- Ein Twin in `quarantine_mode` darf nur für DIAGNOSE (Kalibrierung) verwendet werden.

---

### §6.10.20 TwinDivergenceReport

```python
class TwinDivergenceReport(BaseModel):
    divergence_id: str
    twin_node_ref: str
    sim_kristall_ref: str      # Kristallkandidat mit evidence_class = SIMULATION
    real_kristall_ref: str     # Kristallkandidat mit evidence_class = PHYSICAL_EXPERIMENT
    # Abweichung pro Metrik im metric_vector (z.B. {\"yield\": 0.15, \"purity\": 0.02})
    metric_deviations: dict[str, float] = {}
    # Aggregierte Abweichung (deterministisch berechnet vom Kartographen)
    overall_divergence_score: float  # 0.0–1.0
    tolerance_breached: bool
    calibration_required: bool
    created_at: str
```

Regeln für TwinDivergenceReport:
- `divergence_id` muss eindeutig sein.
- `twin_node_ref` referenziert einen AtlasNode mit `node_type = DIGITAL_TWIN`.
- `sim_kristall_ref` referenziert einen Kristallkandidaten mit `evidence_class ∈ {SIMULATION, SANDBOX}`.
- `real_kristall_ref` referenziert einen Kristallkandidaten mit `evidence_class = PHYSICAL_EXPERIMENT`.
- `overall_divergence_score` muss im Bereich `[0.0, 1.0]` liegen.
- `metric_deviations` enthält die relative Abweichung pro Metrik: `dev = abs(sim - real) / max(abs(real), epsilon)`.
- `overall_divergence_score = mean(metric_deviations.values())` über alle gemeinsamen Metriken.
- Wenn `overall_divergence_score > twin_model.divergence_threshold`:
  - `tolerance_breached = true`
  - `calibration_required = true`
  - Der `drift_score` des Twin-Knotens wird erhöht.
- Der TwinDivergenceReport wird ausschließlich vom Kartographen erzeugt.
- Questor darf keinen TwinDivergenceReport erzeugen.

---

### §6.11 Strategic-Layer-Verträge

Dieser Abschnitt definiert die Datenverträge des Gremium Strategic Layer.

Regeln:
- Diese Verträge beschreiben strategische Steuerungs-, Briefing- und Governance-Zustände.
- Diese Verträge begründen keine Schreibrechte für Questor oder HAL.
- Questor und HAL kennen diese Verträge nicht (→ CHARTER §SR-04, SL-ACC-4).
- Die Schreibrechte liegen ausschließlich beim Kanzler (deterministisch) und der Königin (via Briefing/Directive).

#### §6.11.1 ControlState

```python
class ControlState(BaseModel):
    safety: SafetyAxis
    resource: ResourceAxis
    research: ResearchAxis
    governance: GovernanceAxis
    updated_at: str
    phase_label: str = ""  # abgeleitet, nicht authoritativ
```

Regeln:
- `phase_label` ist ein abgeleitetes Etikett (z.B. „EXPLOITATION + PHYSICAL_WAIT"). Nicht authoritativ.
- Der autoritative Zustand ist das Tupel `(safety, resource, research, governance)`.

#### §6.11.2 AxisTransition

```python
class AxisTransition(BaseModel):
    transition_id: str
    batch_id: str
    axis: Literal["SAFETY", "RESOURCE", "RESEARCH", "GOVERNANCE"]
    from_value: str
    to_value: str
    trigger_reason: str  # max 512 Zeichen, Injection-Scan
    triggered_by: Literal["KANZLER", "KOENIGIN", "MENSCH", "SYSTEM", "HAL"]
    timestamp: str
```

Regeln:
- `batch_id` ist die gemeinsame ID aller Transitionen eines atomaren Commits.
- Einzel-Transition: `batch_id = transition_id` (Selbstreferenz).
- Atomarität: Alle Transitionen eines Batches werden in genau einer atomaren Dateioperation geschrieben (→ CHARTER §SR-55). Entweder alle oder keine.

#### §6.11.3 ControlStateLog

```python
class ControlStateLog(BaseModel):
    mission_id: str
    transitions: list[AxisTransition] = []
    current_state: ControlState  # authoritativ
    updated_at: str
```

#### §6.11.4 StrategicBriefing

```python
class AtlasMacroState(BaseModel):
    total_zones: int
    healthy_zones: int
    degraded_zones: int
    critical_zones: int
    locked_zones: int
    quarantined_zones: int
    unexplored_zones: int
    avg_fracture_score: Optional[float] = None
    avg_uncertainty_score: Optional[float] = None
    total_crystals: int
    total_hypotheses: int
    total_digital_twins: int
    drifted_twins: int
    frontier_candidates_count: int
    vordenker_calibration_score: Optional[float] = None

class BudgetState(BaseModel):
    total_budget_cycles: int
    used_cycles: int
    remaining_cycles: int
    reserved_cycles: int
    burn_rate_per_cycle: float
    estimated_completion_cycle: Optional[int] = None

class TopicSummary(BaseModel):
    topic_id: str
    state: ResearchTopicState
    progress_percent: float
    best_objective_distance: float
    active_zone_count: int
    saturation_cycles: int

class FractureSummary(BaseModel):
    zone_ref: str
    fracture_score: float
    conflict_count: int
    since_cycles: int

class TwinStatusSummary(BaseModel):
    twin_node_ref: str
    display_name: str
    model_version: str
    drift_score: float
    divergence_threshold: float
    calibration_required: bool

class SlotOutage(BaseModel):
    slot_id: str
    state: str
    since: str

class HardwareHealth(BaseModel):
    slot_outages: list[SlotOutage] = []
    questor_health_status: str  # HEALTHY|DEGRADED|UNHEALTHY|DEAD
    operational_failure_count_recent: int

class DecisionOption(BaseModel):
    option_id: str
    description: str  # max 512 Zeichen, Injection-Scan
    impact: str  # max 512 Zeichen
    risk_level: RiskLevel
    requires_human_approval: bool

class RoyalLogAnchor(BaseModel):
    entry_ref: str
    origin: str  # QUEEN|HUMAN
    intent: Optional[DirectiveIntent] = None
    summary: str  # max 256 Zeichen
    outcome: Optional[str] = None
    age_cycles: int

class InFlightPackageSummary(BaseModel):
    package_id: str
    zone_ref: str
    topic_ref: str
    manifest_version_started: str
    gate_mode: str
    twin_invalidated: bool = False

class StrategicBriefing(BaseModel):
    briefing_id: str  # einzige Zyklen-ID
    briefing_type: BriefingType
    manifest_version_ref: str
    atlas_macro_state: AtlasMacroState
    budget_state: BudgetState
    topics: list[TopicSummary] = []
    active_fractures: list[FractureSummary] = []
    twin_status: list[TwinStatusSummary] = []
    hardware_health: HardwareHealth
    in_flight_packages: list[InFlightPackageSummary] = []
    active_hypothesis_refs: list[str] = []
    decisions_required: list[DecisionOption] = []
    royal_log_anchor: list[RoyalLogAnchor] = []
    pending_escalations: list[str] = []
    truncation_applied: bool = False
    generated_at: str
    generated_by: str  # immer "KANZLER"
```

Regeln:
- `briefing_id` ist die einzige Zyklen-ID. `zyklus_id` ist abgeschafft.
- `generated_by` ist immer `"KANZLER"`.
- Verboten im Briefing: `security_mode`, Atlas-Hybrid-Referenzen, Roh-`metric_vector`.
- Fortschritt wird als deterministische Skalare dargestellt.
- Quarantäne-Inhalte werden als `[REDACTED:QUARANTINE]` dargestellt.

#### §6.11.5 StrategicDirective

```python
class StrategicDirective(BaseModel):
    directive_id: str
    briefing_ref: str
    intent: DirectiveIntent
    target_ref: Optional[str] = None
    parameters: DirectiveParameters  # discriminierte Union
    reason: str  # max 1024 Zeichen, Injection-Scan
    drop_soft_preferences: list[str] = []
    valid_for_cycles: int = 10
    created_at: str
```

Regeln:
- `parameters` ist eine discriminierte Union über `intent`.
- Jedes Intent-Submodell hat `intent: Literal[...]` als Discriminator.
- `directive_id` ist eindeutig (→ SL-INT-4).

#### §6.11.6 DirectiveParameters (Discriminierte Union)

```python
class InitialSweepParams(BaseModel):
    intent: Literal["INITIAL_SWEEP"] = "INITIAL_SWEEP"
    grid_spec: dict[str, Any]
    sweep_template_ref: str

class PivotParams(BaseModel):
    intent: Literal["PIVOT_DOMAIN", "PIVOT_TARGET"]
    from_topic_ref: str
    to_topic_seed: TopicSeed

class UnlockBudgetParams(BaseModel):
    intent: Literal["UNLOCK_BUDGET"] = "UNLOCK_BUDGET"
    amount_cycles: int
    purpose: str

class AbortMissionParams(BaseModel):
    intent: Literal["ABORT_MISSION"] = "ABORT_MISSION"
    reason: str

class AddDimensionHintParams(BaseModel):
    intent: Literal["ADD_DIMENSION_HINT"] = "ADD_DIMENSION_HINT"
    source_ref: str
    dimension_seed: DimensionSpec

class IncreaseDiagnosticParams(BaseModel):
    intent: Literal["INCREASE_DIAGNOSTIC"] = "INCREASE_DIAGNOSTIC"
    zone_ref: str  # ← BF-15: Korrektur von target_ref zu zone_ref
    amount: int

class CalibrateTwinParams(BaseModel):
    intent: Literal["CALIBRATE_TWIN"] = "CALIBRATE_TWIN"
    twin_ref: str

class ArchiveTopicParams(BaseModel):
    intent: Literal["ARCHIVE_TOPIC"] = "ARCHIVE_TOPIC"
    topic_ref: str

class SetPriorityParams(BaseModel):
    intent: Literal["SET_PRIORITY"] = "SET_PRIORITY"
    topic_ref: str
    priority: float

class DropSoftPreferenceParams(BaseModel):
    intent: Literal["DROP_SOFT_PREFERENCE"] = "DROP_SOFT_PREFERENCE"
    preference_ref: str

class HumanEscalationParams(BaseModel):
    intent: Literal["HUMAN_ESCALATION"] = "HUMAN_ESCALATION"
    question: str
    escalation_category: EscalationCategory

class SetResearchPhaseParams(BaseModel):
    intent: Literal["SET_RESEARCH_PHASE"] = "SET_RESEARCH_PHASE"
    target_phase: ResearchAxis
    reason: str

class NoActionParams(BaseModel):
    intent: Literal["NO_ACTION"] = "NO_ACTION"

DirectiveParameters = Union[
    InitialSweepParams, PivotParams, UnlockBudgetParams,
    AbortMissionParams, AddDimensionHintParams, IncreaseDiagnosticParams,
    CalibrateTwinParams, ArchiveTopicParams, SetPriorityParams,
    DropSoftPreferenceParams, HumanEscalationParams, SetResearchPhaseParams,
    NoActionParams
]
```

#### §6.11.7 Mission-Verträge

```python
class ManifestConstraint(BaseModel):
    constraint_id: str
    dimension_ref: Optional[str] = None  # None = missionsweite Regel
    operator: ConstraintOperator
    value: Optional[float] = None
    range: Optional[tuple[float, float]] = None
    categories: Optional[list[str]] = None
    enforcement: EnforcementType
    description: str  # max 512 Zeichen, Injection-Scan

class SoftPreference(BaseModel):
    preference_id: str
    text: str  # max 256 Zeichen, Injection-Scan

class ObjectiveSpec(BaseModel):
    metric_ref: str
    direction: Literal["MAXIMIZE", "MINIMIZE"]
    target: Optional[float] = None
    weight: float = 1.0

class ObjectiveFamilySeed(BaseModel):
    family_id: str
    objectives: list[ObjectiveSpec]
    metric_constraints: list[MetricConstraint]  # referenziert §6.10.10
    aggregation: AggregationType

class TopicSeed(BaseModel):
    seed_id: str
    objective_family_ref: str
    scope_description: str  # max 1024 Zeichen, Injection-Scan
    suggested_dimensions: list[str]

class TopicConstraintProposal(BaseModel):
    proposal_id: str
    source_topic_ref: str
    constraint: ManifestConstraint
    origin: Literal["LESSONS_LEARNED"] = "LESSONS_LEARNED"
    status: Literal["PROPOSED", "ACTIVE", "OVERRULED"] = "PROPOSED"

class DimensionSpec(BaseModel):
    dimension_id: str
    display_name: str
    value_type: DimensionValueType
    unit: Optional[str] = None
    initial_range: Optional[tuple[float, float]] = None
    initial_categories: Optional[list[str]] = None
    is_context_dimension: bool = False
    is_integrity_dim: bool = False
    parent_dimension: Optional[str] = None

class TimeService(BaseModel):
    source: str
    now_iso: str
    mission_start_iso: str

class ResearchManifest(BaseModel):
    manifest_id: str
    mission_goal: str  # max 2048 Zeichen, Injection-Scan
    hard_constraints: list[ManifestConstraint]
    soft_preferences: list[SoftPreference] = []
    objective_family_seed: ObjectiveFamilySeed
    initial_dimensions: list[DimensionSpec]
    domain: str
    valid_from: str
    valid_until: Optional[str] = None
    created_by: str  # immer Mensch
    approved_by: str  # immer Mensch
    version: str
    created_at: str
    updated_at: str
```

Regeln:
- `created_by` und `approved_by` sind immer Mensch (→ CHARTER §SR-11).
- `valid_until` wird via TimeService geprüft. Muss in der Zukunft liegen.
- Operator×Enforcement-Matrix: EXCLUSION mit `categories` ODER (`operator`+`value`); SAFETY mit (`operator`+`value`); BOUNDS mit `range` ODER (`operator`+`value`).

#### §6.11.8 Governance-Verträge

```python
class ManifestConstraintDelta(BaseModel):
    action: Literal["ADD", "REMOVE", "MODIFY"]
    constraint: Optional[ManifestConstraint] = None
    constraint_id: Optional[str] = None

class UnlockDecision(BaseModel):
    unlock_id: str
    escalation_ref: str
    zone_refs: list[str]
    conditions: str  # max 1024 Zeichen, Injection-Scan
    approved_by: str  # immer Mensch
    approved_at: str

class HumanResponseFile(BaseModel):
    response_id: str
    escalation_id: str
    decision: HumanResponseDecision
    amount_granted: Optional[int] = None
    constraints_delta: list[ManifestConstraintDelta] = []
    unlock_decision: Optional[UnlockDecision] = None
    scope_refs: list[str] = []
    free_note: str = ""  # Injection-Scan; nur Anchor
    answered_by: str  # immer Mensch
    answered_at: str

class HumanDirective(BaseModel):
    directive_id: str
    constraint_deltas: list[ManifestConstraintDelta] = []
    topic_freezes: list[str] = []
    dimension_freezes: list[str] = []
    set_research_phase: Optional[ResearchAxis] = None
    valid_for_cycles: Optional[int] = None
    note: str = ""  # Injection-Scan; nur Anchor
    created_by: str  # immer Mensch
    created_at: str
    expires_at_cycle: Optional[int] = None

class RoyalLogEntry(BaseModel):
    entry_id: str
    origin: str  # QUEEN|HUMAN
    directive_ref: Optional[str] = None
    briefing_ref: Optional[str] = None
    outcome: str
    outcome_reason: Optional[str] = None  # max 512 Zeichen
    policy_effect_ref: Optional[str] = None
    provisional: bool = False
    timestamp: str

class HumanEscalationRecord(BaseModel):
    escalation_id: str
    escalation_type: EscalationType
    payload_ref: str
    target_ref: Optional[str] = None  # für Dedup
    status: str  # PENDING|ANSWERED|TIMED_OUT
    created_at: str
    timeout_cycles: int
    answered_by: Optional[str] = None
    answer_ref: Optional[str] = None

class CapexRequest(BaseModel):
    request_id: str
    description: str  # max 512 Zeichen, Injection-Scan
    estimated_cost: str
    requires_human_approval: bool = True
    status: DimensionRequestStatus

class MissionBudget(BaseModel):
    mission_id: str
    total_cycles: int
    used_cycles: int
    reserved_cycles: int = 0
    capex_requests: list[CapexRequest] = []
    updated_at: str
```

Regeln:
- `answered_by` und `created_by` sind immer Mensch.
- `free_note` und `note` werden gescannt (Injection-Scan) und nur im Anchor verwendet.
- `provisional` wird von der DTT gesetzt bei trunkiertem Briefing.

#### §6.11.9 Forschungs-Verträge

```python
class SymptomEvent(BaseModel):
    event_id: str
    symptom_type: SymptomType
    zone_ref: Optional[str] = None
    atlas_refs: list[str] = []
    metrics_snapshot: dict[str, float] = {}
    twin_divergence_report_ref: Optional[str] = None
    created_at: str

class CapabilityRequirement(BaseModel):
    capability_id: str
    parameter_requirements: dict[str, Any] = {}

class ExpectationSpec(BaseModel):
    metric_ref: str
    direction: Literal["INCREASE", "DECREASE", "REACH"]
    threshold: Optional[float] = None
    delta: Optional[float] = None

class ScientificHypothesis(BaseModel):
    hypothesis_id: str
    hypothesis_text: str  # max 2048 Zeichen, Injection-Scan
    expected_outcome: str  # max 1024 Zeichen
    expectation_spec: Optional[ExpectationSpec] = None
    source_trigger: SymptomType
    atlas_refs: list[str] = []  # leer nur bei INITIAL_SWEEP
    zone_ref: Optional[str] = None
    required_capabilities: list[CapabilityRequirement]
    dimension_onboarding_request: Optional[DimensionOnboardingRequest] = None
    prozess_skizze: str
    confidence_estimate: float
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    created_at: str

class DimensionOnboardingRequest(BaseModel):
    request_id: str
    proposed_dimension_id: str
    display_name: str
    domain: str
    value_type: str
    unit: Optional[str] = None
    rationale: str  # max 2048 Zeichen, Injection-Scan
    source_ref: str
    source_trigger: SymptomType
    suggested_value_range: Optional[tuple[float, float]] = None
    suggested_categories: Optional[list[str]] = None
    requires_physical_actuation: bool = False
    status: DimensionRequestStatus = DimensionRequestStatus.PROPOSED
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    created_at: str

class DimensionExpansionApproval(BaseModel):
    request_ref: str
    approver: str  # immer Mensch bei physischer Nutzung
    approved_at: str
    scope: str

class CapabilityGapSignal(BaseModel):
    signal_id: str
    waypoint_ref: Optional[str] = None
    hypothesis_ref: str
    missing_capability: str
    attempted_parameters: dict[str, Any] = {}
    suggested_alternatives: list[str] = []
    requires_budget_or_hardware: bool = False
    created_at: str
```

#### §6.11.10 Report- und Registry-Verträge

```python
class CrystalSummary(BaseModel):
    crystal_node_ref: str
    objective_values: dict[str, float]
    support_confidence: float
    fracture_score: Optional[float] = None

class ReportFacts(BaseModel):
    mission_goal_ref: str
    final_objective_values: dict[str, float]
    top_crystal_summaries: list[CrystalSummary]
    rejected_hypotheses_count: int
    twin_calibration_history: list[str] = []
    safety_warnings: list[str] = []
    diagnostic_resolution_summary: list[str] = []

class FinalScientificReport(BaseModel):
    report_id: str
    topic_ref: str
    manifest_ref: str
    facts: ReportFacts
    executive_summary: str  # max 4096 Zeichen, Injection-Scan
    future_recommendations: str  # max 2048 Zeichen, Injection-Scan
    citation_refs: list[str] = []
    generated_at: str
    human_reviewed: bool = False

class CapabilityRegistryEntry(BaseModel):
    capability_id: str
    display_name: str
    status: Literal["ACTIVE", "DEPRECATED", "RETIRED"]
    parameter_schema: dict[str, Any]
    version: str

class TemplateRegistryEntry(BaseModel):
    template_id: str
    template_type: Literal["SWEEP", "DIAGNOSE"]
    domain: str
    status: Literal["ACTIVE", "DEPRECATED"]
    version: str
```

#### §6.11.11 StrategicLayerConfig

```python
class StrategicLayerConfig(BaseModel):
    # GLOBAL
    briefing_interval_cycles: int = 25
    max_briefing_chars: int = 8192
    urgent_cooldown_cycles: int = 3
    royal_log_anchor_depth: int = 3
    directive_ttl_cycles_default: int = 10
    conflict_window_cycles: int = 10
    no_action_stall_limit: int = 4
    max_consecutive_llm_failures: int = 3
    weissraum_min_coverage: float = 0.0
    bridge_edge_threshold: int = 2
    saturation_source: str = "TOPIC_STOP_CONDITION"
    full_rebuild_threshold: float = 0.85
    degraded_threshold: float = 0.60
    quarantine_threshold: float = 0.75
    budget_unlock_threshold_fraction: float = 0.10
    stagnation_budget_threshold: float = 0.80
    diagnostic_budget_default: int = 3
    diagnostic_budget_max: int = 12
    capability_gap_repeat_limit: int = 3
    max_concurrent_packages: int = 1
    max_dimension_requests_per_topic_per_cycle: int = 2
    max_dimension_requests_per_topic_total: int = 10
    bootstrap_retry_limit: int = 3
    quarantine_max_cycles: int = 30
    replication_trigger_progress: float = 0.8
    replication_cadence_cycles: int = 5
    twin_pairing_ttl_cycles: int = 10
    calibration_alert_threshold: float = 0.5
    twin_epsilon_default: float = 1e-6
    twin_abs_tolerance_default: float = 0.05
    twin_calibration_max_attempts: int = 3
    twin_drift_reduction_min: float = 0.20
    twin_late_pairing_window_cycles: int = 15
    escalation_timeout_cycles: int = 50
    escalation_reminder_interval_cycles: int = 10
    escalation_reminder_cap: int = 5
    review_reminder_interval_cycles: int = 20
    review_grace_max_cycles: int = 40
    cold_storage_window_days: int = 30
    manifest_max_chars: int = 4096
    anchor_max_chars: int = 2048
    max_total_context_chars: int = 14336
    active_hypothesis_top_n: int = 5
    in_flight_packages_max: int = 10
    top_crystal_count: int = 10
    semantic_dedup_window_cycles: int = 10
    bootstrap_exit_crystals: int = 3
    bootstrap_exit_cycles: int = 5
    exploitation_entry_whitespace: float = 0.20
    liveness_watchdog_hours: int = 12
    cycle_trigger: str = "EVENT_COUNT"
    # RESEARCH-besetzt
    exploration_weight: float = 0.5
    exploitation_weight: float = 0.5
    require_atlas_grounding: bool = True
    replicate_divergence_check: bool = True
    metric_tolerance_multiplier: float = 1.0
    replication_weight: float = 0.35
    min_confirmations: int = 2
    # RESOURCE-besetzt
    burn_rate_multiplier: float = 1.0
    physical_dispatch_allowed: bool = True
    escalation_timeout_multiplier: float = 1.0
    # GOVERNANCE-besetzt
    stall_detection_active: bool = True

class ParameterOwnershipEntry(BaseModel):
    parameter: str
    owner_axis: OwnerAxis
    default: Any
    notes: str = ""

class ParameterOwnershipMatrix(BaseModel):
    entries: list[ParameterOwnershipEntry]
    version: str
```

Regeln für StrategicLayerConfig:
- RESEARCH-besetzte Parameter werden zur Laufzeit von der ResearchAxis gesetzt.
- RESOURCE-besetzte Parameter werden zur Laufzeit von der ResourceAxis gesetzt.
- GOVERNANCE-besetzte Parameter werden zur Laufzeit von der GovernanceAxis gesetzt.
- GLOBAL-Parameter sind Konstanten und werden nicht zur Laufzeit geändert.
- Regeln lesen diese Parameter über den ControlState; sie setzen sie NICHT direkt.

---

# §7 Zustandsmaschinen

## §7.1 Questor-Zustandsmaschine (11 Zustände)

| Zustand | Bedeutung | Dauer |
| --- | --- | --- |
| IDLE | Wartet auf Envelope | Unbegrenzt |
| RECEIVING | Envelope empfangen, wird geprüft | Millisekunden |
| VALIDATING | Formale Validierung | Millisekunden |
| PLANNING | Loop-Auswahl | Sekunden |
| EXECUTING | Loop wird ausgeführt | Sekunden bis Tage |
| EVALUATING | Ergebnis prüfen | Sekunden |
| WAITING_FOR_RELEASE | Manuelle Freigabe nötig | Stunden bis Tage |
| SAFE_HOLD | Prozess sicher angehalten | Stunden |
| RECOVERING | Nach Crash: Zustand klären | Sekunden bis Minuten |
| FINALIZING | Ergebnis wird gebaut | Millisekunden |
| DONE | Ergebnis übergeben | Terminal |

Übergangstabelle (kritische Übergänge):

| Von | Nach | Auslöser |
| --- | --- | --- |
| IDLE | RECEIVING | Envelope empfangen |
| RECEIVING | VALIDATING | Envelope akzeptiert |
| RECEIVING | FINALIZING | DIRECT_PACKAGE_FORBIDDEN |
| VALIDATING | PLANNING | Validierung bestanden |
| VALIDATING | FINALIZING | PACKAGE_INVALID |
| PLANNING | EXECUTING | Plan erstellt, PolicyEvaluator GO |
| PLANNING | FINALIZING | NO_APPLICABLE_TEMPLATE / ABORT_IF_UNCLEAR |
| EXECUTING | EVALUATING | Alle Steps ausgeführt |
| EXECUTING | FINALIZING | ESTOP / Interlock / Budget erschöpft |
| EXECUTING | WAITING_FOR_RELEASE | Stufe braucht Freigabe |
| EXECUTING | SAFE_HOLD | Lease-Expiry mit SAFE_HOLD-Policy |
| EXECUTING | RECOVERING | Crash / OOM |
| EVALUATING | FINALIZING | Ziel erreicht / nicht erreichbar / Budget erschöpft |
| EVALUATING | PLANNING | Ziel nicht erreicht + Budget übrig |
| WAITING_FOR_RELEASE | EXECUTING | Freigabe erteilt |
| WAITING_FOR_RELEASE | FINALIZING | Freigabe verweigert / Timeout |
| SAFE_HOLD | RECOVERING | Questor startet neu |
| SAFE_HOLD | FINALIZING | Abbruch gewünscht |
| RECOVERING | EXECUTING | Zustand sicher, Resume möglich |
| RECOVERING | FINALIZING | RECOVERY_UNSAFE |
| FINALIZING | DONE | Ergebnis übergeben |
| DONE | IDLE | Immer |

Invarianten:

- Questor ist immer in genau EINEM Zustand
- `FINALIZING` erzeugt IMMER ein vollständiges `questor_ergebnis_paket`
- `DONE` → `IDLE` ist der einzige Rückkehrpfad
- `EXECUTING` ist der einzige Zustand mit HAL-Kommandos
- `RECOVERING` darf nur `reconcile_*` aufrufen

---

## §7.2 HAL-Slot-Zustandsmaschine

| Zustand | Bedeutung |
| --- | --- |
| FREE | Slot verfügbar |
| RESERVED | Slot reserviert |
| ACTIVE | Slot aktiv |
| ERROR | Fehlerzustand |
| ESTOP_SUSPENDED | ESTOP aktiv |
| INTERLOCKED | Hardware-Interlock aktiv |
| MAINTENANCE | Wartung |
| OFFLINE | Nicht erreichbar |

Harte Regel für `INTERLOCKED`:

- Kein `execute_command()`
- Keine automatische Reconciliation auf `FREE`
- `safe_state_verified` muss `true` sein
- `physical_reset_required` muss erfüllt sein

---

## §7.3 HAL-Prozess-Zustandsmaschine

| Zustand | Bedeutung |
| --- | --- |
| PENDING | Prozess wartet |
| RUNNING | Prozess läuft |
| PAUSED | Prozess pausiert |
| SAFE_HOLD | Prozess sicher angehalten |
| WAITING_FOR_RELEASE | Wartet auf manuelle Freigabe |
| COMPLETED | Erfolgreich abgeschlossen |
| ABORTED | Abgebrochen |
| FAULT | Fehler |
| UNKNOWN | Zustand unklar (nach Crash) |

---

## §7.4 Queue-Paket-Lebenszyklus

```text
DISPATCH → PENDING → PROCESSING → COMPLETED / FAILED → RECEIVED → ARCHIVED → CLEANED
                  ↘ DELETED (nur aus PENDING möglich)
```

---

## §7.5 Shutdown-Phasen

```text
SIGNAL_RECEIVED → DRAINING → FINALIZING → TERMINATED
```

---

## §7.6 Health-Monitoring-Zustände

| Zustand | Bedeutung |
| --- | --- |
| HEALTHY | Normal |
| DEGRADED | Einschränkungen |
| UNHEALTHY | Nicht korrekt |
| DEAD | Nicht erreichbar |

---

# §8 Idempotenz-Kanon

## §8.1 Paket-Idempotenz

```python
idempotency_key = package_id + ":" + zyklus_id + ":" + attempt_id
```

Regeln:

- `package_id` und `zyklus_id`: `^[A-Za-z0-9._-]{1,128}$`
- `attempt_id`: Integer, `0–999999`, keine führenden Nullen
- Keine Whitespace
- Maximale Länge: 264 Zeichen

Testvektoren (gültig):

```text
pkg-001:zyklus-014:0
pkg-001:zyklus-014:2
abc.def_1:zyklus-99:10
```

Testvektoren (ungültig):

```text
pkg 001:zyklus-014:2        ← Whitespace
pkg/001:zyklus-014:2        ← Ungültiges Zeichen
pkg-001:zyklus-014:02       ← Führende Null
pkg-001:zyklus-014:         ← Leer
pkg-001:zyklus-014:1000000  ← Außerhalb Bereich
```

---

## §8.2 HAL-Kommando-Idempotenz

```python
hal_idempotency_key = command_id:lease_ref:slot_id
hal_process_idempotency_key = process_id:lease_ref:slot_id
```

---

## §8.3 Deterministische ID-Erzeugung

```python
command_id  = f"cmd-{package_id}-{step_id}-{attempt_id}"
process_id  = f"proc-{package_id}-{step_id}-{attempt_id}"
questor_instance_id = f"qi-{package_id}-{sha256(f'{package_id}:{zyklus_id}:{attempt_id}')[:8]}"
```

---

# §9 Fehlermodell

## §9.1 Fehlerklassen

| Klasse | Bedeutung | Wissenschaftliches Signal? |
| --- | --- | --- |
| OPERATIONAL | Prozessfehler, Crash, Timeout, Lease-Problem | Nein |
| SCIENTIFIC | Wissenschaftliche Zielverfehlung | Ja, als Vorschlag |
| SAFETY | Sicherheitsverletzung, ESTOP | Ja, mit Sicherheitsprüfung |

---

## §9.2 Operationale Fehler (HAL)

```text
LEASE_INVALID, LEASE_EXPIRED, LEASE_REVOKED, SLOT_BUSY, SLOT_UNAVAILABLE,
ZONE_LOCK_UNAVAILABLE, COMMAND_TIMEOUT, PROCESS_TIMEOUT, DEVICE_UNAVAILABLE,
OOM, COMPUTE_OOM, CUDA_OOM, GPU_LOST, SCHEDULER_REJECTED, NODE_UNAVAILABLE,
CONTAINER_OOM_KILLED, CONTAINER_CRASHED, HAL_INTERNAL_ERROR,
DUPLICATE_COMMAND_BLOCKED, COMMAND_INVALID, PARAMETER_INVALID,
PARAMETER_SCHEMA_UNKNOWN, PARAMETER_CHECKSUM_MISMATCH,
PHYSICAL_EXECUTION_FORBIDDEN, COMPUTE_EXECUTION_FORBIDDEN,
RECOVERY_UNSAFE, RESUME_TOKEN_INVALID, STAGE_RELEASE_DENIED
```

---

## §9.3 Sicherheitsfehler (HAL)

```text
ESTOP_RECEIVED, HARDWARE_INTERLOCK_TRIGGERED, EXTERNAL_SAFETY_CHAIN_TRIGGERED,
SAFETY_LIMIT_VIOLATION, UNSAFE_SLOT_STATE, UNSAFE_ZONE_STATE,
PHYSICAL_INTERLOCK_TRIGGERED, SAFETY_RESET_REQUIRED
```

---

## §9.4 Abbruchgründe (Questor)

| Abbruchgrund | Klasse |
| --- | --- |
| PACKAGE_INVALID | OPERATIONAL |
| DIRECT_PACKAGE_FORBIDDEN | OPERATIONAL |
| GATE_MISSING | OPERATIONAL |
| NO_APPLICABLE_TEMPLATE | OPERATIONAL |
| ABORT_IF_UNCLEAR | OPERATIONAL |
| LEASE_QUEUED_TIMEOUT | OPERATIONAL |
| ROUTING_LOOP_TIMEOUT | OPERATIONAL |
| BUDGET_EXHAUSTED | OPERATIONAL |
| TARGET_NOT_REACHED | SCIENTIFIC |
| TARGET_NOT_REACHABLE | SCIENTIFIC |
| ESTOP_RECEIVED | SAFETY |
| HARDWARE_INTERLOCK_TRIGGERED | SAFETY |
| GRACEFUL_SHUTDOWN | OPERATIONAL |
| RECOVERY_UNSAFE | OPERATIONAL |

---

# §10 Enums

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


# ─────────────────────────────────────────────────────────────
# ATLAS-HYB-1.0.0 — Neue Enums
# ─────────────────────────────────────────────────────────────

class EvidenceKind(str, Enum):
    CONFIRMATION = "CONFIRMATION"
    CONTRADICTION = "CONTRADICTION"
    EXPLORATORY_COVERAGE = "EXPLORATORY_COVERAGE"
    DIAGNOSTIC_CLARIFICATION = "DIAGNOSTIC_CLARIFICATION"
    NEGATIVE_KNOWLEDGE = "NEGATIVE_KNOWLEDGE"
    POLICY_BLOCK = "POLICY_BLOCK"
    TWIN_DIVERGENCE = "TWIN_DIVERGENCE"  # ← NEU: Sim-vs-Real-Abweichung


class EvidenceClass(str, Enum):
    SIMULATION = "SIMULATION"
    SANDBOX = "SANDBOX"
    COMPUTE_EVALUATION = "COMPUTE_EVALUATION"
    PHYSICAL_EXPERIMENT = "PHYSICAL_EXPERIMENT"
    HUMAN_REVIEW = "HUMAN_REVIEW"


class ObservationDirection(str, Enum):
    CONFIRMS = "CONFIRMS"
    REFUTES = "REFUTES"
    NEUTRAL = "NEUTRAL"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"


class DimensionValueType(str, Enum):
    CONTINUOUS = "CONTINUOUS"
    DISCRETE = "DISCRETE"
    CATEGORICAL = "CATEGORICAL"
    ORDINAL = "ORDINAL"
    CONDITIONAL = "CONDITIONAL"


class NodeType(str, Enum):
    HYPOTHESIS = "HYPOTHESIS"
    CRYSTAL = "CRYSTAL"
    FRONTIER_ANCHOR = "FRONTIER_ANCHOR"
    ZONE_ANCHOR = "ZONE_ANCHOR"
    DIMENSION_REF = "DIMENSION_REF"
    DIGITAL_TWIN = "DIGITAL_TWIN"  # ← NEU: Digital-Twin-Modell-Knoten


class EdgeType(str, Enum):
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    EXTENDS = "EXTENDS"
    DEPENDS_ON = "DEPENDS_ON"
    DERIVED_FROM = "DERIVED_FROM"
    LOCATED_IN = "LOCATED_IN"
    MEASURES = "MEASURES"
    EXPLAINS = "EXPLAINS"
    DIAGNOSTIC_FOR = "DIAGNOSTIC_FOR"
    BLOCKED_BY = "BLOCKED_BY"
    NEAR_FRONTIER = "NEAR_FRONTIER"


class ZoneHealthState(str, Enum):
    UNEXPLORED = "UNEXPLORED"
    EXPLORED_INCONCLUSIVE = "EXPLORED_INCONCLUSIVE"
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    LOCKED = "LOCKED"


class DiagnosticOutcomeType(str, Enum):
    CONFIRMS_CONTRADICTION = "CONFIRMS_CONTRADICTION"
    EXPLAINS_CONTRADICTION = "EXPLAINS_CONTRADICTION"
    RESOLVES_CONTRADICTION = "RESOLVES_CONTRADICTION"
    INCONCLUSIVE = "INCONCLUSIVE"
    TWIN_DRIFT_CONFIRMED = "TWIN_DRIFT_CONFIRMED"  # ← NEU: Twin weicht ab
    TWIN_CALIBRATED = "TWIN_CALIBRATED"            # ← NEU: Twin neu kalibriert


class FrontierType(str, Enum):
    WEISSRAUM = "WEISSRAUM"
    CONTRADICTION_GAP = "CONTRADICTION_GAP"
    BRIDGE_FRONTIER = "BRIDGE_FRONTIER"
    DIAGNOSTIC_FRONTIER = "DIAGNOSTIC_FRONTIER"
    LOW_COST_FRONTIER = "LOW_COST_FRONTIER"
    DEEP_UNCERTAIN = "DEEP_UNCERTAIN"


class ResearchTopicState(str, Enum):
    PROPOSED = "PROPOSED"
    ACTIVE = "ACTIVE"
    SATURATED = "SATURATED"
    BLOCKED = "BLOCKED"
    ARCHIVED = "ARCHIVED"


class ExpiryPolicy(str, Enum):
    DECAY = "DECAY"
    EXPIRE = "EXPIRE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SafetyStatus(str, Enum):
    CLEAR = "CLEAR"
    RESTRICTED = "RESTRICTED"
    BLOCKED = "BLOCKED"


class BudgetClass(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ScopeType(str, Enum):
    NODE = "NODE"
    SUBZONE = "SUBZONE"
    ZONE = "ZONE"
    DIMENSION = "DIMENSION"
    REGION = "REGION"


class PriorityMode(str, Enum):
    WEIGHTED_SUM = "WEIGHTED_SUM"
    PARETO = "PARETO"
    LEXICOGRAPHIC = "LEXICOGRAPHIC"


class MetricDirection(str, Enum):
    MAXIMIZE = "MAXIMIZE"
    MINIMIZE = "MINIMIZE"


class ConstraintOperator(str, Enum):
    GE = "GE"
    LE = "LE"
    GT = "GT"
    LT = "LT"
    EQ = "EQ"
    RANGE = "RANGE"


class StopMetric(str, Enum):
    FRONTIER_SCORE = "FRONTIER_SCORE"
    EVIDENCE_MASS = "EVIDENCE_MASS"
    FRACTURE_SCORE = "FRACTURE_SCORE"
    BUDGET_USED = "BUDGET_USED"
    TIME_ELAPSED = "TIME_ELAPSED"
    SATURATION_CYCLES = "SATURATION_CYCLES"


class StopOperator(str, Enum):
    BELOW = "BELOW"
    ABOVE = "ABOVE"
    EQUALS = "EQUALS"
    REACHED = "REACHED"


class WaypointStatus(str, Enum):
    PLATZIERT = "PLATZIERT"
    AUSGEFUEHRT = "AUSGEFUEHRT"
    VERWORFEN = "VERWORFEN"


# ─────────────────────────────────────────────────────────────
# STRAT-1.0.0 — Strategic Layer Enums
# ─────────────────────────────────────────────────────────────

class DirectiveIntent(str, Enum):
    NO_ACTION = "NO_ACTION"
    INITIAL_SWEEP = "INITIAL_SWEEP"
    PIVOT_DOMAIN = "PIVOT_DOMAIN"
    PIVOT_TARGET = "PIVOT_TARGET"
    UNLOCK_BUDGET = "UNLOCK_BUDGET"
    ABORT_MISSION = "ABORT_MISSION"
    ADD_DIMENSION_HINT = "ADD_DIMENSION_HINT"
    INCREASE_DIAGNOSTIC = "INCREASE_DIAGNOSTIC"
    CALIBRATE_TWIN = "CALIBRATE_TWIN"
    ARCHIVE_TOPIC = "ARCHIVE_TOPIC"
    SET_PRIORITY = "SET_PRIORITY"
    DROP_SOFT_PREFERENCE = "DROP_SOFT_PREFERENCE"
    HUMAN_ESCALATION = "HUMAN_ESCALATION"
    SET_RESEARCH_PHASE = "SET_RESEARCH_PHASE"

class BriefingType(str, Enum):
    BOOTSTRAP = "BOOTSTRAP"
    PERIODIC = "PERIODIC"
    URGENT = "URGENT"
    FINAL = "FINAL"

class SymptomType(str, Enum):
    INITIAL_SWEEP = "INITIAL_SWEEP"
    WEISSRAUM = "WEISSRAUM"
    FRACTURE_GAP = "FRACTURE_GAP"
    SATURATION = "SATURATION"
    BRIDGE_OPP = "BRIDGE_OPP"
    TWIN_DRIFT = "TWIN_DRIFT"
    CAPABILITY_GAP_FEEDBACK = "CAPABILITY_GAP_FEEDBACK"
    DIMENSION_GAP = "DIMENSION_GAP"
    REPLICATE_DIVERGENCE = "REPLICATE_DIVERGENCE"
    QUARANTINE_BLOCK = "QUARANTINE_BLOCK"

class EscalationType(str, Enum):
    BUDGET = "BUDGET"
    DIMENSION_PHYSICAL = "DIMENSION_PHYSICAL"
    ABORT_CONFIRM = "ABORT_CONFIRM"
    SAFETY_EVENT = "SAFETY_EVENT"
    DEADLOCK = "DEADLOCK"
    CAPEX = "CAPEX"
    MANIFEST_EXPIRED = "MANIFEST_EXPIRED"
    QUARANTINE_EXIT = "QUARANTINE_EXIT"
    LLM_FAILURE = "LLM_FAILURE"
    STRATEGIC_QUESTION = "STRATEGIC_QUESTION"
    TWIN_UNCALIBRATABLE = "TWIN_UNCALIBRATABLE"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    CAPABILITY_DELIVERY = "CAPABILITY_DELIVERY"
    TEMPLATE_GAP = "TEMPLATE_GAP"

class EscalationCategory(str, Enum):
    DEADLOCK = "DEADLOCK"
    STRATEGIC_QUESTION = "STRATEGIC_QUESTION"
    RISK_ACCEPTANCE = "RISK_ACCEPTANCE"

class EnforcementType(str, Enum):
    EXCLUSION = "EXCLUSION"
    SAFETY = "SAFETY"
    BOUNDS = "BOUNDS"

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class AggregationType(str, Enum):
    WEIGHTED_SUM = "WEIGHTED_SUM"
    PARETO = "PARETO"

class DimensionRequestStatus(str, Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"
    COOLDOWN = "COOLDOWN"

class HypothesisStatus(str, Enum):
    PROPOSED = "PROPOSED"
    ACTIVE = "ACTIVE"
    CONFIRMED = "CONFIRMED"
    REFUTED = "REFUTED"
    ARCHIVED = "ARCHIVED"

class HumanResponseDecision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    PARTIAL = "PARTIAL"
    DEFER = "DEFER"

# ── 4-Achsen-Enums (DESIGN-FESTLEGUNG) ──

class SafetyAxis(str, Enum):
    NORMAL = "NORMAL"
    SAFE_MODE = "SAFE_MODE"
    ESTOP_LOCKED = "ESTOP_LOCKED"

class ResourceAxis(str, Enum):
    FUNDED = "FUNDED"
    INCUBATING = "INCUBATING"
    PHYSICAL_WAIT = "PHYSICAL_WAIT"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"

class ResearchAxis(str, Enum):
    BOOTSTRAP = "BOOTSTRAP"
    EXPLORATION = "EXPLORATION"
    EXPLOITATION = "EXPLOITATION"
    SATURATION = "SATURATION"

class GovernanceAxis(str, Enum):
    AUTONOMOUS = "AUTONOMOUS"
    AWAITING_HUMAN = "AWAITING_HUMAN"
    CONFLICT_LOCK = "CONFLICT_LOCK"

class OwnerAxis(str, Enum):
    GLOBAL = "GLOBAL"
    SAFETY = "SAFETY"
    RESOURCE = "RESOURCE"
    RESEARCH = "RESEARCH"
    GOVERNANCE = "GOVERNANCE"
```

---

# §11 Korrekturen gegenüber alten Dokumenten

| # | Korrektur | Quelle (alt) | Status |
| --- | --- | --- | --- |
| 1 | `QuestorSpec.allowed_capabilities`: `list[Capability]` → `list[str]` | v2.4.0 §7.2, Capability-Registry §3.5 | ✅ Eingearbeitet |
| 2 | `planning_hints` als optionales Feld in `ResearchPackage` | Sanitization P5, QuestCompass §18 | ✅ Eingearbeitet |
| 3 | `LoopTemplate.is_recovery_template: bool` (Default: false) | Security-Mode §4.2, Q1 | ✅ Eingearbeitet |
| 4 | `LoopStep.capability`: Pflicht bei HAL_COMMAND/PROCESS_COMMAND | Capability-Registry Q7 | ✅ Eingearbeitet |
| 5 | `health_alert_count` / `health_restart_count` in OperationalMetrics | Health-Monitoring Q6 | ✅ Eingearbeitet |
| 6 | `GateRecord.allowed_security_modes: list[str]` | Security-Mode §3 | ✅ Eingearbeitet |
| 7 | `TrailPolicy` als vollständiger Vertrag | Trail-Map §3.1 | ✅ Eingearbeitet |
| 8 | Atlas-Hybrid-Verträge als optionale Erweiterung eingeführt | ATLAS-HYB-1.0.0 | ✅ Eingearbeitet |
| 9 | Strategic-Layer-Verträge als §6.11 eingeführt | GREMIUM_UNIFIED_SPEC v1.0.0 | ✅ Eingearbeitet |
| 10 | `DirectiveIntent` Enum mit 14 Werten definiert | Unified Spec §6 | ✅ Eingearbeitet |
| 11 | 4-Achsen-Enums (SafetyAxis, ResourceAxis, ResearchAxis, GovernanceAxis) definiert | Unified Spec §6, §38 | ✅ Eingearbeitet |
| 12 | `IncreaseDiagnosticParams.zone_ref` statt `target_ref` (BF-15) | DT9-F-02 | ✅ Eingearbeitet |
| 13 | `DirectiveParameters` als discriminierte Union über `intent` definiert | Unified Spec §10 | ✅ Eingearbeitet |
| 14 | Digital-Twin-Verträge als §6.10.19–§6.10.20 eingeführt | DIGITAL-TWIN-SEM-1.0.0 | ✅ Eingearbeitet |
| 15 | `NodeType.DIGITAL_TWIN` als neuer Knotentyp eingeführt | DIGITAL-TWIN-SEM-1.0.0 | ✅ Eingearbeitet |
| 16 | `EvidenceKind.TWIN_DIVERGENCE` als neue Evidenzart eingeführt | DIGITAL-TWIN-SEM-1.0.0 | ✅ Eingearbeitet |
| 17 | `DiagnosticOutcomeType.TWIN_DRIFT_CONFIRMED` und `TWIN_CALIBRATED` eingeführt | DIGITAL-TWIN-SEM-1.0.0 | ✅ Eingearbeitet |
| 18 | `ResearchPackage.digital_twin_ref` als Pass-Through-Feld eingeführt | DIGITAL-TWIN-SEM-1.0.0 | ✅ Eingearbeitet |

---

# §12 Dokumentenhierarchie

Dieses Dokument steht in der Schicht `foundation/` und wird von allen `specs/`- und `ops/`-Dokumenten referenziert.

Regel: Änderungen an Verträgen in diesem Dokument erfordern eine Versionsänderung und eine Überprüfung aller referenzierenden Dokumente.

Neu referenziert durch:
- `specs/GREMIUM_STRATEGY.md` für Strategic-Layer-Regeln und Achsen-Steuerung
- `specs/GREMIUM.md` für Pipeline-Mechanik (9-Stufen-Pipeline)
- `specs/GREMIUM.md` §6.14 für Digital-Twin-Loop (Pipeline-Integration)
- `specs/GREMIUM_STRATEGY.md` §14 für Digital-Twin-Loop (Strategische Steuerung, SL-TWIN-1..11)