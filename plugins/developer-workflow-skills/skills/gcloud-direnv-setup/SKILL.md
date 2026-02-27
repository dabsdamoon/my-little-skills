---
name: gcloud-direnv-setup
description: Set up per-directory GCP credentials using gcloud and direnv. Use when asked to set up a new project with GCP, switch between multiple GCP projects/accounts, configure direnv for automatic credential switching, troubleshoot GCP authentication issues, or manage multiple Google accounts across directories. Handles service account keys, ADC (Application Default Credentials), organization policies, and multi-account scenarios.
---

# GCloud + Direnv Setup

Set up automatic per-directory GCP credential switching using gcloud configurations and direnv.

## Quick Assessment

Before starting, gather this information:

1. **Project details**: GCP project ID and preferred configuration name
2. **Account**: Which Google account to use (run `gcloud auth list` to see available)
3. **Credential strategy**: Will determine based on org policies

## Workflow

```
1. Check Prerequisites → 2. Create gcloud Config → 3. Determine Strategy → 4. Create .envrc → 5. Verify
```

### Step 1: Check Prerequisites

Verify tools are installed:

```bash
# Check gcloud
gcloud version

# Check direnv
direnv version

# If direnv missing, install and add hook
brew install direnv
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc
source ~/.zshrc
```

### Step 2: Create gcloud Configuration

```bash
# List existing configurations
gcloud config configurations list

# Create new configuration (skip if exists)
gcloud config configurations create CONFIG_NAME

# Set account and project
gcloud config set account USER@EMAIL.COM
gcloud config set project PROJECT_ID

# Authenticate (opens browser)
gcloud auth login
```

### Step 3: Determine Credential Strategy

**Test if Service Account keys are allowed:**

```bash
# Try creating a test service account
gcloud iam service-accounts create test-check-sa \
  --display-name="Test SA" \
  --project=PROJECT_ID 2>&1

# If successful, try creating a key
gcloud iam service-accounts keys create /tmp/test-key.json \
  --iam-account=test-check-sa@PROJECT_ID.iam.gserviceaccount.com 2>&1

# Clean up test
rm -f /tmp/test-key.json
gcloud iam service-accounts delete test-check-sa@PROJECT_ID.iam.gserviceaccount.com --quiet 2>/dev/null
```

**Decision:**
- If key creation succeeds → Use **Service Account Key** (isolated, per-project)
- If `FAILED_PRECONDITION: Key creation is not allowed` → Use **ADC** (shared)

See [references/credential-strategies.md](references/credential-strategies.md) for detailed comparison.

### Step 4: Create .envrc

#### Option A: Service Account Key (Recommended when allowed)

```bash
# Create credentials directory
mkdir -p ~/.config/gcloud/credentials

# Create service account
gcloud iam service-accounts create PROJECT_NAME-local \
  --display-name="PROJECT_NAME Local Dev" \
  --project=PROJECT_ID

# Create key
gcloud iam service-accounts keys create \
  ~/.config/gcloud/credentials/PROJECT_NAME.json \
  --iam-account=PROJECT_NAME-local@PROJECT_ID.iam.gserviceaccount.com

# Grant necessary permissions (adjust roles as needed)
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:PROJECT_NAME-local@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/editor"
```

**.envrc for Service Account Key:**

```bash
export CLOUDSDK_ACTIVE_CONFIG_NAME="CONFIG_NAME"
export GOOGLE_CLOUD_PROJECT="PROJECT_ID"
export PROJECT_ID="PROJECT_ID"
export LOCATION="us-central1"
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/gcloud/credentials/PROJECT_NAME.json"
```

#### Option B: ADC (When SA keys are blocked)

```bash
# Activate configuration
gcloud config configurations activate CONFIG_NAME

# Create ADC (opens browser)
gcloud auth application-default login --project=PROJECT_ID
```

**.envrc for ADC:**

```bash
export CLOUDSDK_ACTIVE_CONFIG_NAME="CONFIG_NAME"

# Load .env file first (if exists)
dotenv_if_exists .env

# Override: use ADC (unset any SA key from .env)
unset GOOGLE_APPLICATION_CREDENTIALS
export GOOGLE_CLOUD_PROJECT="PROJECT_ID"
export PROJECT_ID="PROJECT_ID"
export LOCATION="us-central1"
```

**Important:** ADC is a shared file. The last `gcloud auth application-default login` wins. Projects using ADC share the same credentials.

#### Option C: Hybrid (Multiple projects, mixed strategies)

When you have multiple projects:
- Projects that allow SA keys → Use dedicated key files
- Projects with org policies → Share ADC, set ADC to the most commonly used one

### Step 5: Allow and Verify

```bash
cd /path/to/project
direnv allow

# Verify environment
echo "Config: $CLOUDSDK_ACTIVE_CONFIG_NAME"
echo "Project: $PROJECT_ID"
echo "Credentials: ${GOOGLE_APPLICATION_CREDENTIALS:-"(using ADC)"}"

# Verify gcloud
gcloud config list

# Verify Python SDK can authenticate
python3 -c "import google.auth; creds, proj = google.auth.default(); print(f'Project: {proj}')"
```

## .envrc Templates

### Template 1: Service Account Key

```bash
# GCP Configuration: PROJECT_NAME
export CLOUDSDK_ACTIVE_CONFIG_NAME="CONFIG_NAME"
export GOOGLE_CLOUD_PROJECT="PROJECT_ID"
export PROJECT_ID="PROJECT_ID"
export LOCATION="REGION"
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/gcloud/credentials/PROJECT_NAME.json"
```

### Template 2: ADC with .env Override

```bash
# GCP Configuration: PROJECT_NAME
export CLOUDSDK_ACTIVE_CONFIG_NAME="CONFIG_NAME"

# Load .env first
dotenv_if_exists .env

# Override credentials to use ADC
unset GOOGLE_APPLICATION_CREDENTIALS
export GOOGLE_CLOUD_PROJECT="PROJECT_ID"
export PROJECT_ID="PROJECT_ID"
export LOCATION="REGION"

echo "gcloud config: CONFIG_NAME (using ADC)"
```

### Template 3: Minimal (gcloud CLI only)

```bash
export CLOUDSDK_ACTIVE_CONFIG_NAME="CONFIG_NAME"
```

## Common Permissions

Grant based on needs:

| Use Case | Role |
|----------|------|
| General development | `roles/editor` |
| Vertex AI / Gemini | `roles/aiplatform.user` |
| Cloud Storage | `roles/storage.objectAdmin` |
| Cloud Run | `roles/run.developer` |
| Pub/Sub | `roles/pubsub.editor` |

```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA_EMAIL" \
  --role="ROLE"
```

## Troubleshooting

See [references/troubleshooting.md](references/troubleshooting.md) for common issues.

**Quick fixes:**

```bash
# Quota project mismatch
gcloud auth application-default set-quota-project PROJECT_ID

# direnv not loading
direnv allow

# Check current state
~/.claude/skills/gcloud-direnv-setup/scripts/check_gcloud_setup.sh
```

## References

- [Credential Strategies](references/credential-strategies.md) - SA Key vs ADC comparison
- [Troubleshooting](references/troubleshooting.md) - Common issues and fixes
- [Advanced Patterns](references/advanced-patterns.md) - Multi-account, hierarchical, K8s
