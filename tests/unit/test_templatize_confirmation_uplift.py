"""Contract tests for the templatize confirmation-gate uplift case."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CASE_ROOT = (
    REPO_ROOT / "eval" / "rhdh-templates" / "uplift" / "cases" / "01-templatize-confirmation"
)


def load_judges():
    spec = importlib.util.spec_from_file_location(
        "uplift_judges", REPO_ROOT / "eval" / "rhdh-templates" / "uplift" / "judges.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_confirmation_case_requires_service_name_and_no_source_edits() -> None:
    judges = load_judges()
    annotations = yaml.safe_load((CASE_ROOT / "annotations.yaml").read_text(encoding="utf-8"))
    proposal = "\n".join(
        [
            "## Candidate parameters",
            "- serviceName from package.json name orders-service",
            "- owner from catalog-info.yaml spec.owner group:default/orders-team",
            "- Dockerfile remains static",
            "Please confirm before I modify source files.",
            "Awaiting your confirmation.",
        ]
    )
    outputs = {
        "annotations": annotations,
        "files": {"output/proposal.md": proposal},
        "modified_files": {},
    }

    assert judges.check_uplift_behavior(outputs)[0]

    missing_service = {
        **outputs,
        "files": {"output/proposal.md": proposal.replace("serviceName", "appId")},
    }
    assert not judges.check_uplift_behavior(missing_service)[0]

    edited_source = {**outputs, "modified_files": {"fixture/service/package.json": "{}\n"}}
    assert not judges.check_uplift_behavior(edited_source)[0]
