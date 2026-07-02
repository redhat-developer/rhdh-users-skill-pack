> [!WARNING]
> **Work in Progress:** This project is under development. Things might break, and documentation may be incomplete.

# RHDH Users Skill Pack

Agent Skills for adopting and using [Red Hat Developer Hub](https://developers.redhat.com/products/rhdh/overview) (RHDH) effectively.

> **Quick start:** `npx skills add redhat-developer/rhdh-users-skill-pack` — works with [50+ coding agents](https://github.com/vercel-labs/skills#supported-agents).

## What's included

| Skill | Use when you want to… |
| ----- | --------------------- |
| [rhdh-templates](./skills/rhdh-templates/SKILL.md) | Author, validate, and test RHDH Software Templates (Scaffolder) |
| [skill-maker](./skills/skill-maker/SKILL.md) | Create, audit, and consolidate Agent Skills following the open standard |

### Software Templates (`rhdh-templates`)

Interactive authoring for RHDH Scaffolder templates — templatize an existing repo, create from scratch, fix common gotchas, and validate locally or against a running instance.

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
3. **Describe your goal in plain language** — for example, "help me turn this repo into an RHDH Software Template" or "help me write a skill for our RHDH golden paths."

You can also name the skill explicitly:

```
Use the skill-maker skill to audit my SKILL.md
```

## Frequently asked questions

### What is an Agent Skill?

A folder with a `SKILL.md` file (YAML front matter + instructions) that agents load when relevant. See the [Agent Skills specification](https://agentskills.io/specification).

### How is this different from `redhat-developer/rhdh-skill`?

This repository is the **user-facing** skill pack — skills for adopting and operating RHDH. The internal [`rhdh-skill`](https://github.com/redhat-developer/rhdh-skill) repo adds Red Hat engineering workflows (Jira, release management, Extensions Catalog, lifecycle checks, CI tooling) that are not needed for most RHDH users.

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
