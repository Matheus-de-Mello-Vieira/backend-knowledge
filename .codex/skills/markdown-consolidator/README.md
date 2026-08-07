# Codex Markdown Consolidator

A lossless, reviewed Codex workflow for consolidating overlapping Markdown evidence into either:

- one standalone Markdown publication; or
- one or more durable notes integrated into an existing Markdown knowledge repository.

The skill preserves the complete supported informational union, removes only duplicated meaning, and requires independent subagent review before each downstream stage.

## Repository integration

Repository-integrated mode works with two separately installed companion skills:

- `note-home-finder` decides whether to reuse, extend, create, or split durable notes;
- `markdown-link-normalizer` normalizes changed-note links and validates the final note graph.

The consolidator does not copy their internal rules. It locates their current `SKILL.md` and scripts, records those paths, and uses them through explicit handoff contracts.

## Core guarantees

- Every selected evidence source is inventoried.
- Every non-empty evidence line is extracted.
- Every extracted unit receives one primary topic, disposition, and final representation.
- Examples retain both concrete details and explanation.
- Conflicts, uncertainty, qualifications, limitations, dependencies, and exceptions remain visible.
- Temporary evidence files are never cited, named, or linked in durable notes.
- Every required producer attempt receives an independent subagent review.
- The main agent performs orchestration only.
- Repository candidates are normalized and validated in a disposable shadow tree before durable files are written.

## Installation

Copy the skill directory into a repository:

```text
<repository>/.agents/skills/markdown-consolidator/
```

or install it for the current user:

```text
~/.agents/skills/markdown-consolidator/
```

Repository-integrated mode also requires the companion skills to be installed in a discoverable location such as:

```text
<repository>/.agents/skills/<skill>/
<repository>/.codex/skills/<skill>/
~/.agents/skills/<skill>/
~/.codex/skills/<skill>/
```

Required names:

```text
note-home-finder
markdown-link-normalizer
```

## Usage

### Standalone consolidation

```text
$markdown-consolidator Consolidate all Markdown files under docs/sources into docs/consolidated.md. Preserve all supported information and do not cite the source files.
```

### Integrate into an existing note repository

```text
$markdown-consolidator Integrate the Markdown files under Inbox/oauth-research into this note repository. Use existing notes when they are the correct home, create or split notes when needed, preserve existing content, and validate all resulting links.
```

### Extend rather than duplicate

```text
$markdown-consolidator Consolidate these privacy-governance sources into the existing knowledge base. Prefer extending an appropriate note over creating a duplicate, but keep every source detail represented.
```

### Explicit split permission

```text
$markdown-consolidator Integrate these files into the repository. Split them across multiple notes when the topics have different natural homes, and add contextual links between the resulting notes.
```

## Publication modes

### Standalone

Produces one self-contained Markdown document. The lossless extraction, comparison, conflict resolution, synthesis, evidence materialization, review, and validation flow produces one self-contained document.

### Repository integrated

Adds reviewed stages for:

1. companion-skill discovery;
2. note placement using `note-home-finder`;
3. durable destination and context-note snapshots;
4. unit-to-destination integration planning;
5. multi-note annotated synthesis;
6. publication-set materialization;
7. link normalization and repository-wide validation using `markdown-link-normalizer`;
8. baseline-content, heading, context-boundary, and link-plan validation.

## File classes

Repository mode distinguishes three classes.

### Evidence sources

Selected input files whose complete supported information must be represented. They may be deleted after publication and must never be cited or linked.

### Destination notes

Durable notes that may be reused, extended, or created. These are the only repository files the workflow may publish.

### Context notes

Durable neighboring notes used for taxonomy, terminology, boundaries, and links. They remain read-only unless a reviewed placement plan explicitly promotes them to destinations.

## Explicit execution order

Every semantic stage uses:

```text
specify
  → producer subagent
  → reconcile producer
  → independent stage-review subagent
  → reconcile review
  → deterministic validation
  → advance or retry
```

Repository mode executes:

```text
Evidence inventory
  → Companion discovery
  → Note-home placement
  → Placement review and validation
  → Destination/context snapshots
  → Outline
  → Lossless extraction
  → Topic organization
  → Comparison
  → Conflict decisions
  → Integration plan
  → Integration-plan review and validation
  → Full publication-set synthesis
  → Publication review
  → Lifecycle and review validation
  → Final semantic validation
  → Link normalization in repository shadow
  → Full shadow-tree link validation
  → Repository-integration validation
  → Delegation validation
  → Publish normalized destination notes
```

