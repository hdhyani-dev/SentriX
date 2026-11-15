"""
Finding service — business logic for security findings.
"""

import json
import logging

from sqlalchemy.orm import Session

from core.models import Finding, Severity
from database.repositories import finding_repo

logger = logging.getLogger(__name__)


class FindingService:
    """Application service for security finding management."""

    def get_finding(self, session: Session, finding_id: str) -> Finding | None:
        return finding_repo.get_by_id(session, finding_id)

    def list_findings_by_lab(self, session: Session, lab_id: str) -> list[Finding]:
        return finding_repo.get_by_lab(session, lab_id)

    def list_findings_by_asset(self, session: Session, asset_id: str) -> list[Finding]:
        return finding_repo.get_by_asset(session, asset_id)

    def list_findings_by_severity(self, session: Session, lab_id: str, severity: str) -> list[Finding]:
        return finding_repo.get_by_severity(session, lab_id, severity)

    def get_findings_summary(self, session: Session, lab_id: str) -> dict[str, int]:
        """Get count of findings by severity for a lab."""
        findings = finding_repo.get_by_lab(session, lab_id)
        summary: dict[str, int] = {}
        for f in findings:
            summary[f.severity] = summary.get(f.severity, 0) + 1
        return summary

    def get_evidence_ids(self, finding: Finding) -> list[str]:
        """Parse evidence IDs from the finding's JSON field."""
        if not finding.evidence_ids_json:
            return []
        try:
            return json.loads(finding.evidence_ids_json)
        except (json.JSONDecodeError, TypeError):
            return []

    def count_by_lab(self, session: Session, lab_id: str) -> int:
        return len(finding_repo.get_by_lab(session, lab_id))


finding_service = FindingService()
