---
name: note-link-enrichment
description: Enrich existing note prose with semantically useful internal links while preserving wording. Use when the user asks to find or add cross-link opportunities rather than rewrite the note.
---

# Note Link Enrichment

This workflow owns **link-enrichment orchestration**, not semantic selection or prose mutation.

## Workflow

1. Invoke `$note-link-planner` on the requested note or section. It exclusively decides which existing phrase should link to which repository destination.
2. Pass the approved link plan to `$note-writer` for application to the existing phrases without changing their visible wording except where Markdown syntax requires it. The writer must not add or substitute semantic destinations.
3. Invoke `$markdown-link-normalizer` to normalize relative paths, URL-encoded spaces, and anchors and to validate targets.
4. Reread the affected sentences to ensure the links remain semantically natural.

## Constraints

- Do not select semantic link targets independently of `$note-link-planner`.
- Do not rewrite prose merely to manufacture link text.
- Do not add generic “Related” or “See also” sections unless the user explicitly asks.
- Do not move content; if a link is compensating for misplaced material, report `requires_note_refactor` instead.
- Keep the first useful link to a concept and avoid repeated markup.
