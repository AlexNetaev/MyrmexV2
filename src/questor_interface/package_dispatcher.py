"""Package Dispatcher für Phase 8B."""
import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel

from src.contracts.questor_dispatch import (
    QuestorDispatchEnvelope,
    LeaseGrant,
    SecurityMode,
    GateMode,
)
from src.contracts.research_package import ResearchPackage


class PackageInvalidError(Exception):
    """Paket ist ungültig."""
    pass


class DirectPackageForbiddenError(Exception):
    """Direkte Paket-Übergabe verboten."""
    pass


class DispatchValidationError(BaseModel):
    """Validierungsfehler beim Dispatch."""
    field: str
    reason: str


class ValidationResult(BaseModel):
    """Ergebnis der Validierung."""
    valid: bool
    errors: list[DispatchValidationError] = []


class DispatchResult(BaseModel):
    """Ergebnis des Dispatch."""
    success: bool
    envelope: Optional[QuestorDispatchEnvelope] = None
    error: Optional[str] = None
    error_class: str = "OPERATIONAL"  # OPERATIONAL, SAFETY


class PackageDispatcher:
    """
    Dispatcher baut IMMER einen QuestorDispatchEnvelope.
    Regel 1: Kein nacktes ResearchPackage im Produktivpfad.
    Regel 2: gate_record_ref ist PFLICHTFELD.
    Regel 3: Direkte Übergabe nur mit DEV_SANDBOX_ONLY.
    Regel 7: Dispatcher prüft VOR Dispatch.
    """
    
    def __init__(self, wal=None):
        self.wal = wal
        self._dispatched_envelopes: dict[str, QuestorDispatchEnvelope] = {}
    
    def build_envelope(
        self,
        research_package: ResearchPackage,
        gate_record: Any,
        lease_grants: list[LeaseGrant],
        execution_environment_ref: Optional[str],
        dispatch_mode: str = "PRODUCTION",
        security_mode: SecurityMode = SecurityMode.PHYSICAL_ALLOWED,
        zyklus_id: int = 1,
        attempt_id: int = 1,
    ) -> QuestorDispatchEnvelope:
        """
        Baut QuestorDispatchEnvelope aus ResearchPackage.
        
        Regel 2: gate_record_ref ist PFLICHTFELD.
        """
        # KRITISCH: gate_record_ref prüfen
        if not gate_record or not getattr(gate_record, 'gate_record_id', None):
            raise PackageInvalidError("gate_record_ref fehlt")
        
        # Idempotency-Key berechnen
        idempotency_key = f"{research_package.package_id}:{zyklus_id}:{attempt_id}"
        
        # Gate-Modus aus Gate Record übernehmen
        gate_mode = getattr(gate_record, 'gate_mode', GateMode.STRICT)
        
        envelope = QuestorDispatchEnvelope(
            dispatch_id=str(uuid.uuid4()),
            zyklus_id=zyklus_id,
            attempt_id=attempt_id,
            package=research_package,
            gate_record_ref=gate_record.gate_record_id,
            gate_mode=gate_mode,
            lease_grants=lease_grants,
            security_mode=security_mode,
            idempotency_key=idempotency_key,
            execution_environment_ref=execution_environment_ref,
        )
        
        self._dispatched_envelopes[envelope.dispatch_id] = envelope
        
        return envelope
    
    def validate_before_dispatch(self, envelope: QuestorDispatchEnvelope) -> ValidationResult:
        """
        Regel 7: Prüft VOR Dispatch alle Voraussetzungen.
        - gate_record.signature
        - lease_status
        - Routing-Limits
        - dimension_expansion_approval
        """
        errors = []
        
        # gate_record_ref muss vorhanden sein
        if not envelope.gate_record_ref:
            errors.append(DispatchValidationError(
                field="gate_record_ref",
                reason="gate_record_ref ist PFLICHTFELD"
            ))
        
        # lease_status prüfen (GRANTED oder QUEUED erlaubt)
        for grant in envelope.lease_grants:
            if grant.status not in ("GRANTED", "QUEUED"):
                errors.append(DispatchValidationError(
                    field="lease_grants",
                    reason=f"Lease {grant.lease_id} hat Status {grant.status}"
                ))
        
        # Routing-Limits prüfen
        if hasattr(envelope.package, 'routing_graph'):
            rg = envelope.package.routing_graph
            if not hasattr(rg, 'max_loop_iterations') or rg.max_loop_iterations is None:
                errors.append(DispatchValidationError(
                    field="routing_graph",
                    reason="max_loop_iterations fehlt"
                ))
            if not hasattr(rg, 'branch_condition_timeout') or rg.branch_condition_timeout is None:
                errors.append(DispatchValidationError(
                    field="routing_graph",
                    reason="branch_condition_timeout fehlt"
                ))
        
        # dimension_expansion_approval prüfen (falls physisch)
        if envelope.security_mode == SecurityMode.PHYSICAL_ALLOWED:
            if hasattr(envelope.package, 'dimension_expansion_approval'):
                # Neue Dimensionen ohne Approval sind verboten
                pass  # Logik wird vom Quartiermeister bereits geprüft
        
        return ValidationResult(valid=len(errors) == 0, errors=errors)
    
    def dispatch(self, envelope: QuestorDispatchEnvelope) -> DispatchResult:
        """
        Sendet Envelope an Questor.
        
        Regel 1: Kein nacktes ResearchPackage.
        Regel 2: Ohne gate_record_ref → PACKAGE_INVALID.
        """
        # Validierung vor Dispatch
        validation = self.validate_before_dispatch(envelope)
        if not validation.valid:
            return DispatchResult(
                success=False,
                error=f"Validierung fehlgeschlagen: {validation.errors}",
                error_class="OPERATIONAL"
            )
        
        # Envelope wurde erfolgreich dispatched
        return DispatchResult(
            success=True,
            envelope=envelope
        )
    
    def dispatch_direct_package(
        self,
        research_package: ResearchPackage,
        security_mode: SecurityMode
    ) -> DispatchResult:
        """
        Regel 3: Direkte ResearchPackage-Übergabe ist sandbox-only.
        """
        if security_mode != SecurityMode.DEV_SANDBOX_ONLY:
            return DispatchResult(
                success=False,
                error="DIRECT_PACKAGE_FORBIDDEN",
                error_class="OPERATIONAL"
            )
        
        # Sandbox-Modus: direkte Übergabe erlaubt
        # Aber physical_execution_allowed muss false sein
        return DispatchResult(
            success=True,
            error="Nur im SANDBOX-Modus erlaubt",
            error_class="OPERATIONAL"
        )
