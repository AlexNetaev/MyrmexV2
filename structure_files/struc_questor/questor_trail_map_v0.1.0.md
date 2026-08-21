# 🧭 QUESTOR-INTERNA: THEMA 6 — TRAIL-MAP
## Entscheidungsprotokoll, Nachvollziehbarkeit und lokale Blackbox-Ablage

| Feld | Wert |
|---|---|
| Dateiname | `questor_trail_map_v0.1.0.md` |
| Version | 0.1.0 |
| System | MYRMEX v2.4.0 + Questor v0.2.3 |
| Status | Arbeitsstand — Architektur-Spezifikation, keine Implementierungsfreigabe |
| Bezug | `structure_questor_interna_v0.4.0.md`, Teil P |
| | `structure_questor_interna_v0.3.0.md`, Teil F/G |
| | `structure_standalone_v2.4.0.md` v1.1.1, kanonisch |
| | `structure_standalone_questor_v0.2.3.md` |
| Sprache | Deutsch |
| Modus | Dry-Run / Spezifikation |

---

## 0. Dokumentenhierarchie und Geltung

```
1. structure_standalone_v2.4.0.md v1.1.1                    ← kanonisch
2. structure_hal_v0.2.0.md                                   ← HAL-Vertrag
3. structure_questor_interna_v0.4.0.md                       ← Questor-Interna GESAMT
4. diese Datei: questor_trail_map_v0.1.0.md                  ← Detail: Trail-Map
5. structure_standalone_questor_v0.2.3.md                    ← unterstützend
6. myrmex_questor_integration_tests_v0.4.0.md                ← Integrationstest-Grundlage
```

Bei Widersprüchen gilt die kanonische Hauptreferenz.

Dieses Dokument ist Teil P der Questor-Interna-Gesamtspezifikation.

**Kritische Geltungsregel:**  
Die Trail-Map ist **lokal**, **operational**, **nicht wissenschaftlich**, **nicht Atlas-relevant** und wird **nicht automatisch vom Gremium gelesen**.

---

## 1. Kritische Analyse des Bestehenden

### 1.1 Was bereits existiert

| Quelle | Referenz | Problem |
|---|---|---|
| `structure_questor_interna_v0.3.0.md` §67 | Trail-Map als offenes Thema mit Priorität Niedrig | Keine Struktur, keine Erzeugungsregeln, keine Speicherung. |
| `structure_questor_interna_v0.3.0.md` Teil F | ExpeditionLedger + WAL | Ledger protokolliert Ausführungsereignisse, aber nicht zwingend Entscheidungsbegründungen. |
| `structure_questor_interna_v0.3.0.md` Teil G | Result-Builder + Blackbox | Blackbox existiert lokal, aber Trail-Map als eigener Artefakt-Typ ist nicht spezifiziert. |
| `structure_standalone_v2.4.0.md` / `structure_standalone_questor_v0.2.3.md` | `LocalAuditRef` | Nur Referenz/Digest/Policy-Zusammenfassung, kein Pfad und keine automatische Übergabe. |
| `structure_standalone_questor_v0.2.3.md` | `src/questor/trail_map.py` im Strukturbaum | Datei vorgesehen, aber ohne Spezifikation. |
| `myrmex_questor_integration_tests_v0.4.0.md` | Vollständiges Ergebnis, keine freien Zusatzfelder außerhalb `questor_metadata` | Trail-Map darf nicht als Zusatzfeld in `questor_ergebnis_paket` landen. |

### 1.2 Identifizierte Probleme

| # | Problem | Schweregrad | Begründung |
|---|---|---|---|
| P1 | **Trail-Map ist genannt, aber nicht definiert.** | Hoch | Implementierer wissen nicht, was gespeichert werden soll. |
| P2 | **Abgrenzung zu Ledger fehlt.** | Hoch | Doppelprotokollierung oder widersprüchliche Protokolle möglich. |
| P3 | **Abgrenzung zu Blackbox fehlt.** | Hoch | Unklar, ob Trail-Map Ergebnisbestandteil, Ledgerbestandteil oder Blackboxbestandteil ist. |
| P4 | **Kein Datenvertrag.** | Hoch | Keine Pydantic-Modelle, keine Validierung, keine Hashes. |
| P5 | **Keine Sicherheitsgrenze.** | Kritisch | Trail-Map könnte versehentlich wissenschaftliche Signale oder Atlas-relevante Interpretationen enthalten. |
| P6 | **Keine Regel zur Gremium-Sichtbarkeit.** | Kritisch | Hauptreferenz verbietet automatische Blackbox-Übergabe; Trail-Map darf diesen Schutz nicht umgehen. |
| P7 | **Keine Erzeugungspunkte.** | Hoch | Unklar, welche Entscheidungen Trails erzeugen. |
| P8 | **Keine Retention-/Redaction-Regeln.** | Mittel | Trail-Map kann sensible operative Details enthalten. |
| P9 | **Keine Regel bei Trail-Erzeugungsfehlern.** | Mittel | Ein Fehler im Audit darf die Ausführung nicht blockieren. |
| P10 | **Keine Verknüpfung zu Sanitization, Capability, Security-Mode, Shutdown, Health.** | Mittel | Neue Detailthemen erzeugen wichtige Entscheidungen, aber ohne Trail-Definition würden sie nicht nachvollziehbar. |

### 1.3 Fazit der Analyse

Die Trail-Map ist kein dekoratives Log, sondern ein **operationales Entscheidungsprotokoll**. Sie ist wichtig für:
- Debugging,
- Nachvollziehbarkeit,
- Audits,
- Template-Korrektur,
- Fehleranalyse,
- Rekonstruktion von Entscheidungswegen.

Gleichzeitig ist sie gefährlich, wenn sie falsch eingebunden wird:
- Sie darf **keine wissenschaftlichen Signale** erzeugen.
- Sie darf **nicht automatisch an Atlas/Archiv/Gremium** übergeben werden.
- Sie darf **nicht vom LLM gelesen** werden.
- Sie darf **nicht zur Recovery** verwendet werden; Recovery bleibt **nur WAL**.
- Sie darf **nicht als Ergebnisfeld** außerhalb `questor_metadata` erscheinen.

---

## 2. Formale Definition: Trail-Map

### 2.1 Zweck

Die Trail-Map ist das **lokale Entscheidungsprotokoll** eines Questor-Laufs.

Sie beantwortet:

1. Welche Entscheidungen hat Questor getroffen?
2. Wann wurden sie getroffen?
3. Welche Inputs/Evidenzen lagen vor?
4. Welche Alternativen wurden verworfen?
5. Welche Policies/Vetos/Fallbacks waren beteiligt?
6. Welche Entscheidungskette führte zum finalen Ergebnis?

