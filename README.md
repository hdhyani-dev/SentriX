# SentriX
## Project README, Product Specification & Antigravity Build Instructions

**Document version:** 1.0  
**Project type:** AI-assisted, graph-based cybersecurity risk-path analysis platform  
**Primary language:** Python  
**Initial deployment:** Local, isolated development environment  
**Development IDE:** Google Antigravity  
**Current priority:** Build a working, tested backend and analysis engine first. UI/UX design will be handled as a separate phase after the core functionality is stable.

---

# 1. Instructions to the Antigravity Agent

You are the lead software architect and implementation agent for **ChainBreak**.

Read this entire README before changing or creating project files. Treat it as the source of truth for the initial implementation.

Your task is to build a working, modular, testable application—not merely produce a plan, mockup, or collection of disconnected code snippets.

## Required working method

1. Inspect the existing workspace before making changes.
2. If the workspace is empty, initialize the project using the structure in this README.
3. If files already exist, inspect them and preserve useful working code.
4. Implement the application in the phases specified below.
5. Do not stop after creating placeholder files. Implement functional modules and connect them.
6. Run tests after each major phase and fix failures before proceeding.
7. Keep a `docs/IMPLEMENTATION_STATUS.md` file updated with completed work, test results, known limitations and next steps.
8. Keep `docs/DECISIONS.md` updated when an architectural decision is made.
9. Do not silently change the architecture or add major dependencies. Explain the reason and record the decision.
10. Do not claim a feature works unless it has been implemented and tested.
11. Do not fabricate scan results, validation outcomes, evidence or test results.
12. At completion, provide a concise summary of implemented modules, commands to run the application, tests executed, known limitations and remaining work.

**Important UI instruction:** The immediate goal is the functional application and its underlying logic. Create only a simple, usable development interface if one is needed to exercise the system. Do not spend time polishing visual design, animations, branding, dashboard styling or elaborate layouts. UI/UX design will be specified separately after the core system works.

If a requirement is ambiguous, choose the simplest safe implementation, document the assumption and continue. Ask for clarification only when a decision would materially change the architecture or create a safety/security issue.

---

# 2. Product Overview

## 2.1 Product name

**ChainBreak — Multi-Step Attack Simulation and Risk-Path Analysis Agent**

## 2.2 Product definition

ChainBreak is an AI-assisted cybersecurity analysis platform that examines how multiple security weaknesses may combine into a larger security risk within an explicitly authorized laboratory environment.

It represents laboratory assets, services, security findings, permissions and observed relationships as a graph. Its analysis engine identifies candidate multi-step risk paths, associates each path with supporting evidence, evaluates uncertainty, checks laboratory scope and records safe validation results.

ChainBreak is an analysis and controlled-validation platform. It must not become an unrestricted autonomous penetration-testing tool.

## 2.3 Problem statement

Traditional vulnerability assessment commonly reports weaknesses as individual findings. That can make it difficult to understand how findings across connected systems relate to one another or how their combined presence could create a broader risk.

ChainBreak aims to help an analyst answer:

- Which assets and services exist in the authorized lab?
- Which security findings affect each asset?
- Which relationships between assets are actually supported by evidence?
- Which combinations of findings may create a broader risk?
- What evidence supports each candidate path?
- Which conditions have been verified, inferred or remain unknown?
- Is a proposed validation permitted by the lab scope?
- What is the potential impact and recommended remediation?

## 2.4 Product principles

1. **Evidence first:** Every important finding and graph relationship should have traceable evidence or an explicit statement that evidence is missing.
2. **Deterministic core:** Graph construction, scope enforcement, validation decisions and status transitions must be controlled by deterministic application logic—not by an LLM.
3. **Explainable analysis:** Every candidate path should explain why it was generated.
4. **Uncertainty is explicit:** A graph path is not proof of exploitability.
5. **Scope is enforced server-side:** UI restrictions alone are insufficient.
6. **Safe by default:** Initial operation uses synthetic data, imported evidence and read-only checks.
7. **AI is assistive:** An LLM may explain structured results but must not invent evidence or override policy.
8. **Modular implementation:** UI, data models, graph logic, policy enforcement, AI and reporting must remain separate.

---

# 3. Goals and Non-Goals

## 3.1 MVP goals

The first working release must:

