#!/usr/bin/env python3
"""Materialize a clean publication and exact coverage map from an annotated draft."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from common import SCHEMA_VERSION, dump_json, load_json, unit_records

BEGIN_RE = re.compile(r"^\s*<!--\s*MC:BEGIN\s+([A-Za-z0-9._,-]+)\s+(evidence|detail|explanation)\s*-->\s*$")
END_RE = re.compile(r"^\s*<!--\s*MC:END\s+([A-Za-z0-9._,-]+)\s+(evidence|detail|explanation)\s*-->\s*$")
ALLOWED_DISPOSITIONS = {
    "included_directly", "merged_equivalent", "included_as_detail",
    "preserved_as_variant", "preserved_as_conflict", "preserved_as_historical",
    "preserved_in_appendix", "represented_by_structure",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Strip MC markers and derive exact publication evidence.")
    parser.add_argument("--annotated", type=Path, required=True)
    parser.add_argument("--dispositions", type=Path, required=True)
    parser.add_argument("--units-dir", type=Path, required=True)
    parser.add_argument("--output-document", type=Path, required=True)
    parser.add_argument("--coverage-map", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def normalize_excerpt(text: str) -> str:
    return " ".join(text.split())


def main() -> int:
    args = parse_args()
    units, _ = unit_records(args.units_dir)
    dispositions_doc = load_json(args.dispositions)
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    disposition_entries = dispositions_doc.get("unit_dispositions", [])
    dispositions: dict[str, dict[str, Any]] = {}
    for entry in disposition_entries:
        if not isinstance(entry, dict) or not entry.get("unit_id"):
            errors.append({"code": "invalid_disposition"})
            continue
        unit_id = str(entry["unit_id"])
        if unit_id in dispositions:
            errors.append({"code": "duplicate_disposition", "unit_id": unit_id})
        dispositions[unit_id] = entry
        if entry.get("disposition") not in ALLOWED_DISPOSITIONS:
            errors.append({"code": "invalid_disposition_value", "unit_id": unit_id, "value": entry.get("disposition")})

    missing_dispositions = sorted(set(units) - set(dispositions))
    unknown_dispositions = sorted(set(dispositions) - set(units))
    if missing_dispositions:
        errors.append({"code": "missing_dispositions", "items": missing_dispositions})
    if unknown_dispositions:
        errors.append({"code": "unknown_dispositions", "items": unknown_dispositions})

    lines = args.annotated.read_text(encoding="utf-8").splitlines(keepends=True)
    clean_lines: list[str] = []
    active: tuple[list[str], str, list[str]] | None = None
    evidence: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

    for number, line in enumerate(lines, start=1):
        begin = BEGIN_RE.match(line.rstrip("\r\n"))
        end = END_RE.match(line.rstrip("\r\n"))
        if begin:
            if active is not None:
                errors.append({"code": "nested_marker", "line": number})
                continue
            ids = begin.group(1).split(",")
            kind = begin.group(2)
            unknown = sorted(set(ids) - set(units))
            if unknown:
                errors.append({"code": "marker_unknown_units", "line": number, "items": unknown})
            active = (ids, kind, [])
            continue
        if end:
            if active is None:
                errors.append({"code": "marker_end_without_begin", "line": number})
                continue
            ids, kind, captured = active
            end_ids = end.group(1).split(",")
            end_kind = end.group(2)
            if ids != end_ids or kind != end_kind:
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

    clean_text = "".join(clean_lines)
    if "<!-- MC:" in clean_text:
        errors.append({"code": "marker_leaked_into_publication"})

    coverage_entries: list[dict[str, Any]] = []
    source_ids: set[str] = set()
    examples = 0
    represented_examples = 0
    nonstructural = 0
    represented_nonstructural = 0

    for unit_id, unit in sorted(units.items()):
        source_ids.add(str(unit.get("source_id", "")))
        disposition = dispositions.get(unit_id, {})
        unit_type = str(unit.get("unit_type", ""))
        structural = unit_type in {"heading", "structure"} and disposition.get("disposition") == "represented_by_structure"
        unit_evidence = evidence.get(unit_id, {})
        all_evidence = list(unit_evidence.get("evidence", []))
        detail = list(unit_evidence.get("detail", []))
        explanation = list(unit_evidence.get("explanation", []))
        if unit_type == "example":
            examples += 1
            all_evidence.extend(detail)
            all_evidence.extend(explanation)
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
            if not all_evidence:
                errors.append({"code": "missing_publication_evidence", "unit_id": unit_id})
            else:
                represented_nonstructural += 1
        for excerpt in all_evidence:
            if excerpt not in clean_text:
                errors.append({"code": "generated_evidence_not_in_publication", "unit_id": unit_id})
        coverage_entries.append(
            {
                "unit_id": unit_id,
                "disposition": disposition.get("disposition"),
                "final_section_id": disposition.get("final_section_id"),
                "publication_evidence": all_evidence,
                "example_representation": {
                    "detail_excerpt": detail,
                    "explanation_excerpt": explanation,
                } if unit_type == "example" else None,
            }
        )

    args.output_document.parent.mkdir(parents=True, exist_ok=True)
    args.output_document.write_text(clean_text, encoding="utf-8")
    coverage_map = {
        "schema_version": SCHEMA_VERSION,
        "document": args.output_document.name,
        "sources_used": sorted(source_id for source_id in source_ids if source_id),
        "unit_dispositions": coverage_entries,
    }
    dump_json(args.coverage_map, coverage_map)
    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "units": len(units),
            "dispositions": len(dispositions),
            "nonstructural_units": nonstructural,
            "represented_nonstructural_units": represented_nonstructural,
            "publication_evidence_coverage": represented_nonstructural / nonstructural if nonstructural else 1.0,
            "example_units": examples,
            "represented_example_units": represented_examples,
            "example_exposition_coverage": represented_examples / examples if examples else 1.0,
        },
    }
    dump_json(args.report, report)
    print(report["status"])
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
