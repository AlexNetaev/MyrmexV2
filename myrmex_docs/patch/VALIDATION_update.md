# 📄 VALIDATION.md v1.2.0 — ÄNDERUNGSANWEISUNG (Schritt 5)

**Aktion:** Die folgenden Änderungen sind in die bestehende `ops/VALIDATION.md` (v1.1.0-atlas-hyb.1) einzuarbeiten. Das Ergebnis ist Version **1.2.0-strat.1**.

---

## ÄNDERUNG 1: Kopfzeile

**ERSETZE** die bestehende Kopfzeile:

| Feld | Wert |
|---|---|
| Dateiname | ops/VALIDATION.md |
| Version | **1.2.0-strat.1** |
| Status | ÄNDERUNGSANTRAG STRAT-1.0.0 — nach Freigabe BINDEND |
| System | MYRMEX v2.4.0 + Questor v0.2.3 + HAL v0.2.0 + Gremium Strategic Layer v1.0.0 |
| Schicht | Layer 2 (ops/) — referenziert foundation/ und specs/ |
| Datum | 21. August 2026 |

---

## ÄNDERUNG 2: Neuer Abschnitt §0.2 (nach §0.1 einfügen)

**NEU — nach §0.1 einfügen:**

### §0.2 Änderungsantrag STRAT-1.0.0 — Strategic-Layer-Test-Suite

Dieser Änderungsantrag fügt die Strategic-Layer-Test-Suite (Suite STRAT) in die Teststrategie ein.

Die Strategic-Layer-Test-Suite testet:
- ControlState-Manager und 4-Achsen-Zustandsmaschine
- Closure-Regeln CT-1..CT-10
- SL-AX-ATOMIC (atomare Achsen-Transitionen)
- Intent-Verfügbarkeit und Blocklists
- Validierungspipeline (10 Stufen)
- DirectiveTranslationTable (DTT)
- Konfliktdetektor und NO_ACTION
- Briefing-Erzeugung und Sanitization
- Constitutional Anchor Protocol
- Symptom-Trigger und Vordenker-Ansteuerung
- SL-SAF-7 (SAFE_MODE-Exit)
- SL-SIG-7a (Overfitting als CONSTRAINT_NEAR_MISS)
- Quarantäne-Diagnostik-Ausnahme

Regeln:
- Dieser Änderungsantrag definiert keine neuen Verträge (→ CONTRACTS.md §6.11).
- Dieser Änderungsantrag definiert keine neuen Sicherheitsregeln (→ CHARTER.md).
- Die Strategic-Layer-Tests respektieren das Blackboard-Pattern und die Trennung von Operational und Scientific.
- Questor und HAL erhalten auch in den Tests keine Kenntnis von Strategic-Layer-Verträgen.
- Die Tests referenzieren `specs/GREMIUM_STRATEGY.md` für die Regeldefinitionen.

---

## ÄNDERUNG 3: §2.2 aktualisieren (Test-Verteilung)

**ERSETZE** die bestehende Tabelle in §2.2:

### §2.2 Test-Verteilung

| Ebene | Anzahl | Anteil | Zweck |
|---|---|---|---|
| Unit-Tests | ~252 | 43% | Einzelne Funktionen und Klassen |
| Komponententests | ~44 | 8% | Zusammenspiel mehrerer Module |
| Sicherheitstests | ~30 | 5% | Sicherheitskritische Pfade |
| Performance-/Stress-Tests | ~21 | 4% | Last, Latenz, Ressourcen |
| Atlas-Hybrid-Tests | ~120 | 21% | Atlas-Hybrid-System |
| **Strategic-Layer-Tests** | **~170** | **29%** | **Strategic Layer (Achsen, Kanzler, Königin)** |
| Integrationstests (bestehend) | 18 | 3% | Questor ↔ Gremium (Suite I) |
| Szenario-Tests (bestehend) | 5 | 1% | End-to-End (Suite S) |
| Sonstige bestehende Tests | 51 | 9% | Suite N, R, Z, H |
| **Gesamt** | **~711** | **100%** | |

---

## ÄNDERUNG 4: §2.3 aktualisieren (Test-Suiten-Übersicht)

**ERSETZE** die bestehende Tabelle in §2.3:

### §2.3 Test-Suiten-Übersicht

| Suite | Tests | Status | Zweck |
|---|---|---|---|
| Suite N | 7 | Existiert | Naming & Contract Migration |
| Suite I | 18 | Existiert | Integration |
| Suite S | 5 | Existiert | Szenario-Pflichttests |
| Suite R | 12 | Existiert | Regressions-Tests |
| Suite Z | 8 | Existiert | Zielpräzisierung |
| Suite H | 24 | Existiert | HAL v0.2.0 |
| Suite Q-U | ~252 | NEU | Questor Unit-Tests |
| Suite Q-C | ~44 | NEU | Questor Komponententests |
| Suite Q-S | ~30 | NEU | Questor Sicherheits-Tests |
| Suite Q-P | ~10 | NEU | Questor Performance-Tests |
| Suite Q-T | ~11 | NEU | Questor Stress-Tests |
| Suite ATLAS | ~120 | NEU | Atlas-Hybrid-System |
| **Suite STRAT** | **~170** | **NEU** | **Strategic Layer (Achsen, Kanzler, Königin)** |
| **Gesamt** | **~711** | | |

---

## ÄNDERUNG 5: Neuer Abschnitt §4.7 (nach §4.6 einfügen)

**NEU — nach §4.6 (Suite ATLAS) einfügen:**

### §4.7 Suite STRAT — Strategic-Layer-Tests (~170 Tests)

