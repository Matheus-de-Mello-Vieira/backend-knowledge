# Lexical Information Retrieval

**Lexical Information Retrieval** is the foundational strategy for search systems, relying on the statistical matching of exact keywords rather than "understanding" meaning. At its core, it treats a document as a "bag of words," analyzing the presence and frequency of specific tokens to determine relevance.

## Text Representation

Mathematically, a document is not a string of text, but a **vector** where each dimension corresponds to a specific word or feature from the entire vocabulary. To transform raw text into this mathematical object, we apply a pipeline of processing steps.

* In lexical search (Bag-of-Words/TF-IDF), the vector is **Sparse** and its dimensions are **Explicit Words**. In semantic search (Embeddings), the vector is **Dense** and its dimensions are **Abstract Features**.
  * In sparse vectors, the dimensionality is the vocabulary size. They are sparse because a single document normally contains only a tiny fraction of the total vocabulary, so most dimensions are zero. Additionally, each word is treated as independent, since they are geometrically orthogonal.
  * In semantic embeddings, the vectors have a fixed size, regardless of vocabulary size. They are dense because every dimension represents one abstract feature, so most of them are non-zero. Related words have a smaller angle than unrelated words.

### Tokenization

- **Definition:** The process of breaking a stream of text into individual units called **tokens**.
- **Granularity:**
  - **Word-level:** "Apple pie" $\rightarrow$ `["Apple", "pie"]` (Most common).
  - **Character-level:** "Apple" $\rightarrow$ `["A", "p", "p", "l", "e"]` (Used in some neural nets).
  - **Sub-word (BPE/WordPiece):** "Unhappiness" $\rightarrow$ `["Un", "happi", "ness"]` (Balances vocabulary size and meaning).
- **Challenges:** Handling punctuation, hyphens (e-mail vs email), and languages without spaces (Chinese, Japanese).

### Stop Words

- **Definition:** Extremely common words that carry little semantic meaning and are often filtered out to save space and reduce noise.
- **Examples:** "the", "is", "at", "which", "on".
- **Modern Context:** In traditional search (TF-IDF), removing them is critical. In modern semantic search (BERT/LLMs), they are kept because they provide crucial context (e.g., "flights **to** London" vs "flights **from** London").

### Stemming vs. Lemmatization

Both techniques aim to reduce inflectional forms (running, runs, ran) to a common base form, but they use different methods.

- **Stemming (The "Chop" Method):**
  - **Mechanism:** Heuristically chops off the ends of words based on rules.
  - **Speed:** Very fast.
  - **Accuracy:** Low. Can result in non-words (e.g., "ponies" $\rightarrow$ "poni").
  - **Example:** "Caring" $\rightarrow$ "Car".
- **Lemmatization (The "Dictionary" Method):**
  - **Mechanism:** Uses a vocabulary and morphological analysis to return the dictionary form (lemma).
  - **Speed:** Slower (requires lookups).
  - **Accuracy:** High. Always results in a valid word.
  - **Example:** "Caring" $\rightarrow$ "Care"; "Better" $\rightarrow$ "Good".

### Vocabulary

- **Definition:** The set of all unique tokens known to the system ($V$).
- **Dimensionality:** The size of the vocabulary ($|V|$) dictates the dimensionality of your document vectors.
- **Out-of-Vocabulary (OOV):** Words that appear in user queries but were not in the training data/corpus. Handling OOV is a major challenge in text representation.

### Bag-of-Words (BoW) Assumption

- **Definition:** A simplifying assumption that models a document solely by the **frequency of its words**, completely ignoring grammar and word order.
- **The Metaphor:** Imagine taking all the words in a document, writing them on slips of paper, and shaking them up in a bag.
- **Mathematical Implication:**
  - "The dog bit the man" is mathematically identical to "The man bit the dog."
  - Despite this massive loss of context, it remains surprisingly effective for topic classification and basic keyword search.

---

## Term statistics

