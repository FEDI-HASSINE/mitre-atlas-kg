# src/reasoning/system_analyzer.py
"""
Étape 1: Analyse de la description du système
"""

import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class SystemAnalyzer:
    """Analyse la description d'un système IA"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    
    def _call_llm(self, prompt):
        """Appelle l'API OpenRouter"""
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "MITRE ATLAS Reasoning Engine"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 500
                },
                timeout=30
            )
            if response.status_code != 200:
                return None
            return response.json()['choices'][0]['message']['content']
        except:
            return None
    
    def analyze(self, description):
        """
        Analyse la description et retourne une structure JSON
        
        Args:
            description: Description textuelle du système
            
        Returns:
            dict: System info structuré
        """
        from .prompts import SYSTEM_ANALYSIS_PROMPT
        
        prompt = SYSTEM_ANALYSIS_PROMPT.format(description=description)
        response = self._call_llm(prompt)
        
        if not response:
            return self._fallback_analysis(description)
        
        try:
            # Nettoyer la réponse
            cleaned = response.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            return json.loads(cleaned)
        except:
            return self._fallback_analysis(description)
    
    def _fallback_analysis(self, description):
        """Analyse de secours en cas d'échec LLM"""
        # Extraction basique par mots-clés
        components = []
        keywords = ['RAG', 'LLM', 'API', 'vector', 'database', 'chatbot',
                   'agent', 'model', 'GPT', 'Cloud', 'AWS']
        
        desc_lower = description.lower()
        for kw in keywords:
            if kw.lower() in desc_lower:
                components.append(kw)
        
        return {
            "system_type": "AI system",
            "components": components if components else ["AI system"],
            "data_types": ["unknown"],
            "access_levels": ["unknown"],
            "deployment": ["unknown"],
            "user_types": ["unknown"]
        }