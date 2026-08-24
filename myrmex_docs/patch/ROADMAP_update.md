# 📄 ROADMAP.md v1.2.0 — ÄNDERUNGSANWEISUNG (Schritt 4)

**Aktion:** Die folgenden Änderungen sind in die bestehende `ops/ROADMAP.md` (v1.1.0-atlas-hyb.1) einzuarbeiten. Das Ergebnis ist Version **1.2.0-strat.1**.

---

## ÄNDERUNG 1: Kopfzeile

**ERSETZE** die bestehende Kopfzeile:

| Feld | Wert |
|---|---|
| Dateiname | ops/ROADMAP.md |
| Version | **1.2.0-strat.1** |
| Status | ÄNDERUNGSANTRAG STRAT-1.0.0 — nach Freigabe BINDEND |
| System | MYRMEX v2.4.0 + Questor v0.2.3 + HAL v0.2.0 + Gremium Strategic Layer v1.0.0 |
| Schicht | Layer 2 (ops/) — referenziert foundation/ und specs/ |
| Datum | 21. August 2026 |

---

## ÄNDERUNG 2: Neuer Abschnitt §0.2 (nach §0.1 einfügen)

**NEU — nach §0.1 einfügen:**

### §0.2 Änderungsantrag STRAT-1.0.0 — Strategic-Layer-Phasen

Dieser Änderungsantrag fügt die Implementierungsphasen für den Gremium Strategic Layer (Cognitive Observatory) in die Roadmap ein.

Der Strategic Layer wird als eigener Phasen-Block (S1–S3) geführt, der auf den MYRMEX-Neubau-Phasen 1 bis 3 und den Atlas-Hybrid-Phasen A1–A2 aufbaut.

Regeln:
- Dieser Änderungsantrag definiert keine neuen Verträge (→ CONTRACTS.md §6.11).
- Dieser Änderungsantrag definiert keine neuen Sicherheitsregeln (→ CHARTER.md).
- Die Strategic-Layer-Phasen respektieren das Blackboard-Pattern und die Trennung von Operational und Scientific.
- Questor und HAL erhalten keine Kenntnis von Strategic-Layer-Verträgen (→ CHARTER §SR-04).
- Die strategische Steuerung ist in `specs/GREMIUM_STRATEGY.md` definiert.
- Die Pipeline-Mechanik bleibt in `specs/GREMIUM.md`.

---

## ÄNDERUNG 3: §2.1 aktualisieren (Gesamtsystem-Phasen)

**ERSETZE** die bestehende Tabelle in §2.1:

### §2.1 Gesamtsystem-Phasen

| System | Phasen | Anzahl | Gesamtdauer (Schätzung) |
|---|---|---|---|
| MYRMEX (Migration) | M0–M5 | 6 | 10–15 Tage |
| MYRMEX (Neubau) | Phase 1–10 | 10 | 25–35 Tage |
| Atlas-Hybrid | A1–A5 | 5 | 12–18 Tage |
| **Strategic Layer** | **S1–S3** | **3** | **10–15 Tage** |
| HAL | HAL-H0 bis HAL-H6 | 7 | 15–22 Tage |
| Questor | Q0–Q18 | 19 | 44–67 Tage |
| **Gesamt** | | **50** | **~116–172 Tage** |

---

## ÄNDERUNG 4: §2.2 aktualisieren (Phasen-Typen)

**ERGÄNZE** am Ende der Tabelle in §2.2:

| Typ | Bedeutung |
|---|---|
| Strategic Layer | 4-Achsen-Steuerung, Kanzler/Königin, Briefing-Zyklus, ControlState |

---

## ÄNDERUNG 5: Neuer Abschnitt §4B (nach §4A einfügen)

**NEU — nach §4A (Atlas-Hybrid-Phasen) einfügen:**

### §4B Strategic-Layer-Phasen (S1–S3)

#### §4B.1 Übersicht

