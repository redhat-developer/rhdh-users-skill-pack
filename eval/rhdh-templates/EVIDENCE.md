# `rhdh-templates` behavioral-eval evidence card

**Run date:** 2026-09-02  
**Model:** `gpt-5.6-luna`  
**AEH release:** `v1.39.2`  
**Storage:** local AEH run directories only; raw traces are intentionally not committed.

## Evaluated suites

### Routing

- 19 reviewed cases: 13 advertised workflows and 6 near-miss negatives.
- Three pilot runs were reviewed for activation precision, recall, negative
  avoidance, case-level variance, and named false-positive/false-negative
  clusters.
- The reviewed pilot recorded precision `1.000`, recall `1.000`, and zero
  observed false positives or false negatives. The documented pilot guardrail
  is precision `1.00` / recall `0.95`; this is not a product-wide SLO.
- Reproduce locally with:

  ```bash
  ./eval/rhdh-templates/routing/run-local.sh --runs 3
  ```

### Uplift

- Four representative tasks, with three retained attempts for each skill and
  baseline arm: confirmation gating, secret-safe integration, Nunjucks raw
  block repair, and invalid-template repair.
- Correctness results were respectively: skill `2/3`, `0/3`, `3/3`, `0/3`;
  baseline `3/3`, `3/3`, `3/3`, `0/3`.
- Bounded conclusions: regression for confirmation gating and secret-safe
  integration, no effect for Nunjucks repair, and no effect for invalid-template
  repair because neither arm met the exact contract.
- No uplift threshold is approved; the evidence is mixed or regressive.
- Reproduce the local comparison with:

  ```bash
  ./eval/rhdh-templates/uplift/run-local.sh --runs 3
  ./eval/rhdh-templates/repair-uplift/run-local.sh --runs 3
  ```

## Limitations and scope

- Results are model-, release-, prompt-, fixture-, and date-specific.
- Local AEH artifacts are reproducible sources; this card is an aggregate
  summary, not a substitute for raw traces during investigation.
- Efficiency observations are descriptive token/cache metrics only; no cost or
  latency claim is made.
- No commercial support entitlement, product-wide quality guarantee, or broad
  uplift claim follows from these evaluations.
- MLflow storage is intentionally deferred; no MLflow database is required.
