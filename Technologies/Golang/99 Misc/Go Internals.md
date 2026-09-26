# Go Runtime Internals

## Scope and implementation baseline

The Go runtime is implementation-provided code and state linked into a Go executable. After the operating system loads the process and transfers control to its entry point, the runtime initializes Go-specific state and ultimately invokes `main.main`. It remains active while the program runs, supplying mechanisms required beyond the program's compiled instructions.

The runtime operates inside an operating-system process; it is neither the operating system nor an interpreter or virtual machine. Go code is compiled to native instructions, while the runtime coordinates those instructions with [operating-system threads](../../../Operating%20Systems/05%20Process%20Management.md#Processes%20vs.%20Threads), memory, timers, signals, and I/O. In particular, it schedules [goroutines](../../../Operating%20Systems/05%20Process%20Management.md#User-Space%20Threads%20%28Green%20Threads%20%26%20Coroutines%29), manages their movable stacks and heap allocation, performs garbage collection, parks and readies blocked work, and integrates pollable network I/O with scheduling. These mechanisms make lightweight concurrency and automatic memory management practical without changing Go's language-level semantics.

The implementation details below are pinned to the upstream `gc` compiler and runtime in Go 1.26.6, at commit `1ea5a71ad8ceb7b9f16b4b6f8ea4739a4327dd6e`. Internal layouts, scheduling policies, and performance heuristics are implementation details. Programs rely on the Go specification and documented APIs; language-level guarantees are identified separately where they matter.

## Compiler contracts consumed by the runtime

### SSA lowering and executable metadata

The compiler lowers typed Go through static single assignment (SSA), an intermediate representation in which each computed value is assigned once, into machine code. Alongside instructions, it emits metadata that maps program counters and stack locations to live Go pointers and identifies safe points where execution state is inspectable. The linker combines package code with the runtime and preserves the resulting function, pointer-map, stack-map, and relocation metadata. The resulting executable relies on object-file, loader, and [ABI mechanics](../../../Operating%20Systems/Compilers%2C%20Linkers%2C%20and%20Program%20Loading.md#ABI%20and%20Separate%20Compilation).

That metadata lets the runtime find pointers, copy stacks, unwind panics, construct profiles, and print stack traces without treating arbitrary machine words as pointers. The broader [language-runtime model](../../../Operating%20Systems/Compilers%2C%20Linkers%2C%20and%20Program%20Loading.md#Runtime%20Environments) separates this responsibility from the standard library and the operating system.

### Internal ABI and call metadata

An ABI specifies how separately compiled code agrees on calls, including argument and result placement. Go functions normally use the register-based `ABIInternal`; assembly and compatibility boundaries use `ABI0`, with compiler-generated wrappers bridging them. The internal ABI is deliberately unstable.

## Runtime bootstrap and execution model

### Runtime startup

Startup follows this Go-specific sequence:

1. A platform entry stub transfers control to the runtime.
2. The runtime establishes initial execution state, scheduler state, the allocator, garbage collector, signal machinery, and required bootstrap threads.
3. Package initialization runs in dependency order.
4. Control reaches `main.main`.

### Runtime execution model

The scheduler maps many goroutines onto operating-system threads through the following execution-state components.

#### G, M, and P

The components have distinct responsibilities rather than being analogues of OS process structures.

- **G — goroutine:** A goroutine's execution state: stack bounds, status, saved scheduling context such as [SP](../../../Operating%20Systems/02%20The%20Anatomy%20of%20a%20Process.md#Stack%20Pointer%20%28sp%29) and [PC](../../../Operating%20Systems/04%20Inside%20The%20CPU.md#Registers), waiting reason, and links to structures on which it waits. A `g` is not a [PCB](../../../Operating%20Systems/05%20Process%20Management.md#The%20Process%20Control%20Block%20%28PCB%29) or a complete architectural register file.
- **M — machine:** An OS thread plus runtime state. Each M has a system stack represented by `g0`; `gsignal` is a separate runtime G and stack used while that M handles a delivered signal.
- **P — logical processor:** Permission and per-processor runtime state needed to execute ordinary Go code: a run queue, allocator cache, timers, GC-worker state, and related caches. A P is neither a CPU nor permanently attached to one.

During bootstrap, the runtime creates the initial M (`m0`), its system G (`g0`), and the initial Ps before it can schedule ordinary Go code.

An M needs a P to execute ordinary Go code, and a P executes at most one G at a time. An M can exist without a P while it blocks in a syscall or performs runtime or foreign work. `GOMAXPROCS` limits the number of Ps that execute Go code concurrently, not the number of goroutines or OS threads. On Linux, Go 1.25's defaults can account for [cgroup CPU-bandwidth limits](../../../Operating%20Systems/10%20Virtualization%20and%20Containerization.md#Cgroups:%20Resource%20Governance) and update as limits change; configuration can override that default, and the policy does not create CPU affinity.

#### Goroutine creation and G reuse

A finished G enters the terminal `_Gdead` state before its record is put on a free list for reuse; it no longer represents executing work. Each P keeps a local free cache of `_Gdead` records. If that cache is empty and the shared global free cache has records, the runtime refills the local cache in a batch. If neither cache supplies a record, it allocates a new G.

A `go` statement is lowered to `newproc`, which calls the lower-level helper `newproc1`. It obtains a reusable G or allocates one, supplies a starting stack, and configures its initial execution context. When the goroutine function returns, that context continues through `goexit`, the runtime's goroutine-exit path. For an ordinary `go` statement, `newproc1` returns the configured G in the runnable state.

#### Runnable queues and work discovery

`newproc` preferentially places a new G in `runnext`, the current P's single-G priority slot. Otherwise it enters that P's regular local run queue. `wakep` may arrange for another M to execute runnable work. `runnext` reduces handoff latency; it does not promise immediate execution.

Each P has its own `runnext` slot and a local run queue whose current capacity is 256. A full local queue transfers roughly half of its work together with the new runnable G, rather than merely sending the new G to the shared global runnable queue. This amortizes synchronization and makes work available to idle Ps.

Work discovery is a repeated, conditional policy rather than a fixed sequence. `findRunnable` checks early timers and scheduler work such as tracing or GC, periodically samples the shared global runnable queue for fairness, favors immediately available local or global runnable work, polls nonblocking network events, and performs bounded stealing from other Ps. Some checks restart the search when they make work available. Victim work stealing normally transfers a batch, distinct from the roughly-half transfer used when a local queue overflows. Idle Ms may briefly spin to avoid wake-up latency, but the runtime limits spinning Ms to avoid needless CPU and OS-thread consumption.

#### Parking, readying, syscalls, and timers

Parking is the common transition for a G that cannot proceed. It records a wait state and calls `gopark`; the M switches through `g0` to the scheduler, and the P can run another G. The responsible subsystem later uses a readying path such as `goready`, which makes the G runnable. A ready G need not resume immediately, on the same M, or on the same P.

- **G-blocking operations:** A channel wait, contended mutex, or pollable socket operation parks a G while leaving the P available.
- **M-blocking operations:** Many syscalls, cgo calls, and some file operations block the M. cgo is the generated Go/C boundary, including its ABI and stack transitions. On a blocking [syscall](../../../Operating%20Systems/09%20Kernel%20and%20User%20Space.md#System%20Calls), the runtime detaches or hands off the P so another M can execute Go work; the returning M must acquire a P before returning to ordinary Go code.
- **Timers:** Per-P timer structures make work runnable at expiry. Scheduler sleep decisions and netpoll waits account for the next deadline.

#### Preemption and safe points

Safe points are places where the runtime can account for a G's state. They support fairness, stack scanning, stop-the-world coordination, stack growth, and runtime bookkeeping.

- **Blocked safe points:** A parked G no longer executes user instructions and has an inspectable state.
- **Synchronous safe points:** Compiler-generated checks, including stack-growth checks, provide places where a running G can enter runtime control.
- **Asynchronous safe points:** Platform-specific interruption can stop long-running Gs at instructions whose state can safely be recovered.

`sysmon` monitors runtime conditions and participates in requests to retake a P held by long-running execution. The current `forcePreemptNS` value is 10 ms, but it is a best-effort scheduling target, not a latency SLA. A synchronous request marks the G and makes a later stack check take the preemption path. Go 1.14 added asynchronous preemption, so a tight loop need not wait for a [function-prologue](../../../Operating%20Systems/02%20The%20Anatomy%20of%20a%20Process.md#Function%20Prologue%20and%20Epilogue) check. On Unix-like platforms this may use a delivered signal such as `SIGURG`; the exact interruption mechanism is platform-specific and not a language contract.

An asynchronous interruption succeeds only at an asynchronous safe point. The runtime preserves the interrupted context and may conservatively treat register or stack contents as possible pointers when precise compiler-map positions are unavailable. Otherwise the pending synchronous request remains effective.

## Synchronization and wait records

### Channel representation and `sudog`

The language defines [channels](../01%20Essentials/09%20Concurrency.md#Channel); the following layout is an upstream `gc` implementation detail. An `hchan` contains element type and size, ring-buffer indices, closed state, a mutex, and send and receive wait queues. Fast paths make nonblocking observations, but the locked path establishes correctness. A runtime semaphore is a runtime-managed park/wake queue and accounting protocol, not a POSIX semaphore; its state coordinates the transition between waiting and waking.

A `sudog` is a reusable wait record that represents one G's participation in a particular channel or runtime-semaphore queue; it is not the G itself. It carries the state needed to park, wake, and, where needed, adjust pointers into a copied goroutine stack.

### Unbuffered and buffered channel operations

- **Unbuffered handoff:** A sender and receiver can transfer the element directly between their locations.
- **Buffered operations:** Sends enqueue and receives dequeue ring-buffer elements. If a receiver finds a full buffer and a waiting sender, it receives the oldest buffered element and copies the waiting sender's element into the vacated slot; this can require two copies rather than one.
- **Blocking:** A nil-channel operation blocks indefinitely. A blocking operation queues a `sudog` and parks through `gopark`; its commit/unlock protocol prevents [lost wakeups](../../../Backend%20Engineering/Concurrency/01%20Concurrency%20Fundamentals.md#Condition%20Variables).

### Channel close and `select`

Closing wakes waiters: receivers eventually obtain a zero value with `ok == false`, while blocked and subsequent senders panic. For `select`, the runtime creates wait participation for multiple cases, randomizes polling to avoid deterministic bias, locks involved channels in a stable order, and removes losing records after one case wins.

### Language-level ordering guarantees

The language-level ordering does not depend on `hchan`. These are [Go memory-model](https://go.dev/ref/mem) guarantees:

- **Matching send and receive:** A send happens before completion of its matching receive.
- **Close observation:** Closing a channel happens before a receive that observes the closed state.
- **Buffered channels:** For capacity `C`, the kth receive happens before completion of the k+Cth send.
- **Unbuffered channels:** A receive happens before completion of its matching send.

### Mutex fast paths, spinning, parking, and starvation

[`sync.Mutex`](../01%20Essentials/09%20Concurrency.md#Mutex) uses an [atomic](../../../Backend%20Engineering/Concurrency/01%20Concurrency%20Fundamentals.md#Atomic%20Operations) uncontended fast path. Contention can use bounded active [spinning](../../../Backend%20Engineering/Concurrency/01%20Concurrency%20Fundamentals.md#Spinlocks) before parking through runtime semaphore machinery. A runtime semaphore provides the sleep-and-wake protocol whose commit step prevents a wakeup from being lost while a waiter parks. Normal mode favors throughput; starvation mode directly hands ownership to queued waiters to bound pathological tail latency. These policies are runtime heuristics, not API guarantees.

## Stack and control-flow machinery

### Goroutine stacks

#### Goroutine stack allocation and adaptive starting size

Goroutine stacks are contiguous and movable, unlike segmented stacks, which grow by chaining separately allocated stack segments. `stackMin` is 2 KiB, and `fixedStack` adds and rounds platform-specific overhead; it is the minimum allocation model, not a fixed initial size. With adaptive stack starts enabled, `startingStackSize` is recomputed from scanned stack use after GC and can exceed that minimum.

Stacks use dedicated allocation pools and a stack-specific path rather than ordinary `mcache.alloc` size-class spans. The per-P stack cache is nevertheless held in `mcache`, the P-local runtime cache structure that also supplies small-object allocation.

#### Stack growth, copying, pointer adjustment, and shrinking

Function prologues compare the stack pointer with a guard. Insufficient space transfers through `morestack` on the system stack; the runtime allocates a larger contiguous stack, copies live frames, adjusts pointers into the old stack, and returns the old storage to stack pools. Stacks can also shrink, commonly during GC-related stack processing.

Compiler pointer maps identify pointer-containing stack slots. `sudog` records and other runtime state containing pointers into a copied stack must be adjusted. Arbitrary concurrent access to another G's stack would break this invariant, so channel handoff and stack copying coordinate through channel locks and `sudog` metadata. `//go:nosplit` marks runtime paths that cannot safely start ordinary stack growth.

### Defer implementation

The compiler does not universally implement [`defer`](../01%20Essentials/09%20Concurrency.md#Defer) as a heap list of [closures](../01%20Essentials/08%20Functions%20Deep%20Dive.md#Closure). Eligible functions use open-coded defers represented by function-local state and metadata; other paths use stack-allocated records or heap-backed records when lifetime or control flow requires them. The compiler emits enough metadata for panic unwinding to discover open-coded defers. Deferred arguments and receivers are evaluated when the `defer` statement executes, and normal return invokes defers in reverse registration order.

### Panic unwinding and recovery

Panic handling proceeds in the current G:

1. The runtime constructs or obtains panic state and associates it with the G.
2. It walks that goroutine's frames and executes applicable deferred functions.
3. It continues unwinding unless a valid recovery succeeds.
4. An unhandled panic prints diagnostic information and terminates the process.

A [`panic`](../01%20Essentials/09%20Concurrency.md#panic) unwinds only its originating goroutine; other goroutines do not receive it, even though an unhandled panic later ends the process. `recover` is meaningful only when called by a deferred function while that goroutine unwinds the corresponding panic. Calls outside that context, including indirect calls that fail the required boundary, return `nil`. Successful recovery stops unwinding and follows the language's return semantics; it does not jump back to the panicking statement.

This differs from a runtime fatal error or `throw`, an unrecoverable process fault, and `os.Exit`, which terminates without running defers.

## Object placement and heap allocation

### Escape analysis and object placement

Escape analysis is compile-time dataflow analysis over aliases, assignments, calls, closures, [interfaces](../01%20Essentials/06%20Interfaces%20and%20Generic%20Code.md#Interface), and lifetimes. It places a value on a goroutine's movable stack only when the compiler proves that its lifetime fits there safely. Taking an address alone does not force a heap allocation; returned or stored references, captured variables, interface conversions, indirect calls, dynamically sized values, inlining, and interprocedural analysis can all affect the result. Inlining substitutes a call's body at a call site; interprocedural analysis follows facts across call boundaries.

Escape decisions are compiler- and version-dependent. `go build -gcflags=-m` reports decisions for a build, but it is a diagnostic rather than a language contract.

### Allocator vocabulary: spans, size classes, and scan classes

An arena is a runtime-managed partition of the Go heap address space. The runtime can reserve virtual address space without immediately obtaining physical backing; committed or otherwise physically backed pages are usable for allocations. Within an arena, `mheap` manages pages and spans; a span is a contiguous allocator unit that holds objects of a size class or backs a large object. A size class rounds small allocations to reusable object slots. Scan spans contain objects that must be scanned for pointers; noscan spans hold objects with no heap pointers.

### Tiny, small, and large allocation paths

The runtime separates allocation paths so common small allocations avoid shared-heap coordination.

- **Tiny objects:** Pointer-free objects below the tiny threshold can share a tiny allocation block. This path advances a bump offset within that block, reducing fragmentation and metadata overhead.
- **Small objects:** A request maps to a scan or noscan size class. A P's `mcache` uses allocation bits, an allocation cache, and a free index to consume a free slot from the current span. When that span has no free slot, the cache refills from `mcentral`, which obtains spans from `mheap`.
- **Large objects:** These bypass the normal small-object `mcache`/`mcentral` path and obtain a suitably sized span from `mheap`. `mheap` can reuse reserved and committed free heap pages, so a large allocation does not inherently issue a new OS mapping.

### `mcache`, `mcentral`, and `mheap`

`mcache` is per-P state, not per-thread or per-core state. It reduces allocator contention but cannot promise [L1/L2 residency](../../../Operating%20Systems/04%20Inside%20The%20CPU.md#The%20Cache%20Hierarchy), because Ms and Ps move across CPUs. `mcentral` coordinates spans for a size class, while `mheap` supplies and reclaims spans and tracks their allocation and mark metadata. Zeroing and pointer metadata preserve correctness. Sweeping later returns slots and spans to allocator reuse.

### Heap arenas and virtual-memory backing

`mheap` uses the runtime's platform-memory abstraction to reserve address space and obtain or release physical backing. This is distinct from the underlying [mapping and unmapping of pages](../../../Operating%20Systems/03%20Memory%20Management.md#Mapping%20and%20Unmapping%20Pages): a Go heap arena is a runtime allocator partition, not an OS virtual-memory arena.

## Garbage collection and object lifetime

### Object graph, roots, and reachability

The collector follows the object graph formed by heap pointers. Roots are pointers directly known to the runtime, including globals, goroutine stacks, and runtime data structures. An object is reachable when tracing from those roots reaches it; unreachable objects are eligible for reclamation. A mutator is application or runtime code that changes this graph while collection runs.

Reachability is not lexical scope. The compiler can treat a value as dead before its surrounding function returns once it proves no later use; references in stacks, globals, runtime structures, or finalizer state can also extend lifetime.

### Collector properties and Go 1.26 Green Tea

The `gc` runtime uses a precise, type-aware tracing collector.

- **Concurrent and parallel marking:** Background workers trace reachable objects while the program runs.
- **Non-generational collection:** The collector does not divide objects into generations.
- **Non-compacting heap objects:** The collector does not relocate heap objects to reclaim space.
- **Mark-and-sweep reclamation:** Tracing identifies unreachable objects, and sweeping makes their storage reusable.
- **Write barrier during concurrent marking:** Pointer updates preserve reachability while tracing proceeds.

> [!NOTE] Go 1.26
> Green Tea is the default garbage-collector implementation in Go 1.26. It changes marking and scanning implementation, not language reachability semantics or the broad model of a concurrent, tracing, non-generational, non-compacting collector.

### Mark cycle, safe points, and stop-the-world transitions

The GC pacer is the runtime controller that chooses cycle trigger points and balances expected background work with mutator assists. Collection can be selected by the pacer, allocation pressure, a memory limit, or explicit collection; it is neither continuous nor pause-free.

A stop-the-world (STW) transition temporarily prevents mutators from executing Go code so the runtime can establish a global collector state. A mark cycle has these stages:

1. Sweep termination performs a short STW transition into marking.
2. The runtime prepares roots and enables the write barrier.
3. Background workers trace globals, stacks, and reachable heap objects concurrently with mutators.
4. Mark termination performs another short STW transition.
5. Concurrent or lazy sweeping makes dead slots and spans reusable.

Tricolor marking is a correctness model: white objects are not yet discovered, gray objects await scanning, and black objects have been scanned. It does not require breadth-first traversal. The runtime uses distributed work structures; in Go 1.26, Green Tea changes marking and scanning to improve locality and scalability, particularly for small objects. On Intel Ice Lake and AMD Zen 4 or newer amd64 platforms, vector instructions can assist scanning.

### Write barrier and GC assists

The hybrid deletion/insertion write barrier preserves the tricolor invariant while a mutator changes pointers during tracing. It ensures that changing a pointer cannot make a reachable object invisible to the collector.

During marking, black allocation marks a newly allocated object so it does not need to be rediscovered as white. An allocation can also incur GC assist work when the mutator has incurred more allocation debt than the pacer planned. Assists let allocation pressure contribute tracing work rather than leaving all progress to background workers.

### Pacing, `GOGC`, and `GOMEMLIMIT`

Live heap is the storage found reachable at the end of marking. The pacer uses `GOGC` to control the heap-growth target relative to live heap and roots: a larger value trades memory for less frequent GC work. `GOMEMLIMIT` is a soft limit for the runtime's memory use, not a hard heap cap. An excessively restrictive limit can cause GC thrashing and high CPU use.

### Sweeping and scavenging

Sweeping makes dead object slots and spans reusable by Go's allocator. Scavenging releases the physical backing of unused heap pages to the OS. Free heap memory can therefore remain mapped and reusable without remaining resident. Heap in use is memory assigned to spans, including free slots in those spans; reserved heap is address space retained by the runtime; and process RSS is physical memory currently resident. Go has background and allocation-time scavenging paths.

### Finalizers and cleanups

A finalizer becomes eligible only after the runtime determines that its object is unreachable. It runs asynchronously in a runtime-managed goroutine, has no prompt-execution guarantee, and may never run before process termination. It can resurrect an object by making it reachable again, and cycles involving finalizers complicate reachability. Finalizers are therefore unsuitable for correctness-critical release of files, locks, transactions, or network resources.

`runtime.AddCleanup`, introduced in Go 1.24, provides a separate cleanup mechanism rather than finalizer-equivalent semantics. Cleanups run after an object becomes unreachable, can run concurrently, and have their own documented caveats and lifecycle constraints. They still do not provide prompt or guaranteed release, so explicit resource management remains necessary.

### `runtime.KeepAlive` and liveness boundaries

`unsafe.Pointer` is a pointer representation subject to Go's pointer rules; an ordinary [Go pointer](../01%20Essentials/04%20Understanding%20Pointers.md#Creating%20a%20pointer) keeps its reachable object alive. By contrast, `uintptr` is an integer and not a GC-visible reference. Converting a pointer to `uintptr`, retaining it, and later converting it back can lose liveness and violate pointer rules. Some conversions are valid only within one expression because the compiler and runtime recognize that pattern.

Pointers into goroutine stacks require additional care because stack copying changes their addresses. The current heap is non-moving, but that implementation detail does not grant unrestricted pointer use as a language guarantee. `checkptr` detects selected invalid pointer arithmetic and conversions but cannot prove arbitrary unsafe code correct.

The required liveness boundary for a foreign call is:

1. The program performs its final foreign or syscall use of an object.
2. The compiler might otherwise regard that object as dead before function return.
3. `runtime.KeepAlive(obj)` after the operation establishes the required liveness point.
4. This prevents premature cleanup or finalization; it does not synchronize ordinary shared-memory access.

These restrictions make syscall argument liveness, finalizers and cleanups, foreign-memory ownership, cgo pointer passing, and GC pointer metadata compatible with a movable-stack runtime.

## Runtime representations of Go values

Representation affects copying, aliasing, scanning, and escape decisions. It does not alter language-level behavior promised by the specification.

### Strings

A string is conceptually a descriptor containing a pointer to immutable bytes and a length. Assignment copies that descriptor, not the bytes, and slicing normally creates another descriptor into the same backing storage. A small substring can therefore retain a much larger allocation. String bytes contain no heap pointers, so their storage is noscan memory.

Converting between `string` and `[]byte` normally needs distinct immutable or mutable storage, though the compiler can eliminate copies in selected contexts. Unsynchronized concurrent assignment to or access of a string is a [data race](../../../Backend%20Engineering/Concurrency/01%20Concurrency%20Fundamentals.md#Race%20Conditions). Because the descriptor has multiple words, an ordinary concurrent assignment can also be observed inconsistently.

### Slices

A [slice](../01%20Essentials/07%20Arrays%2C%20Slices%20and%20Maps.md#Slices) descriptor has a backing-array pointer, length, and capacity. Passing it copies the descriptor rather than its elements, so two slices can alias one array. A zero-length slice can still retain a large backing array.

`append` follows this sequence:

1. If capacity remains, it extends the view and writes into the existing array.
2. Otherwise, it chooses a new capacity with an implementation growth heuristic.
3. It allocates an appropriately rounded backing array, copies the live prefix, and returns a new descriptor.

An append that reallocates breaks that particular backing-array relationship. Pointer-containing arrays require write barriers and GC scanning, while pointer-free arrays can use noscan spans. Capacity growth is not a guaranteed doubling rule.

### Interfaces, boxing, and type metadata

An empty interface records a dynamic type and data. A non-empty interface associates the dynamic type with method-dispatch metadata, commonly an `itab`. Depending on representation, an interface assignment may store a value indirectly. Boxing is the representation or allocation of a concrete value so it can be carried through an interface; converting a concrete value to an interface does not inherently require allocation because escape analysis and boxing requirements decide.

Interface equality first compares dynamic types and then uses type-specific equality; comparison panics when the dynamic value is not comparable. Compiler- and runtime-generated type metadata and caches support method dispatch and type assertions. These descriptors also connect ABI metadata, pointer maps, reflection, and dynamic dispatch.

### Reflection and runtime type metadata

The executable includes runtime type descriptors used for interface conversion and assertion, equality and hashing, GC pointer maps, reflection, map operations, allocation size and alignment, method lookup, and panic formatting. Reflection therefore exposes compiler/linker-generated metadata rather than being merely a source-level library abstraction.

Dynamic inspection and calls can inhibit compiler optimization, interface conversion can require boxing, and constructing reflected values can allocate. Some reflection operations only inspect metadata and need not allocate.

### Maps

The language-level behavior of [maps](../01%20Essentials/07%20Arrays%2C%20Slices%20and%20Maps.md#Maps) does not depend on their layout. The following Swiss-table design is an upstream `gc` Go 1.26.6 implementation detail, replacing the older bucket-and-overflow-bucket representation, and is documented by the pinned [`internal/runtime/maps/map.go`](https://github.com/golang/go/blob/go1.26.6/src/internal/runtime/maps/map.go).

#### Swiss-table groups and lookup

A group has eight key/value slots and an eight-byte control word. A hash divides into H1 and H2: H1 chooses a starting group and probe sequence, while H2 occupies control bytes that filter a group with word-level operations before full key comparison. Quadratic probing searches later groups with increasing offsets.

#### Deletion, growth, and iteration

Deleted entries can remain tombstones because turning them into empty slots could incorrectly terminate a later probe. A small map fits in one group; larger maps use multiple tables selected through a directory resembling extendible hashing, in which hash-prefix partitions index tables. Growth can replace a table or split it in two, bounding the size of an individual growth operation.

Iteration order is deliberately unspecified and randomized. Deleting an unseen entry prevents its return, a new entry may or may not be observed, and a returned modified entry exposes its latest value. During growth, the iterator avoids duplicate entries while consulting replacement tables for current values. A map and its backing storage can remain stack-resident when escape analysis proves that safe; stack copying adjusts the contained safe stack pointers. If a map may outlive a frame, escape analysis moves its storage or required referents to the heap. Unsynchronized concurrent map writes are invalid; runtime detection of some such operations is diagnostic behavior, not synchronization.

## Operating-system and foreign-code integration

### cgo, ABI transitions, and pointer passing

cgo crosses Go and platform ABIs and stacks. A blocking C call blocks an M rather than necessarily a P, and a callback from C requires the runtime to recover or establish Go execution state. [Go's pointer-passing rules](https://pkg.go.dev/cmd/cgo#hdr-Passing_pointers) constrain Go pointers and lifetime while C retains access: retention beyond a call requires appropriately pinned Go memory for the required duration, and pointer-containing Go memory has further restrictions.

### OS-thread affinity

`runtime.LockOSThread` is required when state must remain associated with an OS thread, for example for some GUI, namespace, or foreign-runtime APIs. A locked goroutine reduces scheduling flexibility and can increase OS-thread use.

### Signal handling

The kernel delivers [POSIX signals](../../../Operating%20Systems/05%20Process%20Management.md#POSIX%20Signals). The runtime owns in-process handling machinery: it installs or cooperates with handlers, classifies a delivered signal, and consumes, translates, forwards, or mediates it. It may use signals for asynchronous preemption, CPU profiling, synchronous-fault conversion, process-control behavior, diagnostics, or platform-specific coordination.

Each M has signal-related state, and `gsignal` supplies a runtime-controlled stack for signal handling. A handler must preserve interrupted register state and determine whether interruption occurred in Go, runtime, or foreign code; it cannot run arbitrary normal Go code. Synchronous faults such as invalid memory access can become Go panics when they correspond to recoverable Go behavior. Faults in runtime-critical or foreign code can instead be fatal or delegated.

`os/signal.Notify` requests mediated notification; it does not replace handlers the runtime needs, and some signals remain special, synchronous, or uncatchable. With cgo, handler installation, callbacks on foreign threads, and per-thread signal state must cooperate: the alternate signal stack is where a handler runs, and an inherited signal mask controls which signals the thread blocks.

### Network polling and I/O

#### Netpoll abstraction

Netpoll is a runtime abstraction, not a synonym for [`epoll`](../../../Operating%20Systems/07%20Socket%20Management.md#epoll%20Readiness%20Cycle) or a dedicated thread. Its implementations use OS facilities such as epoll, [kqueue](../../../Operating%20Systems/07%20Socket%20Management.md#kqueue%20Readiness%20Cycle), event ports, AIX polling, and Windows mechanisms. Scheduler paths and `sysmon` participate in polling and injecting ready work.

A `pollDesc` is runtime state associated with a pollable [file descriptor](../../../Operating%20Systems/07%20Socket%20Management.md#Sockets%20as%20Kernel%20Objects). It maintains independent read and write waiter state, plus state used to arbitrate readiness, deadlines, and closure; it is not the kernel descriptor itself.

#### Unix readiness-based read path

On Unix readiness-based ports, a pollable `net.Conn.Read` follows this path:

1. `net.Conn.Read` reaches `internal/poll`; the runtime prepares the read waiter state and attempts a nonblocking read syscall.
2. A successful read returns directly. `EAGAIN` means that this Unix read would block; it is not a cross-platform completion result.
3. On Linux, epoll interest is registered when the descriptor is opened. After `EAGAIN`, `pollDesc` installs and commits the read waiter unless readiness, timeout, or close has already won the race.
4. The OS poller reports readiness, and the runtime transitions the read-waiter state and readies the G.
5. The G retries the syscall because readiness is neither completion nor a durable promise that data remains available.

Linux currently uses edge-triggered epoll and an internal wake-up descriptor, but those are platform-specific implementation details.

#### Windows completion-based boundary

Windows networking uses overlapped I/O and completion machinery rather than the Unix `EAGAIN` readiness loop. The scheduler-level consequence remains the same: a G can park while its P executes other Go work and become runnable when the I/O operation's completion machinery resolves it.

#### Deadlines, closure, and waiter races

Read and write waiter states are separate. Descriptor closure, deadlines, timeout timers, and readiness race to resolve the corresponding `pollDesc` waiter state.

#### Regular files, DNS, and TLS boundaries

A readiness facility does not make regular-file I/O asynchronously complete, so blocking filesystem operations can block an M. DNS can use pure-Go or cgo/system-resolver paths with different blocking behavior. TLS is primarily userspace computation over pollable network I/O.

#### `net/http` connection handling

When a [`net/http`](../02%20Built-in%20libraries/HTTP%20Server.md) connection goroutine waits on pollable I/O, netpoll parks it and later makes it runnable for the scheduler. Its [shared listening socket topology](../../../Backend%20Engineering/Concurrency/02%20Application%20Server%20Concurrency.md#Multiple%20Workers%2C%20Single%20Shared%20Listening%20Socket) and HTTP-specific connection and request handling are application and protocol concerns.

Multiple goroutines may call `Accept` on one `net.Listener`. `SO_REUSEPORT` instead distributes incoming connections among separately bound sockets.

## Diagnostics and failure detection

### Runtime traces, metrics, profiles, and compiler evidence

Runtime tools expose evidence about mechanisms, but each measures a particular signal rather than proving a causal explanation by itself.

- **Scheduler traces:** `GODEBUG=schedtrace` reports scheduler state snapshots, not end-to-end request latency.
- **GC and scavenger traces:** Runtime debug traces show cycle and scavenging activity, not an application's complete memory ownership graph.
- **`runtime/metrics`:** Supplies runtime-defined measurements whose units and meanings must be read with the selected Go version.
- **Profiles:** CPU, heap, goroutine, block, and mutex profiles sample or record different costs; none alone proves a root cause.
- **Execution tracing:** Trace and scheduler-latency views reveal runtime events and ordering. Go 1.25's `runtime/trace.FlightRecorder` maintains an in-memory window of recent trace events.
- **Compiler evidence:** Escape output, disassembly, and SSA diagnostics show build-specific compiler decisions.
- **Race detection:** `-race` instruments code and uses runtime support.

Interpreting [runtime evidence](../../../Backend%20Engineering/05%20Observability.md#Symptoms%20vs%20causes) requires telemetry design beyond these runtime-specific signals.

### Global deadlock detection and goroutine leaks

The runtime can identify a restricted global deadlock condition: no runnable goroutines, no executing Go work capable of progress, and no relevant timers, network events, or runtime work expected to make a G runnable. It can then report that all goroutines are asleep.

- A spinning or continuously runnable G can conceal a logical deadlock.
- The runtime cannot generally know whether an external system will respond.
- A G blocked forever while unrelated Gs continue is a leak, not a global deadlock.
- Cyclic application dependencies can remain invisible when foreign calls or external events participate.

Go 1.26 has an experimental goroutine-leak profile, enabled with `GOEXPERIMENT=goroutineleakprofile` and exposed through a `pprof` endpoint. It uses reachability relationships between blocked Gs and synchronization objects to identify some Gs that cannot be awakened; it cannot detect every leak, including cases where a synchronization object remains reachable through globals or runnable G state. As of Go 1.26, the Go team aims to enable the feature by default in Go 1.27; this is not a compatibility promise.

### Race detector internals

Building with `-race` causes compiler instrumentation around memory accesses and synchronization. The linked runtime uses ThreadSanitizer-derived machinery to record access histories and happens-before edges, and standard synchronization operations include hooks it understands. Reports identify conflicting accesses and relevant goroutine-creation stacks.

Data-race-free sequential consistency (DRF-SC) means that a program without data races behaves as though its synchronization-consistent executions are sequentially consistent; the definition belongs to the [Go memory model](https://go.dev/ref/mem). Instrumentation changes timing, memory use, binary size, and scheduler behavior. The absence of a report establishes only that no detectable race occurred in the executions tested. Unsafe code, assembly, cgo, and unsupported platforms can reduce coverage. Race consequences follow from unsynchronized conflicting access.

## Scheduler, GC, and netpoll in one trace

The runtime's subsystems meet in a handler that reads from a network connection on a Unix readiness-based port:

1. The handler G runs on M1 with P0 and allocates through P0's `mcache`.
2. Allocation debt can make that G perform GC assist work.
3. A nonblocking socket read returns `EAGAIN`, so `pollDesc` installs and commits the read waiter before parking the G unless another event resolves the race.
4. M1 returns through `g0` to the scheduler, which selects another runnable G for P0.
5. The OS poller reports the descriptor ready and netpoll changes the waiter state, injecting the G into runnable work.
6. Another M/P can execute the G; resumption has no M or CPU affinity.
7. A deadline timer can race with readiness to produce a timeout, while a concurrent GC can scan the safely parked G.
8. On resumption, the G retries the read because readiness did not guarantee successful consumption.
