"""Tests for Dummy Questor implementation."""

import pytest

from src.contracts.enums import AbbruchKlasse, ErgebnisStatus
from src.contracts.questor_dispatch import QuestorDispatchEnvelope
from src.contracts.questor_metadata import OperationalMetrics, QuestorMetadata
from src.contracts.research_package import ResearchPackage, RoutingGraph
from src.questor_interface.dummy_questor import DummyQuestor


class TestDummyQuestorInitialization:
    """Test DummyQuestor initialization."""

    def test_instance_id_generation(self):
        questor = DummyQuestor()
        assert questor._instance_id.startswith("dummy-questor-")
        assert len(questor._instance_id) == len("dummy-questor-") + 8

    def test_initial_sequence_counter(self):
        questor = DummyQuestor()
        assert questor._sequence_counter == 0


class TestDummyQuestorExecute:
    """Test DummyQuestor execute method."""

    def _create_minimal_dispatch(self) -> QuestorDispatchEnvelope:
        return QuestorDispatchEnvelope(
            dispatch_id="dispatch-test-001",
            zyklus_id="zyklus-test-001",
            attempt_id=0,
            package=ResearchPackage(
                package_id="pkg-test-001",
                source_wegmarke="wegmarke-v1",
                atlas_version_ref="atlas-v1.0",
                ziel="test target",
                routing_graph=RoutingGraph(
                    max_loop_iterations=10,
                    branch_condition_timeout=5.0,
                ),
            ),
            gate_record_ref="gate-rec-test-001",
            dispatch_timestamp="2024-01-01T00:00:00Z",
        )

    def test_execute_returns_result(self):
        questor = DummyQuestor()
        dispatch = self._create_minimal_dispatch()
        result = questor.execute(dispatch)
        assert result is not None

    def test_execute_result_package_ids(self):
        questor = DummyQuestor()
        dispatch = self._create_minimal_dispatch()
        result = questor.execute(dispatch)
        assert result.package_id == "pkg-test-001"
        assert result.zyklus_id == "zyklus-test-001"
        assert result.attempt_id == 0

    def test_execute_result_status(self):
        questor = DummyQuestor()
        dispatch = self._create_minimal_dispatch()
        result = questor.execute(dispatch)
        assert result.status == ErgebnisStatus.ERFOLGREICH
        assert result.abbruch_klasse == AbbruchKlasse.OPERATIONAL
        assert result.abbruch_grund is None

    def test_execute_result_completeness(self):
        questor = DummyQuestor()
        dispatch = self._create_minimal_dispatch()
        result = questor.execute(dispatch)
        assert result.vollstaendig_flag is True
        assert result.rohdaten_checksumme.startswith("sha256-dummy-")

    def test_execute_result_metadata(self):
        questor = DummyQuestor()
        dispatch = self._create_minimal_dispatch()
        result = questor.execute(dispatch)
        assert result.questor_metadata is not None
        assert result.questor_metadata.questor_version == "0.2.3-dummy"
        assert result.questor_metadata.operational_metrics is not None

    def test_execute_increments_sequence(self):
        questor = DummyQuestor()
        dispatch = self._create_minimal_dispatch()

        result1 = questor.execute(dispatch)
        assert result1.sequence_number == 1

        result2 = questor.execute(dispatch)
        assert result2.sequence_number == 2

        result3 = questor.execute(dispatch)
        assert result3.sequence_number == 3

    def test_execute_observed_atlas_version(self):
        questor = DummyQuestor()
        dispatch = self._create_minimal_dispatch()
        result = questor.execute(dispatch)
        assert result.observed_atlas_version_id == "atlas-v1.0"

    def test_execute_empty_collections(self):
        questor = DummyQuestor()
        dispatch = self._create_minimal_dispatch()
        result = questor.execute(dispatch)
        assert result.kristall_kandidaten == []
        assert result.gefahren_beobachtet == []
        assert result.signale_fuer_atlas == []
        assert result.routing_checkpoint == {}
        assert result.ergebnis_daten == {}
        assert result.validierung == {}


class TestDummyQuestorInterfaceCompliance:
    """Test that DummyQuestor implements QuestorInterface correctly."""

    def test_has_execute_method(self):
        questor = DummyQuestor()
        assert hasattr(questor, "execute")
        assert callable(questor.execute)
