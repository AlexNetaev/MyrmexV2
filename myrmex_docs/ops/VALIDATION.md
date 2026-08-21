# 🧪 VALIDATION — TESTSTRATEGIE UND AKZEPTANZKRITERIEN

| Feld | Wert |
| :--- | :--- |
| **Dateiname** | `ops/VALIDATION.md` |
| **Version** | 1.0.0 (New Architecture) |
| **Status** | **BINDEND** — Teststrategie und Akzeptanzkriterien |
| **System** | MYRMEX v2.4.0 + Questor v0.2.3 + HAL v0.2.0 |
| **Schicht** | Layer 2 (ops/) — referenziert foundation/ und specs/ |
| **Datum** | 21. August 2026 |

---

## 0. Geltung und Änderungsregeln

Dieses Dokument definiert die vollständige Teststrategie für das Gesamtsystem.

**Regel:** Dieses Dokument referenziert Verträge aus `CONTRACTS.md` und Sicherheitsregeln aus `CHARTER.md`.
Es definiert keine neuen Verträge und keine neuen Sicherheitsregeln.

**Konfliktregel:** Bei Widersprüchen gilt `CHARTER.md` > `CONTRACTS.md` > `specs/*` > dieses Dokument.

---

## §1 Validierungs-Übersicht und Grundprinzipien

### §1.1 Zweck

Dieses Dokument definiert:
- Die vollständige Testpyramide für MYRMEX v2.4.0 + Questor v0.2.3 + HAL v0.2.0
- Alle bestehenden Test-Suiten (N, I, S, R, Z, H)
- Alle neuen Questor-spezifischen Test-Suiten (Q-U, Q-C, Q-S, Q-P, Q-T)
- Testdaten, Fixtures und Mock-Strategie
- Coverage-Ziele
- Test-Infrastruktur und CI/CD
- Akzeptanzkriterien für das Gesamtsystem

### §1.2 Die sechs Test-Grundprinzipien

| # | Prinzip | Bedeutung | CHARTER-Referenz |
| :--- | :--- | :--- | :--- |
| 1 | **Deterministisch vor LLM** | Tests sind deterministisch. Keine echten LLM-Aufrufe. | CHARTER §SR-13 |
| 2 | **Fail-Closed** | Tests prüfen Fail-Closed-Verhalten an allen kritischen Punkten. | CHARTER §SR-10 |
| 3 | **Blackboard-Pattern** | Tests prüfen, dass keine direkten Aufrufe zwischen Gremium-Rängen erfolgen. | CHARTER §2 |
| 4 | **Keine produktiven Altbezeichnungen** | Tests prüfen, dass keine alten Swarm-Begriffe in produktiven Quellen vorkommen. | — |
| 5 | **Operational ≠ Scientific** | Tests prüfen die strikte Trennung von operationalen und wissenschaftlichen Fehlern. | CHARTER §SR-08 |
| 6 | **ESTOP ≠ LEASE_DENIED** | Tests prüfen die strikte Trennung von ESTOP und LEASE_DENIED. | CHARTER §SR-09 |

### §1.3 Rolle der Test-KI

Die Test-KI handelt als:
- Senior Test Engineer
- Systems Integration Reviewer
- Dry-Run Auditor
- Architektur-Reviewer
- HAL-Integration-Reviewer

### §1.4 Dry-Run-Modus

Wenn keine Implementierungsfreigabe gegeben ist:
- kein Code
- keine Dateiänderungen
- keine pytest-Ausführung
- mentale Simulation
- Bewertung mit `BESTANDEN` / `NICHT BESTANDEN`
- Blocker und Nicht-Blocker getrennt melden
- keine stillschweigenden Annahmen bei unklaren Spezifikationslücken

Wenn kein produktives Repository übergeben wurde:
- N-01 kann nur spezifikationsbasiert bewertet werden
- der spätere reale Source-Scan ist als Implementierungsbedingung zu nennen
- das Fehlen eines Repositories ist im Dry-Run eine Modusbedingung, kein Architekturfehler

### §1.5 Implementierungsmodus

Wenn eine Phase explizit freigegeben ist:
- nur die freigegebene Phase implementieren
- pytest verwenden
- keine späteren Phasen vorziehen
- nach jeder Phase Status-Report schreiben
- reale Source-Scans für N-01 durchführen, sobald produktive Quellen existieren

---

## §2 Testpyramide

### §2.1 Visuelle Darstellung

```
                    /\
                   /  \
                  / E2E \          ← Suite S (5 Tests, existiert)
                 /________\
                /          \
               / Integration\      ← Suite I (18 Tests, existiert)
              /______________\
             /                \
            /   Komponententests\    ← NEU: ~44 Tests
           /____________________\
          /                      \
         /      Unit-Tests       \  ← NEU: ~252 Tests
        /__________________________\
       /                            \
      /    Sicherheit / Performance  \  ← NEU: ~51 Tests
     /________________________________\
```

### §2.2 Test-Verteilung

| Ebene | Anzahl | Anteil | Zweck |
| :--- | :--- | :--- | :--- |
| Unit-Tests | ~252 | 60% | Einzelne Funktionen und Klassen |
| Komponententests | ~44 | 10% | Zusammenspiel mehrerer Module |
| Sicherheitstests | ~30 | 7% | Sicherheitskritische Pfade |
| Performance-/Stress-Tests | ~21 | 5% | Last, Latenz, Ressourcen |
| Integrationstests (bestehend) | 18 | 4% | Questor ↔ Gremium (Suite I) |
| Szenario-Tests (bestehend) | 5 | 1% | End-to-End (Suite S) |
| Sonstige bestehende Tests | 51 | 12% | Suite N, R, Z, H |
| **Gesamt** | **~421** | **100%** | |

### §2.3 Test-Suiten-Übersicht

| Suite | Tests | Status | Zweck |
| :--- | :--- | :--- | :--- |
| Suite N | 7 | Existiert | Naming & Contract Migration |
| Suite I | 18 | Existiert | Integration |
| Suite S | 5 | Existiert | Szenario-Pflichttests |
| Suite R | 12 | Existiert | Regressions-Tests |
| Suite Z | 8 | Existiert | Zielpräzisierung |
| Suite H | 24 | Existiert | HAL v0.2.0 |
| Suite Q-U | ~252 | NEU | Questor Unit-Tests |
| Suite Q-C | ~44 | NEU | Questor Komponententests |
| Suite Q-S | ~30 | NEU | Questor Sicherheits-Tests |
| Suite Q-P | ~10 | NEU | Questor Performance-Tests |
| Suite Q-T | ~11 | NEU | Questor Stress-Tests |
| **Gesamt** | **~421** | | |

---

## §3 Bestehende Test-Suiten

### §3.1 Suite N — Naming & Contract Migration (7 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| N-01 | Keine produktiven Altbezeichnungen | Keine Treffer in produktiven Quellen. Treffer nur in Migrations-/Archiv-/Testdokumenten oder Allowlists erlaubt. Keine aktive Adapterlogik. |
| N-02 | QuestorErgebnisPaket validiert | Pydantic-Validierung erfolgreich. `questor_instance_id` vorhanden. `sequence_number` vorhanden. `idempotency_key` korrekt kanonisch gebildet. `questor_metadata` optional. Keine freien Zusatzfelder außerhalb von `questor_metadata`. |
| N-03 | Archivar nutzt questor_instance_id | Monotone Sequence wird akzeptiert. Doppelte oder rückläufige Sequence wird abgelehnt. Keine alte Instanz-ID wird geprüft. |
| N-04 | Dispatcher baut Envelope | Erzeugt `QuestorDispatchEnvelope`. Sendet nicht nacktes `ResearchPackage` im Produktivpfad. Envelope enthält `gate_record_ref`. Envelope enthält konsistente Lease- und Security-Angaben. |
| N-05 | Direkte Pakete sind sandbox-only | Nur erlaubt, wenn Test-/Dev-Konfiguration aktiv ist. `security_mode = DEV_SANDBOX_ONLY`. Keine physische Ausführung. Standardmäßig: `DIRECT_PACKAGE_FORBIDDEN`. |
| N-06 | QuestorMetadata wird nicht wissenschaftlich interpretiert | Keine Kristalle aus `questor_metadata`. Keine Signale aus `questor_metadata`. `operational_metrics` dürfen nur operational verarbeitet werden. |
| N-07 | Blackbox liegt außerhalb der Gremium-Daten | Nicht unter `data/archiv/`. Nicht unter `data/atlas/`. Nicht unter `data/operational_logs/`. Nur unter `data/questor_blackbox/` oder äquivalent isoliert. |

