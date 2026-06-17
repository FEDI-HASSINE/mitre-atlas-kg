# src/reasoning/__init__.py
"""
Reasoning Engine Module

Consume a natural-language description of an AI system and produce a
structured threat assessment grounded in the MITRE ATLAS knowledge graph.
"""

from .reasoning_engine import ReasoningEngine
from .system_analyzer import SystemAnalyzer
from .component_mapper import ComponentMapper
from .threat_finder import ThreatFinder
from .threat_prioritizer import ThreatPrioritizer
from .report_generator import ReasoningReportGenerator
from .config import (
    THREAT_SEVERITIES,
    SEVERITY_COLORS,
    KNOWN_COMPONENTS,
    PRIORITY_THRESHOLDS
)

__all__ = [
    'ReasoningEngine',
    'SystemAnalyzer',
    'ComponentMapper',
    'ThreatFinder',
    'ThreatPrioritizer',
    'ReasoningReportGenerator',
    'THREAT_SEVERITIES',
    'SEVERITY_COLORS',
    'KNOWN_COMPONENTS',
    'PRIORITY_THRESHOLDS'
]

__version__ = '1.0.0'