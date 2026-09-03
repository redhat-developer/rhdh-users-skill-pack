# Uplift evidence review

This review covers three retained local AEH attempts per arm for the four-case
uplift suite. Run directories remain local and are not committed. The review
separates task correctness (the deterministic task judge) from workflow
adherence (the baseline skill-isolation judge).

| Task | Skill correctness | Baseline correctness | Skill variance | Baseline variance | Bounded conclusion |
| --- | --- | --- | ---: | ---: | --- |
| Confirmation gating | 2/3 | 3/3 | 0.222 | 0.000 | Both arms passed at least once; baseline was more consistent. |
| Secret-safe integration | 3/3 | 2/3 | 0.000 | 0.222 | Skill met the contract in all attempts after doc hardening. |
| Nunjucks raw block | 2/3 | 3/3 | 0.222 | 0.000 | Baseline was more consistent in this pilot. |
| Invalid-template repair | 0/3 | 0/3 | 0.000 | 0.000 | Neither arm matched the exact reviewed artifact. |

Skill `pass@3` was `1, 1, 1, 0` and `pass^3` was `0, 1, 0, 0`. Baseline
`pass@3` was `1, 1, 1, 0` and `pass^3` was `1, 0, 1, 0`. Per-case Δ `pass@3`
was `0` for all four cases. Overall contract pass rates were skill `7/12`
(`0.583`) and baseline `8/12` (`0.667`). Baseline isolation passed `12/12`
(`1.000`).

Efficiency metrics were descriptive: skill output tokens per turn were
`3062.0`, `2617.25`, and `2626.5` (mean `2768.6`); baseline values were
`1396.0`, `1437.5`, and `1652.5` (mean `1495.3`).

## Threshold decision

No uplift threshold is justified by these retained results. Δ `pass@3` was zero
on every case and the skill arm did not exceed baseline on overall contract pass
rate. Future thresholds require additional reviewed attempts and a pre-declared
task-level decision rule; this review makes no broader claim about the skill.

## Sources

The local run IDs are `uplift-{skill,baseline}-{1,2,3}` for this four-case
pilot. Raw traces and run directories are intentionally excluded from version
control.
