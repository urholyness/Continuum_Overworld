# Comms Agents (MCP + MAR + Orion Ready)

A production-minded scaffold for your communications & influence agents: Signal, Scribe, Sentinel, Liaison, Conductor, Analyst, Cartographer. Ships with FastAPI Switchboard, ChromaDB RAG, Redis+RabbitMQ jobs, and integrations to MCP, MAR, and Orion.

## Quickstart
1. Copy `.env.example` → `.env` and fill values.
2. `docker compose -f infra/docker-compose.yml up -d`
3. `uvicorn app.main:app --reload`
4. Smoke test:
```bash
curl -X POST localhost:8000/draft/scribe -H 'Content-Type: application/json' \
  -d '{"issue_card_path":"issue_cards/eudr_smallholders.md","audience":"buyer","tone":"boardroom"}'
```

## Concepts

- **Issue Cards** = source-of-truth topics (short TL;DR + links).
- **Cartographer** ingests `/knowledge` and `/issue_cards` and updates the vector store.
- **MCP** provider exposes these capabilities to your broader agent mesh.
- **MAR** registry hooks let OMEN auto-document and register components.
- **Orion** schedules workflows and logs runs to the DB.

## Architecture

- **7 Agents**: Signal (scanner), Scribe (drafts), Sentinel (risk), Liaison (outreach), Conductor (scheduler), Analyst (analytics), Cartographer (knowledge)
- **FastAPI Switchboard** with 8 main routes for agent operations
- **Data Layer**: PostgreSQL + ChromaDB for RAG, Redis + RabbitMQ for job queues
- **Tech Stack**: Python 3.11+, FastAPI, Pydantic, SQLAlchemy, LangChain
- **Cloud Ready**: AWS deployment with auto-scaling, multi-region, 24/7 operations

