# GREMIUM MODULE INDEX — System Composition & Governance

| Feld | Wert |
|------|------|
| **Dateiname** | `gremium_00_index.md` |
| **Modul** | INDEX |
| **Version** | 1.2.0 |
| **Status** | AKTIV |
| **System-Version** | GREMIUM v0.4.0-control-beta |
| **Komposition** | 10_core@1.0.0 + 20_contracts@1.0.0 + 30_rules@1.0.0 + 40_control@2.0.0 |
| **Basis** | Migration aus v0.2.0 + v0.3.0 + Achsen-Transformation + DT6-Bereinigung |
| **Konfliktregel** | Single Ownership + ControlState (siehe §2) |
| **Letzte Änderung** | v1.2.0: Register-Status korrigiert (BEHOBEN → DESIGN FIXIERT), KV2-13/16 ergänzt, Lade- vs. Konflikt-Hierarchie getrennt |

---

## §0 Zweck und Geltung

Dieses Dokument ist der **System-Index** (Lock-File) des Gremiums. Es definiert:

1. **Komposition:** Welche Modulversionen bilden das aktuelle System.
2. **Lade-Reihenfolge:** In welcher Reihenfolge Module geparst werden.
3. **Konfliktregeln:** Wie Parameterkonflikte aufgelöst werden (Single Ownership + ControlState).
4. **Fund-Register:** Zentrale Verwaltung aller kampagnenübergreifenden Funde mit präzisem Behebungsstatus.
5. **Kompositions-Tests:** Modulübergreifende Invarianten.
6. **Change-Log:** Historie aller Systemänderungen.

**Wichtig:** Dieses Modul enthält keine fachlichen Regeln. Es ist ausschließlich Meta-Ebene.

---

## §1 Modul-Komposition

| Modul | Version | Status | Zweck | Änderungsrate |
|-------|---------|--------|-------|---------------|
| `gremium_10_core.md` | 1.0.0 | AKTIV | Invarianten, Grunddefinitionen, Rollen, Zugriffsregeln | Selten |
| `gremium_20_contracts.md` | 1.0.0 | AKTIV | Alle Datenverträge, Enums, StrategicLayerConfig | Selten–Mittel |
| `gremium_30_rules.md` | 1.0.0 | AKTIV | Mechanik: SL-Regeln, Validierung, Zustandsmaschinen | Mittel |
| `gremium_40_control.md` | 2.0.0 | AKTIV | Steuerung: 4 orthogonale Steuerachsen, ControlState | **Hoch** |

### §1.1 Lade-Reihenfolge (bindend für Parser)

```
1. gremium_10_core.md    (Invarianten, Grundbegriffe)
2. gremium_20_contracts.md (Verträge, Config-Schema)
3. gremium_30_rules.md   (Mechanik, SL-Regeln)
4. gremium_40_control.md (Steuerung, Achsen, Parameter-Besitz)
5. gremium_00_index.md   (dieses Dokument, Meta-Ebene)
```

> **Hinweis (K6-F-31 behoben):** Diese Reihenfolge ist eine reine **Lade- und Parse-Reihenfolge** (Loading Order), damit Symbole verfügbar sind, wenn sie referenziert werden. Sie ist **keine Regel-Hierarchie**. Regelkonflikte werden ausschließlich über das Kontrollmodell (§2) aufgelöst.

---

## §2 Konfliktregeln — Single Ownership + ControlState

### §2.1 Grundprinzip

Es gibt **keine Hierarchie zwischen den Modulen** im Sinne von "Modul X sticht Modul Y". Stattdessen gilt:

