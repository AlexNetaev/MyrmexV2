"""Transaction models for MYRMEX v2.4.0."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WalPhase(str, Enum):
    PREPARE = "PREPARE"
    COMMIT = "COMMIT"


class RecoveryActionType(str, Enum):
    RESUME = "RESUME"
    RETRY_GATE = "RETRY_GATE"
    RECHECK_LEASE = "RECHECK_LEASE"
    CHECK_SLOT = "CHECK_SLOT"
    ABORT = "ABORT"
    QUARANTINE = "QUARANTINE"
    DISCARD = "DISCARD"


class Stage5bState(str, Enum):
    IDEE_OFFEN = "IDEE_OFFEN"
    IDEE_GEPRUEFT = "IDEE_GEPRUEFT"
    IDEE_VERWORFEN = "IDEE_VERWORFEN"
    WEGMARKE_PLATZIERT = "WEGMARKE_PLATZIERT"


class Stage6State(str, Enum):
    WEGMARKE_RESERVIERT = "WEGMARKE_RESERVIERT"
    PAKET_ENTWURF = "PAKET_ENTWURF"
    LOCKED_GATE_PENDING = "LOCKED_GATE_PENDING"
    GATE_APPROVED = "GATE_APPROVED"
    LOCKED_READY_TO_EXEC = "LOCKED_READY_TO_EXEC"
    PAKET_FERTIG = "PAKET_FERTIG"


class Stage7State(str, Enum):
    GATE_PENDING = "GATE_PENDING"
    RICHTER_PASS = "RICHTER_PASS"
    SEHER_PASS = "SEHER_PASS"
    FREIGEGEBEN = "FREIGEGEBEN"
    SEHER_VETO = "SEHER_VETO"
    DISPUTED = "DISPUTED"
    APPEAL_RESOLVED = "APPEAL_RESOLVED"


class Stage8State(str, Enum):
    RESOURCE_WAITING = "RESOURCE_WAITING"
    DISPATCHED = "DISPATCHED"
    EXECUTING = "EXECUTING"
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    ABORTED = "ABORTED"


class WalEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entry_id: str = Field(..., min_length=1)
    sequence_number: int = Field(..., ge=0)
    timestamp: str = Field(..., min_length=1)
    package_id: str = Field(..., min_length=1)
    stage: str = Field(..., min_length=1)
    from_state: str = Field(..., min_length=1)
    to_state: str = Field(..., min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
    phase: WalPhase
    checksum: str = Field(..., min_length=1)


class RecoveryAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    package_id: str = Field(..., min_length=1)
    current_stage: str = Field(..., min_length=1)
    current_state: str = Field(..., min_length=1)
    action: RecoveryActionType
    reason: str = Field(..., min_length=1)
    observed_atlas_version_id: str | None = None
    questor_instance_id: str | None = None