Once we have valid tokens, we need to determine how "important" they are. In a simple count, the word "the" might appear 100 times, while "cryptography" appears once. If we treated them equally, our search results would be dominated by noise.

- **The Goal:** To mathematically distinguish between **noise** (common words) and **signal** (content words).
- **The Method:** We use statistical properties of the text—both within a single document and across the entire collection—to assign a specific "weight" to every term.
- **The Result:** These statistics are the raw ingredients used to calculate relevance scores in algorithms like TF-IDF and BM25.

### Term Frequency (TF)

- **Definition:** The number of times a term $t$ appears in a specific document $d$.
- **Intuition:** If a user searches for "encryption," and Document A mentions it 15 times while Document B mentions it once, Document A is likely more relevant.
- **The Assumption:** The more a term occurs in a document, the more representative it is of that document's content.
- **Raw Count vs. Normalization:**
  - *Raw Count:* Simple integer count (e.g., 5).
  - *Normalized:* Divided by document length to prevent long documents from having an unfair advantage just because they have more words.

### Document Frequency (DF)

- **Definition:** The number of documents in the entire collection (corpus) that contain the term $t$.
- **Scope:** Unlike TF (which is local to one document), DF is a **global statistic** across the whole dataset.
- **Intuition:**
  - "The" appears in 1,000,000 out of 1,000,000 documents. (High DF)
  - "Quantum" appears in 50 out of 1,000,000 documents. (Low DF)
- **The Problem:** High DF usually means the word is generic and carries little specific meaning (low discriminative power).

### Inverse Document Frequency (IDF)

- **Definition:** A weight indicating how rare (and thus informative) a term is. It is mathematically derived from DF.
- **The Formula:** $\text{IDF}(t) = \log(\frac{N}{\text{DF}(t)})$
  - $N$ = Total number of documents.
  - $\text{DF}(t)$ = Number of documents containing term $t$.
- **Mechanism:**
  - If a word is very common (High DF), the fraction $\frac{N}{\text{DF}}$ approaches 1, and $\log(1) = 0$. The weight becomes **zero**.
  - If a word is very rare (Low DF), the fraction becomes huge, and the log returns a **high weight**.
- **Purpose:** To penalize common words and boost rare, specific keywords.

### Zipf’s Law

- **Definition:** An empirical law stating that the frequency of any word is inversely proportional to its rank in the frequency table.
- **The Distribution:**
  - The most frequent word (Rank 1) occurs twice as often as the second most frequent word (Rank 2), and three times as often as the third (Rank 3).
  - Mathematically: $\text{Frequency} \propto \frac{1}{\text{Rank}}$.
- **Relevance to Search:**
  - Natural language follows a **Power Law** distribution.
  - A tiny number of words (stop words) make up the vast majority of text.
  - **Why IDF exists:** Without IDF, the top 100 most frequent words (which are mostly noise) would dominate every search score. IDF mathematically cancels out the "head" of the Zipf curve so we can focus on the "tail" (the meaningful content).

---

## TF-IDF (Baseline Model)

**TF-IDF** (Term Frequency-Inverse Document Frequency) transforms raw counts into weighted scores. It operates on the intuition that a word is important if it appears frequently in a document (**TF**), but rare across the entire corpus (**IDF**).

### **Raw vs. Log-Scaled TF**

- **The Problem (Raw TF):** Using the raw count ($tf$) is linear. A document with 10 occurrences of "AI" is likely more relevant than one with 1, but is a document with 100 occurrences really *10 times* more relevant?
- **The Reality:** Relevance does not scale linearly with frequency. It has **diminishing returns**. The difference between 1 and 2 is huge; the difference between 100 and 101 is negligible.
- **The Solution (Log Normalization):** We dampen the raw count using a logarithm.
  - Formula: $w_{t,d} = 1 + \log(tf_{t,d})$ (if $tf > 0$, else 0).
  - Result: A huge raw count (e.g., 100) becomes a manageable weight (e.g., $\approx 5.6$), preventing keyword stuffing from dominating the score.

### **Different IDF Variants**

