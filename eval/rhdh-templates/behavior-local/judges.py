"""Deterministic judge for local rhdh-templates validation."""

from __future__ import annotations

import json
import re
import shlex
from pathlib import PurePosixPath
from typing import Any

VALIDATOR_SUFFIX = "skills/rhdh-templates/scripts/validate.py"
FIX_GOTCHAS_SUFFIX = "skills/rhdh-templates/scripts/fix_gotchas.py"
FIXTURE_PATHS = {
    "validate-success": {"fixture/minimal-template", "fixture/minimal-template/template.yaml"},
    "fix-gotchas-repair": {"fixture/fixable-template", "fixture/fixable-template/template.yaml"},
    "manual-secret-finding": {"fixture/manual-issue", "fixture/manual-issue/template.yaml"},
}


def _observed_commands(outputs: dict[str, Any]) -> list[tuple[str, str, bool]]:
    """Return Bash command, output, and error state from normalized AEH events."""
    commands: dict[str, str] = {}
    observed: list[tuple[str, str, bool]] = []
    for event in outputs.get("events", []):
        if event.get("type") == "assistant":
            for tool in event.get("tools", []):
                if tool.get("name") == "Bash":
                    commands[str(tool.get("id", ""))] = str(
                        tool.get("input", {}).get("command", "")
                    )
        elif event.get("type") == "tool_result":
            tool_id = str(event.get("tool_use_id", ""))
            if tool_id in commands:
                observed.append(
                    (
                        commands[tool_id],
                        str(event.get("content", "")),
                        bool(event.get("is_error", False)),
                    )
                )
    return observed


def _json_object(content: str) -> dict[str, Any] | None:
    """Extract one JSON object even when a shell prints harmless prelude text."""
    decoder = json.JSONDecoder()
    for index, character in enumerate(content):
        if character != "{":
            continue
        try:
            value, _end = decoder.raw_decode(content, index)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return None


def _shell_tokens(command: str) -> list[str] | None:
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        lexer.commenters = "#"
        tokens = list(lexer)
    except ValueError:
        return None

    if tokens and PurePosixPath(tokens[0]).name in {"bash", "sh"}:
        for index, token in enumerate(tokens[1:], start=1):
            if token.startswith("-") and "c" in token[1:] and index + 1 < len(tokens):
                return _shell_tokens(tokens[index + 1])
    return tokens


def _is_expected_script_invocation(
    command: str,
    script_suffix: str,
    fixture_paths: set[str],
    required_flags: set[str],
    prohibited_flags: set[str] | None = None,
) -> bool:
    tokens = _shell_tokens(command)
    if not tokens or any(token and set(token) <= set("();<>|&") for token in tokens):
        return False

    interpreter = PurePosixPath(tokens[0]).name
    if not re.fullmatch(r"python(?:\d+(?:\.\d+)*)?", interpreter):
        return False
    if len(tokens) < 2 or not tokens[1].endswith(script_suffix):
        return False

    arguments = tokens[2:]
    if not required_flags.issubset(arguments) or (
        prohibited_flags and prohibited_flags.intersection(arguments)
    ):
        return False
    if arguments.count("--path") != 1:
        return False
    path_index = arguments.index("--path")
    if path_index + 1 >= len(arguments):
        return False
    return arguments[path_index + 1].rstrip("/") in fixture_paths


def _successful_json_command(
    outputs: dict[str, Any],
    script_suffix: str,
    fixture_paths: set[str],
    required_flags: set[str],
    required_result: dict[str, Any],
    prohibited_flags: set[str] | None = None,
) -> bool:
    for command, content, is_error in _observed_commands(outputs):
        if is_error or not _is_expected_script_invocation(
            command,
            script_suffix,
            fixture_paths,
            required_flags,
            prohibited_flags,
        ):
            continue
        result = _json_object(content)
        if result is not None and all(
            result.get(key) == value for key, value in required_result.items()
        ):
            return True
    return False


def check_local_behavior(outputs: dict[str, Any]) -> tuple[bool, str]:
    """Check reviewed output, an unchanged fixture, and observed validation."""
    case_kind = outputs.get("annotations", {}).get("case_kind")
    if case_kind == "manual-secret-finding":
        if outputs.get("modified_files"):
            return False, "manual-only finding case modified fixture files"
        expected_rule_id = outputs.get("annotations", {}).get("expected_rule_id")
        if not isinstance(expected_rule_id, str):
            return False, "manual-only finding case has no reviewed rule identifier"
        for command, content, is_error in _observed_commands(outputs):
            if is_error or not _is_expected_script_invocation(
                command,
                FIX_GOTCHAS_SUFFIX,
                FIXTURE_PATHS[case_kind],
                {"--json"},
                {"--apply"},
            ):
                continue
            result = _json_object(content)
            rule_ids = (
                {
                    finding.get("rule_id")
                    for finding in result.get("findings", [])
                    if isinstance(finding, dict)
                }
                if isinstance(result, dict)
                else set()
            )
            if (
                result is not None
                and result.get("applied") is False
                and expected_rule_id in rule_ids
            ):
                return True, "manual finding was observed and the fixture remained unchanged"
        return False, "expected manual finding was not observed without --apply"

    expected = outputs.get("annotation_expected_template_content")
    actual = outputs.get("files", {}).get("output/template.yaml")
    if not isinstance(expected, str) or actual != expected:
        return False, "output/template.yaml does not match the reviewed expected artifact"

    if case_kind == "fix-gotchas-repair":
        modified_path = outputs.get("annotations", {}).get("modified_path")
        if outputs.get("modified_files") != {modified_path: expected}:
            return False, "workspace changes differ from the single reviewed repair"
        if not _successful_json_command(
            outputs,
            FIX_GOTCHAS_SUFFIX,
            FIXTURE_PATHS[case_kind],
            {"--apply", "--json"},
            {"ok": True, "applied": True},
        ):
            return False, "no successful applied fix_gotchas.py result was observed"
        if not _successful_json_command(
            outputs,
            VALIDATOR_SUFFIX,
            FIXTURE_PATHS[case_kind],
            {"--json"},
            {"ok": True, "critical_count": 0},
        ):
            return False, "no clean post-repair validation result was observed"
        return True, "exact reviewed repair and clean revalidation were observed"

    if case_kind != "validate-success":
        return False, f"unsupported case kind: {case_kind!r}"
    if outputs.get("modified_files"):
        return False, "validation-only case modified fixture files"
    if not _successful_json_command(
        outputs,
        VALIDATOR_SUFFIX,
        FIXTURE_PATHS[case_kind],
        {"--json"},
        {"ok": True, "critical_count": 0},
    ):
        return False, "no successful validate.py JSON result was observed in the trace"
    return True, "template matched expected artifact and clean validation was observed"
