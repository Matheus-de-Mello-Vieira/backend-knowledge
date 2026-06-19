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

### Handling Interruption and Behavioral Pivots

During complex agentic loops, you may need to interrupt the model's current trajectory. For example, if a model triggers a database query that returns an overwhelmingly large dataset, you might want to pivot its original plan and instruct it to merely summarize the findings instead of performing a deep analysis.

**Can you ignore a pending tool call to pivot the conversation?**

No. The API operates as a strict state machine. If the model emits a `stop_reason` of `tool_use`, your next request must contain a `tool_result` block resolving that specific execution. Sending a standard text prompt without resolving the pending tool call breaks the sequence and will throw a 400 API error.

**Implementing the Pivot**

To successfully interrupt the model, you must fulfill the API contract while simultaneously injecting the new directive. Do this by combining multiple content blocks within the same user turn:

1. **Resolve the state:** Append the required `tool_result` block containing the function's output to satisfy the API's sequence requirements and provide the requested data.
2. **Inject the pivot:** In the exact same `content` array, append a `text` block containing the new instruction (e.g., "Summarize this data and halt further tool use").

By providing both blocks in a single request, you successfully steer the model's next generation—pivoting its behavior—while maintaining the full context of the session and satisfying the rigid tool execution loop.
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

### Code Execution (Programmatic Tool Calling)

The Claude API includes built-in Code Execution, an Anthropic-provided server-side tool that allows the model to write, execute, and analyze Python code directly within its reasoning loop. Instead of relying on your backend to run custom logic, the model runs short scripts in a secure, ephemeral container hosted by Anthropic.

> [!example] Orchestrating Heterogeneous Pagination
> 
> Imagine building a legal e-discovery agent with Claude that needs to search through multiple document databases. These databases rely on heterogeneous pagination schemas: Database A uses a `next_page_token`, Database B uses `offset` and `limit`, and Database C uses a `page_number`. When trying to manage these varying schemas manually within its standard context window, the model frequently struggles, resulting in infinite loops or skipped pages.
> 
> **The Solution: Programmatic Tool Calling (PTC)**
> 
> The officially recommended approach to handle this complexity is Programmatic Tool Calling. You allow the model to write and execute Python orchestration code inside a sandbox. This code implements the exact loops and conditional logic needed to manage the different pagination states and aggregate the results. By processing intermediate results directly within the sandbox, the model only returns the final aggregated output, which drastically reduces token consumption and latency.
> 
> **Why not use a `PostToolUse` hook?**
> 
> You might consider implementing a `PostToolUse` hook to intercept every tool response, abstract the pagination metadata, and automatically issue follow-up requests. While this could theoretically manage pagination, it is not the recommended approach. A hook requires custom implementation entirely outside of the model's internal orchestration. Anthropic emphasizes PTC for these scenarios because external hooks may not be as efficient or flexible when dealing with complex, multi-step workflows that heavily rely on conditional logic.
#### Why Use Code Execution?

Code Execution bridges the gap between text generation and precise computation. It is crucial for tasks where LLMs traditionally hallucinate or fail.

- **Complex Math:** LLMs struggle with large-number arithmetic or calculus. By writing a Python script to calculate the result, the model guarantees mathematical accuracy.
- **Data Analysis:** If you pass a large CSV file in the context window, the model can use Pandas or NumPy to filter, aggregate, and visualize the data rather than attempting to parse the string text directly.
- **Algorithmic Reasoning:** For complex logic puzzles or sorting tasks, the model can draft an algorithm, test it, read the error output, and refine its logic before delivering the final answer.
#### Enabling the Tool

To grant the model access to this capability, you must explicitly pass the built-in tool configuration in your API request.

**Inject the definition:** In your `tools` array, include the Anthropic-defined Code Execution tool block:
```json
{
	"name": "computer_use", 
	"type": "computer_20241022" 
}
```

#### Execution Loop and Limitations

When the model decides to use the tool, it generates the Python code and pauses.

**How does the code actually run?**

Anthropic's servers intercept the request, spin up an isolated, sandboxed Python environment, execute the code, and automatically inject the stdout (or stderr) back into the prompt as a `tool_result` block. The model reads the output and continues its reasoning.

**Are there limitations to the sandbox?**

Yes. The environment is strictly sandboxed.

- **No internet access:** The code cannot make external HTTP requests or download new packages.
- **Pre-installed libraries:** The environment only contains a specific list of pre-installed data science libraries (like `pandas`, `numpy`, and `matplotlib`).
- **Timeout constraints:** Scripts that run too long or consume too much memory are killed automatically, returning a timeout error to the model.

If you require external network access, custom dependencies, or heavy computation, you must build Client-side tools and execute the Python code on your own backend infrastructure.

### Implementing Reliable Fallbacks and Structurally-Aware Edits

The built-in file system tools are powerful, but they operate primarily on raw text. When dealing with complex structures or non-unique strings, you must implement reliable fallback strategies to prevent corruption.

**When to fall back to Read + Write:** The `Edit` tool frequently fails if the text you are trying to replace is too generic (like `return true;` or `</div>`), because the tool cannot determine a unique anchor point within the file. When `Edit` fails due to non-unique text matches, immediately fall back to using `Read` to load the full file contents into the context window, apply the logical changes internally, and use `Write` to safely overwrite the file entirely.

**When to fall back to Programmatic Tool Calling (PTC):** While `Read` and `Write` are great for plain text, they become risky when editing highly structured data files (like large JSON arrays or complex YAML configurations) where a simple text-based search-and-replace could modify incorrect entries or fail due to formatting inconsistencies.

For example, if you need to update a specific `tax_rate` for the state of "NY" inside a massive `state_taxes.json` file. Instead of using `Grep` to find the line and `Edit` to change the text, the most robust and structurally-aware approach is to use Programmatic Tool Calling. Instruct the agent to generate and execute a Python script that reads the JSON file, parses it into an actual object, updates the specific key programmatically, and writes the modified, properly formatted data back to the file.