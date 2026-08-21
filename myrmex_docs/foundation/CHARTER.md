# 🏛️ CHARTER — VERFASSUNG DES MYRMEX-SYSTEMS

| Feld | Wert |
| :--- | :--- |
| **Dateiname** | `foundation/CHARTER.md` |
| **Version** | 1.0.0 (New Architecture) |
| **Status** | **BINDEND** (Architektur-Freeze) |
| **System** | MYRMEX v2.4.0 + Questor v0.2.3 + HAL v0.2.0 |
| **Geltung** | Oberste Instanz für Prinzipien, Sicherheitsregeln und Hierarchie |
| **Datum** | 21. August 2026 |

---

## 0. Präambel: Der Anti-Endlosschleifen-Pakt
Dieses Dokument friert den Scope der Architektur ein.
1.  **Single Source of Truth:** Jede Information in diesem Dokument ist genau einmal definiert. Alle anderen Dokumente referenzieren sie.
2.  **Keine neuen Features:** Unklare Details während der Codierung werden als "Implementation Detail" im Code gelöst, nicht durch neue Spec-Patches.
3.  **Backlog:** Jede neue Idee wandert in ein "Backlog für v3.0.0".
4.  **Vorrang:** Bei Widersprüchen zwischen diesem Dokument und anderen Spezifikationen (CONTRACTS, SPECS) gilt **immer** dieser Charter.

---

## §1 System-Überblick

### 1.1 Die 6 Schichten
| Schicht | Name | Verantwortung |
| :--- | :--- | :--- |
| **5** | 👑 Königin | Langfristige Vision, Meta-Ziele, menschliche Führung |
| **4** | 🏛️ Gremium | Intelligenz, Atlas, Archiv, Ideen, Pakete, Sicherheit |
| **3** | ⚖️ Dispatch-Koordination | Dispatch-Vorbereitung, Lease-/Gate-Koordination |
| **2** | 🧭 Questor | Paketgebundenes Execution Subsystem (Totalfunktion) |
| **1** | 🔌 HAL & Resource Governor | Slot-Routing, Leases, ESTOP, Hardwarezugriff |
| **0** | ⚙️ Physis / Compute | Hardware, Simulation, Compute |

### 1.2 Die 9-Stufen-Pipeline
1.  **Wissens-Aufnahme** (Archivar)
2.  **Atlas-Strukturierung** (Kartograph)
3.  **Strategische Review** (Kanzler ↔ Königin)
4.  **Ideen-Generierung** (Vordenker)
5.  **Pre-Filter & Ideen-Erdung** (Lotse)
6.  **Paket-Bau** (Quartiermeister)
7.  **Sicherheits-Gate** (Richter + Seher)
8.  **Dispatch & Execution** (Dispatcher → Questor → Receiver)
9.  **Wissens-Rückfluss** (Archivar)

---

## §2 Kernprinzipien (Die 4 Säulen)

| Prinzip | Definition |
| :--- | :--- |
| **1. Fail-Closed** | Wenn ein Zustand nicht sicher bestimmt werden kann: **keine Ausführung**, kontrollierter Abbruch oder Eskalation. Niemals "blind" weitermachen. |
| **2. Deterministic-First** | LLMs dürfen beraten, aber **niemals final entscheiden**. QuestCompass und PolicyEvaluator entscheiden deterministisch. |
| **3. Totalfunktion** | Questor liefert **IMMER** ein Ergebnis (`questor_ergebnis_paket`). Auch bei Early-Abort, Crash oder Shutdown. |
| **4. Blackboard-Pattern** | Keine direkten Aufrufe zwischen Gremiums-Rängen. Kommunikation nur über Atlas und Archiv. Questor ist **kein** Gremiums-Rang. |

---

## §3 Sicherheitsregeln (Der Kanon)
*Dies ist die zentrale Liste aller 58 Sicherheitsregeln. Alle anderen Dokumente verweisen auf diese IDs.*

