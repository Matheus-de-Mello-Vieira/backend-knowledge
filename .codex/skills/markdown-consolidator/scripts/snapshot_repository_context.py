#!/usr/bin/env python3
"""Snapshot durable destination and context notes before integration."""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
from pathlib import Path
from typing import Any

from common import SCHEMA_VERSION, dump_json, load_json

HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Snapshot destination and context notes.")
    parser.add_argument("--placement", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--snapshot-root", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def headings(text: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
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
        if in_fence:
            continue
        match = HEADING_RE.match(line)
        if match:
            result.append({"level": len(match.group(1)), "text": match.group(2).strip(), "line": number})
    return result


def main() -> int:
    args = parse_args()
    root = args.repository_root.resolve()
    placement = load_json(args.placement)
    errors: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    roles: dict[str, str] = {}
    for item in placement.get("destinations", []):
        if isinstance(item, dict) and item.get("path"):
            roles[str(item["path"])] = "destination"
    for item in placement.get("related_notes", []):
        if isinstance(item, dict) and item.get("path") and str(item["path"]) not in roles:
            roles[str(item["path"])] = "context"

    if args.snapshot_root.exists():
        shutil.rmtree(args.snapshot_root)
    args.snapshot_root.mkdir(parents=True, exist_ok=True)

    for relative, role in sorted(roles.items()):
        source = (root / relative).resolve()
        try:
            source.relative_to(root)
        except ValueError:
            errors.append({"code": "path_outside_repository", "path": relative})
            continue
        if not source.exists():
            if role == "destination":
                records.append({"path": relative, "role": role, "exists": False, "snapshot_path": None, "sha256": None, "headings": []})
                continue
            errors.append({"code": "context_note_missing", "path": relative})
            continue
        try:
            raw = source.read_bytes()
            text = raw.decode("utf-8-sig")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append({"code": "snapshot_read_error", "path": relative, "message": str(exc)})
            continue
        destination = args.snapshot_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        records.append({
            "path": relative,
            "role": role,
            "exists": True,
            "snapshot_path": str(destination.resolve()),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "line_count": len(text.splitlines()),
            "headings": headings(text),
        })

    index = {"schema_version": SCHEMA_VERSION, "repository_root": str(root), "notes": records}
    dump_json(args.index, index)
    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "warnings": [],
        "metrics": {"snapshotted_notes": sum(1 for item in records if item.get("exists")), "declared_notes": len(roles)},
    }
    dump_json(args.report, report)
    print(report["status"])
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
