"""
SQLAlchemy ORM model for Asset.
"""

from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from core.models.lab import _new_id, _utcnow


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    lab_id: Mapped[str] = mapped_column(String(36), ForeignKey("laboratories.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hostname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False, default="server")
    operating_system: Mapped[str | None] = mapped_column(String(255), nullable=True)
    os_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    # Relationships
    lab = relationship("Laboratory", back_populates="assets")
    services = relationship("Service", back_populates="asset", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="asset", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Asset(id={self.id!r}, name={self.name!r}, lab_id={self.lab_id!r})>"
