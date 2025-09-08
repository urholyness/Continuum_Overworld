# Farm 5.0 Agent System - Integration Guide & Best Practices

## 🔌 Integration Guide

### 1. Email Integration (Gmail)

#### Setup OAuth2 Authentication
```python
# gmail_integration.py
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)
```

#### Process Emails
```python
async def process_gmail_inbox(service, email_agent):
    # Get unread emails
    results = service.users().messages().list(
        userId='me',
        q='is:unread'
    ).execute()
    
    messages = results.get('messages', [])
    
    for message in messages:
        msg = service.users().messages().get(
            userId='me',
            id=message['id']
        ).execute()
        
        # Extract email data
        email_data = parse_email(msg)
        
        # Process with agent
        result = await email_agent.execute_task({
            "type": "classify_email",
            "email_data": email_data
        })
        
        # Mark as read
        service.users().messages().modify(
            userId='me',
            id=message['id'],
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
```

### 2. OpenAI Integration

#### Enhanced AI Processing
```python
# ai_integration.py
import openai
from typing import Dict, Any
import json

class AIProcessor:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        openai.api_key = api_key
        self.model = model
    
    async def classify_email(self, email_content: str) -> Dict[str, Any]:
        prompt = f"""
        Classify the following email into one of these categories:
        - inquiry: General questions about products/services
        - sales_opportunity: Potential sales lead
        - support_request: Customer needing help
        - internal_memo: Internal company communication
        - spam: Unwanted email
        
        Also provide:
        - confidence: 0-1 score
        - suggested_action: auto_respond, flag_for_review, archive
        - priority: low, medium, high, critical
        
        Email: {email_content}
        
        Return as JSON.
        """
        
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def generate_response(self, email_content: str, 
                              classification: Dict[str, Any]) -> str:
        prompt = f"""
        Generate a professional response to this {classification['category']} email.
        
        Original email: {email_content}
        
        Guidelines:
        - Be helpful and professional
        - Keep response concise
        - Include next steps if applicable
        - Sign as "Farm 5.0 Team"
        """
        
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content

### 3. Database Integration

#### SQLite Setup (Development)
```python
# database.py
import aiosqlite
from datetime import datetime

class Database:
    def __init__(self, db_path: str = "farm5_agents.db"):
        self.db_path = db_path
    
    async def initialize(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS action_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    action_data TEXT,
                    status TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    requires_approval BOOLEAN DEFAULT 0,
                    approved_by TEXT
                )
            ''')
            
            await db.execute('''
                CREATE TABLE IF NOT EXISTS agent_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await db.commit()
    
    async def log_action(self, log_entry):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO action_logs 
                (agent_id, action_type, action_data, status, requires_approval)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                log_entry.agent_id,
                log_entry.action_type,
                json.dumps(log_entry.action_data),
                log_entry.status,
                log_entry.requires_approval
            ))
            await db.commit()
```

#### PostgreSQL Setup (Production)
```python
# For production, use asyncpg
import asyncpg

