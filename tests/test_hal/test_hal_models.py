from src.contracts.enums import (
    EstopOrigin,
    EstopStateName,
    LockPolicy,
    ProcessMode,
    ResourceClass,
    SlotStatus,
)
from src.contracts.hal_models import (
    EnvironmentManifest,
    EstopState,
    HALCommand,
    MutexZone,
    ProcessCommand,
    SlotDescriptor,
    SlotState,
)


def test_slot_state_supports_interlocked():
    """HAL v0.2.0: SlotState muss den Zustand INTERLOCKED unterstützen."""
    state = SlotState(
        slot_id="slot-1",
        status=SlotStatus.INTERLOCKED,
    )

    assert state.status == SlotStatus.INTERLOCKED
    assert state.interlock_latched is False
    assert state.safe_state_verified is False


def test_estop_state_has_origin():
    """HAL v0.2.0: EstopState muss einen expliziten origin besitzen."""
    state = EstopState(
        state=EstopStateName.ACTIVE,
        origin=EstopOrigin.HARDWARE_INTERLOCK,
        reset_policy="MANUAL",
    )

    assert state.origin == EstopOrigin.HARDWARE_INTERLOCK
    assert state.physical_reset_required is False


def test_environment_manifest_accepts_minimal_dummy():
    """HAL v0.2.0: EnvironmentManifest muss Slots, Zonen und ESTOP-Mechanik aufnehmen."""
    manifest = EnvironmentManifest(
        environment_id="env-1",
        environment_version="1",
        schema_version="hal-0.2.0",
        slots=[
            SlotDescriptor(
                slot_id="slot-1",
                resource_class=ResourceClass.SANDBOX_ENVIRONMENT,
            ),
        ],
        mutex_zones=[
            MutexZone(
                zone_id="zone-1",
                lock_policy=LockPolicy.EXCLUSIVE,
            ),
        ],
        capabilities=["dummy"],
        estop_mechanism="software",
        max_command_timeout_s=1.0,
        default_lease_ttl_s=1.0,
        heartbeat_interval_s=1.0,
    )

    assert manifest.slots[0].slot_id == "slot-1"
    assert manifest.mutex_zones[0].zone_id == "zone-1"
    assert manifest.capabilities == ["dummy"]


def test_hal_command_and_process_command_are_distinct():
    """HAL v0.2.0: HALCommand und ProcessCommand sind strikt getrennte Modelle."""
    command = HALCommand(
        command_id="cmd-1",
        idempotency_key="cmd-1:lease-1:slot-1",
        lease_ref="lease-1",
        slot_id="slot-1",
        capability="dummy",
        operation="noop",
        timeout_s=1.0,
    )

    process = ProcessCommand(
        process_id="proc-1",
        lease_ref="lease-1",
        slot_id="slot-1",
        capability="dummy",
        operation="noop",
        process_mode=ProcessMode.START,
        timeout_s=1.0,
    )

    assert command.command_id == "cmd-1"
    assert process.process_id == "proc-1"
    assert not isinstance(command, ProcessCommand)
    assert not isinstance(process, HALCommand)
