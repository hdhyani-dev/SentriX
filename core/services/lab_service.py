"""
Laboratory service — business logic for lab management and data import.
"""

import json
import logging
from typing import Any

from sqlalchemy.orm import Session

from core.models import (
    Laboratory, Asset, Service, Finding, Relationship, Evidence, AuditLog,
    EventType,
)
from database.repositories import (
    lab_repo, asset_repo, service_repo, finding_repo,
    relationship_repo, evidence_repo, audit_log_repo,
)
from schemas.import_schema import FullLabImportSchema

logger = logging.getLogger(__name__)


class LabService:
    """Application service for laboratory CRUD and data import."""

    def create_lab(self, session: Session, name: str, description: str | None = None,
                   scope_policy: dict | None = None, lab_id: str | None = None) -> Laboratory:
        """Create a new laboratory."""
        kwargs: dict[str, Any] = {"name": name, "description": description}
        if lab_id:
            kwargs["id"] = lab_id
        if scope_policy:
            kwargs["scope_policy_json"] = json.dumps(scope_policy)
        lab = lab_repo.create(session, **kwargs)
        audit_log_repo.create(
            session,
            lab_id=lab.id,
            event_type=EventType.LAB_CREATED.value,
            target_type="laboratory",
            target_id=lab.id,
            reason=f"Created lab '{name}'",
        )
        logger.info("Created lab %s (%s)", lab.id, name)
        return lab

    def get_lab(self, session: Session, lab_id: str) -> Laboratory | None:
        return lab_repo.get_by_id(session, lab_id)

    def list_labs(self, session: Session) -> list[Laboratory]:
        return lab_repo.get_all(session)

    def update_lab(self, session: Session, lab_id: str, **kwargs) -> Laboratory | None:
        if "scope_policy" in kwargs and isinstance(kwargs["scope_policy"], dict):
            kwargs["scope_policy_json"] = json.dumps(kwargs.pop("scope_policy"))
        lab = lab_repo.update(session, lab_id, **kwargs)
        if lab:
            audit_log_repo.create(
                session,
                lab_id=lab_id,
                event_type=EventType.LAB_UPDATED.value,
                target_type="laboratory",
                target_id=lab_id,
                reason=f"Updated lab fields: {list(kwargs.keys())}",
            )
        return lab

    def import_full_lab(self, session: Session, data: dict) -> dict[str, Any]:
        """Import a complete lab from a validated JSON structure.

        Returns a summary dict with counts and any errors.
        """
        # Validate with Pydantic
        validated = FullLabImportSchema.model_validate(data)

        result: dict[str, Any] = {
            "lab_id": validated.lab.id,
            "counts": {},
            "errors": [],
        }

        # 1. Check for duplicate lab
        existing = lab_repo.get_by_id(session, validated.lab.id)
        if existing:
            result["errors"].append(f"Lab '{validated.lab.id}' already exists")
            return result

        # 2. Strict validation of same-lab ownership and referential integrity (zero dangling references)
        target_lab_id = validated.lab.id
        asset_ids = {a.id for a in validated.assets}
        evidence_ids = {e.id for e in validated.evidence}
        node_ids = set(asset_ids)
        for s in validated.services:
            node_ids.add(s.id)
        for f in validated.findings:
            node_ids.add(f.id)

        for ev in validated.evidence:
            if ev.lab_id != target_lab_id:
                result["errors"].append(f"Evidence '{ev.id}' has mismatched lab_id '{ev.lab_id}' (expected '{target_lab_id}').")

        for a in validated.assets:
            if a.lab_id != target_lab_id:
                result["errors"].append(f"Asset '{a.id}' has mismatched lab_id '{a.lab_id}' (expected '{target_lab_id}').")

        for s in validated.services:
            if s.asset_id not in asset_ids:
                result["errors"].append(f"Service '{s.id}' references dangling asset_id '{s.asset_id}'.")

        for f in validated.findings:
            if f.lab_id != target_lab_id:
                result["errors"].append(f"Finding '{f.id}' has mismatched lab_id '{f.lab_id}' (expected '{target_lab_id}').")
            if f.asset_id not in asset_ids:
                result["errors"].append(f"Finding '{f.id}' references dangling asset_id '{f.asset_id}'.")
            if f.evidence_ids:
                for feid in f.evidence_ids:
                    if feid not in evidence_ids:
                        result["errors"].append(f"Finding '{f.id}' references non-existent evidence_id '{feid}'.")

        for r in validated.relationships:
            if r.lab_id != target_lab_id:
                result["errors"].append(f"Relationship '{r.id}' has mismatched lab_id '{r.lab_id}' (expected '{target_lab_id}').")
            if r.source_node_id not in node_ids:
                result["errors"].append(f"Relationship '{r.id}' references missing source node '{r.source_node_id}'.")
            if r.target_node_id not in node_ids:
                result["errors"].append(f"Relationship '{r.id}' references missing target node '{r.target_node_id}'.")
            if r.evidence_ids:
                for reid in r.evidence_ids:
                    if reid not in evidence_ids:
                        result["errors"].append(f"Relationship '{r.id}' references non-existent evidence_id '{reid}'.")

        if result["errors"]:
            logger.warning("Import rejected for lab %s due to %d referential error(s)", target_lab_id, len(result["errors"]))
            return result

        # Create lab
        scope_json = None
        if validated.lab.scope_policy:
            scope_json = json.dumps(validated.lab.scope_policy.model_dump())
        lab = lab_repo.create(
            session,
            id=validated.lab.id,
            name=validated.lab.name,
            description=validated.lab.description,
            scope_policy_json=scope_json,
        )
        result["counts"]["lab"] = 1

        # Import evidence first (other records may reference them)
        ev_count = 0
        for ev in validated.evidence:
            content_json = None
            content_hash = None
            if ev.content is not None:
                content_str = json.dumps(ev.content) if isinstance(ev.content, dict) else str(ev.content)
                content_json = content_str
                content_hash = Evidence.compute_hash(content_str)
            evidence_repo.create(
                session,
                id=ev.id,
                lab_id=ev.lab_id,
                evidence_type=ev.evidence_type,
                source=ev.source,
                description=ev.description,
                content_json=content_json,
                content_hash=content_hash,
                related_asset_id=ev.related_asset_id,
                related_finding_id=ev.related_finding_id,
                related_relationship_id=ev.related_relationship_id,
            )
            ev_count += 1
        result["counts"]["evidence"] = ev_count

        # Import assets
        asset_count = 0
        for a in validated.assets:
            metadata_json = json.dumps(a.metadata) if a.metadata else None
            asset_repo.create(
                session,
                id=a.id,
                lab_id=a.lab_id,
                name=a.name,
                hostname=a.hostname,
                ip_address=a.ip_address,
                asset_type=a.asset_type,
                operating_system=a.operating_system,
                os_version=a.os_version,
                description=a.description,
                metadata_json=metadata_json,
            )
            asset_count += 1
        result["counts"]["assets"] = asset_count

        # Import services
        svc_count = 0
        for s in validated.services:
            service_repo.create(
                session,
                id=s.id,
                asset_id=s.asset_id,
                name=s.name,
                protocol=s.protocol,
                port=s.port,
                version=s.version,
                description=s.description,
                evidence_id=s.evidence_id,
            )
            svc_count += 1
        result["counts"]["services"] = svc_count

        # Import findings
        find_count = 0
        for f in validated.findings:
            ev_ids_json = json.dumps(f.evidence_ids) if f.evidence_ids else None
            finding_repo.create(
                session,
                id=f.id,
                lab_id=f.lab_id,
                asset_id=f.asset_id,
                title=f.title,
                description=f.description,
                category=f.category,
                severity=f.severity,
                external_reference=f.external_reference,
                evidence_ids_json=ev_ids_json,
                source=f.source,
                status=f.status,
                remediation=f.remediation,
            )
            find_count += 1
        result["counts"]["findings"] = find_count

        # Import relationships
        rel_count = 0
        for r in validated.relationships:
            ev_ids_json = json.dumps(r.evidence_ids) if r.evidence_ids else None
            relationship_repo.create(
                session,
                id=r.id,
                lab_id=r.lab_id,
                source_node_id=r.source_node_id,
                target_node_id=r.target_node_id,
                relationship_type=r.relationship_type,
                evidence_ids_json=ev_ids_json,
                evidence_status=r.evidence_status,
                description=r.description,
                confidence_rationale=r.confidence_rationale,
                source=r.source,
            )
            rel_count += 1
        result["counts"]["relationships"] = rel_count

        # Audit log
        audit_log_repo.create(
            session,
            lab_id=lab.id,
            event_type=EventType.DATA_IMPORTED.value,
            target_type="laboratory",
            target_id=lab.id,
            reason=f"Full lab import completed",
            metadata_json=json.dumps(result["counts"]),
        )

        logger.info("Imported lab %s: %s", lab.id, result["counts"])
        return result

    def delete_lab(self, session: Session, lab_id: str) -> bool:
        """Delete a lab and all its child records (cascading)."""
        return lab_repo.delete(session, lab_id)


lab_service = LabService()
