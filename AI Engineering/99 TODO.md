- https://modelcontextprotocol.io/specification/2025-11-25/server/utilities/completion
- https://modelcontextprotocol.io/specification/2025-11-25/server/utilities/pagination

<hr>

Task Statement 5.2: Design effective escalation and ambiguity resolution patterns
Knowledge of:
Appropriate escalation triggers: customer requests for a human, policy exceptions/gaps
(not just complex cases), and inability to make meaningful progress
The distinction between escalating immediately when a customer explicitly demands it
versus offering to resolve when the issue is straightforward
Why sentiment-based escalation and self-reported confidence scores are unreliable
proxies for actual case complexity
How multiple customer matches require clarification (requesting additional identifiers)
rather than heuristic selection

Skills in:
Adding explicit escalation criteria with few-shot examples to the system prompt
demonstrating when to escalate versus resolve autonomously
Honoring explicit customer requests for human agents immediately without first
attempting investigation
Acknowledging frustration while offering resolution when the issue is within the agent's
capability, escalating only if the customer reiterates their preference
Escalating when policy is ambiguous or silent on the customer's specific request (e.g.,
competitor price matching when policy only addresses own-site adjustments)
Instructing the agent to ask for additional identifiers when tool results return multiple
matches, rather than selecting based on heuristics

Task Statement 5.5: Design human review workflows and confidence calibration
Knowledge of:
The risk that aggregate accuracy metrics (e.g., 97% overall) may mask poor performance
on specific document types or fields
Stratified random sampling for measuring error rates in high-confidence extractions and
detecting novel error patterns
Field-level confidence scores calibrated using labeled validation sets for routing review
attention
The importance of validating accuracy by document type and field segment before
automating high-confidence extractions

Skills in:
Implementing stratified random sampling of high-confidence extractions for ongoing
error rate measurement and novel pattern detection
Analyzing accuracy by document type and field to verify consistent performance across all
segments before reducing human review
Having models output field-level confidence scores, then calibrating review thresholds
using labeled validation sets
Routing extractions with low model confidence or ambiguous/contradictory source
documents to human review, prioritizing limited reviewer capacity

<hr>

**Incorrect**

**The correct answer is B:**A self-critique step (evaluator-optimizer pattern) directly addresses the root cause of inconsistent explanation completeness by having the agent evaluate its own draft against specific criteria—such as policy context, timelines, and next steps—before presenting it. This catches case-specific gaps that vary across different complex scenarios without requiring human review.

**Your answer:**While few-shot examples can demonstrate ideal response structure for common case types, they cannot adequately cover the highly variable context gaps that differ from case to case. This approach works better for consistent, predictable patterns rather than the diverse omissions described in the scenario.

**Study Area:**Customer Support Resolution Agent — review _Self-Evaluation Patterns_ concepts in the exam study guide.

<hr>
**Incorrect**

**The correct answer is D:**Adding few-shot examples demonstrating correct reasoning and tool sequencing for multi-concern requests is the most effective approach because the agent already handles individual concerns well at 94% accuracy—it simply needs pattern guidance for handling multiple concerns in one message. This is a low-cost, proven technique that directly addresses the root cause of the agent failing to decompose and properly route parameters across multiple requests.

**Your answer:**Using a separate model call to decompose multi-concern messages adds unnecessary latency, complexity, and cost when the agent already demonstrates strong single-concern understanding. This over-engineers the solution when simpler prompt-level guidance can address the pattern recognition gap.

<hr>
**The correct answer is C:**Specifying explicit criteria—flag comments only when their claimed behavior contradicts actual code behavior—directly addresses the root cause by replacing the vague instruction with a precise definition of what constitutes a problem. This eliminates both false positives on acceptable patterns and false negatives on genuinely misleading comments.

**Your answer:**While few-shot examples of misleading comments can help the model recognize similar patterns, this approach won't generalize well to novel types of contradictions because it relies on pattern-matching rather than defining the underlying criterion the model should apply.

<hr>

**The correct answer is D:**Providing concrete input-output examples is the most effective approach because it eliminates the ambiguity inherent in prose descriptions by showing Claude exactly what the expected transformation looks like. This directly addresses the root cause—misinterpretation of prose requirements—by giving unambiguous, concrete targets for field nesting and timestamp formatting.

**Your answer:**A JSON schema can validate the output structure but doesn't help Claude understand the actual transformation logic needed to produce correct results. This approach addresses verification rather than comprehension, meaning Claude would still need to understand the mapping requirements to generate correct output in the first place.

**Study Area:**

<hr>

This is correct. The batch API's asynchronous fire-and-forget model means there is no mechanism to intercept a tool call mid-request, execute the tool, and return results for Claude to continue its analysis. This fundamentally breaks iterative tool-calling workflows that require multiple rounds of tool invocation and response within a single logical interaction.

### Why Option A is Correct

Because batch processing is asynchronous, there is no open connection for the application to listen for tool requests, execute them, and feed the data back into that specific request in real-time. If Claude decides it needs a file mid-batch, the batch item simply finishes and returns a `tool_use` stop reason. You cannot iteratively feed it the requested file contents within that same batch cycle.

### Why the Other Options are Incorrect

- **Option C (The selected answer):** This is factually incorrect. Most modern LLM Batch APIs (including Anthropic's Message Batches API) _do_ support passing tool definitions in the request payload. The problem isn't defining the tools; the problem is the inability to execute the multi-turn back-and-forth required to actually use them.

