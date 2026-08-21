# 🔌 HAL — HARDWARE ABSTRACTION LAYER

| Feld | Wert |
| :--- | :--- |
| **Dateiname** | `specs/HAL.md` |
| **Version** | 1.0.0 (New Architecture) |
| **Status** | **BINDEND** — HAL-Spezifikation |
| **System** | MYRMEX v2.4.0 + Questor v0.2.3 + HAL v0.2.0 |
| **Schicht** | Layer 1 (specs/) — referenziert foundation/ |
| **Datum** | 21. August 2026 |

---

## 0. Geltung und Änderungsregeln

Dieses Dokument definiert die vollständige HAL-Spezifikation.

**Regel:** Dieses Dokument referenziert Verträge aus `CONTRACTS.md` und Sicherheitsregeln aus `CHARTER.md`.
Es definiert keine neuen Verträge und keine neuen Sicherheitsregeln.

**Konfliktregel:** Bei Widersprüchen gilt `CHARTER.md` > `CONTRACTS.md` > dieses Dokument.

---

## §1 HAL-Übersicht und Grundprinzipien

### §1.1 Position im System

HAL ist Schicht 1 im MYRMEX-System (→ CHARTER §1.1).

```
┌─────────────────────────────────────────────────────────────────┐
 │                        QUESTOR (Schicht 2)                       │
 │  QuestCompass → PolicyEvaluator → HAL-Bridge                    │
 └───────────────────────────────┬─────────────────────────────────┘
                                 │ HALCommand / ProcessCommand
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
 │                     HAL INTERFACE (Schicht 1)                    │
 │  get_environment_manifest() · execute_command() · ...           │
 │  Slot State Store · Zone Lock Manager · ESTOP Handler           │
 └───────────────────────────────┬─────────────────────────────────┘
                                 │ DeviceCommand
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
 │              DEVICE ADAPTER / COMPUTE ADAPTER / DUMMY            │
 └───────────────────────────────┬─────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
 │                   PHYSIS / COMPUTE (Schicht 0)                  │
 └─────────────────────────────────────────────────────────────────┘
```

### §1.2 Die sechs HAL-Grundprinzipien

| # | Prinzip | Bedeutung | CHARTER-Referenz |
| :--- | :--- | :--- | :--- |
| 1 | **Dünne Schicht** | HAL bleibt bewusst dünn. Intelligenz bleibt bei Gremium, Questor und Resource Governor. | — |
| 2 | **Deterministisch vor LLM** | HAL enthält keine LLM-Logik. Alle HAL-Entscheidungen sind deterministisch. | CHARTER §2 |
| 3 | **Fail-Closed** | Wenn ein Zustand nicht sicher bestimmt werden kann: kein Kommando ausführen, keinen Slot freigeben, keine Lease akzeptieren. | CHARTER §SR-10 |
| 4 | **Keine wissenschaftliche Interpretation** | HAL erhält keine Forschungsziele. HAL meldet keine wissenschaftlichen Kategorien. | CHARTER §SR-08 |
| 5 | **Keine Lease-Vergabe** | HAL vergibt keine Leases. Leases kommen ausschließlich vom Resource Governor. | CHARTER §SR-06 |
| 6 | **Keine Blackbox-Übergabe** | HAL gibt keine Blackbox-Inhalte an das Gremium weiter. | CHARTER §SR-07 |

### §1.3 Was HAL DARF

| Erlaubt | Begründung |
| :--- | :--- |
| Hardware- oder Compute-Kommandos ausführen | Kernaufgabe |
| Slot-Zustände melden | Zustandsprüfung |
| Lease-Referenzen formal prüfen oder durch den Resource Governor prüfen lassen | Lease-Validierung |
| ESTOP melden und ESTOP-Zustände verwalten | Sicherheitsfunktion |
| Hardware-Interlocks erkennen und melden | Sicherheitsfunktion |
| Zonen-Locks anfragen und verwalten | Kollisionsvermeidung |
| Langzeit-Prozesse verwalten (Start, Hold, Resume, Abort) | Prozessmanagement |
| Technische Fehler operational melden | Fehlerbehandlung |
| Sicherheitsfehler als SAFETY melden | Fehlerbehandlung |
| Kommandos idempotent behandeln | Crash-Sicherheit |
| Audit-Logs für Operationen schreiben | Nachvollziehbarkeit |
| Dummy-Modi für Tests bereitstellen | Testbarkeit |
| Unklare Zustände nach Crash als unsicher melden | Fail-Closed |

### §1.4 Was HAL NICHT DARF

| Verboten | CHARTER-Referenz |
| :--- | :--- |
| Leases vergeben | CHARTER §SR-06 |
| Leases verlängern | CHARTER §SR-06 |
| Leases eigenmächtig erneuern | CHARTER §SR-06 |
| Wissenschaftliche Ziele interpretieren | CHARTER §SR-08 |
| Atlas-Signale schreiben | CHARTER §SR-04 |
| Archiv-Einträge schreiben | CHARTER §SR-04 |
| Kristalle erzeugen | CHARTER §SR-04 |
| Wegmarken erzeugen | CHARTER §SR-04 |
| Ideen bewerten | CHARTER §SR-04 |
| Questor-Logik ersetzen | — |
| ESTOP eigenmächtig zurücksetzen | CHARTER §SR-05 |
| Hardware-Interlocks eigenmächtig zurücksetzen | CHARTER §SR-05 |
| Blackbox-Inhalte an das Gremium weitergeben | CHARTER §SR-07 |
| Finale Sicherheitsfreigaben erteilen | CHARTER §SR-13 |
| LLM-Entscheidungen als sicherheitskritische Endentscheidung nutzen | CHARTER §SR-13 |
| Zonen-Locks eigenmächtig vergeben | CHARTER §SR-06 |

---

## §2 HAL-Knoten und Architektur

### §2.1 HAL Interface

Der zentrale Vertragsendpunkt. Bietet die 16 Funktionen aus → CONTRACTS §3.12.

### §2.2 Device Adapter

