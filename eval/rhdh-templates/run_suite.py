#!/usr/bin/env python3
"""Run one local suite through AEH's supported pipeline scripts."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

EVAL_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = EVAL_ROOT / "behavior-local" / "eval.yaml"
EXPECTED_FIXTURES = {
    "validate-success": Path("cases")
    / "validate-success"
    / "fixture"
    / "minimal-template"
    / "template.yaml",
    "fix-gotchas-repair": Path("cases")
    / "fix-gotchas-repair"
    / "fixture"
    / "fixable-template"
    / "template.yaml",
    "manual-secret-finding": Path("cases")
    / "manual-secret-finding"
    / "fixture"
    / "manual-issue"
    / "template.yaml",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aeh-dir", type=Path, required=True)
    parser.add_argument("--run-id")
    parser.add_argument("--cases", nargs="+")
    parser.add_argument("--no-llm-judges", action="store_true")
    return parser.parse_args()


def run_step(label: str, script: Path, arguments: list[str], *, capture: bool = False) -> str:
    print(f"\n==> {label}", file=sys.stderr, flush=True)
    result = subprocess.run(
        [sys.executable, str(script), *arguments],
        cwd=Path.cwd(),
        capture_output=capture,
        text=True,
        check=False,
    )
    if capture and result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    return result.stdout if capture else ""


def fixtures_are_provisioned(workspace: Path, case_ids: list[str] | None) -> bool:
    """Return whether AEH copied each selected reviewed fixture."""
    selected_cases = case_ids or list(EXPECTED_FIXTURES)
    return all(
        case_id in EXPECTED_FIXTURES and (workspace / EXPECTED_FIXTURES[case_id]).is_file()
        for case_id in selected_cases
    )


def main() -> int:
    args = parse_args()
    aeh_dir = args.aeh_dir.resolve()
    config_path = CONFIG_PATH
    scripts = aeh_dir / "skills" / "eval-run" / "scripts"
    required_scripts = [
        scripts / name
        for name in (
            "preflight.py",
            "workspace.py",
            "execute.py",
            "collect.py",
            "score.py",
            "report.py",
        )
    ]
    missing = [str(path) for path in required_scripts if not path.is_file()]
    if missing:
        print(f"AEH checkout is missing pipeline scripts: {missing}", file=sys.stderr)
        return 2
    if not config_path.is_file():
        print(f"Eval config not found: {config_path}", file=sys.stderr)
        return 2

    sys.path.insert(0, str(aeh_dir))
    from agent_eval.config import EvalConfig  # type: ignore[import-not-found]

    config = EvalConfig.from_yaml(config_path)
    model = config.models.skill
    if not model:
        print("No reference model configured in eval.yaml", file=sys.stderr)
        return 2
    run_id = args.run_id or (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + model.replace("/", "-")
    )
    if not re.fullmatch(r"[A-Za-z0-9._-]+", run_id):
        print(f"Invalid run id: {run_id!r}", file=sys.stderr)
        return 2

    runs_base = Path("eval/runs")
    output_dir = runs_base / config.eval_name() / run_id
    print(f"Suite: {config.name}", file=sys.stderr)
    print(f"Model: {model}", file=sys.stderr)
    print(f"Run: {output_dir}", file=sys.stderr)

    run_step(
        "preflight",
        scripts / "preflight.py",
        ["--config", str(config_path), "--run-id", run_id],
    )
    workspace_args = ["--config", str(config_path), "--run-id", run_id]
    if args.cases:
        workspace_args.extend(["--cases", *args.cases])
    workspace_stdout = run_step("workspace", scripts / "workspace.py", workspace_args, capture=True)
    workspace = next(
        (
            line.removeprefix("WORKSPACE: ").strip()
            for line in workspace_stdout.splitlines()
            if line.startswith("WORKSPACE: ")
        ),
        "",
    )
    if not workspace:
        print("AEH did not report a workspace path", file=sys.stderr)
        return 1
    print(f"Workspace: {workspace}", file=sys.stderr)
    workspace_path = Path(workspace)
    if not fixtures_are_provisioned(workspace_path, args.cases):
        print("AEH did not provision each selected fixture", file=sys.stderr)
        return 1

    execute_args = [
        "--config",
        str(config_path),
        "--workspace",
        workspace,
        "--model",
        model,
        "--output",
        str(output_dir),
        "--run-id",
        run_id,
    ]
    target = config.resolve_skill()
    if target and not config.is_prompt_mode():
        execute_args.extend(["--skill", target])
    run_step("execute", scripts / "execute.py", execute_args)

    run_step(
        "collect",
        scripts / "collect.py",
        ["--config", str(config_path), "--workspace", workspace, "--output", str(output_dir)],
    )
    score_args = [
        "judges",
        "--run-id",
        run_id,
        "--config",
        str(config_path),
        "--workspace",
        workspace,
        "--model",
        model,
    ]
    if args.no_llm_judges:
        score_args.append("--no-llm-judges")
    run_step("score", scripts / "score.py", score_args)

    if config.thresholds:
        run_step(
            "thresholds",
            scripts / "score.py",
            ["regression", "--run-id", run_id, "--config", str(config_path)],
        )

    report_args = ["--run-id", run_id, "--config", str(config_path)]
    run_step("report", scripts / "report.py", report_args)
    print(f"\nResults: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
