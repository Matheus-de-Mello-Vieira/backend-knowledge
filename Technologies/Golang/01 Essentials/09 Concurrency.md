# Concurrency in Go

## **Goroutine**

-   Created with the keyword `go`, example:

    ```go
    go func() {
        // concurrent code
    }()
    ```

-   Executes concurrently with the main function and other goroutines.

## Sync

The **`sync`** package provides synchronization primitives — such as `Mutex`, `WaitGroup`, `Once`, and `Cond` — which allow you to coordinate access to shared resources and control execution among multiple goroutines.

### **`sync.Once`**

-   Ensures that a block of code executes **only once**, even across multiple goroutines.

    ```go
    var once sync.Once
    once.Do(func() {
        fmt.Println("executes only once")
    })
    ```

-   Commonly used for initializations (singleton, cache, etc.).

### **`sync.Cond`**

-   A **condition variable** mechanism for more advanced synchronization.

-   Allows goroutines to wait for a specific signal before proceeding.

    ```go
    var mu sync.Mutex
    cond := sync.NewCond(&mu)
    
    go func() {
        mu.Lock()
        cond.Wait() // waits for signal
        fmt.Println("woke up")
        mu.Unlock()
    }()
    
    time.Sleep(time.Second)
    mu.Lock()
    cond.Signal() // wakes one goroutine
    mu.Unlock()
    ```

### **`sync/atomic`**

-   **Atomic operations** on variables (integers, pointers).

-   Avoids the use of `Mutex` in simple cases (counters, flags).

    ```go
    var counter int32
    atomic.AddInt32(&counter, 1)
    v := atomic.LoadInt32(&counter)
    ```

### **WaitGroup**

-   A counter used to **wait for goroutines to finish**.
-   Main methods:
    -   `.Add(1)` → increments the counter (usually when starting a goroutine).
    -   `.Done()` → decrements the counter (when the goroutine finishes).
    -   `.Wait()` → blocks until the counter reaches **zero**.

```go
package main

import (
	"fmt"
	"sync"
	"time"
)

func worker(id int, wg *sync.WaitGroup) {
	defer wg.Done()
	fmt.Printf("Worker %d starting\n", id)
	time.Sleep(time.Second)
	fmt.Printf("Worker %d done\n", id)
}

func main() {
	var wg sync.WaitGroup

	for i := 1; i <= 3; i++ {
		wg.Add(1)
		go worker(i, &wg)
	}

	wg.Wait()
	fmt.Println("All workers done")
}
```

### **Mutex**

-   Used to protect shared resources from simultaneous access.
-   Types:
    -   **`sync.Mutex`** → simple lock.
        -   `.Lock()` / `.Unlock()`
    -   **`sync.RWMutex`** → read/write lock.
        -   `.RLock()` / `.RUnlock()` → multiple readers can access simultaneously.
        -   `.Lock()` / `.Unlock()` → only one writer, blocks readers and other writers.

## **Channel**

-   Used to **exchange data between goroutines**.

-   Creation:

    ```go
    var c = make(chan int)       // unbuffered
    var c = make(chan int, 5)    // buffered with capacity 5
    ```

    -   `make(chan int)` is equivalent to `make(chan int, 0)` (no buffer).

-   Sending values:

    ```go
    c <- 1
    ```

    -   If the buffer is full, the goroutine **blocks** until someone receives.

-   Receiving values:

    ```go
    i := <-c
    ```

    -   If there’s no value, the goroutine **blocks** until someone sends.

-   Iterating over a channel:

    ```go
    for i := range c {
        fmt.Println(i)
    }
    ```

### Closing channels

-   Close a channel when no one will send to it anymore:

    ```go
    close(c)
    ```

-   Important to avoid **blocked goroutines**.

-   When iterating with `for range`, the loop ends when the channel is closed.

### Trick: Using Channel as a Semaphore

A **buffered channel** of size `n` can hold **at most `n` values**.

You can use this channel as a “token bucket”:

-   To **enter the critical section**, the goroutine sends (`c <- struct{}{}`) → if it’s full, it blocks until one is released.
-   To **leave**, the goroutine consumes (`<-c`) → freeing a spot for another.

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	sem := make(chan struct{}, 2)

	for i := 1; i <= 5; i++ {
		go func(id int) {
			sem <- struct{}{}
			fmt.Println("Worker", id, "started")
			time.Sleep(2 * time.Second)
			fmt.Println("Worker", id, "finished")
			<-sem
		}(i)
	}

	time.Sleep(7 * time.Second)
}
```

## **Select**

-   Similar to `switch`, but for channels.

-   Waits until **one of the channels** is ready to send or receive.

-   Example:

    ```go
    func sendMessage(chickenChannel, tofuChannel chan string) {
        select {
        case website := <-chickenChannel:
            fmt.Printf("Text Sent: Found deal on chicken at %v.", website)
        case website := <-tofuChannel:
            fmt.Printf("Email Sent: Found deal on tofu at %v.", website)
        }
    }
    ```

-   Features:

    -   Executes **one block at a time** (not a loop).
    -   If **more than one channel** is ready, Go picks **randomly**.
    -   If **no channel** is ready, it **waits**.

### Select + default

The `default` clause allows **non-blocking** operation.

```go
select {
case msg := <-c:
    fmt.Println("received:", msg)
default:
    fmt.Println("no message")
}
```

## Ticker and Timer (`time` package)

**Timer** → triggers an event **once** after a period.

```go
timer := time.NewTimer(2 * time.Second)
<-timer.C
fmt.Println("after 2s")
```

**Ticker** → triggers events **periodically**.

```go
ticker := time.NewTicker(1 * time.Second)
for t := range ticker.C {
    fmt.Println("tick:", t)
}
```

## Defer

-   Used to **delay execution** of a function until the surrounding function returns.
-   Useful for **closing resources** (files, connections, unlocks, etc.).

Example:

```go
func main() {
    f, _ := os.Open("file.txt")
    defer f.Close() // executed at the end of main()
    fmt.Println("doing something...")
}
```

### Notes

#### Execution order (LIFO)

-   Multiple `defer`s execute in **reverse order**.
-   If order matters (e.g. release `RLock` before `Lock`), be explicit.

```go
mu.RLock()
defer mu.RUnlock()
mu.Lock()
defer mu.Unlock()
// executes Unlock() then RUnlock()
```

#### Overhead in hot paths

`defer` is cheaper in modern Go versions but **not free**.

In tight loops or highly-called functions, consider explicit cleanup.

```go
for i := 0; i < N; i++ {
    mu.Lock()
    // short work
    mu.Unlock()
}
```

#### Defer inside loops

Each iteration adds a `defer` that runs only at function exit → risk of:

-   holding resources longer than needed,
-   hitting system limits (too many open files, etc.).

```go
// bad: closes all at the end
for _, name := range files {
    f, _ := os.Open(name)
    defer f.Close()
}
// better:
for _, name := range files {
    f, err := os.Open(name)
    if err != nil { continue }
    // use f
    f.Close()
}
```

#### Immediate argument evaluation

-   `defer` arguments are evaluated immediately when declared.

    ```go
    x := 1
    defer fmt.Println(x)
    x = 2
    // output: 1
    ```

-   Anonymous functions close over variables by reference:

    ```go
    x := 1
    defer func() { fmt.Println(x) }()
    x = 2
    // output: 2
    ```

#### WaitGroup: use `defer Done()` at start of goroutine

```go
wg.Add(1)
go func() {
    defer wg.Done()
    // work
}()
```

#### Memory/latency on exit

Too many deferred calls increase cleanup work at return; redesign if necessary.

## `recover` and `panic`

### `panic`

-   Stops normal execution flow.
-   Unwinds the stack until a `recover` is found (or exits the program).

```go
func main() {
    panic("something went wrong")
    fmt.Println("this will never run")
}
```

### `recover`

-   Only works **inside a deferred function**.
-   Captures the value passed to `panic` and **prevents program crash**.
-   Only catches panics in the **same goroutine**.

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

## Context

A `context` is an object passed to functions/goroutines that carries **cancellation, timeout, or request-scoped values**.

* by convention, the context is always the first parameter.

Main purposes:

1.  **Cancel goroutines as a group** when no longer needed.
2.  **Impose time limits** (timeout or deadline).
3.  **Share immutable values** across calls (e.g., request ID, user info).

### Manual cancellation

```go
func main() {
    ctx, cancel := context.WithCancel(context.Background())

    go worker(ctx, "A")
    go worker(ctx, "B")

    time.Sleep(2 * time.Second)
    cancel() // signals cancellation

    time.Sleep(time.Second)
}

