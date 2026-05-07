---
name: markdown-link-normalizer
description: Normalize and validate local Markdown links in notes or documentation. Use when Codex needs to rewrite Markdown links to a consistent project style, URL-encode local paths and heading anchors, remove unnecessary same-folder ./ prefixes, convert slug anchors to heading-text anchors, or verify that local Markdown file and anchor targets resolve after moving or reorganizing notes.
---

# Markdown Link Normalizer

Use this skill for repository notes, Obsidian vaults, and documentation trees where local Markdown links must be consistent and verifiable.

## Workflow

1. Inspect the relevant Markdown tree before editing:

```bash
rg -n "\]\([^)]+\)" <docs-root>
```

2. Normalize local inline links with the bundled script:

```bash
pyenv exec python .codex/skills/markdown-link-normalizer/scripts/normalize_markdown_links.py <docs-root>
```

3. Validate all local file and heading targets:

```bash
pyenv exec python .codex/skills/markdown-link-normalizer/scripts/validate_markdown_links.py <docs-root>
```

4. Spot-check representative changed files with `git diff` or `sed`.

## Link Style

Normalize only local inline Markdown links. Leave external URLs, `mailto:` links, and non-Markdown content alone.

Use this local-link style:

- Encode spaces in local paths as `%20`.
- Omit unnecessary `./` for same-folder targets.
- Preserve `../` when linking to parent folders.
- Use heading-text anchors with URL encoding, such as `#The%20tenets` or `#JSON%20Web%20Tokens%20%28JWT%29`.
- Prefer exact heading text for anchors over lowercase slug anchors.

Examples:

```text
[The tenets] -> 01%20Security%20Principles.md#The%20tenets
[Cryptography] -> ../03%20Cryptography%20and%20Data%20Protection/01%20Cryptography.md
[HMAC] -> ../03%20Cryptography%20and%20Data%20Protection/01%20Cryptography.md#Keyed-Hashing:%20HMAC
```

## Scripts

- `scripts/normalize_markdown_links.py`: rewrites local inline Markdown links in place. Use `--check` to preview files that would change without writing.
- `scripts/validate_markdown_links.py`: reports missing local files and heading anchors. Use after every normalization or note move.

Both scripts accept a root path and recursively process `*.md` files.

## Python Environment

This repository is expected to use the local `pyenv` version defined by `.python-version`. Keep the repo configured to a tooling environment that includes `PyYAML`, then run the bundled scripts with `pyenv exec python`.
