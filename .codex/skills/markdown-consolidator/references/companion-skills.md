# Companion skill interaction

Repository-integrated consolidation participates in the same skill hierarchy as ordinary note authoring. The consolidator owns multi-source evidence extraction, conflict resolution, review, and publication orchestration. It must delegate repository capabilities to their canonical lower-level skills instead of maintaining parallel implementations.

## Capability hierarchy

Repository mode uses:

- `$note-home-finder` for canonical placement. That skill delegates repository retrieval to `$note-topic-search`.
- `$note-boundary-analysis` for deciding what each destination should fully own versus keep only as local context, example, implementation detail, or application consequence.
- `$note-writer` for repository-note prose and explanatory structure after placement and boundaries are accepted.
- `$markdown-link-normalizer` for mechanical local-link normalization and validation.

The consolidator must not restate qmd search procedures, note-boundary heuristics, repository writing style, or Markdown link mechanics when the lower-level skill already owns them.

## Discovery

Run `scripts/locate_companion_skills.py` before repository-integrated work for companions that require runtime discovery. The current locator verifies:

- `note-home-finder`
- `markdown-link-normalizer`

`note-boundary-analysis` and `note-writer` are repository-local semantic capabilities. Load their current `SKILL.md` files from `.codex/skills/` and inject them unchanged into the relevant repository-mode subagent tasks.

Standalone consolidation does not require repository note skills.

## Placement handoff

Use `note-home-finder` inside the placement producer task. Give that subagent:

- the exact `note-home-finder/SKILL.md`;
- source inventory and representative source content;
- repository root;
- intended audience and purpose;
- the Placement Plan contract;
- read-only repository access.

The adapter returns only the placement decision. Search mechanics remain delegated through the home-finder hierarchy.

The placement attempt must pass independent stage review and `validate_placement.py` before outline planning.

## Boundary handoff

Before repository integration planning, inject `note-boundary-analysis/SKILL.md` unchanged.

The integration plan must assign each source unit to one primary destination and determine whether neighboring destinations need:

- canonical coverage;
- concise local context;
- a bounded example;
- an implementation/application handoff;
- or no duplicated body.

The planner must not invent a separate boundary policy.

## Writing handoff

For repository publication, inject `note-writer/SKILL.md` unchanged into the synthesizer/finalizer task and treat it as authoritative for repository prose and structure.

The consolidator's own writing policy continues to govern standalone publications and evidence-preservation constraints. When repository-specific style rules overlap with `note-writer`, the lower-level repository writing skill owns the implementation.

## Markdown Link Normalizer handoff

Use the companion scripts only after candidate paths, headings, and link plans are stable.

`run_link_pipeline.py`:

1. builds a disposable repository shadow;
2. records pre-existing link failures;
3. removes selected evidence files from the final-state shadow;
4. overlays the candidate publication set;
5. invokes the companion normalizer only on changed candidate notes;
6. invokes the companion validator across the full shadow tree;
7. copies normalized candidates to the normalized-output directory.

New or deletion-exposed broken links block publication. Unchanged pre-existing failures are warnings. Never normalize unrelated repository notes by default.

## Mutation boundary

- Evidence sources are disposable and must never be cited or linked.
- Destination notes are the only durable files that may be created or modified.
- Context notes are read-only discovery and link targets unless the placement plan explicitly promotes them to destinations.
- Reciprocal-link edits to context notes require an explicit user instruction and a new placement decision.
