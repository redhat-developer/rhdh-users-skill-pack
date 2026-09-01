#!/usr/bin/env python3
"""Report routing metrics, variance, and named misses from AEH summaries."""

from __future__ import annotations

import argparse
import statistics
from pathlib import Path

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--summaries", type=Path, nargs="+")
    parser.add_argument("--cases-dir", type=Path, required=True)
    return parser.parse_args()


def score_summary(summary_path: Path, cases_dir: Path) -> tuple[dict[str, int], list[str], list[str], list[str]]:
    summary = yaml.safe_load(summary_path.read_text(encoding="utf-8")) or {}
    per_case = summary.get("per_case", {})
    counts = {"true_positive": 0, "true_negative": 0, "false_positive": 0, "false_negative": 0}
    false_positives: list[str] = []
    false_negatives: list[str] = []
    errors: list[str] = []
    for case_dir in sorted(cases_dir.iterdir()):
        if not case_dir.is_dir():
            continue
        annotations = yaml.safe_load((case_dir / "annotations.yaml").read_text(encoding="utf-8")) or {}
        expected = annotations.get("should_trigger")
        matched = per_case.get(case_dir.name, {}).get("activation_match", {}).get("value")
        if not isinstance(expected, bool) or not isinstance(matched, bool):
            errors.append(case_dir.name)
            continue
        observed = expected if matched else not expected
        if expected and observed:
            counts["true_positive"] += 1
        elif not expected and not observed:
            counts["true_negative"] += 1
        elif observed:
            counts["false_positive"] += 1
            false_positives.append(case_dir.name)
        else:
            counts["false_negative"] += 1
            false_negatives.append(case_dir.name)
    return counts, false_positives, false_negatives, errors


def main() -> int:
    args = parse_args()
    summary_paths = args.summaries or ([args.summary] if args.summary else [])
    if not summary_paths:
        raise SystemExit("pass --summary or --summaries")
    precision_values: list[float] = []
    recall_values: list[float] = []
    for summary_path in summary_paths:
        counts, false_positives, false_negatives, errors = score_summary(summary_path, args.cases_dir)
        predicted_positive = counts["true_positive"] + counts["false_positive"]
        actual_positive = counts["true_positive"] + counts["false_negative"]
        precision = counts["true_positive"] / predicted_positive if predicted_positive else 0.0
        recall = counts["true_positive"] / actual_positive if actual_positive else 0.0
        precision_values.append(precision)
        recall_values.append(recall)
        print(f"{summary_path.name}: precision={precision:.3f} recall={recall:.3f}")
        for name, value in counts.items():
            print(f"  {name}: {value}")
        if len(summary_paths) == 1:
            print(f"precision: {precision:.3f}")
            print(f"recall: {recall:.3f}")
        print(f"  false_positives: {', '.join(false_positives) or 'none'}")
        print(f"  false_negatives: {', '.join(false_negatives) or 'none'}")
        if errors:
            print(f"  unscored_cases: {', '.join(errors)}")
            return 1
    print(f"precision_mean: {statistics.mean(precision_values):.3f}")
    print(f"precision_variance: {statistics.pvariance(precision_values):.6f}")
    print(f"recall_mean: {statistics.mean(recall_values):.3f}")
    print(f"recall_variance: {statistics.pvariance(recall_values):.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
