# Publication writing policy

This policy governs the visible consolidated Markdown. Apply it together with the evidence, decision, and lifecycle contracts.

## Instruction priority

Resolve competing instructions in this order:

1. The user's explicit scope, audience, purpose, and output-format requirements.
2. Factual accuracy, complete semantic preservation, standalone exposition, and safety.
3. Accepted conflict decisions, qualifiers, dependencies, limitations, exceptions, and uncertainty.
4. Mandatory writing rules in this policy.
5. Preferred writing practices in this policy.
6. Optional presentation techniques.

A lower-priority instruction never overrides a higher-priority one. When two instructions at the same level conflict, choose the option that preserves more meaning and makes the result easier for the intended audience to use. Record unresolved conflicts as validator findings instead of improvising a compromise.

## Instruction strength

- **Mandatory** means the publication must comply unless a higher-priority instruction prevents compliance.
- **Preferred** means apply the practice when it improves the current document without violating a mandatory rule.
- **Optional** means use the technique only when it clearly improves comprehension or retrieval.

Do not convert preferred or optional practices into rigid universal formatting rules.

## Mandatory rules

### Meaning and evidence

- Preserve every supported fact, scope condition, dependency, limitation, exception, uncertainty, warning, rationale, alternative, historical state, and open question.
- Do not invent facts, repair missing evidence with general knowledge, or silently strengthen, weaken, generalize, narrow, or reinterpret a claim.
- Preserve established terminology unless the sources use true synonyms for the same concept. When terms differ in meaning, retain the distinction and define it.
- State missing required information visibly as `Information unavailable: <specific missing item>` or `To be confirmed: <specific unresolved item>`. Never hide the gap or fill it with a material assumption.
- Make only low-risk editorial assumptions, such as heading capitalization or list punctuation, when they cannot alter meaning. Do not make factual, causal, procedural, legal, technical, or numerical assumptions.

### Reader independence

- Write for a reader who cannot access the inputs or work artifacts.
- State the actual fact, example, definition, comparison, or reasoning. Do not refer to “the material,” “the source,” “the example above,” or another unavailable context.
- Define an unfamiliar or domain-specific term at or immediately after its first substantive use, unless the intended audience can reasonably be expected to know it.
- Present each example close to the concept it illustrates. Include the setup, relevant inputs or actors, mechanism or steps, outcome, and the reason the example matters.

### Information order

- Present the main point or operative conclusion in the first substantive paragraph of the document and, when practical, in the first paragraph of each major section.
- Order information by reader need: conclusion or definition, governing rules, details, exceptions, examples, dependencies, limitations, and references. Use another order only when the subject requires it.
- Keep each paragraph focused on one primary purpose. Split a paragraph when it changes topic, decision, stage, responsibility, or exception.
- Use descriptive headings that identify the subject or decision represented by the section. Avoid generic headings such as `Details`, `Information`, `Miscellaneous`, or `Other` unless qualified by a concrete subject.
- Keep definitions, exceptions, warnings, and examples adjacent to the rules or concepts they modify.

### Operational expression

- Express a sequence as numbered stages or steps when order matters.
- Express requirements as explicit rules, checks, conditions, or decision criteria. Do not bury mandatory behavior inside descriptive narrative.
- State responsibilities with an actor and an action. State inputs, outputs, dependencies, constraints, assumptions, and failure modes where they affect execution.
- Compare closely related concepts directly using shared dimensions. Use a compact table only when it makes those dimensions easier to compare than parallel prose.
- Use precise verbs. Prefer active voice when the responsible actor is known and relevant. Use passive voice when the actor is unknown, irrelevant, or intentionally omitted.

### Concision and completeness

- Remove duplicated meaning, filler, ceremonial framing, weak transitions, and commentary about the document itself.
- Use the shortest wording that preserves all necessary substance. Concision never permits removal of scope, nuance, uncertainty, limitations, dependencies, exceptions, examples, or rationale.
- Do not add broad historical, institutional, motivational, strategic, alignment, maturity, stakeholder, or “best practice” framing unless it changes a concrete decision or action.
- Do not use vague directives or claims such as `make it better`, `improve the flow`, `make it engaging`, `align stakeholders`, or `follow best practices` without operational criteria.

### Formatting

- Use lists, tables, blockquotes, callouts, and examples only when they improve comprehension, comparison, execution, or retrieval.
- Do not fragment a short explanation into many headings or one-item lists.
- Preserve code, commands, tables, equations, links, and external references accurately. Change formatting only when the meaning and behavior remain identical.
- Follow the requested output format. When no format is specified, use conventional Markdown with a single H1 title and a logical heading hierarchy.

## Preferred practices

Apply these when they fit the subject and audience:

- Use short, focused paragraphs, commonly two to five sentences.
- Put decision-relevant information before background.
- Use parallel grammatical structure for related rules and list items.
- Use one canonical term consistently and mention aliases once near the first use.
- Use a direct comparison table for concepts that share at least two meaningful dimensions.
- Use concise examples rather than analogies when an example can demonstrate the actual decision or mechanism.
- Use an appendix only for complete in-scope information that would interrupt the main operational sequence.
- Match technical depth, terminology, and assumed knowledge to the intended audience.

## Optional techniques

Use only when they add clear value:

- A brief overview for long documents.
- A table of contents for documents with many major sections.
- Callouts for high-impact warnings, constraints, or irreversible actions.
- Decision tables for multi-condition choices.
- Appendices for historical variants, exhaustive reference data, or secondary implementation detail.

## Edge cases

- When brevity conflicts with completeness, preserve completeness and improve organization instead of deleting information.
- When a source is verbose but semantically repetitive, merge repeated wording and preserve the full semantic union once.
- When two source terms appear equivalent but the evidence does not prove equivalence, retain both terms and explain the uncertainty.
- When the requested audience lacks prerequisite knowledge, add only source-supported definitions and context. Mark unsupported prerequisites as unavailable rather than inventing them.
- When no reliable information order is evident, group by topic and place rules before examples and exceptions.

## Repository-note writing

These rules apply only in repository-integrated mode.

### Mandatory

- Keep each destination note centered on one stable subject and reading intent.
- Preserve established terminology and heading style unless the reviewed plan requires a change.
- Make each note understandable without access to evidence files or neighboring notes.
- Introduce a local link with enough nearby prose to explain the relationship.
- Do not use a link as a substitute for required facts assigned to the current note.
- Do not write source-oriented phrases such as “the material states” or assume the reader saw an unavailable example.
- Do not add generic “Related” sections when links belong naturally near the concepts they connect.

### Preferred

- Link directly to the relevant heading when that improves retrieval and the heading is stable.
- Place broader-context or prerequisite links near the first point where the dependency matters.
- Compare closely related notes or concepts directly when the distinction affects navigation or use.

### Optional

- Add a compact “See also” section only when several useful relationships do not fit naturally into the body.
- Repeat a small amount of context across notes when the integration plan records the repetition and it is required for local comprehension.
