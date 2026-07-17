# Secrets Detection

Before processing any customer-provided configuration file, scan for embedded secrets. Template variable references (`${VAR_NAME}`, `{{ .Values.x }}`) are safe — they are resolved at deploy time, not literal secrets.

## When to Run

Run this scan as the FIRST step after reading each config file, BEFORE any analysis. If secrets are found, warn the user and ask for confirmation before continuing.

## Detection Patterns

### 1. Literal values on secret-like keys

Flag any YAML key matching these patterns that has a **literal string value** (not a `${...}` or `{{ ... }}` template reference):

```
password, passwd, pwd
secret, clientSecret, client_secret
token, apiToken, api_token, accessToken, access_token
apiKey, api_key, apikey
private_key, privateKey
credentials, credential
```

**Example — FLAGGED:**

```yaml
clientSecret: aB3xYz-real-secret-value
```

**Example — SAFE (template reference):**

```yaml
clientSecret: ${AUTH_AZURE_CLIENT_SECRET}
```

### 2. Known secret prefixes

Flag any value (regardless of key name) matching these prefixes:

| Prefix | Service |
|--------|---------|
| `ghp_` | GitHub personal access token |
| `ghs_` | GitHub server-to-server token |
| `github_pat_` | GitHub fine-grained PAT |
| `glpat-` | GitLab personal access token |
| `sk-` | OpenAI/Anthropic API key |
| `xoxb-`, `xoxp-` | Slack bot/user token |
| `Bearer` | Authorization header |
| `Basic` | Basic auth header |
| `AKIA` | AWS access key ID |
| `ya29.` | Google OAuth token |

### 3. Base64-encoded blobs on sensitive keys

Flag values that look like base64-encoded secrets: 40+ character strings containing only `[A-Za-z0-9+/=]` when found as values for keys like `password`, `secret`, `token`, `key`, `certificate`, `tls.crt`, `tls.key`.

Exception: SHA256 digests used as image tags (e.g., `tag: "c8bd3d988c3f..."`) are NOT secrets — they're content-addressable image references. Only flag base64 on explicitly secret-named keys.

### 4. Inline certificates

Flag blocks that appear to contain PEM-encoded certificates or keys:

```
-----BEGIN RSA PRIVATE KEY-----
-----BEGIN PRIVATE KEY-----
-----BEGIN EC PRIVATE KEY-----
-----BEGIN CERTIFICATE-----
```

Exception: `-----BEGIN CERTIFICATE-----` in `tls.caCertificate` fields may be intentional for Helm values. Still warn but note it may be expected.

## Scan Implementation

For each config file provided via `--config-path`:

```bash
# Find literal secrets on secret-like keys (not template refs)
grep -nE '(password|passwd|secret|token|apiKey|api_key|private_key|credentials|clientSecret):\s+[^${\s]' "$FILE" | grep -v '^\s*#' | grep -v '\${'

# Find known secret prefixes
grep -nE '(ghp_|ghs_|github_pat_|glpat-|sk-|xoxb-|xoxp-|Bearer |Basic |AKIA|ya29\.)' "$FILE" | grep -v '^\s*#'

# Find PEM blocks
grep -n 'BEGIN.*PRIVATE KEY' "$FILE"
```

## Response When Secrets Detected

If any matches are found:

```
⚠️  POTENTIAL SECRETS DETECTED

The following lines in your configuration files appear to contain
literal secret values. Please review before continuing:

  values.yaml:285  clientSecret: aB3x... (possible API secret)
  values.yaml:392  token: glpat-...     (GitLab personal access token)

IMPORTANT: Do not share configuration files containing secrets.
Replace literal values with environment variable references
(e.g., ${MY_SECRET}) before providing files for analysis.

Would you like to:
1. Continue anyway (secrets will NOT be stored or transmitted)
2. Stop so you can redact the files first (recommended)
```

If the user chooses to continue, process the files but do NOT echo secret values in the output report. Replace detected secret values with `[REDACTED]` in any report output.

## Values That Are NOT Secrets

Do not flag these patterns:

- `${VAR_NAME}` — Helm/Backstage template variable references
- `{{ .Values.x }}` — Go template expressions
- `'{{ "{{inherit}}" }}'` — RHDH Helm chart inherit markers
- SHA256 digests used as container image tags (hex strings in `tag:` fields under `image:`)
- `sha512-...` integrity hashes for npm packages
- OCI image references (`oci://registry/image:tag`)
- Empty strings (`""`, `''`)
- Boolean values, numbers, null
