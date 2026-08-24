# 📄 GREMIUM_UNIFIED_SPEC_PATCH_DT9.md

---

| Feld | Wert |
|---|---|
| Dateiname | `specs/patches/GREMIUM_UNIFIED_SPEC_PATCH_DT9.md` |
| Version | 1.0.0 |
| Ziel-Dokument | `gremium_unified_specification.md` v1.0.1 → **v1.0.2** |
| Status | ÄNDERUNGSANTRAG — nach Freigabe BINDEND |
| Basis | DT9-Kampagne (3 Langzeit-Dry-Tests, 8 Funde, 5 Fixes) |
| Konfliktregel | CHARTER > CONTRACTS > `gremium_unified_specification.md` > dieses Dokument |
| Komplexitätsbilanz | ➕ 0 neue Enums, ➕ 0 neue Zustände, ➕ 0 neue Verträge, ➕ 0 neue Algorithmen |

---

## §0 Anweisung zur Anwendung

Dieses Dokument enthält **5 Text-Patches** für die `gremium_unified_specification.md` v1.0.1.

**Regeln:**
- Jeder Patch nennt die **exakte Zielstelle** (Abschnitt + Position).
- **NEU** = Text wird an der angegebenen Stelle eingefügt.
- **ERSETZE** = Bestehender Text wird durch den neuen Text ersetzt.
- **ERGÄNZE** = Eine bestehende Tabelle/Liste wird um Zeilen erweitert.
- Nach Anwendung aller Patches ist die Kopfzeile auf `Version 1.0.2` zu setzen und §45 Change-Log zu aktualisieren.

---

## PATCH 1 — BF-14 → §43.2 (CT-8: PHYSICAL_WAIT → FUNDED Rückkehr)

**Zielstelle:** §43.2, Tabelle der Closure-Regeln.

**Aktion:** ERGÄNZE — Neue Zeile nach CT-7 in die bestehende Tabelle einfügen.

**Einzufügende Tabellenzeile:**

| ID | Auslöser | Erzwungene Folge | Begründung |
|---|---|---|---|
| CT-8 | `resource: PHYSICAL_WAIT → FUNDED` durch CAPEX-/Lieferfreigabe (`HumanResponseFile` mit `decision=APPROVE` und `escalation_type ∈ {CAPEX, CAPABILITY_DELIVERY}`) | `governance: AWAITING_HUMAN → AUTONOMOUS` (sofern keine andere Governance-Sperre aktiv: `safety ≠ SAFE_MODE ∧ safety ≠ ESTOP_LOCKED ∧ kein CONFLICT_LOCK`) | Symmetrie zu CT-5; verhindert Steckenbleiben in AWAITING_HUMAN nach physischer Lieferung |

**Komplexität:** ➕ 0 — identisches Muster wie CT-7.

---

## PATCH 2 — BF-15 → §41 (INCREASE_DIAGNOSTIC bei SAFE_MODE + Quarantäne)

**Zielstelle:** §41, nach der bestehenden `safety_intent_blocklist`-Definition.

**Aktion:** ERGÄNZE — Satz nach der bestehenden Blocklist-Definition einfügen.

**Einzufügender Text:**

