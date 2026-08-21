# 🧭 QUESTOR-INTERNA: THEMA 3 — SECURITY-MODE-VERHALTEN
## Vollständige Verhaltensmatrix, Validierung und Durchsetzung der Security-Modi

| Feld | Wert |
|---|---|
| Dateiname | `questor_security_mode_v0.1.0.md` |
| Version | 0.1.0 |
| System | MYRMEX v2.4.0 + Questor v0.2.3 |
| Status | Arbeitsstand — Architektur-Spezifikation, keine Implementierungsfreigabe |
| Bezug | `structure_questor_interna_v0.4.0.md`, Teil M |
| | `structure_standalone_v2.4.0.md` v1.1.1 (kanonisch) |
| | `structure_hal_v0.2.0.md` §23 |
| Sprache | Deutsch |
| Modus | Dry-Run / Spezifikation |

---

## 0. Dokumentenhierarchie und Geltung

```
1. structure_standalone_v2.4.0.md v1.1.1                    ← kanonisch
2. structure_hal_v0.2.0.md                                   ← HAL-Vertrag
3. structure_questor_interna_v0.4.0.md                       ← Questor-Interna GESAMT
4. diese Datei: questor_security_mode_v0.1.0.md              ← Detail: Security-Mode
5. structure_standalone_questor_v0.2.3.md                    ← unterstützend
```

Bei Widersprüchen gilt die kanonische Hauptreferenz.

Dieses Dokument ist Teil M der Questor-Interna-Gesamtspezifikation.
Es ist eigenständig lesbar, setzt aber Grundkenntnisse der Questor-Architektur voraus.

---

## 1. Kritische Analyse des Bestehenden

### 1.1 Was bereits referenziert wird

| Quelle | Definition / Regel | Problem |
|---|---|---|
| `structure_hal_v0.2.0.md` §15 | `NORMAL`, `SANDBOX`, `DEV_SANDBOX_ONLY`, `RECOVERY` | Definiert die HAL-Reaktion (`PHYSICAL_EXECUTION_FORBIDDEN`), aber nicht die Questor-Vorprüfung. |
| `structure_standalone_v2.4.0.md` §10 | `security_mode` muss zu Gate und Leases passen. | **Wie** prüft Questor das? Was passiert bei Mismatch? |
| `structure_questor_interna_v0.3.0.md` | `security_mode` ist Teil des Kontexts, wird im PolicyEvaluator geprüft. | Die exakte Prüffunktion fehlt. |
| `structure_questor_interna_v0.3.0.md` §16 | `security_mode` ist in der LLM-Sanitization-Blocklist. | Richtig, aber was passiert, wenn der LLM aus dem *Kontext* auf den Modus schließt? |

### 1.2 Identifizierte Probleme

| # | Problem | Schweregrad | Begründung |
|---|---|---|---|
| P1 | **Fehlende Hierarchie der Modi.** Es gibt den Paket-Modus, den globalen System-Modus (SAFE_MODE) und den Slot-Modus. Welcher gewinnt? | **KRITISCH** | Ohne Regel "Restriktivster gewinnt" entstehen Sicherheitslücken. |
| P2 | **`RECOVERY` ist zu vage definiert.** "Primär Zustandsklärung" ist keine maschinenlesbare Regel. Welche Capabilities sind in `RECOVERY` erlaubt? | **KRITISCH** | Questor könnte in `RECOVERY` versehentlich physische Aktionen auslösen. |
| P3 | **Keine Vorprüfung (Pre-Flight) gegen das Gate.** Questor könnte einen Loop planen, der `NORMAL` erfordert, obwohl das Gate nur `SANDBOX` freigegeben hat. | Hoch | Führt zu späten Abbrüchen in der HAL-Bridge statt zu frühen Abbrüchen im PolicyEvaluator. |
| P4 | **Verwechslungsgefahr: `security_mode` vs. `dispatch_mode`.** Beide haben den Wert `RECOVERY`. | Mittel | Implementierer könnten die Felder verwechseln. |
| P5 | **Kein Handling für globale Modus-Wechsel während der Laufzeit.** Was passiert, wenn das Gremium während eines laufenden Loops in den `SAFE_MODE` (global) geht? | Hoch | Laufende Prozesse müssen sicher behandelt werden (Lease-Expiry / ESTOP). |
| P6 | **`DEV_SANDBOX_ONLY` vs. `SANDBOX` Trennschärfe.** HAL unterscheidet das, aber wie filtert Questor Templates dafür? | Mittel | Templates müssen als `dev_only` oder `production_sandbox` markiert sein. |

