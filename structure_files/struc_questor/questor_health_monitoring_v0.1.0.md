# 🧭 QUESTOR-INTERNA: THEMA 5 — QUESTOR-HEALTH-MONITORING
## Heartbeat, Watchdog, externe Überwachung und Recovery-Aktionen

| Feld | Wert |
|---|---|
| Dateiname | `questor_health_monitoring_v0.1.0.md` |
| Version | 0.1.0 |
| System | MYRMEX v2.4.0 + Questor v0.2.3 |
| Status | Arbeitsstand — Architektur-Spezifikation, keine Implementierungsfreigabe |
| Bezug | `structure_questor_interna_v0.4.0.md`, Teil O |
| | `structure_standalone_v2.4.0.md` v1.1.1 (kanonisch) |
| | `structure_hal_v0.2.0.md` |
| Sprache | Deutsch |
| Modus | Dry-Run / Spezifikation |

---

## 0. Dokumentenhierarchie und Geltung

```
1. structure_standalone_v2.4.0.md v1.1.1                    ← kanonisch
2. structure_hal_v0.2.0.md                                   ← HAL-Vertrag
3. structure_questor_interna_v0.4.0.md                       ← Questor-Interna GESAMT
4. diese Datei: questor_health_monitoring_v0.1.0.md          ← Detail: Health-Monitoring
5. structure_standalone_questor_v0.2.3.md                    ← unterstützend
```

Bei Widersprüchen gilt die kanonische Hauptreferenz.

Dieses Dokument ist Teil O der Questor-Interna-Gesamtspezifikation.
Es ist eigenständig lesbar, setzt aber Grundkenntnisse der Questor-Architektur voraus.

---

## 1. Kritische Analyse des Bestehenden

### 1.1 Was bereits existiert

| Quelle | Referenz | Problem |
|---|---|---|
| `structure_questor_interna_v0.3.0.md` §59 | Questor-Prozess mit Hauptloop | **Kein Watchdog, kein Heartbeat, keine Gesundheitsprüfung.** |
| `structure_questor_interna_v0.3.0.md` §67 | "Questor-Health-Monitoring" als offenes Thema (Priorität Niedrig) | **Keine Definition, keine Zustandsmaschine, keine Regeln.** |
| `structure_questor_interna_v0.3.0.md` §7.6 | `OperationalMetrics` pro Paket | Metriken sind paketbezogen, nicht prozessbezogen. |
| `structure_questor_interna_v0.3.0.md` §58 | Queue-Architektur mit `registry.json` | Registry wird von Questor aktualisiert. Wenn Questor hängt, wird die Registry nicht aktualisiert. Aber niemand prüft das. |
| `structure_standalone_v2.4.0.md` §10.1 | Sicherheitsarchitektur | Kein Health-Monitoring für Questor definiert. |

### 1.2 Identifizierte Probleme

| # | Problem | Schweregrad | Begründung |
|---|---|---|---|
| P1 | **Kein Heartbeat-Mechanismus.** Questor ist ein eigener Prozess. Wenn er hängt oder abstürzt, weiß das Gremium nichts davon. | **KRITISCH** | Pakete in `processing/` bleiben für immer hängen. Das Gremium wartet unendlich auf ein Ergebnis. |
| P2 | **Kein interner Watchdog.** Wenn Questor in einem Zustand hängt (z.B. `EXECUTING` ohne Fortschritt), gibt es keinen Mechanismus, der das erkennt. | **KRITISCH** | Questor könnte in einer Endlosschleife gefangen sein, ohne dass es jemand merkt. |
| P3 | **Keine externe Überwachung.** Niemand prüft, ob Questor noch lebt. | Hoch | Wenn Questor abstürzt, wird das nicht erkannt. |
| P4 | **Keine Gesundheitsmetriken auf Prozessebene.** `OperationalMetrics` sind paketbezogen. Es gibt keine Metriken wie Uptime, Speicherverbrauch, CPU-Auslastung. | Mittel | Betriebsprobleme werden nicht erkannt. |
| P5 | **Keine Definition, was "gesund" bedeutet.** Es gibt keine Gesundheitszustände und keine Schwellwerte. | Hoch | Ohne Definition kann kein Monitoring implementiert werden. |
| P6 | **Keine Recovery-Aktion bei Gesundheitsproblemen.** Was passiert, wenn Questor als "ungesund" erkannt wird? | Hoch | Ohne Recovery-Aktion ist das Monitoring wertlos. |
| P7 | **Die `registry.json` wird von Questor aktualisiert.** Wenn Questor hängt, wird die Registry nicht aktualisiert. Aber niemand prüft, ob die Registry veraltet ist. | Mittel | Passive Erkennung von Hängern ist nicht möglich. |
| P8 | **Kein Health-Logging.** Gesundheitsereignisse werden nicht protokolliert. | Mittel | Nachvollziehbarkeit fehlt. |
| P9 | **Keine Integration mit dem Betriebssystem.** Questor könnte über systemd oder Kubernetes überwacht werden, aber das ist nicht spezifiziert. | Niedrig | Betriebssystem-Überwachung ist ein zusätzlicher Schutz, aber nicht die primäre Lösung. |

### 1.3 Fazit der Analyse

Questor ist ein **eigener Prozess**, der unabhängig vom Gremium läuft. Ohne Health-Monitoring:
- Hängende Questor-Prozesse werden nicht erkannt.
- Abgestürzte Questor-Prozesse werden nicht erkannt.
- Pakete in `processing/` bleiben für immer hängen.
- Das Gremium wartet unendlich auf ein Ergebnis.
- Betriebsprobleme (Speicher, CPU) werden nicht erkannt.

**Health-Monitoring ist eine kritische Lücke**, auch wenn es in der bisherigen Spezifikation als "Priorität Niedrig" eingestuft wurde. Ich empfehle, die Priorität auf **HOCH** zu setzen, da ein hängender Questor das gesamte System blockiert.

---

## 2. Formale Definition: Health-Monitoring-Modul

### 2.1 Zweck

Das Health-Monitoring-Modul stellt sicher, dass:

1. Questor seinen eigenen Gesundheitszustand kontinuierlich überwacht.
2. Questor seinen Gesundheitszustand nach außen meldet (Heartbeat).
3. Ein externer Monitor den Gesundheitszustand von Questor prüft.
4. Bei Gesundheitsproblemen definierte Aktionen ausgelöst werden.
5. Gesundheitsereignisse protokolliert werden.

### 2.2 Position in der Architektur

