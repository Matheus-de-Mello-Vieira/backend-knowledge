# Essentials

Values, Basic Types & Core Language Features

## Packages

A package in Go is a way to organize and reuse code. Every Go source file (`.go` file) belongs to a package.

*   Every go file need a `package` declaration.

*   A package is simply a collection of Go files in the same directory that share the same `package` declaration at the top.

Example:

```go
package mathutils

import "fmt"

func Add(a, b int) int {
    return a + b
}

func PrintSum(a, b int) {
    fmt.Println("Sum:", Add(a, b))
}
```

Here:

-   The package name is `mathutils`.
-   You can use this package in another Go file by importing it (if it’s part of the same module or available via a module path).

When you run or build your Go code, the compiler groups all files in the same package together.

### Main package

*   The main package is special — it defines an executable program (not a library).
*   A file in the `main` package must have a `func main()` entry point.
*   Other packages are meant to be imported and reused.

Example of a `main` package using `mathutils`:

```go
package main

import (
    "fmt"
    "example.com/myapp/mathutils"
)

func main() {
    result := mathutils.Add(5, 3)
    fmt.Println("Result:", result)
}
```

### Accessing Elements from

Example project structure

```
myapp/
├── go.mod
├── main.go
└── mathutils/
    ├── add.go
    └── sub.go
```

####  Another File, Same Package

If two .go files are in the same folder and have the same package name, they automatically share all their identifiers (functions, variables, types, etc.), even if they are unexported (start with a lowercase letter).

Example

*   `mathutils/add.go`

    ```go
    package mathutils
    
    func add(a, b int) int {     // lowercase: unexported
        return a + b
    }
    
    func AddAndDouble(a, b int) int { // uppercase: exported
        return add(a, b) * 2
    }
    ```

*   `mathutils/sub.go`

    ```go
    package mathutils
    
    func Sub(a, b int) int {
        return a - b
    }
    
    func CombinedOp(a, b int) int {
        return add(a, b) + Sub(a, b) // can access add() freely
    }
    ```

#### Another Package

When you access code from a *different* package, you must:

1.  Import that package.
2.  Use the exported (capitalized) identifiers from it.
3.  Have a `main` function, to serve as system's entry point.

Example

*   `main.go`

    ```go
    package main
    
    import (
        "fmt"
        "example.com/myapp/mathutils" // module path + folder
    )
    
    func main() {
        sum := mathutils.Add(5, 3)
        fmt.Println(sum)
    
        // mathutils.sub(5,3) ❌ Not allowed (unexported)
    }
    ```

### Standardized library

Go comes with a huge Standardized library of built-in packages: https://pkg.go.dev/std

## Module

A **module** is a collection of related Go packages that are versioned together as a unit.
*   Modules make dependency management and versioning easier.
*   A module is identified by a module path (like `github.com/user/projectname`).
*   Each module has a file named `go.mod` at its root, which defines the module’s path and dependencies.

Example of a `go.mod` file:

```go
module example.com/myapp

go 1.22

require (
    github.com/gin-gonic/gin v1.9.1
)
```

Here:

-   The module path is `example.com/myapp`.
-   The project uses Go 1.22.
-   It depends on the external module `github.com/gin-gonic/gin` (version 1.9.1).

### Creating a new module

````bash
go mod init <module-path>
````

This command creates a `go.mod` file in your project’s root directory.

*   Example:

    ```bash
    go mod init example.com/myapp
    ```


#### Module path

The module path is a unique identifier for your Go module.

*   It tells Go (and other developers) where this module comes from and how to import its packages.
    *   The module path defines the **import base path** for all packages in your project.

Patterns

*   **Local (private or experimental) projects**: If your project is local and not hosted anywhere, you can use any path you like — it just needs to be unique within your workspace.

    ```
    go mod init myapp
    go mod init github.local/myname/myapp
    go mod init example/myapp
    ```

    *   You can then import subpackages relative to that path, e.g.:

        ```go
        import "myapp/mathutils"
        ```

