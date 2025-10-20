# Unit tests in Go

## Basics

-   Put tests in a file ending with `_test.go`.
-   Import `testing`.
-   Test functions must be `func TestXxx(t *testing.T)`.
-   Run with `go test ./...`.

Example

*   `mathutils.go`

    ```go
    package mathutils
    
    func Add(a, b int) int { return a + b }
    ```

*   `mathutils_test.go`

    ```go
    package mathutils
    
    import "testing"
    
    func TestAdd(t *testing.T) {
    	if got := Add(2, 3); got != 5 {
    		t.Fatalf("Add(2,3) = %d, want 5", got)
    	}
    }
    ```

Now you can run

```
go test ./...
```

You will get

```
?       myapp/golearning/cmd/myapp      [no test files]
ok      myapp/golearning/internal/mathutils     0.001s
```

## Table-driven tests

Table-driven tests are the de facto standard pattern in the Go community.

*   They aren’t enforced by the language or tooling, but they’re so idiomatic that you’ll see them in almost every Go project, including the Go standard library itself.
*   **Go favors simplicity and explicit loops.** There’s no built-in test parameterization framework, so writing a loop over a slice of cases is the simplest and most idiomatic way to test multiple inputs/outputs.
*   **Go’s philosophy:** “Clear is better than clever.” Table-driven tests are just a `for` loop over a literal slice — easy to read, easy to maintain.
*   **Standard library precedent:** Packages like `encoding/json`, `fmt`, `strings`, and many others use this style throughout their tests.

Example:

*   `strings/strings_test.go`:

    ```go
    func TestHasPrefix(t *testing.T) {
        var tests = []struct {
            s, prefix string
            out       bool
        }{
            {"abc", "a", true},
            {"abc", "ab", true},
            {"abc", "x", false},
        }
        for _, tt := range tests {
            if out := HasPrefix(tt.s, tt.prefix); out != tt.out {
                t.Errorf("HasPrefix(%q,%q) = %v, want %v", tt.s, tt.prefix, out, tt.out)
            }
        }
    }
    ```

### Parallel tests

You can speed up indepedent tests using `t.Parallel()`

```go
func TestAdd_Table(t *testing.T) {
	tests := []struct{
		name     string
        a, b     int
		want     int
	}{
		{"small", 1, 2, 3},
		{"negatives", -2, -3, -5},
		{"mix", -1, 5, 4},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
            t.Parallel() // optional: speeds up independent tests
			got := Add(tt.a, tt.b)
			if got != tt.want {
				t.Fatalf("Add(%d,%d) = %d; want %d", tt.a, tt.b, got, tt.want)
			}
		})
	}
}
```

## Testing panics

You can capture panics using `recover`

```go
func mustPositive(n int) int {
	if n < 0 { panic("negative") }
	return n
}

func TestMustPositive_Panic(t *testing.T) {
	defer func() {
		if r := recover(); r == nil {
			t.Fatal("expected panic, got none")
		}
	}()
	mustPositive(-1)
}
```

## Test helpers & setup/teardown

```go
func requireEqual[T comparable](t *testing.T, got, want T) {
	t.Helper() // marks this as a helper for cleaner failure lines
	if got != want {
		t.Fatalf("got %v, want %v", got, want)
	}
}

func TestSomething(t *testing.T) {
	t.Cleanup(func(){ /* teardown */ })
	requireEqual(t, 10, 10)
}
```

## Subtests for groups/cases

```go
func TestGroup(t *testing.T) {
	t.Run("case A", func(t *testing.T){ /* ... */ })
	t.Run("case B", func(t *testing.T){ /* ... */ })
}
```

## Benchmarks

Benchmarks in Go are just special test functions that **measure performance** — how fast or how memory-efficient your code is.

They live in `_test.go` files, just like unit tests, but:

-   Their function name must start with `Benchmark`
-   Their signature is `func(b *testing.B)`
-   You run them with `go test -bench .`
    -   you need be on the folder of the `.go` file

```go
package mathutils

import "testing"

// mathutils_test.go
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Add(10, 20)
    }
}
```

Go automatically:

1.  Figures out how many iterations (`b.N`) are needed to get stable timing results.
    *   The total benchmark lasts roughly 1 second.
2.  Runs the loop multiple times.
3.  Reports how long each operation took.

Output looks like:

```
BenchmarkAdd-8   	1000000000	         0.25 ns/op
```

Where:

