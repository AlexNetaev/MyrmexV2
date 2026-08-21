# 🧭 STRUCTURE_STANDALONE_QUESTCOMPASS_V0.1.0

---

```
🧭 MYRMEX V2.4.0 + QUESTOR V0.2.3 — QUESTCOMPASS-SPEZIFIKATION
Dateiname:       structure_standalone_questcompass_v0.1.0.md
Version:         0.1.0
System:          MYRMEX v2.4.0 + Questor v0.2.3
Status:          Arbeitsstand — Architektur-Diskussion, keine Implementierungsfreigabe
Bezug:           structure_standalone_v2.4.0.md v1.1.1 (kanonisch)
                 structure_hal_v0.2.0.md
                 structure_standalone_questor_v0.2.3.md (unterstützend)
Sprache:         Deutsch
Modus:           Dry-Run / Spezifikation
```

---

## 0. Dokumentenhierarchie und Geltung

Diese Datei ist eine **Spezialisierung der Questor-Interna** und steht unterhalb der kanonischen Hauptreferenz.

```
1. structure_standalone_v2.4.0.md v1.1.1          ← kanonisch
2. structure_hal_v0.2.0.md                         ← HAL-Vertrag
3. diese Datei: structure_standalone_questcompass_v0.1.0.md
4. structure_standalone_questor_v0.2.3.md          ← unterstützend
```

Bei Widersprüchen gilt die kanonische Hauptreferenz.

---

## 1. Zweck dieser Datei

Diese Datei definiert die **internen Mechanismen** von Questor, die in der Hauptreferenz und der Questor-Spezifikation als „Black Box" behandelt werden:

- Die Questor-Zustandsmaschine
- Den QuestCompass-Algorithmus (Planung, Ausführung, Bewertung, Re-Planung)
- Die Loop-Architektur (Templates, Instanzen, Ketten)
- Den Template-Lebenszyklus (Erstellung, Korrektur, Versionierung)
- Die Evaluationslogik (objective-type-spezifisch)
- Die Entscheidungstabelle (GO, VETO, RE-PLAN, ABBRUCH)
- Die LLM-Advisor-Integration (Ollama/gemma4:31b-cloud)
- Den PolicyEvaluator als Gatekeeper
- Die Recovery-Logik (WAL-basiert)
- Die template_feedback-Erzeugung

---

## 2. Grundannahmen und Kontext

| Annahme | Wert |
|---|---|
| Nebenläufigkeit | Questor verarbeitet **immer nur EIN Paket** sequentiell |
| LLM-Backend | Ollama mit `gemma4:31b-cloud` (abstrahiert, wechselbar) |
| Questor ist Totalfunktion | Jedes Paket → genau ein Ergebnis, auch bei Early-Abort |
| Questor schreibt nie in Atlas/Archiv | In allen Szenarien bestätigt |
| Questor setzt ESTOP nie zurück | Explizit verboten |
| Questor vergibt keine Leases | Leases kommen vom Resource Governor |
| Recovery-Mechanismus | **NUR WAL** (Write-Ahead Log), keine Blackbox-Recovery |

---

## 3. Die sechs Lebensphasen eines Questor-Laufs

```
┌──────────┐   ┌──────────┐   ┌──────────────────────────────────┐   ┌──────────┐   ┌──────────┐
│ PHASE 1  │──►│ PHASE 2  │──►│ PHASE 3: PLANUNGS- &             │──►│ PHASE 5  │──►│ PHASE 6  │
│ EMPFANG  │   │ VALIDIER.│   │ AUSFÜHRUNGSZYKLUS                │   │ ERGEBNIS │   │ BLACKBOX │
└──────────┘   └──────────┘   │                                  │   └──────────┘   └──────────┘
                              │  ┌────────┐  ┌────────────────┐  │
                              │  │PLANNING│→ │  EXECUTING     │  │
                              │  └────┬───┘  └───────┬────────┘  │
                              │       │              │            │
                              │       │         ┌────┴────┐      │
                              │       │         │EVALUAT. │      │
                              │       │         └────┬────┘      │
                              │       │              │            │
                              │       └── RE-PLAN ───┘            │
                              └──────────────────────────────────┘
```

### PHASE 1: EMPFANG

Questor empfängt ein Eingangsdokument.

| Eingang | Wann erlaubt | Wer sendet |
|---|---|---|
| `QuestorDispatchEnvelope` | Produktiver Normalfall | Dispatcher |
| `ResearchPackage` (direkt) | NUR in `DEV_SANDBOX_ONLY` | Test/Entwicklung |

**Prüfung:**
- Ist ein Eingang vorhanden?
- Ist es ein Envelope oder ein nacktes ResearchPackage?
- Wenn nacktes ResearchPackage und `security_mode ≠ DEV_SANDBOX_ONLY` → sofortiger Abbruch mit `DIRECT_PACKAGE_FORBIDDEN`

### PHASE 2: VALIDIERUNG

Questor prüft das empfangene Dokument auf formale Korrektheit.

**Prüfpunkte:**

| Prüfung | Bei Fehlschlag |
|---|---|
| `gate_record_ref` vorhanden? | `PACKAGE_INVALID` |
| `idempotency_key` kanonisch? | `PACKAGE_INVALID` |
| `attempt_id` im Bereich 0–999999? | `PACKAGE_INVALID` |
| `package_id` / `zyklus_id` Regex-konform? | `PACKAGE_INVALID` |
| `routing_graph.max_loop_iterations` vorhanden? | `PACKAGE_INVALID` |
| `routing_graph.branch_condition_timeout` vorhanden? | `PACKAGE_INVALID` |
| `security_mode` konsistent? | `PACKAGE_INVALID` |
| `dimension_expansion_approval` vorhanden, falls physisch? | `DIMENSION_APPROVAL_MISSING` |
| NaN/Infinity in numerischen Feldern? | `PACKAGE_INVALID` |

**In dieser Phase werden KEINE HAL-Befehle gesendet. Keine LLM-Aufrufe. Nur formale Prüfung.**

### PHASE 3: PLANUNGS- & AUSFÜHRUNGSZYKLUS

Siehe Abschnitt 5 (QuestCompass-Zyklus).

### PHASE 5: ERGEBNISBAU

Questor baut das `questor_ergebnis_paket`.

### PHASE 6: BLACKBOX

Questor schreibt die lokale Blackbox unter `data/questor_blackbox/`.

---

## 4. Die Questor-Zustandsmaschine

### 4.1 Zustände

| Zustand | Bedeutung | Dauer |
|---|---|---|
| `IDLE` | Questor wartet auf Envelope | Unbegrenzt |
| `RECEIVING` | Envelope empfangen, wird geprüft | Millisekunden |
| `VALIDATING` | Formale Validierung des Pakets | Millisekunden |
| `PLANNING` | Autonome Planung: Loop-Auswahl | Sekunden |
| `EXECUTING` | Loop wird ausgeführt (HAL-Kommandos) | Sekunden bis Tage |
| `EVALUATING` | Ergebnis gegen Objective prüfen | Sekunden |
| `WAITING_FOR_RELEASE` | Prozess wartet auf manuelle Freigabe | Stunden bis Tage |
| `SAFE_HOLD` | Prozess sicher angehalten (Lease-Expiry) | Stunden |
| `RECOVERING` | Nach Crash: Zustand wird geklärt | Sekunden bis Minuten |
| `FINALIZING` | Ergebnis wird gebaut | Millisekunden |
| `DONE` | Ergebnis wurde übergeben | Terminal |

