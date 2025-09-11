# Quality-of-Life Development Tools for JavaScript Projects

This guide explains a set of development dependencies that help maintain code quality, consistency, and readability in JavaScript and Node.js projects. It also includes setup instructions so you can integrate them quickly into any project.

In programming slang, “quality-of-life tools” doesn’t literally mean “life” — it’s shorthand for “developer quality-of-life,” meaning tools that make your day-to-day workflow easier, smoother, and less frustrating.
* It’s borrowed from gaming, where “quality-of-life improvements” are small changes that don’t change the core game but make playing it more pleasant (like better menus, faster load times, or auto-saving).

## Tools

### ESLint

**Purpose:** ESLint is a static analysis tool for identifying and fixing problems in JavaScript and TypeScript code. It enforces coding standards, catches potential bugs, and can automatically fix certain issues.

You can configure ESLint to suit your project’s style and requirements, or extend it with additional plugins and rule sets.

#### @eslint/js

This package provides the official set of recommended ESLint rules maintained by the ESLint team. It acts as a ready-made base configuration so you can start linting immediately without manually defining all rules from scratch.

Example usage in a config file:

```js
const js = require('@eslint/js');
module.exports = [js.configs.recommended];
```

#### eslint-plugin-unused-imports

This ESLint plugin adds rules for detecting and automatically removing unused imports and variables. It helps keep your codebase free from unnecessary statements that can clutter files and reduce readability.

Example rule configuration:

```js
"rules": {
  "no-unused-vars": "off",
  "unused-imports/no-unused-imports": "error",
  "unused-imports/no-unused-vars": [
    "error",
    { "vars": "all", "args": "after-used" }
  ]
}
```
### Prettier

**Purpose:** Prettier is an opinionated code formatter that ensures all code in a project follows a consistent style. It automatically formats files according to defined rules (e.g., indentation, quotes, semicolons) without requiring manual intervention.

By integrating Prettier into a project, developers can avoid style debates and focus on functionality.

Example usage:

```bash
prettier --write .
```

### alex

**Purpose:** alex checks natural language text in your codebase—such as documentation, comments, and README files—for potentially insensitive, inconsiderate, or unclear language.

It encourages more inclusive writing by highlighting terms that may be problematic and suggesting alternatives.

Example usage:

```bash
alex README.md
```

### markdownlint-cli

**Purpose:** markdownlint-cli is a command-line tool for enforcing Markdown style rules. It checks for issues such as inconsistent heading levels, incorrect list formatting, and trailing spaces in `.md` files.

This helps maintain clean, consistent documentation across the project.

Example usage:

```bash
markdownlint "**/*.md"
```

### depcheck

**Purpose:** depcheck analyzes a project’s source code to find unused npm dependencies and missing imports. This keeps `package.json` lean and ensures that you’re not installing packages you don’t actually need.

Example usage:

```bash
depcheck
```

### globals

**Purpose:** globals is a library that provides lists of predefined global variables for various environments such as Node.js, browsers, and workers.

It’s commonly used in ESLint configurations to prevent false warnings about undefined variables like `require`, `module`, or `__dirname` when working in Node.js.

Example usage in ESLint config:

```js
const globals = require('globals');
languageOptions: {
  globals: { ...globals.node }
}
```

## Setup

### Installation

You can install all these tools in one command:

```bash
npm install --save-dev eslint @eslint/js eslint-plugin-unused-imports prettier alex markdownlint-cli depcheck globals
```

### ESLint Configuration (eslint.config.cjs)

Place this file in your project root as `eslint.config.cjs`:

```js
const js = require('@eslint/js');
const pluginUnusedImports = require('eslint-plugin-unused-imports');
const globals = require('globals');

module.exports = [
  { ignores: ['node_modules', 'dist', 'build', 'coverage'] },

  js.configs.recommended,

  {
    files: ['**/*.js'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'script', // Change to 'module' if using ES modules (import/export)
      globals: { ...globals.node },
    },
    plugins: {
      'unused-imports': pluginUnusedImports,
    },
    rules: {
      'no-unused-vars': 'off',
      'unused-imports/no-unused-imports': 'error',
      'unused-imports/no-unused-vars': [
        'error',
        {
          vars: 'all',
          varsIgnorePattern: '^_',
          args: 'after-used',
          argsIgnorePattern: '^_',
        },
      ],
    },
  },
];
```

- Use `"sourceType": "script"` for CommonJS (`require` / `module.exports`).
- Switch to `"sourceType": "module"` for ES Modules (`import` / `export`).

### package.json Scripts

Add these scripts to your `package.json` to run the tools easily:

```json
{
  "lint:js": "eslint src --fix",
  "lint:md": "markdownlint '**/*.md'",
  "lint:spell": "cspell '**'",
  "lint:grammar": "alex --config .alexrc.json 'src/**/*.js'",
  "lint:format": "prettier --write .",
  "lint:unused-deps": "depcheck",
  "lint:all": "npm run lint:js && npm run lint:md && npm run lint:spell && npm run lint:grammar && npm run lint:unused-deps && npm run lint:format"
}
```