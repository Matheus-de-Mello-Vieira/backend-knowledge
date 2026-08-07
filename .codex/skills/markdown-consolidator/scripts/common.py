#!/usr/bin/env python3
"""Shared helpers for the markdown-consolidator skill."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "5.0"
SCOPE_KEYS = (
    "source_ids",
    "topic_ids",
    "comparison_ids",
    "decision_ids",
    "unit_ids",
    "validation_categories",
    "reviewed_attempt_ids",
    "review_categories",
    "destination_paths",
    "context_paths",
    "publication_paths",
)


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return data


def dump_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def canonical_json_bytes(data: Any) -> bytes:
    return json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def task_spec_sha256(path: Path) -> str:
    # Hash the parsed JSON so indentation and key order do not matter.
    return sha256_bytes(canonical_json_bytes(load_json(path)))


def json_files(directory: Path, *, exclude_names: Iterable[str] = ()) -> list[Path]:
    excluded = set(exclude_names)
    if not directory.exists():
        return []
    return sorted(
        path
        for path in directory.glob("*.json")
        if path.name not in excluded and path.is_file()
    )


def normalize_scope(scope: Any) -> dict[str, list[str]]:
    raw = scope if isinstance(scope, dict) else {}
    result: dict[str, list[str]] = {}
    for key in SCOPE_KEYS:
        values = raw.get(key, [])
        if not isinstance(values, list):
            values = []
        result[key] = sorted({str(value) for value in values})
    return result


def resolve_under(base: Path, path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else base / path


def is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except (OSError, ValueError):
        return False


def unit_records(units_dir: Path) -> tuple[dict[str, dict[str, Any]], list[Path]]:
    units: dict[str, dict[str, Any]] = {}
    files = json_files(units_dir, exclude_names={"index.json", "validation-report.json"})
    for path in files:
        data = load_json(path)
        for raw in data.get("units", []):
            if not isinstance(raw, dict) or not raw.get("unit_id"):
                continue
            unit_id = str(raw["unit_id"])
            if unit_id in units:
                raise ValueError(f"Duplicate unit_id {unit_id!r} in {path}")
            units[unit_id] = raw
    return units, files


def comparison_records(comparisons_dir: Path) -> tuple[dict[str, dict[str, Any]], list[Path]]:
    records: dict[str, dict[str, Any]] = {}
    files = json_files(comparisons_dir, exclude_names={"index.json", "validation-report.json"})
    for path in files:
        data = load_json(path)
        for raw in data.get("records", []):
            if not isinstance(raw, dict) or not raw.get("comparison_id"):
                continue
            comparison_id = str(raw["comparison_id"])
            if comparison_id in records:
                raise ValueError(f"Duplicate comparison_id {comparison_id!r} in {path}")
            records[comparison_id] = raw
    return records, files
