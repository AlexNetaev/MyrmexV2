# STANDALONE STRUCTURE GREMIUM — v0.3.0 (Delta gegen v0.2.0)

```
🏛️ STANDALONE STRUCTURE GREMIUM — COGNITIVE OBSERVATORY
| Feld | Wert |
| --- | --- |
| Dateiname | specs/standalone_structure_gremium_v0.3.0.md |
| Version | 0.3.0 |
| Status | ÄNDERUNGSANTRAG STRATEGIC-LAYER-2.2.0 (Delta, nicht eigenständig) |
| Basis | v0.2.0 (dieses Dokument wird ZUSAMMEN mit v0.2.0 eingelesen) |
| Testgrundlage | 3 Dry-Test-Kampagnen (PhotoKat-CO₂ / CO₂-to-Methanol / PhotoAryl-85): 323 Tests, 227 Funde, 22 konvergente Funde (KV-01..KV-22) |
| Baut auf | CHARTER 1.0.0, CONTRACTS 1.1.0-atlas-hyb.1, GREMIUM 1.1.0-atlas-hyb.1, DIGITAL-TWIN-SEM-1.0.0 |
| Konfliktregel | CHARTER > CONTRACTS > v0.2.0+v0.3.0 (bei Delta-Widerspruch: v0.3.0 > v0.2.0) |
```

---

## §0 Zweck, Leseregel und Geltung

### §0.1 Zweck
Dieses Dokument ist ein **Delta-Änderungsantrag** gegen v0.2.0. Es behebt die 22 kampagnen-konvergenten Funde (KV-01..KV-22) und deren 227 Einzelfunde aus drei unabhängigen Dry-Test-Kampagnen. Es ist **nicht eigenständig lauffähig**, sondern wird zusammen mit v0.2.0 eingelesen.

### §0.2 Leseregel (bindend für Tests)
1. v0.2.0 bleibt Grundtext. Dieses Dokument überschreibt nur die ausdrücklich als **ERSETZT** oder **GEÄNDERT** markierten Regeln/Abschnitte.
2. Als **NEU** markierte Regeln, Verträge, Schritte und Parameter ergänzen v0.2.0.
3. Bei Widerspruch zwischen v0.2.0 und v0.3.0 gilt v0.3.0. Bei Widerspruch zur CHARTER oder zu CONTRACTS gilt das jeweils höherrangige Dokument (CHARTER > CONTRACTS > dieses Delta).
4. Jede Änderung trägt eine Delta-ID `Δ-xx` und referenziert die ersetzte/neue Regel sowie die behobenen Funde.

### §0.3 Konvergenz-Funde als Änderungsanlass
| KV | Konvergenter Fund | Behebungs-Abschnitt |
|---|---|---|
| KV-01/KV-20 | HUMAN_OVERRIDE nicht deterministisch durchsetzbar | §1 |
| KV-02 | Lessons-Learned kollidiert mit SL-MAN-1 | §4 |
| KV-03 | Zyklus-/Zeit-/Budgetmodell unvollständig | §2 |
| KV-04 | Manifest-Intake nicht fail-closed | §3 |
| KV-05 | Intent-Parameter nicht schema-erzwungen | §3.4 |
| KV-06/KV-07/KV-08 | Twin-Paarung zu lose / ε+Toleranz undefiniert / Trunkierung | §6 |
| KV-09 | Schatten-Variablen-Check scheitert still | §3.3 |
| KV-10 | Replikation unterversorgt | §8 |
| KV-11 | HOLD_STRATEGY lückenhaft | §9 |
| KV-12 | In-flight-Pakete unreguliert | §10 |
| KV-13 | §23-Konfiglücken | §14 |
| KV-14 | Entsperr-/Exit-Pfade fehlen | §5 |
| KV-15 | Dedup nur pro Briefing | §11.2 |
| KV-16 | Tote/inkonsistente Vertragsfelder | §17 |
| KV-17 | First-Order-Scan Schicht-4 fehlt | §12 |
| KV-18 | NO_ACTION-Zwang nicht mechanisch | §11.3 |
| KV-19 | EscalationType unvollständig | §11.6 |
| KV-21 | Initiale Zonen-Erzeugung undefiniert | §3.6 |
| KV-22 | Hypothese→Erwartungs-Brücke fehlt | §7 |

---

## §1 Mensch-Schnittstelle: strukturierte Weisungen (behebt KV-01, KV-20; K-01)

> **ERSETZT** v0.2.0 §15.1 (Eskalationskanal) und ergänzt §6.9, §7.1.
> **Wurzel:** dateibasierter Freitext trifft auf rein deterministischen Kanzler (SL-GATE-1). Menschliche Absichten waren nicht hart durchsetzbar.

### §1.1 NEU: Vertrag `HumanResponseFile` (Antwort auf Eskalation)
```python
class HumanResponseDecision(str, Enum):
    APPROVE = "APPROVE"; REJECT = "REJECT"
    PARTIAL = "PARTIAL"; DEFER = "DEFER"

class ManifestConstraintDelta(BaseModel):
    action: Literal["ADD", "REMOVE", "MODIFY"]
    constraint: Optional[ManifestConstraint] = None   # bei ADD/MODIFY
    constraint_id: Optional[str] = None               # bei REMOVE/MODIFY

class HumanResponseFile(BaseModel):
    response_id: str
    escalation_id: str                     # Pflicht: referenziert offene Eskalation
    decision: HumanResponseDecision
    amount_granted: Optional[int] = None   # bei PARTIAL/APPROVE von BUDGET
    constraints_delta: list[ManifestConstraintDelta] = []
    unlock_decision: Optional[UnlockDecision] = None   # für SAFETY_EVENT, §5
    scope_refs: list[str] = []
    free_note: str = ""                    # Scan; wirkt NUR als Anchor, nie hart
    answered_by: str                       # immer Mensch
    answered_at: str
```
**SL-ESC-5 (NEU):** Antwortdateien müssen gegen dieses Schema validieren. Unparsbare Datei → Kanzler schreibt Status `PARSE_REJECTED`, erzeugt Erinnerungs-Template, **kein stilles Interpretieren**. Teilgenehmigung ist über `decision=PARTIAL` + `amount_granted`/`constraints_delta` modelliert (behebt T4-F-67, PROB-38).

