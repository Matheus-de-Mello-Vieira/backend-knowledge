---
name: note-writer
description: Create or substantively amend Markdown note prose after the destination, abstraction level, content boundary, and any semantic link decisions are already decided. This is the canonical prose-and-structure mutation primitive for repository notes, including explanation repairs and style-focused rewrites that preserve technical meaning. Do not perform placement, boundary analysis, semantic link selection, or broad repository search here.
---

# Note Writer

This skill owns **all substantive durable-note prose and explanatory-structure mutation** after semantic decisions are settled.

Repository architecture comes from `AGENTS.md`; default writing behavior comes from `.codex/model_instructions.md`.

## Capability ownership

Owns:

- writing new sections or explanatory prose;
- amending and rewriting existing sections;
- repairing confusing, incomplete, or weak explanations;
- adapting existing prose to repository writing style while preserving its technical meaning, scope, qualifiers, and terminology;
- integrating required local context;
- creating bounded examples or callouts;
- restructuring paragraphs, bullets, or nearby prose when needed for coherence;
- applying or preserving caller-provided approved link markup without changing its semantic destination.

Higher-level workflows that delegate prose mutation to this skill may prepare inputs and validate the result, but must not reimplement substantive writing themselves.

Requires:

- an approved destination and abstraction level;
- an approved boundary plan when the addition or rewrite is substantial or crosses nearby concepts;
- relevant source material and local note context;
- the technical meaning and constraints that must be preserved during a rewrite;
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

## Code demonstration gate

When code primarily serves to expose a technical mechanism, decide whether the mechanism remains clear when the code is presented as one block.

Load `references/mechanism-code-walkthrough.md` when understanding requires tracking several meaningful state transitions, external or system-managed state, or API operations whose conceptual meaning would otherwise need to be reconstructed after the code block.

Do not trigger the pattern from code length. Keep a complete block when the code itself is the artifact being studied, a final assembled reference, or already exposes its important structure clearly enough that splitting would make the implementation harder to inspect.

## Rewrite discipline

When rewriting existing prose for clarity, explanation quality, or repository style:

- preserve the supported technical meaning, scope, qualifiers, distinctions, caveats, and established terminology unless an accepted semantic decision explicitly changes them;
- use surrounding note context and repository writing policy to infer style rather than mechanically copying another section's formatting;
- improve causal progression, local coherence, and structure without introducing new technical claims merely to make the text feel more complete;
- keep changes within the approved destination and content boundary.

### Modal precision

Preserve necessary uncertainty, but do not weaken direct technical semantics with generic hedging.

For every modal or frequency qualifier introduced or retained, identify the concrete technical condition that makes the proposition non-universal at the current abstraction level. If no such condition exists, state the relationship directly.

When only a consequence or result is contingent, keep the invariant relationship in direct present tense and move the qualification to the narrowest outcome that actually varies. Distinguish among:

- direct semantic relationships and state transitions, which should normally be stated directly;
- supported capabilities, where `can` or equivalent wording carries real meaning;
- possible or non-guaranteed outcomes, where `may`, `can`, or an explicit condition can preserve necessary uncertainty;
- implementation, configuration, platform, resource, filter, or runtime variance, which should be qualified explicitly.

Do not mechanically replace one modal verb with another. Determine first whether modality is necessary and, if so, what proposition it should qualify.

## Scope discipline

- Explain the destination note's own subject completely at its assigned abstraction level.
- Include only the neighboring context required for the local argument.
- Keep examples narrower than the concept they illustrate.
- Stop implementation-specific explanation when the implementation becomes the subject.
- Do not reproduce a complete same-level explanation that another canonical note already owns.

## Durable prose boundary

Caller inputs may contain repository-planning vocabulary such as canonical owner, destination, abstraction boundary, local context, move, merge, split, or duplicate. Treat those terms as editing instructions, not as wording to reproduce automatically.

Translate accepted repository decisions into direct technical explanation:

- describe mechanisms, composition, state, constraints, consequences, and real system boundaries;
- do not make the primary claim of a durable sentence that a note or section owns, covers, defines, focuses on, or contains a concept when the technical relationship can be stated directly;
- do not explain why an example was included when the mechanism the example exposes can be stated directly;
- let technical content establish scope when possible, while preserving explicit scope statements that constrain the validity of a technical claim;
- prefer headings that name technical concepts or real distinctions rather than repository placement or ownership decisions;
- preserve repeated coverage only when it contributes local mechanism, consequence, constraint, or composition meaning.

Repository architecture remains explicit in planning and review artifacts; durable note prose should normally remain system-facing.

## Link application discipline

When the caller supplies an approved link plan or approved link markup:

- preserve the approved source phrase and semantic destination;
- apply the link without introducing navigation-only prose;
- preserve visible wording when required by the plan;
- do not substitute a different related note or create additional semantic links independently;
- confirm the linked sentence remains a useful technical statement if the Markdown link markup is removed.

Semantic link selection belongs exclusively to `$note-link-planner`. Mechanical link normalization belongs to the caller's `$markdown-link-normalizer` stage.

## Verification

Before returning the written candidate:

- reread the affected section as a first-time reader;
- confirm the assigned concept is understandable without duplicated neighboring theory;
- confirm rewrites preserve the intended technical meaning, scope, qualifiers, and terminology;
- confirm modal verbs and frequency qualifiers represent real technical contingency rather than generic caution, and that each qualification is attached to the narrowest claim that requires it;
- confirm examples remain subordinate;
- when the mechanism-code walkthrough pattern was used, confirm each split corresponds to a meaningful technical transition rather than arbitrary code length;
- confirm repository-planning language did not leak into durable prose when a technical relationship could be stated directly;
- confirm approved link decisions were applied without semantic changes and linked sentences remain independently meaningful;
- confirm headings and formatting match nearby note conventions.

Return the completed Markdown candidate or apply the scoped edit when invoked by a higher-level workflow.
