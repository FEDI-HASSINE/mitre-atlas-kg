# src/kg_builder/instanciate_enrichment.py
import os
import csv
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

class EnrichmentInstantiator:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def create_actor(self, tx, name):
        query = "MERGE (a:Actor {name: $name})"
        tx.run(query, name=name.strip())
    
    def create_component(self, tx, name):
        query = "MERGE (c:Component {name: $name})"
        tx.run(query, name=name.strip())
    
    def link_uses(self, tx, technique_id, actor_name):
        query = """
        MATCH (t:Technique {id: $technique_id})
        MATCH (a:Actor {name: $actor_name})
        MERGE (a)-[:USES]->(t)
        """
        tx.run(query, technique_id=technique_id, actor_name=actor_name.strip())
    
    def link_targets(self, tx, technique_id, component_name):
        query = """
        MATCH (t:Technique {id: $technique_id})
        MATCH (c:Component {name: $component_name})
        MERGE (t)-[:TARGETS]->(c)
        """
        tx.run(query, technique_id=technique_id, component_name=component_name.strip())
    
    def set_technique_properties(self, tx, technique_id, severity, cvss_score, first_seen, last_seen):
        query = """
        MATCH (t:Technique {id: $technique_id})
        SET t.severity = $severity,
            t.cvss_score = $cvss_score,
            t.first_seen = $first_seen,
            t.last_seen = $last_seen
        """
        tx.run(query, 
               technique_id=technique_id,
               severity=severity if severity else None,
               cvss_score=float(cvss_score) if cvss_score else None,
               first_seen=first_seen if first_seen else None,
               last_seen=last_seen if last_seen else None)
    
    def set_mitigation_owner(self, tx, mitigation_name, owned_by):
        query = """
        MATCH (m:Mitigation {name: $mitigation_name})
        SET m.owned_by = $owned_by
        """
        tx.run(query, mitigation_name=mitigation_name, owned_by=owned_by)
    
    def instanciate_from_csv(self, csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        with self.driver.session() as session:
            print("Instantiation of enrichments...")
            
            for row in rows:
                tech_id = row['technique_id']
                tech_name = row['technique_name']
                
                print(f"\nProcessing {tech_name} ({tech_id})")
                
                # 1. Create actors.
                actors = [a.strip() for a in row['actors'].split(';') if a.strip()]
                for actor in actors:
                    session.execute_write(self.create_actor, actor)
                    session.execute_write(self.link_uses, tech_id, actor)
                    print(f" Acteur: {actor}")
                
                # 2. Create components.
                components = [c.strip() for c in row['targeted_components'].split(';') if c.strip()]
                for component in components:
                    session.execute_write(self.create_component, component)
                    session.execute_write(self.link_targets, tech_id, component)
                    print(f" Composant: {component}")
                
                # 3. Add properties.
                session.execute_write(
                    self.set_technique_properties,
                    tech_id,
                    row['severity'],
                    row['cvss_score'],
                    row['first_seen'],
                    row['last_seen']
                )
                print(f" Propriétés: severity={row['severity']}, cvss={row['cvss_score']}")
            
            # 4. Add owned_by to mitigations (example).
            mitigation_owners = [
                {"mitigation": "Input and Output Validation for AI Agent Components", "owner": "application_developers"},
                {"mitigation": "Generative AI Guardrails", "owner": "application_developers"},
                {"mitigation": "AI Telemetry Logging", "owner": "application_developers"},
                {"mitigation": "User Training", "owner": "application_developers"},
                {"mitigation": "Control Access to AI Models and Data in Production", "owner": "security_team"},
            ]
            
            print("\nAdding owned_by for mitigations...")
            for item in mitigation_owners:
                session.execute_write(self.set_mitigation_owner, item['mitigation'], item['owner'])
                print(f" {item['mitigation']} → {item['owner']}")
            
            print("\nInstantiation completed!")

if __name__ == "__main__":
    print("Instantiation of enrichments")
    print("=" * 50)
    
    instantiator = EnrichmentInstantiator(URI, USER, PASSWORD)
    instantiator.instanciate_from_csv('C:\\Users\\DELL\\OneDrive\\Desktop\\mitre-atlas-kg\\data\\processed\\enrichment_suggestions_corrected.csv')
    instantiator.close()
