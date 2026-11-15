"""
Scope Policy Controller — enforces server-side, fail-closed access control and validation authorization.
"""

from dataclasses import dataclass, field
import json
import logging
from typing import Any

from core.models.enums import ScopeDecision
from core.policy.action_registry import is_action_prohibited

logger = logging.getLogger(__name__)


@dataclass
class ValidationRequest:
    """Structured request for safe validation."""
    lab_id: str
    target_asset_id: str
    validation_category: str
    requested_action: str
    finding_id: str | None = None
    evidence_ids: list[str] = field(default_factory=list)


@dataclass
class ScopeDecisionResult:
    """Result of policy evaluation."""
    decision: ScopeDecision
    reason: str
    evaluated_rule: str

    @property
    def is_allowed(self) -> bool:
        return self.decision == ScopeDecision.ALLOWED


class ScopePolicyEngine:
    """Evaluates validation requests against laboratory scope policy with fail-closed behavior."""

    @staticmethod
    def evaluate(lab: Any, request: ValidationRequest) -> ScopeDecisionResult:
        """Evaluate a validation request against lab policy.

        Fails closed on any missing, invalid, or ambiguous condition.
        """
        # Rule 1: Lab must exist
        if not lab:
            return ScopeDecisionResult(
                decision=ScopeDecision.BLOCKED,
                reason="Laboratory record not found.",
                evaluated_rule="RULE_LAB_EXISTS",
            )

        # Rule 2: Lab policy must be present
        if not lab.scope_policy_json:
            return ScopeDecisionResult(
                decision=ScopeDecision.BLOCKED,
                reason="Laboratory has no scope policy configured.",
                evaluated_rule="RULE_POLICY_PRESENT",
            )

        try:
            policy = json.loads(lab.scope_policy_json)
        except Exception:
            return ScopeDecisionResult(
                decision=ScopeDecision.BLOCKED,
                reason="Laboratory scope policy JSON is corrupted.",
                evaluated_rule="RULE_POLICY_VALID_JSON",
            )

        # Rule 3: Validation must be enabled for this lab
        if not policy.get("validation_enabled", False):
            return ScopeDecisionResult(
                decision=ScopeDecision.BLOCKED,
                reason="Validation operations are disabled for this laboratory.",
                evaluated_rule="RULE_VALIDATION_ENABLED",
            )

        # Rule 4: Action must not be globally prohibited
        if is_action_prohibited(request.requested_action):
            return ScopeDecisionResult(
                decision=ScopeDecision.BLOCKED,
                reason=f"Action '{request.requested_action}' is globally prohibited.",
                evaluated_rule="RULE_PROHIBITED_ACTION",
            )

        # Rule 5: Action must not be in lab prohibited_actions list
        lab_prohibited = {a.lower() for a in policy.get("prohibited_actions", [])}
        if request.requested_action.lower() in lab_prohibited:
            return ScopeDecisionResult(
                decision=ScopeDecision.BLOCKED,
                reason=f"Action '{request.requested_action}' is listed in lab prohibited actions.",
                evaluated_rule="RULE_LAB_PROHIBITED_ACTION",
            )

        # Rule 6: Target asset must be in allowed_asset_ids
        allowed_assets = set(policy.get("allowed_asset_ids", []))
        if request.target_asset_id not in allowed_assets:
            return ScopeDecisionResult(
                decision=ScopeDecision.BLOCKED,
                reason=f"Target asset '{request.target_asset_id}' is not in allowed asset scope list.",
                evaluated_rule="RULE_ASSET_ALLOWLIST",
            )

        # Rule 7: Validation category must be in allowed_validation_categories
        allowed_categories = set(policy.get("allowed_validation_categories", []))
        if request.validation_category not in allowed_categories:
            return ScopeDecisionResult(
                decision=ScopeDecision.BLOCKED,
                reason=f"Validation category '{request.validation_category}' is not permitted for this lab.",
                evaluated_rule="RULE_CATEGORY_ALLOWLIST",
            )

        # All checks passed — allowed
        return ScopeDecisionResult(
            decision=ScopeDecision.ALLOWED,
            reason="Validation request complies with laboratory scope policy.",
            evaluated_rule="RULE_ALL_CHECKS_PASSED",
        )


scope_policy_engine = ScopePolicyEngine()