### §1.2 NEU: Vertrag `HumanDirective` (strukturiertes Override)
```python
class HumanDirective(BaseModel):
    directive_id: str
    constraint_deltas: list[ManifestConstraintDelta] = []
    topic_freezes: list[str] = []            # topic_ids
    dimension_freezes: list[str] = []
    valid_for_cycles: Optional[int] = None   # None = bis Missionsende
    note: str = ""                           # Scan; nur Anchor
    created_by: str                          # immer Mensch
    created_at: str
    expires_at_cycle: Optional[int] = None   # deterministisch aus valid_for_cycles
```
**SL-MAN-8 (NEU):**
- (a) Freitext-Overrides werden durch `HumanDirective` ersetzt. Nur der **maschinenlesbare Teil** (`constraint_deltas`, `topic_freezes`, `dimension_freezes`) ist hart durchsetzbar. `note` wirkt ausschließlich als Anchor.
- (b) Geht eine Freitext-only-Weisung ein, markiert der Kanzler sie `structured=false` (nur beratend) und quittiert mit einem Template zur strukturierten Erfassung. **Dokumentiertes Restrisiko.**
- (c) Zeitlichkeit: `valid_for_cycles`/`expires_at_cycle` beendet die Wirksamkeit deterministisch (behebt T4-F-83, F-61).

### §1.3 NEU: Validierungsschritt 3b „Weisungs-Prüfung"
> **ERGÄNZT** v0.2.0 §7.1 zwischen Schritt 3 und 4.

Aktive `HumanDirective`-Einträge werden gegen `target_ref`/`parameters` der Direktive geprüft. Verstoß → `VETO("HUMAN_DIRECTIVE_VIOLATION")` (behebt PROB-33, F-62, T4-F-103-Teil).

### §1.4 NEU: Briefing-Kennzeichnung gesperrter Ziele
**SL-BRF-7 (NEU):** LOCKED-/QUARANTINE-Zonen erscheinen im Briefing mit `addressable=false`. Direktiven darauf werden in Schritt 3c abgewiesen, ohne den Konfliktdetektor zu belasten (behebt PROB-30, T4-F-41-Teil).

---

## §2 Zyklus-, Zeit- und Budgetmodell (behebt KV-03; K-02)

> **ERSETZT** v0.2.0 SL-DEF-1; **ERGÄNZT** §6.2, §6.9, §8.2.
> **Wurzel:** zirkuläre Zyklus-Definition, kein Tick-Geber, keine Wall-Clock, kein Verbrauchsmodell.

### §2.1 SL-DEF-3 / SL-DEF-4 (NEU): Zwei Zyklusbegriffe
- **SL-DEF-3 Pipeline-Takt:** ereignisgetrieben; jedes verarbeitete Ergebnis/Paket schreitet fort. Treibt Archivar/Kartograph/Atlas.
- **SL-DEF-4 Strategie-Zyklus:** der Briefing-Regelkreis aus SL-DEF-1. `briefing_interval_cycles` zählt **Strategie-Zyklen**. Ein Strategie-Zyklus wird ausgelöst durch `cycle_trigger ∈ {TIME, EVENT_COUNT, MANUAL}` (Config). `zyklus_id` wird **abgeschafft**; `briefing_id` ist die einzige, fortlaufende Zyklen-ID (behebt F-73, F-74, T4-F-14).

### §2.2 NEU: Vertrag `TimeService` (Wall-Clock-Quelle)
```python
class TimeService(BaseModel):
    source: str                      # z.B. "ntp", "host_clock"
    now_iso: str
    mission_start_iso: str
```
**SL-DEF-5 (NEU):** Alle `*_days`-Parameter (`cold_storage_window_days`) und alle `valid_until`-/Timeout-Auswertungen nutzen ausschließlich `TimeService`. Alle `*_cycles`-Parameter nutzen den Strategie-Zyklus (SL-DEF-4). Eine Vermischung ist unzulässig (behebt F-87).

### §2.3 Budget-Volldefinition
> **ERSETZT** die informelle Semantik in v0.2.0 §6.9.

**SL-BUD-1..4 (NEU):**
- **SL-BUD-1:** `used_cycles += 1` je abgeschlossenem Strategie-Zyklus.
- **SL-BUD-2:** `remaining_cycles = total_cycles − used_cycles − reserved_cycles`.
- **SL-BUD-3:** Bei Freigabe-Umsetzung (`UNLOCK_BUDGET` bestätigt) wird `reserved_cycles → used_cycles` verrechnet.
- **SL-BUD-4:** `burn_rate_per_cycle` und `estimated_completion_cycle` erhalten Formeln oder werden gestrichen:
  - `burn_rate_per_cycle = used_cycles / max(elapsed_cycles, 1)`
  - `estimated_completion_cycle = used_cycles + ceil(remaining_progress / progress_rate)`; ist `progress_rate ≤ 0` → `None`.
  (behebt T4-F-64/65/66, F-72)

### §2.4 NEU: Zustand `BUDGET_EXHAUSTED`
**SL-URG-2 (NEU):** Fällt `remaining_cycles ≤ 0` oder unter `budget_unlock_threshold_fraction`, erzeugt der Kanzler zwingend: URGENT-Briefing + `HumanEscalationRecord(BUDGET)` + DecisionOption. Zustandsautomat: `ACTIVE → BUDGET_EXHAUSTED` (nur Mensch hebt per `UNLOCK_BUDGET`-Bestätigung auf). Ohne Freigabe verhält sich das System wie `HOLD_STRATEGY` (behebt T4-F-63, F-71).

### §2.5 NEU: URGENT-Trigger-Ergänzungen (SL-URG-1 erweitert)
Zusätzlich zu v0.2.0 §8.2:
- `questor_health_status == DEAD`
- `remaining_cycles ≤ budget_unlock_threshold_fraction` (BUDGET_EXHAUSTED)
- Mission ohne aktives Topic (mind. 1 Zyklus, `total_active_topics == 0`)
(behebt F-86, T4-F-90, F-71)

---

## §3 Bootstrap-Härtung & Manifest-Ausdrucksfähigkeit (behebt KV-04, KV-05, KV-21; K-03)

> **ERGÄNZT** v0.2.0 §4 (SL-BOOT), §6.1.

### §3.1 SL-BOOT-0 (NEU): Manifest-Intake-Validierung
Vor SL-BOOT-1-Annahme prüft der Kanzler fail-closed:
1. `created_by == MENSCH` **und** `approved_by == MENSCH`, sonst REJECT (behebt PROB-03, F-37).
2. `value` XOR `range` je Operator (behebt T4-F-03).
3. Jeder `dimension_ref` referenziert eine in `initial_dimensions` deklarierte Dimension (behebt T4-F-07).
4. Kategorische Constraints (`enforcement=EXCLUSION` mit `categories`) müssen `categories` nicht-leer enthalten.
5. `valid_until` (falls gesetzt) liegt via TimeService in der Zukunft (behebt T4-F-11/F-12).
Jeder Verstoß → REJECT mit begründetem Template; kein Bootstrap.

