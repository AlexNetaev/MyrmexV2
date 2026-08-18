# MYRMEX v2.4.0 + Questor v0.2.3

Autonomes Wissenschaftssystem nach Ameisenstaat-Prinzip mit Questor-Integration.

## Was ist MYRMEX?

MYRMEX ist ein autonomes Wissenschaftssystem, das nach dem Prinzip eines Ameisenstaates organisiert ist. Es kombiniert kollektive Intelligenz mit strengen Sicherheitsgarantien, um wissenschaftliche Forschung zu automatisieren.

Das System besteht aus **6 Schichten**:

| Schicht | Name | Verantwortung |
|---------|------|---------------|
| 5 | 👑 Königin | Langfristige Vision, Meta-Ziele, menschliche oder LLM-basierte Führung |
| 4 | 🏛️ Gremium | Intelligenz, Atlas, Archiv, Ideen, Pakete, Sicherheit |
| 3 | ⚖️ Dispatch-Koordination | Dispatch-Vorbereitung, Lease-/Gate-Koordination |
| 2 | 🧭 Questor | Paketgebundenes Execution Subsystem |
| 1 | 🔌 HAL & Resource Governor | Slot-Routing, Leases, ESTOP, Hardwarezugriff |
| 0 | ⚙️ Physis / Compute | Hardware, Simulation, Compute |

Die **9-Stufen-Pipeline** verarbeitet wissenschaftliche Ideen von der Entstehung bis zur Ausführung:

1. Wissens-Aufnahme → 2. Atlas-Strukturierung → 3. Strategische Review → 4. Ideen-Generierung → 5a. Pre-Filter → 5b. Ideen-Erdung → 6. Paket-Bau → 7. Sicherheits-Gate → 8. Dispatch & Execution

---

## Quickstart

### Voraussetzungen

- Python 3.10+
- pip

### Installation

```bash
# Repository klonen
git clone <repository-url>
cd myrmex_v2

# Dependencies installieren
pip install -r requirements.txt
```

### Tests ausführen

```bash
python -m pytest tests/ -v
```

**Erwartetes Ergebnis:** `505 passed`

Alle 10 Phasen sind abgeschlossen und alle 12 Pflicht-Integrationstests bestehen.

---

## Repository-Struktur

```text
myrmex_v2/
├── README.md                    # Dieses Dokument
├── ARCHITECTURE.md              # Architektur-Dokumentation
├── SECURITY.md                  # Sicherheitsdokumentation
├── DEPLOYMENT.md                # Deployment-Anleitung
├── requirements.txt             # Python-Abhängigkeiten
├── pyproject.toml               # Projekt-Konfiguration
├── config.py                    # Hauptkonfiguration
├── src/                         # Quellcode
│   ├── __init__.py
│   ├── contracts/               # Datenverträge (Pydantic-Modelle)
│   │   ├── enums.py
│   │   ├── research_package.py
│   │   ├── questor_dispatch.py
│   │   ├── questor_result.py
│   │   ├── atlas_models.py
│   │   ├── pipeline_models.py
│   │   ├── lease_models.py
│   │   └── questor_metadata.py
│   ├── gremium/                 # Gremium-Komponenten (Schicht 4)
│   │   ├── __init__.py
│   │   ├── archivar.py
│   │   ├── kartograph.py
│   │   ├── kanzler.py
│   │   ├── vordenker.py
│   │   ├── pre_filter.py
│   │   ├── lotse.py
│   │   ├── quartiermeister.py
│   │   ├── sicherheitsrat/      # Sicherheitsrat
│   │   │   ├── __init__.py
│   │   │   ├── richter.py
│   │   │   ├── seher.py
│   │   │   └── circuit_breaker.py
│   │   └── pipeline_orchestrator.py
│   ├── atlas/                   # Atlas-Speicher und Signale
│   │   ├── __init__.py
│   │   ├── atlas_store.py
│   │   ├── signal_registry.py
│   │   └── clustering.py
│   ├── transaction/             # WAL, State Machine, Recovery
│   │   ├── __init__.py
│   │   ├── wal.py
│   │   ├── state_machine.py
│   │   └── recovery.py
│   ├── resource_governor/       # Resource Governor (Schicht 1)
│   │   ├── __init__.py
│   │   ├── governor.py
│   │   ├── slot_manager.py
│   │   └── estop_handler.py
│   ├── hal/                     # HAL Interface (Schicht 1)
│   │   ├── __init__.py
│   │   ├── hal_interface.py
│   │   └── dummy_hal.py
│   └── questor_interface/       # Questor-Anbindung (Schicht 2-3)
│       ├── __init__.py
│       ├── package_dispatcher.py
│       ├── result_receiver.py
│       └── dummy_questor.py
├── tests/                       # Test-Suiten
│   ├── test_atlas/
│   ├── test_contracts/
│   ├── test_gremium/
│   ├── test_hal/
│   ├── test_integration/
│   ├── test_questor_interface/
│   ├── test_resource_governor/
│   └── test_transaction/
└── data/                        # Datenverzeichnisse
    ├── archiv/
    ├── atlas/
    ├── wal/
    ├── operational_logs/
    └── questor_blackbox/
```

