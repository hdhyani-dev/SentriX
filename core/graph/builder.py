"""
Graph builder — constructs a NetworkX DiGraph from database records.

The graph represents lab assets, services, findings and their
relationships as nodes and edges with evidence metadata.
"""

import json
import logging
from typing import Any

import networkx as nx
from sqlalchemy.orm import Session

from core.models import (
    Asset, Service, Finding, Relationship,
    NodeType, RelationshipType, EvidenceStatus,
)
from database.repositories import (
    asset_repo, service_repo, finding_repo, relationship_repo,
)

logger = logging.getLogger(__name__)


class GraphBuilder:
    """Builds a NetworkX directed graph from persisted lab records."""

    def build(self, session: Session, lab_id: str, max_nodes: int = 1000) -> nx.MultiDiGraph:
        """Build a complete graph for a lab using MultiDiGraph to preserve parallel edges.

        Args:
            session: Database session.
            lab_id: Laboratory ID.
            max_nodes: Safety limit on total node count.

        Returns:
            A NetworkX MultiDiGraph with typed nodes and evidence-annotated edges.
        """
        G = nx.MultiDiGraph()

        # Load assets as nodes
        assets = asset_repo.get_by_lab(session, lab_id)
        for asset in assets:
            if G.number_of_nodes() >= max_nodes:
                logger.warning("Max node limit (%d) reached, stopping graph build", max_nodes)
                break
            G.add_node(
                asset.id,
                node_type=NodeType.ASSET.value,
                label=asset.name,
                lab_id=lab_id,
                record_id=asset.id,
                hostname=asset.hostname,
                ip_address=asset.ip_address,
                asset_type=asset.asset_type,
            )

        # Load services as nodes
        for asset in assets:
            services = service_repo.get_by_asset(session, asset.id)
            for svc in services:
                if G.number_of_nodes() >= max_nodes:
                    break
                G.add_node(
                    svc.id,
                    node_type=NodeType.SERVICE.value,
                    label=f"{svc.name}:{svc.port}" if svc.port else svc.name,
                    lab_id=lab_id,
                    record_id=svc.id,
                    parent_asset_id=asset.id,
                    protocol=svc.protocol,
                    port=svc.port,
                    version=svc.version,
                )

        # Load findings as nodes
        findings = finding_repo.get_by_lab(session, lab_id)
        for finding in findings:
            if G.number_of_nodes() >= max_nodes:
                break
            G.add_node(
                finding.id,
                node_type=NodeType.FINDING.value,
                label=finding.title,
                lab_id=lab_id,
                record_id=finding.id,
                severity=finding.severity,
                category=finding.category,
                asset_id=finding.asset_id,
            )

        # Load relationships as edges
        relationships = relationship_repo.get_by_lab(session, lab_id)
        for rel in relationships:
            # Only add edge if both endpoints exist in the graph
            if rel.source_node_id not in G or rel.target_node_id not in G:
                logger.warning(
                    "Skipping relationship %s: endpoint(s) not in graph "
                    "(source=%s exists=%s, target=%s exists=%s)",
                    rel.id,
                    rel.source_node_id, rel.source_node_id in G,
                    rel.target_node_id, rel.target_node_id in G,
                )
                continue

            evidence_ids = []
            if rel.evidence_ids_json:
                try:
                    evidence_ids = json.loads(rel.evidence_ids_json)
                except (json.JSONDecodeError, TypeError):
                    pass

            G.add_edge(
                rel.source_node_id,
                rel.target_node_id,
                key=rel.id,
                relationship_id=rel.id,
                relationship_type=rel.relationship_type,
                evidence_status=rel.evidence_status,
                evidence_ids=evidence_ids,
                description=rel.description,
                confidence_rationale=rel.confidence_rationale,
            )

        logger.info(
            "Built graph for lab %s: %d nodes, %d edges",
            lab_id, G.number_of_nodes(), G.number_of_edges(),
        )
        return G

    def validate_edge(self, G: nx.DiGraph, source_id: str, target_id: str) -> list[str]:
        """Validate that a proposed edge is acceptable.

        Returns a list of error messages (empty = valid).
        """
        errors = []
        if source_id not in G:
            errors.append(f"Source node '{source_id}' does not exist in graph")
        if target_id not in G:
            errors.append(f"Target node '{target_id}' does not exist in graph")
        if source_id == target_id:
            errors.append("Self-loops are not allowed")
        if not errors:
            # Check both endpoints are in the same lab
            src_lab = G.nodes[source_id].get("lab_id")
            tgt_lab = G.nodes[target_id].get("lab_id")
            if src_lab != tgt_lab:
                errors.append(
                    f"Endpoints are in different labs: {src_lab} vs {tgt_lab}"
                )
        return errors


graph_builder = GraphBuilder()
