# GREMIUM RULES — Mechanik, Validierung, Zustandsmaschinen

| Feld | Wert |
|------|------|
| **Dateiname** | `gremium_30_rules.md` |
| **Modul** | RULES |
| **Version** | 1.0.0 |
| **Status** | AKTIV |
| **Hängt ab von** | `gremium_10_core@1.x`, `gremium_20_contracts@1.1.1`, `gremium_40_control@2.1.1` |
| **Änderungsgrund** | Konsolidierung aus v0.2.0 §4,§7-§22 + v0.3.0 §1-§18; mechanische Einlösung des Achsen-Modells |
| **Change-Log** | 1.0.0: Initiale Konsolidierung; Achsen-Integration (ControlState-Lesen statt Direkt-Setzen); provisional-Regel (SL-BRF-9) |

---

## §0 Zweck und Geltung

Dieses Modul definiert die **Mechanik** des Gremiums: Validierungspipeline, DirectiveTranslationTable, Konfliktdetektor, Symptom-Trigger, Signal-Semantik, Manifest-Enforcement, Safety-Kette, Twin-Loop, Dimensions-Lebenszyklus, Briefing-Erzeugung, Sanitization, Budget, Zustandsmaschinen.

**Leitprinzipien:**
1. **Achsen-Integration:** Regeln lesen den `ControlState` (aus `40_control §3`, kanonisch in `20_contracts §3`) und verwenden die zustandsabhängigen Parameter. Sie setzen Achsen-Parameter **nicht** direkt (Single Ownership, K7-F-07 behoben).
2. **Single Source of Truth:** Alle Verträge kommen aus `20_contracts`. Dieses Modul definiert keine eigenen Verträge.
3. **Deterministisch:** Der Kanzler ist rein deterministisch (SL-GATE-1). Alle Regeln sind maschinell ausführbar, kein LLM.
4. **SL-DEP-Lint:** Jede referenzierte Regel/Vertrag muss in `20_contracts` oder diesem Modul definiert sein.

---

## §1 Konsistenz mit 20_contracts und 40_control

### §1.1 SL-DEP-LINT (Regel-Ebene)

Ein Build/Load schlägt fehl, wenn:
1. Eine Regel einen Vertrag referenziert, der nicht in `20_contracts` definiert ist.
2. Eine Regel einen Config-Parameter verwendet, der nicht in `StrategicLayerConfig` (`20_contracts §4`) existiert.
3. Eine Regel einen Achsen-Parameter **direkt setzt** statt ihn über den `ControlState` zu lesen (Single-Ownership-Verstoß).
4. Eine Regel einen Intent verwendet, der nicht im `DirectiveIntent`-Enum (`20_contracts §2.1`) existiert.

### §1.2 Achsen-Lese-Regel (zentral)

Alle Regeln, die Achsen-Parameter benötigen, lesen sie über den `ControlState`:

```
# Pseudocode für Achsen-Lesen
research_params = {
    "exploration_weight":        config.exploration_weight,        # RESEARCH-besetzt
    "exploitation_weight":       config.exploitation_weight,
    "require_atlas_grounding":   config.require_atlas_grounding,
    "replicate_divergence_check": config.replicate_divergence_check,
    "metric_tolerance_multiplier": config.metric_tolerance_multiplier,
    "replication_weight":        config.replication_weight,
    "min_confirmations":         config.min_confirmations,
}
# Die Werte in config werden vom ResearchAxis (40_control §4.1) zustandsabhängig gesetzt.
# Regeln lesen nur, sie schreiben nicht.
```

**K7-F-07 behoben:** `SL-DTT` setzt `exploration_weight` nicht mehr direkt. Die FrontierEngine liest den ResearchAxis-Zustand und verwendet `config.exploration_weight` (RESEARCH-besetzt).

---

## §2 Missions-Bootstrap (SL-BOOT-0..8)

Konsolidiert aus v0.2.0 §4 + v0.3.0 §3.

### §2.1 SL-BOOT-0: Manifest-Intake-Validierung (fail-closed)

Vor SL-BOOT-1-Annahme prüft der Kanzler:
- `created_by == MENSCH` und `approved_by == MENSCH`, sonst REJECT.
- `value` XOR `range` je Operator (SL-MAN-9-Matrix).
- Jeder `dimension_ref` referenziert eine in `initial_dimensions` deklarierte Dimension.
- Kategorische Constraints (`enforcement=EXCLUSION` mit `categories`) müssen `categories` nicht-leer enthalten.
- `valid_until` (falls gesetzt) liegt via TimeService in der Zukunft.
- **Kontext-Budget-Prüfung** (SL-BRF-8): `manifest_max_chars` wird beim Intake geprüft.
- Jeder Verstoß → REJECT mit begründetem Template; kein Bootstrap.

### §2.2 SL-MAN-9: Operator×Enforcement-Matrix

| enforcement | zulässige Bestückung | FrontierEngine-Auswertung |
|---|---|---|
| EXCLUSION | `categories` ODER (`operator` + `value`) | kategorial ∈/∉ bzw. numerischer Vergleich |
| SAFETY | `operator` + `value` | numerischer Vergleich, LOCK bei Verstoß |
| BOUNDS | `range` ODER (`operator` + `value`) | Intervall-Schnitt (SL-MAN-4) |

### §2.3 SL-BOOT-1..6 (Kaltstart)

