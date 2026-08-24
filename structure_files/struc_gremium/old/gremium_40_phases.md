# GREMIUM PHASE STEERING — Mission Phases & PhaseProfiles

| Feld | Wert |
|------|------|
| **Dateiname** | `gremium_40_phases.md` |
| **Modul** | PHASES |
| **Version** | 1.0.0 |
| **Status** | AKTIV |
| **Hängt ab von** | `gremium_10_core@1.0.0`, `gremium_20_contracts@1.0.0`, `gremium_30_rules@1.0.0` |
| **Änderungsgrund** | KV2-01, KV2-06, KV2-08, KV2-14: Phasen-basierte Makro-Steuerung |
| **Change-Log** | 1.0.0: Initiale Phasen-Architektur mit 5 MissionPhases |

---

## §0 Zweck und Geltung

Dieses Modul definiert die **Phasen-basierte Makro-Steuerung** des Gremiums. Statt alle Edge-Cases durch individuelle Sonderregeln abzudecken, kennt das System **5 diskrete Missionsphasen**. Jede Phase lädt ein eigenes **PhaseProfile** (Regelsatz, Toleranzen, Budget-Logik, Eskalations-Timeouts).

**Kernprinzip:** Phasen drehen an deklarierten Stellgrößen, sie ändern niemals Struktur oder Safety.

---

## §1 MissionPhase-Zustandsmaschine

### §1.1 Phasen-Enum

```python
class MissionPhase(str, Enum):
    BOOTSTRAP_CALIBRATION = "BOOTSTRAP_CALIBRATION"
    EXPLORATION = "EXPLORATION"
    EXPLOITATION = "EXPLOITATION"
    PHYSICAL_WAIT = "PHYSICAL_WAIT"
    CRISIS = "CRISIS"
```

### §1.2 Zustandsübergänge

```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     │
    START ──► BOOTSTRAP_CALIBRATION ──► EXPLORATION ──► EXPLOITATION
                    │                         │                │
                    │                         │                │
                    └─────────┬───────────────┴────────────────┘
                              │
                              ▼
                    PHYSICAL_WAIT ◄──── (CAPEX, Inkubation, Lieferung)
                              │
                              └──► (Resume) ──► vorherige Phase
                              
    EXPLORATION/EXPLOITATION ──► CRISIS ──► (Resolution) ──► vorherige Phase
```

### §1.3 Transition-Trigger (deterministisch)

| Von | Nach | Trigger-Bedingung |
|-----|------|-------------------|
| START | BOOTSTRAP_CALIBRATION | Manifest approved, SL-BOOT-1..6 abgeschlossen |
| BOOTSTRAP_CALIBRATION | EXPLORATION | Twin kalibriert ODER ≥ N erste Kristalle ODER ≥ M Zyklen |
| EXPLORATION | EXPLOITATION | Weißraum < 20% ODER erste Zone erreicht degraded_threshold ODER Königin-Direktive |
| EXPLOITATION | EXPLORATION | Königin-Direktive (SET_PHASE) ODER Ziel nicht erreicht + Sättigung |
| * | PHYSICAL_WAIT | CapabilityGap mit requires_budget_or Hardware ODER in-flight-Paket blockiert Slot > X Stunden ODER CAPEX-Eskalation offen |
| PHYSICAL_WAIT | vorherige Phase | blocked_cache cleared ODER CAPEX geliefert ODER in-flight abgeschlossen |
| * | CRISIS | Safety-Event ODER Budget ≤ 0 ODER Twin uncalibratable ODER Eskalation timeout |
| CRISIS | vorherige Phase | Menschliche Auflösung ODER Eskalation beantwortet |

---

## §2 PhaseProfile-Schema

### §2.1 Pydantic-Modell

```python
from pydantic import BaseModel
from typing import Optional
from gremium_20_contracts import StrategicLayerConfig, DirectiveIntent

class PhaseProfile(BaseModel):
    """
    Typisiertes Overlay über StrategicLayerConfig.
    Darf NUR deklarierte Parameter überschreiben.
    """
    phase: MissionPhase
    
    # Strukturelle Schalter (explizit erlaubt)
    allowed_intents: list[DirectiveIntent]
    stall_detection_active: bool = True
    budget_burn_active: bool = True
    require_atlas_grounding: bool = True
    replicate_divergence_check: bool = True
    
    # Parameter-Overrides (Partial über StrategicLayerConfig)
    # Implementierung: alle Felder aus StrategicLayerConfig als Optional
    overrides: Optional[PartialStrategicLayerConfig] = None
    
    # Meta
    description: str
    transition_reason: Optional[str] = None
```

