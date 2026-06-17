## Claude Code Skills: Technical Summary

## Concept & Definition

**Skills** are modular, portable extensions designed to teach Claude Code specific workflows or domain knowledge. Rather than relying on repetitive manual prompting, a Skill encapsulates instructions, metadata, and resources into a reusable "recipe." When a relevant task is identified, Claude dynamically loads the appropriate Skill to execute the work consistently.

## Progressive Context Disclosure

One of the most powerful aspects of Skills is how they manage the context window. Instead of dumping every instruction into the prompt at once, Skills follow a **three-tier loading model** to maintain high performance and lower token costs:

- **Layer 1: Discovery (Metadata)** – Only the Skill's name and description (~100 tokens) are always present in the context. This allows Claude to "know" a capability exists without filling the window.
- **Layer 2: Activation (Instructions)** – The full `SKILL.md` file (the core logic) is only injected into the conversation if Claude determines it is relevant to the current task.
- **Layer 3: Execution (Resources)** – Supporting scripts, heavy documentation, or large assets are only loaded on-demand during the actual execution phase of the Skill.

## Core Capabilities

Skills transform Claude from a reactive chat assistant into a **programmable coding agent**. They enable developers to:

- **Standardize Processes:** Codify team-wide best practices or design guidelines.
- **Automate Complexity:** Handle multi-step development tasks (e.g., migrations or dependency updates).
- **Embed Context:** Provide project-specific knowledge that isn't part of the global training data.
- **Custom Commands:** Extend the CLI with specialized slash commands tailored to a specific stack.

## Structure & Components

Each Skill is organized as a discrete folder containing three primary elements:

- **`SKILL.md`**: The core logic. This file contains the primary instructions describing the Skill’s purpose and operational rules.
- **Metadata**: Define the Skill's identity and the specific triggers that tell Claude when to activate it.
- **Supporting Resources**: Optional scripts, templates, or supplementary documentation used during execution.

## Activation & Execution

Skills are invoked through two primary mechanisms:

- **Explicit Invocations**: Triggered manually by the user via slash commands (e.g., `/api-audit`).
- **Contextual Activation**: Claude autonomously detects the user's intent or the project state and proactively loads the relevant Skill.

## Lifecycle & Collaboration

Because Skills are stored as file-based assets, they are managed using standard software development lifecycles:

- **Version Control**: Skills reside in the repository alongside source code, allowing for versioning and history tracking.
- **Portability**: They can be easily shared across teams or ported between different projects.
- **Local Iteration**: Developers can create, test, and refine Skills locally before deploying them to the wider team.

## Pratical demo

Let's build a practical demo for a **`brand-guardian`** skill. This is a classic use case for teams that need Claude to write code or UI components that strictly follow a specific company's design system without cluttering every single prompt with hex codes and CSS rules.

### 1. The File Structure

In your project, you would create this directory:

Plaintext

```
my-app/
└── .claude/
    └── skills/
        └── brand-guardian/
            ├── SKILL.md
            └── references/
                └── design-tokens.json
```

------

### 2. The `SKILL.md` (The Logic)

This file uses YAML frontmatter for the **Metadata Layer**.

```markdown
---
name: brand-guardian
description: This skill ensures all UI components and CSS follow the "Acme Corp" design system. Trigger this when the user mentions "UI," "styles," "components," or "brand compliance."
---

# Brand Guardian Instructions
When this skill is active, you must act as a Senior Design Engineer. 

## Workflow
1. **Analyze Requirements**: Before writing code, read `references/design-tokens.json` to get the latest hex codes and spacing values.
2. **Apply Constraints**: 
   - Never use "Inter" or "Roboto"; only use the brand font "Lexend."
   - Buttons must always have a `4px` border-radius.
   - Use CSS variables (`--acme-primary`) instead of hardcoded hex values.

## Verification
End every output with a "Compliance Check" list confirming you used the correct tokens.
```

### 3. The Reference File (The Heavy Context)

This is the **Execution Layer**. It is only "read" by Claude if it decides it needs the specific values to complete your request.

**`references/design-tokens.json`**