#### §4.7.1 Übersicht der STRAT-Test-Bereiche

| Bereich | Test-Präfix | Anzahl | Zweck |
|---|---|---|---|
| Verträge | STRAT-CTR | ~20 | Pydantic-Validierung der Strategic-Layer-Verträge |
| Achsen & ControlState | STRAT-AX | ~40 | Achsen-Zustandsmaschine, SL-AX-ATOMIC, Closure-Regeln |
| Kanzler & DTT | STRAT-KANZ | ~55 | Validierungspipeline, DTT, Blocklists, Konfliktdetektor |
| Königin & Briefing | STRAT-KOEN | ~25 | Constitutional Anchor, Briefing-Erzeugung, Sanitization |
| Symptom-Trigger & Signal | STRAT-SYM | ~15 | SymptomEvents, Signal-Semantik, SL-SIG-7a |
| End-to-End | STRAT-E2E | ~15 | Vollständiger Briefing → Directive → Policy-Zyklus |
| **Gesamt** | | **~170** | |

#### §4.7.2 STRAT-CTR — Vertrags-Tests (~20 Tests)

| Test-ID | Test | Erwartet |
|---|---|---|
| STRAT-CTR-01 | `ControlState` validiert mit gültigem Tupel | Pydantic-Validierung erfolgreich |
| STRAT-CTR-02 | `ControlState` mit ungültigem SafetyAxis-Wert | Validierungsfehler |
| STRAT-CTR-03 | `AxisTransition` mit gültigem `batch_id` | Pydantic-Validierung erfolgreich |
| STRAT-CTR-04 | `AxisTransition` mit ungültigem `axis`-Wert | Validierungsfehler |
| STRAT-CTR-05 | `StrategicBriefing` validiert mit gültigen Werten | Pydantic-Validierung erfolgreich |
| STRAT-CTR-06 | `StrategicBriefing.generated_by` ist nicht "KANZLER" | Validierungsfehler |
| STRAT-CTR-07 | `StrategicDirective` mit gültigem `intent` und `parameters` | Pydantic-Validierung erfolgreich |
| STRAT-CTR-08 | `StrategicDirective` mit `intent=UNLOCK_BUDGET` aber `parameters` vom Typ `NoActionParams` | Validierungsfehler (Discriminator-Mismatch) |
| STRAT-CTR-09 | `DirectiveParameters` discriminierte Union: alle 14 Intents validieren | Alle Submodelle validieren |
| STRAT-CTR-10 | `ResearchManifest` mit `created_by` ≠ Mensch | Validierungsfehler |
| STRAT-CTR-11 | `ResearchManifest` mit `approved_by` ≠ Mensch | Validierungsfehler |
| STRAT-CTR-12 | `HumanResponseFile` mit `answered_by` ≠ Mensch | Validierungsfehler |
| STRAT-CTR-13 | `HumanDirective` mit `created_by` ≠ Mensch | Validierungsfehler |
| STRAT-CTR-14 | `StrategicLayerConfig` mit gültigen Defaults | Pydantic-Validierung erfolgreich |
| STRAT-CTR-15 | `StrategicLayerConfig` mit `briefing_interval_cycles = 0` | Validierungsfehler |
| STRAT-CTR-16 | `SymptomEvent` mit gültigem `symptom_type` | Pydantic-Validierung erfolgreich |
| STRAT-CTR-17 | `ScientificHypothesis` mit leerem `hypothesis_text` | Validierungsfehler |
| STRAT-CTR-18 | `DimensionOnboardingRequest` mit `requires_physical_actuation=true` | Pydantic-Validierung erfolgreich |
| STRAT-CTR-19 | `CapabilityGapSignal` mit gültigen Werten | Pydantic-Validierung erfolgreich |
| STRAT-CTR-20 | `FinalScientificReport` mit `human_reviewed=false` | Pydantic-Validierung erfolgreich |

#### §4.7.3 STRAT-AX — Achsen & ControlState Tests (~40 Tests)

