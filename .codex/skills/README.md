# Codex Skill Hierarchy

Skills are organized by **capability ownership**. Higher-level workflows delegate to lower-level skills instead of copying their procedures.

## Policy layer

- `AGENTS.md` defines repository-wide knowledge architecture: note ownership, abstraction boundaries, acceptable duplication, examples, and semantic linking.
- `.codex/model_instructions.md` defines default note-writing behavior.

Skills reference these policies rather than maintaining competing copies.

## Level 1 — Mechanical and retrieval primitives

- **`note-topic-search`** — repository topic retrieval.
- **`markdown-link-normalizer`** — mechanical local-link normalization and validation.
- **`markdownlint-fix`** — Markdown lint repair.

## Level 2 — Semantic decision primitives

- **`note-home-finder`** — canonical placement: reuse, extend, create, or split. Delegates retrieval to `note-topic-search`.
- **`note-boundary-analyzer`** — scope distribution after placement: canonical explanation, local context, examples, implementation/application detail, and duplication.

## Level 3 — Mutation primitives

- **`note-writer`** — scoped note prose and explanatory structure.
- **`note-content-mover`** — approved cross-note structural mutations.

## Level 4 — Note workflows

- **`note-authoring`** — substantial note creation or expansion. Composes placement, boundary analysis, writing, link validation, and lint repair.
- **`note-refactor`** — cross-note cleanup. Composes placement, boundary analysis, content movement, prose repair, link validation, and lint repair.
- **`note-content-boundary`** — compatibility wrapper that delegates to `note-refactor`.

## Level 5 — Repository workflows

- **`markdown-consolidator`** — multi-source evidence consolidation. Owns evidence extraction, comparison, conflict resolution, review, and publication lifecycle, then delegates repository placement, boundaries, writing/mutation, and links to the same lower-level capabilities.

## Dependency contract

Every skill should make its boundary explicit with **Owns**, **Delegates**, and **Must not** responsibilities when applicable.

If a lower-level skill owns a capability, a higher-level skill must invoke or inject that skill rather than reproducing its detailed procedure. Dependencies flow downward; primitives must not invoke composite workflows that depend on them.
