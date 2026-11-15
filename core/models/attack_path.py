"""
SQLAlchemy ORM model for AttackPath (candidate risk path).
"""

from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, _new_id, _utcnow


class AttackPath(Base):
    __tablename__ = "attack_paths"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    lab_id: Mapped[str] = mapped_column(String(36), ForeignKey("laboratories.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    path_status: Mapped[str] = mapped_column(String(30), nullable=False, default="candidate")
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    path_data_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    # Relationships
    lab = relationship("Laboratory", back_populates="attack_paths")

    def __repr__(self) -> str:
        return f"<AttackPath(id={self.id!r}, title={self.title!r}, status={self.path_status})>"
