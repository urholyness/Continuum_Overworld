# The_Bridge/Playbook--StopFixTest__PROD@v1.0.0

**Title**: STOP→FIX→TEST Protocol  
**Owner**: The_Bridge  
**Risk Gate**: T1 (Mandatory)  
**SLA**: 4 hours max per incident  

## Purpose
Enforce disciplined debugging with root-cause analysis, test-first fixes, and validation gates.

## Context
When any pipeline stage fails in production, this protocol ensures systematic resolution without hot patches or bypass flags.

## STOP Phase (15 minutes)

### 1. Freeze Failing Stage
```json
// In stage config
{
  "enabled": false,
  "frozen_reason": "INC-YYYYMMDD-<slug>",
  "frozen_by": "Builder--Code__WSL2@v1.0.0"
}
```

### 2. Create Incident
Create `Aegis/Incidents/INC-YYYYMMDD-<slug>.md`:

```markdown
# Incident: INC-YYYYMMDD-<slug>

**Status**: ACTIVE  
**Severity**: P1/P2/P3  
**Stage**: <Division>/<Capability>  
**Last Good Run**: <timestamp>  

## Symptoms
- Exact error message
- Affected companies/data
- Failure rate

## Scope
- Components impacted
- Downstream effects
- Data at risk

## Suspected Area
- Code region
- Recent changes
- External dependencies
```

### 3. Add Failing Test
Create test that reproduces the issue:
```python
# test_<stage>_incident_<date>.py
def test_reproduces_incident_YYYYMMDD():
    """This test MUST fail until fix is applied"""
    # Minimal repro
    assert False, "Issue: <description>"
```

## FIX Phase (2 hours)

### 1. Root Cause Analysis
Document in incident:
```markdown
## Root Cause
**Hypothesis**: <what broke and why>
**Code Location**: <file:line>
**Evidence**: <logs, traces, data>
```

### 2. Minimal Fix
Rules:
- Fix ONLY in owning stage
- Remove dead code
- Add metrics if visibility poor
- Update contracts if schema changed

### 3. Schema Changes
If data model changes required:
```python
# migrations/<stage>_YYYYMMDD_<description>.py
def migrate_up():
    """Apply schema change"""
    pass

def migrate_down():
    """Rollback schema change"""
    pass
```

## TEST Phase (1.5 hours)

### 1. Unit Tests
```bash
# WSL2/Linux
cd <stage_directory>
python -m pytest test_<stage>_incident_<date>.py -v
```

### 2. Contract Tests
```bash
# Validate interfaces
python The_Bridge/Scripts_Bootstrap/validate-contracts.py <stage>
```

### 3. Integration Test
```bash
# Run bridge validation
python The_Bridge/Scripts_Bootstrap/bridge-validate.py

# Stage-specific integration
python <stage>/run_integration.py --canary "<test_company>"
```

### 4. Canary Deployment
```python
# Single company test
{
  "stage_config": {
    "enabled": true,
    "canary_mode": true,
    "canary_targets": ["Test Company Inc"],
    "canary_compare": true
  }
}
```

### 5. Diff Validation
```bash
# Compare outputs
diff <last_good_output> <canary_output> > validation.diff
```

## Validation Gates

### Claude (Builder) Responsibilities
✅ Write failing test FIRST  
✅ Document root cause with code pointers  
✅ Keep changes scoped to owning stage  
✅ No bypass flags in production  
✅ Update incident with resolution  

### Cursor (Validator) Responsibilities
✅ Verify stage actually frozen in CI  
✅ Confirm new failing test exists and passes  
✅ Check no bypass flags remain  
✅ Validate naming compliance  
✅ Ensure contract tests pass  

## Escalation Rules

| Condition | Action | Escalate To |
|-----------|--------|-------------|
| Cannot reproduce | Document attempts | Aegis + Oracle |
| Cross-stage fix needed | RFC required | The_Bridge |
| Schema change | Migration review | Aegis |
| Data loss risk | Immediate freeze | All parties |
| >4 hour resolution | Status update | Management |

## Bypass Prevention

**Forbidden in PROD**:
```python
# NEVER in production configs
"skip_validation": true
"ignore_consensus": true  
"bypass_checks": true
"force_continue": true
```

## Metrics Collection

Each incident must update:
```json
{
  "incident_id": "INC-YYYYMMDD-<slug>",
  "detection_time": "<timestamp>",
  "resolution_time": "<timestamp>",
  "root_cause": "<category>",
  "stages_affected": ["<stage1>", "<stage2>"],
  "test_added": true,
  "schema_changed": false,
  "downstream_impact": "<description>"
}
```

## Closure Criteria

Incident closes when:
1. ✅ Failing test now passes
2. ✅ Integration tests green
3. ✅ Canary validation complete
4. ✅ No bypass flags in code
5. ✅ Incident documented
6. ✅ Metrics recorded

## Automation Hooks

### Pre-commit
```bash
# .git/hooks/pre-commit
if grep -r "bypass\|skip_validation\|ignore_consensus" --include="*.json"; then
  echo "❌ Bypass flags detected in config"
  exit 1
fi
```

### CI Pipeline
```yaml
- name: Check for active incidents
  run: |
    if [ -f "Aegis/Incidents/ACTIVE" ]; then
      echo "⚠️ Active incident - validating fix"
      python The_Bridge/Scripts_Bootstrap/validate-incident-fix.py
    fi
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0.0 | 2025-08-19 | Initial STOP→FIX→TEST protocol |

---

**Enforcement**: This protocol is **mandatory** for all production failures. No exceptions.