- Run locally.
- Load a prepared, clearly labelled simulated lab.
- Import and validate lab data from JSON.
- Store labs, assets, services, findings, relationships, evidence, candidate paths, validation records and audit logs.
- Build a graph using NetworkX.
- Identify candidate paths from configured, evidence-backed relationships.
- Explain why each candidate path was generated.
- Distinguish observed, inferred, validated, inconclusive and blocked states.
- Enforce a strict lab asset allowlist and permitted-action policy.
- Support safe, read-only or prepared-evidence validation only.
- Maintain an audit trail.
- Produce a useful report, initially as Markdown or HTML; PDF may be added if straightforward.
- Include automated tests and a repeatable demo dataset.

## 3.2 Explicit non-goals for the MVP

Do not implement:

- Unauthorized network scanning.
- Public internet target discovery.
- Exploit execution.
- Credential theft, extraction or cracking.
- Persistence, evasion or stealth.
- Automated lateral movement.
- Destructive testing.
- Automated privilege escalation.
- Unrestricted command execution.
- Autonomous penetration testing.
- Production-network deployment.

Do not add offensive capabilities merely because a tool or library makes them possible.

---

# 4. Target Users and Use Cases

## Primary users

- Cybersecurity students.
- Security researchers working in authorized labs.
- Security assessment analysts.
- Cybersecurity instructors and project evaluators.

## Core user journeys

### Journey A: Load a lab

1. User opens ChainBreak.
2. User creates a lab or imports a prepared JSON dataset.
3. The application validates the input.
4. The application stores the lab and its scope.
5. The user views the registered assets and services.

### Journey B: Analyze findings

1. User imports or enters security findings.
2. The application associates each finding with an asset.
3. The graph engine creates nodes and evidence-backed relationships.
4. The reasoning engine identifies candidate risk paths.
5. The user opens a path and reviews its evidence and uncertainty.

### Journey C: Validate safely

1. User selects a candidate finding or path for review.
2. The scope controller checks the lab, target asset and requested validation category.
3. If the request is not permitted, it is blocked and logged.
4. If permitted, only an implemented safe, read-only or prepared-evidence check can run.
5. The application records the result and evidence.
6. The path status is updated only according to explicit status rules.

### Journey D: Generate a report

1. User selects a lab and assessment.
2. The reporting service gathers assets, findings, paths, evidence and validation records.
3. The report distinguishes facts, inferences and unknowns.
4. User exports the report.

---

# 5. Terminology and Status Model

Use these terms consistently throughout the codebase and reports.

## 5.1 Graph concepts

- **Node:** An asset, service, finding, permission/control or other modeled object.
- **Edge:** A relationship between two nodes.
- **Evidence:** A source record supporting a finding or relationship.
- **Candidate path:** A graph-derived sequence of relationships that may represent a combined risk scenario.
- **Path explanation:** A structured explanation of why the path was selected.

## 5.2 Evidence status

Use a controlled enumeration such as:

- `observed` — directly present in an imported or collected record.
- `inferred` — derived from multiple records or a documented rule.
- `verified` — confirmed by an approved, safe check.
- `missing` — expected evidence is unavailable.
- `contradicted` — evidence conflicts with the claim.

Do not use a single numeric confidence value as a substitute for explaining evidence quality.

## 5.3 Path status

Use a controlled enumeration:

- `candidate` — identified by graph analysis.
- `under_review` — awaiting analyst review.
- `partially_supported` — some, but not all, required conditions have evidence.
- `supported` — the modeled conditions have sufficient evidence for the stated risk assessment.
- `inconclusive` — available information is insufficient.
- `blocked` — a requested validation was rejected by policy.
- `closed` — analyst has closed the assessment.

Never label a candidate graph route as an exploited, successful or proven attack.

## 5.4 Validation result

Use:

- `confirmed`
- `not_confirmed`
- `inconclusive`
- `blocked`
- `not_run`

A validation result applies to a specific condition or finding. It must not automatically prove every edge or the entire multi-step path.

---

# 6. Functional Requirements

## FR-01: Laboratory management

- Create, list, view and update laboratories.
- Store a unique lab ID, name, description and creation time.
- Store a lab scope policy.
- Support importing a lab from JSON.
- Validate imported data before writing to the database.
- Reject malformed or inconsistent input with useful error messages.

## FR-02: Asset inventory

Each asset should support:

- Unique asset ID.
- Lab ID.
- Name.
- Optional hostname and IP address.
- Asset type.
- Optional operating system and version.
- Description.
- Metadata.
- Creation and update timestamps.

Do not assume an IP address is present for every asset.

## FR-03: Service inventory

Each service should support:

- Unique service ID.
- Parent asset ID.
- Service name.
- Optional protocol and port.
- Optional version.
- Description.
- Source/evidence reference.
- Observation timestamp.

Imported service data is descriptive inventory. Do not automatically probe or connect to a service.

## FR-04: Security findings

Each finding should support:

- Unique finding ID.
- Lab ID and affected asset ID.
- Title and description.
- Finding category.
- Severity.
- Optional CVE or external reference.
- Evidence references.
- Source.
- Status.
- Recommended remediation.
- Creation and update timestamps.

Use a controlled severity scale: `informational`, `low`, `medium`, `high`, `critical`, `unknown`.

Do not infer a CVE or severity if the source data does not provide enough information.

## FR-05: Relationships

Each relationship should support:

- Unique relationship ID.
- Lab ID.
- Source node ID and target node ID.
- Relationship type.
- Evidence references.
- Evidence status.
- Description.
- Optional confidence rationale.
- Source and timestamp.

Only create a relationship when the input or a documented deterministic rule supports it. Do not invent edges to make a graph look connected.

## FR-06: Graph engine

Use NetworkX.

Implement reusable services/functions for:

- Building a graph from stored records.
- Adding and removing nodes and edges through validated operations.
- Retrieving a node and its neighbors.
- Retrieving path details.
- Finding candidate paths subject to configured limits.
- Attaching evidence references to graph elements.
- Exporting a graph representation for visualization.

Graph analysis must be deterministic and testable.

Avoid unbounded path enumeration. Set configurable maximum path length, result count and graph-size limits. Handle cycles and disconnected components safely.

## FR-07: Candidate path reasoning

The reasoning engine should:

1. Read the graph and structured findings.
2. Apply explicit path-generation rules.
3. Identify candidate sequences.
4. Record the nodes and edges in each sequence.
5. Record the findings associated with the sequence.
6. Record evidence supporting each relationship.
7. Identify missing or contradictory evidence.
8. Generate a human-readable rationale.
9. Keep the candidate status separate from validation status.

For the MVP, use transparent deterministic rules. Do not ask an LLM to invent graph edges or decide whether a route is technically feasible.

The engine should be able to explain:
- Why this candidate was generated.
- Which records contributed.
- Which assumptions were used.
- Which required facts are missing.
- What would be needed to increase confidence.

## FR-08: Scope controller

Implement a centralized policy service.

A lab policy should include:

- Explicit allowed asset IDs.
- Allowed validation categories.
- Explicit prohibited action categories.
- Whether the lab is enabled for validation.
- Optional time window or approval metadata if needed.

Every validation request must be checked by the backend policy service before execution.

The policy service must fail closed: if scope is missing, malformed, ambiguous or unavailable, the request is blocked.

The UI must not be the only enforcement layer.

## FR-09: Safe validation engine

For the MVP, implement only:

- Validation against prepared evidence.
- Read-only review of supplied configuration data.
- Deterministic checks against documented policy rules.
- Checks against imported service inventory records.

Do not implement exploit execution, remote command execution, credential operations, privilege escalation, persistence, evasion or lateral movement.

Every validation record must include:

- Validation ID.
- Lab ID.
- Target asset ID.
- Validation category.
- Requested action.
- Scope decision.
- Outcome.
- Reason.
- Evidence IDs.
- Timestamp.
- Validator/module version.

If the action is blocked, no validation operation should run.

## FR-10: Evidence tracking and audit log

Evidence records should support:

- Unique evidence ID.
- Lab ID.
- Evidence type.
- Source or filename.
- Description.
- Optional content or structured metadata.
- Collection/import timestamp.
- Hash where appropriate.
- Related asset, finding, relationship or validation IDs.

Audit records should capture:

- Event ID.
- Timestamp.
- Actor or local user identifier where available.
- Event type.
- Target record.
- Decision.
- Reason.
- Relevant metadata.

Avoid storing secrets or unnecessary sensitive information in evidence or logs.

## FR-11: AI explanation layer

AI integration is optional for the initial core engine and must be isolated behind an interface.

The AI layer may:

- Explain a candidate path using supplied structured data.
- Summarize evidence.
- Explain uncertainty and missing evidence.
- Draft impact statements.
- Suggest remediation based on supplied findings.
- Answer questions about the current lab using retrieved application data.

The AI layer must not:

- Create or modify graph edges.
- Change scope policies.
- Authorize a validation.
- Execute tools or shell commands.
- Upgrade validation status.
- Invent evidence or CVEs.
- Present speculation as confirmed fact.