```
SL-BOOT-1: Mensch erstellt ResearchManifest (approved_by = Mensch).
SL-BOOT-2: Kanzler erzeugt MissionBootstrap (Dimensionen, ObjectiveFamily, Topic PROPOSED, Budget).
SL-BOOT-2 erweitert: Fehlen lab_ambient_temp/humidity → Bootstrap blockiert (Schatten-Variablen-Check stets ausführbar).
SL-BOOT-2b: Initiale Zonen aus deterministischem Template des ObjectiveFamilySeed; leerer Atlas → avg_uncertainty_score = None.
SL-BOOT-3: Materialisierung der ManifestConstraints (EXCLUSION/SAFETY/BOUNDS).
SL-BOOT-4: BOOTSTRAP-Briefing mit DecisionOption-Templates.
SL-BOOT-5: Königin antwortet mit INITIAL_SWEEP → Topic PROPOSED→ACTIVE.
SL-BOOT-6: Kanzler emittiert SymptomEvent(INITIAL_SWEEP); Vordenker SEED-MODUS.
SL-BOOT-7: Template-Lücke → Paket zurückgestellt, G-1 ausgelöst.
```

### §2.4 SL-BOOT-8: Kaltstart-Deadlock-Schutz

Nach `bootstrap_retry_limit` (=3) invaliden oder ausbleibenden INITIAL_SWEEP-Antworten: `HumanEscalationRecord(TEMPLATE_GAP)` + DecisionOptions. Topic bleibt PROPOSED; kein stilles Hängen.

---

## §3 Validierungspipeline v2 (10 Stufen)

Konsolidiert aus v0.3.0 §11. Feste Reihenfolge:

```
StrategicDirective (LLM-Output)
 ├─ 1.  Schema (Pydantic + Intent-Submodelle, discriminierte Union SL-DIR-9)
 │      FAIL → VETO("SCHEMA_INVALID")
 ├─ 2.  briefing_ref-Existenz (SL-DIR-2)
 │      FAIL → VETO("REF_NOT_FOUND")
 ├─ 3.  Manifest-Prüfung (+ Seed-Feasibility SL-DTT-2)
 │      FAIL → VETO("MANIFEST_VIOLATION")
 ├─ 3b. Weisungs-Prüfung (aktive HumanDirective, §13.3)
 │      FAIL → VETO("HUMAN_DIRECTIVE_VIOLATION")
 ├─ 3c. Target-Existenz & Zustandsmatrix (Existenzindex;
 │      LOCKED/QUARANTINED/ARCHIVED je Intent)
 │      FAIL → VETO("TARGET_LOCKED"/"TARGET_TERMINAL")
 ├─ 4.  Safety-/Injection-Prüfung (rekursiv, Wortlisten SL-SAN-5)
 │      FAIL → VETO + Audit
 ├─ 5.  Budget-Prüfung (inkl. reserved-Simulation)
 │      FAIL → VETO("BUDGET_NEGATIVE")
 ├─ 6.  Intent-Sonderregeln (alle Intents, SL-DTT §4)
 ├─ 6b. Mode-Prüfung (ControlState-Achsen, §3.1)
 │      FAIL → VETO("MODE_VIOLATION")
 ├─ 6c. Semantische Dedup (semantic_directive_id, §5.2)
 │      FAIL → VETO("DUPLICATE_SEMANTIC")
 ├─ 7.  Konflikt-Modus-Prüfung (§5.1)
 │      FAIL → VETO("CONFLICT_MODE")
 └─ 8.  ACCEPT → DirectiveTranslationTable (§4)
```

### §3.1 Schritt 6b: Mode-Prüfung via ControlState (Achsen-Integration)

Die Mode-Prüfung liest den `ControlState` und wendet die Intent-Verfügbarkeit aus `40_control §5` an:

```
verfügbare_Intents = alle_Intents
                     − safety_intent_blocklist     (aus SafetyAxis)
                     − resource_intent_blocklist   (aus ResourceAxis)
                     − governance_intent_blocklist (aus GovernanceAxis)
                     − research_intent_blocklist   (aus ResearchAxis)

WENN directive.intent ∉ verfügbare_Intents:
    → VETO("MODE_VIOLATION")
```

**Beispiel:** `UNLOCK_BUDGET` ist nur verfügbar, wenn `resource == BUDGET_EXHAUSTED` (40_control §5.1). In jedem anderen ResourceAxis-Zustand → MODE_VIOLATION.

---

## §4 DirectiveTranslationTable (SL-DTT) mit Achsen-Integration

Konsolidiert aus v0.2.0 §6.4 + v0.3.0 §4. Deterministische Übersetzung; kein Interpretationsspielraum.

| Intent | Pflicht-Parameter | Deterministische Wirkung |
|---|---|---|
| NO_ACTION | — | keine Policy-Änderung; Zyklus protokolliert |
| INITIAL_SWEEP | `grid_spec`, `sweep_template_ref` | Topic PROPOSED→ACTIVE, Seed-Symptom (SL-BOOT-6). **Setzt NICHT exploration_weight direkt** — der ResearchAxis besitzt es (K7-F-07 behoben). |
| PIVOT_DOMAIN / PIVOT_TARGET | `from_topic_ref`, `to_topic_seed` | Scope-Check (SL-DIR-8), Feasibility (SL-DTT-2), Loop-Erkennung (SL-DTT-3); altes Topic → ARCHIVED nach Lessons-Learned-Transfer; neues Topic PROPOSED |
| UNLOCK_BUDGET | `amount_cycles`, `purpose` | immer HumanEscalationRecord(BUDGET); bei Bestätigung: `reserved_cycles → used_cycles` (SL-BUD-3) |
| ABORT_MISSION | `reason` | immer ESCALATED; nur mit menschlicher Bestätigung |
| ADD_DIMENSION_HINT | `source_ref`, `dimension_seed` | erzeugt prüfpflichtigen DimensionOnboardingRequest |
| INCREASE_DIAGNOSTIC | `zone_ref`, `amount` | `diagnostic_budget` der Zone += amount (max. `diagnostic_budget_max`) |
| CALIBRATE_TWIN | `twin_ref` | VETO wenn Twin nicht gedriftet (NO_DRIFT); sonst diagnostic_weight + Kalibrierungs-Commitment |
| ARCHIVE_TOPIC | `topic_ref` | Topic → ARCHIVED nach Lessons-Learned-Transfer |
| SET_PRIORITY | `topic_ref`, `priority` | Topic.priority setzen; `valid_for_cycles` möglich |
| DROP_SOFT_PREFERENCE | `preference_ref` | soft_preference deaktivieren (auditiert) |
| HUMAN_ESCALATION | `question`, `escalation_category` | HumanEscalationRecord mit Typ aus category (SL-ESC-6) |
| SET_RESEARCH_PHASE | `target_phase`, `reason` | **Achsen-Transition:** löst ResearchAxis-Wechsel aus (40_control §5.2); Validierung prüft Ziel-ControlState-Gültigkeit |

