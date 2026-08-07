#!/usr/bin/env python3
"""Validate resolution decisions for every required comparison record."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from common import SCHEMA_VERSION, comparison_records, dump_json, load_json

ALLOWED_OUTCOMES = {
    "merge_equivalent", "merge_conditionally", "preserve_primary_and_note_alternative",
    "preserve_as_historical", "preserve_both_unresolved", "requires_human_review",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the conflict and historical-status decision ledger.")
    parser.add_argument("--comparisons-dir", type=Path, required=True)
    parser.add_argument("--comparison-index", type=Path, required=True)
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records, _ = comparison_records(args.comparisons_dir)
    index = load_json(args.comparison_index)
    decision_doc = load_json(args.decisions)
    required = set(map(str, index.get("required_resolution_ids", [])))
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    assigned: list[str] = []
    decision_ids: list[str] = []
    unresolved = 0

    for decision in decision_doc.get("decisions", []):
        if not isinstance(decision, dict) or not decision.get("decision_id"):
            errors.append({"code": "invalid_decision"})
            continue
        decision_id = str(decision["decision_id"])
        decision_ids.append(decision_id)
        comparison_id = str(decision.get("comparison_id", ""))
        assigned.append(comparison_id)
        if comparison_id not in required:
            errors.append({"code": "decision_for_unrequired_or_unknown_comparison", "decision_id": decision_id, "comparison_id": comparison_id})
            continue
        record = records.get(comparison_id, {})
        expected_units = set(map(str, record.get("unit_ids", [])))
        presentations = decision.get("unit_presentations", [])
        presented_units = {
            str(item.get("unit_id"))
            for item in presentations
            if isinstance(item, dict) and item.get("unit_id")
        }
        if presented_units != expected_units:
            errors.append({"code": "decision_unit_presentation_mismatch", "decision_id": decision_id, "missing": sorted(expected_units - presented_units), "unknown": sorted(presented_units - expected_units)})
        if str(decision.get("outcome", "")) not in ALLOWED_OUTCOMES:
            errors.append({"code": "invalid_decision_outcome", "decision_id": decision_id})
        if decision.get("requires_human_review") or decision.get("outcome") in {"preserve_both_unresolved", "requires_human_review"}:
            unresolved += 1

    counts = Counter(assigned)
    missing = sorted(required - set(counts))
    nonexact = sorted(comparison_id for comparison_id in required if counts[comparison_id] != 1)
    if missing:
        errors.append({"code": "missing_required_decisions", "items": missing})
    if nonexact:
        errors.append({"code": "nonexact_decision_assignment", "items": nonexact})
    duplicate_decision_ids = sorted(value for value, count in Counter(decision_ids).items() if count > 1)
    if duplicate_decision_ids:
        errors.append({"code": "duplicate_decision_ids", "items": duplicate_decision_ids})

    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "required_decisions": len(required),
            "decisions": len(decision_ids),
            "unresolved_or_human_review": unresolved,
        },
    }
    dump_json(args.report, report)
    print(report["status"])
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
