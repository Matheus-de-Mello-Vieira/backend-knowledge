---
name: note-content-boundary
description: Refactor overlapping or misplaced Markdown knowledge across notes. This is a composite workflow: delegate placement to $note-home-finder, scope decisions to $note-boundary-analysis, structural mutation to $note-content-mover, prose repair to $note-writer, and broad link repair to $markdown-link-normalizer.
---

# Note Content Boundary

Use this workflow when existing notes overlap, a concept is in the wrong home, implementation detail has leaked across an abstraction boundary, or a cleanup must move/merge/split content without leaving duplication behind.

This skill **does not own** repository search, placement heuristics, boundary classification, prose style, or link-normalization mechanics. It orchestrates the lower-level skills that own those capabilities.

## Delegated capabilities

Required:

1. `$note-home-finder` — identify canonical homes and split decisions.
2. `$note-boundary-analysis` — determine what each note should fully own and what context should remain.
3. `$note-content-mover` — execute approved moves, merges, splits, and duplicate removal.
4. `$note-writer` — repair or integrate prose after structural changes.
5. `$markdown-link-normalizer` — normalize and validate affected local links.

Use `$markdownlint-fix` when the resulting Markdown introduces lint findings.

## Workflow

1. **Resolve ownership**
   - Read the directly affected notes.
   - Delegate canonical-home decisions to `$note-home-finder`.
   - Do not reproduce repository-search logic locally.

2. **Resolve boundaries**
   - Delegate the overlapping material to `$note-boundary-analysis`.
   - Require an explicit disposition for every substantial unit: canonical explanation, required local context, example, implementation detail, application consequence, duplicate, or separate subject.

3. **Apply structural changes**
   - Pass the approved plan to `$note-content-mover`.
   - Do not let the mover reinterpret the plan.

4. **Repair exposition**
   - Use `$note-writer` for substantive rewrites needed because context changed.
   - Keep residual context sufficient but non-duplicative.

5. **Repair links**
   - Use `$markdown-link-normalizer` for path/anchor normalization and validation when the change is broader than a trivial manual edit.

6. **Verify repository cohesion**
   - Confirm each affected note has one center of gravity.
   - Confirm the canonical explanation exists exactly where intended.
   - Confirm examples and implementation details stay within their assigned boundaries.
   - Confirm no accidental same-level duplication remains.
   - Confirm the source and destination both read naturally.

## Constraints

- Do not create a new note unless `$note-home-finder` or the user's explicit instruction establishes it as the correct outcome.
- Do not preserve duplicate full explanations merely because readers might search both locations.
- Do not rewrite unrelated parts of the notes during a boundary cleanup.
- Do not add navigation-only prose to compensate for weak placement.
