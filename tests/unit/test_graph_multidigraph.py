"""
Unit tests for MultiDiGraph parallel edge preservation, bounded path iteration, and stable fingerprinting.
"""

import networkx as nx
import pytest

from core.graph.algorithms import graph_algorithms
from core.models.enums import NodeType, EvidenceStatus


def test_multidigraph_parallel_edge_preservation():
    """Verify that multiple distinct relationships between the same node pair are preserved."""
    G = nx.MultiDiGraph()
    G.add_node("web-01", node_type=NodeType.ASSET.value, label="Web Server")
    G.add_node("svc-http", node_type=NodeType.SERVICE.value, label="HTTP:80")

    # Add parallel edge 1: exposes_service
    G.add_edge(
        "web-01", "svc-http",
        key="rel-001",
        relationship_id="rel-001",
        relationship_type="exposes_service",
        evidence_status=EvidenceStatus.OBSERVED.value,
        evidence_ids=["ev-01"],
    )

    # Add parallel edge 2: connects_to
    G.add_edge(
        "web-01", "svc-http",
        key="rel-002",
        relationship_id="rel-002",
        relationship_type="connects_to",
        evidence_status=EvidenceStatus.OBSERVED.value,
        evidence_ids=["ev-02"],
    )

    assert G.number_of_nodes() == 2
    assert G.number_of_edges() == 2

    # Both relationships must be present and queryable
    edge_data = G.get_edge_data("web-01", "svc-http")
    assert len(edge_data) == 2
    assert "rel-001" in edge_data
    assert "rel-002" in edge_data
    assert edge_data["rel-001"]["relationship_type"] == "exposes_service"
    assert edge_data["rel-002"]["relationship_type"] == "connects_to"


def test_bounded_path_search_cyclic_graph():
    """Verify bounded lazy iteration terminates safely on dense cyclic graphs."""
    G = nx.MultiDiGraph()
    for i in range(1, 6):
        G.add_node(f"asset-{i}", node_type=NodeType.ASSET.value, label=f"Host {i}")

    G.add_node("vuln-root", node_type=NodeType.FINDING.value, label="Root Finding")

    # Create dense cyclic mesh
    for i in range(1, 6):
        for j in range(1, 6):
            if i != j:
                G.add_edge(
                    f"asset-{i}", f"asset-{j}",
                    key=f"e-{i}-{j}",
                    relationship_id=f"e-{i}-{j}",
                    relationship_type="connects_to",
                    evidence_status=EvidenceStatus.OBSERVED.value,
                    evidence_ids=[],
                )

    # Attach finding to asset-5
    G.add_edge(
        "asset-5", "vuln-root",
        key="e-5-vuln",
        relationship_id="e-5-vuln",
        relationship_type="affected_by",
        evidence_status=EvidenceStatus.OBSERVED.value,
        evidence_ids=["ev-scan"],
    )

    # Must terminate without memory exhaustion and cap at max_results
    max_res = 10
    candidates = graph_algorithms.find_candidate_paths(G, max_length=4, max_results=max_res)
    assert len(candidates) <= max_res
    assert len(candidates) > 0

    for cand in candidates:
        assert len(cand["nodes"]) >= 3
        assert "fingerprint" in cand
        assert len(cand["fingerprint"]) == 16


def test_stable_path_fingerprint():
    """Verify identical path sequences yield identical deterministic fingerprints."""
    path = ["asset-web", "asset-app", "asset-db"]
    edges_a = [
        {"source": "asset-web", "target": "asset-app", "relationship_type": "connects_to"},
        {"source": "asset-app", "target": "asset-db", "relationship_type": "connects_to"},
    ]
    edges_b = [
        {"source": "asset-web", "target": "asset-app", "relationship_type": "connects_to"},
        {"source": "asset-app", "target": "asset-db", "relationship_type": "connects_to"},
    ]
    edges_different = [
        {"source": "asset-web", "target": "asset-app", "relationship_type": "has_permission"},
        {"source": "asset-app", "target": "asset-db", "relationship_type": "connects_to"},
    ]

    fp_a = graph_algorithms.compute_fingerprint(path, edges_a)
    fp_b = graph_algorithms.compute_fingerprint(path, edges_b)
    fp_diff = graph_algorithms.compute_fingerprint(path, edges_different)

    assert fp_a == fp_b
    assert fp_a != fp_diff
