"""Contract tests for the repair case in the main uplift judge."""

from __future__ import annotations

import importlib.util
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "uplift_judges", Path(__file__).parents[2] / "eval/rhdh-templates/uplift/judges.py"
)
assert SPEC and SPEC.loader
JUDGES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(JUDGES)


def _outputs() -> dict:
    expected = "apiVersion: scaffolder.backstage.io/v1beta3\n"
    return {
        "annotations": {
            "case_kind": "repair",
            "modified_path": "fixture/invalid-template/template.yaml",
        },
        "annotation_expected_template_content": expected,
        "modified_files": {"fixture/invalid-template/template.yaml": expected},
        "files": {"output/template.yaml": expected},
        "events": [
            {
                "type": "assistant",
                "tools": [
                    {
                        "id": "v",
                        "name": "Bash",
                        "input": {
                            "command": "python skills/rhdh-templates/scripts/validate.py fixture/invalid-template/template.yaml --json"
                        },
                    }
                ],
            },
            {
                "type": "tool_result",
                "tool_use_id": "v",
                "content": '{"ok": true, "critical_count": 0}',
                "is_error": False,
            },
        ],
    }


def test_repair_judge_accepts_exact_repair_and_validation() -> None:
    assert JUDGES.check_uplift_behavior(_outputs()) == (
        True,
        "reviewed repair and clean validation were observed",
    )


def test_repair_judge_rejects_missing_validation() -> None:
    outputs = _outputs()
    outputs["events"] = []
    assert not JUDGES.check_uplift_behavior(outputs)[0]
