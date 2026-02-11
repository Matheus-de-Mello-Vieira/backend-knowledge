# JSONL

## What is JSONL (JSON Lines)?

**JSONL**—also called **NDJSON**—is a text format where **each line is a complete, independent JSON object**.

Example:

```text
{"id": 1, "event": "login", "user": "alice"}
{"id": 2, "event": "logout", "user": "bob"}
{"id": 3, "event": "purchase", "amount": 19.99}
```

Key characteristics:

- One JSON object per line
- Lines are separated by `\n`
- No enclosing array (`[]`)
- Easy to append, stream, and process line-by-line

## JSONL vs Regular JSON

| Aspect         | JSON                               | JSONL                             |
| -------------- | ---------------------------------- | --------------------------------- |
| Structure      | Single JSON value (often an array) | Multiple independent JSON objects |
| Streaming      | Awkward                            | Natural                           |
| Appending data | Hard (must rewrite file)           | Easy (append a line)              |
| Partial reads  | Difficult                          | Simple                            |
| Typical size   | Small–medium                       | Large / unbounded                 |

## How JSONL Relates to HTTP APIs

### 1. Streaming Responses

HTTP APIs often stream data when:

- Results are large
- Data is generated incrementally
- Clients want early results

JSONL fits perfectly because each line can be sent as soon as it’s ready.

Example HTTP response:

```http
Content-Type: application/x-ndjson
Transfer-Encoding: chunked
```

Response body:

```json
{"status": "started"}
{"progress": 10}
{"progress": 50}
{"progress": 100}
{"status": "done"}
```

Clients can process each line immediately without waiting for the full response.

### 2. Bulk Data Uploads

APIs that accept **large datasets** often prefer JSONL over a giant JSON array.

Example request body:

```http
POST /events
Content-Type: application/x-ndjson
{"event": "click", "ts": 1700000001}
{"event": "scroll", "ts": 1700000002}
{"event": "purchase", "ts": 1700000003}
```

Benefits:

- Server can process records incrementally
- Failures can be reported per line
- Lower memory pressure on both sides

### 3. Log and Event Ingestion APIs

Many ingestion APIs expect JSONL because:

- Logs and events are naturally record-based
- Data arrives continuously
- Ordering matters, but global structure doesn’t

Common pattern:

- One HTTP request = many events
- Each line = one event

### 4. Long-Running Jobs & Async APIs

APIs that perform long tasks (ML jobs, exports, crawls) often return **progress updates** as JSONL:

```json
{"type": "info", "message": "Job queued"}
{"type": "info", "message": "Job running"}
{"type": "result", "items_processed": 12000}
```

This avoids:

- WebSockets
- Custom framing protocols

## Content Types You’ll See

- `application/x-ndjson` (most common)
- `application/jsonl`
- `application/json` (sometimes used, but ambiguous)

Clients should not assume a JSON array when using these.

## Client-Side Handling

Key rule: **read line-by-line, not all-at-once**.

Typical flow:

1. Open HTTP connection
2. Read stream
3. Split on `\n`
4. Parse each line as JSON
5. Handle errors per record

This works well with:

- Fetch streams
- cURL pipelines
- Server-sent responses

## When NOT to Use JSONL in APIs

Avoid JSONL when:

- Response is small and finite
- Clients require strict JSON schema validation
- You need nested relationships across records
- You rely heavily on OpenAPI tooling that assumes JSON arrays