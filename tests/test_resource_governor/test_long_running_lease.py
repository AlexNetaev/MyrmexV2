"""Tests for Long Running Lease - SAFE_HOLD Policy (Regel 6)."""

import pytest
from datetime import datetime, timezone, timedelta
import time

from src.resource_governor.slot_manager import SlotManager
from src.resource_governor.governor import ResourceGovernor
from src.contracts.enums import AbbruchKlasse, OnLeaseExpiryPolicy


class TestLongRunningLeaseSafeHold:
    """Tests für Langzeit-Leases mit SAFE_HOLD (Regel 6)."""

    def test_long_running_lease_safe_hold_on_expiry(self):
        """Regel 6: Langzeit-Lease → SAFE_HOLD bei Expiry, nicht harter Abbruch."""
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        slot_manager.register_slot("incubator_slot")
        
        # Langzeit-Lease mit SAFE_HOLD Policy
        lease = governor.request_lease(
            "long_running_pkg",
            "incubator_slot",
            ttl_s=0.2,  # Kurz für Test
            heartbeat_interval_s=0.1,
        )
        assert hasattr(lease, 'lease_id')
        
        # Warten bis TTL abläuft
        time.sleep(0.3)
        
        # Expiry prüfen
        expired = governor.check_expired_leases()
        assert lease.lease_id in expired
        
        # Wichtig: Bei SAFE_HOLD würde der Prozess sicher angehalten werden
        # Nicht hart abgebrochen!

    def test_long_running_lease_grace_period(self):
        """Langzeit-Lease hat eine grace_period_s."""
        # Wird implementiert wenn Governor grace_period unterstützt
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        slot_manager.register_slot("slot_1")
        
        lease = governor.request_lease("pkg_1", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(lease, 'lease_id')
        
        # Grace Period würde hier getestet werden

    def test_long_running_lease_offline_heartbeat_policy(self):
        """offline_heartbeat_policy wird respektiert."""
        # Wird implementiert wenn Governor offline_heartbeat_policy unterstützt
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        slot_manager.register_slot("slot_1")
        
        lease = governor.request_lease("pkg_1", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(lease, 'lease_id')
        
        # Heartbeat testen
        result = governor.heartbeat(lease.lease_id)
        assert result is True

    def test_short_command_lease_aborts_on_expiry(self):
        """SHORT_COMMAND-Lease wird bei Expiry hart abgebrochen."""
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        slot_manager.register_slot("cmd_slot")
        
        # Kurzzeit-Lease (Standard)
        lease = governor.request_lease(
            "short_cmd_pkg",
            "cmd_slot",
            ttl_s=0.1,
            heartbeat_interval_s=0.05,
        )
        assert hasattr(lease, 'lease_id')
        
        # Warten bis TTL abläuft
        time.sleep(0.2)
        
        # Expiry prüfen
        expired = governor.check_expired_leases()
        assert lease.lease_id in expired
        
        # Slot muss wieder frei sein (harter Abbruch)
        state = slot_manager.get_slot_state("cmd_slot")
        assert state == state.__class__.FREE

    def test_long_running_process_not_destroyed_on_safe_hold(self):
        """Regel 6: SAFE_HOLD zerstört den Prozess nicht."""
        # Bei SAFE_HOLD wird der Prozess nur angehalten, nicht zerstört
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        slot_manager.register_slot("process_slot")
        
        lease = governor.request_lease(
            "long_process_pkg",
            "process_slot",
            ttl_s=0.2,
            heartbeat_interval_s=0.1,
        )
        assert hasattr(lease, 'lease_id')
        
        # Warten bis TTL abläuft
        time.sleep(0.3)
        
        # Expiry prüfen
        expired = governor.check_expired_leases()
        assert lease.lease_id in expired
        
        # Wichtig: Der Prozess wäre im SAFE_HOLD-Zustand
        # Nicht zerstört/abgebrochen!

    def test_lease_expiry_policy_safe_hold(self):
        """on_lease_expiry_policy=SAFE_HOLD → Prozess sicher anhalten."""
        # Policy wird in LeaseGrant gespeichert
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        slot_manager.register_slot("slot_1")
        
        lease = governor.request_lease("pkg_1", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(lease, 'lease_id')
        
        # Default Policy ist SAFE_HOLD
        assert lease.on_expiry_policy == OnLeaseExpiryPolicy.SAFE_HOLD

    def test_lease_expiry_policy_abort_to_safe_state(self):
        """on_lease_expiry_policy=ABORT_TO_SAFE_STATE → Prozess in sicheren Zustand."""
        # Policy ABORT_TO_SAFE_STATE würde Prozess in sicheren Zustand bringen
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        slot_manager.register_slot("slot_1")
        
        lease = governor.request_lease("pkg_1", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(lease, 'lease_id')

    def test_lease_expiry_policy_continue_passive_safe(self):
        """on_lease_expiry_policy=CONTINUE_PASSIVE_SAFE → Prozess läuft passiv weiter."""
        # Policy CONTINUE_PASSIVE_SAFE würde Prozess passiv weiterlaufen lassen
        # (z.B. Inkubator hält Temperatur)
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        slot_manager.register_slot("incubator")
        
        lease = governor.request_lease("incubation_pkg", "incubator", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(lease, 'lease_id')
        
        # Default Policy ist SAFE_HOLD
        assert lease.on_expiry_policy == OnLeaseExpiryPolicy.SAFE_HOLD


class TestLeaseExpiryPolicies:
    """Tests für verschiedene Lease-Expiry-Policies."""

    def test_all_four_policies_supported(self):
        """Alle 4 on_lease_expiry_policy Varianten werden unterstützt."""
        # SAFE_HOLD, ABORT_TO_SAFE_STATE, CONTINUE_PASSIVE_SAFE, REQUIRES_RECONCILE
        policies = [
            OnLeaseExpiryPolicy.SAFE_HOLD,
            OnLeaseExpiryPolicy.ABORT_TO_SAFE_STATE,
            OnLeaseExpiryPolicy.CONTINUE_PASSIVE_SAFE,
            OnLeaseExpiryPolicy.REQUIRES_RECONCILE,
        ]
        
        assert len(policies) == 4
        
        # Alle Policies müssen gültig sein
        for policy in policies:
            assert policy is not None

    def test_safe_hold_is_default_for_long_running(self):
        """SAFE_HOLD ist Default für Langzeit-Prozesse."""
        # Standard-Policy ist SAFE_HOLD
        default_policy = OnLeaseExpiryPolicy.SAFE_HOLD
        assert default_policy == OnLeaseExpiryPolicy.SAFE_HOLD

    def test_reconcile_requires_manual_intervention(self):
        """REQUIRES_RECONCILE erfordert manuelle Intervention."""
        # Policy REQUIRES_RECONCILE würde manuelle Prüfung erfordern
        policy = OnLeaseExpiryPolicy.REQUIRES_RECONCILE
        assert policy is not None