### §3.2 Suite I — Integration (18 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| I-01 | Happy Path Szenario A | Questor führt aus. Ergebnis: `status: erfolgreich`, `abbruch_grund: null`, `abbruch_klasse: OPERATIONAL`. Archivar empfängt Ergebnis. Kristallkandidaten werden verarbeitet. Keine Blackbox-Inhalte im Gremium. |
| I-02 | Invalides Paket | Questor bricht ab. Vollständiges Ergebnis: `status: abgebrochen`, `abbruch_grund: PACKAGE_INVALID`, `abbruch_klasse: OPERATIONAL`, `vollstaendig_flag: true`. Archivar kann Ergebnis verarbeiten. Keine HAL-Aktion. |
| I-03 | Direktes ResearchPackage verboten | `abbruch_grund: DIRECT_PACKAGE_FORBIDDEN`. `abbruch_klasse: OPERATIONAL`. Vollständiges Ergebnis. |
| I-04 | Envelope ohne gate_record_ref | `abbruch_grund: PACKAGE_INVALID`. `abbruch_klasse: OPERATIONAL`. Vollständiges Ergebnis. |
| I-05 | LEASE_DENIED ohne ESTOP | Zweites Paket erhält `LEASE_DENIED`. Kein ESTOP. Keine `SAFETY`-Klasse. Paket wartet oder bricht operational ab. |
| I-06 | LEASE_QUEUED Timeout | Kein unbegrenztes Warten. Abbruch: `abbruch_grund: LEASE_QUEUED_TIMEOUT`, `abbruch_klasse: OPERATIONAL`. Oder sicherer Sandbox-Fallback gemäß Policy. |
| I-07 | ESTOP während Questor-Ausführung | Aktive Commands stoppen. Leases werden `ESTOP_SUSPENDED`. Ergebnis: `status: abgebrochen`, `abbruch_grund: ESTOP_RECEIVED`, `abbruch_klasse: SAFETY`. Blackbox erhält `SAFETY_HOLD`. Gremium erhält keine Blackbox. |
| I-08 | Operativer Crash OOM | `status: abgebrochen`. `abbruch_grund: OOM`. `abbruch_klasse: OPERATIONAL`. Keine wissenschaftlichen Signale. Optional `resource_pressure_event` durch Gremium/Archivar. |
| I-09 | Wissenschaftlicher Fehlschlag | `status: fehlgeschlagen`. `abbruch_grund: TARGET_NOT_REACHED`. `abbruch_klasse: SCIENTIFIC`. Signalvorschläge erlaubt. Kristallkandidaten möglich. |
| I-10 | Routing-Loop-Schutz | `max_loop_iterations` wird respektiert. Abbruch: `abbruch_grund: ROUTING_LOOP_TIMEOUT`, `abbruch_klasse: OPERATIONAL`. |
| I-11 | Unbekannte Dimension ohne Approval | Keine physische Ausführung. Sandbox/Simulation erlaubt, falls konfiguriert. Sonst: `abbruch_grund: DIMENSION_APPROVAL_MISSING`, `abbruch_klasse: OPERATIONAL`. |
| I-12 | Fracture Diagnosis | Zone ist in QUARANTÄNE, Paket hat `gate_mode = FRACTURE_DIAGNOSIS`. Questor darf diagnostic-safe ausführen. Ergebnis kann diagnostische Kristallkandidaten enthalten. Diagnose-Kristalle werden nicht in normale Cluster-Berechnung übernommen. |
| I-13 | FULL_REBUILD während Questor läuft | Laufendes Paket referenziert alte `atlas_version_id`. `observed_atlas_version_id` bleibt alt. Neuer `atlas_head_pointer` gilt nur für neue Pakete. Keine Invalidierung laufender Quests. |
| I-14 | SAFE_MODE und Questor | Menschliche Königin löst SAFE_MODE aus. Keine neuen Dispatches. Keine neuen Pakete. Keine neue Exploration. Laufende risikoarme Quests dürfen kontrolliert abschließen. Riskante Quests werden pausiert oder sicher abgebrochen. |
| I-15 | Idempotenz im Archivar | Dasselbe `questor_ergebnis_paket` wird zweimal übergeben. Duplikat wird verworfen. Kein doppelter Kristall. Kein doppeltes Signal. Kanonischer `idempotency_key` wird korrekt verglichen. |
| I-16 | Sequence-Recovery nach Questor-Crash | Questor stirbt nach Sequence 7. Nächste Sequence ist 8. Keine Doppelnummer. Keine ungeklärte Lücke. Falls unsicher: `RECOVERY_UNSAFE`. |
| I-17 | Prompt-Injection im Paketkontext | `kontext` enthält eine Anweisung, Sicherheitsregeln zu ignorieren und physische Messung auszuführen. Questor führt keine sicherheitswidrige Aktion aus. LLM-Vorschläge werden verworfen. Keine physische Ausführung ohne deterministische Freigabe. |
| I-18 | Blackbox-Isolation | Gremium-Komponente versucht, QuestorBlackbox zu lesen. Zugriff ist vertraglich verboten. Ergebnis enthält maximal `LocalAuditRef`. Keine Blackbox-Inhalte im Gremium. |

### §3.3 Suite S — Szenario-Pflichttests (5 Tests)

| Test-ID | Szenario | Fokus |
| :--- | :--- | :--- |
| S-A | Chemie — Kinetik-Optimierung | Happy Path, Envelope, Lease, HAL, Archivar, Kristallkandidaten |
| S-B | Biologie — Zellkultur / UV-Exposition | Routing-Schleife, `max_loop_iterations`, LEASE_DENIED, keine ESTOP durch Ressourcenkonflikt, Langzeit-Prozess mit SAFE_HOLD |
| S-C | Materialwissenschaft — Katalysator-Entdeckung | Gefahren, ESTOP, SAFETY_HOLD, Sicherheitsklassifikation, Hardware-Interlock |
| S-D | Trockenlabor — Hyperparameter-Optimierung | Compute-Job, OOM, operational vs scientific, resource_pressure_metric, CUDA_OOM als OPERATIONAL |
| S-E | Fraktur | Gelbe Fraktur, QUARANTÄNE, FRACTURE_DIAGNOSIS, diagnostische Kristalle, keine normale Cluster-Verzerrung |

### §3.4 Suite R — Regressions-Tests aus v2.3.1 (12 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| R-01 | Crash in Stufe 6 | Recovery bleibt in Stufe 7, nicht Stufe 8. Kein vorzeitiger Questor-Dispatch. |
| R-02 | Slot-Konflikt | LEASE_DENIED. Kein ESTOP. Questor behandelt operational. |
| R-03 | Seher-Halluzination | Veto ohne Evidenz → `SEHER_INVALID_VETO`. Keine blinde Freigabe. Bei Kanzler-Bestätigung Policy-Veto statt rotem Signal. |
| R-04 | Dimensions-Expansion | PROPOSED_BY_IDEA → PROPOSED_BY_WAYPOINT → APPROVED_BEFORE_EXECUTION. Questor blockiert physische Ausführung ohne Approval. |
| R-05 | Gelbe Fraktur | Fraktur-Event korrekt erzeugt. fracture_score korrekt. FRACTURE_DIAGNOSIS möglich. Diagnostische Kristalle bleiben speziell. |
| R-06 | ESTOP vs LEASE_DENIED | Ressourcenkonflikt nie ESTOP. Physikalische Gefahr immer ESTOP. Leases bei ESTOP suspended. |
| R-07 | Operativer Crash | OOM → operational. Kein wissenschaftliches Signal. Optional resource_pressure_event. |
| R-08 | FULL_REBUILD unter Last | Laufende Quests referenzieren alte Atlas-Version. Neuer Head gilt nur für neue Pakete. Alte Version bleibt lesbar. |
| R-09 | Königin-Konflikt | SAFE_MODE. Keine neuen Questor-Dispatches. Menschliche Königin wird nicht überstimmt. |
| R-10 | Totaler Seher-Block | Circuit-Breaker greift. Zustände `SHADOW_MODE`, `TEMP_SUSPENDED` oder `PERMANENT_SUSPENDED` sind explizit definiert. Zustandswechsel werden protokolliert. Automatische Zustandswechsel erfolgen nur bei ausreichender Stichprobe. Rückkehr nach NORMAL erfordert Hysterese und manuelle Prüfung. |
| R-11 | Routing-Loop-Schutz | `max_loop_iterations`. `branch_condition_timeout`. `ROUTING_LOOP_TIMEOUT`. |
| R-12 | Policy-Veto-Review | Review nach `policy_veto_review_interval_cycles`. Standardwert ist 20. Wertebereich ist 1 bis 500. 0 ist ungültig. Review kann bestätigen, aufheben oder eskalieren. Review wird protokolliert. |

