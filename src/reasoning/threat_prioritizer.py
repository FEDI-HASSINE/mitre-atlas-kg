# src/reasoning/threat_prioritizer.py
"""
Step 4: Prioritizing threats
"""

class ThreatPrioritizer:
    """Prioritizes threats by severity and impact"""
    
    def __init__(self):
        self.severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
    
    def prioritize(self, threats):
        """
        Prioritizes threats
        
        Args:
            threats: List of threats
            
        Returns:
            list: Threats prioritized by priority
        """
        if not threats:
            return []
        
        # Calculate a priority score
        for threat in threats:
            threat['priority'] = self._calculate_priority(threat)
        
        # Sort by priority in descending order
        threats.sort(key=lambda x: x.get('priority', 0), reverse=True)
        
        return threats
    
    def _calculate_priority(self, threat):
        """Calculates the priority score of a threat"""
        score = 0
        
        # Score of severity (0-4)
        severity = threat.get('severity', 'medium')
        score += self.severity_order.get(severity.lower(), 2)
        
        # CVSS score (0-3)
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
        
        # Bonus for known actors
        actors = threat.get('actors', [])
        if actors and len(actors) > 0:
            score += 1
        
        # Bonus for available mitigations
        mitigations = threat.get('mitigations', [])
        if mitigations and len(mitigations) > 0:
            score += 1
        
        return score
    
    def get_summary(self, threats):
        """
        Summary of threats by severity
        
        Args:
            threats: List of threats
            
        Returns:
            dict: Summary with counters including total
        """
        summary = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for t in threats:
            severity = t.get('severity', 'medium').lower()
            if severity in summary:
                summary[severity] += 1
        
        # Add total
        summary['total'] = sum(summary.values())
        
        return summary