### §2.2 PartialStrategicLayerConfig

```python
class PartialStrategicLayerConfig(BaseModel):
    """
    Alle Felder aus StrategicLayerConfig, aber Optional.
    Nur gesetzte Felder werden überschrieben.
    """
    briefing_interval_cycles: Optional[int] = None
    max_briefing_chars: Optional[int] = None
    urgent_cooldown_cycles: Optional[int] = None
    royal_log_anchor_depth: Optional[int] = None
    directive_ttl_cycles_default: Optional[int] = None
    conflict_window_cycles: Optional[int] = None
    no_action_stall_limit: Optional[int] = None
    max_consecutive_llm_failures: Optional[int] = None
    weissraum_min_coverage: Optional[float] = None
    bridge_edge_threshold: Optional[int] = None
    saturation_source: Optional[str] = None
    budget_unlock_threshold_fraction: Optional[float] = None
    stagnation_budget_threshold: Optional[float] = None
    max_dimension_requests_per_topic_per_cycle: Optional[int] = None
    diagnostic_budget_default: Optional[int] = None
    diagnostic_budget_max: Optional[int] = None
    quarantine_max_cycles: Optional[int] = None
    replication_trigger_progress: Optional[float] = None
    replication_weight: Optional[float] = None
    min_confirmations: Optional[int] = None
    replication_cadence_cycles: Optional[int] = None
    twin_pairing_ttl_cycles: Optional[int] = None
    calibration_alert_threshold: Optional[float] = None
    escalation_timeout_cycles: Optional[int] = None
    escalation_reminder_interval_cycles: Optional[int] = None
    review_reminder_interval_cycles: Optional[int] = None
    cold_storage_window_days: Optional[int] = None
    capability_gap_repeat_limit: Optional[int] = None
    full_rebuild_threshold: Optional[float] = None
    degraded_threshold: Optional[float] = None
    quarantine_threshold: Optional[float] = None
    vordenker_queue_high_watermark: Optional[int] = None
    twin_epsilon_default: Optional[float] = None
    twin_abs_tolerance_default: Optional[float] = None
    twin_calibration_max_attempts: Optional[int] = None
    twin_drift_reduction_min: Optional[float] = None
    twin_late_pairing_window_cycles: Optional[int] = None
    bootstrap_retry_limit: Optional[int] = None
    negative_knowledge_decay: Optional[float] = None
    max_concurrent_packages: Optional[int] = None
    manifest_max_chars: Optional[int] = None
    anchor_max_chars: Optional[int] = None
    max_total_context_chars: Optional[int] = None
    cycle_trigger: Optional[str] = None
    # NEU in v0.4.0
    metric_tolerance_multiplier: Optional[float] = None
    require_atlas_grounding: Optional[bool] = None
    burn_rate_multiplier: Optional[float] = None
    physical_wait_max_cycles: Optional[int] = None
```

---

## §3 PhaseProfile-Definitionen

### §3.1 BOOTSTRAP_CALIBRATION

```python
BOOTSTRAP_CALIBRATION_PROFILE = PhaseProfile(
    phase=MissionPhase.BOOTSTRAP_CALIBRATION,
    allowed_intents=[
        DirectiveIntent.NO_ACTION,
        DirectiveIntent.INITIAL_SWEEP,
        DirectiveIntent.HUMAN_ESCALATION,
        DirectiveIntent.CALIBRATE_TWIN,
    ],
    stall_detection_active=False,  # System lernt noch
    budget_burn_active=True,
    require_atlas_grounding=False,  # De-novo erlaubt
    replicate_divergence_check=False,  # Varianz lernen
    overrides=PartialStrategicLayerConfig(
        metric_tolerance_multiplier=2.0,  # Hohe Toleranz
        replication_weight=0.0,  # Keine Replikation
        no_action_stall_limit=10,  # Geduldiger
    ),
    description="System lernt Domäne, Twin kalibriert sich, initiale Varianz wird vermessen."
)
```

