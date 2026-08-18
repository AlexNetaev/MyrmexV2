"""Questor Dispatch Envelope Modelle."""
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, model_validator
from enum import Enum


class SecurityMode(str, Enum):
    """Sicherheitsmodus für den Dispatch."""
    DEV_SANDBOX_ONLY = "DEV_SANDBOX_ONLY"
    PHYSICAL_ALLOWED = "PHYSICAL_ALLOWED"
    ESTOP_ACTIVE = "ESTOP_ACTIVE"


class GateMode(str, Enum):
    """Gate-Modus."""
    STRICT = "STRICT"
    LENIENT = "LENIENT"
    SANDBOX = "SANDBOX"


class LeaseGrant(BaseModel):
    """Lease-Grant für eine Slot-ID."""
    slot_id: str
    lease_id: str
    granted_at: str
    ttl_s: int
    status: str  # GRANTED, QUEUED, DENIED


class QuestorDispatchEnvelope(BaseModel):
    """
    Dispatch-Envelope für die Übergabe an Questor.
    Regel 1: Dispatcher baut IMMER einen QuestorDispatchEnvelope.
    Regel 2: gate_record_ref ist PFLICHTFELD.
    """
    dispatch_id: str = Field(..., description="Eindeutige Dispatch-ID")
    zyklus_id: str = Field(..., description="Zyklus-ID", pattern=r"^[a-zA-Z0-9_-]+$")
    attempt_id: int = Field(..., description="Versuchs-ID", ge=1, le=999)
    package: Any = Field(..., description="ResearchPackage (aus research_package.py)")
    gate_record_ref: str = Field(..., description="Referenz auf Gate Record (PFLICHT)", min_length=1)
    gate_mode: GateMode = Field(..., description="Gate-Modus")
    lease_grants: list[LeaseGrant] = Field(default_factory=list, description="Lease-Grants")
    security_mode: SecurityMode = Field(..., description="Sicherheitsmodus")
    idempotency_key: str = Field(..., description="Idempotenz-Schlüssel")
    execution_environment_ref: Optional[str] = Field(None, description="Referenz auf Execution Environment")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Erstellungszeitpunkt")
    
    model_config = {"arbitrary_types_allowed": True}
    
    @model_validator(mode='after')
    def validate_idempotency_key(self) -> 'QuestorDispatchEnvelope':
        """Validiert, dass der idempotency_key kanonisch ist: package_id:zyklus_id:attempt_id."""
        # Extrahiere package_id aus dem Package
        if hasattr(self.package, 'package_id'):
            expected_key = f"{self.package.package_id}:{self.zyklus_id}:{self.attempt_id}"
        else:
            expected_key = f"{self.package.get('package_id', '')}:{self.zyklus_id}:{self.attempt_id}"
        
        if self.idempotency_key != expected_key:
            raise ValueError(f"Idempotency-Key muss kanonisch sein: {expected_key}, got: {self.idempotency_key}")
        
        return self
