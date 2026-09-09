---
name: note-authoring
description: Add already-understood knowledge, rewrite existing prose, or repair an explanation in this repository when the user explicitly requests a repository change. Use when the content itself is known and the main job is to place, scope, and orchestrate the change coherently. Do not use for conceptual questions, raw source ingestion, learning scaffolds, read-only review, or cross-note structural cleanup.
---

# Note Authoring

This workflow owns **known knowledge → durable explanatory prose orchestration** after mutation intent is established. It does not itself own substantive prose mutation; `$note-writer` does.

## Mutation prerequisite

Do not enter this workflow merely because a conceptual question reveals ambiguous, incomplete, or incorrect documentation. The user must explicitly request that repository content be added, rewritten, repaired, applied, updated, or otherwise changed.

Prior edits in the conversation do not authorize mutation for a later conceptual question. If mutation intent is absent, return to routing and use a read-only workflow such as `$note-question`.

## Capability boundary

`$note-authoring` may gather evidence, make or delegate semantic decisions, prepare writer inputs, and validate results. It must not draft, rewrite, or directly apply substantive durable prose itself.

Any substantive prose mutation must be delegated to `$note-writer`, including:

- adding explanatory prose;
- rewriting an existing section;
- repairing a confusing or incomplete explanation;
- adapting existing prose to repository writing style while preserving its technical meaning;
- restructuring paragraphs, bullets, or nearby prose for explanatory clarity.

Trivial mechanical corrections with obvious target and scope should bypass this composite workflow at routing time rather than becoming an exception inside authoring.

## Progressive gates

### Retrieval gate

For every substantial addition, new section, or new note, invoke `$note-topic-search` before placement or writing, even when the user supplied an explicit target. Repository retrieval is a required invariant for substantial edits because it establishes existing coverage, semantic neighbors, and possible same-level duplication.

Only narrow local corrections whose target and scope are already obvious may skip repository retrieval.

### Placement gate

If the target note/section is explicit and the retrieval results confirm that the new material belongs to its established subject without conflicting canonical ownership, skip `$note-home-finder`.

If ownership is unclear, contradicted by retrieval, compound, or likely to create/split notes, invoke `$note-home-finder` and pass the confirmed `$note-topic-search` results so it does not repeat retrieval unnecessarily.

### Boundary gate

Invoke `$note-boundary-analyzer` only when the proposed material can cross subjects or abstraction levels, contains implementation/application detail, or may duplicate another canonical explanation. Skip it for a narrow addition with an obvious local scope.

### Structural gate

Invoke `$note-content-mover` only when an accepted boundary plan says existing durable material must move, merge, split, or be removed as duplication.

### Required writing gate

If durable note prose will be created or substantively changed, invoke `$note-writer` before mutation. Supply the accepted destination, abstraction level, relevant source/local context, boundary decisions when needed, and any approved semantic link plan.

Do not directly draft or rewrite the note inside `$note-authoring`. The writer must not reopen placement, boundary, or link-selection decisions supplied by this workflow.

### Link gate

Invoke `$note-link-planner` when a substantial edit introduces concepts that naturally benefit from existing repository context or when the user asks for links. The planner exclusively owns semantic link selection.

Pass any approved link plan to `$note-writer` only for application/preservation in the prose. Invoke `$markdown-link-normalizer` only when links or anchors changed.

### Review gate

For edits that change note scope, headings, multiple conceptual units, or abstraction boundaries, invoke `$note-cohesion-reviewer` before finalizing. For a narrow local clarification or style-focused rewrite, the writer's own verification is sufficient unless the rewrite changes semantic structure.

Invoke `$markdownlint-fix` only when lint findings are introduced or exposed.

## Question-driven amendment after mutation intent

When the user asks a conceptual question about an existing note **and explicitly requests that the identified documentation defect be fixed**, treat the question as an amendment specification. Determine the missing definition, distinction, state transition, assumption, or causal link where the ambiguity first appears, then delegate the prose repair to `$note-writer` rather than appending an FAQ.

A conceptual question, inspection result, or discovery of ambiguity is not itself sufficient authorization to edit.

## Acceptance criteria

Explicit mutation intent was established before any durable edit; if durable prose was substantively created or changed, `$note-writer` was invoked before mutation; required repository retrieval was performed for substantial additions; only the semantic capabilities needed after that evidence were disclosed; the edited note remains centered, locally sufficient, non-duplicative, and at the intended abstraction level; examples remain subordinate; and any changed links/Markdown validate.