*   `BenchmarkAdd-8`: Name of the benchmark + number of logical CPUs used (8 threads).
*   `1000000000` The number of iterations (`b.N`) Go ran your function.
*   `0.25 ns/op` Average time per operation (each iteration took 0.25 nanoseconds).

### Memory Benchmarking

If your function allocates memory, Go can report allocations too.

Example:

```go
func Concat(a, b string) string {
    return a + b
}

// Sink is a package-level variable used to prevent compiler optimizations.
// Assigning benchmark results to Sink makes the result escape to the heap,
// because the compiler must assume that code outside this function could read it.
// This prevents Go from optimizing the value away or keeping it on the stack,
// ensuring that the benchmark measures real allocations and execution cost.
var Sink string

func BenchmarkConcat(b *testing.B) {
	a := "hello"
    for i := 0; i < b.N; i++ {
        s2 := fmt.Sprintf("%d", i&7) // small dynamic string
		Sink = Concat(a, s2)
    }
}
```

If you run on the folder of the above `.go`:

```bash
go test -bench . -benchmem
```

You will get:

```
BenchmarkConcat-8       21127501                62.84 ns/op            8 B/op          1 allocs/op
```
Where:
*   `BenchmarkAdd-8`: Name of the benchmark + number of logical CPUs used (8 threads).
*  `21127501` The number of iterations (`b.N`) Go ran your function.
*  `62.84 ns/op` Average time per operation (each iteration took 50 nanoseconds).
* `8 B/op` Each operation allocated 16 bytes of heap memory.
*   `1 allocs/op` Each operation made 1 memory allocation
    *   Fewer allocations generally mean better performance, especially for high-frequency code paths (e.g., tight loops or server handlers).
    *   If possible, aim to reduce allocations using techniques like:
        -   Preallocating slices (`make([]T, 0, n)`)
        -   Using `bytes.Buffer` or `strings.Builder`
        -   Reusing objects via sync.Pool

## Code coverage

```bash
go test ./... -cover
go test ./... -coverprofile=coverage.out
go tool cover -html=coverage.out
```

## Fuzz tests

A tool to implement Property-based testing

They live in `_test.go` files, just like unit and benchmark tests, but:

-   Their function name must start with **`Fuzz`**
-   Their signature is **`func(f \*testing.F)`**
-   You run them with:

Example

```go
func FuzzAdd(f *testing.F) {
	f.Add(1, 2) // seed corpus
	f.Fuzz(func(t *testing.T, a, b int) {
		got := Add(a, b)
		// basic invariant: commutative
		if got != Add(b, a) {
			t.Fatalf("not commutative: %d+%d != %d+%d", a, b, b, a)
		}
	})
}
```

Now you run:

```bash
go test -fuzz . -run=^$
```

*   It means "Run *only* fuzz tests (all of them), and skip regular unit tests."

*   If you just run `go test -fuzz .`, Go will first run all regular tests, then fuzz tests.

*   The `-run=^$` part skips the normal ones so fuzzing starts immediately.

*   It will keep fuzzing until you stop it manually (e.g. with `Ctrl + C`), you can specify a time limit using `-fuzztime`.

    *   You can use time values (`s`, `m`, `h`) or input counts (`x` for number of tests).

        *   ```bash
            go test -fuzz=FuzzAdd -run=^$ -fuzztime=5m   # 5 minutes
            go test -fuzz=FuzzAdd -run=^$ -fuzztime=100x # 100 generated inputs total
            ```

    *   After the time (or iteration count) expires, Go stops fuzzing and reports the result.

### Useful variants

| Command                                       | What it does                                |
| --------------------------------------------- | ------------------------------------------- |
| `go test -fuzz=FuzzAdd -run=^$`               | Fuzz only `FuzzAdd`                         |
| `go test -fuzz=FuzzAdd -fuzztime=30s -run=^$` | Fuzz `FuzzAdd` for 30 seconds               |
| `go test -fuzz=FuzzAdd -parallel=4 -run=^$`   | Run up to 4 fuzzing workers                 |
| `go test -fuzz . ./...`                       | Fuzz all packages recursively               |
| `go test -fuzz . -run=^$ -v`                  | Verbose output (shows seeds and crash cases |

## Useful `go test` flags

You also can run `go test` with `-race` to detect data races.

*   `-run=Regex` only run matching tests.
*   `-v` verbose (shows subtests).
*   `-race` detect data races.
*   `-count=1` disable cache (force re-run).
*   `-timeout=2m` change timeout.