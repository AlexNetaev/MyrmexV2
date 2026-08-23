# 🏛️ GREMIUM — VOLLSTÄNDIGE SPEZIFIKATION

| Feld | Wert |
| --- | --- |
| Dateiname | `specs/GREMIUM.md` |
| Version | `1.1.0-atlas-hyb.1` |
| Status | `ÄNDERUNGSANTRAG ATLAS-HYB-1.0.0 — nach Freigabe BINDEND` |
| System | `MYRMEX v2.4.0 + Questor v0.2.3` |
| Schicht | `Layer 1 (specs/) — referenziert foundation/` |
| Datum | `21. August 2026` |

## 0. Geltung und Änderungsregeln

Dieses Dokument definiert die vollständige Gremium-Spezifikation (Schicht 4 im MYRMEX-System).

**Regel:** Dieses Dokument referenziert Verträge aus `CONTRACTS.md` und Sicherheitsregeln aus `CHARTER.md`.
Es definiert keine neuen Verträge und keine neuen Sicherheitsregeln.

**Konfliktregel:** Bei Widersprüchen gilt `CHARTER.md` > `CONTRACTS.md` > dieses Dokument.

## §0.1 Änderungsantrag ATLAS-HYB-1.0.0 — Atlas-Hybrid-Erweiterung

Dieser Änderungsantrag integriert das Atlas-Hybrid-System in die Gremium-Spezifikation.

Das Atlas-Hybrid-System erweitert den Atlas um:

1. Evidence-Semantik
2. Qualitäts- und Reproduktionsmetadaten
3. Typed Dimensions und ZoneGeometry
4. Atlas-Knoten und Atlas-Kanten
5. Objective Families für Multi-Objective-Forschung
6. DiagnosticResolution
7. SafetyConstraints
8. ExclusionConstraints
9. FrontierCandidates
10. ResearchTopics
11. ExplorationPolicy
12. AtlasHybridConfig

Regeln:

- Dieser Änderungsantrag definiert keine neuen Datenverträge.
- Alle Datenverträge kommen aus `CONTRACTS.md §6.10`.
- Dieser Änderungsantrag definiert keine neuen Sicherheitsregeln.
- Questor erhält keine Schreibrechte in Atlas oder Archiv.
- HAL erhält keine wissenschaftliche Interpretation.
- Die bestehende CHARTER-Hierarchie bleibt unberührt.
- Bei Widersprüchen gilt: `CHARTER.md` > `CONTRACTS.md` > dieses Dokument.

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
│  │              ATLAS-HYBRID-SYSTEM                           │   │
│  │  Evidence-Semantik · Energiekonten · Kristallisation      │   │
│  │  FrontierEngine · ResearchTopics · ExplorationPolicy      │   │
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
| --- | --- | --- | --- |
| 1 | Blackboard-Pattern | Alle Ränge des Gremiums kommunizieren ausschließlich über Atlas und Archiv. Keine direkten Aufrufe zwischen Rängen. | CHARTER §2 |
| 2 | Menschliche Königin wird niemals überstimmt | Bei Konflikt zwischen menschlicher und LLM-Königin gewinnt die menschliche Weisung. Nach 2 Konflikten fällt die LLM-Königin auf menschliche Entscheidung zurück. | CHARTER §SR-11 |
| 3 | Fail-Closed | Wenn etwas nicht sicher geprüft werden kann: keine Freigabe, keine physische Ausführung, kontrollierter Abbruch oder Eskalation. | CHARTER §SR-10 |
| 4 | Seher schreibt niemals 🟥 | Der Seher (LLM-Komponente) darf niemals direkt rote Signale schreiben. Rote Signale dürfen nur durch deterministische Komponenten oder nach Sicherheitsprüfung entstehen. | CHARTER §SR-13 |
| 5 | Operational ≠ Scientific | Operationale Fehler erzeugen keine wissenschaftlichen Signale. | CHARTER §SR-08 |
| 6 | Questor ist kein Gremium-Rang | Questor darf nicht in Atlas oder Archiv schreiben. | CHARTER §SR-04 |

### §1.3 Was das Gremium DARF

| Erlaubt | Begründung |
| --- | --- |
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
| --- | --- |
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
| --- | --- | --- | --- |
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
- Prüft `abbruch_klasse`
- Trennt `abbruch_klasse`:
  - `OPERATIONAL` → kein wissenschaftliches Signal (→ CHARTER §SR-08)
  - `SCIENTIFIC` → Kristallkandidaten und Signale möglich
  - `SAFETY` → keine Kristalle und keine Signale aus dem Questor-Ergebnis (→ CHARTER §SR-19)
- Gibt Atlas-Hybrid-Referenzen als Pass-Through weiter:
  - `atlas_expectation_ref`
  - `objective_family_ref`
  - `frontier_candidate_ref`
- Übergibt Kristallkandidaten und Signalvorschläge an den Kartographen
- Darf `operational_metrics` in den `operational_event_log` übernehmen
- Darf bei SAFETY ein separates Sicherheits-Governance-Ereignis protokollieren
- Liest keine QuestorBlackbox (→ CHARTER §SR-07)

**Atlas-Hybrid-Sonderregeln:**

- Wenn `kristall_kandidaten` vorhanden sind, übergibt der Archivar sie zusammen mit:
  - `expectation_ref`
  - `confirms_expectation`
  - `evidence_class`
  - `metric_vector`
  - `evidence_quality`
  - `reproducibility_ref`
  sofern diese Felder im Kristallkandidaten vorhanden sind.
- Wenn `signale_fuer_atlas` vorhanden sind, übergibt der Archivar sie zusammen mit:
  - `evidence_kind`
  - `evidence_class`
  - `expectation_ref`
  - `observation_direction`
  - `is_diagnostic`
  - `is_policy`
  - `quality`
  - `validity`
  - `physical_time_s`
  - `node_ref`
  sofern diese Felder im SignalEvent vorhanden sind.
