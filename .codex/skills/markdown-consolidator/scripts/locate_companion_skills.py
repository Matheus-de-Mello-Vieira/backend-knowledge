#!/usr/bin/env python3
"""Locate required companion Codex skills without copying their logic."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from common import SCHEMA_VERSION, dump_json

REQUIRED = {
    "note-home-finder": ["SKILL.md"],
    "markdown-link-normalizer": [
        "SKILL.md",
        "scripts/normalize_markdown_links.py",
        "scripts/validate_markdown_links.py",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Locate companion Codex skills.")
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--note-home-finder", type=Path)
    parser.add_argument("--link-normalizer", type=Path)
    return parser.parse_args()


def candidates(root: Path, name: str, override: Path | None) -> list[Path]:
    result: list[Path] = []
    if override:
        result.append(override)
    home = Path.home()
    for base in (root, home):
        result.extend([
            base / ".agents" / "skills" / name,
            base / ".codex" / "skills" / name,
        ])
    # Preserve order while removing duplicates.
    seen: set[Path] = set()
    unique: list[Path] = []
    for value in result:
        resolved = value.expanduser().resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    return unique


def find_skill(root: Path, name: str, override: Path | None) -> tuple[Path | None, list[str]]:
    missing_details: list[str] = []
    for path in candidates(root, name, override):
        missing = [rel for rel in REQUIRED[name] if not (path / rel).is_file()]
        if not missing:
            return path, []
        if path.exists():
            missing_details.append(f"{path}: missing {', '.join(missing)}")
    return None, missing_details


def main() -> int:
    args = parse_args()
    root = args.repository_root.resolve()
    errors: list[dict[str, Any]] = []
    skills: dict[str, dict[str, Any]] = {}
    overrides = {
        "note-home-finder": args.note_home_finder,
        "markdown-link-normalizer": args.link_normalizer,
    }
    for name in REQUIRED:
        path, details = find_skill(root, name, overrides[name])
        if path is None:
            errors.append({"code": "companion_skill_not_found", "skill": name, "details": details})
        else:
            skills[name] = {
                "skill_dir": str(path),
                "skill_file": str(path / "SKILL.md"),
            }
            if name == "markdown-link-normalizer":
                skills[name]["normalize_script"] = str(path / "scripts/normalize_markdown_links.py")
                skills[name]["validate_script"] = str(path / "scripts/validate_markdown_links.py")
    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if not errors else "failed",
        "repository_root": str(root),
        "skills": skills,
        "errors": errors,
    }
    dump_json(args.output, report)
    print(report["status"])
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
