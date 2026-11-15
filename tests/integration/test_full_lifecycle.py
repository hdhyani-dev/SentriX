"""
Full integration test: import demo data -> graph -> path reasoning -> scope enforcement -> validation -> report.
"""

import json
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.base import Base
from core.services.lab_service import lab_service
from core.services.graph_service import graph_service
from core.services.path_reasoning_service import path_reasoning_service
from core.services.validation_service import validation_service
from core.services.report_service import report_service
from core.ai.provider import ai_service
from core.ai.base import AIExplanationRequest
from core.models.enums import ScopeDecision, ValidationResult, PathStatus


@pytest.fixture
def fresh_session():
    """Create a temporary in-memory SQLite database session for isolated testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_full_chainbreak_workflow(fresh_session):
    session = fresh_session

    # 1. Load demo JSON
    demo_path = Path(__file__).resolve().parent.parent.parent / "data" / "demo_lab" / "full_lab.json"
    with open(demo_path, "r", encoding="utf-8") as f:
        demo_data = json.load(f)

    import_result = lab_service.import_full_lab(session, demo_data)
    assert import_result["errors"] == []
    assert import_result["counts"]["assets"] == 4
    assert import_result["counts"]["findings"] == 7

    lab_id = "lab-001"

    # 2. Build graph & verify stats
    stats = graph_service.get_graph_stats(session, lab_id)
    assert stats["total_nodes"] > 0
    assert stats["total_edges"] > 0
    # There should be at least one disconnected node (monitoring-station)
    assert stats["disconnected_nodes"] >= 1

    # 3. Path reasoning
    paths = path_reasoning_service.discover_and_persist_candidate_paths(session, lab_id)
    assert len(paths) >= 1
    # Paths must be candidate status initially, never claimed as proven attacks
    for p in paths:
        assert p.path_status == PathStatus.CANDIDATE.value

    # 4. Safe validation - Allowed check
    val_allowed = validation_service.execute_validation(
        session, lab_id, "asset-web", "configuration_check", "check_tls_configuration",
        finding_id="finding-web-tls", evidence_ids=["ev-tls-scan"], attack_path_id=paths[0].id
    )
    assert val_allowed.scope_decision == ScopeDecision.ALLOWED.value
    assert val_allowed.result == ValidationResult.CONFIRMED.value
    # Attack path status should now transition to partially_supported
    session.refresh(paths[0])
    assert paths[0].path_status == PathStatus.PARTIALLY_SUPPORTED.value

    # 5. Safe validation - Blocked check (asset out of scope)
    val_blocked = validation_service.execute_validation(
        session, lab_id, "asset-monitor", "configuration_check", "check_tls_configuration"
    )
    assert val_blocked.scope_decision == ScopeDecision.BLOCKED.value
    assert val_blocked.result == ValidationResult.BLOCKED.value

    # 6. Report generation
    md_report = report_service.generate_report(session, lab_id, format="markdown")
    assert "# ChainBreak Security Risk-Path Assessment Report" in md_report
    assert "Weak TLS configuration confirmed" in md_report

    html_report = report_service.generate_report(session, lab_id, format="html")
    assert "<!DOCTYPE html>" in html_report

    # 7. AI explanation layer
    ai_req = AIExplanationRequest(
        path_id=paths[0].id,
        title=paths[0].title,
        nodes=["asset-web", "asset-app", "asset-db"],
        edges=[],
        findings=[{"title": "Weak TLS", "remediation": "Upgrade TLS"}],
        evidence_descriptions=["Synthetic TLS audit"],
        validation_outcomes=[],
        missing_evidence=[],
        assumptions=[],
    )
    ai_resp = ai_service.explain_path(ai_req)
    assert ai_resp.executive_summary != ""
    assert len(ai_resp.remediation_recommendations) >= 1
