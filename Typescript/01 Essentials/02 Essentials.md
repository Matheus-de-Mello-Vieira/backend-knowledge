# Essentials

## Primitive types

*   `number`:  for all numeric values (integers, floats, hex, binary, octal).
   
    ```typescript
    let age: number = 25;
    ```

   1.  There is no dedicated integer type, but you can check if a number is a integer using `Number.isInteger`.
   
*   `string`: for textual data.

    ```typescript
    let name: string = "Alice";
    ```

*   `boolean`: for logical values (`true` or `false`).

    ```typescript
    let isActive: boolean = true;
    ```

*   `null`: represents an intentional absence of any value.

    ```typescript
    let emptyValue: null = null;
    ```

*   `undefined`:  indicates a variable that has been declared but not assigned.

    ```typescript
    let notAssigned: undefined = undefined;
    ```

*   `symbol`: used for unique and immutable identifiers.

    ```typescript
    let sym: symbol = Symbol("id");
    ```

*   `bigint`: for arbitrarily large integers.

    ```typescript
    let big: bigint = 9007199254740991n;
    ```

## Variable declarations

On typescript, you can optionally explicitly declare the type of variable.

```typescript
let userName: string;

userName = "max";
```

*   Notice that the concept of typing already exists on Javascript, for examplethe code:

    ```javascript
    let userName = "Max";
    
    console.log(typeof userName)
    ```

    Will print `string`

*   You can omit the type declaration if the value is assign ton the variable declaration.

    ```typescript
    let userAge = 38;
    
    userAge = "34"; // Error: Type 'string' is not assignable to type 'number'.
    ```

    *   It is considered good practice to avoid unnecessary explicit typing.

## Assigning types to function parameters

You can explicitly assign the type, of lean on default value type inference.

```javascript
function add(a: number, b = 5) {
    return a + b;
}
```

*   In this case:

    ```typescript
    add(10);      // ✅ OK
    add("10");    // Error
    add(10, 6);   // ✅ OK
    add(10, "4"); // Error
    ```

    

## Flexible types

The `any` allows anything:

```javascript
let age: any = 36;

age = "37"   // ✅ OK
age = false; // ✅ OK
age = {};    // ✅ OK
age = [];    // ✅ OK
```

Notice that the using of the `any` type defeats the propose of using typescript. So you should only use it as last resource.

Instead of `any`, consider using `Union` first.

```javascript
let age: string | number | boolean = 36;

age = "36";      // ✅ OK
age = false;     // ✅ OK
age = {};        // ❌ Error: '{}' is not assignable to type 'string | number | boolean'
age = [];        // ❌ Error: 'any[]' is not assignable to type 'string | number | boolean'
```

## Arrays

