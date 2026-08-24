# 📄 PATCH-DATEI: `GREMIUM_UNIFIED_SPEC_PATCH_DT8.md`

| Feld | Wert |
|---|---|
| Dateiname | `specs/patches/GREMIUM_UNIFIED_SPEC_PATCH_DT8.md` |
| Version | 1.0.0 |
| Ziel-Dokument | `gremium_unified_specification.md` v1.0.0 → **v1.0.1** |
| Status | ÄNDERUNGSANTRAG — nach Freigabe BINDEND |
| Basis | DT8-Kampagne (3 Langzeit-Dry-Tests, 13 Funde, 12 Fixes) |
| Konfliktregel | CHARTER > CONTRACTS > `gremium_unified_specification.md` > dieses Dokument |
| Komplexitätsbilanz | ➕ 0 neue Enums, ➕ 0 neue Zustände, ➕ 0 neue Verträge, ➕ 0 neue Algorithmen |

---

## §0 Anweisung zur Anwendung

Dieses Dokument enthält **12 Text-Patches** für die `gremium_unified_specification.md`. Jeder Patch ist als **exakter Einfüge- oder Ersetzungstext** formuliert.

**Regeln:**
- Jeder Patch nennt die **exakte Zielstelle** (Abschnitt + Position).
- **NEU** = Text wird an der angegebenen Stelle eingefügt.
- **ERSETZE** = Bestehender Text wird durch den neuen Text ersetzt.
- **ERGÄNZE** = Eine bestehende Tabelle/Liste wird um Zeilen erweitert.
- Nach Anwendung aller Patches ist die Kopfzeile auf `Version 1.0.1` zu setzen und §45 Change-Log zu aktualisieren.

---

## PATCH 1 — BF-01 → §33.4 (SAFE_MODE → NORMAL)

**Zielstelle:** `gremium_unified_specification.md` §33.4, nach dem bestehenden Text.

**Aktion:** NEU — Text am Ende von §33.4 einfügen.

**Einzufügender Text:**

> **SL-SAF-7 SAFE_MODE-Exit-Pfad:**
> Der Übergang `safety: SAFE_MODE → NORMAL` erfolgt ausschließlich durch eine `HumanResponseFile.unlock_decision` mit `scope_refs = ["GLOBAL_SAFETY"]` gemäß SL-SAF-5. Kein automatischer Übergang. Kein LLM-Pfad. Der Kanzler validiert die Freigabe und löst den atomaren Achsen-Transition aus.

---

## PATCH 2 — BF-02 → §43.2 (PHYSICAL_WAIT → AWAITING_HUMAN)

**Zielstelle:** `gremium_unified_specification.md` §43.2, Tabelle der Closure-Regeln.

**Aktion:** ERGÄNZE — Neue Zeile nach CT-3 in die bestehende Tabelle einfügen.

**Einzufügende Tabellenzeile:**

| ID | Auslöser | Erzwungene Folge | Begründung |
|---|---|---|---|
| CT-5 | `resource → PHYSICAL_WAIT` | `governance → AWAITING_HUMAN` | Physisches Warten (CAPEX, Lieferung) erfordert menschliche Entscheidung (SR-11) |

---

## PATCH 3 — BF-03 → §43.2 (SAFETY → AWAITING_HUMAN)

**Zielstelle:** `gremium_unified_specification.md` §43.2, Tabelle der Closure-Regeln.

**Aktion:** ERGÄNZE — Neue Zeile nach CT-5 in die bestehende Tabelle einfügen.

**Einzufügende Tabellenzeile:**

| ID | Auslöser | Erzwungene Folge | Begründung |
|---|---|---|---|
| CT-6 | `safety → SAFE_MODE ∨ safety → ESTOP_LOCKED` | `governance → AWAITING_HUMAN` | Sicherheitsereignisse erfordern immer menschliche Aufsicht (SR-11) |

---

## PATCH 4 — BF-04 → §32 (Laufende Jobs bei Budget-Erschöpfung)

**Zielstelle:** `gremium_unified_specification.md` §32, nach SL-BUD-1.

