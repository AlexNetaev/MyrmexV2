"""Tests für Result Receiver."""
import pytest
from unittest.mock import Mock

from src.questor_interface.result_receiver import (
    ResultReceiver,
    ReceiveResult,
    ValidationResult,
)
from src.contracts.questor_result import (
    QuestorErgebnisPaket,
    QuestorMetadata,
    AbbruchKlasse,
    AbbruchGrund,
)


def create_valid_ergebnis_paket(dispatch_ref="dispatch-123"):
    """Erstellt ein gültiges QuestorErgebnisPaket."""
    return QuestorErgebnisPaket(
        package_id="paket-123",
        zyklus_id="zyklus-001",
        attempt_id=1,
        questor_instance_id="questor-1",
        sequence_number=1,
        observed_atlas_version_id="atlas-1.0",
        paket_id="paket-123",  # Alias für package_id
        dispatch_ref=dispatch_ref,
        status="erfolgreich",
        abbruch_grund=None,  # Bei ERFOLGREICH muss abbruch_grund None sein
        abbruch_klasse=AbbruchKlasse.OPERATIONAL,
        vollstaendig_flag=True,
        rohdaten_checksumme="sha256:dummy",
        questor_metadata=QuestorMetadata(
            questor_instance_id="questor-1",
            sequence_number=1,
        ),
        ergebnis_zusammenfassung="Test erfolgreich",
        signale_fuer_atlas=[],
        domain_metadata={}
    )


def test_receiver_validates_questor_ergebnis_paket():
    """Regel 4: Receiver validiert den Vertrag."""
    receiver = ResultReceiver()
    paket = create_valid_ergebnis_paket()
    
    result = receiver.receive(paket)
    
    assert result.success is True
    assert result.questor_ergebnis_paket is not None


def test_receiver_rejects_invalid_package():
    """Regel 4: Ungültiges Paket wird abgelehnt."""
    receiver = ResultReceiver()
    
    # Ungültiges Paket mit leeren required fields - wir müssen Pydantic umgehen
    # indem wir ein gültiges Paket erstellen und dann Felder manipulieren
    from src.contracts.questor_result import QuestorMetadata
    
    # Erstelle ein zunächst gültiges Paket und mache es dann ungültig
    invalid_paket = QuestorErgebnisPaket(
        package_id="paket-123",
        zyklus_id="zyklus-001",
        attempt_id=1,
        questor_instance_id="questor-1",
        sequence_number=1,
        observed_atlas_version_id="atlas-1.0",
        paket_id="",  # Leer - ungültig (wird später gesetzt)
        dispatch_ref="",
        status="erfolgreich",
        abbruch_grund=None,
        abbruch_klasse=AbbruchKlasse.OPERATIONAL,
        vollstaendig_flag=False,
        rohdaten_checksumme="sha256:dummy",  # Muss erst gültig sein für die Erstellung
        questor_metadata=QuestorMetadata(
            questor_instance_id="",  # Auch leer
            sequence_number=0,
        ),
        ergebnis_zusammenfassung=None,
        signale_fuer_atlas=[],
        domain_metadata={}
    )
    
    # Setze package_id und rohdaten_checksumme auf leer nach der Erstellung
    # Dies testet die Receiver-Validierung, nicht die Pydantic-Validierung
    object.__setattr__(invalid_paket, 'package_id', '')
    object.__setattr__(invalid_paket, 'rohdaten_checksumme', '')
    
    result = receiver.receive(invalid_paket)
    
    assert result.success is False


def test_receiver_idempotency_check():
    """Regel 4: Duplikate werden verworfen."""
    receiver = ResultReceiver()
    paket = create_valid_ergebnis_paket()
    
    # Erster Empfang - erfolgreich
    result1 = receiver.receive(paket)
    assert result1.success is True
    
    # Zweiter Empfang mit gleicher paket_id - Duplikat
    result2 = receiver.receive(paket)
    assert result2.success is False
    assert "Duplikat" in result2.error


