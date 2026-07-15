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
    
    ready := false
    
    go func() {
        mu.Lock()
        for !ready {
            cond.Wait()
        }
        mu.Unlock()
        fmt.Println("woke up")
    }()
    
    mu.Lock()
    ready = true
    cond.Signal()
    mu.Unlock()
    ```

- `sync.Cond` **does not remember signals** — if `Signal()` is called when no goroutine is waiting, the signal is lost

- Calling `Wait()` after a lost signal can block **forever**

- A `sync.Cond` must always be paired with a **shared condition (predicate)** protected by the same mutex

- `Wait()` must be called inside a **`for` loop**, not an `if`, to re-check the condition after waking

- The loop is required to handle **missed signals**, **spurious wakeups**, and **multiple waiters**

- Using `time.Sleep` to “ensure” ordering is **not correct synchronization**

- For simple one-time notifications, an **unbuffered channel** is usually **simpler and safer** than `sync.Cond`

  ```go
  ch := make(chan struct{})
  
  go func() {
      <-ch
      fmt.Println("woke up")
  }()
  
  ch <- struct{}{}
  ```

### `sync/atomic`

-   **Atomic operations** on variables (integers, pointers).

-   Avoids the use of `Mutex` in simple cases (counters, flags).

    ```go
    var counter int32
    atomic.AddInt32(&counter, 1)
    v := atomic.LoadInt32(&counter)
    ```

- **CompareAndSwap (CAS)**: A fundamental primitive that updates a value only if it matches an "old" value. This is the basis for lock-free algorithms.

  ```go
  var counter int32
  // Basic Add and Load
  atomic.AddInt32(&counter, 1)
  v := atomic.LoadInt32(&counter)
  
  // CompareAndSwapInt32(addr, old, new) bool
  // Only sets counter to 100 if its current value is 1
  swapped := atomic.CompareAndSwapInt32(&counter, 1, 100)
  ```

  The `CompareAndSwap` function returns a boolean:

  - **`true`**: The current value matched the `old` value, and the `new` value was successfully stored.
  - **`false`**: The current value did not match (meaning another goroutine changed it first), and no update occurred.


### sync.Pool

* lets you **reuse temporary objects** that are:

  - Expensive to allocate

  - Short-lived

  - Used frequently

  - Safe to discard at any time

* Typical examples:

  - Buffers (`[]byte`, `bytes.Buffer`)
  - Temporary structs
  - Encoding/decoding scratch space

* `sync.Pool` assumes: “Objects are cheap to lose and cheap to recreate.”

```go
var bufPool = sync.Pool{
    New: func() any {
        return make([]byte, 0, 4096)
    },
}

func handle() {
    buf := bufPool.Get().([]byte)
    defer bufPool.Put(buf[:0]) // reset before putting back

    // use buf
}
```

Where

- `Get()` → returns an object or calls `New()`
- `Put(x)` → returns an object to the pool

Critial behavior

* **Objects can disappear at any time**: The runtime may clear the pool during garbage collection.
* **Per-P sharding**: Internally, sync.Pool keeps per-P (processor) local pools.
  * Objects tend to be reused by the same goroutine
  * Cross-goroutine reuse is not guaranteed

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

### `sync.singleflight`

* `singleflight` is a concurrency pattern (and a specific Go package) designed to prevent "cache stampedes" or the "thundering herd problem."

* It ensures that if multiple concurrent processes ask for the same thing at the same time, the expensive operation (like a database query or API call) is performed only **once**, and the result is shared among all the callers.

#### `Do(key, fn)`

```go
var g singleflight.Group

key := "user:10"

for i := 0; i < 5; i++ {
  go func(reqID int) {
    val, err, shared := g.Do(key, func() (interface{}, error) {
      // it will be executed once 
      return getProfileFromDB(10), nil
    })

    ...

    // it will be executed five times
    fmt.Printf("Req %d got: %v (Shared? %v)\n", reqID, val, shared)
  }(i)
}
```

- **Behavior:** Executes the given function `fn` for the given `key`. If there is already a `fn` running for that `key`, it blocks until the original finishes and returns the same result.

  - It is blocking, if you need an non-blocking behavior, use `DoChan(key, fn)`

  - `singleflight` automatically removes the key once the function finishes.

    ```mermaid
    sequenceDiagram
        autonumber
        participant ClientA as Client A
        participant ClientB as Client B (Concurrent)
        participant ClientC as Client C (Later)
        participant SG as singleflight.Group
        participant DB as Expensive DB/API Call
    
        note over ClientA, DB: === Phase 1: Concurrent Requests (Coalescing) ===
    
        ClientA->>+SG: g.Do("my-key", fn)
        note right of SG: SG checks map: "my-key" not found.<br/>Marks "my-key" as running.
        SG->>+DB: Execute function (Call ID: 101)
    
        note right of ClientB: Client B arrives while<br/>Call ID 101 is still running.
        ClientB->>SG: g.Do("my-key", fn)
        activate SG
        note right of SG: SG checks map: "my-key" is running.<br/>Client B joins the waiting list.
        deactivate SG
    
        DB-->>-SG: Return Result X (from Call ID 101)
    
        par Return to waiters
            SG-->>ClientA: Returns Result X (shared: true)
        and
            SG-->>ClientB: Returns Result X (shared: true)
        end
    
        note right of SG: CRITICAL STEP:<br/>Function finished.<br/>SG removes "my-key" from internal map.
        deactivate SG
    
        note over ClientA, DB: === Wait time passes... ===
    
        note over ClientA, DB: === Phase 2: Request after finishing (No Caching) ===
    
        ClientC->>+SG: g.Do("my-key", fn)
        note right of SG: SG checks map: "my-key" not found (it was removed).<br/>Marks "my-key" as running fresh.
        SG->>+DB: Execute function AGAIN (Call ID: 102)
        DB-->>-SG: Return Result Y (from Call ID 102)
        SG-->>-ClientC: Returns Result Y (shared: false)
        note right of SG: SG removes "my-key" from map.
    ```

    

- **Returns:** `(v interface{}, err error, shared bool)`

  - `v`: The result data.
  - `shared`: `true` if this result was shared with other callers; `false` if this was the only caller.

#### `DoChan(key, fn)`

```go
ch := g.DoChan("key", expensiveFunc)
select {
case res := <-ch:
    fmt.Println(res.Val)
case <-time.After(500 * time.Millisecond):
    fmt.Println("Timeout!")
}
```

- **Behavior:** The non-blocking (async) version. It returns a channel immediately ( `<-chan Result`) rather than blocking the goroutine.
- **Use Case:** Useful if you want to implement timeouts using `select`.

#### `Forget(key)`

```go
var g singleflight.Group
slow := func() (any, error) { time.Sleep(time.Second); return "done", nil }

