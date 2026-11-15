"""
Evidence & Validation Page — Safe Read-Only Verification, Scope Enforcement, and Evidence Artifacts.
"""

import json
import streamlit as st
import pandas as pd

from database.connection import get_session
from core.services.asset_service import asset_service
from core.services.finding_service import finding_service
from core.services.evidence_service import evidence_service
from core.services.validation_service import validation_service
from core.services.path_reasoning_service import path_reasoning_service
from core.policy.action_registry import PERMITTED_CATEGORIES
from core.models.evidence import Evidence


def render_evidence_validation(lab_id: str | None):
    st.title("Evidence & Safe Validation")
    st.caption("Execute Read-Only Configuration Checks & Inspect Supporting Synthetic Evidence Records")

    # Simulation disclaimer
    st.info(
        "🛡️ **Fail-Closed Scope Policy**: All operations execute strictly read-only against pre-collected snapshots. "
        "Any request targeting out-of-scope assets or unpermitted categories is blocked server-side."
    )

    if not lab_id:
        st.warning("Please select an active laboratory in the sidebar.")
        return

    tab_runner, tab_evidence, tab_history = st.tabs([
        "Safe Validation Console",
        "Evidence Artifacts",
        "Scope & Audit Log",
    ])

    # Tab 1: Safe Validation Console
    with tab_runner:
        st.subheader("Execute Safe Validation Check")
        st.caption("Submit a read-only verification request evaluated by the server-side Scope Controller.")

        with get_session() as session:
            assets = asset_service.list_assets_by_lab(session, lab_id)
            findings = finding_service.list_findings_by_lab(session, lab_id)
            paths = path_reasoning_service.get_candidate_paths_by_lab(session, lab_id)

            if not assets:
                st.warning("No assets registered for this laboratory.")
            else:
                asset_map = {a.name: a.id for a in assets}
                path_map = {f"[{p.path_status.upper()}] {p.title}": p.id for p in paths}

                c_form1, c_form2 = st.columns(2)
                with c_form1:
                    sel_asset_name = st.selectbox("Target Asset in Scope:", list(asset_map.keys()))
                    target_asset_id = asset_map[sel_asset_name]

                    # Filter findings to this asset
                    asset_findings = [f for f in findings if f.asset_id == target_asset_id]
                    finding_options = {"None (General Asset Check)": None}
                    for af in asset_findings:
                        finding_options[f"[{af.severity.upper()}] {af.title}"] = af.id
                    sel_finding_label = st.selectbox("Associated Finding (Optional):", list(finding_options.keys()))
                    selected_finding_id = finding_options[sel_finding_label]

                with c_form2:
                    # Permitted categories from Action Registry
                    categories = list(PERMITTED_CATEGORIES.keys()) + ["prohibited_exploit_test"]
                    sel_category = st.selectbox("Validation Category:", categories)

                    # Dynamically filter permitted actions based on selected category
                    if sel_category in PERMITTED_CATEGORIES:
                        valid_actions = list(PERMITTED_CATEGORIES[sel_category]) + ["exploit_execution (prohibited)"]
                    else:
                        valid_actions = ["exploit_execution", "credential_extraction"]
                    sel_action_label = st.selectbox("Requested Safe Action:", valid_actions)
                    clean_action = sel_action_label.split(" ")[0]

                path_options_with_none = {"None (Independent Check)": None}
                path_options_with_none.update(path_map)
                sel_path_label = st.selectbox("Link to Candidate Risk Path (Optional):", list(path_options_with_none.keys()))
                selected_path_id = path_options_with_none[sel_path_label]

                if st.button("Execute Validation Check", use_container_width=True):
                    record = validation_service.execute_validation(
                        session=session,
                        lab_id=lab_id,
                        target_asset_id=target_asset_id,
                        validation_category=sel_category,
                        requested_action=clean_action,
                        finding_id=selected_finding_id,
                        attack_path_id=selected_path_id,
                    )

                    st.markdown("---")
                    st.subheader("Validation Outcome & Scope Decision")

                    res_col1, res_col2 = st.columns(2)
                    with res_col1:
                        if record.scope_decision == "allowed":
                            st.success(f"**Scope Decision:** `ALLOWED`")
                        else:
                            st.error(f"**Scope Decision:** `BLOCKED`")
                        st.write(f"**Action Requested:** `{record.requested_action}`")
                        st.write(f"**Target Asset:** `{record.asset_id}`")

                    with res_col2:
                        res_badge = record.result.upper()
                        if record.result == "confirmed":
                            st.success(f"**Validation Result:** `{res_badge}`")
                        elif record.result == "blocked":
                            st.error(f"**Validation Result:** `{res_badge}`")
                        else:
                            st.warning(f"**Validation Result:** `{res_badge}`")
                        st.write(f"**Reason:** {record.reason}")
                        st.caption(f"**Validator Module:** `{record.validator_module or 'scope_policy_guard'}`")

                    if selected_path_id:
                        st.info(f"Target candidate path status evaluated against validation result.")

    # Tab 2: Evidence Artifacts
    with tab_evidence:
        st.subheader("Verifiable Synthetic Evidence Records")
        st.caption("Evidence records supporting findings, topological relationships, and configuration assertions.")

        with get_session() as session:
            evidence_list = evidence_service.list_evidence_by_lab(session, lab_id)
            if not evidence_list:
                st.warning("No evidence artifacts recorded for this laboratory.")
            else:
                ev_rows = [{
                    "ID": ev.id,
                    "Type": ev.evidence_type,
                    "Source File": ev.source or "N/A",
                    "Description": ev.description or "N/A",
                    "SHA-256 Hash": (ev.content_hash[:16] + "...") if ev.content_hash else "None",
                } for ev in evidence_list]
                st.dataframe(pd.DataFrame(ev_rows), use_container_width=True)

                st.markdown("---")
                st.markdown("#### Inspect Evidence Content & Verify Cryptographic Integrity")
                sel_ev_id = st.selectbox("Select Evidence Record:", [e.id for e in evidence_list])
                sel_ev = next(e for e in evidence_list if e.id == sel_ev_id)

                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    st.markdown(f"**Type:** `{sel_ev.evidence_type}`")
                    st.markdown(f"**Source Artifact:** `{sel_ev.source}`")
                    st.markdown(f"**Description:** {sel_ev.description}")
                    if sel_ev.content_hash:
                        st.markdown(f"**Stored SHA-256:** `{sel_ev.content_hash}`")
                with col_e2:
                    if sel_ev.content_json and sel_ev.content_hash:
                        computed = Evidence.compute_hash(sel_ev.content_json)
                        if computed == sel_ev.content_hash:
                            st.success("Integrity Verified: Content SHA-256 matches stored checksum.")
                        else:
                            st.error("Integrity Warning: Computed checksum differs from stored hash!")

                content = evidence_service.get_content(sel_ev)
                if content:
                    st.markdown("#### Evidence Payload")
                    if isinstance(content, (dict, list)):
                        st.json(content)
                    else:
                        st.code(str(content))

    # Tab 3: Scope & Audit Log
    with tab_history:
        st.subheader("Historical Validation & Scope Audit Log")
        st.caption("Immutable append-only record of all scope checks, policy decisions, and validation executions.")

        with get_session() as session:
            validations = validation_service.list_validations_by_lab(session, lab_id)
            if not validations:
                st.info("No validation operations executed in this laboratory yet.")
            else:
                v_rows = []
                for v in reversed(validations):
                    v_rows.append({
                        "Validation ID": v.id[:8] + "...",
                        "Asset": v.asset_id,
                        "Category": v.validation_category,
                        "Action": v.requested_action,
                        "Scope Decision": v.scope_decision.upper(),
                        "Result": v.result.upper(),
                        "Reason": v.reason[:70] + "..." if v.reason and len(v.reason) > 70 else (v.reason or "N/A"),
                        "Timestamp": v.created_at.strftime("%Y-%m-%d %H:%M:%S UTC") if getattr(v, "created_at", None) else "N/A",
                    })
                st.dataframe(pd.DataFrame(v_rows), use_container_width=True)
