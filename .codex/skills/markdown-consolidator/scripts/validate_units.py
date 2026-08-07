#!/usr/bin/env python3
"""Validate exhaustive extraction batches and build a unit index."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import SCHEMA_VERSION, dump_json, json_files, load_json

ALLOWED_TYPES = {
    "heading", "metadata", "context", "definition", "claim", "rationale",
    "procedure", "requirement", "recommendation", "warning", "limitation",
    "exception", "alternative", "example", "quote", "code", "table",
    "reference", "open_question", "structure",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate source-line and content-unit extraction coverage.")
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--units-dir", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def valid_range(value: Any) -> tuple[int, int] | None:
    if not isinstance(value, dict):
        return None
    start, end = value.get("start"), value.get("end")
    if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start:
        return None
    return start, end


def main() -> int:
    args = parse_args()
    inventory = load_json(args.inventory)
    source_records = {
        str(item["source_id"]): item
        for item in inventory.get("sources", [])
        if isinstance(item, dict) and item.get("source_id")
    }
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    source_assignment: list[str] = []
    unit_ids: list[str] = []
    unit_types: Counter[str] = Counter()
    unit_source: dict[str, str] = {}
    covered_lines: dict[str, set[int]] = defaultdict(set)
    batch_index: list[dict[str, Any]] = []

    files = json_files(args.units_dir, exclude_names={"index.json", "validation-report.json"})
    if not files:
        errors.append({"code": "missing_unit_batches"})

    for path in files:
        try:
            data = load_json(path)
        except (OSError, ValueError) as exc:
            errors.append({"code": "invalid_unit_batch", "path": str(path), "message": str(exc)})
            continue
        batch_id = str(data.get("batch_id", path.stem))
        batch_sources = [str(value) for value in data.get("sources", [])]
        source_assignment.extend(batch_sources)
        if data.get("uncovered_nonempty_lines") not in ([], None):
            errors.append({"code": "declared_uncovered_nonempty_lines", "batch_id": batch_id, "items": data.get("uncovered_nonempty_lines")})

        for item in data.get("covered_line_ranges", []):
            if not isinstance(item, dict) or not item.get("source_id"):
                errors.append({"code": "malformed_covered_line_range", "batch_id": batch_id})
                continue
            parsed = valid_range(item.get("range"))
            if parsed is None:
                errors.append({"code": "malformed_covered_line_range", "batch_id": batch_id, "value": item})

        batch_unit_ids: list[str] = []
        for unit in data.get("units", []):
            if not isinstance(unit, dict) or not unit.get("unit_id"):
                errors.append({"code": "invalid_unit", "batch_id": batch_id})
                continue
            unit_id = str(unit["unit_id"])
            source_id = str(unit.get("source_id", ""))
            unit_ids.append(unit_id)
            batch_unit_ids.append(unit_id)
            unit_source[unit_id] = source_id
            unit_type = str(unit.get("unit_type", ""))
            unit_types[unit_type] += 1
            if unit_type not in ALLOWED_TYPES:
                errors.append({"code": "invalid_unit_type", "unit_id": unit_id, "unit_type": unit_type})
            if source_id not in source_records:
                errors.append({"code": "unknown_unit_source", "unit_id": unit_id, "source_id": source_id})
                continue
            if source_id not in batch_sources:
                errors.append({"code": "unit_source_outside_batch", "unit_id": unit_id, "source_id": source_id})
            parsed = valid_range(unit.get("source_range"))
            if parsed is None:
                errors.append({"code": "malformed_unit_range", "unit_id": unit_id, "value": unit.get("source_range")})
                continue
            start, end = parsed
            line_count = int(source_records[source_id].get("line_count", 0))
            if end > line_count:
                errors.append({"code": "unit_range_out_of_bounds", "unit_id": unit_id, "end": end, "line_count": line_count})
                continue
            covered_lines[source_id].update(range(start, end + 1))
            if not isinstance(unit.get("source_text"), str):
                errors.append({"code": "missing_source_text", "unit_id": unit_id})
        batch_index.append({"batch_id": batch_id, "path": path.name, "source_ids": batch_sources, "unit_ids": batch_unit_ids})

    duplicate_units = sorted(value for value, count in Counter(unit_ids).items() if count > 1)
    if duplicate_units:
        errors.append({"code": "duplicate_unit_ids", "items": duplicate_units})

    expected_sources = set(source_records)
    assignment_counter = Counter(source_assignment)
    missing_sources = sorted(source_id for source_id in expected_sources if assignment_counter[source_id] == 0)
    duplicate_sources = sorted(source_id for source_id in expected_sources if assignment_counter[source_id] != 1)
    unknown_sources = sorted(set(source_assignment) - expected_sources)
    if missing_sources:
        errors.append({"code": "missing_source_batches", "items": missing_sources})
    if duplicate_sources:
        errors.append({"code": "source_assigned_nonexactly_once", "items": duplicate_sources})
    if unknown_sources:
        errors.append({"code": "unknown_batch_sources", "items": unknown_sources})

    total_nonempty = 0
    total_covered_nonempty = 0
    uncovered_by_source: dict[str, list[int]] = {}
    for source_id, record in source_records.items():
        path = Path(str(record.get("absolute_path", "")))
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except OSError as exc:
            errors.append({"code": "source_read_error", "source_id": source_id, "message": str(exc)})
            continue
        nonempty = {index for index, line in enumerate(lines, start=1) if line.strip()}
        total_nonempty += len(nonempty)
        covered = nonempty & covered_lines[source_id]
        total_covered_nonempty += len(covered)
        uncovered = sorted(nonempty - covered_lines[source_id])
        if uncovered:
            uncovered_by_source[source_id] = uncovered
            errors.append({"code": "uncovered_nonempty_lines", "source_id": source_id, "lines": uncovered})

    index = {
        "schema_version": SCHEMA_VERSION,
        "source_ids": sorted(expected_sources),
        "unit_ids": sorted(set(unit_ids)),
        "unit_count": len(set(unit_ids)),
        "units_by_source": {
            source_id: sorted(unit_id for unit_id, sid in unit_source.items() if sid == source_id)
            for source_id in sorted(expected_sources)
        },
        "unit_type_counts": dict(sorted(unit_types.items())),
        "batches": batch_index,
    }
    dump_json(args.index, index)
    coverage = total_covered_nonempty / total_nonempty if total_nonempty else 1.0
    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "inventory_sources": len(expected_sources),
            "unit_batches": len(files),
            "units": len(set(unit_ids)),
            "nonempty_source_lines": total_nonempty,
            "covered_nonempty_source_lines": total_covered_nonempty,
            "source_line_coverage": coverage,
        },
    }
    dump_json(args.report, report)
    print(report["status"])
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
