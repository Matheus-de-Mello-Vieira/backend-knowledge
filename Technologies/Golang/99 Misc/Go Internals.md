# Go Internals and System Architecture

## Execution Hierarchy and the Go Scheduler

To understand why Go's concurrency is highly efficient, you must look at [how the operating system handles execution boundaries](05%20Process%20Management.md#Processes%20vs.%20Threads), and how the Go runtime works to bypass those heavy hardware limitations.

### Processes and OS Threads (The Kernel's Domain)

- **Processes:** The ultimate resource container. The OS allocates each process a completely isolated virtual address space, managed by hardware Memory Management Units (MMU) and dedicated Page Tables. They cannot directly read each other's memory without heavy Inter-Process Communication (IPC) mechanisms like pipes or shared `mmap` files.
- **OS Threads:** Threads exist within a process, natively sharing the parent's virtual memory (Heap, Data sections, and File Descriptor arrays). However, the OS kernel must still schedule these threads onto physical CPU cores, meaning context switching requires expensive CPU register saving and state restoration. Furthermore, the OS typically parachutes a fixed, contiguous memory block (often 8MB) for each thread's stack, which requires memory Guard Pages to prevent fatal Segmentation Faults.

### Goroutines (User-Space Threads)

- **Microscopic Footprint:** Instead of a rigid OS-level stack, a goroutine starts with a tiny ~2 KB stack.
- **Dynamic Scaling:** Through segmented stack management, a goroutine's stack dynamically grows and shrinks, allowing it to scale up to gigabytes if necessary without wasting massive upfront contiguous virtual memory.

### The M:N Scheduler (G, M, P Model)

Because the OS kernel strictly schedules physical OS threads, the Go runtime acts as an intermediary. It uses an **M:N scheduler** to automatically map thousands of user-space goroutines onto a smaller pool of OS threads. It orchestrates this using three core entities:

|**Symbol**|**Name**|**Represents**|
|---|---|---|
|**G**|Goroutine|A lightweight user-space thread representing your concurrent Go functions.|
|**M**|Machine|An actual OS thread, recognized by the kernel, that executes the Go code on a physical CPU core.|
|**P**|Processor|A logical context that owns a run queue of ready goroutines and local memory caches.|

- **Execution Rules:** Each **M** (OS thread) must have exactly one **P** attached to execute Go code, and each **P** can be attached to only one **M** at a time.
- **Run Queues:** Each **P** maintains a local run queue of ready-to-execute goroutines (**Gs**).
- **Hardware Execution:** The **M** executes these goroutines sequentially by routing them through the physical CPU core's instruction pipeline.
### The Go Runtime

The **Go runtime** is the part of the Go implementation that executes and manages your program after compilation. It sits between your Go code and the operating system, handling language-specific execution mechanics such as goroutine scheduling, stack growth, memory allocation, garbage collection, timers, and coordination with OS threads.

- **What belongs to the runtime:** Goroutine creation, the **G-M-P scheduler**, heap allocation, garbage collection, stack resizing, channel parking and wake-up behavior, and many low-level interactions with the operating system.
- **What does not belong to the runtime:** Your application logic and most standard-library APIs are not themselves the runtime, even though they may call into runtime-managed mechanisms.
## Goroutine Allocation

When you execute a `go` statement, the runtime completely bypasses the OS kernel and executes a highly optimized sequence of user-space memory allocations.

### 1. Allocating the Metadata (The `g` Struct)

Every goroutine is represented by a C-like struct named `g`. This acts as the goroutine's Process Control Block, holding saved values of CPU registers and status flags.

- **Free List Optimization:** The logical processor (**P**) maintains a local list of "dead" `g` structs from finished goroutines.
- If a dead `g` struct is available, the runtime instantly pops it off the list, scrubs it, and reuses it in $O(1)$ constant time. If empty, it allocates a new one on the Heap.

### 2. Allocating the Stack

Unlike OS threads that require system calls for contiguous memory and Guard Pages, a goroutine's stack is just a standard memory block.