### 4.2 Zustandsdiagramm

```
                    ┌──────┐
                    │ IDLE │
                    └──┬───┘
                       │ Envelope empfangen
                       ▼
                 ┌───────────┐
                 │ RECEIVING │
                 └─────┬─────┘
                       │ formal akzeptiert
                       ▼
                 ┌───────────┐     ungültig     ┌────────────┐
                 │VALIDATING │────────────────►│ FINALIZING │──► DONE
                 └─────┬─────┘                  └────────────┘
                       │ gültig
                       ▼
    ┌──────────────────────────────────────────────────────────┐
    │          PLANUNGS- & AUSFÜHRUNGSZYKLUS                    │
    │                                                          │
    │   ┌──────────┐                                          │
    │   │ PLANNING │◄──────────────────────────────┐          │
    │   └────┬─────┘                               │          │
    │        │ Plan erstellt                        │          │
    │        ▼                                     │          │
    │   ┌──────────┐                               │          │
    │   │EXECUTING │◄── RESUME nach SAFE_HOLD      │          │
    │   └────┬─────┘◄── RESUME nach WAITING        │          │
    │        │                                     │          │
    │   ┌────┴───────────────────┐                 │          │
    │   │                        │                 │          │
    │   │ Loops ausgeführt       │ ESTOP/Interlock │          │
    │   │                        │ / schwerer      │          │
    │   │                        │   Fehler        │          │
    │   ▼                        ▼                 │          │
    │ ┌──────────┐         ┌──────────┐            │          │
    │ │EVALUATING│         │FINALIZING│──► DONE    │          │
    │ └────┬─────┘         │(ABORT)   │            │          │
    │      │               └──────────┘            │          │
    │      │                                       │          │
    │ ┌────┴────────────────────────────┐          │          │
    │ │                                 │          │          │
    │ │ Ziel erreicht → FINALIZING      │          │          │
    │ │ Nicht erreicht + Budget → ──────┼──────────┘          │
    │ │ Nicht erreicht + kein Budget →  │                     │
    │ │   FINALIZING (TARGET_NOT_       │                     │
    │ │   REACHED)                      │                     │
    │ └─────────────────────────────────┘                     │
    │                                                          │
    │   Sonderzustände während EXECUTING:                      │
    │   ┌─────────────────────┐                               │
    │   │ WAITING_FOR_RELEASE │ ← Stufe braucht Freigabe      │
    │   └─────────────────────┘                               │
    │   ┌───────────┐                                         │
    │   │ SAFE_HOLD │ ← Lease-Expiry / Crash                  │
    │   └───────────┘                                         │
    │   ┌────────────┐                                        │
    │   │ RECOVERING │ ← Nach Crash: Zustand klären           │
    │   └────────────┘                                        │
    │                                                          │
    └──────────────────────────────────────────────────────────┘
```

### 4.3 Übergangstabelle

| Von | Nach | Auslöser | Bedingung |
|---|---|---|---|
| `IDLE` | `RECEIVING` | Envelope empfangen | Immer |
| `RECEIVING` | `VALIDATING` | Envelope akzeptiert | Formal korrekt |
| `RECEIVING` | `FINALIZING` | DIRECT_PACKAGE_FORBIDDEN | Kein Envelope, kein Sandbox |
| `VALIDATING` | `PLANNING` | Validierung bestanden | Alle Pflichtfelder gültig |
| `VALIDATING` | `FINALIZING` | Validierung fehlgeschlagen | PACKAGE_INVALID |
| `PLANNING` | `EXECUTING` | Plan erstellt | Loop gültig, Budget verfügbar, PolicyEvaluator GO |
| `PLANNING` | `FINALIZING` | Kein Template anwendbar | NO_APPLICABLE_TEMPLATE |
| `PLANNING` | `FINALIZING` | Objective unklar | ABORT_IF_UNCLEAR |
| `EXECUTING` | `EXECUTING` | HAL-Kommando erfolgreich | Weiter im aktuellen Loop |
| `EXECUTING` | `WAITING_FOR_RELEASE` | Stufe abgeschlossen, Freigabe nötig | stage_release_policy |
| `EXECUTING` | `SAFE_HOLD` | Lease-Expiry mit SAFE_HOLD-Policy | on_lease_expiry_policy |
| `EXECUTING` | `EVALUATING` | Alle Steps des Loops ausgeführt | Loop abgeschlossen |
| `EXECUTING` | `FINALIZING` | ESTOP/Interlock | Sicherheitsabbruch |
| `EXECUTING` | `FINALIZING` | Budget erschöpft während Ausführung | max_duration_s erreicht |
| `EXECUTING` | `RECOVERING` | Crash/OOM | Questor-Prozess stirbt |
| `EVALUATING` | `FINALIZING` | Ziel erreicht | Konfidenz ≥ clarity_threshold |
| `EVALUATING` | `PLANNING` | Ziel NICHT erreicht + Budget übrig | Re-Planung möglich |
| `EVALUATING` | `FINALIZING` | Ziel NICHT erreicht + Budget erschöpft | TARGET_NOT_REACHED |
| `EVALUATING` | `FINALIZING` | Ziel unerreichbar | TARGET_NOT_REACHABLE |
| `WAITING_FOR_RELEASE` | `EXECUTING` | Freigabe erteilt | release_stage() erfolgreich |
| `WAITING_FOR_RELEASE` | `FINALIZING` | Freigabe verweigert | STAGE_RELEASE_DENIED |
| `WAITING_FOR_RELEASE` | `FINALIZING` | Max-Wartezeit erreicht | max_wait_time_s |
| `SAFE_HOLD` | `RECOVERING` | Questor startet neu | Server-Restart |
| `SAFE_HOLD` | `FINALIZING` | Abbruch gewünscht | Manueller Abbruch |
| `RECOVERING` | `EXECUTING` | Zustand sicher, Resume möglich | reconcile erfolgreich |
| `RECOVERING` | `FINALIZING` | Zustand unsicher | RECOVERY_UNSAFE |
| `FINALIZING` | `DONE` | Ergebnis übergeben | Immer |
| `DONE` | `IDLE` | Ergebnis geliefert | Immer |

### 4.4 Invarianten

- Questor ist immer in genau EINEM Zustand.
- Jeder Zustand hat definierte Ein- und Ausgänge.
- `FINALIZING` erzeugt IMMER ein vollständiges `questor_ergebnis_paket`.
- `DONE` → `IDLE` ist der einzige Rückkehrpfad.
- `EXECUTING` ist der einzige Zustand, in dem HAL-Kommandos gesendet werden.
- `WAITING_FOR_RELEASE` und `SAFE_HOLD` sind Wartezustände ohne aktive HAL-Kommandos.
- `RECOVERING` darf keine neuen HAL-Kommandos senden, nur `reconcile_*` aufrufen.
- `FINALIZING` darf keine HAL-Kommandos senden.

