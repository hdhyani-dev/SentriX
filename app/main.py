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

st.sidebar.title("🛡️ SentriX")
st.sidebar.caption("AI-Assisted Graph-Based Cybersecurity Risk-Path Analysis")
st.sidebar.markdown("---")

# Lab selector in sidebar
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

from app.pages.path_explorer import render_path_explorer
from app.pages.overview import render_overview
from app.pages.lab_inventory import render_lab_inventory
from app.pages.evidence_validation import render_evidence_validation
from app.pages.reports import render_reports

# Page routing registry — 5 cohesive sections with Path Explorer as the primary experience
PAGE_ROUTES = {
    "Path Explorer": render_path_explorer,
    "Overview": render_overview,
    "Lab & Inventory": render_lab_inventory,
    "Evidence & Validation": render_evidence_validation,
    "Reports": render_reports,
}

choice = st.sidebar.radio("Navigation", list(PAGE_ROUTES.keys()))

st.sidebar.markdown("---")
st.sidebar.info("⚠️ **Synthetic Simulation**: SentriX operates read-only. No offensive actions are executed.")

# Execute active page renderer
render_func = PAGE_ROUTES.get(choice)
if render_func:
    render_func(selected_lab_id)
