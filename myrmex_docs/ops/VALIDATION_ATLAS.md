# 🗺️ VALIDATION_ATLAS — ATLAS-HYBRID TESTSTRATEGIE

| Feld | Wert |
| --- | --- |
| Dateiname | `ops/VALIDATION_ATLAS.md` |
| Version | `1.0.0-atlas-hyb.1` |
| Status | `ÄNDERUNGSANTRAG ATLAS-HYB-1.0.0 — nach Freigabe BINDEND` |
| System | `MYRMEX v2.4.0 + Questor v0.2.3 + HAL v0.2.0` |
| Schicht | `Layer 2 (ops/) — referenziert foundation/ und specs/` |
| Datum | `21. August 2026` |

§0 Geltung und Änderungsregeln

Dieses Dokument definiert die vollständige Teststrategie für das Atlas-Hybrid-System.

Regel: Dieses Dokument referenziert Verträge aus `CONTRACTS.md §6.10` und Sicherheitsregeln aus `CHARTER.md`.
Es definiert keine neuen Verträge und keine neuen Sicherheitsregeln.
Konfliktregel: Bei Widersprüchen gilt `CHARTER.md` > `CONTRACTS.md` > `specs/*` > `ops/VALIDATION.md` > dieses Dokument.

§1 Atlas-Hybrid-Test-Übersicht

§1.1 Zweck

Dieses Dokument definiert:
- Die vollständige Testpyramide für das Atlas-Hybrid-System
- Alle Atlas-spezifischen Test-Suiten (ATLAS-CTR, ATLAS-SEM, ATLAS-TOPO, ATLAS-INT, ATLAS-DIAG, ATLAS-SAF, ATLAS-FRNT, ATLAS-TOP, ATLAS-DOM)
- Testdaten, Fixtures und Mock-Strategie für Atlas-Tests
- Coverage-Ziele für Atlas-Module
- Akzeptanzkriterien für das Atlas-Hybrid-System

§1.2 Die sechs Atlas-Test-Grundprinzipien

| # | Prinzip | Bedeutung | CHARTER-Referenz |
| --- | --- | --- | --- |
| 1 | Deterministisch vor LLM | Atlas-Tests sind deterministisch. Keine echten LLM-Aufrufe. | CHARTER §SR-13 |
| 2 | Fail-Closed | Atlas-Tests prüfen Fail-Closed-Verhalten an allen kritischen Punkten. | CHARTER §SR-10 |
| 3 | Blackboard-Pattern | Atlas-Tests prüfen, dass keine direkten Aufrufe zwischen Gremium-Rängen erfolgen. | CHARTER §2 |
| 4 | Operational ≠ Scientific | Atlas-Tests prüfen die strikte Trennung von operationalen und wissenschaftlichen Fehlern. | CHARTER §SR-08 |
| 5 | Questor schreibt nicht in Atlas | Atlas-Tests prüfen, dass Questor keine Atlas-Signale schreibt. | CHARTER §SR-04 |
| 6 | Leere Zone ist UNEXPLORED | Atlas-Tests prüfen, dass leere Zonen niemals automatisch HEALTHY sind. | — |

§2 ATLAS-CTR — Vertrags-Tests (~15 Tests)

§2.1 Zweck

Diese Tests prüfen, dass alle Atlas-Hybrid-Verträge aus `CONTRACTS.md §6.10` Pydantic-v2-konform sind.

§2.2 Tests

