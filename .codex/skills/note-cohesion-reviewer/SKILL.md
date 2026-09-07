---
name: note-cohesion-reviewer
description: Review one or more durable notes for repository cohesion without editing them. Diagnose center-of-gravity drift, abstraction leakage, same-level duplication, weak local context, oversized examples, explanation/format mismatches, and cross-note relationship problems.
---

# Note Cohesion Reviewer

This is the canonical **read-only semantic review** capability for repository notes.

## Inputs

- target note(s);
- repository invariants from `AGENTS.md`;
- neighboring notes when the caller has retrieved them;
- optional accepted placement/boundary plans for post-edit verification.

## Review dimensions

- **Center of gravity:** Does the note still explain one stable subject for one primary reading intent?
- **Abstraction:** Does theory/mechanism/implementation/application material stay within appropriate boundaries?
- **Canonical ownership:** Is the same concept fully explained elsewhere at the same sense and level?
- **Local sufficiency:** Does the note contain enough neighboring context for its own argument without becoming independently exhaustive?
- **Examples:** Do concrete systems illuminate the concept and stop before becoming implementation documentation?
- **Explanation:** Are causal relationships and important state changes explicit rather than merely listed?
- **Structure:** Does prose/bullets/steps/tables/callouts match the logical shape of the knowledge?
- **Links:** Are conceptual relationships natural, useful, and non-decorative?

## Output contract

Return prioritized findings. Each finding should include:

- `severity`: blocking, important, or optional;
- `location`;
- `principle`;
- `problem`;
- `recommended_action`;
- `related_note` when repository context matters.

Separate confirmed findings from hypotheses that require broader repository search.

## Constraints

Do not edit files. Do not invent missing technical content. Do not recommend broad rewrites when a smaller structural correction would resolve the problem.