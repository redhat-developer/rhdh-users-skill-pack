# Routing pilot review

The reviewed routing matrix has 19 cases: 13 positive workflows and 6
near-miss negatives. Activation is measured only from trace evidence showing
that `skills/rhdh-templates/SKILL.md` was read.

The original pre-change pilot (`routing-pilot-01`) scored 0.895 overall
activation-match accuracy, with `10-list-actions` and `12-explain-action` as
false negatives. Those cases remain natural-language routing prompts; the
directly skill-scoped reruns were discarded as non-comparable evidence. The
three retained pilot summaries are reviewed by the summarizer, which reports
per-case outcomes and variance for all 19 cases. Threshold adoption is
deliberately deferred until three fresh pilots using these natural prompts are
available.

## Trace investigation decision

The pre-change misses were workflow-boundary failures: `list-actions` often
selected browser/`rhdh-local` guidance, while `explain-action` selected general
RHDH references. The skill description already names both workflows. The
review therefore keeps the prompts natural and treats the prior direct-invocation
reruns as a separate experiment rather than evidence of routing uplift.

No routing threshold is approved yet. Once three comparable natural-prompt
pilots are reviewed, the maintainer will either approve a threshold or record
an explicit deferral. The local command defaults to the approved values only
when they are set and returns nonzero when a supplied threshold is violated.

Run three distinct pilots and review them with:

```bash
./eval/rhdh-templates/routing/run-local.sh --runs 3
```

After maintainer approval, thresholds can be checked explicitly; a violated
threshold returns a nonzero status:

```bash
python eval/rhdh-templates/routing/summarize.py \
  --summaries eval/runs/rhdh-templates-routing/<run>/summary.yaml \
  --cases-dir eval/rhdh-templates/routing/cases \
  --min-recall 0.80
```

Thresholds must be justified by the three-run precision, recall, variance, and
miss-cluster review. This pilot does not make a broader claim about the skill.