| Test-ID | Test | Erwartet |
|---|---|---|
| STRAT-AX-01 | ControlState-Tupel `(NORMAL, FUNDED, EXPLORATION, AUTONOMOUS)` ist gültig | Gültig |
| STRAT-AX-02 | ControlState-Tupel `(ESTOP_LOCKED, INCUBATING, EXPLORATION, AUTONOMOUS)` ist ungültig | Ungültig (§30.2) |
| STRAT-AX-03 | ControlState-Tupel `(SAFE_MODE, FUNDED, BOOTSTRAP, AUTONOMOUS)` ist ungültig | Ungültig (§30.2) |
| STRAT-AX-04 | ControlState-Tupel `(NORMAL, BUDGET_EXHAUSTED, EXPLORATION, AUTONOMOUS)` ist ungültig | Ungültig (§30.2) |
| STRAT-AX-05 | CT-1: `resource → BUDGET_EXHAUSTED` erzwingt `governance → AWAITING_HUMAN` | Closure feuert |
| STRAT-AX-06 | CT-2: `safety → ESTOP_LOCKED` + `resource=INCUBATING` → resource verlässt INCUBATING | Closure feuert |
| STRAT-AX-07 | CT-3: `safety → SAFE_MODE` unterdrückt pending ResearchAxis-Transitionen | ResearchAxis-Transition verworfen |
| STRAT-AX-08 | CT-4: `DimensionOnboardingRequest.status → ESCALATED` + `requires_physical_actuation=true` → `governance → AWAITING_HUMAN` | Closure feuert |
| STRAT-AX-09 | CT-5: `resource → PHYSICAL_WAIT` → `governance → AWAITING_HUMAN` | Closure feuert |
| STRAT-AX-10 | CT-6: `safety → SAFE_MODE` → `governance → AWAITING_HUMAN` | Closure feuert |
| STRAT-AX-11 | CT-6: `safety → ESTOP_LOCKED` → `governance → AWAITING_HUMAN` | Closure feuert |
| STRAT-AX-12 | CT-7: `resource: BUDGET_EXHAUSTED → FUNDED` via UNLOCK_BUDGET → `governance → AUTONOMOUS` | Closure feuert |
| STRAT-AX-13 | CT-8: `resource: PHYSICAL_WAIT → FUNDED` via CAPEX-Freigabe + Capability in Registry → `governance → AUTONOMOUS` | Closure feuert |
| STRAT-AX-14 | CT-8: `resource: PHYSICAL_WAIT → FUNDED` via CAPEX-Freigabe aber Capability NICHT in Registry → Closure feuert NICHT | Closure feuert nicht |
| STRAT-AX-15 | CT-9: `safety: SAFE_MODE → NORMAL` via SL-SAF-7 → `governance → AUTONOMOUS` | Closure feuert |
| STRAT-AX-16 | CT-10: `safety: ESTOP_LOCKED → NORMAL` via autorisierten Sicherheitsprozess → `governance → AUTONOMOUS` | Closure feuert |
| STRAT-AX-17 | SL-CT-SIMULTAN: CT-1 und CT-6 feuern gleichzeitig → nur EINE governance-Transition | Eine Transition |
| STRAT-AX-18 | SL-CT-SIMULTAN: CT-5 und CT-6 feuern gleichzeitig → nur EINE governance-Transition | Eine Transition |
| STRAT-AX-19 | SL-AX-ATOMIC: Zwei simultane Achsen-Transitionen werden atomar committet | Atomarer Commit |
| STRAT-AX-20 | SL-AX-ATOMIC: Ungültiger Ziel-Tupel nach Closure → gesamte Transition VERWORFEN | Fail-Closed |
| STRAT-AX-21 | SL-AX-ATOMIC: `batch_id` ist für alle Transitionen eines Commits identisch | Gleiche batch_id |
| STRAT-AX-22 | SL-AX-ATOMIC: Einzel-Transition hat `batch_id = transition_id` | Selbstreferenz |
| STRAT-AX-23 | Severity-Ordnung: SAFETY > RESOURCE bei gleichzeitigem Konflikt | SAFETY gewinnt |
| STRAT-AX-24 | Severity-Ordnung: RESOURCE > GOVERNANCE bei gleichzeitigem Konflikt | RESOURCE gewinnt |
| STRAT-AX-25 | Severity-Ordnung: GOVERNANCE > RESEARCH bei gleichzeitigem Konflikt | GOVERNANCE gewinnt |
| STRAT-AX-26 | ResearchAxis hat keinen Severity-Begriff → Audit + Eskalation bei Konflikt | Eskalation |
| STRAT-AX-27 | SR-A: `safety ∈ {SAFE_MODE, ESTOP_LOCKED}` → alle pending ResearchAxis-Transitionen verworfen | Verworfen |
| STRAT-AX-28 | Liveness-Watchdog: `(now − letzter Strategie-Zyklus) > liveness_watchdog_hours` → Heartbeat-Zyklus | Heartbeat |
| STRAT-AX-29 | `compute_phase_label()` erzeugt korrektes Etikett | z.B. "EXPLOITATION + PHYSICAL_WAIT" |
| STRAT-AX-30 | `compute_phase_label()` ist nicht authoritativ | Nicht authoritativ |
| STRAT-AX-31 | Parameter-Besitz-Matrix: ResearchAxis setzt `exploration_weight` | Erlaubt |
| STRAT-AX-32 | Parameter-Besitz-Matrix: ResourceAxis versucht `exploration_weight` zu setzen | SL-DEP-Lint Build-Fail |
| STRAT-AX-33 | Parameter-Besitz-Matrix: GovernanceAxis setzt `stall_detection_active` | Erlaubt |
| STRAT-AX-34 | Parameter-Besitz-Matrix: SafetyAxis setzt `safety_dispatch_allowed` | Erlaubt |
| STRAT-AX-35 | Closure-Iteration: `closure_max_iterations=5` wird nicht überschritten | Max 5 Iterationen |
| STRAT-AX-36 | Closure-Fixpunkt: Nach 2 Iterationen ist Fixpunkt erreicht | Fixpunkt |
| STRAT-AX-37 | ESTOP + Budget-Schwelle simultan: Gearbeitetes Beispiel aus §34.4 | Korrekter Ziel-Tupel |
| STRAT-AX-38 | `ControlStateLog` wird korrekt aktualisiert | `current_state` authoritativ |
| STRAT-AX-39 | Achsen-Transition wird im `ControlStateLog` protokolliert | Protokolliert |
| STRAT-AX-40 | Achsen-Transition mit `triggered_by=HAL` bei ESTOP | `triggered_by=HAL` |

#### §4.7.4 STRAT-KANZ — Kanzler & DTT Tests (~55 Tests)

