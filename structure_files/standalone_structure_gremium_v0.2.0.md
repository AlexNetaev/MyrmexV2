# 🏛️ STANDALONE STRUCTURE GREMIUM — COGNITIVE OBSERVATORY

| Feld | Wert |
|---|---|
| Dateiname | `specs/standalone_structure_gremium_v0.2.0.md` |
| Version | 0.2.0 |
| Status | ÄNDERUNGSANTRAG STRATEGIC-LAYER-2.1.0 |
| Vorgänger | v0.1.0 (44 Dry-Tests, 40 Funde), Testkampagne 2 (MOF/DAC, 23 Funde), Testkampagne 3 (Suzuki, 105 Tests, 36 Funde) |
| System | MYRMEX v2.4.0 + Questor v0.2.3 + HAL v0.2.0 |
| Baut auf | CHARTER 1.0.0, CONTRACTS 1.1.0-atlas-hyb.1, GREMIUM 1.1.0-atlas-hyb.1, DIGITAL-TWIN-SEM-1.0.0 |
| Konfliktregel | CHARTER > CONTRACTS > dieses Dokument |

---

## §0 Zweck, Geltung und Selbständigkeit

### §0.1 Zweck

Dieses Dokument definiert die **strategische Kognitionsschicht** des Gremiums („Cognitive Observatory"): ein System, das über Wochen autonom forschen kann — drift-frei, CHARTER-konform, mit deterministischen Endentscheidungen und definierten menschlichen Eingriffspunkten.

### §0.2 Selbständigkeitserklärung

Dieses Dokument ist **abgeschlossen testbar als Einzeldatei**. Es enthält:
- alle neuen Datenverträge vollständig (§6),
- alle Zustandsmaschinen (§21),
- alle Regeln mit eindeutigen IDs (SL-xx),
- alle Konfigurationsparameter mit Defaults (§23),
- alle Datenfluss-Diagramme (§24),
- das Fund-Register mit Behebungsstatus (Anhang A).

Es referenziert CHARTER, CONTRACTS, GREMIUM, QUESTOR, HAL und DIGITAL-TWIN-SEM nur zur Einordnung. Wo dieses Dokument eine Änderung an diesen Dokumenten erfordert, ist sie in §25 als Änderungsantrag explizit gemacht.

### §0.3 Verhältnis zur CHARTER-Präambel

Die CHARTER friert den Scope ein („Keine neuen Features"). Dieses Dokument ist daher ein **formaler Änderungsantrag**. Vor Freigabe gilt es als Backlog v3.0.0. Es ändert **keine** der 58 Sicherheitsregeln; es präzisiert ausschließlich deren Durchsetzung auf Gremium-Ebene.

---

## §1 Grunddefinitionen

### §1.1 Der strategische Zyklus (SL-DEF-1)

**1 Zyklus** = 1 abgeschlossener strategischer Regelkreis:

```text
StrategicBriefing erzeugt → StrategicDirective empfangen → Validierung → Policy-Wirkung
```

Alle Parameter mit der Endung `_cycles` beziehen sich auf diesen Zyklus. Der Zykluszähler ist der fortlaufende `briefing_id`-Zähler der Mission. *(behebt F-35)*

### §1.2 Weißraum (SL-DEF-2)

Eine Region gilt als Weißraum, wenn ihre Zone `UNEXPLORED` ist **oder** `EXPLORED_INCONCLUSIVE` mit `evidence_mass == 0`. *(behebt PROB-05)*

### §1.3 Rollen-Kurzreferenz

| Rolle | Schicht | LLM | Kognitive Funktion |
|---|---|---|---|
| 👑 Königin | 5 | Ja (stateless + constitutional) | Vision, Pivot, Budget-Freigabe-Vorschläge, Abschlussbericht-Entwurf |
| 🏛️ Kanzler | 4 | Nein | Briefing, Validierung, Policy, RoyalLog, Dimension-/Eskalations-Governance |
| 🧠 Vordenker | 4 | Ja (grounded) | Kausale Modelle, Hypothesen, Dimensions-Vorschläge |
| 🧭 Lotse | 4 | Nein | Wegmarken, Capability-Prüfung |
| 📦 Quartiermeister | 4 | Nein | Paketbau, Manifest-/Twin-Checks |
| ⚖️ Sicherheitsrat | 4 | Seher advisor-only | Gate |
| 🗺️ Kartograph | 4 | Nein | Atlas, Symptome, Twin-Divergenz, Kalibrierungs-Tracking |
| 📚 Archivar | 4 | Nein | Wissensaufnahme, Sanitization am Eingang |
| 🧭 Questor | 2 | Advisor-intern | Ausführung (unverändert) |

### §1.4 Zugriffs- und Kommunikationsregeln (SL-ACC-1..4)

- **SL-ACC-1:** Alle Kommunikation zwischen Rängen läuft ausschließlich über Blackboard-Artefakte (Atlas, Archiv, Governance-Verzeichnisse gemäß §20.5). Keine direkten Aufrufe. *(CHARTER §2)*
- **SL-ACC-2:** Die Königin liest den Atlas **nicht direkt**. Ihr einziger Informationszugang ist das `StrategicBriefing`. Die GREMIUM-Zugriffsmatrix (§6.12, Zeile Königin) wird entsprechend präzisiert. *(behebt F-33)*
- **SL-ACC-3:** Der Vordenker liest Atlas-Topologie nur lesend und nur als kuratierte Blackboard-Ausschnitte; er schreibt niemals in den Atlas.
- **SL-ACC-4:** Questor und HAL bleiben vollständig unverändert; sie kennen keine strategischen Verträge.

---

## §2 Architektur-Überblick

```text
┌───────────────────────────────────────────────────────────────────────┐
│  MENSCHLICHE KÖNIGIN / SPONSOR (SR-11: niemals überstimmt)            │
│  • setzt ResearchManifest (einziger Autor von hard_constraints)       │
│  • beantwortet HumanEscalationRecords (data/human_inbox/)             │
│  • HUMAN_OVERRIDE, SAFE_MODE, Manifest-Versionierung                  │
└──────────────────────────────┬────────────────────────────────────────┘
                               ▼
┌───────────────────────────────────────────────────────────────────────┐
│  SCHICHT 5: 👑 KÖNIGIN (LLM, stateless + constitutional)              │
│  IN : ResearchManifest + StrategicBriefing + Anchor (RoyalLog)        │
│  OUT: StrategicDirective (Vorschlag, schema-validiert)                │
└──────────────────────────────┬────────────────────────────────────────┘
                               ▼
┌───────────────────────────────────────────────────────────────────────┐
│  SCHICHT 4: 🏛️ GREMIUM — STRATEGISCHE SCHLEIFE                        │
│                                                                       │
│  KANZLER (deterministisch):                                           │
│    Briefing-Generator · Directive-Validator (7 Stufen) ·              │
│    DirectiveTranslationTable · RoyalLog · MissionBudget ·             │
│    Dimension-Governance · Eskalations-Manager · SAFETY-RESPONSE       │
│                                                                       │
│  KARTOGRAPH: Symptome · TwinDivergenceReports · Kalibrierungs-        │
│              Tracking · REPLICATE-Frontiers                           │
│        │ SymptomEvent (Blackboard)                                    │
│        ▼                                                              │
│  VORDENKER (LLM, grounded): ScientificHypothesis +                    │
│        DimensionOnboardingRequest + required_capabilities             │
│        ▼                                                              │
│  PRE-FILTER → LOTSE (+CapabilityGapSignal) → QUARTIERMEISTER          │
│        (+Manifest-/Twin-Check) → SICHERHEITSRAT → DISPATCH            │
│                                                                       │
│  QUESTOR (Schicht 2) → questor_ergebnis_paket → ARCHIVAR              │
│        (Sanitization am Eingang) → KARTOGRAPH → ATLAS                 │
└───────────────────────────────────────────────────────────────────────┘
```

---

## §3 Constitutional Anchor Protocol (Anti-Drift)

Jeder Königin-LLM-Aufruf erhält **exakt drei** Kontextblöcke (SL-ANCHOR-1):

```text
SCHICHT 1 — CONSTITUTIONAL MEMORY (invariant)
   ResearchManifest: mission_goal (Scan), machine-readable hard_constraints,
   soft_preferences, Verbotene Aktionen, Output-Schema
SCHICHT 2 — STATELESS BRIEFING (dynamisch, kuratiert)
   StrategicBriefing: aggregierter Zustand, Budget, Fractures, Twin-Status,
   DecisionsRequired, Hardware-Health — kein security_mode, keine
   Atlas-Hybrid-Referenzen, kein Roh-metric_vector
SCHICHT 3 — ANCHOR (Kontinuität)
   royal_log_anchor: zuerst alle aktiven HUMAN_OVERRIDE-Einträge,
   dann die letzten royal_log_anchor_depth (=3) eigenen Direktiven
   mit Outcome (IMPLEMENTED/VETOED/SUPERSEDED/EXPIRED/ESCALATED)
```

**Invarianten:**
- **SL-ANCHOR-2:** Kein persistenter Gesprächsverlauf. Jeder Aufruf ist frisch.
- **SL-ANCHOR-3:** Menschliche Weisungen im Anchor überschreiben alle Königin-Direktiven. Der Anchor enthält den expliziten Hinweis: „Menschliche Weisungen haben Vorrang vor allen früheren Direktiven." *(behebt PROB-22)*
- **SL-ANCHOR-4:** Bei LLM-Fehler/Timeout: deterministischer Fallback = aktuelle ExplorationPolicy bleibt unverändert; Audit-Event; kein erweiterter Retry-Kontext. Nach `max_consecutive_llm_failures` → HumanEscalationRecord. *(SR-28)*

---

## §4 Missions-Bootstrap (SL-BOOT-1..6)

Das Bootstrap-Protokoll macht das System kaltstartfähig. *(behebt PROB-02/04, 1.1–1.3, F-01–F-07)*

```text
MENSCH übergibt Ziel
    ▼
SL-BOOT-1: Mensch erstellt ResearchManifest (approved_by = Mensch).
           Die LLM-Königin darf einen ENTWURF formulieren; das Manifest
           wird erst mit menschlicher Freigabe gültig. Kein Self-Injection-Pfad.
    ▼
SL-BOOT-2: Kanzler erzeugt MissionBootstrap:
           • alle in manifest.initial_dimensions genannten Dimensionen
             werden als TypedDimension mit approved = true angelegt
             (die menschliche Manifest-Genehmigung deckt diese Freigabe)
           • ObjectiveFamily aus manifest.objective_family_seed
           • ResearchTopic PROPOSED
           • MissionBudget initialisiert
    ▼
SL-BOOT-3: Kanzler materialisiert jede ManifestConstraint:
           enforcement=EXCLUSION → ExclusionConstraint(hard_limit=true)
           enforcement=SAFETY    → SafetyConstraint(active=true)
           enforcement=BOUNDS    → Package-Bounds-Intersektionsregel
    ▼
SL-BOOT-4: Kanzler erzeugt StrategicBriefing(briefing_type=BOOTSTRAP)
           mit deterministischen DecisionOption-Templates
           (Screening-Strategien statt leerer Listen)
    ▼
SL-BOOT-5: Königin antwortet mit INITIAL_SWEEP.
           Kanzler akzeptiert → Topic PROPOSED → ACTIVE
           (Auslöser des Topic-Übergangs ist immer der Kanzler)
    ▼
SL-BOOT-6: Kanzler (nicht Kartograph) emittiert
           SymptomEvent(symptom_type = INITIAL_SWEEP).
           Vordenker wechselt in SEED-MODUS:
           atlas_refs = [] ist ausschließlich bei INITIAL_SWEEP erlaubt.
           Halluzinierte Knoten-IDs bleiben Fail-Closed verworfen.
```

**Template-Lücke (SL-BOOT-7):** Fehlt beim Paketbau ein Template, wird das Paket zurückgestellt und G-1 (Quartiermeister + Domain-Experte) ausgelöst. Für die Domäne der Mission muss vor Missionsstart mindestens ein Sweep- und ein Diagnose-Template registriert sein (Zulassungsvoraussetzung, geprüft bei SL-BOOT-2). *(behebt PROB-04)*

---

## §5 Kern-Patterns

### §5.1 Stateless Director

Die Königin ist zustandslos (§3). Strategisches Gedächtnis entsteht nur durch Manifest, Anchor und Atlas-Aggregate.

### §5.2 Deterministic Gatekeeper

Der Kanzler ist **rein deterministisch** (SL-GATE-1): kein LLM-Einsatz, auch nicht für Zusammenfassungen. Alle Freitext-Bausteine in Briefings werden template-basiert aus strukturierten Daten erzeugt.

### §5.3 Topology-Grounded Hypothesis Engine

Der Vordenker wird ausschließlich über SymptomEvents aktiviert (§8) und nutzt Topology-Prompting (FRACTURE / VOID / BRIDGE / TWIN_DRIFT / SATURATION) auf kuratierten Atlas-Ausschnitten.

### §5.4 Digital-Twin-Loop

Vollständig gemäß DIGITAL-TWIN-SEM-1.0.0, gehärtet nach §12 dieses Dokuments.

---

## §6 Datenverträge (Änderungsantrag an CONTRACTS §6.11)

> Alle Verträge sind Pydantic-v2-Modelle. Freitextfelder sind markiert (Scan = Injection-Scan + Längenlimit). Neue Enums sind in §6.12 zusammengefasst.

### §6.1 ResearchManifest

```python
class ManifestConstraint(BaseModel):
    constraint_id: str
    dimension_ref: Optional[str] = None       # None = missionsweite Regel
    operator: ConstraintOperator              # GE/LE/GT/LT/EQ/RANGE (CONTRACTS §10)
    value: Optional[float] = None
    range: Optional[tuple[float, float]] = None
    categories: Optional[list[str]] = None    # für kategorische Constraints
    enforcement: EnforcementType              # EXCLUSION | SAFETY | BOUNDS
    description: str                          # Freitext, max 512 Zeichen, Scan

class ResearchManifest(BaseModel):
    manifest_id: str
    mission_goal: str                         # Freitext, max 2048 Zeichen, Scan
    hard_constraints: list[ManifestConstraint]  # MASCHINENLESBAR
    soft_preferences: list[str] = []          # Freitext, je max 256 Zeichen, Scan
    objective_family_seed: ObjectiveFamilySeed
    initial_dimensions: list[DimensionSpec]   # Bootstrap-Basis
    domain: str
    valid_from: str
    valid_until: Optional[str]
    created_by: str                           # immer Mensch
    approved_by: str                          # immer Mensch
    version: str                              # semantisch
    created_at: str
    updated_at: str
```

**Regeln (SL-MAN-1..6):**
1. Nur der Mensch erstellt/ändert `hard_constraints`. Die LLM darf ausschließlich Entwürfe liefern. *(behebt PROB-01)*
2. Bei Bootstrap materialisiert der Kanzler jede `ManifestConstraint` gemäß SL-BOOT-3. *(behebt F-18, 6.1)*
3. Die FrontierEngine verwirft Kandidaten, die gegen materialisierte Constraints verstoßen (Hartfilter Nr. 10). *(behebt F-19)*
4. Der Quartiermeister schneidet `parameter_bounds` jedes Pakets mit den Manifest-Constraints (SL-MAN-4). *(behebt 6.1)*
5. **Manifest-Versionssprung:** Erkennt der Kanzler eine neue Version, re-validiert er alle Pakete in `pending/` (Delete-Request bei Verstoß), markiert Pakete in `processing/` im nächsten Briefing und erzeugt ein URGENT-Briefing. *(behebt F-25, PROB-23)*
6. **`valid_until`-Ablauf:** Der Strategiezyklus pausiert; nur Diagnostik ist erlaubt; HumanEscalationRecord(MANIFEST_EXPIRED) wird erzeugt. *(behebt F-26)*

### §6.2 StrategicBriefing und Teilstrukturen

```python
class BriefingType(str, Enum):
    BOOTSTRAP = "BOOTSTRAP"
    PERIODIC = "PERIODIC"
    URGENT = "URGENT"
    FINAL = "FINAL"

class AtlasMacroState(BaseModel):
    total_zones: int
    healthy_zones: int
    degraded_zones: int
    critical_zones: int
    locked_zones: int
    quarantined_zones: int
    unexplored_zones: int
    avg_fracture_score: Optional[float]
    avg_uncertainty_score: float
    total_crystals: int
    total_hypotheses: int
    total_digital_twins: int
    drifted_twins: int
    frontier_candidates_count: int
    vordenker_calibration_score: Optional[float]   # 0.0–1.0, aus §12.7

class BudgetState(BaseModel):
    total_budget_cycles: int
    used_cycles: int
    remaining_cycles: int
    reserved_cycles: int
    burn_rate_per_cycle: float
    estimated_completion_cycle: Optional[int]

class TopicSummary(BaseModel):                    # (behebt PROB-26)
    topic_id: str
    state: ResearchTopicState
    progress_percent: float          # deterministisch: Abstand bester
                                     # ObjectiveFamily-Wert zum Ziel, 0–100
    best_objective_distance: float   # skalare Zielerreichung, deterministisch
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

class HardwareHealth(BaseModel):                  # (behebt PROB-16/37)
    slot_outages: list[SlotOutage]   # Slot-ID, Zustand (ESTOP_SUSPENDED/
                                     # INTERLOCKED/MAINTENANCE/OFFLINE), seit
    questor_health_status: HealthStatus           # HEALTHY/DEGRADED/UNHEALTHY/DEAD
    operational_failure_count_recent: int         # verzerrt KEINE
                                                  # wissenschaftlichen Metriken

class DecisionOption(BaseModel):
    option_id: str
    description: str                 # template-basiert, max 512 Zeichen, Scan
    impact: str                      # template-basiert, max 512 Zeichen
    risk_level: RiskLevel
    requires_human_approval: bool

class RoyalLogAnchor(BaseModel):
    entry_ref: str
    origin: OriginType               # QUEEN | HUMAN
    intent: Optional[DirectiveIntent]  # None bei HUMAN_OVERRIDE-Freitextweisung
    summary: str                     # max 256 Zeichen
    outcome: Optional[DirectiveOutcome]
    age_cycles: int

class StrategicBriefing(BaseModel):
    briefing_id: str
    zyklus_id: str
    briefing_type: BriefingType
    manifest_version_ref: str
    atlas_macro_state: AtlasMacroState
    budget_state: BudgetState
    topics: list[TopicSummary] = []
    active_fractures: list[FractureSummary] = []
    twin_status: list[TwinStatusSummary] = []
    hardware_health: HardwareHealth
    decisions_required: list[DecisionOption] = []
    royal_log_anchor: list[RoyalLogAnchor] = []
    pending_escalations: list[str] = []          # IDs offener Eskalationen
    truncation_applied: bool = False
    generated_at: str
    generated_by: str                            # immer "KANZLER"
```

**Sanitization (SL-BRF-1..6):**
1. Verboten in jedem Briefing: `security_mode`, Atlas-Hybrid-Referenzfelder (`atlas_expectation_ref`, `frontier_candidate_ref`, `expectation_ref`, `evidence_kind/class` …), Roh-`metric_vector`. *(SR-24/29, QUESTOR §12.2a analog)*
2. Fortschritt wird als deterministisch berechnete **Skalare** (`progress_percent`, `best_objective_distance`) übergeben — nicht als Roh-Metriken.
3. Maximale Gesamtlänge: `max_briefing_chars`.
4. **Trunkierungsregel** (SL-BRF-4): Priorität = URGENT-Auslöser > LOCKED/CRITICAL-Zonen > höchste Fractures > aktive Topics > Rest. Jede Trunkierung wird mit `truncation_applied = true` deklariert. *(behebt PROB-29, F-24)*
5. **Quarantäne-Semantik** (SL-BRF-5): Quarantinierte Felder werden entfernt und durch `[REDACTED:QUARANTINE]` ersetzt; das Briefing bleibt gültig; der Vorfall erzeugt einen Audit-Eintrag. *(behebt PROB-20, 7.1)*
6. **URGENT-Kollisionen** (SL-BRF-6): Es existiert genau eine Briefing-Queue. Gleichzeitige URGENT-Auslöser werden zu **einem** Briefing mit priorisierten Abschnitten zusammengeführt. Pro Auslöser-Typ gilt ein Direktiven-Cooldown von `urgent_cooldown_cycles`. *(behebt PROB-31, F-28)*

### §6.3 StrategicDirective und Übersetzung

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
    DROP_SOFT_PREFERENCE = "DROP_SOFT_PREFERENCE"   # ersetzt DROP_CONSTRAINT
    HUMAN_ESCALATION = "HUMAN_ESCALATION"

class DirectiveStatus(str, Enum):
    PROPOSED = "PROPOSED"; ACCEPTED = "ACCEPTED"; VETOED = "VETOED"
    ESCALATED = "ESCALATED"; IMPLEMENTED = "IMPLEMENTED"; REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"; EXPIRED = "EXPIRED"

class StrategicDirective(BaseModel):
    directive_id: str            # deterministisch, SL-DIR-1
    briefing_ref: str            # Pflicht; Existenzprüfung SL-DIR-2
    intent: DirectiveIntent
    target_ref: Optional[str]    # SL-DIR-3
    parameters: dict[str, Any]   # Intent-spezifisch, §6.4
    reason: str                  # max 1024 Zeichen, Scan
    keep_constraints: list[str] = []
    drop_soft_preferences: list[str] = []   # nur soft_preferences!
    priority: float = 0.5
    valid_for_cycles: int = 10   # nur für andauernde Modifikatoren, SL-DIR-4
    created_at: str
```

**Regeln (SL-DIR-1..7):**
1. `directive_id = sha256(briefing_ref + intent + target_ref + canonical_json(parameters))`. Duplikate werden über das RoyalLog erkannt und nicht erneut ausgeführt. *(behebt F-30, PROB-32-teilweise)*
2. Nicht existierende `briefing_ref` → VETO. *(behebt PROB-40)*
3. `target_ref` darf nur leer sein bei `INITIAL_SWEEP`, `NO_ACTION`, `HUMAN_ESCALATION`, `ABORT_MISSION`. *(behebt F-04)*
4. Einmal-Intents (`PIVOT_*`, `ARCHIVE_TOPIC`, `CALIBRATE_TWIN`, `ADD_DIMENSION_HINT`, `UNLOCK_BUDGET`, `ABORT_MISSION`) werden bei ACCEPTED **sofort** ausgeführt; `valid_for_cycles` gilt nur für andauernde Modifikatoren (`SET_PRIORITY`, `INCREASE_DIAGNOSTIC`). EXPIRED ist damit widerspruchsfrei. *(behebt F-29)*
5. `DROP_SOFT_PREFERENCE` kann sprachlich und schema-seitig keine `hard_constraints` adressieren; Versuch → VETO(`MANIFEST_VIOLATION`). *(behebt 4.2, 6.1)*
6. Direktiven auf Topics/Zonen in `LOCKED`-Zustand → Schema-VETO mit Begründung. *(behebt F-32)*
7. `ADD_DIMENSION_HINT` erfordert `source_ref` (Hypothese **oder** Direktiven-Kontext); das Pflichtfeld `source_hypothesis_ref` des DimensionOnboardingRequest ist in diesem Pfad optional. *(behebt F-34)*

### §6.4 DirectiveTranslationTable (SL-DTT)

Deterministische Übersetzung; kein Interpretationsspielraum. *(behebt PROB-03, F-05, F-17)*

| Intent | Pflicht-Parameter | Deterministische Wirkung |
|---|---|---|
| NO_ACTION | — | keine Policy-Änderung; Zyklus protokolliert |
| INITIAL_SWEEP | `dimensions`, `levels` | `exploration_weight = 0.90`, Topic PROPOSED→ACTIVE, Seed-Symptom (SL-BOOT-6) |
| PIVOT_DOMAIN / PIVOT_TARGET | `from_topic_ref`, `to_topic_seed` | altes Topic → ARCHIVED **nach Lessons-Learned-Transfer** (SL-DTT-1); neues Topic PROPOSED |
| UNLOCK_BUDGET | `amount_cycles`, `purpose` | immer HumanEscalationRecord(BUDGET); bei Bestätigung: MissionBudget.reserved += amount |
| ABORT_MISSION | `reason` | immer ESCALATED; nur mit menschlicher Bestätigung umgesetzt |
| ADD_DIMENSION_HINT | `source_ref`, `dimension_seed` | erzeugt prüfpflichtigen DimensionOnboardingRequest |
| INCREASE_DIAGNOSTIC | `zone_ref`, `amount` | `diagnostic_budget` der Zone += amount (max. `diagnostic_budget_max`) |
| CALIBRATE_TWIN | `twin_ref` | VETO wenn Twin nicht gedriftet (NO_DRIFT); sonst `diagnostic_weight = 0.80` + Kalibrierungs-Topic-Commitment |
| ARCHIVE_TOPIC | `topic_ref` | Topic → ARCHIVED nach Lessons-Learned-Transfer |
| SET_PRIORITY | `topic_ref`, `priority` | Topic.priority setzen; `valid_for_cycles` möglich |
| DROP_SOFT_PREFERENCE | `preference_ref` | soft_preference deaktivieren (auditiert) |
| HUMAN_ESCALATION | `question` | HumanEscalationRecord(DEADLOCK) |

**SL-DTT-1 (Lessons-Learned-Transfer):** Vor Archivierung eines Topics übersetzt der Kanzler gescheiterte Regionen (Zonen mit `fracture_score ≥ degraded_threshold` oder ExclusionConstraints) in `ExclusionConstraint`-Vorschläge für das neue Topic. *(behebt 4.1)*

### §6.5 RoyalLog

```python
class DirectiveOutcome(str, Enum):
    IMPLEMENTED = "IMPLEMENTED"; VETOED = "VETOED"; SUPERSEDED = "SUPERSEDED"
    EXPIRED = "EXPIRED"; ESCALATED = "ESCALATED"; HUMAN_OVERRIDE = "HUMAN_OVERRIDE"

class OriginType(str, Enum):
    QUEEN = "QUEEN"; HUMAN = "HUMAN"

class RoyalLogEntry(BaseModel):
    entry_id: str
    origin: OriginType
    directive_ref: Optional[str]      # None bei freien menschlichen Weisungen
    briefing_ref: Optional[str]
    outcome: DirectiveOutcome
    outcome_reason: Optional[str]     # max 512 Zeichen
    policy_effect_ref: Optional[str]
    timestamp: str
```

**Regeln (SL-ROY-1..4):**
1. Das RoyalLog ist ein **operatives Governance-Journal** (SR-08) und wird ausschließlich vom Kanzler geschrieben. Speicherort: `data/archiv/operational/royal_log/`. *(behebt F-36-teilweise)*
2. Outcome-Semantik: `IMPLEMENTED` wird gesetzt, wenn die Policy-Übersetzung wirksam wurde; die tatsächliche Atlas-Wirkung wird als `policy_effect_ref` nachgeführt, sobald messbar. *(behebt F-09)*
3. Menschliche Weisungen werden als `origin = HUMAN`, `outcome = HUMAN_OVERRIDE` eingetragen und im Anchor vor allen Königin-Einträgen angezeigt (SL-ANCHOR-3). *(behebt PROB-22)*
4. Retention: Anker-relevante Einträge bleiben bis Missionsende; danach Cold Storage (§18.4). *(behebt PROB-30)*

### §6.6 SymptomEvent und ScientificHypothesis

```python
class SymptomType(str, Enum):
    INITIAL_SWEEP = "INITIAL_SWEEP"       # vom Kanzler bei Bootstrap
    WEISSRAUM = "WEISSRAUM"
    FRACTURE_GAP = "FRACTURE_GAP"
    SATURATION = "SATURATION"
    BRIDGE_OPP = "BRIDGE_OPP"
    TWIN_DRIFT = "TWIN_DRIFT"
    CAPABILITY_GAP_FEEDBACK = "CAPABILITY_GAP_FEEDBACK"
    DIMENSION_GAP = "DIMENSION_GAP"

class SymptomEvent(BaseModel):
    event_id: str
    symptom_type: SymptomType
    zone_ref: Optional[str]
    atlas_refs: list[str] = []            # deterministisch kuratiert
    metrics_snapshot: dict[str, float] = {}
    twin_divergence_report_ref: Optional[str] = None
    created_at: str

class CapabilityRequirement(BaseModel):   # (behebt 5.1)
    capability_id: str                    # muss in Registry existieren
    parameter_requirements: dict[str, Any] = {}   # z.B. {"min_temp_c": 250}

class ScientificHypothesis(BaseModel):
    hypothesis_id: str
    hypothesis_text: str                  # max 2048 Zeichen, Scan
    expected_outcome: str                 # max 1024 Zeichen
    source_trigger: SymptomType
    atlas_refs: list[str] = []            # leer nur bei INITIAL_SWEEP (SL-BOOT-6)
    zone_ref: Optional[str]
    required_capabilities: list[CapabilityRequirement]   # PFLICHT
    dimension_onboarding_request: Optional[DimensionOnboardingRequest] = None
    prozess_skizze: str                   # G-5, nur menschliche Dokumentation
    confidence_estimate: float            # 0.0–1.0, wird kalibriert (§12.7)
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    created_at: str
```

**Regeln (SL-HYP-1..3):**
1. `required_capabilities` ist maschinenlesbar und Pflicht; der Lotse prüft deterministisch gegen die Capability-Registry. Fehlt die Liste oder ist sie leer → Fail-Closed-Verwurf. *(behebt 5.1)*
2. `prozess_skizze` wird vom Lotsen **nicht** geparst; sie dient nur der menschlichen Nachvollziehbarkeit (G-5).
3. Persistierte Hypothesen werden beim Wiedereinspeisen in einen LLM-Prompt erneut gescannt (Second-Order-Scan, §17.2). *(behebt F-22)*

### §6.7 DimensionOnboardingRequest und DIMENSION_GAP

```python
class DimensionRequestStatus(str, Enum):
    PROPOSED = "PROPOSED"; APPROVED = "APPROVED"
    REJECTED = "REJECTED"; ESCALATED = "ESCALATED"; COOLDOWN = "COOLDOWN"

class DimensionOnboardingRequest(BaseModel):
    request_id: str
    proposed_dimension_id: str
    display_name: str
    domain: str
    value_type: DimensionValueType
    unit: Optional[str] = None
    rationale: str                        # max 2048 Zeichen, Scan
    source_ref: str                       # Hypothese oder Direktive (SL-DIR-7)
    source_trigger: SymptomType
    suggested_value_range: Optional[tuple[float, float]] = None
    suggested_categories: Optional[list[str]] = None
    requires_physical_actuation: bool = False
    status: DimensionRequestStatus = DimensionRequestStatus.PROPOSED
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    created_at: str
```

**Regeln (SL-DIM-1..8)** — vollständiger Lebenszyklus in §13.

### §6.8 CapabilityGapSignal

```python
class CapabilityGapSignal(BaseModel):
    signal_id: str
    waypoint_ref: Optional[str]
    hypothesis_ref: str
    missing_capability: str
    attempted_parameters: dict[str, Any] = {}
    suggested_alternatives: list[str] = []
    requires_budget_or_hardware: bool = False
    created_at: str
```

Speicherort: `data/archiv/operational/events/`. *(behebt F-11)*

### §6.9 MissionBudget und HumanEscalationRecord

```python
class MissionBudget(BaseModel):           # (behebt F-15, F-16)
    mission_id: str
    total_cycles: int
    used_cycles: int
    reserved_cycles: int = 0
    capex_requests: list[CapexRequest] = []
    updated_at: str

class CapexRequest(BaseModel):
    request_id: str
    description: str                      # max 512 Zeichen, Scan
    estimated_cost: str
    requires_human_approval: bool = True  # immer true
    status: DimensionRequestStatus        # wiederverwendeter Status-Enum

class EscalationType(str, Enum):
    BUDGET = "BUDGET"; DIMENSION_PHYSICAL = "DIMENSION_PHYSICAL"
    ABORT_CONFIRM = "ABORT_CONFIRM"; SAFETY_EVENT = "SAFETY_EVENT"
    DEADLOCK = "DEADLOCK"; CAPEX = "CAPEX"
    MANIFEST_EXPIRED = "MANIFEST_EXPIRED"; QUARANTINE_EXIT = "QUARANTINE_EXIT"

class EscalationStatus(str, Enum):
    PENDING = "PENDING"; ANSWERED = "ANSWERED"; TIMED_OUT = "TIMED_OUT"

class HumanEscalationRecord(BaseModel):   # (behebt PROB-17)
    escalation_id: str
    escalation_type: EscalationType
    payload_ref: str
    status: EscalationStatus = EscalationStatus.PENDING
    created_at: str
    timeout_cycles: int
    answered_by: Optional[str] = None
    answer_ref: Optional[str] = None      # Antwortdatei in data/human_inbox/
```

**Regeln (SL-ESC-1..4):**
1. Speicherort: `data/archiv/operational/escalations/`; menschliche Antworten als Dateien in `data/human_inbox/` (Blackboard-konform).
2. **Unbeantwortete Eskalation:** Nach `timeout_cycles` → Systemzustand `HOLD_STRATEGY`: ExplorationPolicy eingefroren, nur `DIAGNOSE`-Pakete erlaubt, keine neuen EXPLORE/OPTIMIZE-Frontiers; Erinnerungs-Eskalation alle `escalation_reminder_interval_cycles`. *(behebt PROB-19)*
3. `ABORT_MISSION` ohne menschliche Bestätigung wird niemals umgesetzt.
4. CAPEX-Anfragen sind immer `requires_human_approval = true` und werden nicht aus dem operativen Zyklus-Budget gedeckt. *(behebt 5.2)*

### §6.10 FinalScientificReport

```python
class ReportFacts(BaseModel):             # DETERMINISTISCH (Kanzler)
    mission_goal_ref: str
    final_objective_values: dict[str, float]   # Skalare, deterministisch
    top_crystal_summaries: list[CrystalSummary]  # strukturierte Skalare
    rejected_hypotheses_count: int
    twin_calibration_history: list[str] = []
    safety_warnings: list[str] = []
    diagnostic_resolution_summary: list[str] = []

class CrystalSummary(BaseModel):
    crystal_node_ref: str
    objective_values: dict[str, float]
    support_confidence: float
    fracture_score: Optional[float]

class FinalScientificReport(BaseModel):   # (behebt PROB-27, 8.1, 8.2)
    report_id: str
    topic_ref: str
    manifest_ref: str
    facts: ReportFacts                    # vom Kanzler injiziert
    executive_summary: str                # LLM, max 4096 Zeichen, Scan
    future_recommendations: str           # LLM, max 2048 Zeichen, Scan
    citation_refs: list[str] = []         # nur existierende Atlas/Archiv-IDs
    generated_at: str
    human_reviewed: bool = False
```

**Regeln (SL-RPT-1..4)** in §18.

### §6.11 StrategicLayerConfig

Vollständig in §23.

### §6.12 Neue Enums (Zusammenfassung)

`BriefingType`, `DirectiveIntent`, `DirectiveStatus`, `DirectiveOutcome`, `OriginType`, `SymptomType` (erweitert), `HypothesisStatus`, `DimensionRequestStatus`, `EscalationType`, `EscalationStatus`, `EnforcementType` (EXCLUSION/SAFETY/BOUNDS), `RiskLevel` (LOW/MEDIUM/HIGH), `FrontierType` **erweitert um `REPLICATE`**.

---

## §7 Direktiven-Lebenszyklus und Kanzler-Validierung

### §7.1 Validierungspipeline (feste Reihenfolge, SL-VAL-1..7)

```text
StrategicDirective (LLM-Output)
  │
  ├─ 1. Schema-Validierung (Pydantic, Enum, Längen, directive_id-Kanon)
  │      FAIL → VETO("SCHEMA_INVALID")
  ├─ 2. briefing_ref-Existenz (SL-DIR-2)         FAIL → VETO
  ├─ 3. Manifest-Prüfung:
  │      • Verstöße gegen hard_constraints?       → VETO("MANIFEST_VIOLATION")
  │      • drop_soft_preferences enthält hard?    → VETO("MANIFEST_VIOLATION")
  │      • target in LOCKED-Zone?                 → VETO("TARGET_LOCKED")
  ├─ 4. Safety-/Injection-Prüfung:
  │      • Safety-Claim in reason/parameters?     → VETO + Audit (SR-27)
  │      • ESTOP-/Reset-Begriffe in Parametern?   → VETO + Audit
  ├─ 5. Budget-Prüfung:
  │      • UNLOCK_BUDGET                          → immer ESCALATED
  │      • Budget unter 0 nach Simulation?        → VETO("BUDGET_NEGATIVE")
  ├─ 6. Intent-Sonderregeln (§6.3, §6.4):
  │      • CALIBRATE_TWIN ohne Drift              → VETO("NO_DRIFT")
  │      • ABORT_MISSION                          → ESCALATED
  ├─ 7. ACCEPT → DirectiveTranslationTable ausführen
```

### §7.2 Konfliktdetektor (SL-CON-1..2) *(behebt PROB-21)*

1. Jeder VETO gegen eine Königin-Direktive zählt als **Konflikt**. Injection-VETOs zählen zusätzlich als Sicherheits-Audit-Ereignis.
2. **2 Konflikte innerhalb von `conflict_window_cycles` (=10)** → menschlicher Fallback gemäß GREMIUM §1.2 Prinzip 2: URGENT-Briefing + HumanEscalationRecord(DEADLOCK); die Königin erzeugt bis zur menschlichen Antwort nur noch NO_ACTION.

### §7.3 NO_ACTION-Überwachung (SL-NOACT-1) *(behebt F-08)*

`no_action_stall_limit` aufeinanderfolgende NO_ACTION-Direktiven **ohne** Atlas-Fortschritt (keine neuen Kristalle, keine Fracture-Änderung) → URGENT-Briefing „Strategischer Stillstand" mit DecisionOptions.

---

## §8 Symptom-Trigger und Vordenker

### §8.1 Trigger-Tabelle (alle Schwellwerte in §23) *(behebt PROB-34, F-14)*

| Symptom | Deterministische Bedingung | Vordenker-Aktion |
|---|---|---|
| INITIAL_SWEEP | Bootstrap (SL-BOOT-6) | Seed-Modus, Sweep-Strategie |
| WEISSRAUM | Zone gemäß SL-DEF-2, aktive Frontier-Region | Void-Prompting: Screening-Strategie |
| FRACTURE_GAP | `fracture_score ≥ quarantine_threshold` | Fracture-Prompting: 1–3 erklärende Hypothesen, ggf. DimensionOnboardingRequest |
| SATURATION | Topic-StopCondition `SATURATION_CYCLES` erfüllt (**einzige Quelle**; das Symptom wird davon abgeleitet) | Paradigma-Wechsel: neue Dimension/Methode |
| BRIDGE_OPP | Cluster-übergreifende Kanten zwischen unterschiedlichen Domänen ≥ `bridge_edge_threshold` | Bridge-Prompting: interdisziplinäre Hypothese |
| TWIN_DRIFT | `TwinDivergenceReport.tolerance_breached = true` | Twin-Calibration-Prompting inkl. Schatten-Variablen-Check (§12.5) |
| CAPABILITY_GAP_FEEDBACK | CapabilityGapSignal eingegangen | Hypothese an verfügbare Capabilities anpassen |
| DIMENSION_GAP | Idee wegen `approved=false`-Dimension blockiert (§13.3) | alternative Hypothese ohne blockierte Dimension |

### §8.2 URGENT-Triggerliste des Kanzlers (SL-URG-1)

URGENT-Briefings werden erzeugt bei:
1. `fracture_score ≥ full_rebuild_threshold` in aktiver Zone
2. `TwinDivergenceReport.tolerance_breached = true`
3. Topic SATURATED ohne Zielerreichung bei Budget > `stagnation_budget_threshold`
4. LOCKED-Zone ohne genehmigte Diagnose-Strategie
5. 2. Konflikt (SL-CON-2)
6. CapabilityGapSignal mit `requires_budget_or_hardware = true` *(behebt F-12)*
7. **SAFETY-Ereignis (ESTOP/Interlock) — ereignisgesteuert, sofort** (§11)
8. Manifest-Versionssprung
9. NO_ACTION-Stall (SL-NOACT-1)
10. Quarantäne-Timeout (§13.7 / §7-Quarantäne)

### §8.3 Diagnose-Budget (SL-DIAG-1..2) *(behebt PROB-09)*

1. `diagnostic_budget` pro Zone wird erhöht durch: Topic-Neustart (+`diagnostic_budget_default`), URGENT-Fracture-Ereignis (+1), Direktive `INCREASE_DIAGNOSTIC` (begrenzt durch `diagnostic_budget_max`).
2. Ist das Budget erschöpft, erzeugt der Pre-Filter kein stilles Verwerfen, sondern eine DecisionOption im nächsten Briefing.

### §8.4 SymptomEvent-Verlustschutz (SL-SYM-1) *(behebt PROB-38)*

SymptomEvents werden **vor** der Queue-Übergabe persistent im operationalen Event-Log abgelegt. Bei High-Watermark der Vordenker-Queue wird das Event nicht verworfen, sondern zurückgestellt und im nächsten freien Slot erneut zugestellt (At-Least-Once mit Event-ID-Deduplizierung).

---

## §9 Signal-Semantik-Korrektur (Änderungsantrag an QUESTOR §10.5)

### §9.1 Der korrigierte Fallback *(behebt PROB-06 — kritischster Fund)*

**Alt:** `not ziel_erreicht` (ohne Erwartung) → 🟨 CONTRADICTION.
**Neu (SL-SIG-1):**

```text
WENN expectation_ref vorhanden:
    confirms_expectation == False → 🟨 CONTRADICTION (REFUTES)
    confirms_expectation == True  → 🟩 (≥0.8) bzw. ⬜ (<0.8)
    confirms_expectation == None  → ⬜ EXPLORATORY_COVERAGE
WENN keine Erwartung UND ziel_erreicht == True:
    konfidenz ≥ 0.8 → 🟩 CONFIRMATION
    konfidenz ≥ 0.5 → ⬜ EXPLORATORY_COVERAGE
WENN keine Erwartung UND ziel_erreicht == False:
    → ⬜ EXPLORATORY_COVERAGE mit evidence_kind = NEGATIVE_KNOWLEDGE
      (negatives Wissen: „Region X erreicht Ziel nicht"; fließt in
       coverage_energy, NICHT in conflict_energy)
```

**Begründung:** Ein verfehltes Ziel ohne Erwartung ist kein Widerspruch. 🟨 bleibt ausschließlich: (a) Erwartung widerlegt, (b) Replikat-Divergenz jenseits der Mess-Toleranz. Ohne diese Korrektur bestraft sich das System für normale Exploration durch Fracture-Inflation und Quarantäne-Kaskaden.

### §9.2 Weitere Semantik-Regeln

- **SL-SIG-2:** OPERATIONALE Paketfehler fließen niemals in wissenschaftliche Metriken (Sättigung, Fracture, Support). Sie erscheinen ausschließlich in `HardwareHealth.operational_failure_count_recent`. *(behebt F-31)*
- **SL-SIG-3:** Eine Sättigung hat genau eine Quelle: die Topic-StopCondition `SATURATION_CYCLES`. Alle davon abgeleiteten Mechanismen (SymptomEvent, URGENT-Briefing) referenzieren diesen Zustand. *(behebt F-14)*
- **SL-SIG-4:** ObjectiveFamily-Constraints (`MetricConstraint`) werden **binär gegatet**: Ein Ergebnis, das ein Constraint verletzt, kann niemals `ziel_erreicht = true` ergeben, unabhängig vom Weighted-Sum. *(behebt PROB-35)*

---

## §10 Manifest-Enforcement zur Laufzeit

*(behebt C3 insgesamt: F-18, F-19, F-25, F-26, 6.1, 6.2, PROB-23, PROB-35)*

### §10.1 Schutzkette

```text
ResearchManifest.hard_constraints (maschinenlesbar)
    │ SL-BOOT-3: Materialisierung
    ▼
ExclusionConstraint / SafetyConstraint im Atlas
    │
    ├─ FrontierEngine-Hartfilter Nr. 10: Kandidat außerhalb → verwerfen
    ├─ Pre-Filter: prüft aktive Constraints (bestehend)
    ├─ Quartiermeister SL-MAN-4: parameter_bounds ∩ Manifest-Constraints
    └─ PolicyEvaluator Prüfung 9 (NEU): Manifest-Constraint-Check
       gegen die finalen Paket-Parameter → VETO("MANIFEST_VIOLATION")
```

### §10.2 Semantische Umgehungsabwehr (SL-MAN-7) *(behebt 6.1)*

Die Königin kann Constraints nicht durch Umdeutung umgehen (z. B. „Argon-Atmosphäre als ambient"), weil:
1. Direktiven-Parameter gegen materialisierte Constraints geprüft werden (Schritt 3 der Validierung),
2. neue kategorische Werte, die nicht in `ManifestConstraint.categories` enthalten sind, als Constraint-Verstoß gelten,
3. die Definition von „Umgebung" ausschließlich aus dem Manifest kommt, nicht aus LLM-Interpretation.

---

## §11 Safety-Reaktionskette (SL-SAF-1..4)

*(behebt PROB-15, F-20, 5.3)*

```text
HAL meldet ESTOP / Hardware-Interlock (SAFETY)
    │  (bestehend: Questor SAFETY-Abbruch, Kristalle/Signale leer, SR-19)
    ▼
SL-SAF-1: Questor-Ergebnis enthält abbruch_klasse = SAFETY.
          Der Archivar protokolliert ein SAFETY-Governance-Ereignis
          (bestehend, GREMIUM §3.1).
    ▼
SL-SAF-2: Der Kanzler empfängt das Governance-Ereignis
          EREIGNISGESTEUERT (nicht erst im nächsten PERIODIC-Zyklus)
          und führt SOFORT aus:
          a) Zone der betroffenen Parameterregion → LOCKED
          b) SafetyConstraint-Vorschlag aus den Paket-Bounds erzeugen
             (source_event_ref = SAFETY-Ereignis)
          c) URGENT-Briefing an die Königin
          d) HumanEscalationRecord(SAFETY_EVENT)
    ▼
