---
name: note-content-mover
description: Execute an already-approved cross-note move, merge, split, or duplicate-removal plan. This is a structural mutation primitive: preserve meaning, update note structure, and leave only the residual context specified by the plan. Do not decide placement or boundaries here.
---

# Note Content Mover

This skill owns **structural mutation across notes** after semantic decisions are complete.

## Capability ownership

Owns:

- executing approved moves, merges, splits, and duplicate removal;
- removing obsolete headings and repairing local structure;
- preserving the residual context specified by the semantic plan;
- identifying changed paths or anchors for later link validation.

Requires:

- an approved boundary/mutation plan specifying source and destination paths;
- content to move, merge, split, or remove;
- residual local context that should remain;
- headings to preserve, rename, or remove;
- known link targets affected by the move.

Must not:

- invoke `$note-home-finder` or `$note-boundary-analyzer`;
- reinterpret placement or boundary decisions;
- invoke `$note-authoring` or `$note-refactor`;
- perform substantive prose redesign beyond minimal adaptation;
- perform broad link normalization.

If the required semantic plan is missing, return that prerequisite to the caller instead of improvising it.

## Mutation rules

- Preserve the complete supported meaning assigned to each destination.
- Adapt moved prose only enough to fit the destination's framing and terminology.
- Remove duplicate source bodies when another note becomes canonical.
- Leave only the residual context explicitly required for local comprehension.
- Remove headings that no longer introduce real content.
- Preserve headings when they still serve a meaningful conceptual unit.
- Do not rewrite unrelated sections.
- Do not create new notes unless the approved plan includes them.

## Residual content

Residual content should explain the source note's own subject, not justify navigation. Prefer concise local explanation with a natural inline link on existing meaningful text; do not leave redirect-only sections.

## Verification

Confirm:

- the source still reads naturally after removal;
- the destination now owns the moved concept at the intended abstraction level;
- no same-level duplicate body remains unintentionally;
- no useful supported meaning was lost;
- no orphan heading was introduced.

Substantive prose repair and mechanical link validation are separate caller-managed stages.