### §3.2 SL-MAN-9 (NEU): Operator×Enforcement-Matrix
`enforcement=EXCLUSION` ist **nur** mit `categories` zulässig (kategorisch). Numerische Schwellwerte werden als `BOUNDS` oder als `EXCLUSION` mit `operator` + `value` modelliert; die FrontierEngine wertet letztere per numerischem Vergleich aus. Kombinatorik:

| enforcement | zulässige Operator-Bestückung | FrontierEngine-Auswertung |
|---|---|---|
| EXCLUSION | `categories` ODER (`operator`+`value`) | kategorial ∈/∉ bzw. numerischer Vergleich |
| SAFETY | `operator`+`value` | numerischer Vergleich, LOCK bei Verstoß |
| BOUNDS | `range` ODER (`operator`+`value`) | Intervall-Schnitt (SL-MAN-4) |

(behebt PROB-01, T4-F-02)

### §3.3 SL-BOOT-2 erweitert: Kontext-Dimensionen als Zulassungsvoraussetzung
Fehlen in `initial_dimensions` die Labor-Kontext-Dimensionen (`lab_ambient_temp`, `lab_ambient_humidity` bzw. domänenäquivalente Sensorik), **blockiert der Bootstrap** mit Template-Vorschlag zur Nachmeldung. Damit ist der Schatten-Variablen-Check (SL-TWIN-5) stets ausführbar (behebt KV-09: T4-F-04, PROB-22, F-38).

### §3.4 SL-DIR-9 (NEU): Intent-Parameter als discriminierte Union
`parameters: dict[str, Any]` wird ersetzt durch eine **discriminierte Union** `DirectiveParameters` mit einem Pydantic-Submodell je Intent (Pflichtfelder gemäß SL-DTT). Validierungsstufe 1 erzwingt die Pflichtparameter maschinell. Für `INITIAL_SWEEP` ersetzt `grid_spec` + `sweep_template_ref` das vage `levels` (behebt KV-05: T4-F-08/F-15, PROB-06, F-40).

### §3.5 SL-BOOT-8 (NEU): Kaltstart-Deadlock-Schutz
Nach `bootstrap_retry_limit` (=3) invaliden oder ausbleibenden `INITIAL_SWEEP`-Antworten: `HumanEscalationRecord(TEMPLATE_GAP)` + DecisionOptions. Das Topic bleibt `PROPOSED`, bis Mensch oder gültige Antwort eintrifft; kein stilles Hängen (behebt T4-F-09, F-39).

### §3.6 SL-BOOT-2b (NEU): Initiale Zonen-Erzeugung
Die **initialen Zonen** erzeugt der **Kartograph** beim ersten `INITIAL_SWEEP`-Symptom (SL-BOOT-6) aus einem deterministischen Template des `ObjectiveFamilySeed`. Bei leerem Atlas ist `AtlasMacroState.avg_uncertainty_score` vom Typ `Optional[float] = None` und wird im Briefing-Template als „keine Daten" dargestellt (behebt KV-21: PROB-17, F-43; PROB-05).

### §3.7 NEU: Verträge `ObjectiveFamilySeed` und `TopicSeed`
```python
class ObjectiveSpec(BaseModel):
    metric_ref: str
    direction: Literal["MAXIMIZE", "MINIMIZE"]
    target: Optional[float] = None
    weight: float = 1.0

class ObjectiveFamilySeed(BaseModel):
    family_id: str
    objectives: list[ObjectiveSpec]
    metric_constraints: list[MetricConstraint]   # binäres Gate, SL-SIG-4
    aggregation: Literal["WEIGHTED_SUM", "PARETO"]

class TopicSeed(BaseModel):
    seed_id: str
    objective_family_ref: str        # Pflicht: referenziert Manifest-Familie
    scope_description: str           # Scan, max 1024
    suggested_dimensions: list[str]  # Referenzen auf bekannte Dimensionen
```
(behebt T4-F-06, T4-F-87)

---

## §4 Lessons-Learned & Pivot-Governance (behebt KV-02; K-04)

> **ERSETZT** v0.2.0 SL-DTT-1; **ERGÄNZT** §6.4.

### §4.1 SL-DTT-1 (GEÄNDERT): `TopicConstraintProposal` statt harter ExclusionConstraints
```python
class TopicConstraintProposal(BaseModel):
    proposal_id: str
    source_topic_ref: str
    constraint: ManifestConstraint       # Vorschlag
    origin: Literal["LESSONS_LEARNED"] = "LESSONS_LEARNED"
    status: Literal["PROPOSED", "ACTIVE", "OVERRULED"] = "PROPOSED"
```
- Der Kanzler erzeugt aus gescheiterten Regionen **topic-lokale weiche Filter** (`TopicConstraintProposal`). Die FrontierEngine behandelt sie **nur innerhalb des neuen Topics** wie hart.
- Sie werden **keine ManifestConstraints**; der Aufstieg zu hart erfolgt ausschließlich über eine neue menschliche Manifest-Version. Damit bleibt SL-MAN-1 gewahrt (behebt KV-02: PROB-25/62, F-52, T4-F-89).

### §4.2 SL-DIR-8 (NEU): Pivot-Scope-Check
`to_topic_seed.objective_family_ref` muss die ObjectiveFamily des Manifests referenzieren. Eine andere Zielfamilie gilt als **neue Mission** und erfordert ein neues Manifest. Verstoß → `VETO("SCOPE_VIOLATION")` (behebt F-51, PROB-26).

### §4.3 SL-DTT-2 (NEU): Feasibility-Check
Macht die Summe der `TopicConstraintProposal`-Einträge den `TopicSeed` leer (leerer Suchraum) → Pivot-VETO(`INFEASIBLE_SEED`) (behebt T4-F-89-Teil).

### §4.4 SL-DTT-3 (NEU): Pivot-Loop-Erkennung
Referenziert `to_topic_seed` die Seed-Signatur eines bereits archivierten Topics → `VETO("PIVOT_LOOP")` (behebt T4-F-88).

---

## §5 Safety-Betriebschluss (behebt KV-14; K-05)

> **ERGÄNZT** v0.2.0 §11 (SL-SAF); **ERSETZT** die kaputte Referenz „§13.7 / §7-Quarantäne" in §8.2 durch §5.6.

### §5.1 SL-SAF-5 (NEU): Entsperrpfad
LOCKED-Zonen werden ausschließlich über eine strukturierte `HumanResponseFile.unlock_decision` auf die zugehörige `SAFETY_EVENT`-Eskalation entsperrt. Zustandsfolge: `LOCKED → DIAGNOSTIC_ONLY → RELEASED`. Der Kanzler führt aus, RoyalLog + Audit. Die Fußnote Anhang A (nicht-sicherheitsrelevant: Kanzler; sicherheitsrelevant: Mensch) wird hiermit normative Regel (behebt F-54, KV-14).

