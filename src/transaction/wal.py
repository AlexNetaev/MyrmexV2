"""Write-Ahead Log (WAL) for MYRMEX v2.4.0 - Two-Phase Commit."""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import uuid

from src.contracts.transaction_models import WalEntry, WalPhase


class WriteAheadLog:
    """Persistent WAL with Two-Phase Commit support."""

    def __init__(self, wal_path: str | Path):
        self.wal_path = Path(wal_path)
        self._sequence_counter = 0
        self._committed_entries: dict[str, WalEntry] = {}
        self._prepared_entries: dict[str, WalEntry] = {}
        self._load_existing_entries()

    def _compute_checksum(self, entry_data: dict[str, Any]) -> str:
        """Compute SHA-256 checksum over serialized entry data."""
        serialized = json.dumps(entry_data, sort_keys=True).encode("utf-8")
        return hashlib.sha256(serialized).hexdigest()

    def _load_existing_entries(self):
        """Load existing entries from WAL file."""
        if not self.wal_path.exists():
            return

        with open(self.wal_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entry = WalEntry(**data)
                    if entry.phase == WalPhase.COMMIT:
                        self._committed_entries[entry.entry_id] = entry
                    else:
                        self._prepared_entries[entry.entry_id] = entry
                    if entry.sequence_number >= self._sequence_counter:
                        self._sequence_counter = entry.sequence_number + 1
                except (json.JSONDecodeError, Exception):
                    # Corrupt entry, skip
                    continue

    def _write_entry(self, entry: WalEntry):
        """Write entry to WAL file with fsync."""
        entry_data = entry.model_dump()
        line = json.dumps(entry_data) + "\n"

        with open(self.wal_path, "a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())

    def prepare(self, package_id: str, stage: str, from_state: str, to_state: str,
                payload: dict[str, Any] | None = None) -> str:
        """Phase 1 of Two-Phase Commit: Write PREPARE entry."""
        entry_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        entry_data_for_checksum = {
            "package_id": package_id,
            "stage": stage,
            "from_state": from_state,
            "to_state": to_state,
            "payload": payload or {},
            "phase": WalPhase.PREPARE.value,
        }

        entry = WalEntry(
            entry_id=entry_id,
            sequence_number=self._sequence_counter,
            timestamp=timestamp,
            package_id=package_id,
            stage=stage,
            from_state=from_state,
            to_state=to_state,
            payload=payload or {},
            phase=WalPhase.PREPARE,
            checksum=self._compute_checksum(entry_data_for_checksum),
        )

        self._sequence_counter += 1
        self._prepared_entries[entry_id] = entry
        self._write_entry(entry)

        return entry_id

    def commit(self, entry_id: str) -> bool:
        """Phase 2 of Two-Phase Commit: Mark entry as COMMITTED."""
        if entry_id not in self._prepared_entries:
            return False

        prepared_entry = self._prepared_entries[entry_id]

        commit_entry = WalEntry(
            entry_id=entry_id,
            sequence_number=self._sequence_counter,
            timestamp=datetime.now(timezone.utc).isoformat(),
            package_id=prepared_entry.package_id,
            stage=prepared_entry.stage,
            from_state=prepared_entry.from_state,
            to_state=prepared_entry.to_state,
            payload=prepared_entry.payload,
            phase=WalPhase.COMMIT,
            checksum=self._compute_checksum({
                "entry_id": entry_id,
                "phase": WalPhase.COMMIT.value,
            }),
        )

        self._sequence_counter += 1
        self._committed_entries[entry_id] = commit_entry
        del self._prepared_entries[entry_id]
        self._write_entry(commit_entry)

        return True

    def read_all(self) -> list[WalEntry]:
        """Read all valid committed entries."""
        return list(self._committed_entries.values())

    def read_uncommitted(self) -> list[WalEntry]:
        """Read all PREPARE entries without corresponding COMMIT."""
        return list(self._prepared_entries.values())

    def read_for_package(self, package_id: str) -> list[WalEntry]:
        """Read all entries (committed and uncommitted) for a package."""
        result = []
        for entry in list(self._committed_entries.values()) + list(self._prepared_entries.values()):
            if entry.package_id == package_id:
                result.append(entry)
        return sorted(result, key=lambda e: e.sequence_number)

    def is_entry_committed(self, entry_id: str) -> bool:
        """Check if an entry has been committed."""
        return entry_id in self._committed_entries

    def get_last_committed_state(self, package_id: str) -> tuple[str, str] | None:
        """Get the last committed (stage, state) for a package."""
        entries = [e for e in self._committed_entries.values() if e.package_id == package_id]
        if not entries:
            return None
        last_entry = max(entries, key=lambda e: e.sequence_number)
        return (last_entry.stage, last_entry.to_state)