- Wenn `abbruch_klasse = OPERATIONAL`, dürfen keine wissenschaftlichen Atlas-Ereignisse erzeugt werden.
- Wenn `abbruch_klasse = SAFETY`, dürfen keine wissenschaftlichen Kristalle oder Signale aus dem Questor-Ergebnis erzeugt werden.
- Ein SAFETY-Ereignis darf nur als Sicherheits-Governance-Ereignis außerhalb der wissenschaftlichen Atlas-Energiekonten geführt werden.

**Verbote:**

- Keine Blackbox lesen
- Keine Questor-internen Trails interpretieren
- Keine operationalen Fehlerklassen als wissenschaftliche Signale behandeln
- Keine SAFETY-Abbrüche als wissenschaftliche Kristalle behandeln
- Keine direkte Atlas-Heilung ohne Kartograph oder Governance-Freigabe

---

### §3.2 Kartograph (Stufe 2)

**Verantwortung:** Strukturiert das Wissen im Atlas und führt das Atlas-Hybrid-System.

**Pflichten:**

- Zonen-Verwaltung (mit parent/child-Hierarchie)
- Cluster-Bildung (DBSCAN-basiert oder vergleichbar deterministisch)
- Signal-Verwaltung (🟥, 🟨, 🟪, 🟩, ⬜)
- Ableitung von `evidence_kind`, falls Questor oder Archivar ihn nicht final gesetzt hat
- Führung der Energiekonten:
  - `support_energy`
  - `conflict_energy`
  - `diagnostic_energy`
  - `policy_energy`
  - `coverage_energy`
- Berechnung von:
  - `evidence_mass`
  - `fracture_score`
  - `support_confidence`
  - `uncertainty_score`
  - `crystallization_progress`
- Kristallisationsprüfung
- Verwaltung von:
  - `AtlasNode`
  - `AtlasEdge`
  - `AtlasZoneSummary`
  - `TypedDimension`
  - `ZoneGeometry`
- Verarbeitung von `DiagnosticResolution`
- Verarbeitung von `SafetyConstraint`
- Verarbeitung von `ExclusionConstraint`
- Aktualisierung der `FrontierEngine`
- FULL_REBUILD (atomar)
- NEUAUSRICHTEN (inkrementell)

**Atlas-Hybrid-Pflichten:**

- Der Kartograph bestimmt die Zone oder Subzone für jedes wissenschaftliche Signal.
- Der Kartograph ordnet Signale bestehenden Knoten zu oder erzeugt neue Knoten.
- Der Kartograph erzeugt Kanten zwischen Knoten, wenn Evidenz dies rechtfertigt.
- Der Kartograph darf keine Kante ohne `evidence_refs` erzeugen.
- Der Kartograph darf keine Evidenz löschen.
- Der Kartograph darf bei DiagnosticResolution nur auditierte Gewichtsanpassungen vornehmen.
- Der Kartograph aktualisiert FrontierCandidates nach jeder relevanten Atlas-Änderung.
- Der Kartograph aktualisiert ResearchTopic-Zustände nur nach deterministischen Regeln.
- Der Kartograph darf keine Sicherheitsfreigaben ersetzen.

**Verbote:**

- Keine eigenmächtige Aufhebung von SafetyConstraints
- Keine eigenmächtige Auflösung von Quarantäne ohne DiagnosticResolution oder Governance-Freigabe
- Keine LLM-Endentscheidung über Atlas-Zustände
- Keine wissenschaftliche Interpretation von operationalen Fehlern

---

### §3.3 Kanzler (Stufe 3)

**Verantwortung:** Strategische Review und Realitäts-Check.

**Pflichten:**

- Lagebericht erstellen
- Weisungsprüfung
- SAFE_MODE verwalten
- Policy-Veto-Review durchführen
- Audit-Log führen
- Periodische Template-Zusammenfassung erhalten (G-8)

**Atlas-Hybrid-Pflichten:**

- Setzt oder bestätigt die `ExplorationPolicy`
- Bestätigt oder hebt `SafetyConstraints` auf, sofern autorisiert
- Prüft `DiagnosticResolution` mit outcome `EXPLAINS_CONTRADICTION` oder `RESOLVES_CONTRADICTION`
- Kann `ResearchTopic` priorisieren, blockieren oder archivieren
- Kann Zonen manuell auf `LOCKED` setzen
- Eskaliert an die menschliche Königin, wenn SAFE_MODE oder dauerhafte Sperren nötig sind

**Verbote:**

- Der Kanzler darf keine Sicherheitsfreigaben durch LLM ersetzen
- Der Kanzler darf die menschliche Königin nicht überstimmen (→ CHARTER §SR-11)
- Der Kanzler darf keine QuestorBlackbox lesen (→ CHARTER §SR-07)

---

### §3.4 Vordenker (Stufe 4)

**Verantwortung:** Erzeugt Roh-Ideen aus Atlas-Mustern.

**Pflichten:**

- Atlas-Muster analysieren
- Roh-Ideen generieren
- `prozess_skizze` mit Idee liefern (G-5)

**Atlas-Hybrid-Pflichten:**

- Nutzt `FrontierCandidate` als bevorzugte Quelle für neue Ideen
- Nutzt `ResearchTopic`, um Ideen thematisch einzuordnen
- Nutzt `AtlasZoneSummary`, um Zonenstatus und Quarantäne zu verstehen
- Nutzt `uncertainty_score`, um informationsreiche Regionen zu erkennen
- Nutzt `CONTRADICTION_GAP`, um Widerspruchslücken aufzulösen
- Nutzt `BRIDGE_FRONTIER`, um thematische Brücken zu schlagen
- Nutzt `DIAGNOSTIC_FRONTIER`, um Diagnose-Ideen vorzuschlagen
- Liefert zu jeder Idee eine `prozess_skizze`
- Wenn eine Idee eine Hypothese testet, liefert der Vordenker eine Erwartungsreferenz oder einen Erwartungsvorschlag

**Verbote:**