| Test-ID | Test | Erwartet |
|---|---|---|
| STRAT-KANZ-01 | Validierungspipeline Stufe 1: Schema-Validierung erfolgreich | Weiter zu Stufe 2 |
| STRAT-KANZ-02 | Validierungspipeline Stufe 1: Schema-Validierung fehlgeschlagen | VETO("SCHEMA_INVALID") |
| STRAT-KANZ-03 | Validierungspipeline Stufe 2: `briefing_ref` existiert | Weiter zu Stufe 3 |
| STRAT-KANZ-04 | Validierungspipeline Stufe 2: `briefing_ref` existiert nicht | VETO("REF_NOT_FOUND") |
| STRAT-KANZ-05 | Validierungspipeline Stufe 3: Manifest-Prüfung erfolgreich | Weiter zu Stufe 3b |
| STRAT-KANZ-06 | Validierungspipeline Stufe 3: Manifest-Prüfung fehlgeschlagen | VETO("MANIFEST_VIOLATION") |
| STRAT-KANZ-07 | Validierungspipeline Stufe 3b: Weisungs-Prüfung erfolgreich | Weiter zu Stufe 3c |
| STRAT-KANZ-08 | Validierungspipeline Stufe 3b: Weisungs-Prüfung fehlgeschlagen | VETO("HUMAN_DIRECTIVE_VIOLATION") |
| STRAT-KANZ-09 | Validierungspipeline Stufe 3c: Target-Existenz erfolgreich | Weiter zu Stufe 4 |
| STRAT-KANZ-10 | Validierungspipeline Stufe 3c: Target ist LOCKED | VETO("TARGET_LOCKED") |
| STRAT-KANZ-11 | Validierungspipeline Stufe 4: Safety-/Injection-Prüfung erfolgreich | Weiter zu Stufe 5 |
| STRAT-KANZ-12 | Validierungspipeline Stufe 4: Injection erkannt | VETO + Audit |
| STRAT-KANZ-13 | Validierungspipeline Stufe 5: Budget-Prüfung erfolgreich | Weiter zu Stufe 6 |
| STRAT-KANZ-14 | Validierungspipeline Stufe 5: Budget negativ | VETO("BUDGET_NEGATIVE") |
| STRAT-KANZ-15 | Validierungspipeline Stufe 6b: Mode-Prüfung via ControlState erfolgreich | Weiter zu Stufe 6c |
| STRAT-KANZ-16 | Validierungspipeline Stufe 6b: Mode-Prüfung fehlgeschlagen | VETO("MODE_VIOLATION") |
| STRAT-KANZ-17 | Validierungspipeline Stufe 6c: Semantische Dedup erfolgreich | Weiter zu Stufe 7 |
| STRAT-KANZ-18 | Validierungspipeline Stufe 6c: Semantisches Duplikat erkannt | VETO("DUPLICATE_SEMANTIC") |
| STRAT-KANZ-19 | Validierungspipeline Stufe 7: Konflikt-Modus-Prüfung erfolgreich | ACCEPT |
| STRAT-KANZ-20 | Validierungspipeline Stufe 7: Konflikt-Modus aktiv | VETO("CONFLICT_MODE") |
| STRAT-KANZ-21 | DTT: NO_ACTION → keine Policy-Änderung | Zyklus protokolliert |
| STRAT-KANZ-22 | DTT: INITIAL_SWEEP → Topic PROPOSED→ACTIVE | Topic aktiviert |
| STRAT-KANZ-23 | DTT: PIVOT_DOMAIN → Scope-Check + Feasibility + Loop-Erkennung | Altes Topic ARCHIVED |
| STRAT-KANZ-24 | DTT: UNLOCK_BUDGET → immer Eskalation(BUDGET) | Eskalation erstellt |
| STRAT-KANZ-25 | DTT: ABORT_MISSION → immer ESCALATED | Eskalation erstellt |
| STRAT-KANZ-26 | DTT: HUMAN_ESCALATION(CAPEX) → `resource → PHYSICAL_WAIT` + `governance → AWAITING_HUMAN` | CT-5 + CT-6 feuern |
| STRAT-KANZ-27 | DTT: SET_RESEARCH_PHASE → löst ResearchAxis-Wechsel aus | Achsen-Transition |
| STRAT-KANZ-28 | DTT: INCREASE_DIAGNOSTIC → `diagnostic_budget += amount` | Budget erhöht |
| STRAT-KANZ-29 | DTT: CALIBRATE_TWIN bei nicht gedriftetem Twin | VETO("NO_DRIFT") |
| STRAT-KANZ-30 | Intent-Verfügbarkeit: UNLOCK_BUDGET bei `resource=FUNDED` | VETO("MODE_VIOLATION") |
| STRAT-KANZ-31 | Intent-Verfügbarkeit: UNLOCK_BUDGET bei `resource=BUDGET_EXHAUSTED` | Intent verfügbar |
| STRAT-KANZ-32 | Intent-Verfügbarkeit: SET_RESEARCH_PHASE bei `resource=BUDGET_EXHAUSTED` | Blockiert |
| STRAT-KANZ-33 | Intent-Verfügbarkeit: SET_RESEARCH_PHASE bei `resource=PHYSICAL_WAIT` | Blockiert |
| STRAT-KANZ-34 | Intent-Verfügbarkeit: SET_RESEARCH_PHASE bei `resource=FUNDED` | Verfügbar |
| STRAT-KANZ-35 | Intent-Verfügbarkeit: INCREASE_DIAGNOSTIC bei `safety=SAFE_MODE` ohne Quarantäne | Blockiert |
| STRAT-KANZ-36 | Intent-Verfügbarkeit: INCREASE_DIAGNOSTIC bei `safety=SAFE_MODE` mit Quarantäne-Zone | Erlaubt (BF-15) |
| STRAT-KANZ-37 | Intent-Verfügbarkeit: INCREASE_DIAGNOSTIC bei `safety=SAFE_MODE` mit Quarantäne aber `amount > diagnostic_budget_default` | Blockiert |
| STRAT-KANZ-38 | Intent-Verfügbarkeit: Alle Intents bei `safety=ESTOP_LOCKED` außer NO_ACTION und HUMAN_ESCALATION | Blockiert |
| STRAT-KANZ-39 | Konfliktdetektor: GOVERNANCE-VETO zählt als Konflikt | Konflikt gezählt |
| STRAT-KANZ-40 | Konfliktdetektor: BENIGN-VETO zählt nicht als Konflikt | Kein Konflikt |
| STRAT-KANZ-41 | Konfliktdetektor: 2 Konflikte in `conflict_window_cycles` → URGENT + DEADLOCK-Eskalation | Eskalation |
| STRAT-KANZ-42 | Konfliktdetektor: Konflikt-Modus → nur NO_ACTION/HUMAN_ESCALATION angenommen | Andere → VETO |
| STRAT-KANZ-43 | NO_ACTION-Stall: `no_action_stall_limit` aufeinanderfolgende NO_ACTION → URGENT | URGENT |
| STRAT-KANZ-44 | NO_ACTION-Stall: `stall_detection_active=false` → Stall-Counter wird NICHT erhöht | Kein URGENT |
| STRAT-KANZ-45 | NO_ACTION-Stall: Während AWAITING_HUMAN → Stall-Überwachung suspendiert | Kein URGENT |
| STRAT-KANZ-46 | SL-SAF-7: SAFE_MODE → NORMAL nur via `HumanResponseFile.unlock_decision` mit `scope_refs=["GLOBAL_SAFETY"]` | Übergang |
| STRAT-KANZ-47 | SL-SAF-7: SAFE_MODE → NORMAL ohne `scope_refs=["GLOBAL_SAFETY"]` | Kein Übergang |
| STRAT-KANZ-48 | SL-BUD-1: `used_cycles += 1 × resource.burn_rate_multiplier` | Budget brennt |
| STRAT-KANZ-49 | SL-BUD-1: `burn_rate_multiplier=0` in PHYSICAL_WAIT | Budget brennt nicht |
| STRAT-KANZ-50 | SL-BUD-1: `burn_rate_multiplier=0` in BUDGET_EXHAUSTED | Budget brennt nicht |
| STRAT-KANZ-51 | SL-BUD-1a: Laufende Questor-Pakete bei BUDGET_EXHAUSTED → nicht beeinflusst | Paket läuft weiter |
| STRAT-KANZ-52 | SL-URG-2: `remaining_cycles ≤ budget_unlock_threshold_fraction` → URGENT + Eskalation(BUDGET) | Eskalation |
| STRAT-KANZ-53 | SL-BRF-9: `provisional=true` bei trunkiertem Briefing | `royal_log_entry.provisional=true` |
| STRAT-KANZ-54 | SL-BRF-9: `provisional=false` bei nicht trunkiertem Briefing | `royal_log_entry.provisional=false` |
| STRAT-KANZ-55 | Semantische Dedup: `semantic_directive_id = sha256(intent + target_ref + canonical_json(parameters))` | Deterministisch |

