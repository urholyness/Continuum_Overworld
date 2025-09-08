# Orion (Farm 5.0 Agent System) Stack Architecture Documentation

## Overview
Orion is a comprehensive multi-agent system designed for automated business operations, including sales outreach, email management, market research, customer support, finance management, data analytics, and growth strategy. The system provides a scalable, secure, and modular framework for agent-based automation.

**Core Mission**: Automated business intelligence and operations through intelligent agent coordination.

## System Architecture

### Core Philosophy
- **Modular Design**: Each agent is self-contained with its own directory
- **Scalability**: New agents can be added without modifying existing code
- **Security**: Environment-based configuration with comprehensive security measures
- **Monitoring**: Real-time dashboard for system health and performance metrics

### High-Level Architecture
```
User/System Request → API Gateway → Agent Manager → Specific Agent
                    ↓
                Task Scheduler → Agent Execution → Logging → Response
                    ↓
                Dashboard ← Analytics ← Performance Metrics
```

## Technology Stack

### Backend Framework
- **Runtime**: Python 3.8+
- **Framework**: FastAPI 0.104.1 with Uvicorn 0.24.0
- **API Documentation**: OpenAPI/Swagger auto-generated
- **Async Support**: Full async/await support for high performance

### AI & ML Integration
- **OpenAI**: OpenAI API 1.3.5 for AI-powered operations
- **Anthropic**: Claude API 0.7.7 for advanced reasoning
- **Google AI**: Google AI services for document processing and analysis

### Dependencies
```python
# Core Framework
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
aiofiles==23.2.1
pydantic==2.5.0

# AI & ML
openai==1.3.5
anthropic==0.7.7

# Email & Communication
google-auth==2.23.4
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.2.0
google-api-python-client==2.109.0
emails==0.6.0

# Database
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
asyncpg==0.29.0

# Security
cryptography==41.0.7
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Monitoring & Logging
prometheus-client==0.19.0
structlog==23.2.0
```

## Project Structure

### Directory Architecture
```
farm5-orion-system/
├── 📁 core/                           # Core framework and base classes
│   ├── __init__.py                    # Package initialization
│   ├── base_agent.py                  # Base agent class and manager
│   └── task_scheduler.py              # Task scheduling system
│
├── 📁 agents/                         # Individual agent implementations
│   ├── __init__.py                    # Agents package initialization
│   ├── templates.py                   # Agent templates and utilities
│   ├── 📁 email_management/           # Email Management Agent
│   ├── 📁 sales_outreach/             # Sales Outreach Agent (Orion)
│   ├── 📁 market_research/            # Market Research Agent
│   ├── 📁 customer_support/           # Customer Support Agent
│   ├── 📁 finance_management/         # Finance Management Agent
│   ├── 📁 data_analytics/             # Data Analytics Agent
│   └── 📁 growth_strategy/            # Growth Strategy Agent
│
├── 📁 api/                            # FastAPI backend service
│   ├── __init__.py                    # API package initialization
│   ├── main.py                        # FastAPI application
│   ├── 📁 routes/                     # API route definitions
│   └── 📁 middleware/                 # Authentication and logging
│
├── 📁 dashboard/                      # React frontend dashboard
│   ├── 📁 components/                 # React components
│   ├── 📁 pages/                      # Dashboard pages
│   └── 📁 services/                   # API integration services
│
├── 📁 config/                         # Configuration files
├── 📁 docs/                           # Documentation and guides
├── 📁 tests/                          # Test files
├── 📁 scripts/                        # Utility scripts
├── 📁 deployment/                     # Deployment configurations
├── 📁 data/                           # Data files and databases
└── 📁 logs/                           # Application logs
```

## Agent Architecture

### Base Agent Framework
```python
class BaseAgent:
    """Abstract base class for all agents"""
    
    def __init__(self):
        self.name: str
        self.status: str
        self.memory: Dict[str, Any]
        self.config: Dict[str, Any]
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task using agent-specific logic"""
        raise NotImplementedError
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status and metadata"""
        pass
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get agent performance analytics"""
        pass
```

### Agent Categories

