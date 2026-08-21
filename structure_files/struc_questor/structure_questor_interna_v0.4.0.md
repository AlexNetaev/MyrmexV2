# 🧭 STRUCTURE_QUESTOR_INTERNA_V0.4.0

## MYRMEX V2.4.0 + QUESTOR V0.2.3 — QUESTOR-INTERNA GESAMTSPEZIFIKATION

| Feld | Wert |
|---|---|
| Dateiname | `structure_questor_interna_v0.4.0.md` |
| Version | 0.4.0 |
| System | MYRMEX v2.4.0 + Questor v0.2.3 |
| Status | Arbeitsstand — Architektur-Spezifikation, keine Implementierungsfreigabe |
| Bezug | `structure_standalone_v2.4.0.md` v1.1.1 (kanonisch) |
| | `structure_hal_v0.2.0.md` |
| | `structure_standalone_questor_v0.2.3.md` (unterstützend) |
| Sprache | Deutsch |
| Modus | Dry-Run / Spezifikation |
| Ersetzt | `structure_questor_interna_v0.3.0.md` |

---

## 0. Dokumentenhierarchie und Geltung

```
1. structure_standalone_v2.4.0.md v1.1.1         ← kanonisch
2. structure_hal_v0.2.0.md                        ← HAL-Vertrag
3. diese Datei: structure_questor_interna_v0.4.0.md ← Questor-Interna GESAMT
4. questor_sanitization_v0.1.0.md                 ← Detail: Sanitization
5. questor_capability_registry_v0.1.0.md          ← Detail: Capability-Registry
6. questor_security_mode_v0.1.0.md                ← Detail: Security-Mode
7. questor_graceful_shutdown_v0.1.0.md            ← Detail: Graceful-Shutdown
8. questor_health_monitoring_v0.1.0.md            ← Detail: Health-Monitoring
9. questor_trail_map_v0.1.0.md                    ← Detail: Trail-Map
10. questor_queue_integration_v0.1.0.md           ← Detail: Queue-Integration
11. questor_test_strategy_v0.1.0.md               ← Detail: Test-Strategie
12. questor_implementation_plan_v0.1.0.md         ← Detail: Implementierungsplan
13. questor_cross_reference_matrix_v0.1.0.md      ← Kreuzreferenz
14. structure_standalone_questor_v0.2.3.md        ← unterstützend
```

Bei Widersprüchen gilt die kanonische Hauptreferenz.

Diese Datei ersetzt:
- `structure_questor_interna_v0.3.0.md` (vollständig)
- `structure_standalone_questcompass_v0.1.0.md` (bereits in v0.3.0 integriert)
- `structure_standalone_hal_bridge_exp_ledger_v0.1.0.md` (bereits in v0.3.0 integriert)

---

## 1. Zweck dieser Datei

Diese Datei ist der **Einstiegspunkt** für die Questor-Interna. Sie definiert:

1. Die vollständige Architektur von Questor (Teile A–S)
2. Die Zusammenfassungen aller Spezifikationen
3. Die Verweise auf die Detaildokumente
4. Die Sicherheitsregeln (Gesamtübersicht)
5. Die Gremium-Auslagerungen (Gesamtübersicht)
6. Die Dokumentenhierarchie

**Wichtig:** Die vollständigen Details der Themen K–S stehen in den jeweiligen Detaildokumenten. Diese Datei enthält nur Zusammenfassungen und Verweise.

---

## 2. Grundannahmen

| Annahme | Wert |
|---|---|
| Nebenläufigkeit | Questor verarbeitet **immer nur EIN Paket** sequentiell |
| LLM-Backend | Ollama mit `gemma4:31b-cloud` (abstrahiert, wechselbar) |
| Questor ist Totalfunktion | Jedes Paket → genau ein Ergebnis, auch bei Early-Abort |
| Questor schreibt nie in Atlas/Archiv | In allen Szenarien bestätigt |
| Questor setzt ESTOP nie zurück | Explizit verboten |
| Questor vergibt keine Leases | Leases kommen vom Resource Governor |
| Recovery-Mechanismus | **NUR WAL** (Write-Ahead Log), keine Blackbox-Recovery |
| Kosten-Tracking | Vereinfacht: Zeit + Reagenzien + Compute (normiert) |
| Kostenberechnung | Erst bei COMPLETED/ABORTED final berechnen |
| Ledger-Verschlüsselung | Keine (kein Mehrwert) |
| WAL-Lebenszyklus | Nur während aktiver Ausführung, nach DONE bereinigt |
| Questor-Prozess | Eigener Prozess, losgelöst vom Gremium |
| Transportmedium | Dateibasierte Queue (`data/questor_queue/`) |
| Kristallkandidat | Loop + Einstellungen + Ergebnis (NICHT der Messwert allein) |
| Signal | Fazit aus Kristallkandidaten (deterministisch erzeugt) |
| Budget-Logik | Ziel erreichen, nicht Budget ausgeben |
| Autonomy-Level | Steuert candidate_window und LLM-Nutzung |
| Templates | Dateien in `data/questor_templates/`, erstellt vom Domain-Experten |

---

## 3. Inhaltsverzeichnis

### Bestehende Teile (aus v0.3.0, unverändert)