| Test-ID | Test | Erwartet |
| --- | --- | --- |
| ATLAS-CTR-01 | `EvidenceQuality` validiert mit gültigen Werten | Pydantic-Validierung erfolgreich |
| ATLAS-CTR-02 | `EvidenceQuality` mit `source_confidence` außerhalb [0.0, 1.0] | Validierungsfehler |
| ATLAS-CTR-03 | `ValidityWindow` mit `valid_until` vor `valid_from` | Validierungsfehler |
| ATLAS-CTR-04 | `ReproducibilityContext` validiert mit gültigen Werten | Pydantic-Validierung erfolgreich |
| ATLAS-CTR-05 | `TypedDimension` mit `value_type = CATEGORICAL` und fehlenden `categories` | Validierungsfehler |
| ATLAS-CTR-06 | `ZoneGeometry` validiert mit gültigen Werten | Pydantic-Validierung erfolgreich |
| ATLAS-CTR-07 | `AtlasZoneSummary` mit `fracture_score = None` und `evidence_mass < min_evidence_mass` | Pydantic-Validierung erfolgreich |
| ATLAS-CTR-08 | `AtlasNode` mit `node_type = CRYSTAL` und `crystallized = false` | Validierungsfehler oder Warnung |
| ATLAS-CTR-09 | `AtlasEdge` mit fehlenden `evidence_refs` | Validierungsfehler |
| ATLAS-CTR-10 | `ObjectiveFamily` mit `priority_mode = PARETO` | Pydantic-Validierung erfolgreich |
| ATLAS-CTR-11 | `DiagnosticResolution` mit `outcome = EXPLAINS_CONTRADICTION` und fehlender `review_authority` | Validierungsfehler |
| ATLAS-CTR-12 | `SafetyConstraint` mit `active = true` | Pydantic-Validierung erfolgreich |
| ATLAS-CTR-13 | `FrontierCandidate` mit `frontier_score` außerhalb [0.0, 1.0] | Validierungsfehler |
| ATLAS-CTR-14 | `ResearchTopic` mit `state = SATURATED` | Pydantic-Validierung erfolgreich |
| ATLAS-CTR-15 | `AtlasHybridConfig` mit `degraded_threshold >= quarantine_threshold` | Validierungsfehler |

§3 ATLAS-SEM — Semantik-Tests (~20 Tests)

§3.1 Zweck

Diese Tests prüfen die Evidence-Semantik und die Erwartungsprüfung.

§3.2 Tests

| Test-ID | Test | Erwartet |
| --- | --- | --- |
| ATLAS-SEM-01 | VALIDATE mit Erwartung, Messwert innerhalb Toleranz | `confirms_expectation = True`, Signal 🟩 |
| ATLAS-SEM-02 | VALIDATE mit Erwartung, Messwert außerhalb Toleranz | `confirms_expectation = False`, Signal 🟨 |
| ATLAS-SEM-03 | VALIDATE ohne Erwartung | `confirms_expectation = None`, Signal ⬜ |
| ATLAS-SEM-04 | EXPLORE ohne Erwartung | `evidence_kind = EXPLORATORY_COVERAGE`, `coverage_energy` steigt |
| ATLAS-SEM-05 | DIAGNOSE mit `ist_diagnostic = true` | Signal 🟪, `diagnostic_energy` steigt |
| ATLAS-SEM-06 | ⬜ WEISS erzeugt `coverage_energy`, keine `support_energy` | `support_energy` unverändert, `coverage_energy` steigt |
| ATLAS-SEM-07 | 🟨 GELB erzeugt `conflict_energy` | `conflict_energy` steigt |
| ATLAS-SEM-08 | 🟥 ROT erzeugt `conflict_energy` und prüft `SafetyConstraint` | `conflict_energy` steigt, `SafetyConstraint` wird geprüft |
| ATLAS-SEM-09 | 🟪 diagnostic erzeugt `diagnostic_energy`, keine `conflict_energy` | `diagnostic_energy` steigt, `conflict_energy` unverändert |
| ATLAS-SEM-10 | 🟪 policy erzeugt `policy_energy`, keine `conflict_energy` | `policy_energy` steigt, `conflict_energy` unverändert |
| ATLAS-SEM-11 | `evidence_class = SANDBOX` bestätigt keinen physischen Kristall | Kristallisation wird blockiert |
| ATLAS-SEM-12 | `evidence_class = SIMULATION` bestätigt keinen physischen Kristall | Kristallisation wird blockiert |
| ATLAS-SEM-13 | `evidence_class = PHYSICAL_EXPERIMENT` kann physischen Kristall bestätigen | Kristallisation ist möglich |
| ATLAS-SEM-14 | OPERATIONALE Fehler erzeugen keine wissenschaftlichen Signale | Keine Signale, keine Kristalle |
| ATLAS-SEM-15 | SAFETY-Abbruch erzeugt keine Kristalle oder Signale | `kristall_kandidaten = []`, `signale_fuer_atlas = []` |
| ATLAS-SEM-16 | `confirms_expectation = None` erzeugt keine sichere Bestätigung | Kein 🟩, kein 🟨 |
| ATLAS-SEM-17 | `expectation_ref` fehlt bei VALIDATE | Fail-Closed, Idee wird verworfen oder auf EXPLORE reduziert |
| ATLAS-SEM-18 | `evidence_quality.sample_size = 1` reduziert `effective_weight` | `effective_weight` ist niedriger als bei `sample_size = 10` |
| ATLAS-SEM-19 | `evidence_quality.variance` hoch reduziert `effective_weight` | `effective_weight` ist niedriger als bei niedriger Varianz |
| ATLAS-SEM-20 | `decay(age_cycles)` reduziert altes Signal | Altes Signal hat niedrigeres `effective_weight` |

