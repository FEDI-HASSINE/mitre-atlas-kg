# src/reasoning/config.py
"""
Configuration of the Reasoning Engine
"""

# Threat Categories
THREAT_SEVERITIES = {
    'critical': 4,
    'high': 3,
    'medium': 2,
    'low': 1
}

# Colors for the report
SEVERITY_COLORS = {
    'critical': '🔴',
    'high': '🟠',
    'medium': '🟡',
    'low': '🟢'
}

# Known components for mapping
KNOWN_COMPONENTS = [
    'RAG', 'Vector DB', 'LLM', 'API', 'Knowledge Base',
    'ChatGPT', 'Copilot', 'Slack AI', 'Email System',
    'Database', 'Cloud Storage', 'MCP Server', 'Cursor',
    'GitHub Copilot', 'Jira', 'Salesforce'
]

# Component-based techniques (cache)
TECHNIQUE_CACHE = {}

# Priority thresholds
PRIORITY_THRESHOLDS = {
    'critical_cvss': 9.0,
    'high_cvss': 7.0,
    'medium_cvss': 4.0
}