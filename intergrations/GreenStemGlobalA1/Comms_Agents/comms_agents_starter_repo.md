# Comms Agents Starter Repo — wired for MCP, MAR & Orion

> Production-minded scaffold for your multi-channel influence machine. Includes:
>
> - Agent layer (Signal, Scribe, Sentinel, Liaison, Conductor, Analyst, Cartographer)
> - API layer (Switchboard / FastAPI)
> - Data layer (Postgres + pgvector, Redis, RQ)
> - Integrations: **MCP** (Multilateral Cerebral Protocol), **MAR** (Multilateral Agentic Repo), and **Orion** (your ops scheduler/runner)

---

## Repository Tree

```
comms-agents/
├─ README.md
├─ .cursorrules
├─ agents.yaml
├─ pyproject.toml
├─ .env.example
├─ infra/
│  ├─ docker-compose.yml
│  └─ sql/
│     └─ 001_init.sql
├─ app/
│  ├─ main.py
│  └─ deps.py
├─ agents/
│  ├─ signal.py
│  ├─ scribe.py
│  ├─ sentinel.py
│  ├─ liaison.py
│  ├─ conductor.py
│  ├─ analyst.py
│  └─ cartographer.py
├─ tools/
│  ├─ retriever.py
│  ├─ buffer_api.py
│  ├─ x_api.py
│  ├─ gmail_api.py
│  ├─ telemetry.py
│  ├─ storage.py
│  └─ auth.py
├─ integrations/
│  ├─ mcp/
│  │  ├─ provider.py
│  │  ├─ schemas.py
│  │  └─ README.md
│  ├─ mar/
│  │  ├─ registry.json
│  │  ├─ omen_hook.py
│  │  └─ README.md
│  └─ orion/
│     ├─ scheduler.py
│     ├─ workflows.py
│     └─ README.md
├─ prompts/
│  ├─ scribe.system.md
│  ├─ signal.system.md
│  ├─ sentinel.system.md
│  └─ tone_guidelines.md
├─ knowledge/
│  ├─ back_burner/
│  │  └─ placeholder.md
│  └─ sources/
│     └─ README.md
├─ issue_cards/
│  ├─ eudr_smallholders.md
│  └─ mechanization_as_a_service.md
└─ tests/
   ├─ test_scribe.py
   ├─ test_signal.py
   ├─ test_sentinel.py
   └─ conftest.py
```

---

## Integration Topology (MCP × MAR × Orion)

**MCP (Multilateral Cerebral Protocol)**

- Role: Standardized tool/server interface so other agents (internal or external) can call your capabilities safely.
- Mount point: `integrations/mcp/provider.py` exposes Switchboard routes as MCP tools (e.g., `draft_scribe`, `scan_signal`, `risk_sentinel`).
- Contract: JSONSchema from `agents.yaml` → reflected into MCP tool specs in `integrations/mcp/schemas.py`.

**MAR (Multilateral Agentic Repo)**

- Role: Your knowledge + agent registry of re-usable components.
- Mount point: `integrations/mar/registry.json` lists these comms-agents as MAR services. `omen_hook.py` lets **OMEN** index, refactor, and auto-register functions; on change, it updates `registry.json` and emits docs into MAR.
- Data: `/knowledge` + `/issue_cards` are ingested by **Cartographer** and mirrored to MAR’s vector store (or referenced if MAR owns the store).

**Orion (Ops Orchestrator/Scheduler)**

- Role: Time-based and event-based runs (e.g., hourly Signal scans, morning digests, approval reminders). Think of it like Prefect/Airflow-lite glued to your domain.
- Mount point: `integrations/orion/scheduler.py` (cron + ad-hoc), `workflows.py` assembles multi-step chains (Signal→Scribe→Sentinel→Conductor draft).
- Control: Orion writes runs to DB (`events`, `campaigns`) and calls Switchboard endpoints with signed JWT from `tools/auth.py`.

**Data Flow**

