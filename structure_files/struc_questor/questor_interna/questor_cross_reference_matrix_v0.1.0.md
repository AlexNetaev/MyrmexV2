# 🧭 QUESTOR-INTERNA: KREUZREFERENZ-MATRIX
## Interaktionen, Abhängigkeiten und Datenflüsse zwischen allen Questor-Interna-Teilen

| Feld | Wert |
|---|---|
| Dateiname | `questor_cross_reference_matrix_v0.1.0.md` |
| Version | 0.1.0 |
| System | MYRMEX v2.4.0 + Questor v0.2.3 |
| Status | Arbeitsstand — Architektur-Spezifikation, keine Implementierungsfreigabe |
| Bezug | `structure_questor_interna_v0.4.0.md`, Anhang C |
| | `structure_standalone_v2.4.0.md` v1.1.1, kanonisch |
| | `structure_hal_v0.2.0.md` |
| Sprache | Deutsch |
| Modus | Dry-Run / Spezifikation |

---

## 0. Dokumentenhierarchie und Geltung

```
1. structure_standalone_v2.4.0.md v1.1.1                    ← kanonisch
2. structure_hal_v0.2.0.md                                   ← HAL-Vertrag
3. structure_questor_interna_v0.4.0.md                       ← Questor-Interna GESAMT
4. diese Datei: questor_cross_reference_matrix_v0.1.0.md     ← Kreuzreferenz-Matrix
5. structure_standalone_questor_v0.2.3.md                    ← unterstützend
6. myrmex_questor_integration_tests_v0.4.0.md                ← Testgrundlage
```

Bei Widersprüchen gilt die kanonische Hauptreferenz.

Diese Datei ist Anhang C der Questor-Interna-Gesamtspezifikation.
Sie ist ein **Nachschlagewerk** und enthält keine neuen Spezifikationen.
Alle hier dokumentierten Interaktionen sind in den jeweiligen Detaildokumenten vollständig spezifiziert.

---

## 1. Zweck dieser Datei

Diese Datei definiert:

1. Die **Interaktionsmatrix** zwischen allen Teilen (A–S).
2. Die **Abhängigkeiten** zwischen den neuen Themen (K–S).
3. Die **Datenflüsse** zwischen Komponenten.
4. Die **gemeinsamen Datenverträge** und ihre Nutzer.
5. Die **Sicherheitsregeln** und ihre Herkunft.
6. Die **Testabdeckung** pro Thema.
7. Die **Implementierungsreihenfolge** und Phasenabhängigkeiten.

---

## 2. Teile-Übersicht

### 2.1 Bestehende Teile (aus v0.3.0)

| Teil | Name | Detaildokument |
|---|---|---|
| A | Questor-Zustandsmaschine | `structure_questor_interna_v0.3.0.md` §3–§8 |
| B | QuestCompass-Algorithmus | `structure_questor_interna_v0.3.0.md` §9–§18 |
| C | Loop-Architektur | `structure_questor_interna_v0.3.0.md` §19–§24 |
| D | Template-Lebenszyklus | `structure_questor_interna_v0.3.0.md` §25–§29 |
| E | HAL-Bridge | `structure_questor_interna_v0.3.0.md` §30–§38 |
| F | ExpeditionLedger + WAL | `structure_questor_interna_v0.3.0.md` §39–§48 |
| G | Result-Builder | `structure_questor_interna_v0.3.0.md` §49–§57 |
| H | Questor-Facade (Queue-Architektur) | `structure_questor_interna_v0.3.0.md` §58–§64 |
| I | Sicherheitsregeln | `structure_questor_interna_v0.3.0.md` §65 |
| J | Gremium-Auslagerungen | `structure_questor_interna_v0.3.0.md` §66 |

### 2.2 Neue Teile (in v0.4.0)

| Teil | Name | Detaildokument |
|---|---|---|
| K | Sanitization | `questor_sanitization_v0.1.0.md` |
| L | Capability-Registry | `questor_capability_registry_v0.1.0.md` |
| M | Security-Mode-Verhalten | `questor_security_mode_v0.1.0.md` |
| N | Questor-Graceful-Shutdown | `questor_graceful_shutdown_v0.1.0.md` |
| O | Questor-Health-Monitoring | `questor_health_monitoring_v0.1.0.md` |
| P | Trail-Map | `questor_trail_map_v0.1.0.md` |
| Q | Gremium-Integration der Queue | `questor_queue_integration_v0.1.0.md` |
| R | Test-Strategie | `questor_test_strategy_v0.1.0.md` |
| S | Implementierungsplan | `questor_implementation_plan_v0.1.0.md` |

---

## 3. Interaktionsmatrix: Neue Themen untereinander

### 3.1 Matrix