Der Device Adapter ist die geräte- oder compute-spezifische Umsetzung.

Mögliche Adapter:
- `DummyAdapter`
- `SimulationAdapter`
- `ComputeAdapter`
- `LabHardwareAdapter`
- `SandboxAdapter`
- `LiquidHandlerAdapter`
- `ReactorAdapter`
- `IncubatorAdapter`
- `GPUClusterAdapter`

**Regeln:**
- Der Adapter darf keine Lease vergeben (→ CHARTER §SR-06).
- Der Adapter darf keine Sicherheitsregeln umgehen.

### §2.3 Slot State Store

Verwaltet Slot-Zustände (→ CONTRACTS §3.7).

**Regel:** Quelle der Wahrheit für Leases ist nicht HAL, sondern der Resource Governor.
HAL darf Slot-Zustände technisch führen, aber Lease-Gültigkeit nicht eigenmächtig erzeugen.

### §2.4 Process State Store

Verwaltet Langzeit-Prozess-Zustände (→ CONTRACTS §3.9).

Für jedes aktive Gerät oder Compute-Job wird ein Prozesszustand geführt:
- `process_id`
- `device_job_id`
- `process_state`
- `resume_token`
- `safe_hold_policy`
- `stage_release_policy`

### §2.5 Zone Lock Manager

Verwaltet zonenbasierte Mutex-Locks (→ CONTRACTS §3.8).

Zonen können sein:
- Gemeinsame Schienen
- Kinematische Kollisionsräume
- Plattenpositionen
- Sicherheitsräume

**Regel:** HAL fragt Zonen-Locks beim Resource Governor an.
HAL verwaltet Zonen-Locks nicht eigenmächtig (→ CHARTER §SR-06).

### §2.6 ESTOP Handler

Verwaltet:
- ESTOP-Ereignisse
- ESTOP-Zustände
- Hardware-Interlock-Ereignisse
- Betroffene Slots
- Suspendierte Leases
- Audit-Events
- Reset-Anfragen

### §2.7 Operational Audit Writer

Schreibt HAL-Ereignisse nach `data/operational_logs/`.

**Regel:** Diese Logs sind operational, nicht wissenschaftlich (→ CHARTER §SR-08).

---

## §3 Slot-Management

### §3.1 Slot-Zustandsmaschine

→ Siehe CONTRACTS §7.2 für die vollständige Zustandsmaschine.

| Zustand | Bedeutung |
| :--- | :--- |
| `FREE` | Slot verfügbar |
| `RESERVED` | Slot reserviert |
| `ACTIVE` | Slot aktiv |
| `ERROR` | Fehlerzustand |
| `ESTOP_SUSPENDED` | ESTOP aktiv |
| `INTERLOCKED` | Hardware-Interlock aktiv |
| `MAINTENANCE` | Wartung |
| `OFFLINE` | Nicht erreichbar |

### §3.2 Übergangstabelle

| Von | Nach | Auslöser |
| :--- | :--- | :--- |
| `FREE` | `RESERVED` | Gültige Lease-Reservierung |
| `RESERVED` | `ACTIVE` | Kommando akzeptiert |
| `ACTIVE` | `FREE` | Erfolgreiche Ausführung und Freigabe |
| `ACTIVE` | `ERROR` | Fehler oder unklarer Zustand |
| `ACTIVE` | `ESTOP_SUSPENDED` | ESTOP |
| `ACTIVE` | `INTERLOCKED` | Hardware-Interlock |
| `RESERVED` | `FREE` | Lease abgelaufen oder widerrufen |
| `ERROR` | `FREE` | Erfolgreiche Reconciliation |
| `ESTOP_SUSPENDED` | `FREE` | ESTOP zurückgesetzt und Lease gültig |
| `INTERLOCKED` | `FREE` | Hardware-Interlock zurückgesetzt, safe_state_verified, manuelle Bestätigung |
| `MAINTENANCE` | `OFFLINE` | Wartung beendet oder Gerät getrennt |
| `OFFLINE` | `FREE` | Gerät wieder verfügbar und geprüft |

### §3.3 Harte Regel für `INTERLOCKED`

→ Siehe CHARTER §SR-09 für die ESTOP/Interlock-Regel.

- Kein `execute_command()`
- Keine automatische Reconciliation auf `FREE`
- Keine Rückkehr in `FREE` ohne manuelle Bestätigung
- `safe_state_verified` muss `true` sein
- `physical_reset_required` muss erfüllt sein

---

## §4 Zonen-Mutex-Modellierung

### §4.1 Zweck

Die zonenbasierte Mutex-Modellierung dient dazu, gemeinsame physische Räume zu schützen:
- Gemeinsame Schienen
- Fahrwege
- Kinematische Kollisionsräume
- Plattenpositionen
- Sicherheitsräume

### §4.2 Zonen-Lock-Anfrage

HAL fragt Zonen-Locks beim Resource Governor an.

→ Siehe CONTRACTS §3.8 für den ZoneState-Vertrag.

### §4.3 Zonen-Lock-Antwort

| Status | Bedeutung |
| :--- | :--- |
| `GRANTED` | Zonen-Lock gewährt |
| `DENIED` | Zonen-Lock abgelehnt |
| `TIMEOUT` | Zonen-Lock-Anfrage hat zu lange gedauert |

### §4.4 Fehlercodes

| Fehler | Bedeutung | Fehlerklasse |
| :--- | :--- | :--- |
| `ZONE_LOCK_UNAVAILABLE` | Zonen-Lock ist nicht verfügbar | OPERATIONAL |
| `ZONE_LOCK_TIMEOUT` | Zonen-Lock-Anfrage hat zu lange gedauert | OPERATIONAL |
| `ZONE_LOCK_DENIED` | Zonen-Lock wurde abgelehnt | OPERATIONAL |
| `ZONE_LOCK_EXPIRED` | Zonen-Lock ist abgelaufen | OPERATIONAL |

→ Siehe CHARTER §SR-08 für die Operational/Scientific-Trennung.

---

## §5 ESTOP und Hardware-Interlocks

