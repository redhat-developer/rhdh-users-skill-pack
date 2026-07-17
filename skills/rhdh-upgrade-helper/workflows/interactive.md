# Workflow: Interactive Upgrade Assessment

This is the DEFAULT workflow when no `--config-path` is provided. It asks intake questions to build an environment profile, then delegates to `workflows/full-report.md` for the actual assessment.

## Step 1: Parse Input

Extract from $ARGUMENTS:

- `rhdh_to` (required): from `--to X.Y`
- `rhdh_from_release` (optional): from `--from X.Y`

**Validation:** `--to` is required. If missing, ask: "What RHDH version are you upgrading to?"

## Step 2: Ask Intake Questions

Follow `references/intake-questions.md` exactly. The flow prioritizes config files over manual questions:

1. Current RHDH version (skip if `--from` was provided)
2. Deployment method (Helm / Operator)
3. **Config files** — ask for file paths based on deployment method (Helm: values.yaml, app-config, dynamic-plugins; Operator: Backstage CR, app-config, dynamic-plugins)

**If config files provided:**

- Show the list of files found and their auto-detected types (Helm values, app-config, dynamic-plugins, Backstage CR)
- Ask: **"Are there additional config files in other locations? (e.g., a separate app-config or dynamic-plugins ConfigMap)"**
- If yes, collect more paths until the user says "done" or "that's all"
- If the user provided a directory path instead of individual files, scan it, show what was found, and still ask if there are more
- Once confirmed, switch to config-driven analysis. Skip Q4–Q7 — auth, SCM, plugins, and features are extracted from the files automatically. Proceed to Step 4.
- **Tip:** Suggest creating a `.rhdh-upgrade-helper.yaml` to save the file paths for future runs. See `references/rhdh-upgrade-helper-config.md`.

**If no config files ("skip") → continue with manual questions:**

4. Auth providers
5. SCM integration
6. Features in use
7. Scale / HA mode

Then proceed to Step 3 to build the environment profile.

## Step 3: Build Environment Profile (manual flow only)

Compile the answers into `$ENVIRONMENT_PROFILE` per `references/intake-questions.md`:

```json
{
  "source": "intake",
  "current_version": "{from Q1 or --from}",
  "deployment_method": "{from Q2}",
  "auth_providers": ["{from Q4}"],
  "scm_integrations": ["{from Q5}"],
  "features": ["{from Q6}"],
  "ha_mode": "{from Q7}",
  "relevant_workspaces": ["{mapped from features}"]
}
```

## Step 4: Run Full Report

Execute `workflows/full-report.md` with:

- `rhdh_to` from Step 1
- `rhdh_from_release` from Step 1 or Q1
- Config files from Q3 (config-driven path), OR `environment_profile` from Step 3 (manual path)

The full-report workflow handles product context gathering, correlation, scoring, and report compilation.
