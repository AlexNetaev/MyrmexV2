# 🗺️ ROADMAP — IMPLEMENTIERUNGSPLAN UND PHASEN

| Feld | Wert |
| --- | --- |
| Dateiname | `ops/ROADMAP.md` |
| Version | `1.1.0-atlas-hyb.1` |
| Status | `ÄNDERUNGSANTRAG ATLAS-HYB-1.0.0 — nach Freigabe BINDEND` |
| System | `MYRMEX v2.4.0 + Questor v0.2.3 + HAL v0.2.0` |
| Schicht | `Layer 2 (ops/) — referenziert foundation/ und specs/` |
| Datum | `21. August 2026` |

## 0. Geltung und Änderungsregeln

Dieses Dokument definiert die vollständige Implementierungsplanung für das Gesamtsystem.

**Regel:** Dieses Dokument referenziert Verträge aus `CONTRACTS.md` und Sicherheitsregeln aus `CHARTER.md`.
Es definiert keine neuen Verträge und keine neuen Sicherheitsregeln.

**Konfliktregel:** Bei Widersprüchen gilt `CHARTER.md` > `CONTRACTS.md` > `specs/*` > `ops/VALIDATION.md` > dieses Dokument.

## §0.1 Änderungsantrag ATLAS-HYB-1.0.0 — Atlas-Hybrid-Phasen

Dieser Änderungsantrag fügt die Implementierungsphasen für das Atlas-Hybrid-System in die Roadmap ein.

Das Atlas-Hybrid-System wird als eigener Phasen-Block (A1–A5) geführt, der auf den MYRMEX-Neubau-Phasen 1 bis 3 aufbaut und vor der finalen End-to-End-Integration (Phase 10) abgeschlossen sein muss.

Regeln:

- Dieser Änderungsantrag definiert keine neuen Verträge (→ CONTRACTS.md).
- Dieser Änderungsantrag definiert keine neuen Sicherheitsregeln (→ CHARTER.md).
- Die Atlas-Hybrid-Phasen respektieren das Blackboard-Pattern und die Trennung von Operational und Scientific.
- Questor erhält auch in der Implementierung keine Atlas-Schreibrechte.

---

## §1 Roadmap-Übersicht und Grundprinzipien

### §1.1 Zweck

Dieses Dokument definiert:

- Die vollständige Phasenplanung für MYRMEX v2.4.0 + Questor v0.2.3 + HAL v0.2.0
- Die Abhängigkeiten zwischen Phasen
- Die Meilensteine und Zeitplanung
- Die Akzeptanzkriterien pro Phase
- Die Risikobewertung
- Die Test-Gates pro Phase

### §1.2 Die sechs Roadmap-Grundprinzipien

| # | Prinzip | Bedeutung | CHARTER-Referenz |
| --- | --- | --- | --- |
| 1 | Phase-by-Phase | Arbeite eine Phase vollständig ab, bevor die nächste beginnt. | — |
| 2 | Kein Code ohne Freigabe | Schreibe keinen Code für Phasen, die nicht freigegeben sind. | — |
| 3 | Dry-Run-Modus | Wenn keine Implementierungsfreigabe vorliegt: kein Code, keine Dateiänderungen, nur mentale Simulation. | — |
| 4 | TDD | Tests werden vor oder parallel zum Code geschrieben. | — |
| 5 | Keine späteren Phasen vorziehen | Implementiere nur die explizit freigegebene Phase. | — |
| 6 | Status-Report nach jeder Phase | Nach jeder Phase ist ein Status-Report zu erstellen. | — |

### §1.3 Rolle der implementierenden KI

Die implementierende KI handelt als:

- Senior Software Engineer
- Systems Architect
- Test Engineer für Systemintegration

### §1.4 Arbeitsregeln

| Regel | Beschreibung |
| --- | --- |
| AR-1 | Arbeite phase-by-phase. |
| AR-2 | Schließe eine Phase vollständig ab, bevor die nächste beginnt. |
| AR-3 | Schreibe keinen Code für Phasen, die nicht freigegeben sind. |
| AR-4 | Wenn keine Implementierungsfreigabe vorliegt: kein Code, keine Dateiänderungen, nur Dry-Run / mentale Simulation. |
| AR-5 | Wenn Implementierungsfreigabe vorliegt: nur die explizit freigegebene Phase implementieren. |
| AR-6 | Python 3.10+, Pydantic v2, pytest. |
| AR-7 | Keine späteren Phasen vorziehen. |
| AR-8 | Nach jeder Phase Status-Report schreiben. |
| AR-9 | Blocker und Nicht-Blocker immer getrennt melden. |

---

## §2 Phasen-Übersicht (alle Systeme)

### §2.1 Gesamtsystem-Phasen

| System | Phasen | Anzahl | Gesamtdauer (Schätzung) |
| --- | --- | --- | --- |
| MYRMEX (Migration) | M0–M5 | 6 | 10–15 Tage |
| MYRMEX (Neubau) | Phase 1–10 | 10 | 25–35 Tage |
| Atlas-Hybrid | A1–A5 | 5 | 12–18 Tage |
| HAL | HAL-H0 bis HAL-H6 | 7 | 15–22 Tage |
| Questor | Q0–Q18 | 19 | 44–67 Tage |
| Gesamt | | 47 | ~106–157 Tage |

### §2.2 Phasen-Typen

| Typ | Bedeutung |
| --- | --- |
| Migration | Umbenennung und Vertragsmigration von v2.3.1 auf v2.4.0 |
| Neubau | Sauberer Neuaufbau ohne Bestand |
| Atlas-Hybrid | Evidenzbasierte, semantische und explorationsfähige Wissenschaftskarte |
| HAL | Hardware Abstraction Layer |
| Questor | Questor-Interna (Teile A–S) |

---

## §3 MYRMEX-Migrationsphasen (M0–M5)

### §3.1 Phase M0: Archivierung und Schnitt

**Ziel:** Alte Referenz archivieren, neue Referenz aktivieren, keine Adapter einplanen.

**Aufgaben:**

- `structure_standalone_v2.3.1.md` als archiviert markieren
- Diese Strukturdatei als primäre Referenz bestätigen
- `structure_standalone_questor_v0.2.3.md` als unterstützend einordnen
- Sicherstellen, dass keine produktive Adapterlogik geplant ist

**Akzeptanzkriterien:**

- [ ] Keine aktive Doppelreferenz
- [ ] Keine produktiven Altbezeichnungen geplant
- [ ] Keine Adapter geplant
- [ ] Konflikthierarchie dokumentiert

### §3.2 Phase M1: Vertrags-Umbenennung

**Ziel:** Neue Vertragswelt sauber einführen.

**Aufgaben:**

- Neue Ergebnis- und Instanzbezeichnungen einführen
- `QuestorDispatchEnvelope` einführen
- `QuestorMetadata`, `LocalAuditRef`, `OperationalMetrics` definieren
- Kanonischen `idempotency_key` implementieren (→ CONTRACTS §8.1)
- QuestorSpec-Defaults implementieren (→ CONTRACTS §1.2)
- Circuit-Breaker-Zustände explizit machen
- Policy-Veto-Review-Parameter konfigurierbar machen

**Akzeptanzkriterien:**

- [ ] Keine alten Bezeichnungen in aktiven Zielquellen
- [ ] Neue Pydantic-Modelle existieren
- [ ] `idempotency_key` ist kanonisch (→ CONTRACTS §8.1)
- [ ] `attempt_id` ist eingeschränkt (0–999999)
- [ ] Mindestens 25 Vertragstests

### §3.3 Phase M2: Archivar auf Questor-Ergebnis umstellen

**Ziel:** Archivar verarbeitet ausschließlich das neue Ergebnis.

**Aufgaben:**

- Sequence-Prüfung auf `questor_instance_id`
- `questor_metadata` optional verarbeiten
- `operational_metrics` nur operational verwenden
- Keine Blackbox-Zugriffe (→ CHARTER §SR-07)

**Akzeptanzkriterien:**

- [ ] Valide Questor-Ergebnisse werden akzeptiert
- [ ] Duplikate werden verworfen
- [ ] OPERATIONALE Abbrüche erzeugen keine wissenschaftlichen Signale (→ CHARTER §SR-08)
- [ ] Mindestens 20 Archivar-Integrationstests

### §3.4 Phase M3: Dispatcher und Receiver umstellen

**Ziel:** Produktiver Envelope-basierter Dispatch, sauberer Empfang des neuen Ergebnisses.

**Aufgaben:**

- Dispatcher baut Envelope
- Dispatcher prüft Gate, Lease, Security-Mode
- Receiver empfängt neues Ergebnis
- Direkte Paketübergaben nur sandbox/dev

**Akzeptanzkriterien:**

- [ ] Dispatcher sendet keine nackten Produktivpakete
- [ ] Envelope enthält `gate_record_ref` (→ CHARTER §SR-53)
- [ ] Receiver validiert Vertrag
- [ ] Mindestens 20 Dispatcher/Receiver-Tests

### §3.5 Phase M4: Questor-Implementierung oder Questor-Dummy

**Ziel:** Questor oder vertragstreuer Dummy ist vorhanden.

**Aufgaben:**

- Entweder: vollständige Questor-Implementierung gemäß v0.2.3
- Oder für Integrationstests: `DummyQuestor`, der vertragstreu reagiert

**Akzeptanzkriterien:**

- [ ] Questor/Dummy empfängt Envelope
- [ ] Liefert neues Ergebnis
- [ ] Keine direkten Atlas-/Archivzugriffe (→ CHARTER §SR-04)
- [ ] Blackbox bleibt lokal (→ CHARTER §SR-07)
- [ ] ESTOP, LEASE_DENIED, ROUTING_LOOP_TIMEOUT, SCIENTIFIC/OPERATIONAL werden korrekt getrennt (→ CHARTER §SR-08, §SR-09)

### §3.6 Phase M5: Gesamtsystem-Tests

**Ziel:** Vollständige Integrationstests ohne Adapter.

**Aufgaben:**

