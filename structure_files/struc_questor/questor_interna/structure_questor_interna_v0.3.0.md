# 🧭 STRUCTURE_QUESTOR_INTERNA_V0.3.0

---

```
🧭 MYRMEX V2.4.0 + QUESTOR V0.2.3 — QUESTOR-INTERNA GESAMTSPEZIFIKATION
Dateiname:       structure_questor_interna_v0.3.0.md
Version:         0.3.0
System:          MYRMEX v2.4.0 + Questor v0.2.3
Status:          Arbeitsstand — Architektur-Diskussion, keine Implementierungsfreigabe
Bezug:           structure_standalone_v2.4.0.md v1.1.1 (kanonisch)
                 structure_hal_v0.2.0.md
                 structure_standalone_questcompass_v0.1.0.md
                 structure_standalone_hal_bridge_exp_ledger_v0.1.0.md
Sprache:         Deutsch
Modus:           Dry-Run / Spezifikation
```

---

## 0. Dokumentenhierarchie und Geltung

```
1. structure_standalone_v2.4.0.md v1.1.1                ← kanonisch
2. structure_hal_v0.2.0.md                               ← HAL-Vertrag
3. diese Datei: structure_questor_interna_v0.3.0.md      ← Questor-Interna GESAMT
4. structure_standalone_questor_v0.2.3.md                 ← unterstützend
```

Bei Widersprüchen gilt die kanonische Hauptreferenz.

Diese Datei **ersetzt** die folgenden Einzel-Dokumente:
- `structure_standalone_questcompass_v0.1.0.md`
- `structure_standalone_hal_bridge_exp_ledger_v0.1.0.md`

---

## 1. Zweck dieser Datei

Diese Datei definiert die **vollständigen internen Mechanismen** von Questor:

| Teil | Thema |
|---|---|
| Teil A | Questor-Zustandsmaschine |
| Teil B | QuestCompass-Algorithmus |
| Teil C | Loop-Architektur |
| Teil D | Template-Lebenszyklus |
| Teil E | HAL-Bridge |
| Teil F | ExpeditionLedger + WAL |
| Teil G | Result-Builder |
| Teil H | Questor-Facade (Queue-Architektur) |
| Teil I | Sicherheitsregeln |
| Teil J | Gremium-Auslagerungen |

---

## 2. Grundannahmen

| Annahme | Wert |
|---|---|
| Nebenläufigkeit | Questor verarbeitet **immer nur EIN Paket** sequentiell |
| LLM-Backend | Ollama mit `gemma4:31b-cloud` (abstrahiert, wechselbar) |
| Questor ist Totalfunktion | Jedes Paket → genau ein Ergebnis, auch bei Early-Abort |
| Questor schreibt nie in Atlas/Archiv | In allen Szenarien bestätigt |
| Questor setzt ESTOP nie zurück | Explizit verboten |
| Questor vergibt keine Leases | Leases kommen vom Resource Governor |
| Recovery-Mechanismus | **NUR WAL** (Write-Ahead Log), keine Blackbox-Recovery |
| Kosten-Tracking | Vereinfacht: Zeit + Reagenzien + Compute (normiert) |
| Kostenberechnung | Erst bei COMPLETED/ABORTED final berechnen |
| Ledger-Verschlüsselung | Keine (kein Mehrwert) |
| WAL-Lebenszyklus | Nur während aktiver Ausführung, nach DONE bereinigt |
| Questor-Prozess | Eigener Prozess, losgelöst vom Gremium |
| Transportmedium | Dateibasierte Queue (`data/questor_queue/`) |

---

# TEIL A: QUESTOR-ZUSTANDSMASCHINE

---

## 3. Die sechs Lebensphasen

```
PHASE 1: EMPFANG      → Envelope empfangen, formal prüfen
PHASE 2: VALIDIERUNG  → Paket-Inhalt prüfen
PHASE 3: PLANUNGS- & AUSFÜHRUNGSZYKLUS → QuestCompass-Loop
PHASE 4: AUSFÜHRUNG   → HAL-Bridge sendet Kommandos
PHASE 5: ERGEBNISBAU  → Result-Builder baut questor_ergebnis_paket
PHASE 6: BLACKBOX     → Lokale Blackbox schreiben
```

## 4. Zustände

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

## 5. Zustandsdiagramm

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

## 6. Übergangstabelle

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

## 7. Invarianten

- Questor ist immer in genau EINEM Zustand.
- `FINALIZING` erzeugt IMMER ein vollständiges `questor_ergebnis_paket`.
- `DONE` → `IDLE` ist der einzige Rückkehrpfad.
- `EXECUTING` ist der einzige Zustand, in dem HAL-Kommandos gesendet werden.
- `WAITING_FOR_RELEASE` und `SAFE_HOLD` sind Wartezustände ohne aktive HAL-Kommandos.
- `RECOVERING` darf keine neuen HAL-Kommandos senden, nur `reconcile_*` aufrufen.
- `FINALIZING` darf keine HAL-Kommandos senden.

## 8. Die drei fundamentalen Verhaltensregeln

| Regel | Bedeutung |
|---|---|
| **FAIL-CLOSED** | Wenn irgendetwas unklar, ungültig oder unsicher ist → keine Ausführung, kontrollierter Abbruch |
| **DETERMINISTIC-FIRST** | LLM darf beraten, aber niemals final entscheiden. QuestCompass entscheidet final deterministisch |
| **TOTALFUNKTION** | Questor liefert IMMER ein Ergebnis. Auch bei Early-Abort. Auch bei Crash |

