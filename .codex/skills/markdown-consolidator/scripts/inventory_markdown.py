#!/usr/bin/env python3
"""Inventory Markdown files for the markdown-consolidator skill."""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import hashlib
import re
import sys
from pathlib import Path
from typing import Any

from common import SCHEMA_VERSION, dump_json

HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recursively inventory readable Markdown files.")
    parser.add_argument("source_root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--exclude", action="append", default=[], help="Glob relative to source_root; repeatable.")
    parser.add_argument("--allow-empty", action="store_true")
    return parser.parse_args()


def excluded(relative_path: str, patterns: list[str]) -> bool:
    normalized = relative_path.replace("\\", "/")
    return any(
        fnmatch.fnmatch(normalized, pattern)
        or fnmatch.fnmatch(f"/{normalized}", pattern)
        for pattern in patterns
    )


def make_source_id(relative_path: str, digest: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", relative_path.lower()).strip("-")
    return f"{(slug[:56] or 'markdown-source')}-{digest[:8]}"


def extract_headings(lines: list[str]) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    in_fence = False
    fence = ""
    for number, line in enumerate(lines, start=1):
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
            headings.append({"level": len(match.group(1)), "text": match.group(2).strip(), "line": number})
    return headings


def main() -> int:
    args = parse_args()
    root = args.source_root.resolve()
    inventory: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "root": str(root if root.is_dir() else root.parent),
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "sources": [],
        "errors": [],
    }

    if not root.exists():
        inventory["errors"].append({"path": str(root), "error": "path does not exist"})
    else:
        candidates = [root] if root.is_file() else sorted(root.rglob("*.md"))
        base = root if root.is_dir() else root.parent
        for path in candidates:
            if not path.is_file() or path.suffix.lower() != ".md":
                continue
            relative = path.relative_to(base).as_posix()
            if excluded(relative, args.exclude):
                continue
            try:
                raw = path.read_bytes()
                text = raw.decode("utf-8-sig")
                digest = hashlib.sha256(raw).hexdigest()
                lines = text.splitlines()
                inventory["sources"].append(
                    {
                        "source_id": make_source_id(relative, digest),
                        "path": relative,
                        "absolute_path": str(path.resolve()),
                        "sha256": digest,
                        "bytes": len(raw),
                        "line_count": len(lines),
                        "nonempty_line_count": sum(1 for line in lines if line.strip()),
                        "headings": extract_headings(lines),
                    }
                )
            except (OSError, UnicodeDecodeError) as exc:
                inventory["errors"].append({"path": relative, "error": str(exc)})

    dump_json(args.output, inventory)
    print(f"Inventoried {len(inventory['sources'])} Markdown file(s).")
    if inventory["errors"]:
        print(f"Inventory contains {len(inventory['errors'])} error(s).", file=sys.stderr)
    if not inventory["sources"] and not args.allow_empty:
        return 2
    return 1 if inventory["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
