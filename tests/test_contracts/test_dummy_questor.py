from src.contracts.enums import AbbruchKlasse, ErgebnisStatus
from src.contracts.questor_dispatch import QuestorDispatchEnvelope
from src.contracts.research_package import ResearchPackage, RoutingGraph
from src.questor_interface.dummy_questor import execute


def _package() -> ResearchPackage:
    return ResearchPackage(
        package_id="pkg-001",
        source_wegmarke="wegmarke-1",
        atlas_version_ref="atlas-1",
        ziel="Phase 1 Testziel",
        routing_graph=RoutingGraph(
            max_loop_iterations=3,
            branch_condition_timeout=30.0,
        ),
    )


def _envelope() -> QuestorDispatchEnvelope:
    return QuestorDispatchEnvelope(
        dispatch_id="dispatch-1",
        zyklus_id="zyklus-014",
        attempt_id=2,
        package=_package(),
        gate_record_ref="gate-1",
        dispatch_timestamp="2026-08-18T00:00:00Z",
    )


def test_dummy_questor_returns_package_invalid():
    """Phase 1 Dummy-Questor liefert immer ein vollständiges PACKAGE_INVALID Ergebnis."""
    result = execute(_envelope())

    assert result.status == ErgebnisStatus.ABGEBROCHEN
    assert result.abbruch_grund == "PACKAGE_INVALID"
    assert result.abbruch_klasse == AbbruchKlasse.OPERATIONAL
    assert result.vollstaendig_flag is True


def test_dummy_questor_result_has_canonical_idempotency_key():
    """Phase 1 Dummy-Questor erzeugt automatisch den kanonischen Idempotency-Key."""
    envelope = _envelope()
    result = execute(envelope)

    expected = f"{envelope.package.package_id}:{envelope.zyklus_id}:{envelope.attempt_id}"
    assert result.idempotency_key == expected
