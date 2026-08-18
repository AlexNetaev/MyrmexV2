"""Tests für den Gate-Flow."""

import pytest
from src.gremium.sicherheitsrat.richter import Richter
from src.gremium.sicherheitsrat.seher import Seher
from src.gremium.sicherheitsrat.gate_flow import GateFlow
from src.contracts.pipeline_models import RichterRule
from src.contracts.enums import (
    GateMode,
    GateDecision,
    RichterResult,
    SeherResult,
)


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


def test_gate_flow_richter_pass_seher_pass():
    """Richter PASS + Seher PASS → FREIGEGEBEN."""
    # Arrange
    rules = {
        "temperature": RichterRule(
            dimension="temperature",
            min_value=0.0,
            max_value=100.0,
        )
    }
    richter = Richter(richter_rules=rules)
    seher = Seher()
    gate_flow = GateFlow(richter=richter, seher=seher)
    package = MockPackage(
        parameter_bounds={"temperature": 25.0},
        limits={"temperature": 50.0},
    )

    # Act
    gate_record = gate_flow.run_gate(package, gate_mode=GateMode.NORMAL)

    # Assert
    assert gate_record.richter_result == RichterResult.RICHTER_PASS
    assert gate_record.seher_result == SeherResult.SEHER_PASS
    assert gate_record.gate_decision == GateDecision.FREIGEGEBEN


def test_gate_flow_richter_reject():
    """Richter REJECT → ABGELEHNT."""
    # Arrange
    rules = {
        "temperature": RichterRule(
            dimension="temperature",
            min_value=0.0,
            max_value=100.0,
        )
    }
    richter = Richter(richter_rules=rules)
    gate_flow = GateFlow(richter=richter)
    package = MockPackage(
        parameter_bounds={"temperature": 150.0},  # Außerhalb
    )

    # Act
    gate_record = gate_flow.run_gate(package)

    # Assert
    assert gate_record.richter_result == RichterResult.RICHTER_REJECT
    assert gate_record.gate_decision == GateDecision.ABGELEHNT


def test_gate_flow_richter_regelluecke():
    """Richter REGELLÜCKE → ABGELEHNT + dimension_onboarding_request."""
    # Arrange
    richter = Richter(richter_rules={})  # Keine Regeln
    gate_flow = GateFlow(richter=richter)
    package = MockPackage(
        limits={"unknown_dimension": 42.0},
    )

    # Act
    gate_record = gate_flow.run_gate(package)

    # Assert
    assert gate_record.richter_result == RichterResult.REGELLUECKE
    assert gate_record.gate_decision == GateDecision.ABGELEHNT
    assert len(gate_record.dimension_onboarding_requests) > 0


def test_gate_flow_richter_pass_seher_veto():
    """Richter PASS + Seher VETO → DISPUTED (Phase 6b)."""
    # Arrange
    rules = {
        "temperature": RichterRule(
            dimension="temperature",
            min_value=0.0,
            max_value=100.0,
        )
    }
    richter = Richter(richter_rules=rules)

    class MockSeherWithVeto:
        def seher_check(self, package, kontext=None):
            return SeherResult.SEHER_VETO

    gate_flow = GateFlow(richter=richter, seher=MockSeherWithVeto())
    package = MockPackage(
        parameter_bounds={"temperature": 25.0},
        limits={"temperature": 50.0},
    )

    # Act
    gate_record = gate_flow.run_gate(package)

    # Assert
    assert gate_record.richter_result == RichterResult.RICHTER_PASS
    assert gate_record.seher_result == SeherResult.SEHER_VETO
    assert gate_record.gate_decision == GateDecision.DISPUTED


def test_gate_flow_sandbox_mode():
    """Regel 5: gate_mode=SANDBOX → FREIGEGEBEN, physical_execution_allowed=false."""
    # Arrange
    rules = {
        "temperature": RichterRule(
            dimension="temperature",
            min_value=0.0,
            max_value=100.0,
        )
    }
    richter = Richter(richter_rules=rules)
    gate_flow = GateFlow(richter=richter)
    package = MockPackage(
        parameter_bounds={"temperature": 25.0},
        limits={"temperature": 50.0},
    )

    # Act
    gate_record = gate_flow.run_gate(package, gate_mode=GateMode.SANDBOX)

    # Assert
    assert gate_record.gate_decision == GateDecision.FREIGEGEBEN
    assert gate_record.physical_execution_allowed is False


