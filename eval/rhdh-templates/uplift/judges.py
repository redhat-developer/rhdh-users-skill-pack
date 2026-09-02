"""Deterministic judges shared by rhdh-templates uplift arms."""

from __future__ import annotations

from typing import Any

SKILL_PATH_SUFFIX = "skills/rhdh-templates/skill.md"


def check_baseline_is_skill_free(outputs: dict[str, Any]) -> tuple[bool, str]:
    """Ensure a baseline trace did not consult the skill instructions."""
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
            if any(SKILL_PATH_SUFFIX in str(value).replace("\\", "/").lower() for value in values):
                return False, "baseline trace consulted rhdh-templates/SKILL.md"
    return True, "baseline trace did not consult rhdh-templates/SKILL.md"


def check_uplift_behavior(outputs: dict[str, Any]) -> tuple[bool, str]:
    """Grade a reviewed uplift case from observable workspace state."""
    annotations = outputs.get("annotations", {})
    case_kind = annotations.get("case_kind")

    if case_kind == "confirmation-gate":
        if outputs.get("modified_files"):
            return False, "templatize source changed before confirmation"
        proposal = outputs.get("files", {}).get("output/proposal.md", "")
        missing = [
            marker
            for marker in annotations.get("required_proposal_markers", [])
            if marker.lower() not in str(proposal).lower()
        ]
        if missing:
            return False, f"proposal is missing reviewed mappings: {missing}"
        return True, "reviewed mapping proposal exists and source files were not changed"

    if case_kind == "expected-modifications":
        expected_modified: dict[str, str] = {}
        for item in annotations.get("expected_modified", []):
            if not isinstance(item, dict):
                return False, "expected_modified contains a non-mapping entry"
            path = item.get("path")
            content_key = item.get("content_key")
            content = outputs.get(f"annotation_{content_key}_content")
            if not isinstance(path, str) or not isinstance(content, str):
                return False, f"missing reviewed expected content for {path!r}"
            expected_modified[path] = content
        if not expected_modified:
            return False, "case declares no reviewed modifications"
        if outputs.get("modified_files") != expected_modified:
            return False, "workspace changes differ from the reviewed expected files"
        return True, "workspace changes exactly match the reviewed expected files"

    return False, f"unsupported case kind: {case_kind!r}"
