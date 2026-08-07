---
name: markdown-consolidator
description: Orchestrate mandatory, independently reviewed multi-subagent consolidation of overlapping Markdown sources. Use standalone mode for one self-contained publication or repository-integrated mode to reuse, extend, create, or split durable notes through the installed note-home-finder and markdown-link-normalizer skills. Preserve the complete supported informational union; never replace consolidation with summarization unless explicitly requested.
---

# Markdown Consolidator

Consolidate selected Markdown evidence without losing supported information. The result is either one standalone publication or a reviewed set of notes integrated into an existing Markdown repository.

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

These files are authoritative for their subjects. Inject applicable references directly into delegated tasks; do not paraphrase them into weaker instructions.

## Main-agent boundary

The main agent may resolve paths and mode, inventory files, locate companion skills, create task specifications and attempts, spawn and wait for subagents, reconcile attempts, snapshot durable notes, run deterministic scripts, inspect machine-readable results, publish accepted candidates, and report metrics.

The main agent must not decide note placement, design outlines, extract or organize information, compare or resolve claims, plan semantic integration, write or repair note prose, perform semantic review, fabricate receipts, or bypass a failed gate.

## Instruction priority

1. Explicit user requirements and safety constraints.
2. Complete and accurate preservation of supported meaning.
3. Accepted placement, conflict, and integration decisions.
4. Mandatory writing and repository rules.
5. Preferred practices.
6. Optional techniques.

Remove only duplicated meaning, filler, ceremony, and non-operational commentary. Preserve facts, scope, nuance, uncertainty, limitations, dependencies, exceptions, rationale, alternatives, examples, code, tables, external references, conflicts, and historical states.

## Publication modes

### Standalone

Produce one self-contained Markdown document. Do not cite, name, or link temporary evidence files.

### Repository integrated

Reuse, extend, create, or split durable notes in an existing Markdown repository.

Mandatory companion skills:

- `note-home-finder` for placement;
- `markdown-link-normalizer` for final local-link normalization and validation.

Classify files as evidence sources, destination notes, or read-only context notes. Evidence sources may be deleted afterward and must never be cited or linked. Durable repository-note links are allowed when they clarify a relationship and resolve after evidence deletion.

## Disposable work layout

Put all internal state under:

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

Record:

- `publication_mode`;
- selected evidence scope;
- repository root when applicable;
- final path or destination repository;
- audience, purpose, output format, assumed knowledge, and terminology constraints;
- work directory and cleanup preference.

Use `repository_integrated` when the request asks the result to participate in an existing note repository. Otherwise use `standalone`.

Exclude the work directory and intended durable outputs from evidence inventory.

### 1. Inventory and initialize

Run `inventory_markdown.py` on evidence only. Stop if complete inventory is impossible.

Initialize lifecycle files with:

```json
{
  "execution_mode": "subagents_required",
  "fallback_used": false,
  "maximum_concurrent_subagents": 3,
  "publication_mode": "standalone or repository_integrated"
}
```

Use a lower concurrency cap when required.

### 2. Locate companion skills — repository mode only

Run `locate_companion_skills.py`. Stop if either required companion is unavailable.

Record the located `SKILL.md` and link-normalizer script paths in `companion-skills.json`.

### 3. Produce, review, and validate placement — repository mode only

1. Spawn one `note-home-finder-adapter` attempt covering all evidence sources.
2. Inject the located companion `note-home-finder/SKILL.md` unchanged.
3. Reconcile the producer.
4. Spawn and reconcile an independent stage review.
5. Run `validate_placement.py`.
6. Advance only when review and validation pass.

Then run `snapshot_repository_context.py` to snapshot all existing destinations and context notes.

### 4. Produce and review the outline

Spawn one `outline-planner` covering all evidence sources. In repository mode, also provide the accepted placement plan and repository context snapshots. Reconcile, review independently, validate the Outline contract, and advance only on success.

### 5. Produce, review, and validate extraction

1. Partition evidence sources with `schedule_batches.py`.
2. Spawn bounded, disjoint `source-analyst` waves.
3. Reconcile and retry failed logical tasks.
4. Review every accepted extraction attempt exactly once using independent stage reviewers.
5. Run `validate_units.py`.

Do not advance until source assignment, line coverage, review coverage, and unit validation pass.

### 6. Produce, review, and validate topic organization

