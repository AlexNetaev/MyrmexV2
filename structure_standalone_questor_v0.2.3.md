# 🧭 MYRMEX V2.4.0 + QUESTOR V0.2.3 — STANDALONE STRUKTURDATEI

**Version:** MYRMEX v2.4.0 + Questor v0.2.3  
**Status:** Bereit für Umbenennung, Migration und Integrationstests  
**Ersetzt:** `structure_standalone_v2.3.1.md`  
**Ansatz:** Kein Adapter. Sauberer Vertragsschnitt. Questor ersetzt die alte Black Box „Schwarm“.  
**Wichtig:** Diese Datei ist die neue Referenz für das Gesamtsystem. Alte Swarm-Begriffe sollen nicht weiterverwendet werden.

---

## TEIL 0: Anweisung für die implementierende oder migrierende KI

### Rolle

Du bist ein Senior Software Engineer / Systems Architect, der MYRMEX v2.4.0 und Questor v0.2.3 sauber integriert.

### Grundregeln

1. Arbeite phase-by-phase.
2. Kein Code für Phasen, die nicht freigegeben sind.
3. Keine Adapter zwischen alter Swarm- und neuer Questor-Welt, außer explizit als temporäres Migrationstool in einem eigenen Migrationstest.
4. Die Zielarchitektur kennt keine produktiven Swarm-Altbezeichnungen.
5. Verwende Python 3.10+, Pydantic v2, pytest.
6. Questor ist nicht die alte Phase-1-Kastenarchitektur.
7. Questor ersetzt die Black Box „Schwarm“ aus v2.3.1.
8. MYRMEX v2.4.0 kommuniziert mit Questor ausschließlich über die in TEIL 3 definierten Verträge.
9. Questor schreibt nicht direkt in Atlas oder Archiv.
10. QuestorBlackbox bleibt lokal und wird nicht an das Gremium übergeben.
11. Sicherheitsregeln sind fail-closed.
12. Operational ≠ Scientific bleibt strikt getrennt.
13. Menschliche Königin wird niemals überstimmt.
14. Leases kommen vom Resource Governor.
15. Hardwarezugriff läuft nur über HAL.

---

## TEIL 1: Zweck dieser Datei

Diese Datei definiert die neue integrierte Struktur von:

- MYRMEX Gremium v2.4.0
- Questor Execution Subsystem v0.2.3
- HAL / Resource Governor
- Questor-Interface
- Blackbox-Isolation
- Integrationstest-Voraussetzungen

Sie ersetzt die alte Anleitung `structure_standalone_v2.3.1.md`.

Der wichtigste Unterschied:

> Der „Schwarm“ ist keine undefinierte Black Box mehr, sondern wird durch Questor ersetzt.  
> Questor ist paketgebunden, domain-agnostisch, deterministic-first, sicherheitsfail-closed und blackbox-isoliert.

---

## TEIL 2: Breaking Changes gegenüber v2.3.1

Diese Änderungen sind bewusst breaking.

| v2.3.1 | v2.4.0 / Questor v0.2.3 |
|---|---|
| Schicht 2: Schwarm | Schicht 2: Questor Execution Subsystem |
| `swarm_ergebnis_paket` | `questor_ergebnis_paket` |
| `SwarmErgebnisPaket` | `QuestorErgebnisPaket` |
| `swarm_instance_id` | `questor_instance_id` |
| `MockSwarm` | `DummyQuestor` oder `MockQuestor` |
| `src/swarm_interface/` | `src/questor_interface/` |
| Dispatcher sendet `ResearchPackage` an MockSwarm | Dispatcher sendet `QuestorDispatchEnvelope` an Questor |
| Receiver empfängt `swarm_ergebnis_paket` | Receiver empfängt `questor_ergebnis_paket` |
| Schwarm ist Black Box | Questor ist spezifiziertes Subsystem |
| keine lokale QuestorBlackbox | QuestorBlackbox ist Teil von Questor, nicht Teil des Gremiums |

### Verbotene Mischformen

Die folgenden Mischformen sind in der Zielarchitektur unerwünscht:

```text
Questor liefert ein swarm_ergebnis_paket
Archivar prüft swarm_instance_id
package_dispatcher ruft MockSwarm auf
result_receiver erwartet SwarmErgebnisPaket
Questor wird als alter 9-Kasten-Schwarm interpretiert
```

