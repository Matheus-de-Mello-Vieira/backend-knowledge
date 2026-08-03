# Lossless data contracts

Use UTF-8 JSON. Include `schema_version: "2.2"` in every top-level artifact. IDs must be stable across reruns when source content and ordering are unchanged.

All artifacts described here are internal and disposable except the final Markdown publication. Store them under the configured work directory. They may contain source paths and IDs for validation, but those identifiers must never be copied into the final publication.

## Inventory

```json
{
  "schema_version": "2.2",
  "root": "/absolute/source/root",
  "generated_at": "ISO-8601 timestamp",
  "sources": [
    {
      "source_id": "guide-a-md-a1b2c3d4",
      "path": "guide-a.md",
      "sha256": "...",
      "bytes": 1234,
      "line_count": 52,
      "headings": [{"level": 1, "text": "Guide", "line": 1}]
    }
  ],
  "errors": []
}
```

## Outline

```json
{
  "schema_version": "2.2",
  "title": "Canonical title",
  "audience": "Requested or inferred audience",
  "scope": "Complete informational union of inventoried sources",
  "sections": [
    {
      "section_id": "installation",
      "heading": "Installation",
      "purpose": "Contain every installation-related unit",
      "topic_ids": ["installation"]
    }
  ],
  "fallback_sections": [
    "Historical Information",
    "Unresolved Conflicts",
    "Variants and Alternatives",
    "Additional Details",
    "External References"
  ]
}
```

`External References` is only for standards, URLs, publications, and bibliography entries that are themselves present in source content. It must not list the local input files.

## Content-unit batch

```json
{
  "schema_version": "2.2",
  "batch_id": "batch-001",
  "sources": ["guide-a-md-a1b2c3d4"],
  "units": [
    {
      "unit_id": "guide-a-md-a1b2c3d4-u0001",
      "source_id": "guide-a-md-a1b2c3d4",
      "source_path": "guide-a.md",
      "heading_path": ["Authentication", "API keys"],
      "line_start": 20,
      "line_end": 24,
      "unit_type": "requirement",
      "source_text": "API keys must be supplied in the Authorization header.",
      "normalized_claim": "API keys are required in the Authorization header.",
      "topic_hint": "api-key-usage",
      "assertion_kind": "instruction",
      "qualifiers": {
        "versions": ["3.x"],
        "dates": [],
        "platforms": [],
        "environments": [],
        "configurations": [],
        "roles": [],
        "other": []
      },
      "confidence": 0.96,
      "warnings": []
    }
  ],
  "covered_line_ranges": [
    {"source_id": "guide-a-md-a1b2c3d4", "line_start": 1, "line_end": 52}
  ],
  "uncovered_nonempty_lines": [],
  "warnings": []
}
```

Allowed `unit_type` values:

`heading`, `metadata`, `context`, `definition`, `claim`, `rationale`, `procedure`, `requirement`, `recommendation`, `warning`, `limitation`, `exception`, `alternative`, `example`, `quote`, `code`, `table`, `reference`, `open_question`, `structure`.

Allowed `assertion_kind` values:

`fact`, `opinion`, `interpretation`, `instruction`, `example`, `structure`.

Every non-empty source line must be covered by at least one unit range. Overlapping ranges are allowed. `uncovered_nonempty_lines` must be empty.

## Topic groups

```json
{
  "schema_version": "2.2",
  "topics": [
    {
      "topic_id": "api-key-usage",
      "canonical_name": "API key usage",
      "aliases": ["key authentication"],
      "unit_ids": ["..."],
      "cross_topic_unit_ids": [],
      "ambiguous_unit_ids": []
    }
  ]
}
```

Every unit ID must occur in exactly one primary `unit_ids` list.

## Comparison batch

```json
{
  "schema_version": "2.2",
  "batch_id": "comparison-authentication",
  "assigned_unit_ids": ["source-a-u001", "source-b-u004"],
  "records": [
    {
      "comparison_id": "cmp-0001",
      "topic_id": "token-expiration",
      "unit_ids": ["source-a-u001", "source-b-u004"],
      "relationship": "conflicting",
      "semantic_union": [
        "One description states 30 minutes.",
        "Another states 60 minutes.",
        "Neither supplies a distinguishing version qualifier."
      ],
      "rationale": "The durations differ under apparently equal scope.",
      "recommended_action": "preserve_as_conflict",
      "confidence": 0.90
    }
  ],
  "accounted_unit_ids": ["source-a-u001", "source-b-u004"],
  "warnings": []
}
```

Allowed relationships:

`equivalent`, `near_duplicate`, `complementary`, `conflicting`, `conditionally_compatible`, `unique`, `outdated`.

`assigned_unit_ids` and `accounted_unit_ids` must contain the same set.

## Decision ledger

