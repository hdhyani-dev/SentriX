"""
Lab & Inventory Page — Scope Policy Configuration, Asset & Service Directory, Findings, and Lab Import.
"""

import json
from pathlib import Path
import streamlit as st
import pandas as pd

from database.connection import get_session
from core.services.lab_service import lab_service
from core.services.asset_service import asset_service, service_service
from core.services.finding_service import finding_service


def render_lab_inventory(selected_lab_id: str | None):
    st.title("Laboratory & Inventory Management")
    st.caption("Manage Scope Authorization, Asset Inventory, Security Findings, and Lab Data Packages")

    tab_policy, tab_assets, tab_findings, tab_import = st.tabs([
        "Scope Policy",
        "Assets & Services",
        "Security Findings",
        "Lab Package & Import",
    ])

    # Tab 1: Scope Policy
    with tab_policy:
        st.subheader("Laboratory Scope & Access Control Policy")
        if not selected_lab_id:
            st.info("No active laboratory selected.")
        else:
            with get_session() as session:
                lab = lab_service.get_lab(session, selected_lab_id)
                if lab:
                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        st.markdown(f"**Laboratory Name:** {lab.name}")
                        st.markdown(f"**Internal Lab ID:** `{lab.id}`")
                        st.markdown(f"**Description:** {lab.description or 'No description provided.'}")
                    with col_p2:
                        if lab.scope_policy_json:
                            try:
                                policy = json.loads(lab.scope_policy_json)
                                st.markdown(f"**Validation Enabled:** `{'YES' if policy.get('validation_enabled') else 'NO'}`")
                                st.markdown(f"**Allowed Assets Count:** `{len(policy.get('allowed_asset_ids', []))}`")
                                st.markdown(f"**Prohibited Actions Count:** `{len(policy.get('prohibited_actions', []))}`")
                            except Exception:
                                pass

                    st.markdown("---")
                    st.markdown("#### Configured Scope Policy Specification (Fail-Closed)")
                    if lab.scope_policy_json:
                        try:
                            policy = json.loads(lab.scope_policy_json)
                            st.json(policy)
                        except Exception:
                            st.code(lab.scope_policy_json)
                    else:
                        st.warning("No scope policy JSON found. All validation requests will fail closed.")

    # Tab 2: Assets & Services
    with tab_assets:
        st.subheader("Asset & Service Directory")
        if not selected_lab_id:
            st.info("Please select a laboratory first.")
        else:
            with get_session() as session:
                assets = asset_service.list_assets_by_lab(session, selected_lab_id)
                if not assets:
                    st.warning("No assets registered in this laboratory.")
                else:
                    asset_rows = []
                    for a in assets:
                        svcs = service_service.list_services_by_asset(session, a.id)
                        svc_str = ", ".join([f"{s.name}:{s.port}" if s.port else s.name for s in svcs])
                        asset_rows.append({
                            "ID": a.id,
                            "Name": a.name,
                            "Type": a.asset_type.upper(),
                            "IP Address": a.ip_address or "N/A",
                            "Hostname": a.hostname or "N/A",
                            "Operating System": f"{a.operating_system or ''} {a.os_version or ''}".strip() or "N/A",
                            "Exposed Services": svc_str or "None",
                        })
                    st.dataframe(pd.DataFrame(asset_rows), use_container_width=True)

                    st.markdown("---")
                    st.markdown("#### Inspect Registered Services by Asset")
                    sel_asset_name = st.selectbox("Choose Asset:", [a.name for a in assets])
                    sel_asset = next(a for a in assets if a.name == sel_asset_name)

                    svcs = service_service.list_services_by_asset(session, sel_asset.id)
                    if not svcs:
                        st.write("No services registered on this host.")
                    else:
                        svc_rows = [{
                            "Service Name": s.name,
                            "Port": s.port or "N/A",
                            "Protocol": s.protocol or "TCP",
                            "Version": s.version or "Unknown",
                            "Description": s.description or "N/A",
                        } for s in svcs]
                        st.dataframe(pd.DataFrame(svc_rows), use_container_width=True)

    # Tab 3: Security Findings
    with tab_findings:
        st.subheader("Security Findings & Weaknesses")
        if not selected_lab_id:
            st.info("Please select a laboratory first.")
        else:
            with get_session() as session:
                findings = finding_service.list_findings_by_lab(session, selected_lab_id)
                assets = asset_service.list_assets_by_lab(session, selected_lab_id)
                asset_map = {a.id: a.name for a in assets}

                if not findings:
                    st.warning("No security findings recorded for this laboratory.")
                else:
                    fc1, fc2 = st.columns(2)
                    severities = ["all", "critical", "high", "medium", "low", "informational"]
                    sel_sev = fc1.selectbox("Filter by Severity", severities)
                    asset_options = ["all"] + list(asset_map.values())
                    sel_asset_filter = fc2.selectbox("Filter by Asset", asset_options)

                    filtered = findings
                    if sel_sev != "all":
                        filtered = [f for f in filtered if f.severity.lower() == sel_sev]
                    if sel_asset_filter != "all":
                        inv_map = {v: k for k, v in asset_map.items()}
                        filtered = [f for f in filtered if f.asset_id == inv_map.get(sel_asset_filter)]

                    f_rows = [{
                        "Severity": f.severity.upper(),
                        "Title": f.title,
                        "Asset": asset_map.get(f.asset_id, f.asset_id),
                        "Category": f.category,
                        "Status": f.status.upper(),
                    } for f in filtered]
                    st.dataframe(pd.DataFrame(f_rows), use_container_width=True)

                    if filtered:
                        st.markdown("---")
                        inspect_title = st.selectbox("Inspect Finding Details & Remediation:", [f.title for f in filtered])
                        sel_f = next(f for f in filtered if f.title == inspect_title)
                        st.markdown(f"**Finding:** `{sel_f.title}`")
                        st.markdown(f"**Description:** {sel_f.description or 'No description provided.'}")
                        st.markdown(f"**Remediation Guidance:** {sel_f.remediation or 'Standard security hardening recommended.'}")

    # Tab 4: Lab Package & Import
    with tab_import:
        st.subheader("Import Lab JSON Definition")
        st.caption("Upload a full lab JSON package. Enforces strict schema and referential integrity (zero dangling references).")

        uploaded = st.file_uploader("Upload Lab JSON definition", type=["json"])
        if uploaded and st.button("Import Lab Definition", use_container_width=True):
            try:
                data = json.load(uploaded)
                with get_session() as session:
                    res = lab_service.import_full_lab(session, data)
                if res.get("errors"):
                    st.error("Import rejected with the following validation errors:")
                    for err in res["errors"]:
                        st.error(f"- {err}")
                else:
                    st.success(f"Lab '{res['lab_id']}' imported successfully!")
                    st.json(res["counts"])
                    st.rerun()
            except Exception as e:
                st.error(f"Import failed: {e}")

        st.markdown("---")
        st.subheader("Reset / Reload Demo Lab")
        st.caption("Replaces or loads the pre-packaged 3-machine synthetic laboratory dataset (`full_lab.json`).")
        if st.button("Reload Synthetic Demo Lab", use_container_width=True):
            demo_path = Path(__file__).resolve().parent.parent.parent / "data" / "demo_lab" / "full_lab.json"
            if not demo_path.exists():
                st.error("Demo dataset file not found at expected location.")
            else:
                with open(demo_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                with get_session() as session:
                    res = lab_service.import_full_lab(session, data)
                if res.get("errors"):
                    st.info(f"Notice: {res['errors'][0]}")
                else:
                    st.success("Demo lab loaded successfully!")
                    st.rerun()
