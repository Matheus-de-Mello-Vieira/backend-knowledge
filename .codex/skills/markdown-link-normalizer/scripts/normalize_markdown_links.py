#!/usr/bin/env python3
"""Normalize local Markdown links in an Obsidian vault.

The script converts resolvable Obsidian Wikilinks to standard Markdown links,
rewrites local Markdown destinations with URL-encoded paths, and converts
heading anchors to exact heading-text anchors when the target heading exists.
External URLs, mailto links, embeds, YAML frontmatter, and fenced/inline code
are left unchanged.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.parse
from collections import defaultdict
from pathlib import Path


MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\n]+)\)")
WIKILINK_RE = re.compile(r"(?<!!)\[\[([^\]\n]+)\]\]")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")


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
                if re.match(r"^#{1,6}\s+", line):
                    heading = strip_heading_markup(line)
                    by_slug.setdefault(slug_heading(line), heading)
                    by_plain.setdefault(heading.lower(), heading)

        self._cache[resolved] = (by_slug, by_plain)
        return self._cache[resolved]


class VaultIndex:
    """Resolve Obsidian Wikilink file targets within a vault root."""

    def __init__(self, vault_root: Path) -> None:
        self.root = vault_root.resolve()
        self._by_basename: dict[str, list[Path]] = defaultdict(list)
        self._by_relative: dict[str, Path] = {}

        for path in sorted(p for p in self.root.rglob("*") if p.is_file()):
            relative = path.relative_to(self.root).as_posix()
            self._by_relative[relative.lower()] = path.resolve()
            self._by_basename[path.name.lower()].append(path.resolve())
            if path.suffix.lower() == ".md":
                self._by_relative[relative[:-3].lower()] = path.resolve()
                self._by_basename[path.stem.lower()].append(path.resolve())

    def resolve(self, source: Path, wikilink_path: str) -> tuple[Path | None, str | None]:
        decoded = urllib.parse.unquote(wikilink_path).strip().replace("\\", "/")
        if not decoded:
            return source.resolve(), None

        # Prefer a same-folder target for a bare name.
        if "/" not in decoded:
            candidate = source.parent / decoded
            candidates = [candidate]
            if not candidate.suffix:
                candidates.insert(0, candidate.with_suffix(".md"))
            for item in candidates:
                if item.exists() and item.is_file():
                    return item.resolve(), None

        # Obsidian documents explicit folder paths as vault-root relative.
        relative_key = decoded.lstrip("/").lower()
        exact = self._by_relative.get(relative_key)
        if exact is not None:
            return exact, None

        if not Path(decoded).suffix:
            exact = self._by_relative.get((decoded.lstrip("/") + ".md").lower())
            if exact is not None:
                return exact, None

        if "/" not in decoded:
            names = [decoded.lower()]
            if not Path(decoded).suffix:
                names.insert(0, (decoded + ".md").lower())
            matches: set[Path] = set()
            for name in names:
                matches.update(self._by_basename.get(name, []))
            if len(matches) == 1:
                return next(iter(matches)), None
            if len(matches) > 1:
                return None, "ambiguous"

        return None, "missing"


def encode_path(path: str) -> str:
    return urllib.parse.quote(path, safe="/.-_")


def encode_anchor(anchor: str) -> str:
    return urllib.parse.quote(anchor, safe="-_.~:")


def is_external(destination: str) -> bool:
    return "://" in destination or destination.startswith("mailto:")


def normalized_relative_path(source: Path, target: Path) -> str:
    relative = os.path.relpath(target.resolve(), start=source.parent.resolve()).replace(os.sep, "/")
    if relative == ".":
        relative = ""
    if relative.startswith("./"):
        relative = relative[2:]
    return encode_path(relative)


def normalize_anchor(target: Path, anchor: str, headings: HeadingCache) -> str:
    decoded_anchor = urllib.parse.unquote(anchor)
    by_slug, by_plain = headings.maps_for(target)
    heading = by_slug.get(decoded_anchor.lower()) or by_plain.get(decoded_anchor.lower()) or decoded_anchor
    return encode_anchor(heading)


def normalize_destination(source: Path, destination: str, headings: HeadingCache) -> str:
    destination = destination.strip()
    if not destination or is_external(destination):
        return destination

    if destination.startswith("#"):
        return "#" + normalize_anchor(source, destination[1:], headings)

    path_part, separator, anchor = destination.partition("#")
    decoded_path = urllib.parse.unquote(path_part)
    target = (source.parent / decoded_path).resolve()
    if not target.exists():
        return destination

    normalized = normalized_relative_path(source, target)
    if separator:
        normalized += "#" + normalize_anchor(target, anchor, headings)

    return normalized


def wikilink_to_markdown(
    source: Path,
    body: str,
    vault: VaultIndex,
    headings: HeadingCache,
) -> tuple[str | None, str | None]:
    target_spec, alias_separator, alias = body.partition("|")
    target_spec = target_spec.strip()
    alias = alias.strip()

    # These are Obsidian search/block syntaxes without a portable equivalent.
    if target_spec.startswith("##") or target_spec.startswith("^^") or "#^" in target_spec:
        return None, "obsidian-specific"

    path_part, separator, anchor = target_spec.partition("#")
    target, error = vault.resolve(source, path_part)
    if target is None:
        return None, error

    # Preserve what Obsidian displays when no custom alias is present.
    label = alias if alias_separator else target_spec
    if not label:
        label = anchor if separator else target.stem

    destination = normalized_relative_path(source, target)
    if separator:
        destination += "#" + normalize_anchor(target, anchor, headings)

    return f"[{label}]({destination})", None


def transform_outside_inline_code(text: str, transform) -> str:
    """Apply transform to text segments outside backtick code spans."""
    result: list[str] = []
    position = 0
    while position < len(text):
        match = re.search(r"`+", text[position:])
        if match is None:
            result.append(transform(text[position:]))
            break

        start = position + match.start()
        delimiter = match.group(0)
        result.append(transform(text[position:start]))
        close = text.find(delimiter, start + len(delimiter))
        if close == -1:
            result.append(transform(text[start:]))
            break

        end = close + len(delimiter)
        result.append(text[start:end])
        position = end

    return "".join(result)


def normalize_file(
    path: Path,
    vault: VaultIndex,
    headings: HeadingCache,
) -> tuple[bool, str, list[tuple[int, str, str]]]:
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    updated_lines: list[str] = []
    unresolved: list[tuple[int, str, str]] = []

    in_frontmatter = bool(lines and lines[0].strip() == "---")
    in_fence = False
    fence_char = ""
    fence_len = 0

    for line_number, line in enumerate(lines, 1):
        if in_frontmatter:
            updated_lines.append(line)
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
            updated_lines.append(line)
            continue

        if in_fence:
            updated_lines.append(line)
            continue

        def transform(segment: str) -> str:
            def replace_wikilink(match: re.Match[str]) -> str:
                body = match.group(1)
                converted, reason = wikilink_to_markdown(path, body, vault, headings)
                if converted is None:
                    if reason != "obsidian-specific":
                        unresolved.append((line_number, match.group(0), reason or "unresolved"))
                    return match.group(0)
                return converted

            segment = WIKILINK_RE.sub(replace_wikilink, segment)

            def replace_markdown(match: re.Match[str]) -> str:
                label = match.group(1)
                destination = match.group(2)
                normalized = normalize_destination(path, destination, headings)
                return f"[{label}]({normalized})"

            return MARKDOWN_LINK_RE.sub(replace_markdown, segment)

        updated_lines.append(transform_outside_inline_code(line, transform))

    updated = "".join(updated_lines)
    return updated != original, updated, unresolved


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert Obsidian Wikilinks and normalize local Markdown links."
    )
    parser.add_argument("root", nargs="?", default=".", help="Obsidian vault root, Markdown file, or directory to process.")
    parser.add_argument("--check", action="store_true", help="Report files that would change without writing.")
    args = parser.parse_args()

    root = Path(args.root)
    vault_root = root.parent if root.is_file() else root
    files = [root] if root.is_file() else sorted(root.rglob("*.md"))
    headings = HeadingCache()
    vault = VaultIndex(vault_root)
    changed: list[Path] = []
    unresolved: list[tuple[Path, int, str, str]] = []

    for path in files:
        did_change, updated, file_unresolved = normalize_file(path, vault, headings)
        unresolved.extend((path, line, link, reason) for line, link, reason in file_unresolved)
        if did_change:
            changed.append(path)
            if not args.check:
                path.write_text(updated, encoding="utf-8")

    for path in changed:
        print(path)
    print(f"changed={len(changed)}")
    print(f"unresolved_wikilinks={len(unresolved)}")
    for path, line, link, reason in unresolved:
        print(f"{path}:{line} -> {link} ({reason})")

    return 1 if (args.check and changed) or unresolved else 0


if __name__ == "__main__":
    sys.exit(main())
