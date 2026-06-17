# src/kg_builder/instanciate_mitigation_owners.py
import os
import csv
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")


class MitigationOwnerInstantiator:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def set_mitigation_owner(self, tx, mitigation_id, mitigation_name, owned_by):
        """Ajoute ou met à jour la propriété owned_by d'une mitigation"""
        query = """
        MATCH (m:Mitigation {id: $mitigation_id})
        SET m.owned_by = $owned_by
        RETURN m.id, m.name, m.owned_by
        """
        result = tx.run(query, mitigation_id=mitigation_id, owned_by=owned_by)
        record = result.single()
        if record:
            print(f"  {record['m.id']} - {record['m.name']} → {record['m.owned_by']}")
            return True
        else:
            print(f"  Mitigation non trouvée: {mitigation_id} - {mitigation_name}")
            return False

    def instanciate_from_csv(self, csv_path):
        """Lit le CSV et instancie les owned_by"""
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        print(f"Chargement de {len(rows)} mitigations depuis {csv_path}")
        print("=" * 60)

        with self.driver.session() as session:
            success_count = 0
            error_count = 0

            for row in rows:
                mitigation_id = row.get('mitigation_id', '').strip()
                mitigation_name = row.get('mitigation_name', '').strip()
                owned_by = row.get('owned_by', '').strip()

                if not mitigation_id or not owned_by:
                    print(f"  Ligne invalide: id={mitigation_id}, owned_by={owned_by}")
                    error_count += 1
                    continue

                result = session.execute_write(
                    self.set_mitigation_owner,
                    mitigation_id,
                    mitigation_name,
                    owned_by
                )

                if result:
                    success_count += 1
                else:
                    error_count += 1

            print("=" * 60)
            print(f"{success_count} mitigations mises à jour avec succès")
            if error_count > 0:
                print(f"{error_count} erreurs rencontrées")

    def verify(self):
        """Vérifie les mitigations avec owned_by"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (m:Mitigation) 
                WHERE m.owned_by IS NOT NULL 
                RETURN m.id, m.name, m.owned_by 
                ORDER BY m.id
            """)
            records = list(result)
            print(f"\n{len(records)} mitigations avec owned_by :")
            print("=" * 60)
            for record in records:
                print(f"   {record['m.id']} - {record['m.name']} → {record['m.owned_by']}")
            print("=" * 60)

    def verify_by_owner(self):
        """Vérifie le nombre de mitigations par propriétaire"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (m:Mitigation) 
                WHERE m.owned_by IS NOT NULL 
                RETURN m.owned_by, count(m) as count 
                ORDER BY count DESC
            """)
            records = list(result)
            print(f"\nRépartition par propriétaire :")
            print("=" * 60)
            for record in records:
                print(f"   {record['m.owned_by']}: {record['count']} mitigations")
            print("=" * 60)

    def create_index(self):
        """Crée l'index sur owned_by si inexistant"""
        with self.driver.session() as session:
            try:
                session.run("CREATE INDEX mitigation_owned_by_idx IF NOT EXISTS FOR (m:Mitigation) ON (m.owned_by)")
                print("Index sur owned_by créé")
            except Exception as e:
                print(f"ℹIndex déjà existant ou erreur: {e}")


if __name__ == "__main__":
    print("Instanciation des owned_by pour les mitigations")
    print("=" * 60)

    csv_path = 'data/processed/mitigation_owners.csv'

    if not os.path.exists(csv_path):
        print(f"Fichier CSV non trouvé: {csv_path}")
        print(" Assurez-vous que le fichier est présent.")
        exit(1)

    try:
        instantiator = MitigationOwnerInstantiator(URI, USER, PASSWORD)

        # Créer l'index
        instantiator.create_index()

        # Instancier les owned_by
        instantiator.instanciate_from_csv(csv_path)

        # Vérifier les résultats
        instantiator.verify()
        instantiator.verify_by_owner()

        instantiator.close()

        print("\nInstanciation terminée avec succès !")

    except Exception as e:
        print(f"\nErreur: {e}")
        exit(1)