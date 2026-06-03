# LLM Processing Pipeline

The LLM Processing Pipeline is the sequence of computational steps a Generative AI model takes to transform a human-readable prompt into a predicted response. Rather than understanding language organically, models push inputs through a highly structured, mathematical assembly line to generate output one piece at a time.

- **The Assembly Line:** Every time you submit a prompt, the text undergoes a rigorous transformation. It starts as raw characters, breaks down into discrete tokens, converts into high-dimensional mathematical vectors, and finally resolves back into human language.
- **The Predictive Engine:** At its core, the entire pipeline is built to execute one fundamental task: calculating the statistical probability of what the very next token should be, based strictly on the context of everything that preceded it.
- **The Iterative Loop:** Unlike traditional software that processes a command and returns a complete result instantly, an LLM generates its response sequentially. The pipeline loops continuously, feeding each newly predicted token back into the system as new input until a stopping condition is met.
- **The Architectural Blueprint:** Understanding this step-by-step pipeline is essential for engineers. It clarifies how models evaluate context, why they hit strict memory limits, and where they are structurally prone to hallucination.
## 1. Tokenization

Tokenization is the process of translating human-readable text into the mathematical inputs required by neural networks. This translation occurs in two distinct steps: first, the raw text string is sliced into smaller fragments (words, subwords, or characters); second, each unique fragment is mapped to its corresponding integer ID from the model vocabulary.

- **What it does:** Converts continuous strings of text into a discrete array of integer token IDs.
- **Why it matters:** The model never reads or generates text directly; it operates entirely on these integer sequences. Token boundaries directly affect inference cost, context usage, and downstream reasoning behavior.
- **The Dual Nature:** A token is a linguistic concept (the string fragment like "app"), but to the model pipeline, a token is purely a number (the integer index like `7402` in the vocabulary matrix).
- **The Rule of Thumb:** In standard natural language, **1 token is roughly ¾ of a word**, meaning a sequence of 100 tokens typically translates to about 75 words.

### Understanding Token Variance and Cost

Token boundaries do not always align perfectly with whole words, and tokenization is not universal across models. The exact token count for the same input changes depending on the tokenizer design used by the model provider.

- **Model variance:** Different tokenizers split the same sentence differently, which changes cost calculations and context-window usage.
- **The multilingual tax:** Because most prominent tokenizers are trained predominantly on English data, non-English languages—especially those with non-Latin scripts (like Cyrillic, Arabic, Hindi, or Mandarin)—are often split into much smaller fragments. A single word in English might be 1 token, while its translation in another language could consume 3 or 4 tokens, making multilingual prompts significantly more expensive and context-heavy.
	- **The domestic flip (Chinese LLMs):** For Chinese-developed models like **DeepSeek** or **Qwen**, the native language is treated as a first-class citizen. Their tokenizers are built with massive vocabularies that include tens of thousands of whole Chinese characters and common multi-character phrases (like "人工智能" - _Artificial Intelligence_) as single tokens. Because Chinese characters inherently possess very high information density, **Chinese text on a Chinese LLM actually consumes fewer tokens than its English translation** (often dropping to a 0.65x ratio compared to English).
