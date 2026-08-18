# Architektur — MYRMEX v2.4.0 + Questor v0.2.3

Vollständige Architektur-Dokumentation für Entwickler und Architekten.

---

## 1. System-Überblick

### 1.1 Die 6 Schichten

| Schicht | Name | Verantwortung |
|---------|------|---------------|
| 5 | 👑 Königin | Langfristige Vision, Meta-Ziele, menschliche oder LLM-basierte Führung |
| 4 | 🏛️ Gremium | Intelligenz, Atlas, Archiv, Ideen, Pakete, Sicherheit |
| 3 | ⚖️ Dispatch-Koordination | Dispatch-Vorbereitung, Lease-/Gate-Koordination |
| 2 | 🧭 Questor | Paketgebundenes Execution Subsystem |
| 1 | 🔌 HAL & Resource Governor | Slot-Routing, Leases, ESTOP, Hardwarezugriff |
| 0 | ⚙️ Physis / Compute | Hardware, Simulation, Compute |

**Empfohlener Name für Schicht 3:** `DispatchCoordinator`

### 1.2 Die 9-Stufen-Pipeline

Die Pipeline verarbeitet wissenschaftliche Ideen von der Entstehung bis zur Ausführung:

| Stufe | Name | Verantwortlich | Beschreibung |
|-------|------|----------------|--------------|
| 1 | Wissens-Aufnahme | Archivar | Empfängt questor_ergebnis_paket, schreibt Kristalle und Signale |
| 2 | Atlas-Strukturierung | Kartograph | Strukturiert Wissen in Zonen, Cluster, Signale |
| 3 | Strategische Review | Kanzler ↔ Königin | Langfristige Ausrichtung, Realitäts-Check |
| 4 | Ideen-Generierung | Vordenker | Erzeugt Roh-Ideen aus Atlas-Mustern |
| 5a | Pre-Filter | Deterministischer Fast-Path | Filtert offensichtliche Probleme (Dimensionen, Quarantäne) |
| 5b | Ideen-Erdung | Lotse | Platziert Wegmarken im Atlas (IDEE_GEPRÜFT → WEGMARKE_PLATZIERT) |
| 6 | Paket-Bau | Quartiermeister | Baut ResearchPackage aus Wegmarke |
| 7 | Sicherheits-Gate | Richter + Seher | Sicherheitsprüfung (NORMAL, FRACTURE_DIAGNOSIS, HIGH_RISK_OVERRIDE, SANDBOX) |
| 8 | Dispatch & Execution | Dispatcher → Questor → Receiver → Archivar | Ausführung über QuestorDispatchEnvelope |

**Datenfluss zwischen den Stufen:**

```text
Stufe 1 ← Stufe 8 (Ergebnis-Rückfluss)
  ↓
Stufe 2
  ↓
Stufe 3
  ↓
Stufe 4
  ↓
Stufe 5a → 5b
  ↓
Stufe 6
  ↓
Stufe 7
  ↓
Stufe 8
```

### 1.3 Kernregeln

#### Blackboard-Pattern
Alle Ränge des Gremiums kommunizieren **ausschließlich** über:
- Atlas
- Archiv

**Keine direkten Aufrufe** zwischen Rängen.

#### Menschliche Königin wird niemals überstimmt
- Bei Konflikt zwischen menschlicher und LLM-Königin gewinnt die menschliche Weisung.
- Nach 2 Konflikten fällt die LLM-Königin auf menschliche Entscheidung zurück.

#### Fail-Closed
Wenn etwas nicht sicher geprüft werden kann:
- keine Freigabe
- keine physische Ausführung
- kontrollierter Abbruch oder Eskalation

#### Seher schreibt niemals 🟥
- Der Seher (LLM-Komponente) darf niemals direkt rote Signale schreiben.
- Rote Signale dürfen nur durch deterministische Komponenten oder nach Sicherheitsprüfung entstehen.

#### Operational ≠ Scientific
| Klasse | Bedeutung | Wissenschaftliches Signal? |
|--------|-----------|---------------------------|
| OPERATIONAL | Prozessfehler, Crash, Timeout, Lease-Problem | nein |
| SCIENTIFIC | wissenschaftliche Zielverfehlung, empirischer Widerspruch | ja, als Vorschlag |
| SAFETY | Sicherheitsverletzung, ESTOP | ja, nur mit Sicherheitsprüfung |