### §5.1 Auslösung

ESTOP darf ausgelöst werden durch:
- Physische Gefahr
- Sicherheitsgrenzwertverletzung
- Hardware-Interlock
- Externe Sicherheitskette
- Manuelle Sicherheitsauslösung
- Testauslösung im TEST-Modus

ESTOP darf **nicht** ausgelöst werden durch:
- Ressourcenkonflikt (→ CHARTER §SR-09)
- Lease-Konflikt (→ CHARTER §SR-09)
- Timeout ohne Sicherheitsbezug
- OOM ohne Sicherheitsbezug
- CUDA-OOM (→ CHARTER §SR-08)
- Wissenschaftlichen Fehlschlag (→ CHARTER §SR-08)

### §5.2 Hardware-Interlock vs Software-ESTOP

| Merkmal | Software-ESTOP | Hardware-Interlock |
| :--- | :--- | :--- |
| `origin` | `SOFTWARE` | `HARDWARE_INTERLOCK` |
| Auslösung | Software entscheidet | Hardware zieht Stecker |
| Kommunikation | HAL kann antworten | HAL kann nicht antworten |
| Reset | Software-Reset möglich | Physischer Reset erforderlich |
| `physical_reset_required` | `false` | `true` |
| `device_reachable` | `true` | oft `false` |
| `safe_state_verified` | oft `true` | oft `false` |
| `inspection_required` | `false` | oft `true` |

→ Siehe CONTRACTS §3.10 für den EstopState-Vertrag.
→ Siehe CONTRACTS §3.11 für den HardwareInterlockEvent-Vertrag.

### §5.3 Wirkung

Bei `ACTIVE` oder `LATCHED`:
1. Keine neuen Kommandos ausführen
2. Aktive Kommandos kontrolliert stoppen
3. Betroffene Slots auf `ESTOP_SUSPENDED` oder `INTERLOCKED`
4. Betroffene Zonen auf `ESTOP_SUSPENDED` oder `INTERLOCKED`
5. Betroffene Leases dem Resource Governor als suspendiert melden
6. Questor erhält Sicherheitsabbruch
7. Audit-Log wird geschrieben

→ Siehe CHARTER §SR-09 für die ESTOP-Regel.

### §5.4 Rücksetzung

ESTOP darf **nicht** zurückgesetzt werden durch:
- Questor (→ CHARTER §SR-05)
- LLM (→ CHARTER §SR-13)
- Automatischen Retry
- Device Adapter

ESTOP darf zurückgesetzt werden durch:
- Autorisierten Sicherheitsprozess
- Menschliche Freigabe
- Definierten Audit-Prozess
- Optional Kanzler-/Sicherheitsfreigabe, falls konfiguriert

Für Hardware-Interlocks gilt zusätzlich:
- `physical_reset_required` muss erfüllt sein
- `safe_state_verified` muss `true` sein
- `inspection_required` muss erfüllt sein
- Manuelle Bestätigung ist zwingend

### §5.5 ESTOP-Zustandsmaschine

→ Siehe CONTRACTS §7.5 für die vollständige Zustandsmaschine.

| Zustand | Bedeutung |
| :--- | :--- |
| `NORMAL` | Kein aktiver ESTOP |
| `ACTIVE` | ESTOP ausgelöst, Ausführung gestoppt |
| `LATCHED` | ESTOP bleibt aktiv bis manueller Quittierung |
| `TEST` | ESTOP-Testmodus ohne echte physische Auslösung |

---

## §6 Langzeit-Prozessmodell

### §6.1 Zweck

Das Langzeit-Prozessmodell dient dazu, geräteautonome Prozesse zu verwalten, die länger dauern als ein einzelner RPC-Aufruf.

Beispiele:
- 72-Stunden-Inkubation
- Lange Temperprozesse
- Lange Materialtests
- Lange Compute-Jobs

### §6.2 Trennung von Kommando und Prozess

→ Siehe CONTRACTS §3.3 und §3.4 für die HALCommand- und ProcessCommand-Verträge.

```
timeout_s:                   Kommando-Timeout (RPC-Aufruf, Sekunden)
expected_process_duration_s: Prozess-Dauer (physikalisch, Sekunden bis Tage)
```

Diese sind **STRIKT** getrennt.

**Beispiel:** `timeout_s = 60.0`, `expected_process_duration_s = 259200.0` (72h)

### §6.3 Prozess-Modi

| Modus | Bedeutung |
| :--- | :--- |
| `START` | Prozess starten |
| `MONITOR` | Prozess überwachen |
| `RESUME` | Prozess fortsetzen |
| `HOLD` | Prozess anhalten |
| `ABORT` | Prozess abbrechen |
| `RELEASE_STAGE` | Nächste Stufe freigeben |

### §6.4 Prozess-Zustandsmaschine

→ Siehe CONTRACTS §7.3 für die vollständige Zustandsmaschine.

| Zustand | Bedeutung |
| :--- | :--- |
| `PENDING` | Prozess wartet |
| `RUNNING` | Prozess läuft |
| `PAUSED` | Prozess pausiert |
| `SAFE_HOLD` | Prozess sicher angehalten |
| `WAITING_FOR_RELEASE` | Wartet auf manuelle Freigabe |
| `COMPLETED` | Erfolgreich abgeschlossen |
| `ABORTED` | Abgebrochen |
| `FAULT` | Fehler |
| `UNKNOWN` | Zustand unklar (nach Crash) |

### §6.5 Lease-Expiry-Policy

| Policy | Bedeutung |
| :--- | :--- |
| `SAFE_HOLD` | Prozess sicher anhalten, aber nicht zerstören |
| `ABORT_TO_SAFE_STATE` | Prozess in sicheren Zustand abbrechen |
| `CONTINUE_PASSIVE_SAFE` | Prozess passiv weiterlaufen lassen (z.B. Inkubator hält Temperatur) |
| `REQUIRES_RECONCILE` | Zustand muss geklärt werden |

### §6.6 Stage-Release-Policy

