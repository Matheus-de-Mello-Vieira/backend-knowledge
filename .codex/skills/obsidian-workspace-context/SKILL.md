---
name: obsidian-workspace-context
description: Extract the active, open, recently used, and link-pane-related Markdown notes from an Obsidian `.obsidian/workspace.json` file while discarding layout and UI presentation details. Use when assisting with study or writing work in an Obsidian vault and current workspace context can identify the note being edited or its nearby research context.
---

# Obsidian Workspace Context

Run the bundled script before editing, extending, reorganizing, or answering questions about notes when the user's current Obsidian workspace is relevant.

```bash
python3 .codex/skills/obsidian-workspace-context/scripts/workspace_context.py
```

Pass an explicit workspace file when working outside the current vault root:

```bash
python3 .codex/skills/obsidian-workspace-context/scripts/workspace_context.py /path/to/vault/.obsidian/workspace.json
```

Use the JSON output as situational context, not as a source of note content. Read the active note first; use open and recent notes only to find related material or preserve the user's study flow.

The output intentionally retains only:

- `active_note`: the Markdown note in Obsidian's active leaf, if any.
- `open_notes`: Markdown notes open in workspace leaves.
- `recent_notes`: recently opened Markdown notes, limited to 10 by default.
- `related_note_targets`: notes selected in backlink and outgoing-link panes.
- `search_queries`: non-empty Obsidian searches, which can indicate active research intent.

Do not infer that every returned note must be modified. Ignore missing files gracefully; workspace state can outlive renames and deletions.

Use `--recent-limit 0` to omit recent history or increase the limit only when broader recent context is needed.
