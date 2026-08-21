# 🏛️ GREMIUM — VOLLSTÄNDIGE SPEZIFIKATION

| Feld | Wert |
| :--- | :--- |
| **Dateiname** | `specs/GREMIUM.md` |
| **Version** | 1.0.0 (New Architecture) |
| **Status** | **BINDEND** — Alle Gremium-Komponenten |
| **System** | MYRMEX v2.4.0 + Questor v0.2.3 |
| **Schicht** | Layer 1 (specs/) — referenziert foundation/ |
| **Datum** | 21. August 2026 |

---

## 0. Geltung und Änderungsregeln

Dieses Dokument definiert die vollständige Gremium-Spezifikation (Schicht 4 im MYRMEX-System).

**Regel:** Dieses Dokument referenziert Verträge aus `CONTRACTS.md` und Sicherheitsregeln aus `CHARTER.md`.
Es definiert keine neuen Verträge und keine neuen Sicherheitsregeln.

**Konfliktregel:** Bei Widersprüchen gilt `CHARTER.md` > `CONTRACTS.md` > dieses Dokument.

---

## §1 Gremium-Übersicht und Grundprinzipien

### §1.1 Position im System

Das Gremium ist Schicht 4 im MYRMEX-System (→ CHARTER §1.1).

```
┌─────────────────────────────────────────────────────────────────┐
 │                    SCHICHT 5: 👑 KÖNIGIN                        │
 │  Langfristige Vision, Meta-Ziele, menschliche Führung           │
 └───────────────────────────────┬─────────────────────────────────┘
                                 │
 ┌───────────────────────────────▼─────────────────────────────────┐
 │                    SCHICHT 4: 🏛️ GREMIUM                         │
 │                                                                   │
 │  ┌──────────────────────────────────────────────────────────┐   │
 │  │              9-STUFEN-PIPELINE                             │   │
 │  │  Stufe 1: Wissens-Aufnahme (Archivar)                     │   │
 │  │  Stufe 2: Atlas-Strukturierung (Kartograph)               │   │
 │  │  Stufe 3: Strategische Review (Kanzler ↔ Königin)         │   │
 │  │  Stufe 4: Ideen-Generierung (Vordenker)                   │   │
 │  │  Stufe 5a: Pre-Filter (Deterministisch)                   │   │
 │  │  Stufe 5b: Ideen-Erdung (Lotse)                           │   │
 │  │  Stufe 6: Paket-Bau (Quartiermeister)                     │   │
 │  │  Stufe 7: Sicherheits-Gate (Richter + Seher)              │   │
 │  │  Stufe 8: Dispatch & Execution (Dispatcher → Questor)     │   │
 │  └──────────────────────────────────────────────────────────┘   │
 │                                                                   │
 │  ┌──────────────────────────────────────────────────────────┐   │
 │  │              SICHERHEITSRAT                                │   │
 │  │  Richter (deterministisch) · Seher (LLM)                  │   │
 │  │  Circuit-Breaker · Berufung · Policy-Veto-Review          │   │
 │  └──────────────────────────────────────────────────────────┘   │
 │                                                                   │
 │  ┌──────────────────────────────────────────────────────────┐   │
 │  │              PIPELINE-ORCHESTRATOR                         │   │
 │  │  Stufen-Übergänge · Bounded Queues · Deadlock-Erkennung   │   │
 │  └──────────────────────────────────────────────────────────┘   │
 │                                                                   │
 │  ┌──────────────────────────────────────────────────────────┐   │
 │  │              ATLAS & SIGNAL-SYSTEM                         │   │
 │  │  Signal-Stacks · Kristallisation · Clustering             │   │
 │  │  fracture_score · FULL_REBUILD · NEUAUSRICHTEN            │   │
 │  └──────────────────────────────────────────────────────────┘   │
 │                                                                   │
 └─────────────────────────────────────────────────────────────────┘
                                 │
 ┌───────────────────────────────▼─────────────────────────────────┐
 │              SCHICHT 3: ⚖️ DISPATCH-KOORDINATION                  │
 │  Dispatch-Vorbereitung, Lease-/Gate-Koordination                 │
 └───────────────────────────────┬─────────────────────────────────┘
                                 │
 ┌───────────────────────────────▼─────────────────────────────────┐
 │              SCHICHT 2: 🧭 QUESTOR                               │
 │  Paketgebundenes Execution Subsystem                             │
 └───────────────────────────────┬─────────────────────────────────┘
                                 │
 ┌───────────────────────────────▼─────────────────────────────────┐
 │              SCHICHT 1: 🔌 HAL & RESOURCE GOVERNOR               │
 │  Slot-Routing, Leases, ESTOP, Hardwarezugriff                    │
 └───────────────────────────────┬─────────────────────────────────┘
                                 │
 ┌───────────────────────────────▼─────────────────────────────────┐
 │              SCHICHT 0: ⚙️ PHYSIS / COMPUTE                      │
 │  Hardware, Simulation, Compute                                   │
 └─────────────────────────────────────────────────────────────────┘
```

### §1.2 Die sechs Gremium-Grundprinzipien

