# How Connections are Established

A TCP connection is established cooperatively by the two transport endpoints before application data can flow. This note focuses on the network-visible TCP handshake and its consequences. The operating-system mechanisms that create listening sockets, maintain pending connections, and expose completed connections through `accept()` are covered in [Socket Management](../../Operating%20Systems/07%20Socket%20Management.md#Listening%20and%20Accepting).

## TCP Three-Way Handshake

A new [TCP connection](../02%20Protocols/05%20TCP.md#Connection-oriented%20transport) begins with three steps:

1. **Client → Server (`SYN`):** The client requests a new connection and communicates its initial sequence information.
2. **Server → Client (`SYN-ACK`):** The server acknowledges the client's synchronization request and supplies its own synchronization information.
3. **Client → Server (`ACK`):** The client acknowledges the server's response. Both endpoints now have enough state to treat the connection as established.

- **Kernel Responsibility:** The application normally does not construct or consume these packets itself. A kernel TCP implementation processes the handshake and maintains the corresponding transport state.
- **Application Handoff:** On the server, a completed connection eventually becomes available to user space through the [listening and accepting](../../Operating%20Systems/07%20Socket%20Management.md#Listening%20and%20Accepting) socket lifecycle.

## Connection Identity

A TCP connection is identified by the pair of endpoints, commonly represented as the four-tuple:

- **Source IP:** Network address of the sending endpoint.
- **Source Port:** Transport port of the sending endpoint.
- **Destination IP:** Network address of the receiving endpoint.
- **Destination Port:** Transport port of the receiving endpoint.

- **Shared Server Port:** One server port can participate in many simultaneous TCP connections.
  - Several clients may all connect to port `443`, for example, while their source addresses or source ports make each established connection distinct.
- **Kernel Demultiplexing:** The kernel uses this transport identity when [demultiplexing](../../Operating%20Systems/07%20Socket%20Management.md#Addressing,%20Ports,%20and%20Demultiplexing) incoming segments to the correct connected socket.

## Kernel State During Establishment

Network establishment and application acceptance are separate stages.

- **Incomplete Handshake State:** While the handshake is incomplete, the server must retain enough state to continue or validate the establishment attempt.
- **Completed Connection State:** Once the handshake succeeds, the completed connection may wait until the application accepts it.
- **OS-Specific Queues:** The exact queue structures, sizes, and overflow policies are operating-system implementation details.
  - Linux is commonly described in terms of SYN-related state and a separate accept queue.
- **Handshake Before `accept()`:** A client can finish the TCP handshake before the server application calls `accept()`.
- **Kernel Ownership:** The kernel owns the connection during that interval and exposes it when the application is ready to claim a connected socket.

> [!warning] SYN Flood
> A SYN flood is a denial-of-service attack that targets the connection-establishment phase. The attacker sends many `SYN` packets but does not complete the handshake, forcing the server or an intermediate stateful device to retain pending state until limits are reached.
>
> - **Defenses:** SYN cookies, SYN proxying, rate limiting, and state-management techniques implemented by operating systems and [firewall technologies](../../Security/05%20Architecture%20and%20Infrastructure%20Security/Network%20Security/Firewall%20Technologies.md#Fourth%20Generation%20and%20Beyond:%20Next-Generation%20Firewalls%20%28NGFW%29%20%282000s%20to%20Present%29).
> - **Different from Slow Acceptance:** The attack is distinct from an application that merely accepts connections too slowly.
>   - In both cases kernel connection state can become a constrained resource.
>   - A SYN flood attacks incomplete handshake state, while slow application acceptance creates pressure around completed connections waiting for the application.
