# frontend/app.py
"""
MITRE ATLAS Knowledge Graph - Web Interface
Version améliorée avec UI/UX modernisé
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Ajouter le chemin du projet pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.query.text2cypher import Text2Cypher
from src.report.report_generator import ReportGenerator
from src.reasoning import ReasoningEngine


# ============================================================
# CONFIGURATION DE LA PAGE
# ============================================================
st.set_page_config(
    page_title="MITRE ATLAS Knowledge Graph",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CSS PERSONNALISÉ - TYPOGRAPHIE AMÉLIORÉE
# ============================================================
st.markdown("""
<style>
    /* --- TYPOGRAPHIE GLOBALE --- */
    .stApp {
        font-size: 18px;
    }
    
    .stMarkdown, .stText, .stParagraph {
        font-size: 18px !important;
        line-height: 1.8 !important;
    }
    
    /* --- EN-TÊTE PRINCIPAL --- */
    .main-header {
        font-size: 3.2rem !important;
        font-weight: 800 !important;
        color: #0A2B4E !important;
        margin-bottom: 0.3rem !important;
        letter-spacing: -0.5px !important;
        background: linear-gradient(135deg, #1F4E78 0%, #0A2B4E 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .sub-header {
        font-size: 1.4rem !important;
        color: #5A6C7D !important;
        margin-bottom: 2rem !important;
        font-weight: 300 !important;
    }
    
    /* --- LOGO SIDEBAR --- */
    .sidebar-logo {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #E2E8F0;
        margin-bottom: 1rem;
    }
    
    .sidebar-logo h1 {
        font-size: 1.8rem;
        font-weight: 800;
        color: #1F4E78;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .sidebar-logo .sub {
        font-size: 0.8rem;
        color: #5A6C7D;
        font-weight: 400;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    /* --- ZONE DE TEXTE ET INPUT --- */
    .stTextInput > div > div > input {
        font-size: 18px !important;
        padding: 12px 16px !important;
        border-radius: 12px !important;
        border: 2px solid #E2E8F0 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #1F4E78 !important;
        box-shadow: 0 0 0 3px rgba(31, 78, 120, 0.15) !important;
    }
    
    .stTextArea > div > div > textarea {
        font-size: 18px !important;
        line-height: 1.6 !important;
        padding: 16px !important;
        border-radius: 12px !important;
        border: 2px solid #E2E8F0 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #1F4E78 !important;
        box-shadow: 0 0 0 3px rgba(31, 78, 120, 0.15) !important;
    }
    
    /* --- BOUTONS --- */
    .stButton > button {
        font-size: 18px !important;
        font-weight: 600 !important;
        padding: 12px 28px !important;
        border-radius: 12px !important;
        border: none !important;
        background: linear-gradient(135deg, #1F4E78 0%, #0A2B4E 100%) !important;
        color: white !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(31, 78, 120, 0.3) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Bouton secondaire */
    .stButton > button[kind="secondary"] {
        background: #F1F5F9 !important;
        color: #1F4E78 !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #E2E8F0 !important;
    }
    
    /* --- SIDEBAR --- */
    .css-1d391kg, .css-1adrfps {
        background: #F8FAFC !important;
    }
    
    /* Exemple Queries alignés à gauche */
    .css-1d391kg .stButton > button {
        font-size: 15px !important;
        padding: 10px 16px !important;
        width: 100% !important;
        text-align: left !important;
        justify-content: flex-start !important;
        background: white !important;
        color: #1F4E78 !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        transition: all 0.2s ease !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    
    .css-1d391kg .stButton > button:hover {
        background: #1F4E78 !important;
        color: white !important;
        border-color: #1F4E78 !important;
    }
    
    /* --- TABS --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 18px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        background: transparent !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #1F4E78 !important;
        color: white !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #E2E8F0 !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"]:hover {
        background: #1F4E78 !important;
    }
    
    /* --- EXPANDER --- */
    .streamlit-expanderHeader {
        font-size: 18px !important;
        font-weight: 600 !important;
        color: #1F4E78 !important;
        background: #F8FAFC !important;
        border-radius: 10px !important;
    }
    
    .streamlit-expanderContent {
        font-size: 17px !important;
        line-height: 1.7 !important;
        padding: 16px !important;
    }
    
    /* --- DATAFRAME --- */
    .stDataFrame {
        font-size: 16px !important;
    }
    
    .stDataFrame table {
        font-size: 16px !important;
    }
    
    .stDataFrame thead tr th {
        font-size: 16px !important;
        font-weight: 700 !important;
        background: #F1F5F9 !important;
        padding: 12px !important;
    }
    
    .stDataFrame tbody tr td {
        padding: 10px !important;
        font-size: 15px !important;
    }
    
    /* --- CODE BLOCK --- */
    .stCodeBlock {
        font-size: 15px !important;
        border-radius: 12px !important;
    }
    
    /* --- INFO, SUCCESS, WARNING, ERROR --- */
    .stAlert {
        font-size: 17px !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
    }
    
    /* --- SELECTBOX --- */
    .stSelectbox > div > div > div {
        font-size: 17px !important;
    }
    
    /* --- CHECKBOX --- */
    .stCheckbox label {
        font-size: 17px !important;
    }
    
    /* --- METRIC STREAMLIT NATIVE --- */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.95rem !important;
        font-weight: 500 !important;
    }
    
    /* --- SEPARATEUR --- */
    hr {
        margin: 2rem 0 !important;
        border-color: #E2E8F0 !important;
        opacity: 0.6 !important;
    }
    
    /* --- MISE EN AVANT DES SÉVÉRITÉS --- */
    .severity-critical {
        color: #DC3545 !important;
        font-weight: 700 !important;
    }
    .severity-high {
        color: #FD7E14 !important;
        font-weight: 700 !important;
    }
    .severity-medium {
        color: #FFC107 !important;
        font-weight: 700 !important;
    }
    .severity-low {
        color: #28A745 !important;
        font-weight: 700 !important;
    }
    
    /* --- FOOTER --- */
    .footer {
        text-align: center;
        color: #94A3B8;
        font-size: 0.9rem;
        padding: 2rem 0 1rem 0;
        border-top: 1px solid #E2E8F0;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================
if 't2c' not in st.session_state:
    st.session_state.t2c = None
if 'report_gen' not in st.session_state:
    st.session_state.report_gen = None
if 'reasoning_engine' not in st.session_state:
    st.session_state.reasoning_engine = None
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'last_results' not in st.session_state:
    st.session_state.last_results = None
if 'reasoning_result' not in st.session_state:
    st.session_state.reasoning_result = None


# ============================================================
# FONCTIONS
# ============================================================
def init_connections():
    """Initialiser les connexions aux services"""
    if st.session_state.t2c is None:
        try:
            st.session_state.t2c = Text2Cypher()
            st.session_state.report_gen = ReportGenerator()
            st.session_state.reasoning_engine = ReasoningEngine()
        except Exception as e:
            st.error(f"❌ Erreur de connexion: {e}")
            return False
    return True


def execute_query(question):
    """Exécuter une requête et mettre à jour l'état"""
    if not init_connections():
        return None
    try:
        result = st.session_state.t2c.ask(question)
        st.session_state.last_results = result
        st.session_state.query_history.append({
            "question": question,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        return result
    except Exception as e:
        st.error(f"❌ Erreur: {e}")
        return {"error": str(e)}


def run_reasoning(system_description):
    """Exécuter le Reasoning Engine"""
    if not init_connections():
        return None
    try:
        with st.spinner("🧠 Analyse du système et évaluation des menaces..."):
            result = st.session_state.reasoning_engine.generate_assessment(system_description)
            st.session_state.reasoning_result = result
            return result
    except Exception as e:
        st.error(f"❌ Erreur: {e}")
        return {"error": str(e)}


def close_connections():
    """Fermer les connexions"""
    if st.session_state.t2c:
        try:
            st.session_state.t2c.close()
        except:
            pass
    if st.session_state.report_gen:
        try:
            st.session_state.report_gen.close()
        except:
            pass
    if st.session_state.reasoning_engine:
        try:
            st.session_state.reasoning_engine.close()
        except:
            pass


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    # Logo stylisé (au lieu de l'image)
    st.markdown("""
    <div class="sidebar-logo">
        <h1>🛡️ ATLAS</h1>
        <div class="sub">MITRE Knowledge Graph</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 📋 Example Queries")
    example_queries = [
        ("📋 List all tactics", "List all tactics"),
        ("🔍 Techniques in Reconnaissance", "Techniques in Reconnaissance"),
        ("🛡️ Mitigations for LLM Prompt Injection", "Mitigations for LLM Prompt Injection"),
        ("👤 Actors using Prompt Injection", "Actors using Prompt Injection"),
        ("🎯 Techniques targeting RAG", "Techniques targeting RAG"),
        ("⚠️ Critical severity techniques", "Critical severity techniques"),
        ("📊 Techniques with CVSS > 8", "Techniques with CVSS > 8"),
        ("🔗 RAG techniques with developer mitigations", "Techniques targeting RAG with developer mitigations"),
        ("🎯 Techniques used by APT28", "Techniques used by APT28"),
    ]
    
    for label, query in example_queries:
        if st.button(label, key=f"example_{label}"):
            st.session_state.query = query
            st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 🧠 Reasoning Engine")
    if st.button("🔍 System Threat Assessment", key="reasoning_btn"):
        st.session_state.active_tab = "reasoning"
        st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 📊 Statistics")
    # Dans app.py, dans la partie Statistics du sidebar ou dans une nouvelle section

# ============================================================
# RECENTLY UPDATED TECHNIQUES (NOUVEAU)
# ============================================================
with st.sidebar:
    # ... code existant ...
    
    st.markdown("---")
    st.markdown("### 🔄 Recent Updates")
    
    if init_connections():
        try:
            with st.session_state.t2c.driver.session() as session:
                recent = session.run("""
                    MATCH (t:Technique)
                    WHERE t.last_updated IS NOT NULL
                    RETURN t.name, t.severity, t.last_updated
                    ORDER BY t.last_updated DESC
                    LIMIT 3
                """)
                
                for r in list(recent):
                    severity = r.get('t.severity', 'unknown')
                    emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(severity, '⚪')
                    st.markdown(f"- {emoji} **{r['t.name']}**")
                    st.caption(f"  updated: {r['t.last_updated']}")
        except Exception as e:
            st.warning(f"⚠️ Could not load recent updates: {e}")
    if init_connections():
        try:
            with st.session_state.t2c.driver.session() as session:
                counts = {
                    "Tactics": session.run("MATCH (t:Tactic) RETURN count(t) as count").single()["count"],
                    "Techniques": session.run("MATCH (t:Technique) RETURN count(t) as count").single()["count"],
                    "Mitigations": session.run("MATCH (m:Mitigation) RETURN count(m) as count").single()["count"],
                    "Case Studies": session.run("MATCH (cs:CaseStudy) RETURN count(cs) as count").single()["count"],
                    "Actors": session.run("MATCH (a:Actor) RETURN count(a) as count").single()["count"],
                    "Components": session.run("MATCH (c:Component) RETURN count(c) as count").single()["count"],
                }
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📋 Tactics", counts["Tactics"])
                    st.metric("🛡️ Mitigations", counts["Mitigations"])
                    st.metric("🧩 Components", counts["Components"])
                with col2:
                    st.metric("⚡ Techniques", counts["Techniques"])
                    st.metric("👤 Actors", counts["Actors"])
                    st.metric("📖 Case Studies", counts["Case Studies"])
        except Exception as e:
            st.warning("⚠️ Cannot connect to Neo4j")


# ============================================================
# MAIN PAGE - HEADER
# ============================================================
st.markdown('<p class="main-header">🛡️ MITRE ATLAS Knowledge Graph</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Query adversarial techniques against AI systems</p>', unsafe_allow_html=True)


# ============================================================
# TABS
# ============================================================
active_tab = st.session_state.get('active_tab', 'query')
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Query", "📊 Results", "📄 Report", "🧠 Reasoning"])


# ============================================================
# TAB 1: QUERY
# ============================================================
with tab1:
    st.markdown("### 🔍 Ask a question about AI threats")
    st.markdown("Enter your question in natural language and the system will translate it to a Cypher query.")
    
    # Utilisation de colonnes pour aligner le champ et le bouton
    col1, col2 = st.columns([5, 1])
    with col1:
        query = st.text_input(
            "Question:",
            value=st.session_state.get('query', ''),
            placeholder="e.g., What mitigations exist for LLM Prompt Injection?",
            label_visibility="collapsed"
        )
    with col2:
        # Ajustement vertical pour aligner avec le champ
        st.write("")
        execute_btn = st.button("🔍 Execute", type="primary", width='stretch')
    
    if execute_btn and query:
        with st.spinner("🔄 Generating response..."):
            result = execute_query(query)
        
        if result and "error" not in result:
            st.success(f"✅ Found {len(result.get('results', []))} results")
            
            with st.expander("📝 Generated Cypher", expanded=False):
                st.code(result.get('cypher', 'N/A'), language="cypher")
            
            st.subheader("📊 Results")
            if result.get('results'):
                st.dataframe(result['results'], width='stretch')
            else:
                st.info("ℹ️ No results found")
        elif result and "error" in result:
            st.error(f"❌ {result['error']}")


# ============================================================
# TAB 2: RESULTS
# ============================================================
with tab2:
    st.markdown("### 📊 Results History")
    
    if st.session_state.last_results:
        result = st.session_state.last_results
        if "error" not in result:
            st.success(f"✅ Found {len(result.get('results', []))} results")
            st.json(result)
        else:
            st.error(f"❌ {result['error']}")
    else:
        st.info("ℹ️ No query executed yet. Run a query in the Query tab.")
    
    if st.session_state.query_history:
        st.markdown("---")
        st.markdown("### 📜 Query History")
        for q in st.session_state.query_history[-10:]:
            st.markdown(f"- **{q['question']}** *(at {q.get('timestamp', '')})*")


# ============================================================
# TAB 3: REPORT
# ============================================================
with tab3:
    st.markdown("### 📄 Generate Threat Report")
    st.markdown("Describe the threat scenario or question to generate a structured report with traceable citations.")
    
    report_query = st.text_area(
        "Threat scenario:",
        placeholder="e.g., Critical severity techniques and their mitigations",
        height=120
    )
    
    if st.button("📄 Generate Report", type="primary", width='stretch'):
        if report_query:
            with st.spinner("🔄 Generating report..."):
                if init_connections():
                    try:
                        report = st.session_state.report_gen.generate_report(report_query)
                        st.markdown(report)
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.download_button(
                            label="📥 Download Markdown",
                            data=report,
                            file_name=f"threat_report_{timestamp}.md",
                            mime="text/markdown",
                            width='stretch'
                        )
                    except Exception as e:
                        st.error(f"❌ Error generating report: {e}")
        else:
            st.warning("⚠️ Please describe the threat scenario")


# ============================================================
# TAB 4: REASONING ENGINE
# ============================================================
with tab4:
    st.markdown("### 🧠 System Threat Assessment")
    st.markdown("""
    Describe your AI system and get a structured threat assessment grounded in the MITRE ATLAS knowledge graph.
    
    **The system will:**
    1. **Analyze** your system description
    2. **Map** components to the knowledge graph
    3. **Find** relevant threats
    4. **Prioritize** risks by severity
    5. **Generate** a structured report with traceable citations
    """)
    
    st.markdown("---")
    
    # System description input
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
        include_citations = st.checkbox("✅ Include citations", value=True)
    with col2:
        generate_summary = st.checkbox("📊 Generate summary", value=True)
    
    st.markdown("---")
    
    if st.button("🧠 Assess Threats", type="primary", width='stretch'):
        if system_description:
            result = run_reasoning(system_description)
            
            if result and "error" not in result:
                st.success("✅ Threat assessment complete!")
                
                # Métriques
                summary = result.get('summary', {})
                total = sum(summary.values())
                
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("Total Threats", total)
                with col2:
                    st.metric("🔴 Critical", summary.get('critical', 0))
                with col3:
                    st.metric("🟠 High", summary.get('high', 0))
                with col4:
                    st.metric("🟡 Medium", summary.get('medium', 0))
                with col5:
                    st.metric("🟢 Low", summary.get('low', 0))
                
                # Informations du système
                with st.expander("📋 System Profile", expanded=False):
                    system_info = result.get('system_info', {})
                    st.json(system_info)
                
                # Menaces identifiées
                threats = result.get('threats', [])
                if threats:
                    with st.expander(f"⚠️ Threats Found ({len(threats)})", expanded=True):
                        severity_icons = {
                            'critical': '🔴',
                            'high': '🟠',
                            'medium': '🟡',
                            'low': '🟢'
                        }
                        
                        for i, t in enumerate(threats[:10], 1):
                            severity = t.get('severity', 'medium').lower()
                            icon = severity_icons.get(severity, '⚪')
                            
                            st.markdown(f"**{i}. {icon} {t.get('technique_name')}**  `{t.get('technique_id')}`")
                            st.markdown(f"   - Severity: **{severity.upper()}**")
                            st.markdown(f"   - CVSS: {t.get('cvss_score', 'N/A')}")
                            
                            mitigations = t.get('mitigations', [])
                            if mitigations:
                                st.markdown(f"   - Mitigations: {', '.join(mitigations[:3])}")
                            
                            actors = t.get('actors', [])
                            if actors:
                                st.markdown(f"   - Actors: {', '.join(actors[:3])}")
                            st.markdown("---")
                
                # Rapport complet
                report = result.get('report', '')
                if report:
                    with st.expander("📄 Full Report", expanded=True):
                        st.markdown(report)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button(
                        label="📥 Download Report (Markdown)",
                        data=report,
                        file_name=f"threat_assessment_{timestamp}.md",
                        mime="text/markdown",
                        width='stretch'
                    )
                
                # Résumé exécutif
                if generate_summary and report:
                    with st.expander("📊 Executive Summary", expanded=False):
                        try:
                            from src.reasoning.report_generator import ReasoningReportGenerator
                            rg = ReasoningReportGenerator()
                            executive_summary = rg.generate_summary(report)
                            st.markdown(executive_summary)
                        except Exception as e:
                            st.info(f"ℹ️ Executive summary unavailable: {e}")
                
            elif result and "error" in result:
                st.error(f"❌ Error: {result['error']}")
        else:
            st.warning("⚠️ Please describe your AI system.")


# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div class="footer">
    <p>🛡️ MITRE ATLAS Knowledge Graph • Powered by Neo4j + Text2Cypher + OpenRouter</p>
    <p>All threats are grounded in the MITRE ATLAS knowledge graph</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# CLEANUP
# ============================================================
import atexit
atexit.register(close_connections)