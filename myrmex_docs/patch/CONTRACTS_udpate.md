# 📜 CONTRACTS.md v1.2.0 — ÄNDERUNGSANWEISUNG (Schritt 1)

**Aktion:** Die folgenden Änderungen sind in die bestehende `foundation/CONTRACTS.md` (v1.1.0-atlas-hyb.1) einzuarbeiten. Das Ergebnis ist Version **1.2.0-strat.1**.

---

## ÄNDERUNG 1: Kopfzeile

**ERSETZE** die bestehende Kopfzeile:

| Feld | Wert |
|---|---|
| Dateiname | foundation/CONTRACTS.md |
| Version | **1.2.0-strat.1** |
| Status | ÄNDERUNGSANTRAG STRAT-1.0.0 — nach Freigabe BINDEND |
| System | MYRMEX v2.4.0 + Questor v0.2.3 + HAL v0.2.0 + Gremium Strategic Layer v1.0.2 |
| Geltung | Single Source of Truth für alle Pydantic-Modelle und Zustandsmaschinen |
| Datum | 21. August 2026 |

---

## ÄNDERUNG 2: Neuer Abschnitt §0.2 (nach §0.1 einfügen)

**NEU — nach §0.1 einfügen:**

### §0.2 Änderungsantrag STRAT-1.0.0 — Strategic-Layer-Integration

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

## ÄNDERUNG 3: Neuer Abschnitt §6.11 (nach §6.10.18 einfügen)

**NEU — nach §6.10.18 AtlasHybridConfig einfügen:**

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

## ÄNDERUNG 4: Neue Enums in §10 einfügen

**NEU — am Ende von §10, nach `WaypointStatus`, einfügen:**

```python
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

## ÄNDERUNG 5: §11 Korrekturen erweitern

**ERGÄNZE — am Ende der Tabelle in §11:**

| # | Korrektur | Quelle (alt) | Status |
|---|---|---|---|
| 9 | Strategic-Layer-Verträge als §6.11 eingeführt | GREMIUM_UNIFIED_SPEC v1.0.0 | ✅ Eingearbeitet |
| 10 | `DirectiveIntent` Enum mit 14 Werten definiert | Unified Spec §6 | ✅ Eingearbeitet |
| 11 | 4-Achsen-Enums (SafetyAxis, ResourceAxis, ResearchAxis, GovernanceAxis) definiert | Unified Spec §6, §38 | ✅ Eingearbeitet |
| 12 | `IncreaseDiagnosticParams.zone_ref` statt `target_ref` (BF-15) | DT9-F-02 | ✅ Eingearbeitet |
| 13 | `DirectiveParameters` als discriminierte Union über `intent` definiert | Unified Spec §10 | ✅ Eingearbeitet |

---

## ÄNDERUNG 6: §12 Dokumentenhierarchie aktualisieren

**ERSETZE** den bestehenden Text in §12:

### §12 Dokumentenhierarchie

Dieses Dokument steht in der Schicht `foundation/` und wird von allen `specs/`- und `ops/`-Dokumenten referenziert.

Regel: Änderungen an Verträgen in diesem Dokument erfordern eine Versionsänderung und eine Überprüfung aller referenzierenden Dokumente.

Neu referenziert durch:
- `specs/GREMIUM_STRATEGY.md` für Strategic-Layer-Regeln und Achsen-Steuerung
- `specs/GREMIUM.md` für Pipeline-Mechanik (9-Stufen-Pipeline)

---

## ZUSAMMENFASSUNG DER ÄNDERUNGEN

| Änderung | Ziel | Aktion | Umfang |
|---|---|---|---|
| 1 | Kopfzeile | ERSETZE | 6 Zeilen |
| 2 | §0.2 | NEU | ~20 Zeilen |
| 3 | §6.11 | NEU | ~450 Zeilen |
| 4 | §10 Enums | ERGÄNZE | ~120 Zeilen |
| 5 | §11 Korrekturen | ERGÄNZE | 5 Zeilen |
| 6 | §12 Hierarchie | ERSETZE | ~8 Zeilen |
| **Gesamt** | | | **~609 Zeilen** |

**Betroffene Abschnitte:** Kopfzeile, §0.2, §6.11, §10, §11, §12.
**Nicht betroffen:** §1–§5, §6.1–§6.9, §6.10.1–§6.10.18, §7–§9.

---

## NACHWEIS: CHARTER-KONFORMITÄT

| CHARTER-Regel | Umsetzung |
|---|---|
| SR-04 | Questor und HAL kennen Strategic-Layer-Verträge nicht. Keine Schreibrechte. |
| SR-08 | RoyalLog/Briefings/Direktiven sind operational. Keine wissenschaftlichen Signale. |
| SR-11 | `created_by` und `approved_by` sind immer Mensch. |
| SR-13 | Königin und Vordenker schlagen vor; Kanzler entscheidet deterministisch. |
| SR-24 | Briefing-Whitelist; Fortschritt als Skalare; keine Hybrid-Referenzen. |

_____________________________________________________________________________________________________


# 📜 CONTRACTS.md v1.2.1 — NACHTRAG DIGITAL-TWIN-SEM-1.0.0

**Aktion:** Die folgenden Änderungen sind in die bestehende `foundation/CONTRACTS.md` (v1.2.0-strat.1) einzuarbeiten. Das Ergebnis ist Version **1.2.1-twin.1**.

---

## ÄNDERUNG 1: Kopfzeile

**ERSETZE** die bestehende Kopfzeile:

| Feld | Wert |
|---|---|
| Dateiname | foundation/CONTRACTS.md |
| Version | **1.2.1-twin.1** |
| Status | ÄNDERUNGSANTRAG DIGITAL-TWIN-SEM-1.0.0 — nach Freigabe BINDEND |
| System | MYRMEX v2.4.0 + Questor v0.2.3 + HAL v0.2.0 + Gremium Strategic Layer v1.0.0 |
| Geltung | Single Source of Truth für alle Pydantic-Modelle und Zustandsmaschinen |
| Datum | 21. August 2026 |

---

## ÄNDERUNG 2: Neuer Abschnitt §0.3 (nach §0.2 einfügen)

**NEU — nach §0.2 einfügen:**

### §0.3 Änderungsantrag DIGITAL-TWIN-SEM-1.0.0 — Digital-Twin-Verträge

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

## ÄNDERUNG 3: Enum-Erweiterungen in §10

**ERGÄNZE** die bestehenden Enums in §10 um neue Werte:

### NodeType — Erweiterung

```python
class NodeType(str, Enum):
    HYPOTHESIS = "HYPOTHESIS"
    CRYSTAL = "CRYSTAL"
    FRONTIER_ANCHOR = "FRONTIER_ANCHOR"
    ZONE_ANCHOR = "ZONE_ANCHOR"
    DIMENSION_REF = "DIMENSION_REF"
    DIGITAL_TWIN = "DIGITAL_TWIN"  # ← NEU: Digital-Twin-Modell-Knoten
