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

## Demo

A local loopback exchange exposes UDP as a sequence of independent datagrams, not a connection with an accepted socket for each peer. The following C fragments use the [POSIX socket interface](../../Operating%20Systems/07%20Socket%20Management.md#POSIX%20Socket%20Interface). Error handling and headers are omitted so that each fragment centers the UDP behavior it causes.

### IPv4 Endpoint Representation

The receiver and sender construct the destination `127.0.0.1:5501` before passing it to a socket operation.

- **`AF_INET`:** Selects the IPv4 address family. `AF_INET6` selects IPv6 instead.
- **`SOCK_DGRAM`:** Selects message-oriented datagram semantics. With `AF_INET`, protocol `0` selects the normal protocol for that type: UDP.
- **`struct sockaddr_in`:** Stores an IPv4 socket address. `{0}` initializes every field to zero before the required fields are set.
    - **`sin_family`:** Must name the same address family as the socket.
    - **`sin_port`:** Stores the transport port in network byte order.
    - **`sin_addr`:** Stores the IPv4 address in binary form.
- **`htons(5501)`:** Converts the 16-bit port from the host's byte order to network byte order, which uses big-endian byte order. `ntohs()` performs the reverse conversion when displaying a received port.
- **`inet_pton(AF_INET, "127.0.0.1", &receiver.sin_addr)`:** Converts an IPv4 address from presentation text into the binary form required by `sin_addr`. It returns `1` on success, `0` when the text is not a valid address for that family, and `-1` for an unsupported family.
- **`inet_ntop()`:** Converts a binary address such as `sender.sin_addr` back into presentation text for logging or display.
- **`(struct sockaddr *)&receiver` and `sizeof(receiver)`:** `bind()` and `sendto()` accept the generic `struct sockaddr` interface because they support several address families. The cast presents the IPv4-specific structure through that interface, and the size tells the kernel how many bytes the actual address structure occupies.

### Receiver Binds a Datagram Endpoint

The receiver binds one datagram socket to the stable local endpoint. Unlike a TCP listener, this socket does not enter a listening state and does not create a new socket when traffic arrives.

```c
int receiver_fd = socket(AF_INET, SOCK_DGRAM, 0);

struct sockaddr_in receiver = {0};
receiver.sin_family = AF_INET;
receiver.sin_port = htons(5501);
inet_pton(AF_INET, "127.0.0.1", &receiver.sin_addr);

bind(receiver_fd, (struct sockaddr *)&receiver, sizeof(receiver));
```

### Sender Transmits Without a Handshake

The sender supplies the destination to `sendto()`. It does not call `connect()`, `listen()`, or `accept()`. Because it has not bound a local endpoint explicitly, the kernel selects a suitable local address and ephemeral source port when it sends the datagram.

```c
int sender_fd = socket(AF_INET, SOCK_DGRAM, 0);

struct sockaddr_in receiver = {0};
receiver.sin_family = AF_INET;
receiver.sin_port = htons(5501);
inet_pton(AF_INET, "127.0.0.1", &receiver.sin_addr);

sendto(
    sender_fd,
    "hello from sender",
    strlen("hello from sender"),
    0,
    (struct sockaddr *)&receiver,
    sizeof(receiver)
);
```

One successful `sendto()` submits one datagram. It does not acknowledge delivery, establish peer state, or guarantee that the receiver will obtain the datagram.
`strlen()` supplies the byte count of the text payload without its terminating `\0` byte.

### Receiver Obtains One Datagram and Its Source Endpoint

`recvfrom()` removes one datagram from `receiver_fd` and records the source endpoint associated with that datagram. `sender_size` initially states the available address-storage size; after the call, it states the size of the source address written into `sender`.

```c
char datagram[257];
struct sockaddr_in sender = {0};
socklen_t sender_size = sizeof(sender);

ssize_t datagram_bytes = recvfrom(
    receiver_fd,
    datagram,
    sizeof(datagram) - 1,
    0,
    (struct sockaddr *)&sender,
    &sender_size
);
datagram[datagram_bytes] = '\0';
```

`datagram` is user-space memory, and `datagram_bytes` is the number of payload bytes copied. The assignment of `\0` assumes the successful result represented by this simplified fragment; production code checks for a negative return before indexing the buffer. The extra byte only makes this text example printable as a C string; UDP does not append a string terminator. If the supplied payload buffer is too small, the datagram is truncated rather than continued by a later `recvfrom()` call. A later receive obtains a later datagram, which may have come from a different source endpoint.

### Reply as Another Datagram

The receiver can use the source address returned by `recvfrom()` as the destination of a reply. This is a new datagram, not a response over an accepted or transport-connected socket.

```c
sendto(
    receiver_fd,
    "hello from receiver",
    strlen("hello from receiver"),
    0,
    (struct sockaddr *)&sender,
    sender_size
);

char reply[257];
ssize_t reply_bytes = recvfrom(
    sender_fd,
    reply,
    sizeof(reply) - 1,
    0,
    NULL,
    NULL
);
reply[reply_bytes] = '\0';
```

The sender's `recvfrom()` ignores the reply's source address by passing `NULL` for both address arguments. Supplying address storage instead would let it identify the sender of every received datagram. Neither socket becomes dedicated to one peer: the receiver can accept later datagrams from other IP/port pairs through the same `receiver_fd`.

### Closure

Each process closes its own descriptor when it has finished with the socket.

```c
close(sender_fd);    // sender process
close(receiver_fd);  // receiver process
```

Closing a UDP descriptor releases that process's reference according to the usual [descriptor lifetime](../../Operating%20Systems/07%20Socket%20Management.md#Socket%20Lifetime%20and%20Closure) rules. It does not perform TCP-style connection termination because no TCP-style transport connection exists.
