# src/kg_builder/ingest.py
import os
import yaml
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

class AtlasIngester:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def clear_database(self, tx):
        tx.run("MATCH (n) DETACH DELETE n")
    
    def create_tactic(self, tx, tactic):
        query = """
        MERGE (t:Tactic {id: $id})
        SET t.name = $name,
            t.description = $description,
            t.created_date = $created_date,
            t.modified_date = $modified_date
        """
        tx.run(query, 
               id=tactic.get('id'),
               name=tactic.get('name'),
               description=tactic.get('description'),
               created_date=tactic.get('created_date'),
               modified_date=tactic.get('modified_date'))
    
    def create_technique(self, tx, technique):
        query = """
        MERGE (t:Technique {id: $id})
        SET t.name = $name,
            t.description = $description,
            t.maturity = $maturity
        WITH t
        UNWIND $tactics AS tactic_id
        MATCH (ta:Tactic {id: tactic_id})
        MERGE (t)-[:BELONGS_TO]->(ta)
        """
        tx.run(query,
               id=technique.get('id'),
               name=technique.get('name'),
               description=technique.get('description'),
               maturity=technique.get('maturity'),
               tactics=technique.get('tactics', []))
    
    def create_subtechnique(self, tx, subtechnique):
        query = """
        MERGE (s:Subtechnique {id: $id})
        SET s.name = $name,
            s.description = $description,
            s.subtechnique_of = $subtechnique_of
        WITH s
        MATCH (t:Technique {id: $subtechnique_of})
        MERGE (s)-[:SUBTECHNIQUE_OF]->(t)
        """
        tx.run(query,
               id=subtechnique.get('id'),
               name=subtechnique.get('name'),
               description=subtechnique.get('description'),
               subtechnique_of=subtechnique.get('subtechnique-of'))
    
    def create_mitigation(self, tx, mitigation):
        query = """
        MERGE (m:Mitigation {id: $id})
        SET m.name = $name,
            m.description = $description,
            m.mitigation_category = $mitigation_category,
            m.ml_lifecycle = $ml_lifecycle
        WITH m
        UNWIND $techniques AS technique_item
        MATCH (t:Technique {id: technique_item})
        MERGE (m)-[:MITIGATES]->(t)
        """
        # Extract technique IDs, which can be dictionaries or strings.
        technique_ids = []
        for tech in mitigation.get('techniques', []):
            if isinstance(tech, dict):
                # Dictionary entries can contain both 'id' and 'use'.
                technique_ids.append(tech.get('id'))
            else:
                technique_ids.append(tech)
        
        tx.run(query,
               id=mitigation.get('id'),
               name=mitigation.get('name'),
               description=mitigation.get('description'),
               mitigation_category=mitigation.get('mitigation-category'),
               ml_lifecycle=mitigation.get('ml-lifecycle', []),
               techniques=technique_ids)
    
    def create_case_study(self, tx, case_study):
        query = """
        MERGE (c:CaseStudy {id: $id})
        SET c.name = $name,
            c.summary = $summary,
            c.incident_date = $incident_date,
            c.incident_date_granularity = $incident_date_granularity,
            c.reporter = $reporter,
            c.actor = $actor,
            c.target = $target,
            c.case_study_type = $case_study_type
        WITH c
        UNWIND $procedures AS procedure
        MATCH (t:Technique {id: procedure.technique})
        MERGE (c)-[:ILLUSTRATES]->(t)
        """
        procedures = []
        for step in case_study.get('procedure', []):
            tech = step.get('technique')
            if isinstance(tech, dict):
                tech = tech.get('id')
            procedures.append({'technique': tech})
        
        tx.run(query,
               id=case_study.get('id'),
               name=case_study.get('name'),
               summary=case_study.get('summary'),
               incident_date=case_study.get('incident-date'),
               incident_date_granularity=case_study.get('incident-date-granularity'),
               reporter=case_study.get('reporter'),
               actor=case_study.get('actor'),
               target=case_study.get('target'),
               case_study_type=case_study.get('case-study-type'),
               procedures=procedures)
    
    def load_from_yaml(self, yaml_path):
        print(f"Loading file: {yaml_path}")
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        print(f"Data loaded: version {data.get('version')}")
        
        with self.driver.session() as session:
            # 1. Load tactics.
            print("Loading tactics...")
            for matrix in data.get('matrices', []):
                tactics = matrix.get('tactics', [])
                print(f"   → {len(tactics)} tactics found")
                for tactic in tactics:
                    session.execute_write(self.create_tactic, tactic)
            
            # 2. Load techniques.
            print("Loading techniques...")
            for matrix in data.get('matrices', []):
                techniques = matrix.get('techniques', [])
                print(f"   → {len(techniques)} techniques found")
                for technique in techniques:
                    if technique.get('object-type') == 'technique':
                        # Check whether this is a subtechnique.
                        if 'subtechnique-of' in technique:
                            session.execute_write(self.create_subtechnique, technique)
                        else:
                            session.execute_write(self.create_technique, technique)
            
            # 3. Load mitigations from the matrix.
            print("Loading mitigations...")
            for matrix in data.get('matrices', []):
                mitigations = matrix.get('mitigations', [])
                print(f"   → {len(mitigations)} mitigations found")
                for mitigation in mitigations:
                    session.execute_write(self.create_mitigation, mitigation)
            
            # 4. Load case studies.
            print("Loading case studies...")
            case_studies = data.get('case-studies', [])
            print(f"   → {len(case_studies)} case studies found")
            for case_study in case_studies:
                session.execute_write(self.create_case_study, case_study)
            
            print("Ingestion completed successfully!")
            
            # Print a summary.
            result = session.run("""
                MATCH (t:Tactic) RETURN count(t) as tactics
            """)
            print(f"Number of tactics: {result.single()['tactics']}")
            
            result = session.run("""
                MATCH (t:Technique) RETURN count(t) as techniques
            """)
            print(f"Number of techniques: {result.single()['techniques']}")
            
            result = session.run("""
                MATCH (s:Subtechnique) RETURN count(s) as subtechniques
            """)
            print(f"Number of subtechniques: {result.single()['subtechniques']}")
            
            result = session.run("""
                MATCH (m:Mitigation) RETURN count(m) as mitigations
            """)
            print(f"Number of mitigations: {result.single()['mitigations']}")
            
            result = session.run("""
                MATCH (c:CaseStudy) RETURN count(c) as case_studies
            """)
            print(f"Number of case studies: {result.single()['case_studies']}")

if __name__ == "__main__":
    print("MITRE ATLAS ingestion start")
    print("=" * 50)
    
    yaml_path = 'data/raw/atlas-data/dist/ATLAS.yaml'
    
    if not os.path.exists(yaml_path):
        print(f"Fichier non trouvé: {yaml_path}")
        print("   Assurez-vous d'avoir cloné le dépôt atlas-data")
        exit(1)
    
    try:
        ingester = AtlasIngester(URI, USER, PASSWORD)
        ingester.load_from_yaml(yaml_path)
        ingester.close()
        print("\nSuccès ! Le graphe est prêt à être interrogé.")
    except Exception as e:
        print(f"\nErreur: {e}")
        exit(1)