```

### EvidenceKind — Erweiterung

```python
class EvidenceKind(str, Enum):
    CONFIRMATION = "CONFIRMATION"
    CONTRADICTION = "CONTRADICTION"
    EXPLORATORY_COVERAGE = "EXPLORATORY_COVERAGE"
    DIAGNOSTIC_CLARIFICATION = "DIAGNOSTIC_CLARIFICATION"
    NEGATIVE_KNOWLEDGE = "NEGATIVE_KNOWLEDGE"
    POLICY_BLOCK = "POLICY_BLOCK"
    TWIN_DIVERGENCE = "TWIN_DIVERGENCE"  # ← NEU: Sim-vs-Real-Abweichung
```

### DiagnosticOutcomeType — Erweiterung

```python
class DiagnosticOutcomeType(str, Enum):
    CONFIRMS_CONTRADICTION = "CONFIRMS_CONTRADICTION"
    EXPLAINS_CONTRADICTION = "EXPLAINS_CONTRADICTION"
    RESOLVES_CONTRADICTION = "RESOLVES_CONTRADICTION"
    INCONCLUSIVE = "INCONCLUSIVE"
    TWIN_DRIFT_CONFIRMED = "TWIN_DRIFT_CONFIRMED"  # ← NEU: Twin weicht ab
    TWIN_CALIBRATED = "TWIN_CALIBRATED"            # ← NEU: Twin neu kalibriert
```

---

## ÄNDERUNG 4: Neuer Abschnitt §6.10.19 (nach §6.10.18 einfügen)

**NEU — nach §6.10.18 AtlasHybridConfig einfügen:**

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
    divergence_threshold: float = 0.10   # Ab wann gilt der Twin als "drifted"? (0.0–1.0)
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

## ÄNDERUNG 5: Neuer Abschnitt §6.10.20 (nach §6.10.19 einfügen)

**NEU — nach §6.10.19 einfügen:**

### §6.10.20 TwinDivergenceReport

```python
class TwinDivergenceReport(BaseModel):
    divergence_id: str
    twin_node_ref: str
    sim_kristall_ref: str      # Kristallkandidat mit evidence_class = SIMULATION
    real_kristall_ref: str     # Kristallkandidat mit evidence_class = PHYSICAL_EXPERIMENT
    # Abweichung pro Metrik im metric_vector (z.B. {"yield": 0.15, "purity": 0.02})
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

## ÄNDERUNG 6: Erweiterung bestehender Verträge

### §1.1 ResearchPackage — Erweiterung

**ERGÄNZE** am Ende der Feldliste von `ResearchPackage`:

```python
class ResearchPackage(BaseModel):
    # ... bestehende Felder ...
    # ── DIGITAL-TWIN-SEM-1.0.0: Neues optionales Feld ──
    digital_twin_ref: Optional[str] = None
```

