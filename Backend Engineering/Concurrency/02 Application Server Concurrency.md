# Application Server Concurrency

An application server often needs to handle many independent requests while making efficient use of the available CPU cores. There are two separate architectural decisions involved:

1. **Application execution model:** How the application is divided into processes and threads.
2. **Connection distribution model:** How listening sockets and accepted connections are distributed among those execution units.

These dimensions are related but independent. A multi-process server, for example, can have all processes compete on one shared listening socket or give each process its own listening socket. Likewise, a multi-threaded server can use one dedicated acceptor thread or distribute connection handling among several threads.

## Application Execution Models

The execution model determines what processes and threads compose the application and how resources are shared between them.

A **process** primarily acts as a resource and isolation boundary. It owns resources such as a [virtual address space](03%20Memory%20Management.md#Virtual%20Memory) and file descriptor table. The actual schedulable execution units are its **threads**: the operating-system scheduler places runnable threads onto CPU cores.

### Single-Threaded Process

A single-threaded application consists of one process with one primary application execution thread.

- Only one sequence of application instructions executes at a time, so application code does not need to coordinate multiple threads concurrently modifying the same memory. This makes the execution model comparatively simple.
- Single-threaded does not mean that the server can handle only one connection at a time. A thread can multiplex many concurrent I/O operations using non-blocking interfaces and an event loop. While one network operation is waiting for the kernel or another machine, the thread can continue processing work associated with another connection.
- The limitation appears when work requires the thread itself. A long CPU-bound operation or a blocking system call prevents that thread from processing other application work until the operation completes.
- Node.js and Redis are commonly associated with this event-loop-oriented application model, although supporting runtime or background work may involve additional threads or processes.

### Multi-Process

A multi-process application runs several worker processes as part of the same application.

- Each process normally has its own [virtual address space](03%20Memory%20Management.md#Virtual%20Memory), page tables, and other process-level resources. This provides strong isolation between workers: one process cannot normally access another process's private memory directly.
- Because each process contains at least one schedulable thread, workers from different processes can execute simultaneously on different CPU cores.
- The isolation also makes communication less direct. Processes that need to exchange data must use Inter-Process Communication or explicitly mapped [shared memory](03%20Memory%20Management.md#Virtual%20Memory). If several processes modify the same shared state, that state still requires synchronization.
- Multiple processes also duplicate some application and kernel state. Switching execution between threads belonging to different processes can additionally require changing the active address-space context, as described in [Context Switching Overhead](05%20Process%20Management.md#Context%20Switching%20Overhead).

NGINX and PostgreSQL are examples of systems that make extensive use of multiple worker processes.

> [!example] Redis Background Persistence  
> Redis provides a useful example of why processes can be valuable even when the main server uses a predominantly single-threaded execution model. For background persistence operations such as an RDB snapshot, Redis can `fork()` a child process to write the snapshot while the parent continues serving client requests. Through Copy-on-Write, the parent and child initially share the same physical memory pages; individual pages are copied only when one of the processes modifies them.
### Multi-Threaded

A multi-threaded application uses one process containing several OS threads.

- The threads share process-level resources, including the same virtual address space and [file descriptors](02%20The%20Anatomy%20of%20a%20Process.md#File%20Descriptors%20(FDs)), while each thread maintains its own execution state, including registers and stack.
- Because the threads share memory directly, communication between them can be inexpensive. One thread can write an object to the heap and another can access the same object without transferring it through an IPC mechanism.
- That shared memory introduces synchronization requirements. If several threads concurrently access mutable state, race conditions can occur. Synchronization mechanisms can make the access correct, but contention around shared state can reduce throughput.
- Multiple runnable threads can also execute simultaneously on different CPU cores, providing true parallelism when the workload can be divided into independent work.
## Connection Distribution Models

The application execution model determines **what workers exist**. A separate decision determines **how incoming network connections reach those workers**.

Backends can [establish connections](01%20How%20Connections%20are%20Established.md) and [read and send data](02%20Reading%20and%20Sending%20Data.md) using several architectures.

Three conceptual roles are useful when describing them:

- **Listener:** Owns a listening socket bound to an address and port.
- **Acceptor:** Calls `accept()` on that socket and obtains a connected socket for an incoming connection.
- **Worker:** Reads requests, executes application logic, and writes responses through connected sockets.

These roles do not necessarily correspond to separate threads or processes. One execution unit can perform all three roles, or the application can distribute them among several workers.

This model is primarily a **TCP connection-distribution model**. UDP-based protocols behave differently because there is no `accept()` operation that creates a new socket for every peer. In protocols such as QUIC, workers receive UDP datagrams and the QUIC implementation associates those packets with logical QUIC connections.

### Single Listener, Single Worker

One execution thread owns the listening socket, accepts connections, and processes their requests.

This model is straightforward, but maintaining high concurrency requires the worker to avoid spending long periods blocked on individual connections. Event-driven servers therefore commonly combine this architecture with non-blocking I/O, allowing one thread to maintain many active connections.

The main limitation is CPU execution. Regardless of how many connections are being managed concurrently, only one application thread executes their application work at a time. CPU-heavy request processing can therefore become a bottleneck.

### Single Acceptor, Multiple Workers

One execution unit owns the listening socket and accepts incoming connections. After accepting a connection, it hands the resulting connected socket or associated work to one of several workers.

The flow is:

1. A connection arrives at the listening socket.
2. The acceptor calls `accept()`.
3. The kernel returns a new connected socket.
4. The acceptor selects a worker.
5. The worker handles the connection or request.

The workers may be threads or processes.

With threads inside the same process, the workers already share the process's file descriptor table. Process-based architectures require an appropriate mechanism for sharing or transferring the accepted connection.

This architecture centralizes connection distribution, which can simplify balancing because one component decides where each connection goes. However, the acceptor can itself become a bottleneck if the connection arrival rate becomes high enough.

### Multiple Workers, Single Shared Listening Socket

Instead of using one dedicated acceptor, several workers can share a listening socket and call `accept()` themselves.

When a connection becomes available, one worker successfully accepts it and handles the resulting connected socket.

This removes the central acceptor but introduces coordination around the shared listening socket.

Historically, implementations could suffer from the **Thundering Herd** problem: several sleeping workers might be awakened when a connection arrives even though only one of them can successfully accept it. The unsuccessful workers wake up, compete for the same work, and return to waiting, wasting CPU cycles.

This architecture does not determine whether workers are processes or threads. Multiple threads can share a socket through their common process resources, while related processes can also share a listening socket through mechanisms such as descriptor inheritance.

### Multiple Listeners with `SO_REUSEPORT`

With `SO_REUSEPORT`, multiple workers can each own an independent listening socket while binding to the same local address and port.

Instead of several workers contending for one shared listening socket, the kernel distributes incoming traffic among the sockets in the `SO_REUSEPORT` group.

For TCP servers, this means different incoming connections can be assigned to different listening sockets and therefore to different workers. Each worker can then accept and process the connections assigned to its socket without coordinating access to one shared acceptor.

This can reduce contention around connection acceptance and distribute network-processing work across multiple CPU cores.

The trade-off is that kernel-level distribution does not necessarily reflect application-level workload. Two connections may look equivalent to the kernel while requiring very different amounts of CPU time, memory, or response processing.

#### Multiplexed Protocols

This limitation becomes more important when an application protocol can **multiplex multiple requests over one transport connection**.

With HTTP/2, many independent HTTP streams can exist inside a single TCP connection. `SO_REUSEPORT` distributes the TCP connection between workers, not the individual HTTP/2 streams. Once one worker accepts that connection, all of its HTTP/2 traffic arrives through the same connected socket.

- The HTTP/2 implementation can still dispatch the application work for individual streams to other threads or workers, but that happens above the socket-distribution layer and is a separate architectural decision.
- HTTP/3 has a similar issue, although its transport model is different. HTTP/3 runs over QUIC, which itself multiplexes streams over UDP. `SO_REUSEPORT` can distribute UDP packets among multiple sockets, but it does not understand HTTP/3 requests or streams.
	- More sophisticated routing can be implemented, for example by using BPF with `SO_REUSEPORT` to keep packets associated with a particular QUIC connection on an appropriate worker. Even then, the routing is based on transport-level information such as the QUIC connection, not individual HTTP/3 requests.

As a result, balanced transport connections do not necessarily produce balanced application work. A single long-lived HTTP/2 or HTTP/3 connection may carry many simultaneous requests while another connection carries almost none.