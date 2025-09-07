#!/bin/bash
# STOP→FIX→TEST Protocol Orchestrator (WSL2/Linux)
# Enforces disciplined debugging workflow

set -euo pipefail

ROOT="/mnt/c/users/password/Continuum_Overworld"
INCIDENTS_DIR="$ROOT/Aegis/Incidents"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Phase tracking
PHASE="${1:-}"
STAGE="${2:-}"
SLUG="${3:-}"

function print_header() {
    echo -e "\n${GREEN}═══════════════════════════════════════════${NC}"
    echo -e "${GREEN}    $1${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════${NC}\n"
}

function print_error() {
    echo -e "${RED}❌ $1${NC}"
}

function print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

function print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# STOP Phase
function stop_phase() {
    print_header "🛑 STOP PHASE"
    
    if [ -z "$STAGE" ] || [ -z "$SLUG" ]; then
        print_error "Usage: $0 stop <stage> <slug>"
        exit 1
    fi
    
    # 1. Freeze the stage
    echo "Freezing stage: $STAGE"
    STAGE_CONFIG=$(find "$ROOT" -name "*$STAGE*" -type d | head -1)
    
    if [ -d "$STAGE_CONFIG" ]; then
        cat > "$STAGE_CONFIG/freeze.json" <<EOF
{
  "enabled": false,
  "frozen_reason": "INC-$(date +%Y%m%d)-$SLUG",
  "frozen_by": "Builder--Code__WSL2@v1.0.0",
  "frozen_at": "$TIMESTAMP"
}
EOF
        print_success "Stage frozen: $STAGE"
    else
        print_warning "Stage directory not found, creating freeze marker"
        touch "$ROOT/.freeze-$STAGE"
    fi
    
    # 2. Create incident
    INCIDENT_ID="INC-$(date +%Y%m%d)-$SLUG"
    INCIDENT_FILE="$INCIDENTS_DIR/$INCIDENT_ID.md"
    
    mkdir -p "$INCIDENTS_DIR"
    
    cat > "$INCIDENT_FILE" <<EOF
# Incident: $INCIDENT_ID

**Status**: ACTIVE  
**Severity**: P2  
**Stage**: $STAGE  
**Created**: $TIMESTAMP  
**Last Good Run**: [TO BE FILLED]  

## Symptoms
- [Describe exact error]
- [Affected scope]
- [Failure rate]

## Scope  
- Components impacted: $STAGE
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
EOF
    
    print_success "Incident created: $INCIDENT_FILE"
    
    # 3. Create failing test template
    TEST_FILE="$ROOT/tests/test_${STAGE}_incident_$(date +%Y%m%d).py"
    mkdir -p "$ROOT/tests"
    
    cat > "$TEST_FILE" <<EOF
#!/usr/bin/env python3
"""
Failing test for incident: $INCIDENT_ID
This test MUST fail until the fix is applied
"""

import pytest

def test_reproduces_incident_$(date +%Y%m%d)():
    """
    Reproduces the issue in $STAGE
    
    Expected: [describe expected behavior]
    Actual: [describe actual failure]
    """
    # TODO: Add minimal reproduction code
    
    # This assertion should fail until fix is applied
    assert False, "Issue in $STAGE: [DESCRIBE THE ISSUE]"
    
    
# Run with: pytest $TEST_FILE -v
EOF
    
    print_success "Test template created: $TEST_FILE"
    
    # Mark incident as active
    echo "$INCIDENT_ID" > "$INCIDENTS_DIR/ACTIVE"
    
    print_header "Next Steps:"
    echo "1. Fill in the incident details: $INCIDENT_FILE"
    echo "2. Implement the failing test: $TEST_FILE"
    echo "3. Run: $0 fix $STAGE $SLUG"
}

