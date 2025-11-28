# Patterns

## Repository

Functions:

```typescript
export interface IRepository<T> {
  findById(id: string | number): Promise<T | null>;
  findAll(): Promise<T[]>;
  create(entity: T): Promise<T>;
  update(id: string | number, data: Partial<T>): Promise<T>;
  delete(id: string | number): Promise<void>;
}
```

## Slug

A “slug” in backend development is a human-readable, URL-safe identifier derived from a resource’s title or name, used to look up and link to that resource. It’s typically lowercase, contains only safe characters (letters, numbers, hyphens), and avoids spaces and punctuation. Example: a blog post titled “Hello, World!” becomes the slug “`hello-world`”.

### Why slugs are used

- **Readability**: URLs like /blog/hello-world are easy to read and share.
- **SEO**: Search engines favor descriptive URLs.
- **Routing**: Slugs can uniquely identify resources in application routes.
- **Stability**: Often kept immutable to avoid broken links.

### Common characteristics

- Lowercase
- Whitespace replaced with hyphens
- Special characters removed or transliterated
- Normalized Unicode: converting Unicode text into a standard, consistent representation so that equivalent strings compare equal and behave predictably.
  - Unicode allows multiple ways to represent the same visible text; normalization resolves those differences.
  - Don’t try to normalize Unicode yourself. Use existing tools.
    - **JavaScript**: `String.prototype.normalize('NFC' | 'NFD' | 'NFKC' | 'NFKD')`
    - **Python**: `unicodedata.normalize(form, s)`
    - **Java**: `java.text.Normalizer.normalize(s, Form.NFC)`
    - Many frameworks’ slugify libraries handle normalization internally.
  - The main Unicode normalization forms:
    - **NFC (Normalization Form C, composed)**: combines base letters + combining marks into single precomposed characters where possible. Common for storing/displaying text on the web.
    - **NFD (Normalization Form D, decomposed)**: splits precomposed characters into base + combining marks. Useful for certain processing tasks (e.g., stripping diacritics).
    - **NFKC (Normalization Form KC, compatibility composed)**: like NFC, but also maps compatibility equivalents to their standard forms (e.g., “①” → “1”). Good for identifiers when you want stricter equivalence and fewer surprises.
    - **NFKD (Normalization Form KD, compatibility decomposed)**: decomposed plus compatibility mappings. Often used when you need to strip accents or reduce text to a simpler form, but it can be lossy.
- Uniqueness enforced (e.g., “`hello-world-2`” if “`hello-world`” already exists)

### How slugs are generated

1. Normalize text (trim, lowercase, and unicode).
2. Optionally transliterate non-ASCII (e.g., “Café” → “cafe”).
   * transliterate non-ASCII is easier after the normalization.
3. Remove disallowed characters.
4. Replace spaces with hyphens; collapse multiple hyphens.
5. Enforce length limits and avoid stopwords or reserved paths if needed.
6. Ensure uniqueness (check database; append a suffix if collision).

### Storage and constraints

- Store in a dedicated slug column with a unique index (often scoped per collection, e.g., unique per author or per site).
- Consider immutability after publish; if changes are allowed, manage redirects from old slugs.

### Security and robustness:

- Don’t put sensitive data in slugs (e.g., user emails).
- Validate allowed characters and normalize Unicode to prevent confusable lookalikes.
