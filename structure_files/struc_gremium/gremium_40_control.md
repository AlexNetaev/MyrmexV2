# GREMIUM CONTROL MODEL — Orthogonale Steuerachsen (Unified Control)

| Feld | Wert |
|------|------|
| **Dateiname** | `gremium_40_control.md` |
| **Modul** | CONTROL |
| **Version** | 2.0.0 |
| **Status** | AKTIV |
| **Ersetzt** | `gremium_40_phases.md@1.0.0` (vollständig; Phasen werden zu Projektionen) |
| **Hängt ab von** | `gremium_10_core@1.x`, `gremium_20_contracts@1.x`, `gremium_30_rules@1.x` |
| **Änderungsgrund** | K5-F-02, K5-F-18, K5-F-20, K5-F-25, K5-F-41, K5-F-48, K5-F-49 |
| **Change-Log** | 2.0.0: Ersetzt das 5-Phasen-Skalar-Modell durch 4 orthogonale Steuerachsen + Parameter-Besitz-Matrix |

---

## §0 Zweck und Geltung

Dieses Modul definiert das **einheitliche Kontrollmodell** des Gremiums. Es ersetzt den einzelnen `MissionPhase`-Skalar durch **vier orthogonale Steuerachsen**, die unabhängig voneinander zustandsbehaftet sind und sich zu einem **Zustandstupel** komponieren.

**Leitprinzipien:**
1. **Single Ownership:** Jeder verhaltensrelevante Parameter hat genau eine Besitzer-Achse. Es gibt kein „Überschreiben" zwischen Achsen.
2. **Komposition statt Override:** Die Achsen kombinieren über Schnittmenge (Intents) und Multiplikation (Raten), nicht über eine Hierarchie.
3. **Gating vs. Besitz:** Eine Achse kann ein Verhalten *freigeben/sperren* (Gate), ohne seinen Wert zu besitzen. Mehrere Gates verknüpfen per UND; die Safety-Achse ist absolut.
4. **Phasen sind Etiketten:** Die früheren fünf „Phasen" werden zu benannten Regionen im Achsen-Raum (für Briefing/Report), nicht zu eigenen Zustandsautomaten.

---

## §1 Das Zustandsmodell

### §1.1 Die vier Achsen

| Achse | Frage | Werte | Treiber | Absolutheit |
|---|---|---|---|---|
| **SafetyAxis** | *Darf gehandelt werden?* | `NORMAL` / `SAFE_MODE` / `ESTOP_LOCKED` | HAL-Ereignis, Mensch | **Absolut** — überstimmt alle anderen |
| **ResourceAxis** | *Stehen Budget & Physis bereit?* | `FUNDED` / `INCUBATING` / `PHYSICAL_WAIT` / `BUDGET_EXHAUSTED` | Budgetzähler, Liefer-/Capability-Signal, in-flight-Pakete | Hoch — gated Aufwand |
| **ResearchAxis** | *Was wird gesucht?* | `BOOTSTRAP` / `EXPLORATION` / `EXPLOITATION` / `SATURATION` | Atlas-Metriken (Coverage, Fracture, Progress) | Normal — steuert Strategie |
| **GovernanceAxis** | *Ist der Mensch verfügbar / nötig?* | `AUTONOMOUS` / `AWAITING_HUMAN` / `CONFLICT_LOCK` | Eskalationsstatus, Konfliktdetektor | Normal — steuert Autonomie |

### §1.2 Zustandstupel

```python
class ControlState(BaseModel):
    safety:     SafetyAxis
    resource:   ResourceAxis
    research:   ResearchAxis
    governance: GovernanceAxis
    updated_at: str
    # abgeleitetes, menschenlesbares Etikett (nur für Briefing/Report)
    phase_label: str   # z.B. "EXPLOITATION + PHYSICAL_WAIT"
```

Der **Gesamtzustand** ist das Tupel `(safety, resource, research, governance)`. Jede Achse wird unabhängig aktualisiert; ein „Phasenwechsel" ist damit eine Änderung *einer* Achse, nicht des ganzen Tupels.

### §1.3 Authoritative Quelle

`ControlState` ist der einzige, autoritative Kontrollzustand. Er wird vom **Kanzler** geschrieben (deterministisch, SL-GATE-1) und in `data/governance/control_state/` persistiert. Das Journal `ControlStateLog` (§8) ist *abgeleitet*, nicht authoritativ.

---

## §2 Die Achsen im Detail

### §2.1 SafetyAxis

| Wert | Bedeutung | Erlaubt |
|---|---|---|
| `NORMAL` | Keine Safety-Einschränkung | alle Intents gemäß anderer Achsen |
| `SAFE_MODE` | Vom Menschen gesetzt; System fährt kontrolliert herunter | nur NO_ACTION, HUMAN_ESCALATION, ABORT_MISSION |
| `ESTOP_LOCKED` | HAL-ESTOP; Zonen LOCKED/INTERLOCKED | nur NO_ACTION, HUMAN_ESCALATION, INCREASE_DIAGNOSTIC (Diagnostik) |

**Transitionen:**
- `NORMAL → SAFE_MODE`: nur Mensch (SL-SAFE-1).
- `NORMAL → ESTOP_LOCKED`: HAL-Ereignis, ereignisgesteuert sofort (SL-SAF-2).
- `ESTOP_LOCKED → NORMAL`: autorisierter Sicherheitsprozess via `HumanResponseFile.unlock_decision` (SL-SAF-5).
- `SAFE_MODE → NORMAL`: nur Mensch.

**Absolutheit:** Ist `safety ≠ NORMAL`, überstimmt die SafetyAxis alle anderen Achsen. Ihre Intent-Sperren sind nicht durch Research/Resource/Governance aufhebbar.

### §2.2 ResourceAxis

| Wert | Bedeutung | burn_rate | physischer Dispatch |
|---|---|---|---|
| `FUNDED` | Budget verfügbar, keine physische Blockade | 1.0 | erlaubt |
| `INCUBATING` | Slots durch in-flight-Pakete belegt; Arbeit läuft | 1.0 | blockiert bis Abschluss |
| `PHYSICAL_WAIT` | Blockiert durch externe Abhängigkeit (CAPEX, Lieferung) | **0.0** | blockiert |
| `BUDGET_EXHAUSTED` | `remaining_cycles ≤ budget_unlock_threshold_fraction` | 0.0 | blockiert |

