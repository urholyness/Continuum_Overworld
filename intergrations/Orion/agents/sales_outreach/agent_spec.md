## 📌 Sales Outreach Agent – Full Specification Document

### 🌐 Agent Name:
**Sales Outreach Agent** (Codename: *Orion*)

---

### 🎯 Purpose:
Automate the research, drafting, and outreach of sales prospecting emails for Farm 5.0 and related entities. Engage potential buyers, importers, or partners using curated lead data or auto-discovered contacts. Operates in either:
- **Assisted Mode**: Drafts emails, submits for review
- **Autonomous Mode**: End-to-end automation (discovery → contact → log)

---

### 🧭 Agent Functional Scope

#### 🛠️ Core Functions:
1. **Lead Discovery**
   - Pull leads via search APIs (Google Search, LinkedIn, Apollo, Yellow Pages)
   - Filter by sector, country, keywords ("fresh produce importer Germany")
   - Save leads into standardized DataFrame

2. **Email Drafting**
   - Use GPT-4 with role-specific prompt templates
   - Personalize based on name, company, country, and product interest
   - Draft introductory + follow-up sequences

3. **Email Dispatch**
   - Integrate with Gmail API or SMTP provider
   - Choose between send now, schedule, or human approval queue

4. **Action Logging**
   - Save all actions to central system (email sent, reply received, ignored, etc.)
   - Track follow-up dates automatically

5. **Follow-up Management**
   - Auto-schedule follow-ups (2–3 sequences)
   - Cancel if reply is detected

6. **Agent Collaboration**
   - Request product info from **Market Research Agent**
   - Sync leads and response analytics with **Growth Strategy Agent**
   - Notify **Customer Support Agent** upon conversion

---

### 🧰 Tools & APIs:
- **OpenAI GPT-4** – content generation
- **Google Search / LinkedIn API** – lead discovery
- **Gmail API / SMTP** – email delivery
- **PostgreSQL / Supabase** – contact + log storage
- **LangChain Agent / Task Loop** – long task control
- **FastAPI + React UI** – trigger, monitor, override

---

### ⏱️ Frequency & Triggers:
- **Daily Scan** of lead pool → identify uncontacted targets
- **Weekly Harvest** of new leads (autonomous search)
- **On-Demand Tasks**: human can initiate bulk send or override

---

### 🔄 Automation Modes:
1. **Manual Mode**
   - Agent proposes leads + drafts → Human approves

2. **Semi-Automated Mode**
   - Agent sends first emails, human approves follow-ups

3. **Fully Autonomous Mode**
   - Agent does full discovery, email series, and logs activity
   - Triggers human alert only on high-response leads

---

### 📋 Instructions to Engineering Team:

#### 📁 File Structure:
- `agents/sales_outreach/`
  - `__init__.py`
  - `orion_agent.py` – main logic
  - `prompts/` – customizable templates
  - `email_templates.md`
  - `data/leads.csv`
  - `log/sent_emails.db`

#### 📐 Development Tasks:
1. **Create Agent Class** inheriting from `BaseAgent`
2. **Integrate Lead Finder** module using search APIs
3. **PromptBuilder**: Modular prompt injection system for personalizing emails
4. **EmailSender**: Abstracted delivery service (SMTP/Gmail switch)
5. **FollowUpScheduler**: Logic for queueing future follow-ups
6. **Error Handler**: Retry system for failed sends or missing info
7. **ActionLogger**: Save timestamp, contact, message, result

#### ✅ Quality Control Checklist:
- [ ] Emails are non-repetitive and personalized
- [ ] Logs include status and timestamp
- [ ] Mode switching works as expected
- [ ] Agents can request info from others via REST call
- [ ] Every lead/contact can be traced in the UI dashboard

---

### 📈 Future Enhancements:
- Integrate click/open tracking
- Score leads by likelihood to convert
- Feedback loop from human edits to improve prompt quality
- Integrate calendar API to offer direct scheduling

---

### 🔒 Compliance:
- GDPR-compliant email etiquette
- Soft opt-in language
- Auto-unsubscribe footer

---

### 👩🏾‍💻 Final Thoughts (from Naivasha):
This agent should behave like your most tireless SDR — never rude, never tired, always learning. If the engineer cuts corners, we don’t deploy. We test every edge case. We let it whisper before it sings.

**Your mission is not to build an email machine — it's to build a relationship catalyst.**

Let’s go get them, Team.