---

## 2. Datenfluss

### 2.1 Ideen-Pipeline (Stufen 4, 5a, 5b)

```text
Vordenker → Pre-Filter → Lotse
```

1. **Vordenker** erzeugt `RohIdee` aus Atlas-Mustern
2. **Pre-Filter** prüft deterministisch:
   - Dimension-Freigabe
   - Quarantäne-Zonen
   - Sättigungs-Zustände
3. **Lotse** platziert `Wegmarke` im Atlas:
   - Zustand: `IDEE_OFFEN` → `IDEE_GEPRÜFT` → `WEGMARKE_PLATZIERT`
   - Nur in Weißraum oder bestätigten grünen Zonen

### 2.2 Paket-Pipeline (Stufen 6, 7, 8)

```text
Quartiermeister → Sicherheits-Gate → Dispatcher
```

1. **Quartiermeister** baut `ResearchPackage` aus `Wegmarke`:
   - Routing-Graph
   - Material/Resource-Listen
   - Parameter-Bounds
   - Gefahren-Mitigationen

2. **Sicherheits-Gate** (Stufe 7):
   - **Richter** (deterministisch): Prüft Regeln, Policies
   - **Seher** (LLM): Bewertet Evidenz, schreibt niemals direkt 🟥
   - **Circuit-Breaker**: Überwacht Seher-Fehlerraten
   - **Berufung**: Bei Richter-Pass + Seher-Veto
   - **Policy-Veto-Review**: Nach 20 Veto-Zyklen

3. **Dispatcher** erzeugt `QuestorDispatchEnvelope`:
   - Mit `gate_record_ref`
   - Mit `lease_grants`
   - Mit `security_mode`

### 2.3 Questor-Anbindung

```text
QuestorDispatchEnvelope → Questor → questor_ergebnis_paket
```

1. **QuestorDispatchEnvelope** enthält:
   - `dispatch_id`, `zyklus_id`, `attempt_id`
   - `package: ResearchPackage`
   - `gate_record_ref: str` (Pflicht)
   - `gate_mode: NORMAL | FRACTURE_DIAGNOSIS | HIGH_RISK_OVERRIDE | SANDBOX`
   - `lease_grants: list[LeaseGrant]`
   - `idempotency_key` (kanonisch: `package_id:zyklus_id:attempt_id`)

2. **Questor** führt aus:
   - Innerhalb gültiger Leases
   - Beachtet `security_mode`
   - Schreibt lokale Blackbox (`data/questor_blackbox/`)

3. **questor_ergebnis_paket**返回:
   - `status: erfolgreich | fehlgeschlagen | abgebrochen`
   - `abbruch_klasse: OPERATIONAL | SCIENTIFIC | SAFETY`
   - `kristall_kandidaten`, `signale_fuer_atlas`
   - `questor_metadata` (optional, operational)

### 2.4 Wissens-Pipeline (Stufen 1, 2)

```text
Archivar → Kartograph → Atlas
```

1. **Archivar** empfängt `questor_ergebnis_paket`:
   - Prüft `idempotency_key`
   - Prüft `sequence_number` pro `questor_instance_id`
   - Trennt `abbruch_klasse`:
     - `OPERATIONAL` → kein wissenschaftliches Signal
     - `SCIENTIFIC` → Kristall + Signal möglich
     - `SAFETY` → Sicherheits-Signal

2. **Kartograph** strukturiert Atlas:
   - Zonen (mit parent/child-Hierarchie)
   - Cluster (DBSCAN-basiert)
   - Signale (🟥, 🟨, 🟪, 🟩, ⬜)
   - `fracture_score` berechnet

---

## 3. Komponenten

### 3.1 Gremium (Schicht 4)

#### Basis-Komponenten
| Komponente | Verantwortung |
|------------|---------------|
| **Archivar** | Empfängt Ergebnisse, schreibt Kristalle/Signale, trennt Operational/Scientific |
| **Kartograph** | Atlas-Strukturierung, Zonen, Cluster, fracture_score |
| **Kanzler** | Strategische Review, Realitäts-Check, Lageberichte |
| **Vordenker** | Ideen-Generierung aus Atlas-Mustern |
| **Pre-Filter** | Deterministischer Fast-Path (Dimensionen, Quarantäne) |
| **Lotse** | Ideen-Erdung, Wegmarken-Platzierung |
| **Quartiermeister** | Paket-Bau aus Wegmarken |

