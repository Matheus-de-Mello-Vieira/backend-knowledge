# Mandatory delegation policy

## Purpose

Keep the main Codex thread limited to orchestration. All semantic work must be performed by spawned subagents with bounded scopes and machine-readable outputs.

## Required execution mode

Set `execution_mode` to `subagents_required` and `fallback_used` to `false` in `<work-dir>/delegation-log.json`.

The main agent must explicitly spawn subagents. Phrases such as `consider using an agent`, `delegate if useful`, or `you may parallelize` do not satisfy this policy.

If the runtime cannot spawn subagents, stop. Do not complete semantic work in the main thread.

## Main-agent boundary

The main agent may:

- resolve paths and user constraints;
- run deterministic scripts;
- read inventory metadata, role files, contracts, policies, receipts, counts, and findings;
- create task records before spawning;
- spawn, wait for, retry, and cancel tasks;
- check schema shape and exact assignment coverage;
- copy an accepted draft to the final path.

The main agent may not:

- semantically read or consolidate source bodies;
- author the outline, topic map, comparison records, decisions, draft, coverage map, or semantic validation reports;
- repair publication prose;
- fabricate receipts, outputs, thread identifiers, or completed task states.

## Required phases

1. `outline`: one outline-planner task covering all inventory sources.
2. `extraction`: one or more source-analyst tasks whose assigned source-ID union equals the inventory source set exactly.
3. `topic_organization`: one topic-organizer task covering every extracted unit.
4. `comparison`: one or more topic-comparator tasks whose assigned topic-ID union equals the topic set exactly.
5. `conflict_resolution`: one or more conflict-resolver tasks covering every conflict, conditional-compatibility, and historical-status record. The phase may be explicitly skipped only when required scope is empty.
6. `synthesis`: exactly one synthesizer task per draft revision. Exactly one revision may be marked accepted.
7. `semantic_validation`: at least two validator tasks with disjoint validation-category assignments. Their category union must cover every required validation category.

## Spawn protocol

For every task:

1. Add a `planned` task entry to `delegation-log.json` before spawning.
2. Include one role, one bounded scope, exact inputs, exact outputs, and a task ID.
3. Inject the complete role instructions and applicable contract.
4. State `Spawn this task as a subagent now. Do not perform it in the main thread.`
5. Require a receipt at `<work-dir>/receipts/<task-id>.json`.
6. Start independent tasks in parallel.
7. Wait for every task in the current phase before starting a dependent phase.
8. Mark a task completed only after its receipt and declared outputs exist.
9. Retry once for malformed or incomplete output. Record both attempts.
10. Stop after a second failure; do not take over the role in the main thread.

## Task receipts

A receipt must be written by the delegated subagent that performed the task. It records:

- task ID, role, and phase;
- assigned source IDs, topic IDs, comparison IDs, decision IDs, unit IDs, or validation categories;
- exact output paths;
- completion status and counts;
- warnings;
- `producer: "subagent"`.

Receipts are operational evidence, not publication content. Store them only under the disposable work directory.

## Parallelism

Parallelize independent, read-heavy work:

- source analysis by source or disjoint batch;
- topic comparison by disjoint topic sets;
- conflict resolution by independent conflict sets;
- semantic validation by disjoint categories.

Keep dependent phases sequential. Use exactly one synthesizer at a time to avoid conflicting publication edits.

## Verification

Run `scripts/validate_delegation.py` before publication. A run fails when required phases, task receipts, assignment coverage, role counts, output files, or validation categories are missing.
