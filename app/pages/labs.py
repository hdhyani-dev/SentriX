"""
Lab Management Page — Import JSON, view scope policy, list labs.
"""

import json
from pathlib import Path
import streamlit as st

from database.connection import get_session
from core.services.lab_service import lab_service


def render_labs(selected_lab_id: str | None):
    st.title("Laboratory Management")

    tab1, tab2, tab3 = st.tabs(["Active Lab Scope", "Import Lab JSON", "Load Demo Lab"])

    with tab1:
        if not selected_lab_id:
            st.info("No active lab selected.")
        else:
            with get_session() as session:
                lab = lab_service.get_lab(session, selected_lab_id)
                if lab:
                    st.write(f"**Lab Name:** {lab.name}")
                    st.write(f"**Lab ID:** `{lab.id}`")
                    st.write(f"**Description:** {lab.description}")
                    st.markdown("#### Configured Scope Policy")
                    if lab.scope_policy_json:
                        try:
                            policy = json.loads(lab.scope_policy_json)
                            st.json(policy)
                        except Exception:
                            st.code(lab.scope_policy_json)
                    else:
                        st.warning("No scope policy configured. All validation will fail closed.")

    with tab2:
        st.markdown("### Upload Lab JSON Package")
        uploaded_file = st.file_uploader("Upload JSON definition", type=["json"])
        if uploaded_file and st.button("Import Uploaded Lab"):
            try:
                data = json.load(uploaded_file)
                with get_session() as session:
                    res = lab_service.import_full_lab(session, data)
                if res.get("errors"):
                    for err in res["errors"]:
                        st.error(err)
                else:
                    st.success(f"Lab '{res['lab_id']}' imported successfully!")
                    st.json(res["counts"])
                    st.rerun()
            except Exception as e:
                st.error(f"Import failed: {e}")

    with tab3:
        st.markdown("### Reset / Load Demo Lab")
        st.write("Loads the pre-packaged 3-machine synthetic laboratory dataset (`full_lab.json`).")
        if st.button("Reload Synthetic Demo Lab"):
            demo_path = Path(__file__).resolve().parent.parent.parent / "data" / "demo_lab" / "full_lab.json"
            if demo_path.exists():
                with open(demo_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                with get_session() as session:
                    # Delete existing demo lab if present to reset cleanly
                    lab_service.delete_lab(session, data["lab"]["id"])
                    res = lab_service.import_full_lab(session, data)
                st.success("Demo lab reloaded successfully!")
                st.json(res["counts"])
                st.rerun()
            else:
                st.error("Demo file full_lab.json not found on disk.")
