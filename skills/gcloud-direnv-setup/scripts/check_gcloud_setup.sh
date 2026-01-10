#!/bin/bash
# GCloud + Direnv Setup Diagnostic Script
# Checks current configuration and identifies common issues

set -e

echo "========================================"
echo "  GCloud + Direnv Diagnostic Report"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_ok() { echo -e "${GREEN}[OK]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_err() { echo -e "${RED}[ERROR]${NC} $1"; }
print_info() { echo -e "     $1"; }

# 1. Check gcloud CLI
echo "1. gcloud CLI"
echo "----------------------------------------"
if command -v gcloud &> /dev/null; then
    print_ok "gcloud is installed"
    print_info "Version: $(gcloud version 2>/dev/null | head -1)"
else
    print_err "gcloud is not installed"
fi
echo ""

# 2. Check direnv
echo "2. direnv"
echo "----------------------------------------"
if command -v direnv &> /dev/null; then
    print_ok "direnv is installed"
    print_info "Version: $(direnv version)"
else
    print_err "direnv is not installed"
    print_info "Install with: brew install direnv"
fi
echo ""

# 3. Check gcloud configurations
echo "3. gcloud Configurations"
echo "----------------------------------------"
ACTIVE_CONFIG=$(gcloud config configurations list --filter="is_active=true" --format="value(name)" 2>/dev/null || echo "")
if [[ -n "$ACTIVE_CONFIG" ]]; then
    print_ok "Active configuration: $ACTIVE_CONFIG"
    print_info "Project: $(gcloud config get-value project 2>/dev/null)"
    print_info "Account: $(gcloud config get-value account 2>/dev/null)"
else
    print_warn "No active gcloud configuration"
fi
echo ""

# 4. Check environment variables
echo "4. Environment Variables"
echo "----------------------------------------"
if [[ -n "$CLOUDSDK_ACTIVE_CONFIG_NAME" ]]; then
    print_ok "CLOUDSDK_ACTIVE_CONFIG_NAME: $CLOUDSDK_ACTIVE_CONFIG_NAME"
else
    print_info "CLOUDSDK_ACTIVE_CONFIG_NAME: (not set)"
fi

if [[ -n "$GOOGLE_CLOUD_PROJECT" ]]; then
    print_ok "GOOGLE_CLOUD_PROJECT: $GOOGLE_CLOUD_PROJECT"
else
    print_info "GOOGLE_CLOUD_PROJECT: (not set)"
fi

if [[ -n "$PROJECT_ID" ]]; then
    print_ok "PROJECT_ID: $PROJECT_ID"
else
    print_info "PROJECT_ID: (not set)"
fi

if [[ -n "$GOOGLE_APPLICATION_CREDENTIALS" ]]; then
    if [[ -f "$GOOGLE_APPLICATION_CREDENTIALS" ]]; then
        print_ok "GOOGLE_APPLICATION_CREDENTIALS: $GOOGLE_APPLICATION_CREDENTIALS"
        # Extract service account email
        SA_EMAIL=$(grep -o '"client_email": "[^"]*"' "$GOOGLE_APPLICATION_CREDENTIALS" 2>/dev/null | cut -d'"' -f4)
        if [[ -n "$SA_EMAIL" ]]; then
            print_info "Service Account: $SA_EMAIL"
        fi
    else
        print_err "GOOGLE_APPLICATION_CREDENTIALS file not found: $GOOGLE_APPLICATION_CREDENTIALS"
    fi
else
    print_info "GOOGLE_APPLICATION_CREDENTIALS: (not set - using ADC)"
fi
echo ""

# 5. Check ADC
echo "5. Application Default Credentials (ADC)"
echo "----------------------------------------"
ADC_FILE="$HOME/.config/gcloud/application_default_credentials.json"
if [[ -f "$ADC_FILE" ]]; then
    print_ok "ADC file exists"
    QUOTA_PROJECT=$(grep -o '"quota_project_id": "[^"]*"' "$ADC_FILE" 2>/dev/null | cut -d'"' -f4)
    if [[ -n "$QUOTA_PROJECT" ]]; then
        print_info "Quota project: $QUOTA_PROJECT"
    fi
else
    print_warn "ADC file not found"
    print_info "Create with: gcloud auth application-default login"
fi
echo ""

# 6. Check direnv status in current directory
echo "6. direnv Status (current directory)"
echo "----------------------------------------"
print_info "Directory: $(pwd)"
if [[ -f ".envrc" ]]; then
    print_ok ".envrc file exists"
    if direnv status 2>/dev/null | grep -q "Found RC allowed true"; then
        print_ok ".envrc is allowed"
    else
        print_warn ".envrc is NOT allowed"
        print_info "Run: direnv allow"
    fi
else
    print_info "No .envrc in current directory"
fi
echo ""

# 7. Potential issues
echo "7. Potential Issues"
echo "----------------------------------------"
ISSUES_FOUND=0

# Check for quota project mismatch
if [[ -n "$GOOGLE_CLOUD_PROJECT" ]] && [[ -f "$ADC_FILE" ]]; then
    ADC_QUOTA=$(grep -o '"quota_project_id": "[^"]*"' "$ADC_FILE" 2>/dev/null | cut -d'"' -f4)
    if [[ "$ADC_QUOTA" != "$GOOGLE_CLOUD_PROJECT" ]] && [[ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]]; then
        print_warn "ADC quota project ($ADC_QUOTA) differs from GOOGLE_CLOUD_PROJECT ($GOOGLE_CLOUD_PROJECT)"
        print_info "Fix: gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT"
        ISSUES_FOUND=1
    fi
fi

# Check for config name mismatch
if [[ -n "$CLOUDSDK_ACTIVE_CONFIG_NAME" ]] && [[ -n "$ACTIVE_CONFIG" ]]; then
    if [[ "$CLOUDSDK_ACTIVE_CONFIG_NAME" != "$ACTIVE_CONFIG" ]]; then
        print_warn "CLOUDSDK_ACTIVE_CONFIG_NAME ($CLOUDSDK_ACTIVE_CONFIG_NAME) differs from active config ($ACTIVE_CONFIG)"
        print_info "This is usually fine - env var takes precedence"
    fi
fi

if [[ $ISSUES_FOUND -eq 0 ]]; then
    print_ok "No issues detected"
fi
echo ""

echo "========================================"
echo "  Diagnostic complete"
echo "========================================"