Für mehrstufige Prozesse mit sicherheitskritischen Stufen:

→ Siehe CONTRACTS §4.5 für den StageReleasePolicy-Vertrag.

**Beispiel:**
```yaml
stages:
  - stage_id: incubation_72h
    release_required: false
    auto_start_allowed: true
  - stage_id: uv_exposure
    release_required: true
    release_authority: SAFETY_PROCESS_OR_HUMAN
    auto_start_allowed: false
```

### §6.7 Resume-Token

Für idempotentes Fortsetzen nach Restart:

**Regeln:**
- `resume_token` wird bei jedem Zustandswechsel aktualisiert
- `resume_token` ist erforderlich für `RESUME`
- Wenn `resume_token` ungültig ist: `RECOVERY_UNSAFE`

---

## §7 Compute-Ressourcenmodell

### §7.1 Zweck

Das Compute-Ressourcenmodell unterscheidet Labor-Aktuatorik von Compute-Ressourcen.

### §7.2 Resource-Class

| Klasse | Bedeutung |
| :--- | :--- |
| `LAB_ACTUATOR` | Physischer Laboraktuator (Roboterarm, Pipettierroboter, Inkubator) |
| `COMPUTE_NODE` | Compute-Ressource (GPU-Cluster, CPU-Node) |
| `SIMULATION_ENVIRONMENT` | Simulationsumgebung |
| `SANDBOX_ENVIRONMENT` | Sandbox-Umgebung |
| `HYBRID_SLOT` | Kombination aus Labor und Compute |

→ Siehe CONTRACTS §3.2 für den SlotDescriptor-Vertrag.

### §7.3 Compute-spezifische Fehlercodes

| Fehler | Bedeutung | Fehlerklasse |
| :--- | :--- | :--- |
| `COMPUTE_OOM` | Host-RAM-OOM | OPERATIONAL |
| `CUDA_OOM` | GPU-Speicher-OOM | OPERATIONAL |
| `GPU_LOST` | GPU nicht erreichbar | OPERATIONAL |
| `SCHEDULER_REJECTED` | Scheduler hat Job abgelehnt | OPERATIONAL |
| `NODE_UNAVAILABLE` | Node nicht erreichbar | OPERATIONAL |
| `CONTAINER_OOM_KILLED` | Container wurde wegen OOM getötet | OPERATIONAL |
| `CONTAINER_CRASHED` | Container ist abgestürzt | OPERATIONAL |

→ Siehe CHARTER §SR-08 für die Operational/Scientific-Trennung.

**Ausnahme:** Wenn ein Compute-Fehler tatsächlich eine physische Gefahr verursacht (z.B. Brand oder Kühlungsausfall), dann ist es nicht der CUDA-Fehler selbst, sondern ein physischer Sensor, der `SAFETY` auslöst.

### §7.4 Compute-spezifische Slot-Felder

→ Siehe CONTRACTS §3.2 für die vollständigen SlotDescriptor-Felder.

```
accelerator_type: Optional[str]
accelerator_count: int
accelerator_memory_gb: Optional[float]
supported_runtimes: list[str]
```

---

## §8 Parameter-Schema-Registry

### §8.1 Zweck

Die Parameter-Schema-Registry dient dazu, komplexe Geräteprofile sicher zu validieren.

### §8.2 Felder

→ Siehe CONTRACTS §3.3 und §3.4 für die HALCommand- und ProcessCommand-Verträge.

| Feld | Bedeutung |
| :--- | :--- |
| `parameter_schema_ref` | Referenz auf das Schema der Parameter |
| `parameter_schema_version` | Version des Schemas |
| `parameter_checksum` | Prüfsumme der Parameter |
| `payload_artifact_ref` | Referenz auf ein externes Artifact |

### §8.3 Regeln

| Regel | Bedeutung |
| :--- | :--- |
| Wenn eine Capability komplexe Profile erwartet, muss `parameter_schema_ref` gesetzt sein. | Schema-Pflicht |
| Wenn `parameter_schema_ref` gesetzt ist, muss `parameter_checksum` gesetzt sein. | Checksum-Pflicht |
| Wenn Schema unbekannt oder Checksumme falsch: `PARAMETER_INVALID`. | Fail-Closed |
| HAL interpretiert die Parameter nicht wissenschaftlich. | Keine wissenschaftliche Interpretation (→ CHARTER §SR-08) |
| HAL prüft nur formal: Schema bekannt, Version erlaubt, Checksumme korrekt, Größe erlaubt. | Formale Prüfung |

### §8.4 Fehlercodes

| Fehler | Bedeutung | Fehlerklasse |
| :--- | :--- | :--- |
| `PARAMETER_SCHEMA_UNKNOWN` | Schema ist unbekannt | OPERATIONAL |
| `PARAMETER_CHECKSUM_MISMATCH` | Checksumme stimmt nicht | OPERATIONAL |
| `PARAMETER_INVALID` | Parameter ist ungültig | OPERATIONAL |

---

## §9 HAL-Schnittstellen

→ Siehe CONTRACTS §3.12 für die vollständige HAL-Interface-Definition.

Die folgenden 16 Funktionen sind verbindlich:

| # | Funktion | Zweck |
| :--- | :--- | :--- |
| 1 | `get_environment_manifest()` | Umgebungsinformationen abrufen |
| 2 | `get_slot_state(slot_id)` | Slot-Zustand abrufen |
| 3 | `get_zone_state(zone_id)` | Zonen-Zustand abrufen |
| 4 | `execute_command(command)` | Kommando ausführen |
| 5 | `start_process(process_command)` | Langzeit-Prozess starten |
| 6 | `monitor_process(process_id)` | Prozess überwachen |
| 7 | `hold_process(process_id)` | Prozess anhalten |
| 8 | `resume_process(process_id, resume_token)` | Prozess fortsetzen |
| 9 | `abort_process(process_id)` | Prozess abbrechen |
| 10 | `release_stage(process_id, stage_id, release_authority)` | Stufe freigeben |
| 11 | `report_estop(reason, trigger_source)` | ESTOP melden |
| 12 | `report_hardware_interlock(interlock_event)` | Hardware-Interlock melden |
| 13 | `get_estop_state()` | ESTOP-Zustand abrufen |
| 14 | `reconcile_slot_state(slot_id)` | Slot-Zustand nach Crash klären |
| 15 | `reconcile_process_state(process_id)` | Prozess-Zustand nach Crash klären |
| 16 | `get_command_status(command_id)` | Kommando-Status abrufen |

