# 🧭 STRUCTURE_STANDALONE_HAL_BRIDGE_EXP_LEDGER_V0.1.0

---

```
🧭 MYRMEX V2.4.0 + QUESTOR V0.2.3 — HAL-BRIDGE & EXPEDITIONLEDGER SPEZIFIKATION
Dateiname:       structure_standalone_hal_bridge_exp_ledger_v0.1.0.md
Version:         0.1.0
System:          MYRMEX v2.4.0 + Questor v0.2.3
Status:          Arbeitsstand — Architektur-Diskussion, keine Implementierungsfreigabe
Bezug:           structure_standalone_v2.4.0.md v1.1.1 (kanonisch)
                 structure_hal_v0.2.0.md
                 structure_standalone_questcompass_v0.1.0.md
Sprache:         Deutsch
Modus:           Dry-Run / Spezifikation
```

---

## 0. Dokumentenhierarchie und Geltung

Diese Datei ist eine **Spezialisierung der Questor-Interna** und steht unterhalb der kanonischen Hauptreferenz.

```
1. structure_standalone_v2.4.0.md v1.1.1                ← kanonisch
2. structure_hal_v0.2.0.md                               ← HAL-Vertrag
3. structure_standalone_questcompass_v0.1.0.md            ← QuestCompass
4. diese Datei: structure_standalone_hal_bridge_exp_ledger_v0.1.0.md
5. structure_standalone_questor_v0.2.3.md                 ← unterstützend
```

Bei Widersprüchen gilt die kanonische Hauptreferenz.

---

## 1. Zweck dieser Datei

Diese Datei definiert zwei zentrale interne Komponenten von Questor:

**Teil A: Die HAL-Bridge** — die einzige Verbindung zwischen Questor und HAL. Sie übersetzt Questor-interne LoopSteps in HAL-verständliche Kommandos und verarbeitet die Ergebnisse.

**Teil B: Das ExpeditionLedger** — das Zustandsjournal von Questor. Es dokumentiert jeden Schritt der Ausführung in einer geordneten, integritätsgesicherten Kette und ermöglicht Crash-Recovery über den WAL.

---

## 2. Grundannahmen

| Annahme | Wert |
|---|---|
| Nebenläufigkeit | Questor verarbeitet **immer nur EIN Paket** sequentiell |
| LLM-Backend | Ollama mit `gemma4:31b-cloud` (abstrahiert, wechselbar) |
| HAL-Spezifikation | `structure_hal_v0.2.0.md` (16 Funktionen) |
| Recovery-Mechanismus | **NUR WAL** (Write-Ahead Log), keine Blackbox-Recovery |
| Kosten-Tracking | Vereinfacht: Zeit + Reagenzien + Compute (normiert) |
| Kostenberechnung | Erst bei COMPLETED/ABORTED final berechnen |
| Ledger-Verschlüsselung | Keine (kein Mehrwert) |
| WAL-Lebenszyklus | Nur während aktiver Ausführung, nach DONE bereinigt |

---

# TEIL A: DIE HAL-BRIDGE

---

## 3. Rolle und Verantwortung der HAL-Bridge

### 3.1 Position im System

```
QUESTOR (Schicht 2)                          HAL (Schicht 1)
┌────────────────────────┐                   ┌────────────────────────┐
│                        │                   │                        │
│  QuestCompass          │                   │  HAL Interface         │
│    │                   │                   │    │                   │
│    ▼                   │                   │    ▼                   │
│  PolicyEvaluator       │                   │  Lease Validation      │
│    │                   │                   │    │                   │
│    ▼                   │                   │    ▼                   │
│  ┌──────────────┐      │                   │  ┌──────────────┐     │
│  │  HAL-BRIDGE  │──────┼──── HALCommand ──┼─►│ execute_cmd  │     │
│  │              │      │                   │  └──────────────┘     │
│  │  Übersetzt   │      │                   │  ┌──────────────┐     │
│  │  LoopSteps   │──────┼── ProcessCommand ─┼─►│ start_proc   │     │
│  │  in HAL-     │      │                   │  └──────────────┘     │
│  │  Kommandos   │◄─────┼── HALCmdResult ──┼──│              │     │
│  │              │◄─────┼── ProcessResult ──┼──│              │     │
│  └──────────────┘      │                   │  └──────────────┘     │
│                        │                   │                        │
└────────────────────────┘                   └────────────────────────┘
```

### 3.2 Was die HAL-Bridge DARF

| Erlaubt | Begründung |
|---|---|
| LoopSteps in HALCommand übersetzen | Kernaufgabe |
| LoopSteps in ProcessCommand übersetzen | Kernaufgabe |
| HALCommand an HAL senden | Einziger Weg zur Hardware |
| ProcessCommand an HAL senden | Einziger Weg zu Langzeit-Prozessen |
| HALCommandResult empfangen und verarbeiten | Ergebnisverarbeitung |
| ProcessResult empfangen und verarbeiten | Ergebnisverarbeitung |
| Slot-Zustände abfragen (get_slot_state) | Zustandsprüfung |
| Prozess-Zustände abfragen (monitor_process) | Prozessüberwachung |
| ESTOP-Zustand abfragen (get_estop_state) | Sicherheitsprüfung |
| Reconciliation anstoßen (reconcile_*) | Recovery |
| Kosten aktualisieren (Zeit, Reagenzien, Compute) | Budget-Tracking |
| Idempotenz sicherstellen | Crash-Sicherheit |

### 3.3 Was die HAL-Bridge NICHT DARF

| Verboten | Begründung |
|---|---|
| Leases vergeben oder verlängern | Nur Resource Governor |
| ESTOP zurücksetzen | Nur autorisierter Sicherheitsprozess |
| Hardware-Interlocks zurücksetzen | Nur physischer Reset |
| Wissenschaftliche Ziele in HALCommand.parameters schreiben | HAL ist nicht wissenschaftlich |
| Atlas-Signale in HALCommand.parameters schreiben | Questor schreibt nicht in Atlas |
| Gate-Logik in HAL ausführen | Gate ist Stufe 7 |
| Direkten Hardwarezugriff umgehen | HAL ist die einzige Schnittstelle |
| Zone-Locks eigenmächtig vergeben | Nur Resource Governor |
| HAL-Kommandos ohne gültige Lease senden | Fail-Closed |
| Sicherheitsentscheidungen treffen | Nur PolicyEvaluator/QuestCompass |
| Heartbeats senden | Heartbeats gehen direkt an Resource Governor |

---

## 4. Input/Output-Verträge der HAL-Bridge

### 4.1 Input: LoopStep (von QuestCompass)

```python
LoopStep:
    step_id: str                          # Eindeutige ID des Steps
    step_type: HAL_COMMAND | PROCESS_COMMAND | MEASURE | WAIT | EVALUATE
    capability: Optional[str]             # z.B. "TEMPERATURE_CONTROL"
    operation: Optional[str]              # z.B. "SET_TEMPERATURE"
    process_mode: Optional[str]           # Für PROCESS_COMMAND: START, MONITOR, etc.
    parameters: dict[str, Any]            # Konkrete Parameterwerte
    depends_on: list[str]                 # IDs vorheriger Steps
    timeout_s: float                      # Kommando-Timeout
    expected_duration_s: Optional[float]  # Für PROCESS_COMMAND: Prozess-Dauer
    parameter_schema_ref: Optional[str]   # Aus LoopTemplate
    parameter_schema_version: Optional[str]
    payload_artifact_ref: Optional[str]   # Aus LoopTemplate oder ResearchPackage
    process_recipe_ref: Optional[str]     # Aus LoopTemplate
    process_recipe_checksum: Optional[str]
    cost: StepCost                        # Geschätzte Kosten
```

