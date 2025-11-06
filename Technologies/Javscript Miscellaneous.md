# Javascript Miscellaneous

## var, let and const

When working with variables in JavaScript, you have three main ways to declare them: `var`, `let`, and `const`. While all three are used to create variables, they differ in how they behave with scope, re-declaration, hoisting, and re-assignment.

Understanding these differences is important because choosing the right keyword can help you avoid bugs and make your code more predictable. Below, you’ll find a detailed explanation of how each one works, along with examples.

### 1. `var`

-   **Scope**: Function-scoped (or globally scoped if declared outside a function). It does not respect block scope (`{}`).

-   **Re-declaration**: Allowed in the same scope.

-   **Hoisting**: Variables declared with `var` are hoisted to the top of their scope and initialized with `undefined`.

-   **Example**:

    ```javascript
    function testVar() {
      if (true) {
        var x = 10;
      }
      console.log(x); // 10 (accessible outside the block)
    }
    ```

### 2. `let`

-   **Scope**: Block-scoped (limited to `{}` where it is defined).

-   **Re-declaration**: Not allowed in the same scope (but can be reassigned).

-   **Hoisting**: Hoisted but not initialized → accessing before declaration gives a `ReferenceError` (this is called the Temporal Dead Zone).

-   **Example**:

    ```javascript
    function testLet() {
      if (true) {
        let y = 20;
        console.log(y); // 20
      }
      console.log(y); // ReferenceError (block-scoped)
    }
    ```

### 3. `const`

-   **Scope**: Block-scoped (like `let`).

-   **Re-declaration**: Not allowed.

-   **Re-assignment**: Not allowed → value must be assigned at declaration.

-   **Hoisting**: Hoisted but not initialized (same behavior as `let`).

-   **Mutability**: The variable binding is constant, but objects and arrays can still be mutated.

-   **Example**:

    ```javascript
    const z = 30;
    // z = 40; // Error: Assignment to constant variable
    
    const obj = { a: 1 };
    obj.a = 2; // Allowed: object properties can change
    ```

### Best pratices

1)   **Keep scope as small as possible**
      Always declare variables in the narrowest scope where they are needed. This makes your code cleaner, easier to debug, and prevents unintended side effects.
2)   **Prefer `const` by default**
      Use `const` whenever possible. This makes your variables immutable by default, reducing the chance of accidental reassignments. It also makes your code easier to read since other developers know the value won’t change.
3)   **Use `let` only when reassignment is needed**
      If you know the variable will change its value (for example, in counters, loops, or reassignments), then `let` is the right choice. This gives flexibility while still keeping the safety of block scope.
4)   **Avoid `var`**
      `var` is considered legacy and should generally be avoided in modern code. Its function scope and hoisting behavior can lead to unexpected bugs, especially in larger projects. Stick to `let` and `const` instead.
5)   **Be cautious with `const` and objects/arrays**
      Remember that `const` only prevents reassignment of the variable itself, not changes to the contents of objects or arrays. If you need true immutability, consider using techniques like `Object.freeze()` or libraries designed for immutable data.

## Spread Operator (...)

### 1. **Expanding Arrays**

You can use it to expand elements of an array where zero or more arguments are expected.

```javascript
const numbers = [1, 2, 3];
console.log(...numbers); 
// Output: 1 2 3
```

Example with functions:

```javascript
function sum(a, b, c) {
  return a + b + c;
}
const nums = [5, 10, 15];
console.log(sum(...nums)); 
// Output: 30
```

------

### 2. **Copying Arrays**

Instead of `slice()`, you can create a shallow copy:

```javascript
const original = [1, 2, 3];
const copy = [...original];
copy.push(4);

console.log(original); // [1, 2, 3]
console.log(copy);     // [1, 2, 3, 4]
```

------

### 3. **Merging Arrays**

```javascript
const a = [1, 2];
const b = [3, 4];
const merged = [...a, ...b];
console.log(merged); // [1, 2, 3, 4]
```

------

### 4. **Working with Strings**

Since strings are iterable, spread works on them too:

```javascript
const word = "hello";
const letters = [...word];
console.log(letters); // ['h', 'e', 'l', 'l', 'o']
```

------

### 5. **Objects**

You can also use it for shallow copies and merging objects:

