# MAR (Multilateral Agentic Repository) Stack Architecture Documentation

## Overview
The Multilateral Agentic Repository (MAR) is a unified, modular, and dynamically extensible repository designed to house and orchestrate multiple autonomous task agents. The system provides a standardized framework for agent development, deployment, and orchestration across diverse workflows.

**Tagline**: *"One protocol. Infinite purpose. Plug in. Power up. Pivot fast."*

## System Architecture

### Core Philosophy
- **Modularity**: Agents are independent and encapsulated
- **Interoperability**: All agents conform to a shared contract interface (API/CLI/UI callable)
- **Swappability**: Agents and LLMs can be interchanged based on task needs
- **Composability**: Agents can be chained into pipelines or workflows
- **Governability**: Optional access control, audit logs, and sandbox modes
- **Portability**: System runs in cloud, local, or hybrid environments

## Technology Stack

### Core Framework
- **Language**: Python 3.8+
- **Agent Framework**: LangChain, LangGraph, AutoGen
- **Memory Management**: Vector databases (Weaviate, Qdrant, Pinecone)
- **Data Processing**: JSON, SQL, YAML, Pickle
- **Logging**: Python logging with structured output

### AI Models & LLMs
| Agent Task     | Primary Model | Fallback |
| -------------- | ------------- | -------- |
| Extraction     | Claude 3.5    | GPT-4o   |
| Summarization  | GPT-4o        | Mixtral  |
| Translation    | GPT-4o        | LLaMA3   |
| Structuring    | Claude 3.5    | Mixtral  |
| Reasoning / QA | Claude 3.5    | GPT-4o   |

### Dependencies
```python
# Core Dependencies
langchain>=0.1.0
langgraph>=0.0.20
autogen>=0.2.0

# Vector Databases
weaviate-client>=3.25.0
qdrant-client>=1.7.0
pinecone-client>=2.2.0

# Data Processing
pandas>=2.0.0
numpy>=1.24.0
pyyaml>=6.0

# Development
pytest>=7.4.0
black>=23.0.0
```

## High-Level Architecture

### Directory Structure
```
Multilateral-Agentic-Repo/
├── agents/                    # Agent implementations
│   ├── csr/                  # CSR/ESG processing agents
│   ├── survey/               # Survey analytics agents
│   ├── legal/                # Legal & compliance agents
│   ├── logistics/            # Logistics & supply chain agents
│   ├── finance/              # Finance & investment agents
│   ├── utility/              # Cross-domain utility agents
│   ├── processing/           # Data processing agents
│   ├── extraction/           # Data extraction agents
│   ├── search/               # Search and discovery agents
│   └── automation/           # Workflow automation agents
├── shared/                   # Shared resources
│   ├── memory/               # Memory management
│   ├── prompts/              # Prompt templates
│   ├── configs/              # Configuration files
│   └── validators/           # Data validation
├── ui/                       # User interface
│   ├── cockpit-dashboard/    # Main dashboard
│   └── visualizer/           # Data visualization
├── orchestrators/            # Workflow orchestration
│   ├── langgraph_flows.py    # LangGraph workflow definitions
│   ├── autogen_protocols.py  # AutoGen protocol definitions
│   └── rule_based_router.py  # Rule-based task routing
├── interfaces/               # Integration interfaces
│   ├── api/                  # REST API endpoints
│   ├── cli/                  # Command-line interface
│   └── notebooks/            # Jupyter notebook integration
├── llm/                      # LLM integration layer
├── admin/                    # Administrative tools
├── configs/                  # Configuration management
└── main.py                   # Main application entry point
```

## Agent Architecture

### Agent Categories

#### 1. CSR / ESG Agents
- `doc_discovery_agent`: Document discovery and sourcing
- `pdf_scraper_agent`: PDF content extraction
- `kpi_extraction_agent`: KPI extraction and analysis
- `scope_emissions_agent`: Emissions scope analysis
- `sdg_alignment_agent`: SDG alignment assessment