### §3.5 Suite Z — Zielpräzisierung (8 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| Z-01 | Kanonische Referenz und Begleitdokument | `structure_standalone_v2.4.0.md` Version 1.1.1 ist primäre Referenz. `structure_hal_v0.2.0.md` ist HAL-spezifische Referenz. `structure_standalone_questor_v0.2.3.md` ist unterstützendes Begleitdokument. Konfliktauflösung ist definiert. Formulierungen im Begleitdokument, die eine primäre Gesamtreferenz beanspruchen, sind nicht bindend. |
| Z-02 | Idempotency-Key-Kanonicalisierung und attempt_id | `idempotency_key = package_id:zyklus_id:attempt_id`. Keine Whitespace. Keine mehrdeutige Serialisierung. `package_id` und `zyklus_id` entsprechen dem erlaubten Regex. `attempt_id >= 0`. `attempt_id <= 999999`. Führende Nullen sind in der kanonischen Form verboten. Maximale Länge des Keys ist 264 Zeichen. Ungültige Eingaben führen zu `PACKAGE_INVALID`. |
| Z-03 | Erfolgssemantik von abbruch_klasse | `status: erfolgreich`. `abbruch_grund: null`. `abbruch_klasse: OPERATIONAL`. Die Semantik ist als Ergebnisklasse dokumentiert. `abbruch_klasse` darf bei Erfolg nicht als tatsächlicher Abbruch interpretiert werden. |
| Z-04 | Circuit-Breaker-Zustände und Metrikfenster | Zustände: `NORMAL`, `SHADOW_MODE`, `TEMP_SUSPENDED`, `PERMANENT_SUSPENDED`. Messfenster ist definiert. Mindeststichprobe ist definiert. Automatische Zustandswechsel erfolgen nur bei ausreichender Stichprobe. Hysterese für Rückkehr nach NORMAL ist definiert. Manuelle Prüfung ist für Rückkehr erforderlich. `PERMANENT_SUSPENDED` hat keine automatische Rückkehr. Audit-Felder enthalten mindestens: `old_state`, `new_state`, `trigger`, `metric_name`, `metric_value`, `window_size`, `sample_size`, `timestamp`, `authority`. |
| Z-05 | Policy-Veto-Review-Parameter | `policy_veto_review_interval_cycles` ist konfigurierbar. Standardwert ist 20. Wertebereich ist 1 bis 500. 0 ist ungültig. Review-Zähler ist persistent. Neustart setzt den Zähler nicht zurück. SAFE_MODE kann die Zählung pausieren, setzt sie aber nicht zurück. Review erzeugt Audit-Event `policy_veto_review`. Audit-Event enthält mindestens: `event_type`, `zyklus_id`, `policy_veto_id`, `review_decision`, `review_reason`, `review_timestamp`, `review_authority`, `escalation_target`. |
| Z-06 | QuestorSpec-Default-Instanz | Ein `ResearchPackage` ohne `questor_spec` wird verarbeitet. Default-Instanz wird angewendet. Defaults sind sicher. `autonomy_level = STRICT`. LLM bleibt Advisor. Keine physische Ausführung bei Unklarheit. `allowed_capabilities` und `allowed_loop_templates` sind leer. Leere Listen bedeuten: keine Capability und kein Template sind standardmäßig freigeschaltet. Physische Ausführung ist ohne explizite Freigabe nicht erlaubt. |
| Z-07 | HAL-Minimalvertrag | HAL bietet mindestens: `get_environment_manifest()`, `get_slot_state()`, `get_zone_state()`, `execute_command()`, `start_process()`, `monitor_process()`, `hold_process()`, `resume_process()`, `abort_process()`, `release_stage()`, `report_estop()`, `report_hardware_interlock()`, `get_estop_state()`, `reconcile_slot_state()`, `reconcile_process_state()`, `get_command_status()`. HAL vergibt keine Leases. HAL interpretiert keine wissenschaftlichen Ziele. HAL prüft `lease_ref` formal oder fragt Resource Governor. Fehler sind klassifiziert als `OPERATIONAL` oder `SAFETY`. ESTOP-Zustände sind: `NORMAL`, `ACTIVE`, `LATCHED`, `TEST`. ESTOP stoppt aktive Kommandos. ESTOP suspendiert betroffene Leases. Questor darf ESTOP nicht zurücksetzen. HAL protokolliert operational. Dummy-HAL kann alle relevanten Fehlermodi simulieren. |
| Z-08 | N-01-Scanbereich und Allowlist | N-01 sucht in produktiven Quellen. Migrations-/Archiv-/Testdokumente sind ausgenommen. Allowlist-Dateien sind zulässig, wenn explizit gekennzeichnet. Allowlist enthält mindestens: `path`, `pattern`, `reason`, `approved_until`, `owner`, `review_required`. Allowlists dürfen keine produktiven Laufzeitquellen freischalten. Allowlists sollten zeitlich begrenzt und review-pflichtig sein. |

### §3.6 Suite H — HAL v0.2.0 (24 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| H-01 | EnvironmentManifest ist vollständig | Manifest enthält Slots, Zonen, Capabilities, Timeout-Grenzen, ESTOP-Mechanismus, Resource-Classes, `supported_security_modes`. |
| H-02 | Kommando ohne Lease wird abgelehnt | `status: DENIED`. `error_code: LEASE_INVALID`. `error_class: OPERATIONAL`. Keine Ausführung. |
| H-03 | Ungültige Lease wird abgelehnt | `status: DENIED`. `error_code: LEASE_INVALID`. Keine Ausführung. |
| H-04 | Abgelaufene Lease wird abgelehnt | `status: DENIED`. `error_code: LEASE_EXPIRED`. Keine Ausführung. |
| H-05 | Slot-Mutex verhindert parallele Ausführung | Zweites Kommando erhält `SLOT_BUSY` oder `DENIED`. Kein paralleler physischer Zugriff. |
| H-06 | Zonen-Mutex verhindert parallele Zonen-Nutzung | Zweites Kommando erhält `ZONE_LOCK_UNAVAILABLE`. Kein paralleler Zugriff auf gemeinsame Schiene. |
| H-07 | ESTOP blockiert neue Kommandos | `status: ESTOP`. Keine neue Ausführung. `error_class: SAFETY`. |
| H-08 | Hardware-Interlock blockiert neue Kommandos | `status: INTERLOCK`. Keine neue Ausführung. `error_class: SAFETY`. `interlock_latched: true`. `physical_reset_required: true`. |
| H-09 | ESTOP suspendiert betroffene Leases | Resource Governor wird informiert. Betroffene Leases werden als suspendiert betrachtet. Questor erhält Sicherheitsabbruch. |
| H-10 | Hardware-Interlock suspendiert betroffene Leases und Zonen | Resource Governor wird informiert. Betroffene Leases werden als suspendiert betrachtet. Betroffene Zonen werden als `INTERLOCKED` betrachtet. Questor erhält Sicherheitsabbruch. |
| H-11 | Timeout führt zu operationalem Fehler | `status: TIMEOUT`. `error_code: COMMAND_TIMEOUT`. `error_class: OPERATIONAL`. Kein ESTOP. |
| H-12 | Timeout bei physischem Slot kann Reconciliation auslösen | Slot kann auf `ERROR` gehen. `reconcile_slot_state` erforderlich. Kein blinder Retry. |
| H-13 | Duplicate Command wird blockiert | `status: DUPLICATE_BLOCKED`. Keine erneute Ausführung. Keine doppelten Seiteneffekte. |
| H-14 | Crash-Recovery ohne blinden Retry | Nach unklarem Crash wird nicht automatisch neu ausgeführt. `RECOVERY_UNSAFE` möglich. Slot bleibt kontrolliert gesperrt bis Klärung. |
| H-15 | HAL schreibt nur operational Logs | Logs landen in `data/operational_logs/`. Keine Atlas-Einträge. Keine Archiv-Einträge. Keine Blackbox-Einträge. |
| H-16 | Physische Ausführung nur bei passendem Security-Mode | `SANDBOX` oder `DEV_SANDBOX_ONLY` führt nicht physisch aus. `NORMAL` darf physisch ausführen, wenn Lease und Slot es erlauben. Verstöße führen zu `PHYSICAL_EXECUTION_FORBIDDEN`. |
| H-17 | Compute-Ausführung nur bei passendem Security-Mode | `SANDBOX` oder `DEV_SANDBOX_ONLY` führt nicht echt aus. `NORMAL` darf Compute ausführen, wenn Lease und Slot es erlauben. Verstöße führen zu `COMPUTE_EXECUTION_FORBIDDEN`. |
| H-18 | Langzeit-Prozess mit SAFE_HOLD | Prozess wird gestartet. Prozess läuft für erwartete Dauer. Bei Lease-Expiry: Prozess geht in `SAFE_HOLD`. Prozess wird nicht zerstört. `resume_token` wird erzeugt. |
| H-19 | Langzeit-Prozess mit RESUME | Prozess wird gestartet. Prozess geht in `SAFE_HOLD`. `resume_process` mit gültigem `resume_token` wird aufgerufen. Prozess wird fortgesetzt. `process_state` geht von `SAFE_HOLD` nach `RUNNING`. |
| H-20 | Langzeit-Prozess mit WAITING_FOR_RELEASE | Prozess wird gestartet. Erste Stufe wird abgeschlossen. Prozess geht in `WAITING_FOR_RELEASE`. `release_stage` wird aufgerufen. Prozess wird fortgesetzt. `process_state` geht von `WAITING_FOR_RELEASE` nach `RUNNING`. |
| H-21 | Langzeit-Prozess mit Stage-Release-Denied | Prozess wird gestartet. Erste Stufe wird abgeschlossen. Prozess geht in `WAITING_FOR_RELEASE`. `release_stage` wird ohne Berechtigung aufgerufen. `STAGE_RELEASE_DENIED` wird zurückgegeben. Prozess bleibt in `WAITING_FOR_RELEASE`. |
| H-22 | CUDA-OOM ist operational | `status: ERROR`. `error_code: CUDA_OOM`. `error_class: OPERATIONAL`. Kein ESTOP. Keine Sicherheitsprüfung. |
| H-23 | Parameter-Schema-Validierung | Kommando mit gültigem Schema wird akzeptiert. Kommando mit unbekanntem Schema wird abgelehnt. Kommando mit falscher Checksumme wird abgelehnt. Fehlercode: `PARAMETER_SCHEMA_UNKNOWN` oder `PARAMETER_CHECKSUM_MISMATCH`. Fehlerklasse: `OPERATIONAL`. |
| H-24 | Dummy-HAL kann alle Fehlermodi simulieren | Alle definierten Fehlermodi sind testbar. Simulation ist deterministisch. Keine echte Hardware beteiligt. |