1. **Single Ownership:** Jeder verhaltensrelevante Parameter in `StrategicLayerConfig` (20_contracts) hat genau eine Besitzer-Achse, deklariert in der Parameter-Besitz-Matrix (40_control §4).
2. **ControlState als Schnittstelle:** Regeln in 30_rules lesen den `ControlState` und wenden ihre Parameter gemäß der Besitzer-Achse an.
3. **Kein Override:** Eine Achse überschreibt niemals eine andere Achse. Achsen komponieren über ein Zustandstupel (safety, resource, research, governance).
4. **Safety ist absolut:** Die SafetyAxis (40_control §2.1) überstimmt alle anderen Achsen. Ihr Gate kann von keiner anderen Achse geöffnet werden.

### §2.2 Konfliktlösung

| Szenario | Lösung |
|----------|--------|
| Regel in 30_rules versucht Parameter ohne Besitzer-Achse zu ändern | Build-Fail (Single-Ownership-Lint) |
| Zwei Regeln in 30_rules wollen denselben Parameter ändern | Nur eine darf es; die andere muss den ControlState lesen |
| Safety-Regel vs. Resource-Achse | Safety gewinnt immer (absolut) |
| Zwei Achsen-Transitionen gleichzeitig | Atomarität geprüft gegen §3.2 in 40_control |

---

## §3 Fund-Register (Kampagnenübergreifend)

**Legende:**
- `OFFEN` = nicht behoben, Design unklar
- `IN ARBEIT` = Fix in Entwicklung, Struktur noch unklar
- `DESIGN FIXIERT` = Achsen-Design löst Fund konzeptionell, mechanische Implementierung in `20_contracts`/`30_rules` ausstehend
- `BEHOBEN` = vollständig implementiert und getestet
- `AKZEPTIERT` = bewusstes Restrisiko