```
┌─────────────────────────────────────────────────────────┐
│                    QUESTOR-PROZESS                       │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │              HAUPTLOOP (§59)                      │   │
│  │  → Paket verarbeiten                             │   │
│  │  → Zustand aktualisieren                         │   │
│  │  → Heartbeat schreiben                           │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │           INTERNAL WATCHDOG (Thread)              │   │
│  │  → Überwacht Zustandsdauer                        │   │
│  │  → Überwacht Speicherverbrauch                    │   │
│  │  → Überwacht CPU-Auslastung                       │   │
│  │  → Meldet Anomalien                               │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │           HEARTBEAT WRITER (Thread)               │   │
│  │  → Schreibt health.json alle N Sekunden           │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
                          │
                          │ health.json
                          ▼
┌─────────────────────────────────────────────────────────┐
│              EXTERNER MONITOR                             │
│  (Pipeline-Orchestrator / Kanzler / Betriebssystem)      │
│                                                         │
│  → Prüft health.json auf Aktualität                     │
│  → Prüft registry.json auf Fortschritt                  │
│  → Prüft Questor-Prozess auf Existenz                   │
│  → Löst Recovery-Aktionen aus                           │
└─────────────────────────────────────────────────────────┘
```

### 2.3 Grundprinzipien

| Prinzip | Bedeutung |
|---|---|
| **Operational** | Health-Monitoring ist immer OPERATIONAL. Niemals SAFETY oder SCIENTIFIC. |
| **Nicht-blockierend** | Health-Monitoring darf die normale Questor-Ausführung nicht blockieren. |
| **Leichtgewichtig** | Health-Monitoring darf nicht selbst zum Ressourcenproblem werden. |
| **Fail-Safe** | Wenn der Heartbeat nicht geschrieben werden kann, wird das protokolliert, aber Questor arbeitet weiter. |
| **Deterministisch** | Health-Monitoring ist deterministisch. Kein LLM. |
| **Auditierbar** | Alle Gesundheitsereignisse werden protokolliert. |

---

## 3. Datenverträge

### 3.1 HealthFile (health.json)

```yaml
HealthFile:
  schema_version: str              # "0.3.1"
  questor_version: str             # Questor-Version
  process_id: int                  # OS-Prozess-ID
  started_at: str                  # ISO-8601 Zeitstempel
  last_heartbeat: str              # ISO-8601 Zeitstempel des letzten Heartbeats
  health_status: HEALTHY | DEGRADED | UNHEALTHY
  watchdog_status: OK | WARNING | CRITICAL
  
  # Aktueller Zustand
  current_state: str               # Questor-Zustand (IDLE, EXECUTING, etc.)
  current_state_since: str         # Seit wann ist Questor in diesem Zustand?
  current_package_id: Optional[str]
  current_zyklus_id: Optional[str]
  current_attempt_id: Optional[int]
  
  # Fortschritt
  packages_processed_total: int
  packages_failed_total: int
  packages_in_queue: int           # Anzahl in pending/
  current_iteration: Optional[int]
  current_loop_index: Optional[int]
  current_step_index: Optional[int]
  
  # Ressourcen
  uptime_s: float
  memory_usage_mb: float
  cpu_usage_percent: float
  open_file_handles: int
  wal_size_mb: float
  ledger_size_mb: float
  
  # Fehler
  last_error: Optional[str]
  last_error_at: Optional[str]
  consecutive_errors: int
  
  # Watchdog
  watchdog_checks:
    state_duration_ok: bool
    memory_ok: bool
    cpu_ok: bool
    progress_ok: bool
    wal_ok: bool
```

### 3.2 HealthMonitorConfig

```yaml
HealthMonitorConfig:
  # Heartbeat
  heartbeat_interval_s: float          # Default: 5.0
  heartbeat_file_path: str             # Default: "data/questor_queue/health.json"
  heartbeat_write_timeout_s: float     # Default: 2.0
  
  # Watchdog
  watchdog_check_interval_s: float     # Default: 10.0
  state_duration_limits:               # Maximale Dauer pro Zustand
    RECEIVING: 10.0
    VALIDATING: 30.0
    PLANNING: 120.0
    EXECUTING: -1                      # -1 = kein Limit (wird durch max_duration_s gesteuert)
    EVALUATING: 60.0
    WAITING_FOR_RELEASE: -1            # -1 = kein Limit (manuelle Freigabe)
    SAFE_HOLD: -1                      # -1 = kein Limit (manuelle Freigabe)
    RECOVERING: 300.0
    FINALIZING: 60.0
  memory_limit_mb: float               # Default: 2048.0
  cpu_limit_percent: float             # Default: 90.0
  progress_check_interval_s: float     # Default: 300.0 (5 Minuten)
  
  # Externer Monitor
  external_monitor_interval_s: float   # Default: 30.0
  heartbeat_stale_threshold_s: float   # Default: 15.0 (3× heartbeat_interval)
  package_processing_timeout_s: float  # Default: 86400.0 (24 Stunden)
  
  # Alerts
  alert_cooldown_s: float              # Default: 300.0 (5 Minuten)
  max_consecutive_alerts: int          # Default: 5
```

### 3.3 HealthEvent

```yaml
HealthEvent:
  timestamp: str
  event_type: HEARTBEAT | WATCHDOG_WARNING | WATCHDOG_CRITICAL | 
              HEALTH_CHECK | HEALTH_ALERT | RECOVERY_ACTION
  health_status: HEALTHY | DEGRADED | UNHEALTHY
  watchdog_status: OK | WARNING | CRITICAL
  details: dict[str, Any]
  action_taken: Optional[str]
```

### 3.4 HealthCheckResult

```yaml
HealthCheckResult:
  questor_alive: bool
  heartbeat_fresh: bool
  heartbeat_age_s: float
  health_status: HEALTHY | DEGRADED | UNHEALTHY
  current_state: Optional[str]
  current_package_id: Optional[str]
  package_processing_time_s: Optional[float]
  memory_ok: bool
  cpu_ok: bool
  progress_ok: bool
  overall_status: HEALTHY | DEGRADED | UNHEALTHY | DEAD
  recommended_action: NONE | ALERT | RESTART | ESCALATE
```

---

## 4. Gesundheitszustände

### 4.1 Definition

| Zustand | Bedeutung | Kriterien |
|---|---|---|
| `HEALTHY` | Questor arbeitet normal. | Heartbeat frisch, kein Watchdog-Alarm, Fortschritt vorhanden. |
| `DEGRADED` | Questor arbeitet, aber mit Einschränkungen. | Heartbeat frisch, aber Watchdog-Warning (z.B. hoher Speicherverbrauch). |
| `UNHEALTHY` | Questor arbeitet nicht korrekt. | Heartbeat veraltet ODER Watchdog-Critical ODER kein Fortschritt. |
| `DEAD` | Questor ist nicht erreichbar. | Prozess läuft nicht ODER Heartbeat seit > 3× Interval nicht aktualisiert. |

### 4.2 Zustandsübergänge

