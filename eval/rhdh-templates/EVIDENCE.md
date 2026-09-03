# `rhdh-templates` behavioral-eval evidence card

**Run date:** 2026-09-03  
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
- Contract pass results for the completed skill arm were respectively: `3/3`,
  `1/3`, `2/3`, `0/3`. Therefore skill `pass@3` was `1, 1, 1, 0` and skill
  `pass^3` was `1, 0, 0, 0`. The expanded baseline comparison was
  stopped before completion, so no new baseline delta is claimed.
- The overall skill-arm contract pass rate was `6/12` (`0.50`).
- Bounded conclusions: confirmation gating passed in this pilot; secret-safe and
  Nunjucks behavior remained variable; diagnose-and-repair and the integrated
  invalid-template case did not match its exact reviewed artifact. A future
  repair contract should decide whether equivalent valid repairs are acceptable
  instead of requiring one exact serialization.
- No uplift threshold is approved; the evidence is mixed or regressive.
- Reproduce the local comparison with:

  ```bash
  ./eval/rhdh-templates/uplift/run-local.sh --runs 3
  ```

## Limitations and scope

- Results are model-, release-, prompt-, fixture-, and date-specific.
- Local AEH artifacts are reproducible sources; this card is an aggregate
  summary, not a substitute for raw traces during investigation.
- Efficiency observations were descriptive: skill output tokens/turn were
  `2405.0`, `2373.5`, `2605.5`; baseline values were `1406.8`, `1380.0`,
  `1432.2`. Command count and loop detection remain secondary guardrails; no cost
  or latency claim is made.
- No commercial support entitlement, product-wide quality guarantee, or broad
  uplift claim follows from these evaluations.
- MLflow storage is intentionally deferred; no MLflow database is required.
