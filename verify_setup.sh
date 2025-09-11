#!/bin/bash
# Continuum_Overworld Setup Verification Script
# Following Agora/Playbook--WebDev__PROD@v2.0.0
# Owner: The_Bridge (Naivasha / Number_1)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Verifying Continuum_Overworld Setup...${NC}"
echo -e "${BLUE}========================================${NC}"

# =============================================================================
# Configuration
# =============================================================================
C_O_ROOT="/mnt/c/users/password/continuum_Overworld"
CONFIG_FILE="$C_O_ROOT/continuum_config.yaml"
ENV_TEMPLATE="$C_O_ROOT/.env.template"
PLAYBOOK="$C_O_ROOT/Agora/Playbook--WebDev__PROD@v2.0.0.md"
NEXUS_SCRIPT="$C_O_ROOT/The_Bridge/deploy_to_nexus.sh"

ISSUES=0

# =============================================================================
# Helper Functions
# =============================================================================
check_success() {
    echo -e "${GREEN}  ✓ $1${NC}"
}

check_warning() {
    echo -e "${YELLOW}  ⚠ $1${NC}"
    ((ISSUES++))
}

check_error() {
    echo -e "${RED}  ✗ $1${NC}"
    ((ISSUES++))
}

check_info() {
    echo -e "${CYAN}  ℹ $1${NC}"
}

# =============================================================================
# Directory Structure Verification
# =============================================================================
echo -e "\n${YELLOW}📁 Directory Structure:${NC}"

REQUIRED_DIVISIONS=("The_Bridge" "Agora" "Forge" "Oracle" "Pantheon" "Atlas" "Aegis" "Meridian")

for division in "${REQUIRED_DIVISIONS[@]}"; do
    if [ -d "$C_O_ROOT/$division" ]; then
        check_success "$division division exists"
    else
        check_error "$division division missing"
    fi
done

# Check specific capabilities
if [ -d "$C_O_ROOT/The_Bridge/Helios_Console--Core__PROD" ]; then
    check_success "Helios Console capability exists"
else
    check_warning "Helios Console capability missing"
fi

if [ -d "$C_O_ROOT/Agora/Site--GreenStemGlobal__PROD@v1.0.0" ]; then
    check_success "GreenStem Global site exists"
else
    check_error "GreenStem Global site missing"
fi

# =============================================================================
# Configuration Files Verification
# =============================================================================
echo -e "\n${YELLOW}⚙️  Configuration Files:${NC}"

if [ -f "$CONFIG_FILE" ]; then
    check_success "continuum_config.yaml exists"
    
    # Check for required keys
    if grep -q "local_realm.*Continuum_Overworld" "$CONFIG_FILE"; then
        check_success "Local realm configuration correct"
    else
        check_error "Local realm configuration missing/incorrect"
    fi
    
    if grep -q "cloud_orchestrator.*Continuum_Nexus" "$CONFIG_FILE"; then
        check_success "Cloud orchestrator configuration correct"
    else
        check_error "Cloud orchestrator configuration missing/incorrect"
    fi
    
    if grep -q "local_prefix.*C_O" "$CONFIG_FILE"; then
        check_success "Local prefix (C_O) configured"
    else
        check_error "Local prefix (C_O) missing"
    fi
    
    if grep -q "cloud_prefix.*C_N" "$CONFIG_FILE"; then
        check_success "Cloud prefix (C_N) configured"
    else
        check_error "Cloud prefix (C_N) missing"
    fi
else
    check_error "continuum_config.yaml missing"
fi

if [ -f "$ENV_TEMPLATE" ]; then
    check_success ".env.template exists"
    
    # Check for required environment variables
    REQUIRED_VARS=("C_O_ENV" "C_N_ENV" "C_N_PREFIX" "AWS_REGION" "PROJECT_NAME")
    for var in "${REQUIRED_VARS[@]}"; do
        if grep -q "^$var=" "$ENV_TEMPLATE"; then
            check_success "$var template exists"
        else
            check_warning "$var template missing"
        fi
    done
else
    check_error ".env.template missing"
fi