- Suite N, I, S, R, Z aus der aktuellen Testdatei
- Questor-spezifische Sicherheits- und Blackbox-Tests

**Akzeptanzkriterien:**

- [ ] Alle Tests bestehen
- [ ] Keine aktiven Altbezeichnungen
- [ ] Keine Adapter in finalen Tests
- [ ] Blackbox bleibt isoliert (→ CHARTER §SR-07)
- [ ] Operational bleibt ohne wissenschaftliches Signal (→ CHARTER §SR-08)

---

## §4 MYRMEX-Neubau-Phasen (Phase 1–10)

### §4.1 Phase 1: Projekt-Setup + Datenverträge

**Aufgaben:**

- Repository-Struktur anlegen
- Requirements und Konfiguration erstellen
- Alle Vertragsmodelle definieren (→ CONTRACTS §1–§6)

**Akzeptanzkriterien:**

- [ ] Alle Modelle sind Pydantic-v2-konform
- [ ] Alle Enums vorhanden
- [ ] Idempotenzregeln korrekt (→ CONTRACTS §8)
- [ ] Routing-Graph enthält Pflichtfelder
- [ ] Gate-Modi vollständig
- [ ] Mindestens 20 Unit-Tests

### §4.2 Phase 2: Event-Sourcing + Archiv + Archivar

**Aufgaben:**

- Atlas-Event-Store
- Snapshots
- Recovery
- Archivar für neue Ergebnisse
- Signal-Registry
- Kristallisation und Verfall

**Akzeptanzkriterien:**

- [ ] Duplikate werden verworfen
- [ ] Unvollständige Pakete werden nicht als Kristalle übernommen
- [ ] OPERATIONALE Abbrüche erzeugen keine wissenschaftlichen Signale (→ CHARTER §SR-08)
- [ ] Signal-Resolution korrekt
- [ ] Mindestens 30 Unit-Tests

### §4.3 Phase 3: Atlas + Kartograph

**Aufgaben:**

- DBSCAN/UMAP-Logik
- fracture_score
- Zone-Health
- FULL_REBUILD
- NEUAUSRICHTEN
- Seed-Zonen
- Atlas-Versionierung

**Akzeptanzkriterien:**

- [ ] Unbekannte Dimensionen werden nicht als null oder 0 behandelt
- [ ] FULL_REBUILD atomar
- [ ] Alte Atlas-Version bleibt für laufende Quests gültig
- [ ] Mindestens 40 Unit-Tests

### §4.4 Phase 4: Transaktions-Schicht

**Aufgaben:**

- WAL
- State Machine
- Recovery
- Crash-Sicherheit

**Akzeptanzkriterien:**

- [ ] Recovery setzt Pakete in die korrekte Stufe zurück
- [ ] Keine übersprungenen Phasen
- [ ] Lease-TTL wird beachtet
- [ ] Mindestens 25 Unit-Tests

### §4.5 Phase 5: Resource Governor + HAL-Vertrag

**Aufgaben:**

- Slot-Manager
- Governor
- ESTOP-Handler
- HAL-Interface
- Dummy-HAL

**Akzeptanzkriterien:**

- [ ] Zwei Pakete können nicht denselben Slot gleichzeitig belegen
- [ ] LEASE_DENIED löst keinen ESTOP aus (→ CHARTER §SR-09)
- [ ] ESTOP suspendiert betroffene Leases
- [ ] Pfad-Leases funktionieren
- [ ] Mindestens 30 Unit-Tests

### §4.6 Phase 6: Sicherheits-Gate

**Aufgaben:**

- Richter
- Seher
- Circuit-Breaker
- Berufungsprozess
- Gate-Record

**Akzeptanzkriterien:**

- [ ] Richter fail-closed (→ CHARTER §SR-10)
- [ ] Seher ohne Evidenz → invalid veto
- [ ] Seher erzeugt niemals direkt rote Signale (→ CHARTER §SR-13)
- [ ] Circuit-Breaker greift
- [ ] Mindestens 35 Unit-Tests

### §4.7 Phase 7: Ideen-Pipeline

**Aufgaben:**

- Vordenker
- Pre-Filter
- Lotse
- blocked_cache
- Pheromon-Gating
- QUARANTÄNE-Regeln

**Akzeptanzkriterien:**

- [ ] Adaptive Temperatur mit Obergrenze
- [ ] UNKNOWN-Dimensionen werden nicht hart verworfen
- [ ] Signal-Stack wird geprüft
- [ ] QUARANTÄNE erlaubt nur diagnostische Wegmarken
- [ ] Mindestens 35 Unit-Tests

### §4.8 Phase 8: Paket-Bau + Dispatch

**Aufgaben:**

- Quartiermeister
- Dispatcher
- Receiver
- Questor-Interface
- DummyQuestor

**Akzeptanzkriterien:**

- [ ] Korrekte Pakete aus Wegmarke
- [ ] Routing-Graph ist gerichtet
- [ ] Envelope wird gebaut
- [ ] Gate und Lease werden geprüft
- [ ] Keine produktiven nackten Paketübergaben
- [ ] Mindestens 25 Unit-Tests

### §4.9 Phase 9: Kanzler + Königin-Interface

**Aufgaben:**

- Lagebericht
- Weisungsprüfung
- SAFE_MODE
- policy_veto_review
- Audit-Log

**Akzeptanzkriterien:**

- [ ] Menschliche Königin wird niemals überstimmt (→ CHARTER §SR-11)
- [ ] SAFE_MODE funktioniert
- [ ] LLM-Königin-Fallback greift nach Konflikten
- [ ] Review nach definierten Zyklen
- [ ] Mindestens 20 Unit-Tests

### §4.10 Phase 10: Pipeline-Orchestrierung + End-to-End Integration

**Aufgaben:**

- Orchestrator
- Event-Steuerung
- Bounded Queues
- Deadlock-Erkennung
- Alle Integrationstests

**Akzeptanzkriterien:**

- [ ] Alle Pflichttests bestehen
- [ ] Keine Endlosschleifen
- [ ] Keine Deadlocks
- [ ] Keine Blackbox im Gremium (→ CHARTER §SR-07)
- [ ] Mindestens 12 Integrationstests

---

## §4A Atlas-Hybrid-Phasen (A1–A5)

### §4A.1 Übersicht

| Meilenstein | Phasen | Dauer (Schätzung) | Abhängigkeiten |
| --- | --- | --- | --- |
| Atlas-MS-1: Core & Topologie | A1–A2 | 5–7 Tage | MYRMEX Phase 1, Phase 3 |
| Atlas-MS-2: Governance & Frontier | A3–A4 | 4–6 Tage | Atlas-MS-1 |
| Atlas-MS-3: Domänen-Integration | A5 | 3–5 Tage | Atlas-MS-2, Questor MS-3 |

### §4A.2 Phase A1: Atlas-Core & Energiekonten

**Meilenstein:** Atlas-MS-1
**Dauer:** 2–3 Tage
**Abhängigkeiten:** MYRMEX Phase 1 (Verträge), Phase 3 (Atlas-Basis)

**Aufgaben:**

- `EvidenceEvent`-Verarbeitung im Kartographen implementieren
- Energiekonten (`support_energy`, `conflict_energy`, `coverage_energy`, `diagnostic_energy`) führen
- `fracture_score`, `support_confidence`, `uncertainty_score` berechnen
- Zone-Health-Zustandsmaschine (`UNEXPLORED`, `EXPLORED_INCONCLUSIVE`, `HEALTHY`, `DEGRADED`, `CRITICAL`, `LOCKED`) implementieren
- Sicherstellen, dass `OPERATIONAL` keine wissenschaftlichen Signale erzeugt
- Sicherstellen, dass `SAFETY` keine Kristalle/Signale aus Questor erzeugt

**Akzeptanzkriterien:**

- [ ] Leere Zone ist `UNEXPLORED` oder `EXPLORED_INCONCLUSIVE`, niemals automatisch `HEALTHY`
- [ ] ⬜ WEISS erzeugt `coverage_energy`, keine `support_energy`
- [ ] `fracture_score` ist `None`, wenn `evidence_mass < min_evidence_mass`
- [ ] Mindestens 30 Unit-Tests (Suite ATLAS-CTR, ATLAS-INT)

### §4A.3 Phase A2: Topologie & Semantik

**Meilenstein:** Atlas-MS-1
**Dauer:** 3–4 Tage
**Abhängigkeiten:** Phase A1

**Aufgaben:**

- `TypedDimension` und `ZoneGeometry` implementieren (kontinuierlich, kategorisch, ordinal, conditional)
- `AtlasNode` und `AtlasEdge` (Wissensgraph) implementieren
- `ObjectiveFamily` und `MetricDefinition` für Multi-Objective-Forschung implementieren
- Kristallisationslogik (`crystallization_progress`, Bedingungen, Evidence-Class-Transfer) implementieren

**Akzeptanzkriterien:**

- [ ] Kategorische Dimensionen (z.B. Katalysator A/B) erzeugen keine falsche Fracture zwischen Zonen
- [ ] Multi-Objective Trade-offs (z.B. Yield vs. Purity) erzeugen keine automatische Fracture
- [ ] Sandbox-Evidenz (`evidence_class = SANDBOX`) bestätigt keine physischen Kristalle direkt
- [ ] Mindestens 30 Unit-Tests (Suite ATLAS-TOPO, ATLAS-SEM)

### §4A.4 Phase A3: DiagnosticResolution & SafetyConstraint

**Meilenstein:** Atlas-MS-2
**Dauer:** 2–3 Tage
**Abhängigkeiten:** Atlas-MS-1

**Aufgaben:**

- `DiagnosticResolution` implementieren (Outcomes: CONFIRMS, EXPLAINS, RESOLVES, INCONCLUSIVE)
- Auditierte Gewichtsanpassung bei `EXPLAINS_CONTRADICTION` (kein Löschen von Evidenz)
- `SafetyConstraint` implementieren (persistent, kein Decay, manuelle Freigabe)
- `ExclusionConstraint` implementieren (Negativ-Wissen, harte/weiche Grenzen)
- `LOCKED`-Zustand und Governance-Override implementieren

