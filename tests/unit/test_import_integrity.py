"""
Unit tests for lab import referential integrity and zero-dangling-reference enforcement.
"""

import pytest
from core.services.lab_service import lab_service
from database.repositories import lab_repo


def test_import_rejects_dangling_service_reference(fresh_session):
    """Verify import is aborted with zero writes when a service references a non-existent asset."""
    session = fresh_session

    data = {
        "lab": {
            "id": "lab-integrity-01",
            "name": "Integrity Test Lab 01",
            "scope_policy": {
                "validation_enabled": True,
                "allowed_asset_ids": ["asset-01"],
                "allowed_validation_categories": ["configuration_check"],
            },
        },
        "assets": [
            {"id": "asset-01", "lab_id": "lab-integrity-01", "name": "Host 01", "asset_type": "server"}
        ],
        "services": [
            # References asset-999 which does NOT exist in assets!
            {"id": "svc-01", "asset_id": "asset-999", "name": "SSH", "port": 22}
        ],
        "findings": [],
        "relationships": [],
        "evidence": [],
    }

    result = lab_service.import_full_lab(session, data)
    assert len(result["errors"]) >= 1
    assert "dangling asset_id 'asset-999'" in result["errors"][0]

    # Verify no records were persisted
    assert lab_repo.get_by_id(session, "lab-integrity-01") is None


def test_import_rejects_cross_lab_asset_pollution(fresh_session):
    """Verify import rejects package when child assets have mismatched lab_id."""
    session = fresh_session

    data = {
        "lab": {
            "id": "lab-integrity-02",
            "name": "Integrity Test Lab 02",
            "scope_policy": {"validation_enabled": True},
        },
        "assets": [
            # asset has lab_id="lab-foreign" instead of "lab-integrity-02"
            {"id": "asset-01", "lab_id": "lab-foreign", "name": "Foreign Host", "asset_type": "server"}
        ],
        "services": [],
        "findings": [],
        "relationships": [],
        "evidence": [],
    }

    result = lab_service.import_full_lab(session, data)
    assert len(result["errors"]) >= 1
    assert "mismatched lab_id" in result["errors"][0]
    assert lab_repo.get_by_id(session, "lab-integrity-02") is None


def test_import_rejects_dangling_relationship_endpoints(fresh_session):
    """Verify import rejects relationships connecting missing node IDs."""
    session = fresh_session

    data = {
        "lab": {
            "id": "lab-integrity-03",
            "name": "Integrity Test Lab 03",
            "scope_policy": {"validation_enabled": True},
        },
        "assets": [
            {"id": "asset-01", "lab_id": "lab-integrity-03", "name": "Host 01", "asset_type": "server"}
        ],
        "services": [],
        "findings": [],
        "relationships": [
            # target node asset-missing is dangling
            {
                "id": "rel-01",
                "lab_id": "lab-integrity-03",
                "source_node_id": "asset-01",
                "target_node_id": "asset-missing",
                "relationship_type": "connects_to",
            }
        ],
        "evidence": [],
    }

    result = lab_service.import_full_lab(session, data)
    assert len(result["errors"]) >= 1
    assert "missing target node 'asset-missing'" in result["errors"][0]
    assert lab_repo.get_by_id(session, "lab-integrity-03") is None
