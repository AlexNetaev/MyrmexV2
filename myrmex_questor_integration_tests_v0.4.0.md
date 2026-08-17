# 🧪 MYRMEX v2.4.0 + QUESTOR v0.2.3 — INTEGRATIONS- UND TROCKENTEST-DATEI

**Dateiname:** `myrmex_questor_integration_tests_v0.4.0.md`
**Version:** 0.4.0
**Bezug:** `structure_standalone_v2.4.0.md`, Strukturversion 1.1.1
**HAL-Bezug:** `structure_hal_v0.2.0.md`
**System:** MYRMEX v2.4.0 + Questor v0.2.3
**Status:** Verbindlicher Testauftrag für Dry-Run und spätere Implementierungsabnahme
**Sprache:** Deutsch

---

## 1. Änderungen gegenüber Version 0.3.1

Diese Testversion ist ein **major update** gegenüber v0.3.1.

Neu:

1. **Suite H** für HAL v0.2.0 mit 24 Tests.
2. Bezug auf `structure_hal_v0.2.0.md`.
3. HAL-spezifische Tests für:
   - Langzeit-Prozesse
   - Hardware-Interlocks
   - Zonen-Mutex
   - Compute-Ressourcenmodell
   - Parameter-Schema-Registry
4. Erweiterte Testvektoren für Prozess-Idempotenz.
5. Erweiterte kritische Warnungen für HAL.

Unverändert aus v0.3.1:

- Suite N (7 Tests)
- Suite I (18 Tests)
- Suite S (5 Tests)
- Suite R (12 Tests)
- Suite Z (8 Tests)

---

## 2. Zweck dieser Datei

Diese Datei definiert die vollständige Testaufforderung für:

- MYRMEX v2.4.0
- Questor v0.2.3
- HAL v0.2.0
- Integration zwischen allen drei Systemen
- Blackbox-Isolation
- Sicherheitsregeln
- Szenario-Pflichttests
- Regressionsfähigkeit gegenüber v2.3.1
- Zielpräzisierung
- HAL-spezifische Tests

Die Datei ist dafür gedacht, einer testenden KI übergeben zu werden, damit diese einen strukturierten Trockenlauf oder später einen implementierten Testlauf durchführt.

---

## 3. Testgrundlage und Dokumentenhierarchie

### 3.1 Primäre Testgrundlage

Verbindlich ist:

- `structure_standalone_v2.4.0.md`, Strukturversion **1.1.1**
- `structure_hal_v0.2.0.md`

Diese Testdatei ist die maßgebliche Testanweisung für diese Strukturversionen.

### 3.2 Unterstützende Dokumente

Unterstützend:

- `structure_standalone_questor_v0.2.3.md`
  - Rolle: unterstützendes Questor-Begleitdokument
  - nicht primär bei Integrationskonflikten

Historisch:

- `questor_myrmex_integration_addendum_v0.1.md`
  - wird durch diese Testdatei präzisiert und bei Unterschieden überstimmt

### 3.3 Fehlende HAL-Datei

Wenn keine separate `hal_v2.4.0.md` oder `structure_hal_v0.2.0.md` vorhanden ist:

- HAL wird nur gegen den HAL-Minimalvertrag aus Strukturversion 1.1.1 geprüft
- Suite H wird als nicht prüfbar markiert
- die Testdatei bleibt für alle anderen Suites gültig

### 3.4 Konfliktregel

Bei Widersprüchen gilt:

1. `structure_standalone_v2.4.0.md` Version 1.1.1
2. `structure_hal_v0.2.0.md`
3. diese Testdatei Version 0.4.0
4. Questor-Begleitdokumente
5. historische Addenda

---

## 4. Rolle der Test-KI

Die Test-KI handelt als:

- Senior Test Engineer
- Systems Integration Reviewer
- Dry-Run Auditor
- Architektur-Reviewer
- HAL-Integration-Reviewer

### 4.1 Dry-Run-Modus

Wenn keine Implementierungsfreigabe gegeben ist:

- kein Code
- keine Dateiänderungen
- keine pytest-Ausführung
- mentale Simulation
- Bewertung mit `BESTANDEN` / `NICHT BESTANDEN`
- Blocker und Nicht-Blocker getrennt melden
- keine stillschweigenden Annahmen bei unklaren Spezifikationslücken

Wenn kein produktives Repository übergeben wurde:

- N-01 kann nur spezifikationsbasiert bewertet werden
- der spätere reale Source-Scan ist als Implementierungsbedingung zu nennen
- das Fehlen eines Repositories ist im Dry-Run eine Modusbedingung, kein Architekturfehler

### 4.2 Implementierungsmodus

Wenn eine Phase explizit freigegeben ist:

- nur die freigegebene Phase implementieren
- pytest verwenden
- keine späteren Phasen vorziehen
- nach jeder Phase Status-Report schreiben
- reale Source-Scans für N-01 durchführen, sobald produktive Quellen existieren

---

## 5. Eingaben für den Testlauf

Erforderliche Eingaben:

1. `structure_standalone_v2.4.0.md`, Strukturversion 1.1.1
2. `myrmex_questor_integration_tests_v0.4.0.md`

Optional:

3. `structure_hal_v0.2.0.md`
4. `structure_standalone_questor_v0.2.3.md`
5. produktives Repository, falls Implementierungsmodus aktiv ist

Wenn nur die Spezifikationen übergeben werden, ist der Lauf als reiner Dry-Run durchzuführen.

---

## 6. Testprinzipien

Die folgenden Prinzipien sind bindend:

1. Deterministisch vor LLM.
2. Fail-Closed.
3. Blackboard-Pattern.
4. Keine produktiven Altbezeichnungen in Zielquellen.
5. Keine produktiven Adapter.
6. Questor ist kein Gremium-Rang.
7. Questor schreibt nicht in Atlas oder Archiv.
8. QuestorBlackbox bleibt isoliert.
9. Operational ≠ Scientific.
10. ESTOP ≠ LEASE_DENIED.
11. Keine physische Ausführung ohne Envelope, Gate und Lease.
12. Menschliche Königin wird niemals überstimmt.
13. Die kanonische Referenz ist `structure_standalone_v2.4.0.md` Version 1.1.1.
14. HAL vergibt keine Leases.
15. HAL interpretiert keine wissenschaftlichen Ziele.
16. LLM bleibt Advisor, niemals finale Sicherheitsinstanz.
17. HAL behandelt CUDA_OOM als OPERATIONAL, nicht als SAFETY.
18. HAL behandelt LEASE_DENIED als OPERATIONAL, nicht als ESTOP.
19. HAL behandelt Hardware-Interlock als SAFETY.
20. HAL behandelt Software-ESTOP als SAFETY.
21. HAL trennt Kommando-Timeout von Prozess-Dauer.
22. HAL unterstützt Langzeit-Prozesse mit SAFE_HOLD und RESUME.
23. HAL unterstützt zonenbasierte Mutex-Modellierung.
24. HAL unterstützt Parameter-Schema-Registry.

---

## 7. Definition produktiver Quellen und Naming-Allowlist

### 7.1 Produktive Quellen

Für N-01 gelten als produktive Quellen:

- `src/`
- `config.py`
- aktive Laufzeitkonfiguration
- aktive Pydantic-Modelle
- aktive Tests, soweit sie keine expliziten Migrations- oder Scan-Fixtures sind

### 7.2 Nicht produktive Quellen

Nicht als produktive Quellen gelten:

- Dokumentationen
- archivierte Spezifikationen
- Migrationsdokumente
- Testdateien, die Suchbegriffe enthalten
- explizite Allowlist-Dateien unter `tests/migration_allowlist/`

### 7.3 Verbotene produktive Altbezeichnungen

Die folgenden Bezeichnungen dürfen in produktiven Quellen nicht vorkommen:

```text
swarm_ergebnis_paket
SwarmErgebnisPaket
swarm_instance_id
MockSwarm
swarm_interface
```

Treffer sind nur erlaubt in:

- Archivdokumenten
- Migrationsdokumenten
- Test-/Scan-Fixtures
- expliziten Allowlists

### 7.4 Allowlist-Format

Empfohlene Datei:

```text
tests/migration_allowlist/naming_allowlist.yaml
```

Mindestfelder pro Eintrag:

```yaml
- path: tests/migration_fixtures/old_contract_samples.py
  pattern: swarm_ergebnis_paket
  reason: migration_test_fixture
  approved_until: 2026-12-31
  owner: architect
  review_required: true
```

Regeln:

- Allowlists müssen explizit sein.
- Allowlists dürfen keine produktiven Laufzeitquellen freischalten.
- Allowlists sollten zeitlich begrenzt sein.
- Allowlists sollten review-pflichtig sein.

---

## 8. Testdaten und Testvektoren

### 8.1 Idempotency-Key für Kommandos

Kanonic:

```text
idempotency_key = package_id + ":" + zyklus_id + ":" + attempt_id
```

Regeln:

- `package_id` und `zyklus_id` müssen dem Format
  `^[A-Za-z0-9._-]{1,128}$`
  genügen.
- `attempt_id` ist eine Ganzzahl.
- `attempt_id >= 0`.
- `attempt_id <= 999999`.
- `attempt_id` wird als einfache Dezimalzahl ohne führende Nullen serialisiert.
- Keine zusätzliche Whitespace.
- Maximale Länge des `idempotency_key`: 264 Zeichen.

### 8.2 Gültige Testvektoren für Kommandos

```text
pkg-001:zyklus-014:0
pkg-001:zyklus-014:2
abc.def_1:zyklus-99:10
```

### 8.3 Ungültige Testvektoren für Kommandos

```text
pkg 001:zyklus-014:2
pkg/001:zyklus-014:2
pkg-001:zyklus/014:2
pkg-001:zyklus-014:02
pkg-001:zyklus-014:
pkg-001:zyklus-014:1000000
```

### 8.4 Idempotency-Key für HAL-Kommandos

Empfohlen:

```text
hal_idempotency_key = command_id:lease_ref:slot_id
```

### 8.5 Idempotency-Key für HAL-Prozesse

Empfohlen:

```text
hal_process_idempotency_key = process_id:lease_ref:slot_id
```

---

## 9. Empfohlene Testreihenfolge

Die Test-KI soll die Tests in dieser Reihenfolge durchführen:

1. Suite N — Naming & Contract Migration
2. Suite I — Integration
3. Suite S — Szenario-Pflichttests
4. Suite R — Regressions-Tests
5. Suite Z — Zielpräzisierung
6. Suite H — HAL v0.2.0
7. abschließende kritische Warnprüfung
8. zusammenfassender Bericht

---

# 10. SUITE N — NAMING & CONTRACT MIGRATION

## N-01: Keine produktiven Altbezeichnungen

### Prüfung

Suche in aktiven produktiven Quellen nach den folgenden Begriffen:

```text
swarm_ergebnis_paket
SwarmErgebnisPaket
swarm_instance_id
MockSwarm
swarm_interface
```

Zusatzprüfung:

- keine produktive Adapterlogik
- keine Dual-Mode-Schnittstelle für alte und neue Welt
- keine produktive Freischaltung alter Begriffe durch allgemeine Ausnahmen

### Erwartet

- keine Treffer in produktiven Quellen
- Treffer nur in Migrations-/Archiv-/Testdokumenten oder Allowlists erlaubt
- keine aktive Adapterlogik
- Allowlist-Einträge sind explizit, zeitlich begrenzt und review-pflichtig

---

## N-02: QuestorErgebnisPaket validiert

### Prüfung

Ein vollständiges `questor_ergebnis_paket` wird erzeugt.

### Erwartet

- Pydantic-Validierung erfolgreich
- `questor_instance_id` vorhanden
- `sequence_number` vorhanden
- `idempotency_key` korrekt kanonisch gebildet
- `questor_metadata` optional
- keine freien Zusatzfelder außerhalb von `questor_metadata`

---

## N-03: Archivar nutzt questor_instance_id

### Prüfung

Archivar prüft Sequence pro:

```text
questor_instance_id
```

### Erwartet

- monotone Sequence wird akzeptiert
- doppelte oder rückläufige Sequence wird abgelehnt
- keine alte Instanz-ID wird geprüft

