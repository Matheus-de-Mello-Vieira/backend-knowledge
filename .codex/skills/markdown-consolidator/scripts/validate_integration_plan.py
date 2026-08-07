#!/usr/bin/env python3
"""Validate unit-to-note assignments, heading policy, and planned note links."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from common import SCHEMA_VERSION, dump_json, load_json, unit_records

RELATIONSHIPS = {
    "broader_context", "prerequisite", "implementation_detail", "contrast",
    "alternative", "example", "continuation", "related_mechanism",
}
OPERATIONS = {"reuse_existing", "extend_section", "add_section", "create_note", "restructure_approved"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a repository integration plan.")
    parser.add_argument("--placement", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--units-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    placement = load_json(args.placement)
    plan = load_json(args.plan)
    units, _ = unit_records(args.units_dir)
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    placement_destinations = {
        str(item.get("path")): str(item.get("action"))
        for item in placement.get("destinations", [])
        if isinstance(item, dict) and item.get("path")
    }
    context_paths = {
        str(item.get("path"))
        for item in placement.get("related_notes", [])
        if isinstance(item, dict) and item.get("path")
    }
    plan_destinations = [item for item in plan.get("destinations", []) if isinstance(item, dict)]
    plan_paths = [str(item.get("path", "")) for item in plan_destinations]
    if set(plan_paths) != set(placement_destinations):
        errors.append({"code": "integration_destination_mismatch", "expected": sorted(placement_destinations), "actual": sorted(set(plan_paths))})
    if len(plan_paths) != len(set(plan_paths)):
        errors.append({"code": "duplicate_integration_destinations"})

    assignments: list[str] = []
    for item in plan_destinations:
        path = str(item.get("path", ""))
        action = item.get("action")
        if action != placement_destinations.get(path):
            errors.append({"code": "destination_action_mismatch", "path": path, "expected": placement_destinations.get(path), "actual": action})
        assigned = [str(value) for value in item.get("assigned_unit_ids", [])]
        assignments.extend(assigned)
        operations = item.get("section_operations", [])
        if not isinstance(operations, list) or not operations:
            errors.append({"code": "missing_section_operations", "path": path})
        operation_units: list[str] = []
        for operation in operations if isinstance(operations, list) else []:
            if not isinstance(operation, dict) or operation.get("operation") not in OPERATIONS:
                errors.append({"code": "invalid_section_operation", "path": path, "operation": operation})
                continue
            operation_units.extend(str(value) for value in operation.get("assigned_unit_ids", []))
        operation_counts = Counter(operation_units)
        if set(operation_counts) != set(assigned) or any(operation_counts[value] != 1 for value in assigned):
            errors.append({"code": "section_operation_unit_coverage", "path": path, "assigned": sorted(assigned), "operation_units": sorted(operation_units)})
        for change in item.get("heading_changes", []):
            if not isinstance(change, dict) or not change.get("old_heading") or not change.get("new_heading"):
                errors.append({"code": "invalid_heading_change", "path": path})
            elif change.get("approved") is not True:
                errors.append({"code": "unapproved_heading_change", "path": path, "old_heading": change.get("old_heading")})

    counts = Counter(assignments)
    expected_units = set(units)
    missing = sorted(expected_units - set(counts))
    unknown = sorted(set(counts) - expected_units)
    nonexact = sorted(unit_id for unit_id in expected_units if counts[unit_id] != 1)
    if missing:
        errors.append({"code": "missing_primary_unit_destinations", "items": missing})
    if unknown:
        errors.append({"code": "unknown_unit_destinations", "items": unknown})
    if nonexact:
        errors.append({"code": "nonexact_primary_unit_destinations", "items": nonexact})

    links = plan.get("link_plan", [])
    seen_links: set[tuple[str, str, str]] = set()
    for index, link in enumerate(links if isinstance(links, list) else []):
        if not isinstance(link, dict):
            errors.append({"code": "invalid_link_plan_entry", "index": index})
            continue
        source = str(link.get("from_path", ""))
        target = str(link.get("to_path", ""))
        relationship = str(link.get("relationship", ""))
        if source not in placement_destinations:
            errors.append({"code": "link_source_not_destination", "path": source})
        if target not in placement_destinations and target not in context_paths:
            errors.append({"code": "link_target_not_durable_note", "path": target})
        if relationship not in RELATIONSHIPS:
            errors.append({"code": "invalid_link_relationship", "relationship": relationship})
        if not str(link.get("reason", "")).strip():
            errors.append({"code": "link_missing_reason", "from_path": source, "to_path": target})
        key = (source, target, str(link.get("to_heading", "")))
        if key in seen_links:
            errors.append({"code": "duplicate_link_plan_entry", "from_path": source, "to_path": target})
        seen_links.add(key)

    modified_context = set(plan.get("modified_context_paths", []))
    if modified_context:
        errors.append({"code": "context_notes_must_remain_read_only", "items": sorted(modified_context)})

    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "destinations": len(plan_paths),
            "units": len(expected_units),
            "units_assigned_once": sum(1 for unit_id in expected_units if counts[unit_id] == 1),
            "planned_links": len(seen_links),
        },
    }
    dump_json(args.report, report)
    print(report["status"])
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
