"""
SentriX — Minimal Working Development Interface (Streamlit)
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st

from database.connection import init_db, get_session
from core.services.lab_service import lab_service

# Initialize DB tables on startup
init_db()

st.set_page_config(
    page_title="SentriX — Risk Path Analysis",
    page_icon="🛡️",
    layout="wide",
)

# Sidebar Lab Selection & Branding
st.sidebar.title("🛡️ SentriX")
st.sidebar.caption("AI-Assisted Graph-Based Cybersecurity Risk-Path Analysis")
st.sidebar.markdown("---")

with get_session() as session:
    labs = lab_service.list_labs(session)
    lab_options = {f"{l.name} ({l.id})": l.id for l in labs}

if not lab_options:
    st.sidebar.warning("No labs found. Please initialize or import a lab.")
    selected_lab_id = None
else:
    selected_label = st.sidebar.selectbox("Active Laboratory", list(lab_options.keys()))
    selected_lab_id = lab_options[selected_label]
    st.session_state["selected_lab_id"] = selected_lab_id

st.sidebar.markdown("---")
st.sidebar.info("⚠️ **Synthetic Simulation**: SentriX operates read-only. No offensive actions are executed.")

from app.views.path_explorer import render_path_explorer
from app.views.overview import render_overview
from app.views.lab_inventory import render_lab_inventory
from app.views.evidence_validation import render_evidence_validation
from app.views.reports import render_reports


def page_path_explorer():
    render_path_explorer(st.session_state.get("selected_lab_id"))


def page_overview():
    render_overview(st.session_state.get("selected_lab_id"))


def page_lab_inventory():
    render_lab_inventory(st.session_state.get("selected_lab_id"))


def page_evidence_validation():
    render_evidence_validation(st.session_state.get("selected_lab_id"))


def page_reports():
    render_reports(st.session_state.get("selected_lab_id"))


# Native Streamlit navigation: powers the top menu buttons with capitalized titles and removes the redundant radio panel
nav = st.navigation([
    st.Page(page_path_explorer, title="Path Explorer", icon="🛡️", default=True),
    st.Page(page_overview, title="Overview", icon="📊"),
    st.Page(page_lab_inventory, title="Lab & Inventory", icon="🏢"),
    st.Page(page_evidence_validation, title="Evidence & Validation", icon="✅"),
    st.Page(page_reports, title="Reports", icon="📄"),
])

nav.run()
