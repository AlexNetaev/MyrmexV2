"""Recovery logic for MYRMEX v2.4.0 - Crash recovery with safety guarantees."""

from datetime import datetime, timezone
from typing import Any

from src.contracts.transaction_models import (
    RecoveryAction,
    RecoveryActionType,
    Stage6State,
    Stage7State,
    Stage8State,
)
from src.transaction.wal import WriteAheadLog


class RecoveryService:
    """Crash recovery service with safety guarantees."""

    def __init__(self, wal: WriteAheadLog, lease_ttl_s: float = 3600.0):
        self.wal = wal
        self.lease_ttl_s = lease_ttl_s
        self._processed_packages: set[str] = set()

    def recover(self, current_time: str | None = None) -> list[RecoveryAction]:
        """
        Perform crash recovery.
        
        Returns a list of RecoveryAction for each package that needs attention.
        Recovery is idempotent - can be called multiple times safely.
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc).isoformat()

        actions: list[RecoveryAction] = []
        
        # Get all packages from WAL
        all_entries = self.wal.read_all() + self.wal.read_uncommitted()
        package_ids = set(e.package_id for e in all_entries)

        for package_id in package_ids:
            # Skip already processed packages (idempotency)
            if package_id in self._processed_packages:
                continue

            action = self._determine_recovery_action(package_id, current_time)
            if action:
                actions.append(action)
                self._processed_packages.add(package_id)

        return actions

    def _determine_recovery_action(self, package_id: str, 
                                   current_time: str) -> RecoveryAction | None:
        """Determine the appropriate recovery action for a package."""
        
        # Get last committed state
        last_committed = self.wal.get_last_committed_state(package_id)
        
        if last_committed is None:
            # No committed state, check for uncommitted entries
            uncommitted = self.wal.read_for_package(package_id)
            if uncommitted and any(e.phase.value == "PREPARE" for e in uncommitted):
                # PREPARE without COMMIT → DRAFT_RECOVERABLE
                return RecoveryAction(
                    package_id=package_id,
                    current_stage="UNKNOWN",
                    current_state="DRAFT_RECOVERABLE",
                    action=RecoveryActionType.DISCARD,
                    reason="Uncommitted PREPARE entry found",
                )
            return None

        stage, state = last_committed

        # Check lease TTL
        if self._is_lease_expired(package_id, stage, current_time):
            return RecoveryAction(
                package_id=package_id,
                current_stage=stage,
                current_state=state,
                action=RecoveryActionType.DISCARD,
                reason="Lease expired",
            )

        # Apply recovery rules based on state
        # KRITISCH: Regel 2 - Kein Stage-Skipping
        
        if state == Stage6State.LOCKED_GATE_PENDING.value:
            # KRITISCH: Zurück zu Stufe 7, NICHT zu Stufe 8
            return RecoveryAction(
                package_id=package_id,
                current_stage=stage,
                current_state=state,
                action=RecoveryActionType.RETRY_GATE,
                reason="LOCKED_GATE_PENDING requires Gate-Prüfung in Stufe 7",
            )

        if state == Stage6State.GATE_APPROVED.value:
            # Lease prüfen
            return RecoveryAction(
                package_id=package_id,
                current_stage=stage,
                current_state=state,
                action=RecoveryActionType.RECHECK_LEASE,
                reason="GATE_APPROVED requires lease recheck",
            )

        if state == Stage6State.LOCKED_READY_TO_EXEC.value:
            # gate_record.signature + lease_status + Slot prüfen
            return RecoveryAction(
                package_id=package_id,
                current_stage=stage,
                current_state=state,
                action=RecoveryActionType.CHECK_SLOT,
                reason="LOCKED_READY_TO_EXEC requires slot verification",
            )

        if state == Stage8State.EXECUTING.value:
            # Physischen Slot-Zustand / Questor-Zustand prüfen
            return RecoveryAction(
                package_id=package_id,
                current_stage=stage,
                current_state=state,
                action=RecoveryActionType.CHECK_SLOT,
                reason="EXECUTING requires Questor/Slot state check",
            )

        # For other states, resume normally
        return RecoveryAction(
            package_id=package_id,
            current_stage=stage,
            current_state=state,
            action=RecoveryActionType.RESUME,
            reason=f"Resuming from {state}",
        )

    def _is_lease_expired(self, package_id: str, stage: str, 
                          current_time: str) -> bool:
        """Check if the lease for a package has expired."""
        # Simplified implementation - in production, this would check
        # actual lease timestamps from the payload
        entries = self.wal.read_for_package(package_id)
        if not entries:
            return False

        # Get the earliest entry timestamp for this package
        earliest_entry = min(entries, key=lambda e: e.timestamp)
        
        try:
            entry_time = datetime.fromisoformat(earliest_entry.timestamp.replace('Z', '+00:00'))
            current = datetime.fromisoformat(current_time.replace('Z', '+00:00'))
            age_seconds = (current - entry_time).total_seconds()
            return age_seconds > self.lease_ttl_s
        except (ValueError, TypeError):
            return False

    def reset_processed_cache(self):
        """Reset the processed packages cache (for testing)."""
        self._processed_packages.clear()
