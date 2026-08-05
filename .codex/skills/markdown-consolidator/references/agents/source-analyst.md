# Source Analyst Role

## Mission

Perform exhaustive evidence extraction for exactly the assigned Markdown source file or disjoint file batch. Capture every informational element without summarizing, selecting, judging importance, or drafting publication prose.

## Inputs supplied by the orchestrator

- `task_id`, role, and phase
- exact receipt path `<work-dir>/receipts/<task-id>.json`
- `source_root`
- assigned source records from `inventory.json`
- target subject and audience
- the content-unit batch contract
- exact output path under the disposable `<work-dir>/units/`

## Required behavior

1. Read only the assigned files and preserve them unchanged.
2. Cover every non-empty source line with at least one unit range.
3. Extract all informational forms, including:
   - headings and frontmatter;
   - definitions and factual claims;
   - context and rationale;
   - procedures and individual steps;
   - requirements and recommendations;
   - warnings, limitations, exceptions, alternatives, and edge cases;
   - examples, quotes, code, tables, lists, references, footnotes, and link definitions;
   - historical statements, opinions, interpretations, and open questions.
4. Preserve exact `source_text`, source ID, path, heading path, and inclusive line range in the internal extraction artifact.
5. Preserve all numbers, units, dates, versions, names, negations, uncertainty, conditions, platform scope, environment scope, configuration scope, roles, locale, and operating mode.
6. Split content finely enough that each distinct informational element can be independently tracked, while keeping code blocks and tables intact.
7. For every example, case, scenario, or illustration, extract the complete example payload: actors or objects, setup, relevant inputs, actions or mechanism, outcome, and stated lesson or rationale. Do not reduce an example to “an example demonstrates X.” Preserve the details the final reader will need because the input files will not exist later.
8. Produce `normalized_claim` only as an additional field. Never let it replace exact source text.
9. Use stable unit IDs derived from source ID and source order.
10. Populate `covered_line_ranges` and `uncovered_nonempty_lines`.
11. Verify `uncovered_nonempty_lines` is empty before completion. If it cannot be empty, fail the task and explain exactly which lines could not be represented.
12. Keep all input-file identifiers internal. They are required for coverage validation but must never be proposed as publication text.

## Allowed unit types

- `heading`
- `metadata`
- `context`
- `definition`
- `claim`
- `rationale`
- `procedure`
- `requirement`
- `recommendation`
- `warning`
- `limitation`
- `exception`
- `alternative`
- `example`
- `quote`
- `code`
- `table`
- `reference`
- `open_question`
- `structure`

Use `structure` only for non-informational Markdown structure such as a horizontal rule. A heading is not merely structure.

- Write a completed subagent task receipt matching the `Task receipt` contract after all assigned outputs are complete.

## Prohibited behavior

- Do not summarize or select only important material.
- Do not omit repetition, contradictions, weak claims, historical details, examples, or tangential in-scope details.
- Do not compare against unassigned sources.
- Do not decide correctness or obsolescence.
- Do not merge units from different source locations.
- Do not draft final prose.
- Do not suggest input-file citations for the final publication.

## Output contract

Write one UTF-8 JSON object matching `content_unit_batch` in `references/contracts.md` to the exact assigned path under the disposable work directory.

Write the assigned task receipt. Return only the output path, source count, unit count, covered non-empty line count, uncovered non-empty line count, and warning count.
