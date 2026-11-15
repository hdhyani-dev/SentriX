"""
Unit tests for Pydantic schemas and database models.
"""

import pytest
from pydantic import ValidationError

from schemas.import_schema import (
    LabImportSchema, AssetImportSchema, ServiceImportSchema,
    FindingImportSchema, RelationshipImportSchema, ScopePolicySchema,
)
from core.models.enums import Severity, EvidenceStatus, PathStatus, ValidationResult


def test_lab_schema_validation():
    # Valid lab
    lab = LabImportSchema(id="lab-test", name="Test Lab", description="Description")
    assert lab.id == "lab-test"
    assert lab.name == "Test Lab"

    # Blank name should raise error
    with pytest.raises(ValidationError):
        LabImportSchema(id="lab-test", name="   ")


def test_finding_schema_severity_validation():
    # Valid severity
    f = FindingImportSchema(
        id="f-1", lab_id="l-1", asset_id="a-1",
        title="Test Finding", category="config", severity="high"
    )
    assert f.severity == "high"

    # Invalid severity should be rejected
    with pytest.raises(ValidationError):
        FindingImportSchema(
            id="f-1", lab_id="l-1", asset_id="a-1",
            title="Test Finding", category="config", severity="ultra_critical"
        )


def test_relationship_schema_validation():
    # Valid relationship
    rel = RelationshipImportSchema(
        id="r-1", lab_id="l-1", source_node_id="a-1", target_node_id="a-2",
        relationship_type="connects_to", evidence_status="observed"
    )
    assert rel.source_node_id == "a-1"
    assert rel.target_node_id == "a-2"

    # Self-loop should be rejected
    with pytest.raises(ValidationError):
        RelationshipImportSchema(
            id="r-1", lab_id="l-1", source_node_id="a-1", target_node_id="a-1",
            relationship_type="connects_to"
        )

    # Invalid evidence status should be rejected
    with pytest.raises(ValidationError):
        RelationshipImportSchema(
            id="r-1", lab_id="l-1", source_node_id="a-1", target_node_id="a-2",
            relationship_type="connects_to", evidence_status="rumor"
        )