---

## §4 Neue Questor-Test-Suiten

### §4.1 Suite Q-U — Questor Unit-Tests (~252 Tests)

#### §4.1.1 `sanitization.py` (18 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| U-SAN-01 | Feld-Whitelist: Nur erlaubte Felder passieren | Nicht-erlaubte Felder werden entfernt |
| U-SAN-02 | Feld-Blocklist: `atlas_version_ref`, `gate_record_ref` werden blockiert | Blockierte Felder sind nicht im Output |
| U-SAN-03 | Injection-Pattern INJ-01: "ignore all previous instructions" | `injection_detected = true`, Feld wird quarantänen |
| U-SAN-04 | Injection-Pattern INJ-04: "ESTOP" im Freitext | `injection_detected = true`, Feld wird quarantänen |
| U-SAN-05 | Injection-Pattern INJ-05: "setze ESTOP zurück" | `injection_detected = true`, Feld wird quarantänen |
| U-SAN-06 | Control-Characters werden entfernt | Output enthält keine Control-Chars |
| U-SAN-07 | Zero-Width-Chars werden entfernt | Output enthält keine Zero-Width-Chars |
| U-SAN-08 | Text über `max_length` wird abgeschnitten | Text ist auf `max_length` begrenzt |
| U-SAN-09 | `parameter_bounds` mit NaN wird verworfen | Feld wird verworfen, Warning |
| U-SAN-10 | `parameter_bounds` mit Infinity wird verworfen | Feld wird verworfen, Warning |
| U-SAN-11 | LLM-Output ist kein JSON → PARSE_ERROR | `status = PARSE_ERROR`, Fallback |
| U-SAN-12 | LLM-Output enthält Safety-Keyword → SAFETY_REJECT | `status = SAFETY_REJECT`, Fallback |
| U-SAN-13 | LLM-Output verletzt parameter_bounds → INVALID | `status = INVALID`, Fallback |
| U-SAN-14 | LLM-Output außerhalb allowed_capabilities → INVALID | `status = INVALID`, Fallback |
| U-SAN-15 | LLM-Timeout → Fallback | Deterministischer Fallback wird verwendet |
| U-SAN-16 | `sanitize_for_llm` gibt `SanitizationResult` zurück | Struktur ist korrekt |
| U-SAN-17 | Leerer Kontext → kein Fehler | Leerer Kontext wird akzeptiert |
| U-SAN-18 | XML-Tag-Escaping: `<konzept>` im Freitext wird escaped | `<` → `&lt;`, `>` → `&gt;` |

#### §4.1.2 `capability_registry.py` (22 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| U-CAP-01 | Registry laden: gültige YAML-Dateien | Registry wird geladen, `capability_count` korrekt |
| U-CAP-02 | Registry laden: ungültige YAML-Datei | Questor startet nicht, Fehler wird protokolliert |
| U-CAP-03 | Registry laden: doppelte `capability_id` | Questor startet nicht, Fehler wird protokolliert |
| U-CAP-04 | `check_capability`: Capability in Registry, HAL, Package | `status = AVAILABLE` |
| U-CAP-05 | `check_capability`: Capability nicht in Registry | `status = UNKNOWN` |
| U-CAP-06 | `check_capability`: Capability deprecated | `status = DEPRECATED` |
| U-CAP-07 | `check_capability`: Capability nicht in HAL-Manifest | `status = UNAVAILABLE` |
| U-CAP-08 | `check_capability`: Capability nicht in allowed_capabilities | `status = SECURITY_RESTRICTED` |
| U-CAP-09 | `check_capability`: Security-Mode passt nicht | `status = SECURITY_RESTRICTED` |
| U-CAP-10 | `validate_parameters`: Alle Pflichtfelder vorhanden | Keine Fehler |
| U-CAP-11 | `validate_parameters`: Pflichtfeld fehlt | `MISSING_REQUIRED_PARAMETER` |
| U-CAP-12 | `validate_parameters`: FLOAT außerhalb Bounds | `BELOW_MIN` oder `ABOVE_MAX` |
| U-CAP-13 | `validate_parameters`: STRING zu lang | `TOO_LONG` |
| U-CAP-14 | `validate_parameters`: ENUM-Wert ungültig | `INVALID_ENUM` |
| U-CAP-15 | `validate_parameters`: NaN | `NAN_PARAMETER` |
| U-CAP-16 | `validate_parameters`: Infinity | `INFINITY_PARAMETER` |
| U-CAP-17 | `get_slots_for_capability`: Ein Slot verfügbar | Liste mit einer Slot-ID |
| U-CAP-18 | `get_slots_for_capability`: Mehrere Slots verfügbar | Liste mit mehreren Slot-IDs |
| U-CAP-19 | `get_slots_for_capability`: Kein Slot verfügbar | Leere Liste |
| U-CAP-20 | `capabilities_available`: Alle Capabilities verfügbar | True |
| U-CAP-21 | `capabilities_available`: Eine Capability fehlt | False |
| U-CAP-22 | Integritäts-Hash der Registry | Hash ist deterministisch und reproduzierbar |

#### §4.1.3 `security_mode.py` (11 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| U-SM-01 | `get_effective_security_mode`: Paket NORMAL, Gate NORMAL, System NORMAL | NORMAL |
| U-SM-02 | `get_effective_security_mode`: Paket NORMAL, Gate SANDBOX | SANDBOX (restriktiver) |
| U-SM-03 | `get_effective_security_mode`: Paket NORMAL, System RECOVERY | RECOVERY (restriktiver) |
| U-SM-04 | `validate_package_security_mode`: Paket-Modus nicht in Gate | PackageInvalidError |
| U-SM-05 | `validate_package_security_mode`: Paket-Modus in Gate | True |
| U-SM-06 | `filter_templates_by_security_mode`: RECOVERY | Nur `is_recovery_template = true` |
| U-SM-07 | `filter_templates_by_security_mode`: SANDBOX | Nur Templates mit `allowed_security_modes ⊇ {SANDBOX}` |
| U-SM-08 | `policy_check_security_mode`: Physische Actuation in SANDBOX | VETO |
| U-SM-09 | `policy_check_security_mode`: Physische Actuation in NORMAL | GO |
| U-SM-10 | `policy_check_security_mode`: RECOVERY mit nicht-Recovery-Capability | VETO |
| U-SM-11 | `security_mode` fehlt im Paket | PACKAGE_INVALID |

#### §4.1.4 `shutdown.py` (13 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| U-SD-01 | SIGTERM empfangen | `shutdown_requested = true`, Timer startet |
| U-SD-02 | Graceful-Shutdown in IDLE | Sofort beenden, `ShutdownResult.status = COMPLETED` |
| U-SD-03 | Graceful-Shutdown in EXECUTING | HAL-Kommando abwarten, Ergebnis bauen |
| U-SD-04 | Graceful-Shutdown in FINALIZING | Ergebnis fertigstellen, dann beenden |
| U-SD-05 | Graceful-Shutdown-Timeout erreicht | Force-Shutdown |
| U-SD-06 | WAL-Flush bei Shutdown | WAL wird flush'd |
| U-SD-07 | WAL-Flush fehlschlägt | Force-Shutdown |
| U-SD-08 | Ergebnis bei Shutdown bauen | `abbruch_grund = GRACEFUL_SHUTDOWN`, `abbruch_klasse = OPERATIONAL` |
| U-SD-09 | Langzeit-Prozess bei Shutdown | SAFE_HOLD anfragen |
| U-SD-10 | SAFE_HOLD fehlschlägt bei Shutdown | Prozess abbrechen |
| U-SD-11 | Leases bei Shutdown freigeben | Leases werden freigegeben |
| U-SD-12 | Blackbox bei Shutdown schreiben | Blackbox wird geschrieben |
| U-SD-13 | ESTOP hat Vorrang vor Shutdown | `abbruch_grund = ESTOP_RECEIVED`, nicht `GRACEFUL_SHUTDOWN` |

