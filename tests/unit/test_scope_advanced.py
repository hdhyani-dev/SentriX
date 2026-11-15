"""
Unit tests for advanced scope controller rules: action/category membership and same-lab ownership.
"""

import json
import pytest

from core.policy.scope_policy import scope_policy_engine, ValidationRequest
from core.models.enums import ScopeDecision
from core.models import Laboratory, Asset, Finding, Evidence


@pytest.fixture
def dummy_lab():
    policy = {
        "validation_enabled": True,
        "allowed_asset_ids": ["asset-web", "asset-app"],
        "allowed_validation_categories": ["prepared_evidence", "configuration_check"],
        "prohibited_actions": ["exploit_execution"],
    }
    return Laboratory(
        id="lab-001",
        name="Scope Test Lab",
        scope_policy_json=json.dumps(policy),
    )


def test_scope_blocked_on_action_category_mismatch(dummy_lab):
    """Verify fail-closed rejection when requested action does not belong to category."""
    # check_tls_configuration belongs to configuration_check, NOT prepared_evidence
    req = ValidationRequest(
        lab_id="lab-001",
        target_asset_id="asset-web",
        validation_category="prepared_evidence",
        requested_action="check_tls_configuration",
    )
    result = scope_policy_engine.evaluate(dummy_lab, req)
    assert not result.is_allowed
    assert result.decision == ScopeDecision.BLOCKED
    assert result.evaluated_rule == "RULE_ACTION_CATEGORY_MEMBERSHIP"
    assert "not permitted under category" in result.reason


def test_scope_blocked_on_cross_lab_asset_ownership(dummy_lab):
    """Verify fail-closed rejection when asset belongs to a foreign lab."""
    # asset-web is in allowlist string, but belongs to lab-999
    foreign_asset = Asset(
        id="asset-web",
        lab_id="lab-999",
        name="Foreign Host",
    )
    req = ValidationRequest(
        lab_id="lab-001",
        target_asset_id="asset-web",
        validation_category="configuration_check",
        requested_action="check_tls_configuration",
    )
    context = {"asset": foreign_asset}
    result = scope_policy_engine.evaluate(dummy_lab, req, context=context)
    assert not result.is_allowed
    assert result.decision == ScopeDecision.BLOCKED
    assert result.evaluated_rule == "RULE_ASSET_LAB_OWNERSHIP"
    assert "belongs to lab 'lab-999'" in result.reason


def test_scope_blocked_on_cross_lab_finding_ownership(dummy_lab):
    """Verify fail-closed rejection when associated finding belongs to another lab."""
    asset = Asset(id="asset-web", lab_id="lab-001", name="Web")
    foreign_finding = Finding(
        id="finding-foreign",
        lab_id="lab-999",
        asset_id="asset-web",
        title="Foreign Weakness",
        category="tls",
    )
    req = ValidationRequest(
        lab_id="lab-001",
        target_asset_id="asset-web",
        validation_category="configuration_check",
        requested_action="check_tls_configuration",
        finding_id="finding-foreign",
    )
    context = {"asset": asset, "finding": foreign_finding}
    result = scope_policy_engine.evaluate(dummy_lab, req, context=context)
    assert not result.is_allowed
    assert result.decision == ScopeDecision.BLOCKED
    assert result.evaluated_rule == "RULE_FINDING_LAB_OWNERSHIP"


def test_scope_blocked_on_cross_lab_evidence_ownership(dummy_lab):
    """Verify fail-closed rejection when supporting evidence belongs to another lab."""
    asset = Asset(id="asset-web", lab_id="lab-001", name="Web")
    foreign_ev = Evidence(
        id="ev-foreign",
        lab_id="lab-999",
        evidence_type="tls_config",
    )
    req = ValidationRequest(
        lab_id="lab-001",
        target_asset_id="asset-web",
        validation_category="configuration_check",
        requested_action="check_tls_configuration",
        evidence_ids=["ev-foreign"],
    )
    context = {"asset": asset, "evidence_records": [foreign_ev]}
    result = scope_policy_engine.evaluate(dummy_lab, req, context=context)
    assert not result.is_allowed
    assert result.decision == ScopeDecision.BLOCKED
    assert result.evaluated_rule == "RULE_EVIDENCE_LAB_OWNERSHIP"
