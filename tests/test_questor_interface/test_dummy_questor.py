"""Tests für DummyQuestor."""
import pytest

from src.questor_interface.dummy_questor import (
    DummyQuestor,
    OperationalCrashError,
    SafetyViolationError,
)
from src.contracts.questor_dispatch import QuestorDispatchEnvelope, LeaseGrant, SecurityMode, GateMode
from src.contracts.questor_result import AbbruchKlasse, AbbruchGrund


class MockPackage:
    """Mock ResearchPackage."""
    def __init__(self):
        self.package_id = "pkg-test"


class MockGateRecord:
    """Mock GateRecord."""
    def __init__(self):
        self.gate_record_id = "gate-test"
        self.gate_mode = GateMode.STRICT


def create_test_envelope():
    """Erstellt Test-Envelope."""
    return QuestorDispatchEnvelope(
        dispatch_id="dispatch-test",
        zyklus_id=1,
        attempt_id=1,
        package=MockPackage(),
        gate_record_ref="gate-test",
        gate_mode=GateMode.STRICT,
        lease_grants=[],
        security_mode=SecurityMode.PHYSICAL_ALLOWED,
        idempotency_key="pkg-test:1:1",
    )


def test_dummy_questor_receives_envelope():
    """Regel 6: DummyQuestor empfängt QuestorDispatchEnvelope."""
    questor = DummyQuestor()
    envelope = create_test_envelope()
    
    result = questor.execute(envelope)
    
    assert result is not None
    assert len(questor._executed_envelopes) == 1


def test_dummy_questor_returns_questor_ergebnis_paket():
    """Regel 6: DummyQuestor liefert questor_ergebnis_paket."""
    questor = DummyQuestor()
    envelope = create_test_envelope()
    
    result = questor.execute(envelope)
    
    assert result.paket_id is not None
    assert result.dispatch_ref == envelope.dispatch_id
    assert result.status == "erfolgreich"
    assert result.vollstaendig_flag is True


def test_dummy_questor_does_not_write_atlas():
    """Regel 6: DummyQuestor schreibt NICHT in Atlas."""
    questor = DummyQuestor()
    
    assert questor.does_not_write_atlas() is True


def test_dummy_questor_does_not_write_archiv():
    """Regel 6: DummyQuestor schreibt NICHT in Archiv."""
    questor = DummyQuestor()
    
    assert questor.does_not_write_archiv() is True


def test_dummy_questor_crash_simulation():
    """DummyQuestor simuliert OOM-Crash."""
    questor = DummyQuestor()
    envelope = create_test_envelope()
    
    with pytest.raises(OperationalCrashError) as exc_info:
        questor.execute_with_crash(envelope)
    
    assert "OOM" in str(exc_info.value)


def test_dummy_questor_estop_simulation():
    """DummyQuestor simuliert ESTOP."""
    questor = DummyQuestor()
    envelope = create_test_envelope()
    
    with pytest.raises(SafetyViolationError) as exc_info:
        questor.execute_with_estop(envelope)
    
    assert "Druckaufbau" in str(exc_info.value)
    assert "ESTOP" in str(exc_info.value)


def test_dummy_questor_loop_timeout():
    """DummyQuestor simuliert ROUTING_LOOP_TIMEOUT."""
    questor = DummyQuestor()
    envelope = create_test_envelope()
    
    result = questor.execute_with_loop_timeout(envelope)
    
    assert result.status == "abgebrochen"
    assert result.abbruch_grund == AbbruchGrund.ROUTING_LOOP_TIMEOUT
    assert result.vollstaendig_flag is True


def test_dummy_questor_early_abort_complete_result():
    """Regel 6: Früher Abbruch liefert vollständiges Ergebnis."""
    questor = DummyQuestor()
    envelope = create_test_envelope()
    
    result = questor.execute_with_loop_timeout(envelope)
    
    # Auch bei Abbruch muss das Ergebnis vollständig sein
    assert result.vollstaendig_flag is True
    assert result.questor_metadata is not None
    assert result.questor_metadata.questor_instance_id is not None
    assert result.questor_metadata.sequence_number >= 1


def test_dummy_questor_estop_is_safety():
    """ESTOP ist SAFETY, nicht OPERATIONAL."""
    questor = DummyQuestor()
    envelope = create_test_envelope()
    
    try:
        questor.execute_with_estop(envelope)
    except SafetyViolationError as e:
        result = questor.create_result_for_crash(envelope, e)
        
        assert result.abbruch_klasse == AbbruchKlasse.SAFETY
        assert result.abbruch_grund == AbbruchGrund.ESTOP


def test_dummy_questor_oom_is_operational():
    """OOM ist OPERATIONAL, nicht SAFETY."""
    questor = DummyQuestor()
    envelope = create_test_envelope()
    
    try:
        questor.execute_with_crash(envelope)
    except OperationalCrashError as e:
        result = questor.create_result_for_crash(envelope, e)
        
        assert result.abbruch_klasse == AbbruchKlasse.OPERATIONAL
        assert result.abbruch_grund == AbbruchGrund.OOM


def test_dummy_questor_loop_timeout_is_operational():
    """ROUTING_LOOP_TIMEOUT ist OPERATIONAL."""
    questor = DummyQuestor()
    envelope = create_test_envelope()
    
    result = questor.execute_with_loop_timeout(envelope)
    
    assert result.abbruch_klasse == AbbruchKlasse.OPERATIONAL
    assert result.abbruch_grund == AbbruchGrund.ROUTING_LOOP_TIMEOUT
