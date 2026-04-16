# backend-knowledge

Personal backend engineering knowledge base organized as Markdown notes, with project-local Codex skill support under `.codex/skills/`.

## Python Tooling

This repository uses a repo-local `pyenv` selection through `.python-version`:

```bash
codex-tools-3.13
```

The intended usage is:

```bash
pyenv exec python ...
```

### One-time setup

Create the global `pyenv` virtualenv if it does not exist yet:

```bash
pyenv virtualenv 3.13.11 codex-tools-3.13
```

Install the dependency used by Codex skill validation:

```bash
PYENV_VERSION=codex-tools-3.13 pyenv exec python -m pip install --upgrade pip
PYENV_VERSION=codex-tools-3.13 pyenv exec python -m pip install PyYAML
```

### Validate the Markdown link skill

```bash
pyenv exec python /Users/matheusmv/.codex/skills/.system/skill-creator/scripts/quick_validate.py .codex/skills/markdown-link-normalizer
pyenv exec python .codex/skills/markdown-link-normalizer/scripts/normalize_markdown_links.py Security --check
pyenv exec python .codex/skills/markdown-link-normalizer/scripts/validate_markdown_links.py Security
```