**Regel-Profil:**
- Hohe Toleranz für Fehlschläge (kein NEGATIVE_KNOWLEDGE-Penalty)
- De-novo-Hypothesen (atlas_refs = []) explizit erlaubt
- Replikation ausgesetzt
- Stall-Detektion deaktiviert

**Exit-Trigger:** Twin kalibriert ODER ≥ N erste Kristalle ODER ≥ M Zyklen

---

### §3.2 EXPLORATION

```python
EXPLORATION_PROFILE = PhaseProfile(
    phase=MissionPhase.EXPLORATION,
    allowed_intents=[
        DirectiveIntent.NO_ACTION,
        DirectiveIntent.SET_PRIORITY,
        DirectiveIntent.ADD_DIMENSION_HINT,
        DirectiveIntent.INCREASE_DIAGNOSTIC,
        DirectiveIntent.CALIBRATE_TWIN,
        DirectiveIntent.HUMAN_ESCALATION,
    ],
    stall_detection_active=True,
    budget_burn_active=True,
    require_atlas_grounding=False,  # De-novo noch erlaubt
    replicate_divergence_check=False,  # Varianz ist Feature
    overrides=PartialStrategicLayerConfig(
        metric_tolerance_multiplier=2.0,
        exploration_weight=0.90,
        exploitation_weight=0.10,
        no_action_stall_limit=6,
    ),
    description="Breites Scannen des Suchraums, Finden von Hotspots."
)
```

**Regel-Profil:**
- REPLICATE_DIVERGENCE deaktiviert (bio Varianz = Rauschen)
- exploration_weight dominiert
- Toleranzen weit
- De-novo noch erlaubt

**Exit-Trigger:** Weißraum < 20% ODER erste Zone erreicht degraded_threshold

---

### §3.3 EXPLOITATION

```python
EXPLOITATION_PROFILE = PhaseProfile(
    phase=MissionPhase.EXPLOITATION,
    allowed_intents=[
        DirectiveIntent.NO_ACTION,
        DirectiveIntent.SET_PRIORITY,
        DirectiveIntent.ADD_DIMENSION_HINT,
        DirectiveIntent.INCREASE_DIAGNOSTIC,
        DirectiveIntent.CALIBRATE_TWIN,
        DirectiveIntent.HUMAN_ESCALATION,
        DirectiveIntent.ARCHIVE_TOPIC,
        DirectiveIntent.PIVOT_TARGET,
    ],
    stall_detection_active=True,
    budget_burn_active=True,
    require_atlas_grounding=True,  # Jetzt Pflicht
    replicate_divergence_check=True,  # Enge Toleranzen
    overrides=PartialStrategicLayerConfig(
        metric_tolerance_multiplier=1.0,
        exploration_weight=0.20,
        exploitation_weight=0.80,
        replication_weight=0.35,
        min_confirmations=2,
        no_action_stall_limit=4,
    ),
    description="Fokussierung auf vielversprechende Zonen, Verifizierung, enge Toleranzen."
)
```

**Regel-Profil:**
- Enge Toleranzen, Replikations-Quote aktiv
- exploitation_weight dominiert
- atlas_refs Pflicht
- REPLICATE_DIVERGENCE aktiv

**Exit-Trigger:** ziel_erreicht == true ODER SATURATION

---

### §3.4 PHYSICAL_WAIT

```python
PHYSICAL_WAIT_PROFILE = PhaseProfile(
    phase=MissionPhase.PHYSICAL_WAIT,
    allowed_intents=[
        DirectiveIntent.NO_ACTION,
        DirectiveIntent.HUMAN_ESCALATION,
        DirectiveIntent.INCREASE_DIAGNOSTIC,
    ],
    stall_detection_active=False,  # Warten ist legitim
    budget_burn_active=False,  # Budget pausiert
    require_atlas_grounding=True,
    replicate_divergence_check=False,
    overrides=PartialStrategicLayerConfig(
        burn_rate_multiplier=0.0,  # Budget verbrennt nicht
        escalation_timeout_cycles=100,  # Längere Fristen
        no_action_stall_limit=999,  # Deaktiviert
    ),
    description="Physische Wartezeit (CAPEX, Inkubation, Lieferung). Budget pausiert."
)
```