SL-SAF-3: Die betroffene Region bleibt für normale Exploration gesperrt,
          bis der autorisierte Sicherheitsprozess den SafetyConstraint
          aufhebt. Diagnostik in der Region ist erlaubt (DIAGNOSE +
          FRACTURE_DIAGNOSIS).
    ▼
SL-SAF-4: Zementierung SR-05: Das DirectiveIntent-Enum enthält keinen
          Reset-Intent; Direktiven-Parameter werden gegen ESTOP-/Reset-
          Begriffe geprüft (Validierung Schritt 4). Die Königin kann
          einen ESTOP-Reset weder benennen noch parametrisieren.
```

**Latenz:** Die Informationskette Königin erreicht das Ereignis sofort (ereignisgesteuert), nicht nach bis zu `briefing_interval_cycles`. *(behebt F-20)*

---

## §12 Digital-Twin-Loop (Härtung)

*(behebt PROB-08/13/14/39, 3.1/3.2/3.3, F-21)*

### §12.1 Paarung (SL-TWIN-1)

Der Kartograph führt einen **TwinPairingStore**: Sim- und Real-Kristalle werden max. `twin_pairing_ttl_cycles` gepuffert. Ungepaarte Kristalle werden nach TTL markiert (`unpaired = true`) und erzeugen keinen Report. Paarung erfordert identisches `objective_family_ref` und `digital_twin_ref` (DIGITAL-TWIN-SEM Regel 2).

### §12.2 Deviations-Berechnung (SL-TWIN-2) *(behebt PROB-39)*

```text
dev_metric = max(
    abs(sim − real) / max(abs(real), epsilon),
    abs(sim − real) / abs_tolerance_metric
)
abs_tolerance_metric = MetricDefinition.tolerance (falls gesetzt, sonst Default)
overall_divergence_score = mean(dev_metric) über alle gemeinsamen Metriken
```

Near-zero-Nenner erzeugen damit keine Fehlalarme mehr.

### §12.3 Twin-Validitätsprüfung (SL-TWIN-3) *(behebt PROB-14)*

- **PolicyEvaluator Prüfung 10 (NEU):** `digital_twin_ref` gesetzt UND `drift_score > divergence_threshold` UND `objective_type ≠ DIAGNOSE` → VETO(`TWIN_DEGRADED`).
- Der Quartiermeister prüft zusätzlich beim Paketbau.
- Ein gedrifteter Twin darf ausschließlich für Kalibrierungs-Diagnostik verwendet werden (DIGITAL-TWIN-SEM Regel 4).

### §12.4 Gate × Security-Mode-Matrix (SL-TWIN-4) *(behebt PROB-13, 3.3)*

| Paket-Zweck | gate_mode | security_mode |
|---|---|---|
| Normale Exploration/Optimierung | NORMAL | NORMAL |
| Fracture-Diagnose (physisch) | FRACTURE_DIAGNOSIS | NORMAL |
| **Twin-Kalibrierung** | FRACTURE_DIAGNOSIS | **SANDBOX oder DEV_SANDBOX_ONLY (erzwungen)** |
| Reine Simulation | SANDBOX | SANDBOX / DEV_SANDBOX_ONLY |
| Hochrisiko-Override | HIGH_RISK_OVERRIDE | NORMAL + menschliche Bestätigung |

Ein physisches Kalibrierungs-Paket ist damit konstruktionsunmöglich: Der Quartiermeister erzwingt den Security-Mode, Richter und Min-Rule bestätigen.

### §12.5 Schatten-Variablen-Check (SL-TWIN-5) *(behebt 3.1)*

Bei `TWIN_DRIFT` enthält der Vordenker-Prompt zwingend die **Umgebungs-Dimensionen** (Labor-Sensorik als TypedDimensions: Temperatur, Luftfeuchtigkeit etc.) mit der Instruktion: „Prüfe zuerst fehlende Kontext-Variablen, bevor Modellparameter kalibriert werden." Die Labor-Sensorik-Dimensionen sind Teil von `manifest.initial_dimensions` (SL-BOOT-2).

### §12.6 Deduplizierung und Deadlock-Freiheit (SL-TWIN-6..7) *(behebt F-21, 3.2)*

1. Kalibrierungs-Frontiers der FrontierEngine und TWIN_DRIFT-Hypothesen des Vordenkers werden über einen `blocked_cache`-Eintrag `(twin_ref, zyklus_id)` dedupliziert.
2. Ein Zone-LOCK wegen Twin-Drift sperrt nur physische NORMAL-Exploration; SANDBOX-Kalibrierung bleibt ausdrücklich erlaubt → kein Kalibrierungs-Deadlock.

### §12.7 Konfidenz-Kalibrierung des Vordenkers (SL-TWIN-8) *(behebt PROB-33)*

Der Kartograph führt je Hypothese den Vergleich `confidence_estimate` vs. tatsächliches Ergebnis (bestätigt/widerlegt nach Ausführung) als rollierenden `vordenker_calibration_score`, sichtbar im Briefing. Bei systematischer Fehleinschätzung (< `calibration_alert_threshold`) erscheint eine DecisionOption; eine automatische Maßnahme erfolgt nicht (LLM bleibt Advisor).

---

## §13 Dimensions-Lebenszyklus

*(behebt PROB-11/12, 2.1/2.2/2.3, F-10, F-34)*

### §13.1 Antrag

Der Vordenker hängt einen `DimensionOnboardingRequest` an eine `ScientificHypothesis` (oder die Königin gibt einen `ADD_DIMENSION_HINT`, SL-DIR-7).

### §13.2 Kanzler-Prüfung (SL-DIM-1..4)

1. **Plausibilität:** physikalisch sinnvoll, messbar (Capability-Abgleich), safety-konform.
2. **Range-Validierung:** `suggested_value_range` wird gegen Capability-Schemas und Domänen-Grenzen geprüft; bei Abweichung erzeugt der Kanzler einen korrigierten Vorschlag mit Audit-Eintrag (keine blinde Übernahme). *(behebt 2.2)*
3. **Cooldown:** mehr als `max_dimension_requests_per_topic_per_cycle` Anfragen pro Topic und Zyklus → Status `COOLDOWN` (archiviert für Audit). *(behebt 2.3)*
4. **Physische Auswirkung:** `requires_physical_actuation = true` → zwingend `ESCALATED` an den Menschen (HumanEscalationRecord(DIMENSION_PHYSICAL)). *(behebt F-10)*

### §13.3 Deadlock-Freiheit (SL-DIM-5) *(behebt PROB-12)*

Ideen, die eine `approved = false`-Dimension verwenden, werden vom Pre-Filter **nicht still verworfen**: Er emittiert `SymptomEvent(DIMENSION_GAP)` an den Vordenker und eine `DecisionOption` ins nächste Briefing („Dimension X blockiert N Ideen — freigeben oder Forschungsrichtung verwerfen").

### §13.4 Genehmigung und Backfill (SL-DIM-6..7) *(behebt 2.1)*

1. Genehmigung erzeugt eine `TypedDimension` mit `approved = false` (physische Nutzung erfordert weiterhin die bestehende `dimension_expansion_approval`; die menschliche Genehmigung des Requests gilt als diese Approval für davon abgeleitete Diagnose-Pakete).
2. Für bestehende Kristalle mit NULL-Werten auf der neuen Dimension erzeugt die FrontierEngine optional `BACKFILL_FRONTIER`-Kandidaten (DIAGNOSE auf Bestandkristalle) mit eigenem Budget.

### §13.5 Abgeleitete Dimensionen (SL-DIM-8) *(behebt PROB-11)*

Dimensionen, die Eigenschaften bestehender kategorischer Dimensionen abbilden (z. B. Siedepunkt eines Lösungsmittels), werden als `parent_dimension`-Referenz angelegt und über `ConditionalRule` in die `ZoneGeometry` integriert.

---

## §14 Capability-Gap-Behandlung

*(behebt PROB-18, 5.1/5.2, F-11/F-12, 1.3)*

```text
VORDENKER: ScientificHypothesis mit required_capabilities (Pflicht)
    ▼
