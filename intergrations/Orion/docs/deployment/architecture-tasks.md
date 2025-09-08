## 🌾 Farm 5.0 Agent System – Full Architecture & Engineering Task Map

> *"Always innovate, always improve, in service to the soil, the seed, and the soul." – Naivasha, CTO of Quiet Thunder.*

---

### 📚 Purpose:

This document defines the architecture and all remaining engineering tasks required to complete the Farm 5.0 Agentic System before deployment. Each module, file, and responsibility is clearly outlined so the engineering team can execute with precision and harmony.

---

## ⚙️ System Overview

The Farm 5.0 Agent System is composed of:

- **Agent Layer** (Orion, etc.)
- **Agent Manager & Core Framework**
- **API Service Layer** (FastAPI)
- **Frontend UI** (React + Tailwind)
- **Data & Configuration Layer** (Supabase/PostgreSQL)
- **Integration Layer** (Email, GPT, Webhooks)
- **Monitoring & Security**

---

## 🧩 1. Agent Layer (📁 `/agents/`)

### ✅ Completed:

- Email Management Agent

### 🛠️ To Build:

- `sales_outreach/orion_agent.py`

  - Inherits BaseAgent
  - Modes: Manual, Semi-Auto, Auto
  - Functions:
    - `discover_leads()`
    - `draft_emails()`
    - `send_email()`
    - `schedule_followups()`
    - `log_action()`
    - `escalate_to_human()`

- Templates Folder: `prompts/email_templates.md`

  - Dynamic placeholders for each prospect type

- Future Agents: (structure ready)

  - `market_research/` → `insight_agent.py`
  - `customer_support/` → `companion_agent.py`
  - `growth_strategy/` → `strategos_agent.py`

---

## 🔗 2. Agent Manager & Core Framework (📁 `/core/`)

### ✅ Completed:

- Agent lifecycle management
- Status manager & approval queue
- Logging backend abstraction

### 🛠️ To Build:

- `core/inter_agent_comm.py`

  - Define REST/async messaging between agents
  - Queue for task delegation

- `core/approval_engine.py`

  - Filter tasks by sensitivity
  - Trigger UI-based human approvals

---

## 🌐 3. API Service Layer (📁 `/api/`)

### ✅ Completed:

- FastAPI framework
- Basic CRUD for agents
- WebSocket support

### 🛠️ To Build:

- `api/sales_routes.py`

  - Endpoint for triggering Orion manually
  - Endpoint for submitting new contact list

- `api/approval_routes.py`

  - Approve/Reject/Comment on pending actions

- `api/metrics.py`

  - Aggregate: #emails sent, open rate (future), conversion rate (future)

---

## 🎛️ 4. Frontend UI (📁 `/frontend/`)

### ✅ Completed:

- Real-time agent monitor
- Pending approval queue
- Historical logs

### 🛠️ To Build:

- Orion Dashboard Panel:

  - View current pipeline
  - Manual trigger buttons
  - Template selector preview

- Prospect View Tab:

  - Table of all current contacts
  - Filters: country, last contact, reply status
  - Integration with lead.csv/DB

---

## 🗃️ 5. Data Layer (📁 `/data/` or Supabase schema)

### ✅ Completed:

- Email action log DB (SQLite/PostgreSQL)

### 🛠️ To Build:

- `leads` table schema:
  - company\_name, contact\_name, email, country, status, last\_contacted, notes
- `actions` table expansion:
  - type, timestamp, status, payload

---

## 🔌 6. Integration Layer (📁 `/services/`)

### ✅ Completed:

- Gmail API token handler
- OpenAI GPT integration stub

### 🛠️ To Build:

- `search_integration.py`
  - Google Search API + keyword extractor
- `calendar_api.py` (Optional)
  - Schedule calls post-conversion
- `email_tracking.py` (Optional)
  - Open & click analytics

---

## 🔐 7. Monitoring & Security (📁 `/ops/`)

### ✅ Completed:

- Basic status checks
- FastAPI healthcheck

### 🛠️ To Build:

- `logtail_exporter.py`

  - Forward logs to external monitor (Logtail/Grafana)

- `auth_middleware.py`

  - Secure API routes
  - Role-based access

---

##

---

## ✅ CTO Final Review Criteria

-

---

## 🌱 Next Steps for Founder (George):

1. Prepare sample lead data for Orion to ingest
2. Finalize dynamic email templates for 3 buyer types
3. Schedule shadow-run of outbound campaign
4. Begin shortlisting markets for Market Research Agent

---

> "Build this not for the vanity of code, but for the dignity of labor, the bounty of harvest, and the voice of a continent rising through the soil."

– Naivasha

