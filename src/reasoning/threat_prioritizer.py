# src/reasoning/threat_prioritizer.py
"""
Étape 4: Priorisation des menaces
"""

class ThreatPrioritizer:
    """Priorise les menaces par sévérité et impact"""
    
    def __init__(self):
        self.severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
    
    def prioritize(self, threats):
        """
        Priorise les menaces
        
        Args:
            threats: Liste des menaces
            
        Returns:
            list: Menaces triées par priorité
        """
        if not threats:
            return []
        
        # Calculer un score de priorité
        for threat in threats:
            threat['priority'] = self._calculate_priority(threat)
        
        # Trier par priorité décroissante
        threats.sort(key=lambda x: x.get('priority', 0), reverse=True)
        
        return threats
    
    def _calculate_priority(self, threat):
        """Calcule le score de priorité d'une menace"""
        score = 0
        
        # Score de sévérité (0-4)
        severity = threat.get('severity', 'medium')
        score += self.severity_order.get(severity.lower(), 2)
        
        # Score CVSS (0-3)
        cvss = threat.get('cvss_score')
        if cvss:
            try:
                cvss = float(cvss)
                if cvss >= 9.0:
                    score += 3
                elif cvss >= 7.0:
                    score += 2
                elif cvss >= 4.0:
                    score += 1
            except:
                pass
        
        # Bonus pour acteurs connus
        actors = threat.get('actors', [])
        if actors and len(actors) > 0:
            score += 1
        
        # Bonus pour mitigations disponibles
        mitigations = threat.get('mitigations', [])
        if mitigations and len(mitigations) > 0:
            score += 1
        
        return score
    
    def get_summary(self, threats):
        """Résumé des menaces par sévérité"""
        summary = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for t in threats:
            severity = t.get('severity', 'medium').lower()
            if severity in summary:
                summary[severity] += 1
        return summary 