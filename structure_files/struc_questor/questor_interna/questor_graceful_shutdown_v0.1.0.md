# 🧭 QUESTOR-INTERNA: THEMA 4 — QUESTOR-GRACEFUL-SHUTDOWN
## Shutdown-Signale, Phasen, Zustandsverhalten und Crash-Sicherheit

| Feld | Wert |
|---|---|
| Dateiname | `questor_graceful_shutdown_v0.1.0.md` |
| Version | 0.1.0 |
| System | MYRMEX v2.4.0 + Questor v0.2.3 |
| Status | Arbeitsstand — Architektur-Spezifikation, keine Implementierungsfreigabe |
| Bezug | `structure_questor_interna_v0.4.0.md`, Teil N |
| | `structure_standalone_v2.4.0.md` v1.1.1 (kanonisch) |
| | `structure_hal_v0.2.0.md` §12 (Langzeit-Prozessmodell) |
| Sprache | Deutsch |
| Modus | Dry-Run / Spezifikation |

---

## 0. Dokumentenhierarchie und Geltung

```
1. structure_standalone_v2.4.0.md v1.1.1                    ← kanonisch
2. structure_hal_v0.2.0.md                                   ← HAL-Vertrag
3. structure_questor_interna_v0.4.0.md                       ← Questor-Interna GESAMT
4. diese Datei: questor_graceful_shutdown_v0.1.0.md          ← Detail: Graceful-Shutdown
5. structure_standalone_questor_v0.2.3.md                    ← unterstützend
```

Bei Widersprüchen gilt die kanonische Hauptreferenz.

Dieses Dokument ist Teil N der Questor-Interna-Gesamtspezifikation.
Es ist eigenständig lesbar, setzt aber Grundkenntnisse der Questor-Architektur voraus.

---

## 1. Kritische Analyse des Bestehenden

### 1.1 Was bereits referenziert wird

| Quelle | Referenz | Problem |
|---|---|---|
| `structure_questor_interna_v0.3.0.md` §67 | "Questor-Graceful-Shutdown" als offenes Thema (Priorität Niedrig) | **Keine Definition, keine Zustandsmaschine, keine Regeln.** |
| `structure_questor_interna_v0.3.0.md` §59 | Questor-Prozess mit Hauptloop | Kein Shutdown-Pfad im Hauptloop definiert. |
| `structure_questor_interna_v0.3.0.md` §8 | "TOTALFUNKTION: Questor liefert IMMER ein Ergebnis" | **Was passiert, wenn Questor sich beendet, bevor das Ergebnis geliefert wurde?** |
| `structure_questor_interna_v0.3.0.md` §44–§46 | WAL-Lebenszyklus und Recovery | WAL wird nach DONE bereinigt. Aber was, wenn Questor sich vor DONE beendet? |
| `structure_questor_interna_v0.3.0.md` §58 | Queue-Architektur: `processing/` | Was passiert mit dem Paket in `processing/` bei Shutdown? |
| `structure_hal_v0.2.0.md` §12 | Langzeit-Prozessmodell: SAFE_HOLD, RESUME | Wie interagiert Shutdown mit SAFE_HOLD? |

### 1.2 Identifizierte Probleme

| # | Problem | Schweregrad | Begründung |
|---|---|---|---|
| P1 | **Keine Definition, was bei SIGTERM/SIGINT passiert.** Questor ist ein eigener Prozess. Es gibt keinen Signal-Handler. | **KRITISCH** | Ohne Signal-Handler wird Questor bei SIGTERM sofort beendet. Laufende HAL-Kommandos werden nicht aufgeräumt. |
| P2 | **Kein Shutdown-Pfad in der Zustandsmaschine.** Die Übergangstabelle (§6 der Questor-Interna v0.3.0) kennt keinen Shutdown-Übergang. | **KRITISCH** | Implementierer wissen nicht, wie Questor auf ein Shutdown-Signal reagieren soll. |
| P3 | **Totalfunktion-Regel vs. Shutdown.** "Questor liefert IMMER ein Ergebnis" — aber was, wenn Questor sich beendet, bevor das Ergebnis gebaut wurde? | **KRITISCH** | Widerspruch zwischen Totalfunktion und Prozessbeendigung. |
| P4 | **Kein Umgang mit aktiven HAL-Kommandos bei Shutdown.** Wird das Kommando abgewartet? Abbrechen? | Hoch | Ohne Regel kann ein HAL-Kommando mitten in der Ausführung abgebrochen werden. |
| P5 | **Kein Umgang mit Langzeit-Prozessen bei Shutdown.** Was passiert mit einem 72-Stunden-Inkubationsprozess? | Hoch | Prozess könnte zerstört werden. |
| P6 | **Kein WAL-Flush bei Shutdown.** Der WAL muss persistent gespeichert werden, bevor Questor sich beendet. | Hoch | Ohne WAL-Flush ist Recovery nach Neustart unmöglich. |
| P7 | **Kein Queue-Handling bei Shutdown.** Was passiert mit dem Paket in `processing/`? | Mittel | Paket könnte verloren gehen. |
| P8 | **Kein Blackbox-Flush bei Shutdown.** Die Blackbox wird erst bei FINALIZING geschrieben. Bei Shutdown vor FINALIZING geht sie verloren. | Mittel | Datenverlust. |
| P9 | **Kein Lease-Handling bei Shutdown.** Leases müssen freigegeben oder suspendiert werden. | Mittel | Leases könnten hängen bleiben. |
| P10 | **Kein Unterschied zwischen Graceful und Forced Shutdown.** SIGTERM vs. SIGKILL. | Mittel | Implementierer könnten beide gleich behandeln. |

### 1.3 Fazit der Analyse

Der Graceful-Shutdown ist eine **kritische Lücke** in der Questor-Spezifikation. Ohne ihn:
- Laufende HAL-Kommandos werden nicht aufgeräumt.
- Langzeit-Prozesse könnten zerstört werden.
- Der WAL wird nicht flush'd → Recovery nach Neustart unmöglich.
- Die Totalfunktion-Regel wird verletzt.
- Pakete in `processing/` gehen verloren.

