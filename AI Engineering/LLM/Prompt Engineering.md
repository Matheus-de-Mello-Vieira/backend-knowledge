# Prompt Engineering

Prompt engineering is the process of refining how you ask a model to perform a task in order to get better, more accurate, and helpful results.

There is a famous saying on data science: "garbage in, garbage out", applying it into prompt engineering context: a prompt lacking context, being vague or ambiguous will result in suboptiomal outputs.

Prompt engineering is a blend of science and art.

* science because it is backed by benchmarks and measurable performance improvements. The techniques are supported by research papers focused on improveing prompt quality.
* art because it involves creative approaches to prompt writing

Prompt engineering is not a universal requirement; it’s a tool for specific complexity. For routine requests—summarizing an article, drafting a standard email, or fact-checking—modern AI is intuitive enough to deliver without a "persona" or a list of constraints. If the task is straightforward, keep your input straightforward. Over-complicating the basics adds friction to your workflow without adding value to the output.
## Composition of a prompt

When a prompt is sent, it becomes the input to the LLM. The input is usually a text with many parts:

* task: tells the llm what action to do.
* context: the context of the task, helps the LLM understand the domain.
* output indicator: it can be an exclamation point, a period, or simply nothing. It tells the LLM that the asking part is finished, and now the output should start.

For example: "Write me a song about rainy days"

* Task: "Write me a song"
* Context: "about rainy days"

## System Prompt

The system prompt is a permanent instruction set that remains fixed within an AI's context window throughout a conversation. Unlike standard user messages, it is never pruned to make room for new data, ensuring the model maintains its core logic indefinitely.

- **The Context Anchor:** While the model deletes older user and agent messages to stay within token limits, the system prompt stays pinned at the start of the conversation.
- **Behavioral Insurance:** Placing instructions here ensures the AI maintains a consistent persona or tone, such as a pirate or a professional assistant, regardless of how long the chat lasts.
- **Strict Technical Guardrails:** This is the ideal location to define rigid constraints, such as forcing the model to generate code only for a specific software version or framework.
- **The Hidden Architect:** Many consumer AI interfaces hide the system prompt from users to protect the tool’s underlying rules and ensure it functions as intended by the developer.
- **The Refiner’s Tool:** In professional workflow builders, editing the system prompt allows for precise control over outputs, making it the most powerful lever for steering AI behavior.
### Assigning AI Roles

Defining a specific role for the AI frames its perspective and dictates the tone, complexity, and focus of its responses. This technique ensures the model analyzes all subsequent instructions through a specialized professional or persona-based lens.

- **The Persona Filter:** Starting a prompt with "Act as..." forces the AI to process information through a specific professional or creative viewpoint, such as a software engineer versus a product manager.
- **Where to Put It:** If you don't have access to the system prompt, just place the role at the very beginning of your first message; it works just as well for most chats.
	- **Context Management:** If the role is defined in a standard message, keep conversations focused and concise to prevent the instruction from being pushed out of the model's active memory window.
- **Complexity Control:** Adjusting the assigned role—from a middle school teacher to a university professor—drastically alters the depth, terminology, and technical detail of the output.
- **Clarity for Humans:** Beyond influencing the AI, explicit roles help other team members immediately understand the intent and expected output style of a specific prompt.
- **Optional vs. Essential:** Specific roles are unnecessary for basic factual queries, such as the distance to the moon, but are critical when you require a distinct tone or specialized expertise.
## Sampling Parameters

When you want to control how creative, focused, or random your LLM's outputs are, you use **sampling parameters**. For a deep dive into the math and mechanics, see [here](LLM%20Processing%20Pipeline.md#Stochastic%20Sampling). Below, we’ll focus entirely on the practical side: how to use them to shape your model's responses.

### Penalties

Large language models love patterns. Sometimes, they love them too much, causing them to get stuck in loops or overuse the same words. To prevent this, we use penalty parameters that mathematically lower the probability of words that have already been generated.

