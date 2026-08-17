"""Tests for LeaseGrant and LeaseStatus contracts."""

import pytest
from pydantic import ValidationError

from src.contracts.enums import OnLeaseExpiryPolicy, ResourceClass, SlotStatus
from src.contracts.lease_models import LeaseGrant, LeaseStatus


def _lease_grant(**overrides):
    data = {
        "lease_id": "lease-1",
        "slot_id": "slot-1",
        "package_id": "pkg-001",
        "granted_at": "2026-08-18T00:00:00Z",
    }
    data.update(overrides)
    return data


def _lease_status(**overrides):
    data = {
        "lease_id": "lease-1",
        "slot_id": "slot-1",
        "package_id": "pkg-001",
        "status": SlotStatus.ACTIVE,
        "granted_at": "2026-08-18T00:00:00Z",
    }
    data.update(overrides)
    return data


def test_lease_grant_requires_lease_id():
    """Test: lease_id ist ein Pflichtfeld."""
    payload = _lease_grant()
    del payload["lease_id"]

    with pytest.raises(ValidationError):
        LeaseGrant(**payload)


def test_lease_grant_requires_granted_at():
    """Test: granted_at ist ein Pflichtfeld."""
    payload = _lease_grant()
    del payload["granted_at"]

    with pytest.raises(ValidationError):
        LeaseGrant(**payload)


def test_lease_grant_defaults_on_expiry_policy():
    """Test: on_expiry_policy default ist SAFE_HOLD."""
    grant = LeaseGrant(**_lease_grant())
    assert grant.on_expiry_policy == OnLeaseExpiryPolicy.SAFE_HOLD


def test_lease_grant_accepts_resource_class():
    """Test: resource_class kann gesetzt werden."""
    grant = LeaseGrant(
        **_lease_grant(resource_class=ResourceClass.SANDBOX_ENVIRONMENT)
    )
    assert grant.resource_class == ResourceClass.SANDBOX_ENVIRONMENT


def test_lease_grant_execution_flags_default_false():
    """Test: execution_allowed flags default zu False."""
    grant = LeaseGrant(**_lease_grant())
    assert grant.physical_execution_allowed is False
    assert grant.sandbox_execution_allowed is False
    assert grant.compute_execution_allowed is False


def test_lease_status_requires_status():
    """Test: status ist ein Pflichtfeld in LeaseStatus."""
    payload = _lease_status()
    del payload["status"]

    with pytest.raises(ValidationError):
        LeaseStatus(**payload)


def test_lease_status_is_active_flag():
    """Test: is_active flag kann gesetzt werden."""
    status = LeaseStatus(**_lease_status(is_active=True))
    assert status.is_active is True


def test_lease_status_is_expired_flag():
    """Test: is_expired flag kann gesetzt werden."""
    status = LeaseStatus(**_lease_status(is_expired=True))
    assert status.is_expired is True


def test_lease_status_suspension_reason():
    """Test: suspension_reason kann gesetzt werden."""
    status = LeaseStatus(
        **_lease_status(
            is_suspended=True,
            suspension_reason="LEASE_EXPIRED",
        )
    )
    assert status.is_suspended is True
    assert status.suspension_reason == "LEASE_EXPIRED"


def test_lease_status_remaining_ttl_non_negative():
    """Test: remaining_ttl_s muss >= 0 sein."""
    with pytest.raises(ValidationError):
        LeaseStatus(**_lease_status(remaining_ttl_s=-1.0))

    # Valid value
    status = LeaseStatus(**_lease_status(remaining_ttl_s=30.0))
    assert status.remaining_ttl_s == 30.0
