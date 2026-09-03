# Evaluation context

This directory contains local evaluations for the `rhdh-templates` Agent Skill.
Cases grade observable workspace state and tool traces, not an agent's prose
claim about what it did.

An **arm** is one evaluation configuration, such as the skill-enabled arm or the
skill-free baseline. An **attempt** is one run of one arm against the same case.
The **contract** is the deterministic judge for a case. A **pilot** is a bounded
set of repeated attempts; it is evidence for this repository, not a product SLO.

The primary question is whether the skill preserves reviewed behavior. Uplift and
routing measurements are secondary and informational until an explicit threshold
is approved. The baseline is useful only when its trace is isolated from the
skill instructions.
