"""Deterministic judges shared by rhdh-templates uplift arms."""

from __future__ import annotations

import re
import json
import shlex
from typing import Any

SKILL_ROOT_PATTERN = re.compile(r"(?:^|[\s'\"/])skills[/\\]rhdh-templates(?:[/\\]|$)", re.I)


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
            if any(SKILL_ROOT_PATTERN.search(str(value)) for value in values):
                return False, "baseline trace consulted the rhdh-templates skill root"
    return True, "baseline trace did not consult the rhdh-templates skill root"


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

    if case_kind == "repair":
        expected = outputs.get("annotation_expected_template_content")
        path = annotations.get("modified_path")
        if not isinstance(expected, str) or not isinstance(path, str):
            return False, "case is missing reviewed repair annotations"
        if outputs.get("modified_files") != {path: expected}:
            return False, "workspace changes differ from the reviewed repair"
        if outputs.get("files", {}).get("output/template.yaml") != expected:
            return False, "output/template.yaml does not match the reviewed repair"
        for event in outputs.get("events", []):
            if event.get("type") != "assistant":
                continue
            for tool in event.get("tools", []):
                if tool.get("name") != "Bash":
                    continue
                command = str(tool.get("input", {}).get("command", ""))
                try:
                    tokens = shlex.split(command)
                except ValueError:
                    continue
                if not any(token.endswith("skills/rhdh-templates/scripts/validate.py") for token in tokens):
                    continue
                if "--json" not in tokens or "fixture/invalid-template/template.yaml" not in tokens:
                    continue
                result = next(
                    (
                        result_event
                        for result_event in outputs.get("events", [])
                        if result_event.get("type") == "tool_result"
                        and result_event.get("tool_use_id") == tool.get("id")
                    ),
                    {},
                )
                try:
                    payload = json.loads(str(result.get("content", "")))
                except json.JSONDecodeError:
                    continue
                if not result.get("is_error") and payload.get("ok") is True and payload.get("critical_count") == 0:
                    return True, "reviewed repair and clean validation were observed"
        return False, "no successful validation with zero critical findings was observed"

    return False, f"unsupported case kind: {case_kind!r}"
