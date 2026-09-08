# Codex Note Skill System

The note system is organized from **user intent** down to reusable capabilities. A workflow should disclose only the next capability or reference required by the current decision gate.

## User-facing workflows

| User intent | Workflow |
| --- | --- |
| Route an ambiguous note request | `$note-workflow` |
| Ask a conceptual question and inspect whether the notes already explain it | `$note-question` |
| Incorporate an article, transcript, scratch text, or other supplied content | `$note-ingestion` |
| Create a learning structure for a topic not yet understood | `$note-scaffolding` |
| Explicitly add already-understood knowledge or repair an explanation | `$note-authoring` |
| Review note quality or architecture without editing it | `$note-review` |
| Split, move, merge, or deduplicate knowledge across notes | `$note-refactor` |
| Enrich a note with natural semantic cross-links | `$note-link-enrichment` |
| Consolidate multiple overlapping/conflicting sources with exhaustive evidence preservation | `$markdown-consolidator` |

Small local corrections may bypass workflow routing when the target and scope are obvious and mutation intent is explicit.

### Read-only intent distinctions

- **`note-question`** answers **“Help me understand this, and tell me whether my notes already explain it.”** Its primary output is a technical answer plus a documentation-coverage assessment.
- **`note-review`** answers **“Is this note/repository structure good?”** Its primary output is prioritized quality or architecture findings.
- **`note-topic-search`** answers **“Where do I already discuss this?”** Its primary output is confirmed repository matches.

A read-only workflow does not become a mutation workflow merely because it discovers a gap. Mutation requires a later or current explicit request to change repository content.

## Reusable capabilities

### Retrieval and extraction

- **`note-topic-search`** — find existing repository coverage.
- **`knowledge-unit-extractor`** — turn supplied source material into explicit conceptual units. Supports normal and exhaustive modes.

### Semantic decisions

- **`note-home-finder`** — decide **where** knowledge belongs: reuse, extend, create, or split. It consumes confirmed repository search results and invokes `$note-topic-search` when those results are absent or stale.
- **`note-boundary-analyzer`** — decide **how much** each destination owns after placement is known.
- **`note-link-planner`** — exclusively decide which existing phrase should link to which semantic repository destination.
- **`note-cohesion-reviewer`** — diagnose center-of-gravity, abstraction, duplication, example-boundary, explanation, and linking problems without editing.

### Mutation and mechanical capabilities

- **`note-writer`** — write scoped explanatory prose from approved semantic inputs and apply approved link markup without selecting semantic link targets.
- **`note-content-mover`** — execute an approved cross-note structural move/split/merge plan.
- **`markdown-link-normalizer`** — mechanically normalize and validate local links.
- **`markdownlint-fix`** — repair Markdown lint findings.

## Mutation authority

Repository access and repository context do not imply permission to mutate files. Questions, searches, assessments, and exploratory discussion remain read-only unless the user explicitly requests a repository change.

A conceptual question may expose a documentation defect. That finding is evidence for a possible later authoring task, not authorization to invoke mutation capabilities. Prior edits in the same conversation do not change this rule unless the user explicitly establishes automatic incorporation behavior.

## Progressive disclosure

Progressive disclosure must never bypass repository invariants. It controls which **conditional reasoning capabilities** are loaded after required evidence is gathered.

Use these gates:

1. Establish the user's intent and mutation authority before disclosing mutation workflows or capabilities.
2. For substantial additions, new sections, new notes, or durable source ingestion, run `$note-topic-search` to establish existing coverage even when the user supplied an explicit target. Only narrow local corrections with obvious scope may skip retrieval.
3. Invoke `$note-home-finder` only when canonical placement is unresolved, contradicted by retrieval, compound, or likely to create/split notes. Reuse supplied fresh search results rather than repeating retrieval.
4. Load boundary analysis only when the edit can cross subjects, abstraction levels, or duplicate existing explanations.
5. Load content movement only when durable content must actually move.
6. Load semantic link planning only when useful cross-links are part of the task or naturally emerge from a substantial edit. `$note-link-planner` alone selects semantic destinations; writers only apply approved link plans.
7. Load mechanical link normalization only when links or anchors changed.
8. Load lint repair only when the edit introduces or exposes lint findings.
9. Load specialized reference files just before the branch or stage that requires them.

The goal is the **minimum sufficient capability set after required invariants are satisfied**, not the maximum available pipeline and not the minimum number of checks.

## Dependency contract

Each skill should state **Owns**, **Inputs/Requires**, **Delegates**, and **Must not** responsibilities when applicable.

Invocation dependencies flow from workflows toward lower-level capabilities. Lower-level primitives never invoke workflows that depend on them. A semantic skill may invoke a lower-level prerequisite it explicitly owns as a dependency—for example, `$note-home-finder` may invoke `$note-topic-search` when fresh search results were not supplied. Data may also flow between primitives through the calling workflow.

Read-only workflows do not invoke mutation workflows or capabilities. A later user request to apply a read-only finding is routed independently according to its new mutation intent.

Repository-wide knowledge architecture remains authoritative in `AGENTS.md`; default prose behavior and mutation authority remain authoritative in `.codex/model_instructions.md`.
