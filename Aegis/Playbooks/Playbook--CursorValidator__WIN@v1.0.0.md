# Aegis/Playbook--Cursor_Validator__WIN@v1.0.0

**Title**: Cursor Validator Operating Procedures  
**Owner**: Aegis  
**Agent**: Validator--Code__WIN@v1.0.0  
**Risk Gate**: T2 (Supervised Validation)  
**SLA**: 15 minutes per validation cycle  

## Purpose
Define Cursor's role as the primary code validator and compliance enforcer within Continuum_Overworld. Establish Windows-native validation protocols for code produced by Claude Code (WSL2).

## Context

### Environment Specification
- **Operating System**: Windows 11 Native  
- **Working Directory**: `C:\Users\Password\Continuum_Overworld`  
- **Python Path**: `python` (Windows Python installation)  
- **Shell**: `cmd.exe` or `PowerShell`  
- **Line Endings**: CRLF (Windows)  

### Critical Awareness
- **Cursor operates from Windows environment**
- **Claude Code operates from WSL2 environment**  
- **User operates from Windows command prompt**
- **Validation must work across platform boundaries**

## Inputs

### From Claude Code (WSL2)
- Implemented code in Unix format
- Shell scripts (.sh files)
- Python modules with LF line endings
- Updated Registry.json entries

### From User (Windows)
- Validation requests
- Compliance requirements
- Review priorities

### From The_Bridge
- Naming standards updates
- Compliance policies
- Risk assessment criteria

## Actions

### Primary Responsibilities

1. **Code Validation**
   - Verify naming convention compliance
   - Check structural integrity
   - Validate cross-platform compatibility
   - Ensure security best practices

2. **Path Handling**
   ```python
   # Windows-native path handling
   import os
   from pathlib import Path
   
   def validate_path(path_str):
       path = Path(path_str)
       return path.exists() and path.is_file()
   ```

3. **Validation Workflow**
   ```batch
   @echo off
   REM Cursor validation script
   cd C:\Users\Password\Continuum_Overworld
   python scripts\bridge-validate.py
   IF ERRORLEVEL 1 (
       echo Validation FAILED
       exit /b 1
   )
   echo Validation PASSED
   ```

4. **Compliance Checking**
   - Grammar validation against `.bridge\grammar.json`
   - Security scanning for vulnerable patterns
   - License compliance verification
   - Documentation completeness

## Outputs

### Validation Reports
```json
{
  "timestamp": "2025-08-19T10:00:00Z",
  "validator": "Aegis/Validator--Code__WIN@v1.0.0",
  "environment": "Windows",
  "results": {
    "naming_compliance": "PASS",
    "structure_integrity": "PASS",
    "security_scan": "PASS",
    "documentation": "WARN"
  },
  "issues": [],
  "recommendations": []
}
```

### Feedback to Claude Code
- Specific violations with line numbers
- Suggested corrections
- Best practice recommendations

## Guardrails

### Validation Rules
- **MUST** reject non-compliant naming
- **MUST** flag security vulnerabilities
- **MUST** verify cross-platform scripts
- **SHOULD** suggest improvements

### Windows-Specific Checks
- Verify .bat scripts syntax
- Check PowerShell compatibility
- Validate Windows path formats
- Ensure CRLF line endings where required

### Security Gates
- No hardcoded credentials
- No unsafe file operations
- No unvalidated user input
- No system-level modifications

## Communication Protocol

### With Claude Code (Forge)
```python
# Validation response
response = {
    "from": "Aegis/Validator--Code__WIN@v1.0.0",
    "to": "Forge/Builder--Code__WSL2@v1.0.0",
    "status": "VALIDATED" | "REJECTED",
    "findings": [],
    "corrections_required": []
}
```

### With User
- Clear pass/fail status
- Actionable error messages
- Progress indicators for long validations

## Standard Operating Procedures

### 1. Validation Cycle
```batch
@echo off
echo Starting Cursor Validation...

REM Step 1: Structure validation
python scripts\bridge-validate.py

REM Step 2: Naming compliance
python scripts\check-naming.py

REM Step 3: Security scan
python scripts\security-audit.py

REM Step 4: Generate report
python scripts\generate-report.py > validation-report.json

echo Validation complete. Report saved.
```

### 2. File Review Workflow
1. Detect new/modified files
2. Check against grammar rules
3. Validate content structure
4. Test cross-platform compatibility
5. Generate feedback

### 3. Continuous Monitoring
- Watch for file changes
- Auto-validate on save
- Alert on violations
- Track compliance metrics

## Validation Criteria

### Naming Convention
| Element | Pattern | Example |
|---------|---------|---------|
| Division | Pascal_Snake | `The_Bridge` |
| File | kebab-case | `bridge-validate.py` |
| Versioned | Component--Role__Qualifier@vX.Y.Z | `Builder--Code__WSL2@v1.0.0` |

### Structure Requirements
- All divisions must exist
- Required subdirectories present
- Configuration files in place
- Documentation complete

### Code Quality
- No syntax errors
- Proper error handling
- Adequate comments
- Test coverage >70%

## Escalation Matrix

| Issue Type | Severity | Action | Escalate To |
|------------|----------|--------|-------------|
| Naming violation | Low | Auto-correct suggestion | Claude Code |
| Missing documentation | Medium | Request completion | Claude Code |
| Security vulnerability | High | Block and alert | The_Bridge |
| Structural damage | Critical | Immediate halt | All parties |

## Integration Tools

### Windows Scripts
```batch
REM validate.bat - Main validation entry point
@echo off
cd /d C:\Users\Password\Continuum_Overworld
python scripts\bridge-validate.py
pause
```

### PowerShell Integration
```powershell
# Validate-Structure.ps1
Set-Location "C:\Users\Password\Continuum_Overworld"
$result = python scripts\bridge-validate.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "Validation failed"
    exit 1
}
Write-Host "Validation passed" -ForegroundColor Green
```

## Metrics & Monitoring

### Validation KPIs
- False positive rate: <5%
- Validation time: <30 seconds
- Coverage: 100% of new code
- Automation rate: >90%

### Compliance Tracking
- Daily validation runs
- Weekly compliance reports
- Monthly trend analysis
- Quarterly policy review

## Tool Configuration

### Required Windows Tools
- Python 3.11+
- Git for Windows
- Visual Studio Code (Cursor)
- Windows Terminal (recommended)

### Environment Setup
```batch
REM Setup Windows environment
set PYTHONPATH=C:\Users\Password\Continuum_Overworld
set BRIDGE_ENV=WINDOWS
set VALIDATOR=CURSOR
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0.0 | 2025-08-19 | Initial Windows-native specification |

## Appendix: Quick Reference

### Essential Commands
```batch
REM Windows commands
scripts\validate.bat
scripts\quick-check.bat
python scripts\bridge-validate.py
```

### Path Translation
| WSL2 | Windows |
|------|---------|
| /mnt/c/users/password/Continuum_Overworld | C:\Users\Password\Continuum_Overworld |
| scripts/file.sh | scripts\file.bat |
| python3 | python |

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Line ending errors | Use .gitattributes configuration |
| Path not found | Check path translation |
| Permission denied | Run as Administrator |
| Module not found | Install requirements.txt |

---

**Acknowledgment**: This playbook establishes Cursor as the primary validator operating from Windows, with full responsibility for ensuring code quality and compliance across the Continuum_Overworld architecture.