**Akzeptanzkriterien:**

- [ ] `SafetyConstraint` unterliegt keinem automatischen Decay
- [ ] Aktive `SafetyConstraint` setzt `frontier_score = 0`
- [ ] `DiagnosticResolution` mit `EXPLAINS` reduziert `conflict_energy` auditiert
- [ ] Mindestens 20 Unit-Tests (Suite ATLAS-DIAG, ATLAS-SAF)

### §4A.5 Phase A4: FrontierEngine & ExplorationPolicy

**Meilenstein:** Atlas-MS-2
**Dauer:** 2–3 Tage
**Abhängigkeiten:** Atlas-MS-1, A3

**Aufgaben:**

- `FrontierEngine` implementieren (Trigger, harte Filter, Score-Berechnung)
- `FrontierCandidate` mit `FrontierRationale` (strukturierte Begründung) erzeugen
- `ResearchTopic` und Zustandsmaschine (PROPOSED, ACTIVE, SATURATED, BLOCKED, ARCHIVED) implementieren
- `ExplorationPolicy` (Exploitation/Exploration-Balance) implementieren

**Akzeptanzkriterien:**

- [ ] `LOCKED` oder harte `SafetyConstraint` verhindert jede Frontier
- [ ] Quarantäne ohne Diagnose-Budget erzeugt keine normalen Frontiers
- [ ] `FrontierCandidate` enthält zwingend eine maschinenlesbare `rationale`
- [ ] `ResearchTopic` wird deterministisch auf `SATURATED` gesetzt
- [ ] Mindestens 25 Unit-Tests (Suite ATLAS-FRNT, ATLAS-TOP)

### §4A.6 Phase A5: Domänen-Integration & Regression

**Meilenstein:** Atlas-MS-3
**Dauer:** 3–5 Tage
**Abhängigkeiten:** Atlas-MS-2, Questor MS-3 (Data & Results)

**Aufgaben:**

- Integration der Chemie-Domäne (Katalysator-Temperatur-Optimierung)
- Integration der Biologie-Domäne (Zellkultur, Batch-Effekte, Inkubation)
- Integration der Physik-Domäne (Sensor-Kalibrierung, Messunsicherheit, ValidityWindow)
- Integration der ML-Domäne (Hyperparameter, Dataset-Versionen, OOM als Operational)
- Anpassung der bestehenden Regressions-Tests (Suite R) an die neue Atlas-Logik

**Akzeptanzkriterien:**

- [ ] Alle 4 Domänen-Beispiele laufen korrekt mit Atlas-Hybrid
- [ ] Bestehende Regressions-Tests (Suite R) sind migriert und bestehen
- [ ] Keine Endlosschleifen in der Frontier-Engine
- [ ] Mindestens 15 Integrationstests (Suite ATLAS-DOM)

---

## §5 HAL-Phasen (HAL-H0 bis HAL-H6)

### §5.1 Phase HAL-H0: HAL-Vertrag in Hauptstruktur bestätigen

**Aufgaben:**

- HAL-Minimalvertrag mit dieser Datei abgleichen
- Dokumentenhierarchie bestätigen
- Keine sicherheitswidrigen Abweichungen zulassen

**Akzeptanzkriterien:**

- [ ] Strukturversion 1.1.1 bleibt maßgeblich
- [ ] HAL v0.2.0 ist als präzisierte Spezifikation akzeptiert

### §5.2 Phase HAL-H1: Interface und Datenmodelle

**Aufgaben:**

- `hal_interface.py`
- `dummy_hal.py`
- Pydantic-Modelle für alle HAL-Verträge (→ CONTRACTS §3)

**Akzeptanzkriterien:**

- [ ] Alle Modelle sind validierbar
- [ ] Keine wissenschaftlichen Felder
- [ ] Fehlerklassen sind korrekt getrennt (→ CHARTER §SR-08)
- [ ] Mindestens 40 Unit-Tests

### §5.3 Phase HAL-H2: Slot- und Lease-Logik

**Aufgaben:**

- Slot-State-Handling
- Lease-Validierung
- Slot-Mutex
- Timeout-Prüfung
- Idempotenzprüfung

**Akzeptanzkriterien:**

- [ ] Kein Slot wird doppelt belegt
- [ ] Ungültige Leases werden abgelehnt
- [ ] Timeouts werden korrekt gemeldet
- [ ] Duplikate werden blockiert
- [ ] Mindestens 25 Unit-Tests

### §5.4 Phase HAL-H3: Zonen-Mutex und Prozess-Logik

**Aufgaben:**

- Zone-State-Handling
- Zonen-Lock-Anfrage und -Antwort
- Prozess-State-Handling
- Langzeit-Prozess-Modell
- SAFE_HOLD und RESUME
- Stage-Release-Policy

**Akzeptanzkriterien:**

- [ ] Keine Zone wird doppelt belegt
- [ ] Zonen-Locks werden korrekt angefragt und freigegeben
- [ ] Langzeit-Prozesse können gestartet, angehalten und fortgesetzt werden
- [ ] Stage-Release funktioniert
- [ ] Mindestens 30 Unit-Tests

### §5.5 Phase HAL-H4: ESTOP und Hardware-Interlocks

**Aufgaben:**

- ESTOP-Zustandsmaschine
- Hardware-Interlock-Zustandsmaschine
- `report_estop`
- `report_hardware_interlock`
- `get_estop_state`
- `reconcile_slot_state`
- `reconcile_process_state`
- Audit-Events für ESTOP und Interlocks

**Akzeptanzkriterien:**

- [ ] ESTOP stoppt Kommandos
- [ ] ESTOP suspendiert Leases
- [ ] Hardware-Interlock stoppt Kommandos
- [ ] Hardware-Interlock suspendiert Leases und Zonen
- [ ] Kein ESTOP bei Ressourcenkonflikt (→ CHARTER §SR-09)
- [ ] Kein blinder Retry nach Crash (→ CHARTER §SR-10)
- [ ] Mindestens 25 Unit-Tests

### §5.6 Phase HAL-H5: Compute-Modell und Parameter-Schema

**Aufgaben:**

- Compute-Ressourcenmodell
- Compute-spezifische Fehlercodes
- Parameter-Schema-Registry
- Parameter-Schema-Validierung

**Akzeptanzkriterien:**

- [ ] Compute-Ressourcen werden korrekt angefragt
- [ ] Compute-Fehler sind operational (→ CHARTER §SR-08)
- [ ] Parameter-Schemas werden korrekt validiert
- [ ] Mindestens 20 Unit-Tests

### §5.7 Phase HAL-H6: Dummy-HAL und Integration

**Aufgaben:**

- Vollständiger Dummy-HAL
- Alle Fehlermodi
- Integration mit Questor-HAL-Bridge
- Integration mit Resource Governor
- Operational-Audit

**Akzeptanzkriterien:**

- [ ] Dummy kann alle relevanten Szenarien simulieren
- [ ] Keine echte Hardware nötig
- [ ] Suite H kann vorbereitet werden
- [ ] Mindestens 25 Integrationstests

---

## §6 Questor-Phasen (Q0–Q18)

### §6.1 Übersicht

| Meilenstein | Phasen | Dauer (Schätzung) | Abhängigkeiten |
| --- | --- | --- | --- |
| MS-1: Foundation | Q0–Q3 | 7–10 Tage | Keine |
| MS-2: Core Questor | Q4–Q8 | 12–18 Tage | MS-1, HAL-H1 |
| MS-3: Data & Results | Q9–Q10 | 5–7 Tage | MS-2 |
| MS-4: Operational | Q11–Q13 | 4–7 Tage | MS-3 |
| MS-5: Integration | Q14 | 3–5 Tage | MS-4, MYRMEX Phase 8 |
| MS-6: Tests | Q15–Q18 | 13–20 Tage | MS-5 |
| Gesamt | Q0–Q18 | ~44–67 Tage | |

### §6.2 Phase Q0: Verträge und Konfiguration

**Meilenstein:** MS-1 (Foundation)
**Dauer:** 1–2 Tage
**Abhängigkeiten:** MYRMEX Phase 1 (Verträge) muss abgeschlossen sein.

**Aufgaben:**

- Questor-spezifische Enums definieren:
  - `ObjectiveType` (OPTIMIZE, EXPLORE, VALIDATE, DIAGNOSE, SIMULATE_ONLY, CLARIFY)
  - `AutonomyLevel` (STRICT, GUIDED, ADAPTIVE)
  - `SecurityMode` (NORMAL, SANDBOX, DEV_SANDBOX_ONLY, RECOVERY)
  - `GateMode` (NORMAL, FRACTURE_DIAGNOSIS, HIGH_RISK_OVERRIDE, SANDBOX)
  - `DecisionType` (für Trail-Map)
  - `HealthStatus` (HEALTHY, DEGRADED, UNHEALTHY, DEAD)
  - `WatchdogStatus` (OK, WARNING, CRITICAL)
  - `ShutdownPhase` (SIGNAL_RECEIVED, DRAINING, FINALIZING, TERMINATED)
- Questor-Konfiguration definieren:
  - `SanitizationConfig`
  - `HealthMonitorConfig`
  - `ShutdownConfig`
  - `QueueConfig`
- Questor-spezifische Datenverträge definieren:
  - `SanitizationResult`
  - `LLMOutputValidation`
  - `CapabilityDefinition`
  - `CapabilityCheckResult`
  - `Trail`
  - `TrailMap`
  - `HealthFile`
  - `ShutdownResult`
- Pydantic-v2-Modelle für alle Verträge erstellen

**Akzeptanzkriterien:**

- [ ] Alle Enums sind definiert und validierbar
- [ ] Alle Konfigurationsmodelle sind Pydantic-v2-konform
- [ ] Alle Datenverträge sind Pydantic-v2-konform
- [ ] Mindestens 15 Unit-Tests für Verträge
- [ ] Keine Abhängigkeit zu Questor-Logik (nur Datenstrukturen)

### §6.3 Phase Q1: Sanitization