```javascript
const obj1 = { x: 1, y: 2 };
const obj2 = { y: 3, z: 4 };

const merged = { ...obj1, ...obj2 };
console.log(merged); // { x: 1, y: 3, z: 4 }
```

*   If properties collide, later ones overwrite earlier ones.

## Difference Between Spread and Rest (`...`)

They look the same (`...`), but behave differently depending on context:

-   **Spread**: expands values

    ```javascript
    const arr = [1, 2, 3];
    console.log(Math.max(...arr)); // 3
    ```

-   **Rest**: collects values

    ```javascript
    function printAll(...args) {
      console.log(args);
    }
    printAll(1, 2, 3); // [1, 2, 3]
    ```

## Array and Object Destructuring

```javascript
const hobbies = ['a', 'b']

const [hobby1, hobby2] = hobbies;

console.log(hobby1) // a
console.log(hobby2) // b
```

*   You can extract less variables than the size of array

    ```javascript
    const hobbies = ['a', 'b', 'c']
    
    const [hobby1, hobby2] = hobbies;
    
    console.log(hobby1) // a
    console.log(hobby2) // b
    ```

*   You can try extract more variables than the size of array, the surplus will be attributed `undefined`

    ```javascript
    const hobbies = ['a', 'b']
    
    const [hobby1, hobby2, hobby3] = hobbies;
    
    console.log(hobby1) // a
    console.log(hobby2) // b
    console.log(hobby3) // undefined
    ```

*   You can use rest parameter to get the rest as array

    ```javascript
    const hobbies = ['a', 'b', 'c', 'd', 'e']
    
    const [hobby1, hobby2, ...remainingHobbies] = hobbies;
    
    console.log(hobby1) // a 
    console.log(hobby2) // b
    console.log(remainingHobbies) // [ 'c', 'd', 'e' ]
    ```

You can deconstruction object too:

```javascript
const user = { id: 42, name: "Rafa", role: "admin" };

// Basic
const { id, name } = user;     // id=42, name="Rafa"

// Rename on the fly
const { role: userRole } = user; // userRole="admin"

// With defaults (only used when value is === undefined)
const { email = "n/a" } = user;  // email="n/a"
```

*   **Nested destructuring**: Grab properties inside properties in one go.

    ```javascript
    const settings = {
      theme: { mode: "dark", contrast: "high" },
      flags: { beta: true }
    };
    
    const {
      theme: { mode, contrast },
      flags: { beta }
    } = settings;
    // mode="dark", contrast="high", beta=true
    ```

*   **Rest properties**: Collect “the rest” of the fields.

    ```javascript
    const { id, ...rest } = { id: 1, a: 2, b: 3 };
    // id=1, rest={ a:2, b:3 }
    ```

*   **Function parameters**: Destructure right in the parameter list—great for options objects.

    ```javascript
    function createUser({ name, email = "n/a", role: r = "user" }) {
      return `${name} <${email}> [${r}]`;
    }
    
    createUser({ name: "Rafa", role: "admin" });
    ```

*   **Combining with arrays**: You can mix object + array destructuring when data gets nested.

    ```javascript
    const resp = {
      meta: { page: 1 },
      data: [{ id: 7, title: "Hello" }, { id: 8, title: "World" }]
    };
    
    const {
      meta: { page },
      data: [first, second]
    } = resp;
    // page=1, first={id:7,...}, second={id:8,...}
    
    const { data: [{ title: firstTitle }] } = resp; // firstTitle="Hello"
    ```

*   **Computed property names (read, not set)**: You can destructure using a dynamic key (from another variable).

    ```javascript
    const key = "name";
    const profile = { name: "Ada", age: 36 };
    
    const { [key]: displayName } = profile; // displayName="Ada"
    ```

## Arrays and Memory in JavaScript

### 1) Dynamic Resizing of Arrays

In JavaScript, a normal `Array` is not a fixed-size block like in C.
 It behaves like a **dynamic array**:

-   When you create an array and push elements, the engine allocates some extra capacity in memory.
-   If you keep adding elements and exceed the capacity, the engine:
    1.  Allocates a larger block of memory (often about double the old size).
    2.  Copies the old elements into the new block.
    3.  Frees the old block.
