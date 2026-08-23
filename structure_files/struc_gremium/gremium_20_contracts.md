# GREMIUM CONTRACTS — Datenverträge, Enums & StrategicLayerConfig

| Feld | Wert |
|------|------|
| **Dateiname** | `gremium_20_contracts.md` |
| **Modul** | CONTRACTS |
| **Version** | 1.1.0 |
| **Status** | AKTIV |
| **Hängt ab von** | `gremium_10_core@1.x` |
| **Wird referenziert von** | `gremium_30_rules`, `gremium_40_control` |
| **Änderungsgrund** | K7-F-01, -07, -08, -09, -13, -14, -15, -16, -18, -19, -20, -21 |
| **Change-Log** | 1.0.0: Konsolidierung, Phantom-Verträge, owner_axis. **1.1.0: Briefing-Verträge vollständig nachgeliefert (inkl. v0.3.0-Änderungen, zyklus_id gestrichen); DirectiveParameters als echte discriminierte Union; ControlState kanonisch hier verortet; ParameterOwnershipMatrix vervollständigt; exploration_weight-Konflikt aufgelöst** |

---

## §0 Zweck und Geltung

Dieses Modul definiert **alle Datenverträge** (Pydantic-v2-Modelle), **alle Enums** und die **StrategicLayerConfig** des Gremiums. Es ist die **einzige Quelle** für Vertragsdefinitionen. `30_rules` und `40_control` referenzieren diese Verträge, definieren aber keine eigenen.

**Leitprinzipien:**
1. **SL-DEP-Vollständigkeit:** Jeder referenzierte Vertrag ist hier definiert. Kein Phantom. *(K7-F-02 behoben: auch die Briefing-Verträge sind jetzt definiert, §7.)*
2. **Single Ownership:** Jeder Parameter in `StrategicLayerConfig` deklariert eine `owner_axis` (§4).
3. **Single Source of Truth:** Jeder Vertrag ist genau einmal definiert. `40_control` referenziert `ControlState` aus §3, definiert ihn nicht selbst. *(K7-F-01 behoben.)*
4. **Freitext markiert:** Alle Freitextfelder tragen `(Scan)` = Injection-Scan + Längenlimit.

---

## §1 SL-DEP-Lint (Vertrags-Vollständigkeitsprüfung)

### §1.1 Regel SL-DEP-LINT

Ein Build/Load des Systems schlägt fehl, wenn:
1. Ein Vertrag referenziert, aber nicht in diesem Modul definiert ist.
2. Ein Config-Parameter in `40_control §4` (Besitz-Matrix) referenziert wird, aber nicht in `StrategicLayerConfig` (§4) existiert.
3. Ein Config-Parameter eine `owner_axis` trägt, die nicht im `OwnerAxis`-Enum (§2.8) existiert.
4. Ein Enum-Wert in `30_rules`/`40_control` verwendet wird, aber nicht im zugehörigen Enum (§2) definiert ist.
5. Ein Vertrag in zwei Modulen definiert ist (Single-Source-of-Truth-Verstoß).

### §1.2 Ausführung

Der SL-DEP-Lint ist ein **statischer Build-Check** (deterministisch, kein LLM), ausgeführt vom Kanzler-Bootstrap bei jeder Kompositions-Änderung (Index §4 COMP-01/02). Ergebnis ist ein Lint-Report in `data/governance/lint/`. *(K7-F-03 präzisiert: Ausführungs-Instanz = Kanzler-Bootstrap.)*

---

## §2 Enums (konsolidiert)

### §2.1 DirectiveIntent (erweitert um SET_RESEARCH_PHASE)

```python
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
    SET_RESEARCH_PHASE = "SET_RESEARCH_PHASE"   # NEU (40_control §5.2)
```

### §2.2 Directive-, Briefing-Enums

```python
class DirectiveStatus(str, Enum):
    PROPOSED = "PROPOSED"; ACCEPTED = "ACCEPTED"; VETOED = "VETOED"
    ESCALATED = "ESCALATED"; IMPLEMENTED = "IMPLEMENTED"; REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"; EXPIRED = "EXPIRED"

class DirectiveOutcome(str, Enum):
    IMPLEMENTED = "IMPLEMENTED"; VETOED = "VETOED"; SUPERSEDED = "SUPERSEDED"
    EXPIRED = "EXPIRED"; ESCALATED = "ESCALATED"; HUMAN_OVERRIDE = "HUMAN_OVERRIDE"

class OriginType(str, Enum):
    QUEEN = "QUEEN"; HUMAN = "HUMAN"

class BriefingType(str, Enum):
    BOOTSTRAP = "BOOTSTRAP"; PERIODIC = "PERIODIC"
    URGENT = "URGENT"; FINAL = "FINAL"

class ResearchTopicState(str, Enum):
    PROPOSED = "PROPOSED"; ACTIVE = "ACTIVE"
    SATURATED = "SATURATED"; ABORTED = "ABORTED"; ARCHIVED = "ARCHIVED"

class AggregationType(str, Enum):
    WEIGHTED_SUM = "WEIGHTED_SUM"; PARETO = "PARETO"
```

### §2.3 Hardware-Enums (NEU — für Briefing §7)

```python
class SlotOutageState(str, Enum):
    ESTOP_SUSPENDED = "ESTOP_SUSPENDED"; INTERLOCKED = "INTERLOCKED"
    MAINTENANCE = "MAINTENANCE"; OFFLINE = "OFFLINE"

class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"; DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"; DEAD = "DEAD"
```

### §2.4 Symptom-, Hypothesis-, Dimension-Enums

```python
class SymptomType(str, Enum):
    INITIAL_SWEEP = "INITIAL_SWEEP"; WEISSRAUM = "WEISSRAUM"
    FRACTURE_GAP = "FRACTURE_GAP"; SATURATION = "SATURATION"
    BRIDGE_OPP = "BRIDGE_OPP"; TWIN_DRIFT = "TWIN_DRIFT"
    CAPABILITY_GAP_FEEDBACK = "CAPABILITY_GAP_FEEDBACK"
    DIMENSION_GAP = "DIMENSION_GAP"
    REPLICATE_DIVERGENCE = "REPLICATE_DIVERGENCE"   # v0.3.0 SL-SIG-5
    QUARANTINE_BLOCK = "QUARANTINE_BLOCK"           # v0.3.0 §5.6

class HypothesisStatus(str, Enum):
    PROPOSED = "PROPOSED"; ACTIVE = "ACTIVE"
    CONFIRMED = "CONFIRMED"; REFUTED = "REFUTED"; ARCHIVED = "ARCHIVED"

class DimensionRequestStatus(str, Enum):
    PROPOSED = "PROPOSED"; APPROVED = "APPROVED"
    REJECTED = "REJECTED"; ESCALATED = "ESCALATED"; COOLDOWN = "COOLDOWN"

class DimensionValueType(str, Enum):
    NUMERIC = "NUMERIC"; CATEGORICAL = "CATEGORICAL"; ORDINAL = "ORDINAL"
```

