#!/usr/bin/env python3
"""Smoke tests for lifecycle, materialization, content, and delegation validation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS))
from common import SCHEMA_VERSION, dump_json, task_spec_sha256  # noqa: E402


def run(*args: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, text=True, capture_output=True)
    if result.returncode != expect:
        raise AssertionError(
            f"Command returned {result.returncode}, expected {expect}: {' '.join(args)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def write_task(work: Path, logical_id: str, attempt_id: str, phase: str, role: str, scope: dict, outputs: list[str], input_attempt_ids: list[str] | None = None) -> tuple[dict, dict]:
    spec = {
        "schema_version": SCHEMA_VERSION,
        "attempt_id": attempt_id,
        "logical_task_id": logical_id,
        "phase": phase,
        "role": role,
        "nested_delegation": "prohibited",
        "assigned_scope": scope,
        "input_paths": [],
        "output_paths": outputs,
        "receipt_path": f"receipts/{attempt_id}.json",
        "created_at": "2026-08-04T00:00:00Z",
    }
    spec_path = work / "task-specs" / f"{attempt_id}.json"
    dump_json(spec_path, spec)
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "attempt_id": attempt_id,
        "logical_task_id": logical_id,
        "producer": "subagent",
        "status": "completed",
        "task_spec_sha256": task_spec_sha256(spec_path),
        "completed_scope": {},
        "output_paths": outputs,
        "warnings": [],
        "completed_at": "2026-08-04T00:01:00Z",
    }
    dump_json(work / "receipts" / f"{attempt_id}.json", receipt)
    task = {
        "logical_task_id": logical_id,
        "phase": phase,
        "allowed_roles": [role],
        "status": "accepted",
        "attempt_ids": [attempt_id],
        "preferred_attempt_id": None,
        "accepted_attempt_id": attempt_id,
        "skip_reason": None,
    }
    attempt = {
        "attempt_id": attempt_id,
        "logical_task_id": logical_id,
        "attempt_number": 1,
        "status": "accepted",
        "task_spec_path": f"task-specs/{attempt_id}.json",
        "receipt_path": f"receipts/{attempt_id}.json",
        "output_paths": outputs,
        "input_attempt_ids": input_attempt_ids or [],
        "replaces_attempt_id": None,
        "runtime_thread_id": None,
        "started_at": "2026-08-04T00:00:00Z",
        "completed_at": "2026-08-04T00:01:00Z",
    }
    return task, attempt



def test_package_structure() -> None:
    references = SKILL_DIR / "references"
    removed = {
        "task-lifecycle.md",
        "delegation-protocol.md",
        "retry-and-supersession.md",
        "synthesis-repair-protocol.md",
    }
    assert not any((references / name).exists() for name in removed)
    for required in (
        references / "execution-protocol.md",
        references / "review-protocol.md",
        references / "companion-skills.md",
        references / "repository-integration.md",
        references / "agents" / "stage-reviewer.md",
        references / "agents" / "note-home-finder-adapter.md",
        references / "agents" / "integration-planner.md",
        SCRIPTS / "validate_reviews.py",
        SCRIPTS / "locate_companion_skills.py",
        SCRIPTS / "validate_placement.py",
        SCRIPTS / "validate_integration_plan.py",
        SCRIPTS / "materialize_publication_set.py",
        SCRIPTS / "run_link_pipeline.py",
        SCRIPTS / "validate_repository_integration.py",
    ):
        assert required.exists(), required
    for role_file in (references / "agents").glob("*.md"):
        text = role_file.read_text(encoding="utf-8")
        assert "## Execution boundary" not in text, role_file
        assert "Do not spawn, delegate to, or request another agent" not in text, role_file


def test_complete_fixture(root: Path) -> None:
    source_root = root / "sources"
    work = root / "output" / ".markdown-consolidator-work"
    source_root.mkdir(parents=True)
    work.mkdir(parents=True)
    (work / "units").mkdir()
    (work / "comparisons").mkdir()
    (work / "drafts").mkdir()
    (work / "task-specs").mkdir()
    (work / "receipts").mkdir()
    (work / "validation").mkdir()
    (work / "reviews").mkdir()

    source = source_root / "learning.md"
    source.write_text(
        "# Learning Modes\n"
        "A learner receives lessons remotely and completes activities later in the day.\n"
        "This separates delivery location from participation timing.\n",
        encoding="utf-8",
    )
    run(
        sys.executable,
        str(SCRIPTS / "inventory_markdown.py"),
        str(source_root),
        "--output",
        str(work / "inventory.json"),
    )
    inventory = json.loads((work / "inventory.json").read_text())
    source_id = inventory["sources"][0]["source_id"]
    heading_id = f"{source_id}-u0001"
    example_id = f"{source_id}-u0002"

    units = {
        "schema_version": SCHEMA_VERSION,
        "batch_id": "extract-001-attempt-1",
        "sources": [source_id],
        "units": [
            {
                "unit_id": heading_id,
                "source_id": source_id,
                "source_path": "learning.md",
                "heading_path": ["Learning Modes"],
                "source_range": {"start": 1, "end": 1},
                "unit_type": "heading",
                "source_text": "# Learning Modes",
                "normalized_claim": "Learning Modes",
                "topic_hint": "learning-modes",
                "assertion_kind": "structure",
                "qualifiers": {"versions": [], "dates": [], "platforms": [], "environments": [], "configurations": [], "roles": [], "other": []},
                "confidence": 1.0,
                "warnings": [],
            },
            {
                "unit_id": example_id,
                "source_id": source_id,
                "source_path": "learning.md",
                "heading_path": ["Learning Modes"],
                "source_range": {"start": 2, "end": 3},
                "unit_type": "example",
                "source_text": "A learner receives lessons remotely and completes activities later in the day.\nThis separates delivery location from participation timing.",
                "normalized_claim": "Remote delivery and participation timing are separate dimensions.",
                "topic_hint": "learning-modes",
                "assertion_kind": "example",
                "qualifiers": {"versions": [], "dates": [], "platforms": [], "environments": [], "configurations": [], "roles": [], "other": []},
                "confidence": 1.0,
                "warnings": [],
            },
        ],
        "covered_line_ranges": [{"source_id": source_id, "range": {"start": 1, "end": 3}}],
        "uncovered_nonempty_lines": [],
        "warnings": [],
    }
    dump_json(work / "units" / "extract-001-attempt-1.json", units)
    run(
        sys.executable,
        str(SCRIPTS / "validate_units.py"),
        "--inventory",
        str(work / "inventory.json"),
        "--units-dir",
        str(work / "units"),
        "--index",
        str(work / "units" / "index.json"),
        "--report",
        str(work / "units" / "validation-report.json"),
    )

    outline = {
        "schema_version": SCHEMA_VERSION,
        "title": "Learning Modes",
        "audience": "General reader",
        "scope": "Complete informational union",
        "sections": [{"section_id": "learning-modes", "heading": "Learning Modes", "purpose": "Explain the example", "source_topic_hints": ["learning-modes"]}],
        "fallback_sections": [],
    }
    dump_json(work / "outline.json", outline)
    topics = {
        "schema_version": SCHEMA_VERSION,
        "topics": [{"topic_id": "learning-modes", "canonical_name": "Learning Modes", "aliases": [], "unit_ids": [heading_id, example_id], "cross_topic_unit_ids": [], "ambiguous_unit_ids": []}],
    }
    dump_json(work / "topics.json", topics)
    run(sys.executable, str(SCRIPTS / "validate_topics.py"), "--unit-index", str(work / "units" / "index.json"), "--topics", str(work / "topics.json"), "--report", str(work / "topic-validation-report.json"))

    comparisons = {
        "schema_version": SCHEMA_VERSION,
        "batch_id": "compare-001-attempt-1",
        "assigned_topic_ids": ["learning-modes"],
        "assigned_unit_ids": [heading_id, example_id],
        "records": [
            {"comparison_id": "cmp-001", "topic_id": "learning-modes", "unit_ids": [heading_id], "relationship": "unique", "semantic_union": ["Learning Modes heading"], "rationale": "Unique structural unit", "recommended_action": "represented_by_structure", "confidence": 1.0},
            {"comparison_id": "cmp-002", "topic_id": "learning-modes", "unit_ids": [example_id], "relationship": "unique", "semantic_union": ["Remote delivery and timing example"], "rationale": "Unique example", "recommended_action": "included_directly", "confidence": 1.0},
        ],
        "accounted_unit_ids": [heading_id, example_id],
        "warnings": [],
    }
    dump_json(work / "comparisons" / "compare-001-attempt-1.json", comparisons)
    run(sys.executable, str(SCRIPTS / "validate_comparisons.py"), "--topics", str(work / "topics.json"), "--comparisons-dir", str(work / "comparisons"), "--index", str(work / "comparisons" / "index.json"), "--report", str(work / "comparisons" / "validation-report.json"))
    decisions = {"schema_version": SCHEMA_VERSION, "decisions": []}
    dump_json(work / "decision-ledger.json", decisions)
    run(sys.executable, str(SCRIPTS / "validate_decisions.py"), "--comparisons-dir", str(work / "comparisons"), "--comparison-index", str(work / "comparisons" / "index.json"), "--decisions", str(work / "decision-ledger.json"), "--report", str(work / "decision-validation-report.json"))

    annotated = work / "drafts" / "annotated-publication-attempt-1.md"
    annotated.write_text(
        "# Learning Modes\n\n"
        f"<!-- MC:BEGIN {example_id} detail -->\n"
        "A learner receives lessons remotely and completes activities later in the day.\n"
        f"<!-- MC:END {example_id} detail -->\n\n"
        f"<!-- MC:BEGIN {example_id} explanation -->\n"
        "This separates delivery location from participation timing: remote instruction does not require synchronous participation.\n"
        f"<!-- MC:END {example_id} explanation -->\n",
        encoding="utf-8",
    )
    dispositions = {
        "schema_version": SCHEMA_VERSION,
        "document_revision": "publication-attempt-1",
        "unit_dispositions": [
            {"unit_id": heading_id, "disposition": "represented_by_structure", "final_section_id": "learning-modes", "notes": None},
            {"unit_id": example_id, "disposition": "included_directly", "final_section_id": "learning-modes", "notes": None},
        ],
    }
    dump_json(work / "unit-dispositions-publication-attempt-1.json", dispositions)
    candidate = work / "drafts" / "candidate-publication-attempt-1.md"
    run(
        sys.executable,
        str(SCRIPTS / "materialize_publication.py"),
        "--annotated",
        str(annotated),
        "--dispositions",
        str(work / "unit-dispositions-publication-attempt-1.json"),
        "--units-dir",
        str(work / "units"),
        "--output-document",
        str(candidate),
        "--coverage-map",
        str(work / "coverage-map.json"),
        "--report",
        str(work / "materialization-report.json"),
    )
    run(sys.executable, str(SCRIPTS / "validate_consolidation.py"), "--document", str(candidate), "--inventory", str(work / "inventory.json"), "--units-dir", str(work / "units"), "--coverage-map", str(work / "coverage-map.json"), "--decisions", str(work / "decision-ledger.json"), "--report", str(work / "validation-report.json"))
    run(sys.executable, str(SCRIPTS / "validate_writing.py"), "--document", str(candidate), "--report", str(work / "writing-validation-report.json"))

    # The exact user-observed failure must be rejected.
    bad = work / "drafts" / "bad.md"
    bad.write_text(candidate.read_text() + "\nThe distance-learning example in the material shows the logic.\n", encoding="utf-8")
    run(sys.executable, str(SCRIPTS / "validate_consolidation.py"), "--document", str(bad), "--inventory", str(work / "inventory.json"), "--units-dir", str(work / "units"), "--coverage-map", str(work / "coverage-map.json"), "--decisions", str(work / "decision-ledger.json"), "--report", str(work / "bad-validation-report.json"), expect=2)

    vague = work / "drafts" / "vague.md"
    vague.write_text(candidate.read_text() + "\nThe process should be handled appropriately.\n", encoding="utf-8")
    run(sys.executable, str(SCRIPTS / "validate_writing.py"), "--document", str(vague), "--report", str(work / "vague-writing-report.json"), expect=2)

    # Create accepted delegation state.
    (work / "validation" / "validate-a.json").write_text('{"status":"passed"}\n')
    (work / "validation" / "validate-b.json").write_text('{"status":"passed"}\n')
    tasks = []
    attempts = []
    empty_scope = {"source_ids": [], "topic_ids": [], "comparison_ids": [], "decision_ids": [], "unit_ids": [], "validation_categories": [], "reviewed_attempt_ids": [], "review_categories": []}
    task_specs = [
        ("outline", "outline-attempt-1", "outline", "outline-planner", {**empty_scope, "source_ids": [source_id]}, ["outline.json"]),
        ("extract-001", "extract-001-attempt-1", "extraction", "source-analyst", {**empty_scope, "source_ids": [source_id]}, ["units/extract-001-attempt-1.json"]),
        ("topic-organization", "topic-organization-attempt-1", "topic_organization", "topic-organizer", {**empty_scope, "unit_ids": [heading_id, example_id]}, ["topics.json"]),
        ("compare-001", "compare-001-attempt-1", "comparison", "topic-comparator", {**empty_scope, "topic_ids": ["learning-modes"]}, ["comparisons/compare-001-attempt-1.json"]),
        ("publication", "publication-attempt-1", "synthesis", "synthesizer", {**empty_scope, "unit_ids": [heading_id, example_id]}, ["drafts/annotated-publication-attempt-1.md", "unit-dispositions-publication-attempt-1.json"]),
        ("validate-a", "validate-a-attempt-1", "semantic_validation", "validator", {**empty_scope, "validation_categories": ["coverage", "conflicts_qualifiers"]}, ["validation/validate-a.json"]),
        ("validate-b", "validate-b-attempt-1", "semantic_validation", "validator", {**empty_scope, "validation_categories": ["standalone_exposition", "coherence_markdown", "writing_quality"]}, ["validation/validate-b.json"]),
    ]
    producer_attempt_ids = []
    for spec_args in task_specs:
        task, attempt = write_task(work, *spec_args)
        tasks.append(task)
        attempts.append(attempt)
        if spec_args[2] in {"outline", "extraction", "topic_organization", "comparison", "synthesis"}:
            producer_attempt_ids.append(spec_args[1])
    tasks.append({"logical_task_id": "conflict-resolution", "phase": "conflict_resolution", "allowed_roles": ["conflict-resolver"], "status": "skipped", "attempt_ids": [], "preferred_attempt_id": None, "accepted_attempt_id": None, "skip_reason": "No required comparison records."})

    for producer_attempt_id in producer_attempt_ids:
        review_id = f"review-{producer_attempt_id}"
        review_attempt_id = f"{review_id}-attempt-1"
        review_path = f"reviews/{review_attempt_id}.json"
        dump_json(work / review_path, {
            "schema_version": SCHEMA_VERSION,
            "review_id": review_attempt_id,
            "review_stage": "fixture",
            "reviewed_attempt_ids": [producer_attempt_id],
            "status": "passed",
            "errors": [],
            "warnings": [],
            "findings": [],
            "metrics": {},
        })
        review_scope = {**empty_scope, "reviewed_attempt_ids": [producer_attempt_id], "review_categories": ["stage_contract"]}
        task, attempt = write_task(work, review_id, review_attempt_id, "stage_review", "stage-reviewer", review_scope, [review_path], [producer_attempt_id])
        tasks.append(task)
        attempts.append(attempt)
    dump_json(work / "task-ledger.json", {"schema_version": SCHEMA_VERSION, "execution_mode": "subagents_required", "fallback_used": False, "maximum_concurrent_subagents": 3, "logical_tasks": tasks})
    dump_json(work / "attempts.json", {"schema_version": SCHEMA_VERSION, "attempts": attempts})
    run(sys.executable, str(SCRIPTS / "validate_task_lifecycle.py"), "--work-dir", str(work), "--require-terminal", "--report", str(work / "task-lifecycle-report.json"))
    run(sys.executable, str(SCRIPTS / "validate_reviews.py"), "--work-dir", str(work), "--report", str(work / "review-validation-report.json"))
    run(sys.executable, str(SCRIPTS / "validate_delegation.py"), "--work-dir", str(work), "--inventory", str(work / "inventory.json"), "--units-dir", str(work / "units"), "--topics", str(work / "topics.json"), "--comparisons-dir", str(work / "comparisons"), "--comparison-index", str(work / "comparisons" / "index.json"), "--decisions", str(work / "decision-ledger.json"), "--report", str(work / "delegation-validation-report.json"))

    # A failed independent review must block review validation.
    review_file = sorted((work / "reviews").glob("*.json"))[0]
    review_doc = json.loads(review_file.read_text())
    review_doc["status"] = "failed"
    dump_json(review_file, review_doc)
    run(sys.executable, str(SCRIPTS / "validate_reviews.py"), "--work-dir", str(work), "--report", str(work / "failed-review-validation-report.json"), expect=2)
    run(sys.executable, str(SCRIPTS / "validate_delegation.py"), "--work-dir", str(work), "--inventory", str(work / "inventory.json"), "--units-dir", str(work / "units"), "--topics", str(work / "topics.json"), "--comparisons-dir", str(work / "comparisons"), "--comparison-index", str(work / "comparisons" / "index.json"), "--decisions", str(work / "decision-ledger.json"), "--report", str(work / "failed-review-delegation-report.json"), expect=2)
    review_doc["status"] = "passed"
    dump_json(review_file, review_doc)


def test_reconciliation(root: Path) -> None:
    work = root / "reconcile"
    (work / "task-specs").mkdir(parents=True)
    (work / "receipts").mkdir()
    (work / "outputs").mkdir()
    tasks = [{"logical_task_id": "publication", "phase": "synthesis", "allowed_roles": ["synthesizer", "publication-finalizer"], "status": "running", "attempt_ids": ["pub-attempt-1", "pub-attempt-2"], "preferred_attempt_id": "pub-attempt-2", "accepted_attempt_id": None, "skip_reason": None}]
    attempts = []
    for number, attempt_id in enumerate(("pub-attempt-1", "pub-attempt-2"), start=1):
        output = f"outputs/{attempt_id}.md"
        (work / output).write_text(f"attempt {number}\n")
        role = "synthesizer" if number == 1 else "publication-finalizer"
        task, attempt = write_task(work, "publication", attempt_id, "synthesis", role, {"source_ids": [], "topic_ids": [], "comparison_ids": [], "decision_ids": [], "unit_ids": ["u1"], "validation_categories": [], "reviewed_attempt_ids": [], "review_categories": []}, [output])
        attempt["attempt_number"] = number
        attempt["status"] = "completed"
        attempts.append(attempt)
    dump_json(work / "task-ledger.json", {"schema_version": SCHEMA_VERSION, "execution_mode": "subagents_required", "fallback_used": False, "maximum_concurrent_subagents": 3, "logical_tasks": tasks})
    dump_json(work / "attempts.json", {"schema_version": SCHEMA_VERSION, "attempts": attempts})
    run(sys.executable, str(SCRIPTS / "reconcile_attempts.py"), "--work-dir", str(work))
    reconciled = json.loads((work / "attempts.json").read_text())["attempts"]
    statuses = {item["attempt_id"]: item["status"] for item in reconciled}
    assert statuses == {"pub-attempt-1": "superseded", "pub-attempt-2": "accepted"}, statuses


def main() -> int:
    test_package_structure()
    with tempfile.TemporaryDirectory(prefix="markdown-consolidator-smoke-") as temp:
        root = Path(temp)
        test_complete_fixture(root)
        test_reconciliation(root)
    print("All smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
