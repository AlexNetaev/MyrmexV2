# 🧭 QUESTOR-INTERNA: THEMA 9 — IMPLEMENTIERUNGSPLAN
## Phasen, Abhängigkeiten, Meilensteine, Akzeptanzkriterien und Zeitplanung

| Feld | Wert |
|---|---|
| Dateiname | `questor_implementation_plan_v0.1.0.md` |
| Version | 0.1.0 |
| System | MYRMEX v2.4.0 + Questor v0.2.3 |
| Status | Arbeitsstand — Architektur-Spezifikation, keine Implementierungsfreigabe |
| Bezug | `structure_questor_interna_v0.4.0.md`, Teil S |
| | `structure_standalone_v2.4.0.md` v1.1.1, kanonisch |
| | `structure_hal_v0.2.0.md` |
| | `structure_standalone_questor_v0.2.3.md` |
| | `myrmex_questor_integration_tests_v0.4.0.md` |
| Sprache | Deutsch |
| Modus | Dry-Run / Spezifikation |

---

## 0. Dokumentenhierarchie und Geltung

```
1. structure_standalone_v2.4.0.md v1.1.1                    ← kanonisch
2. structure_hal_v0.2.0.md                                   ← HAL-Vertrag
3. structure_questor_interna_v0.4.0.md                       ← Questor-Interna GESAMT
4. diese Datei: questor_implementation_plan_v0.1.0.md        ← Detail: Implementierungsplan
5. structure_standalone_questor_v0.2.3.md                    ← unterstützend
6. myrmex_questor_integration_tests_v0.4.0.md                ← Testgrundlage
```

Bei Widersprüchen gilt die kanonische Hauptreferenz.

Dieses Dokument ist Teil S der Questor-Interna-Gesamtspezifikation.
Es ist eigenständig lesbar, setzt aber Grundkenntnisse der Questor-Architektur voraus.

---

## 1. Kritische Analyse des Bestehenden

### 1.1 Was bereits existiert

| Quelle | Phasen | Problem |
|---|---|---|
| `structure_standalone_v2.4.0.md` §13 | M0–M5 (Migration) | Deckt MYRMEX-Migration ab, nicht Questor-Interna. |
| `structure_standalone_v2.4.0.md` §14 | Phase 1–10 (Neubau) | Deckt MYRMEX-Neubau ab, nicht Questor-Interna. |
| `structure_hal_v0.2.0.md` §26 | HAL-H0 bis HAL-H6 | Deckt HAL ab, nicht Questor. |
| `structure_standalone_questor_v0.2.3.md` §12 | M0–M5 | Deckt Vertragsmigration ab, nicht Questor-Implementierung. |
| `structure_questor_interna_v0.3.0.md` §67 | Offene Themen | Liste der Themen, aber kein Implementierungsplan. |

### 1.2 Identifizierte Probleme

| # | Problem | Schweregrad | Begründung |
|---|---|---|---|
| P1 | **Kein Questor-spezifischer Implementierungsplan.** Die bestehenden Phasen decken MYRMEX und HAL ab, aber nicht die Questor-Interna. | **KRITISCH** | Ohne Plan ist die Implementierung unkoordiniert. |
| P2 | **Kein Abhängigkeitsgraph zwischen Questor-Modulen.** Welche Module müssen zuerst implementiert werden? | **KRITISCH** | Ohne Abhängigkeiten werden Module in der falschen Reihenfolge gebaut. |
| P3 | **Keine Akzeptanzkriterien pro Questor-Phase.** Wann ist eine Phase "fertig"? | Hoch | Ohne Kriterien ist der Fortschritt nicht messbar. |
| P4 | **Keine Risikobewertung.** Welche Risiken gibt es bei der Implementierung? | Hoch | Risiken werden nicht früh erkannt. |
| P5 | **Keine Integration mit MYRMEX- und HAL-Phasen.** Wann muss Questor mit MYRMEX und HAL integriert werden? | Hoch | Integrationsprobleme werden spät erkannt. |
| P6 | **Keine Teststrategie pro Phase.** Welche Tests müssen in jeder Phase bestanden werden? | Mittel | Tests werden nachgelagert statt begleitend. |
| P7 | **Keine Zeitplanung.** Wie lange dauert jede Phase? | Mittel | Ohne Zeitplanung ist das Projekt nicht planbar. |
| P8 | **Die neuen Themen (1–8) sind nicht in den bestehenden Phasen enthalten.** Sanitization, Capability-Registry, Security-Mode, Shutdown, Health-Monitoring, Trail-Map, Queue-Integration, Test-Strategie fehlen. | **KRITISCH** | Diese Themen sind neu und müssen in den Plan aufgenommen werden. |

### 1.3 Fazit der Analyse

Die bestehenden Implementierungsphasen (M0–M5, Phase 1–10, HAL-H0–H6) decken die **MYRMEX-** und **HAL-Seite** ab. Aber es fehlt ein **Questor-spezifischer Implementierungsplan**, der:
- Die Questor-Interna (Teil A–J) in Phasen gliedert.
- Die neuen Themen (1–8) integriert.
- Abhängigkeiten zwischen Questor-Modulen definiert.
- Akzeptanzkriterien pro Phase festlegt.
- Risiken bewertet.
- Eine Zeitplanung erstellt.

---

## 2. Abhängigkeitsgraph

### 2.1 Modulabhängigkeiten

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ABHÄNGIGKEITSGRAPH                           │
│                                                                     │
│  EBENE 0 (keine Abhängigkeiten):                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ Sanitization │  │ Capability-  │  │ Security-    │             │
│  │  (Thema 1)   │  │ Registry     │  │ Mode         │             │
│  │              │  │  (Thema 2)   │  │  (Thema 3)   │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│  ┌──────────────┐  ┌──────────────┐                                │
│  │ Health-      │  │ Trail-Map    │                                │
│  │ Monitoring   │  │  (Thema 6)   │                                │
│  │  (Thema 5)   │  │              │                                │
│  └──────────────┘  └──────────────┘                                │
│                                                                     │
│  EBENE 1 (abhängig von Ebene 0):                                   │
│  ┌──────────────┐  ┌──────────────┐                                │
│  │  Facade +    │  │  Loop-       │                                │
│  │  Validator   │  │  Registry    │                                │
│  └──────┬───────┘  └──────┬───────┘                                │
│         │                  │                                        │
│         ▼                  ▼                                        │
│  ┌──────────────────────────────────┐                              │
│  │         QuestCompass             │                              │
│  │  (Objective, Loop Selection,     │                              │
│  │   Evaluation, Decision Engine)   │                              │
│  └──────────────┬───────────────────┘                              │
│                 │                                                   │
│  EBENE 2 (abhängig von Ebene 1):                                   │
│                 ▼                                                   │
│  ┌──────────────────────────────────┐                              │
│  │     PolicyEvaluator +            │                              │
│  │     SafetyMonitor                │                              │
│  └──────────────┬───────────────────┘                              │
│                 │                                                   │
│                 ▼                                                   │
│  ┌──────────────────────────────────┐                              │
│  │         HAL-Bridge               │                              │
│  └──────────────┬───────────────────┘                              │
│                 │                                                   │
│  EBENE 3 (abhängig von Ebene 2):                                   │
│                 ▼                                                   │
│  ┌──────────────────────────────────┐                              │
│  │   ExpeditionLedger + WAL         │                              │
│  └──────────────┬───────────────────┘                              │
│                 │                                                   │
│                 ▼                                                   │
│  ┌──────────────────────────────────┐                              │
│  │        Result-Builder            │                              │
│  │   (+ Blackbox-Archiver)          │                              │
│  └──────────────┬───────────────────┘                              │
│                 │                                                   │
│  EBENE 4 (abhängig von Ebene 3):                                   │
│                 ▼                                                   │
│  ┌──────────────────────────────────┐                              │
│  │         Shutdown                 │                              │
│  │        (Thema 4)                 │                              │
│  └──────────────┬───────────────────┘                              │
│                 │                                                   │
│  EBENE 5 (abhängig von Ebene 4):                                   │
│                 ▼                                                   │
│  ┌──────────────────────────────────┐                              │
│  │      Queue-Integration           │                              │
│  │        (Thema 7)                 │                              │
│  └──────────────┬───────────────────┘                              │
│                 │                                                   │
│  EBENE 6 (abhängig von Ebene 5):                                   │
│                 ▼                                                   │
│  ┌──────────────────────────────────┐                              │
│  │         TESTS                    │                              │
│  │        (Thema 8)                 │                              │
│  └──────────────────────────────────┘                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Externe Abhängigkeiten

