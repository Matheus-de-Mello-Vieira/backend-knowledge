## MCP Tool Design and Operational Risks

Building tools for an AI agent requires a fundamental shift in API design philosophy. When humans read API documentation, they can infer missing context and deduce ambiguous variable names. An LLM cannot. If an MCP server is poorly designed, it will silently degrade the model's performance, leading to constant hallucinations and infinite tool-calling loops.

### Principles of Model-Native Tool Design

To guarantee deterministic and reliable LLM routing, your tool schemas must adhere to four core engineering principles:

#### Atomic

An atomic tool has a single, strictly defined responsibility. You must avoid the "Swiss Army Knife" anti-pattern where a tool takes an `action` parameter to decide what internal logic to run.

- **Bad:** `manage_user(action="delete", id="123")`
- **Good:** `delete_user(id="123")`
- **Why:** The tool's name itself acts as a high-signal semantic cue for the model's reasoning engine.

#### Composable

Tools should be designed to pass data seamlessly to one another. In an MCP architecture, this means the output of one tool should exactly match the expected input schema of the next.

- **Pattern:** `search_files` returns an array of absolute paths, and `read_file` strictly accepts an absolute path.
- **Result:** The model can autonomously chain these tools together in predictable execution pipelines.

#### 3. Unambiguous

If two parameters sound similar, or if a description is vague, the model will hesitate or hallucinate arguments.

- **Vague Description:** _"Update data."_
- **Constrained Description:** _"Updates the status column of a ticket. Use ONLY for transitioning tickets between Open, In Progress, and Closed."_
- **Enums Over Strings:** If a database field only accepts `high`, `medium`, or `low`, explicitly define it as an `enum` in the JSON schema. Never expose it as a free-text string.

#### 4. Minimal Surface Area

Every parameter you expose increases the cognitive load on the LLM and multiplies the chance of a hallucinated argument.

- **Bad:** Exposing underlying HTTP implementation details like `user_agent`, `request_id`, or `timestamp`.
- **Good:** Hardcode infrastructural details on the server-side. Expose only the intent-relevant arguments to the model (e.g., `recipient`, `subject`, `body`).

###  The Tool's Reply

Once the model calls a tool successfully, the MCP server must send back a structured response. In the MCP protocol, this is formatted as a `CallToolResult`.

#### The Anatomy of a Result

An MCP tool result returns an array of `content` blocks. This modular design allows for rich, multi-modal feedback within a single response.

- **Text:** Standard string output, raw data, or JSON strings.
- **Images:** Base64-encoded visual feedback (like plots or diagrams).
- **Resources:** Embedded files or data blobs.

```json
{
  "content": [
    {
      "type": "text",
      "text": "Successfully queried the database. Found 1 user."
    },
    {
      "type": "text",
      "text": "{\"id\": 123, \"name\": \"Alice\", \"role\": \"admin\"}"
    }
  ],
  "isError": false
}
```

#### Engineering Best Practices for Responses

- **Return JSON-in-Text:** It is notoriously difficult for an LLM to reliably extract exact values from conversational prose. Returning structured JSON strings inside the text block makes it vastly easier for the model to parse the data and reuse it as an argument in a subsequent tool call.
- **Visual Feedback:** If you build a Python tool that generates a matplotlib graph, return it as an image content block. The LLM can then visually inspect the plot or directly present it to the user in the Host Application's UI.

#### Error Handling

When a tool fails (e.g., an API is down, or a SQL query has a syntax error), **do not crash the server.** Instead, return a structured error result using the `isError` flag.

```json
{
  "content": [
    {
      "type": "text",
      "text": "Error: Weather API is currently unreachable. Please try again later or check a different city."
    }
  ],
  "isError": true
}
```

- **Why:** This "soft fail" pattern feeds the error string directly back into the LLM's context window. It allows the model to autonomously read the error log, attempt to fix its parameters, or gracefully explain the backend outage to the user instead of hallucinating a successful response.

### The Bottlenecks of MCP Architectures

#### Tool Overload and Context Saturation

When an LLM receives too many tools in its system prompt, the architecture degrades in two ways:

- **Poor Decision-Making:** The semantic space becomes crowded, and the model struggles to pick the correct tool, often triggering the wrong function.
- **Context Consumption:** Tool schemas and descriptions eat up valuable token limits.
- **Mitigation:** Minimize unnecessary tool exposure through Capability Discovery, and design tools that batch operations to reduce redundant `tools/call` round-trips.