*   **Public / hosted modules (recommended for real projects)**: If you plan to share or publish your module (e.g. on GitHub or a private VCS), the module path should match the repository URL.

    For example, if your code lives at:

    ```
    https://github.com/yourname/myapp
    ```

    then you should initialize it with:

    ```bash
    go mod init github.com/yourname/myapp
    ```

    That way, others can import your code with:

    ```bash
    import "github.com/yourname/myapp/mathutils"
    ```

### Add dependencies

```bash
go get <module-path>@<version>
```

*   Adds or updates a dependency manually.

    *   Example:

        ```bash
        go get github.com/gin-gonic/gin@v1.9.1
        ```

### Upgrade or downgrade a dependency

*   ```bash
    go get <module-path>@latest
    ```
    it resolves what “latest” means at that moment — usually the newest tagged stable release (e.g. `v1.12.3`) — and then **pins** that exact version number in your `go.mod`.

*   ```bash
    go get <module-path>@v1.2.3
	```
	Updates a specific dependency to a desired version.

### Clean up unused dependencies

```bash
go mod tidy
```

*   Removes unused modules and adds any missing ones.
*   Most common and safest command for keeping dependencies up to date.
*   It will
    *   Reads the project’s `go.mod`
    *   Downloads any missing dependencies
    *   Cleans up unused ones
    *   Verifies checksums in `go.sum`

*   If you want to work in a already existent project, this is the command to initialize your workspace

### **Download all dependencies**

```bash
go mod download
```

Downloads all the modules listed in `go.mod` to your local cache, but doesn’t install them.

### Verify module integrity

```bash
go mod verify
```

### List all dependencies

```bash
go list -m all
```

## Building

```bash
go build
```

## Running

You can run a specify file with;

```bash
go run investment_calculator.go
```

Or you can run the current module with a dot (`.`):

```bash
go run .
```

## Basic structuring

A **basic Go project** has a clean and opinionated structure — Go emphasizes simplicity and convention over configuration.

### Typical Project Structure

```
myproject/
│
├── cmd/                    # Main applications for this project
│   └── myapp/
│       └── main.go         # Entry point (package main)
│
├── internal/               # Private packages (cannot be imported outside this module)
│   └── service/
│       └── service.go
│
├── pkg/                    # Public packages (importable by external modules)
│   └── utils/
│       └── strings.go
│
├── api/                    # (optional) API definitions, schemas, or protobufs
│
├── configs/                # Configuration files (YAML, JSON, ENV)
│
├── scripts/                # Helper scripts (build, deploy, etc.)
│
├── test/                   # Integration or e2e tests
│
├── go.mod                  # Module definition (dependencies)
├── go.sum                  # Dependency checksums
└── README.md
```

### Key Concepts

*   **`cmd/`**
     Each folder inside represents a separate executable program.
     Example: `cmd/server/main.go` could start a web server.
    
    *   Project with `cmd/` are applications — web servers, CLIs, daemons, etc.
    
*   **`internal/`**
     Code that **must not** be imported by other modules (Go enforces this).
     Great for encapsulating your business logic or data layers.

*   **`pkg/`**
     Reusable packages meant to be imported elsewhere (optional but common in libraries).

*   **`go.mod`**
     Defines your module name and dependencies.
     Example:

    ```
    module github.com/username/myproject
    
    go 1.22
    ```

*   **`main.go`**

     The entry point of your executable — must declare:

    ```go
    package main
    
    func main() {
        // your app starts here
    }
    ```

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

*   notice that I parsed `years` as `float64`, because `math.Pow` needs two floats:

    ```go
    func math.Pow(x float64, y float64) float64
    ```

*   You can explicitly declare the type of variables, so you don't need to convert them afterwards:

    ```go
    var principal float64 = 1000;
    var expectedReturnRate float64 = 0.2;
    var years float64 = 10;
    
    var futureValue = principal * math.Pow((1 + expectedReturnRate), years)
    ```
    
    *   Or simpler:
    
        ```go
        var principal, years float64 = 1000, 10;
        expectedReturnRate := 0.2;
        ```
    
    *   Or, even simpler:
    
        ```go
        principal, years, expectedReturnRate := 1000.0, 10.0, 0.2;
        ```

### **Basic Types**

