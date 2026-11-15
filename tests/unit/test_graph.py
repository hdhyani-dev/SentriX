"""
Unit tests for NetworkX graph construction and path discovery.
"""

import networkx as nx
import pytest

from core.graph.algorithms import graph_algorithms
from core.models.enums import NodeType, EvidenceStatus


@pytest.fixture
def sample_graph():
    G = nx.DiGraph()
    # Assets
    G.add_node("web", node_type=NodeType.ASSET.value, label="Web Server")
    G.add_node("app", node_type=NodeType.ASSET.value, label="App Server")
    G.add_node("db", node_type=NodeType.ASSET.value, label="DB Server")
    G.add_node("isolated", node_type=NodeType.ASSET.value, label="Isolated Host")

    # Findings
    G.add_node("f-web", node_type=NodeType.FINDING.value, label="Web Vuln")
    G.add_node("f-db", node_type=NodeType.FINDING.value, label="DB Vuln")

    # Edges
    G.add_edge("web", "app", relationship_id="r1", relationship_type="connects_to", evidence_status=EvidenceStatus.OBSERVED.value, evidence_ids=["e1"])
    G.add_edge("app", "db", relationship_id="r2", relationship_type="connects_to", evidence_status=EvidenceStatus.OBSERVED.value, evidence_ids=["e2"])
    G.add_edge("web", "f-web", relationship_id="r3", relationship_type="affected_by", evidence_status=EvidenceStatus.OBSERVED.value, evidence_ids=["e3"])
    G.add_edge("db", "f-db", relationship_id="r4", relationship_type="affected_by", evidence_status=EvidenceStatus.MISSING.value, evidence_ids=[])

    return G


def test_disconnected_nodes(sample_graph):
    disconnected = graph_algorithms.get_disconnected_nodes(sample_graph)
    assert "isolated" in disconnected
    assert "web" not in disconnected


def test_cycle_handling():
    G = nx.DiGraph()
    G.add_node("a", node_type=NodeType.ASSET.value)
    G.add_node("b", node_type=NodeType.ASSET.value)
    G.add_node("f", node_type=NodeType.FINDING.value)
    # Cycle between a and b
    G.add_edge("a", "b", relationship_type="connects_to", evidence_status="observed")
    G.add_edge("b", "a", relationship_type="connects_to", evidence_status="observed")
    G.add_edge("b", "f", relationship_type="affected_by", evidence_status="observed")

    # Path algorithm must terminate and not get stuck in infinite cycle
    paths = graph_algorithms.find_candidate_paths(G, max_length=4, max_results=10)
    assert len(paths) >= 1
    # Verify no path has duplicate consecutive nodes
    for p in paths:
        assert len(p["nodes"]) == len(set(p["nodes"]))


def test_missing_evidence_tracking(sample_graph):
    paths = graph_algorithms.find_candidate_paths(sample_graph, max_length=6, max_results=10)
    assert len(paths) > 0
    # Paths reaching f-db should record missing evidence
    db_paths = [p for p in paths if "f-db" in p["nodes"] or "f-db" in p["findings"]]
    assert len(db_paths) > 0
    missing_edges = [m["edge"] for p in db_paths for m in p["missing_evidence"]]
    assert "db -> f-db" in missing_edges
