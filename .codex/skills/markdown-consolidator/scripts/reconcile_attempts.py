#!/usr/bin/env python3
"""Reconcile immutable task attempts into one accepted result per logical task."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from common import SCHEMA_VERSION, dump_json, is_under, load_json, resolve_under, task_spec_sha256

TERMINAL = {"completed", "failed", "cancelled", "accepted", "superseded"}
SUCCESS = {"completed", "accepted", "superseded"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Accept one valid attempt per logical task and supersede older results.")
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def attempt_number(attempt: dict[str, Any]) -> int:
    value = attempt.get("attempt_number", 0)
    return value if isinstance(value, int) else 0


def validate_candidate(work_dir: Path, attempt: dict[str, Any]) -> tuple[bool, list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    attempt_id = str(attempt.get("attempt_id", ""))
    spec_path = resolve_under(work_dir, str(attempt.get("task_spec_path", "")))
    receipt_path = resolve_under(work_dir, str(attempt.get("receipt_path", "")))
    if not spec_path.exists():
        errors.append({"code": "missing_task_spec", "attempt_id": attempt_id, "path": str(spec_path)})
        return False, errors
    if not receipt_path.exists():
        errors.append({"code": "missing_receipt", "attempt_id": attempt_id, "path": str(receipt_path)})
        return False, errors
    if not is_under(spec_path, work_dir) or not is_under(receipt_path, work_dir):
        errors.append({"code": "artifact_outside_work_dir", "attempt_id": attempt_id})
        return False, errors
    try:
        spec = load_json(spec_path)
        receipt = load_json(receipt_path)
    except (OSError, ValueError) as exc:
        errors.append({"code": "invalid_attempt_artifact", "attempt_id": attempt_id, "message": str(exc)})
        return False, errors
    expected_hash = task_spec_sha256(spec_path)
    checks = {
        "attempt_id": receipt.get("attempt_id") == attempt_id == spec.get("attempt_id"),
        "logical_task_id": receipt.get("logical_task_id") == attempt.get("logical_task_id") == spec.get("logical_task_id"),
        "producer": receipt.get("producer") == "subagent",
        "receipt_status": receipt.get("status") == "completed",
        "task_spec_sha256": receipt.get("task_spec_sha256") == expected_hash,
        "nested_delegation": spec.get("nested_delegation") == "prohibited",
    }
    for field, ok in checks.items():
        if not ok:
            errors.append({"code": "attempt_contract_mismatch", "attempt_id": attempt_id, "field": field})
    for output in spec.get("output_paths", []):
        resolved = resolve_under(work_dir, str(output))
        if not is_under(resolved, work_dir):
            errors.append({"code": "output_outside_work_dir", "attempt_id": attempt_id, "path": str(output)})
        elif not resolved.exists():
            errors.append({"code": "missing_output", "attempt_id": attempt_id, "path": str(output)})
    return not errors, errors


def main() -> int:
    args = parse_args()
    work_dir = args.work_dir.resolve()
    tasks_path = work_dir / "task-ledger.json"
    attempts_path = work_dir / "attempts.json"
    report_path = args.report or work_dir / "reconciliation-report.json"
    tasks_doc = load_json(tasks_path)
    attempts_doc = load_json(attempts_path)
    tasks = tasks_doc.get("logical_tasks", [])
    attempts = attempts_doc.get("attempts", [])
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    attempt_by_id = {str(item.get("attempt_id")): item for item in attempts if isinstance(item, dict) and item.get("attempt_id")}
    if len(attempt_by_id) != len([item for item in attempts if isinstance(item, dict) and item.get("attempt_id")]):
        errors.append({"code": "duplicate_attempt_ids"})

    accepted_count = 0
    for task in tasks:
        if not isinstance(task, dict) or not task.get("logical_task_id"):
            errors.append({"code": "invalid_logical_task"})
            continue
        logical_id = str(task["logical_task_id"])
        if task.get("status") == "skipped":
            if task.get("accepted_attempt_id"):
                errors.append({"code": "skipped_task_has_accepted_attempt", "logical_task_id": logical_id})
            continue
        task_attempts = [attempt_by_id[aid] for aid in task.get("attempt_ids", []) if aid in attempt_by_id]
        missing_ids = sorted(set(map(str, task.get("attempt_ids", []))) - set(attempt_by_id))
        if missing_ids:
            errors.append({"code": "missing_attempt_records", "logical_task_id": logical_id, "attempt_ids": missing_ids})
        valid: list[dict[str, Any]] = []
        for attempt in task_attempts:
            if attempt.get("logical_task_id") != logical_id:
                errors.append({"code": "attempt_wrong_logical_task", "attempt_id": attempt.get("attempt_id")})
                continue
            if attempt.get("status") not in SUCCESS:
                continue
            ok, candidate_errors = validate_candidate(work_dir, attempt)
            if ok:
                valid.append(attempt)
            else:
                errors.extend(candidate_errors)

        preferred_id = task.get("preferred_attempt_id")
        chosen: dict[str, Any] | None = None
        if preferred_id:
            chosen = next((item for item in valid if item.get("attempt_id") == preferred_id), None)
            if not chosen:
                errors.append({"code": "invalid_preferred_attempt", "logical_task_id": logical_id, "attempt_id": preferred_id})
        elif valid:
            chosen = sorted(valid, key=lambda item: (attempt_number(item), str(item.get("completed_at", ""))))[-1]

        if chosen:
            chosen_id = str(chosen["attempt_id"])
            for attempt in task_attempts:
                status = attempt.get("status")
                if attempt.get("attempt_id") == chosen_id:
                    attempt["status"] = "accepted"
                elif status in SUCCESS:
                    attempt["status"] = "superseded"
            task["accepted_attempt_id"] = chosen_id
            task["status"] = "accepted"
            accepted_count += 1
        else:
            active = any(item.get("status") in {"planned", "queued", "running"} for item in task_attempts)
            task["accepted_attempt_id"] = None
            task["status"] = "running" if active else "failed"
            if not active:
                errors.append({"code": "logical_task_has_no_valid_attempt", "logical_task_id": logical_id})

    tasks_doc["schema_version"] = SCHEMA_VERSION
    attempts_doc["schema_version"] = SCHEMA_VERSION
    dump_json(tasks_path, tasks_doc)
    dump_json(attempts_path, attempts_doc)
    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "logical_tasks": len(tasks),
            "attempts": len(attempts),
            "accepted_logical_tasks": accepted_count,
            "superseded_attempts": sum(1 for item in attempts if isinstance(item, dict) and item.get("status") == "superseded"),
        },
    }
    dump_json(report_path, report)
    print(report["status"])
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
