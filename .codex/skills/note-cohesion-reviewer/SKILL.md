---
name: note-cohesion-reviewer
description: Review one or more durable notes for repository cohesion without editing them. Diagnose center-of-gravity drift, abstraction leakage, same-level duplication, weak local context, oversized examples, explanation/format mismatches, misplaced qualification, rewrite-fidelity loss, document narration, and cross-note relationship problems.
---

# Note Cohesion Reviewer

This is the canonical **read-only semantic review** capability for repository notes.

## Inputs

- target note(s);
- repository invariants from `AGENTS.md`;
- neighboring notes when the caller has retrieved them;
- optional accepted placement/boundary plans for post-edit verification;
- optional prior or source version when rewrite fidelity must be assessed.

## Review dimensions

- **Center of gravity:** Does the note still explain one stable subject for one primary reading intent?
- **Abstraction:** Does theory/mechanism/implementation/application material stay within appropriate boundaries?
- **Canonical ownership:** Is the same concept fully explained elsewhere at the same sense and level?
- **Local sufficiency:** Does the note contain enough neighboring context for its own argument without becoming independently exhaustive?
- **Examples:** Do concrete systems illuminate the concept and stop before becoming implementation documentation?
- **Explanation:** Are causal relationships and important state changes explicit rather than merely listed?
- **Qualification:** Do modal verbs and frequency qualifiers represent genuine capability, uncertainty, implementation variance, configuration, resource/filter semantics, runtime state, or application choice? Flag wording that makes a deterministic relationship sound merely possible or places uncertainty on a broader proposition than necessary.
- **Structure:** Does the representation match the conceptual partial order of the knowledge? First identify whether neighboring statements form dependencies, sibling branches, parent-child decomposition, or genuinely ordered sequences. Establish the minimum **causal spine** required to make dependencies, transitions, scope, qualification, or convergence explicit. Then inspect the remaining claims individually: if they depend only on context already established by that spine, are independently retrievable, and share a coherent semantic dimension, they should normally be exposed as a scannable branch rather than retained as residual prose. Several consecutive explanatory paragraphs should trigger this decomposition check, but paragraph count is not itself a formatting rule. Stable named siblings should use labeled bullets when useful; lightweight siblings may remain unlabeled; and numbered lists should represent cases where sequence is part of the meaning. Confirm that bullet siblings share a coherent semantic dimension rather than merely a common parent. Flag dependency chains disguised as parallel bullets, semantically mixed bullet groups, and dense prose that retains independently retrievable facts after their common context is established.
- **Representation simplicity:** Is the chosen representation the simplest one that preserves the relationship? Mermaid requires more than the mere presence of branching: prefer prose or numbering when they express the mechanism clearly and compactly, and use Mermaid only when topology, interaction, loops, parallel flows, dependencies, or state transitions are materially easier to understand visually.
- **Rewrite fidelity:** When a prior or source version is available, did restructuring, compression, or style adaptation silently drop a supported claim, relationship, qualifier, caveat, constraint, example, exception, or meaningful scope, or change its semantic strength? Preservation applies to supported knowledge rather than source formatting or taxonomy; flag cases where a weak source categorization is retained even though the same claims could be preserved more accurately under a coherent structure.
- **Links:** Are conceptual relationships natural, useful, and non-decorative?
- **Document narration:** Does durable prose describe note ownership, repository placement, section purpose, or example pedagogy where it could instead describe the technical mechanism, composition, distinction, constraint, or consequence? Preserve real architectural boundary language; flag only document-boundary narration.

## Output contract

Return prioritized findings. Each finding should include:

- `severity`: blocking, important, or optional;
- `location`;
- `principle`;
- `problem`;
- `recommended_action`;
- `related_note` when repository context matters.

For qualification findings, identify the real source of contingency or state that no technical contingency is evident. Recommend moving modality to the narrowest claim that varies rather than merely replacing or deleting a specific word.

For structure findings, identify the local relationship among the affected statements before recommending a representation. Distinguish **necessary prose**, where sentence adjacency still carries causality, transition, scope, qualification, or convergence, from **residual prose**, where a statement now relies only on context already established above. Recommend the minimum causal spine first, then apply the retrieval test to residual claims that remain independently useful under that context. Recommend numbered lists when order itself carries meaning, labeled bullets when independently retrievable sibling concepts share a coherent semantic dimension and have useful stable names, unlabeled bullets when such siblings benefit from scanning but labels would be artificial, and nested bullets only when the child information is genuinely owned by the parent. Do not recommend bullets merely because nearby sentences are short or numerous, share only a broad parent, or lack a common semantic dimension. When a diagram is involved, recommend Mermaid only if the visual relationship is materially clearer than an equivalent compact prose or numbered representation.

For rewrite-fidelity findings, identify the specific supported information that was lost, weakened, strengthened, or otherwise altered. Do not infer missing content when no prior or source version is available for comparison. Do not treat preservation of the source's paragraphing, list structure, labels, grouping, or taxonomy as a fidelity requirement when the underlying supported claims and relationships can be preserved more accurately through a different representation.

For document-narration findings, identify the technical relationship that the prose should express instead of merely recommending removal.

Separate confirmed findings from hypotheses that require broader repository search.

## Constraints

Do not edit files. Do not invent missing technical content. Do not recommend broad rewrites when a smaller structural correction would resolve the problem. Assess rewrite fidelity only against supplied or retrieved prior/source material rather than general knowledge. Ownership and boundary vocabulary is valid in the review artifact itself; the document-narration rule applies to durable note prose and headings.
