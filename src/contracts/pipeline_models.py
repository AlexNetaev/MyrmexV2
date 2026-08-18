"""Pipeline models for MYRMEX v2.4.0."""

from enum import Enum
from typing import Any
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.contracts.enums import GateMode, GateDecision, RichterResult, SeherResult, OnboardingStatus, CircuitBreakerState, AppealStatus, AppealDecision, PolicyReviewDecision


# =============================================================================
# IdeenIntent und EvidenceStatus Enums
# =============================================================================

class IdeenIntent(str, Enum):
    """IdeenIntent: Intent einer Forschungsidee."""
    
    EXPLORATION = "EXPLORATION"
    VERFEINERUNG = "VERFEINERUNG"
    FRACTURE_DIAGNOSIS = "FRACTURE_DIAGNOSIS"
    MITIGATION = "MITIGATION"


class EvidenceStatus(str, Enum):
    """EvidenceStatus: Status der Evidenz einer Gefahrenhypothese."""
    
    BELEGT = "BELEGT"
    HYPOTHETISCH = "HYPOTHETISCH"
    UNBEKANNT = "UNBEKANNT"


class FilterDecision(str, Enum):
    """FilterDecision: Entscheidung des Pre-Filters."""
    
    ERLAUBEN = "ERLAUBEN"
    VERWERFEN = "VERWERFEN"
    DIMENSION_GAP = "DIMENSION_GAP"


# =============================================================================
# GefahrenHypothese Model
# =============================================================================

class GefahrenHypothese(BaseModel):
    """GefahrenHypothese: Hypothese über mögliche Gefahren einer Idee."""
    
    model_config = ConfigDict(extra="forbid")
    
    beschreibung: str = Field(..., min_length=1)
    evidence_status: EvidenceStatus = EvidenceStatus.HYPOTHETISCH
    referenzen: list[str] = Field(default_factory=list)


# =============================================================================
# RohIdee Model (erweitert für Phase 7A)
# =============================================================================

class RohIdee(BaseModel):
    """RohIdee: Eine initiale Forschungsidee vor der Paketierung."""

    model_config = ConfigDict(extra="forbid")

    idee_id: str = Field(..., min_length=1)
    intent: IdeenIntent = IdeenIntent.EXPLORATION
    ziel_koordinate: dict[str, float] = Field(default_factory=dict)
    beschreibung: str = Field(..., min_length=1)
    gefahren_hypothese: GefahrenHypothese = Field(default_factory=lambda: GefahrenHypothese(beschreibung="Keine bekannten Gefahren"))
    proposed_dimensions: list[str] = Field(default_factory=list)
    atlas_version_ref: str = Field(..., min_length=1)
    status: str = "OFFEN"
    fracture_diagnosis_budget: float | None = None
    
    # Legacy fields for backward compatibility
    titel: str | None = None
    relevante_wegmarken: list[str] = Field(default_factory=list)
    prioritaet: int = Field(default=0, ge=0, le=10)
    metadata: dict[str, Any] = Field(default_factory=dict)
    ziel_hypothese: str | None = None


# =============================================================================
# FilterEvent und FilterResult Models
# =============================================================================

class FilterEvent(BaseModel):
    """FilterEvent: Protokolliertes Event einer Pre-Filter-Entscheidung."""
    
    model_config = ConfigDict(extra="forbid")
    
    event_id: str = Field(..., min_length=1)
    idee_id: str = Field(..., min_length=1)
    decision: FilterDecision
    reason: str = Field(..., min_length=1)
    timestamp: str = Field(..., min_length=1)
    signal_snapshot: dict[str, str] = Field(default_factory=dict)  # SignalType as string


class FilterResult(BaseModel):
    """FilterResult: Ergebnis der Pre-Filter-Prüfung."""
    
    model_config = ConfigDict(extra="forbid")
    
    decision: FilterDecision
    reason: str = Field(..., min_length=1)
    filter_event: FilterEvent


# =============================================================================
# BlockedCacheEntry Model
# =============================================================================

class BlockedCacheEntry(BaseModel):
    """BlockedCacheEntry: Eintrag im blocked_cache des Vordenkers."""
    
    model_config = ConfigDict(extra="forbid")
    
    idee_id: str = Field(..., min_length=1)
    grund: str = Field(..., min_length=1)
    timestamp: str = Field(..., min_length=1)


# =============================================================================
# DimensionOnboardingRequest (bereits vorhanden, wird hier nur referenziert)
# =============================================================================


class Wegmarke(BaseModel):
    """Wegmarke: Ein definierter Meilenstein im Forschungsprozess."""

    model_config = ConfigDict(extra="forbid")

    wegmarke_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: str | None = None
    version: str = Field(..., min_length=1)

    required_capabilities: list[str] = Field(default_factory=list)
    parameter_schema_ref: str | None = None


