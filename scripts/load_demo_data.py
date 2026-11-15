"""
Script to load the synthetic demo lab into ChainBreak database.
"""

import json
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from database.connection import init_db, get_session
from core.services.lab_service import lab_service


def main():
    print("Initializing database tables if not present...")
    init_db()

    demo_file = project_root / "data" / "demo_lab" / "full_lab.json"
    if not demo_file.exists():
        print(f"Error: Demo file not found at {demo_file}")
        sys.exit(1)

    print(f"Loading demo dataset from {demo_file}...")
    with open(demo_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    with get_session() as session:
        result = lab_service.import_full_lab(session, data)

    if result.get("errors"):
        print("Import completed with notices/errors:")
        for err in result["errors"]:
            print(f"  - {err}")
    else:
        print("Demo lab imported successfully!")
        print("Counts:")
        for k, v in result["counts"].items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