#### Sicherheitsrat
| Komponente | Typ | Verantwortung |
|------------|-----|---------------|
| **Richter** | deterministisch | Regelprüfung, Policy-Enforcement, Fail-Closed |
| **Seher** | LLM | Evidenz-Bewertung, schreibt niemals direkt 🟥 |
| **Circuit-Breaker** | Zustandsmaschine | Überwacht Seher-Fehlerraten, setzt Seher temporär aus |
| **Appeal (Berufung)** | Prozess | Bei Richter-Pass + Seher-Veto |
| **Policy-Review** | Audit | Nach 20 Veto-Zyklen, persistent über SAFE_MODE |

#### Pipeline-Orchestrator
- Koordiniert Stufen-Übergänge
- Verwaltet Bounded Queues mit Watermarks
- Deadlock-Erkennung
- Notventil-Zyklen

### 3.2 Questor (Schicht 2)

#### Aktuelle Implementierung
- **DummyQuestor**: Simuliert Questor-Verhalten für Tests

#### Zukünftige Implementierung
- **QuestorFacade**: Eingang für QuestorDispatchEnvelope
- **Validator**: Validiert Envelope vor Ausführung
- **ObjectiveParser**: Parst wissenschaftliche Ziele
- **Compass**: Navigiert im Lösungsraum
- **PolicyEvaluator**: Bewertet Policies während Ausführung
- **LoopRegistry**: Verwaltet Schleifen-Templates
- **CapabilityRegistry**: Registriert Fähigkeiten
- **Ledger**: Führt Buch über Ausführungen
- **TrailMap**: Zeichnet Suchpfade auf
- **SafetyMonitor**: Überwacht Sicherheit während Ausführung
- **Recovery**: Stellt Zustand nach Fehlern wieder her
- **Sequence**: Steuert Ausführungs-Sequenz
- **Sanitization**: Bereinigt Eingaben/Ausgaben
- **HalBridge**: Verbindung zu HAL
- **ResultBuilder**: Baut questor_ergebnis_paket
- **BlackboxArchiver**: Archiviert lokale Blackbox

#### Datenverträge
- **QuestorDispatchEnvelope**: Eingang (von Dispatcher)
- **questor_ergebnis_paket**: Ausgang (an Archivar)

### 3.3 HAL & Resource Governor (Schicht 1)

#### Resource Governor
| Komponente | Verantwortung |
|------------|---------------|
| **Slot Manager** | Verwaltet Slots, Mutex-Tabelle, Routing |
| **Governor** | Ressourcen-Allokation, Budget-Überwachung |
| **ESTOP Handler** | Behandelt Emergency Stops, suspendiert Leases |
| **Zone Manager** | Zonen-Mutex, Kollisionsvermeidung |

#### HAL Interface
- **hal_interface**: Abstrakte Schnittstelle für Hardware
- **dummy_hal**: Dummy-Implementierung für Tests

#### Lease-Management
- Lease-Vergabe ausschließlich durch Resource Governor
- Pfad-Leases (atomare Reservierung)
- Langzeit-Leases mit SAFE_HOLD
- TTL-Überwachung

### 3.4 Infrastruktur

#### Atlas Store
- Append-only für Signale
- Snapshot-Mechanismus
- Recovery aus Snapshots
- Event-Count-Tracking

#### Signal Registry
- Signal-Stacks (append-only)
- Prioritäts-basierte Resolution
- Kristallisation nach 3 Bestätigungen
- Signal-Zerfall über Zeit

#### Clustering
- DBSCAN-basierte Cluster-Bildung
- fracture_score-Berechnung
- FULL_REBUILD (atomar)
- NEUAUSRICHTEN (inkrementell)

#### Transaction Layer
- **WAL (Write-Ahead Log)**: Persistente Einträge mit Checksummen
- **State Machine**: Zustandsübergänge für Stufen 5b, 6, 7, 8
- **Recovery**: Setzt Pakete in korrekte Stufe zurück

---

## 4. Datenverträge

### 4.1 QuestorErgebnisPaket

