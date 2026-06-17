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
            # REQUÊTES DE BASE
            # ============================================================
            {
                "question": "Liste les techniques de la tactique Reconnaissance",
                "cypher": "MATCH (t:Technique)-[:BELONGS_TO]->(ta:Tactic {name: 'Reconnaissance'}) RETURN t.name, t.id"
            },
            {
                "question": "Quelles sont les techniques de la tactique Initial Access",
                "cypher": "MATCH (t:Technique)-[:BELONGS_TO]->(ta:Tactic {name: 'Initial Access'}) RETURN t.name, t.id"
            },
            {
                "question": "Liste toutes les tactiques",
                "cypher": "MATCH (t:Tactic) RETURN t.name, t.id, t.description"
            },
            {
                "question": "Combien de techniques existent",
                "cypher": "MATCH (t:Technique) RETURN count(t) as nombre_techniques"
            },

            # ============================================================
            # RECHERCHE PAR MOT-CLÉ
            # ============================================================
            {
                "question": "techniques avec Prompt",
                "cypher": "MATCH (t:Technique) WHERE t.name CONTAINS 'Prompt' RETURN t.name, t.id"
            },
            {
                "question": "techniques avec injection",
                "cypher": "MATCH (t:Technique) WHERE toLower(t.name) CONTAINS 'injection' RETURN t.name, t.id"
            },
            {
                "question": "techniques avec evasion",
                "cypher": "MATCH (t:Technique) WHERE toLower(t.name) CONTAINS 'evasion' RETURN t.name, t.id"
            },
            {
                "question": "tactiques avec access",
                "cypher": "MATCH (t:Tactic) WHERE toLower(t.name) CONTAINS 'access' RETURN t.name, t.id"
            },

            # ============================================================
            # REQUÊTES AVEC MITIGATIONS
            # ============================================================
            {
                "question": "Quelles mitigations pour LLM Prompt Injection",
                "cypher": "MATCH (m:Mitigation)-[:MITIGATES]->(t:Technique {name: 'LLM Prompt Injection'}) RETURN m.name, m.id"
            },
            {
                "question": "Quelles mitigations pour la technique Prompt Injection",
                "cypher": "MATCH (m:Mitigation)-[:MITIGATES]->(t:Technique) WHERE t.name CONTAINS 'Prompt' RETURN m.name, t.name, t.id"
            },
            {
                "question": "Quelles mitigations s'appliquent à une technique",
                "cypher": "MATCH (m:Mitigation)-[:MITIGATES]->(t:Technique) RETURN m.name, t.name LIMIT 10"
            },
            {
                "question": "Quelles techniques ont des mitigations",
                "cypher": "MATCH (m:Mitigation)-[:MITIGATES]->(t:Technique) RETURN DISTINCT t.name, t.id"
            },
            {
                "question": "mitigations pour les développeurs",
                "cypher": "MATCH (m:Mitigation {owned_by: 'application_developers'}) RETURN m.name, m.id"
            },

            # ============================================================
            # REQUÊTES AVEC MATURITÉ
            # ============================================================
            {
                "question": "Quelles techniques ont une maturité demonstrated",
                "cypher": "MATCH (t:Technique {maturity: 'demonstrated'}) RETURN t.name, t.id"
            },
            {
                "question": "techniques avec maturité realized",
                "cypher": "MATCH (t:Technique {maturity: 'realized'}) RETURN t.name, t.id"
            },
            {
                "question": "techniques avec maturité feasible",
                "cypher": "MATCH (t:Technique {maturity: 'feasible'}) RETURN t.name, t.id"
            },

            # ============================================================
            # REQUÊTES AVEC CASE STUDIES
            # ============================================================
            {
                "question": "Quels case studies illustrent Prompt Injection",
                "cypher": "MATCH (c:CaseStudy)-[:ILLUSTRATES]->(t:Technique) WHERE t.name CONTAINS 'Prompt' RETURN c.name, c.summary"
            },
            {
                "question": "case studies pour la technique Reconnaissance",
                "cypher": "MATCH (c:CaseStudy)-[:ILLUSTRATES]->(t:Technique)-[:BELONGS_TO]->(ta:Tactic {name: 'Reconnaissance'}) RETURN c.name, c.summary"
            },

            # ============================================================
            # REQUÊTES COMPLEXES
            # ============================================================
            {
                "question": "Techniques et leurs tactiques",
                "cypher": "MATCH (t:Technique)-[:BELONGS_TO]->(ta:Tactic) RETURN ta.name as Tactique, collect(t.name) as Techniques"
            },
            {
                "question": "Tactiques avec nombre de techniques",
                "cypher": "MATCH (t:Technique)-[:BELONGS_TO]->(ta:Tactic) RETURN ta.name, count(t) as nombre_techniques ORDER BY nombre_techniques DESC"
            },
            {
                "question": "mitigations et les techniques qu'elles protègent",
                "cypher": "MATCH (m:Mitigation)-[:MITIGATES]->(t:Technique) RETURN m.name, collect(t.name) as techniques_protegees"
            },

            # ============================================================
            # ACTEURS (USES)
            # ============================================================
            {
                "question": "acteurs qui utilisent LLM Prompt Injection",
                "cypher": "MATCH (a:Actor)-[:USES]->(t:Technique {name: 'LLM Prompt Injection'}) RETURN a.name"
            },
            {
                "question": "techniques utilisées par APT28",
                "cypher": "MATCH (a:Actor {name: 'APT28'})-[:USES]->(t:Technique) RETURN t.name, t.id"
            },
            {
                "question": "quels acteurs utilisent des techniques critiques",
                "cypher": "MATCH (a:Actor)-[:USES]->(t:Technique {severity: 'critical'}) RETURN DISTINCT a.name"
            },

            # ============================================================
            # COMPOSANTS (TARGETS)
            # ============================================================
            {
                "question": "composants ciblés par LLM Prompt Injection",
                "cypher": "MATCH (t:Technique {name: 'LLM Prompt Injection'})-[:TARGETS]->(c:Component) RETURN c.name"
            },
            {
                "question": "techniques qui ciblent les systèmes RAG",
                "cypher": "MATCH (t:Technique)-[:TARGETS]->(c:Component) WHERE c.name CONTAINS 'RAG' RETURN t.name, t.id"
            },
            {
                "question": "techniques qui ciblent ChatGPT",
                "cypher": "MATCH (t:Technique)-[:TARGETS]->(c:Component {name: 'OpenAI ChatGPT'}) RETURN t.name, t.id"
            },

            # ============================================================
            # SÉVÉRITÉ ET CVSS
            # ============================================================
            {
                "question": "techniques avec sévérité critical",
                "cypher": "MATCH (t:Technique {severity: 'critical'}) RETURN t.name, t.id, t.cvss_score"
            },
            {
                "question": "techniques avec sévérité high",
                "cypher": "MATCH (t:Technique {severity: 'high'}) RETURN t.name, t.id, t.cvss_score"
            },
            {
                "question": "techniques avec CVSS supérieur à 8",
                "cypher": "MATCH (t:Technique) WHERE t.cvss_score > 8 RETURN t.name, t.id, t.cvss_score ORDER BY t.cvss_score DESC"
            },

            # ============================================================
            # REQUÊTES AVEC OPTIONAL MATCH
            # ============================================================
            {
                "question": "techniques avec leurs composants ciblés et mitigations",
                "cypher": "MATCH (t:Technique)-[:TARGETS]->(c:Component) OPTIONAL MATCH (m:Mitigation)-[:MITIGATES]->(t) RETURN t.name, COLLECT(DISTINCT c.name) as targets, COLLECT(DISTINCT m.name) as mitigations LIMIT 10"
            },
            {
                "question": "techniques ciblant RAG et mitigations pour développeurs",
                "cypher": "MATCH (t:Technique)-[:TARGETS]->(c:Component) WHERE c.name CONTAINS 'RAG' OPTIONAL MATCH (m:Mitigation {owned_by: 'application_developers'})-[:MITIGATES]->(t) RETURN t.name, COLLECT(DISTINCT c.name) as targets, COLLECT(DISTINCT m.name) as mitigations"
            },
            {
                "question": "quelles techniques ont une sévérité critical et des mitigations",
                "cypher": "MATCH (t:Technique {severity: 'critical'}) OPTIONAL MATCH (m:Mitigation)-[:MITIGATES]->(t) RETURN t.name, t.cvss_score, COLLECT(m.name) as mitigations"
            },
            {
                "question": "acteurs utilisant des techniques qui ciblent l'inférence",
                "cypher": "MATCH (a:Actor)-[:USES]->(t:Technique)-[:TARGETS]->(c:Component) WHERE c.name CONTAINS 'inference' OR c.name CONTAINS 'RAG' RETURN a.name, COLLECT(DISTINCT t.name) as techniques"
            },

            # ============================================================
            # RELATIONS PRECEDES
            # ============================================================
            {
                "question": "Quelles techniques précèdent LLM Prompt Injection",
                "cypher": "MATCH (t1:Technique)-[:PRECEDES]->(t2:Technique {name: 'LLM Prompt Injection'}) RETURN t1.name, t1.id"
            },
            {
                "question": "Quelles techniques suivent LLM Prompt Crafting",
                "cypher": "MATCH (t1:Technique {name: 'LLM Prompt Crafting'})-[:PRECEDES]->(t2:Technique) RETURN t2.name, t2.id"
            },
            {
                "question": "Chaîne d'attaque complète pour Prompt Injection",
                "cypher": "MATCH path = (start:Technique)-[:PRECEDES*]->(end:Technique {name: 'LLM Prompt Injection'}) RETURN [n in nodes(path) | n.name] as chain"
            },
            {
                "question": "Visualiser la chaîne d'attaque RAG",
                "cypher": "MATCH path = (start:Technique {name: 'LLM Prompt Crafting'})-[:PRECEDES*]->(end:Technique {name: 'Exfiltration via Cyber Means'}) RETURN [n in nodes(path) | n.name] as attack_chain"
            },

            # ============================================================
            # REQUÊTES COMBINÉES
            # ============================================================
            {
                "question": "techniques ciblant RAG avec sévérité critical",
                "cypher": "MATCH (t:Technique)-[:TARGETS]->(c:Component) WHERE c.name CONTAINS 'RAG' AND t.severity = 'critical' RETURN t.name, t.id, t.cvss_score"
            },
            {
                "question": "mitigations pour développeurs pour les techniques critiques",
                "cypher": "MATCH (m:Mitigation {owned_by: 'application_developers'})-[:MITIGATES]->(t:Technique {severity: 'critical'}) RETURN m.name, t.name"
            },
            {
                "question": "acteurs et composants pour LLM Prompt Injection",
                "cypher": "MATCH (a:Actor)-[:USES]->(t:Technique {name: 'LLM Prompt Injection'}) MATCH (t)-[:TARGETS]->(c:Component) RETURN a.name, collect(c.name) as components"
            }
        ]

    def _get_schema_info(self):
        """Récupère les informations du schéma Neo4j avec cache"""
        if self._label_cache is None:
            try:
                with self.driver.session() as session:
                    # Labels
                    result = session.run("CALL db.labels()")
                    self._label_cache = [r['label'] for r in result]
                    
                    # Relations
                    result = session.run("CALL db.relationshipTypes()")
                    self._rel_cache = [r['relationshipType'] for r in result]
                    
                    # Propriétés des techniques
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
        prompt = """Tu es un expert Neo4j Cypher. Convertit la question en langage naturel en requête Cypher VALIDE.

SCHÉMA NEO4J :
- Nœuds : 
  • Tactic : {id, name, description, created_date, modified_date}
  • Technique : {id, name, description, maturity, severity, cvss_score, first_seen, last_seen, last_updated}
  • Subtechnique : {id, name, description, subtechnique_of}
  • Mitigation : {id, name, description, mitigation_category, ml_lifecycle, owned_by}
  • CaseStudy : {id, name, summary, incident_date, reporter, actor, target, case_study_type}
  • Actor : {name}
  • Component : {name}

- Relations :
  • BELONGS_TO : (Technique)-[:BELONGS_TO]->(Tactic)
  • SUBTECHNIQUE_OF : (Subtechnique)-[:SUBTECHNIQUE_OF]->(Technique)
  • MITIGATES : (Mitigation)-[:MITIGATES]->(Technique)
  • ILLUSTRATES : (CaseStudy)-[:ILLUSTRATES]->(Technique)
  • USES : (Actor)-[:USES]->(Technique)
  • TARGETS : (Technique)-[:TARGETS]->(Component)
  • PRECEDES : (Technique)-[:PRECEDES]->(Technique)

RÈGLES DE SYNTAXE CYPHER STRICTES (À RESPECTER ABSOLUMENT) :
1. Le mot-clé WHERE ne peut apparaître qu'après MATCH, OPTIONAL MATCH, ou WITH.
2. Le mot-clé WHERE ne peut JAMAIS apparaître après RETURN, ORDER BY, SKIP, LIMIT.
3. Pour filtrer des résultats après un RETURN, utiliser WITH avant le RETURN.
4. Pour les requêtes avec plusieurs conditions, utiliser plusieurs MATCH ou WITH.
5. Utilise OPTIONAL MATCH pour les relations qui peuvent ne pas exister.
6. Utilise COLLECT(DISTINCT ...) pour regrouper sans doublons.

RÈGLES IMPORTANTES :
1. Utilise CONTAINS pour la recherche par mot-clé (ex: WHERE t.name CONTAINS 'Prompt')
2. Utilise toLower() pour une recherche insensible à la casse
3. Les propriétés disponibles : severity (critical/high/medium/low), cvss_score (float), owned_by (string)
4. Réponds UNIQUEMENT par la requête Cypher, sans explication, sans markdown, sans backticks

CHAIN OF THOUGHT - Réfléchis étape par étape :

Étape 1: Analyser la question
- Quel est le sujet principal ?
- Quelles sont les conditions ?

Étape 2: Identifier les nœuds nécessaires
- Quels nœuds sont requis ?
- Quelles sont leurs propriétés ?

Étape 3: Identifier les relations
- Quelles relations relient ces nœuds ?

Étape 4: Construire MATCH
- Commencer par le nœud principal

Étape 5: Ajouter WHERE
- Filtrer par propriétés

Étape 6: Construire RETURN
- Quelles informations retourner ?

EXEMPLES DE RAISONNEMENT :

Question: "Quelles techniques ciblent les systèmes RAG ?"
Réflexion:
1. Sujet: Technique, condition: cible RAG
2. Nœuds: Technique, Component
3. Relations: TARGETS
4. MATCH: (t:Technique)-[:TARGETS]->(c:Component)
5. WHERE: c.name CONTAINS 'RAG'
6. RETURN: t.name, t.id

Cypher: MATCH (t:Technique)-[:TARGETS]->(c:Component) WHERE c.name CONTAINS 'RAG' RETURN t.name, t.id

Question: "Techniques avec sévérité critical et leurs mitigations"
Réflexion:
1. Sujet: Technique, condition: severity = critical
2. Nœuds: Technique, Mitigation
3. Relations: MITIGATES (optionnelle)
4. MATCH: (t:Technique {severity: 'critical'})
5. OPTIONAL MATCH: (m:Mitigation)-[:MITIGATES]->(t)
6. RETURN: t.name, t.id, COLLECT(DISTINCT m.name)

Cypher: MATCH (t:Technique {severity: 'critical'}) OPTIONAL MATCH (m:Mitigation)-[:MITIGATES]->(t) RETURN t.name, t.id, COLLECT(DISTINCT m.name)

"""
        for ex in self.examples:
            prompt += f"Question: {ex['question']}\nCypher: {ex['cypher']}\n\n"

        prompt += f"Question: {question}\n"
        prompt += "Réflexion:\n"
        prompt += "1. Sujet: "
        prompt += "2. Nœuds: "
        prompt += "3. Relations: "
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
                return f"ERREUR API: {response.status_code} - {response.text}"

            result = response.json()
            cypher = result['choices'][0]['message']['content'].strip()
            cypher = cypher.replace('```cypher', '').replace('```', '').strip()
            
            # Nettoyer le raisonnement si présent
            if 'Cypher:' in cypher:
                cypher = cypher.split('Cypher:')[-1].strip()
            
            return cypher

        except requests.exceptions.Timeout:
            return "ERREUR: Timeout - L'API ne répond pas"
        except Exception as e:
            return f"ERREUR: {str(e)}"

    def validate_cypher(self, cypher):
        try:
            with self.driver.session() as session:
                session.run(f"EXPLAIN {cypher}")
            return True, None
        except Exception as e:
            return False, str(e)

    def validate_semantic(self, cypher):
        """
        Vérifie que la requête Cypher est sémantiquement correcte
        - Vérifie que les labels existent
        - Vérifie que les relations existent
        """
        try:
            labels, rels, _ = self._get_schema_info()
            
            # Extraire les labels mentionnés
            label_pattern = r'MATCH\s*\([^)]*:(\w+)'
            found_labels = re.findall(label_pattern, cypher)
            
            # Extraire les relations mentionnées
            rel_pattern = r'\[[^)]*:(\w+)\]'
            found_rels = re.findall(rel_pattern, cypher)
            
            errors = []
            
            # Vérifier les labels
            for label in found_labels:
                if label not in labels:
                    errors.append(f"Label '{label}' n'existe pas dans la base")
            
            # Vérifier les relations
            for rel in found_rels:
                if rel not in rels:
                    errors.append(f"Relation '{rel}' n'existe pas dans la base")
            
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
        # 1. Bloquer les mots-clés dangereux
        dangerous_keywords = [
            'CREATE', 'DELETE', 'SET', 'REMOVE', 'MERGE',
            'DROP', 'LOAD CSV', 'CALL dbms', 'CALL apoc',
            'DROP CONSTRAINT', 'DROP INDEX', 'CREATE CONSTRAINT',
            'CREATE INDEX', 'CREATE DATABASE', 'DROP DATABASE'
        ]
        
        cypher_upper = cypher.upper()
        for keyword in dangerous_keywords:
            if keyword in cypher_upper:
                raise ValueError(f"❌ Keyword '{keyword}' is not allowed (read-only mode)")
        
        # 2. Vérifier les labels autorisés
        allowed_labels = ['Tactic', 'Technique', 'Subtechnique', 'Mitigation', 
                         'CaseStudy', 'Actor', 'Component']
        
        # Extraction simple des labels
        import re
        label_pattern = r'MATCH\s*\([^)]*:(\w+)'
        found_labels = re.findall(label_pattern, cypher)
        
        for label in found_labels:
            if label not in allowed_labels:
                raise ValueError(f"❌ Label '{label}' is not allowed")
        
        # 3. Enforcer LIMIT si absent
        if 'LIMIT' not in cypher_upper and 'COUNT' not in cypher_upper and 'RETURN' in cypher_upper:
            cypher = cypher + ' LIMIT 100'
        
        # 4. Bloquer les requêtes multi-étapes
        if ';' in cypher:
            # Sépare les requêtes et ne garde que la première
            cypher = cypher.split(';')[0]
        
        return cypher
    def ask(self, question):
        print(f"\n🔍 Question: {question}")

        cypher = self.text_to_cypher(question)
        if cypher.startswith("ERREUR:"):
            print(f"❌ {cypher}")
            return {"error": cypher}

        print(f"📝 Cypher généré: {cypher}")

        # 1. Validation syntaxique (EXPLAIN)
        valid, error = self.validate_cypher(cypher)
        if not valid:
            print(f"❌ Cypher invalide (syntaxe): {error}")
            return {"error": f"Cypher invalide: {error}", "cypher": cypher}

        # 2. Validation sémantique (NOUVEAU)
        valid, semantic_error = self.validate_semantic(cypher)
        if not valid:
            print(f"⚠️ Avertissement sémantique: {semantic_error}")

        results = self.execute(cypher)
        if isinstance(results, dict) and "error" in results:
            print(f"❌ Erreur d'exécution: {results['error']}")
            return {"error": results["error"], "cypher": cypher}

        print(f"📊 Résultats: {len(results) if isinstance(results, list) else 0} entrées trouvées")
        
        result_obj = {"cypher": cypher, "results": results}
        if semantic_error:
            result_obj["semantic_warning"] = semantic_error
        
        return result_obj

    def close(self):
        self.driver.close()


