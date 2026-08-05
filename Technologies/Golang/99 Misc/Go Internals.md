# Go Internals and System Architecture

## Execution Hierarchy and the Go Scheduler

To understand why Go's concurrency is highly efficient, you must look at [[02 The Anatomy of a Process#Processes vs. Threads|how the operating system handles execution boundaries]], and how the Go runtime works to bypass those heavy hardware limitations.

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

## Advanced Scheduling Mechanisms

### Work Stealing

Because CPU cycles are a scarce hardware resource, the Go runtime aggressively balances the workload to keep physical cores fed:

- Every **P** maintains a local queue of active goroutines.
- When a thread (**M**) empties its local queue, it actively "steals" pending goroutines from the run queue of another **P**.

### Spinning Threads (Busy Waiting)

- A spinning thread actively loops and checks for new work instead of immediately going to sleep.
- The OS penalty for waking a sleeping thread (transitioning from Kernel Space back to User Space) is computationally expensive.
- Go intentionally utilizes spinning threads as a hardware optimization to instantly capture new goroutines, prioritizing sub-millisecond execution over strict power efficiency.

## Memory Management

Go applications rely on the [classic virtual memory layout established by the operating system](../../../Operating%20Systems/02%20The%20Anatomy%20of%20a%20Process.md#Process%20Execution%20and%20State).

### Stack vs. Heap Allocation

- **The Stack:** Operates strictly as a contiguous, Last-In, First-Out (LIFO) structure. Because it benefits from excellent spatial locality, the CPU can cache it highly efficiently. Goroutine local variables are automatically freed when the function frame collapses.
- **The Heap:** A massive, upward-growing virtual memory region used for dynamic allocations. Memory placed here is globally accessible but takes longer to access due to pointer chasing and potential L1 cache misses.

### Escape Analysis

- The Go compiler [mathematically analyzes variable lifespans at compile time](../../../Operating%20Systems/02%20The%20Anatomy%20of%20a%20Process.md#The%20Heap).
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

If thousands of goroutines attempted to allocate heap memory simultaneously, it would trigger a massive hardware bottleneck. Constant atomic locking on a global heap would force CPU cores to [invalidate each other's L1 caches via the MESI protocol (False Sharing)](../../../Operating%20Systems/04%20Inside%20The%20CPU.md#The%20Developer%20Trap:%20False%20Sharing).

Go prevents this hardware collision using highly localized allocation:

### Local Memory Caches (`mcache`)

- Each logical processor (**P**) is assigned its own private memory cache called an `mcache`.
- When a goroutine needs heap memory, it requests it directly from its local `mcache`, bypassing global locks and ensuring the data remains safely within the physical CPU core's private L1/L2 cache.

### Size Classes (Slabs)

- To prevent the OS-level [external fragmentation that plagues raw physical memory](../../../Operating%20Systems/03%20Memory%20Management.md#Limitations%20of%20physical%20memory), Go categorizes small objects (≤ 32 KB) into strict size classes (e.g., 8 bytes, 16 bytes).
- If you allocate a 20-byte struct, Go immediately assigns it an optimized 32-byte memory block from the correct bucket.

### The Full Allocation Path (e.g., `new(MyStruct)`)

When your code requests new heap memory, the Go runtime executes a strict sequence to minimize performance bottlenecks:

1. **Size Classification:** The compiler calculates the exact byte size of `MyStruct` and assigns it to a standardized Size Class bucket (e.g., 16 bytes, 32 bytes).
2. **The Fast Path (Local `mcache`):** The active logical processor (**P**) first checks its private `mcache` for an empty block in that exact Size Class. If a block is available, the memory is handed over immediately. Because this is isolated to the specific **P**, the allocation requires absolutely zero locking and executes in constant $O(1)$ time.
3. **The Refill Path (Central Heap):** If the local `mcache` is empty for that specific Size Class, the **P** reaches out to the central, globally shared Go heap. It locks the global heap just long enough to grab a new bulk "span" of memory, refilling its local cache so future allocations can go back to the Fast Path.
4. **The OS Fallback (System Calls):** If the global Go heap itself runs out of available space, or if the requested object is massive (typically > 32 KB), the Go runtime cannot handle it internally. It must transition to Kernel Mode and ask the underlying operating system for more memory. It does this by executing system calls like `brk` (pushing the [[02 The Anatomy of a Process#The Heap|Program Break]] upward) or `mmap` to parachute in pure, [[03 Memory Management#Anonymous Mapping (MAP_ANONYMOUS)|zero-filled physical RAM via Anonymous Mapping]].

## Channels Implementation

Under the hood, a Go channel is not a magical language construct; it is a meticulously designed C-like struct named `hchan` allocated on the [[02 The Anatomy of a Process#The Heap|Heap]].

### 1. The `hchan` Struct

When you create a channel using `make(chan int, 3)`, the Go runtime allocates an `hchan` struct. This struct has three critical components:

- **The Ring Buffer (Data):** For buffered channels, this is a circular array that physically holds the data. It tracks its state using two integer indices: `sendx` (where to put the next item) and `recvx` (where to pull the next item from).
- **The Mutex (Lock):** Because multiple goroutines will try to access the channel simultaneously, every channel has an internal lock. Any time a goroutine wants to read or write to the channel, it must briefly acquire this lock, perform the action, and release it.
- **The Wait Queues (Blockers):** This is the true magic of channels. The struct contains two linked lists: `recvq` (receivers waiting for data) and `sendq` (senders waiting for space).

### 2. Blocking Without Wasting the CPU

When a channel is full (or unbuffered) and a goroutine (**G**) tries to send data, it gets blocked. However, it is crucial that the underlying OS thread (**M**) does not get blocked, as [[02 The Anatomy of a Process#Processes vs. Threads|OS-level context switching is highly expensive]].

Here is how the channel utilizes the [[#Execution Hierarchy and the Go Scheduler|Go Scheduler]] to bypass OS limitations:

1. **Packing the Goroutine:** The runtime packages the blocked goroutine (**G**) along with the data it wants to send into a special struct called a `sudog`.
2. **Joining the Queue:** This `sudog` is pushed onto the channel's `sendq` linked list.
3. **Parking (`gopark`):** The channel calls a runtime function called `gopark`. This tells the scheduler to take the active **G** off the logical processor (**P**) and put it to sleep.
4. **Keep the CPU Busy:** The **M** (OS thread) is now free. The scheduler instantly grabs the next ready **G** from the **P**'s local run queue and starts executing it. The physical CPU never stops working.

### 3. The Direct Handoff (Zero-Copy Optimization)

When a receiver finally comes along to pull data from that full channel, Go executes a brilliant hardware optimization to skip memory overhead:

- The receiver locks the channel and sees the sleeping sender waiting in the `sendq`.
- Instead of having the sender copy its data into the ring buffer, and then having the receiver copy that data out of the ring buffer, the receiver **reads the data directly out of the sleeping sender's memory stack**.
- This direct memory handoff saves CPU cycles and entirely bypasses the channel's internal buffer.

### 4. Waking Up (`goready`)

Once the receiver pulls the data, the blocked sender can finally proceed. The channel calls `goready(G)`, which takes the sleeping sender goroutine out of the wait queue and places it back into a logical processor's (**P**) local run queue so it can be scheduled for execution again.
