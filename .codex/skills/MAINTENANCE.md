# Codex Skill Maintenance

This document defines how to modify the Codex skill system without creating duplicated policy, contradictory contracts, dependency cycles, or routing drift. It is maintenance guidance for the skill architecture itself; runtime workflow behavior remains documented in `README.md` and the individual skills.

## Sources of truth

Use the smallest canonical source that owns the behavior being changed:

| Concern | Canonical source |
| --- | --- |
| Repository knowledge architecture and global skill principles | `../../AGENTS.md` |
| Global durable-prose and mutation behavior | `../model_instructions.md` |
| Runtime workflow/capability graph and progressive disclosure | `README.md` |
| One workflow or capability's local behavioral contract | `<skill>/SKILL.md` |
| Skill selection and user-facing discoverability | `<skill>/agents/openai.yaml` |
| Conditional specialized procedure | `<skill>/references/*.md` |
| Skill-system maintenance procedure | `MAINTENANCE.md` |

Change a behavior at the lowest canonical abstraction level that owns it. Other documents may describe the dependency, decision gate, or postcondition they rely on, but must not independently redefine the owned procedure.

## Contract boundaries

**Callers own sequencing and decision gates. Callees own execution procedure.**

A caller decides that a capability is required, supplies its accepted inputs, and consumes the postcondition it promises. The callee owns how that capability is executed and verified. For example, `$note-authoring` decides that substantive prose mutation is required and delegates it to `$note-writer`; `$note-writer` owns the writing procedure and delegates post-mutation Markdown lint cleanup to `$markdownlint-fix`; `$markdownlint-fix` owns the lint mechanics.

A caller may state a postcondition it depends on, such as `$note-writer` returning its own Markdown mutations after lint validation, but it should not copy the detailed procedure that establishes that postcondition.

Delegated capability ownership is exclusive. If a workflow delegates placement, boundary analysis, semantic link selection, substantive writing, structural movement, link normalization, or lint cleanup, it must not implement a competing version of that capability itself.

## Change-impact procedure

When changing the skill system:

1. **Classify the change.** Decide whether it belongs to repository policy, global writing behavior, runtime routing, workflow orchestration, a semantic capability, a mutation capability, a mechanical capability, or a conditional reference.
2. **Change the canonical owner first.** Do not begin by copying a new rule into multiple callers.
3. **Inspect direct callers.** Check whether their decision gates, required inputs, or assumed postconditions still match the changed capability.
4. **Inspect direct callees.** Confirm that dependency direction, delegated inputs, and returned postconditions remain valid.
5. **Search for stale copies.** Remove or revise duplicated wording that independently states the old behavior.
6. **Update `README.md` when architecture changes.** Changes to ownership, routing, dependency direction, required versus conditional gates, or progressive disclosure belong in the runtime map.
7. **Update `agents/openai.yaml` only when discoverability changes.** Internal verification details or delegated procedures normally belong only in `SKILL.md`.
8. **Use references for conditional complexity.** Move substantial procedures needed only on a specific branch into `references/` and load them at the relevant gate.
9. **Validate representative execution traces.** Confirm the intended skills load in the intended order and that no lower-level primitive invokes an upward workflow dependency.
10. **Lint modified Markdown documentation.** Run the repository Markdown lint workflow on the maintenance changes before considering the edit complete.

## Dependency invariants

Invocation dependencies flow from higher-level intent workflows toward more concrete capabilities. Lower-level primitives must not invoke workflows that depend on them. Sibling workflows compose shared primitives rather than calling one another merely to reuse behavior.

Progressive disclosure determines when conditional capabilities are loaded; it must not weaken required repository invariants. Required evidence gathering, explicit mutation authority, exclusive capability ownership, and mandatory postconditions remain required even when a workflow tries to minimize the loaded capability set.

When a capability's postcondition changes, inspect every caller that relies on it. A later mutation may invalidate an earlier mechanical postcondition: for example, `$note-writer` may return its own Markdown mutation lint-clean, but a later capability that mutates the same file remains responsible for the validation required by that later stage.

## Skill interface metadata

`agents/openai.yaml` describes when a skill should be selected and its broad user-facing role. Keep it intentionally shallow. Do not mirror the complete `SKILL.md` contract, progressive gates, verification checklist, or delegated implementation procedure there.

Update interface metadata when the skill's selection conditions, broad purpose, or user-facing distinction changes. A purely internal implementation or verification change normally does not require an interface update.

## References and progressive disclosure

A reference file owns a specialized procedure that is too detailed or too conditional to preload with the base skill. The parent `SKILL.md` should state the gate that triggers the reference and the postcondition expected from it, while the reference owns the detailed method.

Do not move a core invariant into a reference merely to reduce the base skill's size. If every execution of the skill requires a rule, keep that rule in the base contract.

## Architectural acceptance traces

After changing routing, ownership, or dependencies, verify representative traces such as these:

```text
Conceptual question
→ note-question
→ read-only
```

```text
Rewrite an existing section in repository style
→ note-authoring
→ note-writer
→ structural/style rewrite
→ markdownlint-fix
```

```text
Incorporate supplied source material
→ note-ingestion
→ knowledge-unit-extractor
→ required repository retrieval
→ conditional placement/boundary analysis
→ note-writer
→ markdownlint-fix
```

```text
Move existing knowledge across note boundaries
→ note-refactor
→ note-boundary-analyzer
→ note-content-mover
→ note-writer only where prose repair is required
→ markdownlint-fix for writer mutations
→ note-cohesion-reviewer
```

```text
Enrich existing prose with semantic links
→ note-link-enrichment
→ note-link-planner
→ note-writer applies approved markup
→ writer-owned validation for its mutation
→ markdown-link-normalizer
```

The exact trace may include additional conditional gates, but the ownership direction must remain stable.

## Maintenance acceptance criteria

Before completing a skill-system change, verify that:

- exactly one canonical owner defines each changed behavior;
- callers state decision gates or relied-upon postconditions without duplicating callee procedures;
- no new upward or cyclic invocation dependency was introduced;
- required invariants were not accidentally converted into optional gates;
- `README.md` matches the actual runtime dependency graph when architecture changed;
- interface metadata still routes users to the correct skill without duplicating internal contracts;
- stale names, obsolete conditions, and superseded behavior were searched for and removed where necessary;
- representative execution traces still satisfy mutation authority and capability ownership;
- modified Markdown documentation passes repository lint validation.
