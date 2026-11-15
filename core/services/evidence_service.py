"""
Evidence service — business logic for evidence tracking.
"""

import json
import logging

from sqlalchemy.orm import Session

from core.models import Evidence
from database.repositories import evidence_repo

logger = logging.getLogger(__name__)


class EvidenceService:
    """Application service for evidence tracking and retrieval."""

    def get_evidence(self, session: Session, evidence_id: str) -> Evidence | None:
        return evidence_repo.get_by_id(session, evidence_id)

    def list_evidence_by_lab(self, session: Session, lab_id: str) -> list[Evidence]:
        return evidence_repo.get_by_lab(session, lab_id)

    def get_evidence_by_ids(self, session: Session, evidence_ids: list[str]) -> list[Evidence]:
        """Retrieve multiple evidence records by their IDs."""
        results = []
        for eid in evidence_ids:
            ev = evidence_repo.get_by_id(session, eid)
            if ev:
                results.append(ev)
        return results

    def get_content(self, evidence: Evidence) -> dict | str | None:
        """Parse and return the content of an evidence record."""
        if not evidence.content_json:
            return None
        try:
            return json.loads(evidence.content_json)
        except (json.JSONDecodeError, TypeError):
            return evidence.content_json

    def count_by_lab(self, session: Session, lab_id: str) -> int:
        return len(evidence_repo.get_by_lab(session, lab_id))


evidence_service = EvidenceService()