Use environment variables for API credentials. Never commit `.env` or secrets. If no API key is configured, the application must continue to work with deterministic explanations and clear messaging that AI assistance is unavailable.

## FR-12: Reporting

Generate a report containing:

1. Lab details and scope.
2. Assessment date.
3. Asset and service inventory.
4. Security findings.
5. Candidate paths.
6. Path explanations.
7. Evidence references.
8. Validation results.
9. Uncertainties and limitations.
10. Potential impact.
11. Remediation recommendations.

Reports must distinguish observed facts, inferences and validated conditions. Start with Markdown or HTML export. Add PDF only after the report content is correct.

## FR-13: Application interface

A minimal development interface may be created to exercise the system. It should provide access to:

- Lab management.
- Asset inventory.
- Findings.
- Graph/path analysis.
- Validation history.
- Evidence.
- Reports.

Do not spend time on detailed UI/UX polish in this implementation phase. Keep UI code separate so a redesigned frontend can be introduced later without rewriting core services.

---

# 7. Technical Architecture

## 7.1 Recommended MVP stack

| Layer | Technology | Purpose |
|---|---|---|
| Language | Python 3.11+ | Core application |
| Initial interface | Streamlit | Minimal local development UI |
| Graph analysis | NetworkX | Graph construction and path analysis |
| Database | SQLite | Local persistence |
| ORM | SQLAlchemy | Database access |
| Data validation | Pydantic | Input and schema validation |
| Data processing | Pandas, only if useful | Tabular imports and analysis |
| Visualization | Plotly or PyVis | Basic graph display |
| Testing | Pytest | Automated tests |
| Configuration | python-dotenv / environment variables | Local configuration |
| AI | Optional LLM API adapter | Explanations and summaries |
| Version control | Git | Change tracking |

Do not add FastAPI, Neo4j, Celery, Redis, Docker or other infrastructure unless a demonstrated requirement justifies it. The first release should remain easy to run locally.

## 7.2 Architecture boundaries

Keep these layers separate:

1. **Interface layer:** Streamlit pages or components.
2. **Application/service layer:** Use cases and orchestration.
3. **Domain layer:** Models, enums and business rules.
4. **Graph layer:** NetworkX construction and analysis.
5. **Policy layer:** Scope checks and action authorization.
6. **Validation layer:** Safe read-only checks.
7. **Persistence layer:** SQLAlchemy repositories and SQLite.
8. **AI layer:** Optional LLM provider adapter.
9. **Reporting layer:** Report generation.
10. **Testing layer:** Unit, integration and end-to-end tests.

The interface must call application services. It must not contain graph algorithms or policy decisions.

---

# 8. Suggested Project Structure

Use this as the target structure. Adjust only when there is a clear technical reason.

```text
ChainBreak/
│
├── README.md
├── AGENTS.md
├── requirements.txt
├── .env.example
├── .gitignore
├── pyproject.toml
│
├── app/
│   ├── main.py
│   ├── config.py
│   └── pages/
│       ├── dashboard.py
│       ├── labs.py
│       ├── assets.py
│       ├── findings.py
│       ├── attack_paths.py
│       ├── validation.py
│       ├── evidence.py
│       └── reports.py
│
├── core/
│   ├── models/
│   │   ├── enums.py
│   │   ├── lab.py
│   │   ├── asset.py
│   │   ├── service.py
│   │   ├── finding.py
│   │   ├── relationship.py
│   │   ├── attack_path.py
│   │   ├── evidence.py
│   │   └── validation.py
│   │
│   ├── services/
│   │   ├── lab_service.py
│   │   ├── asset_service.py
│   │   ├── finding_service.py
│   │   ├── graph_service.py
│   │   ├── path_reasoning_service.py
│   │   ├── scope_service.py
│   │   ├── validation_service.py
│   │   ├── evidence_service.py
│   │   └── report_service.py
│   │
│   ├── graph/
│   │   ├── builder.py
│   │   ├── algorithms.py
│   │   └── serializers.py
│   │
│   ├── policy/
│   │   ├── scope_policy.py
│   │   └── action_registry.py
│   │
│   ├── validators/
│   │   ├── base.py
│   │   ├── prepared_evidence.py
│   │   └── configuration_checks.py
│   │
│   ├── ai/
│   │   ├── base.py
│   │   ├── provider.py
│   │   ├── prompts.py
│   │   └── deterministic_fallback.py
│   │
│   └── reporting/
│       ├── markdown_report.py
│       └── html_report.py
│
├── database/
│   ├── connection.py
│   ├── base.py
│   ├── repositories/
│   └── migrations/
│
├── schemas/
│   ├── import_schema.py
│   ├── lab_schema.py
│   ├── finding_schema.py
│   └── api_schema.py
│
├── data/
│   ├── demo_lab/
│   │   ├── lab.json
│   │   ├── assets.json
│   │   ├── findings.json
│   │   ├── services.json
│   │   ├── relationships.json
│   │   └── evidence.json
│   └── schemas/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── docs/
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── DATABASE_SCHEMA.md
│   ├── IMPLEMENTATION_STATUS.md
│   ├── DECISIONS.md
│   ├── TEST_PLAN.md
│   └── DEMO_GUIDE.md
│
├── reports/
│   └── .gitkeep
│
└── scripts/
    ├── initialize_db.py
    ├── load_demo_data.py
    └── run_checks.py
```

