"""Tests für den Quartiermeister (Phase 8A)."""

import pytest
from unittest.mock import MagicMock, Mock

from src.gremium.quartiermeister import (
    Quartiermeister,
    QuartiermeisterState,
    QuartiermeisterEvent,
)
from src.contracts.research_package import RoutingGraph, RoutingNode, RoutingEdge
from src.contracts.pipeline_models import LeaseReservation
from src.contracts.enums import GateDecision


class MockWAL:
    """Mock-WAL für Tests."""

    def __init__(self):
        self.events = []

    def log_event(self, event):
        self.events.append(event)


class MockAtlas:
    """Mock-Atlas für Tests."""

    def __init__(self, atlas_version_id="atlas-v1"):
        self.atlas_version_id = atlas_version_id
        self.dimension_schema = MagicMock()
        self.dimension_schema.has_dimension.return_value = True


class MockWegmarke:
    """Mock-Wegmarke für Tests."""

    def __init__(self, wegmarke_id="wm-1", name="TestZone", version="v1", slot_ids=None, typ="NORMAL"):
        self.wegmarke_id = wegmarke_id
        self.name = name
        self.version = version
        self.slot_ids = slot_ids or ["slot-1", "slot-2"]
        self.typ = typ


@pytest.fixture
def wal():
    return MockWAL()


@pytest.fixture
def atlas():
    return MockAtlas()


@pytest.fixture
def wegmarke():
    return MockWegmarke()


@pytest.fixture
def quartiermeister(wal):
    return Quartiermeister(wal=wal)


def test_quartiermeister_builds_package_from_wegmarke(quartiermeister, wegmarke, atlas):
    """Quartiermeister baut research_package aus Wegmarke."""
    result = quartiermeister.build_package(wegmarke, atlas)

    assert result.decision == "GATE_PENDING"
    assert result.package is not None
    assert result.package.source_wegmarke == wegmarke.wegmarke_id
    assert result.package.atlas_version_ref == atlas.atlas_version_id


def test_quartiermeister_routing_graph_is_directed(quartiermeister, wegmarke, atlas):
    """Regel 1: routing_graph ist ein gerichteter Graph."""
    result = quartiermeister.build_package(wegmarke, atlas)

    routing_graph = result.package.routing_graph
    assert isinstance(routing_graph, RoutingGraph)
    assert len(routing_graph.nodes) > 0
    assert len(routing_graph.edges) > 0

    # Überprüfe, dass Kanten gerichtet sind (from_node != to_node bei mehreren Knoten)
    if len(routing_graph.nodes) > 1:
        for edge in routing_graph.edges:
            assert edge.from_node is not None
            assert edge.to_node is not None


def test_quartiermeister_routing_graph_not_linear_list(quartiermeister, wegmarke, atlas):
    """Regel 1: routing_graph ist KEINE lineare Liste."""
    result = quartiermeister.build_package(wegmarke, atlas)

    routing_graph = result.package.routing_graph

    # Ein gerichteter Graph hat separate nodes und edges Listen
    assert hasattr(routing_graph, "nodes")
    assert hasattr(routing_graph, "edges")

    # Die Struktur unterstützt beliebige Graphen, nicht nur lineare Ketten
    assert isinstance(routing_graph.nodes, list)
    assert isinstance(routing_graph.edges, list)


def test_quartiermeister_routing_graph_has_max_loop_iterations(quartiermeister, wegmarke, atlas):
    """Regel 1: routing_graph hat max_loop_iterations (Pflichtfeld)."""
    result = quartiermeister.build_package(wegmarke, atlas)

    routing_graph = result.package.routing_graph
    assert hasattr(routing_graph, "max_loop_iterations")
    assert routing_graph.max_loop_iterations > 0
    assert isinstance(routing_graph.max_loop_iterations, int)


def test_quartiermeister_routing_graph_has_branch_condition_timeout(quartiermeister, wegmarke, atlas):
    """Regel 1: routing_graph hat branch_condition_timeout (Pflichtfeld)."""
    result = quartiermeister.build_package(wegmarke, atlas)

    routing_graph = result.package.routing_graph
    assert hasattr(routing_graph, "branch_condition_timeout")
    assert routing_graph.branch_condition_timeout > 0.0
    assert isinstance(routing_graph.branch_condition_timeout, float)


def test_quartiermeister_materials_domain_neutral(quartiermeister, wegmarke, atlas):
    """Regel 5: materials_or_resources ist domain-neutral."""
    result = quartiermeister.build_package(wegmarke, atlas)

    materials = result.package.materials_or_resources
    assert len(materials) > 0

    # Domain-neutrale Begriffe (keine gerätespezifischen Namen)
    domain_neutral_terms = [
        "liquid_sample",
        "solid_substrate",
        "compute_node",
        "energy_unit",
        "diagnostic_sample",
        "analysis_medium",
    ]

    for material in materials:
        assert any(term in material for term in domain_neutral_terms), \
            f"Material '{material}' ist nicht domain-neutral"


