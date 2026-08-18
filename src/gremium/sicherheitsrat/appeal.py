"""Berufungsprozess (Appeal) für DISPUTED-Fälle."""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, List, Callable, Any

from src.contracts.pipeline_models import SeherVeto, Appeal, AppealResolution
from src.contracts.enums import AppealStatus, AppealDecision, RichterResult


class AppealManager:
    """Verwaltet Berufungsprozesse bei DISPUTED-Entscheidungen."""
    
    def __init__(self):
        self._appeals: Dict[str, Appeal] = {}
        self._resolutions: Dict[str, AppealResolution] = {}
        self._false_block_callback: Optional[Callable] = None
        self._policy_veto_callback: Optional[Callable] = None
    
    def set_false_block_callback(self, callback: Callable):
        """Callback für false_block-Zählung (Circuit-Breaker)."""
        self._false_block_callback = callback
    
    def set_policy_veto_callback(self, callback: Callable):
        """Callback zum Schreiben von 🟪 POLICY_VETO."""
        self._policy_veto_callback = callback
    
    def create_appeal(
        self,
        package_id: str,
        seher_veto: SeherVeto,
        richter_result: RichterResult,
        gate_mode: Optional[str] = None
    ) -> Appeal:
        """
        Erzeugt einen Appeal bei Richter PASS + Seher VETO.
        
        Args:
            package_id: ID des Pakets
            seher_veto: Das Seher-Veto mit Evidenz
            richter_result: Das Richter-Ergebnis (muss RICHTER_PASS sein)
            gate_mode: Optionaler Gate-Mode (z.B. HIGH_RISK_OVERRIDE)
        
        Returns:
            Appeal-Objekt mit status=DISPUTED
        """
        appeal_id = f"appeal-{uuid.uuid4()}"
        
        appeal = Appeal(
            appeal_id=appeal_id,
            package_id=package_id,
            seher_veto=seher_veto,
            richter_result=richter_result,
            status=AppealStatus.DISPUTED,
            gate_mode=gate_mode,
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        self._appeals[appeal_id] = appeal
        return appeal
    
    def resolve_appeal(
        self,
        appeal_id: str,
        decision: AppealDecision,
        reason: str,
        resolved_by: str
    ) -> AppealResolution:
        """
        Löst einen Appeal auf.
        
        Args:
            appeal_id: ID des Appeals
            decision: APPEAL_GRANTED oder VETO_CONFIRMED
            reason: Begründung der Entscheidung
            resolved_by: Autorität (z.B. "kanzler-1")
        
        Returns:
            AppealResolution mit der Entscheidung
        """
        if appeal_id not in self._appeals:
            raise ValueError(f"Appeal {appeal_id} nicht gefunden")
        
        appeal = self._appeals[appeal_id]
        
        if appeal.status != AppealStatus.DISPUTED:
            raise ValueError(f"Appeal {appeal_id} ist nicht im DISPUTED-Status")
        
        timestamp = datetime.now(timezone.utc).isoformat()
        
        if decision == AppealDecision.APPEAL_GRANTED:
            # Berufung gewährt: Paket wird freigegeben
            appeal.status = AppealStatus.APPEAL_GRANTED
            
            # Als false_block zählen (für Circuit-Breaker)
            if self._false_block_callback:
                self._false_block_callback(appeal.package_id)
            
            resolution = AppealResolution(
                appeal_id=appeal_id,
                decision=decision,
                reason=reason,
                resolved_by=resolved_by,
                timestamp=timestamp
            )
        
        elif decision == AppealDecision.VETO_CONFIRMED:
            # Veto bestätigt: 🟪 POLICY_VETO schreiben (NICHT 🟥!)
            appeal.status = AppealStatus.VETO_CONFIRMED
            
            # 🟪 POLICY_VETO schreiben
            if self._policy_veto_callback:
                self._policy_veto_callback(
                    package_id=appeal.package_id,
                    veto_grund=appeal.seher_veto.veto_grund,
                    policy_ref=appeal.seher_veto.policy_ref
                )
            
            resolution = AppealResolution(
                appeal_id=appeal_id,
                decision=decision,
                reason=reason,
                resolved_by=resolved_by,
                timestamp=timestamp
            )
        
        else:
            raise ValueError(f"Ungültige Entscheidung: {decision}")
        
        self._resolutions[appeal_id] = resolution
        return resolution
    
    def resolve_appeal_with_override(
        self,
        appeal_id: str,
        positive_refutation: Optional[str],
        resolved_by: str
    ) -> str:
        """
        Versucht einen HIGH_RISK_OVERRIDE.
        
        Args:
            appeal_id: ID des Appeals
            positive_refutation: Positive Widerlegung der Gefahr (erforderlich)
            resolved_by: Autorität
        
        Returns:
            "HIGH_RISK_OVERRIDE_GRANTED" oder "HIGH_RISK_OVERRIDE_DENIED"
        """
        if appeal_id not in self._appeals:
            raise ValueError(f"Appeal {appeal_id} nicht gefunden")
        
        appeal = self._appeals[appeal_id]
        
        if appeal.gate_mode != "HIGH_RISK_OVERRIDE":
            raise ValueError(f"Appeal {appeal_id} ist kein HIGH_RISK_OVERRIDE-Fall")
        
        # Positive Widerlegung ist erforderlich
        if not positive_refutation or positive_refutation.strip() == "":
            return "HIGH_RISK_OVERRIDE_DENIED"
        
        # Mit positiver Widerlegung kann der Override gewährt werden
        resolution = self.resolve_appeal(
            appeal_id=appeal_id,
            decision=AppealDecision.APPEAL_GRANTED,
            reason=f"Positive Widerlegung: {positive_refutation}",
            resolved_by=resolved_by
        )
        
        return "HIGH_RISK_OVERRIDE_GRANTED"
    
    def get_appeal(self, appeal_id: str) -> Optional[Appeal]:
        """Holt einen Appeal nach ID."""
        return self._appeals.get(appeal_id)
    
    def get_pending_appeals(self) -> List[Appeal]:
        """Holt alle ausstehenden Appeals (DISPUTED)."""
        return [
            appeal for appeal in self._appeals.values()
            if appeal.status == AppealStatus.DISPUTED
        ]
    
    def get_all_appeals(self) -> List[Appeal]:
        """Holt alle Appeals."""
        return list(self._appeals.values())
    
    def get_resolution(self, appeal_id: str) -> Optional[AppealResolution]:
        """Holt die Resolution eines Appeals."""
        return self._resolutions.get(appeal_id)