---

## §10 Fehlermodell und Fehlerbehandlung

### §10.1 Fehlerklassen

→ Siehe CONTRACTS §9.1 für die vollständige Fehlerklassen-Definition.
→ Siehe CHARTER §SR-08 für die Operational/Scientific-Trennung.

| Klasse | Bedeutung | Wissenschaftliches Signal? |
| :--- | :--- | :--- |
| `OPERATIONAL` | Prozessfehler, Crash, Timeout, Lease-Problem | **Nein** |
| `SAFETY` | Sicherheitsverletzung, ESTOP | Ja, mit Sicherheitsprüfung |

HAL darf **keine** wissenschaftliche Fehlerklasse verwenden.

### §10.2 Operationale Fehler (HAL)

→ Siehe CONTRACTS §9.2 für die vollständige Liste der operationalen Fehler.

```
LEASE_INVALID, LEASE_EXPIRED, LEASE_REVOKED, LEASE_SLOT_MISMATCH,
LEASE_VALIDATION_UNSAFE, SLOT_BUSY, SLOT_UNAVAILABLE,
ZONE_LOCK_UNAVAILABLE, ZONE_LOCK_TIMEOUT, ZONE_LOCK_DENIED,
ZONE_LOCK_EXPIRED, COMMAND_TIMEOUT, PROCESS_TIMEOUT,
DEVICE_UNAVAILABLE, OOM, COMPUTE_OOM, CUDA_OOM, GPU_LOST,
SCHEDULER_REJECTED, NODE_UNAVAILABLE, CONTAINER_OOM_KILLED,
CONTAINER_CRASHED, HAL_INTERNAL_ERROR, DUPLICATE_COMMAND_BLOCKED,
DUPLICATE_PROCESS_BLOCKED, COMMAND_INVALID, PROCESS_INVALID,
PARAMETER_INVALID, PARAMETER_SCHEMA_UNKNOWN, PARAMETER_CHECKSUM_MISMATCH,
TIMEOUT_EXCEEDS_LIMIT, PROCESS_DURATION_EXCEEDS_LIMIT,
PHYSICAL_EXECUTION_FORBIDDEN, COMPUTE_EXECUTION_FORBIDDEN,
RECOVERY_UNSAFE, RESUME_TOKEN_INVALID, STAGE_RELEASE_DENIED
```

Alle diese Fehler sind `OPERATIONAL`.

### §10.3 Sicherheitsfehler (HAL)

→ Siehe CONTRACTS §9.3 für die vollständige Liste der Sicherheitsfehler.

```
ESTOP_RECEIVED, HARDWARE_INTERLOCK_TRIGGERED,
EXTERNAL_SAFETY_CHAIN_TRIGGERED, SAFETY_LIMIT_VIOLATION,
UNSAFE_SLOT_STATE, UNSAFE_ZONE_STATE,
PHYSICAL_INTERLOCK_TRIGGERED, SAFETY_RESET_REQUIRED
```

Alle diese Fehler sind `SAFETY`.

### §10.4 HAL-Fehlerregeln

| Regel | Bedeutung | CHARTER-Referenz |
| :--- | :--- | :--- |
| HAL behandelt CUDA_OOM als OPERATIONAL, nicht als SAFETY | Compute-Fehler sind operational | CHARTER §SR-08 |
| HAL behandelt LEASE_DENIED als OPERATIONAL, nicht als ESTOP | Ressourcenkonflikte sind operational | CHARTER §SR-09 |
| HAL behandelt Hardware-Interlock als SAFETY | Hardware-Interlocks sind sicherheitsrelevant | CHARTER §SR-09 |
| HAL behandelt Software-ESTOP als SAFETY | ESTOP ist sicherheitsrelevant | CHARTER §SR-09 |
| HAL meldet keine wissenschaftlichen Fehlerklassen | Keine wissenschaftliche Interpretation | CHARTER §SR-08 |

---

## §11 Timeout-Semantik

### §11.1 Kommando-Timeout

Jedes Kommando hat `timeout_s` (→ CONTRACTS §3.3).

**Regeln:**
- `timeout_s` muss positiv sein
- `timeout_s` darf `max_command_timeout_s` aus dem Manifest nicht überschreiten
- Wenn `timeout_s` fehlt oder ungültig ist: `COMMAND_INVALID`
- Wenn `timeout_s` zu groß ist: `TIMEOUT_EXCEEDS_LIMIT`

### §11.2 Prozess-Dauer

Jeder Prozess hat `expected_process_duration_s` (→ CONTRACTS §3.4).

**Regeln:**
- `expected_process_duration_s` muss positiv sein
- `expected_process_duration_s` darf `max_process_duration_s` aus dem SlotDescriptor nicht überschreiten
- Wenn `expected_process_duration_s` zu groß ist: `PROCESS_DURATION_EXCEEDS_LIMIT`

### §11.3 Timeout bei Kommandos

Bei Timeout:
1. Kommando wird als `TIMEOUT` gemeldet
2. Wenn der Slot physisch ist und der Zustand unklar bleibt:
   - Slot auf `ERROR`
   - `reconcile_slot_state` erforderlich
   - **Kein blinder Retry**
3. Fehlerklasse: `OPERATIONAL`

### §11.4 Timeout bei Prozessen

Bei Prozess-Timeout:
1. Prozess wird als `FAULT` gemeldet
2. `on_lease_expiry_policy` wird angewendet
3. Wenn `SAFE_HOLD`: Prozess wird sicher angehalten
4. Wenn `ABORT_TO_SAFE_STATE`: Prozess wird in sicheren Zustand abgebrochen
5. Wenn `CONTINUE_PASSIVE_SAFE`: Prozess läuft passiv weiter
6. Wenn `REQUIRES_RECONCILE`: Zustand muss geklärt werden
7. Fehlerklasse: `OPERATIONAL`

