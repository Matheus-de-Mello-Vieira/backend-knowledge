---
name: note-topic-search
description: Search this Markdown knowledge-base repository with the qmd MCP index and return the most relevant existing notes for a topic. Use when Codex needs to find what the repository already contains about a subject, gather related notes before writing a new one, answer questions by locating the closest existing material, or combine keyword and semantic search over the notes.
---

# Note Topic Search

Use this skill to find existing notes before creating new ones or when answering a question from repository content. Prefer qmd MCP search because it combines lexical, semantic, and reranked retrieval over the indexed knowledge base.

## Workflow

1. Normalize the subject before searching:

- Translate the matter to natural technical English because the notes are written in English.
- Preserve acronyms, protocol names, and product names such as `TCP`, `Redis`, `OAuth`, `Wireshark`, and `NGINX`.
- When useful, search with both the original-language term and the English translation.

2. Check qmd status if index freshness or availability is uncertain:

- Use `mcp__qmd__status` to confirm collections, document counts, and health.
- If qmd is unavailable, stale, or clearly missing files, fall back to `rg` under "Fallback Search".

3. Search qmd with typed sub-queries:

- Use `lex` first for exact terms, acronyms, filenames, commands, error names, protocol names, or quoted phrases.
- Add `vec` for conceptual matches, synonyms, and topics that might be expressed with different vocabulary.
- Add `hyde` for broad or nuanced topics where a 50-100 word hypothetical answer would improve recall.
- Put the strongest sub-query first because qmd weights it higher.
- Use `intent` to disambiguate overloaded terms, such as `performance` in backend systems versus UI metrics.
- Keep `limit` around 5-10 unless the user asks for a broad survey.

Example:

```json
{
  "searches": [
    { "type": "lex", "query": "\"connection pool\" timeout postgres" },
    { "type": "vec", "query": "database connection pool exhaustion under load" },
    { "type": "hyde", "query": "Connection pool exhaustion happens when all database connections are busy and new requests wait or fail. Notes may discuss max open connections, timeouts, queueing, Postgres, transactions, and load-related latency." }
  ],
  "intent": "backend database performance notes",
  "limit": 8
}
```

4. Retrieve and confirm candidates:

- Use `mcp__qmd__get` on the best paths or docids returned by qmd.
- Read only enough lines to verify whether the note is centered on the subject or only mentions it in passing.
- Prefer repository paths in the final answer; docids are only an intermediate lookup handle.

5. Use `rg` only as a fallback or precision check:

```bash
rg --files . | rg "keyword|translation|tool"
rg -n --glob '*.md' "keyword|translation|synonym|tool" .
```

6. Return the best matches, not an exhaustive dump.

## Query Patterns

- Exact named topic: use one `lex` query with quoted phrases and important acronyms.
- Conceptual topic: use `vec`, then add a small `lex` query for likely vocabulary.
- Portuguese or mixed-language request: search the English translation, and include original terms in `lex` when they may appear verbatim.
- Ambiguous term: use `intent`, exclusions in `lex`, or both.
- Sparse results: broaden `lex`, add `vec`, then add `hyde`; if still sparse, use `rg` to check filenames and raw text.

## Search Rules

- Prefer title and filename matches first, then body matches.
- Prefer qmd reranked results when they are confirmed by retrieved excerpts.
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
- Do not claim a note is relevant without checking qmd result snippets, retrieved content, filename evidence, or a matching excerpt.
- Prefer repository evidence over assumptions.