| Teil | Thema | Status |
|---|---|---|
| Teil A | Questor-Zustandsmaschine | ✅ Aus v0.3.0 übernommen |
| Teil B | QuestCompass-Algorithmus | ✅ Aus v0.3.0 übernommen |
| Teil C | Loop-Architektur | ✅ Aus v0.3.0 übernommen |
| Teil D | Template-Lebenszyklus | ✅ Aus v0.3.0 übernommen |
| Teil E | HAL-Bridge | ✅ Aus v0.3.0 übernommen |
| Teil F | ExpeditionLedger + WAL | ✅ Aus v0.3.0 übernommen |
| Teil G | Result-Builder | ✅ Aus v0.3.0 übernommen |
| Teil H | Questor-Facade (Queue-Architektur) | ✅ Aus v0.3.0 übernommen |
| Teil I | Sicherheitsregeln | ✅ Aus v0.3.0 übernommen |
| Teil J | Gremium-Auslagerungen | ✅ Aus v0.3.0 übernommen |

### Neue Teile (in v0.4.0)

| Teil | Thema | Detaildokument | Status |
|---|---|---|---|
| Teil K | Sanitization | `questor_sanitization_v0.1.0.md` | 🆕 NEU |
| Teil L | Capability-Registry | `questor_capability_registry_v0.1.0.md` | 🆕 NEU |
| Teil M | Security-Mode-Verhalten | `questor_security_mode_v0.1.0.md` | 🆕 NEU |
| Teil N | Questor-Graceful-Shutdown | `questor_graceful_shutdown_v0.1.0.md` | 🆕 NEU |
| Teil O | Questor-Health-Monitoring | `questor_health_monitoring_v0.1.0.md` | 🆕 NEU |
| Teil P | Trail-Map | `questor_trail_map_v0.1.0.md` | 🆕 NEU |
| Teil Q | Gremium-Integration der Queue | `questor_queue_integration_v0.1.0.md` | 🆕 NEU |
| Teil R | Test-Strategie | `questor_test_strategy_v0.1.0.md` | 🆕 NEU |
| Teil S | Implementierungsplan | `questor_implementation_plan_v0.1.0.md` | 🆕 NEU |

### Anhänge

| Anhang | Thema |
|---|---|
| Anhang A | Sicherheitsregeln Gesamt (alle Teile) |
| Anhang B | Gremium-Auslagerungen Gesamt |
| Anhang C | Kreuzreferenz-Matrix |

---

## TEIL A: QUESTOR-ZUSTANDSMASCHINE

**Status:** Aus v0.3.0 übernommen, unverändert.
**Abschnitte:** §3–§8

Zusammenfassung:
- 11 Zustände: IDLE, RECEIVING, VALIDATING, PLANNING, EXECUTING, EVALUATING, WAITING_FOR_RELEASE, SAFE_HOLD, RECOVERING, FINALIZING, DONE
- Übergangstabelle vollständig definiert
- Drei fundamentale Verhaltensregeln: FAIL-CLOSED, DETERMINISTIC-FIRST, TOTALFUNKTION
- Invarianten definiert

→ Vollständige Spezifikation: `structure_questor_interna_v0.3.0.md`, Teil A (§3–§8)

---

## TEIL B: QUESTCOMPASS-ALGORITHMUS

**Status:** Aus v0.3.0 übernommen, unverändert.
**Abschnitte:** §9–§18

Zusammenfassung:
- Objective Analysis (3 Stufen + Stufe 2.5)
- Loop Selection (4 Schritte, Ranking, Kandidatenfenster)
- Hypothesis Formulation
- Evaluation (pro objective_type)
- Decision Engine (8 Regeln)
- LLM-Advisor-Integration (3 Situationen)
- PolicyEvaluator (8 Prüfungen)
- Autonomy-Level (STRICT, GUIDED, ADAPTIVE)
- FRACTURE_DIAGNOSIS-Sonderregel

→ Vollständige Spezifikation: `structure_questor_interna_v0.3.0.md`, Teil B (§9–§18)

---

## TEIL C: LOOP-ARCHITEKTUR

**Status:** Aus v0.3.0 übernommen, unverändert.
**Abschnitte:** §19–§24

Zusammenfassung:
- Drei Ebenen: LoopTemplate, LoopInstance, HALCommand/ProcessCommand
- LoopTemplate-Definition (vollständig)
- LoopStep-Definition (vollständig)
- Loop-Kette dynamisch (PLAN → EXECUTE → EVALUATE → RE-PLAN)
- Terminierungsbedingungen
- Routing-Graph als Constraint-Framework

→ Vollständige Spezifikation: `structure_questor_interna_v0.3.0.md`, Teil C (§19–§24)

---

## TEIL D: TEMPLATE-LEBENSZYKLUS

**Status:** Aus v0.3.0 übernommen, unverändert.
**Abschnitte:** §25–§29

Zusammenfassung:
- Template-Erstellung durch Domain-Experten
- Speicherung in `data/questor_templates/`
- Laden und Versionierung (semantisch)
- Template-Korrektur (3 Stufen)
- template_feedback (6 Trigger)

→ Vollständige Spezifikation: `structure_questor_interna_v0.3.0.md`, Teil D (§25–§29)

---

## TEIL E: HAL-BRIDGE

**Status:** Aus v0.3.0 übernommen, unverändert.
**Abschnitte:** §30–§38

Zusammenfassung:
- Übersetzungslogik (LoopStep → HALCommand/ProcessCommand)
- Deterministische ID-Erzeugung
- Ergebnisverarbeitung (12 HAL-Status → BridgeResult)
- Prozess-Lebenszyklus
- Kosten-Tracking
- Parameter-Schema-Handling
- Validiert durch 4 Domänen-Beispiele

→ Vollständige Spezifikation: `structure_questor_interna_v0.3.0.md`, Teil E (§30–§38)

---

## TEIL F: EXPEDITIONLEDGER + WAL

**Status:** Aus v0.3.0 übernommen, unverändert.
**Abschnitte:** §39–§48