```python
QuestorErgebnisPaket:
  package_id: str                      # Format: ^[A-Za-z0-9._-]{1,128}$
  zyklus_id: str                       # Format: ^[A-Za-z0-9._-]{1,128}$
  attempt_id: int                      # 0 <= attempt_id <= 999999
  idempotency_key: str                 # Kanonisch: package_id:zyklus_id:attempt_id
  questor_instance_id: str             # Questor-Instanz-ID
  sequence_number: int                 # Monoton pro questor_instance_id
  observed_atlas_version_id: str       # Beobachtete Atlas-Version
  status: erfolgreich | fehlgeschlagen | abgebrochen
  abbruch_grund: Optional[str]         # Pflicht bei fehlgeschlagen/abgebrochen
  abbruch_klasse: OPERATIONAL | SCIENTIFIC | SAFETY
  routing_checkpoint: RoutingCheckpoint
  ergebnis_daten: ErgebnisDaten
  validierung: GuardianValidierung
  kristall_kandidaten: list[KristallKandidat]
  gefahren_beobachtet: list[str]
  signale_fuer_atlas: list[SignalEvent]
  vollstaendig_flag: bool              # Pflichtfeld
  rohdaten_checksumme: str             # Pflichtfeld
  questor_metadata: Optional[QuestorMetadata]
```

**Idempotency-Key (kanonisch):**
```text
idempotency_key = package_id + ":" + zyklus_id + ":" + attempt_id
```

**Regeln:**
- Keine führenden Nullen in attempt_id
- Maximale Länge: 264 Zeichen
- Beispiel gültig: `pkg-001:zyklus-014:2`
- Beispiel ungültig: `pkg-001:zyklus-014:02`

**Semantik von `abbruch_klasse`:**
- Bei `status: erfolgreich`: `abbruch_grund = null`, `abbruch_klasse = OPERATIONAL`
- Bei `status: fehlgeschlagen`: beide Felder müssen gesetzt sein
- Bei `status: abgebrochen`: beide Felder müssen gesetzt sein

### 4.2 QuestorDispatchEnvelope

```python
QuestorDispatchEnvelope:
  dispatch_id: str
  zyklus_id: str
  attempt_id: int
  package: ResearchPackage
  gate_record_ref: str                 # Pflichtfeld
  gate_mode: Optional[NORMAL | FRACTURE_DIAGNOSIS | HIGH_RISK_OVERRIDE | SANDBOX]
  lease_grants: list[LeaseGrant]
  execution_environment_ref: Optional[str]
  dispatch_mode: NORMAL | RETRY | RECOVERY
  security_mode: NORMAL | SANDBOX | DEV_SANDBOX_ONLY | RECOVERY
  dispatch_timestamp: str
  idempotency_key: str                 # Kanonisch gebildet
```

**Pflichtregeln:**
- `gate_record_ref` ist Pflicht → fehlt: `abbruch_grund = PACKAGE_INVALID`
- `gate_mode` darf nicht im Widerspruch zum Gate Record stehen
- `lease_grants` müssen konsistent sein
- `security_mode` muss zu Gate und Leases passen

### 4.3 ResearchPackage

```python
ResearchPackage:
  package_id: str
  source_wegmarke: str
  source_wegmarke_version: Optional[str]
  atlas_version_ref: str
  ziel: str
  materials_or_resources: list[str]
  parameter_bounds: dict[str, tuple[float, float]]
  routing_graph: RoutingGraph          # Pflicht: max_loop_iterations, branch_condition_timeout
  gefahren_mitigationen: list[str]
  kontext: PackageKontext
  dimension_expansion_approval: Optional[str]
  override_requested: bool
  limits: dict[str, float]
  expected_side_effects_or_failure_modes: list[str]
  domain_metadata: dict[str, any]
  questor_spec: Optional[QuestorSpec]
```

**RoutingGraph (Pflichtfelder):**
- `max_loop_iterations`: int
- `branch_condition_timeout`: float

### 4.4 QuestorMetadata, LocalAuditRef, OperationalMetrics

#### QuestorMetadata
```python
QuestorMetadata:
  questor_version: str
  policy_version: str
  local_audit: Optional[LocalAuditRef]
  operational_metrics: Optional[OperationalMetrics]
```

**Regeln:**
- Das Gremium darf `questor_metadata` ignorieren
- `local_audit` enthält keine Blackbox-Inhalte
- `operational_metrics` dürfen ausschließlich operational verwendet werden
- `questor_metadata` erzeugt keine Kristalle oder wissenschaftlichen Signale

