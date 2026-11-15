"""
Controlled enumerations for ChainBreak domain model.

These enums enforce consistent status values across the entire application.
"""

from enum import Enum


class Severity(str, Enum):
    """Severity scale for security findings."""
    INFORMATIONAL = "informational"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class EvidenceStatus(str, Enum):
    """Status of evidence supporting a finding or relationship."""
    OBSERVED = "observed"
    INFERRED = "inferred"
    VERIFIED = "verified"
    MISSING = "missing"
    CONTRADICTED = "contradicted"


class PathStatus(str, Enum):
    """Status of a candidate attack/risk path."""
    CANDIDATE = "candidate"
    UNDER_REVIEW = "under_review"
    PARTIALLY_SUPPORTED = "partially_supported"
    SUPPORTED = "supported"
    INCONCLUSIVE = "inconclusive"
    BLOCKED = "blocked"
    CLOSED = "closed"


class ValidationResult(str, Enum):
    """Result of a validation operation."""
    CONFIRMED = "confirmed"
    NOT_CONFIRMED = "not_confirmed"
    INCONCLUSIVE = "inconclusive"
    BLOCKED = "blocked"
    NOT_RUN = "not_run"


class ScopeDecision(str, Enum):
    """Scope controller decision for a validation request."""
    ALLOWED = "allowed"
    BLOCKED = "blocked"


class FindingStatus(str, Enum):
    """Status of a security finding."""
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    REMEDIATED = "remediated"
    ACCEPTED = "accepted"


class NodeType(str, Enum):
    """Types of nodes in the security graph."""
    ASSET = "asset"
    SERVICE = "service"
    FINDING = "finding"
    PERMISSION = "permission"
    CONTROL = "control"


class RelationshipType(str, Enum):
    """Types of edges in the security graph."""
    HOSTS = "hosts"
    EXPOSES_SERVICE = "exposes_service"
    AFFECTED_BY = "affected_by"
    CONNECTS_TO = "connects_to"
    HAS_PERMISSION = "has_permission"
    DEPENDS_ON = "depends_on"
    EVIDENCE_SUPPORTS = "evidence_supports"


class AssetType(str, Enum):
    """Types of lab assets."""
    SERVER = "server"
    WORKSTATION = "workstation"
    NETWORK_DEVICE = "network_device"
    DATABASE = "database"
    APPLICATION = "application"
    CONTAINER = "container"
    OTHER = "other"


class ValidationCategory(str, Enum):
    """Categories of validation operations."""
    PREPARED_EVIDENCE = "prepared_evidence"
    CONFIGURATION_CHECK = "configuration_check"
    SERVICE_INVENTORY_CHECK = "service_inventory_check"
    POLICY_RULE_CHECK = "policy_rule_check"


class EventType(str, Enum):
    """Types of audit log events."""
    LAB_CREATED = "lab_created"
    LAB_UPDATED = "lab_updated"
    DATA_IMPORTED = "data_imported"
    GRAPH_BUILT = "graph_built"
    PATHS_GENERATED = "paths_generated"
    VALIDATION_REQUESTED = "validation_requested"
    VALIDATION_ALLOWED = "validation_allowed"
    VALIDATION_BLOCKED = "validation_blocked"
    VALIDATION_COMPLETED = "validation_completed"
    REPORT_GENERATED = "report_generated"
    SCOPE_CHECK = "scope_check"
    PATH_STATUS_CHANGED = "path_status_changed"
    EVIDENCE_ADDED = "evidence_added"