**Meilenstein:** MS-1 (Foundation)
**Dauer:** 2–3 Tage
**Abhängigkeiten:** Q0 (Verträge)

**Aufgaben:**

- `sanitization.py` implementieren:
  - Feld-Whitelist und Blocklist
  - Injection-Pattern-Scan (15 Patterns)
  - Inhaltsbereinigung (Control-Chars, Zero-Width, Längenbegrenzung)
  - XML-Tag-Escaping
  - Prompt-Struktur (System-Prompt, Kontext-Block, Aufgaben-Block)
- `llm_output_validator.py` implementieren:
  - JSON-Parsing
  - Schema-Validierung
  - Safety-Claim-Erkennung
  - Constraint-Prüfung (parameter_bounds, allowed_capabilities)
  - Fallback-Logik
- LLM-Adapter implementieren:
  - Ollama-Integration (abstrahiert)
  - Timeout-Handling
  - Retry-Logik (max. `max_calls`)

**Akzeptanzkriterien:**

- [ ] Alle 18 Sanitization-Unit-Tests bestehen (U-SAN-01 bis U-SAN-18)
- [ ] Injection-Patterns werden korrekt erkannt
- [ ] LLM-Output wird korrekt validiert
- [ ] Fallback funktioniert bei LLM-Ausfall
- [ ] Keine sicherheitskritischen Felder gelangen an das LLM (→ CHARTER §SR-24)
- [ ] Mindestens 95% Code-Coverage

### §6.4 Phase Q2: Capability-Registry

**Meilenstein:** MS-1 (Foundation)
**Dauer:** 2–3 Tage
**Abhängigkeiten:** Q0 (Verträge)

**Aufgaben:**

- `capability_registry.py` implementieren:
  - Registry-Laden aus YAML-Dateien
  - `check_capability()` (3 Ebenen: Registry, HAL, Package)
  - `validate_parameters()` (typsicher, NaN/Infinity)
  - `capabilities_available()` (PolicyEvaluator-Funktion)
  - `get_slots_for_capability()`
- Integritäts-Hash
- Capability-Definitionen erstellen:
  - `data/questor_capabilities/general/`
  - `data/questor_capabilities/chemie/`
  - `data/questor_capabilities/biologie/`
  - `data/questor_capabilities/ml/`
  - `data/questor_capabilities/physik/`
- Korrektur: `QuestorSpec.allowed_capabilities` von `list[Capability]` auf `list[str]` ändern (→ CONTRACTS §1.2)

**Akzeptanzkriterien:**

- [ ] Alle 22 Capability-Registry-Unit-Tests bestehen (U-CAP-01 bis U-CAP-22)
- [ ] Registry lädt korrekt aus YAML-Dateien
- [ ] `check_capability()` prüft alle 3 Ebenen
- [ ] `validate_parameters()` erkennt NaN, Infinity, Typfehler
- [ ] `capabilities_available()` funktioniert korrekt
- [ ] Mindestens 4 Capability-Definitionen pro Domäne
- [ ] Mindestens 90% Code-Coverage

### §6.5 Phase Q3: Security-Mode

**Meilenstein:** MS-1 (Foundation)
**Dauer:** 1–2 Tage
**Abhängigkeiten:** Q0 (Verträge), Q2 (Capability-Registry)

**Aufgaben:**

- `security_mode.py` implementieren:
  - `get_effective_security_mode()` (Min-Rule)
  - `validate_package_security_mode()` (Envelope-Check)
  - `filter_templates_by_security_mode()`
  - `policy_check_security_mode()` (PolicyEvaluator-Integration)
- Security-Mode-Matrix implementieren:
  - NORMAL, SANDBOX, DEV_SANDBOX_ONLY, RECOVERY
  - Physische Actuation vs. Compute
  - RECOVERY-Einschränkungen

**Akzeptanzkriterien:**

- [ ] Alle 11 Security-Mode-Unit-Tests bestehen (U-SM-01 bis U-SM-11)
- [ ] Min-Rule funktioniert korrekt (→ CHARTER §SR-35)
- [ ] RECOVERY erlaubt nur `reconcile_*` und `read_*` (→ CHARTER §SR-37)
- [ ] Physische Actuation in SANDBOX wird abgelehnt
- [ ] `security_mode` fehlt → `PACKAGE_INVALID` (→ CHARTER §SR-36)
- [ ] Mindestens 95% Code-Coverage

### §6.6 Phase Q4: Facade und Validator

**Meilenstein:** MS-2 (Core Questor)
**Dauer:** 2–3 Tage
**Abhängigkeiten:** Q0 (Verträge), Q1 (Sanitization), Q2 (Capability-Registry), Q3 (Security-Mode)

**Aufgaben:**

- `facade.py` implementieren:
  - Queue-Lesen aus `pending/`
  - Ältestes-Paket-zuerst-Strategie
  - Envelope-Erkennung (vs. nacktes ResearchPackage)
  - `DIRECT_PACKAGE_FORBIDDEN`
- `validator.py` implementieren:
  - Envelope-Struktur prüfen
  - `gate_record_ref` prüfen (→ CHARTER §SR-53)
  - `idempotency_key` kanonisch prüfen (→ CONTRACTS §8.1)
  - `attempt_id` Bereich prüfen (0–999999)
  - `routing_graph` Pflichtfelder prüfen
  - `questor_spec` validieren
  - `security_mode` gegen Gate prüfen

**Akzeptanzkriterien:**

- [ ] Facade liest korrekt aus `pending/`
- [ ] Validator erkennt alle ungültigen Envelopes
- [ ] `DIRECT_PACKAGE_FORBIDDEN` wird korrekt ausgelöst
- [ ] `PACKAGE_INVALID` wird korrekt ausgelöst
- [ ] Idempotenz-Schutz funktioniert (→ CHARTER §SR-54)
- [ ] Mindestens 20 Unit-Tests
- [ ] Mindestens 85% Code-Coverage

### §6.7 Phase Q5: QuestCompass

**Meilenstein:** MS-2 (Core Questor)
**Dauer:** 3–5 Tage
**Abhängigkeiten:** Q1 (Sanitization), Q2 (Capability-Registry), Q4 (Facade)

**Aufgaben:**

- `objective_parser.py` implementieren:
  - Stufe 1: Deterministisch (objective_type aus QuestorSpec)
  - Stufe 2: Keyword-Matching
  - Stufe 2.5: Objective-Vervollständigung (LLM, optional)
  - Stufe 3: LLM-Advisor (nur falls unklar)
  - Clarity-Score-Berechnung
- `compass.py` implementieren:
  - Loop Selection (Filter, Ranking, Kandidatenfenster)
  - Parameter-Füllung
  - Evaluation (pro objective_type)
  - Decision Engine (8 Regeln)
  - LLM-Advisor-Integration (3 Situationen)
  - FRACTURE_DIAGNOSIS-Sonderregel
- `advisors/llm_advisor.py` implementieren:
  - Ollama-Integration
  - Prompt-Aufbau (mit Sanitization)
  - Output-Validierung
  - Fallback-Logik

**Akzeptanzkriterien:**

- [ ] Alle 15 QuestCompass-Komponententests bestehen (C-QC-01 bis C-QC-15)
- [ ] Objective Analysis funktioniert in allen 3 Stufen
- [ ] Loop Selection funktioniert für STRICT, GUIDED, ADAPTIVE
- [ ] Evaluation funktioniert für alle 6 objective_types
- [ ] Decision Engine wendet alle 8 Regeln korrekt an
- [ ] LLM-Advice wird korrekt angenommen oder abgelehnt (→ CHARTER §SR-13)
- [ ] FRACTURE_DIAGNOSIS erzwingt STRICT
- [ ] Mindestens 85% Code-Coverage

### §6.8 Phase Q6: Loop-Architektur

**Meilenstein:** MS-2 (Core Questor)
**Dauer:** 2–3 Tage
**Abhängigkeiten:** Q2 (Capability-Registry), Q5 (QuestCompass)

**Aufgaben:**

- `loop_registry.py` implementieren:
  - Template-Laden aus YAML-Dateien
  - Template-Validierung
  - Template-Filterung (objective_type, capabilities, budget)
  - Template-Versionierung
- Loop-Template-Erstellung:
  - `data/questor_templates/chemie/`
  - `data/questor_templates/biologie/`
  - `data/questor_templates/ml/`
  - `data/questor_templates/physik/`
- Loop-Instance-Erstellung und -Ausführung:
  - LoopInstance aus LoopTemplate + Parameter
  - Step-Ausführung (sequentiell)
  - Branch-Condition-Handling
  - Terminierung

**Akzeptanzkriterien:**

- [ ] LoopRegistry lädt korrekt aus YAML-Dateien
- [ ] Template-Validierung erkennt ungültige Templates
- [ ] Loop-Instance wird korrekt erstellt
- [ ] Step-Ausführung funktioniert sequentiell
- [ ] Branch-Conditions werden korrekt ausgewertet
- [ ] Terminierung funktioniert korrekt
- [ ] Mindestens 4 Templates pro Domäne
- [ ] Mindestens 15 Unit-Tests
- [ ] Mindestens 85% Code-Coverage

### §6.9 Phase Q7: PolicyEvaluator und SafetyMonitor

**Meilenstein:** MS-2 (Core Questor)
**Dauer:** 2–3 Tage
**Abhängigkeiten:** Q2 (Capability-Registry), Q3 (Security-Mode), Q5 (QuestCompass), Q6 (Loop)

**Aufgaben:**

- `policy_evaluator.py` implementieren:
  - 8 Prüfungen (Safety, Routing, Capability, Budget, Security-Mode, Occam, Dimension, GO)
  - VETO / GO-Entscheidung
  - `capabilities_available()` (aus Q2)
  - `policy_check_security_mode()` (aus Q3)
- `safety_monitor.py` implementieren:
  - ESTOP-Überwachung
  - Interlock-Überwachung
  - Timeout-Überwachung
  - Lease-Expiry-Überwachung
  - Sicherheitsabbruch einleiten

**Akzeptanzkriterien:**

