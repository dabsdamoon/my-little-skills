---
name: gcloud-direnv-setup
description: Sets up per-directory Google Cloud credentials with gcloud configurations and direnv .envrc files, preferring user Application Default Credentials, then service-account impersonation, with key files only as a last resort. Use when the user mentions gcloud, direnv, .envrc, ADC, GOOGLE_APPLICATION_CREDENTIALS, GOOGLE_CLOUD_PROJECT, quota-project warnings, switching GCP projects or Google accounts per directory, org policies that block service account keys, or GCP auth that works in the terminal but not in Claude Code or Codex.
---

# GCloud + Direnv Setup

Switch Google Cloud credentials per directory: one gcloud configuration per project, Application Default Credentials (ADC) for client libraries, and a `.envrc` that selects both when you `cd` in.

## Rules

- **Credential order.** Google's local-development guidance: (1) user credentials through ADC, (2) service-account impersonation, (3) a service-account key only when neither works. See [Sources](#sources-checked-2026-10-26).
- **Least privilege.** Grant the narrowest predefined role for the job. Never `roles/editor` or `roles/owner`.
- **Read-only probes.** Check org policy with `gcloud org-policies describe`. Never create a service account or key just to find out whether keys are allowed.
- **No secrets in direnv.** direnv exports everything in `.envrc`, and in any `.env` it loads, to every process started in the directory. Keep both files to non-secret settings: config name, project, region, and credential file *paths*. Fetch API keys and tokens on demand from Secret Manager through the repo's wrapper (`scripts/with-secrets.sh <command>`) instead of exporting them here. Never print tokens or key contents.

## Quick Assessment

1. **Project**: GCP project ID, region, and a configuration name
2. **Account**: which Google account (`gcloud auth list` shows those already logged in)
3. **Identity the code should run as**: the user (Option A) or a service account (Option B)
4. **Who runs the commands**: the user's terminal, or an agent such as Claude Code or Codex (see [Agent shells](#agent-shells))

## Workflow

```
1. Prerequisites → 2. gcloud config → 3. Credential → 4. .envrc → 5. Verify → 6. Agent shells
```

### Step 1: Check Prerequisites

```bash
gcloud version
direnv version

# Is the direnv hook loaded in interactive zsh? "function" = yes, "none" = no
zsh -ic 'whence -w _direnv_hook' 2>/dev/null
```

If direnv is missing, ask before installing it (`brew install direnv`).

If the hook prints `none`, `.envrc` never loads, not even in the user's own terminal. Show the user the lines below and let them add them to the zshrc they manage (it may be a symlink into a dotfiles repo). Don't edit dotfiles unasked.

- Plain zsh: add at the end of `~/.zshrc` (direnv docs):

  ```zsh
  eval "$(direnv hook zsh)"
  ```

- Powerlevel10k with instant prompt (a `p10k-instant-prompt` block near the top of `~/.zshrc`): the p10k README puts one line above that block and one below it:

  ```zsh
  (( ${+commands[direnv]} )) && emulate zsh -c "$(direnv export zsh)"

  # ... existing p10k-instant-prompt block ...

  (( ${+commands[direnv]} )) && emulate zsh -c "$(direnv hook zsh)"
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

### Step 3: Choose a Credential

See [references/credential-strategies.md](references/credential-strategies.md) for the comparison and multi-account layouts.

#### Option A (default): user credentials through ADC

```bash
gcloud config configurations activate CONFIG_NAME
gcloud auth application-default login --project=PROJECT_ID
```

`--project` sets the quota project written into the ADC file. Grant the user only the roles the work needs ([Least-privilege roles](#least-privilege-roles)).

#### Option B: service-account impersonation

Use when code should run with a service account's permissions (to match production, or because the user shouldn't hold those roles) without a key file. Impersonated ADC works in the C#, Go, Java, Node.js, and Python client libraries.

```bash
# Once, by someone who can set IAM policy on the service account
gcloud iam service-accounts add-iam-policy-binding SA_EMAIL \
  --member="user:USER@EMAIL.COM" \
  --role="roles/iam.serviceAccountTokenCreator"

# ADC that impersonates the service account (client libraries)
gcloud auth application-default login --impersonate-service-account SA_EMAIL

# Optional: gcloud CLI impersonation, saved in the active configuration
gcloud config set auth/impersonate_service_account SA_EMAIL
```

Options A and B both write the one ADC file (`~/.config/gcloud/application_default_credentials.json`). The last `gcloud auth application-default login` wins for every directory that uses ADC.

#### Option C (last resort): service-account key

Only when A and B can't work, for example a tool that accepts nothing but a key file. First check, read-only, whether key creation is blocked:

```bash
gcloud org-policies describe iam.managed.disableServiceAccountKeyCreation \
  --effective --project=PROJECT_ID
