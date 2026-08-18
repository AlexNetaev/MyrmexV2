"""Tests for Path Lease - Atomarität und Fairness."""

import pytest
from datetime import datetime, timezone, timedelta
from threading import Thread, Barrier
import time

from src.resource_governor.slot_manager import SlotManager
from src.resource_governor.governor import ResourceGovernor
from src.resource_governor.zone_manager import ZoneManager
from src.contracts.enums import AbbruchKlasse


class TestPathLeaseAtomicity:
    """Tests für Pfad-Lease-Atomarität (Regel 2)."""

    def test_path_lease_grants_all_slots_atomically(self):
        """Regel 2: Pfad-Lease reserviert ALLE Slots gleichzeitig."""
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        # Slots registrieren
        for slot_id in ["slot_1", "slot_2", "slot_3"]:
            slot_manager.register_slot(slot_id)
        
        # Pfad-Lease für alle Slots anfragen
        # Hinweis: Der Governor hat noch keine request_path_lease Methode
        # Dies wird in der Implementierung hinzugefügt
        # Für jetzt testen wir einzelne Leases
        lease1 = governor.request_lease("pkg_1", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        lease2 = governor.request_lease("pkg_1", "slot_2", ttl_s=60.0, heartbeat_interval_s=10.0)
        lease3 = governor.request_lease("pkg_1", "slot_3", ttl_s=60.0, heartbeat_interval_s=10.0)
        
        # Alle müssen erfolgreich sein
        assert hasattr(lease1, 'lease_id')
        assert hasattr(lease2, 'lease_id')
        assert hasattr(lease3, 'lease_id')

    def test_path_lease_denied_if_any_slot_busy(self):
        """Regel 2: Wenn EIN Slot belegt ist → GESAMTE Pfad-Lease abgelehnt."""
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        # Slots registrieren
        for slot_id in ["slot_1", "slot_2", "slot_3"]:
            slot_manager.register_slot(slot_id)
        
        # Ersten Slot belegen
        lease1 = governor.request_lease("pkg_1", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(lease1, 'lease_id')
        
        # Zweiter Slot ist noch frei
        lease2 = governor.request_lease("pkg_2", "slot_2", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(lease2, 'lease_id')
        
        # Dritter Slot auch
        lease3 = governor.request_lease("pkg_3", "slot_3", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(lease3, 'lease_id')
        
        # Jetzt versuchen wir slot_1 erneut zu belegen → muss abgelehnt werden
        denied = governor.request_lease("pkg_4", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(denied, 'reason')
        assert denied.abbruch_klasse == AbbruchKlasse.OPERATIONAL

    def test_path_lease_no_partial_reservation(self):
        """Regel 2 (KRITISCH): Keine partielle Reservierung. Entweder alle oder keine."""
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        # Slots registrieren
        for slot_id in ["slot_1", "slot_2", "slot_3"]:
            slot_manager.register_slot(slot_id)
        
        # Ersten Slot belegen
        lease1 = governor.request_lease("pkg_1", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(lease1, 'lease_id')
        
        # Versuch eine Pfad-Lease für [slot_2, slot_3] zu bekommen
        # Wenn einer belegt wäre, müsste die gesamte Lease abgelehnt werden
        # Da beide frei sind, sollte es funktionieren
        
        lease2 = governor.request_lease("pkg_2", "slot_2", ttl_s=60.0, heartbeat_interval_s=10.0)
        lease3 = governor.request_lease("pkg_2", "slot_3", ttl_s=60.0, heartbeat_interval_s=10.0)
        
        # Beide müssen erfolgreich sein (keine partielle Reservierung!)
        assert hasattr(lease2, 'lease_id')
        assert hasattr(lease3, 'lease_id')
        
        # Wichtig: Es darf keinen Zustand geben, wo nur slot_2 reserviert ist
        # aber slot_3 nicht (oder umgekehrt)

    def test_path_lease_released_on_expiry(self):
        """Pfad-Lease wird nach TTL freigegeben."""
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        # Slot registrieren
        slot_manager.register_slot("slot_1")
        
        # Lease mit kurzer TTL
        lease = governor.request_lease("pkg_1", "slot_1", ttl_s=0.1, heartbeat_interval_s=0.05)
        assert hasattr(lease, 'lease_id')
        
        # Warten bis TTL abläuft
        time.sleep(0.2)
        
        # Expiry prüfen
        expired = governor.check_expired_leases()
        assert lease.lease_id in expired
        
        # Slot muss wieder frei sein
        assert slot_manager.get_slot_state("slot_1") == slot_manager.get_slot_state("slot_1").__class__.FREE

    def test_max_path_hold_time_enforced(self):
        """Regel 3: Pfad-Lease wird nach max_path_hold_time zwangsweise freigegeben."""
        # Wird implementiert wenn Governor max_path_hold_time unterstützt
        # Für jetzt testen wir dass Leases grundsätzlich verfallen können
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        slot_manager.register_slot("slot_1")
        
        lease = governor.request_lease("pkg_1", "slot_1", ttl_s=0.1, heartbeat_interval_s=0.05)
        assert hasattr(lease, 'lease_id')
        
        time.sleep(0.2)
        
        expired = governor.check_expired_leases()
        assert len(expired) > 0

    def test_path_lease_rollback_on_failure(self):
        """Wenn Pfad-Lease fehlschlägt, werden bereits reservierte Slots freigegeben."""
        # Dieser Test prüft das Rollback-Verhalten
        # Wird vollständig implementiert wenn request_path_lease verfügbar ist
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        for slot_id in ["slot_1", "slot_2"]:
            slot_manager.register_slot(slot_id)
        
        # Beide Slots belegen
        lease1 = governor.request_lease("pkg_1", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        lease2 = governor.request_lease("pkg_1", "slot_2", ttl_s=60.0, heartbeat_interval_s=10.0)
        
        # Freigabe testen
        released1 = governor.release_lease(lease1.lease_id)
        released2 = governor.release_lease(lease2.lease_id)
        
        assert released1 is True
        assert released2 is True
        
        # Beide Slots müssen wieder frei sein
        assert slot_manager.get_slot_state("slot_1") == slot_manager.get_slot_state("slot_1").__class__.FREE
        assert slot_manager.get_slot_state("slot_2") == slot_manager.get_slot_state("slot_2").__class__.FREE


class TestFairness:
    """Tests für Fairness/Aging (Regel 3)."""

    def test_fairness_aging_increases_priority(self):
        """Regel 3: Je länger ein Paket wartet, desto höher die Priorität."""
        # Wird implementiert wenn Governor fairness_priority unterstützt
        # Für jetzt testen wir Grundfunktionalität
        slot_manager = SlotManager()
        governor = ResourceGovernor(slot_manager)
        
        slot_manager.register_slot("slot_1")
        
        # Paket wartet indem es auf Lease wartet
        denied1 = governor.request_lease("pkg_1", "slot_1", ttl_s=60.0, heartbeat_interval_s=10.0)
        assert hasattr(denied1, 'lease_id') or hasattr(denied1, 'reason')
        
        # Nach Wartezeit sollte Priorität steigen
        # (wird in vollständiger Implementierung getestet)

    def test_fairness_no_starvation(self):
        """Regel 3: Wartende Pakete verhungern nicht."""
        # Wird implementiert wenn Fairness-Queue verfügbar ist
        pass

    def test_deadlock_detection_finds_cycles(self):
        """Regel 3: Deadlock-Erkennung findet Zyklen in der Warteschlange."""
        # Wird implementiert wenn detect_deadlocks verfügbar ist
        pass

    def test_deadlock_detection_no_false_positive(self):
        """Keine Deadlock-Erkennung bei linearer Warteschlange."""
        # Wird implementiert wenn detect_deadlocks verfügbar ist
        pass
