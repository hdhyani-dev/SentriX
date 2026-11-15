"""
Evidence Records Page — Inspect uploaded synthetic evidence artifacts.
"""

import json
import streamlit as st
import pandas as pd

from database.connection import get_session
from core.services.evidence_service import evidence_service


def render_evidence(lab_id: str | None):
    st.title("Evidence Repository")
    st.caption("Evidence records supporting findings, relationships, and validations.")

    if not lab_id:
        st.info("Please select a lab first.")
        return

    with get_session() as session:
        evidence_list = evidence_service.list_evidence_by_lab(session, lab_id)
        if not evidence_list:
            st.warning("No evidence records found in this laboratory.")
            return

        ev_rows = []
        for ev in evidence_list:
            ev_rows.append({
                "ID": ev.id,
                "Type": ev.evidence_type,
                "Source": ev.source or "N/A",
                "Description": ev.description or "N/A",
                "SHA-256 Hash": (ev.content_hash[:16] + "...") if ev.content_hash else "None",
            })

        st.dataframe(pd.DataFrame(ev_rows), use_container_width=True)

        st.markdown("---")
        st.subheader("Inspect Evidence Content")

        ev_ids = [e.id for e in evidence_list]
        selected_id = st.selectbox("Select Evidence Record", ev_ids)
        selected_ev = next(e for e in evidence_list if e.id == selected_id)

        st.markdown(f"**Evidence Type:** `{selected_ev.evidence_type}`")
        st.markdown(f"**Source File:** `{selected_ev.source}`")
        st.markdown(f"**Description:** {selected_ev.description}")
        if selected_ev.content_hash:
            st.markdown(f"**Full SHA-256 Hash:** `{selected_ev.content_hash}`")

        content = evidence_service.get_content(selected_ev)
        if content:
            st.markdown("#### Evidence Payload")
            if isinstance(content, (dict, list)):
                st.json(content)
            else:
                st.code(str(content))
        else:
            st.info("No structured content payload stored for this record.")
