# src/kg_builder/add_constraints.py
"""
Script pour ajouter les contraintes d'unicité dans Neo4j
"""

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")


class ConstraintInstantiator:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def add_constraints(self, tx):
        """Ajoute toutes les contraintes d'unicité"""
        constraints = [
            "CREATE CONSTRAINT tactic_id_unique IF NOT EXISTS FOR (t:Tactic) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT technique_id_unique IF NOT EXISTS FOR (t:Technique) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT subtechnique_id_unique IF NOT EXISTS FOR (s:Subtechnique) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT mitigation_id_unique IF NOT EXISTS FOR (m:Mitigation) REQUIRE m.id IS UNIQUE",
            "CREATE CONSTRAINT casestudy_id_unique IF NOT EXISTS FOR (c:CaseStudy) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT actor_name_unique IF NOT EXISTS FOR (a:Actor) REQUIRE a.name IS UNIQUE",
            "CREATE CONSTRAINT component_name_unique IF NOT EXISTS FOR (c:Component) REQUIRE c.name IS UNIQUE",
        ]
        
        success_count = 0
        for constraint in constraints:
            try:
                tx.run(constraint)
                print(f"   ✅ {constraint.split('REQUIRE')[0].strip().replace('CREATE CONSTRAINT', '').strip()}")
                success_count += 1
            except Exception as e:
                if "already exists" in str(e):
                    print(f"   ℹ️ Déjà existant")
                else:
                    print(f"   ❌ Erreur: {e}")
        
        return success_count

    def show_constraints(self, tx):
        """Affiche les contraintes existantes"""
        result = tx.run("SHOW CONSTRAINTS")
        records = list(result)
        print("\n📊 Contraintes existantes:")
        print("=" * 60)
        for r in records:
            name = r.get('name', 'N/A')
            entity = r.get('entityType', 'N/A')
            prop = r.get('properties', [])
            print(f"   • {name}: {entity} {prop}")
        print("=" * 60)
        return len(records)

    def instanciate(self):
        """Instancie toutes les contraintes"""
        print("🚀 Ajout des contraintes Neo4j")
        print("=" * 60)
        
        with self.driver.session() as session:
            # Afficher les contraintes existantes
            before = session.execute_write(self.show_constraints)
            
            print("\n📥 Ajout des nouvelles contraintes...")
            added = session.execute_write(self.add_constraints)
            
            # Afficher les contraintes après
            after = session.execute_write(self.show_constraints)
            
            print(f"\n✅ {added} contraintes ajoutées")
            print(f"📊 Total contraintes: {after}")


if __name__ == "__main__":
    instantiator = ConstraintInstantiator(URI, USER, PASSWORD)
    instantiator.instanciate()
    instantiator.close()