"""
SQLAlchemy ORM model for Validation.
"""

from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, _new_id, _utcnow


class Validation(Base):
    __tablename__ = "validations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    lab_id: Mapped[str] = mapped_column(String(36), ForeignKey("laboratories.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id: Mapped[str] = mapped_column(String(36), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    finding_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("findings.id", ondelete="SET NULL"), nullable=True)
    validation_category: Mapped[str] = mapped_column(String(50), nullable=False)
    requested_action: Mapped[str] = mapped_column(String(255), nullable=False)
    scope_decision: Mapped[str] = mapped_column(String(20), nullable=False)
    result: Mapped[str] = mapped_column(String(20), nullable=False, default="not_run")
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_ids_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    validator_module: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    # Relationships
    lab = relationship("Laboratory", back_populates="validations")

    def __repr__(self) -> str:
        return f"<Validation(id={self.id!r}, result={self.result}, decision={self.scope_decision})>"