| # | Prinzip | Bedeutung | CHARTER-Referenz |
| :--- | :--- | :--- | :--- |
| 1 | **Blackboard-Pattern** | Alle Ränge des Gremiums kommunizieren ausschließlich über Atlas und Archiv. Keine direkten Aufrufe zwischen Rängen. | CHARTER §2 |
| 2 | **Menschliche Königin wird niemals überstimmt** | Bei Konflikt zwischen menschlicher und LLM-Königin gewinnt die menschliche Weisung. Nach 2 Konflikten fällt die LLM-Königin auf menschliche Entscheidung zurück. | CHARTER §SR-11 |
| 3 | **Fail-Closed** | Wenn etwas nicht sicher geprüft werden kann: keine Freigabe, keine physische Ausführung, kontrollierter Abbruch oder Eskalation. | CHARTER §SR-10 |
| 4 | **Seher schreibt niemals 🟥** | Der Seher (LLM-Komponente) darf niemals direkt rote Signale schreiben. Rote Signale dürfen nur durch deterministische Komponenten oder nach Sicherheitsprüfung entstehen. | CHARTER §SR-13 |
| 5 | **Operational ≠ Scientific** | Operationale Fehler erzeugen keine wissenschaftlichen Signale. | CHARTER §SR-08 |
| 6 | **Questor ist kein Gremium-Rang** | Questor darf nicht in Atlas oder Archiv schreiben. | CHARTER §SR-04 |

### §1.3 Was das Gremium DARF

| Erlaubt | Begründung |
| :--- | :--- |
| Atlas und Archiv verwalten | Kernaufgabe des Gremiums |
| Ideen generieren und bewerten | Stufe 4–5b der Pipeline |
| Pakete bauen | Stufe 6 der Pipeline |
| Sicherheits-Gates durchführen | Stufe 7 der Pipeline |
| Dispatch koordinieren | Stufe 8 der Pipeline |
| Ergebnisse von Questor empfangen und verarbeiten | Stufe 1 der Pipeline |
| Kristalle und Signale schreiben | Aus validierten wissenschaftlichen Ergebnissen |
| Operational-Logs schreiben | Für Nachvollziehbarkeit |

### §1.4 Was das Gremium NICHT DARF

| Verboten | CHARTER-Referenz |
| :--- | :--- |
| QuestorBlackbox lesen | CHARTER §SR-07 |
| Questor-interne Trails interpretieren | — |
| Wissenschaftliche Signale aus operationalen Fehlern erzeugen | CHARTER §SR-08 |
| ESTOP zurücksetzen | CHARTER §SR-05 |
| Leases vergeben | CHARTER §SR-06 |
| Hardware direkt ansprechen | CHARTER §SR-12 |
| Menschliche Königin überstimmen | CHARTER §SR-11 |

---

## §2 Die 9-Stufen-Pipeline

### §2.1 Übersicht

Die Pipeline verarbeitet wissenschaftliche Ideen von der Entstehung bis zur Ausführung:

| Stufe | Name | Verantwortlich | Beschreibung |
| :--- | :--- | :--- | :--- |
| 1 | Wissens-Aufnahme | Archivar | Empfängt `questor_ergebnis_paket`, schreibt Kristalle und Signale |
| 2 | Atlas-Strukturierung | Kartograph | Strukturiert Wissen in Zonen, Cluster, Signale |
| 3 | Strategische Review | Kanzler ↔ Königin | Langfristige Ausrichtung, Realitäts-Check |
| 4 | Ideen-Generierung | Vordenker | Erzeugt Roh-Ideen aus Atlas-Mustern |
| 5a | Pre-Filter | Deterministischer Fast-Path | Filtert offensichtliche Probleme (Dimensionen, Quarantäne) |
| 5b | Ideen-Erdung | Lotse | Platziert Wegmarken im Atlas (IDEE_GEPRÜFT → WEGMARKE_PLATZIERT) |
| 6 | Paket-Bau | Quartiermeister | Baut `ResearchPackage` aus Wegmarke |
| 7 | Sicherheits-Gate | Richter + Seher | Sicherheitsprüfung (NORMAL, FRACTURE_DIAGNOSIS, HIGH_RISK_OVERRIDE, SANDBOX) |
| 8 | Dispatch & Execution | Dispatcher → Questor → Receiver → Archivar | Ausführung über `QuestorDispatchEnvelope` |

### §2.2 Datenfluss zwischen den Stufen

```
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

### §2.3 Der vollständige Datenfluss

```
┌─────────────────────────────────────────────────────────────────┐
 │                    IDEEN-PIPELINE (Stufen 4, 5a, 5b)             │
 │                                                                   │
 │  Vordenker → Pre-Filter → Lotse                                 │
 │  (RohIdee)   (deterministisch)  (Wegmarke im Atlas)             │
 └───────────────────────────────┬─────────────────────────────────┘
                                 │
 ┌───────────────────────────────▼─────────────────────────────────┐
 │                    PAKET-PIPELINE (Stufen 6, 7, 8)               │
 │                                                                   │
 │  Quartiermeister → Sicherheits-Gate → Dispatcher                 │
 │  (ResearchPackage)  (Richter + Seher)  (QuestorDispatchEnvelope) │
 └───────────────────────────────┬─────────────────────────────────┘
                                 │
 ┌───────────────────────────────▼─────────────────────────────────┐
 │                    QUESTOR-ANBINDUNG                              │
 │                                                                   │
 │  QuestorDispatchEnvelope → Questor → questor_ergebnis_paket      │
 └───────────────────────────────┬─────────────────────────────────┘
                                 │
 ┌───────────────────────────────▼─────────────────────────────────┐
 │                    WISSENS-PIPELINE (Stufen 1, 2)                │
 │                                                                   │
 │  Archivar → Kartograph → Atlas                                   │
 │  (Kristalle, Signale)  (Zonen, Cluster, fracture_score)          │
 └─────────────────────────────────────────────────────────────────┘
