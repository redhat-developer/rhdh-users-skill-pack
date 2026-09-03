# `rhdh-templates` local validation eval

This eval measures three `rhdh-templates` behaviors using observable trace and
filesystem evidence: validating a clean template, applying one reviewed repair,
and reporting one manual-only secret-field finding. It uses Agent Eval Harness
(AEH) `v1.39.2` and pins `gpt-5.6-luna` as the reference model.

The eval runs locally. It does not require MLflow or a running RHDH instance.
Metric definitions and reporting tiers are documented in [METRICS.md](./METRICS.md);
the glossary is in [CONTEXT.md](./CONTEXT.md).

## Prerequisites

- `git`
- `uv`
- a working, authenticated `codex` command

Run the selector from the repository root:

```bash
./eval/rhdh-templates/run-local.sh behavior-local
```

The first run clones AEH `v1.39.2` under `/tmp`. Set `AEH_CHECKOUT` to reuse an
existing checkout instead. The wrapper makes a private temporary copy of the
current Codex authentication and configuration files for the evaluated agent,
then removes it when the run ends. Set `AEH_CODEX_HOME` to an existing writable
directory to opt out of that temporary isolation.

To run the case with a named output directory and explicitly disable model-based
judges (the configured judge is deterministic):

```bash
./eval/rhdh-templates/run-local.sh behavior-local \
  --cases validate-success \
  --run-id behavior-smoke-01 \
  --no-llm-judges
```

Raw output is written beneath `eval/runs/<eval-name>/<run-id>/` and is ignored
by Git. The command prints the exact directory. A nonzero exit status means an
AEH stage or the configured threshold failed; inspect `summary.yaml`,
`report.html`, and the per-case logs there.

## Evidence and judging

The deterministic judge requires reviewed output, an exact allowed change set,
and structured results observed from the bundled commands:

- the validation case copies the reviewed artifact, leaves its fixture unchanged,
  and observes `validate.py --json` with zero critical findings;
- the repair case changes only the reviewed file to the reviewed content, then
  observes applied `fix_gotchas.py --json` and clean revalidation; and
- the manual-finding case leaves its fixture unchanged and observes the reviewed
  finding from `fix_gotchas.py --json` without `--apply`.

Agent-written summaries are diagnostic only and cannot make a failing case
pass. The prompt, fixture, annotations, and reviewed expected artifact are
self-contained under `behavior-local/cases/`.
