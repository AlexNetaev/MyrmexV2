"""State Machine implementations for MYRMEX v2.4.0 Stufen 5b, 6, 7, 8."""

from abc import ABC, abstractmethod
from typing import Any

from src.contracts.transaction_models import (
    Stage5bState,
    Stage6State,
    Stage7State,
    Stage8State,
)
from src.transaction.wal import WriteAheadLog


class StateMachine(ABC):
    """Abstract base class for state machines with WAL integration."""

    def __init__(self, wal: WriteAheadLog):
        self.wal = wal
        self.valid_transitions: dict[str, list[str]] = {}

    @abstractmethod
    def get_stage_name(self) -> str:
        """Return the stage name (e.g., 'STUFE_5B')."""
        pass

    def can_transition(self, from_state: str, to_state: str) -> bool:
        """Check if a transition is valid."""
        return to_state in self.valid_transitions.get(from_state, [])

    def transition(self, package_id: str, from_state: str, to_state: str,
                   payload: dict[str, Any] | None = None) -> str | None:
        """
        Perform a state transition with Two-Phase Commit.
        Returns entry_id on success, None if transition is invalid.
        """
        if not self.can_transition(from_state, to_state):
            return None

        # Phase 1: PREPARE
        entry_id = self.wal.prepare(
            package_id=package_id,
            stage=self.get_stage_name(),
            from_state=from_state,
            to_state=to_state,
            payload=payload or {},
        )

        try:
            # Phase 2: Apply state change and COMMIT
            self._apply_state_change(package_id, to_state, payload)
            self.wal.commit(entry_id)
            return entry_id
        except Exception:
            # PREPARE remains uncommitted → DRAFT_RECOVERABLE
            raise

    def _apply_state_change(self, package_id: str, to_state: str,
                            payload: dict[str, Any] | None = None):
        """Apply the actual state change. Override in subclasses if needed."""
        pass


class Stufe5bStateMachine(StateMachine):
    """State machine for Stufe 5b (Ideen-Erdung)."""

    def __init__(self, wal: WriteAheadLog):
        super().__init__(wal)
        self.valid_transitions = {
            Stage5bState.IDEE_OFFEN.value: [
                Stage5bState.IDEE_GEPRUEFT.value,
                Stage5bState.IDEE_VERWORFEN.value,
            ],
            Stage5bState.IDEE_GEPRUEFT.value: [Stage5bState.WEGMARKE_PLATZIERT.value],
            Stage5bState.IDEE_VERWORFEN.value: [],  # Endzustand
            Stage5bState.WEGMARKE_PLATZIERT.value: [],
        }

    def get_stage_name(self) -> str:
        return "STUFE_5B"


class Stufe6StateMachine(StateMachine):
    """State machine for Stufe 6 (Paket-Bau)."""

    def __init__(self, wal: WriteAheadLog):
        super().__init__(wal)
        self.valid_transitions = {
            Stage6State.WEGMARKE_RESERVIERT.value: [Stage6State.PAKET_ENTWURF.value],
            Stage6State.PAKET_ENTWURF.value: [Stage6State.LOCKED_GATE_PENDING.value],
            Stage6State.LOCKED_GATE_PENDING.value: [Stage6State.GATE_APPROVED.value],
            Stage6State.GATE_APPROVED.value: [Stage6State.LOCKED_READY_TO_EXEC.value],
            Stage6State.LOCKED_READY_TO_EXEC.value: [Stage6State.PAKET_FERTIG.value],
            Stage6State.PAKET_FERTIG.value: [],
        }

    def get_stage_name(self) -> str:
        return "STUFE_6"


class Stufe7StateMachine(StateMachine):
    """State machine for Stufe 7 (Sicherheits-Gate)."""

    def __init__(self, wal: WriteAheadLog):
        super().__init__(wal)
        self.valid_transitions = {
            Stage7State.GATE_PENDING.value: [
                Stage7State.RICHTER_PASS.value,
                Stage7State.SEHER_VETO.value,
            ],
            Stage7State.RICHTER_PASS.value: [Stage7State.SEHER_PASS.value],
            Stage7State.SEHER_PASS.value: [Stage7State.FREIGEGEBEN.value],
            Stage7State.SEHER_VETO.value: [Stage7State.DISPUTED.value],
            Stage7State.DISPUTED.value: [Stage7State.APPEAL_RESOLVED.value],
            Stage7State.APPEAL_RESOLVED.value: [Stage7State.FREIGEGEBEN.value],
            Stage7State.FREIGEGEBEN.value: [],
        }

    def get_stage_name(self) -> str:
        return "STUFE_7"


class Stufe8StateMachine(StateMachine):
    """State machine for Stufe 8 (Dispatch & Execution - Questor)."""

    def __init__(self, wal: WriteAheadLog):
        super().__init__(wal)
        self.valid_transitions = {
            Stage8State.RESOURCE_WAITING.value: [Stage8State.DISPATCHED.value],
            Stage8State.DISPATCHED.value: [Stage8State.EXECUTING.value],
            Stage8State.EXECUTING.value: [
                Stage8State.ABGESCHLOSSEN.value,
                Stage8State.ABORTED.value,
            ],
            Stage8State.ABGESCHLOSSEN.value: [],
            Stage8State.ABORTED.value: [],
        }

    def get_stage_name(self) -> str:
        return "STUFE_8"
