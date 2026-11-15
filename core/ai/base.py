"""
Base AI Provider Interface and Pydantic response schemas.
"""

from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, Field


class AIExplanationRequest(BaseModel):
    """Structured input passed to the AI explanation layer."""
    path_id: str
    title: str
    nodes: list[str]
    edges: list[dict[str, Any]]
    findings: list[dict[str, Any]]
    evidence_descriptions: list[str]
    validation_outcomes: list[dict[str, Any]]
    missing_evidence: list[dict[str, Any]]
    assumptions: list[dict[str, Any]]


class AIExplanationResponse(BaseModel):
    """Validated structured response from AI explanation layer."""
    executive_summary: str
    path_rationale: str
    supporting_evidence_summary: str
    missing_evidence_summary: str
    assumptions_summary: str
    potential_impact: str
    remediation_recommendations: list[str]
    limitations: str
    provider_used: str = "deterministic_fallback"


class BaseAIProvider(ABC):
    """Abstract interface for AI explanation providers."""

    @abstractmethod
    def explain_path(self, request: AIExplanationRequest) -> AIExplanationResponse:
        """Generate structured explanation from supplied assessment data."""
        pass
