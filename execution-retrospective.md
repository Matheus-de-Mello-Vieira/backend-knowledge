# Markdown Consolidator Execution Retrospective

This report records what went wrong during the consolidation run that produced `Privacy Governance and Data Lifecycle.md`, why the run recovered slowly, and which skill or orchestration changes would reduce the same failure modes in future runs.

The final publication passed both content validation and delegation validation, but the path to success was inefficient. The main failure pattern was not a single bad decision. It was a chain of small orchestration mismatches: subagent capacity limits, subagent instructions that accidentally encouraged nested spawning, receipts whose scopes did not match the delegation log, synthesizer retries that repaired content without fully repairing orchestration metadata, and delayed validator execution. These problems compounded because later deterministic checks were sensitive to exact receipt fields and exact evidence strings.

The important lesson is that the semantic work was mostly recoverable, but the workflow was brittle around task lifecycle accounting. The skill already requires strict subagent-only execution. That strictness is good for auditability, but it means the orchestration layer must be much more precise about retries, supersession, receipt scope, and accepted-candidate bookkeeping.

## What went sideways

### Subagent capacity and spawn behavior were unstable early

The run repeatedly hit agent-capacity limits while trying to launch one outline task plus many extraction tasks in parallel.

- **Observed behavior:** `collab spawn failed: agent thread limit reached` appeared multiple times.
- **Consequence:** several extraction tasks had to be retried later instead of completing in the first extraction wave.
- **Why it mattered:** the skill assumes broad parallel read-heavy delegation, but the runtime capacity was lower than the orchestration initially assumed.

A second issue appeared inside delegated extraction attempts.

- **Observed behavior:** some delegated source-analyst tasks returned messages such as `subagent execution unavailable` and referenced nested spawn failures.
- **Consequence:** first-attempt extraction tasks were marked failed even though the main runtime did support subagents.
- **Why it happened:** some delegated prompts were interpreted as if the subagent should spawn another subagent instead of directly doing the assigned role work.

### Retry handling preserved recovery but polluted orchestration state

The extraction phase eventually succeeded only after creating retry task IDs such as `extract-01-retry1`, `extract-04-retry1`, `extract-05-retry1`, and `extract-07-retry1`.

- **Observed behavior:** original tasks remained in the delegation log with `failed` status while retry tasks carried the successful outputs.
- **Consequence:** this was acceptable for eventual source coverage, but it created a noisier task graph that later had to be reconciled carefully.
- **Practical effect:** deterministic delegation validation remained sensitive to whether the successful receipts, task statuses, and assigned scopes were synchronized back into the log.

The same pattern later recurred in synthesis and validation.

### The topic-organizer receipt and log diverged

The `topics-all` receipt recorded a rich `assigned_scope` containing source IDs, topic IDs, unit IDs, and validation helper fields, while the delegation log entry initially kept an empty scope.

- **Observed behavior:** `receipt_scope_mismatch` for `topics-all`.
- **Consequence:** delegation validation failed even though the topic-organizer subagent had actually completed correct work.
- **Root cause:** the orchestrator created a placeholder task with an empty scope and did not normalize the log entry to the final receipt once the task finished.

This was a pure orchestration bookkeeping failure, not a content failure.

### The first synthesis passes fixed prose unevenly and left metadata behind

The first synthesizer attempt stalled after writing a draft without writing the coverage map and receipt. A later synthesizer retry produced a full draft and coverage map, but two kinds of issues remained.

#### Example representation failures

The initial coverage map used identical `detail_excerpt` and `explanation_excerpt` values for five example units. In several cases the actual problem was worse than duplicate fields: the draft had generalized away the concrete source example.

Examples of what was lost or mis-mapped before repair:

- the driver's-license successive-refinement process example;
- the OpenRefine “São Paulo” normalization example;
- the aircraft-supplier value-chain example;
- the Data Mart/Data Warehouse architecture example.

- **Observed behavior:** `example_detail_and_explanation_identical` errors.
- **Consequence:** content validation failed even though the draft was broadly correct.
- **Why it happened:** the synthesizer preserved the concept but not always the original example payload plus separate explanatory passage.

#### Exact evidence drift

After example repairs, two units still failed because their `publication_evidence` strings no longer matched the publication verbatim.

