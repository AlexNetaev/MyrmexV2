"""Questor Ergebnis Paket Modelle."""
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class AbbruchKlasse(str, Enum):
    """Kategorie des Abbruchs."""
    OPERATIONAL = "OPERATIONAL"
    SCIENTIFIC = "SCIENTIFIC"
    SAFETY = "SAFETY"


class AbbruchGrund(str, Enum):
    """Grund des Abbruchs."""
    OOM = "OOM"
    ESTOP = "ESTOP"
    ROUTING_LOOP_TIMEOUT = "ROUTING_LOOP_TIMEOUT"
    LEASE_DENIED = "LEASE_DENIED"
    PACKAGE_INVALID = "PACKAGE_INVALID"
    GATE_REJECTED = "GATE_REJECTED"
    NONE = "NONE"  # Kein Abbruch


class LocalAuditRef(BaseModel):
    """Referenz auf lokale Audit-Daten."""
    audit_id: str
    blackbox_id: Optional[str] = None
    trail_hash: Optional[str] = None
    stored_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class OperationalMetrics(BaseModel):
    """Operative Metriken der Ausführung."""
    runtime_s: float = 0.0
    memory_peak_mb: float = 0.0
    cpu_percent: float = 0.0
    loop_iterations: int = 0
    branch_evaluations: int = 0


class QuestorMetadata(BaseModel):
    """Metadaten des Questor-Ergebnisses."""
    questor_instance_id: str
    sequence_number: int
    completed_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    local_audit: Optional[LocalAuditRef] = None
    operational_metrics: Optional[OperationalMetrics] = None


class QuestorErgebnisPaket(BaseModel):
    """
    Ergebnis-Paket vom Questor.
    Regel 4: Receiver validiert dieses Paket.
    Regel 6: DummyQuestor liefert dieses Paket.
    """
    paket_id: str = Field(..., description="Eindeutige Paket-ID")
    dispatch_ref: str = Field(..., description="Referenz auf Dispatch-Envelope")
    status: str = Field(..., description="STATUS: erfolgreich, abgebrochen, fehlgeschlagen")
    abbruch_grund: Optional[AbbruchGrund] = None
    abbruch_klasse: Optional[AbbruchKlasse] = None
    vollstaendig_flag: bool = Field(..., description="Vollständigkeits-Flag")
    questor_metadata: QuestorMetadata
    ergebnis_zusammenfassung: Optional[str] = None
    signale_fuer_atlas: list[dict[str, Any]] = Field(default_factory=list)
    domain_metadata: dict[str, Any] = Field(default_factory=dict)
    
    model_config = {"arbitrary_types_allowed": True}