#### §4.1.5 `health_monitor.py` (15 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| U-HM-01 | Heartbeat schreiben | `health.json` wird geschrieben |
| U-HM-02 | Heartbeat atomar schreiben (temp + rename) | Keine korrupte Datei |
| U-HM-03 | Heartbeat bei Disk-Full | Fehler protokolliert, Questor arbeitet weiter |
| U-HM-04 | Watchdog: Zustandsdauer überschritten | `watchdog_status = CRITICAL` |
| U-HM-05 | Watchdog: Speicherverbrauch zu hoch | `watchdog_status = WARNING` |
| U-HM-06 | Watchdog: CPU-Auslastung zu hoch | `watchdog_status = WARNING` |
| U-HM-07 | Watchdog: Kein Fortschritt | `watchdog_status = CRITICAL` |
| U-HM-08 | Watchdog: EXECUTING hat kein Zeitlimit | Kein Alarm bei langer EXECUTING-Dauer |
| U-HM-09 | Watchdog: WAITING_FOR_RELEASE hat kein Zeitlimit | Kein Alarm bei langer Wartezeit |
| U-HM-10 | `determine_health_status`: Alle Checks OK | HEALTHY |
| U-HM-11 | `determine_health_status`: Heartbeat veraltet | UNHEALTHY |
| U-HM-12 | `determine_health_status`: Prozess läuft nicht | DEAD |
| U-HM-13 | Externer Monitor: `health.json` lesen | `HealthCheckResult` korrekt |
| U-HM-14 | Externer Monitor: `health.json` fehlt | `overall_status = DEAD` |
| U-HM-15 | Alert-Cooldown | Kein zweiter Alert innerhalb von `alert_cooldown_s` |

#### §4.1.6 `trail_map.py` (11 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| U-TRAIL-01 | Trail erstellen mit `create_trails = true` | Trail wird erstellt |
| U-TRAIL-02 | Trail erstellen mit `create_trails = false` | Trail wird NICHT erstellt |
| U-TRAIL-03 | Trail mit `require_evidence = true` und Evidenz vorhanden | Trail wird erstellt |
| U-TRAIL-04 | Trail mit `require_evidence = true` und keine Evidenz | Trail wird erstellt mit `EVIDENCE_MISSING` |
| U-TRAIL-05 | Trail-Map finalisieren | `access_level = READ_ONLY`, `integrity_hash` berechnet |
| U-TRAIL-06 | TrailMapSummary erstellen | `trail_count`, `decision_type_counts` korrekt |
| U-TRAIL-07 | Trail-Append-Only: Trail nach Finalisierung hinzufügen | Fehler, Trail wird nicht hinzugefügt |
| U-TRAIL-08 | Trail-Map in Blackbox speichern | Datei wird geschrieben |
| U-TRAIL-09 | Trail-Map-Hash mit Ledger-Hash vergleichen | Hashes stimmen überein |
| U-TRAIL-10 | Trail mit `trail_detail_level = MINIMAL` | Nur `decision_type`, `chosen_alternative_id`, `reasoning` |
| U-TRAIL-11 | Trail mit `trail_detail_level = FULL` | Alle Felder vorhanden |

#### §4.1.7 `queue_integration.py` (14 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| U-QI-01 | Dispatcher schreibt Envelope in `pending/` | Datei wird erstellt, Registry aktualisiert |
| U-QI-02 | Dispatcher schreibt dupliziertes Envelope | Duplikat wird abgelehnt |
| U-QI-03 | Dispatcher schreibt ohne `gate_record_ref` | Fehler, Envelope wird nicht geschrieben |
| U-QI-04 | Questor liest ältestes Paket aus `pending/` | Ältestes Paket wird genommen |
| U-QI-05 | Questor verschiebt Envelope nach `processing/` | Datei wird verschoben, Registry aktualisiert |
| U-QI-06 | Questor schreibt Result nach `completed/` | Datei wird erstellt, Registry aktualisiert |
| U-QI-07 | Questor schreibt Result nach `failed/` | Datei wird erstellt, Registry aktualisiert |
| U-QI-08 | Receiver liest Result aus `completed/` | `QuestorErgebnisPaket` wird gelesen |
| U-QI-09 | Receiver validiert `vollstaendig_flag` | `false` → Ergebnis wird nicht verarbeitet |
| U-QI-10 | Delete-Request für Paket in `pending/` | Paket wird gelöscht |
| U-QI-11 | Delete-Request für Paket in `processing/` | Paket wird NICHT gelöscht |
| U-QI-12 | Registry-Lock: Zwei Prozesse schreiben gleichzeitig | Kein Race Condition |
| U-QI-13 | Envelope-Datei ist korrupt | `QUEUE_FILE_CORRUPT`, Datei wird quarantänen |
| U-QI-14 | `registry.json` ist korrupt | Registry wird aus Dateien rekonstruiert |

#### §4.1.8 Weitere Module (~148 Tests)

| Modul | Test-Anzahl | Schwerpunkte |
| :--- | :--- | :--- |
| `objective_parser.py` | 10 | Keyword-Matching, Clarity-Score |
| `compass.py` | 20 | Loop Selection, Ranking, Candidate-Window |
| `policy_evaluator.py` | 15 | Alle 8 Prüfungen, VETO/GO |
| `loop_registry.py` | 10 | Template laden, validieren, filtern |
| `ledger.py` | 15 | Hash-Chain, Genesis-Hash, NaN/Infinity |
| `safety_monitor.py` | 10 | ESTOP, Interlock, Timeout |
| `recovery.py` | 12 | WAL lesen, Checkpoint finden, Reconcile |
| `sequence.py` | 8 | Atomare Persistierung, Datei-Lock |
| `hal_bridge.py` | 20 | Übersetzung, Ergebnisverarbeitung, Idempotenz |
| `result_builder.py` | 20 | Feldzuordnung, Kristallkandidaten, Signale |
| `blackbox_archiver.py` | 8 | Retention-Class, Limits, Rotation |

**Gesamt Unit-Tests: ~252**

### §4.2 Suite Q-C — Questor Komponententests (~44 Tests)

#### §4.2.1 QuestCompass (15 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| C-QC-01 | Objective Analysis: `objective_type` explizit gesetzt | Stufe 1 wird verwendet, kein LLM |
| C-QC-02 | Objective Analysis: Keyword-Matching | Stufe 2 wird verwendet |
| C-QC-03 | Objective Analysis: LLM-Clarification | Stufe 2.5 wird verwendet |
| C-QC-04 | Objective Analysis: LLM-Ausfall | Fail-Closed, `ABORT_IF_UNCLEAR` |
| C-QC-05 | Loop Selection: Ein Template verfügbar | Direkt wählen, kein LLM |
| C-QC-06 | Loop Selection: Mehrere Templates, STRICT | Top-1 wählen, kein LLM |
| C-QC-07 | Loop Selection: Mehrere Templates, GUIDED | Top-3, LLM bei Score-Diff < 0.15 |
| C-QC-08 | Loop Selection: FRACTURE_DIAGNOSIS | STRICT erzwingen, nur DIAGNOSE-Templates |
| C-QC-09 | Evaluation: OPTIMIZE, Konfidenz ≥ Threshold | ZIEL ERREICHT |
| C-QC-10 | Evaluation: OPTIMIZE, Konfidenz < Threshold | RE-PLANUNG |
| C-QC-11 | Decision Engine: ESTOP aktiv | SOFORT ABBRUCH (SAFETY) |
| C-QC-12 | Decision Engine: Budget erschöpft | ABBRUCH (BUDGET_EXHAUSTED) |
| C-QC-13 | Decision Engine: Ziel unerreichbar | ABBRUCH (TARGET_NOT_REACHABLE, SCIENTIFIC) |
| C-QC-14 | Gesamter Zyklus: PLAN → EXECUTE → EVALUATE → RE-PLAN | Korrekte Zustandsübergänge |
| C-QC-15 | LLM-Advice wird abgelehnt | Deterministische Entscheidung gewinnt |

#### §4.2.2 PolicyEvaluator (9 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| C-PE-01 | Alle Prüfungen bestanden | GO |
| C-PE-02 | ESTOP aktiv | VETO (SAFETY_ACTIVE) |
| C-PE-03 | Außerhalb Routing-Graph | VETO (OUTSIDE_ROUTING_GRAPH) |
| C-PE-04 | Capability nicht verfügbar | VETO (CAPABILITY_UNAVAILABLE) |
| C-PE-05 | Budget überschritten | VETO (BUDGET_EXCEEDED) |
| C-PE-06 | Security-Mode passt nicht | VETO (SECURITY_MODE_MISMATCH) |
| C-PE-07 | Einfachere Alternative existiert | VETO (SIMPLER_ALTERNATIVE_EXISTS) |
| C-PE-08 | Dimension-Approval fehlt | VETO (DIMENSION_APPROVAL_MISSING) |
| C-PE-09 | Kombination: ESTOP + Budget überschritten | VETO (SAFETY_ACTIVE hat Vorrang) |

#### §4.2.3 HAL-Bridge (10 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| C-HB-01 | LoopStep → HALCommand übersetzen | Korrekte Felder |
| C-HB-02 | LoopStep → ProcessCommand übersetzen | Korrekte Felder |
| C-HB-03 | HALCommandResult SUCCESS → Weiter im Loop | `BridgeResult.status = SUCCESS` |
| C-HB-04 | HALCommandResult ESTOP → SAFETY_ABORT | `BridgeResult.status = SAFETY_ABORT` |
| C-HB-05 | HALCommandResult LEASE_DENIED → OPERATIONAL_ABORT | `BridgeResult.status = OPERATIONAL_ABORT` |
| C-HB-06 | HALCommandResult DUPLICATE_BLOCKED → SUCCESS | `BridgeResult.status = SUCCESS` |
| C-HB-07 | Parameter-Validierung vor Senden | Ungültige Parameter → nicht senden |
| C-HB-08 | Idempotenz-Key erzeugen | `command_id:lease_ref:slot_id` |
| C-HB-09 | Kosten aktualisieren nach Ausführung | `accumulated_cost` korrekt |
| C-HB-10 | Prozess in SAFE_HOLD versetzen | `ProcessResult.process_state = SAFE_HOLD` |

