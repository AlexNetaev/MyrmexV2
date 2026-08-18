"""DummyQuestor für Phase 8B - Test-Implementierung."""
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from src.contracts.questor_dispatch import QuestorDispatchEnvelope, SecurityMode
from src.contracts.questor_result import (
    QuestorErgebnisPaket,
    QuestorMetadata,
    AbbruchKlasse,
    AbbruchGrund,
)
from src.contracts.enums import ErgebnisStatus
# Importiere LocalAuditRef und OperationalMetrics aus questor_metadata, nicht aus questor_result
from src.contracts.questor_metadata import (
    LocalAuditRef,
    OperationalMetrics,
)


class OperationalCrashError(Exception):
    """Operativer Crash (z.B. OOM)."""
    pass


class SafetyViolationError(Exception):
    """Sicherheitsverletzung (z.B. ESTOP)."""
    pass


class DummyQuestor:
    """
    DummyQuestor für Testphase.
    Regel 6: Empfängt Envelope, liefert questor_ergebnis_paket.
    Schreibt NICHT in Atlas oder Archiv.
    Simuliert OOM (OPERATIONAL), ESTOP (SAFETY), ROUTING_LOOP_TIMEOUT (OPERATIONAL).
    """
    
    def __init__(self):
        self._executed_envelopes: list[QuestorDispatchEnvelope] = []
        self._sequence_counter: dict[str, int] = {}  # questor_instance_id -> counter
    
    def execute(self, envelope: QuestorDispatchEnvelope) -> QuestorErgebnisPaket:
        """
        Führt Envelope aus und liefert questor_ergebnis_paket.
        
        Regel 6: Liefert vollständiges Ergebnis auch bei frühem Abbruch.
        """
        self._executed_envelopes.append(envelope)
        
        # Questor-Instance-ID generieren
        questor_instance_id = f"dummy-questor-{uuid.uuid4().hex[:8]}"
        
        # Sequence-Number erhöhen
        if questor_instance_id not in self._sequence_counter:
            self._sequence_counter[questor_instance_id] = 0
        self._sequence_counter[questor_instance_id] += 1
        
        # Metadaten erstellen
        metadata = QuestorMetadata(
            questor_instance_id=questor_instance_id,
            sequence_number=self._sequence_counter[questor_instance_id],
            local_audit=LocalAuditRef(
                blackbox_id=f"blackbox-{uuid.uuid4().hex[:8]}",
                manifest_checksum=f"sha256-{uuid.uuid4().hex[:8]}",
                blackbox_digest=f"digest-{uuid.uuid4().hex[:8]}",
                access_policy_summary="test-policy"
            ),
            operational_metrics=OperationalMetrics()
        )
        
        # Erfolgreiches Ergebnis
        result = QuestorErgebnisPaket(
            package_id=envelope.package.package_id if hasattr(envelope.package, 'package_id') else "pkg-001",
            zyklus_id=envelope.zyklus_id,
            attempt_id=envelope.attempt_id,
            questor_instance_id=questor_instance_id,
            sequence_number=self._sequence_counter[questor_instance_id],
            observed_atlas_version_id="atlas-1",
            status=ErgebnisStatus.ERFOLGREICH,
            abbruch_grund=None,
            abbruch_klasse=AbbruchKlasse.OPERATIONAL,
            vollstaendig_flag=True,
            rohdaten_checksumme="sha256:dummy",
            dispatch_ref=envelope.dispatch_id,
            questor_metadata=metadata,
            ergebnis_zusammenfassung="Simulation erfolgreich abgeschlossen",
            signale_fuer_atlas=[],
            domain_metadata={"simulated": True}
        )
        
        return result
    
    def execute_with_crash(self, envelope: QuestorDispatchEnvelope) -> None:
        """
        Simuliert OOM-Crash. Wirft OperationalCrashError.
        
        Regel 6: OOM ist OPERATIONAL, nicht SAFETY.
        """
        raise OperationalCrashError("OOM")
    
    def execute_with_estop(self, envelope: QuestorDispatchEnvelope) -> None:
        """
        Simuliert ESTOP. Wirft SafetyViolationError.
        
        Regel 6: ESTOP ist SAFETY, nicht OPERATIONAL.
        """
        raise SafetyViolationError("Druckaufbau erkannt - ESTOP aktiviert")
    
    def execute_with_loop_timeout(
        self, envelope: QuestorDispatchEnvelope
    ) -> QuestorErgebnisPaket:
        """
        Simuliert ROUTING_LOOP_TIMEOUT.
        
        Regel 6: Early-Abort Complete Result - liefert vollständiges Ergebnis.
        Regel 6: ROUTING_LOOP_TIMEOUT ist OPERATIONAL.
        """
        self._executed_envelopes.append(envelope)
        
        questor_instance_id = f"dummy-questor-{uuid.uuid4().hex[:8]}"
        if questor_instance_id not in self._sequence_counter:
            self._sequence_counter[questor_instance_id] = 0
        self._sequence_counter[questor_instance_id] += 1
        
        metadata = QuestorMetadata(
            questor_instance_id=questor_instance_id,
            sequence_number=self._sequence_counter[questor_instance_id],
            local_audit=LocalAuditRef(
                blackbox_id=f"blackbox-{uuid.uuid4().hex[:8]}",
                manifest_checksum=f"sha256-{uuid.uuid4().hex[:8]}",
                blackbox_digest=f"digest-{uuid.uuid4().hex[:8]}",
                access_policy_summary="test-policy"
            ),
            operational_metrics=OperationalMetrics()
        )
        
        # Early-Abort Complete Result
        result = QuestorErgebnisPaket(
            package_id=envelope.package.package_id if hasattr(envelope.package, 'package_id') else "pkg-001",
            zyklus_id=envelope.zyklus_id,
            attempt_id=envelope.attempt_id,
            questor_instance_id=questor_instance_id,
            sequence_number=self._sequence_counter[questor_instance_id],
            observed_atlas_version_id="atlas-1",
            status=ErgebnisStatus.ABGEBROCHEN,
            abbruch_grund=AbbruchGrund.ROUTING_LOOP_TIMEOUT,
            abbruch_klasse=AbbruchKlasse.OPERATIONAL,
            vollstaendig_flag=True,  # KRITISCH: Vollständig trotz Abbruch
            rohdaten_checksumme="sha256:dummy",
            questor_metadata=metadata,
            ergebnis_zusammenfassung="Abbruch wegen Routing-Loop-Timeout",
            signale_fuer_atlas=[],
            domain_metadata={"simulated": True, "early_abort": True}
        )
        
        return result
    
    def create_result_for_crash(
        self, envelope: QuestorDispatchEnvelope, error: Exception
    ) -> QuestorErgebnisPaket:
        """
        Erstellt questor_ergebnis_paket für einen Crash.
        
        Regel 6: Auch bei Crash wird vollständiges Ergebnis geliefert.
        """
        questor_instance_id = f"dummy-questor-{uuid.uuid4().hex[:8]}"
        if questor_instance_id not in self._sequence_counter:
            self._sequence_counter[questor_instance_id] = 0
        self._sequence_counter[questor_instance_id] += 1
        
        # Abbruch-Klasse bestimmen
        if isinstance(error, SafetyViolationError):
            abbruch_klasse = AbbruchKlasse.SAFETY
            abbruch_grund = AbbruchGrund.ESTOP
        elif isinstance(error, OperationalCrashError):
            abbruch_klasse = AbbruchKlasse.OPERATIONAL
            abbruch_grund = AbbruchGrund.OOM
        else:
            abbruch_klasse = AbbruchKlasse.OPERATIONAL
            abbruch_grund = AbbruchGrund.NONE
        
        metadata = QuestorMetadata(
            questor_instance_id=questor_instance_id,
            sequence_number=self._sequence_counter[questor_instance_id],
            local_audit=LocalAuditRef(
                blackbox_id=f"blackbox-{uuid.uuid4().hex[:8]}",
                manifest_checksum=f"sha256-{uuid.uuid4().hex[:8]}",
                blackbox_digest=f"digest-{uuid.uuid4().hex[:8]}",
                access_policy_summary="test-policy"
            ),
            operational_metrics=OperationalMetrics()
        )
        
        result = QuestorErgebnisPaket(
            package_id=envelope.package.package_id if hasattr(envelope.package, 'package_id') else "pkg-001",
            zyklus_id=envelope.zyklus_id,
            attempt_id=envelope.attempt_id,
            questor_instance_id=questor_instance_id,
            sequence_number=self._sequence_counter[questor_instance_id],
            observed_atlas_version_id="atlas-1",
            status=ErgebnisStatus.ABGEBROCHEN,
            abbruch_grund=abbruch_grund,
            abbruch_klasse=abbruch_klasse,
            vollstaendig_flag=True,
            rohdaten_checksumme="sha256:dummy",
            questor_metadata=metadata,
            ergebnis_zusammenfassung=f"Abbruch: {str(error)}",
            signale_fuer_atlas=[],
            domain_metadata={"simulated": True, "crash": True}
        )
        
        return result
    
    def does_not_write_atlas(self) -> bool:
        """Verifiziert, dass DummyQuestor nicht in Atlas schreibt."""
        return True
    
    def does_not_write_archiv(self) -> bool:
        """Verifiziert, dass DummyQuestor nicht in Archiv schreibt."""
        return True
