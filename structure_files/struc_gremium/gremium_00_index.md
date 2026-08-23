# GREMIUM MODULE INDEX — System Composition & Governance

| Feld | Wert |
|------|------|
| **Dateiname** | `gremium_00_index.md` |
| **Modul** | INDEX |
| **Version** | 1.3.0 |
| **Status** | AKTIV |
| **System-Version** | GREMIUM v0.5.0-complete |
| **Komposition** | 10_core@1.0.0 + 20_contracts@1.1.1 + 30_rules@1.0.0 + 40_control@2.1.1 |
| **Basis** | Migration aus v0.2.0 + v0.3.0 + Achsen-Transformation + Vollständige Modulausrollung |
| **Konfliktregel** | Single Ownership + ControlState (siehe §2) |
| **Letzte Änderung** | v1.3.0: 10_core@1.0.0 und 30_rules@1.0.0 in Komposition aufgenommen; keine Phantom-Module mehr; Fund-Register finalisiert |

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
| `gremium_10_core.md` | **1.0.0** | **AKTIV** | Invarianten, Grunddefinitionen, Rollen, Zugriffsregeln | Selten |
| `gremium_20_contracts.md` | **1.1.1** | **AKTIV** | Alle Datenverträge, Enums, StrategicLayerConfig | Selten–Mittel |
| `gremium_30_rules.md` | **1.0.0** | **AKTIV** | Mechanik: SL-Regeln, Validierung, Zustandsmaschinen | Mittel |
| `gremium_40_control.md` | **2.1.1** | **AKTIV** | Steuerung: 4 orthogonale Steuerachsen, ControlState | **Hoch** |

**Keine Phantom-Module mehr.** Alle referenzierten Module existieren als Dateien.

### §1.1 Lade-Reihenfolge (bindend für Parser)

```
1. gremium_10_core.md    (Invarianten, Grundbegriffe)
2. gremium_20_contracts.md (Verträge, Config-Schema)
3. gremium_30_rules.md   (Mechanik, SL-Regeln)
4. gremium_40_control.md (Steuerung, Achsen, Parameter-Besitz)
5. gremium_00_index.md   (dieses Dokument, Meta-Ebene)
```

> **Hinweis:** Diese Reihenfolge ist eine reine **Lade- und Parse-Reihenfolge** (Loading Order), damit Symbole verfügbar sind, wenn sie referenziert werden. Sie ist **keine Regel-Hierarchie**. Regelkonflikte werden ausschließlich über das Kontrollmodell (§2) aufgelöst.

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
- `DESIGN FIXIERT` = Architektur löst Fund konzeptionell, mechanische Implementierung als Erweiterung ausstehend
- `BEHOBEN` = vollständig implementiert und in den Modulen verankert
- `AKZEPTIERT` = bewusstes Restrisiko

