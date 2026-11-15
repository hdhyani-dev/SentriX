"""
Report Service — queries lab data and renders reports in Markdown or HTML.
"""

from pathlib import Path
from sqlalchemy.orm import Session

from core.models.enums import EventType
from core.reporting.markdown_report import markdown_report_generator
from core.reporting.html_report import html_report_generator
from core.services.asset_service import service_service
from database.repositories import (
    lab_repo, asset_repo, finding_repo,
    attack_path_repo, validation_repo, evidence_repo, audit_log_repo
)


class ReportService:
    """Orchestrates comprehensive report generation."""

    def __init__(self):
        self._md_gen = markdown_report_generator
        self._html_gen = html_report_generator

    def generate_report(self, session: Session, lab_id: str, format: str = "markdown") -> str:
        """Generate a complete assessment report in the specified format."""
        lab = lab_repo.get_by_id(session, lab_id)
        if not lab:
            raise ValueError(f"Laboratory '{lab_id}' not found.")

        assets = asset_repo.get_by_lab(session, lab_id)
        services = service_service.list_services_by_lab(session, lab_id)
        findings = finding_repo.get_by_lab(session, lab_id)
        paths = attack_path_repo.get_by_lab(session, lab_id)
        validations = validation_repo.get_by_lab(session, lab_id)
        evidence = evidence_repo.get_by_lab(session, lab_id)

        audit_log_repo.create(
            session,
            lab_id=lab_id,
            event_type=EventType.REPORT_GENERATED.value,
            target_type="laboratory",
            target_id=lab_id,
            reason=f"Generated {format.upper()} report.",
        )

        if format.lower() == "html":
            return self._html_gen.generate(
                lab, assets, services, findings, paths, validations, evidence
            )
        return self._md_gen.generate(
            lab, assets, services, findings, paths, validations, evidence
        )

    def export_report_to_file(self, session: Session, lab_id: str, output_path: str | Path, format: str = "markdown") -> Path:
        """Generate report and write directly to a file."""
        content = self.generate_report(session, lab_id, format=format)
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(content)
        return out


report_service = ReportService()
