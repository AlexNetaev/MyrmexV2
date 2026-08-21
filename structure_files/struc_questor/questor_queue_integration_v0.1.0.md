# 🧭 QUESTOR-INTERNA: THEMA 7 — GREMIUM-INTEGRATION DER QUEUE
## Dateibasierte Queue, Dispatcher-/Receiver-/Archivar-Protokoll und Registry-Handling

| Feld | Wert |
|---|---|
| Dateiname | `questor_queue_integration_v0.1.0.md` |
| Version | 0.1.0 |
| System | MYRMEX v2.4.0 + Questor v0.2.3 |
| Status | Arbeitsstand — Architektur-Spezifikation, keine Implementierungsfreigabe |
| Bezug | `structure_questor_interna_v0.4.0.md`, Teil Q |
| | `structure_questor_interna_v0.3.0.md`, Teil H (§58–§64) |
| | `structure_standalone_v2.4.0.md` v1.1.1, kanonisch |
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
4. diese Datei: questor_queue_integration_v0.1.0.md          ← Detail: Queue-Integration
5. structure_standalone_questor_v0.2.3.md                    ← unterstützend
6. myrmex_questor_integration_tests_v0.4.0.md                ← Integrationstest-Grundlage
```

Bei Widersprüchen gilt die kanonische Hauptreferenz.

Dieses Dokument ist Teil Q der Questor-Interna-Gesamtspezifikation.
Es ist eigenständig lesbar, setzt aber Grundkenntnisse der Questor-Architektur voraus.

---

## 1. Kritische Analyse des Bestehenden

### 1.1 Was bereits existiert

| Quelle | Referenz | Problem |
|---|---|---|
| `structure_questor_interna_v0.3.0.md` §58 | Queue-Architektur: `pending/`, `processing/`, `completed/`, `failed/`, `delete_requests/`, `registry.json` | **Verzeichnisstruktur definiert, aber kein Dateiformat, kein Schreibprotokoll, keine Registry-Struktur.** |
| `structure_questor_interna_v0.3.0.md` §59 | Questor-Prozess mit Hauptloop | **Questor-seitig definiert. Gremium-seitige Integration fehlt.** |
| `structure_questor_interna_v0.3.0.md` §61 | "Pipeline-Orchestrator liest registry.json und aktualisiert Atlas" | **WAS liest der Orchestrator? WANN? WIE aktualisiert er den Atlas?** |
| `structure_questor_interna_v0.3.0.md` §62 | Löschen von Paketen durch das Gremium | **Delete-Request-Format nicht definiert.** |
| `structure_standalone_v2.4.0.md` §3.2 | Stufe 8: `package_dispatcher → QuestorDispatchEnvelope → QuestorFacade → Questor → questor_ergebnis_paket → result_receiver → Archivar` | **Datenfluss definiert, aber kein Queue-Protokoll.** |
| `structure_standalone_v2.4.0.md` §8.2 | Dispatcher: "erzeugt QuestorDispatchEnvelope" | **Wohin schreibt der Dispatcher? In die Queue? Direkt an Questor?** |
| `structure_standalone_v2.4.0.md` §8.3 | Receiver: "empfängt questor_ergebnis_paket" | **Woher liest der Receiver? Aus der Queue? Direkt von Questor?** |
| `structure_standalone_questor_v0.2.3.md` §6.3 | `QuestorDispatchEnvelope` | Vertrag definiert, aber kein Queue-Schreibprotokoll. |
| `structure_standalone_questor_v0.2.3.md` §8 | Dispatcher-Anpassung | Dispatcher prüft Gate, Lease, Security-Mode, aber kein Queue-Handling. |
| `structure_standalone_questor_v0.2.3.md` §9 | Receiver-Anpassung | Receiver validiert Vertrag, aber kein Queue-Leseprotokoll. |

### 1.2 Identifizierte Probleme

| # | Problem | Schweregrad | Begründung |
|---|---|---|---|
| P1 | **Kein Dateiformat für Queue-Einträge definiert.** Was steht in einer Datei in `pending/`? Was steht in einer Datei in `completed/`? | **KRITISCH** | Ohne Dateiformat kann die Queue nicht implementiert werden. |
| P2 | **Kein Registry-Format definiert.** Was steht in `registry.json`? Welche Felder? Welcher Status? | **KRITISCH** | Ohne Registry-Format kann der Pipeline-Orchestrator die Queue nicht lesen. |
| P3 | **Kein Schreibprotokoll für den Dispatcher.** Wie schreibt der Dispatcher in `pending/`? Atomar? Mit Lock? | Hoch | Ohne Schreibprotokoll können Race Conditions auftreten. |
| P4 | **Kein Leseprotokoll für den Receiver.** Wie liest der Receiver aus `completed/` und `failed/`? Polling? Event? | Hoch | Ohne Leseprotokoll weiß der Receiver nicht, wann ein Ergebnis bereit ist. |
| P5 | **Kein Protokollierungsformat für den Pipeline-Orchestrator.** Was liest der Orchestrator aus `registry.json`? Wie aktualisiert er den Atlas? | Hoch | Ohne Protokollierungsformat kann der Orchestrator den Atlas nicht aktualisieren. |
| P6 | **Kein Delete-Request-Format definiert.** Was steht in einer `.delete`-Datei? | Mittel | Ohne Format kann Questor Delete-Requests nicht verarbeiten. |
| P7 | **Kein Locking-Mechanismus für `registry.json` definiert.** Wer darf wann schreiben? | Hoch | Ohne Locking können Race Conditions auftreten. |
| P8 | **Kein Bereinigungsprotokoll für den Archivar.** Wann und wie bereinigt der Archivar `completed/` und `failed/`? | Mittel | Ohne Bereinigungsprotokoll wächst die Queue unendlich. |
| P9 | **Kein Idempotenz-Schutz für den Dispatcher.** Was passiert, wenn der Dispatcher dasselbe Paket zweimal in `pending/` schreibt? | Hoch | Ohne Idempotenz-Schutz können Duplikate entstehen. |
| P10 | **Kein Fehlerbehandlungsprotokoll.** Was passiert, wenn der Dispatcher nicht schreiben kann? Wenn der Receiver nicht lesen kann? | Mittel | Ohne Fehlerbehandlung ist das System nicht robust. |

### 1.3 Fazit der Analyse

Die Queue-Architektur ist **questor-seitig** gut definiert (Teil H der Questor-Interna v0.3.0), aber die **gremium-seitige Integration** ist eine kritische Lücke. Ohne sie:
- Der Dispatcher weiß nicht, wie er in die Queue schreiben soll.
- Der Receiver weiß nicht, wie er aus der Queue lesen soll.
- Der Pipeline-Orchestrator weiß nicht, wie er die Registry lesen soll.
- Der Archivar weiß nicht, wie er die Queue bereinigen soll.
- Das Gremium weiß nicht, wie es Delete-Requests schreiben soll.

---

## 2. Formale Definition: Queue-Integration

### 2.1 Zweck

Die Queue-Integration definiert das **Protokoll** zwischen dem Gremium (MYRMEX-Pipeline) und Questor für den Austausch von Paketen und Ergebnissen über die dateibasierte Queue.

### 2.2 Architektur-Übersicht

```
┌─────────────────────────────────────────────────────────────────┐
│                        GREMIUM (MYRMEX)                          │
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │  Dispatcher  │    │   Receiver   │    │   Archivar   │       │
│  │  (Stufe 8)   │    │  (Stufe 8)   │    │  (Stufe 1)   │       │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘       │
│         │                   │                   │                │
│         │ SCHREIBEN         │ LESEN             │ BEREINIGEN     │
│         ▼                   ▼                   ▼                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Pipeline-Orchestrator                        │    │
│  │              (liest registry.json)                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                │ Dateisystem
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                    data/questor_queue/                            │
│                                                                   │
│  ├── pending/          ← Dispatcher schreibt, Questor liest     │
│  ├── processing/       ← Questor schreibt/liest (max. 1 Datei)  │
│  ├── completed/        ← Questor schreibt, Receiver liest       │
│  ├── failed/           ← Questor schreibt, Receiver liest       │
│  ├── delete_requests/  ← Gremium schreibt, Questor liest        │
│  └── registry.json     ← Alle schreiben (mit Lock), alle lesen   │
│                                                                   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                │ Dateisystem
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                        QUESTOR-PROZESS                            │
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Facade     │    │  Validator   │    │  Result-     │       │
│  │  (liest      │    │  (prüft      │    │  Builder     │       │
│  │   pending/)  │    │   Pakete)    │    │  (schreibt   │       │
│  │              │    │              │    │   completed/) │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 Grundprinzipien

