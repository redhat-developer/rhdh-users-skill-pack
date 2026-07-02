# Contributing to RHDH Users Skill Pack

Thank you for helping improve Agent Skills for Red Hat Developer Hub users.

This project is released under the Apache-2.0 License.

## What belongs in this repository

This pack is for skills that help people **use and extend RHDH**. Skills aimed at Red Hat internal engineering (Jira automation, release trains, internal CI) belong in [`redhat-developer/rhdh-skill`](https://github.com/redhat-developer/rhdh-skill), not here.

The pack currently ships `skill-maker` for authoring new skills. Additional user-facing skills are welcome as focused contributions.

## Get started

```bash
git clone https://github.com/redhat-developer/rhdh-users-skill-pack.git
cd rhdh-users-skill-pack
uv sync --extra dev
git config core.hooksPath .githooks
```

The `core.hooksPath` setting enables the checked-in pre-commit hook (lint + tests). No separate `pre-commit install` is required.

### Run tests

```bash
uv run pytest
```

### Lint

```bash
uv run ruff check .
uv run ruff format --check .
```

Both run automatically via the pre-commit hook when `pre-commit` is installed.

## Adding or changing a skill

1. Follow the [Agent Skills specification](https://agentskills.io/specification).
2. Place the skill at `skills/<name>/` where `<name>` matches the `name` field in `SKILL.md` front matter.
3. Keep `SKILL.md` focused; put detailed guidance in `references/`, scripts in `scripts/`, and examples in `assets/`.
4. Prefer **stdlib-only Python** for bundled scripts unless a dependency is clearly justified.
5. Update the skills table in [README.md](./README.md) when adding a new skill.
6. Add or update tests under `tests/` when changing scripts or validation logic.

Use the bundled `skill-maker` skill to interview, draft, and audit new skills before opening a PR.

## Submitting a pull request

1. Fork the repository and create a branch from `main`.
2. Make focused commits — one concern per commit when practical.
3. Ensure `uv run pytest` and `uv run ruff check .` pass.
4. Open a pull request with:
   - What user problem the change solves
   - How you tested it
   - Any new prerequisites users should know about

## Reporting issues

Use [GitHub Issues](https://github.com/redhat-developer/rhdh-users-skill-pack/issues) for bugs, missing workflows, and skill ideas. Include your RHDH version, agent tool, and the prompt or task that did not work as expected.

## Code of conduct

Be respectful and constructive. This is a public Red Hat Developer project intended for a broad community of RHDH users.
