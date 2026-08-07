#!/usr/bin/env python3
"""Validate durable-note integration after materialization and link normalization."""

from __future__ import annotations

import argparse
import re
import urllib.parse
from collections import Counter
from pathlib import Path
from typing import Any

from common import SCHEMA_VERSION, dump_json, load_json, unit_records

LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\n]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
META_PATTERNS = [
    r"\bthe material (?:states|shows|explains|describes|mentions)\b",
    r"\b(?:in|from|according to) the material\b",
    r"\bthe (?:sources|documents|files) (?:state|show|explain|describe|mention)\b",
    r"\bas shown in (?:the )?(?:source|material|document)\b",
    r"\bthe (?:example|case|scenario|illustration|definition|diagram|argument) in (?:the )?(?:source|material|document)\b",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate repository-integrated publication set.")
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--units-dir", type=Path, required=True)
    parser.add_argument("--placement", type=Path, required=True)
    parser.add_argument("--integration-plan", type=Path, required=True)
    parser.add_argument("--context-index", type=Path, required=True)
    parser.add_argument("--publication-manifest", type=Path, required=True)
    parser.add_argument("--publication-root", type=Path, required=True)
    parser.add_argument("--coverage-map", type=Path, required=True)
    parser.add_argument("--link-report", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def headings(text: str) -> set[str]:
    result: set[str] = set()
    in_fence = False
    fence = ""
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_fence:
                in_fence, fence = True, marker
            elif marker == fence:
                in_fence, fence = False, ""
            continue
        if in_fence:
            continue
        match = HEADING_RE.match(line)
        if match:
            result.add(match.group(2).strip())
    return result


def resolved_link(from_path: str, destination: str) -> tuple[str, str] | None:
    if not destination or "://" in destination or destination.startswith("mailto:"):
        return None
    path_part, separator, anchor = destination.partition("#")
    decoded = urllib.parse.unquote(path_part)
    if path_part:
        target = (Path(from_path).parent / decoded).as_posix()
        normalized = Path(target).as_posix()
        # Remove simple dot segments without requiring filesystem access.
        parts: list[str] = []
        for part in Path(normalized).parts:
            if part in {"", "."}:
                continue
            if part == ".." and parts:
                parts.pop()
            else:
                parts.append(part)
        target = "/".join(parts)
    else:
        target = from_path
    return target, urllib.parse.unquote(anchor) if separator else ""


def main() -> int:
    args = parse_args()
    repository = args.repository_root.resolve()
    inventory = load_json(args.inventory)
    placement = load_json(args.placement)
    plan = load_json(args.integration_plan)
    context_index = load_json(args.context_index)
    manifest = load_json(args.publication_manifest)
    coverage = load_json(args.coverage_map)
    link_report = load_json(args.link_report)
    units, _ = unit_records(args.units_dir)
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    if link_report.get("status") != "passed":
        errors.append({"code": "link_pipeline_failed"})

    placement_paths = {str(item.get("path")) for item in placement.get("destinations", []) if isinstance(item, dict) and item.get("path")}
    publications = [item for item in manifest.get("publications", []) if isinstance(item, dict)]
    publication_paths = [str(item.get("path", "")) for item in publications]
    if set(publication_paths) != placement_paths or len(publication_paths) != len(set(publication_paths)):
        errors.append({"code": "publication_manifest_destination_mismatch", "expected": sorted(placement_paths), "actual": sorted(set(publication_paths))})

    source_tokens: set[str] = set()
    evidence_absolute: set[Path] = set()
    for item in inventory.get("sources", []):
        if not isinstance(item, dict):
            continue
        for value in (item.get("source_id"), item.get("path"), Path(str(item.get("path", ""))).name):
            if value and len(str(value)) >= 4:
                source_tokens.add(str(value))
        if item.get("absolute_path"):
            evidence_absolute.add(Path(str(item["absolute_path"])).resolve())

    plan_by_path = {str(item.get("path")): item for item in plan.get("destinations", []) if isinstance(item, dict) and item.get("path")}
    snapshots = {str(item.get("path")): item for item in context_index.get("notes", []) if isinstance(item, dict) and item.get("path")}
    observed_links: set[tuple[str, str, str]] = set()
    texts: dict[str, str] = {}

    for relative in publication_paths:
        candidate = args.publication_root / relative
        if not candidate.is_file():
            errors.append({"code": "publication_file_missing", "path": relative})
            continue
        text = candidate.read_text(encoding="utf-8")
        texts[relative] = text
        for pattern in META_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                errors.append({"code": "meta_source_phrase", "path": relative, "pattern": pattern})
        hits = sorted(token for token in source_tokens if token in text)
        if hits:
            errors.append({"code": "evidence_source_reference", "path": relative, "items": hits})
        for match in LINK_RE.finditer(text):
            resolved = resolved_link(relative, match.group(2).strip())
            if resolved is None:
                continue
            target, anchor = resolved
            observed_links.add((relative, target, anchor))
            absolute_target = (repository / target).resolve()
            if absolute_target in evidence_absolute:
                errors.append({"code": "link_targets_disposable_evidence", "from_path": relative, "to_path": target})

        baseline = snapshots.get(relative)
        if baseline and baseline.get("exists"):
            candidate_headings = headings(text)
            approved = {
                str(item.get("old_heading"))
                for item in plan_by_path.get(relative, {}).get("heading_changes", [])
                if isinstance(item, dict) and item.get("approved") is True
            }
            missing_headings = sorted(
                str(item.get("text"))
                for item in baseline.get("headings", [])
                if isinstance(item, dict) and item.get("text") and str(item.get("text")) not in candidate_headings and str(item.get("text")) not in approved
            )
            if missing_headings:
                errors.append({"code": "unapproved_baseline_heading_removal", "path": relative, "headings": missing_headings})

    for link in plan.get("link_plan", []):
        if not isinstance(link, dict):
            continue
        expected = (str(link.get("from_path", "")), str(link.get("to_path", "")), str(link.get("to_heading", "")))
        if expected not in observed_links:
            errors.append({"code": "planned_link_missing", "from_path": expected[0], "to_path": expected[1], "to_heading": expected[2]})

    entries = [item for item in coverage.get("unit_dispositions", []) if isinstance(item, dict)]
    by_unit = {str(item.get("unit_id")): item for item in entries if item.get("unit_id")}
    if set(by_unit) != set(units):
        errors.append({"code": "coverage_unit_set_mismatch", "missing": sorted(set(units) - set(by_unit)), "unknown": sorted(set(by_unit) - set(units))})
    destinations = Counter(str(item.get("destination_path", "")) for item in entries)
    for unit_id, entry in by_unit.items():
        destination = str(entry.get("destination_path", ""))
        evidence = entry.get("publication_evidence", [])
        if destination not in texts:
            errors.append({"code": "unit_destination_missing", "unit_id": unit_id, "destination": destination})
        elif not isinstance(evidence, list) or not evidence or not all(isinstance(value, str) and value in texts[destination] for value in evidence):
            unit = units.get(unit_id, {})
            structural = unit.get("unit_type") in {"heading", "structure"} and entry.get("disposition") == "represented_by_structure"
            if not structural:
                errors.append({"code": "unit_evidence_invalid", "unit_id": unit_id, "destination": destination})

    context_paths = {str(item.get("path")) for item in placement.get("related_notes", []) if isinstance(item, dict) and item.get("path")}
    modified_context = sorted(context_paths & set(publication_paths))
    if modified_context:
        errors.append({"code": "context_note_modified_without_destination_role", "items": modified_context})

    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "publications": len(publication_paths),
            "units": len(units),
            "covered_units": len(by_unit),
            "planned_links": len([item for item in plan.get("link_plan", []) if isinstance(item, dict)]),
            "observed_local_links": len(observed_links),
            "units_by_destination": dict(sorted(destinations.items())),
        },
    }
    dump_json(args.report, report)
    print(report["status"])
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