| Questor-Modul | Externe Abhängigkeit | Muss fertig sein vor |
|---|---|---|
| Contracts / Enums | MYRMEX Phase 1 (Verträge) | Q0 |
| Facade / Validator | MYRMEX Phase 8 (Dispatcher) | Q4 |
| HAL-Bridge | HAL Phase HAL-H1 (Interface) | Q8 |
| HAL-Bridge | MYRMEX Phase 5 (Resource Governor) | Q8 |
| Queue-Integration | MYRMEX Phase 8 (Dispatcher, Receiver) | Q14 |
| Result-Builder | MYRMEX Phase 2 (Archivar) | Q10 |

---

## 3. Meilensteine und Phasen

### 3.1 Übersicht

| Meilenstein | Phasen | Dauer (Schätzung) | Abhängigkeiten |
|---|---|---|---|
| **MS-1: Foundation** | Q0, Q1, Q2, Q3 | 7–10 Tage | Keine |
| **MS-2: Core Questor** | Q4, Q5, Q6, Q7, Q8 | 12–18 Tage | MS-1, HAL-H1 |
| **MS-3: Data & Results** | Q9, Q10 | 5–7 Tage | MS-2 |
| **MS-4: Operational** | Q11, Q12, Q13 | 4–7 Tage | MS-3 |
| **MS-5: Integration** | Q14 | 3–5 Tage | MS-4, MYRMEX Phase 8 |
| **MS-6: Tests** | Q15, Q16, Q17, Q18 | 13–20 Tage | MS-5 |
| **Gesamt** | Q0–Q18 | **~44–67 Tage** | |

### 3.2 Phase Q0: Verträge und Konfiguration

**Meilenstein:** MS-1 (Foundation)
**Dauer:** 1–2 Tage
**Abhängigkeiten:** MYRMEX Phase 1 (Verträge) muss abgeschlossen sein.

**Aufgaben:**
1. Questor-spezifische Enums definieren:
   - `ObjectiveType` (OPTIMIZE, EXPLORE, VALIDATE, DIAGNOSE, SIMULATE_ONLY, CLARIFY)
   - `AutonomyLevel` (STRICT, GUIDED, ADAPTIVE)
   - `SecurityMode` (NORMAL, SANDBOX, DEV_SANDBOX_ONLY, RECOVERY)
   - `GateMode` (NORMAL, FRACTURE_DIAGNOSIS, HIGH_RISK_OVERRIDE, SANDBOX)
   - `DecisionType` (für Trail-Map)
   - `HealthStatus` (HEALTHY, DEGRADED, UNHEALTHY, DEAD)
   - `WatchdogStatus` (OK, WARNING, CRITICAL)
   - `ShutdownPhase` (SIGNAL_RECEIVED, DRAINING, FINALIZING, TERMINATED)
2. Questor-Konfiguration definieren:
   - `SanitizationConfig`
   - `HealthMonitorConfig`
   - `ShutdownConfig`
   - `QueueConfig`
3. Questor-spezifische Datenverträge definieren:
   - `SanitizationResult`
   - `LLMOutputValidation`
   - `CapabilityDefinition`
   - `CapabilityCheckResult`
   - `Trail`
   - `TrailMap`
   - `HealthFile`
   - `ShutdownResult`
4. Pydantic-v2-Modelle für alle Verträge erstellen.

**Akzeptanzkriterien:**
- [ ] Alle Enums sind definiert und validierbar.
- [ ] Alle Konfigurationsmodelle sind Pydantic-v2-konform.
- [ ] Alle Datenverträge sind Pydantic-v2-konform.
- [ ] Mindestens 15 Unit-Tests für Verträge.
- [ ] Keine Abhängigkeit zu Questor-Logik (nur Datenstrukturen).

---

### 3.3 Phase Q1: Sanitization

**Meilenstein:** MS-1 (Foundation)
**Dauer:** 2–3 Tage
**Abhängigkeiten:** Q0 (Verträge)

**Aufgaben:**
1. `sanitization.py` implementieren:
   - Feld-Whitelist und Blocklist
   - Injection-Pattern-Scan (15 Patterns)
   - Inhaltsbereinigung (Control-Chars, Zero-Width, Längenbegrenzung)
   - XML-Tag-Escaping
   - Prompt-Struktur (System-Prompt, Kontext-Block, Aufgaben-Block)
2. `llm_output_validator.py` implementieren:
   - JSON-Parsing
   - Schema-Validierung
   - Safety-Claim-Erkennung
   - Constraint-Prüfung (parameter_bounds, allowed_capabilities)
   - Fallback-Logik
3. LLM-Adapter implementieren:
   - Ollama-Integration (abstrahiert)
   - Timeout-Handling
   - Retry-Logik (max. `max_calls`)

**Akzeptanzkriterien:**
- [ ] Alle 18 Sanitization-Unit-Tests bestehen (U-SAN-01 bis U-SAN-18).
- [ ] Injection-Patterns werden korrekt erkannt.
- [ ] LLM-Output wird korrekt validiert.
- [ ] Fallback funktioniert bei LLM-Ausfall.
- [ ] Keine sicherheitskritischen Felder gelangen an das LLM.
- [ ] Mindestens 95% Code-Coverage.

---

### 3.4 Phase Q2: Capability-Registry

**Meilenstein:** MS-1 (Foundation)
**Dauer:** 2–3 Tage
**Abhängigkeiten:** Q0 (Verträge)

