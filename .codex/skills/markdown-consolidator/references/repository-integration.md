# Repository integration protocol

Apply this protocol only when `publication_mode` is `repository_integrated`.

The consolidator owns evidence-to-publication orchestration. Repository placement, content boundaries, writing, and link mechanics are delegated to their canonical skills.

## File classes

Classify every relevant Markdown file as exactly one of:

- **Evidence source:** selected input whose supported information must be represented; may be deleted after publication.
- **Destination note:** durable note created, reused, or extended by the workflow.
- **Context note:** durable read-only neighboring note used for taxonomy, terminology, boundaries, or link targets.

A context note is not evidence and does not satisfy source-unit coverage unless it becomes an approved destination.

## Placement

Delegate placement to `$note-home-finder`.

Allowed outcomes:

- `reuse_existing_note`
- `extend_existing_note`
- `create_new_note`
- `split_across_notes`

Prefer extending a suitable canonical note over creating a duplicate. Split when distinct topics have different natural homes, abstraction levels, or reading intents.

## Boundary analysis

After placement and before integration planning, apply `$note-boundary-analysis`.

Every substantial source unit must be assigned as one of:

- canonical explanation in its primary destination;
- required local context;
- bounded example;
- implementation/application detail assigned elsewhere;
- intentional duplication with explicit justification.

One source unit still has exactly one **primary destination**. Repeated context is secondary and must be limited to what another note genuinely needs for local comprehension.

## Existing-note preservation

Snapshot every existing destination and context note before synthesis.

Mandatory rules:

- preserve existing supported content, external references, local links, terminology, and note purpose;
- preserve existing headings by default;
- require an approved heading change for removal or rename;
- integrate new content into the conceptually appropriate section;
- keep context notes read-only unless the placement plan promotes them to destinations.

Independent publication review must compare candidates with snapshots and report semantic loss, scope drift, boundary violations, or unnecessary restructuring.

## Integration plan

The integration planner receives:

- accepted placement;
- repository snapshots;
- source units;
- conflict decisions;
- the exact `$note-boundary-analysis` instructions.

It assigns:

- every source unit to one primary destination;
- section operations for each destination;
- protected headings and approved heading changes;
- terminology constraints;
- outgoing links with relationship and reason;
- any intentionally repeated local context and its boundary justification.

Do not invent a separate note-boundary policy inside the consolidator.

## Repository writing

The repository synthesizer and finalizer receive the exact `$note-writer` instructions.

The writer must:

- write only material assigned to each destination;
- preserve each note's center of gravity and abstraction level;
- keep examples subordinate;
- avoid duplicate same-level explanations;
- preserve enough local context for the note's own argument.

The consolidator's standalone writing policy does not override `$note-writer` for repository-specific prose decisions.

## Link relationships

Use links only when they clarify a real relationship such as:

- broader context;
- prerequisite;
- implementation detail;
- contrast;
- alternative;
- example;
- continuation;
- related mechanism.

Semantic link placement follows repository rules; mechanical normalization and target validation are delegated to `$markdown-link-normalizer`.

## Publication set

Every source unit has one primary destination. Intentional repeated context must be recorded in the integration plan and must not replace primary coverage.

Materialize candidates under the work directory. Do not write durable repository paths until content, boundary, writing, integration, review, lifecycle, delegation, and link validation pass.

## Final validation

Repository-integrated publication requires:

- complete unit representation across the publication set;
- one canonical primary destination per source unit;
- no accidental same-level duplication;
- destination notes centered on their intended subjects and abstraction levels;
- no reference or link to disposable evidence files;
- preserved baseline headings unless an approved migration exists;
- planned semantic links present and mechanical links valid;
- no new broken local files or anchors;
- context notes unchanged unless promoted to destinations;
- destination paths and actions matching the reviewed placement plan.
