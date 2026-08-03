# Standalone Lossless Markdown Consolidator for Codex

A self-contained Codex skill that combines multiple Markdown sources into one coherent document without losing source information.

The result is a **standalone Markdown publication**. It does not cite or depend on the temporary input files, so those files can be deleted after consolidation.

## Guarantees

A successful run requires:

- 100% coverage of non-empty source lines during extraction;
- exactly one disposition for every extracted unit;
- a final representation for every non-structural unit;
- preservation of distinct facts, details, examples, steps, warnings, limitations, rationale, alternatives, historical statements, conflicts, code, tables, external references, and qualifiers;
- zero citations or identifiers for the local input files in the final publication;
- zero meta-source narration such as `the material states`, `in the material`, or `the example in the source`;
- exact final-document evidence for every non-structural source unit;
- complete presentation and explanation of every example;
- all intermediate and reasoning artifacts contained in one disposable directory.

Equivalent wording may be merged, but the merged text must preserve the complete semantic union of every contributing source unit. Outdated, conflicting, or awkward material is labeled or moved to an appendix rather than discarded.

## Final and disposable outputs

Only the consolidated document is durable:

```text
output/
└── consolidated.md
```

Everything else is stored together:

```text
output/
└── .markdown-consolidator-work/
    ├── inventory.json
    ├── outline.json
    ├── units/
    ├── topics.json
    ├── comparisons/
    ├── decision-ledger.json
    ├── conflicts.md
    ├── drafts/
    ├── coverage-map.json
    ├── validation-report.json
    └── validation/
```

After validation succeeds, the complete work directory can be removed at once:

```bash
rm -rf output/.markdown-consolidator-work
```

The skill does not delete this directory automatically unless explicitly requested.

## No input-file citations

The final Markdown must not contain:

- input filenames or paths;
- generated source IDs or unit IDs;
- source line numbers or ranges;
- footnotes or links pointing to the local source files;
- phrases such as `Source A states` or `according to notes-a.md`;
- a bibliography of the local input files.

When source material conflicts, the final document describes each position by content and scope, for example:

```md
Two behaviors are documented:

- Version 2 uses a 30-minute expiration period.
- Version 3 uses a 60-minute expiration period.
```

When the distinguishing condition is unknown:

```md
Two behaviors remain unresolved:

- One behavior uses a 30-minute expiration period.
- Another uses a 60-minute expiration period.

The distinguishing condition is unknown.
```

External links, standards, publications, authors, and bibliographic references that are part of the original content are preserved. Only citations to the temporary local input files are prohibited.

## Standalone exposition and verification

The final document must state the subject directly. It must not narrate what the temporary inputs said or assume that the reader has access to them.

Rejected wording includes:

```text
The material states that ...
The sources describe ...
As shown in the source ...
The distance-learning example in the material shows the logic.
```

A source example must be recreated in the final document with enough information to stand alone:

```text
In the distance-learning scenario, students receive the same lesson remotely but complete activities at different times. This demonstrates that delivery location and participation timing are separate dimensions: remote instruction does not necessarily require synchronous participation.
```

The skill verifies this in multiple ways:

1. The deterministic validator scans prose outside code fences for prohibited meta-source patterns.
2. Every non-structural unit must include at least one exact `publication_evidence` excerpt that occurs in the final Markdown.
3. Every example unit must include an exact `detail_excerpt` presenting the example and an exact `explanation_excerpt` explaining its logic or significance.
4. Semantic validator agents compare source examples with the final text and reject dangling allusions to examples, cases, definitions, diagrams, or arguments that were never reproduced.

A run fails when any of these checks fails.

## Architecture

Codex discovers one skill:

```text
.agents/skills/markdown-consolidator/SKILL.md
```

The orchestrator reads role prompts from:

```text
.agents/skills/markdown-consolidator/references/agents/
```

It injects those prompts into built-in subagent tasks for:

1. exhaustive source extraction;
2. topic comparison;
3. conflict and historical-status resolution;
4. single-writer synthesis;
5. unit-level and publication-boundary validation.

No `.codex/agents` directory or `.codex/config.toml` registration is required.

## Installation

### Repository scope

Copy the `.agents` directory into a repository root:

```text
<repository>/.agents/skills/markdown-consolidator/SKILL.md
```

### User scope

Copy the skill directory to:

```text
~/.agents/skills/markdown-consolidator/
```

## Invocation

```text
$markdown-consolidator Perform a complete lossless consolidation of docs/sources into output/consolidated.md. Preserve every informational unit, keep all temporary artifacts under output/.markdown-consolidator-work, and do not cite the input files.
```

For selected files:

```text
$markdown-consolidator Consolidate architecture-a.md, architecture-b.md, and vendor-notes.md into architecture.md. Keep all details, examples, caveats, alternatives, conflicts, and historical behavior. The final document must be standalone and must not name the input files.
```

To remove temporary artifacts automatically after success:

```text
$markdown-consolidator Consolidate docs/sources into output/consolidated.md. After validation passes, delete the disposable work directory. Do not delete the source files.
```

## Package structure

