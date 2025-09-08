# Sales Outreach Agent (Orion) - Testing & Deployment Guide

## 🧪 Testing Guide

### 1. Unit Tests
```python
# tests/test_orion_agent.py
import pytest
from agents.sales_outreach.orion_agent import SalesOutreachAgent, OutreachMode, LeadStatus, Lead

@pytest.fixture
def orion_agent():
    """Create Orion agent instance for testing"""
    return SalesOutreachAgent()

@pytest.mark.asyncio
async def test_lead_discovery(orion_agent):
    """Test lead discovery functionality"""
    result = await orion_agent.discover_leads({
        "sector": "test sector",
        "country": "Germany",
        "limit": 5
    })
    
    assert result["discovered"] > 0
    assert "new_leads" in result
    assert len(result["new_leads"]) <= 5

@pytest.mark.asyncio
async def test_email_drafting(orion_agent):
    """Test email draft generation"""
    # First add a test lead
    test_lead = Lead(
        company_name="Test Company",
        contact_name="Test Contact",
        email="test@example.com",
        country="Germany",
        sector="fresh produce"
    )
    
    orion_agent.leads_df = pd.DataFrame([test_lead.to_dict()])
    
    result = await orion_agent.draft_emails([test_lead.lead_id])
    
    assert result["drafted"] == 1
    assert len(result["emails"]) == 1
    assert "subject" in result["emails"][0]
    assert "body" in result["emails"][0]

@pytest.mark.asyncio
async def test_mode_switching(orion_agent):
    """Test automation mode changes"""
    original_mode = orion_agent.mode
    
    result = orion_agent.set_mode(OutreachMode.FULLY_AUTO)
    assert result["new_mode"] == OutreachMode.FULLY_AUTO.value
    assert orion_agent.mode == OutreachMode.FULLY_AUTO
    
    # Test mode restrictions
    orion_agent.set_mode(OutreachMode.MANUAL)
    result = await orion_agent.draft_emails([])
    assert result["requires_approval"] == True

@pytest.mark.asyncio
async def test_follow_up_scheduling(orion_agent):
    """Test follow-up email scheduling"""
    # Create a lead that needs follow-up
    test_lead = Lead(
        company_name="Test Company",
        email="test@example.com",
        status=LeadStatus.CONTACTED,
        last_contact_date=datetime.now() - timedelta(days=4)
    )
    
    orion_agent.leads_df = pd.DataFrame([test_lead.to_dict()])
    
    result = await orion_agent.check_and_send_follow_ups()
    
    assert "sent" in result
    assert "checked" in result

def test_gdpr_compliance(orion_agent):
    """Test GDPR compliance in email templates"""
    for template_name, template_content in orion_agent.email_templates.items():
        # Check for unsubscribe option
        assert "unsubscribe" in template_content.lower() or \
               "privacy" in template_content.lower()
```

### 2. Integration Tests
```python
# tests/test_orion_integration.py
import pytest
from httpx import AsyncClient
from api.main import app

@pytest.mark.asyncio
async def test_api_lead_discovery():
    """Test lead discovery via API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/sales/discover-leads",
            json={
                "sector": "fresh produce",
                "country": "Germany",
                "limit": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "discovered" in data or "status" in data

@pytest.mark.asyncio
async def test_api_mode_change():
    """Test mode change via API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put(
            "/api/sales/mode",
            json={"mode": "semi_automated"}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] == True

@pytest.mark.asyncio
async def test_api_analytics():
    """Test analytics endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/sales/analytics")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_leads" in data
        assert "response_rate" in data
```

### 3. Edge Case Testing

```python
# tests/test_orion_edge_cases.py

@pytest.mark.asyncio
async def test_rate_limiting(orion_agent):
    """Test daily send limit enforcement"""
    orion_agent.sent_today = orion_agent.daily_send_limit
    
    result = await orion_agent.send_emails([{"lead_id": "test", "to": "test@example.com"}])
    
    assert result["sent"] == 0
    assert "limit" in result["error"].lower()

@pytest.mark.asyncio
async def test_duplicate_lead_handling(orion_agent):
    """Test duplicate email detection"""
    criteria = {"sector": "test", "country": "Germany", "limit": 5}
    
    # Discover leads twice
    await orion_agent.discover_leads(criteria)
    initial_count = len(orion_agent.leads_df)
    
    await orion_agent.discover_leads(criteria)
    final_count = len(orion_agent.leads_df)
    
    # Should not add duplicates
    assert final_count == initial_count

@pytest.mark.asyncio
async def test_error_recovery(orion_agent):
    """Test error handling and recovery"""
    # Simulate email sending failure
    with pytest.raises(Exception):
        await orion_agent.execute_task({"type": "invalid_task_type"})
    
    # Agent should recover
    assert orion_agent.status == AgentStatus.ERROR
    
    # Should be able to execute next task
    result = await orion_agent.execute_task({"type": "discover_leads", "criteria": {}})
    assert orion_agent.status == AgentStatus.IDLE
```

