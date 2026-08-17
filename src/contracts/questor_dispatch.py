from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.contracts.enums import DispatchMode, GateMode, SecurityMode
from src.contracts.research_package import ID_PATTERN, ResearchPackage


class LeaseGrant(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lease_id: str = Field(..., min_length=1)
    slot_id: str | None = None
    path_id: str | None = None
    package_id: str | None = None

    physical_execution_allowed: bool = False
    sandbox_execution_allowed: bool = False
    compute_execution_allowed: bool = False


class QuestorDispatchEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dispatch_id: str = Field(..., min_length=1)
    zyklus_id: str = Field(
        ...,
        pattern=ID_PATTERN,
        min_length=1,
        max_length=128,
    )
    attempt_id: int = Field(..., ge=0, le=999_999, strict=True)

    package: ResearchPackage
    gate_record_ref: str = Field(..., min_length=1)
    gate_mode: GateMode | None = None

    lease_grants: list[LeaseGrant] = Field(default_factory=list)
    execution_environment_ref: str | None = None

    dispatch_mode: DispatchMode = DispatchMode.NORMAL
    security_mode: SecurityMode = SecurityMode.NORMAL

    dispatch_timestamp: str = Field(..., min_length=1)
    idempotency_key: str | None = None

    @model_validator(mode="after")
    def _canonical_idempotency_key(self) -> "QuestorDispatchEnvelope":
        expected = f"{self.package.package_id}:{self.zyklus_id}:{self.attempt_id}"

        if len(expected) > 264:
            raise ValueError("PACKAGE_INVALID")

        if not self.idempotency_key:
            self.idempotency_key = expected
        elif self.idempotency_key != expected:
            raise ValueError("PACKAGE_INVALID")

        return self
