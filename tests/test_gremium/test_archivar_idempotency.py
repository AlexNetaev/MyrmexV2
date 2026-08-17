"""Tests for Archivar idempotency (Regel 2)."""

import pytest

from src.contracts.enums import AbbruchKlasse, ErgebnisStatus
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
    kristall_kandidaten: list | None = None,
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
        kristall_kandidaten=kristall_kandidaten or [],
        ergebnis_daten={},
        validierung={},
        gefahren_beobachtet=[],
        signale_fuer_atlas=[],
        routing_checkpoint={},
    )


def test_duplicate_idempotency_key_is_rejected():
    """Regel 2: Zweites Paket mit gleichem idempotency_key wird verworfen."""
    archivar = Archivar()

    # Erstes Paket verarbeiten
    paket1 = _create_result_package(package_id="pkg-001", zyklus_id="zyklus-014", attempt_id=1)
    result1 = archivar.process_result(paket1)

    assert result1.accepted is True

    # Zweites Paket mit gleichem idempotency_key (selbes package_id, zyklus_id, attempt_id)
    paket2 = _create_result_package(package_id="pkg-001", zyklus_id="zyklus-014", attempt_id=1)
    result2 = archivar.process_result(paket2)

    assert result2.accepted is False
    assert result2.rejection_reason == "DUPLICATE_IDEMPOTENCY_KEY"


def test_duplicate_produces_no_second_crystal():
    """Regel 2: Duplikat erzeugt keinen zweiten Kristall."""
    archivar = Archivar()

    # Erstes Paket mit Kristall-Kandidaten (SAFETY class allows crystals)
    kristall_daten = {"wissenschaftlicher_wert": 42.0}
    paket1 = _create_result_package(
        package_id="pkg-002",
        zyklus_id="zyklus-015",
        attempt_id=1,
        questor_instance_id="questor-B",
        status=ErgebnisStatus.ABGEBROCHEN,
        abbruch_grund="test",
        kristall_kandidaten=[kristall_daten],
        abbruch_klasse=AbbruchKlasse.SAFETY,
    )
    result1 = archivar.process_result(paket1)

    assert result1.accepted is True
    crystals_after_first = len(archivar.get_crystals())
    assert crystals_after_first == 1

    # Duplikat verarbeiten
    paket2 = _create_result_package(
        package_id="pkg-002",
        zyklus_id="zyklus-015",
        attempt_id=1,
        questor_instance_id="questor-B",
        status=ErgebnisStatus.ABGEBROCHEN,
        abbruch_grund="test",
        kristall_kandidaten=[kristall_daten],
        abbruch_klasse=AbbruchKlasse.SAFETY,
    )
    result2 = archivar.process_result(paket2)

    assert result2.accepted is False

    # Es darf keinen zweiten Kristall geben
    crystals_after_second = len(archivar.get_crystals())
    assert crystals_after_second == crystals_after_first


def test_duplicate_produces_no_second_signal():
    """Regel 2: Duplikat erzeugt kein zweites Signal."""
    archivar = Archivar()

    # Erstes Paket mit Signal
    paket1 = _create_result_package(
        package_id="pkg-003",
        zyklus_id="zyklus-016",
        attempt_id=1,
        abbruch_klasse=AbbruchKlasse.SAFETY,
        status=ErgebnisStatus.FEHLGESCHLAGEN,
        abbruch_grund="Scientific failure",
    )
    result1 = archivar.process_result(paket1)

    assert result1.accepted is True
    signals_after_first = len(archivar.get_signals())
    assert signals_after_first >= 1

    # Duplikat verarbeiten
    paket2 = _create_result_package(
        package_id="pkg-003",
        zyklus_id="zyklus-016",
        attempt_id=1,
        abbruch_klasse=AbbruchKlasse.SAFETY,
        status=ErgebnisStatus.FEHLGESCHLAGEN,
        abbruch_grund="Scientific failure",
    )
    result2 = archivar.process_result(paket2)

    assert result2.accepted is False

    # Es darf kein zusätzliches Signal geben
    signals_after_second = len(archivar.get_signals())
    assert signals_after_second == signals_after_first