> **Quarantäne-Diagnostik-Ausnahme:**
> `INCREASE_DIAGNOSTIC` wird aus der `safety_intent_blocklist` bei `safety=SAFE_MODE` entfernt, wenn die Zielzone (`target_ref`) `quarantine_mode=true` hat (§22.6: „Diagnostik erlaubt und budgetiert"). In diesem Fall ist `INCREASE_DIAGNOSTIC` erlaubt, aber nur mit `amount ≤ diagnostic_budget_default` (=3) und nur für die quarantinierte Zone. Alle anderen Blocklist-Einträge bleiben unverändert.

**Komplexität:** ➕ 0 — eine Ausnahme in einer bestehenden Blocklist. Kein neuer Intent, kein neuer Zustand. Nutzt den bestehenden §22.6 Quarantäne-Pfad.

---

## PATCH 3 — BF-16 → §43.2 (CT-9: SAFE_MODE → NORMAL Rückkehr)

**Zielstelle:** §43.2, Tabelle der Closure-Regeln.

**Aktion:** ERGÄNZE — Neue Zeile nach CT-8 in die bestehende Tabelle einfügen.

**Einzufügende Tabellenzeile:**

| ID | Auslöser | Erzwungene Folge | Begründung |
|---|---|---|---|
| CT-9 | `safety: SAFE_MODE → NORMAL` durch SL-SAF-7 (`HumanResponseFile.unlock_decision` mit `scope_refs=["GLOBAL_SAFETY"]`) | `governance: AWAITING_HUMAN → AUTONOMOUS` (sofern keine andere Governance-Sperre aktiv: `resource ≠ BUDGET_EXHAUSTED ∧ resource ≠ PHYSICAL_WAIT ∧ kein CONFLICT_LOCK`) | Symmetrie zu CT-6; verhindert Steckenbleiben in AWAITING_HUMAN nach Sicherheitsfreigabe |

**Komplexität:** ➕ 0 — identisches Muster wie CT-7/CT-8.

---

## PATCH 4 — BF-17 → §20 (SL-SIG-7a Quantifizierung)

**Zielstelle:** §20, nach SL-SIG-7a.

**Aktion:** ERGÄNZE — Satz am Ende von SL-SIG-7a einfügen.

**Einzufügender Text:**

> „Wiederholt" bedeutet: ≥ `min_confirmations` (=2, RESEARCH-besetzt) parameter-äquivalente Kristalle mit derselben Constraint-Verletzung innerhalb von `conflict_window_cycles` (=10). Erst dann erzeugt der Kartograph eine `MetricConstraint`-Fracture. Einzelne Verletzungen bleiben ⬜ CONSTRAINT_NEAR_MISS.

**Komplexität:** ➕ 0 — nutzt bestehende Config-Parameter (`min_confirmations`, `conflict_window_cycles`).

---

## PATCH 5 — BF-18 → §43.2 (CT-Gleichzeitigkeit)

**Zielstelle:** §43.2, nach der Closure-Tabelle.

**Aktion:** NEU — Satz nach der Closure-Tabelle einfügen.

**Einzufügender Text:**

> **SL-CT-SIMULTAN:** Wenn mehrere CT-Regeln denselben Zielwert auf derselben Achse erzwingen (z. B. CT-5 und CT-6 erzwingen beide `governance → AWAITING_HUMAN`), gilt: kein Konflikt, nur eine Transition. Die Severity-Ordnung (§43.1) bestimmt den auslösenden Trigger für das Audit-Log. Bei unterschiedlichen Zielwerten auf derselben Achse: schwerster Zielwert gewinnt (§43.1).

**Komplexität:** ➕ 0 — ein Halbsatz, der bestehende Severity-Logik präzisiert.

---

## PATCH 6 — §44 (Fund-Register aktualisieren)

**Zielstelle:** §44, Tabelle Fund-Register.

**Aktion:** ERGÄNZE — Neue Zeilen am Ende der Tabelle einfügen.

**Einzufügende Tabellenzeilen:**

| Fund-Cluster | Behebungs-Abschnitt | Status |
|---|---|---|
| DT9-F-01 PHYSICAL_WAIT → FUNDED Rückkehr | §43.2 (CT-8) | BEHOBEN |
| DT9-F-03 INCREASE_DIAGNOSTIC bei Quarantäne | §41 (Quarantäne-Diagnostik-Ausnahme) | BEHOBEN |
| DT9-F-04 SAFE_MODE → NORMAL Rückkehr | §43.2 (CT-9) | BEHOBEN |
| DT9-F-05 CT-Gleichzeitigkeit | §43.2 (SL-CT-SIMULTAN) | BEHOBEN |
| DT9-F-07 SL-SIG-7a Quantifizierung | §20 (SL-SIG-7a) | BEHOBEN |

---

## PATCH 7 — §45 (Change-Log aktualisieren)

**Zielstelle:** §45, Tabelle Change-Log.

**Aktion:** ERGÄNZE — Neue Zeile am Ende der Tabelle einfügen.

**Einzufügende Tabellenzeile:**

| Version | Änderung |
|---|---|
| 1.0.2 | DT9-Backfixes: 2 neue Closure-Regeln (CT-8, CT-9), Quarantäne-Diagnostik-Ausnahme (§41), SL-SIG-7a-Quantisierung (§20), SL-CT-SIMULTAN (§43.2). Keine neuen Enums, Zustände oder Verträge. |

---

## PATCH 8 — Kopfzeile aktualisieren

**Zielstelle:** Kopfzeile.

**Aktion:** ERSETZE.

**Bestehender Text:**
> `| Version | 1.0.1 (DT8-Backfixes) |`

**Neuer Text:**
> `| Version | 1.0.2 (DT9-Backfixes) |`

---

## ZUSAMMENFASSUNG DER ÄNDERUNGEN

| Patch | Ziel-Abschnitt | Aktion | Netto-Zeilen |
|---|---|---|---|
| 1 | §43.2 | ERGÄNZE Tabelle | +1 |
| 2 | §41 | ERGÄNZE | +3 |
| 3 | §43.2 | ERGÄNZE Tabelle | +1 |
| 4 | §20 | ERGÄNZE | +2 |
| 5 | §43.2 | NEU | +2 |
| 6 | §44 | ERGÄNZE Tabelle | +5 |
| 7 | §45 | ERGÄNZE Tabelle | +1 |
| 8 | Kopfzeile | ERSETZE | ±0 |
| **Gesamt** | | | **~15 Zeilen** |

---

## NACHWEIS: KEINE KOMPLEXITÄTSERHÖHUNG

| Kriterium | v1.0.1 | v1.0.2 | Delta |
|---|---|---|---|
| Anzahl Enums | 18 | 18 | ➕ 0 |
| Anzahl Achsen-Zustände | 14 | 14 | ➕ 0 |
| Anzahl Closure-Regeln | 9 (CT-1..7, CT-4..6 aus DT8) | 11 (CT-1..9) | ➕ 2 (identisches Muster) |
| Anzahl Pydantic-Modelle | 28 | 28 | ➕ 0 |
| Anzahl SL-Regeln | ~82 | ~83 | ➕ 1 (SL-CT-SIMULTAN) |
| Neue Algorithmen | — | — | ➕ 0 |
| Neue Datenverträge | — | — | ➕ 0 |
| CHARTER-Änderungen | — | — | ➕ 0 |