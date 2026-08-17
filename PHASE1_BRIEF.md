# 🚀 PHASE 1 BRIEF: Verträge, Dummies & TDD-Skelett
**Ziel:** Das absolute Fundament legen. Keine Logik, nur Datenstrukturen, Interfaces und das Test-Gerüst.

## 1. Kontext für die KI
Du bist ein Senior Python Engineer. Wir starten ein neues Projekt: **MYRMEX v2.4.0**. 
Wir nutzen **Python 3.10+**, **Pydantic v2** für Datenmodelle und **pytest** für Tests.
Wir arbeiten streng Test-Driven (TDD). Zuerst werden die leeren Test-Skelette geschrieben, dann die Modelle, bis die Tests grün sind.

## 2. Deine Aufgaben in Phase 1

### Aufgabe A: Repository-Struktur anlegen
Erstelle exakt diese Ordnerstruktur:
```text
myrmex_v2/
 ├── pyproject.toml              # (Erstelle ein Standard-Setup für pytest + pydantic)
 ├── src/
 │   ├── contracts/              # Pydantic v2 Modelle
 │   │   ├── enums.py
 │   │   ├── research_package.py
 │   │   ├── questor_dispatch.py
 │   │   ├── questor_result.py
 │   │   ├── hal_models.py       # Aus HAL v0.2.0
 │   │   └── questor_metadata.py
 │   ├── gremium/
 │   ├── hal/
 │   │   ├── hal_interface.py    # Abstrakte Klasse / Protocol
 │   │   └── dummy_hal.py        # Minimales Stub
 │   └── questor_interface/
 │       └── dummy_questor.py    # Minimales Stub
 └── tests/
     ├── test_contracts/
     └── test_hal/
```

### Aufgabe B: Die Kern-Verträge modellieren (Pydantic v2)
Implementiere die folgenden Modelle basierend auf `structure_standalone_v2.4.0.md` (v1.1.1) und `structure_hal_v0.2.0.md`:

1. **`QuestorErgebnisPaket`**
   - *Kritisch:* `idempotency_key` muss via `@model_validator` automatisch und kanonisch aus `package_id:zyklus_id:attempt_id` gebildet werden.
   - `attempt_id` muss `int >= 0` und `<= 999999` sein.
   - `abbruch_klasse` ist Pflicht (Enum: OPERATIONAL, SCIENTIFIC, SAFETY).

2. **`QuestorDispatchEnvelope`**
   - *Kritisch:* `gate_record_ref` ist ein Pflichtfeld (String). Fehlt es, muss die Validierung fehlschlagen.
   - `security_mode` und `dispatch_mode` als Enums.

3. **HAL-Modelle (`hal_models.py`)**
   - `HALCommand` und `ProcessCommand` (getrennte Modelle!).
   - `SlotState` mit den neuen Zuständen (u.a. `INTERLOCKED`).
   - `EstopState` mit `origin` (SOFTWARE | HARDWARE_INTERLOCK).
   - `EnvironmentManifest`.

### Aufgabe C: Dummy-Stubs erstellen
Erstelle abstrakte Interfaces und minimale Dummies, damit wir später Logik andocken können:
- `hal_interface.py`: Definiere ein Python `Protocol` oder `ABC` mit den Methoden `get_environment_manifest()`, `execute_command()`, `start_process()`, `report_estop()`.
- `dummy_hal.py`: Implementiere das Interface. Wirf standardmäßig `NotImplementedError` oder gib leere Default-Objekte zurück.
- `dummy_questor.py`: Eine Funktion `execute(envelope: QuestorDispatchEnvelope) -> QuestorErgebnisPaket`, die vorerst nur ein leeres Fehler-Paket (`PACKAGE_INVALID`) zurückgibt.

### Aufgabe D: TDD-Skelette für die wichtigsten Tests
Schreibe leere `pytest`-Funktionen mit Docstrings, die beschreiben, was sie tun sollen. Lass sie vorerst fehlschlagen (oder nutze `pytest.mark.skip`), bis die Modelle stehen.

**Beispiele für `tests/test_contracts/test_idempotency.py`:**
```python
def test_idempotency_key_is_canonical():
    """Test Z-02: Key muss exakt package_id:zyklus_id:attempt_id sein, ohne Whitespace."""
    # TODO: Implement
    pass

def test_idempotency_key_rejects_leading_zeros():
    """Test Z-02: attempt_id=02 ist ungültig und muss zu PACKAGE_INVALID führen."""
    # TODO: Implement
    pass

def test_idempotency_key_rejects_out_of_bounds_attempt():
    """Test Z-02: attempt_id > 999999 muss abgelehnt werden."""
    # TODO: Implement
    pass
```

**Beispiele für `tests/test_contracts/test_envelope.py`:**
```python
def test_envelope_requires_gate_record():
    """Test N-04/I-04: Envelope ohne gate_record_ref ist invalid."""
    # TODO: Implement
    pass
```

## 3. Akzeptanzkriterien für Phase 1 (Definition of Done)
- [ ] `pyproject.toml` existiert und `pytest` ist konfigurierbar.
- [ ] Alle Enums (Status, AbbruchKlasse, SecurityMode, SlotStatus, EstopOrigin) sind definiert.
- [ ] `QuestorErgebnisPaket` validiert den kanonischen `idempotency_key` automatisch bei der Instanziierung.
- [ ] `QuestorDispatchEnvelope` lehnt Pakete ohne `gate_record_ref` ab.
- [ ] `HALCommand` und `ProcessCommand` sind strikt getrennt.
- [ ] Keine einzige Zeile Code enthält noch alte Begriffe wie `swarm`, `SwarmErgebnisPaket` oder `MockSwarm`.
- [ ] Das Test-Skelett ist lauffähig (auch wenn einige Tests noch `skip` sind oder `NotImplemented` werfen).

## 4. Output-Erwartung
Generiere den vollständigen Code für Phase 1. Beginne mit `pyproject.toml`, dann die `src/contracts/` Modelle, dann die Dummies, dann die Test-Skelette.