---

## 2. Formale Definition: Shutdown-Modul

### 2.1 Zweck

Das Shutdown-Modul definiert das Verhalten von Questor bei einer angeforderten Beendigung. Es stellt sicher, dass:

1. Aktive HAL-Kommandos kontrolliert abgeschlossen oder abgebrochen werden.
2. Langzeit-Prozesse in einen sicheren Zustand (SAFE_HOLD) versetzt werden.
3. Der WAL flush'd wird (Crash-Sicherheit).
4. Ein vollständiges `questor_ergebnis_paket` geliefert wird (Totalfunktion).
5. Die Queue konsistent bleibt.
6. Leases freigegeben oder suspendiert werden.

### 2.2 Shutdown-Signale

| Signal | Quelle | Bedeutung | Abfangbar? |
|---|---|---|---|
| `SIGTERM` | Betriebssystem / Orchestrator (z.B. Kubernetes) | Graceful Shutdown anfordern | JA |
| `SIGINT` | Terminal (Ctrl+C) | Graceful Shutdown anfordern | JA |
| `SIGKILL` | Betriebssystem / OOM-Killer | Sofortige Beendigung | **NEIN** |
| `shutdown.flag` | Datei-basiert (für Systeme ohne Signal-Support) | Graceful Shutdown anfordern | JA (Polling) |
| `ESTOP` | HAL / Sicherheitskette | Sicherheitsabbruch (kein Shutdown, aber verwandt) | JA |

### 2.3 Shutdown-Phasen

```
PHASE 1: SIGNAL_RECEIVED
  → Shutdown-Signal empfangen
  → Shutdown-Timer starten
  → Keine neuen Pakete aus der Queue nehmen

PHASE 2: DRAINING
  → Aktuelles HAL-Kommando abwarten (mit Timeout)
  → Aktive Langzeit-Prozesse in SAFE_HOLD versetzen
  → Keine neuen HAL-Kommandos senden

PHASE 3: FINALIZING
  → Ergebnis bauen (GRACEFUL_SHUTDOWN)
  → Blackbox schreiben
  → WAL flush'd
  → Queue aktualisieren

PHASE 4: TERMINATED
  → Questor-Prozess beendet
```

### 2.4 Shutdown-Konfiguration

```yaml
ShutdownConfig:
  graceful_shutdown_timeout_s: float    # Default: 60.0
  hal_command_wait_timeout_s: float     # Default: 30.0
  process_hold_timeout_s: float         # Default: 30.0
  result_build_timeout_s: float         # Default: 10.0
  wal_flush_timeout_s: float            # Default: 5.0
  shutdown_flag_path: str               # Default: "data/questor_queue/shutdown.flag"
  poll_shutdown_flag_interval_s: float  # Default: 5.0
```

### 2.5 Shutdown-Ergebnis

```yaml
ShutdownResult:
  status: COMPLETED | TIMEOUT | FORCED
  shutdown_reason: SIGTERM | SIGINT | SHUTDOWN_FLAG | OOM_KILL
  active_hal_command_handled: bool
  active_process_safe_held: bool
  result_delivered: bool
  wal_flushed: bool
  queue_updated: bool
  leases_released: bool
  duration_s: float
```

---

## 3. Zustandsmaschine: Shutdown in jedem Questor-Zustand

### 3.1 Übersicht

| Questor-Zustand | Shutdown-Aktion | Ergebnis |
|---|---|---|
| `IDLE` | Sofort beenden. Keine aktiven Pakete. | `ShutdownResult.status = COMPLETED` |
| `RECEIVING` | Envelope ablehnen. Zurück nach `IDLE`. Sofort beenden. | `ShutdownResult.status = COMPLETED` |
| `VALIDATING` | Validierung abbrechen. Ergebnis als `GRACEFUL_SHUTDOWN` bauen. | `ShutdownResult.status = COMPLETED` |
| `PLANNING` | Planung abbrechen. Ergebnis als `GRACEFUL_SHUTDOWN` bauen. | `ShutdownResult.status = COMPLETED` |
| `EXECUTING` | HAL-Kommando abwarten. Prozess in SAFE_HOLD. Ergebnis als `GRACEFUL_SHUTDOWN` bauen. | `ShutdownResult.status = COMPLETED` oder `TIMEOUT` |
| `EVALUATING` | Evaluation abbrechen. Ergebnis als `GRACEFUL_SHUTDOWN` bauen. | `ShutdownResult.status = COMPLETED` |
| `WAITING_FOR_RELEASE` | Ergebnis als `GRACEFUL_SHUTDOWN` bauen. Prozess bleibt in `WAITING_FOR_RELEASE`. | `ShutdownResult.status = COMPLETED` |
| `SAFE_HOLD` | Ergebnis als `GRACEFUL_SHUTDOWN` bauen. Prozess bleibt in `SAFE_HOLD`. | `ShutdownResult.status = COMPLETED` |
| `RECOVERING` | Recovery abbrechen. Ergebnis als `GRACEFUL_SHUTDOWN` bauen. | `ShutdownResult.status = COMPLETED` |
| `FINALIZING` | Ergebnis fertigstellen und liefern. Dann beenden. | `ShutdownResult.status = COMPLETED` |
| `DONE` | Sofort beenden. | `ShutdownResult.status = COMPLETED` |

### 3.2 Detaillierte Zustandsübergänge

