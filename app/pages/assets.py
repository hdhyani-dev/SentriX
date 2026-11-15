"""
Assets & Services Page — Inventory viewing and inspection.
"""

import streamlit as st
import pandas as pd

from database.connection import get_session
from core.services.asset_service import asset_service, service_service


def render_assets(lab_id: str | None):
    st.title("Asset & Service Inventory")

    if not lab_id:
        st.info("Please select a lab first.")
        return

    with get_session() as session:
        assets = asset_service.list_assets_by_lab(session, lab_id)
        if not assets:
            st.warning("No assets found in this laboratory.")
            return

        # Asset table
        asset_rows = []
        for a in assets:
            svcs = service_service.list_services_by_asset(session, a.id)
            svc_names = ", ".join([f"{s.name}:{s.port}" if s.port else s.name for s in svcs])
            asset_rows.append({
                "ID": a.id,
                "Name": a.name,
                "Type": a.asset_type,
                "IP Address": a.ip_address or "N/A",
                "Hostname": a.hostname or "N/A",
                "OS": f"{a.operating_system or ''} {a.os_version or ''}".strip() or "N/A",
                "Services Exposed": svc_names or "None",
            })

        df = pd.DataFrame(asset_rows)
        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.subheader("Asset Details")
        selected_asset_name = st.selectbox("Select Asset to Inspect", [a.name for a in assets])
        selected_asset = next(a for a in assets if a.name == selected_asset_name)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Description:** {selected_asset.description or 'N/A'}")
            st.markdown(f"**Internal ID:** `{selected_asset.id}`")

        with col2:
            st.markdown("#### Registered Services")
            svcs = service_service.list_services_by_asset(session, selected_asset.id)
            if not svcs:
                st.write("No services registered for this asset.")
            else:
                for s in svcs:
                    st.write(f"- **{s.name}** (Port: `{s.port}`, Protocol: `{s.protocol}`, Version: `{s.version}`)")
