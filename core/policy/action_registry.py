"""
Action Registry — defines recognized validation categories and action safety classification.
"""

from core.models.enums import ValidationCategory


# Explicitly prohibited operations (fail-closed, must never be run)
PROHIBITED_ACTIONS = {
    "exploit_execution",
    "credential_extraction",
    "credential_cracking",
    "privilege_escalation",
    "network_scanning",
    "port_scanning",
    "lateral_movement",
    "destructive_testing",
    "persistence_installation",
    "shell_execution",
}

# Permitted safe read-only operations
PERMITTED_CATEGORIES = {
    ValidationCategory.PREPARED_EVIDENCE.value: {
        "verify_evidence_integrity",
        "verify_evidence_claim",
        "compare_evidence_content",
    },
    ValidationCategory.CONFIGURATION_CHECK.value: {
        "check_tls_configuration",
        "check_http_security_headers",
        "check_database_bind_address",
        "check_process_permissions",
    },
    ValidationCategory.SERVICE_INVENTORY_CHECK.value: {
        "check_service_record_exists",
        "verify_service_port_inventory",
    },
    ValidationCategory.POLICY_RULE_CHECK.value: {
        "verify_least_privilege_rule",
        "verify_network_isolation_rule",
    },
}


def is_action_prohibited(action_name: str) -> bool:
    """Check if requested action is fundamentally prohibited."""
    return action_name.lower().strip() in PROHIBITED_ACTIONS


def is_action_permitted_in_category(category: str, action_name: str) -> bool:
    """Check if action is recognized under a permitted safe category."""
    allowed_actions = PERMITTED_CATEGORIES.get(category, set())
    return action_name.lower().strip() in allowed_actions
