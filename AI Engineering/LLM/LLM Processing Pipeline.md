# LLM Processing Pipeline

The LLM Processing Pipeline is the sequence of computational steps a Generative AI model takes to transform a human-readable prompt into a predicted response. Rather than understanding language organically, models push inputs through a highly structured, mathematical assembly line to generate output one piece at a time.

- **The Assembly Line:** Every time you submit a prompt, the text undergoes a rigorous transformation. It starts as raw characters, breaks down into discrete tokens, converts into high-dimensional mathematical vectors, and finally resolves back into human language.
- **The Predictive Engine:** At its core, the entire pipeline is built to execute one fundamental task: calculating the statistical probability of what the very next token should be, based strictly on the context of everything that preceded it.
- **The Iterative Loop:** Unlike traditional software that processes a command and returns a complete result instantly, an LLM generates its response sequentially. The pipeline loops continuously, feeding each newly predicted token back into the system as new input until a stopping condition is met.
- **The Architectural Blueprint:** Understanding this step-by-step pipeline—from Tokenization down to the final Decoding—is essential for engineers. It clarifies how models evaluate context, why they hit strict memory limits, and where they are structurally prone to hallucination.
## Tokenization

Tokenization is the process of converting raw text into smaller units that the model can process.

- **What it does:** Splits text into model-specific tokens.
- **Why it matters:** Token boundaries affect cost, context usage, and sometimes behavior.
- **Common reality:** Tokens are not the same as words; they may be full words, subwords, punctuation, or whitespace fragments.
- **Rule of thumb:** In standard natural language, **1 token is roughly 3/4 of a word**, so 100 tokens is often about 75 words.

Token boundaries do not always align perfectly with whole words, and tokenization is not universal across models. The exact token count for the same input changes depending on the tokenizer design used by the model provider.

- **Model variance:** Different tokenizers split the same sentence differently, which changes cost calculations and context-window usage.
- **The multilingual tax:** Because most prominent tokenizers are trained predominantly on English data, non-English languages—especially those with non-Latin scripts (like Cyrillic, Arabic, Hindi, or Mandarin)—are often split into much smaller fragments. A single word in English might be 1 token, while its translation in another language could consume 3 or 4 tokens, making multilingual prompts significantly more expensive and context-heavy.
	- **The domestic flip (Chinese LLMs):** For Chinese-developed models like **DeepSeek** or **Qwen**, the native language is treated as a first-class citizen. Their tokenizers are built with massive vocabularies that include tens of thousands of whole Chinese characters and common multi-character phrases (like "人工智能" - _Artificial Intelligence_) as single tokens. Because Chinese characters inherently possess very high information density, **Chinese text on a Chinese LLM actually consumes fewer tokens than its English translation** (often dropping to a 0.65x ratio compared to English).
