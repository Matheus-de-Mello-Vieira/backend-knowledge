# Javascript Syntactic Sugar

## Arrow function

If the function have only one parameter, and the function is properly typed, you can omit the `()` of the parameters

```typescript
const printOutput: (a: number | string) => void = output => console.log(output)
```

It is especially good when the typing is granted

```typescript
button.addEventListerner('click', event => console.log(event))
```

When there is no parameter, you still need use `()`

```typescript
() => console.log("Hello World")
```

## Rest Operator

You can type the rest operator

```typescript
function printAll(...args: number[]) {
  console.log(args);
}
printAll(1, 2, 3); // [1, 2, 3]
```