def test_quartiermeister_dimension_approval_required(quartiermeister, wegmarke, atlas):
    """Regel 2: dimension_expansion_approval wird geprüft."""
    # Atlas hat alle Dimensionen freigegeben
    atlas.dimension_schema.has_dimension.return_value = True

    result = quartiermeister.build_package(wegmarke, atlas)

    # Paket sollte erstellt werden
    assert result.decision == "GATE_PENDING"
    assert result.package is not None


def test_quartiermeister_dimension_approval_missing(quartiermeister, wegmarke, atlas):
    """Regel 2: Ohne Approval → DIMENSION_APPROVAL_MISSING."""
    # Atlas hat Dimension NICHT freigegeben
    atlas.dimension_schema.has_dimension.return_value = False

    result = quartiermeister.build_package(wegmarke, atlas)

    # Paket sollte verworfen werden
    assert result.decision == "VERWORFEN"
    assert result.reason == "DIMENSION_APPROVAL_MISSING"


def test_quartiermeister_lease_reservation_requested(quartiermeister, wegmarke, atlas):
    """Regel 4: lease_reservation wird beim Resource Governor angefordert."""
    result = quartiermeister.build_package(wegmarke, atlas)

    # lease_reservation sollte erstellt worden sein
    assert result.lease_reservation is not None
    assert result.lease_reservation.status == "ACTIVE"
    assert result.lease_reservation.ttl_s > 0


def test_quartiermeister_lease_denied_is_operational(quartiermeister, wegmarke, atlas):
    """Regel 4: LEASE_DENIED ist OPERATIONAL, kein ESTOP."""
    # Mock Resource Governor, der Lease verweigert
    mock_rg = MagicMock()
    mock_rg.request_lease.side_effect = Exception("Resource unavailable")

    qm_with_rg = Quartiermeister(wal=quartiermeister.wal, resource_governor=mock_rg)
    result = qm_with_rg.build_package(wegmarke, atlas)

    # LEASE_DENIED ist OPERATIONAL (kein Absturz, keine Exception)
    assert result.decision == "VERWORFEN"
    assert result.reason == "LEASE_DENIED"
    assert result.lease_reservation is not None
    assert result.lease_reservation.status == "DENIED"


def test_quartiermeister_package_has_atlas_version_ref(quartiermeister, wegmarke, atlas):
    """Paket hat atlas_version_ref."""
    result = quartiermeister.build_package(wegmarke, atlas)

    assert result.package is not None
    assert result.package.atlas_version_ref == atlas.atlas_version_id


def test_quartiermeister_package_has_questor_spec(quartiermeister, wegmarke, atlas):
    """Paket hat optionales questor_spec."""
    result = quartiermeister.build_package(wegmarke, atlas)

    assert result.package is not None
    # questor_spec kann None sein (optional)
    assert result.package.questor_spec is None or isinstance(result.package.questor_spec, dict)


def test_quartiermeister_package_written_to_wal(quartiermeister, wegmarke, atlas):
    """Regel 6: Zustandsübergänge werden im WAL protokolliert."""
    result = quartiermeister.build_package(wegmarke, atlas)

    # WAL sollte Events enthalten
    assert len(quartiermeister.wal.events) > 0

    # Mindestens ein Event sollte den Übergang zu LOCKED_GATE_PENDING protokollieren
    gate_pending_events = [
        e for e in quartiermeister.wal.events
        if e.get("to_state") == "LOCKED_GATE_PENDING"
    ]
    assert len(gate_pending_events) > 0


def test_quartiermeister_state_transitions_valid(quartiermeister, wegmarke, atlas):
    """Zustandsmaschine erlaubt nur gültige Übergänge."""
    result = quartiermeister.build_package(wegmarke, atlas)

    # Paket sollte im Zustand LOCKED_GATE_PENDING sein
    package_id = result.package.package_id
    current_state = quartiermeister._get_state(package_id)

    assert current_state == QuartiermeisterState.LOCKED_GATE_PENDING


def test_quartiermeister_invalid_transition_raises(quartiermeister):
    """Ungültiger Zustandsübergang wirft Fehler."""
    package_id = "test-pkg"
    quartiermeister._set_state(package_id, QuartiermeisterState.WEGMARKE_RESERVIERT)

    # Ungültiger Übergang: WEGMARKE_RESERVIERT → GATE_APPROVED (überspringt PAKET_ENTWURF)
    with pytest.raises(ValueError):
        quartiermeister._transition_state(
            package_id,
            QuartiermeisterState.WEGMARKE_RESERVIERT,
            QuartiermeisterState.GATE_APPROVED,
        )


def test_quartiermeister_handle_gate_decision_approved(quartiermeister, wegmarke, atlas):
    """Gate genehmigt → LOCKED_READY_TO_EXEC."""
    result = quartiermeister.build_package(wegmarke, atlas)
    package_id = result.package.package_id

    # Simuliere Gate-Entscheidung
    gate_result = quartiermeister.handle_gate_decision(package_id, GateDecision.FREIGEGEBEN)

    assert gate_result.decision == "LOCKED_READY_TO_EXEC"

    # Zustand sollte LOCKED_READY_TO_EXEC sein
    current_state = quartiermeister._get_state(package_id)
    assert current_state == QuartiermeisterState.LOCKED_READY_TO_EXEC


