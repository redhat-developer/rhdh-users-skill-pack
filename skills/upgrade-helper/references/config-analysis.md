# Config Analysis: Customer Configuration Parsing

This reference defines how to parse customer configuration files and produce actionable migration findings. Config files can come from `.upgrade-helper.yaml`, `--config` flags, `--config-path` directory scan, or the interactive workflow. See `references/upgrade-helper-config.md` for input resolution order.

## File Discovery

### RHDH Local auto-detection

When scanning a directory, first check if it is an **rhdh-local** project structure:

```bash
# Check for rhdh-local indicators
ls {config_path}/compose.yaml 2>/dev/null
ls {config_path}/configs/app-config/ 2>/dev/null
ls {config_path}/configs/dynamic-plugins/ 2>/dev/null
ls {config_path}/default.env 2>/dev/null
```

If `compose.yaml` and `configs/` subdirectory both exist, treat this as an **rhdh-local project**:

1. **Detect RHDH version** from `compose.yaml` and `default.env`:
   - Read `RHDH_IMAGE` default from compose.yaml (e.g., `quay.io/rhdh-community/rhdh:1.10` → version `1.10`)
   - Read `CATALOG_INDEX_IMAGE` from `default.env` (e.g., `quay.io/rhdh/plugin-catalog-index:1.10`)
   - Use for `--to` if not provided via CLI. If `.env` overrides the image tag, use that instead.
2. **Auto-discover all config files** by scanning the `configs/` subtree recursively:
   - `configs/app-config/*.yaml` → all app-config files
   - `configs/dynamic-plugins/*.yaml` → all dynamic-plugins files
   - `configs/extra-files/` → any additional config
3. **Read env files**: `default.env` first, then `.env` (overrides)
4. Set `environment.deployment_method` to `local`

This means an rhdh-local user can simply run:
```
/upgrade-helper --config-path ./rhdh-local/
```
and the skill discovers everything automatically — version, configs, env vars.

### Standard directory scan

When the directory is NOT an rhdh-local project, scan for these file patterns:

| Pattern | Examples |
|---------|----------|
| `values*.yaml` | `values.yaml`, `values-prod.yaml` |
| `dynamic-plugins*.yaml` | `dynamic-plugins.yaml`, `dynamic-plugins-override.yaml` |
| `app-config*.yaml` | `app-config.yaml`, `app-config-auth.yaml` |
| `compose.yaml`, `docker-compose.yaml` | Compose files (extract RHDH image version) |
| `*.env`, `.env*` | `.env`, `.env.local`, `env.sh` |
| `backstage*.yaml` (with `kind: Backstage`) | `backstage-cr.yaml` |

### When files are provided individually (`--config` or `.upgrade-helper.yaml`)

Do NOT rely on filename — auto-detect the type from content.

## File Type Auto-Detection

For every config file (whether discovered by directory scan or provided individually), classify by content:

| Content marker | Detected type | How to parse |
|---|---|---|
| Contains `global.dynamic.plugins` or `upstream.backstage` | **Helm values** | Extract nested config — see "Parsing Helm Values" below |
| Top-level `plugins:` array with `package:` entries | **Dynamic plugins config** | Parse `plugins:` array directly |
| Top-level `auth:`, `catalog:`, `backend:`, or `proxy:` keys | **App-config** | Parse as root-level Backstage configuration |
| `kind: Backstage` or `apiVersion: rhdh.redhat.com` | **Backstage CR (Operator)** | Extract environment facts — see "Parsing Backstage CR" below |
| Top-level `services:` with an `image:` containing `rhdh` | **Compose file** | Extract RHDH image version — see "Parsing Compose Files" below |
| `KEY=VALUE` pairs (no YAML structure) | **Environment file** | Parse as env vars — see `references/env-vars.md` |

When a file matches multiple markers (e.g., Helm values contain `auth:` under `upstream.backstage.appConfig`), use the most specific match. `global.dynamic.plugins` or `upstream.backstage` → Helm values takes precedence.

## Merging Multiple App-Config Files

Backstage merges multiple app-config files in order — later files override earlier ones (deep merge per key). The skill must do the same before analysis:

1. Sort discovered app-config files alphabetically (e.g., `app-config.yaml` before `app-config.local.yaml`)
2. Deep-merge them in order — later files override keys from earlier files
3. Analyze the **merged result** as one config

This prevents:
- False positives from flagging something in `app-config.yaml` that is overridden in `app-config.local.yaml`
- Missed findings from keys that only exist in `app-config.local.yaml`
- Duplicate findings from both files

Report findings against the **source file** where the final value comes from (not the merged result), so the customer knows which file to edit.

## Parsing Compose Files

When a compose file is detected (rhdh-local or standalone), extract:

- `RHDH_IMAGE` default value → parse the tag to determine the RHDH version (e.g., `quay.io/rhdh-community/rhdh:1.10` → `1.10`)
- Use as `rhdh_to` if not provided via CLI args or `.upgrade-helper.yaml`
- Set `environment.deployment_method` to `local`

Also check for `CATALOG_INDEX_IMAGE` in compose env or `default.env` for the catalog index version.

## Parsing Backstage CR (Operator deployments)

When a file is detected as a Backstage CR, extract these environment facts:

- Set `environment.deployment_method` to `operator`
- Capture `metadata.name` as the instance name
- Note referenced ConfigMap and Secret names from `spec.application.appConfig.configMaps` and `spec.application.dynamicPluginsConfigMapName`

The actual config content (app-config, dynamic-plugins) must be provided as separate files. The CR tells us it's an Operator deployment and which ConfigMaps are involved, but doesn't contain the plugin/auth configuration itself.

## Parsing Helm Values

Helm values embed RHDH config in nested paths. Extract these sections:

### Dynamic plugins from Helm values

```bash
# The plugins list may be at one of these paths:
# 1. global.dynamic.plugins (array of plugin entries)
# 2. global.dynamic.includes[].dynamic-plugins.yaml (references a separate file)
python3 -c "
import yaml, sys
with open('$CONFIG_PATH/values.yaml') as f:
    v = yaml.safe_load(f)
plugins = v.get('global',{}).get('dynamic',{}).get('plugins',[])
for i, p in enumerate(plugins):
    pkg = p.get('package','')
    disabled = p.get('disabled', False)
    print(f'{i}: package={pkg} disabled={disabled}')
"
```

### App-config from Helm values

```bash
# App config is typically at upstream.backstage.appConfig
python3 -c "
import yaml, sys, json
with open('$CONFIG_PATH/values.yaml') as f:
    v = yaml.safe_load(f)
app_config = v.get('upstream',{}).get('backstage',{}).get('appConfig',{})
print(json.dumps(app_config, indent=2))
"
```

## Parsing Dynamic Plugins Config

For each plugin entry in the `plugins:` array, check:

### 1. Bundle-to-OCI Migration (ALWAYS Critical)

Flag **every** `package:` value starting with `./dynamic-plugins/dist/` as **Critical**. No exceptions, no downgrades.

**Why this is always Critical — do NOT rationalize a downgrade:**
- Local paths reference files pre-built inside the RHDH container image. The container image changes with every release.
- `default.packages.yaml` lists NPM package names, NOT local filesystem paths. A package existing in `default.packages.yaml` does NOT mean `./dynamic-plugins/dist/package-name-dynamic` still exists inside the new container image.
- When a local path doesn't exist, the plugin **silently disappears** — no error in logs, no init container failure, just missing functionality. This is the highest-impact silent failure mode.
- The only way to verify whether a local path still exists is to inspect the target container image directly. Since we can't do that, **always treat local-path references as Critical**.

```bash
# Find local-path plugin references with line numbers
grep -n './dynamic-plugins/dist/' "$CONFIG_PATH/dynamic-plugins.yaml" 2>/dev/null
grep -n './dynamic-plugins/dist/' "$CONFIG_PATH/values.yaml" 2>/dev/null
```

**Recommended fix for each local-path reference:**

1. **Best:** Remove the explicit entry entirely. If the plugin is in `dynamic-plugins.default.yaml` (loaded via `includes:`), it's already handled. The customer just needs to override `disabled: false` if the default is disabled.
2. **Alternative:** Replace the `./dynamic-plugins/dist/` path with the OCI reference resolved from the overlay repo workspace metadata.

#### Building the plugin metadata index