### 4.2 Input: Ausführungskontext (von QuestCompass)

```python
ExecutionContext:
    package_id: str
    zyklus_id: str
    attempt_id: int
    lease_grants: list[LeaseGrant]
    security_mode: str                    # NORMAL | SANDBOX | DEV_SANDBOX_ONLY | RECOVERY
    dispatch_mode: str                    # NORMAL | RETRY | RECOVERY
    gate_mode: Optional[str]              # NORMAL | FRACTURE_DIAGNOSIS | etc.
    routing_graph: RoutingGraph
    parameter_bounds: dict[str, tuple]
    remaining_budget: BudgetState
```

### 4.3 Output: HALCommand (an HAL)

```python
HALCommand:
    command_id: str                       # Deterministisch erzeugt
    idempotency_key: str                  # command_id:lease_ref:slot_id
    lease_ref: str                        # Aus lease_grants
    slot_id: str                          # Aus routing_graph.nodes
    capability: str                       # Aus LoopStep.capability
    operation: str                        # Aus LoopStep.operation
    parameters: dict[str, Any]            # Aus LoopStep.parameters
    parameter_schema_ref: Optional[str]   # Aus LoopTemplate
    parameter_schema_version: Optional[str]
    parameter_checksum: Optional[str]     # SHA256 der Parameter
    payload_artifact_ref: Optional[str]   # Aus LoopTemplate oder Package
    timeout_s: float                      # Aus LoopStep.timeout_s
    dispatch_mode: str
    security_mode: str
    request_source: QUESTOR               # Immer QUESTOR
    correlation_id: str                   # package_id:step_id
```

### 4.4 Output: ProcessCommand (an HAL)

```python
ProcessCommand:
    process_id: str                       # Deterministisch erzeugt
    device_job_id: Optional[str]
    lease_ref: str
    slot_id: str
    capability: str
    operation: str
    parameters: dict[str, Any]
    parameter_schema_ref: Optional[str]
    parameter_schema_version: Optional[str]
    parameter_checksum: Optional[str]
    payload_artifact_ref: Optional[str]
    process_mode: str                     # START | MONITOR | RESUME | HOLD | ABORT | RELEASE_STAGE
    expected_process_duration_s: Optional[float]
    process_recipe_ref: Optional[str]     # Aus LoopTemplate
    process_recipe_checksum: Optional[str]
    on_lease_expiry_policy: str           # SAFE_HOLD | ABORT_TO_SAFE_STATE | etc.
    stage_release_policy: Optional[StageReleasePolicy]
    timeout_s: float                      # Kommando-Timeout (NICHT Prozess-Dauer!)
    dispatch_mode: str
    security_mode: str
    request_source: QUESTOR
    correlation_id: str
```

### 4.5 Input: HALCommandResult (von HAL)

```python
HALCommandResult:
    command_id: str
    status: SUCCESS | DENIED | TIMEOUT | ESTOP | INTERLOCK | ERROR |
            DUPLICATE_BLOCKED | LEASE_INVALID | LEASE_EXPIRED |
            SLOT_UNAVAILABLE | ZONE_LOCK_UNAVAILABLE
    error_code: Optional[str]
    error_class: Optional[OPERATIONAL | SAFETY]
    slot_state: SlotState
    started_at: Optional[str]
    finished_at: Optional[str]
    receipt_checksum: Optional[str]
    operational_metrics: Optional[dict[str, float]]
```

### 4.6 Input: ProcessResult (von HAL)

```python
ProcessResult:
    process_id: str
    device_job_id: Optional[str]
    slot_id: str
    process_state: PENDING | RUNNING | PAUSED | SAFE_HOLD |
                   WAITING_FOR_RELEASE | COMPLETED | ABORTED | FAULT | UNKNOWN
    current_stage: Optional[str]
    error_code: Optional[str]
    error_class: Optional[OPERATIONAL | SAFETY]
    started_at: Optional[str]
    finished_at: Optional[str]
    elapsed_time_s: Optional[float]
    resume_token: Optional[str]
    resume_allowed: bool
    operational_metrics: Optional[dict[str, float]]
```

### 4.7 Output: BridgeResult (an QuestCompass)

```python
BridgeResult:
    step_id: str
    status: SUCCESS | FAILED | SAFETY_ABORT | OPERATIONAL_ABORT |
            WAITING | SAFE_HOLD | WAITING_FOR_RELEASE
    hal_status: str
    error_code: Optional[str]
    error_class: Optional[OPERATIONAL | SAFETY]
    result_data: Optional[dict[str, Any]]
    process_id: Optional[str]
    process_state: Optional[str]
    resume_token: Optional[str]
    current_stage: Optional[str]
    actual_cost: StepCost
    started_at: Optional[str]
    finished_at: Optional[str]
    elapsed_time_s: Optional[float]
    slot_state: Optional[SlotState]
    command_id: str
    was_duplicate: bool
```

---

## 5. Übersetzungslogik

### 5.1 Grundregel

```
LoopStep.step_type == HAL_COMMAND oder MEASURE
  → HALCommand erzeugen

LoopStep.step_type == PROCESS_COMMAND
  → ProcessCommand erzeugen

LoopStep.step_type == WAIT
  → Kein HAL-Kommando (Questor wartet intern)

LoopStep.step_type == EVALUATE
  → Kein HAL-Kommando (QuestCompass evaluiert intern)
```

### 5.2 command_id / process_id Erzeugung (deterministisch)

```python
def generate_command_id(package_id, step_id, attempt_id):
    return f"cmd-{package_id}-{step_id}-{attempt_id}"

def generate_process_id(package_id, step_id, attempt_id):
    return f"proc-{package_id}-{step_id}-{attempt_id}"
```

### 5.3 Idempotenz-Schlüssel

```
HALCommand:     hal_idempotency_key = command_id:lease_ref:slot_id
ProcessCommand: hal_process_idempotency_key = process_id:lease_ref:slot_id
```

### 5.4 Slot-Zuordnung

```
1. Wenn der Step einen expliziten Slot hat → verwenden (wenn im Routing-Graph)
2. Wenn der Step eine Capability hat → passenden Slot im Routing-Graph suchen
3. Fallback: Erster Node im Routing-Graph
4. Wenn kein Slot gefunden → BridgeError("NO_SLOT_FOR_CAPABILITY")
```

### 5.5 Lease-Zuordnung

```
1. Lease-Grants aus dem ExecutionContext durchsuchen
2. Lease finden, die zum Slot passt
3. Wenn keine Lease gefunden → BridgeError("NO_LEASE_FOR_SLOT")
4. Lease-Typ prüfen:
   - HAL_COMMAND → lease_type = SHORT_COMMAND
   - PROCESS_COMMAND → lease_type = LONG_RUNNING_PROCESS
```

### 5.6 Parameter-Prüfung

```
1. Parameter aus LoopStep.parameters übernehmen
2. Gegen parameter_bounds aus dem Package prüfen
3. Wenn Parameter außerhalb der Bounds → BridgeError("PARAMETER_OUT_OF_BOUNDS")
4. Parameter-Checksumme berechnen: SHA256(canonical_json(parameters))
```

### 5.7 Trennung timeout_s vs expected_process_duration_s

```
timeout_s:                  Kommando-Timeout (RPC-Aufruf, Sekunden)
expected_process_duration_s: Prozess-Dauer (physikalisch, Sekunden bis Tage)

Diese sind STRIKT getrennt.
Beispiel: timeout_s = 60.0, expected_process_duration_s = 259200.0 (72h)
```

