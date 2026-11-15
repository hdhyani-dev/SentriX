# Architectural Decisions Log (ADR) — ChainBreak

## ADR-001: Model Structure Location
- **Decision:** Place domain models and ORM entities under `core/models/` rather than a top-level `models/` directory.
- **Rationale:** Aligns with standard layered architecture specified in README.md Section 8. Prevents namespace collision with external packages.

## ADR-002: Bounded Path Enumeration Algorithm
- **Decision:** Use NetworkX's `all_simple_paths` with strict `cutoff` and `max_results` limits, identifying sequences starting from asset nodes and ending at downstream assets or finding nodes.
- **Rationale:** Security graphs frequently contain cycles (e.g. bidirectional communication between servers). Simple path enumeration prevents infinite looping while bounding memory and CPU usage.

## ADR-003: Fail-Closed Scope Enforcement Engine
- **Decision:** Implement scope checking as a required server-side gatekeeper before any validator is instantiated or called. If lab policy is missing or target asset is not allowlisted, return `ScopeDecision.BLOCKED` immediately.
- **Rationale:** UI restrictions alone are insufficient for security boundaries. Prohibits any validator invocation when unauthorized.

## ADR-004: Safe Read-Only Validation Only
- **Decision:** Exclude all offensive execution, scanning, and exploit payloads from the MVP. Implement only static configuration checks and prepared evidence verification.
- **Rationale:** Protects host and target integrity. Ensures safe, repeatable evaluation in educational and assessment settings.

## ADR-005: Deterministic AI Fallback Explainer
- **Decision:** Implement an offline, deterministic explainer that conforms to the exact same Pydantic schema as the LLM provider.
- **Rationale:** Guarantees that the entire application operates seamlessly with zero dependencies on third-party API keys or internet access.
