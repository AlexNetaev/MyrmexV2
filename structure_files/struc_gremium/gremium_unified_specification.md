# 🏛️ GREMIUM UNIFIED SPECIFICATION — COGNITIVE OBSERVATORY

| Feld | Wert |
|------|------|
| Version | 1.0.0 (final konsolidiert) |
| Status | EIGENSTÄNDIG LAUFFÄHIG (ersetzt die modulare Aufteilung) |
| Basis | Konsolidierung aus v0.2.0 + v0.3.0 + Achsen-Architektur (Option 2) + alle Patches |
| Baut auf | CHARTER 1.0.0, CONTRACTS 1.1.0-atlas-hyb.1, DIGITAL-TWIN-SEM-1.0.0 |
| Konfliktregel | CHARTER > CONTRACTS > dieses Dokument (intern: SAFETY-Regeln absolut) |
| Testgrundlage | 6 Dry-Test-Kampagnen (DT4..DT7), Fund-rate 0.98 → 0.014 |

---

## §0 Zweck, Leseregel, Geltung

### §0.1 Zweck
Dieses Dokument definiert die strategische Kognitionsschicht des Gremiums
(„Cognitive Observatory"): ein System, das über Wochen autonom forschen kann —
drift-frei, CHARTER-konform, mit deterministischen Endentscheidungen und
definierten menschlichen Eingriffspunkten.

### §0.2 Leseregel und Konfliktregel
- CHARTER > CONTRACTS > dieses Dokument.
- Innerhalb dieses Dokuments: SAFETY-Regeln (SL-SAF, SR-05, SR-19) sind absolut
  und überstimmen alle anderen Regeln.
- Die 4-Achsen-Steuerung (§38..§43) ist eine DESIGN-FESTLEGUNG dieser
  Konsolidierung; wo sie vom Quell-SystemMode (v0.3.0 §9.1) abweicht, ist sie
  als solche markiert.

### §0.3 Logische Modul-Struktur (in dieser einen Datei)
| Modul | Abschnitte | Zweck |
|---|---|---|
| CORE | §1..§5 | Invarianten, Grunddefinitionen, Rollen, Anchor |
| CONTRACTS | §6..§14 | Datenverträge, Enums, Config |
| RULES | §15..§37 | Mechanik, Validierung, Zustandsmaschinen |
| CONTROL | §38..§43 | 4 Achsen, ControlState, atomare Transitionen |
| INDEX | §44..§45 | Fund-Register, Change-Log |

### §0.4 Ehrlichkeitshinweis (bindend für Tests)
- Die Achsen-Architektur ist eine Design-Festlegung, keine Quell-Ableitung.
- Die Severity-Ordnung (§43.1) und Closure-Regeln (§43.2) sind bewusste Wahlen.
- Die Dry-Tests der Entwurfsphase waren selbst-generiert; reale Validierung
  steht aus (§29 Restrisiken).

---

# MODUL CORE

## §1 Grunddefinitionen (SL-DEF-1..5)

**SL-DEF-1 Strategischer Zyklus:** 1 Zyklus = 1 abgeschlossener Regelkreis:
StrategicBriefing erzeugt → StrategicDirective empfangen → Validierung →
Policy-Wirkung. Alle `*_cycles` beziehen sich darauf.

**SL-DEF-2 Weißraum:** Eine Region ist Weißraum, wenn ihre Zone `UNEXPLORED`
ist oder `EXPLORED_INCONCLUSIVE` mit `evidence_mass == 0`.

**SL-DEF-3 Pipeline-Takt:** ereignisgetrieben; jedes verarbeitete Ergebnis
schreitet fort. Treibt Archivar/Kartograph/Atlas.

**SL-DEF-4 Strategie-Zyklus:** der Briefing-Regelkreis (SL-DEF-1).
`briefing_id` ist die einzige Zyklen-ID (`zyklus_id` abgeschafft).
Auslösung durch `cycle_trigger ∈ {TIME, EVENT_COUNT, MANUAL}`.

**SL-DEF-5 TimeService:** Alle `*_days`-Parameter und Timeout-Auswertungen
nutzen `TimeService`. Alle `*_cycles` nutzen den Strategie-Zyklus. Keine
Vermischung.

## §2 Rollen und Zugriffsregeln (SL-ACC-1..4)

| Rolle | Schicht | LLM | Funktion | Achsen-Interaktion |
|---|---|---|---|---|
| 👑 Königin | 5 | Ja (stateless) | Vision, Pivot, Budget-Vorschläge | liest ControlState via Briefing |
| 🏛️ Kanzler | 4 | Nein | Briefing, Validierung, Policy, RoyalLog, Achsen-Verwaltung | liest+schreibt ControlState |
| 🧠 Vordenker | 4 | Ja (grounded) | Hypothesen, Dimensions-Vorschläge | liest via SymptomEvents |
| 🧭 Lotse | 4 | Nein | Wegmarken, Capability-Prüfung | liest für Capability-Checks |
| 📦 Quartiermeister | 4 | Nein | Paketbau, Manifest-/Twin-Checks | liest für Paketbau |
| ⚖️ Sicherheitsrat | 4 | Seher advisor | Gate | liest SafetyAxis |
| 🗺️ Kartograph | 4 | Nein | Atlas, Symptome, Twin-Divergenz | liest für Symptom-Erzeugung |
| 📚 Archivar | 4 | Nein | Wissensaufnahme, Sanitization | liest für Sanitization |
| 🧭 Questor | 2 | intern | Ausführung (unverändert) | keine |

- **SL-ACC-1:** Alle Kommunikation über Blackboard-Artefakte (§33.5). Keine
  direkten Aufrufe. (CHARTER §2)
- **SL-ACC-2:** Die Königin liest den Atlas nicht direkt; ihr einziger Zugang
  ist das StrategicBriefing.
- **SL-ACC-3:** Der Vordenker liest Atlas-Topologie nur lesend als kuratierte
  Ausschnitte; er schreibt nie in den Atlas.
- **SL-ACC-4:** Questor und HAL bleiben unverändert; sie kennen keine
  strategischen Verträge.

## §3 Constitutional Anchor Protocol (SL-ANCHOR-1..4)

Jeder Königin-LLM-Aufruf erhält exakt drei Kontextblöcke (SL-ANCHOR-1):
1. **CONSTITUTIONAL MEMORY** (invariant): mission_goal, hard_constraints,
   soft_preferences, Verbotene Aktionen, Output-Schema.
2. **STATELESS BRIEFING** (dynamisch): aggregierter Zustand, Budget, Fractures,
   Twin-Status, DecisionsRequired — kein security_mode, keine Hybrid-Referenzen,
   kein Roh-metric_vector.
3. **ANCHOR** (Kontinuität): zuerst aktive HUMAN_OVERRIDE-Einträge, dann die
   letzten `royal_log_anchor_depth` (=3) eigenen Direktiven mit Outcome.

- **SL-ANCHOR-2:** Kein persistenter Gesprächsverlauf. Jeder Aufruf frisch.
- **SL-ANCHOR-3:** Menschliche Weisungen im Anchor überschreiben alle
  Königin-Direktiven (expliziter Hinweis im Anchor).
- **SL-ANCHOR-4:** LLM-Fehler/Timeout → Policy bleibt unverändert, Audit, kein
  erweiterter Retry. Nach `max_consecutive_llm_failures` → Eskalation.

## §4 Architektur-Überblick

```
MENSCH (SR-11: nie überstimmt)
  │ setzt ResearchManifest, beantwortet Eskalationen, SAFE_MODE
  ▼
SCHICHT 5: 👑 KÖNIGIN (stateless LLM)
  IN: Manifest + Briefing + Anchor   OUT: StrategicDirective
  ▼
SCHICHT 4: 🏛️ GREMIUM
  KANZLER (deterministisch): Briefing · Validator (10 Stufen) · DTT ·
    RoyalLog · Budget · Dimension-/Eskalations-Governance · SAFETY-RESPONSE ·
    ControlState-Verwaltung (Achsen-Transitionen, SL-AX-ATOMIC)
  KARTOGRAPH → VORDENKER → PRE-FILTER → LOTSE → QUARTIERMEISTER →
    SICHERHEITSRAT → DISPATCH → QUESTOR → ARCHIVAR → KARTOGRAPH → ATLAS
```

## §5 Kern-Patterns
- **Stateless Director** (§5.1): Königin zustandslos.
- **Deterministic Gatekeeper** (§5.2): Kanzler rein deterministisch (SL-GATE-1).
- **Topology-Grounded Hypothesis Engine** (§5.3): Vordenker nur via SymptomEvents.
- **Digital-Twin-Loop** (§5.4): gemäß DIGITAL-TWIN-SEM, gehärtet (§23).
- **Orthogonal Control Axes** (§5.5, DESIGN): 4 Achsen (§38), ControlState-Tupel.

---

# MODUL CONTRACTS

## §6 Enums (konsolidiert)

```python
class DirectiveIntent(str, Enum):
    NO_ACTION="NO_ACTION"; INITIAL_SWEEP="INITIAL_SWEEP"
    PIVOT_DOMAIN="PIVOT_DOMAIN"; PIVOT_TARGET="PIVOT_TARGET"
    UNLOCK_BUDGET="UNLOCK_BUDGET"; ABORT_MISSION="ABORT_MISSION"
    ADD_DIMENSION_HINT="ADD_DIMENSION_HINT"; INCREASE_DIAGNOSTIC="INCREASE_DIAGNOSTIC"
    CALIBRATE_TWIN="CALIBRATE_TWIN"; ARCHIVE_TOPIC="ARCHIVE_TOPIC"
    SET_PRIORITY="SET_PRIORITY"; DROP_SOFT_PREFERENCE="DROP_SOFT_PREFERENCE"
    HUMAN_ESCALATION="HUMAN_ESCALATION"; SET_RESEARCH_PHASE="SET_RESEARCH_PHASE"

class BriefingType(str, Enum):
    BOOTSTRAP="BOOTSTRAP"; PERIODIC="PERIODIC"; URGENT="URGENT"; FINAL="FINAL"

class SymptomType(str, Enum):
    INITIAL_SWEEP="INITIAL_SWEEP"; WEISSRAUM="WEISSRAUM"; FRACTURE_GAP="FRACTURE_GAP"
    SATURATION="SATURATION"; BRIDGE_OPP="BRIDGE_OPP"; TWIN_DRIFT="TWIN_DRIFT"
    CAPABILITY_GAP_FEEDBACK="CAPABILITY_GAP_FEEDBACK"; DIMENSION_GAP="DIMENSION_GAP"
    REPLICATE_DIVERGENCE="REPLICATE_DIVERGENCE"; QUARANTINE_BLOCK="QUARANTINE_BLOCK"

class EscalationType(str, Enum):
    BUDGET="BUDGET"; DIMENSION_PHYSICAL="DIMENSION_PHYSICAL"
    ABORT_CONFIRM="ABORT_CONFIRM"; SAFETY_EVENT="SAFETY_EVENT"
    DEADLOCK="DEADLOCK"; CAPEX="CAPEX"; MANIFEST_EXPIRED="MANIFEST_EXPIRED"
    QUARANTINE_EXIT="QUARANTINE_EXIT"; LLM_FAILURE="LLM_FAILURE"
    STRATEGIC_QUESTION="STRATEGIC_QUESTION"; TWIN_UNCALIBRATABLE="TWIN_UNCALIBRATABLE"
    BUDGET_EXHAUSTED="BUDGET_EXHAUSTED"; CAPABILITY_DELIVERY="CAPABILITY_DELIVERY"
    TEMPLATE_GAP="TEMPLATE_GAP"

class EscalationCategory(str, Enum):
    DEADLOCK="DEADLOCK"; STRATEGIC_QUESTION="STRATEGIC_QUESTION"
    RISK_ACCEPTANCE="RISK_ACCEPTANCE"

class ConstraintOperator(str, Enum): GE; LE; GT; LT; EQ; RANGE
class EnforcementType(str, Enum): EXCLUSION; SAFETY; BOUNDS
class RiskLevel(str, Enum): LOW; MEDIUM; HIGH
class AggregationType(str, Enum): WEIGHTED_SUM; PARETO
class DimensionRequestStatus(str, Enum):
    PROPOSED; APPROVED; REJECTED; ESCALATED; COOLDOWN
class HypothesisStatus(str, Enum): PROPOSED; ACTIVE; CONFIRMED; REFUTED; ARCHIVED
class ResearchTopicState(str, Enum):
    PROPOSED; ACTIVE; SATURATED; ABORTED; ARCHIVED

# Achsen-Enums (DESIGN)
class SafetyAxis(str, Enum): NORMAL; SAFE_MODE; ESTOP_LOCKED
class ResourceAxis(str, Enum): FUNDED; INCUBATING; PHYSICAL_WAIT; BUDGET_EXHAUSTED
class ResearchAxis(str, Enum): BOOTSTRAP; EXPLORATION; EXPLOITATION; SATURATION
class GovernanceAxis(str, Enum): AUTONOMOUS; AWAITING_HUMAN; CONFLICT_LOCK
class OwnerAxis(str, Enum): GLOBAL; SAFETY; RESOURCE; RESEARCH; GOVERNANCE
```

## §7 ControlState-Verträge (KANONISCHE QUELLE)

```python
class ControlState(BaseModel):
    safety: SafetyAxis
    resource: ResourceAxis
    research: ResearchAxis
    governance: GovernanceAxis
    updated_at: str
    phase_label: str = ""   # abgeleitet via compute_phase_label (§42), nicht authoritativ

class AxisTransition(BaseModel):
    transition_id: str
    batch_id: str          # PATCH: gemeinsame ID aller Transitionen eines atomaren
                           # Commits (SL-AX-ATOMIC). Einzel-Transition: batch_id =
                           # transition_id (Selbstreferenz).
    axis: Literal["SAFETY","RESOURCE","RESEARCH","GOVERNANCE"]
    from_value: str
    to_value: str
    trigger_reason: str    # template-basiert, max 512, Scan
    triggered_by: Literal["KANZLER","KOENIGIN","MENSCH","SYSTEM","HAL"]
    timestamp: str

class ControlStateLog(BaseModel):
    mission_id: str
    transitions: list[AxisTransition] = []
    current_state: ControlState   # authoritativ
    updated_at: str
```

> **Atomarität (SL-AX-ATOMIC):** Ein atomarer Commit schreibt alle
> AxisTransition-Einträge eines Batches mit derselben `batch_id` in genau einer
> atomaren Dateioperation (SR-55). Entweder alle oder keiner.

## §8 Mission-Verträge

```python
class ManifestConstraint(BaseModel):
    constraint_id: str
    dimension_ref: Optional[str] = None     # None = missionsweite Regel
    operator: ConstraintOperator
    value: Optional[float] = None
    range: Optional[tuple[float,float]] = None
    categories: Optional[list[str]] = None
    enforcement: EnforcementType
    description: str                        # max 512, Scan

class SoftPreference(BaseModel):
    preference_id: str                      # v0.3.0 §17: {id, text}
    text: str                               # max 256, Scan

class ResearchManifest(BaseModel):
    manifest_id: str
    mission_goal: str                       # max 2048, Scan
    hard_constraints: list[ManifestConstraint]
    soft_preferences: list[SoftPreference] = []
    objective_family_seed: ObjectiveFamilySeed
    initial_dimensions: list[DimensionSpec]
    domain: str
    valid_from: str
    valid_until: Optional[str] = None
    created_by: str                         # immer Mensch
    approved_by: str                        # immer Mensch
    version: str
    created_at: str
    updated_at: str

class ObjectiveSpec(BaseModel):
    metric_ref: str
    direction: Literal["MAXIMIZE","MINIMIZE"]
    target: Optional[float] = None
    weight: float = 1.0

class MetricConstraint(BaseModel):          # binäres Gate (SL-SIG-4)
    constraint_id: str
    metric_ref: str
    operator: ConstraintOperator
    value: float

class ObjectiveFamilySeed(BaseModel):
    family_id: str
    objectives: list[ObjectiveSpec]
    metric_constraints: list[MetricConstraint]
    aggregation: AggregationType

class TopicSeed(BaseModel):
    seed_id: str
    objective_family_ref: str               # Pflicht: Manifest-Familie
    scope_description: str                  # max 1024, Scan
    suggested_dimensions: list[str]

class TopicConstraintProposal(BaseModel):
    proposal_id: str
    source_topic_ref: str
    constraint: ManifestConstraint
    origin: Literal["LESSONS_LEARNED"] = "LESSONS_LEARNED"
    status: Literal["PROPOSED","ACTIVE","OVERRULED"] = "PROPOSED"

class DimensionSpec(BaseModel):
    dimension_id: str
    display_name: str
    value_type: DimensionValueType          # NUMERIC|CATEGORICAL|ORDINAL
    unit: Optional[str] = None
    initial_range: Optional[tuple[float,float]] = None
    initial_categories: Optional[list[str]] = None
    is_context_dimension: bool = False
    is_integrity_dim: bool = False
    parent_dimension: Optional[str] = None  # SL-DIM-8

class TimeService(BaseModel):
    source: str
    now_iso: str
    mission_start_iso: str
```

## §9 Briefing-Verträge (vollständig inkl. v0.3.0-Änderungen)

```python
class AtlasMacroState(BaseModel):
    total_zones: int; healthy_zones: int; degraded_zones: int
    critical_zones: int; locked_zones: int; quarantined_zones: int
    unexplored_zones: int
    avg_fracture_score: Optional[float] = None
    avg_uncertainty_score: Optional[float] = None   # v0.3.0 §3.6: Optional
    total_crystals: int; total_hypotheses: int
    total_digital_twins: int; drifted_twins: int
    frontier_candidates_count: int
    vordenker_calibration_score: Optional[float] = None

class BudgetState(BaseModel):
    total_budget_cycles: int; used_cycles: int; remaining_cycles: int
    reserved_cycles: int; burn_rate_per_cycle: float
    estimated_completion_cycle: Optional[int] = None

class TopicSummary(BaseModel):
    topic_id: str; state: ResearchTopicState
    progress_percent: float; best_objective_distance: float
    active_zone_count: int; saturation_cycles: int

class FractureSummary(BaseModel):
    zone_ref: str; fracture_score: float; conflict_count: int; since_cycles: int

class TwinStatusSummary(BaseModel):
    twin_node_ref: str; display_name: str; model_version: str
    drift_score: float; divergence_threshold: float; calibration_required: bool

class SlotOutage(BaseModel):
    slot_id: str; state: str; since: str

class HardwareHealth(BaseModel):
    slot_outages: list[SlotOutage] = []
    questor_health_status: str             # HEALTHY|DEGRADED|UNHEALTHY|DEAD
    operational_failure_count_recent: int

class DecisionOption(BaseModel):
    option_id: str
    description: str                       # max 512, Scan
    impact: str                            # max 512
    risk_level: RiskLevel
    requires_human_approval: bool

class RoyalLogAnchor(BaseModel):
    entry_ref: str
    origin: str                            # QUEEN|HUMAN
    intent: Optional[DirectiveIntent] = None
    summary: str                           # max 256
    outcome: Optional[str] = None
    age_cycles: int

class InFlightPackageSummary(BaseModel):    # v0.3.0 §10 SL-PKG-1
    package_id: str; zone_ref: str; topic_ref: str
    manifest_version_started: str; gate_mode: str
    twin_invalidated: bool = False          # v0.3.0 §6.5 SL-TWIN-10

class StrategicBriefing(BaseModel):
    briefing_id: str                        # einzige Zyklen-ID (zyklus_id GESTRICHEN)
    briefing_type: BriefingType
    manifest_version_ref: str
    atlas_macro_state: AtlasMacroState
    budget_state: BudgetState
    topics: list[TopicSummary] = []
    active_fractures: list[FractureSummary] = []
    twin_status: list[TwinStatusSummary] = []
    hardware_health: HardwareHealth
    in_flight_packages: list[InFlightPackageSummary] = []   # v0.3.0 §10
    active_hypothesis_refs: list[str] = []                   # v0.3.0 §13 SL-BRF-10
    decisions_required: list[DecisionOption] = []
    royal_log_anchor: list[RoyalLogAnchor] = []
    pending_escalations: list[str] = []
    truncation_applied: bool = False
    generated_at: str
    generated_by: str                       # immer "KANZLER"
```

## §10 Directive-Verträge (discriminierte Union)

```python
class DirectiveParameters(BaseModel):
    """Discriminierte Union über 'intent'. Jedes Intent-Submodell hat
    'intent: Literal[...]' als Discriminator."""
    # Submodelle je Intent (Pflichtfelder gemäß SL-DTT §17):
    # - InitialSweepParams: grid_spec, sweep_template_ref
    # - PivotParams: from_topic_ref, to_topic_seed
    # - UnlockBudgetParams: amount_cycles, purpose
    # - AbortMissionParams: reason
    # - AddDimensionHintParams: source_ref, dimension_seed
    # - IncreaseDiagnosticParams: zone_ref, amount
    # - CalibrateTwinParams: twin_ref
    # - ArchiveTopicParams: topic_ref
    # - SetPriorityParams: topic_ref, priority
    # - DropSoftPreferenceParams: preference_ref
    # - HumanEscalationParams: question, escalation_category
    # - SetResearchPhaseParams: target_phase, reason
    # - NoActionParams: (leer)

class StrategicDirective(BaseModel):
    directive_id: str
    briefing_ref: str
    intent: DirectiveIntent
    target_ref: Optional[str] = None
    parameters: DirectiveParameters         # discriminierte Union
    reason: str                             # max 1024, Scan
    drop_soft_preferences: list[str] = []
    valid_for_cycles: int = 10
    created_at: str
    # v0.3.0 §17: priority und keep_constraints GESTRICHEN (tote Felder)
```

## §11 Governance-Verträge

```python
class HumanResponseDecision(str, Enum): APPROVE; REJECT; PARTIAL; DEFER

class ManifestConstraintDelta(BaseModel):
    action: Literal["ADD","REMOVE","MODIFY"]
    constraint: Optional[ManifestConstraint] = None
    constraint_id: Optional[str] = None

class UnlockDecision(BaseModel):            # v0.3.0 §5.1
    unlock_id: str
    escalation_ref: str
    zone_refs: list[str]
    conditions: str                         # max 1024, Scan
    approved_by: str                        # immer Mensch
    approved_at: str

class HumanResponseFile(BaseModel):
    response_id: str
    escalation_id: str
    decision: HumanResponseDecision
    amount_granted: Optional[int] = None
    constraints_delta: list[ManifestConstraintDelta] = []
    unlock_decision: Optional[UnlockDecision] = None
    scope_refs: list[str] = []
    free_note: str = ""                     # Scan; nur Anchor
    answered_by: str                        # immer Mensch
    answered_at: str

class HumanDirective(BaseModel):
    directive_id: str
    constraint_deltas: list[ManifestConstraintDelta] = []
    topic_freezes: list[str] = []
    dimension_freezes: list[str] = []
    set_research_phase: Optional[ResearchAxis] = None   # Achsen-Integration
    valid_for_cycles: Optional[int] = None
    note: str = ""                          # Scan; nur Anchor
    created_by: str                         # immer Mensch
    created_at: str
    expires_at_cycle: Optional[int] = None

class RoyalLogEntry(BaseModel):
    entry_id: str
    origin: str                             # QUEEN|HUMAN
    directive_ref: Optional[str] = None
    briefing_ref: Optional[str] = None
    outcome: str
    outcome_reason: Optional[str] = None    # max 512
    policy_effect_ref: Optional[str] = None
    provisional: bool = False               # PATCH (SL-BRF-9): DTT setzt true bei
                                            # trunkiertem Briefing
    timestamp: str

class HumanEscalationRecord(BaseModel):
    escalation_id: str
    escalation_type: EscalationType
    payload_ref: str
    target_ref: Optional[str] = None        # für Dedup (escalation_type, target_ref)
    status: str                             # PENDING|ANSWERED|TIMED_OUT
    created_at: str
    timeout_cycles: int
    answered_by: Optional[str] = None
    answer_ref: Optional[str] = None

class MissionBudget(BaseModel):
    mission_id: str; total_cycles: int; used_cycles: int
    reserved_cycles: int = 0
    capex_requests: list[CapexRequest] = []
    updated_at: str

class CapexRequest(BaseModel):
    request_id: str; description: str       # max 512, Scan
    estimated_cost: str
    requires_human_approval: bool = True
    status: DimensionRequestStatus
```

## §12 Forschungs-Verträge

```python
class SymptomEvent(BaseModel):
    event_id: str
    symptom_type: SymptomType
    zone_ref: Optional[str] = None
    atlas_refs: list[str] = []
    metrics_snapshot: dict[str,float] = {}
    twin_divergence_report_ref: Optional[str] = None
    created_at: str

class CapabilityRequirement(BaseModel):
    capability_id: str
    parameter_requirements: dict[str,Any] = {}

class ExpectationSpec(BaseModel):           # v0.3.0 §7.1
    metric_ref: str
    direction: Literal["INCREASE","DECREASE","REACH"]
    threshold: Optional[float] = None
    delta: Optional[float] = None

class ScientificHypothesis(BaseModel):
    hypothesis_id: str
    hypothesis_text: str                    # max 2048, Scan
    expected_outcome: str                   # max 1024
    expectation_spec: Optional[ExpectationSpec] = None   # v0.3.0 SL-HYP-4
    source_trigger: SymptomType
    atlas_refs: list[str] = []              # leer nur bei INITIAL_SWEEP
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
    rationale: str                          # max 2048, Scan
    source_ref: str                         # Hypothese ODER Direktive (SL-DIR-7)
    source_trigger: SymptomType
    suggested_value_range: Optional[tuple[float,float]] = None
    suggested_categories: Optional[list[str]] = None
    requires_physical_actuation: bool = False
    status: DimensionRequestStatus = DimensionRequestStatus.PROPOSED
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    created_at: str

class DimensionExpansionApproval(BaseModel):
    request_ref: str
    approver: str                           # immer Mensch bei physischer Nutzung
    approved_at: str
    scope: str

class CapabilityGapSignal(BaseModel):
    signal_id: str
    waypoint_ref: Optional[str] = None
    hypothesis_ref: str
    missing_capability: str
    attempted_parameters: dict[str,Any] = {}
    suggested_alternatives: list[str] = []
    requires_budget_or_hardware: bool = False
    created_at: str
```

## §13 Report- und Registry-Verträge

```python
class CrystalSummary(BaseModel):
    crystal_node_ref: str
    objective_values: dict[str,float]
    support_confidence: float
    fracture_score: Optional[float] = None

class ReportFacts(BaseModel):
    mission_goal_ref: str
    final_objective_values: dict[str,float]
    top_crystal_summaries: list[CrystalSummary]   # N = top_crystal_count (Config)
    rejected_hypotheses_count: int
    twin_calibration_history: list[str] = []
    safety_warnings: list[str] = []
    diagnostic_resolution_summary: list[str] = []

class FinalScientificReport(BaseModel):
    report_id: str; topic_ref: str; manifest_ref: str
    facts: ReportFacts
    executive_summary: str                  # max 4096, Scan
    future_recommendations: str             # max 2048, Scan
    citation_refs: list[str] = []
    generated_at: str
    human_reviewed: bool = False

class CapabilityRegistryEntry(BaseModel):
    capability_id: str; display_name: str
    status: Literal["ACTIVE","DEPRECATED","RETIRED"]
    parameter_schema: dict[str,Any]
    version: str

class TemplateRegistryEntry(BaseModel):
    template_id: str
    template_type: Literal["SWEEP","DIAGNOSE"]
    domain: str
    status: Literal["ACTIVE","DEPRECATED"]
    version: str
```

## §14 StrategicLayerConfig (mit owner_axis)

```python
class StrategicLayerConfig(BaseModel):
    # GLOBAL (Konstanten, keine Achse setzt sie zur Laufzeit)
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

    # RESEARCH-besetzt (ResearchAxis setzt zur Laufzeit)
    exploration_weight: float = 0.5
    exploitation_weight: float = 0.5
    require_atlas_grounding: bool = True
    replicate_divergence_check: bool = True
    metric_tolerance_multiplier: float = 1.0
    replication_weight: float = 0.35
    min_confirmations: int = 2

    # RESOURCE-besetzt (ResourceAxis setzt zur Laufzeit)
    burn_rate_multiplier: float = 1.0
    physical_dispatch_allowed: bool = True
    escalation_timeout_multiplier: float = 1.0

    # GOVERNANCE-besetzt (GovernanceAxis setzt zur Laufzeit)
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

---

# MODUL RULES

## §15 Missions-Bootstrap (SL-BOOT-0..8)

- **SL-BOOT-0 Manifest-Intake (fail-closed):** `created_by==MENSCH` und
  `approved_by==MENSCH`; `value` XOR `range` je Operator; jeder `dimension_ref`
  existiert in `initial_dimensions`; EXCLUSION mit `categories` nicht-leer;
  `valid_until` via TimeService in Zukunft. Verstoß → REJECT.
- **SL-MAN-9 Operator×Enforcement-Matrix:** EXCLUSION mit `categories` ODER
  (operator+value); SAFETY mit (operator+value); BOUNDS mit `range` ODER
  (operator+value).
- **SL-BOOT-1..6 Kaltstart:** Mensch erstellt Manifest → Kanzler erzeugt
  MissionBootstrap (Dimensionen, ObjectiveFamily, Topic PROPOSED, Budget) →
  materialisiert Constraints → BOOTSTRAP-Briefing → Königin antwortet
  INITIAL_SWEEP → Topic ACTIVE → Kanzler emittiert SymptomEvent(INITIAL_SWEEP).
- **SL-BOOT-2 erweitert:** Fehlen `lab_ambient_temp`/`lab_ambient_humidity` →
  Bootstrap blockiert (Schatten-Variablen-Check stets ausführbar).
- **SL-BOOT-2b Initiale Zonen:** aus deterministischem Template des
  ObjectiveFamilySeed; leerer Atlas → `avg_uncertainty_score = None`.
- **SL-BOOT-7 Template-Lücke:** fehlendes Template → Paket zurückgestellt,
  G-1 ausgelöst.
- **SL-BOOT-8 Deadlock-Schutz:** nach `bootstrap_retry_limit` (=3) invaliden
  INITIAL_SWEEP-Antworten → TEMPLATE_GAP-Eskalation; Topic bleibt PROPOSED.

## §16 Validierungspipeline v2 (10 Stufen, feste Reihenfolge)

```
StrategicDirective
 ├─ 1. Schema (Pydantic + Intent-Submodelle, SL-DIR-9)  FAIL → VETO("SCHEMA_INVALID")
 ├─ 2. briefing_ref-Existenz (SL-DIR-2)                 FAIL → VETO("REF_NOT_FOUND")
 ├─ 3. Manifest-Prüfung (+ Seed-Feasibility SL-DTT-2)   FAIL → VETO("MANIFEST_VIOLATION")
 ├─ 3b. Weisungs-Prüfung (aktive HumanDirective)         FAIL → VETO("HUMAN_DIRECTIVE_VIOLATION")
 ├─ 3c. Target-Existenz & Zustandsmatrix                 FAIL → VETO("TARGET_LOCKED"/"TARGET_TERMINAL")
 ├─ 4. Safety-/Injection-Prüfung (rekursiv, Wortlisten)  FAIL → VETO + Audit
 ├─ 5. Budget-Prüfung (inkl. reserved-Simulation)        FAIL → VETO("BUDGET_NEGATIVE")
 ├─ 6. Intent-Sonderregeln (alle Intents, SL-DTT)
 ├─ 6b. Mode-Prüfung via ControlState (§41)              FAIL → VETO("MODE_VIOLATION")
 ├─ 6c. Semantische Dedup (SL-INT-5)                     FAIL → VETO("DUPLICATE_SEMANTIC")
 ├─ 7. Konflikt-Modus-Prüfung (SL-CON-3)                 FAIL → VETO("CONFLICT_MODE")
 └─ 8. ACCEPT → DirectiveTranslationTable
```

**Schritt 6b (Mode-Prüfung):** liest den ControlState und wendet die
Intent-Verfügbarkeit (§41) an. Die Intent-Whitelist ergibt sich aus der
Achsen-Kombination, nicht aus einem separaten SystemMode.

## §17 DirectiveTranslationTable (SL-DTT)

Deterministische Übersetzung; kein Interpretationsspielraum.

| Intent | Pflicht-Parameter | Deterministische Wirkung |
|---|---|---|
| NO_ACTION | — | keine Policy-Änderung; Zyklus protokolliert |
| INITIAL_SWEEP | grid_spec, sweep_template_ref | Topic PROPOSED→ACTIVE, Seed-Symptom. **Setzt exploration_weight NICHT direkt** (RESEARCH-besetzt) |
| PIVOT_DOMAIN/PIVOT_TARGET | from_topic_ref, to_topic_seed | Scope-Check (SL-DIR-8), Feasibility (SL-DTT-2), Loop-Erkennung (SL-DTT-3); altes Topic→ARCHIVED nach Lessons-Learned; neues PROPOSED |
| UNLOCK_BUDGET | amount_cycles, purpose | immer Eskalation(BUDGET); bei Bestätigung reserved→used (SL-BUD-3) |
| ABORT_MISSION | reason | immer ESCALATED; nur mit menschlicher Bestätigung |
| ADD_DIMENSION_HINT | source_ref, dimension_seed | erzeugt DimensionOnboardingRequest |
| INCREASE_DIAGNOSTIC | zone_ref, amount | diagnostic_budget += amount (max) |
| CALIBRATE_TWIN | twin_ref | VETO wenn nicht gedriftet (NO_DRIFT); sonst diagnostic_weight↑ |
| ARCHIVE_TOPIC | topic_ref | Topic→ARCHIVED nach Lessons-Learned |
| SET_PRIORITY | topic_ref, priority | Topic.priority setzen |
| DROP_SOFT_PREFERENCE | preference_ref | soft_preference deaktivieren |
| HUMAN_ESCALATION | question, escalation_category | Eskalation mit Typ aus category |
| SET_RESEARCH_PHASE | target_phase, reason | löst ResearchAxis-Wechsel aus (§42); Validierung prüft Ziel-ControlState |

- **SL-DTT-1 Lessons-Learned:** topic-lokale weiche Filter
  (TopicConstraintProposal), keine ManifestConstraints. Aufstieg zu hart nur
  über neue menschliche Manifest-Version (SL-MAN-1 gewahrt).
- **SL-BRF-9 provisional:** Die DTT setzt `royal_log_entry.provisional = true`,
  wenn `briefing_ref` auf ein trunkiertes Briefing verweist
  (`briefing.truncation_applied == true`). Es ist ein DTT-Ausgabe-/Audit-Feld,
  kein Feld der Königin-Direktive.

## §18 Konfliktdetektor & NO_ACTION (SL-CON, SL-NOACT)

- **SL-CON-1:** Jeder GOVERNANCE-VETO gegen eine Königin-Direktive zählt als
  Konflikt (BENIGN-VETOs zählen nicht, SL-CON-4).
- **SL-CON-2:** 2 Konflikte in `conflict_window_cycles` → URGENT +
  Eskalation(DEADLOCK); Königin erzeugt nur noch NO_ACTION.
- **SL-CON-3 Mechanischer Konflikt-Modus:** nur NO_ACTION/HUMAN_ESCALATION
  angenommen; übrige → VETO("CONFLICT_MODE"), zählt nicht als neuer Konflikt.
- **SL-CON-4 VETO-Schwere-Klassen:** BENIGN = {NO_DRIFT, TARGET_LOCKED,
  einzelne SCHEMA_INVALID, DUPLICATE_SEMANTIC}; GOVERNANCE = {MANIFEST_VIOLATION,
  HUMAN_DIRECTIVE_VIOLATION, Safety-/Injection-VETOs}.
- **SL-INT-5 Semantische Dedup:** `semantic_directive_id = sha256(intent +
  target_ref + canonical_json(parameters))`. Wiederholung mit gleichem Outcome
  innerhalb `semantic_dedup_window_cycles` → VETO("DUPLICATE_SEMANTIC"),
  ausgenommen NO_ACTION.
- **SL-NOACT-1:** liest `governance.stall_detection_active`. Wenn false →
  Stall-Counter wird NICHT erhöht. Wenn true → `no_action_stall_limit`
  aufeinanderfolgende NO_ACTION ohne Atlas-Fortschritt → URGENT. Reset nach
  URGENT-Zustellung.
- **SL-NOACT-2:** Während HOLD/SAFE (governance=AWAITING_HUMAN oder
  safety=SAFE_MODE) ist die Stall-Überwachung suspendiert. Kein
  Eskalations-Sturm.

## §19 Symptom-Trigger und Vordenker

| Symptom | Deterministische Bedingung | Vordenker-Aktion |
|---|---|---|
| INITIAL_SWEEP | Bootstrap (SL-BOOT-6) | Seed-Modus |
| WEISSRAUM | Zone gemäß SL-DEF-2 | Void-Prompting |
| FRACTURE_GAP | fracture_score ≥ quarantine_threshold | Fracture-Prompting |
| SATURATION | Topic-StopCondition SATURATION_CYCLES (einzige Quelle) | Paradigma-Wechsel |
| BRIDGE_OPP | Cluster-Kanten ≥ bridge_edge_threshold | Bridge-Prompting |
| TWIN_DRIFT | tolerance_breached = true | Twin-Calibration-Prompting |
| CAPABILITY_GAP_FEEDBACK | CapabilityGapSignal eingegangen | Hypothese anpassen |
| DIMENSION_GAP | Idee wegen approved=false-Dimension blockiert | alternative Hypothese |
| REPLICATE_DIVERGENCE | SL-SIG-5 | Replikations-Hypothese |
| QUARANTINE_BLOCK | Idee in quarantinierter Zone blockiert | Diagnose-Hypothese |

- **SL-URG-1 URGENT-Trigger:** fracture_score ≥ full_rebuild_threshold;
  tolerance_breached; Topic SATURATED ohne Ziel bei Budget >
  stagnation_budget_threshold; LOCKED-Zone ohne Diagnose-Strategie; Konflikt;
  CapabilityGap mit requires_budget_or_hardware; SAFETY-Ereignis;
  Manifest-Sprung; NO_ACTION-Stall; Quarantäne-Timeout;
  questor_health_status==DEAD; remaining_cycles ≤ budget_unlock_threshold_fraction;
  Mission ohne aktives Topic.
- **SL-URG-3:** URGENT-Nachzügler während Cooldown werden ins nächste PERIODIC
  gemerged; kein stiller Verlust.
- **SL-SYM-1 Verlustschutz:** SymptomEvents vor Queue-Übergabe persistent;
  bei High-Watermark zurückgestellt und erneut zugestellt (At-Least-Once).

## §20 Signal-Semantik (SL-SIG, SL-HYP)

- **SL-SIG-1 Korrigierter Fallback:**
  ```
  WENN expectation_ref vorhanden:
      confirms_expectation==False → 🟨 CONTRADICTION (REFUTES)
      confirms_expectation==True  → 🟩 (≥0.8) bzw. ⬜ (<0.8)
      confirms_expectation==None  → ⬜ EXPLORATORY_COVERAGE
  WENN keine Erwartung UND ziel_erreicht==True:
      konfidenz ≥ 0.8 → 🟩 CONFIRMATION; ≥ 0.5 → ⬜ EXPLORATORY_COVERAGE
  WENN keine Erwartung UND ziel_erreicht==False:
      → ⬜ EXPLORATORY_COVERAGE mit evidence_kind = NEGATIVE_KNOWLEDGE
  ```
- **SL-SIG-2:** Operationale Paketfehler fließen nie in wissenschaftliche
  Metriken (nur HardwareHealth.operational_failure_count_recent).
- **SL-SIG-3:** Sättigung hat genau eine Quelle (Topic-StopCondition
  SATURATION_CYCLES).
- **SL-SIG-4:** ObjectiveFamily-Constraints werden binär gegatet.
- **SL-HYP-4 Erwartungs-Brücke:** Bestätigende Hypothesen müssen
  ExpectationSpec tragen. `require_atlas_grounding` ist RESEARCH-besetzt:
  in BOOTSTRAP/EXPLORATION ist De-novo (atlas_refs=[]) erlaubt, in
  EXPLOITATION/SATURATION nicht.
- **SL-SIG-5 Replikat-Divergenz:** zwei parameter-äquivalente Kristalle mit
  Differenz > tolerance → REPLICATE_DIVERGENCE (nur wenn
  `replicate_divergence_check == true`, RESEARCH-besetzt).
- **SL-SIG-6:** Operativer Fehler auf integrity_dim → validity=COMPROMISED.
- **SL-SIG-7:** Constraint-Verletzung ohne Erwartung → ⬜ CONSTRAINT_NEAR_MISS.
- **SL-SIG-8:** `negative_knowledge_decay` für erfolglos abgedeckte Regionen.

## §21 Manifest-Enforcement (SL-MAN)

- **Schutzkette:** Manifest.hard_constraints → SL-BOOT-3 Materialisierung →
  ExclusionConstraint/SafetyConstraint im Atlas → FrontierEngine-Hartfilter Nr.10
  → Pre-Filter → Quartiermeister SL-MAN-4 (parameter_bounds ∩ Constraints) →
  PolicyEvaluator Prüfung 9.
- **SL-MAN-7 Semantische Umgehungsabwehr:** neue kategorische Werte nicht in
  ManifestConstraint.categories → Constraint-Verstoß.

## §22 Safety-Reaktionskette (SL-SAF, Quarantäne)

- **SL-SAF-1..4 ESTOP-Kette:** HAL meldet ESTOP → Questor SAFETY-Abbruch (SR-19)
  → Archivar SAFETY-Governance-Ereignis → **Kanzler ereignisgesteuert SOFORT:**
  Zone→LOCKED, SafetyConstraint-Vorschlag, URGENT-Briefing,
  Eskalation(SAFETY_EVENT), **Achsen-Transition safety→ESTOP_LOCKED (§38)**.
- **SL-SAF-2c Globales ESTOP → Zonen-Mapping:** Zonen mit in-flight-Paketen +
  Ursprungs-Slot-Zone → LOCKED; übrige → INTERLOCKED bis HAL-Gesundcheck.
- **SL-SAF-4 erweitert:** ESTOP-/Reset-Begriffsprüfung rekursiv über
  canonical-geflattete parameters.
- **SL-SAF-5 Entsperrpfad:** LOCKED ausschließlich über strukturierte
  HumanResponseFile.unlock_decision. Zustandsfolge LOCKED → DIAGNOSTIC_ONLY →
  RELEASED.
- **SL-SAF-6 SafetyConstraint-Aktivierung:** Vorschlag gilt sofort als
  active=provisional; menschliche Bestätigung macht permanent.
- **§22.6 Quarantäne:** Zustandsmaschine ENTRY → DIAGNOSTIC_ALLOWED →
  QUARANTINE_EXIT → {RESUME, CLOSE}. Diagnostik erlaubt und budgetiert.
  Blockierte Ideen emittieren QUARANTINE_BLOCK. Exit nur über strukturierte
  QUARANTINE_EXIT-Antwort. Sicherheitsrelevanz-Regel: Fracture ist
  sicherheitsrelevant genau dann, wenn seine Zone eine SafetyConstraint- oder
  SAFETY-Enforcement-Dimension schneidet.

## §23 Digital-Twin-Loop (SL-TWIN)

- **SL-TWIN-1 Paarung:** erfordert objective_family_ref + digital_twin_ref +
  Parameter-Äquivalenz. Nicht-äquivalente werden nicht gepaart.
- **SL-TWIN-2 Deviation:**
  ```
  dev_metric = max(
      abs(sim−real)/max(abs(real), twin_epsilon_default),
      abs(sim−real)/abs_tolerance_metric)
  abs_tolerance_metric = MetricDefinition.tolerance falls gesetzt,
                         sonst twin_abs_tolerance_default
  Für real ≈ 0 gilt ausschließlich der Absolutterm.
  ```
- **SL-TWIN-3 Validitätsprüfung:** digital_twin_ref gesetzt UND drift_score >
  threshold UND objective_type ≠ DIAGNOSE → VETO(TWIN_DEGRADED).
- **SL-TWIN-4 Gate×Security-Mode-Matrix:** physisches Kalibrierungs-Paket
  konstruktionsunmöglich (SANDBOX erzwungen).
- **SL-TWIN-5 Schatten-Variablen-Check:** bei TWIN_DRIFT zwingend
  Umgebungs-Dimensionen im Vordenker-Prompt.
- **SL-TWIN-6..7 Dedup/Deadlock-Freiheit:** blocked_cache (twin_ref, zyklus);
  SANDBOX-Kalibrierung bleibt erlaubt.
- **SL-TWIN-8 Konfidenz-Kalibrierung:** rollierender
  vordenker_calibration_score; bei < calibration_alert_threshold DecisionOption.
- **SL-TWIN-9 Kalibrierungs-Abbruch:** nach twin_calibration_max_attempts (=3)
  ohne Drift-Reduktion ≥ twin_drift_reduction_min → SUSPENDED +
  Eskalation(TWIN_UNCALIBRATABLE).
- **SL-TWIN-10 In-flight bei Drift:** twin_invalidated=true im Briefing.
- **SL-TWIN-11 Late-Pairing:** nach TTL weitere
  twin_late_pairing_window_cycles nachpaarbar.

## §24 Dimensions-Lebenszyklus (SL-DIM)

- **SL-DIM-1..4 Kanzler-Prüfung:** Plausibilität, Range-Validierung, Cooldown
  (max_dimension_requests_per_topic_per_cycle), physische Auswirkung
  (requires_physical_actuation=true → zwingend ESCALATED).
- **SL-DIM-5 Deadlock-Freiheit:** Ideen mit approved=false-Dimension werden
  nicht still verworfen → SymptomEvent(DIMENSION_GAP) + DecisionOption.
- **SL-DIM-6..7 Genehmigung/Backfill:** erzeugt TypedDimension(approved=false);
  optional BACKFILL_FRONTIER.
- **SL-DIM-8 Abgeleitete Dimensionen:** parent_dimension-Referenz.
- **SL-DIM-9 CATEGORY_EXTENSION:** neue Kategoriewerte → leichter Request.
- **SL-DIM-10 requires_physical_actuation:** jede Hardware-/Aktuierungsänderung
  außerhalb registrierter Capability-Parameter.
- **SL-DIM-11 Lebenszeit-Limit:** max_dimension_requests_per_topic_total +
  Wiederholungs-Erkennung über proposed_dimension_id.
- **SL-DIM-12 Request-Outcomes:** dimension_request_outcomes im Briefing.
- **SL-DIM-13 Range-Korrekturen:** Feedback-Symptom an Vordenker.
- **SL-DIR-7:** RequestSource-Union statt SymptomType-Zwang.

## §25 Capability-Gap & CAPEX (SL-ESC-7)

```
VORDENKER: ScientificHypothesis mit required_capabilities (Pflicht)
    ▼
LOTSE prüft gegen Capability-Registry
    ├─ erfüllt → Wegmarke
    └─ unerfüllbar → CapabilityGapSignal
           ├─ blocked_cache CAPABILITY_GAP
           ├─ nach capability_gap_repeat_limit Wiederholungen: DecisionOption
           │  (bei requires_budget_or_hardware → CAPEX-Eskalation)
           └─ SL-ESC-7: CAPEX-Wartezeit → Eskalation(CAPABILITY_DELIVERY)
              mit Lieferdatum; blocked_cache-Clearing-Pfad
              → Achsen-Transition resource→PHYSICAL_WAIT (§38)
```

## §26 Mensch-Schnittstelle (SL-ESC)

- **SL-ESC-1..4:** Eskalationskanal dateibasiert (`data/archiv/operational/
  escalations/`); Antworten in `data/human_inbox/`. Unbeantwortete Eskalation →
  nach timeout_cycles → governance→AWAITING_HUMAN. Erinnerungen alle
  escalation_reminder_interval_cycles (max escalation_reminder_cap).
- **SL-ESC-5 HumanResponseFile-Validierung:** Antwortdateien müssen gegen das
  Schema validieren. Unparsbar → PARSE_REJECTED + Erinnerungs-Template.
- **SL-ESC-6 EscalationType-Erweiterung + Dedup:** HUMAN_ESCALATION erhält
  Pflicht-Parameter escalation_category. Dedup über (escalation_type, target_ref).

## §27 Briefing-Erzeugung (SL-BRF)

- **SL-BRF-1..6 Sanitization:** Verboten: security_mode, Hybrid-Referenzen,
  Roh-metric_vector. Fortschritt als deterministische Skalare. Quarantäne →
  [REDACTED:QUARANTINE].
- **SL-BRF-4 Trunkierungspriorität v2:** URGENT-Auslöser + SAFETY >
  LOCKED/CRITICAL/QUARANTINE + drifted Twins + pending_escalations +
  decisions_required > höchste Fractures > aktive Topics > Rest. Twins mit
  calibration_required oder drift_score > 0 fallen nie in die Restklasse.
- **SL-BRF-8 Gesamt-Kontext-Budget:** max_total_context_chars =
  manifest_max_chars + max_briefing_chars + anchor_max_chars. Layer 3 (Anchor)
  wird nie trunkiert.
- **SL-BRF-10:** Briefing exponiert active_hypothesis_refs (Top-N).

## §28 Sanitization (SL-SAN)

- **SL-SAN-0 First-Order-Scan:** aller LLM-Outputs vor Persistenz. Treffer →
  Quarantäne + Audit + einmalige Neu-Generierung, danach Eskalation.
- **SL-SAN-1 Archivar-Eingangssanitization:** Freitextfelder eingehender
  questor_ergebnis_paket werden gescannt (INJ-01..15, XML-Escaping).
- **SL-SAN-2 Second-Order-Scan:** persistierte LLM-Texte beim Wiedereinspeisen
  erneut gescannt. Treffer → Quarantäne, Platzhalter, Audit, DecisionOption.
- **SL-SAN-5:** INJ-01..15 und Safety-Claim-Katalog als normativer Anhang.
- **SL-SAN-6 Roh-Ergebnis-Trennung:** observation_raw (quarantänefähig) und
  interpretation (niemals Erwartungsquelle).
- **SL-RPT-1 Zitiermuster-Entfernung:** deterministisch über Regex-Katalog;
  nicht erfassbare Fälle als review_required.

## §29 Abschluss und Archivierung (SL-RPT)

```
StopCondition REACHED → Topic SATURATED → FINAL-Briefing
  → Kanzler injiziert ReportFacts (deterministisch)
  → Königin-LLM: NUR executive_summary + future_recommendations
  → Kanzler: Sanitization + Zitierungs-Check
  → Mensch: human_reviewed = true → ARCHIVED → Cold Storage
```
- **SL-RPT-2 Fakten-Trennung:** harte Fakten ausschließlich aus ReportFacts.
- **SL-RPT-3..4:** Unreviewed-Reminder alle review_reminder_interval_cycles.
  Nach review_grace_max_cycles finale Eskalation. Nach cold_storage_window_days
  mit human_reviewed=true → Cold Storage.

## §30 Replikation (SL-REP)

- **SL-REP-1:** FrontierType um REPLICATE erweitert.
- **SL-REP-2:** REPLICATE-Frontiers bei crystallization_progress ≥
  replication_trigger_progress und Bestätigungen < min_confirmations
  (RESEARCH-besetzt). Relevante Bestätigung: parameter-äquivalenter Kristall,
  gleiche ObjectiveFamily, ziel_erreicht=true.
- **SL-REP-3:** FrontierEngine gewichtet REPLICATE mit replication_weight.
- **SL-REP-4 Quotenregel:** ≥ 1 Replikation pro replication_cadence_cycles.
- **SL-REP-5 Fracture-getriebene Replikation:** FRACTURE_GAP mit ≥ 2 divergenten
  Kristallen → REPLICATE-DecisionOption.

## §31 Datenintegrität (SL-INT)

- **SL-INT-1 NaN:** Kristall verworfen, gültige Geschwister bleiben. Gilt auch
  für SymptomEvent.metrics_snapshot.
- **SL-INT-2 Sequenzlücken:** akzeptiert + Audit-Flag + Reconciliation (Owner,
  Timeout, Abschlusszustand).
- **SL-INT-3 Referentielle Integrität:** briefing_ref, source_ref,
  twin_divergence_report_ref müssen existieren.
- **SL-INT-4 Idempotenz:** directive_id gemäß SL-DIR-1.
- **SL-INT-6 Registry-Index:** Dateien je Verzeichnis für Existenzprüfungen.

## §32 Zyklus-, Zeit- und Budgetmodell (SL-BUD, SL-URG)

- **SL-BUD-1:** `used_cycles += 1 × resource.burn_rate_multiplier`. In
  PHYSICAL_WAIT/BUDGET_EXHAUSTED ist burn_rate_multiplier=0 → Budget brennt
  nicht. **(Achsen-Integration: ResourceAxis besitzt burn_rate_multiplier.)**
- **SL-BUD-2:** remaining_cycles = total_cycles − used_cycles − reserved_cycles.
- **SL-BUD-3:** Bei UNLOCK_BUDGET-Bestätigung: reserved_cycles → used_cycles.
- **SL-BUD-4 Formeln:**
  ```
  burn_rate_per_cycle = used_cycles / max(elapsed_cycles, 1)
  estimated_completion_cycle = used_cycles + ceil(remaining_progress/progress_rate)
  progress_rate ≤ 0 → None
  ```
- **SL-URG-2 BUDGET_EXHAUSTED:** fällt remaining_cycles ≤ 0 oder unter
  budget_unlock_threshold_fraction → URGENT + Eskalation(BUDGET) +
  DecisionOption. Achsen-Transition: resource→BUDGET_EXHAUSTED,
  governance→AWAITING_HUMAN.

## §33 Zustandsmaschinen

- **§33.1 Topic:** PROPOSED → ACTIVE → {SATURATED, ABORTED} → ARCHIVED. Alle
  Übergänge vom Kanzler. Lessons-Learned-Transfer bei jedem ACTIVE-Abschluss.
- **§33.2 DimensionOnboardingRequest:** PROPOSED → APPROVED | REJECTED |
  ESCALATED | COOLDOWN. ESCALATED → APPROVED/REJECTED (Mensch).
- **§33.3 Eskalation:** PENDING → ANSWERED | TIMED_OUT. TIMED_OUT →
  governance=AWAITING_HUMAN. ANSWERED → Umsetzung → RoyalLog.
- **§33.4 SystemMode → Achsen (DESIGN):** SAFE_MODE → safety=SAFE_MODE;
  HOLD_STRATEGY → governance=AWAITING_HUMAN; ESTOP → safety=ESTOP_LOCKED.
  Der einzelne SystemMode wird nicht als parallele Maschine geführt.
- **§33.5 Speicherorte (Blackboard-konform):**
  | Artefakt | Ort |
  |---|---|
  | ResearchManifest | data/governance/manifests/ |
  | StrategicBriefing | data/governance/briefings/ |
  | StrategicDirective | data/governance/directives/ |
  | MissionBudget | data/governance/budget/ |
  | DimensionOnboardingRequest | data/governance/dimension_requests/ |
  | RoyalLog | data/archiv/operational/royal_log/ |
  | SymptomEvent, CapabilityGapSignal | data/archiv/operational/events/ |
  | ScientificHypothesis | data/archiv/ideen/ |
  | HumanEscalationRecord | data/archiv/operational/escalations/ |
  | Menschliche Antworten | data/human_inbox/ |
  | ControlStateLog | data/governance/control_state/ |
  | Registries | data/governance/registries/ |
  | blocked_cache | data/governance/cache/ |

## §34 Autonomie- und Eskalationsmatrix

| Entscheidung | Königin | Kanzler | Nur Mensch |
|---|---|---|---|
| Exploration gewichten | vorschlagen | final | überstimmen |
| Topic archivieren | vorschlagen | final | überstimmen |
| Budget unter Threshold | vorschlagen | final | überstimmen |
| Budget über Threshold / UNLOCK_BUDGET | vorschlagen | eskalieren | final |
| Neue nicht-physische Dimension | Hint | genehmigen | überstimmen |
| Neue physische Dimension | Hint | eskalieren | final |
| CAPEX / Hardware-Kauf | DecisionOption anregen | eskalieren | final |
| Mission abbrechen | vorschlagen | eskalieren | final bestätigen |
| ESTOP/Interlock zurücksetzen | ❌ niemals | ❌ | ✅ autorisierter Sicherheitsprozess |
| Manifest-hard_constraints | ❌ | ❌ | ✅ (neue Version) |
| Twin-Kalibrierung anweisen | ✅ (CALIBRATE_TWIN) | prüfen + umsetzen | überstimmen |
| SafetyConstraint aufheben | ❌ | nur autorisiert | ✅ |
| ResearchPhase setzen | ✅ (SET_RESEARCH_PHASE) | prüfen + umsetzen | überstimmen (HumanDirective.set_research_phase) |

## §35 CHARTER-Konformitätsmatrix

| CHARTER-Regel | Umsetzung |
|---|---|
| SR-04 | Questor/HAL unverändert; strategische Verträge nur auf Gremium-Ebene |
| SR-08 | RoyalLog/Briefings/Direktiven operational; HardwareHealth verzerrt keine Metriken (SL-SIG-2) |
| SR-10 | Ungültige Direktive → VETO; unklarer DimensionRequest → REJECTED; LLM-Ausfall → Policy bleibt; NaN → Verwurf |
| SR-11 | Mensch nie überstimmt; ABORT, physische Dimensionen, CAPEX, Manifest immer menschlich |
| SR-13 | Königin/Vordenker schlagen vor; Kanzler, Pre-Filter, Gate entscheiden deterministisch |
| SR-14 | NaN-Fail-Closed auf Schicht 4 (SL-INT-1) |
| SR-24 | Briefing-Whitelist; Fortschritt als Skalare |
| SR-29 | security_mode in keinem strategischen Artefakt |
| SR-05 | ESTOP-Reset im Intent-Enum nicht ausdrückbar (SL-SAF-4) |
| §2 Blackboard | Alle Kommunikation über definierte Speicherorte (§33.5) |

## §36 Verbotene Patterns (Strategic Layer)

1. Königin-LLM mit persistentem Gesprächsverlauf.
2. Freitext-Report als primärer LLM-Input (nur strukturierte Briefings).
3. LLM-Einsatz im Kanzler (auch keine LLM-Zusammenfassungen).
4. Direkter Atlas-/Archiv-Zugriff der Königin.
5. Direkte Kommunikation Königin ↔ Vordenker.
6. Automatische Dimensions-Erzeugung ohne Kanzler-Prüfung.
7. security_mode oder Atlas-Hybrid-Referenzen im LLM-Kontext.
8. RoyalLog-Inhalte als wissenschaftliche Signale.
9. Sim-Evidenz, die physische Kristalle direkt bestätigt.
10. Physische Kalibrierungs-Pakete (SL-TWIN-4).
11. Explorations-Fehlschläge als 🟨 CONTRADICTION (SL-SIG-1).
12. Weiterlauf mit offener Eskalation nach Timeout (governance=AWAITING_HUMAN).
13. CHARTER-Änderung als Voraussetzung dieses Dokuments.
14. **Achsen-Parameter direkt setzen statt über ControlState lesen**
    (Single Ownership, §40).

## §37 Testsuite (STRAT-01..55)

STRAT-01..25 (v0.2.0 §28.1) + STRAT-26..45 (v0.3.0 §19) + achsen-spezifisch:

| ID | Test | Erwartung |
|---|---|---|
| STRAT-46 | UNLOCK_BUDGET bei resource=FUNDED | VETO(MODE_VIOLATION) |
| STRAT-47 | UNLOCK_BUDGET bei resource=BUDGET_EXHAUSTED | Intent verfügbar |
| STRAT-48 | De-novo-Hypothese in EXPLORATION | akzeptiert (require_atlas_grounding=false) |
| STRAT-49 | De-novo-Hypothese in EXPLOITATION | verworfen (require_atlas_grounding=true) |
| STRAT-50 | Budget-Burn in PHYSICAL_WAIT | used_cycles ändert sich nicht (burn_rate_multiplier=0) |
| STRAT-51 | Stall-Detektion in AWAITING_HUMAN | suspendiert (stall_detection_active=false) |
| STRAT-52 | SET_RESEARCH_PHASE auf ungültigen Zielzustand | VETO, Achse unverändert |
| STRAT-53 | provisional bei trunkiertem Briefing | royal_log_entry.provisional=true |
| STRAT-54 | Regel setzt Achsen-Parameter direkt | SL-DEP-Lint Build-Fail |
| STRAT-55 | zwei simultane Achsen-Transitionen | atomar + konsistent committet (SL-AX-ATOMIC) |

---

# MODUL CONTROL (4-Achsen-Steuerung, DESIGN)

## §38 Achsen-Definition

| Achse | Werte | Treiber | Absolutheit |
|---|---|---|---|
| SafetyAxis | NORMAL / SAFE_MODE / ESTOP_LOCKED | HAL-Ereignis, Mensch | **Absolut** |
| ResourceAxis | FUNDED / INCUBATING / PHYSICAL_WAIT / BUDGET_EXHAUSTED | Budgetzähler, Liefer-/Capability-Signal, in-flight | Hoch |
| ResearchAxis | BOOTSTRAP / EXPLORATION / EXPLOITATION / SATURATION | Atlas-Metriken | Normal |
| GovernanceAxis | AUTONOMOUS / AWAITING_HUMAN / CONFLICT_LOCK | Eskalationsstatus, Konfliktdetektor | Normal |

Der Gesamtzustand ist das Tupel `(safety, resource, research, governance)`.
Jede Achse wird unabhängig aktualisiert; ein „Phasenwechsel" ist eine Änderung
einer Achse, nicht des ganzen Tupels.

## §39 Kompositionsregeln (Validitätsmatrix)

- **§39.1 Orthogonalität:** Achsen komponieren; kein Override.
- **§39.2 Validitätsmatrix (ungültige Kombinationen):**
  - safety=ESTOP_LOCKED + resource=INCUBATING (ESTOP bricht in-flight ab).
  - safety=SAFE_MODE + research=BOOTSTRAP (SAFE pausiert Bootstrap).
  - resource=BUDGET_EXHAUSTED + governance=AUTONOMOUS (Budget-Erschöpfung
    erzwingt Eskalation).
- **§39.3 Priorität:** Safety ist absolut. Andere Gates multiplikativ.
- **§39.4 Keine Hierarchie zwischen Achsen:** Konflikte werden durch Single
  Ownership (§40) aufgelöst, nicht durch Rangfolge.

## §40 Parameter-Besitz-Matrix (Single Ownership)

- **ResearchAxis-Besitz:** exploration_weight, exploitation_weight,
  require_atlas_grounding, replicate_divergence_check,
  metric_tolerance_multiplier, replication_weight, min_confirmations.
- **ResourceAxis-Besitz:** burn_rate_multiplier, physical_dispatch_allowed,
  escalation_timeout_multiplier.
- **GovernanceAxis-Besitz:** stall_detection_active.
- **SafetyAxis-Besitz:** safety_dispatch_allowed, safety_intent_blocklist
  (berechnete Gates).

Regeln lesen diese Parameter über den ControlState; sie setzen sie NICHT
direkt. Verstöße → SL-DEP-Lint Build-Fail.

## §41 Intent-Verfügbarkeit

```
verfügbare_Intents = alle_Intents
                     − safety_intent_blocklist
                     − resource_intent_blocklist
                     − governance_intent_blocklist
                     − research_intent_blocklist
```

Beispiel: UNLOCK_BUDGET ist nur verfügbar, wenn resource=BUDGET_EXHAUSTED.
SET_RESEARCH_PHASE ist verfügbar, wenn keine Safety-/Governance-Sperre
vorliegt.

## §42 Transitionen & Liveness

- Der Kanzler wertet Achsen-Transitionen bei jedem Strategie-Zyklus aus;
  Safety/Resource sind ereignisgesteuert (lösen sofort einen atomaren
  Auswertungszyklus aus, §43).
- **Liveness-Watchdog:** global; wenn (now − letzter Strategie-Zyklus) >
  liveness_watchdog_hours → Heartbeat-Zyklus (nur Achsen-Auswertung, kein
  Briefing).
- **compute_phase_label(state):** abgeleitetes Etikett, z. B.
  „EXPLOITATION + PHYSICAL_WAIT + CRISIS". Nicht authoritativ.

## §43 SL-AX-ATOMIC: Atomare Achsen-Auswertung

Alle Achsen-Transitionen werden atomar ausgewertet. Kein Zwischenzustand wird
persistiert. (Behebt DT7-F-01 / K6-F-12.)

**Algorithmus (feste Reihenfolge):**
1. **SAMMELN:** alle im Auswertungszeitpunkt ausgelösten Transitionen in
   `direct_transitions` als (axis, from_value, to_value, timestamp).
2. **KONFLIKT-ERKENNUNG:** mehrere Ereignisse auf derselben Achse →
   schwerwiegendster Zielwert gewinnt (§43.1); unterlegene als SUPERSEDED
   verworfen.
3. **ABSCHLUSS (Closure):** Closure-Regeln (§43.2) iterativ anwenden, max
   closure_max_iterations (=5). Erzwungene Transitionen werden hinzugefügt.
4. **VALIDIERUNG:** finaler Ziel-Tupel gegen §39.2. Gültig → Commit. Ungültig
   trotz Closure → gesamte Transition VERWORFEN, ControlState unverändert,
   Audit + Eskalation(STRATEGIC_QUESTION) (fail-closed).
5. **ATOMARER COMMIT:** alle Transitionen des Batches in einer Operation, oder
   keine.
6. **LOGGING:** alle Transitionen eines Commits als ein Batch mit gemeinsamer
   batch_id.

### §43.1 Severity-Ordnung (DESIGN-FESTLEGUNG)

Achsen-Priorität: SAFETY > RESOURCE > GOVERNANCE > RESEARCH.

| Achse | Severity-Ordnung (schwer → leicht) |
|---|---|
| SafetyAxis | ESTOP_LOCKED > SAFE_MODE > NORMAL |
| ResourceAxis | BUDGET_EXHAUSTED > PHYSICAL_WAIT > INCUBATING > FUNDED |
| GovernanceAxis | CONFLICT_LOCK > AWAITING_HUMAN > AUTONOMOUS |
| ResearchAxis | kein Severity-Begriff; bei Konflikt → Audit + Eskalation |

Bei gleicher Achse und Severity entscheidet der früheste TimeService-Zeitstempel.

### §43.2 Closure-Regeln (aus §39.2 abgeleitet)

| ID | Auslöser | Erzwungene Folge | Begründung |
|---|---|---|---|
| CT-1 | resource → BUDGET_EXHAUSTED | governance → AWAITING_HUMAN | §39.2 |
| CT-2 | safety → ESTOP_LOCKED ∧ resource=INCUBATING | resource verlässt INCUBATING (→ FUNDED, sofern kein schwererer Zielwert) | §39.2; in-flight abgebrochen (SR-19) |
| CT-3 | safety → SAFE_MODE | research-Transitionen werden unterdrückt | SAFE pausiert Direktiven |

**SR-A:** ist safety ∈ {SAFE_MODE, ESTOP_LOCKED}, werden alle pending
ResearchAxis-Transitionen verworfen.

### §43.3 Gearbeitetes Beispiel (ESTOP + Budget-Schwelle)

```
Ausgang: safety=NORMAL, resource=INCUBATING, research=EXPLOITATION, governance=AUTONOMOUS
E1: ESTOP → safety: NORMAL→ESTOP_LOCKED
E2: Budget-Schwelle → resource: INCUBATING→BUDGET_EXHAUSTED

1. SAMMELN: [(safety,NORMAL,ESTOP_LOCKED,t1), (resource,INCUBATING,BUDGET_EXHAUSTED,t2)]
2. KONFLIKT: keine (verschiedene Achsen)
3. ABSCHLUSS:
   - CT-2: resource INCUBATING→FUNDED; kollidiert mit E2 (→BUDGET_EXHAUSTED);
     Severity: BUDGET_EXHAUSTED > FUNDED ⇒ BUDGET_EXHAUSTED gewinnt
   - CT-1: resource=BUDGET_EXHAUSTED ⇒ governance AUTONOMOUS→AWAITING_HUMAN
   - SR-A: keine research-Transitionen
   Fixpunkt.
4. VALIDIERUNG: (ESTOP_LOCKED, BUDGET_EXHAUSTED, EXPLOITATION, AWAITING_HUMAN) → GÜLTIG
5. COMMIT: safety, resource, governance atomar
6. LOGGING: 1 Batch, 3 AxisTransition-Einträge
```

---

# MODUL INDEX

## §44 Fund-Register (Behebungsstatus)

| Fund-Cluster | Behebungs-Abschnitt | Status |
|---|---|---|
| KV-01/KV-20 Mensch-Schnittstelle | §11, §17 (SL-BRF-9) | BEHOBEN |
| KV-02 Lessons-Learned | §17 (SL-DTT-1) | BEHOBEN |
| KV-03 Zyklus/Zeit/Budget | §32 (SL-BUD) | BEHOBEN |
| KV-04 Manifest-Intake | §15 (SL-BOOT-0) | BEHOBEN |
| KV-05 Intent-Parameter | §10 (discriminierte Union), §16 | BEHOBEN |
| KV-06/07/08 Twin | §23 (SL-TWIN) | BEHOBEN |
| KV-09 Schatten-Variablen | §15 (SL-BOOT-2) | BEHOBEN |
| KV-10 Replikation | §30 (SL-REP) | BEHOBEN |
| KV-11 HOLD/SAFE | §39/§40 (Achsen), §18 (SL-NOACT-2) | BEHOBEN |
| KV-12 In-flight-Pakete | §9 (InFlightPackageSummary) | BEHOBEN |
| KV-13 Config-Lücken | §14 (StrategicLayerConfig v2) | BEHOBEN |
| KV-14 Entsperr-/Exit-Pfade | §22 (SL-SAF-5, Quarantäne) | BEHOBEN |
| KV-15 Dedup | §18 (SL-INT-5) | BEHOBEN |
| KV-16 Tote Vertragsfelder | §10 (priority/keep_constraints gestrichen) | BEHOBEN |
| KV-17 First-Order-Scan | §28 (SL-SAN-0) | BEHOBEN |
| KV-18 NO_ACTION-Zwang | §18 (SL-CON-3) | BEHOBEN |
| KV-19 EscalationType | §6, §26 (SL-ESC-6) | BEHOBEN |
| KV-21 Initiale Zonen | §15 (SL-BOOT-2b) | BEHOBEN |
| KV-22 Erwartungs-Brücke | §20 (SL-HYP-4) | BEHOBEN |
| DT7-F-01 Simultane Achsen-Transitionen | §43 (SL-AX-ATOMIC) | BEHOBEN |

**Restrisiken (bewusst dokumentiert):**
- Freitext-only-Menschenweisungen sind nur beratend (§11 SL-ESC-5).
- Unreviewed-Reports blockieren Cold Storage, nicht neue Missionen.
- LLM-Wissenschaftsqualität nur in realen Domänen validierbar.
- Die 4-Achsen-Architektur, Severity-Ordnung (§43.1) und Closure-Regeln
  (§43.2) sind Design-Festlegungen; ihre reale Bewährung steht aus.

## §45 Change-Log

| Version | Änderung |
|---|---|
| 1.0.0 | Finale Konsolidierung: v0.2.0 + v0.3.0 + Achsen-Architektur (Option 2) + alle Patches (provisional, batch_id, SL-AX-ATOMIC, ControlState kanonisch). Alle KV-Funde und DT7-F-01 behoben. |

---

**Ende der GREMIUM UNIFIED SPECIFICATION v1.0.0.**