#### LocalAuditRef
```python
LocalAuditRef:
  blackbox_id: str
  manifest_checksum: str
  blackbox_digest: str
  redaction_level: NONE | BASIC | STRONG
  retention_class: NORMAL | SAFETY_HOLD | DEVELOPMENT_HOLD
  access_policy_summary: str
```

**Regeln:**
- Kein Pfad, der automatisch vom Gremium gelesen wird
- Nur Referenz, Digest und Policy-Zusammenfassung

#### OperationalMetrics
```python
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

**Regeln:**
- Rein operational, keine wissenschaftliche Interpretation
- Dürfen in `operational_event_log` einfließen

### 4.5 Gate-Modelle (GateRecord, GateMode)

```python
GateRecord:
  gate_id: str                         # Pflicht
  package_id: str                      # Pflicht
  zyklus_id: str                       # Pflicht
  mode: NORMAL | FRACTURE_DIAGNOSIS | HIGH_RISK_OVERRIDE | SANDBOX
  richter_result: PASS | FAIL
  seher_result: PASS | VETO | TEMP_SUSPENDED
  circuit_breaker_state: CLOSED | OPEN | HALF_OPEN
  appeal_status: PENDING | GRANTED | DENIED
  signature: str                       # Digitale Signatur
```

**GateMode:**
- `NORMAL`: Standardbetrieb
- `FRACTURE_DIAGNOSIS`: Diagnose bei hohem fracture_score
- `HIGH_RISK_OVERRIDE`: Überschreibung mit positiver Widerlegung erforderlich
- `SANDBOX`: Sandbox-Modus, keine physische Ausführung

### 4.6 Lease-Modelle (LeaseGrant, LeaseStatus, PathLease)

#### LeaseGrant
```python
LeaseGrant:
  lease_id: str                        # Pflicht
  granted_at: str                      # Pflicht
  resource_class: str
  slot_id: str
  ttl_seconds: float
  on_expiry_policy: RETURN | EXTEND | RELEASE
  execution_flags: dict[str, bool]     # Default: alle False
```

#### LeaseStatus
```python
LeaseStatus:
  status: ACTIVE | EXPIRED | SUSPENDED | RETURNED
  is_active: bool                      # Computed
  is_expired: bool                     # Computed
  suspension_reason: Optional[str]
  remaining_ttl: float                 # Nicht-negativ
```

#### PathLease
```python
PathLease:
  path_id: str
  reserved_slots: list[str]            # Atomare Reservierung
  start_time: str
  end_time: str
  zone_mutex_refs: list[str]
```

**Regeln:**
- Pfad-Lease ist atomar: alle oder keine Slots
- Keine partielle Reservierung

---

## 5. Zustandsmaschinen

### 5.1 Stufe 5b: IDEE_OFFEN → IDEE_GEPRÜFT → WEGMARKE_PLATZIERT

```text
Zustände:
  - IDEE_OFFEN: Idee wurde vom Vordenker erzeugt
  - IDEE_GEPRÜFT: Pre-Filter hat bestanden
  - WEGMARKE_PLATZIERT: Lotse hat Wegmarke im Atlas platziert
  - IDEE_VERWORFEN: Idee wurde verworfen (blocked_cache)

Übergänge:
  - IDEE_OFFEN → IDEE_GEPRÜFT: Pre-Filter erfolgreich
  - IDEE_GEPRÜFT → WEGMARKE_PLATZIERT: Lotse platziert erfolgreich
  - IDEE_GEPRÜFT → IDEE_VERWORFEN: Lotse verwirft (rote/gelbe/purpurne Zone)
  - IDEE_OFFEN → IDEE_VERWORFEN: Pre-Filter verwirft
```

### 5.2 Stufe 6: WEGMARKE_RESERVIERT → ... → PAKET_FERTIG

```text
Zustände:
  - WEGMARKE_RESERVIERT: Wegmarke wurde für Paketbau reserviert
  - PAKET_IM_BAU: Quartiermeister baut Paket
  - PAKET_FERTIG: Paket ist vollständig
  - PAKET_FEHLGESCHLAGEN: Paketbau fehlgeschlagen

