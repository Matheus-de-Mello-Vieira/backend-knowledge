---
name: markdown-section-style-aligner
description: Align the formatting of one Markdown section to match the surrounding sections in the same note without changing the section's meaning. Use when Codex needs to normalize heading-adjacent spacing, convert standalone bold labels into the note's local bullet pattern, nest related sub-points consistently, remove stray editorial text, or make one section visually consistent with nearby sections in notes or documentation.
---

# Markdown Section Style Aligner

Use this skill when the user points to one section and wants it formatted "like the others" in the same Markdown file.

## Workflow

1. Inspect the target section and at least one adjacent section above and below it.
2. Infer the local formatting pattern from the surrounding sections instead of applying a global Markdown style.
3. Edit only the target section unless a boundary issue requires touching the immediately adjacent separator line.
4. Preserve meaning, ordering, and emphasis unless the user asked for content changes.
5. Read the edited section again to confirm it now matches the local pattern.

## What to Normalize

- Match whether the note uses short framing bullets such as `- **What it does:** ...` and `- **Why it matters:** ...`.
- Convert standalone bold labels followed by paragraphs into bullet-led entries when nearby sections use that pattern.
- Nest related child points under the parent bullet when the surrounding note uses sub-bullets for examples or breakdowns.
- Normalize blank lines around headings, paragraphs, and list blocks to match nearby sections.
- Remove stray editorial setup text that comments on the writing process rather than the subject matter.
- Keep heading levels unchanged unless the surrounding structure proves the target heading is wrong.

## Guardrails

- Do not rewrite the section for style preferences imported from another file or repository.
- Do not compress or expand content just to force symmetry if the surrounding sections do not require it.
- Do not change terminology, links, or technical claims unless the requested formatting fix depends on it.
- Do not reformat the whole file when the user asked for one section.

## Useful Checks

- Compare the target section against the nearest section with the same role in the note.
- Watch for accidental top-level bullets that should be nested under the point immediately above them.
- Watch for missing blank lines before the next heading after converting paragraphs into lists.
- If the note mixes styles intentionally, follow the closest comparable section rather than the majority style across the file.

## Completion

Before finishing, confirm:

- The target section now follows the same bullet, spacing, and subheading conventions as its neighbors.
- The section's meaning did not change.
- No unrelated sections were reformatted.
