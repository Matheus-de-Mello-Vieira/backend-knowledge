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

This repository is an Obsidian knowledge base for durable backend-engineering study notes and reference material. Treat it as a connected knowledge system, not as a collection of independent articles and not as an executable application.

The repository should preserve conceptual ownership: each subject has a natural home, neighboring notes provide different abstraction levels or reading intents, and links connect those layers without requiring duplicate full explanations.

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
- **`Operating Systems/`:** Foundational operating-system and systems-level mechanisms. Keep the core notes as implementation-agnostic as the subject permits; concrete systems may illustrate the theory, while implementation detail belongs in implementation-specific notes.
- **`AI Engineering/`:** AI-development patterns, including retrieval-augmented generation.

Numbered prefixes indicate a learning sequence. Directories prefixed with `99` contain supplementary material. Follow nearby naming and sequencing conventions.

Before creating a note or adding substantial new material, search for existing coverage. Extend the natural canonical home when one exists. Inspect nearby notes for terminology, abstraction level, links, depth, and formatting conventions.

## Knowledge architecture

### Note ownership

Every note has a **center of gravity**: one stable subject explained for one primary reading intent and at an appropriate level of abstraction.

Before a substantial edit, determine:

- what concept is actually being explained;
- which note naturally owns that concept;
- at what abstraction level the explanation belongs;
- which adjacent concepts are required only as local context;
- which details are examples, implementations, or applications that have another natural home.

Prefer one canonical explanation of a concept **per sense and abstraction level**.

A topic may legitimately appear in several notes when each occurrence serves a different purpose. For example, virtual memory may be explained as an OS mechanism, discussed as a database-performance dependency, and referenced as a security-isolation primitive. Do not duplicate the same complete explanation at the same level merely because several notes mention the term.

### Abstraction boundaries

Distinguish neighboring layers when they answer different questions:

- **Theory:** why a concept or mechanism exists and which general properties follow from it.
- **Mechanism:** how components, state, data, or transitions produce the behavior.
- **Implementation:** how a concrete operating system, database, runtime, framework, library, or product realizes or exposes the mechanism.
- **Application:** how another system uses the mechanism and which engineering consequences or trade-offs follow.

A note may briefly cross into an adjacent layer when that context is necessary to explain its own subject. Stop when the adjacent layer becomes the subject of the explanation.

Concrete examples are subordinate to the concept being taught. Include only enough implementation detail to expose the mechanism, distinction, consequence, or trade-off being illustrated.

### Local sufficiency without duplication

A note must explain its own subject completely at its chosen abstraction level. It does **not** need to reproduce complete prerequisite or neighboring explanations merely to be independently exhaustive.

Give enough local context for the current argument to remain understandable, then use a natural inline link when another note owns deeper or adjacent material.

Use this boundary test:

> If removing the material would make the reader understand this note's subject less well, it is probably local context. If removing it would only make the reader know less about another subject, that material probably belongs in another note.

### Cross-note cohesion

Cross-links represent conceptual relationships, not navigation decoration.

- Turn existing meaningful text into a link when possible.
- Preserve the visible wording instead of rewriting prose merely to introduce navigation.
- Prefer the first meaningful occurrence of a concept.
- Link only when the destination provides useful deeper, prerequisite, implementation, contrasting, or adjacent context.
- Prefer the most specific stable section anchor.
- Do not repeatedly link the same concept throughout one note.
- Do not add phrases such as “see more,” “read more,” “for more information,” “this is explained in,” or similar navigation language merely to create a link.
- A link supplements local sufficiency; it does not replace facts that the current note genuinely owns.

## Target document style

Write primarily as concise technical study notes: coherent explanation first, structured decomposition where the knowledge is genuinely parallel or procedural.

### Encourage

- Lead with the definition, mechanism, distinction, or question the section exists to explain.
- Explain causally: problem → mechanism → consequence → trade-off.
- Connect facts instead of merely listing them.
- Keep paragraphs focused, but allow several related sentences when they form one causal explanation.
- Use descriptive bullets for parallel properties, components, alternatives, responsibilities, states, or mechanisms.
- Use nested bullets for consequences, qualifications, submechanisms, or details owned by the parent item.
- Use numbered lists when sequence itself matters.
- Compare related concepts across shared dimensions when comparison clarifies the distinction.
- Progress from the smallest useful model to the depth naturally owned by the current note.
- Preserve important terminology, qualifications, uncertainty, limitations, and implementation-specific variation.
- Use direct, precise language and active voice where appropriate.

### Discourage

- Turning every sentence into a bullet or every idea into a heading.
- Long introductions that delay the concept.
- Dense paragraphs that combine unrelated topics.
- Repetitive transitions, filler, ceremonial conclusions, and generic “Key Takeaways” sections.
- Operational or implementation detail that crosses the note's natural boundary without clarifying its subject.
- Examples or case studies that become longer than the mechanism they exist to illustrate.
- Important conclusions buried after lengthy setup.
- Mechanical overuse of tables, diagrams, callouts, or formatting.
- Unexplained jargon, vague wording, unsupported superlatives, invented precision, or silent changes in scope or certainty.

## Markdown conventions

