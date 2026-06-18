Escalation patterns


---
structured output, including that "other" element in enum
	- including the strategy of include `other` + detail and `unclear`
	- Anthropic's official documentation recommends using few-shot examples to dramatically improve accuracy and consistency in structured data extraction. Specifically, it advises defining a schema and showing examples where missing fields are output as `null`, e.g., 'If a field is not present in the posting, use null'. This directly addresses hallucination by teaching the model the expected behavior for absent data.
	- Correct. According to Anthropic's documentation, this is the recommended approach. Using a string field with an `enum` constraint leverages the Structured Outputs feature's constrained decoding to force the model's output into one of the predefined categories. This explicitly and reliably solves the problem of distinguishing between an absent amenity and an unmentioned one.
---
Anthropic's official cookbooks and API reference document this technique as a highly effective way to guarantee that the model's response conforms to a given JSON schema. By forcing a specific tool call, the model is constrained to produce valid JSON matching the `input_schema`, ensuring consistency even in CI/CD pipelines.

While `output_config.format` is a valid method for structured outputs, it is not the most recommended or reliable technique for strict schema enforcement in all environments. Some models and API versions may not fully support it, and forcing a tool call is the documented fallback that offers broader compatibility and proven reliability.
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

<hr>

escalation
- While identity verification is critical for destructive actions, forcing a user through an automated MFA workflow after they have explicitly requested a human agent is considered a 'bot trap.' Verification should be handled, but it should not serve as a gatekeeper that delays a requested human escalation.
- Best practices for escalation design state that once a user explicitly requests a human agent, the bot should honor that request immediately and without friction. In high-risk security scenarios, the safest and most responsive pattern is to transfer the context to a human who can then oversee the secure verification and approval protocols.
