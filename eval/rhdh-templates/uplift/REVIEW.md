# Uplift evidence review

This review covers three retained local AEH attempts per arm for the four
representative tasks. Run directories remain local and are not committed.
The review separates task correctness (the deterministic task judge) from
workflow adherence (the baseline skill-isolation judge).

| Task | Skill correctness | Baseline correctness | Skill variance | Baseline variance | Bounded conclusion |
| --- | --- | --- | ---: | ---: | --- |
| Confirmation gating | 2/3 | 3/3 | 0.222 | 0.000 | Regression in this case; baseline was more consistent. |
| Secret-safe integration | 0/3 | 3/3 | 0.000 | 0.000 | Regression in this case; baseline completed the exact edit. |
| Nunjucks raw block | 3/3 | 3/3 | 0.000 | 0.000 | No effect in this case. |
| Invalid-template repair | 0/3 | 0/3 | 0.000 | 0.000 | No effect; neither arm satisfied the exact repair contract. |

All nine baseline attempts passed skill-isolation checks. Available efficiency
metrics were output tokens per turn and cache-hit rate. Mean output tokens per
turn were 2,714.5 for the skill arm and 1,545.0 for the baseline arm across
the four-task uplift suite; these are descriptive only and are not treated as
an efficiency claim because the attempts were not paired by latency or cost.

## Threshold decision

No uplift threshold is justified by these retained results. The evidence is
mixed or regressive for three tasks and shows no effect for the fourth. Future
thresholds require additional reviewed attempts and a pre-declared task-level
decision rule; this review makes no broader claim about the skill.

## Sources

The local run IDs are `uplift-{skill,baseline}-{1,2,3}` for the five-task suite.
Raw traces and run directories are intentionally excluded from version control.
