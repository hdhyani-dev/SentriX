"""
Candidate Path Reasoning Service — generates explainable candidate multi-step risk paths.

Applies deterministic graph rules to discover potential attack sequences,
attaches evidence, evaluates uncertainty, and stores candidate paths in the database.
"""

import json
import logging
from typing import Any
import uuid

import networkx as nx
from sqlalchemy.orm import Session

from app.config import settings
from core.graph.builder import graph_builder
from core.graph.algorithms import graph_algorithms
from core.models.enums import PathStatus, EventType, EvidenceStatus
from core.models.attack_path import AttackPath
from database.repositories import attack_path_repo, audit_log_repo

logger = logging.getLogger(__name__)


class PathReasoningService:
    """Discovers, explains, and persists candidate risk paths."""

    def __init__(self):
        self._builder = graph_builder
        self._algorithms = graph_algorithms

    def discover_and_persist_candidate_paths(
        self,
        session: Session,
        lab_id: str,
        max_length: int | None = None,
        max_results: int | None = None,
    ) -> list[AttackPath]:
        """Discover candidate paths in the lab graph and persist them if not already stored."""
        mlen = max_length or settings.MAX_PATH_LENGTH
        mres = max_results or settings.MAX_CANDIDATE_PATHS

        G = self._builder.build(session, lab_id)
        raw_candidates = self._algorithms.find_candidate_paths(G, max_length=mlen, max_results=mres)

        # Load existing paths for this lab to enable fast fingerprint/title deduplication
        existing_paths = attack_path_repo.get_by_lab(session, lab_id)
        existing_fingerprints: dict[str, AttackPath] = {}
        existing_titles: dict[str, AttackPath] = {}
        for p in existing_paths:
            existing_titles[p.title] = p
            if p.path_data_json:
                try:
                    pdata = json.loads(p.path_data_json)
                    fp = pdata.get("fingerprint")
                    if fp:
                        existing_fingerprints[fp] = p
                except Exception:
                    pass

        created_paths: list[AttackPath] = []
        for cand in raw_candidates:
            nodes = cand["nodes"]
            start_node = nodes[0]
            end_node = nodes[-1]
            findings = cand["findings"]
            fp = cand.get("fingerprint", "")
            
            # Descriptive title
            start_label = G.nodes[start_node].get("label", start_node)
            end_label = G.nodes[end_node].get("label", end_node)
            title = f"Candidate Path: {start_label} -> {end_label} via {len(findings)} finding(s)"

            # Rationale generation
            rationale = self._generate_path_rationale(G, cand)
            confidence_rationale = self._evaluate_confidence_and_uncertainty(cand)

            path_data_json = json.dumps(cand)

            # Check if this exact sequence already exists for this lab by fingerprint or title
            existing = existing_fingerprints.get(fp) or existing_titles.get(title)

            if not existing:
                path_obj = attack_path_repo.create(
                    session,
                    id=str(uuid.uuid4()),
                    lab_id=lab_id,
                    title=title,
                    description=f"Multi-step candidate path traversing {len(nodes)} nodes ({len(cand['edges'])} steps).",
                    path_status=PathStatus.CANDIDATE.value,
                    rationale=rationale,
                    confidence_rationale=confidence_rationale,
                    path_data_json=path_data_json,
                )
                created_paths.append(path_obj)
                if fp:
                    existing_fingerprints[fp] = path_obj
                existing_titles[title] = path_obj
            else:
                created_paths.append(existing)

        audit_log_repo.create(
            session,
            lab_id=lab_id,
            event_type=EventType.PATHS_GENERATED.value,
            target_type="laboratory",
            target_id=lab_id,
            reason=f"Generated {len(created_paths)} candidate path(s).",
            metadata_json=json.dumps({"candidate_count": len(created_paths)}),
        )

        return created_paths

    def get_candidate_paths_by_lab(self, session: Session, lab_id: str) -> list[AttackPath]:
        """Fetch all stored attack paths for a laboratory."""
        return attack_path_repo.get_by_lab(session, lab_id)

    def get_path_details(self, session: Session, path_id: str) -> dict[str, Any] | None:
        """Fetch an attack path with parsed structured path data."""
        path = attack_path_repo.get_by_id(session, path_id)
        if not path:
            return None
        
        parsed_data = {}
        if path.path_data_json:
            try:
                parsed_data = json.loads(path.path_data_json)
            except Exception:
                pass

        return {
            "path": path,
            "data": parsed_data,
        }

    def _generate_path_rationale(self, G: nx.DiGraph, candidate: dict[str, Any]) -> str:
        """Generate human-readable deterministic rationale for why this path was selected."""
        nodes = candidate["nodes"]
        findings = candidate["findings"]
        edges = candidate["edges"]

        finding_titles = [G.nodes[f].get("label", f) for f in findings if f in G]

        parts = [
            f"1. Sequence includes {len(nodes)} nodes connecting '{nodes[0]}' to '{nodes[-1]}'.",
            f"2. Traversing {len(edges)} relationship edges backed by evidence records.",
            f"3. Involves key security finding(s): {', '.join(finding_titles) if finding_titles else 'None'}.",
            f"4. Model represents a potential lateral progression or chained privilege vector.",
        ]
        return "\n".join(parts)

    def _evaluate_confidence_and_uncertainty(self, candidate: dict[str, Any]) -> str:
        """Evaluate evidence quality, missing items, and explicit uncertainty."""
        missing = candidate.get("missing_evidence", [])
        assumptions = candidate.get("assumptions", [])
        ev_count = len(candidate.get("evidence_ids", []))

        notes = [f"Supported by {ev_count} distinct evidence record(s)."]
        if missing:
            notes.append(f"UNCONFIRMED: {len(missing)} relationship(s) have missing evidence (e.g. {missing[0].get('edge')}).")
        if assumptions:
            notes.append(f"INFERRED: {len(assumptions)} relationship(s) rely on heuristic inference rather than direct observation.")
        
        if not missing and not assumptions:
            notes.append("High structural confidence: all relationships are directly observed with evidence.")
        else:
            notes.append("Uncertainty note: A candidate graph path models theoretical risk and does not constitute proof of exploitability.")

        return " | ".join(notes)


path_reasoning_service = PathReasoningService()
