---
name: note-workflow
description: Route note-related work to the smallest user-intent workflow that fits. Use when the request is about maintaining this knowledge base but it is not yet clear whether the user is ingesting source material, scaffolding learning, authoring known content, reviewing, refactoring, enriching links, or consolidating multiple sources.
---

# Note Workflow Router

This skill owns **workflow selection only**. It does not perform note semantics or edits.

## Routing table

- Supplied article, transcript, scratch text, lecture notes, or other source content to absorb → `$note-ingestion`.
- Multiple overlapping sources, contradictory evidence, or explicit exhaustive-preservation requirement → `$markdown-consolidator`.
- User wants a structure to learn a topic before the content is known → `$note-scaffolding`.
- User already knows the concept and wants it added/explained, or wants a confusing explanation repaired → `$note-authoring`.
- User asks for assessment/opportunities without applying changes → `$note-review`.
- User wants content moved, split, merged, deduplicated, or boundaries repaired across existing notes → `$note-refactor`.
- User specifically wants internal-link opportunities or link enrichment → `$note-link-enrichment`.
- User only asks where the repository already discusses a topic → `$note-topic-search` directly.
- Trivial local typo/wording correction with an obvious target → edit directly; do not invoke a composite workflow.

## Progressive disclosure rule

Choose one primary workflow before loading its instructions. Do not preload sibling workflows. If a workflow later discovers that the request belongs to a heavier sibling workflow, return an escalation signal to the caller/router before durable mutation.

## Output

Return the selected workflow name and a one-sentence routing reason, then invoke that workflow when tool/runtime support permits.