"""
SQLAlchemy declarative base and common model helpers for all ORM models.
"""

from datetime import datetime, timezone
import uuid

from sqlalchemy.orm import DeclarativeBase


def _utcnow() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)


def _new_id() -> str:
    """Generate a new UUID4 string identifier."""
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models in ChainBreak."""
    pass
