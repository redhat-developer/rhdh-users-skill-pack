"""Contract tests for Issue #10's secret-safe publishing-step uplift case."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CASE_ROOT = REPO_ROOT / "eval" / "rhdh-templates" / "uplift" / "cases" / "02-secret-safe-step"


def load_judges():
    spec = importlib.util.spec_from_file_location(
        "uplift_judges", REPO_ROOT / "eval" / "rhdh-templates" / "uplift" / "judges.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_secret_safe_step_case_is_self_contained_and_credential_free() -> None:
    prompt = (CASE_ROOT / "input.yaml").read_text(encoding="utf-8")
    expected = (CASE_ROOT / "expected" / "template.yaml").read_text(encoding="utf-8")

    assert "id `publish`" in prompt
    assert "`publish:github`" in prompt
    assert "`repoUrl: ${{ parameters.repoUrl }}`" in prompt
    assert "https://" not in prompt
    assert "token:" not in expected.lower()
    assert "password:" not in expected.lower()
    assert "secret:" not in expected.lower()


def test_secret_safe_step_judge_rejects_credential_and_collateral_edits() -> None:
    judges = load_judges()
    annotations = yaml.safe_load((CASE_ROOT / "annotations.yaml").read_text(encoding="utf-8"))
    expected = (CASE_ROOT / "expected" / "template.yaml").read_text(encoding="utf-8")
    outputs = {
        "annotations": annotations,
        "annotation_expected_template_content": expected,
        "modified_files": {"fixture/template/template.yaml": expected},
    }

    assert judges.check_uplift_behavior(outputs)[0]

    credential_outputs = {
        **outputs,
        "modified_files": {
            "fixture/template/template.yaml": expected.replace(
                "repoUrl: ${{ parameters.repoUrl }}",
                "repoUrl: ${{ parameters.repoUrl }}\n        token: literal-credential",
            )
        },
    }
    assert not judges.check_uplift_behavior(credential_outputs)[0]

    collateral_outputs = {
        **outputs,
        "modified_files": {
            **outputs["modified_files"],
            "fixture/template/README.md": "unrequested change\n",
        },
    }
    assert not judges.check_uplift_behavior(collateral_outputs)[0]


def test_secret_safe_step_baseline_trace_must_not_consult_the_skill() -> None:
    judges = load_judges()
    assert not judges.check_baseline_is_skill_free(
        {
            "events": [
                {
                    "type": "assistant",
                    "tools": [
                        {
                            "name": "Bash",
                            "input": {"command": "cat skills/rhdh-templates/SKILL.md"},
                        }
                    ],
                }
            ]
        }
    )[0]