| Thema | K | L | M | N | O | P | Q | R | S |
|---|---|---|---|---|---|---|---|---|---|
| **K: Sanitization** | — | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ |
| **L: Capability-Registry** | ✅ | — | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ |
| **M: Security-Mode** | ✅ | ✅ | — | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| **N: Shutdown** | ❌ | ❌ | ✅ | — | ✅ | ✅ | ✅ | ✅ | ✅ |
| **O: Health-Monitoring** | ❌ | ❌ | ❌ | ✅ | — | ✅ | ✅ | ✅ | ✅ |
| **P: Trail-Map** | ✅ | ✅ | ✅ | ✅ | ✅ | — | ❌ | ✅ | ✅ |
| **Q: Queue-Integration** | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | — | ✅ | ✅ |
| **R: Test-Strategie** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ |
| **S: Implementierungsplan** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |

✅ = Direkte Interaktion vorhanden | ❌ = Keine direkte Interaktion

### 3.2 Detaillierte Interaktionsbeschreibungen

| Von | Nach | Interaktion | Details |
|---|---|---|---|
| K → L | Sanitization → Capability-Registry | Keine direkte Interaktion | Sanitization prüft keine Capabilities. Capability-Registry-Ergebnisse können aber als Trail protokolliert werden. |
| K → M | Sanitization → Security-Mode | `security_mode` wird dem LLM NICHT mitgeteilt | `security_mode` ist in der Sanitization-Blocklist. |
| K → P | Sanitization → Trail-Map | Sanitization-Events werden als Trails protokolliert | `SANITIZATION_QUARANTINE`, `SANITIZATION_REJECT` |
| K → R | Sanitization → Test-Strategie | 18 Unit-Tests (U-SAN-01 bis U-SAN-18) | Siehe Test-Strategie §3.1 |
| K → S | Sanitization → Implementierungsplan | Phase Q1 (2–3 Tage) | Siehe Implementierungsplan §3.3 |
| L → K | Capability-Registry → Sanitization | Keine direkte Interaktion | Siehe K → L |
| L → M | Capability-Registry → Security-Mode | `allowed_security_modes` pro Capability | Capability-Registry definiert, in welchen Modi eine Capability erlaubt ist. |
| L → P | Capability-Registry → Trail-Map | Capability-Checks werden als Trails protokolliert | `CAPABILITY_CHECK` |
| L → R | Capability-Registry → Test-Strategie | 22 Unit-Tests (U-CAP-01 bis U-CAP-22) | Siehe Test-Strategie §3.2 |
| L → S | Capability-Registry → Implementierungsplan | Phase Q2 (2–3 Tage) | Siehe Implementierungsplan §3.4 |
| M → K | Security-Mode → Sanitization | `security_mode` wird dem LLM NICHT mitgeteilt | Siehe K → M |
| M → L | Security-Mode → Capability-Registry | Security-Mode-Einschränkungen pro Capability | Siehe L → M |
| M → N | Security-Mode → Shutdown | Shutdown respektiert den `security_mode` | Kein Modus-Wechsel bei Shutdown. |
| M → P | Security-Mode → Trail-Map | Security-Mode-Checks werden als Trails protokolliert | `SECURITY_MODE_CHECK` |
| M → Q | Security-Mode → Queue-Integration | `security_mode` wird in `registry.json` protokolliert | Siehe Queue-Integration §3.6 |
| M → R | Security-Mode → Test-Strategie | 11 Unit-Tests (U-SM-01 bis U-SM-11) | Siehe Test-Strategie §3.3 |
| M → S | Security-Mode → Implementierungsplan | Phase Q3 (1–2 Tage) | Siehe Implementierungsplan §3.5 |
| N → M | Shutdown → Security-Mode | Shutdown respektiert den `security_mode` | Siehe M → N |
| N → O | Shutdown → Health-Monitoring | Health-Monitoring erkennt, wenn Questor sich beendet | Letzter Heartbeat wird geschrieben. |
| N → P | Shutdown → Trail-Map | Shutdown-Events werden als Trails protokolliert | `SHUTDOWN_INITIATED` |
| N → Q | Shutdown → Queue-Integration | Queue wird bei Shutdown aktualisiert | `status = SHUTDOWN` in `registry.json` |
| N → R | Shutdown → Test-Strategie | 13 Unit-Tests (U-SD-01 bis U-SD-13) | Siehe Test-Strategie §3.4 |
| N → S | Shutdown → Implementierungsplan | Phase Q11 (1–2 Tage) | Siehe Implementierungsplan §3.13 |
| O → N | Health-Monitoring → Shutdown | Health-Monitoring interagiert mit Shutdown | Siehe N → O |
| O → P | Health-Monitoring → Trail-Map | Health-Alerts werden als Trails protokolliert | `HEALTH_ALERT` |
| O → Q | Health-Monitoring → Queue-Integration | `health.json` wird in der Queue gespeichert | Siehe Queue-Integration §3.1 |
| O → R | Health-Monitoring → Test-Strategie | 15 Unit-Tests (U-HM-01 bis U-HM-15) | Siehe Test-Strategie §3.5 |
| O → S | Health-Monitoring → Implementierungsplan | Phase Q12 (2–3 Tage) | Siehe Implementierungsplan §3.14 |
| P → K | Trail-Map → Sanitization | Sanitization-Events werden als Trails protokolliert | Siehe K → P |
| P → L | Trail-Map → Capability-Registry | Capability-Checks werden als Trails protokolliert | Siehe L → P |
| P → M | Trail-Map → Security-Mode | Security-Mode-Checks werden als Trails protokolliert | Siehe M → P |
| P → N | Trail-Map → Shutdown | Shutdown-Events werden als Trails protokolliert | Siehe N → P |
| P → O | Trail-Map → Health-Monitoring | Health-Alerts werden als Trails protokolliert | Siehe O → P |
| P → R | Trail-Map → Test-Strategie | 11 Unit-Tests (U-TRAIL-01 bis U-TRAIL-11) | Siehe Test-Strategie §3.6 |
| P → S | Trail-Map → Implementierungsplan | Phase Q13 (1–2 Tage) | Siehe Implementierungsplan §3.15 |
| Q → M | Queue-Integration → Security-Mode | `security_mode` wird in `registry.json` protokolliert | Siehe M → Q |
| Q → N | Queue-Integration → Shutdown | Queue wird bei Shutdown aktualisiert | Siehe N → Q |
| Q → O | Queue-Integration → Health-Monitoring | `health.json` wird in der Queue gespeichert | Siehe O → Q |
| Q → R | Queue-Integration → Test-Strategie | 14 Unit-Tests (U-QI-01 bis U-QI-14) | Siehe Test-Strategie §3.7 |
| Q → S | Queue-Integration → Implementierungsplan | Phase Q14 (3–5 Tage) | Siehe Implementierungsplan §3.16 |
| R → Alle | Test-Strategie → Alle Themen | Test-Strategie testet alle Themen | Siehe Test-Strategie §3–§6 |
| S → Alle | Implementierungsplan → Alle Themen | Implementierungsplan plant alle Themen | Siehe Implementierungsplan §3 |