---

## 5. Der QuestCompass-Zyklus

### 5.1 Überblick

QuestCompass ist das **Entscheidungszentrum** von Questor. Er ist KEIN eigenständiger Agent, sondern eine logische Funktion innerhalb der Questor-Zustandsmaschine.

Questor empfängt ein Paket mit einem **Ziel** und führt dann **autonom** folgende Schleife durch:

```
PLANEN → AUSFÜHREN → BEWERTEN → (fertig? / neu planen?)
    ▲                                          │
    └──────────── NEIN (Re-Planung) ───────────┘

Abbruch wenn:
  - Ziel erreicht (erfolgreich)
  - Budget erschöpft (fehlgeschlagen)
  - Ziel unerreichbar (fehlgeschlagen)
  - Sicherheitsereignis (abgebrochen)
```

**Die Loop-Kette entsteht durch den Prozess (Feedback-Schleife), nicht vorab.**

### 5.2 QuestCompass im Gesamtsystem

```
┌─────────────────────────────────────────────────────────────────┐
│                     QUESTOR-ZUSTANDSMASCHINE                     │
│                                                                   │
│   ┌────────────────────────────────────────────────────────┐     │
│   │                  QUESTCOMPASS                           │     │
│   │                                                         │     │
│   │  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │     │
│   │  │  Objective  │  │    Loop      │  │  Evaluation  │  │     │
│   │  │  Analysis   │→ │  Selection   │→ │  & Decision  │  │     │
│   │  └─────────────┘  └──────────────┘  └──────────────┘  │     │
│   │                                                         │     │
│   │  ┌──────────────┐                                      │     │
│   │  │  Hypothesis  │                                      │     │
│   │  │  Formulation │                                      │     │
│   │  └──────────────┘                                      │     │
│   └────────────────────────────────────────────────────────┘     │
│                          │                                       │
│                          ▼                                       │
│   ┌────────────────────────────────────────────────────────┐     │
│   │              POLICY EVALUATOR (Gatekeeper)              │     │
│   │  Occam's Razor · Safety Check · Budget Check            │     │
│   │  → GO oder VETO                                        │     │
│   └────────────────────────────────────────────────────────┘     │
│                          │                                       │
│                          ▼                                       │
│   ┌────────────────────────────────────────────────────────┐     │
│   │              SAFETY MONITOR                             │     │
│   │  ESTOP · Interlock · Timeout · Lease-Expiry             │     │
│   └────────────────────────────────────────────────────────┘     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Logische Rollen innerhalb des QuestCompass

| Logische Rolle | Implementiert in | Verantwortung |
|---|---|---|
| **Hypothesis Architect** | QuestCompass | Formuliert den nächsten Loop, plant die Ausführung |
| **Gatekeeper (Red Teamer)** | PolicyEvaluator | Prüft: Ist der Loop sicher? Nötig? Einfach genug? |
| **Machine Planner** | LoopRegistry + HAL-Bridge | Übersetzt den Loop in HAL-Kommandos |
| **Semantic Safety Agent** | SafetyMonitor | Überwacht die Ausführung auf Sicherheitsverletzungen |

**Keine separaten Agenten-Prozesse. Alles innerhalb der Questor-Zustandsmaschine.**

---

## 6. Die sechs Kernfunktionen des QuestCompass

### 6.1 Objective Analysis (Ziel-Analyse)

**Dreistufig, deterministic-first.**

```
STUFE 1: DETERMINISTISCH (immer zuerst)
  ├── objective_type aus QuestorSpec lesen (falls vorhanden)
  ├── parameter_bounds als Suchraum übernehmen
  ├── planning_hints als Startpunkt übernehmen (falls vorhanden)
  └── kontext.domaene als Domänen-Kontext übernehmen

STUFE 2: KEYWORD-MATCHING (falls objective_type fehlt)
  ├── "optimiere" / "maximiere" / "minimiere" → OPTIMIZE
  ├── "erkunde" / "variiere" / "teste" → EXPLORE
  ├── "validiere" / "bestätige" / "prüfe" → VALIDATE
  ├── "diagnostiziere" / "untersuche" → DIAGNOSE
  ├── "simuliere" → SIMULATE_ONLY
  └── "kläre" / "präzisiere" → CLARIFY

STUFE 2.5: OBJECTIVE-VERVOLLSTÄNDIGUNG (LLM, optional)
  → NUR wenn clarity_score < clarity_threshold
  → NUR wenn autonomy_level != STRICT
  → NUR wenn llm_budget.max_calls > 0
  → LLM darf das Ziel UMSCHREIBEN und VERVOLLSTÄNDIGEN
  → LLM darf NICHT die parameter_bounds ändern
  → QuestCompass entscheidet, ob er den Vorschlag annimmt

STUFE 3: LLM-ADVISOR (nur falls Stufe 1+2+2.5 unklar)
  ├── Nur wenn autonomy_level != STRICT
  ├── LLM darf NUR einen objective_type VORSCHLAGEN
  └── Bei LLM-Ausfall → Fail-Closed (ABORT_IF_UNCLEAR)
```

**Output:**

```python
ParsedObjective:
    objective_type: OPTIMIZE | EXPLORE | VALIDATE | DIAGNOSE | SIMULATE_ONLY | CLARIFY
    clarity_score: float              # 0.0 bis 1.0
    parameter_space: dict[str, tuple[float, float]]
    initial_hypothesis: str
    expected_outcome_type: str
    domain: str
    source: DETERMINISTIC | KEYWORD_MATCH | LLM_ADVISED
```

**Clarity-Score-Berechnung (deterministisch):**

| Bedingung | clarity_score |
|---|---|
| objective_type explizit + parameter_bounds + ziel > 10 Zeichen | 1.0 |
| objective_type durch Keyword-Matching + parameter_bounds | 0.7 |
| objective_type nur durch LLM ODER parameter_bounds sehr weit | 0.4 |
| objective_type unklar ODER parameter_bounds fehlen | 0.1 |

**Fail-Closed-Regel:** Wenn `clarity_score < clarity_threshold` → keine physische Ausführung.

### 6.2 Loop Selection (Loop-Auswahl)

**Deterministischer Filter + Ranking mit Autonomy-Level-gesteuertem Kandidatenfenster.**

```
SCHRITT 1: VERFÜGBARE TEMPLATES FILTERN
  ├── Nur Templates aus QuestorSpec.allowed_loop_templates
  ├── Nur Templates, die den objective_type unterstützen
  ├── Nur Templates, deren required_capabilities verfügbar sind
  ├── Nur Templates, deren estimated_total_cost <= Restbudget
  └── Nur Templates, deren required_slot_count <= verfügbare Slots