```
                    ┌──────────────────────────────────────────────────┐
                    │              SHUTDOWN-SIGNAL                     │
                    └──────────────────────┬───────────────────────────┘
                                           │
                    ┌──────────────────────▼───────────────────────────┐
                    │           SHUTDOWN_SIGNAL_RECEIVED                │
                    │  → Shutdown-Timer starten                        │
                    │  → shutdown_requested = true                     │
                    │  → Keine neuen Pakete aus Queue nehmen           │
                    └──────────────────────┬───────────────────────────┘
                                           │
                    ┌──────────────────────▼───────────────────────────┐
                    │              SHUTDOWN_DRAINING                    │
                    │  → Aktuelles HAL-Kommando abwarten               │
                    │  → Aktive Prozesse in SAFE_HOLD                  │
                    │  → Keine neuen HAL-Kommandos                     │
                    └──────────────────────┬───────────────────────────┘
                                           │
                    ┌──────────────────────▼───────────────────────────┐
                    │             SHUTDOWN_FINALIZING                   │
                    │  → Ergebnis bauen (GRACEFUL_SHUTDOWN)            │
                    │  → Blackbox schreiben                            │
                    │  → WAL flush'd                                   │
                    │  → Queue aktualisieren                           │
                    │  → Leases freigeben                              │
                    └──────────────────────┬───────────────────────────┘
                                           │
                    ┌──────────────────────▼───────────────────────────┐
                    │             SHUTDOWN_TERMINATED                   │
                    │  → Questor-Prozess beendet                       │
                    └──────────────────────────────────────────────────┘
```

### 3.3 Sonderfall: Shutdown während `EXECUTING`

```
EXECUTING + Shutdown-Signal
    │
    ├── Ist ein HAL-Kommando aktiv?
    │   ├── JA: Warte auf Abschluss (max. hal_command_wait_timeout_s)
    │   │   ├── Abschluss erfolgreich → Weiter
    │   │   ├── Timeout → Kommando abbrechen (OPERATIONAL)
    │   │   └── Fehler → Kommando abbrechen (OPERATIONAL)
    │   └── NEIN: Weiter
    │
    ├── Ist ein Langzeit-Prozess aktiv?
    │   ├── JA: SAFE_HOLD anfragen (max. process_hold_timeout_s)
    │   │   ├── SAFE_HOLD erfolgreich → resume_token speichern
    │   │   ├── Timeout → Prozess abbrechen (OPERATIONAL)
    │   │   └── Fehler → Prozess abbrechen (OPERATIONAL)
    │   └── NEIN: Weiter
    │
    └── Ergebnis bauen:
        status: abgebrochen
        abbruch_grund: GRACEFUL_SHUTDOWN
        abbruch_klasse: OPERATIONAL
```

### 3.4 Sonderfall: Shutdown während `FINALIZING`

```
FINALIZING + Shutdown-Signal
    │
    ├── Ergebnis bereits gebaut?
    │   ├── JA: Ergebnis liefern, dann beenden
    │   └── NEIN: Ergebnis bauen, dann liefern, dann beenden
    │
    └── Questor beendet sich NACH dem Liefern des Ergebnisses
```

**Regel:** Wenn Questor bereits in `FINALIZING` ist, wird das Ergebnis IMMER fertiggestellt und geliefert, bevor Questor sich beendet. Der Shutdown-Timer wird in diesem Fall ignoriert (aber protokolliert).

### 3.5 Sonderfall: Shutdown während `WAITING_FOR_RELEASE` oder `SAFE_HOLD`

```
WAITING_FOR_RELEASE / SAFE_HOLD + Shutdown-Signal
    │
    ├── Ergebnis bauen (GRACEFUL_SHUTDOWN)
    ├── Prozess bleibt in WAITING_FOR_RELEASE / SAFE_HOLD
    ├── resume_token im WAL speichern
    ├── WAL flush'd
    ├── Questor beendet sich
    │
    └── Nach Neustart: Questor kann den Prozess fortsetzen
```

**Regel:** Der Prozess wird NICHT zerstört. Er bleibt in seinem aktuellen Wartezustand. Nach einem Neustart kann Questor den Prozess fortsetzen, wenn die Freigabe erteilt wird oder der resume_token gültig ist.

---

## 4. Input/Output-Verträge

### 4.1 Shutdown-Handler (Signal)

```python
def handle_shutdown_signal(signum: int, frame: Any) -> None:
    """
    Signal-Handler für SIGTERM und SIGINT.
    """
    logger.info(f"Shutdown-Signal empfangen: {signum}")
    
    # Shutdown-Flag setzen
    shutdown_state.requested = True
    shutdown_state.signal = signum
    shutdown_state.timestamp = now_iso()
    
    # Shutdown-Timer starten
    shutdown_state.timer = threading.Timer(
        shutdown_config.graceful_shutdown_timeout_s,
        force_shutdown
    )
    shutdown_state.timer.start()
    
    # Hauptloop informieren
    main_loop_event.set()
```

### 4.2 Shutdown-Handler (Datei)

```python
def check_shutdown_flag() -> bool:
    """
    Prüft, ob eine shutdown.flag-Datei existiert.
    Wird im Hauptloop aufgerufen.
    """
    if os.path.exists(shutdown_config.shutdown_flag_path):
        logger.info("Shutdown-Flag erkannt")
        shutdown_state.requested = True
        shutdown_state.signal = "SHUTDOWN_FLAG"
        shutdown_state.timestamp = now_iso()
        return True
    return False
```

### 4.3 Graceful-Shutdown-Prozedur

