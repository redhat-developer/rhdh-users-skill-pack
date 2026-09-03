"""Small, deterministic helpers for local uplift summaries."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable


def summarize_attempts(passed: Iterable[bool], attempts: int = 3) -> dict[str, Any]:
    """Return the standard primary metrics for one case and one arm."""
    results = [bool(value) for value in passed]
    if not results:
        raise ValueError("at least one attempt is required")
    selected = results[:attempts]
    return {
        "attempts": len(selected),
        "passes": sum(selected),
        "contract_pass_rate": sum(selected) / len(selected),
        "pass@3": bool(any(selected)) if len(selected) == attempts else None,
        "pass^3": bool(all(selected)) if len(selected) == attempts else None,
    }


def delta_pass_at_3(skill: Iterable[bool], baseline: Iterable[bool]) -> int:
    """Return skill pass@3 minus baseline pass@3."""
    return int(any(skill)) - int(any(baseline))


def efficiency_guardrails(events: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Count Bash commands and flag an immediately repeated command loop."""
    commands = [
        str(tool.get("input", {}).get("command", ""))
        for event in events
        if event.get("type") == "assistant"
        for tool in event.get("tools", [])
        if tool.get("name") == "Bash" and tool.get("input", {}).get("command")
    ]
    counts = Counter(commands)
    repeated = any(count >= 3 for count in counts.values())
    return {"command_count": len(commands), "loop_detected": repeated}
