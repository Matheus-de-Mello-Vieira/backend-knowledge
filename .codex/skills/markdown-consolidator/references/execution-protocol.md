# Execution protocol

This is the canonical orchestration protocol. `SKILL.md` defines stage order. This file defines how each semantic stage runs.

## Common subagent boundary

Inject this instruction into every delegated prompt:

> You are already the delegated subagent. Perform the assigned task directly. Do not spawn, delegate to, or request another agent. Write only the declared outputs and receipt, then return control to the orchestrator.

Nested spawning is a task failure.

## Stage cycle

Execute each semantic stage in this order:

1. **Specify** — create or update one logical task and write one immutable task specification.
2. **Produce** — spawn the assigned producer within the concurrency cap.
3. **Reconcile producer** — accept one valid attempt; supersede or fail the others.
4. **Review** — spawn an independent `stage-reviewer` for the accepted producer attempt or accepted producer batch.
5. **Reconcile review** — accept one valid review attempt for each review task.
6. **Validate** — run the stage's deterministic validator when available.
7. **Advance or retry** — advance only when review and deterministic validation pass. Otherwise retry the producer under the same logical task.

Do not start downstream semantic work before the current stage cycle passes.

## Task and attempt rules

- One semantic responsibility is one logical task.
- A retry is a new immutable attempt under the same task.
- Each non-skipped logical task has exactly one accepted attempt.
- Earlier valid attempts become `superseded`; receipts remain immutable.
- The task specification is the only source of assigned scope.
- A receipt proves the task-spec hash and completed scope; it cannot redefine assigned scope.
- Downstream attempts list only accepted upstream producer and review attempt IDs.
- No attempt may remain active or unreconciled when publication begins.

## Attempt procedure

For each attempt, the orchestrator:

1. creates the logical task when absent;
2. writes `task-specs/<attempt-id>.json` before spawning;
3. records the attempt as `queued` or `running`;
4. injects the role reference, immutable task specification, applicable contracts and protocols, output paths, receipt path, and common subagent boundary;
5. instructs the runtime: **Spawn this task as a subagent now. Do not perform it in the main thread.**;
6. waits for every declared output and receipt;
7. marks the attempt `completed` or `failed`;
8. reconciles before creating dependent work.

Create reviewer and validator attempts only immediately before spawning them. Do not create placeholders.

## Capacity and batching

- Default to at most three concurrent semantic subagents or a lower known runtime limit.
- Record the cap and batch decisions in `runtime-plan.json`.
- Queue excess work and execute bounded waves.
- Use disjoint source, topic, conflict, review, and validation batches.
- Treat capacity failure as retryable, not proof that subagents are unavailable.

Recommended batching:

- large source: one source per analyst;
- many small sources: two or three sources per analyst;
- comparisons and conflicts: disjoint topic or record batches;
- stage reviews: disjoint batches covering accepted producer attempts exactly once;
- final semantic validation: at least two validators with disjoint category sets.

## Retry and supersession

- Increment `attempt_number` and set `replaces_attempt_id`.
- Preserve failed and superseded attempts and receipts.
- Reconcile after every retry wave.
- A new accepted producer invalidates reviews of the superseded attempt and requires a new review.

## Publication lineage

The complete publication or publication set is one logical task named `publication`.

1. The first full-scope attempt uses `synthesizer`.
2. Local defects may be analyzed by `patch-analyst` tasks.
3. A repaired revision uses `publication-finalizer` under the same task.
4. Every accepted publication attempt claims the complete unit set and, in repository mode, the complete destination set.
5. Materialize evidence after each accepted revision; never hand-edit the coverage map.
6. Review every newly accepted publication attempt independently.
7. Re-run semantic and deterministic validation after each reviewed revision.

## Companion-skill boundary

In repository-integrated mode:

- the placement producer receives the actual installed `note-home-finder/SKILL.md`;
- the main agent invokes the actual installed `markdown-link-normalizer` scripts only through `run_link_pipeline.py`;
- neither companion's behavior is reimplemented in subagent prompts;
- companion discovery and paths are recorded in `companion-skills.json`.