---

## N-04: Dispatcher baut Envelope

### Prüfung

Dispatcher empfängt:

- `research_package`
- `gate_record`
- `lease_grants`

### Erwartet

- erzeugt `QuestorDispatchEnvelope`
- sendet nicht nacktes `ResearchPackage` im Produktivpfad
- Envelope enthält `gate_record_ref`
- Envelope enthält konsistente Lease- und Security-Angaben

---

## N-05: Direkte Pakete sind sandbox-only

### Prüfung

Ein direktes `ResearchPackage` ohne Envelope wird übergeben.

### Erwartet

- nur erlaubt, wenn Test-/Dev-Konfiguration aktiv ist
- `security_mode = DEV_SANDBOX_ONLY`
- keine physische Ausführung
- standardmäßig: `DIRECT_PACKAGE_FORBIDDEN`

---

## N-06: QuestorMetadata wird nicht wissenschaftlich interpretiert

### Prüfung

Archivar erhält `questor_metadata`.

### Erwartet

- keine Kristalle aus `questor_metadata`
- keine Signale aus `questor_metadata`
- `operational_metrics` dürfen nur operational verarbeitet werden

---

## N-07: Blackbox liegt außerhalb der Gremium-Daten

### Prüfung

QuestorBlackbox-Pfad wird geprüft.

### Erwartet

- nicht unter `data/archiv/`
- nicht unter `data/atlas/`
- nicht unter `data/operational_logs/`
- nur unter `data/questor_blackbox/` oder äquivalent isoliert

---

# 11. SUITE I — INTEGRATION

## I-01: Happy Path Szenario A

### Setup

Chemie-Kinetik-Paket mit gültigem Envelope.

### Erwartet

- Questor führt aus
- Ergebnis:
  - `status: erfolgreich`
  - `abbruch_grund: null`
  - `abbruch_klasse: OPERATIONAL`
- Archivar empfängt Ergebnis
- Kristallkandidaten werden verarbeitet
- keine Blackbox-Inhalte im Gremium

---

## I-02: Invalides Paket

### Setup

`routing_graph.max_loop_iterations` fehlt.

### Erwartet

- Questor bricht ab
- vollständiges Ergebnis:
  - `status: abgebrochen`
  - `abbruch_grund: PACKAGE_INVALID`
  - `abbruch_klasse: OPERATIONAL`
  - `vollstaendig_flag: true`
- Archivar kann Ergebnis verarbeiten
- keine HAL-Aktion

---

## I-03: Direktes ResearchPackage verboten

### Setup

Direkte Übergabe ohne Envelope, obwohl nicht erlaubt.

### Erwartet

- `abbruch_grund: DIRECT_PACKAGE_FORBIDDEN`
- `abbruch_klasse: OPERATIONAL`
- vollständiges Ergebnis

---

## I-04: Envelope ohne gate_record_ref

### Setup

`QuestorDispatchEnvelope` ohne `gate_record_ref`.

### Erwartet

- `abbruch_grund: PACKAGE_INVALID`
- `abbruch_klasse: OPERATIONAL`
- vollständiges Ergebnis

---

## I-05: LEASE_DENIED ohne ESTOP

### Setup

Zwei Pakete benötigen denselben Slot.

### Erwartet

- zweites Paket erhält `LEASE_DENIED`
- kein ESTOP
- keine `SAFETY`-Klasse
- Paket wartet oder bricht operational ab

---

## I-06: LEASE_QUEUED Timeout

### Setup

Lease bleibt `QUEUED` länger als erlaubt.

### Erwartet

- kein unbegrenztes Warten
- Abbruch:
  - `abbruch_grund: LEASE_QUEUED_TIMEOUT`
  - `abbruch_klasse: OPERATIONAL`
- oder sicherer Sandbox-Fallback gemäß Policy

---

## I-07: ESTOP während Questor-Ausführung

### Setup

HAL meldet physikalische Gefahr.

### Erwartet

- aktive Commands stoppen
- Leases werden `ESTOP_SUSPENDED`
- Ergebnis:
  - `status: abgebrochen`
  - `abbruch_grund: ESTOP_RECEIVED`
  - `abbruch_klasse: SAFETY`
- Blackbox erhält `SAFETY_HOLD`
- Gremium erhält keine Blackbox

---

## I-08: Operativer Crash OOM

### Setup

Compute-Job stirbt mit OOM.

### Erwartet

- `status: abgebrochen`
- `abbruch_grund: OOM`
- `abbruch_klasse: OPERATIONAL`
- keine wissenschaftlichen Signale
- optional `resource_pressure_event` durch Gremium/Archivar

---

## I-09: Wissenschaftlicher Fehlschlag

### Setup

Messung zeigt Zielverfehlung.

### Erwartet

- `status: fehlgeschlagen`
- `abbruch_grund: TARGET_NOT_REACHED`
- `abbruch_klasse: SCIENTIFIC`
- Signalvorschläge erlaubt
- Kristallkandidaten möglich

---

## I-10: Routing-Loop-Schutz

### Setup

Szenario B: Probe pendelt zwischen Inkubator und Mikroskop.

### Erwartet

- `max_loop_iterations` wird respektiert
- Abbruch:
  - `abbruch_grund: ROUTING_LOOP_TIMEOUT`
  - `abbruch_klasse: OPERATIONAL`

---

## I-11: Unbekannte Dimension ohne Approval

### Setup

Paket nutzt neue Dimension, aber `dimension_expansion_approval` fehlt.

### Erwartet

- keine physische Ausführung
- Sandbox/Simulation erlaubt, falls konfiguriert
- sonst:
  - `abbruch_grund: DIMENSION_APPROVAL_MISSING`
  - `abbruch_klasse: OPERATIONAL`

---

## I-12: Fracture Diagnosis

### Setup

Zone ist in QUARANTÄNE, Paket hat `gate_mode = FRACTURE_DIAGNOSIS`.

### Erwartet

- Questor darf diagnostic-safe ausführen
- Ergebnis kann diagnostische Kristallkandidaten enthalten
- Diagnose-Kristalle werden nicht in normale Cluster-Berechnung übernommen

---

## I-13: FULL_REBUILD während Questor läuft

