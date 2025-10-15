# Generic Types

It is static polymorphism 

```typescript
type DataStore<T> = {
  [key: string]: T
};

let store: DataStore<string | boolean> = {}

store.name = 'Max';
store.isInstructor = true;
```

## Inference

TypeScript is very good at inferring types when you use generics.

```typescript
function merge<T>(a: T, b: T) {
  return [a, b]
}
```

*   The return type is inferred as `T[]`

## Working with multiple generic parameters

```typescript
function merge<T, U>(a: T, b: U) {
  return [a, b]
}
```

*   The return type is inferred as `(T | U)[]`

## Constraints

You can add constraints for the generic type

```typescript
function mergeObj<T extends object>(a: T, b: T) {
  return { ...a, ...b };
}
```

*   Notice how doing it, the inferred type goes wild:

    *   ```typescript
        mergeObj({ x: 1 }, { x: "hi" });
        ```

        ```typescript
        function mergeObj<{ x: number } | { x: string }>(
        a: { x: number } | { x: string },
        b: { x: number } | { x: string }
        ): { x: number } | { x: string }
        ```

    *   ```typescript
        mergeObj({ x: 1 }, { y: 2 });
        ```

        ```typescript
        function mergeObj<{ x: number; y?: never } | { y: number; x?: never }>(
          a: { x: number; y?: never } | { y: number; x?: never },
          b: { x: number; y?: never } | { y: number; x?: never }
        ): { x: number; y?: never } | { y: number; x?: never }
        ```

*    If you add a different generic to the second parameter, the inferred types will be better

    ```typescript
    function mergeObj<T extends object, U extends object>(a: T, b: U) {
      return { ...a, ...b };
    }
    ```

    *   ```typescript
        mergeObj({ x: 1 }, { x: "hi" });
        ```
		
		```typescript
		function mergeObj<{ x: number }, { x: string }>(
          a: { x: number },
          b: { x: string }
        ): { x: number } & { x: string }
		```
		
    *   ```typescript
        mergeObj({ x: 1 }, { y: 2 });
        ```

		```typescript
		function mergeObj<{ x: number }, { x: number }>(
          a: { x: number },
          b: { x: number }
        ): { x: number } & { x: number }
		```

## Generic Classes

```typescript
class User<T> {
  constructor (public id: T) {}
}
const user = new User("i1");

user.id; // string
```

