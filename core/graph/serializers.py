"""
Graph serializers — exports NetworkX graphs to JSON/dictionary formats and Plotly visualizations.
"""

from typing import Any
import networkx as nx
import plotly.graph_objects as go

from core.models.enums import NodeType


class GraphSerializer:
    """Serializes NetworkX DiGraph and MultiDiGraph for UI rendering and API consumption."""

    @staticmethod
    def to_cytoscape_elements(G: nx.DiGraph | nx.MultiDiGraph) -> list[dict[str, Any]]:
        """Export graph to Cytoscape-compatible elements list (nodes and edges), supporting MultiDiGraph."""
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

        if isinstance(G, nx.MultiDiGraph):
            for u, v, key, data in G.edges(data=True, keys=True):
                edge_id = data.get("relationship_id") or f"{u}->{v}:{key}"
                elements.append({
                    "data": {
                        "id": edge_id,
                        "source": u,
                        "target": v,
                        "key": key,
                        "label": data.get("relationship_type", "relates_to"),
                        "evidence_status": data.get("evidence_status", "observed"),
                        **data,
                    }
                })
        else:
            for u, v, data in G.edges(data=True):
                edge_id = data.get("relationship_id") or f"{u}->{v}"
                elements.append({
                    "data": {
                        "id": edge_id,
                        "source": u,
                        "target": v,
                        "label": data.get("relationship_type", "relates_to"),
                        "evidence_status": data.get("evidence_status", "observed"),
                        **data,
                    }
                })

        return elements

    @staticmethod
    def to_node_link_data(G: nx.DiGraph | nx.MultiDiGraph) -> dict[str, Any]:
        """Export graph to standard node-link JSON format, supporting MultiDiGraph."""
        nodes = []
        for n, d in G.nodes(data=True):
            nodes.append({"id": n, **d})

        links = []
        if isinstance(G, nx.MultiDiGraph):
            for u, v, k, d in G.edges(data=True, keys=True):
                links.append({"source": u, "target": v, "key": k, **d})
        else:
            for u, v, d in G.edges(data=True):
                links.append({"source": u, "target": v, **d})

        return {"nodes": nodes, "links": links}

    @staticmethod
    def create_network_plotly_figure(
        G: nx.DiGraph | nx.MultiDiGraph,
        highlight_path: list[str] | None = None,
        layout_seed: int = 42,
    ) -> go.Figure:
        """Construct an interactive Plotly network graph visualization.

        Args:
            G: DiGraph or MultiDiGraph to visualize.
            highlight_path: Ordered list of node IDs forming a candidate path to highlight.
            layout_seed: Deterministic seed for reproducible node positioning.
        """
        fig = go.Figure()

        if G.number_of_nodes() == 0:
            fig.update_layout(
                title="Graph is empty — No nodes registered.",
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            )
            return fig

        # Compute deterministic 2D spring layout
        undirected_G = nx.Graph(G)
        pos = nx.spring_layout(undirected_G, seed=layout_seed, k=0.7, iterations=50)

        # Build path edge set for fast membership check
        path_node_set = set(highlight_path) if highlight_path else set()
        path_edge_set: set[tuple[str, str]] = set()
        if highlight_path and len(highlight_path) >= 2:
            for i in range(len(highlight_path) - 1):
                path_edge_set.add((highlight_path[i], highlight_path[i + 1]))

        # 1. Background (unhighlighted) edges
        bg_edge_x = []
        bg_edge_y = []
        hl_edge_x = []
        hl_edge_y = []

        edges_iter = G.edges() if not isinstance(G, nx.MultiDiGraph) else G.edges(keys=True)
        for edge in edges_iter:
            u, v = edge[0], edge[1]
            if u not in pos or v not in pos:
                continue
            x0, y0 = pos[u]
            x1, y1 = pos[v]

            if (u, v) in path_edge_set:
                hl_edge_x.extend([x0, x1, None])
                hl_edge_y.extend([y0, y1, None])
            else:
                bg_edge_x.extend([x0, x1, None])
                bg_edge_y.extend([y0, y1, None])

        # Add background edges
        if bg_edge_x:
            fig.add_trace(go.Scatter(
                x=bg_edge_x, y=bg_edge_y,
                mode="lines",
                line=dict(width=1.2, color="rgba(148, 163, 184, 0.4)"),
                hoverinfo="none",
                name="Topology Edge",
                showlegend=False,
            ))

        # Add highlighted path edges
        if hl_edge_x:
            fig.add_trace(go.Scatter(
                x=hl_edge_x, y=hl_edge_y,
                mode="lines",
                line=dict(width=3.5, color="#10B981"),
                hoverinfo="none",
                name="Candidate Risk Hop",
                showlegend=True,
            ))

        # Color mapping for node types
        type_palette = {
            NodeType.ASSET.value: {"color": "#3B82F6", "name": "Asset", "symbol": "square"},
            NodeType.SERVICE.value: {"color": "#10B981", "name": "Service", "symbol": "circle"},
            NodeType.FINDING.value: {"color": "#EF4444", "name": "Security Finding", "symbol": "diamond"},
            NodeType.PERMISSION.value: {"color": "#F59E0B", "name": "Permission", "symbol": "triangle-up"},
            NodeType.CONTROL.value: {"color": "#8B5CF6", "name": "Control", "symbol": "hexagon"},
        }

        # 2. Group nodes by type for interactive legend
        nodes_by_type: dict[str, list[str]] = {}
        for n, data in G.nodes(data=True):
            nt = data.get("node_type", "unknown")
            nodes_by_type.setdefault(nt, []).append(n)

        for ntype, nlist in nodes_by_type.items():
            meta = type_palette.get(ntype, {"color": "#64748B", "name": ntype.capitalize(), "symbol": "circle"})

            x_coords, y_coords, hover_texts, marker_sizes, border_widths, border_colors = [], [], [], [], [], []

            for nid in nlist:
                if nid not in pos:
                    continue
                x, y = pos[nid]
                x_coords.append(x)
                y_coords.append(y)

                ndata = G.nodes[nid]
                lbl = ndata.get("label", nid)
                is_on_path = nid in path_node_set

                # Dynamic sizing and glow for highlighted path nodes
                if is_on_path:
                    step_num = highlight_path.index(nid) + 1 if highlight_path else 1
                    hover_texts.append(
                        f"<b>[STEP {step_num}] {lbl}</b><br>"
                        f"<b>Node Type:</b> {ntype.upper()}<br>"
                        f"<b>ID:</b> <code>{nid}</code><br>"
                        f"<b>Status:</b> Part of active candidate risk path"
                    )
                    marker_sizes.append(26)
                    border_widths.append(3)
                    border_colors.append("#F59E0B")  # Golden accent for path steps
                else:
                    details = ""
                    if ntype == NodeType.ASSET.value:
                        details = f"IP: {ndata.get('ip_address', 'N/A')} | OS: {ndata.get('operating_system', 'N/A')}"
                    elif ntype == NodeType.FINDING.value:
                        details = f"Severity: {ndata.get('severity', 'N/A').upper()} | Category: {ndata.get('category', 'N/A')}"
                    elif ntype == NodeType.SERVICE.value:
                        details = f"Port: {ndata.get('port', 'N/A')} | Protocol: {ndata.get('protocol', 'N/A')}"

                    hover_texts.append(
                        f"<b>{lbl}</b><br>"
                        f"<b>Type:</b> {ntype}<br>"
                        f"<b>ID:</b> <code>{nid}</code><br>"
                        f"{details}"
                    )
                    marker_sizes.append(18)
                    border_widths.append(1)
                    border_colors.append("#FFFFFF")

            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                mode="markers+text",
                marker=dict(
                    size=marker_sizes,
                    color=meta["color"],
                    symbol=meta["symbol"],
                    line=dict(width=border_widths, color=border_colors),
                ),
                text=[G.nodes[nid].get("label", nid) for nid in nlist],
                textposition="bottom center",
                textfont=dict(size=10, color="#1E293B"),
                hovertext=hover_texts,
                hoverinfo="text",
                name=meta["name"],
            ))

        # Visual layout configuration
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="closest",
            margin=dict(b=20, l=10, r=10, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="#F8FAFC",
            paper_bgcolor="#FFFFFF",
            height=620,
        )

        return fig


graph_serializer = GraphSerializer()
