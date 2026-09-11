# Publication writing policy

This policy governs visible consolidated Markdown and preserves evidence/publication constraints specific to consolidation.

For **repository-integrated mode**, prose structure is delegated to `$note-writer`; note ownership/scope are produced by `$note-home-finder` and `$note-boundary-analyzer`; approved structural moves use `$note-content-mover`. Do not maintain competing repository writing, placement, boundary, or mutation policies in this file.

For **standalone mode**, apply the rules below directly.

## Instruction priority

1. The user's explicit scope, audience, purpose, and output-format requirements.
2. Factual accuracy, complete semantic preservation, and safety.
3. Accepted conflict decisions, qualifiers, dependencies, limitations, exceptions, and uncertainty.
4. Mandatory writing rules below.
5. Preferred writing practices below.

## Meaning and evidence

- Preserve every supported fact, scope condition, dependency, limitation, exception, uncertainty, warning, rationale, alternative, historical state, and open question.
- Do not invent facts, repair missing evidence with general knowledge, or silently strengthen, weaken, generalize, narrow, or reinterpret a claim.
- Preserve established terminology unless the evidence proves terms are interchangeable.
- State unresolved required information visibly rather than filling material gaps with assumptions.

## Standalone exposition

- Write for a reader who cannot access the evidence inputs or work artifacts.
- State the actual fact, example, definition, comparison, or reasoning.
- Define unfamiliar domain-specific terms at first substantive use unless the audience can reasonably be expected to know them.
- Keep examples close to the concept they illustrate.

## Information order

- Present the main concept or conclusion early.
- Keep each paragraph focused on one primary purpose while preserving causal continuity.
- Use descriptive headings that reflect real conceptual units.
- Keep definitions, exceptions, warnings, and examples adjacent to the concepts they modify.

## Operational expression

- Use numbered stages when order matters.
- State responsibilities, inputs, outputs, dependencies, constraints, assumptions, and failure modes when they materially affect the subject.
- Compare closely related concepts directly using shared dimensions.
- Use precise verbs and active voice when the responsible actor is relevant.

## Concision and completeness

- Remove duplicated meaning, filler, ceremonial framing, weak transitions, and commentary about the document itself.
- Use the shortest wording that preserves all necessary substance.
- Do not remove scope, nuance, uncertainty, limitations, dependencies, exceptions, examples, or rationale merely for brevity.
- Do not add broad historical or motivational framing unless it materially changes understanding.

## Formatting

- Use prose for causal explanation.
- Use bullets for genuinely parallel information.
- Use numbered lists when sequence is semantic.
- Use tables only for repeated comparison dimensions.
- Use diagrams only when relationships are materially clearer visually.
- Do not fragment short explanations into many headings or one-item lists.
- Preserve code, commands, equations, links, and external references accurately.

## Repository-integrated mode

Repository publication must additionally:

1. follow the accepted `$note-home-finder` placement;
2. follow the accepted `$note-boundary-analyzer` scope distribution;
3. use `$note-content-mover` only for approved structural relocation of existing durable content;
4. use `$note-writer` for note prose and structure;
5. use `$markdown-link-normalizer` for mechanical link handling;
6. preserve complete source-unit coverage **across the publication set** without requiring duplicate full explanations in multiple destination notes.

A destination note should be complete about its own subject and abstraction level. Give enough neighboring context for local comprehension, but do not duplicate a complete prerequisite or adjacent explanation merely to make every note independently exhaustive.

## Edge cases

- When brevity conflicts with evidence completeness, preserve completeness and improve organization.
- When evidence is semantically repetitive, merge repeated wording and preserve the semantic union once.
- When two terms appear equivalent but the evidence does not prove equivalence, retain both and explain the uncertainty.
- When no reliable information order is evident, group by topic and place rules before examples and exceptions.