**Aktion:** NEU — Satz am Ende von SL-BUD-1 einfügen.

**Einzufügender Text:**

> Mission-Budget-Erschöpfung (`resource=BUDGET_EXHAUSTED`) beeinflusst keine laufenden Questor-Pakete. Diese werden ausschließlich durch ihr eigenes `QuestorSpec.budget.max_duration_s` gesteuert (→ QUESTOR.md §11.5). Neue Pakete werden nicht mehr dispatched (`physical_dispatch_allowed=false`, ResourceAxis-Besitz §40).

---

## PATCH 5 — BF-05 → §43.2 (Dimensions-Eskalation → AWAITING_HUMAN)

**Zielstelle:** `gremium_unified_specification.md` §43.2, Tabelle der Closure-Regeln.

**Aktion:** ERGÄNZE — Neue Zeile nach CT-6 in die bestehende Tabelle einfügen.

**Einzufügende Tabellenzeile:**

| ID | Auslöser | Erzwungene Folge | Begründung |
|---|---|---|---|
| CT-4 | `DimensionOnboardingRequest.status → ESCALATED ∧ requires_physical_actuation=true` | `governance → AWAITING_HUMAN` | Physische Dimensionen erfordern menschliche Freigabe (SL-DIM-4, SR-11) |

---

## PATCH 6 — BF-06 → §41 (safety_intent_blocklist)

**Zielstelle:** `gremium_unified_specification.md` §41, nach der bestehenden Formel.

**Aktion:** NEU — Block nach der bestehenden Formel einfügen.

**Einzufügender Text:**

> **safety_intent_blocklist (explizite Definition):**
>
> Bei `safety=ESTOP_LOCKED`: alle Intents außer `{NO_ACTION, HUMAN_ESCALATION}`.
>
> Bei `safety=SAFE_MODE`: `{PIVOT_DOMAIN, PIVOT_TARGET, UNLOCK_BUDGET, ADD_DIMENSION_HINT, SET_RESEARCH_PHASE, INCREASE_DIAGNOSTIC, CALIBRATE_TWIN, ARCHIVE_TOPIC, SET_PRIORITY, DROP_SOFT_PREFERENCE, ABORT_MISSION, INITIAL_SWEEP}`.
>
> Erlaubt bei `safety=SAFE_MODE`: `{NO_ACTION, HUMAN_ESCALATION}`.
>
> **resource_intent_blocklist (explizite Definition):**
>
> Bei `resource=BUDGET_EXHAUSTED`: `{INITIAL_SWEEP, PIVOT_DOMAIN, PIVOT_TARGET, ADD_DIMENSION_HINT, INCREASE_DIAGNOSTIC, CALIBRATE_TWIN, SET_RESEARCH_PHASE, SET_PRIORITY}`.
>
> Erlaubt bei `resource=BUDGET_EXHAUSTED`: `{NO_ACTION, UNLOCK_BUDGET, HUMAN_ESCALATION, ABORT_MISSION, ARCHIVE_TOPIC, DROP_SOFT_PREFERENCE}`.

---

## PATCH 7 — BF-07 → §41 (SET_RESEARCH_PHASE bei BUDGET_EXHAUSTED)

**Zielstelle:** `gremium_unified_specification.md` §41, nach der bestehenden SET_RESEARCH_PHASE-Regel.

**Aktion:** ERSETZE — Bestehenden Satz durch erweiterten Satz ersetzen.

**Bestehender Text:**
> `SET_RESEARCH_PHASE ist verfügbar, wenn keine Safety-/Governance-Sperre vorliegt.`

**Neuer Text:**
> `SET_RESEARCH_PHASE` ist verfügbar, wenn keine Safety-/Governance-Sperre vorliegt **und** `resource ∈ {FUNDED, INCUBATING}`. Bei `resource=BUDGET_EXHAUSTED` oder `resource=PHYSICAL_WAIT` ist `SET_RESEARCH_PHASE` blockiert (Teil der `resource_intent_blocklist`).

---