### §5.2 SL-SAF-6 (NEU): SafetyConstraint-Aktivierung fail-closed
Ein SafetyConstraint-Vorschlag gilt sofort als `active=provisional` (die Zone ist ohnehin LOCKED); menschliche Bestätigung macht es `permanent`. Aus Paket-Bounds abgeleitete Constraints erhalten zwingend eine DecisionOption zur Einengung (behebt T4-F-78, T4-F-79).

### §5.3 SL-SAF-2c (NEU): Globales ESTOP → Zonen-Mapping
Bei maschinenweitem ESTOP: alle Zonen mit in-flight-Paketen **und** die Ursprungs-Slot-Zone werden `LOCKED`; übrige erhalten `INTERLOCKED` bis zum HAL-Gesundcheck (behebt F-53).

### §5.4 SL-SAF-2d (NEU): Ereignismechanismus
Safety-Ereignisse landen in `data/governance/events/safety/`; der SL-SAF-2-Handler läuft **synchron vor jedem Pipeline-Schritt**. Merge-Priorität bei Kollision (SL-BRF-6): `SAFETY > LOCKED > FRACTURE > TWIN` (behebt PROB-29, T4-F-81, PROB-57).

### §5.5 SL-SAF-4 erweitert: Rekursive ESTOP-Begriffsprüfung
Die Prüfung auf ESTOP-/Reset-Begriffe erfolgt **rekursiv** über canonical-geflattete `parameters` (alle verschachtelten String-Werte) (behebt PROB-37).

### §5.6 §13.6 Quarantäne (NEU, ersetzt kaputte Referenz)
> **Behebt F-55, KV-14, T4-F-17/38/39/40, PROB-50/51.**

- Zustandsmaschine: `ENTRY → DIAGNOSTIC_ALLOWED → QUARANTINE_EXIT → {RESUME, CLOSE}`.
- Diagnostik in Quarantäne ist **erlaubt** und zählt auf das Diagnose-Budget.
- Quarantäne-blockierte Ideen emittieren `SymptomEvent(QUARANTINE_BLOCK)` (kein stilles Verwerfen).
- Exit nur über strukturierte `QUARANTINE_EXIT`-Antwort (`HumanResponseFile.unlock_decision`).
- **Deterministische Sicherheitsrelevanz-Regel:** Ein Fracture ist sicherheitsrelevant genau dann, wenn seine Zone eine SafetyConstraint- oder SAFETY-Enforcement-Dimension schneidet; sonst nicht-sicherheitsrelevant (Kanzler-Autorität).

---

## §6 Digital-Twin-Loop (behebt KV-06, KV-07, KV-08; K-06)

> **ERSETZT** v0.2.0 §12.1, §12.2; **ERGÄNZT** §12.

### §6.1 SL-TWIN-1 (GEÄNDERT): Paarung mit Parameter-Äquivalenz
Paarung erfordert zusätzlich zu `objective_family_ref` + `digital_twin_ref` die **Parameter-Äquivalenz** (Toleranzen aus Capability-Schema, kategorisch exakt). Nicht-äquivalente Kristalle werden nicht gepaart (behebt KV-06: T4-F-46, F-49).

### §6.2 SL-TWIN-2 (GEÄNDERT): ε und Toleranz-Defaults
```
dev_metric = max(
    abs(sim − real) / max(abs(real), twin_epsilon_default),
    abs(sim − real) / abs_tolerance_metric
)
abs_tolerance_metric = MetricDefinition.tolerance
                        falls gesetzt, sonst twin_abs_tolerance_default
```
Für `real ≈ 0` gilt **ausschließlich der Absolutterm**. `twin_epsilon_default` und `twin_abs_tolerance_default` sind Config-Parameter (§14) (behebt KV-07: F-47, F-82, PROB-20).

### §6.3 SL-TWIN-11 (NEU): Late-Pairing
Nach TTL-Ablauf bleiben Kristalle weitere `twin_late_pairing_window_cycles` nachpaarbar, sofern der Partner eintrifft (behebt T4-F-47).

### §6.4 SL-TWIN-9 (NEU): Kalibrierungs-Abbruchbedingung
Nach `twin_calibration_max_attempts` (=3) ohne Drift-Reduktion ≥ `twin_drift_reduction_min`: Twin → `SUSPENDED` + `HumanEscalationRecord(TWIN_UNCALIBRATABLE)` + DecisionOption (physische Rekalibrierung als HAL-Wartungspfad). Keine Endlosschleife (behebt T4-F-48/49).

### §6.5 SL-TWIN-10 (NEU): In-flight bei Drift
Pakete in `processing/` mit gedriftetem Twin erhalten im Briefing `twin_invalidated=true`; die Twin-Auswertung wird abgekoppelt, das physische Ergebnis bleibt wissenschaftlich gültig (behebt PROB-21).

### §6.6 Feldkorrektur und Trunkierungsschutz
- Das Phantom-Feld `objective_type` in Prüfung 10 wird durch `gate_mode`/ObjectiveFamily-Typ ersetzt (behebt T4-F-50).
- **SL-BRF-4 erweitert:** Twins mit `calibration_required=true` oder `drift_score > 0` fallen **nie** in die Trunkierungs-Restklasse (behebt KV-08: T4-F-52, F-45).
- **Kalibrierungs-Score-Bias:** nur Hypothesen mit Erwartung zählen als Samples; explorative Ergebnisse sind markiert und ausgeschlossen (behebt T4-F-51).

---

## §7 Signal-Semantik & Erwartungs-Brücke (behebt KV-22; K-07)

> **ERGÄNZT** v0.2.0 §9.

### §7.1 NEU: Vertrag `ExpectationSpec` (Hypothese→Erwartung)
```python
class ExpectationSpec(BaseModel):
    metric_ref: str
    direction: Literal["INCREASE", "DECREASE", "REACH"]
    threshold: Optional[float] = None
    delta: Optional[float] = None
```
**SL-HYP-4 (NEU):** Bestätigende Hypothesen müssen einen `ExpectationSpec` tragen; der Quartiermeister übersetzt ihn in `expectation_ref`. Der Archivar/Kartograph wertet deterministisch aus; `confirms_expectation` wird **berechnet**, nicht geliefert. Fehlt der Spec, läuft das Paket als EXPLORATION mit `hypothesis_ref`-Bindung (behebt KV-22: T4-F-27/34, PROB-18-Teil).