---

# TEIL B: QUESTCOMPASS-ALGORITHMUS

---

## 9. QuestCompass im Gesamtsystem

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

## 10. Logische Rollen

| Logische Rolle | Implementiert in | Verantwortung |
|---|---|---|
| **Hypothesis Architect** | QuestCompass | Formuliert den nächsten Loop, plant die Ausführung |
| **Gatekeeper (Red Teamer)** | PolicyEvaluator | Prüft: Ist der Loop sicher? Nötig? Einfach genug? |
| **Machine Planner** | LoopRegistry + HAL-Bridge | Übersetzt den Loop in HAL-Kommandos |
| **Semantic Safety Agent** | SafetyMonitor | Überwacht die Ausführung auf Sicherheitsverletzungen |

**Keine separaten Agenten-Prozesse. Alles innerhalb der Questor-Zustandsmaschine.**

## 11. Objective Analysis (Ziel-Analyse)

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

**Clarity-Score-Berechnung:**

| Bedingung | clarity_score |
|---|---|
| objective_type explizit + parameter_bounds + ziel > 10 Zeichen | 1.0 |
| objective_type durch Keyword-Matching + parameter_bounds | 0.7 |
| objective_type nur durch LLM ODER parameter_bounds sehr weit | 0.4 |
| objective_type unklar ODER parameter_bounds fehlen | 0.1 |

**Fail-Closed-Regel:** Wenn `clarity_score < clarity_threshold` → keine physische Ausführung.

## 12. Loop Selection (Loop-Auswahl)

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

## 13. Hypothesis Formulation

**Deterministisch aus der Objective und den Parametern abgeleitet. Kein LLM.**

| objective_type | Hypothese-Format |
|---|---|
| OPTIMIZE | „Bei {parameter} = {wert} erwarte ich eine {metrik} im Bereich [{min}, {max}]." |
| EXPLORE | „Die Variation von {parameter} zwischen {min} und {max} liefert neue Datenpunkte." |
| VALIDATE | „Die Messung bei {parameter} = {wert} sollte den Kristallwert {expected} bestätigen oder widerlegen." |
| DIAGNOSE | „Die Messung bei {parameter} = {wert} sollte die Inkonsistenz bestätigen oder widerlegen." |

## 14. Evaluation (Ergebnisbewertung)

| objective_type | Bewertungskriterium | ZIEL ERREICHT wenn |
|---|---|---|
| OPTIMIZE | Konfidenz = 1.0 − (varianz / bereich) | konfidenz ≥ clarity_threshold |
| EXPLORE | Abdeckung des Parameterraums | abdeckung ≥ 0.8 |
| VALIDATE | Abweichung = \|gemessen − erwartet\| / erwartet | Immer (Bestätigung ODER Widerlegung) |
| DIAGNOSE | Inkonsistenz = \|gemessen − atlas_erwartung\| | Immer (Bestätigung ODER Widerlegung) |
| SIMULATE_ONLY | Simulation abgeschlossen? | JA |
| CLARIFY | Objective wurde präzisiert? | JA |

## 15. Decision Engine (Entscheidungslogik)

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

## 16. LLM-Advisor-Integration

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

## 17. PolicyEvaluator (Gatekeeper)

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

## 18. Autonomy-Level

| Aspekt | STRICT | GUIDED | ADAPTIVE |
|---|---|---|---|
| candidate_window | 1 | 3 | 5 |
| LLM-Beratung | NEIN | Bei Score-Diff < 0.15 | Immer erlaubt |
| Re-Planung | Nur innerhalb bounds | Kleine Anpassungen | Größere Anpassungen |
| Objective-Vervollständigung | NEIN | JA | JA |
| FRACTURE_DIAGNOSIS Override | Immer STRICT | Immer STRICT | Immer STRICT |

---

# TEIL C: LOOP-ARCHITEKTUR

---

## 19. Die drei Ebenen

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

## 20. LoopTemplate — Formale Definition

```yaml
LoopTemplate:
    template_id: str
    template_version: str               # Semantisch (Major.Minor)
    schema_version: str
    domain: str                         # chemie, biologie, ml, physik
    created_by: str
    created_at: str
    last_modified: str

    objective_types: list[ObjectiveType]
    description: str

    required_capabilities: list[str]
    required_slot_count: int
    requires_physical_actuation: bool
    requires_long_running_process: bool

    steps: list[LoopStep]
    max_internal_iterations: int

    parameter_schema: dict[str, ParameterDefinition]
    termination_conditions: list[TerminationCondition]

    on_step_failure: ABORT_LOOP | SKIP_STEP | RETRY_STEP
    max_step_retries: int

    estimated_cost:
        total_time_s: float
        total_reagent_cost: float       # Normiert 0.0–1.0
        total_compute_cost: float
        total_energy_cost: float
```

## 21. LoopStep

```yaml
LoopStep:
    step_id: str
    step_type: HAL_COMMAND | PROCESS_COMMAND | MEASURE | WAIT | EVALUATE
    capability: Optional[str]
    operation: Optional[str]
    process_mode: Optional[str]
    parameters: dict[str, Any]
    depends_on: list[str]
    branch_condition: Optional[BranchCondition]
    on_true_next: Optional[str]
    on_false_next: Optional[str]
    timeout_s: float
    parameter_schema_ref: Optional[str]
    parameter_schema_version: Optional[str]
    payload_artifact_ref: Optional[str]
    process_recipe_ref: Optional[str]
    process_recipe_checksum: Optional[str]
    cost:
        time_cost_s: float
        reagent_cost: float
        compute_cost: float
        energy_cost: float
```

