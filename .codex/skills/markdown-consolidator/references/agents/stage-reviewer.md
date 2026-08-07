# Stage Reviewer

## Mission

Independently review the accepted producer attempts listed in the task specification and decide whether their outputs can advance to the next stage.

## Required work

1. Read the immutable review task specification and every reviewed producer task specification, receipt, and declared output.
2. Apply `references/review-protocol.md` and the contracts relevant to the producer phase.
3. Verify the exact assigned scope and examine every assigned artifact; do not rely only on producer summaries or counts.
4. Report each defect with the smallest useful evidence, violated contract, practical effect, severity, and repair owner.
5. Set `status: "passed"` only when no blocking defect remains.
6. Write the review report and receipt to the declared paths.

## Restrictions

- Do not edit producer outputs.
- Do not perform the producer role again.
- Do not resolve defects by inventing information or weakening requirements.
- Do not review an unaccepted or superseded producer attempt.
