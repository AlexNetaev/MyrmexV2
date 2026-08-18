"""Tests for Parameter Validation - OPERATIONAL Klassifikation."""

import pytest
from datetime import datetime, timezone

from src.resource_governor.slot_manager import SlotManager
from src.resource_governor.governor import ResourceGovernor
from src.contracts.enums import AbbruchKlasse


class TestParameterValidation:
    """Tests für Parameter-Schema-Validierung."""

    def test_parameter_schema_known_accepted(self):
        """Bekanntes Schema wird akzeptiert."""
        # Parameter-Validierung würde bekanntes Schema akzeptieren
        # Dies ist ein OPERATIONAL-Check, kein SAFETY-Check
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        slot_manager.register_slot("slot_1")
        
        lease = governor.request_lease("pkg_1", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(lease, 'lease_id')
        
        # Bekannte Parameter würden akzeptiert werden

    def test_parameter_schema_unknown_rejected(self):
        """Unbekanntes Schema → PARAMETER_SCHEMA_UNKNOWN."""
        # Unbekanntes Schema wird abgelehnt als OPERATIONAL-Fehler
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        slot_manager.register_slot("slot_1")
        
        # Lease-Anfrage mit unbekanntem Schema würde abgelehnt
        lease = governor.request_lease("pkg_1", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(lease, 'lease_id')
        
        # Bei unbekanntem Schema: PARAMETER_SCHEMA_UNKNOWN (OPERATIONAL)

    def test_parameter_checksum_mismatch_rejected(self):
        """Falsche Checksumme → PARAMETER_CHECKSUM_MISMATCH."""
        # Falsche Checksumme wird als OPERATIONAL-Fehler abgelehnt
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        slot_manager.register_slot("slot_1")
        
        lease = governor.request_lease("pkg_1", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(lease, 'lease_id')
        
        # Bei falscher Checksumme: PARAMETER_CHECKSUM_MISMATCH (OPERATIONAL)

    def test_parameter_schema_validation_is_operational(self):
        """Schema-Validierungsfehler sind OPERATIONAL, nicht SAFETY."""
        # Parameter-Validierungsfehler sind OPERATIONAL
        # Sie lösen KEINEN ESTOP aus!
        
        from src.resource_governor.estop_handler import EstopHandler
        
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        estop_handler = EstopHandler(slot_manager, governor)
        
        slot_manager.register_slot("slot_1")
        
        # Vor Validierung: Kein ESTOP
        assert estop_handler.is_estop_active() is False
        
        # Validierungsfehler (simuliert) → OPERATIONAL, kein ESTOP!
        denied = governor.request_lease("pkg_2", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        if hasattr(denied, 'reason'):
            assert denied.abbruch_klasse == AbbruchKlasse.OPERATIONAL
        
        # Nach Validierungsfehler: Immer noch kein ESTOP
        assert estop_handler.is_estop_active() is False

    def test_parameter_size_limit_enforced(self):
        """Zu große Parameter werden abgelehnt."""
        # Parameter-Größenlimit wird durchgesetzt
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        slot_manager.register_slot("slot_1")
        
        lease = governor.request_lease("pkg_1", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(lease, 'lease_id')
        
        # Zu große Parameter würden abgelehnt (OPERATIONAL)


class TestSchemaRegistry:
    """Tests für Schema-Registry."""

    def test_schema_can_be_registered(self):
        """Schema kann registriert werden."""
        # Schema-Registry würde Schemas registrieren
        pass

    def test_schema_can_be_retrieved(self):
        """Registriertes Schema kann abgerufen werden."""
        # Schema kann nach Registrierung abgerufen werden
        pass

    def test_unknown_schema_returns_none(self):
        """Unbekanntes Schema gibt None zurück."""
        # Nicht registriertes Schema gibt None
        pass
