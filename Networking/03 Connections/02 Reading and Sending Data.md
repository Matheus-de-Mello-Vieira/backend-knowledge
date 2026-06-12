# Reading and sending data

This note covers what happens after a TCP connection is already established and the backend process has a connected socket. For the handshake, SYN queue, accept queue, and `accept()` handoff, see [How Connections are Established](01%20How%20Connections%20are%20Established.md). For TCP segment structure, flags, and protocol guarantees, see [TCP](../02%20Protocols/05%20TCP.md).

Once a connection is established, the OS creates two separate memory buffers: one for sending data and one for receiving data. The receive buffer specifically handles incoming client data, while the send buffer handles outbound server data.
## Receiving data

Here is the exact lifecycle of how incoming data moves from the network into your application:

1. **Data Arrival:** The client transmits data over the established connection.
2. **Kernel Interception:** The Kernel automatically receives the data and places it directly into the OS receive buffer. This happens autonomously in the background, entirely without the backend application asking for it.
3. **ACKs and Flow Control:** The Kernel is responsible for acknowledging the received data to the client. [See more](05%20TCP.md#1.%20Flow%20Control%20(Receiver-Driven)).
4. **The User-Space Copy:** The backend application must call a function to copy the data out of the Kernel's buffer and into its own memory space. Because crossing the user/kernel boundary requires memory copying, this operation is computationally expensive.
    - The process can use `read()` (a general-purpose system call for any file descriptor, including sockets) or `recv()` (a socket-specific call that provides extra options).
    - **Blocking Mode:** By default, sockets are blocking, meaning `read()` or `recv()` will completely pause the process until data physically arrives.
    - **Non-Blocking Mode:** If configured differently, both calls return immediately. If there is no data in the buffer, they throw an error like `EAGAIN` or `EWOULDBLOCK`.
    - **Event Polling:** To efficiently manage multiple connections, applications use functions like `epoll_wait()`, which allows the process to wait until the Kernel explicitly notifies it that data is available on one of its monitored connections.
5. **Buffer Cleanup:** Once the data is successfully copied to the application's memory, the Kernel actively discards that duplicated data from the receive buffer to free up space for new traffic.
6. **Application Processing:** The backend process now has the raw data safely in User Space and can proceed to decrypt, parse, and process the payload.
### Sockstress

**Sockstress** is a category of low-bandwidth, asymmetric Denial of Service (DoS) attacks that target TCP’s flow-control architecture. Instead of overwhelming a server with brute-force volumetric traffic, an attacker abuses the receiver-driven **Receive Window ($rwnd$)** mechanics to permanently trap critical server-side kernel memory buffers.

As detailed in the [Flow Control](05%20TCP.md#1.%20Flow%20Control%20(Receiver-Driven)) section, the TCP specification requires a sender to strictly respect the receiver's advertised window size. Because the protocol assumes both endpoints will cooperate in good faith to clear data buffers, the TCP stack lacks a native architectural mechanism to distinguish a legitimately slow client from a malicious one.

> [!NOTE] **Window Stall** 
> While **Sockstress** describes the malicious exploit, a **Window Stall** is the official structural state the TCP engine enters during the attack. A connection is "stalled" whenever a sender is fully blocked from transmitting because the receiver's advertised window ($rwnd$) has choked the effective transmission window down to zero.

#### Zero-Window Attacks

The most straightforward variant of Sockstress relies on freezing transmission entirely by closing the window completely.
```mermaid
sequenceDiagram
    participant Attacker
    participant Target as Target Server

    Attacker->>Target: 1. Establishes TCP Connection
    Note over Attacker,Target: Standard TCP handshake

    Attacker->>Target: 2. Sends Application Request (HTTP GET)
    Target->>Target: Server processes request

    Target-->>Attacker: 3. Attempts response
    Attacker-->>Target: Advertises Window Size = 0

    Note over Attacker: Refuses to read payload
    Note over Target: Response data trapped in send buffer

    loop While rwnd remains 0
        Target-->>Attacker: Periodic Window Probe
        Attacker-->>Target: Replies with Window Size = 0
        Note over Target: Send buffer remains occupied
    end
```

- **The Mechanism:** The attacker opens a standard TCP connection and sends a legitimate request demanding a large payload response (e.g., an HTTP `GET` for a large file or an intense database query).
- **The Freeze:** Once the server processes the request and moves the payload into its **OS Send Buffer**, the attacker deliberately locks its application socket, refuses to call `read()` or `recv()`, and explicitly advertises a $Window Size = 0$ ($rwnd = 0$).
- **Memory Entrapment:** The response data becomes trapped in the server's kernel memory. The server must keep the data cached while periodically transmitting 1-byte **Window Probes** to check the attacker's status. The attacker simply replies to every probe with $rwnd = 0$, holding the connection open indefinitely.

#### Small-Window Attacks

If a server implements basic security timers that automatically drop connections that remain at $rwnd = 0$ for too long, attackers use a highly effective workaround: the **Small-Window Attack**.

```mermaid
sequenceDiagram
    participant Attacker
    participant Target as Target Server

    Attacker->>Target: 1. Requests large file
    Target->>Target: Server puts data in send buffer

    Attacker-->>Target: 2. Advertises rwnd = 1 Byte

    loop Repeated tiny-window cycle
        Target-->>Attacker: Sends 1 Byte Payload
        Target->>Target: Drains 1 byte from buffer
        Attacker-->>Target: Instantly advertises rwnd = 1 Byte
        Note over Target: Server remains effectively trapped
    end
```

- **The Mechanism:** Instead of completely closing the window, the attacker advertises a tiny, absurd window size, such as **$rwnd = 1$ byte**.
- **Bypassing the Timers:** Because the window is technically non-zero, standard zero-window protection timers are never tripped. The server views this as a slow, legitimate client making progress.
- **The Trickle:** The server transmits exactly 1 byte of data, drains 1 byte from its send buffer, and is forced to immediately halt again until the attacker sends another 1-byte window update. This effectively trickles data out over hours, keeping the server's connection slots and memory buffers locked just as effectively as the zero-window method.

#### Operational Impact

- **Kernel Buffer Exhaustion:** By launching thousands of these deadlocked or trickling connections simultaneously, an attacker can completely fill the server's connection tables (`connection slots`) and exhaust the kernel RAM allocated for global TCP send buffers.
- **Stealth and Asymmetry:** Sockstress generates almost no incoming bandwidth traffic. Traditional volumetric firewalls and [Intrusion Detection System (IDS)](Intrusion%20Detection%20and%20Prevention.md#Intrusion%20Detection%20System%20(IDS)) often miss it entirely because the attacker's packets look like perfectly compliant, standard TCP flow-control adjustments.
#### Modern Mitigations

Because basic timers are easily bypassed by window dithering, modern operating systems and reverse proxies utilize advanced behavioral defenses:

- **Minimum Throughput Thresholds:** Rather than checking if a window is exactly zero, modern network stacks track the actual _throughput pacing_ of the socket. If a connection is transferring data below a minimum threshold (e.g., less than 50 bytes/second over a set period), the system marks it as anomalous and drops the socket.
- **Dynamic Socket Buffer Shrinking:** If a client drops its $rwnd$ to a suspiciously small size, advanced Linux kernel TCP auto-tuning features will dynamically shrink the maximum kernel buffer size allocated to that specific socket. This limits the total amount of RAM a single attacker can trap.
- **Connection Rate and State Limits:** Firewalls and Reverse Proxies (such as Nginx or cloud load balancers) are configured to strictly limit the maximum number of concurrent connections allowed per individual source IP, preventing a single attacker from exhausting the global socket table. 
## Send buffers

1. **The `send()` Call:** The backend process initiates the outbound transfer by calling `send()`. This action copies the payload data from the application's memory directly into the Kernel's send buffer.
- **Kernel Dispatch & Efficiency:** Once the data is in the send buffer, the Kernel does not always transmit it immediately; it may wait until it has accumulated enough information to dispatch it efficiently to the client. For example, [Nagle's algorithm](03%20Nagle's%20algorithm.md) intentionally delays transmission until the data reaches the maximum segment size to optimize network efficiency.
- **Transmission and ACKs:** The Kernel begins transmitting the data across the network. As long as the client continues to acknowledge (ACK) the receipt of the data, the Kernel will proceed to send the rest of the data from the buffer to the client.

## Nagle's Algorithm

- **The Problem It Solves:** In the early days of the internet (such as the Telnet era), sending a single byte of data per packet was incredibly inefficient. Every TCP/IP packet requires a 40-byte header (20 bytes for IP + 20 bytes for TCP). Sending 1 byte of payload meant transmitting 41 bytes total—a massive waste of bandwidth.
- **The Solution:** Nagle's algorithm was introduced to combine small segments of data and send them together in a single packet, preventing this overhead waste.
### How It Works

- The algorithm dictates that if a process has small chunks of data to send, the Kernel must hold that data in the send buffer until one of two conditions is met:
    1. The accumulated data reaches the [MSS](#Maximum%20Segment%20Size%20(MSS)) (e.g., 1460 bytes).
    2. There is no unacknowledged data in flight (i.e., if the client has already ACKed all previous packets, the new data will be sent immediately, regardless of size).
- **Example:** If the [MSS](#Maximum%20Segment%20Size%20(MSS)) is 1460 bytes and the application sends 500 bytes, the algorithm holds it. If the application then sends another 1000 bytes, the buffer hits 1500 bytes. The Kernel immediately sends out one full 1460-byte segment and holds the remaining 40 bytes.

### The Problem (Non-Deterministic Tail Delays)

- While Nagle's algorithm saves bandwidth, it introduces non-deterministic delays.
- **The Tail-End Delay:** This delay is especially noticeable when sending large amounts of data that do not perfectly divide into the MSS.
- **Example:** If an application wants to send 5000 bytes over a connection with a 1440-byte [MSS](#Maximum%20Segment%20Size%20(MSS)):
    - The Kernel immediately sends 3 full segments (1440 bytes × 3 = 4320 bytes).
    - The 4th segment contains the remaining 680 bytes. Because it is not a full segment, and the previous segments have not yet been ACKed, Nagle's algorithm pauses and refuses to send the 4th segment until the ACK for the earlier data arrives.

```mermaid
sequenceDiagram
    participant A
    participant B

    A->>B: 1460 bytes
    A->>B: 1460 bytes
    A->>B: 1460 bytes
    
    Note over A: Nagle's algorithm delays further small sends<br/>waiting for ACK
    
    B-->>A: ACK
    A->>B: 620 bytes
```

### Disabling Nagle's Algorithm

- **Prioritizing Latency over Bandwidth:** Because modern applications (like APIs, gaming, and real-time systems) prioritize fast response times over saving a few bytes of network capacity, most clients and servers explicitly disable Nagle's algorithm.
- **`TCP_NODELAY`:** This is the socket option used to disable the algorithm, instructing the Kernel to send data immediately, regardless of segment size.
- **The cURL Example:** The popular `curl` utility disabled Nagle's algorithm by default back in 2016 because the artificial delays were severely slowing down TLS handshakes.

> After a few wasted hours hunting down the reason for slowness during a TLS handshake that turned out to be because of `TCP_NODELAY` not being set, I think we have enough motivation to toggle the default for this option. We now enable `TCP_NODELAY` by default and allow applications to switch it off.
> 
> This also makes `--tcp-nodelay` unnecessary, but `--no-tcp-nodelay` can be used to disable it.
> 
> Thanks-to: Tim Rühsen
> 
> Bug: [https://curl.haxx.se/mail/lib-2016-06/0143.html](https://curl.haxx.se/mail/lib-2016-06/0143.html)
