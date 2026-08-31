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
CODE_SNIPPET_RE = re.compile(
    r"^\s*(?:Code snippet|Snippet de código)\s*$",
    re.IGNORECASE,
)
CODE_FENCE_RE = re.compile(r"^```\s*$")
INLINE_CODE_ONLY_RE = re.compile(r"^`[^`\n]+`$")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s")
BLOCKQUOTE_RE = re.compile(r"^\s{0,3}>")
TABLE_ROW_RE = re.compile(r"^\s*\|")
BLOCKQUOTE_LINE_RE = re.compile(r"^(\s{0,3}>\s?)(.*)$")
CONTINUATION_RE = re.compile(
    r"^(?:in that case,|for example,|for instance,|if\b|then\b|so\b|thus\b|therefore\b|as a result,)",
    re.IGNORECASE,
)
LOWERCASE_START_RE = re.compile(r"^[a-z]")


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


def detect_code_language(next_lines: list[str]) -> str:
    """Detect code block language based on content heuristics."""
    # Join a few lines to analyze
    sample = "\n".join(next_lines[:10]).lower()

    # Check for mermaid diagram keywords
    if any(keyword in sample for keyword in ["flowchart", "graph", "sequencediagram", "classDiagram", "stateDiagram", "erDiagram"]):
        return "mermaid"

    # Check for common programming language patterns
    if any(keyword in sample for keyword in ["def ", "import ", "from ", "class ", "if __name__"]):
        return "python"
    elif any(keyword in sample for keyword in ["function ", "const ", "let ", "var ", "=>", "console.log"]):
        return "javascript"
    elif any(keyword in sample for keyword in ["public class", "private ", "protected ", "void ", "static "]):
        return "java"
    elif any(keyword in sample for keyword in ["package ", "func ", "import (", ":="]):
        return "go"
    elif "```" in sample or "{" in sample or "[" in sample:
        # Generic code-like content
        return "text"

    return "text"


def find_next_non_blank_line(lines: list[str], start_index: int) -> str | None:
    """Find the next non-blank line after the given index."""
    for i in range(start_index + 1, len(lines)):
        if lines[i].strip():
            return lines[i]
    return None


def split_blockquote_prefix(line: str) -> tuple[str, str]:
    match = BLOCKQUOTE_LINE_RE.match(line)
    if not match:
        return "", line
    return match.group(1), match.group(2)


def is_blank_separator(line: str) -> bool:
    prefix, body = split_blockquote_prefix(line)
    if prefix:
        return body.strip() == ""
    return line.strip() == ""


def inline_code_body(line: str) -> str | None:
    _, body = split_blockquote_prefix(line)
    stripped = body.strip()
    if INLINE_CODE_ONLY_RE.match(stripped):
        return stripped
    return None


def prose_prefix(line: str) -> str | None:
    prefix, body = split_blockquote_prefix(line)
    stripped = body.strip() if prefix else line.strip()
    if not stripped:
        return None
    if stripped.startswith("```"):
        return None
    if HEADING_RE.match(stripped):
        return None
    if LIST_ITEM_RE.match(stripped):
        return None
    if TABLE_ROW_RE.match(stripped):
        return None
    return prefix


def prose_body(line: str) -> str:
    prefix, body = split_blockquote_prefix(line)
    return body if prefix else line


def ensure_terminal_punctuation(text: str, punctuation: str = ".") -> str:
    stripped = text.rstrip()
    if not stripped:
        return text
    if stripped.endswith((".", ":", ";", "!", "?")):
        return stripped
    return f"{stripped}{punctuation}"


def natural_join(parts: list[str], conjunction: str = "and") -> str:
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]} {conjunction} {parts[1]}"
    return f"{', '.join(parts[:-1])}, {conjunction} {parts[-1]}"


def next_prose_line(
    lines: list[str], start_index: int, required_prefix: str
) -> tuple[int | None, str | None]:
    for i in range(start_index, len(lines)):
        if is_blank_separator(lines[i]):
            continue
        if prose_prefix(lines[i]) == required_prefix:
            return i, prose_body(lines[i]).strip()
        break
    return None, None


