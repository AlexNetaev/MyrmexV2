# START DATEI — `structure_standalone_v2.4.0.md`

# 🧭 MYRMEX V2.4.0 + QUESTOR V0.2.3 — STANDALONE STRUKTURDATEI

**Dateiname:** `structure_standalone_v2.4.0.md`  
**Strukturversion:** 1.1.1  
**System:** MYRMEX v2.4.0 + Questor v0.2.3  
**Status:** Verbindliche kanonische Referenz für Dry-Run, Implementierung und Integration  
**Ersetzt:**  
- `structure_standalone_v2.3.1.md` als aktive Referenz  
- `structure_standalone_v2.4.0.md` Strukturversion 1.0.0  
- `structure_standalone_v2.4.0.md` Strukturversion 1.1.0  

**Sprache:** Deutsch  
**Freigabezustand:** Keine Implementierungsfreigabe; Standardmodus ist Dry-Run  

---

## 0. Patch-Hinweis für Version 1.1.1

Diese Version ist ein **bereinigender Zwischenstand** gegenüber Strukturversion 1.1.0.

Es gibt keine neue Grundarchitektur, sondern Präzisierungen und dokumentarische Bereinigungen.

### 0.1 Änderungen in 1.1.1

1. Die Kanonische Referenz wurde eindeutig festgelegt.
2. Das Questor-Begleitdokument wurde explizit als unterstützend eingeordnet.
3. Ältere nicht kanonische Idempotenz-Formulierungen wurden ersetzt.
4. `attempt_id` wurde vollständig eingeschränkt.
5. Der kanonische `idempotency_key` wurde mit Testvektoren präzisiert.
6. Die Erfolgssemantik von `abbruch_klasse` wurde klargestellt.
7. Circuit-Breaker-Zustände erhielten Messfenster, Mindeststichproben und Audit-Felder.
8. Policy-Veto-Review erhielt Wertebereich, Persistenz und Audit-Event-Felder.
9. QuestorSpec-Defaults wurden als sichere Restriktion dokumentiert.
10. Der HAL-Minimalvertrag wurde für die spätere separate HAL-Datei präzisiert.
11. Die Definition produktiver Quellen und die Naming-Allowlist wurden konkretisiert.

### 0.2 Ziel dieses Patch-Standes

Diese Datei soll:

- als eigenständige Referenz lesbar sein,
- ohne produktive Adapter auskommen,
- die Integration MYRMEX ↔ Questor eindeutig definieren,
- die spätere HAL-Datei vorbereiten,
- Implementierungs- und Testinterpretationen absichern.

---

# 1. Kanonische Referenz und Dokumentenhierarchie

## 1.1 Primäre Referenz

Diese Datei ist die **primäre und kanonische Referenz** für:

- MYRMEX v2.4.0
- Questor-Integration
- Vertragsfluss
- Sicherheitsregeln
- Testgrundlage
- Migrationsregeln
- HAL-Minimalvertrag bis zur separaten HAL-Datei

## 1.2 Unterstützende Dokumente

Die folgenden Dokumente sind unterstützend:

- `structure_standalone_questor_v0.2.3.md`  
  → Questor-spezifische Referenz, aber nicht primär bei Integrationskonflikten.
- `questor_myrmex_integration_addendum_v0.1.md`  
  → historische Testreferenz; wird durch aktuelle Testdateien ergänzt oder ersetzt, sofern Unterschiede bestehen.

## 1.3 Explizite Klarstellung zum Questor-Begleitdokument

Sofern `structure_standalone_questor_v0.2.3.md` Formulierungen enthält wie:

> Diese Datei ist die neue Referenz für das Gesamtsystem.

so sind diese Formulierungen für MYRMEX v2.4.0 **nicht bindend**.

Verbindlich ist:

- `structure_standalone_questor_v0.2.3.md` ist ein unterstützendes Questor-Begleitdokument.
- Die kanonische Hauptreferenz ist diese Datei.

## 1.4 Konfliktregel

Bei Widersprüchen gilt:

1. Diese Datei in Version 1.1.1.
2. Danach die jeweils aktuelle offizielle Testdatei.
3. Danach Questor-spezifische Begleitdokumente.
4. Danach historische Addenda und Archivalien.

Wenn Questor-Interna und MYRMEX-Integrationsvertrag kollidieren, ist der MYRMEX-Integrationsvertrag maßgeblich. Questor-Interna dürfen ihn nicht umgehen.

---

# 2. Rolle und Arbeitsmodus für implementierende oder testende KI

## 2.1 Rolle

Du bist:

- Senior Software Engineer
- Systems Architect
- Test Engineer für Systemintegration

Du arbeitest an einem autonomen Wissenschaftssystem mit:

- MYRMEX v2.4.0
- Questor v0.2.3

## 2.2 Arbeitsregeln

1. Arbeite phase-by-phase.
2. Schließe eine Phase vollständig ab, bevor die nächste beginnt.
3. Schreibe keinen Code für Phasen, die nicht freigegeben sind.
4. Wenn keine Implementierungsfreigabe vorliegt:
   - kein Code
   - keine Dateiänderungen
   - nur Dry-Run / mentale Simulation
5. Wenn Implementierungsfreigabe vorliegt:
   - nur die explizit freigegebene Phase implementieren
   - Python 3.10+
   - Pydantic v2
   - pytest
6. Keine späteren Phasen vorziehen.
7. Nach jeder Phase Status-Report schreiben.
8. Blocker und Nicht-Blocker immer getrennt melden.

---

# 3. System-Überblick

## 3.1 Die neue 6-Schichten-Architektur

| Schicht | Name | Verantwortung |
|---|---|---|
| 5 | 👑 Königin | Langfristige Vision, Meta-Ziele, menschliche oder LLM-basierte Führung |
| 4 | 🏛️ Gremium | Intelligenz, Atlas, Archiv, Ideen, Pakete, Sicherheit |
| 3 | ⚖️ Dispatch-Koordination | Dispatch-Vorbereitung, Lease-/Gate-Koordination |
| 2 | 🧭 Questor | Paketgebundenes Execution Subsystem |
| 1 | 🔌 HAL & Resource Governor | Slot-Routing, Leases, ESTOP, Hardwarezugriff |
| 0 | ⚙️ Physis / Compute | Hardware, Simulation, Compute |

Empfohlener Name für Schicht 3:

- `DispatchCoordinator`

Nicht empfohlen:

- Namen, die mit Questor-internen Komponenten verwechselt werden können.

---

## 3.2 Die 9-Stufen-Pipeline

Die Pipeline bleibt grundsätzlich erhalten.