**Transitionen:**
- `FUNDED → INCUBATING`: automatisch, wenn `in_flight_packages` alle Slots belegen (abgeleitet aus SL-PKG-1).
- `INCUBATING → FUNDED`: ein in-flight-Paket schließt ab, Slot wird frei.
- `FUNDED|INCUBATING → PHYSICAL_WAIT`: `CapabilityGapSignal.requires_budget_or_hardware == true` ODER CAPEX-Eskalation offen (SL-ESC-7).
- `PHYSICAL_WAIT → FUNDED`: blocked_cache-Clearing-Pfad (Lieferung eingetroffen).
- `* → BUDGET_EXHAUSTED`: Budget-Schwelle unterschritten (SL-URG-2).
- `BUDGET_EXHAUSTED → FUNDED`: Mensch bestätigt `UNLOCK_BUDGET` (SL-BUD-3).

**Kernwirkung:** `PHYSICAL_WAIT` und `BUDGET_EXHAUSTED` setzen `burn_rate_multiplier = 0.0` → **KV2-01/KV2-06 sind jetzt legal behoben**, weil die ResourceAxis die Besitzerin von `burn_rate_multiplier` ist und keine Regel in `30_rules` diesen Parameter sonst setzt.

### §2.3 ResearchAxis

| Wert | Bedeutung | exploration/ exploitation | atlas_refs-Pflicht | Replikat-Divergenz |
|---|---|---|---|---|
| `BOOTSTRAP` | System lernt Domäne, Twin kalibriert | 0.5 / 0.5 | **nein** (De-novo erlaubt) | aus |
| `EXPLORATION` | Breites Scannen, Hotspots finden | 0.9 / 0.1 | **nein** (De-novo erlaubt) | aus |
| `EXPLOITATION` | Fokussierung, Verifizierung | 0.2 / 0.8 | **ja** | an |
| `SATURATION` | Suchraum erschöpft, keine Verbesserung | 0.0 / 1.0 | ja | an |

**Transitionen:**
- `BOOTSTRAP → EXPLORATION`: Twin kalibriert ODER ≥ `bootstrap_exit_crystals` Kristalle ODER ≥ `bootstrap_exit_cycles` Zyklen.
- `EXPLORATION → EXPLOITATION`: Weißraum < `exploitation_entry_whitespace` ODER erste Zone ≥ `degraded_threshold` ODER Mensch/Königin via `SET_RESEARCH_PHASE`.
- `EXPLOITATION → EXPLORATION`: Königin-Direktive ODER Ziel verfehlt + Sättigung.
- `EXPLOITATION → SATURATION`: Topic-StopCondition `SATURATION_CYCLES` (SL-SIG-3, einzige Quelle).
- `SATURATION → EXPLORATION`: Pivot oder neue Dimension.

**Granularität (behebt K5-F-20):** Die ResearchAxis ist **missionsglobal**, aber ihr `SATURATION`-Wert wird *je Topic* als Topic-Status geführt. Ein einzelnes sättigendes Topic setzt die Mission nur dann auf `SATURATION`, wenn **alle** aktiven Topics sättigen. Sonst bleibt die Mission in `EXPLOITATION` und das Topic wird lokal `SATURATED`.

**Kernwirkung:** `require_atlas_grounding` und `replicate_divergence_check` sind ResearchAxis-besessen → **KV2-08 ist jetzt legal behoben** (K5-F-48 aufgelöst).

### §2.4 GovernanceAxis

| Wert | Bedeutung | Stall-Detektion | menschenpflichtige Intents |
|---|---|---|---|
| `AUTONOMOUS` | Keine offene Eskalation | an | keine zusätzlichen |
| `AWAITING_HUMAN` | Eskalation offen (PENDING/TIMED_OUT) | **aus** | UNLOCK_BUDGET, ABORT, physische Dimension, CAPEX |
| `CONFLICT_LOCK` | Konflikt-Modus (SL-CON-3) | aus | nur NO_ACTION, HUMAN_ESCALATION |

**Transitionen:**
- `AUTONOMOUS → AWAITING_HUMAN`: Eskalation erzeugt (PENDING) oder Timeout (SL-ESC-2).
- `AWAITING_HUMAN → AUTONOMOUS`: Eskalation beantwortet (ANSWERED) und umgesetzt.
- `AUTONOMOUS → CONFLICT_LOCK`: ≥ 2 GOVERNANCE-VETOs in `conflict_window_cycles` (SL-CON-1).
- `CONFLICT_LOCK → AUTONOMOUS`: menschliche Auflösung.

**Kernwirkung:** In `AWAITING_HUMAN` ist die Stall-Detektion suspendiert (kein Eskalations-Sturm, SL-NOACT-2) und der Mensch ist als Entscheidungsweg aktiv.

---

## §3 Kompositionsregeln

### §3.1 Orthogonalität

Die vier Achsen sind **design-gemäß kombinierbar**. Der Zustand ist das Tupel; es gibt keinen Zwang, sich für ein Anliegen zu entscheiden. Damit ist **K5-F-18 (Stacking)** aufgelöst: `PHYSICAL_WAIT` (ResourceAxis) und `ESTOP_LOCKED` (SafetyAxis) können gleichzeitig wahr sein.

### §3.2 Gültigkeitsmatrix (Ausnahmen)

Fast alle Kombinationen sind gültig. Die wenigen ungültigen werden explizit verworfen:

| Kombination | Status | Begründung |
|---|---|---|
| `safety=ESTOP_LOCKED` + `resource=INCUBATING` | **UNGÜLTIG** | ESTOP bricht in-flight-Pakete ab (SR-19); Slots sind nicht mehr „belegt" |
| `safety=SAFE_MODE` + `research=BOOTSTRAP` | **UNGÜLTIG** | SAFE_MODE pausiert Bootstrap; ResearchAxis wird eingefroren |
| `resource=BUDGET_EXHAUSTED` + `governance=AUTONOMOUS` | **UNGÜLTIG** | Budget-Erschöpfung erzwingt zwingend eine Eskalation → `AWAITING_HUMAN` |