>[!warning]
> Be gentle with penalties. Setting a repetition or frequency penalty too high (e.g., closer to `2.0`) will make the text look incredibly unnatural, as the model will literally run out of common words (like "and", "the", or the main subject name) and start forcing bizarre synonyms just to bypass the penalty.
#### Repetition Penalty (Open-Source / Hugging Face Standard)

This parameter applies a broad penalty to any token that has already appeared in the text.

- **How it works:** It acts as a multiplier (usually starting at `1.0` for no penalty). Setting it to `1.1` or `1.2` slightly reduces the probability of _all_ previously used words.
- **When to use:** It is a great default safety switch in open-source models to keep the text moving forward and stop infinite loops.

#### Frequency vs. Presence Penalties (OpenAI Standard)

Many modern APIs split the concept of repetition into two surgical tools. They generally range from `-2.0` to `2.0`, where positive numbers discourage repetition.

- **Frequency Penalty (The Word Trimmer):** This penalty is proportional to how many times a word has _already_ appeared. The more times the model says a word, the harder it gets penalized.
    - _Best for:_ Keeping vocabulary diverse in long-form essays or articles. It stops the model from saying "the user" or "important" twenty times in three paragraphs.
  
- **Presence Penalty (The Topic Shifter):** This is a flat, binary penalty. It doesn't care if a word appeared once or fifty times; as soon as it shows up, it gets penalized.
    - _Best for:_ Creative writing and brainstorming. By penalizing words that have already been introduced, it forces the model to constantly bring up _new_ concepts and vocabulary.
### Temperature

Temperature controls the "creativity" or predictability of the model.

- **Low Temperature (0.0 to 0.3):** Makes the model highly deterministic. It will almost always choose the most likely next words. Use this for tasks that require high accuracy and adherence to facts, such as **coding, data extraction, or factual Q&A**.
- **High Temperature (0.7 to 1.0+):** Introduces more randomness, forcing the model to pick less obvious words. Use this for brainstorming, **creative writing, or narrative generation**.
### Top-K

Top-K cuts off the model's vocabulary choices to a strict number of the most likely next words.

- **Usage:** If you set Top-K to 50, the model will _only_ consider the top 50 most probable tokens, completely ignoring the rest of its vocabulary.
- **When to use:** It acts as an absolute safety net. If you are running a high temperature, Top-K guarantees the model will never fetch a completely bizarre, obscure word from the deep tail of its vocabulary. It is also excellent for handling **flat distributions** (e.g., if you ask the model to "List a random color," Top-K prevents it from choosing an incredibly rare hue).
### Top-P

Top-P filters choices based on a cumulative probability threshold rather than a fixed number of words.

- **Usage:** If you set Top-P to 0.9, the model pools the most likely words whose probabilities add up to 90%. If a few words are highly likely, the pool stays small. If many words are plausible, the pool expands dynamically.
- **When to use:** It offers more fluid, context-aware control than Top-K. It's excellent for maintaining a natural conversational flow without letting the model derail.

### Combining the Four: The Generation Pipeline

You don't have to choose between these parameters. In modern inference engines, developers frequently chain **Temperature, Top-K, Top-P, and Penalties** together into a highly controlled, multi-stage pipeline that processes and shapes tokens in this specific order:

1. **Penalties adjust for history.**: First, the engine reviews what has already been generated. If presence, frequency, or repetition penalties are active, the raw scores (logits) of words that have already appeared are mathematically downgraded to prevent loops.
2. **Temperature reshapes the terrain.** Next, Temperature scales those adjusted scores. A high temperature flattens the distribution (making unexpected or heavily penalized words more competitive), while a low temperature steepens it (making the top favorites dominant).
3. **Top-K applies a hard ceiling.** The model then instantly chops off the long tail of the vocabulary, keeping only a strict number of choices (e.g., the top 50 words). This ensures that absolute gibberish is physically blocked from the pool.
4. **Top-P dynamically refines the pool.** Finally, Top-P looks at that surviving subset and narrows it down further based on context, keeping only the tokens that make up a specific cumulative probability (e.g., the top 90%).