### 2.2 Nicht-Zweck

Die Trail-Map ist ausdrücklich **nicht**:

| Nicht-Zweck | Begründung |
|---|---|
| Kein wissenschaftliches Ergebnis | Wissenschaftliche Signale entstehen nur über Kristallkandidaten und Result-Builder-Regeln. |
| Kein Atlas-Input | Questor schreibt nicht in Atlas. |
| Kein Archiv-Input | Questor schreibt nicht ins Archiv. |
| Kein Recovery-Mechanismus | Recovery erfolgt ausschließlich aus WAL. |
| Kein LLM-Kontext | LLM darf Trail-Map nicht lesen. |
| Kein Policy-Ersatz | PolicyEvaluator bleibt deterministische Entscheidungsinstanz. |
| Kein Gate-Ersatz | Sicherheits-Gate bleibt außerhalb von Questor. |

### 2.3 Position in der Architektur

```
Questor
│
├── QuestCompass
│   ├── Objective Analysis         → Trail: OBJECTIVE_ANALYSIS
│   ├── Loop Selection             → Trail: LOOP_SELECTION
│   ├── Parameter Choice           → Trail: PARAMETER_CHOICE
│   ├── Evaluation                 → Trail: EVALUATION
│   └── Re-Planning                → Trail: RE_PLAN
│
├── Sanitization
│   ├── Input quarantined          → Trail: SANITIZATION_QUARANTINE
│   └── LLM output rejected        → Trail: LLM_ADVICE_REJECTED
│
├── Capability-Registry
│   └── Capability check           → Trail: CAPABILITY_CHECK
│
├── Security-Mode
│   └── Security mode check        → Trail: SECURITY_MODE_CHECK
│
├── PolicyEvaluator / SafetyMonitor
│   ├── Policy GO                  → Trail: SAFETY_CHECK
│   └── Policy VETO                → Trail: POLICY_VETO
│
├── Shutdown
│   └── Shutdown received          → Trail: SHUTDOWN_INITIATED
│
├── Health-Monitoring
│   └── Health alert               → Trail: HEALTH_ALERT
│
└── Blackbox
    └── trail_map.json             ← lokale Speicherung
```

### 2.4 Grundprinzipien

| Prinzip | Bedeutung |
|---|---|
| **Operational-only** | Trail-Map ist operational, nicht wissenschaftlich. |
| **Lokal** | Speicherung nur in lokaler Blackbox. |
| **Append-only** | Trails werden nur angehängt, nicht verändert. |
| **Deterministisch** | Trail-Erzeugung ist deterministisch. Kein LLM. |
| **Nicht-blockierend** | Trail-Fehler dürfen Questor-Ausführung nicht abbrechen. |
| **Evidenzbasiert** | Wenn `require_evidence = true`, muss jeder Trail Evidenz enthalten. |
| **Hashbar** | Trail-Map erhält einen Digest; nur Digest/Summary darf referenziert werden. |
| **Nicht Recovery-relevant** | Recovery nutzt WAL, niemals Trail-Map. |

---

## 3. Aktivierung und Policy

### 3.1 Trail-Policy im QuestorSpec

Die Trail-Map wird über eine explizite Policy gesteuert.

```yaml
TrailPolicy:
  create_trails: bool                 # Default: false
  detail_level: MINIMAL | STANDARD | FULL
  require_evidence: bool              # Default: true
  include_llm_advice_summary: bool    # Default: true
  include_rejected_alternatives: bool # Default: true bei STANDARD/FULL
  include_parameter_snapshots: bool   # Default: false, true nur bei FULL
  max_trails_per_package: int         # Default: 1000
  max_trail_map_size_mb: float        # Default: 10.0
  redaction_level: NONE | BASIC | STRONG
```

### 3.2 Default

```yaml
initial_trail_policy:
  create_trails: false
  detail_level: STANDARD
  require_evidence: true
  include_llm_advice_summary: true
  include_rejected_alternatives: true
  include_parameter_snapshots: false
  max_trails_per_package: 1000
  max_trail_map_size_mb: 10.0
  redaction_level: BASIC
```

### 3.3 Kritische Default-Entscheidung

**Default ist `create_trails = false`.**

Begründung:
- Trail-Map kann sensible operative Details enthalten.
- Hauptreferenz verbietet automatische Blackbox-Übergabe.
- Trail-Map ist für Debugging/Audit wertvoll, aber nicht zwingend für Standardausführung.
- Wenn aktiviert, muss klar sein, dass sie lokal bleibt.

### 3.4 Aktivierung

Trail-Map darf aktiviert werden durch:

| Quelle | Erlaubt? | Bedingung |
|---|---:|---|
| `QuestorSpec.initial_trail_policy` | ✅ | Vom Quartiermeister/Paket explizit gesetzt. |
| Questor-Konfiguration | ✅ | Nur als lokaler Betriebsmodus. |
| LLM | ❌ | LLM darf Trails weder aktivieren noch deaktivieren. |
| HAL | ❌ | HAL hat keine Trail-Kontrolle. |
| Archivar automatisch | ❌ | Archivar darf Blackbox nicht automatisch lesen. |
| Atlas | ❌ | Atlas hat keinen Zugriff. |

---

## 4. Datenverträge

### 4.1 TrailMap

```yaml
TrailMap:
  schema_version: str                    # "0.1.0"
  trail_map_id: str                      # deterministisch: trail-{package_id}-{zyklus_id}-{attempt_id}
  package_id: str
  zyklus_id: str
  attempt_id: int
  questor_instance_id: str
  created_at: str
  finalized_at: Optional[str]
  policy: TrailPolicy
  trails: list[Trail]
  summary: TrailMapSummary
  digest: str                            # SHA256 über kanonische TrailMap ohne digest-Feld
  redaction_level: NONE | BASIC | STRONG
  access_policy_summary: str
```

### 4.2 Trail

```yaml
Trail:
  trail_id: str                          # deterministisch: tr-{sequence_number}-{decision_type}
  sequence_number: int                   # monoton innerhalb der TrailMap
  timestamp: str                         # ISO-8601
  state: str                             # Questor-Zustand: PLANNING, EXECUTING, ...
  loop_index: Optional[int]
  step_index: Optional[int]
  decision_type: DecisionType
  actor: DecisionActor
  input_refs: list[InputRef]
  evidence: list[EvidenceRef]
  alternatives_considered: list[AlternativeDecision]
  decision: DecisionRecord
  policy_refs: list[str]
  safety_refs: list[str]
  llm_advice_ref: Optional[str]
  outcome: TrailOutcome
  warnings: list[str]
  redactions: list[RedactionRecord]
  entry_hash: str
  previous_hash: Optional[str]
```