### §2.5 Eskalations- & Constraint-Enums

```python
class EscalationType(str, Enum):
    BUDGET = "BUDGET"; DIMENSION_PHYSICAL = "DIMENSION_PHYSICAL"
    ABORT_CONFIRM = "ABORT_CONFIRM"; SAFETY_EVENT = "SAFETY_EVENT"
    DEADLOCK = "DEADLOCK"; CAPEX = "CAPEX"
    MANIFEST_EXPIRED = "MANIFEST_EXPIRED"; QUARANTINE_EXIT = "QUARANTINE_EXIT"
    LLM_FAILURE = "LLM_FAILURE"; STRATEGIC_QUESTION = "STRATEGIC_QUESTION"
    TWIN_UNCALIBRATABLE = "TWIN_UNCALIBRATABLE"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    CAPABILITY_DELIVERY = "CAPABILITY_DELIVERY"
    TEMPLATE_GAP = "TEMPLATE_GAP"

class EscalationStatus(str, Enum):
    PENDING = "PENDING"; ANSWERED = "ANSWERED"; TIMED_OUT = "TIMED_OUT"

class EscalationCategory(str, Enum):
    DEADLOCK = "DEADLOCK"; STRATEGIC_QUESTION = "STRATEGIC_QUESTION"
    RISK_ACCEPTANCE = "RISK_ACCEPTANCE"
# Hinweis (K7-F-06): STRATEGIC_QUESTION erscheint sowohl als EscalationType
# als auch als EscalationCategory — getreue Übernahme aus v0.3.0 §11.6.

class ConstraintOperator(str, Enum):
    GE = "GE"; LE = "LE"; GT = "GT"; LT = "LT"; EQ = "EQ"; RANGE = "RANGE"

class EnforcementType(str, Enum):
    EXCLUSION = "EXCLUSION"; SAFETY = "SAFETY"; BOUNDS = "BOUNDS"

class RiskLevel(str, Enum):
    LOW = "LOW"; MEDIUM = "MEDIUM"; HIGH = "HIGH"
```

### §2.6 Forschungs-Enums

```python
class FrontierType(str, Enum):
    EXPLORE = "EXPLORE"; OPTIMIZE = "OPTIMIZE"
    DIAGNOSE = "DIAGNOSE"; REPLICATE = "REPLICATE"   # v0.2.0 §19 SL-REP-1
```

### §2.7 ControlState-Achsen-Enums (für 40_control)

```python
class SafetyAxis(str, Enum):
    NORMAL = "NORMAL"; SAFE_MODE = "SAFE_MODE"; ESTOP_LOCKED = "ESTOP_LOCKED"

class ResourceAxis(str, Enum):
    FUNDED = "FUNDED"; INCUBATING = "INCUBATING"
    PHYSICAL_WAIT = "PHYSICAL_WAIT"; BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"

class ResearchAxis(str, Enum):
    BOOTSTRAP = "BOOTSTRAP"; EXPLORATION = "EXPLORATION"
    EXPLOITATION = "EXPLOITATION"; SATURATION = "SATURATION"

class GovernanceAxis(str, Enum):
    AUTONOMOUS = "AUTONOMOUS"; AWAITING_HUMAN = "AWAITING_HUMAN"
    CONFLICT_LOCK = "CONFLICT_LOCK"
```

### §2.8 OwnerAxis (für Single Ownership)

```python
class OwnerAxis(str, Enum):
    GLOBAL = "GLOBAL"          # Konstante/Schwelle, keine Achse setzt sie zur Laufzeit
    SAFETY = "SAFETY"          # SafetyAxis-besessen (absolute Gates)
    RESOURCE = "RESOURCE"      # ResourceAxis-besessen
    RESEARCH = "RESEARCH"      # ResearchAxis-besessen
    GOVERNANCE = "GOVERNANCE"  # GovernanceAxis-besessen
```

---

## §3 ControlState-Verträge (KANONISCHE QUELLE)

> **Single Source of Truth (K7-F-01 behoben):** `ControlState` und `ControlStateLog` sind **ausschließlich hier** definiert. `40_control` referenziert diese Verträge und definiert sie nicht selbst. *(Folgeauftrag: `40_control §1.2/§8` muss die dortige Duplikat-Definition entfernen und auf `20_contracts §3` verweisen.)*

```python
class ControlState(BaseModel):
    safety: SafetyAxis
    resource: ResourceAxis
    research: ResearchAxis
    governance: GovernanceAxis
    updated_at: str
    # Abgeleitetes Feld (K7-F-04): wird durch compute_phase_label (40_control §6)
    # aus den vier Achsen berechnet. Es ist NICHT authoritativ; bei Abweichung
    # von der Ableitung wird es vom Kanzler neu berechnet. Nur für Briefing/Report.
    phase_label: str = ""

class AxisTransition(BaseModel):
    transition_id: str
    axis: Literal["SAFETY", "RESOURCE", "RESEARCH", "GOVERNANCE"]
    from_value: str
    to_value: str
    # K7-F-05: Kanzler ist deterministisch (SL-GATE-1) → trigger_reason ist
    # template-basiert aus strukturierten Daten, kein freier LLM-Text.
    trigger_reason: str                    # template-basiert, max 512, Scan
    triggered_by: Literal["KANZLER", "KOENIGIN", "MENSCH", "SYSTEM", "HAL"]
    timestamp: str

class ControlStateLog(BaseModel):
    mission_id: str
    transitions: list[AxisTransition] = []
    current_state: ControlState            # authoritativ
    updated_at: str
```

---

## §4 StrategicLayerConfig mit owner_axis

### §4.1 Mechanismus

Jeder Config-Parameter trägt eine `owner_axis`-Deklaration über die **ParameterOwnershipMatrix**. Der SL-DEP-Lint (§1) prüft die Vollständigkeit.

**Semantik von `owner_axis`:** Die Besitzer-Achse ist diejenige, die den Parameter **zur Laufzeit setzt**. Parameter, die nur Schwellen/Konstanten sind und nicht zur Laufzeit gesetzt werden, sind `GLOBAL`. *(Klarstellung zu K7-F-08.)*

```python
class ParameterOwnershipEntry(BaseModel):
    parameter: str
    owner_axis: OwnerAxis
    default: Any
    notes: str = ""                        # Scan

class ParameterOwnershipMatrix(BaseModel):
    entries: list[ParameterOwnershipEntry]
    version: str
```

### §4.2 StrategicLayerConfig (vollständig)