| Stufe | Name | Verantwortlich |
|---|---|---|
| 1 | Wissens-Aufnahme | Archivar |
| 2 | Atlas-Strukturierung | Kartograph |
| 3 | Strategische Review | Kanzler ↔ Königin |
| 4 | Ideen-Generierung | Vordenker |
| 5a | Pre-Filter | Deterministischer Fast-Path |
| 5b | Ideen-Erdung | Lotse |
| 6 | Paket-Bau | Quartiermeister |
| 7 | Sicherheits-Gate | Richter + Seher |
| 8 | Dispatch & Execution | Dispatcher → Questor → Receiver → Archivar |

Die entscheidende Änderung in Stufe 8:

```text
package_dispatcher
  → QuestorDispatchEnvelope
    → QuestorFacade
      → Questor
        → questor_ergebnis_paket
          → result_receiver
            → Archivar
```

---

## 3.3 Kernregeln

### Blackboard-Pattern

Alle Ränge des Gremiums kommunizieren ausschließlich über:

- Atlas
- Archiv

Keine direkten Aufrufe zwischen Rängen.

### Questor ist kein Gremium-Rang

Questor darf nicht:

- in den Atlas schreiben
- in das Archiv schreiben
- Wegmarken erzeugen
- Ideen erzeugen
- Gate-Freigaben erteilen
- Leases vergeben
- ESTOP zurücksetzen
- globale Signale direkt schreiben
- finale LLM-Entscheidungen treffen
- menschliche oder königliche Entscheidungen ersetzen

Questor darf nur:

- ein Paket ausführen
- HAL-Kommandos innerhalb gültiger Leases senden
- ein `questor_ergebnis_paket` erzeugen
- Signalvorschläge und Kristallkandidaten übergeben
- eine lokale QuestorBlackbox schreiben

### Fail-Closed

Wenn etwas nicht sicher geprüft werden kann:

- keine Freigabe
- keine physische Ausführung
- kontrollierter Abbruch oder Eskalation

### Operational ≠ Scientific

| Klasse | Bedeutung | Wissenschaftliches Signal? |
|---|---|---|
| OPERATIONAL | Prozessfehler, Crash, Timeout, Lease-Problem | nein |
| SCIENTIFIC | wissenschaftliche Zielverfehlung, empirischer Widerspruch | ja, als Vorschlag |
| SAFETY | Sicherheitsverletzung, ESTOP | ja, nur mit Sicherheitsprüfung |

### Keine direkte physische Ausführung ohne Envelope

Physische Ausführung erfordert:

- gültiges `research_package`
- gültigen `QuestorDispatchEnvelope`
- gültige `gate_record_ref`
- gültige `lease_grants`
- passenden `security_mode`
- vorhandene Dimensionsfreigabe, falls physisch relevant

Direkte Übergaben von `ResearchPackage` ohne Envelope sind standardmäßig verboten.

---

# 4. Harte Grundregeln der Zielarchitektur

1. Kein Adapter zwischen alter und neuer Welt in der Zielarchitektur.
2. Keine produktiven Altbezeichnungen in aktiven Laufzeitquellen.
3. Questor ersetzt die frühere Black Box, ist aber keine alte Kastenarchitektur.
4. Questor ist kein Gremium-Rang.
5. Questor schreibt nicht in Atlas oder Archiv.
6. QuestorBlackbox bleibt lokal und isoliert.
7. Operational ≠ Scientific bleibt strikt.
8. Fail-Closed bleibt verbindlich.
9. Menschliche Königin wird niemals überstimmt.
10. Hardwarezugriff nur über HAL.
11. Leases kommen ausschließlich vom Resource Governor.
12. Direkte physische Ausführung ohne gültigen Envelope ist verboten.
13. Keine gleichwertigen Doppelreferenzen ohne Konflikthierarchie.

---

# 5. Repository-Struktur

Empfohlene Zielstruktur:

```text
myrmex_v2/
  ├── README.md
  ├── requirements.txt
  ├── pyproject.toml
  ├── config.py
  ├── src/
  │   ├── __init__.py
  │   ├── contracts/
  │   │   ├── __init__.py
  │   │   ├── enums.py
  │   │   ├── research_package.py
  │   │   ├── questor_dispatch.py
  │   │   ├── questor_result.py
  │   │   ├── atlas_models.py
  │   │   ├── pipeline_models.py
  │   │   ├── lease_models.py
  │   │   └── questor_metadata.py
  │   ├── gremium/
  │   │   ├── __init__.py
  │   │   ├── archivar.py
  │   │   ├── kartograph.py
  │   │   ├── kanzler.py
  │   │   ├── vordenker.py
  │   │   ├── pre_filter.py
  │   │   ├── lotse.py
  │   │   ├── quartiermeister.py
  │   │   ├── sicherheitsrat/
  │   │   │   ├── __init__.py
  │   │   │   ├── richter.py
  │   │   │   ├── seher.py
  │   │   │   └── circuit_breaker.py
  │   │   └── pipeline_orchestrator.py
  │   ├── atlas/
  │   │   ├── __init__.py
  │   │   ├── atlas_store.py
  │   │   ├── signal_registry.py
  │   │   └── clustering.py
  │   ├── transaction/
  │   │   ├── __init__.py
  │   │   ├── wal.py
  │   │   ├── state_machine.py
  │   │   └── recovery.py
  │   ├── resource_governor/
  │   │   ├── __init__.py
  │   │   ├── governor.py
  │   │   ├── slot_manager.py
  │   │   └── estop_handler.py
  │   ├── hal/
  │   │   ├── __init__.py
  │   │   ├── hal_interface.py
  │   │   └── dummy_hal.py
  │   ├── questor_interface/
  │   │   ├── __init__.py
  │   │   ├── package_dispatcher.py
  │   │   ├── result_receiver.py
  │   │   └── dummy_questor.py
  │   └── questor/
  │       ├── __init__.py
  │       ├── facade.py
  │       ├── validator.py
  │       ├── objective_parser.py
  │       ├── compass.py
  │       ├── policy_evaluator.py
  │       ├── loop_registry.py
  │       ├── capability_registry.py
  │       ├── ledger.py
  │       ├── trail_map.py
  │       ├── safety_monitor.py
  │       ├── recovery.py
  │       ├── sequence.py
  │       ├── sanitization.py
  │       ├── hal_bridge.py
  │       ├── result_builder.py
  │       ├── blackbox_archiver.py
  │       └── advisors/
  ├── tests/
  │   ├── test_contracts/
  │   ├── test_gremium/
  │   ├── test_atlas/
  │   ├── test_transaction/
  │   ├── test_resource_governor/
  │   ├── test_hal/
  │   ├── test_questor_interface/
  │   ├── test_questor/
  │   ├── test_integration/
  │   └── migration_allowlist/
  └── data/
      ├── archiv/
      ├── atlas/
      ├── wal/
      ├── operational_logs/
      └── questor_blackbox/
```

Wichtig:

`data/questor_blackbox/` liegt bewusst außerhalb von:

- `data/archiv/`
- `data/atlas/`
- `data/operational_logs/`

---

# 6. Definition produktiver Quellen und Naming-Allowlist

## 6.1 Produktive Quellen

Für Naming-Tests gelten als produktive Quellen:

- `src/`
- `config.py`
- aktive Laufzeitkonfiguration
- aktive Pydantic-Modelle
- aktive Tests, soweit sie keine expliziten Migrations- oder Scan-Fixtures sind

## 6.2 Nicht produktive Quellen

Nicht als produktive Quellen gelten:

- Dokumentationen
- archivierte Spezifikationen
- Migrationsdokumente
- Testdateien, die Suchbegriffe für Naming-Tests enthalten
- explizite Allowlist-Dateien unter `tests/migration_allowlist/`

## 6.3 Verbotene produktive Altbezeichnungen

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

## 6.4 Allowlist-Format

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

# 7. Datenverträge

Die folgenden Verträge sind verbindlich.

---

## 7.1 ResearchPackage

```text
ResearchPackage:
  package_id: str
  source_wegmarke: str
  source_wegmarke_version: Optional[str]
  atlas_version_ref: str
  ziel: str
  materials_or_resources: list[str]
  parameter_bounds: dict[str, tuple[float, float]]
  routing_graph: RoutingGraph
  gefahren_mitigationen: list[str]
  kontext: PackageKontext
  dimension_expansion_approval: Optional[str]
  override_requested: bool
  limits: dict[str, float]
  expected_side_effects_or_failure_modes: list[str]
  domain_metadata: dict[str, any]
  questor_spec: Optional[QuestorSpec]
```

Regeln:

- `routing_graph.max_loop_iterations` ist Pflicht.
- `routing_graph.branch_condition_timeout` ist Pflicht.
- `dimension_expansion_approval` muss vor physischer Ausführung gültig sein.
- `questor_spec` ist optional.
- Wenn `questor_spec` fehlt, gelten die sicheren Defaults aus Abschnitt 7.2.

Zusätzliche ID-Regeln für Idempotenzkontexte:

- `package_id` muss dem Format  
  `^[A-Za-z0-9._-]{1,128}$`  
  genügen.
- `zyklus_id` muss dem Format  
  `^[A-Za-z0-9._-]{1,128}$`  
  genügen.
- Dadurch ist eine kanonische Idempotency-Key-Bildung ohne Escaping möglich.

---

## 7.2 QuestorSpec und sichere Defaults

```text
QuestorSpec:
  spec_version: str
  autonomy_level: STRICT | GUIDED | ADAPTIVE
  objective_type: Optional[OPTIMIZE | EXPLORE | VALIDATE | DIAGNOSE | SIMULATE_ONLY | CLARIFY]
  clarity_threshold: float
  allowed_capabilities: list[Capability]
  allowed_loop_templates: list[str]
  budget: BudgetSpec
  fallback_policy: list[FallbackRule]
  llm_usage: LLMUsagePolicy
  blackbox_policy: BlackboxPolicy
  initial_trail_policy: InitialTrailPolicy
  operational_metrics_export: allowed | forbidden
```

Wenn `questor_spec` fehlt, gilt folgende Default-Instanz:

```text
DefaultQuestorSpec:
  spec_version: "0.2.3"
  autonomy_level: STRICT
  objective_type: null
  clarity_threshold: 0.9
  allowed_capabilities: []
  allowed_loop_templates: []
  budget:
    max_duration_s: 3600
    max_energy_budget: 1.0
    max_retry_count: 2
    max_llm_calls: 3
  fallback_policy:
    - SANDBOX_IF_UNCLEAR
    - ABORT_IF_NO_SAFE_MODE
  llm_usage:
    advisor_only: true
    max_calls: 3
    timeout_s: 30
    reject_unverified_safety_claims: true
  blackbox_policy:
    write_local: true
    transfer_to_gremium: false
    redaction_level: STRONG
  initial_trail_policy:
    create_trails: false
    require_evidence: true
  operational_metrics_export: allowed
```

### 7.2.1 Bedeutung der leeren Defaults

Die leeren Listen sind bewusst restriktiv:

```text
allowed_capabilities: []
allowed_loop_templates: []
```

Bedeutung:

- Ohne explizite Freigabe sind keine Capabilities aktiv.
- Ohne explizite Freigabe sind keine Loop-Templates aktiv.
- Die Default-Instanz ist fail-closed.
- Die Default-Instanz erlaubt keine physische Ausführung bei Unklarheit.
- Die Default-Instanz bevorzugt sichere Simulation oder sicheren Abbruch, sofern konfiguriert.

---

## 7.3 QuestorDispatchEnvelope

Bevorzugter und produktiver Eingang für Questor.

```text
QuestorDispatchEnvelope:
  dispatch_id: str
  zyklus_id: str
  attempt_id: int
  package: ResearchPackage
  gate_record_ref: str
  gate_mode: Optional[NORMAL | FRACTURE_DIAGNOSIS | HIGH_RISK_OVERRIDE | SANDBOX]
  lease_grants: list[LeaseGrant]
  execution_environment_ref: Optional[str]
  dispatch_mode: NORMAL | RETRY | RECOVERY
  security_mode: NORMAL | SANDBOX | DEV_SANDBOX_ONLY | RECOVERY
  dispatch_timestamp: str
  idempotency_key: str
```

Pflichtregeln:

- `gate_record_ref` ist Pflicht.
- `gate_mode` darf nicht im Widerspruch zum Gate Record stehen.
- `lease_grants` müssen konsistent sein.
- `security_mode` muss zu Gate und Leases passen.
- Wenn `gate_record_ref` fehlt:
  - `abbruch_grund = PACKAGE_INVALID`
  - `abbruch_klasse = OPERATIONAL`

---

## 7.4 QuestorErgebnisPaket

```text
QuestorErgebnisPaket:
  package_id: str
  zyklus_id: str
  attempt_id: int
  idempotency_key: str
  questor_instance_id: str
  sequence_number: int
  observed_atlas_version_id: str
  status: erfolgreich | fehlgeschlagen | abgebrochen
  abbruch_grund: Optional[str]
  abbruch_klasse: OPERATIONAL | SCIENTIFIC | SAFETY
  routing_checkpoint: RoutingCheckpoint
  ergebnis_daten: ErgebnisDaten
  validierung: GuardianValidierung
  kristall_kandidaten: list[KristallKandidat]
  gefahren_beobachtet: list[str]
  signale_fuer_atlas: list[SignalEvent]
  vollstaendig_flag: bool
  rohdaten_checksumme: str
  questor_metadata: Optional[QuestorMetadata]
```

### 7.4.1 Kanonischer Idempotency-Key

Der `idempotency_key` wird kanonisch wie folgt gebildet:

```text
idempotency_key = package_id + ":" + zyklus_id + ":" + attempt_id
```

