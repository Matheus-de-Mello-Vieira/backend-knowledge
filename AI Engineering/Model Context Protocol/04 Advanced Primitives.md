# MCP Advanced Primitives

As MCP evolved, newer primitives were added to move beyond simple request-response loops and support more agentic behavior.

## Sampling

Sampling allows the server to ask the client's LLM to think.

- **Scenario:** A server is processing a messy CSV and is not sure how to categorize a row.
- **Behavior:** It sends a sampling request back to the user's model asking for a classification.
- **Impact:** The server gains intelligence without needing to manage its own model credentials.

## Elicitation

Elicitation allows a server to ask the user for missing information in the middle of a process.

- **Scenario:** A tool is told to book a flight to NYC, but the departure time is missing.
- **Behavior:** The server triggers an elicitation request, and the UI asks a focused question.
- **Validation:** Responses are validated against a schema before being returned to the server.

## Roots

Roots are filesystem boundaries. They tell a server which directories it is allowed to inspect.

- **Purpose:** They scope the agent's attention and reduce irrelevant or unsafe file access.
- **Example:** If the active project root is `Project A`, the server does not need to wander through unrelated folders.