Do not create empty modules merely to match this tree. Create modules when implementing their functionality.

---

# 9. Database Design

Use SQLite and SQLAlchemy for the MVP.

Create these core entities:

## Laboratory
- `id`
- `name`
- `description`
- `scope_policy_json`
- `created_at`
- `updated_at`

## Asset
- `id`
- `lab_id`
- `name`
- `hostname`
- `ip_address`
- `asset_type`
- `operating_system`
- `description`
- `metadata_json`
- `created_at`
- `updated_at`

## Service
- `id`
- `asset_id`
- `name`
- `protocol`
- `port`
- `version`
- `description`
- `evidence_id`

## Finding
- `id`
- `lab_id`
- `asset_id`
- `title`
- `description`
- `category`
- `severity`
- `external_reference`
- `status`
- `remediation`
- `created_at`

## Relationship
- `id`
- `lab_id`
- `source_node_id`
- `target_node_id`
- `relationship_type`
- `evidence_status`
- `description`
- `metadata_json`
- `created_at`

## Evidence
- `id`
- `lab_id`
- `evidence_type`
- `source`
- `description`
- `content_json`
- `content_hash`
- `created_at`

## AttackPath
- `id`
- `lab_id`
- `title`
- `description`
- `path_status`
- `rationale`
- `confidence_rationale`
- `path_data_json`
- `created_at`
- `updated_at`

## Validation
- `id`
- `lab_id`
- `asset_id`
- `finding_id`
- `validation_category`
- `scope_decision`
- `result`
- `reason`
- `evidence_ids_json`
- `created_at`

## AuditLog
- `id`
- `lab_id`
- `event_type`
- `target_type`
- `target_id`
- `decision`
- `reason`
- `metadata_json`
- `created_at`

Define appropriate foreign keys, indexes, uniqueness constraints and delete behavior. Avoid storing every graph property in a large unstructured JSON blob when it should be a proper database field.

For relationships that reference different node types, define a consistent node-ID convention and validate that both endpoints exist in the same lab.

---

# 10. Graph Model and Path Analysis

## 10.1 Node types

Support at least:

- `asset`
- `service`
- `finding`
- `permission`
- `control`

Additional types can be introduced later.

Every node should have:
- Stable ID.
- Node type.
- Lab ID.
- Display label.
- Source record ID.
- Relevant metadata.

## 10.2 Edge types

Support explicitly modeled relationship types, for example:

- `hosts`
- `exposes_service`
- `affected_by`
- `connects_to`
- `has_permission`
- `depends_on`
- `evidence_supports`

Use only relationship types that have a defined meaning and a supporting source or deterministic rule.

## 10.3 Path analysis

Implement bounded graph analysis.

Requirements:
- Maximum path length configurable.
- Maximum candidate count configurable.
- Cycles handled safely.
- Disconnected nodes handled correctly.
- No fabricated edges.
- Each candidate retains ordered node and edge IDs.
- Each candidate retains supporting evidence IDs.
- Each candidate records missing evidence and assumptions.
- Candidate generation is repeatable for the same input.

Do not treat every graph route as an attack path. Use domain-specific rules to determine which node/edge sequences qualify as a candidate risk scenario. Document those rules in `docs/ARCHITECTURE.md`.

For the initial demo, use a small, transparent set of rules and test cases.

---

# 11. Demo Laboratory Dataset

Create a synthetic, clearly labelled laboratory containing three logical machines:

1. `web-server`
2. `app-server`
3. `database-server`

Include representative services and synthetic findings such as:

- An insecure web-service configuration.
- An excessive application permission.
- A database access-control weakness.

Include only relationships that are explicitly described in the synthetic dataset.