**Aufgaben:**
1. `capability_registry.py` implementieren:
   - Registry-Laden aus YAML-Dateien
   - `check_capability()` (3 Ebenen: Registry, HAL, Package)
   - `validate_parameters()` (typsicher, NaN/Infinity)
   - `capabilities_available()` (PolicyEvaluator-Funktion)
   - `get_slots_for_capability()`
   - Integritäts-Hash
2. Capability-Definitionen erstellen:
   - `data/questor_capabilities/general/`
   - `data/questor_capabilities/chemie/`
   - `data/questor_capabilities/biologie/`
   - `data/questor_capabilities/ml/`
   - `data/questor_capabilities/physik/`
3. Korrektur: `QuestorSpec.allowed_capabilities` von `list[Capability]` auf `list[str]` ändern.

**Akzeptanzkriterien:**
- [ ] Alle 22 Capability-Registry-Unit-Tests bestehen (U-CAP-01 bis U-CAP-22).
- [ ] Registry lädt korrekt aus YAML-Dateien.
- [ ] `check_capability()` prüft alle 3 Ebenen.
- [ ] `validate_parameters()` erkennt NaN, Infinity, Typfehler.
- [ ] `capabilities_available()` funktioniert korrekt.
- [ ] Mindestens 4 Capability-Definitionen pro Domäne.
- [ ] Mindestens 90% Code-Coverage.

---

### 3.5 Phase Q3: Security-Mode

**Meilenstein:** MS-1 (Foundation)
**Dauer:** 1–2 Tage
**Abhängigkeiten:** Q0 (Verträge), Q2 (Capability-Registry)

**Aufgaben:**
1. `security_mode.py` implementieren:
   - `get_effective_security_mode()` (Min-Rule)
   - `validate_package_security_mode()` (Envelope-Check)
   - `filter_templates_by_security_mode()`
   - `policy_check_security_mode()` (PolicyEvaluator-Integration)
2. Security-Mode-Matrix implementieren:
   - NORMAL, SANDBOX, DEV_SANDBOX_ONLY, RECOVERY
   - Physische Actuation vs. Compute
   - RECOVERY-Einschränkungen

**Akzeptanzkriterien:**
- [ ] Alle 11 Security-Mode-Unit-Tests bestehen (U-SM-01 bis U-SM-11).
- [ ] Min-Rule funktioniert korrekt.
- [ ] RECOVERY erlaubt nur `reconcile_*` und `read_*`.
- [ ] Physische Actuation in SANDBOX wird abgelehnt.
- [ ] `security_mode` fehlt → `PACKAGE_INVALID`.
- [ ] Mindestens 95% Code-Coverage.

---

### 3.6 Phase Q4: Facade und Validator

**Meilenstein:** MS-2 (Core Questor)
**Dauer:** 2–3 Tage
**Abhängigkeiten:** Q0 (Verträge), Q1 (Sanitization), Q2 (Capability-Registry), Q3 (Security-Mode)

**Aufgaben:**
1. `facade.py` implementieren:
   - Queue-Lesen aus `pending/`
   - Ältestes-Paket-zuerst-Strategie
   - Envelope-Erkennung (vs. nacktes ResearchPackage)
   - `DIRECT_PACKAGE_FORBIDDEN`
2. `validator.py` implementieren:
   - Envelope-Struktur prüfen
   - `gate_record_ref` prüfen
   - `idempotency_key` kanonisch prüfen
   - `attempt_id` Bereich prüfen (0–999999)
   - `routing_graph` Pflichtfelder prüfen
   - `questor_spec` validieren
   - `security_mode` gegen Gate prüfen

**Akzeptanzkriterien:**
- [ ] Facade liest korrekt aus `pending/`.
- [ ] Validator erkennt alle ungültigen Envelopes.
- [ ] `DIRECT_PACKAGE_FORBIDDEN` wird korrekt ausgelöst.
- [ ] `PACKAGE_INVALID` wird korrekt ausgelöst.
- [ ] Idempotenz-Schutz funktioniert.
- [ ] Mindestens 20 Unit-Tests.
- [ ] Mindestens 85% Code-Coverage.

---

### 3.7 Phase Q5: QuestCompass

**Meilenstein:** MS-2 (Core Questor)
**Dauer:** 3–5 Tage
**Abhängigkeiten:** Q1 (Sanitization), Q2 (Capability-Registry), Q4 (Facade)

**Aufgaben:**
1. `objective_parser.py` implementieren:
   - Stufe 1: Deterministisch (objective_type aus QuestorSpec)
   - Stufe 2: Keyword-Matching
   - Stufe 2.5: Objective-Vervollständigung (LLM, optional)
   - Stufe 3: LLM-Advisor (nur falls unklar)
   - Clarity-Score-Berechnung
2. `compass.py` implementieren:
   - Loop Selection (Filter, Ranking, Kandidatenfenster)
   - Parameter-Füllung
   - Evaluation (pro objective_type)
   - Decision Engine (8 Regeln)
   - LLM-Advisor-Integration (3 Situationen)
   - FRACTURE_DIAGNOSIS-Sonderregel
3. `advisors/llm_advisor.py` implementieren:
   - Ollama-Integration
   - Prompt-Aufbau (mit Sanitization)
   - Output-Validierung
   - Fallback-Logik

**Akzeptanzkriterien:**
- [ ] Alle 15 QuestCompass-Komponententests bestehen (C-QC-01 bis C-QC-15).
- [ ] Objective Analysis funktioniert in allen 3 Stufen.
- [ ] Loop Selection funktioniert für STRICT, GUIDED, ADAPTIVE.
- [ ] Evaluation funktioniert für alle 6 objective_types.
- [ ] Decision Engine wendet alle 8 Regeln korrekt an.
- [ ] LLM-Advice wird korrekt angenommen oder abgelehnt.
- [ ] FRACTURE_DIAGNOSIS erzwingt STRICT.
- [ ] Mindestens 85% Code-Coverage.

---

### 3.8 Phase Q6: Loop-Architektur

**Meilenstein:** MS-2 (Core Questor)
**Dauer:** 2–3 Tage
**Abhängigkeiten:** Q2 (Capability-Registry), Q5 (QuestCompass)

**Aufgaben:**
1. `loop_registry.py` implementieren:
   - Template-Laden aus YAML-Dateien
   - Template-Validierung
   - Template-Filterung (objective_type, capabilities, budget)
   - Template-Versionierung
2. Loop-Template-Erstellung:
   - `data/questor_templates/chemie/`
   - `data/questor_templates/biologie/`
   - `data/questor_templates/ml/`
   - `data/questor_templates/physik/`
3. Loop-Instance-Erstellung und -Ausführung:
   - LoopInstance aus LoopTemplate + Parameter
   - Step-Ausführung (sequentiell)
   - Branch-Condition-Handling
   - Terminierung