- Der Vordenker darf keine Wegmarken direkt platzieren
- Der Vordenker darf keine Sicherheitsfreigaben erteilen
- Der Vordenker darf keine FrontierCandidates eigenmächtig als ausführbar markieren

---

### §3.5 Pre-Filter (Stufe 5a)

**Verantwortung:** Deterministischer Fast-Path für offensichtliche Probleme.

**Pflichten:**

- Dimension-Freigabe prüfen
- Quarantäne-Zonen prüfen
- Sättigungs-Zustände prüfen

**Atlas-Hybrid-Pflichten:**

- Prüft `TypedDimension.approved`
- Prüft `ZoneGeometry` auf Gültigkeit
- Prüft aktive `SafetyConstraint`
- Prüft aktive `ExclusionConstraint`
- Prüft `AtlasZoneSummary.locked`
- Prüft `AtlasZoneSummary.quarantine_mode`
- Prüft `AtlasZoneSummary.full_rebuild_required`
- Prüft Verfügbarkeit von Diagnose-Budget bei Diagnose-Ideen
- Prüft, ob eine Idee in eine aktive Frontier passt
- Prüft, ob `atlas_expectation_ref` bei VALIDATE oder DIAGNOSE vorhanden ist oder deterministisch ergänzt werden kann
- Prüft Budget- und Capability-Hinweise, sofern vorhanden

**Fail-Closed-Regeln:**

- Wenn eine Dimension nicht freigegeben ist: Idee verwerfen
- Wenn eine Zone `LOCKED` ist: Idee verwerfen
- Wenn eine Zone `full_rebuild_required = true` hat: Idee verwerfen, außer autorisierte Recovery-/Diagnose-Aktion
- Wenn eine aktive harte `SafetyConstraint` vorhanden ist: Idee verwerfen
- Wenn eine Diagnose-Idee kein Diagnose-Budget hat: Idee verwerfen
- Wenn ein VALIDATE- oder DIAGNOSE-Vorschlag keine Erwartungsreferenz besitzt und keine deterministische Erwartung ableitbar ist: Idee verwerfen oder auf EXPLORE/COVERAGE reduzieren

**Verbote:**

- Der Pre-Filter darf keine LLM-Endentscheidung treffen
- Der Pre-Filter darf keine Sicherheitsfreigaben ersetzen
- Der Pre-Filter darf keine Wegmarke platzieren

---

### §3.6 Lotse (Stufe 5b)

**Verantwortung:** Ideen-Erdung und Wegmarken-Platzierung.

**Pflichten:**

- Wegmarken im Atlas platzieren
- Zustand: `IDEE_OFFEN` → `IDEE_GEPRÜFT` → `WEGMARKE_PLATZIERT`
- Nur in Weißraum oder bestätigten grünen Zonen

**Atlas-Hybrid-Pflichten:**

- Platziert Wegmarken bevorzugt auf Grundlage von `FrontierCandidate`
- Setzt `frontier_candidate_ref`, wenn die Wegmarke aus einer Frontier stammt
- Setzt `atlas_expectation_ref`, wenn eine Hypothese getestet wird
- Setzt Diagnose-Wegmarken nur bei vorhandenem Diagnose-Budget
- Erzeugt bei Diagnose-Wegmarken den erforderlichen Hinweis:
  - `objective_type = DIAGNOSE`
  - `required_gate_mode = FRACTURE_DIAGNOSIS`
- Dokumentiert die Zielgeometrie der Wegmarke über `ZoneGeometry`
- Vermeidet Wegmarken in:
  - `LOCKED`-Zonen
  - aktiven harten `SafetyConstraint`-Regionen
  - `ExclusionConstraint`-Regionen mit `hard_limit = true`
  - Zonen mit `full_rebuild_required = true`

**Verbote:**

- Der Lotse darf keine Sicherheitsfreigaben erteilen
- Der Lotse darf keine Pakete bauen
- Der Lotse darf keine Quarantäne eigenmächtig aufheben
- Der Lotse darf keine Wegmarke in einer gesperrten Frontier platzieren

---

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

**Atlas-Hybrid-Pflichten:**

- Setzt `atlas_expectation_ref` in das `ResearchPackage`, wenn eine Hypothese getestet wird
- Setzt `objective_family_ref`, wenn Multi-Objective-Forschung vorliegt
- Setzt `frontier_candidate_ref`, wenn die Wegmarke aus einer Frontier stammt
- Setzt `autonomy_level = STRICT`, wenn:
  - Diagnose vorliegt
  - Quarantäne vorliegt
  - FRACTURE_DIAGNOSIS erforderlich ist
  - Zone `DEGRADED` oder schlechter ist und keine normale Exploration erlaubt ist
- Setzt `required_gate_mode`-Hinweise bei Diagnose-Wegmarken
- Berücksichtigt `ResourceContext` aus FrontierCandidates
- Berücksichtigt `ExclusionConstraint` und `SafetyConstraint` beim Paketbau
- Darf keine Wegmarken in gesperrten Regionen in Pakete übersetzen

**Verbote:**

- Der Quartiermeister darf keine Gate-Freigaben vorwegnehmen
- Der Quartiermeister darf keine Leases vergeben
- Der Quartiermeister darf keine Sicherheitsfreigaben ersetzen
- Der Quartiermeister darf keine Atlas-Zustände eigenmächtig ändern

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

- → Siehe CHARTER §SR-13 für die LLM-Advisor-Regel.
- Der Seher ist eine LLM-Komponente
- Der Seher darf niemals direkt 🟥 schreiben (→ CHARTER §SR-13)
- Der Seher bewertet Evidenz und gibt `PASS`, `VETO` oder `TEMP_SUSPENDED` zurück
- Veto nur mit Evidenz
- Bei Veto ohne Evidenz: `SEHER_INVALID_VETO`

### §4.4 Circuit-Breaker (Zustandsmaschine)

**Verantwortung:** Überwacht Seher-Fehlerraten und setzt den Seher temporär aus.

