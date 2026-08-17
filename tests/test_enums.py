"""Tests for enum definitions."""

import pytest

from src.contracts.enums import (
    AbbruchKlasse,
    DispatchMode,
    ErgebnisStatus,
    GateMode,
    LockPolicy,
    ProcessLifecycleState,
    ProcessMode,
    RedactionLevel,
    ReleaseAuthority,
    RequestSource,
    ResourceClass,
    RetentionClass,
    SecurityMode,
    SlotStatus,
    ZoneStatus,
)


class TestErgebnisStatus:
    """Test ErgebnisStatus enum."""

    def test_erfolgreich_value(self):
        assert ErgebnisStatus.ERFOLGREICH.value == "erfolgreich"

    def test_fehlgeschlagen_value(self):
        assert ErgebnisStatus.FEHLGESCHLAGEN.value == "fehlgeschlagen"

    def test_abgebrochen_value(self):
        assert ErgebnisStatus.ABGEBROCHEN.value == "abgebrochen"


class TestAbbruchKlasse:
    """Test AbbruchKlasse enum."""

    def test_operational_value(self):
        assert AbbruchKlasse.OPERATIONAL.value == "OPERATIONAL"

    def test_scientific_value(self):
        assert AbbruchKlasse.SCIENTIFIC.value == "SCIENTIFIC"

    def test_safety_value(self):
        assert AbbruchKlasse.SAFETY.value == "SAFETY"


class TestSecurityMode:
    """Test SecurityMode enum."""

    def test_normal_value(self):
        assert SecurityMode.NORMAL.value == "NORMAL"

    def test_sandbox_value(self):
        assert SecurityMode.SANDBOX.value == "SANDBOX"


class TestResourceClass:
    """Test ResourceClass enum."""

    def test_lab_actuator_value(self):
        assert ResourceClass.LAB_ACTUATOR.value == "LAB_ACTUATOR"

    def test_compute_node_value(self):
        assert ResourceClass.COMPUTE_NODE.value == "COMPUTE_NODE"


class TestSlotStatus:
    """Test SlotStatus enum."""

    def test_free_value(self):
        assert SlotStatus.FREE.value == "FREE"

    def test_reserved_value(self):
        assert SlotStatus.RESERVED.value == "RESERVED"


class TestZoneStatus:
    """Test ZoneStatus enum."""

    def test_free_value(self):
        assert ZoneStatus.FREE.value == "FREE"

    def test_locked_value(self):
        assert ZoneStatus.LOCKED.value == "LOCKED"
