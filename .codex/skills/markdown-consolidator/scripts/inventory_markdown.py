#!/usr/bin/env python3
"""Inventory Markdown files for the markdown-consolidator skill."""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recursively inventory readable Markdown files."
    )
    parser.add_argument("source_root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Glob relative to source_root; may be repeated.",
    )
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Exit successfully when no Markdown files are found.",
    )
    return parser.parse_args()


def excluded(relative_path: str, patterns: list[str]) -> bool:
    normalized = relative_path.replace("\\", "/")
    return any(
        fnmatch.fnmatch(normalized, pattern)
        or fnmatch.fnmatch(f"/{normalized}", pattern)
        for pattern in patterns
    )


def source_id(relative_path: str, digest: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", relative_path.lower()).strip("-")
    slug = slug[:56] or "markdown-source"
    return f"{slug}-{digest[:8]}"


def read_source(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError(f"not valid UTF-8: {exc}") from exc
    return text, digest


def extract_headings(lines: list[str]) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    in_fence = False
    fence_marker = ""

    for number, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            continue
        if in_fence:
            continue
        match = HEADING_RE.match(line)
        if match:
            headings.append(
                {
                    "level": len(match.group(1)),
                    "text": match.group(2).strip(),
                    "line": number,
                }
            )
    return headings


def build_inventory(root: Path, patterns: list[str]) -> dict[str, Any]:
    root = root.resolve()
    result: dict[str, Any] = {
        "schema_version": "2.0",
        "root": str(root),
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "sources": [],
        "errors": [],
    }

    if not root.exists():
        result["errors"].append({"path": str(root), "error": "path does not exist"})
        return result

    candidates = [root] if root.is_file() else sorted(root.rglob("*.md"))
    for path in candidates:
        if not path.is_file() or path.suffix.lower() != ".md":
            continue
        try:
            relative = path.relative_to(root if root.is_dir() else root.parent)
        except ValueError:
            relative = Path(path.name)
        relative_str = relative.as_posix()
        if excluded(relative_str, patterns):
            continue
        try:
            text, digest = read_source(path)
            lines = text.splitlines()
            result["sources"].append(
                {
                    "source_id": source_id(relative_str, digest),
                    "path": relative_str,
                    "absolute_path": str(path.resolve()),
                    "sha256": digest,
                    "bytes": path.stat().st_size,
                    "line_count": len(lines),
                    "headings": extract_headings(lines),
                }
            )
        except (OSError, ValueError) as exc:
            result["errors"].append({"path": relative_str, "error": str(exc)})

    return result


def main() -> int:
    args = parse_args()
    inventory = build_inventory(args.source_root, args.exclude)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(inventory, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    if inventory["errors"]:
        print(
            f"Inventory completed with {len(inventory['errors'])} error(s).",
            file=sys.stderr,
        )
    print(f"Inventoried {len(inventory['sources'])} Markdown file(s).")

    if not inventory["sources"] and not args.allow_empty:
        return 2
    return 1 if inventory["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