### 1.3 Fazit der Analyse

Der `security_mode` ist keine einfache Eigenschaft, sondern ein **Constraint-Vektor**, der auf vier Ebenen wirkt:
1. **Paket-Ebene** (Vom Gremium vorgegeben)
2. **Gate-Ebene** (Vom Sicherheits-Gate freigegeben)
3. **System-Ebene** (Globaler SAFE_MODE / ESTOP)
4. **Slot-Ebene** (Hardware-Kapazität)

Questor muss diese vier Ebenen **vor der Ausführung** und **während der Ausführung** kontinuierlich abgleichen.

---

## 2. Formale Definition: Security-Mode-Matrix

### 2.1 Die vier Security-Modi

| Modus | Wert | Bedeutung | Physische Actuation | Compute | Sandbox-Simulation |
|---|---|---|---|---|---|
| `NORMAL` | 0 | Produktivbetrieb. Physische Ausführung erlaubt. | ✅ (wenn Lease/Slot/Gate es erlauben) | ✅ | ✅ |
| `SANDBOX` | 1 | Simulationsbetrieb. Keine physische Wirkung auf echte Proben. | ❌ | ✅ (nur Sandbox-Compute) | ✅ (wenn Slot `sandbox_capable`) |
| `DEV_SANDBOX_ONLY` | 2 | Reine Test/Dev-Umgebung. Keine Produktivdaten, keine echten Proben. | ❌ | ✅ (nur Dev-Compute) | ✅ (nur Dev-Sandbox) |
| `RECOVERY` | 3 | Ausnahmezustand. Nur Zustandsklärung und Aufräumarbeiten. | ❌ (außer `reconcile_*`) | ❌ (außer `reconcile_*`) | ❌ |

### 2.2 Das Prinzip der Restriktivität (Min-Rule)

Der **effektive Security-Modus** (`effective_security_mode`) für jede Aktion ist das **Maximum der Restriktivität** (bzw. Minimum der Erlaubnis) aller beteiligten Ebenen.

```python
# Restriktivitäts-Werte (höher = restriktiver)
MODE_RESTRICTIVENESS = {
    "NORMAL": 0,
    "SANDBOX": 1,
    "DEV_SANDBOX_ONLY": 2,
    "RECOVERY": 3
}

def get_effective_security_mode(
    package_mode: str,
    gate_allowed_modes: list[str],
    global_system_mode: str,
    slot_mode_capability: str
) -> str:
    """
    Der effektive Modus ist der restriktivste aller Ebenen.
    """
    # Wenn der Paket-Modus nicht im Gate erlaubt ist → Fail-Closed
    if package_mode not in gate_allowed_modes:
        return "RECOVERY"  # Fail-Closed: Abbruch oder Recovery
    
    modes = [
        package_mode,
        global_system_mode,
        slot_mode_capability
    ]
    
    # Wähle den Modus mit dem höchsten Restriktivitäts-Wert
    return max(modes, key=lambda m: MODE_RESTRICTIVENESS.get(m, 3))
```

### 2.3 Interaktion: `security_mode` vs. `dispatch_mode`

Diese beiden Felder werden strikt getrennt:

| Feld | Quelle | Zweck | Werte |
|---|---|---|---|
| `security_mode` | Paket / Gate / System | **SICHERHEIT**: Darf die Aktion physische Wirkung haben? | `NORMAL`, `SANDBOX`, `DEV_SANDBOX_ONLY`, `RECOVERY` |
| `dispatch_mode` | Paket / Pipeline | **OPERATION**: Wie wird das Kommando an HAL übergeben? | `NORMAL`, `RETRY`, `RECOVERY` |

**Regel:** Ein `dispatch_mode = RECOVERY` (z.B. "Sende das Kommando erneut, um den Zustand zu prüfen") ändert **NIEMALS** den `security_mode`. Ein Recovery-Kommando in `security_mode = NORMAL` darf physisch wirken (z.B. "Schließe das Ventil sicher"). Ein Recovery-Kommando in `security_mode = SANDBOX` darf nur simulieren.

---

## 3. Validierung beim Paket-Empfang (Envelope-Check)

Bevor Questor ein Paket in die Queue aufnimmt oder verarbeitet, wird der `security_mode` gegen das Gate validiert.

```python
def validate_package_security_mode(package: ResearchPackage, gate_record: GateRecord) -> bool:
    """
    Prüft, ob der geforderte security_mode des Pakets mit dem Gate kompatibel ist.
    """
    # 1. Gate-Record muss vorhanden sein (C13 / Sicherheitsregel)
    if gate_record is None:
        raise PackageInvalidError("gate_record_ref fehlt")
    
    # 2. Paket-Modus muss im Gate erlaubt sein
    if package.security_mode not in gate_record.allowed_security_modes:
        raise PackageInvalidError(
            f"security_mode '{package.security_mode}' ist nicht in "
            f"gate_record.allowed_security_modes ({gate_record.allowed_security_modes})"
        )
    
    # 3. Wenn Paket physische Actuation fordert, aber Gate nur Sandbox erlaubt
    if package.requires_physical_actuation and "NORMAL" not in gate_record.allowed_security_modes:
        raise PackageInvalidError("Paket fordert Physische Actuation, Gate erlaubt nur Sandbox")
        
    return True
```

**Fehlerbehandlung:**
- Wenn die Validierung fehlschlägt: `abbruch_grund = PACKAGE_INVALID`, `abbruch_klasse = OPERATIONAL`.
- Das Paket wird **nicht** in die Queue aufgenommen (oder sofort als `FAILED` markiert).

---

## 4. Auswirkungen auf QuestCompass & Loop-Selection

Der `security_mode` filtert die verfügbaren Templates und Capabilities **bevor** der LLM-Advisor oder die Scoring-Logik greift.

### 4.1 Template-Filterung (Schritt 1 im QuestCompass)

```python
def filter_templates_by_security_mode(
    templates: list[LoopTemplate],
    effective_mode: str,
    registry: CapabilityRegistry
) -> list[LoopTemplate]:
    
    valid_templates = []
    for template in templates:
        # RECOVERY-Modus: Nur explizite Recovery-Templates erlaubt
        if effective_mode == "RECOVERY":
            if not template.is_recovery_template:
                continue
        
        # Prüfe, ob ALLE Capabilities des Templates im effektiven Modus erlaubt sind
        all_caps_allowed = True
        for cap_id in template.required_capabilities:
            cap_def = registry.capabilities.get(cap_id)
            if not cap_def:
                all_caps_allowed = False
                break
            if effective_mode not in cap_def.allowed_security_modes:
                all_caps_allowed = False
                break
        
        if all_caps_allowed:
            valid_templates.append(template)
            
    return valid_templates
```

### 4.2 Besonderheit: `RECOVERY`-Templates

In `security_mode = RECOVERY` dürfen **nur** Templates ausgewählt werden, die als `is_recovery_template = true` markiert sind.
Diese Templates dürfen **nur** Capabilities nutzen, die der Zustandsklärung dienen (z.B. `sensor.read_state`, `actuator.get_position`, `slot.reconcile`).
**Verboten** in `RECOVERY`: Alle Capabilities, die Materie verändern, Energie einbringen oder Compute-Modelle trainieren.