class RichterRule(BaseModel):
    """RichterRule: Deterministische Regel für den Richter."""

    model_config = ConfigDict(extra="forbid")

    dimension: str = Field(..., min_length=1)
    min_value: float | None = None
    max_value: float | None = None
    forbidden_materials: list[str] = Field(default_factory=list)
    required_mitigations: list[str] = Field(default_factory=list)


class DimensionOnboardingRequest(BaseModel):
    """DimensionOnboardingRequest: Anfrage zur Aufnahme einer neuen Dimension."""

    model_config = ConfigDict(extra="forbid")

    onboarding_request_id: str = Field(..., min_length=1)
    dimension: str = Field(..., min_length=1)
    package_id: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=1)
    status: OnboardingStatus = OnboardingStatus.PENDING


class GateRecord(BaseModel):
    """GateRecord: Sicherheits- und Validierungsrecord für ein Gate."""

    model_config = ConfigDict(extra="forbid")

    gate_record_id: str = Field(..., min_length=1)
    gate_id: str = Field(..., min_length=1)
    package_id: str = Field(..., min_length=1)
    zyklus_id: str = Field(..., min_length=1)

    gate_mode: GateMode = GateMode.NORMAL
    gate_decision: GateDecision = GateDecision.ABGELEHNT

    richter_result: RichterResult = RichterResult.RICHTER_REJECT
    seher_result: SeherResult = SeherResult.SEHER_NOT_AVAILABLE

    safety_checks_passed: bool = False
    validation_checks_passed: bool = False

    fracture_diagnosis_result: str | None = None
    override_reason: str | None = None
    sandbox_constraints: list[str] = Field(default_factory=list)

    approved_by: str | None = None
    approved_at: str | None = None

    risk_assessment: dict[str, Any] = Field(default_factory=dict)
    mitigation_requirements: list[str] = Field(default_factory=list)

    signature: str = Field(default="", min_length=0)
    timestamp: str = Field(..., min_length=1)

    dimension_onboarding_requests: list[DimensionOnboardingRequest] = Field(default_factory=list)

    physical_execution_allowed: bool = True


class SeherVeto(BaseModel):
    """SeherVeto: Veto des Sehers mit Evidenz."""

    model_config = ConfigDict(extra="forbid")

    veto_grund: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence_refs: list[str] = Field(..., min_length=1)
    policy_ref: str = Field(..., min_length=1)


class SeherResultModel(BaseModel):
    """SeherResultModel: Ergebnis der Seher-Prüfung."""

    model_config = ConfigDict(extra="forbid")

    decision: SeherResult = SeherResult.SEHER_NOT_AVAILABLE
    veto_grund: str | None = None
    confidence: float | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    policy_ref: str | None = None
    fallback_used: bool = False
    
    # Hilfsfeld für den Zugriff auf das vollständige Veto-Objekt
    veto: SeherVeto | None = None


class CircuitBreakerMetrics(BaseModel):
    """CircuitBreakerMetrics: Metriken des Circuit-Breakers."""

    model_config = ConfigDict(extra="forbid")

    invalid_veto_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    false_block_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    appeal_success_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    window_size: int = Field(default=100, ge=1)
    sample_size: int = Field(default=0, ge=0)


class CircuitBreakerAuditEvent(BaseModel):
    """CircuitBreakerAuditEvent: Audit-Event bei Zustandswechsel."""

    model_config = ConfigDict(extra="forbid")

    old_state: CircuitBreakerState
    new_state: CircuitBreakerState
    trigger: str = Field(..., min_length=1)
    metric_name: str | None = None
    metric_value: float | None = None
    window_size: int = Field(..., ge=1)
    sample_size: int = Field(..., ge=0)
    timestamp: str = Field(..., min_length=1)
    authority: str | None = None


class Appeal(BaseModel):
    """Appeal: Berufung bei DISPUTED-Entscheidung."""

    model_config = ConfigDict(extra="ignore")

    appeal_id: str = Field(..., min_length=1)
    package_id: str = Field(..., min_length=1)
    seher_veto: SeherVeto | None = None
    richter_result: RichterResult
    status: AppealStatus = AppealStatus.PENDING
    gate_mode: str | None = None
    created_at: str | None = None


class AppealResolution(BaseModel):
    """AppealResolution: Auflösung einer Berufung."""

    model_config = ConfigDict(extra="forbid")

    appeal_id: str = Field(..., min_length=1)
    decision: AppealDecision
    reason: str = Field(..., min_length=1)
    resolved_by: str = Field(..., min_length=1)
    timestamp: str = Field(..., min_length=1)


