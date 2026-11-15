"""
ChainBreak — Minimal Working Development Interface (Streamlit)
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
    page_title="ChainBreak — Risk Path Analysis",
    page_icon="🛡️",
    layout="wide",
)

st.sidebar.title("🛡️ ChainBreak")
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

# Navigation menu
pages = [
    "Dashboard",
    "Lab Management",
    "Asset & Services",
    "Security Findings",
    "Candidate Paths",
    "Safe Validation",
    "Evidence Records",
    "Assessment Report",
]

choice = st.sidebar.radio("Navigation", pages)

st.sidebar.markdown("---")
st.sidebar.info("⚠️ **Synthetic Simulation**: ChainBreak operates read-only. No offensive actions are executed.")

# Page routing
if choice == "Dashboard":
    from app.pages.dashboard import render_dashboard
    render_dashboard(selected_lab_id)

elif choice == "Lab Management":
    from app.pages.labs import render_labs
    render_labs(selected_lab_id)

elif choice == "Asset & Services":
    from app.pages.assets import render_assets
    render_assets(selected_lab_id)

elif choice == "Security Findings":
    from app.pages.findings import render_findings
    render_findings(selected_lab_id)

elif choice == "Candidate Paths":
    from app.pages.attack_paths import render_attack_paths
    render_attack_paths(selected_lab_id)

elif choice == "Safe Validation":
    from app.pages.validation import render_validation
    render_validation(selected_lab_id)

elif choice == "Evidence Records":
    from app.pages.evidence import render_evidence
    render_evidence(selected_lab_id)

elif choice == "Assessment Report":
    from app.pages.reports import render_reports
    render_reports(selected_lab_id)
