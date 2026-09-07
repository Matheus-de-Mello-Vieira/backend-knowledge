---
name: note-boundary-analysis
description: Determine exactly how much of proposed or overlapping material each note should own after placement is known. Use to separate canonical explanation, required local context, examples, implementation detail, and adjacent subjects. This skill analyzes scope only; it does not edit files.
---

# Note Boundary Analysis

This skill owns **content-scope distribution** across known note homes.

Use it after `$note-home-finder` has established the likely destination or split plan, or invoke `$note-home-finder` first when placement is not yet resolved.

## Delegated capabilities

When placement is unresolved:

- `$note-home-finder` — canonical homes and abstraction levels.

Do not perform repository search directly. `$note-home-finder` delegates that to `$note-topic-search`.

## Boundary model

For each meaningful content unit, classify it as one of:

- **Canonical explanation:** the destination note owns the full explanation at this abstraction level.
- **Required local context:** the current note needs a concise explanation for its own argument, but another note owns the deeper treatment.
- **Illustrative example:** a concrete system or story clarifies the local concept and should stop once that purpose is satisfied.
- **Implementation detail:** concrete architecture, API, configuration, data structure, version behavior, or operational mechanics owned by an implementation-specific note.
- **Application consequence:** how another system uses or is affected by the mechanism; normally owned by that application/domain note.
- **Duplicate same-level explanation:** content already canonically explained elsewhere in the same sense and abstraction level.
- **Separate subject:** material independently valuable under another reading intent.

## Analysis procedure

1. State the target note's center of gravity and abstraction level.
2. Break the proposed or overlapping material into conceptual units.
3. Classify each unit using the boundary model.
4. For non-canonical units, determine the correct disposition:
   - keep concise local context;
   - keep as a bounded callout/example;
   - move;
   - merge with an existing canonical section;
   - remove duplicate body and preserve a natural inline link;
   - split into another destination.
5. Check that the remaining target-note material forms a coherent explanation without requiring duplicate prerequisite theory.

## Boundary tests

Use these tests explicitly:

- **Understanding test:** Would removing the unit make the reader understand the target subject less well, or merely know less about another subject?
- **Subject test:** Has the explanation started teaching the neighboring system rather than using it to explain the target concept?
- **Abstraction test:** Is a foundational note accumulating concrete implementation behavior that can be explained elsewhere?
- **Duplication test:** Is the same concept already fully explained elsewhere in the same sense and at the same level?
- **Independent-value test:** Would this unit be independently useful to a reader searching for another subject?

## Output contract

Return a boundary plan with:

- `target_center_of_gravity`;
- `target_abstraction_level`;
- one entry per conceptual unit containing:
  - `concept`;
  - `classification`;
  - `disposition`;
  - `destination` when different from the current note;
  - `local_context_limit` when some text should remain;
  - `link_target` when a natural deeper link is appropriate;
- `duplication_to_remove`;
- `examples_to_bound`;
- `confidence`.

Do not edit files or write final prose.