§4 ATLAS-TOPO — Topologie-Tests (~15 Tests)

§4.1 Zweck

Diese Tests prüfen die Topologie des Atlas: Dimensionen, Zonen, Knoten, Kanten.

§4.2 Tests

| Test-ID | Test | Erwartet |
| --- | --- | --- |
| ATLAS-TOPO-01 | `TypedDimension` mit `value_type = CONTINUOUS` und `value_range` | Zone wird korrekt erstellt |
| ATLAS-TOPO-02 | `TypedDimension` mit `value_type = CATEGORICAL` und `categories` | Zone wird korrekt erstellt |
| ATLAS-TOPO-03 | `TypedDimension` mit `value_type = ORDINAL` und `ordinal_levels` | Zone wird korrekt erstellt |
| ATLAS-TOPO-04 | `ConditionalRule` mit `if_dimension = solvent` und `if_value = water` | Bedingung wird korrekt angewendet |
| ATLAS-TOPO-05 | Katalysator A und B in verschiedenen Zonen | Keine falsche Fracture zwischen Zonen |
| ATLAS-TOPO-06 | `AtlasNode` mit `node_type = HYPOTHESIS` | Knoten wird korrekt erstellt |
| ATLAS-TOPO-07 | `AtlasNode` mit `node_type = CRYSTAL` und `crystallized = true` | Knoten wird korrekt erstellt |
| ATLAS-TOPO-08 | `AtlasEdge` mit `edge_type = SUPPORTS` | Kante wird korrekt erstellt |
| ATLAS-TOPO-09 | `AtlasEdge` mit `edge_type = CONTRADICTS` | Kante wird korrekt erstellt |
| ATLAS-TOPO-10 | `AtlasEdge` mit `edge_type = EXPLAINS` | Kante wird korrekt erstellt |
| ATLAS-TOPO-11 | `AtlasZoneSummary` mit `zone_state = UNEXPLORED` | Zone wird korrekt erstellt |
| ATLAS-TOPO-12 | `AtlasZoneSummary` mit `zone_state = LOCKED` | Zone wird korrekt erstellt |
| ATLAS-TOPO-13 | `AtlasZoneSummary` mit `quarantine_mode = true` | Zone wird korrekt erstellt |
| ATLAS-TOPO-14 | `AtlasZoneSummary` mit `full_rebuild_required = true` | Zone wird korrekt erstellt |
| ATLAS-TOPO-15 | Cluster mit `cluster_integration = false` für diagnostische Knoten | Diagnostische Knoten fließen nicht in normale Cluster ein |

§5 ATLAS-INT — Integritäts-Tests (~15 Tests)