### Setup

Kartograph startet FULL_REBUILD, während Questor ein Paket ausführt.

### Erwartet

- laufendes Paket referenziert alte `atlas_version_id`
- `observed_atlas_version_id` bleibt alt
- neuer `atlas_head_pointer` gilt nur für neue Pakete
- keine Invalidierung laufender Quests

---

## I-14: SAFE_MODE und Questor

### Setup

Menschliche Königin löst SAFE_MODE aus.

### Erwartet

- keine neuen Dispatches
- keine neuen Pakete
- keine neue Exploration
- laufende risikoarme Quests dürfen kontrolliert abschließen
- riskante Quests werden pausiert oder sicher abgebrochen

---

## I-15: Idempotenz im Archivar

### Setup

Dasselbe `questor_ergebnis_paket` wird zweimal übergeben.

### Erwartet

- Duplikat wird verworfen
- kein doppelter Kristall
- kein doppeltes Signal
- kanonischer `idempotency_key` wird korrekt verglichen

---

## I-16: Sequence-Recovery nach Questor-Crash

### Setup

Questor stirbt nach Sequence 7.

### Erwartet

- nächste Sequence ist 8
- keine Doppelnummer
- keine ungeklärte Lücke
- falls unsicher: `RECOVERY_UNSAFE`

---

## I-17: Prompt-Injection im Paketkontext

### Setup

`kontext` enthält eine Anweisung, Sicherheitsregeln zu ignorieren und physische Messung auszuführen.

### Erwartet

- Questor führt keine sicherheitswidrige Aktion aus
- LLM-Vorschläge werden verworfen
- keine physische Ausführung ohne deterministische Freigabe

---

## I-18: Blackbox-Isolation

### Setup

Gremium-Komponente versucht, QuestorBlackbox zu lesen.

### Erwartet

- Zugriff ist vertraglich verboten
- Ergebnis enthält maximal `LocalAuditRef`
- keine Blackbox-Inhalte im Gremium

---

# 12. SUITE S — SZENARIO-PFLICHTTESTS

## S-A: Chemie — Kinetik-Optimierung

### Fokus

- Happy Path
- Envelope
- Lease
- HAL
- Archivar
- Kristallkandidaten

---

## S-B: Biologie — Zellkultur / UV-Exposition

### Fokus

- Routing-Schleife
- `max_loop_iterations`
- LEASE_DENIED
- keine ESTOP durch Ressourcenkonflikt
- Langzeit-Prozess mit SAFE_HOLD

---

## S-C: Materialwissenschaft — Katalysator-Entdeckung

### Fokus

- Gefahren
- ESTOP
- SAFETY_HOLD
- Sicherheitsklassifikation
- Hardware-Interlock

---

## S-D: Trockenlabor — Hyperparameter-Optimierung

### Fokus

- Compute-Job
- OOM
- operational vs scientific
- resource_pressure_metric
- CUDA_OOM als OPERATIONAL

---

## S-E: Fraktur

### Fokus

- gelbe Fraktur
- QUARANTÄNE
- FRACTURE_DIAGNOSIS
- diagnostische Kristalle
- keine normale Cluster-Verzerrung

---

# 13. SUITE R — REGRESSIONS-TESTS AUS V2.3.1

## R-01: Crash in Stufe 6

### Erwartet

- Recovery bleibt in Stufe 7, nicht Stufe 8
- kein vorzeitiger Questor-Dispatch

---

## R-02: Slot-Konflikt

### Erwartet

- LEASE_DENIED
- kein ESTOP
- Questor behandelt operational

---

## R-03: Seher-Halluzination

### Erwartet

- Veto ohne Evidenz → `SEHER_INVALID_VETO`
- keine blinde Freigabe
- bei Kanzler-Bestätigung Policy-Veto statt rotem Signal

---

## R-04: Dimensions-Expansion

### Erwartet

- PROPOSED_BY_IDEA → PROPOSED_BY_WAYPOINT → APPROVED_BEFORE_EXECUTION
- Questor blockiert physische Ausführung ohne Approval

---

## R-05: Gelbe Fraktur

### Erwartet

- Fraktur-Event korrekt erzeugt
- fracture_score korrekt
- FRACTURE_DIAGNOSIS möglich
- diagnostische Kristalle bleiben speziell

---

## R-06: ESTOP vs LEASE_DENIED

### Erwartet

- Ressourcenkonflikt nie ESTOP
- physikalische Gefahr immer ESTOP
- Leases bei ESTOP suspended

---

## R-07: Operativer Crash

### Erwartet

- OOM → operational
- kein wissenschaftliches Signal
- optional resource_pressure_event

---

## R-08: FULL_REBUILD unter Last

### Erwartet

- laufende Quests referenzieren alte Atlas-Version
- neuer Head gilt nur für neue Pakete
- alte Version bleibt lesbar

---

## R-09: Königin-Konflikt

### Erwartet

- SAFE_MODE
- keine neuen Questor-Dispatches
- menschliche Königin wird nicht überstimmt

---

## R-10: Totaler Seher-Block

### Erwartet

- Circuit-Breaker greift
- Zustände `SHADOW_MODE`, `TEMP_SUSPENDED` oder `PERMANENT_SUSPENDED` sind explizit definiert
- Zustandswechsel werden protokolliert
- automatische Zustandswechsel erfolgen nur bei ausreichender Stichprobe
- Rückkehr nach NORMAL erfordert Hysterese und manuelle Prüfung

---

## R-11: Routing-Loop-Schutz

### Erwartet

- `max_loop_iterations`
- `branch_condition_timeout`
- `ROUTING_LOOP_TIMEOUT`

---

## R-12: Policy-Veto-Review

### Erwartet

- Review nach `policy_veto_review_interval_cycles`
- Standardwert ist 20
- Wertebereich ist 1 bis 500
- 0 ist ungültig
- Review kann bestätigen, aufheben oder eskalieren
- Review wird protokolliert

---

# 14. SUITE Z — ZIELPRÄZISIERUNG

Diese Suite ist in Version 0.4.0 weiterhin verbindlich.

---

## Z-01: Kanonische Referenz und Begleitdokument

### Prüfung