IDF measures informativeness. While the core concept is constant ($\frac{Total}{Frequency}$), implementations differ to handle edge cases.

- **Standard IDF:** $\log(\frac{N}{df_t})$
  - *Risk:* If a word appears in *every* document ($df_t = N$), the value is 0. If it appears in 0 (impossible in static corpus, but possible in dynamic), it divides by zero.
- **Smooth IDF:** $\log(1 + \frac{N}{df_t + 1})$
  - *Fix:* Adds 1 to the denominator to prevent "division by zero" errors for new/unknown words.
- **Probabilistic IDF:** $\log(\frac{N}{df_t} - 1) = \log(\frac{N - df_t}{df_t})$
  - The "Odds" Interpretation: Given $p = \frac{df_t}{N}$ , it essentially compares the probability of the term appearing ($p$) vs. the probability of it *not* appearing ($1-p$).
  - The Negative Weight Issue: If a word appears in more than half the documents ($p > 0.5$ or $df_t > N/2$), the value inside the log becomes less than 1. Since $\log(x)$ where $x < 1$ is negative, common words get a negative score.
    - *Result:* Having the word in the document actually *hurts* the relevance score (which is why BM25 usually floors this value at 0 or adds a constant).

### **Vector Space Model (VSM)**

- **Concept:** We treat text as geometry. Every document is a **vector** (arrow) in a high-dimensional space.
- **Dimensions:** Each dimension represents a unique term in the vocabulary.
- **Magnitude:** The length of the vector along a specific dimension represents the weight (TF-IDF score) of that term in the document.
- **Visual:** If "apple" and "banana" are axes, a recipe for fruit salad would have a vector pointing essentially diagonally between them.

### **Cosine Similarity**

- **The Metric:** To find the "best" document for a query, we measure the **angle** between the Query Vector and the Document Vector.
- **Why Angle, Not Distance?** Euclidean distance (measuring the gap between points) is flawed because it penalizes long documents (which have longer vectors). The angle focuses on **orientation** (topic match) rather than magnitude (length).
- **Formula:** $\text{similarity} = \cos(\theta) = \frac{A \cdot B}{\|A\| \|B\|}$
- **Range:**
  - **1.0:** Perfect match (vectors point in identical direction).
  - **0.0:** No match (vectors are orthogonal/perpendicular, sharing no words).

### **Why TF-IDF Breaks on Long Documents**

- **The Bias:** Long documents naturally contain higher term frequencies (more chances to say the word) and a wider variety of unique terms.
- **The Result:** Without correction, TF-IDF systematically favors longer documents. A 500-page book mentioning "UFO" once might score higher than a short tweet about "UFOs" simply because the book's vector is "longer" (has more non-zero dimensions) or accumulates more aggregate weight.
- **The Missing Piece:** TF-IDF lacks **Document Length Normalization**. It does not penalize a document for being verbose, which is the primary problem solved by **BM25**.

---

## Probabilistic IR

This section marks the transition from **Geometry** (vectors and angles) to **Probability** (odds and likelihood). The goal shifts from "how similar is this vector?" to "what is the probability this document is relevant?"

### **The Probability of Relevance**

- **The Core Question:** We stop asking "How close are these vectors?" and start asking "Given this query $q$, what is the probability $P(R|d,q)$ that document $d$ is **Relevant**?"
- **The Ranking Principle:** The system should simply rank documents by their probability of relevance, from highest to lowest.
- **The Shift:** We are no longer measuring physical overlap; we are estimating the *chance of user satisfaction*.

### **The Binary Relevance Assumption**

- **The Simplification:** To make the math solvable, we assume relevance is **binary** ($1$ or $0$).
  - A document is either **Relevant** (it answers the query) or **Non-Relevant** (it does not).
  - There is no "sort of relevant."
