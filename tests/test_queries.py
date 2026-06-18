# tests/test_queries.py
import pytest
from src.query.text2cypher import Text2Cypher

@pytest.fixture
def t2c():
    """Fixture to create a Text2Cypher instance"""
    return Text2Cypher()

def test_basic_query(t2c):
    """Test: List all techniques of the Reconnaissance tactic"""
    result = t2c.ask("List all techniques of the Reconnaissance tactic")
    assert "error" not in result
    assert len(result["results"]) > 0

def test_mitigation_query(t2c):
    """Test: List mitigations for LLM Prompt Injection"""
    result = t2c.ask("What mitigations are needed for LLM Prompt Injection?")
    assert "error" not in result
    assert len(result["results"]) > 0

def test_search_query(t2c):
    """Test: Search by keyword - techniques with Prompt"""
    result = t2c.ask("techniques with Prompt")
    assert "error" not in result
    assert len(result["results"]) > 0

def test_count_query(t2c):
    """Test: Count the number of techniques"""
    result = t2c.ask("List all tactics")
    assert "error" not in result
    assert len(result["results"]) == 1
    assert result["results"][0]["nombre_techniques"] == 170

def test_tactics_query(t2c):
    """Test: List all tactics"""
    result = t2c.ask("List all tacticss")
    assert "error" not in result
    assert len(result["results"]) == 16

def test_case_study_query(t2c):
    """Test: Case studies for the Reconnaissance technique"""
    result = t2c.ask("case studies for the Reconnaissance technique")
    assert "error" not in result
    assert len(result["results"]) > 0

def test_complex_query(t2c):
    """Test: Tactics with a number of techniques"""
    result = t2c.ask("Tactics with a number of techniques")
    assert "error" not in result
    assert len(result["results"]) == 16

def test_mitigations_list_query(t2c):
    """Test: List techniques that have mitigations"""
    result = t2c.ask("list techniques that have mitigations")
    assert "error" not in result
    assert len(result["results"]) > 0

def close_t2c(t2c):
    """Close the connection after the tests"""
    t2c.close()