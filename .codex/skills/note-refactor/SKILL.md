---
name: note-refactor
description: Refactor overlapping or misplaced knowledge across Markdown notes without leaving duplication or broken conceptual boundaries. This is the canonical cross-note refactoring workflow and delegates placement, boundary analysis, structural mutation, prose repair, and link validation to lower-level skills.
---

# Note Refactor

Use this workflow for cross-note cleanup: moving misplaced content, merging same-level duplication, splitting mixed subjects, repairing abstraction leakage, or reorganizing notes after ownership changes.

## Capability ownership

Owns:

- sequencing a multi-note refactor;
- carrying approved semantic decisions through structural mutation, prose repair, and validation;
- verifying repository cohesion after the refactor.

Delegates:

1. `$note-home-finder` — canonical homes and split decisions.
2. `$note-boundary-analyzer` — how much each note should own.
3. `$note-content-mover` — approved cross-note move, merge, split, and duplicate removal.
4. `$note-writer` — substantive prose repair after structure changes.
5. `$markdown-link-normalizer` — mechanical path and anchor normalization/validation.
6. `$markdownlint-fix` — introduced Markdown lint findings when applicable.

Must not:

- reproduce repository-search procedures;
- invent its own placement or boundary policy;
- move content before semantic ownership is approved;
- maintain a separate prose style or link-normalization implementation.

## Workflow

1. **Resolve ownership**
   - Read directly affected notes.
   - Delegate canonical-home decisions to `$note-home-finder`.

2. **Resolve boundaries**
   - Delegate overlapping or misplaced material to `$note-boundary-analyzer`.
   - Require a disposition for every substantial unit.

3. **Apply structural changes**
   - Pass the approved plan to `$note-content-mover`.
   - The mover executes; it does not reinterpret the plan.

4. **Repair exposition**
   - Use `$note-writer` when moved or removed context requires substantive rewriting.
   - Keep residual context sufficient but non-duplicative.

5. **Repair links and Markdown**
   - Use `$markdown-link-normalizer` for broad path/anchor changes.
   - Use `$markdownlint-fix` for introduced lint findings when appropriate.

6. **Verify repository cohesion**
   - Confirm every affected note retains one center of gravity.
   - Confirm the canonical explanation exists in the intended destination and abstraction level.
   - Confirm examples and implementation details stay within their assigned boundaries.
   - Confirm no accidental same-level duplicate body remains.
   - Confirm source and destination notes both read naturally.

## Constraints

- Do not create a new note unless `$note-home-finder` or the user's explicit instruction establishes that outcome.
- Do not preserve duplicate full explanations merely because readers might search both locations.
- Do not rewrite unrelated sections during a boundary cleanup.
- Do not add navigation-only prose to compensate for weak placement.