By combining all four, you gain absolute authority over the output: Temperature sets the creative risk level, Penalties stop the model from repeating its own ideas, Top-K provides an unbreakable safety guardrail, and Top-P ensures natural, fluid context-awareness.

| **Goal / Use Case**                                                                   | **Temperature**                              | **Top-K**                               | **Top-P**                          | **Penalties**                                                           | **Why this combination works**                                                                                                                                                                                                                    |
| ------------------------------------------------------------------------------------- | -------------------------------------------- | --------------------------------------- | ---------------------------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Strict Facts / Code**<br><br>  <br><br>_(Data extraction, math, coding)_            | **Low**<br><br>  <br><br>(0.0 – 0.2)         | **Off**<br><br>  <br><br>(or high, 100) | **Low**<br><br>  <br><br>(0.1)     | **None**<br><br>  <br><br>(0.0 / 1.0)                                   | Low temperature and tight Top-P isolate only the absolute highest-probability tokens, while disabling penalties ensures the model is free to reuse required variable names, code structures, or repetitive data structures safely.                |
| **Balanced Conversation**<br><br>  <br><br>_(Customer support, general Q&A)_          | **Medium**<br><br>  <br><br>(0.5 – 0.7)      | **Off**<br><br>  <br><br>(Default)      | **Medium**<br><br>  <br><br>(0.9)  | **None**<br><br>  <br><br>(0.0 / 1.0)                                   | Uses a moderate temperature and standard Top-P to allow for fluid, human-like sentence variation. Keeping Top-K and penalties off allows natural vocabulary and conversational pacing to flow without artificial restrictions.                    |
| **Creative Writing / Fiction**<br><br>  <br><br>_(Scripts, stories, poetry)_          | **High**<br><br>  <br><br>(0.8 – 1.0)        | **High**<br><br>  <br><br>(80 – 100)    | **High**<br><br>  <br><br>(0.95)   | **Presence / Repetition**<br><br>  <br><br>(Pres: 0.5 – 0.8 / Rep: 1.1) | High temperature flattens probabilities to introduce unusual words, while wide Top-K/Top-P ceilings keep options open. The presence penalty complements this by pushing the model to continually explore fresh plot concepts and phrasing.        |
| **Wild Brainstorming**<br><br>  <br><br>_(Marketing taglines, concept ideation)_      | **Very High**<br><br>  <br><br>(1.2 – 1.5)   | **Tight**<br><br>  <br><br>(30 – 40)    | **High**<br><br>  <br><br>(0.95)   | **Presence**<br><br>  <br><br>(Pres: 0.8 – 1.2)                         | Extreme temperature forces maximum risk-taking, which is immediately reigned in by a narrow Top-K ceiling to block gibberish. A high presence penalty rounds this out by forcing the model to switch topics rather than repeating the same angle. |
| **Structured Output**<br><br>  <br><br>_(Strict JSON, YAML, or XML parsing)_          | **Absolute Zero**<br><br>  <br><br>(0.0)     | **Off**                                 | **Off**                            | **None**<br><br>  <br><br>(0.0 / 1.0)                                   | Setting temperature to zero strips away all sampling randomness. Leaving Top-K, Top-P, and penalties completely unrestrictive ensures the model strictly calculates and follows structural syntax rules over creative variation.                  |
| **Roleplay / Persona Chatbots**<br><br>  <br><br>_(Gaming NPCs, historical personas)_ | **Medium-High**<br><br>  <br><br>(0.7 – 0.8) | **Medium**<br><br>  <br><br>(50)        | **Medium**<br><br>  <br><br>(0.85) | **Frequency**<br><br>  <br><br>(Freq: 0.2 – 0.4)                        | Elevated temperature drives witty character banter, capped smoothly by an intermediate Top-K and Top-P to stay structurally relevant. A mild frequency penalty cuts down on annoying catchphrase looping without ruining persona logic.           |
## Core Principles
These core principles streamline AI communication, ensuring every prompt generates high-value, actionable results. Focus on clarity and structure to eliminate guesswork and maximize technical accuracy.

