# Go Internals

## The Go Runtime Scheduler

Go’s runtime scheduler splits execution into three core entities:

| Symbol | Name      | Represents                                                                                     |
| :----- | :-------- | :--------------------------------------------------------------------------------------------- |
| **G**  | Goroutine | A lightweight user-space thread (your Go functions running concurrently).                      |
| **M**  | Machine   | An actual OS thread that executes Go code.                                                     |
| **P**  | Processor | A logical “context” that owns a run queue of goroutines and local caches (like memory caches). |

### Key Rules of the Scheduler
* Each **M** (OS thread) must have one **P** attached to execute Go code.
* Each **P** can be attached to only one **M** at a time.
* Each **P** holds a run queue of goroutines (**Gs**) that are ready to run.
* The **M** executes those goroutines one at a time by running them on a physical CPU core.
## Processes, Threads, and Goroutines

### Processes
* **Isolation:** Each process has its own separate memory space.
* **Characteristics:** Processes do not share memory directly with each other.

### Threads
* **Non-isolated:** All threads within a single process share the same memory space.
* **Cost:** Threads are not cheap to create or manage because they require more system resources.
* **Initial stack size:** Approximately 1 MB by default on most operating systems.

### Goroutines
* Go utilizes multiple threads under the hood, and the Go runtime automatically handles the mapping of goroutines to OS threads.
* **Initial stack size:** Starts at approximately 2 KB.
* The stack automatically grows and shrinks dynamically as needed, scaling up to gigabytes if required.
* **Analogy:** A *process* is to a *processor* as a *goroutine* is to a *thread*.
## Advanced Scheduling Mechanisms

### Work Stealing (M:N Scheduler)
Go uses an **M:N scheduler**, meaning **M** goroutines run on **N** OS threads, all managed automatically by the Go runtime. The scheduler relies on **work stealing** to balance the load across threads:
* Each OS thread (managed by Go's **P** — a logical processor) keeps its own local run queue of goroutines.
* When a thread finishes its tasks and its local queue becomes empty, it does not simply sit idle.
* Instead, it "steals" work (goroutines) from the run queue of another thread that still has tasks pending.

### Spinning Threads
A **spinning thread** is one that keeps running in a loop checking for work to do, rather than immediately going to sleep when it has nothing immediately available.
* This behavior is called **"busy waiting"** — the thread repeatedly spins to see if new work has arrived.
* Spinning makes sense when new work is expected very soon, because waking a parked thread (the sleep-to-wake cycle) is relatively expensive, and spinning avoids scheduler overhead for short idle periods.
* Go’s scheduler utilizes spinning threads as an optimization.
* If an **M** (thread) has no goroutines to run, it spins briefly before parking (sleeping).
* This way, if a new goroutine becomes ready right away, it can start almost instantly without the delay of waking up a parked thread.
## Memory Management

### Memory Layout Overview
When a Go program runs, its memory is divided mainly into two areas:
* **Stack:** Used for function calls and local variables.
* **Heap:** Used for dynamically allocated data (objects that outlive a single function call).

### Stack Allocation
* Each goroutine (lightweight thread) has its own stack.
* Through **segmented stack management**, the stack starts small (a few KB) and automatically grows or shrinks as needed.
* Data allocated on the stack is automatically freed when the function returns.

### Escape Analysis
The Go compiler runs **escape analysis** to decide whether a variable can safely live on the stack or must be moved to the heap.
* If a variable’s lifetime exceeds the scope of its function (e.g., it is returned or stored in a heap object), the compiler lets it "escape" to the heap.

## Heap Allocation and Garbage Collection

Objects that "escape" go to the heap, which is managed by Go’s **Garbage Collector (GC)**.

### Garbage Collector Characteristics
* **Concurrent:** It runs alongside your program, preventing long pauses.
* **Generational / Tricolor Mark-and-Sweep:** It tracks reachable objects efficiently using basically a breadth-first search (BFS). Order is not strictly managed (e.g., it uses a queue instead of a stack), and multiple gray nodes can be processed in parallel.
* **Non-moving:** It does not relocate objects, which is important for pointer safety and interoperability with C.

### The Tricolor GC Process
1. **Start:** All objects are initially **white**. The GC identifies root objects (globals, goroutine stacks, etc.) and colors them **gray**.
2. **Mark Phase (Tracing):** While there are gray objects, the GC picks one and examines all pointers inside it. For each pointer to a white object, it turns that object **gray** (reachable, but not yet scanned). Once it completes scanning, it colors the current object **black**.
3. **End of Marking:** When no gray objects remain, all reachable objects are black. The remaining white objects are unreachable and safe to reclaim.
4. **Sweep Phase:** The GC frees all **white** (unreachable) objects.

---

## Allocation Mechanics

Frequent allocation of small objects by many concurrent goroutines would cause massive contention—slowing everything down—if every allocation required locking a global heap. 

* Instead, each **P** has its own memory cache (called an `mcache`) for fast allocation.
* When a goroutine running on P1 allocates memory, it can often satisfy that request from P1’s local cache, resulting in no global lock and no contention.

```
Global heap
 ├─ P0 → local mcache
 ├─ P1 → local mcache
 ├─ P2 → local mcache
 ...
```

### Size Classes
To make this efficient, Go divides allocations into **size classes** (buckets):
* Small objects (≤ 32 KB) are rounded up to the nearest size class (e.g., 8 bytes, 16 bytes, 32 bytes).
* Each size class has its own **free lists** and **spans** (blocks of memory that hold multiple objects of that class).
* If you allocate a struct that is 20 bytes, Go gives you a 32-byte block from the "32B" size class.
* This method avoids fragmentation and makes reuse very fast.

### The Allocation Path
When executing `p := new(MyStruct)`, the following path is taken:
1. The compiler determines the size of `MyStruct`.
2. The runtime finds which size class it fits into.
3. The current **P** (processor) checks its local `mcache`:
    * If it has a free block in that size class, it hands it out immediately. This means most small allocations are O(1) — constant time and lock-free.
    * If not, it grabs a new span from the central heap (shared pool) and refills its cache.
4. **For large objects (> 32 KB):** The allocator requests memory directly from the **global heap**, which manages larger spans (multiple pages of memory).
5. The global heap receives memory from the operating system via `mmap` or `brk`.