§5.1 Zweck

Diese Tests prüfen die Integrität des Atlas: Fracture, Confidence, Uncertainty, Zone-Health.

§5.2 Tests

| Test-ID | Test | Erwartet |
| --- | --- | --- |
| ATLAS-INT-01 | Leere Zone ist `UNEXPLORED` | `zone_state = UNEXPLORED`, `fracture_score = None` |
| ATLAS-INT-02 | Zone mit `coverage_energy > 0` und `evidence_mass < min_evidence_mass` | `zone_state = EXPLORED_INCONCLUSIVE` |
| ATLAS-INT-03 | Zone mit `fracture_score >= degraded_threshold` | `zone_state = DEGRADED` |
| ATLAS-INT-04 | Zone mit `fracture_score >= quarantine_threshold` | `quarantine_mode = true` |
| ATLAS-INT-05 | Zone mit `fracture_score >= full_rebuild_threshold` | `full_rebuild_required = true`, `zone_state = CRITICAL` |
| ATLAS-INT-06 | Zone mit `support_confidence >= healthy_support_confidence` und `fracture_score < degraded_threshold` | `zone_state = HEALTHY` |
| ATLAS-INT-07 | `fracture_score` ist `None`, wenn `evidence_mass < min_evidence_mass` | `fracture_score = None` |
| ATLAS-INT-08 | `support_confidence` steigt mit `support_energy` | `support_confidence` steigt |
| ATLAS-INT-09 | `uncertainty_score` ist 1.0, wenn `evidence_mass == 0` | `uncertainty_score = 1.0` |
| ATLAS-INT-10 | `uncertainty_score` sinkt mit steigender `evidence_mass` | `uncertainty_score` sinkt |
| ATLAS-INT-11 | `crystallization_progress` steigt mit `support_energy` | `crystallization_progress` steigt |
| ATLAS-INT-12 | Kristallisation wird blockiert, wenn `fracture_score >= max_fracture_for_crystallization` | Kristallisation wird blockiert |
| ATLAS-INT-13 | Kristallisation wird blockiert, wenn `zone_state = LOCKED` | Kristallisation wird blockiert |
| ATLAS-INT-14 | Kristallisation wird blockiert, wenn `quarantine_mode = true` | Kristallisation wird blockiert |
| ATLAS-INT-15 | Kristallisation wird blockiert, wenn `evidence_class = SANDBOX` und keine physische Validierung | Kristallisation wird blockiert |

§6 ATLAS-DIAG — Diagnostik-Tests (~10 Tests)

§6.1 Zweck

Diese Tests prüfen die DiagnosticResolution und die Heilung von Fracture.

§6.2 Tests

| Test-ID | Test | Erwartet |
| --- | --- | --- |
| ATLAS-DIAG-01 | `DiagnosticResolution` mit `outcome = CONFIRMS_CONTRADICTION` | `fracture_score` bleibt relevant, Quarantäne bleibt bestehen |
| ATLAS-DIAG-02 | `DiagnosticResolution` mit `outcome = EXPLAINS_CONTRADICTION` und `review_authority` | `conflict_energy` wird auditiert reduziert |
| ATLAS-DIAG-03 | `DiagnosticResolution` mit `outcome = EXPLAINS_CONTRADICTION` ohne `review_authority` | Validierungsfehler |
| ATLAS-DIAG-04 | `DiagnosticResolution` mit `outcome = RESOLVES_CONTRADICTION` und `review_authority` | Quarantäne darf mit Governance-Freigabe aufgehoben werden |
| ATLAS-DIAG-05 | `DiagnosticResolution` mit `outcome = INCONCLUSIVE` | Keine automatische Heilung |
| ATLAS-DIAG-06 | `DiagnosticResolution` mit `outcome = EXPLAINS_CONTRADICTION` löscht keine Evidenz | Append-Only bleibt erhalten |
| ATLAS-DIAG-07 | `DiagnosticResolution` mit `outcome = EXPLAINS_CONTRADICTION` erzeugt `EXPLAINS`-Kante | Kante wird erstellt |
| ATLAS-DIAG-08 | Diagnostic-Kristall mit `ist_diagnostic = true` und `cluster_integration = false` | Kristall fließt nicht in normale Cluster ein |
| ATLAS-DIAG-09 | Diagnostic-Waypoint mit `required_gate_mode = FRACTURE_DIAGNOSIS` | Waypoint wird korrekt erstellt |
| ATLAS-DIAG-10 | Diagnostic-Waypoint ohne Diagnose-Budget | Waypoint wird verworfen |

