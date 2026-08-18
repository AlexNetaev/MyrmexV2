"""Tests für Package Dispatcher."""
import pytest
from unittest.mock import Mock

from src.questor_interface.package_dispatcher import (
    PackageDispatcher,
    PackageInvalidError,
    DispatchResult,
)
from src.contracts.questor_dispatch import (
    QuestorDispatchEnvelope,
    LeaseGrant,
    SecurityMode,
    GateMode,
)
from src.contracts.research_package import ResearchPackage


class MockGateRecord:
    """Mock Gate Record für Tests."""
    def __init__(self, gate_record_id="gate-123", gate_mode=GateMode.STRICT):
        self.gate_record_id = gate_record_id
        self.gate_mode = gate_mode
        self.signature = "valid-signature"


def create_minimal_package():
    """Erstellt minimales ResearchPackage für Tests."""
    return Mock(spec=ResearchPackage, package_id="pkg-123")


def test_dispatcher_builds_envelope():
    """Regel 1: Dispatcher baut QuestorDispatchEnvelope."""
    dispatcher = PackageDispatcher()
    package = create_minimal_package()
    gate_record = MockGateRecord()
    lease_grants = [LeaseGrant(
        slot_id="slot-1",
        lease_id="lease-1",
        granted_at="2024-01-01T00:00:00Z",
        ttl_s=3600,
        status="GRANTED"
    )]
    
    envelope = dispatcher.build_envelope(
        research_package=package,
        gate_record=gate_record,
        lease_grants=lease_grants,
        execution_environment_ref="exec-env-1",
        zyklus_id="1",
        attempt_id=1,
    )
    
    assert isinstance(envelope, QuestorDispatchEnvelope)
    assert envelope.dispatch_id is not None
    assert envelope.zyklus_id == "1"
    assert envelope.attempt_id == 1


def test_dispatcher_envelope_has_gate_record_ref():
    """Regel 2: Envelope enthält gate_record_ref."""
    dispatcher = PackageDispatcher()
    package = create_minimal_package()
    gate_record = MockGateRecord(gate_record_id="gate-456")
    
    envelope = dispatcher.build_envelope(
        research_package=package,
        gate_record=gate_record,
        lease_grants=[],
        execution_environment_ref=None,
    )
    
    assert envelope.gate_record_ref == "gate-456"


def test_dispatcher_envelope_without_gate_record_ref():
    """Regel 2 (KRITISCH): Ohne gate_record_ref → PACKAGE_INVALID."""
    dispatcher = PackageDispatcher()
    package = create_minimal_package()
    
    # Gate Record ohne ID
    gate_record = MockGateRecord(gate_record_id=None)
    
    with pytest.raises(PackageInvalidError) as exc_info:
        dispatcher.build_envelope(
            research_package=package,
            gate_record=gate_record,
            lease_grants=[],
            execution_environment_ref=None,
        )
    
    assert "gate_record_ref fehlt" in str(exc_info.value)


def test_dispatcher_envelope_has_idempotency_key():
    """Envelope hat idempotency_key aus package_id:zyklus_id:attempt_id."""
    dispatcher = PackageDispatcher()
    package = Mock(spec=ResearchPackage, package_id="pkg-789")
    gate_record = MockGateRecord()
    
    envelope = dispatcher.build_envelope(
        research_package=package,
        gate_record=gate_record,
        lease_grants=[],
        execution_environment_ref=None,
        zyklus_id="5",
        attempt_id=3,
    )
    
    assert envelope.idempotency_key == "pkg-789:5:3"


def test_dispatcher_validates_gate_signature():
    """Regel 7: gate_record.signature wird geprüft."""
    dispatcher = PackageDispatcher()
    package = create_minimal_package()
    gate_record = MockGateRecord()
    
    envelope = dispatcher.build_envelope(
        research_package=package,
        gate_record=gate_record,
        lease_grants=[],
        execution_environment_ref=None,
    )
    
    validation = dispatcher.validate_before_dispatch(envelope)
    assert validation.valid is True


def test_dispatcher_validates_lease_status():
    """Regel 7: lease_status wird geprüft."""
    dispatcher = PackageDispatcher()
    package = create_minimal_package()
    gate_record = MockGateRecord()
    
    # Lease mit DENIED-Status
    lease_grants = [LeaseGrant(
        slot_id="slot-1",
        lease_id="lease-1",
        granted_at="2024-01-01T00:00:00Z",
        ttl_s=3600,
        status="DENIED"
    )]
    
    envelope = dispatcher.build_envelope(
        research_package=package,
        gate_record=gate_record,
        lease_grants=lease_grants,
        execution_environment_ref=None,
    )
    
    validation = dispatcher.validate_before_dispatch(envelope)
    assert validation.valid is False
    assert any("DENIED" in e.reason for e in validation.errors)


def test_dispatcher_validates_routing_limits():
    """Regel 7: max_loop_iterations und branch_condition_timeout werden geprüft."""
    dispatcher = PackageDispatcher()
    package = create_minimal_package()
    gate_record = MockGateRecord()
    
    # Package ohne routing_graph
    envelope = dispatcher.build_envelope(
        research_package=package,
        gate_record=gate_record,
        lease_grants=[],
        execution_environment_ref=None,
    )
    
    validation = dispatcher.validate_before_dispatch(envelope)
    # Sollte valid sein, wenn kein routing_graph vorhanden
    assert validation.valid is True


def test_dispatcher_validates_dimension_approval():
    """Regel 7: dimension_expansion_approval wird geprüft, falls physisch."""
    dispatcher = PackageDispatcher()
    package = create_minimal_package()
    gate_record = MockGateRecord()
    
    envelope = dispatcher.build_envelope(
        research_package=package,
        gate_record=gate_record,
        lease_grants=[],
        execution_environment_ref=None,
        security_mode=SecurityMode.PHYSICAL_ALLOWED,
    )
    
    validation = dispatcher.validate_before_dispatch(envelope)
    assert validation.valid is True


def test_dispatcher_direct_package_forbidden():
    """Regel 3: Direkte ResearchPackage-Übergabe → DIRECT_PACKAGE_FORBIDDEN."""
    dispatcher = PackageDispatcher()
    package = create_minimal_package()
    
    result = dispatcher.dispatch_direct_package(
        research_package=package,
        security_mode=SecurityMode.PHYSICAL_ALLOWED,
    )
    
    assert result.success is False
    assert result.error == "DIRECT_PACKAGE_FORBIDDEN"


def test_dispatcher_direct_package_sandbox_only():
    """Regel 3: Direkte Übergabe nur mit DEV_SANDBOX_ONLY erlaubt."""
    dispatcher = PackageDispatcher()
    package = create_minimal_package()
    
    result = dispatcher.dispatch_direct_package(
        research_package=package,
        security_mode=SecurityMode.DEV_SANDBOX_ONLY,
    )
    
    assert result.success is True


def test_dispatcher_no_naked_package_in_production():
    """Regel 1 (KRITISCH): Kein nacktes ResearchPackage im Produktivpfad."""
    dispatcher = PackageDispatcher()
    package = create_minimal_package()
    gate_record = MockGateRecord()
    
    # Im Produktionsmodus muss Envelope gebaut werden
    envelope = dispatcher.build_envelope(
        research_package=package,
        gate_record=gate_record,
        lease_grants=[],
        execution_environment_ref=None,
        security_mode=SecurityMode.PHYSICAL_ALLOWED,
    )
    
    assert isinstance(envelope, QuestorDispatchEnvelope)
    assert envelope.package is not None