## 22. Loop-Kette — Dynamisch

**Die Loop-Kette ist DYNAMISCH. Sie entsteht durch den PLAN → EXECUTE → EVALUATE → RE-PLAN Zyklus.**

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

## 23. Terminierung

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

## 24. Der Routing-Graph als Constraint-Framework

| Aspekt | Rolle |
|---|---|
| `nodes` | Verfügbare Slots/Geräte — Questor darf nur diese nutzen |
| `edges` | Erlaubte Übergänge — Questor darf nur zwischen verbundenen Nodes wechseln |
| `max_loop_iterations` | Budget-Grenze — maximale Anzahl Planungszyklen |
| `branch_condition_timeout` | Sicherheits-Timeout — maximale Wartezeit auf eine Entscheidung |

---

# TEIL D: TEMPLATE-LEBENSZYKLUS

---

## 25. Wer erstellt Templates?

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

## 26. Speicherung

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

## 27. Laden und Versionierung

- Templates werden **einmalig beim Start** aus `IDLE` geladen. Keine Laufzeit-Registrierung.
- `template_version` ist semantisch (Major.Minor).
- Major-Änderung = inkompatibel. Minor-Änderung = kompatibel.
- Alte Versionen werden im Gremium (Archiv) verwaltet.

## 28. Template-Korrektur

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

## 29. template_feedback — Trigger-Punkte

| Trigger | Bedingung | Schweregrad |
|---|---|---|
| BUDGET-ABWEICHUNG | actual_cost > estimated_cost × 1.5 | MITTEL |
| CLARITY-SCORE ZU NIEDRIG | clarity_score < clarity_threshold | MITTEL |
| TEMPLATE-FEHLER | Ein LoopStep schlägt fehl | KRITISCH |
| UNERWARTETE WERTE | Messwerte außerhalb erwarteter Bereich | MITTEL |
| ZU VIELE ITERATIONEN | iterationen > expected × 2 | NIEDRIG |
| PARAMETER-BOUNDS | < 10% oder > 90% des möglichen Bereichs | NIEDRIG |

---

# TEIL E: HAL-BRIDGE

---

## 30. Rolle und Position

```
QUESTOR (Schicht 2)                          HAL (Schicht 1)
┌────────────────────────┐                   ┌────────────────────────┐
│  QuestCompass          │                   │  HAL Interface         │
│    │                   │                   │    │                   │
│    ▼                   │                   │    ▼                   │
│  PolicyEvaluator       │                   │  Lease Validation      │
│    │                   │                   │    │                   │
│    ▼                   │                   │    ▼                   │
│  ┌──────────────┐      │                   │  ┌──────────────┐     │
│  │  HAL-BRIDGE  │──────┼──── HALCommand ──┼─►│ execute_cmd  │     │
│  │              │──────┼── ProcessCommand ─┼─►│ start_proc   │     │
│  │              │◄─────┼── HALCmdResult ──┼──│              │     │
│  │              │◄─────┼── ProcessResult ──┼──│              │     │
│  └──────────────┘      │                   │  └──────────────┘     │
└────────────────────────┘                   └────────────────────────┘
```

## 31. Was die HAL-Bridge DARF und NICHT DARF

**DARF:**

| Erlaubt | Begründung |
|---|---|
| LoopSteps in HALCommand/ProcessCommand übersetzen | Kernaufgabe |
| HALCommand/ProcessCommand an HAL senden | Einziger Weg zur Hardware |
| HALCommandResult/ProcessResult empfangen und verarbeiten | Ergebnisverarbeitung |
| Slot-/Prozess-Zustände abfragen | Zustandsprüfung |
| ESTOP-Zustand abfragen | Sicherheitsprüfung |
| Reconciliation anstoßen | Recovery |
| Kosten aktualisieren | Budget-Tracking |
| Idempotenz sicherstellen | Crash-Sicherheit |

**NICHT DARF:**

| Verboten | Begründung |
|---|---|
| Leases vergeben oder verlängern | Nur Resource Governor |
| ESTOP zurücksetzen | Nur autorisierter Sicherheitsprozess |
| Wissenschaftliche Ziele in HALCommand.parameters schreiben | HAL ist nicht wissenschaftlich |
| Atlas-Signale in HALCommand.parameters schreiben | Questor schreibt nicht in Atlas |
| Zone-Locks eigenmächtig vergeben | Nur Resource Governor |
| HAL-Kommandos ohne gültige Lease senden | Fail-Closed |
| Sicherheitsentscheidungen treffen | Nur PolicyEvaluator/QuestCompass |
| Heartbeats senden | Heartbeats gehen direkt an Resource Governor |

## 32. Übersetzungslogik

```
LoopStep.step_type == HAL_COMMAND oder MEASURE
  → HALCommand erzeugen

LoopStep.step_type == PROCESS_COMMAND
  → ProcessCommand erzeugen

LoopStep.step_type == WAIT
  → Kein HAL-Kommando (Questor wartet intern)

LoopStep.step_type == EVALUATE
  → Kein HAL-Kommando (QuestCompass evaluiert intern)
```

## 33. Deterministische ID-Erzeugung

```python
command_id  = f"cmd-{package_id}-{step_id}-{attempt_id}"
process_id  = f"proc-{package_id}-{step_id}-{attempt_id}"

hal_idempotency_key        = command_id:lease_ref:slot_id
hal_process_idempotency_key = process_id:lease_ref:slot_id
```

## 34. Ergebnisverarbeitung