| Prinzip | Bedeutung |
|---|---|
| **Dateibasiert** | Die Queue ist eine Sammlung von Dateien in einem Verzeichnis. Kein Message Broker, keine Datenbank. |
| **Atomar** | Alle Schreiboperationen sind atomar (temp file + rename). |
| **Idempotent** | Duplikate werden erkannt und verworfen. |
| **Fail-Closed** | Bei Fehlern wird das Paket nicht verloren. Es bleibt in der Queue. |
| **Deterministisch** | Keine Zufälligkeit. Ältestes Paket zuerst. |
| **Single-Writer** | Nur ein Prozess schreibt gleichzeitig in ein Verzeichnis. |
| **Lock-basiert** | `registry.json` wird mit einem Datei-Lock geschützt. |

---

## 3. Queue-Verzeichnisstruktur und Dateiformate

### 3.1 Verzeichnisstruktur

```
data/questor_queue/
  ├── pending/                    ← Wartende Pakete (Dispatcher schreibt)
  │   └── {idempotency_key}.envelope.json
  ├── processing/                 ← Paket in Bearbeitung (Questor schreibt, max. 1 Datei)
  │   └── {idempotency_key}.envelope.json
  ├── completed/                  ← Abgeschlossene Pakete (Questor schreibt)
  │   └── {idempotency_key}.result.json
  ├── failed/                     ← Fehlgeschlagene Pakete (Questor schreibt)
  │   └── {idempotency_key}.result.json
  ├── delete_requests/            ← Löschanfragen vom Gremium
  │   └── {idempotency_key}.delete
  ├── registry.json               ← Status-Übersicht (mit Datei-Lock)
  ├── registry.json.lock          ← Lock-Datei für registry.json
  └── health.json                 ← Health-Status (Thema 5)
```

### 3.2 Dateinamen-Konvention

Der Dateiname wird aus dem `idempotency_key` abgeleitet:

```
idempotency_key = package_id + ":" + zyklus_id + ":" + attempt_id
file_name = idempotency_key.replace(":", "_")
```

**Beispiel:**
- `idempotency_key = "pkg-001:zyklus-014:2"`
- `file_name = "pkg-001_zyklus-014_2"`

**Regeln:**
- `package_id` und `zyklus_id` enthalten nur Zeichen aus `A-Z`, `a-z`, `0-9`, `.`, `_`, `-`.
- Doppelpunkte werden durch Unterstriche ersetzt.
- Die maximale Länge des Dateinamens beträgt 264 Zeichen (wie der `idempotency_key`).

### 3.3 Envelope-Datei (pending/ und processing/)

```json
{
  "schema_version": "0.3.1",
  "file_type": "ENVELOPE",
  "written_by": "DISPATCHER",
  "written_at": "2025-07-15T12:00:00Z",
  "envelope": {
    "dispatch_id": "disp-001",
    "zyklus_id": "zyklus-014",
    "attempt_id": 2,
    "package": {
      "package_id": "pkg-001",
      "source_wegmarke": "wm-kinetik-001",
      "atlas_version_ref": "atlas-v2.4.0-head",
      "ziel": "Optimiere die Reaktionstemperatur für maximale Ausbeute.",
      "parameter_bounds": {
        "temperatur_C": [20.0, 80.0],
        "katalysator_mol": [0.01, 0.5]
      },
      "routing_graph": {
        "max_loop_iterations": 10,
        "branch_condition_timeout": 300
      },
      "questor_spec": {
        "autonomy_level": "GUIDED",
        "clarity_threshold": 0.9,
        "allowed_capabilities": ["pipette.transfer", "spectrometer.measure_absorbance"],
        "allowed_loop_templates": ["chemie_optimize_v1"],
        "budget": {
          "max_duration_s": 3600,
          "max_retry_count": 2,
          "max_llm_calls": 3
        }
      }
    },
    "gate_record_ref": "gate-7781",
    "gate_mode": "NORMAL",
    "lease_grants": [
      {
        "lease_id": "lease-001",
        "slot_id": "slot-roboter-1",
        "ttl_s": 3600
      }
    ],
    "dispatch_mode": "NORMAL",
    "security_mode": "NORMAL",
    "dispatch_timestamp": "2025-07-15T12:00:00Z",
    "idempotency_key": "pkg-001:zyklus-014:2"
  }
}
```

### 3.4 Result-Datei (completed/ und failed/)

