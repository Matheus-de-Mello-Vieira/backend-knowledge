# Companion skill interaction

This skill supports repository integration through two independently installed companion skills. Use their current `SKILL.md` files as authoritative inputs; do not copy or reinterpret their internal search and link-style rules.

## Discovery

Run `scripts/locate_companion_skills.py` before repository-integrated work. It searches repository- and user-scoped `.agents/skills/` and `.codex/skills/` locations. Explicit paths may override discovery.

Required companions:

- `note-home-finder`
- `markdown-link-normalizer`

Stop repository-integrated execution when either companion is unavailable. Standalone consolidation does not require them.

## Note Home Finder handoff

Use the companion skill inside one spawned `note-home-finder-adapter` producer task. Give that subagent:

- the exact companion `SKILL.md`;
- source inventory and representative source content;
- repository root;
- intended audience and purpose;
- the Placement Plan contract;
- read-only repository access.

The adapter follows the companion workflow, including qmd discovery when available and its documented fallback search. It must not create, move, or edit notes. Its only semantic output is `placement-plan.json`.

The placement attempt must pass an independent stage review and `validate_placement.py` before outline planning.

## Markdown Link Normalizer handoff

Use the companion scripts only after candidate paths, headings, and link plan are stable.

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