**Akzeptanzkriterien:**
- [ ] LoopRegistry lädt korrekt aus YAML-Dateien.
- [ ] Template-Validierung erkennt ungültige Templates.
- [ ] Loop-Instance wird korrekt erstellt.
- [ ] Step-Ausführung funktioniert sequentiell.
- [ ] Branch-Conditions werden korrekt ausgewertet.
- [ ] Terminierung funktioniert korrekt.
- [ ] Mindestens 4 Templates pro Domäne.
- [ ] Mindestens 15 Unit-Tests.
- [ ] Mindestens 85% Code-Coverage.

---

### 3.9 Phase Q7: PolicyEvaluator und SafetyMonitor

**Meilenstein:** MS-2 (Core Questor)
**Dauer:** 2–3 Tage
**Abhängigkeiten:** Q2 (Capability-Registry), Q3 (Security-Mode), Q5 (QuestCompass), Q6 (Loop)

**Aufgaben:**
1. `policy_evaluator.py` implementieren:
   - 8 Prüfungen (Safety, Routing, Capability, Budget, Security-Mode, Occam, Dimension, GO)
   - VETO / GO-Entscheidung
   - `capabilities_available()` (aus Q2)
   - `policy_check_security_mode()` (aus Q3)
2. `safety_monitor.py` implementieren:
   - ESTOP-Überwachung
   - Interlock-Überwachung
   - Timeout-Überwachung
   - Lease-Expiry-Überwachung
   - Sicherheitsabbruch einleiten

**Akzeptanzkriterien:**
- [ ] Alle 9 PolicyEvaluator-Komponententests bestehen (C-PE-01 bis C-PE-09).
- [ ] Alle 8 Prüfungen funktionieren korrekt.
- [ ] VETO wird korrekt ausgelöst.
- [ ] ESTOP wird korrekt erkannt.
- [ ] Interlock wird korrekt erkannt.
- [ ] Timeout wird korrekt erkannt.
- [ ] Mindestens 95% Code-Coverage.

---

### 3.10 Phase Q8: HAL-Bridge

**Meilenstein:** MS-2 (Core Questor)
**Dauer:** 3–4 Tage
**Abhängigkeiten:** Q2 (Capability-Registry), Q3 (Security-Mode), Q7 (PolicyEvaluator), HAL Phase HAL-H1

**Aufgaben:**
1. `hal_bridge.py` implementieren:
   - LoopStep → HALCommand übersetzen
   - LoopStep → ProcessCommand übersetzen
   - HALCommandResult verarbeiten
   - ProcessResult verarbeiten
   - Idempotenz-Key erzeugen
   - Kosten aktualisieren
   - Parameter-Validierung (aus Q2)
   - Security-Mode-Prüfung (aus Q3)
2. HAL-Adapter implementieren:
   - `hal_interface.py` (Interface)
   - `dummy_hal.py` (für Tests)
3. Prozess-Lebenszyklus implementieren:
   - START, MONITOR, RESUME, HOLD, ABORT, RELEASE_STAGE
   - SAFE_HOLD, WAITING_FOR_RELEASE
   - Resume-Token

**Akzeptanzkriterien:**
- [ ] Alle 10 HAL-Bridge-Komponententests bestehen (C-HB-01 bis C-HB-10).
- [ ] LoopStep wird korrekt in HALCommand übersetzt.
- [ ] HALCommandResult wird korrekt verarbeitet.
- [ ] ESTOP → SAFETY_ABORT.
- [ ] LEASE_DENIED → OPERATIONAL_ABORT.
- [ ] DUPLICATE_BLOCKED → SUCCESS.
- [ ] Parameter-Validierung funktioniert.
- [ ] Security-Mode-Prüfung funktioniert.
- [ ] SAFE_HOLD und RESUME funktionieren.
- [ ] Mindestens 90% Code-Coverage.

---

### 3.11 Phase Q9: ExpeditionLedger und WAL

**Meilenstein:** MS-3 (Data & Results)
**Dauer:** 3–4 Tage
**Abhängigkeiten:** Q5 (QuestCompass), Q8 (HAL-Bridge)

**Aufgaben:**
1. `ledger.py` implementieren:
   - Ledger-Struktur
   - Genesis-Hash (C15)
   - Hash-Chain
   - NaN/Infinity-Prüfung (C18)
   - APPEND-ONLY
   - READ-ONLY nach Abschluss
2. `wal.py` implementieren:
   - WAL-Eintrag schreiben (vor Ausführung)
   - WAL-Eintrag aktualisieren (nach Ausführung)
   - WAL-Flush
   - WAL-Lebenszyklus (erstellen, schreiben, bereinigen)
3. `recovery.py` implementieren:
   - WAL lesen
   - Integrität prüfen
   - Letzten Checkpoint finden
   - Zustand rekonstruieren
   - RECOVERY_UNSAFE

**Akzeptanzkriterien:**
- [ ] Genesis-Hash ist deterministisch und reproduzierbar.
- [ ] Hash-Chain ist korrekt.
- [ ] NaN/Infinity wird erkannt und führt zu Fail-Closed.
- [ ] WAL wird korrekt geschrieben und flush'd.
- [ ] Recovery funktioniert korrekt.
- [ ] RECOVERY_UNSAFE wird korrekt ausgelöst.
- [ ] Mindestens 25 Unit-Tests.
- [ ] Mindestens 90% Code-Coverage.

---

### 3.12 Phase Q10: Result-Builder

**Meilenstein:** MS-3 (Data & Results)
**Dauer:** 2–3 Tage
**Abhängigkeiten:** Q9 (Ledger), Q5 (QuestCompass)

**Aufgaben:**
1. `result_builder.py` implementieren:
   - Status bestimmen
   - Sicherheitsregeln anwenden
   - Ergebnis-Daten sammeln
   - Kristallkandidaten erzeugen
   - Signale aus Kristallkandidaten erzeugen
   - Guardian-Validierung
   - Early-Abort-Ergebnis bauen
2. `blackbox_archiver.py` implementieren:
   - Blackbox schreiben
   - Retention-Class bestimmen
   - Limits prüfen
   - Rotation
3. `sequence.py` implementieren:
   - Sequence-Nummer atomar persistieren
   - Datei-Lock
   - `questor_instance_id` erzeugen

**Akzeptanzkriterien:**
- [ ] Alle 10 Result-Builder-Komponententests bestehen (C-RB-01 bis C-RB-10).
- [ ] Ergebnis wird korrekt gebaut.
- [ ] Kristallkandidaten werden korrekt erzeugt.
- [ ] Signale werden korrekt erzeugt.
- [ ] Bei SAFETY: Kristalle und Signale leer.
- [ ] `vollstaendig_flag` ist immer true.
- [ ] Guardian-Validierung funktioniert.
- [ ] Early-Abort-Ergebnis wird korrekt gebaut.
- [ ] Blackbox wird korrekt geschrieben.
- [ ] Sequence-Nummer ist atomar.
- [ ] Mindestens 90% Code-Coverage.

---

### 3.13 Phase Q11: Shutdown

