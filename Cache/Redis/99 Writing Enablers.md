# Prompts

## Redis CLI Transcript Normalizer

Formats Redis CLI examples into a consistent, readable style by normalizing prompts (`redis>` / `redis[n]>`) and capitalizing Redis command names only, while preserving all arguments, outputs, spacing, and ordering exactly. Performs a mechanical transformation with no interpretation, edits, or added explanations.

```
You will be given a Redis CLI transcript.

Your task is to reformat it only.

Rules:
- Normalize prompts to redis> or redis[n]> if a database index is shown
- Capitalize all Redis command names only
- Preserve keys, arguments, string values, numbers, and output exactly
- Preserve command order, spacing, and line breaks
- Do not add, remove, infer, or explain anything
- Do not modify non-Redis text
- If something is ambiguous, leave it unchanged

Return only the reformatted transcript.

Treat this as a mechanical transformation, not an edit.

```

## Redis CLI Example Generator

Generates Redis CLI command examples with exact, production-style formatting. The output uses normalized `redis>` prompts, uppercase command names, preserved arguments and results, and no comments or explanations—ideal for documentation, tests, and reference snippets where precision matters.

```
Generate a Redis CLI example demonstrating the command <COMMAND>.

Requirements:
- Use `redis>` or `redis[n]>` as the prompt
- Capitalize all Redis command names
- Preserve keys, arguments, string values, numbers, and output exactly
- Preserve command order, spacing, and line breaks
- Include command output inline (no `=>`)
- Do not add comments or explanations
- Output a single code block only
```

