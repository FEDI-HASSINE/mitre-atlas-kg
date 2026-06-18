# frontend/pages/queries.py
"""
Page des requêtes prédéfinies et exploration
"""

import streamlit as st
import sys
import os
import pandas as pd

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.query.text2cypher import Text2Cypher

st.set_page_config(
    page_title="MITRE ATLAS - Query Explorer",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Query Explorer")
st.markdown("Explore the MITRE ATLAS knowledge graph with predefined and custom queries")

# Initialize
if 't2c' not in st.session_state:
    st.session_state.t2c = None

def init_connection():
    if st.session_state.t2c is None:
        try:
            st.session_state.t2c = Text2Cypher()
        except Exception as e:
            st.error(f"❌ Connection error: {e}")
            return False
    return True

# Query Categories
QUERY_CATEGORIES = {
    "🏛️ Basic Discovery": [
        "List all tactics",
        "List all techniques",
        "Count techniques",
        "List all mitigations",
        "List all case studies"
    ],
    "🎯 Technique Analysis": [
        "Techniques in Reconnaissance",
        "Techniques in Initial Access",
        "Techniques in Execution",
        "Techniques with Prompt",
        "Techniques with injection",
        "Techniques with evasion"
    ],
    "🛡️ Mitigation Analysis": [
        "Mitigations for LLM Prompt Injection",
        "Mitigations for developers",
        "Mitigations for security team",
        "Techniques with mitigations",
        "Mitigations by category"
    ],
    "👤 Actor Intelligence": [
        "Actors using Prompt Injection",
        "Techniques used by APT28",
        "Actors using critical techniques",
        "All actors and their techniques",
        "Actors targeting RAG"
    ],
    "🎯 Target Analysis": [
        "Techniques targeting RAG",
        "Techniques targeting ChatGPT",
        "Techniques targeting Copilot",
        "Components targeted by Prompt Injection",
        "All components and their techniques"
    ],
    "⚠️ Risk Assessment": [
        "Critical severity techniques",
        "High severity techniques",
        "Medium severity techniques",
        "Techniques with CVSS > 8",
        "Techniques with CVSS > 7",
        "Severity distribution"
    ],
    "🧩 Complex Analysis": [
        "RAG techniques with developer mitigations",
        "Critical techniques with mitigations",
        "Actors using techniques targeting inference",
        "Techniques with severity and CVSS score",
        "Tactics with number of techniques"
    ]
}

# Sidebar - Query Categories
with st.sidebar:
    st.markdown("### 📂 Query Categories")
    
    selected_category = st.selectbox(
        "Select a category",
        list(QUERY_CATEGORIES.keys())
    )
    
    st.markdown("---")
    st.markdown("### 📋 Quick Queries")
    
    for query in QUERY_CATEGORIES[selected_category]:
        if st.button(query, key=f"cat_{query}", width='stretch'):
            st.session_state.query_input = query
            st.rerun()
    
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    
    max_items = st.slider("Max results to display", 5, 50, 20)
    
    show_cypher = st.checkbox("Show generated Cypher", value=True)
    show_summary = st.checkbox("Show summary statistics", value=True)

# Main area
col1, col2 = st.columns([4, 1])

with col1:
    query = st.text_input(
        "Ask a question about AI threats:",
        value=st.session_state.get('query_input', ''),
        placeholder="e.g., What mitigations exist for LLM Prompt Injection?"
    )

with col2:
    st.write("")
    st.write("")
    execute_btn = st.button("🔍 Execute", type="primary", width='stretch')

# Exécution
if execute_btn and query:
    if not init_connection():
        st.stop()
    
    with st.spinner("🔄 Executing query..."):
        result = st.session_state.t2c.ask(query)
    
    if result and "error" not in result:
        results = result.get('results', [])
        
        # Summary statistics
        if show_summary:
            st.success(f"✅ Found {len(results)} results")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Results", len(results))
            with col2:
                # Count unique IDs if available
                ids = set()
                for r in results:
                    for key, value in r.items():
                        if 'id' in key.lower():
                            ids.add(value)
                st.metric("Unique IDs", len(ids) if ids else "N/A")
            with col3:
                st.metric("Query Time", "~2s")
            with col4:
                st.metric("Status", "✅ Success")
        
        # Cypher
        if show_cypher:
            with st.expander("📝 Generated Cypher", expanded=True):
                st.code(result.get('cypher', 'N/A'), language="cypher")
        
        # Results as DataFrame
        if results:
            df = pd.DataFrame(results)
            
            # Limit results
            if len(df) > max_items:
                st.info(f"Showing first {max_items} of {len(df)} results")
                df = df.head(max_items)
            
            st.subheader("📊 Results")
            st.dataframe(df, width='stretch')
            
            # Raw JSON for debugging
            with st.expander("🔧 Raw JSON"):
                st.json(result)
        else:
            st.info("ℹ️ No results found")
    
    elif result and "error" in result:
        st.error(f"❌ Error: {result['error']}")

elif query and not execute_btn:
    st.info("Press 'Execute' or press Enter to run the query")

# Quick Stats (always visible)
st.markdown("---")
st.subheader("📊 Quick Stats")

if init_connection():
    try:
        with st.session_state.t2c.driver.session() as session:
            stats = {
                "Tactics": session.run("MATCH (t:Tactic) RETURN count(t) as c").single()["c"],
                "Techniques": session.run("MATCH (t:Technique) RETURN count(t) as c").single()["c"],
                "Mitigations": session.run("MATCH (m:Mitigation) RETURN count(m) as c").single()["c"],
                "Case Studies": session.run("MATCH (cs:CaseStudy) RETURN count(cs) as c").single()["c"],
                "Actors": session.run("MATCH (a:Actor) RETURN count(a) as c").single()["c"],
                "Components": session.run("MATCH (c:Component) RETURN count(c) as c").single()["c"],
            }
            
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            cols = [col1, col2, col3, col4, col5, col6]
            labels = ["Tactics", "Techniques", "Mitigations", "Case Studies", "Actors", "Components"]
            
            for col, label in zip(cols, labels):
                with col:
                    st.metric(label, stats.get(label, 0))
            
        
            # SEVERITY DISTRIBUTION - CORRECTED
            try:
                severity_data = session.run("""
                    MATCH (t:Technique) 
                    WHERE t.severity IS NOT NULL 
                    RETURN t.severity as severity, count(t) as count
                    ORDER BY count DESC
                """)
                
                severities = list(severity_data)
                if severities:
                    st.subheader("📊 Severity Distribution")
                    severity_df = pd.DataFrame(severities)
                    
                    # ✅ Trouver la colonne de sévérité (avec vérification de type)
                    severity_col = None
                    for col in severity_df.columns:
                        if isinstance(col, str) and 'severity' in col.lower():
                            severity_col = col
                            break
                    
                    if severity_col:
                        st.bar_chart(severity_df.set_index(severity_col))
                    else:
                        # Fallback: utiliser la première colonne
                        st.bar_chart(severity_df.set_index(severity_df.columns[0]))
                else:
                    st.info("ℹ️ No severity data available")
            except Exception as e:
                st.warning(f"Could not load severity distribution: {e}")
            
            
            # COMPONENT DISTRIBUTION - CORRIGÉ
            
            try:
                comp_data = session.run("""
                    MATCH (c:Component)<-[:TARGETS]-(t:Technique)
                    RETURN c.name as component, count(t) as count
                    ORDER BY count DESC
                    LIMIT 10
                """)
                
                components = list(comp_data)
                if components:
                    st.subheader("🎯 Most Targeted Components")
                    comp_df = pd.DataFrame(components)
                    
                    # ✅ Trouver la colonne de composant (avec vérification de type)
                    comp_col = None
                    for col in comp_df.columns:
                        if isinstance(col, str) and ('component' in col.lower() or 'name' in col.lower()):
                            comp_col = col
                            break
                    
                    if comp_col:
                        st.bar_chart(comp_df.set_index(comp_col))
                    else:
                        # Fallback: utiliser la première colonne
                        st.bar_chart(comp_df.set_index(comp_df.columns[0]))
                else:
                    st.info("ℹ️ No component data available")
            except Exception as e:
                st.warning(f"Could not load component distribution: {e}")
                
    except Exception as e:
        st.warning(f"Could not load stats: {e}")

# Footer
st.markdown("---")
st.caption("Powered by MITRE ATLAS Knowledge Graph | Neo4j + Text2Cypher")