## 🚀 Deployment Checklist

### Pre-Deployment

#### Environment Setup
- [ ] Create production environment variables file
- [ ] Set up OpenAI API key with appropriate limits
- [ ] Configure Gmail API credentials
- [ ] Set up database for lead storage
- [ ] Create backup strategy for leads.csv

#### Code Review
- [ ] All edge cases handled
- [ ] Error messages are user-friendly
- [ ] No hardcoded credentials
- [ ] Logging is comprehensive
- [ ] GDPR compliance verified

#### API Configuration
```bash
# .env.production
OPENAI_API_KEY=sk-prod-xxx
OPENAI_MODEL=gpt-4
GMAIL_CREDENTIALS_PATH=/secure/path/credentials.json
ORION_MODE=semi_automated
DAILY_SEND_LIMIT=50
FOLLOW_UP_INTERVALS=3,7,14
RATE_LIMIT_PER_MINUTE=10
```

### Deployment Steps

#### 1. Database Migration
```sql
-- Create leads table
CREATE TABLE IF NOT EXISTS sales_leads (
    lead_id VARCHAR(64) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    country VARCHAR(100),
    sector VARCHAR(100),
    keywords TEXT,
    discovery_source VARCHAR(50),
    discovery_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'discovered',
    last_contact_date TIMESTAMP,
    response_received BOOLEAN DEFAULT FALSE,
    score FLOAT DEFAULT 0.0,
    notes JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create email logs table
CREATE TABLE IF NOT EXISTS email_logs (
    id SERIAL PRIMARY KEY,
    lead_id VARCHAR(64) REFERENCES sales_leads(lead_id),
    email_type VARCHAR(50),
    subject TEXT,
    body TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50),
    error_message TEXT,
    template_used VARCHAR(100),
    personalization_score FLOAT
);
```

#### 2. API Deployment
```bash
# Build Docker image
docker build -t farm5-orion:latest -f Dockerfile.orion .

# Run with proper environment
docker run -d \
  --name orion-agent \
  -e ENV=production \
  -v /secure/credentials:/app/credentials \
  -p 8001:8000 \
  farm5-orion:latest
```

#### 3. Monitoring Setup
```yaml
# prometheus/alerts.yml
groups:
  - name: orion_alerts
    rules:
      - alert: OrionHighErrorRate
        expr: rate(orion_errors_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High error rate in Orion agent"
      
      - alert: OrionLowResponseRate
        expr: orion_response_rate < 5
        for: 1h
        annotations:
          summary: "Low email response rate"
      
      - alert: OrionDailyLimitReached
        expr: orion_emails_sent_today >= orion_daily_limit
        annotations:
          summary: "Daily email limit reached"
```

### Post-Deployment Verification

#### 1. Smoke Tests
```bash
# Test API health
curl -X GET https://api.farm5.0/api/sales/health

# Test lead discovery (small batch)
curl -X POST https://api.farm5.0/api/sales/discover-leads \
  -H "Content-Type: application/json" \
  -d '{"sector": "fresh produce", "country": "Germany", "limit": 2}'

# Test analytics
curl -X GET https://api.farm5.0/api/sales/analytics

# Check mode
curl -X GET https://api.farm5.0/api/sales/status
```

#### 2. Functionality Verification
- [ ] Lead discovery returns results
- [ ] Email templates load correctly
- [ ] Draft emails are personalized
- [ ] Mode switching works
- [ ] Analytics calculate correctly
- [ ] Follow-up scheduling functions

#### 3. Performance Baseline
```python
# performance_test.py
import asyncio
import time
from agents.sales_outreach.orion_agent import SalesOutreachAgent

async def performance_test():
    orion = SalesOutreachAgent()
    
    # Test lead discovery speed
    start = time.time()
    await orion.discover_leads({"limit": 100})
    discovery_time = time.time() - start
    print(f"100 leads discovered in {discovery_time:.2f}s")
    
    # Test email drafting speed
    start = time.time()
    await orion.draft_emails([])  # Draft for 10 leads
    draft_time = time.time() - start
    print(f"10 emails drafted in {draft_time:.2f}s")
    
    # Expected benchmarks:
    # - Lead discovery: < 5s for 100 leads
    # - Email drafting: < 10s for 10 emails

asyncio.run(performance_test())
```