| Meilenstein | Phasen | Dauer (Schätzung) | Abhängigkeiten |
|---|---|---|---|
| Strat-MS-1: ControlState & Achsen | S1 | 3–5 Tage | MYRMEX Phase 1, CONTRACTS §6.11 |
| Strat-MS-2: Kanzler & DTT | S2 | 4–5 Tage | Strat-MS-1, Atlas-MS-1 |
| Strat-MS-3: Königin & Integration | S3 | 3–5 Tage | Strat-MS-2, Atlas-MS-2 |

#### §4B.2 Phase S1: ControlState-Manager & Achsen-Zustandsmaschine

**Meilenstein:** Strat-MS-1
**Dauer:** 3–5 Tage
**Abhängigkeiten:** MYRMEX Phase 1 (Verträge), CONTRACTS §6.11 (Strategic-Layer-Verträge)

**Aufgaben:**
- `ControlState`-Manager implementieren (CONTRACTS §6.11.1)
- 4-Achsen-Zustandsmaschine implementieren (SafetyAxis, ResourceAxis, ResearchAxis, GovernanceAxis)
- `AxisTransition`-Verwaltung (CONTRACTS §6.11.2)
- `ControlStateLog`-Persistenz (CONTRACTS §6.11.3)
- **SL-AX-ATOMIC** implementieren (GREMIUM_STRATEGY.md §34):
  - SAMMELN → KONFLIKT-ERKENNUNG → ABSCHLUSS → VALIDIERUNG → ATOMARER COMMIT → LOGGING
  - `batch_id`-Verwaltung für atomare Commits
- **Severity-Ordnung** implementieren (GREMIUM_STRATEGY.md §34.1):
  - SAFETY > RESOURCE > GOVERNANCE > RESEARCH
- **Closure-Regeln CT-1..CT-10** implementieren (GREMIUM_STRATEGY.md §34.2)
- **SL-CT-SIMULTAN** implementieren (GREMIUM_STRATEGY.md §34.3)
- **Parameter-Besitz-Matrix** implementieren (GREMIUM_STRATEGY.md §31):
  - Single-Ownership-Enforcement
  - SL-DEP-Lint (Build-Fail bei Verstoß)
- **Validitätsmatrix** implementieren (GREMIUM_STRATEGY.md §30):
  - Ungültige Achsen-Kombinationen erkennen und verwerfen
- **Liveness-Watchdog** implementieren (GREMIUM_STRATEGY.md §33)
- `compute_phase_label()` implementieren (abgeleitetes Etikett)
- Speicherorte anlegen: `data/governance/control_state/`

**Akzeptanzkriterien:**
- [ ] ControlState-Tupel wird korrekt verwaltet
- [ ] SL-AX-ATOMIC: Simultane Transitionen werden atomar committet
- [ ] SL-AX-ATOMIC: Ungültige Ziel-Tupel werden verworfen (fail-closed)
- [ ] Alle 10 Closure-Regeln (CT-1..CT-10) feuern korrekt
- [ ] SL-CT-SIMULTAN: Gleichzeitige Closures erzeugen nur eine Transition
- [ ] Parameter-Besitz-Matrix: Kein Achsen-Parameter wird von einer fremden Achse gesetzt
- [ ] Validitätsmatrix: Ungültige Kombinationen werden erkannt
- [ ] Liveness-Watchdog löst Heartbeat-Zyklus aus
- [ ] Mindestens 40 Unit-Tests (Suite STRAT-AX)

#### §4B.3 Phase S2: Kanzler-Implementierung (DTT, Blocklists, Validierung)

**Meilenstein:** Strat-MS-2
**Dauer:** 4–5 Tage
**Abhängigkeiten:** Strat-MS-1, Atlas-MS-1 (Core & Topologie)

**Aufgaben:**
- **Validierungspipeline v2** implementieren (GREMIUM_STRATEGY.md §7, 10 Stufen):
  - Schema → briefing_ref → Manifest → Weisung → Target → Safety/Injection → Budget → Intent-Sonderregeln → Mode-Prüfung → Semantische Dedup → Konflikt-Modus → ACCEPT
- **DirectiveTranslationTable (DTT)** implementieren (GREMIUM_STRATEGY.md §8):
  - Alle 14 Intents mit deterministischer Übersetzung
  - CAPEX-Integration (BF-08: HUMAN_ESCALATION → PHYSICAL_WAIT + AWAITING_HUMAN)
