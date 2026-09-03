"""Tests for the deterministic local uplift metric helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "uplift_metrics",
    Path(__file__).parents[2] / "eval/rhdh-templates/uplift/metrics.py",
)
assert _SPEC and _SPEC.loader
_METRICS = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_METRICS)
delta_pass_at_3 = _METRICS.delta_pass_at_3
efficiency_guardrails = _METRICS.efficiency_guardrails
summarize_attempts = _METRICS.summarize_attempts


def test_summary_reports_primary_three_attempt_metrics() -> None:
    assert summarize_attempts([False, True, False]) == {
        "attempts": 3,
        "passes": 1,
        "contract_pass_rate": 1 / 3,
        "pass@3": True,
        "pass^3": False,
    }


def test_delta_and_efficiency_guardrails() -> None:
    assert delta_pass_at_3([False, False, False], [True, False, False]) == -1
    events = [
        {"type": "assistant", "tools": [{"name": "Bash", "input": {"command": "pwd"}}]},
        {"type": "assistant", "tools": [{"name": "Bash", "input": {"command": "pwd"}}]},
        {"type": "assistant", "tools": [{"name": "Bash", "input": {"command": "pwd"}}]},
    ]
    assert efficiency_guardrails(events) == {"command_count": 3, "loop_detected": True}