Zusammenfassung:
- Ledger-Struktur (APPEND-ONLY, Hash-Chain)
- Genesis-Hash (C15)
- NaN/Infinity-Prüfung (C18)
- WAL-Lebenszyklus
- Recovery aus WAL
- Dokument-Hierarchie (3 Ebenen)
- Zugriffskontrolle

→ Vollständige Spezifikation: `structure_questor_interna_v0.3.0.md`, Teil F (§39–§48)

---

## TEIL G: RESULT-BUILDER

**Status:** Aus v0.3.0 übernommen, unverändert.
**Abschnitte:** §49–§57

Zusammenfassung:
- Algorithmus (9 Schritte)
- Feldzuordnung (Ledger → questor_ergebnis_paket)
- Sonderregeln (5 Regeln)
- Kristallkandidaten (Loop + Einstellungen + Ergebnis)
- Signale aus Kristallkandidaten (deterministisch)
- Early-Abort Complete Result (C21)
- Guardian-Validierung
- Blackbox-Archiver
- Sequence-Manager
- Validiert durch 6 Beispiele

→ Vollständige Spezifikation: `structure_questor_interna_v0.3.0.md`, Teil G (§49–§57)

---

## TEIL H: QUESTOR-FACADE (QUEUE-ARCHITEKTUR)

**Status:** Aus v0.3.0 übernommen, unverändert.
**Abschnitte:** §58–§64

Zusammenfassung:
- Queue-Architektur (pending/, processing/, completed/, failed/, delete_requests/)
- Questor-Prozess (Hauptloop)
- Facade vs. Validator
- Paket-Status und Sichtbarkeit
- Löschanfragen
- Timeout-Handling
- ESTOP-Handling

→ Vollständige Spezifikation: `structure_questor_interna_v0.3.0.md`, Teil H (§58–§64)

**Erweiterung in v0.4.0:** Die Gremium-Integration der Queue ist jetzt in Teil Q vollständig spezifiziert.

---

## TEIL I: SICHERHEITSREGELN

**Status:** Aus v0.3.0 übernommen, in v0.4.0 erweitert.
**Abschnitte:** §65 (v0.3.0) + Anhang A (v0.4.0)

→ Siehe Anhang A für die vollständige Zusammenfassung aller Sicherheitsregeln.

---

## TEIL J: GREMIUM-AUSLAGERUNGEN

**Status:** Aus v0.3.0 übernommen, in v0.4.0 erweitert.
**Abschnitte:** §66 (v0.3.0) + Anhang B (v0.4.0)

→ Siehe Anhang B für die vollständige Zusammenfassung aller Gremium-Auslagerungen.

---

## TEIL K: SANITIZATION (NEU in v0.4.0)

**Detaildokument:** `questor_sanitization_v0.1.0.md`
**Abschnitte im Detaildokument:** §0–§13

### K.1 Zusammenfassung

Das Sanitization-Modul ist die **einzige Schnittstelle** zwischen Questor-internen Daten und dem LLM-Advisor. Es verhindert Prompt-Injection und validiert LLM-Outputs.

### K.2 Kernentscheidungen

| Entscheidung | Wert |
|---|---|
| Feld-Whitelist | Nur `ziel`, `kontext.zusammenfassung`, `parameter_bounds`, `planning_hints` |
| Feld-Blocklist | `atlas_version_ref`, `gate_record_ref`, `lease_grants`, `security_mode`, etc. |
| Injection-Patterns | 15 Regex-Patterns (INJ-01 bis INJ-15) |
| Injection-Aktion | QUARANTINE (Default), REJECT, STRIP |
| Output-Validierung | 6 Schritte: Länge → JSON → Schema → Safety → Constraints → Plausibilität |
| Safety-Claim-Erkennung | 21 Keywords im LLM-Output |
| Fallback | Immer deterministisch bei LLM-Fehler |
| Prompt-Struktur | System-Prompt + Kontext-Block + Aufgaben-Block + Output-Format |

### K.3 Datenverträge

| Vertrag | Zweck |
|---|---|
| `SanitizationConfig` | Konfiguration der Sanitization |
| `FieldRule` | Regel pro Feld |
| `SanitizationResult` | Ergebnis der Input-Sanitization |
| `LLMOutputValidation` | Ergebnis der Output-Validierung |

### K.4 Sicherheitsregeln

- LLM-Output wird NIEMALS direkt als Befehl verwendet
- Bei Injection-Erkennung: Feld wird quarantänen
- Bei Safety-Claim im Output: Output wird verworfen
- Bei LLM-Timeout: Deterministischer Fallback
- `security_mode` wird dem LLM NICHT mitgeteilt

### K.5 Integration

| Komponente | Integration |
|---|---|
| QuestCompass | Ruft Sanitization vor jedem LLM-Aufruf auf |
| ExpeditionLedger | Protokolliert LLM-Aufrufe als Ledger-Eintrag |
| Result-Builder | Übernimmt `llm_advice_rejected_count` in OperationalMetrics |
| Blackbox | Speichert vollständige LLM-Interaktionen |
| Trail-Map | Sanitization-Events werden als Trails protokolliert |

→ Vollständige Spezifikation: `questor_sanitization_v0.1.0.md`

---

## TEIL L: CAPABILITY-REGISTRY (NEU in v0.4.0)

**Detaildokument:** `questor_capability_registry_v0.1.0.md`
**Abschnitte im Detaildokument:** §0–§14

### L.1 Zusammenfassung

Die Capability-Registry ist das **zentrale Verzeichnis aller bekannten Capabilities** in Questor. Sie validiert, ob ein Template ausführbar ist.

### L.2 Kernentscheidungen