```
[Orion] → /scan/signal → Pulse Digest
           ↓ (Issue Card selected)
         /draft/scribe (RAG via retriever) → Drafts + Citations
           ↓
         /risk/sentinel → R/G/A risk
           ↓ (if green/amber)
         /schedule/conductor (pending)
           ↓ (human approval via /approve)
         external APIs (Buffer/X/Gmail)
           ↓
         /analytics/analyst + PostHog telemetry
```

---

## Files — Content

### README.md

````md
# Comms Agents (MCP + MAR + Orion Ready)

A production-minded scaffold for your communications & influence agents: Signal, Scribe, Sentinel, Liaison, Conductor, Analyst, Cartographer. Ships with FastAPI Switchboard, pgvector RAG, Redis+RQ jobs, and integrations to MCP, MAR, and Orion.

## Quickstart
1. Copy `.env.example` → `.env` and fill values.
2. `docker compose -f infra/docker-compose.yml up -d`
3. `uvicorn app.main:app --reload`
4. Smoke test:
```bash
curl -X POST localhost:8000/draft/scribe -H 'Content-Type: application/json' \
  -d '{"issue_card_path":"issue_cards/eudr_smallholders.md","audience":"buyer","tone":"boardroom"}'
````

## Concepts

- **Issue Cards** = source-of-truth topics (short TL;DR + links).
- **Cartographer** ingests `/knowledge` and `/issue_cards` and updates the vector store.
- **MCP** provider exposes these capabilities to your broader agent mesh.
- **MAR** registry hooks let OMEN auto-document and register components.
- **Orion** schedules workflows and logs runs to the DB.

````

### .cursorrules
```txt
# Purpose
You are scaffolding a multi-agent comms system (Signal, Scribe, Liaison, Sentinel, Conductor, Analyst, Cartographer), integrated with MCP, MAR, and Orion.

# Ground rules
- Prefer Python 3.11 + FastAPI + Postgres(+pgvector) + Redis + RQ.
- Use LangGraph/LlamaIndex for orchestration logic.
- RAG over /knowledge and /issue_cards. Cite sources.
- All outbound messages require human approval.
- MCP tool specs mirror agents.yaml schemas.
- Orion only triggers drafts/simulations by default; posting requires /approve.

# Deliverables for any “scaffold” request
- /agents, /tools, /workflows, /prompts, /knowledge, /issue_cards, /infra, /tests
- FastAPI Switchboard with routes: /draft/scribe, /scan/signal, /risk/sentinel, /outreach/liaison, /schedule/conductor, /analytics/analyst, /ingest/cartographer, /approve
- Minimal tests per route.

# Style
- Production-grade. Type hints. Docstrings. Keep dependencies minimal.
````

### agents.yaml

```yaml
version: 0.1
vector_store: pgvector
queue: rq
agents:
  - name: signal
    goal: scan news/policy feeds and produce prioritized briefs
    input_schema:
      type: object
      properties:
        focus_regions: { type: array, items: { type: string } }
        topics: { type: array, items: { type: string } }
    output_schema:
      type: object
      properties:
        pulse_digest: { type: string }
        engage_now:
          type: array
          items:
            type: object
            properties:
              who: {type: string}
              why: {type: string}
              draft_hook: {type: string}
  - name: scribe
    goal: draft LI posts, X threads, comment packs with citations
    input_schema:
      type: object
      properties:
        issue_card_path: { type: string }
        audience: { type: string, enum: [policy, investor, buyer, public] }
        tone: { type: string, enum: [boardroom, policy-brief, field-notes, vision-thread, humor-light] }
    output_schema:
      type: object
      properties:
        linkedin_post: { type: string }
        x_thread: { type: array, items: { type: string } }
        comments_pack: { type: array, items: { type: string } }
        citations: { type: array, items: { type: string } }
  - name: sentinel
    goal: risk & compliance screening
    input_schema: { type: object, properties: { content: {type: string}, jurisdiction: {type: string} } }
    output_schema: { type: object, properties: { risk: {type: string, enum: [green, amber, red]}, notes: {type: array, items: {type:string}} } }
  - name: liaison
    goal: personalized outreach drafts (emails/DMs/comments)
    input_schema: { type: object, properties: { target_profile: {type:string}, campaign_goal:{type:string}, hooks:{type:array, items:{type:string}} } }
    output_schema: { type: object, properties: { email:{type:string}, linkedin_comment:{type:string}, twitter_reply:{type:string} } }
  - name: conductor
    goal: schedule & track posts
    input_schema: { type: object, properties: { platform:{type:string}, content:{type:string}, when:{type:string} } }
    output_schema: { type: object, properties: { scheduled_id:{type:string}, utm:{type:string} } }
  - name: analyst
    goal: attribute performance & learnings
    input_schema: { type: object, properties: { campaign_id:{type:string} } }
    output_schema: { type: object, properties: { kpis:{type:object}, insights:{type:array, items:{type:string}}, suggestions:{type:array, items:{type:string}} } }
  - name: cartographer
    goal: ingest PDFs/notes, extract entities, vectorize
    input_schema: { type: object, properties: { path:{type:string}, tags:{type:array, items:{type:string}} } }
    output_schema: { type: object, properties: { entities:{type:array, items:{type:string}}, vectors:{type:integer} } }
```

