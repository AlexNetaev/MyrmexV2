from src.contracts.enums import (
    ErrorClass,
    EstopOrigin,
    EstopStateName,
    HALCommandResultStatus,
)
from src.contracts.hal_models import HALCommand
from src.hal.dummy_hal import DummyHal


def test_dummy_hal_manifest_is_complete():
    """HAL-Test H-01 Vorbereitungsstufe: Manifest enthält Slots, Zonen und Capabilities."""
    hal = DummyHal()
    manifest = hal.get_environment_manifest()

    assert manifest.slots
    assert manifest.mutex_zones
    assert manifest.capabilities
    assert manifest.estop_mechanism
    assert manifest.supported_security_modes
    assert manifest.supported_resource_classes


def test_dummy_hal_execute_command_defaults_to_denied():
    """HAL-Test H-02/H-03 Vorbereitungsstufe: Dummy-HAL führt ohne Logik nicht aus."""
    hal = DummyHal()

    command = HALCommand(
        command_id="cmd-1",
        idempotency_key="cmd-1:lease-1:slot-1",
        lease_ref="lease-1",
        slot_id="slot-1",
        capability="dummy",
        operation="noop",
        timeout_s=1.0,
    )

    result = hal.execute_command(command)

    assert result.status == HALCommandResultStatus.DENIED
    assert result.error_class == ErrorClass.OPERATIONAL
    assert result.slot_state.slot_id == command.slot_id


def test_dummy_hal_report_estop_returns_active_software_estop():
    """HAL-Test H-07 Vorbereitungsstufe: report_estop liefert ACTIVE mit SOFTWARE-Origin."""
    hal = DummyHal()

    state = hal.report_estop(reason="test", trigger_source="pytest")

    assert state.state == EstopStateName.ACTIVE
    assert state.origin == EstopOrigin.SOFTWARE
    assert state.reset_policy == "MANUAL"
