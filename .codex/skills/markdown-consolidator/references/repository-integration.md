# Repository integration protocol

Apply this protocol only when `publication_mode` is `repository_integrated`.

## File classes

Classify every relevant Markdown file as exactly one of:

- **Evidence source:** selected input whose complete supported information must be represented; may be deleted after publication.
- **Destination note:** durable note created, reused, or extended by the workflow.
- **Context note:** durable read-only neighboring note used for taxonomy, terminology, boundaries, or link targets.

A context note is not evidence. Its content does not satisfy source-unit coverage unless the placement plan makes it a destination and the integration plan maps the relevant source units to exact durable passages.

## Placement outcomes

Allowed outcomes:

- `reuse_existing_note`
- `extend_existing_note`
- `create_new_note`
- `split_across_notes`

Prefer extending a suitable note over creating a duplicate. Reuse without changes is valid only when every source unit maps to exact content already present in the destination. Split when distinct topics have different natural homes or reading intents.

## Existing-note preservation

Snapshot every existing destination and context note before synthesis.

Mandatory rules:

- Preserve existing supported content, external references, local links, terminology, and note purpose.
- Preserve existing headings by default.
- A removed or renamed heading requires an approved `heading_changes` entry.
- Integrate new content into appropriate sections; do not append a generic catch-all section when a specific section exists.
- Context notes remain unmodified unless explicitly promoted to destinations.

Independent publication review must compare each candidate with its snapshot and report semantic loss, scope drift, or unnecessary restructuring.

## Integration plan

After conflict decisions and before writing, one `integration-planner` assigns:

- every source unit to exactly one primary destination;
- section operations for each destination;
- protected headings and approved heading changes;
- terminology constraints derived from neighboring notes;
- outgoing links with relationship and reason;
- any intentional repeated context across notes.

A link never replaces required source information unless the linked durable note is verified to contain the complete mapped information. Each generated note must remain locally comprehensible.

## Link relationships

Use links only when they clarify one of these relationships:

- broader context
- prerequisite
- implementation detail
- contrast
- alternative
- example
- continuation
- related mechanism

State the relationship in nearby prose. Do not insert links mechanically on repeated terms.

## Publication set

The publication logical task may produce one or more annotated notes. Every source unit has one primary destination. Intentional duplication must be declared in the integration plan and must not replace primary coverage.

Materialize candidates under the work directory. Do not write to durable repository paths until content, writing, integration, review, lifecycle, delegation, and link validation all pass.

## Final validation

Repository-integrated publication requires:

- complete unit representation across the publication set;
- no reference or link to disposable evidence files;
- preserved baseline headings unless an approved migration exists;
- all planned links present and contextual;
- no new broken local files or anchors in the final repository shadow;
- context notes unchanged unless they are destinations;
- destination paths and actions matching the reviewed placement plan.
