"""Tests for Atlas Store - Event-Sourcing with snapshots."""

from datetime import datetime, timezone

from src.atlas.atlas_store import AtlasStore
from src.contracts.atlas_models import OperationalEvent, SignalEvent
from src.contracts.enums import EventType, SignalSeverity, SignalType


def test_atlas_store_append_operational_event():
    """AtlasStore: Operational events are appended correctly."""
    store = AtlasStore()

    event = OperationalEvent(
        event_id="evt-001",
        event_type=EventType.OPERATIONAL_EVENT,
        source_package_id="pkg-001",
        timestamp=datetime.now(timezone.utc).isoformat(),
        event_data={"reason": "test"},
    )

    store.append_operational_event(event)

    events = store.get_all_events()
    assert len(events) == 1
    assert events[0]["event_type"] == EventType.OPERATIONAL_EVENT.value


def test_atlas_store_append_scientific_signal():
    """AtlasStore: Scientific signals are appended correctly."""
    store = AtlasStore()

    signal = SignalEvent(
        signal_id="sig-001",
        signal_type=SignalType.SCIENTIFIC,
        source_package_id="pkg-001",
        timestamp=datetime.now(timezone.utc).isoformat(),
        severity=SignalSeverity.PURPLE,
    )

    store.append_scientific_signal(signal)

    events = store.get_all_events()
    assert len(events) == 1
    assert events[0]["event_type"] == EventType.SCIENTIFIC_SIGNAL.value


def test_atlas_store_append_safety_signal():
    """AtlasStore: Safety signals are appended correctly."""
    store = AtlasStore()

    signal = SignalEvent(
        signal_id="sig-001",
        signal_type=SignalType.SAFETY,
        source_package_id="pkg-001",
        timestamp=datetime.now(timezone.utc).isoformat(),
        severity=SignalSeverity.RED,
    )

    store.append_safety_signal(signal)

    events = store.get_all_events()
    assert len(events) == 1
    assert events[0]["event_type"] == EventType.SAFETY_SIGNAL.value


def test_atlas_store_create_snapshot():
    """AtlasStore: Snapshots are created with correct checksum."""
    store = AtlasStore()

    # Add some events
    event = OperationalEvent(
        event_id="evt-001",
        event_type=EventType.OPERATIONAL_EVENT,
        timestamp=datetime.now(timezone.utc).isoformat(),
        event_data={},
    )
    store.append_operational_event(event)

    # Create snapshot
    snapshot = store.create_snapshot()

    assert snapshot.snapshot_id == "snapshot-1"
    assert snapshot.total_events >= 1  # Includes snapshot event
    assert len(snapshot.checksum) == 64  # SHA256 hex


def test_atlas_store_head_pointer_updates():
    """AtlasStore: Head pointer updates on each append."""
    store = AtlasStore()

    initial_pointer = store.get_head_pointer()
    assert initial_pointer == "initial"

    event = OperationalEvent(
        event_id="evt-001",
        event_type=EventType.OPERATIONAL_EVENT,
        timestamp=datetime.now(timezone.utc).isoformat(),
        event_data={},
    )
    store.append_operational_event(event)

    new_pointer = store.get_head_pointer()
    assert new_pointer != initial_pointer
    assert "evt-001" in new_pointer


def test_atlas_store_get_latest_snapshot():
    """AtlasStore: get_latest_snapshot returns most recent snapshot."""
    store = AtlasStore()

    # First snapshot
    store.create_snapshot()

    # Second snapshot
    store.create_snapshot()

    latest = store.get_latest_snapshot()
    assert latest is not None
    assert latest.snapshot_id == "snapshot-2"


def test_atlas_store_recover_from_snapshot():
    """AtlasStore: recover_from_snapshot updates head pointer."""
    store = AtlasStore()

    snapshot = store.create_snapshot()
    original_pointer = snapshot.atlas_head_pointer

    # Modify pointer
    store._atlas_head_pointer = "modified"

    # Recover
    store.recover_from_snapshot(snapshot)

    assert store.get_head_pointer() == original_pointer


def test_atlas_store_event_count():
    """AtlasStore: get_event_count returns correct count."""
    store = AtlasStore()

    assert store.get_event_count() == 0

    for i in range(5):
        event = OperationalEvent(
            event_id=f"evt-{i:03d}",
            event_type=EventType.OPERATIONAL_EVENT,
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_data={},
        )
        store.append_operational_event(event)

    assert store.get_event_count() == 5
