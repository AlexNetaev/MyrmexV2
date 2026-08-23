# GREMIUM CORE — Invarianten, Grunddefinitionen, Rollen, Zugriffsregeln

| Feld | Wert |
|------|------|
| **Dateiname** | `gremium_10_core.md` |
| **Modul** | CORE |
| **Version** | 1.0.0 |
| **Status** | AKTIV |
| **Hängt ab von** | CHARTER 1.0.0, CONTRACTS 1.1.0-atlas-hyb.1 (extern) |
| **Wird referenziert von** | `gremium_20_contracts`, `gremium_30_rules`, `gremium_40_control` |
| **Änderungsgrund** | Konsolidierung aus v0.2.0 §0-§3, §5 + v0.3.0 §2; Achsen-Integration |
| **Change-Log** | 1.0.0: Initiale Konsolidierung; Achsen-Referenzen in Grunddefinitionen; Domain Knowledge Base (KV2-09) als Design-Notiz |

---

## §0 Zweck und Geltung

### §0.1 Zweck

Dieses Modul definiert die **Invarianten** des Gremiums („Cognitive Observatory"): ein System, das über Wochen autonom forschen kann — drift-frei, CHARTER-konform, mit deterministischen Endentscheidungen und definierten menschlichen Eingriffspunkten.

### §0.2 Geltung und Selbständigkeit

Dieses Modul ist die **Grundlage** aller anderen Module. Es definiert:
- die Grunddefinitionen (Zyklus, Weißraum, Zeit),
- die Rollen und Zugriffsregeln,
- das Constitutional Anchor Protocol (Anti-Drift),
- die Architektur und Kern-Patterns,
- das Verhältnis zu CHARTER, CONTRACTS und den Modulen.

Es enthält **keine Datenverträge** (die liegen in `20_contracts`), **keine Mechanik** (die liegt in `30_rules`) und **keine Achsen-Steuerung** (die liegt in `40_control`).

### §0.3 Verhältnis zur CHARTER-Präambel

Die CHARTER friert den Scope ein („Keine neuen Features"). Dieses Modul ist daher ein formaler Änderungsantrag. Es ändert keine der 58 Sicherheitsregeln; es präzisiert ausschließlich deren Durchsetzung auf Gremium-Ebene.

---

## §1 Grunddefinitionen (SL-DEF-1..5)

### §1.1 SL-DEF-1: Der strategische Zyklus

```
1 Zyklus = 1 abgeschlossener strategischer Regelkreis:
StrategicBriefing erzeugt → StrategicDirective empfangen → Validierung → Policy-Wirkung
```

Alle Parameter mit der Endung `_cycles` beziehen sich auf diesen Zyklus. Der Zykluszähler ist der fortlaufende `briefing_id`-Zähler der Mission (v0.3.0 SL-DEF-4: `zyklus_id` abgeschafft).

**Achsen-Integration:** Der strategische Zyklus liest den `ControlState` (kanonisch in `20_contracts §3`, gesteuert durch `40_control`). Die Achsen-Parameter bestimmen das Verhalten innerhalb des Zyklus.

### §1.2 SL-DEF-2: Weißraum

Eine Region gilt als Weißraum, wenn ihre Zone `UNEXPLORED` ist oder `EXPLORED_INCONCLUSIVE` mit `evidence_mass == 0`.

### §1.3 SL-DEF-3: Pipeline-Takt (v0.3.0)

Ereignisgetrieben; jedes verarbeitete Ergebnis/Paket schreitet fort. Treibt Archivar/Kartograph/Atlas.

### §1.4 SL-DEF-4: Strategie-Zyklus (v0.3.0)

Der Briefing-Regelkreis aus SL-DEF-1. `briefing_interval_cycles` zählt Strategie-Zyklen. Ein Strategie-Zyklus wird ausgelöst durch `cycle_trigger ∈ {TIME, EVENT_COUNT, MANUAL}` (Config). `briefing_id` ist die einzige, fortlaufende Zyklen-ID.

### §1.5 SL-DEF-5: TimeService-Nutzung (v0.3.0)

Alle `*_days`-Parameter (`cold_storage_window_days`) und alle `valid_until`-/Timeout-Auswertungen nutzen ausschließlich `TimeService` (Vertrag in `20_contracts §9`). Alle `*_cycles`-Parameter nutzen den Strategie-Zyklus (SL-DEF-4). Eine Vermischung ist unzulässig.

---

## §2 Rollen und Zugriffsregeln

### §2.1 Rollen-Kurzreferenz

| Rolle | Schicht | LLM | Kognitive Funktion | Achsen-Interaktion |
|---|---|---|---|---|
| 👑 Königin | 5 | Ja (stateless + constitutional) | Vision, Pivot, Budget-Freigabe-Vorschläge, Abschlussbericht-Entwurf | liest ControlState via Briefing; schlägt SET_RESEARCH_PHASE vor |
| 🏛️ Kanzler | 4 | Nein | Briefing, Validierung, Policy, RoyalLog, Dimension-/Eskalations-Governance | liest und schreibt ControlState; erzwingt Achsen-Transitionen |
| 🧠 Vordenker | 4 | Ja (grounded) | Kausale Modelle, Hypothesen, Dimensions-Vorschläge | liest ControlState via SymptomEvents |
| 🧭 Lotse | 4 | Nein | Wegmarken, Capability-Prüfung | liest ControlState für Capability-Checks |
| 📦 Quartiermeister | 4 | Nein | Paketbau, Manifest-/Twin-Checks | liest ControlState für Paketbau |
| ⚖️ Sicherheitsrat | 4 | Seher advisor-only | Gate | liest SafetyAxis für Gate-Entscheidungen |
| 🗺️ Kartograph | 4 | Nein | Atlas, Symptome, Twin-Divergenz, Kalibrierungs-Tracking | liest ControlState für Symptom-Erzeugung |
| 📚 Archivar | 4 | Nein | Wissensaufnahme, Sanitization am Eingang | liest ControlState für Sanitization |
| 🧭 Questor | 2 | Advisor-intern | Ausführung (unverändert) | keine Achsen-Interaktion |

### §2.2 Zugriffs- und Kommunikationsregeln (SL-ACC-1..4)

- **SL-ACC-1:** Alle Kommunikation zwischen Rängen läuft ausschließlich über Blackboard-Artefakte (Atlas, Archiv, Governance-Verzeichnisse gemäß `30_rules §20.5`). Keine direkten Aufrufe. (CHARTER §2)
- **SL-ACC-2:** Die Königin liest den Atlas nicht direkt. Ihr einziger Informationszugang ist das `StrategicBriefing`. (behebt F-33)
- **SL-ACC-3:** Der Vordenker liest Atlas-Topologie nur lesend und nur als kuratierte Blackboard-Ausschnitte; er schreibt niemals in den Atlas.
- **SL-ACC-4:** Questor und HAL bleiben vollständig unverändert; sie kennen keine strategischen Verträge.

---

## §3 Constitutional Anchor Protocol (Anti-Drift)

Jeder Königin-LLM-Aufruf erhält exakt drei Kontextblöcke (SL-ANCHOR-1):

```
SCHICHT 1 — CONSTITUTIONAL MEMORY (invariant)
   ResearchManifest: mission_goal (Scan), machine-readable hard_constraints,
   soft_preferences, Verbotene Aktionen, Output-Schema

SCHICHT 2 — STATELESS BRIEFING (dynamisch, kuratiert)
   StrategicBriefing: aggregierter Zustand, Budget, Fractures, Twin-Status,
   DecisionsRequired, Hardware-Health, ControlState-Achsen — kein security_mode,
   keine Atlas-Hybrid-Referenzen, kein Roh-metric_vector

SCHICHT 3 — ANCHOR (Kontinuität)
   royal_log_anchor: zuerst alle aktiven HUMAN_OVERRIDE-Einträge,
   dann die letzten royal_log_anchor_depth (=3) eigenen Direktiven
   mit Outcome (IMPLEMENTED/VETOED/SUPERSEDED/EXPIRED/ESCALATED)
```

**Invarianten:**
- **SL-ANCHOR-2:** Kein persistenter Gesprächsverlauf. Jeder Aufruf ist frisch.
- **SL-ANCHOR-3:** Menschliche Weisungen im Anchor überschreiben alle Königin-Direktiven. Der Anchor enthält den expliziten Hinweis: „Menschliche Weisungen haben Vorrang vor allen früheren Direktiven." (behebt PROB-22)
- **SL-ANCHOR-4:** Bei LLM-Fehler/Timeout: deterministischer Fallback = aktuelle ExplorationPolicy bleibt unverändert; Audit-Event; kein erweiterter Retry-Kontext. Nach `max_consecutive_llm_failures` → HumanEscalationRecord. (SR-28)

---

## §4 Architektur-Überblick

```
┌───────────────────────────────────────────────────────────────────────┐
│  MENSCHLICHE KÖNIGIN / SPONSOR (SR-11: niemals überstimmt)            │
│  • setzt ResearchManifest (einziger Autor von hard_constraints)       │
│  • beantwortet HumanEscalationRecords (data/human_inbox/)             │
│  • HUMAN_OVERRIDE, SAFE_MODE, Manifest-Versionierung                  │
│  • setzt ResearchPhase via HumanDirective.set_research_phase          │
└──────────────────────────────┬────────────────────────────────────────┘
                               ▼
┌───────────────────────────────────────────────────────────────────────┐
│  SCHICHT 5: 👑 KÖNIGIN (LLM, stateless + constitutional)              │
│  IN : ResearchManifest + StrategicBriefing + Anchor (RoyalLog)        │
│  OUT: StrategicDirective (Vorschlag, schema-validiert)                │
└──────────────────────────────┬────────────────────────────────────────┘
                               ▼
┌───────────────────────────────────────────────────────────────────────┐
│  SCHICHT 4: 🏛️ GREMIUM — STRATEGISCHE SCHLEIFE                        │
│                                                                       │
│  KANZLER (deterministisch):                                           │
│    Briefing-Generator · Directive-Validator (10 Stufen) ·             │
│    DirectiveTranslationTable · RoyalLog · MissionBudget ·             │
│    Dimension-Governance · Eskalations-Manager · SAFETY-RESPONSE ·     │
│    ControlState-Verwaltung (Achsen-Transitionen)                      │
│                                                                       │
│  KARTOGRAPH → VORDENKER → PRE-FILTER → LOTSE → QUARTIERMEISTER        │
│  → SICHERHEITSRAT → DISPATCH → QUESTOR → ARCHIVAR → KARTOGRAPH → ATLAS│
└───────────────────────────────────────────────────────────────────────┘
```

**Achsen-Integration:** Der Kanzler verwaltet den `ControlState` (vier orthogonale Achsen: Safety, Resource, Research, Governance). Alle Regeln in `30_rules` lesen den ControlState und verwenden die zustandsabhängigen Parameter. Die Achsen-Transitionen werden durch Ereignisse ausgelöst (ESTOP, Budget-Erschöpfung, Eskalation-Timeout, SET_RESEARCH_PHASE).

---

## §5 Kern-Patterns

### §5.1 Stateless Director

Die Königin ist zustandslos (§3). Strategisches Gedächtnis entsteht nur durch Manifest, Anchor und Atlas-Aggregate.

### §5.2 Deterministic Gatekeeper

Der Kanzler ist rein deterministisch (SL-GATE-1): kein LLM-Einsatz, auch nicht für Zusammenfassungen. Alle Freitext-Bausteine in Briefings werden template-basiert aus strukturierten Daten erzeugt.

### §5.3 Topology-Grounded Hypothesis Engine

Der Vordenker wird ausschließlich über SymptomEvents aktiviert (`30_rules §6`) und nutzt Topology-Prompting (FRACTURE / VOID / BRIDGE / TWIN_DRIFT / SATURATION) auf kuratierten Atlas-Ausschnitten.

### §5.4 Digital-Twin-Loop

Vollständig gemäß DIGITAL-TWIN-SEM-1.0.0, gehärtet nach `30_rules §10`.

### §5.5 Orthogonal Control Axes (NEU)

Das System wird durch vier orthogonale Steuerachsen kontrolliert (Safety, Resource, Research, Governance), definiert in `40_control`. Die Achsen sind unabhängig voneinander zustandsbehaftet und komponieren sich zu einem `ControlState`-Tupel. Regeln lesen den ControlState, sie setzen Achsen-Parameter nicht direkt (Single Ownership).

---

## §6 Verhältnis zu CHARTER, CONTRACTS und den Modulen

### §6.1 Konfliktregel

```
CHARTER > CONTRACTS > 10_core > 20_contracts > 30_rules > 40_control
```

Bei Widerspruch zwischen Modulen gilt das höherprioritäre Modul. Die Achsen-Parameter werden jedoch nicht durch Hierarchie, sondern durch **Single Ownership** aufgelöst (jede Achse besitzt ihre Parameter, Regeln lesen nur).

### §6.2 Modul-Abhängigkeiten

```
10_core (Invarianten, Grunddefinitionen)
    ↑
20_contracts (Datenverträge, Config)
    ↑
30_rules (Mechanik, Validierung, Zustandsmaschinen)
    ↑
40_control (Achsen-Steuerung, ControlState)
```

Jedes Modul referenziert die darunterliegenden Module. Kein Modul definiert Verträge oder Regeln, die in einem anderen Modul liegen.

---

## §7 Domain Knowledge Base (Design-Notiz, KV2-09)

### §7.1 Problem

Lessons-Learned sind topic-lokal (SL-DTT-1, SL-MAN-1 gewahrt). Fundamentale wissenschaftliche Erkenntnisse (z. B. „Disulfidbrücken brechen >90 °C oxidativ auf") werden in neuen, artverwandten Missionen nicht wiederverwendet → Wissens-Amnesie.

### §7.2 Design

Eine **Domain Knowledge Base** (DKB) wird als separate Schicht eingeführt:
- **Getrennt vom Manifest:** Das Manifest bleibt für hard_constraints menschlich-exklusiv (SL-MAN-1).
- **Beratend, nicht hart:** Die DKB ist advisory, nicht deterministisch durchgesetzt.
- **Menschliche Promotion:** Validierte Lessons können vom Menschen in die DKB promoted werden.
- **Domänen-scoped:** Die DKB ist je Domäne (z. B. „Biochemie", „Materialwissenschaft") organisiert.
- **Wiederverwendung:** Neue Missionen derselben Domäne können die DKB als Kontext lesen.

### §7.3 Umsetzung

Die DKB wird als eigener Vertrag in `20_contracts` definiert und als Regel in `30_rules` implementiert. Sie ist **nicht** Teil des ControlState, sondern ein separates Blackboard-Artefakt.

**Status:** Design-Notiz, Umsetzung in zukünftiger Version.

---

## §8 Selbständigkeitserklärung

Dieses Modul ist abgeschlossen testbar als Einzeldatei. Es enthält:
- alle Grunddefinitionen mit eindeutigen IDs (SL-DEF-1..5),
- alle Zugriffsregeln mit eindeutigen IDs (SL-ACC-1..4),
- das Constitutional Anchor Protocol mit eindeutigen IDs (SL-ANCHOR-1..4),
- die Architektur und Kern-Patterns,
- das Verhältnis zu CHARTER, CONTRACTS und den Modulen,
- die Domain Knowledge Base als Design-Notiz.

Es referenziert CHARTER, CONTRACTS, GREMIUM, QUESTOR, HAL und DIGITAL-TWIN-SEM nur zur Einordnung. Wo dieses Modul eine Änderung an diesen Dokumenten erfordert, ist sie in `30_rules §25` als Änderungsantrag explizit gemacht.

---

## §9 Behobene Funde (Traceability)

| Fund | Auflösung |
|---|---|
| KV2-09 (Wissens-Amnesie) | Domain Knowledge Base als Design-Notiz (§7); Umsetzung in zukünftiger Version |
| F-33 (Königin liest Atlas direkt) | SL-ACC-2 (§2.2) |
| PROB-22 (menschliche Weisungen im Anchor) | SL-ANCHOR-3 (§3) |
| F-35 (Zyklus-Definition) | SL-DEF-1 (§1.1) |
| PROB-05 (Weißraum-Definition) | SL-DEF-2 (§1.2) |
| F-73, F-74, T4-F-14 (zyklus_id) | SL-DEF-4 (§1.4), zyklus_id abgeschafft |
| F-87 (Zeit-Vermischung) | SL-DEF-5 (§1.5) |

---

## §10 Changelog

| Version | Datum | Änderung | Funde behoben |
|---|---|---|---|
| 1.0.0 | 2025-01-XX | Initiale Konsolidierung aus v0.2.0 §0-§3, §5 + v0.3.0 §2; Achsen-Referenzen in Grunddefinitionen; Domain Knowledge Base (KV2-09) als Design-Notiz | KV2-09 (Design); F-33, F-35, F-73, F-74, F-87, PROB-05, PROB-22 |

---

**Ende des Core-Moduls v1.0.0.**