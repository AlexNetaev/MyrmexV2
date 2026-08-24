# 🏛️ STANDALONE STRUCTURE GREMIUM — „COGNITIVE OBSERVATORY"

| Feld | Wert |
|---|---|
| Dateiname | specs/standalone_structure_gremium_v0.1.0.md |
| Version | 0.1.0 |
| Status | ENTWURF — Änderungsantrag STRATEGIC-LAYER-2.0.0 |
| System | MYRMEX v2.4.0 + Questor v0.2.3 + HAL v0.2.0 |
| Baut auf | CHARTER 1.0.0, CONTRACTS 1.1.0-atlas-hyb.1, GREMIUM 1.1.0-atlas-hyb.1, DIGITAL-TWIN-SEM-1.0.0 |
| Schicht | Layer 1 (specs/) — referenziert foundation/ |
| Konfliktregel | CHARTER > CONTRACTS > dieses Dokument |

---

## §0 Zweck, Designziele und Nicht-Ziele

### §0.1 Zweck

Dieses Dokument definiert die **strategische Kognitionsschicht** des Gremiums: ein System, das über Wochen autonom forschen kann, ohne Context Drift, ohne CHARTER-Verletzungen und ohne dass ein LLM jemals final entscheidet.

Es vereint die Stärken dreier Entwurfslinien:

| Quelle | Übernommenes Kernkonzept |
|---|---|
| Constitutional Observatory (P2) | Forschungs-Manifest als invariante „Verfassung", Cluster-Bridging |
| Kognitives Gremium (P1) | Anchor Protocol (RoyalLog), Symptom-Trigger, DimensionOnboardingRequest, Capability-Gap |
| Stateless Director (P3) | Zustandslose Königin, StrategicBriefing, Atlas-Topology-Prompting |
| DIGITAL-TWIN-SEM-1.0.0 | DIGITAL_TWIN-Knoten, TwinDivergenceReport, Kalibrierungs-Loop |

### §0.2 Designziele (priorisiert)

1. **CHARTER-Treue**: Keine der 58 Sicherheitsregeln wird verletzt. LLM bleibt Advisor (SR-13), menschliche Königin wird nie überstimmt (SR-11).
2. **Drift-Freiheit**: Die Königin-LLM hat keinen persistenten Gesprächskontext. Jeder Aufruf ist frisch, kuratiert und konstitutionell verankert.
3. **Deterministische Endentscheidung**: Jede LLM-Ausgabe wird durch den Kanzler deterministisch validiert, bevor sie Wirkung entfaltet.
4. **Wissenschaftliche Emergenz**: Das System kann versteckte Variablen entdecken (Dimensions-Expansion), Widersprüche diagnostizieren (Fracture) und Domänen wechseln (Pivot).
5. **Krisenfestigkeit**: ESTOP, Twin-Drift, Capability-Gaps und Deadlocks haben definierte, fail-closed Eskalationspfade.
6. **Rückwärtskompatibilität**: Alle neuen Verträge sind optional. Questor und HAL bleiben unverändert.

### §0.3 Nicht-Ziele

- Keine Änderung der CHARTER-Sicherheitsregeln (nur präzisierende Interpretation).
- Keine Schreibrechte für Questor, HAL oder LLM-Komponenten in Atlas/Archiv.
- Keine direkten Aufrufe zwischen Gremiums-Rängen (Blackboard-Pattern bleibt absolut).
- Kein LLM-Einsatz im Kanzler, Pre-Filter, Lotse, Quartiermeister oder Richter.

---

## §1 Architektur-Überblick

### §1.1 Gesamtsystem mit strategischer Schleife

```text
┌───────────────────────────────────────────────────────────────────────┐
│  MENSCHLICHE KÖNIGIN / SPONSOR (SR-11: niemals überstimmt)            │
│  → setzt Forschungs-Manifest, genehmigt physische Dimensions-         │
│    expansion, kann jederzeit SAFE_MODE / HUMAN_OVERRIDE auslösen      │
└──────────────────────────────┬────────────────────────────────────────┘
                               │ Manifest + Weisungen + Overrides
                               ▼
┌───────────────────────────────────────────────────────────────────────┐
│  SCHICHT 5: 👑 KÖNIGIN (LLM, STATELESS + CONSTITUTIONAL)              │
│  IN : ResearchManifest + StrategicBriefing + RoyalLog-Anker (3)       │
│  OUT: StrategicDirective (schema-validiertes JSON, nur Vorschlag)     │
└──────────────────────────────┬────────────────────────────────────────┘
                               │ StrategicDirective (Vorschlag)
                               ▼
┌───────────────────────────────────────────────────────────────────────┐
│  SCHICHT 4: 🏛️ GREMIUM                                                │
│                                                                       │
│  🏛️ KANZLER (deterministisch, kein LLM)                               │
│     • validiert Direktiven (Manifest, Safety, Budget) → VETO möglich │
│     • erzeugt StrategicBriefings (PERIODIC / URGENT / FINAL)         │
│     • setzt ExplorationPolicy, ResearchTopics                        │
│     • führt RoyalLog (operatives Entscheidungsjournal)               │
│     • genehmigt/eskaliert DimensionOnboardingRequests                │
│                                                                       │
│  🗺️ KARTOGRAPH → erkennt Symptome + TwinDivergenceReports             │
│        │ SymptomEvent (via Blackboard)                                │
│        ▼                                                              │
│  🧠 VORDENKER (LLM, grounded, Topology-Prompting)                     │
│     → ScientificHypothesis + optional DimensionOnboardingRequest      │
│        ▼                                                              │
│  🧭 LOTSE (deterministisch) → Wegmarken + CapabilityGapSignal         │
│        ▼                                                              │
│  📦 QUARTIERMEISTER → ResearchPackage                                 │
│        ▼                                                              │
│  ⚖️ SICHERHEITSRAT (Richter + Seher) → GateRecord                     │
│        ▼                                                              │
│  Stufe 8: Dispatcher → Questor → Receiver → Archivar                  │
└──────────────────────────────┬────────────────────────────────────────┘
                               ▼
        SCHICHT 3 (Dispatch) → SCHICHT 2 (Questor) → SCHICHT 1 (HAL)
                               │
                               ▼ questor_ergebnis_paket
        Archivar → Kartograph → ATLAS (Blackboard, Single Source)
```

### §1.2 Der strategische Regelkreis

