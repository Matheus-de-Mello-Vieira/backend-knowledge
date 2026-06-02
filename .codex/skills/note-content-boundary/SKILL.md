---
name: note-content-boundary
description: Refactor overlapping Markdown note content without leaving duplication behind. Use when Codex needs to move a concept or section from one note to another, keep only a short pointer or callout in the source note, rename or remove obsolete headings, and update local links or anchors after the content boundary changes.
---

# Note Content Boundary

Use this skill when two notes currently share content but should not keep the same explanation in both places.

## Workflow

1. Identify the boundary before editing:

- Read the source and destination notes.
- Determine whether the overlapping content is:
  - the same concept in the same sense;
  - the same word in a different sense;
  - a short mention that should remain;
  - or a full explanation that belongs in only one place.
- Keep the more canonical or process-specific explanation in the stronger home.

2. Choose the right outcome:

- **Move** the substantive content when one note only needs a pointer.
- **Leave both** when the term is shared but the operational meaning is different.
- **Merge** when two sections are saying the same thing at the same level of abstraction.
- **Split** when one note is mixing core subject matter with adjacent background that belongs elsewhere.

3. Move the content cleanly:

- Copy the full explanation into the destination note and adapt it to the destination's framing.
- Remove the duplicated body from the source note.
- Keep only a short residual pointer in the source note when readers may still look there first.
- Prefer a callout when the leftover text is guidance or redirection rather than core content.

4. Clean up the source note structure:

- Remove headings that no longer introduce real content.
- If a heading remains useful for scanning, keep it and shorten the body beneath it.
- If the residual text is only a pointer, consider deleting the heading entirely and leaving only the callout.

5. Repair links and anchors:

- Update links that should now point to the new canonical section.
- If headings changed, check whether any local anchors need to move with them.
- When link cleanup is broader than a couple of manual edits, use `$markdown-link-normalizer` at `.codex/skills/markdown-link-normalizer`.

6. Verify the result:

- Read the edited block in both notes.
- Confirm the source note still reads naturally without the removed section.
- Confirm the destination note now owns the topic at the right level of detail.
- Confirm there is no accidental semantic drift during the move.

## Residual Content Rules

- Leave behind only enough text to explain why the topic is not fully covered there.
- Avoid phrases like "this note" or "that note" when neutral wording reads better.
- Use callouts for scoped asides, redirects, or "see also" guidance.
- Do not leave a heading whose only content is a redundant sentence.
- Prefer linking directly to the destination section, not just the file, when the target section is stable.

See [Residue Patterns](references/residue-patterns.md) for compact examples.

## Heuristics

- Keep **LLM runtime mechanics** with LLM processing notes, not context-management notes.
- Keep **context budgeting, memory, and prompt assembly** with context-engineering notes, not model internals notes.
- Keep **lexical IR tokenization** separate from **LLM tokenization** when the underlying processing role is different.
- Prefer one canonical explanation per concept per sense.
- If a duplicated section exists only because readers may search both notes, replace one copy with a pointer instead of preserving both bodies.

## Link Handling

- Use repository-local Markdown paths.
- Preserve existing naming conventions in the target folder.
- Prefer exact heading-text anchors with URL encoding when linking to a specific section.
- After renaming or deleting headings, search for inbound links before finishing.

## Constraints

- Do not create a new note unless the user asks for one or the existing note boundary is clearly insufficient.
- Do not leave duplicated explanatory paragraphs across notes unless the distinction in meaning is intentional.
- Do not rewrite unrelated parts of either note while doing the boundary cleanup.
- If the boundary is ambiguous, explain the tradeoff before making broader structural changes.
