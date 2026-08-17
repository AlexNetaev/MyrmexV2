"""Tests for Archivar metadata handling."""

import pytest

from src.contracts.enums import AbbruchKlasse, ErgebnisStatus
from src.contracts.questor_metadata import OperationalMetrics, QuestorMetadata
from src.contracts.questor_result import QuestorErgebnisPaket
from src.gremium.archivar import Archivar


def _create_result_package(
    package_id: str = "pkg-001",
    zyklus_id: str = "zyklus-014",
    attempt_id: int = 1,
    questor_instance_id: str = "questor-A",
    sequence_number: int = 1,
    status: ErgebnisStatus = ErgebnisStatus.ERFOLGREICH,
    abbruch_grund: str | None = None,
    abbruch_klasse: AbbruchKlasse = AbbruchKlasse.OPERATIONAL,
    vollstaendig_flag: bool = True,
    questor_metadata: QuestorMetadata | None = None,
) -> QuestorErgebnisPaket:
    """Helper to create a valid QuestorErgebnisPaket."""
    return QuestorErgebnisPaket(
        package_id=package_id,
        zyklus_id=zyklus_id,
        attempt_id=attempt_id,
        questor_instance_id=questor_instance_id,
        sequence_number=sequence_number,
        observed_atlas_version_id="atlas-1",
        status=status,
        abbruch_grund=abbruch_grund,
        abbruch_klasse=abbruch_klasse,
        vollstaendig_flag=vollstaendig_flag,
        rohdaten_checksumme="sha256:dummy",
        questor_metadata=questor_metadata,
    )


def test_questor_metadata_not_scientifically_interpreted():
    """questor_metadata erzeugt keine Kristalle oder Signale."""
    archivar = Archivar()

    # Metadata mit operational metrics (darf nicht wissenschaftlich interpretiert werden)
    metadata = QuestorMetadata(
        questor_version="0.2.3",
        operational_metrics=OperationalMetrics(
            oom_count=5,
            timeout_count=3,
            lease_wait_time_s=10.5,
        ),
    )

    paket = _create_result_package(
        abbruch_klasse=AbbruchKlasse.OPERATIONAL,
        status=ErgebnisStatus.ABGEBROCHEN,
        abbruch_grund="OOM",
        questor_metadata=metadata,
    )
    result = archivar.process_result(paket)

    assert result.accepted is True

    # Metadata darf keine Kristalle erzeugen
    crystals = archivar.get_crystals()
    assert len(crystals) == 0

    # Metadata darf keine wissenschaftlichen Signale erzeugen
    from src.contracts.enums import SignalType

    scientific_signals = [
        s for s in archivar.get_signals() if s.signal_type == SignalType.SCIENTIFIC
    ]
    assert len(scientific_signals) == 0


def test_operational_metrics_go_to_operational_log():
    """operational_metrics aus questor_metadata gehen in operational_event_log."""
    archivar = Archivar()

    metadata = QuestorMetadata(
        questor_version="0.2.3",
        operational_metrics=OperationalMetrics(
            oom_count=5,
            timeout_count=3,
            lease_wait_time_s=10.5,
            capability_retry_count=2,
        ),
    )

    paket = _create_result_package(
        abbruch_klasse=AbbruchKlasse.OPERATIONAL,
        status=ErgebnisStatus.ABGEBROCHEN,
        abbruch_grund="TIMEOUT",
        questor_metadata=metadata,
    )
    result = archivar.process_result(paket)

    assert result.accepted is True

    # Operational events müssen die Metrics enthalten
    operational_events = archivar.get_operational_events()
    assert len(operational_events) >= 1

    event = operational_events[0]
    assert event.event_data.get("oom_count") == 5
    assert event.event_data.get("timeout_count") == 3
    assert event.event_data.get("lease_wait_time_s") == 10.5
