"""Kanzler: Stufe 3 - Strategische Review-Schleife, Lagebericht, Realitäts-Check, SAFE_MODE."""

from datetime import datetime, timezone
from typing import Any
import uuid

from pydantic import BaseModel

from src.contracts.pipeline_models import (
    Lagebericht,
    KoeniglicheWeisung,
    WeisungsResultat,
    SafeModeState,
    SafeModeConfig,
    AuditLogEntry,
    IssuedBy,
    WeisungsStatus,
    RealitaetsCheckStatus,
)
from src.contracts.enums import CircuitBreakerState


class Kanzler:
    """
    Kanzler: Implementiert die strategische Review-Schleife (Stufe 3).
    
    Verantwortlichkeiten:
    - Lagebericht-Erzeugung (Atlas, Ressourcen, Circuit-Breaker)
    - Weisungs-Verarbeitung mit Realitäts-Check
    - SAFE_MODE-Verwaltung
    - Policy-Veto-Review-Trigger (alle N Zyklen)
    - Unterscheidung HUMAN vs LLM Königin
    """

    def __init__(self, policy_review_cycle_limit: int = 20):
        """
        Initialisiert den Kanzler.
        
        Args:
            policy_review_cycle_limit: Anzahl der Zyklen bis zum Policy-Veto-Review (Default: 20)
        """
        self._policy_review_cycle_limit = policy_review_cycle_limit
        self._cycle_counter = 0
        self._safe_mode_state = SafeModeState.INACTIVE
        self._safe_mode_config = SafeModeConfig()
        self._safe_mode_reason: str | None = None
        self._safe_mode_triggered_by: str | None = None
        self._llm_conflict_count = 0  # Aufeinanderfolgende Konflikte für LLM-Königin
        self._audit_log: list[AuditLogEntry] = []
        self._last_lagebericht: Lagebericht | None = None

    def generate_lagebericht(
        self,
        atlas: Any,
        resource_governor: Any,
        circuit_breaker: Any,
    ) -> Lagebericht:
        """
        Erzeugt einen umfassenden Lagebericht.
        
        Args:
            atlas: Atlas-Instanz für Zone-Summaries
            resource_governor: ResourceGovernor für Kapazitäts-Informationen
            circuit_breaker: CircuitBreaker für Seher-Status
            
        Returns:
            Lagebericht mit allen Pflichtfeldern
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Pipeline State Summary aus Atlas
        pipeline_state_summary = {}
        if hasattr(atlas, 'get_zone_summaries'):
            pipeline_state_summary['zones'] = atlas.get_zone_summaries()
        if hasattr(atlas, 'current_version_id'):
            pipeline_state_summary['atlas_version'] = atlas.current_version_id
        
        # Resource Capacity Summary
        resource_capacity_summary = {}
        if hasattr(resource_governor, 'get_capacity_status'):
            resource_capacity_summary = resource_governor.get_capacity_status()
        
        # Signal Provenance
        signal_provenance = {}
        if hasattr(atlas, 'signal_provenance'):
            signal_provenance = atlas.signal_provenance
        
        # Circuit Breaker Status
        seher_circuit_breaker_status = CircuitBreakerState.NORMAL
        if hasattr(circuit_breaker, 'state'):
            seher_circuit_breaker_status = circuit_breaker.state
        
        lagebericht = Lagebericht(
            lagebericht_id=f"lage-{uuid.uuid4().hex[:8]}",
            pipeline_state_summary=pipeline_state_summary,
            resource_capacity_summary=resource_capacity_summary,
            signal_provenance=signal_provenance,
            seher_circuit_breaker_status=seher_circuit_breaker_status,
            timestamp=timestamp,
        )
        
        self._last_lagebericht = lagebericht
        return lagebericht

    def process_weisung(
        self,
        weisung: KoeniglicheWeisung,
        atlas: Any,
    ) -> WeisungsResultat:
        """
        Verarbeitet eine königliche Weisung mit Realitäts-Check.
        
        Args:
            weisung: Die zu verarbeitende Weisung
            atlas: Atlas-Instanz für Realitäts-Check
            
        Returns:
            WeisungsResultat mit Status, ggf. Sonderbericht und SAFE_MODE-Info
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Realitäts-Check durchführen
        realitaets_check_status, konflikt_details = self._realitaets_check(weisung, atlas)
        
        sonderbericht = None
        safe_mode_triggered = False
        
        # Bei Konflikt: Sonderbericht erzeugen
        if realitaets_check_status == RealitaetsCheckStatus.KONFLIKT:
            sonderbericht = self._generate_sonderbericht(weisung, konflikt_details)
            
            # Regel 1: Menschliche Königin wird NIEMALS überstimmt
            if weisung.issued_by == IssuedBy.HUMAN:
                # Konflikt melden, aber nicht überstimmen -> SAFE_MODE aktivieren
                safe_mode_triggered = True
                self._llm_conflict_count = 0  # Reset für HUMAN
                
                self._log_audit(
                    weisungs_id=weisung.weisungs_id,
                    action="human_queen_conflict",
                    result="sonderbericht_erzeugt_safe_mode_aktiv",
                    details={"konflikte": konflikt_details},
                    authority="HUMAN_QUEEN",
                )
            else:
                # Regel 4: LLM-Königin Fallback nach 2 Konflikten
                self._llm_conflict_count += 1
                if self._llm_conflict_count >= 2:
                    safe_mode_triggered = True
                    self._log_audit(
                        weisungs_id=weisung.weisungs_id,
                        action="llm_queen_fallback_triggered",
                        result="safe_mode_aktiv_nach_2_konflikten",
                        details={"conflict_count": self._llm_conflict_count},
                        authority="LLM_QUEEN_FALLBACK",
                    )
                else:
                    self._log_audit(
                        weisungs_id=weisung.weisungs_id,
                        action="llm_queen_conflict",
                        result=f"konflikt_{self._llm_conflict_count}_von_2",
                        details={"konflikte": konflikt_details},
                        authority="LLM_QUEEN",
                    )
        else:
            # Kein Konflikt -> LLM-Zähler zurücksetzen
            self._llm_conflict_count = 0
            
            self._log_audit(
                weisungs_id=weisung.weisungs_id,
                action="weisung_akzeptiert",
                result="kein_konflikt",
                details={"fokus": weisung.fokus_verschiebung},
                authority=weisung.issued_by.value,
            )
        
        # SAFE_MODE aktivieren falls erforderlich
        if safe_mode_triggered:
            self.activate_safe_mode(
                reason=sonderbericht or "Konflikt mit Atlas",
                triggered_by=weisung.issued_by.value,
            )
        
        status = WeisungsStatus.KONFLIKT if realitaets_check_status == RealitaetsCheckStatus.KONFLIKT else WeisungsStatus.AKZEPTIERT
        
        result = WeisungsResultat(
            status=status,
            sonderbericht=sonderbericht,
            safe_mode_triggered=safe_mode_triggered,
            realitaets_check_status=realitaets_check_status,
            konflikt_details=konflikt_details,
            processed_at=timestamp,
        )
        
        return result

    def _realitaets_check(
        self,
        weisung: KoeniglicheWeisung,
        atlas: Any,
    ) -> tuple[RealitaetsCheckStatus, list[str]]:
        """
        Führt den Realitäts-Check durch: Prüft Weisung gegen Atlas.
        
        Regel 2: Realitäts-Check prüft Weisung gegen Atlas
        - Fokus auf gesättigte Zone (⬜ Sättigung) → Konflikt
        - Fokus auf QUARANTÄNE-Zone ohne FRACTURE_DIAGNOSIS → Konflikt
        - Stopp einer Zone, die es nicht gibt → Warnung
        
        Args:
            weisung: Die zu prüfende Weisung
            atlas: Atlas-Instanz
            
        Returns:
            Tuple aus Status und Liste der Konfliktdetails
        """
        konflikt_details = []
        
        # Prüfe fokus_verschiebung
        for zone_id in weisung.fokus_verschiebung:
            zone_info = self._get_zone_info(atlas, zone_id)
            
            if zone_info is None:
                konflikt_details.append(f"Zone '{zone_id}' existiert nicht")
                continue
            
            # Prüfe auf Sättigung
            if zone_info.get('saettigung') == True or zone_info.get('status') == 'GESÄTTIGT':
                konflikt_details.append(f"Fokus auf gesättigte Zone '{zone_id}' (⬜ Sättigung)")
            
            # Prüfe auf QUARANTÄNE ohne FRACTURE_DIAGNOSIS
            if zone_info.get('status') == 'QUARANTÄNE':
                if not zone_info.get('fracture_diagnosis'):
                    konflikt_details.append(f"Fokus auf QUARANTÄNE-Zone '{zone_id}' ohne FRACTURE_DIAGNOSIS")
        
        # Prüfe stopp-Zonen
        for zone_id in weisung.stopp:
            zone_info = self._get_zone_info(atlas, zone_id)
            if zone_info is None:
                konflikt_details.append(f"Stopp für nicht-existente Zone '{zone_id}'")
        
        if konflikt_details:
            return RealitaetsCheckStatus.KONFLIKT, konflikt_details
        
        return RealitaetsCheckStatus.OK, []

    def _get_zone_info(self, atlas: Any, zone_id: str) -> dict | None:
        """Holt Informationen über eine Zone aus dem Atlas."""
        if hasattr(atlas, 'get_zone'):
            zone = atlas.get_zone(zone_id)
            if zone:
                return {
                    'id': getattr(zone, 'zone_id', zone_id),
                    'status': getattr(zone, 'status', 'UNBEKANNT'),
                    'saettigung': getattr(zone, 'saettigung', False),
                    'fracture_diagnosis': getattr(zone, 'fracture_diagnosis', None),
                }
        return None

    def _generate_sonderbericht(self, weisung: KoeniglicheWeisung, konflikt_details: list[str]) -> str:
        """Erzeugt einen Sonderbericht bei Konflikt."""
        lines = [
            f"SONDERBERICHT zur Weisung {weisung.weisungs_id}",
            f"Aussteller: {weisung.issued_by.value}",
            f"Zeitpunkt: {datetime.now(timezone.utc).isoformat()}",
            "",
            "Konflikte:",
        ]
        for detail in konflikt_details:
            lines.append(f"  - {detail}")
        lines.append("")
        lines.append("Empfehlung: Überprüfung der Weisung erforderlich.")
        return "\n".join(lines)

    def activate_safe_mode(self, reason: str, triggered_by: str) -> SafeModeState:
        """
        Aktiviert den SAFE_MODE.
        
        Regel 3: SAFE_MODE stoppt neue Exploration
        - Keine neuen Wegmarken (Lotse blockiert)
        - Keine neuen Pakete (Quartiermeister blockiert)
        - Keine neuen Dispatches (Dispatcher blockiert)
        
        Args:
            reason: Grund für die Aktivierung
            triggered_by: Wer hat den SAFE_MODE ausgelöst
            
        Returns:
            Aktueller SAFE_MODE-Zustand
        """
        self._safe_mode_state = SafeModeState.ACTIVE
        self._safe_mode_reason = reason
        self._safe_mode_triggered_by = triggered_by
        
        self._log_audit(
            weisungs_id=None,
            action="safe_mode_activated",
            result="ACTIVE",
            details={"reason": reason, "triggered_by": triggered_by},
            authority=triggered_by,
        )
        
        return self._safe_mode_state

    def deactivate_safe_mode(self, authorized_by: str) -> SafeModeState:
        """
        Deaktiviert den SAFE_MODE.
        
        Args:
            authorized_by: Autorität, die die Deaktivierung genehmigt
            
        Returns:
            Aktueller SAFE_MODE-Zustand (COOLDOWN)
        """
        if self._safe_mode_state != SafeModeState.ACTIVE:
            return self._safe_mode_state
        
        self._safe_mode_state = SafeModeState.COOLDOWN
        self._safe_mode_reason = None
        self._safe_mode_triggered_by = None
        
        self._log_audit(
            weisungs_id=None,
            action="safe_mode_deactivated",
            result="COOLDOWN",
            details={"authorized_by": authorized_by},
            authority=authorized_by,
        )
        
        return self._safe_mode_state

    def is_safe_mode_active(self) -> bool:
        """Prüft, ob SAFE_MODE aktiv ist."""
        return self._safe_mode_state == SafeModeState.ACTIVE

    def get_safe_mode_state(self) -> SafeModeState:
        """Gibt den aktuellen SAFE_MODE-Zustand zurück."""
        return self._safe_mode_state

    def increment_cycle_and_check_review(self) -> bool:
        """
        Erhöht den Zyklus-Zähler und prüft, ob Policy-Veto-Review fällig ist.
        
        Regel 5: Policy-Veto-Review alle N Zyklen
        - Default N = 20
        - Zähler ist persistent (Neustart setzt nicht zurück)
        - SAFE_MODE pausiert den Zähler, setzt ihn aber nicht zurück
        
        Returns:
            True wenn Review fällig ist, False sonst
        """
        # Regel 5: SAFE_MODE pausiert den Zähler
        if self._safe_mode_state == SafeModeState.ACTIVE:
            return False
        
        self._cycle_counter += 1
        
        review_fällig = self._cycle_counter >= self._policy_review_cycle_limit
        
        if review_fällig:
            self._cycle_counter = 0  # Zurücksetzen nach Trigger
            
            self._log_audit(
                weisungs_id=None,
                action="policy_veto_review_triggered",
                result="review_fällig",
                details={"cycle_limit": self._policy_review_cycle_limit},
                authority="KANZLER",
            )
        
        return review_fällig

    def get_cycle_counter(self) -> int:
        """Gibt den aktuellen Zyklus-Zähler zurück."""
        return self._cycle_counter

    def get_llm_conflict_count(self) -> int:
        """Gibt den aktuellen LLM-Konfliktzähler zurück."""
        return self._llm_conflict_count

    def reset_llm_conflict_count(self) -> None:
        """Setzt den LLM-Konfliktzähler zurück."""
        self._llm_conflict_count = 0

    def _log_audit(
        self,
        weisungs_id: str | None,
        action: str,
        result: str,
        details: dict[str, Any],
        authority: str | None = None,
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