```
                    ┌──────────┐
                    │ HEALTHY  │
                    └────┬─────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
     Watchdog-Warning  Heartbeat   Watchdog-Critical
              │       veraltet        │
              ▼          │            ▼
       ┌──────────┐     │     ┌───────────┐
       │ DEGRADED │     │     │ UNHEALTHY │
       └────┬─────┘     │     └─────┬─────┘
            │            │           │
            │    ┌───────┘           │
            │    │                   │
            │    ▼                   │
            │  ┌───────────┐        │
            │  │ UNHEALTHY │        │
            │  └─────┬─────┘        │
            │        │              │
            │        │   Prozess    │
            │        │   läuft      │
            │        │   nicht      │
            │        ▼              │
            │  ┌──────────┐        │
            │  │   DEAD   │        │
            │  └──────────┘        │
            │                      │
            └──────────────────────┘
                    │
                    ▼
              Recovery-Aktion
```

### 4.3 Bestimmung des Gesundheitszustands

```python
def determine_health_status(
    heartbeat_age_s: float,
    watchdog_status: str,
    progress_ok: bool,
    process_alive: bool
) -> str:
    
    if not process_alive:
        return "DEAD"
    
    if heartbeat_age_s > heartbeat_stale_threshold_s:
        return "UNHEALTHY"
    
    if watchdog_status == "CRITICAL":
        return "UNHEALTHY"
    
    if watchdog_status == "WARNING":
        return "DEGRADED"
    
    if not progress_ok:
        return "UNHEALTHY"
    
    return "HEALTHY"
```

---

## 5. Heartbeat-Mechanismus

### 5.1 Heartbeat-Writer (interner Thread)

Der Heartbeat-Writer ist ein **separater Thread** innerhalb des Questor-Prozesses. Er schreibt die `health.json`-Datei in regelmäßigen Abständen.

```python
class HeartbeatWriter:
    def __init__(self, config: HealthMonitorConfig, questor_state: QuestorState):
        self.config = config
        self.questor_state = questor_state
        self.running = True
        self.thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
    
    def start(self):
        self.thread.start()
    
    def stop(self):
        self.running = False
        self.thread.join(timeout=5.0)
    
    def _heartbeat_loop(self):
        while self.running:
            try:
                self._write_heartbeat()
            except Exception as e:
                # Heartbeat-Fehler ist OPERATIONAL, nicht SAFETY
                logger.error(f"Heartbeat-Write fehlgeschlagen: {e}")
                # Questor arbeitet trotzdem weiter
            
            time.sleep(self.config.heartbeat_interval_s)
    
    def _write_heartbeat(self):
        health_file = HealthFile(
            schema_version="0.3.1",
            questor_version=QUESTOR_VERSION,
            process_id=os.getpid(),
            started_at=self.questor_state.started_at,
            last_heartbeat=now_iso(),
            health_status=self.questor_state.health_status,
            watchdog_status=self.questor_state.watchdog_status,
            current_state=self.questor_state.current_state,
            current_state_since=self.questor_state.current_state_since,
            current_package_id=self.questor_state.current_package_id,
            current_zyklus_id=self.questor_state.current_zyklus_id,
            current_attempt_id=self.questor_state.current_attempt_id,
            packages_processed_total=self.questor_state.packages_processed_total,
            packages_failed_total=self.questor_state.packages_failed_total,
            packages_in_queue=self._count_pending_packages(),
            uptime_s=self._get_uptime(),
            memory_usage_mb=self._get_memory_usage(),
            cpu_usage_percent=self._get_cpu_usage(),
            open_file_handles=self._get_open_file_handles(),
            wal_size_mb=self._get_wal_size(),
            ledger_size_mb=self._get_ledger_size(),
            last_error=self.questor_state.last_error,
            last_error_at=self.questor_state.last_error_at,
            consecutive_errors=self.questor_state.consecutive_errors,
            watchdog_checks=self.questor_state.watchdog_checks
        )
        
        # Atomares Schreiben (temp file + rename)
        tmp_path = self.config.heartbeat_file_path + ".tmp"
        with open(tmp_path, 'w') as f:
            json.dump(health_file.dict(), f, indent=2)
        os.rename(tmp_path, self.config.heartbeat_file_path)
```

### 5.2 Heartbeat-Regeln

| Regel | Beschreibung |
|---|---|
| HB-1 | Der Heartbeat wird alle `heartbeat_interval_s` Sekunden geschrieben. Default: 5 Sekunden. |
| HB-2 | Der Heartbeat wird in einem **separaten Thread** geschrieben, um die Hauptausführung nicht zu blockieren. |
| HB-3 | Der Heartbeat wird **atomar** geschrieben (temp file + rename), um korrupte Dateien zu vermeiden. |
| HB-4 | Wenn der Heartbeat nicht geschrieben werden kann (z.B. Disk-Full), wird der Fehler protokolliert. Questor arbeitet trotzdem weiter. |
| HB-5 | Der Heartbeat enthält den aktuellen Zustand, das aktuelle Paket und die Ressourcenmetriken. |
| HB-6 | Der Heartbeat wird auch im Zustand `IDLE` geschrieben. |
| HB-7 | Der Heartbeat wird auch während `EXECUTING` geschrieben (auch bei Langzeit-Prozessen). |

---

## 6. Interner Watchdog

### 6.1 Watchdog-Thread

Der interne Watchdog ist ein **separater Thread** innerhalb des Questor-Prozesses. Er überwacht die Zustandsdauer, den Speicherverbrauch und die CPU-Auslastung.

