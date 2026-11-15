"""
SQLAlchemy ORM model for Evidence.
"""

import hashlib
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, _new_id, _utcnow


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    lab_id: Mapped[str] = mapped_column(String(36), ForeignKey("laboratories.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_type: Mapped[str] = mapped_column(String(100), nullable=False)
    source: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    related_asset_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    related_finding_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    related_relationship_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    related_validation_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    # Relationships
    lab = relationship("Laboratory", back_populates="evidence_list")

    @staticmethod
    def compute_hash(content: str) -> str:
        """Compute SHA-256 hash of evidence content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def __repr__(self) -> str:
        return f"<Evidence(id={self.id!r}, type={self.evidence_type!r})>"