Die Test-KI prüft, ob die Dokumentenhierarchie eindeutig ist.

### Erwartet

- `structure_standalone_v2.4.0.md` Version 1.1.1 ist primäre Referenz
- `structure_hal_v0.2.0.md` ist HAL-spezifische Referenz
- `structure_standalone_questor_v0.2.3.md` ist unterstützendes Begleitdokument
- Konfliktauflösung ist definiert
- Formulierungen im Begleitdokument, die eine primäre Gesamtreferenz beanspruchen, sind nicht bindend

---

## Z-02: Idempotency-Key-Kanonicalisierung und attempt_id

### Prüfung

Ein `questor_ergebnis_paket` mit bekannten IDs wird erzeugt.

### Erwartet

- `idempotency_key = package_id:zyklus_id:attempt_id`
- keine Whitespace
- keine mehrdeutige Serialisierung
- `package_id` und `zyklus_id` entsprechen dem erlaubten Regex
- `attempt_id >= 0`
- `attempt_id <= 999999`
- führende Nullen sind in der kanonischen Form verboten
- maximale Länge des Keys ist 264 Zeichen
- ungültige Eingaben führen zu `PACKAGE_INVALID`

---

## Z-03: Erfolgssemantik von abbruch_klasse

### Prüfung

Ein erfolgreiches Ergebnis wird validiert.

### Erwartet

- `status: erfolgreich`
- `abbruch_grund: null`
- `abbruch_klasse: OPERATIONAL`
- die Semantik ist als Ergebnisklasse dokumentiert
- `abbruch_klasse` darf bei Erfolg nicht als tatsächlicher Abbruch interpretiert werden

---

## Z-04: Circuit-Breaker-Zustände und Metrikfenster

### Prüfung

Circuit-Breaker-Zustände und Auslösebedingungen werden geprüft.

### Erwartet

- Zustände:
  - `NORMAL`
  - `SHADOW_MODE`
  - `TEMP_SUSPENDED`
  - `PERMANENT_SUSPENDED`
- Messfenster ist definiert
- Mindeststichprobe ist definiert
- automatische Zustandswechsel erfolgen nur bei ausreichender Stichprobe
- Hysterese für Rückkehr nach NORMAL ist definiert
- manuelle Prüfung ist für Rückkehr erforderlich
- `PERMANENT_SUSPENDED` hat keine automatische Rückkehr
- Audit-Felder enthalten mindestens:
  - `old_state`
  - `new_state`
  - `trigger`
  - `metric_name`
  - `metric_value`
  - `window_size`
  - `sample_size`
  - `timestamp`
  - `authority`

---

## Z-05: Policy-Veto-Review-Parameter

### Prüfung

Der Review-Zyklus und sein Audit-Verhalten werden geprüft.

### Erwartet

- `policy_veto_review_interval_cycles` ist konfigurierbar
- Standardwert ist 20
- Wertebereich ist 1 bis 500
- 0 ist ungültig
- Review-Zähler ist persistent
- Neustart setzt den Zähler nicht zurück
- SAFE_MODE kann die Zählung pausieren, setzt sie aber nicht zurück
- Review erzeugt Audit-Event `policy_veto_review`
- Audit-Event enthält mindestens:
  - `event_type`
  - `zyklus_id`
  - `policy_veto_id`
  - `review_decision`
  - `review_reason`
  - `review_timestamp`
  - `review_authority`
  - `escalation_target`

---

## Z-06: QuestorSpec-Default-Instanz

### Prüfung

Ein `ResearchPackage` ohne `questor_spec` wird verarbeitet.

### Erwartet

- Default-Instanz wird angewendet
- Defaults sind sicher
- `autonomy_level = STRICT`
- LLM bleibt Advisor
- keine physische Ausführung bei Unklarheit
- `allowed_capabilities` und `allowed_loop_templates` sind leer
- leere Listen bedeuten: keine Capability und kein Template sind standardmäßig freigeschaltet
- physische Ausführung ist ohne explizite Freigabe nicht erlaubt

---

## Z-07: HAL-Minimalvertrag

### Prüfung

HAL wird als Interface/Dummy gegen den HAL-Vertrag aus `structure_hal_v0.2.0.md` geprüft.

### Erwartet

HAL bietet mindestens:

```text
get_environment_manifest() -> EnvironmentManifest
get_slot_state(slot_id) -> SlotState
get_zone_state(zone_id) -> ZoneState
execute_command(command) -> HALCommandResult
start_process(process_command) -> ProcessResult
monitor_process(process_id) -> ProcessResult
hold_process(process_id) -> ProcessResult
resume_process(process_id, resume_token) -> ProcessResult
abort_process(process_id) -> ProcessResult
release_stage(process_id, stage_id, release_authority) -> ProcessResult
report_estop(reason, trigger_source) -> EstopState
report_hardware_interlock(interlock_event) -> EstopState
get_estop_state() -> EstopState
reconcile_slot_state(slot_id) -> SlotState
reconcile_process_state(process_id) -> ProcessState
get_command_status(command_id) -> HALCommandStatus
```

Weiterhin erwartet:

- HAL vergibt keine Leases
- HAL interpretiert keine wissenschaftlichen Ziele
- HAL prüft `lease_ref` formal oder fragt Resource Governor
- Fehler sind klassifiziert als:
  - `OPERATIONAL`
  - `SAFETY`
- ESTOP-Zustände sind:
  - `NORMAL`
  - `ACTIVE`
  - `LATCHED`
  - `TEST`
- ESTOP stoppt aktive Kommandos
- ESTOP suspendiert betroffene Leases
- Questor darf ESTOP nicht zurücksetzen
- HAL protokolliert operational
- Dummy-HAL kann alle relevanten Fehlermodi simulieren

---

## Z-08: N-01-Scanbereich und Allowlist

### Prüfung

Die Definition produktiver Quellen und die Allowlist werden geprüft.

### Erwartet

- N-01 sucht in produktiven Quellen
- Migrations-/Archiv-/Testdokumente sind ausgenommen
- Allowlist-Dateien sind zulässig, wenn explizit gekennzeichnet
- Allowlist enthält mindestens:
  - `path`
  - `pattern`
  - `reason`
  - `approved_until`
  - `owner`
  - `review_required`