- [ ] Alle 9 PolicyEvaluator-Komponententests bestehen (C-PE-01 bis C-PE-09)
- [ ] Alle 8 Prüfungen funktionieren korrekt
- [ ] VETO wird korrekt ausgelöst
- [ ] ESTOP wird korrekt erkannt (→ CHARTER §SR-09)
- [ ] Interlock wird korrekt erkannt
- [ ] Timeout wird korrekt erkannt
- [ ] Mindestens 95% Code-Coverage

### §6.10 Phase Q8: HAL-Bridge

**Meilenstein:** MS-2 (Core Questor)
**Dauer:** 3–4 Tage
**Abhängigkeiten:** Q2 (Capability-Registry), Q3 (Security-Mode), Q7 (PolicyEvaluator), HAL Phase HAL-H1

**Aufgaben:**

- `hal_bridge.py` implementieren:
  - LoopStep → HALCommand übersetzen
  - LoopStep → ProcessCommand übersetzen
  - HALCommandResult verarbeiten
  - ProcessResult verarbeiten
  - Idempotenz-Key erzeugen (→ CONTRACTS §8.2)
  - Kosten aktualisieren
  - Parameter-Validierung (aus Q2)
  - Security-Mode-Prüfung (aus Q3)
- HAL-Adapter implementieren:
  - `hal_interface.py` (Interface)
  - `dummy_hal.py` (für Tests)
- Prozess-Lebenszyklus implementieren:
  - START, MONITOR, RESUME, HOLD, ABORT, RELEASE_STAGE
  - SAFE_HOLD, WAITING_FOR_RELEASE
  - Resume-Token

**Akzeptanzkriterien:**

- [ ] Alle 10 HAL-Bridge-Komponententests bestehen (C-HB-01 bis C-HB-10)
- [ ] LoopStep wird korrekt in HALCommand übersetzt
- [ ] HALCommandResult wird korrekt verarbeitet
- [ ] ESTOP → SAFETY_ABORT (→ CHARTER §SR-09)
- [ ] LEASE_DENIED → OPERATIONAL_ABORT (→ CHARTER §SR-09)
- [ ] DUPLICATE_BLOCKED → SUCCESS
- [ ] Parameter-Validierung funktioniert
- [ ] Security-Mode-Prüfung funktioniert
- [ ] SAFE_HOLD und RESUME funktionieren
- [ ] Mindestens 90% Code-Coverage

### §6.11 Phase Q9: ExpeditionLedger und WAL

**Meilenstein:** MS-3 (Data & Results)
**Dauer:** 3–4 Tage
**Abhängigkeiten:** Q5 (QuestCompass), Q8 (HAL-Bridge)

**Aufgaben:**

- `ledger.py` implementieren:
  - Ledger-Struktur
  - Genesis-Hash (C15)
  - Hash-Chain
  - NaN/Infinity-Prüfung (C18) (→ CHARTER §SR-14)
  - APPEND-ONLY
  - READ-ONLY nach Abschluss (→ CHARTER §SR-17)
- `wal.py` implementieren:
  - WAL-Eintrag schreiben (vor Ausführung)
  - WAL-Eintrag aktualisieren (nach Ausführung)
  - WAL-Flush
  - WAL-Lebenszyklus (erstellen, schreiben, bereinigen)
- `recovery.py` implementieren:
  - WAL lesen
  - Integrität prüfen
  - Letzten Checkpoint finden
  - Zustand rekonstruieren
  - RECOVERY_UNSAFE

**Akzeptanzkriterien:**

- [ ] Genesis-Hash ist deterministisch und reproduzierbar
- [ ] Hash-Chain ist korrekt
- [ ] NaN/Infinity wird erkannt und führt zu Fail-Closed (→ CHARTER §SR-14)
- [ ] WAL wird korrekt geschrieben und flush'd
- [ ] Recovery funktioniert korrekt (→ CHARTER §SR-16)
- [ ] RECOVERY_UNSAFE wird korrekt ausgelöst
- [ ] Mindestens 25 Unit-Tests
- [ ] Mindestens 90% Code-Coverage

### §6.12 Phase Q10: Result-Builder

**Meilenstein:** MS-3 (Data & Results)
**Dauer:** 2–3 Tage
**Abhängigkeiten:** Q9 (Ledger), Q5 (QuestCompass)

**Aufgaben:**

- `result_builder.py` implementieren:
  - Status bestimmen
  - Sicherheitsregeln anwenden
  - Ergebnis-Daten sammeln
  - Kristallkandidaten erzeugen
  - Signale aus Kristallkandidaten erzeugen
  - Guardian-Validierung
  - Early-Abort-Ergebnis bauen
- `blackbox_archiver.py` implementieren:
  - Blackbox schreiben
  - Retention-Class bestimmen
  - Limits prüfen
  - Rotation
- `sequence.py` implementieren:
  - Sequence-Nummer atomar persistieren
  - Datei-Lock
  - `questor_instance_id` erzeugen

**Akzeptanzkriterien:**

- [ ] Alle 10 Result-Builder-Komponententests bestehen (C-RB-01 bis C-RB-10)
- [ ] Ergebnis wird korrekt gebaut
- [ ] Kristallkandidaten werden korrekt erzeugt (→ CHARTER §SR-18)
- [ ] Signale werden korrekt erzeugt
- [ ] Bei SAFETY: Kristalle und Signale leer (→ CHARTER §SR-19)
- [ ] `vollstaendig_flag` ist immer true (→ CHARTER §SR-20)
- [ ] Guardian-Validierung funktioniert
- [ ] Early-Abort-Ergebnis wird korrekt gebaut
- [ ] Blackbox wird korrekt geschrieben (→ CHARTER §SR-07)
- [ ] Sequence-Nummer ist atomar
- [ ] Mindestens 90% Code-Coverage

### §6.13 Phase Q11: Shutdown

**Meilenstein:** MS-4 (Operational)
**Dauer:** 1–2 Tage
**Abhängigkeiten:** Q9 (WAL), Q10 (Result-Builder)

**Aufgaben:**

- `shutdown.py` implementieren:
  - Signal-Handler (SIGTERM, SIGINT)
  - Shutdown-Flag-Datei prüfen
  - Graceful-Shutdown-Prozedur
  - Force-Shutdown-Prozedur
  - HAL-Kommando abwarten
  - Prozess in SAFE_HOLD versetzen
  - WAL flush'd (→ CHARTER §SR-42)
  - Ergebnis bauen
  - Queue aktualisieren
  - Leases freigeben
  - Blackbox schreiben

**Akzeptanzkriterien:**

- [ ] Alle 13 Shutdown-Unit-Tests bestehen (U-SD-01 bis U-SD-13)
- [ ] SIGTERM wird korrekt behandelt
- [ ] Graceful-Shutdown funktioniert
- [ ] Force-Shutdown funktioniert
- [ ] WAL wird flush'd (→ CHARTER §SR-42)
- [ ] Ergebnis wird gebaut (`GRACEFUL_SHUTDOWN`)
- [ ] ESTOP hat Vorrang vor Shutdown (→ CHARTER §SR-43)
- [ ] Shutdown ist immer OPERATIONAL (→ CHARTER §SR-44)
- [ ] Mindestens 90% Code-Coverage

### §6.14 Phase Q12: Health-Monitoring

**Meilenstein:** MS-4 (Operational)
**Dauer:** 2–3 Tage
**Abhängigkeiten:** Q0 (Verträge)

**Aufgaben:**

- `health_monitor.py` implementieren:
  - Heartbeat-Writer (Thread)
  - Internal-Watchdog (Thread)
  - Externer Monitor (Pipeline-Orchestrator)
  - `determine_health_status()`
  - Alert-Cooldown
  - Recovery-Aktionen
- `health.json` schreiben:
  - Atomares Schreiben (temp + rename)
  - Alle Felder aus `HealthFile`

**Akzeptanzkriterien:**

- [ ] Alle 15 Health-Monitoring-Unit-Tests bestehen (U-HM-01 bis U-HM-15)
- [ ] Heartbeat wird korrekt geschrieben
- [ ] Watchdog erkennt Zustandsdauer-Überschreitung
- [ ] Watchdog erkennt Speicherverbrauch
- [ ] Watchdog erkennt CPU-Auslastung
- [ ] Watchdog erkennt fehlenden Fortschritt
- [ ] Externer Monitor liest korrekt
- [ ] Alert-Cooldown funktioniert
- [ ] Health-Monitoring ist immer OPERATIONAL (→ CHARTER §SR-45)
- [ ] Mindestens 85% Code-Coverage

### §6.15 Phase Q13: Trail-Map

**Meilenstein:** MS-4 (Operational)
**Dauer:** 1–2 Tage
**Abhängigkeiten:** Q0 (Verträge), Q1 (Sanitization), Q2 (Capability-Registry)

**Aufgaben:**

- `trail_map.py` implementieren:
  - Trail-Erzeugung
  - TrailMap-Verwaltung
  - TrailMapSummary
  - Trail-Map in Blackbox speichern
  - Trail-Map-Hash im Ledger protokollieren
- `InitialTrailPolicy` definieren:
  - `create_trails: bool`
  - `require_evidence: bool`
  - `trail_detail_level: MINIMAL | STANDARD | FULL`

**Akzeptanzkriterien:**

- [ ] Alle 11 Trail-Map-Unit-Tests bestehen (U-TRAIL-01 bis U-TRAIL-11)
- [ ] Trails werden korrekt erstellt
- [ ] Trail-Map wird korrekt finalisiert
- [ ] TrailMapSummary wird korrekt erstellt
- [ ] Trail-Map wird in Blackbox gespeichert (→ CHARTER §SR-50)
- [ ] Trail-Map-Hash wird im Ledger protokolliert
- [ ] `create_trails = false` → keine Trails
- [ ] Trail-Map ist OPERATIONAL (→ CHARTER §SR-49)
- [ ] Mindestens 80% Code-Coverage

### §6.16 Phase Q14: Queue-Integration

