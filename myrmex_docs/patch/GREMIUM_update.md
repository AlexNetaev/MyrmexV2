# 📄 GREMIUM.md v2.0.0 — ÄNDERUNGSANWEISUNG (Schritt 3)

**Aktion:** Die folgenden Änderungen sind in die bestehende `specs/GREMIUM.md` (v1.1.0-atlas-hyb.1) einzuarbeiten. Das Ergebnis ist Version **2.0.0-strat.1**.

**Grundprinzip:** GREMIUM.md behält die **Pipeline-Mechanik** (WIE läuft ein Zyklus ab). Die **strategische Steuerung** (WER entscheidet WAS) lebt jetzt in `GREMIUM_STRATEGY.md`.

---

## ÄNDERUNG 1: Kopfzeile

**ERSETZE** die bestehende Kopfzeile:

| Feld | Wert |
|---|---|
| Dateiname | specs/GREMIUM.md |
| Version | **2.0.0-strat.1** |
| Status | BINDEND — Pipeline-Mechanik (Strategie in GREMIUM_STRATEGY.md) |
| System | MYRMEX v2.4.0 + Questor v0.2.3 + HAL v0.2.0 |
| Schicht | Layer 1 (specs/) — referenziert foundation/ |
| Begleitdokument | **specs/GREMIUM_STRATEGY.md v1.0.0** (Strategie & Achsen) |
| Datum | 21. August 2026 |

---

## ÄNDERUNG 2: Neuer Abschnitt §0.2 (nach §0.1 einfügen)

**NEU — nach §0.1 einfügen:**

### §0.2 Beziehung zu GREMIUM_STRATEGY.md

Dieses Dokument definiert die **Pipeline-Mechanik** des Gremiums:
- 9-Stufen-Pipeline (Archivar → Kartograph → Vordenker → Lotse → Quartiermeister → Sicherheitsrat → Dispatcher → Questor → Receiver)
- Sicherheitsrat (Richter, Seher, Circuit-Breaker)
- Pipeline-Orchestrator (Bounded Queues, Deadlock-Erkennung)
- Atlas-Hybrid-System (Energiekonten, Kristallisation, Fractures, FrontierEngine)
- Event-Driven Architecture

`specs/GREMIUM_STRATEGY.md` definiert die **strategische Steuerung**:
- Kanzler & Königin (Briefing-Zyklus, StrategicDirective)
- 4-Achsen-Architektur (Safety, Resource, Research, Governance)
- ControlState und atomare Transitionen (SL-AX-ATOMIC)
- Intent-Verfügbarkeit und Blocklists
- Closure-Regeln (CT-1..CT-10)
- Symptom-Trigger und Vordenker-Ansteuerung

**Konfliktregel zwischen beiden Dokumenten:**
- CHARTER > CONTRACTS > GREMIUM_STRATEGY.md > GREMIUM.md
- Bei Konflikten in der Pipeline-Mechanik: GREMIUM.md ist autoritativ.
- Bei Konflikten in der Strategie/Achsen-Steuerung: GREMIUM_STRATEGY.md ist autoritativ.

---

## ÄNDERUNG 3: §1.1 aktualisieren (Architektur-Übersicht)

**ERSETZE** das Architektur-Diagramm in §1.1:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SCHICHT 5: 👑 KÖNIGIN                        │
│  Langfristige Vision, Meta-Ziele, menschliche Führung           │
│  → Strategische Steuerung: GREMIUM_STRATEGY.md §2, §3          │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                    SCHICHT 4: 🏛️ GREMIUM                         │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  STRATEGISCHE STEUERUNG (→ GREMIUM_STRATEGY.md)          │   │
│  │  Kanzler · Briefing · 4-Achsen · ControlState · DTT      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  PIPELINE-MECHANIK (→ dieses Dokument)                   │   │
│  │  9-Stufen-Pipeline · Sicherheitsrat · Orchestrator        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  ATLAS-HYBRID-SYSTEM                                     │   │
│  │  Evidence-Semantik · Energiekonten · Kristallisation      │   │
│  │  FrontierEngine · ResearchTopics · ExplorationPolicy      │   │
│  │  Digital-Twin-Loop (§6.14)                                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│              SCHICHT 3: ⚖️ DISPATCH-KOORDINATION                  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│              SCHICHT 2: 🧭 QUESTOR                               │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│              SCHICHT 1: 🔌 HAL & RESOURCE GOVERNOR               │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│              SCHICHT 0: ⚙️ PHYSIS / COMPUTE                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## ÄNDERUNG 4: Neuer Abschnitt §6.14 — Digital-Twin-Loop

**NEU — nach §6.13 einfügen:**

### §6.14 Digital-Twin-Loop