- **The code tax:** Code, JSON, markup, and other symbol-heavy text usually consume more tokens than plain prose because they contain more punctuation, indentation, and short repeated fragments.
- **Practical implication:** Before sending large prompts, it is worth checking token counts to avoid truncation, unnecessary cost, or leaving too little room for the model's response.
- **Useful tools:** OpenAI provides a visual [Tokenizer](https://platform.openai.com/tokenizer) and the open-source [Tiktoken](https://github.com/openai/tiktoken) library for local token counting and inspection.

### The Model Vocabulary

The model vocabulary is the strict, pre-defined master list of all possible tokens a model is capable of processing, understanding, or generating.

- **The Finite Dictionary:** A model cannot process a symbol, letter, or word that does not exist in its vocabulary. The vocabulary size is permanently fixed during initial architecture design (for example, Llama 2 has a vocabulary of 32,000 tokens, while GPT-4 has around 100,000).
- **The Building Blocks:** This master list contains every valid unit the tokenizer is allowed to use, including full words ("apple"), subword fragments ("ing", "pre"), individual characters, numbers, punctuation, and invisible control signals (like BOS and EOS tokens).
- **The Fallback Mechanism:** If an input contains an unusual word, a complex typo, or a new slang term, the model does not fail. Because its vocabulary includes individual characters and subwords, the tokenizer simply slices the unknown word down into smaller, recognizable pieces that _do_ exist in the master list.
- **The Memory Cost:** Vocabulary size is a direct optimization trade-off. Every single token in the vocabulary requires its own dedicated mathematical vector in the embedding matrix. Bloating the vocabulary size drastically expands the embedding matrix, increasing the model's overall VRAM requirements and computational footprint.
### Under the Hood: Tokenization Algorithms

How do tokenizers actually decide where to draw the boundaries? They do not rely on standard dictionaries; instead, they use statistical algorithms to find the most computationally efficient way to pack information. Here are the three primary methodologies you will encounter:

- **Byte Pair Encoding (BPE):** The most widespread algorithm, used heavily by OpenAI (GPT) and Meta (Llama). BPE works from the bottom up. It starts by breaking all text into individual characters (bytes) and iteratively merges the most frequently occurring adjacent pairs into single tokens. This is why a common word like "apple" becomes one token, but a rare word like "synecdoche" is left fragmented into multiple subword tokens.
- **Unigram Tokenization:** This algorithm works in reverse, from the top down. It begins with a massive, over-populated vocabulary of words and subwords, and systematically trims away the statistically the least useful tokens until it reaches a strict target vocabulary size. It evaluates the probability of subword combinations, making it highly flexible and efficient for models that need to balance complex vocabularies.

> [!info] **SentencePiece**
> Developed by Google, this is a tokenization utility rather than a standalone base algorithm (it typically runs BPE or Unigram under the hood). Traditional tokenizers assume that spaces naturally separate words, which completely breaks down when processing languages like Chinese or Japanese that do not use spaces. SentencePiece solves this by treating the space itself as just another character (often represented visually as a `_`), allowing it to cleanly process raw text across any language family without requiring language-specific pre-processing.

### Special Tokens: The Control Signals

Beyond the visible text, tokenizers also inject invisible structural markers into the pipeline. These special tokens act as control signals, providing the underlying model with essential navigational metadata about the sequence it is processing.

- **The Starting Gun:** The Beginning of Sequence (BOS) token (often represented as `<s>` or `<|startoftext|>`) tells the model where the prompt actually starts. It initializes the model's internal state and signals that it should begin evaluating the context.
- **The Stop Sign:** The End of Sequence (EOS) token (like `</s>` or `<|endoftext|>`) is arguably the most critical control marker. Because an LLM's natural mathematical state is to predict the next token continuously, the EOS token acts as the designated stopping condition. When the model predicts this specific token, it breaks the iterative generation loop and finalizes your output.
- **The Boundary Lines:** Separator tokens establish rigid structure within the prompt. In modern chat-optimized models, specific formatting tokens (such as `<|im_start|>user` and `<|im_end|>`) strictly divide system instructions, human input, and the AI's previous replies. This structural mapping helps prevent context bleed and mitigates prompt injection attacks.
- **The Filler Material:** Because LLMs are designed to process data in parallel batches for efficiency, every sequence in a computing batch must be the exact same length. Padding tokens (`<pad>`) are essentially meaningless blank spaces appended to the end of shorter prompts to make them fit the uniform batch matrix. The model is mathematically instructed (via an attention mask) to completely ignore these filler tokens during processing.

## 2. Embedding Lookup

Once text has been tokenized, every integer in the input sequence must be converted into a dense vector representation. Neural networks cannot process raw strings or simple IDs; they require complex numbers.

To do this, the model uses an **Embedding Matrix**—a massive internal dictionary that stores exactly one unique mathematical vector for every possible token in the model's vocabulary.

- **What it does:** The lookup process reads the prompt's array of integers sequentially, retrieves the corresponding static vector from the Embedding Matrix for each ID, and outputs a sequence of vectors.
- **Why it matters:** This is the foundational layer where a model first begins to compute "meaning."
- **Mental model:** The Embedding Matrix is the model's master coordinate dictionary, and the lookup is the act of translating your specific prompt into those coordinates.

Caveats:
- **The Blank Slate & Backpropagation:** When a model begins pre-training, its embedding vectors are completely randomized. It has no concept of grammar or definitions. As it processes trillions of tokens, it plays a continuous game of next-word prediction. Every incorrect guess triggers a mathematical adjustment (backpropagation). Because words with similar meanings tend to appear in similar contexts, these adjustments naturally pull related tokens closer together over time.
- **The Dimensional Space & Latent Features:** Models map tokens across hundreds or thousands of dimensions. These dimensions are not explicitly labeled by humans (e.g., there is no specific dimension for "is_plural"); they are _latent_ statistical features. One dimension might loosely track gender, another formality, allowing the model to represent incredibly nuanced concepts mathematically.
- **Semantic Proximity:** After billions of adjustments, the vector space self-organizes so that human language translates perfectly into spatial geometry. The vector distance between "dog" and "puppy" is significantly shorter than "dog" and "calculator." This spatial relationship allows models to perform mathematical operations on language (e.g., `King - Man + Woman ≈ Queen` or mapping the parallel distance between "Paris/France" and "Tokyo/Japan").
- **The Static Dictionary:** It is critical to understand that at this specific stage in the pipeline, the embedding lookup is completely context-free. It is a static 1:1 retrieval. The token for the word "bank" receives the exact same initial vector array whether your prompt says "sitting by the river bank" or "logging into my bank account."
	- **The Pipeline Handoff:** Because this initial lookup only captures the isolated definition of a token, it is insufficient for true language comprehension. To resolve ambiguities (like the "bank" example), these static vectors must be passed to the next stages of the pipeline to receive positional awareness and contextual weighting.
- **The RAG Distinction:** Do not conflate the LLM's internal embedding layer with the external vector embeddings used in Retrieval-Augmented Generation (RAG). Internal pipeline embeddings map _single, isolated tokens_ as raw material for the LLM. External [RAG embeddings](../RAG/02%20Vector%20Databases%20%26%20Embeddings.md) (like OpenAI's `text-embedding-3-small`) map _entire chunks of text_ to compress complex meaning into a single vector, optimized specifically for similarity search in a database.