if [ -f "$PLAYBOOK" ]; then
    check_success "Playbook v2.0.0 exists"
    
    # Check playbook content
    if grep -q "Aegis:T1" "$PLAYBOOK"; then
        check_success "Risk gate configuration found"
    else
        check_warning "Risk gate configuration missing"
    fi
    
    if grep -q "Golden Rules" "$PLAYBOOK"; then
        check_success "Golden Rules section found"
    else
        check_warning "Golden Rules section missing"
    fi
else
    check_error "Playbook missing"
fi

# =============================================================================
# Deployment Script Verification
# =============================================================================
echo -e "\n${YELLOW}🚀 Deployment Scripts:${NC}"

if [ -f "$NEXUS_SCRIPT" ]; then
    check_success "deploy_to_nexus.sh exists"
    
    if [ -x "$NEXUS_SCRIPT" ]; then
        check_success "deploy_to_nexus.sh is executable"
    else
        check_error "deploy_to_nexus.sh not executable"
    fi
    
    # Check script content
    if grep -q "C_O.*C_N" "$NEXUS_SCRIPT"; then
        check_success "C_O → C_N transformation logic found"
    else
        check_warning "Transformation logic missing"
    fi
else
    check_error "deploy_to_nexus.sh missing"
fi

# =============================================================================
# Prerequisites Verification
# =============================================================================
echo -e "\n${YELLOW}🔧 Prerequisites:${NC}"

# Node.js version
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -ge 18 ]; then
        check_success "Node.js version $(node --version) (requires 18+)"
    else
        check_error "Node.js version $(node --version) too old (requires 18+)"
    fi
else
    check_error "Node.js not installed"
fi

# AWS CLI
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version | cut -d'/' -f2 | cut -d' ' -f1)
    check_success "AWS CLI version $AWS_VERSION installed"
    
    # Check AWS credentials
    if aws sts get-caller-identity &> /dev/null; then
        AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
        check_success "AWS credentials configured (Account: $AWS_ACCOUNT)"
    else
        check_warning "AWS credentials not configured"
    fi
else
    check_error "AWS CLI not installed"
fi

# Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | cut -d' ' -f3)
    check_success "Git version $GIT_VERSION installed"
    
    # Check git configuration
    if git config user.name &> /dev/null && git config user.email &> /dev/null; then
        GIT_USER=$(git config user.name)
        check_success "Git user configured: $GIT_USER"
    else
        check_warning "Git user not configured"
    fi
else
    check_error "Git not installed"
fi

# =============================================================================
# Git Repository Verification
# =============================================================================
echo -e "\n${YELLOW}📚 Git Repository:${NC}"

if [ -d "$C_O_ROOT/.git" ]; then
    check_success "Git repository initialized"
    
    # Check current branch
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
    check_info "Current branch: $CURRENT_BRANCH"
    
    # Check for commits
    if git log --oneline -1 &> /dev/null; then
        LAST_COMMIT=$(git log --oneline -1 | head -c 50)
        check_info "Last commit: $LAST_COMMIT..."
    else
        check_warning "No commits found"
    fi
    
    # Check .gitignore
    if [ -f "$C_O_ROOT/.gitignore" ]; then
        check_success ".gitignore exists"
        
        # Check for required patterns
        IGNORE_PATTERNS=("node_modules" ".env.local" ".next")
        for pattern in "${IGNORE_PATTERNS[@]}"; do
            if grep -q "$pattern" "$C_O_ROOT/.gitignore"; then
                check_success "$pattern in .gitignore"
            else
                check_warning "$pattern missing from .gitignore"
            fi
        done
    else
        check_warning ".gitignore missing"
    fi
else
    check_error "Git repository not initialized"
fi

# =============================================================================
# Application-Specific Verification
# =============================================================================
echo -e "\n${YELLOW}🌐 Applications:${NC}"