Dieser Abschnitt definiert die Integration des Digital-Twin-Systems in die Pipeline-Mechanik des Gremiums. Die strategische Steuerung des Twin-Loops (Twin-Drift-Erkennung, Kalibrierungs-Anforderung) ist in `GREMIUM_STRATEGY.md §14` (SL-TWIN-1..11) definiert.

#### §6.14.1 Zweck

Der Digital-Twin-Loop ermöglicht:
- Vergleich von Simulations-Ergebnissen mit Real-Experimenten
- Erkennung von Modell-Drift (Sim-weicht-von-Real-ab)
- Automatische Kalibrierung des Twin-Modells
- Validierung der Modell-Güte über die Zeit

#### §6.14.2 Verträge

Die Datenverträge für den Digital-Twin-Loop sind in `CONTRACTS.md §6.10.19` und `§6.10.20` definiert:
- `DigitalTwinModel` (CONTRACTS §6.10.19)
- `TwinDivergenceReport` (CONTRACTS §6.10.20)

Erweiterungen bestehender Verträge:
- `ResearchPackage.digital_twin_ref` (CONTRACTS §1.1)
- `ReproducibilityContext.digital_twin_ref` (CONTRACTS §6.10.3)
- `AtlasNode.twin_model` (CONTRACTS §6.10.8)
- `DiagnosticResolution.twin_divergence_report_ref` (CONTRACTS §6.10.11)

#### §6.14.3 Sim-Kristall vs. Real-Kristall

| Typ | evidence_class | Erlaubte Knoten-Aktualisierung |
|---|---|---|
| Sim-Kristall | SIMULATION oder SANDBOX | Darf **nur** DIGITAL_TWIN-Knoten aktualisieren. Darf **niemals** einen CRYSTAL-Knoten erzeugen. |
| Real-Kristall | PHYSICAL_EXPERIMENT | Darf CRYSTAL, HYPOTHESIS und DIGITAL_TWIN-Knoten aktualisieren. |
| Kalibrierungs-Kristall | COMPUTE_EVALUATION | Darf **nur** DIGITAL_TWIN-Knoten aktualisieren (neue Parameter, drift_score senken). |

#### §6.14.4 Divergenz-Berechnung (Kartograph)

Der Kartograph berechnet den `TwinDivergenceReport`, wenn er zwei Kristallkandidaten mit demselben `objective_family_ref` und demselben `digital_twin_ref` empfängt:

```
1. Extrahiere metric_vector aus Sim-Kristall und Real-Kristall.
2. Berechne pro Metrik die relative Abweichung:
   dev = abs(sim - real) / max(abs(real), epsilon)
3. overall_divergence_score = mean(dev) über alle gemeinsamen Metriken.
4. Wenn overall_divergence_score > twin_model.divergence_threshold:
   → tolerance_breached = true
   → calibration_required = true
   → Erhöhe den drift_score des Twin-Knotens.
   → Erzeuge SymptomEvent(TWIN_DRIFT) an den Strategischen Layer.
```

#### §6.14.5 Kalibrierungs-Loop

Wenn `calibration_required = true`:

```
1. FrontierEngine erzeugt FrontierCandidate:
   - frontier_type = DIAGNOSTIC_FRONTIER
   - suggested_objective_type = DIAGNOSE
   - suggested_gate_mode = FRACTURE_DIAGNOSIS
   - digital_twin_ref = twin_node_ref

2. Quartiermeister baut ResearchPackage:
   - objective_type = DIAGNOSE
   - digital_twin_ref = twin_node_ref
   - security_mode = SANDBOX oder DEV_SANDBOX_ONLY
     (Kalibrierung ist Compute, keine Physik!)

3. Questor führt Kalibrierungs-Lauf aus.

4. Kartograph aktualisiert DIGITAL_TWIN-Knoten:
   - model_version wird erhöht.
   - drift_score wird reduziert.
   - last_calibration_at wird aktualisiert.
   - DiagnosticResolution.outcome = TWIN_CALIBRATED.
```

#### §6.14.6 Validity-Regeln

- Ein DIGITAL_TWIN-Knoten mit `drift_score > divergence_threshold` wird als DEGRADED markiert.
- Ein DIGITAL_TWIN-Knoten in `quarantine_mode` darf nur für DIAGNOSE (Kalibrierung) verwendet werden.
- Wenn `validity.valid_until` abgelaufen ist, wird der Twin automatisch als DEGRADED markiert.

#### §6.14.7 Pipeline-Integration