def test_gate_flow_high_risk_override_requires_refutation():
    """Regel 4: HIGH_RISK_OVERRIDE erfordert positive Widerlegung."""
    # Arrange
    rules = {
        "temperature": RichterRule(
            dimension="temperature",
            min_value=0.0,
            max_value=100.0,
        )
    }
    richter = Richter(richter_rules=rules)
    gate_flow = GateFlow(richter=richter)
    package = MockPackage(
        parameter_bounds={"temperature": 25.0},
        limits={"temperature": 50.0},
    )

    # Act
    gate_record = gate_flow.run_gate(package, gate_mode=GateMode.HIGH_RISK_OVERRIDE)

    # Assert
    assert gate_record.gate_mode == GateMode.HIGH_RISK_OVERRIDE
    # In Phase 6a: Einfach freigeben, in Phase 6b: Zusätzliche Prüfung


def test_gate_flow_fracture_diagnosis_in_quarantine():
    """Regel 4: FRACTURE_DIAGNOSIS erlaubt diagnostic-safe Ausführung."""
    # Arrange
    rules = {
        "temperature": RichterRule(
            dimension="temperature",
            min_value=0.0,
            max_value=100.0,
        )
    }
    richter = Richter(richter_rules=rules)
    gate_flow = GateFlow(richter=richter)
    package = MockPackage(
        parameter_bounds={"temperature": 25.0},
        limits={"temperature": 50.0},
    )

    # Act
    gate_record = gate_flow.run_gate(package, gate_mode=GateMode.FRACTURE_DIAGNOSIS)

    # Assert
    assert gate_record.gate_mode == GateMode.FRACTURE_DIAGNOSIS


def test_gate_record_has_valid_signature():
    """Regel 3: gate_record hat gültige SHA-256-Signatur."""
    # Arrange
    rules = {
        "temperature": RichterRule(
            dimension="temperature",
            min_value=0.0,
            max_value=100.0,
        )
    }
    richter = Richter(richter_rules=rules)
    gate_flow = GateFlow(richter=richter)
    package = MockPackage(
        parameter_bounds={"temperature": 25.0},
        limits={"temperature": 50.0},
    )

    # Act
    gate_record = gate_flow.run_gate(package)

    # Assert
    assert len(gate_record.signature) == 64  # SHA-256 Hex-Länge
    assert gate_flow.verify_signature(gate_record) is True


def test_gate_record_signature_is_verifiable():
    """Regel 3: Dispatcher kann die Signatur verifizieren."""
    # Arrange
    rules = {
        "temperature": RichterRule(
            dimension="temperature",
            min_value=0.0,
            max_value=100.0,
        )
    }
    richter = Richter(richter_rules=rules)
    gate_flow = GateFlow(richter=richter)
    package = MockPackage(
        parameter_bounds={"temperature": 25.0},
        limits={"temperature": 50.0},
    )

    # Act
    gate_record = gate_flow.run_gate(package)

    # Assert
    assert gate_flow.verify_signature(gate_record) is True


def test_gate_record_signature_tampering_detected():
    """Regel 3: Manipulierte Signatur wird erkannt."""
    # Arrange
    rules = {
        "temperature": RichterRule(
            dimension="temperature",
            min_value=0.0,
            max_value=100.0,
        )
    }
    richter = Richter(richter_rules=rules)
    gate_flow = GateFlow(richter=richter)
    package = MockPackage(
        parameter_bounds={"temperature": 25.0},
        limits={"temperature": 50.0},
    )

    # Act
    gate_record = gate_flow.run_gate(package)

    # Tamper mit der Signatur
    original_signature = gate_record.signature
    gate_record.signature = "tampered_signature"

    # Assert
    assert gate_flow.verify_signature(gate_record) is False


def test_gate_mode_consistency():
    """Regel 3: gate_mode ist konsistent mit dem Gate-Ergebnis."""
    # Arrange
    rules = {
        "temperature": RichterRule(
            dimension="temperature",
            min_value=0.0,
            max_value=100.0,
        )
    }
    richter = Richter(richter_rules=rules)
    gate_flow = GateFlow(richter=richter)
    package = MockPackage(
        parameter_bounds={"temperature": 25.0},
        limits={"temperature": 50.0},
    )

    # Act: Verschiedene Gate-Modes testen
    for mode in [GateMode.NORMAL, GateMode.SANDBOX, GateMode.FRACTURE_DIAGNOSIS, GateMode.HIGH_RISK_OVERRIDE]:
        gate_record = gate_flow.run_gate(package, gate_mode=mode)

        # Assert
        assert gate_record.gate_mode == mode
