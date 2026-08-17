"""Pipeline models for MYRMEX v2.4.0."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.contracts.enums import GateMode


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


class GateRecord(BaseModel):
    """GateRecord: Sicherheits- und Validierungsrecord für ein Gate."""

    model_config = ConfigDict(extra="forbid")

    gate_id: str = Field(..., min_length=1)
    package_id: str = Field(..., min_length=1)
    zyklus_id: str = Field(..., min_length=1)

    gate_mode: GateMode = GateMode.NORMAL

    safety_checks_passed: bool = False
    validation_checks_passed: bool = False

    fracture_diagnosis_result: str | None = None
    override_reason: str | None = None
    sandbox_constraints: list[str] = Field(default_factory=list)

    approved_by: str | None = None
    approved_at: str | None = None

    risk_assessment: dict[str, Any] = Field(default_factory=dict)
    mitigation_requirements: list[str] = Field(default_factory=list)
