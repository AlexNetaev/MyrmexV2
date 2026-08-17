"""Tests for Pydantic contract models."""

import pytest
from pydantic import ValidationError

from src.contracts.enums import AbbruchKlasse, ErgebnisStatus, RedactionLevel, RetentionClass
from src.contracts.questor_metadata import LocalAuditRef, OperationalMetrics, QuestorMetadata
from src.contracts.research_package import ResearchPackage, RoutingGraph


class TestRoutingGraph:
    """Test RoutingGraph model."""

    def test_valid_routing_graph(self):
        rg = RoutingGraph(
            max_loop_iterations=10,
            branch_condition_timeout=5.0,
        )
        assert rg.max_loop_iterations == 10
        assert rg.branch_condition_timeout == 5.0

    def test_invalid_max_loop_iterations(self):
        with pytest.raises(ValidationError):
            RoutingGraph(
                max_loop_iterations=0,
                branch_condition_timeout=5.0,
            )

    def test_invalid_branch_condition_timeout(self):
        with pytest.raises(ValidationError):
            RoutingGraph(
                max_loop_iterations=10,
                branch_condition_timeout=0.0,
            )


class TestResearchPackage:
    """Test ResearchPackage model."""

    def test_minimal_valid_package(self):
        rp = ResearchPackage(
            package_id="test-pkg-001",
            source_wegmarke="wegmarke-v1",
            atlas_version_ref="atlas-v1.0",
            ziel="test target",
            routing_graph=RoutingGraph(
                max_loop_iterations=10,
                branch_condition_timeout=5.0,
            ),
        )
        assert rp.package_id == "test-pkg-001"
        assert rp.materials_or_resources == []
        assert rp.parameter_bounds == {}

    def test_invalid_package_id_pattern(self):
        with pytest.raises(ValidationError):
            ResearchPackage(
                package_id="invalid pkg id!",
                source_wegmarke="wegmarke-v1",
                atlas_version_ref="atlas-v1.0",
                ziel="test target",
                routing_graph=RoutingGraph(
                    max_loop_iterations=10,
                    branch_condition_timeout=5.0,
                ),
            )

    def test_package_with_optional_fields(self):
        rp = ResearchPackage(
            package_id="test-pkg-002",
            source_wegmarke="wegmarke-v1",
            source_wegmarke_version="1.0.0",
            atlas_version_ref="atlas-v1.0",
            ziel="test target",
            routing_graph=RoutingGraph(
                max_loop_iterations=10,
                branch_condition_timeout=5.0,
            ),
            materials_or_resources=["material_a", "material_b"],
            parameter_bounds={"temp": (20.0, 100.0)},
            gefahren_mitigationen=["mitigation_1"],
        )
        assert rp.source_wegmarke_version == "1.0.0"
        assert len(rp.materials_or_resources) == 2


class TestLocalAuditRef:
    """Test LocalAuditRef model."""

    def test_valid_audit_ref(self):
        lar = LocalAuditRef(
            blackbox_id="bb-001",
            manifest_checksum="sha256-abc123",
            blackbox_digest="sha256-def456",
            access_policy_summary="read-only",
        )
        assert lar.redaction_level == RedactionLevel.STRONG
        assert lar.retention_class == RetentionClass.NORMAL

    def test_custom_redaction_and_retention(self):
        lar = LocalAuditRef(
            blackbox_id="bb-001",
            manifest_checksum="sha256-abc123",
            blackbox_digest="sha256-def456",
            redaction_level=RedactionLevel.BASIC,
            retention_class=RetentionClass.SAFETY_HOLD,
            access_policy_summary="restricted",
        )
        assert lar.redaction_level == RedactionLevel.BASIC
        assert lar.retention_class == RetentionClass.SAFETY_HOLD


class TestOperationalMetrics:
    """Test OperationalMetrics model."""

    def test_default_values(self):
        om = OperationalMetrics()
        assert om.oom_count == 0
        assert om.timeout_count == 0
        assert om.lease_wait_time_s == 0.0

    def test_custom_values(self):
        om = OperationalMetrics(
            oom_count=5,
            timeout_count=3,
            lease_wait_time_s=120.5,
            recovery_attempts=2,
        )
        assert om.oom_count == 5
        assert om.recovery_attempts == 2

    def test_negative_value_validation(self):
        with pytest.raises(ValidationError):
            OperationalMetrics(oom_count=-1)


class TestQuestorMetadata:
    """Test QuestorMetadata model."""

    def test_minimal_metadata(self):
        qm = QuestorMetadata()
        assert qm.questor_version is None
        assert qm.local_audit is None
        assert qm.operational_metrics is None

    def test_full_metadata(self):
        qm = QuestorMetadata(
            questor_version="0.2.3",
            policy_version="policy-v1",
            local_audit=LocalAuditRef(
                blackbox_id="bb-001",
                manifest_checksum="sha256-abc",
                blackbox_digest="sha256-def",
                access_policy_summary="default",
            ),
            operational_metrics=OperationalMetrics(
                oom_count=1,
                timeout_count=2,
            ),
        )
        assert qm.questor_version == "0.2.3"
        assert qm.local_audit is not None
        assert qm.operational_metrics is not None
