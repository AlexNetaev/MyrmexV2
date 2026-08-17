# 🏛️ MASTER INDEX & ARCHITECTURE FREEZE v1.0.0
**Status:** 🛑 ARCHITECTURE FROZEN. 
**Datum:** 18. August 2026
**System:** MYRMEX v2.4.0 + Questor v0.2.3 + HAL v0.2.0

## 1. Der Anti-Endlosschleifen-Pakt
Dieses Dokument friert den Scope der Architektur ein. 
- Es werden **keine** neuen Spezifikations-Features mehr für v2.4.0 erfunden.
- Unklare Details während der Codierung werden als "Implementation Detail" im Code (via Docstrings/Implementierung) gelöst, nicht durch neue Spec-Patches.
- Jede neue Idee wandert in ein "Backlog für v3.0.0".

## 2. Aktive Source-of-Truth Dokumente (Bindend für Code)
Diese Dokumente definieren die exakte Architektur. Widersprüche in älteren Docs werden ignoriert.
1. **`structure_standalone_v2.4.0.md`** (Strukturversion 1.1.1) 
   - *Zweck:* Hauptreferenz für Gremium, Questor-Integration, Pipelines, Datenverträge.
2. **`structure_hal_v0.2.0.md`** (HAL-Version 0.2.0) 
   - *Zweck:* Hardware Abstraction Layer (Prozesse, Interlocks, Zonen, Compute).
3. **`myrmex_questor_integration_tests_v0.4.0.md`** (Testversion 0.4.0) 
   - *Zweck:* Die 74 bindenden Tests (Suites N, I, S, R, Z, H).

## 3. Archivierte / Deprecated Dokumente (NICHT in den Code-Chat laden!)
- `structure_standalone_v2.3.1.md` (Veraltet, enthält alte "Schwarm"-Begriffe)
- `questor_myrmex_integration_addendum_v0.1.md` (Ersetzt durch Testdatei v0.4.0)
- `structure_standalone_questor_v0.2.3.md` (Nur historisch, bei Konflikt gilt Doc #1)

## 4. Regel für den implementierenden Chat
Wenn du als KI diesen Index liest: Deine Aufgabe ist es nicht, die Spezifikation zu hinterfragen oder zu erweitern. Deine Aufgabe ist es, die in den oben genannten Dokumenten definierten Verträge in lauffähigen, getesteten Python-Code (Pydantic v2, pytest) zu übersetzen.