SCHRITT 2: RANKING (deterministisch)
  score = (
    w1 × objective_type_match
    + w2 × capability_coverage
    + w3 × cost_efficiency          # GESAMTKOSTEN, nicht Einzelkosten
    + w4 × iteration_history
    + w5 × simplicity
  )

  Default-Gewichte: w1=0.30, w2=0.25, w3=0.15, w4=0.15, w5=0.15
  Gewichte können im QuestorSpec.loop_selection_weights überschrieben werden.

SCHRITT 3: KANDIDATENFENSTER (autonomy_level)
  STRICT:    candidate_window = 1 → Nur Top-Loop, kein LLM
  GUIDED:    candidate_window = 3 → Top 3, LLM bei Score-Diff < 0.15
  ADAPTIVE:  candidate_window = 5 → Top 5, LLM darf beraten

  Sonderregel: Nur EIN Template verfügbar → kein LLM, direkt wählen.

SCHRITT 4: PARAMETER FÜLLEN
  ├── parameter_bounds aus dem Package übernehmen
  ├── planning_hints.initial_parameters als Startpunkt
  ├── Bei Re-Planung: Bisherige Ergebnisse als Startpunkt
  └── Parameter IMMER innerhalb der parameter_bounds halten
```

**Kostenberechnung (Gesamtkosten statt Einzelkosten):**

```
estimated_total_cost = estimated_cost_per_iteration
                     × estimated_iterations_needed

→ Ein teurerer Loop, der in 1 Iteration fertig wird,
  ist besser als ein billiger Loop, der 5 Iterationen braucht.
```

**Sonderfall FRACTURE_DIAGNOSIS:**

```
Wenn gate_mode == FRACTURE_DIAGNOSIS:
  → autonomy_level wird auf STRICT gezwungen
  → candidate_window = 1
  → Nur Templates mit objective_type DIAGNOSE erlaubt
  → max_retry_count = 0
  → LLM wird NICHT konsultiert
```

### 6.3 Hypothesis Formulation (Arbeitshypothese)

**Deterministisch aus der Objective und den Parametern abgeleitet. Kein LLM.**

| objective_type | Hypothese-Format |
|---|---|
| OPTIMIZE | „Bei {parameter} = {wert} erwarte ich eine {metrik} im Bereich [{min}, {max}]." |
| EXPLORE | „Die Variation von {parameter} zwischen {min} und {max} liefert neue Datenpunkte." |
| VALIDATE | „Die Messung bei {parameter} = {wert} sollte den Kristallwert {expected} bestätigen oder widerlegen." |
| DIAGNOSE | „Die Messung bei {parameter} = {wert} sollte die Inkonsistenz bestätigen oder widerlegen." |

Die Hypothese wird im **ExpeditionLedger** protokolliert.

### 6.4 Evaluation (Ergebnisbewertung)

**Objective-type-spezifisch, deterministisch.**

| objective_type | Bewertungskriterium | ZIEL ERREICHT wenn |
|---|---|---|
| OPTIMIZE | Konfidenz = 1.0 − (varianz / bereich) | konfidenz ≥ clarity_threshold |
| EXPLORE | Abdeckung des Parameterraums | abdeckung ≥ 0.8 |
| VALIDATE | Abweichung = \|gemessen − erwartet\| / erwartet | Immer (Bestätigung ODER Widerlegung) |
| DIAGNOSE | Inkonsistenz = \|gemessen − atlas_erwartung\| | Immer (Bestätigung ODER Widerlegung) |
| SIMULATE_ONLY | Simulation abgeschlossen? | JA |
| CLARIFY | Objective wurde präzisiert? | JA |

**Konfidenz-Berechnung für OPTIMIZE:**

```python
def calculate_confidence(measurements, expected_range):
    if len(measurements) < 3:
        return 0.3
    variance = statistics.variance(measurements)
    range_size = expected_range[1] - expected_range[0]
    confidence = max(0.0, 1.0 - (variance / range_size))
    last_three = measurements[-3:]
    if max(last_three) - min(last_three) < range_size * 0.1:
        confidence = min(1.0, confidence + 0.1)
    return round(confidence, 3)
```

### 6.5 Decision Engine (Entscheidungslogik)

**Deterministische Entscheidungstabelle. Regeln in dieser Reihenfolge prüfen:**

| Regel | Bedingung | Aktion |
|---|---|---|
| **REGEL 1** | safety_status == ESTOP oder INTERLOCK | SOFORT ABBRUCH (SAFETY) |
| **REGEL 2** | policy_evaluator_result == VETO | Alternative suchen, sonst ABBRUCH |
| **REGEL 3** | evaluation_result == ZIEL_ERREICHT | FINALIZING (erfolgreich) |
| **REGEL 4** | Nicht erreicht + Budget übrig + Loop erreichbar | RE-PLANUNG |
| **REGEL 5** | Nicht erreicht + Ziel unerreichbar | ABBRUCH (TARGET_NOT_REACHABLE, SCIENTIFIC) |
| **REGEL 6** | Nicht erreicht + kein Budget | ABBRUCH (BUDGET_EXHAUSTED) |
| **REGEL 7** | Fehler + retry_count < max_retry_count | RETRY |
| **REGEL 8** | max_duration_s erreicht | ABBRUCH (BUDGET_EXHAUSTED) |

**Wichtige Korrektur:** Das Ziel ist NICHT, das Budget auszugeben, sondern das Ziel zu erreichen. Budget ist eine Obergrenze, kein Ziel.

### 6.6 LLM-Advisor-Integration

**LLM-Backend:** Ollama mit `gemma4:31b-cloud` (abstrahiert, wechselbar).

**Drei erlaubte Situationen:**

| Situation | Wann | Was darf LLM | Fallback |
|---|---|---|---|
| OBJECTIVE CLARIFICATION | clarity_score < threshold | objective_type vorschlagen | ABORT_IF_UNCLEAR |
| LOOP SELECTION ADVICE | Mehrere Templates mit ähnlichem Score | Template empfehlen | Einfachstes Template |
| RESULT INTERPRETATION | Messergebnisse mehrdeutig | Ergebnisse interpretieren | Deterministische Evaluation |

**Was LLM NIEMALS darf:**

| Verbot | Begründung |
|---|---|
| Final entscheiden | Deterministic-first |
| parameter_bounds ändern | Sicherheitsrelevant |
| allowed_capabilities ändern | Sicherheitsrelevant |
| ESTOP zurücksetzen | Sicherheitsrelevant |
| Atlas-Signale schreiben | Questor darf nicht in Atlas |
| atlas_version_ref lesen/ändern | Pass-Through, kein LLM-Zugriff |
| gate_record_ref lesen | Sicherheitsrelevant |
| lease_grants interpretieren | Sicherheitsrelevant |
| idempotency_key ändern | Intern |

**Prompt-Injection-Schutz:**

```python
PASS_THROUGH_FIELDS = {
    "atlas_version_ref", "package_id", "zyklus_id",
    "attempt_id", "idempotency_key",
}

def sanitize_for_llm(context):
    return {k: v for k, v in context.items()
            if k not in PASS_THROUGH_FIELDS
            and k in {"ziel", "kontext", "parameter_bounds", "planning_hints"}}
