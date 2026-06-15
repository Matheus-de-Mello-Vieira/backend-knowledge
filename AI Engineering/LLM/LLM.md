# Large Language Models (LLMs)

LLMs (`/ˌɛl.ɛl.ˈɛm/`) are AI models designed to understand and generate human-like text, playing a critical role in natural language processing (NLP) by enabling machines to interpret, analyze, and generate human language.

## Key Capabilities

* **Text generation**: Creating coherent and contextually relevant text from prompts.
* **Understanding**: Comprehending and summarizing large text inputs.
* **Translation**: Converting text between languages with high accuracy.

## Enhancing Domain-Specific Performance in LLM Systems

LLM systems are often adapted with a mix of training-time and runtime techniques:

* **Fine-Tuning**: Updates model weights using domain-specific data to improve task behavior, terminology usage, and response style. Best suited for repeatable tasks with stable requirements. Costly to train and maintain, slower to update, and not ideal for frequently changing knowledge.
* **Prompt Engineering**: Constrains and steers model behavior via structured instructions, examples, and output schemas. Fast to iterate and zero-training, but does not introduce new knowledge. Performance can be brittle and highly model-dependent. See [Prompt Engineering](Prompt%20Engineering.md).
* **Domain-Specific Retrieval (RAG)**: Augments the model with external, authoritative data sources at inference time. Improves factual accuracy, freshness, and auditability without retraining. Effectiveness depends on document quality, chunking, embedding strategy, and retrieval precision. See [RAG Fundamentals](../RAG/01%20Fundamentals.md).

## Evolution of LLMs

### GPT (Generative Pre-trained Transformer)

* **Introduced**: 2018 by OpenAI
* **Key innovation**: First large-scale transformer-based lanague model. Used unsupervised leraning on vast text data, followed by fine-tuning.
* **Impact**: Highlighted the power of transformers for NLP and pre-training on large datasets.

### GPT-2

* **Introduced**: 2019 by OpenAI
* **Key innovation**: Scaled up to 1.5 billion parameters, improving text generation and coherence.
* **Impact**: Raised ethical concerns due to its ability to generate realistic text.

### GPT-3

* **Introduced**: 2020 by OpenAI
* **Key innovation**: Scaled up to 175 billions parameters, enabling few-shot learning.
* **Impact**: Widely adopted for various applications, from chatbots to creative writing tools.

### ChatGPT (and GPT-4)

* **Introduced**: ChatGPT in late 2022, GPT-4 in 2023
* **Key innovation**: Enhanced contextual understanding for conversational AI, with GPT-4 adding multimodal capabilities (text and images).
* **Impact**: ChatGPT popularized conversational AI, GPT-4 set new standards for multimodal interaction in human-computer communication.

### GPT-4o

* **Introduced**: March 2023 by OpenAI
* **Key innovation**: GPT-4.0 scaled to trillions of parameters improving complex reasoning and contextual accuracy.
* **Impact**: Sparked ethical debates on AI safety, bias, and misuse, leading to calls for stricter guidelines and transparency in AI deployment.

### GPT-4o Mini

* **Introduced**: March 2023 alongside GPT-4.0 by OpenAI
* **Key innovation**: GPT-4.0 Mini is a compact, resource-efficient version of GPT-4.0, maintaining advanced features with reduced computational needs.
* **Impact**: Expanded advanced AI's reach, promoting use in chatbots and content creation, and ignited discussions on democratizing AI and the risks of widespread access to powerful generative models.

### Gemini 1.5

- **Introduced:** February 2024 by Google.
- **Key Innovation:** Processes up to 1 million tokens with Mixture-of-Experts (MoE) architecture for improved efficiency.
- **Impact:** Enhances performance across text, audio, video, and images, enabling advanced applications like document summarization and data analysis. Prompted discussions on ethical implications in education and content creation.

### Gemini 1.5 Pro

- **Introduced:** February 2024 as part of the Gemini 1.5 rollout.
- **Key Innovation:** Mid-size multimodal model with breakthroughs in long-context understanding, matching the performance of Gemini 1.0 Ultra.
- **Impact:** Boosts capabilities for developers and enterprises in data processing and content generation, raising questions about responsible AI use across industries.

### Claude 3.5

- **Introduced:** June 21, 2024 by Anthropic.
- **Key Innovation:** Advanced vision, 200K token context, "Artifacts" feature, twice the speed of Claude 3 Opus.
- **Impact:** Superior in coding, reasoning, and visual tasks; sparked discussions on responsible AI in customer support and collaboration.