---

## 6. Ergebnisverarbeitung

### 6.1 HALCommandResult → BridgeResult

| HAL-Status | BridgeResult.status | error_class | Questor-Aktion |
|---|---|---|---|
| SUCCESS | SUCCESS | — | Weiter im Loop |
| DUPLICATE_BLOCKED | SUCCESS | — | Weiter (bereits ausgeführt) |
| DENIED | OPERATIONAL_ABORT | OPERATIONAL | QuestCompass entscheidet |
| TIMEOUT | OPERATIONAL_ABORT | OPERATIONAL | Retry oder Abbruch |
| ESTOP | SAFETY_ABORT | SAFETY | Sofortiger Abbruch |
| INTERLOCK | SAFETY_ABORT | SAFETY | Sofortiger Abbruch |
| ERROR | OPERATIONAL_ABORT | OPERATIONAL | QuestCompass entscheidet |
| LEASE_INVALID | OPERATIONAL_ABORT | OPERATIONAL | Abbruch |
| LEASE_EXPIRED | OPERATIONAL_ABORT | OPERATIONAL | Abbruch |
| SLOT_UNAVAILABLE | OPERATIONAL_ABORT | OPERATIONAL | QuestCompass entscheidet |
| ZONE_LOCK_UNAVAILABLE | OPERATIONAL_ABORT | OPERATIONAL | Warten oder Abbruch |

### 6.2 ProcessResult → BridgeResult

| Prozess-Zustand | BridgeResult.status | Questor-Aktion |
|---|---|---|
| COMPLETED | SUCCESS | Weiter / Finalisieren |
| RUNNING | WAITING | Warten / Überwachen |
| SAFE_HOLD | SAFE_HOLD | Warten auf Recovery |
| WAITING_FOR_RELEASE | WAITING_FOR_RELEASE | Warten auf Freigabe |
| ABORTED | OPERATIONAL_ABORT | QuestCompass entscheidet |
| FAULT | OPERATIONAL_ABORT | QuestCompass entscheidet |
| UNKNOWN | OPERATIONAL_ABORT | RECOVERY_UNSAFE |

### 6.3 Sicherheitsfehler (SAFETY)

```
Bei SAFETY_ABORT:
  1. HAL-Bridge sendet KEINE weiteren Kommandos
  2. HAL-Bridge informiert QuestCompass sofort
  3. QuestCompass leitet FINALIZING ein
  4. Ergebnis: abbruch_grund = ESTOP_RECEIVED oder HARDWARE_INTERLOCK_TRIGGERED
  5. abbruch_klasse = SAFETY
  6. kristall_kandidaten = []
  7. signale_fuer_atlas = []
```

### 6.4 Operationale Fehler (OPERATIONAL)

```
Bei OPERATIONAL_ABORT:
  1. HAL-Bridge informiert QuestCompass
  2. QuestCompass entscheidet:
     a. Retry (wenn retry_count < max_retry_count)
     b. Alternativen Loop wählen
     c. Abbruch
  3. Kein ESTOP, keine Sicherheitsprüfung
```

### 6.5 Timeout-Handling

```
Bei TIMEOUT:
  1. HAL meldet status: TIMEOUT, error_code: COMMAND_TIMEOUT
  2. HAL-Bridge prüft: Ist der Slot physisch?
     a. JA → Slot könnte in unsicherem Zustand sein
        → reconcile_slot_state() aufrufen
        → Kein blinder Retry
     b. NEIN (Compute) → Sicherer Retry möglich
  3. QuestCompass entscheidet: Retry oder Abbruch
```

---

## 7. Prozess-Lebenszyklus-Verwaltung

### 7.1 Übersicht der Prozess-Zustände

```
PENDING → RUNNING → COMPLETED
                  → SAFE_HOLD → RUNNING (RESUME)
                  → SAFE_HOLD → ABORTED
                  → WAITING_FOR_RELEASE → RUNNING (RELEASE_STAGE)
                  → WAITING_FOR_RELEASE → ABORTED
                  → FAULT → UNKNOWN → RUNNING | FAULT | ABORTED
                  → ABORTED
```

### 7.2 Langzeit-Prozess starten

```
1. ProcessCommand bauen (process_mode = START)
2. An HAL senden: hal.start_process(cmd)
3. ProcessResult empfangen
4. BridgeResult an QuestCompass zurückgeben
5. Questor wechselt in Zustand EXECUTING (WAITING)
```

### 7.3 SAFE_HOLD behandeln

```
SAFE_HOLD tritt auf wenn:
  - Lease abläuft und on_lease_expiry_policy = SAFE_HOLD
  - Heartbeat verloren geht und Grace-Period abläuft

HAL-Bridge bei SAFE_HOLD:
  1. BridgeResult.status = SAFE_HOLD
  2. resume_token wird im WAL gespeichert
  3. QuestCompass wechselt in Zustand SAFE_HOLD
  4. Keine weiteren HAL-Kommandos
  5. Warten auf Recovery

Nach Recovery:
  1. HAL-Bridge ruft reconcile_process_state() auf
  2. Prüft: Ist der Prozess noch intakt?
  3. Prüft: Ist der resume_token noch gültig?
  4. Wenn JA: RESUME senden
  5. Wenn NEIN: ABBRUCH (RECOVERY_UNSAFE)
```

### 7.4 RESUME senden

```python
ProcessCommand:
    process_id: [vorhandene process_id]
    lease_ref: [NEUE Lease nach Recovery]
    process_mode: RESUME
    resume_token: [aus SAFE_HOLD gespeichert]
    timeout_s: 60.0
```

### 7.5 WAITING_FOR_RELEASE behandeln

```
WAITING_FOR_RELEASE tritt auf wenn:
  - Eine Stufe abgeschlossen ist
  - Die nächste Stufe release_required = true hat
  - auto_start_allowed = false ist

HAL-Bridge bei WAITING_FOR_RELEASE:
  1. BridgeResult.status = WAITING_FOR_RELEASE
  2. current_stage wird gespeichert
  3. QuestCompass wechselt in Zustand WAITING_FOR_RELEASE
  4. Questor wartet auf Freigabe (kann Tage dauern)
  5. Keine weiteren HAL-Kommandos

Bei Freigabe:
  1. Questor empfängt Freigabe-Signal
  2. HAL-Bridge sendet RELEASE_STAGE
  3. Prozess wird fortgesetzt
```

### 7.6 RELEASE_STAGE senden

```python
ProcessCommand:
    process_id: [vorhandene process_id]
    lease_ref: [aktuelle Lease]
    process_mode: RELEASE_STAGE
    parameters:
        stage_id: [stage_id aus stage_release_policy]
        release_authority: [HUMAN | SAFETY_PROCESS | KANZLER]
    timeout_s: 60.0
```

### 7.7 Prozess abbrechen

```python
ProcessCommand:
    process_id: [vorhandene process_id]
    process_mode: ABORT
    timeout_s: 60.0
```

---

## 8. Idempotenz

### 8.1 Deterministische ID-Erzeugung

```
command_id  = f"cmd-{package_id}-{step_id}-{attempt_id}"
process_id  = f"proc-{package_id}-{step_id}-{attempt_id}"
```

### 8.2 Idempotenz-Regeln

