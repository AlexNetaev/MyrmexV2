"""Archivar - Stufe 1 der Pipeline: Die Immunabwehr des Systems."""

import hashlib
from datetime import datetime, timezone
from typing import Any

from src.atlas.atlas_store import AtlasStore
from src.atlas.signal_registry import SignalRegistry
from src.contracts.atlas_models import OperationalEvent, SignalEvent, WissensKristall
from src.contracts.enums import (
    AbbruchKlasse,
    ErgebnisStatus,
    EventType,
    PackageStatus,
    SignalSeverity,
    SignalType,
)
from src.contracts.questor_metadata import OperationalMetrics
from src.contracts.questor_result import QuestorErgebnisPaket


class ArchivarResult:
    """Result of processing a QuestorErgebnisPaket."""

    def __init__(
        self,
        accepted: bool,
        status: str,
        rejection_reason: str | None = None,
    ) -> None:
        self.accepted = accepted
        self.status = status
        self.rejection_reason = rejection_reason


class Archivar:
    """
    Der Archivar: Empfängt QuestorErgebnisPaket und verarbeitet es.
    
    Regeln:
    1. Operational ≠ Scientific: OPERATIONAL-Abbrüche erzeugen KEINE wissenschaftlichen Signale
    2. Idempotenz: Duplikate werden verworfen
    3. Sequence-Monotonie: sequence_number wird pro questor_instance_id geprüft
    """

    def __init__(self) -> None:
        # Track seen idempotency keys
        self._seen_idempotency_keys: set[str] = set()
        # Track last sequence number per questor_instance_id
        self._last_sequence_per_questor: dict[str, int] = {}
        # Event store
        self._atlas_store = AtlasStore()
        # Signal registry
        self._signal_registry = SignalRegistry()
        # Operational event log
        self._operational_events: list[OperationalEvent] = []
        # Crystals
        self._crystals: list[WissensKristall] = []

    def process_result(self, paket: QuestorErgebnisPaket) -> ArchivarResult:
        """
        Process a QuestorErgebnisPaket.
        
        Steps:
        1. Check idempotency_key for duplicates
        2. Check sequence_number monotonicity per questor_instance_id
        3. Check vollstaendig_flag
        4. Separate by abbruch_klasse (OPERATIONAL vs SCIENTIFIC vs SAFETY)
        5. Write to appropriate logs/registries
        """
        # Step 1: Idempotency check
        idempotency_key = paket.idempotency_key
        if idempotency_key in self._seen_idempotency_keys:
            return ArchivarResult(
                accepted=False,
                status="REJECTED",
                rejection_reason="DUPLICATE_IDEMPOTENCY_KEY",
            )

        # Step 2: Sequence monotonicity check (per questor_instance_id)
        questor_id = paket.questor_instance_id
        last_seq = self._last_sequence_per_questor.get(questor_id, 0)

        if paket.sequence_number <= last_seq:
            return ArchivarResult(
                accepted=False,
                status="REJECTED",
                rejection_reason="SEQUENCE_NOT_MONOTONIC",
            )

        # Mark as seen
        self._seen_idempotency_keys.add(idempotency_key)
        self._last_sequence_per_questor[questor_id] = paket.sequence_number

        # Step 3: Check completeness
        if not paket.vollstaendig_flag:
            # Mark as DRAFT_RECOVERABLE, do NOT crystallize
            self._handle_incomplete_package(paket)
            return ArchivarResult(
                accepted=True,
                status="DRAFT_RECOVERABLE",
            )

        # Step 4: Process based on abbruch_klasse
        if paket.abbruch_klasse == AbbruchKlasse.OPERATIONAL:
            self._handle_operational_result(paket)
            return ArchivarResult(
                accepted=True,
                status="ACCEPTED",
            )
        elif paket.abbruch_klasse == AbbruchKlasse.SCIENTIFIC:
            self._handle_scientific_result(paket)
            return ArchivarResult(
                accepted=True,
                status="CRYSTALLIZED" if paket.kristall_kandidaten else "ACCEPTED",
            )
        elif paket.abbruch_klasse == AbbruchKlasse.SAFETY:
            self._handle_safety_result(paket)
            if paket.kristall_kandidaten and paket.vollstaendig_flag:
                return ArchivarResult(
                    accepted=True,
                    status="CRYSTALLIZED",
                )
            return ArchivarResult(
                accepted=True,
                status="ACCEPTED",
            )

        # Default: accepted
        return ArchivarResult(
            accepted=True,
            status="ACCEPTED",
        )

    def _handle_incomplete_package(self, paket: QuestorErgebnisPaket) -> None:
        """Handle an incomplete package (vollstaendig_flag=False)."""
        # Log as operational event, do NOT create crystals or signals
        timestamp = datetime.now(timezone.utc).isoformat()
        event = OperationalEvent(
            event_id=self._generate_event_id("incomplete", paket.package_id),
            event_type=EventType.OPERATIONAL_EVENT,
            source_package_id=paket.package_id,
            source_zyklus_id=paket.zyklus_id,
            questor_instance_id=paket.questor_instance_id,
            timestamp=timestamp,
            event_data={
                "reason": "INCOMPLETE_PACKAGE",
                "sequence_number": paket.sequence_number,
            },
            error_code="INCOMPLETE",
        )
        self._operational_events.append(event)
        self._atlas_store.append_operational_event(event)

    def _handle_operational_result(self, paket: QuestorErgebnisPaket) -> None:
        """
        Handle OPERATIONAL result.
        
        Regel 1: OPERATIONAL-Abbrüche erzeugen KEINE wissenschaftlichen Signale oder Kristalle.
        Sie schreiben ausschließlich in den operational_event_log.
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        # Create operational event
        event_data: dict[str, Any] = {
            "status": paket.status.value,
            "abbruch_grund": paket.abbruch_grund,
            "sequence_number": paket.sequence_number,
        }

        # Include operational_metrics from questor_metadata if present
        if paket.questor_metadata and paket.questor_metadata.operational_metrics:
            metrics = paket.questor_metadata.operational_metrics
            event_data["oom_count"] = metrics.oom_count
            event_data["timeout_count"] = metrics.timeout_count
            event_data["lease_wait_time_s"] = metrics.lease_wait_time_s
            event_data["capability_retry_count"] = metrics.capability_retry_count
            event_data["recovery_attempts"] = metrics.recovery_attempts

        event = OperationalEvent(
            event_id=self._generate_event_id("operational", paket.package_id),
            event_type=EventType.OPERATIONAL_EVENT,
            source_package_id=paket.package_id,
            source_zyklus_id=paket.zyklus_id,
            questor_instance_id=paket.questor_instance_id,
            timestamp=timestamp,
            event_data=event_data,
            error_code=paket.abbruch_grund,
            abbruch_grund=paket.abbruch_grund,
        )

        self._operational_events.append(event)
        self._atlas_store.append_operational_event(event)

        # NOTE: No scientific signals, no crystals!

    def _handle_scientific_result(self, paket: QuestorErgebnisPaket) -> None:
        """Handle SCIENTIFIC result - creates signals and potentially crystals."""
        timestamp = datetime.now(timezone.utc).isoformat()

        # Create scientific signal
        signal = SignalEvent(
            signal_id=self._generate_signal_id(paket.package_id),
            signal_type=SignalType.SCIENTIFIC,
            source_package_id=paket.package_id,
            source_zyklus_id=paket.zyklus_id,
            timestamp=timestamp,
            payload={
                "status": paket.status.value,
                "abbruch_grund": paket.abbruch_grund,
                "ergebnisse": paket.ergebnis_daten,
            },
            severity=SignalSeverity.PURPLE,  # Scientific signals are purple
        )

        self._signal_registry.append_signal(signal)
        self._atlas_store.append_scientific_signal(signal)

        # Create crystals from kristall_kandidaten if complete
        if paket.vollstaendig_flag and paket.kristall_kandidaten:
            self._create_crystals(paket)

    def _handle_safety_result(self, paket: QuestorErgebnisPaket) -> None:
        """Handle SAFETY result - creates safety signals."""
        timestamp = datetime.now(timezone.utc).isoformat()

        # Create safety signal
        signal = SignalEvent(
            signal_id=self._generate_signal_id(paket.package_id),
            signal_type=SignalType.SAFETY,
            source_package_id=paket.package_id,
            source_zyklus_id=paket.zyklus_id,
            timestamp=timestamp,
            payload={
                "status": paket.status.value,
                "abbruch_grund": paket.abbruch_grund,
                "safety_relevant": True,
            },
            severity=SignalSeverity.RED,  # Safety signals are red (highest priority)
        )

        self._signal_registry.append_signal(signal)
        self._atlas_store.append_safety_signal(signal)

        # Create crystals from kristall_kandidaten if complete
        if paket.vollstaendig_flag and paket.kristall_kandidaten:
            self._create_crystals(paket)

    def _create_crystals(self, paket: QuestorErgebnisPaket) -> None:
        """Create WissensKristall from kristall_kandidaten."""
        timestamp = datetime.now(timezone.utc).isoformat()

        for kandidat in paket.kristall_kandidaten:
            crystal_id = self._generate_crystal_id(paket.package_id, len(self._crystals))

            crystal = WissensKristall(
                kristall_id=crystal_id,
                source_package_id=paket.package_id,
                source_zyklus_id=paket.zyklus_id,
                questor_instance_id=paket.questor_instance_id,
                kristall_daten=kandidat,
                confirmation_count=1,
                decay=1.0,
                half_life_s=3600.0,
                created_at=timestamp,
                last_updated_at=timestamp,
            )

            self._crystals.append(crystal)
            self._atlas_store.append_crystal_event(crystal_id, timestamp)

    def _generate_event_id(self, prefix: str, package_id: str) -> str:
        """Generate a unique event ID."""
        timestamp = datetime.now(timezone.utc).isoformat()
        return hashlib.sha256(f"{prefix}:{package_id}:{timestamp}".encode()).hexdigest()[:16]

    def _generate_signal_id(self, package_id: str) -> str:
        """Generate a unique signal ID."""
        timestamp = datetime.now(timezone.utc).isoformat()
        return hashlib.sha256(f"signal:{package_id}:{timestamp}".encode()).hexdigest()[:16]

    def _generate_crystal_id(self, package_id: str, index: int) -> str:
        """Generate a unique crystal ID."""
        timestamp = datetime.now(timezone.utc).isoformat()
        return hashlib.sha256(f"crystal:{package_id}:{index}:{timestamp}".encode()).hexdigest()[:16]

    def get_crystals(self) -> list[WissensKristall]:
        """Get all crystals."""
        return self._crystals.copy()

    def get_signals(self) -> list[SignalEvent]:
        """Get all signals from the registry."""
        return self._signal_registry.get_all_signals()

    def get_operational_events(self) -> list[OperationalEvent]:
        """Get all operational events."""
        return self._operational_events.copy()

    def get_atlas_store(self) -> AtlasStore:
        """Get the atlas store."""
        return self._atlas_store

    def get_signal_registry(self) -> SignalRegistry:
        """Get the signal registry."""
        return self._signal_registry
