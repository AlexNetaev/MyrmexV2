"""Tests for Write-Ahead Log (WAL)."""

import json
import os
import pytest
from pathlib import Path

from src.transaction.wal import WriteAheadLog
from src.contracts.transaction_models import WalPhase


@pytest.fixture
def wal_path(tmp_path):
    """Create a temporary WAL file path."""
    return tmp_path / "test_wal.jsonl"


@pytest.fixture
def wal(wal_path):
    """Create a fresh WAL instance."""
    return WriteAheadLog(wal_path)


def test_wal_entry_has_valid_checksum(wal):
    """Regel 1: Jeder WAL-Eintrag hat eine gültige SHA-256-Checksumme."""
    entry_id = wal.prepare(
        package_id="pkg-001",
        stage="STUFE_6",
        from_state="WEGMARKE_RESERVIERT",
        to_state="PAKET_ENTWURF",
        payload={"test": "data"},
    )
    
    # Read the entry from the prepared entries
    uncommitted = wal.read_uncommitted()
    assert len(uncommitted) == 1
    
    entry = uncommitted[0]
    assert entry.entry_id == entry_id
    assert len(entry.checksum) == 64  # SHA-256 hex length


def test_wal_prepare_writes_persistent_entry(wal, wal_path):
    """Regel 1: prepare() schreibt einen persistenten PREPARE-Eintrag."""
    entry_id = wal.prepare(
        package_id="pkg-001",
        stage="STUFE_6",
        from_state="WEGMARKE_RESERVIERT",
        to_state="PAKET_ENTWURF",
    )
    
    # Check file exists and has content
    assert wal_path.exists()
    
    with open(wal_path, "r") as f:
        content = f.read()
        assert entry_id in content
        assert "PREPARE" in content


def test_wal_commit_marks_entry_committed(wal):
    """Regel 5: commit() markiert einen PREPARE-Eintrag als COMMIT."""
    entry_id = wal.prepare(
        package_id="pkg-001",
        stage="STUFE_6",
        from_state="WEGMARKE_RESERVIERT",
        to_state="PAKET_ENTWURF",
    )
    
    # Before commit: entry is uncommitted
    assert len(wal.read_uncommitted()) == 1
    assert len(wal.read_all()) == 0
    
    # Commit
    result = wal.commit(entry_id)
    assert result is True
    
    # After commit: entry is committed
    assert len(wal.read_uncommitted()) == 0
    assert len(wal.read_all()) == 1


def test_wal_read_uncommitted_returns_prepared_only(wal):
    """read_uncommitted() gibt nur PREPARE-Einträge ohne COMMIT zurück."""
    # Create two entries
    entry_id1 = wal.prepare("pkg-001", "STUFE_6", "A", "B")
    entry_id2 = wal.prepare("pkg-002", "STUFE_6", "A", "B")
    
    # Commit one
    wal.commit(entry_id1)
    
    # Only entry_id2 should be uncommitted
    uncommitted = wal.read_uncommitted()
    assert len(uncommitted) == 1
    assert uncommitted[0].entry_id == entry_id2


def test_wal_discards_corrupt_entries(wal, wal_path):
    """Regel 1: Einträge mit ungültiger Checksumme werden verworfen."""
    # Write a corrupt entry directly to the file with invalid JSON
    with open(wal_path, "w") as f:
        f.write("this is not valid json\n")
    
    # Create new WAL instance - should load without crashing
    wal2 = WriteAheadLog(wal_path)
    
    # Corrupt entry should be discarded
    all_entries = wal2.read_all()
    # The corrupt entry should not be loaded
    assert len(all_entries) == 0


def test_wal_sequence_number_is_monotonic(wal):
    """sequence_number ist monoton steigend."""
    entry_id1 = wal.prepare("pkg-001", "STUFE_6", "A", "B")
    wal.commit(entry_id1)
    
    entry_id2 = wal.prepare("pkg-002", "STUFE_6", "A", "B")
    wal.commit(entry_id2)
    
    entry_id3 = wal.prepare("pkg-003", "STUFE_6", "A", "B")
    wal.commit(entry_id3)
    
    all_entries = sorted(wal.read_all(), key=lambda e: e.sequence_number)
    
    # Sequence numbers should be strictly increasing
    for i in range(1, len(all_entries)):
        assert all_entries[i].sequence_number > all_entries[i-1].sequence_number


def test_wal_read_for_package(wal):
    """read_for_package() returns all entries for a specific package."""
    wal.prepare("pkg-001", "STUFE_6", "A", "B")
    wal.prepare("pkg-002", "STUFE_6", "A", "B")
    wal.prepare("pkg-001", "STUFE_6", "B", "C")
    
    pkg_entries = wal.read_for_package("pkg-001")
    assert len(pkg_entries) == 2
    assert all(e.package_id == "pkg-001" for e in pkg_entries)


def test_wal_is_entry_committed(wal):
    """is_entry_committed() correctly identifies committed entries."""
    entry_id = wal.prepare("pkg-001", "STUFE_6", "A", "B")
    
    assert wal.is_entry_committed(entry_id) is False
    
    wal.commit(entry_id)
    
    assert wal.is_entry_committed(entry_id) is True


def test_wal_get_last_committed_state(wal):
    """get_last_committed_state() returns the latest state for a package."""
    wal.prepare("pkg-001", "STUFE_6", "WEGMARKE_RESERVIERT", "PAKET_ENTWURF")
    wal.commit(wal.read_uncommitted()[0].entry_id)
    
    wal.prepare("pkg-001", "STUFE_6", "PAKET_ENTWURF", "LOCKED_GATE_PENDING")
    wal.commit(wal.read_uncommitted()[0].entry_id)
    
    result = wal.get_last_committed_state("pkg-001")
    assert result == ("STUFE_6", "LOCKED_GATE_PENDING")