```

---

## §3 Gremium-Komponenten

### §3.1 Archivar (Stufe 1)

**Verantwortung:** Empfängt `questor_ergebnis_paket` von Questor und verarbeitet es.

**Pflichten:**
- Prüft `idempotency_key` (→ CONTRACTS §8.1)
- Prüft `sequence_number` pro `questor_instance_id`
- Prüft `vollstaendig_flag`
- Trennt `abbruch_klasse`:
  - `OPERATIONAL` → kein wissenschaftliches Signal (→ CHARTER §SR-08)
  - `SCIENTIFIC` → Kristall + Signal möglich
  - `SAFETY` → Sicherheits-Signal
- Schreibt Kristalle nur aus validierten wissenschaftlichen Ergebnissen
- Schreibt keine wissenschaftlichen Signale bei `OPERATIONAL`
- Darf `operational_metrics` in den `operational_event_log` übernehmen
- Liest keine QuestorBlackbox (→ CHARTER §SR-07)

**Verbote:**
- Keine Blackbox lesen
- Keine Questor-internen Trails interpretieren
- Keine operationalen Fehlerklassen als wissenschaftliche Signale behandeln

### §3.2 Kartograph (Stufe 2)

**Verantwortung:** Strukturiert das Wissen im Atlas.

**Pflichten:**
- Zonen-Verwaltung (mit parent/child-Hierarchie)
- Cluster-Bildung (DBSCAN-basiert)
- Signal-Verwaltung (🟥, 🟨, 🟪, 🟩, ⬜)
- `fracture_score`-Berechnung
- FULL_REBUILD (atomar)
- NEUAUSRICHTEN (inkrementell)

### §3.3 Kanzler (Stufe 3)

**Verantwortung:** Strategische Review und Realitäts-Check.

**Pflichten:**
- Lagebericht erstellen
- Weisungsprüfung
- SAFE_MODE verwalten
- Policy-Veto-Review durchführen
- Audit-Log führen
- Periodische Template-Zusammenfassung erhalten (G-8)

### §3.4 Vordenker (Stufe 4)

**Verantwortung:** Erzeugt Roh-Ideen aus Atlas-Mustern.

**Pflichten:**
- Atlas-Muster analysieren
- Roh-Ideen generieren
- `prozess_skizze` mit Idee liefern (G-5)

### §3.5 Pre-Filter (Stufe 5a)

**Verantwortung:** Deterministischer Fast-Path für offensichtliche Probleme.

**Pflichten:**
- Dimension-Freigabe prüfen
- Quarantäne-Zonen prüfen
- Sättigungs-Zustände prüfen

### §3.6 Lotse (Stufe 5b)

**Verantwortung:** Ideen-Erdung und Wegmarken-Platzierung.

**Pflichten:**
- Wegmarken im Atlas platzieren
- Zustand: `IDEE_OFFEN` → `IDEE_GEPRÜFT` → `WEGMARKE_PLATZIERT`
- Nur in Weißraum oder bestätigten grünen Zonen

### §3.7 Quartiermeister (Stufe 6)

**Verantwortung:** Baut `ResearchPackage` aus Wegmarke.

**Pflichten:**
- Routing-Graph erstellen
- Material/Resource-Listen erstellen
- Parameter-Bounds setzen
- Gefahren-Mitigationen definieren
- `questor_spec` setzen (mit sicheren Defaults, → CONTRACTS §1.2)
- `planning_hints` als optionales Feld setzen (G-12)
- `autonomy_level` basierend auf Aufgabe setzen
- `template_feedback` berücksichtigen (G-9)

---

## §4 Sicherheitsrat (Stufe 7)

### §4.1 Übersicht

Der Sicherheitsrat besteht aus:
- **Richter** (deterministisch)
- **Seher** (LLM)
- **Circuit-Breaker** (Zustandsmaschine)
- **Appeal** (Berufung)
- **Policy-Veto-Review** (Audit)

### §4.2 Richter (deterministisch)

**Verantwortung:** Regelprüfung, Policy-Enforcement, Fail-Closed.

**Regeln:**
- Prüft deterministisch gegen definierte Regeln
- Bei Regelverletzung: `FAIL`
- Bei bestandener Prüfung: `PASS`
- Fail-Closed: Wenn eine Regel nicht sicher geprüft werden kann → `FAIL`

### §4.3 Seher (LLM)

**Verantwortung:** Evidenz-Bewertung.

**Regeln:**
→ Siehe CHARTER §SR-13 für die LLM-Advisor-Regel.

- Der Seher ist eine LLM-Komponente
- Der Seher darf **niemals** direkt 🟥 schreiben (→ CHARTER §SR-13)
- Der Seher bewertet Evidenz und gibt `PASS`, `VETO` oder `TEMP_SUSPENDED` zurück
- Veto nur mit Evidenz
- Bei Veto ohne Evidenz: `SEHER_INVALID_VETO`

### §4.4 Circuit-Breaker (Zustandsmaschine)

**Verantwortung:** Überwacht Seher-Fehlerraten und setzt den Seher temporär aus.

**Zustände:**

| Zustand | Bedeutung |
| :--- | :--- |
| `NORMAL` | Seher arbeitet normal |
| `SHADOW_MODE` | Seher wird überwacht, aber seine Entscheidungen werden nicht direkt umgesetzt |
| `TEMP_SUSPENDED` | Seher ist temporär suspendiert |
| `PERMANENT_SUSPENDED` | Seher ist permanent suspendiert (nur manuelle Rückkehr) |

**Messfenster und Stichprobe:**

```
window_size = 100
minimum_sample_size = 20
max_window_age_days = 28
```

**Regeln:**
- Metriken werden über ein gleitendes Fenster berechnet
- Automatische Zustandswechsel erfolgen nur, wenn `minimum_sample_size` erreicht ist
- Bei zu kleiner Stichprobe darf höchstens ein Alert, aber kein automatischer Sicherheitszustandswechsel ausgelöst werden

**Schwellwerte:**

| Metrik | Schwellwert | Aktion |
| :--- | :--- | :--- |
| `invalid_veto_rate > 0.3` | Alert an Kanzler |
| `false_block_rate > 0.5` | `SHADOW_MODE` |
| `appeal_success_rate > 0.7` | `TEMP_SUSPENDED` |

**Hysterese und Rückkehr:**

Rückkehr nach `NORMAL` erfordert:
1. Metrik liegt in zwei aufeinanderfolgenden Fenstern unter dem jeweiligen Schwellwert
2. Manuelle Prüfung durch Kanzler oder dafür vorgesehenen Sicherheitsprozess
3. Audit-Event für die Rückkehr

`PERMANENT_SUSPENDED`:
- Wird nur manuell durch Kanzler oder menschliche Königin ausgelöst
- Hat keine automatische Rückkehr
- Erfordert expliziten Audit-Trail

**Audit-Felder für Zustandswechsel:**

```
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

