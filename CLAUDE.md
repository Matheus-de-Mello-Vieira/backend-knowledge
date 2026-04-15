# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this knowledge repository.

## Repository Overview

This is a personal backend engineering knowledge base structured as an Obsidian vault. It contains study notes, concepts, and reference materials covering backend technologies, system design patterns, security, networking, and related engineering topics.

## Note Structure

- **Technologies/**: Study notes on specific technologies and frameworks
  - **NodeJS/**: Node.js fundamentals, Express framework, authentication methods, database integration
  - **Golang/**: Go language concepts and patterns
  - **Typescript/**: TypeScript basics and type system
  - **NGINX/**: Web server configuration and usage
- **Backend Engineering/**: System design and engineering pattern notes
  - Communication patterns (request-response, messaging, etc.)
  - Execution models (synchronous, asynchronous, concurrent)
  - Performance analysis and troubleshooting approaches
- **Security/**: Information security concepts and best practices
- **Networking/**: Network protocols, connection management, infrastructure concepts
- **Web APIs/**: API design patterns including REST and GraphQL
- **Cache/**: Caching strategies and Redis usage patterns
- **Operating Systems/**: OS fundamentals and system-level concepts
- **AI Engineering/**: Modern AI development patterns and RAG implementations

## Key Documented Concepts

### Design Patterns
The notes document several important patterns:
- **Repository Pattern**: Data access layer abstraction with standard CRUD operations
- **Slug Generation**: URL-safe identifier creation with Unicode normalization
- **Resilience Engineering**: System availability principles using MTTF/MTTR calculations

### Core Topics
- **HTTP Headers**: Reference material for common HTTP headers and their usage
- **JSONL**: JSON Lines format specifications and use cases
- **Resilience**: Comprehensive coverage of failure types and recovery strategies

## Note Organization

- Numbered prefixes indicate learning sequence (01, 02, etc.)
- "99 Misc" folders contain supplementary and reference materials
- Cross-references between related concepts throughout the notes
- Code examples primarily in TypeScript/JavaScript with some other languages
- Theoretical concepts paired with practical implementation details

## Working with These Notes

When exploring concepts:
- Follow the numbered sequence within each topic for structured learning
- Check cross-references in core files like **Patterns.md** and **Resilience.md**
- Look for related concepts in parallel directories (e.g., security implications of networking topics)
- The NodeJS section contains the most practical implementation examples
- Use the .obsidian configuration for proper link management and navigation

## Obsidian Configuration

- Configured for Markdown links with automatic updates
- Git integration for version control of note changes
- Terminal plugin available for any command-line operations needed

This is a study and reference repository focused on backend engineering knowledge rather than executable code.

## Writing Patterns and Style Guide

### Structure and Organization
- **Clear hierarchical headings**: Uses `#` for main topics, `##` for sections, `###` for subsections
- **Numbered sequencing**: Files prefixed with numbers (01, 02, etc.) indicate learning progression
- **"99 Misc" convention**: Miscellaneous and supplementary content organized under "99" prefix

### Content Formatting
- **Definition-first approach**: Concepts start with clear, bold definitions followed by explanations
- **Bullet-driven explanations**: Heavy use of bullet points for breaking down complex concepts
- **Code-example heavy**: Most technical concepts include practical code examples in fenced blocks
- **Cross-referencing**: Liberal use of markdown links to related concepts, often in `[concept](../path/file.md)` format

### Code and Technical Content
- **Multi-language examples**: Primarily JavaScript/TypeScript, with examples in other languages as needed
- **Inline code emphasis**: Important terms, functions, and parameters wrapped in backticks
- **Command blocks**: Shell commands and installation instructions in dedicated code blocks
- **API patterns**: Consistent format showing request/response examples and HTTP methods

### Explanatory Style
- **Problem-solution format**: Many sections start with "To solve this..." or "When working with..."
- **Progressive complexity**: Simple examples first, followed by advanced use cases
- **Practical focus**: Emphasis on "how to" rather than just theory
- **Real-world context**: Examples often reference actual APIs (LinkedIn, Meetup) and practical scenarios

### Visual Elements
- **Mathematical notation**: Uses LaTeX-style math formatting for formulas (e.g., availability calculations)
- **Mermaid diagrams**: Complex system relationships illustrated with flowcharts
- **Tables**: Comparison tables for different approaches or technologies
- **Emphasized terminology**: Key terms often in **bold** for easy scanning

### Voice and Tone
- **Direct and instructional**: Uses imperative voice for actionable steps
- **Question-driven analysis**: Security sections use "Is this...?" pattern for threat modeling
- **Conversational explanations**: Complex topics broken down with analogies and practical examples
- **Assumption of learning context**: Written for someone actively studying backend engineering

### Cross-Reference Patterns
- **Parenthetical links**: Related concepts linked in parentheses after key terms
- **Directory-aware linking**: Links follow the actual file structure with relative paths
- **Topic clustering**: Related concepts grouped together with extensive internal linking