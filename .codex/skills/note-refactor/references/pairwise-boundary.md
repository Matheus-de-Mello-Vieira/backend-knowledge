# Pairwise Boundary Refactor

Load this reference only when two known notes are being separated or deduplicated and their intended centers of gravity are already explicit.

Do not perform repository-wide placement search by default.

1. State each note's center of gravity in one sentence.
2. Enumerate only the overlapping concepts between the two notes.
3. Give each concept one canonical owner at the relevant sense and abstraction level.
4. Decide the minimum residual local context needed by the non-owner.
5. Mark implementation/application examples that should remain bounded versus move completely.
6. Produce a move/merge/delete/link plan for `$note-content-mover`.

Escalate to `$note-home-finder` only if analysis reveals that a third note is the natural canonical home or the stated boundary is internally inconsistent.