"""Tests for State Machine implementations."""

import pytest
from pathlib import Path

from src.transaction.wal import WriteAheadLog
from src.transaction.state_machine import (
    Stufe5bStateMachine,
    Stufe6StateMachine,
    Stufe7StateMachine,
    Stufe8StateMachine,
)
from src.contracts.transaction_models import (
    Stage5bState,
    Stage6State,
    Stage7State,
    Stage8State,
)


@pytest.fixture
def wal_path(tmp_path):
    return tmp_path / "test_wal.jsonl"


@pytest.fixture
def wal(wal_path):
    return WriteAheadLog(wal_path)


def test_stufe6_valid_transition_path(wal):
    """Stufe 6: WEGMARKE_RESERVIERT → ... → PAKET_FERTIG ist gültig."""
    sm = Stufe6StateMachine(wal)
    
    path = [
        (Stage6State.WEGMARKE_RESERVIERT.value, Stage6State.PAKET_ENTWURF.value),
        (Stage6State.PAKET_ENTWURF.value, Stage6State.LOCKED_GATE_PENDING.value),
        (Stage6State.LOCKED_GATE_PENDING.value, Stage6State.GATE_APPROVED.value),
        (Stage6State.GATE_APPROVED.value, Stage6State.LOCKED_READY_TO_EXEC.value),
        (Stage6State.LOCKED_READY_TO_EXEC.value, Stage6State.PAKET_FERTIG.value),
    ]
    
    current_state = Stage6State.WEGMARKE_RESERVIERT.value
    for from_state, to_state in path:
        assert current_state == from_state
        assert sm.can_transition(from_state, to_state) is True
        entry_id = sm.transition("pkg-001", from_state, to_state)
        assert entry_id is not None
        current_state = to_state


def test_stufe6_invalid_transition_rejected(wal):
    """Stufe 6: WEGMARKE_RESERVIERT → PAKET_FERTIG ist UNGÜLTIG (überspringt Stufen)."""
    sm = Stufe6StateMachine(wal)
    
    # Try to skip all intermediate states
    result = sm.can_transition(
        Stage6State.WEGMARKE_RESERVIERT.value,
        Stage6State.PAKET_FERTIG.value,
    )
    assert result is False
    
    # Try to transition - should return None
    entry_id = sm.transition(
        "pkg-001",
        Stage6State.WEGMARKE_RESERVIERT.value,
        Stage6State.PAKET_FERTIG.value,
    )
    assert entry_id is None


def test_stufe7_valid_transition_path(wal):
    """Stufe 7: GATE_PENDING → RICHTER_PASS → SEHER_PASS → FREIGEGEBEN ist gültig."""
    sm = Stufe7StateMachine(wal)
    
    path = [
        (Stage7State.GATE_PENDING.value, Stage7State.RICHTER_PASS.value),
        (Stage7State.RICHTER_PASS.value, Stage7State.SEHER_PASS.value),
        (Stage7State.SEHER_PASS.value, Stage7State.FREIGEGEBEN.value),
    ]
    
    current_state = Stage7State.GATE_PENDING.value
    for from_state, to_state in path:
        assert sm.can_transition(from_state, to_state) is True
        entry_id = sm.transition("pkg-001", from_state, to_state)
        assert entry_id is not None
        current_state = to_state


def test_stufe7_veto_path(wal):
    """Stufe 7: SEHER_VETO → DISPUTED → APPEAL_RESOLVED ist gültig."""
    sm = Stufe7StateMachine(wal)
    
    # First go through normal path to SEHER_VETO
    sm.transition("pkg-001", Stage7State.GATE_PENDING.value, Stage7State.SEHER_VETO.value)
    sm.transition("pkg-001", Stage7State.SEHER_VETO.value, Stage7State.DISPUTED.value)
    
    # Then through appeal
    assert sm.can_transition(Stage7State.DISPUTED.value, Stage7State.APPEAL_RESOLVED.value) is True
    entry_id = sm.transition("pkg-001", Stage7State.DISPUTED.value, Stage7State.APPEAL_RESOLVED.value)
    assert entry_id is not None


def test_stufe8_questor_dispatch_path(wal):
    """Stufe 8: RESOURCE_WAITING → DISPATCHED → EXECUTING → ABGESCHLOSSEN ist gültig."""
    sm = Stufe8StateMachine(wal)
    
    path = [
        (Stage8State.RESOURCE_WAITING.value, Stage8State.DISPATCHED.value),
        (Stage8State.DISPATCHED.value, Stage8State.EXECUTING.value),
        (Stage8State.EXECUTING.value, Stage8State.ABGESCHLOSSEN.value),
    ]
    
    for from_state, to_state in path:
        assert sm.can_transition(from_state, to_state) is True
        entry_id = sm.transition("pkg-001", from_state, to_state)
        assert entry_id is not None


def test_transition_writes_to_wal(wal, wal_path):
    """Jeder Zustandsübergang schreibt einen WAL-Eintrag."""
    sm = Stufe6StateMachine(wal)
    
    initial_entries = len(wal.read_all()) + len(wal.read_uncommitted())
    
    sm.transition("pkg-001", Stage6State.WEGMARKE_RESERVIERT.value, Stage6State.PAKET_ENTWURF.value)
    
    final_entries = len(wal.read_all()) + len(wal.read_uncommitted())
    assert final_entries > initial_entries


def test_transition_is_two_phase(wal):
    """Regel 5: Übergang nutzt prepare() und commit()."""
    sm = Stufe6StateMachine(wal)
    
    # Before transition: no entries
    assert len(wal.read_uncommitted()) == 0
    assert len(wal.read_all()) == 0
    
    # Transition
    entry_id = sm.transition("pkg-001", Stage6State.WEGMARKE_RESERVIERT.value, Stage6State.PAKET_ENTWURF.value)
    
    # After successful transition: entry should be committed
    assert wal.is_entry_committed(entry_id) is True
    assert len(wal.read_uncommitted()) == 0
    assert len(wal.read_all()) == 1


def test_stufe5b_valid_path(wal):
    """Stufe 5b: IDEE_OFFEN → IDEE_GEPRUEFT → WEGMARKE_PLATZIERT ist gültig."""
    sm = Stufe5bStateMachine(wal)
    
    assert sm.can_transition(Stage5bState.IDEE_OFFEN.value, Stage5bState.IDEE_GEPRUEFT.value) is True
    assert sm.can_transition(Stage5bState.IDEE_GEPRUEFT.value, Stage5bState.WEGMARKE_PLATZIERT.value) is True


def test_invalid_state_transition_rejected(wal):
    """Invalid transitions are rejected across all state machines."""
    sm6 = Stufe6StateMachine(wal)
    sm7 = Stufe7StateMachine(wal)
    sm8 = Stufe8StateMachine(wal)
    
    # Try invalid backward transition
    assert sm6.can_transition(Stage6State.PAKET_FERTIG.value, Stage6State.WEGMARKE_RESERVIERT.value) is False
    
    # Try skipping stages in Stufe 7
    assert sm7.can_transition(Stage7State.GATE_PENDING.value, Stage7State.FREIGEGEBEN.value) is False
    
    # Try going back in Stufe 8
    assert sm8.can_transition(Stage8State.ABGESCHLOSSEN.value, Stage8State.EXECUTING.value) is False