**Meilenstein:** MS-4 (Operational)
**Dauer:** 1–2 Tage
**Abhängigkeiten:** Q9 (WAL), Q10 (Result-Builder)

**Aufgaben:**
1. `shutdown.py` implementieren:
   - Signal-Handler (SIGTERM, SIGINT)
   - Shutdown-Flag-Datei prüfen
   - Graceful-Shutdown-Prozedur
   - Force-Shutdown-Prozedur
   - HAL-Kommando abwarten
   - Prozess in SAFE_HOLD versetzen
   - WAL flush'd
   - Ergebnis bauen
   - Queue aktualisieren
   - Leases freigeben
   - Blackbox schreiben

**Akzeptanzkriterien:**
- [ ] Alle 13 Shutdown-Unit-Tests bestehen (U-SD-01 bis U-SD-13).
- [ ] SIGTERM wird korrekt behandelt.
- [ ] Graceful-Shutdown funktioniert.
- [ ] Force-Shutdown funktioniert.
- [ ] WAL wird flush'd.
- [ ] Ergebnis wird gebaut (`GRACEFUL_SHUTDOWN`).
- [ ] ESTOP hat Vorrang vor Shutdown.
- [ ] Mindestens 90% Code-Coverage.

---

### 3.14 Phase Q12: Health-Monitoring

**Meilenstein:** MS-4 (Operational)
**Dauer:** 2–3 Tage
**Abhängigkeiten:** Q0 (Verträge)

**Aufgaben:**
1. `health_monitor.py` implementieren:
   - Heartbeat-Writer (Thread)
   - Internal-Watchdog (Thread)
   - Externer Monitor (Pipeline-Orchestrator)
   - `determine_health_status()`
   - Alert-Cooldown
   - Recovery-Aktionen
2. `health.json` schreiben:
   - Atomares Schreiben (temp + rename)
   - Alle Felder aus `HealthFile`

**Akzeptanzkriterien:**
- [ ] Alle 15 Health-Monitoring-Unit-Tests bestehen (U-HM-01 bis U-HM-15).
- [ ] Heartbeat wird korrekt geschrieben.
- [ ] Watchdog erkennt Zustandsdauer-Überschreitung.
- [ ] Watchdog erkennt Speicherverbrauch.
- [ ] Watchdog erkennt CPU-Auslastung.
- [ ] Watchdog erkennt fehlenden Fortschritt.
- [ ] Externer Monitor liest korrekt.
- [ ] Alert-Cooldown funktioniert.
- [ ] Mindestens 85% Code-Coverage.

---

### 3.15 Phase Q13: Trail-Map

**Meilenstein:** MS-4 (Operational)
**Dauer:** 1–2 Tage
**Abhängigkeiten:** Q0 (Verträge), Q1 (Sanitization), Q2 (Capability-Registry)

**Aufgaben:**
1. `trail_map.py` implementieren:
   - Trail-Erzeugung
   - TrailMap-Verwaltung
   - TrailMapSummary
   - Trail-Map in Blackbox speichern
   - Trail-Map-Hash im Ledger protokollieren
2. `InitialTrailPolicy` definieren:
   - `create_trails: bool`
   - `require_evidence: bool`
   - `trail_detail_level: MINIMAL | STANDARD | FULL`

**Akzeptanzkriterien:**
- [ ] Alle 11 Trail-Map-Unit-Tests bestehen (U-TRAIL-01 bis U-TRAIL-11).
- [ ] Trails werden korrekt erstellt.
- [ ] Trail-Map wird korrekt finalisiert.
- [ ] TrailMapSummary wird korrekt erstellt.
- [ ] Trail-Map wird in Blackbox gespeichert.
- [ ] Trail-Map-Hash wird im Ledger protokolliert.
- [ ] `create_trails = false` → keine Trails.
- [ ] Mindestens 80% Code-Coverage.

---

### 3.16 Phase Q14: Queue-Integration

**Meilenstein:** MS-5 (Integration)
**Dauer:** 3–5 Tage
**Abhängigkeiten:** Q4 (Facade), Q10 (Result-Builder), Q11 (Shutdown), MYRMEX Phase 8

**Aufgaben:**
1. Queue-Integration implementieren:
   - Dispatcher → `pending/` schreiben
   - Questor → `processing/` → `completed/` oder `failed/`
   - Receiver → `completed/` und `failed/` lesen
   - Pipeline-Orchestrator → `registry.json` lesen
   - Archivar → `completed/` und `failed/` bereinigen
   - Delete-Requests verarbeiten
2. `registry.json` implementieren:
   - Datei-Lock
   - Status-Tracking
   - Atomare Updates
3. `health.json` in Queue integrieren.

**Akzeptanzkriterien:**
- [ ] Alle 14 Queue-Integration-Unit-Tests bestehen (U-QI-01 bis U-QI-14).
- [ ] Dispatcher schreibt korrekt in `pending/`.
- [ ] Questor verschiebt korrekt nach `processing/`.
- [ ] Questor schreibt korrekt nach `completed/` oder `failed/`.
- [ ] Receiver liest korrekt.
- [ ] Pipeline-Orchestrator liest `registry.json`.
- [ ] Archivar bereinigt korrekt.
- [ ] Delete-Requests werden korrekt verarbeitet.
- [ ] Registry-Lock funktioniert.
- [ ] Idempotenz-Schutz funktioniert.
- [ ] Mindestens 85% Code-Coverage.

---

### 3.17 Phase Q15: Unit-Tests

**Meilenstein:** MS-6 (Tests)
**Dauer:** 5–7 Tage
**Abhängigkeiten:** Q0–Q14 (alle Module)

**Aufgaben:**
1. Alle Unit-Tests implementieren (~252 Tests):
   - Sanitization (18 Tests)
   - Capability-Registry (22 Tests)
   - Security-Mode (11 Tests)
   - Trail-Map (11 Tests)
   - Health-Monitoring (15 Tests)
   - Shutdown (13 Tests)
   - Queue-Integration (14 Tests)
   - Objective-Parser (10 Tests)
   - Compass (20 Tests)
   - PolicyEvaluator (15 Tests)
   - LoopRegistry (10 Tests)
   - Ledger (15 Tests)
   - SafetyMonitor (10 Tests)
   - Recovery (12 Tests)
   - Sequence (8 Tests)
   - HAL-Bridge (20 Tests)
   - Result-Builder (20 Tests)
   - Blackbox-Archiver (8 Tests)
2. Test-Fixtures erstellen.
3. Mocks erstellen (mock_hal, mock_llm, mock_resource_governor, mock_filesystem).

**Akzeptanzkriterien:**
- [ ] Alle ~252 Unit-Tests bestehen.
- [ ] Coverage ≥ 88% gesamt.
- [ ] Coverage ≥ 95% für sicherheitskritische Module.
- [ ] Alle Fail-Closed-Punkte sind getestet.
- [ ] Alle Edge Cases sind getestet.

---

### 3.18 Phase Q16: Komponententests

**Meilenstein:** MS-6 (Tests)
**Dauer:** 3–5 Tage
**Abhängigkeiten:** Q15 (Unit-Tests)

