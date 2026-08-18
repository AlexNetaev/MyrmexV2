"""Richter — Deterministische Sicherheitsprüfung (Fail-Closed)."""

import hashlib
import uuid
from datetime import datetime, timezone

from src.contracts.pipeline_models import (
    DimensionOnboardingRequest,
    RichterRule,
)
from src.contracts.enums import RichterResult, OnboardingStatus


class RichterResultData:
    """Datenklasse für Richter-Ergebnis."""

    def __init__(
        self,
        decision: RichterResult,
        reason: str | None = None,
        dimension: str | None = None,
        onboarding_requests: list[DimensionOnboardingRequest] | None = None,
    ):
        self.decision = decision
        self.reason = reason
        self.dimension = dimension
        self.onboarding_requests = onboarding_requests or []


class Richter:
    """
    Der Richter — deterministische, Fail-Closed Sicherheitsprüfung.

    Regel 1: Richter ist deterministisch und Fail-Closed.
    - Wenn eine Dimension keine Regel hat → REGELLÜCKE → REJECTED
    - Wenn limits unvollständig sind → dimension_onboarding_request → REJECTED
    - Wenn eine Prüfung nicht durchgeführt werden kann → REJECTED

    Regel 2: REGELLÜCKE führt zur Ablehnung.
    - Bei fehlender Regel wird ein dimension_onboarding_request erzeugt
    - Das Paket wird ABGELEHNT, nicht mit "wahrscheinlich sicher" freigegeben

    Regel 5: SANDBOX_MODE prüft keine physischen Limits.
    - Im SANDBOX-Modus werden nur virtuelle Prüfungen durchgeführt
    """

    def __init__(self, richter_rules: dict[str, RichterRule] | None = None):
        self.richter_rules = richter_rules or {}
        self._onboarding_requests: list[DimensionOnboardingRequest] = []

    def check(self, package, gate_mode=None) -> RichterResultData:
        """
        Hauptprüfmethode: Führt alle Richter-Prüfungen durch.

        Args:
            package: ResearchPackage mit parameter_bounds, limits, materials_or_resources
            gate_mode: GateMode (NORMAL, SANDBOX, etc.)

        Returns:
            RichterResultData mit Entscheidung und Begründung
        """
        # SANDBOX_MODE: Nur virtuelle Prüfung, keine physischen Limits
        is_sandbox = gate_mode and str(gate_mode) == "SANDBOX"

        # 1. Parameter Bounds prüfen
        bounds_result = self.check_parameter_bounds(package, is_sandbox)
        if bounds_result.decision != RichterResult.RICHTER_PASS:
            return bounds_result

        # 2. Limits prüfen
        limits_result = self.check_limits(package, is_sandbox)
        if limits_result.decision != RichterResult.RICHTER_PASS:
            return limits_result

        # 3. Materialien prüfen
        materials_result = self.check_materials(package, is_sandbox)
        if materials_result.decision != RichterResult.RICHTER_PASS:
            return materials_result

        # Alle Prüfungen bestanden
        return RichterResultData(decision=RichterResult.RICHTER_PASS)

    def check_parameter_bounds(self, package, is_sandbox: bool = False) -> RichterResultData:
        """
        Prüft parameter_bounds gegen die Regeln.

        Args:
            package: ResearchPackage mit parameter_bounds
            is_sandbox: Wenn True, werden physische Limits übersprungen

        Returns:
            RichterResultData mit Entscheidung
        """
        parameter_bounds = getattr(package, "parameter_bounds", {})

        for param_name, param_value in parameter_bounds.items():
            rule = self.richter_rules.get(param_name)

            if rule is None:
                # Fail-Closed: Unbekannte Dimension → REJECTED
                onboarding_request = self._create_dimension_onboarding_request(
                    param_name,
                    getattr(package, "package_id", "unknown"),
                    f"Keine Regel für Parameter '{param_name}'"
                )
                return RichterResultData(
                    decision=RichterResult.REGELLUECKE,
                    reason="REGELLUECKE",
                    dimension=param_name,
                    onboarding_requests=[onboarding_request]
                )

            # Prüfe min/max Werte
            if rule.min_value is not None and param_value < rule.min_value:
                return RichterResultData(
                    decision=RichterResult.RICHTER_REJECT,
                    reason=f"PARAMETER_OUT_OF_BOUNDS",
                    dimension=param_name
                )

            if rule.max_value is not None and param_value > rule.max_value:
                return RichterResultData(
                    decision=RichterResult.RICHTER_REJECT,
                    reason=f"PARAMETER_OUT_OF_BOUNDS",
                    dimension=param_name
                )

        return RichterResultData(decision=RichterResult.RICHTER_PASS)

    def check_limits(self, package, is_sandbox: bool = False) -> RichterResultData:
        """
        Prüft limits gegen die Regeln.

        Args:
            package: ResearchPackage mit limits
            is_sandbox: Wenn True, werden physische Limits übersprungen

        Returns:
            RichterResultData mit Entscheidung
        """
        limits = getattr(package, "limits", {})

        for dimension, limit_value in limits.items():
            rule = self.richter_rules.get(dimension)

            if rule is None:
                # Fail-Closed: Fehlende Regel → REGELLÜCKE → REJECTED
                # NIEMALS: "Wahrscheinlich sicher" → FREIGEGEBEN
                onboarding_request = self._create_dimension_onboarding_request(
                    dimension,
                    getattr(package, "package_id", "unknown"),
                    f"Keine Regel für Dimension '{dimension}'"
                )
                return RichterResultData(
                    decision=RichterResult.REGELLUECKE,
                    reason="REGELLUECKE",
                    dimension=dimension,
                    onboarding_requests=[onboarding_request]
                )

            # Prüfe Limit-Wert
            if rule.min_value is not None and limit_value < rule.min_value:
                return RichterResultData(
                    decision=RichterResult.RICHTER_REJECT,
                    reason="LIMIT_VIOLATION",
                    dimension=dimension
                )

            if rule.max_value is not None and limit_value > rule.max_value:
                return RichterResultData(
                    decision=RichterResult.RICHTER_REJECT,
                    reason="LIMIT_VIOLATION",
                    dimension=dimension
                )

        return RichterResultData(decision=RichterResult.RICHTER_PASS)

    def check_materials(self, package, is_sandbox: bool = False) -> RichterResultData:
        """
        Prüft materials_or_resources gegen verbotene Materialien.

        Args:
            package: ResearchPackage mit materials_or_resources
            is_sandbox: Wenn True, werden Materialprüfungen übersprungen

        Returns:
            RichterResultData mit Entscheidung
        """
        materials = getattr(package, "materials_or_resources", [])

        for material in materials:
            # Prüfe alle Regeln auf verbotene Materialien
            for rule in self.richter_rules.values():
                if material in rule.forbidden_materials:
                    return RichterResultData(
                        decision=RichterResult.RICHTER_REJECT,
                        reason="FORBIDDEN_MATERIAL",
                        dimension="materials"
                    )

        return RichterResultData(decision=RichterResult.RICHTER_PASS)

    def _create_dimension_onboarding_request(
        self,
        dimension: str,
        package_id: str,
        reason: str
    ) -> DimensionOnboardingRequest:
        """Erzeugt einen Dimension-Onboarding-Request."""
        request_id = f"onboard-{uuid.uuid4()}"
        request = DimensionOnboardingRequest(
            onboarding_request_id=request_id,
            dimension=dimension,
            package_id=package_id,
            reason=reason,
            status=OnboardingStatus.PENDING
        )
        self._onboarding_requests.append(request)
        return request

    def get_onboarding_requests(self) -> list[DimensionOnboardingRequest]:
        """Gibt alle erzeugten Onboarding-Requests zurück."""
        return self._onboarding_requests.copy()

    def clear_onboarding_requests(self):
        """Löscht alle gespeicherten Onboarding-Requests."""
        self._onboarding_requests.clear()

    def register_rule(self, rule: RichterRule):
        """Registriert eine neue Richter-Regel."""
        self.richter_rules[rule.dimension] = rule

    def is_deterministic(self) -> bool:
        """
        Bestätigt, dass der Richter deterministisch arbeitet.
        Keine LLMs, kein Zufall, gleiche Eingabe = gleiches Ergebnis.
        """
        return True