```json
{
  "schema_version": "0.3.1",
  "file_type": "RESULT",
  "written_by": "QUESTOR",
  "written_at": "2025-07-15T12:05:00Z",
  "result": {
    "package_id": "pkg-001",
    "zyklus_id": "zyklus-014",
    "attempt_id": 2,
    "idempotency_key": "pkg-001:zyklus-014:2",
    "questor_instance_id": "qi-pkg-001-a1b2c3d4",
    "sequence_number": 5,
    "observed_atlas_version_id": "atlas-v2.4.0-head",
    "status": "erfolgreich",
    "abbruch_grund": null,
    "abbruch_klasse": "OPERATIONAL",
    "routing_checkpoint": {
      "letzter_node": "step_4",
      "iterationen": 2,
      "loops_ausgefuehrt": ["chemie_optimize_v1"]
    },
    "ergebnis_daten": {
      "messwerte": {
        "temperatur_optimum_C": 62.5,
        "ausbeute_prozent": 87.3
      }
    },
    "kristall_kandidaten": [
      {
        "kristall_id": "kristall-001",
        "typ": "kinetik_optimum",
        "loop_template": "chemie_optimize_v1",
        "wert": {"temperatur_C": 62.5, "ausbeute_prozent": 87.3},
        "konfidenz": 0.93,
        "ziel_erreicht": true
      }
    ],
    "signale_fuer_atlas": [
      {
        "signal_typ": "🟩",
        "zone_ref": "zone-kinetik-001"
      }
    ],
    "vollstaendig_flag": true,
    "rohdaten_checksumme": "sha256:a1b2c3d4...",
    "questor_metadata": {
      "questor_version": "0.2.3",
      "local_audit": {
        "blackbox_id": "bb-pkg-001-zyklus-014-2",
        "manifest_checksum": "sha256:...",
        "redaction_level": "STRONG",
        "retention_class": "NORMAL"
      },
      "operational_metrics": {
        "timeout_count": 0,
        "lease_denied_count": 0,
        "llm_advice_rejected_count": 1
      }
    }
  }
}
```

### 3.5 Delete-Request-Datei (delete_requests/)

```json
{
  "schema_version": "0.3.1",
  "file_type": "DELETE_REQUEST",
  "written_by": "KANZLER",
  "written_at": "2025-07-15T12:00:00Z",
  "idempotency_key": "pkg-001:zyklus-014:2",
  "reason": "Paket nicht mehr nötig",
  "requested_by": "kanzler",
  "priority": "NORMAL"
}
```

### 3.6 Registry-Datei (registry.json)

```json
{
  "schema_version": "0.3.1",
  "last_updated": "2025-07-15T12:05:00Z",
  "last_updated_by": "QUESTOR",
  "package_count": 3,
  "packages": {
    "pkg-001:zyklus-014:2": {
      "package_id": "pkg-001",
      "zyklus_id": "zyklus-014",
      "attempt_id": 2,
      "idempotency_key": "pkg-001:zyklus-014:2",
      "status": "COMPLETED",
      "dispatch_timestamp": "2025-07-15T12:00:00Z",
      "processing_started_at": "2025-07-15T12:00:05Z",
      "completed_at": "2025-07-15T12:05:00Z",
      "result_file": "completed/pkg-001_zyklus-014_2.result.json",
      "error_message": null,
      "security_mode": "NORMAL",
      "gate_mode": "NORMAL",
      "questor_instance_id": "qi-pkg-001-a1b2c3d4",
      "sequence_number": 5,
      "delete_requested": false
    },
    "pkg-002:zyklus-015:0": {
      "package_id": "pkg-002",
      "zyklus_id": "zyklus-015",
      "attempt_id": 0,
      "idempotency_key": "pkg-002:zyklus-015:0",
      "status": "PENDING",
      "dispatch_timestamp": "2025-07-15T12:03:00Z",
      "processing_started_at": null,
      "completed_at": null,
      "result_file": null,
      "error_message": null,
      "security_mode": "SANDBOX",
      "gate_mode": "NORMAL",
      "questor_instance_id": null,
      "sequence_number": null,
      "delete_requested": false
    },
    "pkg-003:zyklus-016:1": {
      "package_id": "pkg-003",
      "zyklus_id": "zyklus-016",
      "attempt_id": 1,
      "idempotency_key": "pkg-003:zyklus-016:1",
      "status": "DELETED",
      "dispatch_timestamp": "2025-07-15T11:00:00Z",
      "processing_started_at": null,
      "completed_at": null,
      "result_file": null,
      "error_message": "Delete-Request vom Kanzler",
      "security_mode": "NORMAL",
      "gate_mode": "NORMAL",
      "questor_instance_id": null,
      "sequence_number": null,
      "delete_requested": true
    }
  }
}
```

---

## 4. Dispatcher → Queue (Schreiben)

### 4.1 Ablauf

```
DISPATCHER (Gremium, Stufe 8):
  1. Prüfe: gate_record_ref vorhanden? → NEIN: Abbruch
  2. Prüfe: lease_grants gültig? → NEIN: Abbruch
  3. Prüfe: security_mode passend? → NEIN: Abbruch
  4. Baue QuestorDispatchEnvelope
  5. Berechne idempotency_key
  6. Prüfe: Existiert das Paket bereits in der Queue? → JA: Abbruch (Duplikat)
  7. Schreibe Envelope-Datei nach pending/ (atomar)
  8. Aktualisiere registry.json (mit Lock)
  9. Protokolliere: PACKAGE_DISPATCHED
```

### 4.2 Schreibfunktion (Dispatcher)

```python
def dispatch_to_queue(envelope: QuestorDispatchEnvelope, queue_path: str) -> bool:
    """
    Schreibt ein Envelope in die Queue.
    Returns: True wenn erfolgreich, False wenn Duplikat oder Fehler.
    """
    idempotency_key = envelope.idempotency_key
    file_name = idempotency_key.replace(":", "_") + ".envelope.json"
    pending_path = os.path.join(queue_path, "pending", file_name)
    
    # 1. Prüfe: Existiert das Paket bereits?
    if os.path.exists(pending_path):
        logger.warning(f"Paket bereits in pending/: {idempotency_key}")
        return False
    
    # Prüfe auch processing/, completed/, failed/
    for dir_name in ["processing", "completed", "failed"]:
        dir_path = os.path.join(queue_path, dir_name)
        for f in os.listdir(dir_path):
            if f.startswith(file_name.replace(".envelope.json", "")):
                logger.warning(f"Paket bereits in {dir_name}/: {idempotency_key}")
                return False
    
    # 2. Baue Envelope-Datei
    envelope_file = {
        "schema_version": "0.3.1",
        "file_type": "ENVELOPE",
        "written_by": "DISPATCHER",
        "written_at": now_iso(),
        "envelope": envelope.dict()
    }
    
    # 3. Schreibe atomar (temp file + rename)
    tmp_path = pending_path + ".tmp"
    with open(tmp_path, 'w') as f:
        json.dump(envelope_file, f, indent=2)
    os.rename(tmp_path, pending_path)
    
    # 4. Aktualisiere registry.json (mit Lock)
    update_registry(queue_path, idempotency_key, {
        "package_id": envelope.package.package_id,
        "zyklus_id": envelope.zyklus_id,
        "attempt_id": envelope.attempt_id,
        "idempotency_key": idempotency_key,
        "status": "PENDING",
        "dispatch_timestamp": envelope.dispatch_timestamp,
        "security_mode": envelope.security_mode,
        "gate_mode": envelope.gate_mode,
        "delete_requested": False
    })
    
    logger.info(f"Paket dispatched: {idempotency_key}")
    return True
```

### 4.3 Regeln