**Aufgaben:**
1. Alle Komponententests implementieren (~44 Tests):
   - QuestCompass (15 Tests)
   - PolicyEvaluator (9 Tests)
   - HAL-Bridge (10 Tests)
   - Result-Builder (10 Tests)
2. Test-Szenarien erstellen:
   - Chemie-Kinetik (Happy Path)
   - Biologie-Inkubation (Langzeit-Prozess)
   - ML-Training (Compute)
   - Physik-Messung (Sensor)

**Akzeptanzkriterien:**
- [ ] Alle ~44 Komponententests bestehen.
- [ ] QuestCompass-Zyklus funktioniert end-to-end.
- [ ] PolicyEvaluator prüft alle 8 Regeln.
- [ ] HAL-Bridge übersetzt korrekt.
- [ ] Result-Builder baut korrekte Ergebnisse.

---

### 3.19 Phase Q17: Integrationstests

**Meilenstein:** MS-6 (Tests)
**Dauer:** 3–5 Tage
**Abhängigkeiten:** Q16 (Komponententests), MYRMEX Phase 8, HAL Phase HAL-H6

**Aufgaben:**
1. Suite I (18 Tests) durchführen.
2. Suite S (5 Tests) durchführen.
3. Suite R (12 Tests) durchführen.
4. Suite Z (8 Tests) durchführen.
5. Suite H (24 Tests) durchführen.
6. Suite N (7 Tests) durchführen.

**Akzeptanzkriterien:**
- [ ] Alle 74 bestehenden Integrationstests bestehen.
- [ ] Suite I: 18/18 BESTANDEN.
- [ ] Suite S: 5/5 BESTANDEN.
- [ ] Suite R: 12/12 BESTANDEN.
- [ ] Suite Z: 8/8 BESTANDEN.
- [ ] Suite H: 24/24 BESTANDEN.
- [ ] Suite N: 7/7 BESTANDEN.

---

### 3.20 Phase Q18: Sicherheits- und Performance-Tests

**Meilenstein:** MS-6 (Tests)
**Dauer:** 2–3 Tage
**Abhängigkeiten:** Q17 (Integrationstests)

**Aufgaben:**
1. Sicherheitstests implementieren (~30 Tests):
   - Prompt-Injection (10 Tests)
   - Capability-Bypass (5 Tests)
   - Security-Mode-Eskalation (5 Tests)
   - WAL-Manipulation (3 Tests)
   - Queue-Manipulation (5 Tests)
   - LLM-Output-Manipulation (2 Tests)
2. Performance-Tests implementieren (~10 Tests).
3. Stress-Tests implementieren (~11 Tests).

**Akzeptanzkriterien:**
- [ ] Alle ~30 Sicherheitstests bestehen.
- [ ] Alle ~10 Performance-Tests bestehen.
- [ ] Alle ~11 Stress-Tests bestehen.
- [ ] Keine Sicherheitslücken gefunden.
- [ ] Performance innerhalb der Limits.

---

## 4. Risikobewertung

| # | Risiko | Wahrscheinlichkeit | Auswirkung | Mitigation |
|---|---|---|---|---|
| R1 | **LLM-Backend (Ollama) ist nicht verfügbar oder instabil.** | Mittel | Hoch | Mock-LLM für Tests. Fallback auf deterministischen Pfad. |
| R2 | **HAL-Implementierung ist nicht fertig, wenn Questor HAL-Bridge braucht.** | Mittel | Hoch | Dummy-HAL für Tests. HAL-Bridge gegen Interface entwickeln. |
| R3 | **MYRMEX-Implementierung ist nicht fertig, wenn Questor Queue-Integration braucht.** | Mittel | Hoch | Queue-Integration gegen Dateisystem entwickeln. MYRMEX-Integration nachgelagert. |
| R4 | **Prompt-Injection-Angriffe werden nicht erkannt.** | Niedrig | **KRITISCH** | Mehrschichtige Verteidigung (Whitelist + Pattern-Scan + Output-Validierung). Regelmäßige Pattern-Updates. |
| R5 | **Langzeit-Prozesse (72h) sind schwer zu testen.** | Hoch | Mittel | Mock-HAL mit beschleunigter Zeit. SAFE_HOLD und RESUME testen. |
| R6 | **Die Queue wird bei vielen Paketen langsam.** | Mittel | Mittel | Performance-Tests. Queue-Limits. Bereinigung. |
| R7 | **Der WAL wird zu groß.** | Niedrig | Mittel | WAL-Bereinigung nach DONE. WAL-Größe überwachen. |
| R8 | **Die Trail-Map wird zu groß.** | Niedrig | Niedrig | Trail-Map-Limits. Blackbox-Limits (100 MB). |
| R9 | **Die Implementierung dauert länger als geplant.** | Hoch | Mittel | Puffer einplanen. Kritische Pfade identifizieren. |
| R10 | **Die Coverage-Ziele werden nicht erreicht.** | Mittel | Mittel | Coverage-Gates in CI/CD. Regelmäßige Coverage-Reviews. |

---

## 5. Zeitplan

### 5.1 Gantt-Diagramm (vereinfacht)

```
Woche:     1    2    3    4    5    6    7    8    9   10   11   12   13   14
           |    |    |    |    |    |    |    |    |    |    |    |    |    |
MS-1:      ████████████
  Q0:      ██
  Q1:        ████
  Q2:        ████
  Q3:          ██
           |    |    |    |    |    |    |    |    |    |    |    |    |    |
MS-2:              ████████████████████████
  Q4:              ████
  Q5:                ██████
  Q6:                    ████
  Q7:                      ████
  Q8:                        ██████
           |    |    |    |    |    |    |    |    |    |    |    |    |    |
MS-3:                                    ██████████
  Q9:                                    ██████
  Q10:                                       ████
           |    |    |    |    |    |    |    |    |    |    |    |    |    |
MS-4:                                            ████████
  Q11:                                           ██
  Q12:                                             ████
  Q13:                                               ██
           |    |    |    |    |    |    |    |    |    |    |    |    |    |
MS-5:                                                    ██████
  Q14:                                                   ██████
           |    |    |    |    |    |    |    |    |    |    |    |    |    |
MS-6:                                                          ████████████████
  Q15:                                                         ████████
  Q16:                                                             ██████
  Q17:                                                                 ██████
  Q18:                                                                     ████
           |    |    |    |    |    |    |    |    |    |    |    |    |    |
```

### 5.2 Kritischer Pfad

Der kritische Pfad ist:
```
Q0 → Q1 → Q5 → Q7 → Q8 → Q9 → Q10 → Q11 → Q14 → Q15 → Q16 → Q17 → Q18
```

**Geschätzte Dauer des kritischen Pfads:** ~44–55 Tage (1 Entwickler)

### 5.3 Parallelisierung

Die folgenden Phasen können parallelisiert werden:
- Q1 (Sanitization) und Q2 (Capability-Registry) und Q3 (Security-Mode)
- Q12 (Health-Monitoring) und Q13 (Trail-Map)
- Q15 (Unit-Tests) und Q16 (Komponententests)

