# Javascript Miscellaneous 

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