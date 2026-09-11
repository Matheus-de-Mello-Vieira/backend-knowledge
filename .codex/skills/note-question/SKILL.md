---
name: note-question
description: Answer conceptual questions about technical material or existing notes, then inspect repository coverage without editing. Use when the user is learning, checking understanding, or asking whether the notes already explain something and has not explicitly requested a repository change.
---

# Note Question

This workflow owns **conceptual question → technical answer → repository coverage check**.

It is strictly read-only. A question that reveals ambiguous, incomplete, or incorrect documentation is evidence of a possible documentation defect, not authorization to repair it.

## Workflow

### 1. Answer first

Answer the user's technical question directly before evaluating the documentation state. Use relevant note context and repository terminology when useful, but do not assume the current note is correct merely because it exists.

### 2. Inspect local context

When the question refers to an existing note, section, or recent discussion about one, inspect that material and determine whether it already answers the question.

Classify the local documentation state as one of:

- `answered_clearly`
- `answered_but_ambiguous`
- `missing_required_local_context`
- `not_answered`

### 3. Search broader coverage only when needed

Invoke `$note-topic-search` when broader repository evidence materially affects the documentation assessment, including when:

- the local note does not answer the question;
- another note may already contain the explanation;
- the question spans neighboring concepts or abstraction levels;
- same-level duplication or canonical ownership would change the assessment.

Do not perform repository-wide search when the explicitly referenced local material already settles the documentation question.

### 4. Compare answer and coverage

Report separately:

- the technical answer;
- what the referenced note currently establishes;
- relevant repository coverage found elsewhere, when searched;
- whether the documentation is clear, ambiguous, locally incomplete, or missing.

Do not let repository wording replace the technical answer. Distinguish conceptual truth from documentation state.

### 5. Stop before mutation

Do not edit files or invoke mutation workflows/capabilities. In particular, do not invoke `$note-authoring`, `$note-refactor`, `$note-writer`, or `$note-content-mover`.

If the user later explicitly asks to repair or incorporate the finding, the next request should be routed again and may select a mutation workflow.

## Output

Answer the conceptual question in normal explanatory prose, then concisely state whether and where the current notes already answer it. If a documentation defect is found, describe the defect without applying a fix.

## Constraints

- Do not infer mutation intent from the fact that the user is discussing a repository note.
- Do not infer mutation intent from earlier edits in the same conversation.
- Do not silently convert a learning question into a note review or authoring task.
- Do not ask the user whether to edit unless their current request genuinely requires a choice; simply stop after the read-only answer and coverage assessment.
