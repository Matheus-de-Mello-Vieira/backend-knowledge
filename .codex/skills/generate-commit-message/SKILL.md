---
name: generate-commit-message
description: Generate a Conventional Commits-style message from staged changes only. Use when the user asks for a commit message for already staged work.
---

# Commit Message Generator

## Purpose
Generate a commit message for staged git changes using a Conventional Commits–style format with a short title and optional bullet-point body.

## When To Use
Use this skill when:
- The user asks to generate a commit message
- The user provides a staged diff or summary of changes
- A properly formatted Conventional Commits message is required

Do not use this skill when:
- No staged changes are present
- The user is asking to stage files (`git add`)
- The user is asking for general git help unrelated to commit message generation

---

# Instructions

Your task is to generate a commit message for the user's **staged git changes**.

Follow all rules strictly.

## Guidelines

- Do not add advertisements or tool attribution
- Only generate the message for **staged files or changes**
- **Do not add files** using `git add`
- Assume the user has already staged the correct changes
- Only produce the commit message text

---

# Commit Format

```
<type>: <message title>

<bullet points summarizing what was updated>
```

The body is optional.

---

# Example Titles

```
feat(auth): add jwt login flow
fix(ui): handle null pointer in sidebar
refactor(api): split user controller logic
docs(readme): add usage section
```

---

# Example With Body

```
feat(auth): add jwt login flow

- implement jwt token validation logic
- add documentation for the validation component
```

---

# Rules

* The **title must be lowercase**
* **No period at the end of the title**
* The title must be **50 characters or fewer**
* The title should clearly summarize the change
* Use the body to explain **why**, not just **what**
* Bullet points must be **concise and high-level**

---

# Avoid

* Vague titles such as:

  * `update`
  * `fix stuff`
* Overly long titles
* Excessive technical detail in bullet points

---

# Allowed Types

| Type     | Description                           |
| -------- | ------------------------------------- |
| feat     | New feature                           |
| fix      | Bug fix                               |
| chore    | Maintenance (tooling, dependencies)   |
| docs     | Documentation changes                 |
| refactor | Code restructure (no behavior change) |
| test     | Adding or refactoring tests           |
| style    | Code formatting (no logic change)     |
| perf     | Performance improvements              |

---

# Output Constraints

* Output **only the commit message**
* Do **not** include explanations
* Do **not** include markdown commentary
* Do **not** wrap the output in code blocks
* Ensure:

  * title ≤ 50 characters
  * title is lowercase
  * no trailing period

If a body is unnecessary, return **only the title line**.