### §4.1 SL-DTT-1 (GEÄNDERT): TopicConstraintProposal statt harter ExclusionConstraints

Der Kanzler erzeugt aus gescheiterten Regionen topic-lokale weiche Filter (`TopicConstraintProposal`, Vertrag in `20_contracts §6`). Die FrontierEngine behandelt sie nur innerhalb des neuen Topics wie hart. Aufstieg zu hart nur über neue menschliche Manifest-Version (SL-MAN-1 gewahrt).

### §4.2 SL-BRF-9: provisional-Markierung (K7N-F-01 behoben)

```
WENN strategic_directive.briefing_ref → briefing.truncation_applied == true:
    royal_log_entry.provisional = true
SONST:
    royal_log_entry.provisional = false
```

Das Feld `provisional` wird in `RoyalLogEntry.provisional` (`20_contracts §9`) persistiert. Es ist ein DTT-Ausgabe-/Audit-Feld, kein Feld der Königin-Direktive.

---

## §5 Konfliktdetektor & NO_ACTION (SL-CON, SL-NOACT)

### §5.1 SL-CON-1..4: Konfliktdetektor

- **SL-CON-1:** Jeder GOVERNANCE-VETO gegen eine Königin-Direktive zählt als Konflikt (BENIGN-VETOs zählen nicht, SL-CON-4).
- **SL-CON-2:** 2 Konflikte innerhalb von `conflict_window_cycles` (=10) → menschlicher Fallback: URGENT-Briefing + HumanEscalationRecord(DEADLOCK); Königin erzeugt nur noch NO_ACTION.
- **SL-CON-3 (Mechanischer Konflikt-Modus):** Im Konflikt-Modus werden nur NO_ACTION/HUMAN_ESCALATION angenommen; alle übrigen Intents → VETO("CONFLICT_MODE"), das nicht als neuer Konflikt zählt.
- **SL-CON-4 (VETO-Schwere-Klassen):**
  - BENIGN: `NO_DRIFT`, `TARGET_LOCKED`, `SCHEMA_INVALID` (einzelne), `DUPLICATE_SEMANTIC`.
  - GOVERNANCE: `MANIFEST_VIOLATION`, `HUMAN_DIRECTIVE_VIOLATION`, Safety-/Injection-VETOs.

### §5.2 SL-INT-5: Semantische Dedup

`semantic_directive_id = sha256(intent + target_ref + canonical_json(parameters))` (ohne briefing_ref). Wiederholung mit gleichem Outcome innerhalb der letzten `semantic_dedup_window_cycles` → VETO("DUPLICATE_SEMANTIC"), ausgenommen NO_ACTION. RoyalLog führt `semantic_directive_id` mit.

### §5.3 SL-NOACT-1..2: NO_ACTION-Überwachung (Achsen-Integration)

```
# SL-NOACT-1 (GEÄNDERT): liest governance.stall_detection_active
WENN governance.stall_detection_active == false:
    → Stall-Counter wird NICHT erhöht (KV2-14 behoben)
WENN governance.stall_detection_active == true:
    no_action_stall_limit aufeinanderfolgende NO_ACTION ohne Atlas-Fortschritt
    → URGENT-Briefing "Strategischer Stillstand"
    → Stall-Counter wird nach URGENT-Zustellung zurückgesetzt

# SL-NOACT-2: Während HOLD/SAFE (governance=AWAITING_HUMAN oder safety=SAFE_MODE)
# ist die Stall-Überwachung suspendiert. Kein Eskalations-Sturm.
```

---

## §6 Symptom-Trigger und Vordenker

Konsolidiert aus v0.2.0 §8.

### §6.1 Trigger-Tabelle

| Symptom | Deterministische Bedingung | Vordenker-Aktion |
|---|---|---|
| INITIAL_SWEEP | Bootstrap (SL-BOOT-6) | Seed-Modus, Sweep-Strategie |
| WEISSRAUM | Zone gemäß SL-DEF-2 | Void-Prompting |
| FRACTURE_GAP | `fracture_score ≥ quarantine_threshold` | Fracture-Prompting, ggf. DimensionOnboardingRequest |
| SATURATION | Topic-StopCondition SATURATION_CYCLES (einzige Quelle, SL-SIG-3) | Paradigma-Wechsel |
| BRIDGE_OPP | Cluster-übergreifende Kanten ≥ `bridge_edge_threshold` | Bridge-Prompting |
| TWIN_DRIFT | `TwinDivergenceReport.tolerance_breached == true` | Twin-Calibration-Prompting inkl. Schatten-Variablen-Check |
| CAPABILITY_GAP_FEEDBACK | CapabilityGapSignal eingegangen | Hypothese an Capabilities anpassen |
| DIMENSION_GAP | Idee wegen approved=false-Dimension blockiert | alternative Hypothese |
| REPLICATE_DIVERGENCE | SL-SIG-5 (parameter-äquivalent, Diff > Tolerance) | Replikations-Hypothese |
| QUARANTINE_BLOCK | Idee in quarantinierter Zone blockiert | Diagnose-Hypothese |

