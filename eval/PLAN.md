rhdh-templates eval improvement plan

Status: Approved 2026-09-03
Scope: Local eval harness only — no CI gates, no GEval/DeepEval, routing thresholds deferred.

Goals (priority order)





Regression gate — catch skill changes that break known-good behaviors before merge.



Routing quality — measure whether the right skill activates (informational; no threshold gate yet).



Uplift proof — demonstrate the skill beats a no-skill baseline on representative tasks.

Non-goals





DeepEval RAG metrics (faithfulness, hallucination, relevancy) — wrong problem domain.



GEval / LLM-as-judge rubrics — deferred; revisit only if deterministic judges cannot score a case.



CI integration for AEH/Codex runs — keep evals local until regressions are fixed and workflow is stable.



Product-wide SLOs or commercial quality claims from eval evidence.



MLflow storage (intentionally deferred).



Current state

Four local suites via Agent Eval Harness (AEH) v1.39.2 + Codex (gpt-5.6-luna):







Suite



Cases



Purpose





behavior-local



3



Validate, repair, manual-finding contracts





routing



19



Skill activation (13 positive, 6 negative)





uplift



4



Skill vs baseline on representative authoring tasks





repair-uplift



1



Invalid-template repair (separate narrow contract)

See EVIDENCE.md for the latest bounded results. Key findings (2026-09-02):





Routing: precision 1.0, recall 1.0 on reviewed pilot — thresholds not approved.



Uplift regressions: secret-safe integration (0/3 skill vs 3/3 baseline), confirmation gating (2/3 vs 3/3).



No uplift threshold approved — evidence is mixed or regressive.

Judge contract unit tests live under tests/unit/test_rhdh_templates_* and run via uv run pytest.

Metric vocabulary

Canonical definitions will live in METRICS.md (Phase 1). Glossary terms in CONTEXT.md.







Metric



Use





Contract pass rate



Deterministic judge pass per case





pass@3



≥1 success in 3 attempts (capability)





pass^3



Success on all 3 attempts (reliability)





Δ pass@3



Skill arm minus baseline





Precision / recall



Routing activation only (informational)





Isolation pass rate



Baseline did not read skill instructions

Reporting tiers (local only):







Tier



Metrics



Role





Primary



Contract pass rate, pass@3, pass^3



Skill correctness





Secondary



Δ pass@3, isolation pass rate, command/token guards



Uplift and regression detection





Informational



Routing precision/recall, per-case variance



Routing quality (no gate)



Phase 0 — Fix known regressions

Goal: Make the skill pass its own uplift suite before expanding coverage.







#



Task



Done when





0.1



Fix secret-safe integration (uplift/cases/02-secret-safe-step)



Skill arm ≥ baseline





0.2



Fix confirmation gating (uplift/cases/01-templatize-confirmation)



Skill arm ≥ baseline





0.3



Re-run uplift pilots



./eval/rhdh-templates/uplift/run-local.sh --runs 3





0.4



Update EVIDENCE.md



Card reflects post-fix bounded conclusions





0.5



Re-run routing pilots (informational)



./eval/rhdh-templates/routing/run-local.sh --runs 3; document FN clusters, no threshold gate

Order: 0.1 before 0.2 (secret-safe is a total failure; confirmation is flaky).

Out of scope: CI, GEval, new cases, routing SLO approval.

Phase 1 — Standardize metrics

Goal: Same vocabulary across suites; still local-only.







#



Task



Deliverable





1.1



Create CONTEXT.md



Eval domain glossary (no implementation detail)





1.2



Create METRICS.md



Formulas, tiers, threshold policy, explicit non-goals





1.3



Extend uplift reporting



pass@3, pass^3, Δ pass@3, regression count in summary output





1.4



Add efficiency guardrails (secondary, non-gating)



Command count, loop detection, tokens/turn in summaries





1.5



Align EVIDENCE.md format



Use standardized metric names



Phase 2 — Expand uplift coverage

Goal: Grow toward ~15 uplift cases sourced from real failures. Add 1–2 cases per change set.

Candidate cases (priority order):





11-dry-run — routing positive, no uplift case yet



07-create-location — routing positive, no uplift case yet



05-add-step — common authoring flow



10-list-actions — prior routing false-negative cluster



12-explain-action — prior routing false-negative cluster



09-validate — complements behavior-local

Each new case requires:





input.yaml, annotations.yaml with case_kind



Isolated fixture under cases/<name>/fixture/



Reviewed expected artifact or contract in annotations



Judge coverage in tests/unit/test_rhdh_templates_*

repair-uplift/: keep as a separate suite. Both arms are currently 0/3; fix the skill contract in Phase 0 before merging or expanding.

Phase 3 — CI integration

Deferred. Full AEH/Codex suites remain manual/local.

When revisited, prefer tiered execution:







Tier



Trigger



What runs





L0



Every PR



Judge contract unit tests (uv run pytest tests/unit/test_rhdh_templates_*)





L1



PR touching skill or eval



behavior-local smoke (1 case, Codex)





L2



Nightly / release



Full routing (3 pilots), full uplift comparison



Phase 4 — GEval / LLM rubrics

Skipped. Deterministic judges remain the only grading path. Revisit only if a new case type cannot be scored by artifact + trace checks.

Phase 5 — Live RHDH integration (future, separate)

A distinct suite for Scaffolder dry-run against rhdh-local. Not mixed with skill contract evals.

Borrow operational patterns from rhdh-Lightspeed-Evaluation (pytest harness, trend JSONL, HTML reports). Do not adopt DeepEval faithfulness/hallucination metrics.

Execution timeline







Week



Work





1



Phase 0.1 → 0.2 → 0.3 → 0.4 → 0.5





2



Phase 1.1–1.5





3+



Phase 2 — one or two uplift cases per change set



Decisions log







Date



Decision





2026-09-03



North star: regression gate > routing > uplift proof





2026-09-03



Fix skill regressions before eval infrastructure work





2026-09-03



Adopt pass@3 / pass^3; defer GEval and DeepEval





2026-09-03



No CI for AEH/Codex runs; keep local





2026-09-03



Routing thresholds deferred — informational only





2026-09-03



repair-uplift stays separate from uplift





2026-09-03



No ADR; METRICS.md + CONTEXT.md are sufficient



Related docs





README.md — how to run behavior-local



EVIDENCE.md — latest bounded evidence card



routing/REVIEW.md — routing pilot investigation



uplift/REVIEW.md — uplift evidence review
