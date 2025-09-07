#!/usr/bin/env bash
set -euo pipefail

# WSL2 Bootstrap Script for Continuum_Overworld
# Operating from: /mnt/c/users/password/
# Purpose: Create canonical directory structure following THE_BRIDGE naming standard

ROOT="/mnt/c/users/password/Continuum_Overworld"

echo "🌱 Bootstrapping Continuum_Overworld from WSL2..."
echo "Environment: $(uname -a)"
echo "Working directory: $ROOT"

# Create core directory structure
mkdir -p "$ROOT" \
  "$ROOT/The_Bridge/Console--Core__PROD@" \
  "$ROOT/The_Bridge/Playbooks" \
  "$ROOT/The_Bridge/RFCs" \
  "$ROOT/Pantheon/Orion" \
  "$ROOT/Pantheon/Omen" \
  "$ROOT/Aegis/Audit" \
  "$ROOT/Aegis/Playbooks" \
  "$ROOT/Atlas/Planner--Airfreight__KE-DE@v0.9.2" \
  "$ROOT/Forge/Ingestor--CSRD__EU-DE@v1.6.0" \
  "$ROOT/Forge/Builder--Code__WSL2@v1.0.0" \
  "$ROOT/Forge/Memory--Fabric__PROD@v0.1.0/server" \
  "$ROOT/Forge/Memory--Fabric__PROD@v0.1.0/client" \
  "$ROOT/Forge/Memory--Fabric__PROD@v0.1.0/config" \
  "$ROOT/Forge/Playbooks" \
  "$ROOT/Oracle/Forecaster--Demand__EU-Beans@v2.0.0" \
  "$ROOT/Oracle/Forecaster--ESG__PROD@v1.0.0" \
  "$ROOT/Meridian/Notifier--Companion__PWA@v0.1.0" \
  "$ROOT/Agora/Outreach--Buyers__DE-NL@v0.5.0" \
  "$ROOT/Ledger/Contracts--TermSheets__Global@v0.3.1" \
  "$ROOT/Archive/BACK_BURNER" \
  "$ROOT/.bridge" \
  "$ROOT/scripts" \
  "$ROOT/.github/workflows"

# Create .gitignore
cat > "$ROOT/.gitignore" <<'GIT'
# Global
.DS_Store
.env
*.log
node_modules/
__pycache__/
.venv/
venv/
*.pyc

# Windows
Thumbs.db
desktop.ini

# WSL2
*.sock

# IDE
.vscode/
.idea/
*.swp
*.swo

# Temporary
*.tmp
*.bak
*.cache
GIT

# Create main README
cat > "$ROOT/README.md" <<'MD'
# Continuum_Overworld

Single source of naming truth. Governed by THE_BRIDGE — Naming & Operating Standard v1.0.

## Environment Architecture

