"""
Scope Service — central service for checking lab authorization and logging scope decisions.
"""

import json
import logging
from sqlalchemy.orm import Session

from core.models.enums import EventType, ScopeDecision
from core.policy.scope_policy import scope_policy_engine, ValidationRequest, ScopeDecisionResult
from database.repositories import (
    lab_repo, asset_repo, finding_repo, evidence_repo, audit_log_repo
)

logger = logging.getLogger(__name__)


class ScopeService:
    """Evaluates scope permissions and records audit logs."""

    def __init__(self):
        self._engine = scope_policy_engine

    def check_scope(self, session: Session, request: ValidationRequest) -> ScopeDecisionResult:
        """Check whether a validation request is allowed under lab scope with referential verification."""
        lab = lab_repo.get_by_id(session, request.lab_id)

        # Build referential context for deep same-lab ownership checks
        asset = asset_repo.get_by_id(session, request.target_asset_id)
        finding = finding_repo.get_by_id(session, request.finding_id) if request.finding_id else None
        evidence_records = []
        if request.evidence_ids:
            for eid in request.evidence_ids:
                ev = evidence_repo.get_by_id(session, eid)
                if ev:
                    evidence_records.append(ev)

        context = {
            "asset": asset,
            "finding": finding,
            "evidence_records": evidence_records,
        }

        result = self._engine.evaluate(lab, request, context=context)

        # Audit log the decision
        event_type = EventType.VALIDATION_ALLOWED.value if result.is_allowed else EventType.VALIDATION_BLOCKED.value
        audit_log_repo.create(
            session,
            lab_id=request.lab_id,
            event_type=event_type,
            target_type="asset",
            target_id=request.target_asset_id,
            decision=result.decision.value,
            reason=f"[{result.evaluated_rule}] {result.reason}",
            metadata_json=json.dumps({
                "requested_action": request.requested_action,
                "validation_category": request.validation_category,
                "finding_id": request.finding_id,
            }),
        )

        logger.info(
            "Scope check for lab=%s asset=%s action=%s: %s (%s)",
            request.lab_id, request.target_asset_id, request.requested_action,
            result.decision.value, result.reason,
        )
        return result


scope_service = ScopeService()
