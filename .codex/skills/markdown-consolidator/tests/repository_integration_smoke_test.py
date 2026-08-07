#!/usr/bin/env python3
"""Smoke-test repository placement, publication-set materialization, and link handoff."""

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
        "created_at": "2026-08-06T00:00:00Z",
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
        "completed_at": "2026-08-06T00:01:00Z",
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
        "started_at": "2026-08-06T00:00:00Z",
        "completed_at": "2026-08-06T00:01:00Z",
    }
    return task, attempt


def create_fake_companions(repo: Path) -> tuple[Path, Path]:
    home = repo / ".codex" / "skills" / "note-home-finder"
    links = repo / ".codex" / "skills" / "markdown-link-normalizer"
    (home / "agents").mkdir(parents=True)
    (links / "scripts").mkdir(parents=True)
    (home / "SKILL.md").write_text("---\nname: note-home-finder\n---\n# Note Home Finder\n", encoding="utf-8")
    (links / "SKILL.md").write_text("---\nname: markdown-link-normalizer\n---\n# Link Normalizer\n", encoding="utf-8")
    (links / "scripts" / "normalize_markdown_links.py").write_text(
        "from pathlib import Path\nimport sys\np=Path(sys.argv[1])\nprint(p)\nprint('changed=0')\n",
        encoding="utf-8",
    )
    (links / "scripts" / "validate_markdown_links.py").write_text(
        '''from pathlib import Path
import re, sys, urllib.parse
root=Path(sys.argv[1])
files=[root] if root.is_file() else list(root.rglob('*.md'))
missing=[]
for source in files:
    for n,line in enumerate(source.read_text(encoding='utf-8').splitlines(),1):
        for dest in re.findall(r'(?<!!)\\[[^\\]]+\\]\\(([^)\\n]+)\\)',line):
            if '://' in dest or dest.startswith('mailto:'): continue
            part=dest.split('#',1)[0]
            target=source if not part else source.parent/urllib.parse.unquote(part)
            if not target.exists(): missing.append((source,n,dest))
print(f'missing_files={len(missing)}')
for source,n,dest in missing: print(f'{source}:{n} -> {dest}')
print('missing_anchors=0')
raise SystemExit(1 if missing else 0)
''',
        encoding="utf-8",
    )
    return home, links


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="markdown-consolidator-repo-") as temp:
        root = Path(temp)
        repo = root / "notes"
        work = repo / ".markdown-consolidator-work"
        evidence_root = repo / "Scratch"
        (repo / "Security").mkdir(parents=True)
        evidence_root.mkdir(parents=True)
        work.mkdir(parents=True)
        (work / "units").mkdir()
        (work / "drafts").mkdir()
        (work / "comparisons").mkdir()
        (work / "task-specs").mkdir()
        (work / "receipts").mkdir()
        (work / "reviews").mkdir()
        (work / "validation").mkdir()
        dump_json(work / "runtime-plan.json", {"schema_version": SCHEMA_VERSION, "publication_mode": "repository_integrated", "maximum_concurrent_subagents": 3})

        (repo / "Security" / "OAuth.md").write_text(
            "# OAuth\n\n## Refresh tokens\n\nRefresh tokens renew access without repeating the full authorization flow.\n",
            encoding="utf-8",
        )
        (repo / "Security" / "Token Storage.md").write_text(
            "# Token Storage\n\n## Server-side storage\n\nStore long-lived credentials on the server.\n",
            encoding="utf-8",
        )
        source = evidence_root / "input.md"
        source.write_text("# Rotation\nRotate a refresh token after every successful renewal.\n", encoding="utf-8")
        home, links = create_fake_companions(repo)

        run(
            sys.executable, str(SCRIPTS / "locate_companion_skills.py"),
            "--repository-root", str(repo),
            "--output", str(work / "companion-skills.json"),
        )
        companion = json.loads((work / "companion-skills.json").read_text())
        assert companion["skills"]["note-home-finder"]["skill_dir"] == str(home.resolve())
        assert companion["skills"]["markdown-link-normalizer"]["skill_dir"] == str(links.resolve())

        run(
            sys.executable, str(SCRIPTS / "inventory_markdown.py"), str(evidence_root),
            "--output", str(work / "inventory.json"),
        )
        inventory = json.loads((work / "inventory.json").read_text())
        source_id = inventory["sources"][0]["source_id"]
        heading_id = f"{source_id}-u0001"
        claim_id = f"{source_id}-u0002"

        placement = {
            "schema_version": SCHEMA_VERSION,
            "publication_mode": "repository_integrated",
            "outcome": "extend_existing_note",
            "confidence": "high",
            "destinations": [{
                "path": "Security/OAuth.md",
                "action": "extend",
                "assigned_topics": ["refresh-token-rotation"],
                "rationale": "Refresh-token rotation belongs in the existing OAuth note.",
            }],
            "related_notes": [{
                "path": "Security/Token Storage.md",
                "relationship": "prerequisite",
                "relevant_headings": ["Server-side storage"],
            }],
            "alternatives": [],
            "rationale": "The repository already has the durable OAuth home.",
        }
        dump_json(work / "placement-plan.json", placement)
        run(
            sys.executable, str(SCRIPTS / "validate_placement.py"),
            "--placement", str(work / "placement-plan.json"),
            "--repository-root", str(repo),
            "--inventory", str(work / "inventory.json"),
            "--report", str(work / "placement-validation-report.json"),
        )
        run(
            sys.executable, str(SCRIPTS / "snapshot_repository_context.py"),
            "--placement", str(work / "placement-plan.json"),
            "--repository-root", str(repo),
            "--snapshot-root", str(work / "destination-snapshots"),
            "--index", str(work / "repository-context.json"),
            "--report", str(work / "snapshot-report.json"),
        )

        units = {
            "schema_version": SCHEMA_VERSION,
            "batch_id": "extract-attempt-1",
            "sources": [source_id],
            "units": [
                {
                    "unit_id": heading_id,
                    "source_id": source_id,
                    "source_path": "input.md",
                    "heading_path": ["Rotation"],
                    "source_range": {"start": 1, "end": 1},
                    "unit_type": "heading",
                    "source_text": "# Rotation",
                    "normalized_claim": "Rotation",
                    "topic_hint": "refresh-token-rotation",
                    "assertion_kind": "structure",
                    "qualifiers": {"versions": [], "dates": [], "platforms": [], "environments": [], "configurations": [], "roles": [], "other": []},
                    "confidence": 1.0,
                    "warnings": [],
                },
                {
                    "unit_id": claim_id,
                    "source_id": source_id,
                    "source_path": "input.md",
                    "heading_path": ["Rotation"],
                    "source_range": {"start": 2, "end": 2},
                    "unit_type": "requirement",
                    "source_text": "Rotate a refresh token after every successful renewal.",
                    "normalized_claim": "Rotate refresh tokens after successful renewal.",
                    "topic_hint": "refresh-token-rotation",
                    "assertion_kind": "requirement",
                    "qualifiers": {"versions": [], "dates": [], "platforms": [], "environments": [], "configurations": [], "roles": [], "other": []},
                    "confidence": 1.0,
                    "warnings": [],
                },
            ],
            "covered_line_ranges": [{"source_id": source_id, "range": {"start": 1, "end": 2}}],
            "uncovered_nonempty_lines": [],
            "warnings": [],
        }
        dump_json(work / "units" / "extract-attempt-1.json", units)

        plan = {
            "schema_version": SCHEMA_VERSION,
            "publication_mode": "repository_integrated",
            "destinations": [{
                "path": "Security/OAuth.md",
                "action": "extend",
                "assigned_unit_ids": [heading_id, claim_id],
                "section_operations": [{
                    "operation": "extend_section",
                    "existing_heading": "Refresh tokens",
                    "assigned_unit_ids": [heading_id, claim_id],
                }],
                "protected_headings": ["OAuth", "Refresh tokens"],
                "heading_changes": [],
            }],
            "link_plan": [{
                "from_path": "Security/OAuth.md",
                "from_section": "Refresh tokens",
                "to_path": "Security/Token Storage.md",
                "to_heading": "Server-side storage",
                "relationship": "prerequisite",
                "reason": "Rotation depends on secure server-side token storage.",
            }],
            "terminology_constraints": [],
            "intentional_repetition": [],
            "modified_context_paths": [],
        }
        dump_json(work / "integration-plan.json", plan)
        run(
            sys.executable, str(SCRIPTS / "validate_integration_plan.py"),
            "--placement", str(work / "placement-plan.json"),
            "--plan", str(work / "integration-plan.json"),
            "--units-dir", str(work / "units"),
            "--report", str(work / "integration-plan-validation-report.json"),
        )

        annotated = work / "drafts" / "OAuth.md"
        annotated.write_text(
            "# OAuth\n\n## Refresh tokens\n\n"
            "Refresh tokens renew access without repeating the full authorization flow.\n\n"
            f"<!-- MC:BEGIN {claim_id} evidence -->\n"
            "Rotate a refresh token after every successful renewal. This limits replay after a token is used. "
            "Rotation depends on [secure token storage](Token%20Storage.md#Server-side%20storage).\n"
            f"<!-- MC:END {claim_id} evidence -->\n",
            encoding="utf-8",
        )
        dispositions = {
            "schema_version": SCHEMA_VERSION,
            "document_revision": "publication-attempt-1",
            "unit_dispositions": [
                {"unit_id": heading_id, "disposition": "represented_by_structure", "destination_path": "Security/OAuth.md", "final_section_id": "refresh-tokens", "notes": None},
                {"unit_id": claim_id, "disposition": "included_directly", "destination_path": "Security/OAuth.md", "final_section_id": "refresh-tokens", "notes": None},
            ],
        }
        dump_json(work / "unit-dispositions.json", dispositions)
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "publication_mode": "repository_integrated",
            "revision": "publication-attempt-1",
            "publications": [{
                "path": "Security/OAuth.md",
                "action": "extend",
                "annotated_path": str(annotated),
                "assigned_unit_ids": [heading_id, claim_id],
            }],
        }
        dump_json(work / "publication-manifest.json", manifest)
        run(
            sys.executable, str(SCRIPTS / "materialize_publication_set.py"),
            "--manifest", str(work / "publication-manifest.json"),
            "--dispositions", str(work / "unit-dispositions.json"),
            "--units-dir", str(work / "units"),
            "--output-root", str(work / "candidates"),
            "--coverage-map", str(work / "coverage-map.json"),
            "--report", str(work / "materialization-report.json"),
        )
        run(
            sys.executable, str(SCRIPTS / "run_link_pipeline.py"),
            "--repository-root", str(repo),
            "--work-dir", str(work),
            "--inventory", str(work / "inventory.json"),
            "--publication-manifest", str(work / "publication-manifest.json"),
            "--candidate-root", str(work / "candidates"),
            "--normalizer-skill-dir", str(links),
            "--shadow-root", str(work / "repository-shadow"),
            "--normalized-root", str(work / "normalized-candidates"),
            "--report", str(work / "link-pipeline-report.json"),
        )
        run(
            sys.executable, str(SCRIPTS / "validate_repository_integration.py"),
            "--repository-root", str(repo),
            "--inventory", str(work / "inventory.json"),
            "--units-dir", str(work / "units"),
            "--placement", str(work / "placement-plan.json"),
            "--integration-plan", str(work / "integration-plan.json"),
            "--context-index", str(work / "repository-context.json"),
            "--publication-manifest", str(work / "publication-manifest.json"),
            "--publication-root", str(work / "normalized-candidates"),
            "--coverage-map", str(work / "coverage-map.json"),
            "--link-report", str(work / "link-pipeline-report.json"),
            "--report", str(work / "repository-integration-report.json"),
        )

        normalized = work / "normalized-candidates" / "Security" / "OAuth.md"
        assert normalized.is_file()
        assert "input.md" not in normalized.read_text(encoding="utf-8")

        # Build a complete repository-mode delegated lifecycle fixture.
        outline = {
            "schema_version": SCHEMA_VERSION,
            "title": "OAuth",
            "audience": "Developers",
            "purpose": "Operational reference",
            "output_format": "Repository notes",
            "scope": "Complete source union",
            "sections": [{"section_id": "refresh-tokens", "heading": "Refresh tokens", "purpose": "Explain rotation", "source_topic_hints": ["refresh-token-rotation"]}],
            "fallback_sections": [],
        }
        dump_json(work / "outline.json", outline)
        topics = {"schema_version": SCHEMA_VERSION, "topics": [{"topic_id": "refresh-token-rotation", "canonical_name": "Refresh-token rotation", "aliases": [], "unit_ids": [heading_id, claim_id], "cross_topic_unit_ids": [], "ambiguous_unit_ids": []}]}
        dump_json(work / "topics.json", topics)
        comparisons = {
            "schema_version": SCHEMA_VERSION,
            "batch_id": "compare-attempt-1",
            "assigned_topic_ids": ["refresh-token-rotation"],
            "assigned_unit_ids": [heading_id, claim_id],
            "records": [
                {"comparison_id": "cmp-heading", "topic_id": "refresh-token-rotation", "unit_ids": [heading_id], "relationship": "unique", "semantic_union": ["Rotation heading"], "rationale": "Unique structure", "recommended_action": "represented_by_structure", "confidence": 1.0},
                {"comparison_id": "cmp-claim", "topic_id": "refresh-token-rotation", "unit_ids": [claim_id], "relationship": "unique", "semantic_union": ["Rotate refresh tokens"], "rationale": "Unique requirement", "recommended_action": "included_directly", "confidence": 1.0},
            ],
            "accounted_unit_ids": [heading_id, claim_id],
            "warnings": [],
        }
        dump_json(work / "comparisons" / "compare-attempt-1.json", comparisons)
        dump_json(work / "comparisons" / "index.json", {"schema_version": SCHEMA_VERSION, "topic_ids": ["refresh-token-rotation"], "comparison_ids": ["cmp-heading", "cmp-claim"], "required_resolution_ids": []})
        dump_json(work / "decision-ledger.json", {"schema_version": SCHEMA_VERSION, "decisions": []})
        dump_json(work / "validation" / "validate-a.json", {"schema_version": SCHEMA_VERSION, "status": "passed"})
        dump_json(work / "validation" / "validate-b.json", {"schema_version": SCHEMA_VERSION, "status": "passed"})

        empty = {
            "source_ids": [], "topic_ids": [], "comparison_ids": [], "decision_ids": [],
            "unit_ids": [], "validation_categories": [], "reviewed_attempt_ids": [],
            "review_categories": [], "destination_paths": [], "context_paths": [], "publication_paths": [],
        }
        task_specs = [
            ("placement", "placement-attempt-1", "placement", "note-home-finder-adapter", {**empty, "source_ids": [source_id]}, ["placement-plan.json"]),
            ("outline", "outline-attempt-1", "outline", "outline-planner", {**empty, "source_ids": [source_id], "destination_paths": ["Security/OAuth.md"]}, ["outline.json"]),
            ("extract", "extract-attempt-1", "extraction", "source-analyst", {**empty, "source_ids": [source_id]}, ["units/extract-attempt-1.json"]),
            ("topics", "topics-attempt-1", "topic_organization", "topic-organizer", {**empty, "unit_ids": [heading_id, claim_id]}, ["topics.json"]),
            ("compare", "compare-attempt-1", "comparison", "topic-comparator", {**empty, "topic_ids": ["refresh-token-rotation"]}, ["comparisons/compare-attempt-1.json"]),
            ("integration", "integration-attempt-1", "integration_planning", "integration-planner", {**empty, "unit_ids": [heading_id, claim_id], "destination_paths": ["Security/OAuth.md"]}, ["integration-plan.json"]),
            ("publication", "publication-attempt-1", "synthesis", "synthesizer", {**empty, "unit_ids": [heading_id, claim_id], "publication_paths": ["Security/OAuth.md"]}, ["drafts/OAuth.md", "unit-dispositions.json", "publication-manifest.json"]),
            ("validate-a", "validate-a-attempt-1", "semantic_validation", "validator", {**empty, "validation_categories": ["coverage", "conflicts_qualifiers", "repository_integration"]}, ["validation/validate-a.json"]),
            ("validate-b", "validate-b-attempt-1", "semantic_validation", "validator", {**empty, "validation_categories": ["standalone_exposition", "coherence_markdown", "writing_quality", "link_context"]}, ["validation/validate-b.json"]),
        ]
        tasks, attempts, producers = [], [], []
        for argspec in task_specs:
            task, attempt = write_task(work, *argspec)
            tasks.append(task)
            attempts.append(attempt)
            if argspec[2] in {"placement", "outline", "extraction", "topic_organization", "comparison", "integration_planning", "synthesis"}:
                producers.append(argspec[1])
        tasks.append({"logical_task_id": "conflicts", "phase": "conflict_resolution", "allowed_roles": ["conflict-resolver"], "status": "skipped", "attempt_ids": [], "preferred_attempt_id": None, "accepted_attempt_id": None, "skip_reason": "No required conflicts."})
        for producer in producers:
            logical = f"review-{producer}"
            attempt_id = f"{logical}-attempt-1"
            report_path = f"reviews/{attempt_id}.json"
            dump_json(work / report_path, {"schema_version": SCHEMA_VERSION, "review_id": attempt_id, "review_stage": "fixture", "reviewed_attempt_ids": [producer], "status": "passed", "errors": [], "warnings": [], "findings": [], "metrics": {}})
            task, attempt = write_task(work, logical, attempt_id, "stage_review", "stage-reviewer", {**empty, "reviewed_attempt_ids": [producer], "review_categories": ["stage_contract"]}, [report_path], [producer])
            tasks.append(task)
            attempts.append(attempt)
        dump_json(work / "task-ledger.json", {"schema_version": SCHEMA_VERSION, "execution_mode": "subagents_required", "fallback_used": False, "maximum_concurrent_subagents": 3, "logical_tasks": tasks})
        dump_json(work / "attempts.json", {"schema_version": SCHEMA_VERSION, "attempts": attempts})
        run(sys.executable, str(SCRIPTS / "validate_task_lifecycle.py"), "--work-dir", str(work), "--require-terminal", "--report", str(work / "task-lifecycle-report.json"))
        run(sys.executable, str(SCRIPTS / "validate_reviews.py"), "--work-dir", str(work), "--report", str(work / "review-validation-report.json"))
        run(
            sys.executable, str(SCRIPTS / "validate_delegation.py"),
            "--work-dir", str(work), "--inventory", str(work / "inventory.json"),
            "--units-dir", str(work / "units"), "--topics", str(work / "topics.json"),
            "--comparisons-dir", str(work / "comparisons"), "--comparison-index", str(work / "comparisons" / "index.json"),
            "--decisions", str(work / "decision-ledger.json"), "--placement", str(work / "placement-plan.json"),
            "--integration-plan", str(work / "integration-plan.json"), "--report", str(work / "delegation-validation-report.json"),
        )

        bad_placement = dict(placement)
        bad_placement["destinations"] = [{
            "path": "Scratch/input.md", "action": "extend", "assigned_topics": [], "rationale": "Invalid"
        }]
        dump_json(work / "bad-placement.json", bad_placement)
        run(
            sys.executable, str(SCRIPTS / "validate_placement.py"),
            "--placement", str(work / "bad-placement.json"),
            "--repository-root", str(repo),
            "--inventory", str(work / "inventory.json"),
            "--report", str(work / "bad-placement-report.json"),
            expect=2,
        )

    print("Repository integration smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
