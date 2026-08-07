# Independent stage-review protocol

Every semantic producer output is reviewed by a separate subagent before downstream use.

## Required producer phases

Always review accepted attempts for:

1. `outline`
2. `extraction`
3. `topic_organization`
4. `comparison`
5. `conflict_resolution` when not skipped
6. `synthesis` for the currently accepted publication

Repository-integrated mode also requires reviews for:

1. `placement`
2. `integration_planning`

Final semantic validators are a separate publication-level gate and do not replace stage reviews.

## Independence rules

- The reviewer role is `stage-reviewer`, never the producer role.
- Review task and attempt IDs differ from every reviewed producer.
- When runtime thread IDs exist, reviewer and producer threads differ.
- The reviewer is read-only and never edits producer artifacts.
- Each accepted producer attempt is reviewed exactly once in the current accepted workflow.
- A replacement producer attempt invalidates the previous review.

## Review task specification

```json
{
  "phase": "stage_review",
  "role": "stage-reviewer",
  "assigned_scope": {
    "reviewed_attempt_ids": ["accepted-producer-attempt"],
    "review_categories": ["stage-specific-category"]
  }
}
```

List reviewed producer attempt IDs in `input_attempt_ids`.

## Review result

The report includes exact reviewed attempt IDs, pass/fail status, operational findings, evidence, violated contract, practical effect, severity, repair owner, warnings, and receipt.

`status: "passed"` is valid only when no blocking defect remains.

## Stage focus

- **Placement:** repository search performed; reuse/extend/create/split decision supported; destination paths durable; evidence files excluded; context notes identified; no files modified.
- **Outline:** complete order and destination-aware structure; audience and purpose fit; no source-file organization.
- **Extraction:** full line coverage, semantic fidelity, intact qualifiers, complete examples, correct unit boundaries.
- **Topic organization:** every unit assigned once, no unsupported terminology merge, no omissions.
- **Comparison:** every assigned unit accounted for, correct relationship, complete semantic union.
- **Conflict resolution:** required records resolved, scopes preserved, no invented qualifiers or discarded positions.
- **Integration planning:** every unit has one primary destination; existing-note boundaries and headings are protected; context notes remain read-only; links are useful and do not replace coverage.
- **Publication:** full dispositions, standalone exposition, correct decisions, complete examples, writing-policy compliance, destination-note preservation, and planned link relationships.

## Failure handling

A failed review blocks the stage. Route findings to the producer role, create a new attempt under the same logical task, reconcile it, and review the new accepted attempt. The main agent and reviewer never patch producer artifacts.
