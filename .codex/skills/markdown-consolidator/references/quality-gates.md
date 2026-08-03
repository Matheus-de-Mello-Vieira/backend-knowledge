# Lossless quality gates

## Severity

### Critical

- Source file overwritten.
- Fabricated claim.
- Hidden high-risk contradiction.
- Destructive corruption of code or procedure.
- Input-file citation, path, filename, source ID, unit ID, or line reference remains in the final publication.
- Meta-source narration makes the final publication depend on unavailable inputs, such as `the material states`, `in the material`, or `the example in the source`.

### High

- Any non-empty source line lacks extraction coverage.
- Any extracted informational unit lacks a disposition.
- Any disposition fails to map to a final representation.
- Any distinct fact, detail, example, procedure step, warning, limitation, rationale, alternative, exception, historical claim, conflict, external reference, or qualifier is absent.
- Equivalent-unit merge loses part of the semantic union.
- Internal coverage traceability is missing or invalid.
- A conflict or variant is identified only by a temporary source label rather than content or scope.
- Any intermediate or reasoning artifact is written outside the configured disposable work directory.
- A non-structural unit has no exact final-document evidence excerpt in the coverage map.
- An example unit is only mentioned or alluded to instead of being presented and explained for a reader who has not seen the inputs.

### Medium

- Repeated wording remains when it can be merged without information loss.
- Terminology or structure is inconsistent.
- Broken internal link, retained external-reference footnote, table, or heading hierarchy.

### Low

- Minor formatting or style issue.

## Pass criteria

A run passes only when:

- Critical findings: 0.
- High findings: 0.
- `source_line_coverage`: 1.0.
- `unit_disposition_coverage`: 1.0.
- `unit_final_representation_coverage`: 1.0 for non-structural units.
- `input_source_reference_violations`: 0.
- `meta_source_phrase_violations`: 0.
- `publication_evidence_coverage`: 1.0.
- `example_exposition_coverage`: 1.0.
- Every inventory source appears in internal `sources_used`.
- Deterministic validation exits successfully.
- Semantic validators confirm no source information was lost.
- The final publication remains understandable after the input files and work directory are deleted.
- Every non-publication artifact is contained under the disposable work directory.

## Issue routing

| Finding | Repair owner |
|---|---|
| Uncovered source line | Source extraction |
| Missing or duplicate unit disposition | Synthesis/coverage map |
| Unit mapped but meaning lost | Synthesis |
| Wrong topic assignment | Topic clustering |
| Incomplete semantic union | Comparison and synthesis |
| Incorrect historical/conflict status | Conflict resolution |
| Unsupported final claim | Synthesis/internal traceability |
| Input-file citation or identifier in publication | Synthesis |
| Meta-source narration or unavailable-example allusion | Synthesis |
| Missing exact publication evidence | Synthesis/coverage map |
| Example not presented and explained | Synthesis |
| Artifact outside disposable work directory | Orchestrator |
| Broken Markdown | Formatting repair |
