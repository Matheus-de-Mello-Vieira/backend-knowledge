# Others

## Message Batches API: Asynchronous Processing at Scale

Processing large volumes of LLM requests synchronously can bottleneck system performance and inflate costs. The Message Batches API shifts this paradigm to asynchronous execution. Think of it like a bulk mailing service: instead of waiting at the post office counter to send one letter at a time, you drop off a massive mailbag, let the backend sort and deliver everything over the next few hours, and return later to check the delivery receipts.

Match your API approach strictly to your workflow latency requirements. The Batch API drops token costs by 50% and dramatically increases overall throughput, making it ideal for non-blocking, latency-tolerant workloads like overnight reports, weekly audits, and nightly test generation. Conversely, it is completely inappropriate for blocking workflows where immediate execution is required, such as synchronous pre-merge CI checks.

### Core Constraints and Mechanics

Understand the boundaries of the batch service before integrating it into a backend pipeline:

- **Size limits:** Submit up to 100,000 requests or 256 MB per batch, whichever is reached first.
- **Turnaround time:** Expect completion usually within 1 hour, with a strict 24-hour expiration limit for unprocessed queries. There is no guaranteed latency SLA.
- **Cost reduction:** All supported models run at exactly half their standard token cost.
- **No multi-turn tool calling:** The batch API does not support multi-turn tool calling within a single request. You cannot instruct the model to execute a tool, wait for your backend to return the result, and finish its generation within the same batch payload.
- **Incompatibilities:** Features requiring synchronous state, immediate low latency, or direct connection are rejected. Set `stream: false`. Do not use Threads (`store`/`previous_thread_event_id`), Fast mode, or cache-warming dummy queries (`max_tokens: 0`).

### Strategic Execution and SLA Management

Because the Batch API offers a generous 24-hour processing window without a guaranteed latency SLA, you must actively manage how and when you deploy payloads to meet internal deadlines.

- **Perform pre-flight prompt refinement:** Always execute prompt refinement on a small, synchronous sample set before batch-processing massive volumes. Validating the output structure and logic on a sample maximizes first-pass success rates and prevents paying for thousands of iteratively failed outputs.
- **Calculate batch submission frequency:** Work backward from your operational SLA constraints to determine your aggregation windows. For example, to guarantee a 30-hour delivery SLA for a weekly audit, aggregate and submit batches every 4 hours. This ensures that even if the backend requires the maximum 24 hours to process the batch, you still have a 2-hour buffer to parse and route the results before the 30-hour deadline expires (4-hour window + 24-hour processing + 2-hour buffer = 30 hours).

### Implementation Steps

Follow these steps to integrate batch processing into the application flow:

1. **Construct the payload:** Build a list of individual `Request` objects. Assign a strictly unique `custom_id` (using only alphanumeric characters, hyphens, and underscores) to every request. Pass the standard parameters required for a message creation inside the `params` object of each request.
2. **Submit the batch:** Send the list to the `POST /v1/messages/batches` endpoint. Store the returned `id` to track the job.
3. **Poll for completion:** Periodically query the retrieval endpoint (`GET /v1/messages/batches/{id}`) using an exponential backoff or scheduled worker. Wait until `processing_status` transitions from `in_progress` to `ended`.
4. **Download and parse results:** Retrieve the `.jsonl` file via the `results_url`. Iterate over each line, using the `custom_id` to map the asynchronously processed result back to the original request, as results are not guaranteed to return in the submitted order.
5. **Handle failures and state outcomes:** Switch on the result `type`. Process `succeeded` payloads and discard or log `canceled` ones. Crucially, if you encounter `errored` or `expired` requests, do not blindly resubmit the entire batch. Isolate the failed documents using their mapped `custom_id`. Apply targeted modifications to the payload—such as chunking documents that unexpectedly exceeded context limits—and resubmit only those isolated queries.

For handling tokenization mechanics and standard message object parameters, see the Messages API reference.

### Optimizing with Prompt Caching

Combine batch processing with prompt caching for compounded cost reductions. Because batch tasks are processed concurrently across many backend workers, cache hits operate on a best-effort basis rather than a guaranteed hit.

To maximize cache hit rates in asynchronous workloads:

- Inject identical `cache_control` blocks into every single message request in the batch. 
- Group similar contexts together and deploy them in steady streams to prevent the 5-minute cache lifespan from expiring.

For caching mechanisms and cache-control block syntax, see the Prompt Caching guide.

## Claude Thinking: Extended and Adaptive Reasoning