- Use exactly one `#` heading for the note title.
- Use `##` for major conceptual units and deeper headings only when the content justifies them.
- Do not number headings unless the material has an inherent order, lifecycle, or dependency.
- Use paragraphs for causal explanation and bullets for genuinely parallel or independently scannable ideas.
- Use numbered lists for chronological procedures, algorithms, protocols, lifecycles, and state transitions.
- Use fenced code blocks with the correct language identifier. Keep examples minimal, valid, and relevant.
- Define every symbol in an equation and explain its operational meaning.
- Use tables only for concise comparison across repeated dimensions, then explain the consequential pattern in prose.
- Use small Mermaid diagrams only when relationships, branches, loops, topology, or state transitions are materially clearer visually.
- Never use ASCII-art diagrams.
- Use Obsidian callouts for secondary material such as examples, warnings, terminology clarifications, implementation-specific observations, practical inspection tips, or architectural stories. The main body should retain ownership of the theory.

## Examples and implementation detail

Examples clarify the current concept; they do not transfer ownership of the example system into the current note.

Stop an example when explaining it further would require teaching the concrete system as a subject in its own right. Put deeper implementation material in the note that owns that system and link existing prose naturally when useful.

For foundational notes such as `Operating Systems/`, prefer durable and implementation-agnostic mechanisms. Linux, Windows, PostgreSQL, Docker, Redis, NGINX, or other concrete systems may appear as examples, but their implementation architecture belongs in the corresponding implementation or technology notes.

## Source and editing discipline

- Inspect the target file and directly relevant repository sources before editing.
- Treat supplied and repository-local material as the primary source of truth.
- Do not invent versions, figures, limits, commands, paths, quotations, or implementation details.
- Qualify claims that vary by platform, version, implementation, jurisdiction, or context.
- Preserve valid internal links and create new links only when the destination is known to exist.
- Use paths relative to the current note and update affected links or anchors when moving content.
- Preserve useful existing content. Integrate missing explanations where the reader first needs them, then remove nearby repetition or contradiction.
- Make the smallest coherent edit that resolves the request **after** determining the correct conceptual home.

## Skill architecture

Codex skills in `.codex/skills/` form a capability hierarchy.

- **Lower-level skills own one reusable capability.** Examples include repository retrieval, note placement, boundary analysis, prose writing, content movement, link normalization, and lint repair.
- **Higher-level skills orchestrate lower-level skills.** They define sequencing, handoffs, and acceptance criteria rather than restating delegated implementation procedures.
- **One capability has one canonical owner.** If a lower-level skill owns a task, a higher-level skill must invoke or inject that skill rather than copying its detailed rules.
- **Dependencies flow downward.** Lower-level skills must not invoke higher-level workflows that depend on them.
- **Repository-wide invariants live here.** Skills may reference these rules but should not maintain competing copies of repository architecture policy.
- **Default writing behavior lives in `.codex/model_instructions.md` and `$note-writer`.** Composite skills delegate writing instead of inventing their own style system.
- Composite skills should make their boundaries explicit with **Owns**, **Delegates**, and **Must not** responsibilities when applicable.

The intended hierarchy is:

```text
Repository policy
├── AGENTS.md
└── .codex/model_instructions.md

Level 1 — Mechanical and retrieval primitives
├── note-topic-search
├── markdown-link-normalizer
└── markdownlint-fix

Level 2 — Semantic decision primitives
├── note-home-finder
│   └── note-topic-search
└── note-boundary-analyzer

Level 3 — Mutation primitives
├── note-writer
└── note-content-mover

Level 4 — Note workflows
├── note-authoring
│   ├── note-home-finder
│   ├── note-boundary-analyzer
│   ├── note-writer
│   ├── markdown-link-normalizer
│   └── markdownlint-fix
├── note-refactor
│   ├── note-home-finder
│   ├── note-boundary-analyzer
│   ├── note-content-mover
│   ├── note-writer
│   ├── markdown-link-normalizer
│   └── markdownlint-fix
└── note-content-boundary
    └── compatibility wrapper for note-refactor

Level 5 — Repository workflows
└── markdown-consolidator
    └── delegates repository placement, boundaries, writing/mutation, and link mechanics
        to the same lower-level capabilities
```

## Editing workflow

For small local corrections, avoid unnecessary orchestration. Inspect the target, make the conservative edit, and verify it.

For substantial additions, new sections, note creation, or cross-note refactors:

1. Search existing coverage using the repository search capability.
2. Determine the canonical home and reading intent.
3. Check abstraction and content boundaries.
4. Write or move only the material owned by each destination.
5. Add natural cross-links where another note provides useful deeper context.
6. Validate links, code fences, heading hierarchy, Mermaid syntax, and verifiable commands or examples.
7. Inspect the final diff and reread affected sections as a first-time reader.
8. Run the repository's Markdown lint workflow when appropriate and resolve introduced findings.

When a user asks a question about an existing note and requests a rewrite, treat the question as a documentation defect. Insert the missing definition, assumption, distinction, state transition, or causal link where the ambiguity first appears. Do not append a reactive FAQ or disconnected clarification.

## Repository cohesion verification

Before finalizing a substantial edit, verify:

- Does each edited note still have one clear center of gravity?
- Is every substantial concept explained in its canonical home at the intended abstraction level?
- Did the edit introduce implementation detail above its natural layer?
- Did an example grow beyond what is necessary to clarify the current concept?
- Did the edit duplicate an explanation already present elsewhere at the same abstraction level?
- Can duplicated background be reduced to sufficient local context plus a natural inline link?
- Would any new subsection be independently valuable under another note's subject?
- Are cross-links expressing genuine conceptual relationships rather than compensating for poor placement?