// 1. Start first call (runs for 1s)
go g.Do("key", slow)

time.Sleep(100 * time.Millisecond) // ensure #1 started

// 2. Forget key (unlocks "key" for new callers)
g.Forget("key")

// 3. Start second call immediately
// Because we called Forget, this starts a NEW execution instead of waiting for #1
g.Do("key", slow)
```

- **Behavior:** Removes the key from the map.

  ```mermaid
  sequenceDiagram
      autonumber
      participant G1 as Goroutine 1
      participant Main as Main (Control)
      participant G2 as Goroutine 2
      participant SG as singleflight.Group
      participant Fn as Slow Function
  
      Note over G1, Fn: 1. Start First Call
      G1->>+SG: Do("key", slow)
      SG->>+Fn: Start Execution A (1s)
      
      Note over Main, SG: ... 100ms later ...
  
      Note over Main, SG: 2. Call Forget
      Main->>SG: Forget("key")
      Note right of SG: Map entry for "key" is deleted.<br/>(Execution A is still running!)
  
      Note over G2, Fn: 3. Start Second Call
      G2->>+SG: Do("key", slow)
      Note right of SG: SG sees no entry for "key".<br/>Must start fresh.
      SG->>+Fn: Start Execution B (1s)
  
      Note right of Fn: ⚠️ Both Execution A and B<br/>are running simultaneously.
  
      Fn-->>-SG: Execution A returns
      SG-->>-G1: Returns result "A"
  
      Fn-->>-SG: Execution B returns
      SG-->>-G2: Returns result "B"
  ```

- **User Case**: `Forget` is mostly used if you want to manually cancel/remove a key *while* the function is still potentially running (rare) or if you are managing sophisticated invalidation strategies.

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

### `context.Background`

`context.Background()` returns a non-nil, empty context.

- It is typically used as the **root context** of an application.
- It is never cancelled.
- It has no deadline.
- It contains no values.

```go
func main() {
    ctx := context.Background()
    processRequest(ctx)
}

func processRequest(ctx context.Context) {
    // work
}
```

#### When to Use:

- At the entry point of an application, such as `main`.
- At the beginning of a request-processing chain when no parent context exists.
- In initialization code, background jobs, tests, or command-line applications.

```go
func main() {
    ctx := context.Background()

    if err := run(ctx); err != nil {
        log.Fatal(err)
    }
}
```

#### When NOT to Use:

- Do not replace an existing context with `context.Background()`.
- Do not use it inside a call chain when the caller already provides a context.
- Creating a new background context discards cancellation, deadlines, and request-scoped values from the parent.

```go
// bad: discards the caller's context
func handleRequest(ctx context.Context) {
    process(context.Background())
}

// better: propagates the existing context
func handleRequest(ctx context.Context) {
    process(ctx)
}
```

### `context.TODO`

`context.TODO()` returns a non-nil, empty context.

- It is used when a function requires a `context.Context`, but the correct context has not been decided yet.
- It behaves like `context.Background()`:
    - It is never cancelled.
    - It has no deadline.
    - It contains no values.

```go
func process(ctx context.Context) {
    // work
}

func main() {
    process(context.TODO())
}
```

#### When to Use:

- During development when context propagation has not been implemented yet.
- As a temporary placeholder while refactoring code to accept a context.
- When it is unclear which parent context should be used.
#### When NOT to Use:

- Do not use it as a permanent replacement for a request-scoped context.
- Do not use it when an existing context is already available.
- Prefer passing the caller’s context so cancellation, deadlines, and values can propagate correctly.

```go
// bad: discards cancellation and deadline information
func handleRequest(ctx context.Context) {
    process(context.TODO())
}

// better: propagates the existing context
func handleRequest(ctx context.Context) {
    process(ctx)
}
```

The difference is primarily **intent**:
- `context.Background()` indicates an intentionally selected root context.
- `context.TODO()` indicates that the correct context still needs to be determined.
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