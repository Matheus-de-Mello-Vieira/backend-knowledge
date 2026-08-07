#!/usr/bin/env python3
"""Deterministically validate lossless coverage and standalone publication boundaries."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path
from typing import Any

from common import SCHEMA_VERSION, dump_json, load_json, unit_records

META_PATTERNS = [
    r"\bthe material (?:states|shows|explains|describes|mentions)\b",
    r"\b(?:in|from|according to) the material\b",
    r"\bthe (?:sources|documents|files) (?:state|show|explain|describe|mention)\b",
    r"\bas shown in (?:the )?(?:source|material|document)\b",
    r"\bthe (?:example|case|scenario|illustration|definition|diagram|argument) in (?:the )?(?:source|material|document)\b",
    r"\baccording to (?:source|document|file) [A-Z0-9_-]+\b",
]
DANGLING_PATTERNS = [
    r"\bthe (?:example|case|scenario|illustration|definition|diagram|argument) (?:above|below|mentioned|described earlier|previously described)\b",
]
ALLOWED_DISPOSITIONS = {
    "included_directly", "merged_equivalent", "included_as_detail",
    "preserved_as_variant", "preserved_as_conflict", "preserved_as_historical",
    "preserved_in_appendix", "represented_by_structure",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a materialized standalone consolidation.")
    parser.add_argument("--document", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--units-dir", type=Path, required=True)
    parser.add_argument("--coverage-map", type=Path, required=True)
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def prose_without_code(text: str) -> str:
    result: list[str] = []
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
        if not in_fence:
            result.append(line)
    return "\n".join(result)


def balanced_fences(text: str) -> bool:
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
    return not in_fence


def main() -> int:
    args = parse_args()
    document = args.document.read_text(encoding="utf-8")
    prose = prose_without_code(document)
    inventory = load_json(args.inventory)
    coverage = load_json(args.coverage_map)
    decisions = load_json(args.decisions)
    units, _ = unit_records(args.units_dir)
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    if "<!-- MC:" in document:
        errors.append({"code": "publication_marker_leak"})
    if not balanced_fences(document):
        errors.append({"code": "unbalanced_code_fences"})

    meta_violations: list[dict[str, Any]] = []
    for pattern in META_PATTERNS:
        for match in re.finditer(pattern, prose, flags=re.IGNORECASE):
            meta_violations.append({"pattern": pattern, "excerpt": match.group(0)})
    dangling_violations: list[dict[str, Any]] = []
    for pattern in DANGLING_PATTERNS:
        for match in re.finditer(pattern, prose, flags=re.IGNORECASE):
            dangling_violations.append({"pattern": pattern, "excerpt": match.group(0)})
    if meta_violations:
        errors.append({"code": "meta_source_phrase_violations", "items": meta_violations})
    if dangling_violations:
        errors.append({"code": "dangling_source_dependent_references", "items": dangling_violations})

    source_tokens: set[str] = set()
    for source in inventory.get("sources", []):
        if not isinstance(source, dict):
            continue
        for value in (source.get("source_id"), source.get("path"), Path(str(source.get("path", ""))).name):
            if value:
                source_tokens.add(str(value))
    source_reference_hits: list[str] = []
    for token in sorted(source_tokens, key=len, reverse=True):
        if len(token) >= 4 and token in document:
            source_reference_hits.append(token)
    for unit_id in units:
        if unit_id in document:
            source_reference_hits.append(unit_id)
    if source_reference_hits:
        errors.append({"code": "input_source_reference_violations", "items": sorted(set(source_reference_hits))})

    entries = coverage.get("unit_dispositions", [])
    by_unit: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("unit_id"):
            errors.append({"code": "invalid_coverage_entry"})
            continue
        unit_id = str(entry["unit_id"])
        if unit_id in by_unit:
            errors.append({"code": "duplicate_coverage_entry", "unit_id": unit_id})
        by_unit[unit_id] = entry
    missing = sorted(set(units) - set(by_unit))
    unknown = sorted(set(by_unit) - set(units))
    if missing:
        errors.append({"code": "missing_unit_dispositions", "items": missing})
    if unknown:
        errors.append({"code": "unknown_unit_dispositions", "items": unknown})

    nonstructural = 0
    represented = 0
    examples = 0
    represented_examples = 0
    for unit_id, unit in units.items():
        entry = by_unit.get(unit_id, {})
        disposition = entry.get("disposition")
        if disposition not in ALLOWED_DISPOSITIONS:
            errors.append({"code": "invalid_disposition", "unit_id": unit_id, "value": disposition})
        structural = unit.get("unit_type") in {"heading", "structure"} and disposition == "represented_by_structure"
        evidence = entry.get("publication_evidence", [])
        if not isinstance(evidence, list):
            evidence = []
        if not structural:
            nonstructural += 1
            if evidence and all(isinstance(value, str) and value and value in document for value in evidence):
                represented += 1
            else:
                errors.append({"code": "invalid_publication_evidence", "unit_id": unit_id})
        if unit.get("unit_type") == "example":
            examples += 1
            representation = entry.get("example_representation") or {}
            detail = representation.get("detail_excerpt", [])
            explanation = representation.get("explanation_excerpt", [])
            if not isinstance(detail, list):
                detail = []
            if not isinstance(explanation, list):
                explanation = []
            detail_ok = bool(detail) and all(isinstance(value, str) and value in document for value in detail)
            explanation_ok = bool(explanation) and all(isinstance(value, str) and value in document for value in explanation)
            distinct = " ".join("\n".join(detail).split()) != " ".join("\n".join(explanation).split())
            if detail_ok and explanation_ok and distinct:
                represented_examples += 1
            else:
                errors.append({"code": "invalid_example_exposition", "unit_id": unit_id})

    decision_units: set[str] = set()
    unresolved_conflicts = 0
    for decision in decisions.get("decisions", []):
        if not isinstance(decision, dict):
            continue
        decision_units.update(str(value) for value in decision.get("unit_ids", []))
        if decision.get("requires_human_review") or decision.get("outcome") in {"preserve_both_unresolved", "requires_human_review"}:
            unresolved_conflicts += 1
    missing_decision_units = sorted(decision_units - set(by_unit))
    if missing_decision_units:
        errors.append({"code": "decision_units_missing_coverage", "items": missing_decision_units})

    disposition_coverage = len(set(units) & set(by_unit)) / len(units) if units else 1.0
    evidence_coverage = represented / nonstructural if nonstructural else 1.0
    example_coverage = represented_examples / examples if examples else 1.0
    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "units": len(units),
            "unit_dispositions": len(by_unit),
            "unit_disposition_coverage": disposition_coverage,
            "nonstructural_units": nonstructural,
            "represented_nonstructural_units": represented,
            "unit_final_representation_coverage": evidence_coverage,
            "publication_evidence_coverage": evidence_coverage,
            "example_units": examples,
            "represented_example_units": represented_examples,
            "example_exposition_coverage": example_coverage,
            "input_source_reference_violations": len(set(source_reference_hits)),
            "meta_source_phrase_violations": len(meta_violations),
            "dangling_reference_violations": len(dangling_violations),
            "unresolved_conflicts": unresolved_conflicts,
        },
    }
    dump_json(args.report, report)
    print(report["status"])
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
