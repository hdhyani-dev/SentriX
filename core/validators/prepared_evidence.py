"""
Prepared Evidence Validator — safe, read-only verification against stored evidence snapshots.
"""

from typing import Any

from core.models.enums import ValidationResult, ValidationCategory
from core.validators.base import BaseValidator, ValidationOutcome
from core.models.evidence import Evidence


class PreparedEvidenceValidator(BaseValidator):
    """Verifies findings against stored, pre-collected synthetic evidence."""

    @property
    def category(self) -> str:
        return ValidationCategory.PREPARED_EVIDENCE.value

    def validate(self, context: dict[str, Any]) -> ValidationOutcome:
        action = context.get("requested_action", "")
        evidence_records: list[Evidence] = context.get("evidence_records", [])

        if not evidence_records:
            return ValidationOutcome(
                result=ValidationResult.INCONCLUSIVE,
                reason="No evidence records supplied for prepared evidence verification.",
                validator_module="core.validators.prepared_evidence",
            )

        if action == "verify_evidence_integrity":
            # Check SHA-256 integrity of content
            mismatches = []
            for ev in evidence_records:
                if ev.content_json and ev.content_hash:
                    calculated = Evidence.compute_hash(ev.content_json)
                    if calculated != ev.content_hash:
                        mismatches.append(ev.id)
            if mismatches:
                return ValidationOutcome(
                    result=ValidationResult.NOT_CONFIRMED,
                    reason=f"Hash integrity check failed for evidence ID(s): {', '.join(mismatches)}.",
                    validator_module="core.validators.prepared_evidence",
                    details={"mismatched_ids": mismatches},
                )
            return ValidationOutcome(
                result=ValidationResult.CONFIRMED,
                reason=f"Evidence integrity verified for {len(evidence_records)} record(s).",
                validator_module="core.validators.prepared_evidence",
            )

        elif action in ("verify_evidence_claim", "compare_evidence_content"):
            finding = context.get("finding")
            if not finding:
                return ValidationOutcome(
                    result=ValidationResult.INCONCLUSIVE,
                    reason="Finding context required to evaluate evidence claim.",
                    validator_module="core.validators.prepared_evidence",
                )
            
            # Check if any evidence explicitly associates with this finding
            matched = [ev for ev in evidence_records if ev.related_finding_id == finding.id or ev.id in (finding.evidence_ids_json or "")]
            if matched:
                return ValidationOutcome(
                    result=ValidationResult.CONFIRMED,
                    reason=f"Claim in finding '{finding.title}' is supported by {len(matched)} matching evidence record(s).",
                    validator_module="core.validators.prepared_evidence",
                    details={"matched_evidence_ids": [m.id for m in matched]},
                )
            else:
                return ValidationOutcome(
                    result=ValidationResult.NOT_CONFIRMED,
                    reason="No matching evidence records link to this finding.",
                    validator_module="core.validators.prepared_evidence",
                )

        return ValidationOutcome(
            result=ValidationResult.INCONCLUSIVE,
            reason=f"Unrecognized prepared evidence action '{action}'.",
            validator_module="core.validators.prepared_evidence",
        )


prepared_evidence_validator = PreparedEvidenceValidator()