#### §4.7.5 STRAT-KOEN — Königin & Briefing Tests (~25 Tests)

| Test-ID | Test | Erwartet |
|---|---|---|
| STRAT-KOEN-01 | Constitutional Anchor: Königin erhält exakt 3 Kontextblöcke | 3 Blöcke |
| STRAT-KOEN-02 | Constitutional Anchor: CONSTITUTIONAL MEMORY enthält mission_goal, hard_constraints, soft_preferences | Vorhanden |
| STRAT-KOEN-03 | Constitutional Anchor: STATELESS BRIEFING enthält keinen `security_mode` | Nicht vorhanden |
| STRAT-KOEN-04 | Constitutional Anchor: STATELESS BRIEFING enthält keine Hybrid-Referenzen | Nicht vorhanden |
| STRAT-KOEN-05 | Constitutional Anchor: STATELESS BRIEFING enthält keinen Roh-`metric_vector` | Nicht vorhanden |
| STRAT-KOEN-06 | Constitutional Anchor: ANCHOR enthält aktive HUMAN_OVERRIDE-Einträge zuerst | HUMAN_OVERRIDE zuerst |
| STRAT-KOEN-07 | Constitutional Anchor: ANCHOR enthält letzte `royal_log_anchor_depth=3` Direktiven | 3 Direktiven |
| STRAT-KOEN-08 | Constitutional Anchor: Kein persistenter Gesprächsverlauf | Stateless |
| STRAT-KOEN-09 | Constitutional Anchor: Menschliche Weisungen überschreiben Königin-Direktiven | Mensch gewinnt |
| STRAT-KOEN-10 | Constitutional Anchor: LLM-Fehler → Policy bleibt unverändert | Policy unverändert |
| STRAT-KOEN-11 | Constitutional Anchor: Nach `max_consecutive_llm_failures` → Eskalation | Eskalation |
| STRAT-KOEN-12 | Briefing-Erzeugung: `briefing_id` ist die einzige Zyklen-ID | Keine `zyklus_id` |
| STRAT-KOEN-13 | Briefing-Erzeugung: `generated_by` ist immer "KANZLER" | KANZLER |
| STRAT-KOEN-14 | Briefing-Erzeugung: Trunkierungspriorität v2 wird angewendet | Korrekte Priorität |
| STRAT-KOEN-15 | Briefing-Erzeugung: Twins mit `calibration_required` fallen nie in Restklasse | Nie Restklasse |
| STRAT-KOEN-16 | Briefing-Erzeugung: Quarantäne → `[REDACTED:QUARANTINE]` | Redacted |
| STRAT-KOEN-17 | Briefing-Erzeugung: Gesamt-Kontext-Budget wird eingehalten | `max_total_context_chars` |
| STRAT-KOEN-18 | Briefing-Erzeugung: Layer 3 (Anchor) wird nie trunkiert | Nie trunkiert |
| STRAT-KOEN-19 | Briefing-Erzeugung: `active_hypothesis_refs` (Top-N) vorhanden | Vorhanden |
| STRAT-KOEN-20 | Briefing-Erzeugung: `in_flight_packages` vorhanden | Vorhanden |
| STRAT-KOEN-21 | Briefing-Typ: BOOTSTRAP bei Mission-Start | BOOTSTRAP |
| STRAT-KOEN-22 | Briefing-Typ: PERIODIC im Normalbetrieb | PERIODIC |
| STRAT-KOEN-23 | Briefing-Typ: URGENT bei SL-URG-1 Trigger | URGENT |
| STRAT-KOEN-24 | Briefing-Typ: FINAL bei Topic-SATURATION | FINAL |
| STRAT-KOEN-25 | SL-URG-3: URGENT-Nachzügler während Cooldown → ins nächste PERIODIC gemerged | Gemerged |

