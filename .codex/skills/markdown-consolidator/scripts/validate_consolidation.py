#!/usr/bin/env python3
"""Validate Markdown structure, lossless coverage, and publication independence."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
ANCHOR_LINK_RE = re.compile(r"\[[^\]]+\]\(#([^)]+)\)")
FOOTNOTE_REF_RE = re.compile(r"\[\^([^\]]+)\]")
FOOTNOTE_DEF_RE = re.compile(r"^\[\^([^\]]+)\]:", re.MULTILINE)

META_SOURCE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "material_as_narrator",
        re.compile(
            r"\b(?:the|this|that|provided|supplied|available|source|original|input|underlying)\s+"
            r"material\s+(?:states?|says?|shows?|describes?|mentions?|explains?|demonstrates?|"
            r"indicates?|notes?|provides?|contains?|presents?|uses?)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "located_in_material",
        re.compile(
            r"\b(?:in|from|within|throughout|according\s+to|based\s+on)\s+(?:the\s+)?"
            r"(?:(?:provided|supplied|available|source|original|input|underlying)\s+)?material\b",
            re.IGNORECASE,
        ),
    ),
    (
        "local_sources_as_narrator",
        re.compile(
            r"\b(?:the|these|those|provided|supplied|available|input|source|original)\s+"
            r"(?:source\s+)?(?:documents?|files?|sources?)\s+"
            r"(?:states?|say|says|show|shows|describe|describes|mention|mentions|explain|explains|"
            r"demonstrate|demonstrates|indicate|indicates|note|notes|provide|provides|contain|contains|"
            r"present|presents|use|uses)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "according_to_local_inputs",
        re.compile(
            r"\baccording\s+to\s+(?:the\s+)?(?:material|sources?|documents?|files?)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "shown_in_local_inputs",
        re.compile(
            r"\b(?:as|like)\s+(?:shown|described|explained|mentioned|noted|presented|demonstrated)"
            r"\s+(?:in|by)\s+(?:the\s+)?(?:material|sources?|documents?|files?)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "example_only_in_local_inputs",
        re.compile(
            r"\b(?:example|case\s+study|scenario|illustration|definition|diagram|figure|argument)"
            r"\s+(?:in|from)\s+(?:the\s+)?(?:material|source|document|file)s?\b",
            re.IGNORECASE,
        ),
    ),
    ("available_material", re.compile(r"\bthe\s+available\s+material\b", re.IGNORECASE)),
)

MIN_PUBLICATION_EVIDENCE_CHARS = 8
EXAMPLE_UNIT_TYPES = {"example"}

ALLOWED_DISPOSITIONS = {
    "included_directly",
    "merged_equivalent",
    "included_as_detail",
    "preserved_as_variant",
    "preserved_as_conflict",
    "preserved_as_historical",
    "preserved_in_appendix",
    "represented_by_structure",
}
STRUCTURAL_UNIT_TYPES = {"heading", "structure"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--document", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--units-dir", type=Path, required=True)
    parser.add_argument("--coverage-map", type=Path, required=True)
    parser.add_argument("--decisions", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def add_issue(items: list[dict[str, Any]], code: str, message: str, **extra: Any) -> None:
    issue = {"code": code, "message": message}
    issue.update(extra)
    items.append(issue)


def load_json(path: Path, errors: list[dict[str, Any]], code: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        add_issue(errors, code, f"Missing file: {path}")
        return {}
    except (OSError, json.JSONDecodeError) as exc:
        add_issue(errors, code, f"Cannot read {path}: {exc}")
        return {}
    if not isinstance(value, dict):
        add_issue(errors, code, f"Expected a JSON object: {path}")
        return {}
    return value


def github_anchor(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", "-", text)


def markdown_checks(
    text: str,
    errors: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
) -> None:
    fence_stack: list[tuple[str, int]] = []
    headings: list[tuple[int, str, int]] = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if fence_stack and fence_stack[-1][0] == marker:
                fence_stack.pop()
            elif not fence_stack:
                fence_stack.append((marker, line_number))
            continue
        if fence_stack:
            continue
        match = HEADING_RE.match(line)
        if match:
            headings.append((len(match.group(1)), match.group(2).strip(), line_number))

    for marker, line_number in fence_stack:
        add_issue(errors, "unclosed_code_fence", f"Unclosed {marker} fence at line {line_number}.")

    if not headings:
        add_issue(errors, "no_headings", "Document has no Markdown headings.")
    else:
        if headings[0][0] != 1:
            add_issue(
                warnings,
                "first_heading_not_h1",
                f"First heading is level {headings[0][0]} at line {headings[0][2]}.",
            )
        for previous, current in zip(headings, headings[1:]):
            if current[0] > previous[0] + 1:
                add_issue(
                    warnings,
                    "heading_level_jump",
                    f"Heading level jumps from H{previous[0]} to H{current[0]} at line {current[2]}.",
                )

    names = [heading.casefold() for _, heading, _ in headings]
    for duplicate, count in Counter(names).items():
        if count > 1:
            add_issue(warnings, "duplicate_heading", f"Duplicate heading text: {duplicate}")

    anchors = {github_anchor(heading) for _, heading, _ in headings}
    for target in ANCHOR_LINK_RE.findall(text):
        if target not in anchors:
            add_issue(warnings, "broken_internal_anchor", f"Missing heading for anchor: #{target}")

    refs = set(FOOTNOTE_REF_RE.findall(text))
    definitions = set(FOOTNOTE_DEF_RE.findall(text))
    for missing in sorted(refs - definitions):
        add_issue(errors, "missing_footnote_definition", f"Missing footnote definition: {missing}")
    for unused in sorted(definitions - refs):
        add_issue(warnings, "unused_footnote_definition", f"Unused footnote definition: {unused}")


def prose_lines(text: str) -> list[tuple[int, str]]:
    """Return publication lines outside fenced code blocks."""
    result: list[tuple[int, str]] = []
    fence_marker: str | None = None
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if fence_marker == marker:
                fence_marker = None
            elif fence_marker is None:
                fence_marker = marker
            continue
        if fence_marker is None:
            result.append((line_number, line))
    return result


def validate_standalone_exposition(
    document: str,
    errors: list[dict[str, Any]],
) -> int:
    """Reject prose that narrates or points back to temporary inputs."""
    violations = 0
    for line_number, line in prose_lines(document):
        matches: list[tuple[int, int, str]] = []
        for pattern_name, pattern in META_SOURCE_PATTERNS:
            for match in pattern.finditer(line):
                matches.append((match.start(), match.end(), pattern_name))
        if not matches:
            continue

        matches.sort(key=lambda item: (item[0], item[1]))
        groups: list[tuple[int, int, set[str]]] = []
        for start, end, pattern_name in matches:
            if groups and start <= groups[-1][1]:
                previous_start, previous_end, names = groups[-1]
                names.add(pattern_name)
                groups[-1] = (previous_start, max(previous_end, end), names)
            else:
                groups.append((start, end, {pattern_name}))

        for start, end, names in groups:
            violations += 1
            matched_text = line[start:end]
            add_issue(
                errors,
                "meta_source_narration_in_publication",
                f"Publication depends on unavailable input material at line {line_number}: {matched_text}",
                line=line_number,
                patterns=sorted(names),
                matched_text=matched_text,
            )
    return violations


def exact_excerpt_present(
    excerpt: Any,
    document: str,
    errors: list[dict[str, Any]],
    code: str,
    unit_id: str,
    field: str,
) -> bool:
    """Verify that a coverage-map excerpt is substantive and occurs verbatim."""
    if not isinstance(excerpt, str) or not excerpt.strip():
        add_issue(errors, code, f"Unit {unit_id} has an empty or invalid {field}.", unit_id=unit_id, field=field)
        return False
    cleaned = excerpt.strip()
    if len(re.sub(r"\s+", "", cleaned)) < MIN_PUBLICATION_EVIDENCE_CHARS:
        add_issue(
            errors,
            code,
            f"Unit {unit_id} has {field} that is too short to prove representation.",
            unit_id=unit_id,
            field=field,
            excerpt=cleaned,
        )
        return False
    if cleaned not in document:
        add_issue(
            errors,
            code,
            f"Unit {unit_id} has {field} that does not occur exactly in the publication.",
            unit_id=unit_id,
            field=field,
            excerpt=cleaned[:240],
        )
        return False
    return True


def source_path(inventory: dict[str, Any], source: dict[str, Any]) -> Path:
    absolute = source.get("absolute_path")
    if isinstance(absolute, str) and absolute:
        return Path(absolute)
    return Path(str(inventory.get("root", ""))) / str(source.get("path", ""))


def source_reference_tokens(inventory: dict[str, Any]) -> list[tuple[str, str]]:
    """Return exact local-source identifiers prohibited in publication text."""
    tokens: set[tuple[str, str]] = set()
    for source in inventory.get("sources", []):
        if not isinstance(source, dict):
            continue
        source_id = source.get("source_id")
        if isinstance(source_id, str) and source_id.strip():
            tokens.add(("source_id", source_id.strip()))

        for field in ("path", "absolute_path"):
            value = source.get(field)
            if isinstance(value, str) and value.strip():
                normalized = value.strip().replace("\\", "/")
                tokens.add((field, normalized))
                basename = Path(normalized).name
                if basename:
                    tokens.add(("filename", basename))
    return sorted(tokens, key=lambda item: (-len(item[1]), item[0], item[1].casefold()))


def validate_publication_independence(
    document: str,
    inventory: dict[str, Any],
    units: dict[str, dict[str, Any]],
    errors: list[dict[str, Any]],
) -> int:
    """Reject input paths, filenames, source IDs, and unit IDs in final Markdown."""
    violations: list[dict[str, Any]] = []
    document_folded = document.casefold()

    for token_type, token in source_reference_tokens(inventory):
        variants = {token, token.replace("\\", "/"), token.replace("/", "\\")}
        for variant in sorted(variants, key=len, reverse=True):
            if variant and variant.casefold() in document_folded:
                violations.append({"type": token_type, "token": token})
                break

    for unit_id in units:
        if unit_id.casefold() in document_folded:
            violations.append({"type": "unit_id", "token": unit_id})

    seen: set[tuple[str, str]] = set()
    for violation in violations:
        key = (violation["type"], violation["token"].casefold())
        if key in seen:
            continue
        seen.add(key)
        add_issue(
            errors,
            "input_source_reference_in_publication",
            f"Final publication contains prohibited {violation['type']}: {violation['token']}",
            reference_type=violation["type"],
            token=violation["token"],
        )
    return len(seen)


def load_units(
    units_dir: Path,
    inventory: dict[str, Any],
    errors: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, set[int]], int, int]:
    units: dict[str, dict[str, Any]] = {}
    covered_lines: dict[str, set[int]] = defaultdict(set)
    files = sorted(units_dir.rglob("*.json")) if units_dir.exists() else []
    if not files:
        add_issue(errors, "missing_unit_batches", f"No unit JSON files found under: {units_dir}")
        return units, covered_lines, 0, 0

    for path in files:
        batch = load_json(path, errors, "unit_batch_read_error")
        uncovered = batch.get("uncovered_nonempty_lines", [])
        if uncovered:
            add_issue(
                errors,
                "extraction_reports_uncovered_lines",
                f"Unit batch reports uncovered non-empty lines: {path}",
                uncovered_nonempty_lines=uncovered,
            )
        for unit in batch.get("units", []):
            if not isinstance(unit, dict):
                add_issue(errors, "invalid_unit", f"Non-object unit in {path}")
                continue
            unit_id = unit.get("unit_id")
            source_id = unit.get("source_id")
            start = unit.get("line_start")
            end = unit.get("line_end")
            if not isinstance(unit_id, str) or not unit_id:
                add_issue(errors, "missing_unit_id", f"Unit without ID in {path}")
                continue
            if unit_id in units:
                add_issue(errors, "duplicate_unit_id", f"Duplicate unit ID: {unit_id}")
                continue
            units[unit_id] = unit
            if not isinstance(source_id, str):
                add_issue(errors, "missing_unit_source", f"Unit {unit_id} has no source_id")
                continue
            if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start:
                add_issue(errors, "invalid_unit_line_range", f"Unit {unit_id} has invalid line range")
                continue
            covered_lines[source_id].update(range(start, end + 1))

    inventory_sources = {
        item.get("source_id"): item
        for item in inventory.get("sources", [])
        if isinstance(item, dict) and item.get("source_id")
    }
    total_nonempty = 0
    total_covered_nonempty = 0
    for source_id, source in inventory_sources.items():
        path = source_path(inventory, source)
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except OSError as exc:
            add_issue(errors, "source_read_error", f"Cannot verify source {source_id}: {exc}")
            continue
        nonempty = {index for index, line in enumerate(lines, start=1) if line.strip()}
        covered = nonempty & covered_lines.get(source_id, set())
        missing = sorted(nonempty - covered)
        total_nonempty += len(nonempty)
        total_covered_nonempty += len(covered)
        if missing:
            add_issue(
                errors,
                "uncovered_source_lines",
                f"Source {source_id} has {len(missing)} uncovered non-empty line(s).",
                source_id=source_id,
                lines=missing,
            )

    return units, covered_lines, total_nonempty, total_covered_nonempty


def validate_coverage_map(
    inventory: dict[str, Any],
    units: dict[str, dict[str, Any]],
    coverage_map: dict[str, Any],
    decisions: dict[str, Any],
    errors: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
    total_nonempty: int,
    covered_nonempty: int,
    reference_violations: int,
    meta_source_violations: int,
    document: str,
) -> dict[str, Any]:
    inventory_sources = {
        item.get("source_id"): item
        for item in inventory.get("sources", [])
        if isinstance(item, dict) and item.get("source_id")
    }
    used = set(coverage_map.get("sources_used", []))
    missing_sources = set(inventory_sources) - used
    unknown_sources = used - set(inventory_sources)
    for source_id in sorted(missing_sources):
        add_issue(errors, "source_not_used", f"Inventory source is absent from sources_used: {source_id}")
    for source_id in sorted(unknown_sources):
        add_issue(errors, "unknown_source_id", f"Unknown source in sources_used: {source_id}")

    section_ids: set[str] = set()
    claim_ids: set[str] = set()
    block_ids: set[str] = set()
    for section in coverage_map.get("sections", []):
        if not isinstance(section, dict):
            continue
        section_id = section.get("section_id")
        if isinstance(section_id, str):
            if section_id in section_ids:
                add_issue(errors, "duplicate_section_id", f"Duplicate section ID: {section_id}")
            section_ids.add(section_id)
        for claim in section.get("claims", []):
            if not isinstance(claim, dict):
                continue
            claim_id = claim.get("claim_id")
            if isinstance(claim_id, str):
                if claim_id in claim_ids:
                    add_issue(errors, "duplicate_claim_id", f"Duplicate claim ID: {claim_id}")
                claim_ids.add(claim_id)
            claim_sources = claim.get("sources", [])
            if not claim_sources:
                add_issue(warnings, "claim_without_internal_sources", f"Claim has no internal sources: {claim_id}")
            for ref in claim_sources:
                if not isinstance(ref, dict):
                    continue
                source_id = ref.get("source_id")
                unit_id = ref.get("unit_id")
                start = ref.get("line_start")
                end = ref.get("line_end")
                if source_id not in inventory_sources:
                    add_issue(errors, "claim_unknown_source", f"Claim {claim_id} uses unknown source: {source_id}")
                if unit_id not in units:
                    add_issue(errors, "claim_unknown_unit", f"Claim {claim_id} uses unknown unit: {unit_id}")
                if source_id in inventory_sources:
                    max_line = inventory_sources[source_id].get("line_count", 0)
                    if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start or end > max_line:
                        add_issue(errors, "claim_invalid_line_range", f"Claim {claim_id} has invalid range for {source_id}")
        for block in section.get("content_blocks", []):
            if not isinstance(block, dict):
                continue
            block_id = block.get("block_id")
            if isinstance(block_id, str):
                if block_id in block_ids:
                    add_issue(errors, "duplicate_block_id", f"Duplicate block ID: {block_id}")
                block_ids.add(block_id)
            for unit_id in block.get("source_unit_ids", []):
                if unit_id not in units:
                    add_issue(errors, "block_unknown_unit", f"Block {block_id} uses unknown unit: {unit_id}")

    dispositions = coverage_map.get("unit_dispositions", [])
    disposition_counts: Counter[str] = Counter()
    represented_nonstructural = 0
    publication_evidence_units = 0
    example_units = 0
    example_exposition_units = 0
    for entry in dispositions:
        if not isinstance(entry, dict):
            add_issue(errors, "invalid_unit_disposition", "A unit disposition is not an object.")
            continue
        unit_id = entry.get("unit_id")
        disposition = entry.get("disposition")
        if not isinstance(unit_id, str):
            add_issue(errors, "unit_disposition_missing_id", "A unit disposition has no unit_id.")
            continue
        disposition_counts[unit_id] += 1
        if unit_id not in units:
            add_issue(errors, "disposition_unknown_unit", f"Disposition references unknown unit: {unit_id}")
            continue
        if disposition not in ALLOWED_DISPOSITIONS:
            add_issue(errors, "invalid_disposition", f"Invalid disposition for {unit_id}: {disposition}")

        final_sections = entry.get("final_section_ids", [])
        final_claims = entry.get("final_claim_ids", [])
        final_blocks = entry.get("final_block_ids", [])
        for section_id in final_sections:
            if section_id not in section_ids:
                add_issue(errors, "disposition_unknown_section", f"Unit {unit_id} maps to unknown section: {section_id}")
        for claim_id in final_claims:
            if claim_id not in claim_ids:
                add_issue(errors, "disposition_unknown_claim", f"Unit {unit_id} maps to unknown claim: {claim_id}")
        for block_id in final_blocks:
            if block_id not in block_ids:
                add_issue(errors, "disposition_unknown_block", f"Unit {unit_id} maps to unknown block: {block_id}")

        unit = units[unit_id]
        unit_type = unit.get("unit_type")
        assertion_kind = unit.get("assertion_kind")
        if disposition == "represented_by_structure":
            if unit_type not in STRUCTURAL_UNIT_TYPES:
                add_issue(errors, "nonstructural_structure_disposition", f"Non-structural unit {unit_id} uses represented_by_structure")
            if not final_sections:
                add_issue(errors, "structure_unit_without_section", f"Structural unit {unit_id} has no final section")
        elif unit_type not in STRUCTURAL_UNIT_TYPES:
            if not final_claims and not final_blocks:
                add_issue(errors, "unit_without_final_representation", f"Unit {unit_id} maps to no final claim or block")
            else:
                represented_nonstructural += 1

            evidence = entry.get("publication_evidence")
            evidence_valid = False
            if not isinstance(evidence, list) or not evidence:
                add_issue(
                    errors,
                    "missing_publication_evidence",
                    f"Unit {unit_id} has no exact publication_evidence excerpts.",
                    unit_id=unit_id,
                )
            else:
                evidence_results = [
                    exact_excerpt_present(
                        excerpt,
                        document,
                        errors,
                        "invalid_publication_evidence",
                        unit_id,
                        f"publication_evidence[{index}]",
                    )
                    for index, excerpt in enumerate(evidence)
                ]
                evidence_valid = bool(evidence_results) and all(evidence_results)
            if evidence_valid:
                publication_evidence_units += 1

            is_example = unit_type in EXAMPLE_UNIT_TYPES or assertion_kind == "example"
            if is_example:
                example_units += 1
                representation = entry.get("example_representation")
                if not isinstance(representation, dict):
                    add_issue(
                        errors,
                        "missing_example_representation",
                        f"Example unit {unit_id} has no example_representation object.",
                        unit_id=unit_id,
                    )
                else:
                    detail_ok = exact_excerpt_present(
                        representation.get("detail_excerpt"),
                        document,
                        errors,
                        "invalid_example_detail_excerpt",
                        unit_id,
                        "example_representation.detail_excerpt",
                    )
                    explanation_ok = exact_excerpt_present(
                        representation.get("explanation_excerpt"),
                        document,
                        errors,
                        "invalid_example_explanation_excerpt",
                        unit_id,
                        "example_representation.explanation_excerpt",
                    )
                    if detail_ok and explanation_ok:
                        if representation.get("detail_excerpt", "").strip() == representation.get("explanation_excerpt", "").strip():
                            add_issue(
                                errors,
                                "example_detail_and_explanation_identical",
                                f"Example unit {unit_id} uses the same excerpt for details and explanation.",
                                unit_id=unit_id,
                            )
                        else:
                            example_exposition_units += 1

    for unit_id in sorted(set(units) - set(disposition_counts)):
        add_issue(errors, "missing_unit_disposition", f"No disposition for unit: {unit_id}")
    for unit_id, count in sorted(disposition_counts.items()):
        if count > 1:
            add_issue(errors, "duplicate_unit_disposition", f"Unit {unit_id} has {count} dispositions")

    for decision in decisions.get("decisions", []):
        if not isinstance(decision, dict):
            continue
        decision_units = set(decision.get("unit_ids", []))
        presentation_units = {
            item.get("unit_id")
            for item in decision.get("unit_presentations", [])
            if isinstance(item, dict)
        }
        for unit_id in sorted(decision_units - presentation_units):
            add_issue(errors, "decision_unit_without_presentation", f"Decision omits presentation for unit: {unit_id}")

    source_count = len(inventory_sources)
    dispositioned = len(set(units) & set(disposition_counts))
    nonstructural = sum(1 for unit in units.values() if unit.get("unit_type") not in STRUCTURAL_UNIT_TYPES)
    return {
        "source_files": source_count,
        "sources_used": len(used & set(inventory_sources)),
        "source_coverage": round(len(used & set(inventory_sources)) / source_count, 4) if source_count else 0.0,
        "source_nonempty_lines": total_nonempty,
        "covered_nonempty_lines": covered_nonempty,
        "source_line_coverage": round(covered_nonempty / total_nonempty, 4) if total_nonempty else 1.0,
        "extracted_units": len(units),
        "units_with_dispositions": dispositioned,
        "unit_disposition_coverage": round(dispositioned / len(units), 4) if units else 0.0,
        "nonstructural_units": nonstructural,
        "nonstructural_units_with_final_representation": represented_nonstructural,
        "unit_final_representation_coverage": round(represented_nonstructural / nonstructural, 4) if nonstructural else 1.0,
        "nonstructural_units_with_publication_evidence": publication_evidence_units,
        "publication_evidence_coverage": round(publication_evidence_units / nonstructural, 4) if nonstructural else 1.0,
        "example_units": example_units,
        "example_units_with_complete_exposition": example_exposition_units,
        "example_exposition_coverage": round(example_exposition_units / example_units, 4) if example_units else 1.0,
        "input_source_reference_violations": reference_violations,
        "meta_source_phrase_violations": meta_source_violations,
    }


def main() -> int:
    args = parse_args()
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    try:
        document = args.document.read_text(encoding="utf-8")
    except FileNotFoundError:
        add_issue(errors, "missing_document", f"Missing document: {args.document}")
        document = ""
    except OSError as exc:
        add_issue(errors, "document_read_error", str(exc))
        document = ""

    if not document.strip():
        add_issue(errors, "empty_document", "Final document is empty.")
    else:
        markdown_checks(document, errors, warnings)

    inventory = load_json(args.inventory, errors, "inventory_read_error")
    coverage_map = load_json(args.coverage_map, errors, "coverage_map_read_error")
    decisions = load_json(args.decisions, errors, "decisions_read_error") if args.decisions else {}
    units, _, total_nonempty, covered_nonempty = load_units(args.units_dir, inventory, errors)
    reference_violations = validate_publication_independence(document, inventory, units, errors)
    meta_source_violations = validate_standalone_exposition(document, errors)
    metrics = validate_coverage_map(
        inventory,
        units,
        coverage_map,
        decisions,
        errors,
        warnings,
        total_nonempty,
        covered_nonempty,
        reference_violations,
        meta_source_violations,
        document,
    )

    report = {
        "schema_version": "2.2",
        "status": "failed" if errors else "passed",
        "errors": errors,
        "warnings": warnings,
        "metrics": metrics,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Validation {report['status']}: {len(errors)} error(s), {len(warnings)} warning(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
