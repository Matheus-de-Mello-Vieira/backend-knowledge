---
name: markdown-consolidator
description: Orchestrate mandatory, independently reviewed multi-subagent consolidation of overlapping Markdown sources. Standalone mode produces one self-contained publication. Repository-integrated mode preserves the full supported evidence union while delegating note placement, content boundaries, note writing, and link mechanics to the same lower-level skills used by ordinary repository authoring.
---

# Markdown Consolidator

Consolidate selected Markdown evidence without losing supported information. The result is either one standalone publication or a reviewed set of durable notes integrated into an existing Markdown repository.

The consolidator owns **multi-source evidence orchestration**: inventory, extraction, topic organization, comparison, conflict resolution, review, validation, and publication lifecycle. It does not own repository search, note placement, content-boundary policy, repository prose style, or local-link mechanics.

The main agent is orchestration-only. Semantic producers, stage reviewers, patch analysts, finalizers, and validators run as spawned subagents. If subagent execution is unavailable, stop with `subagent execution unavailable`.

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

These files are authoritative for their subjects. Inject applicable references and lower-level skill instructions directly into delegated tasks; do not paraphrase them into weaker or competing rules.

## Repository capability delegation

Repository-integrated mode must reuse the canonical repository capabilities:

- `$note-home-finder` — placement. It delegates retrieval to `$note-topic-search`.
- `$note-boundary-analysis` — canonical coverage versus local context, examples, implementation detail, and application consequences.
- `$note-writer` — repository-note prose and explanatory structure after placement and boundaries are accepted.
- `$markdown-link-normalizer` — mechanical local-link normalization and validation.

Do not restate the internal procedures of these skills inside consolidator prompts. The consolidator adapts their outputs to its evidence contracts and review lifecycle.

## Main-agent boundary

The main agent may resolve paths and mode, inventory files, locate companion skills, create task specifications and attempts, spawn and wait for subagents, reconcile attempts, snapshot durable notes, run deterministic scripts, inspect machine-readable results, publish accepted candidates, and report metrics.

The main agent must not decide note placement, design outlines, extract or organize information, compare or resolve claims, decide note boundaries, plan semantic integration, write or repair note prose, perform semantic review, fabricate receipts, or bypass a failed gate.

## Instruction priority

1. Explicit user requirements and safety constraints.
2. Complete and accurate preservation of supported meaning.
3. Accepted placement, boundary, conflict, and integration decisions.
4. Repository architecture from `AGENTS.md` and delegated repository-skill decisions.
5. Consolidation-specific writing and publication rules.
6. Preferred practices.

Remove only duplicated meaning, filler, ceremony, and non-operational commentary. Preserve facts, scope, nuance, uncertainty, limitations, dependencies, exceptions, rationale, alternatives, examples, code, tables, external references, conflicts, and historical states.

## Publication modes

### Standalone

Produce one self-contained Markdown document. Do not cite, name, or link temporary evidence files. Apply the standalone writing rules in `references/writing-policy.md`.

### Repository integrated

Reuse, extend, create, or split durable notes in an existing Markdown repository.

Runtime-discovered companions remain:

- `note-home-finder` for placement;
- `markdown-link-normalizer` for final local-link normalization and validation.

Repository-local semantic capabilities additionally required by the workflow are:

- `note-boundary-analysis`;
- `note-writer`.

Load their current `SKILL.md` files unchanged from `.codex/skills/` and inject them into the relevant semantic tasks as described in `references/companion-skills.md`.

Classify files as evidence sources, destination notes, or read-only context notes. Evidence sources may be deleted afterward and must never be cited or linked.

## Disposable work layout

Put internal state under:

```text
<output-or-repository-root>/.markdown-consolidator-work/
  runtime-plan.json
  companion-skills.json
  inventory.json
  task-ledger.json
  attempts.json
  task-specs/
  receipts/
  reviews/
  placement-plan.json
  placement-validation-report.json
  destination-snapshots/
  repository-context.json
  outline.json
  units/
  topics.json
  comparisons/
  decision-ledger.json
  integration-plan.json
  integration-plan-validation-report.json
  patches/
  drafts/
  publication-manifest.json
  candidates/
  normalized-candidates/
  repository-shadow/
  coverage-map.json
  materialization-report.json
  link-pipeline-report.json
  repository-integration-report.json
  validation/
  task-lifecycle-report.json
  review-validation-report.json
  validation-report.json
  writing-validation-report.json
  delegation-validation-report.json
```

Standalone runs may omit repository-only artifacts. Do not delete the work directory unless cleanup is requested.

## Canonical stage cycle

Every semantic stage follows:

```text
specify → produce by subagent → reconcile producer
        → independent subagent review → reconcile review
        → deterministic validation when available
        → advance or retry
```

A downstream semantic stage starts only after the current stage passes review and deterministic validation.

## Explicit execution order

### 0. Resolve mode and paths

Record publication mode, evidence scope, repository root when applicable, final destination, audience, purpose, output format, assumed knowledge, terminology constraints, work directory, and cleanup preference.

Use `repository_integrated` when the result should participate in the existing note repository. Otherwise use `standalone`.

Exclude the work directory and intended durable outputs from evidence inventory.

### 1. Inventory and initialize

Run `inventory_markdown.py` on evidence only. Stop if complete inventory is impossible.

Initialize lifecycle state with subagents required, no fallback, a bounded concurrency cap, and the selected publication mode.

### 2. Resolve repository capabilities — repository mode only

1. Run `locate_companion_skills.py` for runtime-discovered placement and link capabilities.
2. Load `.codex/skills/note-boundary-analysis/SKILL.md`.
3. Load `.codex/skills/note-writer/SKILL.md`.
4. Stop if any required repository capability is unavailable.

Record the runtime-discovered skill paths in `companion-skills.json`; treat repository-local skill files as authoritative semantic inputs.

### 3. Produce, review, and validate placement — repository mode only

1. Spawn one `note-home-finder-adapter` attempt covering all evidence sources.
2. Inject the exact `note-home-finder/SKILL.md` unchanged.
3. Reconcile the producer.
4. Spawn and reconcile an independent stage review.
5. Run `validate_placement.py`.
6. Advance only when review and validation pass.

Then run `snapshot_repository_context.py` for all existing destinations and context notes.

### 4. Produce and review the outline

Spawn one `outline-planner` covering all evidence sources. In repository mode, also provide the accepted placement plan and repository context snapshots. Reconcile, review independently, validate the Outline contract, and advance only on success.

### 5. Produce, review, and validate extraction

Partition evidence sources with `schedule_batches.py`, run bounded source-analyst waves, reconcile and retry failed logical tasks, independently review every accepted extraction attempt, and run `validate_units.py`.

Do not advance until source assignment, line coverage, review coverage, and unit validation pass.

### 6. Produce, review, and validate topic organization

Spawn one full-unit `topic-organizer`, reconcile it, review it independently, and run `validate_topics.py`.

### 7. Produce, review, and validate comparisons

Partition topic IDs into disjoint batches, spawn `topic-comparator` attempts, reconcile them, independently review each accepted attempt, and run `validate_comparisons.py`.

### 8. Produce, review, and validate conflict decisions

Use `comparisons/index.json.required_resolution_ids` as exact scope.

- When non-empty, run bounded conflict-resolution attempts, independent review, and `validate_decisions.py`.
- When empty, record the conflict-resolution task as skipped with an explicit reason.

### 9. Produce, review, and validate integration plan — repository mode only

1. Spawn one full-unit `integration-planner` with placement, snapshots, context notes, topics, comparisons, and decisions.
2. Inject `note-boundary-analysis/SKILL.md` unchanged.
3. Require the planner to assign every source unit one primary destination and to limit repeated context according to the boundary skill.
4. Reconcile it.
5. Spawn and reconcile an independent stage review.
6. Run `validate_integration_plan.py`.
7. Advance only when destination, boundary, and link plans pass.

### 10. Produce and review the full publication

Create the single logical task `publication`.