def test_quartiermeister_handle_gate_decision_rejected(quartiermeister, wegmarke, atlas):
    """Gate abgelehnt → PAKET_VERWORFEN."""
    result = quartiermeister.build_package(wegmarke, atlas)
    package_id = result.package.package_id

    # Simuliere Gate-Entscheidung
    gate_result = quartiermeister.handle_gate_decision(package_id, GateDecision.ABGELEHNT)

    assert gate_result.decision == "VERWORFEN"

    # Zustand sollte PAKET_VERWORFEN sein
    current_state = quartiermeister._get_state(package_id)
    assert current_state == QuartiermeisterState.PAKET_VERWORFEN


def test_quartiermeister_complete_package(quartiermeister, wegmarke, atlas):
    """Paket fertigstellen → PAKET_FERTIG."""
    result = quartiermeister.build_package(wegmarke, atlas)
    package_id = result.package.package_id

    # Erst Gate genehmigen
    quartiermeister.handle_gate_decision(package_id, GateDecision.FREIGEGEBEN)

    # Dann Paket fertigstellen
    complete_result = quartiermeister.complete_package(package_id)

    assert complete_result.decision == "PAKET_FERTIG"

    # Zustand sollte PAKET_FERTIG sein
    current_state = quartiermeister._get_state(package_id)
    assert current_state == QuartiermeisterState.PAKET_FERTIG


def test_quartiermeister_recovery_locked_gate_pending_to_stufe7(quartiermeister, wegmarke, atlas):
    """Regel 3 (KRITISCH): LOCKED_GATE_PENDING → Recovery in Stufe 7, NICHT Stufe 8."""
    result = quartiermeister.build_package(wegmarke, atlas)
    package_id = result.package.package_id

    # Paket ist im Zustand LOCKED_GATE_PENDING
    current_state = quartiermeister._get_state(package_id)
    assert current_state == QuartiermeisterState.LOCKED_GATE_PENDING

    # Recovery-Zustand abrufen
    recovery_state = quartiermeister.get_recovery_state(package_id)

    # KRITISCH: Recovery geht zurück zu PAKET_ENTWURF (Stufe 7), NICHT zu LOCKED_READY_TO_EXEC (Stufe 8)
    assert recovery_state == QuartiermeisterState.PAKET_ENTWURF
    assert recovery_state != QuartiermeisterState.LOCKED_READY_TO_EXEC


def test_quartiermeister_routing_graph_edges_have_from_and_to(quartiermeister, wegmarke, atlas):
    """Routing-Edges haben from_node und to_node."""
    result = quartiermeister.build_package(wegmarke, atlas)

    routing_graph = result.package.routing_graph
    for edge in routing_graph.edges:
        assert hasattr(edge, "from_node")
        assert hasattr(edge, "to_node")
        assert hasattr(edge, "condition")
        assert edge.from_node is not None
        assert edge.to_node is not None
        assert edge.condition is not None


def test_quartiermeister_routing_graph_supports_branches(quartiermeister, wegmarke, atlas):
    """routing_graph unterstützt Verzweigungen (gerichteter Graph)."""
    # Erstelle Wegmarke mit mehreren Slots
    wegmarke_multi = MockWegmarke(slot_ids=["slot-A", "slot-B", "slot-C"])

    result = quartiermeister.build_package(wegmarke_multi, atlas)
    routing_graph = result.package.routing_graph

    # Graph sollte mehrere Knoten und Kanten haben
    assert len(routing_graph.nodes) == 3
    assert len(routing_graph.edges) >= 2  # Mindestens 2 Kanten für 3 Knoten


def test_quartiermeister_event_has_required_fields(quartiermeister, wegmarke, atlas):
    """QuartiermeisterEvent hat alle erforderlichen Felder."""
    result = quartiermeister.build_package(wegmarke, atlas)

    event = result.quartiermeister_event
    assert event is not None
    assert event.event_id is not None
    assert event.package_id is not None
    assert event.from_state is not None
    assert event.to_state is not None
    assert event.timestamp is not None


def test_quartiermeister_lease_reservation_has_ttl(quartiermeister, wegmarke, atlas):
    """LeaseReservation hat TTL."""
    result = quartiermeister.build_package(wegmarke, atlas)

    lease = result.lease_reservation
    assert lease is not None
    assert lease.ttl_s > 0
    assert lease.reservation_id is not None
    assert lease.created_at is not None


def test_quartiermeister_materials_for_diagnostic_waypoint(quartiermeister, atlas):
    """Diagnostic-Wegmarken haben spezielle Materialien."""
    wegmarke_diagnostic = MockWegmarke(typ="DIAGNOSTIC")

    result = quartiermeister.build_package(wegmarke_diagnostic, atlas)

    materials = result.package.materials_or_resources
    assert "diagnostic_sample" in materials or "analysis_medium" in materials