---

## §12 Crash-Recovery und Reconciliation

### §12.1 Grundsätze

Nach einem Crash gilt:
- **Kein automatischer Neustart von Kommandos**
- **Kein automatischer Neustart von Prozessen**
- **Kein blinder Retry**
- **Keine automatische Slot-Freigabe bei unklarem Zustand**
- **Keine automatische Zonen-Freigabe bei unklarem Zustand**

→ Siehe CHARTER §SR-10 für die Fail-Closed-Regel.

### §12.2 Recovery-Schritte

1. `get_estop_state()` prüfen
2. `get_slot_state()` prüfen
3. `get_zone_state()` prüfen
4. `get_command_status()` prüfen, falls vorhanden
5. `reconcile_slot_state()` aufrufen
6. `reconcile_process_state()` aufrufen, falls Prozess aktiv war

### §12.3 Recovery-Entscheidung

| Zustand | Aktion |
| :--- | :--- |
| Zustand eindeutig | Slot kann kontrolliert freigegeben oder weitergenutzt werden. Prozess kann kontrolliert fortgesetzt oder abgebrochen werden. |
| Zustand unklar | Slot auf `ERROR`. Prozess auf `UNKNOWN`. Ergebnis: `RECOVERY_UNSAFE`. |

**Regel:** HAL darf Recovery nicht als wissenschaftliche Entscheidung behandeln (→ CHARTER §SR-08).

---

## §13 Idempotenz

### §13.1 Grundsatz

HAL muss Kommandos und Prozesse idempotent behandeln.

→ Siehe CONTRACTS §8.2 für die HAL-Idempotenz-Regeln.

### §13.2 Idempotenz-Schlüssel

```
hal_idempotency_key        = command_id:lease_ref:slot_id
hal_process_idempotency_key = process_id:lease_ref:slot_id
```

### §13.3 Regeln

| Regel | Bedeutung |
| :--- | :--- |
| Ein bereits ausgeführtes Kommando darf nicht erneut ausgeführt werden. | Keine doppelte Ausführung |
| Ein bereits gestarteter Prozess darf nicht erneut gestartet werden. | Keine doppelte Ausführung |
| Ein blockiertes Duplikat darf keine Seiteneffekte erzeugen. | Keine doppelten Seiteneffekte |
| Ein Duplikat wird als `DUPLICATE_BLOCKED` gemeldet. | Status-Meldung |
| Idempotenz ist besonders wichtig nach Crash, Timeout oder Recovery. | Crash-Sicherheit |

---

## §14 Logging und Audit

### §14.1 Erlaubte Event-Typen

→ Siehe CHARTER §SR-08 für die Operational/Scientific-Trennung.

```
command_received
command_accepted
command_denied
command_started
command_finished
command_timeout
command_duplicate_blocked
process_started
process_state_changed
process_safe_hold
process_waiting_for_release
process_completed
process_aborted
process_fault
process_unknown
lease_validation_failed
slot_state_changed
zone_state_changed
zone_lock_requested
zone_lock_granted
zone_lock_denied
zone_lock_expired
estop_triggered
estop_acknowledged
estop_reset_requested
estop_reset_confirmed
hardware_interlock_triggered
reconciliation_started
reconciliation_finished
```

### §14.2 Zielverzeichnis

```
data/operational_logs/
```

### §14.3 Verbotene Ziele

| Verboten | CHARTER-Referenz |
| :--- | :--- |
| Schreiben nach `data/archiv/` | CHARTER §SR-04 |
| Schreiben nach `data/atlas/` | CHARTER §SR-04 |
| Schreiben nach `data/questor_blackbox/` | CHARTER §SR-07 |
| Speichern wissenschaftlicher Hypothesen | CHARTER §SR-08 |
| Speichern von Questor-internen Trails | CHARTER §SR-50 |
| Speichern von Blackbox-Inhalten | CHARTER §SR-07 |

---

## §15 HAL und Questor

### §15.1 Kommunikation

Questor kommuniziert mit HAL über eine HAL-Bridge (→ specs/QUESTOR.md §8).

Questor darf nicht direkt auf Hardware zugreifen (→ CHARTER §SR-12).

Die HAL-Bridge übersetzt Questor-Intentionen in `HALCommand`- oder `ProcessCommand`-Objekte.

### §15.2 Regeln

| Regel | CHARTER-Referenz |
| :--- | :--- |
| Keine wissenschaftlichen Ziele in `HALCommand.parameters` | CHARTER §SR-08 |
| Keine Atlas-Signale in `HALCommand.parameters` | CHARTER §SR-04 |
| Keine Gate-Logik in HAL | — |
| Keine Lease-Vergabe in Questor oder HAL | CHARTER §SR-06 |

### §15.3 Questor erhält von HAL

- `HALCommandResult` (→ CONTRACTS §3.5)
- `ProcessResult` (→ CONTRACTS §3.6)
- Slot-Zustände (→ CONTRACTS §3.7)
- Zonen-Zustände (→ CONTRACTS §3.8)
- ESTOP-Zustände (→ CONTRACTS §3.10)

### §15.4 Questor meldet daraus resultierende Ergebnisse

Questor meldet die Ergebnisse im `questor_ergebnis_paket` (→ CONTRACTS §2.1).

---

## §16 HAL und Resource Governor

### §16.1 Zuständigkeiten

Resource Governor ist für Leases zuständig.

HAL darf:
- Lease-Referenzen prüfen
- Lease-Status anfragen
- ESTOP-bedingte Lease-Suspendierung melden
- Zonen-Locks anfragen
- Zonen-Lock-Status anfragen