**Meilenstein:** MS-5 (Integration)
**Dauer:** 3–5 Tage
**Abhängigkeiten:** Q4 (Facade), Q10 (Result-Builder), Q11 (Shutdown), MYRMEX Phase 8

**Aufgaben:**

- Queue-Integration implementieren:
  - Dispatcher → `pending/` schreiben
  - Questor → `processing/` → `completed/` oder `failed/`
  - Receiver → `completed/` und `failed/` lesen
  - Pipeline-Orchestrator → `registry.json` lesen
  - Archivar → `completed/` und `failed/` bereinigen
  - Delete-Requests verarbeiten
- `registry.json` implementieren:
  - Datei-Lock (→ CHARTER §SR-56)
  - Status-Tracking
  - Atomare Updates (→ CHARTER §SR-55)
- `health.json` in Queue integrieren

**Akzeptanzkriterien:**

- [ ] Alle 14 Queue-Integration-Unit-Tests bestehen (U-QI-01 bis U-QI-14)
- [ ] Dispatcher schreibt korrekt in `pending/`
- [ ] Questor verschiebt korrekt nach `processing/`
- [ ] Questor schreibt korrekt nach `completed/` oder `failed/`
- [ ] Receiver liest korrekt
- [ ] Pipeline-Orchestrator liest `registry.json`
- [ ] Archivar bereinigt korrekt
- [ ] Delete-Requests werden korrekt verarbeitet
- [ ] Registry-Lock funktioniert (→ CHARTER §SR-56)
- [ ] Idempotenz-Schutz funktioniert (→ CHARTER §SR-54)
- [ ] Kein Löschen von `processing/` (→ CHARTER §SR-57)
- [ ] Mindestens 85% Code-Coverage

### §6.17 Phase Q15: Unit-Tests

**Meilenstein:** MS-6 (Tests)
**Dauer:** 5–7 Tage
**Abhängigkeiten:** Q0–Q14 (alle Module)

**Aufgaben:**

- Alle Unit-Tests implementieren (~252 Tests):
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
- Test-Fixtures erstellen
- Mocks erstellen (mock_hal, mock_llm, mock_resource_governor, mock_filesystem)

**Akzeptanzkriterien:**

- [ ] Alle ~252 Unit-Tests bestehen
- [ ] Coverage ≥ 88% gesamt
- [ ] Coverage ≥ 95% für sicherheitskritische Module
- [ ] Alle Fail-Closed-Punkte sind getestet (→ CHARTER §SR-10)
- [ ] Alle Edge Cases sind getestet

### §6.18 Phase Q16: Komponententests

**Meilenstein:** MS-6 (Tests)
**Dauer:** 3–5 Tage
**Abhängigkeiten:** Q15 (Unit-Tests)

**Aufgaben:**

- Alle Komponententests implementieren (~44 Tests):
  - QuestCompass (15 Tests)
  - PolicyEvaluator (9 Tests)
  - HAL-Bridge (10 Tests)
  - Result-Builder (10 Tests)
- Test-Szenarien erstellen:
  - Chemie-Kinetik (Happy Path)
  - Biologie-Inkubation (Langzeit-Prozess)
  - ML-Training (Compute)
  - Physik-Messung (Sensor)

**Akzeptanzkriterien:**

- [ ] Alle ~44 Komponententests bestehen
- [ ] QuestCompass-Zyklus funktioniert end-to-end
- [ ] PolicyEvaluator prüft alle 8 Regeln
- [ ] HAL-Bridge übersetzt korrekt
- [ ] Result-Builder baut korrekte Ergebnisse

### §6.19 Phase Q17: Integrationstests

**Meilenstein:** MS-6 (Tests)
**Dauer:** 3–5 Tage
**Abhängigkeiten:** Q16 (Komponententests), MYRMEX Phase 8, HAL Phase HAL-H6

**Aufgaben:**

- Suite I (18 Tests) durchführen
- Suite S (5 Tests) durchführen
- Suite R (12 Tests) durchführen
- Suite Z (8 Tests) durchführen
- Suite H (24 Tests) durchführen
- Suite N (7 Tests) durchführen

**Akzeptanzkriterien:**

- [ ] Alle 74 bestehenden Integrationstests bestehen
- [ ] Suite I: 18/18 BESTANDEN
- [ ] Suite S: 5/5 BESTANDEN
- [ ] Suite R: 12/12 BESTANDEN
- [ ] Suite Z: 8/8 BESTANDEN
- [ ] Suite H: 24/24 BESTANDEN
- [ ] Suite N: 7/7 BESTANDEN

### §6.20 Phase Q18: Sicherheits- und Performance-Tests

**Meilenstein:** MS-6 (Tests)
**Dauer:** 2–3 Tage
**Abhängigkeiten:** Q17 (Integrationstests)

**Aufgaben:**

- Sicherheitstests implementieren (~30 Tests):
  - Prompt-Injection (10 Tests)
  - Capability-Bypass (5 Tests)
  - Security-Mode-Eskalation (5 Tests)
  - WAL-Manipulation (3 Tests)
  - Queue-Manipulation (5 Tests)
  - LLM-Output-Manipulation (2 Tests)
- Performance-Tests implementieren (~10 Tests)
- Stress-Tests implementieren (~11 Tests)

**Akzeptanzkriterien:**

- [ ] Alle ~30 Sicherheitstests bestehen
- [ ] Alle ~10 Performance-Tests bestehen
- [ ] Alle ~11 Stress-Tests bestehen
- [ ] Keine Sicherheitslücken gefunden
- [ ] Performance innerhalb der Limits

---

## §7 Meilensteine und Abhängigkeiten

### §7.1 Questor-Meilensteine

| Meilenstein | Phasen | Dauer | Abhängigkeiten |
| --- | --- | --- | --- |
| MS-1: Foundation | Q0–Q3 | 7–10 Tage | Keine |
| MS-2: Core Questor | Q4–Q8 | 12–18 Tage | MS-1, HAL-H1 |
| MS-3: Data & Results | Q9–Q10 | 5–7 Tage | MS-2 |
| MS-4: Operational | Q11–Q13 | 4–7 Tage | MS-3 |
| MS-5: Integration | Q14 | 3–5 Tage | MS-4, MYRMEX Phase 8 |
| MS-6: Tests | Q15–Q18 | 13–20 Tage | MS-5 |

### §7.1b Atlas-Hybrid-Meilensteine

| Meilenstein | Phasen | Dauer | Abhängigkeiten |
| --- | --- | --- | --- |
| Atlas-MS-1: Core & Topologie | A1–A2 | 5–7 Tage | MYRMEX Phase 1, Phase 3 |
| Atlas-MS-2: Governance & Frontier | A3–A4 | 4–6 Tage | Atlas-MS-1 |
| Atlas-MS-3: Domänen-Integration | A5 | 3–5 Tage | Atlas-MS-2, Questor MS-3 |

### §7.2 Externe Abhängigkeiten

| Questor-Meilenstein | MYRMEX-Phase | HAL-Phase | Bedingung |
| --- | --- | --- | --- |
| MS-1 (Foundation) | Phase 1 (Verträge) | — | MYRMEX Phase 1 muss fertig sein |
| MS-2 (Core Questor) | Phase 5 (Resource Governor) | HAL-H1 (Interface) | HAL-H1 muss fertig sein |
| MS-3 (Data & Results) | Phase 2 (Archivar) | — | MYRMEX Phase 2 muss fertig sein |
| MS-4 (Operational) | — | — | Keine externe Abhängigkeit |
| MS-5 (Integration) | Phase 8 (Dispatcher, Receiver) | HAL-H6 (Dummy) | MYRMEX Phase 8 muss fertig sein |
| MS-6 (Tests) | Phase 10 (E2E) | HAL-H6 (Dummy) | Alle müssen fertig sein |

| Atlas-Meilenstein | MYRMEX-Phase | Questor-Phase | Bedingung |
| --- | --- | --- | --- |
| Atlas-MS-1 | Phase 1 (Verträge), Phase 3 (Atlas-Basis) | — | MYRMEX Phase 3 muss fertig sein |
| Atlas-MS-3 | — | MS-3 (Data & Results) | Questor muss Kristallkandidaten mit Atlas-Hybrid-Feldern liefern |

### §7.3 Abhängigkeitsgraph

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ABHÄNGIGKEITSGRAPH                           │
│                                                                     │
│  EBENE 0 (keine Abhängigkeiten):                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ Sanitization │  │ Capability-  │  │ Security-    │             │
│  │  (Q1)        │  │ Registry     │  │ Mode         │             │
│  │              │  │  (Q2)        │  │  (Q3)        │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│  ┌──────────────┐  ┌──────────────┐                                │
│  │ Health-      │  │ Trail-Map    │                                │
│  │ Monitoring   │  │  (Q13)       │                                │
│  │  (Q12)       │  │              │                                │
│  └──────────────┘  └──────────────┘                                │
│                                                                     │
│  EBENE 1 (abhängig von Ebene 0):                                   │
│  ┌──────────────┐  ┌──────────────┐                                │
│  │  Facade +    │  │  Loop-       │                                │
│  │  Validator   │  │  Registry    │                                │
│  │  (Q4)        │  │  (Q6)        │                                │
│  └──────┬───────┘  └──────┬───────┘                                │
│         │                  │                                        │
│         ▼                  ▼                                        │
│  ┌──────────────────────────────────┐                              │
│  │         QuestCompass             │                              │
│  │  (Q5)                            │                              │
│  └──────────────┬───────────────────┘                              │
│                 │                                                   │
│  EBENE 2 (abhängig von Ebene 1):                                   │
│                 ▼                                                   │
│  ┌──────────────────────────────────┐                              │
│  │     PolicyEvaluator +            │                              │
│  │     SafetyMonitor (Q7)           │                              │
│  └──────────────┬───────────────────┘                              │
│                 │                                                   │
│                 ▼                                                   │
│  ┌──────────────────────────────────┐                              │
│  │         HAL-Bridge (Q8)          │                              │
│  └──────────────┬───────────────────┘                              │
│                 │                                                   │
│  EBENE 3 (abhängig von Ebene 2):                                   │
│                 ▼                                                   │
│  ┌──────────────────────────────────┐                              │
│  │   ExpeditionLedger + WAL (Q9)    │                              │
│  └──────────────┬───────────────────┘                              │
│                 │                                                   │
│                 ▼                                                   │
│  ┌──────────────────────────────────┐                              │
│  │        Result-Builder (Q10)      │                              │
│  └──────────────┬───────────────────┘                              │
│                 │                                                   │
│  EBENE 4 (abhängig von Ebene 3):                                   │
│                 ▼                                                   │
│  ┌──────────────────────────────────┐                              │
│  │         Shutdown (Q11)           │                              │
│  └──────────────┬───────────────────┘                              │
│                 │                                                   │
│  EBENE 5 (abhängig von Ebene 4):                                   │
│                 ▼                                                   │
│  ┌──────────────────────────────────┐                              │
│  │      Queue-Integration (Q14)     │                              │
│  └──────────────┬───────────────────┘                              │
│                 │                                                   │
│  EBENE 6 (abhängig von Ebene 5):                                   │
│                 ▼                                                   │
│  ┌──────────────────────────────────┐                              │
│  │         TESTS (Q15–Q18)          │                              │
│  └──────────────────────────────────┘                              │
│                                                                     │
│  ATLAS-HYBRID (parallel zu Ebene 3–5):                             │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │  A1 → A2 → A3 → A4 → A5                                  │      │
│  │  (benötigt MYRMEX Phase 1, 3; A5 benötigt Questor MS-3)  │      │
│  └──────────────────────────────────────────────────────────┘      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## §8 Kritischer Pfad

