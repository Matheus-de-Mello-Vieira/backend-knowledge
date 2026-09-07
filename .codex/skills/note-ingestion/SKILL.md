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

### 2. Repository retrieval

After extraction, invoke `$note-topic-search` for the substantial extracted concepts before placement or writing, even when the user supplied an explicit target. Retrieval establishes existing canonical coverage, semantic neighbors, and possible duplication.

### 3. Placement

If the user supplied a clear canonical target and the retrieval results confirm that all extracted units fit its established subject without conflicting ownership, skip `$note-home-finder`.

Otherwise invoke `$note-home-finder` with the extracted units and the confirmed `$note-topic-search` results.

### 4. Boundary

Invoke `$note-boundary-analyzer` only when extracted units span neighboring subjects, abstraction levels, implementations/applications, or existing same-level coverage. For a single obvious concept in one obvious home, this gate may be skipped.

### 5. Existing durable content

Invoke `$note-content-mover` only if the accepted boundary plan requires relocating existing repository material. Do not load it for ordinary additive ingestion.

### 6. Writing

Invoke `$note-writer` with only the units assigned to each destination, any accepted local-context limits, and any approved link plan. The writer must not select semantic link targets independently.

### 7. Linking and validation

If the new prose introduces concepts with useful existing deeper context, invoke `$note-link-planner`. It exclusively decides which existing phrase should link to which repository destination.

Apply only approved link markup without adding navigation prose. Invoke `$markdown-link-normalizer` only when links or anchors changed. Invoke `$markdownlint-fix` only when lint findings are introduced or exposed.

## Acceptance criteria

- supplied meaning is represented without unsupported additions;
- repository retrieval was performed before substantial durable integration;
- every substantial unit has a natural destination or explicit omission reason;
- note boundaries remain coherent;
- examples and implementation details are bounded;
- no unnecessary full explanation is duplicated;
- durable prose follows repository style.