---

## 4. Interaktionsmatrix: Neue Themen mit bestehenden Teilen

### 4.1 Matrix

| Neues Thema | A | B | C | D | E | F | G | H | I | J |
|---|---|---|---|---|---|---|---|---|---|---|
| **K: Sanitization** | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ | ❌ |
| **L: Capability-Registry** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |
| **M: Security-Mode** | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **N: Shutdown** | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **O: Health-Monitoring** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **P: Trail-Map** | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ | ❌ |
| **Q: Queue-Integration** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **R: Test-Strategie** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **S: Implementierungsplan** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### 4.2 Detaillierte Interaktionsbeschreibungen

| Neues Thema | Bestehender Teil | Interaktion | Details |
|---|---|---|---|
| K: Sanitization | B: QuestCompass | QuestCompass ruft Sanitization vor jedem LLM-Aufruf auf | Sanitization ist die einzige Schnittstelle zum LLM |
| K: Sanitization | F: ExpeditionLedger | LLM-Aufrufe werden als Ledger-Einträge protokolliert | `entry_type: LLM_ADVISOR_CALL` |
| K: Sanitization | G: Result-Builder | `llm_advice_rejected_count` in OperationalMetrics | Operational, keine wissenschaftlichen Signale |
| K: Sanitization | I: Sicherheitsregeln | 6 neue Sicherheitsregeln (S1–S6 aus Teil K) | LLM-Blindheit, Fail-Closed |
| L: Capability-Registry | B: QuestCompass | Template-Filterung nach Capabilities | Loop Selection Schritt 1 |
| L: Capability-Registry | C: Loop-Architektur | `required_capabilities` in LoopTemplate | Template-Validierung |
| L: Capability-Registry | D: Template-Lebenszyklus | Template-Erstellung referenziert Capabilities | Domain-Experte muss Capabilities kennen |
| L: Capability-Registry | E: HAL-Bridge | Parameter-Validierung vor HALCommand-Sendung | `validate_parameters()` |
| L: Capability-Registry | F: ExpeditionLedger | Capability-Checks werden im Ledger protokolliert | `entry_type: CAPABILITY_CHECK` |
| L: Capability-Registry | G: Result-Builder | `capability_retry_count` in OperationalMetrics | Operational |
| L: Capability-Registry | I: Sicherheitsregeln | 5 neue Sicherheitsregeln (S1–S5 aus Teil L) | Fail-Closed bei unbekannter Capability |
| M: Security-Mode | A: Zustandsmaschine | Security-Mode beeinflusst Zustandsübergänge | RECOVERY erlaubt nur reconcile_* |
| M: Security-Mode | B: QuestCompass | Template-Filterung nach Security-Mode | `filter_templates_by_security_mode()` |
| M: Security-Mode | C: Loop-Architektur | `is_recovery_template` in LoopTemplate | NEU: Muss in Teil C ergänzt werden |
| M: Security-Mode | E: HAL-Bridge | `security_mode` in HALCommand | HAL prüft den Modus |
| M: Security-Mode | F: ExpeditionLedger | Security-Mode-Checks im Ledger | `entry_type: SECURITY_MODE_CHECK` |
| M: Security-Mode | G: Result-Builder | OPERATIONAL bei PHYSICAL_EXECUTION_FORBIDDEN | Keine SAFETY-Klassifikation |
| M: Security-Mode | H: Facade | Security-Mode wird im Envelope geprüft | Envelope-Check |
| M: Security-Mode | I: Sicherheitsregeln | 5 neue Sicherheitsregeln (S1–S5 aus Teil M) | Min-Rule, kein Default auf NORMAL |
| N: Shutdown | A: Zustandsmaschine | Shutdown in jedem Zustand definiert | Übergangstabelle erweitert |
| N: Shutdown | E: HAL-Bridge | HAL-Kommandos bei Shutdown abwarten | `drain_active_hal_command()` |
| N: Shutdown | F: ExpeditionLedger | WAL-Flush bei Shutdown | `SHUTDOWN_CHECKPOINT` |
| N: Shutdown | G: Result-Builder | Ergebnis bei Shutdown bauen | `GRACEFUL_SHUTDOWN` |
| N: Shutdown | H: Facade | Queue bei Shutdown aktualisieren | `status = SHUTDOWN` |
| N: Shutdown | I: Sicherheitsregeln | 5 neue Sicherheitsregeln (S1–S5 aus Teil N) | ESTOP-Vorrang, WAL-Flush obligatorisch |
| O: Health-Monitoring | A: Zustandsmaschine | Heartbeat-Writer und Watchdog starten bei Questor-Start | Separate Threads |
| O: Health-Monitoring | H: Facade | `health.json` in der Queue | `data/questor_queue/health.json` |
| O: Health-Monitoring | I: Sicherheitsregeln | 5 neue Sicherheitsregeln (S1–S5 aus Teil O) | OPERATIONAL, kein Neustart bei SAFE_HOLD |
| O: Health-Monitoring | J: Gremium-Auslagerungen | Pipeline-Orchestrator liest `health.json` | Externer Monitor |
| P: Trail-Map | B: QuestCompass | QuestCompass erzeugt Trails | OBJECTIVE_ANALYSIS, LOOP_SELECTION, etc. |
| P: Trail-Map | F: ExpeditionLedger | TrailMapSummary im Ledger | Nur Summary/Digest, keine Details |
| P: Trail-Map | G: Result-Builder | Trail-Map in Blackbox | `trail_map.json` |
| P: Trail-Map | I: Sicherheitsregeln | 5 neue Sicherheitsregeln (S1–S5 aus Teil P) | Lokal, keine Signale, kein LLM-Zugriff |
| Q: Queue-Integration | H: Facade | Queue-Architektur wird vollständig spezifiziert | Dateiformate, Protokolle |
| Q: Queue-Integration | I: Sicherheitsregeln | 5 neue Sicherheitsregeln (S1–S5 aus Teil Q) | Kein Dispatch ohne Gate, atomar |
| Q: Queue-Integration | J: Gremium-Auslagerungen | Dispatcher, Receiver, Archivar, Pipeline-Orchestrator | Gremium-seitige Integration |

