#!/usr/bin/env python3
"""Validate independent stage-review coverage for accepted producer attempts."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from common import (
    SCHEMA_VERSION,
    dump_json,
    load_json,
    normalize_scope,
    resolve_under,
    task_spec_sha256,
)

BASE_REQUIRED_PRODUCER_PHASES = {
    "outline",
    "extraction",
    "topic_organization",
    "comparison",
    "conflict_resolution",
    "synthesis",
}
REPOSITORY_REQUIRED_PRODUCER_PHASES = {"placement", "integration_planning"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate accepted stage-review assignments and reports.")
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def _accepted_context(work_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    ledger = load_json(work_dir / "task-ledger.json")
    attempts_doc = load_json(work_dir / "attempts.json")
    tasks = [item for item in ledger.get("logical_tasks", []) if isinstance(item, dict)]
    attempts = [item for item in attempts_doc.get("attempts", []) if isinstance(item, dict)]
    task_map = {str(item.get("logical_task_id")): item for item in tasks if item.get("logical_task_id")}
    attempt_map = {str(item.get("attempt_id")): item for item in attempts if item.get("attempt_id")}
    return tasks, attempts, task_map, attempt_map


def evaluate_reviews(work_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    tasks, attempts, task_map, attempt_map = _accepted_context(work_dir)

    accepted: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    for logical_id, task in task_map.items():
        if task.get("status") != "accepted" or not task.get("accepted_attempt_id"):
            continue
        attempt_id = str(task["accepted_attempt_id"])
        attempt = attempt_map.get(attempt_id)
        if not attempt or attempt.get("status") != "accepted":
            continue
        spec_path = resolve_under(work_dir, str(attempt.get("task_spec_path", "")))
        receipt_path = resolve_under(work_dir, str(attempt.get("receipt_path", "")))
        if not spec_path.exists() or not receipt_path.exists():
            continue
        spec = load_json(spec_path)
        receipt = load_json(receipt_path)
        if receipt.get("task_spec_sha256") != task_spec_sha256(spec_path):
            continue
        accepted.append((task, attempt, spec))

    runtime_plan_path = work_dir / "runtime-plan.json"
    publication_mode = "standalone"
    if runtime_plan_path.exists():
        publication_mode = str(load_json(runtime_plan_path).get("publication_mode", "standalone"))
    required_phases = set(BASE_REQUIRED_PRODUCER_PHASES)
    if publication_mode == "repository_integrated":
        required_phases.update(REPOSITORY_REQUIRED_PRODUCER_PHASES)

    producers = [
        (task, attempt, spec)
        for task, attempt, spec in accepted
        if str(spec.get("phase")) in required_phases
        and str(spec.get("role")) != "stage-reviewer"
    ]
    reviews = [
        (task, attempt, spec)
        for task, attempt, spec in accepted
        if str(spec.get("phase")) == "stage_review"
    ]

    expected_ids = {str(attempt["attempt_id"]) for _, attempt, _ in producers}
    assignments: list[str] = []
    passed_review_count = 0

    producer_threads = {
        str(attempt["attempt_id"]): attempt.get("runtime_thread_id")
        for _, attempt, _ in producers
    }

    for task, attempt, spec in reviews:
        attempt_id = str(attempt.get("attempt_id"))
        if spec.get("role") != "stage-reviewer":
            errors.append({"code": "review_role_mismatch", "attempt_id": attempt_id, "role": spec.get("role")})
            continue
        scope = normalize_scope(spec.get("assigned_scope"))
        reviewed_ids = scope["reviewed_attempt_ids"]
        if not reviewed_ids:
            errors.append({"code": "empty_review_scope", "attempt_id": attempt_id})
            continue
        assignments.extend(reviewed_ids)
        unknown = sorted(set(reviewed_ids) - expected_ids)
        if unknown:
            errors.append({"code": "unknown_review_targets", "attempt_id": attempt_id, "attempt_ids": unknown})
        input_ids = {str(value) for value in attempt.get("input_attempt_ids", [])}
        if not set(reviewed_ids).issubset(input_ids):
            errors.append({"code": "review_inputs_missing_targets", "attempt_id": attempt_id, "reviewed_attempt_ids": reviewed_ids})
        review_thread = attempt.get("runtime_thread_id")
        if review_thread is not None:
            same_thread = [target for target in reviewed_ids if producer_threads.get(target) is not None and producer_threads[target] == review_thread]
            if same_thread:
                errors.append({"code": "review_not_independent_thread", "attempt_id": attempt_id, "producer_attempt_ids": same_thread})

        output_paths = [resolve_under(work_dir, str(path)) for path in spec.get("output_paths", [])]
        report_paths = [path for path in output_paths if path.suffix.lower() == ".json" and path.exists()]
        if len(report_paths) != 1:
            errors.append({"code": "review_report_count", "attempt_id": attempt_id, "count": len(report_paths)})
            continue
        report = load_json(report_paths[0])
        report_ids = sorted({str(value) for value in report.get("reviewed_attempt_ids", [])})
        if report_ids != reviewed_ids:
            errors.append({"code": "review_report_scope_mismatch", "attempt_id": attempt_id, "expected": reviewed_ids, "actual": report_ids})
        if report.get("status") != "passed":
            errors.append({"code": "review_report_failed", "attempt_id": attempt_id, "report": str(report_paths[0])})
        else:
            passed_review_count += 1

    counts = Counter(assignments)
    missing = sorted(expected_ids - set(counts))
    duplicated = sorted(target for target in expected_ids if counts[target] != 1)
    unknown_assignments = sorted(set(counts) - expected_ids)
    if missing:
        errors.append({"code": "missing_stage_reviews", "attempt_ids": missing})
    if duplicated:
        errors.append({"code": "nonexact_stage_review_coverage", "attempt_ids": duplicated})
    if unknown_assignments:
        errors.append({"code": "unknown_stage_review_assignments", "attempt_ids": unknown_assignments})

    metrics = {
        "required_producer_attempts": len(expected_ids),
        "reviewed_once": sum(1 for target in expected_ids if counts[target] == 1),
        "accepted_review_attempts": len(reviews),
        "passed_review_reports": passed_review_count,
        "producer_attempt_ids": sorted(expected_ids),
    }
    return errors, warnings, metrics


def main() -> int:
    args = parse_args()
    errors, warnings, metrics = evaluate_reviews(args.work_dir.resolve())
    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "warnings": warnings,
        "metrics": metrics,
    }
    dump_json(args.report, report)
    print(report["status"])
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
