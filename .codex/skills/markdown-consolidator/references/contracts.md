# Data contracts — schema 5.0

All JSON artifacts use UTF-8 and `schema_version: "5.0"`. Store internal artifacts under the disposable work directory. Durable output is either one standalone Markdown publication or the reviewed repository publication set.

## Core lifecycle model

The workflow distinguishes:

- **logical task** — the required work, independent of retries;
- **attempt** — one execution of a logical task;
- **accepted result** — the one attempt selected for downstream use.

A retry creates another attempt under the same logical task. It does not create a second logical responsibility. A stage review is a separate logical task whose accepted attempt evaluates one or more accepted producer attempts.

## Task ledger

`task-ledger.json` is orchestrator-owned.

```json
{
  "schema_version": "5.0",
  "execution_mode": "subagents_required",
  "fallback_used": false,
  "maximum_concurrent_subagents": 3,
  "logical_tasks": [
    {
      "logical_task_id": "extract-source-001",
      "phase": "extraction",
      "allowed_roles": ["source-analyst"],
      "status": "accepted",
      "attempt_ids": [
        "extract-source-001-attempt-1",
        "extract-source-001-attempt-2"
      ],
      "preferred_attempt_id": null,
      "accepted_attempt_id": "extract-source-001-attempt-2",
      "skip_reason": null
    }
  ]
}
```

Logical-task statuses:

`planned`, `queued`, `running`, `accepted`, `failed`, `cancelled`, `skipped`.

The `publication` logical task is the only publication lineage. Its attempts may use role `synthesizer` or `publication-finalizer` and must own the complete unit set. Repository-integrated attempts also own the complete destination set.

## Attempts

`attempts.json` is orchestrator-owned. Completed attempt records are immutable except for lifecycle status changes made by reconciliation.

```json
{
  "schema_version": "5.0",
  "attempts": [
    {
      "attempt_id": "extract-source-001-attempt-2",
      "logical_task_id": "extract-source-001",
      "attempt_number": 2,
      "status": "accepted",
      "task_spec_path": "task-specs/extract-source-001-attempt-2.json",
      "receipt_path": "receipts/extract-source-001-attempt-2.json",
      "output_paths": ["units/extract-source-001-attempt-2.json"],
      "input_attempt_ids": ["outline-attempt-1"],
      "replaces_attempt_id": "extract-source-001-attempt-1",
      "runtime_thread_id": null,
      "started_at": "ISO-8601 timestamp",
      "completed_at": "ISO-8601 timestamp"
    }
  ]
}
```

Attempt statuses:

`planned`, `queued`, `running`, `completed`, `failed`, `cancelled`, `accepted`, `superseded`.

Only accepted attempts may feed downstream attempts.

## Task specification

Write one immutable task specification before spawning each attempt.

```json
{
  "schema_version": "5.0",
  "attempt_id": "extract-source-001-attempt-2",
  "logical_task_id": "extract-source-001",
  "phase": "extraction",
  "role": "source-analyst",
  "nested_delegation": "prohibited",
  "assigned_scope": {
    "source_ids": ["source-001"],
    "topic_ids": [],
    "comparison_ids": [],
    "decision_ids": [],
    "unit_ids": [],
    "validation_categories": [],
    "reviewed_attempt_ids": [],
    "review_categories": [],
    "destination_paths": [],
    "context_paths": [],
    "publication_paths": []
  },
  "publication_context": {
    "audience": "software developers",
    "purpose": "operational reference",
    "publication_mode": "standalone",
    "output_format": "standalone Markdown",
    "assumed_knowledge": ["basic command-line use"],
    "mandatory_overrides": []
  },
  "input_paths": ["inventory.json", "outline.json"],
  "output_paths": ["units/extract-source-001-attempt-2.json"],
  "receipt_path": "receipts/extract-source-001-attempt-2.json",
  "created_at": "ISO-8601 timestamp"
}
```

The task specification is the source of truth for assigned scope. The receipt must not redefine that scope.

## Attempt receipt

A subagent writes one receipt after writing all outputs.

```json
{
  "schema_version": "5.0",
  "attempt_id": "extract-source-001-attempt-2",
  "logical_task_id": "extract-source-001",
  "producer": "subagent",
  "status": "completed",
  "task_spec_sha256": "sha256 of canonical task-spec JSON",
  "completed_scope": {
    "source_ids": ["source-001"],
    "unit_count": 42
  },
  "output_paths": ["units/extract-source-001-attempt-2.json"],
  "warnings": [],
  "completed_at": "ISO-8601 timestamp"
}
```

The receipt proves execution of the immutable task specification. It may report completed scope and counts, but cannot alter assigned scope.

## Inventory