---

## 5. Datenfluss-Diagramm

### 5.1 Gesamtsystem-Datenfluss

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          GREMIUM (MYRMEX)                                │
│                                                                         │
│  Dispatcher ──► pending/ ──► Questor ──► completed/ ──► Receiver       │
│       │              │           │              │              │        │
│       │              │           │              │              ▼        │
│       │              │           │              │         Archivar      │
│       │              │           │              │                       │
│       ▼              ▼           ▼              ▼                       │
│  registry.json ◄─── Alle ───► registry.json ──► Pipeline-Orchestrator  │
│                                                                         │
│  delete_requests/ ◄── Kanzler/Quartiermeister                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              │ Dateisystem
                              │
┌─────────────────────────────────────────────────────────────────────────┐
│                        QUESTOR-PROZESS                                   │
│                                                                         │
│  Facade ──► Validator ──► QuestCompass ──► PolicyEvaluator             │
│                                │                    │                   │
│                                │                    ▼                   │
│                                │            SafetyMonitor               │
│                                │                    │                   │
│                                ▼                    ▼                   │
│                          HAL-Bridge ──► HAL Interface                   │
│                                │                    │                   │
│                                ▼                    ▼                   │
│                    ExpeditionLedger + WAL    HALCommandResult           │
│                                │                    │                   │
│                                ▼                    ▼                   │
│                          Result-Builder ──► questor_ergebnis_paket      │
│                                │                                        │
│                                ▼                                        │
│                     Blackbox-Archiver ──► data/questor_blackbox/        │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  QUERSCHNITTSMODULE                                              │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │  │
│  │  │ Sanitization │ │ Capability-  │ │ Security-    │            │  │
│  │  │   (K)        │ │ Registry (L) │ │ Mode (M)     │            │  │
│  │  └──────────────┘ └──────────────┘ └──────────────┘            │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │  │
│  │  │ Shutdown     │ │ Health-      │ │ Trail-Map    │            │  │
│  │  │   (N)        │ │ Monitoring(O)│ │   (P)        │            │  │
│  │  └──────────────┘ └──────────────┘ └──────────────┘            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Datenfluss pro Thema