gcloud org-policies describe iam.disableServiceAccountKeyCreation \
  --effective --project=PROJECT_ID
```

`enforce: true` under `spec.rules` in either output means keys are blocked: go back to A or B. The legacy constraint is enforced by default in organizations created on or after May 3, 2024. If you can't read the policy, ask the org admin instead of probing by creating keys.

If keys are allowed and still required:

```bash
mkdir -p ~/.config/gcloud/credentials

gcloud iam service-accounts create PROJECT_NAME-local \
  --display-name="PROJECT_NAME Local Dev" \
  --project=PROJECT_ID

gcloud iam service-accounts keys create \
  ~/.config/gcloud/credentials/PROJECT_NAME.json \
  --iam-account=PROJECT_NAME-local@PROJECT_ID.iam.gserviceaccount.com
chmod 600 ~/.config/gcloud/credentials/PROJECT_NAME.json

# Narrowest role for the job; see Least-privilege roles
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:PROJECT_NAME-local@PROJECT_ID.iam.gserviceaccount.com" \
  --role="ROLE"
```

Keep the key outside the repo and reference only its path from `.envrc`.

### Step 4: Create .envrc

Pick a template from [.envrc Templates](#envrc-templates): Template 1 for Options A and B, Template 2 for Option C.

### Step 5: Allow and Verify

```bash
cd /path/to/project
direnv allow   # trusts this .envrc; review it first

echo "Config: $CLOUDSDK_ACTIVE_CONFIG_NAME"
echo "Project: $GOOGLE_CLOUD_PROJECT ($GOOGLE_CLOUD_LOCATION)"
echo "Credentials: ${GOOGLE_APPLICATION_CREDENTIALS:-"(using ADC)"}"

gcloud config list

# Python SDK picks up the same project
python3 -c "import google.auth; creds, proj = google.auth.default(); print(f'Project: {proj}')"
```

Set `SKILL_DIR` to this skill directory, then run the read-only diagnostic from the project directory:

```bash
"$SKILL_DIR/scripts/check_gcloud_setup.sh"
```

It reads gcloud configuration, environment variables, the ADC file's type and quota project, and `direnv status`. It changes nothing.

## .envrc Templates

All templates hold non-secret settings only (see [Rules](#rules)).

### Template 1: ADC (Options A and B)

```bash
# GCP Configuration: PROJECT_NAME
export CLOUDSDK_ACTIVE_CONFIG_NAME="CONFIG_NAME"

# Load .env first (if exists). Non-secret config only: no API keys or tokens.
dotenv_if_exists .env

# Use ADC: drop any key path a .env may have set
unset GOOGLE_APPLICATION_CREDENTIALS
export GOOGLE_CLOUD_PROJECT="PROJECT_ID"
export GOOGLE_CLOUD_LOCATION="REGION"
```

### Template 2: Service Account Key (Option C)

```bash
# GCP Configuration: PROJECT_NAME
export CLOUDSDK_ACTIVE_CONFIG_NAME="CONFIG_NAME"
export GOOGLE_CLOUD_PROJECT="PROJECT_ID"
export GOOGLE_CLOUD_LOCATION="REGION"
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/gcloud/credentials/PROJECT_NAME.json"
```

### Template 3: Minimal (gcloud CLI only)

```bash
export CLOUDSDK_ACTIVE_CONFIG_NAME="CONFIG_NAME"
```

`google.auth.default()` reads `GOOGLE_CLOUD_PROJECT`; the Google Gen AI SDK reads `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`. Export `PROJECT_ID` or `LOCATION` as well only when the project's own code reads those names, for example `export LOCATION="$GOOGLE_CLOUD_LOCATION"`.

## Agent Shells

direnv loads `.envrc` from a zsh hook (`_direnv_hook`) that runs before each prompt and on `cd`. Agent tools don't drive that prompt. Claude Code's Bash tool runs each command in a separate process, environment variables don't persist between commands, and it sources `~/.zshrc` only to capture aliases, functions, and shell options. So `.envrc` values are missing from agent commands unless something loads them. Treat Codex CLI the same way unless you have confirmed its shell loads direnv.

If Step 1 printed `none`, fix the hook first or tell the user: nothing loads `.envrc` on that machine.

### Option 1: `direnv exec` per command (any agent)

```bash
direnv exec . gcloud config list
direnv exec . python3 app.py