if __name__ == "__main__":
    print("🚀 Test Text2Cypher avec OpenRouter")
    print("=" * 50)

    t2c = Text2Cypher()

    questions = [
        "techniques avec Prompt",
        "techniques avec evasion",
        "quelles mitigations pour LLM Prompt Injection",
        "Tactiques avec nombre de techniques",
        "case studies pour la technique Reconnaissance",
        "acteurs qui utilisent LLM Prompt Injection",
        "techniques utilisées par APT28",
        "techniques qui ciblent les systèmes RAG",
        "composants ciblés par LLM Prompt Injection",
        "techniques avec sévérité critical",
        "techniques avec CVSS supérieur à 8",
        "techniques ciblant RAG avec sévérité critical",
        "mitigations pour développeurs pour les techniques critiques",
        "techniques ciblant RAG et mitigations pour développeurs",
        "Quelles techniques précèdent LLM Prompt Injection",
        "Chaîne d'attaque complète pour Prompt Injection"
    ]

    for q in questions:
        result = t2c.ask(q)
        if "error" in result:
            print(f"❌ Erreur: {result['error']}")
        else:
            print(f"✅ Succès: {len(result.get('results', []))} résultats")
            if "semantic_warning" in result:
                print(f"⚠️ {result['semantic_warning']}")
        print("-" * 50)

    t2c.close()