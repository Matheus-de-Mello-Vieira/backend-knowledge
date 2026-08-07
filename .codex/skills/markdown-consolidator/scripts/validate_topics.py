#!/usr/bin/env python3
"""Validate exact primary-topic assignment for every extracted unit."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from common import SCHEMA_VERSION, dump_json, load_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate topic groups against the unit index.")
    parser.add_argument("--unit-index", type=Path, required=True)
    parser.add_argument("--topics", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    unit_index = load_json(args.unit_index)
    topics_doc = load_json(args.topics)
    expected = set(map(str, unit_index.get("unit_ids", [])))
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    assignments: list[str] = []
    topic_ids: list[str] = []

    for topic in topics_doc.get("topics", []):
        if not isinstance(topic, dict) or not topic.get("topic_id"):
            errors.append({"code": "invalid_topic"})
            continue
        topic_id = str(topic["topic_id"])
        topic_ids.append(topic_id)
        units = [str(value) for value in topic.get("unit_ids", [])]
        assignments.extend(units)
        unknown_cross = sorted(set(map(str, topic.get("cross_topic_unit_ids", []))) - expected)
        if unknown_cross:
            errors.append({"code": "unknown_cross_topic_units", "topic_id": topic_id, "items": unknown_cross})

    duplicate_topic_ids = sorted(value for value, count in Counter(topic_ids).items() if count > 1)
    if duplicate_topic_ids:
        errors.append({"code": "duplicate_topic_ids", "items": duplicate_topic_ids})
    counts = Counter(assignments)
    missing = sorted(expected - set(counts))
    unknown = sorted(set(counts) - expected)
    duplicate = sorted(value for value in expected if counts[value] != 1)
    if missing:
        errors.append({"code": "unassigned_units", "items": missing})
    if unknown:
        errors.append({"code": "unknown_topic_units", "items": unknown})
    if duplicate:
        errors.append({"code": "nonexact_primary_topic_assignment", "items": duplicate})

    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "units": len(expected),
            "units_assigned_exactly_once": sum(1 for unit_id in expected if counts[unit_id] == 1),
            "topics": len(set(topic_ids)),
        },
    }
    dump_json(args.report, report)
    print(report["status"])
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
