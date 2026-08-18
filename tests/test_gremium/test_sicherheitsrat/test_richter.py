"""Tests für den Richter (Fail-Closed Sicherheitsprüfung)."""

import pytest
from src.gremium.sicherheitsrat.richter import Richter, RichterResultData
from src.contracts.pipeline_models import RichterRule
from src.contracts.enums import RichterResult


class MockPackage:
    """Mock-Paket für Tests."""

    def __init__(
        self,
        package_id="pkg-001",
        zyklus_id="zyklus-001",
        parameter_bounds=None,
        limits=None,
        materials_or_resources=None,
    ):
        self.package_id = package_id
        self.zyklus_id = zyklus_id
        self.parameter_bounds = parameter_bounds or {}
        self.limits = limits or {}
        self.materials_or_resources = materials_or_resources or []


def test_richter_passes_valid_package():
    """Regel 1: Valid package → RICHTER_PASS."""
    # Arrange
    rules = {
        "temperature": RichterRule(
            dimension="temperature",
            min_value=0.0,
            max_value=100.0,
            forbidden_materials=[],
        )
    }
    richter = Richter(richter_rules=rules)
    package = MockPackage(
        parameter_bounds={"temperature": 25.0},
        limits={"temperature": 50.0},
    )

    # Act
    result = richter.check(package)

    # Assert
    assert result.decision == RichterResult.RICHTER_PASS


def test_richter_rejects_out_of_bounds():
    """Regel 1: parameter_bounds außerhalb der Regeln → RICHTER_REJECT."""
    # Arrange
    rules = {
        "temperature": RichterRule(
            dimension="temperature",
            min_value=0.0,
            max_value=100.0,
            forbidden_materials=[],
        )
    }
    richter = Richter(richter_rules=rules)
    package = MockPackage(
        parameter_bounds={"temperature": 150.0},  # Außerhalb des Limits
    )

    # Act
    result = richter.check(package)

    # Assert
    assert result.decision == RichterResult.RICHTER_REJECT
    assert result.reason == "PARAMETER_OUT_OF_BOUNDS"


def test_richter_rejects_forbidden_material():
    """Regel 1: Verbotene Substanz → RICHTER_REJECT."""
    # Arrange
    rules = {
        "materials": RichterRule(
            dimension="materials",
            forbidden_materials=["TOXIC_SUBSTANCE"],
        )
    }
    richter = Richter(richter_rules=rules)
    package = MockPackage(
        materials_or_resources=["TOXIC_SUBSTANCE"],
    )

    # Act
    result = richter.check(package)

    # Assert
    assert result.decision == RichterResult.RICHTER_REJECT
    assert result.reason == "FORBIDDEN_MATERIAL"


def test_richter_fail_closed_on_missing_rule():
    """Regel 1 (KRITISCH): Fehlende Regel → REGELLÜCKE → REJECTED."""
    # Arrange
    # KEINE Regeln registriert
    richter = Richter(richter_rules={})
    package = MockPackage(
        limits={"unknown_dimension": 42.0},
    )

    # Act
    result = richter.check(package)

    # Assert
    assert result.decision == RichterResult.REGELLUECKE
    assert result.reason == "REGELLUECKE"
    assert len(result.onboarding_requests) > 0


def test_richter_fail_closed_on_unknown_dimension():
    """Regel 1 (KRITISCH): Unbekannte Dimension → REJECTED, nicht FREIGEGEBEN."""
    # Arrange
    rules = {
        "temperature": RichterRule(
            dimension="temperature",
            min_value=0.0,
            max_value=100.0,
        )
    }
    richter = Richter(richter_rules=rules)
    package = MockPackage(
        limits={"unknown_dimension": 42.0},  # Keine Regel dafür
    )

    # Act
    result = richter.check(package)

    # Assert
    assert result.decision == RichterResult.REGELLUECKE
    assert result.dimension == "unknown_dimension"


def test_richter_generates_dimension_onboarding_request():
    """Regel 2: REGELLÜCKE erzeugt dimension_onboarding_request."""
    # Arrange
    richter = Richter(richter_rules={})
    package = MockPackage(
        limits={"new_dimension": 10.0},
    )

    # Act
    result = richter.check(package)

    # Assert
    assert result.decision == RichterResult.REGELLUECKE
    assert len(result.onboarding_requests) == 1
    onboarding = result.onboarding_requests[0]
    assert onboarding.dimension == "new_dimension"
    assert onboarding.package_id == package.package_id
    assert "Keine Regel" in onboarding.reason


def test_richter_rejects_incomplete_limits():
    """Regel 2: Unvollständige limits → REJECTED."""
    # Arrange
    rules = {
        "temperature": RichterRule(
            dimension="temperature",
            min_value=0.0,
            max_value=100.0,
        )
    }
    richter = Richter(richter_rules=rules)
    package = MockPackage(
        limits={
            "temperature": 50.0,
            "pressure": 1.0,  # Keine Regel für pressure
        },
    )

    # Act
    result = richter.check(package)

    # Assert
    assert result.decision == RichterResult.REGELLUECKE
    assert result.dimension == "pressure"


def test_richter_is_deterministic():
    """Regel 1: Gleiche Eingabe → gleiches Ergebnis (kein LLM, kein Zufall)."""
    # Arrange
    rules = {
        "temperature": RichterRule(
            dimension="temperature",
            min_value=0.0,
            max_value=100.0,
        )
    }
    richter = Richter(richter_rules=rules)
    package = MockPackage(
        parameter_bounds={"temperature": 25.0},
        limits={"temperature": 50.0},
    )

    # Act: Mehrfache Ausführung
    result1 = richter.check(package)
    result2 = richter.check(package)
    result3 = richter.check(package)

    # Assert
    assert result1.decision == result2.decision == result3.decision
    assert result1.decision == RichterResult.RICHTER_PASS
    assert richter.is_deterministic()


def test_richter_sandbox_mode_no_physical_limits():
    """Regel 5: SANDBOX_MODE prüft keine physischen Limits."""
    # Arrange
    from src.contracts.enums import GateMode

    rules = {
        "temperature": RichterRule(
            dimension="temperature",
            min_value=0.0,
            max_value=100.0,
        )
    }
    richter = Richter(richter_rules=rules)
    package = MockPackage(
        parameter_bounds={"temperature": 25.0},
        limits={"temperature": 50.0},
    )

    # Act: SANDBOX_MODE
    result = richter.check(package, gate_mode=GateMode.SANDBOX)

    # Assert
    assert result.decision == RichterResult.RICHTER_PASS


def test_richter_register_rule():
    """Testet das Registrieren neuer Regeln."""
    # Arrange
    richter = Richter(richter_rules={})

    # Act
    new_rule = RichterRule(
        dimension="pressure",
        min_value=0.0,
        max_value=10.0,
    )
    richter.register_rule(new_rule)

    # Assert
    assert "pressure" in richter.richter_rules
    assert richter.richter_rules["pressure"] == new_rule