### §6.2 SL-URG-1..3: URGENT-Trigger

URGENT-Briefings bei: `fracture_score ≥ full_rebuild_threshold`, `tolerance_breached`, Topic SATURATED ohne Ziel bei Budget > `stagnation_budget_threshold`, LOCKED-Zone ohne Diagnose-Strategie, Konflikt (SL-CON-2), CapabilityGap mit `requires_budget_or_hardware`, SAFETY-Ereignis, Manifest-Sprung, NO_ACTION-Stall, Quarantäne-Timeout, `questor_health_status == DEAD`, `remaining_cycles ≤ budget_unlock_threshold_fraction`, Mission ohne aktives Topic.

**SL-URG-3:** URGENT-Nachzügler während Cooldown werden ins nächste PERIODIC gemerged; kein stiller Verlust.

### §6.3 SL-SYM-1: SymptomEvent-Verlustschutz

SymptomEvents werden vor der Queue-Übergabe persistent abgelegt. Bei High-Watermark der Vordenker-Queue wird das Event zurückgestellt und erneut zugestellt (At-Least-Once mit Event-ID-Dedup).

---

## §7 Signal-Semantik (SL-SIG, SL-HYP)

Konsolidiert aus v0.2.0 §9 + v0.3.0 §7.

### §7.1 SL-SIG-1: Korrigierter Fallback

```
WENN expectation_ref vorhanden:
    confirms_expectation == False → 🟨 CONTRADICTION (REFUTES)
    confirms_expectation == True  → 🟩 (≥0.8) bzw. ⬜ (<0.8)
    confirms_expectation == None  → ⬜ EXPLORATORY_COVERAGE
WENN keine Erwartung UND ziel_erreicht == True:
    konfidenz ≥ 0.8 → 🟩 CONFIRMATION
    konfidenz ≥ 0.5 → ⬜ EXPLORATORY_COVERAGE
WENN keine Erwartung UND ziel_erreicht == False:
    → ⬜ EXPLORATORY_COVERAGE mit evidence_kind = NEGATIVE_KNOWLEDGE
```

### §7.2 SL-HYP-4: Erwartungs-Brücke (Achsen-Integration)

Bestätigende Hypothesen müssen einen `ExpectationSpec` tragen (Vertrag in `20_contracts §10`). Der Quartiermeister übersetzt ihn in `expectation_ref`. Fehlt der Spec, läuft das Paket als EXPLORATION.

**Achsen-Integration:** Die `require_atlas_grounding`-Prüfung (atlas_refs leer nur bei INITIAL_SWEEP) liest `config.require_atlas_grounding` (RESEARCH-besetzt). In BOOTSTRAP/EXPLORATION ist De-novo erlaubt (KV2-08 behoben).

### §7.3 Weitere Semantik-Regeln

- **SL-SIG-2:** OPERATIONALE Paketfehler fließen nie in wissenschaftliche Metriken.
- **SL-SIG-3:** Sättigung hat genau eine Quelle (Topic-StopCondition SATURATION_CYCLES).
- **SL-SIG-4:** ObjectiveFamily-Constraints (MetricConstraint) werden binär gegatet.
- **SL-SIG-5:** Erwartungsunabhängige Replikat-Divergenz → REPLICATE_DIVERGENCE (nur wenn `config.replicate_divergence_check == true`, RESEARCH-besetzt).
- **SL-SIG-6:** Operativer Fehler auf integrity_dim → `validity=COMPROMISED`.
- **SL-SIG-7:** Constraint-Verletzung ohne Erwartung → ⬜ CONSTRAINT_NEAR_MISS.
- **SL-SIG-8:** `negative_knowledge_decay` für erfolglos abgedeckte Regionen.

---

## §8 Manifest-Enforcement (SL-MAN)

### §8.1 Schutzkette

```
ResearchManifest.hard_constraints
    │ SL-BOOT-3: Materialisierung
    ▼
ExclusionConstraint / SafetyConstraint im Atlas
    ├─ FrontierEngine-Hartfilter Nr. 10
    ├─ Pre-Filter
    ├─ Quartiermeister SL-MAN-4: parameter_bounds ∩ Manifest-Constraints
    └─ PolicyEvaluator Prüfung 9: Manifest-Constraint-Check
```

### §8.2 SL-MAN-7: Semantische Umgehungsabwehr

Die Königin kann Constraints nicht durch Umdeutung umgehen. Neue kategorische Werte nicht in `ManifestConstraint.categories` → Constraint-Verstoß.

---

## §9 Safety-Reaktionskette (SL-SAF, Quarantäne)

Konsolidiert aus v0.2.0 §11 + v0.3.0 §5.

### §9.1 SL-SAF-1..4: ESTOP-Kette

```
HAL meldet ESTOP (SAFETY)
  → Questor: SAFETY-Abbruch (SR-19)
  → Archivar: SAFETY-Governance-Ereignis
  → KANZLER (ereignisgesteuert, SOFORT):
      a) Zone → LOCKED
      b) SafetyConstraint-Vorschlag (active=provisional, SL-SAF-6)
      c) URGENT-Briefing
      d) HumanEscalationRecord(SAFETY_EVENT)
      e) Achsen-Transition: safety → ESTOP_LOCKED (40_control §2.1)
```

