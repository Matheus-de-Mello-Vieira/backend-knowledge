#!/usr/bin/env python3
"""Validate a reviewed repository placement plan."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from common import SCHEMA_VERSION, dump_json, load_json

ACTIONS = {"reuse", "extend", "create"}
OUTCOMES = {"reuse_existing_note", "extend_existing_note", "create_new_note", "split_across_notes"}
RELATIONSHIPS = {
    "broader_context", "prerequisite", "implementation_detail", "contrast",
    "alternative", "example", "continuation", "related_mechanism",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate repository note placement.")
    parser.add_argument("--placement", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def safe_relative(root: Path, value: str) -> Path | None:
    path = Path(value)
    if path.is_absolute():
        return None
    resolved = (root / path).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return None
    return resolved


def main() -> int:
    args = parse_args()
    root = args.repository_root.resolve()
    placement = load_json(args.placement)
    inventory = load_json(args.inventory)
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    if placement.get("publication_mode") != "repository_integrated":
        errors.append({"code": "invalid_publication_mode"})
    if placement.get("outcome") not in OUTCOMES:
        errors.append({"code": "invalid_placement_outcome", "value": placement.get("outcome")})
    if placement.get("confidence") not in {"high", "medium", "low"}:
        errors.append({"code": "invalid_placement_confidence"})

    source_paths: set[Path] = set()
    for item in inventory.get("sources", []):
        if not isinstance(item, dict) or not item.get("path"):
            continue
        raw = Path(str(item["path"]))
        source_paths.add(raw.resolve() if raw.is_absolute() else (Path(str(inventory.get("root", root))) / raw).resolve())

    destinations = placement.get("destinations", [])
    if not isinstance(destinations, list) or not destinations:
        errors.append({"code": "missing_destinations"})
        destinations = []
    destination_paths: list[str] = []
    for index, item in enumerate(destinations):
        if not isinstance(item, dict):
            errors.append({"code": "invalid_destination", "index": index})
            continue
        path_text = str(item.get("path", ""))
        action = item.get("action")
        resolved = safe_relative(root, path_text)
        if resolved is None or not path_text.endswith(".md"):
            errors.append({"code": "invalid_destination_path", "path": path_text})
            continue
        destination_paths.append(path_text)
        if action not in ACTIONS:
            errors.append({"code": "invalid_destination_action", "path": path_text, "action": action})
        if resolved in source_paths:
            errors.append({"code": "destination_is_evidence_source", "path": path_text})
        if action in {"reuse", "extend"} and not resolved.is_file():
            errors.append({"code": "existing_destination_missing", "path": path_text})
        if action == "create" and resolved.exists():
            errors.append({"code": "create_destination_already_exists", "path": path_text})
        if not str(item.get("rationale", "")).strip():
            errors.append({"code": "destination_missing_rationale", "path": path_text})

    if len(destination_paths) != len(set(destination_paths)):
        errors.append({"code": "duplicate_destination_paths"})
    if placement.get("outcome") == "split_across_notes" and len(destination_paths) < 2:
        errors.append({"code": "split_requires_multiple_destinations"})
    if placement.get("outcome") != "split_across_notes" and len(destination_paths) != 1:
        errors.append({"code": "single_outcome_requires_one_destination"})
    expected_action = {
        "reuse_existing_note": "reuse",
        "extend_existing_note": "extend",
        "create_new_note": "create",
    }.get(placement.get("outcome"))
    if expected_action and destinations and any(isinstance(item, dict) and item.get("action") != expected_action for item in destinations):
        errors.append({"code": "outcome_action_mismatch", "expected_action": expected_action})

    related = placement.get("related_notes", [])
    context_paths: set[str] = set()
    for index, item in enumerate(related if isinstance(related, list) else []):
        if not isinstance(item, dict):
            errors.append({"code": "invalid_related_note", "index": index})
            continue
        path_text = str(item.get("path", ""))
        resolved = safe_relative(root, path_text)
        if resolved is None or not resolved.is_file():
            errors.append({"code": "related_note_missing", "path": path_text})
            continue
        if path_text in destination_paths:
            errors.append({"code": "destination_repeated_as_context", "path": path_text})
        context_paths.add(path_text)
        if item.get("relationship") not in RELATIONSHIPS:
            errors.append({"code": "invalid_related_note_relationship", "path": path_text, "value": item.get("relationship")})

    if placement.get("confidence") == "low":
        warnings.append({"code": "low_confidence_placement_requires_explicit_user_or_review_approval"})

    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "destinations": len(destination_paths),
            "context_notes": len(context_paths),
            "evidence_sources": len(source_paths),
        },
    }
    dump_json(args.report, report)
    print(report["status"])
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