### 4.3 DecisionType

```yaml
DecisionType:
  OBJECTIVE_ANALYSIS
  OBJECTIVE_CLARIFICATION
  LOOP_SELECTION
  PARAMETER_CHOICE
  EVALUATION
  RE_PLAN
  LLM_ADVICE_ACCEPTED
  LLM_ADVICE_REJECTED
  POLICY_VETO
  SAFETY_CHECK
  EARLY_ABORT
  SANITIZATION_QUARANTINE
  SANITIZATION_REJECT
  CAPABILITY_CHECK
  SECURITY_MODE_CHECK
  SHUTDOWN_INITIATED
  HEALTH_ALERT
```

### 4.4 DecisionActor

```yaml
DecisionActor:
  QUESTCOMPASS
  POLICY_EVALUATOR
  SAFETY_MONITOR
  SANITIZATION_MODULE
  CAPABILITY_REGISTRY
  SECURITY_MODE_MODULE
  HAL_BRIDGE
  RESULT_BUILDER
  SHUTDOWN_HANDLER
  HEALTH_MONITOR
  SYSTEM
```

### 4.5 InputRef

```yaml
InputRef:
  ref_type: PACKAGE_FIELD | TEMPLATE | LEDGER_ENTRY | WAL_ENTRY | HAL_RESULT |
            LLM_ADVICE | POLICY | CAPABILITY | SECURITY_MODE | HEALTH_EVENT
  ref_id: str
  digest: Optional[str]
  redacted: bool
```

### 4.6 EvidenceRef

```yaml
EvidenceRef:
  evidence_type: NUMERIC_MEASUREMENT | POLICY_RULE | CAPABILITY_RESULT |
                 SECURITY_MODE_RESULT | SANITIZATION_RESULT | LLM_VALIDATION_RESULT |
                 HAL_STATUS | BUDGET_STATE | TEMPLATE_SCORE | HEALTH_CHECK |
                 SHUTDOWN_SIGNAL
  description: str
  value_summary: Optional[str]
  source_ref: Optional[str]
  digest: Optional[str]
```

### 4.7 AlternativeDecision

```yaml
AlternativeDecision:
  alternative_id: str
  description: str
  score: Optional[float]
  rejection_reason: str
  vetoed_by: Optional[str]
```

### 4.8 DecisionRecord

```yaml
DecisionRecord:
  selected_option: str
  rationale: str
  deterministic: bool
  confidence: Optional[float]
  used_llm_advice: bool
  llm_advice_accepted: Optional[bool]
  final_authority: QUESTOR_DETERMINISTIC | POLICY_EVALUATOR | SAFETY_MONITOR
```

### 4.9 TrailOutcome

```yaml
TrailOutcome:
  status: ACCEPTED | REJECTED | VETOED | FALLBACK | ABORTED | INFO
  resulting_state: Optional[str]
  resulting_action: Optional[str]
  operational_effect: Optional[str]
```

### 4.10 RedactionRecord

```yaml
RedactionRecord:
  field_path: str
  reason: SENSITIVE_ID | SECURITY_RELEVANT | LLM_PROMPT | RAW_DATA | POLICY_PROTECTED
  redaction_level: NONE | BASIC | STRONG
```

### 4.11 TrailMapSummary

```yaml
TrailMapSummary:
  trail_count: int
  decision_type_counts: dict[str, int]
  llm_advice_used_count: int
  llm_advice_rejected_count: int
  policy_veto_count: int
  safety_check_count: int
  capability_check_count: int
  sanitization_event_count: int
  security_mode_check_count: int
  shutdown_event_count: int
  health_alert_count: int
  final_digest: str
```

### 4.12 TrailMapSummaryRef im Ledger

Der Ledger darf **nur eine Zusammenfassung / Referenz** aufnehmen, nicht die gesamte Trail-Map.

```yaml
TrailMapSummaryRef:
  trail_map_id: str
  trail_count: int
  final_digest: str
  redaction_level: NONE | BASIC | STRONG
  local_only: bool                       # immer true
```

---

## 5. Erzeugungsregeln

### 5.1 Wann wird ein Trail erzeugt?

Ein Trail wird erzeugt, wenn:

| Ereignis | DecisionType |
|---|---|
| Objective-Type wird bestimmt | `OBJECTIVE_ANALYSIS` |
| LLM wird zur Objective-Klärung gefragt | `OBJECTIVE_CLARIFICATION` |
| LoopTemplate wird ausgewählt | `LOOP_SELECTION` |
| Parameter werden gewählt oder angepasst | `PARAMETER_CHOICE` |
| Messergebnis oder Loop-Ergebnis wird bewertet | `EVALUATION` |
| Ziel nicht erreicht und Re-Planung erfolgt | `RE_PLAN` |
| LLM-Rat wird akzeptiert | `LLM_ADVICE_ACCEPTED` |
| LLM-Rat wird verworfen | `LLM_ADVICE_REJECTED` |
| PolicyEvaluator gibt VETO | `POLICY_VETO` |
| SafetyMonitor prüft eine Regel | `SAFETY_CHECK` |
| Questor bricht früh ab | `EARLY_ABORT` |
| Sanitization quarantänisiert ein Feld | `SANITIZATION_QUARANTINE` |
| Sanitization lehnt Input/Output ab | `SANITIZATION_REJECT` |
| Capability wird geprüft | `CAPABILITY_CHECK` |
| Security-Mode wird geprüft | `SECURITY_MODE_CHECK` |
| Shutdown wird eingeleitet | `SHUTDOWN_INITIATED` |
| Health-Monitoring meldet Alert | `HEALTH_ALERT` |

### 5.2 Wann wird kein Trail erzeugt?

Kein Trail wird erzeugt bei:

| Ereignis | Begründung |
|---|---|
| Reiner Heartbeat | Zu häufig, kein Entscheidungswert. |
| Jedes einzelne Log-Event | Trail-Map ist kein Ersatz für Operational Logs. |
| Rohdatenaufnahme ohne Entscheidung | Rohdaten gehören in Blackbox/Ledger, nicht Trail-Map. |
| Interne Schleifen ohne Zustandsänderung | Vermeidet Trail-Spam. |
| Registry-Lesezugriff ohne Entscheidung | Kein Entscheidungsereignis. |

### 5.3 Detail-Level

| Detail-Level | Inhalt |
|---|---|
| `MINIMAL` | DecisionType, Zeit, Actor, Entscheidung, Outcome, Hash. Keine Alternativen. |
| `STANDARD` | Zusätzlich Evidenzen, verworfene Alternativen, Policy-Refs. |
| `FULL` | Zusätzlich Parameter-Snapshots, Scores, LLM-Summary, detaillierte Redactions. |

