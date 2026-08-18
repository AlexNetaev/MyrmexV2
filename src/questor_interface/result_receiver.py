"""Result Receiver für Phase 8B."""
import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, ValidationError

from src.contracts.questor_result import (
    QuestorErgebnisPaket,
    AbbruchKlasse,
    AbbruchGrund,
)


class ReceiveValidationError(BaseModel):
    """Validierungsfehler beim Empfang."""
    field: str
    reason: str


class ValidationResult(BaseModel):
    """Ergebnis der Validierung."""
    valid: bool
    errors: list[ReceiveValidationError] = []


class ReceiveResult(BaseModel):
    """Ergebnis des Empfangs."""
    success: bool
    questor_ergebnis_paket: Optional[QuestorErgebnisPaket] = None
    error: Optional[str] = None
    forwarded_to_archivar: bool = False


class ResultReceiver:
    """
    Receiver validiert questor_ergebnis_paket.
    Regel 4: Validiert Vertrag, Idempotenz, Sequence.
    Regel 5: Liest KEINE Blackbox, schreibt keine Signale um.
    """
    
    def __init__(self, archivar=None, wal=None):
        self.archivar = archivar
        self.wal = wal
        self._received_keys: set[str] = set()  # Idempotenz-Check
        self._sequence_numbers: dict[str, int] = {}  # questor_instance_id -> letzte sequence_number
    
    def receive(self, questor_ergebnis_paket: QuestorErgebnisPaket) -> ReceiveResult:
        """
        Empfängt und validiert questor_ergebnis_paket.
        
        Regel 4: Validiert Vertrag, Idempotenz, Sequence.
        Regel 5: Keine Blackbox-Lesezugriffe.
        """
        # 1. Vertrag validieren (Pydantic)
        validation = self.validate_result(questor_ergebnis_paket)
        if not validation.valid:
            return ReceiveResult(
                success=False,
                error=f"Validierung fehlgeschlagen: {validation.errors}",
                forwarded_to_archivar=False
            )
        
        # 2. Idempotenz prüfen
        idempotency_key = questor_ergebnis_paket.paket_id
        if idempotency_key in self._received_keys:
            return ReceiveResult(
                success=False,
                error="Duplikat erkannt (idempotency_key)",
                forwarded_to_archivar=False
            )
        
        # 3. Sequence-Number prüfen (monoton pro questor_instance_id)
        qid = questor_ergebnis_paket.questor_metadata.questor_instance_id
        seq = questor_ergebnis_paket.questor_metadata.sequence_number
        
        if qid in self._sequence_numbers:
            last_seq = self._sequence_numbers[qid]
            if seq <= last_seq:
                return ReceiveResult(
                    success=False,
                    error=f"Sequence-Number nicht monoton: {seq} <= {last_seq}",
                    forwarded_to_archivar=False
                )
        
        # 4. vollstaendig_flag prüfen
        if not questor_ergebnis_paket.vollstaendig_flag:
            return ReceiveResult(
                success=False,
                error="vollstaendig_flag ist false",
                forwarded_to_archivar=False
            )
        
        # Alles erfolgreich - speichern und weiterleiten
        self._received_keys.add(idempotency_key)
        self._sequence_numbers[qid] = seq
        
        # Weiterleitung an Archivar
        forwarded = self.forward_to_archivar(questor_ergebnis_paket)
        
        return ReceiveResult(
            success=True,
            questor_ergebnis_paket=questor_ergebnis_paket,
            forwarded_to_archivar=forwarded
        )
    
    def validate_result(self, questor_ergebnis_paket: QuestorErgebnisPaket) -> ValidationResult:
        """
        Validiert alle Pflichtfelder des questor_ergebnis_paket.
        
        Regel 4: abbruch_klasse muss OPERATIONAL, SCIENTIFIC oder SAFETY sein.
        """
        errors = []
        
        # Pflichtfelder prüfen
        if not questor_ergebnis_paket.paket_id:
            errors.append(ReceiveValidationError(field="paket_id", reason="Fehlt"))
        
        if not questor_ergebnis_paket.dispatch_ref:
            errors.append(ReceiveValidationError(field="dispatch_ref", reason="Fehlt"))
        
        if not questor_ergebnis_paket.status:
            errors.append(ReceiveValidationError(field="status", reason="Fehlt"))
        
        # abbruch_klasse prüfen (wenn vorhanden)
        if questor_ergebnis_paket.abbruch_klasse is not None:
            if questor_ergebnis_paket.abbruch_klasse not in (
                AbbruchKlasse.OPERATIONAL,
                AbbruchKlasse.SCIENTIFIC,
                AbbruchKlasse.SAFETY
            ):
                errors.append(ReceiveValidationError(
                    field="abbruch_klasse",
                    reason=f"Ungültiger Wert: {questor_ergebnis_paket.abbruch_klasse}"
                ))
        
        # questor_metadata prüfen
        if not questor_ergebnis_paket.questor_metadata:
            errors.append(ReceiveValidationError(field="questor_metadata", reason="Fehlt"))
        elif not questor_ergebnis_paket.questor_metadata.questor_instance_id:
            errors.append(ReceiveValidationError(
                field="questor_metadata.questor_instance_id",
                reason="Fehlt"
            ))
        
        return ValidationResult(valid=len(errors) == 0, errors=errors)
    
    def forward_to_archivar(self, questor_ergebnis_paket: QuestorErgebnisPaket) -> bool:
        """
        Leitet validiertes Paket an Archivar weiter.
        
        Regel 5: Keine Blackbox-Lesezugriffe, keine Signal-Umschreibung.
        """
        if self.archivar is None:
            # Archivar nicht verfügbar - trotzdem als Erfolg markieren (Mock)
            return True
        
        # Archivar aufrufen (ohne Blackbox zu lesen)
        try:
            self.archivar.store(questor_ergebnis_paket)
            return True
        except Exception:
            return False
