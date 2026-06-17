# frontend/utils.py
"""
Utilitaires pour l'interface Streamlit
"""

import pandas as pd

def results_to_dataframe(results):
    """Convertit les résultats en DataFrame pandas"""
    if not results:
        return pd.DataFrame()
    
    df = pd.DataFrame(results)
    return df

def format_results_markdown(results):
    """Formate les résultats en markdown"""
    if not results:
        return "*No results*"
    
    lines = []
    for i, r in enumerate(results, 1):
        if isinstance(r, dict):
            items = [f"**{k}**: {v}" for k, v in r.items()]
            lines.append(f"{i}. " + " | ".join(items))
        else:
            lines.append(f"{i}. {r}")
    return "\n".join(lines)

def get_query_categories():
    """Retourne les catégories de requêtes prédéfinies"""
    return {
        "Basic Discovery": [
            "List all tactics",
            "List all techniques",
            "Count techniques"
        ],
        "Technique Analysis": [
            "Techniques in Reconnaissance",
            "Techniques in Initial Access",
            "Techniques with Prompt"
        ],
        "Mitigation Analysis": [
            "Mitigations for LLM Prompt Injection",
            "Mitigations for developers",
            "Techniques with mitigations"
        ],
        "Actor Intelligence": [
            "Actors using Prompt Injection",
            "Techniques used by APT28",
            "Actors using critical techniques"
        ],
        "Risk Assessment": [
            "Critical severity techniques",
            "Techniques with CVSS > 8",
            "High severity techniques"
        ],
        "Complex Analysis": [
            "Techniques targeting RAG",
            "RAG techniques with developer mitigations",
            "Actors targeting inference"
        ]
    }