| HAL-Status | BridgeResult.status | error_class | Questor-Aktion |
|---|---|---|---|
| SUCCESS | SUCCESS | — | Weiter im Loop |
| DUPLICATE_BLOCKED | SUCCESS | — | Weiter (bereits ausgeführt) |
| DENIED | OPERATIONAL_ABORT | OPERATIONAL | QuestCompass entscheidet |
| TIMEOUT | OPERATIONAL_ABORT | OPERATIONAL | Retry oder Abbruch |
| ESTOP | SAFETY_ABORT | SAFETY | Sofortiger Abbruch |
| INTERLOCK | SAFETY_ABORT | SAFETY | Sofortiger Abbruch |
| ERROR | OPERATIONAL_ABORT | OPERATIONAL | QuestCompass entscheidet |
| LEASE_INVALID | OPERATIONAL_ABORT | OPERATIONAL | Abbruch |
| LEASE_EXPIRED | OPERATIONAL_ABORT | OPERATIONAL | Abbruch |
| SLOT_UNAVAILABLE | OPERATIONAL_ABORT | OPERATIONAL | QuestCompass entscheidet |
| ZONE_LOCK_UNAVAILABLE | OPERATIONAL_ABORT | OPERATIONAL | Warten oder Abbruch |

## 35. Prozess-Lebenszyklus

```
PENDING → RUNNING → COMPLETED
                  → SAFE_HOLD → RUNNING (RESUME)
                  → SAFE_HOLD → ABORTED
                  → WAITING_FOR_RELEASE → RUNNING (RELEASE_STAGE)
                  → WAITING_FOR_RELEASE → ABORTED
                  → FAULT → UNKNOWN → RUNNING | FAULT | ABORTED
                  → ABORTED
```

## 36. Trennung timeout_s vs expected_process_duration_s

```
timeout_s:                  Kommando-Timeout (RPC-Aufruf, Sekunden)
expected_process_duration_s: Prozess-Dauer (physikalisch, Sekunden bis Tage)

Diese sind STRIKT getrennt.
Beispiel: timeout_s = 60.0, expected_process_duration_s = 259200.0 (72h)
```

## 37. Kosten-Tracking

```yaml
StepCost:
    time_cost_s: float
    reagent_cost: float          # Normiert 0.0–1.0
    compute_cost: float          # Normiert 0.0–1.0
    energy_cost: float
```

- Geschätzte Kosten kommen aus dem LoopTemplate.
- Tatsächliche Kosten werden nach Ausführung berechnet.
- FINALE Kosten werden erst bei COMPLETED/ABORTED berechnet.
- `reagent_cost` bleibt normiert. Konkrete Menge in `operational_metrics`.

## 38. Parameter-Schema-Handling

| Feld | Quelle |
|---|---|
| `parameter_schema_ref` | Aus dem LoopTemplate |
| `process_recipe_ref` | Aus dem LoopTemplate |
| `payload_artifact_ref` (statisch) | Aus dem LoopTemplate |
| `payload_artifact_ref` (spezifisch) | Aus dem ResearchPackage |
| `ComputeResourceRequest` | Aus dem LoopTemplate |
| `dataset_ref`-Prüfung | HAL formal, Compute-Adapter Existenz |

---

# TEIL F: EXPEDITIONLEDGER + WAL

---

## 39. Was ist das ExpeditionLedger?

Das ExpeditionLedger ist das **Zustandsjournal** von Questor. Es dokumentiert jeden Schritt der Ausführung in einer geordneten, integritätsgesicherten Kette.

```
Eigenschaften:
  - APPEND-ONLY (keine nachträgliche Änderung)
  - Hash-Chain (jeder Eintrag ist mit dem vorherigen verlinkt)
  - Vollständig (alle Schritte, Entscheidungen, Kosten)
  - Read-only nach Paket-Abschluss
  - Dient als Nachschlagwerk für Domain-Experten
```

## 40. Ledger-Struktur

```python
ExpeditionLedger:
    ledger_id: str
    package_id: str
    zyklus_id: str
    attempt_id: int
    questor_instance_id: str

    genesis_hash: str
    genesis_timestamp: str

    state: PLANNING | EXECUTING | EVALUATING | FINALIZING | DONE | ABORTED
    current_loop_index: int
    current_step_index: int
    iteration_count: int

    entries: list[LedgerEntry]
    accumulated_cost: AccumulatedCost

    last_checkpoint: LedgerCheckpoint
    wal_position: int

    access_level: READ_WRITE | READ_ONLY
    finalized_at: Optional[str]
    archive_path: Optional[str]
```

## 41. Genesis-Hash (C15)

```python
def calculate_genesis_hash(package_id, zyklus_id, attempt_id,
                            gate_record_ref, atlas_version_ref,
                            timestamp, questor_instance_id):
    genesis_input = (
        f"{package_id}:{zyklus_id}:{attempt_id}:"
        f"{gate_record_ref}:{atlas_version_ref}:"
        f"{timestamp}:{questor_instance_id}"
    )
    return sha256(genesis_input)
```

## 42. Hash-Chain-Regel

```
Jeder Eintrag enthält:
  previous_hash = entry_hash des vorherigen Eintrags
  entry_hash = SHA256(entry_id + timestamp + entry_type + previous_hash + payload)

Der Genesis-Eintrag hat:
  previous_hash = "0000...0000" (64 Nullen)
```

## 43. NaN/Infinity-Prüfung (C18)

```
Wenn ein Payload NaN oder Infinity enthält:
  → LEDGER_SERIALIZATION_FAILED
  → Abbruch (Fail-Closed)
```