- **Intent-Verfügbarkeit** implementieren (GREMIUM_STRATEGY.md §32):
  - `safety_intent_blocklist` (explizit, BF-06)
  - `resource_intent_blocklist` (explizit, BF-06)
  - Quarantäne-Diagnostik-Ausnahme (BF-15)
  - SET_RESEARCH_PHASE-Blockierung bei BUDGET_EXHAUSTED (BF-07)
- **Konfliktdetektor & NO_ACTION** implementieren (GREMIUM_STRATEGY.md §9):
  - SL-CON-1..4, SL-INT-5, SL-NOACT-1..2
- **Briefing-Erzeugung** implementieren (GREMIUM_STRATEGY.md §18):
  - StrategicBriefing-Generierung (CONTRACTS §6.11.4)
  - Trunkierungspriorität v2
  - Sanitization (kein security_mode, keine Hybrid-Referenzen)
- **Mensch-Schnittstelle** implementieren (GREMIUM_STRATEGY.md §17):
  - Eskalationskanal (dateibasiert)
  - HumanResponseFile-Validierung
  - Timeout-Handling → governance=AWAITING_HUMAN
- **SL-SAF-7** implementieren (SAFE_MODE-Exit-Pfad)
- **Budget-Modell** implementieren (GREMIUM_STRATEGY.md §23):
  - SL-BUD-1..4, SL-URG-2
  - burn_rate_multiplier via ResourceAxis
- Speicherorte anlegen: `data/governance/briefings/`, `data/governance/directives/`, `data/governance/budget/`, `data/governance/dimension_requests/`, `data/archiv/operational/escalations/`, `data/human_inbox/`

**Akzeptanzkriterien:**
- [ ] Validierungspipeline: Alle 10 Stufen funktionieren in fester Reihenfolge
- [ ] DTT: Alle 14 Intents werden korrekt übersetzt
- [ ] DTT: CAPEX löst resource → PHYSICAL_WAIT und governance → AWAITING_HUMAN aus
- [ ] Intent-Verfügbarkeit: UNLOCK_BUDGET nur bei BUDGET_EXHAUSTED verfügbar
- [ ] Intent-Verfügbarkeit: SET_RESEARCH_PHASE bei BUDGET_EXHAUSTED blockiert
- [ ] Intent-Verfügbarkeit: INCREASE_DIAGNOSTIC bei SAFE_MODE + Quarantäne erlaubt (BF-15)
- [ ] Konfliktdetektor: 2 Konflikte in conflict_window_cycles → DEADLOCK-Eskalation
- [ ] NO_ACTION-Stall: no_action_stall_limit wird korrekt gezählt
- [ ] Briefing: Kein security_mode, keine Hybrid-Referenzen im Briefing
- [ ] SL-SAF-7: SAFE_MODE → NORMAL nur via HumanResponseFile.unlock_decision
- [ ] Budget: burn_rate_multiplier=0 in PHYSICAL_WAIT und BUDGET_EXHAUSTED
- [ ] Mindestens 55 Unit-Tests (Suite STRAT-KANZ)

#### §4B.4 Phase S3: Königin-Integration & End-to-End

**Meilenstein:** Strat-MS-3
**Dauer:** 3–5 Tage
**Abhängigkeiten:** Strat-MS-2, Atlas-MS-2 (Governance & Frontier)

**Aufgaben:**
- **Constitutional Anchor Protocol** implementieren (GREMIUM_STRATEGY.md §3):
  - CONSTITUTIONAL MEMORY (invariant)
  - STATELESS BRIEFING (dynamisch)
  - ANCHOR (Kontinuität, royal_log_anchor_depth=3)
  - Kein persistenter Gesprächsverlauf (SL-ANCHOR-2)
- **StrategicDirective-Verarbeitung** implementieren (CONTRACTS §6.11.5–§6.11.6):
  - Discriminierte Union über `intent`
  - Alle Intent-Submodelle
- **RoyalLog** implementieren (CONTRACTS §6.11.8):
  - RoyalLogEntry mit provisional-Flag (SL-BRF-9)
  - Anchor-Extraktion für Königin-Kontext
