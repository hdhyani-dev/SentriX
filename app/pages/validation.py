"""
Safe Validation Page — Execute read-only checks, review scope controller decisions.
"""

import streamlit as st
import pandas as pd

from database.connection import get_session
from core.services.asset_service import asset_service
from core.services.finding_service import finding_service
from core.services.validation_service import validation_service
from core.services.path_reasoning_service import path_reasoning_service
from core.policy.action_registry import PERMITTED_CATEGORIES, PROHIBITED_ACTIONS


def render_validation(lab_id: str | None):
    st.title("Safe Validation & Scope Enforcement")
    st.caption("Executes read-only synthetic evidence and configuration checks under fail-closed scope rules.")

    if not lab_id:
        st.info("Please select a lab first.")
        return

    with get_session() as session:
        assets = asset_service.list_assets_by_lab(session, lab_id)
        findings = finding_service.list_findings_by_lab(session, lab_id)
        paths = path_reasoning_service.get_candidate_paths_by_lab(session, lab_id)

        asset_map = {a.name: a.id for a in assets}
        finding_map = {f.title: f.id for f in findings}
        path_map = {p.title: p.id for p in paths}

        st.subheader("1. Execute Validation Request")

        col1, col2 = st.columns(2)
        with col1:
            sel_asset_name = st.selectbox("Target Asset", list(asset_map.keys()))
            target_asset_id = asset_map[sel_asset_name]

            categories = list(PERMITTED_CATEGORIES.keys()) + ["prohibited_test_category"]
            sel_category = st.selectbox("Validation Category", categories)

        with col2:
            # Let user choose recognized safe action or a prohibited test action
            if sel_category in PERMITTED_CATEGORIES:
                actions = list(PERMITTED_CATEGORIES[sel_category]) + ["exploit_execution (prohibited test)"]
            else:
                actions = ["exploit_execution", "credential_extraction"]
            sel_action = st.selectbox("Requested Action", actions)
            # Strip label note if test action
            clean_action = sel_action.split(" ")[0]

            sel_finding_name = st.selectbox("Associated Finding (Optional)", ["None"] + list(finding_map.keys()))
            finding_id = finding_map[sel_finding_name] if sel_finding_name != "None" else None

        sel_path_name = st.selectbox("Associated Candidate Path (Optional)", ["None"] + list(path_map.keys()))
        attack_path_id = path_map[sel_path_name] if sel_path_name != "None" else None

        if st.button("Submit Validation Request"):
            record = validation_service.execute_validation(
                session=session,
                lab_id=lab_id,
                target_asset_id=target_asset_id,
                validation_category=sel_category,
                requested_action=clean_action,
                finding_id=finding_id,
                attack_path_id=attack_path_id,
            )

            if record.scope_decision == "allowed":
                st.success(f"Scope Check: ALLOWED | Result: {record.result.upper()}")
                st.write(f"**Outcome Detail:** {record.reason}")
            else:
                st.error(f"Scope Check: BLOCKED | Result: {record.result.upper()}")
                st.write(f"**Reason:** {record.reason}")

        st.markdown("---")
        st.subheader("2. Validation History")

        validations = validation_service.list_validations_by_lab(session, lab_id)
        if not validations:
            st.write("No validations have been recorded yet.")
        else:
            val_rows = []
            for v in reversed(validations):
                val_rows.append({
                    "Timestamp": v.created_at.strftime("%Y-%m-%d %H:%M:%S") if v.created_at else "N/A",
                    "Asset": v.asset_id,
                    "Action": v.requested_action,
                    "Scope Decision": v.scope_decision.upper(),
                    "Result": v.result.upper(),
                    "Reason": v.reason or "N/A",
                })
            st.dataframe(pd.DataFrame(val_rows), use_container_width=True)
