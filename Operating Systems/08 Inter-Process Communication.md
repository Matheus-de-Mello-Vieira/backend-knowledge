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

### Explicit Descriptor Passing

Explicit descriptor passing gives an already-running process access to an already-open resource. It transfers a reference to the underlying kernel-managed resource, not the sender's descriptor number: the receiving process receives a newly allocated entry in its own descriptor table. The two descriptor numbers therefore need not match, even though both entries refer to the same pipe end, socket, or open file description.

On Unix-like systems, connected Unix-domain sockets support this transfer as ancillary (control) data. The sender supplies an `SCM_RIGHTS` control message to `sendmsg()`, and the receiver obtains the new descriptor through `recvmsg()`. Ordinary bytes sent with the control message form the application protocol that identifies the resource and its intended use; passing a descriptor neither discovers a peer nor creates a new channel.

- **Shared resource state:** The received descriptor refers to the same underlying open resource rather than reopening it. Resource-specific shared state, such as a regular file's current offset or a socket endpoint's connection state, remains shared.
- **Independent descriptor lifetime:** Each process closes its own descriptor. Closing the sender's descriptor does not invalidate the receiver's reference, and closing the receiver's descriptor does not release the resource while other references remain.
- **Authority transfer:** A received descriptor lets the receiver operate on the resource with the access represented by that already-open handle. The receiver must treat it as a capability: validate the protocol that supplied it and close it when it is no longer needed or before an unrelated program inherits it across `exec()`.