- **The Reality:** While real relevance is continuous (a nuanced scale), this binary assumption allows us to use standard probability theory (Bayes' Theorem) to derive ranking formulas.

### **The Query Likelihood Intuition**

- **Flipping the Script:** Instead of asking "Does this document match the query?", we ask: **"If I were writing a document about this topic, how likely would I be to use these exact query words?"**
- **The Generative Model:** We treat the document as a "bag of words" that *generated* the query.
  - If a document contains "Apple" 50 times, the probability of a user asking "Apple" is high.
  - If it contains "Apple" 0 times, the probability is near zero.

### **Why "More Occurrences $\neq$ Linearly More Relevant"**

- **The Saturation Concept:** In the vector model (TF-IDF), term frequency is linear or log-linear. In the probabilistic view, we recognize **saturation**.
- **The Reasoning:**
  - **1 mention:** The document *might* be about the topic.
  - **3 mentions:** The document is *definitely* about the topic.
  - **1,000 mentions:** The document is *still* just "about the topic." It hasn't become "more relevant" just because it repeated the word 997 more times.
- **The Outcome:** This insight leads directly to the **BM25 Saturation Curve**, where the score contribution of a term rapidly rises and then plateaus, preventing keyword spamming from breaking the ranking.

---

## BM25

> BM25 is not magic—it is simply **TF-IDF with better assumptions.**

BM25 fixes the two biggest flaws of the baseline model: linear term frequency (spamming works) and the lack of length normalization (long docs always win).

### **The Formula**

#### Document–Query Scoring Function

The relevance score of a document \( D \) with respect to a query \( Q \) is defined as:

\[
\text{Score}(D, Q)
\;=\;
\sum_{q \in Q}
\text{IDF}(q)
\cdot
\text{TF}_{\text{sat}}(q, D)
\]

#### Global Term Weight (Inverse Document Frequency)

\[
\text{IDF}(q)
\;=\;
\log \left(
\frac{N - n_q + 0.5}{n_q + 0.5}
\right)
\]

**Where:**
- \( N \): total number of documents in the corpus  
- \( n_q \): number of documents containing term \( q \)

#### Local Term Weight (Saturated Term Frequency)

\[
\text{TF}_{\text{sat}}(q, D)
\;=\;
\frac{f(q, D)\,(k_1 + 1)}
     {f(q, D) + K}
\]

**Where:**

- \( f(q, D) \): frequency of term \( q \) in document \( D \)  
- \( k_1 \): term frequency saturation parameter

#### Document Length Normalization

\[
K
\;=\;
k_1
\left(
1 - b
+ b \cdot \frac{|D|}{\text{avgdl}}
\right)
\]

**Where:**

- \( |D| \): length of document \( D \)  
- \( \text{avgdl} \): average document length in the corpus  
- \( b \in [0,1] \): document length normalization parameter

### **1. TF Saturation (Diminishing Returns)**

**The Problem:** In standard TF-IDF, if a term appears 100 times, the score keeps going up.

**The Fix:** BM25 introduces a **saturation curve**. The score increases rapidly for the first few occurrences but eventually **plateaus** (asymptotes) to a maximum value of $k_1 + 1$.

Given the equation 3, let \( f = f(q, D) \). We compute:

$$\text{TF}_{\text{sat}}(q, D)\;=\;\frac{f(q, D)\,(k_1 + 1)}{f(q, D) + K}$$

Let \( f = f(q, D) \). We compute:

$$ \lim_{f \to \infty} \frac{f\,(k_1 + 1)}{f + K} $$

Divide numerator and denominator by \( f \):

$$ \lim_{f \to \infty} \frac{k_1 + 1}{1 + \frac{K}{f}} $$

Since \( \frac{K}{f} \to 0 \) as \( f \to \infty \), the limit is:

$$ \boxed{ \lim_{f(q,D)\to\infty} \text{TF}_{\text{sat}}(q, D) = k_1 + 1 } $$

### Document Length Normalization

- **The Problem:** Long documents naturally have higher term counts and more unique words, giving them an unfair advantage in raw TF-IDF.
- **The Fix:** The denominator includes a penalty term based on the ratio $\frac{|D|}{\text{avgdl}}$.
  - If a document is **shorter** than average ($< \text{avgdl}$), the denominator shrinks, boosting the score.
  - If a document is **longer** than average ($> \text{avgdl}$), the denominator grows, penalizing the score.
- **The Logic:** A mention in a tweet is a strong signal. A mention in a 500-page book might just be noise.

### **3. IDF Smoothing**

- **The Twist:** BM25 typically uses the probabilistic IDF variant: $\log \frac{N - n + 0.5}{n + 0.5}$.
- **The Purpose:**
  - **Stop Word Handling:** Extremely common words (where $n > N/2$) can yield negative IDF values. Standard implementations floor this at 0 or a small epsilon to prevent "relevant" terms from penalizing the document.
  - **Rare Word Boosting:** It aggressively boosts rare terms, ensuring that a specific ID or error code dominates the ranking even if the TF is low.

### **4. Hyperparameters ($k_1$, $b$)**

These are the "knobs" you can turn to tune the algorithm for your specific dataset.

- **$k_1$ (Term Saturation Control):**
  - **Typical Value:** 1.2 to 2.0.
  - **Function:** Controls how quickly the TF curve saturates.
  - **Low $k_1$ (e.g., 1.2):** Saturation happens fast. A few mentions are enough to reach max score. (Good for short queries/documents).
  - **High $k_1$ (e.g., 2.0+):** Saturation is slower. We care more about the exact count difference between 10 vs. 20.
- **$b$ (Length Normalization Control):**
  - **Typical Value:** 0.75.
  - **Function:** Controls how much we penalize long documents.
  - **$b = 1$:** Full normalization. We treat length as purely "verbosity" and penalize it heavily.
  - **$b = 0$:** No normalization. We ignore length entirely (reverts to standard TF behavior).
  - **Logic:** If your documents are all roughly the same length (e.g., tweets), set $b$ low. If they vary wildly (tweets vs. books), set $b$ high.

---

## Indexing & execution

### The Inverted Index

- **Definition:** The fundamental data structure of search. Instead of storing documents as "ID $\rightarrow$ Text" (like a database), it stores them as "Word $\rightarrow$ IDs".
- **Analogy:** It’s like the index at the back of a textbook. You don’t read the whole book to find "Photosynthesis"; you look up "Photosynthesis" in the index to find page numbers.
- **Mechanism:**
  - **Key:** The term (token).
  - **Value:** A list of every document ID containing that term.
  - **Speed:** Lookup is $O(1)$ or $O(\log N)$ depending on implementation, regardless of corpus size.

### Posting Lists

- **Definition:** The "Value" part of the inverted index. A "posting" is a single entry in the list, typically containing:
  - **Doc ID:** Which document has the word.
  - **Term Frequency (TF):** How many times it appears (needed for BM25).
  - **Positions:** *Where* it appears (needed for phrase search, e.g., "University *of* California").
- **Compression:** These lists can get huge. Techniques like **Delta Encoding** (storing the difference between IDs: 10, +5, +2 instead of 10, 15, 17) and **VByte** compression are used to keep them small in memory.

### Document Length Storage

- **The Necessity:** BM25 needs $ |D| $ (document length) and $ \text{avgdl} $ (average document length) to normalize scores.
- **Storage:**
  - **Per-Document:** An array storing the length (token count) of every document ID.
  - **Global:** A single value for $\text{avgdl}$ updated as documents are indexed.
- **Impact:** This lookup is extremely fast because it’s just an array access by Doc ID.

### Scoring at Query Time

- **The Process:**
  1. **Parse Query:** Break query "blue sky" into tokens `["blue", "sky"]`.
  2. **Fetch Lists:** Retrieve posting lists for "blue" and "sky".
  3. **Union/Intersection:**
     - **OR Query:** Union the lists (Document must have "blue" OR "sky").
     - **AND Query:** Intersect the lists (Document must have "blue" AND "sky").
  4. **Calculate:** For each matching doc, fetch its TF from the posting list and its Length from storage. Plug them into the BM25 formula.
  5. **Accumulate:** Sum the scores for "blue" and "sky" to get the final document score.

### Why These Models Scale Well

- **Sparsity:** Most words don’t appear in most documents. If a user searches for "Zebra", the engine only touches the 0.01% of documents containing "Zebra". It completely ignores the other 99.99%.
- **Memory Efficiency:** The index is compact. We only store counts and IDs, not the full text.
- **Parallelism:** You can split the index into "shards" (e.g., Docs 1-1M on Server A, Docs 1M-2M on Server B) and query them simultaneously.

---

## Evaluation

How you know one ranking is better than another. This is what turns IR from “math” into “engineering”.

### Core Metrics: Precision & Recall

These are the fundamental trade-offs in search. You can rarely maximize both simultaneously.

- **Precision:** "Of the documents we retrieved, how many are actually relevant?"
  - *Formula:* $\frac{\text{Relevant Retrieved}}{\text{Total Retrieved}}$
  - *High Precision:* Search for "Python error" returns only coding fixes, no snakes.
- **Recall:** "Of all the relevant documents that exist, how many did we manage to find?"
  - *Formula:* $\frac{\text{Relevant Retrieved}}{\text{Total Relevant in Corpus}}$
  - *High Recall:* Search finds *every* legal precedent, even if it returns some irrelevant junk.

### **Precision@k (P@k)**

- **The Problem:** Users rarely look past the first few results. Standard precision evaluates the whole list (which might be 10,000 docs).
- **The Fix:** Measure precision only at rank $k$.
  - **P@1:** Is the very first result relevant? (Critical for Siri/Alexa).
  - **P@10:** How many of the first page results are good? (Standard for Google).
- **Formula:** $\frac{\text{Relevant items in top } k}{k}$

### MAP (Mean Average Precision)

- **The Goal:** To reward systems that put relevant documents **higher** up the list.
- **Mechanism:**
  1. Calculate Precision@k for *every* position $k$ where a relevant document appears.
  2. Average those values to get Average Precision (AP) for a single query.
  3. Take the **Mean** of AP across all queries in your test set.
- **Why it matters:** It penalizes a relevant doc appearing at rank #10 much more than one appearing at rank #2.

### NDCG (Normalized Discounted Cumulative Gain)

- **The Nuance:** Binary relevance (Relevant/Not Relevant) is often too simple. Some docs are "perfect," others are "okay."
- **Cumulative Gain (CG):** Sum of relevance scores (e.g., 3=Perfect, 2=Good, 1=Okay, 0=Bad).
- **Discounted (DCG):** Divides the score by $\log(\text{rank})$. A "Perfect" result at rank #1 gets full points; at rank #10, it gets very few points.
- **Normalized (NDCG):** Divides DCG by the "Ideal DCG" (the score of a perfectly ordered list) to get a value between 0.0 and 1.0. This allows comparison across different queries.

### Offline vs. Online Evaluation

- **Offline Evaluation (The Lab):**
  - **Method:** Use a static dataset with human-labeled "relevance judgments" (e.g., MS MARCO, TREC).
  - **Pros:** Repeatable, safe, no user impact.
  - **Cons:** Expensive to label; human raters might not match real user intent.
- **Online Evaluation (The Wild):**
  - **Method:** A/B testing on live traffic.
  - **Metrics:** Click-Through Rate (CTR), Dwell Time (time spent on page), Conversion Rate.
  - **Pros:** Measures actual user satisfaction.
  - **Cons:** Risky (bad search hurts revenue/trust), noisy data.

---

## Tools & Ecosystem

Where to apply these concepts in the real world.

### Production Search Engines

These are full-scale systems that manage the inverted index, scaling, and scoring for you.

#### Elasticsearch / OpenSearch
- **Role:** The industry standard for search.
- **Relevance:** Uses **BM25** as the default similarity algorithm (since version 5.0). Highly tunable (you can adjust parameters in the mapping settings).

#### Apache Solr
- **Role:** The veteran open-source search platform.
- **Relevance:** Also built on Lucene; exposes deep control over TF-IDF and BM25 parameters.

#### Meilisearch
- **Role:** A modern, Rust-based engine focused on speed and “search-as-you-type.”
- **Relevance:** Uses a unique ranking system that prioritizes typo tolerance and exact matching rules over pure probabilistic BM25, but the foundational lexical concepts remain.

#### Typesense
- **Role:** An open-source, typo-tolerant search engine optimized for speed.
- **Relevance:** A lightweight alternative to Elastic, great for implementing lexical search without the operational overhead.

### Core Libraries (The Engines)

If you are building a search engine from scratch, you use these libraries.

#### Apache Lucene (Java)
- **Role:** The “engine” inside Elasticsearch and Solr.
- **Relevance:** It *is* the reference implementation for the inverted index and BM25 scoring.

#### Tantivy (Rust)
- **Role:** A high-performance search library inspired by Lucene but faster.
- **Relevance:** Becoming the backbone for modern tools (like LanceDB) due to its speed and memory efficiency.

#### Bleve (Go)
- **Role:** The go-to indexing library for Go applications.
- **Relevance:** Implements standard TF-IDF and BM25 scoring.

### Python Libraries (For Learning & Prototyping)

Use these to run the math on your laptop without setting up a server.

#### Scikit-Learn (`sklearn.feature_extraction.text`)
- **Tool:** `TfidfVectorizer`
- **Use:** Perfect for calculating **TF-IDF matrices** on static datasets (CSV / Pandas). Great for understanding the math of sparse vectors.

#### Rank-BM25 (`rank_bm25`)
- **Tools:** `BM25Okapi`, `BM25L`, `BM25Plus`
- **Use:** A dedicated library implementing the various **BM25 algorithms**. Excellent for comparing how different formulas rank the same documents.

#### Gensim
- **Use:** While known for embeddings (Word2Vec), it has robust implementations for TF-IDF and LSI (Latent Semantic Indexing).

---

## Limitations & The Need for Semantic Search

Why TF-IDF and BM25 are not enough for modern applications.

### **1. The Vocabulary Gap (Synonyms)**

- **The Problem:** Lexical search requires exact character matching.
- **The Failure:** A user searching for "laptop" will miss a document that only uses the word "notebook," even though they are the same thing.
- **The Patch:** Developers historically maintained massive "synonym lists" manually, which is brittle and hard to scale.

### **2. Polysemy (Ambiguity)**

- **The Problem:** Many words have multiple meanings.
- **The Failure:** A search for "Java" (the programming language) will return results about "Java" (the island) or "Java" (coffee).
- **The Reason:** Lexical models see the string "J-a-v-a," not the concept behind it. They cannot use surrounding context to disambiguate.

### **3. Long-Tail Queries (Zero Results)**

- **The Problem:** Users often search using natural language questions ("why is my screen flickering?").
- **The Failure:** If the document doesn't contain those *exact* words (e.g., it says "monitor display artifacts"), the lexical score is zero.
- **The Stat:** In traditional search engines, 15-20% of daily queries had never been seen before, often resulting in "0 results found."

### **4. Ignoring User Intent**

- **The Problem:** Keywords don't equal intent.
- **The Failure:**
  - Query: "flights to London"
  - Document: "flights **from** London"
  - *Result:* High lexical score (match on "flights", "London"), but completely wrong intent.
- **The Need:** A system that understands the *directionality* and relationship between words.

### **5. The Transition to Semantic Search**

- **The Solution:** **Vector Embeddings**.
- **The Shift:** Instead of matching distinct words, we match **meaning**.
- **The Mechanism:** We convert text into dense vectors where "King" - "Man" + "Woman" $\approx$ "Queen."
- **The Hybrid Era:** Modern search (RAG, E-commerce) rarely uses *just* one. We now use **Hybrid Search**:
  - **BM25** for exact matches (IDs, names, specific codes).
  - **Embeddings** for concept matches (synonyms, intent, questions).