Before resolving individual plugins, build a **metadata index** that maps every known `dynamicArtifact` path and image name to its metadata file. This handles all naming patterns (full names, `rhdh-bsp-*` abbreviations, `rhdh-backstage-plugin-*`, etc.) seamlessly.

**Step 0 — Clone the overlay repo (run once per session):**

The overlay repo is cloned locally in `workflows/full-report.md` Step 2. All metadata lookups use the local clone at `/tmp/rhdh-overlays-{X.Y}/` — zero API calls, no rate limits, instant reads.

```bash
# Already cloned in Step 2:
# /tmp/rhdh-overlays-{X.Y}/workspaces/*/metadata/*.yaml
```

**Why a two-pass lookup is necessary:** The overlay repo uses multiple naming patterns for metadata files:

| Customer's local path contains | Metadata file might be named |
|---|---|
| `red-hat-developer-hub-backstage-plugin-extensions` | `rhdh-bsp-extensions.yaml` |
| `red-hat-developer-hub-backstage-plugin-adoption-insights` | `rhdh-bsp-adoption-insights.yaml` |
| `red-hat-developer-hub-backstage-plugin-orchestrator` | `rhdh-bsp-orchestrator.yaml` |
| `backstage-plugin-catalog-backend-module-gitlab` | `backstage-plugin-catalog-backend-module-gitlab.yaml` |
| `roadiehq-scaffolder-backend-module-http-request` | `roadiehq-scaffolder-backend-module-http-request.yaml` |
| `rhdh-backstage-plugin-scorecard` | `rhdh-backstage-plugin-scorecard.yaml` |

A filename-based lookup fails for abbreviated names. The `spec.dynamicArtifact` field is the only reliable key — it contains the exact `./dynamic-plugins/dist/` path or `oci://` reference that matches the customer's config.

With the local clone, both passes are instant:
1. **Pass 1 (by filename):** `find /tmp/rhdh-overlays-{X.Y}/workspaces -name "{image-name}.yaml" -path "*/metadata/*"`
2. **Pass 2 (by dynamicArtifact content):** `grep -rl "dynamicArtifact:.*{local-path}" /tmp/rhdh-overlays-{X.Y}/workspaces/*/metadata/`

#### Resolving the OCI replacement from workspace metadata

For each `./dynamic-plugins/dist/` reference, look up the OCI replacement:

**Step 1 — Derive the image name:**

```
./dynamic-plugins/dist/backstage-plugin-catalog-backend-module-gitlab-dynamic
  → strip "./dynamic-plugins/dist/" prefix
  → strip "-dynamic" suffix (if present)
  → "backstage-plugin-catalog-backend-module-gitlab"
```

**Step 2 — Find the metadata file (two-pass lookup using local clone):**

**Pass 1 (by filename):**
```bash
find /tmp/rhdh-overlays-{X.Y}/workspaces -name "{image-name}.yaml" -path "*/metadata/*"
```

**Pass 2 (fallback — by dynamicArtifact content):** If Pass 1 finds no match, grep across all metadata files:
```bash
grep -rl "dynamicArtifact:.*{local-path}" /tmp/rhdh-overlays-{X.Y}/workspaces/*/metadata/
```
This finds the metadata file regardless of its filename — handles `rhdh-bsp-*`, `rhdh-backstage-plugin-*`, and any other naming pattern.

**Step 3 — Read `spec.dynamicArtifact` from the matched metadata file:**

```bash
cat /tmp/rhdh-overlays-{X.Y}/workspaces/{workspace}/metadata/{matched-file}.yaml
```

- **If `oci://...`** → The plugin is **OCI-only** in the target release. The local path will fail. Use this `spec.dynamicArtifact` value directly as the replacement.
- **If `./dynamic-plugins/dist/...`** → The plugin is **still bundled**. Flag as **Important** — recommend removing the explicit entry and relying on `dynamic-plugins.default.yaml` defaults. **Do NOT construct an OCI reference** that doesn't exist in metadata.
- **If no metadata match found (both passes failed)** → The plugin is not available in the target release. Flag as **Critical** with "plugin removed from target release" message.

**Step 4 — Produce migration findings:**

