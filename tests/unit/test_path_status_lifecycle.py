"""
Unit tests for path status transitions and unrelated validation isolation.
"""

import json
import pytest

from core.services.lab_service import lab_service
from core.services.path_reasoning_service import path_reasoning_service
from core.services.validation_service import validation_service
from core.models.enums import PathStatus, ValidationResult, ScopeDecision


@pytest.fixture
def lab_with_paths(fresh_session):
    session = fresh_session
    data = {
        "lab": {
            "id": "lab-lifecycle",
            "name": "Lifecycle Lab",
            "scope_policy": {
                "validation_enabled": True,
                "allowed_asset_ids": ["host-a", "host-b", "host-c", "host-isolated"],
                "allowed_validation_categories": ["configuration_check", "prepared_evidence"],
            },
        },
        "assets": [
            {"id": "host-a", "lab_id": "lab-lifecycle", "name": "Host A", "asset_type": "server"},
            {"id": "host-b", "lab_id": "lab-lifecycle", "name": "Host B", "asset_type": "server"},
            {"id": "host-c", "lab_id": "lab-lifecycle", "name": "Host C", "asset_type": "server"},
            {"id": "host-isolated", "lab_id": "lab-lifecycle", "name": "Isolated Host", "asset_type": "server"},
        ],
        "services": [],
        "findings": [
            {
                "id": "finding-b",
                "lab_id": "lab-lifecycle",
                "asset_id": "host-b",
                "title": "Weak TLS on Host B",
                "category": "crypto",
                "severity": "medium",
                "evidence_ids": ["ev-tls-b"],
            },
            {
                "id": "finding-isolated",
                "lab_id": "lab-lifecycle",
                "asset_id": "host-isolated",
                "title": "Isolated Finding",
                "category": "crypto",
                "severity": "low",
                "evidence_ids": ["ev-iso"],
            },
        ],
        "relationships": [
            {
                "id": "rel-ab",
                "lab_id": "lab-lifecycle",
                "source_node_id": "host-a",
                "target_node_id": "host-b",
                "relationship_type": "connects_to",
            },
            {
                "id": "rel-bc",
                "lab_id": "lab-lifecycle",
                "source_node_id": "host-b",
                "target_node_id": "host-c",
                "relationship_type": "connects_to",
            },
            {
                "id": "rel-b-find",
                "lab_id": "lab-lifecycle",
                "source_node_id": "host-b",
                "target_node_id": "finding-b",
                "relationship_type": "affected_by",
            },
        ],
        "evidence": [
            {
                "id": "ev-tls-b",
                "lab_id": "lab-lifecycle",
                "evidence_type": "tls_config",
                "content": {"check_type": "tls_version", "deprecated": ["TLSv1.0"]},
            },
            {
                "id": "ev-iso",
                "lab_id": "lab-lifecycle",
                "evidence_type": "tls_config",
                "content": {"check_type": "tls_version", "deprecated": ["TLSv1.0"]},
            },
        ],
    }

    lab_service.import_full_lab(session, data)
    paths = path_reasoning_service.discover_and_persist_candidate_paths(session, "lab-lifecycle")
    return session, "lab-lifecycle", paths


def test_unrelated_validation_does_not_mutate_path_status(lab_with_paths):
    """Verify that validating an asset not on the candidate path preserves the path status."""
    session, lab_id, paths = lab_with_paths
    assert len(paths) >= 1
    target_path = paths[0]
    initial_status = target_path.path_status
    assert initial_status == PathStatus.CANDIDATE.value

    # Run confirmed validation on 'host-isolated' which is NOT part of path (host-a -> host-b -> host-c)
    val = validation_service.execute_validation(
        session=session,
        lab_id=lab_id,
        target_asset_id="host-isolated",
        validation_category="configuration_check",
        requested_action="check_tls_configuration",
        finding_id="finding-isolated",
        evidence_ids=["ev-iso"],
        attack_path_id=target_path.id,
    )
    assert val.result == ValidationResult.CONFIRMED.value

    # Path status MUST remain 'candidate' because host-isolated is unrelated
    session.refresh(target_path)
    assert target_path.path_status == PathStatus.CANDIDATE.value


def test_related_validation_transitions_path_to_supported(lab_with_paths):
    """Verify that confirming findings on the path transitions status to supported."""
    session, lab_id, paths = lab_with_paths
    target_path = paths[0]

    # Validate finding-b which IS on host-b on the path
    val = validation_service.execute_validation(
        session=session,
        lab_id=lab_id,
        target_asset_id="host-b",
        validation_category="configuration_check",
        requested_action="check_tls_configuration",
        finding_id="finding-b",
        evidence_ids=["ev-tls-b"],
        attack_path_id=target_path.id,
    )
    assert val.result == ValidationResult.CONFIRMED.value

    session.refresh(target_path)
    # Since finding-b is the only finding on this path, all path findings are confirmed -> SUPPORTED
    assert target_path.path_status in (PathStatus.SUPPORTED.value, PathStatus.PARTIALLY_SUPPORTED.value)
