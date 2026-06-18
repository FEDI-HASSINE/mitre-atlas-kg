# src/reasoning/component_mapper.py
"""
Step 2: Mapping components to the Neo4j graph
"""

from src.query.text2cypher import Text2Cypher

class ComponentMapper:
    """Map components from the system to nodes in the graph"""
    
    def __init__(self):
        self.t2c = Text2Cypher()
        self.cache = {}
    
    def map_components(self, components):
        """
        Map components to the graph
        
        Args:
            components: List of extracted components
            
        Returns:
            dict: Mapping of components to Neo4j nodes
        """
        result = {}
        
        for comp in components:
            # Check the cache
            if comp in self.cache:
                result[comp] = self.cache[comp]
                continue
            
            # Search in the graph
            matched = self._search_component(comp)
            
            if matched:
                self.cache[comp] = matched
                result[comp] = matched
            else:
                # Search more broadly (CONTAINS)
                matched = self._search_component_broad(comp)
                if matched:
                    self.cache[comp] = matched
                    result[comp] = matched
                else:
                    result[comp] = []
        
        return result
    
    def _search_component(self, comp):
        """Exact search for a component"""
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
        """Search by similarity (CONTAINS)"""
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
Step 2: Mapping components to the Neo4j graph
"""

from src.query.text2cypher import Text2Cypher

class ComponentMapper:
    """Map components from the system to nodes in the graph"""
    
    def __init__(self):
        self.t2c = Text2Cypher()
        self.cache = {}
    
    def map_components(self, components):
        """
        Map components to the graph
        
        Args:
            components: List of extracted components
            
        Returns:
            dict: Mapping of components to Neo4j nodes
        """
        result = {}
        
        for comp in components:
            # Check the cache
            if comp in self.cache:
                result[comp] = self.cache[comp]
                continue
            
            # Search in the graph
            matched = self._search_component(comp)
            
            if matched:
                self.cache[comp] = matched
                result[comp] = matched
            else:
                # Search more broadly (CONTAINS)
                matched = self._search_component_broad(comp)
                if matched:
                    self.cache[comp] = matched
                    result[comp] = matched
                else:
                    result[comp] = []
        
        return result
    
    def _search_component(self, comp):
        """
        Search for a component exactly
        Secured: parameterized query
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
            print(f"⚠️ Error searching component: {e}")
        
        return []
    
    def _search_component_broad(self, comp):
        """
        Search by similarity (CONTAINS)
        Secured: parameterized query
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
            print(f"⚠️ Error searching component (broad): {e}")
        
        return []
    
    def close(self):
        self.t2c.close()