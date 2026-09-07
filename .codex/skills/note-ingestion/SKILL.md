---
name: note-ingestion
description: Incorporate supplied source content into the knowledge base. Use when the user provides an article, transcript, scratch note, lecture notes, pasted explanation, or similar material whose knowledge must first be extracted before placement and writing.
---

# Note Ingestion

This workflow owns the transaction from **supplied content → extracted knowledge → durable notes**.

## Capability gates

### 1. Source complexity

Start with `$knowledge-unit-extractor` in normal mode.

If the request contains multiple overlapping sources, material conflicts, or an explicit requirement to preserve every supported detail with exhaustive evidence accounting, stop before durable mutation and return `requires_markdown_consolidator` so the router can select `$markdown-consolidator`.

### 2. Placement

If the user already supplied a clear canonical target and all extracted units fit its established subject, skip repository-wide placement.

Otherwise invoke `$note-home-finder` with the extracted units. It will disclose `$note-topic-search` as needed.

### 3. Boundary

Invoke `$note-boundary-analyzer` only when extracted units span neighboring subjects, abstraction levels, implementations/applications, or existing same-level coverage. For a single obvious concept in one obvious home, this gate may be skipped.

### 4. Existing durable content

Invoke `$note-content-mover` only if the accepted boundary plan requires relocating existing repository material. Do not load it for ordinary additive ingestion.

### 5. Writing

Invoke `$note-writer` with only the units assigned to each destination and any accepted local-context limits.

### 6. Linking and validation

If the new prose introduces concepts with useful existing deeper context, invoke `$note-link-planner`. Apply only approved link markup without adding navigation prose.

Invoke `$markdown-link-normalizer` only when links or anchors changed. Invoke `$markdownlint-fix` only when lint findings are introduced or exposed.

## Acceptance criteria

- supplied meaning is represented without unsupported additions;
- every substantial unit has a natural destination or explicit omission reason;
- note boundaries remain coherent;
- examples and implementation details are bounded;
- no unnecessary full explanation is duplicated;
- durable prose follows repository style.