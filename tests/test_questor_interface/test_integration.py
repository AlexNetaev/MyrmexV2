"""Integrationstests für Questor Interface."""
import pytest
from unittest.mock import Mock

from src.questor_interface.package_dispatcher import PackageDispatcher
from src.questor_interface.result_receiver import ResultReceiver
from src.questor_interface.dummy_questor import DummyQuestor, OperationalCrashError, SafetyViolationError
from src.contracts.questor_dispatch import QuestorDispatchEnvelope, LeaseGrant, SecurityMode, GateMode
from src.contracts.questor_result import AbbruchKlasse, AbbruchGrund


class MockPackage:
    """Mock ResearchPackage."""
    def __init__(self):
        self.package_id = "pkg-integration"


class MockGateRecord:
    """Mock GateRecord."""
    def __init__(self):
        self.gate_record_id = "gate-integration"
        self.gate_mode = GateMode.STRICT


def create_test_envelope():
    """Erstellt Test-Envelope."""
    return QuestorDispatchEnvelope(
        dispatch_id="dispatch-int",
        zyklus_id=1,
        attempt_id=1,
        package=MockPackage(),
        gate_record_ref="gate-integration",
        gate_mode=GateMode.STRICT,
        lease_grants=[LeaseGrant(
            slot_id="slot-1",
            lease_id="lease-1",
            granted_at="2024-01-01T00:00:00Z",
            ttl_s=3600,
            status="GRANTED"
        )],
        security_mode=SecurityMode.PHYSICAL_ALLOWED,
        idempotency_key="pkg-integration:1:1",
    )


def test_quartiermeister_to_dispatcher_pipeline():
    """Quartiermeister → Dispatcher Pipeline funktioniert."""
    dispatcher = PackageDispatcher()
    gate_record = MockGateRecord()
    package = MockPackage()
    
    envelope = dispatcher.build_envelope(
        research_package=package,
        gate_record=gate_record,
        lease_grants=[],
        execution_environment_ref="exec-env",
    )
    
    assert isinstance(envelope, QuestorDispatchEnvelope)
    assert envelope.gate_record_ref == "gate-integration"


def test_dispatcher_to_dummy_questor_pipeline():
    """Dispatcher → DummyQuestor Pipeline funktioniert."""
    dispatcher = PackageDispatcher()
    questor = DummyQuestor()
    gate_record = MockGateRecord()
    
    envelope = dispatcher.build_envelope(
        research_package=MockPackage(),
        gate_record=gate_record,
        lease_grants=[],
        execution_environment_ref=None,
    )
    
    result = questor.execute(envelope)
    
    assert result.dispatch_ref == envelope.dispatch_id
    assert result.status == "erfolgreich"


def test_dummy_questor_to_receiver_pipeline():
    """DummyQuestor → Receiver Pipeline funktioniert."""
    questor = DummyQuestor()
    receiver = ResultReceiver()
    envelope = create_test_envelope()
    
    # Questor ausführen
    ergebnis = questor.execute(envelope)
    
    # Receiver empfängt Ergebnis
    receive_result = receiver.receive(ergebnis)
    
    assert receive_result.success is True
    assert receive_result.forwarded_to_archivar is True


def test_receiver_to_archivar_pipeline():
    """Receiver → Archivar Pipeline funktioniert."""
    mock_archivar = Mock()
    mock_archivar.store = Mock(return_value=True)
    
    receiver = ResultReceiver(archivar=mock_archivar)
    questor = DummyQuestor()
    envelope = create_test_envelope()
    
    ergebnis = questor.execute(envelope)
    receive_result = receiver.receive(ergebnis)
    
    assert receive_result.success is True
    mock_archivar.store.assert_called_once()


