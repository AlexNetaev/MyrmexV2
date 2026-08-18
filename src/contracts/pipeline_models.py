"""Pipeline models for MYRMEX v2.4.0."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.contracts.enums import GateMode, GateDecision, RichterResult, SeherResult, OnboardingStatus, CircuitBreakerState, AppealStatus, AppealDecision, PolicyReviewDecision


class Wegmarke(BaseModel):
    """Wegmarke: Ein definierter Meilenstein im Forschungsprozess."""

    model_config = ConfigDict(extra="forbid")

    wegmarke_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: str | None = None
    version: str = Field(..., min_length=1)

    required_capabilities: list[str] = Field(default_factory=list)
    parameter_schema_ref: str | None = None


class RohIdee(BaseModel):
    """RohIdee: Eine initiale Forschungsidee vor der Paketierung."""

    model_config = ConfigDict(extra="forbid")

    idee_id: str = Field(..., min_length=1)
    titel: str = Field(..., min_length=1)
    beschreibung: str = Field(..., min_length=1)

    ziel_hypothese: str | None = None
    relevante_wegmarken: list[str] = Field(default_factory=list)

    prioritaet: int = Field(default=0, ge=0, le=10)
    metadata: dict[str, Any] = Field(default_factory=dict)


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