#### 2. Survey Analytics Agents
- `response_cleaner_agent`: Survey response cleaning
- `score_calculator_agent`: Score calculation and analysis
- `ranking_synthesizer_agent`: Ranking synthesis and reporting

#### 3. Legal & Compliance Agents
- `contract_parser_agent`: Contract parsing and analysis
- `clause_classifier_agent`: Legal clause classification
- `risk_highlighter_agent`: Risk identification and highlighting

#### 4. Logistics & Supply Chain Agents
- `traceability_agent`: Supply chain traceability
- `shipment_forecaster_agent`: Shipment forecasting
- `qa_dashboard_agent`: Quality assurance dashboard

#### 5. Finance & Investment Agents
- `roi_estimator_agent`: ROI estimation and analysis
- `budget_optimizer_agent`: Budget optimization
- `grant_compliance_agent`: Grant compliance monitoring

#### 6. Utility / Cross-Domain Agents
- `text_summarizer_agent`: Text summarization
- `translation_agent`: Multi-language translation
- `voice_transcriber_agent`: Voice transcription
- `feedback_loop_agent`: Feedback loop management

### Agent Interface Contract

#### Base Agent Class
```python
class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self):
        self.name: str
        self.category: str
        self.status: str
        self.memory: Dict[str, Any]
        self.config: Dict[str, Any]
    
    def process(self, data: Any) -> Any:
        """Process data using agent-specific logic"""
        raise NotImplementedError
    
    def run(self, *args, **kwargs) -> Any:
        """Main execution method"""
        return self.process(*args, **kwargs)
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status and metadata"""
        return {
            "name": self.name,
            "category": self.category,
            "status": self.status,
            "memory_size": len(self.memory)
        }
```

#### Agent Configuration
```python
@dataclass
class AgentConfig:
    """Agent configuration"""
    name: str
    category: str
    version: str
    dependencies: List[str]
    memory_config: Dict[str, Any]
    llm_config: Dict[str, Any]
    execution_config: Dict[str, Any]
```

## Memory & Inter-Agent Protocol

### Shared Memory Architecture

#### Memory Types
- `project_memory.json`: Project-specific context and data
- `agent_state.db`: Agent state persistence
- `query_cache.pkl`: Query result caching
- `task_trace.yaml`: Task execution traceability

#### Memory Management
```python
class MemoryManager:
    """Manages shared memory across agents"""
    
    def __init__(self):
        self.vector_db: VectorDatabase
        self.structured_memory: Dict[str, Any]
        self.cache: Dict[str, Any]
    
    def store(self, key: str, value: Any, metadata: Dict[str, Any] = None):
        """Store data in memory"""
        pass
    
    def retrieve(self, key: str, query_type: str = "exact") -> Any:
        """Retrieve data from memory"""
        pass
    
    def search(self, query: str, limit: int = 10) -> List[Any]:
        """Search memory using vector similarity"""
        pass
```

### Multilateral Cerebral Protocol (MCP)

#### Protocol Standards
- **Memory Reads/Writes**: Standardized memory access patterns
- **Project Context Injection**: Project-specific context management
- **Provenance Tracking**: Complete audit trail of data flow
- **Inter-Agent Coordination**: Standardized communication protocols

#### MCP Implementation
```python
class MCPProtocol:
    """Multilateral Cerebral Protocol implementation"""
    
    def __init__(self):
        self.memory_manager: MemoryManager
        self.context_injector: ContextInjector
        self.provenance_tracker: ProvenanceTracker
    
    def coordinate_agents(self, agents: List[BaseAgent], workflow: Workflow):
        """Coordinate multiple agents in a workflow"""
        pass
    
    def track_provenance(self, data_id: str, transformations: List[str]):
        """Track data transformations and provenance"""
        pass
```

## LLM Backend Layer

### Model Routing & Management

#### Service Broker
```python
class LLMServiceBroker:
    """Manages LLM routing and fallback"""
    
    def __init__(self):
        self.models: Dict[str, ModelConfig]
        self.affinity_scores: Dict[str, float]
        self.retry_config: RetryConfig
    
    def route_request(self, task_type: str, content: str) -> ModelResponse:
        """Route request to appropriate LLM"""
        pass
    
    def handle_fallback(self, primary_model: str, fallback_model: str) -> ModelResponse:
        """Handle model fallback on failure"""
        pass
```

