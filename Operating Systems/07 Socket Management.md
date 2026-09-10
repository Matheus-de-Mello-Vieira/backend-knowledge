# Socket Management

Socket management is how an operating system exposes network communication to user-space programs. The kernel owns socket objects, integrates them with transport protocols such as TCP and UDP, receives incoming packets, maintains protocol and queue state, and decides when I/O can make progress. User-space programs interact with that machinery through descriptors, system calls, and kernel-managed buffers.

Socket management is fundamental to backend engineering because backend software exists behind an interface consumed by another component rather than being the user-facing interface itself. In distributed systems, those consumers are commonly remote clients, frontends, or other services, so communication crosses a network and reaches the application through the operating system's socket abstraction. Some backend components instead communicate through queues, files, pipes, shared memory, or standard input/output, but for networked backends socket behavior underlies concerns such as connection concurrency, buffering, backpressure, readiness, timeouts, and server scaling.

Unix-like systems commonly expose sockets through the [POSIX](01%20Why%20an%20OS.md#Software,%20Hardware,%20and%20POSIX) interface. Stream sockets commonly use [TCP](../Networking/02%20Protocols/05%20TCP.md) for ordered reliable transport, while datagram sockets commonly use [UDP](../Networking/02%20Protocols/04%20UDP.md) for message-orieblnted transport. Application servers compose listening sockets, connected sockets, descriptor sharing, and readiness mechanisms into [connection-distribution architectures](../Backend%20Engineering/Concurrency/02%20Application%20Server%20Concurrency.md#Connection%20Distribution%20Models).

## Sockets as Kernel Objects

Network sockets are one important kind of resource referenced through a [file descriptor](02%20The%20Anatomy%20of%20a%20Process.md#File%20Descriptors%20%28FDs%29). On Unix-like systems, the descriptor is a process-local handle rather than the network connection itself.

- **Descriptor Reference:** `socket()` returns an FD that refers through the process's descriptor machinery to kernel-maintained socket state.
- **Kernel-Owned State:** The underlying socket object can contain the socket type and protocol, local and remote addresses, ports, transport connection state, receive and send queues, socket options, and waiters interested in I/O readiness.
- **Normal Descriptor Rules:** Because the FD is only a handle, the usual descriptor-lifetime rules apply.
    - `dup()` can create another descriptor referring to the same open resource.
    - `fork()` can cause child processes to inherit references.
    - Threads in the same process naturally share the process's descriptor table.
- **Reference-Based Lifetime:** Closing one descriptor does not necessarily destroy the underlying socket immediately. If another descriptor still refers to the same open resource, the socket remains reachable through that reference.
    - This matters for inherited listening sockets, graceful shutdown, and descriptor leaks.
- **Finite Resources:** Sockets consume process and kernel resources. A process that continually creates sockets without closing descriptors it no longer needs can eventually hit its descriptor limit and receive errors such as `EMFILE`.

> [!example] Forked Server Workers
> A server can create and bind a listening socket before calling `fork()`. The child processes inherit descriptors referring to the same underlying listening resource, so several workers can call `accept()` on that listener. Closing the listener in one child does not remove the other inherited references.

## Socket Types

The socket API separates the application's I/O semantics from the transport protocol implementation. For Internet sockets, two important types are stream sockets and datagram sockets.

### Stream Sockets

- **Data Model:** A stream socket exposes an ordered byte stream.
- **Typical Internet Protocol:** With the Internet protocol family, stream sockets are commonly paired with [TCP](../Networking/02%20Protocols/05%20TCP.md).
- **Boundary Semantics:** The application writes bytes into the stream and reads bytes from it; boundaries between individual `send()` or `write()` calls are not preserved.
    - If one side writes 100 bytes and then another 100 bytes, the peer may read 50, then 120, then 30 bytes depending on buffering and timing.
- **Endpoint State:** TCP stream sockets normally become associated with both a local and remote endpoint.
- **Kernel Responsibility:** The application interacts with one connected socket while the kernel maintains the protocol state required to deliver the ordered stream.

### Datagram Sockets

- **Data Model:** A datagram socket preserves message boundaries.
- **Typical Internet Protocol:** With the Internet protocol family, datagram sockets are commonly paired with [UDP](../Networking/02%20Protocols/04%20UDP.md).
- **Boundary Semantics:** One `sendto()` operation produces one transport datagram, and one `recvfrom()` consumes one datagram while also allowing the application to learn which peer sent it.
- **Peer Model:** UDP does not require an `accept()` operation that creates a new socket for every remote peer.
    - A single bound datagram socket can receive messages from many different source addresses.
- **UDP `connect()`:** Applications can use `connect()` with UDP to set a default peer and restrict which peer is accepted.
    - This changes socket API state but does not create a TCP-style transport handshake.

## Addressing, Ports, and Demultiplexing

The kernel combines network- and transport-layer information to decide which socket should receive incoming traffic.

- **IP Address Role:** IP addresses identify network interfaces or hosts at the network layer.
- **Port Role:** Transport protocols add ports so multiple communication endpoints can coexist on the same host.
- **Kernel Demultiplexing:** The kernel combines protocol, address, port, and connection state to select the receiving socket.
    - Packets are therefore demultiplexed to kernel sockets first; applications reach those sockets through their descriptors.
- **TCP Connection Identity:** An established TCP connection is commonly described by the four-tuple `(source IP, source port, destination IP, destination port)`.
    - Many simultaneous TCP connections can share the same server port because their complete connection identities differ.
    - A listening socket is usually selected primarily by the local address and port, while established traffic can be matched against the full connection identity.
- **UDP Delivery:** UDP has no accepted socket per peer.
    - The kernel normally identifies the appropriate bound datagram socket using the protocol and local addressing information.
    - Exact matching rules can also depend on whether the socket has been connected and on configured socket options.

## POSIX Socket Interface

POSIX exposes socket-specific operations on top of the general file-descriptor model. Generic descriptor calls such as `read()`, `write()`, and `close()` can operate on sockets, while socket-specific calls expose operations and metadata that do not make sense for ordinary files.

### Creating a Socket

- **`socket()` — Create Kernel State:** `socket()` asks the kernel to create a socket object and returns a descriptor referring to it.
- **Address Family:** The call specifies an address family such as IPv4 or IPv6.
- **Socket Type:** It specifies a type such as `SOCK_STREAM` or `SOCK_DGRAM`.
- **Protocol Selection:** A protocol can be supplied when the family/type pair does not already imply one.
- **Initial State:** Creating the socket establishes the kernel object but does not by itself choose a local endpoint or establish a remote connection.

### Binding and Local Endpoints

- **`bind()` — Associate Local Endpoint:** `bind()` associates a socket with a local address.
- **Server Use:** A server commonly binds explicitly because clients need a stable destination.
- **Client Use:** A client can often let the kernel choose an ephemeral local port automatically when communication begins.
- **Specific Address:** Binding to a specific local IP restricts the socket to traffic addressed to that interface or address.
- **Wildcard Address:** A wildcard such as `0.0.0.0` on IPv4 asks the kernel to accept traffic for the chosen port on all suitable local IPv4 interfaces. This expands the local addresses through which the process can receive traffic; it does not by itself make the service reachable from another network or from the Internet.
    - Actual reachability also depends on address assignment and routing, network address translation or other ingress controls, and [firewall policy](../Security/05%20Architecture%20and%20Infrastructure%20Security/Network%20Security/01%20Network%20Security.md#Service%20Listening%20Scope%20and%20Network%20Reachability).
    - A wildcard listener can nevertheless expose a service through an interface that was not intended to serve it, such as an internal or management network. Binding to a specific address, including a loopback address when only local clients should connect, narrows that local acceptance scope as defense in depth.
    - `0.0.0.0` is an IPv4 wildcard. IPv6 uses a separate wildcard address, `::`; whether an IPv6 listener also accepts IPv4 traffic is platform- and socket-option-dependent.
- **Binding Conflicts:** Whether multiple sockets may bind overlapping addresses depends on the socket type, current state, operating system, and socket options.

### Establishing Outbound Connections

`connect()` associates a socket with a remote endpoint, but its transport meaning depends on the socket type.

- **TCP `connect()`:** For a TCP stream socket, `connect()` initiates connection establishment.
    - **Blocking Socket:** The call normally waits until the connection succeeds or fails.
    - **Non-Blocking Socket:** Establishment can continue asynchronously and later become observable through readiness or error state.
    - **Kernel Handshake:** The kernel performs the TCP handshake rather than requiring user space to exchange handshake packets manually.
- **UDP `connect()`:** For UDP, `connect()` does not perform a transport handshake.
    - It records a default remote peer in the socket state.
    - It can restrict received datagrams to that peer.
    - Calls such as `send()` and `recv()` can then omit explicit peer addresses.

### Listening and Accepting

A TCP server commonly follows this lifecycle:

1. `socket()` creates the socket-backed descriptor.
2. `bind()` associates the socket with a local address and port.
3. `listen()` changes the socket into a passive listening socket.
4. The kernel receives connection-establishment packets and performs the TCP handshake.
5. Completed connections wait until the application is ready to claim them.
6. `accept()` returns a descriptor referring to a new connected socket.

During TCP's [three-way handshake](../Networking/03%20Connections/01%20How%20Connections%20are%20Established.md#TCP%20Three-Way%20Handshake), the kernel processes the `SYN`, generates the `SYN-ACK`, and interprets the final `ACK`. User space receives the completed connection through `accept()` rather than constructing or consuming those handshake packets itself.

#### Listening Socket vs. Connected Socket

- **Listening Socket:** The listener is a persistent passive endpoint that remains available for future arrivals.
- **`accept()` Result:** Calling `accept()` does not transform the listening socket into a client connection. The kernel instead returns another descriptor referring to a connected socket dedicated to the established connection.
- **One-to-Many Relationship:** A server can have one listening socket and thousands of connected sockets at the same time.
- **Independent Connection State:** Each connected socket has its own transport state and I/O queues even though the connections originally arrived through the same listener.

#### Pending and Established Connection Queues

The kernel needs somewhere to keep connection state while handshakes and application acceptance proceed at different speeds.

- **Incomplete Establishment State:** The kernel retains state for connections whose transport handshake has not yet completed.
- **Completed Connections:** Fully established connections can wait until the application calls `accept()`.
- **Linux Terminology:** On Linux this is commonly discussed as a **SYN queue** for incomplete handshakes and an **accept queue** for completed connections.
- **Listen Backlog:** The backlog supplied to `listen()` influences how much completed connection work can wait for the application.
- **Queue Saturation:** If the application accepts connections too slowly, queues can saturate and the kernel eventually has to delay, drop, reset, or otherwise refuse additional connection work according to its implementation and configuration.

> [!note] Queue Structures Are OS-Specific
> Other operating systems and kernel versions may implement and size incomplete and completed connection state differently. The SYN-queue / accept-queue model is therefore a useful conceptual description rather than a universal data-structure contract, and the exact interpretation and limiting behavior of `listen()` backlog are OS-specific.

#### Blocking `accept()`

- **Blocking Listener:** If no completed connection is available, `accept()` waits. The kernel marks the calling thread as sleeping and can wake it when a connection becomes ready.
- **Non-Blocking Listener:** `accept()` returns immediately when there is nothing to accept, typically with `EAGAIN` or `EWOULDBLOCK` on Unix-like systems.

### Data Transfer

Sockets participate in the common descriptor interface, but socket-specific calls expose networking-specific behavior.

- **Generic Descriptor I/O:** `read()` and `write()` can operate on sockets.
- **`send()` / `recv()`:** Operate on an already-associated peer while accepting socket-specific flags.
- **`sendto()` / `recvfrom()`:** Additionally carry peer addressing information, which is especially important for connectionless datagram sockets.
- **Descriptor vs. Socket Semantics:** Generic descriptor operations provide common I/O primitives, while socket-specific operations expose peer addressing and networking state that ordinary files do not have.

### Socket Configuration

- **`getsockopt()` / `setsockopt()`:** Read and modify options associated with a socket or its protocol stack.
- **Configurable Concerns:** Options can control address reuse, buffer sizing, keepalive behavior, or protocol-specific algorithms.
- **Examples:** `SO_REUSEADDR`, `SO_REUSEPORT`, receive/send buffer options, and TCP-specific options such as `TCP_NODELAY`.
- **Transport Effect:** `setsockopt()` can change protocol-stack behavior; for example, [`TCP_NODELAY`](../Networking/03%20Connections/02%20Reading%20and%20Sending%20Data.md#%60TCP_NODELAY%60) disables Nagle's algorithm for a TCP socket.

### Shutdown and Descriptor Closure

`shutdown()` and `close()` operate at different abstraction layers.

- **`shutdown()` — Communication State:** Changes a connected socket's communication state, allowing reads, writes, or both directions to be disabled while the descriptor remains open.
- **`close()` — Descriptor Lifetime:** Releases that descriptor's reference according to the general [descriptor lifetime](02%20The%20Anatomy%20of%20a%20Process.md#Descriptor%20Operations%20and%20Lifetime) rules.
- **TCP Termination:** For TCP, orderly or abortive closure can produce transport-state transitions involving `FIN` or `RST`.

## Listener, Acceptor, and Worker Roles

Three roles are useful when describing how application servers interact with TCP sockets:

- **Listener:** Owns or refers to the listening socket that receives incoming connection attempts.
- **Acceptor:** Calls `accept()` and obtains connected sockets from the kernel.
- **Worker:** Reads requests, performs application work, and writes responses through connected sockets.

These are conceptual roles, not requirements for separate threads or processes. A single execution unit can perform all three, one acceptor can distribute connections to many workers, or many workers can accept directly. These roles can be combined in several [application-server concurrency models](../Backend%20Engineering/Concurrency/02%20Application%20Server%20Concurrency.md#Connection%20Distribution%20Models), including a single acceptor feeding multiple workers or several workers accepting directly.

## User–Kernel Data Transfer

Socket I/O normally invokes the kernel through `read()`/`recv()` or `write()`/`send()`. The kernel copies payload bytes between application memory and kernel-managed socket buffers. Frequent small I/O operations add system-call overhead, while copying larger payloads also consumes CPU time and memory bandwidth. The direction of the copy depends on whether the application is receiving or sending.

## Receiving Data

Once incoming network data is associated with a socket, the kernel processes the relevant transport protocol and makes application data available in the socket's receive state.

- **Kernel Receive State:** The kernel retains application data until user space consumes it.
- **Application Operation:** `read()`, `recv()`, or `recvfrom()` moves available data into user-space memory.
- **Stream Semantics:** For a stream socket, one read is not tied to one packet or one peer write.
    - `recv()` may return fewer bytes than requested even though the connection remains open.
    - Applications must treat TCP as a stream and continue reading until their own application-level framing says that a complete message has arrived.
- **Blocking Behavior:** On a blocking socket, a read that cannot currently return useful data sleeps the calling thread until the operation can make progress.
    - It does not inherently pause every thread in the process.
- **Non-Blocking Behavior:** On a non-blocking socket, the call returns immediately instead of sleeping for data.
- **TCP End-of-Stream:** An orderly peer shutdown eventually appears as end-of-stream.
    - After already-buffered bytes have been consumed, a read returns zero bytes.
    - The socket API surfaces [TCP](../Networking/02%20Protocols/05%20TCP.md) closure transitions such as `FIN` and `RST` as application-visible end-of-stream or error conditions.

## Sending Data

- **Application Submission:** `write()` or `send()` asks the kernel to accept application bytes for transmission through a socket.
- **Kernel Ownership:** The data generally moves from user-space memory into kernel-managed networking state, after which the transport protocol and network stack decide how and when it is transmitted.
- **Success Semantics:** A successful `send()` does **not** mean that the remote application has received or processed the bytes.
    - It normally means that the local kernel accepted some amount of data from the application.
- **Partial Writes:** Stream-socket writes can be partial, so code must use the returned byte count rather than assuming the whole requested buffer was accepted.
- **Cross-Resource Transfer:** Some operating systems provide specialized operations such as Linux [`sendfile()`](02%20The%20Anatomy%20of%20a%20Process.md#Resource-Specific%20Operations), which can move regular-file data toward a socket without first routing the payload through an application buffer.
    - The socket remains the network destination.
    - The [avoided user-space copy](03%20Memory%20Management.md#Direct%20Memory%20Access%20%28DMA%29) reduces data movement through application memory.
- **TCP Processing:** Once bytes enter a TCP socket, [TCP](../Networking/02%20Protocols/05%20TCP.md) handles segmentation, acknowledgments, retransmissions, flow control, congestion control, and algorithms such as [Nagle's algorithm](../Networking/03%20Connections/02%20Reading%20and%20Sending%20Data.md#Nagle's%20Algorithm).

## Socket Buffers and Backpressure

Sockets separate application execution from network timing with finite kernel-managed buffering and queueing.

- **Receive Buffer:** Retains data that has arrived from the network but has not yet been consumed by the application.
- **Send-Side State:** Retains data the application has submitted but that has not yet progressed far enough through the transport stack to be discarded.
- **Slow Reader:** If an application reads too slowly, receive-side pressure grows.
    - For TCP, this pressure participates in flow control because the receiver cannot advertise unlimited capacity to its peer.
- **Fast Writer:** If the local application writes faster than the kernel and peer can drain outgoing data, send-side capacity fills.
    - A blocking `send()` may sleep.
    - A non-blocking call can return `EAGAIN` or `EWOULDBLOCK`.
- **Backpressure:** Inability to make progress at one stage eventually becomes visible to the previous stage instead of allowing memory usage to grow without bound.
- **Memory Consequence:** Every active socket consumes kernel state and potentially buffer memory, so very large connection counts are also a memory-management concern.

> [!example] Inspecting Socket Queues with `ss`
> On Linux, `ss` exposes parts of the kernel's socket state. Its [operational interpretation](../Backend%20Engineering/03%20Troubleshooting%20Performance.md) depends on socket state: for an established TCP socket, `Recv-Q` can show data waiting for the application to read, while `Send-Q` can show data that has not yet completed the relevant send/acknowledgment progress; for a listening socket, the same columns describe listening/backlog state instead.

## Blocking and Non-Blocking Sockets

- **Blocking Mode:** The kernel suspends the calling thread when an operation cannot currently make useful progress.
    - Examples include `accept()` with no completed connection, `recv()` with no available data, or `send()` when local send capacity is exhausted.
- **Non-Blocking Mode:** The system call returns immediately when progress is unavailable, commonly through `EAGAIN` or `EWOULDBLOCK`.
    - The application can do other work and retry later.
- **Busy-Retry Cost:** Repeatedly retrying every socket in a busy loop wastes CPU.
- **Coordination Choice:** High-concurrency applications avoid busy retry by coordinating outstanding socket work through either readiness notification or completion notification.

## Asynchronous Socket I/O

Asynchronous socket I/O keeps application threads available while network operations wait for progress. It does not eliminate socket buffers, partial transfers, or backpressure; it changes how user space learns that an operation can proceed or has finished. The two main coordination models are readiness-based I/O and completion-based I/O.

> [!note] Event Loop
> An **event loop** is a programming design pattern and control-flow algorithm that repeatedly waits for events, dispatches the work associated with each event, and then waits again. It appears in many forms, including socket-I/O servers that dispatch readiness or completion events and Node.js, which dispatches callbacks scheduled from I/O, timers, and other event sources.
>
### Readiness-Based I/O

The kernel already knows whether a socket currently has data to read, room to accept writes, a completed connection to accept, or an error condition. Readiness interfaces expose changes in that state across many descriptors without requiring one blocked OS thread per connection.

- **Purpose:** User space registers interest in many descriptors and waits for readiness. The wait can block the event-loop thread while none of those descriptors can make progress, but it is one shared wait rather than one blocked thread per socket. When the kernel reports one or more ready descriptors, the thread performs the actual I/O system calls on them.
- **POSIX Interfaces:** `select()` and `poll()` provide descriptor-readiness waiting through portable POSIX interfaces.
- **OS-Specific Scalable Interfaces:** Operating systems also provide implementation-specific facilities with different registration and wakeup semantics.
    - **Linux:** `epoll`.
    - **BSD-Derived Systems:** `kqueue`.
- **Readiness Is Not Transfer:** A readiness notification does not move application data by itself.
    - For example, `epoll_wait()` can report that a socket is readable, but the application still calls `read()` or `recv()` to consume the bytes.
- **Readiness Can Become Stale:** Races and edge-triggered modes mean a supposedly ready operation must still handle cases where no progress is available by the time the application acts.

#### `select()` Readiness Cycle

An event loop can use `select()`, which accepts up to three `fd_set` collections:

- **`readfds`:** Descriptors to watch for readable state.
- **`writefds`:** Descriptors to watch for writable state.
- **`exceptfds`:** Descriptors to watch for exceptional conditions.

Each collection can contain many file descriptors, and a caller can omit categories it does not need. The call is a blocking readiness wait when given a positive timeout or no timeout; a zero timeout makes it return immediately and is therefore a polling use of the interface.

- **Build Sets:** The event loop builds each needed `fd_set` collection with the descriptors it wants the kernel to monitor.
- **Wait:** It calls `select()` with those sets and a timeout. The call returns when one or more descriptors become ready, the timeout expires, or the wait is interrupted.
- **Inspect Results:** `select()` modifies each supplied set so it retains only the ready descriptors. `FD_ISSET(fd, &set)` tests whether one specific descriptor remains in a returned set, and therefore whether it is ready for that set's operation category. The test does not transfer data or report a byte count.
- **Perform I/O:** The event loop calls `read()`, `write()`, `accept()`, or another appropriate I/O operation on each ready descriptor.

##### Example: `select()` with One Listener and One Client

The following C-like pseudocode uses one listening socket and one already-connected client socket.

- **Resources and State:**
    - `listener_fd`: File descriptor for an already-created, bound, and listening socket.
    - `client_fd`: File descriptor for one already-connected client socket.
    - `readfds`: `fd_set` containing the descriptors that the current `select()` call should monitor for read readiness.
    - `watched_client_fd`: Copy of the client descriptor included in the current `readfds` set.
    - `max_fd`: Highest-numbered descriptor currently being watched.
    - `buffer`: User-space memory where bytes read from the client socket are stored.

**Build the Interest Set:** Each event-loop iteration creates a fresh `readfds` set. `FD_ZERO()` clears the set, and `FD_SET()` adds the listener and client descriptors.
- Unlike `epoll`, `select()` does not preserve this interest state across waits. Because `select()` modifies the supplied sets to contain only ready descriptors, the process must rebuild the complete interest set before every call.
- `watched_client_fd` preserves the client descriptor included in this particular wait. This matters because accepting another connection later in the iteration can replace `client_fd`.
- `max_fd` records the highest descriptor being monitored because `select()` uses `nfds` as an exclusive upper bound over the descriptor-number range it must inspect.

```c
for (;;) {
    fd_set readfds;
    FD_ZERO(&readfds);

    FD_SET(listener_fd, &readfds);
    FD_SET(client_fd, &readfds);

    int watched_client_fd = client_fd;
    int max_fd =
        listener_fd > watched_client_fd
            ? listener_fd
            : watched_client_fd;
```

**Wait for Readiness:** The process calls `select()` with `readfds`.
- The first argument is `max_fd + 1`, so the kernel considers descriptor numbers from `0` through `max_fd`. The `NULL` write and exception sets mean that this example monitors only read readiness, while the `NULL` timeout makes the call wait indefinitely until a descriptor becomes ready or the wait is interrupted.
- When `select()` returns successfully, `ready` reports how many readiness conditions were found. More importantly, `readfds` has been modified so that only descriptors currently reported as readable remain in the set.

```c
    int ready = select(
        max_fd + 1,
        &readfds,
        NULL,
        NULL,
        NULL
    );

    if (ready < 0) {
        handle_select_error();
        continue;
    }
```

**Inspect and Act on Client Readiness:** `FD_ISSET()` checks whether `watched_client_fd` remains in the returned `readfds` set.
- If it does, the client socket was reported as read-ready. The readiness notification itself did not transfer any bytes, so the process then calls `read()` to perform the actual I/O and copy available bytes into `buffer`.

```c
    if (FD_ISSET(watched_client_fd, &readfds)) {
        ssize_t bytes =
            read(watched_client_fd, buffer, sizeof(buffer));

        handle_client_bytes(bytes, buffer);
    }
```

**Inspect and Act on Listener Readiness:** The process separately checks whether `listener_fd` remains in `readfds`.
- If it does, the listening socket has read-related readiness, normally meaning that a completed connection can be accepted. `accept()` performs the actual operation and returns a descriptor for the newly connected socket.
- The example stores that descriptor in `client_fd`, so the next loop iteration rebuilds `readfds` using the newly accepted client.

```c
    if (FD_ISSET(listener_fd, &readfds)) {
        client_fd = accept(listener_fd, NULL, NULL);
    }
}
```

**Omitted Production State Transitions:** The example deliberately tracks only one connected client at a time. A real `select()`-based server would normally maintain a collection of active client descriptors, add newly accepted clients to that collection, remove closed connections, calculate the current highest descriptor, inspect all relevant returned descriptors, use non-blocking sockets where appropriate, handle `EAGAIN` or `EWOULDBLOCK`, process partial reads and writes, and preserve per-connection application state across iterations.

##### Benefits and Limits of `select()`

- **Avoiding Unproductive I/O:** `select()` lets the process wait until an operation is likely to make progress instead of repeatedly trying reads, writes, or accepts on unready descriptors.
- **I/O Concurrency:** One event-loop thread can coordinate readiness for many descriptors. The thread may block inside `select()` while nothing is ready, but it does not need one blocked thread per descriptor.
- **Linear Scanning:** After `select()` returns, the process typically tests descriptors with `FD_ISSET()` across the range from `0` through `nfds - 1`. This work grows linearly with that range, including unused descriptor numbers below the highest watched descriptor.
    - **Application-Side Optimization:** The process can maintain a collection of the descriptors it actually registered and call `FD_ISSET()` only for those after `select()` returns. This avoids user-space checks for unused numeric gaps, but it does not reduce `select()`'s own worst-case O(`nfds`) range-dependent work.
- **Set Transfer and Rebuilding:** Each call passes descriptor sets to the kernel and receives modified sets back. The process must also rebuild those sets before the next call, adding overhead as the watched range grows.
- **Descriptor-Set Capacity:** An `fd_set` has an implementation-defined capacity, commonly exposed as `FD_SETSIZE`. A process cannot use `select()` with descriptors outside that set's supported range.

#### `epoll` Readiness Cycle

Linux `epoll` implements the same readiness-based I/O model as `select()`, but changes how the set of watched descriptors is maintained and how ready descriptors are returned. Instead of supplying the complete descriptor set on every wait, an event loop creates an **epoll instance**, registers descriptors with it, and then repeatedly asks the kernel for events from descriptors that have become ready.

Conceptually, an epoll instance maintains two kinds of state:

- **Interest List:** The descriptors and event types that the application has registered for monitoring.
- **Ready List:** References to registered descriptors for which the kernel has detected relevant readiness events.

The event loop interacts with this state through three main operations:

- **Create:** `epoll_create1()` creates an epoll instance and returns a file descriptor referring to it.
- **Register or Modify Interest:** `epoll_ctl()` adds, modifies, or removes descriptors from the interest list.
    - `EPOLL_CTL_ADD` registers a descriptor.
    - `EPOLL_CTL_MOD` changes its registered events.
    - `EPOLL_CTL_DEL` removes it.
    - `EPOLLIN` expresses interest in read-related readiness. For a connected socket, this can mean that `read()` or `recv()` may return bytes; for a listening socket, it normally means that `accept()` can claim a completed connection. It can also accompany end-of-stream, so the application must inspect the I/O result.
    - `EPOLLOUT` expresses interest in write-related readiness. For a connected socket, this usually means that `write()` or `send()` may accept at least some bytes because send-buffer capacity is available; it does not guarantee that one call can write a complete application message.
- **Wait:** `epoll_wait()` waits until registered descriptors have readiness events, a timeout expires, or the wait is interrupted.
    - Instead of modifying the application's complete interest set, it writes ready events into an output array supplied by the application.
    - The return value tells the application how many entries in that array contain events.
- **Perform I/O:** The process inspects those returned events and calls `read()`, `write()`, `accept()`, or another appropriate operation on the corresponding descriptors.

Unlike `select()`, descriptors normally remain registered across calls to `epoll_wait()`. The application therefore does not need to rebuild and transfer its complete watched set before every wait.

##### Example: `epoll` with One Listener and One Client

The following C-like pseudocode uses one listening socket and one already-connected client socket.

- **Resources and State:**
    - `listener_fd`: File descriptor for an already-created, bound, and listening socket.
    - `client_fd`: File descriptor for one already-connected client socket.
    - `epoll_fd`: File descriptor referring to the epoll instance that stores the application's registered interests.
    - `event`: Temporary `epoll_event` structure used when registering one descriptor.
    - `events`: Array where `epoll_wait()` writes readiness events returned by the kernel.
    - `MAX_EVENTS`: Maximum number of events returned into `events` by one wait.
    - `buffer`: User-space memory where bytes read from the client socket are stored.

**Build Persistent Interest State:** The process first creates an epoll instance. It then registers both the listener and the connected client for `EPOLLIN`.
- Registering `listener_fd` asks the kernel to report read-related readiness on the listening socket, normally meaning that a connection can be accepted.
- Registering `client_fd` asks the kernel to report read-related readiness on the connected socket, such as available bytes or end-of-stream.
- These registrations persist in the epoll instance, so the process does not rebuild the complete interest set before every wait.

```c
int epoll_fd = epoll_create1(0);

struct epoll_event event;

event.events = EPOLLIN;
event.data.fd = listener_fd;
epoll_ctl(epoll_fd, EPOLL_CTL_ADD, listener_fd, &event);

event.events = EPOLLIN;
event.data.fd = client_fd;
epoll_ctl(epoll_fd, EPOLL_CTL_ADD, client_fd, &event);
```

**Wait for Readiness:** Each loop iteration allocates an output array and calls `epoll_wait()`.
- `events` is where the kernel writes the ready events
- `MAX_EVENTS` limits how many can be returned in one call.
- A timeout of `-1` means that the call waits indefinitely until an event becomes available or the wait fails.
- The return value `ready` is the number of valid entries written into `events`.

```c
for (;;) {
    struct epoll_event events[MAX_EVENTS];

    int ready = epoll_wait(
        epoll_fd,
        events,
        MAX_EVENTS,
        -1
    );

    if (ready < 0) {
        handle_epoll_error();
        continue;
    }
```

**Inspect the Result:** After a successful wait, the process iterates only over the entries that the kernel returned.
- `events[i].data.fd` recovers the descriptor associated with each readiness event.
- Unlike `select()`, the process does not need to inspect the whole registered descriptor set or scan up to the highest descriptor number.

```c
    for (int i = 0; i < ready; i++) {
        int fd = events[i].data.fd;
```

**Act on Client Readiness:** If the ready descriptor is `client_fd`, the process calls `read()`.
- The readiness notification itself did not transfer any bytes. `read()` performs the actual I/O, copying available data into `buffer`, and `handle_client_bytes()` processes the result.

```c
        if (fd == client_fd) {
            ssize_t bytes = read(fd, buffer, sizeof(buffer));
            handle_client_bytes(bytes, buffer);
        }
```

**Act on Listener Readiness:** If the ready descriptor is `listener_fd`, the process calls `accept()`.
- The listener readiness indicates that connection state is available to accept.
- `accept()` performs the actual operation and returns `new_client_fd`, a descriptor referring to the newly connected socket.
    - That new descriptor is not automatically registered with this epoll instance; production code would normally register it separately before expecting `epoll_wait()` to report its readiness.

```c
        if (fd == listener_fd) {
            int new_client_fd = accept(listener_fd, NULL, NULL);
            handle_new_client(new_client_fd);
        }
    }
}
```

**Omitted Production State Transitions:** The example focuses only on the readiness cycle. A real server would normally make sockets non-blocking, register each accepted client with `epoll_ctl()`, remove closed descriptors, inspect individual event flags, handle `EAGAIN` or `EWOULDBLOCK`, process partial reads and writes, and preserve per-connection application state across event-loop iterations.

##### Level-Triggered and Edge-Triggered Readiness

`epoll` supports two notification policies for readiness. In both modes, an event means that an operation may make progress; the application still calls `read()`, `write()`, `accept()`, or another I/O operation to perform the work.

- **Level-Triggered Mode:** This is the default. `epoll_wait()` can continue reporting a descriptor while it satisfies a registered condition.
    - A socket with unread bytes in its receive buffer can therefore remain readable across several waits.
- **Edge-Triggered Mode (`EPOLLET`):** The kernel reports a transition into readiness rather than repeatedly reporting the same ready state.
    - If arriving data makes a socket readable, the application receives an event. Unread data does not by itself guarantee another event on a later wait.
    - The application normally uses non-blocking descriptors and continues the relevant operation until it returns `EAGAIN` or `EWOULDBLOCK`. This indicates that the operation cannot currently make progress, so the application can return to `epoll_wait()` and wait for a new transition.
    - This can reduce repeated notifications, but the application must drain available work and preserve enough connection state to resume later. Stopping too early can leave data waiting indefinitely when no further readiness transition occurs.

##### Benefits and Limits of `epoll`

- **Persistent Registration:** The kernel retains the watched descriptors and their event interests across calls to `epoll_wait()`. The application does not rebuild and transfer its complete interest set on every iteration as it does with `select()`.
- **Ready-Event Delivery:** `epoll_wait()` returns only the events that are ready rather than requiring the application to inspect every descriptor below a numeric upper bound.
    - Application-side event processing therefore tends to grow with the number of returned events, not with the highest registered descriptor number.
- **Large Descriptor Sets:** `epoll` avoids the `fd_set` capacity restriction associated with `select()` and is intended for large sets of watched descriptors.
- **Registration and Memory Costs:** Persistent registration still requires kernel-maintained state. Adding, changing, and removing interests uses `epoll_ctl()`, and every registered descriptor consumes kernel resources.
    - Very large interest sets can therefore encounter memory costs and system-configured limits.
- **Readiness Is Not I/O:** `EPOLLIN` and `EPOLLOUT` indicate that an operation may make progress; they do not mean the operation has already completed.
    - The application still calls `accept()`, `read()`, `write()`, or another appropriate operation.
    - It must handle partial progress, closure, errors, and cases where the operation no longer makes progress by the time it runs.
- **Edge-Triggered Complexity:** `EPOLLET` can reduce repeated reports for continuing readiness, but it requires the application to drain non-blocking I/O until `EAGAIN` or `EWOULDBLOCK` and retain enough state to resume later.
- **Linux-Specific Interface:** `epoll` is a Linux API, not a portable POSIX readiness interface. Other operating systems provide mechanisms with similar goals, including `kqueue` on BSD-derived systems.

#### `kqueue` Readiness Cycle

`kqueue` is a scalable event-notification mechanism on BSD-derived systems. Like `epoll`, it keeps registrations in the kernel, so an event loop can wait for ready work without rebuilding its complete interest set on every iteration.

- **Filter-Based Model:** A registration combines an identified resource with a `filter` that defines the condition being observed.
- **Broader Scope:** Socket readiness is only one kind of event that a kqueue can monitor.

Socket I/O commonly uses the following filters:

- **`EVFILT_READ`:** Reports read-related readiness.
    - For a listening socket, it indicates that a connection is pending and is available to accept.
    - For a connected socket, it indicates that a read may make progress, such as by returning buffered data or observing end-of-stream.
    - The returned `data` field can provide additional filter-specific information, such as the amount of readable socket data.
- **`EVFILT_WRITE`:** Reports write-related readiness.
    - For a connected socket, it indicates that writing can currently make progress.
    - The returned `data` field can describe available write-buffer space.
- **Event State:** Returned events can carry additional state. For example, `EV_EOF` can report that a socket has shut down, while any already-buffered bytes may still need to be read.

The event loop interacts with `kqueue` through `kqueue()` and `kevent()`:

- **Create:** `kqueue()` creates a kernel event queue and returns a file descriptor referring to it.
- **Describe an Event:** A `struct kevent` identifies the resource through `ident`, selects a `filter`, and carries `flags` and application-associated state.
    - `EV_SET()` is commonly used to populate the structure.
- **Register or Change Interest:** `kevent()` receives a `changelist`—an array of `struct kevent` entries—that describes updates to persistent registrations.
    - `EV_ADD` adds an event or updates an existing matching event.
    - `EV_DELETE` removes an event.
    - `EV_ENABLE` and `EV_DISABLE` temporarily control whether an event can be delivered.
- **Wait for Events:** `kevent()` also receives an `eventlist`, an output array where the kernel records triggered events.
    - Its return value is the number of valid entries written into the `eventlist`.
    - A single call can submit a `changelist` and retrieve events, though event loops commonly apply registration changes separately from repeated waits.
- **Perform I/O:** A delivered event reports a condition, not a completed transfer. The application still calls `accept()`, `read()`, `write()`, or another appropriate operation to make progress.

Registrations normally remain until they are deleted or their configured lifetime semantics remove them.

##### Example: `kqueue` with One Listener and One Client

The following C-like pseudocode uses one listening socket and one already-connected client socket.

- **Resources and State:**
    - `listener_fd`: File descriptor for an already-created, bound, and listening socket.
    - `client_fd`: File descriptor for one already-connected client socket.
    - `kqueue_fd`: File descriptor referring to the kernel kqueue.
    - `changes`: Array of `kevent` structures describing events to register.
    - `events`: Array where `kevent()` writes triggered events returned by the kernel.
    - `MAX_EVENTS`: Maximum number of events returned into `events` by one wait.
    - `buffer`: User-space memory where bytes read from the client socket are stored.

**Register Read Interests:** The process creates a `kqueue` and prepares two persistent `EVFILT_READ` registrations with `EV_SET()`.

- `listener_fd` is registered so the kernel can report connections ready to accept.
- `client_fd` is registered so the kernel can report data ready to read.
- `EV_ADD` makes both registrations persistent.
- This `kevent()` call supplies `changes` as the `changelist` and no `eventlist` because it only updates registrations.

```c
int kqueue_fd = kqueue();

struct kevent changes[2];

EV_SET(
    &changes[0],
    listener_fd,
    EVFILT_READ,
    EV_ADD,
    0,
    0,
    NULL
);

EV_SET(
    &changes[1],
    client_fd,
    EVFILT_READ,
    EV_ADD,
    0,
    0,
    NULL
);

kevent(
    kqueue_fd,
    changes,
    2,
    NULL,
    0,
    NULL
);
```

**Wait for Ready Work:** Each iteration calls `kevent()` without a `changelist`, leaving the registered interests unchanged.

- The kernel writes at most `MAX_EVENTS` triggered events into `events`.
- A `NULL` timeout waits until an event is available or the wait fails.
- The return value, `ready`, is the number of valid entries to process.

```c
for (;;) {
    struct kevent events[MAX_EVENTS];

    int ready = kevent(
        kqueue_fd,
        NULL,
        0,
        events,
        MAX_EVENTS,
        NULL
    );

    if (ready < 0) {
        handle_kqueue_error();
        continue;
    }
```

**Inspect Each Event:** After a successful wait, the process iterates only over the returned entries.

- `events[i].ident` identifies the resource, which is the socket descriptor for these registrations.
- `events[i].filter` identifies the triggered filter.
- `flags`, `fflags`, and `data` carry filter-specific state.
- Because both registrations use `EVFILT_READ`, the descriptor distinguishes the listener from the connected client here.

```c
    for (int i = 0; i < ready; i++) {
        int fd = events[i].ident;
```

**Read the Client Socket:** When the event identifies `client_fd`, `EVFILT_READ` says that reading may make progress.

- The notification does not transfer application bytes; `read()` copies available bytes into `buffer`.
- Production code must also inspect state such as `flags`, because `EV_EOF` can accompany data that remains readable.

```c
        if (fd == client_fd) {
            ssize_t bytes = read(fd, buffer, sizeof(buffer));
            handle_client_bytes(bytes, buffer);
        }
```

**Accept a Pending Connection:** When the event identifies `listener_fd`, `EVFILT_READ` says that a completed connection is available to accept.

- `accept()` creates `new_client_fd`, a descriptor for that connected socket.
- The new descriptor has no `kqueue` registration automatically, so production code must submit a new `struct kevent` entry before later waits can report its readiness.

```c
        if (fd == listener_fd) {
            int new_client_fd = accept(listener_fd, NULL, NULL);
            handle_new_client(new_client_fd);
        }
    }
}
```

**Omitted Production State Transitions:** The example focuses only on the readiness cycle. A real `kqueue`-based server would normally make sockets non-blocking, register each accepted client with `EV_ADD`, delete registrations for closed descriptors with `EV_DELETE`, inspect individual event flags, handle `EAGAIN` or `EWOULDBLOCK`, process partial reads and writes, and preserve per-connection application state across event-loop iterations.

##### Persistent and Transition-Oriented Delivery

A registered `kevent` normally remains associated with its `kqueue` across waits. Its `filter` and `flags` determine whether the event loop continues to see a condition or instead waits for a later transition.

- **Condition-Based Delivery:** Read and write filters normally continue to represent the underlying condition. A socket that remains readable can therefore continue to produce read events.
- **`EV_CLEAR`:** Clears an event's recorded state after delivery, so later delivery depends on a subsequent change. With socket I/O, this style generally requires non-blocking descriptors and draining the available work before returning to the wait.
- **`EV_ONESHOT`:** Removes the registration after its first delivered event.
- **`EV_DISPATCH`:** Disables an event after delivery but retains its registration until the application explicitly enables it again.

These controls can support both condition-oriented and transition-oriented handling, but `kqueue` expresses them through filters and flags rather than through `epoll`'s exact level-triggered and `EPOLLET` modes.

##### Benefits and Limits of `kqueue`

- **Persistent Registration:** Registered events remain in the kernel across waits, so the application does not rebuild and transfer its complete interest set on every iteration as it does with `select()`.
- **Triggered-Event Delivery:** `kevent()` returns triggered events rather than requiring the application to inspect the complete registered descriptor collection after every wait.
    - Application-side processing therefore tends to follow the number of returned events rather than the numeric range of watched descriptors.
- **General Event Model:** Its filters can represent several kinds of kernel event in the same queue, allowing one event loop to coordinate more than network descriptors.
- **Rich Event Information:** Returned `kevent` structures can include filter-specific state in fields such as `flags`, `fflags`, and `data`, rather than merely identifying a descriptor as readable or writable.
- **Registration and Memory Costs:** Persistent registrations require kernel-maintained state. Adding, modifying, and removing events still involves kernel work, and large event sets consume system resources.
- **Readiness Is Not I/O:** `EVFILT_READ` and `EVFILT_WRITE` report conditions under which socket operations may make progress; they do not perform the application I/O.
    - The application still calls `accept()`, `read()`, `write()`, or another appropriate operation.
    - It must still handle partial progress, closure, errors, and conditions that change before the operation executes.
- **Transition-Oriented Complexity:** Flags such as `EV_CLEAR` can reduce repeated delivery of continuing conditions, but applications must correctly drain non-blocking I/O and retain enough state to resume later.
- **Platform-Specific Interface:** `kqueue` is associated with BSD-derived operating systems rather than portable POSIX. Linux provides `epoll` for a similar scalable readiness role, but the APIs and event models are not identical.

#### Other Readiness Interfaces

`select()`, `epoll`, and `kqueue` are not the only readiness interfaces. Some systems provide alternatives that retain the repeated interest-set model; others retain registrations in kernel state and return only events that occurred.

##### `poll()`

POSIX `poll()` serves the same coordination role as `select()`, but represents the watched descriptors as an array of `struct pollfd` entries rather than separate `fd_set` values.

- **`fd`:** Descriptor to monitor.
- **`events`:** Readiness conditions requested by the application, such as `POLLIN` or `POLLOUT`.
- **`revents`:** Conditions observed by the kernel and written back when `poll()` returns.

The caller supplies the number of entries, so `poll()` does not depend on the highest descriptor number or on `fd_set` capacity. It still has no persistent registration: every wait receives the descriptor array again, and the application examines entries with nonzero `revents` after the call returns.

- **`select()`:** Repeatedly transfers descriptor sets represented by `fd_set`.
- **`poll()`:** Repeatedly transfers an explicit descriptor array, avoiding the `fd_set` capacity model.
- **`epoll` and `kqueue`:** Retain the interest set in kernel-managed registrations.

`poll()` improves descriptor representation without removing the repeated-interest-set cost that scalable event mechanisms avoid.

##### `pselect()` and `ppoll()`

`pselect()` and `ppoll()` retain the readiness architecture of `select()` and `poll()`, respectively. Their additional signal mask is installed atomically with the readiness wait, avoiding a race between changing which signals can interrupt the thread and blocking for I/O. They coordinate readiness with POSIX signals; they do not address the large-interest-set scaling problems addressed by `epoll` and `kqueue`.

##### Solaris Event Ports

Solaris **event ports** provide another kernel event queue. `port_create()` creates a port; `port_associate()` associates resources with it; and `port_get()` or `port_getn()` retrieves events. Socket readiness uses a `PORT_SOURCE_FD` association with `poll()`-style conditions.

Retrieving a file-descriptor event removes its association. An application that needs future notifications must associate the descriptor again after processing the event, unlike `epoll` and ordinary `kqueue` registrations. Event ports also multiplex timers, message queues, asynchronous I/O completions, user-generated events, and other system events through the same abstraction.

##### Solaris `/dev/poll`

Solaris also introduced `/dev/poll` as a scalable extension of `poll()`. The application writes descriptor interests into the `/dev/poll` device instead of passing the complete collection on every wait, then asks the device for ready descriptors. This anticipates the persistent-interest model of interfaces such as `epoll`; modern Solaris applications generally use event ports for that role.

##### Windows `WSAPoll()`

Windows Winsock provides `WSAPoll()`, a socket-readiness interface resembling POSIX `poll()`. The caller passes an array of `WSAPOLLFD` structures containing a socket, requested events, and a `revents` field populated by Winsock. The timeout controls whether the call polls, waits for a bounded interval, or waits indefinitely.

Like `poll()`, `WSAPoll()` coordinates non-blocking sockets without persistent registrations. Windows also provides completion-based facilities, especially overlapped I/O and I/O Completion Ports.

#### Reactor Pattern

The **Reactor pattern** organizes event-driven I/O around readiness notifications. Instead of blocking one execution unit on each connection, the application registers I/O interests, waits for the operating system to report which resources may make progress, and dispatches the corresponding application handlers.

A Reactor combines the following responsibilities:

- **Event Sources:** Listening and connected sockets whose readiness state changes as I/O progresses.
- **Readiness Interests:** Conditions the application wants to observe, such as whether a socket is readable or writable.
- **Event Demultiplexer:** An operating-system readiness interface such as `select()`, `epoll`, or `kqueue`, which waits across many registered interests and returns ready events.
- **Dispatcher:** Associates returned events with application handlers and invokes the appropriate handler.
- **Event Handlers:** Perform the actual operation, such as `accept()`, `read()`, or `write()`, and update application state.

The readiness interface supplies only the event demultiplexer. `epoll_wait()` or `kevent()` reports that a socket may make progress, but does not decide what that socket represents or which application operation follows. The Reactor adds that application-level association and dispatch.

A Reactor iteration follows the readiness cycle:

1. The application registers a descriptor and its readiness interests.
2. The event loop waits through the readiness interface.
3. The kernel reports one or more ready resources.
4. The dispatcher identifies the handler associated with each resource.
5. Each handler performs non-blocking I/O and updates connection or application state.
6. The event loop waits again after it has processed the currently available work.

Readiness-delivery semantics affect handler behavior without changing the Reactor architecture. With level-triggered readiness, a resource is reported again while its condition remains true. With transition-oriented mechanisms such as `EPOLLET`, a handler normally consumes available work until the operation would block before returning control to the Reactor.

One event-loop thread can coordinate many connections, but the Reactor pattern does not require all application work to execute on that thread. A Reactor can dispatch CPU-intensive or blocking work to worker threads or processes while retaining readiness-driven coordination for sockets.

> [!example] Redis `ae` Event Loop
> Redis's **`ae`** event library is an example of the Reactor pattern. Redis registers callbacks for generic events such as `AE_READABLE` and `AE_WRITABLE`; the event loop waits for readiness and dispatches the callback associated with each fired descriptor.
>
> The OS-specific readiness backend supplies the Reactor's event demultiplexer. In GoF terms, it acts as a **Strategy** because Redis can use implementations backed by Linux `epoll`, BSD-derived `kqueue`, Solaris event ports, or `select()` while the higher-level event loop retains the same role. Each backend also acts as an **Adapter**, translating Redis's generic event representation to and from the corresponding operating-system API.
>
> For example, the Linux backend translates `AE_READABLE` and `AE_WRITABLE` into `EPOLLIN` and `EPOLLOUT`, waits through `epoll_wait()`, then translates returned events back into Redis's representation. The Reactor can therefore dispatch Redis callbacks without coupling higher-level connection-handling code to `epoll`.
<!-- -->
> [!example] Go's Netpoller Compared with Redis  
> Go's Netpoller follows the same broad Reactor structure as Redis: an OS-specific backend waits for I/O events and a platform-independent layer reacts to them.
>
> The main difference is the **dispatch target**. Redis dispatches a ready descriptor to an application callback. Go instead associates readiness with a goroutine that was parked because its network operation could not progress; when the descriptor becomes ready, the runtime marks that goroutine runnable and lets the scheduler resume it on an available OS thread.
>
> This [runtime abstraction](../Technologies/Golang/99%20Misc/Go%20Internals.md#Handling%20I/O%20Blocking%20%28The%20Netpoller%29) lets Go expose apparently blocking network operations while internally using the same readiness-driven coordination that an explicit event loop such as Redis's `ae` performs.
>
### Completion-Based I/O

Completion-based I/O changes the interaction between user space and the operating system. Instead of waiting for a resource to become ready and then issuing the corresponding I/O call, the application submits the operation itself and later receives its result.

The important distinction is therefore **readiness versus completion**: readiness reports that an operation may now make progress, while completion reports that an already-submitted operation has reached a result. This requires the application to track outstanding operations and preserve any state they depend on until their completions are processed.

#### The Completion Cycle

Completion-based I/O begins by submitting a **specific operation** rather than registering interest in a future condition. The operation can remain outstanding while the application continues doing other work, and the system later reports the result of that submitted operation.

1. **Submit the Operation**
    - The application describes the concrete work it wants performed, such as accepting a connection, receiving bytes into a buffer, or sending bytes from a buffer.
    - The request therefore usually identifies the socket, the operation, its arguments, and some application-defined context that can later be used to recognize the request.
    - This differs from readiness-based I/O, where the application first registers an interest such as "readable" and only performs `recv()` after the readiness notification arrives.
2. **Keep the Operation In Flight**
    - If the operation cannot finish immediately, it remains outstanding.
    - The application can continue doing other work while it waits.
    - Any state still referenced by the operation must remain valid, such as a receive buffer or request metadata.
    - Several operations can be in flight concurrently, possibly across many sockets.
3. **Receive the Completion**
    - When the operation reaches a terminal result, the system produces a completion associated with that submitted request.
    - The completion can report information such as the transferred byte count, an accepted connection, an error, or cancellation.
    - Unlike readiness, this reports the result of work that was already requested rather than merely saying that the operation may now make progress.
4. **Process the Result**
    - The application matches the completion to the original request and processes its result.
    - For example, a completed receive may report that 731 bytes were written into the submitted buffer.
    - The application can then parse those bytes, update connection state, and submit another operation if more work is required.

The cycle then repeats as new operations are submitted from the results of completed ones.

#### In-Flight State and Buffer Lifetime

- **Lifetime Requirement:** A submitted operation can outlive the function or event-loop iteration that created it. While the operation is **in flight**, every piece of state that the operating system or runtime may still access remains valid until the operation reaches a terminal result.
- **Receive State:** A receive operation commonly retains a destination buffer and metadata that identifies the request. Reusing or freeing that memory too early can cause the outstanding operation to write into unrelated data or invalid memory.
- **Ownership Contrast:** With readiness-based I/O, the application usually allocates or selects a buffer when it actually calls `recv()`. With completion-based I/O, the buffer is often attached to the operation at submission time and remains unavailable for unrelated use until completion, making ownership more explicit.
- **Per-Operation State:** Applications therefore commonly retain state for each submitted operation, including:
    - **Associated Socket or Connection:** The endpoint on which the operation runs.
    - **Operation Type:** The requested action, such as accept, receive, or send.
    - **Referenced Buffers:** The memory that the operation reads from or writes to.
    - **Application Context:** Information needed when the completion arrives.
- **Completion Boundary:** Once the completion has been processed, that state can be reused, released, or used to construct subsequent operations.

#### Concurrent Operations and Ordering

- **Concurrent In-Flight Work:** Completion-based interfaces allow several operations to remain **in flight** at the same time, across one or many sockets. This improves concurrency because the application does not need to wait for one operation to finish before submitting unrelated work.
- Multiple outstanding operations also create ordering concerns:
    - **Submission Order:** Operations are created in an application-defined sequence.
    - **Completion Order:** Independent operations can finish in a different order from which they were submitted. The application must therefore identify each completion rather than assume that the next completion belongs to the oldest request.
    - **Transport Order:** TCP still preserves its ordered byte-stream semantics. Completion order does not redefine the protocol's ordering guarantees.
    - **Application Coordination:** The application may still need additional coordination when multiple outstanding operations affect shared connection state or when later processing logically depends on earlier work.
- **Partial Transfers and Framing:** A completion describes only the result of one submitted operation. Many underlying I/O operations, such as `send()` and `recv()`, permit **partial transfers**, so a successful completion may report fewer bytes than the application originally requested.
- **Operation vs. Logical Task Completion:** Completing one I/O operation therefore does not necessarily complete the application's larger task. Sending an entire response may require several completed send operations, while receiving one application message may require several completed receive operations and application-level framing.

#### Cancellation, Timeouts, and Errors

- **Non-Success Outcomes:** An in-flight operation does not necessarily finish successfully. It can complete with an error, be cancelled, or remain pending long enough that the application decides it should no longer continue.
- **Cancellation Race:** By the time the application requests cancellation, the operation may already have completed or may complete concurrently with the cancellation request. Requesting cancellation therefore does not mean that the operation can immediately be forgotten.
- **Terminal Result:** The application must still observe the operation's terminal result before releasing state associated with it. Depending on the interface, that result may indicate:
    - **Successful Completion:** The operation completed normally.
    - **I/O Error:** The operation reached an error result.
    - **Cancellation:** The terminal result reports cancellation.
    - **Completion Despite Cancellation:** The terminal result reports successful completion despite a concurrent cancellation attempt.
- **Timeout Handling:** Timeouts are commonly implemented by combining this mechanism with application-level timing. When a deadline expires, the application requests cancellation of the outstanding operation and then handles whichever terminal result ultimately wins the race.
- **State Lifetime:** This preserves the same lifetime rule as normal completion: buffers, request metadata, and other referenced state remain valid until the application knows that the operation can no longer access them.

#### `io_uring` Completion Cycle

- **Completion-Based Interface:** Linux `io_uring` is an asynchronous I/O interface built around submitting operations and later retrieving their results. An application can prepare operations such as accepting connections, receiving data, or sending data, allow several of them to remain in flight concurrently, and process their completions as they become available.
- **Shared Queue Pair:** Conceptually, an `io_uring` instance maintains two shared queues between user space and the kernel:
    - **Submission Queue (SQ):** Contains references to operations that user space wants the kernel to process. Each operation is described by a **Submission Queue Entry (SQE)**.
    - **Completion Queue (CQ):** Contains results for operations that have finished. Each result is represented by a **Completion Queue Entry (CQE)**.
        - **`res`:** Stores the operation-specific result.
        - **`user_data`:** Carries the value associated with the corresponding SQE, allowing the application to identify the completed request.
- **Completion Cycle:** The application interacts with this state through several main operations:
    - **Create:** `io_uring_setup()` creates an `io_uring` instance and returns a file descriptor referring to it. User space maps the queue state shared with the kernel; libraries such as `liburing` normally wrap these setup details.
    - **Prepare an Operation:** The application obtains an SQE and describes a concrete operation in it.
        - **Socket Operations:** Include accepting a connection, receiving bytes, and sending bytes.
        - **Operation Arguments:** The SQE contains arguments such as the socket descriptor, buffer, and requested byte count.
        - **Request Correlation:** `user_data` can associate application-defined state with the operation so its eventual completion can be correlated with the original request.
    - **Submit:** The application makes one or more prepared SQEs available to the kernel.
        - **Concurrent Submission:** Multiple operations can be submitted together and remain in flight concurrently.
    - **Wait for Completions:** The application can continue executing other work or wait until one or more completions become available.
    - **Process Results:** When an operation finishes, the kernel places a CQE in the completion queue.
        - **Request Identification:** `user_data` identifies the corresponding submitted request.
        - **Operation Result:** `res` contains the operation-specific result. For operations such as receive or send, a non-negative value commonly represents the transferred byte count, while a negative value represents an error.
        - **Single-Shot Lifecycle:** A single-shot operation is no longer in flight after its completion. If the application wants the same kind of work to continue, it prepares and submits another operation.

##### Example: `io_uring` with One Listener and One Client

- **Example Scope:** The following C-like pseudocode uses `liburing` with one listening socket and one already-connected client socket.
- **Resources and State:**
    - **`listener_fd`:** File descriptor for an already-created, bound, and listening socket.
    - **`client_fd`:** File descriptor for one already-connected client socket.
    - **`ring`:** `io_uring` instance containing the submission and completion queues.
    - **`accept_request`:** Application state identifying the currently outstanding accept operation.
    - **`recv_request`:** Application state identifying the currently outstanding receive operation.
    - **`buffer`:** User-space memory supplied to the receive operation.
    - **`sqe`:** Pointer to an SQE being prepared.
    - **`cqe`:** Pointer to a CQE returned after an operation completes.

- **Create the Ring:** The process initializes an `io_uring` instance. `liburing` performs the underlying ring creation and memory mapping.

```c
struct io_uring ring;
io_uring_queue_init(QUEUE_DEPTH, &ring, 0);
```

- **Prepare the Initial Operations:** The process obtains two SQEs. One describes an accept operation on the listener, while the other describes a receive operation on the connected client.
    - **One Operation per SQE:** Each SQE represents one operation.
    - **Request Correlation:** Application request state is stored in `user_data`, allowing the corresponding CQE to identify which operation completed.

```c
struct request accept_request = {
    .type = ACCEPT,
    .fd = listener_fd
};

struct request recv_request = {
    .type = RECV,
    .fd = client_fd
};

struct io_uring_sqe *sqe;

sqe = io_uring_get_sqe(&ring);
io_uring_prep_accept(
    sqe,
    listener_fd,
    NULL,
    NULL,
    0
);
io_uring_sqe_set_data(sqe, &accept_request);

sqe = io_uring_get_sqe(&ring);
io_uring_prep_recv(
    sqe,
    client_fd,
    buffer,
    sizeof(buffer),
    0
);
io_uring_sqe_set_data(sqe, &recv_request);
```

- **Submit the Initial Operations:** `io_uring_submit()` makes both prepared SQEs available for processing.
    - **Independent In-Flight Operations:** The accept and receive operations are now independently in flight.
    - **Independent Completion:** Whichever finishes first produces a completion while the other can remain outstanding.

```c
io_uring_submit(&ring);
```

- **Wait for a Completion:** Each iteration waits for one of the outstanding operations to produce a CQE.

```c
for (;;) {
    struct io_uring_cqe *cqe;

    int result = io_uring_wait_cqe(&ring, &cqe);

    if (result < 0) {
        handle_wait_error(result);
        continue;
    }

    struct request *request =
        io_uring_cqe_get_data(cqe);
```

- **Handle and Replace a Receive:** If the receive operation completes, the process first handles its result.
    - **Positive Result:** A positive `cqe->res` is the number of bytes placed in `buffer`.
    - **Zero Result:** TCP end-of-stream.
    - **Negative Result:** An error.
    - **Replacement Requirement:** Once this CQE is produced, that particular receive operation is finished. Receiving more data therefore requires another receive operation.
    - **Buffer Reuse:** For a successful receive, the process consumes the current contents of `buffer` before giving the same buffer to a new asynchronous operation. It then prepares a replacement receive.

```c
    if (request->type == RECV) {
        if (cqe->res > 0) {
            handle_client_bytes(cqe->res, buffer);

            sqe = io_uring_get_sqe(&ring);
            io_uring_prep_recv(
                sqe,
                client_fd,
                buffer,
                sizeof(buffer),
                0
            );
            io_uring_sqe_set_data(sqe, &recv_request);
        } else if (cqe->res == 0) {
            handle_client_close(client_fd);
        } else {
            handle_recv_error(cqe->res);
        }
    }
```

- **Rearming Scope:** A closed or failed connection is not rearmed in this simplified example. A successful receive is rearmed because the server wants to continue receiving from that client.
- **Handle and Replace an Accept:** An accept CQE likewise finishes one accept operation.
    - **Accepted Descriptor:** On success, `cqe->res` contains the descriptor of the newly accepted connection.
    - **No Automatic Replacement:** Accepting that connection does not automatically create another pending accept operation.
    - **Continued Acceptance:** The process therefore prepares another accept so the listener can continue accepting future connections.

```c
    if (request->type == ACCEPT) {
        if (cqe->res >= 0) {
            int new_client_fd = cqe->res;
            handle_new_client(new_client_fd);
        } else {
            handle_accept_error(cqe->res);
        }

        sqe = io_uring_get_sqe(&ring);
        io_uring_prep_accept(
            sqe,
            listener_fd,
            NULL,
            NULL,
            0
        );
        io_uring_sqe_set_data(sqe, &accept_request);
    }
```

- **Consume the Completion and Submit Replacement Work:** After the process has extracted everything it needs from the CQE, it marks that CQE as consumed. Any replacement SQE prepared while handling the result is then submitted.

```c
    io_uring_cqe_seen(&ring, cqe);

    io_uring_submit(&ring);
}
```

- **Replacement Lifecycle:** The lifecycle therefore continues by replacing completed work:
    - **Accept:** An outstanding accept completes → process it → submit another accept.
    - **Receive with Data:** An outstanding receive completes with data → process the buffer → submit another receive.
    - **Terminal Receive:** An operation that should no longer continue, such as a receive that reaches end-of-stream, is not replaced.
- **Omitted Production State Transitions:** The example deliberately keeps one accept and one receive workflow simple. A real server would normally create per-connection request state and buffers, submit receive operations for newly accepted connections, remove state after closure, handle submission failures and SQ exhaustion, manage many concurrent operations, and potentially use multishot operations or batching to avoid repeatedly submitting equivalent single-shot requests.

##### Benefits and Limits of `io_uring`

- **Submission and Completion Batching:** Multiple operations can be submitted together and multiple CQEs can be processed together, allowing coordination overhead to be amortized across several operations.
- **Shared Queue State:** Submission and completion state is exchanged through memory shared between user space and the kernel.
- **Many In-Flight Operations:** One ring can coordinate outstanding operations across many descriptors without requiring one application thread to block for each operation.
- **Request Correlation:** Operations can complete independently, so `user_data` allows each CQE to be associated with its original request and application state.
- **In-Flight Resource Lifetime:** Buffers and other state referenced by an outstanding operation must remain valid for as long as the operation may still access them.
- **Underlying I/O Semantics:** `io_uring` changes how operations are submitted and how their results are delivered, but the semantics of the underlying operation still apply. Socket receives and sends can therefore produce partial transfers.
- **Broader I/O Interface:** `io_uring` is not limited to networking. It also supports operations for files, polling, timers, synchronization, and other kernel facilities.
- **Linux-Specific Interface:** `io_uring` is a Linux API rather than a portable POSIX interface.

#### Windows Overlapped I/O and IOCP

- **Overlapped I/O and IOCP:** Windows supports asynchronous socket operations through **overlapped I/O**. An application submits operations such as accept, receive, or send together with an `OVERLAPPED` structure that identifies the outstanding request. **I/O Completion Ports (IOCP)** provide a shared queue through which the application can retrieve the results of those operations.
- **Completion Port:** A kernel-managed queue that receives completion packets from associated handles.
- **Handle Association:** Sockets are associated with a completion port using `CreateIoCompletionPort()`. Each association can carry a **completion key**, commonly used to identify connection-level state.
- **Overlapped Request:** Each asynchronous operation carries its own `OVERLAPPED` structure. When the operation completes, the same pointer is returned with its completion, allowing the application to identify the specific request.
- **Completion Cycle:** The application interacts with this state through several main operations:
    - **Create:** `CreateIoCompletionPort()` creates a completion port.
    - **Associate Sockets:** Sockets that will produce completions are associated with the port.
    - **Submit an Operation:** An overlapped-capable operation such as `AcceptEx()`, `WSARecv()`, or `WSASend()` is called with an `OVERLAPPED` structure.
        - **Operation State:** The operation can complete immediately or remain pending.
        - **Pending Result:** `WSA_IO_PENDING` means the operation was successfully initiated and will report its result asynchronously.
        - **In-Flight Lifetime:** The `OVERLAPPED` structure and any referenced buffers must remain valid while the operation is outstanding.
    - **Wait for Completions:** Worker threads call `GetQueuedCompletionStatus()` or `GetQueuedCompletionStatusEx()` to dequeue completion packets.
    - **Process Results:** A completion reports the number of bytes transferred, the completion key associated with the socket, and the `OVERLAPPED` pointer associated with the completed operation.
        - **Single-Shot Lifecycle:** After processing a one-shot operation, the application submits another one when it wants that work to continue.

##### Example: IOCP with One Listener and One Client

- **Example Scope:** The following C-like pseudocode uses one listening socket and one already-connected client socket. The listener has one outstanding `AcceptEx()` operation, while the client has one outstanding `WSARecv()` operation.
- **Resources and State:**
    - **`listener`:** Already-created, bound, and listening socket.
    - **`client`:** One already-connected socket.
    - **`completion_port`:** IOCP used to collect completed operations.
    - **`accept_request`:** State for the outstanding `AcceptEx()` operation.
    - **`recv_request`:** State for the outstanding `WSARecv()` operation.
    - **`OVERLAPPED`:** Windows structure embedded in each request and used to identify its completion.
    - **`accept_socket`:** Socket created before `AcceptEx()` and filled in when a connection is accepted.
    - **`buffer`:** User-space storage supplied to the receive operation.
- **Request Structure:** A request can embed `OVERLAPPED` together with the application state required to process its result:

```c
struct request {
    OVERLAPPED overlapped;
    enum operation_type type;

    SOCKET socket;
    WSABUF buffer;
};
```

- **Create the Completion Port and Associate Sockets:** The process creates an IOCP and associates both the listener and the existing client with it.
    - **Completion Key:** Can identify state shared by operations on that socket.
    - **Operation Identity:** The `OVERLAPPED` pointer returned later identifies the individual operation.

```c
HANDLE completion_port =
    CreateIoCompletionPort(
        INVALID_HANDLE_VALUE,
        NULL,
        0,
        0
    );

CreateIoCompletionPort(
    (HANDLE) listener,
    completion_port,
    (ULONG_PTR) listener_state,
    0
);

CreateIoCompletionPort(
    (HANDLE) client,
    completion_port,
    (ULONG_PTR) client_state,
    0
);
```

- **Prepare and Submit the Initial Receive:** The application initializes a request and passes its embedded `OVERLAPPED` structure to `WSARecv()`.

```c
struct request recv_request = {0};

recv_request.type = RECV;
recv_request.socket = client;
recv_request.buffer.buf = buffer;
recv_request.buffer.len = sizeof(buffer);

DWORD flags = 0;

int result = WSARecv(
    client,
    &recv_request.buffer,
    1,
    NULL,
    &flags,
    &recv_request.overlapped,
    NULL
);

if (
    result == SOCKET_ERROR &&
    WSAGetLastError() != WSA_IO_PENDING
) {
    handle_recv_submission_error();
}
```

- **Submission Result:** A return of `WSA_IO_PENDING` is not an operation failure. It means the receive remains in flight and its result will be reported later. An immediate successful return also represents a successfully initiated overlapped operation; when used normally with IOCP, its completion is still delivered through the completion mechanism.
- **Prepare and Submit the Initial Accept:** `AcceptEx()` requires the application to create the socket that will represent the accepted connection before submitting the operation.

```c
struct request accept_request = {0};

accept_request.type = ACCEPT;
accept_request.socket =
    WSASocket(
        AF_INET,
        SOCK_STREAM,
        IPPROTO_TCP,
        NULL,
        0,
        WSA_FLAG_OVERLAPPED
    );

AcceptEx(
    listener,
    accept_request.socket,
    accept_buffer,
    0,
    ADDRESS_SPACE,
    ADDRESS_SPACE,
    NULL,
    &accept_request.overlapped
);
```

- **Accept State and Completion:** The accept socket and the `OVERLAPPED` request remain associated with this particular outstanding accept. With a receive-data length of zero, this `AcceptEx()` can complete when the connection has been accepted rather than waiting for application data from the peer.
- **Wait for a Completion:** The process waits for one completion packet from the port.

```c
for (;;) {
    DWORD transferred;
    ULONG_PTR completion_key;
    OVERLAPPED *overlapped;

    BOOL success =
        GetQueuedCompletionStatus(
            completion_port,
            &transferred,
            &completion_key,
            &overlapped,
            INFINITE
        );
```

- **Completion Contents:** A dequeued completion contains information from two different scopes:
    - **`completion_key`:** Identifies the handle association and can recover connection-level state.
    - **`overlapped`:** Identifies the particular operation that completed.
    - **`transferred`:** Reports the byte count associated with that operation.
- **Failed Completion:** `GetQueuedCompletionStatus()` can also return a completion for a failed operation; in that case `overlapped` is still non-`NULL`, while the return value indicates failure.
- **Recover the Request:** Because `OVERLAPPED` is embedded in the request structure, the application can recover the request that owns it.

```c
    struct request *request =
        CONTAINING_RECORD(
            overlapped,
            struct request,
            overlapped
        );
```

- **Handle and Replace a Receive:** A receive completion finishes that particular `WSARecv()` request.
    - **Positive Byte Count:** Data was received.
    - **Zero Byte Count:** A successful TCP receive indicates orderly connection closure.
    - **Continued Reception:** If the server wants to continue receiving after processing the bytes, it submits another `WSARecv()` operation.

```c
    if (request->type == RECV) {
        if (!success) {
            handle_recv_error(GetLastError());
            continue;
        }

        if (transferred == 0) {
            handle_client_close(request->socket);
            continue;
        }

        handle_client_bytes(
            transferred,
            request->buffer.buf
        );

        ZeroMemory(
            &request->overlapped,
            sizeof(request->overlapped)
        );

        DWORD flags = 0;

        int result = WSARecv(
            request->socket,
            &request->buffer,
            1,
            NULL,
            &flags,
            &request->overlapped,
            NULL
        );

        if (
            result == SOCKET_ERROR &&
            WSAGetLastError() != WSA_IO_PENDING
        ) {
            handle_recv_submission_error();
        }
    }
```

- **Request and Buffer Reuse:** The same request storage and buffer can be reused here because the previous receive has already reached its completion and the application has finished processing that result before submitting the next receive.
- **Handle and Replace an Accept:** A successful `AcceptEx()` completion finishes one accept request and leaves `accept_request.socket` referring to the newly connected socket.
- **Accepted-Socket Setup:** The application first updates the accepted socket's context and associates it with the completion port so subsequent overlapped operations on that connection can deliver their completions there.

```c
    if (request->type == ACCEPT) {
        if (!success) {
            handle_accept_error(GetLastError());
        } else {
            SOCKET accepted = request->socket;

            setsockopt(
                accepted,
                SOL_SOCKET,
                SO_UPDATE_ACCEPT_CONTEXT,
                (char *) &listener,
                sizeof(listener)
            );

            CreateIoCompletionPort(
                (HANDLE) accepted,
                completion_port,
                (ULONG_PTR) new_client_state,
                0
            );

            handle_new_client(accepted);
        }
```

- **Accept Replacement:** The completed `AcceptEx()` operation is no longer outstanding. To continue accepting connections, the application creates another accept socket, resets the request state, and submits another `AcceptEx()`.

```c
        ZeroMemory(
            &request->overlapped,
            sizeof(request->overlapped)
        );

        request->socket =
            WSASocket(
                AF_INET,
                SOCK_STREAM,
                IPPROTO_TCP,
                NULL,
                0,
                WSA_FLAG_OVERLAPPED
            );

        AcceptEx(
            listener,
            request->socket,
            accept_buffer,
            0,
            ADDRESS_SPACE,
            ADDRESS_SPACE,
            NULL,
            &request->overlapped
        );
    }
}
```

- **Replacement Lifecycle:** The operation lifecycle therefore follows the same general rule for both kinds of work:
    - **Accept:** An overlapped accept completes → process the accepted socket → submit another accept.
    - **Receive with Data:** An overlapped receive completes with data → process those bytes → submit another receive.
    - **Terminal Receive:** An operation that should no longer continue, such as a receive reaching end-of-stream, is not replaced.
- **Omitted Production State Transitions:** A real IOCP server would normally maintain per-connection and per-operation state separately, post several accepts in advance, initiate receives for newly accepted clients, handle synchronous submission failures, manage request allocation and destruction carefully, process partial sends, handle cancellation and shutdown, and use multiple worker threads retrieving completions from the same port.

##### Benefits and Limits of IOCP

- **Many Outstanding Operations:** A completion port can coordinate asynchronous operations across many associated sockets without requiring one blocked application thread per socket.
- **Central Completion Queue:** Completions from many handles can be collected through one port and processed by a worker pool.
- **Connection and Operation Correlation:** Completion keys provide handle-level context, while the returned `OVERLAPPED` pointer identifies the individual completed operation.
- **Worker Concurrency Control:** A completion port has a concurrency value that helps Windows control how many associated worker threads actively process completions at once.
- **In-Flight Resource Lifetime:** `OVERLAPPED` structures and buffers referenced by pending operations must remain valid until those operations have completed.
- **Underlying I/O Semantics:** Overlapped execution changes how an operation waits and reports its result; socket stream semantics such as partial transfers and end-of-stream still apply.
- **Windows-Specific Interface:** Overlapped I/O, IOCP, and extensions such as `AcceptEx()` are Windows mechanisms rather than portable POSIX interfaces.

#### Proactor Pattern

- **Completion-Centered Model:** The **Proactor pattern** organizes asynchronous I/O around the completion of operations that were submitted in advance. Instead of waiting for a resource to become ready and then deciding which I/O call to perform, the application initiates the operation itself and later dispatches logic when that operation completes.
- **Proactor Responsibilities:** A Proactor typically combines the following responsibilities:
    - **Asynchronous Operations:** Concrete I/O requests such as accept, receive, or send operations.
    - **Operation State:** Application state associated with each outstanding request, including buffers and context needed when its result arrives.
    - **Completion Mechanism:** The operating-system facility that reports finished operations, such as `io_uring` completion entries or IOCP completion packets.
    - **Completion Dispatcher:** Associates each completion with the operation and application state that produced it.
    - **Completion Handlers:** Process the completed result and decide what work should be submitted next.
- **Proactor Cycle:**
    1. The application prepares and submits one or more asynchronous operations.
    2. Those operations remain in flight while the application continues other work.
    3. The completion mechanism reports operations that have reached a result.
    4. The dispatcher correlates each completion with its original request.
    5. The completion handler processes the result and updates application state.
    6. The handler submits subsequent operations when more work is required.
- **Result-Centered Dispatch:** The application reacts to **results**, not to permission to attempt the I/O. The operating-system interface performs or coordinates the submitted operation, while application code becomes active again when there is a completion to process.
- **Interface Realizations:** `io_uring` and Windows overlapped I/O with IOCP can both support this architecture. Their APIs differ substantially, but both allow application logic to be structured around outstanding operations and the completions those operations later produce.

### Readiness and Completion Compared

Readiness-based and completion-based I/O both allow one execution context to coordinate many sockets without dedicating a blocked thread to each connection. The difference is where the I/O operation sits in the interaction between user space and the operating system.

|Model|Application submits|Kernel reports|Application action after notification|
|---|---|---|---|
|**Readiness-Based I/O**|Interest in a condition such as readable or writable state.|That an operation may be able to make progress.|Call `accept()`, `recv()`, `send()`, or another appropriate operation and handle its result.|
|**Completion-Based I/O**|The concrete operation itself, such as accept, receive, or send.|The result of that submitted operation.|Correlate the completion with its request, process the result, and submit subsequent work if necessary.|

- **Readiness Interaction:** With readiness-based I/O, the application owns both stages of the interaction. It first waits for the operating system to indicate that a resource may make progress, then performs the actual I/O operation. A readable event, for example, does not contain the received bytes; it tells the application that calling `recv()` is likely to make progress.
- **Completion Interaction:** With completion-based I/O, those stages are combined into one outstanding request. The application submits the receive operation before the data is necessarily available, allows the operation to remain in flight, and later receives its result. The completion therefore refers to a particular operation rather than only to the state of the socket.
- **Preserved Application State:** A readiness-driven event loop primarily tracks **resources and interests**, such as which sockets should be monitored for reads or writes. A completion-driven design primarily tracks **outstanding operations**, including their buffers, request metadata, and the application state needed when each operation finishes.
- **Unchanged Transport Semantics:** The two models do not change the semantics of the underlying transport or I/O operation. TCP remains an ordered byte stream in either model, and operations such as `send()` and `recv()` can still produce partial transfers. The models differ in how the application coordinates those operations, not in what TCP means.
- **Event-Driven Patterns:** At the architectural level, these approaches commonly correspond to two event-driven patterns:
    - **Reactor:** Dispatch application code when a resource becomes ready, after which the handler performs the I/O operation.
    - **Proactor:** Submit the I/O operation first and dispatch application code when that operation completes.
- **Mechanism and Architecture:** The operating-system mechanism and the application architecture should still be distinguished. A library can expose a Proactor-style completion API while internally using a readiness mechanism, and a readiness interface does not by itself determine how an application structures its handlers or concurrency.

## Socket Lifetime and Closure

Descriptor lifetime and transport shutdown are related but not identical concepts.

- **Descriptor Release:** `close(fd)` removes that descriptor's reference to the open socket resource.
- **Final Resource Release:** If no other descriptor or kernel reference keeps the resource alive, the kernel can release the socket object and its associated memory.
- **Shared References:** Duplicated descriptors and descriptors inherited by child processes affect when the final release actually occurs.
- **`shutdown()` Without Closing:** `shutdown()` can disable reads, writes, or both on an existing socket without necessarily releasing the descriptor.
- **Half-Close:** A write-side shutdown can express that the application will send no more bytes while still allowing it to receive.
    - This exposes TCP's bidirectional connection as two independently closable byte directions.
- **Transport Representation:** The transport protocol determines how closure intent appears on the network.
    - TCP may use `FIN` for orderly half-close and `RST` for certain abortive cases, while descriptor lifetime still follows reference ownership in the process.

## Sharing and Distributing Listening Sockets

The socket abstraction allows several execution units to participate in connection acceptance, but there are two importantly different mechanisms: sharing one listener and creating several independent listeners.

### Shared Listening Socket

- **Socket Ownership:** Threads in one process naturally share the process's descriptor table, so several threads can call `accept()` on the same listening socket.
- **Process Sharing:** Related processes can share a listening socket through descriptor inheritance or explicit descriptor-passing mechanisms.
- **Kernel Arbitration:** When several execution units wait on one listener, the kernel coordinates which waiter receives an available connection.
- **Contention Risk:** Poor wakeup strategies can cause a **thundering herd**, where several workers wake for work that only one can claim.
- **Modern Mitigation:** Modern kernels and server designs contain mechanisms to reduce this waste, but the architectural concern comes from contention around one shared listening resource.

### Multiple Listeners with `SO_REUSEPORT`

- **Independent Listeners:** Some operating systems provide `SO_REUSEPORT`, allowing multiple independent sockets to bind compatible copies of the same local address and port.
- **Linux Binding Rule:** On Linux, every socket must enable `SO_REUSEPORT` before `bind()`, and processes binding the same address must have the same effective UID.
    - This prevents a process running as a different user from joining the listener group and receiving a share of new traffic.
    - It does not protect against a malicious or compromised process running with the same effective UID; that process can join the group. Other operating systems may impose different rules.
- **Independent Queue State:** Instead of several workers contending on one socket object, each worker can own its own listener and associated queue state.
- **Kernel Distribution:** The kernel distributes incoming traffic among the sockets in the group.
- **Distribution Policy:** The policy is an OS implementation detail and is based on transport/network information rather than application-level workload.
- **Application-Level Imbalance:** A connection that later carries many requests can therefore create more application work than another connection even if the kernel initially distributed the connections evenly.
