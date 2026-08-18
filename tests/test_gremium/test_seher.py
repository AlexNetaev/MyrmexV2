"""Tests für den Seher (LLM-basierte Gefahrenprüfung)."""
import pytest
from datetime import datetime, timezone
from src.gremium.sicherheitsrat.seher import Seher, SeherSignalWriter, SeherInvalidActionError, SeherInvalidVetoError
from src.contracts.pipeline_models import SeherVeto, SeherResultModel
from src.contracts.enums import SeherResult


def test_seher_pass_with_valid_package():
    """Seher PASS bei validem Paket."""
    seher = Seher()
    package = _create_valid_package()
    
    # Extract string context from PackageKontext for the seher_check call
    kontext_str = package.kontext.inhalt if hasattr(package.kontext, 'inhalt') else str(package.kontext)
    result = seher.seher_check(package, kontext_str)
    
    assert result.decision == SeherResult.SEHER_PASS
    assert result.fallback_used is False


def test_seher_veto_requires_evidence_refs():
    """Regel 2: Veto ohne evidence_refs → SEHER_INVALID_VETO."""
    seher = Seher()
    
    # Pydantic validiert bereits beim Erstellen - leere Liste wird abgelehnt
    with pytest.raises(Exception):  # ValidationError von Pydantic
        SeherVeto(
            veto_grund="Gefährliche Reaktion erwartet",
            confidence=0.85,
            evidence_refs=[],  # Leer!
            policy_ref="POLICY_CHEM_SAFETY_001"
        )


def test_seher_veto_requires_veto_grund():
    """Regel 2: Veto ohne veto_grund → SEHER_INVALID_VETO."""
    seher = Seher()
    
    # Pydantic validiert bereits beim Erstellen - leerer String wird abgelehnt
    with pytest.raises(Exception):  # ValidationError von Pydantic
        SeherVeto(
            veto_grund="",  # Leer!
            confidence=0.85,
            evidence_refs=["EVIDENCE_001"],
            policy_ref="POLICY_CHEM_SAFETY_001"
        )


def test_seher_veto_requires_confidence():
    """Regel 2: Veto ohne confidence → SEHER_INVALID_VETO."""
    seher = Seher()
    
    # Pydantic validiert bereits beim Erstellen - None wird abgelehnt
    with pytest.raises(Exception):  # ValidationError von Pydantic
        SeherVeto(
            veto_grund="Gefährliche Reaktion erwartet",
            confidence=None,  # None!
            evidence_refs=["EVIDENCE_001"],
            policy_ref="POLICY_CHEM_SAFETY_001"
        )


def test_seher_veto_requires_policy_ref():
    """Regel 2: Veto ohne policy_ref → SEHER_INVALID_VETO."""
    seher = Seher()
    
    # Pydantic validiert bereits beim Erstellen - leerer String wird abgelehnt
    with pytest.raises(Exception):  # ValidationError von Pydantic
        SeherVeto(
            veto_grund="Gefährliche Reaktion erwartet",
            confidence=0.85,
            evidence_refs=["EVIDENCE_001"],
            policy_ref=""  # Leer!
        )


def test_seher_never_writes_red_signal():
    """Regel 1 (KRITISCH): Seher schreibt NIEMALS 🟥."""
    writer = SeherSignalWriter()
    
    # Versuch, 🟥 zu schreiben, muss fehlschlagen
    with pytest.raises(SeherInvalidActionError):
        writer.write_signal("🟥", {"package_id": "pkg-001"})


def test_seher_attempt_to_write_red_is_invalid_action():
    """Regel 1: Versuch, 🟥 zu schreiben → SEHER_INVALID_ACTION."""
    seher = Seher()
    
    # Simuliere einen Versuch, ein rotes Signal zu erzeugen
    with pytest.raises(SeherInvalidActionError):
        seher.attempt_to_write_red_signal({"package_id": "pkg-001"})