For each local-path plugin, create a migration issue with:
- `file`: config file path
- `line`: line number of the `package:` entry
- `severity`: `critical` (if OCI-only or removed) or `important` (if still bundled)
- `category`: `bundle-to-oci`
- `current`: the `./dynamic-plugins/dist/...` value
- `replacement`: the `spec.dynamicArtifact` OCI reference (if OCI-only), or "Remove explicit entry; plugin is available via `dynamic-plugins.default.yaml` defaults" (if still bundled)
- `reason`: "OCI-only in target release — local path will fail" or "Still bundled, but recommend relying on defaults for forward compatibility"

### 2. Validate Existing OCI References

For every `oci://` reference in the customer's config, verify it is still valid for the target release:

**Step 1 — Extract the image name from the OCI reference:**

```
oci://ghcr.io/redhat-developer/rhdh-plugin-export-overlays/immobiliarelabs-backstage-plugin-gitlab:bs_1.49.4__7.0.1
  → image name: immobiliarelabs-backstage-plugin-gitlab
```

Strip the registry prefix and everything after the `:` tag or `@` digest.

**Step 2 — Find the metadata (two-pass lookup using local clone):**

Use the same two-pass approach as Section 1:
1. **Pass 1:** `find /tmp/rhdh-overlays-{X.Y}/workspaces -name "{image-name}.yaml" -path "*/metadata/*"`
2. **Pass 2:** `grep -rl "dynamicArtifact:.*{image-name}" /tmp/rhdh-overlays-{X.Y}/workspaces/*/metadata/`

**Step 3 — Compare:**

- Check that the plugin still exists in workspace metadata for the target release. If not → flag as **Critical** ("plugin removed").
- Compare the customer's OCI tag/digest with the `spec.dynamicArtifact` in metadata:
  - If the tag matches (same `bs_{version}__{plugin_version}`) → valid, no action needed.
  - If the tag is older (different backstage version or plugin version) → flag as **Important** with the updated reference from `spec.dynamicArtifact`.
  - If the customer's reference uses a tag but metadata uses a digest (or vice versa) → informational, both are valid.

**Step 4 — Produce validation findings:**

For OCI references that need updating:
- `file`: config file path
- `line`: line number
- `severity`: `critical` (removed) or `important` (outdated tag)
- `category`: `oci-version-mismatch`
- `current`: the customer's OCI reference
- `replacement`: the `spec.dynamicArtifact` from metadata
- `reason`: "Plugin removed from target release" or "OCI reference targets older version; update to {version} for target release compatibility"

### 3. Removed/Renamed Plugins

Check each configured plugin package name against the target release's `default.packages.yaml`. If a package is not listed, it may have been removed or renamed.

### 4. Disabled Plugins Still Referenced

Flag plugins with `disabled: true` that reference local paths — even disabled, they'll cause warnings if the path doesn't exist after upgrade.

## Parsing App-Config

### Auth Provider Analysis

Extract auth provider configuration:

```bash
# Find auth provider blocks
grep -n 'auth:' "$CONFIG_PATH/app-config.yaml" 2>/dev/null
grep -n 'providers:' "$CONFIG_PATH/app-config.yaml" 2>/dev/null
grep -n 'microsoft:' "$CONFIG_PATH/app-config.yaml" 2>/dev/null
grep -n 'gitlab:' "$CONFIG_PATH/app-config.yaml" 2>/dev/null
grep -n 'github:' "$CONFIG_PATH/app-config.yaml" 2>/dev/null
grep -n 'oidc:' "$CONFIG_PATH/app-config.yaml" 2>/dev/null
```

Check for deprecated auth resolver names between Backstage versions:
- `userIdMatchingUserEntityAnnotation` — valid but check if the exact resolver name changed
- `signInResolvers` array format — changed in some Backstage versions

### Proxy Configuration

```bash
grep -n 'proxy:' "$CONFIG_PATH/app-config.yaml" 2>/dev/null
grep -n '/api/' "$CONFIG_PATH/app-config.yaml" 2>/dev/null
```

### Database Configuration

```bash
grep -n 'database:' "$CONFIG_PATH/app-config.yaml" 2>/dev/null
grep -n 'postgres' "$CONFIG_PATH/app-config.yaml" 2>/dev/null
grep -n 'connection:' "$CONFIG_PATH/app-config.yaml" 2>/dev/null
```

