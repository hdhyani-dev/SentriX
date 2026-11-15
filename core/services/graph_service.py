"""
Graph service — orchestrates graph construction, querying, and serializing for a lab.
"""

from typing import Any
import networkx as nx
from sqlalchemy.orm import Session

from core.graph.builder import graph_builder
from core.graph.algorithms import graph_algorithms
from core.graph.serializers import graph_serializer
from core.models.enums import EventType
from database.repositories import audit_log_repo


class GraphService:
    """High-level service for graph construction and analysis."""

    def __init__(self):
        self._builder = graph_builder
        self._algorithms = graph_algorithms
        self._serializer = graph_serializer

    def build_graph(self, session: Session, lab_id: str, max_nodes: int = 1000) -> nx.DiGraph | nx.MultiDiGraph:
        """Construct the NetworkX graph for a given lab."""
        G = self._builder.build(session, lab_id, max_nodes=max_nodes)
        audit_log_repo.create(
            session,
            lab_id=lab_id,
            event_type=EventType.GRAPH_BUILT.value,
            target_type="laboratory",
            target_id=lab_id,
            reason=f"Graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.",
        )
        return G

    def get_plotly_figure(
        self,
        session: Session,
        lab_id: str,
        highlight_path: list[str] | None = None,
    ) -> Any:
        """Generate interactive Plotly visualization for the lab graph."""
        G = self.build_graph(session, lab_id)
        return self._serializer.create_network_plotly_figure(G, highlight_path=highlight_path)

    def get_graph_stats(self, session: Session, lab_id: str) -> dict[str, Any]:
        """Build and calculate stats for a lab's graph."""
        G = self.build_graph(session, lab_id)
        return self._algorithms.graph_stats(G)

    def get_serialized_graph(self, session: Session, lab_id: str) -> dict[str, Any]:
        """Return Cytoscape and node-link representations of the lab graph."""
        G = self.build_graph(session, lab_id)
        return {
            "cytoscape": self._serializer.to_cytoscape_elements(G),
            "node_link": self._serializer.to_node_link_data(G),
            "stats": self._algorithms.graph_stats(G),
        }

    def get_node_details(self, session: Session, lab_id: str, node_id: str) -> dict[str, Any] | None:
        """Retrieve details of a specific node in the graph."""
        G = self.build_graph(session, lab_id)
        return self._algorithms.get_node_details(G, node_id)


graph_service = GraphService()
