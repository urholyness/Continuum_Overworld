# MAR - Multilateral Agentic Repo Methodology

## Updated Framework (2025-08-06)

Enhanced after Grok's analysis identified destructive debugging cycles that create cascading problems.

## Core MAR Principles

### M - **Multilateral Analysis**
**NEW**: **Cascade Impact Assessment** - Before any change, analyze all potential effects across the system
- Map component dependencies and relationships
- Identify all stakeholders/systems that could be affected
- **MANDATORY**: Apply root-cause analysis, not symptom treatment
- Use dependency chain mapping from `/Projects/DEBUGGING_GUARDRAILS.md`

### A - **Agentic Resolution** 
**NEW**: **Single-Issue Resolution Protocol** - One agent, one issue, complete resolution before next
- No parallel fixes that could interfere with each other
- Agent must achieve 100% success on assigned issue before handoff
- **State Reset Verification** - Ensure clean state between agent handoffs
- Document what each agent changed and verify it worked

### R - **Repository Integration**
**NEW**: **Layer Isolation Testing** - Test each layer independently before integration
- Each component must pass isolation tests
- Integration only after all components verified individually
- **No simultaneous multi-layer changes**
- Rollback procedures documented for each integration step

## Anti-Cycle Protocols for MAR

### Before Multi-Agent Deployment:
1. **Cycle Detection Check**:
   - Are multiple error types present simultaneously?
   - Have previous agent actions created new problems?
   - Are error patterns repeating or evolving?
   - Is system state corrupted/inconsistent?

2. **If Cycle Detected**: 
   - **HALT all agent operations**
   - Reset to last known working state
   - Apply single-agent diagnostic approach
   - Only deploy multi-agent system after clean state confirmed

### Enhanced MAR Process:

#### M - Multilateral Analysis (Enhanced)
- **System State Assessment**:
  - Current health of all components
  - History of recent changes and their effects  
  - Dependency mapping of proposed changes
  - Risk assessment for cascade failures

- **Agent Assignment Strategy**:
  - One agent per isolated component/layer
  - Clear boundaries and handoff protocols
  - Verification requirements between agents
  - Emergency stop conditions

#### A - Agentic Resolution (Enhanced)
- **Single-Agent Success Criteria**:
  - Agent must completely resolve assigned issue
  - Must verify no new problems introduced
  - Must test component in isolation
  - Must document all changes made
  - **No handoff until 100% verification complete**

- **Agent Coordination Protocol**:
  - Sequential execution, not parallel (during problem resolution)
  - Clear state checkpoints between agents
  - Rollback procedures if any agent fails
  - Communication of changes to downstream agents

#### R - Repository Integration (Enhanced)
- **Layered Integration Approach**:
  1. **Environment Integration** - Dependencies, setup
  2. **Model Integration** - Data structures, schemas
  3. **Database Integration** - Schema, connections  
  4. **API Integration** - Routes, endpoints
  5. **System Integration** - Full workflow

- **Integration Verification**:
  - Each layer tested before next layer added
  - Regression testing of all previous layers
  - Performance impact assessment
  - **Full rollback if any layer fails**

## Agent-Specific Anti-Cycle Guidelines

### For Discovery Agents:
- **Complete discovery** before making any changes
- Map all dependencies before suggesting solutions
- Identify root causes, not just symptoms
- **No quick fixes during discovery phase**

### For Implementation Agents:
- **Minimum viable changes** to address root cause
- Test changes in isolation before integration
- Verify no cascade effects introduced
- **Document exact changes and reasoning**

### For Verification Agents:
- **Independent testing** of each component
- Regression testing of all related systems
- Performance and stability verification
- **No approval until 100% verification complete**

## Success Metrics for MAR

### Individual Agent Success:
- ✅ Complete resolution of assigned issue
- ✅ No new problems introduced
- ✅ Component verified in isolation
- ✅ Clear handoff documentation

### Multi-Agent System Success:
- ✅ All agents completed successfully
- ✅ Clean integration between components
- ✅ Full system functionality verified
- ✅ No recurring issues or cycles

## Failure Recovery Protocol

If MAR process encounters the destructive cycle:

1. **IMMEDIATE HALT** - Stop all agent operations
2. **State Assessment** - Determine last known working state
3. **Root Cause Analysis** - Why did the cycle occur?
4. **Environment Reset** - Clean slate if necessary
5. **Single-Agent Diagnostic** - One issue, one agent, complete resolution
6. **Gradual Multi-Agent Reintroduction** - Only after stability proven

## Integration with Other Frameworks

### SCIP Integration:
- Use SCIP's dependency analysis in MAR's multilateral analysis
- Apply SCIP's layer verification in MAR's integration phase

### MCP Integration:
- Use MCP's diagnostic verification for agent handoffs
- Apply MCP's manual testing protocols for agent verification

---

**Key Principle**: MAR should create stability and systematic resolution, not chaos and cascade failures.

**Last Updated**: 2025-08-06 - After Grok analysis of destructive debugging cycles