```python
def graceful_shutdown() -> ShutdownResult:
    """
    Führt den Graceful-Shutdown durch.
    """
    result = ShutdownResult(
        status="COMPLETED",
        shutdown_reason=shutdown_state.signal,
        active_hal_command_handled=False,
        active_process_safe_held=False,
        result_delivered=False,
        wal_flushed=False,
        queue_updated=False,
        leases_released=False,
        duration_s=0.0
    )
    
    start_time = time.time()
    
    try:
        # PHASE 1: Keine neuen Pakete
        facade.stop_accepting_new_packages()
        
        # PHASE 2: DRAINING
        if questor_state.current_state == "EXECUTING":
            # Aktives HAL-Kommando abwarten
            result.active_hal_command_handled = drain_active_hal_command()
            
            # Aktive Prozesse in SAFE_HOLD
            result.active_process_safe_held = drain_active_processes()
        
        # PHASE 3: FINALIZING
        if questor_state.current_package is not None:
            # Ergebnis bauen
            build_shutdown_result(result)
            result.result_delivered = True
        
        # WAL flush'd
        result.wal_flushed = flush_wal()
        
        # Queue aktualisieren
        result.queue_updated = update_queue_after_shutdown()
        
        # Leases freigeben
        result.leases_released = release_leases()
        
        # Blackbox schreiben
        write_blackbox_on_shutdown()
        
    except Exception as e:
        logger.error(f"Fehler während Graceful-Shutdown: {e}")
        result.status = "TIMEOUT"
    
    result.duration_s = time.time() - start_time
    return result
```

### 4.4 Force-Shutdown-Prozedur

```python
def force_shutdown() -> None:
    """
    Wird aufgerufen, wenn der Graceful-Shutdown-Timeout erreicht ist.
    """
    logger.warning("Graceful-Shutdown-Timeout erreicht. Force-Shutdown.")
    
    # WAL flush'd (letzte Chance)
    try:
        flush_wal()
    except Exception as e:
        logger.error(f"WAL-Flush bei Force-Shutdown fehlgeschlagen: {e}")
    
    # Prozess beenden
    os._exit(1)
```

### 4.5 Shutdown-Ergebnis im `questor_ergebnis_paket`

```python
def build_shutdown_result(context: ExecutionContext) -> QuestorErgebnisPaket:
    """
    Baut das Ergebnis bei Graceful-Shutdown.
    """
    return QuestorErgebnisPaket(
        package_id=context.package_id,
        zyklus_id=context.zyklus_id,
        attempt_id=context.attempt_id,
        idempotency_key=f"{context.package_id}:{context.zyklus_id}:{context.attempt_id}",
        questor_instance_id=context.questor_instance_id,
        sequence_number=get_next_sequence(context.questor_instance_id),
        observed_atlas_version_id=context.atlas_version_ref,
        status="abgebrochen",
        abbruch_grund="GRACEFUL_SHUTDOWN",
        abbruch_klasse="OPERATIONAL",
        routing_checkpoint=RoutingCheckpoint(
            letzter_node=context.current_node,
            iterationen=context.iteration_count,
            loops_ausgefuehrt=context.executed_loops
        ),
        ergebnis_daten=ErgebnisDaten(messwerte=context.partial_results),
        kristall_kandidaten=[],
        signale_fuer_atlas=[],
        vollstaendig_flag=True,
        rohdaten_checksumme=calculate_checksum(context.partial_results),
        questor_metadata=QuestorMetadata(
            questor_version=QUESTOR_VERSION,
            policy_version=POLICY_VERSION,
            local_audit=LocalAuditRef(...),
            operational_metrics=context.operational_metrics
        )
    )
```

---

## 5. Fehlerbehandlung

| Fehler | Ursache | Aktion | Fehlerklasse |
|---|---|---|---|
| `SHUTDOWN_SIGNAL_RECEIVED` | SIGTERM/SIGINT empfangen | Graceful-Shutdown einleiten | OPERATIONAL |
| `SHUTDOWN_FLAG_DETECTED` | shutdown.flag-Datei erkannt | Graceful-Shutdown einleiten | OPERATIONAL |
| `SHUTDOWN_TIMEOUT` | Graceful-Shutdown-Timeout erreicht | Force-Shutdown | OPERATIONAL |
| `SHUTDOWN_HAL_COMMAND_TIMEOUT` | HAL-Kommando nicht innerhalb Timeout abgeschlossen | Kommando abbrechen | OPERATIONAL |
| `SHUTDOWN_PROCESS_HOLD_TIMEOUT` | Prozess nicht innerhalb Timeout in SAFE_HOLD | Prozess abbrechen | OPERATIONAL |
| `SHUTDOWN_RESULT_BUILD_FAILED` | Ergebnis konnte nicht gebaut werden | WAL flush'd, Paket in processing/ lassen | OPERATIONAL |
| `SHUTDOWN_WAL_FLUSH_FAILED` | WAL konnte nicht flush'd werden | Force-Shutdown | OPERATIONAL |
| `SHUTDOWN_QUEUE_UPDATE_FAILED` | Queue konnte nicht aktualisiert werden | Force-Shutdown | OPERATIONAL |
| `SHUTDOWN_LEASE_RELEASE_FAILED` | Leases konnten nicht freigegeben werden | Force-Shutdown (Leases laufen aus) | OPERATIONAL |
| `SHUTDOWN_BLACKBOX_WRITE_FAILED` | Blackbox konnte nicht geschrieben werden | Force-Shutdown (Blackbox verloren) | OPERATIONAL |

**Kritische Regel:** ALLE Shutdown-Fehler sind `OPERATIONAL`. Ein Shutdown-Fehler ist NIEMALS ein `SAFETY`-Ereignis und NIEMALS ein `SCIENTIFIC`-Ereignis.

**Kritische Regel:** Wenn der Graceful-Shutdown fehlschlägt, wird der Force-Shutdown ausgelöst. Der Force-Shutdown beendet den Prozess sofort, ohne ein Ergebnis zu liefern. Das Paket bleibt in `processing/` und kann nach einem Neustart aus dem WAL wiederhergestellt werden.

---

## 6. Edge Cases