```json
{
  "schema_version": "5.0",
  "root": "/absolute/source/root",
  "generated_at": "ISO-8601 timestamp",
  "sources": [
    {
      "source_id": "guide-md-a1b2c3d4",
      "path": "guide.md",
      "absolute_path": "/repo/docs/guide.md",
      "sha256": "...",
      "bytes": 1234,
      "line_count": 52,
      "nonempty_line_count": 41,
      "headings": [{"level": 1, "text": "Guide", "line": 1}]
    }
  ],
  "errors": []
}
```

## Outline

```json
{
  "schema_version": "5.0",
  "title": "Canonical title",
  "audience": "Requested or safely inferred audience",
  "purpose": "The concrete reader task or decision this document supports",
  "output_format": "Standalone Markdown",
  "assumed_knowledge": ["Source-supported or user-specified prerequisites"],
  "scope": "Complete informational union of selected sources",
  "main_point": "The first substantive conclusion or operative definition",
  "terminology": [
    {
      "canonical_term": "API key",
      "aliases": ["application key"],
      "distinctions": ["OAuth token is a different concept"]
    }
  ],
  "sections": [
    {
      "section_id": "installation",
      "heading": "Installation",
      "purpose": "Explain the installation requirements and ordered procedure",
      "opening_point": "State the installation prerequisites before the steps",
      "content_order": ["definition", "requirements", "steps", "exceptions", "examples"],
      "source_topic_hints": ["setup", "install"]
    }
  ],
  "fallback_sections": [
    "Variants and Alternatives",
    "Historical Information",
    "Unresolved Conflicts",
    "Additional Details",
    "External References"
  ]
}
```

## Content-unit batch

All ranges use one object shape: `{ "start": integer, "end": integer }`.

```json
{
  "schema_version": "5.0",
  "batch_id": "extract-source-001-attempt-2",
  "sources": ["source-001"],
  "units": [
    {
      "unit_id": "source-001-u0001",
      "source_id": "source-001",
      "source_path": "guide.md",
      "heading_path": ["Authentication", "API keys"],
      "source_range": {"start": 20, "end": 24},
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
    {"source_id": "source-001", "range": {"start": 1, "end": 52}}
  ],
  "uncovered_nonempty_lines": [],
  "warnings": []
}
```

Allowed `unit_type` values:

`heading`, `metadata`, `context`, `definition`, `claim`, `rationale`, `procedure`, `requirement`, `recommendation`, `warning`, `limitation`, `exception`, `alternative`, `example`, `quote`, `code`, `table`, `reference`, `open_question`, `structure`.

Every non-empty source line must fall inside at least one unit `source_range`.

## Unit index

Generated by `validate_units.py`:

```json
{
  "schema_version": "5.0",
  "source_ids": ["source-001"],
  "unit_ids": ["source-001-u0001"],
  "unit_count": 1,
  "units_by_source": {"source-001": ["source-001-u0001"]},
  "unit_type_counts": {"requirement": 1},
  "batches": []
}
```

## Topic groups

```json
{
  "schema_version": "5.0",
  "topics": [
    {
      "topic_id": "api-key-usage",
      "canonical_name": "API key usage",
      "aliases": ["key authentication"],
      "unit_ids": ["source-001-u0001"],
      "cross_topic_unit_ids": [],
      "ambiguous_unit_ids": []
    }
  ]
}
```

Every unit has exactly one primary topic assignment.

## Comparison batch