### §7.2 SL-SIG-5 (NEU): Erwartungsunabhängige Replikat-Divergenz
Zwei Kristalle mit parameter-äquivalenten Werten und Differenz > `MetricDefinition.tolerance` → `SymptomEvent(REPLICATE_DIVERGENCE)` + `conflict_energy` auf Zonenebene. `MetricDefinition.tolerance` ist Pflichtbestandteil der Metrik-Definition und wird beim Bootstrap geprüft (SL-BOOT-0). Damit ist der Replikat-Blindspot ohne Erwartung geschlossen (behebt PROB-18/19).

### §7.3 SL-SIG-7 (NEU): Constraint-Verletzung ohne Erwartung
→ `⬜ CONSTRAINT_NEAR_MISS` mit `constraint_gap`-Flag, niemals `🟨` (behebt PROB-15).

### §7.4 NEGATIVE_KNOWLEDGE-Gewichtung
**SL-SIG-8 (NEU):** Die FrontierEngine erhält `negative_knowledge_decay`; erfolglos abgedeckte Regionen verlieren Frontier-Priorität (behebt PROB-13, T4-F-26-Teil).

### §7.5 SL-SIG-6 (NEU): Operativer Fehler vs. wissenschaftliche Validität
Pakete mit operativem Fehler auf einer `integrity_dim` (template-deklariert, z. B. Temperatur) erzeugen Kristalle mit `validity=COMPROMISED` → ausgeschlossen aus Frontier/Support, sichtbar in Diagnostik (behebt T4-F-99).

### §7.6 Konfidenz-Semantik
Bei Erwartungslosigkeit = Messqualitätsscore des Questor, sonst Default `0.5` (behebt PROB-14).

---

## §8 Replikation (behebt KV-10; K-08)

> **ERSETZT/ERGÄNZT** v0.2.0 §19.

- **SL-REP-2 (GEÄNDERT):** `min_confirmations` (=2) wird Config-Parameter (§14). **„Relevante Bestätigung":** parameter-äquivalenter Kristall, gleiche ObjectiveFamily, `ziel_erreicht=true` (behebt PROB-41, T4-F-95, F-77).
- **SL-REP-4 (NEU):** Quotenregel: existiert ein REPLICATE-Kandidat mit `crystallization_progress ≥ replication_trigger_progress`, plant die FrontierEngine **mindestens 1 Replikation pro `replication_cadence_cycles`**. `replication_weight`-Default steigt von 0.10 auf **0.35** (behebt T4-F-94, PROB-42, F-78).
- **SL-REP-5 (NEU):** Fracture-getriebene Replikation: FRACTURE_GAP mit ≥ 2 divergenten Kristallen erzeugt eine REPLICATE-DecisionOption (behebt T4-F-42).
- **`crystallization_progress`** wird definiert (Atlas-abgeleiteter Skalar 0..1, Formel im Atlas-Vertrag, hier versioniert referenziert) (behebt T4-F-96).

---

## §9 HOLD_STRATEGY / SAFE_MODE (behebt KV-11; K-09)

> **ERSETZT** v0.2.0 §21.5; **ERGÄNZT** §7.3, §15.3.

### §9.1 §21.5 (GEÄNDERT): SystemMode-Zustandsmaschine mit Direktiven-Whitelist
```
NORMALBETRIEB ⇄ SAFE_MODE (nur Mensch)
NORMALBETRIEB ⇄ HOLD_STRATEGY (Eskalation-Timeout)
```
**HOLD_STRATEGY-Direktiven-Whitelist:** `{NO_ACTION, HUMAN_ESCALATION, CALIBRATE_TWIN (nur SANDBOX), INCREASE_DIAGNOSTIC}`. Neuer Validierungsschritt **6b „Mode-Prüfung"** weist alle übrigen Intents ab (behebt F-59, T4-F-68/69).

### §9.2 SL-NOACT-2 (NEU)
Die NO_ACTION-Stall-Überwachung (SL-NOACT-1) ist während HOLD/SAFE **suspendiert**. Kein Eskalations-Sturm über einer offenen Eskalation (behebt F-58).

### §9.3 SAFE_MODE-Protokoll (SL-SAFE-1 erweitert)
- Questor führt in-flight-Pakete bis zum sicheren Endpunkt (SR-19-konform); Ergebnisse werden archiviert.
- Bei Beendigung scannt der Kanzler **zwingend** `data/human_inbox/` vor dem neuen Briefing (behebt PROB-55, PROB-56).
- DIAGNOSE-Autorisierung in HOLD: automatisch über Vordenker/Lotse-Pfad; die Königin darf nur `INCREASE_DIAGNOSTIC` vorschlagen (behebt PROB-31).

---

## §10 Paket-Lebenszyklus bei Policy-Änderung (behebt KV-12; K-10)

> **NEU** (v0.2.0 hatte diesen Bereich nicht).

- **SL-PKG-1 (NEU):** Das Briefing enthält `in_flight_packages: list[InFlightPackageSummary]` (id, zone, topic, `manifest_version_started`, gate_mode), gedeckelt (behebt T4-F-91).
```python
class InFlightPackageSummary(BaseModel):
    package_id: str
    zone_ref: str
    topic_ref: str
    manifest_version_started: str
    gate_mode: str
```
- **SL-PKG-2 (NEU):** Manifest-Sprung prüft `processing/`-Pakete gegen die neue Fassung. Verstoß → `stop_request` an Questor (falls Abbruch-API vorhanden), sonst Weiterlauf mit Retro-Tag `policy_violation_retro=true`; das Ergebnis bleibt im Atlas, ist von Frontier/Support ausgeschlossen und wird im Report markiert. Zusätzlich DecisionOption (behebt KV-12: T4-F-74, F-63, PROB-53).
- **SL-PKG-3 (NEU): ABORT-Semantik.** Kein neuer Dispatch; in-flight pro Paket menschlich entscheiden (abschließen/abbrechen via HAL); Topics → ARCHIVED mit Abort-Flag; Abschlussbericht-Variante `ABORT_REPORT` mit Fakten (behebt T4-F-93, F-76).
- **SL-PKG-4 (NEU):** Ergebnisse archivierter Topics routet der Archivar ins Topic-Archiv; sie zählen nur für Lessons-Learned (behebt T4-F-92).
- **Manifest-Expiry:** hard_constraints gelten für Diagnostik fort; BOUNDS/EXCLUSION-Ausnahmen nur per strukturierter `HumanResponseFile.constraints_delta` (behebt F-64, T4-F-75).
- **SL-PKG-5 (NEU): Dispatch-Modell.** `max_concurrent_packages` je Slot/Reaktor aus der Capability-Registry; physische Serialisierung über das Slot-Modell (behebt PROB-12, PROB-09).

