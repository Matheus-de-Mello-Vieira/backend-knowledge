# Learning Structure

Load this reference only after repository neighbors and the likely note home are known.

A learning scaffold should expose the **questions and conceptual dependencies** that will guide study.

## Structure principles

- Begin with the smallest model the learner must understand before details make sense.
- Separate prerequisites already owned by other notes from knowledge this note should eventually own.
- Organize around real conceptual changes: motivation/problem, core model, mechanism, consequences/trade-offs, variants, implementation examples, and applications only when those divisions fit the subject.
- Prefer questions that reveal understanding gaps, such as “What state changes here?”, “Why is this abstraction needed?”, or “Which invariant does this mechanism preserve?”.
- Do not force a universal heading template when the subject has a different natural structure.
- For a multi-note learning path, order notes by conceptual dependency rather than arbitrary taxonomy.

## Repository scaffold form

When creating a durable but incomplete scaffold, prefer headings plus short HTML comments, for example:

```markdown
## Page-table lookup

<!-- Explain the lookup path, the role of each level, and why sparse address spaces make multiple levels useful. -->
```

Do not add visible filler paragraphs whose only purpose is to say what should be learned later.

## Completion boundary

A scaffold is complete when a future learning session can clearly answer:

- what belongs in this note;
- what prerequisite knowledge already lives elsewhere;
- what major questions remain unanswered;
- what order those questions should be studied in.