def merge_stray_inline_code_lines(lines: list[str]) -> list[str]:
    """Fold isolated inline-code-only lines back into nearby prose."""
    merged: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]

        if is_blank_separator(line) and merged and index + 2 < len(lines):
            previous = merged[-1]
            previous_prefix = prose_prefix(previous)
            if previous_prefix is not None:
                scan = index
                code_lines: list[str] = []
                code_prefix = ""

                while (
                    scan + 2 < len(lines)
                    and is_blank_separator(lines[scan])
                    and inline_code_body(lines[scan + 1])
                    and is_blank_separator(lines[scan + 2])
                ):
                    current_prefix, _ = split_blockquote_prefix(lines[scan + 1])
                    if code_lines and current_prefix != code_prefix:
                        break
                    if current_prefix != previous_prefix:
                        break
                    code_prefix = current_prefix
                    code_lines.append(inline_code_body(lines[scan + 1]) or "")
                    scan += 2

                if code_lines:
                    previous_text = prose_body(previous).rstrip()
                    previous_trimmed = previous_text.rstrip()
                    merged_text = previous_trimmed

                    if previous_trimmed.endswith("with:"):
                        merged_text = (
                            f"{previous_trimmed[:-1].rstrip()} "
                            f"{natural_join(code_lines)}"
                        )
                    elif previous_trimmed.endswith(":"):
                        merged_text = (
                            f"{previous_trimmed[:-1].rstrip()}: "
                            f"{natural_join(code_lines, conjunction='and')}"
                        )
                    else:
                        merged_text = f"{previous_trimmed} {natural_join(code_lines)}"

                    next_index, next_text = next_prose_line(lines, scan + 1, previous_prefix)
                    consumed_next_prose = False
                    if next_text:
                        if previous_trimmed.endswith("with:") and LOWERCASE_START_RE.match(
                            next_text
                        ):
                            merged_text = f"{merged_text}, {next_text}"
                            scan = next_index or scan
                            consumed_next_prose = True
                        elif CONTINUATION_RE.match(next_text):
                            merged_text = f"{merged_text}. {next_text}"
                            scan = next_index or scan
                            consumed_next_prose = True
                        elif previous_trimmed.endswith("with:"):
                            merged_text = ensure_terminal_punctuation(
                                merged_text, punctuation=":"
                            )
                        else:
                            merged_text = ensure_terminal_punctuation(merged_text)
                    else:
                        merged_text = ensure_terminal_punctuation(merged_text)

                    if previous_prefix:
                        merged[-1] = f"{previous_prefix}{merged_text}"
                    else:
                        merged[-1] = merged_text
                    if next_text and not consumed_next_prose:
                        merged.append("")
                    index = scan + 1
                    continue

        merged.append(line)
        index += 1

    return merged


def normalize_content(content: str) -> str:
    newline = "\r\n" if "\r\n" in content else "\n"
    has_trailing_newline = content.endswith(("\n", "\r"))
    lines = merge_stray_inline_code_lines(content.splitlines())
    normalized: list[str] = []
    in_code_block = False

    for index, line in enumerate(lines):
        stripped = line.strip()

        # Skip lines that are just "Code snippet"
        if CODE_SNIPPET_RE.match(line):
            continue

        # Toggle code block state
        if line.strip().startswith("```"):
            in_code_block = not in_code_block

            # Check if this is an opening fence without language
            if CODE_FENCE_RE.match(line) and not in_code_block:
                # This is a closing fence, just add it
                normalized.append(line)
                continue
            elif CODE_FENCE_RE.match(line) and in_code_block:
                # This is an opening fence without language, try to detect it
                remaining_lines = lines[index + 1:]
                language = detect_code_language(remaining_lines)
                normalized.append(f"```{language}")
                continue

        # Remove blank lines between list items (handles multiple consecutive blank lines)
        if stripped == "" and normalized and LIST_ITEM_RE.match(normalized[-1]):
            # Look ahead to find the next non-blank line
            next_non_blank = find_next_non_blank_line(lines, index)
            if next_non_blank and LIST_ITEM_RE.match(next_non_blank):
                # Skip this blank line if the next non-blank line is also a list item
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
