#!/usr/bin/env python3
"""Run /usr/local/bin/markdownlint --fix on selected Markdown files."""

from __future__ import annotations

import argparse
import glob
import re
import shutil
import subprocess
import sys
from pathlib import Path


MARKDOWNLINT = "/usr/local/bin/markdownlint"
MARKDOWN_SUFFIXES = {".md", ".markdown", ".mdown", ".mkdn", ".mkd"}
ATX_BOLD_HEADING_RE = re.compile(r"^(#{1,6})\s+\*\*(.*?)\*\*(\s+#+\s*)?$")
LIST_ITEM_RE = re.compile(r"^[ \t]{0,3}(?:[-+*]|\d+[.)])[ \t]+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fix Markdown lint issues with /usr/local/bin/markdownlint."
    )
    parser.add_argument(
        "targets",
        nargs="+",
        help="Markdown files, directories, or glob patterns to fix.",
    )
    parser.add_argument(
        "--config",
        help="Optional markdownlint config file to pass with --config.",
    )
    parser.add_argument(
        "--ignore-path",
        help="Optional markdownlint ignore file to pass with --ignore-path.",
    )
    return parser.parse_args()


def is_markdown_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in MARKDOWN_SUFFIXES


def expand_target(raw_target: str) -> list[Path]:
    matches = glob.glob(raw_target, recursive=True)
    candidates = [Path(match) for match in matches] if matches else [Path(raw_target)]
    files: list[Path] = []

    for candidate in candidates:
        if candidate.is_dir():
            files.extend(
                path
                for path in candidate.rglob("*")
                if is_markdown_file(path) and ".git" not in path.parts
            )
        elif is_markdown_file(candidate):
            files.append(candidate)
        elif not candidate.exists():
            raise FileNotFoundError(f"Target not found: {raw_target}")
        else:
            raise ValueError(f"Target is not a Markdown file or directory: {candidate}")

    return files


def unique_sorted(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    output: list[Path] = []

    for path in sorted(paths, key=lambda item: str(item)):
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            output.append(path)

    return output


def build_markdownlint_command(args: argparse.Namespace, fix: bool, files: list[Path]) -> list[str]:
    command = [MARKDOWNLINT]
    if args.config:
        command.extend(["--config", args.config])
    if args.ignore_path:
        command.extend(["--ignore-path", args.ignore_path])
    if fix:
        command.extend(["--fix", "--quiet"])
    command.extend(str(path) for path in files)
    return command


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, check=False)


def normalize_heading(line: str) -> str:
    match = ATX_BOLD_HEADING_RE.match(line)
    if not match:
        return line

    heading_text = match.group(2).strip()
    if not heading_text:
        return line

    closing = match.group(3) or ""
    return f"{match.group(1)} {heading_text}{closing}"


def normalize_content(content: str) -> str:
    newline = "\r\n" if "\r\n" in content else "\n"
    has_trailing_newline = content.endswith(("\n", "\r"))
    lines = content.splitlines()
    normalized: list[str] = []

    for index, line in enumerate(lines):
        stripped = line.strip()
        if (
            stripped == ""
            and normalized
            and index + 1 < len(lines)
            and LIST_ITEM_RE.match(normalized[-1])
            and LIST_ITEM_RE.match(lines[index + 1])
        ):
            continue
        normalized.append(normalize_heading(line))

    result = newline.join(normalized)
    if has_trailing_newline:
        result += newline
    return result


def normalize_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    normalized = normalize_content(original)
    if normalized == original:
        return False

    path.write_text(normalized, encoding="utf-8")
    return True


def main() -> int:
    args = parse_args()

    if not shutil.which(MARKDOWNLINT):
        print(f"error: required executable not found: {MARKDOWNLINT}", file=sys.stderr)
        return 127

    files: list[Path] = []
    try:
        for target in args.targets:
            files.extend(expand_target(target))
    except (FileNotFoundError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    files = unique_sorted(files)
    if not files:
        print("No Markdown files matched the provided targets.")
        return 0

    normalized_count = 0
    for path in files:
        if normalize_file(path):
            normalized_count += 1

    if normalized_count:
        print(
            f"Applied custom Markdown normalization to {normalized_count} file(s).",
            flush=True,
        )

    print(f"Running markdownlint --fix on {len(files)} file(s).", flush=True)
    fix_result = run(build_markdownlint_command(args, fix=True, files=files))

    print("Verifying remaining markdownlint findings.", flush=True)
    verify_result = run(build_markdownlint_command(args, fix=False, files=files))

    if verify_result.returncode == 0:
        print("markdownlint passes.")
        return 0

    if fix_result.returncode != 0:
        print(
            "markdownlint --fix completed with remaining findings; review the verification output above.",
            file=sys.stderr,
        )
    return verify_result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