The dataset should demonstrate:
- A connected group of assets.
- At least one disconnected asset or unrelated finding.
- More than one candidate relationship sequence where appropriate.
- A finding with missing evidence.
- A scope restriction that causes a validation request to be blocked.
- A safe validation that confirms an individual configuration condition.
- A candidate path that remains unproven as a complete sequence.

The demo must not imply that a real exploit was performed. Use synthetic records and configuration evidence.

Create a demo guide that states the expected outputs and how to reproduce them.

---

# 12. Scope Enforcement and Safe Validation

This is a critical product requirement.

## 12.1 Policy design

The scope controller should accept a structured request containing:

- Lab ID.
- Target asset ID.
- Validation category.
- Requested operation.
- Relevant evidence or input record IDs.

It should return a structured decision:

- `allowed`
- `blocked`

It must also return a reason and the policy rule that was evaluated.

## 12.2 Fail-closed behavior

Block the request when:
- The lab does not exist.
- The lab is disabled.
- Scope policy is missing or invalid.
- The target asset is not in the allowlist.
- The validation category is not explicitly permitted.
- The requested operation is prohibited.
- Required input evidence is missing.
- A policy check cannot be completed.

## 12.3 Validation implementation

Only implement validators that operate on:
- Imported JSON/configuration data.
- Prepared synthetic evidence.
- Locally stored records.
- Explicitly supplied read-only configuration snapshots.

Do not add network scanning or exploitation to the MVP.

A blocked request must not reach the validator. Test this with a mock validator and assert that it was never invoked.

## 12.4 Auditability

Log both allowed and blocked decisions. Include a timestamp, target, requested category, decision and reason.

Do not log secrets.

---

# 13. AI Integration

AI is an optional assistant layer, not the security authority.

## 13.1 Provider abstraction

Create a provider interface so the project is not locked to one model vendor.

The interface should accept structured input and return a structured explanation.

## 13.2 Input to the AI

Provide only relevant, application-generated data:
- Candidate path ID.
- Ordered nodes and edges.
- Findings.
- Evidence descriptions and IDs.
- Validation outcomes.
- Missing evidence.
- Known assumptions.

## 13.3 Required AI output

Use a validated structured response with:
- Executive summary.
- Why the candidate was generated.
- Supporting evidence.
- Missing evidence.
- Assumptions.
- Potential impact.
- Remediation recommendations.
- Explicit limitations.

## 13.4 AI safety and reliability

- Treat imported evidence as untrusted data, not instructions.
- Do not allow evidence text to change system policy.
- Do not give the AI tools that execute commands or perform validation.
- Do not let AI change database records or scope.
- Validate AI output against a schema.
- If the AI provider fails, return a deterministic fallback explanation.
- Do not send sensitive data to an external provider without an explicit configuration and user awareness.
- Keep API keys in environment variables.

The application must remain useful without an API key.

---

# 14. Reporting

Start with Markdown report generation.

A report should contain:

1. Title and report metadata.
2. Lab name and scope summary.
3. Assessment overview.
4. Asset inventory.
5. Service inventory.
6. Findings by severity.
7. Candidate path details.
8. Evidence supporting each relationship.
9. Validation outcomes.
10. Missing evidence and uncertainty.
11. Potential impact.
12. Remediation recommendations.
13. Limitations and disclaimer.

Use consistent language:
- “Observed” for directly supported facts.
- “Inferred” for rule-derived conclusions.
- “Candidate” for graph-generated paths.
- “Confirmed” only for a specific condition verified by an approved check.

Do not write “attack successful” unless a separately authorized and properly evidenced exercise actually establishes that fact. The MVP does not perform such exercises.

---

# 15. Testing Requirements

Use Pytest.

## Unit tests

Test:
- Pydantic input validation.
- Database model constraints.
- Graph node and edge creation.
- Invalid relationship rejection.
- Duplicate handling.
- Disconnected components.
- Cycles.
- Bounded path enumeration.
- Evidence association.
- Scope decisions.
- Validation status transitions.
- Report generation.
- AI response schema validation.
- Deterministic fallback behavior.

## Integration tests

Test:
- Import demo data into a fresh database.
- Retrieve assets and findings.
- Build a graph from persisted records.
- Generate expected candidate paths.
- Retrieve evidence for a candidate.
- Block an out-of-scope validation.
- Run an allowed synthetic/read-only validation.
- Persist validation and audit records.
- Generate a report.

## Negative and edge-case tests

