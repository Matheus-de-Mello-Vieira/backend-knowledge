# Advanced Techniques

## Query expansion

### **The Core Concept**

A retrieval enhancement technique that generates multiple **semantically related variants** of a user’s query before searching the vector database.

- **Goal:** Bridge the gap between how a user asks a question and how the data is actually written (solves "vocabulary mismatch").

- **The Shift:** Moves

  - from **$1 \rightarrow 1$** (Query to Retrieval)

    ```mermaid
    flowchart LR
        A[User Query] --> B[Embed Query]
        B --> C[Vector Search]
        C --> D[Top-k Documents]
        D --> E[LLM Generator]
        E --> F[Final Answer]
    ```

  - to **$1 \rightarrow N$** (Query to Multiple Retrievals).

    ```mermaid
    flowchart LR
        A[User Query] --> B[Query Expansion]
        B --> C1[Query Variant 1]
        B --> C2[Query Variant 2]
        B --> C3[Query Variant N]
    
        C1 --> D1[Vector Search]
        C2 --> D2[Vector Search]
        C3 --> D3[Vector Search]
    
        D1 --> E[Merge Results]
        D2 --> E
        D3 --> E
    
        E --> F[Rerank / Deduplicate]
        F --> G[LLM Generator]
        G --> H[Final Answer]
    ```

Query expansion acts as a **Recall** optimization strategy that uses increased **Semantic Coverage** to ensure that variations in terminology don't prevent the retrieval of relevant documents.

> **Note:** Since Query Expansion prioritizes **Recall** at the expense of **Precision**, a **Reranker** is essential in production to filter the resulting 'Noise' and protect the LLM from irrelevant context.

### **The Workflow**

1. **Input:** User provides a narrow or ambiguous query.
2. **Transformation:** An LLM generates a set of focused, search-oriented reformulations.
3. **Retrieval:** Each expanded query is embedded and searched independently.
4. **Post-Processing:** Results are merged, **deduplicated**, and usually **reranked** to filter out noise.
5. **Generation:** The cleaned context is passed to the generator.

## **Main Approaches to Query Expansion**

### **1. Synonym / Paraphrase Expansion**

This is the most direct way to increase **Semantic Coverage** by using an LLM to "rewrite" the intent.

* **Mechanism:** Generates alternative phrasings of the same intent to match different document vocabularies.
* **Target Metric:** Primarily used to boost **Recall** when the user's language is "narrow" compared to the knowledge base.

**Example Transformation:**

> **Original Query:** *"How to reduce latency in distributed systems?"*

| Expanded Variant | Strategic Goal |
| --- | --- |
| "Ways to minimize **response time** in distributed **architectures**" | Synonym replacement (Latency  Response Time). |
| "Improving **performance** of **microservices** communication" | Domain-specific context (Systems  Microservices). |
| "Lowering **network overhead** in distributed computing" | Technical sub-topic (Latency  Network Overhead). |

**Common Methods:**

* **LLM Rewriting:** A "Chain of Thought" prompt asking for 3-5 variations.
* **Thesaurus-based:** Using tools like WordNet (faster, but lacks context).
* **Controlled Rewriting:** Forcing the LLM to use specific domain terminology.

---

#### **The Trade-off Check**

* **The Gain:** Massive increase in **Semantic Coverage**; you'll catch documents that never mention the word "latency."
* **The Cost:** Higher **Token Usage** for the extra queries and a drop in **Precision** (as "performance" is a broader, noisier term than "latency").

> **Quick Tip:** If your **Recall** is low because users speak "casual" while docs are "technical," this is your best fix.

This approach is the "heavy lifter" of semantic coverage. While the first approach (Synonyms) focuses on **linguistic** variations, **Multi-Query Generation** focuses on **conceptual** variations.

---

## **2. Multi-Query Generation (LLM-driven)**

The system uses an LLM to "deconstruct" the user's intent into several distinct sub-queries from different perspectives.

* **Mechanism:** Instead of just changing words, it changes the **angle** of the search.
* **Target Metric:** Maximizes **Recall** by ensuring that even if the information is split across different documents, the system finds all pieces.

### **The "Perspective" Strategy**

If a user asks: *"Is it worth upgrading to a heat pump?"*
An LLM-driven Multi-Query approach might generate:

1. "Cost-benefit analysis of residential heat pumps 2024" (**Financial angle**)
2. "Energy efficiency ratings of heat pumps vs gas furnaces" (**Technical angle**)
3. "Common installation challenges for air-source heat pumps" (**Practical angle**)
4. "Government rebates and tax credits for heat pump installation" (**Regulatory angle**)

### **Pros vs. Cons (Technical Impact)**

* **Advantage (Recall):** Handles **Conceptual Expansion**. It can find documents that are conceptually relevant even if they don't share a single keyword with the original query.
* **Risk (Precision):** Highly likely to introduce **Noise**. One of those "perspectives" might be too broad, pulling in irrelevant data.
* **Risk (Efficiency):** Significant **Token Usage** and **Latency** increase because you are performing  separate vector searches and processing  sets of results.

### **Implementation Note**

This is the default logic behind tools like **LangChain’s `MultiQueryRetriever**`.

> **Critical Checklist:** If you use Multi-Query Generation, you **must** use a **Reranker**. Without it, your final prompt will likely be filled with "Low-Precision" noise from the different search angles, potentially hurting the **Faithfulness** of the final answer.

This is a sophisticated tactic because it intentionally moves *away* from specific details to capture the "first principles" of a topic.

---

