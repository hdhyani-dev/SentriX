"""
Validation Service — coordinates scope checks, executes safe validators, and persists outcomes.
"""

import json
import logging
from typing import Any
import uuid

from sqlalchemy.orm import Session

from core.models import Validation, Finding, AttackPath, Evidence
from core.models.enums import (
    ValidationResult, ScopeDecision, ValidationCategory, EventType, PathStatus
)
from core.policy.scope_policy import ValidationRequest, ScopeDecisionResult
from core.services.scope_service import scope_service
from core.validators.prepared_evidence import prepared_evidence_validator
from core.validators.configuration_checks import configuration_checks_validator
from database.repositories import (
    validation_repo, finding_repo, evidence_repo, attack_path_repo, audit_log_repo
)

logger = logging.getLogger(__name__)


class ValidationService:
    """Orchestrates safe validation lifecycle."""

    def __init__(self):
        self._scope = scope_service
        self._validators = {
            ValidationCategory.PREPARED_EVIDENCE.value: prepared_evidence_validator,
            ValidationCategory.CONFIGURATION_CHECK.value: configuration_checks_validator,
        }

    def execute_validation(
        self,
        session: Session,
        lab_id: str,
        target_asset_id: str,
        validation_category: str,
        requested_action: str,
        finding_id: str | None = None,
        evidence_ids: list[str] | None = None,
        attack_path_id: str | None = None,
    ) -> Validation:
        """Execute a safe validation check following fail-closed scope policy."""
        eids = evidence_ids or []
        req = ValidationRequest(
            lab_id=lab_id,
            target_asset_id=target_asset_id,
            validation_category=validation_category,
            requested_action=requested_action,
            finding_id=finding_id,
            evidence_ids=eids,
        )

        # 1. Scope policy check
        scope_res: ScopeDecisionResult = self._scope.check_scope(session, req)

        val_id = str(uuid.uuid4())

        # If blocked, record the blocked validation and return IMMEDIATELY
        if not scope_res.is_allowed:
            record = validation_repo.create(
                session,
                id=val_id,
                lab_id=lab_id,
                asset_id=target_asset_id,
                finding_id=finding_id,
                validation_category=validation_category,
                requested_action=requested_action,
                scope_decision=ScopeDecision.BLOCKED.value,
                result=ValidationResult.BLOCKED.value,
                reason=f"Blocked by policy: {scope_res.reason}",
                evidence_ids_json=json.dumps(eids) if eids else None,
                validator_module=None,
            )
            # Only update path status if target asset is actually on the path
            if attack_path_id:
                path = attack_path_repo.get_by_id(session, attack_path_id)
                if path and path.lab_id == lab_id:
                    path_data = {}
                    if path.path_data_json:
                        try:
                            path_data = json.loads(path.path_data_json)
                        except Exception:
                            pass
                    path_nodes = set(path_data.get("nodes", []))
                    if target_asset_id in path_nodes:
                        path.path_status = PathStatus.BLOCKED.value
                        session.flush()

            logger.warning("Validation blocked: %s", scope_res.reason)
            return record

        # 2. Select validator
        validator = self._validators.get(validation_category)
        if not validator:
            record = validation_repo.create(
                session,
                id=val_id,
                lab_id=lab_id,
                asset_id=target_asset_id,
                finding_id=finding_id,
                validation_category=validation_category,
                requested_action=requested_action,
                scope_decision=ScopeDecision.ALLOWED.value,
                result=ValidationResult.INCONCLUSIVE.value,
                reason=f"No validator implemented for category '{validation_category}'.",
                evidence_ids_json=json.dumps(eids) if eids else None,
                validator_module=None,
            )
            return record

        # 3. Gather evidence context
        evidence_records: list[Evidence] = []
        for eid in eids:
            ev = evidence_repo.get_by_id(session, eid)
            if ev:
                evidence_records.append(ev)

        finding_obj = finding_repo.get_by_id(session, finding_id) if finding_id else None
        if finding_obj and not evidence_records and finding_obj.evidence_ids_json:
            try:
                for feid in json.loads(finding_obj.evidence_ids_json):
                    ev = evidence_repo.get_by_id(session, feid)
                    if ev and ev not in evidence_records:
                        evidence_records.append(ev)
            except Exception:
                pass

        context = {
            "requested_action": requested_action,
            "evidence_records": evidence_records,
            "finding": finding_obj,
            "asset_id": target_asset_id,
        }

        # 4. Invoke safe validator
        outcome = validator.validate(context)

        # 5. Persist validation record
        record = validation_repo.create(
            session,
            id=val_id,
            lab_id=lab_id,
            asset_id=target_asset_id,
            finding_id=finding_id,
            validation_category=validation_category,
            requested_action=requested_action,
            scope_decision=ScopeDecision.ALLOWED.value,
            result=outcome.result.value,
            reason=outcome.reason,
            evidence_ids_json=json.dumps([e.id for e in evidence_records]) if evidence_records else None,
            validator_module=outcome.validator_module,
        )

        # Audit log completion
        audit_log_repo.create(
            session,
            lab_id=lab_id,
            event_type=EventType.VALIDATION_COMPLETED.value,
            target_type="validation",
            target_id=val_id,
            decision=outcome.result.value,
            reason=outcome.reason,
        )

        # 6. Update attack path status if specified and verified to be on the path
        if attack_path_id:
            path = attack_path_repo.get_by_id(session, attack_path_id)
            if path and path.lab_id == lab_id:
                path_data = {}
                if path.path_data_json:
                    try:
                        path_data = json.loads(path.path_data_json)
                    except Exception:
                        pass

                path_nodes = set(path_data.get("nodes", []))
                path_findings = set(path_data.get("findings", []))

                is_asset_on_path = target_asset_id in path_nodes
                is_finding_on_path = (finding_id in path_findings) if finding_id else False

                if not is_asset_on_path and not is_finding_on_path:
                    logger.info(
                        "Validation on asset %s / finding %s is not part of path %s; preserving status '%s'",
                        target_asset_id, finding_id, attack_path_id, path.path_status,
                    )
                else:
                    if outcome.result == ValidationResult.CONFIRMED:
                        # Collect all confirmed findings for this lab to check if entire path is verified
                        lab_validations = validation_repo.get_by_lab(session, lab_id)
                        confirmed_findings = {
                            v.finding_id for v in lab_validations
                            if v.finding_id and v.result == ValidationResult.CONFIRMED.value
                        }
                        if finding_id:
                            confirmed_findings.add(finding_id)

                        # If all findings on the path have confirmed validation -> SUPPORTED
                        if path_findings and path_findings.issubset(confirmed_findings):
                            path.path_status = PathStatus.SUPPORTED.value
                        else:
                            path.path_status = PathStatus.PARTIALLY_SUPPORTED.value
                    elif outcome.result == ValidationResult.BLOCKED:
                        path.path_status = PathStatus.BLOCKED.value
                    elif outcome.result == ValidationResult.NOT_CONFIRMED:
                        path.path_status = PathStatus.INCONCLUSIVE.value
                    session.flush()

        logger.info("Validation completed: id=%s result=%s", val_id, outcome.result.value)
        return record

    def list_validations_by_lab(self, session: Session, lab_id: str) -> list[Validation]:
        return validation_repo.get_by_lab(session, lab_id)


validation_service = ValidationService()