#### §4.2.4 Result-Builder (10 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| C-RB-01 | Ergebnis bei Erfolg bauen | `status = erfolgreich`, `abbruch_klasse = OPERATIONAL` |
| C-RB-02 | Ergebnis bei OPERATIONAL-Abbruch bauen | `status = abgebrochen`, `abbruch_klasse = OPERATIONAL` |
| C-RB-03 | Ergebnis bei SCIENTIFIC-Abbruch bauen | `status = fehlgeschlagen`, `abbruch_klasse = SCIENTIFIC` |
| C-RB-04 | Ergebnis bei SAFETY-Abbruch bauen | `kristall_kandidaten = []`, `signale_fuer_atlas = []` |
| C-RB-05 | Early-Abort-Ergebnis bauen | `vollstaendig_flag = true`, alle Pflichtfelder gesetzt |
| C-RB-06 | Kristallkandidaten aus Evaluation erzeugen | Korrekte `konfidenz`, `loop_template`, `loop_parameter` |
| C-RB-07 | Signale aus Kristallkandidaten erzeugen | Korrekte `signal_typ`, `zone_ref` |
| C-RB-08 | Guardian-Validierung: Hash-Chain prüfen | `guardian_status = PASS` |
| C-RB-09 | Guardian-Validierung: NaN in ergebnis_daten | `guardian_status = FAIL` |
| C-RB-10 | Blackbox schreiben | `retention_class` korrekt |

**Gesamt Komponententests: ~44**

### §4.3 Suite Q-S — Questor Sicherheits-Tests (~30 Tests)

#### §4.3.1 Prompt-Injection (10 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| SEC-PI-01 | Injection über `ziel` | Feld wird quarantänen, LLM-Aufruf ohne `ziel` |
| SEC-PI-02 | Injection über `kontext.zusammenfassung` | Feld wird quarantänen |
| SEC-PI-03 | Injection über `planning_hints.hinweis_text` | Feld wird quarantänen |
| SEC-PI-04 | Injection auf Deutsch | Deutsche Patterns werden erkannt |
| SEC-PI-05 | Injection auf Englisch | Englische Patterns werden erkannt |
| SEC-PI-06 | Injection mit Unicode-Escapes | Unicode-Escapes werden erkannt |
| SEC-PI-07 | Injection mit Base64-encoding | Base64-Pattern wird erkannt |
| SEC-PI-08 | Injection im LLM-Output | SAFETY_REJECT, Fallback |
| SEC-PI-09 | Mehrere Injections in einem Feld | Alle werden erkannt, Feld wird quarantänen |
| SEC-PI-10 | Injection in `parameter_bounds` Key | Key wird verworfen |

#### §4.3.2 Capability-Bypass (5 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| SEC-CB-01 | Template fordert nicht registrierte Capability | VETO (CAPABILITY_UNAVAILABLE) |
| SEC-CB-02 | Template fordert Capability außerhalb allowed_capabilities | VETO (SECURITY_RESTRICTED) |
| SEC-CB-03 | LLM schlägt Capability außerhalb allowed_capabilities vor | Vorschlag wird verworfen |
| SEC-CB-04 | Capability mit `requires_physical_actuation = true` in SANDBOX | VETO |
| SEC-CB-05 | Capability mit `requires_dimension_approval = true` ohne Approval | VETO |

#### §4.3.3 Security-Mode-Eskalation (5 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| SEC-SM-01 | Paket fordert NORMAL, Gate erlaubt nur SANDBOX | PACKAGE_INVALID |
| SEC-SM-02 | Paket fordert NORMAL, Slot ist nur sandbox_capable | PHYSICAL_EXECUTION_FORBIDDEN |
| SEC-SM-03 | LLM versucht, security_mode zu ändern | LLM-Output wird verworfen |
| SEC-SM-04 | Security-Mode wird während Ausführung geändert | Nicht möglich (Read-Only im Kontext) |
| SEC-SM-05 | RECOVERY-Modus mit physischer Capability | VETO |

#### §4.3.4 WAL-Manipulation (3 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| SEC-WAL-01 | WAL-Datei wird extern verändert | Hash-Chain-Prüfung schlägt fehl, RECOVERY_UNSAFE |
| SEC-WAL-02 | WAL-Datei wird gelöscht | RECOVERY_UNSAFE |
| SEC-WAL-03 | WAL-Eintrag wird nachträglich geändert | Hash-Chain-Prüfung schlägt fehl |

#### §4.3.5 Queue-Manipulation (5 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| SEC-QM-01 | Envelope-Datei wird extern verändert | Validierung schlägt fehl, PACKAGE_INVALID |
| SEC-QM-02 | Result-Datei wird extern verändert | Receiver-Validierung schlägt fehl |
| SEC-QM-03 | Registry.json wird extern verändert | Registry wird aus Dateien rekonstruiert |
| SEC-QM-04 | Delete-Request-Datei wird extern verändert | Questor prüft Integrität, ungültiger Request wird ignoriert |
| SEC-QM-05 | Zwei Prozesse schreiben gleichzeitig in registry.json ohne Lock | Lock verhindert Race Condition |

#### §4.3.6 LLM-Output-Manipulation (2 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| SEC-LLM-01 | LLM-Output enthält versteckte JSON-Instruktionen | Schema-Validierung lehnt unbekannte Felder ab |
| SEC-LLM-02 | LLM-Output enthält Unicode-Escapes die bei Dekodierung Injektionen ergeben | Sanitization erkennt und blockiert |

**Gesamt Sicherheitstests: ~30**

### §4.4 Suite Q-P — Questor Performance-Tests (~10 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| PERF-01 | Paket-Validierung (Envelope) | < 100ms |
| PERF-02 | Objective Analysis (deterministisch) | < 50ms |
| PERF-03 | Loop Selection (5 Templates) | < 200ms |
| PERF-04 | PolicyEvaluator (alle 8 Prüfungen) | < 100ms |
| PERF-05 | HALCommand-Übersetzung | < 50ms |
| PERF-06 | Result-Builder (Ergebnis bauen) | < 200ms |
| PERF-07 | WAL-Schreiben (100 Einträge) | < 500ms |
| PERF-08 | Ledger-Hash-Chain (100 Einträge) | < 500ms |
| PERF-09 | Trail-Map erstellen (50 Trails) | < 200ms |
| PERF-10 | Heartbeat schreiben | < 50ms |

### §4.5 Suite Q-T — Questor Stress-Tests (~11 Tests)

| Test-ID | Test | Erwartet |
| :--- | :--- | :--- |
| STRESS-01 | Queue mit 100 Paketen in `pending/` | Questor verarbeitet sequentiell, ältestes zuerst |
| STRESS-02 | WAL mit 10.000 Einträgen | Recovery funktioniert, Hash-Chain prüft |
| STRESS-03 | Ledger mit 5.000 Einträgen | Ergebnis wird korrekt gebaut |
| STRESS-04 | Disk zu 95% voll | Heartbeat wird geschrieben, Warning |
| STRESS-05 | Disk zu 100% voll | Fehler wird protokolliert, Questor arbeitet weiter (soweit möglich) |
| STRESS-06 | 10 LLM-Aufrufe gleichzeitig (max_calls = 3) | Nur 3 werden ausgeführt, Rest wird abgelehnt |
| STRESS-07 | Template-Registry mit 500 Templates | Laden < 5 Sekunden |
| STRESS-08 | Capability-Registry mit 200 Capabilities | Laden < 2 Sekunden |
| LOAD-01 | 10 Pakete in 24 Stunden | Alle werden verarbeitet |
| LOAD-02 | 1 Paket mit 100 Iterationen | Budget wird korrekt getrackt |
| LOAD-03 | 1 Langzeit-Prozess (72h) | SAFE_HOLD und RESUME funktionieren |

**Gesamt Performance/Stress-Tests: ~21**

---

## §5 Testdaten und Fixtures

### §5.1 Test-Fixture-Struktur

```
tests/
  └── test_questor/
      ├── fixtures/
      │   ├── envelopes/
      │   │   ├── valid_envelope.json
      │   │   ├── invalid_envelope_no_gate.json
      │   │   ├── invalid_envelope_no_lease.json
      │   │   └── envelope_with_injection.json
      │   ├── templates/
      │   │   ├── chemie_optimize_v1.yaml
      │   │   ├── biologie_incubation_v1.yaml
      │   │   ├── ml_training_v1.yaml
      │   │   └── recovery_reconcile_v1.yaml
      │   ├── capabilities/
      │   │   ├── pipette.transfer.yaml
      │   │   ├── spectrometer.measure_absorbance.yaml
      │   │   └── gpu.train.yaml
      │   ├── hal_manifests/
      │   │   ├── normal_manifest.json
      │   │   ├── sandbox_manifest.json
      │   │   └── recovery_manifest.json
      │   ├── wal/
      │   │   ├── valid_wal/
      │   │   ├── corrupt_wal/
      │   │   └── empty_wal/
      │   └── results/
      │       ├── successful_result.json
      │       ├── operational_abort_result.json
      │       ├── scientific_abort_result.json
      │       └── safety_abort_result.json
      ├── mocks/
      │   ├── mock_hal.py
      │   ├── mock_llm.py
      │   ├── mock_resource_governor.py
      │   └── mock_filesystem.py
      └── conftest.py
```

