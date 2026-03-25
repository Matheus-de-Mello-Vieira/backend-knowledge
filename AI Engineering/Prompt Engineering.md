# Prompt Engineering

Prompt engineering is the process of refining how you ask a model to perform a task in order to get better, more accurate, and helpful results.

There is a famous saying on data science: "garbage in, garbage out", applying it into prompt engineering context: a prompt lacking context, being vague or ambiguous will result in supoptiomal outputs.

Prompt engineering is a blend of science and art.

* science because it is backed by benchmarks and measurable performance improvements. The techniques are supported by research papers focused on improveing prompt quality.
* art because it involves creative approaches to prompt writing

## Composition of a prompt

When a prompt is sent, it becomes the input to the LLM. The input is usually a text with many parts:

* task: tells the llm what action to do.
* context: the context of the task, helps the LLM understand the domain.
* output indicator: it can be an exclamation point, a period, or simply nothing. It tells the LLM that the asking part is finished, and now the output should start.

For example: "Write me a song about rainy days"

* Task: "Write me a song"
* Context: "about rainy days"

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

## Rule of thumb in prompting

* **Always be explicit with the task**: Clear instructions reduce unwanted results
* **Provide context and examples to guide responses**: Context frames the answer and examples show the format
* **Clarify explicitly what you do not want**: Prevents irrelevant or off-topic answers

### In applications

* **Prompts guide AI outputs**: Every AI application relies on carefully crafted prompts to guide the model’s output
* **Prompts combine user input with product rules**: The AI tailors responses by mixing what the user asks with structured instructions from the product
* **Iteration and refinement improve results**: Prompts are continuously tested and adjusted to produce more accurate, relevant, and high-quality outputs