§7 ATLAS-SAF — Sicherheits-Tests (~10 Tests)

§7.1 Zweck

Diese Tests prüfen die SafetyConstraints, ExclusionConstraints und LOCKED-Zustände.

§7.2 Tests

| Test-ID | Test | Erwartet |
| --- | --- | --- |
| ATLAS-SAF-01 | `SafetyConstraint` mit `active = true` | `frontier_score = 0`, keine normale Exploration |
| ATLAS-SAF-02 | `SafetyConstraint` unterliegt keinem automatischen Decay | `SafetyConstraint` bleibt aktiv |
| ATLAS-SAF-03 | `SafetyConstraint` mit `requires_manual_clearance = true` | Nur manuelle Freigabe kann `SafetyConstraint` aufheben |
| ATLAS-SAF-04 | `SafetyConstraint` mit `cleared_by` und `cleared_at` | `SafetyConstraint` wird aufgehoben |
| ATLAS-SAF-05 | `ExclusionConstraint` mit `hard_limit = true` | Region darf nicht normal exploriert werden |
| ATLAS-SAF-06 | `ExclusionConstraint` mit `hard_limit = false` | Region darf nur mit erhöhter Vorsicht betreten werden |
| ATLAS-SAF-07 | Zone mit `zone_state = LOCKED` | Keine normale Frontier, keine normale Exploration |
| ATLAS-SAF-08 | Zone mit `zone_state = LOCKED` und `SafetyConstraint` | `LOCKED` überschreibt alle Frontier-Freigaben |
| ATLAS-SAF-09 | `SafetyConstraint` mit `severity = CRITICAL` | Höchste Priorität, keine Ausnahme |
| ATLAS-SAF-10 | `SafetyConstraint` wird durch Questor nicht aufgelöst | Questor darf `SafetyConstraint` nicht auflösen |

§8 ATLAS-FRNT — Frontier-Tests (~15 Tests)

§8.1 Zweck

Diese Tests prüfen die FrontierEngine und die FrontierCandidates.

§8.2 Tests

| Test-ID | Test | Erwartet |
| --- | --- | --- |
| ATLAS-FRNT-01 | FrontierEngine erzeugt `FrontierCandidate` für Weißraum | `frontier_type = WEISSRAUM` |
| ATLAS-FRNT-02 | FrontierEngine erzeugt `FrontierCandidate` für Widerspruchslücke | `frontier_type = CONTRADICTION_GAP` |
| ATLAS-FRNT-03 | FrontierEngine erzeugt `FrontierCandidate` für Brücken-Frontier | `frontier_type = BRIDGE_FRONTIER` |
| ATLAS-FRNT-04 | FrontierEngine erzeugt `FrontierCandidate` für Diagnose-Frontier | `frontier_type = DIAGNOSTIC_FRONTIER` |
| ATLAS-FRNT-05 | FrontierEngine erzeugt `FrontierCandidate` für tiefe Unsicherheit | `frontier_type = DEEP_UNCERTAIN` |
| ATLAS-FRNT-06 | `FrontierCandidate` enthält `FrontierRationale` | `rationale` ist vorhanden und maschinenlesbar |
| ATLAS-FRNT-07 | `FrontierCandidate` mit `safety_status = BLOCKED` | `frontier_score = 0` |
| ATLAS-FRNT-08 | `FrontierCandidate` mit `safety_status = RESTRICTED` | `frontier_score` wird reduziert |
| ATLAS-FRNT-09 | `FrontierCandidate` mit `safety_status = CLEAR` | `frontier_score` wird nicht reduziert |
| ATLAS-FRNT-10 | FrontierEngine mit `zone_state = LOCKED` | Keine Frontier wird erzeugt |
| ATLAS-FRNT-11 | FrontierEngine mit `SafetyConstraint` | Keine Frontier wird erzeugt |
| ATLAS-FRNT-12 | FrontierEngine mit `ExclusionConstraint` und `hard_limit = true` | Keine Frontier wird erzeugt |
| ATLAS-FRNT-13 | FrontierEngine mit `quarantine_mode = true` und Diagnose-Budget | Nur Diagnose-Frontiers werden erzeugt |
| ATLAS-FRNT-14 | FrontierEngine mit `quarantine_mode = true` ohne Diagnose-Budget | Keine Frontier wird erzeugt |
| ATLAS-FRNT-15 | FrontierEngine mit `full_rebuild_required = true` | Keine Frontier wird erzeugt |

