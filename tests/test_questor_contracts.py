"""Tests for Questor dispatch and result contracts."""

import pytest
from pydantic import ValidationError

from src.contracts.enums import (
    AbbruchKlasse,
    DispatchMode,
    ErgebnisStatus,
    GateMode,
    SecurityMode,
)
from src.contracts.questor_dispatch import LeaseGrant, QuestorDispatchEnvelope
from src.contracts.questor_result import QuestorErgebnisPaket
from src.contracts.research_package import ResearchPackage, RoutingGraph


class TestLeaseGrant:
    """Test LeaseGrant model."""

    def test_minimal_lease_grant(self):
        lg = LeaseGrant(lease_id="lease-001")
        assert lg.lease_id == "lease-001"
        assert lg.slot_id is None
        assert lg.physical_execution_allowed is False

    def test_full_lease_grant(self):
        lg = LeaseGrant(
            lease_id="lease-002",
            slot_id="slot-lab-001",
            path_id="path-001",
            package_id="pkg-001",
            physical_execution_allowed=True,
            sandbox_execution_allowed=False,
            compute_execution_allowed=True,
        )
        assert lg.physical_execution_allowed is True
        assert lg.compute_execution_allowed is True


class TestQuestorDispatchEnvelope:
    """Test QuestorDispatchEnvelope model."""

    def _create_minimal_package(self) -> ResearchPackage:
        return ResearchPackage(
            package_id="test-pkg-001",
            source_wegmarke="wegmarke-v1",
            atlas_version_ref="atlas-v1.0",
            ziel="test target",
            routing_graph=RoutingGraph(
                max_loop_iterations=10,
                branch_condition_timeout=5.0,
            ),
        )

    def test_minimal_dispatch_envelope(self):
        dispatch = QuestorDispatchEnvelope(
            dispatch_id="dispatch-001",
            zyklus_id="zyklus-001",
            attempt_id=0,
            package=self._create_minimal_package(),
            gate_record_ref="gate-rec-001",
            dispatch_timestamp="2024-01-01T00:00:00Z",
        )
        assert dispatch.dispatch_mode == DispatchMode.NORMAL
        assert dispatch.security_mode == SecurityMode.NORMAL
        assert dispatch.gate_mode is None

    def test_idempotency_key_auto_generation(self):
        dispatch = QuestorDispatchEnvelope(
            dispatch_id="dispatch-002",
            zyklus_id="zyklus-002",
            attempt_id=1,
            package=self._create_minimal_package(),
            gate_record_ref="gate-rec-002",
            dispatch_timestamp="2024-01-01T00:00:00Z",
        )
        expected_key = "test-pkg-001:zyklus-002:1"
        assert dispatch.idempotency_key == expected_key

    def test_idempotency_key_validation(self):
        with pytest.raises(ValidationError) as exc_info:
            QuestorDispatchEnvelope(
                dispatch_id="dispatch-003",
                zyklus_id="zyklus-003",
                attempt_id=2,
                package=self._create_minimal_package(),
                gate_record_ref="gate-rec-003",
                dispatch_timestamp="2024-01-01T00:00:00Z",
                idempotency_key="wrong-key",
            )
        assert "PACKAGE_INVALID" in str(exc_info.value)

    def test_dispatch_with_lease_grants(self):
        dispatch = QuestorDispatchEnvelope(
            dispatch_id="dispatch-004",
            zyklus_id="zyklus-004",
            attempt_id=0,
            package=self._create_minimal_package(),
            gate_record_ref="gate-rec-004",
            dispatch_timestamp="2024-01-01T00:00:00Z",
            lease_grants=[
                LeaseGrant(
                    lease_id="lease-004",
                    slot_id="slot-lab-001",
                    physical_execution_allowed=True,
                )
            ],
            gate_mode=GateMode.NORMAL,
        )
        assert len(dispatch.lease_grants) == 1
        assert dispatch.gate_mode == GateMode.NORMAL