Regeln:

- `package_id` und `zyklus_id` enthalten nur Zeichen aus `A-Z`, `a-z`, `0-9`, `.`, `_`, `-`.
- `package_id` und `zyklus_id` sind jeweils 1 bis 128 Zeichen lang.
- `attempt_id` ist eine Ganzzahl.
- `attempt_id >= 0`.
- `attempt_id <= 999999`.
- `attempt_id` wird als einfache Dezimalzahl ohne führende Nullen serialisiert.
- Es wird keine zusätzliche Whitespace verwendet.
- Die maximale Länge des `idempotency_key` beträgt 264 Zeichen.

Beispiel:

```text
pkg-001:zyklus-014:2
```

Wenn diese Regel verletzt wird:

- `abbruch_grund = PACKAGE_INVALID`
- `abbruch_klasse = OPERATIONAL`

### 7.4.2 Testvektoren für Idempotenz

Gültige Beispiele:

```text
pkg-001:zyklus-014:0
pkg-001:zyklus-014:2
abc.def_1:zyklus-99:10
```

Ungültige Beispiele:

```text
pkg 001:zyklus-014:2
pkg/001:zyklus-014:2
pkg-001:zyklus/014:2
pkg-001:zyklus-014:02
pkg-001:zyklus-014:
pkg-001:zyklus-014:1000000
```

Bemerkung:

- `pkg-001:zyklus-014:02` ist als kanonische Form ungültig, weil führende Nullen verboten sind.
- Wenn `attempt_id` als Integer verarbeitet wird, ist die kanonische Ausgabe für `2` immer `2`, nicht `02`.

### 7.4.3 Semantik von `abbruch_klasse`

`abbruch_klasse` ist Pflichtfeld.

Für die Zielversion gilt:

- Bei `status: erfolgreich`:
  - `abbruch_grund = null`
  - `abbruch_klasse = OPERATIONAL`
- Bei `status: fehlgeschlagen`:
  - `abbruch_grund` muss gesetzt sein
  - `abbruch_klasse` muss gesetzt sein
- Bei `status: abgebrochen`:
  - `abbruch_grund` muss gesetzt sein
  - `abbruch_klasse` muss gesetzt sein

Klarstellung:

`abbruch_klasse` ist fachlich als **Ergebnis- und Klassifikationsklasse** zu verstehen, nicht ausschließlich als wörtliche „Abbruchklasse“.

Eine spätere Umbenennung in z. B. `ergebnis_klasse` oder `outcome_class` wird für eine zukünftige Major-Version empfohlen, ist aber in v2.4.0 nicht mehr vorgesehen, um Vertragsstabilität zu wahren.

---

## 7.5 QuestorMetadata

```text
QuestorMetadata:
  questor_version: str
  policy_version: str
  local_audit: Optional[LocalAuditRef]
  operational_metrics: Optional[OperationalMetrics]
```

Regeln:

- Das Gremium darf `questor_metadata` ignorieren.
- `local_audit` enthält keine Blackbox-Inhalte.
- `operational_metrics` dürfen ausschließlich operational verwendet werden.
- `questor_metadata` erzeugt keine Kristalle.
- `questor_metadata` erzeugt keine wissenschaftlichen Signale.

---

## 7.6 LocalAuditRef

```text
LocalAuditRef:
  blackbox_id: str
  manifest_checksum: str
  blackbox_digest: str
  redaction_level: NONE | BASIC | STRONG
  retention_class: NORMAL | SAFETY_HOLD | DEVELOPMENT_HOLD
  access_policy_summary: str
```

Regeln:

- Kein Pfad, der automatisch vom Gremium gelesen wird.
- Keine Übergabe der Blackbox selbst.
- Nur Referenz, Digest und Policy-Zusammenfassung.

---

## 7.7 OperationalMetrics

```text
OperationalMetrics:
  oom_count: int
  timeout_count: int
  lease_wait_time_s: float
  lease_denied_count: int
  lease_queued_timeout_count: int
  capability_retry_count: int
  hal_command_duplicate_blocked_count: int
  llm_advice_rejected_count: int
  llm_advice_timeout_count: int
  branch_condition_unresolved_count: int
  recovery_attempts: int
  recovery_lock_denied_count: int
```

Regeln:

- Diese Metriken sind rein operational.
- Sie dürfen nicht als wissenschaftliche Evidenz interpretiert werden.
- Sie dürfen in `operational_event_log` einfließen, sofern konfiguriert.

---

# 8. Komponenten und Verantwortlichkeiten

## 8.1 Archivar

Der Archivar empfängt ausschließlich:

- `questor_ergebnis_paket`

Pflichten:

- prüft `idempotency_key`
- prüft `sequence_number` pro `questor_instance_id`
- prüft `vollstaendig_flag`
- trennt `abbruch_klasse`
- schreibt Kristalle nur aus validierten wissenschaftlichen Ergebnissen
- schreibt keine wissenschaftlichen Signale bei `OPERATIONAL`
- darf `operational_metrics` operational protokollieren
- liest keine QuestorBlackbox
- übernimmt `questor_metadata` nicht wissenschaftlich

Verbote:

- keine Blackbox lesen
- keine Questor-internen Trails interpretieren
- keine operationale Fehlerklasse als wissenschaftliches Signal behandeln

---

## 8.2 Dispatcher

Der Dispatcher erzeugt produktiv:

- `QuestorDispatchEnvelope`

Input:

- `research_package`
- `gate_record`
- `lease_grants`
- `execution_environment_ref`
- `dispatch_mode`
- `security_mode`

Vor Dispatch prüfen:

- `gate_record.signature`
- `lease_status = GRANTED` oder kontrolliert `QUEUED`
- Heartbeat/TTL
- Slot-Zustand
- Routing-Limits vorhanden
- Dimensions-Approval vorhanden, falls physisch
- `security_mode` passend

Verbote:

- kein produktiver Versand ohne `gate_record_ref`
- kein produktiver Versand ohne gültige Lease-Logik
- keine direkte physische Ausführung ohne Envelope

---

## 8.3 Receiver

Der Receiver empfängt:

- `questor_ergebnis_paket`

Er darf:

- Vertrag validieren
- Idempotenz prüfen
- Sequence prüfen
- an Archivar übergeben

Er darf nicht:

- Blackbox lesen
- Questor-interne Trails interpretieren
- wissenschaftliche Signale eigenmächtig umschreiben
- alte Vertragsformen akzeptieren

---

## 8.4 Questor

Questor ist das paketgebundene Execution Subsystem.

Questor darf:

- ein Paket ausführen
- HAL-Kommandos innerhalb gültiger Leases senden
- ein vollständiges `questor_ergebnis_paket` erzeugen
- lokale Blackbox schreiben

Questor darf nicht:

- in Atlas schreiben
- in Archiv schreiben
- Leases vergeben
- ESTOP zurücksetzen
- Gate-Freigaben erteilen
- globale Signale setzen
- finale LLM-Entscheidungen treffen

---

## 8.5 DummyQuestor

Für Trockenlauf und Integrationstests kann ein vertragstreuer Dummy verwendet werden.

Der Dummy muss:

- `QuestorDispatchEnvelope` akzeptieren
- `questor_ergebnis_paket` zurückgeben
- Early-Abort Complete Result respektieren
- `DIRECT_PACKAGE_FORBIDDEN` liefern, wenn direkte Übergabe unzulässig ist
- ESTOP, LEASE_DENIED und operative Fehler korrekt klassifizieren
- keine Blackbox an das Gremium übergeben

Der Dummy darf nicht:

- alte Black Box emulieren
- produktive Adapterlogik darstellen
- Atlas oder Archiv schreiben
- ESTOP zurücksetzen

---

## 8.6 Circuit Breaker

Der Circuit Breaker wird in v2.4.0 als explizite Zustandsmaschine geführt.

Zustände:

```text
NORMAL
SHADOW_MODE
TEMP_SUSPENDED
PERMANENT_SUSPENDED
```

### 8.6.1 Messfenster und Stichprobe

Empfohlene verbindliche Parameter:

```text
window_size = 100
minimum_sample_size = 20
max_window_age_days = 28
```

Regeln:

- Metriken werden über ein gleitendes Fenster berechnet.
- Automatische Zustandswechsel erfolgen nur, wenn `minimum_sample_size` erreicht ist.
- Bei zu kleiner Stichprobe darf höchstens ein Alert, aber kein automatischer Sicherheitszustandswechsel ausgelöst werden.

### 8.6.2 Schwellwerte

```text
invalid_veto_rate > 0.3 → Alert an Kanzler
false_block_rate > 0.5 → SHADOW_MODE
appeal_success_rate > 0.7 → TEMP_SUSPENDED
```

### 8.6.3 Hysterese und Rückkehr

Rückkehr nach `NORMAL` erfordert:

- Metrik liegt in zwei aufeinanderfolgenden Fenstern unter dem jeweiligen Schwellwert.
- Manuelle Prüfung durch Kanzler oder dafür vorgesehenen Sicherheitsprozess.
- Audit-Event für die Rückkehr.

`PERMANENT_SUSPENDED`:

- wird nur manuell durch Kanzler oder menschliche Königin ausgelöst
- hat keine automatische Rückkehr
- erfordert expliziten Audit-Trail

### 8.6.4 Audit-Felder für Zustandswechsel

Mindestfelder:

```text
old_state
new_state
trigger
metric_name
metric_value
window_size
sample_size
timestamp
authority
```

---

## 8.7 Kanzler und Policy-Veto-Review

Der Kanzler führt Policy-Veto-Reviews durch.

Konfigurationsparameter:

```text
policy_veto_review_interval_cycles = 20
```

### 8.7.1 Wertebereich

```text
policy_veto_review_interval_cycles: int
minimum: 1
maximum: 500
default: 20
```

`0` ist nicht erlaubt.

### 8.7.2 Persistenz

- Der Review-Zähler wird persistent geführt.
- Ein Neustart setzt den Zähler nicht zurück.
- SAFE_MODE kann die Zählung pausieren, setzt sie aber nicht zurück.

### 8.7.3 Review-Entscheidungen

Review kann:

- bestätigen
- aufheben
- eskalieren

### 8.7.4 Audit-Event

Jeder Review erzeugt ein Audit-Event:

```text
policy_veto_review
```

Mindestfelder:

```text
event_type
zyklus_id
policy_veto_id
review_decision
review_reason
review_timestamp
review_authority
escalation_target
```

---

## 8.8 Resource Governor

Resource Governor ist zuständig für:

- Slot-Mutex
- Lease-Vergabe
- Lease-TTL
- Heartbeat
- Pfad-Leases
- Fairness/Aging
- ESTOP-Behandlung auf Lease-Ebene

Resource Governor darf nicht:

- Hardwarekommandos direkt ausführen
- wissenschaftliche Entscheidungen treffen
- Questor-Logik ersetzen
- ESTOP ohne Sicherheitsgrund auslösen

---

# 9. HAL-Minimalvertrag bis zur separaten HAL-Datei

Dieser Abschnitt ist eine präzisierte Vorstufe.

Die vollständige HAL-Spezifikation folgt später als separate Datei, z. B.:

```text
hal_v2.4.0.md
```

Diese Datei darf den HAL-Minimalvertrag präzisieren, aber nicht sicherheitswidrig abschwächen.

---

## 9.1 HAL-Grundprinzipien

HAL ist:

- die einzige Hardware-Schnittstelle
- nicht lease-vergebend
- nicht sicherheitsentscheidend über dem Gremium
- testbar über Dummy-HAL
- deterministisch und hardwarenah
- kein wissenschaftlicher Interpreter

HAL darf nicht:

- Leases vergeben
- wissenschaftliche Signale erzeugen
- Atlas oder Archiv schreiben
- Questor-Logik ersetzen
- ESTOP eigenmächtig zurücksetzen
- Blackbox-Inhalte an das Gremium weitergeben

---

## 9.2 Minimale HAL-Funktionen

HAL muss mindestens bereitstellen:

```text
get_environment_manifest() -> EnvironmentManifest
get_slot_state(slot_id) -> SlotState
execute_command(command: HALCommand) -> HALCommandResult
report_estop(reason: str) -> EstopState
get_estop_state() -> EstopState
reconcile_slot_state(slot_id) -> SlotState
```

---

## 9.3 EnvironmentManifest

```text
EnvironmentManifest:
  environment_id: str
  environment_version: str
  schema_version: str
  slots: list[SlotDescriptor]
  slot_mutex_table: dict[str, list[str]]
  capabilities: list[str]
  estop_mechanism: str
  max_command_timeout_s: float
  default_lease_ttl_s: float
  heartbeat_interval_s: float
  supported_security_modes: list[str]
```

Regeln:

- Keine wissenschaftlichen Daten.
- Keine Atlas-Inhalte.
- Keine Paketinhalte.
- Nur technische Umgebung.

---

## 9.4 SlotState

```text
SlotState:
  slot_id: str
  status: FREE | RESERVED | ACTIVE | ERROR | ESTOP_SUSPENDED | MAINTENANCE | OFFLINE
  current_lease_ref: Optional[str]
  heartbeat_expires_at: Optional[str]
  last_error: Optional[str]
  last_command_id: Optional[str]
  last_state_change_at: str
```

---

## 9.5 HALCommand

