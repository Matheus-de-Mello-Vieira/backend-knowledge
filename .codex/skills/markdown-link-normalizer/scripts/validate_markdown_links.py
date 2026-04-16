#!/usr/bin/env python3
"""Validate local inline Markdown link file and heading targets."""

from __future__ import annotations

import argparse
import re
import sys
import urllib.parse
from pathlib import Path


LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)\n]+)\)")


def strip_heading_markup(line: str) -> str:
    text = re.sub(r"^#{1,6}\s*", "", line).strip()
    return re.sub(r"[*_`]", "", text).strip()


def slug_heading(line: str) -> str:
    text = strip_heading_markup(line).lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", "-", text.strip())


def is_external(destination: str) -> bool:
    return "://" in destination or destination.startswith("mailto:")


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
                if line.startswith("#"):
                    slugs.add(slug_heading(line))
                    plain.add(strip_heading_markup(line).lower())

        self._cache[resolved] = (slugs, plain)
        return self._cache[resolved]


def validate(root: Path) -> tuple[list[tuple[Path, int, str]], list[tuple[Path, int, str]]]:
    files = [root] if root.is_file() else sorted(root.rglob("*.md"))
    headings = HeadingCache()
    missing_files: list[tuple[Path, int, str]] = []
    missing_anchors: list[tuple[Path, int, str]] = []

    for source in files:
        for line_number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
            for match in LINK_RE.finditer(line):
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

    return missing_files, missing_anchors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate local inline Markdown links.")
    parser.add_argument("root", nargs="?", default=".", help="Markdown file or directory to validate.")
    args = parser.parse_args()

    missing_files, missing_anchors = validate(Path(args.root))

    print(f"missing_files={len(missing_files)}")
    for source, line_number, destination in missing_files:
        print(f"{source}:{line_number} -> {destination}")

    print(f"missing_anchors={len(missing_anchors)}")
    for source, line_number, destination in missing_anchors:
        print(f"{source}:{line_number} -> {destination}")

    return 1 if missing_files or missing_anchors else 0


if __name__ == "__main__":
    sys.exit(main())

