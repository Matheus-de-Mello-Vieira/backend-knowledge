# How connections are Established

- **The TCP 3-Way Handshake (Network Perspective):** To establish a reliable connection, the client and server must exchange three specific packets.
    - **Client → Server (`SYN`):** The client requests to synchronize and open a connection.
    - **Server → Client (`SYN-ACK`):** The server acknowledges the request and synchronizes its own connection state.
    - **Client → Server (`ACK`):** The client acknowledges the server's response, finalizing the connection.
- **Server Binding (Backend Perspective):** Before any handshake can occur, a backend application must tell the OS kernel that it is ready to receive traffic.
    - **Listening on an Address and Port:** The server process explicitly binds to an `IP_Address:Port` combination.
    - **Network Interfaces:** A single physical computer often has multiple network interfaces (e.g., Ethernet, Wi-Fi, Localhost/Loopback), and every interface is assigned its own unique IP address. The IP you choose to listen on dictates which specific network can reach your application.
- **The Kernel-to-Process Handoff:**
    - **Kernel Autonomy:** The OS kernel completely manages the TCP 3-way handshake in the background (within Kernel Space). The backend application code is entirely unaware this negotiation is happening.
    - **The `accept()` System Call:** Once the kernel finishes the handshake, it places the fully established connection into a backlog queue. The backend process then issues an `accept()` system call, which generates a file descriptor in User Space. This file descriptor is what grants your application the direct ability to read and write data to that specific client connection.

> [!warning] The `0.0.0.0` (Wildcard) Security Risk
> Binding to `0.0.0.0` tells the kernel to listen on _all_ available network interfaces simultaneously. This is a severe security risk if done unintentionally. It exposes your API or database to every network the machine is connected to, potentially allowing public internet access to an application meant only for internal use. Binding to a specific IP (like `127.0.0.1` for localhost) safely restricts access.

#### SYN flood

A SYN flood is a denial-of-service attack that abuses the TCP handshake. The attacker sends many `SYN` packets but does not finish the handshake with the final `ACK`, forcing the server or firewall to keep half-open connection state until the `SYN` queue or state table is exhausted.

Modern [Firewall Technologies](../../Security/05%20Architecture%20and%20Infrastructure%20Security/Network%20Security/Firewall%20Technologies.md#Fourth%20Generation%20and%20Beyond:%20Next-Generation%20Firewalls%20%28NGFW%29%20%282000s%20to%20Present%29) can mitigate SYN floods with techniques like SYN proxying, SYN cookies, and hardware acceleration.

## Connection Establishment

- **The Two TCP Queues:** For every listening TCP socket, the kernel maintains two distinct data structures to manage incoming traffic.
- **The SYN Queue:** This queue holds incomplete, pending connections that have started, but not yet finished, the TCP 3-way handshake.
- **The Accept Queue:** This queue holds the fully established connections that have completed the handshake and are waiting for the backend process to claim them via the `accept()` system call.

**Sockets vs. Connections**
- **The Listening Socket:** A socket is the kernel's software endpoint for network communication. A "listening" socket acts as a gateway, bound to an IP and Port, simply waiting for incoming traffic.
- **The Connected Socket:** A single listening socket can spawn multiple connections. When a client finishes the handshake, the kernel creates a completely new, distinct "connected socket" (with its own unique file descriptor) dedicated entirely to that specific client connection. The original listening socket remains open to keep listening.
- **Terminology:** While informally used interchangeably, a "socket" is the structural mechanism, whereas a "connection" is the active, established state between two socket endpoints.

**The Incoming Data Pipeline**

- **Layer 2 (Hardware/NIC):** When physical bytes arrive, the Network Interface Card (NIC) handles the Data Link layer. It receives frames addressed to its MAC address and forwards them into system memory using DMA. Smart NICs with advanced firmware can even offload routing work to save CPU cycles.
- **Layers 3 & 4 (The Kernel Network Stack):** Once in memory, the OS Kernel takes over. The kernel's network stack handles Layer 3 (parsing the IP addresses to ensure it reached the right destination) and Layer 4 (reading the TCP/UDP ports to distribute the data to the correct listening user process).

**High-Performance Networking**

- **CPU Core Dedication:** Processing thousands of network interrupts per second requires immense computational power. On high-performance servers with massive core counts (e.g., 48+ cores), engineers will often dedicate specific CPU cores strictly to networking tasks (like handling NIC interrupts or active polling). This guarantees maximum network throughput while leaving the remaining cores completely isolated for the application's actual workload.

**The Connection Lifecycle**
1. **The Initial Request (`SYN`):** When a client sends a `SYN` packet to initiate a connection, the Kernel intercepts it, adds the pending connection to the **SYN Queue**, and replies to the client with a `SYN-ACK`. 
2. **The Client Acknowledgement (`ACK`):** The client receives the `SYN-ACK` and replies with a final `ACK` packet. The Kernel processes this and finishes establishing the TCP connection.
- **Moving Queues (Removal):** The Kernel removes this now-completed connection from the pending **SYN Queue**.
- **Moving Queues (Addition):** The Kernel immediately places the fully established connection into the **Accept Queue**, where it waits for the backend application.
- **The Backend Handoff (`accept`):** The backend process issues an `accept()` system call to claim the connection, which removes it from the Accept Queue.
    - **Blocking State:** By default, if a backend calls `accept()` while the Accept Queue is empty, the process is blocked (paused) until a new connection arrives. To maintain high performance, modern applications configure this call to be non-blocking or handle it asynchronously.
    - **Queue Saturation:** If the backend processes connections slower than the Kernel receives them, the Accept Queue will fill up. Once full, the Kernel cannot move connections out of the SYN Queue, causing the SYN Queue to eventually fill up as well. When both queues are saturated, new incoming connections are dropped or rejected.
    - **The Reverse Proxy Solution:** This queue saturation bottleneck is the primary problem reverse proxies and API gateways (like Nginx or HAProxy) are designed to solve. Sitting at the network edge, their main job is to execute `accept()` as fast as possible to keep the OS queues empty, hold the active connections, and then safely route them to the slower backend services.
- **File Descriptor Creation:** Upon a successful `accept()`, a unique file descriptor is generated in User Space. This descriptor uniquely identifies the active connection and allows the backend code to finally read and write data to the client.


