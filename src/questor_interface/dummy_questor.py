"""Dummy Questor implementation for Phase 1 testing."""

from src.contracts.enums import AbbruchKlasse, ErgebnisStatus
from src.contracts.questor_dispatch import QuestorDispatchEnvelope
from src.contracts.questor_result import QuestorErgebnisPaket


def execute(envelope: QuestorDispatchEnvelope) -> QuestorErgebnisPaket:
    return QuestorErgebnisPaket(
        package_id=envelope.package.package_id,
        zyklus_id=envelope.zyklus_id,
        attempt_id=envelope.attempt_id,
        questor_instance_id="dummy-questor",
        sequence_number=0,
        observed_atlas_version_id=envelope.package.atlas_version_ref,
        status=ErgebnisStatus.ABGEBROCHEN,
        abbruch_grund="PACKAGE_INVALID",
        abbruch_klasse=AbbruchKlasse.OPERATIONAL,
        vollstaendig_flag=True,
        rohdaten_checksumme="unset",
    )