| Entscheidung | Wert |
|---|---|
| Capability-ID | String, z.B. `"pipette.transfer"` |
| HAL-Mapping | `hal_capability_ref` verweist auf HAL-String |
| Prüfebenen | 3: Registry → HAL → Package |
| Parameter-Validierung | Pro Capability, typsicher, NaN/Infinity-Schutz |
| Security-Mode | Pro Capability definiert (`allowed_security_modes`) |
| Speicherung | YAML-Dateien in `data/questor_capabilities/` |
| Laden | Beim Questor-Start, einmalig, read-only |
| Korrektur | `QuestorSpec.allowed_capabilities: list[str]` (statt `list[Capability]`) |

### L.3 Datenverträge

| Vertrag | Zweck |
|---|---|
| `CapabilityDefinition` | Vollständige Definition einer Capability |
| `ParameterDefinition` | Parameter-Schema pro Capability |
| `CapabilityRegistry` | Gesamtstruktur der Registry |
| `CapabilityCheckResult` | Ergebnis einer Capability-Prüfung |

### L.4 Funktionen

| Funktion | Zweck |
|---|---|
| `check_capability()` | Prüft eine Capability (3 Ebenen) |
| `capabilities_available()` | Prüft alle Capabilities eines Loops |
| `validate_parameters()` | Validiert Parameter gegen Schema |
| `get_slots_for_capability()` | Findet Slots für eine Capability |

### L.5 Sicherheitsregeln

- Unbekannte Capability → VETO
- Deprecated Capability → VETO
- Leere `allowed_capabilities` → KEINE Capability erlaubt (fail-closed)
- Security-Mode-Mismatch → VETO
- NaN/Infinity in Parametern → Fail-Closed

→ Vollständige Spezifikation: `questor_capability_registry_v0.1.0.md`

---

## TEIL M: SECURITY-MODE-VERHALTEN (NEU in v0.4.0)

**Detaildokument:** `questor_security_mode_v0.1.0.md`
**Abschnitte im Detaildokument:** §0–§13

### M.1 Zusammenfassung

Der `security_mode` ist ein **Constraint-Vektor**, der auf vier Ebenen wirkt: Paket, Gate, System, Slot. Der restriktivste Modus gewinnt immer.

### M.2 Kernentscheidungen

| Entscheidung | Wert |
|---|---|
| Modi | `NORMAL`, `SANDBOX`, `DEV_SANDBOX_ONLY`, `RECOVERY` |
| Min-Rule | Der restriktivste Modus gewinnt immer |
| RECOVERY | Nur `reconcile_*` und `read_*` Capabilities |
| Physische Actuation | Nur in `NORMAL` erlaubt |
| Default bei fehlendem Modus | `PACKAGE_INVALID` (fail-closed) |
| LLM-Blindheit | LLM erfährt den security_mode NICHT |
| Keine Eskalation | Questor kann den Modus nicht hochstufen |

### M.3 Matrix

| Capability-Typ | NORMAL | SANDBOX | DEV_SANDBOX_ONLY | RECOVERY |
|---|---|---|---|---|
| `requires_physical_actuation = true` | ✅ | ❌ | ❌ | ❌ |
| `requires_physical_actuation = false` | ✅ | ✅ | ✅ | ❌ |
| `requires_dimension_approval = true` | ✅ (mit Approval) | ❌ | ❌ | ❌ |

### M.4 Sicherheitsregeln

- Kein Default auf NORMAL bei fehlendem Modus
- RECOVERY ist strikt (nur reconcile/read)
- Gate ist die absolute Grenze
- Keine Modus-Eskalation während der Laufzeit
- ESTOP hat Vorrang vor allem

→ Vollständige Spezifikation: `questor_security_mode_v0.1.0.md`

---

## TEIL N: QUESTOR-GRACEFUL-SHUTDOWN (NEU in v0.4.0)

**Detaildokument:** `questor_graceful_shutdown_v0.1.0.md`
**Abschnitte im Detaildokument:** §0–§13

### N.1 Zusammenfassung

Das Shutdown-Modul definiert das Verhalten von Questor bei einer angeforderten Beendigung. Es stellt Crash-Sicherheit und Totalfunktion sicher.

### N.2 Kernentscheidungen

| Entscheidung | Wert |
|---|---|
| Signale | SIGTERM, SIGINT, `shutdown.flag` |
| Phasen | SIGNAL_RECEIVED → DRAINING → FINALIZING → TERMINATED |
| Graceful-Timeout | 60 Sekunden (konfigurierbar) |
| HAL-Kommando-Timeout | 30 Sekunden (konfigurierbar) |
| Ergebnis bei Shutdown | `abbruch_grund = GRACEFUL_SHUTDOWN`, `abbruch_klasse = OPERATIONAL` |
| WAL-Flush | Obligatorisch vor Beendigung |
| Langzeit-Prozesse | SAFE_HOLD anfragen |
| ESTOP-Vorrang | ESTOP hat Vorrang vor Shutdown |

### N.3 Shutdown in jedem Zustand

| Zustand | Aktion |
|---|---|
| IDLE | Sofort beenden |
| RECEIVING | Envelope ablehnen, beenden |
| VALIDATING | Abbrechen, Ergebnis bauen |
| PLANNING | Abbrechen, Ergebnis bauen |
| EXECUTING | HAL-Kommando abwarten, SAFE_HOLD, Ergebnis bauen |
| EVALUATING | Abbrechen, Ergebnis bauen |
| WAITING_FOR_RELEASE | Ergebnis bauen, Prozess bleibt warten |
| SAFE_HOLD | Ergebnis bauen, Prozess bleibt halten |
| RECOVERING | Abbrechen, Ergebnis bauen |
| FINALIZING | Ergebnis fertigstellen, dann beenden |
| DONE | Sofort beenden |

