---
name: knowledge-unit-extractor
description: Convert supplied source material into explicit conceptual knowledge units before repository placement or writing. Use for articles, transcripts, scratch notes, pasted explanations, or evidence batches. Supports normal extraction for ordinary ingestion and exhaustive extraction for consolidation workflows.
---

# Knowledge Unit Extractor

This skill owns **source-to-knowledge decomposition**. It does not decide where the extracted knowledge belongs.

## Modes

### Normal

Use for one clean source or a small amount of supplied content. Extract the concepts needed to preserve the substantive meaning without line-by-line accounting.

### Exhaustive

Use when a caller such as `$markdown-consolidator` requires complete source accounting. Preserve provenance, qualifiers, exceptions, uncertainty, contradictory statements, examples, and source ranges according to the caller's contracts.

## Unit model

A unit may be a:

- definition or distinction;
- mechanism or state transition;
- causal claim or consequence;
- constraint, assumption, limitation, or exception;
- comparison or trade-off;
- implementation-specific observation;
- application consequence;
- example or architectural story;
- open question or uncertainty.

Do not split tightly coupled sentences merely to create more units. Do split when the pieces can have different note homes, abstraction levels, qualifiers, or dispositions.

## Capability boundary

Owns:

- preserving the supported semantic content of the supplied source;
- making implicit conceptual units explicit;
- retaining important qualifiers and uncertainty;
- identifying obvious relationships among units.

Must not:

- search the repository;
- choose note destinations;
- decide how much context should remain in a destination;
- write final note prose;
- resolve contradictions by guessing.

## Output contract

Return `units` with, as applicable:

- `concept`;
- `unit_type`;
- `claim_or_scope`;
- `qualifiers`;
- `relationships`;
- `implementation_or_application_context`;
- `source_location` when provenance matters;
- `uncertainty_or_conflict`.

In exhaustive mode, follow the caller's stronger identifiers, source-range, line-coverage, and evidence contracts exactly.