```python
class InternalWatchdog:
    def __init__(self, config: HealthMonitorConfig, questor_state: QuestorState):
        self.config = config
        self.questor_state = questor_state
        self.running = True
        self.thread = threading.Thread(target=self._watchdog_loop, daemon=True)
    
    def start(self):
        self.thread.start()
    
    def stop(self):
        self.running = False
        self.thread.join(timeout=5.0)
    
    def _watchdog_loop(self):
        while self.running:
            try:
                self._check_state_duration()
                self._check_memory()
                self._check_cpu()
                self._check_progress()
                self._check_wal()
                self._update_watchdog_status()
            except Exception as e:
                logger.error(f"Watchdog-Check fehlgeschlagen: {e}")
            
            time.sleep(self.config.watchdog_check_interval_s)
    
    def _check_state_duration(self):
        """Prüft, ob der aktuelle Zustand zu lange dauert."""
        current_state = self.questor_state.current_state
        state_since = self.questor_state.current_state_since
        
        if current_state in self.config.state_duration_limits:
            limit = self.config.state_duration_limits[current_state]
            if limit == -1:
                return  # Kein Limit für diesen Zustand
            
            duration_s = (now() - parse_iso(state_since)).total_seconds()
            if duration_s > limit:
                self.questor_state.watchdog_checks["state_duration_ok"] = False
                self._trigger_alert(
                    "WATCHDOG_STATE_DURATION",
                    f"Zustand {current_state} dauert {duration_s}s (Limit: {limit}s)"
                )
            else:
                self.questor_state.watchdog_checks["state_duration_ok"] = True
    
    def _check_memory(self):
        """Prüft den Speicherverbrauch."""
        memory_mb = self._get_memory_usage()
        if memory_mb > self.config.memory_limit_mb:
            self.questor_state.watchdog_checks["memory_ok"] = False
            self._trigger_alert(
                "WATCHDOG_MEMORY",
                f"Speicherverbrauch {memory_mb}MB (Limit: {self.config.memory_limit_mb}MB)"
            )
        else:
            self.questor_state.watchdog_checks["memory_ok"] = True
    
    def _check_cpu(self):
        """Prüft die CPU-Auslastung."""
        cpu_percent = self._get_cpu_usage()
        if cpu_percent > self.config.cpu_limit_percent:
            self.questor_state.watchdog_checks["cpu_ok"] = False
            self._trigger_alert(
                "WATCHDOG_CPU",
                f"CPU-Auslastung {cpu_percent}% (Limit: {self.config.cpu_limit_percent}%)"
            )
        else:
            self.questor_state.watchdog_checks["cpu_ok"] = True
    
    def _check_progress(self):
        """Prüft, ob Questor Fortschritt macht."""
        if self.questor_state.current_state == "EXECUTING":
            if self.questor_state.last_progress_at is not None:
                time_since_progress = (now() - self.questor_state.last_progress_at).total_seconds()
                if time_since_progress > self.config.progress_check_interval_s:
                    self.questor_state.watchdog_checks["progress_ok"] = False
                    self._trigger_alert(
                        "WATCHDOG_NO_PROGRESS",
                        f"Kein Fortschritt seit {time_since_progress}s"
                    )
                else:
                    self.questor_state.watchdog_checks["progress_ok"] = True
    
    def _check_wal(self):
        """Prüft die WAL-Größe."""
        wal_size_mb = self._get_wal_size()
        if wal_size_mb > 100.0:  # 100 MB Limit
            self.questor_state.watchdog_checks["wal_ok"] = False
            self._trigger_alert(
                "WATCHDOG_WAL_SIZE",
                f"WAL-Größe {wal_size_mb}MB (Limit: 100MB)"
            )
        else:
            self.questor_state.watchdog_checks["wal_ok"] = True
    
    def _update_watchdog_status(self):
        """Aktualisiert den Watchdog-Status basierend auf den Checks."""
        checks = self.questor_state.watchdog_checks
        
        if not checks["state_duration_ok"] or not checks["progress_ok"]:
            self.questor_state.watchdog_status = "CRITICAL"
        elif not checks["memory_ok"] or not checks["cpu_ok"] or not checks["wal_ok"]:
            self.questor_state.watchdog_status = "WARNING"
        else:
            self.questor_state.watchdog_status = "OK"
```

### 6.2 Watchdog-Regeln

| Regel | Beschreibung |
|---|---|
| WD-1 | Der Watchdog läuft in einem **separaten Thread**. |
| WD-2 | Der Watchdog prüft alle `watchdog_check_interval_s` Sekunden. Default: 10 Sekunden. |
| WD-3 | Der Watchdog prüft: Zustandsdauer, Speicherverbrauch, CPU-Auslastung, Fortschritt, WAL-Größe. |
| WD-4 | `EXECUTING`, `WAITING_FOR_RELEASE` und `SAFE_HOLD` haben **kein Zeitlimit** (`-1`), da sie durch externe Ereignisse gesteuert werden. |
| WD-5 | `RECEIVING`, `VALIDATING`, `PLANNING`, `EVALUATING`, `FINALIZING` haben **feste Zeitlimits**. |
| WD-6 | Wenn ein Watchdog-Check fehlschlägt, wird der Status auf `WARNING` oder `CRITICAL` gesetzt. |
| WD-7 | Der Watchdog-Status wird im Heartbeat gemeldet. |
| WD-8 | Der Watchdog löst **keine direkten Aktionen** aus. Er meldet nur. Die Aktionen werden vom externen Monitor ausgelöst. |

### 6.3 Zustandsdauer-Limits (Default)

| Zustand | Limit (Sekunden) | Begründung |
|---|---|---|
| `RECEIVING` | 10 | Envelope-Empfang sollte schnell sein. |
| `VALIDATING` | 30 | Validierung sollte schnell sein. |
| `PLANNING` | 120 | Planung kann länger dauern (LLM-Aufrufe). |
| `EXECUTING` | -1 (kein Limit) | Wird durch `max_duration_s` im Budget gesteuert. |
| `EVALUATING` | 60 | Evaluation sollte schnell sein. |
| `WAITING_FOR_RELEASE` | -1 (kein Limit) | Manuelle Freigabe kann Tage dauern. |
| `SAFE_HOLD` | -1 (kein Limit) | Manuelle Freigabe kann Tage dauern. |
| `RECOVERING` | 300 | Recovery sollte nicht zu lange dauern. |
| `FINALIZING` | 60 | Ergebnisbau sollte schnell sein. |

---

## 7. Externe Überwachung

### 7.1 Wer überwacht Questor?

Die externe Überwachung wird vom **Pipeline-Orchestrator** (Gremium) durchgeführt. Der Pipeline-Orchestrator prüft in regelmäßigen Abständen den Gesundheitszustand von Questor.

**Alternativ** kann die externe Überwachung auch durch das Betriebssystem (systemd, Kubernetes) erfolgen. In diesem Fall ist der Pipeline-Orchestrator für die **inhaltliche** Überwachung zuständig (Fortschritt, Zustand), während das Betriebssystem für die **Prozess-Überwachung** zuständig ist (läuft der Prozess noch?).

### 7.2 Externer Monitor (Pipeline-Orchestrator)