| Regel | Beschreibung |
|---|---|
| D-1 | Der Dispatcher schreibt NUR in `pending/`. Niemals in `processing/`, `completed/` oder `failed/`. |
| D-2 | Der Dispatcher schreibt NUR Envelope-Dateien. Niemals Result-Dateien. |
| D-3 | Der Dispatcher prüft VOR dem Schreiben, ob das Paket bereits existiert (Idempotenz). |
| D-4 | Der Dispatcher schreibt atomar (temp file + rename). |
| D-5 | Der Dispatcher aktualisiert `registry.json` mit einem Datei-Lock. |
| D-6 | Der Dispatcher schreibt NUR wenn `gate_record_ref` vorhanden ist. |
| D-7 | Der Dispatcher schreibt NUR wenn `lease_grants` gültig sind. |
| D-8 | Der Dispatcher schreibt NUR wenn `security_mode` zum Gate passt. |

---

## 5. Questor → Queue (Verarbeiten)

### 5.1 Ablauf (Questor-Hauptloop)

```
QUESTOR-HAUPTLOOP:
  1. Prüfe: Gibt es Delete-Requests? → Verarbeiten
  2. Prüfe: Bin ich IDLE?
     → JA: Prüfe pending/ auf Pakete
     → NEIN: Warte auf Abschluss
  3. Wenn Paket gefunden:
     a. Ältestes Paket nehmen (nach dispatch_timestamp)
     b. Prüfe: Ist das Paket bereits in processing/? → JA: Überspringen
     c. Verschiebe Envelope von pending/ nach processing/ (atomar)
     d. Aktualisiere registry.json: status = PROCESSING
     e. Führe Paket aus
     f. Schreibe Result-Datei nach completed/ oder failed/ (atomar)
     g. Verschiebe Envelope aus processing/ (löschen)
     h. Aktualisiere registry.json: status = COMPLETED oder FAILED
  4. Wenn kein Paket:
     → Warte poll_interval_s (Default: 5 Sekunden)
     → Zurück zu Schritt 1
```

### 5.2 Regeln

| Regel | Beschreibung |
|---|---|
| Q-1 | Questor liest NUR aus `pending/`. Niemals aus `completed/` oder `failed/`. |
| Q-2 | Questor schreibt NUR in `processing/`, `completed/` und `failed/`. Niemals in `pending/`. |
| Q-3 | Questor verschiebt das älteste Paket zuerst (nach `dispatch_timestamp`). |
| Q-4 | Questor verarbeitet immer nur EIN Paket gleichzeitig (max. 1 Datei in `processing/`). |
| Q-5 | Questor schreibt Result-Dateien atomar (temp file + rename). |
| Q-6 | Questor aktualisiert `registry.json` mit einem Datei-Lock. |
| Q-7 | Questor prüft Delete-Requests bei jedem Poll-Intervall. |
| Q-8 | Questor löscht Envelope-Dateien aus `processing/` nach Abschluss. |

---

## 6. Receiver → Queue (Lesen)

### 6.1 Ablauf

```
RECEIVER (Gremium, Stufe 8):
  1. Polling: Prüfe completed/ und failed/ auf neue Result-Dateien
  2. Wenn Result-Datei gefunden:
     a. Lese Result-Datei
     b. Validiere QuestorErgebnisPaket
     c. Prüfe idempotency_key
     d. Prüfe sequence_number
     e. Prüfe vollstaendig_flag
     f. Übergebe an Archivar
     g. Markiere Result-Datei als "gelesen" (optional: verschieben nach processed/)
  3. Warte poll_interval_s
  4. Zurück zu Schritt 1
```

### 6.2 Lesefunktion (Receiver)

```python
def poll_for_results(queue_path: str, processed_path: str) -> list[QuestorErgebnisPaket]:
    """
    Liest neue Result-Dateien aus completed/ und failed/.
    Returns: Liste von QuestorErgebnisPaket.
    """
    results = []
    
    for dir_name in ["completed", "failed"]:
        dir_path = os.path.join(queue_path, dir_name)
        if not os.path.exists(dir_path):
            continue
        
        for file_name in sorted(os.listdir(dir_path)):
            if not file_name.endswith(".result.json"):
                continue
            
            file_path = os.path.join(dir_path, file_name)
            
            # Prüfe: Wurde die Datei bereits gelesen?
            processed_file = os.path.join(processed_path, file_name)
            if os.path.exists(processed_file):
                continue
            
            # Lese Result-Datei
            try:
                with open(file_path, 'r') as f:
                    result_file = json.load(f)
                
                result = QuestorErgebnisPaket(**result_file["result"])
                
                # Validiere
                if not result.vollstaendig_flag:
                    logger.error(f"Result-Datei unvollständig: {file_name}")
                    continue
                
                results.append(result)
                
                # Markiere als gelesen
                os.rename(file_path, processed_file)
                
            except Exception as e:
                logger.error(f"Fehler beim Lesen der Result-Datei {file_name}: {e}")
    
    return results
```

### 6.3 Regeln

| Regel | Beschreibung |
|---|---|
| R-1 | Der Receiver liest NUR aus `completed/` und `failed/`. Niemals aus `pending/` oder `processing/`. |
| R-2 | Der Receiver liest NUR Result-Dateien. Niemals Envelope-Dateien. |
| R-3 | Der Receiver validiert das `QuestorErgebnisPaket` vor der Übergabe an den Archivar. |
| R-4 | Der Receiver prüft `vollstaendig_flag`. Wenn `false`, wird das Ergebnis nicht verarbeitet. |
| R-5 | Der Receiver markiert gelesene Result-Dateien als "gelesen" (verschieben nach `processed/`). |
| R-6 | Der Receiver liest NICHT die QuestorBlackbox. |
| R-7 | Der Receiver interpretiert KEINE Questor-internen Trails. |
| R-8 | Der Receiver schreibt NICHT in `pending/`, `processing/`, `completed/` oder `failed/`. |

---

## 7. Pipeline-Orchestrator → Registry (Lesen)

### 7.1 Zweck

Der Pipeline-Orchestrator liest die `registry.json` und aktualisiert den Atlas mit dem Status der Pakete.

### 7.2 Ablauf

```
PIPELINE-ORCHESTRATOR (Gremium):
  1. Polling: Lese registry.json (mit Lock)
  2. Für jedes Paket in der Registry:
     a. Prüfe: Hat sich der Status geändert?
     b. Wenn JA: Aktualisiere den Atlas
        - PENDING → "Paket wartet auf Verarbeitung"
        - PROCESSING → "Paket wird verarbeitet"
        - COMPLETED → "Paket abgeschlossen"
        - FAILED → "Paket fehlgeschlagen"
        - DELETED → "Paket gelöscht"
  3. Warte poll_interval_s
  4. Zurück zu Schritt 1
```

### 7.3 Lesefunktion (Pipeline-Orchestrator)

```python
def read_registry(queue_path: str) -> dict:
    """
    Liest die registry.json mit einem Datei-Lock.
    Returns: Registry-Inhalt als dict.
    """
    registry_path = os.path.join(queue_path, "registry.json")
    lock_path = os.path.join(queue_path, "registry.json.lock")
    
    # Warte auf Lock
    with FileLock(lock_path, timeout=10.0):
        with open(registry_path, 'r') as f:
            return json.load(f)
```

