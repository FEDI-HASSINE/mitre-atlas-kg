# demo_queries.py
"""
MITRE ATLAS Knowledge Graph - Example Queries
Démonstration des questions réelles que le graphe peut répondre
"""

from src.query.text2cypher import Text2Cypher
import json

def demo():
    t2c = Text2Cypher()
    
    queries = [
        {
            "category": "Basic Discovery",
            "question": "List all tactics in MITRE ATLAS",
            "description": "Identify the 16 high-level adversary objectives"
        },
        {
            "category": "Technique Discovery", 
            "question": "List techniques belonging to the Reconnaissance tactic",
            "description": "Find specific methods used during adversary reconnaissance"
        },
        {
            "category": "Mitigation Analysis",
            "question": "What mitigations exist for LLM Prompt Injection?",
            "description": "Identify defensive controls against prompt injection attacks"
        },
        {
            "category": "Actor Intelligence",
            "question": "Which threat actors use LLM Prompt Injection?",
            "description": "Map adversaries to techniques they employ"
        },
        {
            "category": "Target Analysis",
            "question": "Which techniques target RAG-based systems?",
            "description": "Understand which attack methods affect RAG architectures"
        },
        {
            "category": "Risk Assessment",
            "question": "Techniques with critical severity and their mitigations",
            "description": "Prioritize highest-risk techniques and their controls"
        },
        {
            "category": "Complex Analysis",
            "question": "Techniques targeting RAG with developer-owned mitigations",
            "description": "Find techniques targeting RAG and controls owned by developers"
        },
        {
            "category": "Attribution",
            "question": "What techniques does APT28 use?",
            "description": "Understand the attack patterns of known threat actors"
        },
        {
            "category": "Compliance",
            "question": "Mitigations owned by application developers",
            "description": "Identify controls that developers must implement"
        }
    ]
    
    print("=" * 80)
    print("MITRE ATLAS Knowledge Graph - Query Demo")
    print("Demonstrating real-world questions the graph can answer")
    print("=" * 80)
    
    results_summary = []
    
    for i, q in enumerate(queries, 1):
        print(f"\nQuery {i}: {q['category']}")
        print(f"   Question: {q['question']}")
        print(f"   Purpose: {q['description']}")
        print("-" * 50)
        
        result = t2c.ask(q['question'])
        
        if "error" in result:
            print(f" Error: {result['error']}")
            results_summary.append({
                "query": q['question'],
                "status": "error",
                "count": 0
            })
        else:
            count = len(result.get('results', []))
            print(f" Found {count} results")
            
            # Show first 3 results as sample
            if count > 0:
                print("   Sample results:")
                for j, r in enumerate(result['results'][:3], 1):
                    print(f"      {j}. {r}")
                if count > 3:
                    print(f"      ... and {count - 3} more")
            
            results_summary.append({
                "query": q['question'],
                "status": "success",
                "count": count
            })
        
        print("-" * 50)
    
    # Summary
    print("\n" + "=" * 80)
    print("Query Summary")
    print("=" * 80)
    print(f"Total queries: {len(results_summary)}")
    print(f"Successful: {sum(1 for r in results_summary if r['status'] == 'success')}")
    print(f"Errors: {sum(1 for r in results_summary if r['status'] == 'error')}")
    print("\nResults by query:")
    for r in results_summary:
        print(f"   {r['query'][:50]}... → {r['count']} results")
    
    t2c.close()

if __name__ == "__main__":
    demo()