| Fund-ID | Kampagne | Schwere | Beschreibung | Status | Behoben durch |
|---------|----------|---------|--------------|--------|---------------|
| KV2-01 | T1/T2/T3 | S0 | Zeit-/Zyklusmodell kollidiert mit physischer Realität | **BEHOBEN** | 30_rules §19.2, 40_control §2.2 |
| KV2-02 | T1/T2/T3 | S0 | SL-DEP-1-Verstöße: referenzierte, aber undefinierte Verträge | **BEHOBEN** | 20_contracts §1, §5 |
| KV2-03 | T1/T2 | S1 | Fehlende Config-Parameter (referenziert, nicht definiert) | **BEHOBEN** | 20_contracts §4 |
| KV2-04 | T1/T2/T3 | S0 | Budget-Formeln nutzen undefinierte Größen | **BEHOBEN** | 30_rules §19.2 (SL-BUD-4) |
| KV2-05 | T1/T2 | S1 | Toleranz-Überladung + Bio-Varianz | **BEHOBEN** | 20_contracts §5.4 (hysteresis_band), 30_rules §7 |
| KV2-06 | T1/T2/T3 | S1 | Physische Trägheit ignoriert (in-flight Experimente) | **BEHOBEN** | 30_rules §12, 40_control §2.2 |
| KV2-07 | T1/T2/T3 | S1 | Kontext-Blackout für Menschen (nur Skalare, keine Rohdaten) | OFFEN | EvidenceBundle als Erweiterung geplant |
| KV2-08 | T1/T3 | S1 | Innovations-Deadlock (De-novo ohne atlas_refs verworfen) | **BEHOBEN** | 30_rules §7.2, 40_control §2.3 |
| KV2-09 | T3 | S2 | Wissens-Amnesie über Missionsgrenzen | **DESIGN FIXIERT** | 10_core §7 (Domain Knowledge Base als Design-Notiz) |
| KV2-10 | T1/T2/T3 | S0 | Safety-Scan blind für Bio-Datenformate (FASTA/PDB) | **DESIGN FIXIERT** | 30_rules §15 (SL-SAN-0 greift generisch; Bio-Scanner als Erweiterung) |
| KV2-11 | T1/T2/T3 | S2 | Stilles Scheitern bei CAPEX/BENIGN-VETOs | **BEHOBEN** | 30_rules §12 (SL-ESC-7) |
| KV2-12 | T1/T2 | S2 | Tote Felder / Vertragshygiene (zyklus_id) | **BEHOBEN** | 20_contracts §7 (zyklus_id gestrichen) |
| KV2-13 | T2 | S0 | Kontamination erzeugt plausibles Falsch-Positiv | OFFEN | CONTAMINATED-Status als Erweiterung geplant |
| KV2-14 | T1/T2 | S1 | Stall-Detektion ignoriert in-flight-Pakete | **BEHOBEN** | 30_rules §5.3, 40_control §2.4 |
| KV2-15 | T1/T2 | S2 | Fortschrittsskalar für PARETO undefiniert | OFFEN | Erweiterung geplant |
| KV2-16 | T2 | S1 | StopCondition SATURATION_CYCLES ohne Parameter | **BEHOBEN** | 30_rules §7.1 (SL-SIG-3) |
| KV2-17 | T1/T2 | S2 | valid_until-Ablauf vs. in-flight-Pakete undefiniert | **BEHOBEN** | 30_rules §13.3 (SL-PKG-2) |
| BIO-26 | T2 | S0 | Kontamination erzeugt plausibles Falsch-Positiv | OFFEN | (siehe KV2-13) |
| BIO-36 | T2 | S1 | Slot-Serialisierung: Bio-Parallelisierung nicht ausdrückbar | OFFEN | Batch-Semantik als Erweiterung geplant |
| DRY-05 | T3 | S0 | Regex-Safety erkennt FASTA/PDB-Toxine nicht | **BEHOBEN** | 30_rules §15 (SL-SAN-0 First-Order-Scan) |
| DRY-07 | T3 | S1 | Sunk-Cost-Blindheit bei Manifest-Änderung | **BEHOBEN** | 30_rules §10 (SL-PKG-2 Retro-Tag) |
| DRY-08 | T3 | S1 | Quarantäne-Auflösung ohne Rohdaten-Kontext | OFFEN | EvidenceBundle als Erweiterung geplant |
| DRY-09 | T3 | S2 | Lessons-Learned nie global (Amnesie) | **DESIGN FIXIERT** | 10_core §7 (Domain KB) |
| DRY-10 | T3 | S2 | CAPEX-VETOs führen zu stillem Archivieren | **BEHOBEN** | 30_rules §12 (SL-ESC-7) |
| K5-F-02 | T4 | S0 | Phasen-Override verliert gegen 30_rules | **BEHOBEN** | 40_control §3.4, 30_rules §1.2 |
| K5-F-16 | T4 | S1 | Kein SET_PHASE-Intent für Königin | **BEHOBEN** | 20_contracts §2.1, 30_rules §4 |
| K5-F-17 | T4 | S1 | Kein Phasen-Feld in HumanDirective | **BEHOBEN** | 20_contracts §9 |
| K5-F-18 | T4 | S0 | PHYSICAL_WAIT + CRISIS Stacking undefiniert | **BEHOBEN** | 40_control §3.1 |
| K5-F-20 | T4 | S1 | Missions- vs. Topic-Granularität | **BEHOBEN** | 40_control §2.3 |
| K5-F-25 | T4 | S0 | 15 SystemMode × MissionPhase Kombinationen undefiniert | **BEHOBEN** | 40_control §3.2 |
| K5-F-41 | T4 | S0 | UNLOCK_BUDGET in keiner Phase erlaubt | **BEHOBEN** | 40_control §5.1, 30_rules §3.1 |
| K5-F-42 | T4 | S1 | PIVOT_DOMAIN/DROP_SOFT_PREFERENCE blockiert | **BEHOBEN** | 40_control §5.1 |
| K5-F-43 | T4 | S1 | CALIBRATE_TWIN in PHYSICAL_WAIT blockiert | **BEHOBEN** | 40_control §5.1 |
| K5-F-48 | T4 | S0 | KV2-08-Fix (De-novo) mechanisch unwirksam | **BEHOBEN** | 30_rules §7.2 |
| K5-F-49 | T4 | S0 | KV2-01-Fix (Budget-Pause) mechanisch unwirksam | **BEHOBEN** | 30_rules §19.2 |