## 44. WAL (Write-Ahead Log)

```
VOR der Ausführung:
  1. WAL-Eintrag schreiben (was TUN werden)
  2. Aktion ausführen
  3. WAL-Eintrag aktualisieren (was GETAN wurde)

NACH einem Crash:
  1. WAL lesen
  2. Letzten validen Zustand finden
  3. Prüfen: Wurde die Aktion abgeschlossen?
  4. Wenn JA → weiter
  5. Wenn NEIN → reconcile oder abbrechen

SPEICHERORT: data/wal/questor/{package_id}/{zyklus_id}/
```

## 45. WAL-Lebenszyklus

```
PAKET START:
  → WAL wird erstellt

WÄHREND AUSFÜHRUNG:
  → Jeder Zustandswechsel wird in den WAL geschrieben

NACH PAKET-ABSCHLUSS (FINALIZING → DONE):
  → WAL wird NICHT mehr benötigt
  → WAL-Einträge werden bereinigt
  → Ledger wird als READ-ONLY archiviert
```

## 46. Recovery aus dem WAL

```
1. WAL lesen
2. Integrität prüfen (Hash-Chain)
   → Wenn korrupt: RECOVERY_UNSAFE
3. Letzten Checkpoint finden
   → Wenn kein Checkpoint: RECOVERY_UNSAFE
4. Zustand aus Checkpoint rekonstruieren
5. Einträge nach dem Checkpoint prüfen
6. Letzte Aktion identifizieren:
   a. Keine Aktion → RECOVERED
   b. Aktion COMMITTED → RECOVERED
   c. Aktion PENDING → REQUIRES_RECONCILE
   d. Unbekannt → RECOVERY_UNSAFE
```

## 47. Dokument-Hierarchie nach Paket-Abschluss

```
EBENE 1: questor_ergebnis_paket (DER BERICHT)
  → Geht an: Receiver → Archivar → Gremium
  → Größe: Klein (KB)

EBENE 2: ExpeditionLedger (DAS LABORBUCH)
  → Bleibt lokal: data/questor_ledger/
  → Größe: Mittel bis Groß (MB)
  → Zugriff: Read-only, nur autorisierte Rollen

EBENE 3: QuestorBlackbox (DIE ROHDATEN)
  → Bleibt lokal: data/questor_blackbox/
  → Größe: Groß (MB bis GB)
  → Zugriff: Nur Entwickler/Notfall
```

## 48. Zugriffskontrolle für das Ledger

```python
LEDGER_ACCESS_MATRIX = {
    "questor_intern":     (True,  True,  False),  # Während Ausführung
    "receiver":           (False, False, False),
    "archivar":           (False, False, False),
    "kartograph":         (False, False, False),
    "kanzler":            (False, False, False),
    "vordenker":          (False, False, False),
    "quartiermeister":    (False, False, False),
    "domain_expert":      (True,  False, False),  # Read-only
    "system_integrator":  (True,  False, False),  # Read-only
    "developer":          (True,  False, False),  # Read-only
    "safety_process":     (True,  False, False),  # Read-only (bei SAFETY)
}
```

---

# TEIL G: RESULT-BUILDER

---

## 49. Der Result-Builder-Algorithmus

```
SCHRITT 1: STATUS BESTIMMEN
SCHRITT 2: SICHERHEITSREGELN ANWENDEN
SCHRITT 3: ERGEBNIS-DATEN SAMMELN
SCHRITT 4: SIGNALE AUS KRISTALLKANDIDATEN ERZEUGEN
SCHRITT 5: QUESTOR_METADATA BAUEN
SCHRITT 6: GUARDIAN-VALIDIERUNG
SCHRITT 7: BLACKBOX SCHREIBEN
SCHRITT 8: SEQUENCE ATOMAR PERSISTIEREN
SCHRITT 9: ERGEBNIS ZUSAMMENSETZEN
```

## 50. Feldzuordnung: Ledger → questor_ergebnis_paket

| Feld im Ergebnis | Quelle | Regel |
|---|---|---|
| `package_id` | ExecutionContext | Direkt übernommen |
| `zyklus_id` | ExecutionContext | Direkt übernommen |
| `attempt_id` | ExecutionContext | Direkt übernommen |
| `idempotency_key` | Berechnet | `package_id:zyklus_id:attempt_id` |
| `questor_instance_id` | ExpeditionLedger | Beim Genesis-Eintrag erzeugt |
| `sequence_number` | SequenceStore | Atomar persistiert bei FINALIZATION |
| `observed_atlas_version_id` | ExecutionContext.atlas_version_ref | **Pass-Through, kein LLM-Zugriff** |
| `status` | QuestCompassDecision | erfolgreich / fehlgeschlagen / abgebrochen |
| `abbruch_grund` | QuestCompassDecision | null bei Erfolg, sonst gesetzt |
| `abbruch_klasse` | QuestCompassDecision | OPERATIONAL / SCIENTIFIC / SAFETY |
| `routing_checkpoint` | ExpeditionLedger | Aus Loop-Einträgen abgeleitet |
| `ergebnis_daten` | ExpeditionLedger | Aus STEP_RESULT-Einträgen |
| `validierung` | Result-Builder | Guardian-Validierung |
| `kristall_kandidaten` | QuestCompassDecision | Leer bei SAFETY |
| `gefahren_beobachtet` | QuestCompassDecision | Aus SafetyMonitor |
| `signale_fuer_atlas` | QuestCompassDecision | Leer bei SAFETY |
| `vollstaendig_flag` | Result-Builder | **IMMER true** |
| `rohdaten_checksumme` | Result-Builder | SHA256 über ergebnis_daten |
| `questor_metadata` | Result-Builder | operational_metrics + local_audit + template_feedback |