-   This means appending is **amortized O(1)** (usually fast, but occasionally costly when resizing happens).

Example:

```
let arr = [];
arr.push(1);
arr.push(2);
// Behind the scenes: may resize from capacity 2 → 4 → 8 → 16 …
```

### 2) Arrays Can Become Hash Maps

JavaScript arrays are really objects with special optimizations for **dense integer keys**.
 If you start using them like sparse arrays, the engine may switch to a **hash map representation**:

```
let arr = [];
arr[0] = "a";
arr[1000000] = "b"; // big hole
```

-   The engine sees that the array is no longer dense.
-   Instead of keeping 1 million “holes”, it switches to a hash map (dictionary-like structure).
-   This makes memory usage reasonable, but random access can get slower.

### 3) Pre-allocating with `new Array(length)`

You can give the engine a **hint** by specifying an initial length:

```
let arr = new Array(1000);
```

-   This creates an array with a `length` of 1000.
-   The slots are *empty* (not even `undefined`, just uninitialized “holes”).
-   If you fill the array densely (`arr[i] = ...`), the engine can optimize it better.
-   But if you exceed 1000, it will still resize dynamically.

### 4) Fixed-Size Memory with Typed Arrays

If you want something closer to C-style arrays, use **Typed Arrays**.
 They are views over a raw `ArrayBuffer` and have fixed length.

Example:

```
let arr = new Float64Array(1000);
arr[0] = 42.5;
```

-   `Float64Array(1000)` allocates space for 1000 doubles (64-bit floats).
-   The length is fixed — you cannot push or resize.
-   Data is stored in contiguous memory, which is fast and predictable.

#### Common Typed Array Types

-   `Int8Array` → 8-bit signed integers
-   `Uint8Array` → 8-bit unsigned integers
-   `Uint8ClampedArray` → 8-bit unsigned integers, clamped on overflow
-   `Int16Array` → 16-bit signed integers
-   `Uint16Array` → 16-bit unsigned integers
-   `Int32Array` → 32-bit signed integers
-   `Uint32Array` → 32-bit unsigned integers
-   `Float32Array` → 32-bit floating point
-   `Float64Array` → 64-bit floating point
-   `BigInt64Array` → 64-bit signed integers (`BigInt`)
-   `BigUint64Array` → 64-bit unsigned integers (`BigInt`)

These are extremely useful for numerical computing, graphics, or when you want **low-level control** over memory.

## Optional Chaining

The optional chaining operator (`?.`) safely accesses a property only if the variable is not `null` or `undefined`.

So:

```javascript
variable?.value
```

is equivalent to:

```javascript
(variable != null ? variable.value : undefined)
```

#  Fallback Values in JavaScript

### `variable || 'value'`

-   Logical OR
-   Returns `'value'` if `variable` is falsy.
-   In JavaScript, falsy values are:
     `false`, `0`, `''` (empty string), `null`, `undefined`, `NaN`.

 Example:

```javascript
let a = null;
console.log(a || 'fallback'); // "fallback"

let b = 0;
console.log(b || 'fallback'); // "fallback" (0 is falsy)

let c = '';
console.log(c || 'fallback'); // "fallback" (empty string is falsy)
```

### `variable ?? 'value'`

-   Nullish Coalescing Operator
-   Returns `'value'` only if `variable` is `null` or `undefined`.
-   If `variable` is any other value (including `false`, `0`, `''`, `NaN`), it does not trigger the fallback.

Example:

```
let a = null;
console.log(a ?? 'fallback'); // "fallback"

let b = 0;
console.log(b ?? 'fallback'); // 0 (not fallback)

let c = '';
console.log(c ?? 'fallback'); // "" (not fallback)
```

## Symbols

*   A Symbol is a primitive type introduced in ES6 (ES2015).
*   It’s used to create unique identifiers — values that are guaranteed never to clash with any other value.

You create one like this:

```javascript
const a = Symbol('my-key');
const b = Symbol('my-key');
```

Even though both have the same description `'my-key'`,

*   they are different, unique values:

    ```javascript
    console.log(a === b); // false
    ```

## `typeof`

You can identity the type of a variable using `typeof` at runtime

```typescript
const userName = "Max";

console.log(typeof userName) // string
```