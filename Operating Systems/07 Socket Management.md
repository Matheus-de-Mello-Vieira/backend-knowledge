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

> [!example] Go's Netpoller
> Go allows a goroutine to perform what looks like a blocking network operation without requiring one OS thread to remain blocked for every socket. The runtime can park the goroutine and use the operating system's readiness facilities to learn when the descriptor can make progress. On Linux, Go's netpoller uses mechanisms such as `epoll`; when readiness arrives, the runtime can make the corresponding goroutine runnable again. This [runtime abstraction](../Technologies/Golang/99%20Misc/Go%20Internals.md#Handling%20I/O%20Blocking%20%28The%20Netpoller%29) is built on top of the OS socket and scheduler primitives.

#### `select()` Readiness Cycle

`select()` accepts up to three `fd_set` collections:

- **`readfds`:** Descriptors to watch for readable state.
- **`writefds`:** Descriptors to watch for writable state.
- **`exceptfds`:** Descriptors to watch for exceptional conditions.

Each collection can contain many file descriptors, and a caller can omit categories it does not need. The call is a blocking readiness wait when given a positive timeout or no timeout; a zero timeout makes it return immediately and is therefore a polling use of the interface.

- **Build Sets:** The process builds each needed `fd_set` collection with the descriptors it wants the kernel to monitor.
- **Wait:** It calls `select()` with those sets and a timeout. The call returns when one or more descriptors become ready, the timeout expires, or the wait is interrupted.
- **Inspect Results:** `select()` modifies each supplied set so it retains only the ready descriptors. `FD_ISSET(fd, &set)` tests whether one specific descriptor remains in a returned set, and therefore whether it is ready for that set's operation category. The test does not transfer data or report a byte count.
- **Perform I/O:** The process calls `read()`, `write()`, `accept()`, or another appropriate I/O operation on each ready descriptor.

##### Example: `select()` with One Listener and One Client

The following C-like pseudocode uses one listening socket and one already-connected client socket.

- **Resources and State:**
    - `listener_fd`: File descriptor for an already-created, bound, and listening socket.
    - `client_fd`: File descriptor for one already-connected client socket.
    - `readfds`: `fd_set` containing the descriptors that the current `select()` call should monitor for read readiness.
    - `watched_client_fd`: Copy of the client descriptor included in the current `readfds` set.
    - `max_fd`: Highest-numbered descriptor currently being watched.
    - `buffer`: User-space memory where bytes read from the client socket are stored.

**Build the Interest Set:** Each loop iteration creates a fresh `readfds` set. `FD_ZERO()` clears the set, and `FD_SET()` adds the listener and client descriptors.
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
- **I/O Concurrency:** One thread can coordinate readiness for many descriptors. The thread may block inside `select()` while nothing is ready, but it does not need one blocked thread per descriptor.
- **Linear Scanning:** After `select()` returns, the process typically tests descriptors with `FD_ISSET()` across the range from `0` through `nfds - 1`. This work grows linearly with that range, including unused descriptor numbers below the highest watched descriptor.
    - **Application-Side Optimization:** The process can maintain a collection of the descriptors it actually registered and call `FD_ISSET()` only for those after `select()` returns. This avoids user-space checks for unused numeric gaps, but it does not reduce `select()`'s own worst-case O(`nfds`) range-dependent work.
- **Set Transfer and Rebuilding:** Each call passes descriptor sets to the kernel and receives modified sets back. The process must also rebuild those sets before the next call, adding overhead as the watched range grows.
- **Descriptor-Set Capacity:** An `fd_set` has an implementation-defined capacity, commonly exposed as `FD_SETSIZE`. A process cannot use `select()` with descriptors outside that set's supported range.

#### `epoll` Readiness Cycle

Linux `epoll` implements the same readiness-based I/O model as `select()`, but changes how the set of watched descriptors is maintained and how ready descriptors are returned. Instead of supplying the complete descriptor set on every wait, the process creates an **epoll instance**, registers descriptors with it, and then repeatedly asks the kernel for events from descriptors that have become ready.

Conceptually, an epoll instance maintains two kinds of state:

- **Interest List:** The descriptors and event types that the application has registered for monitoring.
- **Ready List:** References to registered descriptors for which the kernel has detected relevant readiness events.

The process interacts with this state through three main operations:

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

> [!note] Production Event-Loop State
> A real server normally uses non-blocking sockets, registers every accepted client, deletes interests for closed descriptors, handles end-of-stream and errors, processes partial reads and writes, and retains application state for each connection between iterations.

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

### Completion-Based I/O

- **Submission:** User space submits a concrete operation, such as accepting a connection or receiving into a supplied buffer, for the kernel to perform.
- **Completion:** The kernel later reports the operation's result. A completion identifies the submitted operation and records its outcome, such as the byte count, accepted connection, or error.
- **Result Handling:** The application processes completed operations rather than receiving permission to attempt a separate `accept()`, `recv()`, or `send()` call.
- **Concurrent Operations:** Several operations can be in flight at once and can complete in a different order from submission. Applications must correlate every completion with its request and preserve the request state and any buffers used by an in-flight operation for as long as the interface requires.
- **Stream Semantics:** Stream protocols still require application-level ordering and framing; a completion reports one operation's result, not a complete application message.
- **Windows I/O Completion Ports (IOCP):** Windows can queue completions for overlapped I/O operations to a completion port, allowing workers to retrieve completed work without waiting on each socket individually.
- **Linux `io_uring`:** Linux provides shared submission and completion rings. User space places requests in the submission ring, and the kernel later records their results in the completion ring. It supports socket operations such as accepting connections and reading or writing data, but it can also express polling-related operations; it is not merely another name for readiness notification.

### Readiness and Completion Compared

| Model | Kernel reports | Application action after notification |
| --- | --- | --- |
| Readiness-based I/O | An operation may be able to make progress. | Call `accept()`, `recv()`, or `send()` and still handle partial progress or `EAGAIN`. |
| Completion-based I/O | A submitted operation has finished with a result. | Match the completion to its request and process its byte count, resource, or error. |

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
