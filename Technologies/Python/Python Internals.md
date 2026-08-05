# Python Internals and System Architecture

## The Execution Model: Interpreted at Runtime

Unlike languages like Go or C that compile directly into a static executable bound to a specific CPU architecture, Python operates dynamically.

- **The Runtime Engine:** Python relies on a [runtime engine](../../Operating%20Systems/02%20The%20Anatomy%20of%20a%20Process.md#Assembling%20into%20Machine%20Code) to interpret code or compile it just-in-time (JIT).
- **Memory Permissions:** Because the runtime generates raw machine instructions on the fly, it must constantly juggle memory permissions—requesting writable memory from the OS to generate code, then switching it to read-only/executable (W^X) before the CPU can safely run it.

## Memory Layout and The OOP Penalty

Python heavily enforces an [object-oriented paradigm](../../Operating%20Systems/02%20The%20Anatomy%20of%20a%20Process.md#The%20OOP%20Penalty), meaning almost every entity (even simple integers) is a Class instance. This creates severe performance implications at the hardware level.

### Heap Fragmentation and Metadata Bloat

- **Massive Heap Allocation:** Instantiating a class triggers a small, individual allocation on the Heap.
- **Metadata Bloat:** Every tiny object requires its own hidden metadata header. For example, wrapping a simple 4-byte primitive integer into a Python object adds massive overhead, consuming unnecessary physical RAM just to store a single number.

### Pointer Chasing vs. Hardware Caching

- **The Object Graph:** Python objects frequently contain other objects (composition). However, the parent object does not physically hold the child data; it holds pointers to random, scattered locations across the Heap.
- **L1 Cache Misses:** Because these objects are randomly scattered, reading them destroys the CPU's [spatial locality](../../Operating%20Systems/03%20Memory%20Management.md#Spatial%20Locality). When the CPU reads a pointer and jumps to a new memory address, it causes an immediate L1 Cache Miss, forcing the processor to stall and wait for system RAM (a phenomenon known as Pointer Chasing).

## Garbage Collection

To clean up this massive web of heap allocations, Python relies primarily on Automated Memory Management.

### Reference Counting

- Python utilizes [reference counting](../../Operating%20Systems/02%20The%20Anatomy%20of%20a%20Process.md#Memory%20Leaks%20&%20Garbage%20Collection) as its primary garbage collection mechanism.
- Every object's hidden metadata header includes an internal integer counter (`ob_refcnt`).
- Every time a variable points to the object, the CPU increments this counter; when a variable is destroyed, the CPU decrements it.
- If the counter hits `0`, the system automatically calls `free()` to reclaim the memory.
- **The Compute Cost:** Constantly updating this counter in memory for every single object interaction is computationally expensive.

## Concurrency and Hardware Collisions

Python uses Singletons for its most common values: `None`, `True`, and `False`. This means there is only one physical instance of `None` in the entire Python process memory space. Historically, combining this Singleton pattern with Reference Counting created a massive hardware bottleneck in multithreaded applications.

### The Cache Invalidation Storm

- Because `None` is used constantly across all threads, multiple CPU cores would frequently increment and decrement its shared reference counter.
- Due to the [MESI cache coherency protocol](../../Operating%20Systems/04%20Inside%20The%20CPU.md#The%20MESI%20Protocol), when Core 1 modified the reference count for `None`, the hardware marked Core 1's cache line as **Modified (M)**.
- This instantly broadcasted an invalidation signal across the CPU bus, marking Core 2's cached copy of `None` as **Invalid (I)**.
- **Cache Thrashing:** Even if threads were performing entirely separate tasks, simply referencing `None` forced the CPU cores to violently fight over the exact same 64-byte Cache Line. This [cache invalidation storm](../../Operating%20Systems/04%20Inside%20The%20CPU.md#Case%20Study:%20Python%E2%80%99s%20%60None%60%20and%20the%20Cache%20Invalidation%20Storm) effectively disabled the L1 cache for Python's most heavily used object, crippling performance by forcing cores to fetch the data from the slow L3 cache.

### The Fix: Immortal Objects (PEP 683)

- In Python 3.12, engineers introduced **Immortal Objects** to solve this hardware collision.
- They hardcoded the reference count for `None`, `True`, and `False` to a massive, special value that the interpreter knows never to change.
- Because the reference count is no longer modified, the CPU cores can pull the cache line into their L1 caches and leave it permanently in the **Shared (S)** state.
- Cores can now read `None` simultaneously in 1 nanosecond with zero cross-talk or bus contention.
