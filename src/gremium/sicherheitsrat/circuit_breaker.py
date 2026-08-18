"""Circuit-Breaker für den Seher — Schutz vor Fehlverhalten."""

from collections import deque
from datetime import datetime, timezone
from typing import Any

from src.contracts.enums import CircuitBreakerState, SeherResult, AppealDecision
from src.contracts.pipeline_models import CircuitBreakerMetrics, CircuitBreakerAuditEvent


class CircuitBreaker:
    """
    Circuit-Breaker überwacht den Seher und schützt vor Fehlverhalten.

    Regel 3: Circuit-Breaker mit vier Metriken:
    - invalid_veto_rate > 0.3 → Alert an Kanzler
    - false_block_rate > 0.5 → SHADOW_MODE
    - appeal_success_rate > 0.7 → TEMP_SUSPENDED
    - Manuelle Eskalation → PERMANENT_SUSPENDED

    Messfenster: window_size = 100, minimum_sample_size = 20
    Rückkehr zu NORMAL erfordert Hysterese (2 Fenster unter Schwelle) + manuelle Bestätigung
    """

    WINDOW_SIZE = 100
    MINIMUM_SAMPLE_SIZE = 20
    INVALID_VETO_THRESHOLD = 0.3
    FALSE_BLOCK_THRESHOLD = 0.5
    APPEAL_SUCCESS_THRESHOLD = 0.7
    HYSTERESIS_WINDOWS = 2

    def __init__(self):
        self.state = CircuitBreakerState.NORMAL
        self.metrics_window: deque[dict[str, Any]] = deque(maxlen=self.WINDOW_SIZE)
        self.consecutive_below_threshold = 0
        self.audit_events: list[CircuitBreakerAuditEvent] = []
        self.kanzler_alerts: list[dict] = []

    def record_decision(
        self,
        decision: SeherResult,
        was_false_block: bool = False,
        was_invalid_veto: bool = False,
        was_appeal_successful: bool = False
    ):
        """
        Protokolliert eine Seher-Entscheidung für Metriken.

        Args:
            decision: Seher-Entscheidung
            was_false_block: Ob die Blockade falsch war (Berufung erfolgreich)
            was_invalid_veto: Ob das Veto ungültig war
            was_appeal_successful: Ob eine Berufung erfolgreich war
        """
        self.metrics_window.append({
            "decision": decision,
            "was_false_block": was_false_block,
            "was_invalid_veto": was_invalid_veto,
            "was_appeal_successful": was_appeal_successful,
            "timestamp": datetime.now(timezone.utc)
        })
        self._evaluate_thresholds()

    def _calculate_metrics(self) -> CircuitBreakerMetrics:
        """Berechnet aktuelle Metriken aus dem Fenster."""
        sample_size = len(self.metrics_window)
        if sample_size == 0:
            return CircuitBreakerMetrics(
                window_size=self.WINDOW_SIZE,
                sample_size=0
            )

        invalid_vetos = sum(1 for m in self.metrics_window if m["was_invalid_veto"])
        false_blocks = sum(1 for m in self.metrics_window if m["was_false_block"])
        successful_appeals = sum(1 for m in self.metrics_window if m["was_appeal_successful"])

        return CircuitBreakerMetrics(
            invalid_veto_rate=invalid_vetos / sample_size if sample_size > 0 else 0.0,
            false_block_rate=false_blocks / sample_size if sample_size > 0 else 0.0,
            appeal_success_rate=successful_appeals / sample_size if sample_size > 0 else 0.0,
            window_size=self.WINDOW_SIZE,
            sample_size=sample_size
        )

    def _evaluate_thresholds(self):
        """Überprüft Schwellwerte und führt Zustandswechsel durch."""
        if len(self.metrics_window) < self.MINIMUM_SAMPLE_SIZE:
            return  # Keine automatische Entscheidung unter Mindeststichprobe

        metrics = self._calculate_metrics()

        # Invalid Veto Rate → Alert an Kanzler (kein Zustandswechsel)
        if metrics.invalid_veto_rate > self.INVALID_VETO_THRESHOLD:
            self._alert_kanzler("invalid_veto_rate", metrics.invalid_veto_rate)

        # False Block Rate → SHADOW_MODE
        if metrics.false_block_rate > self.FALSE_BLOCK_THRESHOLD:
            if self.state == CircuitBreakerState.NORMAL:
                self._transition_to(
                    CircuitBreakerState.SHADOW_MODE,
                    "false_block_rate",
                    metrics.false_block_rate
                )

        # Appeal Success Rate → TEMP_SUSPENDED
        if metrics.appeal_success_rate > self.APPEAL_SUCCESS_THRESHOLD:
            if self.state == CircuitBreakerState.NORMAL:
                self._transition_to(
                    CircuitBreakerState.TEMP_SUSPENDED,
                    "appeal_success_rate",
                    metrics.appeal_success_rate
                )

    def _alert_kanzler(self, metric_name: str, metric_value: float):
        """Sendet einen Alert an den Kanzler."""
        alert = {
            "metric_name": metric_name,
            "metric_value": metric_value,
            "threshold": self.INVALID_VETO_THRESHOLD,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "state": self.state.value
        }
        self.kanzler_alerts.append(alert)

    def _transition_to(
        self,
        new_state: CircuitBreakerState,
        trigger: str,
        metric_value: float,
        authority: str | None = None
    ):
        """Führt einen Zustandswechsel durch."""
        old_state = self.state
        if old_state == new_state:
            return

        self.state = new_state
        self.consecutive_below_threshold = 0

        audit_event = CircuitBreakerAuditEvent(
            old_state=old_state,
            new_state=new_state,
            trigger=trigger,
            metric_name=trigger.split("_")[0] if "_" in trigger else trigger,
            metric_value=metric_value,
            window_size=self.WINDOW_SIZE,
            sample_size=len(self.metrics_window),
            timestamp=datetime.now(timezone.utc).isoformat(),
            authority=authority
        )
        self.audit_events.append(audit_event)

    def _check_hysteresis_for_recovery(self, current_value: float, threshold: float) -> bool:
        """
        Prüft Hysterese für Rückkehr zu NORMAL.

        Regel 3: Rückkehr erfordert 2 Fenster unter Schwelle + manuelle Bestätigung.
        """
        if current_value < threshold:
            self.consecutive_below_threshold += 1
        else:
            self.consecutive_below_threshold = 0

        return self.consecutive_below_threshold >= self.HYSTERESIS_WINDOWS

    def request_recovery(self, authority: str) -> bool:
        """
        Beantragt manuelle Wiederherstellung zu NORMAL.

        Args:
            authority: Autorität, die die Wiederherstellung beantragt

        Returns:
            bool: True wenn erfolgreich
        """
        if self.state == CircuitBreakerState.PERMANENT_SUSPENDED:
            return False  # Keine automatische Rückkehr von PERMANENT_SUSPENDED

        metrics = self._calculate_metrics()

        # Bestimme relevanten Schwellwert basierend auf aktuellem Zustand
        if self.state == CircuitBreakerState.SHADOW_MODE:
            threshold = self.FALSE_BLOCK_THRESHOLD
            current_value = metrics.false_block_rate
        elif self.state == CircuitBreakerState.TEMP_SUSPENDED:
            threshold = self.APPEAL_SUCCESS_THRESHOLD
            current_value = metrics.appeal_success_rate
        else:
            return True  # Bereits NORMAL

        if self._check_hysteresis_for_recovery(current_value, threshold):
            self._transition_to(
                CircuitBreakerState.NORMAL,
                "manual_recovery",
                0.0,
                authority
            )
            return True
        return False

    def escalate_to_permanent_suspended(self, authority: str):
        """
        Eskaliert zu PERMANENT_SUSPENDED (nur manuell).

        Args:
            authority: Autorität, die die Eskalation durchführt
        """
        self._transition_to(
            CircuitBreakerState.PERMANENT_SUSPENDED,
            "manual_escalation",
            0.0,
            authority
        )

    def is_seher_blocking(self) -> bool:
        """
        Prüft ob der Seher blockierend wirkt.

        Returns:
            bool: True wenn Seher-Ergebnisse als Blockade gewertet werden
        """
        return self.state in [
            CircuitBreakerState.NORMAL,
            CircuitBreakerState.TEMP_SUSPENDED
        ]

    def is_seher_skipped(self) -> bool:
        """
        Prüft ob der Seher übersprungen wird.

        Returns:
            bool: True wenn Seher komplett übersprungen wird
        """
        return self.state in [
            CircuitBreakerState.TEMP_SUSPENDED,
            CircuitBreakerState.PERMANENT_SUSPENDED
        ]

    def get_metrics(self) -> CircuitBreakerMetrics:
        """Gibt aktuelle Metriken zurück."""
        return self._calculate_metrics()

    def get_audit_events(self) -> list[CircuitBreakerAuditEvent]:
        """Gibt Audit-Events zurück."""
        return self.audit_events.copy()

    def get_kanzler_alerts(self) -> list[dict]:
        """Gibt Kanzler-Alerts zurück."""
        return self.kanzler_alerts.copy()

    def reset(self):
        """Setzt den Circuit-Breaker zurück (für Tests)."""
        self.state = CircuitBreakerState.NORMAL
        self.metrics_window.clear()
        self.consecutive_below_threshold = 0
        self.audit_events.clear()
        self.kanzler_alerts.clear()
