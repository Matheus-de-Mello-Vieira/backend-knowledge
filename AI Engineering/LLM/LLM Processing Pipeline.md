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

- **The Query, Key, and Value (QKV) Framework:** To calculate attention, the pipeline mathematically splits each token's vector into three distinct, learned vectors:
    - **The Query (What I want):** The token asking for information (e.g., the word "bank" asking "what kind of bank am I?").
    - **The Key (What I have):** The token broadcasting its identity (e.g., the word "river" broadcasting "I relate to nature and water").
    - **The Value (What I contribute):** The actual mathematical substance the token will pass along if a match is made.
- **Attention Scores & Softmax:** The model calculates relevance by multiplying a token's Query against every other token's Key in the sequence (a dot product). A high score means the words are highly relevant to each other. These raw scores are then passed through a **Softmax** function, which normalizes them into percentages that add up to 100%. This dictates exactly how much of each Value vector should be blended into the Query token to update its meaning.
    - **The Softmax Function** takes a vector of raw, unnormalized scores (called logits) and transforms them into a probability distribution. It does this by exponentiating each score—making them all positive—and then dividing each by the sum of all the exponentiated scores. This ensures that every resulting value falls between $0$ and $1$, and that all the values across the vector sum up to exactly $1$ (or 100%), making it ideal for multi-class classification tasks in machine learning.
    - **The Quadratic Bottleneck ($O(N^2)$):** Because every single token's Query must be mathematically compared against every other token's Key in the sequence, the computational and memory complexity scales quadratically ($O(N^2)$). Doubling the sequence length does not double the workload—it quadruples it. This fundamental architectural trait is what dictates the strict context window limits of modern LLMs.
- **Multi-Head Attention (MHA):** Instead of calculating one single set of relationships, the model runs this QKV process simultaneously across multiple independent "heads." One head might focus on grammatical structure (e.g., matching verbs to nouns), while another focuses on sentiment. Modern architectures (like Llama 3) optimize this further using **Grouped-Query Attention (GQA)**, which shares Keys and Values across multiple Query heads to drastically reduce VRAM usage during generation.
- **Causal Masking (The One-Way Mirror):** Because Generative AI models are auto-regressive (they predict the future based strictly on the past), the attention mechanism must be tightly regulated. A mathematical "causal mask" is applied to block out all future tokens. Token #4 is allowed to query Tokens 1, 2, and 3 to build its context, but its attention scores for Token 5 and beyond are forced to zero
### Feed-Forward Networks

After attention mixes information across tokens, feed-forward layers transform each token representation independently.

- **The MLP Block:** Once self-attention has allowed a token to absorb context from the rest of the sentence, the updated vector is passed into a Multi-Layer Perceptron (MLP) block. While attention is about _routing_ information between different words, the feed-forward layer is where the model actually _processes and refines_ that information individually for each token.
- **Non-Linear Activations (SwiGLU):** Neural networks require non-linear mathematical functions to understand complex, abstract patterns rather than just straight lines. While older architectures used simpler functions like ReLU or GELU, modern frontier models predominantly use **SwiGLU**. This gated activation function acts like a smart valve—one branch decides _what_ information is useful, while the other carries the actual data—making the network significantly more expressive without bloating compute costs.
- **Residual Connections:** Deep neural networks suffer from signal degradation, where the original meaning gets lost as it passes through dozens of attention and MLP blocks. To prevent this, the pipeline uses residual (or "skip") connections. It takes the original vector from _before_ a block and simply adds it to the newly processed vector _after_ the block. This ensures the core identity of the token is preserved as it travels deeper into the network.
- **Pre-Normalization (RMSNorm):** To keep the massive arrays of numbers mathematically stable (preventing them from exploding into infinity or shrinking to zero), the vectors are normalized before entering each layer. Modern models replace standard Layer Normalization with **RMSNorm** (Root Mean Square Normalization). By dropping the computationally expensive step of mean-centering the data, RMSNorm provides a massive speedup across billions of calculations without sacrificing stability.

## 5. Logits and Next-Token Prediction

After the final transformer layer, the model produces a score for every possible token in its vocabulary.

- **What it does:** Converts the final hidden state into logits over the vocabulary.
- **Why it matters:** These logits represent the model's raw preferences before sampling or selection.
- **Mental model:** The model is not choosing a word yet; it is assigning a score to every possible next token before decoding narrows the field.

- **Vocabulary-Wide Scoring (The Raw Logits):** Once the deep Transformer layers have fully contextualized the input, the final vector is projected back into the vocabulary space using the output projection matrix. This generates a massive array of raw mathematical scores called **logits**. There is exactly one logit for every single token in the model's master vocabulary. If the vocabulary has 100,000 tokens, the model calculates 100,000 logits simultaneously.
- **Softmax Probabilities:** Because raw logits are unnormalized real numbers (they can be arbitrarily large positive or negative values), they are difficult to interpret or sample from directly. The pipeline passes this array through a **Softmax function**, which transforms the raw logits into a proper probability distribution. The values are squashed into percentages between 0 and 1 that add up to exactly 100%. At this precise moment, the model is mathematically stating: _"Based on the context, there is an 88% chance the next token is 'X', a 5% chance it is 'Y', etc."_

