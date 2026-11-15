"""
Candidate Paths Page — Graph analysis, path reasoning, and explainability.
"""

import json
import streamlit as st
import pandas as pd

from database.connection import get_session
from core.services.path_reasoning_service import path_reasoning_service
from core.services.graph_service import graph_service
from core.ai.provider import ai_service
from core.ai.base import AIExplanationRequest


def render_attack_paths(lab_id: str | None):
    st.title("Candidate Risk Paths (Graph Analysis)")

    if not lab_id:
        st.info("Please select a lab first.")
        return

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔍 Run Path Discovery"):
            with get_session() as session:
                paths = path_reasoning_service.discover_and_persist_candidate_paths(session, lab_id)
            st.success(f"Discovered and updated {len(paths)} candidate path(s)!")
            st.rerun()

    with get_session() as session:
        paths = path_reasoning_service.get_candidate_paths_by_lab(session, lab_id)
        if not paths:
            st.warning("No candidate paths found. Click 'Run Path Discovery' to analyze the graph.")
            return

        # Display table of paths
        path_rows = []
        for p in paths:
            path_rows.append({
                "Status": p.path_status.upper(),
                "Title": p.title,
                "Confidence / Uncertainty": p.confidence_rationale[:80] + "..." if p.confidence_rationale else "N/A",
            })
        st.dataframe(pd.DataFrame(path_rows), use_container_width=True)

        st.markdown("---")
        st.subheader("Path Inspection & Explainability")

        path_titles = [p.title for p in paths]
        selected_title = st.selectbox("Select Candidate Path to Examine", path_titles)
        selected_path = next(p for p in paths if p.title == selected_title)

        st.markdown(f"### `{selected_path.title}`")
        st.write(f"**Current Path Status:** `{selected_path.path_status}`")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Path Rationale")
            st.markdown(selected_path.rationale or "No rationale recorded.")

        with c2:
            st.markdown("#### Evidence & Confidence Evaluation")
            st.markdown(selected_path.confidence_rationale or "No confidence evaluation recorded.")

        # Show raw sequence data
        if selected_path.path_data_json:
            try:
                data = json.loads(selected_path.path_data_json)
                st.markdown("#### Traversed Nodes Sequence")
                st.code(" ➔ ".join(data.get("nodes", [])))
            except Exception:
                pass

        st.markdown("---")
        st.markdown("#### 🤖 AI-Assisted Path Explanation")
        st.caption("Requests an explanation from the AI layer (or deterministic fallback if no API key is set).")

        if st.button("Generate AI Explanation"):
            data = {}
            if selected_path.path_data_json:
                try:
                    data = json.loads(selected_path.path_data_json)
                except Exception:
                    pass

            req = AIExplanationRequest(
                path_id=selected_path.id,
                title=selected_path.title,
                nodes=data.get("nodes", []),
                edges=data.get("edges", []),
                findings=[{"title": f} for f in data.get("findings", [])],
                evidence_descriptions=[f"Evidence ID: {eid}" for eid in data.get("evidence_ids", [])],
                validation_outcomes=[],
                missing_evidence=data.get("missing_evidence", []),
                assumptions=data.get("assumptions", []),
            )
            explanation = ai_service.explain_path(req)

            st.info(f"**Provider Used:** `{explanation.provider_used}`")
            st.markdown(f"**Executive Summary:** {explanation.executive_summary}")
            st.markdown(f"**Path Rationale:**\n{explanation.path_rationale}")
            st.markdown(f"**Potential Impact:** {explanation.potential_impact}")
            st.markdown("**Remediation Recommendations:**")
            for r in explanation.remediation_recommendations:
                st.write(f"- {r}")
            st.caption(f"**Limitations Notice:** {explanation.limitations}")
