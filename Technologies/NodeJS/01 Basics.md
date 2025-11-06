# Typescript

## What is TypeScript?

TypeScript is a programming language developed by Microsoft. It is a **superset of JavaScript**

* which means any valid JavaScript code is also valid TypeScript code.
* The main difference is that TypeScript adds **static typing** to the language.
  * With static typing, you can specify what type each variable should be (like string, number, boolean, etc.) before running the code.
* TypeScript then checks your code for type errors during development—**before** your code runs in the browser or Node.js.

## Why is TypeScript important?

JavaScript is a dynamically typed language, which means you can accidentally mix up different types (like strings and numbers) without the language warning you.

* These mistakes might only cause problems at runtime, which can make bugs harder to find and fix.
* TypeScript helps you catch these mistakes early, making your code more robust, easier to understand, and less prone to bugs.

### Example: JavaScript Typing Issue

Imagine you write this JavaScript function:

```javascript
function add(a, b) {
  return a + b;
}

console.log(add(2, 3));      // Output: 5
console.log(add('2', 3));    // Output: "23"
```

- The first call works as expected (`2 + 3` equals `5`).
- The second call **unexpectedly concatenates** the string `'2'` and the number `3`, resulting in `'23'` (a string!), not `5`.
- JavaScript doesn't warn you about this, and it might cause bugs in your program.

## How TypeScript Helps

If you write the same function in TypeScript:

```typescript
function add(a: number, b: number): number {
  return a + b;
}

add(2, 3);      // OK
add('2', 3);    // ERROR: Argument of type 'string' is not assignable to parameter of type 'number'.
```

- Here, `a: number` and `b: number` mean both parameters **must** be numbers.
- If you try to call `add('2', 3)`, TypeScript immediately gives you an error while you’re coding—before you even run your program.
- This helps catch bugs early and ensures your code behaves as you expect.