# Application Server Concurrency

An application server often needs to handle many independent requests while making efficient use of the available CPU cores. Three separate architectural decisions shape that behavior:

1. **Application execution model:** How the application is divided into processes and threads.
2. **I/O coordination model:** How each execution unit waits for and responds to connection activity.
3. **Connection distribution model:** How listening sockets and accepted connections are distributed among those execution units.

These dimensions are related but independent. A multi-process server, for example, can have all processes compete on one shared listening socket or give each process its own listening socket. A single-threaded worker can use an event loop to coordinate many connections, while a multi-process or multi-threaded deployment can give each execution unit its own event loop. Likewise, a multi-threaded server can use one dedicated acceptor thread or distribute connection handling among several threads.

## Application Execution Models

The execution model determines what processes and threads compose the application and how resources are shared between them.

A **process** primarily acts as a resource and isolation boundary. It owns resources such as a [virtual address space](../../Operating%20Systems/03%20Memory%20Management.md#Virtual%20Memory) and file descriptor table. The actual schedulable execution units are its **threads**: the operating-system scheduler places runnable threads onto CPU cores.

### Single-Threaded Process

A single-threaded application consists of one process with one primary application execution thread.

- **Execution Simplicity:** Only one sequence of application instructions executes at a time, so application code does not need to coordinate multiple threads concurrently modifying the same memory.
- **I/O Concurrency:** Single-threaded does not mean that the server can handle only one connection at a time.
    - A thread can multiplex many concurrent I/O operations using [non-blocking sockets](../../Operating%20Systems/07%20Socket%20Management.md#Blocking%20and%20Non-Blocking%20Sockets) and an event loop.
    - While one network operation is waiting for the kernel or another machine, the thread can continue processing work associated with another connection.
- **CPU and Blocking Limit:** A long CPU-bound operation or a blocking system call prevents that thread from processing other application work until the operation completes.
- **Common Examples:** Node.js and Redis are commonly associated with this event-loop-oriented application model, although supporting runtime or background work may involve additional threads or processes.

### Multi-Process

A multi-process application runs several worker processes as part of the same application.

- **Isolation:** Each process normally has its own virtual address space, page tables, and other process-level resources.
    - One process cannot normally access another process's private memory directly.
- **CPU Parallelism:** Because each process contains at least one schedulable thread, workers from different processes can execute simultaneously on different CPU cores.
- **Communication Cost:** Isolation makes communication less direct.
    - Processes that need to exchange data must use [Inter-Process Communication](../../Operating%20Systems/08%20Inter-Process%20Communication.md#Process%20Boundaries%20and%20Communication) or explicitly mapped shared memory.
    - If several processes modify the same shared state, that state still requires synchronization.
- **Duplicated State:** Multiple processes duplicate some application and kernel state.
- **Address-Space Switching:** Switching execution between threads belonging to different processes can additionally require changing the active address-space context.
- **Common Examples:** NGINX and PostgreSQL make extensive use of multiple worker processes.

> [!example] Redis Background Persistence  
> Redis provides a useful example of why processes can be valuable even when the main server uses a predominantly single-threaded execution model. For background persistence operations such as an RDB snapshot, Redis can `fork()` a child process to write the snapshot while the parent continues serving client requests. Through Copy-on-Write, the parent and child initially share the same physical memory pages; individual pages are copied only when one of the processes modifies them.

### Multi-Threaded

A multi-threaded application uses one process containing several OS threads.

- **Shared Process Resources:** Threads share process-level resources, including the same virtual address space and [file descriptors](../../Operating%20Systems/02%20The%20Anatomy%20of%20a%20Process.md#File%20Descriptors%20%28FDs%29), while each thread maintains its own execution state, including registers and stack.
- **Cheap Communication:** Because threads share memory directly, one thread can write an object to the heap and another can access the same object without transferring it through an IPC mechanism.
- **Synchronization Requirement:** Shared mutable state introduces [race conditions](01%20Concurrency%20Fundamentals.md#Race%20Conditions) when several threads access it concurrently.
    - Synchronization mechanisms can make the access correct, but contention around shared state can reduce throughput.
- **CPU Parallelism:** Multiple runnable threads can execute simultaneously on different CPU cores when the workload can be divided into independent work.

## I/O Coordination Models

<!-- TODO: Add blocking-per-connection, bounded worker-pool, runtime-managed task-per-connection, and hybrid event-loop/worker-offload models. Contrast their resource costs, backpressure behavior, and CPU-bound-work handling with explicit event loops. -->

The execution model determines which workers exist. The I/O coordination model determines how a worker makes progress across many active connections when an individual socket operation cannot proceed immediately. It is separate from connection distribution, which determines where a newly arrived connection goes.

### Event-Driven Connection Handling

An event-driven server retains state for active listeners and connections, waits for events across them, and dispatches the handler associated with each event. It avoids dedicating one blocked execution unit to every connection that is waiting for I/O.

An event loop repeats this sequence:

1. It records the state needed to continue each connection and registers readiness interests or submits I/O operations.
2. It waits for one or more events.
3. It maps each event to the connection or operation that produced it.
4. The corresponding handler advances that connection's state, then updates its interests or submits its next operation.

[Readiness- and completion-based I/O](../../Operating%20Systems/07%20Socket%20Management.md#Readiness%20and%20Completion%20Compared) differ in what the event represents:

| Model | Event means | Handler action |
| --- | --- | --- |
| **Readiness-driven** | A socket may be able to make progress. | The handler attempts `accept()`, `read()`, `write()`, or another appropriate operation. |
| **Completion-driven** | A submitted I/O operation has reached a result. | The handler processes that result and submits subsequent work when needed. |

The [Reactor pattern](../../Operating%20Systems/07%20Socket%20Management.md#Reactor%20Pattern) organizes dispatch around readiness, while the [Proactor pattern](../../Operating%20Systems/07%20Socket%20Management.md#Proactor%20Pattern) organizes dispatch around completed operations. They are two event-driven architectures, not different process or thread models.

Event-driven coordination provides I/O concurrency, not CPU parallelism. One event-loop thread can coordinate many connections, but a CPU-intensive handler or a blocking operation prevents that loop from processing later events. Such work must run in another execution unit when the server needs the loop to remain responsive.

- **Execution-model relationship:** A server can use one event loop in a single-threaded process or run separate loops in several threads or processes. Multiple loops provide CPU parallelism when the operating system schedules them on different cores.
- **Connection-distribution relationship:** Listener and acceptor architecture assigns a transport connection to a worker or loop. The event loop then coordinates I/O for the connections assigned to it.

## Connection Distribution Models

The application execution model determines **what workers exist**. A separate decision determines **how incoming network connections reach those workers**.

Application servers build connection-distribution architectures from listening sockets, `accept()`, connected sockets, descriptor sharing, and the [listener, acceptor, and worker roles](../../Operating%20Systems/07%20Socket%20Management.md#Listener%2C%20Acceptor%2C%20and%20Worker%20Roles).

- **Primary Model:** These architectures primarily distribute TCP connections.
- **UDP Difference:** [Datagram sockets](../../Operating%20Systems/07%20Socket%20Management.md#Datagram%20Sockets) do not use `accept()` to create a new socket for every peer.
    - In protocols such as QUIC, workers receive UDP datagrams and the QUIC implementation associates those packets with logical QUIC connections.

### Single Listener, Single Worker

One execution thread owns the listening socket, accepts connections, and processes their requests.

- **Listener Ownership:** One thread owns the listening socket.
- **Acceptance Path:** The same thread accepts incoming connections.
- **Worker Assignment:** The accepting thread is also the only application worker.
- **I/O Concurrency:** Maintaining high connection concurrency requires the worker to avoid spending long periods blocked on individual connections.
    - Event-driven servers commonly combine this architecture with non-blocking I/O so one thread can maintain many active connections.
- **Main Benefit:** The architecture is straightforward and avoids coordination among multiple application workers.
- **Main Trade-off:** Only one application thread executes application work at a time.
    - CPU-heavy request processing can therefore become a bottleneck regardless of how many connections are managed concurrently.

> [!example] Node.js Event Loop
> A single [Node.js process](../../Technologies/NodeJS/01%20Basics/04%20Internals.md#Event%20loop) combines the listener, acceptor, and worker roles in its event loop. Network I/O waits through [operating-system readiness mechanisms](../../Operating%20Systems/07%20Socket%20Management.md#Readiness-Based%20I%2FO), allowing the event loop to process callbacks for other connections. A long CPU-bound JavaScript callback nevertheless prevents that application thread from accepting or processing more work until it completes.

### Single Acceptor, Multiple Workers

One execution unit owns the listening socket and accepts incoming connections. After accepting a connection, it hands the resulting connected socket or associated work to one of several workers.

The flow is:

1. A connection becomes available through the listening socket.
2. The acceptor calls `accept()`.
3. The kernel returns a new connected socket.
4. The acceptor selects a worker.
5. The worker handles the connection or request.

Features:

- **Listener Ownership:** One acceptor owns or controls the listening socket.
- **Acceptance Path:** All accepted connections pass through that execution unit.
- **Worker Assignment:** The acceptor explicitly selects one of several workers.
- **Worker Type:** Workers may be threads or processes.
    - Threads inside the same process already share the process's file descriptor table.
    - Process-based architectures require an appropriate mechanism for sharing or transferring the accepted connection.
- **Main Benefit:** Centralized connection distribution can simplify balancing because one component decides where each connection goes.
- **Main Trade-off:** The acceptor can become a bottleneck if the connection arrival rate becomes high enough.

> [!example] Go `net/http` Goroutines
> A Go [`net/http` server](../../Technologies/Golang/99%20Misc/Go%20Internals.md#The%20Goroutine-Per-Connection%20Model%20%28Single%20Listener,%20Multiple%20Workers%29) accepts connections in one goroutine and starts a separate goroutine to handle each accepted connection. The acceptor remains available for later arrivals while the Go runtime schedules the connection-handling goroutines as application workers.

### Multiple Workers, Single Shared Listening Socket

Instead of using one dedicated acceptor, several workers [share a listening socket](../../Operating%20Systems/07%20Socket%20Management.md#Shared%20Listening%20Socket) and call `accept()` themselves.

- **Listener Ownership:** Several workers refer to the same underlying listening socket.
- **Acceptance Path:** Each worker can call `accept()` directly.
    - When a connection becomes available, one worker successfully accepts it and handles the resulting connected socket.
- **Worker Type:** The architecture does not determine whether workers are processes or threads.
    - Multiple threads can share a socket through their common process resources.
    - Related processes can share a listening socket through mechanisms such as descriptor inheritance.
- **Main Benefit:** There is no dedicated central acceptor.
- **Coordination Cost:** Workers coordinate around one shared listening resource.
- **Historical Risk — Thundering Herd:** Several sleeping workers can be awakened even though only one can successfully accept the available connection.
    - Unsuccessful workers wake, compete for the same work, and return to waiting, wasting CPU cycles.

> [!example] Gunicorn Pre-Fork Workers
> In a pre-fork Gunicorn deployment, the listening socket is created before workers are forked, so multiple worker processes inherit references to that listener and call `accept()`. The kernel maintains the pending connection state; the workers consume completed connections when they are ready to run application code.

### Multiple Listeners with `SO_REUSEPORT`

With [`SO_REUSEPORT`](../../Operating%20Systems/07%20Socket%20Management.md#Multiple%20Listeners%20with%20SO_REUSEPORT), multiple workers can each own an independent listening socket while binding to the same local address and port.

- **Listener Ownership:** Each worker owns an independent listening socket.
- **Kernel Distribution:** The kernel distributes incoming traffic among the sockets in the `SO_REUSEPORT` group instead of making workers contend for one listener.
- **TCP Assignment:** Different incoming TCP connections can be assigned to different listening sockets and workers.
- **Acceptance Path:** Each worker accepts and processes the connections assigned to its own listener without coordinating access to one shared accept path.
- **Main Benefit:** This can reduce contention around connection acceptance and distribute networking work across multiple CPU cores.
- **Main Trade-off:** Kernel-level distribution does not necessarily reflect application-level workload.
    - Two connections may look equivalent to the kernel while requiring very different amounts of CPU time, memory, or response processing.

> [!example] NGINX Socket Sharding
> [NGINX](../../Technologies/NGINX/02%20NGINX%20Internals.md#Connection%20Acceptance%20and%20Socket%20Management) can use `SO_REUSEPORT` so multiple worker processes each own an independent listening socket bound to the same address and port. The kernel distributes incoming connections among those listeners, reducing contention around a single shared accept path. Kernel distribution selects a listener; the selected NGINX worker then accepts and processes the connection.

#### Multiplexed Protocols

This limitation becomes more important when an application protocol can **multiplex multiple requests over one transport connection**.

- **Distribution Unit:** `SO_REUSEPORT` distributes transport connections or traffic, not application-level requests or streams.
- **[HTTP/2](../../Networking/02%20Protocols/09%20HTTP2.md#HTTP%2F2) Consequence:** Many independent HTTP streams can exist inside a single TCP connection.
    - `SO_REUSEPORT` distributes the TCP connection between workers, not the individual HTTP/2 streams.
    - Once one worker accepts that connection, all of its transport traffic arrives through the same connected socket.
    - The HTTP/2 implementation can still dispatch application work for individual streams to other threads or workers after the connection has been accepted, independently of which worker owns the transport I/O.
- **[HTTP/3](../../Networking/02%20Protocols/10%20HTTP3.md#HTTP%2F3) / QUIC Consequence:** HTTP/3 runs over QUIC, which multiplexes streams over UDP.
    - `SO_REUSEPORT` can distribute UDP traffic among multiple sockets, but it does not understand HTTP/3 requests or streams.
    - More sophisticated routing can use mechanisms such as BPF with `SO_REUSEPORT` to keep packets associated with a particular QUIC connection on an appropriate worker.
    - Even then, routing operates on transport-level information rather than individual HTTP requests.
- **Load-Balancing Limitation:** Balanced transport connections do not necessarily produce balanced application work.
    - A single long-lived HTTP/2 or HTTP/3 connection may carry many simultaneous requests while another connection carries almost none.