```text
.agents/skills/markdown-consolidator/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
│   ├── consolidation-config.example.json
│   └── final-document-template.md
├── references/
│   ├── agents/
│   │   ├── source-analyst.md
│   │   ├── topic-comparator.md
│   │   ├── conflict-resolver.md
│   │   ├── synthesizer.md
│   │   └── validator.md
│   ├── contracts.md
│   ├── decision-policy.md
│   └── quality-gates.md
└── scripts/
    ├── inventory_markdown.py
    └── validate_consolidation.py
```

## How it works

### 1. Inventory

All selected Markdown files are inventoried. Generated outputs, the skill directory, and the disposable work directory are excluded.

### 2. Exhaustive extraction

Every non-empty line must be covered by an extracted unit. Headings, metadata, prose, lists, code, tables, footnotes, links, warnings, examples, and references are included.

### 3. Comparison

Units are classified as equivalent, near-duplicate, complementary, conflicting, conditionally compatible, unique, or outdated. No deletion path exists inside the selected source set.

### 4. Preservation-oriented decisions

Conflicts determine presentation and status, not deletion. Non-primary statements remain visible as alternatives, exceptions, historical behavior, or unresolved claims.

### 5. Complete standalone synthesis

One writer creates the detailed final document. Information that does not fit the main narrative goes into explicit appendices. Input-file provenance is written only to the internal coverage map.

### 6. Validation

The deterministic validator checks:

- source-line coverage;
- unit disposition coverage;
- final representation coverage;
- internal source, unit, section, claim, and block mappings;
- absence of source filenames, paths, IDs, and local-file citations in the publication;
- absence of meta-source narration and references to unavailable input content;
- exact publication-evidence coverage for every non-structural unit;
- complete example exposition, including both details and explanation;
- Markdown structure, code fences, anchors, and footnotes.

Semantic validator agents separately compare source units with final text to detect meaning loss and file-oriented attribution.

## Helper scripts

Inventory sources:

```bash
python .agents/skills/markdown-consolidator/scripts/inventory_markdown.py \
  docs/sources \
  --output output/.markdown-consolidator-work/inventory.json \
  --exclude '.git/**' \
  --exclude '.agents/**' \
  --exclude '.codex/**' \
  --exclude 'node_modules/**' \
  --exclude '.markdown-consolidator-work/**' \
  --exclude '.consolidation/**' \
  --exclude 'output/**'
```

Validate a run:

```bash
python .agents/skills/markdown-consolidator/scripts/validate_consolidation.py \
  --document output/.markdown-consolidator-work/drafts/draft-1.md \
  --inventory output/.markdown-consolidator-work/inventory.json \
  --units-dir output/.markdown-consolidator-work/units \
  --coverage-map output/.markdown-consolidator-work/coverage-map.json \
  --decisions output/.markdown-consolidator-work/decision-ledger.json \
  --report output/.markdown-consolidator-work/validation-report.json
```

The scripts use only the Python standard library.

## Pass criteria

A run passes only when:

```text
source_coverage = 1.0
source_line_coverage = 1.0
unit_disposition_coverage = 1.0
unit_final_representation_coverage = 1.0
publication_evidence_coverage = 1.0
example_exposition_coverage = 1.0
input_source_reference_violations = 0
meta_source_phrase_violations = 0
```

Agent validation must also confirm that no semantic detail was lost. Mapping a unit in JSON without actually preserving its meaning is a high-severity failure.

## Important distinction

Lossless does not mean verbatim concatenation. The skill may:

- reorganize sections;
- normalize terminology;
- merge duplicate wording;
- improve transitions;
- present current information before historical information.

It may not:

- select only important points;
- shorten procedures or examples;
- remove alternatives or caveats;
- hide conflicts;
- discard outdated information;
- replace detailed sections with an overview;
- cite or identify the temporary input files in the final publication;
- use meta-source narration such as `the material states` or `in the material`;
- refer to an example without presenting and explaining it in the final document.

## Troubleshooting

### Intermediate files appear beside the final document

Confirm the installed `SKILL.md` defines the disposable work directory as:

```text
<output-dir>/.markdown-consolidator-work
```

Every artifact except the final Markdown should be written below that directory.

### The final document cites input files

Inspect:

```text
output/.markdown-consolidator-work/validation-report.json
```

The deterministic validator rejects exact input paths, filenames, source IDs, and unit IDs found in the final Markdown. Semantic validation also checks file-oriented wording such as `Source A states`.

### The final document says “the material states” or refers to an unavailable example

Inspect the deterministic findings in:

```text
output/.markdown-consolidator-work/validation-report.json
```

The validator emits `meta_source_narration_in_publication` for phrases that point back to temporary inputs. It also verifies exact `publication_evidence` for every non-structural unit and requires `detail_excerpt` plus `explanation_excerpt` for every example unit.

### The output is still a summary

Confirm the installed `SKILL.md` contains the heading `Non-negotiable completion rule` and the frontmatter description includes `lossless semantic consolidation`.

Invoke the skill explicitly with:

```text
Preserve every informational unit; do not summarize. Require 100% source-line, unit-disposition, and final-representation coverage.
```

### The final document becomes very long

That is expected when sources contain substantial unique information. Use sections and appendices to improve navigation; do not shorten by omission.

## Scope

Suitable for technical documentation, research notes, architecture documents, policies, requirements, migration guides, and knowledge-base consolidation.

Not intended for summarization, simple concatenation, single-file proofreading, or externally verifying whether source claims are true.