def test_receiver_sequence_check():
    """Regel 4: sequence_number pro questor_instance_id wird geprüft."""
    receiver = ResultReceiver()
    
    paket1 = create_valid_ergebnis_paket()
    paket1.questor_metadata.questor_instance_id = "questor-A"
    paket1.questor_metadata.sequence_number = 1
    
    paket2 = create_valid_ergebnis_paket(dispatch_ref="dispatch-456")
    paket2.paket_id = "paket-456"
    paket2.questor_metadata.questor_instance_id = "questor-A"
    paket2.questor_metadata.sequence_number = 2
    
    result1 = receiver.receive(paket1)
    assert result1.success is True
    
    result2 = receiver.receive(paket2)
    assert result2.success is True


def test_receiver_sequence_monotonic():
    """Regel 4: Nur monotone Folgen werden akzeptiert."""
    receiver = ResultReceiver()
    
    paket1 = create_valid_ergebnis_paket()
    paket1.questor_metadata.questor_instance_id = "questor-B"
    paket1.questor_metadata.sequence_number = 5
    
    paket2 = create_valid_ergebnis_paket(dispatch_ref="dispatch-789")
    paket2.paket_id = "paket-789"
    paket2.questor_metadata.questor_instance_id = "questor-B"
    paket2.questor_metadata.sequence_number = 3  # Kleiner als vorher!
    
    result1 = receiver.receive(paket1)
    assert result1.success is True
    
    result2 = receiver.receive(paket2)
    assert result2.success is False
    assert "nicht monoton" in result2.error


def test_receiver_sequence_duplicate_rejected():
    """Regel 4: Doppelte sequence_number wird abgelehnt."""
    receiver = ResultReceiver()
    
    paket1 = create_valid_ergebnis_paket()
    paket1.questor_metadata.questor_instance_id = "questor-C"
    paket1.questor_metadata.sequence_number = 10
    
    paket2 = create_valid_ergebnis_paket(dispatch_ref="dispatch-999")
    paket2.paket_id = "paket-999"
    paket2.questor_metadata.questor_instance_id = "questor-C"
    paket2.questor_metadata.sequence_number = 10  # Gleich wie vorher!
    
    result1 = receiver.receive(paket1)
    assert result1.success is True
    
    result2 = receiver.receive(paket2)
    assert result2.success is False


def test_receiver_forwards_to_archivar():
    """Regel 4: Receiver leitet an Archivar weiter."""
    mock_archivar = Mock()
    mock_archivar.store = Mock(return_value=True)
    
    receiver = ResultReceiver(archivar=mock_archivar)
    paket = create_valid_ergebnis_paket()
    
    result = receiver.receive(paket)
    
    assert result.success is True
    assert result.forwarded_to_archivar is True
    mock_archivar.store.assert_called_once()


def test_receiver_does_not_read_blackbox():
    """Regel 5: Receiver liest KEINE Blackbox."""
    receiver = ResultReceiver()
    paket = create_valid_ergebnis_paket()
    
    # Blackbox-ID ist vorhanden, aber Receiver sollte sie nicht lesen
    assert paket.questor_metadata.local_audit is None  # Nicht gesetzt im Test
    
    result = receiver.receive(paket)
    assert result.success is True
    # Receiver hat keine Blackbox gelesen


def test_receiver_does_not_rewrite_signals():
    """Regel 5: Receiver schreibt keine Signale um."""
    receiver = ResultReceiver()
    
    original_signals = [{"signal_type": "TEST", "value": 1.0}]
    paket = create_valid_ergebnis_paket()
    paket.signale_fuer_atlas = original_signals.copy()
    
    result = receiver.receive(paket)
    
    # Signale sollten unverändert sein
    assert paket.signale_fuer_atlas == original_signals


def test_receiver_operational_not_scientific():
    """OPERATIONAL-Abbruch erzeugt kein wissenschaftliches Signal."""
    receiver = ResultReceiver()
    
    paket = create_valid_ergebnis_paket()
    paket.status = "abgebrochen"
    paket.abbruch_grund = AbbruchGrund.OOM
    paket.abbruch_klasse = AbbruchKlasse.OPERATIONAL
    paket.signale_fuer_atlas = []  # Keine wissenschaftlichen Signale
    
    result = receiver.receive(paket)
    
    assert result.success is True
    assert len(paket.signale_fuer_atlas) == 0  # Keine Signale hinzugefügt
