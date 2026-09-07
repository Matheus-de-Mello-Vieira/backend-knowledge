---
name: markdown-consolidator
description: Orchestrate mandatory, independently reviewed multi-subagent consolidation of overlapping Markdown sources. Standalone mode produces one self-contained publication. Repository-integrated mode preserves the full supported evidence union while delegating note placement, content boundaries, writing/mutation, and link mechanics to the same lower-level skills used by ordinary repository workflows.
---

# Markdown Consolidator

Consolidate selected Markdown evidence without losing supported information. The result is either one standalone publication or a reviewed set of durable notes integrated into an existing Markdown repository.

The consolidator owns **multi-source evidence orchestration**: inventory, extraction, topic organization, comparison, conflict resolution, review, validation, and publication lifecycle. It does not own repository retrieval, note placement, content-boundary policy, repository prose style, cross-note mutation semantics, or local-link mechanics.

The main agent is orchestration-only. Semantic producers, stage reviewers, patch analysts, finalizers, and validators run as spawned subagents. If subagent execution is unavailable, stop with `subagent execution unavailable`.

## Repository capability delegation

Repository-integrated mode reuses the canonical repository capabilities:

- `$note-home-finder` — placement; it delegates retrieval to `$note-topic-search`.
- `$note-boundary-analyzer` — canonical coverage versus local context, examples, implementation detail, application consequences, and duplication.
- `$note-writer` — repository-note prose and explanatory structure after placement and boundaries are accepted.
- `$note-content-mover` — approved structural movement of existing durable content.
- `$note-refactor` — complete cross-note cleanup when integration requires placement + boundary + mutation + prose/link repair.
- `$markdown-link-normalizer` — mechanical local-link normalization and validation.

Do not restate the internal procedures of these skills inside consolidator prompts. Adapt their outputs to consolidation evidence contracts and the review lifecycle.

## Read in this order

1. `references/contracts.md`
2. `references/execution-protocol.md`
3. `references/review-protocol.md`
4. `references/decision-policy.md`
5. `references/writing-policy.md`
6. `references/evidence-materialization.md`
7. `references/quality-gates.md`
8. For repository-integrated mode: `references/companion-skills.md`
9. For repository-integrated mode: `references/repository-integration.md`

These files are authoritative for consolidation-specific subjects. Inject applicable lower-level skill instructions unchanged rather than paraphrasing them into competing rules.

## Main-agent boundary

The main agent may resolve paths and mode, inventory files, locate companion skills, create task specifications and attempts, spawn and wait for subagents, reconcile attempts, snapshot durable notes, run deterministic scripts, inspect machine-readable results, publish accepted candidates, and report metrics.

The main agent must not decide note placement, extract or organize information, compare or resolve claims, decide note boundaries, write or repair note prose, invent cross-note mutation policy, perform semantic review, fabricate receipts, or bypass a failed gate.

## Publication modes

### Standalone

Produce one self-contained Markdown document. Do not cite, name, or link temporary evidence files. Apply `references/writing-policy.md` directly.

### Repository integrated

Reuse, extend, create, or split durable notes in an existing Markdown repository. Runtime-discovered companions remain `note-home-finder` and `markdown-link-normalizer`. Load repository-local `note-boundary-analyzer`, `note-writer`, `note-content-mover`, and `note-refactor` skill instructions as required by `references/companion-skills.md`.

Classify files as evidence sources, destination notes, or read-only context notes. Evidence sources may be deleted afterward and must never be cited or linked.

## Execution order

The existing consolidation lifecycle remains authoritative for inventory, extraction, topic organization, comparison, conflict resolution, independent review, deterministic validation, repair, and publication. Repository-specific stages add the following handoffs:

1. **Placement:** inject `$note-home-finder` into the placement producer and validate the placement plan.
2. **Boundary analysis:** inject `$note-boundary-analyzer` into repository integration planning; every source unit receives one primary destination and any repeated local context is explicitly bounded.
3. **Structural mutation:** when integration moves existing durable repository content, execute the approved move through `$note-content-mover`; use `$note-refactor` for broader cross-note cleanup.
4. **Repository writing:** inject `$note-writer` into repository synthesizer/finalizer tasks after placement and boundaries are accepted.
5. **Links:** run `$markdown-link-normalizer` after candidate paths/headings stabilize.
6. **Validation:** verify coverage across the publication set, note center of gravity, abstraction level, bounded repetition, source preservation, and local-link validity before publication.

Do not replace or weaken the consolidator's existing evidence accounting, conflict resolution, review, lifecycle, and deterministic quality gates.

## Required invariants

In addition to the existing consolidation invariants:

- repository mode has one reviewed placement plan and one boundary-aware integration plan;
- every source unit has exactly one primary destination;
- repeated context is explicit, bounded, and not a duplicate canonical explanation;
- every destination preserves its center of gravity and intended abstraction level;
- structural moves of existing durable content follow `$note-content-mover` or `$note-refactor` rather than ad hoc synthesizer policy;
- repository prose follows `$note-writer`;
- no final link targets disposable evidence;
- no new broken local path or anchor remains after normalization.

## Final response

Report durable publication paths, publication mode, review/content/writing/lifecycle/delegation status, repository/link status when applicable, source and unit counts, destination count, unresolved-conflict count, and work-directory cleanup status. Do not dump internal artifacts or private reasoning.
