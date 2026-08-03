# Repository Instructions

## Context7 documentation

Use Context7 MCP to fetch current documentation whenever a request concerns a library, framework, software development kit (SDK), application programming interface (API), command-line interface (CLI), or cloud service. This requirement applies even to familiar tools such as React, Next.js, Prisma, Express, Tailwind CSS, Django, and Spring Boot because their documentation can change after model training.

Use Context7 for API syntax, configuration, setup, version migrations, library-specific debugging, and CLI usage. Prefer it to web search for library documentation.

Do not use Context7 for general programming concepts, business-logic debugging, code review, refactoring, or scripts written from scratch without a library-specific question.

Follow this retrieval sequence:

1. Call `resolve-library-id` with the library name and the user's full question unless the user supplied an exact `/org/project` library ID.
2. Select the best result by exact name match, relevance, snippet count, source reputation, and benchmark score. Prefer version-specific IDs when the user names a version. If the results are weak, retry with an alternate spelling or a more precise query.
3. Call `query-docs` with the selected library ID and the user's full question rather than isolated keywords.
4. Base the answer or repository edit on the retrieved documentation.

## Repository purpose

This repository is a personal backend-engineering knowledge base organized as an Obsidian vault. It contains durable study notes and reference material about backend technologies, system design, security, networking, operating systems, web APIs, caching, and artificial intelligence engineering. Treat it as a documentation repository rather than an executable application.

## Content organization

- **`Technologies/`:** Notes about specific languages, frameworks, and infrastructure tools.
    - **`NodeJS/`:** Node.js fundamentals, Express, authentication, and database integration.
    - **`Golang/`:** Go concepts and patterns.
    - **`Typescript/`:** TypeScript fundamentals and type-system concepts.
    - **`NGINX/`:** Web-server configuration and operation.
- **`Backend Engineering/`:** Communication patterns, execution models, performance analysis, and general engineering patterns.
- **`Security/`:** Information-security concepts and practices.
- **`Networking/`:** Protocols, connection management, and infrastructure concepts.
- **`Web APIs/`:** API design, including REST and GraphQL.
- **`Cache/`:** Caching strategies and Redis patterns.
- **`Operating Systems/`:** Operating-system and systems-level concepts.
- **`AI Engineering/`:** AI-development patterns, including retrieval-augmented generation.

Numbered file or directory prefixes indicate a learning sequence. Directories prefixed with `99` contain supplementary or miscellaneous material. Follow the existing sequence and nearby naming conventions when adding content.

Before creating a note, search for existing coverage in the repository. Extend the most appropriate existing note when the topic already has a natural home, and inspect nearby notes for terminology, links, depth, and formatting conventions. Core files such as `Patterns.md` and `Resilience.md` may provide useful cross-topic context.

## Writing principles

Write self-contained explanations for someone actively studying backend engineering.

- **Define before elaborating:** Introduce each central concept in plain language before using its terminology.
- **Explain causally:** Prefer problem → mechanism → consequence → optimization → trade-off over disconnected facts.
- **Progress from simple to advanced:** Begin with the smallest useful example, then introduce variants, failure paths, and operational concerns.
- **Connect theory to practice:** Pair conceptual explanations with realistic examples, verified commands, code, diagrams, or calculations when they materially improve understanding.
- **Expose constraints:** Explain where state lives, who owns it, what changes over time, and where latency, memory, contention, complexity, or risk enters.
- **Cover boundaries:** Include relevant trade-offs, failure modes, edge cases, and implementation-specific variation.
- **Avoid unsupported precision:** Do not invent versions, figures, limits, commands, paths, quotations, or behavior. Qualify claims that vary by platform or implementation.

Use direct, instructional language and active verbs. Keep the writing note-agnostic: explain the subject itself instead of saying “this note explains” or “in this section.” Avoid filler, generic conclusions, unexplained jargon, and vague words such as “things” or “stuff.”

## Markdown conventions

- Use exactly one `#` heading for a note title, `##` for major sections, and deeper headings only when their content justifies them.
- Do not number headings unless the material has an inherent order, progression, lifecycle, or dependency.
- Open with a clear definition and establish why the subject matters.
- Use paragraphs for causal explanations and bullets for related, independently scannable ideas.
- Prefer labeled bullets such as **Constraint:**, **Mechanism:**, and **Practical implication:** when the label improves navigation.
- Use numbered lists for chronological procedures, protocols, algorithms, or state transitions.
- Use fenced code blocks with the correct language identifier. Keep examples minimal, valid, and relevant.
- Define every symbol in an equation and explain its operational meaning.
- Use tables for concise comparisons across shared dimensions. Interpret the important pattern after the table.
- Use small Mermaid diagrams when relationships, pipelines, or state transitions are harder to understand in prose.
- Use Obsidian callouts sparingly for genuine caveats, warnings, or implementation variance.

Preserve useful existing content when editing. Integrate missing explanations at the earliest point where a reader would need them, then remove nearby repetition or contradictions.

## Cross-references

Add links where a related concept naturally enters the explanation rather than collecting links in a generic “Related concepts” or “See also” section.

- Use paths relative to the current note and confirm that every target exists.
- Preserve valid internal links when revising content.
- Follow the vault's existing Markdown-link conventions and directory structure.
- Prefer neutral wording, such as “For tokenization mechanics, see …,” over references to “this note” or “that note.”
- Update affected links and anchors when moving or renaming content.

## Editing workflow

1. Inspect the target file and all directly relevant local sources before drafting.
2. Search the vault for overlapping coverage and established terminology.
3. Make the smallest coherent edit that fully resolves the request; avoid leaving duplicated explanations in multiple notes.
4. Validate links, code fences, heading hierarchy, Mermaid syntax, and any commands or code examples that can be checked locally.
5. Inspect the final diff and reread the surrounding material as a first-time reader.
6. Run the repository's Markdown lint workflow when appropriate and resolve introduced findings.

When a user asks a question about an existing note and requests a rewrite, treat the question as a documentation defect. Insert the missing definition, assumption, distinction, or causal link where the ambiguity first arises instead of appending a reactive FAQ or disconnected clarification.
