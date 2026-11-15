"""
SQLAlchemy ORM model for Relationship (graph edge).
"""

from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from core.models.lab import _new_id, _utcnow


class Relationship(Base):
    __tablename__ = "relationships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    lab_id: Mapped[str] = mapped_column(String(36), ForeignKey("laboratories.id", ondelete="CASCADE"), nullable=False, index=True)
    source_node_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    target_node_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False)
    evidence_ids_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_status: Mapped[str] = mapped_column(String(20), nullable=False, default="observed")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    # Relationships
    lab = relationship("Laboratory", back_populates="relationships_list")

    def __repr__(self) -> str:
        return f"<Relationship(id={self.id!r}, {self.source_node_id} --{self.relationship_type}--> {self.target_node_id})>"