## Environment Extraction

From the parsed config files, extract concrete environment facts:

| Fact | How to Extract |
|------|---------------|
| Deployment method | `values.yaml` present → Helm. `backstage` CR YAML present → Operator. |
| Auth providers | Keys under `auth.providers` in app-config |
| Database type | `backend.database.client` value (`pg` = Postgres, `better-sqlite3` = local) |
| Database host | `backend.database.connection.host` — if contains `azure` or `rds`, note cloud provider |
| SCM integrations | Keys under `integrations` in app-config (`github`, `gitlab`, `bitbucket`) |
| Proxy endpoints | Count of entries under `proxy.endpoints` |
| Total plugins | Count of entries in `plugins:` array in dynamic-plugins config |
| Enabled plugins | Count where `disabled` is not `true` |
| Catalog locations | Count and types under `catalog.locations` |

## Output Structure

Capture as `$CONFIG_ANALYSIS`:

```json
{
  "config_path": "/path/to/configs",
  "files_found": ["values.yaml", "dynamic-plugins.yaml"],
  "environment": {
    "deployment_method": "helm|operator",
    "auth_providers": ["microsoft", "gitlab"],
    "database_type": "pg",
    "database_host": "my-azure-postgres.postgres.database.azure.com",
    "scm_integrations": ["gitlab"],
    "proxy_endpoint_count": 5,
    "total_plugins": 28,
    "enabled_plugins": 22,
    "catalog_location_count": 12
  },
  "migration_issues": [
    {
      "file": "values.yaml",
      "line": 36,
      "severity": "critical",
      "category": "bundle-to-oci",
      "current": "./dynamic-plugins/dist/roadiehq-scaffolder-backend-module-http-request-dynamic",
      "replacement": "oci://registry.access.redhat.com/rhdh/roadiehq-scaffolder-backend-module-http-request@sha256:2e498...",
      "reason": "Plugin is OCI-only in target release (spec.dynamicArtifact is an oci:// reference)"
    },
    {
      "file": "values.yaml",
      "line": 25,
      "severity": "important",
      "category": "bundle-to-oci",
      "current": "./dynamic-plugins/dist/backstage-plugin-catalog-backend-module-gitlab-dynamic",
      "replacement": "Remove explicit entry; plugin is available via dynamic-plugins.default.yaml defaults (override disabled: false if needed)",
      "reason": "Still bundled, but recommend relying on defaults for forward compatibility"
    },
    {
      "file": "values.yaml",
      "line": 63,
      "severity": "important",
      "category": "oci-version-mismatch",
      "current": "oci://ghcr.io/.../immobiliarelabs-backstage-plugin-gitlab:bs_1.45.3__6.0.0",
      "replacement": "oci://ghcr.io/.../immobiliarelabs-backstage-plugin-gitlab:bs_1.49.4__7.0.1",
      "reason": "OCI reference targets older version; update to bs_1.49.4__7.0.1 for target release"
    }
  ],
  "deprecated_config_keys": [
    {
      "file": "app-config.yaml",
      "line": 15,
      "path": "auth.providers.microsoft.signInResolvers",
      "issue": "Resolver name format changed in Backstage 1.48",
      "fix": "Update resolver name to match new format"
    }
  ],
  "plugin_summary": {
    "total": 28,
    "local_path": 3,
    "oci": 22,
    "disabled": 6,
    "needs_migration": 3
  }
}
```

## Severity Rules

| Finding | Severity | Downgrade allowed? |
|---------|----------|--------------------|
| Local-path plugin reference (`./dynamic-plugins/dist/`) | **Critical** — plugin silently disappears after upgrade | **NO.** Never downgrade to Important/Informational. The presence in `default.packages.yaml` does NOT confirm the local filesystem path exists in the target container image. |
| Plugin package not found in target release's package list | **Critical** — plugin may be removed or renamed | No |
| Deprecated auth resolver name | **Critical** — login will fail after upgrade | No |
| Deprecated config key | **Important** — may cause warnings or unexpected behavior | Yes, to Informational if the key is still functional |
| Disabled plugin with local path | **Important** — won't cause runtime error but config is stale | Yes |