## 51. Sonderregeln

```
REGEL 1: observed_atlas_version_id ist PASS-THROUGH
REGEL 2: vollstaendig_flag ist IMMER true
REGEL 3: abbruch_klasse ist IMMER gesetzt (auch bei Erfolg: OPERATIONAL)
REGEL 4: Bei SAFETY: kristall_kandidaten = [], signale_fuer_atlas = []
REGEL 5: questor_metadata erzeugt KEINE Kristalle/Signale
```

## 52. Kristallkandidaten — Korrigierte Definition

**Der Kristallkandidat ist NICHT der Messwert allein, sondern der VERWENDETE LOOP mit den jeweiligen Einstellungen und dem Ergebnis.**

```python
KristallKandidat:
    kristall_id: str
    typ: str                          # z.B. "kinetik_optimum"
    loop_template: str                # Welcher Loop wurde verwendet
    loop_parameter: dict[str, Any]    # Mit welchen Einstellungen
    wert: dict[str, Any]              # Was war das Ergebnis
    konfidenz: float                  # Wie sicher ist das Ergebnis
    ziel_erreicht: bool               # Wurde das Ziel erreicht
    ist_diagnostic: bool              # Ist es ein Diagnose-Kristall
    cluster_integration: bool         # Darf es in normale Cluster
```

**Wer erzeugt Kristallkandidaten?** Der **QuestCompass** während der EVALUATION. Deterministisch:
- Konfidenz >= clarity_threshold → Kristallkandidat
- Konfidenz < clarity_threshold → Kein Kristallkandidat

## 53. Signale für Atlas — Fazit aus Kristallkandidaten

```python
def generate_signal_from_kristall(kristall, zone_ref, objective_type):
    if kristall.ziel_erreicht and kristall.konfidenz >= 0.8:
        signal_typ = "🟩"  # GRÜN: Bestätigt
    elif kristall.ziel_erreicht and kristall.konfidenz >= 0.5:
        signal_typ = "⬜"  # WEISS: Neutral
    elif not kristall.ziel_erreicht:
        signal_typ = "🟨"  # GELB: Widerspruch
    else:
        signal_typ = "⬜"  # WEISS: Fallback

    if kristall.ist_diagnostic:
        signal_typ = "🟪"  # PURPUR: Diagnostisch

    return SignalEvent(signal_typ=signal_typ, zone_ref=zone_ref, ...)
```

## 54. Early-Abort Complete Result (C21)

```python
def build_early_abort_result(abbruch_grund, context):
    return QuestorErgebnisPaket(
        status="abgebrochen",
        abbruch_grund=abbruch_grund,
        abbruch_klasse="OPERATIONAL",
        routing_checkpoint=RoutingCheckpoint(letzter_node="LEER", iterationen=0, ...),
        ergebnis_daten=ErgebnisDaten(messwerte={}),
        kristall_kandidaten=[],
        signale_fuer_atlas=[],
        vollstaendig_flag=True,
        rohdaten_checksumme="sha256:",
        ...
    )
```

## 55. Guardian-Validierung

```
CHECK 1: Hash-Chain-Integrität
CHECK 2: Keine NaN/Infinity in ergebnis_daten (C18)
CHECK 3: Alle Pflichtfelder vorhanden
CHECK 4: Genesis-Hash korrekt
CHECK 5: Keine verbotenen Felder

Bei FAIL: Ergebnis wird trotzdem gebaut, aber mit guardian_status: FAIL
```

## 56. Blackbox-Archiver

```yaml
QuestorBlackbox:
    blackbox_id: str
    package_id: str
    zyklus_id: str
    attempt_id: int
    ledger: ExpeditionLedger
    raw_data: dict[str, Any]
    llm_advice_log: list[dict]
    error_details: Optional[dict]
    created_at: str
    questor_version: str
    retention_class: NORMAL | SAFETY_HOLD | DEVELOPMENT_HOLD
```

**retention_class-Bestimmung:**

| Bedingung | retention_class |
|---|---|
| abbruch_klasse == SAFETY | SAFETY_HOLD |
| security_mode in (DEV_SANDBOX_ONLY, SANDBOX) | DEVELOPMENT_HOLD |
| Sonst | NORMAL |

**Blackbox-Limits:**

```yaml
max_file_size_mb: 100
max_blackbox_count: 50
rotation_policy: OLDEST_FIRST
retention_by_class:
  NORMAL: 90_days
  SAFETY_HOLD: unlimited
  DEVELOPMENT_HOLD: 30_days
```

## 57. Sequence-Manager

```python
questor_instance_id = f"qi-{package_id}-{sha256(f'{package_id}:{zyklus_id}:{attempt_id}')[:8]}"

# Sequence-Nummer wird atomar persistiert:
# 1. FINALIZATION-Eintrag ins Ledger
# 2. Checkpoint erstellen
# 3. Sequence-Store aktualisieren (Datei-Lock)
# 4. WAL-Eintrag als COMMITTED markieren
```

---

# TEIL H: QUESTOR-FACADE (QUEUE-ARCHITEKTUR)

---

## 58. Queue-Architektur

