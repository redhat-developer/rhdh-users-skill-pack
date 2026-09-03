# Uplift evidence review

This review covers three retained local AEH attempts for the four-case skill
arm. The expanded baseline comparison was not completed. Run directories remain
local and are not committed.
The review separates task correctness (the deterministic task judge) from
workflow adherence (the baseline skill-isolation judge).

| Task | Skill correctness | Baseline correctness | Skill variance | Baseline variance | Bounded conclusion |
| --- | --- | --- | ---: | ---: | --- |
| Confirmation gating | 3/3 | not run | 0.000 | — | Skill passed the reviewed contract in this pilot. |
| Secret-safe integration | 1/3 | not run | 0.222 | — | Skill was inconsistent in this pilot. |
| Nunjucks raw block | 2/3 | not run | 0.222 | — | Skill was mostly successful in this pilot. |
| Invalid-template repair | 0/3 | not run | 0.000 | — | Skill repaired structure but did not match the exact reviewed artifact. |

Baseline results for the expanded four-case suite are unavailable because that
pilot was stopped after the skill arm. Efficiency metrics from the completed
skill attempts were output tokens per turn of 3,005.2, 2,869.0, and 2,703.4;
these are descriptive only.

## Threshold decision

No uplift threshold is justified by these retained results. The evidence is
mixed or regressive for three tasks and shows no effect for the fourth. Future
thresholds require additional reviewed attempts and a pre-declared task-level
decision rule; this review makes no broader claim about the skill.

## Sources

The local run IDs are `uplift-{skill,baseline}-{1,2,3}` for the five-task suite.
Raw traces and run directories are intentionally excluded from version control.