Alle übrigen Kombinationen sind erlaubt. Der Kanzler prüft bei jeder Achsen-Änderung diese Matrix; ein ungültiger Zielzustand wird verworfen (Achse bleibt im alten Wert) + Audit.

### §3.3 Priorität bei Zielkonflikten

Achsen konkurrieren nicht um Parameterwerte (Single Ownership). Wo sich **Gates** überlappen, gilt:

```
effektive_Freigabe = SafetyGate UND ResourceGate UND ResearchGate UND GovernanceGate
```

Die **SafetyAxis ist absolut**: ihr Gate kann von keiner anderen Achse geöffnet werden. Alle anderen Gates sind gleichrangig und multiplikativ.

### §3.4 Keine Hierarchie zwischen Achsen

Im Unterschied zum Phasen-Modell gibt es **keine „unterste/oberste Achse"**. Die Konfliktregel des Index (bisher `30_rules > 40_phases`) wird ersetzt durch: **Regeln in `30_rules` lesen den `ControlState` und wenden ihre Parameter gemäß der Parameter-Besitz-Matrix (§4) an.** Es gibt keinen Override-Kampf mehr.

---

## §4 Parameter-Besitz-Matrix

Jeder verhaltensrelevante Parameter hat genau eine Besitzer-Achse. `30_rules` darf einen Parameter nur dann zur Laufzeit ändern, wenn die Besitzer-Achse den Zustand wechselt.

### §4.1 ResearchAxis-Besitz

| Parameter | Werte je ResearchAxis-Wert |
|---|---|
| `exploration_weight` / `exploitation_weight` | BOOTSTRAP 0.5/0.5 · EXPLORATION 0.9/0.1 · EXPLOITATION 0.2/0.8 · SATURATION 0.0/1.0 |
| `require_atlas_grounding` | BOOTSTRAP/EXPLORATION `false` · EXPLOITATION/SATURATION `true` |
| `replicate_divergence_check` | BOOTSTRAP/EXPLORATION `false` · EXPLOITATION/SATURATION `true` |
| `replication_weight` | EXPLORATION 0.10 · EXPLOITATION/SATURATION 0.35 |
| `metric_tolerance_multiplier` | BOOTSTRAP/EXPLORATION 2.0 · EXPLOITATION/SATURATION 1.0 |
| `min_confirmations` | EXPLORATION 1 · EXPLOITATION/SATURATION 2 |

### §4.2 ResourceAxis-Besitz

| Parameter | Werte je ResourceAxis-Wert |
|---|---|
| `burn_rate_multiplier` | FUNDED/INCUBATING 1.0 · PHYSICAL_WAIT/BUDGET_EXHAUSTED 0.0 |
| `physical_dispatch_allowed` | FUNDED `true` · INCUBATING/PHYSICAL_WAIT/BUDGET_EXHAUSTED `false` |
| `escalation_timeout_multiplier` | FUNDED/INCUBATING 1.0 · PHYSICAL_WAIT 2.0 (längere menschliche Frist) |

### §4.3 GovernanceAxis-Besitz

| Parameter | Werte je GovernanceAxis-Wert |
|---|---|
| `stall_detection_active` | AUTONOMOUS `true` · AWAITING_HUMAN/CONFLICT_LOCK `false` |
| `effective_no_action_stall_limit` | AUTONOMOUS = Config-Wert · sonst `∞` |

### §4.4 SafetyAxis-Besitz (absolute Gates)

| Gate | Werte je SafetyAxis-Wert |
|---|---|
| `safety_dispatch_allowed` | NORMAL `true` · SAFE_MODE/ESTOP_LOCKED `false` |
| `safety_intent_blocklist` | NORMAL `[]` · SAFE_MODE `[alle außer NO_ACTION/HUMAN_ESCALATION/ABORT]` · ESTOP_LOCKED `[alle außer NO_ACTION/HUMAN_ESCALATION/INCREASE_DIAGNOSTIC]` |

### §4.5 Global-Konstanten (nicht achsen-besessen)

Alle übrigen `StrategicLayerConfig`-Parameter (z. B. `briefing_interval_cycles`, `max_briefing_chars`, `twin_*`, `quarantine_max_cycles`, `cycle_trigger`) bleiben **globale Konstanten**. Sie werden von keiner Achse zur Laufzeit geändert.

> **Regel (Single-Ownership-Lint):** Jeder Parameter, der von einer Achse gesetzt wird, muss in §4 gelistet sein. Ein Parameter, der in `30_rules` außerhalb seiner Besitzer-Achse verändert wird, ist ein Verstoß → Build-Fail.

---

## §5 Intent-Verfügbarkeit (behebt K5-F-41)

Die verfügbaren Intents sind die Schnittmenge über alle Achsen:

```
verfügbare_Intents = alle_Intents
                     − SafetyAxis.safety_intent_blocklist
                     − ResourceAxis.resource_intent_blocklist
                     − GovernanceAxis.governance_intent_blocklist
                     − ResearchAxis.research_intent_blocklist
```

### §5.1 Achsen-spezifische Intent-Regeln

| Intent | Verfügbarkeit |
|---|---|
| `NO_ACTION`, `HUMAN_ESCALATION` | immer (außer SafeMode-Sperre) |
| `UNLOCK_BUDGET` | **nur** wenn `resource = BUDGET_EXHAUSTED` |
| `CALIBRATE_TWIN` | nur wenn ein Twin gedriftet ist; in `PHYSICAL_WAIT` erlaubt (SANDBOX braucht keine Physis) |
| `INCREASE_DIAGNOSTIC` | in NORMAL, PHYSICAL_WAIT, ESTOP_LOCKED (Diagnostik) |
| `INITIAL_SWEEP` | nur wenn `research = BOOTSTRAP` |
| `SET_PRIORITY`, `ADD_DIMENSION_HINT`, `PIVOT_TARGET`, `ARCHIVE_TOPIC`, `DROP_SOFT_PREFERENCE` | nur wenn `research ∈ {EXPLORATION, EXPLOITATION}` |
| `SET_RESEARCH_PHASE` *(neu)* | Königin/Mensch schlägt ResearchAxis-Wechsel vor (Validierung prüft Zielzustand) |
| `ABORT_MISSION` | immer (aber ESCALATED, nur Mensch bestätigt) |

