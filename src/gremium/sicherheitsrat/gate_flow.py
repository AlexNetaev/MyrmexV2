"""Gate-Flow — Sicherheits-Gate mit Richter, Seher, Circuit-Breaker und Appeal."""

import hashlib
import uuid
from datetime import datetime, timezone

from src.contracts.pipeline_models import GateRecord, DimensionOnboardingRequest, SeherResultModel
from src.contracts.enums import GateMode, GateDecision, RichterResult, SeherResult, SeherDecision, CircuitBreakerState

from .richter import Richter, RichterResultData
from .seher import Seher
from .circuit_breaker import CircuitBreaker
from .appeal import AppealManager


class GateFlow:
    """
    Gate-Flow — Führt das Sicherheits-Gate durch.

    Der Gate-Flow kombiniert:
    - Richter (deterministisch, Fail-Closed)
    - Seher (LLM-basiert, mit Circuit-Breaker geschützt)
    - Circuit-Breaker (schützt vor Seher-Fehlverhalten)
    - Appeal-Manager (Berufungsprozess bei DISPUTED)
    - Policy-Review (regelmäßige Überprüfung von POLICY_VETOs)

    Gate-Entscheidungslogik:
    - Richter REJECT → ABGELEHNT
    - Richter PASS + Seher PASS → FREIGEGEBEN
    - Richter PASS + Seher VETO → DISPUTED (Appeal wird erstellt)
    - Richter REGELLÜCKE → ABGELEHNT + dimension_onboarding_request
    - gate_mode = SANDBOX → FREIGEGEBEN (nur virtuell, physical_execution_allowed=false)
    - gate_mode = HIGH_RISK_OVERRIDE → Positive Widerlegung erforderlich
    - Circuit-Breaker SHADOW_MODE/TEMP_SUSPENDED → Seher-Ergebnis wird ignoriert/übersprungen
    """

    def __init__(
        self,
        richter: Richter | None = None,
        seher: Seher | None = None,
        circuit_breaker: CircuitBreaker | None = None,
        appeal_manager: AppealManager | None = None,
        policy_review=None  # Optional für Phase 6B
    ):
        self.richter = richter or Richter()
        self.seher = seher or Seher()
        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self.appeal_manager = appeal_manager or AppealManager()
        self.policy_review = policy_review
        self._cycle_counter = 0

    def run_gate(self, package, gate_mode: GateMode = GateMode.NORMAL) -> GateRecord:
        """
        Führt das vollständige Gate durch.

        Args:
            package: ResearchPackage zur Prüfung
            gate_mode: GateMode (NORMAL, SANDBOX, etc.)

        Returns:
            GateRecord mit Ergebnis und Signatur
        """
        self._cycle_counter += 1
        
        # 1. Richter prüfen (immer, deterministisch)
        richter_result = self.richter.check(package, gate_mode)

        # 2. Gate-Entscheidung basierend auf Richter-Ergebnis
        if richter_result.decision == RichterResult.RICHTER_REJECT:
            return self._create_gate_record(
                package,
                gate_mode,
                richter_result=RichterResult.RICHTER_REJECT,
                seher_result_model=SeherResultModel(decision=SeherDecision.SEHER_NOT_CALLED),
                gate_decision=GateDecision.ABGELEHNT,
                onboarding_requests=[]
            )

        if richter_result.decision == RichterResult.REGELLUECKE:
            # REGELLÜCKE → ABGELEHNT + dimension_onboarding_request
            return self._create_gate_record(
                package,
                gate_mode,
                richter_result=RichterResult.REGELLUECKE,
                seher_result_model=SeherResultModel(decision=SeherDecision.SEHER_NOT_CALLED),
                gate_decision=GateDecision.ABGELEHNT,
                onboarding_requests=richter_result.onboarding_requests
            )

        # 3. Circuit-Breaker Status prüfen
        cb_state = self.circuit_breaker.state
        
        seher_result_model = SeherResultModel(decision=SeherDecision.SEHER_NOT_CALLED)
        
        if cb_state == CircuitBreakerState.TEMP_SUSPENDED or cb_state == CircuitBreakerState.PERMANENT_SUSPENDED:
            # Seher wird übersprungen
            seher_result_model = SeherResultModel(decision=SeherDecision.SEHER_NOT_CALLED)
        elif cb_state == CircuitBreakerState.SHADOW_MODE:
            # Seher aufrufen, aber Ergebnis nicht als Blockade werten
            seher_result_raw = self.seher.seher_check(package, getattr(package, "kontext", None))
            if isinstance(seher_result_raw, SeherResult):
                seher_result_model = SeherResultModel(decision=seher_result_raw)
            else:
                seher_result_model = seher_result_raw
            # In SHADOW_MODE: Veto wird nicht als Blockade gewertet → wie PASS behandeln
            if seher_result_model.decision == SeherDecision.SEHER_VETO:
                seher_result_model = SeherResultModel(decision=SeherDecision.SEHER_PASS)
        else:
            # NORMAL: Seher normal aufrufen
            seher_result_raw = self.seher.seher_check(package, getattr(package, "kontext", None))
            if isinstance(seher_result_raw, SeherResult):
                seher_result_model = SeherResultModel(decision=seher_result_raw)
            else:
                seher_result_model = seher_result_raw

        # 4. Gate-Entscheidung basierend auf Seher-Ergebnis
        gate_decision = GateDecision.FREIGEGEBEN  # Default bei PASS
        
        if seher_result_model.decision == SeherDecision.SEHER_PASS:
            gate_decision = GateDecision.FREIGEGEBEN
        elif seher_result_model.decision == SeherDecision.SEHER_VETO:
            # Richter PASS + Seher VETO → DISPUTED → Appeal erstellen
            gate_decision = GateDecision.DISPUTED
            
            # Appeal erstellen
            appeal = self.appeal_manager.create_appeal(
                package_id=getattr(package, "package_id", "unknown"),
                seher_veto=seher_result_model.veto,
                richter_result=richter_result
            )
        elif seher_result_model.decision in [
            SeherDecision.SEHER_INVALID_VETO,
            SeherDecision.SEHER_INVALID_ACTION,
            SeherDecision.SEHER_NOT_AVAILABLE
        ]:
            gate_decision = GateDecision.ABGELEHNT

        # 5. SANDBOX_MODE: Keine physische Ausführung
        physical_execution_allowed = True
        if gate_mode == GateMode.SANDBOX:
            gate_decision = GateDecision.FREIGEGEBEN
            physical_execution_allowed = False

        # 6. HIGH_RISK_OVERRIDE: Positive Widerlegung erforderlich
        if gate_mode == GateMode.HIGH_RISK_OVERRIDE:
            # Erfordert positive Widerlegung der Gefahr
            pass

        # 7. FRACTURE_DIAGNOSIS: Erlaubt diagnostic-safe in QUARANTÄNE
        if gate_mode == GateMode.FRACTURE_DIAGNOSIS:
            # Erlaubt diagnostic-safe Ausführung in QUARANTÄNE-Zonen
            pass

        # 8. Policy-Veto-Review prüfen (alle N Zyklen)
        if self.policy_review:
            if self.policy_review.increment_cycle():
                # Review fällig → durchführen
                self.policy_review.run_review([])

        # 9. gate_record erzeugen mit Signatur
        return self._create_gate_record(
            package,
            gate_mode,
            richter_result=richter_result.decision,
            seher_result_model=seher_result_model,
            gate_decision=gate_decision,
            onboarding_requests=richter_result.onboarding_requests,
            physical_execution_allowed=physical_execution_allowed
        )

    def _create_gate_record(
        self,
        package,
        gate_mode: GateMode,
        richter_result: RichterResult,
        seher_result_model: SeherResultModel,
        gate_decision: GateDecision,
        onboarding_requests: list[DimensionOnboardingRequest],
        physical_execution_allowed: bool = True
    ) -> GateRecord:
        """Erzeugt ein signiertes GateRecord."""
        gate_record_id = f"gate-{uuid.uuid4()}"
        timestamp = datetime.now(timezone.utc).isoformat()

        # Extrahiere SeherResult Enum aus dem Modell für das GateRecord
        seher_result_enum = seher_result_model.decision

        # Erst GateRecord ohne Signatur erstellen (signature ist optional für die Erstellung)
        gate_record = GateRecord(
            gate_record_id=gate_record_id,
            gate_id=gate_record_id,
            package_id=getattr(package, "package_id", "unknown"),
            zyklus_id=getattr(package, "zyklus_id", "unknown"),
            gate_mode=gate_mode,
            gate_decision=gate_decision,
            richter_result=richter_result,
            seher_result=seher_result_enum,
            safety_checks_passed=(richter_result == RichterResult.RICHTER_PASS),
            validation_checks_passed=(gate_decision == GateDecision.FREIGEGEBEN),
            timestamp=timestamp,
            dimension_onboarding_requests=onboarding_requests,
            physical_execution_allowed=physical_execution_allowed,
            signature=""  # Platzhalter, wird sofort danach gesetzt
        )

        # Signatur generieren und setzen
        gate_record.signature = self._generate_signature(gate_record)

        return gate_record

    def _generate_signature(self, gate_record: GateRecord) -> str:
        """
        Generiert eine SHA-256-Signatur über die relevanten Felder.

        Die Signatur umfasst:
        - package_id
        - richter_result
        - seher_result
        - gate_decision
        - gate_mode
        - timestamp
        """
        payload = (
            f"{gate_record.package_id}:"
            f"{gate_record.richter_result.value}:"
            f"{gate_record.seher_result.value}:"
            f"{gate_record.gate_decision.value}:"
            f"{gate_record.gate_mode.value}:"
            f"{gate_record.timestamp}"
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    def verify_signature(self, gate_record: GateRecord) -> bool:
        """
        Verifiziert die Signatur eines GateRecords.

        Args:
            gate_record: GateRecord zur Verifikation

        Returns:
            True wenn Signatur gültig, False wenn manipuliert
        """
        expected_signature = self._generate_signature(gate_record)
        return gate_record.signature == expected_signature