HAL darf **nicht**:
- Leases erzeugen (→ CHARTER §SR-06)
- Leases verlängern (→ CHARTER §SR-06)
- Leases widerrufen (→ CHARTER §SR-06)
- Lease-Kontingente verwalten
- Pfad-Leases eigenmächtig koordinieren
- Zonen-Locks eigenmächtig vergeben (→ CHARTER §SR-06)

### §16.2 Pfad-Leases

Pfad-Leases bleiben Aufgabe des Resource Governors.

→ Siehe CONTRACTS §4.3 für den PathLease-Vertrag.

### §16.3 Zonen-Locks

Zonen-Locks werden vom Resource Governor verwaltet.

HAL sieht normalerweise nur slotbezogene Lease-Referenzen.

---

## §17 HAL und Sicherheitsmodus

### §17.1 Sicherheitsmodi

→ Siehe CONTRACTS §1.3 für die SecurityMode-Definition.

| Modus | Bedeutung |
| :--- | :--- |
| `NORMAL` | Produktivbetrieb. Physische Ausführung erlaubt. |
| `SANDBOX` | Simulationsbetrieb. Keine physische Wirkung auf echte Proben. |
| `DEV_SANDBOX_ONLY` | Reine Test/Dev-Umgebung. Keine Produktivdaten, keine echten Proben. |
| `RECOVERY` | Ausnahmezustand. Nur Zustandsklärung und Aufräumarbeiten. |

### §17.2 HAL-Reaktion auf Sicherheitsmodi

| Modus | Physisch | Compute | Sandbox |
| :--- | :--- | :--- | :--- |
| `NORMAL` | ✅ wenn `physical_actuation = true` und Lease `physical_execution_allowed = true` | ✅ wenn `compute_capable = true` und Lease `compute_execution_allowed = true` | ✅ |
| `SANDBOX` | ❌ | Nur Sandbox-Compute | ✅ wenn `sandbox_capable = true` |
| `DEV_SANDBOX_ONLY` | ❌ | Nur Dev-Compute | Nur Dev-Sandbox |
| `RECOVERY` | ❌ (außer `reconcile_*`) | ❌ (außer `reconcile_*`) | ❌ |

→ Siehe CHARTER §SR-35 bis §SR-39 für die Security-Mode-Regeln.

### §17.3 Fehler bei Modus-Mismatch

Wenn der Modus nicht zum Slot passt:

| Fehler | Fehlerklasse |
| :--- | :--- |
| `PHYSICAL_EXECUTION_FORBIDDEN` | OPERATIONAL |
| `COMPUTE_EXECUTION_FORBIDDEN` | OPERATIONAL |

→ Siehe CHARTER §SR-08 für die Operational/Scientific-Trennung.

---

## §18 Dummy-HAL

### §18.1 Zweck

Für Trockenlauf, Integrationstests und Implementierung ohne echte Hardware ist ein Dummy-HAL erforderlich.

### §18.2 Simulierbare Fehlermodi

Der Dummy-HAL muss folgende Modi simulieren können:

```
SUCCESS
LEASE_DENIED
LEASE_EXPIRED
LEASE_REVOKED
SLOT_BUSY
SLOT_UNAVAILABLE
ZONE_LOCK_UNAVAILABLE
ZONE_LOCK_DENIED
COMMAND_TIMEOUT
PROCESS_TIMEOUT
ESTOP
HARDWARE_INTERLOCK
OOM
COMPUTE_OOM
CUDA_OOM
GPU_LOST
SCHEDULER_REJECTED
NODE_UNAVAILABLE
CONTAINER_OOM_KILLED
CONTAINER_CRASHED
DEVICE_UNAVAILABLE
DUPLICATE_BLOCKED
DUPLICATE_PROCESS_BLOCKED
RECOVERY_UNSAFE
RESUME_TOKEN_INVALID
STAGE_RELEASE_DENIED
```

### §18.3 Zusätzliche Anforderungen

Der Dummy-HAL muss zusätzlich können:
- Slot-Zustände deterministisch zurückgeben
- Zonen-Zustände deterministisch zurückgeben
- ESTOP auslösen und zurücksetzen, aber nur über autorisierte Dummy-Funktionen
- Hardware-Interlock auslösen und zurücksetzen, aber nur über autorisierte Dummy-Funktionen
- Manifest bereitstellen
- Kommandos idempotent behandeln
- Prozesse idempotent behandeln
- Timeout simulieren
- Prozess-Timeout simulieren
- Unklaren Crash-Zustand simulieren
- Langzeit-Prozess mit SAFE_HOLD simulieren
- Langzeit-Prozess mit RESUME simulieren
- Langzeit-Prozess mit WAITING_FOR_RELEASE simulieren
- Operational-Audit-Ereignisse schreiben

### §18.4 Regel

Der Dummy-HAL darf **keine** echte Hardware ansprechen.

---

## §19 Implementierungsphasen

### §19.1 Übersicht

| Phase | Name | Dauer (Schätzung) |
| :--- | :--- | :--- |
| HAL-H0 | HAL-Vertrag in Hauptstruktur bestätigen | 1 Tag |
| HAL-H1 | Interface und Datenmodelle | 3–5 Tage |
| HAL-H2 | Slot- und Lease-Logik | 2–3 Tage |
| HAL-H3 | Zonen-Mutex und Prozess-Logik | 3–4 Tage |
| HAL-H4 | ESTOP und Hardware-Interlocks | 2–3 Tage |
| HAL-H5 | Compute-Modell und Parameter-Schema | 2–3 Tage |
| HAL-H6 | Dummy-HAL und Integration | 3–4 Tage |

### §19.2 Phase HAL-H0: HAL-Vertrag bestätigen

**Aufgaben:**
- HAL-Minimalvertrag mit dieser Datei abgleichen
- Dokumentenhierarchie bestätigen
- Keine sicherheitswidrigen Abweichungen zulassen

**Akzeptanz:**
- [ ] Strukturversion 1.1.1 bleibt maßgeblich
- [ ] HAL v0.2.0 ist als präzisierte Spezifikation akzeptiert

### §19.3 Phase HAL-H1: Interface und Datenmodelle