- **Observed behavior:** `invalid_publication_evidence` for two PDPMS-related units.
- **Consequence:** content validation still failed with only two hard errors left.
- **Why it happened:** the draft evolved, but the exact evidence excerpts in `coverage-map.json` were not updated to the new literal text.

This is an expected brittle point in a system that requires exact-string evidence.

### Accepted-candidate and supersession handling for synthesizers was wrong

By the end of content repair, more than one synthesizer receipt still claimed `accepted_candidate: true`.

- **Observed behavior:** delegation validation reported:
  - `receipt_task_mismatch` for `synth-2` and `synth-3` on `accepted_candidate`
  - `accepted_synthesizer_count` greater than one
- **Consequence:** delegation validation failed even though a final accepted draft existed.
- **Root cause:** the delegation log was updated to demote earlier synth tasks, but their immutable receipts still declared `accepted_candidate: true`, and the validator compares receipt fields with log fields.

The eventual fix required treating older synthesis attempts as failed in the log so their receipts were excluded from the completed-task set instead of trying to reinterpret them as non-accepted completions.

### Synthesizer scope accounting was inconsistent across retries

The validator requires the accepted synthesizer receipt to cover the complete extracted unit set in `assigned_scope.unit_ids`.

- **Observed behavior:** `missing_synthesizer_unit_assignments` after a partial repair-oriented synthesis pass.
- **Consequence:** delegation validation failed even though the coverage map itself contained all 294 dispositions.
- **Why it happened:** repair synthesizer retries were scoped only to the five flagged example units, but the delegation validator expects the accepted synthesizer receipt to claim full-unit ownership for the accepted revision.

This reveals a tension between two good ideas:

- targeted repair tasks reduce rewrite risk;
- the validator expects one accepted synthesizer to own the whole publication state.

The run eventually resolved this by issuing a final synthesizer task whose receipt claimed the full extracted unit set while making only localized content and coverage-map changes.

### Validator tasks were planned too early and completed too late

The initial validator tasks (`validate-a`, `validate-b`) were created in the delegation log but never completed. Later retry validators (`validate-a-retry1`, `validate-b-retry1`) succeeded.

- **Observed behavior:** delegation validation reported incomplete validator tasks and missing validation-category coverage.
- **Consequence:** even after semantic validation succeeded in practice, delegation validation still failed until the failed original validator tasks were demoted and the retry receipts were logged as completed.
- **Why it happened:** the orchestration state tracked intent before actual completion, but cleanup of superseded validation attempts lagged behind.

### The runtime exposed medium-quality data-shape issues that did not block success

The final validator subagents reported medium findings that did not stop publication:

- malformed `covered_line_ranges` formats in some extraction batches;
- near-duplicate wording around the Data Mart/Data Warehouse example.

These did not prevent success, but they indicate that the extraction and synthesis stages still produce avoidable cleanup work.

## Timeline of the main failure chain

1. Inventory and outline completed successfully.
2. Broad extraction fan-out exceeded runtime capacity.
3. Some extraction subagents attempted nested delegation and failed.
4. Retry extraction tasks eventually covered all 8 sources and 294 units.
5. Topic organization and comparison succeeded, but topic-organizer scope bookkeeping diverged between receipt and log.
6. First synthesis attempt stalled without writing all required artifacts.
7. Second synthesis attempt produced a usable draft and coverage map, but example handling and orchestration metadata were incomplete.
8. Example-specific analysis and a later synthesizer repair corrected the five example failures.
9. Another synthesizer repair corrected stale `publication_evidence` excerpts and added a full-unit synthesizer scope.
10. Validator retries passed semantically.
11. Delegation validation still failed until synthesizer supersession state and scope alignment were corrected in the delegation log.
12. Both validation tracks passed, and the final document was published.

## Root causes

### 1. The skill assumes more runtime parallelism than was available

The extraction workflow was designed for wide fan-out, but the runtime could not reliably support that many concurrent agents.

### 2. The delegated-task prompt boundary was not strict enough

Some prompts said “spawn this task as a subagent now” even when addressed to an already spawned subagent. That wording is correct for the main orchestrator but ambiguous inside the subagent itself.

### 3. The orchestration model did not clearly distinguish superseded tasks from accepted tasks