# Non-secret config from .envrc, secrets fetched for this one process
direnv exec . scripts/with-secrets.sh python3 app.py
```

`direnv exec DIR COMMAND` loads the first `.envrc` or `.env` found in DIR, then runs the command. If the `.envrc` hasn't been allowed, it prints a "blocked" error and doesn't run the command.

### Option 2: Claude Code hooks that write `CLAUDE_ENV_FILE`

SessionStart, Setup, CwdChanged, and FileChanged hooks can append `export` lines to the file named by `$CLAUDE_ENV_FILE`, and Claude Code runs that file before each Bash command. CwdChanged fires when a command changes the working directory; what a CwdChanged hook writes lasts until the next CwdChanged, when Claude Code clears it. Hook commands run in the current directory, so `direnv export bash` there prints the exports for that directory. Output from the `.envrc` itself (such as `echo`) goes to stderr, not into the file.

Put this in `.claude/settings.local.json` (one project, not committed) or `~/.claude/settings.json` (all projects), only when the user asks for it:

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "direnv export bash >> \"$CLAUDE_ENV_FILE\"" } ] }
    ],
    "CwdChanged": [
      { "hooks": [ { "type": "command", "command": "direnv export bash >> \"$CLAUDE_ENV_FILE\"" } ] }
    ]
  }
}
```

- Every exported value reaches every Bash command in the session, which is one more reason `.envrc` stays non-secret. Secrets still go through `scripts/with-secrets.sh`.
- `direnv allow` still applies: a blocked `.envrc` exports none of its variables.

## Least-privilege Roles

| Need | Role |
|------|------|
| Vertex AI / Gemini (Agent Platform) | `roles/aiplatform.user` |
| Read Cloud Storage objects | `roles/storage.objectViewer` |
| Read and write Cloud Storage objects | `roles/storage.objectUser` |
| Publish to Pub/Sub | `roles/pubsub.publisher` |
| Consume from Pub/Sub | `roles/pubsub.subscriber` |
| Deploy to Cloud Run | `roles/run.developer` |
| Call a private Cloud Run service | `roles/run.invoker` |
| Impersonate a service account | `roles/iam.serviceAccountTokenCreator`, on that service account |

Grant the role to the identity that calls the API: the user for Option A, the service account for B and C. Where a role can be granted on a single bucket, topic, or service, prefer that over the whole project.

```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:USER@EMAIL.COM" \
  --role="ROLE"
# For a service account: --member="serviceAccount:SA_EMAIL"
```

## Troubleshooting

See [references/troubleshooting.md](references/troubleshooting.md) for common issues.

**Quick fixes:**

```bash
# Quota project mismatch
gcloud auth application-default set-quota-project PROJECT_ID

# direnv not loading
direnv allow

# Agent command missing .envrc values
direnv exec . COMMAND
```

## References

- [Credential Strategies](references/credential-strategies.md) - ADC, impersonation, and key comparison; org-policy check; multi-account layouts
- [Troubleshooting](references/troubleshooting.md) - Common issues and fixes
- [Advanced Patterns](references/advanced-patterns.md) - Hierarchical .envrc, CI/CD, GKE, containers

## Sources (checked 2026-10-26)

Volatile facts this skill depends on. Re-check them when a command fails or a date matters.

- Credential order for local development, the impersonation command, and the Token Creator requirement: [Set up ADC for a local development environment](https://docs.cloud.google.com/docs/authentication/set-up-adc-local-dev-environment) and [Use service account impersonation](https://docs.cloud.google.com/docs/authentication/use-service-account-impersonation) (both updated 2026-10-22).
- Key-creation constraints `iam.managed.disableServiceAccountKeyCreation` (managed) and `iam.disableServiceAccountKeyCreation` (legacy, enforced by default for organizations created on or after 2024-05-03): [Restricting service account usage](https://docs.cloud.google.com/resource-manager/docs/organization-policy/restricting-service-accounts) (updated 2026-10-22).
- `gcloud org-policies describe CONSTRAINT --effective --project=PROJECT_ID`: [gcloud reference](https://docs.cloud.google.com/sdk/gcloud/reference/org-policies/describe) (updated 2026-05-27), output format from [Using constraints](https://docs.cloud.google.com/resource-manager/docs/organization-policy/using-constraints).
- `GOOGLE_CLOUD_LOCATION`: [googleapis/python-genai README](https://github.com/googleapis/python-genai).
- GitHub Actions: `google-github-actions/auth@v3` (latest release v3.0.0, 2025-08-28) and `setup-gcloud@v3` (v3.0.1); Direct Workload Identity Federation is the action's preferred mode.
- Workload Identity Federation for GKE principal identifiers: [GKE how-to](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/workload-identity) (updated 2026-10-22).
- `CLAUDE_ENV_FILE` from SessionStart, Setup, CwdChanged, and FileChanged hooks: [Claude Code hooks](https://code.claude.com/docs/en/hooks); Bash tool behavior: [tools reference](https://code.claude.com/docs/en/tools-reference).
- direnv hook placement with instant prompt: [Powerlevel10k README FAQ](https://github.com/romkatv/powerlevel10k#how-do-i-initialize-direnv-when-using-instant-prompt); `direnv exec` and `direnv export`: [direnv man page](https://direnv.net/man/direnv.1.html).