```json
{
  "schema_version": "5.0",
  "batch_id": "compare-001",
  "assigned_topic_ids": ["token-expiration"],
  "assigned_unit_ids": ["source-a-u001", "source-b-u004"],
  "records": [
    {
      "comparison_id": "cmp-0001",
      "topic_id": "token-expiration",
      "unit_ids": ["source-a-u001", "source-b-u004"],
      "relationship": "conflicting",
      "semantic_union": [
        "One behavior uses 30 minutes.",
        "Another uses 60 minutes.",
        "No distinguishing qualifier is supplied."
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

## Decision ledger

```json
{
  "schema_version": "5.0",
  "decisions": [
    {
      "decision_id": "decision-0001",
      "comparison_id": "cmp-0001",
      "topic_id": "token-expiration",
      "unit_ids": ["source-a-u001", "source-b-u004"],
      "outcome": "preserve_both_unresolved",
      "resolution": "Both durations remain because applicability is unresolved.",
      "evidence_unit_ids": ["source-a-u001", "source-b-u004"],
      "unit_presentations": [
        {"unit_id": "source-a-u001", "required_presentation": "preserved_as_conflict", "label": "30-minute behavior"},
        {"unit_id": "source-b-u004", "required_presentation": "preserved_as_conflict", "label": "60-minute behavior"}
      ],
      "confidence": 0.70,
      "requires_human_review": true
    }
  ]
}
```

## Patch proposal

A patch analyst proposes changes but does not own the publication.

```json
{
  "schema_version": "5.0",
  "patch_id": "patch-001",
  "finding_ids": ["finding-017"],
  "affected_unit_ids": ["source-a-u010"],
  "recommended_changes": [
    {
      "location_hint": "Section heading",
      "replacement_markdown": "...",
      "reason": "Restore concrete example details and explanation."
    }
  ],
  "warnings": []
}
```

## Unit dispositions

The publication writer produces dispositions without manually copying evidence strings.

```json
{
  "schema_version": "5.0",
  "document_revision": "publication-attempt-2",
  "unit_dispositions": [
    {
      "unit_id": "source-001-u0001",
      "disposition": "included_directly",
      "destination_path": null,
      "final_section_id": "api-keys",
      "notes": null
    }
  ]
}
```

Allowed dispositions:

`included_directly`, `merged_equivalent`, `included_as_detail`, `preserved_as_variant`, `preserved_as_conflict`, `preserved_as_historical`, `preserved_in_appendix`, `represented_by_structure`, `represented_in_existing_note`.

`destination_path` is required in repository-integrated mode and null in standalone mode.

## Annotated publication markers

The annotated draft uses temporary, line-only markers:

```md
<!-- MC:BEGIN source-001-u0001 evidence -->
Pass the API key in the `Authorization` header.
<!-- MC:END source-001-u0001 evidence -->
```

One passage may support multiple equivalent units:

```md
<!-- MC:BEGIN source-a-u001,source-b-u004 evidence -->
The behavior applies under both documented configurations.
<!-- MC:END source-a-u001,source-b-u004 evidence -->
```

Examples require separate markers:

```md
<!-- MC:BEGIN example-u001 detail -->
A learner receives lessons remotely and completes activities later in the day.
<!-- MC:END example-u001 detail -->

