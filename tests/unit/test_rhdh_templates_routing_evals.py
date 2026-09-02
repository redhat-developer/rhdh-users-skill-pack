"""Contract tests for the Issue #8 routing evaluation."""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTING_ROOT = REPO_ROOT / "eval" / "rhdh-templates" / "routing"
sys.path.insert(0, str(REPO_ROOT))


def test_routing_matrix_covers_workflows_styles_and_near_misses() -> None:
    expected_workflows = {
        "init",
        "templatize",
        "create",
        "add-parameter",
        "add-step",
        "add-skeleton",
        "create-location",
        "fix-gotchas",
        "validate",
        "list-actions",
        "dry-run",
        "explain-action",
        "examples",
    }
    expected_negatives = {
        "upgrade-helper",
        "skill-maker",
        "backend-plugin",
        "kubernetes",
        "yaml-format",
        "rhdh-config",
    }
    cases = ROUTING_ROOT / "cases"
    annotations = {
        case.name: yaml.safe_load((case / "annotations.yaml").read_text(encoding="utf-8"))
        for case in cases.iterdir()
        if case.is_dir()
    }
    positives = {value["category"] for value in annotations.values() if value["should_trigger"]}
    negatives = {
        case.split("-", 1)[1].removesuffix("-negative")
        for case, value in annotations.items()
        if not value["should_trigger"]
    }
    styles = {
        value["style"]
        for value in annotations.values()
        if value["should_trigger"] and "style" in value
    }

    assert positives == expected_workflows
    assert negatives == expected_negatives
    assert styles == {"explicit", "implicit", "terse", "ambiguous"}


def test_routing_judge_uses_trace_evidence_not_agent_claims() -> None:
    judges = importlib.import_module("eval.rhdh-templates.routing.judges")
    assert judges.check_routing(
        {
            "annotations": {"should_trigger": False},
            "conversation": "I used rhdh-templates.",
            "events": [],
        }
    )[0]
    assert not judges.check_routing({"annotations": {"should_trigger": True}, "events": []})[0]


def test_summary_reports_variance_and_named_misses(tmp_path: Path) -> None:
    cases = tmp_path / "cases"
    for name, should_trigger in {
        "positive-hit": True,
        "positive-miss": True,
        "negative-hit": False,
        "negative-miss": False,
    }.items():
        (cases / name).mkdir(parents=True)
        (cases / name / "annotations.yaml").write_text(
            yaml.safe_dump({"should_trigger": should_trigger}), encoding="utf-8"
        )
    summary = tmp_path / "summary.yaml"
    summary.write_text(
        yaml.safe_dump(
            {
                "per_case": {
                    "positive-hit": {"activation_match": {"value": True}},
                    "positive-miss": {"activation_match": {"value": False}},
                    "negative-hit": {"activation_match": {"value": True}},
                    "negative-miss": {"activation_match": {"value": False}},
                }
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            ROUTING_ROOT / "summarize.py",
            "--summaries",
            summary,
            "--cases-dir",
            cases,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "precision_mean: 0.500" in result.stdout
    assert "recall_mean: 0.500" in result.stdout
    assert "precision_variance: 0.000000" in result.stdout
    assert "false_positives: negative-miss" in result.stdout
    assert "false_negatives: positive-miss" in result.stdout


def test_summary_fails_when_approved_threshold_is_violated(tmp_path: Path) -> None:
    cases = tmp_path / "cases"
    (cases / "positive").mkdir(parents=True)
    (cases / "positive" / "annotations.yaml").write_text(
        yaml.safe_dump({"should_trigger": True}), encoding="utf-8"
    )
    summary = tmp_path / "summary.yaml"
    summary.write_text(
        yaml.safe_dump({"per_case": {"positive": {"activation_match": {"value": False}}}}),
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            sys.executable,
            ROUTING_ROOT / "summarize.py",
            "--summary",
            summary,
            "--cases-dir",
            cases,
            "--min-recall",
            "0.5",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "threshold_failed" in result.stdout


def test_local_command_defaults_to_three_runs_and_has_candidate_guidance() -> None:
    command = (ROUTING_ROOT / "run-local.sh").read_text(encoding="utf-8")
    candidates = (ROUTING_ROOT / "candidates" / "README.md").read_text(encoding="utf-8")

    assert "runs=3" in command
    assert "gpt-5.6-luna" in command
    assert "review" in candidates.lower()
    assert "do not overwrite" in candidates.lower()