### 7.4 Regeln

| Regel | Beschreibung |
|---|---|
| PO-1 | Der Pipeline-Orchestrator liest NUR die `registry.json`. Niemals die Envelope- oder Result-Dateien. |
| PO-2 | Der Pipeline-Orchestrator schreibt NICHT in die Queue. |
| PO-3 | Der Pipeline-Orchestrator aktualisiert den Atlas basierend auf dem Registry-Status. |
| PO-4 | Der Pipeline-Orchestrator liest die Registry mit einem Datei-Lock. |
| PO-5 | Der Pipeline-Orchestrator aktualisiert den Atlas NICHT für `OPERATIONAL`-Fehler. |
| PO-6 | Der Pipeline-Orchestrator aktualisiert den Atlas NICHT für `SAFETY`-Fehler. |
| PO-7 | Der Pipeline-Orchestrator aktualisiert den Atlas NUR für `SCIENTIFIC`-Ergebnisse. |

---

## 8. Archivar → Ergebnis (Verarbeiten)

### 8.1 Ablauf

```
ARCHIVAR (Gremium, Stufe 1):
  1. Empfängt QuestorErgebnisPaket vom Receiver
  2. Prüft idempotency_key
  3. Prüft sequence_number pro questor_instance_id
  4. Prüft vollstaendig_flag
  5. Trennt abbruch_klasse:
     - OPERATIONAL → Keine wissenschaftlichen Signale
     - SCIENTIFIC → Kristalle und Signale verarbeiten
     - SAFETY → Kristalle und Signale leer, Sicherheitsprüfung
  6. Schreibt Kristalle (nur aus validierten wissenschaftlichen Ergebnissen)
  7. Schreibt Signale (nur aus validierten wissenschaftlichen Ergebnissen)
  8. Protokolliert operational_metrics (optional)
  9. Bereinigt completed/ und failed/ (optional)
```

### 8.2 Bereinigungsfunktion (Archivar)

```python
def cleanup_queue(queue_path: str, processed_path: str, max_age_days: int = 7):
    """
    Bereinigt completed/ und failed/ nach der Archivierung.
    """
    for dir_name in ["completed", "failed"]:
        dir_path = os.path.join(queue_path, dir_name)
        if not os.path.exists(dir_path):
            continue
        
        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)
            
            # Prüfe: Ist die Datei älter als max_age_days?
            file_age = time.time() - os.path.getmtime(file_path)
            if file_age > max_age_days * 86400:
                os.remove(file_path)
                logger.info(f"Result-Datei bereinigt: {file_name}")
    
    # Bereinige auch processed/
    for file_name in os.listdir(processed_path):
        file_path = os.path.join(processed_path, file_name)
        file_age = time.time() - os.path.getmtime(file_path)
        if file_age > max_age_days * 86400:
            os.remove(file_path)
            logger.info(f"Processed-Datei bereinigt: {file_name}")
```

### 8.3 Regeln

| Regel | Beschreibung |
|---|---|
| A-1 | Der Archivar empfängt NUR `QuestorErgebnisPaket`. Niemals Envelope-Dateien. |
| A-2 | Der Archivar liest NICHT die QuestorBlackbox. |
| A-3 | Der Archivar interpretiert KEINE Questor-internen Trails. |
| A-4 | Der Archivar schreibt KEINE wissenschaftlichen Signale bei `OPERATIONAL`. |
| A-5 | Der Archivar schreibt Kristalle NUR aus validierten wissenschaftlichen Ergebnissen. |
| A-6 | Der Archivar bereinigt `completed/` und `failed/` nach der Archivierung. |
| A-7 | Der Archivar bereinigt NICHT `pending/` oder `processing/`. |
| A-8 | Der Archivar aktualisiert `registry.json` nach der Bereinigung. |

---

## 9. Delete-Requests (Gremium → Questor)

### 9.1 Ablauf

```
GREMIUM (Kanzler / Quartiermeister):
  1. Entscheidung: Paket nicht mehr nötig
  2. Schreibe Delete-Request-Datei nach delete_requests/
  3. Aktualisiere registry.json: delete_requested = true

QUESTOR:
  1. Polling: Prüfe delete_requests/ auf neue Delete-Requests
  2. Wenn Delete-Request gefunden:
     a. Prüfe: Ist das Paket in pending/? → JA: Löschen
     b. Prüfe: Ist das Paket in processing/? → JA: NICHT löschen
     c. Prüfe: Ist das Paket in completed/ oder failed/? → JA: NICHT löschen
  3. Aktualisiere registry.json: status = DELETED
  4. Lösche Delete-Request-Datei
```

### 9.2 Regeln

| Regel | Beschreibung |
|---|---|
| DR-1 | Das Gremium schreibt Delete-Requests NUR in `delete_requests/`. |
| DR-2 | Questor prüft Delete-Requests bei jedem Poll-Intervall. |
| DR-3 | Pakete in `pending/` KÖNNEN gelöscht werden. |
| DR-4 | Pakete in `processing/` KÖNNEN NICHT gelöscht werden. |
| DR-5 | Pakete in `completed/` oder `failed/` KÖNNEN NICHT gelöscht werden. |
| DR-6 | Questor aktualisiert `registry.json` nach der Löschung. |
| DR-7 | Questor löscht die Delete-Request-Datei nach der Verarbeitung. |

---

## 10. Zustandsmaschine: Paket-Lebenszyklus in der Queue

```
                    ┌──────────┐
                    │ DISPATCH │ (Dispatcher schreibt Envelope)
                    └────┬─────┘
                         │
                         ▼
                    ┌──────────┐
                    │ PENDING  │ (Envelope in pending/)
                    └────┬─────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
     Questor nimmt   Delete-     Questor nimmt
     Paket auf      Request      Paket NICHT auf
              │          │       (Duplikat)
              ▼          ▼          │
        ┌──────────┐ ┌──────────┐  │
        │PROCESSING│ │ DELETED  │  │
        └────┬─────┘ └──────────┘  │
             │                      │
     ┌───────┼───────┐              │
     │       │       │              │
  SUCCESS  FAILED  ERROR            │
     │       │       │              │
     ▼       ▼       ▼              │
┌──────────┐┌──────────┐           │
│COMPLETED ││ FAILED   │           │
└────┬─────┘└────┬─────┘           │
     │           │                  │
     ▼           ▼                  │
┌──────────┐┌──────────┐           │
│ RECEIVER ││ RECEIVER │           │
│  LIEST   ││  LIEST   │           │
└────┬─────┘└────┬─────┘           │
     │           │                  │
     ▼           ▼                  │
┌──────────┐┌──────────┐           │
│ ARCHIVAR ││ ARCHIVAR │           │
│VERARBEITET│VERARBEITET│          │
└────┬─────┘└────┬─────┘           │
     │           │                  │
     ▼           ▼                  │
┌──────────┐┌──────────┐           │
│BEREINIGT ││BEREINIGT │           │
└──────────┘└──────────┘           │
                                    │
                                    ▼
                              ┌──────────┐
                              │ VERWORFEN│ (Duplikat)
                              └──────────┘
```