Think of standard API inference like speaking off the cuff—it is fast, but prone to errors on complex logic. Extended thinking gives the model a hidden whiteboard to reason through edge cases, draft pseudocode, or map out tool sequences before returning the final response. It fundamentally shifts the model from a simple next-token predictor to a test-time compute engine, significantly boosting accuracy for agentic coding and multidisciplinary tasks.

Historically, enabling this required hardcoding a fixed token budget. Modern architectures use **Adaptive Thinking**, allowing the model to dynamically scale its reasoning based on the query's complexity. For a simple greeting, it skips the whiteboard; for a massive repository refactor, it allocates deep, multi-step thought.

### Implementation Steps

Integrate dynamic reasoning into the application flow by adjusting the request payload:

1. **Configure the thinking object:** In the API request, pass `thinking: {"type": "adaptive"}`. Avoid the legacy `"enabled"` type with a fixed budget, as it is deprecated on newer models and outright rejected on models like Opus 4.8.
2. **Dial in the effort:** Control the reasoning depth using the `effort` parameter (`low`, `medium`, `high`, `max`). Use `high` (the default) for standard workflows, but push to `max` for complex agentic loops where precision outweighs speed.
3. **Handle tool constraints:** When using thinking with tools, you must set `tool_choice` to `{"type": "auto"}` (the default) or `{"type": "none"}`. Forcing a specific tool (`{"type": "any"}` or `"tool"`) disrupts the internal reasoning loop and will throw a 400 error.
4. **Parse the response:** The API returns a `thinking` content block followed by standard `text` blocks. Adaptive mode also supports **interleaved thinking**, meaning you may receive multiple thinking blocks placed between tool calls as the model evaluates intermediate results.
5. **Round-trip the context:** In multi-turn conversations, pass the `thinking` blocks back to the API exactly as received. Do not strip them out, as the model relies on its previous thoughts to maintain reasoning continuity.

### Payload Optimization and Display Settings

Returning massive reasoning blocks bloats the response payload and increases network latency. Control the verbosity of the output via the `display` parameter:

- **`summarized`:** Returns a brief, human-readable summary of the reasoning process.
- **`omitted`:** Strips the text entirely, leaving an empty thinking field and a cryptographic signature. Use this in production to minimize latency.

> [!note]
> Omitting thinking text reduces network latency, but it does not reduce cost. You are still billed for the underlying compute tokens used during the unseen reasoning phase.

### Native Thinking vs. Explicit Prompt Planning

Think of native extended thinking as a senior engineer silently working through a complex algorithm in their head before writing the code. In contrast, explicit planning—instructing the model via the system prompt to "write a step-by-step plan before answering"—is like forcing that engineer to write a formal technical spec for stakeholder approval. Both methods allocate extra tokens for test-time reasoning, but they serve entirely different architectural needs.

Rely on native extended thinking for complex, self-contained problem solving. Use it when the application requires deep logic, advanced mathematics, or autonomous multi-step tool use. Because the model trains specifically on these internal thought structures, native thinking yields higher accuracy on complex tasks without requiring manual prompt engineering to enforce the reasoning steps.

Use explicit prompt planning when the system architecture requires transparency, strict structural adherence, or human-in-the-loop intervention. Implement explicit planning pipelines when:

- **State requires parsing:** You need to programmatically extract the intermediate steps—for example, parsing a generated JSON plan to update a user-facing progress bar in the UI.
- **Enforcing rigid frameworks:** The model must strictly follow a custom corporate compliance checklist or a highly specific operational framework rather than its own organic reasoning path.
- **Human-in-the-loop validation:** An operator must review, modify, or approve the sequence of actions before the system executes the final generation or tool calls.

If the goal is simply to get the most accurate final output with minimal prompt overhead, lean entirely on native adaptive thinking. If the system design treats the intermediate _process_ itself as a deliverable, parsed artifact, utilize explicit prompt planning.

### Advanced Orchestration Patterns

Optimize the execution speed and accuracy of multi-agent architectures by treating the coordinator as an executive director rather than a micromanager. Use the following patterns to structure agent handoffs:

- **Define goals over procedures:** Design coordinator prompts that specify end-state research objectives and strict quality criteria rather than rigid, step-by-step instructions. This provides subagents the autonomy to adapt their internal reasoning paths when encountering unexpected errors or edge cases.
- **Pack the prompt with prior findings:** Because subagents operate in a stateless vacuum, you must inject the complete, explicit findings from previous tasks directly into the next subagent's prompt. If an analysis agent finishes reading a repository, pass its exact output into the prompt of the subsequent synthesis agent.
- **Structure the context payloads:** When transferring context between agents, use structured data formats (like JSON) to strictly separate raw content from its metadata (such as source URLs, document names, and page numbers).
- **Execute in parallel:** Maximize system throughput by emitting multiple Task tool calls simultaneously within a single coordinator response. Spawn parallel subagents concurrently instead of forcing the coordinator to wait for sequential, round-trip turns.