- **Claude Code**: Operating in WSL2 (`/mnt/c/users/password/`)
- **Cursor**: Operating in Windows (`C:\Users\Password\`)
- **Shared Filesystem**: Windows drives mounted at `/mnt/c/` in WSL2

## Quick Start

### From WSL2 (Claude Code):
```bash
bash scripts/mk-structure.sh
python3 scripts/bridge-validate.py
```

### From Windows (Cursor/User):
```batch
scripts\mk-structure.bat
python scripts\bridge-validate.py
```

## Division Structure

- **The_Bridge**: Control surface and governance
- **Pantheon**: Agent registry and lifecycle
- **Aegis**: Risk, compliance, validation
- **Atlas**: Planning and logistics
- **Forge**: Building and implementation
- **Oracle**: Forecasting and analysis
- **Meridian**: Notifications and alerts
- **Agora**: Outreach and communication
- **Ledger**: Contracts and records
- **Archive**: Deferred items

## Naming Convention

- Divisions: `Pascal_Snake`
- Files: `kebab-case`
- Versioned: `Component--Role__Qualifier@v<MAJOR>.<MINOR>.<PATCH>`
MD

# Create The_Bridge templates
cat > "$ROOT/The_Bridge/Playbooks/README.md" <<'MD'
# The_Bridge/Playbooks

Operational SOPs and console operations.

## Naming Convention
`Playbook--<Function>__<Scope>@v<semver>.md`

## Template Structure
- Purpose → Context → Inputs → Outputs → Guardrails → Ownership
MD

cat > "$ROOT/The_Bridge/RFCs/README.md" <<'MD'
# The_Bridge/RFCs

Change proposals and architectural decisions.

## Naming Convention
`BRIDGE/RFC--<Title>__<Scope>@v<semver>.md`

## RFC Process
1. Draft proposal
2. Review period
3. Aegis validation
4. Implementation
MD

# Create Pantheon registry
cat > "$ROOT/Pantheon/Registry.json" <<'JSON'
{
  "schema_version": "1.0.0",
  "agents": [
    {
      "id": "claude-code-wsl2",
      "identifier": "Builder--Code__WSL2@v1.0.0",
      "division": "Forge",
      "environment": "WSL2",
      "capabilities": ["scaffold", "implement", "test"],
      "path": "Forge/Builder--Code__WSL2@v1.0.0"
    },
    {
      "id": "cursor-validator-win",
      "identifier": "Validator--Code__WIN@v1.0.0",
      "division": "Aegis",
      "environment": "Windows",
      "capabilities": ["validate", "review", "audit"],
      "path": "Aegis/Validator--Code__WIN@v1.0.0"
    }
  ],
  "components": []
}
JSON

# Create environment configuration
cat > "$ROOT/.bridge/environments.json" <<'JSON'
{
  "claude_code": {
    "type": "WSL2",
    "python": "/usr/bin/python3",
    "shell": "/bin/bash",
    "path_prefix": "/mnt/c/users/password",
    "line_endings": "lf"
  },
  "cursor": {
    "type": "Windows",
    "python": "python",
    "shell": "cmd.exe",
    "path_prefix": "C:\\Users\\Password",
    "line_endings": "crlf"
  },
  "shared": {
    "root": "Continuum_Overworld",
    "encoding": "utf-8",
    "git_autocrlf": "true"
  }
}
JSON

# Create grammar configuration
cat > "$ROOT/.bridge/grammar.json" <<'JSON'
{
  "division_case": "Pascal_Snake",
  "file_case": "kebab-case",
  "label_pattern": "^[A-Z][A-Za-z]*(_[A-Z][a-zA-Z]*)*$",
  "versioned_dir_pattern": "^.+--.+__.+@v\\d+\\.\\d+\\.\\d+/?$",
  "playbook_pattern": "^Playbook--[A-Za-z0-9]+__[^@]+@v\\d+\\.\\d+\\.\\d+\\.md$",
  "rfc_pattern": "^RFC--[A-Za-z0-9]+__[^@]+@v\\d+\\.\\d+\\.\\d+\\.md$",
  "agent_pattern": "^Agent--[A-Za-z0-9_]+:[A-Za-z0-9]+__T[0-5]\\.md$"
}
JSON

# Create .gitattributes for cross-platform line endings
cat > "$ROOT/.gitattributes" <<'GIT'
# Cross-platform line ending configuration
* text=auto

# Unix line endings
*.sh text eol=lf
*.py text eol=lf
*.json text eol=lf
*.md text eol=lf
*.yml text eol=lf
*.yaml text eol=lf

# Windows line endings
*.bat text eol=crlf
*.cmd text eol=crlf
*.ps1 text eol=crlf

# Binary files
*.png binary
*.jpg binary
*.pdf binary
*.exe binary
GIT

# Create initial Aegis playbook
cat > "$ROOT/Aegis/Playbooks/Playbook--KYF__PROD@v1.1.0.md" <<'MD'
# Aegis/Playbook--KYF__PROD@v1.1.0

**Title**: Know Your Framework  
**Owner**: Aegis  
**Risk Gate**: T2  
**SLA**: 30 minutes  

## Purpose
Validate all code submissions against THE_BRIDGE naming standards and security requirements.

## Context
Cross-platform validation between WSL2 (Claude Code) and Windows (Cursor).

## Inputs
- Code changes from Forge
- RFC proposals from The_Bridge
- Agent specifications from Pantheon

## Outputs
- Validation report
- Compliance score
- Risk assessment

## Guardrails
- Reject non-conformant naming
- Block unsafe code patterns
- Enforce versioning standards

## Ownership
Primary: Aegis/Validator--Code__WIN@v1.0.0 (Cursor)
Secondary: The_Bridge/Console--Core__PROD@
MD

# Create sample agent spec
cat > "$ROOT/Pantheon/Orion/Agent--Prospector_Miner:ESG__T2.md" <<'MD'
# Agent--Prospector_Miner:ESG__T2

**Agent**: Prospector_Miner:ESG__T2  
**Division**: Oracle  
**Tier**: T2 (Supervised Autonomy)  

## Inputs
- Company names
- Reporting years
- ESG frameworks

## Actions
- Search for ESG reports
- Extract KPI data
- Validate findings
- Generate insights

## Constraints
- Rate limits: 100 requests/hour
- Data retention: 30 days
- PII handling: Redact personal information

## Escalation
- T3 approval for >1000 companies
- Manual review for disputed data
- Aegis audit for compliance issues

## Metrics
- Precision: >95%
- Recall: >90%
- SLA: 5 minutes per company
MD

# Make script executable
chmod +x "$ROOT/scripts/mk-structure.sh"

echo "✅ WSL2 scaffold created successfully!"
echo ""
echo "📁 Structure created under: $ROOT"
echo "🔧 Next steps:"
echo "  1. Run validation: python3 $ROOT/scripts/bridge-validate.py"
echo "  2. Create Windows bootstrap: $ROOT/scripts/mk-structure.bat"
echo "  3. Initialize git repository: cd $ROOT && git init"
echo ""
echo "🌉 Cross-platform bridge ready for WSL2 ↔ Windows collaboration"