**Korrektur-Erfordernis:** Das Feld `is_recovery_template: bool` (Default: `false`) muss in die `LoopTemplate`-Spezifikation (Teil C der Questor-Interna) aufgenommen werden.

---

## 5. Auswirkungen auf den PolicyEvaluator

Der PolicyEvaluator (§17 der Questor-Interna) führt den finalen Check vor der Ausführung durch.

```python
def policy_check_security_mode(
    loop_instance: LoopInstance,
    effective_mode: str,
    context: ExecutionContext
) -> PolicyDecision:
    
    # 1. Physische Actuation vs. Modus
    if loop_instance.requires_physical_actuation:
        if effective_mode != "NORMAL":
            return VETO(
                reason="PHYSICAL_ACTUATION_FORBIDDEN_IN_CURRENT_MODE",
                details=f"Loop erfordert physische Actuation, aber effektiver Modus ist {effective_mode}"
            )
    
    # 2. Dimension-Expansion (neue physische Dimensionen)
    if loop_instance.requires_dimension_expansion:
        if effective_mode != "NORMAL":
            return VETO("DIMENSION_EXPANSION_FORBIDDEN_IN_SANDBOX_OR_RECOVERY")
        if context.package.dimension_expansion_approval is None:
            return VETO("DIMENSION_APPROVAL_MISSING")
            
    # 3. RECOVERY-Check: Sind alle Steps im Loop Recovery-konform?
    if effective_mode == "RECOVERY":
        for step in loop_instance.steps:
            if step.step_type == HAL_COMMAND:
                if not step.capability.startswith("reconcile_") and not step.capability.startswith("read_"):
                    return VETO("NON_RECOVERY_CAPABILITY_IN_RECOVERY_MODE")
                    
    return GO()
```

---

## 6. Auswirkungen auf HAL-Bridge & Execution

Die HAL-Bridge übersetzt den Loop in `HALCommand`s und `ProcessCommand`s. Der `effective_security_mode` wird in jedes Kommando geschrieben.

```yaml
HALCommand:
  command_id: "cmd-..."
  security_mode: "SANDBOX"  # ← Wird aus dem effektiven Modus übernommen
  ...
```

### 6.1 HAL-Reaktion auf Modus-Mismatch

Wenn Questor (durch einen Bug oder veraltete Manifest-Daten) einen Command mit `security_mode: NORMAL` sendet, aber der Slot im HAL nur `sandbox_capable = true` ist (oder das globale System im SAFE_MODE ist):

1. HAL lehnt das Kommando ab.
2. HAL antwortet mit `status: DENIED`, `error_code: PHYSICAL_EXECUTION_FORBIDDEN`, `error_class: OPERATIONAL`.
3. **HAL löst KEINEN ESTOP aus** (da es sich um eine operative Ablehnung handelt, nicht um einen Sicherheitsvorfall).
4. Questor HAL-Bridge empfängt die Ablehnung.
5. Questor bricht den Loop ab (`abbruch_grund = HAL_EXECUTION_DENIED`, `abbruch_klasse = OPERATIONAL`).

### 6.2 HAL-Regeln (aus `structure_hal_v0.2.0.md` §23)

| Modus | Physisch | Compute | Sandbox |
|---|---|---|---|
| `NORMAL` | ✅ wenn `physical_actuation = true` und Lease `physical_execution_allowed = true` | ✅ wenn `compute_capable = true` und Lease `compute_execution_allowed = true` | ✅ |
| `SANDBOX` | ❌ | Nur Sandbox-Compute | ✅ wenn `sandbox_capable = true` |
| `DEV_SANDBOX_ONLY` | ❌ | Nur Dev-Compute | Nur Dev-Sandbox |
| `RECOVERY` | ❌ (außer `reconcile_*`) | ❌ (außer `reconcile_*`) | ❌ |

