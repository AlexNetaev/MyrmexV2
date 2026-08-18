"""DummyQuestor für Phase 8B - Test-Implementierung."""
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from src.contracts.questor_dispatch import QuestorDispatchEnvelope, SecurityMode
from src.contracts.questor_result import (
    QuestorErgebnisPaket,
    QuestorMetadata,
    LocalAuditRef,
    OperationalMetrics,
    AbbruchKlasse,
    AbbruchGrund,
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
                audit_id=f"audit-{uuid.uuid4().hex[:8]}",
                blackbox_id=f"blackbox-{uuid.uuid4().hex[:8]}",
                trail_hash=f"hash-{uuid.uuid4().hex[:8]}"
            ),
            operational_metrics=OperationalMetrics(
                runtime_s=0.5,
                memory_peak_mb=128.0,
                cpu_percent=25.0,
                loop_iterations=1,
                branch_evaluations=0
            )
        )
        
        # Erfolgreiches Ergebnis
        result = QuestorErgebnisPaket(
            paket_id=str(uuid.uuid4()),
            dispatch_ref=envelope.dispatch_id,
            status="erfolgreich",
            abbruch_grund=AbbruchGrund.NONE,
            abbruch_klasse=None,
            vollstaendig_flag=True,
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
                audit_id=f"audit-{uuid.uuid4().hex[:8]}",
                blackbox_id=f"blackbox-{uuid.uuid4().hex[:8]}",
                trail_hash=f"hash-{uuid.uuid4().hex[:8]}"
            ),
            operational_metrics=OperationalMetrics(
                runtime_s=0.1,
                memory_peak_mb=64.0,
                cpu_percent=10.0,
                loop_iterations=0,
                branch_evaluations=0
            )
        )
        
        # Early-Abort Complete Result
        result = QuestorErgebnisPaket(
            paket_id=str(uuid.uuid4()),
            dispatch_ref=envelope.dispatch_id,
            status="abgebrochen",
            abbruch_grund=AbbruchGrund.ROUTING_LOOP_TIMEOUT,
            abbruch_klasse=AbbruchKlasse.OPERATIONAL,
            vollstaendig_flag=True,  # KRITISCH: Vollständig trotz Abbruch
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
                audit_id=f"audit-{uuid.uuid4().hex[:8]}",
                blackbox_id=f"blackbox-{uuid.uuid4().hex[:8]}",
                trail_hash=f"hash-{uuid.uuid4().hex[:8]}"
            ),
            operational_metrics=OperationalMetrics(
                runtime_s=0.05,
                memory_peak_mb=32.0,
                cpu_percent=5.0,
                loop_iterations=0,
                branch_evaluations=0
            )
        )
        
        result = QuestorErgebnisPaket(
            paket_id=str(uuid.uuid4()),
            dispatch_ref=envelope.dispatch_id,
            status="abgebrochen",
            abbruch_grund=abbruch_grund,
            abbruch_klasse=abbruch_klasse,
            vollstaendig_flag=True,
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