- **Symptom-Trigger** implementieren (GREMIUM_STRATEGY.md §10):
  - Alle 10 SymptomTypes
  - SL-URG-1 (alle URGENT-Trigger)
  - SL-URG-3 (Nachzügler-Merge)
  - SL-SYM-1 (Verlustschutz, At-Least-Once)
- **Signal-Semantik** implementieren (GREMIUM_STRATEGY.md §11):
  - SL-SIG-1..8, SL-HYP-4
  - SL-SIG-7a (Overfitting als CONSTRAINT_NEAR_MISS)
  - Parameter-Äquivalenz-Toleranz (DT10-F-04)
- **Missions-Bootstrap** implementieren (GREMIUM_STRATEGY.md §6):
  - SL-BOOT-0..8
  - Manifest-Intake (fail-closed)
- **Dimensions-Lebenszyklus** implementieren (GREMIUM_STRATEGY.md §15):
  - SL-DIM-1..13
  - CT-4 (Dimensions-Eskalation → AWAITING_HUMAN)
- **Capability-Gap & CAPEX** implementieren (GREMIUM_STRATEGY.md §16):
  - SL-ESC-7
  - blocked_cache-Clearing-Pfad
  - CT-8 mit Capability-Registry-Check (DT10-F-03)
- **Digital-Twin-Loop (strategisch)** implementieren (GREMIUM_STRATEGY.md §14):
  - SL-TWIN-1..11
  - SymptomEvent(TWIN_DRIFT)
- **Abschluss und Archivierung** implementieren (GREMIUM_STRATEGY.md §20):
  - SL-RPT-1..4
  - FINAL-Briefing → FinalScientificReport
- **Replikation** implementieren (GREMIUM_STRATEGY.md §21):
  - SL-REP-1..5
- **Sanitization** implementieren (GREMIUM_STRATEGY.md §19):
  - SL-SAN-0..6
  - First-Order-Scan, Second-Order-Scan
- **Datenintegrität** implementieren (GREMIUM_STRATEGY.md §22):
  - SL-INT-1..6
- **End-to-End-Integration** mit Pipeline (GREMIUM.md):
  - SymptomEvents → Vordenker
  - StrategicDirective → DTT → Policy-Wirkung
  - Briefing-Zyklus ↔ Pipeline-Orchestrator
- Speicherorte anlegen: `data/archiv/operational/royal_log/`, `data/archiv/operational/events/`, `data/archiv/ideen/`, `data/governance/manifests/`, `data/governance/registries/`, `data/governance/cache/`

**Akzeptanzkriterien:**
- [ ] Constitutional Anchor: Königin erhält exakt 3 Kontextblöcke
- [ ] Constitutional Anchor: Kein persistenter Gesprächsverlauf
- [ ] StrategicDirective: Alle 14 Intent-Submodelle validieren korrekt
- [ ] RoyalLog: provisional=true bei trunkiertem Briefing
- [ ] Symptom-Trigger: Alle 10 SymptomTypes werden korrekt erzeugt
- [ ] SL-URG-1: Alle URGENT-Trigger funktionieren
- [ ] SL-SIG-7a: Overfitting wird als CONSTRAINT_NEAR_MISS behandelt
- [ ] SL-SIG-7a: "Wiederholt" = ≥ min_confirmations innerhalb conflict_window_cycles
- [ ] Missions-Bootstrap: Manifest-Intake ist fail-closed
- [ ] Dimensions-Lebenszyklus: CT-4 feuert bei physischer Dimension
- [ ] Capability-Gap: CT-8 erfordert Capability-Registry-Eintrag (nicht nur Budget-Freigabe)
- [ ] Digital-Twin-Loop: TWIN_DRIFT erzeugt SymptomEvent
- [ ] End-to-End: Briefing → Directive → DTT → Policy-Wirkung funktioniert
- [ ] Mindestens 60 Unit-Tests + 15 Integrationstests (Suite STRAT-KOEN, STRAT-E2E)

---

## ÄNDERUNG 6: §7 aktualisieren (Meilensteine und Abhängigkeiten)

**ERGÄNZE** nach §7.1b (Atlas-Hybrid-Meilensteine):

