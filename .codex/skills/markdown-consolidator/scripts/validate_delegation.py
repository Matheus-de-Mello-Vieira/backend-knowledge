#!/usr/bin/env python3
"""Validate accepted subagent assignments and mode-specific phase coverage."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from common import (
    SCHEMA_VERSION,
    comparison_records,
    dump_json,
    is_under,
    load_json,
    normalize_scope,
    resolve_under,
    task_spec_sha256,
    unit_records,
)
from validate_reviews import evaluate_reviews

BASE_VALIDATION_CATEGORIES = {
    "coverage",
    "conflicts_qualifiers",
    "standalone_exposition",
    "coherence_markdown",
    "writing_quality",
}
REPOSITORY_VALIDATION_CATEGORIES = {"repository_integration", "link_context"}
ALLOWED_PUBLICATION_ROLES = {"synthesizer", "publication-finalizer"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate mandatory delegated execution using accepted attempts only.")
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--units-dir", type=Path, required=True)
    parser.add_argument("--topics", type=Path, required=True)
    parser.add_argument("--comparisons-dir", type=Path, required=True)
    parser.add_argument("--comparison-index", type=Path, required=True)
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--placement", type=Path)
    parser.add_argument("--integration-plan", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def add_exact_coverage(label: str, expected: set[str], assignments: list[str], errors: list[dict[str, Any]]) -> int:
    counts = Counter(assignments)
    missing = sorted(expected - set(counts))
    unknown = sorted(set(counts) - expected)
    nonexact = sorted(value for value in expected if counts[value] != 1)
    if missing:
        errors.append({"code": f"missing_{label}_assignments", "items": missing})
    if unknown:
        errors.append({"code": f"unknown_{label}_assignments", "items": unknown})
    if nonexact:
        errors.append({"code": f"nonexact_{label}_assignments", "items": nonexact})
    return sum(1 for value in expected if counts[value] == 1)


def main() -> int:
    args = parse_args()
    work_dir = args.work_dir.resolve()
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    ledger = load_json(work_dir / "task-ledger.json")
    attempts_doc = load_json(work_dir / "attempts.json")
    runtime_plan = load_json(work_dir / "runtime-plan.json") if (work_dir / "runtime-plan.json").exists() else {}
    publication_mode = str(runtime_plan.get("publication_mode", "standalone"))
    inventory = load_json(args.inventory)
    topics_doc = load_json(args.topics)
    comparison_index = load_json(args.comparison_index)
    _ = load_json(args.decisions)
    units, _ = unit_records(args.units_dir)
    comparisons, _ = comparison_records(args.comparisons_dir)

    if publication_mode not in {"standalone", "repository_integrated"}:
        errors.append({"code": "invalid_publication_mode", "value": publication_mode})
    if ledger.get("execution_mode") != "subagents_required":
        errors.append({"code": "invalid_execution_mode"})
    if ledger.get("fallback_used") is not False:
        errors.append({"code": "fallback_used"})

    tasks = [item for item in ledger.get("logical_tasks", []) if isinstance(item, dict)]
    attempts = [item for item in attempts_doc.get("attempts", []) if isinstance(item, dict)]
    task_map = {str(item.get("logical_task_id")): item for item in tasks if item.get("logical_task_id")}
    attempt_map = {str(item.get("attempt_id")): item for item in attempts if item.get("attempt_id")}
    accepted_attempts: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = []

    for logical_id, task in task_map.items():
        if task.get("status") == "skipped":
            continue
        accepted_id = task.get("accepted_attempt_id")
        if task.get("status") != "accepted" or not accepted_id:
            errors.append({"code": "logical_task_not_accepted", "logical_task_id": logical_id, "status": task.get("status")})
            continue
        attempt = attempt_map.get(str(accepted_id))
        if not attempt or attempt.get("status") != "accepted":
            errors.append({"code": "accepted_attempt_missing_or_invalid", "logical_task_id": logical_id, "attempt_id": accepted_id})
            continue
        spec_path = resolve_under(work_dir, str(attempt.get("task_spec_path", "")))
        receipt_path = resolve_under(work_dir, str(attempt.get("receipt_path", "")))
        if not spec_path.exists() or not receipt_path.exists():
            errors.append({"code": "accepted_attempt_artifact_missing", "attempt_id": accepted_id})
            continue
        spec = load_json(spec_path)
        receipt = load_json(receipt_path)
        if spec.get("nested_delegation") != "prohibited":
            errors.append({"code": "nested_delegation_not_prohibited", "attempt_id": accepted_id})
        if receipt.get("producer") != "subagent" or receipt.get("status") != "completed":
            errors.append({"code": "invalid_accepted_receipt", "attempt_id": accepted_id})
        if receipt.get("task_spec_sha256") != task_spec_sha256(spec_path):
            errors.append({"code": "task_spec_hash_mismatch", "attempt_id": accepted_id})
        if receipt.get("attempt_id") != accepted_id or receipt.get("logical_task_id") != logical_id:
            errors.append({"code": "accepted_identity_mismatch", "attempt_id": accepted_id})
        for output in spec.get("output_paths", []):
            resolved = resolve_under(work_dir, str(output))
            if not is_under(resolved, work_dir) or not resolved.exists():
                errors.append({"code": "accepted_output_missing_or_outside_work_dir", "attempt_id": accepted_id, "path": str(output)})
        accepted_attempts.append((task, attempt, spec))

    active = [item.get("attempt_id") for item in attempts if item.get("status") in {"planned", "queued", "running", "completed"}]
    if active:
        errors.append({"code": "nonterminal_or_unreconciled_attempts", "attempt_ids": active})

    expected_sources = {
        str(item["source_id"])
        for item in inventory.get("sources", [])
        if isinstance(item, dict) and item.get("source_id")
    }
    expected_units = set(units)
    expected_topics = {
        str(item["topic_id"])
        for item in topics_doc.get("topics", [])
        if isinstance(item, dict) and item.get("topic_id")
    }
    required_resolution = set(map(str, comparison_index.get("required_resolution_ids", [])))

    placement_paths: set[str] = set()
    if publication_mode == "repository_integrated":
        placement_path = args.placement or work_dir / "placement-plan.json"
        if not placement_path.exists():
            errors.append({"code": "placement_plan_missing"})
        else:
            placement = load_json(placement_path)
            placement_paths = {
                str(item.get("path")) for item in placement.get("destinations", [])
                if isinstance(item, dict) and item.get("path")
            }
        placement_attempts = [(t, a, s) for t, a, s in accepted_attempts if s.get("phase") == "placement"]
        if len(placement_attempts) != 1 or placement_attempts[0][2].get("role") != "note-home-finder-adapter":
            errors.append({"code": "placement_assignment_count", "count": len(placement_attempts)})
        elif set(normalize_scope(placement_attempts[0][2].get("assigned_scope"))["source_ids"]) != expected_sources:
            errors.append({"code": "placement_source_scope_mismatch"})
    else:
        if any(spec.get("phase") in {"placement", "integration_planning"} for _, _, spec in accepted_attempts):
            errors.append({"code": "repository_stage_present_in_standalone_mode"})

    outline_attempts = [(t, a, s) for t, a, s in accepted_attempts if s.get("phase") == "outline"]
    if len(outline_attempts) != 1 or outline_attempts[0][2].get("role") != "outline-planner":
        errors.append({"code": "outline_assignment_count", "count": len(outline_attempts)})
    elif set(normalize_scope(outline_attempts[0][2].get("assigned_scope"))["source_ids"]) != expected_sources:
        errors.append({"code": "outline_source_scope_mismatch"})

    extraction_assignments: list[str] = []
    for _, _, spec in accepted_attempts:
        if spec.get("phase") == "extraction":
            if spec.get("role") != "source-analyst":
                errors.append({"code": "extraction_role_mismatch", "attempt_id": spec.get("attempt_id")})
            extraction_assignments.extend(normalize_scope(spec.get("assigned_scope"))["source_ids"])
    sources_exact = add_exact_coverage("source", expected_sources, extraction_assignments, errors)

    organizers = [(t, a, s) for t, a, s in accepted_attempts if s.get("phase") == "topic_organization"]
    if len(organizers) != 1 or organizers[0][2].get("role") != "topic-organizer":
        errors.append({"code": "topic_organizer_assignment_count", "count": len(organizers)})
    elif set(normalize_scope(organizers[0][2].get("assigned_scope"))["unit_ids"]) != expected_units:
        errors.append({"code": "topic_organizer_unit_scope_mismatch"})

    comparison_assignments: list[str] = []
    for _, _, spec in accepted_attempts:
        if spec.get("phase") == "comparison":
            if spec.get("role") != "topic-comparator":
                errors.append({"code": "comparison_role_mismatch", "attempt_id": spec.get("attempt_id")})
            comparison_assignments.extend(normalize_scope(spec.get("assigned_scope"))["topic_ids"])
    topics_exact = add_exact_coverage("topic", expected_topics, comparison_assignments, errors)

    resolution_assignments: list[str] = []
    accepted_resolution_attempts = 0
    for _, _, spec in accepted_attempts:
        if spec.get("phase") == "conflict_resolution":
            accepted_resolution_attempts += 1
            if spec.get("role") != "conflict-resolver":
                errors.append({"code": "conflict_role_mismatch", "attempt_id": spec.get("attempt_id")})
            resolution_assignments.extend(normalize_scope(spec.get("assigned_scope"))["comparison_ids"])
    skipped_resolution_tasks = [task for task in tasks if task.get("phase") == "conflict_resolution" and task.get("status") == "skipped"]
    if required_resolution:
        if skipped_resolution_tasks:
            errors.append({"code": "conflict_phase_skipped_with_required_scope"})
    else:
        if accepted_resolution_attempts:
            errors.append({"code": "conflict_attempts_with_empty_required_scope"})
        if len(skipped_resolution_tasks) != 1:
            errors.append({"code": "empty_conflict_phase_requires_one_skipped_task", "count": len(skipped_resolution_tasks)})
    conflicts_exact = add_exact_coverage("conflict", required_resolution, resolution_assignments, errors)

    if publication_mode == "repository_integrated":
        integration_path = args.integration_plan or work_dir / "integration-plan.json"
        if not integration_path.exists():
            errors.append({"code": "integration_plan_missing"})
        integrators = [(t, a, s) for t, a, s in accepted_attempts if s.get("phase") == "integration_planning"]
        if len(integrators) != 1 or integrators[0][2].get("role") != "integration-planner":
            errors.append({"code": "integration_planner_assignment_count", "count": len(integrators)})
        else:
            scope = normalize_scope(integrators[0][2].get("assigned_scope"))
            if set(scope["unit_ids"]) != expected_units:
                errors.append({"code": "integration_planner_unit_scope_mismatch"})
            if set(scope["destination_paths"]) != placement_paths:
                errors.append({"code": "integration_planner_destination_scope_mismatch"})

    publication_tasks = [task for task in tasks if task.get("phase") == "synthesis" and task.get("logical_task_id") == "publication"]
    publication_accepted = [(task, attempt, spec) for task, attempt, spec in accepted_attempts if task.get("logical_task_id") == "publication"]
    if len(publication_tasks) != 1 or len(publication_accepted) != 1:
        errors.append({"code": "publication_lineage_count", "logical_tasks": len(publication_tasks), "accepted_attempts": len(publication_accepted)})
    else:
        _, _, publication_spec = publication_accepted[0]
        if publication_spec.get("role") not in ALLOWED_PUBLICATION_ROLES:
            errors.append({"code": "invalid_publication_role", "role": publication_spec.get("role")})
        scope = normalize_scope(publication_spec.get("assigned_scope"))
        if set(scope["unit_ids"]) != expected_units:
            errors.append({"code": "publication_full_unit_scope_mismatch"})
        if publication_mode == "repository_integrated" and set(scope["publication_paths"]) != placement_paths:
            errors.append({"code": "publication_full_destination_scope_mismatch"})

    required_categories = set(BASE_VALIDATION_CATEGORIES)
    if publication_mode == "repository_integrated":
        required_categories.update(REPOSITORY_VALIDATION_CATEGORIES)
    validation_assignments: list[str] = []
    validator_count = 0
    for _, _, spec in accepted_attempts:
        if spec.get("phase") == "semantic_validation":
            validator_count += 1
            if spec.get("role") != "validator":
                errors.append({"code": "validator_role_mismatch", "attempt_id": spec.get("attempt_id")})
            validation_assignments.extend(normalize_scope(spec.get("assigned_scope"))["validation_categories"])
    categories_exact = add_exact_coverage("validation_category", required_categories, validation_assignments, errors)
    if validator_count < 2:
        errors.append({"code": "insufficient_validator_agents", "count": validator_count})

    review_errors, review_warnings, review_metrics = evaluate_reviews(work_dir)
    errors.extend({"code": "stage_review_validation", "detail": item} for item in review_errors)
    warnings.extend({"code": "stage_review_warning", "detail": item} for item in review_warnings)

    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "publication_mode": publication_mode,
            "logical_tasks": len(tasks),
            "attempts": len(attempts),
            "accepted_attempts": len(accepted_attempts),
            "superseded_attempts": sum(1 for item in attempts if item.get("status") == "superseded"),
            "inventory_sources": len(expected_sources),
            "sources_assigned_once": sources_exact,
            "units": len(expected_units),
            "topics": len(expected_topics),
            "topics_assigned_once": topics_exact,
            "comparison_records": len(comparisons),
            "required_conflict_records": len(required_resolution),
            "conflict_records_assigned_once": conflicts_exact,
            "destination_notes": len(placement_paths),
            "accepted_publication_attempts": len(publication_accepted),
            "completed_validators": validator_count,
            "validation_categories_covered": categories_exact,
            "required_stage_reviews": review_metrics.get("required_producer_attempts", 0),
            "producer_attempts_reviewed_once": review_metrics.get("reviewed_once", 0),
            "accepted_stage_review_attempts": review_metrics.get("accepted_review_attempts", 0),
        },
    }
    dump_json(args.report, report)
    print(report["status"])
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