### §9.2 SL-SAF-5: Entsperrpfad

LOCKED-Zonen werden ausschließlich über strukturierte `HumanResponseFile.unlock_decision` entsperrt. Zustandsfolge: LOCKED → DIAGNOSTIC_ONLY → RELEASED.

### §9.3 §13.6 Quarantäne

Zustandsmaschine: ENTRY → DIAGNOSTIC_ALLOWED → QUARANTINE_EXIT → {RESUME, CLOSE}. Diagnostik erlaubt und budgetiert. Quarantäne-blockierte Ideen emittieren QUARANTINE_BLOCK. Exit nur über strukturierte QUARANTINE_EXIT-Antwort. Deterministische Sicherheitsrelevanz-Regel: Fracture ist sicherheitsrelevant genau dann, wenn seine Zone eine SafetyConstraint- oder SAFETY-Enforcement-Dimension schneidet.

---

## §10 Digital-Twin-Loop (SL-TWIN)

Konsolidiert aus v0.2.0 §12 + v0.3.0 §6.

- **SL-TWIN-1:** Paarung mit Parameter-Äquivalenz.
- **SL-TWIN-2:** ε und Toleranz-Defaults (`dev_metric = max(Relativterm, Absolutterm)`; für real ≈ 0 gilt Absolutterm).
- **SL-TWIN-3:** Twin-Validitätsprüfung (PolicyEvaluator Prüfung 10).
- **SL-TWIN-4:** Gate × Security-Mode-Matrix (physisches Kalibrierungs-Paket konstruktionsunmöglich).
- **SL-TWIN-5:** Schatten-Variablen-Check.
- **SL-TWIN-6..7:** Deduplizierung via blocked_cache; SANDBOX-Kalibrierung bleibt erlaubt.
- **SL-TWIN-8:** Konfidenz-Kalibrierung des Vordenkers.
- **SL-TWIN-9:** Kalibrierungs-Abbruchbedingung (nach 3 Versuchen ohne Drift-Reduktion → SUSPENDED + Eskalation).
- **SL-TWIN-10:** In-flight bei Drift (`twin_invalidated=true`).
- **SL-TWIN-11:** Late-Pairing.

---

## §11 Dimensions-Lebenszyklus (SL-DIM)

Konsolidiert aus v0.2.0 §13 + v0.3.0 §15.

- **SL-DIM-1..4:** Kanzler-Prüfung (Plausibilität, Range-Validierung, Cooldown, physische Auswirkung).
- **SL-DIM-5:** Deadlock-Freiheit (DIMENSION_GAP-Symptom statt stillem Verwerfen).
- **SL-DIM-6..7:** Genehmigung und Backfill.
- **SL-DIM-8:** Abgeleitete Dimensionen (parent_dimension).
- **SL-DIM-9:** Neue Kategoriewerte → CATEGORY_EXTENSION-Request.
- **SL-DIM-10:** Normatives Kriterium für requires_physical_actuation.
- **SL-DIM-11:** Lebenszeit-Limit `max_dimension_requests_per_topic_total`.
- **SL-DIM-12:** Request-Outcomes im Briefing.
- **SL-DIM-13:** Range-Korrekturen als Feedback-Symptom.

---

## §12 Capability-Gap & CAPEX (SL-ESC-7)

```
VORDENKER: ScientificHypothesis mit required_capabilities
    ▼
LOTSE prüft gegen Capability-Registry
    ├─ erfüllt → Wegmarke
    └─ unerfüllbar → CapabilityGapSignal
           ├─ blocked_cache-Eintrag CAPABILITY_GAP
           ├─ nach capability_gap_repeat_limit Wiederholungen:
           │  DecisionOption an Königin
           │  (bei requires_budget_or_hardware → CAPEX-Eskalation)
           └─ SL-ESC-7: CAPEX-Wartezeit → HumanEscalationRecord(CAPABILITY_DELIVERY)
              mit strukturiertem Lieferdatum; blocked_cache-Clearing-Pfad
              → Achsen-Transition: resource → PHYSICAL_WAIT (40_control §2.2)
```

---

## §13 Mensch-Schnittstelle (SL-ESC)

Konsolidiert aus v0.2.0 §15 + v0.3.0 §1.

### §13.1 SL-ESC-1..4: Eskalationskanal

Speicherort `data/archiv/operational/escalations/`; Antworten in `data/human_inbox/`. Unbeantwortete Eskalation → nach `timeout_cycles` → governance → AWAITING_HUMAN (Achsen-Transition). Erinnerungen alle `escalation_reminder_interval_cycles` (max. `escalation_reminder_cap`).

### §13.2 SL-ESC-5: HumanResponseFile-Validierung

Antwortdateien müssen gegen das Schema (`20_contracts §9`) validieren. Unparsbare Datei → PARSE_REJECTED + Erinnerungs-Template. Teilgenehmigung über `decision=PARTIAL`.

### §13.3 Schritt 3b: Weisungs-Prüfung (HumanDirective)

Aktive HumanDirective-Einträge werden gegen `target_ref`/`parameters` der Direktive geprüft. Verstoß → VETO("HUMAN_DIRECTIVE_VIOLATION").

### §13.4 SL-ESC-6: EscalationType-Erweiterung + Dedup

`HUMAN_ESCALATION` erhält Pflicht-Parameter `escalation_category`. Eskalations-Dedup über `(escalation_type, target_ref)` (target_ref in `HumanEscalationRecord.target_ref`, K7-F-16 behoben).

---

## §14 Briefing-Erzeugung (SL-BRF)