#### §4.7.6 STRAT-SYM — Symptom-Trigger & Signal Tests (~15 Tests)

| Test-ID | Test | Erwartet |
|---|---|---|
| STRAT-SYM-01 | SymptomEvent(INITIAL_SWEEP) bei Bootstrap | SymptomEvent erzeugt |
| STRAT-SYM-02 | SymptomEvent(WEISSRAUM) bei Zone gemäß SL-DEF-2 | SymptomEvent erzeugt |
| STRAT-SYM-03 | SymptomEvent(FRACTURE_GAP) bei `fracture_score ≥ quarantine_threshold` | SymptomEvent erzeugt |
| STRAT-SYM-04 | SymptomEvent(SATURATION) bei Topic-StopCondition SATURATION_CYCLES | SymptomEvent erzeugt |
| STRAT-SYM-05 | SymptomEvent(TWIN_DRIFT) bei `tolerance_breached=true` | SymptomEvent erzeugt |
| STRAT-SYM-06 | SymptomEvent(CAPABILITY_GAP_FEEDBACK) bei CapabilityGapSignal | SymptomEvent erzeugt |
| STRAT-SYM-07 | SymptomEvent(DIMENSION_GAP) bei blockierter approved=false-Dimension | SymptomEvent erzeugt |
| STRAT-SYM-08 | SymptomEvent(REPLICATE_DIVERGENCE) bei SL-SIG-5 | SymptomEvent erzeugt |
| STRAT-SYM-09 | SymptomEvent(QUARANTINE_BLOCK) bei blockierter Idee in quarantinierter Zone | SymptomEvent erzeugt |
| STRAT-SYM-10 | SL-SIG-7a: Overfitting (`train_val_gap > threshold`) → ⬜ CONSTRAINT_NEAR_MISS | Kein 🟨 |
| STRAT-SYM-11 | SL-SIG-7a: Overfitting wiederholt (≥ `min_confirmations` in `conflict_window_cycles`) → MetricConstraint-Fracture | Fracture |
| STRAT-SYM-12 | SL-SIG-7a: "Parameter-äquivalent" mit Float-Toleranz (`metric_tolerance_multiplier`) | Toleranz angewendet |
| STRAT-SYM-13 | SL-SIG-1: `confirms_expectation=False` → 🟨 CONTRADICTION | 🟨 |
| STRAT-SYM-14 | SL-SIG-1: `confirms_expectation=True` + `konfidenz ≥ 0.8` → 🟩 | 🟩 |
| STRAT-SYM-15 | SL-SIG-1: `confirms_expectation=None` → ⬜ EXPLORATORY_COVERAGE | ⬜ |

#### §4.7.7 STRAT-E2E — End-to-End Tests (~15 Tests)

| Test-ID | Test | Erwartet |
|---|---|---|
| STRAT-E2E-01 | Vollständiger Zyklus: Briefing → Directive → Validierung → DTT → Policy-Wirkung | Zyklus abgeschlossen |
| STRAT-E2E-02 | Missions-Bootstrap: Manifest → BOOTSTRAP-Briefing → INITIAL_SWEEP → Topic ACTIVE | Bootstrap erfolgreich |
| STRAT-E2E-03 | Missions-Bootstrap: Manifest-Intake fail-closed bei ungültigem Manifest | REJECT |
| STRAT-E2E-04 | Missions-Bootstrap: Nach `bootstrap_retry_limit=3` invaliden INITIAL_SWEEP → TEMPLATE_GAP-Eskalation | Eskalation |
| STRAT-E2E-05 | CAPEX-Flow: CapabilityGapSignal → CAPEX-Eskalation → PHYSICAL_WAIT → AWAITING_HUMAN → Mensch genehmigt → Capability in Registry → FUNDED → AUTONOMOUS | Vollständiger Flow |
| STRAT-E2E-06 | SAFE_MODE-Flow: SafetyConstraint → SAFE_MODE → AWAITING_HUMAN → Diagnose → SL-SAF-7 → NORMAL → AUTONOMOUS | Vollständiger Flow |
| STRAT-E2E-07 | ESTOP-Flow: HAL ESTOP → ESTOP_LOCKED → AWAITING_HUMAN → Sicherheitsprozess → NORMAL → AUTONOMOUS | Vollständiger Flow |
| STRAT-E2E-08 | BUDGET_EXHAUSTED-Flow: Budget-Schwelle → BUDGET_EXHAUSTED → AWAITING_HUMAN → UNLOCK_BUDGET → FUNDED → AUTONOMOUS | Vollständiger Flow |
| STRAT-E2E-09 | Quarantäne-Diagnostik-Flow: Fracture → Quarantäne → SAFE_MODE → INCREASE_DIAGNOSTIC (BF-15) → Diagnose → Exit | Vollständiger Flow |
| STRAT-E2E-10 | Overfitting-Flow: CONSTRAINT_NEAR_MISS → wiederholt → MetricConstraint-Fracture → Vordenker erhält Symptom | Vollständiger Flow |
| STRAT-E2E-11 | Simultane Multi-Achsen-Transition: ESTOP + Budget-Schwelle + SATURATION gleichzeitig | SL-AX-ATOMIC korrekt |
| STRAT-E2E-12 | Dimensions-Eskalation-Flow: Vordenker schlägt Dimension vor → CT-4 → AWAITING_HUMAN → Mensch genehmigt → AUTONOMOUS | Vollständiger Flow |
| STRAT-E2E-13 | Topic-Archivierung-Flow: StopCondition REACHED → SATURATED → FINAL-Briefing → ReportFacts → FinalScientificReport → ARCHIVED | Vollständiger Flow |
| STRAT-E2E-14 | HumanDirective-Override: Mensch sendet HumanDirective → Königin-Direktive wird überschrieben | Mensch gewinnt |
| STRAT-E2E-15 | SymptomEvent-Verlustschutz: SymptomEvent vor Queue-Übergabe persistent → At-Least-Once | Nicht verloren |