```python
class StrategicLayerConfig(BaseModel):
    # --- Zyklen und Briefings (GLOBAL) ---
    briefing_interval_cycles: int = 25
    max_briefing_chars: int = 8192
    urgent_cooldown_cycles: int = 3
    cycle_trigger: str = "EVENT_COUNT"              # TIME | EVENT_COUNT | MANUAL

    # --- Anchor (GLOBAL) ---
    royal_log_anchor_depth: int = 3

    # --- Direktiven (GLOBAL / GOVERNANCE) ---
    directive_ttl_cycles_default: int = 10
    conflict_window_cycles: int = 10
    no_action_stall_limit: int = 4
    max_consecutive_llm_failures: int = 3

    # --- Trigger-Schwellwerte (GLOBAL) ---
    weissraum_min_coverage: float = 0.0
    bridge_edge_threshold: int = 2
    saturation_source: str = "TOPIC_STOP_CONDITION"
    full_rebuild_threshold: float = 0.85
    degraded_threshold: float = 0.60
    quarantine_threshold: float = 0.75

    # --- Budget (RESOURCE-Schwellen) ---
    budget_unlock_threshold_fraction: float = 0.10
    stagnation_budget_threshold: float = 0.80
    diagnostic_budget_default: int = 3
    diagnostic_budget_max: int = 12
    capability_gap_repeat_limit: int = 3
    max_concurrent_packages: int = 1

    # --- Dimensionen (GLOBAL) ---
    max_dimension_requests_per_topic_per_cycle: int = 2
    max_dimension_requests_per_topic_total: int = 10    # v0.3.0 SL-DIM-11
    bootstrap_retry_limit: int = 3

    # --- Quarantäne (GLOBAL) ---
    quarantine_max_cycles: int = 30

    # --- Replikation (GLOBAL-Schwellen) ---
    replication_trigger_progress: float = 0.8
    replication_cadence_cycles: int = 5

    # --- Twin (GLOBAL) ---
    twin_pairing_ttl_cycles: int = 10
    calibration_alert_threshold: float = 0.5
    twin_epsilon_default: float = 1e-6
    twin_abs_tolerance_default: float = 0.05
    twin_calibration_max_attempts: int = 3
    twin_drift_reduction_min: float = 0.20
    twin_late_pairing_window_cycles: int = 15

    # --- Eskalation und Abschluss (GLOBAL) ---
    escalation_timeout_cycles: int = 50
    escalation_reminder_interval_cycles: int = 10
    escalation_reminder_cap: int = 5
    review_reminder_interval_cycles: int = 20
    review_grace_max_cycles: int = 40
    cold_storage_window_days: int = 30

    # --- Kontext-Budget (GLOBAL) ---
    manifest_max_chars: int = 4096
    anchor_max_chars: int = 2048
    max_total_context_chars: int = 14336

    # --- Briefing-Inhalte (GLOBAL) ---
    active_hypothesis_top_n: int = 5
    in_flight_packages_max: int = 10
    top_crystal_count: int = 10
    semantic_dedup_window_cycles: int = 10

    # --- RESEARCH-besetzte Parameter (ResearchAxis setzt zur Laufzeit) ---
    exploration_weight: float = 0.5
    exploitation_weight: float = 0.5
    require_atlas_grounding: bool = True
    replicate_divergence_check: bool = True
    metric_tolerance_multiplier: float = 1.0
    replication_weight: float = 0.35
    min_confirmations: int = 2

    # --- RESOURCE-besetzte Parameter (ResourceAxis setzt zur Laufzeit) ---
    burn_rate_multiplier: float = 1.0
    physical_dispatch_allowed: bool = True
    escalation_timeout_multiplier: float = 1.0

    # --- GOVERNANCE-besetzte Parameter (GovernanceAxis setzt zur Laufzeit) ---
    stall_detection_active: bool = True

    # --- Achsen-Trigger-Schwellen (GLOBAL) ---
    bootstrap_exit_crystals: int = 3
    bootstrap_exit_cycles: int = 5
    exploitation_entry_whitespace: float = 0.20

    # --- Liveness (GLOBAL) ---
    liveness_watchdog_hours: int = 12
```

> **K7-F-08 behoben:** `effective_no_action_stall_limit` wurde **entfernt**. Stall-Detektion wird ausschließlich über `stall_detection_active` (GOVERNANCE-besetzter Boolean) + `no_action_stall_limit` (GLOBAL-Konstante) gesteuert. Das Problem, `∞` als `int` darstellen zu müssen, entfällt.

### §4.3 ParameterOwnershipMatrix (vollständig)

