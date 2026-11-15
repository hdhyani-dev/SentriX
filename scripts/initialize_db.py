"""
Initialize the ChainBreak database.

Creates all tables from ORM models. Safe to run multiple times
(create_all is idempotent).
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from core.models import (
    Laboratory, Asset, Service, Finding, Relationship,
    Evidence, AttackPath, Validation, AuditLog,
)
from database.connection import init_db, engine


def main():
    print("Initializing ChainBreak database...")
    print(f"  Engine URL: {engine.url}")
    init_db()
    print("  All tables created successfully.")
    print("Done.")


if __name__ == "__main__":
    main()