### §4.5 Appeal (Berufung)

**Verantwortung:** Bei Richter-Pass + Seher-Veto.

**Ablauf:**
1. Richter gibt `PASS`
2. Seher gibt `VETO`
3. Appeal wird ausgelöst
4. Kanzler prüft den Appeal
5. Appeal wird `GRANTED` oder `DENIED`

### §4.6 Policy-Veto-Review

**Verantwortung:** Periodische Überprüfung von Policy-Vetos.

**Konfigurationsparameter:**

```
policy_veto_review_interval_cycles = 20
```

**Wertebereich:**
- Minimum: 1
- Maximum: 500
- Default: 20
- `0` ist nicht erlaubt

**Persistenz:**
- Der Review-Zähler wird persistent geführt
- Ein Neustart setzt den Zähler nicht zurück
- SAFE_MODE kann die Zählung pausieren, setzt sie aber nicht zurück

**Review-Entscheidungen:**
- Bestätigen
- Aufheben
- Eskalieren

**Audit-Event:**

Jeder Review erzeugt ein Audit-Event `policy_veto_review` mit mindestens:
```
event_type
zyklus_id
policy_veto_id
review_decision
review_reason
review_timestamp
review_authority
escalation_target
```

### §4.7 Gate-Zustandsmaschine

→ Siehe CONTRACTS §7.4 für die vollständige Zustandsmaschine.

| Zustand | Bedeutung |
| :--- | :--- |
| `GATE_PENDING` | Paket wartet auf Sicherheitsprüfung |
| `RICHTER_PRUEFT` | Richter prüft deterministisch |
| `SEHER_PRUEFT` | Seher bewertet (wenn Richter PASS) |
| `FREIGEGEBEN` | Gate passiert (Richter PASS + Seher PASS) |
| `DISPUTED` | Berufung läuft (Richter PASS + Seher VETO) |
| `ABGELEHNT` | Gate nicht passiert |

**Übergänge:**

| Von | Nach | Auslöser |
| :--- | :--- | :--- |
| `GATE_PENDING` | `RICHTER_PRUEFT` | Start |
| `RICHTER_PRUEFT` | `ABGELEHNT` | Richter FAIL |
| `RICHTER_PRUEFT` | `SEHER_PRUEFT` | Richter PASS |
| `SEHER_PRUEFT` | `FREIGEGEBEN` | Seher PASS |
| `SEHER_PRUEFT` | `DISPUTED` | Seher VETO (startet Appeal) |
| `DISPUTED` | `FREIGEGEBEN` | Appeal GRANTED |
| `DISPUTED` | `ABGELEHNT` | Appeal DENIED |

### §4.8 Gate-Modi

→ Siehe CONTRACTS §4.4 für den GateMode-Vertrag.

| Modus | Bedeutung |
| :--- | :--- |
| `NORMAL` | Standardbetrieb |
| `FRACTURE_DIAGNOSIS` | Diagnose bei hohem fracture_score |
| `HIGH_RISK_OVERRIDE` | Überschreibung mit positiver Widerlegung erforderlich |
| `SANDBOX` | Sandbox-Modus, keine physische Ausführung |

---

## §5 Pipeline-Orchestrator

### §5.1 Verantwortung

Der Pipeline-Orchestrator koordiniert die Stufen-Übergänge und verwaltet die Bounded Queues.

### §5.2 Bounded Queues mit Watermarks

Jede Pipeline-Stufe hat eine begrenzte Queue:

```
Queue-Struktur:
  - max_size: maximale Größe
  - high_watermark: Warnschwelle (z.B. 80%)
  - low_watermark: Entwarnung (z.B. 50%)

Verhalten:
  - Bei high_watermark: Neue Items werden abgelehnt
  - Bei low_watermark: Normalbetrieb resumes
  - Deadlock-Erkennung überwacht alle Queues
```

### §5.3 Deadlock-Erkennung

Der Orchestrator erkennt Deadlocks:

**Erkennung:**
- Zyklische Abhängigkeiten zwischen Queues
- Timeouts bei State-Transitions
- Blockierte Leases ohne Fortschritt

**Behandlung:**
- Notventil-Zyklen initiieren
- Pakete in vorherige Stufe zurücksetzen
- Circuit-Breaker für betroffene Komponenten

### §5.4 Notventil-Zyklen

Bei Deadlock oder kritischem Fehler:

```
Notventil-Ablauf:
  1. Alle aktiven Transaktionen stoppen
  2. Pakete in sichere Zustände zurücksetzen
  3. Leases freigeben oder suspendieren
  4. SAFE_MODE aktivieren (falls nötig)
  5. Menschliche Königin benachrichtigen
```