## PATCH 8 — BF-08 → §17 (CAPEX in DTT)

**Zielstelle:** `gremium_unified_specification.md` §17, Tabelle DirectiveTranslationTable, Zeile `HUMAN_ESCALATION`.

**Aktion:** ERSETZE — Die „Deterministische Wirkung"-Spalte der Zeile `HUMAN_ESCALATION` erweitern.

**Bestehender Text (Spalte „Deterministische Wirkung"):**
> `Eskalation mit Typ aus category`

**Neuer Text (Spalte „Deterministische Wirkung"):**
> `Eskalation mit Typ aus category. Bei escalation_category=CAPEX: löst zusätzlich resource → PHYSICAL_WAIT (via CT-5) und governance → AWAITING_HUMAN (via CT-6) aus.`

---

## PATCH 9 — BF-09 → §39.2 (Quarantäne + Research-Achse)

**Zielstelle:** `gremium_unified_specification.md` §39.2, nach den bestehenden ungültigen Kombinationen.

**Aktion:** NEU — Satz am Ende von §39.2 einfügen.

**Einzufügender Text:**

> Quarantäne (`quarantine_mode=true` auf allen aktiven Topics) ändert die ResearchAxis nicht. Sie blockiert nur normalen Dispatch. Die ResearchAxis bleibt in ihrem aktuellen Zustand, solange `diagnostic_budget > 0` ist. Bei `diagnostic_budget == 0` und Quarantäne: URGENT-Trigger (SL-URG-1).

---

## PATCH 10 — BF-10 → §20 (Overfitting-Semantik)

**Zielstelle:** `gremium_unified_specification.md` §20, nach SL-SIG-7.

**Aktion:** NEU — Satz nach SL-SIG-7 einfügen.

**Einzufügender Text:**

> **SL-SIG-7a Overfitting:** Overfitting (z. B. `train_val_gap > threshold` in einem ObjectiveFamily-Constraint) wird als `CONSTRAINT_NEAR_MISS` (SL-SIG-7) behandelt: ⬜ Signal, kein 🟨 CONTRADICTION. Erst wenn der Constraint wiederholt verletzt wird, erzeugt der Kartograph eine `MetricConstraint`-Fracture.

---

## PATCH 11 — BF-11 → §43.2 (CT-1 Umkehrung)

**Zielstelle:** `gremium_unified_specification.md` §43.2, Tabelle der Closure-Regeln.

**Aktion:** ERGÄNZE — Neue Zeile nach CT-4 in die bestehende Tabelle einfügen.

**Einzufügende Tabellenzeile:**

| ID | Auslöser | Erzwungene Folge | Begründung |
|---|---|---|---|
| CT-7 | `resource: BUDGET_EXHAUSTED → FUNDED` durch UNLOCK_BUDGET-Genehmigung | `governance: AWAITING_HUMAN → AUTONOMOUS` (sofern keine andere Governance-Sperre aktiv) | Symmetrie zu CT-1; verhindert Steckenbleiben in AWAITING_HUMAN |

---

## PATCH 12 — BF-12 → §43.2 (CT-3 Präzisierung)

**Zielstelle:** `gremium_unified_specification.md` §43.2, Tabelle der Closure-Regeln, Zeile CT-3.

**Aktion:** ERSETZE — Die „Erzwungene Folge"-Spalte der Zeile CT-3 erweitern.

**Bestehender Text (Spalte „Erzwungene Folge"):**
> `research-Transitionen werden unterdrückt`

**Neuer Text (Spalte „Erzwungene Folge"):**
> `research-Transitionen werden unterdrückt; bei gleichzeitigem Auftreten im selben Batch hat Safety Vorrang (§43.1)`

---

## PATCH 13 — BF-13 → §44 (Fund-Register aktualisieren)

**Zielstelle:** `gremium_unified_specification.md` §44, Tabelle Fund-Register.

**Aktion:** ERGÄNZE — Neue Zeilen am Ende der Tabelle einfügen.

**Einzufügende Tabellenzeilen:**

| Fund-Cluster | Behebungs-Abschnitt | Status |
|---|---|---|
| DT8-F-01 Dimensions-Eskalation → AWAITING_HUMAN | §43.2 (CT-4) | BEHOBEN |
| DT8-F-02 PHYSICAL_WAIT → AWAITING_HUMAN | §43.2 (CT-5) | BEHOBEN |
| DT8-F-03 CAPEX in §41 | §17 (SL-DTT), §43.2 (CT-5/CT-6) | BEHOBEN |
| DT8-F-05 SAFETY → AWAITING_HUMAN | §43.2 (CT-6) | BEHOBEN |
| DT8-F-06 SAFE_MODE → NORMAL | §33.4 (SL-SAF-7) | BEHOBEN |
| DT8-F-07 safety_intent_blocklist | §41 | BEHOBEN |
| DT8-F-08 Quarantäne + Research-Achse | §39.2 | BEHOBEN |
| DT8-F-10 Overfitting | §20 (SL-SIG-7a) | BEHOBEN |
| DT8-F-11 Laufende Jobs bei Budget-Erschöpfung | §32 (SL-BUD-1) | BEHOBEN |
| DT8-F-12 SET_RESEARCH_PHASE bei BUDGET_EXHAUSTED | §41 | BEHOBEN |
| DT8-F-13 CT-1 Umkehrung | §43.2 (CT-7) | BEHOBEN |

---

## PATCH 14 — §45 (Change-Log aktualisieren)

**Zielstelle:** `gremium_unified_specification.md` §45, Tabelle Change-Log.

**Aktion:** ERGÄNZE — Neue Zeile am Ende der Tabelle einfügen.

**Einzufügende Tabellenzeile:**

| Version | Änderung |
|---|---|
| 1.0.1 | DT8-Backfixes: 4 neue Closure-Regeln (CT-4 bis CT-7), SL-SAF-7 (SAFE_MODE-Exit), explizite Intent-Blocklists (§41), Overfitting-Semantik (§20), Quarantäne-Klarstellung (§39.2), CAPEX-Integration (§17), Budget-Job-Klarstellung (§32). Keine neuen Enums, Zustände oder Verträge. |

---

## PATCH 15 — Kopfzeile aktualisieren

**Zielstelle:** `gremium_unified_specification.md`, Kopfzeile.

**Aktion:** ERSETZE.

**Bestehender Text:**
> `| Version | 1.0.0 (final konsolidiert) |`

**Neuer Text:**
> `| Version | 1.0.1 (DT8-Backfixes) |`

---

## ZUSAMMENFASSUNG DER ÄNDERUNGEN

| Patch | Ziel-Abschnitt | Aktion | Netto-Zeilen |
|---|---|---|---|
| 1 | §33.4 | NEU | +2 |
| 2 | §43.2 | ERGÄNZE Tabelle | +1 |
| 3 | §43.2 | ERGÄNZE Tabelle | +1 |
| 4 | §32 | NEU | +2 |
| 5 | §43.2 | ERGÄNZE Tabelle | +1 |
| 6 | §41 | NEU | +8 |
| 7 | §41 | ERSETZE | ±0 |
| 8 | §17 | ERSETZE | ±0 |
| 9 | §39.2 | NEU | +2 |
| 10 | §20 | NEU | +1 |
| 11 | §43.2 | ERGÄNZE Tabelle | +1 |
| 12 | §43.2 | ERSETZE | ±0 |
| 13 | §44 | ERGÄNZE Tabelle | +11 |
| 14 | §45 | ERGÄNZE Tabelle | +1 |
| 15 | Kopfzeile | ERSETZE | ±0 |
| **Gesamt** | | | **~31 Zeilen** |

**Betroffene Abschnitte:** §17, §20, §32, §33.4, §39.2, §41, §43.2, §44, §45, Kopfzeile.

**Nicht betroffen:** §1–§16, §18, §19, §21–§31, §33.1–§33.3, §33.5, §34–§38, §40, §42.

**Keine Änderungen an:** Questor, HAL, CONTRACTS, CHARTER, ROADMAP, VALIDATION.