LOTSE prüft deterministisch gegen Capability-Registry (3 Ebenen analog Q2)
    ├─ erfüllt → Wegmarke
    └─ unerfüllbar → CapabilityGapSignal
           │
           ├─ blocked_cache-Eintrag CAPABILITY_GAP für die Idee
           │  (Vordenker erhält CAPABILITY_GAP_FEEDBACK-Symptom)
           ├─ nach capability_gap_repeat_limit Wiederholungen:
           │  DecisionOption an Königin
           │  (bei requires_budget_or_hardware = true → CAPEX-Eskalation,
           │   immer requires_human_approval = true)
           └─ Speicherort: data/archiv/operational/events/ (SL-ACC-1-konform)
```

---

## §15 Mensch-Schnittstelle

*(behebt PROB-17/19/22/28, F-15/F-16, 8.3, 5.2)*

### §15.1 Eskalationskanal

Vertrag und Regeln: §6.9 (SL-ESC-1..4). Der Kanal ist dateibasiert und Blackboard-konform; die Königin erhält offene Eskalationen als `pending_escalations` im Briefing, kann sie aber nicht selbst beantworten.

### §15.2 Zustandsmaschine der menschlichen Interaktion

```text
ESCALATION_ERZEUGT (PENDING)
    ├─ Mensch antwortet → ANSWERED → Umsetzung durch Kanzler → RoyalLog
    ├─ timeout_cycles erreicht → TIMED_OUT → HOLD_STRATEGY
    │       └─ Erinnerung alle escalation_reminder_interval_cycles
    └─ Mensch ignoriert dauerhaft → HOLD_STRATEGY bleibt
        (nur Diagnostik; kein unbeobachteter Weiterlauf)
