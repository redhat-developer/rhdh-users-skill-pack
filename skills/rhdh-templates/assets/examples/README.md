# RHDH Templates Examples

Bundled worked examples for local learning and validation. Each passes `validate.py` with zero critical findings.

For the full curated catalog of upstream reference templates (official library and AI quickstarts), run:

```bash
python skills/rhdh-templates/scripts/list_examples.py --recommended --json
```

See [../references/example-catalog.md](../references/example-catalog.md) for the category guide and common-demand context.

| Example | Stack | Notes |
|---------|-------|-------|
| [minimal-template](./minimal-template/) | Generic | Starter scaffold from `init`. Single parameter form. |
| [nodejs-backend](./nodejs-backend/) | Node.js | `EntityPicker`, `RepoUrlPicker`, publish and register, GitHub Actions `{% raw %}` |
| [java-springboot](./java-springboot/) | Java / Spring Boot | Maven `pom.xml`, `Application.java`, multi-section forms |

These bundled examples correspond to upstream references in [red-hat-developer-hub-software-templates](https://github.com/redhat-developer/red-hat-developer-hub-software-templates): `nodejs-backend` maps to `templates/github/nodejs-backend`, and `java-springboot` maps to `templates/github/spring-boot-backend`.

Validate any example locally:

```bash
python skills/rhdh-templates/scripts/validate.py \
  --path skills/rhdh-templates/assets/examples/nodejs-backend \
  --repo --lint-skeleton --json
```

Replace `nodejs-backend` with `java-springboot` or `minimal-template` as needed.