| # | Edge Case | Erwartetes Verhalten |
|---|---|---|
| EC-1 | Questor ist in `IDLE` und empfängt SIGTERM. | Questor beendet sich sofort. Keine aktiven Pakete. `ShutdownResult.status = COMPLETED`. |
| EC-2 | Questor ist in `EXECUTING` und ein HAL-Kommando läuft seit 25 Sekunden. `hal_command_wait_timeout_s = 30`. SIGTERM kommt. | Questor wartet noch 5 Sekunden auf das HAL-Kommando. Wenn es abgeschlossen wird: Ergebnis bauen. Wenn nicht: Kommando abbrechen, Ergebnis als `GRACEFUL_SHUTDOWN` bauen. |
| EC-3 | Questor ist in `EXECUTING` und ein 72-Stunden-Inkubationsprozess läuft. SIGTERM kommt. | Questor sendet `hold_process()` an HAL. Prozess geht in `SAFE_HOLD`. `resume_token` wird im WAL gespeichert. Ergebnis als `GRACEFUL_SHUTDOWN` bauen. Questor beendet sich. |
| EC-4 | Questor ist in `EXECUTING` und der HAL ist nicht erreichbar (Netzwerkfehler). SIGTERM kommt. | Questor kann das HAL-Kommando nicht abwarten. Questor kann den Prozess nicht in SAFE_HOLD versetzen. Ergebnis als `GRACEFUL_SHUTDOWN` bauen. WAL flush'd. Questor beendet sich. Nach Neustart: Recovery aus WAL. |
| EC-5 | Questor ist in `FINALIZING` und das Ergebnis wurde bereits gebaut, aber noch nicht geliefert. SIGTERM kommt. | Questor liefert das Ergebnis. Dann beendet sich Questor. `ShutdownResult.status = COMPLETED`. |
| EC-6 | Questor ist in `WAITING_FOR_RELEASE` und wartet auf eine manuelle Freigabe. SIGTERM kommt. | Questor baut das Ergebnis als `GRACEFUL_SHUTDOWN`. Der Prozess bleibt in `WAITING_FOR_RELEASE`. Questor beendet sich. Nach Neustart: Questor kann den Prozess fortsetzen, wenn die Freigabe erteilt wird. |
| EC-7 | Questor empfängt SIGTERM und dann SIGKILL (z.B. OOM-Killer) innerhalb von 100ms. | Questor hat keine Zeit für Graceful-Shutdown. Prozess wird sofort beendet. WAL wurde möglicherweise nicht flush'd. Nach Neustart: Recovery aus WAL (wenn möglich) oder `RECOVERY_UNSAFE`. |
| EC-8 | Questor ist in `RECOVERING` und empfängt SIGTERM. | Questor bricht die Recovery ab. Ergebnis als `GRACEFUL_SHUTDOWN` bauen. WAL flush'd. Questor beendet sich. Nach Neustart: Recovery wird erneut versucht. |
| EC-9 | Questor empfängt SIGTERM während des WAL-Flush. | WAL-Flush wird abgebrochen. Questor beendet sich. Nach Neustart: Recovery aus WAL (wenn möglich) oder `RECOVERY_UNSAFE`. |
| EC-10 | Questor empfängt SIGTERM, aber das Ergebnis kann nicht gebaut werden (z.B. Ledger ist korrupt). | Questor versucht, den WAL zu flush'd. Wenn das fehlschlägt: Force-Shutdown. Paket bleibt in `processing/`. Nach Neustart: Recovery aus WAL. |
| EC-11 | Questor empfängt SIGTERM, aber die Queue-Datei ist gesperrt (anderer Prozess schreibt). | Questor wartet auf die Queue-Datei (max. 5 Sekunden). Wenn die Sperre nicht aufgehoben wird: Force-Shutdown. Queue wird nicht aktualisiert. Nach Neustart: Queue wird erneut geprüft. |
| EC-12 | Questor empfängt SIGTERM, aber die Blackbox-Datei ist zu groß (> 100MB). | Questor schreibt die Blackbox nicht (Limit erreicht). Ergebnis wird trotzdem gebaut. Blackbox-Verlust wird protokolliert. |

---

## 7. Sicherheitsregeln (Fail-Closed-Punkte)

| # | Regel | Fail-Closed-Aktion |
|---|---|---|
| S1 | **Keine neuen Pakete bei Shutdown.** Sobald `shutdown_requested = true`, werden keine neuen Pakete aus der Queue genommen. | Paket bleibt in `pending/`. |
| S2 | **Keine neuen HAL-Kommandos bei Shutdown.** Sobald `shutdown_requested = true`, werden keine neuen HAL-Kommandos gesendet. | HAL-Kommando wird nicht gesendet. |
| S3 | **WAL-Flush ist obligatorisch.** Der WAL MUSS vor der Beendigung flush'd werden. Wenn das fehlschlägt: Force-Shutdown. | Force-Shutdown. |
| S4 | **Ergebnis wird gebaut, wenn möglich.** Wenn Questor ein Paket verarbeitet, wird das Ergebnis als `GRACEFUL_SHUTDOWN` gebaut. | Wenn das Ergebnis nicht gebaut werden kann: Force-Shutdown. |
| S5 | **Langzeit-Prozesse werden in SAFE_HOLD versetzt.** Wenn ein Langzeit-Prozess läuft, wird er in SAFE_HOLD versetzt. | Wenn SAFE_HOLD nicht möglich ist: Prozess wird abgebrochen. |
| S6 | **Leases werden freigegeben.** Leases werden bei Shutdown freigegeben. | Wenn die Freigabe fehlschlägt: Leases laufen aus (TTL). |
| S7 | **ESTOP hat Vorrang vor Shutdown.** Wenn ein ESTOP aktiv ist, wird der Shutdown als ESTOP-Abort behandelt. | Ergebnis als `ESTOP_RECEIVED` bauen, nicht als `GRACEFUL_SHUTDOWN`. |
| S8 | **Shutdown ist OPERATIONAL.** Ein Shutdown ist NIEMALS ein SAFETY-Ereignis und NIEMALS ein SCIENTIFIC-Ereignis. | `abbruch_klasse = OPERATIONAL`. |
| S9 | **Shutdown-Timeout ist hart.** Wenn der Graceful-Shutdown-Timeout erreicht ist, wird der Force-Shutdown ausgelöst. | Force-Shutdown. |
| S10 | **Blackbox wird geschrieben, wenn möglich.** Die Blackbox wird bei Shutdown geschrieben, wenn das Limit nicht erreicht ist. | Wenn das Limit erreicht ist: Blackbox wird nicht geschrieben. |