```
data/questor_queue/
  ├── pending/          ← Wartende Pakete
  ├── processing/       ← Paket in Bearbeitung (max. 1 Datei)
  ├── completed/        ← Abgeschlossene Pakete (Archivar bereinigt)
  ├── failed/           ← Fehlgeschlagene Pakete (Archivar bereinigt)
  ├── delete_requests/  ← Löschanfragen vom Gremium
  └── registry.json     ← Status-Übersicht (mit Datei-Lock)
```

## 59. Der Questor-Prozess

```
QUESTOR-PROZESS (eigener Prozess, losgelöst vom Gremium):

  START:
    1. Questor-Prozess startet
    2. Konfiguration laden
    3. LoopRegistry laden (data/questor_templates/)
    4. WAL prüfen (Recovery nötig?)
    5. Wenn Recovery nötig → recover()
    6. Wenn kein Recovery → Hauptloop starten

  HAUPTLOOP:
    while true:
      1. Prüfe: Gibt es Lösch-Anfragen? → Verarbeiten
      2. Prüfe: Bin ich IDLE?
         → JA: Prüfe pending/ auf Pakete
         → NEIN: Warte auf Abschluss
      3. Wenn Paket gefunden:
         → Ältestes Paket nehmen
         → Nach processing/ verschieben
         → Ausführen
         → Ergebnis schreiben
         → Nach completed/ oder failed/ verschieben
         → Registry aktualisieren
      4. Wenn kein Paket:
         → Warte 5 Sekunden (poll_interval_s)
         → Zurück zu Schritt 1
```

## 60. Facade vs. Validator — Abgrenzung

| Prüfung | Wer | Was |
|---|---|---|
| Ist es ein Envelope? | **Facade** | Envelope vs. nacktes ResearchPackage |
| Ist gate_record_ref vorhanden? | **Facade** | Envelope-Struktur |
| Ist idempotency_key kanonisch? | **Facade** | Envelope-Struktur |
| Ist attempt_id im Bereich? | **Facade** | Envelope-Struktur |
| Ist das Paket inhaltlich gültig? | **Validator** | Paket-Inhalt |
| Ist routing_graph vollständig? | **Validator** | Paket-Inhalt |
| Ist questor_spec gültig? | **Validator** | Paket-Inhalt |

## 61. Paket-Status und Sichtbarkeit

```
SCHREIBEN IN DIE QUEUE:
  → Dispatcher schreibt Envelope in data/questor_queue/pending/
  → Dispatcher aktualisiert registry.json

SCHREIBEN IN DEN ATLAS:
  → NICHT Questor (Questor schreibt nie in Atlas!)
  → Der Pipeline-Orchestrator (gehört zum Gremium)
    liest registry.json und aktualisiert den Atlas

AKTUALISIERUNG DER REGISTRY:
  → Questor aktualisiert NUR die lokale registry.json
  → Questor verschiebt NUR Dateien zwischen den Ordnern
```

## 62. Löschen von Paketen durch das Gremium

```
1. Kanzler/Quartiermeister entscheidet: Paket nicht mehr nötig
2. Löschanfrage wird geschrieben:
   data/questor_queue/delete_requests/{package_id}_{zyklus_id}_{attempt_id}.delete
3. Questor prüft bei nächstem Poll die Löschanfrage
4. Wenn Paket in pending/ → löschen
5. Wenn Paket in processing/ → NICHT löschen
6. Registry aktualisieren: status = GELÖSCHT

REGEL:
  → Pakete in pending/ können gelöscht werden
  → Pakete in processing/ können NICHT gelöscht werden
  → Pakete in completed/ oder failed/ können NICHT gelöscht werden
```

## 63. Timeout-Handling

```
1. max_duration_s wird im QuestorSpec.budget definiert
2. QuestCompass prüft max_duration_s bei jedem Planungszyklus
3. Wenn max_duration_s erreicht:
   → QuestCompass bricht ab mit BUDGET_EXHAUSTED
   → Result-Builder baut vollständiges Ergebnis
   → Facade wird korrekt zurückgesetzt (IDLE)
   → Paket wird nach failed/ verschoben
```

## 64. ESTOP-Handling

```
1. HAL meldet ESTOP (SAFETY)
2. HAL-Bridge sendet KEINE weiteren Kommandos
3. QuestCompass leitet FINALIZING ein (SAFETY)
4. Result-Builder baut vollständiges Ergebnis
5. Ergebnis wird nach failed/ verschoben
6. Facade wird korrekt zurückgesetzt (IDLE)
7. Questor kann nach ESTOP weiterarbeiten
```

---

# TEIL I: SICHERHEITSREGELN

---

## 65. Zusammenfassung aller Sicherheitsregeln

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
| atlas_version_ref ist Pass-Through | QuestCompass v0.1.0 |
| HAL-Bridge sendet keine Kommandos bei SAFETY_ABORT | HAL-Bridge v0.1.0 |
| Recovery NUR aus WAL | HAL-Bridge v0.1.0 |
| Ledger ist READ-ONLY nach Abschluss | ExpeditionLedger v0.1.0 |
| Kristallkandidat = Loop + Einstellungen + Ergebnis | Result-Builder v0.1.0 |
| Bei SAFETY: Kristalle und Signale leer | Result-Builder v0.1.0 |
| vollstaendig_flag ist IMMER true | Result-Builder v0.1.0 |
| Questor verarbeitet immer nur EIN Paket | Grundannahme |
| Questor ist eigener Prozess, losgelöst vom Gremium | Facade v0.1.0 |
| Pakete in processing/ nicht löschbar | Facade v0.1.0 |

---

# TEIL J: GREMIUM-AUSLAGERUNGEN

---

## 66. Alle Gremium-Auslagerungen