#### 1. Email Management Agent
- **Purpose**: Email classification and automated responses
- **Capabilities**: Email parsing, sentiment analysis, response generation
- **Integration**: Gmail API, email templates, response tracking

#### 2. Sales Outreach Agent (Orion)
- **Purpose**: Automated lead generation and outreach
- **Capabilities**: Lead discovery, email drafting, campaign management
- **Modes**: Manual, Semi-Auto, Fully-Auto
- **Features**: Personalized email generation, lead scoring, follow-up automation

#### 3. Market Research Agent
- **Purpose**: Competitive analysis and trend monitoring
- **Capabilities**: Market data collection, competitor analysis, trend identification
- **Data Sources**: Web scraping, API integrations, public databases

#### 4. Customer Support Agent
- **Purpose**: Ticket routing and automated responses
- **Capabilities**: Ticket classification, response generation, escalation management
- **Integration**: Support platforms, knowledge bases, customer databases

#### 5. Finance Management Agent
- **Purpose**: Expense tracking and financial reporting
- **Capabilities**: Expense categorization, budget monitoring, financial analysis
- **Integration**: Accounting systems, banking APIs, expense platforms

#### 6. Data Analytics Agent
- **Purpose**: Performance metrics and business insights
- **Capabilities**: Data aggregation, metric calculation, insight generation
- **Integration**: Business intelligence tools, databases, reporting systems

#### 7. Growth Strategy Agent
- **Purpose**: Meta-coordination of all agents
- **Capabilities**: Strategy optimization, agent coordination, performance analysis
- **Integration**: All other agents, business metrics, strategic planning tools

## API Architecture

### FastAPI Application Structure
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Farm 5.0 Agent System",
    description="Multi-agent business automation platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Endpoints

#### Sales Outreach (Orion) Endpoints
```python
# Agent Status
GET /api/sales/status                    # Get Orion agent status and analytics

# Lead Management
POST /api/sales/discover-leads           # Discover new sales leads
POST /api/sales/draft-emails             # Draft personalized emails
POST /api/sales/send-emails              # Send email batches
POST /api/sales/update-lead-status       # Update lead status

# Campaign Management
POST /api/sales/start-campaign           # Start outreach campaign
POST /api/sales/pause-campaign           # Pause active campaign
POST /api/sales/change-mode              # Change automation mode
```

#### Email Management Endpoints
```python
# Email Operations
POST /api/email/classify                 # Classify incoming emails
POST /api/email/generate-response        # Generate automated responses
POST /api/email/send-response            # Send generated responses
GET /api/email/analytics                 # Get email performance metrics
```

#### Market Research Endpoints
```python
# Research Operations
POST /api/research/analyze-competitor    # Analyze competitor data
POST /api/research/market-trends         # Identify market trends
GET /api/research/insights               # Get research insights
```

### API Models

#### Lead Discovery Criteria
```python
class LeadDiscoveryCriteria(BaseModel):
    sector: str = Field(default="fresh produce importer")
    country: str = Field(default="Germany")
    keywords: List[str] = Field(default=["fresh produce", "importer"])
    limit: int = Field(default=20, ge=1, le=100)
```

#### Email Draft Request
```python
class EmailDraftRequest(BaseModel):
    lead_ids: Optional[List[str]] = Field(default=None)
    limit: int = Field(default=10, ge=1, le=50)
```

#### Lead Status Update
```python
class LeadStatusUpdate(BaseModel):
    lead_id: str
    new_status: LeadStatus
    notes: Optional[str] = Field(default=None)
```

## Data Flow Architecture

### Request Processing Flow
1. **User/System Request**: API endpoint receives request
2. **API Gateway**: Request validation and routing
3. **Agent Manager**: Task distribution and agent selection
4. **Specific Agent**: Task execution and processing
5. **Response Generation**: Result formatting and return

### Agent Execution Flow
1. **Task Received**: Agent receives task from manager
2. **Validation**: Input validation and parameter checking
3. **Processing**: Agent-specific logic execution
4. **Action**: External API calls or system operations
5. **Logging**: Complete audit trail of operations
6. **Response**: Structured response with results