---

## §11 Validierungspipeline v2 (behebt KV-05, KV-15, KV-18; K-11)

> **ERSETZT** v0.2.0 §7.1 (7 Stufen → 10 Stufen).

### §11.1 Neue Pipeline (feste Reihenfolge)
```
StrategicDirective (LLM-Output)
 ├─ 1.  Schema (Pydantic + Intent-Submodelle, SL-DIR-9)      FAIL → VETO("SCHEMA_INVALID")
 ├─ 2.  briefing_ref-Existenz (SL-DIR-2)                      FAIL → VETO
 ├─ 3.  Manifest-Prüfung (+ Seed-Feasibility SL-DTT-2)        FAIL → VETO("MANIFEST_VIOLATION")
 ├─ 3b. Weisungs-Prüfung (aktive HumanDirective, §1.3)        FAIL → VETO("HUMAN_DIRECTIVE_VIOLATION")
 ├─ 3c. Target-Existenz & Zustandsmatrix (Existenzindex;
 │      LOCKED/QUARANTINED/ARCHIVED je Intent)                FAIL → VETO("TARGET_LOCKED"/"TARGET_TERMINAL")
 ├─ 4.  Safety-/Injection-Prüfung (rekursiv, Wortlisten)      FAIL → VETO + Audit
 ├─ 5.  Budget-Prüfung (inkl. reserved-Simulation)            FAIL → VETO("BUDGET_NEGATIVE")
 ├─ 6.  Intent-Sonderregeln (alle Intents, SL-DTT)
 ├─ 6b. Mode-Prüfung (HOLD/SAFE-Whitelist, §9.1)              FAIL → VETO("MODE_VIOLATION")
 ├─ 6c. Semantische Dedup (semantic_directive_id, §11.2)      FAIL → VETO("DUPLICATE_SEMANTIC")
 ├─ 7.  Konflikt-Modus-Prüfung (§11.3)                        FAIL → VETO("CONFLICT_MODE")
 └─ 8.  ACCEPT → DirectiveTranslationTable
```

### §11.2 SL-INT-5 (NEU): Semantische Dedup
`semantic_directive_id = sha256(intent + target_ref + canonical_json(parameters))` (**ohne** `briefing_ref`). Wiederholung mit gleichem Outcome innerhalb der letzten N Zyklen → `VETO("DUPLICATE_SEMANTIC")`, ausgenommen NO_ACTION. Das RoyalLog führt `semantic_directive_id` mit (behebt KV-15: T4-F-19, F-67).

### §11.3 SL-CON-3 (NEU): Mechanischer Konflikt-Modus
Im Konflikt-Modus werden nur NO_ACTION/HUMAN_ESCALATION **angenommen**; alle übrigen Intents → `VETO("CONFLICT_MODE")`, das **nicht** als neuer Konflikt zählt. Damit ist der NO_ACTION-Zwang mechanisch erzwungen, nicht LLM-abhängig (behebt KV-18: PROB-39, F-56).

### §11.4 SL-CON-4 (NEU): VETO-Schwere-Klassen
- **BENIGN:** `NO_DRIFT`, `TARGET_LOCKED`, `SCHEMA_INVALID` (einzelne), `DUPLICATE_SEMANTIC`.
- **GOVERNANCE:** `MANIFEST_VIOLATION`, `HUMAN_DIRECTIVE_VIOLATION`, Safety-/Injection-VETOs.
Nur GOVERNANCE-VETOs zählen ins Konfliktfenster (SL-CON-1) (behebt F-57).

### §11.5 Weitere Direktiven-Regeln
- SUPERSEDED-Kriterium: gleiche `semantic_directive_id`-Präfix (intent+target), verschiedene Parameter (behebt T4-F-21).
- `DirectiveOutcome` **+= REJECTED** (behebt T4-F-22).
- Direktiven auf ARCHIVED-Targets → `VETO("TARGET_TERMINAL")` (behebt PROB-61).

### §11.6 SL-ESC-6 (NEU): EscalationType-Erweiterung + Dedup
```
EscalationType += { LLM_FAILURE, STRATEGIC_QUESTION, TWIN_UNCALIBRATABLE,
                    BUDGET_EXHAUSTED, CAPABILITY_DELIVERY, TEMPLATE_GAP }
```
- `HUMAN_ESCALATION` erhält Pflicht-Parameter `escalation_category ∈ {DEADLOCK, STRATEGIC_QUESTION, RISK_ACCEPTANCE}` → bestimmt den Typ (behebt PROB-59, T4-F-72/73/87/88, F-44).
- Eskalations-Dedup über `(escalation_type, target_ref)`; Erinnerungs-Cap (behebt T4-F-70, T4-F-71).

---

## §12 Sanitization-Vervollständigung (behebt KV-17; K-12)

> **ERGÄNZT** v0.2.0 §17.

