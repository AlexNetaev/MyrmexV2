"""Königin-Interface: Schicht 5 - Interface für königliche Weisungen."""

from datetime import datetime, timezone
from typing import Any
import uuid

from pydantic import ValidationError

from src.contracts.pipeline_models import (
    KoeniglicheWeisung,
    WeisungsResultat,
    AuditLogEntry,
    IssuedBy,
)
from src.gremium.kanzler import Kanzler


class KoeniginInterface:
    """
    Königin-Interface: Schicht 5 - Interface für königliche Weisungen.
    
    Verantwortlichkeiten:
    - Weisungs-Empfang und Validierung
    - Audit-Log für alle Weisungen, Konflikte und SAFE_MODE-Wechsel
    - Unterscheidung HUMAN vs LLM
    - Weiterleitung an Kanzler
    """

    def __init__(self, kanzler: Kanzler | None = None):
        """
        Initialisiert das Königin-Interface.
        
        Args:
            kanzler: Optionaler Kanzler (wird erstellt falls nicht angegeben)
        """
        self._kanzler = kanzler or Kanzler()
        self._audit_log: list[AuditLogEntry] = []

    def receive_weisung(self, weisung: KoeniglicheWeisung) -> bool:
        """
        Empfängt und validiert eine königliche Weisung.
        
        Args:
            weisung: Die zu validierende Weisung
            
        Returns:
            True wenn Weisung gültig ist und weitergeleitet wurde, False sonst
        """
        # Schema-Validierung
        try:
            # Pydantic v2 Validierung
            validated_weisung = KoeniglicheWeisung.model_validate(weisung.model_dump())
        except ValidationError as e:
            self._log_audit(
                weisungs_id=getattr(weisung, 'weisungs_id', None),
                action="weisung_invalid",
                result="schema_validation_failed",
                details={"error": str(e)},
                authority=None,
            )
            return False
        
        # Protokolliere Empfang
        self._log_audit(
            weisungs_id=validated_weisung.weisungs_id,
            action="weisung_received",
            result="valid",
            details={
                "issued_by": validated_weisung.issued_by.value,
                "fokus_verschiebung": validated_weisung.fokus_verschiebung,
                "stopp": validated_weisung.stopp,
            },
            authority=validated_weisung.issued_by.value,
        )
        
        return True

    def process_weisung(self, weisung: KoeniglicheWeisung, atlas: Any) -> WeisungsResultat:
        """
        Verarbeitet eine königliche Weisung.
        
        Args:
            weisung: Die zu verarbeitende Weisung
            atlas: Atlas-Instanz für Realitäts-Check
            
        Returns:
            WeisungsResultat der Verarbeitung
            
        Raises:
            ValueError: Wenn Weisung ungültig ist
        """
        # Erst validieren
        if not self.receive_weisung(weisung):
            raise ValueError("Ungültige Weisung")
        
        # An Kanzler weiterleiten
        result = self._kanzler.process_weisung(weisung, atlas)
        
        # Ergebnis protokollieren
        self._log_audit(
            weisungs_id=weisung.weisungs_id,
            action="weisung_processed",
            result=result.status.value,
            details={
                "safe_mode_triggered": result.safe_mode_triggered,
                "realitaets_check_status": result.realitaets_check_status.value,
                "konflikt_details": result.konflikt_details,
            },
            authority=weisung.issued_by.value,
        )
        
        # Bei Konflikt separat protokollieren
        if result.status.value == "KONFLIKT":
            self._log_conflict(weisung, result)
        
        return result

    def _log_conflict(self, weisung: KoeniglicheWeisung, result: WeisungsResultat) -> None:
        """Protokolliert einen Konflikt im Audit-Log."""
        self._log_audit(
            weisungs_id=weisung.weisungs_id,
            action="conflict_detected",
            result=result.realitaets_check_status.value,
            details={
                "konflikt_details": result.konflikt_details,
                "sonderbericht": result.sonderbericht,
                "issued_by": weisung.issued_by.value,
            },
            authority=weisung.issued_by.value,
        )

    def activate_safe_mode(self, reason: str, triggered_by: str) -> None:
        """
        Aktiviert den SAFE_MODE.
        
        Args:
            reason: Grund für die Aktivierung
            triggered_by: Wer hat den SAFE_MODE ausgelöst
        """
        self._kanzler.activate_safe_mode(reason, triggered_by)
        
        self._log_audit(
            weisungs_id=None,
            action="safe_mode_activated",
            result="ACTIVE",
            details={"reason": reason, "triggered_by": triggered_by},
            authority=triggered_by,
        )

    def deactivate_safe_mode(self, authorized_by: str) -> None:
        """
        Deaktiviert den SAFE_MODE.
        
        Args:
            authorized_by: Autorität, die die Deaktivierung genehmigt
        """
        self._kanzler.deactivate_safe_mode(authorized_by)
        
        self._log_audit(
            weisungs_id=None,
            action="safe_mode_deactivated",
            result="COOLDOWN",
            details={"authorized_by": authorized_by},
            authority=authorized_by,
        )

    def is_safe_mode_active(self) -> bool:
        """Prüft, ob SAFE_MODE aktiv ist."""
        return self._kanzler.is_safe_mode_active()

    def generate_lagebericht(self, atlas: Any, resource_governor: Any, circuit_breaker: Any) -> Any:
        """
        Erzeugt einen Lagebericht über den Kanzler.
        
        Args:
            atlas: Atlas-Instanz
            resource_governor: ResourceGovernor-Instanz
            circuit_breaker: CircuitBreaker-Instanz
            
        Returns:
            Lagebericht
        """
        return self._kanzler.generate_lagebericht(atlas, resource_governor, circuit_breaker)

    def increment_cycle_and_check_review(self) -> bool:
        """
        Erhöht den Zyklus-Zähler und prüft Review-Fälligkeit.
        
        Returns:
            True wenn Review fällig ist
        """
        return self._kanzler.increment_cycle_and_check_review()

    def _log_audit(
        self,
        weisungs_id: str | None,
        action: str,
        result: str,
        details: dict,
        authority: str | None,
    ) -> AuditLogEntry:
        """Protokolliert eine Aktion im Audit-Log."""
        entry = AuditLogEntry(
            entry_id=f"audit-{uuid.uuid4().hex[:8]}",
            weisungs_id=weisungs_id,
            action=action,
            result=result,
            details=details,
            timestamp=datetime.now(timezone.utc).isoformat(),
            authority=authority,
        )
        self._audit_log.append(entry)
        return entry

    def get_audit_log(self) -> list[AuditLogEntry]:
        """Gibt das Audit-Log zurück."""
        return self._audit_log.copy()

    def clear_audit_log(self) -> None:
        """Löscht das Audit-Log."""
        self._audit_log.clear()

    def get_kanzler(self) -> Kanzler:
        """Gibt den internen Kanzler zurück."""
        return self._kanzler

    def distinguishes_human_and_llm(self, issued_by: IssuedBy) -> bool:
        """
        Prüft, ob zwischen HUMAN und LLM unterschieden wird.
        
        Args:
            issued_by: Die zu prüfende Herkunft
            
        Returns:
            True wenn die Unterscheidung korrekt ist
        """
        return issued_by in [IssuedBy.HUMAN, IssuedBy.LLM]
