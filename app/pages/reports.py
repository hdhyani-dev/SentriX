"""
Reports Page — View and export assessment reports.
"""

from pathlib import Path
import streamlit as st

from database.connection import get_session
from core.services.report_service import report_service


def render_reports(lab_id: str | None):
    st.title("Assessment Report Generation")

    if not lab_id:
        st.info("Please select a lab first.")
        return

    with get_session() as session:
        format_choice = st.radio("Report Format", ["Markdown", "HTML"], horizontal=True)

        if st.button("Generate Live Assessment Report"):
            try:
                report_text = report_service.generate_report(session, lab_id, format=format_choice.lower())
                st.session_state["generated_report"] = report_text
                st.session_state["report_format"] = format_choice.lower()
            except Exception as e:
                st.error(f"Failed to generate report: {e}")

        if "generated_report" in st.session_state:
            content = st.session_state["generated_report"]
            fmt = st.session_state.get("report_format", "markdown")

            st.download_button(
                label=f"📥 Download Report ({fmt.upper()})",
                data=content,
                file_name=f"chainbreak_report_{lab_id}.{'html' if fmt == 'html' else 'md'}",
                mime="text/html" if fmt == "html" else "text/markdown",
            )

            st.markdown("---")
            st.subheader("Report Preview")
            if fmt == "markdown":
                st.markdown(content)
            else:
                st.components.v1.html(content, height=600, scrolling=True)
