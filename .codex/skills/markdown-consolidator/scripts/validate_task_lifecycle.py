#!/usr/bin/env python3
"""Validate task, attempt, task-spec, receipt, and accepted-result lifecycle integrity."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from common import SCHEMA_VERSION, dump_json, is_under, json_files, load_json, resolve_under, task_spec_sha256


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate logical-task and attempt lifecycle state.")
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--require-terminal", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    work_dir = args.work_dir.resolve()
    report_path = args.report or work_dir / "task-lifecycle-report.json"
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    tasks_doc = load_json(work_dir / "task-ledger.json")
    attempts_doc = load_json(work_dir / "attempts.json")
    tasks = [item for item in tasks_doc.get("logical_tasks", []) if isinstance(item, dict)]
    attempts = [item for item in attempts_doc.get("attempts", []) if isinstance(item, dict)]

    if tasks_doc.get("execution_mode") != "subagents_required":
        errors.append({"code": "invalid_execution_mode"})
    if tasks_doc.get("fallback_used") is not False:
        errors.append({"code": "fallback_used"})

    task_ids = [str(item.get("logical_task_id", "")) for item in tasks]
    attempt_ids = [str(item.get("attempt_id", "")) for item in attempts]
    for label, values in (("logical_task", task_ids), ("attempt", attempt_ids)):
        duplicates = sorted(value for value, count in Counter(values).items() if value and count > 1)
        if duplicates:
            errors.append({"code": f"duplicate_{label}_ids", "items": duplicates})

    task_map = {str(item.get("logical_task_id")): item for item in tasks if item.get("logical_task_id")}
    attempt_map = {str(item.get("attempt_id")): item for item in attempts if item.get("attempt_id")}

    receipt_paths = json_files(work_dir / "receipts")
    receipt_ids: set[str] = set()
    for path in receipt_paths:
        try:
            receipt = load_json(path)
        except (OSError, ValueError) as exc:
            errors.append({"code": "invalid_receipt", "path": str(path), "message": str(exc)})
            continue
        attempt_id = str(receipt.get("attempt_id", ""))
        if not attempt_id:
            errors.append({"code": "receipt_missing_attempt_id", "path": str(path)})
            continue
        receipt_ids.add(attempt_id)
        if attempt_id not in attempt_map:
            errors.append({"code": "orphan_receipt", "attempt_id": attempt_id})

    for task_id, task in task_map.items():
        linked = [str(value) for value in task.get("attempt_ids", [])]
        actual = sorted(aid for aid, attempt in attempt_map.items() if attempt.get("logical_task_id") == task_id)
        if sorted(linked) != actual:
            errors.append({"code": "task_attempt_index_mismatch", "logical_task_id": task_id, "declared": sorted(linked), "actual": actual})
        accepted_id = task.get("accepted_attempt_id")
        if task.get("status") == "accepted":
            if not accepted_id or accepted_id not in attempt_map:
                errors.append({"code": "accepted_task_missing_attempt", "logical_task_id": task_id})
            elif attempt_map[accepted_id].get("status") != "accepted":
                errors.append({"code": "accepted_status_mismatch", "logical_task_id": task_id, "attempt_id": accepted_id})
        elif accepted_id:
            errors.append({"code": "nonaccepted_task_has_accepted_attempt", "logical_task_id": task_id})

    accepted_attempts = [item for item in attempts if item.get("status") == "accepted"]
    for attempt in attempts:
        attempt_id = str(attempt.get("attempt_id", ""))
        logical_id = str(attempt.get("logical_task_id", ""))
        if logical_id not in task_map:
            errors.append({"code": "attempt_unknown_logical_task", "attempt_id": attempt_id})
        status = str(attempt.get("status", ""))
        if args.require_terminal and status in {"planned", "queued", "running"}:
            errors.append({"code": "active_attempt_remains", "attempt_id": attempt_id, "status": status})
        if status in {"completed", "accepted", "superseded"}:
            spec_path = resolve_under(work_dir, str(attempt.get("task_spec_path", "")))
            receipt_path = resolve_under(work_dir, str(attempt.get("receipt_path", "")))
            if not spec_path.exists():
                errors.append({"code": "missing_task_spec", "attempt_id": attempt_id})
                continue
            if not receipt_path.exists():
                errors.append({"code": "missing_receipt", "attempt_id": attempt_id})
                continue
            if not is_under(spec_path, work_dir) or not is_under(receipt_path, work_dir):
                errors.append({"code": "attempt_artifact_outside_work_dir", "attempt_id": attempt_id})
                continue
            spec = load_json(spec_path)
            receipt = load_json(receipt_path)
            if spec.get("attempt_id") != attempt_id or receipt.get("attempt_id") != attempt_id:
                errors.append({"code": "attempt_identity_mismatch", "attempt_id": attempt_id})
            if spec.get("logical_task_id") != logical_id or receipt.get("logical_task_id") != logical_id:
                errors.append({"code": "logical_task_identity_mismatch", "attempt_id": attempt_id})
            if spec.get("nested_delegation") != "prohibited":
                errors.append({"code": "nested_delegation_not_prohibited", "attempt_id": attempt_id})
            if receipt.get("producer") != "subagent" or receipt.get("status") != "completed":
                errors.append({"code": "invalid_receipt_producer_or_status", "attempt_id": attempt_id})
            if receipt.get("task_spec_sha256") != task_spec_sha256(spec_path):
                errors.append({"code": "task_spec_hash_mismatch", "attempt_id": attempt_id})
            for output in spec.get("output_paths", []):
                resolved = resolve_under(work_dir, str(output))
                if not is_under(resolved, work_dir):
                    errors.append({"code": "output_outside_work_dir", "attempt_id": attempt_id, "path": str(output)})
                elif not resolved.exists():
                    errors.append({"code": "missing_output", "attempt_id": attempt_id, "path": str(output)})
        for input_attempt_id in attempt.get("input_attempt_ids", []):
            upstream = attempt_map.get(str(input_attempt_id))
            if not upstream or upstream.get("status") != "accepted":
                errors.append({"code": "nonaccepted_upstream_attempt", "attempt_id": attempt_id, "upstream_attempt_id": input_attempt_id})

    accepted_by_task = Counter(str(item.get("logical_task_id")) for item in accepted_attempts)
    for logical_id, count in accepted_by_task.items():
        if count != 1:
            errors.append({"code": "accepted_attempt_count", "logical_task_id": logical_id, "count": count})

    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "logical_tasks": len(tasks),
            "attempts": len(attempts),
            "accepted_attempts": len(accepted_attempts),
            "superseded_attempts": sum(1 for item in attempts if item.get("status") == "superseded"),
            "receipts": len(receipt_ids),
            "active_attempts": sum(1 for item in attempts if item.get("status") in {"planned", "queued", "running"}),
        },
    }
    dump_json(report_path, report)
    print(report["status"])
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