**Zustände:**

| Zustand | Bedeutung |
| --- | --- |
| NORMAL | Seher arbeitet normal |
| SHADOW_MODE | Seher wird überwacht, aber seine Entscheidungen werden nicht direkt umgesetzt |
| TEMP_SUSPENDED | Seher ist temporär suspendiert |
| PERMANENT_SUSPENDED | Seher ist permanent suspendiert (nur manuelle Rückkehr) |

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
| --- | --- | --- |
| invalid_veto_rate > 0.3 | Alert an Kanzler | |
| false_block_rate > 0.5 | SHADOW_MODE | |
| appeal_success_rate > 0.7 | TEMP_SUSPENDED | |

**Hysterese und Rückkehr:**

Rückkehr nach `NORMAL` erfordert:

- Metrik liegt in zwei aufeinanderfolgenden Fenstern unter dem jeweiligen Schwellwert
- Manuelle Prüfung durch Kanzler oder dafür vorgesehenen Sicherheitsprozess
- Audit-Event für die Rückkehr

`PERMANENT_SUSPENDED`:

- Wird nur manuell durch Kanzler oder menschliche Königin ausgelöst
- Hat keine automatische Rückkehr
- Erfordert expliziten Audit-Trail

**Audit-Felder für Zustandswechsel:**

- `old_state`
- `new_state`
- `trigger`
- `metric_name`
- `metric_value`
- `window_size`
- `sample_size`
- `timestamp`
- `authority`

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

- `event_type`
- `zyklus_id`
- `policy_veto_id`
- `review_decision`
- `review_reason`
- `review_timestamp`
- `review_authority`
- `escalation_target`

### §4.7 Gate-Zustandsmaschine

→ Siehe CONTRACTS §7.4 für die vollständige Zustandsmaschine.

| Zustand | Bedeutung |
| --- | --- |
| GATE_PENDING | Paket wartet auf Sicherheitsprüfung |
| RICHTER_PRUEFT | Richter prüft deterministisch |
| SEHER_PRUEFT | Seher bewertet (wenn Richter PASS) |
| FREIGEGEBEN | Gate passiert (Richter PASS + Seher PASS) |
| DISPUTED | Berufung läuft (Richter PASS + Seher VETO) |
| ABGELEHNT | Gate nicht passiert |

**Übergänge:**

| Von | Nach | Auslöser |
| --- | --- | --- |
| GATE_PENDING | RICHTER_PRUEFT | Start |
| RICHTER_PRUEFT | ABGELEHNT | Richter FAIL |
| RICHTER_PRUEFT | SEHER_PRUEFT | Richter PASS |
| SEHER_PRUEFT | FREIGEGEBEN | Seher PASS |
| SEHER_PRUEFT | DISPUTED | Seher VETO (startet Appeal) |
| DISPUTED | FREIGEGEBEN | Appeal GRANTED |
| DISPUTED | ABGELEHNT | Appeal DENIED |

### §4.8 Gate-Modi

→ Siehe CONTRACTS §4.4 für den GateMode-Vertrag.

| Modus | Bedeutung |
| --- | --- |
| NORMAL | Standardbetrieb |
| FRACTURE_DIAGNOSIS | Diagnose bei hohem fracture_score |
| HIGH_RISK_OVERRIDE | Überschreibung mit positiver Widerlegung erforderlich |
| SANDBOX | Sandbox-Modus, keine physische Ausführung |

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

---

## §6 Atlas-Hybrid-System

### §6.1 Zweck

Der Atlas ist die wissenschaftliche Landkarte des Gremiums.

Er dient nicht nur der Ablage von Wissen, sondern ermöglicht:

- wissenschaftliche Orientierung,
- Erkennung von Wissenslücken,
- Bewertung von Widersprüchen,
- Isolation instabiler Wissensbereiche,
- gezielte Diagnose,
- autonome Auswahl sinnvoller nächster Forschungsschritte.

Der Atlas-Hybrid kombiniert:

1. Topologie
2. Evidenzdynamik
3. Integrität
4. Sicherheit und Governance
5. Zugang
6. Exploration

Alle Datenverträge dieses Abschnitts sind in `CONTRACTS.md §6.10` definiert.

**Regeln:**

- Questor schreibt nicht in den Atlas (→ CHARTER §SR-04)
- HAL schreibt nicht in den Atlas
- LLM-Komponenten dürfen beraten, aber nicht final über Atlas-Zustände entscheiden
- Operationale Fehler erzeugen keine wissenschaftlichen Signale (→ CHARTER §SR-08)
- Bei SAFETY-Abbruch sind Kristalle und Signale aus Questor leer (→ CHARTER §SR-19)
- Fail-Closed gilt bei allen unklaren Atlas-Zuständen (→ CHARTER §SR-10)

### §6.2 Referenzen

Dieser Abschnitt referenziert folgende Verträge:

- `CONTRACTS §6.10.1` EvidenceQuality
- `CONTRACTS §6.10.2` ValidityWindow
- `CONTRACTS §6.10.3` ReproducibilityContext
- `CONTRACTS §6.10.4` TypedDimension
- `CONTRACTS §6.10.5` ConditionalRule
- `CONTRACTS §6.10.6` ZoneGeometry
- `CONTRACTS §6.10.7` AtlasZoneSummary
- `CONTRACTS §6.10.8` AtlasNode
- `CONTRACTS §6.10.9` AtlasEdge
- `CONTRACTS §6.10.10` ObjectiveFamily
- `CONTRACTS §6.10.11` DiagnosticResolution
- `CONTRACTS §6.10.12` SafetyConstraint
- `CONTRACTS §6.10.13` ExclusionConstraint
- `CONTRACTS §6.10.14` FrontierCandidate
- `CONTRACTS §6.10.15` DiagnosticWaypoint
- `CONTRACTS §6.10.16` ResearchTopic
- `CONTRACTS §6.10.17` ExplorationPolicy
- `CONTRACTS §6.10.18` AtlasHybridConfig