Wenn solche Mischformen gefunden werden, müssen sie korrigiert werden.

---

## TEIL 3: System-Überblick

### 3.1 Die neue 6-Schichten-Architektur

| Schicht | Name | Verantwortung |
|---|---|---|
| 5 | 👑 Königin | Langfristige Vision, Meta-Ziele |
| 4 | 🏛️ Gremium | Intelligence, Atlas, Pakete, Sicherheit |
| 3 | ⚖️ Dispatch-Koordination | Dispatch-Queue, Lease-/Gate-Koordination |
| 2 | 🧭 Questor | Paketgebundenes Execution Subsystem |
| 1 | 🔌 HAL & Resource Governor | Slot-Routing, Leases, ESTOP |
| 0 | ⚙️ Physis / Compute | Hardware / Compute |

Hinweis:

Schicht 3 sollte nicht „Arbiter“ genannt werden, wenn Verwechslungsgefahr mit dem internen `QuestCompass` besteht.

Empfohlener Name:

```text
DispatchCoordinator
```

oder:

```text
Taskforce / Dispatch Coordinator
```

---

### 3.2 Die 9-Stufen-Pipeline bleibt grundsätzlich erhalten

Stufe 1: Wissens-Aufnahme  
Stufe 2: Atlas-Strukturierung  
Stufe 3: Strategische Review  
Stufe 4: Ideen-Generierung  
Stufe 5a: Pre-Filter  
Stufe 5b: Ideen-Erdung  
Stufe 6: Paket-Bau  
Stufe 7: Sicherheits-Gate  
Stufe 8: Dispatch & Execution  

Aber Stufe 8 ändert sich wesentlich:

Alt:

```text
Resource Governor → HAL → Schwarm
```

Neu:

```text
Resource Governor → HAL → Questor
```

und konkreter:

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

## TEIL 4: Kernregeln

### 4.1 Blackboard-Pattern

Alle Ränge des Gremiums kommunizieren weiterhin ausschließlich über Atlas und Archiv.

Keine direkten Aufrufe zwischen Rängen.

---

### 4.2 Questor ist kein Gremium-Rang

Questor darf nicht:

- in den Atlas schreiben
- in das Archiv schreiben
- Wegmarken erzeugen
- Ideen erzeugen
- Gate-Freigaben erteilen
- Leases vergeben
- ESTOP zurücksetzen
- globale Signale direkt schreiben

Questor darf nur:

- ein Paket ausführen
- HAL-Kommandos innerhalb gültiger Leases senden
- ein `questor_ergebnis_paket` erzeugen
- Signalvorschläge und Kristallkandidaten übergeben
- eine lokale QuestorBlackbox schreiben

---

### 4.3 Fail-Closed

Wenn etwas nicht sicher geprüft werden kann:

```text
keine Freigabe
keine physische Ausführung
kontrollierter Abbruch oder Eskalation
```

---

### 4.4 Operational ≠ Scientific

Weiterhin strikt:

| Klasse | Bedeutung | Wissenschaftliches Signal? |
|---|---|---:|
| `OPERATIONAL` | Prozessfehler, Crash, Timeout, Lease-Problem | nein |
| `SCIENTIFIC` | wissenschaftliche Zielverfehlung, empirischer Widerspruch | ja, als Vorschlag |
| `SAFETY` | Sicherheitsverletzung, ESTOP | ja, mit Sicherheitsprüfung |

---

### 4.5 Keine direkte physische Ausführung ohne Envelope

Physische Ausführung erfordert:

- gültiges `research_package`
- gültigen `QuestorDispatchEnvelope`
- `gate_record_ref`
- gültige `lease_grants`
- `security_mode` passend
- keine fehlende Dimensionsfreigabe

Direkte `ResearchPackage`-Übergaben sind standardmäßig sandbox-only.

---

## TEIL 5: Repository-Struktur v2.4.0

