---
name: note-content-mover
description: Execute an already-approved cross-note move, merge, split, or duplicate-removal plan. This is a mutation primitive: preserve meaning, update note structure, and leave only the residual context specified by the plan. Do not decide placement or boundaries here.
---

# Note Content Mover

This skill owns **structural mutation across notes** after semantic decisions are complete.

## Required input

An approved plan from `$note-boundary-analysis` or a higher-level workflow that specifies:

- source and destination paths;
- content to move, merge, split, or remove;
- residual local context that should remain;
- headings to preserve, rename, or remove;
- known link targets affected by the move.

If those decisions are not known, stop and delegate upward to `$note-boundary-analysis`; do not improvise placement.

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

Residual content should explain the source note's own subject, not justify navigation.

Prefer a concise local explanation with an inline link on existing meaningful text. Do not leave “see more” sections or headings whose only content is a redirect.

## Link handoff

After structural mutation:

- identify paths or anchors that changed;
- hand broad link repair and validation to `$markdown-link-normalizer`;
- do not invent targets that were not verified.

## Verification

Confirm:

- the source still reads naturally after removal;
- the destination now owns the moved concept at the intended abstraction level;
- no same-level duplicate body remains unintentionally;
- no useful supported meaning was lost;
- no orphan heading was introduced.

This skill does not decide prose style beyond minimal adaptation. Substantive rewriting belongs to `$note-writer`.
