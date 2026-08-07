#!/usr/bin/env python3
"""Validate observable publication-writing rules without replacing semantic review."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path
from typing import Any

from common import SCHEMA_VERSION, dump_json

BLOCKED_GENERIC_HEADINGS = {
    "details", "information", "miscellaneous", "other", "more", "general", "content",
}
REVIEW_GENERIC_HEADINGS = {"notes", "background", "additional information"}
BLOCKED_PHRASES = [
    r"\bmake it better\b",
    r"\bmake (?:it|this) engaging\b",
    r"\bimprove the flow\b",
    r"\balign stakeholders\b",
    r"\bfollow best practices\b",
    r"\bhandle(?:d)? appropriately\b",
]
CEREMONIAL_PHRASES = [
    r"\bin today['’]s rapidly evolving\b",
    r"\bit is important to note that\b",
    r"\bthis (?:document|section|guide) (?:aims|seeks) to\b",
    r"\bwithout further ado\b",
    r"\bin conclusion,? it can be said\b",
]
UNRESOLVED_PLACEHOLDERS = [
    r"\b(?:TODO|TBD|FIXME|XXX)\b",
    r"\{\{[^{}]+\}\}",
    r"\[insert [^\]]+\]",
]
WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
LIST_RE = re.compile(r"^\s*(?:[-+*]|\d+[.)])\s+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate observable writing rules in a standalone Markdown publication.")
    parser.add_argument("--document", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--paragraph-warning-words", type=int, default=180)
    parser.add_argument("--intro-warning-words", type=int, default=250)
    return parser.parse_args()


def strip_fenced_code(text: str) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    in_fence = False
    fence = ""
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_fence:
                in_fence, fence = True, marker
            elif marker == fence:
                in_fence, fence = False, ""
            continue
        if not in_fence:
            result.append((number, line))
    return result


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def paragraph_blocks(lines: list[tuple[int, str]]) -> list[tuple[int, int, str]]:
    blocks: list[tuple[int, int, str]] = []
    current: list[str] = []
    start = 0
    end = 0
    for number, line in lines + [(10**9, "")]:
        stripped = line.strip()
        boundary = not stripped or HEADING_RE.match(stripped) or LIST_RE.match(line) or stripped.startswith("|") or stripped.startswith(">")
        if boundary:
            if current:
                blocks.append((start, end, " ".join(current)))
                current = []
            continue
        if not current:
            start = number
        current.append(stripped)
        end = number
    return blocks


def main() -> int:
    args = parse_args()
    text = args.document.read_text(encoding="utf-8")
    lines = strip_fenced_code(text)
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    headings: list[tuple[int, int, str]] = []
    previous_level = 0
    for number, line in lines:
        match = HEADING_RE.match(line.strip())
        if not match:
            continue
        level = len(match.group(1))
        heading = match.group(2).strip().rstrip("#").strip()
        headings.append((number, level, heading))
        if previous_level and level > previous_level + 1:
            errors.append({"code": "heading_level_jump", "line": number, "from_level": previous_level, "to_level": level, "heading": heading})
        previous_level = level
        normalized = re.sub(r"[^a-z0-9]+", " ", heading.lower()).strip()
        if normalized in BLOCKED_GENERIC_HEADINGS:
            errors.append({"code": "generic_heading", "line": number, "heading": heading})
        elif normalized in REVIEW_GENERIC_HEADINGS:
            warnings.append({"code": "possibly_generic_heading", "line": number, "heading": heading})

    h1_count = sum(1 for _, level, _ in headings if level == 1)
    if h1_count != 1:
        errors.append({"code": "invalid_h1_count", "count": h1_count})

    normalized_headings = [re.sub(r"[^a-z0-9]+", " ", h.lower()).strip() for _, _, h in headings]
    duplicates = sorted(name for name, count in Counter(normalized_headings).items() if name and count > 1)
    if duplicates:
        warnings.append({"code": "duplicate_heading_text", "headings": duplicates})

    first_h2_line = next((number for number, level, _ in headings if level == 2), None)
    first_h1_line = next((number for number, level, _ in headings if level == 1), 0)
    pre_section_lines = [line for number, line in lines if number > first_h1_line and (first_h2_line is None or number < first_h2_line)]
    pre_section_text = "\n".join(pre_section_lines)
    substantive_intro = " ".join(
        line.strip() for line in pre_section_lines
        if line.strip() and not line.strip().startswith("<!--")
    )
    if word_count(substantive_intro) < 5:
        warnings.append({"code": "missing_early_main_point", "detail": "Confirm that the requested format justifies omitting a substantive opening statement; otherwise add one before the first major section."})
    intro_words = word_count(pre_section_text)
    if intro_words > args.intro_warning_words:
        warnings.append({"code": "long_introduction", "word_count": intro_words, "threshold": args.intro_warning_words})

    prose = "\n".join(line for _, line in lines)
    for pattern in BLOCKED_PHRASES:
        for match in re.finditer(pattern, prose, flags=re.IGNORECASE):
            errors.append({"code": "vague_nonoperational_phrase", "excerpt": match.group(0), "pattern": pattern})
    for pattern in CEREMONIAL_PHRASES:
        for match in re.finditer(pattern, prose, flags=re.IGNORECASE):
            warnings.append({"code": "ceremonial_or_delaying_phrase", "excerpt": match.group(0), "pattern": pattern})
    for pattern in UNRESOLVED_PLACEHOLDERS:
        for match in re.finditer(pattern, prose, flags=re.IGNORECASE):
            errors.append({"code": "unresolved_placeholder", "excerpt": match.group(0), "pattern": pattern})

    paragraphs = paragraph_blocks(lines)
    long_paragraphs = []
    for start, end, paragraph in paragraphs:
        count = word_count(paragraph)
        if count > args.paragraph_warning_words:
            long_paragraphs.append({"start_line": start, "end_line": end, "word_count": count})
    if long_paragraphs:
        warnings.append({"code": "dense_paragraphs", "items": long_paragraphs})

    total_words = word_count(prose)
    heading_count = len(headings)
    if total_words >= 200 and heading_count > max(8, total_words // 45):
        warnings.append({"code": "possible_excessive_fragmentation", "headings": heading_count, "words": total_words})

    list_items = sum(1 for _, line in lines if LIST_RE.match(line))
    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "words": total_words,
            "headings": heading_count,
            "h1_count": h1_count,
            "paragraphs": len(paragraphs),
            "long_paragraphs": len(long_paragraphs),
            "list_items": list_items,
            "intro_words": intro_words,
            "blocked_phrase_violations": sum(1 for item in errors if item.get("code") == "vague_nonoperational_phrase"),
            "unresolved_placeholders": sum(1 for item in errors if item.get("code") == "unresolved_placeholder"),
        },
    }
    dump_json(args.report, report)
    print(report["status"])
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
