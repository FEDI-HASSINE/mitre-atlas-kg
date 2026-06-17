# src/reasoning/prompts.py
"""
Prompts pour le Reasoning Engine
"""

SYSTEM_ANALYSIS_PROMPT = """
You are an AI security expert. Analyze the following system description and extract key components.

SYSTEM DESCRIPTION:
{description}

Extract the following information as JSON:
{{
  "system_type": "brief description of the system",
  "components": ["list", "of", "key", "components"],
  "data_types": ["types of data handled"],
  "access_levels": ["public", "internal", "restricted"],
  "deployment": ["cloud", "on-premise", "hybrid"],
  "user_types": ["who uses the system"]
}}

Return ONLY valid JSON.
"""

REPORT_SYNTHESIS_PROMPT = """
You are an AI security expert. Create a structured threat assessment report.

SYSTEM DESCRIPTION:
{description}

SYSTEM PROFILE:
{system_info}

THREATS IDENTIFIED FROM KNOWLEDGE GRAPH:
{threats}

Create a structured Markdown report with:

## 1. Executive Summary
Brief overview of the system and key risks

## 2. System Profile
- System Type
- Components
- Data Types
- Access Levels
- Deployment

## 3. Threat Assessment
For each threat found:
- Technique Name and ID (with ATLAS citation)
- Severity Level
- CVSS Score (if available)
- Why it affects this system
- Mitigations (from the graph)
- Actors known to use this technique

## 4. Risk Score Summary
| Component | Threat Count | Critical | High | Medium | Low |
|-----------|--------------|----------|------|--------|-----|

## 5. Recommendations
Prioritized recommendations based on the threats

Requirements:
- Every threat MUST include the MITRE ATLAS technique ID as citation
- Mitigations MUST come from the data provided
- Be specific about why each threat applies to this system
- Write in ENGLISH

Return as Markdown.
"""

REPORT_SUMMARY_PROMPT = """
Summarize the following threat assessment in 3-4 sentences for an executive audience:

{report}

Be concise and focus on the most critical risks.
"""