```python
OWNERSHIP_MATRIX = ParameterOwnershipMatrix(
    version="1.1.0",
    entries=[
        # === RESEARCH-besetzt (ResearchAxis setzt zur Laufzeit) ===
        ParameterOwnershipEntry(parameter="exploration_weight", owner_axis=OwnerAxis.RESEARCH, default=0.5),
        ParameterOwnershipEntry(parameter="exploitation_weight", owner_axis=OwnerAxis.RESEARCH, default=0.5),
        ParameterOwnershipEntry(parameter="require_atlas_grounding", owner_axis=OwnerAxis.RESEARCH, default=True),
        ParameterOwnershipEntry(parameter="replicate_divergence_check", owner_axis=OwnerAxis.RESEARCH, default=True),
        ParameterOwnershipEntry(parameter="metric_tolerance_multiplier", owner_axis=OwnerAxis.RESEARCH, default=1.0),
        ParameterOwnershipEntry(parameter="replication_weight", owner_axis=OwnerAxis.RESEARCH, default=0.35),
        ParameterOwnershipEntry(parameter="min_confirmations", owner_axis=OwnerAxis.RESEARCH, default=2),
        # === RESOURCE-besetzt (ResourceAxis setzt zur Laufzeit) ===
        ParameterOwnershipEntry(parameter="burn_rate_multiplier", owner_axis=OwnerAxis.RESOURCE, default=1.0),
        ParameterOwnershipEntry(parameter="physical_dispatch_allowed", owner_axis=OwnerAxis.RESOURCE, default=True),
        ParameterOwnershipEntry(parameter="escalation_timeout_multiplier", owner_axis=OwnerAxis.RESOURCE, default=1.0),
        # === GOVERNANCE-besetzt (GovernanceAxis setzt zur Laufzeit) ===
        ParameterOwnershipEntry(parameter="stall_detection_active", owner_axis=OwnerAxis.GOVERNANCE, default=True),
        # === SAFETY-besetzt (absolute Gates, berechnet, keine Config-Defaults) ===
        ParameterOwnershipEntry(parameter="safety_dispatch_allowed", owner_axis=OwnerAxis.SAFETY, default=True,
                                notes="berechnetes Gate aus SafetyAxis-Zustand"),
        ParameterOwnershipEntry(parameter="safety_intent_blocklist", owner_axis=OwnerAxis.SAFETY, default=[],
                                notes="berechnete Blockliste aus SafetyAxis-Zustand"),
        # === GLOBAL (Konstanten/Schwellen, nicht zur Laufzeit gesetzt) ===
        ParameterOwnershipEntry(parameter="briefing_interval_cycles", owner_axis=OwnerAxis.GLOBAL, default=25),
        ParameterOwnershipEntry(parameter="max_briefing_chars", owner_axis=OwnerAxis.GLOBAL, default=8192),
        ParameterOwnershipEntry(parameter="urgent_cooldown_cycles", owner_axis=OwnerAxis.GLOBAL, default=3),
        ParameterOwnershipEntry(parameter="cycle_trigger", owner_axis=OwnerAxis.GLOBAL, default="EVENT_COUNT"),
        ParameterOwnershipEntry(parameter="royal_log_anchor_depth", owner_axis=OwnerAxis.GLOBAL, default=3),
        ParameterOwnershipEntry(parameter="directive_ttl_cycles_default", owner_axis=OwnerAxis.GLOBAL, default=10),
        ParameterOwnershipEntry(parameter="conflict_window_cycles", owner_axis=OwnerAxis.GLOBAL, default=10),
        ParameterOwnershipEntry(parameter="no_action_stall_limit", owner_axis=OwnerAxis.GLOBAL, default=4),
        ParameterOwnershipEntry(parameter="max_consecutive_llm_failures", owner_axis=OwnerAxis.GLOBAL, default=3),
        ParameterOwnershipEntry(parameter="weissraum_min_coverage", owner_axis=OwnerAxis.GLOBAL, default=0.0),
        ParameterOwnershipEntry(parameter="bridge_edge_threshold", owner_axis=OwnerAxis.GLOBAL, default=2),
        ParameterOwnershipEntry(parameter="saturation_source", owner_axis=OwnerAxis.GLOBAL, default="TOPIC_STOP_CONDITION"),
        ParameterOwnershipEntry(parameter="full_rebuild_threshold", owner_axis=OwnerAxis.GLOBAL, default=0.85),
        ParameterOwnershipEntry(parameter="degraded_threshold", owner_axis=OwnerAxis.GLOBAL, default=0.60),
        ParameterOwnershipEntry(parameter="quarantine_threshold", owner_axis=OwnerAxis.GLOBAL, default=0.75),
        ParameterOwnershipEntry(parameter="budget_unlock_threshold_fraction", owner_axis=OwnerAxis.GLOBAL, default=0.10),
        ParameterOwnershipEntry(parameter="stagnation_budget_threshold", owner_axis=OwnerAxis.GLOBAL, default=0.80),
        ParameterOwnershipEntry(parameter="diagnostic_budget_default", owner_axis=OwnerAxis.GLOBAL, default=3),
        ParameterOwnershipEntry(parameter="diagnostic_budget_max", owner_axis=OwnerAxis.GLOBAL, default=12),
        ParameterOwnershipEntry(parameter="capability_gap_repeat_limit", owner_axis=OwnerAxis.GLOBAL, default=3),
        ParameterOwnershipEntry(parameter="max_concurrent_packages", owner_axis=OwnerAxis.GLOBAL, default=1),
        ParameterOwnershipEntry(parameter="max_dimension_requests_per_topic_per_cycle", owner_axis=OwnerAxis.GLOBAL, default=2),
        ParameterOwnershipEntry(parameter="max_dimension_requests_per_topic_total", owner_axis=OwnerAxis.GLOBAL, default=10),
        ParameterOwnershipEntry(parameter="bootstrap_retry_limit", owner_axis=OwnerAxis.GLOBAL, default=3),
        ParameterOwnershipEntry(parameter="quarantine_max_cycles", owner_axis=OwnerAxis.GLOBAL, default=30),
        ParameterOwnershipEntry(parameter="replication_trigger_progress", owner_axis=OwnerAxis.GLOBAL, default=0.8),
        ParameterOwnershipEntry(parameter="replication_cadence_cycles", owner_axis=OwnerAxis.GLOBAL, default=5),
        ParameterOwnershipEntry(parameter="twin_pairing_ttl_cycles", owner_axis=OwnerAxis.GLOBAL, default=10),
        ParameterOwnershipEntry(parameter="calibration_alert_threshold", owner_axis=OwnerAxis.GLOBAL, default=0.5),
        ParameterOwnershipEntry(parameter="twin_epsilon_default", owner_axis=OwnerAxis.GLOBAL, default=1e-6),
        ParameterOwnershipEntry(parameter="twin_abs_tolerance_default", owner_axis=OwnerAxis.GLOBAL, default=0.05),
        ParameterOwnershipEntry(parameter="twin_calibration_max_attempts", owner_axis=OwnerAxis.GLOBAL, default=3),
        ParameterOwnershipEntry(parameter="twin_drift_reduction_min", owner_axis=OwnerAxis.GLOBAL, default=0.20),
        ParameterOwnershipEntry(parameter="twin_late_pairing_window_cycles", owner_axis=OwnerAxis.GLOBAL, default=15),
        ParameterOwnershipEntry(parameter="escalation_timeout_cycles", owner_axis=OwnerAxis.GLOBAL, default=50),
        ParameterOwnershipEntry(parameter="escalation_reminder_interval_cycles", owner_axis=OwnerAxis.GLOBAL, default=10),
        ParameterOwnershipEntry(parameter="escalation_reminder_cap", owner_axis=OwnerAxis.GLOBAL, default=5),
        ParameterOwnershipEntry(parameter="review_reminder_interval_cycles", owner_axis=OwnerAxis.GLOBAL, default=20),
        ParameterOwnershipEntry(parameter="review_grace_max_cycles", owner_axis=OwnerAxis.GLOBAL, default=40),
        ParameterOwnershipEntry(parameter="cold_storage_window_days", owner_axis=OwnerAxis.GLOBAL, default=30),
        ParameterOwnershipEntry(parameter="manifest_max_chars", owner_axis=OwnerAxis.GLOBAL, default=4096),
        ParameterOwnershipEntry(parameter="anchor_max_chars", owner_axis=OwnerAxis.GLOBAL, default=2048),
        ParameterOwnershipEntry(parameter="max_total_context_chars", owner_axis=OwnerAxis.GLOBAL, default=14336),
        ParameterOwnershipEntry(parameter="active_hypothesis_top_n", owner_axis=OwnerAxis.GLOBAL, default=5),
        ParameterOwnershipEntry(parameter="in_flight_packages_max", owner_axis=OwnerAxis.GLOBAL, default=10),
        ParameterOwnershipEntry(parameter="top_crystal_count", owner_axis=OwnerAxis.GLOBAL, default=10),
        ParameterOwnershipEntry(parameter="semantic_dedup_window_cycles", owner_axis=OwnerAxis.GLOBAL, default=10),
        ParameterOwnershipEntry(parameter="bootstrap_exit_crystals", owner_axis=OwnerAxis.GLOBAL, default=3),
        ParameterOwnershipEntry(parameter="bootstrap_exit_cycles", owner_axis=OwnerAxis.GLOBAL, default=5),
        ParameterOwnershipEntry(parameter="exploitation_entry_whitespace", owner_axis=OwnerAxis.GLOBAL, default=0.20),
        ParameterOwnershipEntry(parameter="liveness_watchdog_hours", owner_axis=OwnerAxis.GLOBAL, default=12),
    ]
)
```