Go comes with a couple of built-in basic types:

*   `int` A integer number (e.g., `-5`, `10`, `12` etc)
    *   `uint` An unsigned integer which means a strictly non-negative integer
    *   `int8` A 8-bit signed integer, which is an integer with a specific range from -128 to 127
    *   `uint8` A 8-bit unsigned integer, an integer that can represent values from 0 to 255
    *   `int32` A 32-bit signed integer, which is an integer with a specific range from -2,147,483,648 to 2,147,483,647
    *   `rune` An alias for `int32`, represents a Unicode code point, and is used when dealing with Unicode characters (e.g., 'a', 'ñ', '世')
    *   `uint32` A 32-bit unsigned integer, an integer that can represent values from 0 to 4,294,967,295
    *   `int64` A 64-bit signed integer, an integer that can represent a larger range of values, specifically from -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807
    
*   `float64` a real number (e.g., `-5.2`, `10.123`, `12.9` etc)

*   `string` a text value
    * In Go, strings are enclosed in double quotes (`"`) or backticks (`` ` ``), but not in single quotes (`'`).
    
    * If double quotes (`"`) - to create a interpreted string literals.
    
        * you can use escape sequences as `\n` to break lines 
    
        * You create multiline strings, you can use `\n`
    
            ```go
            message := "This is line one.\nThis is line two.\nThis is line three."
            fmt.Println(message)
            ```
    
    * You can use  backticks (`` ` ``) - to create a raw string literal.
    
        * You can't use escape sequences, for example `` fmt.Print(`a\nb`) `` will print `a\nb`.
    
        * to make multiline strings
    
            ```go
            package main
            
            import "fmt"
            
            func main() {
                message := `This is a multiline string in Go.
            It can span multiple lines
            without needing escape sequences like \n or \t.
            "Quotes" and \slashes\ are taken literally.`
            
                fmt.Println(message)
            }
            ```
    
            
    
*   `bool` `true` or `false`

All Go value types come with a so-called "null value" which is the value stored in a variable if no other value is explicitly set.

-   `int` => `0`
-   `float64` => `0.0`
-   `string` => `""` *(i.e., an empty string)*
-   `bool` => `false`

### `:=` operator

The code

```go
expectedReturnRate := 0.2;
```

Is equivalent of

```go
var expectedReturnRate = 0.2;
```

By convention, you should use this operator as often as possible.

You can't assign type, so when using this operator, you need to trust on the i

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

### fmt.Printf

Printf formats according to a format specifier and writes to standard output. It returns the number of bytes written and any write error encountered.

*   You can find all formatting options in https://pkg.go.dev/fmt

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

*   So to use:

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

*   ```go
    func calculateFutureValues(investmentAmount, expectedReturnRate, years float64) (fv float64, rfv float64) {
    	fv = investmentAmount * math.Pow(1+expectedReturnRate/100, years)
    	rfv = fv / math.Pow(1+inflationRate/100, years)
    
    	return
    }
    ```

    *   You can still returning like `return fv, rfv`. but `return` suffice.
    *   It is recommend to explicitly name the returns `fv float64, rfv float64` and explicitly return all values `return fv, rfv` , mainly if the function is very large - otherwise the function can became very confuse.

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

### `for`, `break` and `continue`

`for` is the unique loop in go

*   ```go
    for i := 0; i < 2; i++ {
    	fmt.Println(i)
    }
    ```
*   ```go
    for someCondition {
      // do something ...
    }
    ```

*   ```go
    for { // infinite loopp
    	...
    }
    ```



You can use `break` to interrupt the loop, or `continue` to finish the current iteration.

## files

### Writing files

```go
func main() {
	balance := 104.1
	balanceText := fmt.Sprint(balance)
	os.WriteFile("balance.txt", []byte(balanceText), 0644)
}
```

### Reading files

```go
func main() {
	data, _ := os.ReadFile("balance.txt")

	balanceText := string(data)
	balance, _ := strconv.ParseFloat(balanceText, 64)

	fmt.Println(balance)
}
```

## Handling errors

Functions don't crash the application, instead it should be returned by functions

*   instead of try-catch, in Go you need to check and handle errors explicitly after each function call that can fail — usually with `if err != nil { ... }`

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

Sure — here’s your text translated into **English**, keeping the technical meaning and style accurate and natural for Go developers:

------

## Defer

-   Used to **delay the execution** of a function until the end of the current function.

-   Very useful for **resource cleanup** (files, connections, unlocks, etc).

-   Example:

    ```go
    func main() {
        f, _ := os.Open("file.txt")
        defer f.Close() // will be executed at the end of main()
    
        fmt.Println("do something...")
    }
    ```

### Notes

#### Execution order (LIFO)

-   Multiple `defer` calls are executed in **reverse order** of registration.
-   If order matters (e.g., releasing `RLock` before `Lock`), be explicit.

```go
mu.RLock()
defer mu.RUnlock()
mu.Lock()
defer mu.Unlock()
// execution order: Unlock() after RUnlock()
```

#### Overhead in hot paths

`defer` has become much cheaper in modern Go versions, but it’s **not free**.

In performance-critical paths (tight loops, frequently called functions), it may be better to:

-   call `Unlock()/Close()` **explicitly** at the end of the block, or
    -   `defer mu.Unlock()` is idiomatic and safe, but **holds the lock until the end of the function**.
    -   If the critical section is small, prefer to limit its scope.
-   move non-critical work outside the loop.

```go
// critical path: avoid defer inside each iteration
for i := 0; i < N; i++ {
    mu.Lock()
    // short work
    mu.Unlock() // instead of defer mu.Unlock()
}
```

#### Defer inside a loop

Each iteration adds a new `defer` that **only runs at the end of the function**, which can cause:

-   holding resources longer than needed,
-   hitting system limits (too many open files, connections, etc.).

```go
// bad: everything is closed only at the end
for _, name := range files {
    f, _ := os.Open(name)
    defer f.Close()
    // ...
}

// better: close per iteration
for _, name := range files {
    f, err := os.Open(name)
    if err != nil { /* handle */; continue }
    // use f
    f.Close()
}
```

#### Immediate evaluation of arguments

-   The arguments of `defer` are evaluated **when the defer is declared**, not when it executes.

    ```go
    // prints the value of x at the moment of the defer
    x := 1
    defer fmt.Println(x) // captures 1
    x = 2
    // output: 1
    ```

-   For anonymous functions, the **variables are closed by reference**:

    ```go
    x := 1
    defer func() { fmt.Println(x) }() // sees x=2
    x = 2
    // output: 2
    ```

#### WaitGroup: use `defer Done()` at the beginning of the goroutine

-   Helps avoid forgetting `Done()` in error/panic paths:

    ```go
    wg.Add(1)
    go func() {
        defer wg.Done()
        // work
    }()
    ```

#### Memory/latency on function exit

-   Many `defer` calls accumulate and increase the work done at function exit (they all fire).
     In functions that may register hundreds or thousands, reconsider the design.

------

## `recover` and `panic`

### `panic`

-   Interrupts the normal flow of the program.

-   Unwinds the stack until it finds a `recover` (or terminates the program if none is found).

-   Simple example:

    ```go
    func main() {
        panic("something went wrong")
        fmt.Println("this will never be executed")
    }
    ```

### `recover`

-   Only works **inside a deferred function**.

    -   If you call `recover()` outside of a `defer`, it always returns `nil`.

-   Captures the value passed to `panic` and **prevents the program from crashing**.

-   you should `return error` for expected problems and `panic` only for truly unexpected or unrecoverable conditions.

-   Remember: `recover` only catches panics from the **same goroutine**.

-   Example:

    ```go
    func main() {
        safe()
        fmt.Println("continues normally")
    }
    
    func safe() {
        defer func() {
            if r := recover(); r != nil {
                fmt.Println("recovered from panic:", r)
            }
        }()
    
        fmt.Println("about to panic...")
        panic("PANIC!!!")
    }
    ```

Output:

```
about to panic...
recovered from panic: PANIC!!!
continues normally
```

------

Would you like me to make it more concise (e.g., for documentation or slides), or keep this full version with explanations?