```python
class ExternalQuestorMonitor:
    def __init__(self, config: HealthMonitorConfig):
        self.config = config
        self.last_alert_at = None
        self.consecutive_alerts = 0
    
    def check_questor_health(self) -> HealthCheckResult:
        """Prüft den Gesundheitszustand von Questor."""
        
        # 1. Prüfe, ob der Questor-Prozess läuft
        process_alive = self._check_process_alive()
        
        # 2. Lese die health.json
        health_file = self._read_health_file()
        
        if health_file is None:
            return HealthCheckResult(
                questor_alive=process_alive,
                heartbeat_fresh=False,
                heartbeat_age_s=float('inf'),
                health_status="DEAD",
                current_state=None,
                current_package_id=None,
                package_processing_time_s=None,
                memory_ok=False,
                cpu_ok=False,
                progress_ok=False,
                overall_status="DEAD",
                recommended_action="RESTART"
            )
        
        # 3. Prüfe Heartbeat-Alter
        heartbeat_age_s = (now() - parse_iso(health_file.last_heartbeat)).total_seconds()
        heartbeat_fresh = heartbeat_age_s <= self.config.heartbeat_stale_threshold_s
        
        # 4. Prüfe Paket-Verarbeitungszeit
        package_processing_time_s = None
        if health_file.current_package_id is not None:
            package_processing_time_s = (now() - parse_iso(health_file.current_state_since)).total_seconds()
        
        # 5. Prüfe Fortschritt
        progress_ok = health_file.watchdog_checks.get("progress_ok", True)
        
        # 6. Bestimme Gesamtstatus
        overall_status = determine_health_status(
            heartbeat_age_s=heartbeat_age_s,
            watchdog_status=health_file.watchdog_status,
            progress_ok=progress_ok,
            process_alive=process_alive
        )
        
        # 7. Bestimme empfohlene Aktion
        recommended_action = self._determine_action(overall_status, heartbeat_age_s, package_processing_time_s)
        
        return HealthCheckResult(
            questor_alive=process_alive,
            heartbeat_fresh=heartbeat_fresh,
            heartbeat_age_s=heartbeat_age_s,
            health_status=health_file.health_status,
            current_state=health_file.current_state,
            current_package_id=health_file.current_package_id,
            package_processing_time_s=package_processing_time_s,
            memory_ok=health_file.watchdog_checks.get("memory_ok", True),
            cpu_ok=health_file.watchdog_checks.get("cpu_ok", True),
            progress_ok=progress_ok,
            overall_status=overall_status,
            recommended_action=recommended_action
        )
    
    def _determine_action(self, overall_status, heartbeat_age_s, package_processing_time_s):
        if overall_status == "DEAD":
            return "RESTART"
        
        if overall_status == "UNHEALTHY":
            if heartbeat_age_s > self.config.heartbeat_stale_threshold_s * 2:
                return "RESTART"
            if package_processing_time_s and package_processing_time_s > self.config.package_processing_timeout_s:
                return "ESCALATE"
            return "ALERT"
        
        if overall_status == "DEGRADED":
            return "ALERT"
        
        return "NONE"
    
    def _check_process_alive(self) -> bool:
        """Prüft, ob der Questor-Prozess läuft."""
        health_file = self._read_health_file()
        if health_file is None:
            return False
        
        try:
            os.kill(health_file.process_id, 0)
            return True
        except OSError:
            return False
    
    def _read_health_file(self) -> Optional[HealthFile]:
        """Liest die health.json-Datei."""
        try:
            with open(self.config.heartbeat_file_path, 'r') as f:
                data = json.load(f)
            return HealthFile(**data)
        except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
            logger.error(f"Fehler beim Lesen der health.json: {e}")
            return None
```

### 7.3 Überwachungsintervall

Der externe Monitor prüft den Gesundheitszustand alle `external_monitor_interval_s` Sekunden. Default: 30 Sekunden.

### 7.4 Alert-Cooldown

Um Alert-Stürme zu vermeiden, gibt es einen Alert-Cooldown:

```python
def should_alert(self) -> bool:
    if self.last_alert_at is None:
        return True
    
    time_since_last_alert = (now() - self.last_alert_at).total_seconds()
    if time_since_last_alert < self.config.alert_cooldown_s:
        return False
    
    if self.consecutive_alerts >= self.config.max_consecutive_alerts:
        return False
    
    return True
```

---

## 8. Recovery-Aktionen

### 8.1 Aktionsmatrix

| Gesamtstatus | Empfohlene Aktion | Beschreibung |
|---|---|---|
| `HEALTHY` | `NONE` | Keine Aktion. |
| `DEGRADED` | `ALERT` | Alert an Kanzler senden. Questor arbeitet weiter. |
| `UNHEALTHY` | `ALERT` oder `RESTART` | Alert an Kanzler senden. Wenn Heartbeat seit > 2× Threshold veraltet: Neustart. |
| `DEAD` | `RESTART` | Questor-Prozess neu starten. |

### 8.2 Neustart-Prozedur

```
1. Questor-Prozess beenden (SIGTERM, dann SIGKILL nach Timeout)
2. WAL prüfen (Recovery nötig?)
3. Questor-Prozess neu starten
4. Questor führt Recovery aus (wenn nötig)
5. Health-Event protokollieren
```

### 8.3 Eskalations-Prozedur

```
1. Alert an Kanzler senden
2. Kanzler prüft den Zustand
3. Wenn nötig: Manuelle Intervention
4. Wenn nötig: SAFE_MODE auslösen
5. Health-Event protokollieren
```

### 8.4 Regeln

| Regel | Beschreibung |
|---|---|
| RA-1 | Ein Neustart wird **nur** bei `DEAD` oder `UNHEALTHY` mit veraltetem Heartbeat ausgelöst. |
| RA-2 | Ein Neustart wird **niemals** automatisch bei `DEGRADED` ausgelöst. |
| RA-3 | Ein Neustart wird **niemals** automatisch bei `WAITING_FOR_RELEASE` oder `SAFE_HOLD` ausgelöst. |
| RA-4 | Ein Neustart wird **niemals** ohne WAL-Prüfung durchgeführt. |
| RA-5 | Eine Eskalation wird **immer** an den Kanzler gesendet. |
| RA-6 | Eine Eskalation kann zu `SAFE_MODE` führen, aber nur durch menschliche Freigabe. |
| RA-7 | Recovery-Aktionen sind **immer** OPERATIONAL. Niemals SAFETY oder SCIENTIFIC. |

---

## 9. Zustandsmaschine: Health-Monitoring-Lifecycle

```
                    ┌──────────────────────────────────────────┐
                    │          QUESTOR-START                    │
                    └──────────────────────┬───────────────────┘
                                           │
                    ┌──────────────────────▼───────────────────┐
                    │     HEARTBEAT-WRITER STARTEN              │
                    │     INTERNAL-WATCHDOG STARTEN             │
                    └──────────────────────┬───────────────────┘
                                           │
                    ┌──────────────────────▼───────────────────┐
                    │     HAUPTLOOP LAUFEN                      │
                    │     (Paket verarbeiten)                   │
                    └──────────────────────┬───────────────────┘
                                           │
                    ┌──────────────────────▼───────────────────┐
                    │     HEARTBEAT SCHREIBEN                   │
                    │     (alle heartbeat_interval_s)           │
                    └──────────────────────┬───────────────────┘
                                           │
                    ┌──────────────────────▼───────────────────┐
                    │     WATCHDOG-CHECKS DURCHFÜHREN           │
                    │     (alle watchdog_check_interval_s)      │
                    └──────────────────────┬───────────────────┘
                                           │
                    ┌──────────────────────▼───────────────────┐
                    │     EXTERNER MONITOR PRÜFT                │
                    │     (alle external_monitor_interval_s)    │
                    └──────────────────────┬───────────────────┘
                                           │
                    ┌──────────┬───────────┼───────────┬──────────┐
                    │          │           │           │          │
                 HEALTHY   DEGRADED   UNHEALTHY    DEAD     SHUTDOWN
                    │          │           │           │          │
                    ▼          ▼           ▼           ▼          ▼
                 KEINE     ALERT      ALERT/      RESTART    STOPPEN
                 AKTION   SENDEN     RESTART
```

