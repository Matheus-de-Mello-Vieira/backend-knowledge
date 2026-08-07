#!/usr/bin/env python3
"""Materialize multiple repository notes and derive exact unit evidence."""

from __future__ import annotations

import argparse
import re
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Any

from common import SCHEMA_VERSION, dump_json, load_json, unit_records

BEGIN_RE = re.compile(r"^\s*<!--\s*MC:BEGIN\s+([A-Za-z0-9._,-]+)\s+(evidence|detail|explanation)\s*-->\s*$")
END_RE = re.compile(r"^\s*<!--\s*MC:END\s+([A-Za-z0-9._,-]+)\s+(evidence|detail|explanation)\s*-->\s*$")
ALLOWED_DISPOSITIONS = {
    "included_directly", "merged_equivalent", "included_as_detail",
    "preserved_as_variant", "preserved_as_conflict", "preserved_as_historical",
    "preserved_in_appendix", "represented_by_structure", "represented_in_existing_note",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize an annotated publication set.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dispositions", type=Path, required=True)
    parser.add_argument("--units-dir", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--coverage-map", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def normalize_excerpt(text: str) -> str:
    return " ".join(text.split())


def materialize_one(path: Path, units: set[str]) -> tuple[str, dict[str, dict[str, list[str]]], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    evidence: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    clean_lines: list[str] = []
    active: tuple[list[str], str, list[str]] | None = None
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(keepends=True), start=1):
        begin = BEGIN_RE.match(line.rstrip("\r\n"))
        end = END_RE.match(line.rstrip("\r\n"))
        if begin:
            if active is not None:
                errors.append({"code": "nested_marker", "line": number})
                continue
            ids = begin.group(1).split(",")
            unknown = sorted(set(ids) - units)
            if unknown:
                errors.append({"code": "marker_unknown_units", "line": number, "items": unknown})
            active = (ids, begin.group(2), [])
            continue
        if end:
            if active is None:
                errors.append({"code": "marker_end_without_begin", "line": number})
                continue
            ids, kind, captured = active
            if ids != end.group(1).split(",") or kind != end.group(2):
                errors.append({"code": "marker_pair_mismatch", "line": number})
            excerpt = "".join(captured).strip()
            if not excerpt:
                errors.append({"code": "empty_marker", "line": number, "unit_ids": ids, "kind": kind})
            else:
                for unit_id in ids:
                    evidence[unit_id][kind].append(excerpt)
            active = None
            continue
        clean_lines.append(line)
        if active is not None:
            active[2].append(line)
    if active is not None:
        errors.append({"code": "unclosed_marker", "unit_ids": active[0], "kind": active[1]})
    clean = "".join(clean_lines)
    if "<!-- MC:" in clean:
        errors.append({"code": "marker_leaked_into_publication"})
    return clean, evidence, errors


def main() -> int:
    args = parse_args()
    manifest = load_json(args.manifest)
    dispositions_doc = load_json(args.dispositions)
    units, _ = unit_records(args.units_dir)
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    if args.output_root.exists():
        shutil.rmtree(args.output_root)
    args.output_root.mkdir(parents=True, exist_ok=True)

    dispositions: dict[str, dict[str, Any]] = {}
    for entry in dispositions_doc.get("unit_dispositions", []):
        if not isinstance(entry, dict) or not entry.get("unit_id"):
            errors.append({"code": "invalid_disposition"})
            continue
        unit_id = str(entry["unit_id"])
        if unit_id in dispositions:
            errors.append({"code": "duplicate_disposition", "unit_id": unit_id})
        dispositions[unit_id] = entry
        if entry.get("disposition") not in ALLOWED_DISPOSITIONS:
            errors.append({"code": "invalid_disposition_value", "unit_id": unit_id, "value": entry.get("disposition")})
        if not entry.get("destination_path"):
            errors.append({"code": "disposition_missing_destination", "unit_id": unit_id})

    missing_dispositions = sorted(set(units) - set(dispositions))
    unknown_dispositions = sorted(set(dispositions) - set(units))
    if missing_dispositions:
        errors.append({"code": "missing_dispositions", "items": missing_dispositions})
    if unknown_dispositions:
        errors.append({"code": "unknown_dispositions", "items": unknown_dispositions})

    publications = [item for item in manifest.get("publications", []) if isinstance(item, dict)]
    publication_paths: set[str] = set()
    manifest_unit_assignments: list[str] = []
    all_evidence: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    publication_texts: dict[str, str] = {}
    for item in publications:
        relative = str(item.get("path", ""))
        annotated = Path(str(item.get("annotated_path", "")))
        if not relative or Path(relative).is_absolute() or not relative.endswith(".md"):
            errors.append({"code": "invalid_publication_path", "path": relative})
            continue
        if relative in publication_paths:
            errors.append({"code": "duplicate_publication_path", "path": relative})
            continue
        publication_paths.add(relative)
        assigned_manifest_units = [str(value) for value in item.get("assigned_unit_ids", [])]
        manifest_unit_assignments.extend(assigned_manifest_units)
        if not annotated.is_file():
            errors.append({"code": "annotated_publication_missing", "path": str(annotated)})
            continue
        clean, evidence, item_errors = materialize_one(annotated, set(units))
        for error in item_errors:
            errors.append({"publication": relative, **error})
        destination = args.output_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(clean, encoding="utf-8")
        publication_texts[relative] = clean
        for unit_id, kinds in evidence.items():
            expected_destination = str(dispositions.get(unit_id, {}).get("destination_path", ""))
            if expected_destination and expected_destination != relative:
                errors.append({"code": "evidence_in_wrong_destination", "unit_id": unit_id, "expected": expected_destination, "actual": relative})
            for kind, excerpts in kinds.items():
                all_evidence[unit_id][kind].extend(excerpts)

    from collections import Counter
    manifest_counts = Counter(manifest_unit_assignments)
    if set(manifest_counts) != set(units) or any(manifest_counts[unit_id] != 1 for unit_id in units):
        errors.append({"code": "publication_manifest_unit_coverage", "missing": sorted(set(units) - set(manifest_counts)), "unknown": sorted(set(manifest_counts) - set(units)), "nonexact": sorted(unit_id for unit_id in units if manifest_counts[unit_id] != 1)})
    declared_destinations = {str(entry.get("destination_path", "")) for entry in dispositions.values()}
    unknown_destinations = sorted(declared_destinations - publication_paths)
    if unknown_destinations:
        errors.append({"code": "disposition_destination_not_published", "items": unknown_destinations})

    entries: list[dict[str, Any]] = []
    examples = represented_examples = nonstructural = represented_nonstructural = 0
    source_ids: set[str] = set()
    for unit_id, unit in sorted(units.items()):
        source_ids.add(str(unit.get("source_id", "")))
        disposition = dispositions.get(unit_id, {})
        destination_path = str(disposition.get("destination_path", ""))
        unit_evidence = all_evidence.get(unit_id, {})
        evidence = list(unit_evidence.get("evidence", []))
        detail = list(unit_evidence.get("detail", []))
        explanation = list(unit_evidence.get("explanation", []))
        unit_type = str(unit.get("unit_type", ""))
        structural = unit_type in {"heading", "structure"} and disposition.get("disposition") == "represented_by_structure"
        if unit_type == "example":
            examples += 1
            evidence.extend(detail)
            evidence.extend(explanation)
            if not detail:
                errors.append({"code": "example_missing_detail", "unit_id": unit_id})
            if not explanation:
                errors.append({"code": "example_missing_explanation", "unit_id": unit_id})
            if detail and explanation and normalize_excerpt("\n".join(detail)) == normalize_excerpt("\n".join(explanation)):
                errors.append({"code": "example_detail_and_explanation_identical", "unit_id": unit_id})
            if detail and explanation:
                represented_examples += 1
        if not structural:
            nonstructural += 1
            if not evidence:
                errors.append({"code": "missing_publication_evidence", "unit_id": unit_id})
            elif destination_path in publication_texts and all(value in publication_texts[destination_path] for value in evidence):
                represented_nonstructural += 1
            else:
                errors.append({"code": "generated_evidence_not_in_destination", "unit_id": unit_id, "destination": destination_path})
        entries.append({
            "unit_id": unit_id,
            "disposition": disposition.get("disposition"),
            "destination_path": destination_path,
            "final_section_id": disposition.get("final_section_id"),
            "publication_evidence": evidence,
            "example_representation": {"detail_excerpt": detail, "explanation_excerpt": explanation} if unit_type == "example" else None,
        })

    coverage = {
        "schema_version": SCHEMA_VERSION,
        "publication_mode": "repository_integrated",
        "documents": sorted(publication_paths),
        "sources_used": sorted(source_id for source_id in source_ids if source_id),
        "unit_dispositions": entries,
    }
    dump_json(args.coverage_map, coverage)
    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "publications": len(publication_paths),
            "units": len(units),
            "publication_evidence_coverage": represented_nonstructural / nonstructural if nonstructural else 1.0,
            "example_exposition_coverage": represented_examples / examples if examples else 1.0,
        },
    }
    dump_json(args.report, report)
    print(report["status"])
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
