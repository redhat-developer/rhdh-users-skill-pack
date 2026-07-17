# RHDH Architecture Context

Reference for understanding what actually changes for customers during an RHDH upgrade. Used by the customer-360 skill to generate accurate predictions.

## Core Concept: What Customers Configure vs. What Changes Upstream

Customers interact with RHDH through **three configuration surfaces**:

1. **`app-config.yaml`** — Backstage configuration (auth, catalog, proxy, integrations)
2. **`dynamic-plugins.yaml`** — Plugin installation and enablement (OCI images, plugin config)
3. **Environment variables** — Feature flags, proxy settings, auth overrides

They do NOT interact with:
- The `rhdh-plugins` monorepo workspace structure
- The `rhdh-plugin-export-overlays` repo directly
- Backstage source code

**Critical rule for predictions:** A change in upstream source organization (workspace rename, consolidation, repo restructuring) does NOT affect customers unless it changes the plugin's NPM package name, OCI image reference, or configuration keys.

## Dynamic Plugin Loading Model

### How plugins get to the customer's cluster

1. **Build time:** `rhdh-plugin-export-overlays` automation exports plugins from source, packages them as OCI images, publishes to registries.
2. **Deploy time:** Customer's `dynamic-plugins.yaml` lists plugins by OCI image reference (`oci://registry/image:tag!plugin-path`).
3. **Pod start:** The `install-dynamic-plugins` init container downloads OCI images into `/dynamic-plugins-root/` shared volume.
4. **Runtime:** `backstage-backend` container loads plugins from the shared volume using `@backstage/backend-dynamic-feature-service`.

### What customers put in dynamic-plugins.yaml

```yaml
plugins:
  - package: oci://registry.redhat.io/rhdh/rhdh-hub-rhel9@sha256:abc123!backstage-plugin-foo
    disabled: false
    pluginConfig:
      dynamicPlugins:
        frontend:
          backstage-plugin-foo:
            dynamicRoutes:
              - path: /foo
                importName: FooPage
```

The `package` field uses the **OCI image reference** and **plugin path within the image**. This is decoupled from the upstream workspace name.

### What actually identifies a plugin at runtime

- **Backend plugins:** Identified by their Backstage plugin ID (from `createBackendPlugin({pluginId: '...'})`)
- **Frontend plugins:** Identified by `scalprum.name` in their `package.json` (usually the NPM package name)
- **OCI images:** Tagged with `bs_<backstage_version>__<plugin_version>` in the overlay repo's registry

## What Actually Breaks on Upgrade

### Tier 1: Direct customer impact (high confidence predictions)

| Change Type | What Breaks | How to Detect | Customer Symptom |
|---|---|---|---|
| **Plugin removed from release** | Plugin OCI image no longer published for the new release | Compare `default.packages.yaml` or workspace listings between releases | Pod fails to start — init container can't pull image |
| **Plugin moved from bundle to OCI-only** | Plugin was shipped inside the RHDH container image (local path `./dynamic-plugins/dist/...`) but is now only available via OCI registry (`oci://...`). Customer's `dynamic-plugins.yaml` still references the old local path. | Check `spec.dynamicArtifact` in workspace metadata on the target release branch (`workspaces/{workspace}/metadata/{image-name}.yaml` on `release-{X.Y}`). If it changed from `./dynamic-plugins/dist/...` to `oci://...`, the plugin requires OCI migration. If the metadata file is absent, the plugin was removed entirely. | Plugin silently disappears — no error, just missing UI tabs or broken functionality. The init container doesn't fail because it never tries to load a local-path plugin that doesn't exist. |
| **Plugin config key renamed/removed** | Customer's `pluginConfig` in `dynamic-plugins.yaml` has stale keys | Compare plugin CHANGELOGs for config schema changes | Plugin loads but doesn't work correctly, or throws config validation errors |
| **Backstage API breaking change** | Customer's custom-built plugins use removed/changed APIs | Check `@backstage/*` package version diff + upstream breaking change notes | Custom plugin crashes on load |
| **Frontend wiring migration** | Legacy `dynamicPlugins.frontend` config syntax deprecated | Compare Backstage version — 1.49+ moves to `app.extensions` | Frontend plugins don't render or render incorrectly |
| **Node.js major version change** | Native dependencies in custom plugins may be incompatible | Compare `versions.json` Node.js field between releases | Init container or runtime crash |
| **Auth provider changes** | Auth module behavior changes, new resolvers, changed defaults | Compare RHDH auth module code between releases | Login failures, token issues |

### Tier 2: Indirect impact (medium confidence predictions)