## Companion interaction

### `note-home-finder`

The consolidator spawns a `note-home-finder-adapter` subagent and injects the installed companion `SKILL.md` unchanged. The adapter follows the companion's repository search workflow and produces only a machine-readable placement plan.

Placement outcomes:

- reuse an existing note;
- extend an existing note;
- create a new note;
- split the material across multiple notes.

The placement output is independently reviewed and deterministically validated before outline planning.

### `markdown-link-normalizer`

The consolidator invokes the companion scripts only after candidate note paths, headings, and link relationships are stable.

The link pipeline:

1. copies the repository's Markdown files into a disposable shadow tree;
2. records pre-existing link failures;
3. removes selected evidence files from the modeled final state;
4. overlays candidate destination notes;
5. normalizes only changed candidate notes;
6. validates every local Markdown file and heading target in the final shadow tree;
7. copies normalized candidates into a disposable normalized-output directory.

New or evidence-deletion-exposed link failures block publication. Unchanged pre-existing failures are reported as warnings.

## Existing-note preservation

Before synthesis, the skill snapshots every existing destination and context note.

Mandatory behavior:

- preserve existing supported content and note purpose;
- preserve established terminology and external references;
- preserve existing headings unless a reviewed heading migration is approved;
- integrate material into specific existing sections instead of appending a generic catch-all section;
- keep context notes read-only;
- compare final candidates with snapshots during independent review.

## Link behavior

Repository links are allowed and encouraged only when they clarify a useful relationship:

- broader context;
- prerequisite;
- implementation detail;
- contrast;
- alternative;
- example;
- continuation;
- related mechanism.

The relationship must be stated in nearby prose. A link cannot replace facts assigned to the current note.

Temporary evidence links remain forbidden.

## Durable and disposable outputs

### Standalone

Durable:

```text
consolidated.md
```

### Repository integrated

Durable:

```text
one or more reviewed destination notes
```

Disposable internal state:

```text
.markdown-consolidator-work/
```

This directory contains placement plans, snapshots, extraction units, comparisons, decisions, integration plans, annotated drafts, candidates, shadow repository, receipts, reviews, and validation reports. It may be deleted as one directory after successful publication.

## New scripts

```text
locate_companion_skills.py
validate_placement.py
snapshot_repository_context.py
validate_integration_plan.py
materialize_publication_set.py
run_link_pipeline.py
validate_repository_integration.py
```

The existing lifecycle, review, extraction, topic, comparison, decision, writing, consolidation, and delegation scripts remain in use.

## Important contracts

### Placement plan

Defines the outcome, confidence, destination paths and actions, context notes, and rationale.

### Repository context index

Records immutable snapshots, hashes, and existing headings for destination and context notes.

### Integration plan

Assigns every source unit to exactly one primary destination and defines section operations, protected headings, approved heading migrations, terminology constraints, and contextual links.

### Publication manifest

Lists every candidate note, action, annotated path, and assigned unit set for one publication revision.

### Repository coverage map

Maps every source unit to its durable destination and exact materialized evidence.

## Validation rules

Repository publication is blocked when any of these remains:

- an evidence source is selected as a durable destination;
- a source unit lacks one primary destination;
- a context note is modified without becoming a destination;
- an existing heading disappears without an approved migration;
- a planned link is missing;
- a local link targets disposable evidence;
- a new local file or anchor target is broken;
- a destination note loses supported baseline content;
- source-dependent narration appears;
- final evidence coverage is incomplete;
- a required producer lacks an independent review;
- lifecycle or delegation validation fails.

## Tests

Run both suites:

```bash
python .agents/skills/markdown-consolidator/tests/smoke_test.py
python .agents/skills/markdown-consolidator/tests/repository_integration_smoke_test.py
```

Compile all scripts:

```bash
python -m py_compile .agents/skills/markdown-consolidator/scripts/*.py
```

The repository-integration suite covers companion discovery, placement validation, snapshots, unit-to-note assignment, publication-set materialization, shadow-tree link validation, repository integration validation, and rejection of disposable evidence as a destination.

## Scope limitations

The uploaded `markdown-link-normalizer` companion normalizes and validates local inline Markdown links. Other syntaxes, such as Obsidian wikilinks, reference-style links, or raw HTML links, require separate tooling unless the companion skill is later expanded.

The consolidator does not create reciprocal links in unrelated context notes by default. Request those edits explicitly so they become reviewed destinations.