## **3. Step-Back / Abstraction Expansion**

The system generates a higher-level, more generalized version of the query to capture foundational or conceptual context.

* **Mechanism:** It "steps back" from the specific technical question to ask about the broader category or principle.
* **Strategic Goal:** To retrieve **background information** or **foundational concepts** that help the LLM provide a more "grounded" and authoritative answer.

### **The Abstraction Logic**

If the specific "needle" is too hard to find, you retrieve the "haystack" to understand the environment.

**Example Transformation:**

> **Original Query:** *"How does vector quantization reduce memory usage in FAISS?"*

**The Step-Back Query:**

> *"Techniques for reducing memory usage in vector search systems"*

* **Why it works:** The documentation for FAISS might assume you already understand Vector Quantization. By stepping back, you retrieve the *definitions* of quantization, which gives the generator the "mental model" needed to explain the specific FAISS implementation.

### **Technical Impact**

* **Recall (Pro):** High. It ensures that the system doesn't miss the "big picture" documents that define terms and concepts.
* **Precision (Con):** Very Low. A step-back query is, by definition, less specific, meaning it will retrieve a lot of general info that might not be needed for a direct answer.
* **Token Usage (Con):** Requires an additional "step-back" generation call and adds more (potentially redundant) background text to the final context.

> **Note:** This is particularly effective for **Complex Reasoning** tasks. It provides the "contextual scaffolding" that prevents the LLM from getting lost in highly technical or granular details.

### 4. Hypothetical Document Expansion (HyDE)

Instead of transforming the user’s query into more queries, HyDE uses an LLM to generate a **hypothetical answer** (a "fake" document) and uses *that* for retrieval.

- **Mechanism:** It maps the **Query** $\rightarrow$ **Hypothetical Doc** $\rightarrow$ **Vector Space**.
- **The Logic:** In many embedding models, a "question" vector and an "answer" vector are quite far apart. However, a "fake answer" vector and a "real answer" vector should be very close.

### **The Workflow**

1. **Generate:** The LLM writes a brief, plausible response to the user's query (even if it's based on "hallucination").
2. **Embed:** That hypothetical response is converted into a vector.
3. **Retrieve:** The system looks for real documents that look like the hypothetical one.

### **Technical Impact**

- **Recall (Pro):** Very High for "Zero-Shot" scenarios. It provides a much richer set of keywords and technical context for the embedding model to latch onto.
- **Precision (Con):** Can be risky. If the LLM generates a completely wrong hypothetical answer (hallucination), it might lead the retriever into a completely irrelevant part of the vector database.
- **Latency/Token Usage (Con):** You are generating a full (albeit short) paragraph before even starting the retrieval process.

> **Note:** HyDE is a **Recall** powerhouse when you have a **Vocabulary Mismatch** (e.g., the user asks a casual question, but the documents are dense academic papers). The hypothetical answer "translates" the user's intent into the professional dialect of the corpus.

This final approach is the bridge between **Dense Retrieval** (semantic/vector-based) and **Sparse Retrieval** (keyword/BM25-based). It focuses on "textual overlap" rather than just conceptual meaning.

## 5. Keyword Expansion (Sparse Retrieval Context)

This technique targets **Sparse Retrieval** systems (like BM25) by explicitly adding technical tokens that might be missing from the original query.

- **Mechanism:** It expands a query with specific entities, definitions, and acronyms to ensure a literal text match.
- **Primary Use Case:** **Hybrid Search** systems where you combine vector search with traditional keyword search.

### **The Expansion Logic**

It "unpacks" the query to ensure the search engine hits specific, high-value tokens.

**Example Transformation:**

> **Original Query:** *"How to set up CI/CD?"*

**Keyword Expansion:**

> *"CI/CD **continuous integration continuous deployment DevOps pipeline automation**"*

- **Why it works:** A vector search might understand the *concept* of CI/CD, but a keyword search might miss a document that only uses the full term "Continuous Integration" without using the acronym.

### **Technical Impact**

- **Recall (Pro):** High for technical documentation, legal codes, or medical records where specific terminology and abbreviations are used inconsistently.
- **Precision (Con):** Lowered if the expansion adds generic terms (e.g., adding "Software" to every query), which can dilute the search results.
- **Complexity:** In a hybrid system, you have to manage two different sets of expanded queries (one for the vector engine and one for the keyword engine).

## **Pros vs. Cons**

In practice, Query Expansion represents a deliberate trade-off: you **sacrifice Precision and Latency** (accepting more noise and higher compute costs) in order to **maximize Recall**.

| **Aspect**       | **Impact** | **Technical Reality**                                        |
| ---------------- | ---------- | ------------------------------------------------------------ |
| **Recall**       | ⬆️ **Pro**  | More relevant documents are caught via higher semantic coverage. |
| **Precision**    | ⬇️ **Con**  | More irrelevant documents ("Noise") enter the context window. |
| **Latency**      | ⬇️ **Con**  | Multiple queries mean more LLM calls and more DB lookups.    |
| **Faithfulness** | ⚠️ **Risk** | Lower Precision can lead the LLM to hallucinate based on the "Noise." |
| **Token Usage**  | ⬇️ **Con**  | Higher costs from generating $N$ queries and passing a larger "candidate set" to the LLM. |

## When Query Expansion Is Most Useful

- Enterprise document search
- Legal / compliance systems
- Highly technical corpora
- Ambiguous user queries
- Short queries (1–5 words)

Less useful when:

- Queries are already long and detailed
- Corpus is small
- Retrieval is already high-recall