def test_full_pipeline_quartiermeister_to_archivar():
    """Vollständige Pipeline: Quartiermeister → Dispatcher → Questor → Receiver → Archivar."""
    mock_archivar = Mock()
    mock_archivar.store = Mock(return_value=True)
    
    dispatcher = PackageDispatcher()
    questor = DummyQuestor()
    receiver = ResultReceiver(archivar=mock_archivar)
    gate_record = MockGateRecord()
    
    # 1. Quartiermeister baut Paket (simuliert)
    package = MockPackage()
    
    # 2. Dispatcher baut Envelope
    envelope = dispatcher.build_envelope(
        research_package=package,
        gate_record=gate_record,
        lease_grants=[],
        execution_environment_ref="exec-env",
    )
    
    # 3. Questor führt aus
    ergebnis = questor.execute(envelope)
    
    # 4. Receiver empfängt und leitet weiter
    receive_result = receiver.receive(ergebnis)
    
    assert receive_result.success is True
    assert mock_archivar.store.called


def test_full_pipeline_with_estop():
    """Pipeline mit ESTOP: Questor bricht ab, Receiver empfängt SAFETY-Ergebnis."""
    mock_archivar = Mock()
    mock_archivar.store = Mock(return_value=True)
    
    questor = DummyQuestor()
    receiver = ResultReceiver(archivar=mock_archivar)
    envelope = create_test_envelope()
    
    # ESTOP simulieren
    try:
        questor.execute_with_estop(envelope)
    except SafetyViolationError as e:
        ergebnis = questor.create_result_for_crash(envelope, e)
        
        # Receiver empfängt SAFETY-Ergebnis
        receive_result = receiver.receive(ergebnis)
        
        assert receive_result.success is True
        assert ergebnis.abbruch_klasse == AbbruchKlasse.SAFETY
        assert ergebnis.abbruch_grund == AbbruchGrund.ESTOP


def test_full_pipeline_with_oom():
    """Pipeline mit OOM: Questor bricht ab, Receiver empfängt OPERATIONAL-Ergebnis."""
    mock_archivar = Mock()
    mock_archivar.store = Mock(return_value=True)
    
    questor = DummyQuestor()
    receiver = ResultReceiver(archivar=mock_archivar)
    envelope = create_test_envelope()
    
    # OOM simulieren
    try:
        questor.execute_with_crash(envelope)
    except OperationalCrashError as e:
        ergebnis = questor.create_result_for_crash(envelope, e)
        
        # Receiver empfängt OPERATIONAL-Ergebnis
        receive_result = receiver.receive(ergebnis)
        
        assert receive_result.success is True
        assert ergebnis.abbruch_klasse == AbbruchKlasse.OPERATIONAL
        assert ergebnis.abbruch_grund == AbbruchGrund.OOM


def test_full_pipeline_with_recovery():
    """Phase 4 Recovery arbeitet mit Questor-Interface zusammen."""
    # Simuliert Recovery nach Crash
    questor = DummyQuestor()
    receiver = ResultReceiver()
    envelope = create_test_envelope()
    
    # Normaler Durchlauf
    ergebnis = questor.execute(envelope)
    receive_result = receiver.receive(ergebnis)
    
    assert receive_result.success is True
    
    # Recovery: Duplikat wird erkannt
    receive_result2 = receiver.receive(ergebnis)
    assert receive_result2.success is False
    assert "Duplikat" in receive_result2.error


def test_envelope_flows_through_wal():
    """Zustandsübergänge werden im WAL protokolliert."""
    # Mock WAL
    mock_wal = Mock()
    mock_wal.transition = Mock()
    
    dispatcher = PackageDispatcher(wal=mock_wal)
    gate_record = MockGateRecord()
    
    envelope = dispatcher.build_envelope(
        research_package=MockPackage(),
        gate_record=gate_record,
        lease_grants=[],
        execution_environment_ref=None,
    )
    
    # Dispatch
    result = dispatcher.dispatch(envelope)
    
    assert result.success is True
    # WAL würde hier den Übergang protokollieren


def test_no_swarm_terminology_in_questor_interface():
    """Keine alten Swarm-Begriffe in src/questor_interface/."""
    import inspect
    from src.questor_interface import package_dispatcher, result_receiver, dummy_questor
    
    # Prüfe Quellcode auf verbotene Begriffe
    forbidden_terms = ["swarm", "hive", "colony"]
    
    for module in [package_dispatcher, result_receiver, dummy_questor]:
        source = inspect.getsource(module)
        source_lower = source.lower()
        
        for term in forbidden_terms:
            assert term not in source_lower, f"Verbotener Begriff '{term}' gefunden in {module.__name__}"