```

**LLM-Metriken (in operational_metrics):**

```yaml
llm_advice_rejected_count: 0
llm_advice_timeout_count: 0
llm_calls_used: 0
llm_calls_remaining: 3
```

---

## 7. Der PolicyEvaluator (Gatekeeper)

### 7.1 Aufgabe

Der PolicyEvaluator prüft jeden Loop-Vorschlag des QuestCompass BEVOR er ausgeführt wird.

### 7.2 Prüfungen

```python
class PolicyEvaluator:
    def evaluate(self, loop_instance, context) -> PolicyResult:

        # 1. Sicherheitsprüfung
        if context.safety_status in (ESTOP, INTERLOCK):
            return VETO("SAFETY_ACTIVE")

        # 2. Routing-Graph-Prüfung
        if not within_routing_graph(loop_instance, context.routing_graph):
            return VETO("OUTSIDE_ROUTING_GRAPH")

        # 3. Capability-Prüfung
        if not capabilities_available(loop_instance, context.hal_manifest):
            return VETO("CAPABILITY_UNAVAILABLE")

        # 4. Budget-Prüfung
        if not within_budget(loop_instance, context.remaining_budget):
            return VETO("BUDGET_EXCEEDED")

        # 5. Security-Mode-Prüfung
        if not security_mode_compatible(loop_instance, context.security_mode):
            return VETO("SECURITY_MODE_MISMATCH")

        # 6. Occam's Razor
        simpler = find_simpler_alternative(loop_instance, context)
        if simpler is not None:
            return VETO("SIMPLER_ALTERNATIVE_EXISTS", suggestion=simpler)

        # 7. Dimensions-Approval
        if loop_instance.requires_physical_actuation:
            if context.dimension_expansion_approval is None:
                return VETO("DIMENSION_APPROVAL_MISSING")

        # 8. Alle Prüfungen bestanden
        return GO()
```

### 7.3 Occam's Razor

Der PolicyEvaluator prüft:
- Kann das Ziel auch mit Simulation erreicht werden? → `SANDBOX_IF_UNCLEAR` priorisieren
- Kann ein einfacherer Loop das Ziel erreichen? → Einfacheren Loop vorschlagen
- Ist ein teurer Loop wirklich nötig? → Gesamtkosten vergleichen

**Achtung:** Immer den billigsten Loop zu wählen kann kontraproduktiv sein, wenn mehr Iterationen nötig sind. Der PolicyEvaluator vergleicht **Gesamtkosten**, nicht Einzelkosten.

---

## 8. Die Loop-Architektur

### 8.1 Die drei Ebenen

```
EBENE 1: LoopTemplate (Definition / Muster)
  → "optimize_loop_v1" ist ein Template
  → Beschreibt WIE optimiert wird

EBENE 2: LoopInstance (Konkrete Ausführung)
  → Eine konkrete Instanz mit konkreten Parametern
  → Wird im ExpeditionLedger protokolliert

EBENE 3: HALCommand / ProcessCommand (Physische Aktion)
  → Konkrete HAL-Befehle
```

### 8.2 LoopTemplate — Formale Definition

```yaml
LoopTemplate:
    # Identität
    template_id: str                    # z.B. "optimize_loop_v1"
    template_version: str               # z.B. "1.0" (semantisch)
    schema_version: str                 # z.B. "questor_template_v1"
    domain: str                         # z.B. "chemie", "biologie", "ml", "physik"
    created_by: str
    created_at: str
    last_modified: str

    # Zweck
    objective_types: list[ObjectiveType]
    description: str

    # Voraussetzungen
    required_capabilities: list[str]
    required_slot_count: int
    requires_physical_actuation: bool
    requires_long_running_process: bool

    # Struktur
    steps: list[LoopStep]
    max_internal_iterations: int

    # Parameter
    parameter_schema: dict[str, ParameterDefinition]

    # Terminierung
    termination_conditions: list[TerminationCondition]

    # Fehlerbehandlung
    on_step_failure: ABORT_LOOP | SKIP_STEP | RETRY_STEP
    max_step_retries: int

    # Kosten (vom Domain-Experten geschätzt)
    estimated_cost:
        total_time_s: float
        total_reagent_cost: float       # Normiert 0.0–1.0
        total_compute_cost: float       # Normiert 0.0–1.0
        total_energy_cost: float
```

### 8.3 LoopStep

```yaml
LoopStep:
    step_id: str
    step_type: HAL_COMMAND | PROCESS_COMMAND | MEASURE | WAIT | EVALUATE
    capability: Optional[str]
    operation: Optional[str]
    process_mode: Optional[str]         # Für PROCESS_COMMAND
    parameters: dict[str, Any]
    depends_on: list[str]
    branch_condition: Optional[BranchCondition]
    on_true_next: Optional[str]
    on_false_next: Optional[str]
    timeout_s: float
    cost:
        time_cost_s: float
        reagent_cost: float
        compute_cost: float
        energy_cost: float
```

### 8.4 LoopInstance

```python
LoopInstance:
    template_id: str
    template_version: str
    instance_id: str
    package_id: str
    resolved_parameters: dict[str, Any]
    state: PENDING | RUNNING | COMPLETED | FAILED | ABORTED | SAFE_HOLD
    current_step_index: int
    completed_steps: list[str]
    iteration_count: int
    step_results: dict[str, StepResult]
    started_at: Optional[str]
    finished_at: Optional[str]
    last_error: Optional[str]
    retry_count: int
```

### 8.5 Loop-Kette

**Die Loop-Kette ist DYNAMISCH. Sie entsteht durch den PLAN → EXECUTE → EVALUATE → RE-PLAN Zyklus.**

Questor bekommt KEINE fertige Loop-Kette. Er bekommt einen **Rahmen** (Routing-Graph + QuestorSpec) und baut die Kette **iterativ**.

```
ZYKLUS 1:
  PLANNING:   QuestCompass wählt Loop "grob_sweep_v1"
  EXECUTING:  Loop wird ausgeführt
  EVALUATING: Ergebnis: Konfidenz 0.7 (< threshold 0.9)
  ENTSCHEIDUNG: RE-PLANUNG nötig

ZYKLUS 2:
  PLANNING:   QuestCompass wählt Loop "fein_sweep_v1"
  EXECUTING:  Loop wird ausgeführt
  EVALUATING: Ergebnis: Konfidenz 0.93 (>= threshold 0.9)
  ENTSCHEIDUNG: ZIEL ERREICHT → FINALIZING