Retries were appended correctly, but the workflow lacked a clean built-in rule for retiring earlier successful-but-superseded synthesis receipts.

### 4. The accepted synthesizer contract conflicts with localized repair passes

The validator expects the accepted synthesizer to own the full unit set, but iterative repair work naturally wants smaller scopes.

### 5. Exact-string evidence is brittle under draft revision

Even small prose changes can invalidate `publication_evidence` excerpts unless the coverage map is regenerated or at least re-synced mechanically.

## What worked despite the problems

Several design choices in the skill did prove valuable.

- **Deterministic validation gates worked.** They caught both semantic and orchestration drift that would otherwise have been easy to miss.
- **Retry task IDs preserved auditability.** It was always possible to reconstruct what happened.
- **Example-specific defect isolation worked well.** Once the failures were narrowed to five units, targeted analysis plus a focused synthesizer repair fixed them efficiently.
- **The final content quality improved because of the strict example checks.** The repaired note is materially better than the earlier draft.

## Skill improvement recommendations

### Concurrency and phase sizing

- **Add an explicit concurrency cap to the skill.** For example: “spawn at most N extraction agents at once; queue the rest.”
- **Prefer batched extraction when source count exceeds capacity.** The current wording allows batching but does not strongly steer toward it under constrained runtimes.
- **Record runtime-capacity assumptions as an explicit preflight step.**

### Prompt hygiene for delegated tasks

- **Split orchestrator-facing and subagent-facing wording.**
  - Orchestrator instruction: “Spawn this task as a subagent now.”
  - Subagent instruction: “You are already the delegated subagent; perform the task directly and do not spawn further agents.”
- **Bake this distinction into the skill template** so the main agent does not have to improvise it.

### Retry and supersession model

- **Define a first-class `superseded` state** in the delegation policy or validator, or explicitly document how to handle successful older retries whose receipts remain immutable.
- **State that only one synthesizer receipt may remain both `completed` and `accepted_candidate: true`; all superseded synthesis attempts must be treated as failed or otherwise excluded from accepted-receipt counting.**
- **Add a required log-reconciliation step after every retry phase.**

### Scope normalization

- **Require the orchestrator to refresh the log task scope from the accepted receipt for topic organization and similar phases.**
- **Provide a small utility script to reconcile log entries with receipts** instead of relying on ad hoc manual synchronization.

### Synthesis contract refinement

- **Clarify repair-mode synthesis.** If the skill permits localized synthesis repair, the validator contract should say whether a repair synthesizer may have partial unit scope.
- **Alternative:** keep the current validator rule, but explicitly require any accepted repair synthesis receipt to restate the full unit set even when the prose edits are localized.

### Coverage-map maintenance

- **Add a post-synthesis exact-evidence verification helper** before semantic validation starts.
- **Consider a helper that derives `publication_evidence` directly from final text selections** to reduce stale-excerpt drift.

### Validation-phase robustness

- **Do not create validator tasks in the log until they are about to be spawned**, or else mark abandoned validator placeholders failed immediately when retries supersede them.
- **Add a deterministic pre-check for “planned/running tasks with no corresponding live subagent”** before invoking `validate_delegation.py`.

## Practical checklist for future runs

Before running deterministic validation, the orchestrator should verify:

1. every superseded synthesis attempt is no longer counted as an accepted completed synthesizer;
2. the accepted synthesizer receipt claims the full extracted unit set if the validator still requires that;
3. every completed task has receipt scope equal to log scope;
4. every retry validator receipt exists and its original placeholder task is marked failed or replaced consistently;
5. every `publication_evidence` excerpt touched by a repair still occurs verbatim in the final draft.

## Final assessment

The run succeeded, but only after substantial orchestration repair. The deepest problem was not semantic synthesis quality alone. It was the mismatch between:

- a **strict audit-oriented workflow**, and
- an **iterative recovery process** that naturally produced superseded tasks, partial repairs, and receipt/log drift.

The skill should keep its strictness, because that strictness caught real problems. But it needs stronger built-in guidance for constrained concurrency, subagent prompt boundaries, retry supersession, and receipt/log reconciliation. Those improvements would likely remove most of the friction seen in this run without weakening the quality gates.