| Pipeline-Stufe | Digital-Twin-Aktion |
|---|---|
| Archivar (Stufe 1) | Übergibt `digital_twin_ref` und `twin_model_version` aus `ReproducibilityContext` an Kartograph |
| Kartograph (Stufe 2) | Berechnet TwinDivergenceReport, aktualisiert drift_score, erzeugt SymptomEvent(TWIN_DRIFT) |
| Vordenker (Stufe 4) | Erhält TWIN_DRIFT-Symptom, schlägt Kalibrierungs-Hypothese vor |
| Lotse (Stufe 5b) | Platziert Diagnose-Wegmarke mit `digital_twin_ref` |
| Quartiermeister (Stufe 6) | Baut SANDBOX-Paket für Kalibrierung |
| Sicherheitsrat (Stufe 7) | Prüft Kalibrierungs-Paket (gate_mode = FRACTURE_DIAGNOSIS) |
| Dispatcher (Stufe 8) | Sendet Kalibrierungs-Paket an Questor |

#### §6.14.8 Sicherheitsregeln

- Questor darf `digital_twin_ref` nicht als LLM-Kontext verwenden (→ CHARTER §SR-24).
- Questor darf den Twin nicht eigenmächtig kalibrieren.
- Kalibrierung erfolgt ausschließlich über den definierten Pipeline-Pfad.
- Sim-Evidenz darf keine physischen Kristalle bestätigen (→ CHARTER §SR-08, GREMIUM §6.7 Evidence-Class-Transferregel).

---

## ÄNDERUNG 5: §3.2 Kartograph erweitern (Digital-Twin-Pflichten)

**ERGÄNZE** am Ende der Kartograph-Pflichten in §3.2:

```
Digital-Twin-Pflichten:
- Vergleicht Sim-Kristalle mit Real-Kristallen (gleicher digital_twin_ref)
- Berechnet TwinDivergenceReport deterministisch
- Aktualisiert drift_score des DIGITAL_TWIN-Knotens
- Erzeugt SymptomEvent(TWIN_DRIFT) bei tolerance_breached
- Verarbeitet DiagnosticResolution mit outcome = TWIN_CALIBRATED
- Markiert DIGITAL_TWIN-Knoten als DEGRADED bei drift_score > threshold
- Prüft ValidityWindow des Twin-Modells
```

---

## ÄNDERUNG 6: §3.4 Vordenker erweitern (Digital-Twin-Pflichten)

**ERGÄNZE** am Ende der Vordenker-Pflichten in §3.4:

```
Digital-Twin-Pflichten:
- Erhält SymptomEvent(TWIN_DRIFT) bei Modell-Drift
- Schlägt Kalibrierungs-Hypothesen vor
- Nutzt TwinStatusSummary im Briefing für Drift-Erkennung
- Liefert Schatten-Variablen-Check bei TWIN_DRIFT (§6.14.4)
```

---

## ÄNDERUNG 7: §14 Dokumentenhierarchie aktualisieren

**ERSETZE** den bestehenden Text in §14:

### §14 Dokumentenhierarchie

Dieses Dokument steht in der Schicht `specs/` und referenziert:
- `foundation/CHARTER.md` für Sicherheitsregeln (CHARTER §SR-XX)
- `foundation/CONTRACTS.md` für Datenverträge (CONTRACTS §X.X)
- `specs/QUESTOR.md` für Questor-spezifische Details
- `specs/HAL.md` für HAL-spezifische Details
- **`specs/GREMIUM_STRATEGY.md` für strategische Steuerung (Achsen, ControlState, Kanzler/Königin)**

Regel: Änderungen an Gremium-Modulen in diesem Dokument erfordern eine Versionsänderung und eine Überprüfung der referenzierten Dokumente.

**Aufteilung zwischen GREMIUM.md und GREMIUM_STRATEGY.md:**

| Thema | GREMIUM.md (dieses Dokument) | GREMIUM_STRATEGY.md |
|---|---|---|
| 9-Stufen-Pipeline | ✅ | — |
| Sicherheitsrat (Richter/Seher) | ✅ | — |
| Pipeline-Orchestrator | ✅ | — |
| Atlas-Hybrid-System | ✅ | — |
| Digital-Twin-Loop (Pipeline) | ✅ (§6.14) | Strategie (§14) |
| Event-Driven Architecture | ✅ | — |
| Kanzler & Königin | — | ✅ |
| Briefing-Zyklus | — | ✅ |
| 4-Achsen-Architektur | — | ✅ |
| ControlState & SL-AX-ATOMIC | — | ✅ |
| Intent-Verfügbarkeit | — | ✅ |
| Closure-Regeln (CT-1..CT-10) | — | ✅ |
| Symptom-Trigger | — | ✅ |
| DTT (DirectiveTranslationTable) | — | ✅ |

---

## ÄNDERUNG 8: §13 Zusammenfassung erweitern

**ERGÄNZE** am Ende der Tabelle in §13:

| Thema | Entscheidung | Quelle |
|---|---|---|
| Strategische Steuerung | In GREMIUM_STRATEGY.md ausgelagert | §0.2 |
| Digital-Twin-Loop | Pipeline-Integration in §6.14, Strategie in GREMIUM_STRATEGY.md §14 | §6.14 |
| 4-Achsen-Architektur | In GREMIUM_STRATEGY.md definiert | §0.2 |

---

## ÄNDERUNG 9: Anhang B aktualisieren (Akzeptanzprüfung)

**ERGÄNZE** am Ende der Tabelle in Anhang B:

| # | Kriterium | Status |
|---|---|---|
| 27 | §0.2 Referenz auf GREMIUM_STRATEGY.md ist vorhanden | ☐ |
| 28 | §6.14 Digital-Twin-Loop ist definiert | ☐ |
| 29 | §3.2 Kartograph enthält Digital-Twin-Pflichten | ☐ |
| 30 | §3.4 Vordenker enthält Digital-Twin-Pflichten | ☐ |
| 31 | §14 Dokumentenhierarchie enthält GREMIUM_STRATEGY.md | ☐ |
| 32 | Keine strategischen Inhalte (Achsen, ControlState) in diesem Dokument | ☐ |

---

## ZUSAMMENFASSUNG DER ÄNDERUNGEN

| Änderung | Ziel | Aktion | Umfang |
|---|---|---|---|
| 1 | Kopfzeile | ERSETZE | 8 Zeilen |
| 2 | §0.2 | NEU | ~25 Zeilen |
| 3 | §1.1 | ERSETZE | ~40 Zeilen |
| 4 | §6.14 | NEU | ~120 Zeilen |
| 5 | §3.2 | ERGÄNZE | ~8 Zeilen |
| 6 | §3.4 | ERGÄNZE | ~5 Zeilen |
| 7 | §14 | ERSETZE | ~25 Zeilen |
| 8 | §13 | ERGÄNZE | 3 Zeilen |
| 9 | Anhang B | ERGÄNZE | 6 Zeilen |
| **Gesamt** | | | **~240 Zeilen** |

---

## NACHWEIS: CHARTER-KONFORMITÄT

| CHARTER-Regel | Umsetzung |
|---|---|
| SR-04 | Questor schreibt nicht in Atlas. Digital-Twin-Referenzen sind Pass-Through. |
| SR-08 | Sim-Evidenz bestätigt keine physischen Kristalle. Operational ≠ Scientific. |
| SR-13 | Kalibrierung wird nicht durch LLM entschieden. Deterministischer Pfad. |
| SR-24 | `digital_twin_ref` ist nicht LLM-whitelisted. |

---

## FEHLENDE VERTRÄGE IN CONTRACTS.md (Nachtrag zu Schritt 1)

Die folgenden Digital-Twin-Verträge aus `DIGITAL-TWIN-SEM-1.0.0.md` müssen noch in `CONTRACTS.md §6.10` ergänzt werden (als §6.10.19 und §6.10.20):

| Vertrag | Abschnitt | Quelle |
|---|---|---|
| `DigitalTwinModel` | §6.10.19 | DIGITAL-TWIN-SEM-1.0.0 §2 |
| `TwinDivergenceReport` | §6.10.20 | DIGITAL-TWIN-SEM-1.0.0 §2 |
| Enum-Erweiterung `NodeType.DIGITAL_TWIN` | §10 | DIGITAL-TWIN-SEM-1.0.0 §1 |
| Enum-Erweiterung `EvidenceKind.TWIN_DIVERGENCE` | §10 | DIGITAL-TWIN-SEM-1.0.0 §1 |
| Enum-Erweiterung `DiagnosticOutcomeType.TWIN_DRIFT_CONFIRMED` | §10 | DIGITAL-TWIN-SEM-1.0.0 §1 |
| Enum-Erweiterung `DiagnosticOutcomeType.TWIN_CALIBRATED` | §10 | DIGITAL-TWIN-SEM-1.0.0 §1 |
| `ResearchPackage.digital_twin_ref` | §1.1 | DIGITAL-TWIN-SEM-1.0.0 §3 |
| `ReproducibilityContext.digital_twin_ref` | §6.10.3 | DIGITAL-TWIN-SEM-1.0.0 §3 |
| `AtlasNode.twin_model` | §6.10.8 | DIGITAL-TWIN-SEM-1.0.0 §3 |
| `DiagnosticResolution.twin_divergence_report_ref` | §6.10.11 | DIGITAL-TWIN-SEM-1.0.0 §3 |

**Empfehlung:** Diese Verträge als `CONTRACTS.md §6.10.19–§6.10.20` und Enum-Erweiterungen in einem separaten Nachtrag (CONTRACTS v1.2.1) einarbeiten, bevor die Implementierung beginnt.