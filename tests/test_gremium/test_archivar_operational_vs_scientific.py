"""Tests for Archivar Operational vs Scientific separation (Regel 1)."""

import pytest

from src.contracts.enums import AbbruchKlasse, ErgebnisStatus, EventType, SignalType
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
    )


def test_operational_abort_produces_no_scientific_signal():
    """Regel 1: OPERATIONAL-Abbruch (z.B. OOM) erzeugt KEIN wissenschaftliches Signal."""
    archivar = Archivar()

    paket = _create_result_package(
        status=ErgebnisStatus.ABGEBROCHEN,
        abbruch_grund="OOM",
        abbruch_klasse=AbbruchKlasse.OPERATIONAL,
    )
    result = archivar.process_result(paket)

    assert result.accepted is True

    # Keine wissenschaftlichen Signale
    scientific_signals = [
        s for s in archivar.get_signals() if s.signal_type == SignalType.SCIENTIFIC
    ]
    assert len(scientific_signals) == 0


def test_operational_abort_writes_to_operational_log():
    """Regel 1: OPERATIONAL-Abbruch schreibt in operational_event_log."""
    archivar = Archivar()

    paket = _create_result_package(
        status=ErgebnisStatus.ABGEBROCHEN,
        abbruch_grund="TIMEOUT",
        abbruch_klasse=AbbruchKlasse.OPERATIONAL,
    )
    result = archivar.process_result(paket)

    assert result.accepted is True

    # Muss im operational log sein
    operational_events = archivar.get_operational_events()
    assert len(operational_events) >= 1

    event = operational_events[0]
    assert event.event_type == EventType.OPERATIONAL_EVENT
    assert event.abbruch_grund == "TIMEOUT"


def test_operational_abort_produces_no_crystal():
    """Regel 1: OPERATIONAL-Abbruch erzeugt keinen Kristall."""
    archivar = Archivar()

    paket = _create_result_package(
        status=ErgebnisStatus.ABGEBROCHEN,
        abbruch_grund="LEASE_DENIED",
        abbruch_klasse=AbbruchKlasse.OPERATIONAL,
        kristall_kandidaten=[{"value": 42}],  # Sollte ignoriert werden
    )
    result = archivar.process_result(paket)

    assert result.accepted is True

    # Keine Kristalle
    crystals = archivar.get_crystals()
    assert len(crystals) == 0


def test_scientific_failure_produces_signal():
    """SCIENTIFIC-Fehlschlag erzeugt ein Atlas-Signal."""
    archivar = Archivar()

    paket = _create_result_package(
        status=ErgebnisStatus.FEHLGESCHLAGEN,
        abbruch_grund="Hypothesis refuted",
        abbruch_klasse=AbbruchKlasse.SCIENTIFIC,
    )
    result = archivar.process_result(paket)

    assert result.accepted is True

    # Muss wissenschaftliches Signal erzeugen
    signals = archivar.get_signals()
    scientific_signals = [
        s for s in signals if s.signal_type == SignalType.SCIENTIFIC
    ]
    assert len(scientific_signals) >= 1


def test_safety_abort_triggers_safety_signal():
    """SAFETY-Abbruch erzeugt ein Sicherheits-Signal."""
    archivar = Archivar()

    paket = _create_result_package(
        status=ErgebnisStatus.ABGEBROCHEN,
        abbruch_grund="Safety threshold exceeded",
        abbruch_klasse=AbbruchKlasse.SAFETY,
    )
    result = archivar.process_result(paket)

    assert result.accepted is True

    # Muss Safety-Signal erzeugen
    signals = archivar.get_signals()
    safety_signals = [s for s in signals if s.signal_type == SignalType.SAFETY]
    assert len(safety_signals) >= 1
