# Deriving types from types

## `typeof`

The typescript augments the [JavaScript operator `typeof`](../../Javscript%20Miscellaneous.md#typeof).

*   It introduces a new `typeof` that is used automatically intead of the javascript one depeding on the situation.

```typescript
// Define a constant variable with a string value
const userName = 'Max';

// Use typeof at runtime (inside console.log) to check the data type of userName
console.log(typeof userName); // Output: "string"

// Use typeof at the type level (TypeScript feature) to extract the type of userName
type UserName = typeof userName; 
// Now, UserName is a type alias for 'string'

// ✅ Correct usage: assigning a string to a variable of type UserName
const validUserName: UserName = "Alice"; // OK, since it's a string

// ❌ Incorrect usage: assigning a number to a variable of type UserName
const invalidUserName: UserName = 1; // Error: Type '1' is not assignable to type '"Max"'.
```

### More useful example

The code

```typescript
const settings = {
    difficulty: 'easy',
    minLevel: 10,
    didStart: false,
    player: ['John', "Jane"]
}

type Settings = {
  difficulty: string;
  minLevel: number;
  didStart: boolean;
  player: string[];
};

function loadData(settings: Settings) {
    // ...
}

loadData(settings)
```

Have a implicit duplication of knowledge the declaration of `settings` and `Settings` - a violation of DRY tenet. You can use `typeof` to avoid it:

```typescript
const settings = {
    difficulty: 'easy',
    minLevel: 10,
    didStart: false,
    player: ['John', "Jane"]
}

type Settings = typeof settings

function loadData(settings: Settings) {
    // ...
}

loadData(settings)
```

Or, even:

```typescript
function loadData(s: typeof settings) {
    // ...
}
```

### Another great use-case for `typeof`

You have a function `sum(a: number, b: number)` that sums two numbers. You also have `subtract(a: number, b: number)` that subtracts two numbers.

In addition, you have `performMathAction(cb)` which receives a `cb` parameter. `cb` should be either a pointer to the `sum` or the `subtract` function. So that you could either call `performMathAction(sum)` or `performMathAction(subtract)`.

Hence the idea is that `performMathAction` calls `sum` or `subtract` internally (and passes values to those functions).

```typescript
function sum(a: number, b: number) {
  return a + b;
}
function subtract(a: number, b: number) {
  return a - b;
}

function performMathAction(cb: (a: number, b: number) => number) {
  // some code...
}
```

But since you already defined `sum` and `subtract` somewhere else in your code, you can also simply derive the function type with help of `typeof`.

```typescript
function sum(a: number, b: number) {
  return a + b;
}
function subtract(a: number, b: number) {
  return a - b;
}

function performMathAction(cb: typeof sum | typeof subtract) {
  // some code...
}
```

## `keyof`

You can use `keyof` to descript a type that holds all keys of another type

```typescript
type User = { name: string; age: number };
type UserKeys = keyof User;

let validKey: UserKeys;
validKey = "age";
validKey = "name";
```

### More useful example

```typescript
type User = { name: string; age: number };

function getProb<T extends object, U extends keyof T>(obj: T, key: U) {
    const val = obj[key]

    if(val === undefined || val === null) {
        throw new Error("Accessing undefined or null value")
    }

    return val
}

const user: User = {name: "Matheus", age: 23}
const name = getProb(user, 'name') // inferred type: string
const age = getProb(user, 'age') // inferred type: number
getProb(user, 'email') // Argument of type '"email"' is not assignable to parameter of type 'keyof User'
```

*   You can also declare as:

    ```typescript
    function getProb<T extends object>(obj: T, key: keyof T) {
        const val = obj[key]
    
        if(val === undefined || val === null) {
            throw new Error("Accessing undefined or null value")
        }
    
        return val
    }
    ```

    But it will cause a worse type inferrence:

    ``` typescript
    const name = getProb(user, 'name') // inferred type: string | number 
    const age = getProb(user, 'age') // inferred type: string | number
    ```

## Indexed access types

