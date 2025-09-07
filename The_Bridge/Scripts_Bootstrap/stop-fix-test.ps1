# STOP→FIX→TEST Protocol Orchestrator (Windows PowerShell)
# Enforces disciplined debugging workflow

param(
    [Parameter(Position=0)]
    [string]$Phase,
    
    [Parameter(Position=1)]
    [string]$Stage,
    
    [Parameter(Position=2)]
    [string]$Slug
)

$Root = "C:\Users\Password\Continuum_Overworld"
$IncidentsDir = "$Root\Aegis\Incidents"
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

# Color functions
function Write-Success { Write-Host "✅ $args" -ForegroundColor Green }
function Write-Error { Write-Host "❌ $args" -ForegroundColor Red }
function Write-Warning { Write-Host "⚠️  $args" -ForegroundColor Yellow }
function Write-Header { 
    Write-Host "`n═══════════════════════════════════════════" -ForegroundColor Green
    Write-Host "    $args" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════`n" -ForegroundColor Green
}

# STOP Phase
function Stop-Phase {
    Write-Header "🛑 STOP PHASE"
    
    if (-not $Stage -or -not $Slug) {
        Write-Error "Usage: .\stop-fix-test.ps1 stop <stage> <slug>"
        exit 1
    }
    
    # 1. Freeze the stage
    Write-Host "Freezing stage: $Stage"
    $StageConfig = Get-ChildItem -Path $Root -Directory -Recurse | Where-Object { $_.Name -like "*$Stage*" } | Select-Object -First 1
    
    if ($StageConfig) {
        $FreezeJson = @{
            enabled = $false
            frozen_reason = "INC-$(Get-Date -Format 'yyyyMMdd')-$Slug"
            frozen_by = "Validator--Code__WIN@v1.0.0"
            frozen_at = $Timestamp
        } | ConvertTo-Json
        
        Set-Content -Path "$($StageConfig.FullName)\freeze.json" -Value $FreezeJson
        Write-Success "Stage frozen: $Stage"
    } else {
        Write-Warning "Stage directory not found, creating freeze marker"
        New-Item -Path "$Root\.freeze-$Stage" -ItemType File -Force | Out-Null
    }
    
    # 2. Create incident
    $IncidentId = "INC-$(Get-Date -Format 'yyyyMMdd')-$Slug"
    $IncidentFile = "$IncidentsDir\$IncidentId.md"
    
    if (-not (Test-Path $IncidentsDir)) {
        New-Item -Path $IncidentsDir -ItemType Directory -Force | Out-Null
    }
    
    $IncidentContent = @"
# Incident: $IncidentId

**Status**: ACTIVE  
**Severity**: P2  
**Stage**: $Stage  
**Created**: $Timestamp  
**Last Good Run**: [TO BE FILLED]  

## Symptoms
- [Describe exact error]
- [Affected scope]
- [Failure rate]

## Scope  
- Components impacted: $Stage
- Downstream effects: [TO BE FILLED]
- Data at risk: [TO BE FILLED]

## Suspected Area
- Code region: [TO BE FILLED]
- Recent changes: [CHECK GIT LOG]
- External dependencies: [TO BE FILLED]

## Root Cause
**Hypothesis**: [TO BE FILLED]  
**Code Location**: [file:line]  
**Evidence**: [logs, traces]  

## Resolution
- Test added: [ ]
- Fix applied: [ ]
- Validated: [ ]
"@
    
    Set-Content -Path $IncidentFile -Value $IncidentContent
    Write-Success "Incident created: $IncidentFile"
    
    # 3. Create failing test template
    $TestFile = "$Root\tests\test_${Stage}_incident_$(Get-Date -Format 'yyyyMMdd').py"
    if (-not (Test-Path "$Root\tests")) {
        New-Item -Path "$Root\tests" -ItemType Directory -Force | Out-Null
    }
    
    $TestContent = @"
#!/usr/bin/env python3
"""
Failing test for incident: $IncidentId
This test MUST fail until the fix is applied
"""

import pytest

def test_reproduces_incident_$(Get-Date -Format 'yyyyMMdd')():
    """
    Reproduces the issue in $Stage
    
    Expected: [describe expected behavior]
    Actual: [describe actual failure]
    """
    # TODO: Add minimal reproduction code
    
    # This assertion should fail until fix is applied
    assert False, "Issue in $Stage: [DESCRIBE THE ISSUE]"
    
    
# Run with: pytest $TestFile -v
"@
    
    Set-Content -Path $TestFile -Value $TestContent
    Write-Success "Test template created: $TestFile"
    
    # Mark incident as active
    Set-Content -Path "$IncidentsDir\ACTIVE" -Value $IncidentId
    
    Write-Header "Next Steps:"
    Write-Host "1. Fill in the incident details: $IncidentFile"
    Write-Host "2. Implement the failing test: $TestFile"
    Write-Host "3. Run: .\stop-fix-test.ps1 fix $Stage $Slug"
}

# FIX Phase
function Fix-Phase {
    Write-Header "🔧 FIX PHASE"
    
    if (-not $Stage -or -not $Slug) {
        Write-Error "Usage: .\stop-fix-test.ps1 fix <stage> <slug>"
        exit 1
    }
    
    $IncidentId = "INC-$(Get-Date -Format 'yyyyMMdd')-$Slug"
    $IncidentFile = "$IncidentsDir\$IncidentId.md"
    
    if (-not (Test-Path $IncidentFile)) {
        Write-Error "Incident not found: $IncidentFile"
        Write-Host "Run '.\stop-fix-test.ps1 stop $Stage $Slug' first"
        exit 1
    }
    
    Write-Success "Working on incident: $IncidentId"
    
    # Check for bypass flags
    Write-Host "Checking for bypass flags..."
    $BypassFlags = Get-ChildItem -Path $Root -Include "*.json","*.py" -Recurse | 
        Select-String -Pattern "skip_validation|ignore_consensus|bypass_checks"
    
    if ($BypassFlags) {
        Write-Error "Bypass flags detected! Remove them before proceeding."
        $BypassFlags | ForEach-Object { Write-Host "  $_" }
        exit 1
    }
    
    Write-Success "No bypass flags found"
    
    # Validate naming compliance
    Write-Host "Running naming validation..."
    python "$Root\The_Bridge\Scripts_Bootstrap\bridge-validate.py"
    
    Write-Header "Fix Guidelines:"
    Write-Host "1. Fix ONLY in the owning stage: $Stage"
    Write-Host "2. Remove any dead code"
    Write-Host "3. Add metrics if visibility is poor"
    Write-Host "4. Update contracts if schema changed"
    Write-Host ""
    Write-Host "After applying fix, run: .\stop-fix-test.ps1 test $Stage $Slug"
}

# TEST Phase
function Test-Phase {
    Write-Header "🧪 TEST PHASE"
    
    if (-not $Stage -or -not $Slug) {
        Write-Error "Usage: .\stop-fix-test.ps1 test <stage> <slug>"
        exit 1
    }
    
    $IncidentId = "INC-$(Get-Date -Format 'yyyyMMdd')-$Slug"
    $IncidentFile = "$IncidentsDir\$IncidentId.md"
    $TestFile = "$Root\tests\test_${Stage}_incident_$(Get-Date -Format 'yyyyMMdd').py"
    
    # 1. Run the incident test
    Write-Host "Running incident test..."
    $TestResult = python -m pytest $TestFile -v 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Incident test now passes!"
    } else {
        Write-Error "Incident test still failing - fix incomplete"
        Write-Host $TestResult
        exit 1
    }
    
    # 2. Run validation
    Write-Host "Running structure validation..."
    python "$Root\The_Bridge\Scripts_Bootstrap\bridge-validate.py"
    
    # 3. Check for bypass flags again
    Write-Host "Final bypass flag check..."
    $BypassFlags = Get-ChildItem -Path $Root -Include "*.json","*.py" -Exclude "test_*.py" -Recurse | 
        Select-String -Pattern "skip_validation|ignore_consensus|bypass_checks"
    
    if ($BypassFlags) {
        Write-Error "Bypass flags still present!"
        exit 1
    }
    
    # 4. Unfreeze stage
    $StageConfig = Get-ChildItem -Path $Root -Directory -Recurse | Where-Object { $_.Name -like "*$Stage*" } | Select-Object -First 1
    if ($StageConfig -and (Test-Path "$($StageConfig.FullName)\freeze.json")) {
        Remove-Item "$($StageConfig.FullName)\freeze.json"
        Write-Success "Stage unfrozen: $Stage"
    }
    
    if (Test-Path "$Root\.freeze-$Stage") {
        Remove-Item "$Root\.freeze-$Stage"
    }
    
    # 5. Close incident
    $Content = Get-Content $IncidentFile
    $Content = $Content -replace "ACTIVE", "RESOLVED"
    $Content += "`n**Resolved**: $Timestamp"
    $Content += "`n**Resolution Time**: [CALCULATE]"
    Set-Content -Path $IncidentFile -Value $Content
    
    # Remove active marker
    if (Test-Path "$IncidentsDir\ACTIVE") {
        Remove-Item "$IncidentsDir\ACTIVE"
    }
    
    Write-Success "Incident resolved: $IncidentId"
    
    Write-Header "✅ STOP→FIX→TEST Complete!"
    Write-Host "Incident $IncidentId has been resolved."
    Write-Host "Remember to:"
    Write-Host "1. Update incident with final details"
    Write-Host "2. Commit the test that caught this issue"
    Write-Host "3. Document lessons learned"
}

# Main dispatcher
switch ($Phase) {
    "stop" { Stop-Phase }
    "fix" { Fix-Phase }
    "test" { Test-Phase }
    default {
        Write-Header "STOP→FIX→TEST Protocol"
        Write-Host "Usage: .\stop-fix-test.ps1 <phase> <stage> <slug>"
        Write-Host ""
        Write-Host "Phases:"
        Write-Host "  stop  - Freeze stage, create incident, add test"
        Write-Host "  fix   - Validate fix approach, check compliance"
        Write-Host "  test  - Run tests, unfreeze, close incident"
        Write-Host ""
        Write-Host "Example:"
        Write-Host "  .\stop-fix-test.ps1 stop Oracle\Forecaster esg-timeout"
        Write-Host "  .\stop-fix-test.ps1 fix Oracle\Forecaster esg-timeout"
        Write-Host "  .\stop-fix-test.ps1 test Oracle\Forecaster esg-timeout"
        exit 1
    }
}