### Be Specific

Effective AI prompting requires balancing strict specificity with extreme simplicity to prevent hallucinations. Providing clear, concise instructions guarantees accurate and targeted outputs without confusing the model.

- **The New Hire Analogy:** Treat the AI like a brilliant new employee with flawless credentials but zero project context. You must explicitly detail every task requirement without assuming any prior knowledge.
- **The Specificity Balance:** Define your exact needs, such as explicitly replacing identifying data with 'XXX' or dictating that the output must contain zero additional commentary. Unambiguous boundaries prevent the AI from making unapproved decisions.
- **The Iterative Approach:** Start with a clear, concise request to generate a high-level baseline. You can always ask targeted follow-up questions to expand on specific points later.
	- **The Baseline Draft:** Begin with a minimal, structurally sound prompt to establish your foundation. Ask for a high-level summary or a simple table first so you can verify the AI understands the core task before complicating it.
	- **The Targeted Drill-Down:** Avoid packing every possible requirement into your initial request. Once you have your baseline, use follow-up prompts to expand only on the specific sections or ideas that need more depth.
	- **The Single-Variable Tweak:** When refining an output, adjust only one constraint at a time. If you change the tone, the length, and the format all at once, you won't know which instruction caused the model to derail.
	- **The Corrective Nudge:** If the AI deviates from your goal or hallucinates, do not start over and rewrite the entire initial prompt from scratch. Simply tell the model exactly what to fix, replace, or omit in the very next conversational turn.
	- **The Context Chain:** Treat the conversation as a continuous thread. Because the AI retains the context of the current chat, you can build incredibly complex and nuanced outputs one simple, easily digestible step at a time.
- **The Anti-Jargon Rule:** Avoid corporate buzzwords and overly complex phrasing. If you would not use a convoluted phrase in daily conversation with a colleague or client, do not use it with an AI.
- **The Editing Imperative:** Good writing is the ability to cut unnecessary words. Review your drafted prompts and ruthlessly delete filler language, as every useless word increases the chance of the model generating irrelevant outputs.
- **The Redundancy Trap:** Never over-explain established concepts. If you instruct the AI to use a specific, recognized business framework, you do not need to separately command it to follow the fundamental rules already built into that framework.
- **The Human Test:** Read your prompt aloud to a colleague to verify clarity. If a human cannot quickly understand your request or describe the correct execution process, the AI will inevitably fail at it too.
### Don't leave room for interpretations

Effective prompting requires balancing the AI's existing knowledge with explicit context to prevent guesswork and hallucination. By defining custom rules and eliminating ambiguity, you ensure the AI delivers precise, actionable results rather than generic interpretations.

- **The Information Baseline:** Assume the AI requires the same level of detail a human would need to complete a task, despite its extensive pre-existing training.
- **The Probe Protocol:** Before assuming the AI understands specific technical acronyms like DRY or KISS, ask it to define the terms to ensure your foundational concepts are aligned.
- **Custom Rule Injection:** Explicitly define project-specific constraints—such as unique naming conventions or internal proprietary protocols—within the prompt before referencing them in a task.
- **The Knowledge Expiration:** Account for training cutoffs by manually providing data or articles for any events, tools, or documentation that emerged after the AI’s last update.
- **The Interpretation Hazard:** Avoid vague instructions like "ask me if you need more info," as generative models are designed to produce results and will often "fill in the gaps" with assumptions rather than seeking clarification.
- **The Benchmarking Strategy:** To ensure the AI identifies missing information accurately, provide a specific checklist of required sections or criteria it must use to evaluate the input.
- **The Generation Trap:** Recognize that a "bad" response is often a symptom of missing context; if the AI isn't given a clear boundary, it will prioritize generating text over maintaining accuracy.
### Don't ask for everything at once

