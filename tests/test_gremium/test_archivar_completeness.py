"""Tests for Archivar completeness handling."""

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
    status: ErgebnisStatus = ErgebnisStatus.ABGEBROCHEN,
    abbruch_grund: str | None = "INCOMPLETE",
    abbruch_klasse: AbbruchKlasse = AbbruchKlasse.SAFETY,
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


def test_incomplete_package_not_crystallized():
    """vollstaendig_flag=false → DRAFT_RECOVERABLE, kein Kristall."""
    archivar = Archivar()

    paket = _create_result_package(
        vollstaendig_flag=False,
        kristall_kandidaten=[{"value": 42}],  # Sollte ignoriert werden
    )
    result = archivar.process_result(paket)

    assert result.accepted is True
    assert result.status == "DRAFT_RECOVERABLE"

    # Keine Kristalle
    crystals = archivar.get_crystals()
    assert len(crystals) == 0


def test_complete_package_crystallized():
    """vollstaendig_flag=true → Kristall wird geschrieben."""
    archivar = Archivar()

    kristall_daten = {"wissenschaftlicher_wert": 42.0}
    paket = _create_result_package(
        vollstaendig_flag=True,
        kristall_kandidaten=[kristall_daten],
        abbruch_klasse=AbbruchKlasse.SAFETY,
        status=ErgebnisStatus.ABGEBROCHEN,
        abbruch_grund="test",
    )
    result = archivar.process_result(paket)

    assert result.accepted is True
    assert result.status == "CRYSTALLIZED"

    # Kristall muss existieren
    crystals = archivar.get_crystals()
    assert len(crystals) == 1
    assert crystals[0].kristall_daten == kristall_daten
