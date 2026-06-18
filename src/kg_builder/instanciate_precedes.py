# src/kg_builder/instanciate_precedes.py
"""
Script to instantiate PRECEDES relationships between techniques
Based on attack chains documented in case studies
Use of MERGE to avoid duplicates
Verification of existing relationships
"""

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")


class PrecedesInstantiator:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_precedes_by_name(self, tx, from_name, to_name):
        """
        Creates a PRECEDES relationship by technique name
        Use of MERGE to avoid duplicates
        """
        query = """
        MATCH (t1:Technique {name: $from_name})
        MATCH (t2:Technique {name: $to_name})
        MERGE (t1)-[:PRECEDES]->(t2)
        RETURN t1.id, t2.id
        """
        result = tx.run(query, from_name=from_name, to_name=to_name)
        record = result.single()
        if record:
            print(f"   ✅ {record['t1.id']} ({from_name}) → PRECEDES → {record['t2.id']} ({to_name})")
            return True
        return False

    def create_precedes_by_id(self, tx, from_id, to_id):
        """
        Creates a PRECEDES relationship by technique ID
        Use of MERGE to avoid duplicates
        """
        query = """
        MATCH (t1:Technique {id: $from_id})
        MATCH (t2:Technique {id: $to_id})
        MERGE (t1)-[:PRECEDES]->(t2)
        RETURN t1.id, t2.id
        """
        result = tx.run(query, from_id=from_id, to_id=to_id)
        record = result.single()
        if record:
            print(f"   Use of MERGE to avoid duplicates {record['t1.id']} → PRECEDES → {record['t2.id']}")
            return True
        return False

    def delete_all_precedes(self, tx):
        """Delete all PRECEDES relationships (for cleanup)"""
        query = "MATCH ()-[r:PRECEDES]->() DELETE r"
        result = tx.run(query)
        print("   🗑️ Toutes les relations PRECEDES supprimées")
        return True

    def count_precedes(self, tx):
        """Count the PRECEDES relationships"""
        query = "MATCH ()-[r:PRECEDES]->() RETURN count(r) as count"
        result = tx.run(query)
        record = result.single()
        return record['count'] if record else 0

    def show_precedes(self, tx):
        """Display all PRECEDES relationships"""
        query = """
        MATCH (t1:Technique)-[r:PRECEDES]->(t2:Technique)
        RETURN t1.name as from_name, t1.id as from_id, t2.name as to_name, t2.id as to_id
        """
        result = tx.run(query)
        records = list(result)
        
        print("\n📊 Relations PRECEDES existantes:")
        print("=" * 60)
        for r in records:
            print(f"   • {r['from_name']} ({r['from_id']}) → {r['to_name']} ({r['to_id']})")
        print("=" * 60)
        return len(records)

    def instanciate_from_case_studies(self):
        """
        Instanciate the PRECEDES relationships from the case studies
        """
        
        # DDefinition of the attack chains
        attack_chains = [
            # Chain 1: Classic RAG Attack (based on AML.CS0035, AML.CS0037)
            {
                "from": "LLM Prompt Crafting",
                "to": "Prompt Infiltration via Public-Facing Application"
            },
            {
                "from": "Prompt Infiltration via Public-Facing Application",
                "to": "RAG Poisoning"
            },
            {
                "from": "RAG Poisoning",
                "to": "LLM Prompt Injection"
            },
            {
                "from": "LLM Prompt Injection",
                "to": "Exfiltration via Cyber Means"
            },
            
            # Chain 2: Attack via agents (based on AML.CS0037, AML.CS0039)
            {
                "from": "LLM Prompt Crafting",
                "to": "AI Agent Tool Invocation"
            },
            {
                "from": "AI Agent Tool Invocation",
                "to": "Exfiltration via Cyber Means"
            },
            
            # Chain 3: Attack via code assistant (based on AML.CS0041)
            {
                "from": "LLM Prompt Crafting",
                "to": "LLM Prompt Obfuscation"
            },
            {
                "from": "LLM Prompt Obfuscation",
                "to": "AI Supply Chain Compromise"
            },
            
            # Chain 4: Attack on memory (based on AML.CS0040)
            {
                "from": "LLM Prompt Injection",
                "to": "Memory"
            },
            
            # Chain 5: Evasion Attack (based on AML.CS0032, AML.CS0043)
            {
                "from": "Full AI Model Access",
                "to": "Evade AI Model"
            },
            {
                "from": "LLM Prompt Crafting",
                "to": "Evade AI Model"
            },
        ]
        
        print("📥 Instanciation des relations PRECEDES...")
        print("=" * 60)
        
        with self.driver.session() as session:
            #1. Display existing relationships before
            before_count = session.execute_write(self.count_precedes)
            print(f"   📊 Relations PRECEDES avant: {before_count}")
            
            if before_count > 0:
                session.execute_write(self.show_precedes)
                print()
            
            # 2. Create the relationships (MERGE)
            print("   🔄 Création des relations (MERGE)...")
            success_count = 0
            error_count = 0
            skipped_count = 0
            
            for chain in attack_chains:
                try:
                    result = session.execute_write(
                        self.create_precedes_by_name,
                        chain["from"],
                        chain["to"]
                    )
                    if result:
                        success_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    if "already exists" in str(e).lower():
                        skipped_count += 1
                        print(f"   ⏭️ Déjà existant: {chain['from']} → {chain['to']}")
                    else:
                        print(f"   ❌ Erreur: {e}")
                        error_count += 1
            
            #3. Display existing relationships after
            after_count = session.execute_write(self.count_precedes)
            print()
            session.execute_write(self.show_precedes)
            
            # 4. Résumé
            print()
            print("=" * 60)
            print("📊 RÉSUMÉ")
            print("=" * 60)
            print(f"   ✅ Relations créées: {success_count}")
            print(f"   ⏭️ Relations déjà existantes (MERGE): {skipped_count}")
            print(f"   ❌ Erreurs: {error_count}")
            print(f"   📊 Relations PRECEDES totales: {after_count}")
            print(f"   📈 Nouvelles relations ajoutées: {after_count - before_count}")
            print("=" * 60)
            
            return {
                "created": success_count,
                "skipped": skipped_count,
                "errors": error_count,
                "total_before": before_count,
                "total_after": after_count
            }


if __name__ == "__main__":
    print("🚀 Instanciation des relations PRECEDES (avec MERGE)")
    print("=" * 60)
    
    try:
        instantiator = PrecedesInstantiator(URI, USER, PASSWORD)
        result = instantiator.instanciate_from_case_studies()
        instantiator.close()
        
        print("\n✅ Instanciation terminée avec succès !")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        exit(1)