```

### §15.3 SAFE_MODE (SL-SAFE-1) *(behebt F-27)*

Bei aktivem SAFE_MODE: keine PERIODIC-Briefings, keine neuen Direktiven; URGENT ausschließlich für Safety-Ereignisse; RoyalLog-Eintrag `SAFE_MODE_ACTIVE`; bei Beendigung: neues Briefing mit vollständigem Anchor.

---

## §16 Briefing-Erzeugung (Zusammenführung)

```text
ATLAS (Blackboard)                        KANZLER
  │ AtlasZoneSummary-Metriken               │ 1. Aggregieren → AtlasMacroState
  ├────────────────────────────────────────►│ 2. MissionBudget → BudgetState
  │ FrontierCandidates / Topics             │ 3. Topics → TopicSummary[] (Skalare)
  ├────────────────────────────────────────►│ 4. Fractures filtern → FractureSummary[]
  │ TwinDivergenceReports / Twin-Knoten     │ 5. Twin-Status → TwinStatusSummary[]
  ├────────────────────────────────────────►│ 6. HAL-Slot-Zustände + Questor-Health
  │ Slot-Zustände (operational)             │    → HardwareHealth (ohne security_mode)
  ├────────────────────────────────────────►│ 7. Handlungsoptionen → DecisionOption[]
  │ RoyalLog                                │ 8. Anchor: HUMAN_OVERRIDE zuerst,
  ├────────────────────────────────────────►│    dann letzte N Direktiven
  │                                         │ 9. Sanitization (SL-BRF-1..6)
  │                                         │10. Trunkierung nach SL-BRF-4
  └─────────────────────────────────────────► StrategicBriefing schreiben