Übergänge:
  - WEGMARKE_RESERVIERT → PAKET_IM_BAU: Quartiermeister startet
  - PAKET_IM_BAU → PAKET_FERTIG: Paketbau erfolgreich
  - PAKET_IM_BAU → PAKET_FEHLGESCHLAGEN: Paketbau fehlgeschlagen
```

### 5.3 Stufe 7: GATE_PENDING → ... → FREIGEGEBEN / DISPUTED

```text
Zustände:
  - GATE_PENDING: Paket wartet auf Sicherheitsprüfung
  - RICHTER_PRUEFT: Richter prüft deterministisch
  - SEHER_PRUEFT: Seher bewertet (wenn Richter PASS)
  - FREIGEGEBEN: Gate passiert (Richter PASS + Seher PASS)
  - DISPUTED: Berufung läuft (Richter PASS + Seher VETO)
  - ABGELEHNT: Gate nicht passiert

Übergänge:
  - GATE_PENDING → RICHTER_PRUEFT: Start
  - RICHTER_PRUEFT → ABGELEHNT: Richter FAIL
  - RICHTER_PRUEFT → SEHER_PRUEFT: Richter PASS
  - SEHER_PRUEFT → FREIGEGEBEN: Seher PASS
  - SEHER_PRUEFT → DISPUTED: Seher VETO (startet Appeal)
  - DISPUTED → FREIGEGEBEN: Appeal GRANTED
  - DISPUTED → ABGELEHNT: Appeal DENIED
```

### 5.4 Stufe 8: RESOURCE_WAITING → ... → ABGESCHLOSSEN / ABORTED

```text
Zustände:
  - RESOURCE_WAITING: Wartet auf Leases
  - LEASE_GRANTED: Leases wurden gewährt
  - QUESTOR_DISPATCHED: An Questor gesendet
  - QUESTOR_RUNNING: Questor führt aus
  - ABGESCHLOSSEN: Erfolgreich abgeschlossen
  - ABORTED: Abgebrochen (OPERATIONAL/SCIENTIFIC/SAFETY)

Übergänge:
  - RESOURCE_WAITING → LEASE_GRANTED: Leases gewährt
  - RESOURCE_WAITING → ABORTED: LeaseDenied (kein ESTOP!)
  - LEASE_GRANTED → QUESTOR_DISPATCHED: Envelope gesendet
  - QUESTOR_DISPATCHED → QUESTOR_RUNNING: Questor startet
  - QUESTOR_RUNNING → ABGESCHLOSSEN: Erfolgreich
  - QUESTOR_RUNNING → ABORTED: Fehler/Abbruch
```

---

## 6. Event-Driven Architecture

### 6.1 Pipeline-Events

Events werden über den Pipeline-Orchestrator verteilt:

```text
Event-Typen:
  - IDEE_ERZEUGT: Vordenker hat Idee generiert
  - IDEE_GEPRUEFT: Pre-Filter erfolgreich
  - WEGMARKE_PLATZIERT: Lotse hat Wegmarke gesetzt
  - PAKET_GEBAUT: Quartiermeister fertig
  - GATE_FREIGEGEBEN: Sicherheits-Gate passiert
  - QUESTOR_COMPLETED: Questor fertig
  - KRISTALL_ERZEUGT: Archivar hat Kristall geschrieben
  - SIGNAL_ERZEUGT: Archivar hat Signal geschrieben
```

### 6.2 Bounded Queues mit Watermarks

Jede Pipeline-Stufe hat eine begrenzte Queue:

```text
Queue-Struktur:
  - max_size: maximale Größe
  - high_watermark: Warnschwelle (z.B. 80%)
  - low_watermark: Entwarnung (z.B. 50%)

Verhalten:
  - Bei high_watermark: Neue Items werden abgelehnt
  - Bei low_watermark: Normalbetrieb resumes
  - Deadlock-Erkennung überwacht alle Queues
```

### 6.3 Deadlock-Erkennung

Der Orchestrator erkennt Deadlocks:

```text
Erkennung:
  - Zyklische Abhängigkeiten zwischen Queues
  - Timeouts bei State-Transitions
  - Blockierte Leases ohne Fortschritt

Behandlung:
  - Notventil-Zyklen initiieren
  - Pakete in vorherige Stufe zurücksetzen
  - Circuit-Breaker für betroffene Komponenten