- **SL-SAN-0 (NEU):** First-Order-Scan **aller** LLM-Outputs (Direktiven, Hypothesen, Report-Teile, Manifest-Entwürfe) **vor Persistenz**. Treffer → Quarantäne + Audit + einmalige Neu-Generierung, danach Eskalation (behebt KV-17: T4-F-107, F-66, T4-F-108).
- **SL-SAN-5 (NEU):** `INJ-01..15` und der Safety-Claim-Katalog werden als **normativer Anhang** (Wort-/Regex-Liste) definiert (behebt PROB-34, PROB-36, PROB-45).
- **SL-SAN-2 (GEÄNDERT):** Second-Order-Treffer → Quarantäne des Artefakts, Platzhalter, Audit, DecisionOption (behebt F-65, PROB-35).
- **SL-RPT-1 (GEÄNDERT):** Zitiermuster-Entfernung determinisiert über Regex-Katalog („et al.", Name+Jahr); nicht regex-erfassbare Fälle werden als `review_required` markiert statt still entfernt (behebt PROB-44).
- **SL-SAN-6 (NEU):** Roh-Ergebnis-Trennung in `observation_raw` (quarantänefähig) und `interpretation` (niemals Erwartungsquelle) (behebt PROB-16).

---

## §13 Briefing & Kontext-Budget (behebt KV-08; K-13)

> **ERGÄNZT** v0.2.0 §6.2.

- **SL-BRF-8 (NEU): Gesamt-Kontext-Budget.** `max_total_context_chars = manifest_max_chars + max_briefing_chars + anchor_max_chars`. Layer 1 wird beim Intake geprüft (SL-BOOT-0); Layer 3 (Anchor) wird **nie** trunkiert (behebt T4-F-85, F-85).
- **SL-BRF-4 (GEÄNDERT): Trunkierungspriorität v2:**
  1. URGENT-Auslöser + SAFETY
  2. LOCKED/CRITICAL/QUARANTINE + drifted Twins + `pending_escalations` + `decisions_required`
  3. höchste Fractures
  4. aktive Topics
  5. Rest
  (behebt T4-F-86, F-45).
- **SL-BRF-9 (NEU):** Direktiven auf trunkierten Briefings markiert die DTT als `provisional=true` (Audit) (behebt T4-F-18).
- **SL-BRF-10 (NEU):** Das Briefing exponiert `active_hypothesis_refs` (Top-N), damit die Königin gültige `source_ref` bilden kann (behebt F-70).
- **SL-URG-3 (NEU):** URGENT-Nachzügler während Cooldown werden ins nächste PERIODIC gemerged und dort deklariert; kein stiller Verlust (behebt F-88).
- **SL-NOACT-1 (GEÄNDERT):** `AtlasProgressSnapshot` je Zyklus für den Fortschrittsvergleich; der Stall-Counter wird nach URGENT-Zustellung zurückgesetzt (behebt PROB-64, PROB-40).

---

## §14 Konfiguration: StrategicLayerConfig v2 (behebt KV-13; K-14)

> **ERSETZT** v0.2.0 §23. Alle v0.2.0-Werte bleiben unverändert, sofern nicht markiert. Neu/ergänzt:

```python
class StrategicLayerConfig(BaseModel):
    # --- v0.2.0 (unverändert übernommen) ---
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
    budget_unlock_threshold_fraction: float = 0.10
    stagnation_budget_threshold: float = 0.80
    max_dimension_requests_per_topic_per_cycle: int = 2
    diagnostic_budget_default: int = 3
    diagnostic_budget_max: int = 12
    quarantine_max_cycles: int = 30
    replication_trigger_progress: float = 0.8
    twin_pairing_ttl_cycles: int = 10
    calibration_alert_threshold: float = 0.5
    escalation_timeout_cycles: int = 50
    escalation_reminder_interval_cycles: int = 10
    review_reminder_interval_cycles: int = 20
    cold_storage_window_days: int = 30

    # --- NEU in v0.3.0 ---
    replication_weight: float = 0.35               # GEÄNDERT (war 0.10)
    min_confirmations: int = 2                     # NEU (KV-10)
    replication_cadence_cycles: int = 5            # NEU (SL-REP-4)
    capability_gap_repeat_limit: int = 3           # NEU (§14 v0.2.0 referenzierte es)
    full_rebuild_threshold: float = 0.85           # NEU (SL-URG-1)
    degraded_threshold: float = 0.60               # NEU (SL-DTT-1)
    quarantine_threshold: float = 0.75             # NEU (FRACTURE_GAP-Trigger)
    vordenker_queue_high_watermark: int = 50       # NEU (SL-SYM-1)
    twin_epsilon_default: float = 1e-6             # NEU (SL-TWIN-2)
    twin_abs_tolerance_default: float = 0.05       # NEU (SL-TWIN-2)
    twin_calibration_max_attempts: int = 3         # NEU (SL-TWIN-9)
    twin_drift_reduction_min: float = 0.20         # NEU (SL-TWIN-9)
    twin_late_pairing_window_cycles: int = 15      # NEU (SL-TWIN-11)
    bootstrap_retry_limit: int = 3                 # NEU (SL-BOOT-8)
    negative_knowledge_decay: float = 0.5          # NEU (SL-SIG-8)
    max_concurrent_packages: int = 1               # NEU (SL-PKG-5)
    manifest_max_chars: int = 4096                 # NEU (SL-BRF-8)
    anchor_max_chars: int = 2048                   # NEU (SL-BRF-8)
    max_total_context_chars: int = 14336           # NEU (SL-BRF-8)
    cycle_trigger: str = "EVENT_COUNT"             # NEU (SL-DEF-4): TIME|EVENT_COUNT|MANUAL
```
Zusätzlich: §20.5-Speichertabelle wird um `blocked_cache` (`data/governance/cache/`) und TwinPairingStore (`data/archiv/operational/twin/`) ergänzt; SL-INT-1 gilt auch für `SymptomEvent.metrics_snapshot`; Diagnose-Budget über Max → DecisionOption + menschliche Ausnahme; Capability-Registry erhält Status `ACTIVE/DEPRECATED/RETIRED` (behebt PROB-52, PROB-63, F-80, F-81).

---

## §15 Dimensions-Lebenszyklus (K-15)

> **ERGÄNZT** v0.2.0 §13.

- **SL-DIM-10 (NEU):** Normatives Kriterium für `requires_physical_actuation`: jede Hardware-/Aktuierungsänderung außerhalb registrierter Capability-Parameter (behebt T4-F-54).
- **SL-DIR-7 (GEÄNDERT):** `RequestSource`-Union statt SymptomType-Zwang für den Königin-Pfad (behebt T4-F-55, PROB-27).
- **SL-DIM-11 (NEU):** Lebenszeit-Limit `max_dimension_requests_per_topic_total` + Wiederholungs-Erkennung über `proposed_dimension_id` (behebt T4-F-57).
- **SL-DIM-12 (NEU):** Request-Outcomes (REJECTED/ESCALATED-Ergebnis) erscheinen als `dimension_request_outcomes` im Briefing (behebt T4-F-58).
- **NEU: Vertrag `DimensionExpansionApproval`** (behebt F-46, §0.2-Verstoß):
```python
class DimensionExpansionApproval(BaseModel):
    request_ref: str
    approver: str          # immer Mensch bei physischer Nutzung
    approved_at: str
    scope: str
```
- **SL-DIM-9 (NEU):** Neue Kategoriewerte in approved Dimensionen → leichter `CATEGORY_EXTENSION`-Request; bei constraint-belegten Dimensionen greift SL-MAN-7 (behebt PROB-10).
- **SL-DIM-13 (NEU):** Range-Korrekturen werden dem Vordenker als Feedback-Symptom zurückgemeldet (behebt T4-F-62).

---

## §16 Topic-Zustandsmaschine & Endzustände (K-17)

> **ERGÄNZT** v0.2.0 §21.

### §16.1 §21.6 (NEU): ResearchTopic-Zustandsmaschine
```
PROPOSED → ACTIVE → {SATURATED, ABORTED} → ARCHIVED
```
Alle Übergänge werden vom Kanzler ausgelöst. **Lessons-Learned-Transfer erfolgt bei jedem ACTIVE-Abschluss** (SATURATED, ABORTED, PIVOT), nicht nur bei Pivot (behebt F-84, T4-F-22).

### §16.2 Endzustände
- Mission ohne aktives Topic → URGENT + DecisionOptions (neues Topic-Seed | ABORT | UNLOCK_BUDGET) (behebt T4-F-90).
- Unreviewed-Report: nach `review_grace_max_cycles` finale Eskalation; neue Missionen werden nicht blockiert, Cold Storage wartet (dokumentiertes Restrisiko) (behebt F-75, T4-F-102).

---

## §17 Vertragshygiene (K-19)

> **ERGÄNZT/BEREINIGT** v0.2.0 §6.

- **Streichen** (tote Felder): `StrategicDirective.priority`, `StrategicDirective.keep_constraints` (behebt KV-16: T4-F-23/24, F-68).
- **`soft_preferences`** wird zu `list[SoftPreference{id, text}]`; `preference_ref` referenziert die ID (behebt T4-F-12, F-83).
- **`valid_for_cycles`** auf Einmal-Intents → `VETO("SCHEMA_INVALID")` (behebt F-69).
- **Nicht existierende `preference_ref`** → `VETO("REF_NOT_FOUND")` (behebt PROB-60).
- **SL-INT-1 (GEÄNDERT):** NaN-Teil-Verwurf: der betroffene Kristall wird verworfen, gültige Geschwister-Kristalle desselben Pakets bleiben erhalten (behebt PROB-46, T4-F-103).
- **SL-INT-2 (GEÄNDERT):** Reconciliation erhält Owner (Empfänger-Instanz), Timeout und Abschlusszustand (behebt PROB-47, T4-F-104, F-42).
- **SL-INT-6 (NEU):** Registry-Index-Dateien je Verzeichnis für Existenzprüfungen (behebt PROB-48).
- **`ReportFacts.top_crystal_summaries`** erhält definiertes N = `top_crystal_count` (Config, Default 10) (behebt PROB-43).

---

## §18 Selbständigkeit, Registries & Deployment (K-20)

> **ERGÄNZT** v0.2.0 §0.2, §25.

- **SL-DEP-1 (NEU): Inline-Pflicht.** Alle referenzierten Fremdverträge werden in diesem Delta vollständig definiert oder mit exaktem Version-Pin deklariert. §0.2-Checkliste wird als Anhang geführt (behebt F-46, T4-F-05/06/28/96/105).
- **SL-DEP-2 (NEU): Registries.** Capability-Registry und Template-Registry mit Minimal-Schema, Speicherort `data/governance/registries/`, Status-/Versionierungsfeldern; Template-Registrierung erhält Plausibilitäts-Gate statt reinem Existenz-Check (behebt PROB-04, T4-F-05/28).
```python
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
- **SL-DEP-3 (NEU): Deployment-Reihenfolge.** Der Strategic Layer aktiviert erst, wenn der QUESTOR-§10.5-Patch gemerged ist (Feature-Flag `STRAT_SIGNAL_FIX`); andernfalls dokumentierter Fallback (behebt T4-F-106).
- **SL-DEP-4 (NEU): LLM-Versions-Pinning** für Königin und Vordenker in der Missionskonfiguration (behebt T4-F-110).
- **SL-ESC-7 (NEU): CAPEX-Wartezeit.** CapabilityGap mit `requires_budget_or_hardware=true` → `HumanEscalationRecord(CAPABILITY_DELIVERY)` mit strukturiertem Lieferdatum; `blocked_cache` erhält expliziten Clearing-Pfad bei Verfügbarkeit (behebt T4-F-31/32, PROB-09).

---

## §19 Neue Pflichttests (Suite STRAT, Ergänzung zu STRAT-01..25)

> **NEU** in §28.1. Alle beziehen sich auf v0.3.0-Regeln.

| ID | Test | Erwartung |
|---|---|---|
| STRAT-26 | Direktive verstößt gegen aktive HumanDirective | VETO(HUMAN_DIRECTIVE_VIOLATION) |
| STRAT-27 | Semantisches Direktiven-Duplikat über Briefing-Grenze | VETO(DUPLICATE_SEMANTIC) |
| STRAT-28 | Manifest mit `approved_by ≠ MENSCH` | Bootstrap-REJECT |
| STRAT-29 | Twin-Deviation bei real ≈ 0 | kein Fehlalarm (Absolutterm) |
| STRAT-30 | Sim/Real-Paarung mit verschiedenen Parametern | Paarung abgelehnt |
| STRAT-31 | 3 Kalibrierungen ohne Drift-Reduktion | Twin SUSPENDED + Eskalation |
| STRAT-32 | REPLICATE-Quote bei vorhandenem Kandidaten | ≥ 1 Replikation pro Kadenz |
| STRAT-33 | SET_PRIORITY während HOLD_STRATEGY | VETO(MODE_VIOLATION) |
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

---

## §20 Fund-Register-Zuordnung (Behebungsstatus)

| Cluster (aus Auswertung) | v0.3.0-Abschnitt | Status |
|---|---|---|
| K-01 Mensch-Schnittstelle | §1 | BEHOBEN (Restrisiko: Freitext-only beratend) |
| K-02 Zyklus/Zeit/Budget | §2 | BEHOBEN |
| K-03 Bootstrap | §3 | BEHOBEN |
| K-04 Lessons-Learned/Pivot | §4 | BEHOBEN |
| K-05 Safety-Betriebsschluss | §5 | BEHOBEN |
| K-06 Twin-Loop | §6 | BEHOBEN |
| K-07 Signal-Semantik | §7 | BEHOBEN |
| K-08 Replikation | §8 | BEHOBEN |
| K-09 HOLD/SAFE | §9 | BEHOBEN |
| K-10 Paket-Lebenszyklus | §10 | BEHOBEN |
| K-11 Validierung v2 | §11 | BEHOBEN |
| K-12 Sanitization | §12 | BEHOBEN |
| K-13 Briefing/Kontext | §13 | BEHOBEN |
| K-14 Config | §14 | BEHOBEN |
| K-15 Dimensions | §15 | BEHOBEN |
| K-16 Quarantäne | §5.6 | BEHOBEN |
| K-17 Topic-Zustand/Ende | §16 | BEHOBEN |
| K-18 NO_ACTION/Konflikt | §11.3/§13 | BEHOBEN |
| K-19 Vertragshygiene | §17 | BEHOBEN |
| K-20 Selbständigkeit/Deployment | §18 | BEHOBEN |

**Dokumentierte Restrisiken (bewusst, v0.3.0):**
1. Freitext-only-Menschenweisungen sind nur beratend (§1.2b) — Struktur erforderlich.
2. Unreviewed-Reports blockieren Cold Storage, nicht neue Missionen (§16.2).
3. LLM-Wissenschaftsqualität nur in realen Domänen validierbar (übernommen aus v0.2.0 §29).