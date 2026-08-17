"""Tests for Archivar sequence monotonicity (Regel 3)."""

import pytest

from src.contracts.enums import AbbruchKlasse, ErgebnisStatus
from src.contracts.questor_result import QuestorErgebnisPaket
from src.gremium.archivar import Archivar


def _create_result_package(
    package_id: str,
    zyklus_id: str,
    attempt_id: int,
    questor_instance_id: str,
    sequence_number: int,
) -> QuestorErgebnisPaket:
    """Helper to create a valid QuestorErgebnisPaket."""
    return QuestorErgebnisPaket(
        package_id=package_id,
        zyklus_id=zyklus_id,
        attempt_id=attempt_id,
        questor_instance_id=questor_instance_id,
        sequence_number=sequence_number,
        observed_atlas_version_id="atlas-1",
        status=ErgebnisStatus.ERFOLGREICH,
        abbruch_klasse=AbbruchKlasse.OPERATIONAL,
        vollstaendig_flag=True,
        rohdaten_checksumme="sha256:dummy",
    )


def test_monotonic_sequence_accepted():
    """Regel 3: Steigende sequence_number wird akzeptiert."""
    archivar = Archivar()

    # Sequenz 1, 2, 3 für questor-A
    paket1 = _create_result_package("pkg-001", "zyklus-001", 1, "questor-A", 1)
    result1 = archivar.process_result(paket1)
    assert result1.accepted is True

    paket2 = _create_result_package("pkg-002", "zyklus-002", 1, "questor-A", 2)
    result2 = archivar.process_result(paket2)
    assert result2.accepted is True

    paket3 = _create_result_package("pkg-003", "zyklus-003", 1, "questor-A", 3)
    result3 = archivar.process_result(paket3)
    assert result3.accepted is True


def test_duplicate_sequence_rejected():
    """Regel 3: Gleiche sequence_number wird verworfen."""
    archivar = Archivar()

    # Erstes Paket mit sequence_number=1
    paket1 = _create_result_package("pkg-001", "zyklus-001", 1, "questor-A", 1)
    result1 = archivar.process_result(paket1)
    assert result1.accepted is True

    # Zweites Paket mit gleicher sequence_number=1 (anderes package_id)
    paket2 = _create_result_package("pkg-002", "zyklus-002", 1, "questor-A", 1)
    result2 = archivar.process_result(paket2)

    assert result2.accepted is False
    assert result2.rejection_reason == "SEQUENCE_NOT_MONOTONIC"


def test_lower_sequence_rejected():
    """Regel 3: Niedrigere sequence_number wird verworfen."""
    archivar = Archivar()

    # Erstes Paket mit sequence_number=5
    paket1 = _create_result_package("pkg-001", "zyklus-001", 1, "questor-A", 5)
    result1 = archivar.process_result(paket1)
    assert result1.accepted is True

    # Zweites Paket mit niedrigerer sequence_number=3
    paket2 = _create_result_package("pkg-002", "zyklus-002", 1, "questor-A", 3)
    result2 = archivar.process_result(paket2)

    assert result2.accepted is False
    assert result2.rejection_reason == "SEQUENCE_NOT_MONOTONIC"


def test_sequence_is_per_questor_instance():
    """Regel 3: Zwei verschiedene questor_instance_id dürfen dieselbe sequence_number haben."""
    archivar = Archivar()

    # questor-A mit sequence_number=1
    paket_a1 = _create_result_package("pkg-001", "zyklus-001", 1, "questor-A", 1)
    result_a1 = archivar.process_result(paket_a1)
    assert result_a1.accepted is True

    # questor-B mit gleicher sequence_number=1 (muss akzeptiert werden)
    paket_b1 = _create_result_package("pkg-002", "zyklus-002", 1, "questor-B", 1)
    result_b1 = archivar.process_result(paket_b1)
    assert result_b1.accepted is True

    # questor-A mit sequence_number=2 (muss akzeptiert werden)
    paket_a2 = _create_result_package("pkg-003", "zyklus-003", 1, "questor-A", 2)
    result_a2 = archivar.process_result(paket_a2)
    assert result_a2.accepted is True

    # questor-B mit sequence_number=2 (muss akzeptiert werden)
    paket_b2 = _create_result_package("pkg-004", "zyklus-004", 1, "questor-B", 2)
    result_b2 = archivar.process_result(paket_b2)
    assert result_b2.accepted is True
