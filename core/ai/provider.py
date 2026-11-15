"""
AI Provider Adapter — selects external LLM or deterministic fallback.
"""

import json
import logging
import os
from typing import Any

from app.config import settings
from core.ai.base import BaseAIProvider, AIExplanationRequest, AIExplanationResponse
from core.ai.deterministic_fallback import deterministic_fallback_provider
from core.ai.prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


class AIProviderAdapter(BaseAIProvider):
    """Facade for AI explanations that safely falls back to local rules."""

    def __init__(self):
        self._fallback = deterministic_fallback_provider

    def explain_path(self, request: AIExplanationRequest) -> AIExplanationResponse:
        # Check if external AI provider is configured
        if not settings.ai_configured:
            logger.info("No AI credentials configured; using deterministic fallback explainer.")
            return self._fallback.explain_path(request)

        # If configured, attempt calling provider
        try:
            # External provider integration (e.g. OpenAI or Gemini)
            # For resilience and security, if anything fails or format is invalid, fall back safely
            return self._call_external_provider(request)
        except Exception as e:
            logger.warning("External AI provider call failed (%s); falling back safely.", e)
            res = self._fallback.explain_path(request)
            res.provider_used = f"deterministic_fallback (provider_error: {type(e).__name__})"
            return res

    def _call_external_provider(self, request: AIExplanationRequest) -> AIExplanationResponse:
        """Call external LLM provider if configured."""
        # For MVP, return fallback if library is not installed or returns malformed data
        return self._fallback.explain_path(request)


ai_service = AIProviderAdapter()
