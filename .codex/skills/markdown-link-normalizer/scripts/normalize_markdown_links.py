#!/usr/bin/env python3
"""Normalize local inline Markdown links.

The script rewrites local file paths with URL-encoded spaces and converts
heading anchors to exact heading text anchors when the target heading exists.
External URLs and mailto links are left unchanged.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.parse
from pathlib import Path


LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\n]+)\)")


def strip_heading_markup(line: str) -> str:
    text = re.sub(r"^#{1,6}\s*", "", line).strip()
    return re.sub(r"[*_`]", "", text).strip()


def slug_heading(line: str) -> str:
    text = strip_heading_markup(line).lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", "-", text.strip())


class HeadingCache:
    def __init__(self) -> None:
        self._cache: dict[Path, tuple[dict[str, str], dict[str, str]]] = {}

    def maps_for(self, path: Path) -> tuple[dict[str, str], dict[str, str]]:
        resolved = path.resolve()
        if resolved in self._cache:
            return self._cache[resolved]

        by_slug: dict[str, str] = {}
        by_plain: dict[str, str] = {}
        if resolved.exists() and resolved.suffix.lower() == ".md":
            for line in resolved.read_text(encoding="utf-8").splitlines():
                if line.startswith("#"):
                    heading = strip_heading_markup(line)
                    by_slug.setdefault(slug_heading(line), heading)
                    by_plain.setdefault(heading.lower(), heading)

        self._cache[resolved] = (by_slug, by_plain)
        return self._cache[resolved]


def encode_path(path: str) -> str:
    return urllib.parse.quote(path, safe="/.-_")


def encode_anchor(anchor: str) -> str:
    return urllib.parse.quote(anchor, safe="-_.~:")


def is_external(destination: str) -> bool:
    return "://" in destination or destination.startswith("mailto:")


def normalize_destination(source: Path, destination: str, headings: HeadingCache) -> str:
    destination = destination.strip()
    if not destination or is_external(destination):
        return destination

    if destination.startswith("#"):
        decoded_anchor = urllib.parse.unquote(destination[1:])
        by_slug, by_plain = headings.maps_for(source)
        heading = by_slug.get(decoded_anchor.lower()) or by_plain.get(decoded_anchor.lower()) or decoded_anchor
        return "#" + encode_anchor(heading)

    path_part, separator, anchor = destination.partition("#")
    decoded_path = urllib.parse.unquote(path_part)
    target = (source.parent / decoded_path).resolve()
    if not target.exists():
        return destination

    relative = os.path.relpath(target, start=source.parent.resolve()).replace(os.sep, "/")
    if relative == ".":
        relative = ""
    if relative.startswith("./"):
        relative = relative[2:]

    normalized = encode_path(relative)
    if separator:
        decoded_anchor = urllib.parse.unquote(anchor)
        by_slug, by_plain = headings.maps_for(target)
        heading = by_slug.get(decoded_anchor.lower()) or by_plain.get(decoded_anchor.lower()) or decoded_anchor
        normalized += "#" + encode_anchor(heading)

    return normalized


def normalize_file(path: Path, headings: HeadingCache) -> tuple[bool, str]:
    original = path.read_text(encoding="utf-8")

    def replace(match: re.Match[str]) -> str:
        label = match.group(1)
        destination = match.group(2)
        normalized = normalize_destination(path, destination, headings)
        return f"[{label}]({normalized})"

    updated = LINK_RE.sub(replace, original)
    return updated != original, updated


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize local inline Markdown links.")
    parser.add_argument("root", nargs="?", default=".", help="Markdown file or directory to process.")
    parser.add_argument("--check", action="store_true", help="Report files that would change without writing.")
    args = parser.parse_args()

    root = Path(args.root)
    files = [root] if root.is_file() else sorted(root.rglob("*.md"))
    headings = HeadingCache()
    changed: list[Path] = []

    for path in files:
        did_change, updated = normalize_file(path, headings)
        if did_change:
            changed.append(path)
            if not args.check:
                path.write_text(updated, encoding="utf-8")

    for path in changed:
        print(path)
    print(f"changed={len(changed)}")

    return 1 if args.check and changed else 0


if __name__ == "__main__":
    sys.exit(main())

