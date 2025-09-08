# MCP Init Instructions

Claude Code Initialization Protocol:

## 1. On Session Start:
- Load global memory from: `MCP/agents/claude_code.json`
- Load project-specific memory from: `[project_folder]/memory.json`
- Merge both into current working context
- If memory exceeds token window, compress older notes

## 2. During Session:
- Append context updates to both memory files as major changes occur
- Track environment states, database connections, and API usage
- Log security events and credential access attempts
- Monitor virtual environment status and dependencies

## 3. On Session End:
- Update timestamp in both memory files
- Log session summary to `MCP/logs/session_[timestamp].json`
- Sync project contexts and security status
- Archive completed tasks and update project statuses

## Project Architecture Overview

### Active Projects:
- **Orion**: Multi-agent AI automation system (Python/FastAPI/React)
- **Stat-R_AI**: ESG analytics platform with AI/ML pipeline (Python/Streamlit)
- **Vifungu**: API key storage (⚠️ SECURITY CONCERN: plaintext keys)

### Infrastructure Tracking:
- **Virtual Environments**: 3 Python venvs across Stat-R_AI
- **Databases**: SQLite files in Stat-R_AI/esg_kpi_mvp/
- **Configuration Files**: .env files, JSON configs
- **API Integrations**: OpenAI, Anthropic, Google Cloud, GitHub

### Security Items:
🚨 **CRITICAL**: Vifungu/Keys.md contains exposed GitHub API key
- Requires immediate encryption or migration to environment variables
- Should be integrated with secure credential management system

### Memory Management:
- **Global Context**: MCP/agents/claude_code.json
- **Project Context**: [project]/memory.json per project
- **Session Logs**: MCP/logs/ for historical tracking
- **Compression**: Automatic when token limits approached

### Enhanced Features:
- Environment configuration tracking
- Database connection management  
- API credential security monitoring
- Virtual environment state management
- Cross-project testing coordination

## Usage Notes:
- Always load both global and project memory at session start
- Update timestamps on any significant changes
- Prioritize security concerns in all operations
- Maintain detailed logs for audit trails