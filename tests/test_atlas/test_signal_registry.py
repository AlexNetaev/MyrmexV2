"""Tests for Signal Registry resolution, crystallization, and decay."""

import time
from datetime import datetime, timezone

import pytest

from src.atlas.signal_registry import SignalRegistry
from src.contracts.atlas_models import SignalEvent
from src.contracts.enums import SignalSeverity, SignalType


def _create_signal(
    signal_id: str,
    coordinate: str = "pkg-001:zyklus-001",
    signal_type: SignalType = SignalType.SCIENTIFIC,
    severity: SignalSeverity = SignalSeverity.WHITE,
) -> SignalEvent:
    """Helper to create a SignalEvent."""
    return SignalEvent(
        signal_id=signal_id,
        signal_type=signal_type,
        source_package_id="pkg-001",
        source_zyklus_id="zyklus-001",
        timestamp=datetime.now(timezone.utc).isoformat(),
        payload={"value": 42},
        severity=severity,
    )


def test_signal_resolution_priority():
    """🟥 + 🟩 → 🟥 gewinnt (höchste Priorität)."""
    registry = SignalRegistry()

    # Erstes Signal: GREEN (niedrige Priorität)
    green_signal = _create_signal("sig-green", severity=SignalSeverity.GREEN)
    registry.append_signal(green_signal)

    resolved_before = registry.resolve_coordinate("pkg-001:zyklus-001")
    assert resolved_before is not None
    assert resolved_before.severity == SignalSeverity.GREEN

    # Zweites Signal: RED (höchste Priorität) - same coordinate
    red_signal = _create_signal("sig-red", coordinate="pkg-001:zyklus-001", severity=SignalSeverity.RED)
    registry.append_signal(red_signal)

    resolved_after = registry.resolve_coordinate("pkg-001:zyklus-001")
    assert resolved_after is not None
    assert resolved_after.severity == SignalSeverity.RED


def test_crystallization_after_three_confirmations():
    """confirmation_count >= 3 → decay = 0."""
    registry = SignalRegistry()

    # Drei Signale für dieselbe Koordinate
    for i in range(3):
        signal = _create_signal(f"sig-{i}", coordinate="coord-crystal")
        registry.append_signal(signal)

    # Kristall sollte erzeugt worden sein mit confirmation_count >= 3 und decay = 0
    crystals = registry.get_crystals()
    assert len(crystals) >= 1

    crystal = crystals[0]
    assert crystal.confirmation_count >= 3
    assert crystal.decay == 0.0


def test_signal_decay_over_time():
    """strength = initial × (0.5 ^ (age / half_life))."""
    registry = SignalRegistry()

    # Signal mit kurzer half_life für schnellen Test
    signal = _create_signal("sig-decay", coordinate="pkg-001:zyklus-decay")
    registry.append_signal(signal, half_life_s=0.1)  # 100ms half-life

    # Warte etwas
    time.sleep(0.15)

    # Stärke sollte abgenommen haben
    resolved = registry.resolve_coordinate("pkg-001:zyklus-decay")
    assert resolved is not None
    assert resolved.payload.get("strength", 1.0) < 1.0


def test_signal_stack_is_append_only():
    """Signal-Stack ist append-only, keine Mutation."""
    registry = SignalRegistry()

    # Erstes Signal
    signal1 = _create_signal("sig-1", coordinate="pkg-001:zyklus-stack")
    registry.append_signal(signal1)

    stack_before = registry.get_signal_stack("pkg-001:zyklus-stack").copy()
    assert len(stack_before) == 1

    # Zweites Signal
    signal2 = _create_signal("sig-2", coordinate="pkg-001:zyklus-stack")
    registry.append_signal(signal2)

    stack_after = registry.get_signal_stack("pkg-001:zyklus-stack")
    assert len(stack_after) == 2

    # Erstes Signal muss unverändert sein
    assert stack_after[0].signal_id == "sig-1"
    assert stack_after[1].signal_id == "sig-2"