---

## ÄNDERUNG 6: §8.1 aktualisieren (Test-Ausführungsstrategie)

**ERGÄNZE** nach PHASE 4 in §8.1:

```
PHASE 4b: Strategic-Layer-Tests (~12 Minuten)
   → pytest -m strat
```

**ERSETZE** PHASE 8:

```
PHASE 8: Vollständige Suite (~67 Minuten)
   → pytest --cov=src/questor --cov=src/gremium --cov=src/strategy
```

---

## ÄNDERUNG 7: §8.2 aktualisieren (Test-Gates)

**ERGÄNZE** nach GATE-ATLAS in §8.2:

| Gate | Bedingung |
|---|---|
| GATE-STRAT | Alle Strategic-Layer-Tests bestehen (Suite STRAT) |

---

## ÄNDERUNG 8: §9 aktualisieren (Akzeptanzkriterien)

**ERGÄNZE** am Ende der Tabelle in §9:

| # | Kriterium | CHARTER-Referenz |
|---|---|---|
| 41 | Alle Strategic-Layer-Tests bestehen (Suite STRAT) | — |
| 42 | Strategic-Layer-Phasen S1–S3 abgeschlossen | — |
| 43 | ControlState wird atomar verwaltet (SL-AX-ATOMIC) | CHARTER §SR-55 |
| 44 | Alle 10 Closure-Regeln (CT-1..CT-10) funktionieren | — |
| 45 | Intent-Verfügbarkeit wird korrekt durch Blocklists gesteuert | — |
| 46 | SAFE_MODE → NORMAL nur via menschliche Freigabe (SL-SAF-7) | CHARTER §SR-11 |
| 47 | ESTOP_LOCKED → NORMAL nur via autorisierten Sicherheitsprozess | CHARTER §SR-05 |
| 48 | Königin erhält exakt 3 Kontextblöcke (Constitutional Anchor) | CHARTER §SR-13 |
| 49 | Kein security_mode im Briefing | CHARTER §SR-29 |
| 50 | Questor und HAL kennen keine Strategic-Layer-Verträge | CHARTER §SR-04 |

---

## ÄNDERUNG 9: §12 aktualisieren (Protokollformat)

**ERGÄNZE** am Ende der Protokollformate in §12:

```
[STRAT-TEST STRAT-CTR-XX] [MODUL] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
[STRAT-TEST STRAT-AX-XX] [MODUL] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
[STRAT-TEST STRAT-KANZ-XX] [MODUL] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
[STRAT-TEST STRAT-KOEN-XX] [MODUL] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
[STRAT-TEST STRAT-SYM-XX] [MODUL] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
[STRAT-TEST STRAT-E2E-XX] [MODUL] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
```

---

## ÄNDERUNG 10: §13 aktualisieren (Zusammenfassender Bericht)

**ERGÄNZE** in §13.3 Ergebnisse:

```
STRAT-CTR GESAMT: X/~20 BESTANDEN
STRAT-AX GESAMT: X/~40 BESTANDEN
STRAT-KANZ GESAMT: X/~55 BESTANDEN
STRAT-KOEN GESAMT: X/~25 BESTANDEN
STRAT-SYM GESAMT: X/~15 BESTANDEN
STRAT-E2E GESAMT: X/~15 BESTANDEN
STRAT GESAMT: X/~170 BESTANDEN
GESAMT: X/~711 BESTANDEN
```

---

## ÄNDERUNG 11: §11 aktualisieren (Kritische Warnungen)

**ERGÄNZE** am Ende von §11:

### §11.19 Kein ControlState ohne SL-AX-ATOMIC
Wenn ein Test erwartet, dass Achsen-Transitionen nicht atomar committet werden, ist der Test falsch.
→ Siehe GREMIUM_STRATEGY.md §34.

### §11.20 Keine Closure-Regel ohne Severity-Ordnung
Wenn ein Test erwartet, dass Closure-Regeln die Severity-Ordnung ignorieren, ist der Test falsch.
→ Siehe GREMIUM_STRATEGY.md §34.1.

