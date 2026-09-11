---
name: note-refactor
description: Refactor existing knowledge across Markdown note boundaries: move, split, merge, deduplicate, or repair abstraction leakage without losing meaning. Use when durable content already exists and its ownership or distribution must change.
---

# Note Refactor

This is the canonical cross-note structural workflow.

## Scope gate

### Known pair / explicit intended boundary

When the user names the affected notes and their intended responsibilities are already clear, skip repository-wide placement. Load `references/pairwise-boundary.md`, then invoke `$note-boundary-analyzer` directly.

### Ownership uncertain or more than two destinations

Invoke `$note-home-finder` and load `references/multi-note-refactor.md` only when canonical homes, split destinations, or reading intents are unresolved.

## Mutation gates

1. `$note-boundary-analyzer` produces the disposition plan.
2. Invoke `$note-content-mover` only for approved structural movement/removal.
3. Invoke `$note-writer` only where moved/removed context leaves prose that requires substantive repair. The writer owns lint validation for any Markdown it mutates.
4. Invoke `$note-link-planner` only when new semantic links are needed and their targets are not already specified by the plan.
5. Invoke `$markdown-link-normalizer` only when paths or anchors changed.
6. For structural Markdown mutations performed outside `$note-writer`, invoke `$markdownlint-fix` when the mutating capability's contract requires lint validation or when those mutations introduce or expose lint findings. A writer lint pass does not validate later mutations automatically.

## Final review

Invoke `$note-cohesion-reviewer` after a substantive refactor. Give it the affected notes plus the accepted boundary plan so it can check canonical ownership, center of gravity, abstraction level, residual context, and accidental duplication.

## Constraints

- Do not preserve duplicate full explanations merely because readers may search both locations.
- Do not rewrite unrelated sections.
- Do not create a new destination unless accepted placement establishes it.
- Residual source text should explain the source note's own subject, not act as navigation-only prose.