> **K7-F-09 behoben:** Die Matrix ist jetzt vollständig (alle ~55 Parameter). Der SL-DEP-Lint (COMP-01) ist damit ausführbar.

### §4.4 exploration_weight-Konflikt (K7-F-07 behoben)

`exploration_weight` ist **RESEARCH-besetzt**. Die Rule `SL-DTT` (in `30_rules`) setzt den Wert **nicht mehr direkt**. Stattdessen:
- Die ResearchAxis besitzt `exploration_weight` und setzt ihn zustandsabhängig (BOOTSTRAP 0.5, EXPLORATION 0.9, EXPLOITATION 0.2, SATURATION 0.0 — Werte in `40_control §4.1`).
- Der v0.2.0 §6.4 SL-DTT-Eintrag „INITIAL_SWEEP → exploration_weight = 0.90" wird in `30_rules` so umgeschrieben, dass `INITIAL_SWEEP` den **ResearchAxis-Übergang** auslöst, nicht den Wert direkt setzt.
- **Single Ownership gewahrt:** genau ein Besitzer (ResearchAxis).

---

## §5 Phantom-Verträge (KV2-02-Auflösung)

### §5.1 UnlockDecision *(NEU-DESIGN, K7-F-10: in v0.3.0 referenziert, nie definiert)*

```python
class UnlockDecision(BaseModel):
    unlock_id: str
    escalation_ref: str                     # referenziert SAFETY_EVENT/QUARANTINE_EXIT
    zone_refs: list[str]                    # zu entsperrende Zonen
    conditions: str                         # template-basiert, max 1024, Scan
    approved_by: str                        # immer Mensch
    approved_at: str
```

### §5.2 MetricConstraint *(NEU-DESIGN; K7-F-11: Binärgate-Semantik explizit)*

```python
class MetricConstraint(BaseModel):
    constraint_id: str
    metric_ref: str                         # referenziert MetricDefinition
    operator: ConstraintOperator            # GE/LE/GT/LT/EQ
    value: float                            # Schwellwert
    description: str = ""                   # max 256, Scan
    # Semantik (v0.3.0 §3.7, SL-SIG-4): binäres Gate. Das Ergebnis ist
    # ausschließlich erfüllt/nicht-erfüllt. Ein verletztes Constraint
    # verhindert ziel_erreicht=true unabhängig vom Weighted-Sum.
```

### §5.3 DimensionSpec *(NEU-DESIGN; K7-F-12: parent_dimension ergänzt)*

```python
class DimensionSpec(BaseModel):
    dimension_id: str
    display_name: str
    value_type: DimensionValueType
    unit: Optional[str] = None
    initial_range: Optional[tuple[float, float]] = None   # NUMERIC
    initial_categories: Optional[list[str]] = None         # CATEGORICAL
    is_context_dimension: bool = False      # z.B. lab_ambient_temp
    is_integrity_dim: bool = False          # template-deklariert (SL-SIG-6)
    parent_dimension: Optional[str] = None  # NEU: abgeleitete Dimension (SL-DIM-8)
```

### §5.4 MetricDefinition *(NEU-DESIGN; hysteresis_band validierungspflichtig)*

```python
class MetricDefinition(BaseModel):
    metric_id: str
    display_name: str
    unit: str
    direction: Literal["MAXIMIZE", "MINIMIZE"]
    tolerance: float                        # Pflicht (SL-SIG-5, SL-TWIN-2)
    target: Optional[float] = None
    is_binary_gate: bool = False
    # NEU-DESIGN (KV2-05/FIND-BIO-23): verhindert Gate-Flip bei Messrauschen.
    # In v0.3.0 nicht angelegt; validierungspflichtig in 30_rules.
    hysteresis_band: Optional[float] = None
```

### §5.5 DirectiveParameters als discriminierte Union *(K7-F-13 behoben)*

```python
class GridSpec(BaseModel):
    dimensions: list[str]
    levels: dict[str, list[float]]
    template_ref: str

class NoActionParams(BaseModel):
    intent: Literal[DirectiveIntent.NO_ACTION]

class InitialSweepParams(BaseModel):
    intent: Literal[DirectiveIntent.INITIAL_SWEEP]
    grid_spec: GridSpec                     # v0.3.0 SL-DIR-9: ersetzt dimensions+levels
    sweep_template_ref: str

class PivotDomainParams(BaseModel):
    intent: Literal[DirectiveIntent.PIVOT_DOMAIN]
    from_topic_ref: str
    to_topic_seed: TopicSeed

class PivotTargetParams(BaseModel):
    intent: Literal[DirectiveIntent.PIVOT_TARGET]
    from_topic_ref: str
    to_topic_seed: TopicSeed

class UnlockBudgetParams(BaseModel):
    intent: Literal[DirectiveIntent.UNLOCK_BUDGET]
    amount_cycles: int
    purpose: str                            # max 512, Scan

class AbortMissionParams(BaseModel):
    intent: Literal[DirectiveIntent.ABORT_MISSION]
    reason: str                             # max 1024, Scan

class AddDimensionHintParams(BaseModel):
    intent: Literal[DirectiveIntent.ADD_DIMENSION_HINT]
    source_ref: str
    dimension_seed: str

class IncreaseDiagnosticParams(BaseModel):
    intent: Literal[DirectiveIntent.INCREASE_DIAGNOSTIC]
    zone_ref: str
    amount: int

class CalibrateTwinParams(BaseModel):
    intent: Literal[DirectiveIntent.CALIBRATE_TWIN]
    twin_ref: str

class ArchiveTopicParams(BaseModel):
    intent: Literal[DirectiveIntent.ARCHIVE_TOPIC]
    topic_ref: str

class SetPriorityParams(BaseModel):
    intent: Literal[DirectiveIntent.SET_PRIORITY]
    topic_ref: str
    priority: float

class DropSoftPreferenceParams(BaseModel):
    intent: Literal[DirectiveIntent.DROP_SOFT_PREFERENCE]
    preference_ref: str

class HumanEscalationParams(BaseModel):
    intent: Literal[DirectiveIntent.HUMAN_ESCALATION]
    question: str                           # max 1024, Scan
    escalation_category: EscalationCategory # v0.3.0 §11.6 Pflicht

class SetResearchPhaseParams(BaseModel):
    intent: Literal[DirectiveIntent.SET_RESEARCH_PHASE]
    target_phase: ResearchAxis
    reason: str                             # max 512, Scan

DirectiveParameters = Annotated[
    Union[
        NoActionParams, InitialSweepParams, PivotDomainParams, PivotTargetParams,
        UnlockBudgetParams, AbortMissionParams, AddDimensionHintParams,
        IncreaseDiagnosticParams, CalibrateTwinParams, ArchiveTopicParams,
        SetPriorityParams, DropSoftPreferenceParams, HumanEscalationParams,
        SetResearchPhaseParams,
    ],
    Field(discriminator="intent")
]
```

