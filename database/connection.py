"""
Database connection management for ChainBreak.

Provides engine creation, session factory, and context manager.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from database.base import Base


def _create_engine(url: str | None = None):
    """Create a SQLAlchemy engine with appropriate settings."""
    db_url = url or settings.DATABASE_URL
    engine = create_engine(
        db_url,
        echo=(settings.LOG_LEVEL == "DEBUG"),
        pool_pre_ping=True,
    )
    # Enable WAL mode and foreign keys for SQLite
    if db_url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()
    return engine


# Default engine and session factory
engine = _create_engine()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


def init_db(engine_override=None) -> None:
    """Create all database tables from ORM models.

    Must be called after all model modules have been imported so that
    Base.metadata is fully populated.
    """
    target_engine = engine_override or engine
    Base.metadata.create_all(bind=target_engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Provide a transactional database session scope.

    Usage:
        with get_session() as session:
            session.add(record)
            # auto-committed on exit, rolled back on exception
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