Wenn der Modus nicht zum Slot passt:
- Physisch: `error_code: PHYSICAL_EXECUTION_FORBIDDEN`, `error_class: OPERATIONAL`
- Compute: `error_code: COMPUTE_EXECUTION_FORBIDDEN`, `error_class: OPERATIONAL`

---

## 7. Interaktion mit globalem `SAFE_MODE` und `ESTOP`

### 7.1 Globaler Modus-Wechsel während der Ausführung

Das Gremium (oder der Mensch) kann MYRMEX jederzeit in den globalen `SAFE_MODE` versetzen. Dies geschieht **außerhalb** von Questor.

**Ablauf:**
1. Gremium setzt globalen Modus auf `SAFE_MODE` (entspricht `SANDBOX` oder `RECOVERY` auf Systemebene).
2. HAL suspendiert alle aktiven physischen Leases (`ESTOP_SUSPENDED` oder `SAFE_HOLD`).
3. Questor empfängt von der HAL-Bridge die Meldung: `Lease-Expiry` oder `ESTOP`.
4. Questor-Zustandsmaschine reagiert:
   - Bei `ESTOP`: Übergang zu `FINALIZING` (SAFETY_ABORT).
   - Bei `Lease-Expiry` mit `SAFE_HOLD`: Übergang zu `SAFE_HOLD`.
5. Questor beendet den aktuellen Loop kontrolliert.

**Regel:** Questor selbst **überwacht nicht** den globalen Modus durch Polling. Questor reagiert **ausschließlich** auf die Signale der HAL-Bridge (`ESTOP`, `LEASE_DENIED`, `SAFE_HOLD`).

### 7.2 Vorrang-Regel

```
ESTOP > SAFE_MODE > security_mode (Paket)
```

Wenn ein ESTOP aktiv ist, wird der `security_mode` des Pakets irrelevant. Questor bricht sofort ab.

---

## 8. Edge Cases

| # | Edge Case | Erwartetes Verhalten |
|---|---|---|
| EC-1 | Paket fordert `security_mode: NORMAL`, aber das Gate (`gate_record`) hat nur `["SANDBOX"]` freigegeben. | **Envelope-Check scheitert.** `abbruch_grund = PACKAGE_INVALID`, `abbruch_klasse = OPERATIONAL`. Paket wird nicht ausgeführt. |
| EC-2 | Paket ist `security_mode: SANDBOX`. Das gewählte Template enthält einen Step `reactor.heat` (physische Actuation). Die Capability-Registry erlaubt `reactor.heat` nur in `NORMAL`. | **Template-Filterung (QuestCompass)** entfernt dieses Template. Wenn kein alternatives Template existiert: `NO_APPLICABLE_TEMPLATE`. |
| EC-3 | Paket ist `security_mode: RECOVERY`. Der LLM-Advisor (der den Modus nicht kennt, da er sanitized wurde) schlägt ein Template vor, das `pipette.transfer` nutzt. | **PolicyEvaluator VETO.** `NON_RECOVERY_CAPABILITY_IN_RECOVERY_MODE`. Der LLM-Vorschlag wird verworfen. |
| EC-4 | Questor startet einen Langzeit-Prozess (Inkubator, 72h) in `security_mode: NORMAL`. Nach 24h zieht das Gremium die Lease (globaler SAFE_MODE). | HAL meldet `SAFE_HOLD` (gemäß `on_lease_expiry_policy`). Questor geht in Zustand `SAFE_HOLD`. Prozess wird nicht zerstört, aber angehalten. |
| EC-5 | `security_mode` Feld fehlt im `ResearchPackage` (Null / None). | **Envelope-Check scheitert.** `PACKAGE_INVALID`. Fail-Closed. Default ist NICHT `NORMAL`. |
| EC-6 | Paket ist `DEV_SANDBOX_ONLY`, aber der einzige verfügbare Compute-Slot ist ein Produktions-Slot (nicht als Dev-Sandbox markiert). | **HAL-Bridge / Slot-Check.** HAL lehnt ab mit `COMPUTE_EXECUTION_FORBIDDEN`. Questor bricht operativ ab. |
| EC-7 | Ein Template hat `is_recovery_template = true`, nutzt aber eine Capability, die in der Registry `requires_physical_actuation = true` hat. | **Registry-Validierung beim Start / Template-Upload.** Template wird als ungültig markiert. Recovery-Templates dürfen keine physische Actuation erfordern. |

