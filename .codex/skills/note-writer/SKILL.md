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

Choose structure from the **conceptual partial order** of the knowledge rather than from the source formatting.

First identify the local relationships among the ideas:

- which ideas depend on earlier ideas for their meaning;
- which ideas are sibling branches under the same parent and can be understood independently of one another;
- which ideas are subordinate details owned by one parent;
- which relationships are not merely dependent but genuinely ordered sequences.

Then apply a second-stage retrieval test. After the minimum context or dependency is explicit, identify which consequences, properties, constraints, alternatives, or observations remain independently retrievable and would be easier to scan as a set. Do not treat a causal region as prose-only merely because it contains dependency edges.

Before making a bullet set, verify that its members share a coherent semantic dimension, not merely a common parent. They should answer the same implicit question in comparable terms; do not mix states, events, transitions, actors, or unrelated kinds of fact in one sibling group.

### Causal spine and branches

A causal explanation may contain both a **causal spine** and **retrievable branches**. Preserve in prose only the claims whose adjacency is still doing conceptual work: establishing causality, transition, scope, qualification, contrast, or convergence.

After that spine is explicit, inspect the remaining claims individually. A claim may be causally downstream from earlier prose without itself needing to remain prose. If it depends only on context already established above, can be understood independently of neighboring claims, and belongs to the same semantic dimension as its peers, expose it as a scannable branch when that improves retrieval.

Several consecutive explanatory paragraphs should trigger an explicit decomposition check. This is a review heuristic, not a paragraph-count quota: two strong siblings may justify bullets, while many tightly dependent statements may still require prose.

A common local shape is therefore:

1. prose establishes why the mechanism exists or what dependency matters;
2. labeled or unlabeled bullets expose properties, constraints, consequences, responsibilities, alternatives, or observations that now stand independently under that context;
3. prose resumes when those branches converge or another dependency must be established.

Then choose the local representation:

- **Prose:** the minimum dependency edges, causality, motivation, transitions, contrast, qualification, and conceptual development required for understanding. Prose should make clear why one idea leads to, constrains, or changes the interpretation of another.
- **Labeled descriptive bullets:** sibling named properties, components, mechanisms, states, responsibilities, alternatives, or comparison dimensions when each item has a concise stable name worth retrieving later. Use the form `- **Label:** Explanation.` so the label names the concept and the following text explains its meaning, mechanism, consequence, constraint, or distinction.
- **Unlabeled bullets:** sibling consequences, observations, conditions, implications, or other independently understandable points when a label would be artificial or add ceremony without improving retrieval.
- **Nested bullets:** consequences, qualifications, submechanisms, or details owned by a parent item.
- **Numbered lists:** ordered procedures, protocols, algorithms, lifecycles, state transitions, or other dependencies where the sequence itself is part of the meaning.
- **Tables:** repeated comparison dimensions across several entities.
- **Mermaid:** branches, loops, topology, interactions, dependencies, parallel flows, or state transitions that are materially clearer visually than in compact prose or a numbered list. The existence of branching alone does not justify a diagram.
- **Callouts:** secondary examples, warnings, terminology clarifications, implementation observations, practical inspection, or architectural stories.

A causal subject does not require one uninterrupted paragraph. Use the minimum prose necessary to establish a dependency, expose independently retrievable sibling consequences, properties, constraints, alternatives, observations, or branches as bullets when that improves scanning, and resume prose when the branches converge or another dependency must be established.

Prefer labeled bullets when sibling concepts have stable names that materially help retrieval or comparison. Prefer unlabeled bullets when the sibling structure is real but labels would merely restate the sentence. Do not use bullets solely because statements are short or visually easier to scan; the items must first be locally independent, independently retrievable, and semantically coherent under the established context.

Do not mechanically apply one form to an entire section. A section may move from prose to bullets, from bullets to prose, or from an ordered prefix to an unordered sibling set as the conceptual partial order changes locally.

## Code demonstration gate