```
1. Die HAL-Bridge erzeugt command_id/process_id DETERMINISTISCH.
2. Bei einem Crash und Recovery wird derselbe command_id erzeugt.
   → HAL erkennt das Duplikat → DUPLICATE_BLOCKED
   → HAL-Bridge behandelt DUPLICATE_BLOCKED als SUCCESS
   → Keine doppelte Ausführung
3. Die HAL-Bridge speichert den letzten command_id im WAL.
```

---

## 9. Security-Mode-Handling

### 9.1 Security-Mode-Prüfung

```
NORMAL:
  → Physische Ausführung erlaubt (wenn Slot physical_actuation = true)
  → Compute-Ausführung erlaubt (wenn Slot compute_capable = true)

SANDBOX:
  → Nur Simulation/Sandbox erlaubt
  → Wenn Step requires_physical_actuation → PHYSICAL_EXECUTION_FORBIDDEN

DEV_SANDBOX_ONLY:
  → Nur Test/Dev-Sandbox
  → Wenn Step requires_physical_actuation → PHYSICAL_EXECUTION_FORBIDDEN

RECOVERY:
  → Keine neue physische Ausführung
  → Nur Zustandsklärung erlaubt (MEASURE, EVALUATE)
```

### 9.2 FRACTURE_DIAGNOSIS Sonderregeln

```
Wenn gate_mode == FRACTURE_DIAGNOSIS:
  → Nur diagnostic-safe Capabilities erlaubt
  → Keine Langzeit-Prozesse
  → Nur ein Durchlauf (max_loop_iterations = 1)
  → max_retry_count = 0
  → autonomy_level wird auf STRICT gezwungen
  → LLM wird NICHT konsultiert
```

---

## 10. Kosten-Tracking

### 10.1 Kostenmodell

```yaml
StepCost:
    time_cost_s: float          # Geschätzte/tatsächliche Zeit in Sekunden
    reagent_cost: float         # Normiert 0.0–1.0
    compute_cost: float         # Normiert 0.0–1.0
    energy_cost: float          # Geschätzter Energieverbrauch
```

### 10.2 Kosten-Aktualisierung

```
1. Geschätzte Kosten kommen aus dem LoopTemplate
2. Tatsächliche Kosten werden nach Ausführung berechnet
3. Wenn HAL operational_metrics liefert → diese verwenden
4. Kosten werden im WAL protokolliert
5. Kosten werden im ExpeditionLedger akkumuliert
6. FINALE Kosten werden erst bei COMPLETED/ABORTED berechnet
```

### 10.3 Gesamtkosten statt Einzelkosten

```
estimated_total_cost = estimated_cost_per_iteration
                     × estimated_iterations_needed

→ Ein teurerer Loop, der in 1 Iteration fertig wird,
  ist besser als ein billiger Loop, der 5 Iterationen braucht.
```

### 10.4 Woher kommen die Kosten-Daten?

| Quelle | Was |
|---|---|
| LoopTemplate | Geschätzte Kosten (vom Domain-Experten) |
| HAL operational_metrics | Tatsächliche Zeit, tatsächlicher Verbrauch |
| Questor-Berechnung | Differenz geschätzt vs. tatsächlich |
| Kartograph (Gremium) | Aggregation pro Zone/Dimension |

### 10.5 Reagenzien-Tracking

```
reagent_cost bleibt normiert (0.0–1.0).
Die konkrete Menge wird in operational_metrics dokumentiert.
Der Kartograph aggregiert pro Zone.
HAL kann keine Kosten berechnen (fehlende Daten).
```

---

## 11. HAL-Bridge-Zustandsmaschine

### 11.1 Zustände

| Zustand | Bedeutung |
|---|---|
| `IDLE` | Kein aktiver Step |
| `SENDING` | Kommando wird an HAL gesendet |
| `WAITING_FOR_RESULT` | Warten auf HAL-Antwort |
| `PROCESSING_RESULT` | Ergebnis wird verarbeitet |
| `MONITORING_PROCESS` | Langzeit-Prozess wird überwacht |
| `WAITING_FOR_RELEASE` | Warten auf manuelle Freigabe |
| `SAFE_HOLD` | Prozess ist in SAFE_HOLD |
| `RECOVERING` | Recovery nach Crash |
| `ERROR` | Fehler aufgetreten |

### 11.2 Zustandsdiagramm

```
┌──────┐    LoopStep     ┌─────────┐    gesendet    ┌──────────────────┐
│ IDLE │───────────────►│ SENDING │──────────────►│ WAITING_FOR_     │
└──────┘                 └─────────┘                │ RESULT           │
    ▲                                               └────────┬─────────┘
    │                                                        │
    │                                              ┌─────────┴─────────┐
    │                                              │                   │
    │                                         HALCommand          ProcessCommand
    │                                              │                   │
    │                                              ▼                   ▼
    │                                    ┌──────────────┐   ┌──────────────────┐
    │                                    │ PROCESSING_  │   │ MONITORING_      │
    │                                    │ RESULT       │   │ PROCESS          │
    │                                    └──────┬───────┘   └────────┬─────────┘
    │                                           │                    │
    │                                    ┌──────┴──────┐      ┌──────┴──────┐
    │                                    │             │      │             │
    │                                 SUCCESS       ERROR   RUNNING    SAFE_HOLD
    │                                    │             │      │             │
    │                                    ▼             ▼      │             ▼
    └────────────────────────────────────┘          ┌────┐   │      ┌───────────┐
                                                    │ERROR│   │      │ SAFE_HOLD │
                                                    └────┘   │      └─────┬─────┘
                                                             │            │
                                                             │      Recovery + Resume
                                                             │            │
                                                             ▼            ▼
                                                    ┌──────────────────────────┐
                                                    │ WAITING_FOR_RELEASE      │
                                                    └────────────┬─────────────┘
                                                                 │
                                                          Freigabe erteilt
                                                                 │
                                                                 ▼
                                                         RELEASE_STAGE
                                                                 │
                                                                 ▼
                                                              IDLE
```

---

## 12. ESTOP-Behandlung

```
Wenn HAL ein ESTOP-Signal sendet:
  1. HAL-Bridge empfängt ESTOP (asynchron)
  2. HAL-Bridge setzt internen Zustand auf SAFETY_ABORT
  3. HAL-Bridge sendet KEINE weiteren Kommandos
  4. HAL-Bridge informiert QuestCompass sofort
  5. QuestCompass leitet FINALIZING ein (SAFETY)
  6. Ergebnis: ESTOP_RECEIVED oder HARDWARE_INTERLOCK_TRIGGERED
  7. abbruch_klasse: SAFETY
  8. kristall_kandidaten: []
  9. signale_fuer_atlas: []
```

---

## 13. Parameter-Schema-Handling

### 13.1 Woher kommt parameter_schema_ref?

```
parameter_schema_ref kommt aus dem LoopTemplate.

Der Domain-Experte erstellt LoopTemplates basierend auf
HAL-Spezifikationen, Limits und Geräteprofilen, die ihm
von HAL zur Verfügung gestellt werden.
```

### 13.2 Woher kommt process_recipe_ref?

```
process_recipe_ref kommt aus dem LoopTemplate.

Der Domain-Experte erstellt Rezepte basierend auf
HAL-Spezifikationen und fügt sie dem Template bei.
```

### 13.3 Woher kommt payload_artifact_ref?

```
Statische Konfiguration (nicht anpassbar):
  → Aus dem LoopTemplate

Versuchsspezifische Daten (nur für diesen Versuch):
  → Aus dem ResearchPackage (domain_metadata)
```

### 13.4 Schema-Validierung

