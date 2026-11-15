"""
SQLAlchemy ORM model for Laboratory.
"""

from datetime import datetime

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, _new_id, _utcnow


class Laboratory(Base):
    __tablename__ = "laboratories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    scope_policy_json: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    # Relationships
    assets = relationship("Asset", back_populates="lab", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="lab", cascade="all, delete-orphan")
    relationships_list = relationship("Relationship", back_populates="lab", cascade="all, delete-orphan")
    evidence_list = relationship("Evidence", back_populates="lab", cascade="all, delete-orphan")
    attack_paths = relationship("AttackPath", back_populates="lab", cascade="all, delete-orphan")
    validations = relationship("Validation", back_populates="lab", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="lab", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Laboratory(id={self.id!r}, name={self.name!r})>"