```text
HALCommand:
  command_id: str
  idempotency_key: str
  lease_ref: str
  slot_id: str
  capability: str
  operation: str
  parameters: dict[str, any]
  timeout_s: float
  dispatch_mode: NORMAL | RETRY | RECOVERY
  security_mode: NORMAL | SANDBOX | DEV_SANDBOX_ONLY | RECOVERY
```

Regeln:

- `HALCommand` enthält keine wissenschaftlichen Ziele.
- `HALCommand` enthält nur technische Ausführungsparameter.
- `lease_ref` muss gültig oder überprüfbar sein.
- `command_id` muss eindeutig sein.

---

## 9.6 HALCommandResult

```text
HALCommandResult:
  command_id: str
  status: SUCCESS | DENIED | TIMEOUT | ESTOP | ERROR | DUPLICATE_BLOCKED | LEASE_INVALID | LEASE_EXPIRED | SLOT_UNAVAILABLE
  error_code: Optional[str]
  error_class: Optional[OPERATIONAL | SAFETY]
  slot_state: SlotState
  started_at: Optional[str]
  finished_at: Optional[str]
  receipt_checksum: Optional[str]
  operational_metrics: Optional[dict[str, float]]
```

---

## 9.7 EstopState

```text
EstopState:
  state: NORMAL | ACTIVE | LATCHED | TEST
  reason: Optional[str]
  trigger_source: Optional[str]
  affected_slots: list[str]
  suspended_leases: list[str]
  timestamp: str
  reset_policy: str
  acknowledged_by: Optional[str]
```

---

## 9.8 HAL-Fehlermodell

HAL-Fehler sind strikt zu klassifizieren.

### Operationale Fehler

```text
LEASE_INVALID
LEASE_EXPIRED
LEASE_REVOKED
SLOT_BUSY
SLOT_UNAVAILABLE
COMMAND_TIMEOUT
DEVICE_UNAVAILABLE
OOM
HAL_INTERNAL_ERROR
DUPLICATE_COMMAND_BLOCKED
```

### Sicherheitsfehler

```text
ESTOP_RECEIVED
SAFETY_LIMIT_VIOLATION
UNSAFE_SLOT_STATE
PHYSICAL_INTERLOCK_TRIGGERED
```

HAL darf keine wissenschaftlichen Fehlerklassen melden, wie z. B.:

```text
TARGET_NOT_REACHED
HYPOTHESIS_FAILED
SCIENTIFIC_CONTRADICTION
```

---

## 9.9 ESTOP-Semantik

Zustände:

```text
NORMAL
ACTIVE
LATCHED
TEST
```

Bei `ACTIVE` oder `LATCHED`:

- keine neuen Kommandos ausführen
- aktive Kommandos kontrolliert stoppen
- betroffene Leases auf `ESTOP_SUSPENDED`
- Questor erhält Sicherheitsabbruch
- Resource Governor wird informiert
- Audit-Log wird geschrieben

Reset:

- nicht durch Questor
- nicht durch LLM
- nur durch autorisierten Sicherheitsprozess oder menschliche Freigabe
- immer mit Audit-Event

---

## 9.10 HAL-Idempotenz

HAL sollte Kommandos idempotent behandeln.

Empfehlung:

```text
hal_idempotency_key = command_id
```

oder stärker:

```text
hal_idempotency_key = command_id:lease_ref:slot_id
```

Regeln:

- Ein bereits ausgeführtes Kommando darf nicht erneut ausgeführt werden.
- Ein blockiertes Duplikat sollte als `DUPLICATE_BLOCKED` gemeldet werden.
- Idempotenz ist besonders wichtig nach Crash, Timeout oder Recovery.

---

## 9.11 Crash-Recovery und Reconciliation

Nach Crash gilt:

- kein blinder Retry
- Slot-Zustand prüfen
- letzten Kommandostatus prüfen
- nur fortsetzen, wenn Zustand eindeutig ist
- bei Unklarheit operational abbrechen oder sicher in Wartestellung gehen

`reconcile_slot_state(slot_id)` dient dazu, einen Slot-Zustand nach unklarem Crash zu klären.

---

## 9.12 HAL-Logging

HAL protokolliert operational.

Empfohlene Events:

```text
command_received
command_accepted
command_denied
command_started
command_finished
command_timeout
estop_triggered
estop_acknowledged
lease_validation_failed
slot_state_changed
```

Diese Logs gehören nach:

```text
data/operational_logs/
```

Nicht nach:

```text
data/archiv/
data/atlas/
data/questor_blackbox/
```

---

## 9.13 Dummy-HAL

Dummy-HAL muss für Tests simulieren können:

- erfolgreiche Ausführung
- `LEASE_DENIED`
- `LEASE_EXPIRED`
- `ESTOP`
- `OOM / Compute-Crash`
- Slot-Konflikte
- Timeout-Szenarien
- `DUPLICATE_BLOCKED`
- unklaren Crash-Recovery-Zustand

Dummy-HAL darf keine echte Hardware ansprechen.

---

## 9.14 HAL-Datenfluss

Vereinfachter Datenfluss:

```text
Resource Governor
       |
       | LeaseGrant
       v
Gremium / Dispatcher
       |
       | QuestorDispatchEnvelope
       v
     Questor
       |
       | HALCommand + lease_ref
       v
   HAL Interface
       |
       | LeaseValidationRequest
       +----> Resource Governor
       |
       | DeviceCommand
       v
Device Adapter / Dummy
       |
       v
Physis / Compute
       |
       | DeviceResult / DeviceError
       v
   HAL Interface
       |
       | HALCommandResult
       v
     Questor
       |
       | QuestorErgebnisPaket
       v
Gremium / Receiver / Archivar

HAL kann zusätzlich:
  EstopEvent -> Resource Governor
  EstopEvent -> Questor
  OperationalAudit -> Operational Logs
```

---

# 10. Sicherheitsarchitektur

## 10.1 MYRMEX-Seite

Weiterhin gültig:

- Richter deterministisch
- Seher LLM-basiert
- Seher schreibt niemals direkt rote Signale
- Veto nur mit Evidenz
- Berufung über Kanzler
- Circuit-Breaker bleibt aktiv
- SAFE_MODE schützt menschliche Königin
- Fail-Closed bei Regellücken

## 10.2 Questor-Seite

Zusätzlich verbindlich:

- keine physische Ausführung ohne Envelope
- keine physische Ausführung ohne Gate
- keine physische Ausführung ohne Lease
- keine Umgehung von forbidden_modes
- keine finale LLM-Entscheidung
- keine direkte Atlas-Schreiberei
- keine Blackbox-Übergabe an das Gremium

## 10.3 HAL-Seite

- Hardwarezugriff nur über HAL
- keine Ausführung ohne gültige Lease-Referenz
- ESTOP stoppt aktive Kommandos
- ESTOP suspendiert betroffene Leases
- Ressourcenkonflikte bleiben operational
- HAL bleibt deterministic-first

---

# 11. ESTOP vs LEASE_DENIED

