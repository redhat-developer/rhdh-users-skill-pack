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

- Four representative tasks with three retained attempts per arm:
  confirmation gating (`01-templatize-confirmation`), secret-safe integration
  (`02-secret-safe-step`), Nunjucks raw block repair (`03-nunjucks-raw`), and
  invalid-template repair (`05-invalid-template-repair`).
- Contract pass results, in case order, were skill `2/3`, `3/3`, `2/3`, `0/3`
  and baseline `3/3`, `2/3`, `3/3`, `0/3`. Skill `pass@3` was `1, 1, 1, 0`
  and `pass^3` was `0, 1, 0, 0`; baseline `pass@3` was `1, 1, 1, 0` and
  `pass^3` was `1, 0, 1, 0`.
- The corresponding per-case Δ `pass@3` values were `0, 0, 0, 0`. Overall
  contract pass rates were skill `7/12` (`0.583`) and baseline `8/12`
  (`0.667`). Baseline isolation passed `12/12` (`1.000`).
- Bounded conclusions: confirmation gating was `2/3` for both arms; secret-safe
  integration was `3/3` for skill and `2/3` for baseline; Nunjucks repair was
  `2/3` for skill versus `3/3` for baseline; invalid-template repair was `0/3`
  for both. The exact repair contract remains stricter than structural validity.
- No uplift threshold is approved; the evidence is mixed or regressive.
- Reproduce locally with:

  ```bash
  ./eval/rhdh-templates/uplift/run-local.sh --runs 3
  ```

## Limitations and scope

- Results are model-, release-, prompt-, fixture-, and date-specific.
- Local AEH artifacts are reproducible sources; this card is an aggregate
  summary, not a substitute for raw traces during investigation.
- Efficiency observations were descriptive: skill output tokens/turn were
  `3062.0`, `2617.25`, `2626.5` (mean `2768.6`); baseline values were `1396.0`,
  `1437.5`, `1652.5` (mean `1495.3`). Command count and loop detection remain
  secondary guardrails; no cost or latency claim is made.
- No commercial support entitlement, product-wide quality guarantee, or broad
  uplift claim follows from these evaluations.
- MLflow storage is intentionally deferred; no MLflow database is required.
