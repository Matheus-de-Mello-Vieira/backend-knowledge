# Recommended MCPs

For protocol mechanics, start with [01 Overview](./01%20Overview.md) and [03 Core Primitives](./03%20Core%20Primitives.md). This note focuses on practical MCPs that are commonly useful when building or operating AI-assisted development workflows.

## Best MCPs to Install

* **Playwright MCP:** Useful for web development and automated testing. It allows the model to interact with a live browser, capture screenshots, and inspect the accessibility tree to debug UI issues or scrape data in real time. [Server info](https://github.com/microsoft/playwright-mcp)
* **LSP (Language Server Protocol) MCP:** Bridges IDE language intelligence directly to the model. This provides hover information, real-time diagnostics, and go-to-definition capabilities. [Server info](https://github.com/isaacphi/mcp-language-server)
* **Context7:** A documentation-as-context tool that fetches version-specific docs and code examples directly from library sources. [Server info](https://github.com/upstash/context7)
* **Remote Repository MCP:** Provides a unified interface to repository hosting APIs so the model can inspect pull requests, issues, and CI/CD state. [MCP Registry](https://registry.modelcontextprotocol.io/), [GitHub MCP](https://github.com/github/github-mcp-server), [GitLab reference server](https://github.com/modelcontextprotocol/servers-archived/tree/main/src/gitlab)
* **Local Git MCP:** Gives the model access to local version control history, helping it inspect changes and craft atomic commits. [Server info](https://github.com/modelcontextprotocol/servers/tree/main/src/git)
* **Filesystem MCP:** Provides structured access to read, write, and search local directories. [Server info](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)

## A Note on the Bash or Shell MCP

Many of the MCPs listed above can technically be replaced by a single shell-oriented MCP. Specialized servers are usually better for several reasons:

- **Safety and Guardrails:** Specialized MCPs typically use allow-lists or tighter boundaries that reduce destructive risk.
- **Structured Output:** They return structured data rather than raw terminal text, reducing parsing errors and hallucinations.
- **Token Efficiency:** They often support chunking and focused access patterns that reduce context waste.
- **Portability:** They behave more consistently across macOS, Linux, and Windows than shell command assumptions do.