**Regel:** `FULL` darf nur lokal verwendet werden und erhöht Blackbox-Größe. Bei `FULL` muss `max_trail_map_size_mb` strikt geprüft werden.

---

## 6. Hash-Chain und Integrität

### 6.1 Append-only-Regel

Die Trail-Map ist append-only.

```python
def append_trail(trail_map: TrailMap, trail: Trail) -> TrailMap:
    trail.sequence_number = len(trail_map.trails) + 1
    trail.previous_hash = (
        trail_map.trails[-1].entry_hash
        if trail_map.trails
        else None
    )
    trail.entry_hash = canonical_sha256(trail_without_entry_hash(trail))
    trail_map.trails.append(trail)
    return trail_map
```

### 6.2 Finalisierung

Bei `FINALIZING`:

```python
def finalize_trail_map(trail_map: TrailMap) -> TrailMap:
    trail_map.finalized_at = now_iso()
    trail_map.summary = build_summary(trail_map.trails)
    trail_map.digest = canonical_sha256(trail_map_without_digest(trail_map))
    return trail_map
```

### 6.3 Integritätsprüfungen

Beim Schreiben oder Lesen:

| Prüfung | Fehler bei Verletzung |
|---|---|
| `sequence_number` monoton und lückenlos | `TRAIL_SEQUENCE_INVALID` |
| `previous_hash` stimmt mit Vorgänger überein | `TRAIL_HASH_CHAIN_INVALID` |
| `entry_hash` stimmt mit kanonischem Entry überein | `TRAIL_ENTRY_HASH_INVALID` |
| `digest` stimmt mit kanonischer TrailMap überein | `TRAIL_MAP_DIGEST_INVALID` |
| `trail_count` stimmt mit tatsächlicher Länge überein | `TRAIL_SUMMARY_INVALID` |

### 6.4 Kritische Abgrenzung zu Ledger

| Aspekt | ExpeditionLedger | Trail-Map |
|---|---|---|
| Zweck | Ausführungs- und Ergebnisrekonstruktion | Entscheidungsnachvollziehbarkeit |
| Recovery-relevant | Ja, über WAL/Ledger-Kontext | Nein |
| Inhalt | HAL-Ergebnisse, Kosten, Checkpoints, Status | Entscheidungen, Gründe, Alternativen |
| Zugriff | Questor-intern, Result-Builder | Lokal in Blackbox |
| Wird im Ergebnis referenziert | Indirekt über `LocalAuditRef` | Nur Digest/Summary in Blackbox/LocalAudit |
| Wissenschaftlich | Nein, aber Grundlage für Ergebnisdaten | Nein, niemals Signalquelle |

---

## 7. Speicherung

### 7.1 Speicherort

Die Trail-Map wird lokal in der Blackbox gespeichert:

```
data/questor_blackbox/
  └── {blackbox_id}/
      ├── manifest.json
      ├── ledger_snapshot.json
      ├── raw_data/
      ├── llm_advice_log.json
      ├── trail_map.json        ← Trail-Map
      └── error_details.json
```

**Kritische Regel:**  
Die Datei `trail_map.json` wird **nicht** in `data/archiv/`, **nicht** in `data/atlas/` und **nicht** in `data/operational_logs/` gespeichert.

### 7.2 Blackbox-Manifest

Das Blackbox-Manifest erhält eine Referenz:

```yaml
BlackboxManifest:
  blackbox_id: str
  package_id: str
  zyklus_id: str
  attempt_id: int
  includes_trail_map: bool
  trail_map_digest: Optional[str]
  trail_map_redaction_level: Optional[str]
```

### 7.3 LocalAuditRef

Im `questor_ergebnis_paket` erscheint die Trail-Map **nicht als direktes Feld**.

Stattdessen bleibt die bestehende Regel gültig:

```yaml
LocalAuditRef:
  blackbox_id: str
  manifest_checksum: str
  blackbox_digest: str
  redaction_level: NONE | BASIC | STRONG
  retention_class: NORMAL | SAFETY_HOLD | DEVELOPMENT_HOLD
  access_policy_summary: str
```

**Wichtig:**  
Kein Pfad, der automatisch vom Gremium gelesen wird.  
Keine Übergabe der Blackbox selbst.  
Nur Referenz, Digest und Policy-Zusammenfassung.

### 7.4 Ledger-Eintrag zur Trail-Map

Der Ledger darf am Ende einen Summary-Eintrag enthalten:

```yaml
LedgerEntry:
  entry_type: TRAIL_MAP_SUMMARY
  payload:
    trail_map_id: "trail-pkg-001-zyklus-001-0"
    trail_count: 42
    final_digest: "sha256:..."
    redaction_level: BASIC
    local_only: true
  previous_hash: "..."
  entry_hash: "..."
```

**Regel:** Dieser Ledger-Eintrag enthält **keine Trail-Details**.

---

## 8. Redaction und Zugriff

### 8.1 Redaction-Level

| Level | Bedeutung |
|---|---|
| `NONE` | Keine Redaction. Nur für lokale Entwicklung. |
| `BASIC` | IDs, Raw-Prompt-Fragmente und sicherheitsrelevante Felder werden maskiert. |
| `STRONG` | Nur Entscheidungstypen, Hashes, Status, stark verkürzte Rationale. |

### 8.2 Felder, die redigiert werden müssen

| Feld/Inhalt | Redaction-Grund |
|---|---|
| vollständige LLM-Prompts | `LLM_PROMPT` |
| vollständige LLM-Rohantworten | `LLM_PROMPT` / `RAW_DATA` |
| Gate-Details | `SECURITY_RELEVANT` |
| Lease-Details | `SECURITY_RELEVANT` |
| vollständige Parameter-Snapshots bei sensiblen Domänen | `RAW_DATA` |
| interne Policy-Konfiguration | `POLICY_PROTECTED` |
| Pfade zu lokalen Dateien | `SENSITIVE_ID` |
| sicherheitsrelevante Fehlermeldungen | `SECURITY_RELEVANT` |

### 8.3 Zugriffspolitik

| Rolle / Komponente | Zugriff |
|---|---|
| Questor intern | Vollzugriff während Laufzeit |
| Result-Builder | Darf Digest/Summary referenzieren |
| Blackbox-Archiver | Darf Trail-Map lokal speichern |
| Archivar | Kein automatischer Zugriff |
| Atlas | Kein Zugriff |
| Pipeline-Orchestrator | Kein automatischer Zugriff |
| Kanzler | Nur periodische/angeforderte Zusammenfassung, keine Rohdaten |
| Domain-Experte | Zugriff nur explizit autorisiert zur Template-Korrektur |
| LLM | Kein Zugriff |