### Stochastic Sampling

If the pipeline simply selected the #1 highest-probability token at every step (a process called **Greedy Decoding**), the output would become highly repetitive, robotic, and prone to infinite loops. To achieve fluent, natural language, the system instead uses **Stochastic Sampling**.

Rather than picking the absolute winner, the model treats the softmax distribution like a weighted die. If a token is assigned a 15% probability, it has exactly a 15% chance of being randomly drawn. This allows the model to take different linguistic paths on the exact same prompt.

To control this randomness and prevent the model from occasionally drawing a nonsensical token from the extreme low end of the distribution, engineers apply modifiers to reshape or constrain the probabilities _before_ the die is rolled:

- **Penalty Parameters:** Before considering randomness, the system looks backward at the already generated text. To prevent infinite loops (eg.: `the the the the...`), it artificially lowers the raw logit scores of previously used tokens. Logit penalties generally fall into two distinct architectural standards depending on whether you are using commercial APIs or traditional open-source libraries.
	- **The Commercial Standard (Additive Subtraction):** Popularized by OpenAI and adopted by modern inference engines (vLLM, llama.cpp). It treats token suppression as a first-order linear equation: $\text{Total Penalty} = \alpha x + \beta$ (subtracted from the raw logit, where $x$ is the token count).
	    - **Frequency Penalty ($\alpha$):** The linear coefficient. Every single time a token is repeated, its logit score is reduced by an additional fixed increment, making it highly effective at breaking compounding loops.
	    - **Presence Penalty ($\beta$):** The constant coefficient. A flat, one-time "cover charge" applied to a logit the exact moment a token appears at least once, explicitly forcing the model to pivot to entirely new concepts.
	- **The Open-Source Standard (Multiplicative Scaling):** Standardized by Hugging Face via the single `repetition_penalty` parameter ($\theta$). Instead of subtracting a fixed value, it scales the raw logits via division or multiplication depending on their initial sign. Positive logits ($z_i > 0$) are divided ($z_i / \theta$), while negative logits ($z_i < 0$) are multiplied ($z_i \cdot \theta$).
		- **The Intent Behind the Split:** The fundamental goal of a penalty is to mathematically lower a token's raw score. If a logit is positive (e.g., **10**) and the penalty scalar is **1.2**, dividing it ($10 / 1.2 \approx 8.33$) successfully reduces the score. However, if a logit is negative (e.g., **-10**), dividing it would yield **-8.33**—a mathematically _higher_ number that would accidentally reward the token. By switching to multiplication for negative numbers ($-10 \cdot 1.2 = -12$), the formula ensures the score is driven further down the number line, successfully penalizing the token regardless of its starting sign.
		- **The Mathematical Flaw (Asymmetrical Distortion):** The Softmax function calculates probabilities based strictly on the _distance_ between logits, not their absolute values (e.g., a gap of **2** means the same thing whether the logits are **10** and **8**, or **-4** and **-6**). By using zero as an arbitrary pivot point, multiplicative scaling destroys this shift invariance.
		- **The Zero-Point Trap:** If a model's native logits are heavily positive, division _shrinks_ the gap between them, accidentally acting like a high Temperature (flattening the distribution and injecting randomness). If the logits are heavily negative, multiplication _expands_ the gap, acting like a low Temperature (sharpening the distribution and forcing determinism). Because different LLM architectures naturally output logits at entirely different numerical scales, this method is highly unpredictable in production.
	- **The Production Reality:** While historically divided, modern production inference frameworks have largely converged. Engines like vLLM, TGI, and llama.cpp now accept both OpenAI-style additive parameters and Hugging Face-style multiplicative parameters natively to maximize developer flexibility.
- **Temperature:** A mathematical divisor ($T$) applied to every raw logit before the softmax function ($z_i/T$). Because it literally divides the raw scores, a high temperature (e.g., **1.5**) shrinks the gap between high and low logits, flattening the distribution to inject more randomness into the final draw. Conversely, a low temperature (e.g., **0.1**) divides the logits by a small fraction—exponentially expanding the gap between scores, sharpening the distribution, and forcing the draw to be highly deterministic.
	- **The Zero-Temperature Override:** Mathematically, setting $T = 0$ would cause a division-by-zero error. In practice, APIs treat `temperature = 0` as a system override. It completely bypasses the Softmax sampling pipeline and triggers **Greedy Decoding** (an `argmax` function that strictly selects the single highest-scoring token). _Note: Due to floating-point rounding variations on GPU hardware, even `temperature = 0` does not guarantee 100% strict determinism across multiple runs._
