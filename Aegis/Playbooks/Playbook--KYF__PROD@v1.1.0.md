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
