# Typescript

## What is TypeScript?

- TypeScript is a programming language created by Microsoft.
- It is a superset of JavaScript—every JavaScript program is also valid TypeScript.
- Adds static typing to JavaScript.
  - Static typing means you declare what type a variable or function parameter should be (like string, number, or boolean) before running your code.
  - The types  (string, number, boolean, etc.)  are checked while you’re writing code, not at runtime.
  - Checks for type errors during development, not at runtime.

## Why is TypeScript important?

- JavaScript is dynamically typed—types can change, and mistakes are only found when you run the code.
  - Mixing up types (like strings and numbers) can cause hard-to-find bugs.
- TypeScript catches type mistakes early, during coding.
  - Makes code more robust, readable, and easier to maintain.

## Example: JavaScript Typing Issue

```javascript
function add(a, b) {
  return a + b;
}

console.log(add(2, 3));      // Output: 5
console.log(add('2', 3));    // Output: "23"
```

- `add(2, 3)` works: `2 + 3` equals `5`.
- `add('2', 3)` does not work as expected: outputs `"23"` instead of `5`.
- JavaScript does not warn about this type mix-up.

### How TypeScript Helps

```typescript
function add(a: number, b: number): number {
  return a + b;
}

add(2, 3);      // OK
add('2', 3);    // ERROR: Argument of type 'string' is not assignable to parameter of type 'number'.
```

- TypeScript enforces that both `a` and `b` must be numbers.
- If you try `add('2', 3)`, TypeScript gives an error immediately.
- Prevents bugs before running the code.

## Installation

You can install typescript (locally or globally) using npm

### Global install

```
npm install -g typescript
tsc -v
```

-   This makes `tsc` available everywhere on your system.
-   Useful for quick experiments or compiling small scripts without setting up a project.
-   But your global version can get out of sync with the version your project expects.

### Local (per-project) install

```
npm install -D typescript
```

-   Adds TypeScript to your `devDependencies`.

-   Ensures the whole team and your CI build use the same version.

-   You run it via:

    ```
    npx tsc -v
    ```

    or through a build script in `package.json`.

### Common Setup

Many devs install both locally and globally:

-   Install globally for convenience (`npm i -g typescript`), so you can run `tsc` quickly.
-   Also install locally in each project (`npm i -D typescript`) to lock the version.

## Execution

You can compile the typescript code into javascript using `tsc`

# Naming Conventions

-   `camelCase` → variables, functions, methods, properties
-   `PascalCase` → classes, interfaces, types, enums
-   `UPPER_SNAKE_CASE` → global constants
-   `T, U, V (or descriptive)` → generics
-   `kebab-case / camelCase` → file names