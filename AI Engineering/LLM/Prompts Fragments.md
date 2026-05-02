# Prompt Fragments

### **Title: The 4-Backtick Markdown Trick (Safe Export Directive)**

**Description:** A reusable prompt snippet designed to prevent markdown rendering bugs when an LLM generates text containing internal code blocks. It forces the model to wrap its entire output in a 4-backtick container, ensuring the nested 3-backtick blocks don't prematurely break the formatting. This keeps the output perfectly intact and clean for copy-pasting into your own `.md` files.

```
**FORMATTING INSTRUCTION for Markdown containing Code Blocks:**
When generating Markdown content that includes internal code blocks (e.g., ```json or ```bash), you MUST wrap your entire response inside a 4-backtick raw text block (````text ... ````). 

**Why this is necessary:**
Standard markdown parsers close a code block at the first matching 3-backtick delimiter they find. If you wrap my requested markdown in standard 3 backticks, the internal code blocks will prematurely close the outer block, breaking the rendering and making it impossible for me to cleanly copy-paste the raw content. Using a 4-backtick outer container safely encapsulates the 3-backtick internal blocks.
```