### §7.1c Strategic-Layer-Meilensteine

| Meilenstein | Phasen | Dauer | Abhängigkeiten |
|---|---|---|---|
| Strat-MS-1: ControlState & Achsen | S1 | 3–5 Tage | MYRMEX Phase 1, CONTRACTS §6.11 |
| Strat-MS-2: Kanzler & DTT | S2 | 4–5 Tage | Strat-MS-1, Atlas-MS-1 |
| Strat-MS-3: Königin & Integration | S3 | 3–5 Tage | Strat-MS-2, Atlas-MS-2 |

### §7.2b Strategic-Layer-Abhängigkeiten

| Strat-Meilenstein | MYRMEX-Phase | Atlas-Phase | Questor-Phase | Bedingung |
|---|---|---|---|---|
| Strat-MS-1 | Phase 1 (Verträge) | — | — | CONTRACTS §6.11 muss definiert sein |
| Strat-MS-2 | — | Atlas-MS-1 | — | ControlState muss funktionieren |
| Strat-MS-3 | — | Atlas-MS-2 | — | Kanzler muss funktionieren |

---

## ÄNDERUNG 7: §7.3 aktualisieren (Abhängigkeitsgraph)

**ERGÄNZE** am Ende des Abhängigkeitsgraphen in §7.3:

```
 │  STRATEGIC LAYER (nach Atlas-MS-2):                                │
 │  ┌──────────────────────────────────────────────────────────┐      │
 │  │  S1 → S2 → S3                                            │      │
 │  │  (S1 benötigt MYRMEX Phase 1 + CONTRACTS §6.11)          │      │
 │  │  (S2 benötigt S1 + Atlas-MS-1)                           │      │
 │  │  (S3 benötigt S2 + Atlas-MS-2)                           │      │
 │  └──────────────────────────────────────────────────────────┘      │
```

---

## ÄNDERUNG 8: §8 aktualisieren (Kritischer Pfad)

**ERGÄNZE** nach §8.3 (Atlas-Hybrid-Pfad):

### §8.4 Strategic-Layer-Pfad

Der Strategic-Layer-Pfad ist:

```
MYRMEX Phase 1 → S1 → S2 → S3 → MYRMEX Phase 10 (E2E)
```

**Parallelisierung:**
- S1 kann parallel zu Atlas A1-A2 entwickelt werden (beide hängen nur von MYRMEX Phase 1 ab).
- S2 erfordert Atlas-MS-1 (A1-A2 abgeschlossen).
- S3 erfordert Atlas-MS-2 (A3-A4 abgeschlossen).
- S3 kann parallel zu Questor Q9-Q13 (MS-3 und MS-4) entwickelt werden.

---

## ÄNDERUNG 9: §10 aktualisieren (Zeitplanung)

**ERGÄNZE** im Gantt-Diagramm in §10.1 (nach Atlas-Block):

```
   Strategic:                              ██████████████████
     S1:                                   ██████
     S2:                                         ██████
     S3:                                               ██████
```

**ERGÄNZE** in §10.2 (Empfohlene Reihenfolge):

```
 WOCHE 6-7:
     Strategic S1 (ControlState & Achsen)
     Atlas A3 (DiagnosticResolution & SafetyConstraint)

 WOCHE 7-8:
     Strategic S2 (Kanzler & DTT)
     Atlas A4 (FrontierEngine & ExplorationPolicy)

 WOCHE 8-9:
     Strategic S3 (Königin & Integration)
     Atlas A5 (Domänen-Integration & Regression)
```

---

## ÄNDERUNG 10: §11 aktualisieren (Test-Gates)

**ERGÄNZE** in §11.1 (Test-Gates):

| Gate | Bedingung |
|---|---|
| GATE-STRAT | Alle Strategic-Layer-Tests bestehen (Suite STRAT) |

**ERGÄNZE** in §11.2 (Teststrategie pro Phase):

