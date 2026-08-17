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


def test_idempotency_key_is_canonical():
    """Test Z-02: Key muss exakt package_id:zyklus_id:attempt_id sein, ohne Whitespace."""
    paket = QuestorErgebnisPaket(**_payload())
    assert paket.idempotency_key == "pkg-001:zyklus-014:2"


def test_idempotency_key_rejects_leading_zeros():
    """Test Z-02: attempt_id als '02' serialisiert ist ungültig und muss zu PACKAGE_INVALID führen."""
    payload = _payload(idempotency_key="pkg-001:zyklus-014:02")

    with pytest.raises(ValidationError):
        QuestorErgebnisPaket(**payload)


def test_idempotency_key_rejects_out_of_bounds_attempt():
    """Test Z-02: attempt_id > 999999 muss abgelehnt werden."""
    payload = _payload(attempt_id=1_000_000)

    with pytest.raises(ValidationError):
        QuestorErgebnisPaket(**payload)


def test_package_id_rejects_whitespace():
    """Test Z-02: package_id mit Whitespace ist ungültig."""
    payload = _payload(package_id="pkg 001")

    with pytest.raises(ValidationError):
        QuestorErgebnisPaket(**payload)


def test_zyklus_id_rejects_invalid_characters():
    """Test Z-02: zyklus_id mit Slash ist ungültig."""
    payload = _payload(zyklus_id="zyklus/014")

    with pytest.raises(ValidationError):
        QuestorErgebnisPaket(**payload)
