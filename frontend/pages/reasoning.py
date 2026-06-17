# frontend/pages/reasoning.py
"""
Page dédiée au Reasoning Engine
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.reasoning import ReasoningEngine

st.set_page_config(
    page_title="MITRE ATLAS - Reasoning Engine",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 System Threat Assessment")
st.markdown("Describe your AI system and get a structured threat assessment grounded in the MITRE ATLAS knowledge graph.")

# Initialize
if 'reasoning_engine' not in st.session_state:
    st.session_state.reasoning_engine = None

def init_engine():
    if st.session_state.reasoning_engine is None:
        try:
            st.session_state.reasoning_engine = ReasoningEngine()
            return True
        except Exception as e:
            st.error(f"❌ Error: {e}")
            return False
    return True

# Description du système
system_description = st.text_area(
    "Describe your AI system:",
    placeholder="""
Example:
Our system is a RAG-based conversational assistant that helps customer support agents.
It uses an LLM (GPT-4) to generate responses based on a vector knowledge base.
The data contains customer information (name, email, purchase history).
The system is deployed on AWS and accessible via REST API.
    """,
    height=200
)

col1, col2 = st.columns(2)
with col1:
    include_citations = st.checkbox("Include traceable citations", value=True)
with col2:
    generate_summary = st.checkbox("Generate executive summary", value=True)

if st.button("🧠 Assess Threats", type="primary"):
    if system_description:
        if init_engine():
            with st.spinner("Analyzing system and assessing threats..."):
                try:
                    result = st.session_state.reasoning_engine.generate_assessment(system_description)
                    
                    if "error" not in result:
                        # Métriques
                        summary = result.get('summary', {})
                        st.success("✅ Threat assessment complete!")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Threats", summary.get('total', 0))
                        with col2:
                            st.metric("🔴 Critical", summary.get('critical', 0))
                        with col3:
                            st.metric("🟠 High", summary.get('high', 0))
                        with col4:
                            st.metric("🟡 Medium", summary.get('medium', 0))
                        
                        # Rapport
                        report = result.get('report', '')
                        if report:
                            st.markdown("---")
                            st.markdown(report)
                            
                            st.download_button(
                                label="📥 Download Report",
                                data=report,
                                file_name=f"threat_assessment.md",
                                mime="text/markdown"
                            )
                    else:
                        st.error(f"❌ {result['error']}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    else:
        st.warning("Please describe your AI system.")

# Footer
st.markdown("---")
st.caption("Powered by MITRE ATLAS Knowledge Graph | Neo4j + Text2Cypher + Reasoning Engine")