- Standalone mode: spawn one full-scope `synthesizer`, apply the standalone writing policy, then run `materialize_publication.py`.
- Repository mode: spawn one full-scope, full-destination `synthesizer`, inject `note-writer/SKILL.md` unchanged together with the accepted boundary/integration plan, then run `materialize_publication_set.py` into the disposable candidate root.

Reconcile the publication attempt. Spawn an independent publication-stage review with annotated output, clean candidates, dispositions, coverage map, outline, decisions, and the applicable writing/boundary inputs. Require the review to pass.

The writer uses temporary `MC` evidence markers. Never hand-maintain evidence excerpts.

### 11. Validate lifecycle and stage-review coverage

Run `validate_task_lifecycle.py` and `validate_reviews.py`. Do not spawn final validators until both pass.

### 12. Run final semantic and deterministic validation

Spawn at least two validator tasks with disjoint category scopes.

All modes require exact coverage of:

- `coverage`
- `conflicts_qualifiers`
- `standalone_exposition`
- `coherence_markdown`
- `writing_quality`

Repository mode additionally requires:

- `repository_integration`
- `link_context`

Standalone mode runs `validate_consolidation.py` and `validate_writing.py`.

Repository mode:

1. run `validate_writing.py` for every candidate note;
2. validate center of gravity, abstraction level, and duplication against the accepted boundary plan;
3. run `run_link_pipeline.py` using `markdown-link-normalizer`;
4. run `validate_repository_integration.py` against normalized candidates;
5. treat new or evidence-deletion-exposed broken links as errors and unchanged pre-existing failures as warnings.

Every semantic or writing finding must be accepted or repaired before publication.

### 13. Repair

Run at most three repair cycles:

1. group accepted findings into bounded scopes;
2. spawn patch-analyst tasks;
3. spawn a full-scope publication-finalizer attempt;
4. in repository mode, reinject `note-writer/SKILL.md` and the accepted boundary plan;
5. reconcile and materialize the complete revision;
6. independently review the new publication;
7. rerun applicable lifecycle, review, content, boundary, writing, repository, link, and delegation validation.

A patch analyst never owns publication output. A finalizer owns every unit and destination.

### 14. Run final delegation validation

Run `validate_delegation.py`. It must validate accepted producer assignments, required repository stages, review coverage, complete publication ownership, final validator coverage, receipt hashes, outputs, and terminal lifecycle state.

### 15. Publish

Publish only when every required semantic review and deterministic report passes.

- Standalone: copy the accepted clean candidate to the requested final path.
- Repository mode: copy only normalized candidates from `normalized-candidates/` to their reviewed destination paths. Do not modify context notes unless they were approved destinations.

Do not publish annotated drafts, snapshots, plans, reviews, receipts, or internal identifiers. Delete the work directory only after successful publication and only when cleanup was requested.

## Required invariants

- every selected evidence source is assigned once to accepted extraction work;
- every non-empty evidence line is extracted;
- every unit has one primary topic, comparison accounting, disposition, and final representation;
- every required conflict is resolved or visibly preserved as unresolved;
- every accepted producer in a required phase is independently reviewed exactly once;
- exactly one full-scope publication attempt is accepted;
- final validator categories are covered exactly once across at least two agents;
- no attempt remains active or unreconciled at publication time;
- no nested spawning, hash mismatch, stale evidence, evidence citation, source-dependent phrase, or blocking writing defect remains;
- repository mode has one reviewed placement plan and one reviewed boundary-aware integration plan;
- repository units have exactly one primary destination;
- repeated context is explicit, bounded, and not a duplicate canonical explanation;
- each repository destination preserves its center of gravity and abstraction level;
- context notes remain read-only unless promoted;
- existing destination headings are preserved unless approved;
- no final link targets disposable evidence;
- no new broken local path or anchor remains after normalization.

## Final response

Report durable publication paths, mode, review/content/writing/lifecycle/delegation status, repository/link status when applicable, source and unit counts, destination count, accepted/superseded/failed attempt counts, unresolved-conflict count, and work-directory cleanup status. Do not dump internal artifacts or private reasoning.
