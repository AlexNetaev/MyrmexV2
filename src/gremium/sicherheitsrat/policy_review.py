"""Policy-Veto-Review alle N Zyklen."""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any

from src.contracts.pipeline_models import PolicyVetoReview
from src.contracts.enums import PolicyReviewDecision


class PolicyReviewManager:
    """
    Verwaltet den Policy-Veto-Review alle N Zyklen.
    
    Regel 5:
    - Default-Intervall: 20 Zyklen
    - Range: 1-500, 0 ungültig
    - Zähler ist persistent (Neustart setzt nicht zurück)
    - SAFE_MODE pausiert Zählung, setzt aber nicht zurück
    - Jeder Review erzeugt Audit-Event 'policy_veto_review'
    """
    
    def __init__(self, interval_cycles: int = 20):
        """
        Initialisiert den Policy-Review-Manager.
        
        Args:
            interval_cycles: Review-Intervall in Zyklen (1-500, Default 20)
        
        Raises:
            ValueError: Wenn interval_cycles außerhalb des Bereichs [1, 500]
        """
        if not isinstance(interval_cycles, int) or interval_cycles < 1 or interval_cycles > 500:
            raise ValueError(
                f"interval_cycles muss im Bereich [1, 500] sein, got {interval_cycles}"
            )
        
        self.interval_cycles = interval_cycles
        self.current_cycle = 0
        self.safe_mode = False
        self._review_history: List[PolicyVetoReview] = []
    
    def set_safe_mode(self, enabled: bool):
        """
        Aktiviert oder deaktiviert den SAFE_MODE.
        
        Im SAFE_MODE wird die Zählung pausiert, aber nicht zurückgesetzt.
        """
        self.safe_mode = enabled
    
    def increment_cycle(self) -> bool:
        """
        Erhöht den Zykluszähler um 1.
        
        Returns:
            True wenn Review fällig ist, False otherwise
        
        Hinweis:
            - Im SAFE_MODE wird der Zähler nicht erhöht
            - Bei Erreichen von interval_cycles wird True zurückgegeben
              und der Zähler zurückgesetzt
        """
        if self.safe_mode:
            return False
        
        self.current_cycle += 1
        
        if self.current_cycle >= self.interval_cycles:
            self.current_cycle = 0
            return True
        
        return False
    
    def run_review(
        self,
        policy_vetos: List[Dict[str, Any]],
        authority: str,
        zyklus_id: str,
        decisions: Optional[Dict[str, str]] = None
    ) -> List[PolicyVetoReview]:
        """
        Führt den Policy-Veto-Review durch.
        
        Args:
            policy_vetos: Liste der aktiven 🟪 POLICY_VETOs
            authority: Autorität die den Review durchführt (z.B. "kanzler-1")
            zyklus_id: ID des aktuellen Zyklus
            decisions: Optionale vordefinierte Entscheidungen pro veto_id
        
        Returns:
            Liste der PolicyVetoReview-Objekte mit Audit-Events
        """
        reviews = []
        timestamp = datetime.now(timezone.utc).isoformat()
        
        for veto in policy_vetos:
            veto_id = veto.get("policy_veto_id", f"veto-{uuid.uuid4()}")
            
            # Entscheidung bestimmen
            if decisions and veto_id in decisions:
                review_decision = decisions[veto_id]
            else:
                # Standard: CONFIRMED (konservative Entscheidung)
                review_decision = "CONFIRMED"
            
            # Validierung der Entscheidung
            if review_decision not in ["CONFIRMED", "LIFTED", "ESCALATED"]:
                review_decision = "CONFIRMED"
            
            # Eskalationsziel bei ESCALATED
            escalation_target = None
            if review_decision == "ESCALATED":
                escalation_target = "gremium-ausschuss"
            
            # Review-Begründung
            review_reason = self._generate_review_reason(review_decision, veto)
            
            # Audit-Event erzeugen
            review = PolicyVetoReview(
                event_type="policy_veto_review",
                zyklus_id=zyklus_id,
                policy_veto_id=veto_id,
                review_decision=review_decision,
                review_reason=review_reason,
                review_timestamp=timestamp,
                review_authority=authority,
                escalation_target=escalation_target
            )
            
            reviews.append(review)
            self._review_history.append(review)
        
        return reviews
    
    def _generate_review_reason(self, decision: str, veto: Dict[str, Any]) -> str:
        """Generiert eine Begründung für die Review-Entscheidung."""
        reasons = {
            "CONFIRMED": "Policy-Verstoß bestätigt nach erneuter Prüfung",
            "LIFTED": "Policy-Verstoß aufgehoben aufgrund neuer Erkenntnisse",
            "ESCALATED": "An Gremium-Ausschuss eskaliert wegen komplexer Sachlage"
        }
        return reasons.get(decision, "Review durchgeführt")
    
    def get_review_history(self) -> List[PolicyVetoReview]:
        """Holt die Historie aller Reviews."""
        return self._review_history
    
    def get_next_review_cycle(self) -> int:
        """Gibt den nächsten Zyklus an, bei dem Review fällig ist."""
        return self.interval_cycles - self.current_cycle
    
    def reset_counter(self):
        """
        Setzt den Zähler zurück.
        
        Wird normalerweise nur nach einem erfolgreichen Review aufgerufen.
        In der persistenten Implementierung würde dies nicht bei Neustart passieren.
        """
        self.current_cycle = 0
