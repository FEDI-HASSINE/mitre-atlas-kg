# tests/test_ingest.py
import pytest
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

@pytest.fixture
def driver():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    yield driver
    driver.close()

def test_tactics_exist(driver):
    with driver.session() as session:
        result = session.run("MATCH (t:Tactic) RETURN count(t) as count")
        count = result.single()["count"]
        assert count >= 16

def test_techniques_exist(driver):
    with driver.session() as session:
        result = session.run("MATCH (t:Technique) RETURN count(t) as count")
        count = result.single()["count"]
        assert count >= 170

def test_relations_exist(driver):
    with driver.session() as session:
        result = session.run("MATCH (t:Technique)-[:BELONGS_TO]->(ta:Tactic) RETURN count(t) as count")
        count = result.single()["count"]
        assert count > 0