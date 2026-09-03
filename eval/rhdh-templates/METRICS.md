# Local evaluation metrics

## Definitions

For a case with `n` attempts, let `pass_i` be 1 when its deterministic contract
judge passes and 0 otherwise.

- **Contract pass rate** = `sum(pass_i) / n`.
- **pass@3** = 1 when at least one of three attempts passes, otherwise 0.
- **pass^3** = 1 when all three attempts pass, otherwise 0.
- **Δ pass@3** = skill `pass@3` minus baseline `pass@3`, comparing the same case.
- **Precision** = true-positive routing activations divided by all positive
  activations; **recall** = true-positive activations divided by all advertised
  positive cases. Routing metrics are informational only.
- **Isolation pass rate** = baseline attempts whose trace does not read the
  `rhdh-templates` skill root, divided by baseline attempts.

## Reporting tiers

Primary reports contain contract pass rate, pass@3, and pass^3. Secondary reports
contain Δ pass@3, isolation pass rate, and efficiency guardrails. Informational
reports contain routing precision/recall and per-case variance.

Command count, repeated-command loop detection, and tokens per turn are
descriptive guardrails. They do not gate a run and are not cost or latency claims.

## Policy and non-goals

All results are local, bounded, and model-, fixture-, prompt-, and release-specific.
No uplift threshold is currently approved. CI integration, MLflow storage,
DeepEval retrieval metrics, and GEval/LLM-as-judge rubrics are out of scope.
