"""Questor Ergebnis Paket Modelle."""
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator
from enum import Enum

from src.contracts.enums import ErgebnisStatus, AbbruchKlasse as AbbruchKlasseEnum, AbbruchKlasse
from src.contracts.questor_metadata import QuestorMetadata


# Exportiere AbbruchKlasse und AbbruchGrund für andere Module
__all__ = ["QuestorErgebnisPaket", "AbbruchKlasse", "AbbruchGrund", "LocalAuditRef", "OperationalMetrics"]


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


class QuestorErgebnisPaket(BaseModel):
    """
    Ergebnis-Paket vom Questor.
    Regel 4: Receiver validiert dieses Paket.
    Regel 6: DummyQuestor liefert dieses Paket.
    
    Rückwärtskompatibel zum alten Schema (Phase 2 Archivar).
    Alle alten Felder sind vorhanden, neue Felder sind optional.
    """
    # Alte Pflichtfelder (müssen bleiben für Archivar-Kompatibilität)
    package_id: str = Field(..., description="Eindeutige Paket-ID", min_length=1, pattern=r"^[a-zA-Z0-9_-]+$")
    zyklus_id: str = Field(..., description="Zyklus-ID", pattern=r"^[a-zA-Z0-9_-]+$")
    attempt_id: int = Field(..., description="Attempt-ID", ge=1, le=999)
    questor_instance_id: str = Field(..., description="Questor-Instanz-ID")
    sequence_number: int = Field(..., description="Sequenznummer", ge=0)
    observed_atlas_version_id: str = Field(..., description="Atlas-Version-ID")
    status: ErgebnisStatus = Field(..., description="STATUS: erfolgreich, abgebrochen, fehlgeschlagen")
    abbruch_grund: Optional[str] = None
    abbruch_klasse: AbbruchKlasseEnum = Field(default=AbbruchKlasseEnum.OPERATIONAL, description="Abbruch-Kategorie")
    vollstaendig_flag: bool = Field(..., description="Vollständigkeits-Flag")
    rohdaten_checksumme: str = Field(..., description="Checksumme der Rohdaten", min_length=1)
    kristall_kandidaten: list[Any] = Field(default_factory=list, description="Kandidaten für Kristalle")
    ergebnis_daten: dict[str, Any] = Field(default_factory=dict, description="Ergebnisdaten")
    validierung: dict[str, Any] = Field(default_factory=dict, description="Validierungsdaten")
    gefahren_beobachtet: list[str] = Field(default_factory=list, description="Beobachtete Gefahren")
    signale_fuer_atlas: list[Any] = Field(default_factory=list, description="Signale für Atlas")
    routing_checkpoint: dict[str, Any] = Field(default_factory=dict, description="Routing-Checkpoint")
    
    # Neue optionale Felder (Phase 8B) - alle optional mit Default-Werten
    paket_id: Optional[str] = Field(default=None, description="Alias für package_id")
    dispatch_ref: Optional[str] = Field(default=None, description="Referenz auf Dispatch-Envelope")
    questor_metadata: Optional[QuestorMetadata] = Field(default=None, description="Metadaten des Questors")
    ergebnis_zusammenfassung: Optional[str] = Field(default=None, description="Zusammenfassung des Ergebnisses")
    domain_metadata: dict[str, Any] = Field(default_factory=dict, description="Domain-Metadaten")
    
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    
    @property
    def idempotency_key(self) -> str:
        """Berechnet den Idempotenz-Schlüssel aus package_id:zyklus_id:attempt_id."""
        return f"{self.package_id}:{self.zyklus_id}:{self.attempt_id}"
    
    @model_validator(mode='before')
    @classmethod
    def validate_idempotency_key_format(cls, data: Any) -> Any:
        """Validiert, dass der idempotency_key keine führenden Nullen hat."""
        if isinstance(data, dict):
            idempotency_key = data.get('idempotency_key')
            if idempotency_key is not None:
                # Prüfe auf führende Nullen im attempt_id-Teil
                parts = idempotency_key.split(':')
                if len(parts) == 3:
                    attempt_part = parts[2]
                    if attempt_part != attempt_part.lstrip('0') or (attempt_part == '0' and len(attempt_part) > 1):
                        raise ValueError("Idempotency-Key darf keine führenden Nullen im attempt_id-Teil haben")
        return data
    
    @model_validator(mode='after')
    def validate_abbruch_consistency(self) -> 'QuestorErgebnisPaket':
        """Validiert die Konsistenz von status, abbruch_grund und abbruch_klasse."""
        # Bei ERFOLGREICH darf kein abbruch_grund gesetzt sein und abbruch_klasse muss OPERATIONAL sein
        if self.status == ErgebnisStatus.ERFOLGREICH:
            if self.abbruch_grund is not None:
                raise ValueError("Bei ERFOLGREICH darf abbruch_grund nicht gesetzt sein (PACKAGE_INVALID)")
            if self.abbruch_klasse != AbbruchKlasseEnum.OPERATIONAL:
                raise ValueError("Bei ERFOLGREICH muss abbruch_klasse OPERATIONAL sein (PACKAGE_INVALID)")
        
        # Bei ABGEBROCHEN oder FEHLGESCHLAGEN muss abbruch_grund gesetzt sein
        if self.status in [ErgebnisStatus.ABGEBROCHEN, ErgebnisStatus.FEHLGESCHLAGEN]:
            if self.abbruch_grund is None:
                raise ValueError("Bei ABGEBROCHEN/FEHLGESCHLAGEN muss abbruch_grund gesetzt sein (PACKAGE_INVALID)")
        
        return self
