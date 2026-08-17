"""Dummy Questor implementation for Phase 1 testing."""

import uuid
from datetime import datetime, timezone

from src.contracts.enums import AbbruchKlasse, ErgebnisStatus
from src.contracts.questor_dispatch import QuestorDispatchEnvelope
from src.contracts.questor_metadata import OperationalMetrics, QuestorMetadata
from src.contracts.questor_result import QuestorErgebnisPaket
from src.questor_interface import QuestorInterface


class DummyQuestor(QuestorInterface):
    """Dummy Questor implementation for Phase 1 testing."""

    def __init__(self) -> None:
        self._instance_id = f"dummy-questor-{uuid.uuid4().hex[:8]}"
        self._sequence_counter = 0

    def execute(self, dispatch: QuestorDispatchEnvelope) -> QuestorErgebnisPaket:
        """Execute a research package dispatch and return results (dummy)."""
        self._sequence_counter += 1

        now = datetime.now(timezone.utc).isoformat()

        return QuestorErgebnisPaket(
            package_id=dispatch.package.package_id,
            zyklus_id=dispatch.zyklus_id,
            attempt_id=dispatch.attempt_id,
            questor_instance_id=self._instance_id,
            sequence_number=self._sequence_counter,
            observed_atlas_version_id=dispatch.package.atlas_version_ref,
            status=ErgebnisStatus.ERFOLGREICH,
            abbruch_klasse=AbbruchKlasse.OPERATIONAL,
            vollstaendig_flag=True,
            rohdaten_checksumme=f"sha256-dummy-{uuid.uuid4().hex[:16]}",
            questor_metadata=QuestorMetadata(
                questor_version="0.2.3-dummy",
                operational_metrics=OperationalMetrics(),
            ),
        )