class TestQuestorErgebnisPaket:
    """Test QuestorErgebnisPaket model."""

    def test_successful_result(self):
        result = QuestorErgebnisPaket(
            package_id="pkg-001",
            zyklus_id="zyklus-001",
            attempt_id=0,
            questor_instance_id="questor-inst-001",
            sequence_number=1,
            observed_atlas_version_id="atlas-v1.0",
            status=ErgebnisStatus.ERFOLGREICH,
            abbruch_klasse=AbbruchKlasse.OPERATIONAL,
            vollstaendig_flag=True,
            rohdaten_checksumme="sha256-abc123",
        )
        assert result.abbruch_grund is None
        assert result.kristall_kandidaten == []
        assert result.gefahren_beobachtet == []

    def test_failed_result(self):
        result = QuestorErgebnisPaket(
            package_id="pkg-002",
            zyklus_id="zyklus-002",
            attempt_id=1,
            questor_instance_id="questor-inst-002",
            sequence_number=2,
            observed_atlas_version_id="atlas-v1.0",
            status=ErgebnisStatus.FEHLGESCHLAGEN,
            abbruch_grund="timeout during execution",
            abbruch_klasse=AbbruchKlasse.OPERATIONAL,
            vollstaendig_flag=False,
            rohdaten_checksumme="sha256-def456",
        )
        assert result.abbruch_grund == "timeout during execution"

    def test_aborted_result_with_safety_class(self):
        result = QuestorErgebnisPaket(
            package_id="pkg-003",
            zyklus_id="zyklus-003",
            attempt_id=0,
            questor_instance_id="questor-inst-003",
            sequence_number=3,
            observed_atlas_version_id="atlas-v1.0",
            status=ErgebnisStatus.ABGEBROCHEN,
            abbruch_grund="safety threshold exceeded",
            abbruch_klasse=AbbruchKlasse.SAFETY,
            vollstaendig_flag=False,
            rohdaten_checksumme="sha256-ghi789",
        )
        assert result.abbruch_klasse == AbbruchKlasse.SAFETY

    def test_successful_result_with_abbruch_grund_invalid(self):
        with pytest.raises(ValidationError) as exc_info:
            QuestorErgebnisPaket(
                package_id="pkg-004",
                zyklus_id="zyklus-004",
                attempt_id=0,
                questor_instance_id="questor-inst-004",
                sequence_number=4,
                observed_atlas_version_id="atlas-v1.0",
                status=ErgebnisStatus.ERFOLGREICH,
                abbruch_grund="should not be set",
                abbruch_klasse=AbbruchKlasse.OPERATIONAL,
                vollstaendig_flag=True,
                rohdaten_checksumme="sha256-jkl012",
            )
        assert "PACKAGE_INVALID" in str(exc_info.value)

    def test_successful_result_with_non_operational_abbruch_klasse_invalid(self):
        with pytest.raises(ValidationError) as exc_info:
            QuestorErgebnisPaket(
                package_id="pkg-005",
                zyklus_id="zyklus-005",
                attempt_id=0,
                questor_instance_id="questor-inst-005",
                sequence_number=5,
                observed_atlas_version_id="atlas-v1.0",
                status=ErgebnisStatus.ERFOLGREICH,
                abbruch_klasse=AbbruchKlasse.SAFETY,
                vollstaendig_flag=True,
                rohdaten_checksumme="sha256-mno345",
            )
        assert "PACKAGE_INVALID" in str(exc_info.value)

    def test_failed_result_without_abbruch_grund_invalid(self):
        with pytest.raises(ValidationError) as exc_info:
            QuestorErgebnisPaket(
                package_id="pkg-006",
                zyklus_id="zyklus-006",
                attempt_id=0,
                questor_instance_id="questor-inst-006",
                sequence_number=6,
                observed_atlas_version_id="atlas-v1.0",
                status=ErgebnisStatus.FEHLGESCHLAGEN,
                abbruch_klasse=AbbruchKlasse.OPERATIONAL,
                vollstaendig_flag=False,
                rohdaten_checksumme="sha256-pqr678",
            )
        assert "PACKAGE_INVALID" in str(exc_info.value)

    def test_idempotency_key_auto_generation(self):
        result = QuestorErgebnisPaket(
            package_id="pkg-007",
            zyklus_id="zyklus-007",
            attempt_id=2,
            questor_instance_id="questor-inst-007",
            sequence_number=7,
            observed_atlas_version_id="atlas-v1.0",
            status=ErgebnisStatus.ERFOLGREICH,
            abbruch_klasse=AbbruchKlasse.OPERATIONAL,
            vollstaendig_flag=True,
            rohdaten_checksumme="sha256-stu901",
        )
        expected_key = "pkg-007:zyklus-007:2"
        assert result.idempotency_key == expected_key
