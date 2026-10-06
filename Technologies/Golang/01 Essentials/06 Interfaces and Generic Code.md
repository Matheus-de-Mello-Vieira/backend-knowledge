# Interfaces and Generic Code

## Interface

An **interface** describes behavior through method signatures. A type implements a method-only interface when its method set contains every required method with the matching signature. Implementation is **implicit**: no `implements` declaration is needed, so concrete types do not need to know which interfaces their callers use.

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

`MakeItSpeak` depends on the `Speak` behavior rather than on `Dog` or `Cat`. Calling `s.Speak()` invokes the implementation associated with the concrete value passed to it.

> [!tip] Interface naming
> A useful convention for a one-method interface is the method name plus `-er`, such as `Speaker`. For several methods, choose a name that describes their shared behavior rather than enumerating them.

### Static type and dynamic value

An interface variable has a static interface type; a non-nil interface value carries a dynamic concrete type and a value of that type.

```go
var s Speaker = Dog{}
```

Here, the static type of `s` is `Speaker`, its dynamic type is `Dog`, and its dynamic value is `Dog{}`. The static type determines the methods available through `s`; the dynamic type determines which implementation runs. Assigning an interface value to another compatible interface preserves its concrete dynamic type and value, rather than nesting one interface inside another.

Assignment copies the assigned value, not every object reachable from it:

- **Value payload:** Assigning a struct copies the struct; later changes to the original struct do not change the stored copy.
- **Shared references:** Assigning a pointer copies the pointer, so the interface and the original pointer refer to the same object. Likewise, copied slices and maps retain their references to underlying storage.

