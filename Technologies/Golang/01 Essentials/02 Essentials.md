# Essentials

Values, Basic Types & Core Language Features

## Values and Types

### Variables

You declare variables using `var`, the convention is camelCase.

```go
var principal = 1000
var expectedReturnRate = 0.2;
var years = 10;
```

The go doesn't allow mix different types:

```go
var oneYearValue = principal * (1 + expectedReturnRate) // ❌ Error: invalid operation: principal * (1 + expectedReturnRate) (mismatched types int and float64)
```

You can convert `principal` to `float64` first:

```go
var oneYearValue = float64(principal) * (1 + expectedReturnRate) // ✅ OK
```

To calculate the future value, you can use the package `math`:

```go
package main

import "math"

func main() {
 var principal = 1000;
 var expectedReturnRate = 0.2;
 var years = 10;

 var futureValue = float64(principal) * math.Pow((1 + expectedReturnRate), float64(years))
}
```

* notice that I parsed `years` as `float64`, because `math.Pow` needs two floats:

    ```go
    func math.Pow(x float64, y float64) float64
    ```

* You can explicitly declare the type of variables, so you don't need to convert them afterwards:

    ```go
    var principal float64 = 1000;
    var expectedReturnRate float64 = 0.2;
    var years float64 = 10;

    var futureValue = principal * math.Pow((1 + expectedReturnRate), years)
    ```

    * Or simpler:

        ```go
        var principal, years float64 = 1000, 10;
        expectedReturnRate := 0.2;
        ```

    * Or, even simpler:

        ```go
        principal, years, expectedReturnRate := 1000.0, 10.0, 0.2;
        ```

### Single-Letter Variable Names in Go

In Go, using short or even single-letter variable names is a common and idiomatic practice. This convention reflects Go’s philosophy of simplicity and brevity. Single-letter identifiers are typically used when the variable’s purpose is immediately clear from context and when the scope of use is small—such as within short loops, conditionals, or brief helper functions.

Examples include common variables like `i` for loop counters, `r` for receivers, `b` for bytes or buffers, and `err` for errors. The Go standard library itself follows this approach extensively, promoting compact and readable code.

However, clarity should always take precedence. Descriptive names are preferred when variables have a broader scope, persist across multiple lines, or when their role is not self-evident. Overusing short names can make code harder to read and maintain, especially in complex logic.

In summary, single-letter variable names are appropriate in Go when they enhance conciseness without sacrificing clarity. The key is to balance brevity and readability according to context.

### **Basic Types**

Go comes with a couple of built-in basic types:

* `int` A integer number (e.g., `-5`, `10`, `12` etc)
    * `uint` An unsigned integer which means a strictly non-negative integer
    * `int8` A 8-bit signed integer, which is an integer with a specific range from -128 to 127
    * `uint8` A 8-bit unsigned integer, an integer that can represent values from 0 to 255
    * `int32` A 32-bit signed integer, which is an integer with a specific range from -2,147,483,648 to 2,147,483,647
    * `rune` An alias for `int32`, represents a Unicode code point, and is used when dealing with Unicode characters (e.g., 'a', 'ñ', '世')
    * `uint32` A 32-bit unsigned integer, an integer that can represent values from 0 to 4,294,967,295
    * `int64` A 64-bit signed integer, an integer that can represent a larger range of values, specifically from -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807

* `float64` a real number (e.g., `-5.2`, `10.123`, `12.9` etc)