### Approval Workflow
1. **Sensitive Action**: Agent identifies action requiring approval
2. **Approval Queue**: Action placed in human review queue
3. **Human Review**: Manual review and decision making
4. **Approved/Rejected**: Decision communicated back to agent
5. **Execution**: Action executed or cancelled based on decision

### Monitoring & Feedback
1. **All Actions**: Every action logged to monitoring system
2. **Logging System**: Structured logging with metadata
3. **Dashboard**: Real-time updates and status display
4. **Analytics**: Performance metrics and trend analysis
5. **Optimization**: Continuous improvement based on data

## Component Interactions

### Core Framework Components

#### BaseAgent
- **Purpose**: Abstract base class for all agents
- **Responsibilities**: Common agent functionality, status management, analytics
- **Interface**: Standardized methods for task execution and status reporting

#### AgentManager
- **Purpose**: Orchestrates agent lifecycle and communication
- **Responsibilities**: Agent registration, task distribution, health monitoring
- **Features**: Load balancing, failover, performance optimization

#### TaskScheduler
- **Purpose**: Manages task queues and priorities
- **Responsibilities**: Task queuing, priority management, resource allocation
- **Features**: Background processing, rate limiting, task optimization

### Agent Layer Components

#### Email Management Agent
- **Integration**: Gmail API, email templates, response tracking
- **Capabilities**: Email classification, sentiment analysis, response generation
- **Workflow**: Email receipt → classification → response generation → sending

#### Sales Outreach Agent (Orion)
- **Integration**: CRM systems, email platforms, lead databases
- **Capabilities**: Lead discovery, email drafting, campaign management
- **Workflow**: Lead discovery → qualification → email drafting → sending → follow-up

#### Market Research Agent
- **Integration**: Web scraping tools, market data APIs, competitor databases
- **Capabilities**: Market data collection, competitor analysis, trend identification
- **Workflow**: Research request → data collection → analysis → insight generation

### API Service Components

#### FastAPI Application
- **Purpose**: REST API for agent management
- **Features**: OpenAPI documentation, request validation, error handling
- **Middleware**: CORS, authentication, rate limiting, logging

#### WebSocket Support
- **Purpose**: Real-time updates for dashboard
- **Features**: Live agent status, real-time metrics, instant notifications
- **Implementation**: FastAPI WebSocket endpoints with connection management

#### Authentication
- **Purpose**: Secure access control
- **Methods**: JWT tokens, API keys, role-based access control
- **Security**: Token rotation, secure storage, access logging

### Dashboard Components

#### React Components
- **Purpose**: Interactive UI elements
- **Features**: Real-time updates, responsive design, user-friendly interface
- **Components**: Agent status cards, performance charts, control panels

#### Real-time Updates
- **Purpose**: Live agent status and metrics
- **Implementation**: WebSocket connections, server-sent events
- **Features**: Instant updates, live monitoring, real-time alerts

#### Approval Interface
- **Purpose**: Human oversight for sensitive actions
- **Features**: Approval queue, decision interface, audit trail
- **Workflow**: Action request → human review → decision → execution

## Security Architecture

### Authentication & Authorization
- **JWT Tokens**: Secure API access with token-based authentication
- **Role-based Access Control**: Granular permissions based on user roles
- **API Key Management**: Secure API key storage and rotation
- **Session Management**: Secure session handling and timeout

### Data Protection
- **Encryption**: Data encryption at rest and in transit
- **GDPR Compliance**: Personal data protection and privacy compliance
- **Secure Credential Storage**: Encrypted storage of sensitive credentials
- **Input Validation**: Comprehensive input sanitization and validation

### API Security
- **Rate Limiting**: Prevents API abuse and manages costs
- **Input Validation**: Request parameter validation and sanitization
- **CORS Configuration**: Controlled cross-origin resource sharing
- **Error Handling**: Secure error messages without information leakage

### Monitoring & Alerting
- **Security Event Logging**: Complete audit trail of security events
- **Anomaly Detection**: Automated detection of suspicious activities
- **Real-time Threat Monitoring**: Continuous security monitoring
- **Incident Response**: Automated incident response procedures

## Monitoring & Observability