**Kernwirkung:** `UNLOCK_BUDGET` ist jetzt **genau dann** verfügbar, wenn es gebraucht wird (`BUDGET_EXHAUSTED`). K5-F-41 ist aufgelöst. `CALIBRATE_TWIN` in `PHYSICAL_WAIT` erlaubt SANDBOX-Kalibrierung während CAPEX-Wartezeit (behebt den Regressionsfund K5-F-43). `PIVOT_DOMAIN` und `DROP_SOFT_PREFERENCE` sind nicht mehr dauerhaft blockiert (K5-F-42 aufgelöst).

### §5.2 SET_RESEARCH_PHASE (neuer Intent)

Um das „Steuern auf hohem Niveau" für Königin **und** Mensch bedienbar zu machen (K5-F-16/F-17), wird ein neuer Intent eingeführt:

```python
class SetResearchPhaseParams(BaseModel):
    target_phase: ResearchAxis        # Zielwert der ResearchAxis
    reason: str                        # max 512, Scan
```

- Königin kann `SET_RESEARCH_PHASE` als Direktive senden (Validierung prüft, ob der Ziel-`ControlState` gültig ist, §3.2).
- Mensch kann den ResearchAxis-Wechsel über ein neues Feld in `HumanDirective` anweisen:
  ```python
  class HumanDirective(BaseModel):
      ...
      set_research_phase: Optional[ResearchAxis] = None   # neu
  ```
- Nur die **ResearchAxis** ist so direkt setzbar. Safety/Resource/Governance bleiben ereignis-/eskalationsgetrieben (Safety ist absolut, Resource/Governance sind Fakt-zustände).

---

## §6 Phasen als Projektion (Rückgewinnung)

Die früheren fünf Phasen sind **benannte Regionen** im Achsen-Raum. Sie dienen nur der menschenlesbaren Kennzeichnung in Briefing und Report, nicht der Steuerung.

| Ehemalige Phase | Achsen-Region |
|---|---|
| BOOTSTRAP_CALIBRATION | `research=BOOTSTRAP` |
| EXPLORATION | `research=EXPLORATION` |
| EXPLOITATION | `research=EXPLOITATION` |
| PHYSICAL_WAIT | `resource ∈ {PHYSICAL_WAIT, INCUBATING}` |
| CRISIS | `safety ∈ {SAFE_MODE, ESTOP_LOCKED}` ODER `resource=BUDGET_EXHAUSTED` ODER `governance=CONFLICT_LOCK` |

```python
def compute_phase_label(state: ControlState) -> str:
    labels = []
    labels.append(state.research.value)
    if state.resource in (ResourceAxis.PHYSICAL_WAIT, ResourceAxis.INCUBATING):
        labels.append(state.resource.value)
    if (state.safety != SafetyAxis.NORMAL or
        state.resource == ResourceAxis.BUDGET_EXHAUSTED or
        state.governance == GovernanceAxis.CONFLICT_LOCK):
        labels.append("CRISIS")
    return " + ".join(labels)
```

**Kernwirkung:** Die Phasen-Intuition bleibt erhalten, aber es gibt keinen parallelen Zustandsautomaten mehr. **K5-F-25 ist aufgelöst** — die „15 Kombinationen" sind jetzt die legitimen Projektionen des Tupels.

---

## §7 Transitionen: Auswertung und Liveness

### §7.1 Wer wertet aus

Der Kanzler wertet Achsen-Transitionen bei jedem Strategie-Zyklus aus (SL-DEF-4). Für ereignisgesteuerte Achsen (SafetyAxis, ResourceAxis bei ESTOP/CapabilityGap) gilt die ereignisgesteuerte Sofortigkeit (SL-SAF-2, §5.4 v0.3.0).

### §7.2 Liveness-Watchdog (behebt das Zeitmodell-Erbe)

Da `cycle_trigger=EVENT_COUNT` in ereignisarmen Phasen (Inkubation, Lieferung) stillstehen kann, führt der Kanzler einen **Wall-Clock-Watchdog** via `TimeService`:

```
wenn (now − letzter_strategie_zyklus) > liveness_watchdog_hours:
    emittiere Heartbeat-Zyklus (kein Briefing, nur Achsen-Auswertung)
```

Damit stehen Achsen-Transitionen (z. B. `PHYSICAL_WAIT → FUNDED` bei Lieferung, Eskalations-Timeouts) nicht unbegrenzt still. Der Watchdog ist **global** und nicht achsen-besessen.

> **Hinweis:** Der Watchdog behebt das Symptom (Stillstand). Die zugrundeliegende Frage, ob Eskalations-Timeouts Wall-Clock statt Zyklen sein sollten, bleibt als offener Punkt im Fund-Register (KV2-01-Teil) und wird in `30_rules` adressiert.

---

## §8 ControlStateLog (Audit)

```python
class AxisTransition(BaseModel):
    transition_id: str
    axis: Literal["SAFETY", "RESOURCE", "RESEARCH", "GOVERNANCE"]
    from_value: str
    to_value: str
    trigger_reason: str
    triggered_by: Literal["KANZLER", "KOENIGIN", "MENSCH", "SYSTEM", "HAL"]
    timestamp: str

class ControlStateLog(BaseModel):
    mission_id: str
    transitions: list[AxisTransition] = []
    current_state: ControlState
    updated_at: str
```

Speicherort: `data/governance/control_state/`. Das Log ist Journal (abgeleitet); der `ControlState.current_state` ist authoritativ.

---

## §9 Integration mit bestehenden Regeln

Die Regeln in `30_rules` werden so angepasst, dass sie den `ControlState` lesen, statt eigene Modus-Mechanik zu tragen:

| Bisherige Regel | Neue Anbindung |
|---|---|
| SL-BUD-1 (`used_cycles += 1`) | `used_cycles += 1 × resource.burn_rate_multiplier` → in PHYSICAL_WAIT/BUDGET_EXHAUSTED brennt nichts |
| SL-NOACT-1 (Stall) | nur wenn `governance.stall_detection_active == true` UND `in_flight_packages == 0` |
| SL-HYP-1/SL-BOOT-6 (atlas_refs) | `require_atlas_grounding = research.require_atlas_grounding` |
| SL-SIG-5 (REPLICATE_DIVERGENCE) | nur wenn `research.replicate_divergence_check == true` |
| Validierungsschritt 6b (Mode-Prüfung) | liest `ControlState`, wendet §5-Intent-Schnittmenge an |
| SL-URG-2 (BUDGET_EXHAUSTED) | setzt `resource = BUDGET_EXHAUSTED` UND `governance = AWAITING_HUMAN` |
| SL-SAF-2 (ESTOP) | setzt `safety = ESTOP_LOCKED` |
| HOLD_STRATEGY / SAFE_MODE (v0.3.0 §9) | werden zu Projektionen: HOLD ≈ `governance=AWAITING_HUMAN`, SAFE ≈ `safety=SAFE_MODE` |

**Wichtig:** `SystemMode` (NORMALBETRIEB/SAFE_MODE/HOLD_STRATEGY) wird **nicht** als parallele Maschine weitergeführt. Er wird in die Achsen aufgelöst (SAFE → SafetyAxis, HOLD → GovernanceAxis). Damit gibt es genau **ein** Kontrollmodell.

---

## §10 Config-Erweiterung

`StrategicLayerConfig` (in `20_contracts`) wird ergänzt um:

```python
# ResearchAxis-Trigger
bootstrap_exit_crystals: int = 3
bootstrap_exit_cycles: int = 5
exploitation_entry_whitespace: float = 0.20
# Liveness
liveness_watchdog_hours: int = 12
```

Zusätzlich erhält jeder Parameter in `StrategicLayerConfig` eine Metadaten-Annotation `owner_axis` (aus §4), die vom Single-Ownership-Lint geprüft wird. Parameter ohne `owner_axis` gelten als Global-Konstante.

---

## §11 Behobene K5-Funde (Traceability)

| Fund | Auflösung |
|---|---|
| K5-F-02 (Override verliert gegen 30_rules) | §3.4 + §4: kein Override, Single Ownership; Regeln lesen ControlState |
| K5-F-18 (PHYSICAL_WAIT + CRISIS Stacking) | §3.1: verschiedene Achsen, beide gleichzeitig wahr |
| K5-F-20 (Missions- vs. Topic-Granularität) | §2.3: SATURATION je Topic; Mission nur wenn alle sättigen |
| K5-F-25 (15 Kombinationen undefiniert) | §3.2 + §6: Achsen komponieren; nur 3 ungültige Kombinationen |
| K5-F-41 (UNLOCK_BUDGET blockiert) | §5.1: verfügbar genau bei BUDGET_EXHAUSTED |
| K5-F-42 (tote Intents) | §5.1: PIVOT_DOMAIN/DROP_SOFT_PREFERENCE in EXPLORATION/EXPLOITATION verfügbar |
| K5-F-43 (CALIBRATE_TWIN in PHYSICAL_WAIT) | §5.1: erlaubt (SANDBOX) |
| K5-F-48 (KV2-08-Fix unwirksam) | §2.3 + §4.1: require_atlas_grounding ist ResearchAxis-besessen |
| K5-F-49 (KV2-01-Fix unwirksam) | §2.2 + §4.2: burn_rate_multiplier ist ResourceAxis-besessen |
| K5-F-16/17 (kein SET_PHASE, kein menschliches Feld) | §5.2: SET_RESEARCH_PHASE + HumanDirective.set_research_phase |

**Weiterhin offen** (werden in `30_rules`/`20_contracts` adressiert, nicht hier): KV2-02 (Vertragslücken), KV2-03 (Config-Lücken), KV2-10 (Bio-Sequenz-Safety), KV2-07 (EvidenceBundle), K5-F-33 (Phantom-Safety-Felder).

---

## §12 Tests (L1, modul-lokal)

| ID | Test | Erwartung |
|---|---|---|
| CTRL-01 | ESTOP während PHYSICAL_WAIT | `safety=ESTOP_LOCKED` UND `resource=PHYSICAL_WAIT` gleichzeitig; kein Konflikt |
| CTRL-02 | ESTOP bricht INCUBATING ab | Zielzustand `ESTOP_LOCKED + INCUBATING` wird als ungültig verworfen; resource→FUNDED/PHYSICAL_WAIT |
| CTRL-03 | Budget-Erschöpfung | `resource=BUDGET_EXHAUSTED` erzwingt `governance=AWAITING_HUMAN` |
| CTRL-04 | UNLOCK_BUDGET bei FUNDED | Intent nicht verfügbar (Schnittmenge) |
| CTRL-05 | UNLOCK_BUDGET bei BUDGET_EXHAUSTED | Intent verfügbar |
| CTRL-06 | burn_rate in PHYSICAL_WAIT | `used_cycles` ändert sich nicht |
| CTRL-07 | De-novo-Hypothese in EXPLORATION | akzeptiert (require_atlas_grounding=false) |
| CTRL-08 | De-novo-Hypothese in EXPLOITATION | verworfen (require_atlas_grounding=true) |
| CTRL-09 | REPLICATE_DIVERGENCE in EXPLORATION | kein Symptom |
| CTRL-10 | REPLICATE_DIVERGENCE in EXPLOITATION | Symptom emittiert |
| CTRL-11 | SET_RESEARCH_PHASE auf ungültigen Zielzustand | VETO, Achse unverändert |
| CTRL-12 | Mensch setzt ResearchAxis via HumanDirective | ResearchAxis wechselt, Safety/Resource/Governance unverändert |
| CTRL-13 | Stall-Detektion in AWAITING_HUMAN | suspendiert |
| CTRL-14 | Liveness-Watchdog nach X Stunden ohne Event | Heartbeat-Zyklus emittiert |
| CTRL-15 | Single-Ownership-Lint: Parameter außerhalb Besitzer-Achse geändert | Build-Fail |
| CTRL-16 | phase_label-Berechnung | korrekte menschenlesbare Projektion |

