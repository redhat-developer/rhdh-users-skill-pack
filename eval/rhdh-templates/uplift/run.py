#!/usr/bin/env python3
"""Run one uplift arm through Agent Eval Harness."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aeh-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--run-id", required=True)
    return parser.parse_args()


def run(script: Path, arguments: list[str], *, capture: bool = False) -> str:
    result = subprocess.run(
        [sys.executable, str(script), *arguments], capture_output=capture, text=True, check=False
    )
    if capture and result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    if result.returncode:
        raise SystemExit(result.returncode)
    return result.stdout


def run_namespace(config_path: Path) -> str:
    config_text = config_path.read_text(encoding="utf-8")
    if config_path.name == "skill.eval.yaml":
        return "rhdh-templates"
    return config_text.splitlines()[0].removeprefix("name: ")


def main() -> int:
    args = parse_args()
    scripts = args.aeh_dir.resolve() / "skills" / "eval-run" / "scripts"
    required = [
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
    if missing := [str(path) for path in required if not path.is_file()]:
        print(f"AEH checkout is missing pipeline scripts: {missing}", file=sys.stderr)
        return 2
    config_path = args.config.resolve()
    run(scripts / "preflight.py", ["--config", str(config_path), "--run-id", args.run_id])
    workspace_output = run(
        scripts / "workspace.py",
        ["--config", str(config_path), "--run-id", args.run_id],
        capture=True,
    )
    workspace = next(
        (
            line.removeprefix("WORKSPACE: ")
            for line in workspace_output.splitlines()
            if line.startswith("WORKSPACE: ")
        ),
        "",
    )
    if not workspace:
        print("AEH did not report a workspace path", file=sys.stderr)
        return 1
    output = Path("eval/runs/rhdh-templates-uplift") / run_namespace(config_path) / args.run_id
    execute_args = [
        "--config",
        str(config_path),
        "--workspace",
        workspace,
        "--model",
        args.model,
        "--output",
        str(output),
        "--run-id",
        args.run_id,
    ]
    run(scripts / "execute.py", execute_args)
    run(
        scripts / "collect.py",
        ["--config", str(config_path), "--workspace", workspace, "--output", str(output)],
    )
    run(
        scripts / "score.py",
        [
            "judges",
            "--run-id",
            args.run_id,
            "--config",
            str(config_path),
            "--workspace",
            workspace,
            "--model",
            args.model,
        ],
    )
    run(scripts / "report.py", ["--run-id", args.run_id, "--config", str(config_path)])
    print(output / "summary.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