---

## 10. Fehlerbehandlung

| Fehler | Ursache | Aktion | Fehlerklasse |
|---|---|---|---|
| `HEARTBEAT_WRITE_FAILED` | Disk-Full, Permission-Error | Fehler protokollieren, Questor arbeitet weiter | OPERATIONAL |
| `HEARTBEAT_STALE` | Heartbeat seit > Threshold nicht aktualisiert | Externer Monitor meldet `UNHEALTHY` | OPERATIONAL |
| `WATCHDOG_STATE_DURATION` | Zustand dauert zu lange | Watchdog-Status auf `CRITICAL` setzen | OPERATIONAL |
| `WATCHDOG_MEMORY` | Speicherverbrauch zu hoch | Watchdog-Status auf `WARNING` setzen | OPERATIONAL |
| `WATCHDOG_CPU` | CPU-Auslastung zu hoch | Watchdog-Status auf `WARNING` setzen | OPERATIONAL |
| `WATCHDOG_NO_PROGRESS` | Kein Fortschritt seit > Interval | Watchdog-Status auf `CRITICAL` setzen | OPERATIONAL |
| `WATCHDOG_WAL_SIZE` | WAL-Größe zu groß | Watchdog-Status auf `WARNING` setzen | OPERATIONAL |
| `HEALTH_FILE_NOT_FOUND` | health.json existiert nicht | Externer Monitor meldet `DEAD` | OPERATIONAL |
| `HEALTH_FILE_CORRUPT` | health.json ist korrupt | Externer Monitor meldet `DEAD` | OPERATIONAL |
| `PROCESS_NOT_FOUND` | Questor-Prozess läuft nicht | Externer Monitor meldet `DEAD` | OPERATIONAL |
| `MONITOR_CHECK_FAILED` | Externer Monitor kann nicht prüfen | Fehler protokollieren, erneut versuchen | OPERATIONAL |

**Kritische Regel:** ALLE Health-Monitoring-Fehler sind `OPERATIONAL`. Ein Health-Monitoring-Fehler ist NIEMALS ein `SAFETY`-Ereignis und NIEMALS ein `SCIENTIFIC`-Ereignis.

**Kritische Regel:** Health-Monitoring-Fehler führen **niemals** zu einem Abbruch des aktuellen Pakets. Questor arbeitet weiter, auch wenn das Health-Monitoring fehlschlägt.

---

## 11. Edge Cases

| # | Edge Case | Erwartetes Verhalten |
|---|---|---|
| EC-1 | Questor ist in `EXECUTING` mit einem 72-Stunden-Inkubationsprozess. Der Watchdog prüft die Zustandsdauer. | `EXECUTING` hat kein Zeitlimit (`-1`). Der Watchdog meldet keinen Alarm. Der Fortschritt wird über `current_step_index` und `last_progress_at` geprüft. |
| EC-2 | Questor ist in `WAITING_FOR_RELEASE` und wartet auf eine manuelle Freigabe. Der externe Monitor prüft den Heartbeat. | `WAITING_FOR_RELEASE` hat kein Zeitlimit. Der Heartbeat wird weiterhin geschrieben. Der externe Monitor meldet `HEALTHY`. |
| EC-3 | Questor ist in `PLANNING` und der LLM-Advisor antwortet nicht (Timeout). Der Watchdog prüft die Zustandsdauer. | `PLANNING` hat ein Limit von 120 Sekunden. Wenn der LLM-Timeout 30 Sekunden beträgt und der Watchdog nach 120 Sekunden noch keinen Zustandswechsel sieht, wird ein `WATCHDOG_STATE_DURATION`-Alarm ausgelöst. |
| EC-4 | Questor schreibt den Heartbeat, aber die Disk ist voll. | `HEARTBEAT_WRITE_FAILED` wird protokolliert. Questor arbeitet weiter. Der externe Monitor erkennt den veralteten Heartbeat und meldet `UNHEALTHY`. |
| EC-5 | Questor stürzt ab (OOM-Killer). Der Heartbeat wird nicht mehr geschrieben. | Der externe Monitor erkennt den veralteten Heartbeat und meldet `DEAD`. Recovery-Aktion: Neustart. |
| EC-6 | Questor ist in `RECOVERING` und die Recovery dauert länger als 300 Sekunden. | `WATCHDOG_STATE_DURATION`-Alarm. Der externe Monitor meldet `UNHEALTHY`. Recovery-Aktion: Alert an Kanzler. |
| EC-7 | Die `health.json`-Datei wird von einem anderen Prozess gelöscht. | Der externe Monitor erkennt `HEALTH_FILE_NOT_FOUND` und meldet `DEAD`. Recovery-Aktion: Neustart. |
| EC-8 | Questor ist in `EXECUTING` und der `current_step_index` ändert sich seit 10 Minuten nicht. | `WATCHDOG_NO_PROGRESS`-Alarm. Der externe Monitor meldet `UNHEALTHY`. Recovery-Aktion: Alert an Kanzler. |
| EC-9 | Questor ist in `IDLE` und es gibt keine Pakete in `pending/`. Der Heartbeat wird weiterhin geschrieben. | Der externe Monitor meldet `HEALTHY`. Kein Alarm. |
| EC-10 | Questor startet neu und der Watchdog-Thread startet nicht. | Der Heartbeat wird weiterhin geschrieben, aber der `watchdog_status` bleibt auf dem letzten Wert. Der externe Monitor erkennt den fehlenden Watchdog-Status und meldet `DEGRADED`. |
| EC-11 | Der externe Monitor kann die `health.json` nicht lesen (Permission-Error). | `MONITOR_CHECK_FAILED` wird protokolliert. Der externe Monitor versucht es erneut. Nach 3 Fehlversuchen: Alert an Kanzler. |
| EC-12 | Questor ist in `FINALIZING` und der Ergebnisbau dauert länger als 60 Sekunden. | `WATCHDOG_STATE_DURATION`-Alarm. Der externe Monitor meldet `UNHEALTHY`. Recovery-Aktion: Alert an Kanzler. |

---

## 12. Sicherheitsregeln (Fail-Closed-Punkte)