class PolicyVetoReview(BaseModel):
    """PolicyVetoReview: Review eines Policy-Vetos."""

    model_config = ConfigDict(extra="forbid")

    event_type: str = "policy_veto_review"
    zyklus_id: str = Field(..., min_length=1)
    policy_veto_id: str = Field(..., min_length=1)
    review_decision: PolicyReviewDecision
    review_reason: str = Field(..., min_length=1)
    review_timestamp: str = Field(..., min_length=1)
    review_authority: str = Field(..., min_length=1)
    escalation_target: str | None = None


# =============================================================================
# Phase 7B: Lotse Models
# =============================================================================

class WegmarkeTyp(str, Enum):
    """WegmarkeTyp: Typ einer Wegmarke."""
    
    NORMAL = "NORMAL"
    DIAGNOSTIC = "DIAGNOSTIC"


class WegmarkeStatus(str, Enum):
    """WegmarkeStatus: Status einer Wegmarke."""
    
    PLATZIERT = "PLATZIERT"
    VERWORFEN = "VERWORFEN"
    ZURUECKGESTELLT = "ZURUECKGESTELLT"
    BLOCKIERT = "BLOCKIERT"


class LotseDecision(str, Enum):
    """LotseDecision: Entscheidung des Lotsen."""
    
    PLATZIEREN = "PLATZIEREN"
    VERWERFEN = "VERWERFEN"
    ZURUECKSTELLEN = "ZURUECKSTELLEN"


class Wegmarke(BaseModel):
    """Wegmarke: Eine platzierte Wegmarke im Atlas."""
    
    model_config = ConfigDict(extra="forbid")
    
    wegmarke_id: str = Field(..., min_length=1)
    idee_id: str = Field(..., min_length=1)
    ziel_koordinate: dict[str, float] = Field(default_factory=dict)
    wegmarke_typ: WegmarkeTyp = WegmarkeTyp.NORMAL
    atlas_version_ref: str = Field(..., min_length=1)
    signal_snapshot_version: str = Field(..., min_length=1)
    fracture_diagnosis_budget: float | None = None
    status: WegmarkeStatus = WegmarkeStatus.PLATZIERT
    platzierungs_timestamp: str = Field(..., min_length=1)


class LotseEvent(BaseModel):
    """LotseEvent: Protokolliertes Event einer Lotse-Entscheidung."""
    
    model_config = ConfigDict(extra="forbid")
    
    event_id: str = Field(..., min_length=1)
    idee_id: str = Field(..., min_length=1)
    decision: LotseDecision
    signal_snapshot: dict[str, str] = Field(default_factory=dict)
    atlas_version_ref: str = Field(..., min_length=1)
    timestamp: str = Field(..., min_length=1)


class LotseResult(BaseModel):
    """LotseResult: Ergebnis der Lotse-Prüfung."""
    
    model_config = ConfigDict(extra="forbid")
    
    decision: LotseDecision
    wegmarke: Wegmarke | None = None
    reason: str = Field(..., min_length=1)
    lotse_event: LotseEvent | None = None


# =============================================================================
# Phase 8A: Quartiermeister Models
# =============================================================================

class QuartiermeisterState(str, Enum):
    """QuartiermeisterState: Zustände der Quartiermeister-Zustandsmaschine."""
    
    WEGMARKE_RESERVIERT = "WEGMARKE_RESERVIERT"
    PAKET_ENTWURF = "PAKET_ENTWURF"
    LOCKED_GATE_PENDING = "LOCKED_GATE_PENDING"
    GATE_APPROVED = "GATE_APPROVED"
    LOCKED_READY_TO_EXEC = "LOCKED_READY_TO_EXEC"
    PAKET_FERTIG = "PAKET_FERTIG"
    PAKET_VERWORFEN = "PAKET_VERWORFEN"


class LeaseReservation(BaseModel):
    """LeaseReservation: Kurzlebige Resource Reservation beim Resource Governor."""
    
    model_config = ConfigDict(extra="forbid")
    
    reservation_id: str = Field(..., min_length=1)
    package_id: str = Field(..., min_length=1)
    slot_ids: list[str] = Field(default_factory=list)
    ttl_s: float = Field(..., gt=0.0)
    status: str = Field(..., min_length=1)  # ACTIVE, EXPIRED, RELEASED
    created_at: str = Field(..., min_length=1)





class PackageKontext(BaseModel):
    """PackageKontext: Kontextinformationen für ein ResearchPackage (Phase 8A)."""

    model_config = ConfigDict(extra="forbid")

    kontext_id: str = Field(..., min_length=1)
    domaene: str = Field(..., min_length=1)
    beschreibung: str = Field(..., min_length=1)
    erwartete_transformation: str = Field(..., min_length=1)

    # Legacy fields for backward compatibility
    parent_package_id: str | None = None
    related_packages: list[str] = Field(default_factory=list)
    domain: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