```

---

## §17 Sanitization-Erweiterung

*(behebt PROB-01/20, 7.1/7.2/7.3, F-22, F-23)*

### §17.1 Archivar-Eingangssanitization (SL-SAN-1)

Alle Freitextfelder eingehender `questor_ergebnis_paket`-Inhalte werden **vor** Atlas-/Archiv-Schreibung gescannt und geescaped (Injection-Patterns INJ-01..15, XML-Escaping, Längenlimits — QUESTOR §12.3 analog auf Schicht 4). Quarantinierte Inhalte werden protokolliert, nie injiziert. Damit ist Atlas-Vergiftung über Sensor-/Ergebnisdaten blockiert.

### §17.2 Second-Order-Scan (SL-SAN-2)

Jeder persistierte LLM-erzeugte Text (Hypothesen, Rationales, Direktiven-Reasons, Manifest-Entwürfe) wird beim Wiedereinspeisen in einen LLM-Prompt erneut gescannt.

### §17.3 Direktiven- und Report-Validierung (SL-SAN-3..4)

1. Direktiven durchlaufen die Safety-Claim-Erkennung (SR-27) in Validierungsschritt 4.
2. `FinalScientificReport`-Freitextfelder durchlaufen die Sanitization-Pipeline plus **Zitierungs-Check** (§18.2).

---

## §18 Abschluss und Archivierung

*(behebt PROB-27, PROB-28, 8.1/8.2/8.3)*

### §18.1 Ablauf

```text
StopCondition REACHED → Topic SATURATED → Kanzler erzeugt FINAL-Briefing
    ▼
