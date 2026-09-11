---
name: note-scaffolding
description: Create a learning-oriented note or note-set scaffold for a topic the user wants to learn but has not yet fully studied. Use to establish conceptual boundaries, prerequisites, questions, and learning sequence without pretending the missing knowledge is already known.
---

# Note Scaffolding

This workflow creates **structure for future learning**, not a finished explanation.

## Progressive workflow

1. Invoke `$note-topic-search` to identify existing prerequisites, neighboring concepts, and already-covered material.
2. If the new topic's home or whether it should be one note versus a sequence is unclear, invoke `$note-home-finder`. Skip it when the target is already explicit and structurally appropriate.
3. Load `references/learning-structure.md` only now and design the scaffold.
4. Do **not** invoke `$note-boundary-analyzer` unless existing durable prose is being redistributed as part of the scaffold.
5. Create or amend the requested scaffold. Do not fill sections with unsupported knowledge merely to make the note look complete.
6. If the scaffold contains internal links, invoke `$markdown-link-normalizer`; otherwise skip link machinery.

## Output modes

- **Plan only:** return the proposed note(s), section sequence, learning questions, and prerequisite relationships without modifying files.
- **Repository scaffold:** create the requested headings and, when helpful, non-rendered HTML comments describing what each section should eventually explain.

Prefer plan-only mode when the user has not asked for repository changes.

## Constraints

- Existing notes own existing concepts; scaffold links to them instead of duplicating them.
- A scaffold may be intentionally incomplete.
- Do not convert open learning questions into claims unless supported by supplied/repository sources.
- Split into multiple notes only when different reading intents or abstraction levels justify it.