---

## 9. Sicherheitsregeln (Fail-Closed-Punkte)

| # | Regel | Fail-Closed-Aktion |
|---|---|---|
| S1 | **Min-Rule (Restriktivität):** Der effektivste Modus ist immer der restriktivste aus Paket, Gate, System und Slot. | Wenn uneindeutig → `RECOVERY` oder Abort. |
| S2 | **Kein Default auf NORMAL:** Wenn `security_mode` im Paket fehlt oder ungültig ist, wird NICHT `NORMAL` angenommen. | `PACKAGE_INVALID` (OPERATIONAL). |
| S3 | **RECOVERY ist strikt:** In `RECOVERY` sind nur `reconcile_*` und `read_*` Capabilities erlaubt. | PolicyEvaluator VETO. |
| S4 | **Gate ist die absolute Grenze:** Questor darf niemals einen Modus ausführen, der nicht im `gate_record.allowed_security_modes` steht. | Envelope-Reject. |
| S5 | **LLM-Blindheit:** Der LLM-Advisor erfährt den `security_mode` nicht. Er kann keine Modi "überreden" oder "umschalten". | Sanitization-Blocklist (Thema 1). |
| S6 | **Physische Actuation erfordert NORMAL:** `requires_physical_actuation = true` im Template/Loop führt in jedem Modus außer `NORMAL` zum VETO. | PolicyEvaluator VETO. |
| S7 | **Keine Modus-Eskalation:** Questor kann seinen `security_mode` während der Laufzeit niemals "hochstufen" (z.B. von SANDBOX auf NORMAL). | Architektonisch unmöglich (Read-Only im Kontext). |

---

## 10. Integration mit bestehenden Komponenten

| Komponente | Integration |
|---|---|
| **Envelope / Dispatcher** | Liefert `security_mode` und `gate_record_ref`. Questor validiert beides beim Empfang. |
| **Capability-Registry (Thema 2)** | Liefert `allowed_security_modes` pro Capability. QuestCompass nutzt dies zur Template-Filterung. |
| **QuestCompass** | Filtert Templates. Der LLM-Advisor wird ohne `security_mode`-Kontext aufgerufen. |
| **PolicyEvaluator** | Führt den finalen `policy_check_security_mode` durch. |
| **HAL-Bridge** | Schreibt `security_mode` in jeden `HALCommand` und `ProcessCommand`. |
| **ExpeditionLedger** | Protokolliert den `effective_security_mode` im Genesis-Entry und bei jedem Capability-Check. |
| **Result-Builder** | Wenn ein Paket wegen `PHYSICAL_EXECUTION_FORBIDDEN` abbricht, wird dies als `OPERATIONAL` im Ergebnis protokolliert, nicht als `SAFETY`. |
| **Sanitization (Thema 1)** | `security_mode` ist in der Blocklist und wird dem LLM NICHT mitgeteilt. |
| **Trail-Map (Thema 6)** | Security-Mode-Checks werden als Trails protokolliert (`SECURITY_MODE_CHECK`). |
| **Graceful-Shutdown (Thema 4)** | Shutdown respektiert den `security_mode`. Kein Modus-Wechsel bei Shutdown. |
| **Queue-Integration (Thema 7)** | `security_mode` wird in der `registry.json` protokolliert. |

---

## 11. Validierung durch konkretes Beispiel

### 11.1 Szenario: ML-Training in der Sandbox

**Input (ResearchPackage):**
```yaml
package_id: "pkg-ml-007"
security_mode: "SANDBOX"
gate_record_ref: "gate-7781"
ziel: "Trainiere ein neuronales Netz zur Bilderkennung."
questor_spec:
  allowed_capabilities: ["gpu.train", "cpu.preprocess"]
```

