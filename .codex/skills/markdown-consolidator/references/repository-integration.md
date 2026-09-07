# Repository integration protocol

Apply this protocol only when `publication_mode` is `repository_integrated`.

The consolidator owns evidence-to-publication orchestration. Repository placement, content boundaries, writing/mutation, and link mechanics are delegated to their canonical skills.

## File classes

Classify every relevant Markdown file as exactly one of:

- **Evidence source:** selected input whose supported information must be represented; may be deleted after publication.
- **Destination note:** durable note created, reused, or extended by the workflow.
- **Context note:** durable read-only neighboring note used for taxonomy, terminology, boundaries, or link targets.

A context note is not evidence and does not satisfy source-unit coverage unless it becomes an approved destination.

## Placement

Delegate placement to `$note-home-finder`.

Allowed outcomes are `reuse_existing_note`, `extend_existing_note`, `create_new_note`, and `split_across_notes`. Prefer extending a suitable canonical note over creating a duplicate. Split when distinct topics have different natural homes, abstraction levels, or reading intents.

## Boundary analysis

After placement and before integration planning, apply `$note-boundary-analyzer`.

Every substantial source unit must be assigned as canonical explanation, required local context, bounded example, implementation/application detail assigned elsewhere, or intentional repetition with explicit justification. One source unit still has exactly one primary destination; repeated context is secondary and limited to what another note genuinely needs.

## Existing-note preservation

Snapshot every existing destination and context note before synthesis. Preserve supported content, external references, local links, terminology, note purpose, and headings by default. Require an approved heading change for removal or rename. Keep context notes read-only unless promoted to destinations.

## Integration plan

The integration planner receives accepted placement, repository snapshots, source units, conflict decisions, and the exact `$note-boundary-analyzer` instructions. It assigns every source unit one primary destination, section operations, protected headings, terminology constraints, semantic links, and intentionally repeated local context with its boundary justification.

Do not invent a separate note-boundary policy inside the consolidator.

## Structural mutation

When accepted integration requires moving existing durable repository material between notes, apply `$note-content-mover` to the approved move/split/merge plan. When the required operation is a broader cross-note cleanup, delegate that scope to `$note-refactor`.

The consolidator must not silently reimplement cross-note mutation semantics inside the synthesizer.

## Repository writing

The repository synthesizer and finalizer receive the exact `$note-writer` instructions. The writer writes only assigned material, preserves each note's center of gravity and abstraction level, keeps examples subordinate, avoids same-level duplication, and preserves enough local context for the note's own argument.

The consolidator's standalone writing policy does not override `$note-writer` for repository-specific prose decisions.

## Link relationships

Use links only when they clarify a real relationship such as broader context, prerequisite, implementation detail, contrast, alternative, example, continuation, or related mechanism. Semantic link placement follows repository rules; mechanical normalization and target validation are delegated to `$markdown-link-normalizer`.

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