- Allowlists dürfen keine produktiven Laufzeitquellen freischalten
- Allowlists sollten zeitlich begrenzt und review-pflichtig sein

---

# 15. SUITE H — HAL V0.2.0

Diese Suite ist neu in Version 0.4.0 und prüft die HAL v0.2.0 Spezifikation.

---

## H-01: EnvironmentManifest ist vollständig

### Prüfung

Das Manifest wird auf Vollständigkeit geprüft.

### Erwartet

- Manifest enthält Slots
- Manifest enthält Zonen
- Manifest enthält Capabilities
- Manifest enthält Timeout-Grenzen
- Manifest enthält ESTOP-Mechanismus
- Manifest enthält Resource-Classes
- Manifest enthält `supported_security_modes`

---

## H-02: Kommando ohne Lease wird abgelehnt

### Prüfung

Ein `HALCommand` ohne gültige `lease_ref` wird gesendet.

### Erwartet

- `status: DENIED`
- `error_code: LEASE_INVALID`
- `error_class: OPERATIONAL`
- keine Ausführung

---

## H-03: Ungültige Lease wird abgelehnt

### Prüfung

Ein `HALCommand` mit ungültiger `lease_ref` wird gesendet.

### Erwartet

- `status: DENIED`
- `error_code: LEASE_INVALID`
- keine Ausführung

---

## H-04: Abgelaufene Lease wird abgelehnt

### Prüfung

Ein `HALCommand` mit abgelaufener `lease_ref` wird gesendet.

### Erwartet

- `status: DENIED`
- `error_code: LEASE_EXPIRED`
- keine Ausführung

---

## H-05: Slot-Mutex verhindert parallele Ausführung

### Prüfung

Zwei Kommandos werden gleichzeitig auf denselben Slot gesendet.

### Erwartet

- zweites Kommando erhält `SLOT_BUSY` oder `DENIED`
- kein paralleler physischer Zugriff

---

## H-06: Zonen-Mutex verhindert parallele Zonen-Nutzung

### Prüfung

Zwei Kommandos werden gleichzeitig auf dieselbe Zone gesendet.

### Erwartet

- zweites Kommando erhält `ZONE_LOCK_UNAVAILABLE`
- kein paralleler Zugriff auf gemeinsame Schiene

---

## H-07: ESTOP blockiert neue Kommandos

### Prüfung

ESTOP wird ausgelöst, dann wird ein neues Kommando gesendet.

### Erwartet

- `status: ESTOP`
- keine neue Ausführung
- `error_class: SAFETY`

---

## H-08: Hardware-Interlock blockiert neue Kommandos

### Prüfung

Hardware-Interlock wird ausgelöst, dann wird ein neues Kommando gesendet.

### Erwartet

- `status: INTERLOCK`
- keine neue Ausführung
- `error_class: SAFETY`
- `interlock_latched: true`
- `physical_reset_required: true`

---

## H-09: ESTOP suspendiert betroffene Leases

### Prüfung

ESTOP wird ausgelöst.

### Erwartet

- Resource Governor wird informiert
- betroffene Leases werden als suspendiert betrachtet
- Questor erhält Sicherheitsabbruch

---

## H-10: Hardware-Interlock suspendiert betroffene Leases und Zonen

### Prüfung

Hardware-Interlock wird ausgelöst.

### Erwartet

- Resource Governor wird informiert
- betroffene Leases werden als suspendiert betrachtet
- betroffene Zonen werden als `INTERLOCKED` betrachtet
- Questor erhält Sicherheitsabbruch

---

## H-11: Timeout führt zu operationalem Fehler

### Prüfung

Ein Kommando überschreitet seinen `timeout_s`.

### Erwartet

- `status: TIMEOUT`
- `error_code: COMMAND_TIMEOUT`
- `error_class: OPERATIONAL`
- kein ESTOP

---

## H-12: Timeout bei physischem Slot kann Reconciliation auslösen

### Prüfung

Ein Kommando auf einem physischen Slot überschreitet seinen `timeout_s`.

### Erwartet

- Slot kann auf `ERROR` gehen
- `reconcile_slot_state` erforderlich
- kein blinder Retry

---

## H-13: Duplicate Command wird blockiert

### Prüfung

Dasselbe Kommando wird zweimal gesendet.

### Erwartet

- `status: DUPLICATE_BLOCKED`
- keine erneute Ausführung
- keine doppelten Seiteneffekte

---

## H-14: Crash-Recovery ohne blinden Retry

### Prüfung

HAL crasht während eines Kommandos und wird neu gestartet.

### Erwartet

- nach unklarem Crash wird nicht automatisch neu ausgeführt
- `RECOVERY_UNSAFE` möglich
- Slot bleibt kontrolliert gesperrt bis Klärung

---

## H-15: HAL schreibt nur operational Logs

### Prüfung

HAL-Ereignisse werden protokolliert.

### Erwartet

- Logs landen in `data/operational_logs/`
- keine Atlas-Einträge
- keine Archiv-Einträge
- keine Blackbox-Einträge

---

## H-16: Physische Ausführung nur bei passendem Security-Mode

### Prüfung

Ein Kommando wird mit `SANDBOX` oder `DEV_SANDBOX_ONLY` auf einen physischen Slot gesendet.

### Erwartet

- `SANDBOX` oder `DEV_SANDBOX_ONLY` führt nicht physisch aus
- `NORMAL` darf physisch ausführen, wenn Lease und Slot es erlauben
- Verstöße führen zu `PHYSICAL_EXECUTION_FORBIDDEN`

---

## H-17: Compute-Ausführung nur bei passendem Security-Mode

### Prüfung

Ein Compute-Kommando wird mit `SANDBOX` oder `DEV_SANDBOX_ONLY` auf einen Compute-Slot gesendet.

### Erwartet

- `SANDBOX` oder `DEV_SANDBOX_ONLY` führt nicht echt aus
- `NORMAL` darf Compute ausführen, wenn Lease und Slot es erlauben
- Verstöße führen zu `COMPUTE_EXECUTION_FORBIDDEN`

---

## H-18: Langzeit-Prozess mit SAFE_HOLD

