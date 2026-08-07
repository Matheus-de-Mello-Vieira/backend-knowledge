#!/usr/bin/env python3
"""Validate comparison batches and build a comparison index."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from common import SCHEMA_VERSION, dump_json, json_files, load_json

ALLOWED_RELATIONSHIPS = {
    "equivalent", "near_duplicate", "complementary", "conflicting",
    "conditionally_compatible", "unique", "outdated",
}
REQUIRES_RESOLUTION = {"conflicting", "conditionally_compatible", "outdated"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate topic comparison batches.")
    parser.add_argument("--topics", type=Path, required=True)
    parser.add_argument("--comparisons-dir", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    topics_doc = load_json(args.topics)
    topic_units = {
        str(topic["topic_id"]): set(map(str, topic.get("unit_ids", [])))
        for topic in topics_doc.get("topics", [])
        if isinstance(topic, dict) and topic.get("topic_id")
    }
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    assigned_topics: list[str] = []
    comparison_ids: list[str] = []
    required_resolution_ids: list[str] = []
    batches: list[dict[str, Any]] = []

    files = json_files(args.comparisons_dir, exclude_names={"index.json", "validation-report.json"})
    if topic_units and not files:
        errors.append({"code": "missing_comparison_batches"})

    for path in files:
        data = load_json(path)
        batch_id = str(data.get("batch_id", path.stem))
        batch_topics = [str(value) for value in data.get("assigned_topic_ids", [])]
        assigned_topics.extend(batch_topics)
        unknown_topics = sorted(set(batch_topics) - set(topic_units))
        if unknown_topics:
            errors.append({"code": "unknown_assigned_topics", "batch_id": batch_id, "items": unknown_topics})
        expected_units = set().union(*(topic_units.get(topic_id, set()) for topic_id in batch_topics)) if batch_topics else set()
        assigned_units = set(map(str, data.get("assigned_unit_ids", [])))
        accounted_units = set(map(str, data.get("accounted_unit_ids", [])))
        if assigned_units != expected_units:
            errors.append({"code": "assigned_unit_scope_mismatch", "batch_id": batch_id, "missing": sorted(expected_units - assigned_units), "unknown": sorted(assigned_units - expected_units)})
        if accounted_units != assigned_units:
            errors.append({"code": "accounted_unit_scope_mismatch", "batch_id": batch_id, "missing": sorted(assigned_units - accounted_units), "unknown": sorted(accounted_units - assigned_units)})

        record_accounting: set[str] = set()
        batch_record_ids: list[str] = []
        for record in data.get("records", []):
            if not isinstance(record, dict) or not record.get("comparison_id"):
                errors.append({"code": "invalid_comparison_record", "batch_id": batch_id})
                continue
            comparison_id = str(record["comparison_id"])
            comparison_ids.append(comparison_id)
            batch_record_ids.append(comparison_id)
            relationship = str(record.get("relationship", ""))
            if relationship not in ALLOWED_RELATIONSHIPS:
                errors.append({"code": "invalid_relationship", "comparison_id": comparison_id, "relationship": relationship})
            if relationship in REQUIRES_RESOLUTION:
                required_resolution_ids.append(comparison_id)
            record_units = set(map(str, record.get("unit_ids", [])))
            if not record_units or not record_units <= assigned_units:
                errors.append({"code": "comparison_unit_scope_error", "comparison_id": comparison_id})
            record_accounting.update(record_units)
            topic_id = str(record.get("topic_id", ""))
            if topic_id not in batch_topics:
                errors.append({"code": "comparison_topic_scope_error", "comparison_id": comparison_id, "topic_id": topic_id})
            if relationship in {"equivalent", "near_duplicate"} and not record.get("semantic_union"):
                errors.append({"code": "missing_semantic_union", "comparison_id": comparison_id})
        if record_accounting != assigned_units:
            errors.append({"code": "record_accounting_mismatch", "batch_id": batch_id, "missing": sorted(assigned_units - record_accounting), "unknown": sorted(record_accounting - assigned_units)})
        batches.append({"batch_id": batch_id, "path": path.name, "topic_ids": batch_topics, "comparison_ids": batch_record_ids})

    topic_counts = Counter(assigned_topics)
    missing_topics = sorted(set(topic_units) - set(topic_counts))
    unknown_topics = sorted(set(topic_counts) - set(topic_units))
    nonexact_topics = sorted(topic_id for topic_id in topic_units if topic_counts[topic_id] != 1)
    if missing_topics:
        errors.append({"code": "missing_topic_comparisons", "items": missing_topics})
    if unknown_topics:
        errors.append({"code": "unknown_topic_assignments", "items": unknown_topics})
    if nonexact_topics:
        errors.append({"code": "nonexact_topic_assignment", "items": nonexact_topics})
    duplicate_comparisons = sorted(value for value, count in Counter(comparison_ids).items() if count > 1)
    if duplicate_comparisons:
        errors.append({"code": "duplicate_comparison_ids", "items": duplicate_comparisons})

    index = {
        "schema_version": SCHEMA_VERSION,
        "comparison_ids": sorted(set(comparison_ids)),
        "required_resolution_ids": sorted(set(required_resolution_ids)),
        "batches": batches,
    }
    dump_json(args.index, index)
    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "topics": len(topic_units),
            "topics_assigned_exactly_once": sum(1 for topic_id in topic_units if topic_counts[topic_id] == 1),
            "comparison_records": len(set(comparison_ids)),
            "required_resolution_records": len(set(required_resolution_ids)),
        },
    }
    dump_json(args.report, report)
    print(report["status"])
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