**Gate-Record (vom Gremium):**
```yaml
gate_id: "gate-7781"
allowed_security_modes: ["SANDBOX", "DEV_SANDBOX_ONLY"]
```

**HAL-Manifest (Slot):**
```yaml
slots:
  - slot_id: "gpu-cluster-prod-01"
    capabilities: ["gpu.train"]
    sandbox_capable: false  # Produktions-Slot, keine Sandbox
    physical_actuation: false
    compute_capable: true
  - slot_id: "gpu-cluster-sandbox-01"
    capabilities: ["gpu.train"]
    sandbox_capable: true
    physical_actuation: false
    compute_capable: true
```

### 11.2 Durchlauf

1. **Envelope-Check:**
   - Paket `security_mode = SANDBOX`.
   - Gate `allowed_security_modes = [SANDBOX, DEV_SANDBOX_ONLY]`.
   - Match? **JA**. Paket wird akzeptiert.

2. **QuestCompass (Loop Selection):**
   - Template `ml_train_v1` erfordert `gpu.train`.
   - Registry-Check: `gpu.train` erlaubt `[NORMAL, SANDBOX, DEV_SANDBOX_ONLY]`.
   - Template ist gültig für `SANDBOX`.

3. **PolicyEvaluator:**
   - `effective_security_mode = SANDBOX`.
   - `requires_physical_actuation = false` (Compute).
   - Check bestanden. **GO**.

4. **HAL-Bridge (Execution):**
   - Questor sucht Slot für `gpu.train`.
   - Slot `gpu-cluster-prod-01` ist **NICHT** `sandbox_capable`. Da wir im `SANDBOX` Modus sind, darf dieser Slot **nicht** genutzt werden.
   - Slot `gpu-cluster-sandbox-01` ist `sandbox_capable = true`.
   - Questor wählt `gpu-cluster-sandbox-01`.
   - HALCommand wird mit `security_mode: SANDBOX` und `slot_id: gpu-cluster-sandbox-01` gesendet.

5. **HAL-Ausführung:**
   - HAL prüft: Command ist `SANDBOX`, Slot ist `sandbox_capable`.
   - HAL führt das Training in der isolierten Sandbox-Umgebung aus.
   - **SUCCESS**.

### 11.3 Was wäre passiert, wenn der Sandbox-Slot belegt gewesen wäre?

- Questor hätte keinen gültigen Slot gefunden (`CAPABILITY_NO_SLOT_AVAILABLE` im Kontext von Security-Mode).
- PolicyEvaluator oder HAL-Bridge hätten den Loop operativ abgebrochen.
- `abbruch_grund = NO_SANDBOX_SLOT_AVAILABLE`, `abbruch_klasse = OPERATIONAL`.
- **Kein Fallback auf den Produktions-Slot!** (Fail-Closed).

---

## 12. Offene Fragen und Risiken

| # | Frage / Risiko | Schweregrad | Empfehlung |
|---|---|---|---|
| Q1 | **Wie wird `is_recovery_template` in der LoopTemplate-Struktur verankert?** Bisher gibt es dieses Feld im Template-Schema (Teil C/D) noch nicht explizit. | Hoch | Das Feld `is_recovery_template: bool` (Default: `false`) muss in die `LoopTemplate`-Spezifikation (Teil C) aufgenommen werden. |
| Q2 | **Kann ein Paket `RECOVERY` als `security_mode` haben?** Ja, wenn das Gremium ein Paket schnürt, um einen hängenden Zustand aufzuräumen. Das Gate muss das aber explizit erlauben. | Mittel | Die Spezifikation deckt das ab (Envelope-Check). |
| Q3 | **Was ist der Unterschied zwischen `global_system_mode = SAFE_MODE` und `security_mode = RECOVERY`?** `SAFE_MODE` ist ein Gremiums-weiter Zustand (ESTOP-nah). `RECOVERY` ist ein Paket-spezifischer Modus für Aufräumarbeiten. | Mittel | Die Trennung ist korrekt. Questor reagiert auf SAFE_MODE über HAL-Signale (ESTOP/SAFE_HOLD), nicht über Paket-Felder. |