Empfohlene neue Struktur:

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
 │   │   ├── archivar.py
 │   │   ├── kartograph.py
 │   │   ├── kanzler.py
 │   │   ├── vordenker.py
 │   │   ├── pre_filter.py
 │   │   ├── lotse.py
 │   │   ├── quartiermeister.py
 │   │   ├── sicherheitsrat/
 │   │   └── pipeline_orchestrator.py
 │   ├── atlas/
 │   ├── transaction/
 │   ├── resource_governor/
 │   ├── hal/
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
 │   └── test_integration/
 └── data/
     ├── archiv/
     ├── atlas/
     ├── wal/
     ├── operational_logs/
     └── questor_blackbox/
```

Wichtig:

`data/questor_blackbox/` liegt bewusst außerhalb von:

```text
data/archiv/
data/atlas/
data/operational_logs/
```

---

## TEIL 6: Questor-Schnittstelle

Questor wird nicht mehr als „Schwarm“ angesprochen.

Questor erhält bevorzugt einen `QuestorDispatchEnvelope`.

---

## 6.1 ResearchPackage

`ResearchPackage` bleibt im Kern kompatibel, wird aber um optionale Questor-Felder erweitert.

```yaml
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

---

## 6.2 QuestorSpec

Optional.

```yaml
QuestorSpec:
  spec_version: "0.2.3"
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

Wenn `questor_spec` fehlt, gelten sichere Defaults.

---

## 6.3 QuestorDispatchEnvelope

Bevorzugter Eingang für Questor.

```yaml
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
- `security_mode` muss zum Gate und zu den Leases passen.
- Wenn `gate_record_ref` fehlt:

```yaml
abbruch_grund: PACKAGE_INVALID
abbruch_klasse: OPERATIONAL
```

---

## 6.4 QuestorErgebnisPaket

Neuer Name für das ehemalige `swarm_ergebnis_paket`.

```yaml
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

Wichtig:

`questor_instance_id` ersetzt `swarm_instance_id`.

---

## 6.5 QuestorMetadata

Optional.

```yaml
QuestorMetadata:
  questor_version: str
  policy_version: str
  local_audit: Optional[LocalAuditRef]
  operational_metrics: Optional[OperationalMetrics]
```

Regeln:

- Das Gremium darf `questor_metadata` ignorieren.
- `local_audit` enthält keine Blackbox-Inhalte.
- `operational_metrics` dürfen für `operational_event_log` genutzt werden.
- `questor_metadata` erzeugt keine wissenschaftlichen Signale.

---

## 6.6 LocalAuditRef

```yaml
LocalAuditRef:
  blackbox_id: str
  manifest_checksum: str
  blackbox_digest: str
  redaction_level: NONE | BASIC | STRONG
  retention_class: NORMAL | SAFETY_HOLD | DEVELOPMENT_HOLD
  access_policy_summary: str
```

Wichtig:

Kein Pfad, der automatisch vom Gremium gelesen wird.

Keine Übergabe der Blackbox selbst.

---

## 6.7 OperationalMetrics

```yaml
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

Diese Metriken sind operational.

Sie dürfen nicht als wissenschaftliche Evidenz interpretiert werden.

---

## TEIL 7: Archivar-Anpassung

Der Archivar empfängt ab sofort:

```text
questor_ergebnis_paket
```

nicht mehr:

```text
swarm_ergebnis_paket
```

### Pflichten des Archivars

- prüft `idempotency_key`
- prüft `sequence_number` pro `questor_instance_id`
- prüft `vollstaendig_flag`
- trennt `abbruch_klasse`
- schreibt Kristalle nur aus validierten wissenschaftlichen Ergebnissen
- schreibt keine wissenschaftlichen Signale bei `OPERATIONAL`
- darf `operational_metrics` in den operational_event_log übernehmen
- liest keine QuestorBlackbox

---

## TEIL 8: Dispatcher-Anpassung

Der `package_dispatcher` darf nicht mehr einfach ein `ResearchPackage` an einen Mock senden.

Er soll einen `QuestorDispatchEnvelope` bauen.

### Input für Dispatcher

- `research_package`
- `gate_record`
- `lease_grants`
- `execution_environment_ref`
- `dispatch_mode`
- `security_mode`

### Output

```text
QuestorDispatchEnvelope
```

### Vor Dispatch prüfen

- `gate_record.signature`
- `lease_status = GRANTED` oder kontrolliert `QUEUED`
- Heartbeat/TTL
- Slot-Zustand
- Routing-Limits vorhanden
- Dimensions-Approval vorhanden, falls physisch