---

## 8. Integration mit bestehenden Komponenten

### 8.1 Questor-Zustandsmaschine

Der Shutdown wird als **externer Trigger** behandelt, der in jedem Zustand empfangen werden kann. Die Zustandsmaschine wird um einen Shutdown-Handler erweitert:

```python
# In der Zustandsmaschine:
if shutdown_state.requested:
    if current_state == "IDLE":
        terminate()
    elif current_state == "FINALIZING":
        finish_and_terminate()
    else:
        graceful_shutdown()
```

### 8.2 QuestCompass

QuestCompass wird bei Shutdown **nicht** aufgerufen. Die Planung wird abgebrochen. Das Ergebnis wird als `GRACEFUL_SHUTDOWN` gebaut, ohne dass QuestCompass eine Entscheidung trifft.

### 8.3 HAL-Bridge

Die HAL-Bridge wird bei Shutdown aufgerufen, um:
1. Aktive HAL-Kommandos abzuwarten.
2. Aktive Langzeit-Prozesse in SAFE_HOLD zu versetzen.
3. Leases freizugeben.

```python
# HAL-Bridge bei Shutdown:
def shutdown_hal_bridge():
    # Aktive Kommandos abwarten
    for command_id in active_commands:
        wait_for_command(command_id, timeout=hal_command_wait_timeout_s)
    
    # Aktive Prozesse in SAFE_HOLD
    for process_id in active_processes:
        hold_process(process_id)
    
    # Leases freigeben
    for lease in active_leases:
        release_lease(lease)
```

### 8.4 ExpeditionLedger

Das Ledger wird bei Shutdown als `READ_ONLY` markiert (wenn möglich). Der letzte Eintrag ist ein `SHUTDOWN_INITIATED`-Eintrag:

```yaml
LedgerEntry:
  entry_type: SHUTDOWN_INITIATED
  payload:
    shutdown_reason: SIGTERM
    current_state: EXECUTING
    active_hal_commands: ["cmd-001"]
    active_processes: ["proc-001"]
    shutdown_timestamp: "2025-07-15T12:00:00Z"
  previous_hash: ...
  entry_hash: ...
```

### 8.5 WAL

Der WAL wird bei Shutdown flush'd. Der letzte WAL-Eintrag ist ein `SHUTDOWN_CHECKPOINT`:

```yaml
WALEntry:
  entry_type: SHUTDOWN_CHECKPOINT
  payload:
    shutdown_reason: SIGTERM
    current_state: EXECUTING
    last_completed_step: "step_3"
    active_process_resume_token: "resume-token-abc123"
    shutdown_timestamp: "2025-07-15T12:00:00Z"
  wal_position: 42
  checksum: ...
```

### 8.6 Queue

Die Queue wird bei Shutdown aktualisiert:

```
Wenn Paket in processing/ ist:
  → Wenn Ergebnis geliefert wurde: Paket nach failed/ verschieben
  → Wenn Ergebnis NICHT geliefert wurde: Paket in processing/ lassen
  → Registry aktualisieren: status = SHUTDOWN
```

### 8.7 Result-Builder

Der Result-Builder wird bei Shutdown aufgerufen, um das Ergebnis zu bauen:

```python
def build_shutdown_result(context):
    return QuestorErgebnisPaket(
        status="abgebrochen",
        abbruch_grund="GRACEFUL_SHUTDOWN",
        abbruch_klasse="OPERATIONAL",
        routing_checkpoint=RoutingCheckpoint(
            letzter_node=context.current_node,
            iterationen=context.iteration_count,
            ...
        ),
        ergebnis_daten=ErgebnisDaten(messwerte=context.partial_results),
        kristall_kandidaten=[],
        signale_fuer_atlas=[],
        vollstaendig_flag=True,
        rohdaten_checksumme="sha256:",
        ...
    )
```

### 8.8 Blackbox-Archiver

Der Blackbox-Archiver wird bei Shutdown aufgerufen, um die Blackbox zu schreiben:

```python
def write_blackbox_on_shutdown(context):
    blackbox = QuestorBlackbox(
        blackbox_id=f"bb-{context.package_id}-{context.zyklus_id}",
        package_id=context.package_id,
        zyklus_id=context.zyklus_id,
        attempt_id=context.attempt_id,
        ledger=context.ledger,
        raw_data=context.raw_data,
        llm_advice_log=context.llm_advice_log,
        error_details={"shutdown_reason": shutdown_state.signal},
        created_at=now_iso(),
        questor_version=QUESTOR_VERSION,
        retention_class="NORMAL"
    )
    write_blackbox(blackbox)
```

### 8.9 Health-Monitoring (Thema 5)

Das Health-Monitoring erkennt, wenn Questor sich beendet. Der letzte Heartbeat wird geschrieben. Der externe Monitor erkennt, dass Questor nicht mehr antwortet.

### 8.10 Trail-Map (Thema 6)

Shutdown-Events werden als Trails protokolliert:

| DecisionType | Trigger |
|---|---|
| `SHUTDOWN_INITIATED` | Shutdown-Signal empfangen |

### 8.11 Queue-Integration (Thema 7)

Die Queue wird bei Shutdown aktualisiert. Die `registry.json` wird mit `status = SHUTDOWN` aktualisiert.

---

## 9. Validierung durch konkretes Beispiel

### 9.1 Szenario: Chemie-Kinetik-Paket in EXECUTING mit Langzeit-Prozess

**Input:**