#### Model Configuration
```python
@dataclass
class ModelConfig:
    """LLM model configuration"""
    name: str
    provider: str
    api_key: str
    endpoint: str
    capabilities: List[str]
    cost_per_token: float
    max_tokens: int
    temperature: float
```

## UI Cockpit Design

### Core Views

#### 1. Agent Dashboard
- All available agents, versions, and status
- Agent health monitoring
- Performance metrics and usage statistics

#### 2. Project Builder
- Drag & drop agents into workflow
- Workflow visualization and editing
- Pipeline configuration and validation

#### 3. Memory Viewer
- Explore project memory and feedback logs
- Memory search and analysis
- Data provenance tracking

#### 4. Job Runner
- Execute, monitor, and debug agent chains
- Real-time execution monitoring
- Error handling and recovery

#### 5. Training Playground
- Fine-tune prompt strategies
- Agent performance optimization
- A/B testing and validation

#### 6. LLM Router Panel
- Assign models per agent/task
- Model performance monitoring
- Cost optimization and routing

#### 7. User Access Portal
- Role-based access control
- Guest/researcher/owner roles
- Permission management

### Technology Stack
- **Frontend**: React + TypeScript
- **Styling**: Tailwind CSS
- **Visualization**: D3.js for agent call stack visualization
- **Real-time**: WebSocket for live updates
- **State Management**: React Context + Redux

## Deployment Architecture

### Deployment Options

#### 1. Local Mode
```bash
python main.py --agent kpi_extractor
python main.py --workflow csr_pipeline
```

#### 2. Notebook Integration
```python
%load_ext agentic.magic
%agentic run --agent kpi_extractor --input "company_data"
```

#### 3. Cloud Run (FastAPI + Uvicorn)
```python
# API-first deployment
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 4. LangChain Integration
```python
from mar.agents import KPIExtractorAgent
from langchain.agents import AgentExecutor

agent = KPIExtractorAgent()
executor = AgentExecutor.from_agent_and_tools(agent)
```

#### 5. CLI Pipeline Builder
```bash
agentic build-pipeline --tasks "search,extract,validate"
agentic run-pipeline --pipeline csr_workflow
```

#### 6. Docker Compose Stack
```yaml
version: '3.8'
services:
  mar-api:
    build: .
    ports:
      - "8000:8000"
  mar-ui:
    build: ./ui
    ports:
      - "3000:3000"
  vector-db:
    image: weaviate/weaviate
    ports:
      - "8080:8080"