# Agora Site
AGORA_SITE="$C_O_ROOT/Agora/Site--GreenStemGlobal__PROD@v1.0.0"
if [ -d "$AGORA_SITE" ]; then
    cd "$AGORA_SITE"
    
    if [ -f "package.json" ]; then
        check_success "Agora package.json exists"
        
        # Check for Next.js
        if grep -q "\"next\":" "package.json"; then
            NEXT_VERSION=$(grep "\"next\":" package.json | cut -d'"' -f4)
            check_success "Next.js $NEXT_VERSION configured"
        else
            check_warning "Next.js not configured"
        fi
        
        # Check for TypeScript
        if grep -q "\"typescript\":" "package.json"; then
            check_success "TypeScript configured"
        else
            check_warning "TypeScript not configured"
        fi
        
        # Check for Tailwind
        if grep -q "\"tailwindcss\":" "package.json"; then
            check_success "Tailwind CSS configured"
        else
            check_warning "Tailwind CSS not configured"
        fi
    else
        check_warning "Agora package.json missing"
    fi
    
    # Check for Nexus Bridge
    if [ -f "src/lib/nexus-bridge.ts" ]; then
        check_success "Nexus Bridge integration exists"
        
        if grep -q "transformToNexus" "src/lib/nexus-bridge.ts"; then
            check_success "C_O → C_N transformation functions found"
        else
            check_warning "Transformation functions missing"
        fi
    else
        check_warning "Nexus Bridge integration missing"
    fi
    
    cd "$C_O_ROOT"
fi

# Helios Console
HELIOS_CONSOLE="$C_O_ROOT/The_Bridge/Helios_Console--Core__PROD"
if [ -d "$HELIOS_CONSOLE" ]; then
    if [ -f "$HELIOS_CONSOLE/package.json" ]; then
        check_success "Helios Console package.json exists"
    else
        check_warning "Helios Console package.json missing"
    fi
fi

# =============================================================================
# Security & Compliance Check
# =============================================================================
echo -e "\n${YELLOW}🛡️  Security & Compliance (Aegis):${NC}"

# Check for sensitive files in git
if [ -f ".env" ]; then
    if git ls-files --error-unmatch .env &> /dev/null; then
        check_error ".env file is tracked by git (security risk)"
    else
        check_success ".env file not tracked by git"
    fi
fi

# Check for secrets in .env.template
if [ -f "$ENV_TEMPLATE" ]; then
    if grep -q "=.*[a-zA-Z0-9]{20,}" "$ENV_TEMPLATE"; then
        check_warning "Potential secrets found in .env.template"
    else
        check_success "No hardcoded secrets in .env.template"
    fi
fi

# Check package-lock.json exists (supply chain security)
if [ -f "$AGORA_SITE/package-lock.json" ]; then
    check_success "package-lock.json exists (dependency locking)"
else
    check_warning "package-lock.json missing (dependency security risk)"
fi

# =============================================================================
# Summary Report
# =============================================================================
echo -e "\n${BLUE}========================================${NC}"

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ SETUP VERIFICATION PASSED${NC}"
    echo -e "${GREEN}Continuum_Overworld (C_O) ready for development${NC}"
    echo -e "${GREEN}Deploys to → Continuum_Nexus (C_N) in AWS${NC}"
    EXIT_CODE=0
else
    echo -e "${YELLOW}⚠️  SETUP VERIFICATION COMPLETED WITH $ISSUES ISSUES${NC}"
    echo -e "${YELLOW}Review warnings above before proceeding${NC}"
    EXIT_CODE=1
fi

echo -e "\n${CYAN}🎯 Quick Start Commands:${NC}"
echo -e "${BLUE}Local Development:${NC}"
echo -e "  cd Agora/Site--GreenStemGlobal__PROD@v1.0.0"
echo -e "  npm install && npm run dev"

echo -e "\n${BLUE}Helios Console:${NC}"
echo -e "  cd The_Bridge/Helios_Console--Core__PROD"
echo -e "  npm install && npm run dev"

echo -e "\n${BLUE}Deploy to Nexus:${NC}"
echo -e "  ./The_Bridge/deploy_to_nexus.sh"

echo -e "\n${CYAN}📋 Architecture Summary:${NC}"
echo -e "${BLUE}  Local (C_O):${NC} Development in Continuum_Overworld"
echo -e "${BLUE}  Cloud (C_N):${NC} Execution in Continuum_Nexus"
echo -e "${BLUE}  Resources:${NC} Auto-transformed C_O → C_N"
echo -e "${BLUE}  Governance:${NC} The_Bridge oversight, Aegis security gate"

echo -e "\n${BLUE}========================================${NC}"

exit $EXIT_CODE