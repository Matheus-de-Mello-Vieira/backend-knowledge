# Enum

Go doesn’t have a *native* `enum` keyword like languages such as C, Java, or Rust. However, you can achieve **enumeration-like behavior** using **constants** and the special keyword **`iota`**.

### Basic Concept

An *enum* represents a set of related, named constants. In Go, you define these using a `const` block with `iota` — a built-in counter that increments automatically.

#### Example:

```go
package main

import "fmt"

type Direction int

const (
    North Direction = iota
    East
    South
    West
)

func main() {
    fmt.Println(North, East, South, West)
}
```

**Output:**

```
0 1 2 3
```

Here:

- `Direction` is a custom type (an alias for `int`).
- `iota` starts at `0` and increments by `1` for each constant in the block.

### Why Use a Custom Type

By defining a **named type** (`Direction`), you add type safety:

- Functions can explicitly require a `Direction` parameter.
- You avoid mixing unrelated constants (e.g., you can’t accidentally pass a “color” constant where a “direction” is expected).

#### Example:

```go
func move(d Direction) {
    switch d {
    case North:
        fmt.Println("Moving north")
    case South:
        fmt.Println("Moving south")
    default:
        fmt.Println("Staying put")
    }
}
```

### Enum Values Beyond Simple Counting

You can use `iota` creatively for **bitmasks** or **custom starting values**:

#### Bit Flags Example:

```go
type Permission uint8

const (
    Read Permission = 1 << iota
    Write
    Execute
)

func main() {
    fmt.Println(Read, Write, Execute) // 1 2 4
}
```

## Good ideias for functions

### `String()` — for readable output

By default, printing an enum shows its underlying value (like `0`, `1`, etc.).
 You can make it more readable by implementing the `String()` method for the type.

#### Example:

```go
func (d Direction) String() string {
    return [...]string{"North", "East", "South", "West"}[d]
}

func main() {
    fmt.Println(North, South) // Output: North South
}
```

Or use Go’s `Stringer` code generation tool for larger enums:

```bash
go install golang.org/x/tools/cmd/stringer@latest
stringer -type=Direction
```

This generates a `String()` method automatically.

###  `FromString(s string)` — parse user input or config strings

```go
func DirectionFromString(s string) (Direction, error) {
    switch s {
    case "North":
        return North, nil
    case "East":
        return East, nil
    case "South":
        return South, nil
    case "West":
        return West, nil
    default:
        return Direction(-1), fmt.Errorf("invalid direction: %s", s)
    }
}
```

Example:

```go
d, err := DirectionFromString("East")
if err != nil {
    fmt.Println("Error:", err)
} else {
    fmt.Println("Parsed:", d) // "Parsed: East"
}
```

### `IsValid()` — simple validation

```go
func (d Direction) IsValid() bool {
    return d >= North && d <= West
}
```


Example:

```go
fmt.Println(Direction(2).IsValid())  // true
fmt.Println(Direction(99).IsValid()) // false
```

### `AllDirections()` — for iteration

```
func AllDirections() []Direction {
    return []Direction{North, East, South, West}
}
```

Example:

```
for _, d := range AllDirections() {
    fmt.Println(d)
}
```

### JSON Marshalling

In Go, the `encoding/json` package checks **each field’s type** recursively when marshalling or unmarshalling.

If a type implements the `json.Marshaler` or `json.Unmarshaler` interface, the package automatically uses those methods — no matter how deeply nested it is.

```go
func (d Direction) MarshalJSON() ([]byte, error) {
    return json.Marshal(d.String())
}

func (d *Direction) UnmarshalJSON(data []byte) error {
    var s string
    if err := json.Unmarshal(data, &s); err != nil {
        return err
    }
    dir, err := DirectionFromString(s)
    if err != nil {
        return err
    }
    *d = dir
    return nil
}
```

