# Codex Skill Hierarchy

Skills are organized by **capability ownership**. A higher-level workflow delegates to lower-level skills instead of copying their procedures.

## Repository policy

`AGENTS.md` defines repository-wide knowledge architecture: note ownership, abstraction boundaries, acceptable duplication, examples, and semantic linking.

`.codex/model_instructions.md` defines default note-writing behavior.

Skills reference these policies rather than maintaining competing copies.

## Reusable primitives

- **`note-topic-search`** — retrieve relevant repository notes.
- **`note-boundary-analysis`** — classify canonical content, local context, examples, implementation detail, application consequences, and duplicates.
- **`note-writer`** — write scoped note prose after placement and boundaries are known.
- **`note-content-mover`** — execute approved cross-note structural mutations.
- **`markdown-link-normalizer`** — mechanically normalize and validate local links.
- **`markdownlint-fix`** — repair Markdown lint findings.

## Semantic decisions

- **`note-home-finder`** — choose reuse/extend/create/split outcomes and canonical destinations. It delegates repository retrieval to `note-topic-search`.

## Composite workflows

- **`note-authoring`** — substantial new notes or sections. It composes placement, boundary analysis, writing, link validation, and lint repair.
- **`note-content-boundary`** — cross-note cleanup and refactoring. It composes placement, boundary analysis, content movement, prose repair, and link validation.
- **`markdown-consolidator`** — multi-source evidence consolidation. It owns extraction/conflict/review lifecycle, then delegates repository placement, boundaries, writing, and links to the same lower-level capabilities.

## Dependency rule

If a lower-level skill owns a capability, a higher-level skill must invoke or inject that skill instead of reproducing its detailed procedure.

Dependencies flow downward. Primitive skills must not invoke composite workflows that depend on them.
