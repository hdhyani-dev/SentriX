"""
Pydantic schemas for importing lab data from JSON.

These schemas validate external input before it reaches the database.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ScopePolicySchema(BaseModel):
    """Schema for lab scope policy within an import."""
    allowed_asset_ids: list[str] = Field(default_factory=list)
    allowed_validation_categories: list[str] = Field(default_factory=list)
    prohibited_actions: list[str] = Field(default_factory=list)
    validation_enabled: bool = True
    notes: str | None = None


class LabImportSchema(BaseModel):
    """Schema for importing a laboratory definition."""
    id: str = Field(..., min_length=1, max_length=36)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    scope_policy: ScopePolicySchema | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Lab name must not be blank")
        return v.strip()


class AssetImportSchema(BaseModel):
    """Schema for importing an asset."""
    id: str = Field(..., min_length=1, max_length=36)
    lab_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=255)
    hostname: str | None = None
    ip_address: str | None = None
    asset_type: str = "server"
    operating_system: str | None = None
    os_version: str | None = None
    description: str | None = None
    metadata: dict[str, Any] | None = None


class ServiceImportSchema(BaseModel):
    """Schema for importing a service."""
    id: str = Field(..., min_length=1, max_length=36)
    asset_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=255)
    protocol: str | None = None
    port: int | None = Field(None, ge=0, le=65535)
    version: str | None = None
    description: str | None = None
    evidence_id: str | None = None


class FindingImportSchema(BaseModel):
    """Schema for importing a security finding."""
    id: str = Field(..., min_length=1, max_length=36)
    lab_id: str = Field(..., min_length=1)
    asset_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    category: str = Field(..., min_length=1)
    severity: str = "unknown"
    external_reference: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    source: str | None = None
    status: str = "open"
    remediation: str | None = None

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        allowed = {"informational", "low", "medium", "high", "critical", "unknown"}
        if v.lower() not in allowed:
            raise ValueError(f"Severity must be one of {allowed}, got '{v}'")
        return v.lower()


class RelationshipImportSchema(BaseModel):
    """Schema for importing a relationship (graph edge)."""
    id: str = Field(..., min_length=1, max_length=36)
    lab_id: str = Field(..., min_length=1)
    source_node_id: str = Field(..., min_length=1)
    target_node_id: str = Field(..., min_length=1)
    relationship_type: str = Field(..., min_length=1)
    evidence_ids: list[str] = Field(default_factory=list)
    evidence_status: str = "observed"
    description: str | None = None
    confidence_rationale: str | None = None
    source: str | None = None

    @field_validator("evidence_status")
    @classmethod
    def validate_evidence_status(cls, v: str) -> str:
        allowed = {"observed", "inferred", "verified", "missing", "contradicted"}
        if v.lower() not in allowed:
            raise ValueError(f"Evidence status must be one of {allowed}, got '{v}'")
        return v.lower()

    @field_validator("target_node_id")
    @classmethod
    def source_target_differ(cls, v: str, info) -> str:
        if info.data.get("source_node_id") == v:
            raise ValueError("source_node_id and target_node_id must differ")
        return v


class EvidenceImportSchema(BaseModel):
    """Schema for importing an evidence record."""
    id: str = Field(..., min_length=1, max_length=36)
    lab_id: str = Field(..., min_length=1)
    evidence_type: str = Field(..., min_length=1)
    source: str | None = None
    description: str | None = None
    content: dict[str, Any] | str | None = None
    related_asset_id: str | None = None
    related_finding_id: str | None = None
    related_relationship_id: str | None = None


class FullLabImportSchema(BaseModel):
    """Complete lab import package — lab + all child records."""
    lab: LabImportSchema
    assets: list[AssetImportSchema] = Field(default_factory=list)
    services: list[ServiceImportSchema] = Field(default_factory=list)
    findings: list[FindingImportSchema] = Field(default_factory=list)
    relationships: list[RelationshipImportSchema] = Field(default_factory=list)
    evidence: list[EvidenceImportSchema] = Field(default_factory=list)
