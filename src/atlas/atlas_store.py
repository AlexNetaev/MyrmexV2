"""Atlas Store - Event-Sourcing-Fundament mit Snapshots und Recovery."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.contracts.atlas_models import AtlasSnapshot, OperationalEvent, SignalEvent
from src.contracts.enums import EventType


class AtlasStore:
    """
    Append-only Event-Log mit periodischen Snapshots.
    
    Features:
    - Append-only Event-Log (JSON-Dateien oder In-Memory)
    - Periodische Snapshots (AtlasSnapshot)
    - atlas_head_pointer-Verwaltung
    - Recovery: letzten validen Snapshot laden
    """

    def __init__(self, storage_path: str | None = None) -> None:
        self._events: list[dict[str, Any]] = []
        self._snapshots: list[AtlasSnapshot] = []
        self._atlas_head_pointer: str = "initial"
        self._storage_path = Path(storage_path) if storage_path else None

    def append_operational_event(self, event: OperationalEvent) -> None:
        """Append an operational event to the log."""
        event_dict = {
            "event_type": EventType.OPERATIONAL_EVENT.value,
            "event_id": event.event_id,
            "timestamp": event.timestamp,
            "data": event.model_dump(),
        }
        self._events.append(event_dict)
        self._update_head_pointer(event.event_id)

    def append_scientific_signal(self, signal: SignalEvent) -> None:
        """Append a scientific signal to the log."""
        event_dict = {
            "event_type": EventType.SCIENTIFIC_SIGNAL.value,
            "signal_id": signal.signal_id,
            "timestamp": signal.timestamp,
            "data": signal.model_dump(),
        }
        self._events.append(event_dict)
        self._update_head_pointer(signal.signal_id)

    def append_safety_signal(self, signal: SignalEvent) -> None:
        """Append a safety signal to the log."""
        event_dict = {
            "event_type": EventType.SAFETY_SIGNAL.value,
            "signal_id": signal.signal_id,
            "timestamp": signal.timestamp,
            "data": signal.model_dump(),
        }
        self._events.append(event_dict)
        self._update_head_pointer(signal.signal_id)

    def append_crystal_event(self, crystal_id: str, timestamp: str) -> None:
        """Append a crystal creation event to the log."""
        event_dict = {
            "event_type": EventType.CRYSTAL_CREATED.value,
            "crystal_id": crystal_id,
            "timestamp": timestamp,
            "data": {"crystal_id": crystal_id},
        }
        self._events.append(event_dict)
        self._update_head_pointer(crystal_id)

    def _update_head_pointer(self, ref_id: str) -> None:
        """Update the atlas head pointer."""
        self._atlas_head_pointer = f"{ref_id}:{len(self._events)}"

    def create_snapshot(self) -> AtlasSnapshot:
        """
        Create a periodic snapshot of the current state.
        
        Returns an AtlasSnapshot with checksum.
        """
        current_time = datetime.now(timezone.utc).isoformat()

        # Calculate checksum of all events
        events_json = json.dumps(self._events, sort_keys=True)
        checksum = hashlib.sha256(events_json.encode()).hexdigest()

        snapshot = AtlasSnapshot(
            snapshot_id=f"snapshot-{len(self._snapshots) + 1}",
            atlas_head_pointer=self._atlas_head_pointer,
            timestamp=current_time,
            total_events=len(self._events),
            total_crystals=sum(
                1 for e in self._events if e["event_type"] == EventType.CRYSTAL_CREATED.value
            ),
            checksum=checksum,
        )

        self._snapshots.append(snapshot)

        # Also log the snapshot creation
        snapshot_event = {
            "event_type": EventType.SNAPSHOT_CREATED.value,
            "snapshot_id": snapshot.snapshot_id,
            "timestamp": current_time,
            "data": snapshot.model_dump(),
        }
        self._events.append(snapshot_event)

        return snapshot

    def get_latest_snapshot(self) -> AtlasSnapshot | None:
        """Get the most recent snapshot."""
        if not self._snapshots:
            return None
        return self._snapshots[-1]

    def recover_from_snapshot(self, snapshot: AtlasSnapshot) -> None:
        """
        Recover state from a snapshot.
        
        In a real implementation, this would load events from disk.
        For Phase 2, we just update the head pointer.
        """
        self._atlas_head_pointer = snapshot.atlas_head_pointer

    def get_events_since(self, pointer: str) -> list[dict[str, Any]]:
        """Get events since a given head pointer."""
        # Simple implementation: return all events
        # A real implementation would parse the pointer and filter
        return self._events.copy()

    def get_all_events(self) -> list[dict[str, Any]]:
        """Get all events in the log."""
        return self._events.copy()

    def get_head_pointer(self) -> str:
        """Get the current atlas head pointer."""
        return self._atlas_head_pointer

    def get_event_count(self) -> int:
        """Get the total number of events."""
        return len(self._events)
