# Go Runtime Internals

The Go runtime is implementation-provided code and state linked into a Go executable. After the operating system loads the process and transfers control to its entry point, the runtime initializes Go-specific state and ultimately invokes `main.main`. It remains active while the program runs, supplying the mechanisms required to execute Go programs beyond their compiled instructions.

The runtime operates inside an operating-system process; it is neither the operating system nor an interpreter or virtual machine. Go code is compiled to native instructions, while the runtime coordinates those instructions with [operating-system threads](../../../Operating%20Systems/05%20Process%20Management.md#Processes%20vs.%20Threads), memory, timers, signals, and I/O. In particular, it schedules [goroutines](../../../Operating%20Systems/05%20Process%20Management.md#User-Space%20Threads%20%28Green%20Threads%20%26%20Coroutines%29), manages their movable stacks and heap allocation, performs garbage collection, parks and readies blocked work, and integrates pollable network I/O with scheduling. These mechanisms make lightweight concurrency and automatic memory management practical without changing the language-level semantics of Go programs.

The [language-runtime model](../../../Operating%20Systems/Compilers%2C%20Linkers%2C%20and%20Program%20Loading.md#Runtime%20Environments) separates this responsibility from the standard library and from the operating system. The runtime's internal structures, scheduling choices, and many performance policies are implementation details; programs should rely on the Go specification and documented APIs rather than on a particular runtime layout or scheduling outcome.

## Compiler and linker metadata

The compiler lowers typed Go through SSA into machine code. Alongside instructions, it emits stack and pointer maps, safe-point data, function metadata, and relocation information. The linker combines package code with the runtime, preserving metadata that the executable needs after compilation. The resulting executable relies on [object-file, loader, and ABI mechanics](../../../Operating%20Systems/Compilers%2C%20Linkers%2C%20and%20Program%20Loading.md).

Go functions normally use the register-based internal calling convention, `ABIInternal`. Assembly and compatibility boundaries use `ABI0`; compiler-generated wrappers bridge the two. The internal ABI is deliberately unstable. PC and stack metadata let the runtime find pointers, copy stacks, unwind panics, construct profiles, and print stack traces without treating arbitrary words as pointers.

## Runtime Execution Model

The scheduler maps many goroutines onto operating-system threads, but its components have distinct responsibilities rather than being analogues of OS process structures.

- **G — goroutine:** A goroutine's execution state: its stack bounds, status, saved scheduling context such as [SP](../../../Operating%20Systems/02%20The%20Anatomy%20of%20a%20Process.md#Stack%20Pointer%20%28sp%29) and [PC](../../../Operating%20Systems/04%20Inside%20The%20CPU.md#Registers), waiting reason, and links to structures on which it waits. A `g` is not a [PCB](../../../Operating%20Systems/05%20Process%20Management.md#The%20Process%20Control%20Block%20%28PCB%29) or a complete architectural register file.
- **M — machine:** An OS thread plus runtime state. Each M has a system stack represented by `g0`; signal handling may use `gsignal`.
- **P — logical processor:** The permission and per-processor runtime state needed to execute ordinary Go code: a run queue, allocator cache, timers, GC-worker state, and related caches. A P is neither a CPU nor permanently attached to one.

An M needs a P to execute ordinary Go code, and a P executes at most one G at a time. An M can exist without a P while it blocks in a syscall or performs runtime or foreign work. `GOMAXPROCS` limits the number of Ps that execute Go code concurrently, not the number of goroutines or OS threads. On Linux, Go 1.25's defaults can account for cgroup CPU-bandwidth limits and update as limits change; configuration can override that default, and the policy still does not create CPU affinity.

### Runtime startup

Startup follows this Go-specific sequence:

1. A platform entry stub transfers control to the runtime.
2. The runtime establishes the initial M (`m0`), its system goroutine (`g0`), scheduler state, Ps, allocator, GC, signal machinery, and required bootstrap threads.
3. Package initialization runs in dependency order.
4. Control reaches `main.main`.

### Creation, queues, and work selection

After a goroutine finishes, its `G` record enters a  state and becomes eligible for reuse; it no longer represents executing work. Each P keeps a local free cache of dead `G` records. If that cache is empty and the shared global free cache has records, the runtime refills the local cache in a batch. If neither cache supplies a record, it allocates a new `G`.

A `go` statement is lowered to `newproc`, an internal runtime function. `newproc` calls `newproc1`, its lower-level helper, which obtains a reusable G through that cache hierarchy or allocates one, provides a starting stack, and configures the G's initial execution context. When the goroutine function returns, that context continues through `goexit`, the runtime's goroutine-exit path. For an ordinary `go` statement, `newproc1` returns the configured G in the runnable state.

`newproc` then asks the scheduler to place the G preferentially in `runnext`, the current P's single-goroutine priority slot. If that preference is not used, the G enters the P's regular local run queue. `wakep` may arrange for another M to execute runnable work. `runnext` reduces handoff latency; it does not promise immediate execution.

Each P has its own `runnext` slot and a local run queue whose current capacity is 256. A full local queue does not simply send the new G to the global queue: the slow path transfers roughly half of the local work together with the new runnable G. This amortizes synchronization and makes work available to idle Ps.

When a P needs work, it considers these sources in an order shaped by locality and fairness:

1. `runnext` and the local queue.
2. Periodic global-queue fairness work and then the global queue.
3. Ready network events and expired timers.
4. Batches stolen from another P.
5. GC work.

Work stealing normally transfers a batch rather than one G. Scheduler spinning is also bounded: an idle M may briefly search for work to avoid wake-up latency, but the runtime limits spinning Ms to avoid needless CPU and OS-thread consumption.

### Parking, waking, syscalls, and timers

Parking is the common transition for a goroutine that cannot proceed. It records its wait state and calls `gopark`; the M switches through `g0` to the scheduler, and the P can run another G. The responsible subsystem later uses a readying path such as `goready`, which makes the G runnable. A ready G need not resume immediately, on the same M, or on the same P.

- **G-blocking operations:** A channel wait, contended mutex, or pollable socket operation parks a G while leaving the P available.
- **M-blocking operations:** Many syscalls, cgo calls, and some file operations block the M. On a blocking [syscall](../../../Operating%20Systems/09%20Kernel%20and%20User%20Space.md#System%20Calls), the runtime detaches or hands off the P so another M can execute Go work; the returning M must acquire a P before returning to ordinary Go code.
- **Timers:** Per-P timer structures make work runnable at expiry. Scheduler sleep decisions and netpoll waits account for the next deadline, while network deadlines connect a timer to a descriptor's `pollDesc` state.

### Preemption and safe points

Safe points are places where the runtime can account for a goroutine's state. They support fairness, stack scanning, stop-the-world coordination, stack growth, and runtime bookkeeping.

- **Blocked safe points:** A parked G no longer executes user instructions and has an inspectable state.
- **Synchronous safe points:** Compiler-generated checks, including stack-growth checks, provide places where a running G can enter runtime control.
- **Asynchronous safe points:** Platform-specific interruption can stop many long-running Gs at instructions whose state can safely be recovered.

`sysmon` monitors runtime conditions and participates in requests to retake a P held by long-running execution. The current `forcePreemptNS` value is 10 ms, but it is a best-effort scheduling target, not a latency SLA. A synchronous request marks the G and makes a later stack check take the preemption path. Go 1.14 added asynchronous preemption, so a tight loop need not wait for a function-prologue check. On Unix-like platforms this may use a signal such as `SIGURG`; the exact interruption mechanism is platform-specific and is not a language contract.

An asynchronous interruption succeeds only at an asynchronous safe point. The runtime preserves the interrupted context, and may conservatively treat register or stack contents as possible pointers when precise compiler-map positions are unavailable. Otherwise the pending synchronous request remains effective.

## Goroutine Stacks

Goroutine stacks are contiguous and movable, not segmented.

- **Stack allocation:** Initial stacks are small—currently based on a 2 KiB minimum with platform adjustments. Dedicated stack pools and per-P stack caches supply this storage, separately from ordinary object allocation through `mcache`.
- **Growth and shrinking:** Function prologues compare the [stack pointer](../../../Operating%20Systems/02%20The%20Anatomy%20of%20a%20Process.md#Stack%20Pointer%20%28sp%29) with a guard. Insufficient space transfers through `morestack` on the system stack; the runtime allocates a larger contiguous stack, copies live frames, adjusts pointers into the old stack, and returns the old storage to stack pools. Stacks can also shrink, commonly during GC-related stack processing.
- **Copied-stack integrity:** Compiler pointer maps identify pointer-containing stack slots. Runtime wait records, including `sudog` records used by channels, must be adjusted when they contain pointers into a copied stack. Arbitrary concurrent access to another G's stack would break this invariant, so channel handoff and stack copying coordinate through channel locks and `sudog` metadata. `//go:nosplit` marks runtime paths that cannot safely start ordinary stack growth.

## Escape Analysis and Object Placement

Escape analysis is compile-time dataflow analysis over aliases, assignments, calls, closures, interfaces, and lifetimes. It places a value on a goroutine's movable stack only when the compiler proves that its lifetime fits there safely. Taking an address alone does not force a heap allocation; returned or stored references, captured variables, interface conversions, indirect calls, dynamically sized values, inlining, and interprocedural analysis can all affect the result.

Escape decisions are compiler- and version-dependent. `go build -gcflags=-m` reports decisions for a build, but it is a diagnostic rather than a language contract.

## Heap allocation

The runtime separates allocation paths so common small allocations avoid shared-heap coordination. `mcache` is per-P state, not per-thread or per-core state: it reduces allocator contention, but cannot promise [L1/L2 residency](../../../Operating%20Systems/04%20Inside%20The%20CPU.md#The%20Cache%20Hierarchy) because Ms and Ps move across CPUs.

- **Tiny objects:** Pointer-free objects below the tiny threshold can share tiny allocation blocks, reducing fragmentation and metadata overhead.
- **Small objects:** A requested size maps to a scan or noscan size class. A P's `mcache` supplies a current span for that class, usually through a bump or free-slot operation. Exhaustion obtains a span from `mcentral`, which obtains spans from `mheap`.
- **Large objects:** These bypass the normal small-object `mcache`/`mcentral` path and obtain a suitably sized span from `mheap`. `mheap` may reuse reserved and committed free heap pages; a large allocation does not inherently issue a new OS mapping.

`mheap` manages pages and arenas through the runtime's platform memory abstraction. Spans carry allocation and mark metadata. Scan/noscan classification reduces GC work; zeroing and pointer metadata preserve correctness. During marking, allocation participates in black allocation and may incur GC assist work. Sweeping later returns slots and spans to allocator reuse. This is distinct from [virtual-memory mechanisms](../../../Operating%20Systems/03%20Memory%20Management.md).

## Garbage collection

The `gc` runtime uses a precise, type-aware tracing collector. Its stable conceptual properties are:

- **Concurrent and parallel marking:** Background workers trace reachable objects while the program runs.
- **Non-generational collection:** The collector does not divide objects into generations.
- **Non-compacting heap objects:** The collector does not relocate heap objects to reclaim space.
- **Mark-and-sweep reclamation:** Tracing identifies unreachable objects, and sweeping makes their storage reusable.
- **Write barrier during concurrent marking:** Pointer updates preserve reachability while tracing proceeds.

> [!NOTE] Go 1.26
> Green Tea is the default garbage-collector implementation in Go 1.26. It changes the implementation of marking and scanning, not the language's reachability semantics or the broad model of a concurrent, tracing, non-generational, non-compacting collector.

Collection occurs in cycles selected by the pacer, allocation pressure, memory limits, or explicit collection; it does not run continuously and it is not pause-free.

### Cycle, barrier, and pacing

A cycle has the following causal stages:

1. Sweep termination performs a short stop-the-world transition into marking.
2. The runtime prepares roots and enables the write barrier.
3. Background workers trace globals, stacks, and reachable heap objects concurrently with the program.
4. Mutators assist when allocation outpaces planned GC progress.
5. Mark termination performs another short stop-the-world transition.
6. Concurrent or lazy sweeping makes dead slots and spans reusable.

Tricolor marking is a correctness abstraction, not a required breadth-first traversal. The runtime uses distributed work structures; in Go 1.26, Green Tea changes the marking/scanning implementation to improve locality and scalability, particularly for small objects. On Intel Ice Lake and AMD Zen 4 or newer amd64 platforms, vector instructions can assist scanning.

The hybrid deletion/insertion write barrier preserves reachability while a mutator changes the object graph concurrently with tracing. It combines techniques derived from Yuasa and Dijkstra barriers so that changing a pointer cannot make a reachable object invisible to the collector.

`GOGC` controls the heap-growth target relative to live heap and roots: a larger value trades memory for less frequent GC work. `GOMEMLIMIT` is a soft limit for the runtime's memory use, not a hard heap cap. The pacer chooses trigger points and balances expected background work with mutator assists. An excessively restrictive limit can cause GC thrashing and high CPU use.

### Sweeping and scavenging

Sweeping makes dead object slots and spans reusable by Go's allocator. Scavenging releases the physical backing of unused heap pages to the OS. Free heap memory can therefore remain mapped and reusable without remaining resident: reserved heap, heap in use, live heap, and process RSS are different measurements. Go has background and allocation-time scavenging paths.

## Channels and mutexes

A channel is represented by an `hchan` containing element type and size, ring-buffer indices, closed state, a mutex, and send and receive wait queues. Fast paths make nonblocking observations, but the locked path establishes correctness. A `sudog` records one G's participation in a particular wait queue; it is not the G itself.

- **Unbuffered handoff:** A sender and receiver can transfer the element directly between their locations.
- **Buffered operations:** Sends enqueue and receives dequeue ring-buffer elements. If a receiver finds a full buffer and a waiting sender, it receives the oldest buffered element and copies the waiting sender's element into the vacated slot; this can require two copies rather than one.
- **Blocking and close:** A nil-channel operation blocks indefinitely. A blocking operation queues a `sudog` and parks through `gopark`; its commit/unlock protocol prevents lost wakeups. Closing wakes waiters: receivers eventually obtain a zero value with `ok == false`, while blocked and subsequent senders panic.
- **`select`:** The runtime creates wait participation for multiple cases, randomizes polling to avoid deterministic bias, locks involved channels in a stable order, and removes losing records after one case wins.

The language-level ordering does not depend on the `hchan` layout. These are [Go memory-model](https://go.dev/ref/mem) guarantees:

- **Matching send and receive:** A send happens before completion of its matching receive.
- **Close observation:** Closing a channel happens before a receive that observes the closed state.
- **Buffered channels:** For capacity `C`, the kth receive happens before completion of the k+Cth send.
- **Unbuffered channels:** A receive happens before completion of its matching send.

`sync.Mutex` uses an [atomic uncontended fast path](../../../Backend%20Engineering/Concurrency/01%20Concurrency%20Fundamentals.md). Contention can use bounded active spinning before parking through runtime semaphore machinery, whose purpose is to avoid losing a wakeup that races with sleep. Normal mode favors throughput; starvation mode directly hands ownership to queued waiters to bound pathological tail latency. Those policies are runtime heuristics, not API guarantees.

## Network Polling and I/O

Netpoll is a runtime abstraction, not a synonym for `epoll` and not necessarily a dedicated thread. Its implementations use OS facilities such as epoll, kqueue, event ports, AIX polling, and Windows mechanisms. Scheduler paths and `sysmon` participate in polling and injecting ready work.

For a pollable `net.Conn.Read`, the path is:

1. `net.Conn.Read` reaches `internal/poll`, and the runtime attempts the nonblocking read syscall.
2. A successful read returns directly. On `EAGAIN`, the descriptor's `pollDesc` records or confirms read interest and parks the G.
3. The OS-specific poller reports readiness; the runtime transitions the descriptor's read-waiter state and readies the G.
4. The G retries the syscall because readiness is neither completion nor a durable promise that data remains available.

Several I/O boundaries constrain how the runtime applies readiness:

- **Read and write waiters:** Their state is separate. Descriptor closure, deadlines, and timeout timers race with readiness and must resolve the same waiter state.
- **Regular files:** A [readiness](../../../Operating%20Systems/07%20Socket%20Management.md#Readiness%20and%20Completion%20Compared) facility does not make regular-file I/O asynchronously complete, so blocking filesystem operations can block an M.
- **DNS, TLS, and cgo:** DNS can use pure-Go or cgo/system resolver paths with different blocking behavior. TLS is primarily userspace computation over pollable network I/O. A cgo call can block its M while the scheduler keeps the P useful elsewhere.
- **Linux implementation:** Linux currently uses edge-triggered epoll and an internal wake-up descriptor, but that is a platform-specific implementation detail.

### net/http Connection Handling

When a [`net/http`](../02%20Built-in%20libraries/HTTP%20Server.md) connection goroutine waits on pollable I/O, netpoll parks it and later makes it runnable for the scheduler. Its [acceptor and worker topology](../../../Backend%20Engineering/Concurrency/02%20Application%20Server%20Concurrency.md#Single%20Acceptor%2C%20Multiple%20Workers) and HTTP-specific connection and request handling are application and protocol concerns.

Multiple goroutines may call `Accept` on one `net.Listener`. [`SO_REUSEPORT`](../../../Operating%20Systems/07%20Socket%20Management.md#Multiple%20Listeners%20with%20%60SO_REUSEPORT%60) instead distributes incoming connections among separately bound sockets.

## cgo and thread affinity

cgo crosses Go and platform ABIs and stacks. A blocking C call blocks an M rather than necessarily a P, and a callback from C requires the runtime to recover or establish Go execution state. Go's pointer-passing rules keep object visibility and lifetime sound across that boundary.

`runtime.LockOSThread` is required when state must remain associated with an OS thread, for example for some GUI, namespace, or foreign-runtime APIs. A locked goroutine reduces scheduling flexibility and can increase OS-thread use.

## Signals

The runtime owns machinery for [POSIX signal](../../../Operating%20Systems/05%20Process%20Management.md#POSIX%20Signals) delivery. It may use signals for asynchronous preemption, CPU profiling, synchronous-fault conversion, process-control behavior, diagnostics, or platform-specific coordination. Each M has signal-related state, and `gsignal` supplies a runtime-controlled stack for signal handling. A handler must preserve interrupted register state and determine whether the interruption occurred in Go, runtime, or foreign code; it cannot run arbitrary normal Go code.

Synchronous faults such as invalid memory access can become Go panics when they correspond to recoverable Go behavior. Faults in runtime-critical or foreign code can instead be fatal or delegated. `os/signal.Notify` requests mediated notification; it does not replace handlers the runtime needs, and some signals remain special, synchronous, or uncatchable. With cgo, handler installation, alternate signal stacks, callbacks on foreign threads, and inherited masks must cooperate.

## Runtime diagnostics

Runtime tools expose evidence about mechanisms, but each measures a particular signal rather than proving a causal explanation by itself.

- **Scheduler traces:** `GODEBUG=schedtrace` reports scheduler state snapshots, not end-to-end request latency.
- **GC and scavenger traces:** Runtime debug traces show cycle and scavenging activity, not an application's complete memory ownership graph.
- **`runtime/metrics`:** Supplies runtime-defined measurements whose units and meanings must be read with the selected Go version.
- **Profiles:** CPU, heap, goroutine, block, and mutex profiles sample or record different costs; none alone proves a root cause.
- **Execution tracing:** Trace and scheduler-latency views reveal runtime events and ordering. Go 1.25's `runtime/trace.FlightRecorder` maintains an in-memory window of recent trace events.
- **Compiler evidence:** Escape output, disassembly, and SSA diagnostics show build-specific compiler decisions.
- **Race detection:** `-race` instruments code and uses runtime support.

Interpreting [runtime evidence](../../../Backend%20Engineering/05%20Observability.md) requires telemetry design beyond these runtime-specific signals.

## Runtime representations of Go values

Representation affects copying, aliasing, scanning, and escape decisions. It does not alter the language-level behavior promised by the specification.

### Strings

A string is conceptually a descriptor containing a pointer to immutable bytes and a length. Assignment copies that descriptor, not the bytes, and slicing normally creates another descriptor into the same backing storage. A small substring can therefore retain a much larger allocation. String bytes contain no heap pointers, so their storage is noscan memory.

Converting between `string` and `[]byte` normally needs distinct immutable or mutable storage, though the compiler can eliminate copies in selected contexts. Concurrent assignment to a string is still unsafe: the descriptor has multiple words and ordinary assignment does not atomically publish it.

### Slices

A slice descriptor has a backing-array pointer, length, and capacity. Passing it copies the descriptor rather than its elements, so two slices can alias one array. A zero-length slice can still retain a large backing array.

`append` follows this sequence:

1. If capacity remains, it extends the view and writes into the existing array.
2. Otherwise, it chooses a new capacity with an implementation growth heuristic.
3. It allocates an appropriately rounded backing array, copies the live prefix, and returns a new descriptor.

An append that reallocates breaks that particular backing-array relationship. Pointer-containing arrays require write barriers and GC scanning, while pointer-free arrays can use noscan spans. Capacity growth is not a guaranteed doubling rule.

### Interfaces

An empty interface records a dynamic type and data. A non-empty interface associates the dynamic type with method-dispatch metadata, commonly an `itab`. Depending on representation, an interface assignment may store a value indirectly. Converting a concrete value to an interface does not inherently require allocation: escape analysis and boxing requirements decide.

Interface equality first compares dynamic types and then uses type-specific equality; comparison panics when the dynamic value is not comparable. Compiler- and runtime-generated type metadata and caches support method dispatch and type assertions. These descriptors also connect ABI metadata, pointer maps, reflection, and dynamic dispatch.

### Maps

Current Go maps use Swiss Tables rather than the older bucket-and-overflow-bucket model.

- **Group layout and lookup:** A group has eight key/value slots and an eight-byte control word. A hash divides into H1 and H2: H1 chooses a starting group and probe sequence, while H2 occupies control bytes that filter a group with word-level operations before full key comparison. Quadratic probing searches later groups.
- **Deletion and growth:** Deleted entries can remain tombstones because turning them into empty slots could incorrectly terminate a later probe. A small map fits in one group; larger maps use multiple tables selected through a directory resembling extendible hashing. Growth can replace a table or split it in two, bounding the size of an individual growth operation.
- **Iteration and synchronization:** Iteration order is deliberately unspecified and randomized. Deleting an unseen entry prevents its return, a new entry may or may not be observed, and a returned modified entry exposes its latest value. During growth, the iterator avoids duplicate entries while consulting replacement tables for current values. Pointer-valued keys must not refer to addresses that stack copying can move, so compiler placement decisions prevent unsafe stack references from being stored in a map. Unsynchronized concurrent map writes are invalid; runtime detection of some such operations is diagnostic behavior, not synchronization. [`internal/runtime/maps/map.go`](https://go.dev/src/internal/runtime/maps/map.go) documents the current design.

## Defer, panic, and recover

The compiler does not universally implement `defer` as a heap list of closures. Eligible functions use open-coded defers represented by function-local state and metadata; other paths use stack-allocated records or heap-backed records when lifetime or control flow requires them. The compiler emits enough metadata for panic unwinding to discover open-coded defers. Deferred arguments and receivers are evaluated when the `defer` statement executes, and normal return invokes defers in reverse registration order.

Panic handling proceeds in the current G:

1. The runtime constructs or obtains panic state and associates it with the G.
2. It walks that goroutine's frames and executes applicable deferred functions.
3. It continues unwinding unless a valid recovery succeeds.
4. An unhandled panic prints diagnostic information and terminates the process.

A panic unwinds only its originating goroutine; other goroutines do not receive it, even though an unhandled panic later ends the process. `recover` is meaningful only when called by a deferred function while that goroutine unwinds the corresponding panic. Calls outside that context, including indirect calls that fail the required boundary, return `nil`. Successful recovery stops the unwinding and follows the language's return semantics; it does not jump back to the panicking statement.

This differs from a runtime fatal error or `throw`, an unrecoverable process fault, and `os.Exit`, which terminates without running defers.

## Unsafe pointers and object mobility

A Go pointer keeps its reachable object alive, whereas a `uintptr` is an integer and not a GC-visible reference. Converting a pointer to `uintptr`, retaining it, and later converting it back can lose liveness and violate pointer rules. Some conversions are valid only within one expression because the compiler and runtime recognize that pattern.

Pointers into goroutine stacks require additional care because stack copying changes their addresses. The current heap is non-moving, but that implementation detail does not grant unrestricted pointer use as a language guarantee. `runtime.KeepAlive` establishes a liveness boundary after an object's final foreign or syscall use; it is not a general memory barrier. `checkptr` detects selected invalid pointer arithmetic and conversions but cannot prove arbitrary unsafe code correct.

These restrictions make syscall argument liveness, finalizers and cleanups, foreign-memory ownership, cgo pointer passing, pointer-valued map keys, and GC pointer metadata compatible with a movable-stack runtime.

## Object lifetime, finalizers, and cleanups

Reachability is not lexical scope. The compiler can treat a value as dead before its surrounding function returns once it proves no later use; references in stacks, globals, runtime structures, or finalizer state can also extend lifetime.

A finalizer becomes eligible only after the runtime determines that its object is unreachable. It runs asynchronously in a runtime-managed goroutine, has no prompt-execution guarantee, and may never run before process termination. It can resurrect an object by making it reachable again, and cycles involving finalizers complicate reachability. Finalizers are therefore unsuitable for correctness-critical release of files, locks, transactions, or network resources.

`runtime.AddCleanup`, introduced in Go 1.24, provides a separate cleanup mechanism rather than finalizer-equivalent semantics. Cleanups run after an object becomes unreachable, can run concurrently, and have their own documented caveats and lifecycle constraints. They still do not provide prompt or guaranteed release, so explicit resource management remains necessary.

The required liveness boundary for a foreign call is:

1. The program performs its final foreign or syscall use of an object.
2. The compiler might otherwise regard that object as dead before function return.
3. `runtime.KeepAlive(obj)` after the operation establishes the required liveness point.
4. This prevents premature cleanup or finalization; it does not synchronize ordinary shared-memory access.

## Deadlock and goroutine leaks

The runtime can identify a restricted global deadlock condition: no runnable goroutines, no executing Go work capable of progress, and no relevant timers, network events, or runtime work expected to make a G runnable. It can then report that all goroutines are asleep.

- A spinning or continuously runnable G can conceal a logical deadlock.
- The runtime cannot generally know whether an external system will respond.
- A G blocked forever while unrelated Gs continue is a leak, not a global deadlock.
- Cyclic application dependencies can remain invisible when foreign calls or external events participate.

Go 1.26 has an experimental goroutine-leak profile, enabled with `GOEXPERIMENT=goroutineleakprofile` and exposed through a `pprof` endpoint. It uses reachability relationships between blocked Gs and synchronization objects to identify some Gs that cannot be awakened; it cannot detect every leak, including cases where a synchronization object remains reachable through globals or runnable G state. The feature is expected to become enabled by default in Go 1.27.

## Race detector internals

Building with `-race` causes compiler instrumentation around memory accesses and synchronization. The linked runtime uses ThreadSanitizer-derived machinery to record access histories and happens-before edges, and standard synchronization operations include hooks it understands. Reports identify conflicting accesses and relevant goroutine-creation stacks.

Instrumentation changes timing, memory use, binary size, and scheduler behavior. The absence of a report establishes only that no detectable race occurred in the executions tested. Unsafe code, assembly, cgo, and unsupported platforms can reduce coverage. The race definition and DRF-SC semantics belong to the [Go memory model](https://go.dev/ref/mem), while [race consequences](../../../Backend%20Engineering/Concurrency/01%20Concurrency%20Fundamentals.md) follow from unsynchronized conflicting access.

## Reflection and runtime type metadata

The executable includes runtime type descriptors used for interface conversion and assertion, equality and hashing, GC pointer maps, reflection, map operations, allocation size and alignment, method lookup, and panic formatting. Reflection therefore exposes compiler/linker-generated metadata rather than being merely a source-level library abstraction.

Dynamic inspection and calls can inhibit compiler optimization, interface conversion can require boxing, and constructing reflected values can allocate. Some reflection operations only inspect metadata and need not allocate.

## Scheduler, GC, and netpoll in one trace

The runtime's subsystems meet in a handler that reads from a network connection:

1. The handler G runs on M1 with P0 and allocates through P0's `mcache`.
2. Allocation debt can make that G perform GC assist work.
3. A nonblocking socket read returns `EAGAIN`, so `pollDesc` records the waiter and parks the G.
4. M1 returns through `g0` to the scheduler, which selects another runnable G for P0.
5. The OS poller reports the descriptor ready and netpoll changes the waiter state, injecting the G into runnable work.
6. Another M/P can execute the G; resumption has no M or CPU affinity.
7. A deadline timer can race with readiness to produce a timeout, while a concurrent GC can scan the safely parked G.
8. On resumption, the G retries the read because readiness did not guarantee successful consumption.
