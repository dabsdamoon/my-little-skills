# Credential Strategies

## Comparison: Service Account Key vs ADC

| Feature | Service Account Key | ADC (Application Default Credentials) |
|---------|---------------------|---------------------------------------|
| **File location** | Custom (e.g., `~/.config/gcloud/credentials/`) | `~/.config/gcloud/application_default_credentials.json` |
| **Per-directory** | Yes (via `GOOGLE_APPLICATION_CREDENTIALS`) | No (single shared file) |
| **Identity** | Service account | User account |
| **Created by** | `gcloud iam service-accounts keys create` | `gcloud auth application-default login` |
| **Org policy** | May be blocked | Always allowed |
| **Rotation** | Manual | Automatic (OAuth refresh) |
| **Audit trail** | Shows as service account | Shows as user |
| **Best for** | Production-like, isolated environments | Quick setup, shared environments |

## Decision Tree

```
Can you create service account keys?
├── Yes → Use Service Account Key
│         ├── Want isolation between projects? → Separate SA per project
│         └── Sharing credentials OK? → Can use same SA
└── No (org policy blocks) → Use ADC
                             └── Multiple accounts?
                                 ├── One primary → Set ADC to primary
                                 └── Equal usage → Switch ADC manually
```

## Detecting Organization Policy Restrictions

```bash
# This error indicates SA keys are blocked:
# FAILED_PRECONDITION: Key creation is not allowed on this service account

# Check org policies (requires permissions)
gcloud resource-manager org-policies describe \
  iam.disableServiceAccountKeyCreation \
  --project=PROJECT_ID
```

## Multi-Account Scenarios

### Scenario 1: Different accounts, SA keys allowed for all

```
~/.config/gcloud/credentials/
├── project-a.json  (account1@gmail.com's SA)
├── project-b.json  (account2@company.com's SA)
└── project-c.json  (account1@gmail.com's SA)
```

Each .envrc points to its own key file.

### Scenario 2: Mixed - some allow SA keys, some don't

```
Project A (allows SA keys):
  .envrc → GOOGLE_APPLICATION_CREDENTIALS=project-a.json

Project B (org policy blocks):
  .envrc → unset GOOGLE_APPLICATION_CREDENTIALS (uses ADC)

ADC file: Set to Project B's account
```

### Scenario 3: All use ADC (no SA keys allowed anywhere)

```
ADC file: Set to most frequently used account

Switching between accounts requires:
  gcloud config configurations activate other-config
  gcloud auth application-default login --project=other-project
```

## Environment Variables Reference

| Variable | Purpose | Set By |
|----------|---------|--------|
| `CLOUDSDK_ACTIVE_CONFIG_NAME` | Switches gcloud CLI config | .envrc |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to SA key JSON | .envrc |
| `GOOGLE_CLOUD_PROJECT` | Default project for SDKs | .envrc |
| `GOOGLE_CLOUD_QUOTA_PROJECT` | Billing/quota project | .envrc or ADC |
| `CLOUDSDK_CONFIG` | Custom gcloud config dir | .envrc (advanced) |

## Security Considerations

### Service Account Keys
- Store in secure location with restricted permissions (`chmod 600`)
- Never commit to version control
- Add to `.gitignore`: `*.json` in credentials directories
- Rotate periodically
- Use least-privilege roles

### ADC
- OAuth tokens auto-refresh
- Credentials scoped to user's permissions
- No key file to manage
- Actions attributed to user in audit logs
