#!/usr/bin/env python3
"""Validate normalized local Markdown links in an Obsidian vault."""

from __future__ import annotations

import argparse
import re
import sys
import urllib.parse
from pathlib import Path


MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)\n]+)\)")
WIKILINK_RE = re.compile(r"(?<!!)\[\[([^\]\n]+)\]\]")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")


def strip_heading_markup(line: str) -> str:
    text = re.sub(r"^#{1,6}\s*", "", line).strip()
    return re.sub(r"[*_`]", "", text).strip()


def slug_heading(line: str) -> str:
    text = strip_heading_markup(line).lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", "-", text.strip())


def is_external(destination: str) -> bool:
    return "://" in destination or destination.startswith("mailto:")


def is_obsidian_specific_wikilink(body: str) -> bool:
    target_spec = body.partition("|")[0].strip()
    return target_spec.startswith("##") or target_spec.startswith("^^") or "#^" in target_spec


class HeadingCache:
    def __init__(self) -> None:
        self._cache: dict[Path, tuple[set[str], set[str]]] = {}

    def headings_for(self, path: Path) -> tuple[set[str], set[str]]:
        resolved = path.resolve()
        if resolved in self._cache:
            return self._cache[resolved]

        slugs: set[str] = set()
        plain: set[str] = set()
        if resolved.exists() and resolved.suffix.lower() == ".md":
            for line in resolved.read_text(encoding="utf-8").splitlines():
                if re.match(r"^#{1,6}\s+", line):
                    slugs.add(slug_heading(line))
                    plain.add(strip_heading_markup(line).lower())

        self._cache[resolved] = (slugs, plain)
        return self._cache[resolved]


def segments_outside_inline_code(text: str) -> list[str]:
    segments: list[str] = []
    position = 0
    while position < len(text):
        match = re.search(r"`+", text[position:])
        if match is None:
            segments.append(text[position:])
            break
        start = position + match.start()
        if start > position:
            segments.append(text[position:start])
        delimiter = match.group(0)
        close = text.find(delimiter, start + len(delimiter))
        if close == -1:
            break
        position = close + len(delimiter)
    return segments


def validate(
    root: Path,
) -> tuple[
    list[tuple[Path, int, str]],
    list[tuple[Path, int, str]],
    list[tuple[Path, int, str]],
]:
    files = [root] if root.is_file() else sorted(root.rglob("*.md"))
    headings = HeadingCache()
    missing_files: list[tuple[Path, int, str]] = []
    missing_anchors: list[tuple[Path, int, str]] = []
    remaining_wikilinks: list[tuple[Path, int, str]] = []

    for source in files:
        lines = source.read_text(encoding="utf-8").splitlines()
        in_frontmatter = bool(lines and lines[0].strip() == "---")
        in_fence = False
        fence_char = ""
        fence_len = 0

        for line_number, line in enumerate(lines, 1):
            if in_frontmatter:
                if line_number > 1 and line.strip() == "---":
                    in_frontmatter = False
                continue

            fence = FENCE_RE.match(line)
            if fence:
                marker = fence.group(1)
                if not in_fence:
                    in_fence = True
                    fence_char = marker[0]
                    fence_len = len(marker)
                elif marker[0] == fence_char and len(marker) >= fence_len:
                    in_fence = False
                continue
            if in_fence:
                continue

            for segment in segments_outside_inline_code(line):
                for match in WIKILINK_RE.finditer(segment):
                    if not is_obsidian_specific_wikilink(match.group(1)):
                        remaining_wikilinks.append((source, line_number, match.group(0)))

                for match in MARKDOWN_LINK_RE.finditer(segment):
                    destination = match.group(1).strip()
                    if not destination or is_external(destination):
                        continue

                    path_part, separator, anchor = destination.partition("#")
                    if path_part:
                        target = (source.parent / urllib.parse.unquote(path_part)).resolve()
                        if not target.exists():
                            missing_files.append((source, line_number, destination))
                            continue
                    else:
                        target = source.resolve()

                    if separator and target.suffix.lower() == ".md":
                        anchor_text = urllib.parse.unquote(anchor).lower()
                        slug_set, plain_set = headings.headings_for(target)
                        if anchor_text not in slug_set and anchor_text not in plain_set:
                            missing_anchors.append((source, line_number, destination))

    return missing_files, missing_anchors, remaining_wikilinks


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate normalized local Markdown links.")
    parser.add_argument("root", nargs="?", default=".", help="Markdown file or directory to validate.")
    args = parser.parse_args()

    missing_files, missing_anchors, remaining_wikilinks = validate(Path(args.root))

    print(f"missing_files={len(missing_files)}")
    for source, line_number, destination in missing_files:
        print(f"{source}:{line_number} -> {destination}")

    print(f"missing_anchors={len(missing_anchors)}")
    for source, line_number, destination in missing_anchors:
        print(f"{source}:{line_number} -> {destination}")

    print(f"remaining_wikilinks={len(remaining_wikilinks)}")
    for source, line_number, wikilink in remaining_wikilinks:
        print(f"{source}:{line_number} -> {wikilink}")

    return 1 if missing_files or missing_anchors or remaining_wikilinks else 0


if __name__ == "__main__":
    sys.exit(main())
