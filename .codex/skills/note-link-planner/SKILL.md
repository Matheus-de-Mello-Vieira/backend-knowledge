---
name: note-link-planner
description: Plan semantically useful internal Markdown links without changing prose. Use when a note should connect naturally to deeper, prerequisite, implementation, contrasting, or adjacent repository notes. This skill decides what should link where; mechanical path/anchor handling belongs to markdown-link-normalizer.
---

# Note Link Planner

This skill owns **semantic link selection**.

## Workflow

1. Read the target prose and identify only concepts whose deeper repository context would materially help the reader.
2. Prefer phrases that already exist in the prose; preserve their visible text exactly when practical.
3. Invoke `$note-topic-search` only for concepts whose destination is not already known.
4. Confirm the destination actually provides useful deeper or adjacent context.
5. Prefer the first meaningful occurrence and the most specific stable section anchor.

## Link relationships

Useful relationships include prerequisite, deeper mechanism, implementation, application consequence, contrast, alternative, example, and broader context.

## Output contract

Return a link plan containing:

- `source_phrase` exactly as it appears;
- `target_path`;
- `target_heading` when useful;
- `relationship`;
- `reason`.

## Exclusions

Do not:

- add new navigation prose merely to create a link;
- repeatedly link the same concept;
- link generic terms just because a note exists;
- use links to compensate for content that is actually misplaced;
- mechanically normalize paths or anchors.