- **The code tax:** Code, JSON, markup, and other symbol-heavy text usually consume more tokens than plain prose because they contain more punctuation, indentation, and short repeated fragments.
- **Practical implication:** Before sending large prompts, it is worth checking token counts to avoid truncation, unnecessary cost, or leaving too little room for the model's response.
- **Useful tools:** OpenAI provides a visual [Tokenizer](https://platform.openai.com/tokenizer) and the open-source [Tiktoken](https://github.com/openai/tiktoken) library for local token counting and inspection.

### Under the Hood: Tokenization Algorithms

How do tokenizers actually decide where to draw the boundaries? They do not rely on standard dictionaries; instead, they use statistical algorithms to find the most computationally efficient way to pack information. Here are the three primary methodologies you will encounter:

- **Byte Pair Encoding (BPE):** The most widespread algorithm, used heavily by OpenAI (GPT) and Meta (Llama). BPE works from the bottom up. It starts by breaking all text into individual characters (bytes) and iteratively merges the most frequently occurring adjacent pairs into single tokens. This is why a common word like "apple" becomes one token, but a rare word like "synecdoche" is left fragmented into multiple subword tokens.
- **Unigram Tokenization:** This algorithm works in reverse, from the top down. It begins with a massive, over-populated vocabulary of words and subwords, and systematically trims away the statistically least useful tokens until it reaches a strict target vocabulary size. It evaluates the probability of subword combinations, making it highly flexible and efficient for models that need to balance complex vocabularies.

> [!info] **SentencePiece**
> Developed by Google, this is a tokenization utility rather than a standalone base algorithm (it typically runs BPE or Unigram under the hood). Traditional tokenizers assume that spaces naturally separate words, which completely breaks down when processing languages like Chinese or Japanese that do not use spaces. SentencePiece solves this by treating the space itself as just another character (often represented visually as a `_`), allowing it to cleanly process raw text across any language family without requiring language-specific pre-processing.

### Special Tokens: The Control Signals

Beyond the visible text, tokenizers also inject invisible structural markers into the pipeline. These special tokens act as control signals, providing the underlying model with essential navigational metadata about the sequence it is processing.

- **The Starting Gun:** The Beginning of Sequence (BOS) token (often represented as `<s>` or `<|startoftext|>`) tells the model where the prompt actually starts. It initializes the model's internal state and signals that it should begin evaluating the context.
- **The Stop Sign:** The End of Sequence (EOS) token (like `</s>` or `<|endoftext|>`) is arguably the most critical control marker. Because an LLM's natural mathematical state is to predict the next token continuously, the EOS token acts as the designated stopping condition. When the model predicts this specific token, it breaks the iterative generation loop and finalizes your output.
- **The Boundary Lines:** Separator tokens establish rigid structure within the prompt. In modern chat-optimized models, specific formatting tokens (such as `<|im_start|>user` and `<|im_end|>`) strictly divide system instructions, human input, and the AI's previous replies. This structural mapping helps prevent context bleed and mitigates prompt injection attacks.
- **The Filler Material:** Because LLMs are designed to process data in parallel batches for efficiency, every sequence in a computing batch must be the exact same length. Padding tokens (`<pad>`) are essentially meaningless blank spaces appended to the end of shorter prompts to make them fit the uniform batch matrix. The model is mathematically instructed (via an attention mask) to completely ignore these filler tokens during processing.

## Embedding Lookup

Once text has been tokenized, each token ID is converted into a dense vector representation.

- **What it does:** Maps discrete token IDs into continuous vector space.
- **Why it matters:** Neural networks operate on numbers, not raw strings.
- **Mental model:** Embeddings are the model's learned coordinate system for representing symbolic input.

**Topics to expand later**

- Token embeddings vs positional embeddings
- Learned representations and semantic structure
- Why embedding layers are different from retrieval embeddings used in RAG systems
- Input embedding matrix and output projection weight tying

## 3. Positional Information

A sequence model must know not only *which* tokens exist, but also *where* they appear in the sequence.

- **What it does:** Encodes order information so the model can distinguish `"dog bites man"` from `"man bites dog"`.
- **Why it matters:** Attention alone is permutation-invariant without positional information.

**Topics to expand later**

- Absolute positional embeddings
- Rotary positional embeddings (RoPE)
- Relative position schemes
- Why positional design influences long-context behavior

## 4. Contextualization via Transformer Layers

This is the core computation stage where the model builds meaning by allowing each token to interact with other tokens in the sequence.

- **What it does:** Rewrites token representations layer by layer using self-attention and feed-forward blocks.
- **Why it matters:** The vector for a token becomes context-dependent rather than static.
- **Example:** The representation of `"bank"` changes depending on whether nearby tokens refer to finance or a river.

### Self-Attention

Self-attention allows each token to weigh the relevance of other tokens when updating its internal representation.

**Topics to expand later**

- Query, key, and value vectors
- Attention scores and softmax normalization
- Multi-head attention
- Causal masking in decoder-only models

### Feed-Forward Networks

After attention mixes information across tokens, feed-forward layers transform each token representation independently.

**Topics to expand later**

- MLP blocks
- Non-linear activations
- Residual connections
- Layer normalization

## 5. Logits and Next-Token Prediction

After the final transformer layer, the model produces a score for every possible token in its vocabulary.

- **What it does:** Converts the final hidden state into logits over the vocabulary.
- **Why it matters:** These logits represent the model's raw preferences before sampling or selection.

**Topics to expand later**

- Vocabulary-wide scoring
- Softmax probabilities
- Why the highest-probability token is not always chosen
- Calibration and confidence limitations

## 6. Decoding and Token Selection

Decoding is the policy layer that turns logits into an actual output token.

- **What it does:** Applies a selection strategy to choose the next token.
- **Why it matters:** Decoding strongly affects creativity, determinism, repetition, and factual stability.

**Common strategies**

- **Greedy decoding:** Always pick the highest-probability token.
- **Temperature scaling:** Adjusts how flat or sharp the probability distribution is.
- **Top-k sampling:** Restricts selection to the `k` most likely tokens.
- **Top-p (nucleus) sampling:** Restricts selection to the smallest token set whose cumulative probability exceeds `p`.

**Topics to expand later**

- Frequency and presence penalties
- Beam search
- Stop sequences
- Structured decoding for JSON or grammar-constrained outputs

## 7. Iterative Generation Loop

Generation is autoregressive: each newly produced token becomes part of the context for predicting the next one.

- **What it does:** Repeats prediction until a stop condition is reached.
- **Stop conditions:** End-of-sequence token, token limit, tool handoff, or application-level cutoff.
- **Key implication:** Errors can compound because flawed tokens become part of the future context.

**Topics to expand later**

- KV cache and why it improves decoding efficiency
- Streaming output
- Response truncation
- Repetition loops and degeneration

## 8. Context Window Constraints

The entire pipeline operates within a finite token budget.

- **What it does:** Limits how much prior text the model can attend to during inference.
- **Why it matters:** Older instructions may be dropped, diluted, or effectively ignored.
- **See also:** [Context Engineering](Context%20Engineering.md)

**Topics to expand later**

- Sliding window behavior
- Lost-in-the-middle effects
- Attention scaling limits
- Tradeoffs between long context and latency

## 9. Inference vs Training

This note is about **inference**, not training.

- **Inference:** The model uses fixed weights to predict tokens.
- **Training:** The model updates weights by minimizing prediction error across large datasets.

> **Rule of Thumb:** During inference, the model is not "learning" new facts into its parameters. It is applying previously learned weights to the current context.

**Topics to expand later**

- Pretraining objective
- Supervised fine-tuning
- RLHF and post-training alignment
- Why prompting changes behavior without changing weights

## 10. Where Adjacent Systems Fit

Several common LLM system components are *outside* the core processing pipeline but influence its inputs and outputs.

- **Prompt Engineering:** Shapes the instruction payload before tokenization. See [Prompt Engineering](Prompt%20Engineering.md).
- **Context Engineering:** Controls what information enters the context window. See [Context Engineering](Context%20Engineering.md).
- **RAG:** Injects retrieved external information before or during generation. See [RAG Fundamentals](../RAG/01%20Fundamentals.md).
- **Tool Calling:** Delegates precise actions outside the model's internal reasoning loop.

## Common Misconceptions

- **"The model thinks in words."** It operates over token IDs and vector transformations.
- **"Embeddings are the same as understanding."** Embeddings are only the starting representation; contextualization happens deeper in the network.
- **"The model writes a full answer at once."** It predicts one token at a time.
- **"Temperature makes the model smarter."** It changes sampling behavior, not the knowledge stored in the model.
- **"Longer prompts always improve results."** More context can also dilute signal and increase cost.

## Suggested Expansions

- Add one worked example tracing a short prompt through tokenization, attention, and decoding.
- Add a section on KV cache, batching, and serving latency for production systems.
- Add a section comparing decoder-only, encoder-only, and encoder-decoder architectures.
- Add diagrams for attention, masking, and the autoregressive loop.

## Related Notes

* [Large Language Models (LLMs)](LLM.md): Use this note for a broad overview of what LLMs are, what they can do, and how they evolved.
* [Context Engineering](Context%20Engineering.md): Read this note to understand how context selection, memory, and token limits shape model performance.
* [Prompt Engineering](Prompt%20Engineering.md): Go here for practical techniques to steer output behavior with instructions, examples, and constraints.
* [RAG Fundamentals](../RAG/01%20Fundamentals.md): Use this note when the system augments the model with retrieved external knowledge.
