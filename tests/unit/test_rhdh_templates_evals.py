"""Contract tests for the issue #6 rhdh-templates eval assets."""

from __future__ import annotations

import importlib
import os
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
EVAL_ROOT = REPO_ROOT / "eval" / "rhdh-templates"
sys.path.insert(0, str(REPO_ROOT))


def test_local_runner_help_is_available_without_starting_aeh() -> None:
    result = subprocess.run(
        [EVAL_ROOT / "run-local.sh", "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "behavior-local" in result.stdout
    assert "routing" not in result.stdout
    assert "uplift" not in result.stdout


def test_local_runner_isolates_codex_home_and_removes_the_copy(
    tmp_path: Path,
) -> None:
    source_home = tmp_path / "source-codex-home"
    source_home.mkdir()
    (source_home / "auth.json").write_text('{"token": "test-only"}\n')
    (source_home / "config.toml").write_text('model = "test"\n')

    aeh_checkout = tmp_path / "aeh"
    execute = aeh_checkout / "skills" / "eval-run" / "scripts" / "execute.py"
    execute.parent.mkdir(parents=True)
    execute.touch()

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_uv = fake_bin / "uv"
    fake_uv.write_text(
        "#!/usr/bin/env bash\n"
        "printf '%s\\n' \"${CODEX_HOME}\"\n"
        "test -f \"${CODEX_HOME}/auth.json\"\n"
    )
    fake_uv.chmod(0o755)

    env = os.environ.copy()
    env.update(
        {
            "AEH_CHECKOUT": str(aeh_checkout),
            "CODEX_HOME": str(source_home),
            "PATH": f"{fake_bin}:{env['PATH']}",
        }
    )
    result = subprocess.run(
        [EVAL_ROOT / "run-local.sh", "behavior-local"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    isolated_home = Path(result.stdout.strip())
    assert isolated_home != source_home
    assert not isolated_home.exists()
    assert (source_home / "auth.json").read_text() == '{"token": "test-only"}\n'


def test_python_runner_exposes_a_stable_local_interface() -> None:
    result = subprocess.run(
        [sys.executable, EVAL_ROOT / "run_suite.py", "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "--aeh-dir" in result.stdout
    assert "--config" in result.stdout
    assert "--cases" in result.stdout
    assert "--no-llm-judges" in result.stdout


def _valid_outputs() -> dict:
    template = "apiVersion: scaffolder.backstage.io/v1beta3\nkind: Template\n"
    return {
        "annotations": {"case_kind": "validate-success"},
        "annotation_expected_template_content": template,
        "files": {"output/template.yaml": template},
        "modified_files": {},
        "events": [
            {
                "type": "assistant",
                "tools": [
                    {
                        "id": "validate-1",
                        "name": "Bash",
                        "input": {
                            "command": (
                                "python skills/rhdh-templates/scripts/validate.py "
                                "--path fixture/template --json"
                            )
                        },
                    }
                ],
            },
            {
                "type": "tool_result",
                "tool_use_id": "validate-1",
                "content": (
                    "shell initialization warning\n"
                    '{"ok": true, "critical_count": 0}\n'
                ),
                "is_error": False,
            },
        ],
    }


def test_local_judge_accepts_observed_clean_validation() -> None:
    judges = importlib.import_module("eval.rhdh-templates.behavior-local.judges")

    passed, rationale = judges.check_local_behavior(_valid_outputs())

    assert passed is True, rationale


def test_local_judge_rejects_agent_claim_without_trace_evidence() -> None:
    judges = importlib.import_module("eval.rhdh-templates.behavior-local.judges")
    outputs = _valid_outputs()
    outputs["events"] = []
    outputs["conversation"] = "Validation passed with zero critical findings."

    passed, rationale = judges.check_local_behavior(outputs)

    assert passed is False
    assert "validate.py" in rationale


def test_local_judge_rejects_modified_fixture() -> None:
    judges = importlib.import_module("eval.rhdh-templates.behavior-local.judges")
    outputs = _valid_outputs()
    outputs["modified_files"] = {"fixture/template.yaml": "changed\n"}

    passed, rationale = judges.check_local_behavior(outputs)

    assert passed is False
    assert "modified" in rationale


def test_eval_config_and_case_are_portable_and_complete() -> None:
    configs = list(EVAL_ROOT.glob("**/eval.yaml"))

    assert configs == [EVAL_ROOT / "behavior-local" / "eval.yaml"]
    config_path = configs[0]
    text = config_path.read_text(encoding="utf-8")
    config = yaml.safe_load(text)
    cases_dir = config_path.parent / config["dataset"]["path"]
    cases = list(cases_dir.iterdir())

    assert "/home/" not in text
    assert config["models"]["skill"] == "gpt-5.6-luna"
    assert config["dataset"]["workspace"]["files"] == ["fixture"]
    assert cases == [cases_dir / "validate-success"]
    assert (cases[0] / "input.yaml").is_file()
    assert (cases[0] / "annotations.yaml").is_file()
    assert (cases[0] / "fixture").is_dir()


def test_reviewed_template_matches_the_fixture() -> None:
    case = EVAL_ROOT / "behavior-local" / "cases" / "validate-success"

    assert (case / "expected" / "template.yaml").read_text() == (
        case / "fixture" / "minimal-template" / "template.yaml"
    ).read_text()