Konsolidiert aus v0.2.0 §6.2, §16 + v0.3.0 §13.

### §14.1 Erzeugungs-Pipeline

```
ATLAS → KANZLER:
  1. Aggregieren → AtlasMacroState
  2. MissionBudget → BudgetState
  3. Topics → TopicSummary[]
  4. Fractures → FractureSummary[]
  5. Twin-Status → TwinStatusSummary[]
  6. HAL-Slot-Zustände → HardwareHealth
  7. In-flight-Pakete → InFlightPackageSummary[] (SL-PKG-1)
  8. Aktive Hypothesen → active_hypothesis_refs (Top-N, SL-BRF-10)
  9. DecisionOption[]
 10. Anchor: HUMAN_OVERRIDE zuerst, dann letzte N Direktiven
 11. Sanitization (SL-BRF-1..6)
 12. Trunkierung nach SL-BRF-4 (Priorität v2)
 13. StrategicBriefing schreiben (ohne zyklus_id, SL-DEF-4)
```

### §14.2 SL-BRF-8: Gesamt-Kontext-Budget

`max_total_context_chars = manifest_max_chars + max_briefing_chars + anchor_max_chars`. Layer 1 beim Intake (SL-BOOT-0); Layer 3 (Anchor) wird nie trunkiert.

### §14.3 SL-BRF-4: Trunkierungspriorität v2

URGENT-Auslöser + SAFETY > LOCKED/CRITICAL/QUARANTINE + drifted Twins + pending_escalations + decisions_required > höchste Fractures > aktive Topics > Rest. Twins mit calibration_required oder drift_score > 0 fallen nie in die Restklasse.

---

## §15 Sanitization (SL-SAN, SL-RPT)

Konsolidiert aus v0.2.0 §17 + v0.3.0 §12.

- **SL-SAN-0:** First-Order-Scan aller LLM-Outputs vor Persistenz. Treffer → Quarantäne + Audit + einmalige Neu-Generierung, danach Eskalation.
- **SL-SAN-1:** Archivar-Eingangssanitization (INJ-01..15, XML-Escaping, Längenlimits).
- **SL-SAN-2:** Second-Order-Scan (re-scan beim Wiedereinspeisen).
- **SL-SAN-3..4:** Direktiven- und Report-Validierung.
- **SL-SAN-5:** INJ-01..15 und Safety-Claim-Katalog als normativer Anhang.
- **SL-SAN-6:** Roh-Ergebnis-Trennung (observation_raw / interpretation).
- **SL-RPT-1:** Zitiermuster-Entfernung über Regex-Katalog; nicht erfassbare Fälle als review_required.

---

## §16 Abschluss und Archivierung (SL-RPT)

```
StopCondition REACHED → Topic SATURATED → FINAL-Briefing
  → Kanzler injiziert ReportFacts (deterministisch)
  → Königin-LLM: NUR executive_summary + future_recommendations
  → Kanzler: Sanitization + Zitierungs-Check
  → Mensch: human_reviewed = true → ARCHIVED → Cold Storage
```

Unreviewed-Reminder alle `review_reminder_interval_cycles`. Nach `review_grace_max_cycles` finale Eskalation. Nach `cold_storage_window_days` mit human_reviewed=true → Cold Storage.

---

## §17 Replikation (SL-REP)

- **SL-REP-1:** FrontierType um REPLICATE erweitert.
- **SL-REP-2:** REPLICATE-Frontiers bei `crystallization_progress ≥ replication_trigger_progress` und Bestätigungen < `min_confirmations` (RESEARCH-besetzt).
- **SL-REP-3:** FrontierEngine gewichtet REPLICATE mit `replication_weight` (RESEARCH-besetzt).
- **SL-REP-4:** Quotenregel: ≥ 1 Replikation pro `replication_cadence_cycles`.
- **SL-REP-5:** Fracture-getriebene Replikation (FRACTURE_GAP mit ≥ 2 divergenten Kristallen → REPLICATE-DecisionOption).

---

## §18 Datenintegrität (SL-INT)

- **SL-INT-1:** NaN/Infinity → Kristall verworfen, gültige Geschwister bleiben (v0.3.0 §17). Gilt auch für SymptomEvent.metrics_snapshot.
- **SL-INT-2:** Sequenzlücken → akzeptiert + Audit-Flag + Reconciliation (Owner, Timeout, Abschlusszustand).
- **SL-INT-3:** Referentielle Integrität (briefing_ref, source_ref, twin_divergence_report_ref).
- **SL-INT-4:** Idempotenz (directive_id gemäß SL-DIR-1).
- **SL-INT-5:** Semantische Dedup (§5.2).
- **SL-INT-6:** Registry-Index-Dateien je Verzeichnis.

---

## §19 Zyklus-, Zeit- und Budgetmodell (SL-DEF, SL-BUD, SL-URG)

Konsolidiert aus v0.3.0 §2.

### §19.1 SL-DEF-3..5: Zwei Zyklusbegriffe + TimeService

- **SL-DEF-3 Pipeline-Takt:** ereignisgetrieben.
- **SL-DEF-4 Strategie-Zyklus:** Briefing-Regelkreis; `briefing_id` ist die einzige Zyklen-ID (zyklus_id abgeschafft).
- **SL-DEF-5:** Alle `*_days` nutzen TimeService; alle `*_cycles` nutzen Strategie-Zyklus. Keine Vermischung.

### §19.2 SL-BUD-1..4: Budget (Achsen-Integration)

