# Codex Note Skill System

The note system is organized from **user intent** down to reusable capabilities. A workflow should disclose only the next capability or reference required by the current decision gate.

## User-facing workflows

| User intent | Workflow |
| --- | --- |
| Route an ambiguous note request | `$note-workflow` |
| Incorporate an article, transcript, scratch text, or other supplied content | `$note-ingestion` |
| Create a learning structure for a topic not yet understood | `$note-scaffolding` |
| Add already-understood knowledge or repair an explanation | `$note-authoring` |
| Review a note without editing it | `$note-review` |
| Split, move, merge, or deduplicate knowledge across notes | `$note-refactor` |
| Enrich a note with natural semantic cross-links | `$note-link-enrichment` |
| Consolidate multiple overlapping/conflicting sources with exhaustive evidence preservation | `$markdown-consolidator` |

Small local corrections may bypass workflow routing when the target and scope are obvious.

## Reusable capabilities

### Retrieval and extraction

- **`note-topic-search`** — find existing repository coverage.
- **`knowledge-unit-extractor`** — turn supplied source material into explicit conceptual units. Supports normal and exhaustive modes.

### Semantic decisions

- **`note-home-finder`** — decide **where** knowledge belongs: reuse, extend, create, or split.
- **`note-boundary-analyzer`** — decide **how much** each destination owns after placement is known.
- **`note-link-planner`** — identify valuable semantic links and existing phrases that can carry them.
- **`note-cohesion-reviewer`** — diagnose center-of-gravity, abstraction, duplication, example-boundary, explanation, and linking problems without editing.

### Mutation and mechanical capabilities

- **`note-writer`** — write scoped explanatory prose from approved semantic inputs.
- **`note-content-mover`** — execute an approved cross-note structural move/split/merge plan.
- **`markdown-link-normalizer`** — mechanically normalize and validate local links.
- **`markdownlint-fix`** — repair Markdown lint findings.

## Progressive disclosure

A workflow must not load its entire possible dependency set up front. Use gates:

1. Determine whether the target and ownership are already known.
2. Load retrieval/placement only if ownership is unresolved.
3. Load boundary analysis only when the edit can cross subjects, abstraction levels, or duplicate existing explanations.
4. Load content movement only when durable content must actually move.
5. Load semantic link planning only when useful cross-links are part of the task or naturally emerge from a substantial edit.
6. Load mechanical link normalization only when links or anchors changed.
7. Load lint repair only when the edit introduces or exposes lint findings.
8. Load specialized reference files just before the branch or stage that requires them.

The goal is the **minimum sufficient capability set**, not the maximum available pipeline.

## Dependency contract

Each skill should state **Owns**, **Inputs/Requires**, **Delegates**, and **Must not** responsibilities when applicable.

Invocation dependencies flow from workflows toward lower-level capabilities. Lower-level primitives never invoke workflows that depend on them. Data may flow from one primitive to another through the calling workflow, but the workflow owns that sequencing.

Repository-wide knowledge architecture remains authoritative in `AGENTS.md`; default prose behavior remains authoritative in `.codex/model_instructions.md`.