---

## §13 Changelog

| Version | Datum | Änderung | Funde behoben |
|---|---|---|---|
| 2.0.0 | 2025-01-XX | Ersetzt 5-Phasen-Skalar durch 4 orthogonale Steuerachsen; Parameter-Besitz-Matrix; Intent-Schnittmenge; SET_RESEARCH_PHASE | K5-F-02, F-16, F-17, F-18, F-20, F-25, F-41, F-42, F-43, F-48, F-49 |

---

**Ende des Control-Moduls.**

____________________________________________________________________

# Update 1:


Ich führe den **`40_control`-Cleanup** durch und behebe damit K7N-F-02 (ControlState-Dublette). Das ist ein gezieltes, kleines Patch — kein Rewrite. Ich bumpfe `40_control` auf **v2.1.0** und ersetze die beiden Duplikat-Definitionen durch Verweise auf die kanonische Quelle `20_contracts §3`.

**Vorab-Check (aus DT7-N bestätigt):** Die Achsen-Enums (`SafetyAxis`, `ResourceAxis`, `ResearchAxis`, `GovernanceAxis`) sind bereits korrekt **nur** in `20_contracts §2.7` definiert und werden von `40_control` referenziert → dort ist **keine** Änderung nötig. Die Dublette betrifft ausschließlich `ControlState` (§1.2) und `ControlStateLog`/`AxisTransition` (§8).

---

# PATCH: gremium_40_control.md → v2.1.0

## Änderung 1 — Header (Version + Abhängigkeit + Änderungsgrund)

**Ersetze den Header-Block:**

```markdown
| Feld | Wert |
|------|------|
| **Dateiname** | `gremium_40_control.md` |
| **Modul** | CONTROL |
| **Version** | 2.1.0 |
| **Status** | AKTIV |
| **Ersetzt** | `gremium_40_phases.md@1.0.0` (vollständig; Phasen werden zu Projektionen) |
| **Hängt ab von** | `gremium_10_core@1.x`, **`gremium_20_contracts@1.1.0` (kanonische Quelle für ControlState/ControlStateLog/Achsen-Enums)**, `gremium_30_rules@1.x` |
| **Änderungsgrund** | K5-F-02, -18, -20, -25, -41, -42, -43, -48, -49; **K7N-F-02** |
| **Change-Log** | 2.0.0: Ersetzt das 5-Phasen-Skalar-Modell durch 4 orthogonale Steuerachsen + Parameter-Besitz-Matrix. **2.1.0: ControlState-/ControlStateLog-Dublette entfernt; Verweis auf 20_contracts §3 (Single Source of Truth)** |
```

---

## Änderung 2 — §1.2 Zustandsmodell (ControlState-Dublette entfernen)

**Vorher (§1.2 in v2.0.0):**

```markdown
### §1.2 Zustandsmodell

[Einleitungstext zum Tupel]

class ControlState(BaseModel):
    safety:     SafetyAxis
    resource:   ResourceAxis
    research:   ResearchAxis
    governance: GovernanceAxis
    updated_at: str
    phase_label: str   # z.B. "EXPLOITATION + PHYSICAL_WAIT"

Der Gesamtzustand ist das Tupel (safety, resource, research, governance). ...
```

**Nachher (§1.2 in v2.1.0):**

```markdown
### §1.2 Zustandsmodell

> **Single Source of Truth (K7N-F-02 behoben):** Der Vertrag `ControlState` ist
> **ausschließlich** in `gremium_20_contracts.md §3` definiert. Dieses Modul
> referenziert ihn und definiert ihn nicht selbst. Die Achsen-Enums
> (`SafetyAxis`, `ResourceAxis`, `ResearchAxis`, `GovernanceAxis`) sind in
> `20_contracts §2.7` definiert.

Der **Gesamtzustand** ist das Tupel `(safety, resource, research, governance)`
gemäß `20_contracts §3`. Jede Achse wird unabhängig aktualisiert; ein
„Phasenwechsel" ist damit eine Änderung *einer* Achse, nicht des ganzen Tupels.

Das Feld `phase_label` ist ein **abgeleitetes** Feld: Es wird durch
`compute_phase_label` (§6) aus den vier Achsen berechnet und ist nicht
authoritativ (siehe `20_contracts §3`).
```

---

## Änderung 3 — §8 ControlStateLog (Duplikat entfernen)

**Vorher (§8 in v2.0.0):**

```markdown
## §8 ControlStateLog (Audit)

class AxisTransition(BaseModel):
    transition_id: str
    axis: Literal["SAFETY", "RESOURCE", "RESEARCH", "GOVERNANCE"]
    from_value: str
    to_value: str
    trigger_reason: str
    triggered_by: Literal["KANZLER", "KOENIGIN", "MENSCH", "SYSTEM", "HAL"]
    timestamp: str

class ControlStateLog(BaseModel):
    mission_id: str
    transitions: list[AxisTransition] = []
    current_state: ControlState
    updated_at: str
```

**Nachher (§8 in v2.1.0):**

```markdown
## §8 ControlStateLog (Audit)

> **Single Source of Truth (K7N-F-02 behoben):** Die Verträge `AxisTransition`
> und `ControlStateLog` sind **ausschließlich** in `gremium_20_contracts.md §3`
> definiert. Dieses Modul referenziert sie und definiert sie nicht selbst.
> Die Semantik von `trigger_reason` (template-basiert, kein freier LLM-Text,
> da der Kanzler deterministisch ist, SL-GATE-1) ist in `20_contracts §3`
> dokumentiert.

Das Log ist ein **Journal** (abgeleitet); `ControlState.current_state` ist
authoritativ. Speicherort: `data/governance/control_state/`.
```

---

## Keine Änderung nötig (Bestätigung)

