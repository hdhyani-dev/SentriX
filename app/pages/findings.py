"""
Security Findings Page — View and filter findings and remediation guidance.
"""

import streamlit as st
import pandas as pd

from database.connection import get_session
from core.services.finding_service import finding_service
from core.services.asset_service import asset_service


def render_findings(lab_id: str | None):
    st.title("Security Findings")

    if not lab_id:
        st.info("Please select a lab first.")
        return

    with get_session() as session:
        findings = finding_service.list_findings_by_lab(session, lab_id)
        assets = asset_service.list_assets_by_lab(session, lab_id)
        asset_map = {a.id: a.name for a in assets}

        if not findings:
            st.warning("No security findings recorded for this laboratory.")
            return

        # Filters
        c1, c2 = st.columns(2)
        severities = ["all", "critical", "high", "medium", "low", "informational"]
        sel_sev = c1.selectbox("Filter by Severity", severities)

        asset_names = ["all"] + list(asset_map.values())
        sel_asset = c2.selectbox("Filter by Affected Asset", asset_names)

        filtered = findings
        if sel_sev != "all":
            filtered = [f for f in filtered if f.severity.lower() == sel_sev]
        if sel_asset != "all":
            inv_map = {v: k for k, v in asset_map.items()}
            filtered = [f for f in filtered if f.asset_id == inv_map.get(sel_asset)]

        # Summary table
        rows = []
        for f in filtered:
            rows.append({
                "Severity": f.severity.upper(),
                "Title": f.title,
                "Asset": asset_map.get(f.asset_id, f.asset_id),
                "Category": f.category,
                "Status": f.status,
                "Source": f.source or "N/A",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

        st.markdown("---")
        st.subheader("Finding Detail & Remediation")
        if filtered:
            sel_title = st.selectbox("Inspect Finding", [f.title for f in filtered])
            f_detail = next(f for f in filtered if f.title == sel_title)

            st.write(f"**Description:** {f_detail.description}")
            st.write(f"**Remediation:** {f_detail.remediation or 'No specific remediation recorded.'}")
            evidence_ids = finding_service.get_evidence_ids(f_detail)
            st.write(f"**Associated Evidence IDs:** {', '.join([f'`{e}`' for e in evidence_ids]) if evidence_ids else 'None (Missing evidence)'}")