```

### 6.4 Notventil-Zyklen

Bei Deadlock oder kritischem Fehler:

```text
Notventil-Ablauf:
  1. Alle aktiven Transaktionen stoppen
  2. Pakete in sichere Zustände zurücksetzen
  3. Leases freigeben oder suspendieren
  4. SAFE_MODE aktivieren (falls nötig)
  5. Menschliche Königin benachrichtigen
```

---

## 7. Atlas und Signal-System

### 7.1 Signal-Typen (🟥, 🟨, 🟪, 🟩, ⬜)

| Symbol | Name | Bedeutung | Quelle |
|--------|------|-----------|--------|
| 🟥 | ROT | Kritischer Fehler, Sicherheitsproblem | Nur Sicherheits-Gate/ESTOP |
| 🟨 | GELB | Warnung, erhöhte Vorsicht | Kartograph, Lotse |
| 🟪 | PURPUR | Quarantäne, diagnostisch nur | Lotse (nur mit Budget) |
| 🟩 | GRÜN | Bestätigt, sicher | Nach 3 Bestätigungen |
| ⬜ | WEISS | Unbestätigt, neutral | Default für neue Signale |

### 7.2 Signal-Resolution

Signale werden priorisiert aufgelöst:

```text
Priorität (hoch → niedrig):
  1. 🟥 ROT (immer dominant)
  2. 🟨 GELB
  3. 🟪 PURPUR
  4. 🟩 GRÜN
  5. ⬜ WEISS

Resolution:
  - Höchste Priorität gewinnt
  - Bei gleicher Priorität: neuestes Signal
  - Stack-basiert (append-only)
```

### 7.3 Kristallisation und Verfall

```text
Kristallisation:
  - Nach 3 Bestätigungen wird Signal zu Kristall
  - Kristalle sind persistent
  - Kristalle bilden Atlas-Struktur

Verfall:
  - Signale zerfallen über Zeit (TTL)
  - Ungenutzte Signale verblassen
  - fracture_score steigt bei vielen roten Signalen
```

### 7.4 fracture_score und Zone-Health

```python
fracture_score: float  # 0.0 - 1.0

Berechnung:
  - Anteil roter Signale an Gesamtsignalen
  - Gewichteter Durchschnitt über Zeit
  - Cluster-lokal und global

Zone-Health:
  - HEALTHY: fracture_score < 0.3
  - DEGRADED: 0.3 <= fracture_score < 0.7
  - CRITICAL: fracture_score >= 0.7
