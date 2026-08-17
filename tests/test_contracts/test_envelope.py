import pytest
from pydantic import ValidationError

from src.contracts.questor_dispatch import QuestorDispatchEnvelope
from src.contracts.research_package import ResearchPackage, RoutingGraph


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


def _envelope_payload(**overrides):
    data = {
        "dispatch_id": "dispatch-1",
        "zyklus_id": "zyklus-014",
        "attempt_id": 2,
        "package": _package(),
        "gate_record_ref": "gate-1",
        "dispatch_timestamp": "2026-08-18T00:00:00Z",
    }
    data.update(overrides)
    return data


def test_envelope_requires_gate_record():
    """Test N-04/I-04: Envelope ohne gate_record_ref ist invalid."""
    payload = _envelope_payload()
    payload.pop("gate_record_ref")

    with pytest.raises(ValidationError):
        QuestorDispatchEnvelope(**payload)


def test_envelope_rejects_empty_gate_record():
    """Test N-04/I-04: Envelope mit leerer gate_record_ref ist invalid."""
    payload = _envelope_payload(gate_record_ref="")

    with pytest.raises(ValidationError):
        QuestorDispatchEnvelope(**payload)


def test_envelope_computes_canonical_idempotency_key():
    """Test Z-02: Envelope erzeugt automatisch den kanonischen Idempotency-Key."""
    envelope = QuestorDispatchEnvelope(**_envelope_payload())

    assert envelope.idempotency_key == "pkg-001:zyklus-014:2"


def test_envelope_rejects_mismatched_idempotency_key():
    """Test Z-02: Envelope lehnt einen nicht kanonischen Idempotency-Key ab."""
    payload = _envelope_payload(idempotency_key="pkg-001:zyklus-014:3")

    with pytest.raises(ValidationError):
        QuestorDispatchEnvelope(**payload)
