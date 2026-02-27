# Troubleshooting Guide

## Common Issues and Solutions

### 1. "Quota project does not match"

**Error:**
```
WARNING: Your active project does not match the quota project in your local
Application Default Credentials file.
```

**Cause:** ADC was created with a different project than currently active.

**Solutions:**

```bash
# Option A: Update quota project only
gcloud auth application-default set-quota-project PROJECT_ID

# Option B: Re-create ADC entirely
gcloud auth application-default login --project=PROJECT_ID
```

---

### 2. "Permission denied" on Service Account Key Creation

**Error:**
```
FAILED_PRECONDITION: Key creation is not allowed on this service account.
```

**Cause:** Organization policy `iam.disableServiceAccountKeyCreation` is enabled.

**Solutions:**

1. Use ADC instead of service account key
2. Request exception from organization admin
3. Use Workload Identity (for GKE)

---

### 3. direnv Not Loading .envrc

**Symptoms:** Environment variables not set when entering directory.

**Diagnostic:**
```bash
cd /path/to/project
direnv status
```

**Solutions:**

```bash
# Allow the .envrc file
direnv allow

# Check hook is in shell
grep direnv ~/.zshrc  # or ~/.bashrc

# Reload shell config
source ~/.zshrc

# Verify hook works
cd .. && cd -
```

---

### 4. Python SDK Using Wrong Credentials

**Symptoms:** Python code authenticates with wrong project/account.

**Diagnostic:**
```python
import google.auth
credentials, project = google.auth.default()
print(f"Project: {project}")
print(f"Credentials type: {type(credentials)}")
```

**Causes and Solutions:**

| Cause | Solution |
|-------|----------|
| `GOOGLE_APPLICATION_CREDENTIALS` not set | Check .envrc is loaded |
| ADC has wrong account | Re-run `gcloud auth application-default login` |
| .env overrides .envrc | Put `unset GOOGLE_APPLICATION_CREDENTIALS` after `dotenv_if_exists` |
| Cached credentials | Restart Python/IDE |

---

### 5. gcloud CLI Uses Different Project Than SDK

**Symptoms:** `gcloud` commands work, but Python SDK fails or uses different project.

**Cause:** gcloud CLI and SDK use different credential sources.

**Understanding:**
- gcloud CLI: Uses `CLOUDSDK_ACTIVE_CONFIG_NAME` config
- Python SDK: Uses `GOOGLE_APPLICATION_CREDENTIALS` or ADC

**Solution:** Ensure both are configured:

```bash
# In .envrc
export CLOUDSDK_ACTIVE_CONFIG_NAME="my-config"  # For gcloud CLI
export GOOGLE_APPLICATION_CREDENTIALS="..."      # For SDK
# OR
export GOOGLE_CLOUD_PROJECT="project-id"        # For SDK with ADC
```

---

### 6. Service Account Has No Permissions

**Error:**
```
403 Permission denied on resource
```

**Diagnostic:**
```bash
# Check SA permissions
gcloud projects get-iam-policy PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:SERVICE_ACCOUNT_EMAIL" \
  --format="table(bindings.role)"
```

**Solution:**
```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/NEEDED_ROLE"
```

---

### 7. Wrong Account in ADC After Switching

**Symptoms:** After `cd` to different project, still using old account.

**Cause:** ADC is a single shared file, doesn't auto-switch with direnv.

**Solutions:**

1. **Use SA keys** (if allowed) - each project has own key
2. **Manual ADC switch** when changing accounts:
   ```bash
   gcloud config configurations activate OTHER_CONFIG
   gcloud auth application-default login --project=OTHER_PROJECT
   ```
3. **Rename ADC files** (advanced):
   ```bash
   # Save current ADC
   mv ~/.config/gcloud/application_default_credentials.json \
      ~/.config/gcloud/adc-account1.json

   # In .envrc, point to specific ADC
   export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/gcloud/adc-account1.json"
   ```

---

### 8. direnv .envrc Order Issues

**Symptoms:** Variables from .env override .envrc settings.

**Cause:** `dotenv_if_exists` runs after exports, then .env sets values.

**Solution:** Override AFTER loading .env:

```bash
# WRONG order
export GOOGLE_APPLICATION_CREDENTIALS=""  # Gets overwritten
dotenv_if_exists .env                      # .env sets credentials

# CORRECT order
dotenv_if_exists .env                      # Load .env first
unset GOOGLE_APPLICATION_CREDENTIALS       # Then override
export GOOGLE_CLOUD_PROJECT="my-project"
```

---

### 9. "API not enabled" Errors

**Error:**
```
API [SERVICE.googleapis.com] not enabled on project
```

**Solution:**
```bash
# Enable specific API
gcloud services enable SERVICE.googleapis.com --project=PROJECT_ID

# Common APIs
gcloud services enable aiplatform.googleapis.com    # Vertex AI
gcloud services enable storage.googleapis.com       # Cloud Storage
gcloud services enable run.googleapis.com           # Cloud Run
gcloud services enable pubsub.googleapis.com        # Pub/Sub
```

---

## Diagnostic Commands

```bash
# Full diagnostic
echo "=== gcloud config ==="
gcloud config configurations list
gcloud config list

echo "=== ADC ==="
cat ~/.config/gcloud/application_default_credentials.json | grep -E "(quota_project|client_id)"

echo "=== Environment ==="
echo "CLOUDSDK_ACTIVE_CONFIG_NAME: $CLOUDSDK_ACTIVE_CONFIG_NAME"
echo "GOOGLE_CLOUD_PROJECT: $GOOGLE_CLOUD_PROJECT"
echo "GOOGLE_APPLICATION_CREDENTIALS: ${GOOGLE_APPLICATION_CREDENTIALS:-"(not set)"}"

echo "=== direnv ==="
direnv status
```