Kanzler injiziert ReportFacts (deterministisch aus Atlas)
    ▼
Königin-LLM füllt NUR: executive_summary + future_recommendations
    ▼
Kanzler validiert: Sanitization + Zitierungs-Check + keine Safety-Claims
    ▼
HumanEscalationRecord(Review) → human_reviewed = true
    ▼
Topic → ARCHIVED; System wartet auf neue Mission
```

### §18.2 Zitierungs-Check (SL-RPT-1)

Jede Referenz in `citation_refs` muss eine existierende Atlas- oder Archiv-ID sein. Externe Zitiermuster („Smith et al.") sind unzulässig und werden entfernt. *(behebt 8.1)*

### §18.3 Fakten-Trennung (SL-RPT-2)

Harte Fakten (Zielwerte, Kristall-Zusammenfassungen, Twin-Historie, SafetyWarnings) stammen ausschließlich aus `ReportFacts` (deterministisch). Der Sanitization-Widerspruch aus PROB-27 ist aufgelöst: Die Königin benötigt keinen Roh-`metric_vector`, da der Kanzler strukturierte Skalare injiziert.

### §18.4 Review und Cold Storage (SL-RPT-3..4)

1. Unreviewed-Reminder alle `review_reminder_interval_cycles`. *(behebt PROB-28)*
2. Nach `cold_storage_window_days` mit `human_reviewed = true`: Atlas-Snapshot in Cold Storage; Ressourcen freigegeben; neue Missionen werden nicht blockiert. *(behebt 8.3)*

---

## §19 Replikations-Strategie

*(behebt PROB-36)*

**SL-REP-1:** `FrontierType` wird um `REPLICATE` erweitert.
**SL-REP-2:** Der Kartograph erzeugt REPLICATE-Frontiers, wenn `crystallization_progress ≥ replication_trigger_progress` (0.8) und die Anzahl relevanter Bestätigungen < `min_confirmations`.
**SL-REP-3:** Die FrontierEngine gewichtet REPLICATE-Kandidaten mit `replication_weight` (§23). Kristallisation hängt damit nicht mehr vom Zufall ab.

---

## §20 Datenintegrität und Speicherorte

*(behebt PROB-07/25/30/40, F-30, F-36)*

### §20.1 NaN/Infinity in der Wissenspipeline (SL-INT-1)

Kristallkandidaten mit ungültigem `metric_vector` (NaN/Infinity) werden vom Archivar **verworfen** und als operatives Ereignis protokolliert (Fail-Closed). Sie gelangen niemals in den Atlas. *(SR-14 auf Schicht 4 erweitert)*

### §20.2 Sequenzlücken (SL-INT-2)

Der Receiver akzeptiert Ergebnisse mit Sequenzlücke und setzt ein Audit-Flag (Totalfunktion vor Strenge, SR-20). Ein Reconciliation-Auftrag wird erzeugt. Kein stilles Verwerfen.

### §20.3 Referentielle Integrität (SL-INT-3)

- `briefing_ref` einer Direktive muss existieren (SL-DIR-2).
- `source_ref` eines DimensionOnboardingRequest muss existieren.
- `twin_divergence_report_ref` einer DiagnosticResolution muss existieren.

### §20.4 Idempotenz (SL-INT-4)

`directive_id`-Bildung gemäß SL-DIR-1; Duplikate werden über das RoyalLog erkannt.

### §20.5 Speicherorte (Blackboard-konform)

| Artefakt | Ort |
|---|---|
| ResearchManifest | `data/governance/manifests/` |
| StrategicBriefing | `data/governance/briefings/` |
| StrategicDirective | `data/governance/directives/` |
| MissionBudget | `data/governance/budget/` |
| DimensionOnboardingRequest | `data/governance/dimension_requests/` |
| RoyalLog | `data/archiv/operational/royal_log/` |
| SymptomEvent, CapabilityGapSignal | `data/archiv/operational/events/` |
| ScientificHypothesis | `data/archiv/ideen/` |
| HumanEscalationRecord | `data/archiv/operational/escalations/` |
| Menschliche Antworten | `data/human_inbox/` |

Alle Verzeichnisse sind dateibasiert; Schreibzugriffe sind atomar (SR-55); kein Rang schreibt außerhalb seiner Rolle.

---

## §21 Zustandsmaschinen

### §21.1 Strategischer Zyklus

```text
ZYKLUS_START
  → BRIEFING_ERZEUGT (PERIODIC/URGENT/BOOTSTRAP/FINAL)
  → DIREKTIVE_ANGEFORDERT (LLM-Aufruf, 3 Kontextblöcke)
       ├─ LLM-Fehler → Fallback (SL-ANCHOR-4) → nächster Zyklus
       ▼
  → DIREKTIVE_PROPOSED → VALIDIERUNG (§7.1)
       ├─ VETO → RoyalLog(VETOED) → Konfliktdetektor → nächster Zyklus
       ├─ ESCALATED → HumanEscalationRecord → (HOLD_STRATEGY bei Timeout)
       └─ ACCEPTED → DirectiveTranslationTable → IMPLEMENTED
  → POLICY_WIRKSAM → Pipeline läuft → nächster Zyklus
