---
name: markdown-consolidator
description: Consolidate multiple overlapping Markdown sources with exhaustive evidence preservation, conflict handling, independent review, and optional repository integration. This is the heavy workflow for multi-source reconciliation; ordinary single-source ingestion should use note-ingestion.
---

# Markdown Consolidator

The consolidator owns **multi-source evidence orchestration**: inventory, exhaustive extraction, topic organization, comparison, conflict resolution, independent review, deterministic validation, repair, and publication lifecycle.

It composes repository primitives for placement, boundaries, mutation, writing, and links rather than reimplementing them.

## Mode gate

- **Standalone:** produce one self-contained publication.
- **Repository integrated:** publish the supported knowledge union into durable repository notes.

If the request is only one clean source without exhaustive source accounting, prefer `$note-ingestion` instead.

## Progressive reference loading

Do not read every reference up front.

- Before the first semantic subagent, load `references/execution-protocol.md`.
- Load the relevant contract sections from `references/contracts.md` when a stage begins producing or validating that artifact type.
- At extraction/materialization stages, load `references/evidence-materialization.md` and inject `$knowledge-unit-extractor` in **exhaustive** mode into source-analysis work; consolidation contracts remain authoritative for IDs, ranges, and coverage.
- Before the first independent review, load `references/review-protocol.md`.
- Load `references/decision-policy.md` only when comparison output contains conflicts that require semantic resolution.
- Load `references/writing-policy.md` only before publication synthesis/finalization.
- Load `references/quality-gates.md` only for final validation and repair.
- Load `references/companion-skills.md` and `references/repository-integration.md` only in repository-integrated mode.

## Repository capability gates

In repository mode:

- placement uses `$note-home-finder` only when durable destinations are not already fixed by an accepted user constraint;
- boundary distribution uses `$note-boundary-analyzer` after placement;
- `$note-content-mover` is loaded only when accepted integration requires moving existing durable repository content;
- repository prose uses `$note-writer` only after placement/boundary decisions are accepted;
- `$markdown-link-normalizer` runs only after candidate paths/headings stabilize.

The consolidator is a sibling workflow to `$note-ingestion`, `$note-authoring`, and `$note-refactor`; it does not invoke those workflows.

## Stage router

Execute these groups in order, applying the stage cycle from `references/execution-protocol.md`:

1. **Resolve + inventory:** mode, paths, evidence scope, lifecycle state.
2. **Placement (repository only):** accepted durable destinations and repository snapshots.
3. **Understand evidence:** outline, exhaustive extraction, topic organization.
4. **Reconcile evidence:** comparisons; conflict resolution only when required.
5. **Plan repository integration (repository only):** primary destination for every unit plus boundary-aware local context and links.
6. **Publish candidate:** standalone synthesizer or repository publication set.
7. **Validate:** lifecycle/review coverage, semantic coverage, writing, repository integration, and links.
8. **Repair if required:** bounded repair cycles with a new complete publication attempt and independent re-review.
9. **Publish durable result:** only after all required gates pass.

Exact artifact schemas, review rules, deterministic validators, and publication mechanics live in the stage-specific references and scripts; load them when the corresponding stage starts.

## Non-negotiable invariants

- every selected evidence source is accounted for;
- exhaustive mode represents every required supported unit with provenance;
- every required conflict is resolved or explicitly preserved as unresolved;
- every accepted producer in a required semantic phase receives independent review;
- exactly one full-scope publication revision is accepted at publication time;
- repository mode assigns every source unit one primary durable destination;
- repeated local context is explicit and bounded rather than a second canonical explanation;
- no disposable evidence file becomes a final link target;
- no new broken local path or anchor is published;
- context notes remain read-only unless explicitly promoted to destinations.

## Final response

Report publication mode, durable output paths, source/unit/destination counts, unresolved conflicts, review/validation status, repository/link status when applicable, and cleanup status. Do not dump internal artifacts or private reasoning.