### Performance Metrics
- **Response Time**: API endpoint performance and latency
- **Throughput**: Tasks processed per minute and system capacity
- **Error Rate**: System reliability and error frequency
- **Resource Usage**: CPU, memory, and API cost monitoring

### Health Monitoring
- **Agent Health**: Individual agent status and responsiveness
- **Service Health**: API service availability and performance
- **System Health**: Overall system status and resource utilization
- **External Dependencies**: Third-party service health monitoring

### Dashboard Features
- **Real-time Monitoring**: Live system status and performance metrics
- **Historical Analytics**: Performance trends and pattern analysis
- **Alert Management**: Proactive notification of issues and anomalies
- **Performance Optimization**: Data-driven optimization recommendations

## Development Workflow

### Local Development Setup
```bash
# Setup environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Start development server
uvicorn api.main:app --reload
```

### Adding New Agents
1. **Create Agent Directory**: Add new directory in `agents/`
2. **Implement Agent Class**: Inherit from `BaseAgent` and implement required methods
3. **Register with Manager**: Add agent to `AgentManager` for orchestration
4. **Create API Routes**: Add API endpoints if needed
5. **Add Dashboard Components**: Create UI components for agent management
6. **Testing & Documentation**: Write tests and document agent capabilities

### Testing Strategy
- **Unit Testing**: Individual agent testing with pytest
- **Integration Testing**: API endpoint and agent interaction testing
- **End-to-End Testing**: Complete workflow validation
- **Performance Testing**: Load testing and scalability validation

### Deployment Pipeline
- **Development**: Local testing environment
- **Staging**: Cloud deployment for integration testing
- **Production**: Scaled deployment with monitoring and alerting

## Performance Considerations

### Optimization Strategies
- **Caching**: Response caching for common queries and operations
- **Batch Processing**: Group similar tasks for improved efficiency
- **Rate Limiting**: Prevent API abuse and manage external service costs
- **Database Optimization**: Indexed queries and connection pooling

### Scaling Considerations
- **Horizontal Scaling**: Multiple server instances for high availability
- **Load Balancing**: Intelligent request distribution across instances
- **Database Scaling**: Read replicas and connection pooling
- **Caching Layers**: Redis caching for frequently accessed data

### Resource Management
- **API Cost Management**: Monitor and optimize external API usage
- **Memory Management**: Efficient memory usage and garbage collection
- **Connection Pooling**: Optimize database and external service connections
- **Background Processing**: Async task processing for long-running operations

## Future Architecture Considerations

### Short-term Enhancements (3-6 months)
- **Mobile Application**: Mobile dashboard for on-the-go monitoring
- **Advanced Analytics**: Enhanced performance metrics and insights
- **Multi-language Support**: Internationalization and localization
- **Enhanced Security**: Advanced security features and compliance

### Medium-term Enhancements (6-12 months)
- **Machine Learning Optimization**: AI-powered performance optimization
- **Voice Interface Integration**: Voice commands and interactions
- **Predictive Analytics**: Predictive insights and trend forecasting
- **Advanced Automation Workflows**: Complex multi-agent workflows

### Long-term Enhancements (12+ months)
- **AI Model Fine-tuning**: Custom AI models for specific business needs
- **White-label Solutions**: Reusable platform for different industries
- **Enterprise Integrations**: Advanced enterprise system integrations
- **Advanced AI Capabilities**: Next-generation AI features and capabilities

## Integration Points

### External System Integration
- **Email Platforms**: Gmail, Outlook, custom email systems
- **CRM Systems**: Salesforce, HubSpot, custom CRM platforms
- **Database Systems**: PostgreSQL, MySQL, cloud databases
- **Cloud Services**: AWS, Google Cloud, Azure integration

### Internal Dependencies
- **MAR Integration**: Multilateral Agentic Repository coordination
- **MCP Protocol**: Multilateral Cerebral Protocol compliance
- **SCIP Framework**: Smart Collaborative Inference Protocol support
- **Nyxion Platform**: Survey and analysis platform integration

---

*This documentation reflects the current state of the Orion system. For the most up-to-date information, refer to the running system and configuration files.*