```
HAL prüft (nicht HAL-Bridge):
  1. Ist parameter_schema_ref bekannt?
     → NEIN: PARAMETER_SCHEMA_UNKNOWN
  2. Ist parameter_schema_version erlaubt?
     → NEIN: PARAMETER_INVALID
  3. Stimmt parameter_checksum?
     → NEIN: PARAMETER_CHECKSUM_MISMATCH
  4. Ist die Payload-Größe erlaubt?
     → NEIN: PARAMETER_INVALID
```

### 13.5 ComputeResourceRequest

```
ComputeResourceRequest kommt aus dem LoopTemplate.
Ähnlich wie process_recipe_ref: Wissen über die Hardware
wird vom Domain-Experten in das Template geschrieben.
```

### 13.6 dataset_ref-Prüfung

```
HAL prüft formal (Schema, Checksumme).
Der Compute-Adapter prüft die Existenz.
```

---

## 14. Integration mit QuestCompass

### 14.1 Aufruf-Sequenz

```
QuestCompass:
  1. Wählt Loop aus
  2. PolicyEvaluator prüft → GO
  3. QuestCompass übergibt LoopStep an HAL-Bridge

HAL-Bridge:
  4. Prüft Security-Mode
  5. Prüft Lease-Zuordnung
  6. Prüft Parameter gegen parameter_bounds
  7. Baut HALCommand oder ProcessCommand
  8. Sendet an HAL
  9. Empfängt HALCommandResult oder ProcessResult
  10. Verarbeitet Ergebnis
  11. Aktualisiert Kosten
  12. Schreibt in WAL
  13. Liefert BridgeResult an QuestCompass zurück

QuestCompass:
  14. Empfängt BridgeResult
  15. Entscheidet: Weiter, Retry, Re-Planung oder Abbruch
```

---

## 15. Validierungsbeispiele

### 15.1 Beispiel A: Chemie — Kurzlebige Kommandos

```
LoopStep: SET_TEMPERATURE(40.0) auf reaktor-01
  → HALCommand mit capability TEMPERATURE_CONTROL
  → HALCommandResult: SUCCESS
  → BridgeResult: SUCCESS

LoopStep: MEASURE_RATE auf sensor-01
  → HALCommand mit capability REACTION_RATE_MEASURE
  → HALCommandResult: SUCCESS, rate=0.847
  → BridgeResult: SUCCESS
```

### 15.2 Beispiel B: Biologie — Langzeit-Prozess

```
LoopStep: START_LONG_RUNNING auf inkubator-01
  → ProcessCommand mit process_mode START
  → expected_process_duration_s: 259200.0
  → on_lease_expiry_policy: SAFE_HOLD
  → ProcessResult: RUNNING

Nach Crash → SAFE_HOLD:
  → ProcessResult: SAFE_HOLD, resume_token vorhanden
  → BridgeResult: SAFE_HOLD

Nach Recovery → RESUME:
  → ProcessCommand mit process_mode RESUME
  → ProcessResult: RUNNING
  → BridgeResult: SUCCESS (läuft weiter)

Nach 72h → WAITING_FOR_RELEASE:
  → ProcessResult: WAITING_FOR_RELEASE, current_stage: uv_exposition
  → BridgeResult: WAITING_FOR_RELEASE

Nach Freigabe → RELEASE_STAGE:
  → ProcessCommand mit process_mode RELEASE_STAGE
  → ProcessResult: RUNNING, current_stage: uv_exposition
  → BridgeResult: SUCCESS
```

### 15.3 Beispiel C: Physik — Mix aus Kommandos und Prozess

```
LoopStep: LOAD_SAMPLE auf kryostat-01
  → HALCommand mit capability SAMPLE_HANDLING
  → HALCommandResult: SUCCESS

LoopStep: COOLDOWN auf kryostat-01
  → ProcessCommand mit process_mode START
  → process_recipe_ref: "recipe://physik/cooldown_standard_v2"
  → ProcessResult: RUNNING

LoopStep: MEASURE_CONDUCTIVITY auf sensor-physik-01
  → HALCommand mit capability CONDUCTIVITY_MEASURE
  → HALCommandResult: SUCCESS
```

### 15.4 Beispiel D: ML/Compute — GPU-Training

```
LoopStep: TRAIN_MODEL auf gpu-cluster-01
  → ProcessCommand mit process_mode START
  → capability: ML_TRAINING
  → ProcessResult: RUNNING

Bei CUDA-OOM:
  → ProcessResult: FAULT, error_code: CUDA_OOM
  → error_class: OPERATIONAL (NICHT SAFETY!)
  → BridgeResult: OPERATIONAL_ABORT
  → QuestCompass entscheidet: Retry mit kleinerem batch_size
```

---

# TEIL B: DAS EXPEDITIONLEDGER

---

## 16. Was ist das ExpeditionLedger?

Das ExpeditionLedger ist das **Zustandsjournal** von Questor. Es dokumentiert jeden Schritt der Ausführung in einer geordneten, integritätsgesicherten Kette.

**Analogie:** Das ExpeditionLedger ist wie ein Laborbuch, das jede Aktion, jede Messung und jede Entscheidung dokumentiert — mit einem Hash, der sicherstellt, dass nichts nachträglich geändert wurde.

```
Eigenschaften:
  - APPEND-ONLY (keine nachträgliche Änderung)
  - Hash-Chain (jeder Eintrag ist mit dem vorherigen verlinkt)
  - Vollständig (alle Schritte, Entscheidungen, Kosten)
  - Read-only nach Paket-Abschluss
  - Dient als Nachschlagwerk für Domain-Experten
```

---

## 17. Formale Definition

### 17.1 Ledger-Struktur

```python
ExpeditionLedger:
    # Identität
    ledger_id: str
    package_id: str
    zyklus_id: str
    attempt_id: int
    questor_instance_id: str

    # Genesis
    genesis_hash: str
    genesis_timestamp: str

    # Zustand
    state: PLANNING | EXECUTING | EVALUATING | FINALIZING | DONE | ABORTED
    current_loop_index: int
    current_step_index: int
    iteration_count: int

    # Einträge (append-only, Hash-Chain)
    entries: list[LedgerEntry]

    # Kosten
    accumulated_cost: AccumulatedCost

    # Recovery
    last_checkpoint: LedgerCheckpoint
    wal_position: int

    # Zugriff
    access_level: READ_WRITE | READ_ONLY
    finalized_at: Optional[str]

    # Archivierung
    archive_path: Optional[str]
```

### 17.2 LedgerEntry

```python
LedgerEntry:
    entry_id: int                     # Fortlaufend, monoton steigend
    timestamp: str                    # ISO-8601
    entry_type: GENESIS | PLANNING_START | PLANNING_RESULT |
                LOOP_START | STEP_START | STEP_RESULT |
                EVALUATION | DECISION | COST_UPDATE |
                ERROR | RECOVERY | FINALIZATION
    previous_hash: str                # Hash des vorherigen Eintrags
    entry_hash: str                   # Hash dieses Eintrags
    payload: dict[str, Any]
    cost_delta: Optional[StepCost]
```

### 17.3 AccumulatedCost

```python
AccumulatedCost:
    total_time_s: float
    total_reagent_cost: float
    total_compute_cost: float
    total_energy_cost: float
    estimated_total_time_s: float
    estimated_total_reagent_cost: float
    last_updated: str
```

### 17.4 LedgerCheckpoint

```python
LedgerCheckpoint:
    checkpoint_id: int
    entry_id: int
    state: str
    current_loop_index: int
    current_step_index: int
    iteration_count: int
    accumulated_cost: AccumulatedCost
    timestamp: str
    hash: str
```

---

