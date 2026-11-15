# Test Plan — ChainBreak

## 1. Test Strategy
Testing in ChainBreak verifies that:
1. Input data schemas reject malformed input, invalid severities, and self-loop relationships.
2. NetworkX graph builder reliably handles cycles, multi-hop sequences, and disconnected components.
3. Candidate path discovery attaches evidence, identifies missing evidence, and respects bounding limits.
4. Scope controller fails closed on missing policy, disabled labs, out-of-scope assets, and prohibited actions.
5. Blocked validations NEVER invoke the underlying validator.
6. Allowed validations execute safely against local configuration records.
7. Reports are accurately generated in Markdown and HTML.
8. The entire workflow operates deterministically without external API keys.

## 2. Test Suites
- **Unit Tests (`tests/unit/`):**
  - `test_models_and_schemas.py`: Pydantic schema validation for labs, findings, and relationships.
  - `test_graph.py`: Graph creation, cycle safety, disconnected nodes, and evidence tracking.
  - `test_scope_and_validation.py`: Fail-closed policy evaluation under various boundary conditions.
- **Integration Tests (`tests/integration/`):**
  - `test_full_lifecycle.py`: End-to-end flow from JSON import to graph, candidate path reasoning, scope validation, AI fallback, and report export.
- **Automated Verification Script (`scripts/run_checks.py`):**
  - Runs full health checks across SQLite, loaded fixtures, path reasoning, validation, and reporting.

## 3. Execution Commands
```powershell
# Run full Pytest suite
.\venv\Scripts\pytest.exe -v

# Run platform self-checks
.\venv\Scripts\python.exe scripts\run_checks.py
```