```json
{
  "schema_version": "2.2",
  "decisions": [
    {
      "decision_id": "decision-0001",
      "topic_id": "token-expiration",
      "unit_ids": ["source-a-u001", "source-b-u004"],
      "outcome": "preserve_both_unresolved",
      "resolution": "Both durations remain documented because applicability is unresolved.",
      "evidence_unit_ids": ["source-a-u001", "source-b-u004"],
      "unit_presentations": [
        {
          "unit_id": "source-a-u001",
          "required_presentation": "preserved_as_conflict",
          "label": "30-minute behavior"
        },
        {
          "unit_id": "source-b-u004",
          "required_presentation": "preserved_as_conflict",
          "label": "60-minute behavior"
        }
      ],
      "confidence": 0.70,
      "requires_human_review": true
    }
  ]
}
```

Allowed outcomes:

`merge_equivalent`, `merge_conditionally`, `preserve_primary_and_note_alternative`, `preserve_as_historical`, `preserve_both_unresolved`, `requires_human_review`.

Every decision unit ID must appear in `unit_presentations`. Labels must describe content or scope and must not identify local input files.

## Coverage map

The coverage map is an internal validation artifact. Store it only as `<work-dir>/coverage-map.json`. Do not publish it with the final Markdown.

```json
{
  "schema_version": "2.2",
  "document": "consolidated.md",
  "sources_used": ["guide-a-md-a1b2c3d4"],
  "sections": [
    {
      "section_id": "api-keys",
      "heading": "API Keys",
      "claims": [
        {
          "claim_id": "final-claim-0001",
          "summary": "API keys are passed in the Authorization header.",
          "publication_excerpt": "Pass the API key in the `Authorization` header.",
          "sources": [
            {
              "source_id": "guide-a-md-a1b2c3d4",
              "line_start": 20,
              "line_end": 24,
              "unit_id": "guide-a-md-a1b2c3d4-u0001"
            }
          ]
        }
      ],
      "content_blocks": [
        {
          "block_id": "final-code-0001",
          "block_type": "code",
          "publication_excerpt": "Authorization: Bearer YOUR_API_KEY",
          "source_unit_ids": ["guide-a-md-a1b2c3d4-u0002"]
        }
      ]
    }
  ],
  "unit_dispositions": [
    {
      "unit_id": "guide-a-md-a1b2c3d4-u0001",
      "disposition": "included_directly",
      "final_section_ids": ["api-keys"],
      "final_claim_ids": ["final-claim-0001"],
      "final_block_ids": [],
      "publication_evidence": [
        "Pass the API key in the `Authorization` header."
      ],
      "example_representation": null,
      "notes": "Requirement retained directly."
    }
  ]
}
```

Allowed dispositions:

`included_directly`, `merged_equivalent`, `included_as_detail`, `preserved_as_variant`, `preserved_as_conflict`, `preserved_as_historical`, `preserved_in_appendix`, `represented_by_structure`.

Requirements:

- `sources_used` must contain every inventory source ID.
- Every extracted unit ID must appear exactly once in `unit_dispositions`.
- Every non-`structure` unit must map to at least one final claim ID or final block ID.
- Every non-structural disposition must include a non-empty `publication_evidence` array. Each entry must be an exact excerpt that occurs in the final Markdown; IDs and summaries alone are not proof of representation.
- Units whose `unit_type` or `assertion_kind` is `example` must also include `example_representation` with two exact final-document excerpts:
  - `detail_excerpt`: the passage that actually presents the example's relevant setup, entities, mechanism, steps, and outcome;
  - `explanation_excerpt`: the passage that explains the example's logic, significance, or relationship to the surrounding concept.
- An example is not represented by a sentence that merely refers to “the example,” “the material,” “the source,” or another unavailable input. The reader must receive the example itself and its explanation.
- `represented_by_structure` is allowed only for `heading` or `structure` units and must map to a final section ID.
- Every referenced claim ID, block ID, section ID, source ID, unit ID, and line range must exist and be valid.
- Source paths, IDs, line ranges, and unit IDs in this map are internal only and must not appear in the final Markdown.

## Validation report

```json
{
  "schema_version": "2.2",
  "status": "passed",
  "errors": [],
  "warnings": [],
  "metrics": {
    "source_files": 3,
    "sources_used": 3,
    "source_coverage": 1.0,
    "source_nonempty_lines": 450,
    "covered_nonempty_lines": 450,
    "source_line_coverage": 1.0,
    "extracted_units": 127,
    "units_with_dispositions": 127,
    "unit_disposition_coverage": 1.0,
    "nonstructural_units": 119,
    "nonstructural_units_with_final_representation": 119,
    "unit_final_representation_coverage": 1.0,
    "publication_evidence_coverage": 1.0,
    "example_exposition_coverage": 1.0,
    "input_source_reference_violations": 0,
    "meta_source_phrase_violations": 0
  },
  "findings": []
}
```