```json
{
  "colors": {
    "primary": "#FF5733",
    "secondary": "#2E4053",
    "background": "#F4F6F7"
  },
  "spacing": {
    "base": "8px",
    "large": "24px"
  },
  "typography": {
    "font-family": "Lexend, sans-serif"
  }
}
```

### 4. The Demo: Progressive Disclosure in Action

Here is how the interaction looks in the **Claude Code CLI**:

**User:** > "Claude, build a login button for the hero section."

**How Claude Processes This (Under the Hood):**

1. **Layer 1 (Metadata):** Claude scans all installed skills. It sees `brand-guardian` and its description mentioning "UI." It decides this is a match.
2. **Layer 2 (Instructions):** Claude "loads" the `SKILL.md`. It now knows it needs to be a "Senior Design Engineer" and follow the Acme Corp rules.
3. **Layer 3 (Execution):** Claude sees the instruction to "read `design-tokens.json`." It uses its filesystem tool to read that specific file and extract `#FF5733`.

**Claude's Response:**

> I'm applying the **brand-guardian** skill to ensure design compliance.
>
> ```js
> const LoginButton = () => (
>   <button style={{ 
>     backgroundColor: 'var(--acme-primary, #FF5733)', 
>     fontFamily: 'Lexend',
>     borderRadius: '4px' 
>   }}>
>     Log In
>   </button>
> );
> ```
>
> **Compliance Check:**
>
> - [x] Used Lexend Font
> - [x] Applied Primary Brand Color
> - [x] Enforced 4px Border Radius

### Why this works:

- **No Context Bloat:** If you were just asking Claude to "refactor a backend function," the `brand-guardian` instructions and the heavy `design-tokens.json` file would **never** be loaded, saving you thousands of tokens.
- **Consistency:** Every developer on the team who clones this repo gets the same `.claude/skills` folder, ensuring the AI behaves identically for everyone.

## Skill Priority

If you clone a repository that has a skill with the same name as one of your personal skills, which one wins? There's a clear priority order:

1. **Enterprise** — managed settings, highest priority
2. **Personal** — your home directory (`~/.claude/skills`)
3. **Project** — the `.claude/skills` directory inside a repository
4. **Plugins** — installed plugins, lowest priority

This lets organizations enforce standards through enterprise skills while still allowing individual customization. If your company has an enterprise "code-review" skill and you create a personal "code-review" skill with the same name, the enterprise version takes precedence.

To avoid conflicts, use descriptive names. Instead of just "review," use something like "frontend-review" or "backend-review."

## Advanced Skill Configuration and Isolation

While the basic metadata and logic of a skill reside in its `SKILL.md` file, you can heavily customize how that skill executes by leveraging YAML frontmatter. This configuration layer dictates the skill's operational boundaries, execution context, and tool access.

### Execution Context: Forking Sub-Agents

By default, when Claude triggers a skill, it injects the `SKILL.md` instructions and any subsequent outputs directly into your main conversation window. For simple tasks, this is efficient. However, for verbose operations—like a deep codebase analysis or brainstorming divergent architectures—this clutters your primary context window and dilutes the AI's reasoning on your core task.

Use the `context: fork` frontmatter option to isolate the skill's execution.

```
---
name: deep-analysis
description: Analyzes the entire repository for security vulnerabilities.
context: fork
---
```

When a skill is configured with `context: fork`, Claude spawns an isolated sub-agent to execute the task. The sub-agent performs the heavy lifting, processes the verbose outputs, and only returns the final, summarized result to your main session. This prevents the exploratory or verbose context generated during the skill's execution from polluting your main conversational memory.

### Restricting Tool Access

To adhere to the principle of least privilege, use the `allowed-tools` frontmatter to strictly bind the capabilities of the skill during its execution.

```
---
name: format-code
description: Formats code according to style guidelines.
allowed-tools:
  - Read
  - Write
---
```

If a formatting skill should never be allowed to execute arbitrary shell commands or perform web searches, omit those tools from the `allowed-tools` list. By explicitly defining which tools the skill can access, you prevent destructive actions (like accidental deletions via the Bash tool) if the model hallucinates or misunderstands the prompt while the skill is active.

### Enforcing Parameter Inputs