§9 ATLAS-TOP — Themen-Tests (~10 Tests)

§9.1 Zweck

Diese Tests prüfen die ResearchTopics und die ExplorationPolicy.

§9.2 Tests

| Test-ID | Test | Erwartet |
| --- | --- | --- |
| ATLAS-TOP-01 | `ResearchTopic` mit `state = PROPOSED` | Topic wird korrekt erstellt |
| ATLAS-TOP-02 | `ResearchTopic` mit `state = ACTIVE` | Topic wird korrekt erstellt |
| ATLAS-TOP-03 | `ResearchTopic` mit `state = SATURATED` | Topic wird korrekt erstellt |
| ATLAS-TOP-04 | `ResearchTopic` mit `state = BLOCKED` | Topic wird korrekt erstellt |
| ATLAS-TOP-05 | `ResearchTopic` mit `state = ARCHIVED` | Topic wird korrekt erstellt |
| ATLAS-TOP-06 | `ResearchTopic` wird deterministisch auf `SATURATED` gesetzt | Keine LLM-Entscheidung |
| ATLAS-TOP-07 | `ExplorationPolicy` mit `exploitation_weight`, `exploration_weight`, `diagnostic_weight` | Policy wird korrekt erstellt |
| ATLAS-TOP-08 | `ExplorationPolicy` wird durch Kanzler gesetzt | Keine LLM-Entscheidung |
| ATLAS-TOP-09 | `ExplorationPolicy` mit `score_weights` | Score-Berechnung verwendet die Gewichte |
| ATLAS-TOP-10 | `ResearchTopic` mit `stop_conditions` | Topic wird bei Erfüllung der Bedingungen auf `SATURATED` gesetzt |

§10 ATLAS-DOM — Domänen-Tests (~10 Tests)

§10.1 Zweck

Diese Tests prüfen die Integration des Atlas-Hybrid-Systems mit den vier Domänen: Chemie, Biologie, Physik, ML.

§10.2 Tests

| Test-ID | Test | Erwartet |
| --- | --- | --- |
| ATLAS-DOM-01 | Chemie: Katalysator-Temperatur-Optimierung | Katalysator A und B erzeugen keine falsche Fracture |
| ATLAS-DOM-02 | Chemie: Multi-Objective Trade-off (Yield vs. Purity) | Trade-off erzeugt keine Fracture |
| ATLAS-DOM-03 | Biologie: Zellkultur-Inkubation | Batch-Effekte werden über `ReproducibilityContext` geführt |
| ATLAS-DOM-04 | Biologie: Diagnose findet kontaminierte Charge | `DiagnosticResolution` mit `outcome = EXPLAINS_CONTRADICTION` |
| ATLAS-DOM-05 | Physik: Sensor-Kalibrierung | Messunsicherheit wird über `EvidenceQuality` geführt |
| ATLAS-DOM-06 | Physik: Kalibrierung mit `ValidityWindow` | Kalibrierung läuft nach `valid_until` ab |
| ATLAS-DOM-07 | Physik: Hardware-Interlock | `SafetyConstraint` wird erstellt, kein automatischer Decay |
| ATLAS-DOM-08 | ML: Hyperparameter-Optimierung | OOM bleibt OPERATIONAL, keine wissenschaftlichen Signale |
| ATLAS-DOM-09 | ML: Dataset-Version als Artefakt | `ReproducibilityContext` enthält `dataset_version` |
| ATLAS-DOM-10 | ML: Sandbox-Evidenz bestätigt keinen physischen Kristall | `evidence_class = SANDBOX` blockiert Kristallisation |