# FIX Phase
function fix_phase() {
    print_header "🔧 FIX PHASE"
    
    if [ -z "$STAGE" ] || [ -z "$SLUG" ]; then
        print_error "Usage: $0 fix <stage> <slug>"
        exit 1
    fi
    
    INCIDENT_ID="INC-$(date +%Y%m%d)-$SLUG"
    INCIDENT_FILE="$INCIDENTS_DIR/$INCIDENT_ID.md"
    
    if [ ! -f "$INCIDENT_FILE" ]; then
        print_error "Incident not found: $INCIDENT_FILE"
        echo "Run '$0 stop $STAGE $SLUG' first"
        exit 1
    fi
    
    print_success "Working on incident: $INCIDENT_ID"
    
    # Check for bypass flags
    echo "Checking for bypass flags..."
    if grep -r "skip_validation\|ignore_consensus\|bypass_checks" "$ROOT" --include="*.json" --include="*.py"; then
        print_error "Bypass flags detected! Remove them before proceeding."
        exit 1
    fi
    
    print_success "No bypass flags found"
    
    # Validate naming compliance
    echo "Running naming validation..."
    python3 "$ROOT/The_Bridge/Scripts_Bootstrap/bridge-validate.py"
    
    print_header "Fix Guidelines:"
    echo "1. Fix ONLY in the owning stage: $STAGE"
    echo "2. Remove any dead code"
    echo "3. Add metrics if visibility is poor"
    echo "4. Update contracts if schema changed"
    echo ""
    echo "After applying fix, run: $0 test $STAGE $SLUG"
}

# TEST Phase  
function test_phase() {
    print_header "🧪 TEST PHASE"
    
    if [ -z "$STAGE" ] || [ -z "$SLUG" ]; then
        print_error "Usage: $0 test <stage> <slug>"
        exit 1
    fi
    
    INCIDENT_ID="INC-$(date +%Y%m%d)-$SLUG"
    INCIDENT_FILE="$INCIDENTS_DIR/$INCIDENT_ID.md"
    TEST_FILE="$ROOT/tests/test_${STAGE}_incident_$(date +%Y%m%d).py"
    
    # 1. Run the incident test
    echo "Running incident test..."
    if python3 -m pytest "$TEST_FILE" -v; then
        print_success "Incident test now passes!"
    else
        print_error "Incident test still failing - fix incomplete"
        exit 1
    fi
    
    # 2. Run validation
    echo "Running structure validation..."
    python3 "$ROOT/The_Bridge/Scripts_Bootstrap/bridge-validate.py"
    
    # 3. Check for bypass flags again
    echo "Final bypass flag check..."
    if grep -r "skip_validation\|ignore_consensus\|bypass_checks" "$ROOT" --include="*.json" --include="*.py" --exclude-dir=tests; then
        print_error "Bypass flags still present!"
        exit 1
    fi
    
    # 4. Unfreeze stage
    STAGE_CONFIG=$(find "$ROOT" -name "*$STAGE*" -type d | head -1)
    if [ -f "$STAGE_CONFIG/freeze.json" ]; then
        rm "$STAGE_CONFIG/freeze.json"
        print_success "Stage unfrozen: $STAGE"
    fi
    
    if [ -f "$ROOT/.freeze-$STAGE" ]; then
        rm "$ROOT/.freeze-$STAGE"
    fi
    
    # 5. Close incident
    sed -i 's/ACTIVE/RESOLVED/g' "$INCIDENT_FILE"
    echo "" >> "$INCIDENT_FILE"
    echo "**Resolved**: $TIMESTAMP" >> "$INCIDENT_FILE"
    echo "**Resolution Time**: [CALCULATE]" >> "$INCIDENT_FILE"
    
    # Remove active marker
    rm -f "$INCIDENTS_DIR/ACTIVE"
    
    print_success "Incident resolved: $INCIDENT_ID"
    
    # Create metrics entry
    METRICS_FILE="$INCIDENTS_DIR/metrics.json"
    if [ ! -f "$METRICS_FILE" ]; then
        echo "[]" > "$METRICS_FILE"
    fi
    
    print_header "✅ STOP→FIX→TEST Complete!"
    echo "Incident $INCIDENT_ID has been resolved."
    echo "Remember to:"
    echo "1. Update incident with final details"
    echo "2. Commit the test that caught this issue"
    echo "3. Document lessons learned"
}

# Main dispatcher
case "$PHASE" in
    stop)
        stop_phase
        ;;
    fix)
        fix_phase
        ;;
    test)
        test_phase
        ;;
    *)
        print_header "STOP→FIX→TEST Protocol"
        echo "Usage: $0 <phase> <stage> <slug>"
        echo ""
        echo "Phases:"
        echo "  stop  - Freeze stage, create incident, add test"
        echo "  fix   - Validate fix approach, check compliance"
        echo "  test  - Run tests, unfreeze, close incident"
        echo ""
        echo "Example:"
        echo "  $0 stop Oracle/Forecaster esg-timeout"
        echo "  $0 fix Oracle/Forecaster esg-timeout"
        echo "  $0 test Oracle/Forecaster esg-timeout"
        exit 1
        ;;
esac