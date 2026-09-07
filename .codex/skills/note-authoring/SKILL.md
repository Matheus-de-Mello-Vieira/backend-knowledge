---
name: note-authoring
description: Add substantial knowledge to this repository while preserving canonical ownership, abstraction boundaries, writing style, and links. This is the default composite workflow for creating a note or adding a meaningful new section; it delegates each capability to the lower-level skill that owns it.
---

# Note Authoring

Use this workflow for substantial additions, new sections, or new notes. Small local corrections should normally be edited directly without invoking the full hierarchy.

## Capability ownership

Owns:

- sequencing substantial note creation or expansion;
- carrying placement and boundary decisions into a validated repository edit.

Delegates:

1. `$note-home-finder` — canonical destination or split plan.
2. `$note-boundary-analyzer` — exact scope each destination owns.
3. `$note-writer` — note prose and explanatory structure.
4. `$markdown-link-normalizer` — mechanical local-link normalization and validation.
5. `$markdownlint-fix` — introduced Markdown lint findings when applicable.
6. `$note-refactor` — existing misplaced or duplicated content that must move across note boundaries before authoring can proceed cleanly.

Must not reproduce the internal procedures of delegated skills.

## Workflow

1. **Place**
   - Send the topic or draft to `$note-home-finder`.
   - Treat a user-supplied target as strong evidence, not an exemption from architecture checks for substantial additions.

2. **Bound**
   - Send the placement result and proposed material to `$note-boundary-analyzer`.
   - Require explicit separation of canonical explanation, local context, examples, implementation detail, application consequences, and duplicates.

3. **Refactor first when necessary**
   - If existing notes already contain misplaced or duplicate material that blocks clean ownership, invoke `$note-refactor`.

4. **Write**
   - Give `$note-writer` the approved destination, abstraction level, boundary plan, relevant source material, and nearby note context.
   - The writer must not reopen placement decisions.

5. **Link and validate**
   - Normalize links with `$markdown-link-normalizer` when necessary.
   - Run Markdown lint/fix when appropriate.
   - Reread affected notes for conceptual cohesion.

## Acceptance criteria

The edit is complete only when:

- every substantial concept has one canonical home at the intended abstraction level;
- each note retains a clear center of gravity;
- local context is sufficient without reproducing neighboring theory;
- concrete examples remain subordinate to the concept;
- implementation-specific material lives in implementation-specific notes unless required briefly for illustration;
- links express genuine conceptual relationships;
- the final Markdown is structurally valid.

Apply the edit directly when write access is available. Report the durable files changed and the substantive architectural decision concisely.