| # | Thema | Gremium-Komponente | Status |
|---|---|---|---|
| G-1 | Template-Erstellung bei fehlendem Template | Quartiermeister + Domain-Experte | ✅ |
| G-2 | Template-Korrektur nach Questor-Feedback | Domain-Experte (NICHT Kanzler) | ✅ |
| G-3 | Template-Versionierung (alte Versionen im Archiv) | Archivar | ✅ |
| G-4 | Ressourcen-Karte (Verbrauch pro Zone/Dimension) | Kartograph | ✅ |
| G-5 | Vordenker liefert `prozess_skizze` mit Idee | Vordenker | ✅ |
| G-6 | `template_feedback` operational protokollieren | Archivar | ✅ |
| G-7 | Kosten-Schätzungen für Reagenzien | System-Integrator | ✅ |
| G-8 | Kanzler erhält periodische Template-Zusammenfassung | Kanzler (nur Übersicht) | ✅ |
| G-9 | Quartiermeister berücksichtigt `template_feedback` | Quartiermeister | ✅ |
| G-10 | `atlas_version_ref` ist Pass-Through, kein LLM-Zugriff | Questor (intern) | ✅ |
| G-11 | `loop_selection_weights` optional im QuestorSpec | Quartiermeister | ✅ |
| G-12 | `planning_hints` als optionales Feld | Quartiermeister | ✅ |
| G-13 | Pipeline-Orchestrator liest `registry.json` und aktualisiert Atlas | Pipeline-Orchestrator (Gremium) | ✅ |
| G-14 | Archivar bereinigt `completed/` und `failed/` nach Archivierung | Archivar | ✅ |
| G-15 | Gremium schreibt Löschanfragen in `delete_requests/` | Kanzler / Quartiermeister | ✅ |

---

## 67. Noch offene Themen

| # | Thema | Priorität | Anmerkung |
|---|---|---|---|
| 1 | Sanitization — LLM-Input-Sanitization | 🟡 Mittel | Prompt-Injection-Schutz |
| 2 | Capability-Registry — Formale Definition | 🟡 Mittel | Was ist eine Capability? HAL-Mapping |
| 3 | Trail-Map — Struktur, Erzeugung | 🟢 Niedrig | Kann nachgelagert |
| 4 | Questor-Health-Monitoring | 🟢 Niedrig | Kann nachgelagert |
| 5 | Questor-Graceful-Shutdown | 🟢 Niedrig | Kann nachgelagert |
| 6 | security_mode-Verhalten im Detail | 🟢 Niedrig | Kann nachgelagert |

---

## 68. Zusammenfassung aller Architektur-Entscheidungen

| Thema | Entscheidung |
|---|---|
| Questor-Zustandsmaschine | 11 Zustände, PLAN→EXECUTE→EVALUATE→RE-PLAN Zyklus |
| Loop-Kette | Dynamisch, entsteht durch Feedback-Schleife |
| Routing-Graph | Constraint-Framework, kein fester Plan |
| Kristallkandidat | Loop + Einstellungen + Ergebnis (NICHT Messwert allein) |
| Signal | Fazit aus Kristallkandidaten (deterministisch) |
| Autonomy-Level | Steuert candidate_window und LLM-Nutzung |
| Budget-Logik | Ziel erreichen, nicht Budget ausgeben |
| Kostenmodell | Zeit + Reagenzien + Compute (normiert) |
| Gesamtkosten statt Einzelkosten | Ja, verhindert Kosten-Falle |
| Templates | Dateien in data/questor_templates/ |
| Template-Erstellung | Domain-Experte / System-Integrator |
| Template-Korrektur | Questor → Archivar → Domain-Experte |
| Template-Versionierung | Semantisch (Major.Minor) |
| HAL-Bridge | Einzige Verbindung zu HAL |
| HAL-Bridge übersetzt | LoopStep → HALCommand/ProcessCommand |
| HAL-Bridge prüft | Security-Mode, Lease, parameter_bounds |
| DUPLICATE_BLOCKED | Als SUCCESS behandelt |
| ESTOP/INTERLOCK | Als SAFETY_ABORT behandelt |
| SAFE_HOLD / RESUME | Vollständig spezifiziert |
| WAITING_FOR_RELEASE | Questor wartet bis HAL antwortet |
| timeout_s vs expected_duration | Strikt getrennt |
| ExpeditionLedger | APPEND-ONLY, Hash-Chain |
| Genesis-Hash | Aus Paket-IDs + Gate-Ref + Atlas-Ref |
| NaN/Infinity | Fail-Closed (C18) |
| WAL | Crash-Recovery, nach DONE bereinigt |
| Recovery | NUR aus WAL |
| Result-Builder | Liest aus Ledger, baut questor_ergebnis_paket |
| Guardian-Validierung | Hash-Chain, NaN/Infinity, Pflichtfelder |
| Blackbox | Lokal, retention_class, Limits |
| Sequence-Manager | Atomar, Datei-Lock |
| questor_instance_id | Deterministisch, von Facade erzeugt |
| Facade | Dateibasierte Queue, eigener Prozess |
| Queue | pending/, processing/, completed/, failed/, delete_requests/ |
| Poll-Intervall | 5 Sekunden |
| Ältestes Paket zuerst | Ja |
| Pakete in processing/ | Max. 1 Datei (impliziter Lock) |
| Registry | Mit Datei-Lock |
| Pipeline-Orchestrator | Liest registry.json, aktualisiert Atlas |
| Archivar | Bereinigt completed/ und failed/ |
| Löschanfragen | Über delete_requests/ |