### §6.3 Topologie

Der Atlas besteht aus:

- Dimensionen
- Zonen
- Subzonen
- Knoten
- Kanten
- Clustern

**Dimensionen:**

- Werden durch `TypedDimension` beschrieben
- Können kontinuierlich, diskret, kategorisch, ordinal oder conditional sein
- Müssen für physische Exploration freigegeben sein
- Neue Dimensionen unterliegen den bestehenden Approval-Regeln

**Zonen:**

- Werden durch `AtlasZoneSummary` beschrieben
- Besitzen eine `ZoneGeometry`
- Können kontinuierliche Grenzen und kategorische Constraints kombinieren
- Können parent/child-hierarchisch organisiert sein
- Können Subzonen enthalten

**Knoten:**

- Werden durch `AtlasNode` beschrieben
- Können sein:
  - `HYPOTHESIS`
  - `CRYSTAL`
  - `FRONTIER_ANCHOR`
  - `ZONE_ANCHOR`
  - `DIMENSION_REF`

**Kanten:**

- Werden durch `AtlasEdge` beschrieben
- Müssen `evidence_refs` besitzen
- Können sein:
  - `SUPPORTS`
  - `CONTRADICTS`
  - `EXTENDS`
  - `DEPENDS_ON`
  - `DERIVED_FROM`
  - `LOCATED_IN`
  - `MEASURES`
  - `EXPLAINS`
  - `DIAGNOSTIC_FOR`
  - `BLOCKED_BY`
  - `NEAR_FRONTIER`

**Cluster:**

- Gruppieren thematisch verwandte Zonen oder Knoten
- Werden deterministisch berechnet
- Diagnostic-Knoten mit `cluster_integration = false` fließen nicht in normale Cluster ein

### §6.4 Evidence-Semantik

Signale bleiben in den bestehenden Symbolen erhalten:

| Symbol | Name | Bedeutung |
| --- | --- | --- |
| 🟩 | GRÜN | Bestätigung |
| ⬜ | WEISS | Neutral / Coverage |
| 🟨 | GELB | Widerspruch |
| 🟪 | PURPUR | Diagnostik oder Policy |
| 🟥 | ROT | Sicherheitsrelevantes Ereignis / schwerer Konflikt |

Zusätzlich erhält jedes Signal eine Semantik über `evidence_kind`.

**Atlas-Hybrid-Semantik:**

| Signal | evidence_kind / Behandlung | Energiekonto |
| --- | --- | --- |
| 🟩 | `CONFIRMATION` | `support_energy` |
| ⬜ | `EXPLORATORY_COVERAGE` | `coverage_energy` |
| 🟨 | `CONTRADICTION` | `conflict_energy` |
| 🟪 diagnostic | `DIAGNOSTIC_CLARIFICATION` | `diagnostic_energy` |
| 🟪 policy | `POLICY_BLOCK` | `policy_energy` |
| 🟥 | Sicherheits-Governance + optional `conflict_energy` | zusätzlich `SafetyConstraint` prüfen |

**Regeln:**

- 🟩 darf nicht aus rein operationalen Fehlern entstehen.
- ⬜ darf nicht als Bestätigung gezählt werden.
- 🟨 entsteht, wenn eine Erwartung widerlegt wird oder ein wissenschaftlicher Widerspruch vorliegt.
- 🟪 diagnostic darf nicht automatisch als wissenschaftlicher Widerspruch gezählt werden.
- 🟪 policy ist Governance, kein automatischer wissenschaftlicher Widerspruch.
- 🟥 darf nicht durch eine LLM-Komponente erzeugt werden.
- 🟥 darf nicht durch Questor bei SAFETY-Abbruch erzeugt werden (→ CHARTER §SR-19).
- Wenn 🟥 durch einen autorisierten Sicherheitsprozess entsteht, muss der Kartograph zusätzlich einen `SafetyConstraint` prüfen oder aktualisieren.

### §6.5 Energiekonten und Scores

Für jede Zone und jeden Knoten führt der Kartograph Energiekonten.

**Energiekonten:**

```text
support_energy      = Summe aller effektiven Bestätigungsenergien
conflict_energy     = Summe aller effektiven Widerspruchsenergien
diagnostic_energy   = Summe aller effektiven diagnostischen Energien
policy_energy       = Summe aller effektiven Policy-Energien
coverage_energy     = Summe aller effektiven Coverage-Energien

evidence_mass       = support_energy + conflict_energy
```

**Effektive Signalwirkung:**

```text
effective_weight(signal) =
      base_weight(signal)
    × konfidenz(signal)
    × decay(age_cycles)
```

**Decay:**

```text
decay(age_cycles) = exp(-signal_decay_lambda × age_cycles)
```

**Default-Signalgewichte:**

| Signal | support_base | conflict_base | diagnostic_base | policy_base | coverage_base |
| --- | ---: | ---: | ---: | ---: | ---: |
| 🟩 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 |
| ⬜ | 0.00 | 0.00 | 0.00 | 0.00 | 0.10 |
| 🟨 | 0.00 | 0.60 | 0.00 | 0.00 | 0.00 |
| 🟥 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 |
| 🟪 diagnostic | 0.00 | 0.00 | 0.30 | 0.00 | 0.00 |
| 🟪 policy | 0.00 | 0.00 | 0.00 | 0.30 | 0.00 |

Diese Gewichte sind deterministische Defaults.
Sie können über die Atlas-Konfiguration angepasst werden, sofern keine CHARTER-Regel verletzt wird.

**Fracture-Score:**

```text
Wenn evidence_mass < min_evidence_mass:
    fracture_score = None
Sonst:
    fracture_score =
        conflict_energy
        /
        (support_energy + conflict_energy + epsilon)
```

**Support-Confidence:**

```text
support_confidence =
    support_energy
    /
    (support_energy + k_conf)
```

**Uncertainty-Score:**

