# Evidence materialization

Exact evidence is generated from temporary markers, not copied manually into JSON.

The writer surrounds durable passages with `MC:BEGIN` and `MC:END` markers.

- Standalone mode uses `materialize_publication.py`.
- Repository-integrated mode uses `materialize_publication_set.py` with the complete publication manifest.

Both scripts remove markers, write clean Markdown candidates, and derive exact `publication_evidence` excerpts. Repository mode also records each unit's durable `destination_path`.

Examples use separate detail and explanation markers. Materialization rejects missing, empty, nested, mismatched, or identical detail/explanation evidence.

Re-run materialization after every accepted publication revision. Never hand-edit the coverage map.
