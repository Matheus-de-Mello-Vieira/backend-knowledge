---
name: note-content-mover
description: Execute an already-approved cross-note move, merge, split, or duplicate-removal plan. This is a mutation primitive: preserve meaning, update note structure, and leave only the residual context specified by the plan. Do not decide placement or boundaries here.
---

# Note Content Mover

This skill owns **structural mutation across notes** after semantic decisions are complete.

## Capability ownership

Owns:

- executing approved moves, merges, splits, and duplicate removal;
- removing obsolete headings and repairing local structure;
- preserving the residual context specified by the semantic plan;
- identifying changed paths or anchors for link validation.

Delegates:

- placement to `$note-home-finder`;
- scope/disposition decisions to `$note-boundary-analyzer`;
- substantive prose repair to `$note-writer`;
- broad link repair to `$markdown-link-normalizer`.

Must not reinterpret the semantic plan.

## Required input

An approved plan from `$note-boundary-analyzer` or a higher-level workflow specifying:

- source and destination paths;
- content to move, merge, split, or remove;
- residual local context that should remain;
- headings to preserve, rename, or remove;
- known link targets affected by the move.

If those decisions are not known, delegate upward; do not improvise placement.

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
