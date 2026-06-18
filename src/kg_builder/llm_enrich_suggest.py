# src/kg_builder/llm_enrich_suggest.py
import os
import json
import csv
import yaml
import requests
from dotenv import load_dotenv
from datetime import date, datetime

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

# The 6 techniques to enhance
TARGET_TECHNIQUES = [
    {"id": "AML.T0015", "name": "Evade AI Model"},
    {"id": "AML.T0051", "name": "LLM Prompt Injection"},
    {"id": "AML.T0053", "name": "AI Agent Tool Invocation"},
    {"id": "AML.T0065", "name": "LLM Prompt Crafting"},
    {"id": "AML.T0052", "name": "Phishing"},
    {"id": "AML.T0025", "name": "Exfiltration via Cyber Means"},
]

class LLMEnricher:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.model = OPENROUTER_MODEL
    
    def _serialize_value(self, value):
        """Convert a value to JSON-serializable format"""
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._serialize_value(v) for v in value]
        else:
            return value
    
    def find_case_studies(self, technique_id, yaml_path):
        """Find the case studies associated with a technique"""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        related_cases = []
        for cs in data.get('case-studies', []):
            for step in cs.get('procedure', []):
                tech = step.get('technique')
                if isinstance(tech, dict):
                    tech = tech.get('id')
                if tech == technique_id:
                    # Ensure that everything is serializable
                    cs_copy = {
                        'id': cs.get('id'),
                        'name': cs.get('name'),
                        'actor': cs.get('actor'),
                        'target': cs.get('target'),
                        'date': self._serialize_value(cs.get('incident-date')),
                        'summary': cs.get('summary', '')[:500]
                    }
                    related_cases.append(cs_copy)
                    break
        return related_cases
    
    def suggest_enrichment(self, technique_id, technique_name, case_studies):
        """Use LLM to suggest enrichment fields."""
        # Ensure all data is serializable.
        case_studies_serializable = self._serialize_value(case_studies)
        
        prompt = f"""
You are an AI security and MITRE ATLAS expert.

Analyze the following technique: **{technique_name} ({technique_id})**

Associated Case Studies (real incidents where this technique was used):
{json.dumps(case_studies_serializable, indent=2, ensure_ascii=False)}

Suggest the following enrichments for this technique:

1. **Actors**: Which actors (individuals, groups, organizations) have used this technique? (list of names)
2. **Targeted Components**: Which systems, components, or infrastructures are attacked by this technique? (list)
3. **Severity**: critical, high, medium, low (estimate based on impact)
4. **CVSS Score**: 0.0 - 10.0 (estimate a score)
5. **First Seen**: First observation date (YYYY-MM-DD)
6. **Last Seen**: Last observation date (YYYY-MM-DD)

Respond ONLY in VALID JSON format:
{{
  "actors": ["actor1", "actor2"],
  "targeted_components": ["component1", "component2"],
  "severity": "critical|high|medium|low",
  "cvss_score": 8.5,
  "first_seen": "2024-01-01",
  "last_seen": "2024-12-31"
}}
"""
        
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "MITRE ATLAS Enrichment"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 800
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return {"error": f"API Error: {response.status_code} - {response.text[:200]}"}
            
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            content = content.replace('```json', '').replace('```', '').strip()
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            return {"error": f"JSON Parse Error: {e}"}
        except requests.exceptions.Timeout:
            return {"error": "Timeout - API not responding"}
        except Exception as e:
            return {"error": str(e)}
    
    def export_to_csv(self, results, output_path='data/processed/enrichment_suggestions.csv'):
        """Export results to CSV"""
        fieldnames = [
            'technique_id', 'technique_name',
            'actors', 'targeted_components',
            'severity', 'cvss_score',
            'first_seen', 'last_seen',
            'case_studies_count'
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for r in results:
                writer.writerow({
                    'technique_id': r['technique_id'],
                    'technique_name': r['technique_name'],
                    'actors': '; '.join(r.get('actors', [])),
                    'targeted_components': '; '.join(r.get('targeted_components', [])),
                    'severity': r.get('severity', ''),
                    'cvss_score': r.get('cvss_score', ''),
                    'first_seen': r.get('first_seen', ''),
                    'last_seen': r.get('last_seen', ''),
                    'case_studies_count': r.get('case_studies_count', 0)
                })
        
        print(f"Exported to {output_path}")

if __name__ == "__main__":
    print("Generating enrichment suggestions")
    print("=" * 50)
    
    enricher = LLMEnricher()
    yaml_path = 'data/raw/atlas-data/dist/ATLAS.yaml'
    results = []
    
    for tech in TARGET_TECHNIQUES:
        print(f"\nProcessing {tech['name']} ({tech['id']})...")
        
        # Find case studies
        cases = enricher.find_case_studies(tech['id'], yaml_path)
        print(f"   → {len(cases)} case studies found")
        
        if not cases:
            print(f"No case studies found, skipping suggestion")
            results.append({
                'technique_id': tech['id'],
                'technique_name': tech['name'],
                'actors': [],
                'targeted_components': [],
                'severity': '',
                'cvss_score': '',
                'first_seen': '',
                'last_seen': '',
                'case_studies_count': 0
            })
            continue
        
        # LLM suggestion
        print(f"Sending to API... (estimated time: 5-10 seconds)")
        suggestion = enricher.suggest_enrichment(tech['id'], tech['name'], cases)
        
        if 'error' in suggestion:
            print(f"Error: {suggestion['error']}")
            suggestion = {}
        else:
            print(f"Suggestion received: {len(suggestion.get('actors', []))} actors, {len(suggestion.get('targeted_components', []))} components")
        
        results.append({
            'technique_id': tech['id'],
            'technique_name': tech['name'],
            'actors': suggestion.get('actors', []),
            'targeted_components': suggestion.get('targeted_components', []),
            'severity': suggestion.get('severity', ''),
            'cvss_score': suggestion.get('cvss_score', ''),
            'first_seen': suggestion.get('first_seen', ''),
            'last_seen': suggestion.get('last_seen', ''),
            'case_studies_count': len(cases)
        })
    
    # Export to CSV
    enricher.export_to_csv(results)
    
    print("\n" + "=" * 50)
    print("File generated: data/processed/enrichment_suggestions.csv")
    print("Open it in Excel for manual verification")