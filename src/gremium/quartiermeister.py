"""Quartiermeister: Baut research_packages aus Wegmarken (Stufe 6)."""

import uuid
from datetime import datetime, timezone
from typing import Optional, Any

from pydantic import BaseModel, Field

from src.contracts.research_package import (
    ResearchPackage,
    RoutingGraph,
    RoutingNode,
    RoutingEdge,
)
from src.contracts.pipeline_models import (
    PackageKontext,
    QuartiermeisterState,
    LeaseReservation,
    LotseEvent,
)
from src.contracts.enums import GateDecision


class QuartiermeisterEvent(BaseModel):
    """QuartiermeisterEvent: Protokolliertes Event eines Zustandsübergangs."""

    model_config = {"extra": "forbid"}

    event_id: str = Field(..., min_length=1)
    package_id: str = Field(..., min_length=1)
    from_state: QuartiermeisterState
    to_state: QuartiermeisterState
    timestamp: str = Field(..., min_length=1)
    reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class QuartiermeisterResult(BaseModel):
    """QuartiermeisterResult: Ergebnis des Paket-Baus."""

    model_config = {"extra": "forbid"}

    decision: str  # PAKET_ERSTELLT, VERWORFEN, GATE_PENDING
    package: ResearchPackage | None = None
    lease_reservation: LeaseReservation | None = None
    quartiermeister_event: QuartiermeisterEvent | None = None
    reason: str | None = None