```text
Wenn evidence_mass == 0:
    uncertainty_score = 1.0
Sonst:
    uncertainty_score =
          exp(-evidence_mass / k_evidence)
        × (0.5 + 0.5 × variance_factor)
```

**Bedeutung:**

- `fracture_score` misst Widersprüchlichkeit.
- `support_confidence` misst bestätigende Evidenz.
- `uncertainty_score` misst Ungewissheit und Informationspotenzial.
- `coverage_energy` misst Erkundung ohne Bestätigung oder Widerspruch.

### §6.6 Zone-Health und Quarantäne

Zonen haben einen Zustand und zusätzliche Modi.

**Zustände:**

```text
UNEXPLORED
EXPLORED_INCONCLUSIVE
HEALTHY
DEGRADED
CRITICAL
LOCKED
```

**Modi:**

```text
quarantine_mode: bool
full_rebuild_required: bool
locked: bool
```

**Regeln:**

```text
Wenn locked == true:
    zone_state = LOCKED

Wenn full_rebuild_required == true:
    zone_state = CRITICAL
    quarantine_mode = true

Wenn evidence_mass < min_evidence_mass:
    Wenn coverage_energy > 0:
        zone_state = EXPLORED_INCONCLUSIVE
    Sonst:
        zone_state = UNEXPLORED

Wenn fracture_score >= full_rebuild_threshold:
    zone_state = CRITICAL
    full_rebuild_required = true
    quarantine_mode = true

Wenn fracture_score >= quarantine_threshold:
    zone_state = DEGRADED
    quarantine_mode = true

Wenn fracture_score >= degraded_threshold:
    zone_state = DEGRADED

Wenn fracture_score < degraded_threshold
und support_confidence >= healthy_support_confidence:
    zone_state = HEALTHY

Sonst:
    zone_state = EXPLORED_INCONCLUSIVE
```

**Quarantäne-Modus:**

```text
Wenn quarantine_mode == true:
    normale Exploration ist verboten
    normale Optimierung ist verboten
    VALIDATE ist nur eingeschränkt nach Freigabe erlaubt
    DIAGNOSE ist erlaubt, wenn Diagnose-Budget vorhanden ist
```

**LOCKED:**

```text
Wenn locked == true:
    keine normale Frontier
    keine normale Exploration
    nur Audit, Diagnose oder autorisierte Governance-Aktionen
```

Eine leere Zone ist niemals automatisch `HEALTHY`.

### §6.7 Kristallisation

Kristallisation ist der Übergang von einer Hypothese zu einem Kristall.

**Kristallisationsfortschritt:**

```text
crystallization_progress =
    support_energy
    /
    crystallization_threshold
```

Kristallisation erfolgt nur, wenn alle folgenden Bedingungen erfüllt sind:

```text
1. Der Knoten ist eine Hypothese.
2. crystallization_progress >= 1.0
3. Mindestens `min_confirmations` relevante Bestätigungen liegen vor.
4. fracture_score < max_fracture_for_crystallization
5. Kein starkes 🟨- oder 🟥-Ereignis innerhalb der `interrupt_window`
6. Die Zone ist nicht `LOCKED`
7. Die Zone ist nicht in `quarantine_mode`, außer Diagnose ist explizit freigegeben
8. Keine aktive Policy-Blockade verhindert die Kristallisation
9. Die Evidence-Class-Transferregeln sind erfüllt
```

**Evidence-Class-Transferregel:**

```text
Wenn evidence_class = SIMULATION oder SANDBOX:
    darf kein physischer Kristall ohne physische Validierung erzeugt werden.
```

Kristallisation erzeugt:

- einen `AtlasNode` mit `node_type = CRYSTAL`
- mindestens eine `LOCATED_IN`-Kante zur Zone
- optional `SUPPORTS`, `EXTENDS` oder `DERIVED_FROM`-Kanten
- einen Audit-Eintrag

Kristalle sind persistent, können aber durch neue Evidenz herausgefordert werden.

### §6.8 DiagnosticResolution

Diagnostik kann Widersprüche bestätigen, erklären oder auflösen.

Der Kartograph verarbeitet `DiagnosticResolution`.

**Outcomes:**

| Outcome | Bedeutung |
| --- | --- |
| `CONFIRMS_CONTRADICTION` | Diagnose bestätigt den Widerspruch |
| `EXPLAINS_CONTRADICTION` | Diagnose erklärt die Ursache des Widerspruchs |
| `RESOLVES_CONTRADICTION` | Diagnose löst den Widerspruch auf |
| `INCONCLUSIVE` | Diagnose ist unklar |

**Regeln:**

```text
CONFIRMS_CONTRADICTION:
    fracture_score bleibt relevant
    Quarantäne bleibt bestehen oder wird verschärft

EXPLAINS_CONTRADICTION:
    betroffene conflict_energy darf auditiert reduziert werden
    keine Löschung von Evidenz
    Audit-Event erforderlich
    review_authority erforderlich

RESOLVES_CONTRADICTION:
    Quarantäne darf nur mit Governance-Freigabe aufgehoben werden
    betroffene Knoten können neu bewertet werden
    Audit-Event erforderlich
    review_authority erforderlich

INCONCLUSIVE:
    keine automatische Heilung
    uncertainty_score bleibt relevant
```

**Diagnostic-Kristalle:**

```text
ist_diagnostic = true
cluster_integration = false
```

Diagnostic-Kristalle fließen nicht in normale Cluster-Berechnungen ein.

### §6.9 SafetyConstraint und ExclusionConstraint

**SafetyConstraint:**

- Wird durch `SafetyConstraint` beschrieben
- Ist persistent
- Hat keinen automatischen Decay
- Kann nur durch autorisierte Governance aufgehoben werden
- Überschreibt Frontier-Freigaben

**Regeln:**

```text
Wenn SafetyConstraint.active == true:
    frontier_score für betroffene Region = 0
    keine normale Exploration
    nur Audit, Diagnose oder autorisierte Freigabe
```

**ExclusionConstraint:**