| Bereich | Status | Begründung |
|---|---|---|
| §1.1 Achsen-Übersicht (Tabelle) | **bleibt** | Dokumentation, keine Vertragsdefinition; kanonische Enums in `20_contracts §2.7` |
| §2 Achsen-Detail (Werte, Transitionen) | **bleibt** | Verhaltensspezifikation, keine Vertragsduplikate |
| §3 Kompositionsregeln / §3.2 Validitätsmatrix | **bleibt** | Logik, referenziert `ControlState` nur |
| §4 Parameter-Besitz-Matrix | **bleibt** | referenziert Config-Parameter aus `20_contracts §4` |
| §5 Intent-Verfügbarkeit / §5.2 SET_RESEARCH_PHASE | **bleibt** | nutzt `DirectiveIntent`/`ResearchAxis` aus `20_contracts §2` |
| §6 `compute_phase_label` | **bleibt** | Funktion (Ableitungslogik), nutzt `ControlState` aus `20_contracts §3` |
| §9 Integration / §10 Config-Erweiterung / §11 Traceability / §12 Tests | **bleibt** | keine Vertragsduplikate |

---

## Wirkung auf K7N-F-02

| Fund | Vorher | Nachher |
|---|---|---|
| **K7N-F-02** | `ControlState` in `40_control §1.2` **und** `20_contracts §3` definiert → Single Source of Truth verletzt | `ControlState`/`ControlStateLog`/`AxisTransition` **nur** in `20_contracts §3`; `40_control` referenziert → **BEHOBEN** |

---

## Folgeauftrag: Index-Komposition (trivial, 1 Zeile)

Im `gremium_00_index.md` ist die Kompositions-Zeile zu aktualisieren:

```
vorher:  10_core@1.0.0 + 20_contracts@1.0.0 + 30_rules@1.0.0 + 40_control@2.0.0
nachher: 10_core@1.0.0 + 20_contracts@1.1.0 + 30_rules@1.0.0 + 40_control@2.1.0
```

*(Hinweis: `20_contracts` steht hier auf `1.1.0`, da die Nachbesserung aus DT7-V bereits eingeflossen ist. `10_core` und `30_rules` bleiben Phantom, bis sie gebaut werden.)*

---

## Zusammenfassung

✅ **K7N-F-02 behoben:** Die ControlState-/ControlStateLog-/AxisTransition-Dublette ist entfernt; `40_control` verweist auf die kanonische Quelle `20_contracts §3`. Die Single Source of Truth ist wiederhergestellt.
✅ **Minimalinvasiv:** Nur Header, §1.2 und §8 geändert; alle Verhaltensspezifikationen (Achsen, Komposition, Besitz-Matrix, Intent-Logik) bleiben unberührt.
✅ **Enums bestätigt:** Bereits korrekt nur in `20_contracts §2.7`, keine Änderung nötig.

____________________________________________________________________

# Update 2:

Ich führe **Schritt 2** durch: die Klärung der `provisional`-Verortung (K7N-F-01). Das ist eine Design-Entscheidung mit einem kleinen Patch in `20_contracts` und einer Umsetzungs-Notiz für `30_rules`.

## Die Design-Entscheidung

Ich habe den Fund gegen die Knowledge Base geprüft:

> **v0.3.0 §13 SL-BRF-9:** *„Direktiven auf trunkierten Briefings markiert die DTT als `provisional=true` (Audit)."*

