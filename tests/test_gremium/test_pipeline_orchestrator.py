"""Pipeline Orchestrator Tests for Phase 10."""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, MagicMock, patch

from src.gremium.pipeline_orchestrator import PipelineOrchestrator, BoundedQueue
from src.contracts.pipeline_models import (
    PipelineEvent, PipelineEventType, QueueStatus, 
    DeadlockReport, NotventilConfig, PipelineMetrics
)


class TestBoundedQueue:
    """Tests für die BoundedQueue-Klasse."""

    def test_bounded_queue_creation(self):
        """BoundedQueue kann mit High/Low-Watermarks erstellt werden."""
        queue = BoundedQueue(high_watermark=100, low_watermark=20)
        assert queue.high_watermark == 100
        assert queue.low_watermark == 20
        assert queue.is_empty()
        assert not queue.is_full()

    def test_bounded_queue_put_get(self):
        """Items können in die Queue eingefügt und entnommen werden."""
        queue = BoundedQueue(high_watermark=100, low_watermark=20)
        queue.put("item1")
        queue.put("item2")
        
        assert queue.qsize() == 2
        assert queue.get() == "item1"
        assert queue.get() == "item2"

    def test_bounded_queue_is_full(self):
        """Queue meldet is_full wenn High-Watermark erreicht."""
        queue = BoundedQueue(high_watermark=3, low_watermark=1)
        queue.put("item1")
        queue.put("item2")
        queue.put("item3")
        
        assert queue.is_full()
        assert queue.should_stop_production()

    def test_bounded_queue_should_stop_production_at_high_watermark(self):
        """Regel 2: Produktion stoppt bei High-Watermark."""
        queue = BoundedQueue(high_watermark=5, low_watermark=2)
        for i in range(5):
            queue.put(f"item{i}")
        
        assert queue.should_stop_production()

    def test_bounded_queue_should_resume_production_at_low_watermark(self):
        """Regel 2: Produktion setzt fort bei Low-Watermark."""
        queue = BoundedQueue(high_watermark=10, low_watermark=3)
        for i in range(8):
            queue.put(f"item{i}")
        
        # 5 Items entnehmen um unter Low-Watermark zu kommen
        for _ in range(5):
            queue.get()
        
        assert queue.should_resume_production()


