# Advanced Patterns

## Hierarchical .envrc Files

direnv supports parent directory inheritance. Use this for shared settings.

### Structure

```
~/projects/
├── .envrc                          # Shared: region
├── company-a/
│   ├── .envrc                      # Company A config
│   ├── project-1/.envrc            # Project-specific overrides
│   └── project-2/.envrc
└── company-b/
    ├── .envrc                      # Company B config
    └── project-3/.envrc
```

### Parent .envrc (~/projects/.envrc)

```bash
# Shared across all projects
export GOOGLE_CLOUD_LOCATION="us-central1"
```

### Child .envrc (~/projects/company-a/.envrc)

```bash
# Inherits from parent
source_up  # Load parent .envrc

export CLOUDSDK_ACTIVE_CONFIG_NAME="company-a"
export GOOGLE_CLOUD_PROJECT="company-a-shared"
```

### Grandchild .envrc (~/projects/company-a/project-1/.envrc)

```bash
source_up  # Loads company-a/.envrc which loads projects/.envrc

# Override project only
export GOOGLE_CLOUD_PROJECT="project-1-id"
```

---

## CLOUDSDK_CONFIG Per Directory

Store entire gcloud configuration per directory (advanced isolation).

```bash
# In .envrc
export CLOUDSDK_CONFIG="$PWD/.gcloud"
```

This creates a separate gcloud config directory with:
- configurations/
- properties
- credentials.db
- application_default_credentials.json

**Pros:** Complete isolation
**Cons:** Requires separate `gcloud auth login` per directory

---

## Multiple ADC Files

Rename and manage multiple ADC files:

```bash
# Create ADC for each account
gcloud config configurations activate account1
gcloud auth application-default login
mv ~/.config/gcloud/application_default_credentials.json \
   ~/.config/gcloud/adc-account1.json

gcloud config configurations activate account2
gcloud auth application-default login
mv ~/.config/gcloud/application_default_credentials.json \
   ~/.config/gcloud/adc-account2.json
```

**In .envrc:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/gcloud/adc-account1.json"
```

---

## Kubernetes Context Switching

Combine GCP and K8s context switching:

```bash
# In .envrc
export CLOUDSDK_ACTIVE_CONFIG_NAME="my-gcp-config"
export KUBECONFIG="$HOME/.kube/configs/my-cluster.yaml"

# Or use gcloud to get credentials on-demand
# gcloud container clusters get-credentials CLUSTER_NAME --zone ZONE
```

### Per-Cluster Config Files

```bash
# Generate cluster-specific kubeconfig
KUBECONFIG=~/.kube/configs/cluster-a.yaml \
  gcloud container clusters get-credentials cluster-a --zone us-central1-a
```

**In .envrc:**
```bash
export CLOUDSDK_ACTIVE_CONFIG_NAME="project-a"
export KUBECONFIG="$HOME/.kube/configs/cluster-a.yaml"
```

---

## Shell Prompt Integration

Add GCP project to prompt for visibility.

### Zsh (with PROMPT)

```bash
# In ~/.zshrc
function gcp_project_prompt() {
  if [[ -n "$GOOGLE_CLOUD_PROJECT" ]]; then
    echo " [gcp:$GOOGLE_CLOUD_PROJECT]"
  fi
}

PROMPT='%n@%m %~$(gcp_project_prompt) %# '
```

### With Powerlevel10k

```bash
# In ~/.p10k.zsh, add to POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS:
typeset -g POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(
  ...
  gcloud
  ...
)
```

---

## CI/CD Considerations

Action versions and identifiers checked 2026-10-26 (see SKILL.md Sources).

### GitHub Actions: Workload Identity Federation

`google-github-actions/auth` prefers Direct Workload Identity Federation: GitHub's OIDC token is exchanged for Google credentials, so no service account key is stored as a secret.

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: 'read'
      id-token: 'write'
    steps:
      - uses: 'actions/checkout@v7'   # must come before auth
      - uses: 'google-github-actions/auth@v3'
        with:
          project_id: 'PROJECT_ID'
          workload_identity_provider: 'projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID'
      - uses: 'google-github-actions/setup-gcloud@v3'
```

Create the pool and provider, and grant roles to the federated principal, as the [auth README](https://github.com/google-github-actions/auth#direct-wif) shows. The action's `credentials_json` input (a service account key in a GitHub secret) is its last listed option; use it only when federation isn't possible.

### Workload Identity Federation for GKE

Grant IAM roles directly to the Kubernetes ServiceAccount with a principal identifier. No Google service account or key is needed:

```bash
gcloud projects add-iam-policy-binding projects/PROJECT_ID \
  --role=ROLE \
  --member=principal://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/PROJECT_ID.svc.id.goog/subject/ns/NAMESPACE/sa/KSA_NAME \
  --condition=None
```

GKE documents linking the Kubernetes ServiceAccount to an IAM service account (`roles/iam.workloadIdentityUser` plus the `iam.gke.io/gcp-service-account` annotation) as the alternative, for APIs where federated identities have limitations. That method needs both the IAM binding and the annotation.

---

## Terraform Integration

Google recommends ADC for Terraform. After `gcloud auth application-default login` (optionally with `--impersonate-service-account SA_EMAIL`), the provider picks up the credentials with no key file. The provider's `impersonate_service_account` field is the alternative when each environment should use a different service account.

```hcl
provider "google" {
  project = var.project_id
  region  = var.region
  # Credentials from ADC
}
```

**.envrc for Terraform:**
```bash
export CLOUDSDK_ACTIVE_CONFIG_NAME="my-config"
unset GOOGLE_APPLICATION_CREDENTIALS
export TF_VAR_project_id="my-project"
export TF_VAR_region="us-central1"
```

---

## Docker / Devcontainer Integration

Mount only the one credential file, read-only, and point `GOOGLE_APPLICATION_CREDENTIALS` at the mount path. Never mount all of `~/.config/gcloud`: it holds every account's gcloud login, not just the one the container needs.

```bash
# ADC (user or impersonated)
docker run \
  -v "$HOME/.config/gcloud/application_default_credentials.json:/tmp/keys/adc.json:ro" \
  -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/keys/adc.json \
  -e GOOGLE_CLOUD_PROJECT="$GOOGLE_CLOUD_PROJECT" \
  my-image

# Key file (last resort): same pattern with the key path
docker run \
  -v "$GOOGLE_APPLICATION_CREDENTIALS:/tmp/keys/key.json:ro" \
  -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/keys/key.json \
  my-image
```

**.devcontainer/devcontainer.json:**
```json
{
  "mounts": [
    "source=${localEnv:HOME}/.config/gcloud/application_default_credentials.json,target=/tmp/keys/adc.json,type=bind,readonly"
  ],
  "containerEnv": {
    "GOOGLE_APPLICATION_CREDENTIALS": "/tmp/keys/adc.json"
  }
}
```
