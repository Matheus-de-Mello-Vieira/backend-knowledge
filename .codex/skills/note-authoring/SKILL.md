---
name: note-authoring
description: Add already-understood knowledge or repair an explanation in this repository. Use when the content itself is known and the main job is to place, scope, and write it coherently. Do not use for raw source ingestion, learning scaffolds, read-only review, or cross-note structural cleanup.
---

# Note Authoring

This workflow owns **known knowledge → durable explanatory prose**.

## Progressive gates

### Target gate

If the target note/section is explicit and the new material clearly belongs to its established subject, skip repository-wide placement.

If ownership is unclear, compound, or likely to create a new note, invoke `$note-home-finder` (which discloses `$note-topic-search` as needed).

### Boundary gate

Invoke `$note-boundary-analyzer` only when the proposed material can cross subjects or abstraction levels, contains implementation/application detail, or may duplicate another canonical explanation. Skip it for a narrow addition with an obvious local scope.

### Structural gate

Invoke `$note-content-mover` only when an accepted boundary plan says existing durable material must move, merge, split, or be removed as duplication.

### Writing gate

Invoke `$note-writer` for the substantive prose edit. Provide only accepted semantic inputs; the writer must not reopen placement decisions.

### Link gate

Invoke `$note-link-planner` when a substantial edit introduces concepts that naturally benefit from existing repository context or when the user asks for links. Otherwise skip semantic link planning.

Invoke `$markdown-link-normalizer` only when links or anchors changed.

### Review gate

For edits that change note scope, headings, multiple conceptual units, or abstraction boundaries, invoke `$note-cohesion-reviewer` before finalizing. For a narrow local clarification, the writer's own verification is sufficient.

Invoke `$markdownlint-fix` only when lint findings are introduced or exposed.

## Question-driven amendment

When the user asks a conceptual question about an existing note and wants it fixed, treat the question as a documentation defect. Insert the missing definition, distinction, state transition, assumption, or causal link where the ambiguity first appears rather than appending an FAQ.

## Acceptance criteria

The smallest sufficient capability set was used; the edited note remains centered, locally sufficient, non-duplicative, and at the intended abstraction level; examples remain subordinate; and any changed links/Markdown validate.