When building slash commands for other developers on your team, you often need specific inputs before the skill can run. Use the `argument-hint` frontmatter to prompt users for required parameters if they invoke the skill without them.

```
---
name: generate-component
description: Scaffolds a new React component.
argument-hint: "Please provide the component name (e.g., /generate-component Button)"
---
```

If a developer types `/generate-component` and hits enter, Claude Code intercepts the execution and displays the string defined in `argument-hint`, ensuring the skill has the exact data it needs to function correctly without failing silently.
## Navigating the Claude Code Ecosystem

To understand how Skills fit into your development environment, it helps to see them as the "connective tissue" between your instructions and your tools.

### 1. Skills vs. Subagents

The best way to differentiate these is the **"Kitchen Analogy"**:

- **Skill = A Cookbook:** It’s a set of instructions and recipes. When Claude (the Head Chef) needs to make a specific sauce, he opens the book, reads the instructions into his memory, and does the work himself.
- **Subagent = A Sous Chef:** This is a separate worker with their own "station" (context window). Claude delegates a whole task to them (e.g., "Go prep all the vegetables"). The Sous Chef works independently and just brings back the finished tray.

| **Feature**    | **Skills**                                     | **Subagents**                                        |
| -------------- | ---------------------------------------------- | ---------------------------------------------------- |
| **Context**    | Shared with the main chat.                     | Isolated (separate window).                          |
| **Best For**   | "How-to" guides, small utilities, style rules. | Heavy research, large file analysis, parallel tasks. |
| **Efficiency** | Progressive loading (saves tokens).            | Zero bloat in your main chat window.                 |

### 2. Skills vs. Commands

In the latest versions of Claude Code, these have largely **merged**, but the distinction remains in how they are triggered:

- **Slash Commands (`/fix`):** These are explicit, user-driven shortcuts. You type it, Claude does it. They are predictable and provide a "manual override."
- **Skills:** These are the *package* that powers the command. A Skill can be a slash command, but it can also be **automatically discovered**. If you describe a Skill's purpose in its metadata, Claude can choose to load it without you ever typing a slash.

> **Note:** If you find yourself typing a specific prompt repeatedly, turn it into a **Command**. If you want Claude to "know" how to do something whenever the topic comes up, turn it into a **Skill**.

### 3. Skills vs. MCP (Model Context Protocol)

This is a comparison of **Knowledge vs. Access**:

- **MCP:** This is the "pipe" or the "adapter." It connects Claude to the outside world (GitHub, Google Drive, your Database). It gives Claude **Tools** (e.g., `list_github_repos`).
- **Skills:** These are the "manual" for the tools. An MCP server might give Claude the tool to "Post to Slack," but a **Skill** tells Claude *when* to post, *what* tone to use, and *how* to format the message.

**Example:**

- **MCP:** Provides the `query_sql` tool.
- **Skill:** Provides the "Database Best Practices" guide that tells Claude to always add `LIMIT 10` to every query it writes using that tool.

### Summary Table: Which to use?

| **Use Case**                                 | **Recommended Tool** | **Why?**                                             |
| -------------------------------------------- | -------------------- | ---------------------------------------------------- |
| "Always use 2 spaces for indentation."       | **`CLAUDE.md`**      | It's always-on context for every message.            |
| "Run my custom linter and fix the errors."   | **Skill / Command**  | High-utility, repeatable action.                     |
| "Research this 50-file bug across the repo." | **Subagent**         | Prevents the main chat from hitting the token limit. |
| "Read my internal Jira tickets."             | **MCP**              | Requires a live connection to an external API.       |

### **Skills vs. `settings.json` Rules**

This is a comparison of **Global Guardrails** versus **Contextual Logic**.

- **`settings.json` Rules = The Constitution:** These are the "laws of the land" for your entire environment. They are injected into the system prompt at the start of **every** turn. They define your persona, your preferred libraries (like Pydantic), and how you expect Claude to use its tools (like MCP).
- **Skills = The Specialist's Manual:** These are deep-dives into specific procedures. Instead of forcing Claude to remember 50 different Pydantic validation rules at all times, a Skill loads that specific "validation logic" only when you are actually defining a new model.

