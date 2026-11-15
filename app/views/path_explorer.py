"""
Path Explorer Page — Interactive Plotly Graph, Candidate Path Selection, and Step-by-Step Inspector.
Primary hero interface for SentriX risk-path exploration.
"""

import json
import streamlit as st
import pandas as pd

from database.connection import get_session
from core.services.path_reasoning_service import path_reasoning_service
from core.services.graph_service import graph_service
from core.models.enums import PathStatus


def render_path_explorer(lab_id: str | None):
    st.title("Attack Path Explorer")
    st.caption("Visual Graph Analysis, Multi-Step Risk Reasoning & Epistemic Uncertainty Tracking")

    # Simulation disclaimer
    st.info(
        "🛡️ **Simulation Mode**: Visualizing theoretical multi-step risk paths derived from graph topology. "
        "A candidate path models architectural risk and does not constitute proof of active exploitability."
    )

    if not lab_id:
        st.warning("Please select a laboratory in the sidebar to visualize topology and candidate risk paths.")
        return

    # Action bar
    top_col1, top_col2 = st.columns([3, 1])
    with top_col2:
        if st.button("Run Path Discovery", use_container_width=True, help="Compute bounded candidate paths for the lab"):
            with get_session() as session:
                discovered = path_reasoning_service.discover_and_persist_candidate_paths(session, lab_id)
            st.success(f"Discovered and updated {len(discovered)} candidate risk path(s)!")
            st.rerun()

    with get_session() as session:
        paths = path_reasoning_service.get_candidate_paths_by_lab(session, lab_id)

        # 1. Path Selection & Controls
        selected_path_obj = None
        highlight_nodes = None

        if paths:
            path_options = {
                f"[{p.path_status.upper()}] {p.title}": p.id
                for p in paths
            }
            selected_path_label = st.selectbox(
                "Select Candidate Risk Path to Inspect & Highlight:",
                list(path_options.keys()),
                index=0,
            )
            selected_path_id = path_options[selected_path_label]
            selected_path_obj = next((p for p in paths if p.id == selected_path_id), None)

            if selected_path_obj and selected_path_obj.path_data_json:
                try:
                    pdata = json.loads(selected_path_obj.path_data_json)
                    highlight_nodes = pdata.get("nodes", [])
                except Exception:
                    highlight_nodes = []
        else:
            st.info("No candidate paths discovered yet. Click **'Run Path Discovery'** above to evaluate the graph.")

        # 2. Hero Interactive Plotly Graph
        st.subheader("Laboratory Graph Topology")
        try:
            fig = graph_service.get_plotly_figure(session, lab_id, highlight_path=highlight_nodes)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to render graph visualization: {e}")

        # 3. Path Details & Step-by-Step Inspector
        if selected_path_obj:
            st.markdown("---")
            st.subheader(f"Path Analysis: {selected_path_obj.title}")

            badge_col1, badge_col2, badge_col3 = st.columns(3)
            status_colors = {
                PathStatus.CANDIDATE.value: "orange",
                PathStatus.PARTIALLY_SUPPORTED.value: "blue",
                PathStatus.SUPPORTED.value: "green",
                PathStatus.BLOCKED.value: "red",
                PathStatus.INCONCLUSIVE.value: "gray",
            }
            badge_color = status_colors.get(selected_path_obj.path_status, "gray")

            badge_col1.markdown(f"**Verification Status:** :{badge_color}[{selected_path_obj.path_status.upper()}]")
            badge_col2.markdown(f"**Path ID:** `...{selected_path_obj.id[-12:]}`")
            badge_col3.markdown(f"**Traversed Steps:** {len(highlight_nodes) - 1 if highlight_nodes else 'N/A'} hops")

            col_inspector, col_steps = st.columns([1, 1])

            # Parse path data
            path_data = {}
            if selected_path_obj.path_data_json:
                try:
                    path_data = json.loads(selected_path_obj.path_data_json)
                except Exception:
                    pass

            with col_inspector:
                st.markdown("#### Path Rationale & Narrative")
                st.markdown(selected_path_obj.rationale or "No deterministic rationale recorded.")

                st.markdown("#### Confidence & Epistemic Uncertainty")
                st.info(selected_path_obj.confidence_rationale or "Standard structural analysis.")

                missing_ev = path_data.get("missing_evidence", [])
                if missing_ev:
                    st.warning(f"⚠️ **Missing Empirical Evidence:** {len(missing_ev)} relationship(s) lack direct proof.")
                    for m in missing_ev:
                        st.caption(f"- Edge: `{m.get('edge')}` ({m.get('relationship_type')})")

                assumptions = path_data.get("assumptions", [])
                if assumptions:
                    st.caption(f"ℹ️ **Inferred Assumptions:** {len(assumptions)} step(s) rely on heuristic inference.")

            with col_steps:
                st.markdown("#### Step-by-Step Traversal")
                raw_edges = path_data.get("edges", [])
                if raw_edges:
                    step_rows = []
                    for idx, e in enumerate(raw_edges, 1):
                        step_rows.append({
                            "Hop": f"Step {idx}",
                            "From": e.get("source"),
                            "To": e.get("target"),
                            "Type": e.get("relationship_type"),
                            "Evidence Status": (e.get("evidence_status") or "observed").upper(),
                        })
                    st.dataframe(pd.DataFrame(step_rows), use_container_width=True)
                else:
                    st.write("No edge steps parsed.")

                findings = path_data.get("findings", [])
                if findings:
                    st.markdown("#### Associated Security Findings")
                    for f in findings:
                        st.markdown(f"- 🔴 `{f}`")

                st.markdown("---")
                st.caption("To validate this path under fail-closed authorization, go to **Evidence & Validation**.")
