---
name: note-topic-search
description: Search this Markdown knowledge-base repository and return the most relevant existing notes for a topic. This is the canonical repository-retrieval primitive used by higher-level note skills. Use it to discover exact coverage and semantic neighbors; do not make placement or editing decisions here.
---

# Note Topic Search

This skill owns **repository topic retrieval**. Higher-level skills such as `$note-home-finder` must delegate search mechanics here instead of duplicating qmd or fallback-search procedures.

## Capability boundary

This skill may:

- normalize a topic into useful search terms;
- search the qmd MCP index;
- retrieve and confirm candidate notes;
- report exact and semantic matches.

This skill must not:

- decide the canonical home of new material;
- decide whether material should be split;
- decide how much content belongs in a target note;
- create, move, or edit notes.

Those decisions belong to higher-level semantic or workflow skills.

## Workflow

1. Normalize the subject:

- Translate the matter to natural technical English because the notes are written in English.
- Preserve canonical terms, acronyms, protocol names, commands, and product names.
- When useful, search with both the original-language term and the English translation.

2. Check qmd status when index freshness or availability is uncertain.

3. Search qmd with typed subqueries:

- use `lex` for exact terms, filenames, commands, acronyms, protocol names, and quoted phrases;
- use `vec` for conceptual matches and synonyms;
- use `hyde` for broad or nuanced topics where a hypothetical description improves recall;
- use `intent` to disambiguate overloaded terms;
- keep the result set focused, normally around 5–10 candidates.

4. Retrieve the strongest candidates and confirm whether each note is centered on the subject or only mentions it in passing.

5. Use `rg` only as a fallback or precision check when qmd is unavailable, stale, or clearly incomplete:

```bash
rg --files . | rg "keyword|translation|tool"
rg -n --glob '*.md' "keyword|translation|synonym|tool" .
```

6. Return the best confirmed matches, not an exhaustive dump.

## Search rules

- Prefer title and filename matches first, then body matches.
- Prefer qmd reranked results only after retrieved content confirms relevance.
- Use close synonyms when direct terms return little.
- Prefer notes whose folder and surrounding context also match the topic.
- Rank passing mentions below notes centered on the concept.
- If no exact home exists, return the closest semantic neighbors and state that the match is partial.

## Output contract

Return:

- `matches`: usually 3–5 repository paths with a short relevance reason;
- `coverage`: direct, partial, or none;
- `confidence`: high, medium, or low;
- `gap`: a concise statement of what appears not to exist.

Do not recommend placement or edits. `$note-home-finder` owns that decision.
