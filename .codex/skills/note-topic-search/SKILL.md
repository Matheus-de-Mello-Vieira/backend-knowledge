---
name: note-topic-search
description: Search this Markdown knowledge-base repository for notes about a given topic and return the most relevant existing files. Use when Codex needs to find what the repository already contains about a subject, gather related notes before writing a new one, or answer questions by locating the closest existing material.
---

# Note Topic Search

Use this skill to find existing notes before creating new ones or when answering a question from repository content.

## Workflow

1. Normalize the subject to English before searching:

- Translate the matter to natural technical English because the notes are written in English.
- Preserve acronyms, protocol names, and product names such as `TCP`, `Redis`, `OAuth`, `Wireshark`, and `NGINX`.
- When useful, search with both the original-language term and the English translation.

2. Search filenames first:

```bash
rg --files . | rg "keyword|translation|tool"
```

3. Search note contents next:

```bash
rg -n --glob '*.md' "keyword|translation|synonym|tool" .
```

4. Read only the most promising candidates to confirm relevance.

5. Return the best matches, not an exhaustive dump.

## Search Rules

- Prefer title and filename matches first, then body matches.
- Use close synonyms if the direct term returns little or nothing.
- Prefer notes whose surrounding folder also matches the topic.
- If a note mentions the subject only in passing, rank it below notes centered on that subject.
- If nothing exact exists, return the closest conceptual matches and say that the match is partial.

## Output Format

Respond with:

- top matching notes as repository paths
- a short reason for each match
- confidence: high, medium, or low
- a short gap note if the repository seems not to have a direct note on the subject

Keep the result concise. Usually 3-5 notes is enough.

## Constraints

- Do not create or edit notes unless the user explicitly asks.
- Do not claim a note is relevant without checking at least its filename or a matching excerpt.
- Prefer repository evidence over assumptions.
