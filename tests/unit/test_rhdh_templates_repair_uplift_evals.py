"""Contract tests for the Issue #12 invalid-template repair uplift evaluation."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
EVAL_ROOT = REPO_ROOT / "eval" / "rhdh-templates" / "repair-uplift"


def load_judges():
    spec = importlib.util.spec_from_file_location("repair_uplift_judges", EVAL_ROOT / "judges.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_arms_use_the_same_repair_fixture() -> None:
    skill = yaml.safe_load((EVAL_ROOT / "skill.eval.yaml").read_text(encoding="utf-8"))
    baseline = yaml.safe_load((EVAL_ROOT / "baseline.eval.yaml").read_text(encoding="utf-8"))
    assert skill["dataset"]["path"] == "cases"
    assert skill["dataset"]["path"] == baseline["dataset"]["path"]
    assert skill["dataset"]["workspace"]["files"] == ["fixture"]
    assert skill["dataset"]["workspace"] == baseline["dataset"]["workspace"]


def test_fixture_contains_the_reviewed_repair_defects() -> None:
    fixture = (
        EVAL_ROOT
        / "cases"
        / "invalid-template-repair"
        / "fixture"
        / "invalid-template"
        / "template.yaml"
    ).read_text(encoding="utf-8")
    expected = (
        EVAL_ROOT / "cases" / "invalid-template-repair" / "expected" / "template.yaml"
    ).read_text(encoding="utf-8")
    assert "apiVersion: backstage.io/v1beta2" in fixture
    assert "parameters: []" in fixture
    assert fixture.count("id: create") == 2
    assert "apiVersion: scaffolder.backstage.io/v1beta3" in expected
    assert "componentId:" in expected
    assert "id: finish" in expected


def test_repair_judge_requires_exact_repair_and_clean_validation() -> None:
    judges = load_judges()
    expected = "apiVersion: scaffolder.backstage.io/v1beta3\n"
    outputs = {
        "annotations": {"modified_path": "fixture/invalid-template/template.yaml"},
        "annotation_expected_template_content": expected,
        "files": {"output/template.yaml": expected},
        "modified_files": {"fixture/invalid-template/template.yaml": expected},
        "events": [
            {
                "type": "assistant",
                "tools": [
                    {"id": "validate", "name": "Bash", "input": {"command": "validate.py --json"}}
                ],
            },
            {
                "type": "tool_result",
                "tool_use_id": "validate",
                "content": '{"ok": true, "critical_count": 0}',
                "is_error": False,
            },
        ],
    }
    assert judges.check_repair(outputs)[0]
    outputs["events"] = []
    assert not judges.check_repair(outputs)[0]
    outputs["events"] = [
        {
            "type": "assistant",
            "tools": [
                {"id": "validate", "name": "Bash", "input": {"command": "validate.py --json"}}
            ],
        },
        {
            "type": "tool_result",
            "tool_use_id": "validate",
            "content": '{"ok": false, "critical_count": 1}',
            "is_error": False,
        },
    ]
    assert not judges.check_repair(outputs)[0]


def test_baseline_judge_rejects_skill_consultation() -> None:
    judges = load_judges()
    outputs = {
        "events": [
            {
                "type": "assistant",
                "tools": [
                    {"name": "Read", "input": {"file_path": "skills/rhdh-templates/SKILL.md"}}
                ],
            }
        ]
    }
    assert not judges.check_baseline_is_skill_free(outputs)[0]


def test_local_runner_uses_three_attempts_and_task_specific_comparison() -> None:
    command = (EVAL_ROOT / "run-local.sh").read_text(encoding="utf-8")
    assert "runs=3" in command
    assert "repair-uplift-${arm}-${index}" in command
    assert "compare.py" in command
    assert "comparison_input" in command
    assert "invalid-template repair task" in command