### N.4 Sicherheitsregeln

- Keine neuen Pakete bei Shutdown
- Keine neuen HAL-Kommandos bei Shutdown
- WAL-Flush ist obligatorisch
- Ergebnis wird gebaut, wenn möglich
- ESTOP hat Vorrang vor Shutdown
- Shutdown ist immer OPERATIONAL

→ Vollständige Spezifikation: `questor_graceful_shutdown_v0.1.0.md`

---

## TEIL O: QUESTOR-HEALTH-MONITORING (NEU in v0.4.0)

**Detaildokument:** `questor_health_monitoring_v0.1.0.md`
**Abschnitte im Detaildokument:** §0–§16

### O.1 Zusammenfassung

Das Health-Monitoring stellt sicher, dass Questor seinen eigenen Gesundheitszustand überwacht und nach außen meldet.

### O.2 Kernentscheidungen

| Entscheidung | Wert |
|---|---|
| Heartbeat-Datei | `data/questor_queue/health.json` |
| Heartbeat-Intervall | 5 Sekunden (konfigurierbar) |
| Watchdog-Intervall | 10 Sekunden (konfigurierbar) |
| Externes Monitor-Intervall | 30 Sekunden (konfigurierbar) |
| Gesundheitszustände | HEALTHY, DEGRADED, UNHEALTHY, DEAD |
| Watchdog-Status | OK, WARNING, CRITICAL |
| Recovery-Aktionen | NONE, ALERT, RESTART, ESCALATE |
| Alert-Cooldown | 300 Sekunden |

### O.3 Watchdog-Prüfungen

| Prüfung | Limit |
|---|---|
| Zustandsdauer | Pro Zustand definiert (EXECUTING: kein Limit) |
| Speicherverbrauch | 2048 MB |
| CPU-Auslastung | 90% |
| Fortschritt | 300 Sekunden ohne Fortschritt → CRITICAL |
| WAL-Größe | 100 MB |

### O.4 Sicherheitsregeln

- Health-Monitoring ist immer OPERATIONAL
- Health-Monitoring blockiert nicht die Ausführung
- Kein automatischer Neustart bei WAITING_FOR_RELEASE oder SAFE_HOLD
- Kein automatischer Neustart ohne WAL-Prüfung
- Alert-Cooldown verhindert Alert-Stürme

→ Vollständige Spezifikation: `questor_health_monitoring_v0.1.0.md`

---

## TEIL P: TRAIL-MAP (NEU in v0.4.0)

**Detaildokument:** `questor_trail_map_v0.1.0.md`
**Abschnitte im Detaildokument:** §0–§13

### P.1 Zusammenfassung

Die Trail-Map ist das **Entscheidungsprotokoll** von Questor. Sie dokumentiert, warum welche Entscheidung getroffen wurde.

### P.2 Kernentscheidungen

| Entscheidung | Wert |
|---|---|
| Aktivierung | `QuestorSpec.initial_trail_policy.create_trails` |
| Default | `create_trails = false` |
| Evidenz-Pflicht | `require_evidence = true` (Default) |
| Detail-Level | MINIMAL, STANDARD, FULL |
| Speicherung | In der Blackbox (`trail_map.json`) |
| Ledger-Integration | Nur TrailMapSummary (Hash) im Ledger |
| Gremium-Zugriff | VERBOTEN |
| Wissenschaftliche Signale | KEINE aus Trails |

### P.3 DecisionTypes

`OBJECTIVE_ANALYSIS`, `OBJECTIVE_CLARIFICATION`, `LOOP_SELECTION`, `PARAMETER_CHOICE`, `EVALUATION`, `RE_PLAN`, `LLM_ADVICE_ACCEPTED`, `LLM_ADVICE_REJECTED`, `POLICY_VETO`, `SAFETY_CHECK`, `EARLY_ABORT`, `SANITIZATION_QUARANTINE`, `SANITIZATION_REJECT`, `CAPABILITY_CHECK`, `SECURITY_MODE_CHECK`, `SHUTDOWN_INITIATED`, `HEALTH_ALERT`

### P.4 Sicherheitsregeln

- Trail-Map ist OPERATIONAL (keine wissenschaftlichen Signale)
- Trail-Map bleibt lokal (Blackbox)
- Trail-Map ist APPEND-ONLY
- Trail-Map wird nicht vom LLM gelesen
- Trail-Map-Hash wird im Ledger protokolliert

→ Vollständige Spezifikation: `questor_trail_map_v0.1.0.md`

---

## TEIL Q: GREMIUM-INTEGRATION DER QUEUE (NEU in v0.4.0)

**Detaildokument:** `questor_queue_integration_v0.1.0.md`
**Abschnitte im Detaildokument:** §0–§17

### Q.1 Zusammenfassung

Die Queue-Integration definiert das **Protokoll** zwischen dem Gremium und Questor für den Austausch von Paketen und Ergebnissen.

### Q.2 Kernentscheidungen

| Entscheidung | Wert |
|---|---|
| Queue-Pfad | `data/questor_queue/` |
| Verzeichnisse | `pending/`, `processing/`, `completed/`, `failed/`, `delete_requests/` |
| Dateiformat | JSON mit `schema_version`, `file_type`, `written_by`, `written_at` |
| Registry | `registry.json` mit Datei-Lock |
| Atomare Schreiboperationen | temp file + rename |
| Idempotenz | Duplikate werden erkannt und verworfen |
| Ältestes Paket zuerst | Ja (nach `dispatch_timestamp`) |

### Q.3 Zuständigkeiten