---

## TEIL 9: Receiver-Anpassung

Der `result_receiver` empfängt:

```text
questor_ergebnis_paket
```

und leitet es an den Archivar weiter.

Er darf:

- Vertrag validieren
- Idempotenz prüfen
- Sequence prüfen
- an Archivar übergeben

Er darf nicht:

- Blackbox lesen
- Questor-interne Trails interpretieren
- wissenschaftliche Signale eigenmächtig umschreiben

---

## TEIL 10: Questor v0.2.3 — verbindliche Kernregeln

Die folgenden Regeln sind für Questor v0.2.3 verbindlich.

---

## 10.1 Deterministic-first

QuestCompass entscheidet final deterministisch.

LLM-Module dürfen nur beraten.

---

## 10.2 LLM nur Advisor

LLM darf nicht:

- Sicherheitsfreigaben erteilen
- Budgets ändern
- finale Template-Auswahl treffen
- HALCommands direkt auslösen
- Atlas-Signale schreiben
- ESTOP zurücksetzen
- Blackbox-Zugriffe freigeben
- Trails ohne Evidence erzeugen

---

## 10.3 QuestorBlackbox

Questor schreibt eine lokale Blackbox.

Diese ist:

- paketlokal
- nicht gremiumsöffentlich
- nicht Teil des Archivs
- nicht Teil des Atlas
- nur für Entwickler/Notfallzugriff gedacht

---

## 10.4 Fail-closed Regeln

Unbekannte BranchCondition → nicht nehmen.  
Unbekannter Template-Platzhalter → Template ungültig.  
Unklare Objective → keine physische Ausführung.  
Fehlende Dimensionsfreigabe → keine physische Ausführung.  
Fehlende Gate-Referenz → Abbruch.  
Unklarer HAL-Status nach Crash → kein blinder Retry.

---

## 10.5 Early-Abort Complete Result

Auch frühe Abbrüche müssen ein vollständiges `questor_ergebnis_paket` erzeugen.

Betroffene Fälle:

```text
PACKAGE_INVALID
DIRECT_PACKAGE_FORBIDDEN
GATE_MISSING
NO_APPLICABLE_TEMPLATE
NO_SAFE_MODE_AVAILABLE
LEASE_QUEUED_TIMEOUT
ROUTING_BRANCH_UNRESOLVED
TEMPLATE_PLACEHOLDER_UNRESOLVED
RECOVERY_UNSAFE
LEDGER_SERIALIZATION_FAILED
```

Wenn Felder nicht sinnvoll gefüllt werden können, müssen sichere Platzhalter verwendet werden.

---

## 10.6 Strict Output in v2.4.0

Da Myrmex v2.4.0 den neuen Vertrag besitzt, ist kein v2.3.1-Strict-Mode mehr nötig.

Aber:

> Das `questor_ergebnis_paket` darf nur Felder enthalten, die in v2.4.0 definiert sind.

Keine freien Zusatzfelder außerhalb von `questor_metadata`.

---

## TEIL 11: Questor-interne Clarifications v0.2.3

Questor v0.2.3 enthält zusätzlich zu v0.2.2 die folgenden Clarifications:

| ID | Thema |
|---|---|
| C13 | `not_in`, `exists`, `not_exists` canonicalisieren |
| C14 | `DIRECT_PACKAGE_FORBIDDEN` als expliziter Abbruchgrund |
| C15 | Genesis-Hash für ExpeditionLedger |
| C16 | `RESULT_FINALIZED` und Sequence-Atomarität |
| C17 | Recovery-Lock und stale Locks |
| C18 | NaN/Infinity im Ledger fail-closed |
| C19 | Template-Fehlerisolierung |
| C20 | Strict Output Compatibility Mode für Migration |
| C21 | Early-Abort Minimal Result Completeness |

Für MYRMEX v2.4.0 gilt:

- C20 ist nur relevant, falls temporär gegen v2.3.1 getestet wird.
- In der Zielarchitektur wird C20 durch den v2.4.0-Vertrag ersetzt.

---

## TEIL 12: Implementierungs- und Migrationsphasen

---

## Phase M0: Archivierung und Schnitt

### Aufgaben

