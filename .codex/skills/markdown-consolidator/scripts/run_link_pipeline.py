#!/usr/bin/env python3
"""Run the companion markdown-link-normalizer against a disposable repository shadow."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from common import SCHEMA_VERSION, dump_json, load_json

ISSUE_RE = re.compile(r"^(.*?):(\d+) -> (.+)$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize changed note links and validate the final repository shadow.")
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--publication-manifest", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--normalizer-skill-dir", type=Path, required=True)
    parser.add_argument("--shadow-root", type=Path, required=True)
    parser.add_argument("--normalized-root", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def copy_markdown_tree(source: Path, destination: Path, excluded: list[Path]) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for path in source.rglob("*.md"):
        resolved = path.resolve()
        if any(_is_under(resolved, item) for item in excluded):
            continue
        relative = path.relative_to(source)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def _is_under(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def run(script: Path, target: Path, python_prefix: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [*python_prefix, str(script), str(target)],
        text=True,
        capture_output=True,
        check=False,
    )


def parse_issues(stdout: str, root: Path) -> set[tuple[str, int, str]]:
    result: set[tuple[str, int, str]] = set()
    for line in stdout.splitlines():
        match = ISSUE_RE.match(line.strip())
        if not match:
            continue
        source = Path(match.group(1))
        try:
            relative = source.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            relative = source.as_posix()
        result.add((relative, int(match.group(2)), match.group(3)))
    return result


def main() -> int:
    args = parse_args()
    repository = args.repository_root.resolve()
    work_dir = args.work_dir.resolve()
    inventory = load_json(args.inventory)
    manifest = load_json(args.publication_manifest)
    normalize_script = args.normalizer_skill_dir / "scripts" / "normalize_markdown_links.py"
    validate_script = args.normalizer_skill_dir / "scripts" / "validate_markdown_links.py"
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    if shutil.which("uv") and (repository / ".venv").exists():
        python_prefix = ["uv", "run", "python"]
    else:
        python_prefix = [sys.executable]
        if shutil.which("uv"):
            warnings.append({"code": "uv_venv_missing_used_current_python"})

    if not normalize_script.is_file() or not validate_script.is_file():
        errors.append({"code": "normalizer_companion_scripts_missing", "skill_dir": str(args.normalizer_skill_dir)})
        report = {"schema_version": SCHEMA_VERSION, "status": "failed", "errors": errors, "warnings": warnings, "metrics": {}}
        dump_json(args.report, report)
        print("failed")
        return 2

    excluded = [work_dir, repository / ".git", repository / ".agents", repository / ".codex", repository / "node_modules"]
    copy_markdown_tree(repository, args.shadow_root, excluded)
    baseline = run(validate_script, args.shadow_root, python_prefix)
    baseline_issues = parse_issues(baseline.stdout, args.shadow_root)

    # Model the repository after temporary evidence files are deleted.
    inventory_root = Path(str(inventory.get("root", repository))).resolve()
    for source in inventory.get("sources", []):
        if not isinstance(source, dict) or not source.get("absolute_path"):
            continue
        absolute = Path(str(source["absolute_path"])).resolve()
        try:
            relative = absolute.relative_to(repository)
        except ValueError:
            # Source outside the repository does not affect the final note tree.
            continue
        target = args.shadow_root / relative
        if target.exists():
            target.unlink()

    publications = [item for item in manifest.get("publications", []) if isinstance(item, dict)]
    for item in publications:
        relative = Path(str(item.get("path", "")))
        candidate = args.candidate_root / relative
        shadow = args.shadow_root / relative
        if not candidate.is_file():
            errors.append({"code": "candidate_missing", "path": relative.as_posix()})
            continue
        shadow.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(candidate, shadow)

    normalization_runs: list[dict[str, Any]] = []
    for item in publications:
        relative = Path(str(item.get("path", "")))
        shadow = args.shadow_root / relative
        if not shadow.is_file():
            continue
        process = run(normalize_script, shadow, python_prefix)
        normalization_runs.append({
            "path": relative.as_posix(),
            "returncode": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
        })
        if process.returncode != 0:
            errors.append({"code": "link_normalization_failed", "path": relative.as_posix(), "stderr": process.stderr.strip()})

    final = run(validate_script, args.shadow_root, python_prefix)
    final_issues = parse_issues(final.stdout, args.shadow_root)
    baseline_keys = {(source, destination) for source, _, destination in baseline_issues}
    publication_paths = {str(item.get("path", "")) for item in publications}
    new_issues = sorted(
        issue for issue in final_issues
        if (issue[0], issue[2]) not in baseline_keys or issue[0] in publication_paths
    )
    inherited_issues = sorted(issue for issue in final_issues if issue not in new_issues)
    if new_issues:
        errors.append({
            "code": "new_or_deletion_exposed_link_failures",
            "items": [{"source": source, "line": line, "destination": destination} for source, line, destination in new_issues],
        })
    if inherited_issues:
        warnings.append({
            "code": "preexisting_link_failures",
            "items": [{"source": source, "line": line, "destination": destination} for source, line, destination in inherited_issues],
        })

    if args.normalized_root.exists():
        shutil.rmtree(args.normalized_root)
    args.normalized_root.mkdir(parents=True, exist_ok=True)
    for item in publications:
        relative = Path(str(item.get("path", "")))
        shadow = args.shadow_root / relative
        if shadow.is_file():
            target = args.normalized_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(shadow, target)

    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if not errors else "failed",
        "companion_skill_dir": str(args.normalizer_skill_dir.resolve()),
        "python_command": python_prefix,
        "errors": errors,
        "warnings": warnings,
        "normalization_runs": normalization_runs,
        "baseline_validation": {"returncode": baseline.returncode, "stdout": baseline.stdout, "stderr": baseline.stderr},
        "final_validation": {"returncode": final.returncode, "stdout": final.stdout, "stderr": final.stderr},
        "metrics": {
            "publication_files": len(publications),
            "baseline_link_failures": len(baseline_issues),
            "final_link_failures": len(final_issues),
            "new_link_failures": len(new_issues),
            "preexisting_link_failures": len(inherited_issues),
        },
    }
    dump_json(args.report, report)
    print(report["status"])
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