### §8.1 Questor-kritischer Pfad

Der kritische Pfad ist:

```
Q0 → Q1 → Q5 → Q7 → Q8 → Q9 → Q10 → Q11 → Q14 → Q15 → Q16 → Q17 → Q18
```

Geschätzte Dauer des kritischen Pfads: ~44–55 Tage (1 Entwickler)

### §8.2 Parallelisierung

Die folgenden Phasen können parallelisiert werden:

| Phasen | Können parallel laufen |
| --- | --- |
| Q1, Q2, Q3 | Ja (alle hängen nur von Q0 ab) |
| Q12, Q13 | Ja (beide hängen nur von Q0 ab) |
| Q15, Q16 | Ja (beide hängen von Q14 ab) |
| A1–A4, Q9–Q13 | Ja (Atlas parallel zu Questor MS-3/MS-4) |

Mit 2 Entwicklern: ~30–40 Tage
Mit 3 Entwicklern: ~22–30 Tage

### §8.3 Atlas-Hybrid-Pfad

Der Atlas-Hybrid-Pfad ist:

```
MYRMEX Phase 3 → A1 → A2 → A3 → A4 → A5 → MYRMEX Phase 10 (E2E)
```

**Parallelisierung:**

Atlas A1-A4 kann parallel zu Questor Q9-Q13 (MS-3 und MS-4) entwickelt werden.
Atlas A5 (Domänen-Integration) erfordert Questor MS-3.

---

## §9 Risikobewertung

### §9.1 Risiko-Matrix

| # | Risiko | Wahrscheinlichkeit | Auswirkung | Mitigation |
| --- | --- | --- | --- | --- |
| R1 | LLM-Backend (Ollama) ist nicht verfügbar oder instabil | Mittel | Hoch | Mock-LLM für Tests. Fallback auf deterministischen Pfad. |
| R2 | HAL-Implementierung ist nicht fertig, wenn Questor HAL-Bridge braucht | Mittel | Hoch | Dummy-HAL für Tests. HAL-Bridge gegen Interface entwickeln. |
| R3 | MYRMEX-Implementierung ist nicht fertig, wenn Questor Queue-Integration braucht | Mittel | Hoch | Queue-Integration gegen Dateisystem entwickeln. MYRMEX-Integration nachgelagert. |
| R4 | Prompt-Injection-Angriffe werden nicht erkannt | Niedrig | KRITISCH | Mehrschichtige Verteidigung (Whitelist + Pattern-Scan + Output-Validierung). Regelmäßige Pattern-Updates. |
| R5 | Langzeit-Prozesse (72h) sind schwer zu testen | Hoch | Mittel | Mock-HAL mit beschleunigter Zeit. SAFE_HOLD und RESUME testen. |
| R6 | Die Queue wird bei vielen Paketen langsam | Mittel | Mittel | Performance-Tests. Queue-Limits. Bereinigung. |
| R7 | Der WAL wird zu groß | Niedrig | Mittel | WAL-Bereinigung nach DONE. WAL-Größe überwachen. |
| R8 | Die Trail-Map wird zu groß | Niedrig | Niedrig | Trail-Map-Limits. Blackbox-Limits (100 MB). |
| R9 | Die Implementierung dauert länger als geplant | Hoch | Mittel | Puffer einplanen. Kritische Pfade identifizieren. |
| R10 | Die Coverage-Ziele werden nicht erreicht | Mittel | Mittel | Coverage-Gates in CI/CD. Regelmäßige Coverage-Reviews. |
| R11 | Atlas-Hybrid-Energiekonten erzeugen unerwartete Zone-Health-Übergänge | Mittel | Mittel | Umfassende Unit-Tests für alle Zustandsübergänge. Deterministische Schwellwerte. |
| R12 | FrontierEngine erzeugt Endlosschleifen bei komplexer Topologie | Niedrig | Hoch | Max-Iteration-Limit. Deterministische Terminierung. Suite ATLAS-FRNT. |

---

## §10 Zeitplanung

### §10.1 Gantt-Diagramm (vereinfacht)

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
  Atlas:                               ████████████████████████
    A1-A2:                             ████████
    A3-A4:                                     ████████
    A5:                                                ██████
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

### §10.2 Empfohlene Reihenfolge

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
    MYRMEX Phase 3 (Atlas + Kartograph)
    Atlas A1 (Core & Energiekonten)
    Atlas A2 (Topologie & Semantik)
    Questor Q6 (Loop)
    Questor Q7 (PolicyEvaluator)
    Questor Q8 (HAL-Bridge)

WOCHE 7-8:
    HAL Phase HAL-H4 (ESTOP/Interlock)
    HAL Phase HAL-H5 (Compute/Schema)
    Atlas A3 (DiagnosticResolution & SafetyConstraint)
    Atlas A4 (FrontierEngine & ExplorationPolicy)
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

WOCHE 10-11:
    Atlas A5 (Domänen-Integration & Regression)

WOCHE 11-14:
    MYRMEX Phase 10 (E2E)
    Questor Q15 (Unit-Tests)
    Questor Q16 (Komponententests)
    Questor Q17 (Integrationstests)
    Questor Q18 (Sicherheits-/Performance-Tests)
```

---

## §11 Test-Gates pro Phase

### §11.1 Test-Gates

| Gate | Bedingung |
| --- | --- |
| GATE-1 | Alle Unit-Tests bestehen |
| GATE-2 | Alle Komponententests bestehen |
| GATE-3 | Alle Sicherheitstests bestehen |
| GATE-4 | Coverage ≥ 88% |
| GATE-5 | Alle Integrationstests bestehen (Suite I) |
| GATE-6 | Alle Szenario-Tests bestehen (Suite S) |
| GATE-7 | Performance-Tests innerhalb der Limits |
| GATE-8 | Keine offenen Blocker |
| GATE-ATLAS | Alle Atlas-Unit- und Integrationstests bestehen (Suite ATLAS) |

### §11.2 Teststrategie pro Phase

| Phase | Test-Typ | Anzahl | Coverage-Ziel |
| --- | --- | --- | --- |
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
| A1 | Unit-Tests (Atlas-Core) | 30 | 90% |
| A2 | Unit-Tests (Topologie) | 30 | 90% |
| A3 | Unit-Tests (Governance) | 20 | 95% |
| A4 | Unit-Tests (Frontier) | 25 | 85% |
| A5 | Integrationstests (Domänen) | 15 | — |
| Q15 | Alle Unit-Tests (Wiederholung) | ~252 | ≥ 88% |
| Q16 | Alle Komponententests | ~44 | — |
| Q17 | Alle Integrationstests (Suite I, S, R, Z, H, N) | 74 | — |
| Q18 | Sicherheits-/Performance-/Stress-Tests | ~51 | — |
| Gesamt | | ~541 | ≥ 88% |

---

## §12 Akzeptanzkriterien für das Gesamtsystem

Nach Abschluss aller Phasen muss gelten:

| # | Kriterium | CHARTER-Referenz |
| --- | --- | --- |
| 1 | Alle ~421 Tests bestehen | — |
| 2 | Coverage ≥ 88% gesamt | — |
| 3 | Coverage ≥ 95% für sicherheitskritische Module | — |
| 4 | Alle Fail-Closed-Punkte sind getestet | CHARTER §SR-10 |
| 5 | Keine Sicherheitslücken gefunden | — |
| 6 | Performance innerhalb der Limits | — |
| 7 | Alle 74 bestehenden Integrationstests bestehen | — |
| 8 | Questor schreibt nicht in Atlas/Archiv | CHARTER §SR-04 |
| 9 | Questor setzt ESTOP nicht zurück | CHARTER §SR-05 |
| 10 | Questor vergibt keine Leases | CHARTER §SR-06 |
| 11 | Blackbox bleibt lokal | CHARTER §SR-07 |
| 12 | Operational ≠ Scientific | CHARTER §SR-08 |
| 13 | ESTOP ≠ LEASE_DENIED | CHARTER §SR-09 |
| 14 | LLM ist nur Advisor | CHARTER §SR-13 |
| 15 | Totalfunktion: Jedes Paket → genau ein Ergebnis | CHARTER §SR-20 |
| 16 | Deterministic-first | CHARTER §2 |
| 17 | Fail-Closed bei Unklarheit | CHARTER §SR-10 |
| 18 | Keine produktiven Altbezeichnungen | — |
| 19 | `idempotency_key` ist kanonisch | CONTRACTS §8.1 |
| 20 | `attempt_id` ist eingeschränkt (0–999999) | CONTRACTS §1.3 |
| 21 | Alle Atlas-Hybrid-Tests bestehen (Suite ATLAS) | — |
| 22 | Atlas-Hybrid-Phasen A1–A5 abgeschlossen | — |
| 23 | FrontierEngine erzeugt keine Endlosschleifen | — |
| 24 | Alle 4 Domänen-Beispiele laufen mit Atlas-Hybrid | — |
| 25 | Bestehende Regressions-Tests (Suite R) migriert | — |
| 26 | GATE-ATLAS bestanden | — |
| 27 | Atlas-Hybrid-Zonen verwenden korrekte Zustandsmaschine | GREMIUM §6.6 |
| 28 | Kristallisation nutzt `crystallization_progress` | GREMIUM §6.7 |
| 29 | Energiekonten sind deterministisch und auditierbar | GREMIUM §6.5 |
| 30 | FrontierCandidates enthalten strukturierte Begründung | GREMIUM §6.10 |
| 31 | Atlas-Hybrid: Leere Zonen sind `UNEXPLORED`, nicht `HEALTHY` | GREMIUM §6.6 |
| 32 | Atlas-Hybrid: `SafetyConstraint` unterliegt keinem Decay | GREMIUM §6.9 |
| 33 | Atlas-Hybrid: Questor schreibt keine Atlas-Signale | CHARTER §SR-04 |
| 34 | Atlas-Hybrid: `DiagnosticResolution` heilt Fracture nur auditiert | GREMIUM §6.8 |
| 35 | Atlas-Hybrid: `FrontierCandidate` enthält strukturierte Begründung | GREMIUM §6.10 |
| 36 | Atlas-Hybrid: Multi-Objective Trade-offs erzeugen keine Fracture | GREMIUM §6.10.10 |

---

## §13 Status-Report-Template

Nach jeder Phase ist folgender Report zu erstellen:

```
Phase: [Q-Nummer / A-Nummer]
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

