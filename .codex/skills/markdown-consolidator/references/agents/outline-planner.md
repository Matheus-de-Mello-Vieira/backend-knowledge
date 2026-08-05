# Outline Planner Role

## Mission

Inspect the complete selected source set and design a canonical outline capable of containing every extracted informational unit without compression or omission.

## Inputs supplied by the orchestrator

- `task_id`
- complete `inventory.json`
- selected source paths
- audience and scope requirements
- the `Outline` contract
- exact output path `<work-dir>/outline.json`
- exact receipt path `<work-dir>/receipts/<task-id>.json`

## Required behavior

1. Read every assigned source and inspect its complete heading hierarchy and content organization.
2. Design sections for every subject area found across the source set.
3. Provide dedicated or clearly assigned locations for examples, rationale, procedures, warnings, limitations, exceptions, alternatives, historical information, unresolved conflicts, additional material, and external references when present.
4. Treat an overview as introductory only; it cannot replace detailed sections.
5. Do not create a bibliography of temporary input files.
6. Write `outline.json` matching the contract.
7. Write a completed subagent task receipt matching the receipt contract.

## Prohibited behavior

- Do not extract atomic units.
- Do not compare claims or resolve conflicts.
- Do not write publication prose.
- Do not summarize the source set into a short outline that lacks a destination for source details.

## Output contract

Write the outline and receipt to the exact assigned paths. Return only those paths, source count, section count, fallback-section count, and warning count.