| Thema | Eingabe | Verarbeitung | Ausgabe |
|---|---|---|---|
| K: Sanitization | Kontext aus QuestCompass | Feld-Filter + Injection-Scan + Prompt-Bau | SanitizationResult → LLM |
| K: Sanitization | LLM-Response | JSON-Parse + Schema + Safety + Constraints | LLMOutputValidation → QuestCompass |
| L: Capability-Registry | YAML-Dateien | Laden + Validieren + Hash | CapabilityRegistry (read-only) |
| L: Capability-Registry | capability_id + Kontext | 3-Ebenen-Check | CapabilityCheckResult |
| M: Security-Mode | Paket + Gate + System + Slot | Min-Rule | effective_security_mode |
| N: Shutdown | SIGTERM/SIGINT/Flag | DRAINING → FINALIZING → TERMINATED | ShutdownResult + Ergebnis |
| O: Health-Monitoring | Questor-Zustand | Heartbeat + Watchdog | health.json |
| P: Trail-Map | Entscheidungsereignisse | Trail-Erzeugung + Hash-Chain | TrailMap → Blackbox |
| Q: Queue-Integration | Envelope/Result-Dateien | Lesen/Schreiben/Verschieben | registry.json + Dateien |

---

## 6. Gemeinsame Datenverträge

### 6.1 Verträge und ihre Nutzer

| Vertrag | Definiert in | Genutzt von |
|---|---|---|
| `SanitizationConfig` | K | K, B (QuestCompass) |
| `SanitizationResult` | K | K, B (QuestCompass) |
| `LLMOutputValidation` | K | K, B (QuestCompass) |
| `CapabilityDefinition` | L | L, B, E (HAL-Bridge), PolicyEvaluator |
| `CapabilityCheckResult` | L | L, B, PolicyEvaluator |
| `HealthFile` | O | O, Q (Queue), Pipeline-Orchestrator |
| `HealthMonitorConfig` | O | O, Q (Queue) |
| `ShutdownConfig` | N | N, A (Zustandsmaschine) |
| `ShutdownResult` | N | N, G (Result-Builder) |
| `Trail` | P | P, B, K, L, M, N, O |
| `TrailMap` | P | P, G (Blackbox-Archiver) |
| `TrailMapSummary` | P | P, F (Ledger) |
| `TrailPolicy` | P | P, QuestorSpec |
| `QuestorDispatchEnvelope` | Hauptreferenz §7.3 | Q (Queue), Dispatcher, Facade |
| `QuestorErgebnisPaket` | Hauptreferenz §7.4 | Q (Queue), Result-Builder, Receiver |
| `registry.json` | Q | Q, Dispatcher, Questor, Pipeline-Orchestrator |
| `HALCommand` | HAL v0.2.0 §8.7 | E (HAL-Bridge), HAL |
| `HALCommandResult` | HAL v0.2.0 §8.10 | E (HAL-Bridge), HAL |
| `ExpeditionLedger` | F | F, G, N, P |
| `WALEntry` | F | F, N |
| `QuestorBlackbox` | G | G, P |
| `LocalAuditRef` | Hauptreferenz §7.6 | G, Hauptreferenz |

### 6.2 Korrektur-Erfordernisse

| Vertrag | Korrektur | Quelle |
|---|---|---|
| `QuestorSpec.allowed_capabilities` | `list[Capability]` → `list[str]` | L §3.5 |
| `LoopTemplate` | Neues Feld: `is_recovery_template: bool` | M §4.2 |
| `LoopStep.capability` | Pflicht bei HAL_COMMAND und PROCESS_COMMAND | L §14 Q7 |
| `InitialTrailPolicy` | Muss als Pydantic-Modell definiert werden | P §3.1 |
| `planning_hints` | Muss als optionales Feld in ResearchPackage aufgenommen werden | K §14 Q2 |

---

## 7. Sicherheitsregeln: Herkunft und Zuordnung

### 7.1 Gesamtübersicht

