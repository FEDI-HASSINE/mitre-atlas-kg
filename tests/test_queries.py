# tests/test_queries.py
import pytest
from src.query.text2cypher import Text2Cypher

@pytest.fixture
def t2c():
    """Fixture pour créer une instance de Text2Cypher"""
    return Text2Cypher()

def test_basic_query(t2c):
    """Test: Liste les techniques de la tactique Reconnaissance"""
    result = t2c.ask("liste les techniques de la tactique Reconnaissance")
    assert "error" not in result
    assert len(result["results"]) > 0

def test_mitigation_query(t2c):
    """Test: Quelles mitigations pour LLM Prompt Injection"""
    result = t2c.ask("quelles mitigations pour LLM Prompt Injection")
    assert "error" not in result
    assert len(result["results"]) > 0

def test_search_query(t2c):
    """Test: Recherche par mot-clé - techniques avec Prompt"""
    result = t2c.ask("techniques avec Prompt")
    assert "error" not in result
    assert len(result["results"]) > 0

def test_count_query(t2c):
    """Test: Compter le nombre de techniques"""
    result = t2c.ask("combien de techniques existent")
    assert "error" not in result
    assert len(result["results"]) == 1
    assert result["results"][0]["nombre_techniques"] == 170

def test_tactics_query(t2c):
    """Test: Liste toutes les tactiques"""
    result = t2c.ask("liste toutes les tactiques")
    assert "error" not in result
    assert len(result["results"]) == 16

def test_case_study_query(t2c):
    """Test: Case studies pour la technique Reconnaissance"""
    result = t2c.ask("case studies pour la technique Reconnaissance")
    assert "error" not in result
    assert len(result["results"]) > 0

def test_complex_query(t2c):
    """Test: Tactiques avec nombre de techniques"""
    result = t2c.ask("Tactiques avec nombre de techniques")
    assert "error" not in result
    assert len(result["results"]) == 16

def test_mitigations_list_query(t2c):
    """Test: Quelles techniques ont des mitigations"""
    result = t2c.ask("quelles techniques ont des mitigations")
    assert "error" not in result
    assert len(result["results"]) > 0

def close_t2c(t2c):
    """Fermer la connexion après les tests"""
    t2c.close()