---
name: note-home-finder
description: Decide whether a topic already belongs in an existing Markdown note and, if a new note is warranted, choose the most appropriate location for it inside this knowledge-base repository. Use when Codex needs to search the current notes for related material, avoid duplicates, determine whether to reuse an existing note or create a new one, and recommend the best folder and filename based on repository structure and nearby notes.
---

# Note Home Finder

Use this skill before creating a new note when the correct location is not obvious.

## Workflow

1. Normalize the matter into English before searching:

- Translate the topic to natural technical English because this repository's notes are written in English.
- Preserve canonical terms, acronyms, protocol names, and product names such as `TCP`, `NGINX`, `GraphQL`, `OAuth`, `Wireshark`, and `Redis`.
- When useful, search with both the original-language term and the English translation to avoid missing nearby notes.

2. Search existing notes before making any placement decision:

```bash
rg --files . | rg "keyword|translation|tool"
rg -n --glob '*.md' "keyword|translation|synonym|tool" .
```

3. Read only the closest candidate notes to determine whether the topic:

- is already covered directly;
- belongs as a subsection of an existing note;
- deserves a new sibling note near related material;
- has no close cluster and needs a new placement.

4. Inspect the repository structure only after the search results narrow the likely area:

```bash
find . -maxdepth 2 -type d | sort
```

5. Choose the outcome using this priority order:

- Extend an existing note if the matter is clearly a subsection of that note.
- Reuse an existing note if the matter is already covered at the right granularity.
- Place a sibling note in an existing folder if the matter matches that cluster.
- Create a new top-level note only when no existing folder is a clear fit.
- Create a new subfolder only when there are multiple notes expected around the same subtopic.

6. Return a concrete recommendation:

- target path
- whether to reuse an existing note, extend one, or create a new one
- short rationale based on neighboring notes

## Placement Rules

- Prefer semantic fit over literal keyword matching.
- Follow the repository's existing taxonomy first: `Networking`, `Security`, `Web APIs`, `Technologies`, `Backend Engineering`, `Operating Systems`, `Cache`, `AI Engineering`.
- Reuse existing numbered sequences when the target folder already uses ordered filenames.
- Match nearby naming style. If siblings are English, keep the filename in English unless the repository area is clearly using another convention.
- Generate the recommended filename in English.
- Do not create duplicate notes when an existing note already covers the subject at the right granularity.
- If the matter overlaps multiple areas, choose the folder where a future reader would most likely look first.
- Treat note discovery as mandatory. Do not recommend a new file before checking for related notes.

## Decision Heuristics

- Protocols, network behavior, traffic analysis, routing, switching, and infrastructure operations usually belong under `Networking/`.
- Authentication, authorization, cryptography, threats, hardening, and governance usually belong under `Security/`.
- HTTP, REST, GraphQL, API lifecycle, and service contracts usually belong under `Web APIs/`.
- Language- or tool-specific notes usually belong under `Technologies/`.
- Cross-cutting operational backend concerns such as performance debugging and service communication may fit `Backend Engineering/`.

Use these heuristics only after checking whether a closer existing cluster already exists.

## Output Format

Respond with:

- outcome: reuse existing note, extend existing note, or create new note
- recommended path
- confidence: high, medium, or low
- rationale in 1-3 sentences
- alternatives only if the decision is ambiguous

## Constraints

- Do not create or move files unless the user explicitly asks for that action.
- Do not write note contents when the user only asked for placement.
- If the matter already belongs inside an existing note, say so directly instead of forcing a new file.
