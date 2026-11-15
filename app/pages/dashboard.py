"""
Dashboard Page — High-level summary of active laboratory.
"""

import streamlit as st
import pandas as pd

from database.connection import get_session
from core.services.lab_service import lab_service
from core.services.asset_service import asset_service
from core.services.finding_service import finding_service
from core.services.graph_service import graph_service
from core.services.evidence_service import evidence_service
from core.services.path_reasoning_service import path_reasoning_service


def render_dashboard(lab_id: str | None):
    st.title("Laboratory Dashboard")

    if not lab_id:
        st.info("No laboratory selected. Go to **Lab Management** to create or import a lab.")
        return

    with get_session() as session:
        lab = lab_service.get_lab(session, lab_id)
        if not lab:
            st.error("Selected laboratory not found.")
            return

        st.subheader(f"Lab: {lab.name}")
        if lab.description:
            st.caption(lab.description)

        # Metrics row
        col1, col2, col3, col4, col5 = st.columns(5)
        num_assets = asset_service.count_by_lab(session, lab_id)
        num_findings = finding_service.count_by_lab(session, lab_id)
        num_evidence = evidence_service.count_by_lab(session, lab_id)
        stored_paths = path_reasoning_service.get_candidate_paths_by_lab(session, lab_id)

        try:
            stats = graph_service.get_graph_stats(session, lab_id)
            num_nodes = stats["total_nodes"]
            num_edges = stats["total_edges"]
        except Exception:
            num_nodes, num_edges = 0, 0

        col1.metric("Assets", num_assets)
        col2.metric("Findings", num_findings)
        col3.metric("Candidate Paths", len(stored_paths))
        col4.metric("Graph Nodes/Edges", f"{num_nodes} / {num_edges}")
        col5.metric("Evidence Records", num_evidence)

        st.markdown("---")

        # Findings severity breakdown
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Findings by Severity")
            summary = finding_service.get_findings_summary(session, lab_id)
            if summary:
                df = pd.DataFrame(list(summary.items()), columns=["Severity", "Count"])
                st.dataframe(df, use_container_width=True)
            else:
                st.write("No findings recorded.")

        with c2:
            st.markdown("### Scope & Verification Notice")
            st.markdown(
                """
                - **Deterministic Analysis:** Path discovery is computed through explicit graph reachability.
                - **Scope Enforcement:** Actions outside allowed assets are automatically blocked server-side.
                - **Safe Verification:** Only prepared synthetic evidence and read-only checks are allowed.
                - **AI Assistant:** Explanations ground in structured findings; never hallucinating edges or CVEs.
                """
            )