| Fall | Bedeutung | Klasse | Folge |
|---|---|---|---|
| LEASE_DENIED | Ressource belegt | OPERATIONAL | warten, neu planen oder operational abbrechen |
| ESTOP | physikalische Gefahr | SAFETY | stoppen, Leases suspendieren, Sicherheitsprüfung |

Ein Ressourcenkonflikt ist niemals ein ESTOP.

---

# 12. Blackbox-Isolation

Questor schreibt eine lokale Blackbox.

Diese ist:

- paketlokal
- nicht gremiumsöffentlich
- nicht Teil des Archivs
- nicht Teil des Atlas
- nicht Teil der operationalen Logs
- nur für Entwickler-/Notfallzugriff gedacht

Das Gremium darf maximal erhalten:

- `LocalAuditRef`

Es darf niemals erhalten:

- komplette Blackbox
- Questor-interne Trails
- interne Entscheidungsrohdaten als direkte Quelle

---

# 13. Implementierungs- und Migrationsphasen

Die folgende Struktur gilt sowohl für Migration als auch für sauberen Neuaufbau.

---

## Phase M0: Archivierung und Schnitt

Ziel:

- alte Referenz archivieren
- neue Referenz aktivieren
- keine Adapter einplanen
- Dokumentenhierarchie klären

Aufgaben:

- `structure_standalone_v2.3.1.md` als archiviert markieren
- diese Datei als primäre Referenz bestätigen
- `structure_standalone_questor_v0.2.3.md` als unterstützend einordnen
- sicherstellen, dass keine produktive Adapterlogik geplant ist

Akzeptanz:

- keine aktive Doppelreferenz
- keine produktiven Altbezeichnungen geplant
- keine Adapter geplant
- Konflikthierarchie dokumentiert

---

## Phase M1: Vertrags-Umbenennung

Ziel:

- neue Vertragswelt sauber einführen

Aufgaben:

- neue Ergebnis- und Instanzbezeichnungen einführen
- `QuestorDispatchEnvelope` einführen
- `QuestorMetadata`, `LocalAuditRef`, `OperationalMetrics` definieren
- kanonischen `idempotency_key` implementieren
- QuestorSpec-Defaults implementieren
- Circuit-Breaker-Zustände explizit machen
- Policy-Veto-Review-Parameter konfigurierbar machen

Akzeptanz:

- keine alten Bezeichnungen in aktiven Zielquellen
- neue Pydantic-Modelle existieren
- `idempotency_key` ist kanonisch
- `attempt_id` ist eingeschränkt
- mindestens 25 Vertragstests

---

## Phase M2: Archivar auf Questor-Ergebnis umstellen

Ziel:

- Archivar verarbeitet ausschließlich das neue Ergebnis

Aufgaben:

- Sequence-Prüfung auf `questor_instance_id`
- `questor_metadata` optional verarbeiten
- `operational_metrics` nur operational verwenden
- keine Blackbox-Zugriffe

Akzeptanz:

- valide Questor-Ergebnisse werden akzeptiert
- Duplikate werden verworfen
- OPERATIONALE Abbrüche erzeugen keine wissenschaftlichen Signale
- mindestens 20 Archivar-Integrationstests

---

## Phase M3: Dispatcher und Receiver umstellen

Ziel:

- produktiver Envelope-basierter Dispatch
- sauberer Empfang des neuen Ergebnisses

Aufgaben:

- Dispatcher baut Envelope
- Dispatcher prüft Gate, Lease, Security-Mode
- Receiver empfängt neues Ergebnis
- direkte Paketübergaben nur sandbox/dev

Akzeptanz:

- Dispatcher sendet keine nackten Produktivpakete
- Envelope enthält `gate_record_ref`
- Receiver validiert Vertrag
- mindestens 20 Dispatcher/Receiver-Tests

---

## Phase M4: Questor-Implementierung oder Questor-Dummy

Ziel:

- Questor oder vertragstreuer Dummy ist vorhanden

Aufgaben:

- entweder vollständige Questor-Implementierung gemäß v0.2.3
- oder DummyQuestor für Integrationstests

Akzeptanz:

- Questor/Dummy empfängt Envelope
- liefert neues Ergebnis
- keine direkten Atlas-/Archivzugriffe
- Blackbox bleibt lokal
- ESTOP, LEASE_DENIED, ROUTING_LOOP_TIMEOUT, SCIENTIFIC/OPERATIONAL werden korrekt getrennt

---

## Phase M5: Gesamtsystem-Tests

Ziel:

- vollständige Integrationstests ohne Adapter

Aufgaben:

- Suite N
- Suite I
- Suite S
- Suite R
- Suite Z aus der aktuellen Testdatei
- Questor-spezifische Sicherheits- und Blackbox-Tests

Akzeptanz:

- alle Tests bestehen
- keine aktiven Altbezeichnungen
- keine Adapter in finalen Tests
- Blackbox bleibt isoliert
- Operational bleibt ohne wissenschaftliches Signal

---

# 14. Neubaupfad für MYRMEX v2.4.0

Wenn kein Bestand migriert, sondern frisch aufgebaut wird, gelten die folgenden Phasen.

---

## Phase 1: Projekt-Setup + Datenverträge

Aufgaben:

- Repository-Struktur anlegen
- Requirements und Konfiguration erstellen
- alle Vertragsmodelle definieren

Akzeptanz:

- alle Modelle sind Pydantic-v2-konform
- alle Enums vorhanden
- Idempotenzregeln korrekt
- Routing-Graph enthält Pflichtfelder
- Gate-Modi vollständig
- mindestens 20 Unit-Tests

---

## Phase 2: Event-Sourcing + Archiv + Archivar

Aufgaben:

- Atlas-Event-Store
- Snapshots
- Recovery
- Archivar für neue Ergebnisse
- Signal-Registry
- Kristallisation und Verfall

Akzeptanz:

- Duplikate werden verworfen
- unvollständige Pakete werden nicht als Kristalle übernommen
- OPERATIONALE Abbrüche erzeugen keine wissenschaftlichen Signale
- Signal-Resolution korrekt
- mindestens 30 Unit-Tests

---

## Phase 3: Atlas + Kartograph

Aufgaben:

- DBSCAN/UMAP-Logik
- fracture_score
- Zone-Health
- FULL_REBUILD
- NEUAUSRICHTEN
- Seed-Zonen
- Atlas-Versionierung

Akzeptanz:

- unbekannte Dimensionen werden nicht als null oder 0 behandelt
- FULL_REBUILD atomar
- alte Atlas-Version bleibt für laufende Quests gültig
- mindestens 40 Unit-Tests

---

## Phase 4: Transaktions-Schicht

Aufgaben:

- WAL
- State Machine
- Recovery
- Crash-Sicherheit

Akzeptanz:

- Recovery setzt Pakete in die korrekte Stufe zurück
- keine übersprungenen Phasen
- Lease-TTL wird beachtet
- mindestens 25 Unit-Tests

---

## Phase 5: Resource Governor + HAL-Vertrag

Aufgaben:

- Slot-Manager
- Governor
- ESTOP-Handler
- HAL-Interface
- Dummy-HAL

Akzeptanz:

- zwei Pakete können nicht denselben Slot gleichzeitig belegen
- LEASE_DENIED löst keinen ESTOP aus
- ESTOP suspendiert betroffene Leases
- Pfad-Leases funktionieren
- mindestens 30 Unit-Tests

---

## Phase 6: Sicherheits-Gate

Aufgaben:

- Richter
- Seher
- Circuit-Breaker
- Berufungsprozess
- Gate-Record

Akzeptanz:

- Richter fail-closed
- Seher ohne Evidenz → invalid veto
- Seher erzeugt niemals direkt rote Signale
- Circuit-Breaker greift
- mindestens 35 Unit-Tests

---

## Phase 7: Ideen-Pipeline

Aufgaben:

- Vordenker
- Pre-Filter
- Lotse
- blocked_cache
- Pheromon-Gating
- QUARANTÄNE-Regeln

Akzeptanz:

- adaptive Temperatur mit Obergrenze
- UNKNOWN-Dimensionen werden nicht hart verworfen
- Signal-Stack wird geprüft
- QUARANTÄNE erlaubt nur diagnostische Wegmarken
- mindestens 35 Unit-Tests

---

## Phase 8: Paket-Bau + Dispatch

Aufgaben:

- Quartiermeister
- Dispatcher
- Receiver
- Questor-Interface
- DummyQuestor

Akzeptanz:

- korrekte Pakete aus Wegmarke
- Routing-Graph ist gerichtet
- Envelope wird gebaut
- Gate und Lease werden geprüft
- keine produktiven nackten Paketübergaben
- mindestens 25 Unit-Tests

---

## Phase 9: Kanzler + Königin-Interface

Aufgaben:

- Lagebericht
- Weisungsprüfung
- SAFE_MODE
- policy_veto_review
- Audit-Log

Akzeptanz:

- menschliche Königin wird niemals überstimmt
- SAFE_MODE funktioniert
- LLM-Königin-Fallback greift nach Konflikten
- Review nach definierten Zyklen
- mindestens 20 Unit-Tests

---

## Phase 10: Pipeline-Orchestrierung + End-to-End Integration

Aufgaben:

- Orchestrator
- Event-Steuerung
- bounded queues
- Deadlock-Erkennung
- alle Integrationstests

Akzeptanz:

- alle Pflichttests bestehen
- keine Endlosschleifen
- keine Deadlocks
- keine Blackbox im Gremium
- mindestens 12 Integrationstests

---

# 15. Verbotene Patterns

Die folgenden Patterns sind in der Zielarchitektur verboten:

1. Questor schreibt direkt in den Atlas.
2. Questor schreibt direkt in das Archiv.
3. Questor liest globale Signal-Stacks.
4. Questor setzt ESTOP zurück.
5. Questor vergibt Leases.
6. Questor erzeugt rote Signale direkt.
7. Gremium liest QuestorBlackbox.
8. Dispatcher sendet produktiv ohne `gate_record_ref`.
9. Receiver erwartet alte Ergebnisformen.
10. Archivar prüft alte Instanz-ID-Felder.
11. Produktive Adapterlogik zwischen alter und neuer Welt.
12. Direkte physische Ausführung ohne Envelope.
13. Operational wird als Scientific interpretiert.
14. LEASE_DENIED wird als ESTOP behandelt.
15. Zwei gleichwertige primäre Referenzdateien ohne Konflikthierarchie.
16. HAL vergibt Leases.
17. HAL interpretiert wissenschaftliche Ziele.
18. HAL setzt ESTOP eigenmächtig zurück.

---

# 16. Akzeptanzkriterien für das Gesamtsystem

Nach Abschluss muss gelten:

- keine produktiven Altbezeichnungen
- MYRMEX v2.4.0 und Questor v0.2.3 sind konsistent
- neues Ergebnis wird vom Archivar korrekt verarbeitet
- Sequence-Prüfung nutzt `questor_instance_id`
- `idempotency_key` ist kanonisch definiert
- `attempt_id` ist vollständig eingeschränkt
- QuestorSpec-Defaults sind maschinenlesbar
- Circuit-Breaker-Zustände sind explizit
- Policy-Veto-Review ist konfigurierbar
- HAL-Minimalvertrag ist testbar
- QuestorBlackbox ist isoliert
- Operational bleibt ohne wissenschaftliches Signal
- ESTOP und LEASE_DENIED bleiben strikt getrennt
- Routing-Loop-Schutz funktioniert
- FRACTURE_DIAGNOSIS funktioniert
- Dimensions-Expansion bleibt approval-pflichtig
- SAFE_MODE bleibt menschlich sicher
- alle Test-Suiten bestehen

---

# 17. Erwartete Test-Suiten

Diese Struktur ist kompatibel mit einer Testdatei, die mindestens die folgenden Suites enthält:

- Suite N — Naming & Contract Migration
- Suite I — Integration
- Suite S — Szenario-Pflichttests
- Suite R — Regressions-Tests
- Suite Z — Zielpräzisierung

Empfohlene Mindestanzahlen:

```text
NAMING: 7 Tests
INTEGRATION: 18 Tests
SZENARIEN: 5 Tests
REGRESSION: 12 Tests
PRÄZISIERUNG: 8 Tests
GESAMT: 50 Tests
```

Wenn eine Testdatei zusätzliche HAL-Suite enthält, sollte diese später als Suite H geführt werden.

---

# 18. Status-Report-Template

Nach jeder Phase ist folgender Report zu erstellen:

```text
Phase: [Nummer]
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

# 19. Empfehlung für die Testreihenfolge

Empfohlene Reihenfolge:

1. Naming-/Vertragstests
2. Archivar-Receiver-Tests
3. Dispatcher-Envelope-Tests
4. Questor-Vertragstests
5. Questor-Sicherheitsregeln
6. Integrationstests
7. Szenario-Pflichttests A–E
8. Regressions-Tests aus v2.3.1
9. Präzisierungs-Tests
10. spätere HAL-Integrationstests nach separater HAL-Datei

---

# 20. Bewusst nicht in dieser Datei

Diese Datei enthält bewusst nicht:

- vollständige HAL-Implementierungsdetails
- vollständige Questor-Interna
- vollständige Testfälle aller Suites
- produktive Code-Beispiele
- Hardware-spezifische Gerätetreiber

Diese Inhalte folgen in separaten Dateien, insbesondere:

- Testdatei
- HAL-Datei
- ggf. Questor-Interna-Dokumentation