- **Top-K (The Hard Cutoff):** The system sorts the temperature-scaled logits and keeps only the top _K_ highest scores. The logits of all other tokens are overwritten to negative infinity ($-\infty$).
- **Top-P / Nucleus Sampling (The Dynamic Cutoff):** The system calculates the cumulative probability of the remaining valid tokens. Once that cumulative sum hits the _P_ threshold (e.g., **0.90**), any remaining tokens outside that "nucleus" are also overwritten to $-\infty$.
- **The Final Softmax:** The system passes this masked logit array through the Softmax function. Because $e^{-\infty} = 0$, all filtered tokens receive exactly 0% probability, and the Softmax math perfectly normalizes the surviving tokens so their probabilities equal exactly 100% for the final weighted draw.

### Calibration and Confidence Limitations

It is a dangerous engineering mistake to equate high token probability with factual accuracy. A model will happily assign a 99% probability to a heavily hallucinated claim simply because that token fits the grammatical and contextual pattern of the sentence perfectly.

- **The Post-Training Penalty:** While foundational base models are generally well-calibrated, modern models heavily aligned via [RLHF](#The%20Training%20Pipeline) (Reinforcement Learning from Human Feedback) are notoriously overconfident. They are trained to sound authoritative, which skews their logits upward even when they are factually incorrect. 
- **The Calibration Gap:** In a perfectly calibrated system, outputs assigned 90% confidence should be factually correct exactly 90% of the time. In reality, LLMs suffer from a severe "hard-easy effect"—remaining stubbornly confident on highly complex tasks they fail at, while sometimes showing underconfidence on trivial ones.
- **The Engineering Reality:** Because raw token probabilities are an unreliable proxy for epistemic uncertainty (whether the model genuinely "knows" the answer), production pipelines often require secondary validation tools. This includes temperature scaling (recalibrating logits downward) or implementing probe classifiers that evaluate the model's hidden states rather than its raw output text.

## 6. Iterative Generation Loop

Generation is strictly autoregressive: the model cannot plan a full sentence in advance. It must append each newly produced token to the original prompt and restart the entire computational pipeline to predict the next one.

- **What it does:** Repeats the entire forward pass of the model sequentially until a definitive stopping condition is reached.
- **Stop conditions:** The loop terminates when the model predicts the End-of-Sequence (EOS) token, hits a hardcoded `max_tokens` limit, triggers a predefined application-level stop sequence, or initiates a tool/function call.
- **Key implication:** Errors compound. Because every generated token becomes permanent context for the next cycle, a single hallucinated or malformed token can force the model to mathematically double down on the mistake (often called the "hallucination snowball").
    

**The KV Cache (The Efficiency Engine):** Mathematically, self-attention requires comparing the Query vector of the newest token against the Key and Value vectors of _every single preceding token_. If a sequence is 10,000 tokens long, recalculating the Keys and Values for the first 9,999 tokens on every single generation step would be computationally disastrous. To solve this, engines use a **Key-Value (KV) Cache**. The system saves the computed Key and Value vectors of all past tokens in GPU memory. During the next loop, the model only computes the Query for the single new token, comparing it against the cached memory of the past. This turns an impossibly slow process into a rapid, scalable operation, though the KV cache size becomes the primary bottleneck for memory consumption in long-context tasks.

**Streaming Output & Detokenization:** Because the loop generates exactly one token at a time, applications do not have to wait for the entire response to finish before showing it to the user. As each integer ID is selected, it is passed backward through the tokenizer (detokenization) to retrieve the text fragment (e.g., `"apple"`). This fragment is instantly streamed to the client via [Server-Sent Events (SSE)](01%20Communication%20Patterns.md#Server-Sent%20Events) or [WebSockets](08%20WebSockets.md#Web%20Sockets). This architectural trait is why optimizing for **Time to First Token (TTFT)** is a critical metric in AI engineering.

**Response Truncation:** Truncation occurs when the generation loop is artificially severed before the model predicts an EOS token. This usually happens when the pipeline hits the `max_tokens` parameter set in the API request, or when the total sequence length (Prompt + Output) exceeds the model's absolute maximum context window limit. Truncated outputs often end mid-word or leave JSON objects unclosed, requiring application-layer logic to handle gracefully.

**Repetition Loops and Degeneration:** Because the loop relies heavily on self-attention, generative models are highly susceptible to repetition degeneration. If the model outputs the same token twice, that token receives a heavier attention weight in the context window. This mathematically increases the probability of the model outputting it a third time, creating a runaway feedback loop. If left unmitigated (via Temperature scaling or repetition penalty parameters), the model will devolve into infinite, nonsensical loops (e.g., `"the the the the the"`).
## Context Window Constraints

The entire pipeline operates within a finite token budget. Every single token submitted in the prompt, plus every token generated in the response, draws from this shared pool.

- **What it does:** Limits exactly how much prior text the model can mathematically attend to during inference.
- **Why it matters:** Once the sequence exceeds this hardcoded limit, the system cannot process further tokens without dropping, diluting, or truncating instructions.
- **See also:** [Context Engineering](Context%20Engineering.md), [RAG](01%20Fundamentals.md)
### The Hardware Bottleneck (The KV Cache Wall)

Because the core math of self-attention scales quadratically ($O(N^2)$), running long contexts requires massive amounts of VRAM. To keep the auto-regressive generation loop efficient, the system must save the computed Keys and Values for all past tokens (the KV Cache). As the context grows, this cache balloons exponentially. It quickly exceeds the physical memory limits of the GPU hardware, causing Out-Of-Memory (OOM) crashes long before the compute processors max out.

### Tradeoffs Between Long Context and Latency

Loading a massive prompt creates a severe bottleneck during the **Prefill Phase** (the time it takes the model to read the prompt before generating the first word).

- **Time To First Token (TTFT):** If you pass a 100,000-token document into the prompt, the model must execute the massive matrix multiplications across all 100k tokens simultaneously to build the initial context. This causes TTFT to spike from milliseconds to tens of seconds.
- **Throughput Degradation:** Because long contexts occupy massive amounts of VRAM for the KV Cache, the inference server cannot run as many concurrent user requests in parallel (a lower batch size). Processing massive context for one user mathematically degrades the speed and throughput for everyone else on the server.
### The "Lost-in-the-Middle" Effect

Even if the hardware successfully processes a massive context window, the model's architectural recall degrades. Studies reveal that LLMs exhibit a sharp "U-shaped" performance curve when retrieving facts from long prompts.

- **Primacy Effect:** The model near-perfectly remembers the very beginning of the prompt (where foundational system instructions usually live).
- **Recency Effect:** The model near-perfectly remembers the very end of the prompt (the most recent tokens directly preceding generation).
- **Attention Dilution:** Facts buried deep in the middle of a massive context window are routinely skipped over or hallucinated. Because attention scores are normalized via the Softmax function (they must sum exactly to 100%), spreading attention across 100,000 tokens dilutes the mathematical weight of any single middle token to near-zero, making it functionally invisible.
### Handling the Overflow (Cutoffs vs. Eviction)

When an application exceeds the maximum context limit, systems handle the overflow in distinct ways:

- **Hard Truncation (Standard):** The API simply throws a token limit error, or the model strictly stops generating mid-sentence once the absolute ceiling is hit.
- **Sliding Window Attention (SWA):** To simulate infinite context without blowing up VRAM, some architectures use a First-In, First-Out (FIFO) buffer. As new tokens are generated, the oldest tokens are mathematically pushed out of the attention window to maintain a fixed compute cost.
- **The Engineering Trap:** Sliding windows inherently destroy the earliest context. If your core system instructions (e.g., _"You must strictly output in JSON"_) are at the beginning of the prompt, a sliding window will eventually push them out of the memory cache, causing the model to abruptly break character mid-generation. Production systems must implement **System Prompt Pinning** (or "Attention Sinks") to permanently anchor those foundational tokens so they are never evicted.

## Inference vs. Training 

This entire document has focused on **inference**, which is fundamentally different from training. Understanding this strict boundary is critical for diagnosing why an AI system fails at a specific task.

- **Inference (The Forward Pass):** The model's neural network is completely frozen. It pushes the user's input through the layers mathematically to calculate probabilities and generate tokens.
- **Training (The Backward Pass):** The model actively updates its billions of mathematical weights (via backpropagation) by minimizing prediction errors across massive datasets.

> **Rule of Thumb:** During inference, the model is completely read-only. It is not "learning" new facts into its parameters from your prompt. It is simply applying its previously frozen weights to mathematically route your current context.

### The Training Pipeline

To understand why models behave the way they do during inference, engineers must understand the three distinct phases of how those frozen weights were originally configured:

- **1. Pretraining (The Knowledge Engine):** The model is fed trillions of tokens from the internet and trained on a simple self-supervised objective: predict the next word. It learns grammar, facts, coding logic, and reasoning natively. However, a raw pretrained model is a document completer, not an assistant. If you prompt it with _"What is the capital of France?"_, it might output _"What is the capital of Germany?"_ because it assumes it is completing a quiz worksheet.
- **2. Supervised Fine-Tuning (SFT):** The model is trained on tens of thousands of high-quality, human-written Q&A pairs. This teaches the model the **dialogue format**. It learns that it should stop acting like a raw text completer and start acting like an agent that directly answers instructions.
- **3. RLHF (Post-Training Alignment):** Reinforcement Learning from Human Feedback. The model generates multiple answers to a prompt, humans (or other AI models) rank them, and an algorithm mathematically penalizes toxic, unhelpful, or poorly formatted responses. This bakes in the final "tone," safety guardrails, and refusal behaviors.

### In-Context Learning

If the weights are completely frozen during inference, how can you paste a brand-new, undocumented API schema into the prompt and have the model instantly write perfect code for it?

This is the mechanical magic of **In-Context Learning**. You are not altering the model's long-term memory; you are leveraging its short-term memory.

- **Parameters (Long-Term Memory):** The frozen weights act as the _rules engine_ for language, logic, and reasoning.
- **Context Window (Short-Term Memory):** The prompt acts as the temporary _variable storage_ for the current task.

Because the Self-Attention mechanism is incredibly powerful, the model doesn't need to "learn" the new API into its permanent weights. Instead, the frozen attention heads dynamically read the new syntax rules provided in the prompt, calculate the relationships on the fly, and apply their generalized reasoning capabilities to generate a novel response. The moment the generation loop ends and the context window is cleared, the model completely forgets the API ever existed.
## Where Adjacent Systems Fit

Several common LLM system components are *outside* the core processing pipeline but influence its inputs and outputs.

- [**Prompt Engineering**](Prompt%20Engineering.md): Shapes the instruction payload before tokenization.
- [**Context Engineering**](Context%20Engineering.md): Controls what information enters the context window.
- [**RAG**](../RAG/01%20Fundamentals.md): Injects retrieved external information before or during generation.
- **Tool Calling:** Delegates precise actions outside the model's internal reasoning loop.

## Production Serving & Batching

When deploying models to production, the engineering focus shifts from the mathematical accuracy of a single prompt to the hardware utilization of the server.

### Multi-Tenant Batching

At its core, a GPU is a massive, highly parallel calculator designed to multiply giant grids of numbers (matrices) simultaneously.

- **The Single-User Waste:** If you send a single user's prompt to the GPU, the math required is so relatively small that it might only light up 5% of the GPU's compute cores. The other 95% of the processor sits completely idle, waiting for the operation to finish.
- **The Batching Solution:** Batching physically stacks multiple independent user requests (e.g., User A, User B, and User C) into a single, combined matrix. The GPU then pushes this giant composite matrix through the neural network's weights in a single forward pass. Because of the GPU's parallel architecture, it takes almost the exact same amount of time to calculate the next token for 10 stacked users as it does to calculate it for 1 user. This maximizes throughput and drastically reduces the cost-per-token.
    
### The Latency vs. Throughput Tradeoff

In production inference, every architectural decision is a tug-of-war between two opposing forces:

- **Throughput (The Server's Goal):** How many total tokens the system can generate per second across all users. High throughput requires massive batch sizes.
- **Latency (The User's Goal):** How fast an individual user receives their response.
    - **TTFT (Time To First Token):** The time it takes to process the initial prompt (the prefill phase) and stream the very first word.
    - **TPOT (Time Per Output Token):** The speed at which subsequent words stream onto the screen. Pushing the batch size too high maximizes throughput but crushes TPOT, resulting in a sluggish, stuttering experience for the end user.

### Static Batching vs. Continuous Batching

Historically, batching LLM requests was highly inefficient because generation tasks are entirely unpredictable in length. User A might ask for a 5-word sentence, while User B asks for a 500-word essay.

- **Static Batching (The Old Standard):** The server groups 10 requests together and starts generating. Because the GPU must execute the matrix math uniformly, the entire batch is held hostage by the longest request. Even if 9 users finish their answers in 2 seconds, their GPU slots sit entirely idle and wasted while waiting for User B's 500-word essay to finish.
- **Continuous Batching / In-Flight Batching (The Modern Standard):** Implemented by modern engines like vLLM and TGI. Instead of waiting for a full batch to finish, the scheduler operates at the _token level_. The exact millisecond User A's short request finishes and emits an End-of-Sequence (EOS) token, the server immediately evicts User A from the batch and dynamically pulls User C's new request into that empty slot on the very next generation loop. This massively increases hardware utilization.

### PagedAttention

Even with Continuous Batching, production servers hit a massive memory wall. Because the exact length of a user's generated response is unknown, traditional systems had to pre-allocate massive, contiguous blocks of VRAM for each user's KV Cache just in case they generated a long response. This led to massive memory fragmentation (wasting up to 60% of available VRAM).
- **The Solution:** Inspired by [how operating systems manage RAM](03%20Memory%20Management.md), engines like vLLM use **PagedAttention**. It chops the KV Cache into small, fixed-size blocks (pages). The system dynamically allocates new memory pages on the fly only as the model actually generates new tokens. This entirely eliminates fragmentation, allowing the server to squeeze significantly more concurrent users into the same GPU.

### Security & Privacy

- **The Core Risk (Memory Leakage):** If a bug exists in the continuous batching scheduler, the pointers managing the KV Cache could theoretically cross wires. This would cause the attention mechanism to accidentally pull the Value vectors from User A's prompt to generate the next word for User B, leaking sensitive context.
- **The Mathematical Defense (Block-Diagonal Masking):** To prevent tokens from bleeding across users during the giant matrix multiplication, the engine applies a strict multi-tenant Attention Mask. Mathematically, it creates a block-diagonal matrix where the attention scores between User A's tokens and User B's tokens are forcefully overwritten to negative infinity ($-\infty$). After passing through the Softmax function, their influence on each other drops to exactly 0%. While they are processed by the same hardware simultaneously, they are mathematically walled off.
- **The Architectural Defense (Pointer Isolation):** Systems like PagedAttention do not just optimize memory; they isolate it. Much like how a modern Operating System prevents your web browser from reading the RAM allocated to your password manager, PagedAttention uses virtual memory mapping. User B's generation loop only possesses the virtual pointers to their specific blocks of VRAM. It is structurally impossible for the model to attend to User A's memory blocks because User B's isolated process does not have the system address to reach them.
- **The Side-Channel Vulnerability:** While direct memory leakage is prevented mathematically, batching does introduce theoretical timing vulnerabilities. Because User A and User B share the same physical GPU compute cycles, a highly sophisticated, malicious User B could measure the exact millisecond delays in their token generation (TPOT) to infer the sequence length or computational density of User A's hidden prompt.
- **The Enterprise Solution (Dedicated Instances):** Because shared batching always carries theoretical multi-tenant risks, high-security sectors (banking, healthcare, government) often bypass public APIs entirely. They pay cloud providers for **Dedicated Endpoints** or **Provisioned Throughput**. In these setups, the server still uses batching to remain efficient, but it strictly batches the internal requests of that _single_ enterprise client. No external user ever touches the physical GPU.

## Transformer Architectures

To deeply understand these architectures, we have to look back at the original 2017 Google paper (_Attention Is All You Need_). The original Transformer was built with two distinct halves: an Encoder to read text, and a Decoder to write text. Over the last few years, the AI industry realized you do not always need both halves, and the architecture splintered into three evolutionary paths based strictly on how the **Attention Mask** is applied.

- **What it does:** Compares the three main Transformer architecture families by how they apply attention and how that choice affects capabilities.
- **Why it matters:** The attention-mask design determines whether a model is best suited for understanding, generation, or sequence-to-sequence transformation.
- **Mental model:** The same core Transformer machinery can behave like a reader, a writer, or a translator depending on which parts of the architecture are kept and how attention is constrained.

### Encoder-Only (The Readers / Understanders)

In an Encoder-only model, the causal mask (the mechanism that hides future tokens) is completely removed. Every token in the sequence calculates its attention score against every other token simultaneously—past, present, and future. If you feed it the sentence "The bank of the river," the word "bank" looks ahead at the word "river" to immediately understand its own context.

- **Famous models:** BERT, RoBERTa.
- **The math:** Unmasked / bi-directional attention.
- **Strengths:** Because it has total visibility of the entire sequence at once, it achieves state-of-the-art deep contextual understanding.
- **Weaknesses:** It is mathematically incapable of generating text. Because it expects to see the whole sentence at once, it cannot iteratively predict a "next" word.
- **Primary use cases:** Text classification, sentiment analysis, named entity recognition, and search engine ranking (embedding generation).

### Decoder-Only (The Writers / Generators)

This is the architecture that powers the entire modern Generative AI boom. In a Decoder-only model, a strict "Lower Triangular Mask" is applied to the attention matrix. The attention scores for any future tokens are overwritten to negative infinity ($-\infty$). Token #4 is mathematically barred from looking at Token #5.

- **Famous models:** GPT-4, Llama 3, Mistral, Claude.
- **The math:** Strict causal masking / auto-regressive attention.
- **Strengths:** It is the ultimate engine for generation. By forcing the model to strictly predict the future based only on the past, it becomes exceptionally skilled at fluent, open-ended text creation, coding, and reasoning.
- **Weaknesses:** Because it reads prompts strictly left-to-right, the early tokens in a prompt cannot look ahead to see the end of the prompt. This is why [Chain of Thought Prompting](Prompt%20Engineering.md#Chain%20of%20Thought%20Prompting) is required for complex logic. You have to force the model to generate its own scratchpad text so it can "see" its own logic as past tokens. 
- **Primary use cases:** Chatbots, code generation, creative writing, and general-purpose reasoning agents.

### Encoder-Decoder (The Translators)

This architecture combines both halves to solve complex transformation tasks. It operates in two distinct phases:

- **Famous models:** T5, BART, the original 2017 Transformer.
- **The math:** Bi-directional attention + causal attention + cross-attention.
- **The encoder phase:** The input prompt is passed into the Encoder, which uses unmasked bi-directional attention to read the entire text at once and compress it into a dense mathematical representation.
- **The decoder phase:** The Decoder begins generating the output one token at a time using strict causal masking. However, it introduces a new mechanism called **Cross-Attention**. While generating, the Decoder's _Query_ vectors do not just look at their own past tokens; they also query the _Key_ and _Value_ vectors generated by the Encoder.
- **Strengths:** Unmatched at sequence-to-sequence tasks where the output heavily depends on a holistic understanding of the input.
- **Weaknesses:** Computationally heavy and complex. You are essentially running two separate neural networks in tandem.
- **Primary use cases:** Language translation (e.g., English to French), document summarization, and audio transcription (e.g., Whisper, which encodes audio and decodes text).
- **The Industry Consensus:** While Encoder-Decoder architectures are elegant, the industry realized around 2020 that if you simply scale up a Decoder-only model with enough parameters and training data, it becomes incredibly proficient at translation and summarization anyway. This is why almost all modern frontier models (OpenAI, Anthropic, Meta) have abandoned the Encoder and are strictly **Decoder-only**.

## Multi-Turn Conversations & Tool Calling

The jump from a single text completion to a dynamic, multi-turn AI agent is entirely an engineering trick. At the neural network level, a language model is entirely stateless and does not possess an ongoing internal memory. Once the generation loop finishes outputting a response, the context window is wiped clean. To create a continuous conversation, the system relies on the host application to maintain a rolling transcript.

### The Append-Only Transcript

- **The Brute Force Loop:** When a user sends a third message in a chat, the application does not just send that single sentence. It takes the System Prompt, the user's first message, the AI's first reply, the user's second message, the AI's second reply, and the new third message, concatenates them into one massive string, and submits the entire transcript back to the API from scratch.
- **Chat Formatting Tokens:** To prevent the model from confusing its own past words with the user's instructions, the raw text is wrapped in specialized, invisible control tokens during training and inference (e.g., `<|im_start|>user`, `<|im_start|>assistant`). This acts as a rigid script, mathematically teaching the model exactly which lines it "spoke" and which lines it needs to respond to.
### Prefix Caching

- **The Recompute Problem:** Because the entire transcript is submitted every single turn, the $O(N^2)$ Self-Attention matrix grows rapidly. Recomputing the dense math for the entire history on every single turn would crush server latency and waste immense compute.
- **Prefix Caching:** Modern inference servers use **Prefix Caching** to solve this. The server recognizes that the first 2,000 tokens of a new prompt are perfectly identical to the prompt submitted moments prior. It retrieves the already-computed Key and Value vectors for those 2,000 tokens directly from VRAM. The GPU only has to execute the heavy math for the newest sentence, seamlessly picking up exactly where it left off.

### Tool Calling

- **The Orchestration Boundary:** The model itself cannot execute code, query a database, or search the web. It is mathematically confined to predicting the next token. Tool calling is an orchestration handshake between the model and the host application.
- **The Syntax Trigger:** During the System Prompt phase, the host application provides a list of available tools formatted as JSON schemas. If the model determines a tool is needed, it stops writing conversational text and instead generates a perfectly formatted JSON object matching the requested tool's schema.
- **The Halting Phase:** The inference server detects this specific JSON structure, immediately halts the generation loop, and passes the JSON payload back to the host application (e.g., a Python backend).
- **The Injection Phase:** The host application actually executes the API call or database query. It takes the raw data returned by that external tool, appends it to the rolling transcript under a new `<|im_start|>tool` role, and sends the entire massive prompt back to the LLM to read the data and summarize the final answer for the user.

## Mixture of Experts (MoE) Architecture

The **Mixture of Experts (MoE)** architecture is an engineering solution designed to decouple a model's knowledge capacity from its generation latency.

### The Problem: Compute Scaling and the Dense Bottleneck

In a neural network, a **parameter** is an individual learned mathematical value (a weight or a bias) that stores the model's understanding of language. When a model is labeled "70B," it means it contains 70 billion of these parameters.

However, in a standard **Dense** Transformer (such as Llama 3 70B), every single token in a prompt must be evaluated against 100% of these parameters. When processing a trivial token (like a comma), a dense model still executes matrix operations across massive layers dedicated to complex logic or coding. Because the inference compute cost (FLOPs per token) scales linearly, $O(P)$, with the parameter count, making a dense model mathematically smarter uniformly crushes its generation speed.
- **FLOPs** stands for **Floating-Point Operations**

### The Solution: Sparse Routing

MoE models solve this compute bottleneck by making the Feed-Forward Network (FFN) layers **sparse**. The Multi-Head Attention layers remain shared, but the FFN block is duplicated into multiple parallel "Experts."

- **The Router (Gating Network):** Placed directly before the FFN layer, a lightweight routing network analyzes the token's hidden state vector and computes a probability score across all available experts.
- **Top-$K$ Routing:** The router selects only the top-$K$ highest-scoring experts (typically $K=1$ or $K=2$) to process that specific token. The unselected experts remain completely uncomputed (zeroed out) for that cycle.
- **Mathematical Specialization:** Experts organize automatically during pre-training based on abstract statistical distribution patterns (e.g., one expert may naturally specialize in syntax structure, while another activates for numerical processing).

### Active vs. Total Parameters

This architecture splits the parameter metric into two distinct operational values, effectively solving the compute bottleneck:

- **Total Parameters (The Knowledge Base):** The combined parameter count of all experts. For example, Mixtral 8x7B has roughly **47B** total parameters.
- **Active Parameters (The Compute Cost):** Because the router only activates 2 experts per token, the actual mathematical operations executed during the forward pass only use **13B** active parameters. The model generates text at the blazing speed of a 13B model, while pulling from the vast intelligence of a 47B model.

## Quantization

Neural-network parameters are numerical values, and the **number format used to store those values determines how many bits each parameter occupies and how precisely it can represent numbers**.

A common representation is **floating point**, where the available bits are divided between the number's sign, exponent, and significant digits. Different floating-point formats make different trade-offs between memory usage, numerical range, and precision:

- **FP32 (32-bit Floating Point):** Uses 32 bits, or 4 bytes, per value. It provides high numerical precision but requires substantial memory and bandwidth.
- **FP16 (16-bit Floating Point):** Uses 16 bits, or 2 bytes, per value. It reduces memory usage and allows faster computation on hardware optimized for lower precision.
- **BF16 (Brain Floating Point 16):** Also uses 16 bits, but dedicates more of those bits to the exponent and fewer to numerical precision. This gives it approximately the same numerical range as FP32 while retaining the 2-byte storage cost of FP16.
    

These formats illustrate an important hardware trade-off: **more bits preserve more numerical information, but they also consume more memory and require more data to move through the GPU's memory system.**

Quantization pushes this trade-off further by representing model weights and, in some cases, activations using even lower-precision formats such as INT8, INT4, FP8, or FP4.

### The Problem: The VRAM and Memory-Bandwidth Wall

Model parameters must be stored in [VRAM](GPU.md#Global%20Memory%20/%20VRAM) while the model is running. Their numerical precision therefore directly affects the model's static memory footprint.

For example, a parameter stored in FP16 or BF16 occupies 16 bits, or 2 bytes. A dense 70B-parameter model stored entirely at 16-bit precision therefore requires approximately:

$$  
70\text{B parameters} \times 2\text{ bytes} \approx 140\text{ GB}  
$$

This data must not only fit in VRAM; the weights also have to be read from memory while the GPU executes the model. Large models can therefore be constrained by both **VRAM capacity** and **memory bandwidth**.

During inference, the model's weights are frozen, which makes it possible to represent many of them using lower precision while preserving most of the model's behavior.

### Lower-Precision Representation

Quantization maps model values into a smaller numerical representation. Traditional approaches commonly use integer formats such as INT8 or INT4, while modern hardware also supports low-precision floating-point formats such as FP8 and FP4.

- **INT8:** Uses 8 bits per quantized value, roughly halving the raw storage required compared with FP16/BF16.
- **INT4:** Uses 4 bits per quantized value, reducing raw storage to roughly one quarter of FP16/BF16.
- **FP8 / FP4:** Low-precision floating-point formats that retain a floating-point representation while using fewer bits.

For example, ignoring additional metadata such as scaling factors, the raw weight storage of a 70B model falls from roughly **140 GB at 16-bit precision** to approximately **70 GB at 8-bit precision** or **35 GB at 4-bit precision**.

The exact computation performed by the GPU depends on the quantization method. Some approaches perform matrix operations directly using low-precision arithmetic supported by the hardware, while others store weights in a compressed format and convert them to a higher-precision representation during computation.

The important architectural effect is that **fewer bits per value reduce both the amount of VRAM required and the amount of data that must move through the GPU's memory system.**
### Quantization Methodologies

Applying naive quantization introduces rounding errors that can degrade the model's logic. To mitigate this, engineers use sophisticated compression frameworks:

- **Post-Training Quantization (PTQ):** Applied after the FP16 base model is fully trained. Frameworks like **AWQ** (Activation-Aware Weight Quantization) measure activation channels during a brief calibration run, identify the top 1% of the most critical weights, and protect them from aggressive quantization while compressing the remaining 99% down to 4-bit.
- **Quantization-Aware Training (QAT):** Simulates quantization errors during the actual training or fine-tuning process. This forces the network to adapt its parameters natively to compensate for precision loss, producing higher accuracy at ultra-low bit rates.
- **MoE Quantization Risks:** Quantizing MoE architectures requires extreme care. The lightweight Router relies on precise numerical differences to choose experts. If quantized too aggressively, rounding errors can flip routing decisions. Inference engines often apply **mixed-precision quantization**, keeping the sensitive Router at FP16 while compressing the heavy Expert blocks to INT4.