The [runtime representation](../99%20Misc/Go%20Internals.md#Interfaces%2C%20boxing%2C%20and%20type%20metadata) determines how the payload is carried; converting to an interface does not by itself guarantee a heap allocation.

### The special "Any Value Allowed" type

The empty interface, `interface{}`, requires no methods and accepts a value of any type. Since Go 1.18, `any` is an alias for `interface{}`, not a distinct type or a different representation.

```go
func PrintAnything(v any) {
    fmt.Println(v)
}

// Inside a function:
PrintAnything("hello")
PrintAnything(123)
PrintAnything(true)
```

An `any` value still has a static type: `any`. Storing an `int` in it does not make integer operations available without recovering an appropriate type.

### Nil interfaces and typed nil values

The zero value of an interface has neither a dynamic type nor a dynamic value and equals `nil`. Assigning a typed nil pointer retains its type, so the resulting interface is non-nil. [Go FAQ](https://go.dev/doc/faq#nil_error)

```go
var p *Dog = nil
var s Speaker = p

fmt.Println(p == nil) // true
fmt.Println(s == nil) // false: dynamic type is *Dog
```

A non-nil interface therefore does not guarantee a usable underlying object. A call with a nil pointer depends on the concrete method: a pointer-receiver method can explicitly handle nil, while a method that dereferences it panics. In this example, invoking the value-receiver `Dog.Speak` through the nil `*Dog` panics because it needs a `Dog` value.

When absence should be represented by a nil interface, check the concrete pointer before converting it to the interface and return an explicit `nil` for absence:

```go
func asSpeaker(d *Dog) Speaker {
    if d == nil {
        return nil // no dynamic type or value
    }
    return d // dynamic type *Dog with a non-nil pointer
}

// Inside a function:
s := asSpeaker(nil)
if s != nil {
    fmt.Println(s.Speak())
}
```

Returning `d` without the check would retain `*Dog` as the dynamic type even when the pointer is nil. With this function's return convention, `s != nil` also guarantees that the underlying `*Dog` is non-nil; that guarantee comes from the function, not from interface semantics.

> [!tip] Error returns
> The same rule applies to `error`, which is an interface: return an explicit `nil` on success, not a nil pointer of a concrete error type. Check a concrete error pointer before returning it as `error` if nil represents success.

### Type assertion

A type assertion `value.(T)` checks the dynamic value of an interface:

- **Concrete target:** The dynamic type must be exactly `T`; an assertion does not perform a numeric conversion or match merely by underlying type.
- **Interface target:** The dynamic type must implement `T`. Success produces a value of the target interface type while retaining the same concrete dynamic type and value.

The single-result form panics on failure. The comma-ok form returns the zero value of `T` and `false` instead; a nil interface also fails an assertion. 

```go
var s Speaker = Dog{}
dog, ok := s.(Dog)
if ok {
    fmt.Println("It's a dog:", dog.Speak())
}

var value any = 123
if intVal, ok := value.(int); ok {
    fmt.Println("Integer:", intVal)
}
```

### Type switches

A [type switch](02%20Essentials.md#switch%20for%20types) selects a branch using the same distinction: a concrete case matches a dynamic type, while an interface case matches implementation of that interface. Cases are tested in source order; `case nil` matches a nil interface.

```go
switch v := s.(type) {
case Dog:
    fmt.Println("Dog says:", v.Speak())
case Cat:
    fmt.Println("Cat says:", v.Speak())
case nil:
    fmt.Println("No speaker")
default:
    fmt.Println("Unknown speaker")
}
```

In a single-type case such as `case Dog`, `v` has that case's type. In the default branch or a multi-type case, it keeps the switch expression's interface type.

### Interface Composition

Embedding smaller interfaces combines their required methods. A type implements the combined interface only when it satisfies all of them.

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

Interface satisfaction uses the method set of the assigned type, not the convenience rules for calling a method on a variable. For a defined non-interface, non-pointer type `T`, the receiver rules are:

- **`T`:** Includes methods declared with receiver `T`.
- **`*T`:** Includes methods declared with receiver `T` or `*T`.

Embedding can additionally promote methods into these method sets. Thus both `T` and `*T` satisfy an interface whose required methods all have value receivers. If a required method has a pointer receiver, only `*T` satisfies it. An unrelated pointer-receiver method does not prevent `T` from satisfying a smaller interface.

```go
type Printer interface {
    Print()
}

type Data struct{}
func (d Data) Print() { fmt.Println("Value receiver") }

type Doc struct{}
func (d *Doc) Print() { fmt.Println("Pointer receiver") }

// Inside a function:
var data Data
var p Printer = data
p = &data // both Data and *Data implement Printer
p.Print()

var doc Doc
doc.Print() // shorthand for (&doc).Print(): doc is addressable
p = &doc
p.Print()
// p = doc // compile-time error: Doc does not implement Printer
```

Automatic address taking makes `doc.Print()` valid, but does not add `Print` to the method set of `Doc` for interface assignment.

### Interface equality

Interface values are equal when both are nil, or when they have identical dynamic types and equal dynamic values. Different dynamic types compare unequal, even when their values look numerically equal.

```go
var a any = int(1)
var b any = int64(1)
fmt.Println(a == b) // false
```

Comparing interfaces with the same non-comparable dynamic type, such as a slice, panics. Comparing with `nil` does not compare the payload and is safe; different dynamic types also compare unequal without comparing their payloads. A comparable struct or array can still panic during equality if an interface field or element contains a non-comparable dynamic value.

## Generics

### The Basics

Go added generics in **Go 1.18**, using **type parameters** for functions and types. Type parameters express relationships between input and output types without converting all values to interfaces.

```go
func Map[T any](s []T, f func(T) T) []T {
    result := make([]T, len(s))
    for i, v := range s {
        result[i] = f(v)
    }
    return result
}
```

- **Type parameter `T`:** Represents the element type chosen when the function is instantiated.
- **Constraint `any`:** Allows any type argument. It does not change `s` into `[]any`; the callback and result retain the same element type `T`.

```go
x := Map([]int{1, 2, 3}, func(i int) int { return i * 2 })
// x has type []int
```

Interfaces and generics solve different problems: an interface value packages a concrete value behind a behavior contract, while a type parameter preserves a compile-time relationship across values in reusable code.

### Constraints

A constraint is an interface whose **type set** determines the allowed type arguments. A generic body must be valid for every type admitted by its constraint; operations such as `+` require support throughout that set.

```go
func SumNumbers[T int | float64](nums []T) T {
    var sum T
    for _, v := range nums {
        sum += v
    }
    return sum
}
```

`int | float64` is a union of exactly those types. A defined type with underlying type `int` is not included automatically; `~int` includes all types with underlying type `int`.

Reusable constraints give the type set a name:

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

Method-only interfaces such as `Speaker` work both as value types and as constraints. Interfaces containing type terms such as unions or `~int` are constraint-only: `Number` is not a type for an ordinary variable holding a number. The predeclared `comparable` constraint permits `==` and `!=`; comparison can still panic when a permitted interface value contains a non-comparable dynamic value.

### Parameterized Types

Types also accept type parameters. Instantiation chooses the field types, and methods reuse the receiver's parameters:

```go
type Pair[T any, U any] struct {
    First  T
    Second U
}

func (p Pair[T, U]) Swap() Pair[U, T] {
    return Pair[U, T]{p.Second, p.First}
}

// Inside a function:
p := Pair[int, string]{1, "hello"}
swapped := p.Swap() // Pair[string, int]
```

Instantiated types retain concrete type identity and [runtime type metadata](../99%20Misc/Go%20Internals.md#Reflection%20and%20runtime%20type%20metadata) for reflection. This is not type erasure. Nor does the language require one separate machine-code body per type argument: the standard compiler shares code for some instantiations with the same shape, and other compilers may choose differently.

### Type Inference

Function calls infer type arguments when argument types and constraints provide enough information. The earlier `Map` call infers `T` as `int`; spelling `Map[int](...)` is also valid. If inference cannot determine the arguments, supply them explicitly.

Generic type instantiation still requires its type arguments, as in `Pair[int, string]`.

### Limitations and Design Philosophy

Go's generics favor reusable, statically checked code rather than a general template language:

- **No higher-kinded type parameters:** A parameter does not stand for a generic type constructor to be applied as `T[U]`.
- **No method-specific type parameters:** Methods do not declare additional type parameters, even on generic types; they use the receiver's parameters. Generic functions declare their own.
- **No user-defined specialization:** There is no declaration mechanism selecting a special generic implementation for one type argument.
- **Interface-based constraints:** Type sets describe admitted types and supported operations; they do not introduce ad-hoc operator overloading.
- **Constraint-limited operations:** An unconstrained `T any` does not support arithmetic merely because a particular call uses a number. Operations guaranteed for all types, such as assignment, remain valid.

### Typical Use Cases

- Utility functions such as mapping, filtering, reducing, and minimum or maximum calculations.
- Generic data structures such as `Stack[T]`, `Set[T]`, and `List[T]`, with constraints appropriate to their operations.
- Algorithms whose logic is independent of the element type.
- Replacing repeated implementations that differ only in their types.