### A. Grundregeln (Hauptreferenz & Questor)
| ID | Regel |
| :--- | :--- |
| **SR-01** | Keine physische Ausführung ohne gültigen `QuestorDispatchEnvelope`. |
| **SR-02** | Keine physische Ausführung ohne gültiges Gate (`gate_record_ref`). |
| **SR-03** | Keine physische Ausführung ohne gültige Lease (`lease_grants`). |
| **SR-04** | Questor schreibt **nie** in Atlas oder Archiv. |
| **SR-05** | Questor setzt **nie** einen ESTOP zurück. |
| **SR-06** | Questor vergibt **nie** Leases (nur Resource Governor). |
| **SR-07** | QuestorBlackbox bleibt **lokal** und isoliert. |
| **SR-08** | **Operational ≠ Scientific**: Prozessfehler erzeugen keine wissenschaftlichen Signale. |
| **SR-09** | **ESTOP ≠ LEASE_DENIED**: Ressourcenkonflikte sind Operational, keine Safety-Events. |
| **SR-10** | Fail-Closed bei Unklarheit (z.B. unklarer Crash-Zustand). |
| **SR-11** | Menschliche Königin wird **niemals** überstimmt. |
| **SR-12** | Hardwarezugriff **nur** über HAL. |
| **SR-13** | LLM ist **nur Advisor**, niemals finale Instanz. |
| **SR-14** | NaN/Infinity in Payloads führt zu **Fail-Closed** (C18). |
| **SR-15** | `atlas_version_ref` ist Pass-Through (kein LLM-Zugriff). |
| **SR-16** | Recovery erfolgt **NUR** aus WAL (keine Blackbox-Recovery). |
| **SR-17** | Ledger ist **READ-ONLY** nach Paket-Abschluss. |
| **SR-18** | Kristallkandidat = Loop + Einstellungen + Ergebnis (nicht nur Messwert). |
| **SR-19** | Bei SAFETY-Abbruch: Kristalle und Signale sind **leer**. |
| **SR-20** | `vollstaendig_flag` ist **IMMER** true (Totalfunktion). |
| **SR-21** | Questor verarbeitet **immer nur EIN** Paket sequentiell. |
| **SR-22** | Questor ist ein **eigener Prozess** (los gelöst vom Gremium). |
| **SR-23** | Pakete in `processing/` sind **nicht löschbar** (außer durch Shutdown/Recovery). |

### B. Sanitization & LLM-Schutz
| ID | Regel |
| :--- | :--- |
| **SR-24** | Nur Whitelist-Felder (`ziel`, `kontext`, `bounds`) gelangen an das LLM. |
| **SR-25** | Injection-Patterns werden erkannt und **quarantänen**. |
| **SR-26** | LLM-Output wird gegen Constraints (`parameter_bounds`) validiert. |
| **SR-27** | Safety-Claims im LLM-Output ("ignore safety") werden **abgelehnt**. |
| **SR-28** | Bei LLM-Fehler/Timeout: **Deterministischer Fallback**. |
| **SR-29** | `security_mode` wird dem LLM **NICHT** mitgeteilt. |

### C. Capability & Security Mode
| ID | Regel |
| :--- | :--- |
| **SR-30** | Unbekannte Capability → **VETO**. |
| **SR-31** | Deprecated Capability → **VETO**. |
| **SR-32** | Leere `allowed_capabilities` → **KEINE** Capability erlaubt (Fail-Closed). |
| **SR-33** | Security-Mode-Mismatch → **VETO**. |
| **SR-34** | NaN/Infinity in Parametern → **Fail-Closed**. |
| **SR-35** | **Min-Rule**: Der restriktivste Modus (Paket/Gate/System/Slot) gewinnt. |
| **SR-36** | Kein Default auf `NORMAL` bei fehlendem Modus (`PACKAGE_INVALID`). |
| **SR-37** | `RECOVERY` erlaubt nur `reconcile_*` und `read_*`. |
| **SR-38** | Keine Modus-Eskalation während der Laufzeit. |
| **SR-39** | Gate ist die **absolute Grenze** (Questor darf Gate nicht umgehen). |

### D. Shutdown, Health & Ops
| ID | Regel |
| :--- | :--- |
| **SR-40** | Keine neuen Pakete bei Shutdown. |
| **SR-41** | Keine neuen HAL-Kommandos bei Shutdown. |
| **SR-42** | WAL-Flush ist **obligatorisch** vor Beendigung. |
| **SR-43** | **ESTOP** hat Vorrang vor Shutdown. |
| **SR-44** | Shutdown ist **immer OPERATIONAL** (nie SAFETY). |
| **SR-45** | Health-Monitoring ist **immer OPERATIONAL**. |
| **SR-46** | Health-Monitoring blockiert **nicht** die Ausführung. |
| **SR-47** | Kein automatischer Neustart bei `WAITING_FOR_RELEASE` oder `SAFE_HOLD`. |
| **SR-48** | Kein automatischer Neustart ohne WAL-Prüfung. |

### E. Trail-Map & Queue
| ID | Regel |
| :--- | :--- |
| **SR-49** | Trail-Map ist **OPERATIONAL** (keine wissenschaftlichen Signale). |
| **SR-50** | Trail-Map bleibt **lokal** (Blackbox). |
| **SR-51** | Trail-Map ist **APPEND-ONLY**. |
| **SR-52** | Trail-Map wird **nicht** vom LLM gelesen. |
| **SR-53** | Kein Dispatch ohne `gate_record_ref`. |
| **SR-54** | Keine Duplikate in der Queue (Idempotenz). |
| **SR-55** | Atomare Schreiboperationen (temp + rename). |
| **SR-56** | Registry-Lock ist Pflicht. |
| **SR-57** | Kein Löschen von `processing/` durch Gremium. |
| **SR-58** | Queue-Fehler sind **immer OPERATIONAL**. |