- `structure_standalone_v2.3.1.md` als Altversion archivieren
- neue Datei `structure_standalone_questor_v0.2.3.md` zur Referenz machen
- alle alten Swarm-Begriffe identifizieren
- keine Adapter in Zielarchitektur einbauen

### Akzeptanzkriterien

- [ ] Alte v2.3.1-Datei ist als archiviert markiert.
- [ ] Neue v2.4.0/Questor-v0.2.3-Referenz ist aktiv.
- [ ] Keine produktive Adapter-Logik geplant.

---

## Phase M1: Vertrags-Umbenennung

### Aufgaben

- `SwarmErgebnisPaket` → `QuestorErgebnisPaket`
- `swarm_ergebnis_paket` → `questor_ergebnis_paket`
- `swarm_instance_id` → `questor_instance_id`
- `MockSwarm` → `DummyQuestor`
- `swarm_interface` → `questor_interface`
- neue Modelle für `QuestorDispatchEnvelope`, `QuestorMetadata`, `LocalAuditRef`, `OperationalMetrics`

### Akzeptanzkriterien

- [ ] Alle alten Swarm-Namen sind aus Zielquellen entfernt.
- [ ] Neue Pydantic-Modelle existieren.
- [ ] Idempotency-Key bleibt `package_id + zyklus_id + attempt_id`.
- [ ] Sequence-Prüfung nutzt `questor_instance_id`.
- [ ] Mindestens 25 Vertragstests.

---

## Phase M2: Archivar auf Questor-Ergebnis umstellen

### Aufgaben

- Archivar empfängt `questor_ergebnis_paket`
- Sequence-Prüfung auf `questor_instance_id`
- `questor_metadata` optional verarbeiten
- operational_metrics in operational_event_log übernehmen, falls konfiguriert
- keine Blackbox-Lesezugriffe

### Akzeptanzkriterien

- [ ] Archivar akzeptiert valide Questor-Ergebnisse.
- [ ] Duplikate werden verworfen.
- [ ] OPERATIONALE Abbrüche erzeugen keine wissenschaftlichen Signale.
- [ ] Mindestens 20 Archivar-Integrationstests.

---

## Phase M3: Dispatcher und Receiver umstellen

### Aufgaben

- Dispatcher baut `QuestorDispatchEnvelope`
- Dispatcher prüft Gate, Lease, Security-Mode
- Receiver empfängt `questor_ergebnis_paket`
- direkte `ResearchPackage`-Aufrufe nur sandbox/dev

### Akzeptanzkriterien

- [ ] Dispatcher sendet keine nackten Produktivpakete mehr.
- [ ] Envelope enthält `gate_record_ref`.
- [ ] Receiver validiert Vertrag.
- [ ] Mindestens 20 Dispatcher/Receiver-Tests.

---

## Phase M4: Questor-Implementierung oder Questor-Dummy

### Aufgaben

Entweder:

1. vollständige Questor-Implementierung gemäß Questor v0.2.3

oder für Integrationstests:

2. `DummyQuestor`, der vertragstreu reagiert.

### Akzeptanzkriterien

- [ ] Questor oder DummyQuestor empfängt `QuestorDispatchEnvelope`.
- [ ] Questor liefert `questor_ergebnis_paket`.
- [ ] Keine direkten Atlas-/Archivzugriffe.
- [ ] Blackbox bleibt lokal.
- [ ] ESTOP, LEASE_DENIED, ROUTING_LOOP_TIMEOUT, SCIENTIFIC/OPERATIONAL werden korrekt unterschieden.

---

## Phase M5: Gesamtsystem-Tests

### Aufgaben

- alle Tests aus `questor_myrmex_integration_addendum_v0.1.md`
- alte v2.3.1 Pflichttests in neuer Terminologie
- Szenarien A–E
- Questor-spezifische Sicherheits- und Blackbox-Tests

### Akzeptanzkriterien

- [ ] Alle Naming-/Vertragstests bestehen.
- [ ] Alle Integrationstests bestehen.
- [ ] Alle Regressions-Tests bestehen.
- [ ] Keine alten Swarm-Begriffe in aktiven Testpfaden.
- [ ] Keine Adapter in finalen Tests.

---

## TEIL 13: Sicherheitsarchitektur in v2.4.0

Die Sicherheitsarchitektur aus v2.3.1 bleibt grundsätzlich bestehen, wird aber um Questor-spezifische Regeln ergänzt.