AI performance improves significantly when complex requests are broken down into a series of smaller, manageable tasks. Treating your prompt as a step-by-step conversation prevents shallow results and minimizes the risk of model hallucinations.

- **The Multi-Task Penalty:** Cramming several distinct requests into one prompt often forces the AI to provide surface-level responses or skip critical details to satisfy every requirement at once.
- **The Iterative Advantage:** Prompting is naturally conversational; handling one task at a time mimics human workflow and allows the AI to focus its full processing power on a single objective.
- **Deep-Dive Accuracy:** Single-task prompts yield more technical depth, such as detailed formula explanations and optimized logic, whereas "all-in-one" prompts often resort to generic solutions.
- **Modular Troubleshooting:** Isolating tasks makes it easier to refine specific steps; if one part of the process fails, you can ask for corrections without the AI losing track of the broader context or breaking previous work.
- **The Lost-in-the-Middle Effect:** AI models naturally prioritize information at the beginning and end of a prompt, meaning critical instructions buried in the middle of a long request are frequently ignored. See [why](LLM%20Processing%20Pipeline.md#The%20"Lost-in-the-Middle"%20Effect).
- **Detail vs. Density:** Effective prompting requires detailed explanations for specific actions rather than a high density of different goals. Focus on being thorough about one task before moving to the next.

### Ensure the formatting of the response

AI outputs are inherently non-deterministic, leading to unpredictable formatting that can disrupt automated workflows. Mastering response control requires a combination of hyper-specific constraints and the strategic use of examples to ensure consistency and scalability.

- **The Format Gamble:** Without explicit instructions, AI models default to unpredictable layouts—randomly mixing code blocks, markdown, or conversational filler—which makes the output difficult to process reliably.
- **The Scalability Anchor:** Standardizing output formats is essential for scaling prompts across teams and ensuring the response from one prompt can serve as a clean, predictable input for the next step in an automated chain.
- **The Precision Hammer:** Achieving a specific result requires extreme specificity and repetition; explicitly tell the AI what to exclude, such as "no commentary" or "code only," to override its tendency to be chatty.
- **The Golden Rule:** Providing a concrete example is the most effective way to dictate tone and structure, as AI models are optimized to follow patterns even when those patterns contradict written instructions.
- **The Bootstrap Method:** If you lack a reference template, iterate with the AI to generate a single perfect response, then "feed" that result back into your main prompt as the official formatting example.
- **The Logic Override:** Examples possess such high instructional weight that the model will often follow the format of a provided snippet even if the text instructions mistakenly ask for a different file type.
- **The Workflow Chain:** Consistent formatting is the "glue" for complex operations, such as refiner engines, where any deviation in the first output will cause the entire subsequent logic path to fail.
- **The Complexity Filter:** While simple questions don't require rigid formatting, save these high-effort techniques for technical tasks like coding or project documentation where specific standards and indentations are non-negotiable.
### Managing Long-Context Prompts

As AI context windows expand to handle massive datasets, structural organization becomes the deciding factor in maintaining output quality. Proper prompt architecture ensures the model remains focused on your primary objective despite high information density.

- **The Single-Focus Standard:** Even when providing millions of tokens of data, always restrict the AI to one specific output at a time—such as a single class or unit test—to prevent logic breakdown and confusion.
- **The Priority Zones:** Place critical instructions at the very beginning or the absolute end of your prompt, as models naturally deprioritize information buried in the middle of long datasets.
- **The Structural Roadmap:** Use clear tags or labels (e.g., Context, Task, Document 1) to categorize information, allowing the AI to easily index and reference specific data points within a large volume of text.
- **The Indexing Advantage:** Organizing multiple reference materials into labeled sections enables the AI to cite specific sources accurately, leading to more grounded and verifiable responses.
- **The Context Trap:** Do not mistake a larger context window for an invitation to multitask; overloading a single prompt with multiple objectives remains the most common cause of poor performance in advanced models.
- **The Reference Rule:** Effective long-context prompting relies on using the available space for background information and data while keeping the "ask" extremely targeted and isolated.
### Formatting and Organization

Treating prompts as living code ensures they remain understandable, editable, and scalable for future users. Effective prompt engineering prioritizes human readability alongside machine performance to facilitate long-term collaboration.

- **The Natural Language Script:** Prompts are functional instructions for a machine; viewing them as code shifts the focus from one-off queries to durable, reusable assets that require standard maintenance.
- **The Hand-Off Principle:** Assume that a colleague will eventually need to update your prompt. Clear structure prevents technical debt and ensures the logic remains accessible when the original creator is no longer involved.
- **The Documentation Layer:** Since internal "comments" are interpreted by the AI and can skew results, use external metadata—such as prompt titles and descriptions—to explain the intent and expected outcome to human users.
- **The Human-Centric UI:** Use visual elements like Markdown tags, bolding, and whitespace to create a hierarchy. While the AI may process a dense block of text, human editors need visual cues to identify where to safely modify variables or instructions.
- **The Versioning Mindset:** A well-organized prompt is easier to troubleshoot and refine, allowing it to evolve alongside model updates without requiring a complete rewrite every time a project requirement changes.
## Techniques

### Zero-Shot Prompting

Prompting the model without providing any examples or demonstrations.

* **How it works**: You simply write the task you want the model to perform, and it generates a response based solely on its pretraining.
* **Key Traits**: Offers maximum freedom but may result in vague or unpredictable output.
* **When to Use**: Best for simple, well-understood tasks.

**Example**:

```
Write me a song about rainy days.
```

### Few-Shot Prompting

A prompting technique where the model is given a few examples before being asked to perform a task.

- **How it works**: You show the model several input-output pairs, allowing it to learn a pattern and then apply that pattern to a new input.
- **Key Traits**: Helps guide the model by providing clear expectations, improving accuracy and consistency in the response.
- **When to Use**: Best for tasks like classification, translation, or summarization, where following a consistent structure matters.

**Example**:

```
Classify the sentiment as Positive or Negative.

This movie was terrible -> Negative
This movie was awesome, I loved it -> Positive
The acting was flat and the plot was boring -> Negative
The cinematography was beautiful and the story was inspiring -> Positive

This movie was way too long and the ending was disappointing -> 
```

The model learns the pattern from the provided `input → label` examples and applies the same pattern to the final unseen sentence:

```
Negative
```

### Chain of Thought Prompting

Researchers have found that asking a model to explain its reasoning step-by-step significantly improves performance. This is especially effective for complex tasks because it forces the model to process logic linearly rather than jumping straight to a conclusion. By explaining why it chooses one path over another, the model is less likely to hallucinate and more likely to arrive at a correct final answer.

**How to use it**:
Simply append a short instruction to your prompt, such as:

- "Let’s think step-by-step."
- "Show your chain of thought."
- "Explain your reasoning before providing the final answer."

While many modern systems (like ChatGPT or Gemini) now have some reasoning behavior built-in, explicitly requesting a step-by-step breakdown still provides extra clarity and helps you verify the logic behind the output.

## Prompting for applications

* **Prompts guide AI outputs**: Every AI application relies on carefully crafted prompts to guide the model’s output
* **Prompts combine user input with product rules**: The AI tailors responses by mixing what the user asks with structured instructions from the product
* **Iteration and refinement improve results**: Prompts are continuously tested and adjusted to produce more accurate, relevant, and high-quality outputs