### §5.2 Mock-Strategie

| Mock | Zweck |
| :--- | :--- |
| `mock_hal.py` | Simuliert HAL-Antworten (SUCCESS, DENIED, ESTOP, etc.) |
| `mock_llm.py` | Simuliert LLM-Antworten (JSON, Timeout, Injection) |
| `mock_resource_governor.py` | Simuliert Lease-Vergabe und -Ablehnung |
| `mock_filesystem.py` | Simuliert Disk-Full, Permission-Error, etc. |

### §5.3 Testdaten-Regeln

| Regel | Beschreibung |
| :--- | :--- |
| TD-1 | Testdaten sind deterministisch. Keine Zufälligkeit. |
| TD-2 | Testdaten enthalten keine echten Forschungsdaten. |
| TD-3 | Testdaten enthalten keine echten Gate-Records. |
| TD-4 | Testdaten enthalten keine echten Lease-Tokens. |
| TD-5 | Testdaten sind in `tests/test_questor/fixtures/` gespeichert. |
| TD-6 | Testdaten sind versioniert (git). |

---

## §6 Coverage-Ziele

### §6.1 Mindestabdeckung pro Modul

| Modul | Mindestabdeckung | Begründung |
| :--- | :--- | :--- |
| `sanitization.py` | 95% | Sicherheitskritisch |
| `capability_registry.py` | 90% | Sicherheitskritisch |
| `security_mode.py` | 95% | Sicherheitskritisch |
| `policy_evaluator.py` | 95% | Sicherheitskritisch |
| `safety_monitor.py` | 95% | Sicherheitskritisch |
| `shutdown.py` | 90% | Crash-Sicherheit |
| `health_monitor.py` | 85% | Betriebssicherheit |
| `hal_bridge.py` | 90% | Hardware-Zugriff |
| `result_builder.py` | 90% | Ergebnis-Integrität |
| `ledger.py` | 90% | Datenintegrität |
| `recovery.py` | 90% | Crash-Recovery |
| `compass.py` | 85% | Kernlogik |
| `trail_map.py` | 80% | Operational |
| `queue_integration.py` | 85% | Betriebskritisch |
| `facade.py` | 85% | Eintrittspunkt |
| `validator.py` | 90% | Eintrittspunkt |
| **Gesamt** | **≥ 88%** | |

### §6.2 Coverage-Regeln

| Regel | Beschreibung |
| :--- | :--- |
| COV-1 | Sicherheitskritische Module haben ≥ 95% Abdeckung. |
| COV-2 | Kernlogik hat ≥ 85% Abdeckung. |
| COV-3 | Jeder Fail-Closed-Punkt muss getestet sein. |
| COV-4 | Jeder Edge Case muss getestet sein. |
| COV-5 | Jede Fehlerbehandlung muss getestet sein. |
| COV-6 | Jeder Zustandsübergang muss getestet sein. |

---

## §7 Test-Infrastruktur

### §7.1 Framework

| Tool | Zweck |
| :--- | :--- |
| pytest | Test-Framework |
| pytest-cov | Code-Coverage |
| pytest-asyncio | Async-Tests (falls nötig) |
| pytest-timeout | Timeout für Tests |
| pytest-mock | Mocking |
| hypothesis | Property-based Testing (optional) |

### §7.2 Test-Konfiguration

```ini
# pytest.ini
[pytest]
testpaths = tests/test_questor
addopts = --cov=src/questor --cov-report=html --cov-report=term-missing
timeout = 60
markers =
    unit: Unit-Tests
    component: Komponententests
    integration: Integrationstests
    security: Sicherheitstests
    performance: Performance-Tests
    stress: Stress-Tests
    slow: Langsame Tests (> 10s)
```

### §7.3 Continuous Integration

```yaml
# .github/workflows/questor-tests.yml
name: Questor Tests
on: [push, pull_request]
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest tests/test_questor -m unit --cov=src/questor
  component-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pytest tests/test_questor -m component
  security-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pytest tests/test_questor -m security
  performance-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pytest tests/test_questor -m performance --timeout=300
```

---

## §8 Test-Ausführungsstrategie

### §8.1 Ausführungsreihenfolge

```
PHASE 1: Unit-Tests (schnell, ~2 Minuten)
  → pytest -m unit

PHASE 2: Komponententests (~5 Minuten)
  → pytest -m component

PHASE 3: Sicherheitstests (~3 Minuten)
  → pytest -m security

PHASE 4: Integrationstests (Suite I, ~10 Minuten)
  → pytest -m integration

PHASE 5: Szenario-Tests (Suite S, ~15 Minuten)
  → pytest -m scenario

PHASE 6: Performance/Stress-Tests (~10 Minuten)
  → pytest -m "performance or stress" --timeout=300

PHASE 7: Vollständige Suite (~45 Minuten)
  → pytest --cov=src/questor
```

### §8.2 Test-Gates

| Gate | Bedingung |
| :--- | :--- |
| GATE-1 | Alle Unit-Tests bestehen |
| GATE-2 | Alle Komponententests bestehen |
| GATE-3 | Alle Sicherheitstests bestehen |
| GATE-4 | Coverage ≥ 88% |
| GATE-5 | Alle Integrationstests bestehen (Suite I) |
| GATE-6 | Alle Szenario-Tests bestehen (Suite S) |
| GATE-7 | Performance-Tests innerhalb der Limits |
| GATE-8 | Keine offenen Blocker |

---

## §9 Akzeptanzkriterien für das Gesamtsystem

Das Gesamtsystem gilt als integriert, wenn:

| # | Kriterium | CHARTER-Referenz |
| :--- | :--- | :--- |
| 1 | Alle Naming-Tests bestehen | — |
| 2 | Alle Integrationstests bestehen | — |
| 3 | Alle Szenario-Tests bestehen | — |
| 4 | Alle Regressions-Tests bestehen | — |
| 5 | Alle Präzisierungs-Tests bestehen | — |
| 6 | Alle HAL-Tests bestehen | — |
| 7 | Alle Questor-Unit-Tests bestehen | — |
| 8 | Alle Questor-Komponententests bestehen | — |
| 9 | Alle Questor-Sicherheitstests bestehen | — |
| 10 | Alle Questor-Performance-/Stress-Tests bestehen | — |
| 11 | Keine produktiven Altbezeichnungen vorhanden sind | — |
| 12 | Kein produktiver Adapter vorhanden ist | — |
| 13 | QuestorBlackbox isoliert bleibt | CHARTER §SR-07 |
| 14 | Operational keine wissenschaftlichen Signale erzeugt | CHARTER §SR-08 |
| 15 | ESTOP und LEASE_DENIED strikt getrennt bleiben | CHARTER §SR-09 |
| 16 | SAFE_MODE weiterhin menschliche Sicherheit garantiert | CHARTER §SR-11 |
| 17 | FRACTURE_DIAGNOSIS korrekt bleibt | — |
| 18 | Dimensions-Expansion approval-pflichtig bleibt | — |
| 19 | `idempotency_key` kanonisch ist | CONTRACTS §8.1 |
| 20 | `attempt_id` vollständig eingeschränkt ist | CONTRACTS §1.3 |
| 21 | QuestorSpec-Defaults sicher sind | CONTRACTS §1.2 |
| 22 | Circuit-Breaker-Zustände explizit sind | — |
| 23 | Policy-Veto-Review konfigurierbar ist | — |
| 24 | HAL-Minimalvertrag testbar ist | CONTRACTS §3.12 |
| 25 | HAL Langzeit-Prozesse unterstützt | CONTRACTS §3.4 |
| 26 | HAL Hardware-Interlocks unterstützt | CONTRACTS §3.11 |
| 27 | HAL Zonen-Mutex unterstützt | CONTRACTS §3.8 |
| 28 | HAL Compute-Ressourcenmodell unterstützt | CONTRACTS §3.2 |
| 29 | HAL Parameter-Schema-Registry unterstützt | CONTRACTS §3.3 |
| 30 | Naming-Allowlist explizit und review-pflichtig ist | — |

---

## §10 Sicherheitsregeln für Tests

| # | Regel | CHARTER-Referenz |
| :--- | :--- | :--- |
| S1 | Tests dürfen keine echte Hardware ansprechen. | CHARTER §SR-12 |
| S2 | Tests dürfen keine echten Leases verwenden. | CHARTER §SR-06 |
| S3 | Tests dürfen keine echten Gate-Records verwenden. | — |
| S4 | Tests dürfen keine echten Atlas-Daten verwenden. | CHARTER §SR-04 |
| S5 | Tests dürfen keine echten LLM-Aufrufe machen (nur Mocks). | CHARTER §SR-13 |
| S6 | Tests müssen deterministisch sein. | CHARTER §2 |
| S7 | Tests müssen reproduzierbar sein. | — |
| S8 | Tests dürfen keine Daten in `data/archiv/` oder `data/atlas/` schreiben. | CHARTER §SR-04 |
| S9 | Tests dürfen keine Daten in `data/questor_blackbox/` schreiben (nur in `tests/tmp/`). | CHARTER §SR-07 |
| S10 | Sicherheitstests müssen die Fail-Closed-Punkte testen. | CHARTER §SR-10 |