#### 2. The JSON Schema Bottleneck

LLMs are primarily trained on human knowledge, natural language, and raw code. MCP forces them to interface through strict JSON Schema specifications, which can easily become ambiguous if not rigorously defined.

**Common Ambiguity Traps:**

- **Ambiguous Formats:** `{ "date": "string" }`  
    The model does not know whether it should generate `2024-01-15`, `January 15`, or a Unix timestamp.
- **Optional Numeric Limits:** `{ "limit": "number" }`  
    The model does not know the maximum allowed limit or the default behavior when the field is omitted.
- **Complex Structures:** `{ "filter": {}, "sort": {} }`  
    The model does not know which database columns are valid for filtering or sorting.

**The Fix:** You must treat your JSON schemas as part of the prompt surface. Use the `description` fields inside your schemas to explicitly document formats, boundaries, and defaults (e.g., `"description": "The date formatted strictly as YYYY-MM-DD"`).

## Logging

While tools and resources return data directly to the LLM's context window, **Logging** is designed entirely for the Host Application and the developers. It provides a standardized, structured way for the MCP Server to stream background observability data (such as execution progress, debugging info, and system errors) without interrupting the active LLM conversation.

### The Execution Flow: Setting Levels and Streaming

Because logging can be incredibly noisy, the protocol places the Host Application in complete control of the verbosity.

#### 1. Capability Handshake

During the [initial connection](02%20Architecture.md#Capability%20Discovery), the server must explicitly declare that it supports structured logging: `{"capabilities": {"logging": {}}}`.

#### 2. The Client Configures Verbosity (`logging/setLevel`)

The Host Application evaluates its current environment (e.g., is it running in a developer's debug mode or production?) and sends a request to the server dictating the minimum severity level it wants to receive.

**The Client Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "logging/setLevel",
  "params": {
    "level": "info"
  }
}
```

#### 3. The Server Streams Data (`notifications/message`)

Once the level is set, the server pushes one-way JSON-RPC notifications down the transport stream (Stdio or SSE) whenever an event occurs. Because these are _notifications_, they do not require an `id` and do not expect a response from the client.

**The Server Notification:**

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/message",
  "params": {
    "level": "error",
    "logger": "database",
    "data": {
      "error": "Connection failed",
      "details": { "host": "localhost", "port": 5432 }
    }
  }
}
```

> [!note] Granular Request Scoping
> 
> In newer drafts of the MCP protocol, global log levels via `logging/setLevel` are being migrated toward per-request log levels. By passing an `io.modelcontextprotocol/logLevel` parameter inside a specific request's `_meta` object, the server scopes its `notifications/message` logs explicitly to that individual request's response stream. This allows massive, multi-client hosts to isolate debugging logs for a single tool call without cross-contaminating the entire session.

### Supported Severity Levels

MCP uses the [RFC 5424](../../Backend%20Engineering/05%20Observability.md#RFC%205424%20/%20Syslog%20Severity%20Levels) syslog severity model for `logging/setLevel`. 

At the protocol boundary, the operational rule is simple: when the client sets a minimum level such as `warning`, the server must emit `warning` and anything more severe, while dropping lower-severity events like `notice`, `info`, and `debug`.

### Engineering Best Practices: Structured vs. Unstructured Logging

- **Transport Nuances (Stdio):** In a local Stdio deployment, the Host Application will automatically capture anything the server prints to `stderr`. However, `stderr` is unstructured text. Utilizing the official `notifications/message` method allows you to send rich, parseable JSON objects (via the `data` property), making it far easier to integrate with modern observability dashboards or DevTools UIs.
- **Separation of Concerns (Logs vs. Tool Errors):** Do not confuse Logging with Tool Errors (the `isError: true` flag we discussed in the Tools section).
    - If a tool fails, you return the error text inside the `CallToolResult` so the **LLM** can read it, learn from the mistake, and try again.
    - You use the `notifications/message` logging endpoint to send the actual stack trace and internal DB query details to the **Host Application**, completely hiding it from the AI's context window.
- **Security & Sanitization:** Log payloads (`data`) must never contain raw user credentials, secret API keys, or personally identifiable information (PII). The MCP server must sanitize payloads before streaming them down the transport layer to prevent accidental leaks into the host's monitoring software.