> **K7-F-13 behoben:** `DirectiveParameters` ist jetzt eine echte discriminierte Union (Discriminator `intent`). Validierungsstufe 1 erzwingt die Intent-Pflichtparameter maschinell (SL-DIR-9).

### §5.6 crystallization_progress *(K7-F-14: Version-Pin korrigiert)*

```
crystallization_progress(zone) =
    clamp( 0.0, 1.0,
           best_objective_distance(zone) × evidence_mass_factor(zone) )

  best_objective_distance(zone) = Abstand des besten Kristalls der Zone
                                  zum ObjectiveFamily-Ziel (normiert 0..1)
  evidence_mass_factor(zone)     = min(1.0, crystal_count(zone) / min_confirmations)

Version-Pin: CONTRACTS 1.1.0-atlas-hyb.1 (SL-DEP-1-konform, exakter Pin)
```

---

## §6 Mission-Verträge

```python
class ManifestConstraint(BaseModel):
    constraint_id: str
    dimension_ref: Optional[str] = None       # None = missionsweite Regel
    operator: ConstraintOperator
    value: Optional[float] = None
    range: Optional[tuple[float, float]] = None
    categories: Optional[list[str]] = None
    enforcement: EnforcementType
    description: str                          # max 512, Scan

class SoftPreference(BaseModel):
    preference_id: str                        # entspricht v0.3.0 §17 "{id, text}";
                                              # preference_ref referenziert diese ID
    text: str                                 # max 256, Scan

class ObjectiveSpec(BaseModel):
    metric_ref: str
    direction: Literal["MAXIMIZE", "MINIMIZE"]
    target: Optional[float] = None
    weight: float = 1.0

class ObjectiveFamilySeed(BaseModel):
    family_id: str
    objectives: list[ObjectiveSpec]
    metric_constraints: list[MetricConstraint]   # binäres Gate, SL-SIG-4
    aggregation: AggregationType

class TopicSeed(BaseModel):
    seed_id: str
    objective_family_ref: str
    scope_description: str                    # max 1024, Scan
    suggested_dimensions: list[str]

class TopicConstraintProposal(BaseModel):
    proposal_id: str
    source_topic_ref: str
    constraint: ManifestConstraint
    origin: Literal["LESSONS_LEARNED"] = "LESSONS_LEARNED"
    status: Literal["PROPOSED", "ACTIVE", "OVERRULED"] = "PROPOSED"

class ResearchManifest(BaseModel):
    manifest_id: str
    mission_goal: str                         # max 2048, Scan
    hard_constraints: list[ManifestConstraint]
    soft_preferences: list[SoftPreference] = []   # v0.3.0 §17
    objective_family_seed: ObjectiveFamilySeed
    initial_dimensions: list[DimensionSpec]
    domain: str
    valid_from: str
    valid_until: Optional[str] = None
    created_by: str                           # immer Mensch
    approved_by: str                          # immer Mensch
    version: str
    created_at: str
    updated_at: str
```

---

## §7 Briefing-Verträge *(NEU in v1.1.0 — K7-F-18/-19/-20/-21 behoben)*

> **Vollständig definiert aus v0.2.0 §6.2, mit allen v0.3.0-Änderungen eingearbeitet. Das tote Feld `zyklus_id` ist gestrichen (KV-16 bereinigt, K7-F-20 behoben).**

```python
class SlotOutage(BaseModel):
    slot_id: str
    state: SlotOutageState
    since: str

class AtlasMacroState(BaseModel):
    total_zones: int
    healthy_zones: int
    degraded_zones: int
    critical_zones: int
    locked_zones: int
    quarantined_zones: int
    unexplored_zones: int
    avg_fracture_score: Optional[float] = None
    avg_uncertainty_score: Optional[float] = None   # v0.3.0 §3.6: Optional (leerer Atlas)
    total_crystals: int
    total_hypotheses: int
    total_digital_twins: int
    drifted_twins: int
    frontier_candidates_count: int
    vordenker_calibration_score: Optional[float] = None   # 0.0–1.0

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
    progress_percent: float          # deterministisch, 0–100
    best_objective_distance: float   # deterministisch
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

class HardwareHealth(BaseModel):
    slot_outages: list[SlotOutage] = []
    questor_health_status: HealthStatus
    operational_failure_count_recent: int    # verzerrt KEINE wissenschaftlichen Metriken

class DecisionOption(BaseModel):
    option_id: str
    description: str                 # template-basiert, max 512, Scan
    impact: str                      # template-basiert, max 512
    risk_level: RiskLevel
    requires_human_approval: bool

class RoyalLogAnchor(BaseModel):
    entry_ref: str
    origin: OriginType               # QUEEN | HUMAN
    intent: Optional[DirectiveIntent] = None   # None bei HUMAN_OVERRIDE-Freitextweisung
    summary: str                     # max 256 Zeichen
    outcome: Optional[DirectiveOutcome] = None
    age_cycles: int

class InFlightPackageSummary(BaseModel):      # v0.3.0 §10 SL-PKG-1
    package_id: str
    zone_ref: str
    topic_ref: str
    manifest_version_started: str
    gate_mode: str
    twin_invalidated: bool = False            # v0.3.0 §6.5 SL-TWIN-10 (K7-F-21 behoben)

class StrategicBriefing(BaseModel):
    briefing_id: str                          # einzige Zyklen-ID (v0.3.0 SL-DEF-4)
    # zyklus_id GESTRICHEN (v0.3.0 SL-DEF-4, KV-16; K7-F-20 behoben)
    briefing_type: BriefingType
    manifest_version_ref: str
    atlas_macro_state: AtlasMacroState
    budget_state: BudgetState
    topics: list[TopicSummary] = []
    active_fractures: list[FractureSummary] = []
    twin_status: list[TwinStatusSummary] = []
    hardware_health: HardwareHealth
    in_flight_packages: list[InFlightPackageSummary] = []   # v0.3.0 §10 SL-PKG-1
    active_hypothesis_refs: list[str] = []                  # v0.3.0 §13 SL-BRF-10 (Top-N)
    decisions_required: list[DecisionOption] = []
    royal_log_anchor: list[RoyalLogAnchor] = []
    pending_escalations: list[str] = []
    truncation_applied: bool = False
    generated_at: str
    generated_by: str                                       # immer "KANZLER"
```

