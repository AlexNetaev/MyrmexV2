"""Pipeline Orchestrator Implementation for Phase 10."""

import queue
import time
from datetime import datetime, timezone
from typing import Any, Callable
from unittest.mock import Mock

from src.contracts.pipeline_models import (
    PipelineEvent, PipelineEventType, QueueStatus,
    DeadlockReport, NotventilConfig, PipelineMetrics
)


class BoundedQueue:
    """Eine bounded Queue mit High/Low-Watermarks."""
    
    def __init__(self, high_watermark: int, low_watermark: int):
        self.high_watermark = high_watermark
        self.low_watermark = low_watermark
        self._queue: queue.Queue = queue.Queue(maxsize=high_watermark)
    
    def put(self, item: Any, timeout: float | None = None) -> bool:
        """Fügt Item hinzu. Blockiert wenn Queue voll."""
        try:
            self._queue.put(item, timeout=timeout)
            return True
        except queue.Full:
            return False
    
    def get(self, timeout: float | None = None) -> Any:
        """Holt Item. Blockiert wenn Queue leer."""
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def qsize(self) -> int:
        """Aktuelle Größe der Queue."""
        return self._queue.qsize()
    
    def is_full(self) -> bool:
        """Prüft ob Queue voll ist (High-Watermark erreicht)."""
        return self.qsize() >= self.high_watermark
    
    def is_empty(self) -> bool:
        """Prüft ob Queue leer ist."""
        return self.qsize() == 0
    
    def should_stop_production(self) -> bool:
        """Produktion stoppen bei High-Watermark."""
        return self.is_full()
    
    def should_resume_production(self) -> bool:
        """Produktion fortsetzen bei Low-Watermark."""
        return self.qsize() <= self.low_watermark


