---
name: note-review
description: Review existing notes and report improvement opportunities without applying edits. Use when the user asks to assess, critique, audit, or identify gaps, duplication, boundary problems, writing problems, or link opportunities before deciding what to change.
---

# Note Review

This workflow is **read-only**. Mutation capabilities remain undisclosed unless the user later asks to apply findings.

## Gates

1. Read the explicitly requested note(s).
2. Invoke `$note-cohesion-reviewer` for local structural and conceptual review.
3. If a finding depends on whether another note already owns the concept, invoke `$note-topic-search` only for that concept and re-evaluate the finding.
4. If the user specifically asks about boundaries between known notes, invoke `$note-boundary-analyzer` with those notes' established subjects; do not invoke repository-wide placement unless ownership itself is uncertain.
5. If the user asks for link opportunities, invoke `$note-link-planner`; otherwise do not load link-planning instructions.

## Output

Return prioritized opportunities grouped by substantive impact, not by skill or tool. Distinguish:

- confirmed defects;
- architectural opportunities;
- optional refinements;
- questions that require additional evidence.

Do not edit files or silently transition into `$note-authoring` or `$note-refactor`.