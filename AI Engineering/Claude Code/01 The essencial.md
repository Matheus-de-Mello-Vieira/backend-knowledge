# Essentials

## Slash commands

* `/clear` Wipes all conversation history, no context preservation
  * Use it when conversation is off track or irrelevant 
  
* `/compact` Summarizes and condenses context, preserving essential info
  * At natural breakpoints to manage context limits.
  
* `/agents` Manage sub agents

* `/config` will open the config panel
  * It will saved on `settings.json` files:
    * User: `~/.claude/`, affects only you, all projects
      * best for:
        * Personal preferences you want everywhere (themes, editor settings)
        * Tools and plugins you use across all projects
        * API keys and authentication (stored securely)
    * Project:  `.claude/` in repository, affects  all collaborators on this repository, and it is commited to git
      * best for:
        * Team-shared settings (permissions, hooks, MCP servers)
        * Plugins the whole team should have
        * Standardizing tooling across collaborators
    * Local: `.claude/*.local.*` files, affects only you in this repository only, and it is gitignored
      * best for:
        * Personal overrides for a specific project
        * Testing configurations before sharing with the team
        * Machine-specific settings that won’t work for others

* `/ide` help you to install claude extension on your ide

* `/hooks` manager hooks - shell commands you can register to run during Claude Code processing.

  * It can be executed in many times:
  
    | `SessionStart`       | When a session begins or resumes                             |
    | -------------------- | ------------------------------------------------------------ |
    | `UserPromptSubmit`   | When you submit a prompt, before Claude processes it         |
    | `PreToolUse`         | Before a tool call executes. Can block it                    |
    | `PermissionRequest`  | When a permission dialog appears                             |
    | `PostToolUse`        | After a tool call succeeds                                   |
    | `PostToolUseFailure` | After a tool call fails                                      |
    | `Notification`       | When Claude Code sends a notification                        |
    | `SubagentStart`      | When a subagent is spawned                                   |
    | `SubagentStop`       | When a subagent finishes                                     |
    | `Stop`               | When Claude finishes responding                              |
    | `TeammateIdle`       | When an [agent team](https://code.claude.com/docs/en/agent-teams) teammate is about to go idle |
    | `TaskCompleted`      | When a task is being marked as completed                     |
    | `ConfigChange`       | When a configuration file changes during a session           |
    | `WorktreeCreate`     | When a worktree is being created via `--worktree` or `isolation: "worktree"`. Replaces default git behavior |
    | `WorktreeRemove`     | When a worktree is being removed, either at session exit or when a subagent finishes |
    | `PreCompact`         | Before context compaction                                    |
    | `SessionEnd`         | When a session terminates                                    |

* `/memory` manage memory

  * Just like settings, there are many `CLAUDE.MD` or `CLAUDE.local.md` for project memory, user memory or local project memory.

    * You can place multiple memory files within the same repository. The system aggregates all `CLAUDE.MD` files found along the directory path, starting from the repository root and continuing through each subfolder up to the current folder.

    * You can use hooks to switch the `CLAUDE.md` content, for example an script that append its contents based on key words form user input.

      ```json
      {
        "hooks": {
          "UserPromptSubmit": {
            "command": "./scripts/context-switcher.sh",
            "description": "Dynamically load relevant context based on user query"
          }
        }
      }
      ```

      ```sh
      #!/bin/bash
      # Analyze user input and load appropriate context
      user_input="$1"
      
      if [[ $user_input == *"database"* || $user_input == *"migration"* ]]; then
        echo "@./context/database-context.md" >> CLAUDE.md
      elif [[ $user_input == *"API"* || $user_input == *"endpoint"* ]]; then
        echo "@./context/api-context.md" >> CLAUDE.md
      elif [[ $user_input == *"frontend"* || $user_input == *"component"* ]]; then
        echo "@./context/frontend-context.md" >> CLAUDE.md
      fi
      ```

  * You can select which one you want to open.

  * You can type `#` with some info to include it on the memory, selecting which one.

* `/init` will create a new `CLAUDE.MD` file with codebase documentation.

* `/rewind` Claude automatically tracks file changes made on each prompt, and allow us to redo it.

  * If you press `esc` twice, it also will rewind.
  * it will enable you view the prompts you made, and select one to rewind.
  * It doesn't track changes made manually or by bash.
  * Think of checkpoints as "local undo" and git as "permanent history"

* You can create custom commands, eg:

  * create `.claude/commands/commit-code.md`

    * it can be project scoped, but also user scoped

    ```
    For example
    
    ---
    allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
    description: Create a git commit
    ---
    
    ## Context
    
    - Current git status: !`git status`
    - Current git diff (staged and unstaged changes): !`git diff HEAD`
    - Current branch: ! `git branch --show-current`
    - Recent commits: ! `git log --oneline -10`
    
    ## Your task
    
    Based on the above changes, create a single git commit.
    ```

  * run `/commit-code <main subject>` 

* You can connect Claude to an LSP, so it can do refactorings like rename much faster.

  * install the equivalent plugin `/plugin` searching by `lsp`