### §5.5 Externer Questor-Monitor

→ Siehe specs/QUESTOR.md §16 für das Questor-Health-Monitoring.

Der Pipeline-Orchestrator liest die `health.json` und prüft den Gesundheitszustand von Questor.

```
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

---

## §6 Atlas und Signal-System

### §6.1 Signal-Typen

| Symbol | Name | Bedeutung | Quelle |
| :--- | :--- | :--- | :--- |
| 🟥 | ROT | Kritischer Fehler, Sicherheitsproblem | Nur Sicherheits-Gate/ESTOP |
| 🟨 | GELB | Warnung, erhöhte Vorsicht | Kartograph, Lotse |
| 🟪 | PURPUR | Quarantäne, diagnostisch nur | Lotse (nur mit Budget) |
| 🟩 | GRÜN | Bestätigt, sicher | Nach 3 Bestätigungen |
| ⬜ | WEISS | Unbestätigt, neutral | Default für neue Signale |

### §6.2 Signal-Resolution

Signale werden priorisiert aufgelöst:

```
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

### §6.3 Kristallisation und Verfall

**Kristallisation:**
- Nach 3 Bestätigungen wird Signal zu Kristall
- Kristalle sind persistent
- Kristalle bilden Atlas-Struktur

**Verfall:**
- Signale zerfallen über Zeit (TTL)
- Ungenutzte Signale verblassen
- `fracture_score` steigt bei vielen roten Signalen

### §6.4 fracture_score und Zone-Health

```
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

### §6.5 FULL_REBUILD und NEUAUSRICHTEN

**FULL_REBUILD:**
- Atomarer Neuaufbau des gesamten Atlas
- Alle Zonen und Cluster neu berechnen
- Signale neu bewerten
- Nur bei kritischem fracture_score

**NEUAUSRICHTEN:**
- Inkrementelle Anpassung
- Betroffene Zonen neu strukturieren
- Minimale Unterbrechung

### §6.6 Atlas-Versionierung

```
atlas_version_ref: str  # z.B. "atlas-v2.4.0-head"

Regeln:
  - Questor empfängt atlas_version_ref als Pass-Through
  - Questor setzt observed_atlas_version_id = atlas_version_ref
  - Questor darf atlas_version_ref NICHT interpretieren
  - Questor darf atlas_version_ref NICHT ändern
  - Questor darf atlas_version_ref NICHT einem LLM übergeben