Die Schlüsselwörter sind **„DTT"** und **„Audit"**. Daraus leite ich drei Eigenschaften ab:
1. `provisional` wird **von der DirectiveTranslationTable (DTT) gesetzt**, nicht von der Königin.
2. Es ist ein **Audit-Marker** zur Nachvollziehbarkeit („die Königin hatte möglicherweise nicht den vollständigen Kontext").
3. Es gehört **weder in `StrategicBriefing` noch in `StrategicDirective`** (das sind Eingangs-Verträge).

**Verortungs-Entscheidung:** `provisional` wird als **optionales Feld in `RoyalLogEntry`** persistiert. Begründung:
- Das `RoyalLog` ist das operative Governance-Journal (v0.2.0 §6.5, SL-ROY-1), das der Kanzler deterministisch schreibt.
- `RoyalLogEntry` verknüpft bereits `directive_ref` und `briefing_ref` → der Marker ist direkt der betroffenen Direktive zuordenbar.
- Es ist der **minimale, konsistenteste** Ort: kein neuer Vertrag nötig, keine Verunreinigung der Königin-Direktive.

---

# PATCH: gremium_20_contracts.md → v1.1.1

## Änderung 1 — §9 Governance-Verträge: `RoyalLogEntry` um `provisional` ergänzen

**Vorher:**

```python
class RoyalLogEntry(BaseModel):
    entry_id: str
    origin: OriginType
    directive_ref: Optional[str] = None
    briefing_ref: Optional[str] = None
    outcome: DirectiveOutcome
    outcome_reason: Optional[str] = None      # max 512
    policy_effect_ref: Optional[str] = None
    timestamp: str
```

**Nachher:**

```python
class RoyalLogEntry(BaseModel):
    entry_id: str
    origin: OriginType
    directive_ref: Optional[str] = None
    briefing_ref: Optional[str] = None
    outcome: DirectiveOutcome
    outcome_reason: Optional[str] = None      # max 512
    policy_effect_ref: Optional[str] = None
    # NEU (v0.3.0 §13 SL-BRF-9): Audit-Marker, gesetzt von der DTT (30_rules).
    # true genau dann, wenn briefing_ref auf ein trunkiertes Briefing verweist
    # (briefing.truncation_applied == true). NICHT von der Königin gesetzt.
    provisional: bool = False
    timestamp: str
```

## Änderung 2 — §8 Directive-Verträge: Kommentar präzisieren

**Vorher (Kommentar unter `StrategicDirective`):**

```markdown
> `provisional` (v0.3.0 SL-BRF-9) ist ein **DTT-Ausgabe-Feld**, kein Feld der
> Königin-Direktive. Es wird bei der Policy-Übersetzung in `30_rules` gesetzt,
> wenn `briefing_ref` auf ein trunkiertes Briefing verweist.
```

**Nachher:**

```markdown
> `provisional` (v0.3.0 SL-BRF-9) ist ein **DTT-Ausgabe-/Audit-Feld**, kein Feld
> der Königin-Direktive. Es wird bei der Policy-Übersetzung in `30_rules` gesetzt
> und in `RoyalLogEntry.provisional` (§9) persistiert, wenn `briefing_ref` auf ein
> trunkiertes Briefing verweist (`briefing.truncation_applied == true`).
> **K7N-F-01 behoben:** Verortung ist `RoyalLogEntry`, nicht `StrategicDirective`.
```

## Änderung 3 — Header + Changelog

```markdown
| Version | 1.1.1 |
| Änderungsgrund | K7N-F-01 (provisional-Verortung) |
```

```markdown
| 1.1.1 | 2025-01-XX | provisional als Audit-Feld in RoyalLogEntry verortet (v0.3.0 SL-BRF-9); Kommentar in §8 präzisiert | K7N-F-01 |
```

---

## Umsetzungs-Notiz für `30_rules` (noch zu bauen)

Die DTT (v0.2.0 §6.4) setzt den Marker deterministisch bei der Policy-Übersetzung:

```
WENN strategic_directive.briefing_ref → briefing.truncation_applied == true:
    royal_log_entry.provisional = true
SONST:
    royal_log_entry.provisional = false
```

Das ist eine reine `30_rules`-Regel (deterministisch, SL-GATE-1-konform, kein LLM). Sie wird beim Bau von `30_rules` als Teil der DirectiveTranslationTable-Implementierung eingetragen.

---

## Wirkung auf K7N-F-01

| Fund | Vorher | Nachher |
|---|---|---|
| **K7N-F-01** | `provisional` fehlt in Briefing **und** Direktive; Verortung unklar | `provisional` als optionales Audit-Feld in `RoyalLogEntry` (§9); DTT setzt es in `30_rules` → **BEHOBEN (Verortung geklärt, Umsetzung in 30_rules dokumentiert)** |

---

## Zusammenfassung

✅ **K7N-F-01 geklärt:** `provisional` ist ein **DTT-Ausgabe-/Audit-Feld**, persistiert in `RoyalLogEntry.provisional` (nicht in Briefing oder Direktive). Die Semantik ist eindeutig und SL-GATE-1-konform.
✅ **Minimalinvasiv:** Nur ein optionales Feld in `RoyalLogEntry` + Kommentar-Präzisierung; kein neuer Vertrag.
✅ **Umsetzung dokumentiert:** Die DTT-Regel für `30_rules` ist als Notiz festgehalten.


____________________________________________________________________

# Update 3:

Ich führe die **Hygiene-Fixes** durch. Das sind zwei minimale, gezielte Patches — reine Version-Bumps, keine funktionalen Änderungen.

---

# PATCH 1: gremium_40_control.md → v2.1.1

**Nur der Header-Block ändert sich:**

```markdown
| Feld | Wert |
|------|------|
| **Dateiname** | `gremium_40_control.md` |
| **Modul** | CONTROL |
| **Version** | 2.1.1 |
| **Status** | AKTIV |
| **Ersetzt** | `gremium_40_phases.md@1.0.0` (vollständig; Phasen werden zu Projektionen) |
| **Hängt ab von** | `gremium_10_core@1.x`, **`gremium_20_contracts@1.1.1`** (kanonische Quelle für ControlState/ControlStateLog/Achsen-Enums), `gremium_30_rules@1.x` |
| **Änderungsgrund** | K5-F-02, -18, -20, -25, -41, -42, -43, -48, -49; K7N-F-02; **K7R-F-01** |
| **Change-Log** | 2.0.0: Achsen-Modell. 2.1.0: ControlState-Dublette entfernt. **2.1.1: Abhängigkeit auf 20_contracts@1.1.1 aktualisiert (K7R-F-01)** |
```

**Keine inhaltliche Änderung.** §1.2, §8 und alle Verhaltensspezifikationen bleiben unverändert.

---

# PATCH 2: gremium_00_index.md → v1.2.1

**Nur Header und Kompositions-Zeile ändern sich:**

```markdown
| Feld | Wert |
|------|------|
| **Dateiname** | `gremium_00_index.md` |
| **Modul** | INDEX |
| **Version** | 1.2.1 |
| **Status** | AKTIV |
| **System-Version** | GREMIUM v0.4.0-control-beta |
| **Komposition** | 10_core@1.0.0 + **20_contracts@1.1.1** + 30_rules@1.0.0 + **40_control@2.1.1** |
| **Basis** | Migration aus v0.2.0 + v0.3.0 + Achsen-Transformation + DT6-Bereinigung |
| **Konfliktregel** | Single Ownership + ControlState (siehe §2) |
| **Letzte Änderung** | **v1.2.1: Kompositions-Zeile auf 20_contracts@1.1.1 + 40_control@2.1.1 aktualisiert (K7R-F-02)** |
```

**Zusätzlich im Change-Log (§5):**

```markdown
| **1.2.1** | **2025-01-XX** | **Hygiene: Komposition auf 20_contracts@1.1.1 + 40_control@2.1.1 aktualisiert** | **K7R-F-01, K7R-F-02** |
```

**Keine inhaltliche Änderung.** Fund-Register, Konfliktregeln, COMP-Tests bleiben unverändert.

---

## Wirkung

| Fund | Vorher | Nachher |
|---|---|---|
| **K7R-F-01** | `40_control@2.1.0` → `20_contracts@1.1.0` (veraltet) | `40_control@2.1.1` → `20_contracts@1.1.1` (aktuell) |
| **K7R-F-02** | Index-Komposition veraltet | Index-Komposition aktuell |

Damit sind **alle bekannten Funde in `20_contracts` und `40_control` vollständig aufgelöst**. Die beiden Module sind jetzt stabil und konsistent versioniert.

---

## Zusammenfassung

✅ **K7R-F-01 behoben:** `40_control@2.1.1` referenziert `20_contracts@1.1.1`.
✅ **K7R-F-02 behoben:** Index-Komposition auf aktuelle Versionen aktualisiert.
✅ **Minimalinvasiv:** Nur Header und Kompositionszeile; keine inhaltlichen Änderungen.