| Fund-ID | Kampagne | Schwere | Beschreibung | Status | Behoben durch |
|---------|----------|---------|--------------|--------|---------------|
| KV2-01 | T1/T2/T3 | S0 | Zeit-/Zyklusmodell kollidiert mit physischer Realität | **DESIGN FIXIERT** | 40_control (ResourceAxis) |
| KV2-02 | T1/T2/T3 | S0 | SL-DEP-1-Verstöße: referenzierte, aber undefinierte Verträge | OFFEN | 20_contracts (geplant) |
| KV2-03 | T1/T2 | S1 | Fehlende Config-Parameter (referenziert, nicht definiert) | IN ARBEIT | 20_contracts |
| KV2-04 | T1/T2/T3 | S0 | Budget-Formeln nutzen undefinierte Größen | OFFEN | 30_rules (geplant) |
| KV2-05 | T1/T2 | S1 | Toleranz-Überladung + Bio-Varianz | **DESIGN FIXIERT** | 40_control (ResearchAxis) |
| KV2-06 | T1/T2/T3 | S1 | Physische Trägheit ignoriert (in-flight Experimente) | **DESIGN FIXIERT** | 40_control (ResourceAxis) |
| KV2-07 | T1/T2/T3 | S1 | Kontext-Blackout für Menschen (nur Skalare, keine Rohdaten) | OFFEN | 20_contracts (EvidenceBundle) |
| KV2-08 | T1/T3 | S1 | Innovations-Deadlock (De-novo ohne atlas_refs verworfen) | **DESIGN FIXIERT** | 40_control (ResearchAxis) |
| KV2-09 | T3 | S2 | Wissens-Amnesie über Missionsgrenzen | OFFEN | 10_core (Domain KB) |
| KV2-10 | T1/T2/T3 | S0 | Safety-Scan blind für Bio-Datenformate (FASTA/PDB) | OFFEN | 30_rules (Bio-Scanner) |
| KV2-11 | T1/T2/T3 | S2 | Stilles Scheitern bei CAPEX/BENIGN-VETOs | OFFEN | 30_rules (Go/No-Go) |
| KV2-12 | T1/T2 | S2 | Tote Felder / Vertragshygiene (zyklus_id) | IN ARBEIT | 20_contracts |
| **KV2-13** | **T2** | **S0** | **Kontamination erzeugt plausibles Falsch-Positiv** | **OFFEN** | **20_contracts** |
| KV2-14 | T1/T2 | S1 | Stall-Detektion ignoriert in-flight-Pakete | **DESIGN FIXIERT** | 40_control (GovernanceAxis) |
| KV2-15 | T1/T2 | S2 | Fortschrittsskalar für PARETO undefiniert | OFFEN | 20_contracts |
| **KV2-16** | **T2** | **S1** | **StopCondition SATURATION_CYCLES ohne Parameter** | **OFFEN** | **20_contracts/30_rules** |
| KV2-17 | T1/T2 | S2 | valid_until-Ablauf vs. in-flight-Pakete undefiniert | OFFEN | 30_rules |
| BIO-26 | T2 | S0 | Kontamination erzeugt plausibles Falsch-Positiv | OFFEN | 20_contracts |
| BIO-36 | T2 | S1 | Slot-Serialisierung: Bio-Parallelisierung nicht ausdrückbar | OFFEN | 20_contracts |
| DRY-05 | T3 | S0 | Regex-Safety erkennt FASTA/PDB-Toxine nicht | OFFEN | 30_rules |
| DRY-07 | T3 | S1 | Sunk-Cost-Blindheit bei Manifest-Änderung | IN ARBEIT | 30_rules |
| DRY-08 | T3 | S1 | Quarantäne-Auflösung ohne Rohdaten-Kontext | OFFEN | 20_contracts |
| DRY-09 | T3 | S2 | Lessons-Learned nie global (Amnesie) | OFFEN | 10_core |
| DRY-10 | T3 | S2 | CAPEX-VETOs führen zu stillem Archivieren | OFFEN | 30_rules |
| K5-F-02 | T4 | S0 | Phasen-Override verliert gegen 30_rules | **DESIGN FIXIERT** | 40_control (Single Ownership) |
| K5-F-16 | T4 | S1 | Kein SET_PHASE-Intent für Königin | **DESIGN FIXIERT** | 40_control (SET_RESEARCH_PHASE) |
| K5-F-17 | T4 | S1 | Kein Phasen-Feld in HumanDirective | **DESIGN FIXIERT** | 40_control |
| K5-F-18 | T4 | S0 | PHYSICAL_WAIT + CRISIS Stacking undefiniert | **DESIGN FIXIERT** | 40_control (Achsen-Orthogonalität) |
| K5-F-20 | T4 | S1 | Missions- vs. Topic-Granularität | **DESIGN FIXIERT** | 40_control (ResearchAxis) |
| K5-F-25 | T4 | S0 | 15 SystemMode × MissionPhase Kombinationen undefiniert | **DESIGN FIXIERT** | 40_control (4 Achsen) |
| K5-F-41 | T4 | S0 | UNLOCK_BUDGET in keiner Phase erlaubt | **DESIGN FIXIERT** | 40_control (Intent-Schnittmenge) |
| K5-F-42 | T4 | S1 | PIVOT_DOMAIN/DROP_SOFT_PREFERENCE blockiert | **DESIGN FIXIERT** | 40_control |
| K5-F-43 | T4 | S1 | CALIBRATE_TWIN in PHYSICAL_WAIT blockiert | **DESIGN FIXIERT** | 40_control (SANDBOX) |
| K5-F-48 | T4 | S0 | KV2-08-Fix (De-novo) mechanisch unwirksam | **DESIGN FIXIERT** | 40_control (ResearchAxis) |
| K5-F-49 | T4 | S0 | KV2-01-Fix (Budget-Pause) mechanisch unwirksam | **DESIGN FIXIERT** | 40_control (ResourceAxis) |

**Zählung:** 35 Funde insgesamt.
- **OFFEN:** 16
- **IN ARBEIT:** 3
- **DESIGN FIXIERT:** 16
- **BEHOBEN:** 0
- **AKZEPTIERT:** 0