| # | Regel | Herkunft | Teil |
|---|---|---|---|
| 1 | Keine physische Ausführung ohne Envelope | Hauptreferenz §4 | I |
| 2 | Keine physische Ausführung ohne Gate | Hauptreferenz §4 | I |
| 3 | Keine physische Ausführung ohne Lease | Hauptreferenz §4 | I |
| 4 | Questor schreibt nicht in Atlas/Archiv | Hauptreferenz §3.3 | I |
| 5 | Questor setzt ESTOP nicht zurück | Hauptreferenz §3.3 | I |
| 6 | Questor vergibt keine Leases | Hauptreferenz §3.3 | I |
| 7 | Blackbox bleibt lokal | Hauptreferenz §12 | I |
| 8 | Operational ≠ Scientific | Hauptreferenz §3.3 | I |
| 9 | ESTOP ≠ LEASE_DENIED | Hauptreferenz §11 | I |
| 10 | Fail-Closed bei Unklarheit | Questor-Interna §8 | I |
| 11 | LLM nur Advisor, niemals final | Questor v0.2.3 §10.1 | I |
| 12 | Menschliche Königin wird niemals überstimmt | Hauptreferenz §4 | I |
| 13 | Hardwarezugriff nur über HAL | Hauptreferenz §4 | I |
| 14 | NaN/Infinity → Fail-Closed | C18 | I |
| 15 | Recovery NUR aus WAL | Questor-Interna §2 | I |
| 16 | Nur Whitelist-Felder gelangen an das LLM | K §10 S1 | K |
| 17 | Injection-Patterns werden erkannt und quarantänen | K §10 S2 | K |
| 18 | LLM-Output wird gegen Constraints validiert | K §10 S3–S4 | K |
| 19 | Safety-Claims im LLM-Output werden abgelehnt | K §10 S2 | K |
| 20 | Bei LLM-Fehler: deterministischer Fallback | K §10 S5–S6 | K |
| 21 | security_mode wird dem LLM NICHT mitgeteilt | K §10 S9, M §9 S5 | K, M |
| 22 | Unbekannte Capability → VETO | L §11 S2 | L |
| 23 | Deprecated Capability → VETO | L §11 S4 | L |
| 24 | Leere allowed_capabilities → KEINE Capability erlaubt | L §11 S3 | L |
| 25 | Security-Mode-Mismatch → VETO | L §11 S5 | L |
| 26 | NaN/Infinity in Parametern → Fail-Closed | L §11 S7 | L |
| 27 | Min-Rule: Restriktivster Modus gewinnt | M §9 S1 | M |
| 28 | Kein Default auf NORMAL | M §9 S2 | M |
| 29 | RECOVERY nur reconcile/read | M §9 S3 | M |
| 30 | Keine Modus-Eskalation | M §9 S7 | M |
| 31 | Gate ist die absolute Grenze | M §9 S4 | M |
| 32 | Keine neuen Pakete bei Shutdown | N §7 S1 | N |
| 33 | Keine neuen HAL-Kommandos bei Shutdown | N §7 S2 | N |
| 34 | WAL-Flush ist obligatorisch | N §7 S3 | N |
| 35 | ESTOP hat Vorrang vor Shutdown | N §7 S7 | N |
| 36 | Shutdown ist immer OPERATIONAL | N §7 S8 | N |
| 37 | Health-Monitoring ist immer OPERATIONAL | O §12 S1 | O |
| 38 | Health-Monitoring blockiert nicht | O §12 S2 | O |
| 39 | Kein automatischer Neustart bei WAITING_FOR_RELEASE | O §12 S3 | O |
| 40 | Trail-Map ist OPERATIONAL | P §11 S1 | P |
| 41 | Trail-Map bleibt lokal | P §11 S2 | P |
| 42 | Trail-Map wird nicht vom LLM gelesen | P §11 S3 | P |
| 43 | Trail-Map ist nicht Recovery-relevant | P §11 S4 | P |
| 44 | Kein Dispatch ohne gate_record_ref | Q §13 S1 | Q |
| 45 | Keine Duplikate in der Queue | Q §13 S4 | Q |
| 46 | Atomare Schreiboperationen | Q §13 S5 | Q |
| 47 | Kein Löschen von processing/ | Q §13 S7 | Q |
| 48 | Queue-Fehler sind immer OPERATIONAL | Q §13 S10 | Q |

**Gesamt: 48 Sicherheitsregeln**

---

## 8. Testabdeckung pro Thema

### 8.1 Unit-Tests

| Thema | Test-IDs | Anzahl | Datei |
|---|---|---|---|
| K: Sanitization | U-SAN-01 bis U-SAN-18 | 18 | `questor_sanitization_v0.1.0.md` |
| L: Capability-Registry | U-CAP-01 bis U-CAP-22 | 22 | `questor_capability_registry_v0.1.0.md` |
| M: Security-Mode | U-SM-01 bis U-SM-11 | 11 | `questor_security_mode_v0.1.0.md` |
| N: Shutdown | U-SD-01 bis U-SD-13 | 13 | `questor_graceful_shutdown_v0.1.0.md` |
| O: Health-Monitoring | U-HM-01 bis U-HM-15 | 15 | `questor_health_monitoring_v0.1.0.md` |
| P: Trail-Map | U-TRAIL-01 bis U-TRAIL-11 | 11 | `questor_trail_map_v0.1.0.md` |
| Q: Queue-Integration | U-QI-01 bis U-QI-14 | 14 | `questor_queue_integration_v0.1.0.md` |
| Bestehende Module | Diverse | ~148 | `questor_test_strategy_v0.1.0.md` |
| **Gesamt Unit-Tests** | | **~252** | |