### Production Monitoring Dashboard

#### Key Metrics to Track
1. **Activity Metrics**
   - Total leads discovered
   - Emails sent per day
   - Follow-ups scheduled
   - Response rate

2. **Performance Metrics**
   - API response times
   - Email generation time
   - Error rate
   - Success rate

3. **Business Metrics**
   - Conversion rate
   - Lead quality score
   - Cost per lead
   - ROI

#### Grafana Dashboard Config
```json
{
  "dashboard": {
    "title": "Orion Sales Agent Dashboard",
    "panels": [
      {
        "title": "Emails Sent Today",
        "targets": [
          {
            "expr": "orion_emails_sent_today"
          }
        ]
      },
      {
        "title": "Response Rate",
        "targets": [
          {
            "expr": "rate(orion_responses_received[24h]) / rate(orion_emails_sent[24h]) * 100"
          }
        ]
      },
      {
        "title": "Lead Discovery Trend",
        "targets": [
          {
            "expr": "increase(orion_leads_discovered[1h])"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(orion_errors_total[5m])"
          }
        ]
      }
    ]
  }
}
```

## 🔒 Security Checklist

### API Security
- [ ] API keys rotated and secured
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention
- [ ] XSS protection

### Email Security
- [ ] SPF/DKIM configured
- [ ] Email content sanitized
- [ ] Bounce handling implemented
- [ ] Unsubscribe mechanism tested

### Data Security
- [ ] Lead data encrypted at rest
- [ ] PII handling compliant with GDPR
- [ ] Backup encryption enabled
- [ ] Access logs configured

## 📊 Success Criteria

### Week 1 Goals
- [ ] 100+ leads discovered
- [ ] 50+ initial emails sent
- [ ] < 5% error rate
- [ ] > 10% open rate

### Month 1 Goals
- [ ] 500+ leads in database
- [ ] > 15% response rate
- [ ] 5+ conversions
- [ ] < 2% unsubscribe rate

### Optimization Targets
- Email personalization score > 0.8
- Average response time < 5 seconds
- Daily automation rate > 80%
- Lead quality score > 0.7

## 🚨 Rollback Plan

### Quick Rollback Steps
1. Set mode to MANUAL to stop automated sending
   ```bash
   curl -X PUT https://api.farm5.0/api/sales/mode \
     -H "Content-Type: application/json" \
     -d '{"mode": "manual"}'
   ```

2. Restore previous Docker image
   ```bash
   docker stop orion-agent
   docker run -d --name orion-agent farm5-orion:previous
   ```

3. Restore database backup if needed
   ```bash
   pg_restore -d farm5_production backup_before_deploy.sql
   ```

## 📈 Scaling Strategy

### Horizontal Scaling
```yaml
# kubernetes/orion-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orion-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: orion-agent
  template:
    metadata:
      labels:
        app: orion-agent
    spec:
      containers:
      - name: orion
        image: farm5-orion:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        env:
        - name: AGENT_INSTANCE_ID
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
```

### Vertical Scaling
- Increase daily send limits gradually
- Add more email templates
- Expand to more countries/sectors
- Implement A/B testing for templates

## 🎯 Final Deployment Approval

### Sign-off Checklist
- [ ] Code review completed
- [ ] Security scan passed
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Team training completed
- [ ] Rollback plan tested

### Deployment Command
```bash
# Final deployment
./deploy-orion.sh --env production --version 1.0.0 --mode semi_automated

# Monitor deployment
watch -n 5 'curl -s https://api.farm5.0/api/sales/health | jq'
```

---

## 🎉 Launch Communication

### Internal Announcement
```
Subject: Orion Sales Agent Now Live! 🚀

Team,

I'm excited to announce that Orion, our automated sales outreach agent, is now live in production!

What Orion Does:
- Discovers new leads automatically
- Drafts personalized outreach emails
- Manages follow-up sequences
- Tracks responses and conversions

Current Mode: Semi-Automated (emails require approval)

Access Dashboard: https://dashboard.farm5.0/agents/orion

Please report any issues to #orion-support

Let's revolutionize our sales process together!

Best,
Farm 5.0 Tech Team
```

---

Remember: **Start in MANUAL mode, earn trust, then gradually increase automation!**