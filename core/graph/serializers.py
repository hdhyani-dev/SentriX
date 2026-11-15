"""
Graph serializers — exports NetworkX graphs to JSON/dictionary formats for visualization and API consumers.
"""

from typing import Any
import networkx as nx

from core.models.enums import NodeType


class GraphSerializer:
    """Serializes a NetworkX DiGraph for UI rendering and API consumption."""

    @staticmethod
    def to_cytoscape_elements(G: nx.DiGraph) -> list[dict[str, Any]]:
        """Export graph to Cytoscape-compatible elements list (nodes and edges)."""
        elements: list[dict[str, Any]] = []

        # Color mapping for node types
        color_map = {
            NodeType.ASSET.value: "#2563EB",       # Blue
            NodeType.SERVICE.value: "#059669",     # Green
            NodeType.FINDING.value: "#DC2626",     # Red
            NodeType.PERMISSION.value: "#D97706",  # Amber
            NodeType.CONTROL.value: "#7C3AED",     # Purple
        }

        for node_id, data in G.nodes(data=True):
            node_type = data.get("node_type", "unknown")
            elements.append({
                "data": {
                    "id": node_id,
                    "label": data.get("label", node_id),
                    "node_type": node_type,
                    "color": color_map.get(node_type, "#6B7280"),
                    **data,
                }
            })

        for u, v, data in G.edges(data=True):
            elements.append({
                "data": {
                    "id": f"{u}->{v}",
                    "source": u,
                    "target": v,
                    "label": data.get("relationship_type", "relates_to"),
                    "evidence_status": data.get("evidence_status", "observed"),
                    **data,
                }
            })

        return elements

    @staticmethod
    def to_node_link_data(G: nx.DiGraph) -> dict[str, Any]:
        """Export graph to standard node-link JSON format."""
        nodes = []
        for n, d in G.nodes(data=True):
            nodes.append({"id": n, **d})

        links = []
        for u, v, d in G.edges(data=True):
            links.append({"source": u, "target": v, **d})

        return {"nodes": nodes, "links": links}


graph_serializer = GraphSerializer()
