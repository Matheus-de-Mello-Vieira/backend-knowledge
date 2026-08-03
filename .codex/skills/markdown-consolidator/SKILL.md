---
name: markdown-consolidator
description: Perform a complete, lossless semantic consolidation of multiple Markdown files about the same subject. Preserve every informational unit, detail, example, caveat, procedure, warning, rationale, variant, historical statement, conflict, code block, table, external reference, and qualifier while removing only redundant wording. Produce one standalone Markdown publication with no citations, paths, names, IDs, or line references to the input files. Keep all extraction, provenance, decisions, drafts, conflicts, and validation artifacts in one disposable work directory. Use when asked to merge, unify, reconcile, synthesize, or update overlapping .md sources. Never replace the sources with a summary unless the user explicitly requests summarization.
---

# Markdown Consolidator

Create one coherent, standalone Markdown document from overlapping sources without losing source information. This is **lossless semantic consolidation**, not summarization, shortening, or selective extraction.

The skill is self-contained. The orchestrator reads role definitions from `references/agents/*.md` and injects them into built-in subagent tasks. No `.codex/agents` registration is required.

## Publication boundary

The final publication must be independent from the temporary source set.

It must not contain:

- input filenames or paths;
- source IDs or extraction unit IDs;
- source line numbers or line ranges;
- footnotes or links whose purpose is to cite an input file;
- phrases such as `according to source-a.md`, `Source A states`, or equivalent file-oriented attribution;
- a bibliography of the local input files.

When input files disagree, describe the competing statements by their content, scope, version, date, platform, configuration, or uncertainty—not by filename or synthetic source label.

External URLs, publication references, standards, authors, and bibliographic information that are themselves part of the source content must still be preserved. The prohibition applies only to citations and identifiers for the temporary input files.

All input-file provenance remains in the internal coverage map under the disposable work directory. It is used for validation only and is not copied into the final Markdown.

### Standalone exposition

The publication must state the subject matter directly and must never make the temporary inputs part of the narrative.

Reject constructions such as:

- `the material states`, `the material shows`, or `the material explains`;
- `in the material`, `from the material`, or `according to the material`;
- `the sources describe`, `the documents mention`, or `the files show`;
- `as shown in the source` or `the example in the material`;
- any sentence that assumes the reader has seen an example, definition, diagram, case, or argument that exists only in an input file.

An example from a source must be recreated as standalone exposition. Include the relevant setup, entities, mechanism or steps, outcome, and an explanation of the principle it demonstrates. Do not merely name or allude to the example.

Bad:

```text
The distance-learning example in the material shows the logic.
```

Good:

```text
In the distance-learning scenario, students receive the same lesson remotely but complete activities at different times. The example demonstrates that delivery location and participation timing are separate dimensions: a course can be remote without being synchronous.
```

Use only details supported by the extracted units. Explain the supported logic without inventing missing facts.

## Non-negotiable completion rule

A run is complete only when every extracted source unit has exactly one recorded disposition and is represented in the final document or its appendices.

Allowed dispositions:

- `included_directly`: represented as its own final claim or content block;
- `merged_equivalent`: merged with semantically equivalent units, with all contributing units mapped to the final claim;
- `included_as_detail`: retained as a supporting detail under a broader final statement;
- `preserved_as_variant`: retained as an alternative, exception, implementation, or contextual variant;
- `preserved_as_conflict`: retained in an unresolved disagreement;
- `preserved_as_historical`: retained and clearly labeled as historical, deprecated, or superseded;
- `preserved_in_appendix`: retained in an appendix because it would interrupt the main narrative;
- `represented_by_structure`: a heading or structural unit represented by the final outline rather than prose.

There is no omission disposition for readable, in-scope source information. Material that is duplicate, outdated, weakly supported, or awkward must still be represented through merging, labeling, qualification, or an appendix. If a file is outside the requested scope, exclude it during inventory rather than silently omitting units after extraction.

## Operating principles

