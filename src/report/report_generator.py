# src/report/report_generator.py
import os
import json
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.query.text2cypher import Text2Cypher


class ReportGenerator:
    def __init__(self):
        self.t2c = Text2Cypher()
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
        self.max_items = 15
        self.max_workers = 5  # Nombre de workers parallèles
        self.min_relevance_score = 40  # Score minimum pour garder un item

    def _call_llm(self, prompt, temperature=0.3):
        """Call OpenRouter API"""
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "MITRE ATLAS Report Generator"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": 800
                },
                timeout=30
            )

            if response.status_code != 200:
                return f"API ERROR: {response.status_code}"

            result = response.json()
            return result['choices'][0]['message']['content'].strip()

        except Exception as e:
            return f"ERROR: {str(e)}"

    def _format_graph_results(self, results):
        """Format graph results as readable text"""
        if not results:
            return "No results found."

        formatted = []
        for i, item in enumerate(results, 1):
            if isinstance(item, dict):
                pairs = []
                for key, value in item.items():
                    if isinstance(value, list):
                        value_str = ", ".join(value)
                    else:
                        value_str = str(value)
                    clean_key = key.split('.')[-1] if '.' in key else key
                    pairs.append(f"{clean_key}: {value_str}")
                formatted.append(f"{i}. " + " | ".join(pairs))
            else:
                formatted.append(f"{i}. {item}")

        return "\n".join(formatted)

    def _generate_citations(self, results):
        """Generate traceable citations to graph elements"""
        citations = []
        for i, item in enumerate(results, 1):
            if isinstance(item, dict):
                tech_id = item.get('t.id') or item.get('id') or f"Item_{i}"
                tech_name = item.get('t.name') or item.get('name') or "Technique"
                citations.append(f"[{i}] {tech_name} ({tech_id})")
        return "\n".join(citations)

    def _get_current_date(self):
        """Return formatted current date"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ============================================================
    # PHASE MAP: Résumé + Score de pertinence (parallèle)
    # ============================================================
    def _map_item(self, item):
        """
        Map un seul item → résumé + score de pertinence
        (exécuté en parallèle pour plusieurs items)
        """
        prompt = f"""
        Analyze the following MITRE ATLAS item and provide:
        1. A one-sentence summary
        2. A relevance score (0-100) for threat assessment reports

        Item: {item}

        Return EXACTLY in this JSON format:
        {{"summary": "your one-sentence summary here", "relevance_score": 85}}
        """
        response = self._call_llm(prompt, temperature=0.2)
        
        try:
            # Essayer de parser le JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return {
                    'item': item,
                    'summary': data.get('summary', str(item)[:100]),
                    'relevance_score': min(100, max(0, int(data.get('relevance_score', 50))))
                }
        except:
            pass
        
        # Fallback
        return {
            'item': item,
            'summary': str(item)[:150],
            'relevance_score': 50
        }

    def _map_phase(self, items):
        """
        Map Phase: Traiter tous les items en parallèle
        Retourne: liste de (item, summary, score)
        """
        print(f"   📊 MAP: Génération de {len(items)} résumés en parallèle...")
        
        mapped_results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._map_item, item): item for item in items}
            
            for future in as_completed(futures):
                result = future.result()
                mapped_results.append(result)
                print(f"      ✅ Item traité (score: {result['relevance_score']})")
        
        return mapped_results

    # ============================================================
    # PHASE FILTER: Filtrer par pertinence
    # ============================================================
    def _filter_phase(self, mapped_results):
        """
        Filter Phase: Garder seulement les items avec score >= min_relevance_score
        """
        print(f"   📊 FILTER: Filtrage des items (score >= {self.min_relevance_score})...")
        
        filtered = [r for r in mapped_results if r['relevance_score'] >= self.min_relevance_score]
        filtered.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        print(f"      ✅ {len(filtered)} items conservés sur {len(mapped_results)}")
        return filtered

    # ============================================================
    # PHASE REDUCE: Synthèse finale
    # ============================================================
    def _reduce_phase(self, filtered_items, question):
        """
        Reduce Phase: Synthèse finale à partir des meilleurs items
        """
        print("   📊 REDUCE: Synthèse finale...")
        
        if not filtered_items:
            return "No relevant items found for this query."
        
        # Prendre les 10 meilleurs items pour la synthèse
        top_items = filtered_items[:10]
        
        # Construire les résumés avec scores
        summary_lines = []
        for r in top_items:
            summary_lines.append(f"- {r['summary']} (score: {r['relevance_score']})")
        
        reduce_prompt = f"""
        You are an AI security expert. Based on the following summaries (sorted by relevance), answer the question:

        **Question:** {question}

        **Summaries (sorted by relevance):**
        {chr(10).join(summary_lines)}

        **Instructions:**
        1. Synthesize the most important information
        2. Structure your response with clear sections
        3. Cite techniques by their name and ID
        4. Use a professional, factual tone
        5. Write in ENGLISH
        6. Be concise but comprehensive
        7. Prioritize the most relevant sources

        **Important:** Only include information that is directly supported by the summaries.
        """
        
        return self._call_llm(reduce_prompt, temperature=0.4)

    # ============================================================
    # GÉNÉRATION DU RAPPORT COMPLET (avec Map-Reduce)
    # ============================================================
    def generate_report(self, question, include_citations=True):
        """
        Generate a structured report from a natural language question
        avec architecture Map-Reduce (inspirée de GraphRAG)

        Args:
            question: Natural language question
            include_citations: Include traceable citations

        Returns:
            Structured markdown report
        """
        print(f"\n📊 Generating report for: {question}")
        print("=" * 60)

        # 1. Execute query on graph
        result = self.t2c.ask(question)

        if "error" in result:
            return f"Error: {result['error']}"

        data = result["results"]
        cypher = result.get("cypher", "N/A")

        if not data:
            return "No results found for this query."

        # 2. Limit items
        items = data[:self.max_items]
        print(f"📥 {len(items)} items à traiter")

        # 3. PHASE MAP: Générer des résumés en parallèle
        mapped_results = self._map_phase(items)

        # 4. PHASE FILTER: Garder seulement les items pertinents
        filtered = self._filter_phase(mapped_results)

        # 5. PHASE REDUCE: Synthèse finale
        final_report = self._reduce_phase(filtered, question)

        # 6. Build final report with citations
        report = []

        # Header
        report.append(f"# AI Threat Analysis Report\n")
        report.append(f"**Question:** {question}\n")
        report.append(f"**Generated:** {self._get_current_date()}\n")
        report.append("---\n")

        # Executive Summary
        report.append("## Executive Summary\n")
        report.append(final_report)
        report.append("\n")

        # Detailed Results (avec scores de pertinence)
        report.append("## Detailed Results (with Relevance Scores)\n")
        if filtered:
            report.append("| # | Summary | Relevance Score |")
            report.append("|---|---------|-----------------|")
            for i, r in enumerate(filtered[:10], 1):
                summary = r['summary'][:80] + "..." if len(r['summary']) > 80 else r['summary']
                report.append(f"| {i} | {summary} | {r['relevance_score']} |")
            report.append("")
        else:
            report.append("No items met the minimum relevance threshold.\n")

        # Source Data
        report.append("## Source Data\n")
        report.append("```")
        report.append(self._format_graph_results(items))
        report.append("```\n")

        # Traceable Citations
        if include_citations:
            report.append("## Traceable Citations\n")
            report.append("The information above is sourced from the MITRE ATLAS knowledge graph:\n")
            report.append(self._generate_citations(items))
            report.append("\n")
            report.append("*Citations reference MITRE ATLAS technique IDs present in the graph.*\n")

        # Cypher Query
        report.append("## Cypher Query Executed\n")
        report.append("```cypher")
        report.append(cypher)
        report.append("```\n")

        # Footer
        report.append("---\n")
        report.append(f"*Report generated with Map-Reduce pipeline (inspired by GraphRAG).*\n")
        report.append(f"*Items analyzed: {len(items)} | Filtered: {len(filtered)} | Min relevance: {self.min_relevance_score}*\n")
        report.append(f"*Report automatically generated by the MITRE ATLAS Knowledge Graph system.*\n")

        print("✅ Report generated successfully!")
        print(f"   📊 MAP: {len(items)} items → FILTER: {len(filtered)} items → REDUCE: synthèse")
        print("=" * 60)

        return "\n".join(report)

    def save_report(self, report, output_path):
        """Save report to file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📁 Report saved: {output_path}")

    def close(self):
        self.t2c.close()


if __name__ == "__main__":
    print("🚀 ReportGenerator Test (Map-Reduce version)")
    print("=" * 60)

    generator = ReportGenerator()

    # Test 1: Critical techniques
    question = "techniques with critical severity and their mitigations"
    report = generator.generate_report(question, include_citations=True)
    print(report)
    generator.save_report(report, "reports/report_critical_techniques.md")

    # Test 2: RAG techniques
    print("\n" + "=" * 60)
    question2 = "techniques targeting RAG and mitigations for developers"
    report2 = generator.generate_report(question2, include_citations=True)
    print(report2)
    generator.save_report(report2, "reports/report_rag_techniques.md")

    generator.close()