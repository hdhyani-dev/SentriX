"""
Graph algorithms — bounded path finding, neighbor queries, component analysis.

All algorithms are deterministic and handle cycles/disconnected components safely.
"""

import logging
import sys
from pathlib import Path
from typing import Any

# Ensure project root is in sys.path when executed directly
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import networkx as nx

from core.models.enums import NodeType, EvidenceStatus

logger = logging.getLogger(__name__)


class GraphAlgorithms:
    """Deterministic graph analysis algorithms for ChainBreak."""

    def find_candidate_paths(
        self,
        G: nx.DiGraph,
        max_length: int = 6,
        max_results: int = 50,
    ) -> list[dict[str, Any]]:
        """Find candidate risk paths through the graph.

        A candidate path is an ordered sequence of nodes where:
        1. The path starts at an asset node.
        2. The path terminates at an asset node or a finding node.
        3. The path has length >= 2 (at least 2 edges).
        4. Associated findings on all traversed assets are identified and attached.

        Args:
            G: The lab graph.
            max_length: Maximum number of edges in a path.
            max_results: Maximum number of candidate paths to return.

        Returns:
            List of candidate path dicts.
        """
        candidates: list[dict[str, Any]] = []

        # Find all asset nodes as potential starting points
        asset_nodes = [
            n for n, d in G.nodes(data=True)
            if d.get("node_type") == NodeType.ASSET.value
        ]

        # Potential target nodes: other assets or findings
        target_nodes = [
            n for n, d in G.nodes(data=True)
            if d.get("node_type") in (NodeType.ASSET.value, NodeType.FINDING.value)
        ]

        visited_paths: set[tuple] = set()

        for source in asset_nodes:
            for target in target_nodes:
                if source == target:
                    continue
                if len(candidates) >= max_results:
                    break

                try:
                    paths = list(nx.all_simple_paths(
                        G, source, target, cutoff=max_length
                    ))
                except (nx.NetworkXError, nx.NodeNotFound):
                    continue

                for path in paths:
                    if len(candidates) >= max_results:
                        break

                    path_key = tuple(path)
                    if path_key in visited_paths:
                        continue
                    visited_paths.add(path_key)

                    # Must have at least 2 edges
                    if len(path) < 3:
                        continue

                    # Collect finding nodes in path OR directly attached to traversed assets
                    finding_nodes = [
                        n for n in path
                        if G.nodes[n].get("node_type") == NodeType.FINDING.value
                    ]
                    # Also look at findings attached to assets on the path
                    for node in path:
                        if G.nodes[node].get("node_type") == NodeType.ASSET.value:
                            for succ in G.successors(node):
                                if G.nodes[succ].get("node_type") == NodeType.FINDING.value:
                                    if succ not in finding_nodes:
                                        finding_nodes.append(succ)

                    if not finding_nodes:
                        continue

                    candidate = self._build_candidate(G, path, finding_nodes)
                    candidates.append(candidate)

            if len(candidates) >= max_results:
                break

        logger.info("Found %d candidate paths (max_length=%d, max_results=%d)",
                     len(candidates), max_length, max_results)
        return candidates

    def _build_candidate(
        self,
        G: nx.DiGraph,
        path: list[str],
        finding_nodes: list[str],
    ) -> dict[str, Any]:
        """Build a candidate path data structure from a node sequence."""
        edges = []
        all_evidence_ids: list[str] = []
        missing_evidence: list[dict] = []
        assumptions: list[dict] = []

        for i in range(len(path) - 1):
            src, tgt = path[i], path[i + 1]
            edge_data = G.edges[src, tgt]
            edge_info = {
                "source": src,
                "target": tgt,
                "relationship_id": edge_data.get("relationship_id"),
                "relationship_type": edge_data.get("relationship_type"),
                "evidence_status": edge_data.get("evidence_status"),
                "description": edge_data.get("description"),
            }
            edges.append(edge_info)

            # Collect evidence
            ev_ids = edge_data.get("evidence_ids", [])
            all_evidence_ids.extend(ev_ids)

            # Track missing and inferred evidence
            status = edge_data.get("evidence_status", "")
            if status == EvidenceStatus.MISSING.value:
                missing_evidence.append({
                    "edge": f"{src} -> {tgt}",
                    "relationship_type": edge_data.get("relationship_type"),
                    "note": "Evidence for this relationship is missing",
                })
            elif status == EvidenceStatus.INFERRED.value:
                assumptions.append({
                    "edge": f"{src} -> {tgt}",
                    "relationship_type": edge_data.get("relationship_type"),
                    "rationale": edge_data.get("confidence_rationale", "No rationale provided"),
                })

        return {
            "nodes": path,
            "edges": edges,
            "findings": finding_nodes,
            "evidence_ids": list(set(all_evidence_ids)),
            "missing_evidence": missing_evidence,
            "assumptions": assumptions,
        }

    def get_neighbors(self, G: nx.DiGraph, node_id: str) -> dict[str, list[str]]:
        """Get predecessors and successors of a node."""
        if node_id not in G:
            return {"predecessors": [], "successors": []}
        return {
            "predecessors": list(G.predecessors(node_id)),
            "successors": list(G.successors(node_id)),
        }

    def get_connected_components(self, G: nx.DiGraph) -> list[set[str]]:
        """Get weakly connected components of the directed graph."""
        return [set(c) for c in nx.weakly_connected_components(G)]

    def get_disconnected_nodes(self, G: nx.DiGraph) -> list[str]:
        """Get nodes with no edges."""
        return [n for n in G.nodes() if G.degree(n) == 0]

    def get_node_details(self, G: nx.DiGraph, node_id: str) -> dict[str, Any] | None:
        """Get full details of a node including its edges."""
        if node_id not in G:
            return None
        data = dict(G.nodes[node_id])
        data["id"] = node_id
        data["in_edges"] = [
            {"source": u, **dict(G.edges[u, node_id])}
            for u in G.predecessors(node_id)
        ]
        data["out_edges"] = [
            {"target": v, **dict(G.edges[node_id, v])}
            for v in G.successors(node_id)
        ]
        return data

    def get_path_details(self, G: nx.DiGraph, node_ids: list[str]) -> dict[str, Any] | None:
        """Get details of a specific path given an ordered list of node IDs."""
        if not node_ids or len(node_ids) < 2:
            return None
        for nid in node_ids:
            if nid not in G:
                return None
        for i in range(len(node_ids) - 1):
            if not G.has_edge(node_ids[i], node_ids[i + 1]):
                return None
        finding_nodes = [
            n for n in node_ids
            if G.nodes[n].get("node_type") == NodeType.FINDING.value
        ]
        return self._build_candidate(G, node_ids, finding_nodes)

    def graph_stats(self, G: nx.DiGraph) -> dict[str, Any]:
        """Get summary statistics for a graph."""
        components = self.get_connected_components(G)
        node_types: dict[str, int] = {}
        for _, data in G.nodes(data=True):
            nt = data.get("node_type", "unknown")
            node_types[nt] = node_types.get(nt, 0) + 1
        return {
            "total_nodes": G.number_of_nodes(),
            "total_edges": G.number_of_edges(),
            "connected_components": len(components),
            "node_types": node_types,
            "is_dag": nx.is_directed_acyclic_graph(G),
            "disconnected_nodes": len(self.get_disconnected_nodes(G)),
        }