> [!example] NGINX Process-Channel Topology
> A newly forked NGINX worker inherits descriptors that were already open before its [`fork()`](05%20Process%20Management.md#POSIX%20Process-Control%20Interface). An already-running worker cannot inherit a descriptor for a socket pair created later. The [NGINX master](../Technologies/NGINX/02%20NGINX%20Internals.md#Master%20Process%20and%20Worker%20Control) therefore passes the new process-channel descriptor to existing workers with `SCM_RIGHTS`, combining descriptor inheritance with explicit passing as its process topology changes.

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

An anonymous pipe is reached through descriptors that a process already holds. It is commonly created before `fork()` so related processes inherit references to the same kernel pipe state; [explicit descriptor passing](#Explicit%20Descriptor%20Passing) can also transfer an endpoint to another process.

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

An **addressed Unix-domain socket** provides a rendezvous mechanism. For a connection-oriented socket type, a server creates a socket, binds a [local Unix-domain address](07%20Socket%20Management.md#Binding), and begins listening. Independently started clients create their own sockets and connect through that address. The listening address remains a stable rendezvous point while each accepted connection has its own endpoint state.

With a pathname-based address, the pathname identifies where the peers meet; after connection establishment, application data flows through the resulting socket endpoints rather than through the pathname itself.

`socketpair()` solves a different problem. It creates two unnamed, already-connected socket endpoints in one operation. No `bind()`, `listen()`, `connect()`, or `accept()` rendezvous is required. The processes must instead receive those endpoint descriptors through an existing relationship, commonly [descriptor inheritance across `fork()`](05%20Process%20Management.md#POSIX%20Process-Control%20Interface) or [explicit descriptor passing](#Explicit%20Descriptor%20Passing).

A socket pair therefore provides the bidirectional channel that would otherwise require two oppositely directed pipes when each peer needs an independent byte stream. The mechanisms differ in how peers obtain their endpoints:

| Property | Addressed Unix-domain socket | `socketpair()` |
| --- | --- | --- |
| Peer rendezvous | Through a Unix-domain address | Not required |
| Independently started peers | Natural fit | Requires endpoint distribution |
| Connection setup | Address-based connection lifecycle | Endpoints created already connected |
| Filesystem pathname required | Only for pathname-based addressing | No |

> [!example] Docker Daemon and `/var/run/docker.sock`
> On Linux, Docker Engine uses `unix:///var/run/docker.sock` as its default local daemon endpoint. The pathname gives independently started clients such as the Docker CLI and other Engine API clients a stable address through which they can reach the same listener without receiving a descriptor in advance.
>
> This naturally supports a **one-listener-to-many-clients** service model. The listening socket remains the shared rendezvous point, while each successful `accept()` creates a separate connected socket for one client.
>
> A `socketpair()` would instead create one already-connected pair of endpoints. The daemon could create many socket pairs, but every future client would still need another mechanism to receive its endpoint descriptor. The addressed Unix-domain socket solves that discovery and distribution problem directly: clients know one stable address, connect when needed, and receive an independent connection to the daemon.
<!-- -->
> [!example] Node.js `child_process.fork()` IPC
> On Unix, [`child_process.fork()`](../Technologies/NodeJS/01%20Basics/04%20Internals.md#Child%20Processes%20and%20IPC) creates a parent-child IPC channel that libuv backs with a Unix-domain `SOCK_STREAM` socket pair. Because the parent creates the specific child and can distribute an endpoint during process creation, no stable address or listener is needed.
<!-- -->
> [!example] NGINX Master and Worker Control Channels
> [NGINX](../Technologies/NGINX/02%20NGINX%20Internals.md#Master%20Process%20and%20Worker%20Control) creates a Unix-domain `SOCK_STREAM` socket pair for each worker or helper process it spawns on Unix and uses the channel for internal process-control messages. The master manages many children by maintaining separate private pairs rather than exposing a rendezvous address for those relationships.

The way peers obtain their endpoints is separate from the socket's data model:

- **`SOCK_STREAM`:** Transfers an ordered byte stream and does not preserve individual write boundaries.
- **`SOCK_SEQPACKET`:** Transfers ordered records while preserving message boundaries, where the address family and operating system support it.

Both addressed Unix-domain sockets and socket pairs can use socket types supported by the platform. Addressability, directionality, and message-boundary semantics therefore describe separate properties of the channel.

[Socket management](07%20Socket%20Management.md#Sockets%20as%20Kernel%20Objects) provides the common descriptor-backed socket model; the address family and binding rules determine how an addressed local socket becomes discoverable.

## Stream Framing

A stream delivers bytes, not application messages. A receiver can obtain a partial message, several messages together, or data ending in the middle of an application-level field. The application protocol must therefore define how the receiver identifies each message's beginning and end.

### Frame Format

A common frame contains a message type, a payload length, and the payload. The type selects how the payload is interpreted, while the length lets the receiver determine how many bytes belong to that message before processing the next frame. A record-preserving transport such as `SOCK_SEQPACKET` supplies record boundaries, but the application still defines the meaning of each record.

### Incremental Frame Decoding

<!-- TODO: Explain the receiver state machine: retain unread bytes across reads; parse a complete fixed-size header; validate its type and declared payload length; wait only for the declared payload after validation; emit one frame; and retain any following bytes for the next frame. Contrast partial input, which is normal, with a completed invalid header. -->

### Invalid Frames and Resource Bounds

<!-- TODO: Explain that the application validates declared lengths before allocating or waiting indefinitely, defines frame-size, buffering, and progress limits, and treats malformed input as a protocol violation. State that a simple length-prefixed stream should be closed after malformed input unless its format provides a trustworthy resynchronization mechanism. Clarify that `SOCK_SEQPACKET` preserves record boundaries but does not validate record meaning or resource policy. -->

### Logical Channels and Endpoint Isolation

One connection can carry several logical message types when a framing protocol distinguishes them. Separate pipes or socket pairs instead isolate those channels through independent endpoints. The choice depends on whether independent endpoint lifetime and flow control are more valuable than one shared protocol and connection.

## Unix-Domain Sockets and Loopback TCP/IP

Unix-domain sockets and loopback Internet sockets both let local processes exchange data through kernel socket objects, but they use different addressing namespaces and protocol models. `AF_UNIX` selects local Unix-domain addressing. `AF_INET` and `AF_INET6` select IPv4 and IPv6 Internet-domain addressing, respectively; the socket type and protocol then determine whether the endpoint uses TCP, UDP, or another compatible transport.

An addressed Unix-domain socket uses a local Unix-domain address, commonly a pathname. Only processes on the same host can connect through that address, and the communication does not use IP or a transport protocol such as TCP. An Internet-domain listener instead uses an IP address and port. Binding it to the IPv4 loopback address `127.0.0.1` or the IPv6 loopback address `::1` restricts it to local traffic. `localhost` is commonly configured to resolve to one or both of those addresses.

Loopback traffic never traverses an Ethernet or Wi-Fi link to reach another machine, but it still follows the IP and selected transport-stack model. This makes a loopback TCP endpoint behave like a local instance of the same address, port, and transport model that a service can use for remote clients when it binds a non-loopback address.

- **Unix-domain socket:** Use when the communication is inherently host-local and a Unix-domain address is suitable for peer rendezvous.
- **Loopback TCP/IP:** Use when local participants need Internet-domain addressing or transport behavior that also applies to a networked deployment.

## Mechanism Selection

Select an IPC mechanism from the required communication shape rather than from the fact that all participants happen to run locally.

<!-- TODO: Refine this selection list in place. Distinguish a pipe's endpoint distribution through an existing relationship from a FIFO's pathname rendezvous; distinguish a socket pair's known peers from an addressed Unix-domain listener's independently started clients; and make the trade-off between one framed connection and separate endpoints explicit as independent lifetime, flow-control, and failure boundaries. Keep loopback TCP as a local use of an Internet-domain model that can also be deployed across hosts, not as cross-host IPC. -->

- **Pipe or FIFO:** A bounded, unidirectional byte stream is sufficient. Use two channels when both peers must send independent byte streams.
- **Socket pair:** Two known peers need an unnamed bidirectional socket channel.
- **Unix-domain socket:** Local clients need to rendezvous with a local service through a Unix-domain address.
- **Loopback TCP/IP:** Local participants need Internet-domain addressing or TCP behavior that is also usable across hosts.
- **Shared mapping:** Participants need access to the same data rather than a copied byte stream, and the design includes an explicit synchronization protocol.

The mechanism's data model does not replace an application protocol. Streams require framing, shared memory requires synchronization, and every design must define endpoint lifetime, failure handling, and backpressure behavior.