- The runtime maps the 2KB request to a specific **Size Class** bucket.
- The **P** checks its private `mcache`. If the 2KB Free List has an empty block, it pulls it instantly without locking the global heap.

#### Stack Growth Checks

Goroutine stacks are dynamically sized rather than fixed. Because a function call may require more stack space than is currently available, the compiler inserts a **stack-growth check** near the beginning of most functions.

Conceptually, the function compares the current Stack Pointer (`sp`) against the goroutine's stack guard. If there is not enough remaining stack space, execution enters the runtime, which grows the goroutine's stack and then resumes the function.

### 3. Initializing the Execution State

To prepare the goroutine for the physical CPU hardware:

- **Stack Boundaries:** The runtime records the top and bottom addresses of the 2KB block. The Go compiler secretly injects software-bounds checking into your functions using these boundaries to dynamically grow the stack instead of relying on hardware Guard Pages.
- **Hardware Registers:** The runtime sets the saved Stack Pointer (`sp`) to the highest address of the 2KB block (stacks grow downwards). It sets the saved Instruction Pointer (`pc`) to the memory address of your target function.

### 4. Enqueueing for Execution

- The runtime pushes the new goroutine onto the **P**'s local run queue (capped at 256 goroutines).
- If full, it spills over to the Global Run Queue. The OS thread (**M**) eventually pops the goroutine, loads its saved `sp` and `pc` into the physical CPU hardware registers, and seamlessly executes it.

## Advanced Scheduling Mechanisms

### Work Stealing

Because CPU cycles are a scarce hardware resource, the Go runtime aggressively balances the workload to keep physical cores fed:

- Every **P** maintains a local queue of active goroutines.
- When a thread (**M**) empties its local queue, it actively "steals" pending goroutines from the run queue of another **P**.

### Spinning Threads (Busy Waiting)

- A spinning thread actively loops and checks for new work instead of immediately going to sleep.
- The OS penalty for waking a sleeping thread (transitioning from Kernel Space back to User Space) is computationally expensive.
- Go intentionally utilizes spinning threads as a hardware optimization to instantly capture new goroutines, prioritizing sub-millisecond execution over strict power efficiency.

### Goroutine Preemption