```

#### 7. Project Mode
- Projects run in isolated workspaces
- Access to shared modules and agents
- Isolated memory and configuration

## API Architecture

### REST API Endpoints

#### Agent Management
```
GET    /api/v1/agents              # List all agents
GET    /api/v1/agents/{id}         # Get agent details
POST   /api/v1/agents              # Create new agent
PUT    /api/v1/agents/{id}         # Update agent
DELETE /api/v1/agents/{id}         # Delete agent
```

#### Workflow Management
```
GET    /api/v1/workflows            # List workflows
GET    /api/v1/workflows/{id}      # Get workflow details
POST   /api/v1/workflows            # Create workflow
POST   /api/v1/workflows/{id}/run  # Execute workflow
```

#### Memory Management
```
GET    /api/v1/memory              # Search memory
POST   /api/v1/memory              # Store data
GET    /api/v1/memory/{id}         # Retrieve data
DELETE /api/v1/memory/{id}         # Delete data
```

#### Execution Monitoring
```
GET    /api/v1/jobs                # List running jobs
GET    /api/v1/jobs/{id}           # Get job status
POST   /api/v1/jobs/{id}/cancel    # Cancel job
```

### API Authentication
- **JWT Tokens**: Bearer token authentication
- **API Keys**: Service-to-service authentication
- **Role-based Access**: Granular permission control

## Data Flow Architecture

### Agent Execution Flow
1. **Input Validation**: Validate input data and parameters
2. **Context Injection**: Inject project context and memory
3. **LLM Routing**: Route to appropriate LLM based on task
4. **Processing**: Execute agent-specific logic
5. **Memory Update**: Update shared memory with results
6. **Provenance Tracking**: Track data transformations
7. **Output Generation**: Generate structured output

### Workflow Orchestration
1. **Workflow Definition**: Define agent sequence and dependencies
2. **Task Distribution**: Distribute tasks to available agents
3. **Execution Monitoring**: Monitor task execution and progress
4. **Error Handling**: Handle failures and retry logic
5. **Result Aggregation**: Aggregate results from multiple agents
6. **Output Generation**: Generate final workflow output

## Security Architecture

### Access Control
- **Role-based Access Control (RBAC)**: Granular permission management
- **Agent Sandboxing**: Isolated execution environments
- **Memory Isolation**: Project-level memory separation
- **Audit Logging**: Complete audit trail of all operations

### Data Protection
- **Encryption**: Data encryption at rest and in transit
- **Token Management**: Secure API key and token handling
- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: API rate limiting and abuse prevention

## Monitoring & Observability

### Performance Metrics
- **Agent Performance**: Execution time, success rate, error rate
- **LLM Usage**: Token consumption, cost tracking, model performance
- **Memory Usage**: Memory consumption, cache hit rates
- **Workflow Metrics**: Pipeline execution time, throughput

### Health Monitoring
- **Agent Health**: Agent availability and responsiveness
- **Service Health**: API endpoint health and performance
- **Resource Monitoring**: CPU, memory, and storage usage
- **Error Tracking**: Error rates and failure patterns

### Logging & Debugging
- **Structured Logging**: JSON-formatted logs with context
- **Trace Correlation**: Request tracing across agent boundaries
- **Debug Mode**: Step-by-step execution debugging
- **Performance Profiling**: Detailed performance analysis

## Integration Points

### External Systems
- **ESG Data Platforms**: Integration with existing ESG databases
- **Survey Platforms**: Connection to survey management systems
- **Legal Systems**: Integration with legal document management
- **Financial Systems**: Connection to financial data sources

### Internal Dependencies
- **Rank_AI**: ESG KPI extraction integration
- **Nyxion**: Survey and analysis platform integration
- **MCP Protocol**: Multilateral Cerebral Protocol compliance
- **SCIP Framework**: Smart Collaborative Inference Protocol support

## Future Architecture Considerations

### Scalability
- **Horizontal Scaling**: Multiple agent instances and load balancing
- **Vertical Scaling**: Resource optimization and performance tuning
- **Distributed Execution**: Multi-node agent execution
- **Auto-scaling**: Dynamic resource allocation based on demand

### Advanced Features
- **Auto Agent Benchmarking**: Automated agent performance evaluation
- **GPU-aware Routing**: GPU-optimized task distribution
- **Real-time Coordination**: WebSocket-based agent coordination
- **Mobile App Companion**: Mobile dashboard and monitoring
- **AgentChain-as-a-Service**: Enterprise-grade agent orchestration
- **Claude Code Integration**: Shell and task runner integration
- **Audio Processing**: Whisper integration for voice extraction
- **Agentic Debug Mode**: Advanced debugging and workflow analysis
- **GitOps Bridge**: Version control for workflows and outputs

## Development Workflow

### Agent Development
1. **Pattern Discovery**: Scan existing code for reusable patterns
2. **Agent Generation**: Generate agent code from discovered patterns
3. **Interface Implementation**: Implement standard agent interface
4. **Testing & Validation**: Test agent functionality and performance
5. **Documentation**: Document agent capabilities and usage
6. **Integration**: Integrate agent into MAR ecosystem

### Testing Strategy
- **Unit Testing**: Individual agent testing with pytest
- **Integration Testing**: Agent interaction and workflow testing
- **Performance Testing**: Load testing and performance benchmarking
- **Security Testing**: Vulnerability assessment and penetration testing

---

*This documentation reflects the current state of the MAR system. For the most up-to-date information, refer to the running system and configuration files.*