---

## 13. Zusammenfassung der Spezifikation

| Aspekt | Definition |
|---|---|
| **Werte** | `NORMAL`, `SANDBOX`, `DEV_SANDBOX_ONLY`, `RECOVERY` |
| **Grundprinzip** | Min-Rule: Der restriktivste Modus (aus Paket, Gate, System, Slot) gewinnt immer. |
| **Envelope-Check** | Paket-Modus MUSS im Gate-Record erlaubt sein. Sonst `PACKAGE_INVALID`. |
| **RECOVERY** | Erlaubt nur `reconcile_*` und `read_*` Capabilities. Keine physische Actuation. |
| **LLM-Sanitization** | `security_mode` wird dem LLM vorenthalten. |
| **HAL-Bridge** | Schreibt den effektiven Modus in jedes HALCommand. HAL ist die letzte Instanz, die bei Mismatch mit `PHYSICAL_EXECUTION_FORBIDDEN` (OPERATIONAL) ablehnt. |
| **Fail-Closed** | Fehlender Modus = Abort. Mismatch = Abort. Kein Fallback auf weniger restriktive Modi. |
| **Modulname** | `security_mode.py` |
| **Position** | `src/questor/security_mode.py` |

---

## 14. Kritische Bewertung der eigenen Spezifikation

**Stärken:**
- Die "Min-Rule" (Restriktivität) eliminiert alle Schlupflöcher, bei denen ein Paket durch geschickte Wahl des Templates den Modus aushebeln könnte.
- Klare Trennung zwischen `security_mode` (Sicherheit) und `dispatch_mode` (Operation).
- RECOVERY ist nun maschinenlesbar definiert (nur `reconcile_*` / `read_*`).
- Die Interaktion mit dem globalen SAFE_MODE ist über die HAL-Signale (ESTOP/SAFE_HOLD) sauber gelöst, ohne dass Questor selbst Polling betreiben muss.

**Schwächen / Anpassungsbedarf:**
- Das Feld `is_recovery_template` muss in Teil C (Loop-Architektur) nachgetragen werden.
- Die Slot-Auswahl-Strategie (Thema 2) muss um den `sandbox_capable`-Check erweitert werden. Ein Slot ist nur dann "verfügbar", wenn seine `sandbox_capable`-Eigenschaft zum `effective_security_mode` passt.

**Empfehlung:** Die Spezifikation ist implementierungsreif. Die genannten Anpassungen in Teil C und Thema 2 sollten als Mini-Updates in die jeweiligen Dokumente übernommen werden.

---

## 15. Kreuzreferenzen

| Referenz | Beziehung |
|---|---|
| `structure_questor_interna_v0.4.0.md`, Teil M | Dieses Dokument IST Teil M |
| `structure_hal_v0.2.0.md` §23 | HAL-Regeln für security_mode |
| `structure_standalone_v2.4.0.md` §10.2 | Questor-Sicherheitsregeln |
| `questor_sanitization_v0.1.0.md` | `security_mode` wird dem LLM NICHT mitgeteilt |
| `questor_capability_registry_v0.1.0.md` | `allowed_security_modes` pro Capability |
| `questor_graceful_shutdown_v0.1.0.md` | Shutdown respektiert security_mode |
| `questor_trail_map_v0.1.0.md` | Security-Mode-Checks werden als Trails protokolliert |
| `questor_queue_integration_v0.1.0.md` | security_mode wird in registry.json protokolliert |
| `questor_test_strategy_v0.1.0.md` | 11 Unit-Tests (U-SM-01 bis U-SM-11) |
| `questor_implementation_plan_v0.1.0.md` | Phase Q3 (1-2 Tage) |