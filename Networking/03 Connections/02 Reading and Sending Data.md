# Reading and Sending Data

After a TCP connection is established, the application exchanges a byte stream through a connected socket. The generic operating-system mechanics—kernel send and receive buffers, `read()`/`recv()`, `write()`/`send()`, blocking and non-blocking behavior, backpressure, and readiness polling—are covered in [Socket Management](../../Operating%20Systems/07%20Socket%20Management.md#Receiving%20Data).

This note focuses on behavior that comes specifically from TCP once application bytes have entered the socket abstraction.

## Receiving Data over TCP

The kernel receives TCP segments, validates and reorders the byte ranges when necessary, and exposes an ordered byte stream to the application. TCP packet boundaries are not application message boundaries: the application may receive only part of one logical message or several logical messages in one `recv()`, depending on its own framing protocol and the bytes currently available.

TCP also connects receive-side buffering to **flow control**. As the local application's unread data occupies receive-buffer capacity, the TCP implementation adjusts the receive window (`rwnd`) advertised to the peer. The sender must respect that advertised capacity, as described in [Flow Control](../02%20Protocols/05%20TCP.md#1.%20Flow%20Control%20%28Receiver-Driven%29).

This creates an important dependency between application speed and network progress: if the receiving application stops consuming data, kernel receive capacity becomes constrained and TCP eventually slows or stops the peer rather than allowing receive memory to grow without bound.

## Sending Data over TCP

A successful socket `send()` means that the local kernel accepted some amount of application data; it does not mean that the peer application has received it. The TCP implementation then decides how those bytes are segmented and transmitted while respecting reliability, flow control, and congestion control.

Sent bytes may need to remain represented in kernel state until TCP knows they no longer require retransmission. A slow peer, packet loss, a small advertised receive window, or network congestion can therefore prevent the sender from draining its local send-side state. When that pressure reaches the application, socket writes can block or report that they would block, as described in [Socket Buffers and Backpressure](../../Operating%20Systems/07%20Socket%20Management.md#Socket%20Buffers%20and%20Backpressure).

## Slow or Stalled Receivers

TCP deliberately allows a receiver to slow the sender by advertising a small receive window. This is necessary for normal flow control: a legitimate application may temporarily stop reading because it is busy, descheduled, or processing data more slowly than it arrives.

The same mechanism means that long-lived slow receivers can retain server resources. A server may keep connection state and unsent application data for a client that makes very little progress. At scale, enough such connections can consume descriptors, application memory, and kernel socket-buffer memory even when inbound bandwidth is small.

### Zero-Window State

If the receiver has no available TCP receive-buffer capacity, it may advertise `rwnd = 0`. The sender then stops normal data transmission and uses TCP's persist mechanism to periodically probe for a window update so that a lost update cannot leave the connection deadlocked forever.

A malicious or pathological peer can exploit long-lived zero-window behavior to make a sender retain connection state and pending data. Real systems limit the impact through combinations of kernel timeouts, application deadlines, reverse-proxy policies, connection limits, and resource limits rather than assuming that every protocol-compliant slow peer may remain indefinitely.

### Persistently Small Windows

A peer does not need to advertise exactly zero to make progress extremely slow. Persistently tiny receive windows can keep a connection alive while allowing only limited forward progress. TCP implementations contain algorithms intended to avoid inefficient tiny transmissions, so the exact packet behavior is implementation-dependent, but the resource-management consequence remains: connections that make insufficient progress can occupy scarce state for a long time.

For backend systems, this is why connection count alone is not enough to characterize load. Connection **progress**, buffered bytes, deadlines, and per-client limits also matter.

## Nagle's Algorithm

Nagle's algorithm reduces the number of very small TCP segments produced by applications that repeatedly write tiny amounts of data. The historical problem was especially visible in interactive applications where a one-byte payload could otherwise carry tens of bytes of TCP/IP headers.

The algorithm is based on the relationship between small writes and outstanding unacknowledged data:

- if there is no unacknowledged data in flight, TCP can send the new small data immediately;
- while unacknowledged data exists, additional small writes can be buffered until enough data accumulates for a full-sized segment or the outstanding data is acknowledged.

The relevant size boundary is the [Maximum Segment Size (MSS)](../02%20Protocols/05%20TCP.md#Maximum%20Segment%20Size%20%28MSS%29). Because acknowledgments depend on network timing and the peer's ACK policy, Nagle's algorithm can introduce latency that is difficult for an application to predict.

### `TCP_NODELAY`

`TCP_NODELAY` disables Nagle's algorithm for a TCP socket. Applications that prioritize latency for small writes often enable it, accepting the possibility of more small TCP segments in exchange for avoiding Nagle-induced waiting.

Disabling Nagle does not bypass TCP's other constraints. Flow control, congestion control, socket-buffer capacity, and the network itself can still delay a write after the application submits its bytes.

> [!example] cURL and TLS Handshakes
> cURL enabled `TCP_NODELAY` by default in 2016 after small-write delays were found to hurt TLS handshake latency. This is a concrete example of an application changing a socket option because a transport optimization that is useful for bandwidth efficiency can conflict with a latency-sensitive request/response pattern.
