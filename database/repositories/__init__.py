"""
Database repositories for ChainBreak.

Each repository provides CRUD operations for a specific entity type.
All repositories accept a SQLAlchemy session and do not manage transactions.
"""

import json
from typing import TypeVar, Generic, Type
from sqlalchemy.orm import Session

from database.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Generic repository providing common CRUD operations."""

    def __init__(self, model: Type[T]):
        self._model = model

    def create(self, session: Session, **kwargs) -> T:
        instance = self._model(**kwargs)
        session.add(instance)
        session.flush()
        return instance

    def get_by_id(self, session: Session, record_id: str) -> T | None:
        return session.get(self._model, record_id)

    def get_all(self, session: Session) -> list[T]:
        return list(session.query(self._model).all())

    def get_by_field(self, session: Session, field_name: str, value) -> list[T]:
        column = getattr(self._model, field_name, None)
        if column is None:
            raise ValueError(f"{self._model.__name__} has no field '{field_name}'")
        return list(session.query(self._model).filter(column == value).all())

    def update(self, session: Session, record_id: str, **kwargs) -> T | None:
        instance = self.get_by_id(session, record_id)
        if instance is None:
            return None
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        session.flush()
        return instance

    def delete(self, session: Session, record_id: str) -> bool:
        instance = self.get_by_id(session, record_id)
        if instance is None:
            return False
        session.delete(instance)
        session.flush()
        return True

    def count(self, session: Session) -> int:
        return session.query(self._model).count()


# --- Specific repository instances ---

from core.models.lab import Laboratory
from core.models.asset import Asset
from core.models.service import Service
from core.models.finding import Finding
from core.models.relationship import Relationship
from core.models.evidence import Evidence
from core.models.attack_path import AttackPath
from core.models.validation import Validation
from core.models.audit_log import AuditLog


class LabRepository(BaseRepository[Laboratory]):
    def __init__(self):
        super().__init__(Laboratory)

    def get_by_name(self, session: Session, name: str) -> Laboratory | None:
        return session.query(Laboratory).filter(Laboratory.name == name).first()


class AssetRepository(BaseRepository[Asset]):
    def __init__(self):
        super().__init__(Asset)

    def get_by_lab(self, session: Session, lab_id: str) -> list[Asset]:
        return self.get_by_field(session, "lab_id", lab_id)


class ServiceRepository(BaseRepository[Service]):
    def __init__(self):
        super().__init__(Service)

    def get_by_asset(self, session: Session, asset_id: str) -> list[Service]:
        return self.get_by_field(session, "asset_id", asset_id)


class FindingRepository(BaseRepository[Finding]):
    def __init__(self):
        super().__init__(Finding)

    def get_by_lab(self, session: Session, lab_id: str) -> list[Finding]:
        return self.get_by_field(session, "lab_id", lab_id)

    def get_by_asset(self, session: Session, asset_id: str) -> list[Finding]:
        return self.get_by_field(session, "asset_id", asset_id)

    def get_by_severity(self, session: Session, lab_id: str, severity: str) -> list[Finding]:
        return list(
            session.query(Finding)
            .filter(Finding.lab_id == lab_id, Finding.severity == severity)
            .all()
        )


class RelationshipRepository(BaseRepository[Relationship]):
    def __init__(self):
        super().__init__(Relationship)

    def get_by_lab(self, session: Session, lab_id: str) -> list[Relationship]:
        return self.get_by_field(session, "lab_id", lab_id)

    def get_by_source(self, session: Session, source_id: str) -> list[Relationship]:
        return self.get_by_field(session, "source_node_id", source_id)

    def get_by_target(self, session: Session, target_id: str) -> list[Relationship]:
        return self.get_by_field(session, "target_node_id", target_id)


class EvidenceRepository(BaseRepository[Evidence]):
    def __init__(self):
        super().__init__(Evidence)

    def get_by_lab(self, session: Session, lab_id: str) -> list[Evidence]:
        return self.get_by_field(session, "lab_id", lab_id)


class AttackPathRepository(BaseRepository[AttackPath]):
    def __init__(self):
        super().__init__(AttackPath)

    def get_by_lab(self, session: Session, lab_id: str) -> list[AttackPath]:
        return self.get_by_field(session, "lab_id", lab_id)


class ValidationRepository(BaseRepository[Validation]):
    def __init__(self):
        super().__init__(Validation)

    def get_by_lab(self, session: Session, lab_id: str) -> list[Validation]:
        return self.get_by_field(session, "lab_id", lab_id)


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self):
        super().__init__(AuditLog)

    def get_by_lab(self, session: Session, lab_id: str) -> list[AuditLog]:
        return self.get_by_field(session, "lab_id", lab_id)

    def get_by_event_type(self, session: Session, event_type: str) -> list[AuditLog]:
        return self.get_by_field(session, "event_type", event_type)


# Singleton instances
lab_repo = LabRepository()
asset_repo = AssetRepository()
service_repo = ServiceRepository()
finding_repo = FindingRepository()
relationship_repo = RelationshipRepository()
evidence_repo = EvidenceRepository()
attack_path_repo = AttackPathRepository()
validation_repo = ValidationRepository()
audit_log_repo = AuditLogRepository()
