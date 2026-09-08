# User Datagram Protocol

UDP (User Datagram Protocol) is a Layer 4 transport protocol that sends discrete messages called **datagrams**. Unlike [TCP](05%20TCP.md), UDP does not establish a transport connection before application data is sent and does not provide reliability, ordering, flow control, or congestion control by itself.

The operating system normally exposes UDP through a [datagram socket](../../Operating%20Systems/07%20Socket%20Management.md#Datagram%20Sockets). Socket creation and binding establish the local endpoint, the kernel demultiplexes incoming datagrams to that socket, and kernel buffers plus blocking or non-blocking I/O determine when the application can send or receive them.

## Core Properties

UDP has a deliberately small transport contract:

- **Message-Oriented Transport:** Each application send corresponds to one UDP datagram, and the receiver observes datagram boundaries.
- **Connectionless Operation:** No TCP-style handshake is required before sending a datagram.
- **Best-Effort Delivery:** UDP does not acknowledge delivery or retransmit lost datagrams.
- **No Ordering Guarantee:** Datagrams may arrive in a different order from the one in which they were sent.
- **No Built-In Flow Control:** UDP does not make a sender slow down because the receiving application is consuming data slowly.
- **No Built-In Congestion Control:** Applications or higher-level protocols must provide appropriate congestion behavior when necessary.
- **Small Header:** The UDP header is 8 bytes.
- **Transport State Meaning:** Calling UDP "stateless" refers to the absence of TCP-style per-connection transport state.
  - The operating system still maintains a UDP socket object, queues received datagrams, and tracks binding information.
  - Applications can also maintain arbitrary peer or session state above UDP.

## Ports and Demultiplexing

[IP](03%20Internet%20Protocol.md#Internet%20Protocol) routes packets between network endpoints, while UDP adds 16-bit source and destination ports.

- **Port Width:** UDP source and destination ports are 16-bit values ranging from `0` to `65535`.
- **Kernel Demultiplexing:** The receiving kernel uses the protocol and local addressing information to [demultiplex](../../Operating%20Systems/07%20Socket%20Management.md#Addressing,%20Ports,%20and%20Demultiplexing) an incoming datagram to an appropriate UDP socket.
- **No Hard Peer Limit from Port Count:** The 65,536 possible port values are **not** a hard limit on the number of remote peers a UDP server can communicate with.
  - One bound UDP socket can receive datagrams from many different source IP/port pairs because UDP does not create a new accepted socket for each peer.
- **Source Port:** The source port gives the receiver an address to which it can direct a response.
- **Application Correlation:** Application protocols commonly add their own identifiers when they need to match requests with responses.
  - DNS, for example, includes a transaction ID because multiple queries can be in flight independently.

> [!note] UDP `connect()` Does Not Create a Transport Connection
> A UDP application can call [`connect()`](../../Operating%20Systems/07%20Socket%20Management.md#Establishing%20Outbound%20Connections) to record a default peer and restrict which peer is accepted by the socket API. No TCP-style handshake occurs, and UDP does not gain TCP-style per-connection transport state.

## UDP Datagram

A UDP header contains four 16-bit fields:

```mermaid
packet-beta
title UDP Datagram (32-bit width)
0-15: "Source Port (16 bits)"
16-31: "Destination Port (16 bits)"
32-47: "Length (16 bits)"
48-63: "Checksum (16 bits)"
64-95: "Data / Payload (Variable Length)"
```

- **Source Port:** Identifies the sender's transport endpoint; it may be zero in cases where no response port is supplied.
- **Destination Port:** Identifies the target UDP endpoint on the destination host.
- **Length:** Stores the total UDP datagram length, including the 8-byte header.
- **Checksum:** Provides an integrity check over the UDP datagram plus information from the IP layer.

> [!note] UDP Datagram Boundaries vs. IP Packets
> The UDP datagram becomes payload for IP, but one datagram does **not** necessarily correspond to exactly one IP packet.
>
> - **IPv4 Fragmentation:** A sufficiently large datagram can be split through IP fragmentation.
> - **IPv6 Fragmentation:** IPv6 relies on endpoint fragmentation rather than router fragmentation.
> - **Operational Consequence:** Applications generally avoid depending on fragmentation because losing one fragment prevents reconstruction of the complete datagram.

## Reliability Above UDP

UDP deliberately leaves several transport guarantees to higher layers.

- **Not Provided by UDP:** Packet-loss recovery, duplication handling, reordering, retransmission, session establishment, and congestion control are not built into the protocol.
- **Application Responsibility:** An application that needs any of those properties must implement them itself or use a protocol built above UDP.
- **Workload-Specific Guarantees:** This does not mean every UDP application should recreate TCP.
  - Real-time media may prefer to discard late data rather than retransmit it.
  - [QUIC](10%20HTTP3.md#HTTP%2F3) builds reliable multiplexed streams, congestion control, and cryptographic connection state above UDP because it needs substantially stronger semantics.

## Use Cases

### DNS

- **Common Transport:** Classic DNS commonly uses UDP for requests that fit its transport requirements.
- **Response Matching:** A client uses the DNS transaction ID together with endpoint information to match a response with its query.
- **Alternative Transports:** DNS can also use TCP when required, and modern encrypted DNS transports introduce additional protocol layers.

### Real-Time Media

- **Timeliness Priority:** Interactive voice and video frequently prefer timeliness over perfect retransmission.
- **Late Data:** A packet arriving too late may be less useful than a missing packet.
- **Higher-Level Mechanisms:** Protocols built for real-time media can use UDP while implementing their own loss handling, jitter buffering, pacing, and congestion behavior.

### VPNs and Tunnels

- **TCP-over-TCP Risk:** Many VPN transports use UDP because tunneling TCP inside another TCP connection can produce interacting reliability and congestion-control loops known as **TCP-over-TCP meltdown**.
- **UDP Tunnel:** A UDP-based tunnel can preserve the inner transport's behavior while the tunnel implements the security, replay protection, path management, or reliability properties it actually needs.
- **Direct IP Tunneling:** Some tunneling protocols encapsulate IP directly rather than using TCP or UDP.
- **NAT and Firewall Behavior:** NATs and stateful firewalls often handle port-based TCP/UDP traffic more naturally because ports provide convenient session-identification information.

## Advantages and Trade-offs

UDP's simplicity reduces transport overhead and avoids connection-establishment latency, but the missing mechanisms become the application's responsibility when they are required.

### Advantages

- **No Transport Handshake:** Data can be sent without first establishing a transport connection.
- **Small Header:** The transport header has a fixed 8-byte size.
- **Preserved Message Boundaries:** The receiver observes discrete datagrams rather than a byte stream.
- **Application Control:** Applications can choose their own reliability and timing trade-offs.
- **Protocol Foundation:** UDP is useful as a base for protocols such as DNS, real-time media transports, and QUIC.

### Trade-offs

- **Delivery:** No delivery guarantee.
- **Ordering:** No ordering guarantee.
- **Retransmission:** No built-in retransmission.
- **Flow Control:** No transport-level flow control.
- **Congestion Control:** No transport-level congestion control.
- **Source Spoofing:** Source addresses are easier to spoof than in protocols that require a bidirectional handshake before meaningful state is established.

## Datagram Receive Semantics

`recvfrom()` exposes two important UDP properties at the application interface: preserved datagram boundaries and sender addressing. Given an already-bound [datagram socket](../../Operating%20Systems/07%20Socket%20Management.md#Datagram%20Sockets), a receive can look like:

```c
char buffer[1024];
struct sockaddr_in remote = {0};
socklen_t remote_size = sizeof(remote);

ssize_t n = recvfrom(
    sockfd,
    buffer,
    sizeof(buffer),
    0,
    (struct sockaddr *)&remote,
    &remote_size
);
```

- **One Call, One Datagram:** `recvfrom()` consumes one received datagram rather than exposing a continuous TCP-style byte stream.
- **Sender Address:** The call can also return the source address associated with that datagram.
- **Many Peers, One Socket:** This fits UDP's peer model: one bound datagram socket can receive messages from many remote endpoints without calling `accept()` for each peer.