### §11.21 Kein SAFE_MODE-Exit ohne menschliche Freigabe
Wenn ein Test erwartet, dass SAFE_MODE → NORMAL automatisch erfolgt, ist der Test falsch.
→ Siehe GREMIUM_STRATEGY.md §13 (SL-SAF-7).

### §11.22 Kein ESTOP-Reset durch Questor oder LLM
Wenn ein Test erwartet, dass Questor oder LLM einen ESTOP zurücksetzen kann, ist der Test falsch.
→ Siehe CHARTER §SR-05.

### §11.23 Keine Achsen-Parameter direkt setzen
Wenn ein Test erwartet, dass eine Regel Achsen-Parameter direkt setzt (statt über ControlState zu lesen), ist der Test falsch.
→ Siehe GREMIUM_STRATEGY.md §31 (Single Ownership).

### §11.24 Kein security_mode im Briefing
Wenn ein Test erwartet, dass `security_mode` im StrategicBriefing enthalten ist, ist der Test falsch.
→ Siehe CHARTER §SR-29.

---

## ÄNDERUNG 12: §15 aktualisieren (Dokumentenhierarchie)

**ERGÄNZE** am Ende von §15:

Dieses Dokument referenziert zusätzlich:
- `specs/GREMIUM_STRATEGY.md` für Strategic-Layer-Regeln (Achsen, ControlState, Kanzler/Königin)

---

## ÄNDERUNG 13: §14 aktualisieren (Fehlerbericht)

**ERGÄNZE** am Ende der Protokollformate in §14:

```
[STRAT-TEST STRAT-XXX-XX]
Komponente: [Komponente]
Problem: [Problem]
Erwartetes Verhalten: [Erwartung]
Beobachtetes Verhalten: [Beobachtung]
Wahrscheinliche Ursache: [Ursache]
Empfohlene Korrektur: [Korrektur]
Priorität: Blocker | Hoch | Mittel | Niedrig
```

---

## ÄNDERUNG 14: Test-Fixture-Struktur erweitern

**ERGÄNZE** in §5.1:

```
tests/
    └── test_strategy/
        ├── fixtures/
        │   ├── control_states/
        │   │   ├── normal_funded_exploration_autonomous.json
        │   │   ├── estop_locked_budget_exhausted.json
        │   │   ├── safe_mode_awaiting_human.json
        │   │   └── physical_wait_awaiting_human.json
        │   ├── briefings/
        │   │   ├── bootstrap_briefing.json
        │   │   ├── periodic_briefing.json
        │   │   ├── urgent_briefing.json
        │   │   └── final_briefing.json
        │   ├── directives/
        │   │   ├── initial_sweep_directive.json
        │   │   ├── unlock_budget_directive.json
        │   │   ├── pivot_domain_directive.json
        │   │   └── no_action_directive.json
        │   ├── manifests/
        │   │   ├── valid_manifest.json
        │   │   └── invalid_manifest.json
        │   ├── human_responses/
        │   │   ├── unlock_budget_response.json
        │   │   ├── capex_approval_response.json
        │   │   └── safety_unlock_response.json
        │   └── symptom_events/
        │       ├── initial_sweep_event.json
        │       ├── fracture_gap_event.json
        │       ├── twin_drift_event.json
        │       └── capability_gap_event.json
        ├── mocks/
        │   ├── mock_kanzler.py
        │   ├── mock_koenigin_llm.py
        │   ├── mock_control_state_manager.py
        │   └── mock_atlas.py
        └── conftest.py
```

---

## ZUSAMMENFASSUNG DER ÄNDERUNGEN

| Änderung | Ziel | Aktion | Umfang |
|---|---|---|---|
| 1 | Kopfzeile | ERSETZE | 6 Zeilen |
| 2 | §0.2 | NEU | ~20 Zeilen |
| 3 | §2.2 | ERSETZE | ~12 Zeilen |
| 4 | §2.3 | ERSETZE | ~15 Zeilen |
| 5 | §4.7 | NEU | ~250 Zeilen |
| 6 | §8.1 | ERGÄNZE | ~3 Zeilen |
| 7 | §8.2 | ERGÄNZE | 1 Zeile |
| 8 | §9 | ERGÄNZE | ~10 Zeilen |
| 9 | §12 | ERGÄNZE | ~6 Zeilen |
| 10 | §13 | ERGÄNZE | ~7 Zeilen |
| 11 | §11 | ERGÄNZE | ~20 Zeilen |
| 12 | §15 | ERGÄNZE | ~2 Zeilen |
| 13 | §14 | ERGÄNZE | ~8 Zeilen |
| 14 | §5.1 | ERGÄNZE | ~40 Zeilen |
| **Gesamt** | | | **~400 Zeilen** |

---

## NACHWEIS: CHARTER-KONFORMITÄT

| CHARTER-Regel | Umsetzung |
|---|---|
| SR-04 | Questor und HAL kennen keine Strategic-Layer-Verträge. In STRAT-E2E-15 geprüft. |
| SR-05 | ESTOP-Reset nur durch autorisierten Sicherheitsprozess. In STRAT-AX-16 und STRAT-E2E-07 geprüft. |
| SR-11 | SAFE_MODE-Exit nur durch menschliche Freigabe. In STRAT-KANZ-46 und STRAT-E2E-06 geprüft. |
| SR-13 | Königin ist LLM-Advisor. Kanzler ist deterministisch. In STRAT-KOEN-01..11 geprüft. |
| SR-29 | Kein security_mode im Briefing. In STRAT-KOEN-03 geprüft. |
| SR-55 | SL-AX-ATOMIC nutzt atomare Dateioperationen. In STRAT-AX-19..22 geprüft. |