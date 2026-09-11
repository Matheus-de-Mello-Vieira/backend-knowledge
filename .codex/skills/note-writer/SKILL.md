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

Higher-level workflows are responsible for supplying semantic decisions and for other downstream mechanical stages when applicable, such as link normalization after link changes. When this skill mutates a Markdown file, Markdown lint cleanup and verification is a required downstream dependency of the writer itself.

## Writing grammar

Choose structure from the logic of the knowledge:

- **Prose:** causality, motivation, relationships, and conceptual development.
- **Labeled descriptive bullets:** parallel named properties, components, mechanisms, states, responsibilities, alternatives, or comparison dimensions when each item has its own explanation. Use the form `- **Label:** Explanation.` so the label names the concept and the following text explains its meaning, mechanism, consequence, constraint, or distinction.
- **Nested bullets:** consequences, qualifications, submechanisms, or details owned by a parent item.
- **Numbered lists:** ordered procedures, protocols, algorithms, lifecycles, or state transitions.
- **Tables:** repeated comparison dimensions across several entities.
- **Mermaid:** branches, loops, topology, dependencies, or state transitions that prose cannot express as clearly.
- **Callouts:** secondary examples, warnings, terminology clarifications, implementation observations, practical inspection, or architectural stories.

Prefer labeled descriptive bullets when several sibling statements answer the same implicit question or occupy the same conceptual dimension and each has a concise stable name. Prefer prose when the statements depend on one another to form a causal argument, progression, or continuous explanation.

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
- reassess the representation form rather than mechanically preserving the source format: use labeled descriptive bullets for parallel named concepts with independent explanations, prose for causal or dependent reasoning, numbered lists for ordered processes, and nested bullets for subordinate consequences or qualifications;
- do not treat a style-focused rewrite as vocabulary, tone, or sentence-level editing only;
- keep changes within the approved destination and content boundary.

### Rewrite preservation

Before restructuring existing prose, identify the distinct supported information carried by the source passage: technical claims, relationships, qualifiers, exceptions, caveats, constraints, examples, terminology, and meaningful scope.

Rewrite and reorganize those units according to the repository's explanatory grammar, then compare the result with the original. Every unique supported unit must remain represented unless its removal was explicitly authorized as duplication, correction, irrelevance, or scope cleanup.

A style-focused rewrite may change wording, ordering, paragraph/list structure, and local transitions, but it must not silently remove technical information or change the semantic strength of supported claims. Structural compression is valid only when it preserves semantic coverage.

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

## Post-write Markdown validation

Whenever this skill mutates one or more repository Markdown files, `$markdownlint-fix` is mandatory on every Markdown file changed by the writer before it returns control to its caller.

1. Complete the approved prose, explanatory-structure, or approved-link-markup mutation.
2. Perform the writer's semantic verification on the changed material.
3. Invoke `$markdownlint-fix` on every Markdown file changed by the writer, using only those changed files as lint targets.
4. Let `$markdownlint-fix` own routine auto-fixes, remaining lint repair, and the clean rerun according to its own contract; do not reproduce that mechanical procedure here.
5. If lint cleanup changes the edited area, reread it and confirm the changes remained mechanical and did not alter the approved technical meaning.
6. Return control only after the writer-produced Markdown has completed the lint stage successfully.

If this skill only returns a candidate Markdown fragment or proposed replacement without mutating a repository file, do not invoke file-based lint cleanup. A later workflow stage that mutates Markdown after the writer returns remains responsible for the validation required by that stage; the writer's lint pass guarantees only that the Markdown state it produced was lint-clean when it returned.

## Verification

Before returning the written candidate:

- reread the affected section as a first-time reader;
- confirm the assigned concept is understandable without duplicated neighboring theory;
- confirm rewrites preserve the intended technical meaning, scope, qualifiers, and terminology;
- confirm structural compression or reformatting did not discard unique technical claims, relationships, qualifiers, caveats, constraints, examples, or exceptions from the original material;
- confirm semantically parallel named concepts use labeled descriptive bullets when that structure is clearer, and that prose was not retained merely because the source was originally written as paragraphs;
- confirm modal verbs and frequency qualifiers represent real technical contingency rather than generic caution, and that each qualification is attached to the narrowest claim that requires it;
- confirm examples remain subordinate;
- when the mechanism-code walkthrough pattern was used, confirm each split corresponds to a meaningful technical transition rather than arbitrary code length;
- confirm repository-planning language did not leak into durable prose when a technical relationship could be stated directly;
- confirm approved link decisions were applied without semantic changes and linked sentences remain independently meaningful;
- confirm headings and formatting match nearby note conventions;
- if repository Markdown files were mutated, confirm `$markdownlint-fix` was invoked on every Markdown file changed by the writer before returning.

Return the completed Markdown candidate or apply the scoped edit when invoked by a higher-level workflow.
