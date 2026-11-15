"""
Overview Page — Executive KPIs, risk posture distribution, and scope authorization summary.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from database.connection import get_session
from core.services.lab_service import lab_service
from core.services.asset_service import asset_service
from core.services.finding_service import finding_service
from core.services.graph_service import graph_service
from core.services.evidence_service import evidence_service
from core.services.path_reasoning_service import path_reasoning_service
from core.services.validation_service import validation_service


def render_overview(lab_id: str | None):
    st.title("Operation Overview")
    st.caption("AI-Assisted Cybersecurity Risk-Path Analysis & Posture Monitoring")

    # Synthetic simulation banner
    st.info(
        "🛡️ **Synthetic Lab Environment**: SentriX operates read-only against authorized lab topologies. "
        "No offensive actions, exploits, or intrusive network scanners are permitted or executed."
    )

    if not lab_id:
        st.warning("No laboratory selected. Go to **Lab & Inventory** to register or import a lab.")
        return

    with get_session() as session:
        lab = lab_service.get_lab(session, lab_id)
        if not lab:
            st.error("Selected laboratory record was not found.")
            return

        # 1. Top Metrics Bar
        assets_count = asset_service.count_by_lab(session, lab_id)
        findings_count = finding_service.count_by_lab(session, lab_id)
        evidence_count = evidence_service.count_by_lab(session, lab_id)
        paths = path_reasoning_service.get_candidate_paths_by_lab(session, lab_id)
        validations = validation_service.list_validations_by_lab(session, lab_id)

        try:
            stats = graph_service.get_graph_stats(session, lab_id)
            total_nodes = stats.get("total_nodes", 0)
            total_edges = stats.get("total_edges", 0)
        except Exception:
            total_nodes, total_edges = 0, 0

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Assets", assets_count)
        c2.metric("Open Findings", findings_count)
        c3.metric("Candidate Paths", len(paths))
        c4.metric("Validations Run", len(validations))
        c5.metric("Graph Elements", f"{total_nodes} nodes / {total_edges} edges")

        st.markdown("---")

        # 2. Risk Distribution & Status Charts
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.subheader("Security Findings by Severity")
            summary = finding_service.get_findings_summary(session, lab_id)
            if summary:
                sev_order = ["critical", "high", "medium", "low", "informational", "unknown"]
                color_map = {
                    "critical": "#DC2626",
                    "high": "#EA580C",
                    "medium": "#F59E0B",
                    "low": "#3B82F6",
                    "informational": "#10B981",
                    "unknown": "#6B7280",
                }
                data_rows = [{"Severity": k.capitalize(), "Count": v, "Color": color_map.get(k.lower(), "#6B7280")}
                             for k, v in summary.items()]
                df_sev = pd.DataFrame(data_rows)

                fig_donut = px.pie(
                    df_sev,
                    names="Severity",
                    values="Count",
                    color="Severity",
                    color_discrete_map={row["Severity"]: row["Color"] for row in data_rows},
                    hole=0.55,
                )
                fig_donut.update_layout(
                    margin=dict(t=20, b=20, l=20, r=20),
                    height=300,
                    showlegend=True,
                )
                st.plotly_chart(fig_donut, use_container_width=True)
            else:
                st.info("No security findings recorded for this laboratory.")

        with col_chart2:
            st.subheader("Candidate Path Verification Status")
            if paths:
                status_counts: dict[str, int] = {}
                for p in paths:
                    st_val = p.path_status.replace("_", " ").capitalize()
                    status_counts[st_val] = status_counts.get(st_val, 0) + 1

                df_status = pd.DataFrame(list(status_counts.items()), columns=["Status", "Paths"])
                fig_bar = px.bar(
                    df_status,
                    x="Status",
                    y="Paths",
                    color="Status",
                    color_discrete_sequence=["#F59E0B", "#10B981", "#3B82F6", "#EF4444"],
                )
                fig_bar.update_layout(
                    margin=dict(t=20, b=20, l=20, r=20),
                    height=300,
                    showlegend=False,
                    xaxis_title="",
                    yaxis_title="Path Count",
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No candidate paths discovered yet. Open **Path Explorer** to run discovery.")

        st.markdown("---")

        # 3. Laboratory Posture & Operational Principles
        st.subheader("Operational Scope & Epistemological Boundaries")
        col_info1, col_info2 = st.columns(2)

        with col_info1:
            st.markdown(
                """
                - **Deterministic Path Reasoning:** Graph exploration follows explicit reachability algorithms (`NetworkX`).
                - **Multi-Edge Preservation:** Parallel relationships (e.g., service exposure alongside network connection) are preserved without edge overwriting.
                - **Fail-Closed Authorization:** Every validation check is audited and blocked if out-of-scope.
                """
            )

        with col_info2:
            st.markdown(
                """
                - **Evidence First:** Paths distinguish empirical evidence (`observed`) from heuristic rules (`inferred`).
                - **Uncertainty Tracking:** Missing evidence is explicitly surfaced to prevent false confidence.
                - **Safe Verification:** Only configuration checks and static evidence audits are executed.
                """
            )