**Briefing-Sanitization (SL-BRF-1..6, übernommen aus v0.2.0 §6.2):** Verboten in jedem Briefing sind `security_mode`, Atlas-Hybrid-Referenzfelder und Roh-`metric_vector`. Fortschritt wird als deterministische Skalare übergeben. Trunkierung nach `SL-BRF-4` (v0.3.0 §13: Trunkierungspriorität v2). Direktiven auf trunkierten Briefings markiert die DTT als `provisional=true` (v0.3.0 SL-BRF-9; das Feld liegt an der Direktiven-Übersetzung, §10).

---

## §8 Directive-Verträge (mit discriminierte Union)

```python
class StrategicDirective(BaseModel):
    directive_id: str
    briefing_ref: str
    intent: DirectiveIntent
    target_ref: Optional[str] = None
    parameters: DirectiveParameters            # discriminierte Union (§5.5)
    reason: str                                # max 1024, Scan
    drop_soft_preferences: list[str] = []
    valid_for_cycles: int = 10                 # nur andauernde Modifikatoren (SL-DIR-4)
    created_at: str
    # v0.3.0 §17: priority und keep_constraints GESTRICHEN (tote Felder, KV-16)
```

> `provisional` (v0.3.0 SL-BRF-9) ist ein **DTT-Ausgabe-Feld**, kein Feld der Königin-Direktive. Es wird bei der Policy-Übersetzung in `30_rules` gesetzt, wenn `briefing_ref` auf ein trunkiertes Briefing verweist.

---

## §9 Governance-Verträge

```python
class HumanResponseDecision(str, Enum):
    APPROVE = "APPROVE"; REJECT = "REJECT"
    PARTIAL = "PARTIAL"; DEFER = "DEFER"

class ManifestConstraintDelta(BaseModel):
    action: Literal["ADD", "REMOVE", "MODIFY"]
    constraint: Optional[ManifestConstraint] = None
    constraint_id: Optional[str] = None

class HumanResponseFile(BaseModel):
    response_id: str
    escalation_id: str
    decision: HumanResponseDecision
    amount_granted: Optional[int] = None
    constraints_delta: list[ManifestConstraintDelta] = []
    unlock_decision: Optional[UnlockDecision] = None
    scope_refs: list[str] = []
    free_note: str = ""                       # Scan; nur Anchor
    answered_by: str                          # immer Mensch
    answered_at: str

class HumanDirective(BaseModel):
    directive_id: str
    constraint_deltas: list[ManifestConstraintDelta] = []
    topic_freezes: list[str] = []
    dimension_freezes: list[str] = []
    set_research_phase: Optional[ResearchAxis] = None   # 40_control §5.2
    valid_for_cycles: Optional[int] = None
    note: str = ""                            # Scan; nur Anchor
    created_by: str                           # immer Mensch
    created_at: str
    expires_at_cycle: Optional[int] = None

class HumanEscalationRecord(BaseModel):
    escalation_id: str
    escalation_type: EscalationType
    payload_ref: str
    target_ref: Optional[str] = None          # NEU (K7-F-16): für Dedup-Schlüssel
                                              # (escalation_type, target_ref), v0.3.0 §11.6
    status: EscalationStatus = EscalationStatus.PENDING
    created_at: str
    timeout_cycles: int
    answered_by: Optional[str] = None
    answer_ref: Optional[str] = None

class RoyalLogEntry(BaseModel):
    entry_id: str
    origin: OriginType
    directive_ref: Optional[str] = None
    briefing_ref: Optional[str] = None
    outcome: DirectiveOutcome
    outcome_reason: Optional[str] = None      # max 512
    policy_effect_ref: Optional[str] = None
    timestamp: str

class TimeService(BaseModel):                 # v0.3.0 §2.2
    source: str
    now_iso: str
    mission_start_iso: str
```

---

## §10 Forschungs-Verträge

```python
class CapabilityRequirement(BaseModel):
    capability_id: str
    parameter_requirements: dict[str, Any] = {}

class SymptomEvent(BaseModel):
    event_id: str
    symptom_type: SymptomType
    zone_ref: Optional[str] = None
    atlas_refs: list[str] = []
    metrics_snapshot: dict[str, float] = {}
    twin_divergence_report_ref: Optional[str] = None
    created_at: str

class ExpectationSpec(BaseModel):             # v0.3.0 §7.1
    metric_ref: str
    direction: Literal["INCREASE", "DECREASE", "REACH"]
    threshold: Optional[float] = None
    delta: Optional[float] = None

class DimensionOnboardingRequest(BaseModel):
    request_id: str
    proposed_dimension_id: str
    display_name: str
    domain: str
    value_type: DimensionValueType
    unit: Optional[str] = None
    rationale: str                            # max 2048, Scan
    source_ref: str                           # RequestSource-Union: Hypothese ODER Direktive
    source_trigger: SymptomType
    suggested_value_range: Optional[tuple[float, float]] = None
    suggested_categories: Optional[list[str]] = None
    requires_physical_actuation: bool = False
    status: DimensionRequestStatus = DimensionRequestStatus.PROPOSED
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    created_at: str

class ScientificHypothesis(BaseModel):
    hypothesis_id: str
    hypothesis_text: str                      # max 2048, Scan
    expected_outcome: str                     # max 1024
    expectation_spec: Optional[ExpectationSpec] = None   # v0.3.0 SL-HYP-4
    source_trigger: SymptomType
    atlas_refs: list[str] = []
    zone_ref: Optional[str] = None
    required_capabilities: list[CapabilityRequirement]
    dimension_onboarding_request: Optional[DimensionOnboardingRequest] = None
    prozess_skizze: str
    confidence_estimate: float
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    created_at: str

class DimensionExpansionApproval(BaseModel):  # v0.3.0 §15
    request_ref: str
    approver: str                             # immer Mensch bei physischer Nutzung
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

> **K7-F-17 präzisiert:** `source_ref` in `DimensionOnboardingRequest` ist die RequestSource-Union (v0.3.0 §15 SL-DIR-7). Die Union-Semantik wird als Validierungsregel in `30_rules` erzwungen: `source_ref` muss eine existierende Hypothese **oder** Direktive referenzieren.

---

## §11 Budget-, Report-, Registry-Verträge

```python
class MissionBudget(BaseModel):
    mission_id: str
    total_cycles: int
    used_cycles: int
    reserved_cycles: int = 0
    capex_requests: list[CapexRequest] = []
    updated_at: str