| Phase | Test-Typ | Anzahl | Coverage-Ziel |
|---|---|---|---|
| S1 | Unit-Tests (ControlState, Achsen) | 40 | 95% |
| S2 | Unit-Tests (Kanzler, DTT, Blocklists) | 55 | 90% |
| S3 | Unit-Tests + Integration (Königin, E2E) | 75 | 85% |
| Strategic Gesamt | | ~170 | ≥ 90% |

---

## ÄNDERUNG 11: §12 aktualisieren (Akzeptanzkriterien)

**ERGÄNZE** am Ende der Tabelle in §12:

| # | Kriterium | CHARTER-Referenz |
|---|---|---|
| 37 | Alle Strategic-Layer-Tests bestehen (Suite STRAT) | — |
| 38 | Strategic-Layer-Phasen S1–S3 abgeschlossen | — |
| 39 | ControlState wird atomar verwaltet (SL-AX-ATOMIC) | CHARTER §SR-55 |
| 40 | Alle 10 Closure-Regeln (CT-1..CT-10) funktionieren | — |
| 41 | Intent-Verfügbarkeit wird korrekt durch Blocklists gesteuert | — |
| 42 | SAFE_MODE → NORMAL nur via menschliche Freigabe (SL-SAF-7) | CHARTER §SR-11 |
| 43 | ESTOP_LOCKED → NORMAL nur via autorisierten Sicherheitsprozess | CHARTER §SR-05 |
| 44 | Königin erhält exakt 3 Kontextblöcke (Constitutional Anchor) | CHARTER §SR-13 |
| 45 | Kein security_mode im Briefing | CHARTER §SR-29 |
| 46 | Questor und HAL kennen keine Strategic-Layer-Verträge | CHARTER §SR-04 |

---

## ÄNDERUNG 12: §14 aktualisieren (Sicherheitsregeln)

**ERGÄNZE** in §14.1 (Implementierungsregeln):

| # | Regel | CHARTER-Referenz |
|---|---|---|
| IR-16 | Strategic-Layer-Implementierung erzeugt keine neuen Sicherheitsregeln | CHARTER §3 |
| IR-17 | Strategic-Layer-Implementierung definiert keine neuen Datenverträge | CONTRACTS §6.11 |
| IR-18 | ControlState-Parameter werden nur über die Besitzer-Achse gesetzt | GREMIUM_STRATEGY §31 |
| IR-19 | Königin-LLM ist stateless (kein persistenter Gesprächsverlauf) | GREMIUM_STRATEGY §3 |

**ERGÄNZE** in §14.2 (Verbotene Patterns):

| # | Pattern | CHARTER-Referenz |
|---|---|---|
| VP-21 | Königin-LLM mit persistentem Gesprächsverlauf | GREMIUM_STRATEGY §27 |
| VP-22 | LLM-Einsatz im Kanzler | GREMIUM_STRATEGY §27 |
| VP-23 | Direkter Atlas-Zugriff der Königin | GREMIUM_STRATEGY §27 |
| VP-24 | Achsen-Parameter direkt setzen statt über ControlState | GREMIUM_STRATEGY §27 |
| VP-25 | security_mode im strategischen Briefing | CHARTER §SR-29 |

---

## ÄNDERUNG 13: §15 aktualisieren (Zusammenfassung)

**ERSETZE** die bestehende Tabelle in §15:

| Aspekt | Definition |
|---|---|
| Phasen | Q0–Q18 (19 Questor), M0–M5 (6 MYRMEX-Migration), Phase 1–10 (10 MYRMEX-Neubau), A1–A5 (5 Atlas-Hybrid), **S1–S3 (3 Strategic Layer)**, HAL-H0 bis HAL-H6 (7 HAL) |
| Meilensteine | MS-1 bis MS-6 (6 Questor), Atlas-MS-1 bis Atlas-MS-3 (3 Atlas), **Strat-MS-1 bis Strat-MS-3 (3 Strategic)** |
| Gesamtdauer | ~44–67 Tage (Questor), ~12–18 Tage (Atlas), **~10–15 Tage (Strategic)**, ~22–30 Tage (3 Entwickler) |
| Test-Anzahl | ~541 + **~170 Strategic** = **~711 Tests** |
| Coverage-Ziel | ≥ 88% gesamt, ≥ 95% sicherheitskritisch |
| Kritischer Pfad | Q0 → Q1 → Q5 → Q7 → Q8 → Q9 → Q10 → Q11 → Q14 → Q15 → Q16 → Q17 → Q18 |
| Atlas-Pfad | MYRMEX Phase 3 → A1 → A2 → A3 → A4 → A5 → MYRMEX Phase 10 |
| **Strategic-Pfad** | **MYRMEX Phase 1 → S1 → S2 → S3 → MYRMEX Phase 10** |
| Externe Abhängigkeiten | MYRMEX Phase 1, 2, 3, 5, 8; HAL Phase HAL-H1, HAL-H6; Questor MS-3; **CONTRACTS §6.11** |
| Risiken | 12 + **2 Strategic** = 14 identifizierte Risiken |
| Akzeptanzkriterien | 36 + **10 Strategic** = **46 Kriterien** |
| Test-Gates | 9 + **GATE-STRAT** = **10 Gates** |

