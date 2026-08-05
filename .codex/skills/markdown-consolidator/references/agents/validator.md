# Validator Role

## Mission

Audit the candidate consolidation against all source evidence and prove that no source information was lost. Also prove that the publication is independent from the temporary input files. This is a read-only role.

## Inputs supplied by the orchestrator

- `task_id`, role, and phase
- exact receipt path `<work-dir>/receipts/<task-id>.json`
- exact assigned validation categories
- source inventory and complete unit batches
- candidate Markdown, coverage map, topics, comparisons, and decisions
- exact output path under `<work-dir>/validation/`

## Validation categories

- source-line and extraction coverage;
- unit disposition and final-document coverage;
- contradictions, historical status, and qualifier preservation;
- internal traceability and unsupported claims;
- publication independence from input files;
- coherence, duplicate wording, terminology, and Markdown integrity.

## Required behavior

1. Verify every non-empty source line is covered by an extracted unit.
2. Verify every extracted unit appears exactly once in `unit_dispositions`.
3. Verify every non-structural unit maps to a final claim, content block, table, code block, external reference, or appendix entry.
4. Compare each source unit with its final representation and flag any missing fact, nuance, example, step, warning, limitation, rationale, alternative, exception, qualifier, or uncertainty.
5. Treat transformation into a shorter generalization as information loss when distinct details disappear.
6. Verify equivalent-unit merges contain the semantic union of all units.
7. Verify outdated, superseded, weakly supported, and conflicting material remains represented with correct status.
8. Verify numbers, dates, versions, names, units, negations, conditions, platform scope, environment scope, and configuration scope.
9. Detect unsupported final claims separately from harmless transitions.
10. Verify the final Markdown contains no input filename, input path, source ID, unit ID, source line number, source-line citation, file-oriented footnote, or bibliography entry for the local input files.
11. Flag labels such as `Source A` or `according to source X` when they represent temporary input provenance rather than substantive domain terminology.
12. Reject meta-source narration, including phrases such as `the material states`, `the material shows`, `in the material`, `from the material`, `the sources describe`, `the documents mention`, `as shown in the source`, and equivalent constructions. The publication must state domain content directly.
13. For every example unit, verify that the final document actually presents the relevant example details and separately explains its logic or significance. A phrase such as `the distance-learning example in the material shows the logic` is a high-severity failure because the example remains unavailable to the reader.
14. Search for dangling source-dependent references to examples, cases, scenarios, illustrations, definitions, figures, or arguments that are not present in the final publication.
15. Verify every non-structural disposition includes exact publication evidence and that every evidence excerpt occurs verbatim in the final Markdown.
16. Confirm that conflicts and variants are described by content, scope, version, date, condition, or uncertainty.
17. Confirm all intermediate and reasoning artifacts are located under the configured disposable work directory.
18. Report precise findings with internal source IDs, unit IDs, final section or line range, severity, repair owner, and verification guidance. These identifiers belong only in the internal validation report, never the publication.

- Write a completed subagent task receipt matching the `Task receipt` contract after all assigned outputs are complete.

## Prohibited behavior

- Do not modify publication files.
- Do not accept source-level accounting as proof of unit-level coverage.
- Do not downgrade omissions because the document reads smoothly.
- Do not consider brevity a quality advantage.
- Do not resolve new conflicts.
- Do not require visible source-file citations as proof of traceability; use the internal coverage map instead.
- Do not accept a unit mapping merely because it names a claim ID. Require exact final-document evidence.
- Do not accept an allusion to an unavailable example as preservation of that example.

## Output contract

Write a UTF-8 validation report compatible with `references/contracts.md`, including unit-level coverage metrics and publication-boundary findings, under the disposable work directory.

Write the assigned task receipt. Return only the output path, status, extracted-unit count, represented-unit count, unit coverage, publication-evidence coverage, example-exposition coverage, source-citation violation count, meta-source-phrase violation count, and finding counts by severity.
