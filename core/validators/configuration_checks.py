"""
Configuration Checks Validator — safe, read-only inspection of imported configuration snapshots.
"""

import json
from typing import Any

from core.models.enums import ValidationResult, ValidationCategory
from core.validators.base import BaseValidator, ValidationOutcome
from core.models.evidence import Evidence


class ConfigurationChecksValidator(BaseValidator):
    """Performs deterministic checks on configuration snapshots."""

    @property
    def category(self) -> str:
        return ValidationCategory.CONFIGURATION_CHECK.value

    def validate(self, context: dict[str, Any]) -> ValidationOutcome:
        action = context.get("requested_action", "")
        evidence_records: list[Evidence] = context.get("evidence_records", [])

        if not evidence_records:
            return ValidationOutcome(
                result=ValidationResult.INCONCLUSIVE,
                reason="Configuration check requires configuration evidence records.",
                validator_module="core.validators.configuration_checks",
            )

        # Parse config evidence payloads
        configs = []
        for ev in evidence_records:
            if ev.content_json:
                try:
                    configs.append(json.loads(ev.content_json))
                except Exception:
                    pass

        if action == "check_tls_configuration":
            for cfg in configs:
                if cfg.get("check_type") == "tls_version":
                    deprecated = cfg.get("deprecated", [])
                    if deprecated:
                        return ValidationOutcome(
                            result=ValidationResult.CONFIRMED,
                            reason=f"Weak TLS configuration confirmed: deprecated protocol(s) {', '.join(deprecated)} supported.",
                            validator_module="core.validators.configuration_checks",
                            details={"deprecated_protocols": deprecated},
                        )
                    else:
                        return ValidationOutcome(
                            result=ValidationResult.NOT_CONFIRMED,
                            reason="TLS audit shows only modern TLS protocols enabled.",
                            validator_module="core.validators.configuration_checks",
                        )
            return ValidationOutcome(
                result=ValidationResult.INCONCLUSIVE,
                reason="Supplied evidence does not contain a tls_version configuration check.",
                validator_module="core.validators.configuration_checks",
            )

        elif action == "check_database_bind_address":
            for cfg in configs:
                if cfg.get("check_type") == "database_config":
                    bind = cfg.get("bind_address")
                    if bind in ("0.0.0.0", "::"):
                        return ValidationOutcome(
                            result=ValidationResult.CONFIRMED,
                            reason=f"Unrestricted database bind confirmed (bind-address={bind}).",
                            validator_module="core.validators.configuration_checks",
                            details={"bind_address": bind},
                        )
                    else:
                        return ValidationOutcome(
                            result=ValidationResult.NOT_CONFIRMED,
                            reason=f"Database bind address is restricted to '{bind}'.",
                            validator_module="core.validators.configuration_checks",
                        )
            return ValidationOutcome(
                result=ValidationResult.INCONCLUSIVE,
                reason="Supplied evidence does not contain a database_config record.",
                validator_module="core.validators.configuration_checks",
            )

        elif action == "check_process_permissions":
            for cfg in configs:
                if cfg.get("check_type") == "process_permissions":
                    user = cfg.get("user")
                    if user in ("root", "Administrator", "SYSTEM"):
                        return ValidationOutcome(
                            result=ValidationResult.CONFIRMED,
                            reason=f"Excessive process permission confirmed: running as '{user}'.",
                            validator_module="core.validators.configuration_checks",
                            details={"user": user},
                        )
                    else:
                        return ValidationOutcome(
                            result=ValidationResult.NOT_CONFIRMED,
                            reason=f"Process runs under standard least-privilege user '{user}'.",
                            validator_module="core.validators.configuration_checks",
                        )
            return ValidationOutcome(
                result=ValidationResult.INCONCLUSIVE,
                reason="Supplied evidence does not contain process_permissions data.",
                validator_module="core.validators.configuration_checks",
            )

        return ValidationOutcome(
            result=ValidationResult.INCONCLUSIVE,
            reason=f"Unrecognized configuration check action '{action}'.",
            validator_module="core.validators.configuration_checks",
        )


configuration_checks_validator = ConfigurationChecksValidator()
