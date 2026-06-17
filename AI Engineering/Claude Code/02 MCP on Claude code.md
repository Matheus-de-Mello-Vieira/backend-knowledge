# MCP on Claude Code

## Optimizing MCPs in Claude Code

As outlined in the architectural challenges of generic LLMs, giving an AI access to too many tools at once leads to severe context bloat and poor tool selection. In Claude Code, this issue most commonly manifests when developers rely on a single, monolithic MCP configuration. 

### The Project-Wide Pitfall

Keeping all your MCPs in a generic, project-wide configuration means Claude Code is forced to load tools it won't need for most tasks. To bypass the context limitations and JSON ambiguities mentioned previously, you must curate exactly which tools Claude has access to at any given time.

## Secret Management & Environment Variables

When configuring MCP servers, you will frequently need to provide API keys, access tokens, or sensitive database credentials. Hardcoding these secrets directly into your `mcp.json` files creates a critical security vulnerability and risks accidentally leaking credentials to public version control systems.

### Environment Variable Expansion in `mcp.json`

To keep your configurations secure and portable, Claude Code supports dynamic environment variable expansion within your MCP configuration files. Instead of writing raw credentials, you can use the standard `${VARIABLE_NAME}` syntax.

For example, a secure configuration for a GitHub MCP server would look like this:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

### Targeted Configuration Strategy

Instead of a single `mcp.json` file in your project root, create multiple, task-specific configurations (for example, `mcp.json.frontend`, `mcp.json.database`, `mcp.json.testing`). 

You can then load these dynamically via the command line based on the task at hand:

* **To append specific tools to your existing configuration:**
  Use this to add a focused set of tools without losing your base setup.
  ```bash
  claude --mcp-config <full-path>/mcp.json.something
  ```

* **To completely replace the existing MCPs (Strict Mode):**
  Use this to lock Claude Code into a highly specific context, completely removing the burden of unrelated tools.
  ```bash
  claude --mcp-config <full-path>/mcp.json.something --strict-mcp-config
  ```

## Plugins

Plugins are a lightweight way to package and share a bundle of Slash Commands, Subagents, MCP servers, and Hooks. To manage plugins, use the `/plugins` command. A marketplace is a bundle of plugins that can be installed together.

