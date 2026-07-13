# Socket Management

Socket management is how the operating system exposes network communication to user-space programs. The kernel owns the actual TCP/UDP machinery; user space interacts with it through file descriptors, system calls, and kernel-managed buffers.

For the TCP handshake and `accept()` handoff, see [How connections are Established](../Networking/03%20Connections/01%20How%20connections%20are%20Established.md). For receive buffers, send buffers, and blocking reads, see [Reading and sending data](../Networking/03%20Connections/02%20Reading%20and%20Sending%20Data.md).

## Sockets as file descriptors

Network sockets are one important kind of file descriptor. The kernel exposes a socket to user space as an FD, but the underlying kernel object stores network-specific state such as protocol, local and remote addresses, ports, send buffers, receive buffers, and connection state.

For the broader FD abstraction across files, standard streams, pipes, devices, and event monitors, see [File Descriptors](02%20The%20Anatomy%20of%20a%20Process.md#File%20Descriptors%20(FDs)).

## What socket management adds

- **Creation:** A process calls `socket()` to ask the kernel for a new socket-backed FD.
- **Binding:** The socket can be associated with a local IP address and port.
- **Listening and accepting:** Server processes use `listen()` and `accept()` to turn a passive listening socket into active connected sockets.
- **Buffer management:** The kernel owns the receive and send buffers and decides when reads, writes, and wakeups become possible.
- **Readiness notification:** Polling systems such as `epoll` let a process monitor many socket FDs efficiently without blocking one thread per connection.