---

## 9. Fehlerbehandlung

| Fehler | Ursache | Aktion | Fehlerklasse |
|---|---|---|---|
| `TRAIL_POLICY_DISABLED` | `create_trails = false` | Keine Trail-Erzeugung | Kein Fehler |
| `TRAIL_EVIDENCE_MISSING` | `require_evidence = true`, aber keine Evidenz | Trail wird mit Warning gespeichert oder bei kritischer Entscheidung verworfen | OPERATIONAL |
| `TRAIL_MAX_COUNT_EXCEEDED` | Mehr als `max_trails_per_package` | Weitere Trails werden nicht gespeichert; Summary erhält Warning | OPERATIONAL |
| `TRAIL_MAP_SIZE_EXCEEDED` | Datei größer als `max_trail_map_size_mb` | Trail-Map wird finalisiert, keine weiteren Trails | OPERATIONAL |
| `TRAIL_WRITE_FAILED` | Blackbox/Dateisystem nicht beschreibbar | Operational Log schreiben, Ausführung läuft weiter | OPERATIONAL |
| `TRAIL_HASH_CHAIN_INVALID` | Hash-Kette beschädigt | Trail-Map als invalid markieren, nicht für Audit nutzen | OPERATIONAL |
| `TRAIL_REDACTION_FAILED` | Redaction schlägt fehl | Fail-Closed: stärker redigieren oder Trail verwerfen | OPERATIONAL |
| `TRAIL_UNKNOWN_DECISION_TYPE` | Ungültiger DecisionType | Trail verwerfen, Warning | OPERATIONAL |
| `TRAIL_FINALIZE_FAILED` | Finalisierung schlägt fehl | Blackbox ohne Trail-Map schreiben, LocalAuditRef bleibt gültig | OPERATIONAL |

**Kritische Regel:**  
Trail-Map-Fehler dürfen die Paketverarbeitung **nicht abbrechen**.  
Die Trail-Map ist diagnostisch, nicht ausführungsentscheidend.

---

## 10. Edge Cases

| # | Edge Case | Erwartetes Verhalten |
|---|---|---|
| EC-1 | `create_trails = false`, aber Sanitization erkennt Prompt-Injection. | Kein Trail wird erzeugt. Das Sanitization-Audit bleibt im Operational Log / Ledger nach jeweiliger Regel erhalten. |
| EC-2 | `require_evidence = true`, aber ein `LLM_ADVICE_REJECTED` hat keine EvidenceRef. | Trail erhält Warning `TRAIL_EVIDENCE_MISSING`; wenn Detail-Level STANDARD/FULL, muss mindestens eine LLMOutputValidation-Referenz ergänzt werden. |
| EC-3 | Trail-Map erreicht `max_trails_per_package` mitten in EXECUTING. | Weitere Trails werden nicht gespeichert. Summary enthält Warning. Questor läuft weiter. |
| EC-4 | Blackbox-Schreiben schlägt fehl. | `TRAIL_WRITE_FAILED`; Questor baut Ergebnis trotzdem. `LocalAuditRef` muss Blackbox-Fehler in Policy Summary oder OperationalMetrics reflektieren. |
| EC-5 | LLM versucht, aus Trail-Map zu lernen oder sie als Kontext anzufordern. | Verboten. Trail-Map wird dem LLM nie übergeben. Sanitization blockiert entsprechende Felder. |
| EC-6 | Trail-Map enthält versehentlich vollständige Gate-Details. | Redaction muss greifen. Wenn Redaction fehlschlägt: Trail verwerfen oder STRONG Redaction anwenden. |
| EC-7 | PolicyEvaluator VETO erzeugt sowohl LedgerEntry als auch Trail. | Erlaubt, aber Inhalte unterscheiden sich: Ledger = Ereignis/VETO; Trail = Begründung/Alternativen/Evidence. |
| EC-8 | Questor crasht vor Finalisierung der Trail-Map. | Recovery erfolgt aus WAL, nicht Trail-Map. Unfinalisierte Trail-Map darf höchstens diagnostisch genutzt werden. |
| EC-9 | Trail-Map Digest stimmt nicht mit Blackbox-Manifest überein. | Blackbox-Manifest markiert Trail-Map invalid. Ergebnis bleibt gültig, wenn Guardian-Validierung sonst bestanden ist. |
| EC-10 | `FULL` Detail-Level erzeugt zu große Parameter-Snapshots. | `TRAIL_MAP_SIZE_EXCEEDED`; weitere Snapshots werden verworfen, ggf. Wechsel auf STRONG Redaction. |
| EC-11 | Health-Monitoring erzeugt viele Alerts. | Alert-Cooldown liegt im Health-Monitoring; Trail-Map protokolliert nur tatsächliche Health-Alert-Events, nicht jeden Heartbeat. |
| EC-12 | Shutdown während Trail-Finalisierung. | Shutdown hat Vorrang. Trail-Map wird best-effort finalisiert; WAL/Ergebnisbau bleiben wichtiger. |

---

## 11. Sicherheitsregeln

| # | Regel | Fail-Closed-Aktion |
|---|---|---|
| S1 | Trail-Map ist OPERATIONAL, niemals SCIENTIFIC. | Keine Signale, keine Kristalle aus Trails. |
| S2 | Trail-Map bleibt lokal in der Blackbox. | Keine automatische Übergabe an Gremium/Atlas/Archiv. |
| S3 | Trail-Map wird nicht vom LLM gelesen. | Sanitization/Prompt-Building blockiert Zugriff. |
| S4 | Trail-Map ist nicht Recovery-relevant. | Recovery ausschließlich aus WAL. |
| S5 | Trail-Map ist append-only. | Hash-Chain validieren; bei Fehler invalid markieren. |
| S6 | Trail-Map darf kein neues Ergebnisfeld erzeugen. | Nur LocalAuditRef / Blackbox-Manifest / Ledger-Summary. |
| S7 | Sicherheitsrelevante Details werden redigiert. | Bei Redaction-Fehler: STRONG Redaction oder Trail verwerfen. |
| S8 | Trail-Fehler blockieren Questor nicht. | Operational Log, Ausführung läuft weiter. |
| S9 | LLM-Advice bleibt Advisor-only. | Trails dürfen LLM-Rat dokumentieren, aber nicht autorisieren. |
| S10 | Trail-Map-Digest wird protokolliert. | Digest/Summary erlaubt, Detaildaten lokal. |

---

## 12. Integration mit bestehenden Komponenten

### 12.1 QuestCompass

QuestCompass erzeugt Trails für:

| QuestCompass-Aktion | DecisionType |
|---|---|
| Objective-Type bestimmt | `OBJECTIVE_ANALYSIS` |
| Objective-Klärung via LLM | `OBJECTIVE_CLARIFICATION` |
| Template ausgewählt | `LOOP_SELECTION` |
| Parameter gewählt | `PARAMETER_CHOICE` |
| Ergebnis bewertet | `EVALUATION` |
| Re-Planung gestartet | `RE_PLAN` |

Beispiel:

```yaml
Trail:
  decision_type: LOOP_SELECTION
  actor: QUESTCOMPASS
  evidence:
    - evidence_type: TEMPLATE_SCORE
      description: "Template chemie_optimize_v1 hatte höchsten Score"
      value_summary: "score=0.82"
  alternatives_considered:
    - alternative_id: "chemie_explore_v1"
      score: 0.61
      rejection_reason: "objective_type mismatch"
  decision:
    selected_option: "chemie_optimize_v1"
    rationale: "Bestes Template für OPTIMIZE mit verfügbaren Capabilities"
    deterministic: true
    confidence: 0.82
    used_llm_advice: false
    final_authority: QUESTOR_DETERMINISTIC
  outcome:
    status: ACCEPTED
    resulting_state: EXECUTING
```

### 12.2 Sanitization

Sanitization erzeugt Trails für:

| Ereignis | DecisionType |
|---|---|
| Freitextfeld quarantänisiert | `SANITIZATION_QUARANTINE` |
| Input vollständig abgelehnt | `SANITIZATION_REJECT` |
| LLM-Output verworfen | `LLM_ADVICE_REJECTED` |
| LLM-Output akzeptiert | `LLM_ADVICE_ACCEPTED` |

**Wichtig:** Vollständige Prompts und Rohantworten gehören nicht in Trail-Map, sondern höchstens redigiert / als Digest.

### 12.3 Capability-Registry

Capability-Checks werden als Trails protokolliert:

```yaml
Trail:
  decision_type: CAPABILITY_CHECK
  actor: CAPABILITY_REGISTRY
  evidence:
    - evidence_type: CAPABILITY_RESULT
      description: "Capability pipette.transfer verfügbar"
      value_summary: "status=AVAILABLE, slots=1"
  decision:
    selected_option: "AVAILABLE"
    rationale: "Registry, HAL-Manifest und allowed_capabilities bestanden"
    deterministic: true
    used_llm_advice: false
    final_authority: POLICY_EVALUATOR
```

### 12.4 Security-Mode

Security-Mode-Checks werden als Trails protokolliert:

```yaml
Trail:
  decision_type: SECURITY_MODE_CHECK
  actor: SECURITY_MODE_MODULE
  evidence:
    - evidence_type: SECURITY_MODE_RESULT
      description: "Effektiver Modus bestimmt"
      value_summary: "package=NORMAL, gate=NORMAL, effective=NORMAL"
  decision:
    selected_option: "NORMAL"
    rationale: "Restriktivster Modus aus Paket/Gate/System/Slot"
    deterministic: true
    used_llm_advice: false
    final_authority: POLICY_EVALUATOR
```

### 12.5 PolicyEvaluator und SafetyMonitor

| Ereignis | DecisionType |
|---|---|
| Policy GO | `SAFETY_CHECK` |
| Policy VETO | `POLICY_VETO` |
| ESTOP / Interlock erkannt | `SAFETY_CHECK` mit Outcome `ABORTED` |

**Kritische Regel:** ESTOP/Interlock bleibt SAFETY im Ergebnis, aber der Trail selbst bleibt operationales Protokoll.

### 12.6 ExpeditionLedger

Der Ledger erhält nur:
- TrailMapSummaryRef,
- optional einzelne Decision-Event-Hashes bei kritischen Entscheidungen,
- keine vollständigen Trail-Details.

### 12.7 WAL

Keine direkte Integration.

**Regel:** WAL bleibt einziger Recovery-Mechanismus. Trail-Map darf nach Crash nicht zur Wiederaufnahme verwendet werden.

### 12.8 Result-Builder

Result-Builder:
1. finalisiert Trail-Map best-effort,
2. übergibt sie an Blackbox-Archiver,
3. übernimmt nur Digest/Manifest in LocalAuditRef-Kontext,
4. erzeugt keine wissenschaftlichen Signale aus Trails.

### 12.9 Blackbox-Archiver

Blackbox-Archiver speichert `trail_map.json` lokal und ergänzt Manifest-Digest.

### 12.10 Health-Monitoring

Health-Alerts können Trails erzeugen, aber Heartbeats nicht.

### 12.11 Graceful-Shutdown

Shutdown erzeugt `SHUTDOWN_INITIATED`. Bei Shutdown wird Trail-Map best-effort finalisiert.

### 12.12 Queue-Integration

Keine direkte Queue-Sichtbarkeit der Trail-Map.

Die Queue-Registry darf höchstens enthalten:

```yaml
trail_map_present: true
trail_map_digest: "sha256:..."
```

**Aber:** Nur wenn diese Information nicht automatisch zum Gremium-Read der Trail-Map führt.

---

## 13. Validierung durch konkretes Beispiel

### 13.1 Szenario

Ein Chemie-Paket wird geplant. Questor:
1. erkennt Objective `OPTIMIZE`,
2. quarantänisiert eine Prompt-Injection im `ziel`,
3. prüft `pipette.transfer`,
4. wählt Template `chemie_optimize_v1`,
5. verwirft LLM-Rat wegen Safety-Claim,
6. führt deterministisch weiter.

### 13.2 Eingangsbedingungen

```yaml
package_id: "pkg-chemie-001"
zyklus_id: "zyklus-014"
attempt_id: 2
questor_instance_id: "questor-local-001"

initial_trail_policy:
  create_trails: true
  detail_level: STANDARD
  require_evidence: true
  include_llm_advice_summary: true
  include_rejected_alternatives: true
  include_parameter_snapshots: false
  redaction_level: BASIC
```

### 13.3 Beispiel-Trails

#### Trail 1: Sanitization

```yaml
trail_id: "tr-000001-SANITIZATION_QUARANTINE"
sequence_number: 1
timestamp: "2025-07-15T12:00:00Z"
state: PLANNING
decision_type: SANITIZATION_QUARANTINE
actor: SANITIZATION_MODULE
input_refs:
  - ref_type: PACKAGE_FIELD
    ref_id: "ziel"
    digest: "sha256:input-field-digest"
    redacted: true
evidence:
  - evidence_type: SANITIZATION_RESULT
    description: "Injection-Patterns erkannt"
    value_summary: "INJ-01, INJ-04, INJ-07"
    source_ref: "sanitization-result-001"
decision:
  selected_option: "QUARANTINE"
  rationale: "Freitextfeld enthält sicherheitsrelevante Prompt-Injection-Muster"
  deterministic: true
  confidence: null
  used_llm_advice: false
  llm_advice_accepted: null
  final_authority: QUESTOR_DETERMINISTIC
outcome:
  status: ACCEPTED
  resulting_state: PLANNING
  resulting_action: "ziel redacted for LLM"
warnings: []
redactions:
  - field_path: "input_refs[0]"
    reason: SECURITY_RELEVANT
    redaction_level: BASIC
```

