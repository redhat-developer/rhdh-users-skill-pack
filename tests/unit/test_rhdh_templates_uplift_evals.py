"""Contract tests for the Issue #9 paired uplift evaluation."""

from __future__ import annotations

import importlib
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
UPLIFT_ROOT = REPO_ROOT / "eval" / "rhdh-templates" / "uplift"


def test_skill_and_baseline_use_the_same_reviewed_cases_and_fixture() -> None:
    skill = yaml.safe_load((UPLIFT_ROOT / "skill.eval.yaml").read_text(encoding="utf-8"))
    baseline = yaml.safe_load((UPLIFT_ROOT / "baseline.eval.yaml").read_text(encoding="utf-8"))
    assert skill["dataset"]["path"] == baseline["dataset"]["path"] == "cases"
    assert skill["dataset"]["workspace"] == baseline["dataset"]["workspace"]
    assert skill["dataset"]["workspace"]["files"] == ["fixture"]
    assert skill["mlflow"]["experiment"] == "rhdh-templates-uplift"
    assert baseline["mlflow"]["experiment"] == "rhdh-templates-uplift"


def test_uplift_judge_enforces_confirmation_and_exact_modifications() -> None:
    judges = importlib.import_module("eval.rhdh-templates.uplift.judges")
    assert judges.check_uplift_behavior(
        {
            "annotations": {
                "case_kind": "confirmation-gate",
                "required_proposal_markers": ["owner"],
            },
            "files": {"output/proposal.md": "owner"},
            "modified_files": {},
        }
    )[0]
    assert not judges.check_uplift_behavior(
        {
            "annotations": {
                "case_kind": "confirmation-gate",
                "required_proposal_markers": ["owner"],
            },
            "files": {"output/proposal.md": "owner"},
            "modified_files": {"fixture/service/package.json": "changed"},
        }
    )[0]


def test_baseline_judge_rejects_skill_consultation() -> None:
    judges = importlib.import_module("eval.rhdh-templates.uplift.judges")
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


def test_uplift_runner_requires_mlflow_and_three_attempts_by_default() -> None:
    command = (UPLIFT_ROOT / "run-local.sh").read_text(encoding="utf-8")
    assert "runs=3" in command
    assert "MLFLOW_TRACKING_URI" in command
    assert "compare.py" in command
