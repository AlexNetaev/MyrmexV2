"""Tests for ResearchPackage and RoutingGraph contracts."""

import pytest
from pydantic import ValidationError

from src.contracts.research_package import (
    PackageKontext,
    ResearchPackage,
    RoutingGraph,
    RoutingNode,
)


def _routing_graph(**overrides):
    data = {
        "max_loop_iterations": 3,
        "branch_condition_timeout": 30.0,
    }
    data.update(overrides)
    return data


def _package(**overrides):
    data = {
        "package_id": "pkg-001",
        "source_wegmarke": "wegmarke-1",
        "atlas_version_ref": "atlas-1",
        "ziel": "Testziel",
        "routing_graph": _routing_graph(),
    }
    data.update(overrides)
    return data


def test_research_package_requires_routing_graph():
    """Test: routing_graph ist ein Pflichtfeld in ResearchPackage."""
    payload = _package()
    del payload["routing_graph"]

    with pytest.raises(ValidationError):
        ResearchPackage(**payload)


def test_routing_graph_requires_max_loop_iterations():
    """Test: max_loop_iterations ist ein Pflichtfeld mit gt=0."""
    payload = _routing_graph()
    del payload["max_loop_iterations"]

    with pytest.raises(ValidationError):
        RoutingGraph(**payload)

    # Test with invalid value <= 0
    payload = _routing_graph(max_loop_iterations=0)
    with pytest.raises(ValidationError):
        RoutingGraph(**payload)

    payload = _routing_graph(max_loop_iterations=-1)
    with pytest.raises(ValidationError):
        RoutingGraph(**payload)


def test_routing_graph_requires_branch_condition_timeout():
    """Test: branch_condition_timeout ist ein Pflichtfeld mit gt=0.0."""
    payload = _routing_graph()
    del payload["branch_condition_timeout"]

    with pytest.raises(ValidationError):
        RoutingGraph(**payload)

    # Test with invalid value <= 0.0
    payload = _routing_graph(branch_condition_timeout=0.0)
    with pytest.raises(ValidationError):
        RoutingGraph(**payload)

    payload = _routing_graph(branch_condition_timeout=-1.0)
    with pytest.raises(ValidationError):
        RoutingGraph(**payload)


def test_routing_graph_accepts_valid_values():
    """Test: RoutingGraph akzeptiert gültige Werte."""
    rg = RoutingGraph(
        max_loop_iterations=5,
        branch_condition_timeout=60.0,
    )

    assert rg.max_loop_iterations == 5
    assert rg.branch_condition_timeout == 60.0


def test_routing_node_is_optional_in_routing_graph():
    """Test: nodes ist optional in RoutingGraph."""
    rg = RoutingGraph(
        max_loop_iterations=3,
        branch_condition_timeout=30.0,
    )

    assert rg.nodes == []


def test_routing_node_creation():
    """Test: RoutingNode kann erstellt werden."""
    node = RoutingNode(
        node_id="node-1",
        node_type="COMPUTE",
        capabilities_required=["dummy"],
    )

    assert node.node_id == "node-1"
    assert node.node_type == "COMPUTE"
    assert node.capabilities_required == ["dummy"]


def test_package_kontext_creation():
    """Test: PackageKontext kann erstellt werden."""
    kontext = PackageKontext(
        kontext_id="kontext-1",
        domain="test-domain",
        tags=["tag1", "tag2"],
    )

    assert kontext.kontext_id == "kontext-1"
    assert kontext.domain == "test-domain"
    assert kontext.tags == ["tag1", "tag2"]


def test_research_package_with_package_kontext():
    """Test: ResearchPackage kann mit PackageKontext erstellt werden."""
    kontext = PackageKontext(
        kontext_id="kontext-1",
        domain="test-domain",
    )

    pkg = ResearchPackage(
        package_id="pkg-001",
        source_wegmarke="wegmarke-1",
        atlas_version_ref="atlas-1",
        ziel="Testziel",
        routing_graph=_routing_graph(),
        kontext=kontext,
    )

    assert pkg.kontext is not None
    assert pkg.kontext.kontext_id == "kontext-1"