### 8.2 Komponententests

| Thema | Test-IDs | Anzahl | Datei |
|---|---|---|---|
| B: QuestCompass | C-QC-01 bis C-QC-15 | 15 | `questor_test_strategy_v0.1.0.md` |
| PolicyEvaluator | C-PE-01 bis C-PE-09 | 9 | `questor_test_strategy_v0.1.0.md` |
| E: HAL-Bridge | C-HB-01 bis C-HB-10 | 10 | `questor_test_strategy_v0.1.0.md` |
| G: Result-Builder | C-RB-01 bis C-RB-10 | 10 | `questor_test_strategy_v0.1.0.md` |
| **Gesamt Komponententests** | | **~44** | |

### 8.3 Sicherheitstests

| Thema | Test-IDs | Anzahl | Datei |
|---|---|---|---|
| K: Prompt-Injection | SEC-PI-01 bis SEC-PI-10 | 10 | `questor_test_strategy_v0.1.0.md` |
| L: Capability-Bypass | SEC-CB-01 bis SEC-CB-05 | 5 | `questor_test_strategy_v0.1.0.md` |
| M: Security-Mode-Eskalation | SEC-SM-01 bis SEC-SM-05 | 5 | `questor_test_strategy_v0.1.0.md` |
| F: WAL-Manipulation | SEC-WAL-01 bis SEC-WAL-03 | 3 | `questor_test_strategy_v0.1.0.md` |
| Q: Queue-Manipulation | SEC-QM-01 bis SEC-QM-05 | 5 | `questor_test_strategy_v0.1.0.md` |
| K: LLM-Output-Manipulation | SEC-LLM-01 bis SEC-LLM-02 | 2 | `questor_test_strategy_v0.1.0.md` |
| **Gesamt Sicherheitstests** | | **~30** | |

### 8.4 Bestehende Integrationstests

| Suite | Tests | Anzahl | Datei |
|---|---|---|---|
| N: Naming | N-01 bis N-07 | 7 | `myrmex_questor_integration_tests_v0.4.0.md` |
| I: Integration | I-01 bis I-18 | 18 | `myrmex_questor_integration_tests_v0.4.0.md` |
| S: Szenarien | S-A bis S-E | 5 | `myrmex_questor_integration_tests_v0.4.0.md` |
| R: Regression | R-01 bis R-12 | 12 | `myrmex_questor_integration_tests_v0.4.0.md` |
| Z: Präzisierung | Z-01 bis Z-08 | 8 | `myrmex_questor_integration_tests_v0.4.0.md` |
| H: HAL | H-01 bis H-24 | 24 | `myrmex_questor_integration_tests_v0.4.0.md` |
| **Gesamt bestehend** | | **74** | |

### 8.5 Gesamtübersicht

| Kategorie | Anzahl |
|---|---|
| Unit-Tests (neu) | ~252 |
| Komponententests (neu) | ~44 |
| Sicherheitstests (neu) | ~30 |
| Performance-/Stress-Tests (neu) | ~21 |
| Bestehende Integrationstests | 74 |
| **Gesamt** | **~421** |

---

## 9. Implementierungsreihenfolge

### 9.1 Phasen und Abhängigkeiten

```
Phase Q0 (Verträge)
    │
    ├──► Phase Q1 (Sanitization) ──────────────────────────────────┐
    ├──► Phase Q2 (Capability-Registry) ──────────────────────────┤
    └──► Phase Q3 (Security-Mode) ◄── Q2 ────────────────────────┤
                                                                    │
Phase Q4 (Facade/Validator) ◄── Q0, Q1, Q2, Q3 ──────────────────┤
    │                                                               │
    └──► Phase Q5 (QuestCompass) ◄── Q1, Q2, Q4 ─────────────────┤
         │                                                          │
         └──► Phase Q6 (Loop-Architektur) ◄── Q2, Q5 ────────────┤
              │                                                     │
              └──► Phase Q7 (PolicyEvaluator) ◄── Q2, Q3, Q5, Q6 ┤
                   │                                                │
                   └──► Phase Q8 (HAL-Bridge) ◄── Q2, Q3, Q7 ────┤
                        │                                           │
                        └──► Phase Q9 (Ledger/WAL) ◄── Q5, Q8 ───┤
                             │                                      │
                             └──► Phase Q10 (Result-Builder) ◄── Q9│
                                  │                                 │
                                  └──► Phase Q11 (Shutdown) ◄── Q9, Q10
                                       │
                                       ├──► Phase Q12 (Health-Monitoring) ◄── Q0
                                       └──► Phase Q13 (Trail-Map) ◄── Q0, Q1, Q2
                                            │
                                            └──► Phase Q14 (Queue-Integration) ◄── Q4, Q10, Q11
                                                 │
                                                 └──► Phase Q15–Q18 (Tests) ◄── Alle
```