```

→ Siehe CHARTER §SR-15 für die Pass-Through-Regel.

---

## §7 Dispatch-Koordination (Stufe 8)

### §7.1 Dispatcher

**Verantwortung:** Erzeugt `QuestorDispatchEnvelope` und schreibt in die Queue.

→ Siehe specs/QUESTOR.md §18 für die vollständige Queue-Integration.

**Input:**
- `research_package`
- `gate_record`
- `lease_grants`
- `execution_environment_ref`
- `dispatch_mode`
- `security_mode`

**Vor Dispatch prüfen:**
- `gate_record.signature`
- `lease_status = GRANTED` oder kontrolliert `QUEUED`
- Heartbeat/TTL
- Slot-Zustand
- Routing-Limits vorhanden
- Dimensions-Approval vorhanden, falls physisch
- `security_mode` passend

**Output:**
- `QuestorDispatchEnvelope` (→ CONTRACTS §1.3)

**Verbote:**
- Kein produktiver Versand ohne `gate_record_ref` (→ CHARTER §SR-53)
- Kein produktiver Versand ohne gültige Lease-Logik
- Keine direkte physische Ausführung ohne Envelope (→ CHARTER §SR-01)

### §7.2 Receiver

**Verantwortung:** Empfängt `questor_ergebnis_paket` von Questor.

→ Siehe specs/QUESTOR.md §18 für die vollständige Queue-Integration.

**Pflichten:**
- Vertrag validieren
- Idempotenz prüfen (→ CONTRACTS §8.1)
- Sequence prüfen
- An Archivar übergeben

**Verbote:**
- Blackbox lesen
- Questor-interne Trails interpretieren
- Wissenschaftliche Signale eigenmächtig umschreiben
- Alte Vertragsformen akzeptieren

### §7.3 Questor-Anbindung

```
QuestorDispatchEnvelope → Questor → questor_ergebnis_paket
```

**QuestorDispatchEnvelope enthält:**
- `dispatch_id`, `zyklus_id`, `attempt_id`
- `package: ResearchPackage`
- `gate_record_ref: str` (Pflicht)
- `gate_mode: NORMAL | FRACTURE_DIAGNOSIS | HIGH_RISK_OVERRIDE | SANDBOX`
- `lease_grants: list[LeaseGrant]`
- `idempotency_key` (kanonisch: `package_id:zyklus_id:attempt_id`)

**Questor führt aus:**
- Innerhalb gültiger Leases
- Beachtet `security_mode`
- Schreibt lokale Blackbox (`data/questor_blackbox/`)

**questor_ergebnis_paket enthält:**
- `status: erfolgreich | fehlgeschlagen | abgebrochen`
- `abbruch_klasse: OPERATIONAL | SCIENTIFIC | SAFETY`
- `kristall_kandidaten`, `signale_fuer_atlas`
- `questor_metadata` (optional, operational)

---

## §8 Gremium-Auslagerungen

→ Siehe CHARTER §4 für die vollständige Liste aller 22 Gremium-Auslagerungen.

Die folgenden Gremium-Auslagerungen sind für das Gremium relevant:

| # | Thema | Gremium-Komponente |
| :--- | :--- | :--- |
| G-1 | Template-Erstellung bei fehlendem Template | Quartiermeister + Domain-Experte |
| G-2 | Template-Korrektur nach Questor-Feedback | Domain-Experte (NICHT Kanzler) |
| G-3 | Template-Versionierung (alte Versionen im Archiv) | Archivar |
| G-4 | Ressourcen-Karte (Verbrauch pro Zone/Dimension) | Kartograph |
| G-5 | Vordenker liefert prozess_skizze mit Idee | Vordenker |
| G-6 | template_feedback operational protokollieren | Archivar |
| G-7 | Kosten-Schätzungen für Reagenzien | System-Integrator |
| G-8 | Kanzler erhält periodische Template-Zusammenfassung | Kanzler (nur Übersicht) |
| G-9 | Quartiermeister berücksichtigt template_feedback | Quartiermeister |
| G-10 | atlas_version_ref ist Pass-Through, kein LLM-Zugriff | Questor (intern) |
| G-11 | loop_selection_weights optional im QuestorSpec | Quartiermeister |
| G-12 | planning_hints als optionales Feld | Quartiermeister |
| G-13 | Pipeline-Orchestrator liest registry.json und aktualisiert Atlas | Pipeline-Orchestrator (Gremium) |
| G-14 | Archivar bereinigt completed/ und failed/ nach Archivierung | Archivar |
| G-15 | Gremium schreibt Löschanfragen in delete_requests/ | Kanzler / Quartiermeister |
| G-16 | Capability-Definitionen erstellen und pflegen | System-Integrator |
| G-17 | Health-Monitoring: Externer Monitor liest health.json | Pipeline-Orchestrator |
| G-18 | Health-Monitoring: Recovery-Aktionen auslösen | Kanzler / Pipeline-Orchestrator |
| G-19 | Shutdown-Signal senden (SIGTERM) | Kanzler / Orchestrator |
| G-20 | Trail-Map lesen (nur autorisierte Rollen) | Domain-Experte / Entwickler |
| G-21 | Test-Strategie: CI/CD einrichten | System-Integrator |
| G-22 | Implementierungsplan: Phasen freigeben | Kanzler / Architekt |

---

## §9 Zustandsmaschinen der Pipeline-Stufen

### §9.1 Stufe 5b: IDEE_OFFEN → IDEE_GEPRÜFT → WEGMARKE_PLATZIERT

→ Siehe CONTRACTS §7.4 für die vollständige Zustandsmaschine.

**Zustände:**
- `IDEE_OFFEN`: Idee wurde vom Vordenker erzeugt
- `IDEE_GEPRÜFT`: Pre-Filter hat bestanden
- `WEGMARKE_PLATZIERT`: Lotse hat Wegmarke im Atlas platziert
- `IDEE_VERWORFEN`: Idee wurde verworfen (blocked_cache)

**Übergänge:**
- `IDEE_OFFEN` → `IDEE_GEPRÜFT`: Pre-Filter erfolgreich
- `IDEE_GEPRÜFT` → `WEGMARKE_PLATZIERT`: Lotse platziert erfolgreich
- `IDEE_GEPRÜFT` → `IDEE_VERWORFEN`: Lotse verwirft (rote/gelbe/purpurne Zone)
- `IDEE_OFFEN` → `IDEE_VERWORFEN`: Pre-Filter verwirft

### §9.2 Stufe 6: WEGMARKE_RESERVIERT → ... → PAKET_FERTIG

→ Siehe CONTRACTS §7.4 für die vollständige Zustandsmaschine.

**Zustände:**
- `WEGMARKE_RESERVIERT`: Wegmarke wurde für Paketbau reserviert
- `PAKET_IM_BAU`: Quartiermeister baut Paket
- `PAKET_FERTIG`: Paket ist vollständig
- `PAKET_FEHLGESCHLAGEN`: Paketbau fehlgeschlagen

**Übergänge:**
- `WEGMARKE_RESERVIERT` → `PAKET_IM_BAU`: Quartiermeister startet
- `PAKET_IM_BAU` → `PAKET_FERTIG`: Paketbau erfolgreich
- `PAKET_IM_BAU` → `PAKET_FEHLGESCHLAGEN`: Paketbau fehlgeschlagen

### §9.3 Stufe 7: GATE_PENDING → ... → FREIGEGEBEN / DISPUTED

→ Siehe CONTRACTS §7.4 für die vollständige Zustandsmaschine.

**Zustände:**
- `GATE_PENDING`: Paket wartet auf Sicherheitsprüfung
- `RICHTER_PRUEFT`: Richter prüft deterministisch
- `SEHER_PRUEFT`: Seher bewertet (wenn Richter PASS)
- `FREIGEGEBEN`: Gate passiert (Richter PASS + Seher PASS)
- `DISPUTED`: Berufung läuft (Richter PASS + Seher VETO)
- `ABGELEHNT`: Gate nicht passiert

**Übergänge:**
- `GATE_PENDING` → `RICHTER_PRUEFT`: Start
- `RICHTER_PRUEFT` → `ABGELEHNT`: Richter FAIL
- `RICHTER_PRUEFT` → `SEHER_PRUEFT`: Richter PASS
- `SEHER_PRUEFT` → `FREIGEGEBEN`: Seher PASS
- `SEHER_PRUEFT` → `DISPUTED`: Seher VETO (startet Appeal)
- `DISPUTED` → `FREIGEGEBEN`: Appeal GRANTED
- `DISPUTED` → `ABGELEHNT`: Appeal DENIED

### §9.4 Stufe 8: RESOURCE_WAITING → ... → ABGESCHLOSSEN / ABORTED

→ Siehe CONTRACTS §7.4 für die vollständige Zustandsmaschine.

**Zustände:**
- `RESOURCE_WAITING`: Wartet auf Leases
- `LEASE_GRANTED`: Leases wurden gewährt
- `QUESTOR_DISPATCHED`: An Questor gesendet
- `QUESTOR_RUNNING`: Questor führt aus
- `ABGESCHLOSSEN`: Erfolgreich abgeschlossen
- `ABORTED`: Abgebrochen (OPERATIONAL/SCIENTIFIC/SAFETY)

**Übergänge:**
- `RESOURCE_WAITING` → `LEASE_GRANTED`: Leases gewährt
- `RESOURCE_WAITING` → `ABORTED`: LeaseDenied (kein ESTOP!)
- `LEASE_GRANTED` → `QUESTOR_DISPATCHED`: Envelope gesendet
- `QUESTOR_DISPATCHED` → `QUESTOR_RUNNING`: Questor startet
- `QUESTOR_RUNNING` → `ABGESCHLOSSEN`: Erfolgreich
- `QUESTOR_RUNNING` → `ABORTED`: Fehler/Abbruch

---

## §10 Event-Driven Architecture

### §10.1 Pipeline-Events

Events werden über den Pipeline-Orchestrator verteilt:

**Event-Typen:**
- `IDEE_ERZEUGT`: Vordenker hat Idee generiert
- `IDEE_GEPRUEFT`: Pre-Filter erfolgreich
- `WEGMARKE_PLATZIERT`: Lotse hat Wegmarke gesetzt
- `PAKET_GEBAUT`: Quartiermeister fertig
- `GATE_FREIGEGEBEN`: Sicherheits-Gate passiert
- `QUESTOR_COMPLETED`: Questor fertig
- `KRISTALL_ERZEUGT`: Archivar hat Kristall geschrieben
- `SIGNAL_ERZEUGT`: Archivar hat Signal geschrieben

### §10.2 Bounded Queues mit Watermarks

Jede Pipeline-Stufe hat eine begrenzte Queue:

```
Queue-Struktur:
  - max_size: maximale Größe
  - high_watermark: Warnschwelle (z.B. 80%)
  - low_watermark: Entwarnung (z.B. 50%)

