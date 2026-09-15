# Inter-Process Communication (IPC)

Processes isolate their ordinary virtual-memory mappings, so they need an explicit mechanism to exchange data or coordinate work. IPC combines channel-based mechanisms, which transfer data through kernel-managed objects, with shared-memory mechanisms, which intentionally expose the same storage to several processes. [Process isolation](03%20Memory%20Management.md#Virtual%20Memory) and [file descriptors](02%20The%20Anatomy%20of%20a%20Process.md#File%20Descriptors%20%28FDs%29) establish the prerequisite models.

## Process Boundaries and Communication

A process cannot directly read or write another process's ordinary address space. IPC creates a controlled relationship across that boundary, but the mechanism determines whether it transfers bytes, exposes shared storage, preserves message boundaries, or only signals an event.

- **Channel-based IPC:** Pipes and sockets carry data through kernel-managed endpoints and buffers. Their finite buffering produces backpressure when one participant outpaces another.
- **Shared-memory IPC:** Compatible mappings can make the same physical pages visible in several processes. This avoids copying payload through a separate pipe or socket, but it does not establish when a reader may consume data or when a writer may modify it.
- **Coordination:** Shared mutable state needs a protocol that protects its invariants and establishes when state is ready to observe. Signals and channel readiness can notify a process, but notification alone does not make concurrent access safe.

## Descriptor-Based Channels

On Unix-like systems, a process ordinarily accesses a pipe or socket endpoint through a file descriptor. The descriptor is a process-local handle, not the channel or its buffer; its number is chosen from an available slot in that process's descriptor table. Code must therefore not assume that a newly created endpoint has a particular number.

Descriptor lifetime controls whether an endpoint remains usable. `fork()` gives a child descriptors referring to the parent's open resources, `dup()` creates another descriptor referring to the same resource, and `close()` removes one such reference. An endpoint reaches its end-of-file or shutdown state only according to the resource's own rules after the relevant references are gone.

[POSIX process control](05%20Process%20Management.md#POSIX%20Process-Control%20Interface) explains descriptor inheritance across `fork()`, while [descriptor operations and lifetime](02%20The%20Anatomy%20of%20a%20Process.md#Descriptor%20Operations%20and%20Lifetime) explains the common handle model.

## Shared-Memory IPC

`mmap()` creates a mapping in a process's virtual address space; a shared mapping gives multiple processes virtual addresses that ultimately refer to the same physical pages. For compatible `MAP_SHARED` mappings, a process can observe changes made through another process's mapping without transferring those bytes through a pipe or socket. [Memory visibility and IPC](02%20The%20Anatomy%20of%20a%20Process.md#Memory%20Visibility%20%26%20Inter-Process%20Communication%20%28IPC%29) explains the mapping, backing, lifetime, and copy-on-write distinctions.

Shared storage is not synchronization. A writer and reader still need to agree on ownership, update order, and readiness; otherwise a reader can observe incomplete or conflicting state. [Synchronization mechanisms](../Backend%20Engineering/Concurrency/01%20Concurrency%20Fundamentals.md#Synchronization%20Mechanisms) provide the relevant mutex, semaphore, atomic-operation, and condition-variable models.

## Pipes

A POSIX pipe is a kernel-managed inter-process communication (IPC) resource that carries a bounded, unidirectional byte stream. A producer writes bytes at one end and a consumer reads them at the other. The kernel buffer absorbs temporary differences in their execution rates, but its finite capacity eventually makes each side's progress depend on the other.

### Endpoints and Kernel State

Calling `pipe(p)` creates a pipe and stores two process-local [file descriptors](02%20The%20Anatomy%20of%20a%20Process.md#File%20Descriptors%20%28FDs%29) in `p`: `p[0]` is the read end, and `p[1]` is the write end.

- **Descriptor handles:** The descriptors refer to the pipe; they are not the pipe buffer itself.
- **Kernel pipe state:** The kernel maintains the buffered byte stream and the references to its read and write ends.
- **Anonymous pipe:** An anonymous pipe has no filesystem pathname. Related processes commonly share its endpoints when descriptors created before `fork()` are inherited.

### Stream and File Semantics

A pipe exposes an ordered byte stream rather than discrete messages. A `read()` consumes whichever bytes are currently available, so one read result does not reveal application-message or `write()` boundaries.

Pipes are non-seekable: consuming bytes advances through the stream, but `lseek()` does not supply the position semantics of a regular file. This is one example of how [resource-specific operations](02%20The%20Anatomy%20of%20a%20Process.md#Resource-Specific%20Operations) remain different beneath the common descriptor interface.

On Linux, [`splice()`](02%20The%20Anatomy%20of%20a%20Process.md#Specialized%20Descriptor%20Transfers%20and%20Zero-Copy) transfers bytes between a pipe and another compatible file-descriptor-backed resource without copying the payload through an application buffer. At least one descriptor must refer to a pipe; paths such as regular file → pipe and pipe → socket depend on endpoint support.

> [!note] Pipes and Go Channels
> [Go channels](../Technologies/Golang/01%20Essentials/09%20Concurrency.md#Channel) transfer typed values and preserve value boundaries; pipes transfer untyped stream bytes. Both can use bounded buffering and impose blocking or backpressure when producer and consumer rates differ.

### Blocking and Backpressure

A pipe buffer decouples producer and consumer only while it holds unread bytes or has usable capacity. Once the buffer is empty or full, a blocking operation waits for the other side to change that state.

- **Empty pipe:** A `read()` blocks while the pipe is empty and at least one write-end reference remains open. When a writer adds bytes, the reader can resume and consume them.
- **Full pipe:** A `write()` blocks when the pipe lacks enough capacity for the operation to make progress. Reading frees capacity and allows the writer to resume.
- **Backpressure:** A consumer that reads too slowly eventually fills the bounded pipe buffer and constrains producer progress instead of allowing queued data to grow without bound.

While an operation waits, its calling thread is in the operating system's [blocked state](05%20Process%20Management.md#Core%20Mechanics), allowing another runnable thread to use the CPU.

### Readiness and Completion

Pipes work with readiness interfaces such as `poll()` and `epoll()`. Readiness answers whether an operation can make progress without blocking; it does not perform that operation or deliver its result. This lets one thread coordinate many pipes, sockets, and other event sources instead of blocking on one empty stream.

- **Readable read end:** The read end is readable when the pipe holds bytes or when an end condition is observable. A subsequent `read()` therefore either consumes available bytes or returns EOF after the buffer is empty and no write-end references remain.
- **Writable write end:** The write end is writable when the pipe has capacity for a write to make progress. A writer still performs the `write()` after receiving the notification.

A readiness-driven consumer follows this sequence:

1. The consumer waits for the pipe read end to become readable.
2. A producer writes bytes, or the last write-end reference closes.
3. The readiness interface reports the state change.
4. The consumer calls `read()` and handles bytes or EOF.

Completion-based I/O instead submits a concrete operation, including its destination buffer, before data is available. A submitted pipe read remains pending until the system can perform the transfer, then reports a completion for that particular operation. The application therefore tracks outstanding operations and keeps each operation's buffer valid until its completion is processed.

The two models differ in when the application supplies the I/O operation: readiness reports permission to attempt a read or write, while completion reports the result of work already submitted. An implementation can expose completion semantics while using readiness or polling internally. The same distinction applies to [readiness- and completion-based socket I/O](07%20Socket%20Management.md#Readiness%20and%20Completion%20Compared), where transport semantics add networking-specific concerns.

#### Buffering and Backpressure Boundary

Pending reads do not increase the pipe's kernel buffer capacity. When a submitted read completes, it drains bytes from that buffer into its user-space destination buffer. Pre-submitting reads can therefore drain the pipe earlier and queue additional data in user-space memory; it moves the effective backpressure boundary downstream rather than increasing the pipe's bounded kernel buffer.

### EOF and Pipe Lifetime

A reader observes EOF only after the pipe has no more buffered data and no process retains a write-end reference:

1. The reader consumes every buffered byte.
2. Every write end is closed.

An open write end means the kernel must still allow for a future write. An empty pipe with any write-end reference is therefore a waitable stream rather than EOF. Processes that inherit endpoints must close every unused end; otherwise, a process that only reads can keep its own later read waiting by retaining its write end. These rules follow the same [descriptor lifetime](02%20The%20Anatomy%20of%20a%20Process.md#Descriptor%20Operations%20and%20Lifetime) model as other FD-backed resources.

### Anonymous Pipes and FIFOs

An anonymous pipe is reached through descriptors that a process already holds. It is commonly created before `fork()` so related processes inherit references to the same kernel pipe state; descriptor-passing mechanisms can also transfer an endpoint to another process.

A **FIFO** (named pipe) adds a filesystem pathname that independent processes can use as a rendezvous point. Once opened, a FIFO still carries a bounded byte stream through kernel-managed state. Its pathname does not make the transferred bytes persistent regular-file content.

### Shell Pipeline Construction

Shell pipelines combine pipe endpoint configuration with the [POSIX process-control interface](05%20Process%20Management.md#POSIX%20Process-Control%20Interface). For `cat file | grep foo`, the pipe-specific result is that `cat` receives the write end as FD `1` and `grep` receives the read end as FD `0`.

The following fragments show the pipe-specific descriptor setup. They omit argument construction and error handling so that each fragment exposes one change to endpoint references.

1. **Create the pipe:** The shell starts with FDs `0`, `1`, and `2` connected to terminal input, output, and error. It must create the kernel communication resource before either child exists:

    ```c
    int p[2];
    pipe(p);
    ```

    `p[0]` now refers to the read end and `p[1]` to the write end. Assume they are FDs `3` and `4`; the actual numbers depend on which descriptors are available. The shell holds both endpoint references, so each later `fork()` gives its child access to the same kernel pipe state.

2. **Connect `cat` to the write end:** The first child inherits references to both pipe endpoints. Its setup path makes the write-end construction handle become standard output and discards every pipe reference it will not use:

    ```c
    dup2(p[1], 1);
    close(p[0]);
    close(p[1]);
    ```

    FD `1` retains the write-end reference after `p[1]` is closed; the child no longer retains a read-end reference. When that child executes `cat`, its prepared FD `1` determines where `cat` writes.

3. **Connect `grep` to the read end:** The parent still holds both construction handles when it creates the second child, so this child also receives both endpoints. Its setup path makes the read-end handle become standard input and discards the write-end reference:

    ```c
    dup2(p[0], 0);
    close(p[0]);
    close(p[1]);
    ```

    FD `0` retains the read-end reference after `p[0]` is closed; the child no longer retains a write-end reference. When that child executes `grep`, its prepared FD `0` determines where `grep` reads.

4. **Release the shell's construction handles:** Once both children have inherited the endpoints, the shell no longer needs either reference:

    ```c
    close(p[0]);
    close(p[1]);
    ```

    Closing the shell's write-end reference allows `grep` to observe EOF once `cat` closes its write end and the pipe's buffered bytes are consumed.

Temporary descriptors are construction handles, not final stream assignments. Closing them prevents a process that does not need an endpoint from extending that endpoint's lifetime. The resulting stream connection is `cat` FD `1` → pipe → `grep` FD `0`.

After the children execute their commands, `cat` opens `file` and transfers its bytes approximately as follows:

```c
read(file_fd, buffer, n);
write(1, buffer, n);
```

FD `1` refers to the pipe write end, so that `write()` supplies bytes to the pipe. `grep` reads from FD `0`, which refers to the pipe read end, and writes matching output to its unchanged FD `1`, the terminal:

```c
read(0, buffer, n);
```

When `cat` reaches file EOF and exits, its write descriptor closes. After `grep` consumes the remaining pipe bytes and no write-end references remain, a later `read(0, ...)` returns `0` to signal EOF.

## Unix-Domain Sockets and Socket Pairs

Unix-domain sockets provide socket communication between processes on the same host. They use the `AF_UNIX` [socket family](07%20Socket%20Management.md#Socket%20Families) while retaining the descriptor, buffering, lifetime, and I/O model shared by other sockets.

An **addressed Unix-domain socket** provides a rendezvous mechanism. For a connection-oriented socket type, a server creates a socket, binds a [local Unix-domain address](07%20Socket%20Management.md#Binding%20and%20Local%20Endpoints), and begins listening. Independently started clients create their own sockets and connect through that address. The listening address remains a stable rendezvous point while each accepted connection has its own endpoint state.

With a pathname-based address, the pathname identifies where the peers meet; after connection establishment, application data flows through the resulting socket endpoints rather than through the pathname itself.

`socketpair()` solves a different problem. It creates two unnamed, already-connected socket endpoints in one operation. No `bind()`, `listen()`, `connect()`, or `accept()` rendezvous is required. The processes must instead receive those endpoint descriptors through an existing relationship, commonly [descriptor inheritance across `fork()`](05%20Process%20Management.md#POSIX%20Process-Control%20Interface) or an explicit descriptor-passing mechanism.

A socket pair therefore provides the bidirectional channel that would otherwise require two oppositely directed pipes when each peer needs an independent byte stream. The mechanisms differ in how peers obtain their endpoints:

| Property | Addressed Unix-domain socket | `socketpair()` |
| --- | --- | --- |
| Peer rendezvous | Through a Unix-domain address | Not required |
| Independently started peers | Natural fit | Requires endpoint distribution |
| Connection setup | Address-based connection lifecycle | Endpoints created already connected |
| Filesystem pathname required | Only for pathname-based addressing | No |
| Connected communication | Bidirectional for the connected socket types discussed here | Bidirectional |
| Byte stream or record semantics | Determined by socket type | Determined by socket type |

The way peers obtain their endpoints is separate from the socket's data model:

- **`SOCK_STREAM`:** Transfers an ordered byte stream and does not preserve individual write boundaries.
- **`SOCK_SEQPACKET`:** Transfers ordered records while preserving message boundaries, where the address family and operating system support it.

Both addressed Unix-domain sockets and socket pairs can use socket types supported by the platform. Addressability, directionality, and message-boundary semantics therefore describe separate properties of the channel.

[Socket management](07%20Socket%20Management.md#Sockets%20as%20Kernel%20Objects) provides the common descriptor-backed socket model; the address family and binding rules determine how an addressed local socket becomes discoverable.

## Stream Framing and Logical Channels

<!-- TODO: Explain how a receiver accumulates stream bytes until a complete frame is available, validates a declared length before allocating or waiting for a payload, and recovers or closes the channel after malformed input. Compare that application protocol with record boundaries supplied by `SOCK_SEQPACKET`. Possible connections: [Socket Management — Stream Sockets](07%20Socket%20Management.md#Stream%20Sockets) for byte-stream behavior; [TCP](../Networking/02%20Protocols/05%20TCP.md) for stream transport. -->

A stream delivers bytes, not application messages. A receiver can obtain a partial message, several messages together, or data ending in the middle of an application-level field. The application protocol must therefore define how the receiver identifies each message's beginning and end.

A common frame contains a message type, a payload length, and the payload. The type selects how the payload is interpreted, while the length lets the receiver determine how many bytes belong to that message before processing the next frame. A record-preserving transport such as `SOCK_SEQPACKET` supplies record boundaries, but the application still defines the meaning of each record.

One connection can carry several logical message types when a framing protocol distinguishes them. Separate pipes or socket pairs instead isolate those channels through independent endpoints. The choice depends on whether independent endpoint lifetime and flow control are more valuable than one shared protocol and connection.

## Unix-Domain Sockets and Loopback TCP/IP

<!-- TODO: Expand the path from a local TCP/IP send through the host networking stack to local delivery. Contrast Unix-domain addressing, access control, deployment constraints, and interoperability with an IP address and port. Keep transport lifecycle details in Socket Management and TCP. Possible connections: [Socket Management — Binding and Local Endpoints](07%20Socket%20Management.md#Binding%20and%20Local%20Endpoints), [TCP](../Networking/02%20Protocols/05%20TCP.md), [UDP](../Networking/02%20Protocols/04%20UDP.md), and [Network Security — Service Listening Scope and Network Reachability](../Security/05%20Architecture%20and%20Infrastructure%20Security/Network%20Security/01%20Network%20Security.md#Service%20Listening%20Scope%20and%20Network%20Reachability). -->

`AF_UNIX` selects local socket communication. `AF_INET` selects IPv4 Internet-protocol communication, including local loopback; `127.0.0.1` is the conventional IPv4 loopback address, and `::1` is the IPv6 loopback address. `localhost` is commonly configured to resolve to one or both loopback addresses.

A loopback connection remains on the host, but it still follows the IP and transport-stack model rather than Unix-domain socket addressing. It does not traverse an Ethernet or Wi-Fi link to reach another machine. A Unix-domain socket instead uses local socket addressing and cannot be used by a process on another host.

- **Unix-domain socket:** Fits communication that is inherently local and can use Unix-domain addressing.
- **Loopback TCP/IP:** Fits local communication that should use the same IP address, port, and TCP socket model as a networked service.

[TCP](../Networking/02%20Protocols/05%20TCP.md) and [UDP](../Networking/02%20Protocols/04%20UDP.md) explain the transport behavior used by Internet-domain sockets; [Socket Management](07%20Socket%20Management.md#Binding%20and%20Local%20Endpoints) explains binding and local acceptance scope.

## Mechanism Selection

<!-- TODO: Develop a comparison across directionality, peer discovery, addressing, byte-stream versus record semantics, message framing, buffering, synchronization, and cross-host reachability. Use concrete requirements to show why no mechanism is universally preferable. Possible connections: [Memory visibility and IPC](02%20The%20Anatomy%20of%20a%20Process.md#Memory%20Visibility%20%26%20Inter-Process%20Communication%20%28IPC%29) for shared mappings; [Synchronization Mechanisms](../Backend%20Engineering/Concurrency/01%20Concurrency%20Fundamentals.md#Synchronization%20Mechanisms) for coordination; [Socket Management](07%20Socket%20Management.md) and [TCP](../Networking/02%20Protocols/05%20TCP.md) for socket and transport behavior. -->

Select an IPC mechanism from the required communication shape rather than from the fact that all participants happen to run locally.

- **Pipe or FIFO:** A bounded, unidirectional byte stream is sufficient. Use two channels when both peers must send independent byte streams.
- **Socket pair:** Two known peers need an unnamed bidirectional socket channel.
- **Unix-domain socket:** Local clients need to rendezvous with a local service through a Unix-domain address.
- **Loopback TCP/IP:** Local participants need Internet-domain addressing or TCP behavior that is also usable across hosts.
- **Shared mapping:** Participants need access to the same data rather than a copied byte stream, and the design includes an explicit synchronization protocol.

The mechanism's data model does not replace an application protocol. Streams require framing, shared memory requires synchronization, and every design must define endpoint lifetime, failure handling, and backpressure behavior.