class Quartiermeister:
    """
    Quartiermeister (Stufe 6): Baut research_packages aus Wegmarken.

    Regel 1: routing_graph ist ein GERICHTETER GRAPH (keine lineare Liste)
    Regel 2: dimension_expansion_approval wird VOR physischer Execution geprüft
    Regel 3: Zustandsmaschine mit LOCKED_GATE_PENDING
    Regel 4: lease_reservation wird beim Resource Governor angefordert
    Regel 5: materials_or_resources ist domain-neutral
    Regel 6: Jeder Zustandsübergang wird im WAL protokolliert
    """

    VALID_TRANSITIONS = {
        QuartiermeisterState.WEGMARKE_RESERVIERT: [
            QuartiermeisterState.PAKET_ENTWURF,
            QuartiermeisterState.PAKET_VERWORFEN,
        ],
        QuartiermeisterState.PAKET_ENTWURF: [QuartiermeisterState.LOCKED_GATE_PENDING],
        QuartiermeisterState.LOCKED_GATE_PENDING: [
            QuartiermeisterState.GATE_APPROVED,
            QuartiermeisterState.PAKET_VERWORFEN,
        ],
        QuartiermeisterState.GATE_APPROVED: [QuartiermeisterState.LOCKED_READY_TO_EXEC],
        QuartiermeisterState.LOCKED_READY_TO_EXEC: [QuartiermeisterState.PAKET_FERTIG],
    }

    def __init__(self, wal, resource_governor=None):
        """
        Initialisiere den Quartiermeister.

        Args:
            wal: Write-Ahead-Log für Zustandsübergänge
            resource_governor: Resource Governor für lease_reservations
        """
        self.wal = wal
        self.resource_governor = resource_governor
        self._state_cache: dict[str, QuartiermeisterState] = {}

    def build_package(
        self, wegmarke, atlas, execution_environment=None
    ) -> QuartiermeisterResult:
        """
        Baue ein research_package aus einer Wegmarke.

        Args:
            wegmarke: Die Wegmarke, aus der das Paket gebaut wird
            atlas: Der Atlas für Dimensions- und Versionsinformationen
            execution_environment: Optionale Ausführungsumgebung

        Returns:
            QuartiermeisterResult mit dem erstellten Paket oder Ablehnungsgrund
        """
        # Schritt 1: lease_reservation anfordern (Regel 4)
        lease_reservation = self._request_lease_reservation(wegmarke)
        if not lease_reservation or lease_reservation.status != "ACTIVE":
            return QuartiermeisterResult(
                decision="VERWORFEN",
                reason="LEASE_DENIED",
                lease_reservation=lease_reservation,
            )

        # Zustand: WEGMARKE_RESERVIERT
        package_id = f"pkg-{uuid.uuid4().hex[:16]}"
        self._set_state(package_id, QuartiermeisterState.WEGMARKE_RESERVIERT)

        # Schritt 2: routing_graph bauen (Regel 1 - gerichteter Graph)
        routing_graph = self.build_routing_graph(wegmarke, execution_environment)

        # Schritt 3: materials_or_resources extrahieren (Regel 5 - domain-neutral)
        materials = self.extract_materials(wegmarke)

        # Schritt 4: dimension_expansion_approval prüfen (Regel 2)
        dimension_approval_ok = self.check_dimension_approval(
            package_id, routing_graph, atlas
        )
        if not dimension_approval_ok:
            self._transition_state(
                package_id,
                QuartiermeisterState.WEGMARKE_RESERVIERT,
                QuartiermeisterState.PAKET_VERWORFEN,
                reason="DIMENSION_APPROVAL_MISSING",
            )
            return QuartiermeisterResult(
                decision="VERWORFEN",
                reason="DIMENSION_APPROVAL_MISSING",
                lease_reservation=lease_reservation,
            )

        # Schritt 5: ResearchPackage erstellen
        kontext = PackageKontext(
            kontext_id=f"ctx-{uuid.uuid4().hex[:8]}",
            domaene="exploration",
            beschreibung=f"Paket für Wegmarke {wegmarke.wegmarke_id}",
            erwartete_transformation="Erkundung neuer Zone",
        )

        package = ResearchPackage(
            package_id=package_id,
            source_wegmarke=wegmarke.wegmarke_id,
            source_wegmarke_version=wegmarke.version,
            atlas_version_ref=atlas.atlas_version_id
            if hasattr(atlas, "atlas_version_id")
            else "unknown",
            ziel=f"Erkunde {wegmarke.name}",
            materials_or_resources=materials,
            parameter_bounds={},
            routing_graph=routing_graph,
            gefahren_mitigationen=[],
            kontext=kontext,
            dimension_expansion_approval=None,
            override_requested=False,
            limits={},
            expected_side_effects_or_failure_modes=[],
            domain_metadata={},
            questor_spec=None,
        )

        # Zustand: PAKET_ENTWURF
        self._transition_state(
            package_id,
            QuartiermeisterState.WEGMARKE_RESERVIERT,
            QuartiermeisterState.PAKET_ENTWURF,
            reason="Paket erstellt",
        )

        # Zustand: LOCKED_GATE_PENDING (wartet auf Gate-Entscheidung)
        self._transition_state(
            package_id,
            QuartiermeisterState.PAKET_ENTWURF,
            QuartiermeisterState.LOCKED_GATE_PENDING,
            reason="Wartet auf Gate-Prüfung",
        )

        # gate_record-Anfrage würde hier erfolgen (Phase 8b)
        # Für jetzt: Paket ist bereit für Gate-Prüfung

        return QuartiermeisterResult(
            decision="GATE_PENDING",
            package=package,
            lease_reservation=lease_reservation,
            quartiermeister_event=self._create_event(
                package_id,
                QuartiermeisterState.PAKET_ENTWURF,
                QuartiermeisterState.LOCKED_GATE_PENDING,
            ),
        )

    def build_routing_graph(self, wegmarke, execution_environment=None) -> RoutingGraph:
        """
        Baue einen gerichteten routing_graph (Regel 1).

        Der routing_graph ist KEINE lineare Liste, sondern ein gerichteter Graph
        mit nodes, edges, max_loop_iterations und branch_condition_timeout.
        """
        nodes = []
        edges = []

        # Knoten aus execution_environment und Wegmarke bauen
        slot_ids = getattr(wegmarke, "slot_ids", ["default-slot"])
        if not slot_ids:
            slot_ids = ["default-slot"]

        for i, slot_id in enumerate(slot_ids):
            capability = (
                execution_environment.get_capability(slot_id)
                if execution_environment and hasattr(execution_environment, "get_capability")
                else f"capability-{slot_id}"
            )
            node = RoutingNode(
                node_id=f"node-{i}-{slot_id}",
                capability=capability,
                slot_id=slot_id,
                parameters={},
            )
            nodes.append(node)

        # Kanten bauen (gerichteter Graph)
        for i in range(len(nodes) - 1):
            edge = RoutingEdge(
                from_node=nodes[i].node_id,
                to_node=nodes[i + 1].node_id,
                condition="success",
                priority=i,
            )
            edges.append(edge)

        # Falls nur ein Knoten existiert, erstelle eine Selbstkante
        if len(nodes) == 1:
            edges.append(
                RoutingEdge(
                    from_node=nodes[0].node_id,
                    to_node=nodes[0].node_id,
                    condition="complete",
                    priority=0,
                )
            )

        # KRITISCH: max_loop_iterations und branch_condition_timeout sind Pflichtfelder
        max_loop_iterations = (
            getattr(execution_environment, "max_loop_iterations", 10)
            if execution_environment
            else 10
        )
        branch_condition_timeout = (
            getattr(execution_environment, "branch_condition_timeout", 5.0)
            if execution_environment
            else 5.0
        )

        return RoutingGraph(
            nodes=nodes,
            edges=edges,
            max_loop_iterations=max_loop_iterations,
            branch_condition_timeout=branch_condition_timeout,
            entry_node_id=nodes[0].node_id if nodes else None,
        )

    def extract_materials(self, wegmarke) -> list[str]:
        """
        Extrahiere domain-neutrale Materialien (Regel 5).

        Keine gerätespezifischen Bezeichnungen, nur abstrakte Kategorien.
        """
        # Domain-neutrale Materialbeschreibung
        materials = []

        # Basierend auf Wegmarken-Typ
        wegmarke_typ = getattr(wegmarke, "typ", getattr(wegmarke, "wegmarke_typ", "NORMAL"))
        if wegmarke_typ == "DIAGNOSTIC":
            materials.extend(["diagnostic_sample", "analysis_medium"])
        else:
            materials.extend(["liquid_sample", "solid_substrate"])

        # Immer benötigte Ressourcen
        materials.extend(["compute_node", "energy_unit"])

        return materials

    def check_dimension_approval(
        self, package_id: str, routing_graph: RoutingGraph, atlas
    ) -> bool:
        """
        Prüfe dimension_expansion_approval VOR physischer Execution (Regel 2).

        Wenn das Paket eine neue Dimension nutzt, die noch nicht freigegeben ist,
        MUSS dimension_expansion_approval gesetzt sein.
        """
        # Prüfe alle Dimensionen im routing_graph
        for node in routing_graph.nodes:
            dimension = node.slot_id  # Oder node.capability, je nach Modell
            if hasattr(atlas, "dimension_schema"):
                if not atlas.dimension_schema.has_dimension(dimension):
                    # Neue Dimension ohne Approval
                    self._create_dimension_onboarding_request(dimension, package_id)
                    return False

        return True

    def _request_lease_reservation(self, wegmarke) -> LeaseReservation | None:
        """
        Fordere lease_reservation beim Resource Governor an (Regel 4).

        Kurzlebige Reservation mit TTL. Bei Fehlschlag: LEASE_DENIED (OPERATIONAL).
        """
        if not self.resource_governor:
            # Mock-Reservation für Tests ohne Resource Governor
            return LeaseReservation(
                reservation_id=f"res-{uuid.uuid4().hex[:16]}",
                package_id="pending",
                slot_ids=getattr(wegmarke, "slot_ids", ["default-slot"]),
                ttl_s=300.0,  # 5 Minuten TTL
                status="ACTIVE",
                created_at=datetime.now(timezone.utc).isoformat(),
            )

        # Echte Anfrage an Resource Governor
        try:
            reservation = self.resource_governor.request_lease(
                slot_ids=getattr(wegmarke, "slot_ids", ["default-slot"]),
                ttl_s=300.0,
            )
            return reservation
        except Exception:
            return LeaseReservation(
                reservation_id=f"res-{uuid.uuid4().hex[:16]}",
                package_id="pending",
                slot_ids=[],
                ttl_s=300.0,
                status="DENIED",
                created_at=datetime.now(timezone.utc).isoformat(),
            )

    def _create_dimension_onboarding_request(
        self, dimension: str, package_id: str
    ) -> None:
        """Erzeuge dimension_onboarding_request für neue Dimension."""
        # Wird in Phase 9 implementiert
        pass

    def _set_state(self, package_id: str, state: QuartiermeisterState) -> None:
        """Setze den Zustand eines Pakets."""
        self._state_cache[package_id] = state

    def _get_state(self, package_id: str) -> QuartiermeisterState | None:
        """Hole den Zustand eines Pakets."""
        return self._state_cache.get(package_id)

    def _transition_state(
        self,
        package_id: str,
        from_state: QuartiermeisterState,
        to_state: QuartiermeisterState,
        reason: str | None = None,
    ) -> None:
        """
        Führe einen Zustandsübergang durch und protokolliere im WAL (Regel 6).
        """
        # Validierung des Übergangs
        valid_targets = self.VALID_TRANSITIONS.get(from_state, [])
        if to_state not in valid_targets:
            raise ValueError(
                f"Ungültiger Übergang: {from_state} → {to_state}. "
                f"Erlaubt: {valid_targets}"
            )

        # WAL-Protokollierung
        event = self._create_event(package_id, from_state, to_state, reason)
        if self.wal:
            self.wal.log_event(event.model_dump())

        # Zustand aktualisieren
        self._set_state(package_id, to_state)

    def _create_event(
        self,
        package_id: str,
        from_state: QuartiermeisterState,
        to_state: QuartiermeisterState,
        reason: str | None = None,
    ) -> QuartiermeisterEvent:
        """Erzeuge ein QuartiermeisterEvent."""
        return QuartiermeisterEvent(
            event_id=f"evt-{uuid.uuid4().hex[:16]}",
            package_id=package_id,
            from_state=from_state,
            to_state=to_state,
            timestamp=datetime.now(timezone.utc).isoformat(),
            reason=reason,
        )

    def handle_gate_decision(
        self, package_id: str, gate_decision: GateDecision
    ) -> QuartiermeisterResult:
        """
        Verarbeite Gate-Entscheidung.

        Args:
            package_id: ID des Pakets
            gate_decision: Entscheidung des Sicherheits-Gates

        Returns:
            QuartiermeisterResult mit aktualisiertem Zustand
        """
        current_state = self._get_state(package_id)
        if current_state != QuartiermeisterState.LOCKED_GATE_PENDING:
            return QuartiermeisterResult(
                decision="ERROR",
                reason=f"Ungültiger Zustand: {current_state}",
            )

        if gate_decision == GateDecision.FREIGEGEBEN:
            self._transition_state(
                package_id,
                QuartiermeisterState.LOCKED_GATE_PENDING,
                QuartiermeisterState.GATE_APPROVED,
                reason="Gate genehmigt",
            )
            self._transition_state(
                package_id,
                QuartiermeisterState.GATE_APPROVED,
                QuartiermeisterState.LOCKED_READY_TO_EXEC,
                reason="Bereit zur Ausführung",
            )
            return QuartiermeisterResult(
                decision="LOCKED_READY_TO_EXEC",
                reason="Gate genehmigt, bereit zur Ausführung",
            )
        else:
            self._transition_state(
                package_id,
                QuartiermeisterState.LOCKED_GATE_PENDING,
                QuartiermeisterState.PAKET_VERWORFEN,
                reason=f"Gate abgelehnt: {gate_decision}",
            )
            return QuartiermeisterResult(
                decision="VERWORFEN",
                reason=f"Gate abgelehnt: {gate_decision}",
            )

    def complete_package(self, package_id: str) -> QuartiermeisterResult:
        """
        Schließe das Paket ab (PAKET_FERTIG).

        Args:
            package_id: ID des Pakets

        Returns:
            QuartiermeisterResult mit abgeschlossenem Paket
        """
        current_state = self._get_state(package_id)
        if current_state != QuartiermeisterState.LOCKED_READY_TO_EXEC:
            return QuartiermeisterResult(
                decision="ERROR",
                reason=f"Ungültiger Zustand: {current_state}",
            )

        self._transition_state(
            package_id,
            QuartiermeisterState.LOCKED_READY_TO_EXEC,
            QuartiermeisterState.PAKET_FERTIG,
            reason="Paket fertiggestellt",
        )

        return QuartiermeisterResult(
            decision="PAKET_FERTIG",
            reason="Paket fertiggestellt",
        )

    def get_recovery_state(self, package_id: str) -> QuartiermeisterState | None:
        """
        Hole den Recovery-Zustand für ein Paket.

        KRITISCH: LOCKED_GATE_PENDING geht zurück in Stufe 7 (Gate-Prüfung),
        NICHT in Stufe 8 (Dispatch).
        """
        state = self._get_state(package_id)
        if state == QuartiermeisterState.LOCKED_GATE_PENDING:
            # Recovery: Zurück zu PAKET_ENTWURF für erneute Gate-Prüfung
            return QuartiermeisterState.PAKET_ENTWURF
        return state