```yaml
# Questor-Zustand
current_state: EXECUTING
current_package:
  package_id: "pkg-chemie-001"
  zyklus_id: "zyklus-014"
  attempt_id: 2

# Aktives HAL-Kommando
active_hal_command:
  command_id: "cmd-pkg-chemie-001-step_3-2"
  capability: "spectrometer.measure_absorbance"
  started_at: "2025-07-15T11:59:30Z"
  timeout_s: 60.0

# Aktiver Langzeit-Prozess
active_process:
  process_id: "proc-pkg-chemie-001-step_4-2"
  capability: "incubator.incubate"
  process_state: RUNNING
  expected_duration_s: 259200.0  # 72 Stunden
  started_at: "2025-07-15T11:00:00Z"

# Shutdown-Konfiguration
shutdown_config:
  graceful_shutdown_timeout_s: 60.0
  hal_command_wait_timeout_s: 30.0
  process_hold_timeout_s: 30.0
```

### 9.2 Shutdown-Durchlauf

**Schritt 1: SIGTERM empfangen**
```
Zeit: 2025-07-15T12:00:00Z
Signal: SIGTERM
Aktion: Shutdown-Timer starten (60 Sekunden)
       shutdown_requested = true
       Keine neuen Pakete aus Queue nehmen
```

**Schritt 2: DRAINING — Aktives HAL-Kommando abwarten**
```
Zeit: 2025-07-15T12:00:00Z
Aktives Kommando: cmd-pkg-chemie-001-step_3-2
Gestartet: 2025-07-15T11:59:30Z
Verstrichene Zeit: 30 Sekunden
Timeout: 60 Sekunden
Verbleibende Zeit: 30 Sekunden

Aktion: Warte auf Abschluss des Kommandos (max. 30 Sekunden)
```

**Schritt 3: HAL-Kommando abgeschlossen**
```
Zeit: 2025-07-15T12:00:15Z
HAL-Kommando: SUCCESS
Aktion: Ergebnis des Kommandos im Ledger speichern
       active_hal_command_handled = true
```

**Schritt 4: DRAINING — Aktiven Prozess in SAFE_HOLD versetzen**
```
Zeit: 2025-07-15T12:00:15Z
Aktiver Prozess: proc-pkg-chemie-001-step_4-2
Aktion: hold_process(proc-pkg-chemie-001-step_4-2)

HAL antwortet:
  process_state: SAFE_HOLD
  resume_token: "resume-token-abc123"
  safe_hold_active: true

Aktion: resume_token im WAL speichern
       active_process_safe_held = true
```

**Schritt 5: FINALIZING — Ergebnis bauen**
```
Zeit: 2025-07-15T12:00:16Z
Aktion: Ergebnis als GRACEFUL_SHUTDOWN bauen

QuestorErgebnisPaket:
  package_id: "pkg-chemie-001"
  zyklus_id: "zyklus-014"
  attempt_id: 2
  status: "abgebrochen"
  abbruch_grund: "GRACEFUL_SHUTDOWN"
  abbruch_klasse: "OPERATIONAL"
  routing_checkpoint:
    letzter_node: "step_4"
    iterationen: 2
    loops_ausgefuehrt: ["chemie_optimize_v1"]
  ergebnis_daten:
    messwerte:
      step_3: {"absorbance": 0.45, "wavelength_nm": 450.0}
  kristall_kandidaten: []
  signale_fuer_atlas: []
  vollstaendig_flag: true
```

**Schritt 6: WAL flush'd**
```
Zeit: 2025-07-15T12:00:17Z
Aktion: WAL-Eintrag schreiben

WALEntry:
  entry_type: SHUTDOWN_CHECKPOINT
  payload:
    shutdown_reason: SIGTERM
    current_state: EXECUTING
    last_completed_step: "step_3"
    active_process_resume_token: "resume-token-abc123"
    shutdown_timestamp: "2025-07-15T12:00:17Z"
  wal_position: 42
```

**Schritt 7: Queue aktualisieren**
```
Zeit: 2025-07-15T12:00:18Z
Aktion: Paket nach failed/ verschieben
       Registry aktualisieren: status = SHUTDOWN
```

**Schritt 8: Leases freigeben**
```
Zeit: 2025-07-15T12:00:19Z
Aktion: Leases freigeben
       Resource Governor informieren
```

**Schritt 9: Blackbox schreiben**
```
Zeit: 2025-07-15T12:00:20Z
Aktion: Blackbox schreiben
       retention_class: NORMAL
```

**Schritt 10: Questor beenden**
```
Zeit: 2025-07-15T12:00:21Z
Aktion: Questor-Prozess beenden
       ShutdownResult.status = COMPLETED
       ShutdownResult.duration_s = 21.0
```

### 9.3 Ergebnis

Der Graceful-Shutdown wurde erfolgreich durchgeführt:
- Das aktive HAL-Kommando wurde abgewartet und abgeschlossen.
- Der Langzeit-Prozess wurde in SAFE_HOLD versetzt.
- Das Ergebnis wurde als `GRACEFUL_SHUTDOWN` gebaut und geliefert.
- Der WAL wurde flush'd.
- Die Queue wurde aktualisiert.
- Die Leases wurden freigegeben.
- Die Blackbox wurde geschrieben.
- Questor hat sich beendet.

Nach einem Neustart kann Questor den Langzeit-Prozess aus dem SAFE_HOLD fortsetzen, wenn die Freigabe erteilt wird.

---

## 10. Offene Fragen und Risiken