| Komponente | Schreibt | Liest |
|---|---|---|
| Dispatcher | `pending/`, `registry.json` | — |
| Questor | `processing/`, `completed/`, `failed/`, `registry.json` | `pending/`, `delete_requests/` |
| Receiver | — | `completed/`, `failed/` |
| Pipeline-Orchestrator | — | `registry.json` |
| Archivar | Bereinigt `completed/`, `failed/` | — |
| Gremium (Kanzler) | `delete_requests/` | — |

### Q.4 Sicherheitsregeln

- Kein Dispatch ohne `gate_record_ref`
- Keine Duplikate
- Atomare Schreiboperationen
- Registry-Lock
- Kein Löschen von `processing/`
- Queue-Fehler sind immer OPERATIONAL

→ Vollständige Spezifikation: `questor_queue_integration_v0.1.0.md`

---

## TEIL R: TEST-STRATEGIE (NEU in v0.4.0)

**Detaildokument:** `questor_test_strategy_v0.1.0.md`
**Abschnitte im Detaildokument:** §0–§16

### R.1 Zusammenfassung

Die Test-Strategie definiert die vollständige Testabdeckung für Questor: ~325 Tests in 5 Kategorien.

### R.2 Test-Pyramide

| Ebene | Anzahl | Anteil |
|---|---|---|
| Unit-Tests | ~150 | 60% |
| Komponententests | ~50 | 20% |
| Integrationstests | 18 | 8% |
| Szenario-Tests | 5 | 2% |
| Sicherheits-/Performance-Tests | ~51 | 10% |
| **Gesamt** | **~325** | 100% |

### R.3 Coverage-Ziele

| Modul | Mindestabdeckung |
|---|---|
| Sicherheitskritische Module | ≥ 95% |
| Kernlogik | ≥ 85% |
| Gesamt | ≥ 88% |

### R.4 Neue Test-Suiten

| Suite | Tests | Zweck |
|---|---|---|
| Q-U | ~150 | Questor Unit-Tests |
| Q-C | ~50 | Questor Komponententests |
| Q-S | ~30 | Questor Sicherheits-Tests |
| Q-P | ~10 | Questor Performance-Tests |
| Q-T | ~11 | Questor Stress-Tests |

→ Vollständige Spezifikation: `questor_test_strategy_v0.1.0.md`

---

## TEIL S: IMPLEMENTIERUNGSPLAN (NEU in v0.4.0)

**Detaildokument:** `questor_implementation_plan_v0.1.0.md`
**Abschnitte im Detaildokument:** §0–§11

### S.1 Zusammenfassung

Der Implementierungsplan definiert 19 Phasen (Q0–Q18) in 6 Meilensteinen mit einer geschätzten Gesamtdauer von 44–67 Tagen (1 Entwickler).

### S.2 Meilensteine

| Meilenstein | Phasen | Dauer |
|---|---|---|
| MS-1: Foundation | Q0–Q3 | 7–10 Tage |
| MS-2: Core Questor | Q4–Q8 | 12–18 Tage |
| MS-3: Data & Results | Q9–Q10 | 5–7 Tage |
| MS-4: Operational | Q11–Q13 | 4–7 Tage |
| MS-5: Integration | Q14 | 3–5 Tage |
| MS-6: Tests | Q15–Q18 | 13–20 Tage |

### S.3 Kritischer Pfad

```
Q0 → Q1 → Q5 → Q7 → Q8 → Q9 → Q10 → Q11 → Q14 → Q15 → Q16 → Q17 → Q18
```

### S.4 Externe Abhängigkeiten

| Questor-Meilenstein | MYRMEX-Phase | HAL-Phase |
|---|---|---|
| MS-1 | Phase 1 (Verträge) | — |
| MS-2 | Phase 5 (Resource Governor) | HAL-H1 (Interface) |
| MS-5 | Phase 8 (Dispatcher, Receiver) | HAL-H6 (Dummy) |
| MS-6 | Phase 10 (E2E) | HAL-H6 (Dummy) |

→ Vollständige Spezifikation: `questor_implementation_plan_v0.1.0.md`

---

## ANHANG A: SICHERHEITSREGELN GESAMT

### A.1 Aus der Hauptreferenz (unverändert)

| # | Regel | Quelle |
|---|---|---|
| 1 | Keine physische Ausführung ohne Envelope | Hauptreferenz §4 |
| 2 | Keine physische Ausführung ohne Gate | Hauptreferenz §4 |
| 3 | Keine physische Ausführung ohne Lease | Hauptreferenz §4 |
| 4 | Questor schreibt nicht in Atlas/Archiv | Hauptreferenz §3.3 |
| 5 | Questor setzt ESTOP nicht zurück | Hauptreferenz §3.3 |
| 6 | Questor vergibt keine Leases | Hauptreferenz §3.3 |
| 7 | Blackbox bleibt lokal | Hauptreferenz §12 |
| 8 | Operational ≠ Scientific | Hauptreferenz §3.3 |
| 9 | ESTOP ≠ LEASE_DENIED | Hauptreferenz §11 |
| 10 | Fail-Closed bei Unklarheit | Hauptreferenz §3.3 |
| 11 | Menschliche Königin wird niemals überstimmt | Hauptreferenz §4 |
| 12 | Hardwarezugriff nur über HAL | Hauptreferenz §4 |

### A.2 Aus Questor v0.2.3 (unverändert)