```

**Regeln:**
- Keine Verschachtelung von Loops. Nur sequentielle Kette.
- Die Kette wird im ExpeditionLedger protokolliert.
- Im Ergebnis (`routing_checkpoint`) steht, welche Loops ausgeführt wurden.

### 8.6 Terminierung

| Bedingung | Ergebnis |
|---|---|
| ALL_STEPS_COMPLETED | Loop = COMPLETED |
| MAX_ITERATIONS_REACHED | Loop = COMPLETED (Teil-Ergebnis) |
| PROCESS_COMPLETED | Loop = COMPLETED |
| PROCESS_ABORTED | Loop = ABORTED |
| STEP_FAILED | Loop = FAILED |
| BUDGET_EXHAUSTED | Loop = ABORTED |
| ESTOP_RECEIVED | Loop = ABORTED (SAFETY) |
| LEASE_EXPIRED | Loop = ABORTED (OPERATIONAL) |

### 8.7 Fehlerbehandlung

| on_step_failure | Verhalten |
|---|---|
| ABORT_LOOP | Loop wird sofort abgebrochen |
| SKIP_STEP | Step wird übersprungen (nur wenn nicht kritisch) |
| RETRY_STEP | Step wird wiederholt (bis max_step_retries) |

---

## 9. Der Routing-Graph als Constraint-Framework

**Der Routing-Graph ist KEIN fester Ausführungsplan. Er ist das SPIELFELD, auf dem Questor plant.**

| Aspekt | Rolle |
|---|---|
| `nodes` | Verfügbare Slots/Geräte — Questor darf nur diese nutzen |
| `edges` | Erlaubte Übergänge — Questor darf nur zwischen verbundenen Nodes wechseln |
| `max_loop_iterations` | Budget-Grenze — maximale Anzahl Planungszyklen |
| `branch_condition_timeout` | Sicherheits-Timeout — maximale Wartezeit auf eine Entscheidung |

**Im Ergebnis (`routing_checkpoint`) steht der EXECUTION TRACE:**

```yaml
routing_checkpoint:
  letzter_node: "sensor-01"
  iterationen: 2
  max_iterationen: 3
  ausgefuehrte_loops:
    - "grob_sweep_v1 (Iteration 1)"
    - "fein_sweep_v1 (Iteration 2)"
```

---

## 10. Der Template-Lebenszyklus

### 10.1 Wer erstellt Templates?

```
STUFE 4: VORDENKER
  → Generiert Idee MIT groben Prozessschritten (prozess_skizze)
  → Das ist KEIN Template, nur eine SKIZZE

STUFE 6: QUARTIERMEISTER
  → Prüft: Gibt es ein passendes Template in der Registry?
  → JA: Template referenzieren
  → NEIN: Template-Antrag stellen → Paket wird ZURÜCKGESTELLT

DOMAIN-EXPERTE / SYSTEM-INTEGRATOR
  → Erstellt Template als YAML-Datei
  → Registriert in data/questor_templates/
  → Version 1.0
```

### 10.2 Speicherung

```
data/questor_templates/
  ├── chemie/
  │   ├── optimize_loop_v1.yaml
  │   ├── validate_loop_v1.yaml
  │   └── diagnostic_loop_v1.yaml
  ├── biologie/
  │   ├── incubation_loop_v1.yaml
  │   └── diagnostic_loop_v1.yaml
  ├── ml/
  │   ├── hyperparameter_sweep_v1.yaml
  │   └── training_loop_v1.yaml
  └── physik/
      ├── measurement_loop_v1.yaml
      └── calibration_loop_v1.yaml
```

### 10.3 Laden

Templates werden **einmalig beim Start** aus `IDLE` geladen. Keine Laufzeit-Registrierung.

### 10.4 Versionierung

- `template_version` ist semantisch (Major.Minor)
- Major-Änderung = inkompatibel
- Minor-Änderung = kompatibel
- Alte Versionen werden im Gremium (Archiv) verwaltet
- QuestorSpec referenziert `template_id` → neueste kompatible Version
- QuestorSpec referenziert `template_id:version` → exakte Version

### 10.5 Template-Korrektur

```
STUFE A: QUESTOR DOKUMENTIERT
  → template_feedback in questor_metadata

STUFE B: ARCHIVAR PROTOKOLLIERT (operational)
  → operational_event_log
  → KEINE wissenschaftliche Interpretation

STUFE C: DOMAIN-EXPERTE WERTET AUS UND ENTSCHEIDET
  → KORRIGIEREN → Neue Template-Version
  → PARAMETER ANPASSEN → Kosten/Timeouts korrigieren
  → VERWERFEN → Template als deprecated markieren
  → BESTÄTIGEN → Keine Aktion

KANZLER: Erhält nur periodische ZUSAMMENFASSUNG (keine Details)
```

---

## 11. template_feedback

### 11.1 Struktur

```yaml
template_feedback:
  template_id: str
  template_version: str
  feedback_typ: FEHLER | UNERWARTETE_WERTE | ERFOLG | BUDGET_ABWEICHUNG | CLARITY_ISSUE | ITERATION_EXCESS
  begruendung: str                      # Detaillierte Begründung
  betroffener_step: Optional[str]
  beobachtete_werte: Optional[dict]
  erwartete_werte: Optional[dict]
  verbesserungsvorschlag: list[str]
  auswirkung_auf_package: Optional[str]
  schwergrad: KRITISCH | MITTEL | NIEDRIG
```

### 11.2 Trigger-Punkte

| Trigger | Bedingung | Schweregrad |
|---|---|---|
| BUDGET-ABWEICHUNG | actual_cost > estimated_cost × 1.5 | MITTEL |
| CLARITY-SCORE ZU NIEDRIG | clarity_score < clarity_threshold | MITTEL |
| TEMPLATE-FEHLER | Ein LoopStep schlägt fehl | KRITISCH |
| UNERWARTETE WERTE | Messwerte außerhalb erwarteter Bereich | MITTEL |
| ZU VIELE ITERATIONEN | iterationen > expected × 2 | NIEDRIG |
| PARAMETER-BOUNDS | < 10% oder > 90% des möglichen Bereichs | NIEDRIG |

### 11.3 Kein LLM für template_feedback

template_feedback wird DETERMINISTISCH erzeugt. Kein LLM wird benötigt.

---

## 12. Autonomy-Level und sein Einfluss

### 12.1 Definition

`autonomy_level` existiert bereits im QuestorSpec (`STRICT | GUIDED | ADAPTIVE`). Er beeinflusst DREI Bereiche:

1. **PLANUNGSFREIHEIT:** Wie frei darf QuestCompass planen?
2. **LOOP-AUSWAHL:** Wie viele Kandidaten darf die LLM sehen?
3. **RE-PLANUNGSFREIHEIT:** Wie frei darf QuestCompass nachplanen?

### 12.2 Wirkungstabelle

| Aspekt | STRICT | GUIDED | ADAPTIVE |
|---|---|---|---|
| candidate_window | 1 | 3 | 5 |
| LLM-Beratung | NEIN | Bei Score-Diff < 0.15 | Immer erlaubt |
| Re-Planung | Nur innerhalb bounds | Kleine Anpassungen | Größere Anpassungen |
| Objective-Vervollständigung | NEIN | JA | JA |
| FRACTURE_DIAGNOSIS Override | Immer STRICT | Immer STRICT | Immer STRICT |

### 12.3 Wer setzt das Autonomy-Level?

Der **Quartiermeister** setzt `autonomy_level` im QuestorSpec basierend auf:
- Aufgabe (Diagnose → STRICT, Optimierung → GUIDED/ADAPTIVE)
- Zone-Health (QUARANTÄNE → STRICT)
- Bisherige Erfahrungen (nach vielen Tests → Level anpassen)

Das Gremium kann das Level pro Aufgabe anpassen und über die Zeit verbessern.

---

## 13. Die drei fundamentalen Verhaltensregeln

### Regel 1: FAIL-CLOSED

Wenn irgendetwas unklar, ungültig oder unsicher ist → keine Ausführung, kontrollierter Abbruch.

### Regel 2: DETERMINISTIC-FIRST

LLM darf beraten, aber niemals final entscheiden. QuestCompass entscheidet final deterministisch.

### Regel 3: TOTALFUNKTION

Questor liefert IMMER ein Ergebnis. Auch bei Early-Abort. Auch bei Crash.

---

## 14. Budget-Logik

### 14.1 Grundsatz

**Das Ziel ist NICHT, das Budget auszugeben, sondern das Ziel zu erreichen.**

Budget ist eine Obergrenze, kein Ziel. Questor bricht ab, wenn das Ziel unerreichbar ist — auch wenn noch Budget übrig ist.

### 14.2 Budget-Grenzen

| Budget | Quelle | Wirkung |
|---|---|---|
| `max_loop_iterations` | `routing_graph` | Max. Anzahl Planungszyklen |
| `max_duration_s` | `QuestorSpec.budget` | Max. Gesamtzeit |
| `max_retry_count` | `QuestorSpec.budget` | Max. Retries |
| `max_llm_calls` | `QuestorSpec.budget` | Max. LLM-Aufrufe |
| `max_energy_budget` | `QuestorSpec.budget` | Max. Energie |

### 14.3 Kostenmodell

```yaml
StepCost:
    time_cost_s: float
    reagent_cost: float          # Normiert 0.0–1.0
    compute_cost: float          # Normiert 0.0–1.0
    energy_cost: float