| # | Regel | Fail-Closed-Aktion |
|---|---|---|
| S1 | **Health-Monitoring ist OPERATIONAL.** Ein Health-Monitoring-Fehler ist niemals SAFETY oder SCIENTIFIC. | `abbruch_klasse = OPERATIONAL`. |
| S2 | **Health-Monitoring blockiert nicht.** Der Heartbeat-Writer und der Watchdog laufen in separaten Threads. | Questor arbeitet weiter, auch wenn das Health-Monitoring fehlschlägt. |
| S3 | **Kein automatischer Neustart bei WAITING_FOR_RELEASE oder SAFE_HOLD.** Diese Zustände werden durch externe Ereignisse gesteuert. | Kein Neustart. Alert an Kanzler. |
| S4 | **Kein automatischer Neustart ohne WAL-Prüfung.** Vor einem Neustart muss der WAL geprüft werden. | WAL-Prüfung durchführen. |
| S5 | **Keine Eskalation ohne menschliche Freigabe.** Eine Eskalation kann zu `SAFE_MODE` führen, aber nur durch menschliche Freigabe. | Alert an Kanzler. Kanzler entscheidet. |
| S6 | **Heartbeat ist atomar.** Der Heartbeat wird über temp file + rename geschrieben. | Keine korrupten Heartbeat-Dateien. |
| S7 | **Watchdog löst keine direkten Aktionen aus.** Der Watchdog meldet nur. Die Aktionen werden vom externen Monitor ausgelöst. | Keine direkten Aktionen vom Watchdog. |
| S8 | **Alert-Cooldown verhindert Alert-Stürme.** Alerts werden nur alle `alert_cooldown_s` Sekunden gesendet. | Keine Alert-Stürme. |
| S9 | **Health-Monitoring schreibt keine Blackbox.** Health-Events werden in `data/operational_logs/` geschrieben, nicht in `data/questor_blackbox/`. | Keine Blackbox-Einträge. |
| S10 | **Health-Monitoring schreibt nicht in Atlas oder Archiv.** Health-Events sind operational. | Keine Atlas- oder Archiv-Einträge. |

---

## 13. Integration mit bestehenden Komponenten

### 13.1 Questor-Zustandsmaschine

Der Heartbeat-Writer und der interne Watchdog werden beim Questor-Start gestartet und beim Questor-Shutdown gestoppt.

```python
# Beim Questor-Start:
heartbeat_writer = HeartbeatWriter(config, questor_state)
heartbeat_writer.start()

internal_watchdog = InternalWatchdog(config, questor_state)
internal_watchdog.start()

# Beim Questor-Shutdown:
heartbeat_writer.stop()
internal_watchdog.stop()
```

### 13.2 Queue-Architektur

Die `health.json` wird in `data/questor_queue/` gespeichert, zusammen mit der `registry.json`.

```
data/questor_queue/
  ├── pending/
  ├── processing/
  ├── completed/
  ├── failed/
  ├── delete_requests/
  ├── registry.json
  └── health.json          ← NEU
```

### 13.3 Pipeline-Orchestrator (Gremium)

Der Pipeline-Orchestrator liest die `health.json` und prüft den Gesundheitszustand von Questor.

```python
# Im Pipeline-Orchestrator:
questor_monitor = ExternalQuestorMonitor(config)

while True:
    health_check = questor_monitor.check_questor_health()
    
    if health_check.overall_status == "DEAD":
        restart_questor()
    elif health_check.overall_status == "UNHEALTHY":
        if health_check.recommended_action == "RESTART":
            restart_questor()
        else:
            alert_kanzler(health_check)
    elif health_check.overall_status == "DEGRADED":
        alert_kanzler(health_check)
    
    time.sleep(config.external_monitor_interval_s)
```

### 13.4 ExpeditionLedger

Health-Events werden NICHT im Ledger gespeichert. Das Ledger ist für die Paket-Ausführung, nicht für das Health-Monitoring.

### 13.5 Operational Logs

Health-Events werden in `data/operational_logs/` geschrieben:

```yaml
HealthEvent:
  timestamp: "2025-07-15T12:00:00Z"
  event_type: WATCHDOG_WARNING
  health_status: DEGRADED
  watchdog_status: WARNING
  details:
    check: memory
    memory_usage_mb: 1900.0
    memory_limit_mb: 2048.0
  action_taken: null
```

### 13.6 WAL

Das Health-Monitoring hat **keine** direkte Integration mit dem WAL. Der WAL wird nur für die Paket-Ausführung verwendet.

### 13.7 Result-Builder

Das Health-Monitoring hat **keine** direkte Integration mit dem Result-Builder. Health-Events erzeugen keine `questor_ergebnis_paket`.

### 13.8 Blackbox-Archiver

Das Health-Monitoring hat **keine** direkte Integration mit dem Blackbox-Archiver. Health-Events werden nicht in der Blackbox gespeichert.

### 13.9 Graceful-Shutdown (Thema 4)

Das Health-Monitoring erkennt, wenn Questor sich beendet. Der letzte Heartbeat wird geschrieben. Der externe Monitor erkennt, dass Questor nicht mehr antwortet.

### 13.10 Trail-Map (Thema 6)

Health-Alerts werden als Trails protokolliert:

| DecisionType | Trigger |
|---|---|
| `HEALTH_ALERT` | Health-Alert wurde ausgelöst |

### 13.11 Queue-Integration (Thema 7)

Die `health.json` wird in der Queue gespeichert. Der externe Monitor liest die `health.json` und die `registry.json`.

---

## 14. Validierung durch konkretes Beispiel

### 14.1 Szenario: Questor hängt in PLANNING

**Ausgangszustand:**
- Questor ist in `PLANNING` seit 150 Sekunden.
- Das Zeitlimit für `PLANNING` ist 120 Sekunden.
- Der Heartbeat wird alle 5 Sekunden geschrieben.
- Der externe Monitor prüft alle 30 Sekunden.

### 14.2 Ablauf

**Schritt 1: Watchdog erkennt Zustandsdauer-Überschreitung**
```
Zeit: T+150s
Watchdog-Check: state_duration
  current_state: PLANNING
  state_since: T+0s
  duration_s: 150
  limit_s: 120
  → WATCHDOG_STATE_DURATION Alarm
  → watchdog_status = CRITICAL
```

**Schritt 2: Heartbeat wird geschrieben**
```
Zeit: T+155s
Heartbeat-Writer schreibt health.json:
  health_status: UNHEALTHY
  watchdog_status: CRITICAL
  current_state: PLANNING
  current_state_since: T+0s
  watchdog_checks:
    state_duration_ok: false
    memory_ok: true
    cpu_ok: true
    progress_ok: true
    wal_ok: true
```

