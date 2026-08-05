#!/usr/bin/env python3
"""Validate that the Markdown consolidation ran through required subagents."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "2.2"
REQUIRED_VALIDATION_CATEGORIES = {
    "source_line_extraction",
    "unit_final_coverage",
    "conflicts_qualifiers",
    "traceability_unsupported_claims",
    "publication_independence",
    "coherence_markdown",
}
ALLOWED_ROLES = {
    "outline-planner",
    "source-analyst",
    "topic-organizer",
    "topic-comparator",
    "conflict-resolver",
    "synthesizer",
    "validator",
}
ROLE_PHASE = {
    "outline-planner": "outline",
    "source-analyst": "extraction",
    "topic-organizer": "topic_organization",
    "topic-comparator": "comparison",
    "conflict-resolver": "conflict_resolution",
    "synthesizer": "synthesis",
    "validator": "semantic_validation",
}
SCOPE_KEYS = {
    "source_ids",
    "topic_ids",
    "comparison_ids",
    "unit_ids",
    "validation_categories",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--units-dir", type=Path, required=True)
    parser.add_argument("--topics", type=Path, required=True)
    parser.add_argument("--comparisons-dir", type=Path, required=True)
    parser.add_argument("--decisions", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def load_json(path: Path, errors: list[dict[str, Any]], code: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append({"code": code, "message": f"Missing file: {path}"})
        return {}
    except (OSError, json.JSONDecodeError) as exc:
        errors.append({"code": code, "message": f"Cannot read {path}: {exc}"})
        return {}
    if not isinstance(data, dict):
        errors.append({"code": code, "message": f"Expected JSON object: {path}"})
        return {}
    return data


def json_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(path for path in directory.glob("*.json") if path.is_file())


def normalize_scope(value: Any) -> dict[str, list[str]]:
    scope = value if isinstance(value, dict) else {}
    result: dict[str, list[str]] = {}
    for key in SCOPE_KEYS:
        items = scope.get(key, [])
        if not isinstance(items, list):
            items = []
        result[key] = sorted({str(item) for item in items})
    return result


def resolve_under_work_dir(work_dir: Path, path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else work_dir / path


def is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except (OSError, ValueError):
        return False


def flatten_units(units_dir: Path, errors: list[dict[str, Any]]) -> set[str]:
    result: set[str] = set()
    files = json_files(units_dir)
    if not files:
        errors.append({"code": "missing_unit_batches", "message": f"No JSON unit batches in {units_dir}"})
    for path in files:
        data = load_json(path, errors, "unit_batch_read_error")
        for unit in data.get("units", []):
            if isinstance(unit, dict) and unit.get("unit_id"):
                result.add(str(unit["unit_id"]))
    return result


def load_comparison_ids(comparisons_dir: Path, errors: list[dict[str, Any]]) -> tuple[set[str], set[str]]:
    all_ids: set[str] = set()
    required_resolution: set[str] = set()
    for path in json_files(comparisons_dir):
        data = load_json(path, errors, "comparison_read_error")
        for record in data.get("records", []):
            if not isinstance(record, dict) or not record.get("comparison_id"):
                continue
            comparison_id = str(record["comparison_id"])
            all_ids.add(comparison_id)
            if record.get("relationship") in {"conflicting", "conditionally_compatible", "outdated"}:
                required_resolution.add(comparison_id)
    return all_ids, required_resolution


def add_count_coverage_errors(
    label: str,
    expected: set[str],
    assignments: Iterable[str],
    errors: list[dict[str, Any]],
) -> int:
    counter = Counter(assignments)
    assigned = set(counter)
    missing = sorted(expected - assigned)
    unknown = sorted(assigned - expected)
    duplicated = sorted(item for item, count in counter.items() if count != 1 and item in expected)
    if missing:
        errors.append({"code": f"missing_{label}_assignments", "items": missing})
    if unknown:
        errors.append({"code": f"unknown_{label}_assignments", "items": unknown})
    if duplicated:
        errors.append({"code": f"non_disjoint_{label}_assignments", "items": duplicated})
    return sum(1 for item in expected if counter.get(item) == 1)


def main() -> int:
    args = parse_args()
    work_dir = args.work_dir.resolve()
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    inventory = load_json(args.inventory, errors, "inventory_read_error")
    topics = load_json(args.topics, errors, "topics_read_error")
    log_path = work_dir / "delegation-log.json"
    log = load_json(log_path, errors, "delegation_log_read_error")

    if log.get("execution_mode") != "subagents_required":
        errors.append({"code": "invalid_execution_mode", "value": log.get("execution_mode")})
    if log.get("fallback_used") is not False:
        errors.append({"code": "fallback_used", "value": log.get("fallback_used")})

    tasks_raw = log.get("tasks", [])
    if not isinstance(tasks_raw, list):
        errors.append({"code": "invalid_task_entries"})
        tasks_raw = []
    tasks = [task for task in tasks_raw if isinstance(task, dict)]
    if len(tasks) != len(tasks_raw):
        errors.append({"code": "invalid_task_entries"})

    task_ids = [str(task.get("task_id", "")) for task in tasks]
    duplicate_task_ids = sorted(item for item, count in Counter(task_ids).items() if item and count > 1)
    if duplicate_task_ids:
        errors.append({"code": "duplicate_task_ids", "items": duplicate_task_ids})

    receipts_dir = work_dir / "receipts"
    receipts: dict[str, dict[str, Any]] = {}
    for path in json_files(receipts_dir):
        receipt = load_json(path, errors, "receipt_read_error")
        task_id = str(receipt.get("task_id", ""))
        if not task_id:
            errors.append({"code": "receipt_missing_task_id", "path": str(path)})
            continue
        if task_id in receipts:
            errors.append({"code": "duplicate_receipt_task_id", "task_id": task_id})
        receipts[task_id] = receipt

    unknown_receipts = sorted(set(receipts) - {task_id for task_id in task_ids if task_id})
    if unknown_receipts:
        errors.append({"code": "unlogged_task_receipts", "task_ids": unknown_receipts})

    completed_tasks: list[dict[str, Any]] = []
    completed_receipts: list[dict[str, Any]] = []
    for task in tasks:
        task_id = str(task.get("task_id", ""))
        role = str(task.get("role", ""))
        phase = str(task.get("phase", ""))
        status = str(task.get("status", ""))
        if role not in ALLOWED_ROLES:
            errors.append({"code": "unknown_role", "task_id": task_id, "role": role})
        elif ROLE_PHASE[role] != phase:
            errors.append({"code": "role_phase_mismatch", "task_id": task_id, "role": role, "phase": phase})

        if status == "skipped":
            if phase != "conflict_resolution" or any(normalize_scope(task.get("assigned_scope")).values()):
                errors.append({"code": "invalid_skipped_task", "task_id": task_id})
            continue
        if status == "failed":
            warnings.append({"code": "failed_attempt_recorded", "task_id": task_id})
            continue
        if status != "completed":
            errors.append({"code": "incomplete_task", "task_id": task_id, "status": status})
            continue

        completed_tasks.append(task)
        receipt = receipts.get(task_id)
        if not receipt:
            errors.append({"code": "missing_task_receipt", "task_id": task_id})
            continue
        completed_receipts.append(receipt)

        if receipt.get("producer") != "subagent":
            errors.append({"code": "invalid_receipt_producer", "task_id": task_id, "producer": receipt.get("producer")})
        for field in ("role", "phase", "status", "accepted_candidate"):
            expected = task.get(field)
            actual = receipt.get(field)
            if actual != expected:
                errors.append({"code": "receipt_task_mismatch", "task_id": task_id, "field": field, "expected": expected, "actual": actual})
        if normalize_scope(receipt.get("assigned_scope")) != normalize_scope(task.get("assigned_scope")):
            errors.append({"code": "receipt_scope_mismatch", "task_id": task_id})

        declared_receipt_path = str(task.get("receipt_path", ""))
        if not declared_receipt_path:
            errors.append({"code": "missing_declared_receipt_path", "task_id": task_id})
        else:
            resolved_receipt = resolve_under_work_dir(work_dir, declared_receipt_path)
            if not is_under(resolved_receipt, receipts_dir):
                errors.append({"code": "receipt_outside_receipts_dir", "task_id": task_id, "path": declared_receipt_path})
            elif not resolved_receipt.exists():
                errors.append({"code": "missing_declared_receipt", "task_id": task_id, "path": declared_receipt_path})

        task_outputs = sorted(str(item) for item in task.get("output_paths", []) if item)
        receipt_outputs = sorted(str(item) for item in receipt.get("output_paths", []) if item)
        if task_outputs != receipt_outputs:
            errors.append({"code": "receipt_output_mismatch", "task_id": task_id})
        for output in receipt_outputs:
            resolved = resolve_under_work_dir(work_dir, output)
            if not is_under(resolved, work_dir):
                errors.append({"code": "output_outside_work_dir", "task_id": task_id, "path": output})
            elif not resolved.exists():
                errors.append({"code": "missing_declared_output", "task_id": task_id, "path": output})

    expected_sources = {
        str(item["source_id"])
        for item in inventory.get("sources", [])
        if isinstance(item, dict) and item.get("source_id")
    }
    extracted_units = flatten_units(args.units_dir, errors)
    expected_topics = {
        str(item["topic_id"])
        for item in topics.get("topics", [])
        if isinstance(item, dict) and item.get("topic_id")
    }
    _, required_conflicts = load_comparison_ids(args.comparisons_dir, errors)

    role_receipts: dict[str, list[dict[str, Any]]] = {role: [] for role in ALLOWED_ROLES}
    for receipt in completed_receipts:
        role = str(receipt.get("role", ""))
        if role in role_receipts:
            role_receipts[role].append(receipt)

    if len(role_receipts["outline-planner"]) != 1:
        errors.append({"code": "outline_planner_count", "count": len(role_receipts["outline-planner"])})
    else:
        outline_sources = normalize_scope(role_receipts["outline-planner"][0].get("assigned_scope"))["source_ids"]
        add_count_coverage_errors("outline_source", expected_sources, outline_sources, errors)
    if len(role_receipts["topic-organizer"]) != 1:
        errors.append({"code": "topic_organizer_count", "count": len(role_receipts["topic-organizer"])})

    source_assignments = [
        source_id
        for receipt in role_receipts["source-analyst"]
        for source_id in normalize_scope(receipt.get("assigned_scope"))["source_ids"]
    ]
    sources_assigned_once = add_count_coverage_errors("source", expected_sources, source_assignments, errors)

    topic_assignments = [
        topic_id
        for receipt in role_receipts["topic-comparator"]
        for topic_id in normalize_scope(receipt.get("assigned_scope"))["topic_ids"]
    ]
    topics_assigned_once = add_count_coverage_errors("topic", expected_topics, topic_assignments, errors)

    conflict_assignments = [
        comparison_id
        for receipt in role_receipts["conflict-resolver"]
        for comparison_id in normalize_scope(receipt.get("assigned_scope"))["comparison_ids"]
    ]
    conflicts_assigned_once = add_count_coverage_errors("conflict", required_conflicts, conflict_assignments, errors)
    if not required_conflicts:
        skipped_conflict = any(task.get("phase") == "conflict_resolution" and task.get("status") == "skipped" for task in tasks)
        if not skipped_conflict and not role_receipts["conflict-resolver"]:
            errors.append({"code": "empty_conflict_phase_not_logged"})

    synthesizers = role_receipts["synthesizer"]
    accepted_synthesizers = [receipt for receipt in synthesizers if receipt.get("accepted_candidate") is True]
    if not synthesizers:
        errors.append({"code": "missing_synthesizer"})
    if len(accepted_synthesizers) != 1:
        errors.append({"code": "accepted_synthesizer_count", "count": len(accepted_synthesizers)})

    validators = role_receipts["validator"]
    if len(validators) < 2:
        errors.append({"code": "insufficient_validator_agents", "count": len(validators)})
    validation_assignments = [
        category
        for receipt in validators
        for category in normalize_scope(receipt.get("assigned_scope"))["validation_categories"]
    ]
    categories_covered_once = add_count_coverage_errors(
        "validation_category", REQUIRED_VALIDATION_CATEGORIES, validation_assignments, errors
    )

    if role_receipts["topic-organizer"]:
        organizer_scope = normalize_scope(role_receipts["topic-organizer"][0].get("assigned_scope"))["unit_ids"]
        add_count_coverage_errors("topic_organizer_unit", extracted_units, organizer_scope, errors)

    if len(accepted_synthesizers) == 1:
        synthesis_scope = normalize_scope(accepted_synthesizers[0].get("assigned_scope"))["unit_ids"]
        add_count_coverage_errors("synthesizer_unit", extracted_units, synthesis_scope, errors)

    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "logged_tasks": len(tasks),
            "completed_tasks": len(completed_tasks),
            "completed_subagent_receipts": len(completed_receipts),
            "inventory_sources": len(expected_sources),
            "sources_assigned_once": sources_assigned_once,
            "extracted_units": len(extracted_units),
            "topics": len(expected_topics),
            "topics_assigned_once": topics_assigned_once,
            "required_conflict_records": len(required_conflicts),
            "conflict_records_assigned_once": conflicts_assigned_once,
            "completed_synthesizers": len(synthesizers),
            "accepted_synthesizers": len(accepted_synthesizers),
            "completed_validators": len(validators),
            "validation_categories_covered_once": categories_covered_once,
        },
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(args.report), "errors": len(errors)}))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
