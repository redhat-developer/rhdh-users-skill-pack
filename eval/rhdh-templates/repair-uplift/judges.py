"""Deterministic judges for the invalid-template repair uplift evaluation."""

from __future__ import annotations

import json
import re
import shlex
from typing import Any

SKILL_ROOT_PATTERN = re.compile(r"(?:^|[\s'\"/])skills[/\\]rhdh-templates(?:[/\\]|$)", re.I)


def _observed_commands(outputs: dict[str, Any]) -> list[tuple[str, str, bool]]:
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


def _clean_validation_was_observed(outputs: dict[str, Any]) -> bool:
    for command, content, is_error in _observed_commands(outputs):
        try:
            tokens = shlex.split(command)
        except ValueError:
            continue
        if is_error or not any(
            token.endswith("skills/rhdh-templates/scripts/validate.py") for token in tokens
        ):
            continue
        if "--json" not in tokens or "fixture/invalid-template/template.yaml" not in tokens:
            continue
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            continue
        if (
            isinstance(result, dict)
            and result.get("ok") is True
            and result.get("critical_count") == 0
        ):
            return True
    return False


def check_repair(outputs: dict[str, Any]) -> tuple[bool, str]:
    """Require the reviewed repair and a clean local validation trace."""
    annotations = outputs.get("annotations", {})
    expected = outputs.get("annotation_expected_template_content")
    modified_path = annotations.get("modified_path")
    if not isinstance(expected, str) or not isinstance(modified_path, str):
        return False, "case is missing reviewed repair annotations"
    if outputs.get("modified_files") != {modified_path: expected}:
        return False, "workspace changes differ from the reviewed repair"
    if outputs.get("files", {}).get("output/template.yaml") != expected:
        return False, "output/template.yaml does not match the reviewed repair"
    if not _clean_validation_was_observed(outputs):
        return False, "no successful validation with zero critical findings was observed"
    return True, "reviewed repair and clean validation were observed"


def check_baseline_is_skill_free(outputs: dict[str, Any]) -> tuple[bool, str]:
    """Ensure the baseline trace did not consult the skill instructions."""
    for event in outputs.get("events", []):
        if event.get("type") != "assistant":
            continue
        for tool in event.get("tools", []):
            tool_input = tool.get("input", {})
            values: list[object] = []
            if tool.get("name") == "Read":
                values.append(tool_input.get("file_path", ""))
            elif tool.get("name") == "Bash":
                values.extend(tool_input.get("read_paths", []))
                values.append(tool_input.get("command", ""))
            if any(SKILL_ROOT_PATTERN.search(str(value)) for value in values):
                return False, "baseline trace consulted the rhdh-templates skill root"
    return True, "baseline trace did not consult the rhdh-templates skill root"