Regeln:
- `digital_twin_ref` ist Pass-Through für Questor (wie `atlas_expectation_ref`).
- Questor darf `digital_twin_ref` nicht als LLM-Kontext verwenden.
- Questor darf `digital_twin_ref` nicht verwenden, um direkt auf den Atlas zuzugreifen.
- `digital_twin_ref` wird in die Sanitization-Blocklist aufgenommen (→ QUESTOR.md §12.2a).

### §6.10.3 ReproducibilityContext — Erweiterung

**ERGÄNZE** am Ende der Feldliste von `ReproducibilityContext`:

```python
class ReproducibilityContext(BaseModel):
    # ... bestehende Felder ...
    # ── DIGITAL-TWIN-SEM-1.0.0: Neue optionale Felder ──
    digital_twin_ref: Optional[str] = None
    twin_model_version: Optional[str] = None
```

### §6.10.8 AtlasNode — Erweiterung

**ERGÄNZE** am Ende der Feldliste von `AtlasNode`:

```python
class AtlasNode(BaseModel):
    # ... bestehende Felder ...
    # ── DIGITAL-TWIN-SEM-1.0.0: Neues optionales Feld ──
    twin_model: Optional[DigitalTwinModel] = None
```

Regeln:
- `twin_model` ist nur relevant, wenn `node_type = DIGITAL_TWIN`.
- Bei anderen `node_type`-Werten muss `twin_model = None` sein.

### §6.10.11 DiagnosticResolution — Erweiterung

**ERGÄNZE** am Ende der Feldliste von `DiagnosticResolution`:

```python
class DiagnosticResolution(BaseModel):
    # ... bestehende Felder ...
    # ── DIGITAL-TWIN-SEM-1.0.0: Neues optionales Feld ──
    twin_divergence_report_ref: Optional[str] = None
```

---

## ÄNDERUNG 7: §11 Korrekturen erweitern

**ERGÄNZE** am Ende der Tabelle in §11:

| # | Korrektur | Quelle (alt) | Status |
|---|---|---|---|
| 14 | Digital-Twin-Verträge als §6.10.19–§6.10.20 eingeführt | DIGITAL-TWIN-SEM-1.0.0 | ✅ Eingearbeitet |
| 15 | `NodeType.DIGITAL_TWIN` als neuer Knotentyp eingeführt | DIGITAL-TWIN-SEM-1.0.0 | ✅ Eingearbeitet |
| 16 | `EvidenceKind.TWIN_DIVERGENCE` als neue Evidenzart eingeführt | DIGITAL-TWIN-SEM-1.0.0 | ✅ Eingearbeitet |
| 17 | `DiagnosticOutcomeType.TWIN_DRIFT_CONFIRMED` und `TWIN_CALIBRATED` eingeführt | DIGITAL-TWIN-SEM-1.0.0 | ✅ Eingearbeitet |
| 18 | `ResearchPackage.digital_twin_ref` als Pass-Through-Feld eingeführt | DIGITAL-TWIN-SEM-1.0.0 | ✅ Eingearbeitet |

---

## ÄNDERUNG 8: §12 Dokumentenhierarchie aktualisieren

**ERGÄNZE** am Ende von §12:

Neu referenziert durch:
- `specs/GREMIUM.md` §6.14 für Digital-Twin-Loop (Pipeline-Integration)
- `specs/GREMIUM_STRATEGY.md` §14 für Digital-Twin-Loop (Strategische Steuerung, SL-TWIN-1..11)

---

## ZUSAMMENFASSUNG DER ÄNDERUNGEN

| Änderung | Ziel | Aktion | Umfang |
|---|---|---|---|
| 1 | Kopfzeile | ERSETZE | 6 Zeilen |
| 2 | §0.3 | NEU | ~18 Zeilen |
| 3 | §10 Enums | ERGÄNZE | ~8 Zeilen |
| 4 | §6.10.19 | NEU | ~30 Zeilen |
| 5 | §6.10.20 | NEU | ~25 Zeilen |
| 6 | §1.1, §6.10.3, §6.10.8, §6.10.11 | ERGÄNZE | ~20 Zeilen |
| 7 | §11 Korrekturen | ERGÄNZE | 5 Zeilen |
| 8 | §12 Hierarchie | ERGÄNZE | ~3 Zeilen |
| **Gesamt** | | | **~115 Zeilen** |

---

## NACHWEIS: CHARTER-KONFORMITÄT

| CHARTER-Regel | Umsetzung |
|---|---|
| SR-04 | Questor schreibt nicht in Atlas. `digital_twin_ref` ist Pass-Through. |
| SR-08 | Sim-Evidenz bestätigt keine physischen Kristalle. Evidence-Class-Transferregel bleibt. |
| SR-13 | Kalibrierung wird nicht durch LLM entschieden. Deterministischer Pfad. |
| SR-24 | `digital_twin_ref` wird in die Sanitization-Blocklist aufgenommen. |