### **Weight Tying: The Symmetric Optimization** 

In many LLM architectures, the input embedding matrix (which translates token IDs into vectors at the start of the pipeline) and the output projection matrix (which translates the final processed vectors back into token probabilities at the end) are actually the exact same set of weights.

- **The Symmetrical Logic:** Intuitively, the mathematical transformation from a discrete word into an abstract concept should be the exact inverse of translating that abstract concept back into a word.
- **The Efficiency Gain:** Because the model's vocabulary is massive (often containing 50,000 to 100,000+ tokens), the matrices required to map these dimensions consume a huge percentage of the model's parameters. By "tying" these weights together—using the same matrix for both input lookup and output generation—architects drastically reduce the overall memory footprint of the model, saving valuable VRAM while naturally preventing overfitting.

## 3. Positional Information

Because modern neural networks ingest data simultaneously rather than sequentially, the pipeline must mathematically inject an awareness of word order before deep processing begins. Positional information acts as a coordinate system, ensuring the model knows exactly where each token sits in the prompt sequence.

- **What it does:** Injects sequential and spatial awareness into the static token embeddings.    
- **Why it matters:** Without it, the model would process "The dog bit the man" and "The man bit the dog" as the exact same unordered bag of words.
- **Mental model:** If the [embedding lookup](#2.%20Embedding%20Lookup) provides the definition of the word, the positional embedding provides the timestamp of when that word was spoken.

- **The Parallel Processing Problem:** Older AI architectures (like RNNs) read text one word at a time, naturally building a sense of sequence. Modern Transformer models read all tokens simultaneously to maximize computing efficiency. Because this parallel ingestion strips away all inherent sequential order, architects must manually add position data back into the vector.
- **Absolute Positional Embeddings:** Early LLMs used a rigid, fixed coordinate system. Every slot in a sequence received a specific mathematical identifier (e.g., "This token is at absolute Slot 1," "This token is at absolute Slot 42"). These coordinates were often generated using complex sine and cosine waves. However, this absolute approach is brittle; if a model was only trained on 2,000 slots, it completely breaks down if you give it a prompt with 2,001 tokens because it lacks a mathematical coordinate for that new slot.
- **Relative Position Schemes:** Modern frontier models use a fluid approach. Instead of assigning a fixed absolute slot, the model calculates the distance between tokens (e.g., "Token X is exactly 4 steps away from Token Y").
	- Techniques like **Rotary Positional Embeddings (RoPE)** or ALiBi rotate the vector mathematically based on its position. This allows the model to understand the relationship between words based purely on their distance from one another, rather than a rigid grid.
	- **The Long-Context Key:** Relative positioning is the secret to massive context windows (like Claude's 200K or Gemini's 1M+ token limits). Because relative schemes (like RoPE) rely on calculating angles and distances rather than fixed slots, engineers can mathematically "stretch" or interpolate these distances. This allows a model trained on shorter texts to successfully process massive documents it was never originally sized for.
- **The Vector Merger:** To complete this pipeline step, the static semantic vector (from the Embedding Lookup) and the spatial coordinate vector (the Positional Information) are fused together—typically added element-wise. This creates a unified vector that tells the downstream Transformer layers both _what_ the token means and _where_ it belongs.

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