**Mit 2 Entwicklern:** ~30–40 Tage
**Mit 3 Entwicklern:** ~22–30 Tage

---

## 6. Integration mit MYRMEX und HAL

### 6.1 Meilenstein-Abhängigkeiten

| Questor-Meilenstein | MYRMEX-Phase | HAL-Phase | Bedingung |
|---|---|---|---|
| MS-1 (Foundation) | Phase 1 (Verträge) | — | MYRMEX Phase 1 muss fertig sein |
| MS-2 (Core Questor) | Phase 5 (Resource Governor) | HAL-H1 (Interface) | HAL-H1 muss fertig sein |
| MS-3 (Data & Results) | Phase 2 (Archivar) | — | MYRMEX Phase 2 muss fertig sein |
| MS-4 (Operational) | — | — | Keine externe Abhängigkeit |
| MS-5 (Integration) | Phase 8 (Dispatcher, Receiver) | HAL-H6 (Dummy) | MYRMEX Phase 8 muss fertig sein |
| MS-6 (Tests) | Phase 10 (E2E) | HAL-H6 (Dummy) | Alle müssen fertig sein |

### 6.2 Empfohlene Reihenfolge

```
WOCHE 1-2:
  MYRMEX Phase 1 (Verträge)
  Questor Q0 (Verträge)
  Questor Q1 (Sanitization)
  Questor Q2 (Capability-Registry)
  Questor Q3 (Security-Mode)

WOCHE 3-4:
  MYRMEX Phase 2 (Archivar)
  MYRMEX Phase 5 (Resource Governor)
  HAL Phase HAL-H1 (Interface)
  Questor Q4 (Facade)
  Questor Q5 (QuestCompass)

WOCHE 5-6:
  HAL Phase HAL-H2 (Slot/Lease)
  HAL Phase HAL-H3 (Zonen/Prozess)
  Questor Q6 (Loop)
  Questor Q7 (PolicyEvaluator)
  Questor Q8 (HAL-Bridge)

WOCHE 7-8:
  HAL Phase HAL-H4 (ESTOP/Interlock)
  HAL Phase HAL-H5 (Compute/Schema)
  Questor Q9 (Ledger/WAL)
  Questor Q10 (Result-Builder)

WOCHE 9:
  HAL Phase HAL-H6 (Dummy)
  Questor Q11 (Shutdown)
  Questor Q12 (Health-Monitoring)
  Questor Q13 (Trail-Map)

WOCHE 10:
  MYRMEX Phase 8 (Dispatcher/Receiver)
  Questor Q14 (Queue-Integration)

WOCHE 11-14:
  MYRMEX Phase 10 (E2E)
  Questor Q15 (Unit-Tests)
  Questor Q16 (Komponententests)
  Questor Q17 (Integrationstests)
  Questor Q18 (Sicherheits-/Performance-Tests)
```

---

## 7. Teststrategie pro Phase

| Phase | Test-Typ | Anzahl | Coverage-Ziel |
|---|---|---|---|
| Q0 | Unit-Tests (Verträge) | 15 | 90% |
| Q1 | Unit-Tests (Sanitization) | 18 | 95% |
| Q2 | Unit-Tests (Capability-Registry) | 22 | 90% |
| Q3 | Unit-Tests (Security-Mode) | 11 | 95% |
| Q4 | Unit-Tests (Facade/Validator) | 20 | 85% |
| Q5 | Unit-Tests + Komponenten (QuestCompass) | 35 | 85% |
| Q6 | Unit-Tests (Loop) | 15 | 85% |
| Q7 | Unit-Tests + Komponenten (Policy/Safety) | 24 | 95% |
| Q8 | Unit-Tests + Komponenten (HAL-Bridge) | 30 | 90% |
| Q9 | Unit-Tests (Ledger/WAL) | 25 | 90% |
| Q10 | Unit-Tests + Komponenten (Result-Builder) | 30 | 90% |
| Q11 | Unit-Tests (Shutdown) | 13 | 90% |
| Q12 | Unit-Tests (Health-Monitoring) | 15 | 85% |
| Q13 | Unit-Tests (Trail-Map) | 11 | 80% |
| Q14 | Unit-Tests (Queue-Integration) | 14 | 85% |
| Q15 | Alle Unit-Tests (Wiederholung) | ~252 | ≥ 88% |
| Q16 | Alle Komponententests | ~44 | — |
| Q17 | Alle Integrationstests (Suite I, S, R, Z, H, N) | 74 | — |
| Q18 | Sicherheits-/Performance-/Stress-Tests | ~51 | — |
| **Gesamt** | | **~421** | **≥ 88%** |

---

## 8. Akzeptanzkriterien für das Gesamtsystem

Nach Abschluss aller Phasen muss gelten:

| # | Kriterium | Quelle |
|---|---|---|
| 1 | Alle ~421 Tests bestehen | Thema 8 |
| 2 | Coverage ≥ 88% gesamt | Thema 8 |
| 3 | Coverage ≥ 95% für sicherheitskritische Module | Thema 8 |
| 4 | Alle Fail-Closed-Punkte sind getestet | Thema 8 |
| 5 | Keine Sicherheitslücken gefunden | Thema 8 |
| 6 | Performance innerhalb der Limits | Thema 8 |
| 7 | Alle 74 bestehenden Integrationstests bestehen | Testdatei v0.4.0 |
| 8 | Questor schreibt nicht in Atlas/Archiv | Hauptreferenz |
| 9 | Questor setzt ESTOP nicht zurück | Hauptreferenz |
| 10 | Questor vergibt keine Leases | Hauptreferenz |
| 11 | Blackbox bleibt lokal | Hauptreferenz |
| 12 | Operational ≠ Scientific | Hauptreferenz |
| 13 | ESTOP ≠ LEASE_DENIED | Hauptreferenz |
| 14 | LLM ist nur Advisor | Questor v0.2.3 |
| 15 | Totalfunktion: Jedes Paket → genau ein Ergebnis | Questor-Interna |
| 16 | Deterministic-first | Questor-Interna |
| 17 | Fail-Closed bei Unklarheit | Questor-Interna |
| 18 | Keine produktiven Altbezeichnungen | Hauptreferenz |
| 19 | `idempotency_key` ist kanonisch | Hauptreferenz |
| 20 | `attempt_id` ist eingeschränkt (0–999999) | Hauptreferenz |

---

## 9. Offene Fragen und Risiken