---

## 13.1 Sicherheits-Gate

Weiterhin:

- Richter deterministisch
- Seher LLM-basiert
- Seher schreibt niemals direkt 🟥
- Veto nur mit Evidenz
- Berufung über Kanzler
- Circuit-Breaker bleibt

---

## 13.2 Questor-Sicherheit

Questor ergänzt:

- keine physische Ausführung ohne Envelope
- keine physische Ausführung ohne Gate
- keine physische Ausführung ohne Lease
- keine Umgehung von forbidden_modes
- keine finale LLM-Entscheidung
- keine direkte Atlas-Schreiberei
- keine Blackbox-Übergabe

---

## TEIL 14: Akzeptanzkriterien für das Gesamtsystem

Nach Abschluss der Migration und Integration muss gelten:

- [ ] Keine produktiven Swarm-Altbezeichnungen mehr.
- [ ] MYRMEX v2.4.0 und Questor v0.2.3 sind konsistent.
- [ ] `questor_ergebnis_paket` wird vom Archivar korrekt verarbeitet.
- [ ] `questor_instance_id` wird für Sequence-Prüfung genutzt.
- [ ] QuestorBlackbox ist isoliert.
- [ ] Operational bleibt ohne wissenschaftliches Signal.
- [ ] ESTOP und LEASE_DENIED bleiben strikt getrennt.
- [ ] Routing-Loop-Schutz funktioniert.
- [ ] FRACTURE_DIAGNOSIS funktioniert.
- [ ] Dimensions-Expansion bleibt approval-pflichtig.
- [ ] SAFE_MODE bleibt unverändert menschlich sicher.
- [ ] Alle Tests aus dem Integrations-Addendum bestehen.

---

## TEIL 15: Migrations-Checkliste für den anderen Chat

Der andere Chat sollte diese Checkliste abarbeiten:

### 15.1 Namen

- [ ] `SwarmErgebnisPaket` → `QuestorErgebnisPaket`
- [ ] `swarm_ergebnis_paket` → `questor_ergebnis_paket`
- [ ] `swarm_instance_id` → `questor_instance_id`
- [ ] `MockSwarm` → `DummyQuestor`
- [ ] `swarm_interface` → `questor_interface`
- [ ] „Schwarm“ in Spezifikationen → „Questor“

### 15.2 Verträge

- [ ] `QuestorDispatchEnvelope` eingeführt
- [ ] `ResearchPackage.questor_spec` optional eingeführt
- [ ] `QuestorMetadata` optional eingeführt
- [ ] `LocalAuditRef` definiert
- [ ] `OperationalMetrics` definiert
- [ ] Archivar auf neue Felder getestet

### 15.3 Architektur

- [ ] Kein produktiver Adapter
- [ ] Dispatcher nutzt Envelope
- [ ] Receiver nutzt neues Ergebnis
- [ ] QuestorBlackbox liegt außerhalb von Gremium-Daten
- [ ] HAL bleibt einzige Hardware-Schnittstelle

### 15.4 Tests

- [ ] Naming-Tests
- [ ] Vertrags-Tests
- [ ] Questor-Tests
- [ ] Integrationstests
- [ ] Szenario-Tests A–E
- [ ] Regressions-Tests aus v2.3.1

---

## TEIL 16: Verbotene patterns

Die folgenden Patterns sind in der Zielarchitektur verboten:

```text
Questor schreibt direkt in den Atlas.
Questor schreibt direkt in das Archiv.
Questor liest globale Pheromon-/Signal-Stacks.
Questor setzt ESTOP zurück.
Questor vergibt Leases.
Questor erzeugt 🟥 direkt.
Gremium liest QuestorBlackbox.
Dispatcher sendet produktiv ohne gate_record_ref.
Receiver erwartet swarm_ergebnis_paket.
Archivar prüft swarm_instance_id.
```

---

## TEIL 17: Empfehlung für die finale Testreihenfolge

1. Naming-/Vertragstests
2. Archivar-Receiver-Tests
3. Dispatcher-Envelope-Tests
4. Questor-Vertragstests
5. Questor-Sicherheitsregeln
6. Integrationstests
7. Szenario-Pflichttests A–E
8. Regressions-Tests aus v2.3.1
