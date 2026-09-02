# Routing pilot review

The reviewed routing matrix has 19 cases: 13 positive workflows and 6
near-miss negatives. Activation is measured only from trace evidence showing
that `skills/rhdh-templates/SKILL.md` was read.

The original pre-change pilot (`routing-pilot-01`) scored 0.895 overall
activation-match accuracy, with `10-list-actions` and `12-explain-action` as
false negatives. After making those prompts explicitly local and
skill-scoped, three fresh pilots—`routing-20260902T143643Z-1`,
`routing-20260902T143643Z-2`, and `routing-20260902T143643Z-3`—each scored
1.000 activation-match accuracy, precision, recall, and negative avoidance.
Precision and recall variance were both 0.000000, with no false positives or
false negatives.

## Trace investigation decision

The pre-change misses were workflow-boundary failures: `list-actions` often
selected browser/`rhdh-local` guidance, while `explain-action` selected general
RHDH references. The skill description already named both workflows, so the
minimal effective change was to make the two prompts explicitly local and
skill-scoped. The post-change pilots show the misses are resolved for this
reviewed matrix and model.

The post-change evidence supports a provisional routing threshold of precision
`1.00` and recall `0.95` for this reviewed matrix and pinned model. This is a
pilot guardrail, not a product-wide SLO; any future miss should trigger review.
The local summarizer enforces an explicitly supplied threshold and returns
nonzero when it is violated.

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