### 9.2 Kritischer Pfad

```
Q0 → Q1 → Q5 → Q7 → Q8 → Q9 → Q10 → Q11 → Q14 → Q15 → Q16 → Q17 → Q18
```

### 9.3 Parallelisierbare Phasen

| Phasen | Können parallel laufen |
|---|---|
| Q1, Q2, Q3 | Ja (alle hängen nur von Q0 ab) |
| Q12, Q13 | Ja (beide hängen nur von Q0 ab) |
| Q15, Q16 | Ja (beide hängen von Q14 ab) |

---

## 10. Offene Fragen und Risiken (Gesamt)

| # | Frage / Risiko | Betroffene Themen | Schweregrad | Status |
|---|---|---|---|---|
| 1 | `planning_hints` muss in ResearchPackage-Vertrag aufgenommen werden | K, L | Hoch | Offen |
| 2 | `QuestorSpec.allowed_capabilities` muss von `list[Capability]` auf `list[str]` korrigiert werden | L | Kritisch | Offen |
| 3 | `LoopTemplate.is_recovery_template` muss ergänzt werden | M | Hoch | Offen |
| 4 | LLM-Modell-ID `gemma4:31b-cloud` muss verifiziert werden | K | Mittel | Offen |
| 5 | Injection-Pattern-Liste muss als konfigurierbare Datei angelegt werden | K | Mittel | Offen |
| 6 | Capability-Hierarchie für v0.4.0 prüfen | L | Niedrig | Offen |
| 7 | Trail-Map-Größenlimit muss konfiguriert werden | P | Mittel | Offen |
| 8 | Externer Health-Monitor muss definiert werden | O | Hoch | Offen |
| 9 | Shutdown-Counter für Restart-Schleifen | N | Hoch | Offen |
| 10 | Queue-Verzeichnisse beim Questor-Start erstellen | Q | Mittel | Offen |
| 11 | PID-File gegen parallele Questor-Instanzen | Q | Hoch | Offen |
| 12 | `registry.json` regelmäßig bereinigen | Q | Niedrig | Offen |
| 13 | Test-Umgebung für Performance-/Stress-Tests | R | Mittel | Offen |
| 14 | CI/CD-Pipeline einrichten | R, S | Mittel | Offen |
| 15 | Code-Review-Prozess definieren | S | Niedrig | Offen |

**Gesamt: 15 offene Fragen/Risiken**

---

## 11. Datenintegritäts-Check für dieses Dokument

| Prüfpunkttyp | Erwartet | Enthalten |
|---|---:|---:|
| Teile-Übersicht (bestehend) | 10 | 10 |
| Teile-Übersicht (neu) | 9 | 9 |
| Interaktionsmatrix (neu untereinander) | 9×9 | 9×9 |
| Detaillierte Interaktionsbeschreibungen | 30+ | 42 |
| Interaktionsmatrix (neu mit bestehend) | 9×10 | 9×10 |
| Detaillierte Interaktionsbeschreibungen (mit bestehend) | 25+ | 32 |
| Datenfluss-Diagramm | 1 | 1 |
| Gemeinsame Datenverträge | 20+ | 24 |
| Korrektur-Erfordernisse | 5 | 5 |
| Sicherheitsregeln | 48 | 48 |
| Test-IDs | 421+ | ~421 |
| Implementierungsphasen | 19 | 19 |
| Offene Fragen/Risiken | 15 | 15 |

---

## 12. Kreuzreferenzen

| Referenz | Beziehung |
|---|---|
| `structure_questor_interna_v0.4.0.md`, Anhang C | Dieses Dokument IST Anhang C |
| `questor_sanitization_v0.1.0.md` | Teil K, 18 Unit-Tests |
| `questor_capability_registry_v0.1.0.md` | Teil L, 22 Unit-Tests |
| `questor_security_mode_v0.1.0.md` | Teil M, 11 Unit-Tests |
| `questor_graceful_shutdown_v0.1.0.md` | Teil N, 13 Unit-Tests |
| `questor_health_monitoring_v0.1.0.md` | Teil O, 15 Unit-Tests |
| `questor_trail_map_v0.1.0.md` | Teil P, 11 Unit-Tests |
| `questor_queue_integration_v0.1.0.md` | Teil Q, 14 Unit-Tests |
| `questor_test_strategy_v0.1.0.md` | Teil R, ~347 neue Tests |
| `questor_implementation_plan_v0.1.0.md` | Teil S, 19 Phasen |
| `structure_questor_interna_v0.3.0.md` | Teile A–J (bestehend) |
| `structure_standalone_v2.4.0.md` v1.1.1 | Kanonische Hauptreferenz |
| `structure_hal_v0.2.0.md` | HAL-Vertrag |
| `myrmex_questor_integration_tests_v0.4.0.md` | 74 bestehende Tests |
| `structure_standalone_questor_v0.2.3.md` | Unterstützendes Begleitdokument |