class PostgresDatabase:
    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        self.pool = None
    
    async def initialize(self):
        self.pool = await asyncpg.create_pool(self.connection_url)
        
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS action_logs (
                    id SERIAL PRIMARY KEY,
                    agent_id VARCHAR(50) NOT NULL,
                    action_type VARCHAR(100) NOT NULL,
                    action_data JSONB,
                    status VARCHAR(50),
                    timestamp TIMESTAMPTZ DEFAULT NOW(),
                    requires_approval BOOLEAN DEFAULT FALSE,
                    approved_by VARCHAR(100)
                )
            ''')
```

### 4. Monitoring Integration

#### Prometheus Metrics
```python
# monitoring.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
task_counter = Counter('agent_tasks_total', 'Total tasks executed', ['agent_id', 'status'])
task_duration = Histogram('agent_task_duration_seconds', 'Task execution time', ['agent_id'])
active_agents = Gauge('active_agents', 'Number of active agents')

def track_task_execution(agent_id: str):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                task_counter.labels(agent_id=agent_id, status='success').inc()
                return result
            except Exception as e:
                task_counter.labels(agent_id=agent_id, status='error').inc()
                raise
            finally:
                duration = time.time() - start_time
                task_duration.labels(agent_id=agent_id).observe(duration)
        return wrapper
    return decorator
```

#### Slack Notifications
```python
# notifications.py
import aiohttp

class SlackNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def send_alert(self, message: str, level: str = "info"):
        color_map = {
            "info": "#36a64f",
            "warning": "#ff9900",
            "error": "#ff0000"
        }
        
        payload = {
            "attachments": [{
                "color": color_map.get(level, "#36a64f"),
                "text": message,
                "footer": "Farm 5.0 Agent System",
                "ts": int(datetime.now().timestamp())
            }]
        }
        
        async with aiohttp.ClientSession() as session:
            await session.post(self.webhook_url, json=payload)
```

## 🎯 Best Practices

### 1. Error Handling
```python
class AgentError(Exception):
    """Base exception for agent errors"""
    pass

class RetryableError(AgentError):
    """Error that can be retried"""
    pass

class CriticalError(AgentError):
    """Error that requires immediate attention"""
    pass

async def robust_task_execution(agent, task_data):
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            return await agent.execute_task(task_data)
        except RetryableError as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (attempt + 1))
                continue
            raise
        except CriticalError as e:
            # Send immediate alert
            await notify_critical_error(agent.agent_id, str(e))
            raise
```

### 2. Rate Limiting
```python
from asyncio import Semaphore
from functools import wraps

class RateLimiter:
    def __init__(self, calls_per_minute: int):
        self.semaphore = Semaphore(calls_per_minute)
        self.call_times = []
    
    async def acquire(self):
        async with self.semaphore:
            now = time.time()
            # Remove calls older than 1 minute
            self.call_times = [t for t in self.call_times if now - t < 60]
            
            if len(self.call_times) >= self.calls_per_minute:
                sleep_time = 60 - (now - self.call_times[0])
                await asyncio.sleep(sleep_time)
            
            self.call_times.append(now)
            yield

# Usage
rate_limiter = RateLimiter(calls_per_minute=60)

async def rate_limited_api_call():
    async with rate_limiter.acquire():
        # Make API call
        pass
```

### 3. Caching Strategy
```python
from functools import lru_cache
import hashlib

class ResponseCache:
    def __init__(self, ttl_seconds: int = 3600):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def _get_cache_key(self, prompt: str) -> str:
        return hashlib.md5(prompt.encode()).hexdigest()
    
    async def get_or_compute(self, prompt: str, compute_func):
        cache_key = self._get_cache_key(prompt)
        
        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.ttl:
                return cached_data
        
        # Compute and cache
        result = await compute_func(prompt)
        self.cache[cache_key] = (result, time.time())
        return result
```

### 4. Security Best Practices

#### API Key Management
```python
# Never hardcode API keys
import os
from cryptography.fernet import Fernet

class SecureConfig:
    def __init__(self):
        self.cipher = Fernet(os.getenv("ENCRYPTION_KEY").encode())
    
    def encrypt_api_key(self, api_key: str) -> bytes:
        return self.cipher.encrypt(api_key.encode())
    
    def decrypt_api_key(self, encrypted_key: bytes) -> str:
        return self.cipher.decrypt(encrypted_key).decode()
```

#### Input Validation
```python
from pydantic import BaseModel, validator

class EmailTaskData(BaseModel):
    email_id: str
    subject: str
    body: str
    
    @validator('email_id')
    def validate_email_id(cls, v):
        if not v or len(v) > 100:
            raise ValueError('Invalid email ID')
        return v
    
    @validator('body')
    def sanitize_body(cls, v):
        # Remove potentially harmful content
        return v.replace('<script>', '').replace('</script>', '')
```

### 5. Performance Optimization

#### Batch Processing
```python
async def batch_process_items(items: List[Any], batch_size: int = 10):
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        
        # Process batch concurrently
        batch_tasks = [process_item(item) for item in batch]
        batch_results = await asyncio.gather(*batch_tasks)
        results.extend(batch_results)
        
        # Small delay between batches
        await asyncio.sleep(0.1)
    
    return results
```

#### Connection Pooling
```python
class ConnectionPool:
    def __init__(self, max_connections: int = 10):
        self.pool = asyncio.Queue(maxsize=max_connections)
        self.created = 0
        self.max_connections = max_connections
    
    async def acquire(self):
        if self.pool.empty() and self.created < self.max_connections:
            conn = await self._create_connection()
            self.created += 1
        else:
            conn = await self.pool.get()
        
        return conn
    
    async def release(self, conn):
        await self.pool.put(conn)
```

## 📊 Monitoring Dashboard Queries

### Key Metrics to Track
```sql
-- Agent performance
SELECT 
    agent_id,
    COUNT(*) as total_actions,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
    AVG(CASE WHEN status = 'success' THEN 1 ELSE 0 END) * 100 as success_rate
FROM action_logs
WHERE timestamp > datetime('now', '-7 days')
GROUP BY agent_id;

-- Pending approvals aging
SELECT 
    agent_id,
    action_type,
    julianday('now') - julianday(timestamp) as days_pending
FROM action_logs
WHERE requires_approval = 1 AND approved_by IS NULL
ORDER BY timestamp ASC;

-- Hourly activity
SELECT 
    strftime('%Y-%m-%d %H:00', timestamp) as hour,
    COUNT(*) as actions
FROM action_logs
WHERE timestamp > datetime('now', '-24 hours')
GROUP BY hour
ORDER BY hour;
```

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] All API keys configured in environment variables
- [ ] Database migrations completed
- [ ] SSL certificates installed
- [ ] Backup strategy implemented
- [ ] Monitoring alerts configured
- [ ] Rate limits tested
- [ ] Error handling verified
- [ ] Security scan completed

### Deployment Steps
1. **Build Docker Image**
   ```bash
   docker build -t farm5-agents:latest .
   docker tag farm5-agents:latest your-registry/farm5-agents:v1.0.0
   docker push your-registry/farm5-agents:v1.0.0
   ```

2. **Deploy to Kubernetes**
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: farm5-agents
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: farm5-agents
     template:
       metadata:
         labels:
           app: farm5-agents
       spec:
         containers:
         - name: farm5-agents
           image: your-registry/farm5-agents:v1.0.0
           ports:
           - containerPort: 8000
           env:
           - name: OPENAI_API_KEY
             valueFrom:
               secretKeyRef:
                 name: farm5-secrets
                 key: openai-api-key
   ```

3. **Health Checks**
   ```python
   @app.get("/health/live")
   async def liveness():
       return {"status": "alive"}
   
   @app.get("/health/ready")
   async def readiness():
       # Check all dependencies
       checks = {
           "database": await check_database(),
           "openai": await check_openai_api(),
           "gmail": await check_gmail_api()
       }
       
       all_healthy = all(checks.values())
       return {
           "status": "ready" if all_healthy else "not ready",
           "checks": checks
       }
   ```

## 📈 Scaling Strategies

### Horizontal Scaling
- Use Kubernetes HPA (Horizontal Pod Autoscaler)
- Scale based on CPU/Memory or custom metrics
- Implement proper session affinity if needed

### Vertical Scaling
- Monitor resource usage patterns
- Adjust container resource limits
- Use appropriate instance types

### Agent-Specific Scaling
```python
# Dynamic agent allocation based on workload
class DynamicAgentPool:
    def __init__(self, agent_class, min_agents=1, max_agents=10):
        self.agent_class = agent_class
        self.min_agents = min_agents
        self.max_agents = max_agents
        self.agents = []
        self.load_threshold = 0.8
    
    async def scale_agents(self, current_load: float):
        current_count = len(self.agents)
        
        if current_load > self.load_threshold and current_count < self.max_agents:
            # Scale up
            new_agent = self.agent_class()
            self.agents.append(new_agent)
        elif current_load < 0.3 and current_count > self.min_agents:
            # Scale down
            self.agents.pop()
```

## 🎉 You're Ready to Launch!

With this complete system, you now have:
- ✅ Core infrastructure with 7 specialized agents
- ✅ Real-time monitoring dashboard
- ✅ Task scheduling and automation
- ✅ Secure API integrations
- ✅ Scalable architecture
- ✅ Comprehensive error handling
- ✅ Production-ready deployment guides

Start small, measure everything, and scale based on real usage data. The system is designed to grow with your needs!

Need help? Contact: tech@greenstem.global