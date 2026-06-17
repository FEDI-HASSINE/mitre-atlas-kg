# MITRE ATLAS Knowledge Graph

Queryable knowledge graph of [MITRE ATLAS](https://atlas.mitre.org/), the public taxonomy of adversarial techniques against AI systems.

The project loads ATLAS data into Neo4j, enriches it with governance-oriented metadata, and exposes natural-language querying, report generation, and a system-to-threat reasoning workflow.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Data Ingestion](#data-ingestion)
- [Running the Application](#running-the-application)
- [Usage Examples](#usage-examples)
- [Testing](#testing)
- [Known Limitations](#known-limitations)
- [Acknowledgements](#acknowledgements)

## Overview

This project turns MITRE ATLAS into an interactive knowledge graph for AI security analysis.

It supports questions such as:

- Which ATLAS techniques target RAG systems?
- Which mitigations apply to LLM Prompt Injection?
- Which actors use critical techniques?
- Which controls are owned by application developers or security teams?
- Given a system description, which AI threats are most relevant?

## Features

| Area | Description |
| --- | --- |
| Knowledge graph | Neo4j graph containing ATLAS tactics, techniques, subtechniques, mitigations, and case studies. |
| Natural-language query | Text2Cypher interface powered by OpenRouter and validated with Neo4j `EXPLAIN`. |
| Enrichment | Adds actors, targeted components, severity, CVSS scores, mitigation ownership, and attack-chain relationships. |
| Reasoning engine | Converts an AI system description into mapped components, relevant threats, prioritization, and a report. |
| Report generation | Produces Markdown reports with graph results, ATLAS technique IDs, and the executed Cypher query. |
| Streamlit frontend | Web UI for querying, exploring results, generating reports, and running threat assessments. |

Current graph size after ingestion and enrichment:

| Node or relation type | Count |
| --- | ---: |
| Tactics | 16 |
| Techniques | 170 |
| Mitigations | 35 |
| Case studies | 57 |
| Actors | 42 |
| Components | 43 |
| PRECEDES attack-chain relations | 7+ |

## Architecture

```text
User
  |
  v
Streamlit frontend
  |
  +--> Text2Cypher query interface
  |       |
  |       v
  |     Neo4j knowledge graph
  |
  +--> Report generator
  |       |
  |       v
  |     Graph-backed Markdown reports
  |
  +--> Reasoning engine
          |
          +--> 1. Analyze system description with LLM
          +--> 2. Map components to graph components
          +--> 3. Find relevant ATLAS techniques
          +--> 4. Prioritize threats
          +--> 5. Generate final assessment report
```

Core graph model:

```text
(Technique)-[:BELONGS_TO]->(Tactic)
(Subtechnique)-[:SUBTECHNIQUE_OF]->(Technique)
(Mitigation)-[:MITIGATES]->(Technique)
(CaseStudy)-[:ILLUSTRATES]->(Technique)
(Actor)-[:USES]->(Technique)
(Technique)-[:TARGETS]->(Component)
(Technique)-[:PRECEDES]->(Technique)
```

## Project Structure

```text
mitre-atlas-kg/
  data/
    raw/atlas-data/                  MITRE ATLAS source data
    processed/                       Enrichment CSV files
  frontend/
    app.py                           Main Streamlit app
    pages/                           Additional Streamlit pages
    requirements.txt                 Frontend dependencies
  reports/                           Generated Markdown reports
  src/
    kg_builder/
      ingest.py                      Core ATLAS ingestion
      llm_enrich_suggest.py          LLM enrichment suggestions
      instanciate_enrichment.py      Actor/component/severity enrichment
      instanciate_enrichment2.py     Updated enrichment script
      instanciate_mitigation_owners.py
      instanciate_precedes.py        Attack-chain relationships
    query/
      text2cypher.py                 Natural language to Cypher
    reasoning/
      reasoning_engine.py            Main reasoning orchestrator
      system_analyzer.py             System description analysis
      component_mapper.py            Graph component matching
      threat_finder.py               Threat discovery
      threat_prioritizer.py          Threat prioritization
      report_generator.py            Reasoning report generation
    report/
      report_generator.py            Query-based report generation
    schema.yaml                      Graph schema reference
  tests/
    test_ingest.py
    test_queries.py
    test_reasoning.py
  requirements.txt
  README.md
```

## Prerequisites

| Requirement | Version or note |
| --- | --- |
| Python | 3.10+ |
| Neo4j | 5.x |
| APOC | Optional, useful for Neo4j exploration |
| OpenRouter API key | Required for Text2Cypher and LLM-powered features |
| Docker | Optional, useful for running Neo4j locally |

## Installation

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
pip install -r frontend/requirements.txt
```

### 3. Start Neo4j

Using Docker:

```bash
docker run -d \
  --name neo4j-atlas \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5
```

Neo4j Browser will be available at:

```text
http://localhost:7474
```

### 4. Add MITRE ATLAS data

If `data/raw/atlas-data` is not already present, clone the official data repository:

```bash
git clone https://github.com/mitre-atlas/atlas-data.git data/raw/atlas-data
```

## Configuration

Create a `.env` file at the project root:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=openai/gpt-4o-mini
```

Useful Neo4j indexes:

```cypher
CREATE INDEX tactic_id IF NOT EXISTS FOR (t:Tactic) ON (t.id);
CREATE INDEX technique_id IF NOT EXISTS FOR (t:Technique) ON (t.id);
CREATE INDEX mitigation_id IF NOT EXISTS FOR (m:Mitigation) ON (m.id);
CREATE INDEX casestudy_id IF NOT EXISTS FOR (c:CaseStudy) ON (c.id);
CREATE INDEX actor_name IF NOT EXISTS FOR (a:Actor) ON (a.name);
CREATE INDEX component_name IF NOT EXISTS FOR (c:Component) ON (c.name);
CREATE INDEX technique_severity IF NOT EXISTS FOR (t:Technique) ON (t.severity);
CREATE INDEX mitigation_owned_by IF NOT EXISTS FOR (m:Mitigation) ON (m.owned_by);
```

## Data Ingestion

Run the core ATLAS ingestion:

```bash
python -m src.kg_builder.ingest
```

Add enrichment data:

```bash
python -m src.kg_builder.instanciate_enrichment2
python -m src.kg_builder.instanciate_mitigation_owners
python -m src.kg_builder.instanciate_precedes
```

Quick verification:

```bash
python -c "from src.query.text2cypher import Text2Cypher; t=Text2Cypher(); print(t.ask('List all tactics')); t.close()"
```

## Running the Application

Start the Streamlit UI:

```bash
streamlit run frontend/app.py
```

Then open:

```text
http://localhost:8501
```

The application includes:

| Tab | Purpose |
| --- | --- |
| Query | Ask natural-language questions and inspect generated Cypher. |
| Results | View previous query results. |
| Report | Generate Markdown reports from graph queries. |
| Reasoning | Describe an AI system and receive a threat assessment. |

## Usage Examples

### Natural-language queries

Try questions such as:

```text
List all tactics
Techniques in Reconnaissance
Mitigations for LLM Prompt Injection
Actors using Prompt Injection
Techniques targeting RAG
Critical severity techniques
Techniques with CVSS > 8
Attack chain for Prompt Injection
```

### Python query example

```python
from src.query.text2cypher import Text2Cypher

t2c = Text2Cypher()
result = t2c.ask("What mitigations exist for LLM Prompt Injection?")
print(result)
t2c.close()
```

### Report generation example

```python
from src.report.report_generator import ReportGenerator

generator = ReportGenerator()
report = generator.generate_report("Critical severity techniques and their mitigations")
generator.save_report(report, "reports/report.md")
generator.close()
```

### Reasoning engine example

```python
from src.reasoning import ReasoningEngine

engine = ReasoningEngine()

description = """
Our system is a RAG-based customer support assistant using GPT-4.
It has access to a vector database containing customer PII and is exposed via REST API.
"""

result = engine.generate_assessment(description)
print(result["report"])
engine.close()
```

## Testing

Run only the project tests:

```bash
python -m pytest tests -q
```

Known result in the local virtual environment:

```text
18 passed
```

Note: running `pytest` at the repository root may also collect tests from `data/raw/atlas-data`. Use `python -m pytest tests` unless a project-level `pytest.ini` is added.

## Known Limitations

| Limitation | Impact | Suggested improvement |
| --- | --- | --- |
| Text2Cypher is LLM-generated | Generated queries can be wrong or unsafe if not constrained. | Add strict read-only validation and keyword allowlists. |
| Enrichments are partly LLM/manual | Provenance and confidence are limited. | Add source, reviewer, confidence, and validation date fields. |
| Severity/CVSS covers selected techniques | Risk prioritization is incomplete. | Extend scoring to all techniques or mark unknown values explicitly. |
| Components are free text | Matching can be inconsistent. | Introduce a controlled component taxonomy. |
| PRECEDES relations are manual | Attack chains may be incomplete. | Derive chains from case-study procedure order where possible. |
| No Docker Compose file | Setup requires manual Neo4j configuration. | Add `docker-compose.yml` for reproducibility. |

## Acknowledgements

- MITRE ATLAS for the adversarial AI taxonomy and source data.
- Neo4j for graph storage and querying.
- OpenRouter for LLM access used by Text2Cypher and report generation.

Built as an AI Governance Engineering project for Voyverse.