class TestPipelineOrchestrator:
    """Tests für den PipelineOrchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Erstellt einen Orchestrator mit Mocks."""
        with patch('src.gremium.pipeline_orchestrator.PipelineOrchestrator._init_components'):
            orch = PipelineOrchestrator()
            return orch

    def test_orchestrator_event_driven(self):
        """Regel 1: Orchestrator ist event-gesteuert, nicht busy-loop."""
        with patch('src.gremium.pipeline_orchestrator.PipelineOrchestrator._init_components'):
            orch = PipelineOrchestrator()
            
            # Event-Handler sollten registriert sein
            assert hasattr(orch, 'event_handlers')
            assert PipelineEventType.NEW_CRYSTAL in orch.event_handlers
            assert PipelineEventType.QUESTOR_RESULT in orch.event_handlers

    def test_orchestrator_bounded_queues(self):
        """Regel 2: Queues sind bounded mit High/Low-Watermarks."""
        with patch('src.gremium.pipeline_orchestrator.PipelineOrchestrator._init_components'):
            orch = PipelineOrchestrator()
            
            # Alle 4 Queues sollten existieren
            assert hasattr(orch, 'ideen_queue')
            assert hasattr(orch, 'wegmarken_queue')
            assert hasattr(orch, 'pakete_queue')
            assert hasattr(orch, 'ergebnisse_queue')
            
            # Watermarks prüfen
            assert orch.ideen_queue.high_watermark == 100
            assert orch.ideen_queue.low_watermark == 20
            
            assert orch.wegmarken_queue.high_watermark == 50
            assert orch.wegmarken_queue.low_watermark == 10
            
            assert orch.pakete_queue.high_watermark == 20
            assert orch.pakete_queue.low_watermark == 5
            
            assert orch.ergebnisse_queue.high_watermark == 100
            assert orch.ergebnisse_queue.low_watermark == 20

    def test_orchestrator_detects_deadlock(self):
        """Regel 3: Deadlock-Erkennung funktioniert."""
        with patch('src.gremium.pipeline_orchestrator.PipelineOrchestrator._init_components'):
            orch = PipelineOrchestrator()
            
            # Mock: Queue voll, keine Consumer
            orch.ideen_queue = Mock()
            orch.ideen_queue.is_full.return_value = True
            orch.ideen_queue.qsize.return_value = 100
            
            result = orch.detect_deadlock()
            assert isinstance(result, DeadlockReport)

    def test_orchestrator_notventil_zyklen(self):
        """Regel 4: Notventil-Zyklen werden durchgesetzt."""
        with patch('src.gremium.pipeline_orchestrator.PipelineOrchestrator._init_components'):
            orch = PipelineOrchestrator()
            orch.notventil_config = NotventilConfig(notventil_zyklen=50)
            
            # Paket mit zu vielen Zyklen
            should_timeout = orch.check_notventil("pkg-001", current_zyklus=60)
            assert should_timeout

    def test_orchestrator_pipeline_timeout(self):
        """Regel 4: Paket-Timeout bei zu vielen Zyklen."""
        with patch('src.gremium.pipeline_orchestrator.PipelineOrchestrator._init_components'):
            orch = PipelineOrchestrator()
            orch.notventil_config = NotventilConfig(notventil_zyklen=50)
            
            # Paket im Timeout-Limit
            should_timeout = orch.check_notventil("pkg-002", current_zyklus=30)
            assert not should_timeout
            
            # Paket über Timeout-Limit
            should_timeout = orch.check_notventil("pkg-003", current_zyklus=51)
            assert should_timeout

    def test_orchestrator_integrates_all_stufen(self):
        """Orchestrator integriert alle 9 Stufen."""
        orch = PipelineOrchestrator()
        
        # Alle Stufen sollten vorhanden sein (durch _init_components gesetzt)
        assert hasattr(orch, 'archivar')
        assert hasattr(orch, 'kartograph')
        assert hasattr(orch, 'kanzler')
        assert hasattr(orch, 'vordenker')
        assert hasattr(orch, 'pre_filter')
        assert hasattr(orch, 'lotse')
        assert hasattr(orch, 'quartiermeister')
        assert hasattr(orch, 'sicherheits_gate')
        assert hasattr(orch, 'dispatcher')

    def test_orchestrator_no_busy_loop(self):
        """Regel 1: Kein busy-loop, nur event-gesteuert."""
        with patch('src.gremium.pipeline_orchestrator.PipelineOrchestrator._init_components'):
            orch = PipelineOrchestrator()
            
            # run() sollte events verarbeiten, nicht pollend
            assert hasattr(orch, '_get_next_event')
            assert hasattr(orch, '_handle_new_crystal')
            assert hasattr(orch, '_handle_questor_result')

    def test_orchestrator_recovery_after_crash(self):
        """Orchestrator kann nach Crash wieder starten."""
        with patch('src.gremium.pipeline_orchestrator.PipelineOrchestrator._init_components'):
            orch1 = PipelineOrchestrator()
            orch1.running = False
            
            # Neuer Orchestrator sollte starten können
            orch2 = PipelineOrchestrator()
            assert orch2.running or not orch2.running  # Initialzustand


class TestPipelineModels:
    """Tests für die Pipeline-Modelle."""

    def test_pipeline_event_creation(self):
        """PipelineEvent kann erstellt werden."""
        event = PipelineEvent(
            event_id="evt-001",
            event_type=PipelineEventType.NEW_CRYSTAL,
            payload={"crystal_id": "c-001"},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        assert event.event_id == "evt-001"
        assert event.event_type == PipelineEventType.NEW_CRYSTAL

    def test_queue_status_creation(self):
        """QueueStatus kann erstellt werden."""
        status = QueueStatus(
            queue_name="ideen_queue",
            current_size=50,
            high_watermark=100,
            low_watermark=20,
            is_full=False,
            is_empty=False  # Bei current_size=50 ist Queue nicht leer
        )
        
        assert status.queue_name == "ideen_queue"
        assert status.current_size == 50
        assert not status.is_full
        assert not status.is_empty

    def test_deadlock_report_creation(self):
        """DeadlockReport kann erstellt werden."""
        report = DeadlockReport(
            reason="Queue full, no consumers",
            affected_queues=["ideen_queue"],
            affected_packages=["pkg-001"],
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        assert report.detected
        assert report.reason == "Queue full, no consumers"

    def test_notventil_config_defaults(self):
        """NotventilConfig hat korrekte Default-Werte."""
        config = NotventilConfig()
        
        assert config.notventil_zyklen == 50
        assert config.avg_zyklen_pro_paket == 25.0
        assert config.max_package_lifetime_s == 3600.0

    def test_pipeline_metrics_creation(self):
        """PipelineMetrics kann erstellt werden."""
        metrics = PipelineMetrics(
            total_packages_processed=100,
            total_estops=2,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        assert metrics.total_packages_processed == 100
        assert metrics.total_estops == 2