Beyond [Javascript Arrays](../../Javscript Miscellaneous.md#Arrays-and-Memory-in-JavaScript) features, typescript allows you enforce typing:

```javascript
let hobbies = ["Sports", "Cooking"]

hobbies.push(25); // ❌ Error: Argument of type 'number' is not assignable to parameter of type 'string'
```

*   Or declare the type explicitlly

    ```javascript
    let hobbies: string[] = ["Sports", "Cooking"]
    ```

    *   ```javascript
        let users: (string | number)[];
        
        users = [1, "Max"];     // ✅ OK
        users = [5, 1];         // ✅ OK
        users = ["Max", "Anna"] // ✅ OK
        ```

    *   ```javascript
        let users: Array<string | number>;
        ```

### Tuples

Define a presized array, with type for each element:

```javascript
let possibleResults: [number, number];
possibleResults = [1, -1];          // ✅ OK
possibleResults = [5, 10, 12];      // ❌ Error: tuple type '[number, number]' only allows 2 elements
```

*   ```javascript
    let userStatus: [string, boolean];
    
    userStatus = ["Alice", true];   // ✅ OK
    userStatus = ["Bob", false];    // ✅ OK
    userStatus = ["Charlie", 42];   // ❌ Error, second value must be boolean
    ```

### Object Types

You can define the type of elements in object

```typescript
let user: {
  name: string;
  age: number | string;
  hobbies: string[];
  role: {
    description: string;
    id: number;
  };
} = {
  name: "Max",
  age: 38,
  hobbies: ["Sports", "Cooking"],
  role: {
    description: "admin",
    id: 5,
  },
};
```

-   If you have a small, fixed object shape, writing it out manually is fine.
-   If you have a union of keys (especially reused or evolving), `Record` with literal keys is better: it’s concise, automatically stays in sync with the union, and scales much better.

### "any non-nullish value" type

*   `{}` is the non-nullish top type.
*   It allows any value except `null` and `undefined`.
*   So you can assign strings, numbers, booleans, arrays, functions, and objects to it.

```typescript
let val: {};

val = "some text";  // ✅ OK: string is a non-null object type
val = 1;            // ✅ OK: number is a non-null object type
val = null;         // ❌ Error: Type 'null' is not assignable to type '{}'
val = undefined;    // ❌ Error: Type 'undefined' is not assignable to type '{}'
val = [];           // ✅ OK: arrays are also objects
val = { a: 1 };     // ✅ OK: plain objects work too
```

### Record type

`Record<Keys, Type>` constructs a type with a set of properties `Keys`, where each property is of type `Type`.

-   `Keys` must be a union of string, number, or symbol literal types.
-   `Type` is the type of the values.

```typescript
// A record with string keys and number values
let scores: Record<string, number>;

scores = {
  Alice: 10,
  Bob: 15,
  Charlie: 20,
};

scores = {
  Alice: "ten",  // ❌ Error: Type 'string' is not assignable to type 'number'
};
```

*   It is the same of

    ```typescript
    let scores: { [probs: string]: number };
    ```

    

#### With literal keys

You can restrict the allowed keys:

```typescript
type Role = "admin" | "editor" | "viewer";

let permissions: Record<Role, boolean>;

permissions = {
  admin: true,
  editor: false,
  viewer: true,
};

permissions = {
  admin: true,
  editor: true,
  // ❌ Error: Property 'viewer' is missing
};
```

## Enums

```typescript
enum Role {
    Admin,
    Editor,
    Guest
}

let userRole: Role = Role.Admin;
userRole = Role.Guest;
```

*   The default are numeric enum, starting with 0, so the above code is equivalent to:

    ```typescript
    enum Role {
        Admin = 0,
        Editor = 1,
        Guest = 2
    }
    ```

*   For numeric enums, you can access enum members by name, and otherwise:

    ```typescript
    enum Role {
        Admin,   // 0
        Editor,  // 1
        Guest    // 2
    }
    
    let userRole: Role;
    
    // Assigning by enum member
    userRole = Role.Admin;
    console.log(userRole); // 0
    
    // Assigning directly by number
    userRole = 2;
    console.log(userRole); // 2 (which corresponds to Role.Guest)
    
    // Accessing enum names by number
    console.log(Role[0]); // "Admin"
    console.log(Role[1]); // "Editor"
    console.log(Role[2]); // "Guest"
    ```

*   You can overide the values of enum:

    ```typescript
    enum Role {
        Admin = "Admin",
        Editor = "Editor",
        Guest = "Guest"
    }
    ```

    *   The acces is also bidirectional:

        ```typescript
        let userRole: Role;
        
        // Assigning by enum member
        userRole = Role.Admin;
        console.log(userRole); // 👉 "Admin"
        
        // Assigning directly by literal string
        userRole = "Guest";
        console.log(userRole); // 👉 "Guest"
        
        // Accessing values directly
        console.log(Role.Admin);  // 👉 "Admin"
        console.log(Role.Editor); // 👉 "Editor"
        console.log(Role.Guest);  // 👉 "Guest"
        ```

## Literal

You can assign a type that allows only a predefined set of strings

```typescript
let userRole: 'admin' | 'editor' | 'guest' = 'admin';

userRole = 'editor';    // ✅ OK: "editor" is part of the union
userRole = 'guest';     // ✅ OK: "guest" is part of the union
userRole = 'admin';     // ✅ OK: "admin" is part of the union

userRole = 'superadmin'; // ❌ Error: Type '"superadmin"' is not assignable to type '"admin" | "editor" | "guest"'
userRole = '';           // ❌ Error: Type '""' is not assignable to type '"admin" | "editor" | "guest"'
```

It is far more popular than enum.

It allows any type, not only strings:

```typescript
let possibleResults: [-1 | 1, -1 | 1];

possibleResults = [1, -1];   // ✅ OK: both entries are either -1 or 1
possibleResults = [-1, 1];   // ✅ OK: both entries are either -1 or 1
possibleResults = [1, 1];    // ✅ OK
possibleResults = [-1, -1];  // ✅ OK

possibleResults = [0, 1];    // ❌ Error: Type '0' is not assignable to type '-1 | 1'
possibleResults = [1];       // ❌ Error: Source has 1 element(s) but target requires 2
possibleResults = [1, -1, 1];// ❌ Error: Source has 3 element(s) but target requires 2
```

## Type Aliases

You can create a custom type under a name:

```typescript
type Role = 'admin', 'editor', 'guest', 'reader'
```

You can use a custom type to declare others custom types:

```typescript
type Role = 'admin' | 'editor' | 'guest' | 'reader';
type User = {
    name: string,
    age: number;
    role: Role;
    permissions: string[];
}
```

## Function Return Value Types

```typescript
function add(a: number, b: number): number {
  return a + b;
}
```

*   But it can be infered in most cases.

### Void type

You can explicitlly define as `void`, but normally it can is infered:

```typescript
function log(message: string): void {
  console.log(message);
}
```

### Never type

It means that this function never completes. 

*   this is different from `void` that means that the function completes e returns nothing.

```typescript
function logAndThrow(errorMessage: string): never {
    console.log(errorMessage);
    throw new Error(errorMessage);
}
```

## Function as type

You can be generic with:
```typescript
function performJob(cb: Function) {
    // ...
    cb();
}
```

But to be more specifc you can:
*  specify the return type
  ```typescript
  function performJob(cb: () => void) ...
  ```
  
*   specify the parameters types

    ```  typescript
    function performJob(cb: (m: string, m1: number) => void) ...
    ```

For example:

```typescript
type User = {
    name: string;
    age: number;
    greet: () => string;
}
```

## Special types (null and undefield)

```typescript
let a: null;
```

*   It is userful to allow `null` out of other types

    ```typescript
    let a: null | string;
    ```
*   Same ideia applies to `undefield`
   
    ```typescript
    let a: undefield;
    ```

## Forced "not null" (! mark)

You can convince the typescript that a value isn't null (even if its type is null), by appending it a `!`.

```typescript
const nullable = document.getElementById('user-name'); // HTMLElement | null
const nonNullable = nullable!; // HTMLElement
```

*  Equivalently:

    ```typescript
    const nonNullable = document.getElementById('user-name')!; // HTMLElement
    ```

It will only silence the typescript about a potential `null` value, it doesn't check if it is true. So it can be dangerous.

*   Also consider using [optional chaining](../../Javscript Miscellaneous.md#Optional-Chaining) instead

## Type casting

You can use a type assertion (`as`) to tell the compiler that a value should be treated as a subtype or supertype of its current static type.

*   If there is no subtype/supertype relationship, the assertion will be rejected (unless you go through `unknown`/`any` as an escape hatch).

For example

```typescript
const htmlElement = document.getElementById('user-name'); // HTMLElement | null
const htmlInputElement = htmlElement as HTMLInputElement; // HTMLInputElement
```

*   Equivalently

    ```typescript
    const htmlInputElement = document.getElementById('user-name') as HTMLInputElement
    ```

*   Notice that the `null` part of the union was ignored, because TypeScript only requires the target type to be a subtype or supertype of at least one member of the union.

    ``` typescript
    class Car { ... }
    class House { ... }
    class SportsCar extends Car { ... }
    
    const thing: Car | House = new House();
    const fastCar = thing as SportsCar; // ✅ OK
    ```

*   You can't do it to a type that isn't subclass:

    ```typescript
    document.getElementById('user-name') as number; // ERROR: Conversion of type 'HTMLElement | null' to type 'number' may be a mistake because neither type sufficiently overlaps with the other. If this was intentional, convert the expression to 'unknown' first.
    ```

*   be careful using this feature, because you may be wrong, and the typescript won't help you on these cases.

## Unkown type

The `unknown` is like `any`, but instead of allowing anything, it denies everything.

```typescript
var anyVariable: any = "a";
anyVariable.log() // ✅ OK
var unknownVariable: unknown = "a";
unknownVariable.log() // ❌ Error: 'unknownVariable' is of type 'unknown'
```

*   The advantage of using `unknown` is that it forces you do checks like:

    ```typescript
    function process(val: unknown) {
      if (
        typeof val === 'object' &&
        !!val &&
        'log' in val &&
        typeof val.log === 'function'
      ) {
        val.log();  // ✅ OK
      }
    }
    ```

## Optional Value

You can append the parameter name with `?` to make it optional.

```typescript
function generateError(msg?: string) {
    throw new Error(msg)
}
```

Also to properties:

```typescript
type User = {
  name: string;
  age: number;
  role?: "admin" | "guest";
};
```