§11 Test-Fixtures und Mocks

§11.1 Test-Fixture-Struktur

```text
tests/
  └── test_atlas/
      ├── fixtures/
      │   ├── zones/
      │   │   ├── empty_zone.json
      │   │   ├── healthy_zone.json
      │   │   ├── degraded_zone.json
      │   │   ├── quarantined_zone.json
      │   │   └── locked_zone.json
      │   ├── nodes/
      │   │   ├── hypothesis_node.json
      │   │   ├── crystal_node.json
      │   │   └── frontier_anchor_node.json
      │   ├── signals/
      │   │   ├── green_signal.json
      │   │   ├── yellow_signal.json
      │   │   ├── red_signal.json
      │   │   ├── purple_diagnostic_signal.json
      │   │   ├── purple_policy_signal.json
      │   │   └── white_signal.json
      │   ├── frontiers/
      │   │   ├── weissraum_frontier.json
      │   │   ├── contradiction_gap_frontier.json
      │   │   └── diagnostic_frontier.json
      │   └── topics/
      │       ├── active_topic.json
      │       ├── saturated_topic.json
      │       └── blocked_topic.json
      ├── mocks/
      │   ├── mock_archivar.py
      │   ├── mock_kartograph.py
      │   └── mock_frontier_engine.py
      └── conftest.py
```

§11.2 Mock-Strategie

| Mock | Zweck |
| --- | --- |
| `mock_archivar.py` | Simuliert Archivar-Verhalten (Empfang von `questor_ergebnis_paket`) |
| `mock_kartograph.py` | Simuliert Kartograph-Verhalten (Atlas-Strukturierung) |
| `mock_frontier_engine.py` | Simuliert FrontierEngine-Verhalten (Frontier-Erzeugung) |

§12 Coverage-Ziele

§12.1 Mindestabdeckung pro Atlas-Modul

| Modul | Mindestabdeckung | Begründung |
| --- | --- | --- |
| `atlas_core.py` | 90% | Kernlogik des Atlas |
| `atlas_topology.py` | 85% | Topologie-Logik |
| `atlas_integrity.py` | 90% | Integritäts-Logik |
| `atlas_diagnostic.py` | 90% | Diagnostik-Logik |
| `atlas_safety.py` | 95% | Sicherheitskritisch |
| `atlas_frontier.py` | 85% | Frontier-Logik |
| `atlas_topic.py` | 80% | Themen-Logik |
| Gesamt | ≥ 88% | |

§12.2 Coverage-Regeln

| Regel | Beschreibung |
| --- | --- |
| ATLAS-COV-1 | Sicherheitskritische Atlas-Module haben ≥ 95% Abdeckung. |
| ATLAS-COV-2 | Kernlogik hat ≥ 85% Abdeckung. |
| ATLAS-COV-3 | Jeder Fail-Closed-Punkt muss getestet sein. |
| ATLAS-COV-4 | Jeder Edge Case muss getestet sein. |
| ATLAS-COV-5 | Jede Fehlerbehandlung muss getestet sein. |
| ATLAS-COV-6 | Jeder Zustandsübergang muss getestet sein. |

