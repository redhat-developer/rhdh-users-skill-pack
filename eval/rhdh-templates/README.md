# `rhdh-templates` local validation eval

This eval measures one `rhdh-templates` behavior using observable trace and
filesystem evidence: validating an already-valid Software Template without
changing its fixture. It uses Agent Eval Harness (AEH) `v1.39.2` and pins
`gpt-5.6-luna` as the reference model.

The eval runs locally. It does not require MLflow or a running RHDH instance.

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

The deterministic judge requires all of the following:

- `output/template.yaml` exactly matches the reviewed expected artifact;
- no fixture file was modified; and
- the normalized tool trace contains a successful `validate.py` result whose
  JSON reports `ok: true` and zero critical findings.

Agent-written summaries are diagnostic only and cannot make a failing case
pass. The prompt, fixture, annotations, and reviewed expected artifact are
self-contained under `behavior-local/cases/validate-success/`.