```

Kosten werden vom Domain-Experten im Template geschätzt und nach der Ausführung im `operational_metrics` dokumentiert. Die Aggregation pro Zone/Dimension erfolgt im **Kartograph** (Gremium).

---

## 15. Recovery (NUR WAL)

### 15.1 Grundsatz

**Recovery erfolgt NUR aus dem WAL (Write-Ahead Log). Keine Blackbox-Recovery.**

### 15.2 Recovery-Ablauf

```
1. Questor startet neu nach Crash
2. Questor liest den WAL (data/wal/)
   → Letzter valider Zustand wird rekonstruiert
   → ExpeditionLedger wird wiederhergestellt
   → Aktueller Loop-Schritt wird identifiziert
3. Questor ruft reconcile_process_state() auf
   → HAL prüft physischen Zustand
4. QuestCompass entscheidet: FORTSETZEN oder ABBRECHEN
5. Questor setzt am letzten Punkt an
```

### 15.3 Recovery-Entscheidung

| Bedingung | Entscheidung |
|---|---|
| Prozess in SAFE_HOLD + Zustand sicher + Resume-Token gültig | FORTSETZEN (RESUME) |
| Prozess in SAFE_HOLD + Zustand unsicher | ABBRECHEN (RECOVERY_UNSAFE) |
| Prozess in UNKNOWN | ABBRECHEN (RECOVERY_UNSAFE) |
| ESTOP aktiv | ABBRECHEN (SAFETY) |
| Kein Resume-Token | ABBRECHEN (RESUME_TOKEN_INVALID) |

---

## 16. SAFE_HOLD und WAITING_FOR_RELEASE

### 16.1 SAFE_HOLD

**Wann:** Lease-Expiry bei Langzeit-Prozess mit `on_lease_expiry_policy: SAFE_HOLD`.

**Questor-Verhalten:**
1. QuestCompass wechselt in Zustand SAFE_HOLD
2. Keine neuen HAL-Kommandos
3. Questor wartet auf Recovery
4. Nach Recovery: RESUME oder ABBRUCH

### 16.2 WAITING_FOR_RELEASE

**Wann:** Stufe abgeschlossen, nächste Stufe braucht manuelle Freigabe (`release_required: true`).

**Questor-Verhalten:**
1. Questor wechselt in Zustand WAITING_FOR_RELEASE
2. Questor wartet auf Antwort vom HAL
3. Wartezeit kann mehrere Tage betragen
4. Bei Freigabe: RELEASE_STAGE senden → EXECUTING
5. Bei Verweigerung: FINALIZING (STAGE_RELEASE_DENIED)
6. Bei Timeout: FINALIZING (max_wait_time_s erreicht)

---

## 17. atlas_version_ref — Pass-Through

`atlas_version_ref` ist ein **reiner Pass-Through-String**.

```
Questor empfängt:  package.atlas_version_ref = "atlas-v042"
Questor setzt:     observed_atlas_version_id = "atlas-v042"

Questor darf NICHT:
  ✗ atlas_version_ref interpretieren
  ✗ atlas_version_ref ändern
  ✗ atlas_version_ref einem LLM-Advisor übergeben
  ✗ atlas_version_ref in einen Prompt einbauen
  ✗ atlas_version_ref in template_feedback verwenden
```

---

## 18. planning_hints (optionales Feld)

```yaml
planning_hints:
  preferred_strategy: "coarse_to_fine"
  initial_parameters:
    temperatur: 40.0
    druck: 1.0
  priority_parameters:
    - "temperatur"
  known_constraints:
    - "Temperatur über 80°C vermeiden"
  expected_optimum_region:
    temperatur: (38.0, 45.0)
