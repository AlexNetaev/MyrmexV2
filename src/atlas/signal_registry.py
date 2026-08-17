"""Signal Registry for Atlas - append-only signal stack with resolution and decay."""

import hashlib
from datetime import datetime, timezone
from typing import Any

from src.contracts.atlas_models import SignalEvent, WissensKristall
from src.contracts.enums import SignalSeverity


# Priority order for signal resolution (higher index = higher priority)
_SEVERITY_PRIORITY = {
    SignalSeverity.WHITE: 0,
    SignalSeverity.GREEN: 1,
    SignalSeverity.PURPLE: 2,
    SignalSeverity.YELLOW: 3,
    SignalSeverity.RED: 4,
}


class SignalRegistry:
    """
    Signal-Stack pro Koordinate (append-only).
    
    Features:
    - Signal-Resolution: 🟥 > 🟨 > 🟪 > 🟩 > ⬜
    - Kristallisation: confirmation_count >= 3 → decay = 0
    - Verfall: strength = initial × (0.5 ^ (age / half_life))
    """

    def __init__(self) -> None:
        # Map coordinate -> list of signals (append-only)
        self._signal_stacks: dict[str, list[SignalEvent]] = {}
        # Map crystal_id -> WissensKristall
        self._crystals: dict[str, WissensKristall] = {}
        # Track which coordinates have been crystallized
        self._crystallized_coordinates: set[str] = set()

    def append_signal(
        self,
        signal: SignalEvent,
        half_life_s: float = 3600.0,
    ) -> None:
        """
        Append a signal to the stack for its coordinate.
        
        The coordinate is derived from source_package_id and source_zyklus_id.
        If not available, uses a default coordinate.
        """
        coordinate = self._get_coordinate(signal)

        if coordinate not in self._signal_stacks:
            self._signal_stacks[coordinate] = []

        # Apply decay to signal strength
        current_time = datetime.now(timezone.utc)
        signal_time = datetime.fromisoformat(signal.timestamp.replace("Z", "+00:00"))
        age_s = (current_time - signal_time).total_seconds()

        # Calculate strength based on decay formula
        strength = 1.0 * (0.5 ** (age_s / half_life_s))
        signal.payload["strength"] = strength

        self._signal_stacks[coordinate].append(signal)

        # Check for crystallization
        self._check_crystallization(coordinate, half_life_s)

    def _get_coordinate(self, signal: SignalEvent) -> str:
        """Extract or derive coordinate from signal."""
        if signal.source_package_id and signal.source_zyklus_id:
            return f"{signal.source_package_id}:{signal.source_zyklus_id}"
        return "default"

    def resolve_coordinate(self, coordinate: str) -> SignalEvent | None:
        """
        Resolve the effective signal for a coordinate.
        
        Returns the signal with highest severity priority.
        """
        if coordinate not in self._signal_stacks:
            return None

        stack = self._signal_stacks[coordinate]
        if not stack:
            return None

        # Find signal with highest priority
        highest_priority = -1
        resolved_signal = None

        for signal in stack:
            priority = _SEVERITY_PRIORITY.get(signal.severity, 0)
            if priority > highest_priority:
                highest_priority = priority
                resolved_signal = signal

        return resolved_signal

    def get_signal_stack(self, coordinate: str) -> list[SignalEvent]:
        """Get the append-only signal stack for a coordinate."""
        if coordinate not in self._signal_stacks:
            return []
        return self._signal_stacks[coordinate].copy()

    def _check_crystallization(self, coordinate: str, half_life_s: float) -> None:
        """
        Check if a coordinate should be crystallized.
        
        Crystallization occurs when confirmation_count >= 3.
        """
        if coordinate in self._crystallized_coordinates:
            return

        stack = self._signal_stacks.get(coordinate, [])
        if len(stack) < 3:
            return

        # Crystallize
        confirmation_count = len(stack)
        if confirmation_count >= 3:
            self._create_crystal(coordinate, confirmation_count, half_life_s)
            self._crystallized_coordinates.add(coordinate)

    def _create_crystal(
        self,
        coordinate: str,
        confirmation_count: int,
        half_life_s: float,
    ) -> None:
        """Create a WissensKristall from accumulated signals."""
        stack = self._signal_stacks.get(coordinate, [])
        if not stack:
            return

        first_signal = stack[0]

        # Generate crystal ID
        crystal_id = hashlib.sha256(
            f"{coordinate}:{confirmation_count}".encode()
        ).hexdigest()[:16]

        current_time = datetime.now(timezone.utc).isoformat()

        # Aggregate kristall_daten from all signals
        kristall_daten: dict[str, Any] = {
            "confirmation_count": confirmation_count,
            "signals": [s.signal_id for s in stack],
        }

        # Merge payloads
        for signal in stack:
            for key, value in signal.payload.items():
                if key not in kristall_daten:
                    kristall_daten[key] = value

        crystal = WissensKristall(
            kristall_id=crystal_id,
            source_package_id=first_signal.source_package_id or "unknown",
            source_zyklus_id=first_signal.source_zyklus_id or "unknown",
            questor_instance_id="archivar",
            kristall_daten=kristall_daten,
            confirmation_count=confirmation_count,
            decay=0.0,  # Crystallized signals have no decay
            half_life_s=half_life_s,
            created_at=current_time,
            last_updated_at=current_time,
        )

        self._crystals[crystal_id] = crystal

    def get_crystals(self) -> list[WissensKristall]:
        """Get all crystals."""
        return list(self._crystals.values())

    def get_all_signals(self) -> list[SignalEvent]:
        """Get all signals across all coordinates."""
        all_signals = []
        for stack in self._signal_stacks.values():
            all_signals.extend(stack)
        return all_signals
