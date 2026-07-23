---
name: markdownlint-fix
description: Fix Markdown lint issues with `/usr/local/bin/markdownlint`. Use when Codex needs to clean up Markdown formatting problems in one file, several files, globbed paths, or directories; run markdownlint's auto-fix mode; and report any remaining non-auto-fixable lint findings.
---

# Markdownlint Fix

## Workflow

Use `scripts/markdownlint_fix.py` for Markdown lint cleanup instead of hand-editing routine lint violations.

Run it from the repository root when possible:

```bash
.codex/skills/markdownlint-fix/scripts/markdownlint_fix.py README.md docs
```

The script:

- Requires `/usr/local/bin/markdownlint`.
- Expands explicit files, directories, and globs into Markdown files.
- Normalizes bold-only ATX headings such as `# **Title**` into `# Title`.
- Removes all blank lines (single or multiple) between adjacent list items.
- Removes lines containing only "Code snippet" or "Snippet de código" text.
- Adds language identifiers to code fences that lack them (e.g., ` ``` ` becomes ` ```mermaid ` for diagrams).
- Runs `/usr/local/bin/markdownlint --fix` on the selected files.
- Runs `/usr/local/bin/markdownlint` again to report remaining issues that need manual edits.

## Target Selection

Pass only the files or directories the user asked to fix. Do not run the script across the whole repository unless the user asked for project-wide cleanup.

Use quoted globs so the script can expand them consistently:

```bash
.codex/skills/markdownlint-fix/scripts/markdownlint_fix.py "docs/**/*.md" "notes/*.markdown"
```

For filenames with spaces, pass each path as a normal shell argument:

```bash
.codex/skills/markdownlint-fix/scripts/markdownlint_fix.py "notes/My Note.md"
```

## Configuration

Let markdownlint discover local config files by default.

If the task requires a specific config or ignore file, pass it through the script:

```bash
.codex/skills/markdownlint-fix/scripts/markdownlint_fix.py --config .markdownlint.json --ignore-path .markdownlintignore docs
```

## Markdown Style Conventions

- Nested lists must use 4 spaces (enforced by markdownlint).
- Blank lines before nested lists are not required.
- Blank lines between adjacent list items are not allowed and will be automatically removed (including multiple consecutive blank lines).
- Blank lines after list blocks are required (not enforced by markdownlint).

## Manual Follow-Up

Treat a nonzero result after the second lint run as a to-do list, not as a script failure. Fix remaining findings manually, then rerun the script on the same targets until markdownlint exits cleanly.

Before finishing, summarize:

- The targets fixed.
- Whether markdownlint passes.
- Any remaining rules that require manual follow-up.
