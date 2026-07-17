# RHDH Local: Pre-Upgrade Testing Recommendation

## Purpose

RHDH Local lets customers test their configuration changes locally using `podman compose` before deploying to a Kubernetes cluster. This is the safest way to validate an upgrade — no cluster required, no risk to production.

## Direct Analysis of RHDH Local Projects

The rhdh-upgrade-helper skill can analyze an rhdh-local project directory directly:

```
/rhdh-upgrade-helper --to 1.10 --config-path ./rhdh-local/
```

When the skill detects an rhdh-local project structure (`compose.yaml` + `configs/` directory), it:
- Auto-discovers all config files in `configs/app-config/` and `configs/dynamic-plugins/`
- Merges multiple app-config files (e.g., `app-config.yaml` + `app-config.local.yaml`)
- Extracts the current RHDH version from `compose.yaml` / `default.env`
- Reads env vars from `default.env` and `.env`

See `references/config-analysis.md` "RHDH Local auto-detection" for details.

## Detection

Check if the customer already has RHDH Local set up:

```bash
# Check working directory and parent directories
find . -maxdepth 3 -name 'compose.yaml' -exec grep -l 'rhdh' {} \; 2>/dev/null
find . -maxdepth 3 -type d -name 'configs' -exec test -d '{}/app-config' \; -print 2>/dev/null
```

## Report Output

### If RHDH Local is detected:

```
### Pre-Upgrade Testing

RHDH Local detected at `{path}`. Use it to validate your updated configuration
before deploying to your cluster:

1. Update your local RHDH image tag to the target version
2. Apply the config changes from the "Critical" section above
3. Run `podman compose up` and verify:
   - Pods start without errors
   - Authentication works
   - Your plugins load correctly
   - Catalog providers sync
```

### If RHDH Local is NOT detected:

```
### Pre-Upgrade Testing with RHDH Local

Before deploying this upgrade to your cluster, consider testing locally with
**RHDH Local** — a lightweight setup that runs RHDH using `podman compose`
on your workstation. No Kubernetes cluster required.

**Why:** Testing locally catches configuration issues before they affect
your production environment. The changes identified in this report can be
validated in minutes without risking a failed upgrade on your cluster.

**Get started:**
1. Clone rhdh-local: `git clone https://github.com/redhat-developer/rhdh-local.git`
2. Copy your updated config files into the rhdh-local directory
3. Set the target RHDH version in the compose configuration
4. Run `podman compose up` and verify the changes from this report
5. Once validated, apply the same changes to your cluster deployment

For setup instructions, see the RHDH Local repository:
https://github.com/redhat-developer/rhdh-local
```