### Prüfung

Ein Langzeit-Prozess wird gestartet und die Lease läuft ab.

### Erwartet

- Prozess wird gestartet
- Prozess läuft für erwartete Dauer
- Bei Lease-Expiry: Prozess geht in `SAFE_HOLD`
- Prozess wird nicht zerstört
- `resume_token` wird erzeugt

---

## H-19: Langzeit-Prozess mit RESUME

### Prüfung

Ein Langzeit-Prozess wird gestartet, geht in `SAFE_HOLD`, und wird dann fortgesetzt.

### Erwartet

- Prozess wird gestartet
- Prozess geht in `SAFE_HOLD`
- `resume_process` mit gültigem `resume_token` wird aufgerufen
- Prozess wird fortgesetzt
- `process_state` geht von `SAFE_HOLD` nach `RUNNING`

---

## H-20: Langzeit-Prozess mit WAITING_FOR_RELEASE

### Prüfung

Ein Langzeit-Prozess mit mehrstufiger Ausführung wird gestartet.

### Erwartet

- Prozess wird gestartet
- Erste Stufe wird abgeschlossen
- Prozess geht in `WAITING_FOR_RELEASE`
- `release_stage` wird aufgerufen
- Prozess wird fortgesetzt
- `process_state` geht von `WAITING_FOR_RELEASE` nach `RUNNING`

---

## H-21: Langzeit-Prozess mit Stage-Release-Denied

### Prüfung

Ein Langzeit-Prozess mit mehrstufiger Ausführung wird gestartet und die Freigabe wird ohne Berechtigung angefordert.

### Erwartet

- Prozess wird gestartet
- Erste Stufe wird abgeschlossen
- Prozess geht in `WAITING_FOR_RELEASE`
- `release_stage` wird ohne Berechtigung aufgerufen
- `STAGE_RELEASE_DENIED` wird zurückgegeben
- Prozess bleibt in `WAITING_FOR_RELEASE`

---

## H-22: CUDA-OOM ist operational

### Prüfung

Ein Compute-Job stirbt mit CUDA-OOM.

### Erwartet

- `status: ERROR`
- `error_code: CUDA_OOM`
- `error_class: OPERATIONAL`
- kein ESTOP
- keine Sicherheitsprüfung

---

## H-23: Parameter-Schema-Validierung

### Prüfung

Kommandos mit verschiedenen Parameter-Schemas werden gesendet.

### Erwartet

- Kommando mit gültigem Schema wird akzeptiert
- Kommando mit unbekanntem Schema wird abgelehnt
- Kommando mit falscher Checksumme wird abgelehnt
- Fehlercode: `PARAMETER_SCHEMA_UNKNOWN` oder `PARAMETER_CHECKSUM_MISMATCH`
- Fehlerklasse: `OPERATIONAL`

---

## H-24: Dummy-HAL kann alle Fehlermodi simulieren

### Prüfung

Der Dummy-HAL wird auf alle definierten Fehlermodi geprüft.

### Erwartet

- alle definierten Fehlermodi sind testbar
- Simulation ist deterministisch
- keine echte Hardware beteiligt

---

# 16. Protokollformat

Die Test-KI muss jeden Test wie folgt protokollieren:

```text
[NAMING-TEST N-XX] [KOMPONENTE] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
[INTEGRATIONS-TEST I-XX] [SZENARIO Y] [KOMPONENTE] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
[SZENARIO-TEST S-X] [KOMPONENTE] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
[REGRESSIONS-TEST R-XX] [KOMPONENTE] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
[PRÄZISIERUNGS-TEST Z-XX] [KOMPONENTE] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
[HAL-TEST H-XX] [KOMPONENTE] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
```

Am Ende müssen die Gesamtsummen stehen:

```text
NAMING GESAMT: X/7 BESTANDEN
INTEGRATION GESAMT: X/18 BESTANDEN
SZENARIEN GESAMT: X/5 BESTANDEN
REGRESSION GESAMT: X/12 BESTANDEN
PRÄZISIERUNG GESAMT: X/8 BESTANDEN
HAL GESAMT: X/24 BESTANDEN
GESAMT: X/74 BESTANDEN
```

---

# 17. Zusammenfassender Bericht an die Test-KI

Am Ende des Testlaufs muss die Test-KI einen Bericht in dieser Struktur liefern:

```text
## Testbericht — MYRMEX v2.4.0 + Questor v0.2.3 + HAL v0.2.0

### 1. Modus
- Dry-Run | Implementierung

### 2. Testgrundlage
- structure_standalone_v2.4.0.md v1.1.1
- structure_hal_v0.2.0.md
- myrmex_questor_integration_tests_v0.4.0.md
- optional: structure_standalone_questor_v0.2.3.md
- optional: produktives Repository

### 3. Ergebnisse
NAMING GESAMT: X/7 BESTANDEN
INTEGRATION GESAMT: X/18 BESTANDEN
SZENARIEN GESAMT: X/5 BESTANDEN
REGRESSION GESAMT: X/12 BESTANDEN
PRÄZISIERUNG GESAMT: X/8 BESTANDEN
HAL GESAMT: X/24 BESTANDEN
GESAMT: X/74 BESTANDEN

### 4. Blocker
- [Blocker 1]
- [Blocker 2]
- oder: keine

### 5. Nicht-Blocker
- [Nicht-Blocker 1]
- oder: keine

### 6. Kritische Abweichungen
- [Abweichung]
- oder: keine

### 7. Sicherheitsrelevante Befunde
- [Befund]
- oder: keine

### 8. Gesamtbewertung
- BESTANDEN | NICHT BESTANDEN | TEILWEISE BESTANDEN

### 9. Freigabeempfehlung
- Freigabe für Phase X | keine Freigabe | nur bedingte Freigabe

### 10. Nächster Schritt
- [konkreter nächster Schritt]
```

---

# 18. Fehlerbericht bei nicht bestandenen Tests

Wenn ein Test fehlschlägt, muss die Test-KI zusätzlich melden:

