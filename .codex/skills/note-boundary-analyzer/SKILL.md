---
name: note-boundary-analyzer
description: Determine exactly how much proposed or overlapping material each note should own after canonical placement is known. Use to separate canonical explanation, required local context, examples, implementation detail, application consequences, duplicates, and separate subjects. This skill analyzes scope only; it does not edit files.
---

# Note Boundary Analyzer

This skill owns **content-scope distribution**. It answers **how much belongs in each note** after `$note-home-finder` has answered **where the concept belongs**.

## Capability ownership

Owns:

- classifying proposed or overlapping material by conceptual role;
- deciding what a destination should explain fully versus briefly;
- detecting same-level duplication and abstraction leakage;
- producing an explicit boundary/disposition plan.

Delegates:

- canonical placement to `$note-home-finder`;
- repository retrieval indirectly to `$note-topic-search` through `$note-home-finder`;
- prose writing to `$note-writer`;
- cross-note mutation to `$note-content-mover` or `$note-refactor`.

Must not:

- search the repository directly when placement is unresolved;
- choose destinations independently of `$note-home-finder`;
- edit files or write final prose;
- normalize links.

## Boundary model

For each meaningful content unit, classify it as one of:

- **Canonical explanation:** the destination owns the full explanation at this sense and abstraction level.
- **Required local context:** the current note needs a concise explanation for its own argument, but another note owns the deeper treatment.
- **Illustrative example:** a concrete system or story clarifies the local concept and should stop once that purpose is satisfied.
- **Implementation detail:** concrete architecture, API, configuration, data structure, version behavior, or operational mechanics owned by an implementation-specific note.
- **Application consequence:** how another system uses or is affected by the mechanism; normally owned by that application or domain note.
- **Duplicate same-level explanation:** content already canonically explained elsewhere in the same sense and abstraction level.
- **Separate subject:** material independently valuable under another reading intent.

## Analysis procedure

1. State the target note's center of gravity and abstraction level.
2. Break the proposed or overlapping material into conceptual units.
3. Classify each unit using the boundary model.
4. For every non-canonical unit, choose a disposition:
   - keep concise local context;
   - keep as a bounded callout or example;
   - move;
   - merge with an existing canonical section;
   - remove duplicate body while preserving a natural inline link when useful;
   - split into another destination.
5. Check that the remaining target-note material forms a coherent explanation without duplicate prerequisite theory.

## Boundary tests

- **Understanding test:** Would removing the unit make the reader understand the target subject less well, or merely know less about another subject?
- **Subject test:** Has the explanation started teaching the neighboring system rather than using it to explain the target concept?
- **Abstraction test:** Is a foundational note accumulating concrete implementation behavior that belongs elsewhere?
- **Duplication test:** Is the same concept already fully explained elsewhere in the same sense and at the same level?
- **Independent-value test:** Would this unit be independently useful to a reader searching for another subject?

## Output contract

Return a boundary plan containing:

- `target_center_of_gravity`;
- `target_abstraction_level`;
- one entry per conceptual unit with:
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