**Zählung:** 35 Funde insgesamt.
- **OFFEN:** 5 (KV2-07, KV2-13/BIO-26, KV2-15, BIO-36, DRY-08)
- **IN ARBEIT:** 0
- **DESIGN FIXIERT:** 3 (KV2-09, KV2-10, DRY-09)
- **BEHOBEN:** 27
- **AKZEPTIERT:** 0

---

## §4 Kompositions-Tests (Cross-Module Invariants)

Diese Tests müssen bei **jeder** Versions-Komposition durchgeführt werden. Da alle Module jetzt existieren, sind alle Tests ausführbar.

| ID | Test | Erwartung |
|----|------|-----------|
| COMP-01 | Parameter hat `owner_axis` in 40_control §4 | Single-Ownership-Lint besteht |
| COMP-02 | Regel in 30_rules ändert Parameter ohne Besitzer-Achse | Build-Fail |
| COMP-03 | SafetyAxis überstimmt andere Achsen | Safety-Gate ist absolut |
| COMP-04 | ControlState-Tupel ist immer gültig | Nur explizit ungültige Kombinationen werden verworfen |
| COMP-05 | 40_control referenziert Parameter aus 20_contracts | Parameter existiert und ist typkompatibel |
| COMP-06 | 30_rules referenziert Vertrag aus 20_contracts | Vertrag existiert und ist vollständig definiert |
| COMP-07 | 10_core definiert Rolle, 30_rules nutzt sie | Rolle existiert und Zugriffsregeln sind konsistent |
| COMP-08 | StrategicLayerConfig hat Default für jeden Parameter | Kein Parameter ist required ohne Default |
| COMP-09 | ControlStateLog referenziert Achsenwert | Wert existiert im Achsen-Enum |
| COMP-10 | Lade-Reihenfolge wird verletzt | Parser-Fehler |

---

## §5 Change-Log

| Version | Datum | Änderung | Funde behoben |
|---------|-------|----------|---------------|
| 1.0.0 | 2025-01-XX | Initiale modulare Struktur, Migration aus v0.2.0+v0.3.0, Phasen-Architektur | — |
| 1.1.0 | 2025-01-XX | 40_phases → 40_control: Phasen-Skalar durch 4 orthogonale Steuerachsen ersetzt | K5-F-02, -18, -25, -41, -48, -49 (Design) |
| 1.2.0 | 2025-01-XX | DT6-Bereinigung: Status "BEHOBEN" → "DESIGN FIXIERT"; KV2-13, KV2-16 ergänzt | K6-F-31, -32, -33, -34 |
| 1.2.1 | 2025-01-XX | Hygiene: Komposition auf 20_contracts@1.1.1 + 40_control@2.1.1 aktualisiert | K7R-F-01, K7R-F-02 |
| **1.3.0** | **2025-01-XX** | **Vollständige Komposition: 10_core@1.0.0 und 30_rules@1.0.0 aufgenommen; keine Phantom-Module mehr; Fund-Register finalisiert (27 BEHOBEN, 3 DESIGN FIXIERT, 5 OFFEN)** | **KV2-01..06, KV2-08, KV2-11, KV2-12, KV2-14, KV2-16, KV2-17, DRY-05, DRY-07, DRY-10, K5-F-02..49, K7-F-01..21, K7N-F-01..02, K7R-F-01..02** |

---

## §6 Anhang: Glossar

| Begriff | Definition |
|---------|------------|
| **Modul** | Selbstständige Spezifikationsdatei mit eigener Version |
| **Komposition** | Menge von Modulversionen, die ein System bilden |
| **ControlState** | Autoritatives Zustandstupel (safety, resource, research, governance) |
| **Steuerachse** | Eine der 4 orthogonalen Dimensionen des ControlState |
| **Parameter-Besitz-Matrix** | Deklaration, welche Achse welchen Parameter besitzt (40_control §4) |
| **DESIGN FIXIERT** | Fund ist durch die Architektur konzeptionell gelöst, aber die mechanische Implementierung als Erweiterung steht noch aus |

---

**Ende des Index-Moduls v1.3.0.**