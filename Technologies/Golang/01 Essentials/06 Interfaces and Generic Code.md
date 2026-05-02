## Interface

An **interface** in Go defines a **set of method signatures** — a *contract* that any type can fulfill.

*   But unlike languages such as Java or C#, you don’t have to *declare* that a type implements an interface.
*   Go uses **implicit implementation**: if a type has the right methods, it automatically satisfies the interface.

```go
package main

import "fmt"

type Speaker interface {
    Speak() string
}

type Dog struct{}
func (d Dog) Speak() string { return "Woof!" }

type Cat struct{}
func (c Cat) Speak() string { return "Meow!" }

func MakeItSpeak(s Speaker) {
    fmt.Println(s.Speak())
}

func main() {
    MakeItSpeak(Dog{})
    MakeItSpeak(Cat{})
}
```

My convention:

*   if your interface have only one method, the name of interface should be 'verb + er'. As `speak` and `speaker`.
*   if there is many method, the name should reflect the key feature of them

Key Properties of Go Interfaces:

*    **Implicit Implementation**

    *   No need for `implements` or `extends` keywords.
    *   If a type matches an interface’s methods, it’s good to go.
    *   That makes interfaces **decoupled** — types don’t need to know about them at all.

*   **Empty Interface** (`interface{}`)

    *   The empty interface — `interface{}` — represents a value of **any type**.

        ```go
        func PrintAnything(v interface{}) {
            fmt.Println(v)
        }
        
        PrintAnything("hello")
        PrintAnything(123)
        PrintAnything(true)
        ```

*   **Type Assertions** You can recover the concrete type stored inside an interface value.

    ```go
    var s Speaker = Dog{}
    dog, ok := s.(Dog)
    if ok {
        fmt.Println("It's a dog:", dog.Speak())
    }
    ```

*   **Type Switches** You can recover the concrete type stored inside an interface value.

    ```go
    switch v := s.(type) {
    case Dog:
        fmt.Println("Dog says:", v.Speak())
    case Cat:
        fmt.Println("Cat says:", v.Speak())
    default:
        fmt.Println("Unknown speaker")
    }
    ```

### Interface Composition

Go allows combining smaller interfaces into larger ones

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}
type Writer interface {
    Write(p []byte) (n int, err error)
}
type ReadWriter interface {
    Reader
    Writer
}
```

### Interfaces and receivers

In Go, interfaces are implemented by methods — and methods are defined on receivers (either value or pointer).

*   So the kind of receiver you choose directly affects whether your type satisfies an interface.

*   The rule is:

    *   If all methods are value receivers: Both the type `T` **and** the pointer `*T` implement the interface.

        ```go
        type Printer interface {
            Print()
        }
        
        type Data struct{}
        
        func (d Data) Print() { fmt.Println("Value receiver") }
        
        func main() {
            var d Data
            var p Printer
        
            p = d   // ✅ works
            p.Print()
        
            p = &d  // ✅ also works
            p.Print()
        }
        ```

    *   If at least one is pointer receiver: Only the pointer `*T`  implement the interface.

        ```go
        type Printer interface {
            Print()
        }
        
        type Doc struct{}
        
        func (d *Doc) Print() { fmt.Println("Pointer receiver") }
        
        func main() {
            var d Doc
            var p Printer
        
            p = &d  // ✅ works
            p.Print()
        
            // p = d  // ❌ compile-time error: Doc does not implement Printer
        }
        ```

## The special "Any Value Allowed" type

It is `interface{}`:

```go
func printSomething(value interface{}) {
	fmt.Println(value)
}
```

but, it is recommended to use `any`:

```go
func printSomething(value any) {
	fmt.Println(value)
}
```

### Type assertion

You can use [`switch` for types](02%20Essentials.md#switch%20for%20types), or:

```
typedVal, ok := value.(int)

if ok {
	fmt.Println("Integer:", typedVal)
}
```

Or, even better:

```go
if intVal, ok := value.(int); ok {
	fmt.Println("Integer:", typedVal)
}
```

## Generics

### The Basics

Go added generics in **Go 1.18**, using **type parameters** for functions and types.
 You declare them in square brackets `[]`, like in many other languages:

```go
func Map[T any](s []T, f func(T) T) []T {
    result := make([]T, len(s))
    for i, v := range s {
        result[i] = f(v)
    }
    return result
}
```

Here:

-   `T` is a **type parameter**.

-   `any` is a **constraint**, shorthand for `interface{}`.

-   You can call it like:

    ```go
    Map([]int{1,2,3}, func(x int) int { return x * 2 })
    ```

So far, that’s similar to C#’s or Java’s generics syntax — except Go’s are **erased** at compile time (no runtime generics) and **monomorphized per instantiation** (the compiler generates specific versions for each used type).

### Constraints

Constraints are **interfaces** that restrict what operations can be performed on a type parameter.

Example:

```go
func SumNumbers[T int | float64](nums []T) T {
    var sum T
    for _, v := range nums {
        sum += v
    }
    return sum
}
```

Here, `T int | float64` means T must be either `int` or `float64` — a type set.
 This is Go’s way of saying “T supports +” without a fully generic numeric type hierarchy.

You can also define reusable constraints:

```go
type Number interface {
    int | float64 | int64
}

func Sum[T Number](vals []T) T {
    var total T
    for _, v := range vals {
        total += v
    }
    return total
}
```

### Parameterized Types

You can also parameterize types, not just functions:

```go
type Pair[T any, U any] struct {
	First  T
	Second U
}

func (p Pair[T, U]) Swap() Pair[U, T] {
	return Pair[U, T]{p.Second, p.First}
}
```

Instantiation:

```go
p := Pair[int, string]{1, "hello"}
```

No runtime reflection or type metadata is generated; Go instantiates a version of `Pair` for each concrete type used.

### Type Inference

Go can infer type arguments in many cases, so you usually don’t need to specify them explicitly:

```go
x := Map([]int{1, 2, 3}, func(i int) int { return i * 2 })
// no need for Map[int]
```

But sometimes inference fails, especially if there’s no clear mapping between argument types and type parameters.

### Limitations and Design Philosophy

Go’s generics are intentionally *minimalist*. Compared to, say, C++ templates or Rust traits:

-   No higher-kinded types (you can’t have `T[U]` parameters).
-   No generic methods on non-generic types (every method using generics must belong to a generic type or function).
-   No specialization.
-   Constraints are always interface-based — no ad-hoc operator overloading beyond what type sets allow.
-   You can’t use operators on unconstrained types — only on those that are guaranteed valid by the constraint.

This aligns with Go’s general philosophy: **simplicity, readability, and compile-time safety** over expressive power.

### Typical Use Cases

-   Utility functions like `min`, `max`, `map`, `filter`, `reduce`.
-   Generic data structures (`Stack[T]`, `Set[T]`, `List[T]`).
-   Algorithms that don’t care about the element type.
-   Reducing boilerplate across similar logic for different types.
