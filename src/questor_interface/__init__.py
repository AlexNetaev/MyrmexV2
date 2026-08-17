"""Questor interface package for MYRMEX v2.4.0."""

from typing import Protocol, runtime_checkable

from src.contracts.questor_dispatch import QuestorDispatchEnvelope
from src.contracts.questor_result import QuestorErgebnisPaket


@runtime_checkable
class QuestorInterface(Protocol):
    """Questor interface for MYRMEX v2.4.0 / Questor v0.2.3."""

    def execute(self, dispatch: QuestorDispatchEnvelope) -> QuestorErgebnisPaket:
        """Execute a research package dispatch and return results."""
        ...
