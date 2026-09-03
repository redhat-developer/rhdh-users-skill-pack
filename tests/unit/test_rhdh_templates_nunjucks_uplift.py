"""Contract tests for the Issue #11 Nunjucks raw-block uplift case."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CASE_ROOT = REPO_ROOT / "eval" / "rhdh-templates" / "uplift" / "cases" / "03-nunjucks-raw"
UPLIFT_ROOT = CASE_ROOT.parents[1]


def load_judges():
    spec = importlib.util.spec_from_file_location("uplift_judges", UPLIFT_ROOT / "judges.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def case_outputs(*, modified_files: dict[str, str] | None = None) -> dict[str, object]:
    annotations = yaml.safe_load((CASE_ROOT / "annotations.yaml").read_text(encoding="utf-8"))
    expected_readme = (CASE_ROOT / annotations["expected_readme"]).read_text(encoding="utf-8")
    expected_workflow = (CASE_ROOT / annotations["expected_workflow"]).read_text(encoding="utf-8")
    return {
        "annotations": annotations,
        "annotation_expected_readme_content": expected_readme,
        "annotation_expected_workflow_content": expected_workflow,
        "modified_files": modified_files
        or {
            "fixture/raw-template/skeleton/README.md": expected_readme,
            "fixture/raw-template/skeleton/.github/workflows/ci.yaml": expected_workflow,
        },
    }


def test_nunjucks_case_is_self_contained_and_requires_both_reviewed_repairs() -> None:
    prompt = yaml.safe_load((CASE_ROOT / "input.yaml").read_text(encoding="utf-8"))["prompt"]
    readme = (CASE_ROOT / "fixture" / "raw-template" / "skeleton" / "README.md").read_text(
        encoding="utf-8"
    )
    workflow = (
        CASE_ROOT / "fixture" / "raw-template" / "skeleton" / ".github" / "workflows" / "ci.yaml"
    ).read_text(encoding="utf-8")
    expected_readme = (CASE_ROOT / "expected" / "README.md").read_text(encoding="utf-8")
    expected_workflow = (CASE_ROOT / "expected" / "ci.yaml").read_text(encoding="utf-8")

    assert "fixture/raw-template/skeleton" in prompt
    assert "{{ values.componentId }}" in readme
    assert "${{ github.ref }}" in workflow
    assert expected_readme == "# ${{ values.componentId }}\n"
    assert "{% raw %}${{ github.ref }}{% endraw %}" in expected_workflow


def test_nunjucks_judge_rejects_missing_or_extra_changes() -> None:
    judges = load_judges()
    correct = case_outputs()
    assert judges.check_uplift_behavior(correct)[0]

    missing_workflow = case_outputs(
        modified_files={
            "fixture/raw-template/skeleton/README.md": correct["annotation_expected_readme_content"]
        }
    )
    assert not judges.check_uplift_behavior(missing_workflow)[0]

    unexpected_template_change = case_outputs()
    unexpected_template_change["modified_files"]["fixture/raw-template/template.yaml"] = "changed\n"
    assert not judges.check_uplift_behavior(unexpected_template_change)[0]


def test_nunjucks_uplift_runs_three_local_attempts_per_arm_with_case_comparison() -> None:
    command = (UPLIFT_ROOT / "run-local.sh").read_text(encoding="utf-8")

    assert "runs=3" in command
    assert "for arm in skill baseline; do" in command
    assert 'for index in $(seq 1 "${runs}"); do' in command
    assert 'prefix="uplift-$(date -u +%Y%m%dT%H%M%SZ)"' in command
    assert 'run_id="${prefix}-${arm}-${index}"' in command
    assert "${prefix}-skill-${index}" in command
    assert "${prefix}-baseline-${index}" in command
    assert "compare.py" in command
    assert "Observed comparison only" in command