### 10.1 Status-Werte

| Status | Bedeutung | Wer setzt ihn? |
|---|---|---|
| `PENDING` | Paket wartet auf Verarbeitung | Dispatcher |
| `PROCESSING` | Paket wird verarbeitet | Questor |
| `COMPLETED` | Paket erfolgreich abgeschlossen | Questor |
| `FAILED` | Paket fehlgeschlagen | Questor |
| `DELETED` | Paket gelöscht | Questor (auf Delete-Request) |
| `RECEIVED` | Ergebnis vom Receiver gelesen | Receiver |
| `ARCHIVED` | Ergebnis vom Archivar archiviert | Archivar |
| `CLEANED` | Result-Datei bereinigt | Archivar |

---

## 11. Fehlerbehandlung

| Fehler | Ursache | Aktion | Fehlerklasse |
|---|---|---|---|
| `QUEUE_WRITE_FAILED` | Dispatcher kann nicht in pending/ schreiben | Fehler protokollieren, Paket nicht dispatchen | OPERATIONAL |
| `QUEUE_READ_FAILED` | Questor kann nicht aus pending/ lesen | Fehler protokollieren, erneut versuchen | OPERATIONAL |
| `QUEUE_MOVE_FAILED` | Questor kann Envelope nicht verschieben | Fehler protokollieren, erneut versuchen | OPERATIONAL |
| `QUEUE_RESULT_WRITE_FAILED` | Questor kann Result nicht schreiben | Fehler protokollieren, WAL flush'd | OPERATIONAL |
| `QUEUE_REGISTRY_LOCK_FAILED` | Registry-Lock kann nicht erworben werden | Warten, erneut versuchen | OPERATIONAL |
| `QUEUE_DUPLICATE_DETECTED` | Paket existiert bereits in der Queue | Paket verwerfen, Duplikat protokollieren | OPERATIONAL |
| `QUEUE_FILE_CORRUPT` | Envelope- oder Result-Datei ist korrupt | Datei quarantine, Fehler protokollieren | OPERATIONAL |
| `QUEUE_DELETE_REQUEST_FAILED` | Delete-Request kann nicht verarbeitet werden | Fehler protokollieren, erneut versuchen | OPERATIONAL |
| `QUEUE_CLEANUP_FAILED` | Archivar kann nicht bereinigen | Fehler protokollieren, erneut versuchen | OPERATIONAL |

**Kritische Regel:** ALLE Queue-Fehler sind `OPERATIONAL`. Ein Queue-Fehler ist NIEMALS ein `SAFETY`-Ereignis und NIEMALS ein `SCIENTIFIC`-Ereignis.

---

## 12. Edge Cases

| # | Edge Case | Erwartetes Verhalten |
|---|---|---|
| EC-1 | Der Dispatcher schreibt dasselbe Paket zweimal in `pending/`. | Zweites Schreiben wird abgelehnt (Duplikat). `QUEUE_DUPLICATE_DETECTED` wird protokolliert. |
| EC-2 | Questor liest ein Paket aus `pending/`, aber die Datei ist korrupt. | `QUEUE_FILE_CORRUPT` wird protokolliert. Datei wird in `quarantine/` verschoben. Paket wird nicht verarbeitet. |
| EC-3 | Questor verschiebt ein Paket von `pending/` nach `processing/`, aber der Rename schlägt fehl. | `QUEUE_MOVE_FAILED` wird protokolliert. Questor versucht es erneut. Nach 3 Fehlversuchen: Alert. |
| EC-4 | Questor schreibt ein Result nach `completed/`, aber die Disk ist voll. | `QUEUE_RESULT_WRITE_FAILED` wird protokolliert. WAL wird flush'd. Questor versucht es erneut. |
| EC-5 | Der Receiver liest ein Result aus `completed/`, aber die Datei wurde bereits vom Archivar bereinigt. | `QUEUE_READ_FAILED` wird protokolliert. Receiver überspringt die Datei. |
| EC-6 | Das Gremium schreibt einen Delete-Request für ein Paket in `processing/`. | Questor löscht das Paket NICHT. Delete-Request wird protokolliert und ignoriert. |
| EC-7 | Zwei Receiver lesen gleichzeitig aus `completed/`. | Jeder Receiver liest nur die Dateien, die er noch nicht gelesen hat. Keine Duplikate. |
| EC-8 | Die `registry.json` ist korrupt. | Questor kann die Registry nicht lesen. `QUEUE_REGISTRY_LOCK_FAILED` wird protokolliert. Questor versucht, die Registry aus den Dateien in den Verzeichnissen zu rekonstruieren. |
| EC-9 | Der Dispatcher schreibt ein Envelope, aber `gate_record_ref` fehlt. | Dispatcher bricht ab. `PACKAGE_INVALID` wird protokolliert. Envelope wird nicht geschrieben. |
| EC-10 | Questor ist in `EXECUTING` und ein Delete-Request kommt. | Questor verarbeitet den Delete-Request NICHT (Paket ist in `processing/`). Delete-Request wird ignoriert. |
| EC-11 | Der Archivar bereinigt `completed/`, aber der Receiver liest noch. | Der Archivar wartet, bis der Receiver die Datei gelesen hat (Lock). |
| EC-12 | Die Queue ist leer und Questor ist `IDLE`. | Questor wartet `poll_interval_s` Sekunden und prüft erneut. Kein Fehler. |

---

## 13. Sicherheitsregeln (Fail-Closed-Punkte)

| # | Regel | Fail-Closed-Aktion |
|---|---|---|
| S1 | **Kein Dispatch ohne gate_record_ref.** Der Dispatcher schreibt NICHT in die Queue, wenn `gate_record_ref` fehlt. | `PACKAGE_INVALID`. |
| S2 | **Kein Dispatch ohne gültige Lease.** Der Dispatcher schreibt NICHT in die Queue, wenn `lease_grants` ungültig sind. | `LEASE_INVALID`. |
| S3 | **Kein Dispatch ohne passenden security_mode.** Der Dispatcher schreibt NICHT in die Queue, wenn `security_mode` nicht zum Gate passt. | `SECURITY_MODE_MISMATCH`. |
| S4 | **Keine Duplikate.** Der Dispatcher prüft VOR dem Schreiben, ob das Paket bereits existiert. | `QUEUE_DUPLICATE_DETECTED`. |
| S5 | **Atomare Schreiboperationen.** Alle Schreiboperationen sind atomar (temp file + rename). | Keine partiellen Dateien. |
| S6 | **Registry-Lock.** `registry.json` wird mit einem Datei-Lock geschützt. | Keine Race Conditions. |
| S7 | **Kein Löschen von processing/.** Pakete in `processing/` können NICHT gelöscht werden. | Delete-Request wird ignoriert. |
| S8 | **Kein Lesen der Blackbox.** Der Receiver und der Archivar lesen NICHT die QuestorBlackbox. | Zugriff ist vertraglich verboten. |
| S9 | **Keine wissenschaftlichen Signale aus OPERATIONAL.** Der Archivar schreibt KEINE wissenschaftlichen Signale bei `OPERATIONAL`. | Keine Kristalle, keine Signale. |
| S10 | **Queue-Fehler sind OPERATIONAL.** Ein Queue-Fehler ist NIEMALS ein `SAFETY`-Ereignis und NIEMALS ein `SCIENTIFIC`-Ereignis. | `abbruch_klasse = OPERATIONAL`. |

