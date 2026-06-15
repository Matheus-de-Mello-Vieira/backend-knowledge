# MCP Advanced Primitives and Boundaries

For the basic server building blocks, see [03 Core Primitives](./03%20Core%20Primitives.md). For implementation guidance and common failure modes, see [05 Tool Design and Operational Risks](./05%20Tool%20Design%20and%20Operational%20Risks.md).

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

## Permissions Boundaries: The Gatekeeper Layer

Permissions boundaries are the security layers that prevent an LLM from acting as a rogue agent. Since LLMs can be manipulated or can misfire, they cannot be trusted to police themselves.

The host application acts as the enforcer. The server offers capabilities, but the host decides whether they are allowed.

### The Three Layers of Defense

#### Level 1: The Human (Consent and Confirmation)

When the LLM tries to execute a sensitive tool, the host asks the user for permission.

- **Scenario:** The LLM calls `delete_file(path="/docs/report.pdf")`.
- **Boundary:** The host asks whether the operation should be allowed.
- **Policy:** Write operations usually require stricter approval than read operations.

#### Level 2: The Host (Capability Negotiation)

Before any conversation starts, the client and server perform a handshake. The host can reject sensitive tools entirely.

- **Scenario:** A server offers `execute_shell_command`.
- **Boundary:** The host can hide that capability so the model never sees it.

#### Level 3: The Infrastructure (Sandboxing)

Even if the human and host approve, the operating system or container runtime can still deny the action.

- **Scenario:** The model tries to read `file:///etc/shadow`.
- **Boundary:** A sandboxed or restricted runtime denies the read request.

### The Confused Deputy Problem

Permissions boundaries primarily exist to mitigate the **Confused Deputy** problem.

1. A malicious document tells the model to exfiltrate data or trigger a tool.
2. The LLM tries to comply.
3. The permissions boundary intercepts the action and gives the user a chance to deny it.

### Best Practices for Developers

- **Atomic Tools:** Prefer specific tools such as `restart_server` over generic tools such as `run_script`.
- **Read vs. Write Separation:** Separate read-only tools from state-changing tools.
- **Statelessness:** Do not assume prior permissions remain valid later.

### Implementation Example: Sampling Permission

Sampling is high risk because it allows the server to speak through the client's model. The client must explicitly opt in.

```json
{
  "capabilities": {
    "sampling": {}
  }
}
```

If `sampling` is absent, the server cannot ask the client's model to generate text on its behalf.