```
# SL-BUD-1 (GEÄNDERT): liest resource.burn_rate_multiplier
used_cycles += 1 × resource.burn_rate_multiplier
# In PHYSICAL_WAIT/BUDGET_EXHAUSTED ist burn_rate_multiplier = 0 → Budget brennt nicht (KV2-01 behoben)

# SL-BUD-2: remaining_cycles = total_cycles − used_cycles − reserved_cycles
# SL-BUD-3: Bei UNLOCK_BUDGET-Bestätigung: reserved_cycles → used_cycles
# SL-BUD-4: burn_rate_per_cycle und estimated_completion_cycle mit Formeln
```

### §19.3 SL-URG-2: BUDGET_EXHAUSTED

Fällt `remaining_cycles ≤ 0` oder unter `budget_unlock_threshold_fraction`: URGENT-Briefing + HumanEscalationRecord(BUDGET) + DecisionOption. Achsen-Transition: resource → BUDGET_EXHAUSTED, governance → AWAITING_HUMAN.

---

## §20 Zustandsmaschinen (Topic, Dimension, Eskalation, Achsen)

### §20.1 Topic-Zustandsmaschine (§21.6)

```
PROPOSED → ACTIVE → {SATURATED, ABORTED} → ARCHIVED
```
Alle Übergänge vom Kanzler. Lessons-Learned-Transfer bei jedem ACTIVE-Abschluss.

### §20.2 DimensionOnboardingRequest

```
PROPOSED → APPROVED | REJECTED | ESCALATED | COOLDOWN
ESCALATED → APPROVED (Mensch) | REJECTED (Mensch)
APPROVED → TypedDimension(approved=false)
```

### §20.3 Eskalation

```
PENDING → ANSWERED | TIMED_OUT
TIMED_OUT → governance=AWAITING_HUMAN (+ Erinnerungen)
ANSWERED → Umsetzung → RoyalLog
```

### §20.4 SystemMode → Achsen (v0.3.0 §9 Auflösung)

```
NORMALBETRIEB ⇄ SAFE_MODE (nur Mensch)  → safety=SAFE_MODE
NORMALBETRIEB ⇄ HOLD_STRATEGY (Timeout)  → governance=AWAITING_HUMAN
```
**Wichtig:** SystemMode wird nicht als parallele Maschine geführt. SAFE → SafetyAxis, HOLD → GovernanceAxis. HOLD-Whitelist `{NO_ACTION, HUMAN_ESCALATION, CALIBRATE_TWIN (SANDBOX), INCREASE_DIAGNOSTIC}` wird über die Achsen-Intent-Verfügbarkeit (40_control §5) abgebildet.

---

## §21 Autonomie- und Eskalationsmatrix

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

---

## §22 CHARTER-Konformitätsmatrix

| CHARTER-Regel | Umsetzung |
|---|---|
| SR-04 | Questor/HAL unverändert; strategische Verträge nur auf Gremium-Ebene |
| SR-08 | RoyalLog/Briefings/Direktiven operational; HardwareHealth verzerrt keine wissenschaftlichen Metriken (SL-SIG-2) |
| SR-10 | Ungültige Direktive → VETO; unklarer DimensionRequest → REJECTED; LLM-Ausfall → Policy bleibt; NaN → Verwurf |
| SR-11 | Mensch wird nie überstimmt; ABORT, physische Dimensionen, CAPEX, Manifest immer menschlich |
| SR-13 | Königin/Vordenker schlagen vor; Kanzler, Pre-Filter, Gate entscheiden deterministisch |
| SR-14 | NaN-Fail-Closed auf Schicht 4 (SL-INT-1) |
| SR-24 | Briefing-Whitelist; Fortschritt als Skalare |
| SR-29 | security_mode in keinem strategischen Artefakt |
| SR-05 | ESTOP-Reset im Intent-Enum nicht ausdrückbar (SL-SAF-4) |
| §2 Blackboard | Alle Kommunikation über definierte Speicherorte; keine direkten Rang-Aufrufe |

---

## §23 Verbotene Patterns (Strategic Layer)

1. Königin-LLM mit persistentem Gesprächsverlauf.
2. Freitext-Report als primärer LLM-Input (nur strukturierte Briefings).
3. LLM-Einsatz im Kanzler (auch keine LLM-Zusammenfassungen).
4. Direkter Atlas-/Archiv-Zugriff der Königin.
5. Direkte Kommunikation Königin ↔ Vordenker.
6. Automatische Dimensions-Erzeugung ohne Kanzler-Prüfung.
7. `security_mode` oder Atlas-Hybrid-Referenzen im LLM-Kontext.
8. RoyalLog-Inhalte als wissenschaftliche Signale.
9. Sim-Evidenz, die physische Kristalle direkt bestätigt.
10. Physische Kalibrierungs-Pakete (SL-TWIN-4).
11. Explorations-Fehlschläge als 🟨 CONTRADICTION (SL-SIG-1).
12. Weiterlauf mit offener Eskalation nach Timeout (governance=AWAITING_HUMAN stattdessen).
13. CHARTER-Änderung als Voraussetzung dieses Moduls.
14. **Achsen-Parameter direkt setzen** statt über ControlState lesen (Single Ownership).

---

## §24 Akzeptanzkriterien und Tests (Suite STRAT-01..45)

Konsolidiert aus v0.2.0 §28.1 (STRAT-01..25) + v0.3.0 §19 (STRAT-26..45). Zusätzlich achsen-spezifische Tests:

| ID | Test | Erwartung |
|---|---|---|
| STRAT-01..25 | (v0.2.0 §28.1, unverändert) | — |
| STRAT-26 | Direktive verstößt gegen aktive HumanDirective | VETO(HUMAN_DIRECTIVE_VIOLATION) |
| STRAT-27 | Semantisches Direktiven-Duplikat über Briefing-Grenze | VETO(DUPLICATE_SEMANTIC) |
| STRAT-28 | Manifest mit approved_by ≠ MENSCH | Bootstrap-REJECT |
| STRAT-29 | Twin-Deviation bei real ≈ 0 | kein Fehlalarm (Absolutterm) |
| STRAT-30 | Sim/Real-Paarung mit verschiedenen Parametern | Paarung abgelehnt |
| STRAT-31 | 3 Kalibrierungen ohne Drift-Reduktion | Twin SUSPENDED + Eskalation |
| STRAT-32 | REPLICATE-Quote bei vorhandenem Kandidaten | ≥ 1 Replikation pro Kadenz |
| STRAT-33 | SET_PRIORITY während HOLD (governance=AWAITING_HUMAN) | VETO(MODE_VIOLATION) |
| STRAT-34 | 4× NO_ACTION während HOLD | kein Stall-URGENT |
| STRAT-35 | Manifest-Sprung mit in-flight-Paket | Retro-Tag + DecisionOption |
| STRAT-36 | ABORT_MISSION bestätigt | Dispatch-Stopp, ABORT_REPORT |
| STRAT-37 | Budgeterschöpfung | BUDGET_EXHAUSTED + Eskalation |
| STRAT-38 | 2 BENIGN-VETOs in 10 Zyklen | kein Menschen-Fallback |
| STRAT-39 | Pivot in fremde ObjectiveFamily | VETO(SCOPE_VIOLATION) |
| STRAT-40 | Lessons-Learned-Vorschläge | topic-lokal, nie Manifest |
| STRAT-41 | Diagnostik in quarantinierter Zone | erlaubt, budgetiert |
| STRAT-42 | Zonen-Entsperrung | nur strukturierte HumanResponseFile |
| STRAT-43 | Layer 1+2+3 > Gesamtbudget | Intake-/Trunkierungsregeln greifen |
| STRAT-44 | Injection in Vordenker-Hypothese bei Erstpersistenz | First-Order-Scan + Quarantäne |
| STRAT-45 | Replikat-Divergenz ohne Erwartung | REPLICATE_DIVERGENCE-Symptom |
| **STRAT-46** | **UNLOCK_BUDGET bei resource=FUNDED** | **VETO(MODE_VIOLATION)** |
| **STRAT-47** | **UNLOCK_BUDGET bei resource=BUDGET_EXHAUSTED** | **Intent verfügbar** |
| **STRAT-48** | **De-novo-Hypothese (atlas_refs=[]) in EXPLORATION** | **akzeptiert (require_atlas_grounding=false)** |
| **STRAT-49** | **De-novo-Hypothese in EXPLOITATION** | **verworfen (require_atlas_grounding=true)** |
| **STRAT-50** | **Budget-Burn in PHYSICAL_WAIT** | **used_cycles ändert sich nicht (burn_rate_multiplier=0)** |
| **STRAT-51** | **Stall-Detektion in AWAITING_HUMAN** | **suspendiert (stall_detection_active=false)** |
| **STRAT-52** | **SET_RESEARCH_PHASE auf ungültigen Zielzustand** | **VETO, Achse unverändert** |
| **STRAT-53** | **provisional bei trunkiertem Briefing** | **royal_log_entry.provisional=true** |
| **STRAT-54** | **Regel setzt Achsen-Parameter direkt** | **SL-DEP-Lint Build-Fail (Single Ownership)** |

---

## §25 Behobene Funde (Traceability)

| Fund | Auflösung |
|---|---|
| KV2-01 (Zeit/Budget) | SL-BUD-1 liest resource.burn_rate_multiplier (§19.2) |
| KV2-04 (Budget-Formeln) | SL-BUD-4 mit Formeln (§19.2) |
| KV2-05 (Toleranz-Überladung) | metric_tolerance_multiplier RESEARCH-besetzt; hysteresis_band in 20_contracts |
| KV2-06 (physische Trägheit) | resource=PHYSICAL_WAIT, burn_rate=0 (§19.2, §12) |
| KV2-07 (Kontext-Blackout) | EvidenceBundle-Vertrag in 20_contracts (geplant) |
| KV2-08 (De-novo-Deadlock) | require_atlas_grounding RESEARCH-besetzt (§7.2) |
| KV2-10 (Bio-Sequenz-Safety) | SL-SAN-0/SL-SAN-5 (§15); Bio-Scanner als Erweiterung |
| KV2-11 (stilles Scheitern) | Go/No-Go-Eskalation via SL-ESC (§13) |
| KV2-14 (Stall-Detektion) | SL-NOACT-1 liest governance.stall_detection_active (§5.3) |
| K7-F-07 (exploration_weight) | SL-DTT setzt nicht mehr direkt; ResearchAxis besitzt (§4, §1.2) |
| K7N-F-01 (provisional) | DTT setzt provisional in RoyalLogEntry (§4.2) |

**Weiterhin offen** (in `10_core` oder als Erweiterung): KV2-09 (Wissens-Amnesie, Domain Knowledge Base), KV2-13 (Kontamination, CONTAMINATED-Status), KV2-10 (Bio-Sequenz-Scanner als konkrete Implementierung).

---

## §26 Changelog

| Version | Datum | Änderung | Funde behoben |
|---|---|---|---|
| 1.0.0 | 2025-01-XX | Initiale Konsolidierung aus v0.2.0+v0.3.0; Achsen-Integration (ControlState-Lesen); provisional-Regel; STRAT-46..54 | KV2-01, -04, -05, -06, -08, -14; K7-F-07; K7N-F-01 |

---

**Ende des Rules-Moduls v1.0.0.**