---

## 14. Integration mit bestehenden Komponenten

### 14.1 Dispatcher (Gremium, Stufe 8)

Der Dispatcher schreibt Envelope-Dateien in `pending/` und aktualisiert `registry.json`.

### 14.2 Receiver (Gremium, Stufe 8)

Der Receiver liest Result-Dateien aus `completed/` und `failed/` und übergibt sie an den Archivar.

### 14.3 Archivar (Gremium, Stufe 1)

Der Archivar verarbeitet `QuestorErgebnisPaket` und bereinigt `completed/` und `failed/`.

### 14.4 Pipeline-Orchestrator (Gremium)

Der Pipeline-Orchestrator liest `registry.json` und aktualisiert den Atlas.

### 14.5 Kanzler / Quartiermeister (Gremium)

Der Kanzler oder Quartiermeister schreibt Delete-Requests in `delete_requests/`.

### 14.6 Questor-Facade (Questor)

Die Questor-Facade liest aus `pending/`, verschiebt nach `processing/`, und schreibt nach `completed/` oder `failed/`.

### 14.7 Questor-Validator (Questor)

Der Questor-Validator prüft die Envelope-Dateien in `processing/`.

### 14.8 Questor-Result-Builder (Questor)

Der Questor-Result-Builder schreibt Result-Dateien nach `completed/` oder `failed/`.

### 14.9 Questor-Health-Monitoring (Thema 5)

Das Health-Monitoring schreibt `health.json` in die Queue.

### 14.10 WAL (Thema 4)

Der WAL wird bei Shutdown flush'd. Die Queue wird bei Shutdown aktualisiert.

### 14.11 Graceful-Shutdown (Thema 4)

Shutdown aktualisiert die Queue. Die `registry.json` wird mit `status = SHUTDOWN` aktualisiert.

### 14.12 Trail-Map (Thema 6)

Die Trail-Map hat keine direkte Queue-Integration. Trail-Maps werden in der Blackbox gespeichert, nicht in der Queue.

---

## 15. Validierung durch konkretes Beispiel

### 15.1 Szenario: Chemie-Kinetik-Paket durch die Queue

**Schritt 1: Dispatcher schreibt Envelope**

```
Zeit: T+0s
Dispatcher baut QuestorDispatchEnvelope:
  package_id: "pkg-chemie-001"
  zyklus_id: "zyklus-014"
  attempt_id: 2
  idempotency_key: "pkg-chemie-001:zyklus-014:2"
  gate_record_ref: "gate-7781"
  security_mode: "NORMAL"

Dispatcher prüft:
  gate_record_ref vorhanden? → JA
  lease_grants gültig? → JA
  security_mode passend? → JA
  Paket bereits in Queue? → NEIN

Dispatcher schreibt:
  Datei: data/questor_queue/pending/pkg-chemie-001_zyklus-014_2.envelope.json
  Registry: status = PENDING
```

**Schritt 2: Questor liest Envelope**

```
Zeit: T+5s
Questor-Hauptloop prüft pending/:
  → pkg-chemie-001_zyklus-014_2.envelope.json gefunden

Questor verschiebt:
  pending/pkg-chemie-001_zyklus-014_2.envelope.json
  → processing/pkg-chemie-001_zyklus-014_2.envelope.json

Questor aktualisiert Registry:
  status = PROCESSING
  processing_started_at = T+5s
```

**Schritt 3: Questor führt Paket aus**

```
Zeit: T+5s bis T+300s
Questor führt das Paket aus:
  → RECEIVING → VALIDATING → PLANNING → EXECUTING → EVALUATING → FINALIZING
```

**Schritt 4: Questor schreibt Result**

```
Zeit: T+300s
Questor schreibt Result-Datei:
  Datei: data/questor_queue/completed/pkg-chemie-001_zyklus-014_2.result.json
  Inhalt: QuestorErgebnisPaket mit status = "erfolgreich"

Questor löscht Envelope aus processing/:
  processing/pkg-chemie-001_zyklus-014_2.envelope.json → gelöscht

Questor aktualisiert Registry:
  status = COMPLETED
  completed_at = T+300s
  result_file = "completed/pkg-chemie-001_zyklus-014_2.result.json"
```

**Schritt 5: Receiver liest Result**

```
Zeit: T+305s
Receiver pollt completed/:
  → pkg-chemie-001_zyklus-014_2.result.json gefunden

Receiver liest und validiert:
  → QuestorErgebnisPaket gültig
  → vollstaendig_flag = true
  → idempotency_key korrekt
  → sequence_number korrekt

Receiver übergibt an Archivar
Receiver markiert Datei als gelesen
```

**Schritt 6: Archivar verarbeitet Ergebnis**

```
Zeit: T+306s
Archivar empfängt QuestorErgebnisPaket:
  → status = "erfolgreich"
  → abbruch_klasse = "OPERATIONAL"
  → kristall_kandidaten = [kinetik_optimum]
  → signale_fuer_atlas = [🟩]

Archivar schreibt Kristalle und Signale
Archivar protokolliert operational_metrics
```

**Schritt 7: Archivar bereinigt Queue**

```
Zeit: T+7 Tage
Archivar bereinigt completed/:
  → pkg-chemie-001_zyklus-014_2.result.json → gelöscht

Archivar aktualisiert Registry:
  status = CLEANED
```

### 15.2 Ergebnis

Das Paket wurde erfolgreich durch die Queue verarbeitet:
1. Dispatcher schrieb das Envelope in `pending/`.
2. Questor las das Envelope und verarbeitete es.
3. Questor schrieb das Result in `completed/`.
4. Receiver las das Result und übergab es an den Archivar.
5. Archivar verarbeitete das Ergebnis und bereinigte die Queue.

---

## 16. Offene Fragen und Risiken