| # | Frage / Risiko | Schweregrad | Empfehlung |
|---|---|---|---|
| Q1 | **Soll die Implementierung mit einem Dummy-Questor beginnen?** | Mittel | Empfehlung: JA. Ein Dummy-Questor ermöglicht frühe Integrationstests, bevor die vollständige Implementierung fertig ist. |
| Q2 | **Soll die Implementierung in einem separaten Repository erfolgen?** | Mittel | Empfehlung: NEIN. Questor sollte im selben Repository wie MYRMEX implementiert werden, um die Integration zu erleichtern. |
| Q3 | **Wie wird die LLM-Integration getestet?** | Hoch | Empfehlung: Mock-LLM mit deterministischen Antworten. Keine echten LLM-Aufrufe in Tests. |
| Q4 | **Wie wird die HAL-Integration getestet?** | Hoch | Empfehlung: Dummy-HAL aus `structure_hal_v0.2.0.md` §24. |
| Q5 | **Wie wird die Queue-Integration getestet?** | Mittel | Empfehlung: Dateisystem-basierte Tests mit `tmp_path` Fixture. |
| Q6 | **Soll die Implementierung mit CI/CD unterstützt werden?** | Mittel | Empfehlung: JA. GitHub Actions oder GitLab CI für automatische Tests. |
| Q7 | **Wie wird die Dokumentation während der Implementierung gepflegt?** | Niedrig | Empfehlung: Docstrings in jedem Modul. README pro Phase. |
| Q8 | **Was passiert, wenn eine Phase nicht abgeschlossen werden kann?** | Mittel | Empfehlung: Blocker melden. Phase als "Blockiert" markieren. Nächste Phase beginnen, wenn möglich. |
| Q9 | **Soll die Implementierung mit einem Code-Review-Prozess begleitet werden?** | Mittel | Empfehlung: JA. Jede Phase sollte von einem zweiten Entwickler reviewed werden. |
| Q10 | **Wie wird die Performance während der Implementierung überwacht?** | Niedrig | Empfehlung: Performance-Tests in jeder Phase. Profiling bei Verdacht auf Performance-Probleme. |

---

## 10. Status-Report-Template

Nach jeder Phase ist folgender Report zu erstellen:

```
Phase: [Q-Nummer]
Name: [Name]
Status: Abgeschlossen | In Arbeit | Blockiert
Modus: Dry-Run | Implementierung
Erstellte Dateien:
  - [Datei]
Tests:
  - X/Y bestanden
Akzeptanzkriterien:
  - [x] Kriterium 1
  - [ ] Kriterium 2
Blocker:
  - [Blocker oder keine]
Nicht-Blocker:
  - [Nicht-Blocker oder keine]
Nächster Schritt:
  - [Beschreibung]
Offene Fragen:
  - [Fragen oder keine]
```

---

## 11. Zusammenfassung der Spezifikation

| Aspekt | Definition |
|---|---|
| **Phasen** | Q0–Q18 (19 Phasen) |
| **Meilensteine** | MS-1 bis MS-6 (6 Meilensteine) |
| **Gesamtdauer** | ~44–67 Tage (1 Entwickler), ~22–30 Tage (3 Entwickler) |
| **Test-Anzahl** | ~421 Tests |
| **Coverage-Ziel** | ≥ 88% gesamt, ≥ 95% sicherheitskritisch |
| **Kritischer Pfad** | Q0 → Q1 → Q5 → Q7 → Q8 → Q9 → Q10 → Q11 → Q14 → Q15 → Q16 → Q17 → Q18 |
| **Externe Abhängigkeiten** | MYRMEX Phase 1, 2, 5, 8; HAL Phase HAL-H1, HAL-H6 |
| **Risiken** | 10 identifizierte Risiken mit Mitigation |
| **Akzeptanzkriterien** | 20 Kriterien für das Gesamtsystem |

---

## 12. Kritische Bewertung der eigenen Spezifikation

**Stärken:**
- Vollständiger Abhängigkeitsgraph zwischen Questor-Modulen
- Klare Meilensteine mit definierten Phasen
- Akzeptanzkriterien pro Phase
- Risikobewertung mit Mitigation
- Zeitplan mit Parallelisierungsoptionen
- Integration mit MYRMEX- und HAL-Phasen
- Teststrategie pro Phase
- 20 Akzeptanzkriterien für das Gesamtsystem

**Schwächen:**
- Die Zeitplanung ist eine Schätzung und kann sich ändern.
- Die Abhängigkeiten von MYRMEX und HAL können zu Verzögerungen führen.
- Die LLM-Integration ist ein Risiko, das schwer zu testen ist.
- Die Langzeit-Prozess-Tests sind schwer zu simulieren.

**Empfehlung:** Die Spezifikation ist implementierungsreif, ABER:
1. Die Implementierung sollte mit einem Dummy-Questor beginnen, um frühe Integrationstests zu ermöglichen.
2. Die LLM-Integration sollte mit einem Mock-LLM getestet werden.
3. Die HAL-Integration sollte mit einem Dummy-HAL getestet werden.
4. Die Queue-Integration sollte mit Dateisystem-basierten Tests getestet werden.
5. CI/CD sollte von Anfang an eingerichtet werden.
6. Jede Phase sollte mit einem Status-Report abgeschlossen werden.

---

## 13. Kreuzreferenzen

| Referenz | Beziehung |
|---|---|
| `structure_questor_interna_v0.4.0.md`, Teil S | Dieses Dokument IST Teil S |
| `structure_standalone_v2.4.0.md` §13 | MYRMEX-Migrationsphasen (M0–M5) |
| `structure_standalone_v2.4.0.md` §14 | MYRMEX-Neubau-Phasen (1–10) |
| `structure_hal_v0.2.0.md` §26 | HAL-Implementierungsphasen (HAL-H0 bis HAL-H6) |
| `structure_standalone_questor_v0.2.3.md` §12 | Questor-Migrationsphasen (M0–M5) |
| `questor_sanitization_v0.1.0.md` | Phase Q1 |
| `questor_capability_registry_v0.1.0.md` | Phase Q2 |
| `questor_security_mode_v0.1.0.md` | Phase Q3 |
| `questor_graceful_shutdown_v0.1.0.md` | Phase Q11 |
| `questor_health_monitoring_v0.1.0.md` | Phase Q12 |
| `questor_trail_map_v0.1.0.md` | Phase Q13 |
| `questor_queue_integration_v0.1.0.md` | Phase Q14 |
| `questor_test_strategy_v0.1.0.md` | Phasen Q15–Q18 |
| `myrmex_questor_integration_tests_v0.4.0.md` | 74 bestehende Integrationstests |

---

## 14. Datenintegritäts-Check für dieses Dokument

| Prüfpunkttyp | Erwartet | Enthalten |
|---|---:|---:|
| Kritische Probleme | 8 | 8 |
| Phasen | 19 | 19 |
| Meilensteine | 6 | 6 |
| Akzeptanzkriterien pro Phase | 19 | 19 |
| Risiken | 10 | 10 |
| Zeitplan | 1 | 1 |
| Kritischer Pfad | 1 | 1 |
| Integration mit MYRMEX/HAL | 1 | 1 |
| Teststrategie pro Phase | 1 | 1 |
| Gesamtsystem-Akzeptanzkriterien | 20 | 20 |
| Offene Fragen/Risiken | 10 | 10 |
| Kritische Bewertung | Ja | Ja |
| Kreuzreferenzen | Ja | Ja |