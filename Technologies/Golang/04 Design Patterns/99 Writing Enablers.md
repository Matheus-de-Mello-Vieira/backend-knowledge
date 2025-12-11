GoF book: https://www.javier8a.com/itc/bd1/articulo.pdf


Prompt
```
Consolidate everything we discussed into a GoF-style explanation of the design pattern adapted to Go.

Follow these requirements precisely:

General style requirements:
- Use clear, direct language suitable for an experienced engineer.
- Avoid meta-commentary or self-referential explanations.
- Use headings only; do not use horizontal dividers.
- Prefer bullet points with **bold labels followed by inline explanations** whenever suitable.
- Skip any section where the pattern has no meaningful or defensible content (do not force filler).

Bullet-point formatting rules (strict):
- All explanatory bullets must follow exactly this format:
  * **Bold label**: inline explanation.
- Do not split the label and the explanation across lines.
- Do not add extra prose between bullets.

Required sections:

## Motivation
- Introduce a realistic Go scenario where the pattern is useful.
- Explain concrete problems that arise without the pattern.
- Keep the explanation technical and succinct.

## Sample Code
- Provide Go code demonstrating the pattern’s structure.
- Include relevant components (Product, Interface, Concrete Types, Client, etc.).
- Keep code idiomatic, minimal, and focused on the essence of the pattern.

## Consequences
- Use bullets.
- Each bullet must follow the strict bullet format defined above.

## Implementation
- Discuss variants, trade-offs, and Go-specific considerations.
- Use bullets where appropriate, following the same bullet rules.
- Avoid repeating generic GoF theory; assume the reader knows the classical pattern.

## Go-Idiomatic Alternatives
- Present Go-native approaches (interfaces, closures, functional options, etc.) when they meaningfully address the same challenges.
- Explain when these alternatives should be preferred.
- Include snippets only if necessary.
- Use the same bullet format when employing bullets.
- Skip this section if the pattern maps cleanly to Go without distinct alternatives.

## Known Uses
- Provide real examples from:
  - The Go standard library (when relevant).
  - Well-known third-party libraries or frameworks.
  - Established OSS projects that employ the pattern in recognizable form.
- Use bullet points (following the strict bullet format) when listing examples.
- Skip this section if there are no widely recognized or high-quality uses in Go.

Formatting rules:
- Use markdown headings (##, ###), bullet lists, and fenced Go code blocks.
- Do not use horizontal rules.
- Maintain a depth of explanation comparable to the Builder Pattern (Go Context) example.
```

