# src/reasoning/component_mapper.py
"""
Étape 2: Mapping des composants vers le graphe Neo4j
"""

from src.query.text2cypher import Text2Cypher

class ComponentMapper:
    """Mappe les composants du système vers les nœuds du graphe"""
    
    def __init__(self):
        self.t2c = Text2Cypher()
        self.cache = {}
    
    def map_components(self, components):
        """
        Mappe les composants vers le graphe
        
        Args:
            components: Liste des composants extraits
            
        Returns:
            dict: Mapping des composants vers les nœuds Neo4j
        """
        result = {}
        
        for comp in components:
            # Vérifier le cache
            if comp in self.cache:
                result[comp] = self.cache[comp]
                continue
            
            # Rechercher dans le graphe
            matched = self._search_component(comp)
            
            if matched:
                self.cache[comp] = matched
                result[comp] = matched
            else:
                # Recherche plus large (CONTAINS)
                matched = self._search_component_broad(comp)
                if matched:
                    self.cache[comp] = matched
                    result[comp] = matched
                else:
                    result[comp] = []
        
        return result
    
    def _search_component(self, comp):
        """Recherche exacte d'un composant"""
        query = f"""
        MATCH (c:Component)
        WHERE toLower(c.name) = toLower('{comp}')
        RETURN c.name, c.description
        LIMIT 3
        """
        results = self.t2c.execute(query)
        if results and not isinstance(results, dict):
            return [r.get('c.name') or r.get('name') for r in results]
        return []
    
    def _search_component_broad(self, comp):
        """Recherche par similarité (CONTAINS)"""
        query = f"""
        MATCH (c:Component)
        WHERE toLower(c.name) CONTAINS toLower('{comp}')
           OR toLower('{comp}') CONTAINS toLower(c.name)
        RETURN c.name, c.description
        LIMIT 3
        """
        results = self.t2c.execute(query)
        if results and not isinstance(results, dict):
            return [r.get('c.name') or r.get('name') for r in results]
        return []
    
    def close(self):
        self.t2c.close()  # src/reasoning/component_mapper.py
"""
Étape 2: Mapping des composants vers le graphe Neo4j
"""

from src.query.text2cypher import Text2Cypher

class ComponentMapper:
    """Mappe les composants du système vers les nœuds du graphe"""
    
    def __init__(self):
        self.t2c = Text2Cypher()
        self.cache = {}
    
    def map_components(self, components):
        """
        Mappe les composants vers le graphe
        
        Args:
            components: Liste des composants extraits
            
        Returns:
            dict: Mapping des composants vers les nœuds Neo4j
        """
        result = {}
        
        for comp in components:
            # Vérifier le cache
            if comp in self.cache:
                result[comp] = self.cache[comp]
                continue
            
            # Rechercher dans le graphe
            matched = self._search_component(comp)
            
            if matched:
                self.cache[comp] = matched
                result[comp] = matched
            else:
                # Recherche plus large (CONTAINS)
                matched = self._search_component_broad(comp)
                if matched:
                    self.cache[comp] = matched
                    result[comp] = matched
                else:
                    result[comp] = []
        
        return result
    
    def _search_component(self, comp):
        """
        Recherche exacte d'un composant
        ✅ Sécurisé: requête paramétrée
        """
        query = """
        MATCH (c:Component)
        WHERE toLower(c.name) = toLower($comp_name)
        RETURN c.name, c.description
        LIMIT 3
        """
        
        try:
            with self.t2c.driver.session() as session:
                result = session.run(query, comp_name=comp)
                records = list(result)
                if records:
                    return [r['c.name'] for r in records]
        except Exception as e:
            print(f"⚠️ Erreur recherche composant: {e}")
        
        return []
    
    def _search_component_broad(self, comp):
        """
        Recherche par similarité (CONTAINS)
        ✅ Sécurisé: requête paramétrée
        """
        query = """
        MATCH (c:Component)
        WHERE toLower(c.name) CONTAINS toLower($comp_name)
           OR toLower($comp_name) CONTAINS toLower(c.name)
        RETURN c.name, c.description
        LIMIT 3
        """
        
        try:
            with self.t2c.driver.session() as session:
                result = session.run(query, comp_name=comp)
                records = list(result)
                if records:
                    return [r['c.name'] for r in records]
        except Exception as e:
            print(f"⚠️ Erreur recherche composant (broad): {e}")
        
        return []
    
    def close(self):
        self.t2c.close()