<!-- MC:BEGIN example-u001 explanation -->
This separates delivery location from participation timing: remote instruction does not imply synchronous participation.
<!-- MC:END example-u001 explanation -->
```

Markers cannot be nested. Standalone mode uses `materialize_publication.py`; repository-integrated mode uses `materialize_publication_set.py`.

## Coverage map

Generated mechanically from the annotated draft and unit dispositions:

```json
{
  "schema_version": "5.0",
  "document": "consolidated.md",
  "sources_used": ["source-001"],
  "unit_dispositions": [
    {
      "unit_id": "source-001-u0001",
      "disposition": "included_directly",
      "final_section_id": "api-keys",
      "publication_evidence": ["Pass the API key in the `Authorization` header."],
      "example_representation": null
    }
  ]
}
```

The final publication contains neither markers nor internal identifiers.

## Stage-review report

A `stage-reviewer` writes one read-only report for the accepted producer attempts in its immutable task specification.

```json
{
  "schema_version": "5.0",
  "review_id": "review-extraction-wave-001-attempt-1",
  "review_stage": "extraction",
  "reviewed_attempt_ids": ["extract-batch-001-attempt-2"],
  "status": "passed",
  "errors": [],
  "warnings": [],
  "findings": [
    {
      "finding_id": "review-finding-001",
      "severity": "high",
      "artifact": "units/extract-batch-001-attempt-2.json",
      "unit_ids": ["source-001-u0007"],
      "excerpt": "...",
      "violated_contract": "Preserve every example outcome.",
      "practical_effect": "The downstream publication cannot reproduce the complete example.",
      "repair_owner": "source-analyst"
    }
  ],
  "metrics": {}
}
```

`status` may be `passed` only when no blocking error or finding remains. `reviewed_attempt_ids` must exactly match the review task specification. A review report never modifies producer artifacts.

## Validation report

Every semantic finding must be operational rather than vague. It identifies the location or unit IDs, the smallest useful excerpt, the violated rule, the practical effect, severity, and repair owner.

```json
{
  "schema_version": "5.0",
  "status": "passed",
  "errors": [],
  "warnings": [],
  "findings": [
    {
      "finding_id": "finding-001",
      "category": "writing_quality",
      "severity": "medium",
      "section": "Authentication requirements",
      "unit_ids": ["source-001-u0001"],
      "excerpt": "Authentication should be handled appropriately.",
      "violated_rule": "Express requirements as explicit rules or checks.",
      "practical_effect": "The reader cannot determine the required authentication behavior.",
      "repair_owner": "publication-finalizer"
    }
  ],
  "metrics": {}
}
```

## Companion-skill registry

`companion-skills.json` records located companion installations.

```json
{
  "schema_version": "5.0",
  "status": "passed",
  "repository_root": "/repo/notes",
  "skills": {
    "note-home-finder": {
      "skill_dir": "/repo/notes/.codex/skills/note-home-finder",
      "skill_file": "/repo/notes/.codex/skills/note-home-finder/SKILL.md"
    },
    "markdown-link-normalizer": {
      "skill_dir": "/repo/notes/.codex/skills/markdown-link-normalizer",
      "skill_file": "/repo/notes/.codex/skills/markdown-link-normalizer/SKILL.md",
      "normalize_script": ".../normalize_markdown_links.py",
      "validate_script": ".../validate_markdown_links.py"
    }
  },
  "errors": []
}
```

## Placement plan

Produced by the `note-home-finder-adapter` after following the installed companion skill.

```json
{
  "schema_version": "5.0",
  "publication_mode": "repository_integrated",
  "outcome": "split_across_notes",
  "confidence": "high",
  "destinations": [
    {
      "path": "Security/OAuth.md",
      "action": "extend",
      "assigned_topics": ["refresh-token-rotation"],
      "rationale": "The topic is a direct subsection of the existing OAuth note."
    },
    {
      "path": "Web APIs/Token Renewal Failures.md",
      "action": "create",
      "assigned_topics": ["renewal-failure-handling"],
      "rationale": "Failure handling has a distinct operational reading intent."
    }
  ],
  "related_notes": [
    {
      "path": "Security/Token Storage.md",
      "relationship": "prerequisite",
      "relevant_headings": ["Server-side storage"]
    }
  ],
  "alternatives": [],
  "rationale": "The source topics map to two established repository clusters."
}
```

Destination actions are `reuse`, `extend`, or `create`. Placement outcomes are `reuse_existing_note`, `extend_existing_note`, `create_new_note`, or `split_across_notes`.

## Repository context index

Generated deterministically from the reviewed placement plan.

```json
{
  "schema_version": "5.0",
  "repository_root": "/repo/notes",
  "notes": [
    {
      "path": "Security/OAuth.md",
      "role": "destination",
      "exists": true,
      "snapshot_path": "/work/destination-snapshots/Security/OAuth.md",
      "sha256": "...",
      "line_count": 120,
      "headings": [{"level": 1, "text": "OAuth", "line": 1}]
    }
  ]
}
```

## Integration plan

```json
{
  "schema_version": "5.0",
  "publication_mode": "repository_integrated",
  "destinations": [
    {
      "path": "Security/OAuth.md",
      "action": "extend",
      "assigned_unit_ids": ["source-001-u0001"],
      "section_operations": [
        {
          "operation": "extend_section",
          "existing_heading": "Refresh tokens",
          "assigned_unit_ids": ["source-001-u0001"]
        }
      ],
      "protected_headings": ["OAuth", "Refresh tokens"],
      "heading_changes": []
    }
  ],
  "link_plan": [
    {
      "from_path": "Security/OAuth.md",
      "from_section": "Refresh tokens",
      "to_path": "Security/Token Storage.md",
      "to_heading": "Server-side storage",
      "relationship": "prerequisite",
      "reason": "Refresh-token rotation depends on secure token storage."
    }
  ],
  "terminology_constraints": [],
  "intentional_repetition": [],
  "modified_context_paths": []
}
```

Every source unit appears exactly once across `destinations[].assigned_unit_ids`. Context notes are read-only and cannot appear in `modified_context_paths`.

## Publication manifest

Repository-integrated synthesis writes one manifest for the complete candidate set.

```json
{
  "schema_version": "5.0",
  "publication_mode": "repository_integrated",
  "revision": "publication-attempt-2",
  "publications": [
    {
      "path": "Security/OAuth.md",
      "action": "extend",
      "annotated_path": "/work/drafts/publication-attempt-2/Security/OAuth.md",
      "assigned_unit_ids": ["source-001-u0001"]
    }
  ]
}
```

Paths are repository-relative and must match the reviewed placement and integration plans.

## Repository coverage map

`materialize_publication_set.py` generates exact evidence across all destination notes.

```json
{
  "schema_version": "5.0",
  "publication_mode": "repository_integrated",
  "documents": ["Security/OAuth.md"],
  "sources_used": ["source-001"],
  "unit_dispositions": [
    {
      "unit_id": "source-001-u0001",
      "disposition": "included_directly",
      "destination_path": "Security/OAuth.md",
      "final_section_id": "refresh-tokens",
      "publication_evidence": ["Rotate refresh tokens after each successful renewal."],
      "example_representation": null
    }
  ]
}
```

## Link-pipeline report

`run_link_pipeline.py` records the exact installed companion skill, normalization runs, baseline link failures, final failures, and newly introduced failures. The report passes only when no new or source-deletion-exposed local file or anchor failure remains.