graph_algorithms = GraphAlgorithms()


if __name__ == "__main__":
    print("=" * 65)
    print("  ChainBreak — Graph Analysis & Candidate Path Discovery Engine")
    print("=" * 65)

    try:
        from database.connection import init_db, get_session
        from core.graph.builder import graph_builder
        from core.services.lab_service import lab_service

        init_db()
        with get_session() as session:
            labs = lab_service.list_labs(session)
            if not labs:
                print("No lab found in database. Building synthetic demo graph...")
                G = nx.DiGraph()
                G.add_node("web-server", node_type="asset", label="web-server")
                G.add_node("app-server", node_type="asset", label="app-server")
                G.add_node("db-server", node_type="asset", label="database-server")
                G.add_node("vuln-tls", node_type="finding", label="Weak TLS")
                G.add_node("vuln-perms", node_type="finding", label="Root Permissions")
                G.add_edge("web-server", "app-server", relationship_type="connects_to", evidence_status="observed", evidence_ids=["ev-1"])
                G.add_edge("app-server", "db-server", relationship_type="connects_to", evidence_status="observed", evidence_ids=["ev-2"])
                G.add_edge("web-server", "vuln-tls", relationship_type="affected_by", evidence_status="observed", evidence_ids=["ev-3"])
                G.add_edge("app-server", "vuln-perms", relationship_type="affected_by", evidence_status="observed", evidence_ids=["ev-4"])
                lab_name = "Standalone Demo Fixture"
            else:
                lab = labs[0]
                lab_name = f"{lab.name} ({lab.id})"
                G = graph_builder.build(session, lab.id)
    except Exception as e:
        print(f"Notice: Connecting in standalone mode ({e}).")
        G = nx.DiGraph()

    stats = graph_algorithms.graph_stats(G)
    print(f"\nTarget Lab Graph: {lab_name}")
    print(f"• Total Nodes: {stats['total_nodes']}")
    print(f"• Total Edges: {stats['total_edges']}")
    print(f"• Connected Components: {stats['connected_components']}")
    print(f"• Disconnected Isolated Hosts: {stats['disconnected_nodes']}")
    print(f"• Node Type Distribution: {stats['node_types']}")

    print("\nRunning Bounded Candidate Path Discovery...")
    candidates = graph_algorithms.find_candidate_paths(G, max_length=6, max_results=20)
    print(f"Discovered {len(candidates)} candidate risk path(s):\n")

    for i, c in enumerate(candidates, 1):
        seq = " ➔ ".join(c["nodes"])
        findings_count = len(c["findings"])
        ev_count = len(c["evidence_ids"])
        missing_count = len(c["missing_evidence"])
        assumptions_count = len(c["assumptions"])

        print(f"[{i}] Path: {seq}")
        print(f"    Edges: {len(c['edges'])} hops | Findings Attached: {findings_count} | Evidence Records: {ev_count}")
        if missing_count > 0:
            print(f"    ⚠️ Missing Evidence: {missing_count} edge(s) lack empirical evidence")
        if assumptions_count > 0:
            print(f"    ℹ️ Inferred Assumptions: {assumptions_count} edge(s) rely on rule inference")
        print()

    print("=" * 65)
    print("  Analysis Complete (Safe, Deterministic, Read-Only)")
    print("=" * 65)