class CapexRequest(BaseModel):
    request_id: str
    description: str                          # max 512, Scan
    estimated_cost: str
    requires_human_approval: bool = True
    status: DimensionRequestStatus

class ReportFacts(BaseModel):
    mission_goal_ref: str
    final_objective_values: dict[str, float]
    top_crystal_summaries: list[CrystalSummary]   # N = top_crystal_count (Config)
    rejected_hypotheses_count: int
    twin_calibration_history: list[str] = []
    safety_warnings: list[str] = []
    diagnostic_resolution_summary: list[str] = []

class CrystalSummary(BaseModel):
    crystal_node_ref: str
    objective_values: dict[str, float]
    support_confidence: float
    fracture_score: Optional[float] = None

class FinalScientificReport(BaseModel):
    report_id: str
    topic_ref: str
    manifest_ref: str
    facts: ReportFacts
    executive_summary: str                    # max 4096, Scan
    future_recommendations: str               # max 2048, Scan
    citation_refs: list[str] = []
    generated_at: str
    human_reviewed: bool = False

class CapabilityRegistryEntry(BaseModel):     # v0.3.0 §18 SL-DEP-2
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

---

## §12 Tests (L1, modul-lokal)

| ID | Test | Erwartung |
|---|---|---|
| CON-01 | SL-DEP-Lint: Phantom-Vertrag referenziert | Build-Fail |
| CON-02 | SL-DEP-Lint: Vertrag in zwei Modulen definiert | Build-Fail (K7-F-01) |
| CON-03 | StrategicBriefing vollständig definiert | Schema validiert (K7-F-18) |
| CON-04 | StrategicBriefing enthält in_flight_packages | vorhanden (K7-F-19) |
| CON-05 | StrategicBriefing enthält active_hypothesis_refs | vorhanden |
| CON-06 | StrategicBriefing enthält KEIN zyklus_id | Feld abwesend (K7-F-20) |
| CON-07 | AtlasMacroState.avg_uncertainty_score Optional | Typ Optional[float] |
| CON-08 | InFlightPackageSummary enthält twin_invalidated | vorhanden (K7-F-21) |
| CON-09 | DirectiveParameters ist discriminierte Union | Discriminator "intent" (K7-F-13) |
| CON-10 | InitialSweepParams mit grid_spec | validiert |
| CON-11 | HumanEscalationParams mit escalation_category | validiert (v0.3.0 §11.6) |
| CON-12 | ControlState nur in 20_contracts definiert | keine Dublette (K7-F-01) |
| CON-13 | ParameterOwnershipMatrix vollständig | alle Parameter abgedeckt (K7-F-09) |
| CON-14 | exploration_weight nur RESEARCH-besetzt | kein SL-DTT-Direktzugriff (K7-F-07) |
| CON-15 | effective_no_action_stall_limit entfernt | Feld abwesend (K7-F-08) |
| CON-16 | UnlockDecision definiert | Schema validiert |
| CON-17 | DimensionSpec enthält parent_dimension | vorhanden (K7-F-12) |
| CON-18 | crystallization_progress Version-Pin | "CONTRACTS 1.1.0-atlas-hyb.1" (K7-F-14) |
| CON-19 | HumanEscalationRecord enthält target_ref | vorhanden (K7-F-16) |
| CON-20 | SET_RESEARCH_PHASE in DirectiveIntent | vorhanden |
| CON-21 | StrategicDirective ohne priority/keep_constraints | Felder abwesend (KV-16) |
| CON-22 | SoftPreference-Referenz konsistent | preference_ref → preference_id (K7-F-15) |

---

## §13 Behobene Funde (Traceability)

| Fund | Auflösung |
|---|---|
| KV2-02 | Phantom-Verträge definiert (§5) |
| KV2-03 | StrategicLayerConfig vervollständigt (§4.2) |
| K7-F-01 | ControlState nur in §3; 40_control muss referenzieren |
| K7-F-07 | exploration_weight RESEARCH-besetzt; SL-DTT setzt nicht mehr direkt (§4.4) |
| K7-F-08 | effective_no_action_stall_limit entfernt; stall_detection_active + no_action_stall_limit |
| K7-F-09 | ParameterOwnershipMatrix vollständig (§4.3) |
| K7-F-12 | DimensionSpec.parent_dimension ergänzt (§5.3) |
| K7-F-13 | DirectiveParameters als echte discriminierte Union (§5.5) |
| K7-F-14 | crystallization_progress Version-Pin korrigiert (§5.6) |
| K7-F-15 | SoftPreference-Referenz dokumentiert (§6) |
| K7-F-16 | HumanEscalationRecord.target_ref ergänzt (§9) |
| K7-F-18/19 | Briefing-Verträge vollständig inkl. v0.3.0-Änderungen (§7) |
| K7-F-20 | zyklus_id gestrichen (§7) |
| K7-F-21 | InFlightPackageSummary.twin_invalidated ergänzt (§7) |

**Weiterhin offen** (in `30_rules`/`40_control`): K7-F-05 (trigger_reason Template in 40_control), K7-F-10/11 (NEU-DESIGN-Validierung), K7-F-17 (RequestSource-Union-Validierung in 30_rules), KV2-04 (Budget-Formeln), KV2-10 (Bio-Sequenz-Safety), KV2-07 (EvidenceBundle).

**Folgeauftrag an `40_control`:** §1.2/§8 ControlState-Duplikat entfernen und auf `20_contracts §3` verweisen (K7-F-01 vollständig schließen).

---

## §14 Changelog

| Version | Datum | Änderung | Funde behoben |
|---|---|---|---|
| 1.0.0 | 2025-01-XX | Konsolidierung; Phantom-Verträge; StrategicLayerConfig mit owner_axis | KV2-02, KV2-03, K6-F-19..30 |
| **1.1.0** | **2025-01-XX** | **Briefing-Verträge vollständig (inkl. v0.3.0-Änderungen, zyklus_id gestrichen); DirectiveParameters als discriminierte Union; ControlState kanonisch verortet; ParameterOwnershipMatrix vollständig; exploration_weight-Konflikt aufgelöst; effective_no_action_stall_limit entfernt; target_ref, parent_dimension ergänzt** | **K7-F-01, -07, -08, -09, -12, -13, -14, -15, -16, -18, -19, -20, -21** |

---

**Ende des Contracts-Moduls v1.1.0.**