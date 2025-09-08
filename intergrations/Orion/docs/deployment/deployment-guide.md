# Farm 5.0 Agent System - Deployment Guide

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8+
- Node.js 16+ (for dashboard)
- Gmail/Outlook API credentials
- OpenAI API key

### Step 1: Set Up the Backend

```bash
# Create project directory
mkdir farm5-agents
cd farm5-agents

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn python-multipart aiofiles
pip install openai google-auth google-auth-oauthlib google-auth-httplib2
pip install google-api-python-client python-dotenv

# Create .env file
echo "OPENAI_API_KEY=your_key_here" > .env
echo "GMAIL_CREDENTIALS_PATH=credentials.json" >> .env
```

### Step 2: Deploy the Core System

1. **Create project structure:**
```
farm5-agents/
├── core/
│   ├── __init__.py
│   ├── agents.py (core agent classes)
│   ├── manager.py (agent manager)
│   └── dashboard.py (dashboard provider)
├── agents/
│   ├── __init__.py
│   ├── email_agent.py
│   ├── sales_agent.py
│   └── research_agent.py
├── api/
│   ├── __init__.py
│   └── main.py (FastAPI app)
├── frontend/
│   └── dashboard.html
├── .env
├── requirements.txt
└── README.md
```

2. **Run the API server:**
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Configure Email Integration

1. **Gmail API Setup:**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create new project or select existing
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download credentials.json

2. **Update Email Agent with real implementation:**
```python
# In email_agent.py
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class EmailManagementAgent(BaseAgent):
    def __init__(self):
        super().__init__(...)
        self.gmail_service = self._initialize_gmail()
    
    def _initialize_gmail(self):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        return build('gmail', 'v1', credentials=creds)
```

### Step 4: Deploy to Cloud (Production)

#### Option A: Deploy to Vercel + Supabase

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy API
vercel --prod

# Set up Supabase for database
# 1. Create account at supabase.com
# 2. Create new project
# 3. Update connection string in .env
```

#### Option B: Deploy to AWS/GCP

```bash
# Using AWS Lambda + API Gateway
# 1. Package your application
zip -r farm5-agents.zip .

# 2. Create Lambda function
aws lambda create-function \
  --function-name farm5-agents \
  --runtime python3.9 \
  --handler api.main.handler \
  --zip-file fileb://farm5-agents.zip

# 3. Set up API Gateway
# Use AWS Console or CLI
```

### Step 5: Set Up Monitoring

1. **Create monitoring dashboard:**
```python
# monitoring.py
import logging
from datetime import datetime

class AgentMonitor:
    def __init__(self):
        self.metrics = {
            "api_calls": 0,
            "errors": 0,
            "approvals_pending": 0
        }
    
    def log_metric(self, metric_name, value):
        self.metrics[metric_name] = value
        # Send to monitoring service (Datadog, CloudWatch, etc.)
```

2. **Set up alerts:**
```yaml
# alerts.yaml
alerts:
  - name: high_error_rate
    condition: error_rate > 0.05
    action: email_notification
  
  - name: pending_approvals
    condition: pending_approvals > 10
    action: slack_notification
```

## 📊 Cost Optimization Tips

1. **API Rate Limiting:**
```python
from asyncio import Semaphore

class RateLimiter:
    def __init__(self, rate=10):
        self.semaphore = Semaphore(rate)
    
    async def acquire(self):
        async with self.semaphore:
            yield
```

2. **Caching Responses:**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_response(prompt_hash):
    # Cache OpenAI responses
    pass
```

3. **Batch Processing:**
```python
async def batch_process_emails(emails, batch_size=10):
    for i in range(0, len(emails), batch_size):
        batch = emails[i:i+batch_size]
        await process_batch(batch)
```

## 🔧 Adding New Agents

### Template for New Agent:

```python
# agents/new_agent.py
from core.agents import BaseAgent

class NewAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="new_agent_001",
            name="New Agent",
            description="Description of what this agent does"
        )
    
    async def execute_task(self, task_data):
        self.status = AgentStatus.WORKING
        
        try:
            # Your agent logic here
            result = await self.perform_action(task_data)
            
            self.log_action(
                action_type="task_completed",
                action_data=result
            )
            
            self.status = AgentStatus.IDLE
            return result
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.log_action("error", {"error": str(e)}, status="error")
            raise
```

### Register the agent:
```python
# In api/main.py
from agents.new_agent import NewAgent

new_agent = NewAgent()
agent_manager.register_agent(new_agent)
```

## 📝 Weekly Operations Checklist

### Monday - Planning
- [ ] Review previous week's metrics
- [ ] Set agent priorities
- [ ] Update task board

### Daily
- [ ] Check pending approvals
- [ ] Monitor error logs
- [ ] Review agent performance

### Friday - Review
- [ ] Generate weekly report
- [ ] Cost analysis
- [ ] Plan improvements

## 🛠 Troubleshooting

### Common Issues:

1. **Agent not responding:**
   ```bash
   # Check agent status
   curl http://localhost:8000/api/agents/email_manager_001
   
   # View logs
   curl http://localhost:8000/api/logs?agent_id=email_manager_001
   ```

2. **High API costs:**
   - Enable caching
   - Reduce prompt complexity
   - Batch similar requests

3. **Slow performance:**
   - Check rate limits
   - Optimize database queries
   - Use async operations

## 🚀 Next Steps

1. **Phase 1 (Week 1-2):**
   - Deploy Email Management Agent
   - Set up basic monitoring
   - Test with real emails

2. **Phase 2 (Week 3-4):**
   - Add Sales Outreach Agent
   - Implement approval workflow
   - Create mobile dashboard

3. **Phase 3 (Month 2):**
   - Deploy all 6 agents
   - Create Meta-Agent
   - Full automation

## 📞 Support

- GitHub Issues: [your-repo]/issues
- Email: tech@greenstem.global
- Slack: #farm5-agents

---

Remember: Start small, measure everything, iterate quickly! 🌱