§13 Test-Gates für Atlas-Hybrid

| Gate | Bedingung |
| --- | --- |
| GATE-ATLAS-1 | Alle ATLAS-CTR-Tests bestehen |
| GATE-ATLAS-2 | Alle ATLAS-SEM-Tests bestehen |
| GATE-ATLAS-3 | Alle ATLAS-TOPO-Tests bestehen |
| GATE-ATLAS-4 | Alle ATLAS-INT-Tests bestehen |
| GATE-ATLAS-5 | Alle ATLAS-DIAG-Tests bestehen |
| GATE-ATLAS-6 | Alle ATLAS-SAF-Tests bestehen |
| GATE-ATLAS-7 | Alle ATLAS-FRNT-Tests bestehen |
| GATE-ATLAS-8 | Alle ATLAS-TOP-Tests bestehen |
| GATE-ATLAS-9 | Alle ATLAS-DOM-Tests bestehen |
| GATE-ATLAS-10 | Coverage ≥ 88% für Atlas-Module |

§14 Kritische Warnungen für Atlas-Tests

§14.1 Nicht alte Atlas-Logik testen

Wenn ein Test die alte Atlas-Logik (Signal-Resolution nach Priorität, Kristallisation nach 3 Bestätigungen) erwartet, ist der Test falsch.

§14.2 Keine Questor-Atlas-Schreibrechte

Wenn ein Test erwartet, dass Questor direkt in den Atlas schreibt, ist der Test falsch.
→ Siehe CHARTER §SR-04.

§14.3 Keine wissenschaftlichen Signale aus operationalen Fehlern

Wenn ein Test OOM, Timeout oder Lease-Konflikt als wissenschaftliches Signal interpretiert, ist der Test falsch.
→ Siehe CHARTER §SR-08.

§14.4 Leere Zone ist UNEXPLORED

Wenn ein Test erwartet, dass eine leere Zone automatisch HEALTHY ist, ist der Test falsch.

§14.5 SafetyConstraint unterliegt keinem Decay

Wenn ein Test erwartet, dass ein SafetyConstraint nach einer bestimmten Zeit automatisch aufgehoben wird, ist der Test falsch.

§14.6 DiagnosticResolution löscht keine Evidenz

Wenn ein Test erwartet, dass eine DiagnosticResolution Evidenz löscht, ist der Test falsch.
Append-Only bleibt erhalten.

§14.7 FrontierCandidate ist keine Ausführungsfreigabe

Wenn ein Test erwartet, dass ein FrontierCandidate direkt ausgeführt wird, ist der Test falsch.
FrontierCandidates sind Empfehlungen, keine Ausführungsfreigaben.

§15 Zusammenfassung der Atlas-Test-Spezifikation

| Aspekt | Definition |
| --- | --- |
| Test-Suiten | ATLAS-CTR, ATLAS-SEM, ATLAS-TOPO, ATLAS-INT, ATLAS-DIAG, ATLAS-SAF, ATLAS-FRNT, ATLAS-TOP, ATLAS-DOM |
| Gesamt-Tests | ~120 |
| Coverage-Ziel | ≥ 88% für Atlas-Module |
| Test-Gates | 10 Gates |
| Akzeptanzkriterien | 10 Kriterien |
| Kritische Warnungen | 7 Warnungen |

§16 Dokumentenhierarchie

Dieses Dokument steht in der Schicht `ops/` und referenziert:
- `foundation/CHARTER.md` für Sicherheitsregeln (CHARTER §SR-XX)
- `foundation/CONTRACTS.md` für Datenverträge (CONTRACTS §6.10)
- `specs/GREMIUM.md` für Gremium-spezifische Details
- `specs/QUESTOR.md` für Questor-spezifische Details
- `ops/VALIDATION.md` für die übergeordnete Teststrategie

Regel: Änderungen an Atlas-Test-Suiten in diesem Dokument erfordern eine Versionsänderung und eine Überprüfung der referenzierten Dokumente.