> **Transparenz-Hinweis:** Kein Fund ist aktuell vollständig `BEHOBEN`, da die mechanische Einlösung der Achsen-Architektur in den Phantom-Modulen `20_contracts` und `30_rules` aussteht. `DESIGN FIXIERT` bedeutet: Das Achsen-Modell löst den Fund konzeptionell auf; die Implementierung ist der nächste zwingende Schritt.

---

## §4 Kompositions-Tests (Cross-Module Invariants)

Diese Tests müssen bei **jeder** Versions-Komposition durchgeführt werden.

| ID | Test | Erwartung | Voraussetzung |
|----|------|-----------|---------------|
| COMP-01 | Parameter hat `owner_axis` in 40_control §4 | Single-Ownership-Lint besteht | 20_contracts, 30_rules existieren |
| COMP-02 | Regel in 30_rules ändert Parameter ohne Besitzer-Achse | Build-Fail | 20_contracts, 30_rules existieren |
| COMP-03 | SafetyAxis überstimmt andere Achsen | Safety-Gate ist absolut | 40_control |
| COMP-04 | ControlState-Tupel ist immer gültig | Nur explizit ungültige Kombinationen werden verworfen | 40_control |
| COMP-05 | 40_control referenziert Parameter aus 20_contracts | Parameter existiert und ist typkompatibel | 20_contracts |
| COMP-06 | 30_rules referenziert Vertrag aus 20_contracts | Vertrag existiert und ist vollständig definiert | 20_contracts |
| COMP-07 | 10_core definiert Rolle, 30_rules nutzt sie | Rolle existiert und Zugriffsregeln sind konsistent | 10_core, 30_rules |
| COMP-08 | StrategicLayerConfig hat Default für jeden Parameter | Kein Parameter ist required ohne Default | 20_contracts |
| COMP-09 | ControlStateLog referenziert Achsenwert | Wert existiert im Achsen-Enum | 40_control |
| COMP-10 | Lade-Reihenfolge wird verletzt | Parser-Fehler | — |

---

## §5 Change-Log

| Version | Datum | Änderung | Funde behoben |
|---------|-------|----------|---------------|
| 1.0.0 | 2025-01-XX | Initiale modulare Struktur, Migration aus v0.2.0+v0.3.0, Phasen-Architektur | — |
| 1.1.0 | 2025-01-XX | 40_phases → 40_control: Phasen-Skalar durch 4 orthogonale Steuerachsen ersetzt | K5-F-02, -18, -25, -41, -48, -49 (Design) |
| **1.2.0** | **2025-01-XX** | **DT6-Bereinigung:** Status "BEHOBEN" → "DESIGN FIXIERT" (Transparenz); KV2-13, KV2-16 ins Register aufgenommen; Lade-Reihenfolge explizit von Konflikt-Hierarchie getrennt; COMP-Test-Voraussetzungen deklariert | **K6-F-31, K6-F-32, K6-F-33, K6-F-34** |

---

## §6 Anhang: Glossar

| Begriff | Definition |
|---------|------------|
| **Modul** | Selbstständige Spezifikationsdatei mit eigener Version |
| **Komposition** | Menge von Modulversionen, die ein System bilden |
| **ControlState** | Autoritatives Zustandstupel (safety, resource, research, governance) |
| **Steuerachse** | Eine der 4 orthogonalen Dimensionen des ControlState |
| **Parameter-Besitz-Matrix** | Deklaration, welche Achse welchen Parameter besitzt (40_control §4) |
| **DESIGN FIXIERT** | Fund ist durch die Achsen-Architektur konzeptionell gelöst, aber die mechanische Implementierung in `20_contracts`/`30_rules` steht noch aus |
| **Phantom-Modul** | Modul, das im Index referenziert wird, aber noch nicht als Datei existiert (aktuell: 20_contracts, 30_rules, 10_core) |

---

**Ende des Index-Moduls.**