- Wird durch `ExclusionConstraint` beschrieben
- Kann negativ gelerntes Wissen repräsentieren
- Kann harte oder weiche Grenzen darstellen

**Regeln:**

```text
Wenn hard_limit == true:
    Region darf nicht normal exploriert werden

Wenn hard_limit == false:
    Region darf nur mit erhöhter Vorsicht oder Diagnostik betreten werden
```

Beide Constraint-Typen müssen `evidence_refs` oder `source_event_ref` besitzen.

### §6.10 FrontierEngine

Die FrontierEngine findet sinnvolle nächste Forschungsziele.

Sie ist keine Ausführungsinstanz.

Sie erzeugt nur:

```text
FrontierCandidate
```

**Trigger:**

```text
Nach jedem neuen wissenschaftlichen Signal
Nach jeder Kristallisation
Nach jeder DiagnosticResolution
Nach jedem FULL_REBUILD
Nach jeder relevanten Zone-Health-Änderung
Nach jeder ResearchTopic-Änderung
Periodisch gemäß ExplorationPolicy
```

**Harte Filter:**

```text
Ausschluss, wenn:
- Zone LOCKED ist
- aktive harte SafetyConstraint vorhanden ist
- Zone full_rebuild_required = true hat
- Dimension nicht freigegeben ist
- ZoneGeometry ungültig ist
- Quarantäne ohne Diagnose-Budget vorliegt
- keine passende Capability erkennbar ist
- Policy-Veto aktiv ist
- FrontierCandidate gegen ExclusionConstraint verstößt
```

**Frontier-Score:**

```text
frontier_score =
      safety_factor
    × (
          w_novelty        × novelty_score
        + w_promise        × promise_score
        + w_information    × information_gain_score
        + w_connectivity   × connectivity_score
        + w_cluster        × cluster_relevance_score
      )
    −  w_cost            × estimated_cost
    −  w_risk            × risk_score
```

**`safety_factor`:**

```text
BLOCKED    = 0.0
RESTRICTED = 0.5
CLEAR      = 1.0
```

FrontierCandidates müssen enthalten:

- Zielzone oder Zielgeometrie
- Frontier-Typ
- Scores
- ResourceContext
- SafetyStatus
- strukturierte Begründung
- vorgeschlagenen Objective-Type
- vorgeschlagenen Gate-Mode

FrontierCandidates sind Empfehlungen.

Sie ersetzen nicht:

- Pre-Filter
- Lotse
- Quartiermeister
- Sicherheits-Gate
- Lease
- Questor-Validierung

### §6.11 ResearchTopic und ExplorationPolicy

**ResearchTopic:**

- Wird durch `ResearchTopic` beschrieben
- Kann `PROPOSED`, `ACTIVE`, `SATURATED`, `BLOCKED` oder `ARCHIVED` sein
- Kann mit Zonen, Clustern, Dimensionen und ObjectiveFamily verbunden sein

**Topic-Zustände:**

```text
PROPOSED:
    Thema ist vorgeschlagen

ACTIVE:
    Thema ist freigegeben und wird bearbeitet

SATURATED:
    Keine relevanten Frontiers über Threshold
    oder Stop-Bedingungen erfüllt

BLOCKED:
    Quarantäne, SafetyConstraint, Policy-Veto oder Budget-Blockade

ARCHIVED:
    Thema abgeschlossen oder beendet
```

**ExplorationPolicy:**

- Wird durch `ExplorationPolicy` beschrieben
- Steuert das Verhältnis von Exploitation, Exploration und Diagnostik
- Wird durch Kanzler, Königin oder autorisierten Governance-Prozess gesetzt
- darf nicht durch LLM final entschieden werden

**Regeln:**

```text
Die FrontierEngine verwendet die ExplorationPolicy deterministisch.
Die ExplorationPolicy darf keine Sicherheitsregeln überschreiben.
```

### §6.12 Zugriffsmatrix

| Komponente | Atlas lesen | Atlas schreiben | EvidenceEvents erzeugen | SafetyConstraint freigeben |
| --- | ---: | ---: | ---: | ---: |
| Archivar | ✅ | ❌ | ✅ via Übergabe | ❌ |
| Kartograph | ✅ | ✅ | ✅ abgeleitet | ❌ |
| Kanzler | ✅ | ❌ | ❌ | ✅ |
| Königin | ✅ | ❌ | ❌ | ✅ |
| Vordenker | ✅ | ❌ | ❌ | ❌ |
| Pre-Filter | ✅ | ❌ | ❌ | ❌ |
| Lotse | ✅ | ✅ Wegmarken | ❌ | ❌ |
| Quartiermeister | ✅ | ❌ | ❌ | ❌ |
| Richter | ✅ | ❌ | ❌ | ❌ |
| Seher | ✅ eingeschränkt | ❌ | ❌ niemals 🟥 | ❌ |
| Dispatcher | ✅ | ❌ | ❌ | ❌ |
| Receiver | ❌ | ❌ | ❌ | ❌ |
| Questor | ❌ | ❌ | ❌ | ❌ |
| HAL | ❌ | ❌ | ❌ | ❌ |

**Regeln:**

- Questor schreibt niemals in den Atlas (→ CHARTER §SR-04)
- HAL schreibt niemals in den Atlas
- Seher schreibt niemals 🟥 (→ CHARTER §SR-13)
- Sicherheitsfreigaben erfolgen nur durch autorisierte Governance-Prozesse

### §6.13 FULL_REBUILD, NEUAUSRICHTEN und Atlas-Versionierung

**FULL_REBUILD:**

```text
Wenn full_rebuild_required == true:
    FULL_REBUILD wird vorbereitet
```

**Regeln:**

- FULL_REBUILD ist atomar
- Alte Atlas-Version bleibt für laufende Quests gültig
- Neuer `atlas_head_pointer` gilt nur für neue Pakete
- Keine Invalidierung laufender Quests

**NEUAUSRICHTEN:**