| **Feature**      | **settings.json Rules**                      | **Skills**                                     |
| ---------------- | -------------------------------------------- | ---------------------------------------------- |
| **Visibility**   | **Always-On.** Present in every message.     | **On-Demand.** Loaded via triggers.            |
| **Priority**     | **Tier 1 (Highest).** Defines core behavior. | **Tier 2.** Defines specific workflows.        |
| **Context Cost** | Constant. Fixed token overhead.              | Dynamic. Efficient for large docs.             |
| **Best For**     | Personas, LSPs, and "Non-negotiables."       | API documentation and complex "How-to" guides. |

#### **The "Context Rot" Warning**

If you pack too many rules into `settings.json`, you risk **Attention Dilution**. Claude may begin to prioritize the first few and last few rules while "fuzzing" the ones in the middle.

> **Pro Tip:** Use **`settings.json`** for *how to think* (e.g., "Always use Pyright for type checking") and **Skills** for *what to build* (e.g., "Here is how we implement our specific Agent Lifecycle").

#### **Case Study: The "Eyes" vs. The "Encyclopedia"**

To see the difference between a **Rule** and a **Skill** in practice, consider how a developer might configure **Type Checking** (Pyright) versus **API Documentation** (Context7).

##### **1. The Rule: Static Validation (Pyright)**

A rule in `settings.json` like `"Use the Pyright Language Server via the MCP LSP server"` functions as the AI’s **"Eyes."**

- **Why it's a Rule:** Because you are writing code, the AI needs its "eyes" open for every single character it types to catch syntax errors or type mismatches in real-time.
- **Effect:** It is a low-latency, always-on background process that ensures basic code quality without requiring the AI to "think" about whether it should be active.

##### **2. The Skill: Dynamic Research (Context7)**

A directive like `"Always use Context7 when I need library/API documentation"` is better suited as a **Skill**.

- **Why it's a Skill:** This is a heavy-duty research tool. If it were a constant rule, the AI might hesitate and try to "look up" documentation for basic functions it already knows (like `json` or `os`), wasting tokens and increasing latency.
- **Effect:** By moving this to a Skill, you switch the logic from "always trust the tool" to "trigger the Researcher Mode." The AI only pulls in massive chunks of external documentation when it recognizes a complex or unfamiliar third-party API.

### **Skills vs. `CLAUDE.md`**

This is a comparison of **Project Foundations** versus **Task-Specific Workflows**.

- **`CLAUDE.md` = The Project Constitution:** This is the "Ground Truth" for a specific repository. Claude Code is hard-coded to read this file the moment it initializes in a directory. It contains the "Universal Laws" of the codebase—build commands, test suites, and core tech-stack choices—that apply to every single file.
- **Skills = The Specialist's Toolkit:** These are "Lazy-Loaded" expertise modules. While `CLAUDE.md` tells Claude *what* the project is, a Skill tells Claude *how* to perform a complex, multi-step operation. They allow you to keep the main context window clean by only loading heavy documentation or intricate logic when a specific intent is triggered.

| **Feature**      | **CLAUDE.md**                         | **Skills**                                   |
| ---------------- | ------------------------------------- | -------------------------------------------- |
| **Scope**        | **Repo-Wide.** Unique to one project. | **Portable.** Can be shared across repos.    |
| **Loading**      | **Always-On.** Read at session start. | **On-Demand.** Triggered by context/intent.  |
| **Context Cost** | Constant. Part of the base prompt.    | Dynamic. High efficiency for large docs.     |
| **Best For**     | Build/Test commands and core styles.  | Complex workflows (e.g., "Agent Lifecycle"). |

#### **The "Context Hygiene" Strategy**

The common mistake is treating `CLAUDE.md` like a junk drawer for every rule you’ve ever written. As the file grows, Claude's "Reasoning Density" drops.

> **Pro Tip:** Use **`CLAUDE.md`** for the *Metadata of the Project* (e.g., "We use Pydantic v2 and pytest") and move your *Procedural Guides* (e.g., "How to implement a new Agent from `AGENTS.md`") into **Skills**. This keeps Claude's immediate "working memory" sharp and focused on the code at hand.