## 18. Genesis-Hash (C15)

### 18.1 Berechnung

```python
def calculate_genesis_hash(package_id, zyklus_id, attempt_id,
                            gate_record_ref, atlas_version_ref,
                            timestamp, questor_instance_id):
    genesis_input = (
        f"{package_id}:"
        f"{zyklus_id}:"
        f"{attempt_id}:"
        f"{gate_record_ref}:"
        f"{atlas_version_ref}:"
        f"{timestamp}:"
        f"{questor_instance_id}"
    )
    return sha256(genesis_input)
```

### 18.2 Der erste Ledger-Eintrag (GENESIS)

```yaml
LedgerEntry:
  entry_id: 0
  entry_type: GENESIS
  previous_hash: "0000000000000000000000000000000000000000000000000000000000000000"
  entry_hash: [Genesis-Hash]
  payload:
    package_id: "pkg-chem-001"
    zyklus_id: "zyklus-chem-001"
    attempt_id: 0
    gate_record_ref: "gr-chem-001"
    atlas_version_ref: "atlas-v042"
    questor_instance_id: "qi-chem-001-a"
    security_mode: NORMAL
    gate_mode: NORMAL
```

### 18.3 Hash-Chain-Regel

```
Jeder Eintrag enthält:
  previous_hash = entry_hash des vorherigen Eintrags
  entry_hash = SHA256(entry_id + timestamp + entry_type + previous_hash + payload)

Der Genesis-Eintrag hat:
  previous_hash = "0000...0000" (64 Nullen)

Prüfung:
  entry_hash[n] == SHA256(n + timestamp[n] + type[n] + entry_hash[n-1] + payload[n])
```

---

## 19. Ledger-Operationen

### 19.1 Eintrag hinzufügen (append-only)

```
1. Vorherigen Hash holen
2. Entry-ID bestimmen (fortlaufend)
3. Timestamp erzeugen
4. Entry-Hash berechnen
5. NaN/Infinity-Prüfung (C18, Fail-Closed)
   → Wenn NaN oder Infinity → LEDGER_SERIALIZATION_FAILED → Abbruch
6. Eintrag erzeugen und anhängen
7. In WAL schreiben
```

### 19.2 NaN/Infinity-Prüfung (C18)

```
Wenn ein Payload NaN oder Infinity enthält:
  → LEDGER_SERIALIZATION_FAILED
  → Abbruch (Fail-Closed)
  → Keine weitere Verarbeitung
```

### 19.3 Checkpoint erstellen

```
1. Aktuellen Zustand erfassen
2. Checkpoint-Hash berechnen
3. In WAL schreiben
4. Für Recovery verfügbar machen
```

### 19.4 Kosten aktualisieren

```
1. StepCost aus BridgeResult übernehmen
2. AccumulatedCost aktualisieren
3. Als COST_UPDATE-Eintrag ins Ledger schreiben
4. In WAL protokollieren
```

---

## 20. WAL (Write-Ahead Log)

### 20.1 Zweck

Der WAL ist das **Crash-Recovery-Protokoll** von Questor. Er schreibt jeden Zustand, BEVOR er angewendet wird.

### 20.2 WAL-Prinzip

```
VOR der Ausführung:
  1. WAL-Eintrag schreiben (was TUN werden)
  2. Aktion ausführen
  3. WAL-Eintrag aktualisieren (was GETAN wurde)

NACH einem Crash:
  1. WAL lesen
  2. Letzten validen Zustand finden
  3. Prüfen: Wurde die Aktion abgeschlossen?
  4. Wenn JA → weiter
  5. Wenn NEIN → reconcile oder abbrechen
```

### 20.3 Speicherort

```
data/wal/questor/{package_id}/{zyklus_id}/
```

### 20.4 WAL-Einträge

```python
WALEntry:
    wal_id: int
    timestamp: str
    entry_type: LEDGER_ENTRY | CHECKPOINT | HAL_COMMAND_SENT |
                HAL_COMMAND_RESULT | PROCESS_STATE_CHANGED |
                COST_UPDATE | STATE_CHANGE | ERROR | RECOVERY_START
    package_id: str
    zyklus_id: str
    attempt_id: int
    payload: dict[str, Any]
    status: PENDING | COMMITTED | ROLLED_BACK
```

### 20.5 WAL-Einträge (Beispiele)

```yaml
# Beim Start:
- entry_type: GENESIS
  package_id: "pkg-chem-001"
  ledger_id: "ledger-chem-001"

# Bei jedem HAL-Befehl:
- entry_type: HAL_COMMAND_SENT
  command_id: "cmd-pkg-chem-001-set_temp_40-0"
  step_id: "set_temp_40"

# Bei jedem HAL-Ergebnis:
- entry_type: HAL_COMMAND_RESULT
  command_id: "cmd-pkg-chem-001-set_temp_40-0"
  status: SUCCESS

# Bei Prozess-Zustandswechsel:
- entry_type: PROCESS_STATE_CHANGED
  process_id: "proc-bio-001"
  old_state: RUNNING
  new_state: SAFE_HOLD
  resume_token: "rt-bio-001-safe-hold"

# Bei jedem Checkpoint:
- entry_type: CHECKPOINT
  state: EXECUTING
  current_loop_index: 0
  current_step_index: 3
  accumulated_cost: {time: 180, reagent: 0.05}
```

### 20.6 Was der WAL NICHT enthält

```
✗ Vollständige Messdaten (sind im Ledger)
✗ LLM-Prompts und Antworten (sind in der Blackbox)
✗ Template-Definitionen (sind in der Registry)
✗ Package-Inhalte (sind im Envelope)
✗ HALCommandResult-Details (nur Status und command_id)
```

### 20.7 WAL-Lebenszyklus

```
PAKET START:
  → WAL wird erstellt
  → Genesis-Eintrag wird geschrieben

WÄHREND AUSFÜHRUNG:
  → Jeder Zustandswechsel wird in den WAL geschrieben
  → Jeder HAL-Befehl wird in den WAL geschrieben
  → Jeder Checkpoint wird in den WAL geschrieben

BEI CRASH:
  → WAL wird gelesen
  → Letzter Checkpoint wird geladen
  → Zustand wird rekonstruiert

NACH PAKET-ABSCHLUSS (FINALIZING → DONE):
  → WAL wird NICHT mehr benötigt
  → Ledger enthält die vollständige Aufzeichnung
  → WAL-Einträge werden bereinigt
  → Ledger wird als READ-ONLY archiviert

REGEL:
  → WAL existiert NUR während der aktiven Ausführung
  → Nach DONE ist der WAL überflüssig
  → Der Ledger ist die permanente Aufzeichnung
```

---

## 21. Recovery aus dem WAL

### 21.1 Recovery-Ablauf

```
1. WAL lesen
2. Integrität prüfen (Hash-Chain)
   → Wenn korrupt: RECOVERY_UNSAFE
3. Letzten Checkpoint finden
   → Wenn kein Checkpoint: RECOVERY_UNSAFE
4. Zustand aus Checkpoint rekonstruieren
5. Einträge nach dem Checkpoint prüfen
6. Letzte Aktion identifizieren:
   a. Keine Aktion nach Checkpoint → Zustand klar → RECOVERED
   b. Aktion COMMITTED → Zustand klar → RECOVERED
   c. Aktion PENDING (HAL_COMMAND_SENT) → REQUIRES_RECONCILE
   d. Aktion PENDING (PROCESS_STATE_CHANGED) → REQUIRES_RECONCILE
   e. Unbekannter Zustand → RECOVERY_UNSAFE
```

