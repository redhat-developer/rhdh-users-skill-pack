"""Trace-based routing judges for rhdh-templates."""

from __future__ import annotations

from typing import Any

SKILL_PATH_SUFFIX = "skills/rhdh-templates/skill.md"


def _normalise_path(value: object) -> str:
    return str(value).replace("\\", "/").lower()


def observed_activation(outputs: dict[str, Any]) -> bool:
    """Return whether events show the rhdh-templates instructions were read."""
    for event in outputs.get("events", []):
        if event.get("type") != "assistant":
            continue
        for tool in event.get("tools", []):
            tool_input = tool.get("input", {})
            paths: list[object] = []
            if tool.get("name") == "Read":
                paths.append(tool_input.get("file_path", ""))
            elif tool.get("name") == "Bash":
                paths.extend(tool_input.get("read_paths", []))
                paths.append(tool_input.get("command", ""))
            if any(SKILL_PATH_SUFFIX in _normalise_path(path) for path in paths):
                return True
    return False


def check_routing(outputs: dict[str, Any]) -> tuple[bool, str]:
    """Compare observed activation with the reviewed case expectation."""
    expected = bool(outputs.get("annotations", {}).get("should_trigger", False))
    activated = observed_activation(outputs)
    if activated == expected:
        return True, f"trace activation={activated} matched expected={expected}"
    return False, f"trace activation={activated} did not match expected={expected}"