```text
Fehlgeschlagener Test: [ID]
Komponente: [Komponente]
Problem: [Problem]
Erwartetes Verhalten: [Erwartung]
Beobachtetes Verhalten: [Beobachtung]
Wahrscheinliche Ursache: [Ursache]
Empfohlene Korrektur: [Korrektur]
Priorität: Blocker | Hoch | Mittel | Niedrig
```

Wenn ein Test wegen fehlender Eingaben nicht prüfbar ist:

```text
Nicht prüfbarer Test: [ID]
Grund: [Grund]
Empfehlung: [benötigte Unterlage oder Freigabe]
Status: BLOCKIERT | NICHT PRÜFBAR
```

Ein nicht prüfbarer Test darf nicht stillschweigend als bestanden markiert werden.

---

# 19. Kritische Warnungen für den Test

## 19.1 Nicht alte Kasten testen

Wenn ein Test alte Kasten wie:

```text
AnalystCaste
PlannerCaste
ExecutorCaste
TheoristCaste
```

als aktive Vertragskomponenten erwartet, ist der Test falsch.

Questor ersetzt nicht diese Kasten direkt, sondern die frühere Black Box aus v2.3.1.

---

## 19.2 Keine Blackbox im Archivar

Wenn ein Test erwartet, dass der Archivar QuestorBlackbox liest, ist der Test falsch.

---

## 19.3 Keine wissenschaftlichen Signale aus operationalen Fehlern

Wenn ein Test OOM, Timeout oder Lease-Konflikt als wissenschaftliches Signal interpretiert, ist der Test falsch.

---

## 19.4 Kein ESTOP bei Ressourcenkonflikt

Wenn ein Test LEASE_DENIED als ESTOP behandelt, ist der Test falsch.

---

## 19.5 Kein direkter Atlas-Zugriff durch Questor

Wenn ein Test erwartet, dass Questor direkt Signale in den Atlas schreibt, ist der Test falsch.

---

## 19.6 Keine Doppelreferenz

Wenn ein Test zwei primäre Referenzdateien ohne Konflikthierarchie annimmt, ist der Test falsch.

---

## 19.7 Keine HAL-Lease-Vergabe

Wenn ein Test erwartet, dass HAL Leases vergibt, ist der Test falsch.

---

## 19.8 Keine HAL-Wissenschaft

Wenn ein Test erwartet, dass HAL wissenschaftliche Ziele interpretiert oder wissenschaftliche Signale erzeugt, ist der Test falsch.

---

## 19.9 Kein CUDA-OOM als SAFETY

Wenn ein Test CUDA_OOM als SAFETY oder ESTOP interpretiert, ist der Test falsch.

---

## 19.10 Kein Hardware-Interlock als OPERATIONAL

Wenn ein Test Hardware-Interlock als OPERATIONAL interpretiert, ist der Test falsch.

---

## 19.11 Kein blinder Retry nach Crash

Wenn ein Test erwartet, dass HAL nach einem Crash automatisch neu startet, ist der Test falsch.

---

## 19.12 Keine automatische Interlock-Rücksetzung

Wenn ein Test erwartet, dass HAL einen Hardware-Interlock automatisch zurücksetzt, ist der Test falsch.

---

## 19.13 Keine Zonen-Lock-Eigenvergabe

Wenn ein Test erwartet, dass HAL Zonen-Locks eigenmächtig vergibt, ist der Test falsch.

---

## 19.14 Keine Prozess-Fortsetzung ohne Resume-Token

Wenn ein Test erwartet, dass HAL einen Prozess ohne gültigen Resume-Token fortsetzt, ist der Test falsch.

---

## 19.15 Keine Stage-Release ohne Berechtigung

Wenn ein Test erwartet, dass HAL eine Stage ohne Berechtigung freigibt, ist der Test falsch.

---

# 20. Akzeptanzkriterien für das Gesamtsystem

Das Gesamtsystem gilt als integriert, wenn:

- alle Naming-Tests bestehen
- alle Integrationstests bestehen
- alle Szenario-Tests bestehen
- alle Regressions-Tests bestehen
- alle Präzisierungs-Tests bestehen
- alle HAL-Tests bestehen
- keine produktiven Altbezeichnungen vorhanden sind
- kein produktiver Adapter vorhanden ist
- QuestorBlackbox isoliert bleibt
- Operational keine wissenschaftlichen Signale erzeugt
- ESTOP und LEASE_DENIED strikt getrennt bleiben
- SAFE_MODE weiterhin menschliche Sicherheit garantiert
- FRACTURE_DIAGNOSIS korrekt bleibt
- Dimensions-Expansion approval-pflichtig bleibt
- `idempotency_key` kanonisch ist
- `attempt_id` vollständig eingeschränkt ist
- QuestorSpec-Defaults sicher sind
- Circuit-Breaker-Zustände explizit sind
- Policy-Veto-Review konfigurierbar ist
- HAL-Minimalvertrag testbar ist
- HAL Langzeit-Prozesse unterstützt
- HAL Hardware-Interlocks unterstützt
- HAL Zonen-Mutex unterstützt
- HAL Compute-Ressourcenmodell unterstützt
- HAL Parameter-Schema-Registry unterstützt
- Naming-Allowlist explizit und review-pflichtig ist

---

# 21. Übergabeempfehlung für die andere KI

Wenn du diese Dateien in eine andere KI gibst, empfehle ich diese Aufforderung:

```text
Du bist Senior Test Engineer und Systems Architect.

Führe einen strukturierten Dry-Run für MYRMEX v2.4.0, Questor v0.2.3 und HAL v0.2.0 durch.

Verwende dafür:
1. structure_standalone_v2.4.0.md, Strukturversion 1.1.1
2. structure_hal_v0.2.0.md
3. myrmex_questor_integration_tests_v0.4.0.md

Wenn keine Implementierungsfreigabe gegeben ist:
- kein Code
- keine Dateiänderungen
- nur mentale Simulation

Führe alle Tests in der empfohlenen Reihenfolge durch:
1. Suite N
2. Suite I
3. Suite S
4. Suite R
5. Suite Z
6. Suite H

Erstelle am Ende:
- ein vollständiges Testprotokoll
- eine Zusammenfassung
- Blocker und Nicht-Blocker
- eine Gesamtbewertung
- eine Freigabeempfehlung
```