- Inkrementelle Anpassung betroffener Zonen
- Minimale Unterbrechung
- Nur wenn kein FULL_REBUILD erforderlich ist

**Atlas-Versionierung:**

```text
atlas_version_ref: str
```

**Regeln:**

- Questor empfängt `atlas_version_ref` als Pass-Through
- Questor setzt `observed_atlas_version_id = atlas_version_ref`
- Questor darf `atlas_version_ref` nicht interpretieren
- Questor darf `atlas_version_ref` nicht ändern
- Questor darf `atlas_version_ref` nicht einem LLM übergeben
- → CHARTER §SR-15

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
| --- | --- | --- |
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
| --- | --- | --- |
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
| --- | --- | --- |
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
| --- | --- | --- |
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
| Atlas-Hybrid | Evidenzbasierte, semantische und explorationsfähige Wissenschaftskarte | §6 |
| Evidence-Semantik | Signale werden über evidence_kind interpretiert | §6.4 |
| Energiekonten | Support, Conflict, Diagnostic, Policy, Coverage | §6.5 |
| FrontierEngine | Erzeugt FrontierCandidates, keine Ausführung | §6.10 |
| ResearchTopic | Themenautonomie mit Zustandsmaschine | §6.11 |
| SafetyConstraint | Persistent, kein Decay, manuelle Freigabe | §6.9 |
| DiagnosticResolution | Kann Widersprüche erklären oder auflösen | §6.8 |
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

---

## Anhang A: Korrekturhinweis für alte GREMIUM.md-Stellen

Die folgenden alten Annahmen werden durch den Änderungsantrag `ATLAS-HYB-1.0.0` korrigiert oder präzisiert:

| # | Alte Annahme | Korrektur | Quelle |
|---:|---|---|---|
| 1 | `SAFETY → Sicherheits-Signal` | Bei SAFETY-Abbruch sind Kristalle und Signale aus Questor leer. Ein separates Sicherheits-Governance-Ereignis ist erlaubt. | CHARTER §SR-19 |
| 2 | Signal-Resolution nur nach Priorität | Signal-Resolution wird durch Energiekonten und Evidence-Semantik ergänzt. Priorität bleibt nur für Safety-Override relevant. | §6.4, §6.5 |
| 3 | Kristallisation nach 3 Bestätigungen | Kristallisation nutzt `crystallization_progress`, Mindestbestätigungen, Fracture-Grenze und Interrupt-Window. | §6.7 |
| 4 | `fracture_score` primär aus roten Signalen | `fracture_score` wird aus `conflict_energy` und `support_energy` berechnet. | §6.5 |
| 5 | Zone-Health: `HEALTHY < 0.3`, `DEGRADED < 0.7`, `CRITICAL >= 0.7` | Zone-Health nutzt `degraded_threshold`, `quarantine_threshold`, `full_rebuild_threshold`, `UNEXPLORED`, `EXPLORED_INCONCLUSIVE` und `LOCKED`. | §6.6 |
| 6 | Weiß ist neutral, aber ohne Funktion | Weiß erzeugt `coverage_energy` und kann `EXPLORED_INCONCLUSIVE` unterstützen. | §6.4, §6.5, §6.6 |
| 7 | Leere Zone kann implizit als gesund gelten | Leere Zone ist `UNEXPLORED` oder `EXPLORED_INCONCLUSIVE`, niemals automatisch `HEALTHY`. | §6.6 |

---

## Anhang B: Akzeptanzprüfung für ATLAS-HYB-1.0.0

Nach dem Einfügen dieser Änderungen sollte `GREMIUM.md` folgende Kriterien erfüllen:

| # | Kriterium | Status |
|---:|---|---|
| 1 | Kopfzeile enthält Version `1.1.0-atlas-hyb.1` | ☐ |
| 2 | `§0.1 Änderungsantrag ATLAS-HYB-1.0.0` ist vorhanden | ☐ |
| 3 | Archivar ist auf Atlas-Hybrid aktualisiert | ☐ |
| 4 | Archivar behandelt SAFETY gemäß `CHARTER §SR-19` | ☐ |
| 5 | Kartograph ist auf Atlas-Hybrid aktualisiert | ☐ |
| 6 | Kartograph führt Energiekonten | ☐ |
| 7 | Kartograph aktualisiert FrontierEngine | ☐ |
| 8 | Kanzler verwaltet ExplorationPolicy und Safety-Freigaben | ☐ |
| 9 | Vordenker nutzt FrontierCandidates | ☐ |
| 10 | Pre-Filter prüft SafetyConstraints und ExclusionConstraints | ☐ |
| 11 | Lotse setzt Erwartungsreferenzen und Diagnose-Wegmarken | ☐ |
| 12 | Quartiermeister setzt Atlas-Hybrid-Referenzen | ☐ |
| 13 | `§6 Atlas-Hybrid-System` ersetzt das alte Atlas-Signal-System | ☐ |
| 14 | Energy-Formeln sind dokumentiert | ☐ |
| 15 | Zone-Health enthält `UNEXPLORED` und `EXPLORED_INCONCLUSIVE` | ☐ |
| 16 | Quarantäne ist als Modus beschrieben | ☐ |
| 17 | DiagnosticResolution ist beschrieben | ☐ |
| 18 | SafetyConstraint ist persistent und blockierend | ☐ |
| 19 | FrontierEngine erzeugt nur Empfehlungen | ☐ |
| 20 | ResearchTopic und ExplorationPolicy sind beschrieben | ☐ |
| 21 | Zugriffsmatrix enthält Questor ohne Atlas-Schreibrecht | ☐ |
| 22 | Zugriffsmatrix enthält HAL ohne Atlas-Schreibrecht | ☐ |
| 23 | Zugriffsmatrix enthält Seher ohne rote Signale | ☐ |
| 24 | Keine neuen Datenverträge wurden definiert | ☐ |
| 25 | Keine neuen Sicherheitsregeln wurden definiert | ☐ |
| 26 | CHARTER-Hierarchie bleibt gewahrt | ☐ |

---