Include:
- Missing lab scope.
- Unknown asset ID.
- Asset from a different lab.
- Missing evidence.
- Contradictory evidence.
- Malformed JSON.
- Duplicate IDs.
- Empty graph.
- Cyclic graph.
- Excessively large input.
- AI provider unavailable.
- Invalid AI response.
- Database unavailable.

Tests must use synthetic data and must not contact external targets.

---

# 16. Development Phases and Acceptance Criteria

Implement in this order. Do not skip ahead to visual polish.

## Phase 0 — Workspace inspection and planning

Tasks:
- Inspect current files and Python environment.
- Confirm the available Python version.
- Create or update `AGENTS.md`.
- Create `docs/PRD.md`.
- Create `docs/ARCHITECTURE.md`.
- Create `docs/DECISIONS.md`.
- Create `docs/IMPLEMENTATION_STATUS.md`.
- Record assumptions and risks.

Acceptance:
- Architecture and responsibilities are documented.
- No unnecessary dependencies have been installed.
- Existing working files have been preserved.

## Phase 1 — Project foundation

Tasks:
- Create the agreed folder structure.
- Configure Python packaging and dependencies.
- Add `.gitignore`.
- Add `.env.example`.
- Add application configuration.
- Initialize SQLite.
- Create a minimal application entry point.
- Add a health/status check.

Acceptance:
- Application starts locally.
- Database initializes successfully.
- Configuration loads safely.
- Basic tests pass.

## Phase 2 — Models, schemas and persistence

Tasks:
- Implement domain enums and models.
- Implement SQLAlchemy entities.
- Implement Pydantic input/output schemas.
- Implement repositories.
- Add import validation.
- Add database initialization and demo-load scripts.

Acceptance:
- Demo records can be imported.
- Invalid records are rejected with clear errors.
- Records can be created, retrieved and updated.
- Tests pass on a fresh database.

## Phase 3 — Demo dataset and inventory services

Tasks:
- Create the three-machine synthetic lab.
- Add assets, services, findings, relationships and evidence.
- Implement lab, asset, service and finding services.
- Add inventory queries and detail retrieval.

Acceptance:
- Demo lab loads reproducibly.
- Inventory counts match the fixture.
- Every finding references a valid asset.
- Every relationship references valid nodes in the same lab.

## Phase 4 — Graph engine

Tasks:
- Implement graph builder.
- Implement node and edge validation.
- Add graph serializers.
- Implement bounded graph queries.
- Add graph analysis tests.

Acceptance:
- Graph reflects the database records.
- Invalid edges are rejected.
- Disconnected components remain disconnected.
- Cycles do not cause unbounded execution.
- Graph output is deterministic for the same dataset.

## Phase 5 — Candidate path reasoning

Tasks:
- Document path-generation rules.
- Implement candidate path discovery.
- Attach finding and evidence references.
- Record assumptions and missing evidence.
- Implement path explanations.
- Add deterministic tests for expected and unexpected paths.

Acceptance:
- Expected candidates are generated from the demo fixture.
- Unsupported paths are not generated.
- Every candidate has a rationale.
- A candidate is never automatically marked as validated.
- Path length and result count are bounded.

## Phase 6 — Scope controller and safe validation

Tasks:
- Implement centralized scope policy.
- Implement action registry.
- Implement fail-closed authorization.
- Implement prepared-evidence validator.
- Implement read-only configuration checks.
- Persist outcomes and audit logs.

Acceptance:
- Out-of-scope requests are blocked.
- Prohibited categories are blocked.
- A blocked request never invokes a validator.
- Allowed checks operate only on supplied local records.
- Every decision is auditable.

## Phase 7 — Evidence and reporting

Tasks:
- Complete evidence service.
- Associate evidence with findings and relationships.
- Implement Markdown report generation.
- Add report tests.
- Add a reproducible report command or interface action.

Acceptance:
- Report includes the relevant evidence and validation records.
- Uncertainty and limitations are explicit.
- No unsupported claims are generated.
- Report can be regenerated from stored data.

## Phase 8 — AI explanation adapter

Tasks:
- Define provider interface.
- Implement optional provider integration.
- Validate structured responses.
- Add deterministic fallback.
- Add tests for missing API key, provider failure and malformed output.

Acceptance:
- Core analysis works without an API key.
- AI cannot change scope or validation outcomes.
- AI explanations are traceable to supplied records.
- Unsupported claims are rejected or clearly flagged.

## Phase 9 — Minimal integration interface

