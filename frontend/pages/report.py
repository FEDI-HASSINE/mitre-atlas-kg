# frontend/pages/report.py
"""
Page de génération de rapport
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.report.report_generator import ReportGenerator

st.set_page_config(
    page_title="MITRE ATLAS - Report Generator",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Threat Report Generator")

# Initialize
if 'report_gen' not in st.session_state:
    st.session_state.report_gen = ReportGenerator()

query = st.text_area(
    "Describe the threat scenario:",
    placeholder="e.g., Critical severity techniques and their mitigations",
    height=150
)

include_citations = st.checkbox("Include traceable citations", value=True)

if st.button("Generate Report", type="primary"):
    if query:
        with st.spinner("Generating report..."):
            try:
                report = st.session_state.report_gen.generate_report(query, include_citations)
                st.markdown(report)
                
                st.download_button(
                    label="Download as Markdown",
                    data=report,
                    file_name="threat_report.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter a query")