```text
                 ┌────────────────────────────────┐
                 │                                │
                 ▼                                │
   ATLAS-ZUSTAND ──► KANZLER erzeugt             │
   (Kartograph)      StrategicBriefing           │
                         │                        │
                         ▼                        │
                     KÖNIGIN (LLM)               │
                         │                        │
                         ▼                        │
                  StrategicDirective              │
                         │                        │
                         ▼                        │
                  KANZLER validiert               │
                    ├─ VETO → RoyalLog(REJECTED) ─┤ (nächster Zyklus)
                    ├─ ESCALATION → Mensch        │
                    └─ ACCEPT → ExplorationPolicy │
                         │                        │
                         ▼                        │
                  9-Stufen-Pipeline               │
                  (Ideen → Pakete → Questor)      │
                         │                        │
                         ▼                        │
                  Neue Kristalle/Signale ─────────┘
```

---

## §2 Kern-Patterns

### §2.1 Constitutional Anchor Protocol (Anti-Drift, 3 Schichten)

Jeder Königin-LLM-Aufruf erhält exakt drei Kontextblöcke — nichts anderes:

```text
┌──────────────────────────────────────────────────────────────────┐
│ SCHICHT 1 — CONSTITUTIONAL MEMORY (invariant)                    │
│   ResearchManifest als System-Prompt:                            │
│   • mission_goal (max 2048 Zeichen)                              │
│   • hard_constraints (unveränderlich, nur Mensch darf ändern)    │
│   • soft_preferences (durch Direktiven anpassbar)                │
│   • Verbotene Aktionen (Safety-Overrides, Atlas-Schreibzugriff)  │
│   • Output-Schema (StrategicDirective)                           │
├──────────────────────────────────────────────────────────────────┤
│ SCHICHT 2 — STATELESS BRIEFING (dynamisch, kuratiert)            │
│   StrategicBriefing, deterministisch vom Kanzler erzeugt:        │
│   • AtlasMacroState (aggregierte Metriken, keine Rohknoten)      │
│   • BudgetState, aktive Fractures, Twin-Status                   │
│   • DecisionsRequired (strukturierte Handlungsoptionen)          │
│   • KEIN security_mode, KEINE Atlas-Hybrid-Referenzen            │
├──────────────────────────────────────────────────────────────────┤
│ SCHICHT 3 — ROYAL LOG ANCHOR (Kontinuität)                       │
│   Letzte N=3 eigene StrategicDirectives + deren Outcome          │
│   (IMPLEMENTED / REJECTED / SUPERSEDED / EXPIRED)                │
│   → vom Kanzler aus dem RoyalLog extrahiert, nie direkter        │
│     Archiv-Zugriff der Königin                                   │
└──────────────────────────────────────────────────────────────────┘
```

**Invarianten:**
- Kein persistenter Gesprächsverlauf der Königin-LLM. Jeder Aufruf ist ein frischer Kontext.
- Die Königin erhält niemals Roh-Atlas-Daten, niemals `security_mode`, niemals Blackbox-Inhalte.
- Bei LLM-Fehler/Timeout: deterministischer Fallback = „aktuelle ExplorationPolicy bleibt unverändert" + Alert an Kanzler (SR-28 analog).

### §2.2 Stateless Director

Die Königin ist eine **zustandslose Direktorin**: Sie kennt nur das, was ihr im aktuellen Aufruf übergeben wird. Strategisches Gedächtnis entsteht ausschließlich durch:
1. das invariante Manifest (Zielkonstanz),
2. den RoyalLog-Anker (Entscheidungskontinuität),
3. den Atlas selbst (Wissensgedächtnis, für die Königin nur als Aggregat sichtbar).

### §2.3 Deterministic Gatekeeper (Kanzler)

Der Kanzler ist **rein deterministisch** (kein LLM, auch nicht für Zusammenfassungen — diese werden template-basiert erzeugt). Er ist die einzige Instanz, die:
- StrategicBriefings erzeugt (Informations-Flaschenhals),
- StrategicDirectives validiert und in ExplorationPolicy übersetzt,
- das RoyalLog führt,
- DimensionOnboardingRequests prüft.

### §2.4 Topology-Grounded Hypothesis Engine (Vordenker)

Der Vordenker wird nicht passiv, sondern über **Symptom-Trigger** aktiviert. Er nutzt **Topology-Prompting** (Fracture / Void / Bridge / Twin-Drift) auf kuratierten Atlas-Ausschnitten. Graph-RAG ist optional erlaubt, da laut Zugriffsmatrix (GREMIUM §6.12) der Vordenker den Atlas lesen darf — jedoch nur lesend, nie schreibend, und alle Ausgaben laufen durch Pre-Filter und Lotse.

### §2.5 Digital-Twin-Loop (gemäß DIGITAL-TWIN-SEM-1.0.0)

Sim-Kristalle (`evidence_class = SIMULATION`) aktualisieren ausschließlich `DIGITAL_TWIN`-Knoten. Der Kartograph erzeugt bei Sim-vs-Real-Vergleich einen `TwinDivergenceReport`. Bei `calibration_required = true` entsteht ein `URGENT`-StrategicBriefing und die Königin kann `CALIBRATE_TWIN` anweisen — Kalibrierung läuft immer als `DIAGNOSE`-Paket im SANDBOX/Compute-Modus, niemals physisch.

---

## §3 Rollen und Verantwortlichkeiten

### §3.1 Rollen-Matrix

| Rolle | Kognitive Funktion | LLM | Atlas lesen | Atlas schreiben | Neue Artefakte |
|---|---|---|---|---|---|
| 👑 Königin | Vision, Pivot, Budget-Freigabe, Abschlussbericht | Ja (stateless + constitutional) | ❌ (nur Briefings) | ❌ | StrategicDirective, FinalScientificReport (Entwurf) |
| 🏛️ Kanzler | Briefing, Validierung, Policy, RoyalLog, Dimension-Governance | Nein | ✅ (Metriken) | ❌ | StrategicBriefing, RoyalLogEntry, ExplorationPolicy |
| 🧠 Vordenker | Kausale Modelle, Hypothesen, Dimensions-Vorschläge | Ja (grounded) | ✅ (Topologie) | ❌ | ScientificHypothesis, DimensionOnboardingRequest |
| 🧭 Lotse | Physische Erdung, Capability-Check | Nein | ✅ (Geometrie) | ✅ (nur Wegmarken) | DiagnosticWaypoint, CapabilityGapSignal |
| 📦 Quartiermeister | Paketbau | Nein | ✅ | ❌ | ResearchPackage |
| 🗺️ Kartograph | Wissensstruktur, Symptome, Twin-Divergenz | Nein | ✅ | ✅ | SymptomEvent, TwinDivergenceReport |
| 📚 Archivar | Wissensaufnahme | Nein | ❌ | ✅ (Kristalle/Signale) | — |
| ⚖️ Sicherheitsrat | Gate | Seher: Ja (nur Advisor) | ✅ eingeschränkt | ❌ (nie 🟥) | GateRecord |
| 🧭 Questor | Ausführung | nur Advisor-intern | ❌ | ❌ | questor_ergebnis_paket |