Tasks:
- Build a simple Streamlit interface for exercising the backend.
- Add basic navigation for labs, assets, findings, paths, validation, evidence and reports.
- Connect every page to application services.
- Clearly label synthetic demo data.
- Show errors and empty states.

Acceptance:
- User can load the demo lab.
- User can inspect findings and paths.
- User can view evidence and validation outcomes.
- User can export a report.
- UI contains no fake results or disconnected controls.

Do not spend time on detailed UI/UX styling in this phase.

## Phase 10 — Final verification and handoff

Tasks:
- Run the complete test suite.
- Run static checks if configured.
- Test setup from a clean environment.
- Verify the demo workflow.
- Review dependency and secret handling.
- Complete technical documentation.
- Update implementation status and demo guide.

Acceptance:
- Fresh setup instructions work.
- Tests pass, or failures are explicitly documented.
- Demo can be reproduced.
- Known limitations are documented.
- No secrets or generated local databases are committed.

---

# 17. Initial Commands and Developer Experience

Support a simple local setup.

Suggested Windows PowerShell commands:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

python scripts/initialize_db.py
python scripts/load_demo_data.py

streamlit run app/main.py
```

If the project uses a different entry point, update these commands and the README accordingly.

Also provide:
- A command to run tests.
- A command to reload/reset demo data safely.
- A command to generate a report.
- A command to run any configured lint/type checks.

Never delete a user's existing database or records without an explicit confirmation and a safe backup/reset procedure.

---

# 18. Configuration and Secret Management

Create `.env.example` with placeholders only, for example:

```dotenv
APP_ENV=development
DATABASE_URL=sqlite:///./chainbreak.db
AI_PROVIDER=
AI_API_KEY=
AI_MODEL=
```

Requirements:
- `.env` must be in `.gitignore`.
- Do not hardcode API keys.
- Do not print secrets.
- Do not commit local database files or private evidence.
- Provide a useful error when optional AI configuration is missing.
- The app must run without AI credentials.

---

# 19. Quality Standards

All implementation should follow these standards:

- Use type hints for public functions.
- Use descriptive names.
- Keep functions focused.
- Avoid giant files and monolithic classes.
- Use structured logging.
- Handle errors explicitly.
- Validate untrusted imports.
- Avoid silent exception swallowing.
- Avoid unnecessary abstractions.
- Avoid duplicate business logic.
- Keep business rules out of UI files.
- Use stable IDs rather than display names as references.
- Add tests for security-sensitive behavior.
- Document non-obvious graph rules.
- Keep dependencies limited and justified.

Do not optimize prematurely. Correctness, traceability and maintainability are more important than clever algorithms.

---

# 20. Definition of Done

The initial ChainBreak implementation is complete only when all of the following are true:

- [ ] Project can be installed in a fresh Python virtual environment.
- [ ] Database initializes successfully.
- [ ] Synthetic three-machine lab imports successfully.
- [ ] Assets, services and findings can be inspected.
- [ ] Graph is constructed from stored records.
- [ ] Candidate paths are generated using documented rules.
- [ ] Each path includes supporting evidence references.
- [ ] Observed, inferred and validated states are distinguished.
- [ ] Out-of-scope validation is blocked by backend policy.
- [ ] Blocked requests do not invoke validators.
- [ ] Safe local validation outcomes are recorded.
- [ ] Audit records are persisted.
- [ ] Reports can be generated.
- [ ] AI is optional and cannot override deterministic controls.
- [ ] Minimal interface is connected to real application services.
- [ ] Automated tests pass.
- [ ] Setup and demo instructions are documented.
- [ ] Known limitations are documented.

---

# 21. Final Instruction to Antigravity

Begin by inspecting the workspace and this README.

Then:

1. Produce a short implementation plan and identify any conflicts with the current workspace.
2. Create the documentation and project foundation.
3. Implement the phases in order.
4. Test each phase before continuing.
5. Keep the application runnable throughout development.
6. Update `docs/IMPLEMENTATION_STATUS.md` after every phase.
7. Do not build elaborate UI/UX yet.
8. Do not add offensive or destructive functionality.
9. Do not fabricate completed work or successful test results.

When all phases are complete, provide:

- A summary of the architecture.
- A list of implemented features.
- The exact setup and run commands.
- The exact test command and actual test results.
- The demo workflow.
- Known limitations.
- Any remaining incomplete requirements.

**The goal is a working, evidence-first ChainBreak MVP with a reliable graph engine, candidate path reasoning, scope enforcement, safe validation, auditability and reporting. The visual redesign will be a separate next phase.**
