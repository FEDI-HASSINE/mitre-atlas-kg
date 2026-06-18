# tests/test_reasoning.py
"""
Unit tests for the Reasoning Engine
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.reasoning.reasoning_engine import ReasoningEngine


@pytest.fixture
def engine():
    return ReasoningEngine()


def test_system_analyzer(engine):
    """Test the system analyzer"""
    description = "This is a RAG chatbot with an API."
    result = engine.analyzer.analyze(description)
    
    assert isinstance(result, dict)
    assert 'system_type' in result
    assert 'components' in result


def test_component_mapper(engine):
    """Test the component mapper"""
    components = ['RAG', 'API']
    result = engine.mapper.map_components(components)
    
    assert isinstance(result, dict)
    assert 'RAG' in result or 'API' in result


def test_threat_finder(engine):
    """Test the threat finder"""
    mapped = {'RAG': ['RAG-based systems']}
    threats = engine.finder.find_threats(mapped)
    
    assert isinstance(threats, list)
    if threats:
        assert 'technique_id' in threats[0]


def test_threat_prioritizer(engine):
    """Test the threat prioritizer"""
    threats = [
        {'severity': 'critical', 'cvss_score': 9.1},
        {'severity': 'low', 'cvss_score': 3.0}
    ]
    prioritized = engine.prioritizer.prioritize(threats)
    
    assert len(prioritized) == 2
    assert prioritized[0]['priority'] >= prioritized[1]['priority']


def test_full_workflow(engine):
    """Test the full workflow"""
    description = "A simple RAG chatbot with vector database."
    result = engine.generate_assessment(description)
    
    assert 'system_info' in result
    assert 'threats' in result
    assert 'report' in result
    assert 'summary' in result


def test_fallback_analysis(engine):
    """Test the fallback analysis"""
    description = ""
    result = engine.analyzer._fallback_analysis(description)
    
    assert isinstance(result, dict)
    assert result['system_type'] == 'AI system'


def test_report_save(engine, tmp_path):
    """Test the report save"""
    report = "# Test Report"
    filename = str(tmp_path / "test_report.md")
    result = engine.save_report(report, filename)
    
    assert os.path.exists(filename)
    assert result == filename