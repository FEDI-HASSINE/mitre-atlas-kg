# src/reasoning/config.py
"""
Configuration du Reasoning Engine
"""

# Catégories de menaces
THREAT_SEVERITIES = {
    'critical': 4,
    'high': 3,
    'medium': 2,
    'low': 1
}

# Couleurs pour le rapport
SEVERITY_COLORS = {
    'critical': '🔴',
    'high': '🟠',
    'medium': '🟡',
    'low': '🟢'
}

# Composants connus pour mapping
KNOWN_COMPONENTS = [
    'RAG', 'Vector DB', 'LLM', 'API', 'Knowledge Base',
    'ChatGPT', 'Copilot', 'Slack AI', 'Email System',
    'Database', 'Cloud Storage', 'MCP Server', 'Cursor',
    'GitHub Copilot', 'Jira', 'Salesforce'
]

# Techniques par composant (cache)
TECHNIQUE_CACHE = {}

# Seuils de priorisation
PRIORITY_THRESHOLDS = {
    'critical_cvss': 9.0,
    'high_cvss': 7.0,
    'medium_cvss': 4.0
}