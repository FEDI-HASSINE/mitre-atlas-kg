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
        """Add all uniqueness constraints"""
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
                    print(f"   ℹ️ Already exists")
                else:
                    print(f"   ❌ Error: {e}")
        
        return success_count

    def show_constraints(self, tx):
        """Display existing constraints"""
        result = tx.run("SHOW CONSTRAINTS")
        records = list(result)
        print("\n📊 Existing constraints:")
        print("=" * 60)
        for r in records:
            name = r.get('name', 'N/A')
            entity = r.get('entityType', 'N/A')
            prop = r.get('properties', [])
            print(f"   • {name}: {entity} {prop}")
        print("=" * 60)
        return len(records)

    def instanciate(self):
        """Instantiates all constraints"""
        print("Added Neo4j constraints")
        print("=" * 60)
        
        with self.driver.session() as session:
            # Display existing constraints
            before = session.execute_write(self.show_constraints)
            
            print("\n📥 Adding new constraints...")
            added = session.execute_write(self.add_constraints)
            
            # Display constraints after
            after = session.execute_write(self.show_constraints)
            
            print(f"\n✅ {added} constraints added")
            print(f"📊 Total constraints: {after}")


if __name__ == "__main__":
    instantiator = ConstraintInstantiator(URI, USER, PASSWORD)
    instantiator.instanciate()
    instantiator.close()