Spawn one full-unit `topic-organizer`, reconcile it, review it independently, and run `validate_topics.py`.

### 7. Produce, review, and validate comparisons

Partition topic IDs into disjoint batches, spawn `topic-comparator` attempts, reconcile, review each accepted attempt exactly once, and run `validate_comparisons.py`.

### 8. Produce, review, and validate conflict decisions

Use `comparisons/index.json.required_resolution_ids` as exact scope.

- When non-empty: spawn bounded `conflict-resolver` attempts, reconcile, independently review, then run `validate_decisions.py`.
- When empty: create one skipped conflict-resolution logical task with an explicit reason and no attempt or review.

### 9. Produce, review, and validate integration plan — repository mode only

1. Spawn one full-unit `integration-planner` with the placement plan, snapshots, context notes, topics, comparisons, and decisions.
2. Reconcile it.
3. Spawn and reconcile an independent stage review.
4. Run `validate_integration_plan.py`.
5. Advance only when every source unit has one primary destination and the destination/link plan passes.

### 10. Produce and review the full publication

Create the single logical task `publication`.

- Standalone mode: spawn one full-scope `synthesizer`, then run `materialize_publication.py`.
- Repository mode: spawn one full-scope, full-destination `synthesizer`, then run `materialize_publication_set.py` into the disposable candidate root.

Reconcile the publication attempt. Spawn an independent publication-stage review with the annotated output, clean candidates, dispositions, coverage map, outline, decisions, writing policy, and repository snapshots/plan when applicable. Require the review to pass.

The writer uses temporary `MC` evidence markers. Never hand-maintain evidence excerpts.

### 11. Validate lifecycle and stage-review coverage

Run:

```bash
python <skill-dir>/scripts/validate_task_lifecycle.py \
  --work-dir <work-dir> \
  --require-terminal \
  --report <work-dir>/task-lifecycle-report.json

python <skill-dir>/scripts/validate_reviews.py \
  --work-dir <work-dir> \
  --report <work-dir>/review-validation-report.json
```

Do not spawn final validators until both pass.

### 12. Run final semantic and deterministic validation

Spawn at least two `validator` tasks with disjoint category scopes.

All modes require exact coverage of:

- `coverage`
- `conflicts_qualifiers`
- `standalone_exposition`
- `coherence_markdown`
- `writing_quality`

Repository mode additionally requires:

- `repository_integration`
- `link_context`

Reconcile validators.

Standalone mode runs `validate_consolidation.py` and `validate_writing.py`.

Repository mode:

1. run `validate_writing.py` for every candidate note;
2. run `run_link_pipeline.py` using the installed `markdown-link-normalizer` skill;
3. run `validate_repository_integration.py` against normalized candidates;
4. treat new or evidence-deletion-exposed broken links as errors and unchanged pre-existing failures as warnings.

Every writing warning must be accepted or repaired by a semantic validator.

### 13. Repair

Run at most three repair cycles:

1. group accepted findings into bounded scopes;
2. spawn `patch-analyst` tasks;
3. spawn a full-scope `publication-finalizer` attempt under `publication`;
4. reconcile and materialize the complete revision;
5. independently review the new accepted publication attempt;
6. re-run lifecycle, review, semantic, content, writing, repository, link, and delegation validation applicable to the mode.

A patch analyst never owns publication output. A finalizer owns every unit and every destination.

### 14. Run final delegation validation

Run `validate_delegation.py`. It must validate accepted producer assignments, required repository stages, review coverage, complete publication ownership, final validator coverage, receipt hashes, outputs, and terminal lifecycle state.

### 15. Publish

Publish only when every required semantic review and deterministic report passes.

- Standalone: copy the accepted clean candidate to the requested final path.
- Repository mode: copy only normalized candidates from `normalized-candidates/` to their reviewed destination paths. Create parent directories as needed. Do not modify context notes.

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
- repository mode has one reviewed placement plan and one reviewed integration plan;
- repository units have exactly one primary destination;
- context notes remain read-only;
- existing destination headings are preserved unless approved;
- no final link targets disposable evidence;
- no new broken local path or anchor remains after normalization.

## Final response

Report durable publication paths, mode, review/content/writing/lifecycle/delegation status, repository/link status when applicable, source and unit counts, destination count, accepted/superseded/failed attempt counts, unresolved-conflict count, and work-directory cleanup status. Do not dump internal artifacts or private reasoning.