| # | Regel | Quelle |
|---|---|---|
| 13 | LLM nur Advisor, niemals final | Questor v0.2.3 §10.1 |
| 14 | NaN/Infinity → Fail-Closed | C18 |
| 15 | atlas_version_ref ist Pass-Through | QuestCompass |
| 16 | Recovery NUR aus WAL | HAL-Bridge |
| 17 | Ledger ist READ-ONLY nach Abschluss | ExpeditionLedger |
| 18 | Kristallkandidat = Loop + Einstellungen + Ergebnis | Result-Builder |
| 19 | Bei SAFETY: Kristalle und Signale leer | Result-Builder |
| 20 | vollstaendig_flag ist IMMER true | Result-Builder |
| 21 | Questor verarbeitet immer nur EIN Paket | Grundannahme |
| 22 | Questor ist eigener Prozess | Facade |
| 23 | Pakete in processing/ nicht löschbar | Facade |

### A.3 Aus Sanitization (NEU in v0.4.0)

| # | Regel | Quelle |
|---|---|---|
| 24 | Nur Whitelist-Felder gelangen an das LLM | Teil K |
| 25 | Injection-Patterns werden erkannt und quarantänen | Teil K |
| 26 | LLM-Output wird gegen Constraints validiert | Teil K |
| 27 | Safety-Claims im LLM-Output werden abgelehnt | Teil K |
| 28 | Bei LLM-Fehler: deterministischer Fallback | Teil K |
| 29 | security_mode wird dem LLM NICHT mitgeteilt | Teil K |

### A.4 Aus Capability-Registry (NEU in v0.4.0)

| # | Regel | Quelle |
|---|---|---|
| 30 | Unbekannte Capability → VETO | Teil L |
| 31 | Deprecated Capability → VETO | Teil L |
| 32 | Leere allowed_capabilities → KEINE Capability erlaubt | Teil L |
| 33 | Security-Mode-Mismatch → VETO | Teil L |
| 34 | NaN/Infinity in Parametern → Fail-Closed | Teil L |

### A.5 Aus Security-Mode (NEU in v0.4.0)

| # | Regel | Quelle |
|---|---|---|
| 35 | Min-Rule: Restriktivster Modus gewinnt | Teil M |
| 36 | Kein Default auf NORMAL | Teil M |
| 37 | RECOVERY nur reconcile/read | Teil M |
| 38 | Keine Modus-Eskalation | Teil M |
| 39 | Gate ist die absolute Grenze | Teil M |

### A.6 Aus Graceful-Shutdown (NEU in v0.4.0)

| # | Regel | Quelle |
|---|---|---|
| 40 | Keine neuen Pakete bei Shutdown | Teil N |
| 41 | Keine neuen HAL-Kommandos bei Shutdown | Teil N |
| 42 | WAL-Flush ist obligatorisch | Teil N |
| 43 | ESTOP hat Vorrang vor Shutdown | Teil N |
| 44 | Shutdown ist immer OPERATIONAL | Teil N |

### A.7 Aus Health-Monitoring (NEU in v0.4.0)

| # | Regel | Quelle |
|---|---|---|
| 45 | Health-Monitoring ist immer OPERATIONAL | Teil O |
| 46 | Health-Monitoring blockiert nicht | Teil O |
| 47 | Kein Neustart bei WAITING_FOR_RELEASE | Teil O |
| 48 | Kein Neustart ohne WAL-Prüfung | Teil O |

### A.8 Aus Trail-Map (NEU in v0.4.0)

| # | Regel | Quelle |
|---|---|---|
| 49 | Trail-Map ist OPERATIONAL | Teil P |
| 50 | Trail-Map bleibt lokal | Teil P |
| 51 | Trail-Map ist APPEND-ONLY | Teil P |
| 52 | Trail-Map wird nicht vom LLM gelesen | Teil P |

### A.9 Aus Queue-Integration (NEU in v0.4.0)

| # | Regel | Quelle |
|---|---|---|
| 53 | Kein Dispatch ohne gate_record_ref | Teil Q |
| 54 | Keine Duplikate in der Queue | Teil Q |
| 55 | Atomare Schreiboperationen | Teil Q |
| 56 | Registry-Lock | Teil Q |
| 57 | Kein Löschen von processing/ | Teil Q |
| 58 | Queue-Fehler sind immer OPERATIONAL | Teil Q |

**Gesamt: 58 Sicherheitsregeln**

---

## ANHANG B: GREMIUM-AUSLAGERUNGEN GESAMT

### B.1 Aus v0.3.0 (unverändert)

| # | Thema | Gremium-Komponente | Status |
|---|---|---|---|
| G-1 | Template-Erstellung bei fehlendem Template | Quartiermeister + Domain-Experte | ✅ |
| G-2 | Template-Korrektur nach Questor-Feedback | Domain-Experte (NICHT Kanzler) | ✅ |
| G-3 | Template-Versionierung (alte Versionen im Archiv) | Archivar | ✅ |
| G-4 | Ressourcen-Karte (Verbrauch pro Zone/Dimension) | Kartograph | ✅ |
| G-5 | Vordenker liefert prozess_skizze mit Idee | Vordenker | ✅ |
| G-6 | template_feedback operational protokollieren | Archivar | ✅ |
| G-7 | Kosten-Schätzungen für Reagenzien | System-Integrator | ✅ |
| G-8 | Kanzler erhält periodische Template-Zusammenfassung | Kanzler (nur Übersicht) | ✅ |
| G-9 | Quartiermeister berücksichtigt template_feedback | Quartiermeister | ✅ |
| G-10 | atlas_version_ref ist Pass-Through, kein LLM-Zugriff | Questor (intern) | ✅ |
| G-11 | loop_selection_weights optional im QuestorSpec | Quartiermeister | ✅ |
| G-12 | planning_hints als optionales Feld | Quartiermeister | ✅ |
| G-13 | Pipeline-Orchestrator liest registry.json und aktualisiert Atlas | Pipeline-Orchestrator (Gremium) | ✅ |
| G-14 | Archivar bereinigt completed/ und failed/ nach Archivierung | Archivar | ✅ |
| G-15 | Gremium schreibt Löschanfragen in delete_requests/ | Kanzler / Quartiermeister | ✅ |

