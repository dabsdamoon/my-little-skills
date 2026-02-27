# Advanced Patterns

## Hierarchical .envrc Files

direnv supports parent directory inheritance. Use this for shared settings.

### Structure

```
~/projects/
├── .envrc                          # Shared: credentials directory
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
export CREDENTIALS_DIR="$HOME/.config/gcloud/credentials"
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
export GOOGLE_APPLICATION_CREDENTIALS="$CREDENTIALS_DIR/project-1.json"
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

### GitHub Actions

```yaml
- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v2
  with:
    credentials_json: ${{ secrets.GCP_SA_KEY }}

- name: Set up Cloud SDK
  uses: google-github-actions/setup-gcloud@v2
```

### Workload Identity (Recommended for GKE)

Avoid SA keys entirely in production:

```bash
# Bind K8s SA to GCP SA
gcloud iam service-accounts add-iam-policy-binding \
  GSA_NAME@PROJECT_ID.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:PROJECT_ID.svc.id.goog[NAMESPACE/KSA_NAME]"
```

---

## Terraform Integration

```hcl
# Use environment variables
provider "google" {
  project = var.project_id
  region  = var.region
  # Credentials from GOOGLE_APPLICATION_CREDENTIALS
}
```

**.envrc for Terraform:**
```bash
export CLOUDSDK_ACTIVE_CONFIG_NAME="my-config"
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/gcloud/credentials/my-project.json"
export TF_VAR_project_id="my-project"
export TF_VAR_region="us-central1"
```

---

## Docker / Devcontainer Integration

Mount credentials into containers:

```bash
docker run -v ~/.config/gcloud:/root/.config/gcloud \
  -e GOOGLE_APPLICATION_CREDENTIALS=/root/.config/gcloud/credentials/my-project.json \
  my-image
```

**.devcontainer/devcontainer.json:**
```json
{
  "mounts": [
    "source=${localEnv:HOME}/.config/gcloud,target=/home/vscode/.config/gcloud,type=bind"
  ],
  "containerEnv": {
    "GOOGLE_APPLICATION_CREDENTIALS": "/home/vscode/.config/gcloud/credentials/my-project.json"
  }
}
```
