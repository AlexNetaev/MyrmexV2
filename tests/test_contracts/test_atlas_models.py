"""Tests for Atlas models (SignalEvent, Zone, Cluster)."""

import pytest
from pydantic import ValidationError

from src.contracts.atlas_models import Cluster, SignalEvent, Zone


def _signal_event(**overrides):
    data = {
        "signal_id": "signal-1",
        "signal_type": "TEST_SIGNAL",
        "timestamp": "2026-08-18T00:00:00Z",
    }
    data.update(overrides)
    return data


def _zone(**overrides):
    data = {
        "zone_id": "zone-1",
        "name": "Test Zone",
    }
    data.update(overrides)
    return data


def _cluster(**overrides):
    data = {
        "cluster_id": "cluster-1",
        "name": "Test Cluster",
    }
    data.update(overrides)
    return data


def test_signal_event_requires_signal_id():
    """Test: signal_id ist ein Pflichtfeld."""
    payload = _signal_event()
    del payload["signal_id"]

    with pytest.raises(ValidationError):
        SignalEvent(**payload)


def test_signal_event_requires_signal_type():
    """Test: signal_type ist ein Pflichtfeld."""
    payload = _signal_event()
    del payload["signal_type"]

    with pytest.raises(ValidationError):
        SignalEvent(**payload)


def test_signal_event_requires_timestamp():
    """Test: timestamp ist ein Pflichtfeld."""
    payload = _signal_event()
    del payload["timestamp"]

    with pytest.raises(ValidationError):
        SignalEvent(**payload)


def test_signal_event_defaults_severity_to_info():
    """Test: severity default ist INFO."""
    event = SignalEvent(**_signal_event())
    assert event.severity == "INFO"


def test_signal_event_defaults_acknowledged_false():
    """Test: acknowledged default ist False."""
    event = SignalEvent(**_signal_event())
    assert event.acknowledged is False


def test_zone_requires_zone_id():
    """Test: zone_id ist ein Pflichtfeld."""
    payload = _zone()
    del payload["zone_id"]

    with pytest.raises(ValidationError):
        Zone(**payload)


def test_zone_requires_name():
    """Test: name ist ein Pflichtfeld."""
    payload = _zone()
    del payload["name"]

    with pytest.raises(ValidationError):
        Zone(**payload)


def test_zone_optional_parent():
    """Test: parent_zone_id ist optional."""
    zone = Zone(**_zone())
    assert zone.parent_zone_id is None


def test_zone_child_zones_default_empty():
    """Test: child_zones default ist leere Liste."""
    zone = Zone(**_zone())
    assert zone.child_zones == []


def test_cluster_requires_cluster_id():
    """Test: cluster_id ist ein Pflichtfeld."""
    payload = _cluster()
    del payload["cluster_id"]

    with pytest.raises(ValidationError):
        Cluster(**payload)


def test_cluster_requires_name():
    """Test: name ist ein Pflichtfeld."""
    payload = _cluster()
    del payload["name"]

    with pytest.raises(ValidationError):
        Cluster(**payload)


def test_cluster_member_zones_default_empty():
    """Test: member_zones default ist leere Liste."""
    cluster = Cluster(**_cluster())
    assert cluster.member_zones == []


def test_cluster_member_resources_default_empty():
    """Test: member_resources default ist leere Liste."""
    cluster = Cluster(**_cluster())
    assert cluster.member_resources == []


def test_cluster_capacity_default_empty_dict():
    """Test: capacity default ist leeres Dict."""
    cluster = Cluster(**_cluster())
    assert cluster.capacity == {}
