"""Deterministic judge for local rhdh-templates validation."""

from __future__ import annotations

import json
from typing import Any


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


def _successful_validation(outputs: dict[str, Any]) -> bool:
    for command, content, is_error in _observed_commands(outputs):
        if "validate.py" not in command or is_error:
            continue
        result = _json_object(content)
        if result is not None and result.get("ok") is True:
            if result.get("critical_count") == 0:
                return True
    return False


def check_local_behavior(outputs: dict[str, Any]) -> tuple[bool, str]:
    """Check reviewed output, an unchanged fixture, and observed validation."""
    case_kind = outputs.get("annotations", {}).get("case_kind")
    if case_kind != "validate-success":
        return False, f"unsupported case kind: {case_kind!r}"

    expected = outputs.get("annotation_expected_template_content")
    actual = outputs.get("files", {}).get("output/template.yaml")
    if not isinstance(expected, str) or actual != expected:
        return False, "output/template.yaml does not match the reviewed expected artifact"
    if outputs.get("modified_files"):
        return False, "validation-only case modified fixture files"
    if not _successful_validation(outputs):
        return False, "no successful validate.py JSON result was observed in the trace"
    return True, "template matched expected artifact and clean validation was observed"