### §3.2 Königin (Schicht 5) — neue Pflichten

1. Erzeugt zu jedem StrategicBriefing **genau eine** StrategicDirective (oder explizit `NO_ACTION`).
2. Begründet jede Direktive (`reason`, max 1024 Zeichen) gegen das Manifest.
3. Darf nur Intents aus dem `DirectiveIntent`-Enum verwenden.
4. Darf niemals SafetyConstraints aufheben, niemals `security_mode` referenzieren, niemals Ausführungsbefehle formulieren.

**Verbote:** direkter Atlas-/Archivzugriff; direkte Kommunikation mit Vordenker/Lotse/Questor; Setzen von ExplorationPolicy; finale Entscheidungen.

### §3.3 Kanzler — neue Pflichten (Erweiterung zu GREMIUM §3.3)

1. **Briefing-Generator**: Erzeugt PERIODIC-Briefings alle `briefing_interval_cycles` und URGENT-Briefings bei:
   - `fracture_score ≥ full_rebuild_threshold` in einer aktiven Zone,
   - `TwinDivergenceReport.tolerance_breached = true`,
   - Topic `SATURATED` ohne Zielerreichung bei Budget > `stagnation_budget_threshold`,
   - `LOCKED`-Zone ohne genehmigte Diagnose-Strategie,
   - 2 aufeinanderfolgenden VETOs gegen Königin-Direktiven.
2. **Directive-Validator**: Prüft jede Direktive in fester Reihenfolge (siehe §5.2).
3. **RoyalLog-Führer**: Schreibt nach jeder Direktiven-Entscheidung einen `RoyalLogEntry`.
4. **Dimension-Governance**: Prüft DimensionOnboardingRequests; genehmigt nur, wenn physikalisch sinnvoll, messbar und safety-konform; eskaliert an Mensch bei physischer Auswirkung.
5. **Final-Briefing**: Bei `MISSION_COMPLETE` oder `ABORT` erzeugt er das FINAL-Briefing für den Abschlussbericht.

### §3.4 Vordenker — neue Pflichten (Erweiterung zu GREMIUM §3.4)

1. Verarbeitet `SymptomEvent`s des Kartographen (via Blackboard).
2. Wählt Prompting-Strategie nach Symptomtyp (§6, Schritt D).
3. Erzeugt je Trigger 1–3 `ScientificHypothesis`-Objekte inkl. `prozess_skizze` (G-5).
4. Darf bei erkannten versteckten Variablen einen `DimensionOnboardingRequest` anhängen.
5. Erhält bei `CapabilityGapSignal` Feedback und darf die Hypothese an reale Capabilities anpassen.

**Verbote:** Wegmarken platzieren, Dimensionen eigenmächtig erstellen, Sicherheitsfreigaben erteilen, FrontierCandidates als ausführbar markieren.

### §3.5 Kartograph — neue Pflichten

1. Erzeugt `SymptomEvent`s bei definierten Atlas-Zuständen (§5.4).
2. Erzeugt `TwinDivergenceReport` gemäß DIGITAL-TWIN-SEM-1.0.0 Regel 2.
3. Aktualisiert `DIGITAL_TWIN`-Knoten nach Kalibrierung (Regel 3/4 des Twin-Antrags).

### §3.6 Lotse — neue Pflicht

Erzeugt ein `CapabilityGapSignal`, wenn eine Hypothese nicht mit verfügbaren Capabilities planbar ist. Das Signal geht an den Vordenker (Re-Planung) oder bei Budget-/Hardware-Relevanz als `DecisionOption` ins nächste StrategicBriefing.

---

## §4 Neue Datenverträge (Änderungsantrag an CONTRACTS.md §6.11)

> Regel: Diese Verträge werden in `CONTRACTS.md` als §6.11 „Strategic Layer" aufgenommen. Dieses Dokument definiert sie nur, CONTRACTS ist Single Source of Truth. Alle Felder mit Freitext erhalten Injection-Scan gemäß Sanitization-Pipeline.

### §4.1 ResearchManifest

```python
class ResearchManifest(BaseModel):
    manifest_id: str
    mission_goal: str                      # max 2048 Zeichen, Injection-Scan
    hard_constraints: list[str]            # nur Mensch darf ändern
    soft_preferences: list[str]            # via Direktive anpassbar
    domain: str
    objective_family_ref: Optional[str]    # Verweis auf ObjectiveFamily
    valid_from: str
    valid_until: Optional[str]
    created_by: str
    approved_by: str                       # IMMER menschliche Königin
    version: str                           # semantisch
    created_at: str
    updated_at: str
```

### §4.2 StrategicBriefing und Teilstrukturen

```python
class BriefingType(str, Enum):
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

class BudgetState(BaseModel):
    total_budget_cycles: int
    used_cycles: int
    remaining_cycles: int
    burn_rate_per_cycle: float
    estimated_completion_cycle: Optional[int]

class RiskLevel(str, Enum):
    LOW = "LOW"; MEDIUM = "MEDIUM"; HIGH = "HIGH"

class DecisionOption(BaseModel):
    option_id: str
    description: str                       # max 512 Zeichen, Injection-Scan
    impact: str                            # max 512 Zeichen
    risk_level: RiskLevel
    requires_human_approval: bool

class FractureSummary(BaseModel):
    zone_ref: str
    fracture_score: float
    conflict_count: int
    since_cycles: int

class TwinStatusSummary(BaseModel):
    twin_node_ref: str
    display_name: str
    drift_score: float
    divergence_threshold: float
    calibration_required: bool

class StrategicBriefing(BaseModel):
    briefing_id: str
    zyklus_id: str
    briefing_type: BriefingType
    manifest_version_ref: str
    atlas_macro_state: AtlasMacroState
    budget_state: BudgetState
    active_fractures: list[FractureSummary] = []
    twin_status: list[TwinStatusSummary] = []
    active_topics: list[TopicSummary] = []
    decisions_required: list[DecisionOption] = []
    royal_log_anchor: list[RoyalLogAnchor] = []   # letzte N Direktiven
    generated_at: str
    generated_by: str                      # IMMER "KANZLER" (deterministisch)
```

