"""Gate-Flow — Sicherheits-Gate mit Richter und Seher."""

import hashlib
import uuid
from datetime import datetime, timezone

from src.contracts.pipeline_models import GateRecord, DimensionOnboardingRequest
from src.contracts.enums import GateMode, GateDecision, RichterResult, SeherResult

from .richter import Richter, RichterResultData
from .seher import Seher


class GateFlow:
    """
    Gate-Flow — Führt das Sicherheits-Gate durch.

    Der Gate-Flow kombiniert:
    - Richter (deterministisch, Fail-Closed)
    - Seher (LLM-basiert, in Phase 6a als Stub)

    Gate-Entscheidungslogik:
    - Richter REJECT → ABGELEHNT
    - Richter PASS + Seher PASS → FREIGEGEBEN
    - Richter PASS + Seher VETO → DISPUTED (Phase 6b: Kanzler entscheidet)
    - Richter REGELLÜCKE → ABGELEHNT + dimension_onboarding_request
    - gate_mode = SANDBOX → FREIGEGEBEN (nur virtuell, physical_execution_allowed=false)
    - gate_mode = HIGH_RISK_OVERRIDE → Positive Widerlegung erforderlich
    """

    def __init__(self, richter: Richter, seher: Seher | None = None):
        self.richter = richter
        self.seher = seher or Seher()

    def run_gate(self, package, gate_mode: GateMode = GateMode.NORMAL) -> GateRecord:
        """
        Führt das vollständige Gate durch.

        Args:
            package: ResearchPackage zur Prüfung
            gate_mode: GateMode (NORMAL, SANDBOX, etc.)

        Returns:
            GateRecord mit Ergebnis und Signatur
        """
        # 1. Richter prüfen (immer, deterministisch)
        richter_result = self.richter.check(package, gate_mode)

        # 2. Gate-Entscheidung basierend auf Richter-Ergebnis
        if richter_result.decision == RichterResult.RICHTER_REJECT:
            return self._create_gate_record(
                package,
                gate_mode,
                richter_result=RichterResult.RICHTER_REJECT,
                seher_result=SeherResult.SEHER_NOT_CALLED,
                gate_decision=GateDecision.ABGELEHNT,
                onboarding_requests=[]
            )

        if richter_result.decision == RichterResult.REGELLUECKE:
            # REGELLÜCKE → ABGELEHNT + dimension_onboarding_request
            return self._create_gate_record(
                package,
                gate_mode,
                richter_result=RichterResult.REGELLUECKE,
                seher_result=SeherResult.SEHER_NOT_CALLED,
                gate_decision=GateDecision.ABGELEHNT,
                onboarding_requests=richter_result.onboarding_requests
            )

        # 3. Seher prüfen (bei RICHTER_PASS)
        seher_result = self.seher.seher_check(package, getattr(package, "kontext", None))

        # 4. Gate-Entscheidung basierend auf Seher-Ergebnis
        if seher_result == SeherResult.SEHER_PASS:
            gate_decision = GateDecision.FREIGEGEBEN
        elif seher_result == SeherResult.SEHER_VETO:
            gate_decision = GateDecision.DISPUTED  # Phase 6b: Kanzler entscheidet
        else:
            gate_decision = GateDecision.ABGELEHNT

        # 5. SANDBOX_MODE: Keine physische Ausführung
        physical_execution_allowed = True
        if gate_mode == GateMode.SANDBOX:
            gate_decision = GateDecision.FREIGEGEBEN
            physical_execution_allowed = False

        # 6. HIGH_RISK_OVERRIDE: Positive Widerlegung erforderlich
        if gate_mode == GateMode.HIGH_RISK_OVERRIDE:
            # Erfordert positive Widerlegung der Gefahr
            # In Phase 6a: Einfach freigeben, in Phase 6b: Zusätzliche Prüfung
            pass

        # 7. FRACTURE_DIAGNOSIS: Erlaubt diagnostic-safe in QUARANTÄNE
        if gate_mode == GateMode.FRACTURE_DIAGNOSIS:
            # Erlaubt diagnostic-safe Ausführung in QUARANTÄNE-Zonen
            pass

        # 8. gate_record erzeugen mit Signatur
        return self._create_gate_record(
            package,
            gate_mode,
            richter_result=richter_result.decision,
            seher_result=seher_result,
            gate_decision=gate_decision,
            onboarding_requests=richter_result.onboarding_requests,
            physical_execution_allowed=physical_execution_allowed
        )

    def _create_gate_record(
        self,
        package,
        gate_mode: GateMode,
        richter_result: RichterResult,
        seher_result: SeherResult,
        gate_decision: GateDecision,
        onboarding_requests: list[DimensionOnboardingRequest],
        physical_execution_allowed: bool = True
    ) -> GateRecord:
        """Erzeugt ein signiertes GateRecord."""
        gate_record_id = f"gate-{uuid.uuid4()}"
        timestamp = datetime.now(timezone.utc).isoformat()

        # Erst GateRecord ohne Signatur erstellen (signature ist optional für die Erstellung)
        gate_record = GateRecord(
            gate_record_id=gate_record_id,
            gate_id=gate_record_id,
            package_id=getattr(package, "package_id", "unknown"),
            zyklus_id=getattr(package, "zyklus_id", "unknown"),
            gate_mode=gate_mode,
            gate_decision=gate_decision,
            richter_result=richter_result,
            seher_result=seher_result,
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
