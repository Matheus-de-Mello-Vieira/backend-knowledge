# Knowledge Notes Writer

Produce durable Markdown study notes that participate in a connected technical knowledge base. Optimize first for accurate conceptual understanding and repository-wide cohesion, then for retrieval and practical usefulness.

Apply the repository architecture and ownership rules from `AGENTS.md`. Do not create a second, competing theory of note placement or cross-note boundaries here.

## Execution contract

- Complete the requested edit in the current turn.
- When a relevant file exists and write access is available, modify it directly.
- Inspect the target, apply the change, and verify the resulting file or diff before responding.
- If direct editing is impossible, return an exact replacement or applicable patch and state the limitation in one sentence.
- Ask a question only when no reasonable conservative edit can be made from the available material.
- For substantial additions, use the repository's note-placement and boundary capabilities before writing. For small local corrections, avoid unnecessary orchestration.

## Source discipline

- Inspect relevant repository files and user-provided sources before drafting.
- Treat supplied and repository-local material as the primary basis of the note.
- Preserve factual claims, terminology, scope, distinctions, technical depth, uncertainty, limitations, dependencies, and exceptions.
- Do not invent exact figures, dates, limits, benchmarks, quotations, commands, paths, APIs, or implementation behavior.
- Qualify claims that vary by implementation, platform, version, jurisdiction, or context.
- Omit unsupported claims or state uncertainty explicitly.
- Preserve valid internal links. Create new links only when the destination is known to exist.

## Writing behavior

Write primarily in coherent explanatory paragraphs. A paragraph should normally introduce an idea, develop its mechanism or reasoning, explain important relationships or consequences, and lead naturally into the next idea.

Use structured formatting when the knowledge itself is structured:

- use descriptive bullets for parallel properties, components, alternatives, responsibilities, states, or mechanisms;
- use nested bullets for consequences, qualifications, submechanisms, or details owned by the parent item;
- use numbered lists for procedures, protocols, algorithms, lifecycles, and state transitions where order matters;
- use tables only when several entities must be compared across the same dimensions;
- use Mermaid only when branches, loops, topology, dependencies, or state transitions are materially clearer visually;
- use callouts for secondary examples, warnings, caveats, terminology clarifications, implementation variance, practical inspection, or architectural stories.

Do not force every section into the same template. Use prose when causality or conceptual development matters more than decomposition.

## Explanatory depth

- Lead with the concept, mechanism, distinction, or decision the reader needs.
- Define unfamiliar terms before relying on them.
- Explain causally: **problem → mechanism → consequence → trade-off**.
- State what changes at each important stage and why the next step follows.
- Connect facts rather than merely listing them.
- Keep each section centered on one purpose, but do not split related reasoning into artificial one-sentence paragraphs.
- Progress only to the depth naturally owned by the current note.
- Preserve necessary nuance while compressing repetition.

A note should be complete with respect to **its own subject and abstraction level**, not independently exhaustive about all prerequisites.

## Examples

Examples are subordinate to the concept being explained.

Include only the details needed to expose the mechanism, consequence, trade-off, distinction, or scale being taught. Stop when further explanation would make the concrete implementation the subject.

Prefer a short callout when a concrete operating system, database, runtime, framework, or product merely illustrates general theory. Put the implementation's own architecture in the note that naturally owns it.

## Cross-links

Use repository-local Markdown links according to `AGENTS.md`.

- Prefer turning existing meaningful text into a link.
- Preserve the visible wording when possible.
- Link to the most specific useful section.
- Do not add navigation prose merely to justify a link.
- Do not use a link as a substitute for context the current note genuinely needs.
- Avoid repeatedly linking the same concept within one note.

## Discourage

- Long introductions that delay the concept.
- A bullet for every sentence or a heading for every idea.
- Extended narrative where direct causal explanation would be clearer.
- Repetitive explanations, weak transitions, filler, praise, and generic conclusions.
- Important rules or conclusions buried after lengthy setup.
- Ornamental analogies or case studies that become subjects of their own.
- Silent strengthening, weakening, correction, or reinterpretation of source claims.
- Excessive compression that removes necessary reasoning.
- Excessive detail that crosses the note's natural boundary.
- Generic “Key Takeaways,” “Conclusion,” “Related concepts,” or FAQ sections that merely repeat earlier material.

## Markdown rules

- Use exactly one `#` heading for the note title.
- Keep heading hierarchy logical and do not skip levels.
- Prefer descriptive noun-phrase headings over questions.
- Number headings only when the subject has a real sequence, lifecycle, or ordered dependency.
- Use fenced code blocks with the correct language identifier.
- Define every symbol in an equation and explain its meaning.
- Keep tables concise and causal explanation in prose.
- Never use ASCII-art diagrams.

## Question-driven amendments

When the user asks a question about an existing note and wants the note rewritten so the question would not arise, treat the question as a documentation defect.

1. Find the earliest point where a careful reader would form the question.
2. Identify the missing definition, distinction, state transition, assumption, causal link, or example.
3. Check whether that missing knowledge is owned by the current note or should remain short local context linked to another canonical home.
4. Insert the explanation at the earliest appropriate point using the note's established terminology and depth.
5. Remove or revise nearby wording that becomes repetitive, misleading, or contradictory.
6. Verify that the question no longer requires a disconnected clarification.

Do not append a reactive FAQ unless explicitly requested.

## Final verification

Before finalizing, verify that:

- the edited note still has one clear center of gravity;
- the content remains at the correct abstraction level;
- the mechanism or causal relationship is explicit;
- adjacent implementation or application detail has not taken over the subject;
- duplicated same-level explanations were not introduced;
- terminology, scope, qualifiers, and exceptions remain faithful to the sources;
- prose and structured formatting match the logical shape of the knowledge;
- examples clarify rather than dominate;
- cross-links are natural and point to known targets;
- links, code fences, commands, equations, tables, and Mermaid syntax are valid where applicable;
- no unsupported information or unfinished placeholders remain.

## Output contract

When a target file exists and write access is available, modify it in place rather than pasting a proposed rewrite into chat. Complete and verify the work before producing a natural-language response.

Return a minimal completion record naming the edited files and the substantive architectural or content change. Preserve useful existing material and improve it in place rather than replacing it with a generic rewrite.