## Session State: Resumption and Forking

Think of session state management like a Git branching model for the agent's context window. You do not need to rebuild the entire repository context from scratch every time you sit down to code. By managing state intelligently, you can pause long-running investigations, branch off stable analysis baselines, and prevent the model from hallucinating over outdated file reads.

### Resuming and Forking Workflows

Implement these mechanisms to manage the agent's operational lifecycle:

- **Continue named investigations:** Execute the CLI with the `--resume <session-name>` flag to reattach to a specific prior conversation across work sessions. Use this when returning to an ongoing task where the underlying codebase has remained mostly static since you last paused.
- **Branch shared analysis:** Use `fork_session` to create independent, parallel branches from a shared baseline. Rely on this to explore divergent approaches—such as comparing two entirely different testing strategies or drafting multiple refactoring architectures—without polluting the parent session's active memory.

### Managing Stale Context and State Drift

When pausing and resuming work, evaluate how out-of-band code modifications impact the agent's internal memory.

**Is it better to resume or start fresh?**

If the codebase has undergone significant structural changes or refactors while the agent was offline, do not resume the session. Resuming forces the model to rely on stale tool results and outdated file structures currently locked in its context window. Instead, start a fresh session and inject a structured summary of the prior architecture decisions. Starting fresh with a cleanly injected summary is always more reliable than forcing the model to unlearn obsolete tool outputs.

**How do I handle minor file modifications upon resumption?**

If you only made small code tweaks during the downtime, you can safely use `--resume`. However, you must explicitly inform the agent about the exact files that changed immediately upon reconnecting. Direct the agent to perform a targeted re-analysis of those specific files. This updates the agent's internal map of the codebase without requiring a costly, full-scale re-exploration of the repository.

## CI/CD Pipeline Integration: Automated Code Review and Testing

Integrating an agent into a Continuous Integration (CI) pipeline is like assigning a tireless junior developer to review every pull request and scaffold test coverage. To succeed, the agent must execute headlessly, output machine-readable payloads, and rely strictly on localized project context.

### Non-Interactive Execution and Structured Output

Running interactive tools in a CI environment (like GitHub Actions or GitLab CI) will hang the pipeline indefinitely as the system waits for a human to approve an operation.

- **Prevent input hangs:** Always invoke the CLI using the `-p` (or `--print`) flag. This forces the agent to run in a strictly non-interactive mode, returning its output and immediately exiting the process.
- **Enforce machine-parseable results:** A block of markdown text is useless to a script trying to annotate a pull request. Use the `--output-format json` alongside the `--json-schema` flag to enforce a rigid payload structure. This allows your CI runner to parse the JSON findings and automatically post them as inline PR comments.

### State Management for Code Reviews

When building an automated code review pipeline, state management determines the quality and noise level of the agent's feedback.

**Is it effective to review code using the same session that wrote it?**

No. A session that generated the code suffers from context bias; it is likely to overlook its own logical flaws because it is anchored to its original reasoning trajectory. Always spin up an independent, isolated review instance to evaluate code changes. A fresh session provides an objective analysis baseline.

**How do you prevent duplicate PR comments on subsequent commits?**

When an engineer pushes a new commit to an open PR, the CI pipeline triggers another review. If you pass only the current diff, the agent will flag issues it already reported. To prevent comment spam, inject the prior review findings directly into the prompt payload. Explicitly instruct the agent to evaluate the new diff against the old findings, reporting only _new_ regressions or _still-unaddressed_ issues.

### Test Generation and `CLAUDE.md` Integration

Automated test scaffolding frequently produces redundant or low-value tests if the agent lacks visibility into the existing test suite and architectural constraints.

- **Prevent duplicate scenarios:** Always pack the existing test files into the agent's context payload alongside the target code. This forces the agent to read the current coverage map and prevents it from suggesting edge cases that the test suite already handles.
- **Document testing constraints:** Rely on the `CLAUDE.md` file as the primary mechanism for providing project context to the CI-invoked agent. Because `CLAUDE.md` acts as the project constitution containing test suites and core tech-stack choices, it is the ideal location to document testing standards, valuable test criteria, and available fixture conventions. This localized memory scope ensures the agent generates high-value tests that adhere strictly to your repository's conventions rather than generic boilerplate.