### B.2 Neu in v0.4.0

| # | Thema | Gremium-Komponente | Status |
|---|---|---|---|
| G-16 | Capability-Definitionen erstellen und pflegen | System-Integrator | 🆕 |
| G-17 | Health-Monitoring: Externer Monitor liest health.json | Pipeline-Orchestrator | 🆕 |
| G-18 | Health-Monitoring: Recovery-Aktionen auslösen | Kanzler / Pipeline-Orchestrator | 🆕 |
| G-19 | Shutdown-Signal senden (SIGTERM) | Kanzler / Orchestrator | 🆕 |
| G-20 | Trail-Map lesen (nur autorisierte Rollen) | Domain-Experte / Entwickler | 🆕 |
| G-21 | Test-Strategie: CI/CD einrichten | System-Integrator | 🆕 |
| G-22 | Implementierungsplan: Phasen freigeben | Kanzler / Architekt | 🆕 |

**Gesamt: 22 Gremium-Auslagerungen**

---

## ANHANG C: KREUZREFERENZ-MATRIX

→ Vollständige Matrix: `questor_cross_reference_matrix_v0.1.0.md`

### C.1 Interaktionsmatrix (Übersicht)

| Thema | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| **1: Sanitization** | — | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ |
| **2: Capability-Registry** | ✅ | — | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ |
| **3: Security-Mode** | ✅ | ✅ | — | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| **4: Shutdown** | ❌ | ❌ | ✅ | — | ✅ | ✅ | ✅ | ✅ | ✅ |
| **5: Health-Monitoring** | ❌ | ❌ | ❌ | ✅ | — | ✅ | ✅ | ✅ | ✅ |
| **6: Trail-Map** | ✅ | ✅ | ✅ | ✅ | ✅ | — | ❌ | ✅ | ✅ |
| **7: Queue-Integration** | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | — | ✅ | ✅ |
| **8: Test-Strategie** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ |
| **9: Implementierungsplan** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |

✅ = Interaktion vorhanden | ❌ = Keine direkte Interaktion

---

## 4. Zusammenfassung aller Architektur-Entscheidungen

| Thema | Entscheidung | Quelle |
|---|---|---|
| Questor-Zustandsmaschine | 11 Zustände, PLAN→EXECUTE→EVALUATE→RE-PLAN Zyklus | Teil A |
| Loop-Kette | Dynamisch, entsteht durch Feedback-Schleife | Teil C |
| Routing-Graph | Constraint-Framework, kein fester Plan | Teil C |
| Kristallkandidat | Loop + Einstellungen + Ergebnis | Teil G |
| Signal | Fazit aus Kristallkandidaten (deterministisch) | Teil G |
| Autonomy-Level | Steuert candidate_window und LLM-Nutzung | Teil B |
| Budget-Logik | Ziel erreichen, nicht Budget ausgeben | Teil B |
| Kostenmodell | Zeit + Reagenzien + Compute (normiert) | Teil E |
| Templates | Dateien in data/questor_templates/ | Teil D |
| HAL-Bridge | Einzige Verbindung zu HAL | Teil E |
| ExpeditionLedger | APPEND-ONLY, Hash-Chain | Teil F |
| WAL | Crash-Recovery, nach DONE bereinigt | Teil F |
| Recovery | NUR aus WAL | Teil F |
| Result-Builder | Liest aus Ledger, baut questor_ergebnis_paket | Teil G |
| Blackbox | Lokal, retention_class, Limits | Teil G |
| Facade | Dateibasierte Queue, eigener Prozess | Teil H |
| Sanitization | Feld-Whitelist + Injection-Scan + Output-Validierung | Teil K |
| Capability-Registry | 3 Prüfebenen, YAML-basiert, read-only | Teil L |
| Security-Mode | Min-Rule, 4 Modi, RECOVERY strikt | Teil M |
| Graceful-Shutdown | 4 Phasen, WAL-Flush, Totalfunktion | Teil N |
| Health-Monitoring | Heartbeat + Watchdog + Externer Monitor | Teil O |
| Trail-Map | Entscheidungsprotokoll, in Blackbox | Teil P |
| Queue-Integration | Dateibasiert, atomar, idempotent | Teil Q |
| Test-Strategie | ~325 Tests, ≥88% Coverage | Teil R |
| Implementierungsplan | 19 Phasen, 6 Meilensteine, ~44-67 Tage | Teil S |

---

## 5. Offene Themen aus v0.3.0 — Status

| # | Thema | Status in v0.3.0 | Status in v0.4.0 |
|---|---|---|---|
| 1 | Sanitization | 🟡 Offen | ✅ Teil K |
| 2 | Capability-Registry | 🟡 Offen | ✅ Teil L |
| 3 | Trail-Map | 🟢 Offen | ✅ Teil P |
| 4 | Questor-Health-Monitoring | 🟢 Offen | ✅ Teil O |
| 5 | Questor-Graceful-Shutdown | 🟢 Offen | ✅ Teil N |
| 6 | security_mode-Verhalten | 🟢 Offen | ✅ Teil M |
| 7 | Gremium-Integration der Queue | Nicht gelistet | ✅ Teil Q |
| 8 | Test-Strategie | Nicht gelistet | ✅ Teil R |
| 9 | Implementierungsplan | Nicht gelistet | ✅ Teil S |

**Alle offenen Themen aus v0.3.0 sind in v0.4.0 spezifiziert.**

---

*Ende des Hauptdokuments.*
*Für Details siehe die jeweiligen Detaildokumente.*