1. Treat source files as immutable temporary evidence. Never modify them.
2. Preserve all source information, not merely information judged important.
3. Preserve dates, versions, numbers, units, negations, exceptions, conditions, alternatives, rationale, uncertainty, examples, warnings, procedures, code, tables, external references, and meaningful metadata.
4. Remove only redundant expression. Never remove a distinct fact, nuance, condition, example, or perspective.
5. Deduplicate meaning only when the merged final statement covers the full semantic union of all contributing units.
6. Do not silently resolve conflicts or discard superseded claims. Preserve their status and context.
7. Use exactly one publication writer. Parallelize only independent read-heavy analysis.
8. Keep complete source traceability internally in the disposable work directory.
9. Never expose input-file provenance in the final publication.
10. Every extracted unit must map to one or more final claims, sections, code blocks, tables, external references, or appendices.
11. Document length is not a quality problem. Do not compress to fit an assumed length or token target.
12. Never produce only an overview, executive summary, highlights list, or selected findings unless explicitly requested.
13. Validate unit-level coverage and the absence of input-file citations before declaring success.
14. Write direct, self-contained exposition. Never use meta-source narration or assume that the reader has access to the original examples.
15. Require exact final-document evidence for every non-structural unit and both detail and explanation evidence for every example unit.

## Default inputs and outputs

Defaults:

- Source root: user-selected files or directory; otherwise the current working directory.
- Source pattern: `**/*.md`.
- Exclude: output directories, `.git`, `.agents`, `.codex`, `node_modules`, and both `.markdown-consolidator-work` and legacy `.consolidation` directories.
- Final document: `consolidated.md` in the selected output directory or current directory.
- Disposable work directory: `.markdown-consolidator-work/` beside the final document.
- Audience: infer from the sources.
- Detail level: exhaustive and lossless.
- Publication attribution: no citations to input files.
- Internal traceability: coverage map stored only in the work directory.
- Conflict policy: preserve all positions; resolve status only when supported.
- Maximum repair iterations: 3.
- Automatic cleanup: disabled unless the user explicitly requests it.

Ask one focused question only when the source set or output path cannot be determined. Infer minor style preferences. Do not infer permission to summarize.

## Required deliverables

Create only one durable publication artifact outside the work directory:

```text
consolidated.md
```

Place every disposable artifact under one directory:

```text
.markdown-consolidator-work/
  inventory.json
  outline.json
  units/
  topics.json
  comparisons/
  decision-ledger.json
  conflicts.md
  drafts/
  coverage-map.json
  validation-report.json
  validation/
```

The entire work directory may be deleted after a successful run. Do not place intermediate or reasoning artifacts beside the final document.

If the user explicitly asks for cleanup after success, delete the work directory only after final validation passes. Otherwise report that it is safe to remove with one recursive deletion command.

## Reference-backed subagent roles

```text
references/agents/source-analyst.md
references/agents/topic-comparator.md
references/agents/conflict-resolver.md
references/agents/synthesizer.md
references/agents/validator.md
```

### Delegation protocol

Before starting a role-specific subagent:

1. Read the complete role file.
2. Read the referenced contracts and policies.
3. Build a task prompt containing the complete role instructions, exact assigned scope, input paths, output path, applicable contract, audience, terminology, conflict policy, lossless-coverage rule, publication boundary, and work-directory boundary.
4. Explicitly state: `This is exhaustive consolidation, not summarization. Do not omit any informational unit. Do not cite or name the input files in publication prose. State content directly. Never write meta-source phrases such as “the material states” or refer to examples that are not fully presented and explained in the final document.`
5. Use an explorer-style subagent for extraction and validation, a default-style subagent for comparison and conflict reasoning, and one worker-style subagent for synthesis.
6. Validate the returned artifact before accepting it.
7. Retry once with concrete validation errors when malformed or incomplete.
8. Fall back to sequential execution in the main agent when subagents are unavailable.

Do not assume subagents can discover role files. Inject the role text and contracts into each delegated task.

## Workflow

### 1. Resolve output and work paths

Let `<final-document>` be the requested standalone Markdown path.

Set:

```text
<output-dir> = parent directory of <final-document>
<work-dir> = <output-dir>/.markdown-consolidator-work
```

All temporary files must remain under `<work-dir>`. Never spread drafts, maps, reports, or conflict records across the output directory.

Exclude `<work-dir>` and `<final-document>` from source discovery.

### 2. Preflight and inventory

Run:

```bash
python <skill-dir>/scripts/inventory_markdown.py <source-root> \
  --output <work-dir>/inventory.json \
  --exclude '.git/**' \
  --exclude '.agents/**' \
  --exclude '.codex/**' \
  --exclude 'node_modules/**' \
  --exclude '.markdown-consolidator-work/**' \
  --exclude '.consolidation/**'
```

Also exclude the selected output directory when it is inside the source root and could contain generated Markdown.

Stop with a concrete error when no readable Markdown files are found. Record unreadable files; do not skip them silently.

Read `references/contracts.md` before creating intermediate JSON.

### 3. Plan a complete canonical outline

Inspect the full heading structure of every source, not representative samples. Build an outline capable of containing all extracted information.

The outline must include:

- every source topic;
- sections for exceptions, alternatives, examples, warnings, limitations, and rationale when present;
- enough space to present every example as a self-contained scenario and explain its relevance;
- a historical or deprecated-information section when needed;
- an unresolved-conflicts section when needed;
- an additional-material appendix for information that does not fit cleanly elsewhere;
- external references when they exist in the source content.

Do not add an input-source bibliography or local-file reference section.

Save `<work-dir>/outline.json`. An overview may introduce the document, but it must never substitute for the detailed sections.

### 4. Extract all source content

Read:

- `references/agents/source-analyst.md`
- the `Content-unit batch` contract in `references/contracts.md`

Delegate one read-only extraction task per file or disjoint batch. Each analyst must cover every non-empty source line through a content unit. This includes headings, frontmatter, prose, lists, blockquotes, examples, code fences, tables, footnotes, link definitions, comments containing information, and references.

Each extraction result must include:

- exact source text and line range;
- all qualifiers and assertion type;
- a `covered_line_ranges` list;
- an `uncovered_nonempty_lines` list, which must be empty before acceptance.

Do not accept an extraction batch with uncovered non-empty lines. Do not summarize paragraphs into a smaller set of selected claims.

Write batches only under `<work-dir>/units/`.

### 5. Group topics without dropping units

Create `<work-dir>/topics.json`. Every extracted unit ID must appear in exactly one primary topic group, with optional cross-topic references. Units that do not fit the main outline go to an explicit `additional-source-material` topic rather than being discarded.

### 6. Compare relationships

Read `references/agents/topic-comparator.md` and delegate topic groups in parallel.

Allowed relationships:

- `equivalent`
- `near_duplicate`
- `complementary`
- `conflicting`
- `conditionally_compatible`
- `unique`
- `outdated`

Do not use `irrelevant` as a deletion mechanism. Information inside the selected source set must be preserved. For equivalent or near-duplicate units, calculate the semantic union that the final merged statement must retain.

Write all comparison outputs under `<work-dir>/comparisons/`.

### 7. Resolve conflicts and historical status

Read `references/agents/conflict-resolver.md` and `references/decision-policy.md`.

Resolve independent conflict sets in parallel. A decision controls presentation and status, never survival.

The final publication must describe positions by content and scope. It must not say which local file contained them. For unresolved conflicts, use direct standalone wording such as:

```text
Two behaviors remain unresolved:

- Under one condition, ...
- Under another condition, ...

The available facts do not establish which condition distinguishes them.
```

Write `<work-dir>/decision-ledger.json` and `<work-dir>/conflicts.md`.

### 8. Build a unit-disposition ledger before writing

Before synthesis, create a planned disposition entry for every extracted unit. No unit may be absent. The ledger may be stored in the draft coverage map and completed by the synthesizer.

For every unit record:

- planned disposition;
- target section;
- merge group when applicable;
- expected final claim or block;
- reason for labeling as historical, variant, conflict, or appendix material.

Do not begin final approval until the planned unit count equals the extracted unit count.

### 9. Synthesize with one writer

Read:

- `references/agents/synthesizer.md`
- the `Coverage map` contract in `references/contracts.md`
- `references/decision-policy.md`

The writer receives all accepted units, not a shortened selection. The writer must:

- write complete detailed sections, not an overview-only answer;
- preserve every distinct source fact and nuance;
- merge duplicates only by semantic union;
- retain all examples unless they are exactly redundant, in which case map all equivalent examples to the retained example;
- retain procedures step by step;
- retain warnings, limitations, rationale, alternatives, and edge cases;
- preserve code blocks and tables unless combining exact duplicates;
- preserve historical or superseded information with labels;
- place awkward but in-scope material in an appendix;
- preserve external references and links that are part of the content;
- populate `unit_dispositions` for every extracted unit;
- populate exact `publication_evidence` excerpts for every non-structural unit;
- for every example unit, include exact excerpts for both the presented example details and the explanation of its logic;
- state content directly without `the material states`, `in the material`, `the sources describe`, or similar meta-source phrasing;
- never refer to an example, definition, case, or argument that the final document does not itself present;
- never optimize for brevity;
- never include input filenames, paths, source IDs, unit IDs, or source line ranges in publication prose, headings, footnotes, links, or reference lists.

Write `<work-dir>/drafts/draft-1.md` and `<work-dir>/coverage-map.json`.

After validation succeeds, copy the accepted draft to `<final-document>`.

### 10. Validate lossless coverage and publication independence

Read `references/agents/validator.md` and `references/quality-gates.md`.

Run validators for:

1. source-line and extraction coverage;
2. unit-disposition and final-document coverage;
3. contradictions, historical status, and qualifier preservation;
4. internal traceability and unsupported claims;
5. absence of input filenames, paths, source IDs, line citations, file-oriented attribution, and meta-source narration in the final document;
6. exact publication-evidence coverage for every non-structural unit;
7. complete presentation and explanation of every example unit;
8. coherence, duplicate wording, terminology, and Markdown integrity.

Also run:

```bash
python <skill-dir>/scripts/validate_consolidation.py \
  --document <work-dir>/drafts/draft-1.md \
  --inventory <work-dir>/inventory.json \
  --units-dir <work-dir>/units \
  --coverage-map <work-dir>/coverage-map.json \
  --decisions <work-dir>/decision-ledger.json \
  --report <work-dir>/validation-report.json
```

A run fails when:

- any extracted unit lacks a disposition;
- any disposition refers to no final section or claim;
- any source contains uncovered non-empty lines;
- semantic validators identify lost information;
- the final Markdown names or cites an input file, path, source ID, unit ID, or line range;
- the final Markdown contains meta-source phrases such as `the material states`, `in the material`, or `the example in the source`;
- any non-structural unit lacks exact final-document evidence;
- any example unit lacks both a presented example and an explanation of its logic.

### 11. Repair with a bounded loop

For at most three repair iterations:

1. Group findings by extraction, clustering, comparison, conflict status, synthesis, internal traceability, publication-boundary violation, or formatting.
2. Route each finding to its responsible stage.
3. Allow only the single publication writer to edit the draft.
4. Re-run semantic and deterministic validation.

Do not patch around missing information by weakening validation or deleting a unit.

### 12. Publish and optionally clean up

When all quality gates pass:

1. Copy the validated draft to `<final-document>`.
2. Confirm the final document contains no local-source citations or identifiers.
3. Leave every non-publication artifact under `<work-dir>`.
4. If the user requested automatic cleanup, delete `<work-dir>` after the copy succeeds.
5. Otherwise report the final document and the single directory that may be deleted.

Do not delete the original sources unless the user explicitly asks for that separate action.

## Final quality gate

Do not declare success unless:

- every readable selected file was processed;
- every non-empty source line is covered by extraction;
- every extracted unit has exactly one valid disposition;
- every non-structural unit has a verified final representation;
- every equivalent merge preserves the full semantic union;
- all distinct examples, procedures, caveats, rationale, alternatives, conflicts, historical statements, code, tables, and external references remain represented;
- source line, unit disposition, and final representation coverage are all `1.0`;
- no unsupported factual claim remains;
- the final document contains no citations or identifiers for input files;
- the final document contains no meta-source narration or dangling references to unavailable input content;
- every non-structural unit has exact publication evidence;
- every example is presented and explained rather than merely referenced;
- all intermediate artifacts exist only under `<work-dir>`;
- code fences, tables, links, anchors, and any retained external-reference footnotes are valid;
- the document reads as one coherent, complete publication rather than a summary or source-by-source compilation.

Read `references/quality-gates.md` for severity and routing rules.

## Final response

Report only:

- final document path;
- validation status;
- number of source files processed;
- extracted-unit count and represented-unit count;
- unresolved-conflict count;
- work-directory path;
- whether the work directory was deleted or may now be deleted safely.

Do not expose chain-of-thought or dump intermediate JSON into chat.