**Aufgaben:**
- `hal_interface.py`
- `dummy_hal.py`
- Pydantic-Modelle für alle HAL-Verträge (→ CONTRACTS §3)

**Akzeptanz:**
- [ ] Alle Modelle sind validierbar
- [ ] Keine wissenschaftlichen Felder
- [ ] Fehlerklassen sind korrekt getrennt
- [ ] Mindestens 40 Unit-Tests

### §19.4 Phase HAL-H2: Slot- und Lease-Logik

**Aufgaben:**
- Slot-State-Handling
- Lease-Validierung
- Slot-Mutex
- Timeout-Prüfung
- Idempotenzprüfung

**Akzeptanz:**
- [ ] Kein Slot wird doppelt belegt
- [ ] Ungültige Leases werden abgelehnt
- [ ] Timeouts werden korrekt gemeldet
- [ ] Duplikate werden blockiert
- [ ] Mindestens 25 Unit-Tests

### §19.5 Phase HAL-H3: Zonen-Mutex und Prozess-Logik

**Aufgaben:**
- Zone-State-Handling
- Zonen-Lock-Anfrage und -Antwort
- Prozess-State-Handling
- Langzeit-Prozess-Modell
- SAFE_HOLD und RESUME
- Stage-Release-Policy

**Akzeptanz:**
- [ ] Keine Zone wird doppelt belegt
- [ ] Zonen-Locks werden korrekt angefragt und freigegeben
- [ ] Langzeit-Prozesse können gestartet, angehalten und fortgesetzt werden
- [ ] Stage-Release funktioniert
- [ ] Mindestens 30 Unit-Tests

### §19.6 Phase HAL-H4: ESTOP und Hardware-Interlocks

**Aufgaben:**
- ESTOP-Zustandsmaschine
- Hardware-Interlock-Zustandsmaschine
- `report_estop`
- `report_hardware_interlock`
- `get_estop_state`
- `reconcile_slot_state`
- `reconcile_process_state`
- Audit-Events für ESTOP und Interlocks

**Akzeptanz:**
- [ ] ESTOP stoppt Kommandos
- [ ] ESTOP suspendiert Leases
- [ ] Hardware-Interlock stoppt Kommandos
- [ ] Hardware-Interlock suspendiert Leases und Zonen
- [ ] Kein ESTOP bei Ressourcenkonflikt (→ CHARTER §SR-09)
- [ ] Kein blinder Retry nach Crash
- [ ] Mindestens 25 Unit-Tests

### §19.7 Phase HAL-H5: Compute-Modell und Parameter-Schema

**Aufgaben:**
- Compute-Ressourcenmodell
- Compute-spezifische Fehlercodes
- Parameter-Schema-Registry
- Parameter-Schema-Validierung

**Akzeptanz:**
- [ ] Compute-Ressourcen werden korrekt angefragt
- [ ] Compute-Fehler sind operational (→ CHARTER §SR-08)
- [ ] Parameter-Schemas werden korrekt validiert
- [ ] Mindestens 20 Unit-Tests

### §19.8 Phase HAL-H6: Dummy-HAL und Integration

**Aufgaben:**
- Vollständiger Dummy-HAL
- Alle Fehlermodi
- Integration mit Questor-HAL-Bridge
- Integration mit Resource Governor
- Operational-Audit

**Akzeptanz:**
- [ ] Dummy kann alle relevanten Szenarien simulieren
- [ ] Keine echte Hardware nötig
- [ ] Suite H kann vorbereitet werden
- [ ] Mindestens 25 Integrationstests

---

## §20 Zusammenfassung der Architektur-Entscheidungen

| Thema | Entscheidung | Quelle |
| :--- | :--- | :--- |
| HAL ist dünne Schicht | Ja | §1.2 |
| HAL ist deterministisch | Ja, keine LLM-Logik | §1.2 |
| HAL ist fail-closed | Ja | §1.2 |
| HAL interpretiert keine wissenschaftlichen Ziele | Ja | §1.2 |
| HAL vergibt keine Leases | Ja | §1.4 |
| HAL gibt keine Blackbox weiter | Ja | §1.4 |
| Slot-Zustandsmaschine | 8 Zustände | §3.1 |
| INTERLOCKED ist härter als ESTOP_SUSPENDED | Ja | §3.3 |
| Zonen-Mutex | 4 Lock-Policies | §4 |
| ESTOP vs Hardware-Interlock | Strikt getrennt | §5.2 |
| Langzeit-Prozessmodell | SAFE_HOLD, RESUME, WAITING_FOR_RELEASE | §6 |
| Trennung timeout_s vs expected_process_duration_s | Strikt | §6.2 |
| Compute-Ressourcenmodell | 5 Resource-Classes | §7.2 |
| CUDA_OOM ist OPERATIONAL | Ja | §7.3 |
| Parameter-Schema-Registry | Schema + Checksum | §8 |
| HAL-Schnittstellen | 16 Funktionen | §9 |
| Fehlermodell | OPERATIONAL / SAFETY | §10 |
| Timeout-Semantik | Kommando vs Prozess | §11 |
| Crash-Recovery | Kein blinder Retry | §12 |
| Idempotenz | command_id:lease_ref:slot_id | §13 |
| Logging | Nur operational | §14 |
| Sicherheitsmodus | 4 Modi, HAL prüft | §17 |
| Dummy-HAL | Alle Fehlermodi simulierbar | §18 |
| Implementierungsphasen | HAL-H0 bis HAL-H6 | §19 |

---

## §21 Dokumentenhierarchie

Dieses Dokument steht in der Schicht `specs/` und referenziert:
- `foundation/CHARTER.md` für Sicherheitsregeln (CHARTER §SR-XX)
- `foundation/CONTRACTS.md` für Datenverträge (CONTRACTS §X.X)
- `specs/QUESTOR.md` für Questor-spezifische Details
- `specs/GREMIUM.md` für Gremium-spezifische Details

**Regel:** Änderungen an HAL-Modulen in diesem Dokument erfordern eine Versionsänderung und eine Überprüfung der referenzierten Dokumente.