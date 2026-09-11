# Multi-note Refactor

Load this reference only when ownership is unresolved across several notes or the change may create/split destinations.

1. Retrieve the smallest relevant neighborhood, not the entire repository.
2. Use `$note-home-finder` to establish one reading intent and abstraction level per destination.
3. Build a concept-by-destination matrix before mutation.
4. Use `$note-boundary-analyzer` to classify canonical coverage, required local context, examples, implementation/application handoffs, and duplicates.
5. Apply structural changes in dependency order so a destination exists before source content is removed.
6. Validate the complete affected set after all moves rather than reviewing each file in isolation.

Do not turn taxonomy cleanup into broad unrelated prose rewriting.