## §14 Sicherheitsregeln für die Implementierung

### §14.1 Implementierungsregeln

| # | Regel | CHARTER-Referenz |
| --- | --- | --- |
| IR-1 | Keine produktiven Altbezeichnungen in aktiven Laufzeitquellen | — |
| IR-2 | Keine Adapter zwischen alter und neuer Welt in der Zielarchitektur | — |
| IR-3 | Questor ersetzt die frühere Black Box, ist aber keine alte Kastenarchitektur | — |
| IR-4 | Questor ist kein Gremium-Rang | CHARTER §SR-04 |
| IR-5 | Questor schreibt nicht in Atlas oder Archiv | CHARTER §SR-04 |
| IR-6 | QuestorBlackbox bleibt lokal und isoliert | CHARTER §SR-07 |
| IR-7 | Operational ≠ Scientific bleibt strikt | CHARTER §SR-08 |
| IR-8 | Fail-Closed bleibt verbindlich | CHARTER §SR-10 |
| IR-9 | Menschliche Königin wird niemals überstimmt | CHARTER §SR-11 |
| IR-10 | Hardwarezugriff nur über HAL | CHARTER §SR-12 |
| IR-11 | Leases kommen ausschließlich vom Resource Governor | CHARTER §SR-06 |
| IR-12 | Direkte physische Ausführung ohne gültigen Envelope ist verboten | CHARTER §SR-01 |
| IR-13 | Keine gleichwertigen Doppelreferenzen ohne Konflikthierarchie | — |
| IR-14 | Atlas-Hybrid-Implementierung erzeugt keine neuen Sicherheitsregeln | CHARTER §3 |
| IR-15 | Atlas-Hybrid-Implementierung definiert keine neuen Datenverträge | CONTRACTS §6.10 |

### §14.2 Verbotene Patterns

Die folgenden Patterns sind in der Zielarchitektur verboten:

| # | Pattern | CHARTER-Referenz |
| --- | --- | --- |
| VP-1 | Questor schreibt direkt in den Atlas | CHARTER §SR-04 |
| VP-2 | Questor schreibt direkt in das Archiv | CHARTER §SR-04 |
| VP-3 | Questor liest globale Signal-Stacks | — |
| VP-4 | Questor setzt ESTOP zurück | CHARTER §SR-05 |
| VP-5 | Questor vergibt Leases | CHARTER §SR-06 |
| VP-6 | Questor erzeugt rote Signale direkt | — |
| VP-7 | Gremium liest QuestorBlackbox | CHARTER §SR-07 |
| VP-8 | Dispatcher sendet produktiv ohne `gate_record_ref` | CHARTER §SR-53 |
| VP-9 | Receiver erwartet alte Ergebnisformen | — |
| VP-10 | Archivar prüft alte Instanz-ID-Felder | — |
| VP-11 | Produktive Adapterlogik zwischen alter und neuer Welt | — |
| VP-12 | Direkte physische Ausführung ohne Envelope | CHARTER §SR-01 |
| VP-13 | Operational wird als Scientific interpretiert | CHARTER §SR-08 |
| VP-14 | LEASE_DENIED wird als ESTOP behandelt | CHARTER §SR-09 |
| VP-15 | Zwei gleichwertige primäre Referenzdateien ohne Konflikthierarchie | — |
| VP-16 | HAL vergibt Leases | CHARTER §SR-06 |
| VP-17 | HAL interpretiert wissenschaftliche Ziele | CHARTER §SR-08 |
| VP-18 | HAL setzt ESTOP eigenmächtig zurück | CHARTER §SR-05 |
| VP-19 | Atlas-Hybrid erzeugt Sicherheitsregeln außerhalb von CHARTER | CHARTER §3 |
| VP-20 | FrontierEngine überschreibt SafetyConstraints | GREMIUM §6.9 |

---

## §15 Zusammenfassung der Spezifikation

| Aspekt | Definition |
| --- | --- |
| Phasen | Q0–Q18 (19 Questor-Phasen), M0–M5 (6 MYRMEX-Migrationsphasen), Phase 1–10 (10 MYRMEX-Neubau-Phasen), A1–A5 (5 Atlas-Hybrid-Phasen), HAL-H0 bis HAL-H6 (7 HAL-Phasen) |
| Meilensteine | MS-1 bis MS-6 (6 Questor-Meilensteine), Atlas-MS-1 bis Atlas-MS-3 (3 Atlas-Meilensteine) |
| Gesamtdauer | ~44–67 Tage (Questor, 1 Entwickler), ~12–18 Tage (Atlas-Hybrid), ~22–30 Tage (3 Entwickler) |
| Test-Anzahl | ~541 Tests (inkl. ~120 Atlas-Hybrid-Tests) |
| Coverage-Ziel | ≥ 88% gesamt, ≥ 95% sicherheitskritisch |
| Kritischer Pfad | Q0 → Q1 → Q5 → Q7 → Q8 → Q9 → Q10 → Q11 → Q14 → Q15 → Q16 → Q17 → Q18 |
| Atlas-Pfad | MYRMEX Phase 3 → A1 → A2 → A3 → A4 → A5 → MYRMEX Phase 10 |
| Externe Abhängigkeiten | MYRMEX Phase 1, 2, 3, 5, 8; HAL Phase HAL-H1, HAL-H6; Questor MS-3 (für Atlas A5) |
| Risiken | 12 identifizierte Risiken mit Mitigation |
| Akzeptanzkriterien | 36 Kriterien für das Gesamtsystem |
| Test-Gates | 9 Gates (inkl. GATE-ATLAS) |

---

## §16 Dokumentenhierarchie

Dieses Dokument steht in der Schicht `ops/` und referenziert:

- `foundation/CHARTER.md` für Sicherheitsregeln (CHARTER §SR-XX)
- `foundation/CONTRACTS.md` für Datenverträge (CONTRACTS §X.X)
- `specs/QUESTOR.md` für Questor-spezifische Details
- `specs/HAL.md` für HAL-spezifische Details
- `specs/GREMIUM.md` für Gremium-spezifische Details (inkl. Atlas-Hybrid-System §6)
- `ops/VALIDATION.md` für Teststrategie und Akzeptanzkriterien

**Regel:** Änderungen an Phasen in diesem Dokument erfordern eine Versionsänderung und eine Überprüfung der referenzierten Dokumente.

---

## Anhang A: Akzeptanzprüfung für ATLAS-HYB-1.0.0

Nach dem Einfügen dieser Änderungen sollte `ROADMAP.md` folgende Kriterien erfüllen:

| # | Kriterium | Status |
|---:|---|---|
| 1 | Kopfzeile enthält Version `1.1.0-atlas-hyb.1` | ☐ |
| 2 | `§0.1 Änderungsantrag ATLAS-HYB-1.0.0` ist vorhanden | ☐ |
| 3 | `§2.1` enthält Atlas-Hybrid in der Gesamttabelle | ☐ |
| 4 | `§4A` definiert die Phasen A1 bis A5 | ☐ |
| 5 | Phase A1 deckt Energiekonten und Zone-Health ab | ☐ |
| 6 | Phase A2 deckt Topologie, kategorische Dimensionen und ObjectiveFamily ab | ☐ |
| 7 | Phase A3 deckt DiagnosticResolution und SafetyConstraint ab | ☐ |
| 8 | Phase A4 deckt FrontierEngine und ResearchTopic ab | ☐ |
| 9 | Phase A5 deckt die 4 Domänen-Beispiele ab | ☐ |
| 10 | `§7` enthält Atlas-Meilensteine und Abhängigkeiten | ☐ |
| 11 | `§8` beschreibt den Atlas-Pfad und Parallelisierung | ☐ |
| 12 | `§10` enthält Atlas-Phasen im Gantt-Diagramm | ☐ |
| 13 | `§11` enthält GATE-ATLAS und Teststrategie | ☐ |
| 14 | `§12` enthält Atlas-spezifische Akzeptanzkriterien | ☐ |
| 15 | Keine neuen Sicherheitsregeln wurden definiert | ☐ |
| 16 | CHARTER-Hierarchie bleibt gewahrt | ☐ |

---