Verhalten:
  - Bei high_watermark: Neue Items werden abgelehnt
  - Bei low_watermark: Normalbetrieb resumes
  - Deadlock-Erkennung überwacht alle Queues
```

### §10.3 Deadlock-Erkennung

Der Orchestrator erkennt Deadlocks:

**Erkennung:**
- Zyklische Abhängigkeiten zwischen Queues
- Timeouts bei State-Transitions
- Blockierte Leases ohne Fortschritt

**Behandlung:**
- Notventil-Zyklen initiieren
- Pakete in vorherige Stufe zurücksetzen
- Circuit-Breaker für betroffene Komponenten

### §10.4 Notventil-Zyklen

Bei Deadlock oder kritischem Fehler:

```
Notventil-Ablauf:
  1. Alle aktiven Transaktionen stoppen
  2. Pakete in sichere Zustände zurücksetzen
  3. Leases freigeben oder suspendieren
  4. SAFE_MODE aktivieren (falls nötig)
  5. Menschliche Königin benachrichtigen
```

---

## §11 Sicherheitsregeln

→ Siehe CHARTER §3 für die vollständige Liste aller 58 Sicherheitsregeln.

Die folgenden Sicherheitsregeln sind für das Gremium relevant:

| # | Regel | CHARTER-Referenz |
| :--- | :--- | :--- |
| 1 | Keine physische Ausführung ohne Envelope | CHARTER §SR-01 |
| 2 | Keine physische Ausführung ohne Gate | CHARTER §SR-02 |
| 3 | Keine physische Ausführung ohne Lease | CHARTER §SR-03 |
| 4 | Questor schreibt nicht in Atlas/Archiv | CHARTER §SR-04 |
| 5 | Questor setzt ESTOP nicht zurück | CHARTER §SR-05 |
| 6 | Questor vergibt keine Leases | CHARTER §SR-06 |
| 7 | Blackbox bleibt lokal | CHARTER §SR-07 |
| 8 | Operational ≠ Scientific | CHARTER §SR-08 |
| 9 | ESTOP ≠ LEASE_DENIED | CHARTER §SR-09 |
| 10 | Fail-Closed bei Unklarheit | CHARTER §SR-10 |
| 11 | Menschliche Königin wird niemals überstimmt | CHARTER §SR-11 |
| 12 | Hardwarezugriff nur über HAL | CHARTER §SR-12 |
| 13 | LLM nur Advisor, niemals final | CHARTER §SR-13 |
| 14 | Kein Dispatch ohne gate_record_ref | CHARTER §SR-53 |
| 15 | Keine Duplikate in der Queue | CHARTER §SR-54 |
| 16 | Atomare Schreiboperationen | CHARTER §SR-55 |
| 17 | Registry-Lock | CHARTER §SR-56 |
| 18 | Kein Löschen von processing/ | CHARTER §SR-57 |
| 19 | Queue-Fehler sind immer OPERATIONAL | CHARTER §SR-58 |

---

## §12 Implementierungsphasen

### §12.1 Übersicht

→ Siehe specs/QUESTOR.md §20 für den vollständigen Questor-Implementierungsplan.

Die folgenden Phasen sind für das Gremium relevant:

| Phase | Name | Dauer (Schätzung) |
| :--- | :--- | :--- |
| Phase 1 | Contracts & Datenmodelle | 3–5 Tage |
| Phase 2 | Atlas & Signal-System | 3–4 Tage |
| Phase 3 | Transaction (WAL, State Machine) | 2–3 Tage |
| Phase 4 | Resource Governor & HAL | 3–4 Tage |
| Phase 5 | Gremium Basis (Archivar, Kartograph) | 3–4 Tage |
| Phase 6 | Gremium Erweitert (Vordenker, Lotse) | 3–4 Tage |
| Phase 7 | Sicherheitsrat (Richter, Seher) | 3–4 Tage |
| Phase 8 | Questor-Interface | 2–3 Tage |
| Phase 9 | Pipeline-Orchestrierung | 3–4 Tage |
| Phase 10 | Integration & Regression | 5–7 Tage |

### §12.2 Phase 1: Contracts & Datenmodelle

**Aufgaben:**
- Alle Pydantic-Modelle definieren (→ CONTRACTS)
- Alle Enums definieren
- Idempotenz-Regeln implementieren

**Akzeptanzkriterien:**
- [ ] Alle Modelle sind Pydantic-v2-konform
- [ ] Alle Enums vorhanden
- [ ] Idempotenzregeln korrekt
- [ ] Mindestens 50 Unit-Tests

### §12.3 Phase 5: Gremium Basis (Archivar, Kartograph)

**Aufgaben:**
- Archivar implementieren
- Kartograph implementieren
- Atlas-Store implementieren
- Signal-Registry implementieren

**Akzeptanzkriterien:**
- [ ] Archivar empfängt und verarbeitet `questor_ergebnis_paket`
- [ ] Archivar trennt `abbruch_klasse` korrekt
- [ ] Archivar liest keine Blackbox
- [ ] Kartograph strukturiert Atlas korrekt
- [ ] Mindestens 40 Unit-Tests

### §12.4 Phase 7: Sicherheitsrat (Richter, Seher)

**Aufgaben:**
- Richter implementieren
- Seher implementieren (LLM)
- Circuit-Breaker implementieren
- Appeal implementieren
- Policy-Veto-Review implementieren

**Akzeptanzkriterien:**
- [ ] Richter ist deterministisch und fail-closed
- [ ] Seher schreibt niemals direkt 🟥
- [ ] Circuit-Breaker greift bei Schwellwerten
- [ ] Appeal funktioniert korrekt
- [ ] Policy-Veto-Review ist konfigurierbar
- [ ] Mindestens 40 Unit-Tests

### §12.5 Phase 8: Questor-Interface

**Aufgaben:**
- Dispatcher implementieren
- Receiver implementieren
- DummyQuestor implementieren

**Akzeptanzkriterien:**
- [ ] Dispatcher baut `QuestorDispatchEnvelope`
- [ ] Dispatcher prüft Gate, Lease, Security-Mode
- [ ] Receiver empfängt `questor_ergebnis_paket`
- [ ] Keine produktiven nackten Paketübergaben
- [ ] Mindestens 40 Unit-Tests

### §12.6 Phase 10: Integration & Regression

**Aufgaben:**
- Alle Integrationstests durchführen
- Alle Regressions-Tests durchführen
- Alle Szenario-Tests durchführen

**Akzeptanzkriterien:**
- [ ] Alle Pflichttests bestehen
- [ ] Keine Endlosschleifen
- [ ] Keine Deadlocks
- [ ] Keine Blackbox im Gremium
- [ ] Mindestens 120 Integrationstests

---

## §13 Zusammenfassung der Architektur-Entscheidungen

| Thema | Entscheidung | Quelle |
| :--- | :--- | :--- |
| Blackboard-Pattern | Alle Ränge kommunizieren über Atlas und Archiv | §1.2 |
| Menschliche Königin | Wird niemals überstimmt | §1.2 |
| Fail-Closed | Bei Unklarheit: keine Freigabe | §1.2 |
| Seher | Schreibt niemals direkt 🟥 | §1.2 |
| Operational ≠ Scientific | Strikte Trennung | §1.2 |
| Questor | Ist kein Gremium-Rang | §1.2 |
| 9-Stufen-Pipeline | Vollständig definiert | §2 |
| Sicherheitsrat | Richter + Seher + Circuit-Breaker + Appeal + Policy-Veto-Review | §4 |
| Circuit-Breaker | 4 Zustände, Messfenster, Hysterese | §4.4 |
| Policy-Veto-Review | Konfigurierbar, persistent, Audit-Event | §4.6 |
| Pipeline-Orchestrator | Bounded Queues, Deadlock-Erkennung, Notventil | §5 |
| Atlas | Signal-Typen, Kristallisation, fracture_score | §6 |
| Dispatch | Envelope-basiert, Queue-Integration | §7 |
| Gremium-Auslagerungen | 22 Auslagerungen | §8 |
| Zustandsmaschinen | 4 Pipeline-Stufen | §9 |
| Event-Driven Architecture | Pipeline-Events, Bounded Queues | §10 |
| Sicherheitsregeln | 19 relevante Regeln | §11 |
| Implementierungsphasen | 10 Phasen | §12 |

---

## §14 Dokumentenhierarchie

Dieses Dokument steht in der Schicht `specs/` und referenziert:
- `foundation/CHARTER.md` für Sicherheitsregeln (CHARTER §SR-XX)
- `foundation/CONTRACTS.md` für Datenverträge (CONTRACTS §X.X)
- `specs/QUESTOR.md` für Questor-spezifische Details
- `specs/HAL.md` für HAL-spezifische Details

**Regel:** Änderungen an Gremium-Modulen in diesem Dokument erfordern eine Versionsänderung und eine Überprüfung der referenzierten Dokumente.