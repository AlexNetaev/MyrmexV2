"""Tests for QuestorErgebnisPaket contract."""

import pytest
from pydantic import ValidationError

from src.contracts.enums import AbbruchKlasse, ErgebnisStatus
from src.contracts.questor_result import QuestorErgebnisPaket


def _payload(**overrides):
    data = {
        "package_id": "pkg-001",
        "zyklus_id": "zyklus-014",
        "attempt_id": 2,
        "questor_instance_id": "questor-test",
        "sequence_number": 1,
        "observed_atlas_version_id": "atlas-1",
        "status": ErgebnisStatus.ABGEBROCHEN,
        "abbruch_grund": "PACKAGE_INVALID",
        "abbruch_klasse": AbbruchKlasse.OPERATIONAL,
        "vollstaendig_flag": True,
        "rohdaten_checksumme": "sha256:dummy",
    }
    data.update(overrides)
    return data


def test_questor_result_idempotency_auto_computed():
    """Test: idempotency_key wird automatisch aus package_id:zyklus_id:attempt_id berechnet."""
    paket = QuestorErgebnisPaket(**_payload())
    assert paket.idempotency_key == "pkg-001:zyklus-014:2"


def test_questor_result_rejects_invalid_abbruch_klasse():
    """Test: Bei ERFOLGREICH muss abbruch_klasse OPERATIONAL sein."""
    payload = _payload(
        status=ErgebnisStatus.ERFOLGREICH,
        abbruch_grund=None,
        abbruch_klasse=AbbruchKlasse.SAFETY,
    )

    with pytest.raises(ValidationError) as exc_info:
        QuestorErgebnisPaket(**payload)

    assert "PACKAGE_INVALID" in str(exc_info.value)


def test_questor_result_requires_questor_instance_id():
    """Test: questor_instance_id ist ein Pflichtfeld."""
    payload = _payload()
    del payload["questor_instance_id"]

    with pytest.raises(ValidationError):
        QuestorErgebnisPaket(**payload)


def test_questor_result_sequence_number_is_int():
    """Test: sequence_number muss eine ganze Zahl >= 0 sein."""
    payload = _payload(sequence_number=-1)

    with pytest.raises(ValidationError):
        QuestorErgebnisPaket(**payload)

    # Test with float (should fail due to strict int requirement if applicable)
    payload = _payload(sequence_number=1.5)
    with pytest.raises(ValidationError):
        QuestorErgebnisPaket(**payload)


def test_questor_result_erfolgreich_requires_no_abbruch_grund():
    """Test: Bei ERFOLGREICH darf abbruch_grund None sein."""
    payload = _payload(
        status=ErgebnisStatus.ERFOLGREICH,
        abbruch_grund="some_reason",
        abbruch_klasse=AbbruchKlasse.OPERATIONAL,
    )

    with pytest.raises(ValidationError) as exc_info:
        QuestorErgebnisPaket(**payload)

    assert "PACKAGE_INVALID" in str(exc_info.value)


def test_questor_result_abgebrochen_requires_abbruch_grund():
    """Test: Bei ABGEBROCHEN muss abbruch_grund gesetzt sein."""
    payload = _payload(
        status=ErgebnisStatus.ABGEBROCHEN,
        abbruch_grund=None,
    )

    with pytest.raises(ValidationError) as exc_info:
        QuestorErgebnisPaket(**payload)

    assert "PACKAGE_INVALID" in str(exc_info.value)


def test_questor_result_vollstaendig_flag_required():
    """Test: vollstaendig_flag ist ein Pflichtfeld."""
    payload = _payload()
    del payload["vollstaendig_flag"]

    with pytest.raises(ValidationError):
        QuestorErgebnisPaket(**payload)


def test_questor_result_rohdaten_checksumme_required():
    """Test: rohdaten_checksumme ist ein Pflichtfeld mit min_length=1."""
    payload = _payload(rohdaten_checksumme="")

    with pytest.raises(ValidationError):
        QuestorErgebnisPaket(**payload)
