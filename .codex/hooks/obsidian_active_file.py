#!/usr/bin/env python3
"""Inject Obsidian note context into UserPromptSubmit output.

The hook is intentionally narrow: it only emits note paths for model context and
note names for user-facing messages, never note content, backlinks, searches,
selections, or cursor state.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Iterable


def _safe_markdown_path(value: Any) -> Path | None:
    """Return a safe vault-relative Markdown path, or None."""
    if not isinstance(value, str) or not value:
        return None

    # Prevent a filename from turning the tiny context line into multiple lines.
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        return None

    path = Path(value)
    if path.is_absolute() or path.suffix.lower() != ".md" or ".." in path.parts:
        return None
    return path


def _leaves(value: Any) -> Iterable[dict[str, Any]]:
    """Yield Obsidian workspace leaf objects from nested workspace containers."""
    if not isinstance(value, dict):
        return

    if value.get("type") == "leaf":
        yield value

    children = value.get("children")
    if isinstance(children, list):
        for child in children:
            yield from _leaves(child)


def _workspace_from_environment() -> Path | None:
    """Resolve explicit workspace/vault overrides, if configured."""
    explicit_workspace = os.environ.get("OBSIDIAN_WORKSPACE")
    if explicit_workspace:
        return Path(explicit_workspace).expanduser()

    explicit_vault = os.environ.get("OBSIDIAN_VAULT")
    if explicit_vault:
        return Path(explicit_vault).expanduser() / ".obsidian" / "workspace.json"

    return None


def _find_workspace(cwd: Path) -> Path | None:
    """Find the nearest Obsidian workspace by walking upward from the Codex cwd."""
    overridden = _workspace_from_environment()
    if overridden is not None:
        return overridden if overridden.is_file() else None

    current = cwd.resolve()
    for directory in (current, *current.parents):
        candidate = directory / ".obsidian" / "workspace.json"
        if candidate.is_file():
            return candidate
    return None


def _vault_root(workspace_path: Path) -> Path:
    """Return the Obsidian vault root for a workspace file."""
    return workspace_path.parent.parent.resolve()


def _absolute_note(workspace_path: Path, relative_note: Path) -> Path | None:
    """Resolve a workspace note while keeping it inside the vault."""
    # <vault>/.obsidian/workspace.json -> <vault>
    vault_root = _vault_root(workspace_path)
    note = (vault_root / relative_note).resolve()

    try:
        note.relative_to(vault_root)
    except ValueError:
        return None

    # Workspace state can outlive a rename/delete; stale paths add no value.
    if not note.is_file():
        return None
    return note


def _primary_note(workspace: dict[str, Any], workspace_path: Path) -> Path | None:
    """Return the most recent valid Markdown note from lastOpenFiles."""
    last_open_files = workspace.get("lastOpenFiles")
    if not isinstance(last_open_files, list):
        return None

    for value in last_open_files:
        relative_note = _safe_markdown_path(value)
        if relative_note is None:
            continue

        note = _absolute_note(workspace_path, relative_note)
        if note is not None:
            return note

    return None


def _open_markdown_notes(workspace: dict[str, Any], workspace_path: Path) -> list[Path]:
    """Return the currently open Markdown notes from workspace leaves."""
    notes: list[Path] = []
    seen: set[Path] = set()

    for key in ("main", "left", "right", "floating"):
        for leaf in _leaves(workspace.get(key)):
            state = leaf.get("state")
            if not isinstance(state, dict) or state.get("type") != "markdown":
                continue

            state_data = state.get("state")
            if not isinstance(state_data, dict):
                continue

            relative_note = _safe_markdown_path(state_data.get("file"))
            if relative_note is None:
                continue

            note = _absolute_note(workspace_path, relative_note)
            if note is None or note in seen:
                continue

            seen.add(note)
            notes.append(note)

    return notes


def _note_label(note: Path) -> str:
    """Return the note filename with the Markdown extension."""
    return note.name


def _load_hook_input() -> dict[str, Any] | None:
    try:
        value = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return None
    return value if isinstance(value, dict) else None


def _display_path(note: Path, workspace_path: Path) -> str:
    """Return a note path relative to the vault root."""
    return note.relative_to(_vault_root(workspace_path)).as_posix()


def _emit_context(primary_note: Path, open_notes: list[Path], workspace_path: Path) -> None:
    context_lines = [f"Primary Obsidian file: {_display_path(primary_note, workspace_path)}"]

    if open_notes:
        context_lines.append("Open Markdown notes:")
        context_lines.extend(f"- {_display_path(note, workspace_path)}" for note in open_notes)

    context = "\n".join(context_lines)
    output = {
        "systemMessage": f"Current note: {_note_label(primary_note)}",
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }
    json.dump(output, sys.stdout, ensure_ascii=False, separators=(",", ":"))
    sys.stdout.write("\n")


def main() -> int:
    hook_input = _load_hook_input()
    if hook_input is None:
        return 0

    if hook_input.get("hook_event_name") != "UserPromptSubmit":
        return 0

    raw_cwd = hook_input.get("cwd")
    if not isinstance(raw_cwd, str) or not raw_cwd:
        return 0

    workspace_path = _find_workspace(Path(raw_cwd))
    if workspace_path is None:
        return 0

    try:
        workspace = json.loads(workspace_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0

    if not isinstance(workspace, dict):
        return 0

    primary_note = _primary_note(workspace, workspace_path)
    if primary_note is None:
        return 0

    _emit_context(primary_note, _open_markdown_notes(workspace, workspace_path), workspace_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