| Change Type | What Breaks | How to Detect | Customer Symptom |
|---|---|---|---|
| **Database schema additions** | New plugins require new DB schemas; `CREATEDB` privilege may be needed | Check if new plugins are enabled by default | Pod startup error about missing schemas |
| **MUI v5 styling changes** | Dynamic plugins lose default CSS declarations | Check if customer has custom frontend plugins using MUI | Visual regressions — broken layouts, missing styles |
| **Plugin version jump** | Large version jumps (3+ minor) increase regression risk | Compare plugin versions in overlay repo metadata between releases | Subtle behavioral changes in plugins |
| **Support level change** | Tech-preview → GA may change behavior expectations | Compare `spec.support` in overlay metadata between releases | Features work differently than in tech-preview |

### Tier 3: Does NOT break (common false positives to avoid)

| Change | Why It Does NOT Break |
|---|---|
| **Workspace renamed/consolidated** in rhdh-plugins monorepo | Plugin package names and OCI images are independent of workspace names |
| **Workspace added** upstream | New workspaces mean new plugins available, not breakage of existing ones |
| **Workspace removed** upstream | Only breaks if the plugin OCI image is no longer published. Check if the plugin was merged into another workspace (package name unchanged) vs. truly removed |
| **CHANGELOG entries about dependency updates** | Internal dependency changes don't affect the customer unless they change the plugin's external API |
| **Code churn** in upstream source | High churn indicates instability risk but does not directly break customer deployments |

## The Overlay Repo's Role

`rhdh-plugin-export-overlays` is the **metadata and automation hub** between source code and shipped artifacts:

- **`versions.json`**: Backstage version, Node.js version, CLI version for the release
- **`workspaces/{name}/source.json`**: Git commit SHA the plugin was built from
- **`workspaces/{name}/metadata/*.yaml`**: Per-plugin version, support level, config examples
- **`default.packages.yaml`**: Which plugins are enabled/disabled by default in the RHDH image

### What the overlay repo tells us about upgrade impact

1. **`versions.json` diff** → Backstage version jump, Node.js version jump (Tier 1 risks)
2. **Workspace listing diff** → New/removed plugin availability (check if removed = truly gone or just reorganized)
3. **`metadata/*.yaml` version diff** → Plugin version jumps (Tier 2 risk)
4. **`metadata/*.yaml` support diff** → Support level changes (Tier 2 risk)
5. **`default.packages.yaml` diff** → Newly enabled-by-default plugins (may affect resource usage, require new DB schemas)
6. **Bundle → OCI migration** → Plugins that moved from local bundle (`./dynamic-plugins/dist/`) to OCI-only (`oci://...`). This is a **Tier 1 risk** — the plugin silently disappears after upgrade unless the customer updates their `dynamic-plugins.yaml` to use the OCI reference. Detect by checking `spec.dynamicArtifact` in workspace metadata on the target release branch — if it changed from `./dynamic-plugins/dist/` to `oci://`, the plugin requires OCI migration. If the metadata file is absent, the plugin was removed entirely.

## Plugin Storage: Ephemeral vs. NFS

| Mode | When Used | Upgrade Impact |
|---|---|---|
| **Ephemeral** (default, single pod) | Volume recreated each pod start; plugins re-downloaded | Clean upgrade — no stale artifacts |
| **Persistent/NFS** (multi-pod) | Shared volume; plugins downloaded once | Stale lock files can block pod starts after unclean termination. Stale plugin versions can persist if download step is skipped |

Lock file location: `/dynamic-plugins-root/install-dynamic-plugins.lock`

## RHDH Release Structure

- **RHDH version** (e.g., 1.10) → pinned **Backstage version** (e.g., 1.49.4) → determines API compatibility
- **Plugin versions** are independent of RHDH version — they version on their own cadence
- **OCI image tags** encode both: `bs_1.49.4__1.2.3` (Backstage version + plugin version)
- **Overlay repo branches**: `release-X.Y` (e.g., `release-1.10`)

## Prediction Quality Rules

1. **Never predict breakage from workspace renames/consolidation** — workspace is source organization, not runtime identity
2. **Always verify plugin removal** means the OCI image is truly gone, not just reorganized under a different workspace
3. **Backstage version jump size** is the strongest signal for custom plugin breakage — 4+ minor versions = high risk
4. **Node.js major version jump** is the strongest signal for native dependency breakage
5. **Frontend wiring migration** (legacy → new frontend system) is the strongest signal for frontend config breakage
6. **Check what customers actually configure** (their `dynamic-plugins.yaml` and `app-config.yaml`) — predict breakage in those surfaces, not in upstream internals they never touch
7. **Always check for bundle→OCI migrations** for every upgrade. Plugins are progressively moved from the RHDH container image bundle to OCI-only distribution across releases. If a customer's `dynamic-plugins.yaml` references `./dynamic-plugins/dist/...` for a plugin that is now OCI-only, the plugin will silently disappear after upgrade. Detect by checking `spec.dynamicArtifact` in workspace metadata on the target release branch — see `references/config-analysis.md` Section 1.
