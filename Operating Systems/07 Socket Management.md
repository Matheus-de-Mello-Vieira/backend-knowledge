# Socket Management

Socket management is how an operating system exposes network communication to user-space programs. The kernel owns socket objects, integrates them with transport protocols such as TCP and UDP, receives incoming packets, maintains protocol and queue state, and decides when I/O can make progress. User-space programs interact with that machinery through descriptors, system calls, and kernel-managed buffers.

This note focuses on the operating-system abstraction and the [POSIX](01%20Why%20an%20OS.md#Software,%20Hardware,%20and%20POSIX) socket interface commonly used on Unix-like systems. Protocol-specific behavior such as TCP retransmission, congestion control, or UDP header structure belongs in the networking notes; application-server architectures belong in backend engineering.

## Sockets as Kernel Objects

Network sockets are one important kind of resource referenced through a [file descriptor](02%20The%20Anatomy%20of%20a%20Process.md#File%20Descriptors%20%28FDs%29). On Unix-like systems, `socket()` returns an FD that the process uses as a local handle. The descriptor is not the network connection itself: it refers through the process's descriptor machinery to kernel-maintained socket state.

That kernel state can include the socket type and protocol, local and remote addresses, ports, transport connection state, receive and send queues, socket options, and waiters interested in I/O readiness. Because the FD is only a handle, normal descriptor lifetime rules also apply to sockets. A descriptor can be duplicated with `dup()`, inherited across `fork()`, or shared by threads through the process's descriptor table.

Closing one descriptor therefore does not necessarily destroy the underlying socket immediately. If another descriptor still refers to the same open resource, the socket remains reachable through that reference. This distinction becomes important for inherited listening sockets, graceful shutdown, and descriptor leaks.

> [!example] Forked Server Workers
> A server can create and bind a listening socket before calling `fork()`. The child processes inherit descriptors referring to the same underlying listening resource, so several workers can call `accept()` on that listener. Closing the listener in one child does not remove the other inherited references.

Like other descriptor-backed resources, sockets consume finite process and kernel resources. A process that continually creates sockets without closing descriptors it no longer needs can eventually hit its descriptor limit and receive errors such as `EMFILE`.

## Socket Types

The socket API separates the application's I/O semantics from the transport protocol implementation. For Internet sockets, two important types are stream sockets and datagram sockets.

### Stream Sockets

A stream socket exposes an ordered byte stream. With the Internet protocol family this is commonly paired with [TCP](../Networking/02%20Protocols/05%20TCP.md). The application writes bytes into the stream and reads bytes from it; boundaries between individual `send()` or `write()` calls are not preserved. If one side writes 100 bytes and then another 100 bytes, the peer may read 50, then 120, then 30 bytes depending on buffering and timing.

TCP stream sockets normally become associated with both a local and remote endpoint. The application interacts with one connected socket while the kernel maintains the protocol state required to deliver the ordered stream.

### Datagram Sockets

A datagram socket preserves message boundaries. With the Internet protocol family this is commonly paired with [UDP](../Networking/02%20Protocols/04%20UDP.md). One `sendto()` operation produces one transport datagram, and one `recvfrom()` consumes one datagram while also allowing the application to learn which peer sent it.

UDP does not require an `accept()` operation that creates a new socket for every remote peer. A single bound datagram socket can receive messages from many different source addresses. Applications can also use `connect()` with UDP to set a default peer and restrict which peer is accepted, but this does not create a TCP-style transport handshake.

## Addressing, Ports, and Demultiplexing

IP addresses identify network interfaces or hosts at the network layer, while transport protocols add ports so multiple communication endpoints can coexist on the same host. The kernel combines protocol, address, port, and connection state to decide which socket should receive incoming traffic. Packets are therefore demultiplexed to kernel sockets first; applications reach those sockets through their descriptors.

For an established TCP connection, the transport endpoints are commonly described by the four-tuple `(source IP, source port, destination IP, destination port)`. This allows many simultaneous TCP connections to share the same server port because the complete connection identity differs. A listening socket is usually selected primarily by the local address and port, while established traffic can be matched against the full connection identity.

UDP has no accepted socket per peer. The kernel normally identifies the appropriate bound datagram socket using the protocol and local addressing information, with the exact matching rules affected by whether the socket has been connected and by socket options.

## POSIX Socket Interface

POSIX exposes socket-specific operations on top of the general file-descriptor model. Generic descriptor calls such as `read()`, `write()`, and `close()` can operate on sockets, while socket-specific calls expose operations and metadata that do not make sense for ordinary files.

### Creating a Socket

`socket()` asks the kernel to create a socket object and returns a descriptor referring to it. The call specifies an address family such as IPv4 or IPv6, a socket type such as `SOCK_STREAM` or `SOCK_DGRAM`, and optionally a protocol when the family/type pair does not already imply one.

Creating the socket establishes the kernel object but does not by itself choose the local endpoint or establish a remote connection.

### Binding and Local Endpoints

`bind()` associates a socket with a local address. A server commonly binds explicitly because clients need a stable destination, while a client can often let the kernel choose an ephemeral local port automatically when communication begins.

Binding to a specific local IP restricts the socket to traffic addressed to that interface or address. A wildcard address such as `0.0.0.0` on IPv4 asks the kernel to accept traffic for the chosen port on all suitable local IPv4 interfaces. Whether multiple sockets may bind overlapping addresses depends on the socket type, current state, operating system, and socket options.

### Establishing Outbound Connections

`connect()` associates a socket with a remote endpoint, but its transport meaning depends on the socket type.

For a TCP stream socket, `connect()` initiates connection establishment. On a blocking socket the call normally waits until the connection succeeds or fails; on a non-blocking socket, establishment can continue asynchronously and later become observable through readiness/error state. The kernel performs the TCP handshake rather than requiring user space to exchange the handshake packets manually.

For UDP, `connect()` does not perform a transport handshake. It records a default remote peer in the socket state and can restrict received datagrams to that peer, allowing calls such as `send()` and `recv()` to omit explicit peer addresses.

### Listening and Accepting

A TCP server commonly follows this lifecycle:

1. `socket()` creates the socket-backed descriptor.
2. `bind()` associates the socket with a local address and port.
3. `listen()` changes the socket into a passive listening socket.
4. The kernel receives connection-establishment packets and performs the TCP handshake.
5. Completed connections wait until the application is ready to claim them.
6. `accept()` returns a descriptor referring to a new connected socket.

The packet-level three-way handshake is covered in [How Connections are Established](../Networking/03%20Connections/01%20How%20Connections%20are%20Established.md). The important OS distinction is that normal server code does not manually receive the `SYN`, generate the `SYN-ACK`, and interpret the final `ACK`. The kernel's TCP implementation handles those protocol transitions and exposes the completed connection through `accept()`.

#### Listening Socket vs. Connected Socket

The listening socket is a persistent passive endpoint. Calling `accept()` does not transform it into a client connection. Instead, the kernel returns another descriptor referring to a connected socket dedicated to the established connection, while the original listener remains available for future arrivals.

A server can therefore have one listening socket and thousands of connected sockets at the same time. Each connected socket has its own transport state and I/O queues even though the connections originally arrived through the same listener.

#### Pending and Established Connection Queues

The kernel needs somewhere to keep connection state while handshakes and application acceptance proceed at different speeds. Conceptually, TCP servers therefore distinguish between incomplete connection-establishment state and fully established connections waiting for `accept()`.

On Linux this is commonly discussed as a SYN queue for incomplete handshakes and an accept queue for completed connections. Other operating systems and kernel versions may implement and size these structures differently, so the two-queue model should be treated as a useful conceptual description rather than a universal data-structure contract.

The backlog supplied to `listen()` influences how much completed connection work can wait for the application, but its exact interpretation and limiting behavior are OS-specific. When the application accepts connections too slowly, queues can saturate and the kernel eventually has to delay, drop, reset, or otherwise refuse additional connection work according to its implementation and configuration.

#### Blocking `accept()`

On a blocking listening socket, `accept()` waits when no completed connection is available. The kernel marks the calling thread as sleeping and can wake it when a connection becomes ready. On a non-blocking listener, `accept()` returns immediately when there is nothing to accept, typically with `EAGAIN` or `EWOULDBLOCK` on Unix-like systems.

> [!example] Gunicorn and the Accept Queue
> A pre-fork application server such as Gunicorn can create a listening socket and have multiple worker processes call `accept()` on inherited references to that listener. The kernel maintains the pending connection state; the workers consume completed connections when they are ready to run application code.

### Data Transfer

Sockets participate in the common descriptor interface, so `read()` and `write()` can operate on them. Socket-specific calls provide additional capabilities:

- `send()` and `recv()` operate on an already-associated peer while accepting socket-specific flags.
- `sendto()` and `recvfrom()` additionally carry peer addressing information, which is especially important for connectionless datagram sockets.

The common FD interface therefore unifies how the process identifies the resource, while these socket-specific operations expose networking semantics that ordinary files do not have.

### Socket Configuration

`getsockopt()` and `setsockopt()` read and modify options associated with a socket or its protocol stack. Options can control concerns such as address reuse, buffer sizing, keepalive behavior, or protocol-specific algorithms.

Examples include `SO_REUSEADDR`, `SO_REUSEPORT`, receive/send buffer options, and TCP-specific options such as `TCP_NODELAY`. The API for setting an option belongs to socket management; the transport consequence of an option such as `TCP_NODELAY` belongs to [TCP](../Networking/02%20Protocols/05%20TCP.md) and its related protocol notes.

### Shutdown and Descriptor Closure

`shutdown()` and `close()` operate at different abstraction layers. `shutdown()` changes a connected socket's communication state, allowing reads, writes, or both directions to be disabled while the descriptor remains open. `close()` releases that descriptor's reference according to the general [descriptor lifetime](02%20The%20Anatomy%20of%20a%20Process.md#Descriptor%20Operations%20and%20Lifetime) rules.

The final transport behavior depends on the protocol. For TCP, orderly or abortive closure can produce protocol-level transitions involving `FIN` or `RST`, but those wire-level details are separate from descriptor ownership.

## Listener, Acceptor, and Worker Roles

Three roles are useful when describing how application servers interact with TCP sockets:

- **Listener:** owns or refers to the listening socket that receives incoming connection attempts.
- **Acceptor:** calls `accept()` and obtains connected sockets from the kernel.
- **Worker:** reads requests, performs application work, and writes responses through connected sockets.

These are conceptual roles, not requirements for separate threads or processes. A single execution unit can perform all three, one acceptor can distribute connections to many workers, or many workers can accept directly. Those compositions are application architecture and are covered in [Application Server Concurrency](../Backend%20Engineering/Concurrency/02%20Application%20Server%20Concurrency.md#Connection%20Distribution%20Models).

## Receiving Data

Once incoming network data is associated with a socket, the kernel processes the relevant transport protocol and makes application data available in the socket's receive state. The application then calls an operation such as `read()`, `recv()`, or `recvfrom()` to move data into user-space memory.

For a stream socket, one read is not tied to one packet or one peer write. `recv()` may return fewer bytes than requested even though the connection remains open, so applications must treat TCP as a stream and continue reading until their own application-level framing says that a complete message has arrived.

On a blocking socket, a read that cannot currently return useful data sleeps the calling thread until the operation can make progress. It does not inherently pause every thread in the process. On a non-blocking socket, the call returns immediately instead.

For TCP, an orderly shutdown by the peer eventually appears as end-of-stream: after already-buffered bytes have been consumed, a read returns zero bytes. Transport-level FIN/RST behavior is part of TCP; the socket API turns that protocol state into application-visible I/O results.

## Sending Data

`write()` or `send()` asks the kernel to accept application bytes for transmission through a socket. The data generally moves from user-space memory into kernel-managed networking state, after which the transport protocol and network stack decide how and when it is transmitted.

A successful `send()` does **not** mean that the remote application has received or processed the bytes. It normally means that the local kernel accepted some amount of data from the application. Stream-socket writes can also be partial, so code must use the returned byte count rather than assuming the whole requested buffer was accepted.

Some operating systems also provide specialized cross-resource operations such as Linux [`sendfile()`](02%20The%20Anatomy%20of%20a%20Process.md#Resource-Specific%20Operations), which can move regular-file data toward a socket without first routing the payload through an application buffer. The socket remains the network destination; the avoided user-space copy and its performance consequences are discussed through [Kafka's zero-copy example](03%20Memory%20Management.md#Architecture%20Story:%20Kafka,%20DMA,%20and%20Zero-Copy).

For TCP, later protocol work includes segmentation, acknowledgments, retransmissions, flow control, congestion control, and algorithms such as Nagle's algorithm. Those mechanisms belong to [TCP](../Networking/02%20Protocols/05%20TCP.md); the OS-facing boundary is that the application submits bytes to the socket while the kernel owns the transport machinery.

## Socket Buffers and Backpressure

Sockets separate application execution from network timing with kernel-managed buffering and queueing. A receive buffer lets the kernel retain data that has arrived from the network but has not yet been consumed by the application. Send-side state retains data the application has submitted but that has not yet progressed far enough through the transport stack to be discarded.

These buffers are finite. If an application reads too slowly, receive-side pressure grows. For TCP, that pressure participates in flow control because the receiver cannot advertise unlimited capacity to its peer. If the local application writes faster than the kernel and peer can drain outgoing data, send-side capacity fills; a blocking `send()` may then sleep, while a non-blocking call can return `EAGAIN` or `EWOULDBLOCK`.

This is **backpressure**: inability to make progress at one stage eventually becomes visible to the previous stage instead of allowing memory usage to grow without bound. Because every active socket consumes kernel state and potentially buffer memory, very large connection counts are also a memory-management concern.

> [!example] Inspecting Socket Queues with `ss`
> On Linux, `ss` exposes parts of the kernel's socket state. For an established TCP socket, `Recv-Q` can show data waiting for the application to read, while `Send-Q` can show data that has not yet completed the relevant send/acknowledgment progress. For a listening socket, the same columns describe listening/backlog state instead. The operational interpretation is covered in [Troubleshooting Performance](../Backend%20Engineering/03%20Troubleshooting%20Performance.md).

## Blocking and Non-Blocking Sockets

Blocking mode asks the kernel to suspend the calling thread when an operation cannot currently make useful progress. Examples include `accept()` with no completed connection, `recv()` with no available data, or `send()` when local send capacity is exhausted.

A non-blocking socket changes that contract. The system call returns immediately and reports that progress is currently unavailable, commonly through `EAGAIN` or `EWOULDBLOCK`. The application can do other work and retry later.

Repeatedly retrying every socket in a busy loop would waste CPU, however. Efficient high-concurrency applications therefore combine non-blocking sockets with a readiness-notification mechanism that tells them which descriptors are worth trying again.

## Readiness Notification

The kernel already knows whether a socket currently has data to read, room to accept writes, a completed connection to accept, or an error condition. Readiness interfaces let user space wait for changes in that state across many descriptors instead of dedicating one blocked OS thread to each connection.

POSIX provides interfaces such as `select()` and `poll()` for waiting on descriptor readiness. Operating systems also provide implementation-specific scalable facilities: Linux provides `epoll`, while BSD-derived systems provide `kqueue`. Their registration and wakeup semantics differ, but the common idea is the same: user space registers interest in descriptors, sleeps until relevant state changes, and then performs the actual I/O system calls on the descriptors reported as ready.

Readiness does not transfer application data by itself. For example, `epoll_wait()` can report that a socket is readable, but the application still calls `read()` or `recv()` to consume the bytes. Races and edge-triggered modes also mean a supposedly ready operation must still be written to handle cases where no progress is available by the time the application acts.

> [!example] Go's Netpoller
> Go allows a goroutine to perform what looks like a blocking network operation without requiring one OS thread to remain blocked for every socket. The runtime can park the goroutine and use the operating system's readiness facilities to learn when the descriptor can make progress. On Linux, Go's netpoller uses mechanisms such as `epoll`; when readiness arrives, the runtime can make the corresponding goroutine runnable again. This is a runtime abstraction built on top of the OS socket and scheduler primitives, as discussed in [Go Internals](../Technologies/Golang/99%20Misc/Go%20Internals.md#Handling%20I/O%20Blocking%20%28The%20Netpoller%29).

## Socket Lifetime and Closure

`close(fd)` removes that descriptor's reference to the open socket resource. If no other descriptor or kernel reference keeps the resource alive, the kernel can release the socket object and its associated memory. Duplicated descriptors and descriptors inherited by child processes therefore affect when the final release actually occurs.

For connected stream sockets, descriptor lifetime and transport shutdown are related but not identical concepts. `shutdown()` can disable reads, writes, or both on an existing socket without necessarily releasing the descriptor. A write-side shutdown can express that the application will send no more bytes while still allowing it to receive, which exposes TCP's bidirectional connection as two independently closable byte directions.

The transport protocol determines how that intent appears on the network. TCP may use `FIN` for orderly half-close and `RST` for certain abortive cases, but those wire-level state transitions belong to the TCP lifecycle rather than the generic descriptor model.

## Sharing and Distributing Listening Sockets

The socket abstraction allows several execution units to participate in connection acceptance, but there are two importantly different mechanisms: sharing one listener and creating several independent listeners.

### Shared Listening Socket

Threads in one process naturally share the process's descriptor table, so several threads can call `accept()` on the same listening socket. Related processes can also share a listening socket through descriptor inheritance or explicit descriptor-passing mechanisms.

When several execution units wait on one listener, the kernel coordinates which waiter receives an available connection. Poor wakeup strategies can cause a **thundering herd**, where several workers wake for work that only one can claim. Modern kernels and server designs contain mechanisms to reduce this waste, but the architectural concern comes from contention around one shared listening resource.

### Multiple Listeners with `SO_REUSEPORT`

Some operating systems provide `SO_REUSEPORT`, allowing multiple independent sockets to bind compatible copies of the same local address and port. Instead of several workers contending on one socket object, each worker can own its own listener and associated queue state, while the kernel distributes incoming traffic among the group.

The distribution policy is an OS implementation detail and is based on transport/network information rather than application-level workload. A connection that later carries many requests can therefore create more application work than another connection even if the kernel initially distributed the connections evenly.

> [!example] NGINX Socket Sharding
> NGINX can use `SO_REUSEPORT` so multiple worker processes each own an independent listening socket bound to the same address and port. The kernel distributes incoming connections among those listeners, reducing contention around a single shared accept path. The NGINX-specific architecture builds on the generic OS primitive described here.