When writing or materially revising a code demo, load `references/mechanism-code-walkthrough.md` by default when the demo teaches an interaction, lifecycle, state transition, or system-managed behavior. This includes demonstrations with multiple actors, setup or teardown, connection or request lifecycles, protocol exchanges, or API calls that change kernel, runtime, database, filesystem, or network state.

Skip the reference only when the code is primarily a final copyable artifact or a cohesive implementation whose own structure already makes the mechanism clear. Do not use code length as the decision criterion.

## Rewrite discipline

When rewriting existing prose for clarity, explanation quality, or repository style:

- preserve the supported technical meaning, scope, qualifiers, distinctions, caveats, and established terminology unless an accepted semantic decision explicitly changes them;
- use surrounding note context and repository writing policy to infer style rather than mechanically copying another section's formatting;
- improve causal progression, local coherence, and structure without introducing new technical claims merely to make the text feel more complete;
- reassess the conceptual relationships rather than mechanically preserving the source representation: identify the minimum causal spine, inspect the residual claims individually, and expose independently retrievable and semantically coherent siblings as labeled or unlabeled bullets according to whether stable names aid retrieval; use numbered lists when sequence is part of the meaning, and use nested bullets only for details genuinely owned by the parent item;
- allow local alternation among prose, bullet groups, and numbered sequences when that better matches how the explanation branches and converges;
- preserve supported claims and relationships rather than the source's paragraphing, labels, grouping, or taxonomy. If the source places non-peer concepts in one category, preserve the underlying claims while reorganizing them into a more coherent representation instead of silently retaining the weak categorization;
- prefer the simplest representation that preserves the relationship; do not introduce Mermaid when compact prose or numbering is equally clear;
- do not treat a style-focused rewrite as vocabulary, tone, or sentence-level editing only;
- keep changes within the approved destination and content boundary.

### Rewrite preservation

Before restructuring existing prose, identify the distinct supported information carried by the source passage: technical claims, relationships, qualifiers, exceptions, caveats, constraints, examples, terminology, and meaningful scope.

Rewrite and reorganize those units according to the repository's explanatory grammar, then compare the result with the original. Every unique supported unit must remain represented unless its removal was explicitly authorized as duplication, correction, irrelevance, or scope cleanup.

A style-focused rewrite may change wording, ordering, paragraph/list structure, labels, grouping, and local taxonomy when needed to represent the supported relationships more accurately. Preservation applies to semantic coverage and strength, not to the source representation. Structural compression or reclassification is valid only when it preserves every supported claim, qualification, relationship, and relevant distinction.

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
- confirm structural compression, reclassification, or reformatting did not discard unique technical claims, relationships, qualifiers, caveats, constraints, examples, or exceptions from the original material;
- confirm the local representation matches the conceptual partial order and retrieval test: dependencies use only the prose needed to remain explicit; after the causal spine is established, residual claims are inspected individually and independently retrievable consequences, properties, constraints, alternatives, observations, and sibling branches are exposed when scanning benefits; every bullet set has a coherent semantic dimension; stable named siblings use labels when useful; lightweight siblings remain unlabeled when labels would be artificial; subordinate details remain attached to their parent; and ordered relationships use numbering when sequence matters;
- when several consecutive explanatory paragraphs remain, confirm they still require prose adjacency rather than merely inheriting context already established above;
- confirm Mermaid is used only when the visual relationship is materially clearer than compact prose or numbering;
- confirm modal verbs and frequency qualifiers represent real technical contingency rather than generic caution, and that each qualification is attached to the narrowest claim that requires it;
- confirm examples remain subordinate;
- when the mechanism-code walkthrough pattern was used, confirm each split corresponds to a meaningful technical transition rather than arbitrary code length;
- confirm repository-planning language did not leak into durable prose when a technical relationship could be stated directly;
- confirm approved link decisions were applied without semantic changes and linked sentences remain independently meaningful;
- confirm headings and formatting match nearby note conventions;
- if repository Markdown files were mutated, confirm `$markdownlint-fix` was invoked on every Markdown file changed by the writer before returning.

Return the completed Markdown candidate or apply the scoped edit when invoked by a higher-level workflow.