```

### 7.5 FULL_REBUILD und NEUAUSRICHTEN

#### FULL_REBUILD
- Atomarer Neuaufbau des gesamten Atlas
- Alle Zonen und Cluster neu berechnen
- Signale neu bewerten
- Nur bei kritischem fracture_score

#### NEUAUSRICHTEN
- Inkrementelle Anpassung
- Betroffene Zonen neu strukturieren
- Minimale Unterbrechung

---

## 8. Test-Architektur

### 8.1 Test-Phasen (1–10)

| Phase | Komponente | Tests | Status |
|-------|------------|-------|--------|
| 1 | Contracts & Datenmodelle | ~50 | ✅ Abgeschlossen |
| 2 | Atlas & Signal-System | ~40 | ✅ Abgeschlossen |
| 3 | Transaction (WAL, State Machine) | ~30 | ✅ Abgeschlossen |
| 4 | Resource Governor & HAL | ~50 | ✅ Abgeschlossen |
| 5 | Gremium Basis (Archivar, Kartograph) | ~40 | ✅ Abgeschlossen |
| 6 | Gremium Erweitert (Vordenker, Lotse) | ~50 | ✅ Abgeschlossen |
| 7 | Sicherheitsrat (Richter, Seher) | ~40 | ✅ Abgeschlossen |
| 8 | Questor-Interface | ~40 | ✅ Abgeschlossen |
| 9 | Pipeline-Orchestrierung | ~45 | ✅ Abgeschlossen |
| 10 | Integration & Regression | ~120 | ✅ Abgeschlossen |

**Gesamt: 505 Tests grün**

### 8.2 Die 12 Pflicht-Integrationstests

Suite I (Integration) umfasst 18 Tests, davon 12 kritische Pflichttests:

| # | Test | Beschreibung |
|---|------|--------------|
| I-01 | Happy Path Szenario A | Vollständiger Durchlauf ohne Fehler |
| I-02 | Invalides Paket | Paket-Validierung schlägt fehl |
| I-03 | Direktes ResearchPackage verboten | Ohne Envelope abgelehnt |
| I-04 | Envelope ohne gate_record_ref | PACKAGE_INVALID |
| I-05 | LEASE_DENIED ohne ESTOP | LeaseDenied löst keinen ESTOP aus |
| I-06 | LEASE_QUEUED Timeout | Timeout bei queued Lease |
| I-07 | ESTOP während Questor-Ausführung | ESTOP unterbricht sicher |
| I-08 | Operativer Crash OOM | OOM ist OPERATIONAL, nicht SCIENTIFIC |
| I-09 | Wissenschaftlicher Fehlschlag | SCIENTIFIC mit Signal |
| I-10 | Routing-Loop-Schutz | Endlosschleife verhindert |
| I-11 | Unbekannte Dimension ohne Approval | dimension_expansion_approval required |
| I-12 | Fracture Diagnosis | FRACTURE_DIAGNOSIS Mode aktiv |

### 8.3 Test-Suiten (N, I, S, R, Z, H)

| Suite | Name | Tests | Zweck |
|-------|------|-------|-------|
| N | Naming & Contract Migration | ~10 | Keine alten Swarm-Begriffe, Vertragsvalidierung |
| I | Integration | 18 | End-to-End Integrationsszenarien |
| S | Szenario-Pflichttests | 5 | Domänenspezifische Szenarien (Chemie, Biologie, Material, etc.) |
| R | Regressions-Tests | 12 | Kritische Regressionen verhindern |
| Z | Zielpräzisierung | ~10 | Zieldefinition und -schärfung |
| H | HAL v0.2.0 | ~15 | Hardware Abstraction Layer Tests |

### 8.4 BEWEIS-PFLICHT

Für jede Phase gilt:
- Alle Tests der Phase müssen bestehen
- Keine kritischen Warnungen
- Dokumentation aktualisiert
- Sicherheitsgarantien verifiziert

---

## 9. Erweiterbarkeit

### 9.1 Questor-Implementierung (zukünftig)

Die aktuelle DummyQuestor-Implementierung wird ersetzt durch:
- Echte Questor-Engine mit ObjectiveParser, Compass, LoopRegistry
- Capability-Adapter für spezifische Fähigkeiten
- Policy-Evaluator für dynamische Policy-Bewertung

**Voraussetzungen:**
- Questor-Interface bleibt stabil
- QuestorDispatchEnvelope und questor_ergebnis_paket unverändert
- Blackbox-Isolation erhalten

### 9.2 HAL-Device-Adapter (zukünftig)

HAL v0.2.0 definiert das Interface. Device-Adapter werden implementiert für:
- Roboterarme
- Sensoren (Temperatur, Druck, pH, etc.)
- Aktoren (Ventile, Pumpen, Heizungen)
- Laborgeräte (Zentrifugen, Spektrometer, etc.)

**Voraussetzungen:**
- HAL-Interface stabil
- Slot-Mutex-Tabelle erweitert
- ESTOP-Mechanismus hardware-seitig implementiert

### 9.3 LLM-Integration (zukünftig)

Aktuell ist der Seher die einzige LLM-Komponente. Zukünftig:
- LLM-Königin (mit menschlichem Override)
- LLM-unterstützte Ideen-Generierung (Vordenker)
- LLM-unterstützte Evidenz-Bewertung (Seher)

**Sicherheitsregeln:**
- Deterministischer Fallback immer verfügbar
- Prompt-Injection-Schutz obligatorisch
- Circuit-Breaker für alle LLM-Komponenten
- LLM-Königin Fallback nach 2 Konflikten

### 9.4 Deployment (zukünftig)

Aktueller Stand: Lokal/Simulation

Zukünftige Optionen:
- **Cloud-Deployment**: Kubernetes, Docker, Serverless
- **On-Prem**: Bare-Metal, VM-Cluster
- **Hybrid**: Cloud-Steuerung, On-Prem-Ausführung

**Entscheidung erforderlich vor produktivem Deployment:**
- Zielumgebung definieren
- Skalierungsanforderungen klären
- Compliance- und Audit-Anforderungen prüfen
