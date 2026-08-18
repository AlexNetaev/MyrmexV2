"""Tests for GateRecord and pipeline models."""

import pytest
from pydantic import ValidationError

from src.contracts.enums import GateMode
from src.contracts.pipeline_models import GateRecord, RohIdee, Wegmarke


def _gate_record(**overrides):
    data = {
        "gate_record_id": "gate-record-1",
        "gate_id": "gate-1",
        "package_id": "pkg-001",
        "zyklus_id": "zyklus-014",
        "gate_mode": GateMode.NORMAL,
        "timestamp": "2026-08-18T00:00:00Z",
    }
    data.update(overrides)
    return data


def test_gate_record_accepts_all_four_modes():
    """Test: GateRecord akzeptiert alle vier gate_mode-Werte."""
    modes = [
        GateMode.NORMAL,
        GateMode.FRACTURE_DIAGNOSIS,
        GateMode.HIGH_RISK_OVERRIDE,
        GateMode.SANDBOX,
    ]

    for mode in modes:
        gr = GateRecord(**_gate_record(gate_mode=mode))
        assert gr.gate_mode == mode


def test_gate_record_rejects_invalid_mode():
    """Test: GateRecord lehnt ungültige gate_mode-Werte ab."""
    # Pydantic will reject invalid enum values
    with pytest.raises(ValidationError):
        GateRecord(**_gate_record(gate_mode="INVALID_MODE"))


def test_gate_record_requires_gate_id():
    """Test: gate_id ist ein Pflichtfeld."""
    payload = _gate_record()
    del payload["gate_id"]

    with pytest.raises(ValidationError):
        GateRecord(**payload)


def test_gate_record_requires_package_id():
    """Test: package_id ist ein Pflichtfeld."""
    payload = _gate_record()
    del payload["package_id"]

    with pytest.raises(ValidationError):
        GateRecord(**payload)


def test_gate_record_requires_zyklus_id():
    """Test: zyklus_id ist ein Pflichtfeld."""
    payload = _gate_record()
    del payload["zyklus_id"]

    with pytest.raises(ValidationError):
        GateRecord(**payload)


def test_gate_record_defaults_to_normal_mode():
    """Test: gate_mode default ist NORMAL."""
    payload = {
        "gate_record_id": "gate-record-1",
        "gate_id": "gate-1",
        "package_id": "pkg-001",
        "zyklus_id": "zyklus-014",
        "timestamp": "2026-08-18T00:00:00Z",
    }
    gr = GateRecord(**payload)
    assert gr.gate_mode == GateMode.NORMAL


def test_wegmarke_creation():
    """Test: Wegmarke kann erstellt werden."""
    w = Wegmarke(
        wegmarke_id="wegmarke-1",
        name="Test Wegmarke",
        version="1.0.0",
    )

    assert w.wegmarke_id == "wegmarke-1"
    assert w.name == "Test Wegmarke"
    assert w.version == "1.0.0"


def test_wegmarke_requires_fields():
    """Test: Wegmarke erfordert Pflichtfelder."""
    with pytest.raises(ValidationError):
        Wegmarke(
            wegmarke_id="wegmarke-1",
            # missing name and version
        )


def test_roh_idee_creation():
    """Test: RohIdee kann erstellt werden."""
    idee = RohIdee(
        idee_id="idee-1",
        titel="Test Idee",
        beschreibung="Eine Test-Idee",
        atlas_version_ref="v1.0.0",
    )

    assert idee.idee_id == "idee-1"
    assert idee.titel == "Test Idee"
    assert idee.beschreibung == "Eine Test-Idee"


def test_roh_idee_prioritaet_bounds():
    """Test: prioritaet muss zwischen 0 und 10 sein."""
    with pytest.raises(ValidationError):
        RohIdee(
            idee_id="idee-1",
            titel="Test",
            beschreibung="Test",
            prioritaet=-1,
            atlas_version_ref="v1.0.0",
        )

    with pytest.raises(ValidationError):
        RohIdee(
            idee_id="idee-1",
            titel="Test",
            beschreibung="Test",
            prioritaet=11,
            atlas_version_ref="v1.0.0",
        )

    # Valid values
    idee_low = RohIdee(
        idee_id="idee-1",
        titel="Test",
        beschreibung="Test",
        prioritaet=0,
        atlas_version_ref="v1.0.0",
    )
    assert idee_low.prioritaet == 0

    idee_high = RohIdee(
        idee_id="idee-2",
        titel="Test",
        beschreibung="Test",
        prioritaet=10,
        atlas_version_ref="v1.0.0",
    )
    assert idee_high.prioritaet == 10