```

### §21.2 Direktiven-Status

```text
PROPOSED → ACCEPTED | VETOED | ESCALATED
ACCEPTED → IMPLEMENTED (Einmal-Intents sofort, Modifikatoren nach Übersetzung)
IMPLEMENTED → SUPERSEDED (neuere Direktive) | EXPIRED (nur Modifikatoren)
ESCALATED → IMPLEMENTED (Mensch bestätigt) | REJECTED (Mensch lehnt ab)
```

### §21.3 DimensionOnboardingRequest

```text
PROPOSED → APPROVED | REJECTED | ESCALATED | COOLDOWN
ESCALATED → APPROVED (Mensch) | REJECTED (Mensch)
APPROVED → TypedDimension(approved=false) erzeugt
physische Nutzung → dimension_expansion_approval erforderlich
```

### §21.4 Eskalation

```text
PENDING → ANSWERED | TIMED_OUT
TIMED_OUT → HOLD_STRATEGY (+ periodische Erinnerungen)
ANSWERED → Umsetzung → RoyalLog
```

### §21.5 SAFE_MODE / HOLD_STRATEGY

```text
NORMALBETRIEB → SAFE_MODE (nur Mensch): Briefings/Direktiven pausiert
NORMALBETRIEB → HOLD_STRATEGY (Eskalation-Timeout): nur DIAGNOSE erlaubt
SAFE_MODE/HOLD_STRATEGY → NORMALBETRIEB (Mensch): frisches Briefing + Anchor
```

---

## §22 Autonomie- und Eskalationsmatrix

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

---

## §23 Konfiguration: StrategicLayerConfig

```python
class StrategicLayerConfig(BaseModel):
    # Zyklen und Briefings
    briefing_interval_cycles: int = 25
    max_briefing_chars: int = 8192
    urgent_cooldown_cycles: int = 3
    # Anchor
    royal_log_anchor_depth: int = 3
    # Direktiven
    directive_ttl_cycles_default: int = 10
    conflict_window_cycles: int = 10
    no_action_stall_limit: int = 4
    max_consecutive_llm_failures: int = 3
    # Trigger-Schwellwerte (SL-DEF + §8.1)
    weissraum_min_coverage: float = 0.0
    bridge_edge_threshold: int = 2
    saturation_source: str = "TOPIC_STOP_CONDITION"   # einzige Quelle
    # Budget
    budget_unlock_threshold_fraction: float = 0.10
    stagnation_budget_threshold: float = 0.80
    # Dimensionen
    max_dimension_requests_per_topic_per_cycle: int = 2
    # Diagnose
    diagnostic_budget_default: int = 3          # konsistent mit AtlasHybridConfig
    diagnostic_budget_max: int = 12
    # Quarantäne
    quarantine_max_cycles: int = 30             # danach QUARANTINE_EXIT-Eskalation
    # Replikation
    replication_trigger_progress: float = 0.8
    replication_weight: float = 0.10
    # Twin
    twin_pairing_ttl_cycles: int = 10
    calibration_alert_threshold: float = 0.5    # vordenker_calibration_score
    # Eskalation und Abschluss
    escalation_timeout_cycles: int = 50
    escalation_reminder_interval_cycles: int = 10
    review_reminder_interval_cycles: int = 20
    cold_storage_window_days: int = 30
```

---

## §24 Datenflüsse in Einzelschritten (aktualisierte Diagramme)

### Schritt A — Missionsstart (mit Bootstrap)

```text
MENSCH              KANZLER                          KÖNIGIN
  │                    │                                │
  │ Ziel + Constraints │                                │
  ├───────────────────►│ SL-BOOT-1..4:                  │
  │                    │ Manifest, Dimensions,          │
  │                    │ Constraints materialisiert,    │
  │                    │ BOOTSTRAP-Briefing             │
  │                    ├───────────────────────────────►│
  │                    │                                │ INITIAL_SWEEP
  │                    │◄───────────────────────────────┤
  │                    │ Validierung → Topic ACTIVE      │
  │                    │ SL-BOOT-6: INITIAL_SWEEP-Symptom│
  │                    │ RoyalLogEntry(IMPLEMENTED)      │
```

### Schritt B — Direktiven-Validierung

```text
StrategicDirective
  → Schema → briefing_ref → Manifest → Safety/Injection → Budget
  → Intent-Sonderregeln → ACCEPT/VETO/ESCALATED
  → DirectiveTranslationTable → ExplorationPolicy/Topics
  → RoyalLog → Konfliktdetektor
```

### Schritt C — Symptom → Hypothese → Wegmarke (mit Capability-Gap)

```text
KARTOGRAPH          VORDENKER (LLM)          PRE-FILTER        LOTSE
    │ SymptomEvent       │                      │                │
    ├───────────────────►│ Topology-Prompting   │                │
    │                    │ ScientificHypothesis │                │
    │                    │ + required_capabilities               │
    │                    ├─────────────────────►│ Dimensionen,   │
    │                    │                      │ Quarantäne,    │
    │                    │                      │ Safety,        │
    │                    │                      │ approved-Dims  │
    │                    │                      │ (sonst         │
    │                    │                      │  DIMENSION_GAP)│
    │                    │                      ├───────────────►│
    │                    │                      │                │ Capability-
    │                    │                      │                │ Check
    │                    │                      │                ├─ erfüllt:
    │                    │                      │                │  Wegmarke
    │                    │                      │                ├─ Lücke:
    │                    │                      │                │  CapabilityGapSignal
    │                    │◄──────────────────────────────────────┤  (Feedback)
```

### Schritt D — DimensionOnboarding

```text
VORDENKER        KANZLER                    MENSCH (falls physisch)     ATLAS
    │ Request        │ Plausibilität, Range,         │                     │
    ├───────────────►│ Cooldown prüfen               │                     │
    │                ├─ physisch → ESCALATED         │                     │
    │                ├──────────────────────────────►│ genehmigen          │
    │                │◄──────────────────────────────┤                     │
    │                ├─ APPROVED → TypedDimension    │                     │
    │                │  (approved=false)             ├────────────────────►│
    │                │ optional: BACKFILL_FRONTIER   │                     │
    │                │ RoyalLog + Audit              │                     │
```

### Schritt E — Twin-Divergenz und Kalibrierung (gehärtet)

```text
QUESTOR      ARCHIVAR     KARTOGRAPH               KANZLER        KÖNIGIN
   │            │             │ TwinPairingStore        │             │
   │ Sim (SBX)  ├────────────►│ Paarung (TTL)           │             │
   │ Real       ├────────────►│ Deviation (SL-TWIN-2)   │             │
   │            │             │ tolerance_breached?     │             │
   │            │             ├────────────────────────►│ URGENT      │
   │            │             │                         ├────────────►│
   │            │             │                         │             │ CALIBRATE_TWIN
   │            │             │                         │◄────────────┤
   │            │             │                         │ NO_DRIFT-Check
   │            │             │                         │ diagnostic_weight↑
   │            │             │                         ▼             │
   │            │             │   Vordenker: Schatten-Variablen-Check │
   │            │             │   zuerst (SL-TWIN-5), dann Kalibrier- │
   │            │             │   hypothesen; Dedup via blocked_cache │
   │            │             │   → DIAGNOSE-Paket, security_mode =   │
   │            │             │     SANDBOX (erzwungen, SL-TWIN-4)    │
   │◄────────────────────────────────────── Dispatch ──┘               │
   │ Kalibrierungs-Kristall (COMPUTE_EVALUATION)                      │
   ├───────────────────────────►│ Twin-Knoten: model_version↑,         │
   │                            │ drift_score↓, TWIN_CALIBRATED        │
```

### Schritt F — ESTOP und Safety-Reaktion

```text
HAL: ESTOP/Interlock (SAFETY)
  → Questor: SAFETY-Abbruch, Kristalle/Signale leer (SR-19)
  → Archivar: SAFETY-Governance-Ereignis
  → KANZLER (ereignisgesteuert, SOFORT):
      Zone → LOCKED · SafetyConstraint-Vorschlag
      URGENT-Briefing · HumanEscalationRecord(SAFETY_EVENT)
  → Region gesperrt bis autorisierter Sicherheitsprozess
```

### Schritt G — Abschluss

```text
StopCondition REACHED → FINAL-Briefing
  → Kanzler injiziert ReportFacts (deterministisch)
  → Königin-LLM: NUR executive_summary + future_recommendations
  → Kanzler: Sanitization + Zitierungs-Check
  → Mensch: human_reviewed = true → ARCHIVED → Cold Storage
