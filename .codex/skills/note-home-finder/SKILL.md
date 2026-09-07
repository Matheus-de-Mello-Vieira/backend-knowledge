---
name: note-home-finder
description: Decide the canonical home and reading intent for a topic or compound draft. Use for new notes and substantial additions when placement is not trivial. Delegate repository discovery to $note-topic-search; this skill owns placement, reuse/extend/create/split decisions, not search mechanics, boundary depth, or prose writing.
---

# Note Home Finder

This skill owns **canonical placement**. It answers **where knowledge belongs** after repository retrieval has established the relevant existing notes.

## Capability ownership

Owns:

- center-of-gravity and reading-intent decisions;
- theory/mechanism/implementation/application placement;
- reuse, extend, create, and split outcomes;
- canonical destinations for compound material.

Delegates:

- repository discovery and candidate retrieval to `$note-topic-search`.

Must not:

- reproduce qmd query syntax or fallback-search procedures;
- decide how much neighboring content should remain locally;
- write, move, or normalize note content;
- invoke higher-level authoring or refactoring workflows.

The caller may pass the accepted placement to `$note-boundary-analyzer`; this skill does not invoke the analyzer itself.

## Inputs

- the topic, draft, or substantial proposed addition;
- an optional user-proposed target note;
- confirmed candidate notes from `$note-topic-search`;
- repository taxonomy and nearby naming/sequence conventions.

A user-proposed target is strong evidence, but it does not override a clear conceptual or abstraction-boundary mismatch.

## Placement decision

Determine:

1. **Center of gravity:** What single subject is the material really trying to explain?
2. **Reading intent:** Why would a future reader open the destination note?
3. **Abstraction level:** Is the material theory, mechanism, implementation, or application?
4. **Existing ownership:** Does one confirmed note already explain this concept in the same sense and at the same level?
5. **Compound structure:** Does the material contain distinct concepts that future readers would search for separately?

Choose one outcome:

- `reuse_existing_note`
- `extend_existing_note`
- `create_new_note`
- `split_across_notes`

## Decision rules

Prefer, in order:

1. Reuse an existing canonical explanation when the topic is already covered at the right granularity.
2. Extend an existing note when the material is clearly part of that note's subject and reading intent.
3. Split material when distinct concepts have different canonical homes, abstraction levels, or reading intents.
4. Create a sibling note inside an established cluster when the topic is substantial but not naturally subordinate to an existing note.
5. Create a new top-level note or folder only when no existing taxonomy is a clear fit.

Do not split tightly coupled submechanisms merely because they can be named separately. Do split when one title would become vague because the material mixes foundational theory, concrete implementation, and downstream application.

## Abstraction heuristic

Use `AGENTS.md` as authoritative:

- foundational theory should not accumulate implementation documentation;
- implementation-specific notes should own concrete architecture, configuration, APIs, or product behavior;
- application notes may explain how a foundational mechanism affects their system without redeveloping the foundational theory.

## Output contract

Return:

- `outcome`;
- `recommended_path` for single-home outcomes;
- `split_plan` for split outcomes, with one line per subtopic and destination;
- `abstraction_level` for each destination;
- `reading_intent`;
- `confidence`;
- `rationale` in 1–3 sentences;
- `alternatives` only when genuinely ambiguous.

Do not write or move content.
