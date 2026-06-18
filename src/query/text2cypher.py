# src/query/text2cypher.py
import os
import requests
import json
import re
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")


class Text2Cypher:
    def __init__(self):
        self.driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
        self.api_key = OPENROUTER_API_KEY
        self.model = OPENROUTER_MODEL
        self.examples = self._load_examples()
        self._label_cache = None
        self._rel_cache = None
        self._prop_cache = None

    def _load_examples(self):
        return [
            # ============================================================
            # BASIC QUERIES
            # ============================================================
            {
                "question": "List techniques of the Reconnaissance tactic",
                "cypher": "MATCH (t:Technique)-[:BELONGS_TO]->(ta:Tactic {name: 'Reconnaissance'}) RETURN t.name, t.id"
            },
            {
                "question": "What are the techniques of the Initial Access tactic",
                "cypher": "MATCH (t:Technique)-[:BELONGS_TO]->(ta:Tactic {name: 'Initial Access'}) RETURN t.name, t.id"
            },
            {
                "question": "List all tactics",
                "cypher": "MATCH (t:Tactic) RETURN t.name, t.id, t.description"
            },
            {
                "question": "How many techniques exist",
                "cypher": "MATCH (t:Technique) RETURN count(t) as number_of_techniques"
            },

            # ============================================================
            # KEYWORD SEARCH
            # ============================================================
            {
                "question": "techniques with Prompt",
                "cypher": "MATCH (t:Technique) WHERE t.name CONTAINS 'Prompt' RETURN t.name, t.id"
            },
            {
                "question": "techniques with injection",
                "cypher": "MATCH (t:Technique) WHERE toLower(t.name) CONTAINS 'injection' RETURN t.name, t.id"
            },
            {
                "question": "techniques with evasion",
                "cypher": "MATCH (t:Technique) WHERE toLower(t.name) CONTAINS 'evasion' RETURN t.name, t.id"
            },
            {
                "question": "tactics with access",
                "cypher": "MATCH (t:Tactic) WHERE toLower(t.name) CONTAINS 'access' RETURN t.name, t.id"
            },

            # ============================================================
            # REQUESTS WITH MITIGATIONS
            # ============================================================
            {
                "question": "What mitigations exist for LLM Prompt Injection",
                "cypher": "MATCH (m:Mitigation)-[:MITIGATES]->(t:Technique {name: 'LLM Prompt Injection'}) RETURN m.name, m.id"
            },
            {
                "question": "What mitigations exist for the Prompt Injection technique",
                "cypher": "MATCH (m:Mitigation)-[:MITIGATES]->(t:Technique) WHERE t.name CONTAINS 'Prompt' RETURN m.name, t.name, t.id"
            },
            {
                "question": "What mitigations apply to a technique",
                "cypher": "MATCH (m:Mitigation)-[:MITIGATES]->(t:Technique) RETURN m.name, t.name LIMIT 10"
            },
            {
                "question": "Which techniques have mitigations",
                "cypher": "MATCH (m:Mitigation)-[:MITIGATES]->(t:Technique) RETURN DISTINCT t.name, t.id"
            },
            {
                "question": "mitigations for developers",
                "cypher": "MATCH (m:Mitigation {owned_by: 'application_developers'}) RETURN m.name, m.id"
            },

            # ============================================================
            # REQUESTS WITH MATURITY
            # ============================================================
            {
                "question": "Which techniques have demonstrated maturity",
                "cypher": "MATCH (t:Technique {maturity: 'demonstrated'}) RETURN t.name, t.id"
            },
            {
                "question": "techniques with realized maturity",
                "cypher": "MATCH (t:Technique {maturity: 'realized'}) RETURN t.name, t.id"
            },
            {
                "question": "techniques with feasible maturity",
                "cypher": "MATCH (t:Technique {maturity: 'feasible'}) RETURN t.name, t.id"
            },

            # ============================================================
            # REQUESTS WITH CASE STUDIES
            # ============================================================
            {
                "question": "Which case studies illustrate Prompt Injection",
                "cypher": "MATCH (c:CaseStudy)-[:ILLUSTRATES]->(t:Technique) WHERE t.name CONTAINS 'Prompt' RETURN c.name, c.summary"
            },
            {
                "question": "case studies for the Reconnaissance technique",
                "cypher": "MATCH (c:CaseStudy)-[:ILLUSTRATES]->(t:Technique)-[:BELONGS_TO]->(ta:Tactic {name: 'Reconnaissance'}) RETURN c.name, c.summary"
            },

            # ============================================================
            # COMPLEX QUERIES
            # ============================================================
            {
                "question": "Techniques and their tactics",
                "cypher": "MATCH (t:Technique)-[:BELONGS_TO]->(ta:Tactic) RETURN ta.name as Tactic, collect(t.name) as Techniques"
            },
            {
                "question": "Tactics with number of techniques",
                "cypher": "MATCH (t:Technique)-[:BELONGS_TO]->(ta:Tactic) RETURN ta.name, count(t) as number_of_techniques ORDER BY number_of_techniques DESC"
            },
            {
                "question": "mitigations and the techniques they protect",
                "cypher": "MATCH (m:Mitigation)-[:MITIGATES]->(t:Technique) RETURN m.name, collect(t.name) as protected_techniques"
            },

            # ============================================================
            # ACTORS (USES)
            # ============================================================
            {
                "question": "actors who use LLM Prompt Injection",
                "cypher": "MATCH (a:Actor)-[:USES]->(t:Technique {name: 'LLM Prompt Injection'}) RETURN a.name"
            },
            {
                "question": "techniques used by APT28",
                "cypher": "MATCH (a:Actor {name: 'APT28'})-[:USES]->(t:Technique) RETURN t.name, t.id"
            },
            {
                "question": "which actors use critical techniques",
                "cypher": "MATCH (a:Actor)-[:USES]->(t:Technique {severity: 'critical'}) RETURN DISTINCT a.name"
            },

            # ============================================================
            # COMPONENTS (TARGETS)
            # ============================================================
            {
                "question": "components targeted by LLM Prompt Injection",
                "cypher": "MATCH (t:Technique {name: 'LLM Prompt Injection'})-[:TARGETS]->(c:Component) RETURN c.name"
            },
            {
                "question": "techniques that target RAG systems",
                "cypher": "MATCH (t:Technique)-[:TARGETS]->(c:Component) WHERE c.name CONTAINS 'RAG' RETURN t.name, t.id"
            },
            {
                "question": "techniques that target ChatGPT",
                "cypher": "MATCH (t:Technique)-[:TARGETS]->(c:Component {name: 'OpenAI ChatGPT'}) RETURN t.name, t.id"
            },

            # ============================================================
            # SEVERITY AND CVSS
            # ============================================================
            {
                "question": "techniques with critical severity",
                "cypher": "MATCH (t:Technique {severity: 'critical'}) RETURN t.name, t.id, t.cvss_score"
            },
            {
                "question": "techniques with high severity",
                "cypher": "MATCH (t:Technique {severity: 'high'}) RETURN t.name, t.id, t.cvss_score"
            },
            {
                "question": "techniques with CVSS greater than 8",
                "cypher": "MATCH (t:Technique) WHERE t.cvss_score > 8 RETURN t.name, t.id, t.cvss_score ORDER BY t.cvss_score DESC"
            },

            # ============================================================
            # REQUESTS WITH OPTIONAL MATCH
            # ============================================================
            {
                "question": "techniques with their targeted components and mitigations",
                "cypher": "MATCH (t:Technique)-[:TARGETS]->(c:Component) OPTIONAL MATCH (m:Mitigation)-[:MITIGATES]->(t) RETURN t.name, COLLECT(DISTINCT c.name) as targets, COLLECT(DISTINCT m.name) as mitigations LIMIT 10"
            },
            {
                "question": "techniques targeting RAG and mitigations for developers",
                "cypher": "MATCH (t:Technique)-[:TARGETS]->(c:Component) WHERE c.name CONTAINS 'RAG' OPTIONAL MATCH (m:Mitigation {owned_by: 'application_developers'})-[:MITIGATES]->(t) RETURN t.name, COLLECT(DISTINCT c.name) as targets, COLLECT(DISTINCT m.name) as mitigations"
            },
            {
                "question": "which techniques have critical severity and mitigations",
                "cypher": "MATCH (t:Technique {severity: 'critical'}) OPTIONAL MATCH (m:Mitigation)-[:MITIGATES]->(t) RETURN t.name, t.cvss_score, COLLECT(m.name) as mitigations"
            },
            {
                "question": "actors using techniques that target inference",
                "cypher": "MATCH (a:Actor)-[:USES]->(t:Technique)-[:TARGETS]->(c:Component) WHERE c.name CONTAINS 'inference' OR c.name CONTAINS 'RAG' RETURN a.name, COLLECT(DISTINCT t.name) as techniques"
            },

            # ============================================================
            # PRECEDES RELATIONSHIPS
            # ============================================================
            {
                "question": "Which techniques precede LLM Prompt Injection",
                "cypher": "MATCH (t1:Technique)-[:PRECEDES]->(t2:Technique {name: 'LLM Prompt Injection'}) RETURN t1.name, t1.id"
            },
            {
                "question": "Which techniques follow LLM Prompt Crafting",
                "cypher": "MATCH (t1:Technique {name: 'LLM Prompt Crafting'})-[:PRECEDES]->(t2:Technique) RETURN t2.name, t2.id"
            },
            {
                "question": "Complete attack chain for Prompt Injection",
                "cypher": "MATCH path = (start:Technique)-[:PRECEDES*]->(end:Technique {name: 'LLM Prompt Injection'}) RETURN [n in nodes(path) | n.name] as chain"
            },
            {
                "question": "Visualize the RAG attack chain",
                "cypher": "MATCH path = (start:Technique {name: 'LLM Prompt Crafting'})-[:PRECEDES*]->(end:Technique {name: 'Exfiltration via Cyber Means'}) RETURN [n in nodes(path) | n.name] as attack_chain"
            },

            # ============================================================
            # COMBINED QUERIES
            # ============================================================
            {
                "question": "techniques targeting RAG with critical severity",
                "cypher": "MATCH (t:Technique)-[:TARGETS]->(c:Component) WHERE c.name CONTAINS 'RAG' AND t.severity = 'critical' RETURN t.name, t.id, t.cvss_score"
            },
            {
                "question": "mitigations for developers for critical techniques",
                "cypher": "MATCH (m:Mitigation {owned_by: 'application_developers'})-[:MITIGATES]->(t:Technique {severity: 'critical'}) RETURN m.name, t.name"
            },
            {
                "question": "actors and components for LLM Prompt Injection",
                "cypher": "MATCH (a:Actor)-[:USES]->(t:Technique {name: 'LLM Prompt Injection'}) MATCH (t)-[:TARGETS]->(c:Component) RETURN a.name, collect(c.name) as components"
            }
        ]

    def _get_schema_info(self):
        """Retrieve Neo4j schema information with caching"""
        if self._label_cache is None:
            try:
                with self.driver.session() as session:
                    # Labels
                    result = session.run("CALL db.labels()")
                    self._label_cache = [r['label'] for r in result]
                    
                    # Relationships
                    result = session.run("CALL db.relationshipTypes()")
                    self._rel_cache = [r['relationshipType'] for r in result]
                    
                    # Technique properties
                    result = session.run("""
                        MATCH (t:Technique) 
                        RETURN keys(t) as properties 
                        LIMIT 1
                    """)
                    for r in result:
                        self._prop_cache = r['properties']
            except:
                self._label_cache = []
                self._rel_cache = []
                self._prop_cache = []
        
        return self._label_cache, self._rel_cache, self._prop_cache

    def _build_prompt(self, question):
        prompt = """You are a Neo4j Cypher expert. Translate the natural language question into a VALID Cypher query.

NEO4J SCHEMA :
- Nodes : 
  • Tactic : {id, name, description, created_date, modified_date}
  • Technique : {id, name, description, maturity, severity, cvss_score, first_seen, last_seen, last_updated}
  • Subtechnique : {id, name, description, subtechnique_of}
  • Mitigation : {id, name, description, mitigation_category, ml_lifecycle, owned_by}
  • CaseStudy : {id, name, summary, incident_date, reporter, actor, target, case_study_type}
  • Actor : {name}
  • Component : {name}

- Relationships :
  • BELONGS_TO : (Technique)-[:BELONGS_TO]->(Tactic)
  • SUBTECHNIQUE_OF : (Subtechnique)-[:SUBTECHNIQUE_OF]->(Technique)
  • MITIGATES : (Mitigation)-[:MITIGATES]->(Technique)
  • ILLUSTRATES : (CaseStudy)-[:ILLUSTRATES]->(Technique)
  • USES : (Actor)-[:USES]->(Technique)
  • TARGETS : (Technique)-[:TARGETS]->(Component)
  • PRECEDES : (Technique)-[:PRECEDES]->(Technique)

STRICT CYPHER SYNTAX RULES (MUST BE RESPECTED) :
1. The WHERE keyword can only appear after MATCH, OPTIONAL MATCH, or WITH.
2. The WHERE keyword can NEVER appear after RETURN, ORDER BY, SKIP, LIMIT.
3. To filter results after a RETURN, use WITH before the RETURN.
4. For queries with multiple conditions, use multiple MATCH or WITH.
5. Use OPTIONAL MATCH for relationships that may not exist.
6. Use COLLECT(DISTINCT ...) to group without duplicates.

IMPORTANT RULES :
1. Use CONTAINS for keyword search (e.g., WHERE t.name CONTAINS 'Prompt')
2. Use toLower() for case-insensitive search
3. Available properties : severity (critical/high/medium/low), cvss_score (float), owned_by (string)
4. Respond ONLY with the Cypher query, no explanation, no markdown, no backticks

CHAIN OF THOUGHT - Think step by step :

Step 1: Analyze the question
- What is the main subject ?
- What are the conditions ?

Step 2: Identify required nodes
- Which nodes are needed ?
- What are their properties ?

Step 3: Identify relationships
- Which relationships connect these nodes ?

Step 4: Build MATCH
- Start with the main node

Step 5: Add WHERE
- Filter by properties

Step 6: Build RETURN
- What information to return ?

REASONING EXAMPLES :

Question: "Which techniques target RAG systems ?"
Reasoning:
1. Subject: Technique, condition: targets RAG
2. Nodes: Technique, Component
3. Relationships: TARGETS
4. MATCH: (t:Technique)-[:TARGETS]->(c:Component)
5. WHERE: c.name CONTAINS 'RAG'
6. RETURN: t.name, t.id

Cypher: MATCH (t:Technique)-[:TARGETS]->(c:Component) WHERE c.name CONTAINS 'RAG' RETURN t.name, t.id

Question: "Techniques with critical severity and their mitigations"
Reasoning:
1. Subject: Technique, condition: severity = critical
2. Nodes: Technique, Mitigation
3. Relationships: MITIGATES (optional)
4. MATCH: (t:Technique {severity: 'critical'})
5. OPTIONAL MATCH: (m:Mitigation)-[:MITIGATES]->(t)
6. RETURN: t.name, t.id, COLLECT(DISTINCT m.name)

Cypher: MATCH (t:Technique {severity: 'critical'}) OPTIONAL MATCH (m:Mitigation)-[:MITIGATES]->(t) RETURN t.name, t.id, COLLECT(DISTINCT m.name)

"""
        for ex in self.examples:
            prompt += f"Question: {ex['question']}\nCypher: {ex['cypher']}\n\n"

        prompt += f"Question: {question}\n"
        prompt += "Reasoning:\n"
        prompt += "1. Subject: "
        prompt += "2. Nodes: "
        prompt += "3. Relationships: "
        prompt += "4. MATCH: "
        prompt += "5. WHERE: "
        prompt += "6. RETURN: "
        prompt += "\nCypher:"
        return prompt

    def text_to_cypher(self, question):
        prompt = self._build_prompt(question)

        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "MITRE ATLAS KG"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0,
                    "max_tokens": 500
                },
                timeout=30
            )

            if response.status_code != 200:
                return f"API ERROR: {response.status_code} - {response.text}"

            result = response.json()
            cypher = result['choices'][0]['message']['content'].strip()
            cypher = cypher.replace('```cypher', '').replace('```', '').strip()
            
            # Clean reasoning if present
            if 'Cypher:' in cypher:
                cypher = cypher.split('Cypher:')[-1].strip()
            
            return cypher

        except requests.exceptions.Timeout:
            return "ERROR: Timeout - API not responding"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def validate_cypher(self, cypher):
        try:
            with self.driver.session() as session:
                session.run(f"EXPLAIN {cypher}")
            return True, None
        except Exception as e:
            return False, str(e)

    def validate_semantic(self, cypher):
        """
        Verify that the Cypher query is semantically correct
        - Verify that the labels exist
        - Verify that the relationships exist
        """
        try:
            labels, rels, _ = self._get_schema_info()
            
            # Extract mentioned labels
            label_pattern = r'MATCH\s*\([^)]*:(\w+)'
            found_labels = re.findall(label_pattern, cypher)
            
            # Extract mentioned relationships
            rel_pattern = r'\[[^)]*:(\w+)\]'
            found_rels = re.findall(rel_pattern, cypher)
            
            errors = []
            
            # Check labels
            for label in found_labels:
                if label not in labels:
                    errors.append(f"Label '{label}' does not exist in the database")
            
            # Check relationships
            for rel in found_rels:
                if rel not in rels:
                    errors.append(f"Relationship '{rel}' does not exist in the database")
            
            if errors:
                return False, "; ".join(errors)
            
            return True, None
            
        except Exception as e:
            return False, str(e)

    def execute(self, cypher):
        try:
            safe_cypher = self.sanitize_cypher(cypher)
            with self.driver.session() as session:
                result = session.run(safe_cypher)
                return [record.data() for record in result]
        except Exception as e:
            return {"error": str(e)}
    
    def sanitize_cypher(self, cypher):
        """
        Sanitize and secure Cypher query before execution.
        - Read-only mode: block dangerous keywords
        - Enforce LIMIT
        - Validate syntax
        """
        #1. Block dangerous keywords
        dangerous_keywords = [
            'CREATE', 'DELETE', 'SET', 'REMOVE', 'MERGE',
            'DROP', 'LOAD CSV', 'CALL dbms', 'CALL apoc',
            'DROP CONSTRAINT', 'DROP INDEX', 'CREATE CONSTRAINT',
            'CREATE INDEX', 'CREATE DATABASE', 'DROP DATABASE'
        ]
        
        cypher_upper = cypher.upper()
        for keyword in dangerous_keywords:
            if keyword in cypher_upper:
                raise ValueError(f"Keyword '{keyword}' is not allowed (read-only mode)")
        
        # 2. Check allowed labels
        allowed_labels = ['Tactic', 'Technique', 'Subtechnique', 'Mitigation', 
                         'CaseStudy', 'Actor', 'Component']
        
        # Simple label extraction
        import re
        label_pattern = r'MATCH\s*\([^)]*:(\w+)'
        found_labels = re.findall(label_pattern, cypher)
        
        for label in found_labels:
            if label not in allowed_labels:
                raise ValueError(f"Label '{label}' is not allowed")
        
        #3. Enforce LIMIT if absent
        if 'LIMIT' not in cypher_upper and 'COUNT' not in cypher_upper and 'RETURN' in cypher_upper:
            cypher = cypher + ' LIMIT 100'
        
        #4. Block multi-step requests
        if ';' in cypher:
            # Split and keep only the first query
            cypher = cypher.split(';')[0]
        
        return cypher
    
    def ask(self, question):
        print(f"\nQuestion: {question}")

        cypher = self.text_to_cypher(question)
        if cypher.startswith("ERROR:"):
            print(f"{cypher}")
            return {"error": cypher}

        print(f"Cypher generated: {cypher}")

        # 1. Syntax validation (EXPLAIN)
        valid, error = self.validate_cypher(cypher)
        if not valid:
            print(f"Invalid Cypher (syntax): {error}")
            return {"error": f"Invalid Cypher: {error}", "cypher": cypher}

        # 2. Semantic Validation
        valid, semantic_error = self.validate_semantic(cypher)
        if not valid:
            print(f"Semantic warning: {semantic_error}")

        results = self.execute(cypher)
        if isinstance(results, dict) and "error" in results:
            print(f"Execution error: {results['error']}")
            return {"error": results["error"], "cypher": cypher}

        print(f"Results: {len(results) if isinstance(results, list) else 0} entries found")
        
        result_obj = {"cypher": cypher, "results": results}
        if semantic_error:
            result_obj["semantic_warning"] = semantic_error
        
        return result_obj

    def close(self):
        self.driver.close()


if __name__ == "__main__":
    print("Text2Cypher Test with OpenRouter")
    print("=" * 50)

    t2c = Text2Cypher()

    questions = [
        "techniques with Prompt",
        "techniques with evasion",
        "what mitigations for LLM Prompt Injection",
        "Tactics with number of techniques",
        "case studies for the Reconnaissance technique",
        "actors who use LLM Prompt Injection",
        "techniques used by APT28",
        "techniques that target RAG systems",
        "components targeted by LLM Prompt Injection",
        "techniques with critical severity",
        "techniques with CVSS greater than 8",
        "techniques targeting RAG with critical severity",
        "mitigations for developers for critical techniques",
        "techniques targeting RAG and mitigations for developers",
        "Which techniques precede LLM Prompt Injection",
        "Complete attack chain for Prompt Injection"
    ]

    for q in questions:
        result = t2c.ask(q)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Success: {len(result.get('results', []))} results")
            if "semantic_warning" in result:
                print(f"Warning: {result['semantic_warning']}")
        print("-" * 50)

    t2c.close()