### 21.2 Recovery-Entscheidung durch QuestCompass

```
RECOVERED:
  → Zustand ist klar
  → QuestCompass setzt am letzten Punkt an
  → Weiter im Planungszyklus

REQUIRES_RECONCILE:
  → Zustand ist unklar
  → HAL-Bridge ruft reconcile_slot_state() oder reconcile_process_state() auf
  → HAL prüft physischen Zustand
  → QuestCompass entscheidet: FORTSETZEN oder ABBRECHEN

RECOVERY_UNSAFE:
  → Zustand ist nicht wiederherstellbar
  → Questor bricht ab mit RECOVERY_UNSAFE
  → Ergebnis wird gebaut (Early-Abort Complete Result)
```

---

## 22. Ledger und Sequence-Manager

### 22.1 Sequence-Atomarität (C16)

```
Die sequence_number wird ATOMAR mit dem Ledger-Eintrag FINALIZATION geschrieben.

1. Sequence-Nummer bestimmen (nächste pro questor_instance_id)
2. FINALIZATION-Eintrag ins Ledger schreiben
3. Checkpoint erstellen
4. Sequence-Nummer atomar persistieren (Datei-Lock)
5. WAL-Eintrag als COMMITTED markieren
```

### 22.2 Sequence-Persistenz

```python
SequenceStore:
    path: "data/questor_state/sequences.json"
    
    get_next_sequence(questor_instance_id) -> int
    increment_atomically(questor_instance_id, sequence) -> None
    
    # Datei-Lock für Atomarität
    # Bei Mismatch: SEQUENCE_MISMATCH → Abbruch
```

---

## 23. Dokument-Hierarchie nach Paket-Abschluss

### 23.1 Dreiteilung

```
┌─────────────────────────────────────────────────────────────────┐
│  EBENE 1: questor_ergebnis_paket (DER BERICHT)                   │
│  → Geht an: Receiver → Archivar → Gremium                       │
│  → Enthält: Zusammenfassung, Ergebnisse, Signale                │
│  → Analogie: Abstract + Results einer Arbeit                    │
│  → Größe: Klein (KB)                                            │
├─────────────────────────────────────────────────────────────────┤
│  EBENE 2: ExpeditionLedger (DAS LABORBUCH)                       │
│  → Bleibt lokal: data/questor_ledger/                           │
│  → Enthält: Vollständiger Prozess, alle Steps,                  │
│    alle HAL-Kommandos, alle Entscheidungen                      │
│  → Analogie: Vollständiges Laborbuch + Rohdaten                 │
│  → Größe: Mittel bis Groß (MB)                                  │
│  → Zugriff: Read-only, nur autorisierte Rollen                  │
├─────────────────────────────────────────────────────────────────┤
│  EBENE 3: QuestorBlackbox (DIE ROHDATEN)                         │
│  → Bleibt lokal: data/questor_blackbox/                         │
│  → Enthält: Sensordaten, LLM-Logs, interne Zustände            │
│  → Analogie: Rohdatenordner, Messgeräte-Logs                    │
│  → Größe: Groß (MB bis GB)                                      │
│  → Zugriff: Nur Entwickler/Notfall                              │
└─────────────────────────────────────────────────────────────────┘
```

### 23.2 Wer bekommt was?

| Empfänger | questor_ergebnis_paket | ExpeditionLedger | Blackbox |
|---|---|---|---|
| Receiver | ✅ Ja | ❌ Nein | ❌ Nein |
| Archivar | ✅ Ja | ❌ Nein | ❌ Nein |
| Kartograph | ✅ (über Archiv) | ❌ Nein | ❌ Nein |
| Kanzler | ✅ (über Archiv) | ❌ Nein | ❌ Nein |
| Domain-Experte | ✅ (über Archiv) | ✅ Read-only | ❌ Nein |
| System-Integrator | ✅ (über Archiv) | ✅ Read-only | ✅ Notfall |
| Entwickler | ✅ | ✅ Read-only | ✅ Notfall |

### 23.3 Nutzung des Ledgers als Nachschlagwerk

```
SZENARIO: Domain-Experte will Loop-Template verbessern

1. Domain-Experte sieht im questor_ergebnis_paket:
   → template_feedback: "Step 'measure_rate' liefert NaN bei > 43°C"

2. Domain-Experte will den GENAUEN Ablauf verstehen:
   → Öffnet das ExpeditionLedger via ledger_id
   → Liest die Ledger-Einträge für den betroffenen Step
   → Erkennt: Sensor-Drift ab 44°C

3. Domain-Experte korrigiert das Template:
   → Neue Version: optimize_loop_v1 → optimize_loop_v2
   → Registry wird aktualisiert
```

---

## 24. Zugriffskontrolle für das Ledger

```python
LEDGER_ACCESS_MATRIX = {
    # Rolle: (lesen, schreiben, löschen)
    "questor_intern":     (True,  True,  False),  # Während Ausführung
    "receiver":           (False, False, False),
    "archivar":           (False, False, False),
    "kartograph":         (False, False, False),
    "kanzler":            (False, False, False),
    "vordenker":          (False, False, False),
    "quartiermeister":    (False, False, False),
    "domain_expert":      (True,  False, False),  # Read-only
    "system_integrator":  (True,  False, False),  # Read-only
    "developer":          (True,  False, False),  # Read-only
    "safety_process":     (True,  False, False),  # Read-only (bei SAFETY)
}

# Regeln:
# 1. Während Ausführung: Nur Questor-intern darf schreiben
# 2. Nach FINALIZATION: Niemand darf schreiben (READ-ONLY)
# 3. Nach FINALIZATION: Niemand darf löschen
# 4. Kanzler, Archivar, Kartograph: KEIN Zugriff
# 5. Zugriff nur über ledger_id (Verlinkung im questor_ergebnis_paket)
```

---

## 25. Archivierung nach Paket-Abschluss

```
NACH PAKET-ABSCHLUSS:

1. Ledger wird FINALISIERT:
   → Letzter Eintrag: FINALIZATION
   → Ledger wird als READ-ONLY markiert
   → Keine weiteren Einträge möglich

2. Ledger wird ARCHIVIERT:
   → Ablage: data/questor_ledger/{package_id}/{zyklus_id}/
   → Format: JSON (serialisiert)
   → Komprimierung: Optional (gzip)
   → Retention: Unbegrenzt (wie ein Laborbuch)

3. WAL wird BEREINIGT:
   → WAL-Einträge für dieses Paket werden gelöscht
   → Nur der Ledger bleibt als permanente Aufzeichnung

4. Blackbox bleibt:
   → data/questor_blackbox/{blackbox_id}/
   → Retention abhängig von retention_class:
     NORMAL: 90 Tage
     SAFETY_HOLD: Unbegrenzt
     DEVELOPMENT_HOLD: 30 Tage
```

---

## 26. Integration: HAL-Bridge und ExpeditionLedger

### 26.1 Wer schreibt ins Ledger?

| Komponente | Schreibt ins Ledger? | Was? |
|---|---|---|
| QuestCompass | ✅ Ja | PLANNING_START, PLANNING_RESULT, EVALUATION, DECISION |
| HAL-Bridge | ✅ Ja | STEP_START, STEP_RESULT, COST_UPDATE |
| PolicyEvaluator | ✅ Ja | DECISION (GO/VETO) |
| SafetyMonitor | ✅ Ja | ERROR (ESTOP, INTERLOCK) |
| Result-Builder | ✅ Ja | FINALIZATION |
| Recovery | ✅ Ja | RECOVERY_START, RECOVERY |