func worker(ctx context.Context, name string) {
    for {
        select {
        case <-ctx.Done():
            fmt.Println("Worker", name, "stopped:", ctx.Err())
            return
        default:
            fmt.Println("Worker", name, "working...")
            time.Sleep(500 * time.Millisecond)
        }
    }
}
```

### Timeout (`WithTimeout`)

Creates a context that cancels automatically after the specified duration.

```go
ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
defer cancel()

select {
case <-time.After(3 * time.Second):
    fmt.Println("took too long")
case <-ctx.Done():
    fmt.Println("cancelled:", ctx.Err())
}
```

### Deadline (`WithDeadline`)

Same as timeout, but with a **specific expiration time**.

```go
deadline := time.Now().Add(1 * time.Second)
ctx, cancel := context.WithDeadline(context.Background(), deadline)
defer cancel()
```

### `WithValue`

`context.WithValue` is a function in Go’s **`context`** package used to create a new context that carries a **key–value pair**.

* It’s primarily used to pass request-scoped data **down a call chain**, such as through functions or goroutines, **without using global variables**.

```go
func main() {
    ctx := context.Background()

    // Create a new context with a key-value pair
    ctx = context.WithValue(ctx, "userID", 42)

    // Pass context down the call chain
    processRequest(ctx)
}

func processRequest(ctx context.Context) {
    // Retrieve value from context
    userID := ctx.Value("userID")

    if userID != nil {
        fmt.Println("User ID:", userID)
    } else {
        fmt.Println("No user ID found")
    }
}
```

#### When to Use:

- For **request-scoped data** that is **cross-cutting**, such as:
  - Tracing IDs
  - Authentication tokens
  - Request metadata
- When **passing data through layers** of your application (middleware, handlers, services, etc.)

#### When NOT to Use:

- **Do not use it for optional parameters or general data passing.**
  - That’s better handled by function parameters or struct fields.
- **Keys should be unexported custom types** to avoid collisions.

## `errgroup`

`errgroup` is a wrapper around goroutines + WaitGroup + context, simplifying concurrent task execution and error collection.

-   When running multiple goroutines with `sync.WaitGroup`, if one fails you must:
    -   handle the error manually,
    -   synchronize access,
    -   and remember to cancel other goroutines.
-   `errgroup` does all of this **automatically**:
    -   Add goroutines with `g.Go(func() error { ... })`.
    -   If one returns an error, it cancels the context.
    -   `g.Wait()` returns the first non-nil error (or `nil` if all succeeded).

```go
package main

import (
	"fmt"
	"net/http"
	"golang.org/x/sync/errgroup"
)

func fetch(urls []string) error {
	var g errgroup.Group

	for _, url := range urls {
		u := url
		g.Go(func() error {
			resp, err := http.Get(u)
			if err != nil {
				return err
			}
			defer resp.Body.Close()
			fmt.Println("ok:", u)
			return nil
		})
	}

	return g.Wait()
}

func main() {
	urls := []string{
		"https://golang.org",
		"https://httpstat.us/503",
		"https://github.com",
	}

	if err := fetch(urls); err != nil {
		fmt.Println("Error:", err)
	} else {
		fmt.Println("All good!")
	}
}
```