**Schritt 3: Externer Monitor prüft**
```
Zeit: T+180s
Externer Monitor liest health.json:
  heartbeat_age_s: 25 (frisch)
  health_status: UNHEALTHY
  watchdog_status: CRITICAL
  → overall_status: UNHEALTHY
  → recommended_action: ALERT
```

**Schritt 4: Alert an Kanzler**
```
Zeit: T+180s
Alert an Kanzler:
  event_type: HEALTH_ALERT
  health_status: UNHEALTHY
  watchdog_status: CRITICAL
  details:
    check: state_duration
    current_state: PLANNING
    duration_s: 180
    limit_s: 120
  recommended_action: ALERT
```

**Schritt 5: Kanzler prüft**
```
Zeit: T+300s
Kanzler prüft den Zustand:
  → Questor ist in PLANNING seit 300 Sekunden
  → LLM-Advisor antwortet nicht
  → Entscheidung: Questor neu starten
```

**Schritt 6: Neustart**
```
Zeit: T+310s
1. SIGTERM an Questor senden
2. Warten auf Graceful-Shutdown (60 Sekunden)
3. Wenn Questor nicht beendet: SIGKILL
4. WAL prüfen
5. Questor neu starten
6. Questor führt Recovery aus
7. Health-Event protokollieren
```

### 14.3 Ergebnis

Questor wurde als `UNHEALTHY` erkannt. Der Kanzler wurde alarmiert. Questor wurde neu gestartet. Das Paket wurde aus dem WAL wiederhergestellt.

---

## 15. Offene Fragen und Risiken

| # | Frage / Risiko | Schweregrad | Empfehlung |
|---|---|---|---|
| Q1 | **Wer ist der "externe Monitor"?** Der Pipeline-Orchestrator (Gremium) oder ein separater Prozess? | Hoch | Empfehlung: Der Pipeline-Orchestrator ist der externe Monitor. Er hat bereits Zugriff auf die Queue und die Registry. |
| Q2 | **Was passiert, wenn der externe Monitor selbst ausfällt?** | Hoch | Empfehlung: Das Betriebssystem (systemd, Kubernetes) überwacht den externen Monitor als Fallback. |
| Q3 | **Sollte Questor sich selbst neu starten können?** | Mittel | Empfehlung: NEIN. Questor sollte sich nicht selbst neu starten. Der externe Monitor oder das Betriebssystem sollte das tun. |
| Q4 | **Wie wird der Questor-Prozess neu gestartet?** | Mittel | Empfehlung: Über systemd oder Kubernetes. Der externe Monitor sendet ein Signal an den Prozess-Manager. |
| Q5 | **Was passiert, wenn Questor in WAITING_FOR_RELEASE ist und der externe Monitor einen Neustart auslöst?** | Hoch | Empfehlung: KEIN Neustart bei WAITING_FOR_RELEASE oder SAFE_HOLD. Nur Alert an Kanzler. |
| Q6 | **Sollte das Health-Monitoring in die OperationalMetrics aufgenommen werden?** | Niedrig | Empfehlung: JA. `health_alert_count` und `health_restart_count` sollten in die OperationalMetrics aufgenommen werden. |
| Q7 | **Was passiert, wenn die health.json-Datei zu groß wird?** | Niedrig | Empfehlung: Die health.json ist klein (< 10 KB). Kein Problem. |

---

## 16. Zusammenfassung der Spezifikation

| Aspekt | Definition |
|---|---|
| **Modulname** | `health_monitor.py` |
| **Position** | `src/questor/health_monitor.py` |
| **Heartbeat-Datei** | `data/questor_queue/health.json` |
| **Heartbeat-Intervall** | Default: 5 Sekunden (konfigurierbar) |
| **Watchdog-Intervall** | Default: 10 Sekunden (konfigurierbar) |
| **Externes Monitor-Intervall** | Default: 30 Sekunden (konfigurierbar) |
| **Heartbeat-Stale-Threshold** | Default: 15 Sekunden (3× Heartbeat-Intervall) |
| **Gesundheitszustände** | `HEALTHY`, `DEGRADED`, `UNHEALTHY`, `DEAD` |
| **Watchdog-Status** | `OK`, `WARNING`, `CRITICAL` |
| **Recovery-Aktionen** | `NONE`, `ALERT`, `RESTART`, `ESCALATE` |
| **Fehlerbehandlung** | Immer OPERATIONAL, niemals SAFETY, niemals SCIENTIFIC |
| **Fail-Closed** | Kein automatischer Neustart bei WAITING_FOR_RELEASE oder SAFE_HOLD |
| **Integration** | Queue-Architektur, Pipeline-Orchestrator, Operational Logs |

---

## 17. Kritische Bewertung der eigenen Spezifikation

**Stärken:**
- Klare Gesundheitszustände mit definierten Übergängen
- Heartbeat-Mechanismus mit atomarem Schreiben
- Interner Watchdog mit konfigurierbaren Zeitlimits
- Externer Monitor mit definierten Recovery-Aktionen
- Alert-Cooldown verhindert Alert-Stürme
- Health-Monitoring ist immer OPERATIONAL
- Integration mit Queue-Architektur und Pipeline-Orchestrator

**Schwächen:**
- Der externe Monitor ist der Pipeline-Orchestrator, der selbst ausfallen könnte
- Kein automatischer Neustart bei WAITING_FOR_RELEASE oder SAFE_HOLD (bewusst, aber einschränkend)
- Die health.json ist eine einzelne Datei, die korrupt werden könnte
- Kein Health-Monitoring für den externen Monitor selbst

**Empfehlung:** Die Spezifikation ist implementierungsreif, ABER:
1. Der externe Monitor sollte durch das Betriebssystem (systemd, Kubernetes) als Fallback überwacht werden.
2. Die health.json sollte als atomare Datei geschrieben werden (temp file + rename).
3. Die Health-Monitoring-Konfiguration sollte in der Questor-Konfiguration enthalten sein.

---

## 18. Kreuzreferenzen

| Referenz | Beziehung |
|---|---|
| `structure_questor_interna_v0.4.0.md`, Teil O | Dieses Dokument IST Teil O |
| `structure_questor_interna_v0.3.0.md` §59 | Questor-Prozess mit Hauptloop |
| `structure_questor_interna_v0.3.0.md` §58 | Queue-Architektur |
| `questor_graceful_shutdown_v0.1.0.md` | Shutdown interagiert mit Health-Monitoring |
| `questor_trail_map_v0.1.0.md` | Health-Alerts werden als Trails protokolliert |
| `questor_queue_integration_v0.1.0.md` | health.json wird in der Queue gespeichert |
| `questor_test_strategy_v0.1.0.md` | 15 Unit-Tests (U-HM-01 bis U-HM-15) |
| `questor_implementation_plan_v0.1.0.md` | Phase Q12 (2-3 Tage) |