---

## §11 Kritische Warnungen für den Test

### §11.1 Nicht alte Kasten testen

Wenn ein Test alte Kasten wie `AnalystCaste`, `PlannerCaste`, `ExecutorCaste`, `TheoristCaste` als aktive Vertragskomponenten erwartet, ist der Test falsch.

Questor ersetzt nicht diese Kasten direkt, sondern die frühere Black Box aus v2.3.1.

### §11.2 Keine Blackbox im Archivar

Wenn ein Test erwartet, dass der Archivar QuestorBlackbox liest, ist der Test falsch.

→ Siehe CHARTER §SR-07.

### §11.3 Keine wissenschaftlichen Signale aus operationalen Fehlern

Wenn ein Test OOM, Timeout oder Lease-Konflikt als wissenschaftliches Signal interpretiert, ist der Test falsch.

→ Siehe CHARTER §SR-08.

### §11.4 Kein ESTOP bei Ressourcenkonflikt

Wenn ein Test LEASE_DENIED als ESTOP behandelt, ist der Test falsch.

→ Siehe CHARTER §SR-09.

### §11.5 Kein direkter Atlas-Zugriff durch Questor

Wenn ein Test erwartet, dass Questor direkt Signale in den Atlas schreibt, ist der Test falsch.

→ Siehe CHARTER §SR-04.

### §11.6 Keine Doppelreferenz

Wenn ein Test zwei primäre Referenzdateien ohne Konflikthierarchie annimmt, ist der Test falsch.

### §11.7 Keine HAL-Lease-Vergabe

Wenn ein Test erwartet, dass HAL Leases vergibt, ist der Test falsch.

→ Siehe CHARTER §SR-06.

### §11.8 Keine HAL-Wissenschaft

Wenn ein Test erwartet, dass HAL wissenschaftliche Ziele interpretiert oder wissenschaftliche Signale erzeugt, ist der Test falsch.

→ Siehe CHARTER §SR-08.

### §11.9 Kein CUDA-OOM als SAFETY

Wenn ein Test CUDA_OOM als SAFETY oder ESTOP interpretiert, ist der Test falsch.

→ Siehe CHARTER §SR-08.

### §11.10 Kein Hardware-Interlock als OPERATIONAL

Wenn ein Test Hardware-Interlock als OPERATIONAL interpretiert, ist der Test falsch.

→ Siehe CHARTER §SR-09.

### §11.11 Kein blinder Retry nach Crash

Wenn ein Test erwartet, dass HAL nach einem Crash automatisch neu startet, ist der Test falsch.

→ Siehe CHARTER §SR-10.

### §11.12 Keine automatische Interlock-Rücksetzung

Wenn ein Test erwartet, dass HAL einen Hardware-Interlock automatisch zurücksetzt, ist der Test falsch.

→ Siehe CHARTER §SR-05.

### §11.13 Keine Zonen-Lock-Eigenvergabe

Wenn ein Test erwartet, dass HAL Zonen-Locks eigenmächtig vergibt, ist der Test falsch.

→ Siehe CHARTER §SR-06.

### §11.14 Keine Prozess-Fortsetzung ohne Resume-Token

Wenn ein Test erwartet, dass HAL einen Prozess ohne gültigen Resume-Token fortsetzt, ist der Test falsch.

### §11.15 Keine Stage-Release ohne Berechtigung

Wenn ein Test erwartet, dass HAL eine Stage ohne Berechtigung freigibt, ist der Test falsch.

---

## §12 Protokollformat

Die Test-KI muss jeden Test wie folgt protokollieren:

```
[NAMING-TEST N-XX] [KOMPONENTE] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
[INTEGRATIONS-TEST I-XX] [SZENARIO Y] [KOMPONENTE] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
[SZENARIO-TEST S-X] [KOMPONENTE] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
[REGRESSIONS-TEST R-XX] [KOMPONENTE] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
[PRÄZISIERUNGS-TEST Z-XX] [KOMPONENTE] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
[HAL-TEST H-XX] [KOMPONENTE] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
[QUESTOR-UNIT-TEST Q-U-XXX] [MODUL] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
[QUESTOR-KOMPONENTENTEST Q-C-XX] [MODUL] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
[QUESTOR-SICHERHEITSTEST Q-S-XX] [MODUL] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
[QUESTOR-PERFORMANCETEST Q-P-XX] [MODUL] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
[QUESTOR-STRESSTEST Q-T-XX] [MODUL] [PROBLEM?] [BESTANDEN/NICHT BESTANDEN]
```

Am Ende müssen die Gesamtsummen stehen:

```
NAMING GESAMT: X/7 BESTANDEN
INTEGRATION GESAMT: X/18 BESTANDEN
SZENARIEN GESAMT: X/5 BESTANDEN
REGRESSION GESAMT: X/12 BESTANDEN
PRÄZISIERUNG GESAMT: X/8 BESTANDEN
HAL GESAMT: X/24 BESTANDEN
QUESTOR-UNIT GESAMT: X/~252 BESTANDEN
QUESTOR-KOMPONENTEN GESAMT: X/~44 BESTANDEN
QUESTOR-SICHERHEIT GESAMT: X/~30 BESTANDEN
QUESTOR-PERFORMANCE GESAMT: X/~10 BESTANDEN
QUESTOR-STRESS GESAMT: X/~11 BESTANDEN
GESAMT: X/~421 BESTANDEN
```

---

## §13 Zusammenfassender Bericht an die Test-KI

Am Ende des Testlaufs muss die Test-KI einen Bericht in dieser Struktur liefern:

```
## Testbericht — MYRMEX v2.4.0 + Questor v0.2.3 + HAL v0.2.0

### 1. Modus
- Dry-Run | Implementierung

### 2. Testgrundlage
- CHARTER.md (foundation/)
- CONTRACTS.md (foundation/)
- QUESTOR.md (specs/)
- HAL.md (specs/)
- GREMIUM.md (specs/)
- VALIDATION.md (ops/)
- optional: produktives Repository

### 3. Ergebnisse
NAMING GESAMT: X/7 BESTANDEN
INTEGRATION GESAMT: X/18 BESTANDEN
SZENARIEN GESAMT: X/5 BESTANDEN
REGRESSION GESAMT: X/12 BESTANDEN
PRÄZISIERUNG GESAMT: X/8 BESTANDEN
HAL GESAMT: X/24 BESTANDEN
QUESTOR-UNIT GESAMT: X/~252 BESTANDEN
QUESTOR-KOMPONENTEN GESAMT: X/~44 BESTANDEN
QUESTOR-SICHERHEIT GESAMT: X/~30 BESTANDEN
QUESTOR-PERFORMANCE GESAMT: X/~10 BESTANDEN
QUESTOR-STRESS GESAMT: X/~11 BESTANDEN
GESAMT: X/~421 BESTANDEN

### 4. Blocker
- [Blocker 1]
- [Blocker 2]
- oder: keine

### 5. Nicht-Blocker
- [Nicht-Blocker 1]
- oder: keine

### 6. Kritische Abweichungen
- [Abweichung]
- oder: keine

### 7. Sicherheitsrelevante Befunde
- [Befund]
- oder: keine

### 8. Gesamtbewertung
- BESTANDEN | NICHT BESTANDEN | TEILWEISE BESTANDEN

### 9. Freigabeempfehlung
- Freigabe für Phase X | keine Freigabe | nur bedingte Freigabe

### 10. Nächster Schritt
- [konkreter nächster Schritt]
```

---

## §14 Fehlerbericht bei nicht bestandenen Tests

Wenn ein Test fehlschlägt, muss die Test-KI zusätzlich melden:

```
Fehlgeschlagener Test: [ID]
Komponente: [Komponente]
Problem: [Problem]
Erwartetes Verhalten: [Erwartung]
Beobachtetes Verhalten: [Beobachtung]
Wahrscheinliche Ursache: [Ursache]
Empfohlene Korrektur: [Korrektur]
Priorität: Blocker | Hoch | Mittel | Niedrig
```

Wenn ein Test wegen fehlender Eingaben nicht prüfbar ist:

```
Nicht prüfbarer Test: [ID]
Grund: [Grund]
Empfehlung: [benötigte Unterlage oder Freigabe]
Status: BLOCKIERT | NICHT PRÜFBAR
```

Ein nicht prüfbarer Test darf nicht stillschweigend als bestanden markiert werden.

---

## §15 Dokumentenhierarchie

Dieses Dokument steht in der Schicht `ops/` und referenziert:
- `foundation/CHARTER.md` für Sicherheitsregeln (CHARTER §SR-XX)
- `foundation/CONTRACTS.md` für Datenverträge (CONTRACTS §X.X)
- `specs/QUESTOR.md` für Questor-spezifische Details
- `specs/HAL.md` für HAL-spezifische Details
- `specs/GREMIUM.md` für Gremium-spezifische Details

**Regel:** Änderungen an Test-Suiten in diesem Dokument erfordern eine Versionsänderung und eine Überprüfung der referenzierten Dokumente.