# Codex Skill Hierarchy

Skills are organized by **capability ownership**. Higher-level workflows compose lower-level capabilities instead of copying their procedures.

## Policy layer

- `AGENTS.md` defines repository-wide knowledge architecture: note ownership, abstraction boundaries, acceptable duplication, examples, and semantic linking.
- `.codex/model_instructions.md` defines default note-writing behavior.

Skills reference these policies rather than maintaining competing copies.

## Level 1 — Retrieval and mechanical primitives

- **`note-topic-search`** — repository topic retrieval.
- **`markdown-link-normalizer`** — mechanical local-link normalization and validation.
- **`markdownlint-fix`** — Markdown lint repair.

## Level 2 — Semantic decision primitives

- **`note-home-finder`** — canonical placement: reuse, extend, create, or split. It invokes only `note-topic-search`.
- **`note-boundary-analyzer`** — scope distribution after placement. It consumes an accepted placement but does not invoke placement, writing, or mutation skills.

## Level 3 — Mutation primitives

- **`note-writer`** — scoped note prose and explanatory structure from approved semantic inputs.
- **`note-content-mover`** — approved cross-note structural mutation from an approved boundary/move plan.

Mutation primitives do not invoke semantic-decision or workflow skills. Missing prerequisites are returned to the caller.

## Level 4 — Note workflows

- **`note-authoring`** — substantial note creation or expansion. Composes placement, boundary analysis, optional movement, writing, link validation, and lint repair.
- **`note-refactor`** — cross-note cleanup. Composes placement, boundary analysis, content movement, prose repair, link validation, and lint repair.
- **`note-content-boundary`** — compatibility wrapper that delegates to `note-refactor`.

## Level 5 — Repository workflows

- **`markdown-consolidator`** — multi-source evidence consolidation. Owns evidence extraction, comparison, conflict resolution, review, and publication lifecycle, then composes the same placement, boundary, mutation, writing, and link primitives used by note workflows.

## Dependency contract

Every skill should make its boundary explicit with **Owns**, **Requires/Inputs**, **Delegates**, and **Must not** responsibilities when applicable.

Invocation dependencies flow from more abstract workflows toward more concrete capabilities. A semantic or mutation primitive must not invoke a workflow that depends on it. Data may flow between primitives in sequence—for example, a boundary analyzer consumes an accepted placement—but the caller owns that sequencing.
