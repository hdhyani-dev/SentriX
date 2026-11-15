"""
Base validator interface for safe, read-only validation operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from core.models.enums import ValidationResult


@dataclass
class ValidationOutcome:
    """Outcome of running a safe validator."""
    result: ValidationResult
    reason: str
    validator_module: str
    details: dict[str, Any] | None = None


class BaseValidator(ABC):
    """Abstract base class for all safe validators."""

    @property
    @abstractmethod
    def category(self) -> str:
        """The validation category this validator handles."""
        pass

    @abstractmethod
    def validate(self, context: dict[str, Any]) -> ValidationOutcome:
        """Run the safe validation logic against provided local context.

        Must NEVER perform network requests, execute commands, or modify state.
        """
        pass
