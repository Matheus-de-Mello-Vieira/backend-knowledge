from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).parents[1] / "hooks" / "obsidian_active_file.py"
SPEC = importlib.util.spec_from_file_location("obsidian_active_file", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class HookTests(unittest.TestCase):
    def _vault(
        self,
        active_file: str = "Notes/Test.md",
        secondary_file: str = "Notes/Second.md",
        last_open_files: list[str] | None = None,
    ):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / ".obsidian").mkdir()
        note = root / active_file
        secondary_note = root / secondary_file
        note.parent.mkdir(parents=True, exist_ok=True)
        secondary_note.parent.mkdir(parents=True, exist_ok=True)
        note.write_text("hello\n", encoding="utf-8")
        secondary_note.write_text("world\n", encoding="utf-8")
        workspace = {
            "active": "leaf-1",
            "lastOpenFiles": last_open_files or [active_file, secondary_file],
            "main": {
                "type": "split",
                "children": [
                    {
                        "type": "leaf",
                        "id": "leaf-1",
                        "state": {
                            "type": "markdown",
                            "state": {"file": active_file},
                        },
                    },
                    {
                        "type": "leaf",
                        "id": "leaf-2",
                        "state": {
                            "type": "markdown",
                            "state": {"file": secondary_file},
                        },
                    },
                ],
            },
        }
        (root / ".obsidian" / "workspace.json").write_text(
            json.dumps(workspace), encoding="utf-8"
        )
        return temp, root, note.resolve(), secondary_note.resolve()

    def test_emits_primary_recent_note_and_open_markdown_notes(self):
        temp, root, note, secondary_note = self._vault()
        self.addCleanup(temp.cleanup)
        payload = json.dumps(
            {"hook_event_name": "UserPromptSubmit", "cwd": str(root)}
        )
        stdout = io.StringIO()
        with patch.object(sys, "stdin", io.StringIO(payload)), redirect_stdout(stdout):
            self.assertEqual(MODULE.main(), 0)
        output = json.loads(stdout.getvalue())
        self.assertEqual(
            output["hookSpecificOutput"]["additionalContext"],
            "\n".join(
                [
                    "Primary Obsidian file: Notes/Test.md",
                    "Open Markdown notes:",
                    "- Notes/Test.md",
                    "- Notes/Second.md",
                ]
            ),
        )
        self.assertEqual(output["systemMessage"], "Current note: Test.md")

    def test_finds_vault_from_nested_cwd(self):
        temp, root, _, _ = self._vault()
        self.addCleanup(temp.cleanup)
        nested = root / "a" / "b"
        nested.mkdir(parents=True)
        workspace = MODULE._find_workspace(nested)
        self.assertIsNotNone(workspace)
        self.assertEqual(
            workspace.resolve(), (root / ".obsidian" / "workspace.json").resolve()
        )

    def test_non_markdown_active_leaf_still_uses_last_open_files(self):
        temp, root, note, secondary_note = self._vault()
        self.addCleanup(temp.cleanup)
        path = root / ".obsidian" / "workspace.json"
        workspace = json.loads(path.read_text(encoding="utf-8"))
        workspace["main"]["children"][0]["state"]["type"] = "search"
        path.write_text(json.dumps(workspace), encoding="utf-8")
        payload = json.dumps(
            {"hook_event_name": "UserPromptSubmit", "cwd": str(root)}
        )
        stdout = io.StringIO()
        with patch.object(sys, "stdin", io.StringIO(payload)), redirect_stdout(stdout):
            self.assertEqual(MODULE.main(), 0)
        output = json.loads(stdout.getvalue())
        self.assertEqual(
            output["hookSpecificOutput"]["additionalContext"],
            "\n".join(
                [
                    "Primary Obsidian file: Notes/Test.md",
                    "Open Markdown notes:",
                    "- Notes/Second.md",
                ]
            ),
        )
        self.assertEqual(output["systemMessage"], "Current note: Test.md")

    def test_rejects_parent_traversal(self):
        self.assertIsNone(MODULE._safe_markdown_path("../secret.md"))

    def test_explicit_vault_override(self):
        temp, root, _, _ = self._vault()
        self.addCleanup(temp.cleanup)
        elsewhere = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(elsewhere))
        with patch.dict(os.environ, {"OBSIDIAN_VAULT": str(root)}, clear=False):
            workspace = MODULE._find_workspace(elsewhere)
            self.assertIsNotNone(workspace)
            self.assertEqual(
                workspace.resolve(),
                (root / ".obsidian" / "workspace.json").resolve(),
            )

    def test_skips_non_markdown_last_open_files(self):
        temp, root, note, _ = self._vault(
            last_open_files=["image.png", "Notes/Test.md", "Notes/Second.md"]
        )
        self.addCleanup(temp.cleanup)
        payload = json.dumps(
            {"hook_event_name": "UserPromptSubmit", "cwd": str(root)}
        )
        stdout = io.StringIO()
        with patch.object(sys, "stdin", io.StringIO(payload)), redirect_stdout(stdout):
            self.assertEqual(MODULE.main(), 0)
        output = json.loads(stdout.getvalue())
        self.assertTrue(
            output["hookSpecificOutput"]["additionalContext"].startswith(
                "Primary Obsidian file: Notes/Test.md"
            )
        )
        self.assertEqual(output["systemMessage"], "Current note: Test.md")


if __name__ == "__main__":
    unittest.main()
