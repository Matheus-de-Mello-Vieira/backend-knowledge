---
name: note-home-finder
description: Decide whether a topic already belongs in an existing Markdown note by using the qmd MCP index, and if a new note is warranted, choose the most appropriate location inside this knowledge-base repository. Use when Codex needs to search current notes for related material, avoid duplicates, determine whether to reuse or extend an existing note, or recommend the best folder and filename based on repository structure and nearby notes.
---

# Note Home Finder

Use this skill before creating a new note when the correct location is not obvious. Prefer qmd MCP search for discovery because placement depends on both exact matches and semantic neighbors.

## Workflow

1. Normalize the matter before searching:

- Translate the topic to natural technical English because this repository's notes are written in English.
- Preserve canonical terms, acronyms, protocol names, and product names such as `TCP`, `NGINX`, `GraphQL`, `OAuth`, `Wireshark`, and `Redis`.
- When useful, search with both the original-language term and the English translation to avoid missing nearby notes.

2. Check qmd status if index freshness or availability is uncertain:

- Use `mcp__qmd__status` to confirm the repository collection, document count, vector index, and pending embeddings.
- If qmd is unavailable, stale, or clearly missing files, fall back to `rg` under "Fallback Search".

3. Search qmd before making any placement decision:

- Use `lex` first for exact topic names, acronyms, commands, protocol names, product names, and likely filenames.
- Add `vec` for semantic neighbors that may not share the same wording.
- Add `hyde` for broad or nuanced topics where a 50-100 word hypothetical note description would improve recall.
- Use `intent` to disambiguate overloaded terms and to name the likely domain, such as security, networking, cache, or backend performance.
- Keep `limit` around 8-12 because placement needs neighboring notes, not just the single best match.

Example:

```json
{
  "searches": [
    { "type": "lex", "query": "\"OAuth\" authorization token refresh" },
    { "type": "vec", "query": "where should a note about OAuth token refresh behavior fit in this backend knowledge base" },
    { "type": "hyde", "query": "A note about OAuth token refresh explains access tokens, refresh tokens, expiration, token rotation, security risks, authorization flows, and how backend services should handle renewal failures." }
  ],
  "intent": "choose a home for a backend security or web API note",
  "limit": 10
}
```

4. Retrieve and compare the closest candidates:

- Use `mcp__qmd__get` on the best paths or docids returned by qmd.
- Read enough of each candidate to decide whether the topic is already covered, should become a subsection, or should become a sibling note.
- Prefer repository paths in the final recommendation; docids are only intermediate lookup handles.

5. Use `rg` as a fallback or precision check:

```bash
rg --files . | rg "keyword|translation|tool"
rg -n --glob '*.md' "keyword|translation|synonym|tool" .
```

6. Inspect repository structure only after qmd or `rg` narrows the likely area:

```bash
find . -maxdepth 2 -type d | sort
```

7. Determine whether the topic:

- is already covered directly;
- belongs as a subsection of an existing note;
- deserves a new sibling note near related material;
- has no close cluster and needs a new placement.

8. Choose the outcome using this priority order:

- Extend an existing note if the matter is clearly a subsection of that note.
- Reuse an existing note if the matter is already covered at the right granularity.
- Place a sibling note in an existing folder if the matter matches that cluster.
- Create a new top-level note only when no existing folder is a clear fit.
- Create a new subfolder only when there are multiple notes expected around the same subtopic.

9. Return a concrete recommendation:

- target path
- whether to reuse an existing note, extend one, or create a new one
- short rationale based on neighboring notes

## Query Patterns

- Direct duplicate check: use `lex` with quoted canonical terms, then retrieve likely matches.
- Placement by concept: use `vec` plus a small `lex` query for expected vocabulary.
- Broad topic: use `lex` + `vec` + `hyde` and compare several neighboring notes.
- Portuguese or mixed-language request: search the English translation, and include original terms in `lex` if they may appear verbatim.
- Ambiguous term: use `intent`, `lex` exclusions, or both.
- Sparse qmd results: broaden terms, inspect likely folders with `rg --files`, then use raw content search.

## Placement Rules

- Prefer semantic fit over literal keyword matching.
- Prefer qmd reranked neighbors when retrieved content confirms they represent the local cluster.
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
- Do not recommend a new path without checking qmd results, retrieved note content, filename evidence, or matching excerpts for nearby notes.