```

---

## §25 Änderungsliste an bestehenden Dokumenten

| Dokument | Änderung |
|---|---|
| **CONTRACTS.md** | Neuer §6.11 mit allen Verträgen aus §6; neue Enums (§6.12); `FrontierType` + `REPLICATE`; QUESTOR §10.5-Fallback gemäß §9.1 (Signal-Semantik-Korrektur) |
| **GREMIUM.md** | Neue Kanzler-Pflichten (Briefing-Generator, Directive-Validator mit 7 Stufen, DirectiveTranslationTable, RoyalLog, Eskalations-Manager, SAFETY-RESPONSE); Vordenker-Pflichten (Symptom-Trigger, Seed-Modus); Kartograph (SymptomEvents, TwinPairingStore, REPLICATE-Frontiers, Kalibrierungs-Tracking); Archivar (Eingangssanitization); Lotse (CapabilityGapSignal); Zugriffsmatrix §6.12 präzisiert (Königin: nur Briefings); PolicyEvaluator-Prüfungen 9+10 |
| **KOENIGIN.md (neu)** | Constitutional Stateless Anchor Pattern, Anchor-Regeln, Fallback-Regeln |
| **QUESTOR.md** | §10.5 Fallback-Korrektur (§9.1); sonst keine Änderungen |
| **HAL.md** | Keine Änderungen (Kompatibilitätsbestätigung) |
| **ROADMAP.md** | Neue Phasen S1–S4 + S-INT (§28.3) |
| **VALIDATION.md** | Neue Suite STRAT (§28) |
| **CHARTER.md** | Keine Regeländerung; optionaler redaktioneller Hinweis, dass Schicht 5 als Constitutional Stateless Pattern spezifiziert ist |

---

## §26 CHARTER-Konformitätsmatrix

| CHARTER-Regel | Umsetzung |
|---|---|
| SR-04 | Questor/HAL unverändert; strategische Verträge wirken nur auf Gremium-Ebene |
| SR-08 | RoyalLog, Briefings, Direktiven sind operational; HardwareHealth verzerrt keine wissenschaftlichen Metriken (SL-SIG-2) |
| SR-10 | Ungültige Direktive → VETO; unklarer DimensionRequest → REJECTED; LLM-Ausfall → Policy bleibt; NaN → Verwurf |
| SR-11 | Mensch wird nie überstimmt; ABORT, physische Dimensionen, CAPEX, Manifest immer menschlich; HUMAN_OVERRIDE im Anchor |
| SR-13 | Königin/Vordenker schlagen vor; Kanzler, Pre-Filter, Gate entscheiden deterministisch |
| SR-14 | NaN-Fail-Closed auf Schicht 4 erweitert (SL-INT-1) |
| SR-24 | Briefing-Whitelist (§6.2 SL-BRF-1); Fortschritt als Skalare |
| SR-29 | `security_mode` in keinem strategischen Artefakt |
| SR-05 | ESTOP-Reset im Intent-Enum nicht ausdrückbar (SL-SAF-4) |
| §2 Blackboard | Alle Kommunikation über definierte Speicherorte (§20.5); keine direkten Rang-Aufrufe |
| §8 Hierarchie | Dieses Dokument widerspricht CHARTER/CONTRACTS nicht; Änderungen als Änderungsanträge |

---

## §27 Verbotene Patterns (Strategic Layer)

1. Königin-LLM mit persistentem Gesprächsverlauf.
2. Freitext-Report als primärer LLM-Input (nur strukturierte Briefings).
3. LLM-Einsatz im Kanzler (auch keine LLM-Zusammenfassungen).
4. Direkter Atlas-/Archiv-Zugriff der Königin.
5. Direkte Kommunikation Königin ↔ Vordenker.
6. Automatische Dimensions-Erzeugung ohne Kanzler-Prüfung.
7. `security_mode` oder Atlas-Hybrid-Referenzen im LLM-Kontext.
8. RoyalLog-Inhalte als wissenschaftliche Signale.
9. Sim-Evidenz, die physische Kristalle direkt bestätigt (DIGITAL-TWIN-SEM Regel 1).
10. Physische Kalibrierungs-Pakete (SL-TWIN-4).
11. Explorations-Fehlschläge als 🟨 CONTRADICTION (SL-SIG-1).
12. Weiterlauf mit offener Eskalation nach Timeout (HOLD_STRATEGY stattdessen).
13. CHARTER-Änderung als Voraussetzung dieses Änderungsantrags.

---

## §28 Akzeptanzkriterien und Tests (Suite STRAT)

### §28.1 Pflichttests (Auszug, insgesamt ≥ 60)

| ID | Test | Erwartung |
|---|---|---|
| STRAT-01 | Direktive außerhalb Intent-Enum | Schema-VETO |
| STRAT-02 | `drop_soft_preferences` auf hard_constraint | VETO MANIFEST_VIOLATION |
| STRAT-03 | `security_mode` in Briefing-Template | blockiert, Audit |
| STRAT-04 | LLM-Timeout ×3 | Fallback, dann Eskalation |
| STRAT-05 | 2 VETOs in 10 Zyklen | URGENT + menschlicher Fallback |
| STRAT-06 | ABORT_MISSION | immer ESCALATED |
| STRAT-07 | DimensionRequest physisch | immer ESCALATED |
| STRAT-08 | TWIN_DRIFT → CALIBRATE_TWIN | SANDBOX erzwungen |
| STRAT-09 | CALIBRATE_TWIN ohne Drift | VETO NO_DRIFT |
| STRAT-10 | Explorations-Fehlschlag ohne Erwartung | ⬜ NEGATIVE_KNOWLEDGE, kein conflict_energy |
| STRAT-11 | ESTOP | SOFORTIGES URGENT + LOCKED + SafetyConstraint-Vorschlag |
| STRAT-12 | Manifest v2 mid-mission | pending-Pakete re-validiert, Delete-Requests |
| STRAT-13 | Injektion in Ergebnis-Freitext | Archivar-Quarantäne vor Atlas |
| STRAT-14 | Second-Order-Injection über gespeicherte Hypothese | Re-Scan greift |
| STRAT-15 | Unbeantwortete Eskalation | HOLD_STRATEGY nach Timeout |
| STRAT-16 | Human Override | Anchor-Priorität, keine Override-Schleife |
| STRAT-17 | Constraint-Verletzung bei WEIGHTED_SUM | `ziel_erreicht` kann nicht true sein |
| STRAT-18 | Kaltstart (leerer Atlas) | Bootstrap → erste Pakete ohne manuellen Anstoß |
| STRAT-19 | Briefing > max_chars | deterministische Trunkierung, deklariert |
| STRAT-20 | Capability-Gap ×N | blocked_cache, dann CAPEX-Eskalation |
| STRAT-21 | Quarantäne > quarantine_max_cycles | QUARANTINE_EXIT-Eskalation |
| STRAT-22 | Replikat-Bedarf | REPLICATE-Frontier bei progress ≥ 0.8 |
| STRAT-23 | FinalReport | Fakten deterministisch, Zitierungs-Check, kein Roh-metric_vector |
| STRAT-24 | Sequenzlücke | akzeptiert + Audit-Flag, kein Verlust |
| STRAT-25 | NaN in metric_vector | Archivar verwirft, operatives Ereignis |

### §28.2 Abdeckung

≥ 40 Unit-Tests, ≥ 20 Integrationstests; alle Fail-Closed-Pfade; alle Negativtests (Injektion, Leckage, VETO).

### §28.3 Roadmap-Phasen

| Phase | Inhalt | Dauer |
|---|---|---|
| S1 | Verträge & Enums in CONTRACTS §6.11, StrategicLayerConfig | 2–3 Tage |
| S2 | Kanzler-Erweiterung (Briefing, Validator, Translation, RoyalLog, Eskalation, SAFETY-RESPONSE) | 4–5 Tage |
| S3 | KOENIGIN.md-Umsetzung (Stateless-Aufruf, Sanitization, Fallback) | 3–4 Tage |
| S4 | Vordenker-Erweiterung (Trigger, Seed-Modus, DimensionOnboarding), Signal-Korrektur QUESTOR §10.5, Twin-Härtung, REPLICATE | 5–6 Tage |
| S-INT | Integration & Regression (Suite STRAT) | 4–6 Tage |

---

## §29 Restrisiken (bewusst dokumentiert)

1. **LLM-Qualität des Vordenkers** bei echten wissenschaftlichen Durchbrüchen ist nur mit realen Domänen validierbar.
2. **Manifest-Qualität:** Schlechte menschliche Constraints schützen nur vor Verletzung, nicht vor Sinnlosigkeit.
3. **CHARTER-Präambel:** Bis zur formellen Freigabe bleibt dieser Änderungsantrag Backlog v3.0.0.

---

## Anhang A: Fund-Register (Behebungsstatus)

| Cluster | Funde | Behoben durch |
|---|---|---|
| C1 Kaltstart | PROB-02/04; 1.1/1.2/1.3; F-01–F-07 | §4 (SL-BOOT-1..7), §8.1 |
| C2 Direktive→Policy | PROB-03; F-04/05/17/29/32; 4.2 | §6.3/6.4 (SL-DIR, SL-DTT) |
| C3 Manifest & Constraints | PROB-01/23/35; 6.1/6.2; 4.2; F-18/19/25/26 | §6.1, §10 (SL-MAN) |
| C4 Safety-Reaktion | PROB-15; F-20; 5.3 | §11 (SL-SAF) |
| C5 Twin-Loop | PROB-08/13/14/39; 3.1/3.2/3.3; F-21 | §12 (SL-TWIN) |
| C6 Signal-Semantik | PROB-06; F-14/31 | §9 (SL-SIG) |
| C7 Dimensions | PROB-11/12; 2.1/2.2/2.3; F-10/34 | §13 (SL-DIM) |
| C8 Capability-Gap | PROB-18; 5.1/5.2; F-11/12; 1.3 | §14, §6.6/6.8 |
| C9 Mensch-Schnittstelle | PROB-17/19/22/28; F-15/16; 8.3 | §15, §6.9 (SL-ESC) |
| C10 Briefing | PROB-16/29/31/37; F-24/28 | §6.2 (SL-BRF), §16 |
| C11 Sanitization | PROB-01/20; 7.1/7.2/7.3; F-22/23 | §17 (SL-SAN) |
| C12 Abschlussbericht | PROB-27/28; 8.1/8.2/8.3 | §18 (SL-RPT) |
| C13 Replikation | PROB-36 | §19 (SL-REP) |
| C14 Integrität | PROB-07/25/30/40; F-30/36 | §20 (SL-INT) |
| C15 Grunddefinitionen | PROB-05/09/10*/21/24/32/33/34; F-08/09/13*/27/33/35 | §1, §8.2/8.3, §21.5, §23, §12.7 |

\* PROB-10/F-13 (Review-Autorität EXPLAINS/Quarantäne-Aufhebung): in dieser Version wie folgt festgelegt — nicht-sicherheitsrelevante Fractures: Kanzler; sicherheitsrelevante: Mensch; RESOLVES aus CRITICAL: Mensch. *(Nachtrag zu C15)*

---

## Anhang B: Dokumentenhierarchie

Dieses Dokument ist ein Entwurf in `specs/` und referenziert:
- `foundation/CHARTER.md` (Sicherheitsregeln, SR-XX)
- `foundation/CONTRACTS.md` (§6.10 bestehend, §6.11 neu)
- `specs/GREMIUM.md`, `specs/QUESTOR.md`, `specs/HAL.md`
- Änderungsantrag `DIGITAL-TWIN-SEM-1.0.0`

Regel: Bei Widersprüchen gilt CHARTER > CONTRACTS > dieses Dokument. Nach Übernahme in die Zieldokumente wird diese Datei als ARCHIVIERT markiert.