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

- Five representative tasks, with three retained attempts for each skill and
  baseline arm: confirmation gating, secret-safe integration, Nunjucks raw
  block repair, diagnose-and-repair, and invalid-template repair.
- The newly integrated `05-invalid-template-repair` case passed the skill arm in
  all three attempts (`pass@3=1`, `pass^3=1`). The expanded baseline comparison
  was not completed in this pilot, so no new baseline delta is claimed for this
  case.
- Contract pass results were respectively: skill `1/3`, `3/3`, `3/3`, `0/3`;
  baseline `3/3`, `3/3`, `3/3`, `0/3`. Thus `pass@3` was skill `1, 1, 1, 0`
  and baseline `1, 1, 1, 0`; `pass^3` was skill `0, 1, 1, 0` and baseline
  `1, 1, 1, 0`.
- The corresponding per-case Δ `pass@3` values were `0, 0, 0, 0`.
- The overall contract pass rates were skill `6/12` (`0.50`) and baseline
  `9/12` (`0.75`). Baseline isolation passed `11/12` (`0.917`).
- Bounded conclusions: secret-safe integration now meets the contract in all
  three skill attempts; confirmation gating remains flaky because two proposals
  omitted the reviewed `serviceName` mapping; Nunjucks repair remains `3/3` for
  both arms; invalid-template repair remains `0/3` for both arms.
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
- Efficiency observations were descriptive: skill output tokens/turn were
  `2405.0`, `2373.5`, `2605.5`; baseline values were `1406.8`, `1380.0`,
  `1432.2`. Command count and loop detection remain secondary guardrails; no cost
  or latency claim is made.
- No commercial support entitlement, product-wide quality guarantee, or broad
  uplift claim follows from these evaluations.
- MLflow storage is intentionally deferred; no MLflow database is required.
