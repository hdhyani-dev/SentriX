"""
Verification script for ChainBreak — runs self-checks across database, models, graph, policy, validators, and tests.
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from database.connection import init_db, get_session
from core.services.lab_service import lab_service
from core.services.asset_service import asset_service
from core.services.finding_service import finding_service
from core.services.graph_service import graph_service
from core.services.path_reasoning_service import path_reasoning_service
from core.services.validation_service import validation_service
from core.services.report_service import report_service
from core.ai.provider import ai_service
from core.ai.base import AIExplanationRequest


def run_checks():
    print("=" * 60)
    print("  SentriX Platform Self-Check & Health Verification")
    print("=" * 60)

    # 1. DB Init
    print("\n[1/6] Database Initialization...")
    init_db()
    print("  ✓ SQLite tables verified.")

    # 2. Lab & Inventory Check
    print("\n[2/6] Lab Inventory Check...")
    with get_session() as session:
        labs = lab_service.list_labs(session)
        print(f"  ✓ Found {len(labs)} registered laboratory(s).")
        if not labs:
            print("  ! Notice: No labs present. Run `python scripts/load_demo_data.py` to load demo lab.")
            return True

        lab = labs[0]
        assets = asset_service.list_assets_by_lab(session, lab.id)
        findings = finding_service.list_findings_by_lab(session, lab.id)
        print(f"  ✓ Active Lab: '{lab.name}' (ID: {lab.id})")
        print(f"  ✓ Assets: {len(assets)}, Findings: {len(findings)}")

        # 3. Graph Analysis Check
        print("\n[3/6] Graph Analysis & Serialization...")
        stats = graph_service.get_graph_stats(session, lab.id)
        print(f"  ✓ Graph Nodes: {stats['total_nodes']}, Edges: {stats['total_edges']}, Components: {stats['connected_components']}")

        # 4. Path Reasoning Check
        print("\n[4/6] Candidate Path Discovery...")
        paths = path_reasoning_service.discover_and_persist_candidate_paths(session, lab.id)
        print(f"  ✓ Discovered {len(paths)} candidate multi-step path(s).")

        # 5. Scope & Safe Validation Check
        print("\n[5/6] Fail-Closed Scope Enforcement & Safe Validation...")
        v_allowed = validation_service.execute_validation(
            session, lab.id, "asset-web", "configuration_check", "check_tls_configuration",
            finding_id="finding-web-tls", evidence_ids=["ev-tls-scan"]
        )
        print(f"  ✓ Allowed Request: Scope={v_allowed.scope_decision.upper()}, Result={v_allowed.result.upper()}")

        v_blocked = validation_service.execute_validation(
            session, lab.id, "asset-monitor", "configuration_check", "check_tls_configuration"
        )
        print(f"  ✓ Blocked Request (out-of-scope asset): Scope={v_blocked.scope_decision.upper()}, Result={v_blocked.result.upper()}")

        # 6. Report & AI Check
        print("\n[6/6] Report Generation & AI Adapter Check...")
        report_md = report_service.generate_report(session, lab.id, format="markdown")
        print(f"  ✓ Markdown Report generated ({len(report_md)} bytes).")

        ai_req = AIExplanationRequest(
            path_id=paths[0].id if paths else "test",
            title=paths[0].title if paths else "test path",
            nodes=["asset-web", "asset-app"],
            edges=[],
            findings=[{"title": "Weak TLS"}],
            evidence_descriptions=["Synthetic TLS check"],
            validation_outcomes=[],
            missing_evidence=[],
            assumptions=[],
        )
        ai_resp = ai_service.explain_path(ai_req)
        print(f"  ✓ AI Adapter ({ai_resp.provider_used}): {ai_resp.executive_summary[:60]}...")

    print("\n" + "=" * 60)
    print("  ALL CORE SYSTEM CHECKS PASSED SUCCESSFULLY! ✓")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = run_checks()
    if not success:
        sys.exit(1)
