# Credential Strategies

Google's order for local development (checked 2026-10-26, see SKILL.md Sources): user credentials through ADC first, service-account impersonation second, a service-account key only when neither works.

## Comparison

| Feature | A. User ADC (default) | B. Impersonation | C. Service Account Key (last resort) |
|---------|-----------------------|------------------|--------------------------------------|
| **Created by** | `gcloud auth application-default login` | `gcloud auth application-default login --impersonate-service-account SA_EMAIL` | `gcloud iam service-accounts keys create` |
| **File** | `~/.config/gcloud/application_default_credentials.json` | Same ADC file | Custom path, e.g. `~/.config/gcloud/credentials/` |
| **Per-directory** | No (one shared file) | No (one shared file) | Yes, via `GOOGLE_APPLICATION_CREDENTIALS` |
| **Identity** | User account | Service account, minted from the user's login | Service account |
| **Needs** | Roles on the user | `roles/iam.serviceAccountTokenCreator` on the service account | Key creation allowed by org policy |
| **Long-lived secret on disk** | No key file | No key file | Yes, the private key |
| **Library support** | All ADC libraries | C#, Go, Java, Node.js, Python | All ADC libraries |

## Decision Tree

```
Can the code run as the user (with least-privilege roles on the user)?
├── Yes → A. User ADC
└── No, it must run as a service account
    ├── Can the user get roles/iam.serviceAccountTokenCreator on it,
    │   and does the client library support impersonated ADC?
    │   └── Yes → B. Impersonation
    └── No → check org policy (below)
        ├── Keys blocked → back to A or B; ask the admin for Token Creator
        └── Keys allowed → C. Service account key, least-privilege role, chmod 600
```

## Checking Whether Keys Are Blocked (read-only)

```bash
gcloud org-policies describe iam.managed.disableServiceAccountKeyCreation \
  --effective --project=PROJECT_ID
gcloud org-policies describe iam.disableServiceAccountKeyCreation \
  --effective --project=PROJECT_ID
```

- `enforce: true` under `spec.rules`: key creation is blocked.
- `enforce: false`, or no policy found: that constraint doesn't block keys.
- `iam.managed.disableServiceAccountKeyCreation` is the managed constraint; `iam.disableServiceAccountKeyCreation` is the legacy one. The legacy constraint is enforced by default in organizations created on or after May 3, 2024. Check both.
- Permission denied: the answer is unknown. Ask the org admin. Don't create a service account or key to find out.

## Multi-Account Scenarios

### Scenario 1: One account per project, user ADC

```
gcloud configurations: project-a (user1@...), project-b (user2@...)
ADC file: whichever account ran `gcloud auth application-default login` last
```

`CLOUDSDK_ACTIVE_CONFIG_NAME` in each `.envrc` switches the gcloud CLI per directory. The ADC file does not switch. Re-run `gcloud auth application-default login` when you move to a project that needs the other account, or keep one ADC file per account (see [advanced-patterns.md](advanced-patterns.md#multiple-adc-files)).

### Scenario 2: Same user, different service accounts per project

```
Project A: gcloud config set auth/impersonate_service_account sa-a@...   (config project-a)
Project B: gcloud config set auth/impersonate_service_account sa-b@...   (config project-b)
```

The gcloud CLI impersonates per configuration, so it switches with `.envrc`. Impersonated ADC for client libraries is still one shared file: re-run `gcloud auth application-default login --impersonate-service-account SA_EMAIL` when switching.

### Scenario 3: Mixed, one project needs a key

```
Project A (ADC):  .envrc → unset GOOGLE_APPLICATION_CREDENTIALS
Project B (key):  .envrc → GOOGLE_APPLICATION_CREDENTIALS=$HOME/.config/gcloud/credentials/project-b.json
```

Only project B carries a key. Its `.envrc` holds the path, never the key contents.

## Environment Variables Reference

| Variable | Purpose | Set By |
|----------|---------|--------|
| `CLOUDSDK_ACTIVE_CONFIG_NAME` | Switches gcloud CLI config | .envrc |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to a credential file (key, or a saved ADC file) | .envrc, only when needed |
| `GOOGLE_CLOUD_PROJECT` | Default project for `google.auth.default()` and SDKs | .envrc |
| `GOOGLE_CLOUD_LOCATION` | Default region for SDKs such as Google Gen AI | .envrc |
| `GOOGLE_CLOUD_QUOTA_PROJECT` | Billing/quota project | .envrc or ADC |
| `CLOUDSDK_CONFIG` | Custom gcloud config dir | .envrc (advanced) |

None of these are secrets. API keys and tokens never go in `.envrc` or `.env`; fetch them through `scripts/with-secrets.sh`.

## Security Considerations

### User ADC and impersonation
- No key file to leak or rotate; OAuth tokens refresh automatically
- Actions are limited to the user's (A) or service account's (B) roles, so keep those roles narrow
- The ADC file is still a credential: never commit it or mount all of `~/.config/gcloud` into containers

### Service Account Keys
- Last resort; prefer A or B
- Store outside the repo with `chmod 600`
- Never commit; add the credentials directory to `.gitignore` if it is ever under a repo
- Rotate and delete keys you no longer use
- Grant the narrowest role, never `roles/editor`