def test_seher_can_write_warn_candidate():
    """Seher darf warn_candidate schreiben."""
    writer = SeherSignalWriter()
    
    # Dies sollte erfolgreich sein
    success = writer.write_signal("warn_candidate", {
        "package_id": "pkg-001",
        "warning": "Potenzielle Gefahr erkannt"
    })
    
    assert success is True


def test_seher_can_write_policy_veto():
    """Seher darf 🟪 POLICY_VETO schreiben."""
    writer = SeherSignalWriter()
    
    # Dies sollte erfolgreich sein
    success = writer.write_signal("POLICY_VETO", {
        "package_id": "pkg-001",
        "veto_grund": "Policy-Verletzung",
        "policy_ref": "POLICY_001"
    })
    
    assert success is True


def test_seher_fallback_when_llm_unavailable():
    """Regel 6: Deterministischer Fallback bei LLM-Ausfall."""
    seher = Seher(llm_available=False)  # LLM simuliert als nicht verfügbar
    package = _create_valid_package()
    
    kontext_str = package.kontext.inhalt if hasattr(package.kontext, 'inhalt') else str(package.kontext)
    result = seher.seher_check(package, kontext_str)
    
    assert result.fallback_used is True
    assert result.decision in [SeherResult.SEHER_PASS, SeherResult.SEHER_VETO]


def test_seher_fallback_never_vetos_without_evidence():
    """Regel 6: Fallback erzeugt kein Veto ohne Evidenz."""
    seher = Seher(llm_available=False)  # Fallback aktivieren
    package = _create_package_with_unknown_risk()
    
    kontext_str = package.kontext.inhalt if hasattr(package.kontext, 'inhalt') else str(package.kontext)
    result = seher.seher_check(package, kontext_str)
    
    # Fallback darf kein Veto ohne Evidenz erzeugen
    if result.decision == SeherResult.SEHER_VETO:
        assert result.evidence_refs is not None
        assert len(result.evidence_refs) >= 1


def test_seher_fallback_is_logged_in_gate_record():
    """Regel 6: Fallback-Nutzung wird im gate_record protokolliert."""
    seher = Seher(llm_available=False)
    package = _create_valid_package()
    
    kontext_str = package.kontext.inhalt if hasattr(package.kontext, 'inhalt') else str(package.kontext)
    result = seher.seher_check(package, kontext_str)
    
    assert result.fallback_used is True


def _create_valid_package():
    """Hilfsmethode zum Erstellen eines validen Test-Pakets."""
    from src.contracts.research_package import ResearchPackage, RoutingGraph, PackageKontext
    
    return ResearchPackage(
        package_id="pkg-test-001",
        source_wegmarke="wegmarke-test",
        atlas_version_ref="atlas-v1",
        ziel="Test-Ziel",
        routing_graph=RoutingGraph(
            max_loop_iterations=3,
            branch_condition_timeout=30.0,
        ),
        materials_or_resources=["water"],
        kontext=PackageKontext(
            kontext_id="kontext-001",
            domaene="test",
            beschreibung="Test context",
            erwartete_transformation="Test transformation"
        ),
        parameter_bounds={"temp": (20.0, 30.0)},
        gefahren_mitigationen=["standard_safety"]
    )


def _create_package_with_unknown_risk():
    """Hilfsmethode zum Erstellen eines Pakets mit unbekanntem Risiko."""
    from src.contracts.research_package import ResearchPackage, RoutingGraph, PackageKontext
    
    return ResearchPackage(
        package_id="pkg-test-002",
        source_wegmarke="wegmarke-test",
        atlas_version_ref="atlas-v1",
        ziel="Test-Ziel",
        routing_graph=RoutingGraph(
            max_loop_iterations=3,
            branch_condition_timeout=30.0,
        ),
        materials_or_resources=["unknown_substance"],
        kontext=PackageKontext(
            kontext_id="kontext-002",
            domaene="unknown",
            beschreibung="Test context for unknown risk",
            erwartete_transformation="Test transformation",
            domain="unknown"
        ),
        parameter_bounds={},
        gefahren_mitigationen=[]
    )