### Verzeichnis-Beschreibungen

| Verzeichnis | Beschreibung |
|-------------|--------------|
| `src/contracts/` | Pydantic-Datenmodelle für alle Systemverträge |
| `src/gremium/` | Intelligenzschicht: Archivar, Kartograph, Kanzler, Vordenker, Lotse, Quartiermeister, Sicherheitsrat |
| `src/atlas/` | Wissensspeicher, Signal-Registry, Clustering-Dienste |
| `src/transaction/` | Write-Ahead Log, State Machine, Recovery-Mechanismen |
| `src/resource_governor/` | Slot-Manager, Governor, ESTOP-Handler, Zone-Manager |
| `src/hal/` | Hardware Abstraction Layer Interface und Dummy-Implementierung |
| `src/questor_interface/` | Dispatcher, Receiver, Dummy-Questor für Integration |
| `tests/` | Alle Test-Suiten (505 Tests in 10 Phasen) |
| `data/` | Laufzeitdaten: Archiv, Atlas, WAL, Logs, Questor-Blackbox |

---

## Phasen-Übersicht

Das System wurde in 10 Phasen implementiert und getestet:

| Phase | Komponente | Tests | Status |
|-------|------------|-------|--------|
| 1 | Contracts & Datenmodelle | ~50 | ✅ Abgeschlossen |
| 2 | Atlas & Signal-System | ~40 | ✅ Abgeschlossen |
| 3 | Transaction (WAL, State Machine) | ~30 | ✅ Abgeschlossen |
| 4 | Resource Governor & HAL | ~50 | ✅ Abgeschlossen |
| 5 | Gremium Basis (Archivar, Kartograph) | ~40 | ✅ Abgeschlossen |
| 6 | Gremium Erweitert (Vordenker, Lotse) | ~50 | ✅ Abgeschlossen |
| 7 | Sicherheitsrat (Richter, Seher) | ~40 | ✅ Abgeschlossen |
| 8 | Questor-Interface | ~40 | ✅ Abgeschlossen |
| 9 | Pipeline-Orchestrierung | ~45 | ✅ Abgeschlossen |
| 10 | Integration & Regression | ~120 | ✅ Abgeschlossen |

**Gesamt:** 505 Tests grün

---

## Dokumentation

| Dokument | Zweck |
|----------|-------|
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | Vollständige Architektur-Dokumentation für Entwickler und Architekten |
| [`SECURITY.md`](./SECURITY.md) | Sicherheitsdokumentation für Sicherheitsverantwortliche und Auditoren |
| [`DEPLOYMENT.md`](./DEPLOYMENT.md) | Deployment-Anleitung und Konfiguration |

### Spezifikations-Referenzen

- `structure_standalone_v2.4.0.md` — Hauptreferenz (Strukturversion 1.1.1)
- `structure_hal_v0.2.0.md` — HAL-Spezifikation
- `myrmex_questor_integration_tests_v0.4.0.md` — Test-Spezifikation

---

## Lizenz / Credits

MYRMEX v2.4.0 + Questor v0.2.3

Entwickelt als autonomes Wissenschaftssystem nach Ameisenstaat-Prinzip.

**Kernprinzipien:**
- Menschliche Königin wird niemals überstimmt
- Fail-Closed als Sicherheitsgarantie
- Operational ≠ Scientific (strikt getrennt)
- Deterministisch vor LLM
