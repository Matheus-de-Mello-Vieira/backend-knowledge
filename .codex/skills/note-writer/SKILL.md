---
name: note-writer
description: Write or amend Markdown note prose after the destination, abstraction level, content boundary, and any semantic link decisions are already decided. This is the canonical prose-and-structure mutation primitive for repository notes. Do not perform placement, boundary analysis, semantic link selection, or broad repository search here.
---

# Note Writer

This skill owns **note prose and explanatory structure**.

Repository architecture comes from `AGENTS.md`; default writing behavior comes from `.codex/model_instructions.md`.

## Capability ownership

Owns:

- writing new sections;
- amending existing sections;
- integrating required local context;
- creating bounded examples or callouts;
- restructuring nearby prose when needed for coherence;
- applying or preserving caller-provided approved link markup without changing its semantic destination.

Requires:

- an approved destination and abstraction level;
- an approved boundary plan when the addition is substantial or crosses nearby concepts;
- relevant source material and local note context;
- an approved link plan when semantic links are part of the edit.

Must not:

- search for canonical homes;
- invoke `$note-home-finder` or `$note-boundary-analyzer`;
- decide whether substantial material belongs in another note;
- select semantic link targets or decide whether a relationship deserves a link;
- invoke `$note-link-planner`, `$note-authoring`, or `$note-refactor`;
- move content between notes without an approved structural plan;
- perform broad link normalization.

Higher-level workflows are responsible for supplying semantic decisions and invoking mechanical validation afterward.

## Writing grammar

Choose structure from the logic of the knowledge:

- **Prose:** causality, motivation, relationships, and conceptual development.
- **Descriptive bullets:** parallel properties, components, mechanisms, states, responsibilities, or alternatives.
- **Nested bullets:** consequences, qualifications, submechanisms, or details owned by a parent item.
- **Numbered lists:** ordered procedures, protocols, algorithms, lifecycles, or state transitions.
- **Tables:** repeated comparison dimensions across several entities.
- **Mermaid:** branches, loops, topology, dependencies, or state transitions that prose cannot express as clearly.
- **Callouts:** secondary examples, warnings, terminology clarifications, implementation observations, practical inspection, or architectural stories.

Do not mechanically apply all forms to every section.

## Scope discipline

- Explain the destination note's own subject completely at its assigned abstraction level.
- Include only the neighboring context required for the local argument.
- Keep examples narrower than the concept they illustrate.
- Stop implementation-specific explanation when the implementation becomes the subject.
- Do not reproduce a complete same-level explanation that another canonical note already owns.

## Link application discipline

When the caller supplies an approved link plan or approved link markup:

- preserve the approved source phrase and semantic destination;
- apply the link without introducing navigation-only prose;
- preserve visible wording when required by the plan;
- do not substitute a different related note or create additional semantic links independently.

Semantic link selection belongs exclusively to `$note-link-planner`. Mechanical link normalization belongs to the caller's `$markdown-link-normalizer` stage.

## Verification

Before returning the written candidate:

- reread the affected section as a first-time reader;
- confirm the assigned concept is understandable without duplicated neighboring theory;
- confirm examples remain subordinate;
- confirm terminology and qualifiers are preserved;
- confirm approved link decisions were applied without semantic changes;
- confirm headings and formatting match nearby note conventions.

Return the completed Markdown candidate or apply the scoped edit when invoked by a higher-level workflow.