| # | Frage / Risiko | Schweregrad | Empfehlung |
|---|---|---|---|
| Q1 | **Wer sendet das Shutdown-Signal?** Das Gremium (Kanzler) oder ein menschlicher Operator? | Mittel | Empfehlung: Das Gremium (Kanzler) kann ein Shutdown-Signal senden. Ein menschlicher Operator kann auch ein Shutdown-Signal senden (z.B. über SIGTERM). |
| Q2 | **Was passiert, wenn Questor in einer Schleife von Graceful-Shutdown und Neustart gefangen ist?** | Hoch | Empfehlung: Ein Shutdown-Counter wird geführt. Wenn Questor mehr als 3 Mal innerhalb von 5 Minuten neu startet, wird ein Alarm ausgelöst. |
| Q3 | **Was passiert, wenn der Graceful-Shutdown-Timeout zu kurz ist?** | Mittel | Empfehlung: Der Timeout sollte konfigurierbar sein. Default: 60 Sekunden. Für Langzeit-Prozesse sollte der Timeout länger sein. |
| Q4 | **Was passiert, wenn der HAL nicht erreichbar ist und Questor sich beenden will?** | Hoch | Empfehlung: Questor versucht, den WAL zu flush'd. Wenn das fehlschlägt: Force-Shutdown. Nach Neustart: Recovery aus WAL. |
| Q5 | **Was passiert, wenn Questor in WAITING_FOR_RELEASE ist und sich beendet?** | Mittel | Empfehlung: Das Ergebnis wird als GRACEFUL_SHUTDOWN gebaut. Der Prozess bleibt in WAITING_FOR_RELEASE. Nach Neustart: Questor kann den Prozess fortsetzen, wenn die Freigabe erteilt wird. |
| Q6 | **Was passiert, wenn Questor in SAFE_HOLD ist und sich beendet?** | Mittel | Empfehlung: Das Ergebnis wird als GRACEFUL_SHUTDOWN gebaut. Der Prozess bleibt in SAFE_HOLD. Nach Neustart: Questor kann den Prozess fortsetzen, wenn der resume_token gültig ist. |
| Q7 | **Sollte es einen "Shutdown-Grund" im Ergebnis geben?** | Niedrig | Empfehlung: Ja. `abbruch_grund = GRACEFUL_SHUTDOWN` ist bereits definiert. Zusätzlich könnte ein `shutdown_reason`-Feld in `questor_metadata` aufgenommen werden. |

---

## 11. Zusammenfassung der Spezifikation

| Aspekt | Definition |
|---|---|
| **Modulname** | `shutdown.py` |
| **Position** | `src/questor/shutdown.py` |
| **Signale** | SIGTERM, SIGINT, shutdown.flag |
| **Phasen** | SIGNAL_RECEIVED → DRAINING → FINALIZING → TERMINATED |
| **Timeout** | Default: 60 Sekunden (konfigurierbar) |
| **HAL-Kommando-Timeout** | Default: 30 Sekunden (konfigurierbar) |
| **Prozess-HOLD-Timeout** | Default: 30 Sekunden (konfigurierbar) |
| **Ergebnis** | `status: abgebrochen`, `abbruch_grund: GRACEFUL_SHUTDOWN`, `abbruch_klasse: OPERATIONAL` |
| **WAL** | Wird bei Shutdown flush'd |
| **Queue** | Paket nach failed/ verschieben (wenn Ergebnis geliefert) oder in processing/ lassen (wenn nicht) |
| **Leases** | Werden freigegeben |
| **Blackbox** | Wird geschrieben (wenn Limit nicht erreicht) |
| **Fail-Closed** | Wenn Graceful-Shutdown fehlschlägt → Force-Shutdown |

---

## 12. Kritische Bewertung der eigenen Spezifikation

**Stärken:**
- Klare Shutdown-Phasen mit definierten Timeouts
- Totalfunktion-Regel wird erfüllt (Ergebnis wird gebaut)
- WAL-Flush sichert Crash-Recovery
- Langzeit-Prozesse werden in SAFE_HOLD versetzt
- Queue bleibt konsistent
- Leases werden freigegeben
- Blackbox wird geschrieben
- ESTOP hat Vorrang vor Shutdown

**Schwächen:**
- Wenn der HAL nicht erreichbar ist, kann der Prozess nicht in SAFE_HOLD versetzt werden
- Wenn der WAL-Flush fehlschlägt, ist die Recovery nach Neustart gefährdet
- Der Graceful-Shutdown-Timeout könnte zu kurz sein für komplexe Pakete
- Es gibt keine Möglichkeit, den Shutdown zu "pausieren" oder "fortzusetzen"

**Empfehlung:** Die Spezifikation ist implementierungsreif, ABER:
1. Der Graceful-Shutdown-Timeout sollte konfigurierbar sein und für Langzeit-Prozesse länger sein.
2. Ein Shutdown-Counter sollte geführt werden, um Schleifen von Graceful-Shutdown und Neustart zu erkennen.
3. Die Interaktion mit dem Resource Governor (Lease-Freigabe) sollte in der Resource-Governor-Spezifikation ergänzt werden.

---

## 13. Kreuzreferenzen

| Referenz | Beziehung |
|---|---|
| `structure_questor_interna_v0.4.0.md`, Teil N | Dieses Dokument IST Teil N |
| `structure_questor_interna_v0.3.0.md` §8 | Totalfunktion-Regel: Ergebnis wird IMMER gebaut |
| `structure_questor_interna_v0.3.0.md` §44–§46 | WAL-Lebenszyklus und Recovery |
| `structure_questor_interna_v0.3.0.md` §58 | Queue-Architektur |
| `structure_hal_v0.2.0.md` §12 | Langzeit-Prozessmodell: SAFE_HOLD, RESUME |
| `questor_capability_registry_v0.1.0.md` | Capabilities werden bei Shutdown nicht ausgeführt |
| `questor_security_mode_v0.1.0.md` | Shutdown respektiert security_mode |
| `questor_health_monitoring_v0.1.0.md` | Health-Monitoring erkennt Shutdown |
| `questor_trail_map_v0.1.0.md` | Shutdown-Events werden als Trails protokolliert |
| `questor_queue_integration_v0.1.0.md` | Queue wird bei Shutdown aktualisiert |
| `questor_test_strategy_v0.1.0.md` | 13 Unit-Tests (U-SD-01 bis U-SD-13) |
| `questor_implementation_plan_v0.1.0.md` | Phase Q11 (1-2 Tage) |