#### Trail 2: Objective Analysis

```yaml
trail_id: "tr-000002-OBJECTIVE_ANALYSIS"
sequence_number: 2
timestamp: "2025-07-15T12:00:01Z"
state: PLANNING
decision_type: OBJECTIVE_ANALYSIS
actor: QUESTCOMPASS
input_refs:
  - ref_type: PACKAGE_FIELD
    ref_id: "ziel"
    digest: "sha256:redacted-ziel"
    redacted: true
evidence:
  - evidence_type: POLICY_RULE
    description: "Keyword-Matching"
    value_summary: "Keyword 'Optimiere' → OPTIMIZE"
decision:
  selected_option: "OPTIMIZE"
  rationale: "Deterministische Objective-Erkennung anhand Keyword-Mapping"
  deterministic: true
  confidence: 0.7
  used_llm_advice: false
  llm_advice_accepted: null
  final_authority: QUESTOR_DETERMINISTIC
outcome:
  status: ACCEPTED
  resulting_state: PLANNING
```

#### Trail 3: Capability Check

```yaml
trail_id: "tr-000003-CAPABILITY_CHECK"
sequence_number: 3
timestamp: "2025-07-15T12:00:02Z"
state: PLANNING
decision_type: CAPABILITY_CHECK
actor: CAPABILITY_REGISTRY
input_refs:
  - ref_type: CAPABILITY
    ref_id: "pipette.transfer"
    digest: "sha256:capability-definition"
    redacted: false
evidence:
  - evidence_type: CAPABILITY_RESULT
    description: "Capability verfügbar"
    value_summary: "AVAILABLE; slot_count=1; security_mode=NORMAL"
decision:
  selected_option: "AVAILABLE"
  rationale: "Capability in Registry, HAL-Manifest und allowed_capabilities vorhanden"
  deterministic: true
  confidence: null
  used_llm_advice: false
  llm_advice_accepted: null
  final_authority: POLICY_EVALUATOR
outcome:
  status: ACCEPTED
  resulting_state: PLANNING
```

#### Trail 4: LLM Advice Rejected

```yaml
trail_id: "tr-000004-LLM_ADVICE_REJECTED"
sequence_number: 4
timestamp: "2025-07-15T12:00:05Z"
state: PLANNING
decision_type: LLM_ADVICE_REJECTED
actor: SANITIZATION_MODULE
input_refs:
  - ref_type: LLM_ADVICE
    ref_id: "llm-call-001"
    digest: "sha256:llm-response"
    redacted: true
evidence:
  - evidence_type: LLM_VALIDATION_RESULT
    description: "Safety-Claim im LLM-Output erkannt"
    value_summary: "SAFETY_REJECT"
decision:
  selected_option: "REJECT_LLM_ADVICE"
  rationale: "LLM-Output enthält Safety-Claim und darf nicht verwendet werden"
  deterministic: true
  confidence: null
  used_llm_advice: true
  llm_advice_accepted: false
  final_authority: QUESTOR_DETERMINISTIC
outcome:
  status: REJECTED
  resulting_state: PLANNING
  resulting_action: "deterministic_fallback"
```

#### Trail 5: Loop Selection

```yaml
trail_id: "tr-000005-LOOP_SELECTION"
sequence_number: 5
timestamp: "2025-07-15T12:00:06Z"
state: PLANNING
decision_type: LOOP_SELECTION
actor: QUESTCOMPASS
input_refs:
  - ref_type: TEMPLATE
    ref_id: "chemie_optimize_v1"
    digest: "sha256:template"
    redacted: false
evidence:
  - evidence_type: TEMPLATE_SCORE
    description: "Template-Ranking"
    value_summary: "score=0.82; objective_match=true; capabilities_available=true"
alternatives_considered:
  - alternative_id: "chemie_explore_v1"
    description: "Explorations-Template"
    score: 0.61
    rejection_reason: "Niedrigerer Score für objective_type OPTIMIZE"
    vetoed_by: null
decision:
  selected_option: "chemie_optimize_v1"
  rationale: "Höchster deterministischer Score unter zulässigen Templates"
  deterministic: true
  confidence: 0.82
  used_llm_advice: false
  llm_advice_accepted: null
  final_authority: QUESTOR_DETERMINISTIC
outcome:
  status: ACCEPTED
  resulting_state: EXECUTING
```

### 13.4 Finalisierte TrailMapSummary

```yaml
TrailMapSummary:
  trail_count: 5
  decision_type_counts:
    SANITIZATION_QUARANTINE: 1
    OBJECTIVE_ANALYSIS: 1
    CAPABILITY_CHECK: 1
    LLM_ADVICE_REJECTED: 1
    LOOP_SELECTION: 1
  llm_advice_used_count: 1
  llm_advice_rejected_count: 1
  policy_veto_count: 0
  safety_check_count: 0
  capability_check_count: 1
  sanitization_event_count: 1
  security_mode_check_count: 0
  shutdown_event_count: 0
  health_alert_count: 0
  final_digest: "sha256:trail-map-final"
```

### 13.5 Ergebnis

- Trail-Map dokumentiert die Entscheidungsfolge.
- Keine Trail-Details werden an Atlas/Archiv übergeben.
- LLM-Rat wurde korrekt dokumentiert, aber verworfen.
- Capability-Prüfung ist nachvollziehbar.
- Sanitization-Quarantäne ist nachvollziehbar.
- Das Ergebnis bleibt vertragskonform; keine freien Zusatzfelder außerhalb `questor_metadata`.

---

## 14. Offene Fragen und Risiken