**Regel-Profil:**
- burn_rate_per_cycle = 0
- Stall-Detektion ausgesetzt
- Safety-Monitoring bleibt aktiv
- Nur NO_ACTION, HUMAN_ESCALATION, INCREASE_DIAGNOSTIC erlaubt

**Trigger:** Automatisch bei:
- CapabilityGap mit requires_budget_or_hardware = true
- in-flight-Paket blockiert Slot > X Stunden
- CAPEX-Eskalation offen

**Exit-Trigger:** blocked_cache cleared ODER Lieferung eingetroffen ODER in-flight abgeschlossen

---

### §3.5 CRISIS

```python
CRISIS_PROFILE = PhaseProfile(
    phase=MissionPhase.CRISIS,
    allowed_intents=[
        DirectiveIntent.NO_ACTION,
        DirectiveIntent.HUMAN_ESCALATION,
        DirectiveIntent.ABORT_MISSION,
    ],
    stall_detection_active=False,
    budget_burn_active=True,
    require_atlas_grounding=True,
    replicate_divergence_check=False,
    overrides=PartialStrategicLayerConfig(
        escalation_timeout_cycles=25,  # Schnellere Reaktion
        urgent_cooldown_cycles=1,
        no_action_stall_limit=2,
    ),
    description="Krise: Safety-Event, Budget-Erschöpfung, Twin uncalibratable. Menschliche Entscheidung erforderlich."
)
```

**Regel-Profil:**
- Nur NO_ACTION, HUMAN_ESCALATION, ABORT_MISSION
- Wall-Clock-Timeouts für Menschen
- Schnellere Eskalationen

**Trigger:**
- Safety-Event (ESTOP)
- Budget ≤ 0
- Twin uncalibratable
- Eskalation timeout

**Exit-Trigger:** Menschliche Auflösung ODER Eskalation beantwortet

---

## §4 PhaseHistoryLog

### §4.1 Vertrag

```python
class PhaseTransition(BaseModel):
    transition_id: str
    from_phase: MissionPhase
    to_phase: MissionPhase
    trigger_reason: str
    triggered_by: str  # KANZLER | KOENIGIN | MENSCH | SYSTEM
    timestamp: str
    context_snapshot: dict[str, Any]  # Budget, Zyklen, offene Eskalationen

class PhaseHistoryLog(BaseModel):
    mission_id: str
    transitions: list[PhaseTransition] = []
    current_phase: MissionPhase
    phase_entered_at: str
    updated_at: str
```

### §4.2 Speicherort

`data/governance/phase_history/`

---

## §5 Integration mit bestehenden Regeln

### §5.1 SL-NOACT-1 (Stall-Detektion)

**Vorher:** `no_action_stall_limit` aufeinanderfolgende NO_ACTION ohne Atlas-Fortschritt → URGENT

**Neu:** Stall-Detektion prüft zuerst:
```python
if current_phase_profile.stall_detection_active == False:
    return  # Kein Stall-Alarm
if in_flight_packages_count > 0:
    return  # Pakete brüten, NO_ACTION legitim
# Sonst: normale Stall-Logik
```

### §5.2 SL-BUD-1 (Budget-Burn)

**Vorher:** `used_cycles += 1` je Strategie-Zyklus

**Neu:**
```python
if current_phase_profile.budget_burn_active == False:
    return  # Budget pausiert (PHYSICAL_WAIT)
used_cycles += 1 * current_phase_profile.overrides.burn_rate_multiplier
```

### §5.3 SL-REP-2 (Replikation)

**Vorher:** Replikation bei crystallization_progress ≥ 0.8

**Neu:**
```python
if current_phase_profile.replicate_divergence_check == False:
    return  # Keine Replikation in BOOTSTRAP/EXPLORATION
# Sonst: normale Replikations-Logik
```

### §5.4 SL-HYP-1 (Atlas-Grounding)

**Vorher:** atlas_refs = [] nur bei INITIAL_SWEEP erlaubt

**Neu:**
```python
if current_phase_profile.require_atlas_grounding == False:
    # De-novo erlaubt (BOOTSTRAP, EXPLORATION)
    pass
else:
    # atlas_refs Pflicht (EXPLOITATION, PHYSICAL_WAIT, CRISIS)
    if not hypothesis.atlas_refs:
        return VETO("GROUNDING_REQUIRED")
```

