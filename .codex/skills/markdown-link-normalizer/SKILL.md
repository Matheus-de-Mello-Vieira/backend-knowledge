---
name: markdown-link-normalizer
description: Normalize and validate local Markdown links in Obsidian vaults, notes, or documentation. Use when Codex needs to convert Obsidian Wikilinks to portable Markdown links, rewrite Markdown links to a consistent project style, URL-encode local paths and heading anchors, remove unnecessary same-folder ./ prefixes, convert slug anchors to heading-text anchors, or verify that local Markdown file and anchor targets resolve after moving or reorganizing notes.
---

# Markdown Link Normalizer

Use this skill for Obsidian vaults, repository notes, and documentation trees where local links must be consistent and verifiable.

The canonical stored link format is standard Markdown, not Obsidian Wikilinks. When a resolvable Wikilink appears in normal note body text, convert it to an equivalent Markdown link before applying the normal Markdown normalization rules.

## Workflow

1. Inspect the relevant Markdown tree before editing, including both Markdown links and Wikilinks:

```bash
rg -n '(\]\([^)]+\)|\[\[[^]]+\]\])' <vault-root>
```

2. Normalize the vault. The normalizer first converts resolvable Wikilinks, then normalizes all local Markdown destinations:

```bash
uv run python .codex/skills/markdown-link-normalizer/scripts/normalize_markdown_links.py <vault-root>
```

Use `--check` to preview files that would change without writing:

```bash
uv run python .codex/skills/markdown-link-normalizer/scripts/normalize_markdown_links.py --check <vault-root>
```

3. Validate all local file and heading targets and verify that no normal-body Wikilinks remain:

```bash
uv run python .codex/skills/markdown-link-normalizer/scripts/validate_markdown_links.py <vault-root>
```

4. Spot-check representative changed files with `git diff` or `sed`.

## Obsidian Wikilink Conversion

Obsidian supports both Wikilinks and Markdown links for internal links. Prefer Markdown links for interoperability.

Convert normal Wikilinks when their targets can be resolved unambiguously inside the supplied vault root:

```text
[[Three laws of motion]]
-> [Three laws of motion](Three%20laws%20of%20motion.md)

[[Three laws of motion|Newton's laws]]
-> [Newton's laws](Three%20laws%20of%20motion.md)

[[Three laws of motion#Second law]]
-> [Three laws of motion#Second law](Three%20laws%20of%20motion.md#Second%20law)

[[Projects/Three laws of motion]]
-> [Projects/Three laws of motion](Projects/Three%20laws%20of%20motion.md)
```

For bare note names, resolve against the vault rather than assuming the target is in the current folder. Prefer a same-folder match; otherwise convert only when the vault contains one unambiguous matching target. Emit the resulting Markdown path relative to the source note.

If a Wikilink target is missing or ambiguous, leave it unchanged and report it. Do not guess a destination.

### Obsidian-specific forms

Do not rewrite constructs that do not have a safely equivalent portable Markdown meaning:

- `![[...]]` embeds.
- Block references such as `[[Note#^block-id]]`.
- Header/block search forms such as `[[## heading]]` and `[[^^block]]`.
- Wikilinks inside YAML frontmatter/properties.
- Wikilinks inside fenced code blocks or inline code spans.

These forms may intentionally depend on Obsidian behavior. Normalization must not silently change their semantics.

## Markdown Link Style

Normalize only local inline Markdown links in normal note body text. Leave external URLs, `mailto:` links, embeds, YAML frontmatter, and code content alone.

Use this local-link style:

- Include `.md` for Markdown note file targets.
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

## Validation

After normalization, treat these as failures:

- A local Markdown destination points to a missing file.
- A Markdown heading anchor does not match a heading in its target note.
- A normal-body Wikilink remains because it was unresolved, ambiguous, or otherwise not converted.

Obsidian-specific embeds and Wikilinks deliberately preserved inside YAML or code are not part of this validation invariant.

## Scripts

- `scripts/normalize_markdown_links.py`: converts resolvable Obsidian Wikilinks to Markdown links and normalizes local inline Markdown links in place. Use `--check` to preview changes.
- `scripts/validate_markdown_links.py`: reports missing local files, missing heading anchors, and remaining normal-body Wikilinks. Use after every normalization or note move.

Both scripts accept a root path and recursively process `*.md` files. For Obsidian Wikilink resolution, pass the vault root whenever possible.

## Obsidian Setting

To prevent Obsidian from creating new Wikilinks after migration, open **Settings → Files and links** and disable **Use [[Wikilinks]]**. Obsidian will then insert Markdown links even when link autocomplete is started with `[[`.

## Python Environment

This repository uses `uv` for Python environment management. The Python version is pinned in `.python-version` and the virtual environment is created automatically via `uv sync`. Run bundled scripts with `uv run python`.
