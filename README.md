> [!WARNING]
> **Work in Progress:** This project is under development. Things might break, and documentation may be incomplete.

# RHDH Users Skill Pack

Agent Skills for adopting and using [Red Hat Developer Hub](https://developers.redhat.com/products/rhdh/overview) (RHDH) effectively.

> **Quick start:** `npx skills add redhat-developer/rhdh-users-skill-pack` — works with [50+ coding agents](https://github.com/vercel-labs/skills#supported-agents).

## What's included

| Skill | Use when you want to… |
| ----- | --------------------- |
| [skill-maker](./skills/skill-maker/SKILL.md) | Create, audit, and consolidate Agent Skills following the open standard |
| [upgrade-helper](./skills/upgrade-helper/SKILL.md) | Prepare for an RHDH upgrade — analyzes your config files against a target release and produces a personalized migration plan |
| [rhdh-templates](./skills/rhdh-templates/SKILL.md) | Author, validate, and test RHDH Software Templates (Scaffolder)         |

### Upgrade assessment (`upgrade-helper`)

Analyzes your RHDH configuration against a target release and produces a personalized migration plan — showing exactly what affects your setup and what doesn't. Works with Helm, Operator, and rhdh-local deployments.

**What it does:**

- Resolves OCI references for every plugin via overlay repo workspace metadata
- Validates existing OCI plugin tags against the target release
- Searches RHDHBUGS Jira per-plugin for known bugs affecting your versions
- Filters breaking changes into "Affects You" vs "Does NOT Affect You"
- Computes a 0-100 Readiness Score with transparent breakdown
- Includes bundled release notes for RHDH 1.4–1.10

**How to invoke:**

```bash
# With a .upgrade-helper.yaml config file (recommended for repeat use)
/upgrade-helper

# With individual files
/upgrade-helper --from 1.8 --to 1.10 --config ./values.yaml --config ./app-config.yaml

# With a config directory
/upgrade-helper --to 1.10 --config-path ./my-configs/

# With an rhdh-local project (auto-discovers configs, version, env vars)
/upgrade-helper --to 1.10 --config-path ./rhdh-local/

# Interactive (no config files)
/upgrade-helper --to 1.10
```

Run `/upgrade-helper --help` for full documentation.

### Software Templates (`rhdh-templates`)

Interactive authoring for RHDH Scaffolder templates — templatize an existing repo, create from scratch, fix common gotchas, and validate locally or against a running instance.

- **[rhdh-templates](./skills/rhdh-templates/SKILL.md)** — Interactive authoring and validation for Software Templates. Includes curated reference catalog (official library + AI quickstarts), worked examples (`nodejs-backend`, `java-springboot`) and bundled JSON Schema validation. Sub-commands:
  - **[init](./skills/rhdh-templates/references/init.md)** — Check tooling, scaffold template repo layout, optional RHDH connectivity.
  - **[templatize](./skills/rhdh-templates/references/templatize.md)** — Convert existing codebase into a parameterized template.
  - **[create](./skills/rhdh-templates/references/create.md)** — Guided from-scratch template authoring when no reference code exists.
  - **[add-parameter](./skills/rhdh-templates/references/add-parameter.md)** — Add a parameter or parameter group to existing `template.yaml`.
  - **[add-step](./skills/rhdh-templates/references/add-step.md)** — Add a scaffolder step to existing `template.yaml`.
  - **[add-skeleton](./skills/rhdh-templates/references/add-skeleton.md)** — Add or parameterize skeleton files with Nunjucks.
  - **[create-location](./skills/rhdh-templates/references/create-location.md)** — Generate or update root `location.yaml` for catalog registration.
  - **[fix-gotchas](./skills/rhdh-templates/references/fix-gotchas.md)** — Auto-fix common RHDH template mistakes (raw/endraw blocks, catalog-info path, etc.).
  - **[validate](./skills/rhdh-templates/references/validate.md)** — Local YAML schema, gotcha validation, and optional Nunjucks lint via `--lint-skeleton` (no RHDH required).
  - **[list-actions](./skills/rhdh-templates/references/list-actions.md)** — List available Scaffolder actions from a running RHDH instance.
  - **[dry-run](./skills/rhdh-templates/references/dry-run.md)** — Test template execution via Scaffolder v2 dry-run API.
  - **[explain-action](./skills/rhdh-templates/references/explain-action.md)** — Show action input schema or template parameter schema.
  - **[example-catalog](./skills/rhdh-templates/references/example-catalog.md)** — Browse curated reference templates (official library, AI quickstarts, bundled).

Example prompts:

- "Help me turn this Node.js repo into an RHDH Software Template"
- "Validate my `template.yaml` and fix Scaffolder gotchas"
- "List scaffolder actions available on my RHDH instance"

### Agent Skills authoring (`skill-maker`)

Create, audit, or consolidate [Agent Skills](https://agentskills.io/specification) — useful when packaging your own RHDH workflows or contributing skills to this pack.

Example prompts:

- "Help me create a skill for our team's RHDH onboarding workflow"
- "Audit this SKILL.md — it never triggers when I expect it to"
- "Merge these two skills into one router skill"

## Installation

```bash
npx skills add redhat-developer/rhdh-users-skill-pack
```

Or install only one skill:

```bash
npx skills add redhat-developer/rhdh-users-skill-pack --skill rhdh-templates
npx skills add redhat-developer/rhdh-users-skill-pack --skill skill-maker
```

### List skills without installing

```bash
npx skills add redhat-developer/rhdh-users-skill-pack --list
```

### Target a specific agent

```bash
npx skills add redhat-developer/rhdh-users-skill-pack -a claude-code
npx skills add redhat-developer/rhdh-users-skill-pack -a cursor
```

Supported agents include Claude Code, Cursor, Codex, Pi, and [many others](https://github.com/vercel-labs/skills#supported-agents).

### Local checkout (development)

```bash
git clone https://github.com/redhat-developer/rhdh-users-skill-pack.git
npx skills add ./rhdh-users-skill-pack
```

## How to use

1. **Install** the pack (see above).
2. **Open your project** in an agent-enabled editor or CLI.
3. **Describe your goal in plain language** — for example, "help me turn this repo into an RHDH Software Template."

You can also name the skill explicitly:

```
Use the rhdh-templates skill to validate my template.yaml
Use the skill-maker skill to audit my SKILL.md
```

## Frequently asked questions

### What is an Agent Skill?

A folder with a `SKILL.md` file (YAML front matter + instructions) that agents load when relevant. See the [Agent Skills specification](https://agentskills.io/specification).

### How is this different from `redhat-developer/rhdh-skill`?

This repository is the **user-facing** skill pack — skills for adopting and operating RHDH. The [`rhdh-skill`](https://github.com/redhat-developer/rhdh-skill) repo adds skills used by the RHDH engineering team (Jira, release management, Extensions Catalog, lifecycle checks, CI tooling) that are not needed for most RHDH users.

### Can I contribute a new skill?

Yes. See [CONTRIBUTING.md](./CONTRIBUTING.md). Proposed skills should help RHDH users adopt or operate the platform and follow the Agent Skills open standard. Use `skill-maker` to draft and review new skills before opening a PR.

### Where do I get help?

- RHDH product documentation: [Red Hat Developer Hub](https://docs.redhat.com/en/documentation/red_hat_developer_hub)
- Issues and feature requests: [GitHub Issues](https://github.com/redhat-developer/rhdh-users-skill-pack/issues)

## Development

For contributors validating changes locally:

```bash
git clone https://github.com/redhat-developer/rhdh-users-skill-pack.git
cd rhdh-users-skill-pack
uv sync --extra dev
git config core.hooksPath .githooks
uv run pytest
```

See [CONTRIBUTING.md](./CONTRIBUTING.md) and [AGENTS.md](./AGENTS.md) for contribution guidelines.

## License

Apache-2.0 — see [LICENSE](./LICENSE).
