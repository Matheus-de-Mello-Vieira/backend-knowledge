# Go internals

Go’s runtime scheduler splits execution into three entities

| Symbol | Name      | Represents                                                   |
| ------ | --------- | ------------------------------------------------------------ |
| **G**  | Goroutine | A lightweight user-space thread (your Go functions running concurrently) |
| **M**  | Machine   | An actual OS thread that executes Go code                    |
| **P**  | Processor | A logical “context” that owns a run queue of goroutines and local caches (like memory caches) |

Where;
*   Each **M** (OS thread) must **have one P** to execute Go code.
*   Each **P** can be **attached to only one M at a time**.
*   Each **P** holds the **run queue of goroutines (Gs)* that are ready to run.
*   The **M** executes those Gs (goroutines) one at a time, by running them on a real CPU core.

## Process, theads e goroutine

### Processes

-   **Isolation:** Each process has its own separate memory space.
-   **Characteristics:** Processes do not share memory directly with each other.

### Threads

-   **Non-isolated:** All threads within a process share the same memory space.
-   **Cost:** Threads are not cheap to create or manage — they require more system resources.
-   **Initial stack size:** ~1 MB (by default on most operating systems)

### Goroutines (Go)

-   Go uses multiple threads under the hood and manages scheduling between many goroutines.
-   The Go runtime automatically handles the mapping of goroutines to OS threads.
-   **Initial stack size:** ~2 KB (approximately)
    -   The stack grows and shrinks automatically as needed (up to GBs if required).
-   **Analogy:**
    -   A *process* is to a *processor*
    -   As a *goroutine* is to a *thread*

#### Work Stealing

Go uses a **M:N scheduler**, meaning:

-   **M** goroutines run on **N** OS threads,
-   all managed automatically by the Go runtime.

The scheduler uses **work stealing** to balance load across threads.

*   Each **OS thread** (managed by Go’s “P” — a *logical processor* in Go’s runtime) keeps its own **local run queue** of goroutines.
*   When a thread finishes its tasks and its queue becomes **empty**, it doesn’t just sit idle.
*   Instead, it **“steals”** work — i.e., goroutines — from the **run queue of another thread** that still has tasks.

#### Spinning thread

A **spinning thread** is a thread that **keeps running in a loop**, checking for work to do, **instead of going to sleep** when it has nothing immediately available.

*   This behavior is called **“busy waiting”** — the thread repeatedly *spins* (runs) to see if new work has arrived.
*   Spinning can make sense when:
    -   New work is expected very soon,
    -   Waking up (sleep → wake cycle) is relatively expensive,
    -   You want to avoid scheduler overhead for short idle periods.
*   Go’s scheduler sometimes uses *spinning threads* as an optimization.
    *   If a thread (called an **M** in Go’s runtime) has no goroutines to run, it **spins briefly** before parking (sleeping).
    *   This way, if a new goroutine becomes ready *right away*, it can start almost instantly — no delay from waking up a parked thread.

## `go tool trace`

`go tool trace` is a **powerful profiling and visualization tool** in the Go toolchain.

*   It helps you **see what your Go program was doing over time** — especially how goroutines, threads, and the scheduler interact.

It provides a **timeline view** of:

-   Goroutine creation and execution
-   Network, syscall, and GC (garbage collection) events
-   Scheduler activity
-   Processor usage and work-stealing behavior

You use `go tool trace` to:

-   **Understand performance bottlenecks**
-   **Visualize concurrency** (when and how goroutines run)
-   **Debug scheduling issues** (e.g., goroutines blocked on channels or syscalls)
-   **See GC pauses**
-   **Inspect parallelism** and CPU utilization

### Basic Workflow

Here’s how you typically use it:

#### 1. Generate a trace file

You run your Go program with tracing enabled:

```
go test -trace trace.out
```

or, for a normal Go program:

```
go run main.go
```

(inside your code, you can also manually start a trace — more on that below.)

####  2. View the trace

Then, use the tool to analyze it:

```
go tool trace trace.out
```

This launches an **interactive web UI** in your browser that looks similar to Chrome’s performance tools.

## Memory Management

### Memory Layout Overview

When a Go program runs, its memory is divided mainly into:

-   **Stack** — for function calls and local variables.
-   **Heap** — for dynamically allocated data (objects that outlive a single function call).

### Stack Allocation

-   Each **goroutine** (lightweight thread) has its **own stack**.
-   The stack starts small (a few KB) and **grows or shrinks automatically** as needed — this is called **segmented stack management**.
-   Data allocated on the stack is **automatically freed** when the function returns.

### Escape Analysis

The Go compiler runs **escape analysis** to decide whether a variable can safely live on the stack or must be moved to the heap.

*   If a variable’s lifetime exceeds the scope of its function (e.g., it’s returned or stored in a heap object), the compiler “lets it escape” to the heap.

### Heap Allocation and Garbage Collection

Objects that “escape” go to the **heap**, managed by Go’s **garbage collector (GC)**.

#### The Go GC is:

-   **Concurrent** — runs alongside your program (no long pauses).

-   **Generational / tricolor mark-and-sweep** — tracks reachable objects efficiently.

    -   It is basically a breadth-first (BFS) search, but they don't care about the order (eg.: they use a queue instead of a stack) and multiple gray nodes can be processed paralelly.

    -   Process:

        1)   **Start:**

            -   All objects are initially **white**.

            -   The GC identifies root objects (globals, goroutine stacks, etc.) and colors them **gray**.

        2)   **Mark phase (tracing):**

             -   While there are gray objects:
                 -   The GC picks one gray object.
                 -   It examines all the pointers inside it.
                 -   For each pointer to a white object, it turns that object **gray** (reachable, but not yet scanned).
                 -   Once it’s done, it colors the current object **black**.

             2)   **End of marking:**
                  -   When no gray objects remain, all reachable objects are black.
                      -   The remaining white ones are unreachable — safe to reclaim.

        2)   **Sweep phase:**
             -   GC frees all **white** (unreachable) objects.

-   **Non-moving** — doesn’t relocate objects (important for pointer safety and interoperability with C).

### Allocation Mechanics

-   When many goroutines (and thus threads) run at once, they frequently allocate small objects.
     If every allocation required locking a **global heap**, that would cause massive contention — slowing everything down.

-   Each **P** has its **own memory cache** (called an `mcache`) for fast allocation.

-   So instead of a single shared heap, you have:

    ```sql
    Global heap
     ├─ P0 → local mcache
     ├─ P1 → local mcache
     ├─ P2 → local mcache
     ...
    ```

When a goroutine running on P1 allocates memory, it can often satisfy that request from P1’s local cache — **no global lock, no contention**.

#### Size Classes

To make this efficient, Go divides allocations into **size classes** (buckets).

-   Small objects (≤ 32 KB) are rounded up to the nearest size class — e.g., 8 bytes, 16 bytes, 32 bytes, etc.
-   Each size class has its own **free lists** and **spans** (blocks of memory that hold multiple objects of that class).

```
Size class 1: 8-byte objects
Size class 2: 16-byte objects
Size class 3: 32-byte objects
...
Size class N: up to 32 KB
```

So if you allocate a struct that’s 20 bytes, Go gives you a 32-byte block from the “32B” size class.

This avoids fragmentation and makes reuse very fast.

### The Allocation Path

```go
p := new(MyStruct)
```

1)   The compiler determines the size of MyStruct.

2)   The runtime finds which size class it fits into.

3)   The current P (processor) checks its local mcache:

     *    If it has a free block in that size class, it hands it out immediately. ✅

     *    If not, it grabs a new span from the central heap (shared pool) and refills its cache.

This means most small allocations are O(1) — constant time and lock-free.

For large objects (> 32 KB):

*   The allocator requests memory directly from the **global heap**, which manages larger spans (multiple pages of memory).

*   The global heap gets memory from the **operating system** via `mmap` or `brk`.