* [`string`](#Strings) An immutable sequence of bytes, commonly used for text.

* `bool` `true` or `false`

All Go value types come with a so-called "null value" which is the value stored in a variable if no other value is explicitly set.

* `int` => `0`
* `float64` => `0.0`
* `string` => `""` *(i.e., an empty string)*
* `bool` => `false`

### Strings

A `string` is an immutable sequence of bytes. It commonly holds UTF-8 text, but its bytes are not required to form valid UTF-8. Its zero value is the empty string, `""`, not nil.

#### String literals

The delimiters determine how source text becomes string contents:

* **Interpreted literals (`"..."`):** Process escapes such as `\n` for a newline, `\t` for a tab, and `\"` for a double quote. Use `\n` to put line breaks into a quoted string.
* **Raw literals (backticks):** Preserve backslashes and double quotes without interpreting escapes, and permit actual line breaks. A backtick cannot appear inside a raw literal; carriage returns are discarded.

```go
message := "This is line one.\nThis is line two.\nThis is line three."
fmt.Println(message) // prints three lines

raw := `This is a multiline string in Go.
"Quotes" and \slashes\ are literal; \n and \t remain text.`
fmt.Println(raw) // prints two lines without interpreting the backslashes
```

Single quotes produce a rune literal, such as `'é'`, not a string literal. Use `"é"` for a string.

#### Bytes, runes, and UTF-8

Two units matter for string operations:

* **Byte:** An eight-bit value. Go's `byte` type is an alias for `uint8`; string storage and byte indexes use this unit.
* **Rune:** A Unicode code point, represented by Go's `rune` alias for `int32`. UTF-8 encodes a code point as one or more bytes.

`len(s)` counts bytes, not runes. Converting to `[]rune` decodes the string as UTF-8, so the resulting slice's length counts decoded code points:

```go
s := "Goé"
fmt.Println(len(s))         // 4: G and o use one byte each; é uses two
fmt.Println(len([]rune(s))) // 3
```

> [!note] Code points and visible characters
> A user-perceived character can contain multiple code points, such as a letter followed by a combining accent. Rune count is therefore not always a count of visible characters.

#### Indexing and slicing

String indexes and slice bounds are byte offsets. Indexing returns a byte; slicing returns a string containing the selected bytes:

```go
fmt.Println(s[2])  // 195: the first UTF-8 byte of é, not its rune value
fmt.Println(s[:2]) // Go
fmt.Println(s[2:]) // é
```

Indexes must be nonnegative and smaller than `len(s)`. In `s[low:high]`, `low` is the starting byte offset and `high` is the excluded ending offset; the bounds must satisfy `0 <= low <= high <= len(s)`.

> [!warning] Cutting through UTF-8
> Slicing does not validate code point boundaries. `s[:3]` contains `Go` followed by only the first byte of `é`, so the result is not valid UTF-8. Choose boundaries at complete code points when slicing text.

#### Iteration

Choose the loop according to the unit required:

* **Indexed loop:** Visits every byte with `s[i]` for indexes from zero through `len(s)-1`.
* **`range` loop:** Decodes UTF-8 and yields a byte offset together with a rune value. Offsets advance by the encoded width, not necessarily by one.

```go
for offset, r := range s {
    fmt.Println(offset, string(r))
}
// 0 G
// 1 o
// 2 é
```

If `range` encounters invalid UTF-8, it yields the replacement rune U+FFFD and advances one byte. Iteration does not change the original bytes.

#### Immutability, assignment, and concatenation

String contents cannot be changed through indexing: `s[0] = 'g'` is invalid. A variable holding a string can still be assigned a different value. Assignment does not require duplicating the bytes because the [string representation](../99%20Misc/Go%20Internals.md#Strings) refers to immutable storage.

```go
A := "Go"
B := A
A = A + "lang"

fmt.Println(A) // Golang
fmt.Println(B) // Go
```

`+` concatenates byte sequences into a string value; it does not modify the operands. String equality compares byte sequences, so visually equivalent text with different code point encodings is not necessarily equal.

#### Converting to mutable slices

Conversion selects how the string is interpreted:

* **`[]byte(s)`:** Preserves the bytes, providing mutable byte elements. `string(bytes)` forms a string from those bytes without requiring valid UTF-8.
* **`[]rune(s)`:** Decodes UTF-8 into mutable code point elements. `string(runes)` encodes the rune values as UTF-8; invalid code points become U+FFFD.

```go
s := "Goé"
bytes := []byte(s)
bytes[0] = 'g'
fmt.Println(s, string(bytes)) // Goé goé

runes := []rune(s)
runes[2] = 'a'
fmt.Println(s, string(runes)) // Goé Goa
```

Mutating the converted slice does not change the source string. Likewise, mutating a source slice after converting it to a string does not change the resulting string. These are semantic guarantees, not promises about how many allocations or copies the compiler emits.

> [!warning] Decoding is not byte-preserving
> Invalid UTF-8 becomes replacement runes during decoding. Converting through `[]rune` therefore does not round-trip arbitrary bytes unchanged; use `[]byte` when byte preservation matters.

### short variable declaration (`:=`)

The code

```go
expectedReturnRate := 0.2;
```

Is equivalent of

```go
var expectedReturnRate = 0.2;
```

By convention, you should use this operator as often as possible.

You can't assign type, so when using this operator, you need to trust on the inference.

A short variable declaration (`:=`) declares new variables and may reassign existing ones, provided at least one variable on the left-hand side is new.

* So you can:

    ```go
    data, err := os.ReadFile("balance.txt")
    ...
    balance, err := strconv.ParseFloat(balanceText, 64)
    ```

## Constant

It works similar to variables, but you can't change the value of a `const`.

```go
const inflationRate = 0.025
...
futureRealValue := futureValue / math.Pow(1 + inflationRate, years)
```

## fmt package

### fmt.Println

Is the way to print on the console in go:

```go
package main

import "fmt"

func main() {
 fmt.Println("Hello World")
}
```

It can also receive many parameters, that will end up concating them with spaces.

````go
fmt.Println("Hello", "World") // Hello World
````

### fmt.Scan

Scan scans text read from standard input, storing successive space-separated values into successive arguments. Newlines count as space. It returns the number of items successfully scanned. If that is less than the number of arguments, err will report why.

```go
const inflationRate = 0.025

var principal, years, expectedReturnRate float64

fmt.Print("Principal: ")
fmt.Scan(&principal)

fmt.Print("Years: ")
fmt.Scan(&years)

fmt.Print("Expected return rate: ")
fmt.Scan(&expectedReturnRate)

var futureValue = principal * math.Pow((1+expectedReturnRate), years)

futureRealValue := futureValue / math.Pow(1+inflationRate, years)

fmt.Println("Future value:", futureValue)
fmt.Println("Future real value:", futureRealValue)
```

But this function also has an **important limitation:** You can't (easily) fetch **multi-word input values**. Fetching text that consists of more than a single word is tricky with this function.

To do it, you should:

```go
package main

import (
 "bufio"
 "fmt"
 "log"
 "os"
 "strings"
)


func main() {
 fmt.Print("Text: ")

 reader := bufio.NewReader(os.Stdin)

 text, err := reader.ReadString('\n')

 if err != nil {
  log.Fatal("Error", err)
 }

 text = strings.TrimSuffix(text, "\n")
 text = strings.TrimSuffix(text, "\r")

 log.Println(text)
}
```

* Where `reader.ReadString` will read the input until a `\n`
* `strings.TrimSuffix` will return "s without the provided trailing suffix string. If s doesn't end with suffix, s is returned unchanged."

### fmt.Printf

Printf formats according to a format specifier and writes to standard output. It returns the number of bytes written and any write error encountered.

* You can find all formatting options in <https://pkg.go.dev/fmt>

```go
// given a float64 ebt and profit
fmt.Printf("EBT: %v\n", ebt)
fmt.Printf("EBT: %v\nProfit: %v\n", ebt, profit)
```

You can also control how the float values are printed, for example to print only two decimal places:

```go
fmt.Printf("EBT: %.2f\n", ebt)
fmt.Printf("Profit: %.2f\n", profit)
```

### fmt.Stringf

It allows format strings, but return it instead of print it.

```go
formattedEBT := fmt.Sprintf("EBT: %.2f", ebt)
fmt.Println(formattedEBT)
```

## Functions

```go
func outputText(text string)  {
  fmt.Print(text)
}
```

To specify the return type:

```go
func calculateFutureValues(investmentAmount, expectedReturnRate, years float64) (float64, float64) {
    fv := investmentAmount * math.Pow(1+expectedReturnRate/100, years)
    rfv := fv / math.Pow(1+inflationRate/100, years)
    return fv, rfv
}
```

* So to use:

    ```go
    func main() {
     investmentAmount := 10000.0    // Initial investment
     expectedReturnRate := 7.0      // Annual return rate in %
     years := 10.0                  // Investment period in years

     fv, rfv := calculateFutureValues(investmentAmount, expectedReturnRate, years)

     fmt.Printf("Future Value: $%.2f\n", fv)
     fmt.Printf("Inflation-Adjusted Future Value: $%.2f\n", rfv)
    }
    ```

You can specify names for each returned value:

* ```go
    func calculateFutureValues(investmentAmount, expectedReturnRate, years float64) (fv float64, rfv float64) {
     fv = investmentAmount * math.Pow(1+expectedReturnRate/100, years)
     rfv = fv / math.Pow(1+inflationRate/100, years)

     return
    }
    ```

    * You can still returning like `return fv, rfv`. but `return` suffice.
    * It is recommend to explicitly name the returns `fv float64, rfv float64` and explicitly return all values `return fv, rfv` , mainly if the function is very large - otherwise the function can became very confuse.

## Control Structures

### `If`, `else if` and `else`

```go
if choice == 1 {
    ...
} else if choice == 2 {
    ...
} else if choice == 3 {
    ...
} else {
    ....
}
```

### `switch`

```go
switch choice {
case 1:
    ...
case 2:
    ...
case 3:
    ...
default:
    ...
}
```

#### `switch` for types

````go
func printSomething(value any) {
 switch value.(type) {
 case int:
  fmt.Println("Integer:", value)
 case float64:
  fmt.Println("Float:", value)
 case string:
  fmt.Println(value)
 default:
  //...
 }
}
````

### `for`, `break` and `continue`

`for` is the unique loop in go

* ```go
    for i := 0; i < 2; i++ {
     fmt.Println(i)
    }
    ```

* ```go
    for someCondition {
      // do something ...
    }
    ```

* ```go
    for { // infinite loopp
     ...
    }
    ```

You can use `break` to interrupt the loop, or `continue` to finish the current iteration.

## Handling errors

Functions don't crash the application, instead it should be returned by functions

* instead of try-catch, in Go you need to check and handle errors explicitly after each function call that can fail — usually with `if err != nil { ... }`

```go
package main

import (
 "fmt"
 "os"
 "strconv"
 "strings"
)

func main() {
 data, err := os.ReadFile("balance.txt")
 if err != nil {
  fmt.Fprintf(os.Stderr, "Error reading file: %v\n", err)
  os.Exit(1)
 }

 balanceText := strings.TrimSpace(string(data)) // remove spaces/newlines
 balance, err := strconv.ParseFloat(balanceText, 64)
 if err != nil {
  fmt.Fprintf(os.Stderr, "Error parsing balance: %v\n", err)
  os.Exit(1)
 }

 fmt.Printf("Balance: %.2f\n", balance)
}
```

And Instead of throwing exceptions, in Go you return errors as values and let the caller decide how to handle them.

```go
import (
 "errors"
 "fmt"
)

// Instead of throwing an exception, we return an error
func divide(a, b float64) (float64, error) {
 if b == 0 {
  return 0, errors.New("cannot divide by zero")
 }
 return a / b, nil
}
```

### Multiple erros

It is common situations like:

```go
err := context.ShouldBindJSON(&event)

if err != nil {
    ...
}
...
err1 := event.Save()
if err1 != nil {
    ...
}
```

To avoid create multiple `err` variables, as `err1`, you can:

```go
if err := context.ShouldBindJSON(&event); err != nil {
 ...
}
...
if err := event.Save(); err != nil {
 ...
}
```

### Handling Different Error Types with `switch`

This approach is useful when your program can produce various error types, and you want to handle each case differently.

````go
_, err := os.Open("/no/such/file.txt")
if err != nil {
 switch {
 case errors.Is(err, os.ErrNotExist):
  fmt.Println("System says: file does not exist")
 case errors.Is(err, os.ErrPermission):
  fmt.Println("System says: permission denied")
 default:
  fmt.Println("System says: some other error:", err)
 }
}
````

## `enum`

Go doesn’t have a *native* `enum` keyword like languages such as C, Java, or Rust. However, you can achieve enumeration-like behavior using constants and the special keyword **`iota`**.

An *enum* represents a set of related, named constants. In Go, you define these using a `const` block with `iota` — a built-in counter that increments automatically.

### Example

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

```text
0 1 2 3
```

Here:

* `Direction` is a custom type (an alias for `int`).
* `iota` starts at `0` and increments by `1` for each constant in the block.