---

## §6 Safety-Garantien

### §6.1 Unveränderliche Regeln

Folgende Regeln können durch PhaseProfile **niemals** umgangen werden:

- SL-SAF-1..6 (Safety-Reaktionskette)
- SL-SAN-0..6 (Sanitization)
- SL-ACC-1..4 (Zugriffsregeln)
- SL-BOOT-0..8 (Bootstrap-Validierung)
- Validierungsreihenfolge (§7.1 in 30_rules)
- CHARTER-Regeln (SR-01..SR-58)

### §6.2 PhaseProfile-Validierung

```python
def validate_phase_profile(profile: PhaseProfile) -> bool:
    # 1. Alle Overrides müssen in StrategicLayerConfig existieren
    for field, value in profile.overrides.dict(exclude_none=True).items():
        if not hasattr(StrategicLayerConfig, field):
            raise ValueError(f"Parameter {field} nicht in StrategicLayerConfig")
    
    # 2. allowed_intents müssen im Enum existieren
    for intent in profile.allowed_intents:
        if intent not in DirectiveIntent:
            raise ValueError(f"Intent {intent} existiert nicht")
    
    # 3. Keine Safety-Parameter überschreiben
    safety_params = ["escalation_timeout_cycles_min", "safety_scan_enabled"]
    for param in safety_params:
        if getattr(profile.overrides, param, None) is not None:
            raise ValueError(f"Safety-Parameter {param} darf nicht überschrieben werden")
    
    return True
```

---

## §7 Tests (L1: Modul-lokal)

| ID | Test | Erwartung |
|----|------|-----------|
| PHASE-01 | Phase-Transition BOOTSTRAP → EXPLORATION bei Twin kalibriert | Transition ausgeführt, PhaseHistoryLog aktualisiert |
| PHASE-02 | Stall-Detektion in PHYSICAL_WAIT deaktiviert | Kein URGENT trotz 10× NO_ACTION |
| PHASE-03 | Budget-Burn in PHYSICAL_WAIT = 0 | used_cycles bleibt gleich |
| PHASE-04 | De-novo-Hypothese in EXPLORATION erlaubt | Hypothese akzeptiert |
| PHASE-05 | De-novo-Hypothese in EXPLOITATION verworfen | VETO(GROUNDING_REQUIRED) |
| PHASE-06 | REPLICATE_DIVERGENCE in EXPLORATION deaktiviert | Kein Symptom trotz Varianz |
| PHASE-07 | REPLICATE_DIVERGENCE in EXPLOITATION aktiv | Symptom emittiert |
| PHASE-08 | PhaseProfile überschreibt nicht-deklarierten Parameter | PhaseProfile ungültig |
| PHASE-09 | PhaseProfile versucht Safety-Regel zu umgehen | PhaseProfile ungültig, Audit |
| PHASE-10 | CRISIS bei ESTOP | Sofortige Transition, nur NO_ACTION/HUMAN_ESCALATION/ABORT erlaubt |
| PHASE-11 | PHYSICAL_WAIT bei CAPEX-Eskalation | Transition, Budget pausiert |
| PHASE-12 | PhaseHistoryLog speichert alle Transitionen | Vollständige Historie |

---

## §8 Fund-Register-Beiträge

| Fund-ID | Behoben durch | Mechanismus |
|---------|---------------|-------------|
| KV2-01 | PHYSICAL_WAIT-Phase | Budget pausiert, Timer stehen nicht still |
| KV2-06 | PHYSICAL_WAIT-Phase | Physische Trägheit als eigener Zustand |
| KV2-08 | EXPLORATION-Phase | De-novo ohne atlas_refs erlaubt |
| KV2-14 | PHYSICAL_WAIT + in_flight-Check | Stall-Detektion ignoriert brütende Pakete |

---

## §9 Change-Log

| Version | Datum | Änderung | Funde behoben |
|---------|-------|----------|---------------|
| 1.0.0 | 2025-01-XX | Initiale Phasen-Architektur mit 5 MissionPhases | KV2-01, KV2-06, KV2-08, KV2-14 |

---

**Ende des Phasen-Moduls.**