"""
Unit tests for scope controller (fail-closed) and safe validation engine.
"""

import json
from unittest.mock import MagicMock

from core.models.enums import ScopeDecision, ValidationResult
from core.policy.scope_policy import scope_policy_engine, ValidationRequest


def create_mock_lab(enabled=True, allowed_assets=None, allowed_cats=None, prohibited=None):
    mock = MagicMock()
    mock.id = "lab-test"
    policy = {
        "validation_enabled": enabled,
        "allowed_asset_ids": allowed_assets or ["asset-1", "asset-2"],
        "allowed_validation_categories": allowed_cats or ["configuration_check", "prepared_evidence"],
        "prohibited_actions": prohibited or ["exploit_execution", "credential_extraction"],
    }
    mock.scope_policy_json = json.dumps(policy)
    return mock


def test_scope_allowed_request():
    lab = create_mock_lab()
    req = ValidationRequest(
        lab_id="lab-test",
        target_asset_id="asset-1",
        validation_category="configuration_check",
        requested_action="check_tls_configuration",
    )
    result = scope_policy_engine.evaluate(lab, req)
    assert result.decision == ScopeDecision.ALLOWED
    assert result.is_allowed is True


def test_scope_blocked_when_lab_missing():
    req = ValidationRequest(
        lab_id="unknown",
        target_asset_id="asset-1",
        validation_category="configuration_check",
        requested_action="check_tls_configuration",
    )
    result = scope_policy_engine.evaluate(None, req)
    assert result.decision == ScopeDecision.BLOCKED
    assert "not found" in result.reason.lower()


def test_scope_blocked_when_validation_disabled():
    lab = create_mock_lab(enabled=False)
    req = ValidationRequest(
        lab_id="lab-test",
        target_asset_id="asset-1",
        validation_category="configuration_check",
        requested_action="check_tls_configuration",
    )
    result = scope_policy_engine.evaluate(lab, req)
    assert result.decision == ScopeDecision.BLOCKED
    assert "disabled" in result.reason.lower()


def test_scope_blocked_when_asset_not_in_allowlist():
    lab = create_mock_lab(allowed_assets=["asset-1"])
    req = ValidationRequest(
        lab_id="lab-test",
        target_asset_id="asset-unauthorized",
        validation_category="configuration_check",
        requested_action="check_tls_configuration",
    )
    result = scope_policy_engine.evaluate(lab, req)
    assert result.decision == ScopeDecision.BLOCKED
    assert "not in allowed asset scope" in result.reason.lower()


def test_scope_blocked_on_globally_prohibited_action():
    lab = create_mock_lab()
    req = ValidationRequest(
        lab_id="lab-test",
        target_asset_id="asset-1",
        validation_category="configuration_check",
        requested_action="exploit_execution",
    )
    result = scope_policy_engine.evaluate(lab, req)
    assert result.decision == ScopeDecision.BLOCKED
    assert "prohibited" in result.reason.lower()