---

## ÄNDERUNG 14: §9 aktualisieren (Risikobewertung)

**ERGÄNZE** am Ende der Risiko-Matrix in §9.1:

| # | Risiko | Wahrscheinlichkeit | Auswirkung | Mitigation |
|---|---|---|---|---|
| R13 | ControlState-Achsen erzeugen unerwartete Closure-Kaskaden | Mittel | Hoch | SL-AX-ATOMIC mit closure_max_iterations=5. Fail-Closed bei ungültigem Ziel-Tupel. Suite STRAT-AX. |
| R14 | Königin-LLM erzeugt Direktiven, die nicht zur Achsen-Situation passen | Mittel | Mittel | Intent-Verfügbarkeit (§32) blockiert unpassende Intents deterministisch. DTT validiert gegen ControlState. |

---

## ÄNDERUNG 15: §16 aktualisieren (Dokumentenhierarchie)

**ERGÄNZE** am Ende von §16:

Dieses Dokument referenziert zusätzlich:
- `specs/GREMIUM_STRATEGY.md` für Strategic-Layer-Regeln (Achsen, ControlState, Kanzler/Königin)

---

## ZUSAMMENFASSUNG DER ÄNDERUNGEN

| Änderung | Ziel | Aktion | Umfang |
|---|---|---|---|
| 1 | Kopfzeile | ERSETZE | 6 Zeilen |
| 2 | §0.2 | NEU | ~15 Zeilen |
| 3 | §2.1 | ERSETZE | ~8 Zeilen |
| 4 | §2.2 | ERGÄNZE | 1 Zeile |
| 5 | §4B | NEU | ~180 Zeilen |
| 6 | §7.1c + §7.2b | NEU | ~20 Zeilen |
| 7 | §7.3 | ERGÄNZE | ~5 Zeilen |
| 8 | §8.4 | NEU | ~10 Zeilen |
| 9 | §10 | ERGÄNZE | ~15 Zeilen |
| 10 | §11 | ERGÄNZE | ~8 Zeilen |
| 11 | §12 | ERGÄNZE | ~10 Zeilen |
| 12 | §14 | ERGÄNZE | ~12 Zeilen |
| 13 | §15 | ERSETZE | ~12 Zeilen |
| 14 | §9 | ERGÄNZE | ~4 Zeilen |
| 15 | §16 | ERGÄNZE | ~2 Zeilen |
| **Gesamt** | | | **~308 Zeilen** |

---

## NACHWEIS: CHARTER-KONFORMITÄT

| CHARTER-Regel | Umsetzung |
|---|---|
| SR-04 | Questor und HAL erhalten keine Strategic-Layer-Phasen. Keine Schreibrechte. |
| SR-11 | SAFE_MODE-Exit und ESTOP-Reset erfordern menschliche Freigabe. In S2/S3 als Akzeptanzkriterium. |
| SR-13 | Königin ist LLM-Advisor. Kanzler ist deterministisch. In S2/S3 als Akzeptanzkriterium. |
| SR-29 | Kein security_mode im Briefing. In S2 als Akzeptanzkriterium. |
| SR-55 | SL-AX-ATOMIC nutzt atomare Dateioperationen. In S1 als Akzeptanzkriterium. |