| # | Frage / Risiko | Schweregrad | Empfehlung |
|---|---|---|---|
| Q1 | **Soll `create_trails` wirklich Default false sein?** | Mittel | Ja. Wegen lokaler Blackbox-Sensibilität. Für Debug/Dev kann es aktiviert werden. |
| Q2 | **Wie detailliert darf `FULL` sein?** | Hoch | `FULL` nur lokal, mit Größenlimit und Redaction. Keine automatisierte Weitergabe. |
| Q3 | **Kann Trail-Map bei Audits gebraucht werden?** | Mittel | Ja, aber nur über autorisierten lokalen Blackbox-Zugriff, nicht automatisch. |
| Q4 | **Darf der Archivar Trail-Map lesen?** | Hoch | Nicht automatisch. Nur explizit autorisiert und redigiert. |
| Q5 | **Was passiert bei Widerspruch zwischen Ledger und Trail-Map?** | Hoch | Ledger/WAL gewinnen. Trail-Map wird als diagnostisch invalid markiert. |
| Q6 | **Darf Trail-Map für Template-Korrektur verwendet werden?** | Mittel | Ja, durch Domain-Experten mit autorisiertem Zugriff und Redaction. |
| Q7 | **Wie verhindert man Trail-Spam?** | Mittel | Max Count, Size Limit, keine Heartbeats, keine reinen Log-Events. |
| Q8 | **Kann Trail-Map sensible Sicherheitsdaten enthalten?** | Hoch | Ja. Deshalb Redaction + lokal + kein Auto-Read. |
| Q9 | **Soll Trail-Map im Ledger vollständig gespiegelt werden?** | Kritisch | Nein. Nur Summary/Digest. |
| Q10 | **Kann Trail-Map wissenschaftliche Signale erzeugen?** | Kritisch | Nein. Explizit verboten. |

---

## 15. Zusammenfassung der Spezifikation

| Aspekt | Definition |
|---|---|
| **Modulname** | `trail_map.py` |
| **Position** | `src/questor/trail_map.py` |
| **Zweck** | Lokales Entscheidungsprotokoll |
| **Default** | `create_trails = false` |
| **Speicherung** | `data/questor_blackbox/{blackbox_id}/trail_map.json` |
| **Gremium-Zugriff** | Kein automatischer Zugriff |
| **Atlas/Archiv** | Keine Schreiboperation, keine automatische Übergabe |
| **Recovery** | Keine Recovery-Nutzung; WAL bleibt einzige Recovery-Quelle |
| **Hashing** | Append-only Hash-Chain + finaler Digest |
| **Ledger-Integration** | Nur `TRAIL_MAP_SUMMARY`, keine Details |
| **Result-Integration** | Nur über `LocalAuditRef` / Blackbox-Manifest |
| **DecisionTypes** | 17 definierte Typen |
| **Redaction** | NONE / BASIC / STRONG |
| **Fail-Closed** | Bei Redaction-Fehler: stärker redigieren oder Trail verwerfen |
| **Fehlerklasse** | Immer OPERATIONAL |

---

## 16. Kritische Bewertung der eigenen Spezifikation

### 16.1 Stärken

- Klare Trennung von Ledger, WAL, Blackbox und Trail-Map.
- Keine Verletzung der kanonischen Regel: Questor schreibt nicht in Atlas/Archiv.
- Keine freien Zusatzfelder im `questor_ergebnis_paket`.
- Trail-Map bleibt lokal und operational.
- Append-only Hash-Chain schafft Integrität.
- Redaction-Regeln reduzieren Datenabflussrisiko.
- Neue Themen 1–5 sind integriert:
  - Sanitization,
  - Capability-Registry,
  - Security-Mode,
  - Shutdown,
  - Health-Monitoring.

### 16.2 Schwächen

- Trail-Map erhöht Komplexität und Blackbox-Größe.
- Redaction ist fehleranfällig.
- Bei `FULL` können sensible Details entstehen.
- Widersprüche zwischen Ledger und Trail-Map müssen sauber behandelt werden.
- Default `false` bedeutet: In Standardläufen fehlt detaillierte Entscheidungsnachvollziehbarkeit, wenn nicht explizit aktiviert.

### 16.3 Empfehlung

Die Spezifikation ist implementierungsreif, **unter folgenden Bedingungen**:

1. `create_trails` bleibt Default `false`.
2. Trail-Map wird ausschließlich lokal in der Blackbox gespeichert.
3. Ledger erhält nur Summary/Digest.
4. LLM bekommt niemals Zugriff auf Trail-Map.
5. Recovery nutzt niemals Trail-Map.
6. Result-Builder darf keine wissenschaftlichen Signale aus Trails erzeugen.
7. Redaction muss vor Speicherung validiert werden.
8. Integrationstests müssen prüfen, dass keine Trail-Details in Atlas/Archiv/Queue-Ergebnis gelangen.

---

## 17. Kreuzreferenzen

| Referenz | Beziehung |
|---|---|
| `structure_questor_interna_v0.4.0.md`, Teil P | Dieses Dokument IST Teil P |
| `structure_questor_interna_v0.3.0.md`, Teil F | Abgrenzung zu ExpeditionLedger + WAL |
| `structure_questor_interna_v0.3.0.md`, Teil G | Integration mit Result-Builder und Blackbox |
| `structure_standalone_v2.4.0.md` | Kanonische Regeln: keine Atlas-/Archiv-Schreiboperation, LocalAuditRef |
| `structure_standalone_questor_v0.2.3.md` | `src/questor/trail_map.py`, Blackbox, Ergebnisvertrag |
| `questor_sanitization_v0.1.0.md` | Sanitization-Events werden Trails |
| `questor_capability_registry_v0.1.0.md` | Capability-Checks werden Trails |
| `questor_security_mode_v0.1.0.md` | Security-Mode-Checks werden Trails |
| `questor_graceful_shutdown_v0.1.0.md` | Shutdown erzeugt `SHUTDOWN_INITIATED` |
| `questor_health_monitoring_v0.1.0.md` | Health-Alerts erzeugen `HEALTH_ALERT` |
| `questor_queue_integration_v0.1.0.md` | Keine direkte Trail-Map-Übergabe über Queue |
| `questor_test_strategy_v0.1.0.md` | Unit-Tests U-TM-01 bis U-TM-11 |
| `questor_implementation_plan_v0.1.0.md` | Phase Q13 |
| `myrmex_questor_integration_tests_v0.4.0.md` | Ergebnisvertrag: keine freien Zusatzfelder außerhalb `questor_metadata` |

---

## 18. Datenintegritäts-Check für dieses Dokument

| Prüfpunkttyp | Erwartet | Enthalten |
|---|---:|---:|
| Kritische Probleme | 10 | 10 |
| Datenverträge | 7+ | 11 |
| DecisionTypes | 17 | 17 |
| Edge Cases | 12 | 12 |
| Sicherheitsregeln | 10 | 10 |
| Integrationspunkte | 10+ | 12 |
| Validierungsbeispiel | 1 | 1 |
| Offene Fragen/Risiken | 7+ | 10 |
| Kritische Bewertung | Ja | Ja |
| Kreuzreferenzen | Ja | Ja |