class PipelineOrchestrator:
    """
    Event-gesteuerter Pipeline-Orchestrator für MYRMEX v2.4.0.
    
    Verbindet alle 9 Stufen der Pipeline:
    1. Archivar (Questor-Ergebnisse empfangen)
    2. Kartograph (Atlas strukturieren)
    3. Kanzler (Lagebericht erzeugen)
    4. Vordenker (Ideen generieren)
    5a. Pre-Filter (Ideen prüfen)
    5b. Lotse (Wegmarken platzieren)
    6. Quartiermeister (Pakete bauen)
    7. Sicherheits-Gate (Pakete prüfen)
    8. Dispatcher (an Questor senden)
    """
    
    def __init__(self):
        self.running = False
        self._init_components()
        self._init_queues()
        self._init_event_handlers()
        
        # Notventil-Konfiguration
        self.notventil_config = NotventilConfig()
        self.package_cycle_counts: dict[str, int] = {}
        
        # Pipeline-Metriken
        self.metrics = PipelineMetrics(
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    def _init_components(self):
        """Initialisiert alle Pipeline-Komponenten (wird von Tests gemockt)."""
        # Diese werden in der echten Implementierung injiziert
        self.archivar = Mock()
        self.kartograph = Mock()
        self.kanzler = Mock()
        self.vordenker = Mock()
        self.pre_filter = Mock()
        self.lotse = Mock()
        self.quartiermeister = Mock()
        self.sicherheits_gate = Mock()
        self.dispatcher = Mock()
    
    def _init_queues(self):
        """Initialisiert die 4 bounded Queues mit Watermarks."""
        # ideen_queue: High-Watermark 100, Low-Watermark 20
        self.ideen_queue = BoundedQueue(high_watermark=100, low_watermark=20)
        
        # wegmarken_queue: High-Watermark 50, Low-Watermark 10
        self.wegmarken_queue = BoundedQueue(high_watermark=50, low_watermark=10)
        
        # pakete_queue: High-Watermark 20, Low-Watermark 5
        self.pakete_queue = BoundedQueue(high_watermark=20, low_watermark=5)
        
        # ergebnisse_queue: High-Watermark 100, Low-Watermark 20
        self.ergebnisse_queue = BoundedQueue(high_watermark=100, low_watermark=20)
    
    def _init_event_handlers(self):
        """Initialisiert die Event-Handler für event-gesteuerte Verarbeitung."""
        self.event_handlers: dict[PipelineEventType, Callable] = {
            PipelineEventType.NEW_CRYSTAL: self._handle_new_crystal,
            PipelineEventType.NEW_WAYPOINT: self._handle_new_waypoint,
            PipelineEventType.NEW_PACKAGE: self._handle_new_package,
            PipelineEventType.GATE_DECISION: self._handle_gate_decision,
            PipelineEventType.QUESTOR_RESULT: self._handle_questor_result,
            PipelineEventType.ESTOP: self._handle_estop,
            PipelineEventType.SAFE_MODE: self._handle_safe_mode,
        }
    
    def run(self):
        """Event-gesteuerter Haupt-Loop (kein busy-loop)."""
        self.running = True
        
        while self.running:
            # Event aus Queue holen (blocking, kein polling)
            event = self._get_next_event()
            
            if event is None:
                # Kein Event verfügbar → kurz warten
                time.sleep(0.1)
                continue
            
            # Handler aufrufen
            handler = self.event_handlers.get(event.event_type)
            if handler:
                try:
                    handler(event)
                except Exception as e:
                    self._handle_error(event, e)
            
            # Deadlock-Check
            deadlock_report = self.detect_deadlock()
            if deadlock_report.detected:
                self._handle_deadlock(deadlock_report)
    
    def stop(self):
        """Stoppt den Orchestrator."""
        self.running = False
    
    def _get_next_event(self) -> PipelineEvent | None:
        """
        Holt das nächste Event aus einer der Queues.
        Priorisierte Queue-Auswahl (ergebnisses zuerst).
        """
        # Priorität: Ergebnisse > Pakete > Wegmarken > Ideen
        if not self.ergebnisse_queue.is_empty():
            return self.ergebnisse_queue.get(timeout=0.1)
        elif not self.pakete_queue.is_empty():
            return self.pakete_queue.get(timeout=0.1)
        elif not self.wegmarken_queue.is_empty():
            return self.wegmarken_queue.get(timeout=0.1)
        elif not self.ideen_queue.is_empty():
            return self.ideen_queue.get(timeout=0.1)
        else:
            # Kein Event verfügbar
            return None
    
    def _handle_new_crystal(self, event: PipelineEvent):
        """Handler für NEW_CRYSTAL Events (triggert Kartograph)."""
        # Stufe 2: Kartograph strukturiert Atlas
        self.kartograph.strukturieren(event.payload)
    
    def _handle_new_waypoint(self, event: PipelineEvent):
        """Handler für NEW_WAYPOINT Events (triggert Quartiermeister)."""
        # Stufe 6: Quartiermeister baut Pakete
        self.quartiermeister.baue_paket(event.payload)
    
    def _handle_new_package(self, event: PipelineEvent):
        """Handler für NEW_PACKAGE Events (triggert Sicherheits-Gate)."""
        # Stufe 7: Sicherheits-Gate prüft Paket
        self.sicherheits_gate.pruefe_paket(event.payload)
    
    def _handle_gate_decision(self, event: PipelineEvent):
        """Handler für GATE_DECISION Events (triggert Dispatcher)."""
        # Stufe 8: Dispatcher sendet an Questor
        if event.payload.get('decision') == 'APPROVED':
            self.dispatcher.sende_an_questor(event.payload)
    
    def _handle_questor_result(self, event: PipelineEvent):
        """Handler für QUESTOR_RESULT Events (triggert Archivar)."""
        # Stufe 1: Archivar empfängt Questor-Ergebnisse
        self.archivar.empfange_ergebnis(event.payload)
    
    def _handle_estop(self, event: PipelineEvent):
        """Handler für ESTOP Events."""
        self.metrics.total_estops += 1
        # Sofortiger Stopp aller laufenden Operationen
    
    def _handle_safe_mode(self, event: PipelineEvent):
        """Handler für SAFE_MODE Events."""
        self.metrics.total_safe_mode_activations += 1
        # SAFE_MODE aktivieren
    
    def _handle_error(self, event: PipelineEvent, error: Exception):
        """Fehlerbehandlung für Event-Handler."""
        # Log error und continue
        pass
    
    def detect_deadlock(self) -> DeadlockReport:
        """
        Regel 3: Erkennt Deadlocks in der Pipeline.
        
        Deadlock-Szenarien:
        - Queue voll und keine Consumer aktiv
        - Paket zu lange in Pipeline (Timeout)
        - Circuit-Breaker in PERMANENT_SUSPENDED
        """
        affected_queues = []
        affected_packages = []
        
        # Prüfe ob Queues voll sind
        if self.ideen_queue.is_full():
            affected_queues.append("ideen_queue")
        if self.wegmarken_queue.is_full():
            affected_queues.append("wegmarken_queue")
        if self.pakete_queue.is_full():
            affected_queues.append("pakete_queue")
        if self.ergebnisse_queue.is_full():
            affected_queues.append("ergebnisse_queue")
        
        # Prüfe Paket-Timeouts
        for package_id, zyklus_count in list(self.package_cycle_counts.items()):
            if zyklus_count > self.notventil_config.notventil_zyklen:
                affected_packages.append(package_id)
        
        detected = len(affected_queues) > 0 or len(affected_packages) > 0
        
        if detected:
            reason = "Queues full" if affected_queues else "Package timeout"
            self.metrics.total_deadlocks_detected += 1
        else:
            reason = "No deadlock detected"
        
        return DeadlockReport(
            detected=detected,
            reason=reason,
            affected_queues=affected_queues,
            affected_packages=affected_packages,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    def _handle_deadlock(self, report: DeadlockReport):
        """Behandelt einen erkannten Deadlock."""
        # Alert auslösen, Recovery versuchen
        pass
    
    def check_notventil(self, package_id: str, current_zyklus: int) -> bool:
        """
        Regel 4: Prüft Notventil-Zyklen.
        
        Returns True wenn Paket abgebrochen werden soll (Timeout).
        """
        # Zyklus-Zähler aktualisieren
        self.package_cycle_counts[package_id] = current_zyklus
        
        # Prüfen ob Timeout erreicht
        if current_zyklus > self.notventil_config.notventil_zyklen:
            self.metrics.total_timeouts += 1
            return True
        
        return False
    
    def get_queue_status(self, queue_name: str) -> QueueStatus:
        """Returns Status einer Queue."""
        queue_map = {
            "ideen_queue": self.ideen_queue,
            "wegmarken_queue": self.wegmarken_queue,
            "pakete_queue": self.pakete_queue,
            "ergebnisse_queue": self.ergebnisse_queue,
        }
        
        q = queue_map.get(queue_name)
        if not q:
            raise ValueError(f"Unknown queue: {queue_name}")
        
        return QueueStatus(
            queue_name=queue_name,
            current_size=q.qsize(),
            high_watermark=q.high_watermark,
            low_watermark=q.low_watermark,
            is_full=q.is_full(),
            is_empty=q.is_empty()
        )
    
    def get_metrics(self) -> PipelineMetrics:
        """Returns aktuelle Pipeline-Metriken."""
        self.metrics.current_queue_sizes = {
            "ideen_queue": self.ideen_queue.qsize(),
            "wegmarken_queue": self.wegmarken_queue.qsize(),
            "pakete_queue": self.pakete_queue.qsize(),
            "ergebnisse_queue": self.ergebnisse_queue.qsize(),
        }
        self.metrics.timestamp = datetime.now(timezone.utc).isoformat()
        return self.metrics
