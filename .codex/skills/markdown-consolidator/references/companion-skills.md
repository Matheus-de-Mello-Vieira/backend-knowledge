# Companion skill interaction

Repository-integrated consolidation participates in the same capability hierarchy as ordinary note authoring and refactoring. The consolidator owns multi-source evidence extraction, conflict resolution, review, and publication orchestration. It delegates repository capabilities to their canonical lower-level skills instead of maintaining parallel implementations.

## Capability hierarchy

Repository mode uses:

- `$note-home-finder` for canonical placement. That skill delegates repository retrieval to `$note-topic-search`.
- `$note-boundary-analyzer` for deciding what each destination should fully own versus keep only as local context, example, implementation detail, or application consequence.
- `$note-writer` for repository-note prose and explanatory structure after placement and boundaries are accepted.
- `$note-content-mover` when an accepted integration plan requires structural movement of existing durable content between notes.
- `$markdown-link-normalizer` for mechanical local-link normalization and validation.
- `$note-refactor` when a repository integration requires a complete cross-note refactor rather than a simple evidence-to-destination synthesis.

The consolidator must not restate qmd search procedures, note-boundary heuristics, repository writing style, content-movement rules, or Markdown link mechanics when a lower-level skill already owns them.

## Discovery

Run `scripts/locate_companion_skills.py` before repository-integrated work for runtime-discovered capabilities. The current locator verifies `note-home-finder` and `markdown-link-normalizer`.

Load the current repository-local semantic/mutation skills directly from `.codex/skills/` when required:

- `note-boundary-analyzer/SKILL.md`
- `note-writer/SKILL.md`
- `note-content-mover/SKILL.md`
- `note-refactor/SKILL.md`

Standalone consolidation does not require repository note skills.

## Placement handoff

Use `note-home-finder` inside the placement producer task. Give that subagent the exact skill instructions, source inventory and representative source content, repository root, intended audience and purpose, the Placement Plan contract, and read-only repository access.

The adapter returns only the placement decision. Search mechanics remain delegated through the home-finder hierarchy.

## Boundary handoff

Before repository integration planning, inject `note-boundary-analyzer/SKILL.md` unchanged. The integration plan must assign each source unit one primary destination and explicitly distinguish canonical coverage, concise local context, bounded examples, implementation/application handoffs, and non-duplicated bodies.

## Mutation handoff

If the accepted integration plan requires moving existing durable repository content across notes, use `note-content-mover` for the approved structural operation. If the change is a broader cross-note cleanup with placement, boundary, movement, prose, and link repair, delegate that portion to `note-refactor` rather than recreating the workflow inside the consolidator.

## Writing handoff

For repository publication, inject `note-writer/SKILL.md` unchanged into the synthesizer/finalizer task and treat it as authoritative for repository prose and structure. The consolidator's own writing policy governs standalone publications and evidence-preservation constraints, not repository prose style.

## Markdown Link Normalizer handoff

Use the companion scripts only after candidate paths, headings, and link plans are stable. `run_link_pipeline.py` builds a disposable repository shadow, records pre-existing failures, overlays candidates, normalizes changed notes, validates the full shadow tree, and copies normalized candidates to the normalized-output directory.

New or deletion-exposed broken links block publication. Unchanged pre-existing failures are warnings. Never normalize unrelated repository notes by default.

## Mutation boundary

- Evidence sources are disposable and must never be cited or linked.
- Destination notes are the only durable files that may be created or modified.
- Context notes are read-only discovery and link targets unless the placement plan explicitly promotes them to destinations.
- Reciprocal-link edits to context notes require explicit user instruction and a new placement decision.