**Sanitization-Regeln für StrategicBriefing:**
- Nur aggregierte Metriken; keine Roh-Knoten, keine `metric_vector`-Rohdaten.
- `security_mode` ist verboten (SR-29 analog).
- Atlas-Hybrid-Referenzfelder (`atlas_expectation_ref`, `frontier_candidate_ref` …) sind verboten (QUESTOR §12.2a analog).
- Maximale Gesamtlänge: `max_briefing_chars` (Default 8192).

### §4.3 StrategicDirective

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
    HUMAN_ESCALATION = "HUMAN_ESCALATION"

class DirectiveStatus(str, Enum):
    PROPOSED = "PROPOSED"          # von LLM erzeugt
    ACCEPTED = "ACCEPTED"          # Kanzler validiert
    VETOED = "VETOED"              # Kanzler-Veto
    ESCALATED = "ESCALATED"        # an Mensch übergeben
    IMPLEMENTED = "IMPLEMENTED"    # in Policy übersetzt
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"      # durch neuere Direktive ersetzt
    EXPIRED = "EXPIRED"            # valid_for_cycles abgelaufen

class StrategicDirective(BaseModel):
    directive_id: str
    briefing_ref: str                      # Pflicht: Bezug zum Briefing
    intent: DirectiveIntent
    target_ref: Optional[str]              # Zone, Topic, Dimension, Twin
    parameters: dict[str, Any] = {}
    reason: str                            # max 1024 Zeichen, Injection-Scan
    keep_constraints: list[str] = []
    drop_constraints: list[str] = []       # nur soft_preferences!
    priority: float = 0.5                  # 0.0–1.0
    valid_for_cycles: int = 10
    created_at: str
```

**Harte Validierungsregeln:**
- `drop_constraints` darf niemals `hard_constraints` des Manifests enthalten → sonst VETO.
- `UNLOCK_BUDGET` über `budget_unlock_threshold` → `requires_human_approval`.
- `ABORT_MISSION` → immer `ESCALATED` an Mensch (Bestätigung erforderlich).
- `ADD_DIMENSION_HINT` erzeugt einen prüfpflichtigen `DimensionOnboardingRequest`.

### §4.4 RoyalLog

```python
class DirectiveOutcome(str, Enum):
    IMPLEMENTED = "IMPLEMENTED"
    VETOED = "VETOED"
    SUPERSEDED = "SUPERSEDED"
    EXPIRED = "EXPIRED"
    ESCALATED = "ESCALATED"

class RoyalLogEntry(BaseModel):
    entry_id: str
    directive_ref: str
    briefing_ref: str
    outcome: DirectiveOutcome
    outcome_reason: Optional[str]          # max 512 Zeichen
    policy_effect_ref: Optional[str]       # resultierende ExplorationPolicy
    timestamp: str

class RoyalLogAnchor(BaseModel):
    directive_ref: str
    intent: DirectiveIntent
    outcome: DirectiveOutcome
    age_cycles: int
```

Regeln: RoyalLog ist ein **operatives Governance-Journal** (kein wissenschaftliches Signal, SR-08). Es wird vom Kanzler geführt und liegt im operationalen Archivbereich. Die Königin erhält niemals Schreibzugriff.

### §4.5 SymptomEvent und ScientificHypothesis

```python
class SymptomType(str, Enum):
    WEISSRAUM = "WEISSRAUM"
    FRACTURE_GAP = "FRACTURE_GAP"
    SATURATION = "SATURATION"
    BRIDGE_OPP = "BRIDGE_OPP"
    TWIN_DRIFT = "TWIN_DRIFT"
    CAPABILITY_GAP_FEEDBACK = "CAPABILITY_GAP_FEEDBACK"

class SymptomEvent(BaseModel):
    event_id: str
    symptom_type: SymptomType
    zone_ref: Optional[str]
    atlas_refs: list[str] = []             # deterministisch kuratierte Knoten/Kanten
    metrics_snapshot: dict[str, float] = {}
    twin_divergence_report_ref: Optional[str] = None
    created_at: str

class HypothesisStatus(str, Enum):
    PROPOSED = "PROPOSED"
    PRE_FILTER_PASSED = "PRE_FILTER_PASSED"
    WAYPOINT_PLACED = "WAYPOINT_PLACED"
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"