| # | Frage / Risiko | Schweregrad | Empfehlung |
|---|---|---|---|
| Q1 | **Wer erstellt die Queue-Verzeichnisse?** Questor beim Start? Der Dispatcher? Das Betriebssystem? | Mittel | Empfehlung: Questor erstellt die Verzeichnisse beim Start, wenn sie nicht existieren. |
| Q2 | **Was passiert, wenn die Queue-Verzeichnisse nicht existieren?** | Mittel | Empfehlung: Questor erstellt die Verzeichnisse beim Start. Wenn das fehlschlägt: Questor startet nicht. |
| Q3 | **Was passiert, wenn die Disk voll ist und Questor nicht schreiben kann?** | Hoch | Empfehlung: Questor protokolliert den Fehler und versucht es erneut. Nach 3 Fehlversuchen: Alert. |
| Q4 | **Was passiert, wenn zwei Questor-Instanzen gleichzeitig laufen?** | Hoch | Empfehlung: Questor prüft beim Start, ob bereits eine Instanz läuft (PID-Datei). Wenn ja: Questor startet nicht. |
| Q5 | **Was passiert, wenn der Receiver nicht pollt?** | Mittel | Empfehlung: Der Receiver sollte überwacht werden (Health-Monitoring, Thema 5). |
| Q6 | **Was passiert, wenn der Archivar nicht bereinigt?** | Mittel | Empfehlung: Die Queue wächst unendlich. Ein Cleanup-Job sollte regelmäßig laufen. |
| Q7 | **Sollte die Queue in einer Datenbank statt in Dateien gespeichert werden?** | Niedrig | Empfehlung: NEIN. Die dateibasierte Queue ist einfach, robust und erfordert keine zusätzliche Infrastruktur. |
| Q8 | **Was passiert, wenn die registry.json zu groß wird?** | Niedrig | Empfehlung: Die registry.json sollte regelmäßig bereinigt werden (alte Einträge löschen). |

---

## 17. Zusammenfassung der Spezifikation

| Aspekt | Definition |
|---|---|
| **Queue-Pfad** | `data/questor_queue/` |
| **Verzeichnisse** | `pending/`, `processing/`, `completed/`, `failed/`, `delete_requests/` |
| **Dateiformat** | JSON mit `schema_version`, `file_type`, `written_by`, `written_at` |
| **Dateinamen** | `{idempotency_key}.envelope.json` oder `{idempotency_key}.result.json` |
| **Registry** | `registry.json` mit Datei-Lock |
| **Dispatcher** | Schreibt Envelope in `pending/`, aktualisiert Registry |
| **Questor** | Liest aus `pending/`, schreibt nach `completed/` oder `failed/` |
| **Receiver** | Liest aus `completed/` und `failed/`, übergibt an Archivar |
| **Archivar** | Verarbeitet Ergebnis, bereinigt Queue |
| **Pipeline-Orchestrator** | Liest `registry.json`, aktualisiert Atlas |
| **Delete-Requests** | Gremium schreibt in `delete_requests/`, Questor verarbeitet |
| **Atomare Schreiboperationen** | temp file + rename |
| **Idempotenz** | Duplikate werden erkannt und verworfen |
| **Fehlerbehandlung** | Immer OPERATIONAL, niemals SAFETY, niemals SCIENTIFIC |

---

## 18. Kritische Bewertung der eigenen Spezifikation

**Stärken:**
- Klare Verzeichnisstruktur mit definierten Dateiformaten
- Atomare Schreiboperationen verhindern Race Conditions
- Idempotenz-Schutz verhindert Duplikate
- Registry-Lock verhindert Race Conditions
- Klare Zuständigkeiten (Dispatcher, Questor, Receiver, Archivar)
- Delete-Requests sind klar definiert
- Fehlerbehandlung ist immer OPERATIONAL

**Schwächen:**
- Die Queue ist dateibasiert und kann bei vielen Paketen langsam werden
- Die `registry.json` kann bei vielen Paketen groß werden
- Kein Message Broker für Event-basierte Benachrichtigungen
- Kein automatisches Cleanup für `pending/` und `processing/`

**Empfehlung:** Die Spezifikation ist implementierungsreif, ABER:
1. Die Queue-Verzeichnisse sollten beim Questor-Start erstellt werden.
2. Die `registry.json` sollte regelmäßig bereinigt werden.
3. Ein PID-File sollte verhindern, dass zwei Questor-Instanzen gleichzeitig laufen.
4. Die Queue sollte überwacht werden (Health-Monitoring, Thema 5).

---

## 19. Kreuzreferenzen

| Referenz | Beziehung |
|---|---|
| `structure_questor_interna_v0.4.0.md`, Teil Q | Dieses Dokument IST Teil Q |
| `structure_questor_interna_v0.3.0.md`, Teil H (§58–§64) | Queue-Architektur, Questor-Prozess, Facade, Validator |
| `structure_standalone_v2.4.0.md` §8.1 | Archivar |
| `structure_standalone_v2.4.0.md` §8.2 | Dispatcher |
| `structure_standalone_v2.4.0.md` §8.3 | Receiver |
| `structure_standalone_questor_v0.2.3.md` §6.3 | QuestorDispatchEnvelope |
| `structure_standalone_questor_v0.2.3.md` §8 | Dispatcher-Anpassung |
| `structure_standalone_questor_v0.2.3.md` §9 | Receiver-Anpassung |
| `myrmex_questor_integration_tests_v0.4.0.md` I-01 | Happy Path |
| `myrmex_questor_integration_tests_v0.4.0.md` I-02 | Invalides Paket |
| `myrmex_questor_integration_tests_v0.4.0.md` I-03 | Direktes ResearchPackage verboten |
| `myrmex_questor_integration_tests_v0.4.0.md` I-04 | Envelope ohne gate_record_ref |
| `myrmex_questor_integration_tests_v0.4.0.md` I-15 | Idempotenz im Archivar |
| `questor_sanitization_v0.1.0.md` | Sanitization hat keine direkte Queue-Integration |
| `questor_capability_registry_v0.1.0.md` | Capability-Registry hat keine direkte Queue-Integration |
| `questor_security_mode_v0.1.0.md` | security_mode wird in registry.json protokolliert |
| `questor_graceful_shutdown_v0.1.0.md` | Shutdown aktualisiert die Queue |
| `questor_health_monitoring_v0.1.0.md` | health.json wird in der Queue gespeichert |
| `questor_trail_map_v0.1.0.md` | Trail-Map hat keine direkte Queue-Integration |
| `questor_test_strategy_v0.1.0.md` | 14 Unit-Tests (U-QI-01 bis U-QI-14) |
| `questor_implementation_plan_v0.1.0.md` | Phase Q14 (3-5 Tage) |

---

## 20. Datenintegritäts-Check für dieses Dokument

| Prüfpunkttyp | Erwartet | Enthalten |
|---|---:|---:|
| Kritische Probleme | 10 | 10 |
| Datenverträge / Dateiformate | 4 | 4 (Envelope, Result, Delete-Request, Registry) |
| Zustandsmaschine | 1 | 1 (Paket-Lebenszyklus) |
| Fehlerbehandlungstypen | 9 | 9 |
| Edge Cases | 12 | 12 |
| Sicherheitsregeln | 10 | 10 |
| Integrationspunkte | 10+ | 12 |
| Validierungsbeispiel | 1 | 1 |
| Offene Fragen/Risiken | 8 | 8 |
| Kritische Bewertung | Ja | Ja |
| Kreuzreferenzen | Ja | Ja |