```

**Regeln:**
- Optional — Questor muss auch ohne sie planen können
- Nicht bindend — QuestCompass darf sie ignorieren
- Keine Sicherheitsrelevanz — Sicherheitsregeln kommen aus `gefahen_mitigationen`
- Domänenunabhängig

---

## 19. Datenübergabe an Questor

### 19.1 Pflichtfelder

| Feld | Zweck |
|---|---|
| `ziel` | Was soll erreicht werden? |
| `parameter_bounds` | Erlaubte Parameterbereiche |
| `routing_graph` | Verfügbare Nodes/Edges, Constraints |
| `questor_spec` | Capabilities, Templates, Budget, LLM-Policy |
| `materials_or_resources` | Verfügbare Materialien/Geräte |
| `limits` | Max. Dauer, Energie |
| `gate_record_ref` | Sicherheitsfreigabe |
| `lease_grants` | Ressourcen-Zugriff |
| `security_mode` | NORMAL / SANDBOX / etc. |

### 19.2 Optionale Felder

| Feld | Zweck |
|---|---|
| `kontext.beschreibung` | Domänenbeschreibung |
| `kontext.domaene` | Domäne (chemie, biologie, ml, physik) |
| `domain_metadata` | Domänenspezifische Daten |
| `gefahen_mitigationen` | Sicherheitsmaßnahmen |
| `planning_hints` | Planungshinweise |
| `atlas_version_ref` | Pass-Through (kein LLM-Zugriff) |

### 19.3 Was Questor NICHT bekommt

| Daten | Warum nicht |
|---|---|
| Atlas-Signal-Stacks | Questor darf keine globalen Signale lesen |
| Archiv-Einträge | Questor darf kein Archiv lesen |
| Andere Paketinhalte | Questor ist paketgebunden |
| Blackbox-Inhalte anderer Pakete | Isolation |

---

## 20. Sicherheitsregeln (Zusammenfassung)

| Regel | Quelle |
|---|---|
| Keine physische Ausführung ohne Envelope | Hauptreferenz |
| Keine physische Ausführung ohne Gate | Hauptreferenz |
| Keine physische Ausführung ohne Lease | Hauptreferenz |
| LLM nur Advisor, niemals final | Questor v0.2.3 |
| Questor schreibt nicht in Atlas/Archiv | Hauptreferenz |
| Questor setzt ESTOP nicht zurück | Hauptreferenz |
| Questor vergibt keine Leases | Hauptreferenz |
| Blackbox bleibt lokal | Hauptreferenz |
| Operational ≠ Scientific | Hauptreferenz |
| ESTOP ≠ LEASE_DENIED | Hauptreferenz |
| Fail-Closed bei Unklarheit | Questor v0.2.3 |
| NaN/Infinity → Fail-Closed | C18 |
| atlas_version_ref ist Pass-Through | Diese Datei |

---

## 21. Abdeckung der 5 Szenarien

| Szenario | Pfad | Zyklen |
|---|---|---|
| **S1: Happy Path** | IDLE → RECEIVING → VALIDATING → PLANNING → EXECUTING → EVALUATING → FINALIZING → DONE | 1 Zyklus |
| **S2: ESTOP** | IDLE → ... → EXECUTING → FINALIZING(SAFETY) → DONE | 0 Zyklen |
| **S3: Seher-Veto** | Questor nicht beteiligt | — |
| **S4: Langzeit 72h** | IDLE → ... → EXECUTING → SAFE_HOLD → RECOVERING → EXECUTING → WAITING_FOR_RELEASE → EXECUTING → EVALUATING → FINALIZING → DONE | 1 Zyklus |
| **S5: Fracture** | IDLE → ... → PLANNING(FRACTURE_DIAGNOSIS) → EXECUTING → EVALUATING → FINALIZING → DONE | 1 Zyklus |

---

## 22. Noch offene Themen (für spätere Erweiterungen)

| # | Thema | Status |
|---|---|---|
| 1 | ExpeditionLedger — Format, Operationen, Genesis-Hash | ❌ Offen |
| 2 | HAL-Bridge — Wie werden Loops in HALCommands übersetzt? | ❌ Offen |
| 3 | Result-Builder — Wie wird das questor_ergebnis_paket gebaut? | ❌ Offen |
| 4 | Blackbox-Archiver — Format, Rotation, Retention | ❌ Offen |
| 5 | Sequence-Manager — Atomarität, Persistenz | ❌ Offen |
| 6 | Trail-Map — Struktur, Erzeugung | ❌ Offen |
| 7 | Sanitization — Vollständige Regeln | ❌ Offen |
| 8 | Questor-Facade — Transportmedium | ❌ Offen |
| 9 | Capability-Registry — Formale Definition | ❌ Offen |
| 10 | Questor-Health-Monitoring | ❌ Offen |
| 11 | Questor-Graceful-Shutdown | ❌ Offen |
| 12 | Questor und security_mode-Verhalten | ❌ Offen |

---

## Appendix A: Gremium-Auslagerungen (Erinnerungen)

Die folgenden Punkte wurden ans Gremium ausgelagert und müssen dort in späteren Schritten eingebaut werden:

| # | Thema | Gremium-Komponente | Status |
|---|---|---|---|
| **G-1** | Template-Erstellung bei fehlendem Template | Quartiermeister + Domain-Experte | ✅ Definiert |
| **G-2** | Template-Korrektur nach Questor-Feedback | Domain-Experte (NICHT Kanzler) | ✅ Definiert |
| **G-3** | Template-Versionierung (alte Versionen im Archiv) | Archivar | ✅ Definiert |
| **G-4** | Ressourcen-Karte (Verbrauch pro Zone/Dimension) | Kartograph | ✅ Definiert |
| **G-5** | Vordenker liefert `prozess_skizze` mit Idee | Vordenker | ✅ Definiert |
| **G-6** | `template_feedback` operational protokollieren | Archivar | ✅ Definiert |
| **G-7** | Kosten-Schätzungen für Reagenzien bereitstellen | System-Integrator / Konfiguration | ✅ Definiert |
| **G-8** | Kanzler erhält periodische Template-Zusammenfassung | Kanzler (nur Übersicht) | 🟡 Neu |
| **G-9** | Quartiermeister berücksichtigt `template_feedback` beim Package-Bau | Quartiermeister | 🟡 Neu |
| **G-10** | `atlas_version_ref` ist Pass-Through, kein LLM-Zugriff | Questor (intern) | 🟡 Neu |
| **G-11** | `loop_selection_weights` optional im QuestorSpec | Quartiermeister | 🟡 Neu |
| **G-12** | `planning_hints` als optionales Feld im ResearchPackage | Quartiermeister | 🟡 Neu |

---

## Appendix B: Zusammenfassung der Architektur-Entscheidungen

| Entscheidung | Ergebnis |
|---|---|
| Questor verarbeitet ein Paket | Sequentiell, keine Nebenläufigkeit |
| LLM-Backend | Ollama/gemma4:31b-cloud (abstrahiert) |
| Loop-Kette | Dynamisch, entsteht durch Feedback-Schleife |
| Routing-Graph | Constraint-Framework, kein fester Plan |
| Templates | Dateien in `data/questor_templates/` |
| Template-Laden | Einmalig beim Start aus IDLE |
| Template-Verschachtelung | NEIN, nur sequentielle Kette |
| Template-Erstellung | Domain-Experte / System-Integrator |
| Template-Korrektur | Questor → Archivar → Domain-Experte |
| Kanzler und Templates | Nur periodische Zusammenfassung |
| Budget-Logik | Ziel erreichen, nicht Budget ausgeben |
| Kostenmodell | Zeit + Reagenzien + Compute (vereinfacht) |
| Gesamtkosten statt Einzelkosten | Ja, verhindert Kosten-Falle |
| Recovery | NUR WAL, keine Blackbox-Recovery |
| SAFE_HOLD | Questor wartet, dann RESUME oder ABBRUCH |
| WAITING_FOR_RELEASE | Questor wartet bis HAL antwortet (kann Tage dauern) |
| FRACTURE_DIAGNOSIS | Immer STRICT, kein LLM, max 1 Iteration |
| atlas_version_ref | Pass-Through, kein LLM-Zugriff |
| QuestCompass | Deterministic-first, LLM nur Advisor |
| PolicyEvaluator | Gatekeeper mit Occam's Razor |
| Autonomy-Level | Steuert candidate_window und LLM-Nutzung |
| Objective-Vervollständigung | LLM darf umschreiben, QuestCompass entscheidet |
