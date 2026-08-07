# Repository Instructions

## Context7 documentation

Use Context7 MCP whenever a request concerns a library, framework, software development kit (SDK), application programming interface (API), command-line interface (CLI), or cloud service. This applies even to familiar technologies because their documentation can change after model training.

Use Context7 for API syntax, setup, configuration, migrations, library-specific debugging, and CLI behavior. Prefer it to web search for library documentation.

Do not use Context7 for general programming concepts, business-logic debugging, code review, refactoring, or standalone scripts that do not depend on a specific library.

Follow this sequence:

1. Call `resolve-library-id` with the library name and the user's full question unless the user supplied an exact `/org/project` ID.
2. Select the best result by exact-name match, relevance, snippet count, source reputation, benchmark score, and version fit. Prefer a version-specific ID when the user names a version. Retry with an alternate spelling or more precise query when the results are weak.
3. Call `query-docs` with the selected library ID and the full question.
4. Base the answer or repository edit on the retrieved documentation.

## Repository purpose

This repository is an Obsidian knowledge base for durable backend-engineering study notes and reference material. It covers technologies, system design, security, networking, operating systems, web APIs, caching, and artificial intelligence engineering. Treat it as a documentation repository, not as an executable application.

## Content organization

- **`Technologies/`:** Languages, frameworks, and infrastructure tools.
    - **`NodeJS/`:** Node.js, Express, authentication, and database integration.
    - **`Golang/`:** Go concepts and patterns.
    - **`Typescript/`:** TypeScript fundamentals and type-system concepts.
    - **`NGINX/`:** Web-server configuration and operation.
- **`Backend Engineering/`:** Communication patterns, execution models, performance, and general engineering patterns.
- **`Security/`:** Information-security concepts and practices.
- **`Networking/`:** Protocols, connection management, and infrastructure concepts.
- **`Web APIs/`:** REST, GraphQL, and API design.
- **`Cache/`:** Caching strategies and Redis patterns.
- **`Operating Systems/`:** Operating-system and systems-level concepts.
- **`AI Engineering/`:** AI-development patterns, including retrieval-augmented generation.

Numbered prefixes indicate a learning sequence. Directories prefixed with `99` contain supplementary material. Follow nearby naming and sequencing conventions.

Before creating a note, search for existing coverage. Extend the most appropriate note when the topic already has a natural home. Inspect nearby notes for terminology, links, depth, and formatting conventions. Files such as `Patterns.md` and `Resilience.md` may provide useful cross-topic context.

## Target document style

Write notes as practitioner handbooks or engineering references. Optimize for scanning, retrieval, and application rather than continuous textbook-style reading.

### Encourage

- Lead with the definition, rule, mechanism, or decision the reader needs.
- Use short, self-contained sections with descriptive headings.
- Keep paragraphs focused on one primary idea.
- Organize explanations as problem → mechanism → consequence → trade-off.
- Express processes as explicit stages, state transitions, or procedures.
- Compare related concepts directly across shared dimensions.
- Surface constraints, assumptions, ownership, state, dependencies, and failure conditions.
- Use labeled bullets such as **Mechanism:**, **Constraint:**, and **Practical implication:** when they improve retrieval.
- Use tables, examples, code, diagrams, and callouts only when they make a decision or mechanism easier to understand.
- Progress from the smallest useful model to variants, edge cases, and operational concerns.
- Preserve important terminology, qualifications, uncertainty, limitations, and implementation-specific variation.
- Use direct, instructional language, active voice, and precise verbs.
- Make each section useful when read independently.

### Discourage

- Long introductions that delay the main point.
- Broad historical, institutional, or motivational framing that does not affect application.
- Dense paragraphs that combine several unrelated ideas.
- Extended narrative when a rule, workflow, comparison, or checklist would be clearer.
- Repetitive transitions, generic conclusions, filler, and ceremonial language.
- Abstract claims about maturity, alignment, strategy, or stakeholders without operational consequences.
- Ornamental analogies or case studies that are longer than the concept they explain.
- Important conclusions buried at the end of a section.
- Mechanical overuse of headings, bullets, tables, callouts, or diagrams.
- Unexplained jargon, vague wording, unsupported superlatives, or invented precision.
- Silent changes to the source's meaning, scope, certainty, or established terminology.

## Markdown conventions

- Use exactly one `#` heading for the note title.
- Use `##` for major reference units and deeper headings only when their content justifies them.
- Do not number headings unless the material has an inherent order, lifecycle, or dependency.
- Open with a concise definition and practical significance. Do not require a fixed number of introductory paragraphs.
- Use paragraphs for causal explanation and bullets for independently scannable ideas.
- Use numbered lists for chronological procedures, algorithms, protocols, and state transitions.
- Use fenced code blocks with the correct language identifier. Keep examples minimal, valid, and relevant.
- Define every symbol in an equation and explain its operational meaning.
- Use tables for concise comparisons across shared dimensions, then interpret the important pattern.
- Use small Mermaid diagrams only when relationships or state transitions are harder to understand in prose.
- Use Obsidian callouts sparingly for genuine caveats, warnings, or implementation variance.

## Source and editing discipline

- Inspect the target file and directly relevant local sources before editing.
- Treat supplied and repository-local material as the primary source of truth.
- Do not invent versions, figures, limits, commands, paths, quotations, or implementation details.
- Qualify claims that vary by platform, version, implementation, jurisdiction, or context.
- Preserve valid internal links and create new links only when the destination is known to exist.
- Add links where the related concept naturally enters the explanation; do not collect them in a generic “See also” section.
- Use paths relative to the current note and update affected links or anchors when moving content.
- Preserve useful existing content. Integrate missing explanations at the earliest point where the reader needs them, then remove nearby repetition or contradiction.

## Editing workflow

1. Inspect the target file and directly relevant sources.
2. Search the vault for overlapping coverage and established terminology.
3. Make the smallest coherent edit that fully resolves the request.
4. Validate links, code fences, heading hierarchy, Mermaid syntax, and verifiable commands or examples.
5. Inspect the final diff and reread the affected section as a first-time reader.
6. Run the repository's Markdown lint workflow when appropriate and resolve introduced findings.

When a user asks a question about an existing note and requests a rewrite, treat the question as a documentation defect. Insert the missing definition, assumption, distinction, state transition, or causal link where the ambiguity first appears. Do not append a reactive FAQ or disconnected clarification.
