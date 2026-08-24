# 📄 GREMIUM_STRATEGY.md — v1.0.0 (Schritt 2)

---

| Feld | Wert |
|---|---|
| Dateiname | specs/GREMIUM_STRATEGY.md |
| Version | 1.0.0 |
| Status | BINDEND — ersetzt die strategischen Anteile der GREMIUM_UNIFIED_SPECIFICATION v1.0.0 |
| System | MYRMEX v2.4.0 + Questor v0.2.3 + HAL v0.2.0 |
| Schicht | Layer 1 (specs/) — referenziert foundation/ |
| Baut auf | CHARTER 1.0.0, CONTRACTS 1.2.0-strat.1, GREMIUM.md 2.0.0, DIGITAL-TWIN-SEM-1.0.0 |
| Konfliktregel | CHARTER > CONTRACTS > GREMIUM.md > dieses Dokument (intern: SAFETY-Regeln absolut) |
| Testgrundlage | DT8 (13 Funde), DT9 (8 Funde), DT10 (4 Funde) |
| Datum | 21. August 2026 |

---

## §0 Zweck, Leseregel, Geltung

### §0.1 Zweck
Dieses Dokument definiert die **strategische Kognitionsschicht** des Gremiums („Cognitive Observatory"): ein System, das über Wochen autonom forschen kann — drift-frei, CHARTER-konform, mit deterministischen Endentscheidungen und definierten menschlichen Eingriffspunkten.

### §0.2 Abgrenzung zu GREMIUM.md
- **GREMIUM.md** definiert die **Pipeline-Mechanik**: 9-Stufen-Pipeline, Archivar → Kartograph → Vordenker → Lotse → Quartiermeister → Sicherheitsrat → Dispatcher → Questor → Receiver.
- **Dieses Dokument** definiert die **strategische Steuerung**: Kanzler/Königin, Briefing-Zyklus, 4-Achsen-Architektur, ControlState, Intent-Verfügbarkeit, Closure-Regeln.
- Beide Dokumente bilden eine Einheit. GREMIUM.md ist das „Wie läuft ein Zyklus ab?", dieses Dokument ist das „Wer entscheidet was?".

### §0.3 Leseregel und Konfliktregel
- CHARTER > CONTRACTS > GREMIUM.md > dieses Dokument.
- Innerhalb dieses Dokuments: SAFETY-Regeln (SL-SAF, SR-05, SR-19) sind **absolut** und überstimmen alle anderen Regeln.
- Die 4-Achsen-Steuerung (§29..§34) ist eine **DESIGN-FESTLEGUNG**; wo sie vom Quell-SystemMode abweicht, ist sie als solche markiert.

### §0.4 Vertragsreferenz
Alle Datenverträge (Enums, Pydantic-Modelle, Config) sind in **CONTRACTS.md §6.11** definiert. Dieses Dokument definiert **keine neuen Verträge**. Es referenziert ausschließlich:
- `CONTRACTS §6.11.1` ControlState
- `CONTRACTS §6.11.2` AxisTransition
- `CONTRACTS §6.11.3` ControlStateLog
- `CONTRACTS §6.11.4` StrategicBriefing
- `CONTRACTS §6.11.5` StrategicDirective
- `CONTRACTS §6.11.6` DirectiveParameters
- `CONTRACTS §6.11.7` Mission-Verträge
- `CONTRACTS §6.11.8` Governance-Verträge
- `CONTRACTS §6.11.9` Forschungs-Verträge
- `CONTRACTS §6.11.10` Report-Verträge
- `CONTRACTS §6.11.11` StrategicLayerConfig

### §0.5 Ehrlichkeitshinweis (bindend für Tests)
Die Achsen-Architektur ist eine Design-Festlegung, keine Quell-Ableitung. Die Severity-Ordnung (§34.1) und Closure-Regeln (§34.2) sind bewusste Wahlen. Die Dry-Tests DT8–DT10 waren selbst-generiert; reale Validierung steht aus.

---

## MODUL CORE

---

## §1 Grunddefinitionen (SL-DEF-1..5)

**SL-DEF-1 Strategischer Zyklus:** 1 Zyklus = 1 abgeschlossener Regelkreis: StrategicBriefing erzeugt → StrategicDirective empfangen → Validierung → Policy-Wirkung. Alle `*_cycles` beziehen sich darauf.

**SL-DEF-2 Weißraum:** Eine Region ist Weißraum, wenn ihre Zone `UNEXPLORED` ist oder `EXPLORED_INCONCLUSIVE` mit `evidence_mass == 0`.

**SL-DEF-3 Pipeline-Takt:** ereignisgetrieben; jedes verarbeitete Ergebnis schreitet fort. Treibt Archivar/Kartograph/Atlas.

**SL-DEF-4 Strategie-Zyklus:** der Briefing-Regelkreis (SL-DEF-1). `briefing_id` ist die einzige Zyklen-ID (`zyklus_id` abgeschafft). Auslösung durch `cycle_trigger ∈ {TIME, EVENT_COUNT, MANUAL}`.

**SL-DEF-5 TimeService:** Alle `*_days`-Parameter und Timeout-Auswertungen nutzen `TimeService`. Alle `*_cycles` nutzen den Strategie-Zyklus. Keine Vermischung.

---

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

**SL-ACC-1:** Alle Kommunikation über Blackboard-Artefakte (§24.5). Keine direkten Aufrufe. (→ CHARTER §2)

**SL-ACC-2:** Die Königin liest den Atlas nicht direkt; ihr einziger Zugang ist das StrategicBriefing.

**SL-ACC-3:** Der Vordenker liest Atlas-Topologie nur lesend als kuratierte Ausschnitte; er schreibt nie in den Atlas.

**SL-ACC-4:** Questor und HAL bleiben unverändert; sie kennen keine strategischen Verträge. (→ CHARTER §SR-04)

---

## §3 Constitutional Anchor Protocol (SL-ANCHOR-1..4)

Jeder Königin-LLM-Aufruf erhält exakt drei Kontextblöcke (SL-ANCHOR-1):

1. **CONSTITUTIONAL MEMORY** (invariant): mission_goal, hard_constraints, soft_preferences, Verbotene Aktionen, Output-Schema.
2. **STATELESS BRIEFING** (dynamisch): aggregierter Zustand, Budget, Fractures, Twin-Status, DecisionsRequired — kein security_mode, keine Hybrid-Referenzen, kein Roh-metric_vector.
3. **ANCHOR** (Kontinuität): zuerst aktive HUMAN_OVERRIDE-Einträge, dann die letzten `royal_log_anchor_depth` (=3) eigenen Direktiven mit Outcome.

**SL-ANCHOR-2:** Kein persistenter Gesprächsverlauf. Jeder Aufruf frisch.

**SL-ANCHOR-3:** Menschliche Weisungen im Anchor überschreiben alle Königin-Direktiven (expliziter Hinweis im Anchor).

**SL-ANCHOR-4:** LLM-Fehler/Timeout → Policy bleibt unverändert, Audit, kein erweiterter Retry. Nach `max_consecutive_llm_failures` → Eskalation.

---

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

---

## §5 Kern-Patterns

1. **Stateless Director (§5.1):** Königin zustandslos.
2. **Deterministic Gatekeeper (§5.2):** Kanzler rein deterministisch (SL-GATE-1). Kein LLM im Kanzler.
3. **Topology-Grounded Hypothesis Engine (§5.3):** Vordenker nur via SymptomEvents.
4. **Digital-Twin-Loop (§5.4):** gemäß DIGITAL-TWIN-SEM, gehärtet (§14).
5. **Orthogonal Control Axes (§5.5, DESIGN):** 4 Achsen (§29), ControlState-Tupel.

---

## MODUL RULES

---

## §6 Missions-Bootstrap (SL-BOOT-0..8)

**SL-BOOT-0 Manifest-Intake (fail-closed):** `created_by==MENSCH` und `approved_by==MENSCH`; `value` XOR `range` je Operator; jeder `dimension_ref` existiert in `initial_dimensions`; EXCLUSION mit `categories` nicht-leer; `valid_until` via TimeService in Zukunft. Verstoß → REJECT.

**SL-MAN-9 Operator×Enforcement-Matrix:** EXCLUSION mit `categories` ODER (operator+value); SAFETY mit (operator+value); BOUNDS mit `range` ODER (operator+value).

**SL-BOOT-1..6 Kaltstart:** Mensch erstellt Manifest → Kanzler erzeugt MissionBootstrap (Dimensionen, ObjectiveFamily, Topic PROPOSED, Budget) → materialisiert Constraints → BOOTSTRAP-Briefing → Königin antwortet INITIAL_SWEEP → Topic ACTIVE → Kanzler emittiert SymptomEvent(INITIAL_SWEEP).

**SL-BOOT-2 erweitert:** Fehlen `lab_ambient_temp`/`lab_ambient_humidity` → Bootstrap blockiert (Schatten-Variablen-Check stets ausführbar).

**SL-BOOT-2b Initiale Zonen:** aus deterministischem Template des ObjectiveFamilySeed; leerer Atlas → `avg_uncertainty_score = None`.

**SL-BOOT-7 Template-Lücke:** fehlendes Template → Paket zurückgestellt, G-1 ausgelöst.

**SL-BOOT-8 Deadlock-Schutz:** nach `bootstrap_retry_limit` (=3) invaliden INITIAL_SWEEP-Antworten → TEMPLATE_GAP-Eskalation; Topic bleibt PROPOSED.

---

## §7 Validierungspipeline v2 (10 Stufen, feste Reihenfolge)

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
 ├─ 6b. Mode-Prüfung via ControlState (§32)              FAIL → VETO("MODE_VIOLATION")
 ├─ 6c. Semantische Dedup (SL-INT-5)                     FAIL → VETO("DUPLICATE_SEMANTIC")
 ├─ 7. Konflikt-Modus-Prüfung (SL-CON-3)                 FAIL → VETO("CONFLICT_MODE")
 └─ 8. ACCEPT → DirectiveTranslationTable
```

**Schritt 6b (Mode-Prüfung):** liest den ControlState und wendet die Intent-Verfügbarkeit (§32) an. Die Intent-Whitelist ergibt sich aus der Achsen-Kombination, nicht aus einem separaten SystemMode.

---

## §8 DirectiveTranslationTable (SL-DTT)

Deterministische Übersetzung; kein Interpretationsspielraum.

| Intent | Pflicht-Parameter | Deterministische Wirkung |
|---|---|---|
| NO_ACTION | — | keine Policy-Änderung; Zyklus protokolliert |
| INITIAL_SWEEP | grid_spec, sweep_template_ref | Topic PROPOSED→ACTIVE, Seed-Symptom. Setzt exploration_weight NICHT direkt (RESEARCH-besetzt) |
| PIVOT_DOMAIN / PIVOT_TARGET | from_topic_ref, to_topic_seed | Scope-Check (SL-DIR-8), Feasibility (SL-DTT-2), Loop-Erkennung (SL-DTT-3); altes Topic→ARCHIVED nach Lessons-Learned; neues PROPOSED |
| UNLOCK_BUDGET | amount_cycles, purpose | immer Eskalation(BUDGET); bei Bestätigung reserved→used (SL-BUD-3) |
| ABORT_MISSION | reason | immer ESCALATED; nur mit menschlicher Bestätigung |
| ADD_DIMENSION_HINT | source_ref, dimension_seed | erzeugt DimensionOnboardingRequest |
| INCREASE_DIAGNOSTIC | zone_ref, amount | diagnostic_budget += amount (max) |
| CALIBRATE_TWIN | twin_ref | VETO wenn nicht gedriftet (NO_DRIFT); sonst diagnostic_weight↑ |
| ARCHIVE_TOPIC | topic_ref | Topic→ARCHIVED nach Lessons-Learned |
| SET_PRIORITY | topic_ref, priority | Topic.priority setzen |
| DROP_SOFT_PREFERENCE | preference_ref | soft_preference deaktivieren |
| HUMAN_ESCALATION | question, escalation_category | Eskalation mit Typ aus category. **Bei escalation_category=CAPEX: löst zusätzlich resource → PHYSICAL_WAIT (via CT-5) und governance → AWAITING_HUMAN (via CT-6) aus.** (BF-08) |
| SET_RESEARCH_PHASE | target_phase, reason | löst ResearchAxis-Wechsel aus (§33); Validierung prüft Ziel-ControlState |

**SL-DTT-1 Lessons-Learned:** topic-lokale weiche Filter (TopicConstraintProposal), keine ManifestConstraints. Aufstieg zu hart nur über neue menschliche Manifest-Version (SL-MAN-1 gewahrt).

**SL-BRF-9 provisional:** Die DTT setzt `royal_log_entry.provisional = true`, wenn `briefing_ref` auf ein trunkiertes Briefing verweist (`briefing.truncation_applied == true`). Es ist ein DTT-Ausgabe-/Audit-Feld, kein Feld der Königin-Direktive.

---

## §9 Konfliktdetektor & NO_ACTION (SL-CON, SL-NOACT)

**SL-CON-1:** Jeder GOVERNANCE-VETO gegen eine Königin-Direktive zählt als Konflikt (BENIGN-VETOs zählen nicht, SL-CON-4).

**SL-CON-2:** 2 Konflikte in `conflict_window_cycles` → URGENT + Eskalation(DEADLOCK); Königin erzeugt nur noch NO_ACTION.

**SL-CON-3 Mechanischer Konflikt-Modus:** nur NO_ACTION/HUMAN_ESCALATION angenommen; übrige → VETO("CONFLICT_MODE"), zählt nicht als neuer Konflikt.

**SL-CON-4 VETO-Schwere-Klassen:** BENIGN = {NO_DRIFT, TARGET_LOCKED, einzelne SCHEMA_INVALID, DUPLICATE_SEMANTIC}; GOVERNANCE = {MANIFEST_VIOLATION, HUMAN_DIRECTIVE_VIOLATION, Safety-/Injection-VETOs}.

**SL-INT-5 Semantische Dedup:** `semantic_directive_id = sha256(intent + target_ref + canonical_json(parameters))`. Wiederholung mit gleichem Outcome innerhalb `semantic_dedup_window_cycles` → VETO("DUPLICATE_SEMANTIC"), ausgenommen NO_ACTION.

**SL-NOACT-1:** liest `governance.stall_detection_active`. Wenn false → Stall-Counter wird NICHT erhöht. Wenn true → `no_action_stall_limit` aufeinanderfolgende NO_ACTION ohne Atlas-Fortschritt → URGENT. Reset nach URGENT-Zustellung.

**SL-NOACT-2:** Während HOLD/SAFE (governance=AWAITING_HUMAN oder safety=SAFE_MODE) ist die Stall-Überwachung suspendiert. Kein Eskalations-Sturm.

---

## §10 Symptom-Trigger und Vordenker

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

**SL-URG-1 URGENT-Trigger:** fracture_score ≥ full_rebuild_threshold; tolerance_breached; Topic SATURATED ohne Ziel bei Budget > stagnation_budget_threshold; LOCKED-Zone ohne Diagnose-Strategie; Konflikt; CapabilityGap mit requires_budget_or_hardware; SAFETY-Ereignis; Manifest-Sprung; NO_ACTION-Stall; Quarantäne-Timeout; questor_health_status==DEAD; remaining_cycles ≤ budget_unlock_threshold_fraction; Mission ohne aktives Topic.

**SL-URG-3:** URGENT-Nachzügler während Cooldown werden ins nächste PERIODIC gemerged; kein stiller Verlust.

**SL-SYM-1 Verlustschutz:** SymptomEvents vor Queue-Übergabe persistent; bei High-Watermark zurückgestellt und erneut zugestellt (At-Least-Once).

---

## §11 Signal-Semantik (SL-SIG, SL-HYP)

**SL-SIG-1 Korrigierter Fallback:**
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

**SL-SIG-2:** Operationale Paketfehler fließen nie in wissenschaftliche Metriken (nur HardwareHealth.operational_failure_count_recent).

**SL-SIG-3:** Sättigung hat genau eine Quelle (Topic-StopCondition SATURATION_CYCLES).

**SL-SIG-4:** ObjectiveFamily-Constraints werden binär gegatet.

**SL-SIG-5 Replikat-Divergenz:** zwei parameter-äquivalente Kristalle mit Differenz > tolerance → REPLICATE_DIVERGENCE (nur wenn `replicate_divergence_check == true`, RESEARCH-besetzt). „Parameter-äquivalent" bedeutet: Alle Diskrepanzen in kontinuierlichen Dimensionen liegen innerhalb der konfigurierten Toleranz (`metric_tolerance_multiplier` oder `twin_epsilon_default`). *(DT10-F-04)*

**SL-SIG-6:** Operativer Fehler auf integrity_dim → validity=COMPROMISED.

**SL-SIG-7:** Constraint-Verletzung ohne Erwartung → ⬜ CONSTRAINT_NEAR_MISS.

**SL-SIG-7a Overfitting:** Overfitting (z. B. `train_val_gap > threshold` in einem ObjectiveFamily-Constraint) wird als `CONSTRAINT_NEAR_MISS` (SL-SIG-7) behandelt: ⬜ Signal, kein 🟨 CONTRADICTION. Erst wenn der Constraint wiederholt verletzt wird, erzeugt der Kartograph eine `MetricConstraint`-Fracture. „Wiederholt" bedeutet: ≥ `min_confirmations` (=2, RESEARCH-besetzt) parameter-äquivalente Kristalle mit derselben Constraint-Verletzung innerhalb von `conflict_window_cycles` (=10). *(BF-10, BF-17)*

**SL-SIG-8:** `negative_knowledge_decay` für erfolglos abgedeckte Regionen.

**SL-HYP-4 Erwartungs-Brücke:** Bestätigende Hypothesen müssen ExpectationSpec tragen. `require_atlas_grounding` ist RESEARCH-besetzt: in BOOTSTRAP/EXPLORATION ist De-novo (atlas_refs=[]) erlaubt, in EXPLOITATION/SATURATION nicht.

---

## §12 Manifest-Enforcement (SL-MAN)

Schutzkette: Manifest.hard_constraints → SL-BOOT-3 Materialisierung → ExclusionConstraint/SafetyConstraint im Atlas → FrontierEngine-Hartfilter Nr.10 → Pre-Filter → Quartiermeister SL-MAN-4 (parameter_bounds ∩ Constraints) → PolicyEvaluator Prüfung 9.

**SL-MAN-7 Semantische Umgehungsabwehr:** neue kategorische Werte nicht in ManifestConstraint.categories → Constraint-Verstoß.

---

## §13 Safety-Reaktionskette (SL-SAF, Quarantäne)

**SL-SAF-1..4 ESTOP-Kette:** HAL meldet ESTOP → Questor SAFETY-Abbruch (SR-19) → Archivar SAFETY-Governance-Ereignis → Kanzler ereignisgesteuert SOFORT: Zone→LOCKED, SafetyConstraint-Vorschlag, URGENT-Briefing, Eskalation(SAFETY_EVENT), Achsen-Transition safety→ESTOP_LOCKED (§29).

**SL-SAF-2c Globales ESTOP → Zonen-Mapping:** Zonen mit in-flight-Paketen + Ursprungs-Slot-Zone → LOCKED; übrige → INTERLOCKED bis HAL-Gesundcheck.

**SL-SAF-4 erweitert:** ESTOP-/Reset-Begriffsprüfung rekursiv über canonical-geflattete parameters.

**SL-SAF-5 Entsperrpfad:** LOCKED ausschließlich über strukturierte HumanResponseFile.unlock_decision. Zustandsfolge LOCKED → DIAGNOSTIC_ONLY → RELEASED.

**SL-SAF-6 SafetyConstraint-Aktivierung:** Vorschlag gilt sofort als active=provisional; menschliche Bestätigung macht permanent.

**SL-SAF-7 SAFE_MODE-Exit-Pfad:** *(BF-01)* Der Übergang `safety: SAFE_MODE → NORMAL` erfolgt ausschließlich durch eine `HumanResponseFile.unlock_decision` mit `scope_refs = ["GLOBAL_SAFETY"]` gemäß SL-SAF-5. Kein automatischer Übergang. Kein LLM-Pfad. Der Kanzler validiert die Freigabe und löst den atomaren Achsen-Transition aus. CT-9 (§34.2) erzwingt die Governance-Rückkehr.

**§13.6 Quarantäne:** Zustandsmaschine ENTRY → DIAGNOSTIC_ALLOWED → QUARANTINE_EXIT → {RESUME, CLOSE}. Diagnostik erlaubt und budgetiert. Blockierte Ideen emittieren QUARANTINE_BLOCK. Exit nur über strukturierte QUARANTINE_EXIT-Antwort. Sicherheitsrelevanz-Regel: Fracture ist sicherheitsrelevant genau dann, wenn seine Zone eine SafetyConstraint- oder SAFETY-Enforcement-Dimension schneidet.

---

## §14 Digital-Twin-Loop (SL-TWIN)

**SL-TWIN-1 Paarung:** erfordert objective_family_ref + digital_twin_ref + Parameter-Äquivalenz. Nicht-äquivalente werden nicht gepaart.

**SL-TWIN-2 Deviation:**
```
dev_metric = max(
    abs(sim−real)/max(abs(real), twin_epsilon_default),
    abs(sim−real)/abs_tolerance_metric)
abs_tolerance_metric = MetricDefinition.tolerance falls gesetzt,
                       sonst twin_abs_tolerance_default
Für real ≈ 0 gilt ausschließlich der Absolutterm.
```

**SL-TWIN-3 Validitätsprüfung:** digital_twin_ref gesetzt UND drift_score > threshold UND objective_type ≠ DIAGNOSE → VETO(TWIN_DEGRADED).

**SL-TWIN-4 Gate×Security-Mode-Matrix:** physisches Kalibrierungs-Paket konstruktionsunmöglich (SANDBOX erzwungen).

**SL-TWIN-5 Schatten-Variablen-Check:** bei TWIN_DRIFT zwingend Umgebungs-Dimensionen im Vordenker-Prompt.

**SL-TWIN-6..7 Dedup/Deadlock-Freiheit:** blocked_cache (twin_ref, zyklus); SANDBOX-Kalibrierung bleibt erlaubt.

**SL-TWIN-8 Konfidenz-Kalibrierung:** rollierender vordenker_calibration_score; bei < calibration_alert_threshold DecisionOption.

**SL-TWIN-9 Kalibrierungs-Abbruch:** nach twin_calibration_max_attempts (=3) ohne Drift-Reduktion ≥ twin_drift_reduction_min → SUSPENDED + Eskalation(TWIN_UNCALIBRATABLE).

**SL-TWIN-10 In-flight bei Drift:** twin_invalidated=true im Briefing.

**SL-TWIN-11 Late-Pairing:** nach TTL weitere twin_late_pairing_window_cycles nachpaarbar.

---

## §15 Dimensions-Lebenszyklus (SL-DIM)

**SL-DIM-1..4 Kanzler-Prüfung:** Plausibilität, Range-Validierung, Cooldown (max_dimension_requests_per_topic_per_cycle), physische Auswirkung (requires_physical_actuation=true → zwingend ESCALATED). CT-4 (§34.2) erzwingt governance → AWAITING_HUMAN.

**SL-DIM-5 Deadlock-Freiheit:** Ideen mit approved=false-Dimension werden nicht still verworfen → SymptomEvent(DIMENSION_GAP) + DecisionOption.

**SL-DIM-6..7 Genehmigung/Backfill:** erzeugt TypedDimension(approved=false); optional BACKFILL_FRONTIER.

**SL-DIM-8 Abgeleitete Dimensionen:** parent_dimension-Referenz.

**SL-DIM-9 CATEGORY_EXTENSION:** neue Kategoriewerte → leichter Request.

**SL-DIM-10 requires_physical_actuation:** jede Hardware-/Aktuierungsänderung außerhalb registrierter Capability-Parameter.

**SL-DIM-11 Lebenszeit-Limit:** max_dimension_requests_per_topic_total + Wiederholungs-Erkennung über proposed_dimension_id.

**SL-DIM-12 Request-Outcomes:** dimension_request_outcomes im Briefing.

**SL-DIM-13 Range-Korrekturen:** Feedback-Symptom an Vordenker.

**SL-DIR-7:** RequestSource-Union statt SymptomType-Zwang.

---

## §16 Capability-Gap & CAPEX (SL-ESC-7)

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
              → Achsen-Transition resource→PHYSICAL_WAIT (§29)
```

---

## §17 Mensch-Schnittstelle (SL-ESC)

**SL-ESC-1..4:** Eskalationskanal dateibasiert (`data/archiv/operational/escalations/`); Antworten in `data/human_inbox/`. Unbeantwortete Eskalation → nach timeout_cycles → governance→AWAITING_HUMAN. Erinnerungen alle escalation_reminder_interval_cycles (max escalation_reminder_cap).

**SL-ESC-5 HumanResponseFile-Validierung:** Antwortdateien müssen gegen das Schema validieren. Unparsbar → PARSE_REJECTED + Erinnerungs-Template.

**SL-ESC-6 EscalationType-Erweiterung + Dedup:** HUMAN_ESCALATION erhält Pflicht-Parameter escalation_category. Dedup über (escalation_type, target_ref).

---

## §18 Briefing-Erzeugung (SL-BRF)

**SL-BRF-1..6 Sanitization:** Verboten: security_mode, Hybrid-Referenzen, Roh-metric_vector. Fortschritt als deterministische Skalare. Quarantäne → [REDACTED:QUARANTINE].

**SL-BRF-4 Trunkierungspriorität v2:** URGENT-Auslöser + SAFETY > LOCKED/CRITICAL/QUARANTINE + drifted Twins + pending_escalations + decisions_required > höchste Fractures > aktive Topics > Rest. Twins mit calibration_required oder drift_score > 0 fallen nie in die Restklasse.

**SL-BRF-8 Gesamt-Kontext-Budget:** max_total_context_chars = manifest_max_chars + max_briefing_chars + anchor_max_chars. Layer 3 (Anchor) wird nie trunkiert.

**SL-BRF-10:** Briefing exponiert active_hypothesis_refs (Top-N).

---

## §19 Sanitization (SL-SAN)

**SL-SAN-0 First-Order-Scan:** aller LLM-Outputs vor Persistenz. Treffer → Quarantäne + Audit + einmalige Neu-Generierung, danach Eskalation.

**SL-SAN-1 Archivar-Eingangssanitization:** Freitextfelder eingehender questor_ergebnis_paket werden gescannt (INJ-01..15, XML-Escaping).

**SL-SAN-2 Second-Order-Scan:** persistierte LLM-Texte beim Wiedereinspeisen erneut gescannt. Treffer → Quarantäne, Platzhalter, Audit, DecisionOption.

**SL-SAN-5:** INJ-01..15 und Safety-Claim-Katalog als normativer Anhang.

**SL-SAN-6 Roh-Ergebnis-Trennung:** observation_raw (quarantänefähig) und interpretation (niemals Erwartungsquelle).

**SL-RPT-1 Zitiermuster-Entfernung:** deterministisch über Regex-Katalog; nicht erfassbare Fälle als review_required.

---

## §20 Abschluss und Archivierung (SL-RPT)

```
StopCondition REACHED → Topic SATURATED → FINAL-Briefing
  → Kanzler injiziert ReportFacts (deterministisch)
  → Königin-LLM: NUR executive_summary + future_recommendations
  → Kanzler: Sanitization + Zitierungs-Check
  → Mensch: human_reviewed = true → ARCHIVED → Cold Storage
```

**SL-RPT-2 Fakten-Trennung:** harte Fakten ausschließlich aus ReportFacts.

**SL-RPT-3..4:** Unreviewed-Reminder alle review_reminder_interval_cycles. Nach review_grace_max_cycles finale Eskalation. Nach cold_storage_window_days mit human_reviewed=true → Cold Storage.

---

## §21 Replikation (SL-REP)

**SL-REP-1:** FrontierType um REPLICATE erweitert.

**SL-REP-2:** REPLICATE-Frontiers bei crystallization_progress ≥ replication_trigger_progress und Bestätigungen < min_confirmations (RESEARCH-besetzt). Relevante Bestätigung: parameter-äquivalenter Kristall, gleiche ObjectiveFamily, ziel_erreicht=true. „Parameter-äquivalent" bedeutet: Alle Diskrepanzen in kontinuierlichen Dimensionen liegen innerhalb der konfigurierten Toleranz (`metric_tolerance_multiplier` oder `twin_epsilon_default`). *(DT10-F-04)*

**SL-REP-3:** FrontierEngine gewichtet REPLICATE mit replication_weight.

**SL-REP-4 Quotenregel:** ≥ 1 Replikation pro replication_cadence_cycles.

**SL-REP-5 Fracture-getriebene Replikation:** FRACTURE_GAP mit ≥ 2 divergenten Kristallen → REPLICATE-DecisionOption.

---

## §22 Datenintegrität (SL-INT)

**SL-INT-1 NaN:** Kristall verworfen, gültige Geschwister bleiben. Gilt auch für SymptomEvent.metrics_snapshot.

**SL-INT-2 Sequenzlücken:** akzeptiert + Audit-Flag + Reconciliation (Owner, Timeout, Abschlusszustand).

**SL-INT-3 Referentielle Integrität:** briefing_ref, source_ref, twin_divergence_report_ref müssen existieren.

**SL-INT-4 Idempotenz:** directive_id gemäß SL-DIR-1.

**SL-INT-6 Registry-Index:** Dateien je Verzeichnis für Existenzprüfungen.

---

## §23 Zyklus-, Zeit- und Budgetmodell (SL-BUD, SL-URG)

**SL-BUD-1:** `used_cycles += 1 × resource.burn_rate_multiplier`. In PHYSICAL_WAIT/BUDGET_EXHAUSTED ist burn_rate_multiplier=0 → Budget brennt nicht. (Achsen-Integration: ResourceAxis besitzt burn_rate_multiplier.)

**SL-BUD-1a:** *(BF-04)* Mission-Budget-Erschöpfung (`resource=BUDGET_EXHAUSTED`) beeinflusst keine laufenden Questor-Pakete. Diese werden ausschließlich durch ihr eigenes `QuestorSpec.budget.max_duration_s` gesteuert (→ QUESTOR.md §11.5). Neue Pakete werden nicht mehr dispatched (`physical_dispatch_allowed=false`, ResourceAxis-Besitz §31).

**SL-BUD-2:** remaining_cycles = total_cycles − used_cycles − reserved_cycles.

**SL-BUD-3:** Bei UNLOCK_BUDGET-Bestätigung: reserved_cycles → used_cycles.

**SL-BUD-4 Formeln:**
```
burn_rate_per_cycle = used_cycles / max(elapsed_cycles, 1)
estimated_completion_cycle = used_cycles + ceil(remaining_progress/progress_rate)
progress_rate ≤ 0 → None
```

**SL-URG-2 BUDGET_EXHAUSTED:** fällt remaining_cycles ≤ 0 oder unter budget_unlock_threshold_fraction → URGENT + Eskalation(BUDGET) + DecisionOption. Achsen-Transition: resource→BUDGET_EXHAUSTED, governance→AWAITING_HUMAN (via CT-1).

---

## §24 Zustandsmaschinen

**§24.1 Topic:** PROPOSED → ACTIVE → {SATURATED, ABORTED} → ARCHIVED. Alle Übergänge vom Kanzler. Lessons-Learned-Transfer bei jedem ACTIVE-Abschluss.

**§24.2 DimensionOnboardingRequest:** PROPOSED → APPROVED | REJECTED | ESCALATED | COOLDOWN. ESCALATED → APPROVED/REJECTED (Mensch).

**§24.3 Eskalation:** PENDING → ANSWERED | TIMED_OUT. TIMED_OUT → governance=AWAITING_HUMAN. ANSWERED → Umsetzung → RoyalLog.

**§24.4 SystemMode → Achsen (DESIGN):** SAFE_MODE → safety=SAFE_MODE; HOLD_STRATEGY → governance=AWAITING_HUMAN; ESTOP → safety=ESTOP_LOCKED. Der einzelne SystemMode wird nicht als parallele Maschine geführt.

**§24.5 Speicherorte (Blackboard-konform):**

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

---

## §25 Autonomie- und Eskalationsmatrix

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

## §26 CHARTER-Konformitätsmatrix

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
| §2 Blackboard | Alle Kommunikation über definierte Speicherorte (§24.5) |

---

## §27 Verbotene Patterns (Strategic Layer)

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
14. Achsen-Parameter direkt setzen statt über ControlState lesen (Single Ownership, §31).

---

## §28 Testsuite (STRAT-01..55)

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

## MODUL CONTROL (4-Achsen-Steuerung, DESIGN)

---

## §29 Achsen-Definition

| Achse | Werte | Treiber | Absolutheit |
|---|---|---|---|
| SafetyAxis | NORMAL / SAFE_MODE / ESTOP_LOCKED | HAL-Ereignis, Mensch | Absolut |
| ResourceAxis | FUNDED / INCUBATING / PHYSICAL_WAIT / BUDGET_EXHAUSTED | Budgetzähler, Liefer-/Capability-Signal, in-flight | Hoch |
| ResearchAxis | BOOTSTRAP / EXPLORATION / EXPLOITATION / SATURATION | Atlas-Metriken | Normal |
| GovernanceAxis | AUTONOMOUS / AWAITING_HUMAN / CONFLICT_LOCK | Eskalationsstatus, Konfliktdetektor | Normal |

Der Gesamtzustand ist das Tupel `(safety, resource, research, governance)`. Jede Achse wird unabhängig aktualisiert; ein „Phasenwechsel" ist eine Änderung einer Achse, nicht des ganzen Tupels.

---

## §30 Kompositionsregeln (Validitätsmatrix)

**§30.1 Orthogonalität:** Achsen komponieren; kein Override.

**§30.2 Validitätsmatrix (ungültige Kombinationen):**
- safety=ESTOP_LOCKED + resource=INCUBATING (ESTOP bricht in-flight ab).
- safety=SAFE_MODE + research=BOOTSTRAP (SAFE pausiert Bootstrap).
- resource=BUDGET_EXHAUSTED + governance=AUTONOMOUS (Budget-Erschöpfung erzwingt Eskalation).

**§30.3 Priorität:** Safety ist absolut. Andere Gates multiplikativ.

**§30.4 Keine Hierarchie zwischen Achsen:** Konflikte werden durch Single Ownership (§31) aufgelöst, nicht durch Rangfolge.

**§30.5 Quarantäne und ResearchAxis:** *(BF-09)* Quarantäne (`quarantine_mode=true` auf allen aktiven Topics) ändert die ResearchAxis nicht. Sie blockiert nur normalen Dispatch. Die ResearchAxis bleibt in ihrem aktuellen Zustand, solange `diagnostic_budget > 0` ist. Bei `diagnostic_budget == 0` und Quarantäne: URGENT-Trigger (SL-URG-1).

---

## §31 Parameter-Besitz-Matrix (Single Ownership)

**ResearchAxis-Besitz:** exploration_weight, exploitation_weight, require_atlas_grounding, replicate_divergence_check, metric_tolerance_multiplier, replication_weight, min_confirmations.

**ResourceAxis-Besitz:** burn_rate_multiplier, physical_dispatch_allowed, escalation_timeout_multiplier.

**GovernanceAxis-Besitz:** stall_detection_active.

**SafetyAxis-Besitz:** safety_dispatch_allowed, safety_intent_blocklist (berechnete Gates).

Regeln lesen diese Parameter über den ControlState; sie setzen sie NICHT direkt. Verstöße → SL-DEP-Lint Build-Fail.

---

## §32 Intent-Verfügbarkeit

```
verfügbare_Intents = alle_Intents
                     − safety_intent_blocklist
                     − resource_intent_blocklist
                     − governance_intent_blocklist
                     − research_intent_blocklist
```

### §32.1 safety_intent_blocklist (explizite Definition, BF-06)

Bei `safety=ESTOP_LOCKED`: alle Intents außer `{NO_ACTION, HUMAN_ESCALATION}`.

Bei `safety=SAFE_MODE`: `{PIVOT_DOMAIN, PIVOT_TARGET, UNLOCK_BUDGET, ADD_DIMENSION_HINT, SET_RESEARCH_PHASE, INCREASE_DIAGNOSTIC, CALIBRATE_TWIN, ARCHIVE_TOPIC, SET_PRIORITY, DROP_SOFT_PREFERENCE, ABORT_MISSION, INITIAL_SWEEP}`.

Erlaubt bei `safety=SAFE_MODE`: `{NO_ACTION, HUMAN_ESCALATION}`.

**Quarantäne-Diagnostik-Ausnahme (BF-15):** `INCREASE_DIAGNOSTIC` wird aus der `safety_intent_blocklist` bei `safety=SAFE_MODE` entfernt, wenn die Zielzone (`zone_ref` aus den Intent-Parametern) `quarantine_mode=true` hat (§13.6: „Diagnostik erlaubt und budgetiert"). In diesem Fall ist `INCREASE_DIAGNOSTIC` erlaubt, aber nur mit `amount ≤ diagnostic_budget_default` (=3) und nur für die quarantinierte Zone. Alle anderen Blocklist-Einträge bleiben unverändert.

### §32.2 resource_intent_blocklist (explizite Definition, BF-06)

Bei `resource=BUDGET_EXHAUSTED`: `{INITIAL_SWEEP, PIVOT_DOMAIN, PIVOT_TARGET, ADD_DIMENSION_HINT, INCREASE_DIAGNOSTIC, CALIBRATE_TWIN, SET_RESEARCH_PHASE, SET_PRIORITY}`.

Erlaubt bei `resource=BUDGET_EXHAUSTED`: `{NO_ACTION, UNLOCK_BUDGET, HUMAN_ESCALATION, ABORT_MISSION, ARCHIVE_TOPIC, DROP_SOFT_PREFERENCE}`.

### §32.3 Intent-Sonderregeln

- `UNLOCK_BUDGET` ist nur verfügbar, wenn `resource=BUDGET_EXHAUSTED`.
- `SET_RESEARCH_PHASE` ist verfügbar, wenn keine Safety-/Governance-Sperre vorliegt **und** `resource ∈ {FUNDED, INCUBATING}`. Bei `resource=BUDGET_EXHAUSTED` oder `resource=PHYSICAL_WAIT` ist `SET_RESEARCH_PHASE` blockiert (Teil der `resource_intent_blocklist`). *(BF-07)*

---

## §33 Transitionen & Liveness

Der Kanzler wertet Achsen-Transitionen bei jedem Strategie-Zyklus aus; Safety/Resource sind ereignisgesteuert (lösen sofort einen atomaren Auswertungszyklus aus, §34).

**Liveness-Watchdog:** global; wenn (now − letzter Strategie-Zyklus) > liveness_watchdog_hours → Heartbeat-Zyklus (nur Achsen-Auswertung, kein Briefing).

**compute_phase_label(state):** abgeleitetes Etikett, z. B. „EXPLOITATION + PHYSICAL_WAIT + CRISIS". Nicht authoritativ.

---

## §34 SL-AX-ATOMIC: Atomare Achsen-Auswertung

Alle Achsen-Transitionen werden atomar ausgewertet. Kein Zwischenzustand wird persistiert. (Behebt DT7-F-01 / K6-F-12.)

**Algorithmus (feste Reihenfolge):**

1. **SAMMELN:** alle im Auswertungszeitpunkt ausgelösten Transitionen in `direct_transitions` als (axis, from_value, to_value, timestamp).
2. **KONFLIKT-ERKENNUNG:** mehrere Ereignisse auf derselben Achse → schwerwiegendster Zielwert gewinnt (§34.1); unterlegene als SUPERSEDED verworfen.
3. **ABSCHLUSS (Closure):** Closure-Regeln (§34.2) iterativ anwenden, max closure_max_iterations (=5). Erzwungene Transitionen werden hinzugefügt.
4. **VALIDIERUNG:** finaler Ziel-Tupel gegen §30.2. Gültig → Commit. Ungültig trotz Closure → gesamte Transition VERWORFEN, ControlState unverändert, Audit + Eskalation(STRATEGIC_QUESTION) (fail-closed).
5. **ATOMARER COMMIT:** alle Transitionen des Batches in einer Operation, oder keine.
6. **LOGGING:** alle Transitionen eines Commits als ein Batch mit gemeinsamer batch_id.

### §34.1 Severity-Ordnung (DESIGN-FESTLEGUNG)

Achsen-Priorität: **SAFETY > RESOURCE > GOVERNANCE > RESEARCH**.

| Achse | Severity-Ordnung (schwer → leicht) |
|---|---|
| SafetyAxis | ESTOP_LOCKED > SAFE_MODE > NORMAL |
| ResourceAxis | BUDGET_EXHAUSTED > PHYSICAL_WAIT > INCUBATING > FUNDED |
| GovernanceAxis | CONFLICT_LOCK > AWAITING_HUMAN > AUTONOMOUS |
| ResearchAxis | kein Severity-Begriff; bei Konflikt → Audit + Eskalation |

Bei gleicher Achse und Severity entscheidet der früheste TimeService-Zeitstempel.

### §34.2 Closure-Regeln (CT-1..CT-10)

| ID | Auslöser | Erzwungene Folge | Begründung | Quelle |
|---|---|---|---|---|
| CT-1 | resource → BUDGET_EXHAUSTED | governance → AWAITING_HUMAN | §30.2 | v1.0.0 |
| CT-2 | safety → ESTOP_LOCKED ∧ resource=INCUBATING | resource verlässt INCUBATING (→ FUNDED, sofern kein schwererer Zielwert) | §30.2; in-flight abgebrochen (SR-19) | v1.0.0 |
| CT-3 | safety → SAFE_MODE | research-Transitionen werden unterdrückt; bei gleichzeitigem Auftreten im selben Batch hat Safety Vorrang (§34.1) | SAFE pausiert Direktiven | v1.0.0 + BF-12 |
| CT-4 | DimensionOnboardingRequest.status → ESCALATED ∧ requires_physical_actuation=true | governance → AWAITING_HUMAN | Physische Dimensionen erfordern menschliche Freigabe (SL-DIM-4, SR-11) | BF-05 |
| CT-5 | resource → PHYSICAL_WAIT | governance → AWAITING_HUMAN | Physisches Warten (CAPEX, Lieferung) erfordert menschliche Entscheidung (SR-11) | BF-02 |
| CT-6 | safety → SAFE_MODE ∨ safety → ESTOP_LOCKED | governance → AWAITING_HUMAN | Sicherheitsereignisse erfordern immer menschliche Aufsicht (SR-11) | BF-03 |
| CT-7 | resource: BUDGET_EXHAUSTED → FUNDED durch UNLOCK_BUDGET-Genehmigung | governance: AWAITING_HUMAN → AUTONOMOUS (sofern keine andere Governance-Sperre aktiv) | Symmetrie zu CT-1; verhindert Steckenbleiben in AWAITING_HUMAN | BF-11 |
| CT-8 | resource: PHYSICAL_WAIT → FUNDED durch CAPEX-/Lieferfreigabe (HumanResponseFile mit decision=APPROVE und escalation_type ∈ {CAPEX, CAPABILITY_DELIVERY}) **und** Capability in Registry als ACTIVE registriert | governance: AWAITING_HUMAN → AUTONOMOUS (sofern keine andere Governance-Sperre aktiv) | Symmetrie zu CT-5; verhindert Steckenbleiben in AWAITING_HUMAN nach physischer Lieferung. **DT10-F-03-Präzisierung:** Der Übergang erfordert nicht nur die Budget-Freigabe, sondern das Clearing des blocked_cache (d.h. die Capability muss in der Registry als ACTIVE registriert sein). | BF-14 + DT10-F-03 |
| CT-9 | safety: SAFE_MODE → NORMAL durch SL-SAF-7 (HumanResponseFile.unlock_decision mit scope_refs=["GLOBAL_SAFETY"]) | governance: AWAITING_HUMAN → AUTONOMOUS (sofern keine andere Governance-Sperre aktiv: resource ≠ BUDGET_EXHAUSTED ∧ resource ≠ PHYSICAL_WAIT ∧ kein CONFLICT_LOCK) | Symmetrie zu CT-6; verhindert Steckenbleiben in AWAITING_HUMAN nach Sicherheitsfreigabe | BF-16 |
| CT-10 | safety: ESTOP_LOCKED → NORMAL durch autorisierten Sicherheitsprozess (SR-05) | governance: AWAITING_HUMAN → AUTONOMOUS (sofern keine andere Governance-Sperre aktiv) | Symmetrie zu CT-6 für ESTOP; verhindert Steckenbleiben in AWAITING_HUMAN nach ESTOP-Reset | DT10-F-01 |

**SR-A:** ist safety ∈ {SAFE_MODE, ESTOP_LOCKED}, werden alle pending ResearchAxis-Transitionen verworfen.

### §34.3 SL-CT-SIMULTAN (Gleichzeitigkeit, BF-18)

Wenn mehrere CT-Regeln denselben Zielwert auf derselben Achse erzwingen (z. B. CT-5 und CT-6 erzwingen beide `governance → AWAITING_HUMAN`), gilt: kein Konflikt, nur eine Transition. Die Severity-Ordnung (§34.1) bestimmt den auslösenden Trigger für das Audit-Log. Bei unterschiedlichen Zielwerten auf derselben Achse: schwerster Zielwert gewinnt (§34.1).

### §34.4 Gearbeitetes Beispiel (ESTOP + Budget-Schwelle)

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
   - CT-6: safety=ESTOP_LOCKED ⇒ governance AUTONOMOUS→AWAITING_HUMAN
     → SL-CT-SIMULTAN: CT-1 und CT-6 fordern dasselbe Ziel → nur EINE Transition
   - SR-A: keine research-Transitionen
   Fixpunkt.
4. VALIDIERUNG: (ESTOP_LOCKED, BUDGET_EXHAUSTED, EXPLOITATION, AWAITING_HUMAN) → GÜLTIG
5. COMMIT: safety, resource, governance atomar
6. LOGGING: 1 Batch, 3 AxisTransition-Einträge
```

---

## MODUL INDEX

---

## §35 Fund-Register (Behebungsstatus)

| Fund-Cluster | Behebungs-Abschnitt | Status |
|---|---|---|
| KV-01/KV-20 Mensch-Schnittstelle | §17, §18 (SL-BRF-9) | BEHOBEN |
| KV-02 Lessons-Learned | §8 (SL-DTT-1) | BEHOBEN |
| KV-03 Zyklus/Zeit/Budget | §23 (SL-BUD) | BEHOBEN |
| KV-04 Manifest-Intake | §6 (SL-BOOT-0) | BEHOBEN |
| KV-05 Intent-Parameter | §7 (Validierungspipeline) | BEHOBEN |
| KV-06/07/08 Twin | §14 (SL-TWIN) | BEHOBEN |
| KV-09 Schatten-Variablen | §6 (SL-BOOT-2) | BEHOBEN |
| KV-10 Replikation | §21 (SL-REP) | BEHOBEN |
| KV-11 HOLD/SAFE | §30/§31 (Achsen), §9 (SL-NOACT-2) | BEHOBEN |
| KV-12 In-flight-Pakete | CONTRACTS §6.11.4 (InFlightPackageSummary) | BEHOBEN |
| KV-13 Config-Lücken | CONTRACTS §6.11.11 (StrategicLayerConfig v2) | BEHOBEN |
| KV-14 Entsperr-/Exit-Pfade | §13 (SL-SAF-5, Quarantäne) | BEHOBEN |
| KV-15 Dedup | §9 (SL-INT-5) | BEHOBEN |
| KV-16 Tote Vertragsfelder | §8 (priority/keep_constraints gestrichen) | BEHOBEN |
| KV-17 First-Order-Scan | §19 (SL-SAN-0) | BEHOBEN |
| KV-18 NO_ACTION-Zwang | §9 (SL-CON-3) | BEHOBEN |
| KV-19 EscalationType | §6 Enums, §17 (SL-ESC-6) | BEHOBEN |
| KV-21 Initiale Zonen | §6 (SL-BOOT-2b) | BEHOBEN |
| KV-22 Erwartungs-Brücke | §11 (SL-HYP-4) | BEHOBEN |
| DT7-F-01 Simultane Achsen-Transitionen | §34 (SL-AX-ATOMIC) | BEHOBEN |
| DT8-F-01 Dimensions-Eskalation → AWAITING_HUMAN | §34.2 (CT-4) | BEHOBEN |
| DT8-F-02 PHYSICAL_WAIT → AWAITING_HUMAN | §34.2 (CT-5) | BEHOBEN |
| DT8-F-03 CAPEX in §41 | §8 (SL-DTT), §34.2 (CT-5/CT-6) | BEHOBEN |
| DT8-F-05 SAFETY → AWAITING_HUMAN | §34.2 (CT-6) | BEHOBEN |
| DT8-F-06 SAFE_MODE → NORMAL | §13 (SL-SAF-7) | BEHOBEN |
| DT8-F-07 safety_intent_blocklist | §32.1 | BEHOBEN |
| DT8-F-08 Quarantäne + Research-Achse | §30.5 | BEHOBEN |
| DT8-F-10 Overfitting | §11 (SL-SIG-7a) | BEHOBEN |
| DT8-F-11 Laufende Jobs bei Budget-Erschöpfung | §23 (SL-BUD-1a) | BEHOBEN |
| DT8-F-12 SET_RESEARCH_PHASE bei BUDGET_EXHAUSTED | §32.3 | BEHOBEN |
| DT8-F-13 CT-1 Umkehrung | §34.2 (CT-7) | BEHOBEN |
| DT9-F-01 PHYSICAL_WAIT → FUNDED Rückkehr | §34.2 (CT-8) | BEHOBEN |
| DT9-F-03 INCREASE_DIAGNOSTIC bei Quarantäne | §32.1 (Quarantäne-Diagnostik-Ausnahme) | BEHOBEN |
| DT9-F-04 SAFE_MODE → NORMAL Rückkehr | §34.2 (CT-9) | BEHOBEN |
| DT9-F-05 CT-Gleichzeitigkeit | §34.3 (SL-CT-SIMULTAN) | BEHOBEN |
| DT9-F-07 SL-SIG-7a Quantifizierung | §11 (SL-SIG-7a) | BEHOBEN |
| DT10-F-01 ESTOP_LOCKED → NORMAL Rückkehr | §34.2 (CT-10) | BEHOBEN |
| DT10-F-02 Terminologie zone_ref | §32.1 (BF-15) | BEHOBEN |
| DT10-F-03 CT-8 Trigger-Präzisierung | §34.2 (CT-8, DT10-F-03-Präzisierung) | BEHOBEN |
| DT10-F-04 Parameter-Äquivalenz-Toleranz | §11 (SL-SIG-5), §21 (SL-REP-2) | BEHOBEN |

**Restrisiken (bewusst dokumentiert):**
- Freitext-only-Menschenweisungen sind nur beratend (§17 SL-ESC-5).
- Unreviewed-Reports blockieren Cold Storage, nicht neue Missionen.
- LLM-Wissenschaftsqualität nur in realen Domänen validierbar.
- Die 4-Achsen-Architektur, Severity-Ordnung (§34.1) und Closure-Regeln (§34.2) sind Design-Festlegungen; ihre reale Bewährung steht aus.

---

## §36 Change-Log

| Version | Änderung |
|---|---|
| 1.0.0 | Erstellung aus GREMIUM_UNIFIED_SPECIFICATION v1.0.0. Integration aller DT8-Backfixes (BF-01..BF-13), DT9-Backfixes (BF-14..BF-18) und DT10-Empfehlungen (CT-10, CT-8-Präzisierung, Parameter-Äquivalenz-Toleranz). Datenverträge in CONTRACTS.md §6.11 ausgelagert. 10 Closure-Regeln (CT-1..CT-10). SL-CT-SIMULTAN. SL-SAF-7. SL-SIG-7a. Quarantäne-Diagnostik-Ausnahme. |