### pyproject.toml

```toml
[project]
name = "comms-agents"
version = "0.1.0"
description = "Comms & Influence Agents — MCP/MAR/Orion-ready"
requires-python = ">=3.11"
dependencies = [
  "fastapi",
  "uvicorn[standard]",
  "pydantic>=2",
  "python-dotenv",
  "rq",
  "redis",
  "psycopg[binary]",
  "SQLAlchemy",
  "pgvector",
  "httpx",
  "typing-extensions",
  "posthog",
  "markdown-it-py",
  "llama-index-core; extra == 'llama'",
]

[tool.pytest.ini_options]
pythonpath = ["."]
```

### .env.example

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=comms
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

REDIS_URL=redis://localhost:6379

POSTHOG_API_KEY=changeme
JWT_SECRET=supersecret

BUFFER_TOKEN=changeme
X_BEARER_TOKEN=changeme
GMAIL_CLIENT_ID=changeme
GMAIL_CLIENT_SECRET=changeme
```

### infra/docker-compose.yml

```yaml
version: "3.9"
services:
  db:
    image: ankane/pgvector
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports: ["5432:5432"]
  redis:
    image: redis:7
    ports: ["6379:6379"]
```

### infra/sql/001\_init.sql

```sql
CREATE TABLE IF NOT EXISTS posts (
  id SERIAL PRIMARY KEY,
  platform TEXT NOT NULL,
  content TEXT NOT NULL,
  status TEXT DEFAULT 'pending',
  scheduled_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS approvals (
  id SERIAL PRIMARY KEY,
  post_id INTEGER REFERENCES posts(id),
  approved BOOLEAN,
  approved_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
  id SERIAL PRIMARY KEY,
  kind TEXT NOT NULL,
  payload JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS campaigns (
  id SERIAL PRIMARY KEY,
  name TEXT,
  meta JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS risk_logs (
  id SERIAL PRIMARY KEY,
  post_id INTEGER REFERENCES posts(id),
  level TEXT,
  notes JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### app/deps.py

```python
from pydantic import BaseModel

class ScribeIn(BaseModel):
    issue_card_path: str
    audience: str
    tone: str

class ScribeOut(BaseModel):
    linkedin_post: str
    x_thread: list[str]
    comments_pack: list[str]
    citations: list[str]

class SignalIn(BaseModel):
    focus_regions: list[str] | None = None
    topics: list[str] | None = None

class SignalOut(BaseModel):
    pulse_digest: str
    engage_now: list[dict]

class SentinelIn(BaseModel):
    content: str
    jurisdiction: str

class SentinelOut(BaseModel):
    risk: str
    notes: list[str]
```

### app/main.py

```python
from fastapi import FastAPI, HTTPException
from app.deps import ScribeIn, ScribeOut, SignalIn, SignalOut, SentinelIn, SentinelOut
from agents import scribe as scribe_agent
from agents import signal as signal_agent
from agents import sentinel as sentinel_agent
from agents import conductor as conductor_agent
from agents import liaison as liaison_agent
from agents import analyst as analyst_agent
from agents import cartographer as cartographer_agent

app = FastAPI(title="Comms Agents Switchboard")

@app.post("/draft/scribe", response_model=ScribeOut)
def draft_scribe(payload: ScribeIn):
    return scribe_agent.run(payload)

@app.post("/scan/signal", response_model=SignalOut)
def scan_signal(payload: SignalIn):
    return signal_agent.run(payload)

@app.post("/risk/sentinel", response_model=SentinelOut)
def risk_sentinel(payload: SentinelIn):
    return sentinel_agent.run(payload)

@app.post("/schedule/conductor")
def schedule_conductor(data: dict):
    return conductor_agent.run(data)

@app.post("/outreach/liaison")
def outreach_liaison(data: dict):
    return liaison_agent.run(data)

@app.post("/analytics/analyst")
def analytics_analyst(data: dict):
    return analyst_agent.run(data)

@app.post("/ingest/cartographer")
def ingest_cartographer(data: dict):
    return cartographer_agent.run(data)

@app.post("/approve")
def approve(data: dict):
    return conductor_agent.approve(data)
```

### agents/scribe.py

```python
from app.deps import ScribeIn, ScribeOut
from tools.retriever import retrieve_context

def run(payload: ScribeIn) -> ScribeOut:
    ctx = retrieve_context(payload.issue_card_path)
    # NOTE: Replace this mock with LLM + prompt template using prompts/scribe.system.md
    li = f"[LI/{payload.tone}] {ctx['title']}: {ctx['tldr']}\n> Proof: " + ", ".join(ctx["links"])
    x = [f"{ctx['title']} — {ctx['tldr']}", "More in comments."]
    comments = ["Thoughtful take #1", "Thoughtful take #2", "Thoughtful take #3"]
    return ScribeOut(linkedin_post=li, x_thread=x, comments_pack=comments, citations=ctx["links"])
```

### agents/signal.py

```python
from app.deps import SignalIn, SignalOut

def run(payload: SignalIn) -> SignalOut:
    # TODO: wire RSS/Twitter lists; for now, mocked digest
    digest = "Policy pulse: EUDR update; KE-EU logistics corridors; diaspora investment bill draft."
    engage = [
        {"who": "@TradeKE", "why": "Live thread on exporter requirements", "draft_hook": "Comment with traceability pilot"},
        {"who": "EU DG-ENV", "why": "Clarify smallholder guidance", "draft_hook": "Ask for SME toolkit link"}
    ]
    return SignalOut(pulse_digest=digest, engage_now=engage)
```

### agents/sentinel.py

```python
from app.deps import SentinelIn, SentinelOut

RULES = [
    ("definitive claims without source", "amber"),
    ("policy endorsements", "amber"),
    ("legal exposure (promises, guarantees)", "red"),
]

def run(payload: SentinelIn) -> SentinelOut:
    notes = [r[0] for r in RULES if r]
    # naive: everything starts amber until tuned
    return SentinelOut(risk="amber", notes=notes)
```

### agents/conductor.py

```python
from datetime import datetime
import uuid

_PENDING: dict[str, dict] = {}

def run(data: dict):
    sid = str(uuid.uuid4())
    _PENDING[sid] = {"status": "pending", **data}
    return {"scheduled_id": sid, "status": "pending"}

def approve(data: dict):
    sid = data.get("scheduled_id")
    if sid not in _PENDING:
        return {"error": "not_found"}
    rec = _PENDING[sid]
    rec["status"] = "approved"
    rec["approved_at"] = datetime.utcnow().isoformat()
    # TODO: call Buffer/X adapters here
    return {"scheduled_id": sid, "status": "approved"}
```

### agents/liaison.py

```python
def run(data: dict):
    target = data.get("target_profile", "")
    goal = data.get("campaign_goal", "intro")
    hooks = data.get("hooks", [])
    email = f"Subject: Exploring {goal}\n\nHello {target}, quick note on synergies: " + "; ".join(hooks)
    return {"email": email, "linkedin_comment": "Great point—here's a buyer-side implication.", "twitter_reply": "DMs open to share pilot data."}
```

### agents/analyst.py

```python
def run(data: dict):
    # TODO: fetch analytics; mock KPIs
    kpis = {"followers_delta": 42, "meaningful_replies": 5, "warm_intros": 2}
    insights = ["Threads with data points outperform by 30%", "Morning posts get higher buyer engagement"]
    suggestions = ["Add chart to LI", "Tag chambers of commerce"]
    return {"kpis": kpis, "insights": insights, "suggestions": suggestions}
```

### agents/cartographer.py

```python
from tools.retriever import index_path

def run(data: dict):
    path = data.get("path")
    tags = data.get("tags", [])
    ent, vec = index_path(path, tags)
    return {"entities": ent, "vectors": vec}
```

### tools/retriever.py

```python
from pathlib import Path
import json

def retrieve_context(issue_card_path: str) -> dict:
    p = Path(issue_card_path)
    title = p.stem.replace("_", " ").title()
    text = p.read_text(encoding="utf-8") if p.exists() else ""
    # Dumb parsing: title, first paragraph as TL;DR, collect http links
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    tldr = next((l for l in lines if l and not l.startswith("#")), "No TL;DR")
    links = [l for l in lines if l.startswith("http")]
    return {"title": title, "tldr": tldr, "links": links}

_INDEX = {}

def index_path(path: str, tags: list[str]):
    _INDEX[path] = {"tags": tags}
    # TODO: real embeddings via pgvector/LLM
    return ["OrgA", "PolicyX"], 1
```

### tools/auth.py

```python
import jwt, time

def sign(payload: dict, secret: str) -> str:
    return jwt.encode({**payload, "iat": int(time.time())}, secret, algorithm="HS256")
```

### tools/telemetry.py

```python
def track(event: str, props: dict | None = None):
    # TODO: wire PostHog
    print("telemetry:", event, props or {})
```

### integrations/mcp/README.md

```md
# MCP Integration

This repo exposes Switchboard routes as MCP tools so external agents (or your IDE copilots) can call them.
- Provider: `provider.py` registers tools `draft_scribe`, `scan_signal`, `risk_sentinel`, etc.
- Schemas: Derived from `agents.yaml` (kept in `schemas.py`).
- Auth: Signed JWT via `tools/auth.py`.
```

### integrations/mcp/schemas.py

```python
# Normally you'd load agents.yaml and convert to JSON Schema here.
DRAFT_SCRIBE_INPUT = {
  "type": "object",
  "properties": {"issue_card_path": {"type": "string"}, "audience": {"type": "string"}, "tone": {"type": "string"}},
}
```

### integrations/mcp/provider.py

```python
# Pseudo-code for MCP provider, adapt to your MCP runtime
from app.main import draft_scribe, scan_signal, risk_sentinel

TOOLS = {
  "draft_scribe": {"input_schema": "see schemas.py", "handler": draft_scribe},
  "scan_signal": {"input_schema": {}, "handler": scan_signal},
  "risk_sentinel": {"input_schema": {}, "handler": risk_sentinel},
}
```

### integrations/mar/README.md

```md
# MAR Integration

- `registry.json` lists these agents as reusable services.
- `omen_hook.py` exposes a function for OMEN to: scan `/agents` & `/tools`, extract functions, write documentation stubs, and update `registry.json`.
```

### integrations/mar/registry.json

```json
{
  "services": [
    {"name": "scribe", "route": "/draft/scribe", "desc": "Draft posts with citations"},
    {"name": "signal", "route": "/scan/signal", "desc": "Policy & trend pulse"},
    {"name": "sentinel", "route": "/risk/sentinel", "desc": "Risk & compliance screen"}
  ]
}
```

### integrations/mar/omen\_hook.py

```python
from pathlib import Path
import json, re

REG = Path(__file__).with_name("registry.json")

DOCS = []
for p in Path(__file__).parents[2].joinpath("agents").glob("*.py"):
    DOCS.append({"file": p.name, "functions": ["run"]})

reg = json.loads(REG.read_text())
reg["docs"] = DOCS
REG.write_text(json.dumps(reg, indent=2))
```

### integrations/orion/README.md

```md
# Orion Integration

- `scheduler.py` runs cron-like jobs (e.g., hourly Signal scans) and records events.
- `workflows.py` assembles multi-step chains (Signal→Scribe→Sentinel→Conductor pending).
- Auth with Switchboard via signed JWT.
```

### integrations/orion/scheduler.py

```python
import time
from integrations.orion.workflows import morning_digest

if __name__ == "__main__":
    # toy scheduler loop
    while True:
        # 9:00 UTC-ish daily stub
        morning_digest()
        time.sleep(60 * 60 * 24)
```

### integrations/orion/workflows.py

```python
import requests, os

BASE = os.getenv("SWITCHBOARD_URL", "http://localhost:8000")

def morning_digest():
    # 1) Scan
    sig = requests.post(f"{BASE}/scan/signal", json={"topics": ["EUDR", "Trade"], "focus_regions": ["KE", "EU"]}).json()
    # 2) Draft from a default issue card
    sc = requests.post(f"{BASE}/draft/scribe", json={"issue_card_path": "issue_cards/eudr_smallholders.md", "audience": "buyer", "tone": "boardroom"}).json()
    # 3) Risk screen
    rs = requests.post(f"{BASE}/risk/sentinel", json={"content": sc["linkedin_post"], "jurisdiction": "EU"}).json()
    # 4) If green/amber, schedule as pending
    if rs["risk"] in ("green", "amber"):
        requests.post(f"{BASE}/schedule/conductor", json={"platform": "linkedin", "content": sc["linkedin_post"], "when": "tomorrow 09:05"})
    return {"signal": sig, "scribe": sc, "risk": rs}
```

### prompts/scribe.system.md

```md
Role: Scribe — boardroom-poetic strategist with skeptical edge and quick wit. Forward-looking, no fluff, cite sources. Output LI + X + 3 smart comments. Avoid promises; propose pilots.
```

### prompts/signal.system.md

```md
Prioritize sources by authority and recency. De-duplicate, cluster by topic, and surface 2–3 Engage-Now handles with why-it-matters.
```

### prompts/sentinel.system.md

```md
Flag legal exposure, unverifiable claims, and political endorsements. Classify risk: green/amber/red with specific edit notes.
```

### prompts/tone\_guidelines.md

```md
- Corporate-smart, poetic when earned, skeptical, light humor. No fluff. Action > adjectives.
```

### issue\_cards/eudr\_smallholders.md

```md
EUDR & Kenyan Smallholders: Risk, Readiness, Opportunity
EU deforestation rules reshape procurement; Kenyan smallholders risk exclusion without traceability. Bridge: cooperative traceability + exporter QA + diaspora-backed upgrades.
https://environment.ec.europa.eu/publications/eu-deforestation-regulation_en
```

### issue\_cards/mechanization\_as\_a\_service.md

```md
Mechanization-as-a-Service for East African Smallholders
Per-acre cost drops with shared CAPEX; uptime + operator training drive ROI; bundling with offtake reduces price risk.
```

### knowledge/back\_burner/placeholder.md

```md
This folder holds raw notes and back-burner ideas to be ingested by Cartographer.
```

### tests/conftest.py

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)
```

### tests/test\_scribe.py

```python
def test_scribe(client):
    r = client.post("/draft/scribe", json={"issue_card_path": "issue_cards/eudr_smallholders.md", "audience": "buyer", "tone": "boardroom"})
    assert r.status_code == 200
    data = r.json()
    assert "linkedin_post" in data
```

### tests/test\_signal.py

```python
def test_signal(client):
    r = client.post("/scan/signal", json={"topics": ["EUDR"], "focus_regions": ["KE"]})
    assert r.status_code == 200
    assert "pulse_digest" in r.json()
```

### tests/test\_sentinel.py

```python
def test_sentinel(client):
    r = client.post("/risk/sentinel", json={"content": "Test", "jurisdiction": "EU"})
    assert r.status_code == 200
    assert r.json()["risk"] in ("green", "amber", "red")
```