### 26.2 Wer liest das Ledger?

| Komponente | Liest das Ledger? | Wofür? |
|---|---|---|
| QuestCompass | ✅ Ja | Für Re-Planung (bisherige Ergebnisse) |
| Result-Builder | ✅ Ja | Für questor_ergebnis_paket |
| Recovery | ✅ Ja | Für Crash-Recovery |
| Blackbox-Archiver | ✅ Ja | Für Blackbox-Inhalt |
| Gremium | ❌ NEIN | Questor schreibt nicht ins Gremium |

### 26.3 Ledger-Einträge pro QuestCompass-Zyklus

```
ZYKLUS 1:
  PLANNING_START    → "QuestCompass plant Loop 1"
  PLANNING_RESULT   → "Loop 'optimize_loop_v1' gewählt"
  LOOP_START        → "Loop gestartet"
  STEP_START        → "Step 'set_temp_40' gestartet"
  STEP_RESULT       → "Step erfolgreich, Ergebnis: {...}"
  COST_UPDATE       → "Kosten aktualisiert"
  EVALUATION        → "Konfidenz 0.7 < threshold → RE-PLANUNG"
  DECISION          → "RE-PLANUNG"

ZYKLUS 2:
  PLANNING_START    → "QuestCompass plant Loop 2"
  ...
  EVALUATION        → "Konfidenz 0.93 >= threshold → ZIEL ERREICHT"
  DECISION          → "FINALIZING"
  FINALIZATION      → "Ergebnis wird gebaut"
```

---

## 27. Zusammenfassung der Entscheidungen

### HAL-Bridge

| Thema | Entscheidung |
|---|---|
| HAL-Bridge ist die einzige Verbindung zu HAL | ✅ |
| LoopStep → HALCommand/ProcessCommand | ✅ |
| command_id deterministisch erzeugt | ✅ |
| Security-Mode-Prüfung vor dem Senden | ✅ |
| Lease-Zuordnung vor dem Senden | ✅ |
| Parameter gegen parameter_bounds geprüft | ✅ |
| DUPLICATE_BLOCKED als SUCCESS behandelt | ✅ |
| ESTOP/INTERLOCK als SAFETY_ABORT | ✅ |
| TIMEOUT als OPERATIONAL_ABORT | ✅ |
| SAFE_HOLD / RESUME / WAITING_FOR_RELEASE | ✅ |
| Kosten bei Langzeit erst bei COMPLETED/ABORTED final | ✅ |
| process_recipe_ref aus LoopTemplate | ✅ |
| payload_artifact_ref: statisch → Template, spezifisch → Package | ✅ |
| ComputeResourceRequest aus LoopTemplate | ✅ |
| dataset_ref: HAL formal, Adapter Existenz | ✅ |
| Recovery NUR aus WAL | ✅ |
| Heartbeats NICHT über HAL-Bridge | ✅ |
| Zonen-Locks NICHT von HAL-Bridge vergeben | ✅ |

### ExpeditionLedger

| Thema | Entscheidung |
|---|---|
| Ledger ist APPEND-ONLY | ✅ |
| Hash-Chain für Integrität | ✅ |
| Genesis-Hash aus Paket-IDs + Gate-Ref + Atlas-Ref | ✅ |
| NaN/Infinity → Fail-Closed (C18) | ✅ |
| WAL für Crash-Recovery | ✅ |
| Recovery NUR aus WAL | ✅ |
| Keine Verschlüsselung | ✅ |
| Read-only nach Abschluss | ✅ |
| Zugriff nur für autorisierte Rollen | ✅ |
| Kanzler hat KEINEN Ledger-Zugriff | ✅ |
| Domain-Experte hat Read-only-Zugriff | ✅ |
| WAL wird nach Abschluss bereinigt | ✅ |
| Ledger wird nach Abschluss archiviert | ✅ |
| Dreiteilung: Bericht / Ledger / Blackbox | ✅ |
| Sequence-Atomarität über Datei-Lock | ✅ |

---

## 28. Noch offene Themen (für spätere Erweiterungen)

| # | Thema | Status |
|---|---|---|
| 1 | Result-Builder — Wie wird das questor_ergebnis_paket gebaut? | ❌ Offen |
| 2 | Blackbox-Archiver — Format, Rotation, Retention | ❌ Offen |
| 3 | Questor-Facade — Transportmedium | ❌ Offen |
| 4 | Capability-Registry — Formale Definition | ❌ Offen |
| 5 | Trail-Map — Struktur, Erzeugung | ❌ Offen |
| 6 | Sanitization — Vollständige Regeln | ❌ Offen |
| 7 | Questor-Health-Monitoring | ❌ Offen |
| 8 | Questor-Graceful-Shutdown | ❌ Offen |
| 9 | security_mode-Verhalten im Detail | ❌ Offen |

---

## Appendix A: Gremium-Auslagerungen (Erinnerungen)

| # | Thema | Gremium-Komponente | Status |
|---|---|---|---|
| G-1 | Template-Erstellung bei fehlendem Template | Quartiermeister + Domain-Experte | ✅ Definiert |
| G-2 | Template-Korrektur nach Questor-Feedback | Domain-Experte (NICHT Kanzler) | ✅ Definiert |
| G-3 | Template-Versionierung (alte Versionen im Archiv) | Archivar | ✅ Definiert |
| G-4 | Ressourcen-Karte (Verbrauch pro Zone/Dimension) | Kartograph | ✅ Definiert |
| G-5 | Vordenker liefert prozess_skizze mit Idee | Vordenker | ✅ Definiert |
| G-6 | template_feedback operational protokollieren | Archivar | ✅ Definiert |
| G-7 | Kosten-Schätzungen für Reagenzien | System-Integrator | ✅ Definiert |
| G-8 | Kanzler erhält periodische Template-Zusammenfassung | Kanzler (nur Übersicht) | ✅ Definiert |
| G-9 | Quartiermeister berücksichtigt template_feedback | Quartiermeister | ✅ Definiert |
| G-10 | atlas_version_ref ist Pass-Through, kein LLM-Zugriff | Questor (intern) | ✅ Definiert |
| G-11 | loop_selection_weights optional im QuestorSpec | Quartiermeister | ✅ Definiert |
| G-12 | planning_hints als optionales Feld | Quartiermeister | ✅ Definiert |

---

## Appendix B: Sicherheitsregeln (Zusammenfassung)

| Regel | Quelle |
|---|---|
| Keine physische Ausführung ohne Envelope | Hauptreferenz |
| Keine physische Ausführung ohne Gate | Hauptreferenz |
| Keine physische Ausführung ohne Lease | Hauptreferenz |
| LLM nur Advisor, niemals final | Questor v0.2.3 |
| Questor schreibt nicht in Atlas/Archiv | Hauptreferenz |
| Questor setzt ESTOP nicht zurück | Hauptreferenz |
| Questor vergibt keine Leases | Hauptreferenz |
| Blackbox bleibt lokal | Hauptreferenz |
| Operational ≠ Scientific | Hauptreferenz |
| ESTOP ≠ LEASE_DENIED | Hauptreferenz |
| Fail-Closed bei Unklarheit | Questor v0.2.3 |
| NaN/Infinity → Fail-Closed | C18 |
| atlas_version_ref ist Pass-Through | QuestCompass v0.1.0 |
| HAL-Bridge sendet keine Kommandos bei SAFETY_ABORT | Diese Datei |
| Recovery NUR aus WAL | Diese Datei |
| Ledger ist READ-ONLY nach Abschluss | Diese Datei |

---