class ScientificHypothesis(BaseModel):
    hypothesis_id: str
    hypothesis_text: str                   # max 2048 Zeichen, Injection-Scan
    expected_outcome: str                  # max 1024 Zeichen
    source_trigger: SymptomType
    atlas_refs: list[str] = []
    zone_ref: Optional[str]
    dimension_onboarding_request: Optional["DimensionOnboardingRequest"] = None
    prozess_skizze: str                    # Pflicht (G-5)
    confidence_estimate: float             # 0.0–1.0, LLM-Schätzung (nicht final)
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    created_at: str
```

### §4.6 DimensionOnboardingRequest

```python
class DimensionRequestStatus(str, Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"

class DimensionOnboardingRequest(BaseModel):
    request_id: str
    proposed_dimension_id: str
    display_name: str
    domain: str
    value_type: DimensionValueType         # aus CONTRACTS §6.10.4
    unit: Optional[str] = None
    rationale: str                         # max 2048 Zeichen, Injection-Scan
    source_hypothesis_ref: str
    source_trigger: SymptomType
    suggested_value_range: Optional[tuple[float, float]] = None
    suggested_categories: Optional[list[str]] = None
    requires_physical_actuation: bool = False
    status: DimensionRequestStatus = DimensionRequestStatus.PROPOSED
    reviewed_by: Optional[str] = None      # KANZLER oder MENSCH
    reviewed_at: Optional[str] = None
    created_at: str
```

Regeln:
- Genehmigung erzeugt eine `TypedDimension` mit `approved = false`.
- Physische Nutzung erfordert weiterhin `dimension_expansion_approval` im ResearchPackage (PolicyEvaluator-Prüfung 7, QUESTOR §6.2).
- `requires_physical_actuation = true` → zwingend `ESCALATED` an menschliche Königin.

### §4.7 CapabilityGapSignal

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

### §4.8 FinalScientificReport

```python
class FinalScientificReport(BaseModel):
    report_id: str
    topic_ref: str
    manifest_ref: str
    summary_markdown: str                  # von Königin-LLM entworfen
    key_crystal_refs: list[str] = []
    rejected_hypotheses_count: int
    twin_calibration_history: list[str] = []
    safety_warnings: list[str] = []
    generated_at: str
    human_reviewed: bool = False
```

Regel: Der Report ist ein **Entwurf** für den Menschen. Er wird erst nach `human_reviewed = true` als Abschlussdokument geführt.

---

## §5 Zustandsmaschinen und Lebenszyklen

### §5.1 Strategischer Zyklus

```text
ZYKLUS_START
    │
    ▼
BRIEFING_ERZEUGT (Kanzler, deterministisch)
    │
    ▼
DIREKTIVE_ANGEFORDERT (LLM-Aufruf mit 3 Kontextblöcken)
    │
    ├── LLM-Fehler/Timeout ──► FALLBACK: keine Direktive, Policy bleibt,
    │                          Alert + RoyalLogEntry(EXPIRED-Kommentar)
    ▼
DIREKTIVE_PROPOSED
    │
    ▼
VALIDIERUNG (§5.2, feste Reihenfolge)
    │
    ├── FAIL ──────────────► VETOED → RoyalLog → nächster Zyklus
    ├── HUMAN_REQUIRED ────► ESCALATED → Mensch entscheidet
    └── PASS ──────────────► ACCEPTED
                                │
                                ▼
                        POLICY_UMGESETZT (ExplorationPolicy / Topics)
                                │
                                ▼
                        IMPLEMENTED → RoyalLog → Pipeline läuft
```

### §5.2 Validierungspipeline des Kanzlers (feste Reihenfolge)

```text
StrategicDirective
    │
    ├─ 1. Schema-Validierung (Pydantic, Enum, Längen)
    │      FAIL → VETO("SCHEMA_INVALID")
    ├─ 2. Manifest-Prüfung
    │      • verstößt gegen hard_constraints? → VETO("MANIFEST_VIOLATION")
    │      • drop_constraints enthält hard_constraint? → VETO
    ├─ 3. Safety-Prüfung
    │      • aktive SafetyConstraint betroffen? → VETO("SAFETY_ACTIVE")
    │      • Injection-/Safety-Claim in reason? → VETO + Audit
    ├─ 4. Budget-Prüfung
    │      • UNLOCK_BUDGET über Threshold? → ESCALATED (Mensch)
    ├─ 5. Capability-Plausibilität
    │      • Ziel benötigt unbekannte Capability? → nur als DecisionOption,
    │        nicht als automatische Freigabe
    ├─ 6. Intent-spezifische Sonderregeln (§4.3)
    │      • ABORT_MISSION → ESCALATED
    │      • CALIBRATE_TWIN ohne drifted Twin → VETO("NO_DRIFT")
    └─ 7. ACCEPT → übersetze in ExplorationPolicy / ResearchTopic-Änderung
```

### §5.3 DimensionOnboarding-Lebenszyklus

```text
VORDENKER schlägt vor (via ScientificHypothesis)
    │
    ▼
PROPOSED
    │
    ▼
KANZLER-PRÜFUNG (deterministisch)
    ├─ physikalisch sinnvoll? messbar? safety-konform?
    ├─ NEIN ───────────────► REJECTED (archiviert für Audit)
    ├─ requires_physical_actuation = true ─► ESCALATED → Mensch
    └─ JA, nicht-physisch ─► APPROVED
                                 │
                                 ▼
                    TypedDimension erzeugt (approved = false)
                                 │
                    physische Nutzung erst nach
                    dimension_expansion_approval (Mensch/Kanzler
                    gemäß bestehender Approval-Regeln)
```

### §5.4 Symptom-Trigger (Kartograph, deterministisch)

| Symptom | Bedingung | Vordenker-Aktion |
|---|---|---|
| WEISSRAUM | `evidence_mass == 0` und `coverage_energy ≈ 0` in aktiver Frontier-Region | Void-Prompting: Screening-Strategie |
| FRACTURE_GAP | `fracture_score ≥ quarantine_threshold` | Fracture-Prompting: erklärende Hypothese, ggf. DimensionOnboardingRequest |
| SATURATION | `uncertainty_score` sinkt über `saturation_window_cycles` nicht, Topic → SATURATED | Paradigma-Wechsel: neue Dimension/Methode |
| BRIDGE_OPP | Cluster-übergreifende Kanten zwischen unterschiedlichen Domänen | Bridge-Prompting: interdisziplinäre Hypothese |
| TWIN_DRIFT | `TwinDivergenceReport.tolerance_breached = true` | Twin-Calibration-Prompting |
| CAPABILITY_GAP_FEEDBACK | CapabilityGapSignal des Lotsen | Hypothese an Capabilities anpassen |

Regel: Ein Symptom-Ereignis erzeugt niemals direkt ein Paket. Der Pfad bleibt immer: Vordenker → Pre-Filter → Lotse → Quartiermeister → Gate → Dispatch.

---

## §6 Datenflüsse in Einzelschritten (mit Diagrammen)

### Schritt A — Missionsstart und Manifest

```text
MENSCH                KANZLER                     KÖNIGIN (LLM)
  │                      │                             │
  │ Ziel + Constraints   │                             │
  ├─────────────────────►│                             │
  │                      │ ResearchManifest erstellen  │
  │                      │ (approved_by = Mensch)      │
  │                      │ ResearchTopic PROPOSED      │
  │                      │ ExplorationPolicy initial   │
  │                      │                             │
  │                      │ StrategicBriefing(PERIODIC) │
  │                      ├────────────────────────────►│
  │                      │                             │ StrategicDirective
  │                      │◄────────────────────────────┤ (INITIAL_SWEEP)
  │                      │ Validierung (§5.2)          │
  │                      │ → Policy + Topics setzen    │
  │                      │ RoyalLogEntry(IMPLEMENTED)  │
```

### Schritt B — Briefing-Erzeugung (Kanzler, deterministisch)

```text
ATLAS (Blackboard)                KANZLER
  │                                  │
  │ AtlasZoneSummary-Metriken        │
  ├─────────────────────────────────►│
  │ FrontierCandidates               │ 1. Aggregieren → AtlasMacroState
  ├─────────────────────────────────►│ 2. Budget aus Zyklen-Log → BudgetState
  │ TwinDivergenceReports            │ 3. Fractures filtern → FractureSummary[]
  ├─────────────────────────────────►│ 4. Twin-Status → TwinStatusSummary[]
  │ ResearchTopic-Zustände           │ 5. Handlungsoptionen ableiten
  ├─────────────────────────────────►│    → DecisionOption[]
  │ RoyalLog                         │ 6. Letzte 3 Direktiven → RoyalLogAnchor[]
  ├─────────────────────────────────►│ 7. Sanitization-Check (Länge, Verbote)
  │                                  │ 8. StrategicBriefing schreiben (Blackboard)
```

### Schritt C — Direktiven-Validierung (Kanzler)

```text
StrategicDirective (LLM-Output)
        │
        ▼
┌─────────────────┐    FAIL    ┌──────────────────────────┐
│ Schema-Check    ├───────────►│ VETO + Audit-Event        │
└────────┬────────┘            │ RoyalLogEntry(VETOED)     │
         │ PASS                └──────────────────────────┘
         ▼
┌─────────────────┐    FAIL    ┌──────────────────────────┐
│ Manifest-Check  ├───────────►│ VETO("MANIFEST_VIOLATION")│
└────────┬────────┘            └──────────────────────────┘
         │ PASS
         ▼
┌─────────────────┐    FAIL    ┌──────────────────────────┐
│ Safety-Check    ├───────────►│ VETO("SAFETY_ACTIVE")     │
└────────┬────────┘            └──────────────────────────┘
         │ PASS
         ▼
┌─────────────────┐  HUMAN_REQ ┌──────────────────────────┐
│ Budget/Intent-  ├───────────►│ ESCALATED → Mensch        │
│ Sonderregeln    │            │ SAFE_MODE möglich         │
└────────┬────────┘            └──────────────────────────┘
         │ PASS
         ▼
ExplorationPolicy aktualisieren → ResearchTopics steuern
RoyalLogEntry(IMPLEMENTED) → nächster strategischer Zyklus
```

### Schritt D — Symptom → Hypothese → Wegmarke

```text
KARTOGRAPH                VORDENKER (LLM)              PRE-FILTER      LOTSE
    │                          │                          │              │
    │ SymptomEvent             │                          │              │
    │ (z.B. FRACTURE_GAP)      │                          │              │
    ├─────────────────────────►│                          │              │
    │                          │ 1. Topologie-Ausschnitt  │              │
    │                          │    lesen (Blackboard)    │              │
    │                          │ 2. Prompt-Strategie:     │              │
    │                          │    FRACTURE/VOID/BRIDGE  │              │
    │                          │ 3. LLM generiert         │              │
    │                          │    ScientificHypothesis  │              │
    │                          │    (+prozess_skizze)     │              │
    │                          │ ScientificHypothesis     │              │
    │                          ├─────────────────────────►│              │
    │                          │                          │ Dimensionen, │
    │                          │                          │ Quarantäne,  │
    │                          │                          │ Safety prüfen│
    │                          │                          ├─────────────►│
    │                          │                          │              │ Wegmarke
    │                          │                          │              │ platzieren
    │                          │                          │              │ (Atlas)
    ▼                          ▼                          ▼              ▼
  Atlas bleibt              kein Schreibrecht          deterministisch  nur Wegmarken
  unverändert               in Atlas                   fail-closed
```

### Schritt E — DimensionOnboardingRequest

```text
VORDENKER            KANZLER                 MENSCH (falls physisch)      ATLAS
    │                    │                              │                   │
    │ Hypothese mit      │                              │                   │
    │ DimensionRequest   │                              │                   │
    ├───────────────────►│                              │                   │
    │                    │ deterministische Prüfung:    │                   │
    │                    │ sinnvoll? messbar? safety?   │                   │
    │                    │                              │                   │
    │                    ├─ nicht-physisch → APPROVED   │                   │
    │                    │                              │                   │
    │                    ├─ physisch → ESCALATED        │                   │
    │                    ├─────────────────────────────►│                   │
    │                    │                              │ genehmigt/ablehnen│
    │                    │◄─────────────────────────────┤                   │
    │                    │ APPROVED → TypedDimension    │                   │
    │                    │ (approved=false) erzeugen    ├──────────────────►│
    │                    │ RoyalLog + Audit             │                   │
```

### Schritt F — Digital-Twin-Divergenz und Kalibrierung

```text
QUESTOR          ARCHIVAR       KARTOGRAPH                 KANZLER          KÖNIGIN
   │                │               │                          │                │
   │ Sim-Paket      │               │                          │                │
   │ (SANDBOX)      │               │                          │                │
   ├───────────────►│ Sim-Kristall  │                          │                │
   │                ├──────────────►│ TwinDivergenceReport     │                │
   │ Real-Paket     │               │ berechnen (determinist.) │                │
   │ (NORMAL)       │               │ tolerance_breached=true? │                │
   ├───────────────►│ Real-Kristall │ calibration_required=true│                │
   │                ├──────────────►│ drift_score erhöhen      │                │
   │                │               ├─────────────────────────►│ URGENT-Briefing│
   │                │               │                          ├───────────────►│
   │                │               │                          │                │ Directive:
   │                │               │                          │                │ CALIBRATE_TWIN
   │                │               │                          │◄───────────────┤
   │                │               │                          │ Validierung    │
   │                │               │                          │ diagnostic_    │
   │                │               │                          │ weight ↑       │
   │                │               │                          ▼                │
   │                │               │          Vordenker → Kalibrierungs-       │
   │                │               │          hypothesen → DIAGNOSE-Paket      │
   │                │               │          (security_mode = SANDBOX)        │
   │◄──────────────────────────────────────────── Dispatch ─────┘                │
   │ Kalibrierungs-Kristall (COMPUTE_EVALUATION)                                │
   ├────────────────────────────────►│ Twin-Knoten aktualisieren:               │
   │                                 │ model_version ↑, drift_score ↓           │
   │                                 │ DiagnosticResolution(TWIN_CALIBRATED)    │
```

### Schritt G — Eskalation und menschlicher Override

```text
AUSLÖSER                          REAKTION
─────────────────────────────────────────────────────────────────────
2× VETO gegen Direktiven      ──► URGENT-Briefing + ESCALATED
ABORT_MISSION                 ──► immer ESCALATED (Mensch bestätigt)
SafetyConstraint-Konflikt     ──► SAFE_MODE möglich (nur Mensch)
Twin-Drift wiederholt         ──► Mensch entscheidet über Twin-Einsatz
LLM 3× Timeout in Folge       ──► deterministischer Fallback + Alert
                                  + Eskalation an Kanzler/Mensch

MENSCH kann jederzeit:
  • HUMAN_OVERRIDE: jede Direktive ersetzen
  • SAFE_MODE: Exploration stoppen, nur Diagnose/Audit
  • Manifest-Version erhöhen (einziger Weg, hard_constraints zu ändern)
  • ExplorationPolicy direkt setzen (überstimmt LLM-Königin, SR-11)
```

### Schritt H — Abschluss und Finalbericht

```text
KARTOGRAPH meldet Topic-StopCondition erfüllt
        │
        ▼
KANZLER: StrategicBriefing(FINAL)
        │  • alle Kristalle (aggregiert)
        │  • verworfene Hypothesen
        │  • Twin-Kalibrierungs-Historie
        ▼
KÖNIGIN (LLM): FinalScientificReport (Entwurf)
        │
        ▼
KANZLER: Validierung (keine Safety-Claims, keine Geheimnisse)
        │
        ▼
MENSCH: Review → human_reviewed = true
        │
        ▼
Topic → ARCHIVED, System wartet auf neue Mission
```

---

## §7 Sanitization und LLM-Schutz (Strategic Layer)

| Richtung | Betroffene Felder | Maßnahme |
|---|---|---|
| Eingang Königin | `mission_goal`, `DecisionOption.description`, Briefing-Freitext | Injection-Pattern-Scan (QUESTOR §12.3), XML-Escaping, Längenlimits |
| Ausgang Königin | `StrategicDirective.reason`, `parameters` | Schema-Validierung, Safety-Claim-Erkennung (QUESTOR §12.5), Constraint-Prüfung |
| Eingang Vordenker | Symptom-metrics, Topologie-Ausschnitt | nur kuratierte Felder, keine Blackbox-Inhalte |
| Ausgang Vordenker | `hypothesis_text`, `rationale` | Injection-Scan, Safety-Claim-Erkennung |
| Alle | `security_mode` | wird keinem strategischen LLM mitgeteilt (SR-29 analog) |
| Alle | Atlas-Hybrid-Referenzfelder | nicht LLM-whitelisted (QUESTOR §12.2a analog) |

**Fallback-Regel (SR-28 analog):** Jeder LLM-Fehler führt zu einem deterministischen Fallback: aktuelle `ExplorationPolicy` bleibt unverändert, Ereignis wird protokolliert, keine automatische Wiederholung mit erweitertem Kontext.

---

## §8 Autonomie- und Eskalationsmatrix

| Entscheidung | LLM-Königin darf | Kanzler darf | Nur Mensch darf |
|---|---|---|---|
| Exploration gewichten | vorschlagen | final umsetzen | überstimmen |
| Topic archivieren | vorschlagen | final umsetzen | überstimmen |
| Budget unter Threshold freigeben | vorschlagen | final umsetzen | überstimmen |
| Budget über Threshold freigeben | vorschlagen | eskalieren | final entscheiden |
| Neue nicht-physische Dimension | Hint geben | genehmigen | überstimmen |
| Neue physische Dimension | Hint geben | eskalieren | final genehmigen |
| Mission abbrechen | vorschlagen | eskalieren | final bestätigen |
| SafetyConstraint ändern/aufheben | ❌ niemals | ❌ ohne Autorisierung | ✅ (autorisierter Prozess) |
| Manifest-hard_constraints ändern | ❌ niemals | ❌ | ✅ (neue Manifest-Version) |
| Twin kalibrieren | anweisen (CALIBRATE_TWIN) | prüfen + umsetzen | überstimmen |

---

## §9 CHARTER-Konformitätsmatrix

| CHARTER-Regel | Umsetzung |
|---|---|
| SR-04 (Questor schreibt nie in Atlas/Archiv) | Unverändert. Alle neuen Verträge wirken nur auf Gremium-/Kanzler-Ebene. |
| SR-08 (Operational ≠ Scientific) | RoyalLog, Briefings und Direktiven sind operational; sie erzeugen keine Kristalle/Signale. |
| SR-10 (Fail-Closed) | Ungültige Direktive → VETO; unklarer DimensionRequest → REJECTED; LLM-Ausfall → Policy bleibt. |
| SR-11 (Mensch nie überstimmt) | Jede Direktive ist Vorschlag; Mensch kann jederzeit überstimmen; ABORT und physische Dimensions-Expansion zwingend menschlich bestätigt. |
| SR-13 (LLM nur Advisor) | Königin und Vordenker schlagen vor; Kanzler, Pre-Filter, Sicherheitsrat entscheiden deterministisch. |
| SR-24 (Whitelist) | StrategicBriefing hat definierte Whitelist-Felder; Freitext nur mit Scan. |
| SR-29 (security_mode geheim) | `security_mode` ist in keinem Briefing/Direktive/Hypothese erlaubt. |
| §2 Blackboard | Alle Kommunikation über Atlas/Archiv; keine direkten Rang-Aufrufe; SymptomEvents sind Blackboard-Artefakte. |
| §8 Hierarchie | Dieses Dokument widerspricht CHARTER/CONTRACTS nicht; Änderungen fließen als Änderungsanträge in CONTRACTS/GREMIUM. |

---

## §10 Verbotene Patterns (Strategic Layer)

1. Königin-LLM mit persistentem Gesprächsverlauf.
2. Freitext-Report als primärer LLM-Input (nur strukturierte Briefings).
3. LLM-Einsatz im Kanzler (auch keine LLM-Zusammenfassungen).
4. Direkter Schreibzugriff der Königin oder des Vordenkers auf Atlas/Archiv.
5. Direkte Kommunikation Königin ↔ Vordenker (nur über Kanzler/Blackboard).
6. Automatische Dimensions-Erzeugung ohne Kanzler-Prüfung.
7. `security_mode` oder Atlas-Hybrid-Referenzen im LLM-Kontext.
8. RoyalLog-Inhalte als wissenschaftliche Signale.
9. Sim-Kristalle, die physische Kristalle direkt bestätigen (nur über physische Validierung, gemäß DIGITAL-TWIN-SEM Regel 1).
10. CHARTER-Änderung als Voraussetzung dieses Änderungsantrags.

---

## §11 Erforderliche Dokument-Änderungen

| Dokument | Änderung |
|---|---|
| CONTRACTS.md | Neuer §6.11 „Strategic Layer" mit allen Verträgen aus §4; neue Enums: `BriefingType`, `DirectiveIntent`, `DirectiveStatus`, `DirectiveOutcome`, `SymptomType`, `HypothesisStatus`, `DimensionRequestStatus`, `RiskLevel`. DIGITAL-TWIN-SEM-1.0.0 bleibt unverändert integriert. |
| GREMIUM.md | Neue Pflichten für Kanzler (§3.3), Vordenker (§3.4), Kartograph (§3.2), Lotse (§3.6); neuer Abschnitt „Strategic Layer" mit Trigger-Tabelle und Validierungspipeline; neue Pipeline-Events: `BRIEFING_GENERATED`, `DIRECTIVE_ACCEPTED`, `DIRECTIVE_VETOED`, `DIMENSION_REQUEST_APPROVED`, `TWIN_DIVERGENCE_DETECTED`, `MISSION_ARCHIVED`. Zugriffsmatrix unverändert. |
| KOENIGIN.md (neu, specs/) | Constitutional Stateless Anchor Pattern, Briefing/Directive-Verträge, Fallback-Regeln, CHARTER-Konformität (SR-11, SR-13). |
| QUESTOR.md | Keine funktionalen Änderungen (Kompatibilitätsbestätigung analog HAL §0.1). |
| HAL.md | Keine Änderungen. |
| CHARTER.md | Keine Regeländerung; optionaler redaktioneller Hinweis in §1.1, dass Schicht 5 als Constitutional Stateless Pattern spezifiziert ist. |
| ROADMAP.md | Neue Phasen S1–S4 (§13). |
| VALIDATION.md | Neue Test-Suite STRAT (§14). |

---

## §12 Konfiguration: StrategicLayerConfig

```python
class StrategicLayerConfig(BaseModel):
    briefing_interval_cycles: int = 25          # PERIODIC-Rhythmus
    max_briefing_chars: int = 8192
    royal_log_anchor_depth: int = 3             # Anker-Tiefe
    directive_ttl_cycles_default: int = 10
    budget_unlock_threshold: float = 0.10       # Anteil Restbudget, darüber Mensch
    saturation_window_cycles: int = 10
    stagnation_budget_threshold: float = 0.80   # URGENT bei Zielverfehlung
    max_consecutive_llm_failures: int = 3       # dann Eskalation
    dimension_auto_approval_non_physical: bool = True
    twin_urgent_on_tolerance_breach: bool = True
    final_report_requires_human_review: bool = True
```

---

## §13 Roadmap-Ergänzung (Phasen S1–S4)

| Phase | Inhalt | Abhängigkeit | Dauer |
|---|---|---|---|
| S1 | Verträge & Enums in CONTRACTS §6.11, StrategicLayerConfig | A4 abgeschlossen | 2–3 Tage |
| S2 | Kanzler-Erweiterung: Briefing-Generator, Directive-Validator, RoyalLog | S1 | 3–4 Tage |
| S3 | KOENIGIN.md-Umsetzung: Stateless-Aufruf, Sanitization, Fallback | S2 | 3–4 Tage |
| S4 | Vordenker-Erweiterung: Symptom-Trigger, Topology-Prompting, DimensionOnboarding; Twin-Loop-Integration | S2, DIGITAL-TWIN-SEM umgesetzt | 4–5 Tage |
| S-INT | Integration & Regression (Suite STRAT) | S4, Atlas A5 | 3–5 Tage |

---

## §14 Akzeptanzkriterien und Tests (Suite STRAT)

1. Königin erzeugt niemals eine Direktive außerhalb des Intent-Enums.
2. Direktive mit `drop_constraints` auf hard_constraint → immer VETO.
3. `security_mode` erscheint in keinem LLM-Kontext (Negativ-Test).
4. LLM-Timeout → Policy unverändert, RoyalLog-Eintrag, kein Crash.
5. 2× VETO → URGENT-Briefing + Eskalation.
6. ABORT_MISSION → immer ESCALATED.
7. DimensionRequest physisch → immer ESCALATED an Mensch.
8. TWIN_DRIFT → URGENT-Briefing → CALIBRATE_TWIN-Pfad endet in `TWIN_CALIBRATED` (SANDBOX).
9. CapabilityGapSignal → Hypothese wird angepasst oder als DecisionOption eskaliert.
10. Blackboard-Verletzungstest: keine direkten Rang-Aufrufe nachweisbar.
11. Manifest-Versionierung: alte Direktiven referenzieren immer die zur Aufrufzeit gültige Manifest-Version.
12. ≥ 40 Unit-Tests, ≥ 15 Integrationstests, alle Fail-Closed-Pfade getestet.

---

## §15 Dokumentenhierarchie

Dieses Dokument ist ein Entwurf in `specs/` und referenziert:
- `foundation/CHARTER.md` (Sicherheitsregeln, SR-XX)
- `foundation/CONTRACTS.md` (Datenverträge, §6.10/§6.11)
- `specs/GREMIUM.md`, `specs/QUESTOR.md`, `specs/HAL.md`
- Änderungsantrag `DIGITAL-TWIN-SEM-1.0.0`

Regel: Nach Übernahme dieses Entwurfs in die Zieldokumente wird diese Datei als ARCHIVIERT markiert. Bei Widersprüchen gilt immer CHARTER > CONTRACTS > dieses Dokument.


---

### Kurze Einordnung meiner Designentscheidungen

1. **Basis ist das „Constitutional Stateless Institute"** (staatlose Königin + deterministischer Kanzler), weil es die CHARTER-konformste und drift-freieste Architektur ist.
2. **Ergänzt um die Governance-Schärfe aus Vergleich 3**: klare Eskalationsmatrix, Verbotsliste, Blackboard-Disziplin.
3. **Digital Twin ist jetzt voll integriert** — dein `DIGITAL-TWIN-SEM-1.0.0` liefert bereits `DIGITAL_TWIN`-Knoten und `TwinDivergenceReport`, daher habe ich den Kalibrierungs-Loop als Schritt F direkt eingebaut (statt ihn nur als Option zu führen).
4. **RoyalLog liegt beim Kanzler**, nicht beim Archivar: Der Kanzler führt laut GREMIUM §3.3 bereits das Audit-Log, damit bleibt das RoyalLog ein operatives Governance-Journal ohne Konflikt mit der wissenschaftlichen Rolle des Archivars.
5. **CHARTER bleibt unangetastet** — alle Neuerungen sind Änderungsanträge an CONTRACTS/GREMIUM plus eine neue `KOENIGIN.md`.

Wenn du möchtest, kann ich als Nächstes entweder (a) den konkreten Änderungstext für `CONTRACTS.md §6.11` als direkt einfügbaren Block ausformulieren oder (b) die neue `KOENIGIN.md` vollständig entwerfen.