The Go runtime has its own scheduler for deciding which goroutine (**G**) executes on an OS thread (**M**) using a logical processor (**P**). This scheduling layer is independent from the operating-system scheduler: the OS [preemptively schedules](../../../Operating%20Systems/05%20Process%20Management.md#Cooperative%20vs.%20Preemptive%20Multitasking) the **M**, while the Go runtime decides which **G** that M should execute.

A goroutine cannot be interrupted at an arbitrary instruction unless the runtime knows that its execution state can be safely preserved and inspected. These locations are called **safe points**. The modern runtime distinguishes three categories:

- **Blocked safe point:** the goroutine is already descheduled, such as while blocked on synchronization or a system call.
- **Synchronous safe point:** the running goroutine explicitly reaches a runtime/compiler check where a pending preemption request can be observed.
- **Asynchronous safe point:** the runtime interrupts a running goroutine at an instruction where its stack and register state can still be safely recovered.

Before Go 1.14, goroutine preemption depended primarily on the first two categories. Go 1.14 added asynchronous safe points, allowing the runtime to interrupt many long-running goroutines without waiting for them to naturally reach a synchronous check.

#### Before Go 1.14: Synchronous Preemption

Before asynchronous preemption existed, the runtime could **request** that a goroutine stop, but it generally could not immediately interrupt arbitrary Go code. The goroutine first had to reach a synchronous safe point, historically associated mainly with function calls. This made the mechanism cooperative-like: the runtime initiated the request, but the running goroutine had to execute code containing a preemption check before the request could actually take effect.

The runtime reused the compiler-inserted stack-growth checks described in [Stack Growth Checks](#Stack%20Growth%20Checks) for preemption. When it wanted to preempt a goroutine, it set a preemption flag and replaced the goroutine's normal stack guard (`stackguard0`) with the special `stackPreempt` value. The next function Nested Calls would therefore make the ordinary stack check appear to fail. Execution entered the stack-growth path, where the runtime recognized that this was actually a **preemption request**, rather than a real stack overflow, and transferred control to the scheduler.

Conceptually:

`preemption requested → stackguard0 = stackPreempt → next function call → stack check fails → runtime detects preemption → scheduler`

This approach was cheap because Go could reuse checks that were already necessary for stack growth instead of injecting a separate scheduler check into every instruction or loop iteration.

The weakness was code that did not reach one of those checks. Consider:

```go
for {
    x++
}
```

If the compiler generated a tight loop with no function calls or other safe points, the goroutine could continue executing for an arbitrarily long time. A pending preemption request existed, but the goroutine never executed the stack check required to observe it. This could delay other goroutines and, more importantly, delay operations such as garbage collection that need running goroutines to reach safe states. The Go runtime tracked this limitation for years as the “tight loops should be preemptible” problem.

Blocking operations did not have the same problem. If a goroutine blocked on a channel, synchronization primitive, system call, or another operation that descheduled it, it naturally entered a **blocked safe point** and stopped consuming its P.

#### `sysmon` and Preemption Requests

Go also has a special runtime monitoring thread called **`sysmon`**. It runs independently of the normal G-M-P execution path—it does not require a P—and performs several runtime maintenance tasks, including monitoring long-running execution, network polling, and reclaiming Ps associated with long system calls.

For scheduling fairness, `sysmon` periodically calls `retake`, which examines running Ps. The runtime currently defines `forcePreemptNS` as **10 ms**. If a P remains on the same scheduling tick for roughly that duration, `retake` calls `preemptone(pp)` to request preemption. This is a scheduling target rather than a guarantee that every goroutine executes for exactly 10 ms.

`preemptone` locates the M and G currently associated with that P and marks the goroutine for preemption:

```text
gp.preempt = true
gp.stackguard0 = stackPreempt
```

The `stackguard0` modification preserves the synchronous preemption mechanism described above. In modern Go, however, `preemptone` can additionally request **asynchronous preemption** of the M.

This means `sysmon` does **not** itself rip a goroutine from the CPU. Its role is primarily:

`observe long-running P → request preemption`

The actual interruption and transition into the scheduler are handled by the rest of the runtime and, for asynchronous preemption, platform-specific OS mechanisms.

#### Go 1.14+: Asynchronous Preemption

Go 1.14 added **asynchronous goroutine preemption**. The key improvement is that a running goroutine no longer always has to reach the next function-prologue stack check before the runtime can interrupt it. Loops without function calls therefore no longer have the same ability to indefinitely delay scheduling or garbage collection.

Importantly, asynchronous preemption did **not replace** the old mechanism. Modern Go still uses blocked and synchronous safe points. Asynchronous safe points were added as another way to stop a goroutine when synchronous preemption would take too long.

The process begins similarly. `sysmon` notices that execution has exceeded the scheduler's target time slice, `retake` calls `preemptone`, and the goroutine is marked for preemption. But if asynchronous preemption is supported, `preemptone` also marks the P and calls the platform-specific `preemptM` mechanism for the M currently executing the goroutine.

On Unix-like systems, `preemptM` sends a signal to the target OS thread. Go currently uses **`SIGURG`** as its dedicated non-cooperative preemption signal. The signal interrupts the M at whatever instruction it happens to be executing and transfers control temporarily to the Go runtime's signal handler.

Receiving the signal does **not** automatically mean the goroutine can be stopped at that exact instruction. The runtime first examines the interrupted Program Counter, Stack Pointer, registers, and runtime state to determine whether execution is currently at an **asynchronous safe point**. Some runtime regions cannot safely be preempted—for example, while the M is holding certain runtime locks, allocating memory, executing a system call, or otherwise maintaining runtime invariants.

If the location is not safe, the signal handler does not force the switch there. The synchronous preemption request remains pending, and another asynchronous attempt can occur later.

If the instruction **is** an asynchronous safe point, the runtime modifies the interrupted thread's saved execution context. Instead of returning directly to the instruction that was interrupted, it changes the context so that the thread appears to have called a runtime assembly function named **`asyncPreempt`**. The signal handler then returns normally.

Conceptually:

`sysmon → retake → preemptone → preemptM → OS interrupts M → check async safe point → inject asyncPreempt`

`asyncPreempt` is architecture-specific assembly because the interruption may occur at essentially any safe instruction, meaning ordinary calling-convention assumptions cannot be relied upon. It saves the general-purpose registers—and, where necessary, additional register state—before transferring execution into Go runtime code.

The Go continuation, `asyncPreempt2`, then switches to the system stack and either parks the goroutine or calls the scheduler's normal preemption path. The scheduler can place the interrupted goroutine back into a runnable state and choose another G to execute on the P. Later, when the original goroutine is scheduled again, its preserved state allows it to resume from the point where it was interrupted.

One complication of asynchronous interruption is **garbage collection**. At synchronous safe points the compiler/runtime has precise information about where pointers live on the stack. At an asynchronous safe point, however, execution may be between the compiler's normal precise stack-map locations. The runtime therefore preserves register state and conservatively scans the relevant asynchronous frame so potential pointers are not accidentally treated as non-pointers and collected.

Therefore, the evolution can be summarized as:

**Before Go 1.14**

`runtime requests preemption → G must reach a synchronous safe point → usually next function/stack check → scheduler`

A tight loop without such a safe point could run for a very long time despite a pending preemption request.

**Go 1.14+**

`runtime requests preemption → try asynchronous interruption → if current instruction is safe, inject asyncPreempt → save registers → scheduler`

If asynchronous interruption cannot safely happen at that moment, the existing synchronous mechanism remains available as a fallback.

The result is that modern Go combines **blocked, synchronous, and asynchronous safe points**, giving the runtime much stronger control over long-running goroutines while still preserving the invariants required for stack management and garbage collection.
## Memory Management

Go applications rely on the [classic virtual memory layout established by the operating system](02%20The%20Anatomy%20of%20a%20Process.md#Process%20Execution%20and%20State).

### Stack vs. Heap Allocation

- **The Stack:** Operates strictly as a contiguous, Last-In, First-Out (LIFO) structure. Because it benefits from excellent spatial locality, the CPU can cache it highly efficiently. Goroutine local variables are automatically freed when the function frame collapses.
- **The Heap:** A massive, upward-growing virtual memory region used for dynamic allocations. Memory placed here is globally accessible but takes longer to access due to pointer chasing and potential L1 cache misses.

### Escape Analysis

- The Go compiler [mathematically analyzes variable lifespans at compile time](02%20The%20Anatomy%20of%20a%20Process.md#The%20Heap).
- If the compiler detects that a variable's reference "escapes" the local function's scope, it automatically moves the allocation off the Stack and onto the Heap.

## Garbage Collection (GC)

Objects that escape to the heap must eventually be cleaned up. Unlike C or C++ which require manual `free()` calls—creating extreme risks for Memory Leaks, Double-Frees, and Dangling Pointers—Go automates this.

### Characteristics

- **Concurrent:** Runs continuously alongside the program to prevent full application freezes.
- **Non-moving:** It does not shuffle physical memory addresses around, ensuring pointer stability and allowing seamless interoperability with C code.
- **Tricolor Mark-and-Sweep:** Go tracks reachable objects using a highly optimized breadth-first search.

### The Tricolor Process

1. All objects begin as **White**.
2. The GC identifies root objects (globals, active goroutine stacks) and colors them **Gray**.
3. **Tracing:** The GC inspects Gray objects. Any White object referenced by a Gray object is also colored Gray.
4. Once an object is fully scanned, it is colored **Black**.
5. **Sweeping:** When no Gray objects remain, the GC reclaims the memory of all remaining White (unreachable) objects.

## Low-Level Allocation Mechanics

If thousands of goroutines attempted to allocate heap memory simultaneously, it would trigger a massive hardware bottleneck. Constant atomic locking on a global heap would force CPU cores to [invalidate each other's L1 caches via the MESI protocol (False Sharing)](04%20Inside%20The%20CPU.md#The%20Developer%20Trap:%20False%20Sharing).

Go prevents this hardware collision using highly localized allocation:

### Local Memory Caches (`mcache`)

- Each logical processor (**P**) is assigned its own private memory cache called an `mcache`.
- When a goroutine needs heap memory, it requests it directly from its local `mcache`, bypassing global locks and ensuring the data remains safely within the physical CPU core's private L1/L2 cache.

### Size Classes (Slabs)

- To prevent the OS-level [External Fragmentation that plagues raw physical memory](03%20Memory%20Management.md#Limitations%20of%20physical%20memory), Go categorizes small objects (≤ 32 KB) into strict size classes (e.g., 8 bytes, 16 bytes).
- If you allocate a 20-byte struct, Go immediately assigns it an optimized 32-byte memory block from the correct bucket.

### The Full Allocation Path (e.g., `new(MyStruct)`)

1. **Size Classification:** The compiler calculates the exact byte size of `MyStruct` and assigns it to a standardized Size Class bucket.
2. **The Fast Path (Local `mcache`):** The active **P** checks its private `mcache` for an empty block. If available, it executes in constant $O(1)$ time with zero locking.
3. **The Refill Path (Central Heap):** If the `mcache` is empty, the **P** reaches out to the central Go heap, locks it briefly to grab a bulk "span" of memory, and refills its local cache.
4. **The OS Fallback (System Calls):** If the global Go heap runs out of space or for objects > 32 KB, the runtime asks the OS kernel for pure, [zero-filled physical RAM via Anonymous Mapping](03%20Memory%20Management.md#Anonymous%20Mapping%20(%60MAP_ANONYMOUS%60)) (using `mmap` or `brk`).

## Handling Network Connections

When building backend servers, [the architecture](02%20Application%20Server%20Concurrency.md#Single%20Listener,%20Single%20Worker) must distribute three core roles: the **listener**, the **acceptor**, and the **worker**. 

Traditional models face strict bottlenecks: single-threaded event loops (like Node.js) max out on CPU computation, while multi-threaded models (like Apache) require strict locking and suffer from the Thundering Herd problem when threads compete to accept connections.

### The Goroutine-Per-Connection Model (Single Listener, Multiple Workers)

By default, Go's `net/http` package utilizes the **[Single Listener, Multiple Worker Threads](02%20Application%20Server%20Concurrency.md#Single%20Acceptor,%20Multiple%20Workers)** execution pattern. Because Go's goroutines start with a microscopic memory footprint compared to OS threads, Go can seamlessly spawn a dedicated worker goroutine for every single incoming network connection rather than relying on a limited pool of OS threads.

- **The Acceptor Loop (Single Listener):** A single main goroutine acts as the listener and acceptor in a continuous loop, calling `accept()` to turn pending network connections into dedicated file descriptors (connected sockets).
- **The Worker Handoff (Internal Load Balancing):** Once a connection is accepted, the main goroutine acts as an internal load balancer. It instantly spawns a new worker goroutine and hands the file descriptor directly to it.
- **Isolated Execution (Multiple Workers):** The worker goroutine is fully responsible for reading the incoming request, executing the business logic, and writing the response. Because the Go scheduler distributes these worker goroutines across all available logical processors (**P**), the business logic executes in parallel across multiple physical CPU cores.

### Handling I/O Blocking (The Netpoller)

Socket I/O is usually handled asynchronously with mechanisms like `epoll` or `select`. If network data is not yet available, standard socket reads would block the OS thread. Go abstracts this entirely through the internal **Netpoller**:

- Instead of blocking the OS thread (**M**), the runtime parks the worker goroutine and registers the file descriptor with the OS's `epoll` mechanism.
- The **M** is instantly freed to grab the next ready goroutine from the run queue.
- When `epoll` notifies the runtime that network data has arrived, the scheduler wakes the sleeping worker goroutine back up to resume execution.

### Scaling the Acceptor (Multiple Listeners Pattern)

A known drawback of the single listener pattern is that a central accepting process can still become a bottleneck under heavy connection loads. If a single acceptor goroutine cannot pull connections out of the OS kernel's queue fast enough, Go can shift to the **[Multiple Listeners (Same Port and Address)](02%20Application%20Server%20Concurrency.md#4.%20Multiple%20Listeners%20(Same%20Port%20and%20Address))** pattern using the `SO_REUSEPORT` socket option.

Because the OS kernel is completely blind to goroutines, you cannot simply spawn multiple goroutines to listen to one socket. You must create multiple physical file descriptors. This is implemented in two ways:

- **Multiple Processes:** You spin up multiple, completely independent instances of your Go application (e.g., 4 separate OS processes). Each process binds to the same port.
- **Multiple Sockets, One Process:** Using Go's `net.ListenConfig`, the application explicitly opens multiple separate `net.Listener` sockets on the exact same port, spawning one acceptor goroutine per socket.

**How the Kernel Handles It:**

- By using `SO_REUSEPORT`, the OS allows these multiple independent sockets to bind to the exact same port.
- The OS kernel creates separate accept queues for each file descriptor and natively load-balances incoming network connections across them.
- When a new connection arrives, the OS notifies `epoll` about a specific file descriptor. The Go runtime's Netpoller catches this and wakes up *only* the specific acceptor goroutine mapped to that socket, completely eliminating the single-acceptor bottleneck and the Thundering Herd problem.

## Channels Implementation

Under the hood, a Go channel is not a magical language construct; it is a meticulously designed C-like struct named `hchan` allocated on the [Heap](02%20The%20Anatomy%20of%20a%20Process.md#The%20Heap).

### 1. The `hchan` Struct

When you create a channel using `make(chan int, 3)`, the runtime allocates an `hchan` struct. This struct has three critical components:

- **The Ring Buffer (Data):** For buffered channels, this is a circular array that physically holds the data. It tracks its state using integer indices.
- **The Mutex (Lock):** Every channel has an internal lock. Goroutines must briefly acquire this lock to read or write, then release it.
- **The Wait Queues (Blockers):** The struct contains two linked lists: `recvq` (receivers waiting for data) and `sendq` (senders waiting for space).

### 2. Blocking Without Wasting the CPU

When a channel is full (or unbuffered) and a goroutine (**G**) tries to send data, it gets blocked. To prevent blocking the underlying OS thread, the runtime acts:

1. **Packing:** The runtime packages the blocked goroutine (**G**) and its data into a `sudog` struct.
2. **Queueing:** The `sudog` is pushed onto the channel's `sendq` linked list.
3. **Parking (`gopark`):** The channel calls `gopark`. The scheduler removes the active **G** from the logical processor (**P**) and puts it to sleep.
4. **Freeing the CPU:** The **M** (OS thread) immediately executes the next ready **G** from the local run queue.

### 3. Direct Memory Handoffs (Single-Copy Optimization)

When a goroutine arrives at a channel and finds another goroutine sleeping in a wait queue, it executes a brilliant hardware optimization to skip redundant intermediate memory copying. The active goroutine does the memory chores for the sleeping one:

- **Sleeping Sender (Full Channel):** If a receiver arrives and finds a sleeping sender, its action depends on the buffer:
    - _Unbuffered:_ The receiver reads the data **directly out of the sleeping sender's memory stack**.
    - _Buffered (FIFO Shuffling):_ The receiver reads the oldest data from the front of the ring buffer, and then copies the sleeping sender's data directly into the newly freed spot at the back of the buffer to maintain FIFO ordering.
- **Sleeping Receiver (Empty Channel):** If a sender arrives and finds a sleeping receiver, the sender completely bypasses the ring buffer. It writes its data **directly into the sleeping receiver's frozen stack**.
- In all scenarios, the active goroutine performs a single, direct memory copy from stack to stack, bypassing the heap-allocated ring buffer entirely.

### 4. Waking Up (`goready`)

Once the memory transfer is complete, the blocked goroutine can proceed. The channel calls `goready(G)`, which takes the sleeping goroutine out of the wait queue and places it back into a logical processor's (**P**) local run queue.
