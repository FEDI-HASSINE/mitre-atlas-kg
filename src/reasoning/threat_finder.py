# src/reasoning/threat_finder.py
"""
Étape 3: Recherche des menaces dans le graphe
"""

from src.query.text2cypher import Text2Cypher

class ThreatFinder:
    """Trouve les menaces pour les composants identifiés"""
    
    def __init__(self):
        self.t2c = Text2Cypher()
    
    def find_threats(self, mapped_components):
        """
        Trouve les techniques qui ciblent les composants
        ✅ Sécurisé: requêtes paramétrées
        
        Args:
            mapped_components: Dict {composant: [noms_neo4j]}
            
        Returns:
            list: Menaces avec détails
        """
        threats = []
        seen = set()
        
        for user_component, neo4j_names in mapped_components.items():
            if not neo4j_names:
                continue
            
            for neo4j_name in neo4j_names:
                # ✅ Requête paramétrée (pas d'interpolation)
                query = """
                MATCH (t:Technique)-[:TARGETS]->(c:Component {name: $component_name})
                OPTIONAL MATCH (m:Mitigation)-[:MITIGATES]->(t)
                OPTIONAL MATCH (a:Actor)-[:USES]->(t)
                RETURN 
                    t.name as technique_name,
                    t.id as technique_id,
                    t.severity as severity,
                    t.cvss_score as cvss_score,
                    t.description as technique_description,
                    COLLECT(DISTINCT m.name) as mitigations,
                    COLLECT(DISTINCT a.name) as actors,
                    $component_name as targeted_component
                """
                
                try:
                    with self.t2c.driver.session() as session:
                        result = session.run(query, component_name=neo4j_name)
                        
                        for r in list(result):
                            tech_id = r.get('technique_id')
                            if tech_id and tech_id not in seen:
                                seen.add(tech_id)
                                threats.append({
                                    'technique_name': r.get('technique_name'),
                                    'technique_id': tech_id,
                                    'severity': r.get('severity'),
                                    'cvss_score': r.get('cvss_score'),
                                    'technique_description': r.get('technique_description'),
                                    'mitigations': r.get('mitigations', []),
                                    'actors': r.get('actors', []),
                                    'targeted_component': r.get('targeted_component')
                                })
                except Exception as e:
                    print(f"⚠️ Erreur recherche menaces pour {neo4j_name}: {e}")
        
        return threats
    
    def find_additional_threats(self, system_type):
        """
        Menaces supplémentaires basées sur le type de système
        ✅ Sécurisé: requêtes paramétrées
        
        Args:
            system_type: Type de système
            
        Returns:
            list: Menaces supplémentaires
        """
        # Mapping des types de systèmes vers techniques courantes
        system_mapping = {
            'RAG': ['AML.T0051', 'AML.T0052'],
            'chatbot': ['AML.T0051', 'AML.T0065'],
            'agent': ['AML.T0051', 'AML.T0053', 'AML.T0065'],
            'API': ['AML.T0051', 'AML.T0025'],
        }
        
        threat_ids = []
        system_type_lower = system_type.lower()
        for key, ids in system_mapping.items():
            if key.lower() in system_type_lower:
                threat_ids.extend(ids)
        
        if not threat_ids:
            return []
        
        # ✅ Requête paramétrée avec liste
        query = """
        MATCH (t:Technique)
        WHERE t.id IN $threat_ids
        OPTIONAL MATCH (m:Mitigation)-[:MITIGATES]->(t)
        OPTIONAL MATCH (a:Actor)-[:USES]->(t)
        RETURN 
            t.name as technique_name,
            t.id as technique_id,
            t.severity as severity,
            t.cvss_score as cvss_score,
            COLLECT(DISTINCT m.name) as mitigations,
            COLLECT(DISTINCT a.name) as actors
        """
        
        try:
            with self.t2c.driver.session() as session:
                result = session.run(query, threat_ids=threat_ids)
                records = list(result)
                if records:
                    return [{
                        'technique_name': r.get('technique_name'),
                        'technique_id': r.get('technique_id'),
                        'severity': r.get('severity'),
                        'cvss_score': r.get('cvss_score'),
                        'mitigations': r.get('mitigations', []),
                        'actors': r.get('actors', [])
                    } for r in records]
        except Exception as e:
            print(f"⚠️ Erreur recherche menaces additionnelles: {e}")
        
        return []
    
    def close(self):
        self.t2c.close()