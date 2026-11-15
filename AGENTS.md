# AGENTS.md — ChainBreak

## Project Description
ChainBreak is an AI-assisted cybersecurity analysis platform that models laboratory
assets, services, findings, permissions and relationships as a graph. It identifies
candidate multi-step risk paths, associates each path with evidence, evaluates
uncertainty, enforces laboratory scope, and records safe validation results.

## Architecture
- **Language:** Python 3.11+
- **Interface:** Streamlit (minimal development UI)
- **Graph Engine:** NetworkX
- **Database:** SQLite via SQLAlchemy
- **Validation:** Pydantic
- **Testing:** Pytest

## Key Directories
- `app/` — Streamlit UI pages
- `core/models/` — Domain enums and data models
- `core/services/` — Application/business logic services
- `core/graph/` — NetworkX graph construction and analysis
- `core/policy/` — Scope enforcement and action authorization
- `core/validators/` — Safe read-only validation checks
- `core/ai/` — Optional AI explanation layer
- `core/reporting/` — Report generation (Markdown/HTML)
- `database/` — SQLAlchemy ORM, connection, repositories
- `schemas/` — Pydantic input/output schemas
- `data/demo_lab/` — Synthetic demo dataset
- `scripts/` — DB initialization, demo loading, checks
- `tests/` — Unit, integration, and fixture tests

## Conventions
- Type hints on all public functions
- Controlled enumerations for status values
- Evidence-first: every finding/relationship must reference evidence or state it is missing
- Scope enforcement is server-side, fail-closed
- AI is optional — system works fully without API keys
- No offensive or destructive capabilities
