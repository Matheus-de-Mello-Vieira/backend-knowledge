# Integrating Claude Tool Use: The Agentic Loop

Think of tool use (also known as function calling) as giving the model a set of API keys and hands. Instead of just answering questions with static training data, the model can look up a customer's billing history in Stripe, trigger a deployment pipeline, or query a live database. The model itself does not execute your internal code; it simply acts as the orchestration engine, reading your function signatures and telling you exactly which function to call and what arguments to pass.

## Architecture: Client vs. Server Tools

Understand where the execution happens before building the pipeline:

- **Client-side tools:** You define a custom JSON schema (like `lookup_user_record`), pass it to the API, and handle the actual execution within your application infrastructure.
- **Server-side tools:** Anthropic provides and executes these directly on their backend (e.g., the built-in Web Search tool). You pass the configuration, and Anthropic's servers fetch the data before returning the result to the model.

## Implementing the Agentic Loop

Build the interaction cycle by treating the LLM as a state machine that pauses execution until an external condition is met. Follow these steps:

1. **Provide tool definitions:** Pass a list of tools in your API request using the `tools` parameter. Define each tool with a clear name, a highly detailed `description` (which the model relies on heavily to evaluate if the tool solves the user's intent), and a JSON Schema detailing the `input_schema`.
2. **Process the stop reason:** When the model decides a tool is necessary, it pauses text generation and returns a response with a `stop_reason` of `tool_use`. It also returns a `tool_use` content block containing the generated arguments.
3. **Execute the function locally:** Parse the `tool_use` block, extract the arguments, and run the corresponding function in your backend environment.
4. **Return the result:** Send a new message back to the model. Append a `tool_result` content block containing the function's output (raw text, JSON, or an error message). The model reads this result and either generates a final human-readable response or triggers another tool.

## Steering and Enforcing Schema Compliance

Control how aggressively the model reaches for tools and enforce rigid payload structures:

- **Enforce strict schemas:** Set `strict: true` in the tool definition. This guarantees the model's output will exactly match your JSON schema, preventing downstream validation errors and type panics in your backend.
- **Control the trigger conditions:** By default, `tool_choice` is set to `{"type": "auto"}`, letting the model organically decide when a tool is appropriate. To force the model to use a specific tool, set `tool_choice` to `{"type": "tool", "name": "my_function"}`. To force it to use _any_ tool before answering, use `{"type": "any"}`.
- **Tweak the system prompt:** If the model hesitates to use a tool, add an explicit directive like "Always investigate the database using tools before responding."
## Threat Modeling and System Security

When giving an LLM the ability to trigger backend functions, strictly isolate its execution environment and treat its output as untrusted input.

**Is this vulnerable to indirect prompt injection?**

Yes. If the model uses a tool to fetch a webpage or an external database record, a malicious payload inside that external data can hijack the model's instructions. Never grant a tool destructive capabilities (like `DROP TABLE` or `refund_customer`) without a human-in-the-loop review step or strict, hardcoded parameter boundary checks.

**Does the model validate the tool's execution authority?**

No. The model does not understand your IAM roles or RBAC policies. If you expose an `admin_delete_user` tool to the model in a customer-facing chatbot, the model will attempt to use it if requested. Always enforce authorization at the application layer, validating that the user interacting with the model actually has permission to execute the triggered tool.

**Are tool schemas retained in the context window?**

Yes. Every tool definition you pass consumes input tokens and occupies the context window. Passing hundreds of unused tools degrades reasoning performance and inflates costs. Use dynamic tool fetching or semantic tool search with vector embeddings to inject only the necessary tool schemas into the prompt based on the user's initial query.

## The Task Tool: Orchestrating Subagents

Think of the Task tool as a dispatch system for multi-agent architectures. Instead of a primary coordinator model attempting to execute a sprawling, multi-domain workflow synchronously, it uses the Task tool to spawn specialized child processes. It is the backend equivalent of a lead software architect handing off a highly specific database migration ticket to a dedicated DBA rather than writing the SQL themselves.

### Configuration and Agent Definitions

To build a functional hierarchy, explicitly define the orchestration boundaries and permissions within your application code:

- **Enable the dispatcher:** You must explicitly inject `"Task"` into the `allowedTools` array of the coordinator model. If this is omitted, the primary agent cannot invoke child processes and will fail when attempting to delegate work.
- **Define the specialists:** Create an `AgentDefinition` for every subagent type in your system infrastructure. This configuration acts as the subagent's operating manual. It requires a clear `description` (which the coordinator relies on to know _when_ to invoke it), a customized `system prompt` to govern its behavior, and strict tool restrictions to prevent scope creep.

### State Management and Context Boundaries

When a coordinator spawns a subagent via the Task tool, understand how state flows through the system to prevent execution failures.

**Do subagents inherit the parent's memory?**

No. Subagents launch in an entirely stateless void. They do not automatically inherit the parent coordinator's context window, nor do they share memory states between concurrent subagent invocations. You must explicitly pack all necessary context, constraints, and historical data into the prompt payload when invoking the Task tool. If the subagent needs a user's API key or a database schema to complete its objective, the coordinator must pass that exact data in the initial task assignment.

**Is this capable of divergent exploration?**

Yes. Utilize fork-based session management to tackle ambiguous problem-solving. Once the coordinator establishes a shared analysis baseline, use the Task tool to fork the session state. This allows you to spawn multiple subagents to explore divergent architectural approaches simultaneously—such as having one subagent draft a REST API implementation while another drafts a GraphQL approach—without polluting the parent model's primary context window until the tasks resolve and return their findings.

## Tool Distribution and Choice Configuration

Think of tool distribution like granting Identity and Access Management (IAM) permissions in a microservices architecture. If you give a specialized microservice access to every database in the VPC, you increase the attack surface and the likelihood of an expensive, runaway query. Similarly, dumping 18 tools into a single agent's context window cripples its reasoning. The increased decision complexity sharply degrades tool selection reliability. If you give a dedicated synthesis agent access to web search tools, it will inevitably attempt to misuse them to fill knowledge gaps rather than focusing on synthesizing the provided text.

### Scoping and Restricting Access

Treat agent capabilities with the principle of least privilege. Structure tool access to prevent cross-specialization misuse:

- **Restrict by role:** Give subagents only the 4 to 5 tools strictly necessary to complete their specific domain task.
- **Constrain generic inputs:** Replace overly broad, generic tools with heavily constrained alternatives. Instead of giving an agent a raw `fetch_url` tool, provide a `load_document` tool that strictly validates target URLs and restricts execution to known document formats.
- **Provide high-frequency bridges:** If an agent occasionally needs external context to finish its job, provide a highly scoped cross-role tool. For example, give a synthesis agent a `verify_fact` tool for quick, localized checks, but force it to route complex, multi-step research tasks back up to the primary coordinator.

### Steering Execution Sequences

Control exactly how and when the model interacts with its environment using the `tool_choice` configuration parameter:

- **Guarantee execution:** Set `tool_choice` to `{"type": "any"}` to strictly forbid the model from returning conversational text. This forces the model to emit a tool call, ensuring the backend pipeline does not stall waiting for a structured payload that never arrives.
- **Force sequential pipelines:** When building deterministic pipelines, force the model to execute a specific tool first. Set `tool_choice` to `{"type": "tool", "name": "extract_metadata"}`. Once the backend processes this forced extraction, pass the results back to the model in the next turn with `tool_choice` set to `auto`, allowing it to dynamically choose its subsequent enrichment tools.


## Built-in Tools: Navigating and Modifying the Codebase

Think of built-in file system tools as a surgeon's instrument tray. You would not use a bone saw (a full-file `Write`) to make a precision incision (an `Edit`), nor would you blindly open the patient (reading every file upfront) when an ultrasound (`Grep` and `Glob`) can pinpoint the exact issue. Applying the right tool prevents context window bloat and eliminates destructive file overwrites.

### Tool Selection and Purpose

Categorize the tools by their operational intent to ensure you trigger the most efficient system call:

* **Glob:** Use this for file path pattern matching. Execute `Glob` to quickly map out directory structures or isolate specific file types (e.g., finding all test files via `/*.test.tsx`).
* **Grep:** Use this for deep content searches. Execute `Grep` to search raw file contents for specific patterns, such as locating all callers of a deprecated function, finding hardcoded error messages, or hunting down orphaned import statements.
* **Edit:** Use this for targeted, surgical modifications. `Edit` relies on exact, unique text matching to replace a specific block of code without touching the rest of the file.
* **Read / Write:** Use these for full file operations. `Read` dumps the entire file into the context window, while `Write` overwrites the file entirely from top to bottom.

### Operational Workflows

Mastering these tools requires stringing them together into incremental, non-destructive workflows.

**Build understanding incrementally:**
Never read the entire codebase upfront. Start by using `Grep` to find the execution entry points or specific function definitions. Once located, use `Read` on those specific files to follow the import tree and trace the data flow.

**Trace wrapper modules:**
When dealing with complex architectures that wrap underlying libraries, trace usage by first reading the wrapper file to identify all exported names. Then, iterate with `Grep` to search for each of those exported names across the rest of the codebase.

**Implement reliable fallbacks:**
`Edit` frequently fails if the text you are trying to replace is too generic (like `return true;` or `</div>`), because the tool cannot determine the unique anchor point. When `Edit` fails due to non-unique text matches, immediately fall back to using `Read` to load the full file contents, apply the logical changes internally, and use `Write` to safely overwrite the file.
