#!/usr/bin/env python3
"""Extract non-presentational study context from an Obsidian workspace file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable


def unique(values: Iterable[str]) -> list[str]:
    """Return non-empty strings in first-seen order."""
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def markdown_path(value: Any) -> str | None:
    """Keep only vault-relative Markdown paths."""
    if not isinstance(value, str):
        return None
    path = Path(value)
    if path.suffix.lower() != ".md" or path.is_absolute() or ".." in path.parts:
        return None
    return path.as_posix()


def leaves(value: Any) -> Iterable[dict[str, Any]]:
    """Yield every leaf in Obsidian's nested workspace tree."""
    if not isinstance(value, dict):
        return
    if value.get("type") == "leaf":
        yield value
    for child in value.get("children", []):
        yield from leaves(child)


def extract_context(workspace: dict[str, Any], recent_limit: int) -> dict[str, Any]:
    all_leaves = list(
        leaf
        for key in ("main", "left", "right")
        for leaf in leaves(workspace.get(key))
    )

    open_notes: list[str] = []
    backlink_notes: list[str] = []
    outgoing_link_notes: list[str] = []
    search_queries: list[str] = []
    active_note: str | None = None

    for leaf in all_leaves:
        state = leaf.get("state")
        if not isinstance(state, dict):
            continue
        leaf_type = state.get("type")
        state_data = state.get("state")
        if not isinstance(state_data, dict):
            continue

        if leaf_type == "markdown":
            note = markdown_path(state_data.get("file"))
            if note:
                open_notes.append(note)
                if leaf.get("id") == workspace.get("active"):
                    active_note = note
        elif leaf_type == "backlink":
            note = markdown_path(state_data.get("file"))
            if note:
                backlink_notes.append(note)
        elif leaf_type == "outgoing-link":
            note = markdown_path(state_data.get("file"))
            if note:
                outgoing_link_notes.append(note)
        elif leaf_type == "search":
            query = state_data.get("query")
            if isinstance(query, str) and query.strip():
                search_queries.append(query.strip())

    recent_notes = unique(
        note
        for value in workspace.get("lastOpenFiles", [])
        if (note := markdown_path(value)) is not None
    )[:recent_limit]

    return {
        "active_note": active_note,
        "open_notes": unique(open_notes),
        "recent_notes": recent_notes,
        "related_note_targets": {
            "backlinks": unique(backlink_notes),
            "outgoing_links": unique(outgoing_link_notes),
        },
        "search_queries": unique(search_queries),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract relevant Markdown-note context from Obsidian workspace.json."
    )
    parser.add_argument(
        "workspace",
        nargs="?",
        type=Path,
        default=Path(".obsidian/workspace.json"),
        help="workspace.json path (default: .obsidian/workspace.json)",
    )
    parser.add_argument(
        "--recent-limit",
        type=int,
        default=10,
        help="maximum recent Markdown notes to include (default: 10)",
    )
    args = parser.parse_args()
    if args.recent_limit < 0:
        parser.error("--recent-limit must be zero or greater")
    return args


def main() -> int:
    args = parse_args()
    try:
        workspace = json.loads(args.workspace.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"Workspace file not found: {args.workspace}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as error:
        print(f"Invalid JSON in {args.workspace}: {error}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"Unable to read {args.workspace}: {error}", file=sys.stderr)
        return 2

    if not isinstance(workspace, dict):
        print(f"Workspace root must be an object: {args.workspace}", file=sys.stderr)
        return 2

    print(json.dumps(extract_context(workspace, args.recent_limit), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
