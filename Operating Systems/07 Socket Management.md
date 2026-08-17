# Socket Management

Socket management is how the operating system exposes network communication to user-space programs. The kernel owns the actual TCP/UDP machinery; user space interacts with it through file descriptors, system calls, and kernel-managed buffers.

## Sockets as file descriptors

Network sockets are one important kind of [file descriptor](02%20The%20Anatomy%20of%20a%20Process.md#File%20Descriptors%20%28FDs%29). The kernel exposes a socket to user space as an FD, but the underlying kernel object stores network-specific state such as protocol, local and remote addresses, ports, send buffers, receive buffers, and connection state.


## What socket management adds

- **Creation:** A process calls `socket()` to ask the kernel for a new socket-backed FD.
- **Binding:** The socket can be associated with a local IP address and port.
- **Listening and accepting:** Server processes use `listen()` and `accept()` to turn a passive listening socket into active connected sockets.
- **Buffer management:** The kernel owns the receive and send buffers and decides when reads, writes, and wakeups become possible.
- **Readiness notification:** Polling systems such as `epoll` let a process monitor many socket FDs efficiently without blocking one thread per connection.
