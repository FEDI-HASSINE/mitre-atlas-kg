# src/reasoning/reasoning_engine.py
"""
Reasoning Engine - Classe principale orchestrant les 5 étapes
"""

import json
from .system_analyzer import SystemAnalyzer
from .component_mapper import ComponentMapper
from .threat_finder import ThreatFinder
from .threat_prioritizer import ThreatPrioritizer
from .report_generator import ReasoningReportGenerator

class ReasoningEngine:
    """Orchestrateur principal du Reasoning Engine"""
    
    def __init__(self):
        self.analyzer = SystemAnalyzer()
        self.mapper = ComponentMapper()
        self.finder = ThreatFinder()
        self.prioritizer = ThreatPrioritizer()
        self.reporter = ReasoningReportGenerator()
    
    def generate_assessment(self, description):
        """
        Génère une évaluation complète des menaces
        
        Args:
            description: Description textuelle du système
            
        Returns:
            dict: {
                'system_info': {...},
                'threats': [...],
                'report': 'markdown...',
                'summary': {...}
            }
        """
        print("\n" + "=" * 60)
        print("🧠 Reasoning Engine - Threat Assessment")
        print("=" * 60)
        
        # Étape 1: Analyser la description
        print("\n📊 Step 1: Analyzing system description...")
        system_info = self.analyzer.analyze(description)
        print(f"   → System: {system_info.get('system_type', 'Unknown')}")
        print(f"   → Components: {system_info.get('components', [])}")
        
        # Étape 2: Mapper les composants
        print("\n📊 Step 2: Mapping components to graph...")
        components = system_info.get('components', [])
        mapped = self.mapper.map_components(components)
        print(f"   → Mapped {len(mapped)} components")
        
        # Étape 3: Trouver les menaces
        print("\n📊 Step 3: Finding threats...")
        threats = self.finder.find_threats(mapped)
        
        # Menaces additionnelles
        system_type = system_info.get('system_type', '')
        if len(threats) < 3:
            additional = self.finder.find_additional_threats(system_type)
            threats.extend(additional)
        
        print(f"   → Found {len(threats)} threats")
        
        # Étape 4: Prioriser
        print("\n📊 Step 4: Prioritizing threats...")
        prioritized = self.prioritizer.prioritize(threats)
        summary = self.prioritizer.get_summary(prioritized)
        print(f"   → Critical: {summary['critical']}, High: {summary['high']}, Medium: {summary['medium']}, Low: {summary['low']}")
        
        # Étape 5: Générer le rapport
        print("\n📊 Step 5: Generating report...")
        report = self.reporter.generate(description, system_info, prioritized)
        print("   → Report generated")
        
        print("\n" + "=" * 60)
        print("✅ Assessment complete!")
        
        return {
            'system_info': system_info,
            'threats': prioritized,
            'report': report,
            'summary': summary
        }
    
    def save_report(self, report, filename=None):
        """Sauvegarde le rapport dans un fichier"""
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/threat_assessment_{timestamp}.md"
        
        import os
        os.makedirs('reports', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📁 Report saved: {filename}")
        return filename
    
    def close(self):
        """Ferme les connexions"""
        self.mapper.close()
        self.finder.close()


# Exemple d'utilisation
if __name__ == "__main__":
    engine = ReasoningEngine()
    
    description = """
    Our system is a RAG-based conversational assistant that helps customer support agents.
    It uses an LLM (GPT-4) to generate responses based on a vector knowledge base.
    The data contains customer information (name, email, purchase history).
    The system is deployed on AWS and accessible via REST API.
    """
    
    result = engine.generate_assessment(description)
    
    print("\n" + "=" * 60)
    print("📄 REPORT")
    print("=" * 60)
    print(result['report'])
    
    engine.save_report(result['report'])
    engine.close()