---

## §4 Gremium-Auslagerungen (Der Kanon)
*Aufgaben, die Questor NICHT selbst erledigt, sondern an das Gremium delegiert.*

| ID | Thema | Verantwortlich |
| :--- | :--- | :--- |
| **G-01** | Template-Erstellung bei fehlendem Template | Quartiermeister + Experte |
| **G-02** | Template-Korrektur nach Feedback | Domain-Experte |
| **G-03** | Template-Versionierung (Archiv) | Archivar |
| **G-04** | Ressourcen-Karte (Verbrauch) | Kartograph |
| **G-05** | Prozess-Skizze mit Idee | Vordenker |
| **G-06** | `template_feedback` protokollieren | Archivar |
| **G-07** | Kosten-Schätzungen (Reagenzien) | System-Integrator |
| **G-08** | Periodische Template-Übersicht | Kanzler |
| **G-09** | `template_feedback` berücksichtigen | Quartiermeister |
| **G-10** | `atlas_version_ref` Pass-Through | Questor (Intern) |
| **G-11** | `loop_selection_weights` | Quartiermeister |
| **G-12** | `planning_hints` | Quartiermeister |
| **G-13** | Atlas-Update via Registry | Pipeline-Orchestrator |
| **G-14** | Queue-Bereinigung | Archivar |
| **G-15** | Löschanfragen stellen | Kanzler |
| **G-16** | Capability-Definitionen pflegen | System-Integrator |
| **G-17** | Health-Monitoring (Extern) | Pipeline-Orchestrator |
| **G-18** | Recovery-Aktionen auslösen | Kanzler |
| **G-19** | Shutdown-Signal senden | Kanzler |
| **G-20** | Trail-Map lesen (Audit) | Domain-Experte |
| **G-21** | CI/CD Pipeline | System-Integrator |
| **G-22** | Phasen-Freigabe | Kanzler / Architekt |

---

## §5 Grundannahmen & Invarianten
*   **Nebenläufigkeit:** Questor verarbeitet **immer nur EIN** Paket sequentiell.
*   **LLM-Backend:** Abstrahiert (Ollama/gemma), wechselbar, aber **nie** entscheidend.
*   **Kosten-Tracking:** Zeit + Reagenzien + Compute (normiert).
*   **Kristallkandidat:** Loop + Einstellungen + Ergebnis (NICHT der Messwert allein).
*   **Signal:** Fazit aus Kristallkandidaten (deterministisch erzeugt).
*   **Budget-Logik:** Ziel erreichen, nicht Budget ausgeben.

---

## §6 Verbotene Patterns
Folgende Muster sind in der Zielarchitektur **streng verboten**:
1.  **Questor schreibt in Atlas/Archiv.**
2.  **Questor setzt ESTOP zurück.**
3.  **Gremium liest QuestorBlackbox.**
4.  **Dispatcher sendet produktiv ohne `gate_record_ref`.**
5.  **Produktive Adapterlogik** zwischen alter (Swarm) und neuer (Questor) Welt.
6.  **Operational wird als Scientific interpretiert.**
7.  **LEASE_DENIED wird als ESTOP behandelt.**
8.  **HAL vergibt Leases.**
9.  **HAL interpretiert wissenschaftliche Ziele.**
10. **Zwei gleichwertige primäre Referenzdateien** ohne Konflikthierarchie.

---

## §7 Idempotenz-Kanon
Der `idempotency_key` ist der Schlüssel zur Crash-Sicherheit und Duplikat-Vermeidung.

**Format:**
```regex
^[A-Za-z0-9._-]{1,128}$ : ^[A-Za-z0-9._-]{1,128}$ : [0-9]{1,6}
```
**Komponenten:**
1.  `package_id` (String, max 128 Zeichen)
2.  `zyklus_id` (String, max 128 Zeichen)
3.  `attempt_id` (Integer, 0 bis 999999, **keine führenden Nullen**)

**Beispiele:**
*   ✅ `pkg-001:zyklus-014:2` (Gültig)
*   ❌ `pkg-001:zyklus-014:02` (Ungültig: führende Null)
*   ❌ `pkg 001:zyklus-014:2` (Ungültig: Leerzeichen)

---

## §8 Dokumentenhierarchie
Dieses Dokument steht an der Spitze der Pyramide.

1.  **Layer 0 (Fundament):** `CHARTER.md` (Dieses Dokument), `CONTRACTS.md`
2.  **Layer 1 (Spezifikation):** `QUESTOR.md`, `HAL.md`, `GREMIUM.md`
3.  **Layer 2 (Operation):** `VALIDATION.md`, `ROADMAP.md`

**Regel:** Ein Dokument in Layer N darf niemals ein Dokument in Layer N-1 widersprechen.