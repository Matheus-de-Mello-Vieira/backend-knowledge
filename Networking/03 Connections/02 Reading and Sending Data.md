# Reading and Sending Data

After a TCP connection is established, the application exchanges a byte stream through a [connected socket](../../Operating%20Systems/07%20Socket%20Management.md#Receiving%20Data). [Kernel send and receive buffering](../../Operating%20Systems/07%20Socket%20Management.md#Socket%20Buffers%20and%20Backpressure), blocking and non-blocking I/O, backpressure, and readiness determine when application I/O can make progress, while TCP provides the ordered-stream, reliability, flow-control, retransmission, and congestion-control behavior applied to those bytes.

Buffer capacity applies to finite queued networking state rather than necessarily to one contiguous byte array. On Linux, that queued data is represented with [`sk_buff`](../../Operating%20Systems/07%20Socket%20Management.md#Linux%20sk_buff%20Objects) (`skb`) objects; the representation does not change the TCP semantics described here.

## Receiving Data over TCP

- **Ordered Byte Stream:** The kernel receives TCP segments, validates and reorders byte ranges when necessary, and exposes an ordered byte stream to the application.
- **No Message Boundaries:** TCP packet boundaries are not application message boundaries.
    - The application may receive only part of one logical message or several logical messages in one `recv()`, depending on its framing protocol and the bytes currently available.
- **Flow-Control Integration:** Receive-side buffering participates directly in TCP flow control.
    - As unread application data occupies receive-buffer capacity, the TCP implementation adjusts the receive window (`rwnd`) advertised to the peer.
    - The sender must respect that [advertised capacity](../02%20Protocols/05%20TCP.md#1.%20Flow%20Control%20%28Receiver-Driven%29).
- **Application-Speed Dependency:** Network progress depends partly on how quickly the receiving application consumes data.
    - If the application stops reading, kernel receive capacity becomes constrained.
    - TCP eventually slows or stops the peer rather than allowing receive memory to grow without bound.

## Sending Data over TCP

- **Local Acceptance:** A successful socket `send()` means that the local kernel accepted some amount of application data; it does not mean that the peer application has received it.
- **Transport Processing:** TCP decides how accepted bytes are segmented and transmitted while respecting reliability, flow control, and congestion control.
- **Retransmission State:** Sent bytes may need to remain represented in kernel state until TCP knows they no longer require retransmission.
- **Drain Constraints:** A slow peer, packet loss, a small advertised receive window, or network congestion can prevent the sender from draining its local send-side state.
- **Application Backpressure:** When that pressure reaches the application, [socket writes can block or report that they would block](../../Operating%20Systems/07%20Socket%20Management.md#Socket%20Buffers%20and%20Backpressure).

## Slow or Stalled Receivers

TCP deliberately allows a receiver to slow the sender by advertising a small receive window.

- **Normal Purpose:** This behavior is necessary for flow control because a legitimate application may temporarily stop reading while it is busy, descheduled, or processing data more slowly than it arrives.
- **Resource Retention:** Long-lived slow receivers can retain server resources.
    - A server may keep connection state and unsent application data for a client that makes very little progress.
- **Scale Consequence:** Enough slow connections can consume descriptors, application memory, and kernel socket-buffer memory even when inbound bandwidth is small.

### Zero-Window State

- **Trigger:** If the receiver has no available TCP receive-buffer capacity, it may advertise `rwnd = 0`.
- **Sender Behavior:** The sender stops normal data transmission.
- **Persist Mechanism:** TCP periodically probes for a window update so a lost update cannot leave the connection deadlocked forever.
- **Abuse Potential:** A malicious or pathological peer can use long-lived zero-window behavior to make a sender retain connection state and pending data.
- **Mitigations:** Real systems limit the impact through combinations of kernel timeouts, application deadlines, reverse-proxy policies, connection limits, and resource limits rather than assuming every protocol-compliant slow peer may remain indefinitely.

### Persistently Small Windows

- **Slow Progress Without Zero:** A peer does not need to advertise exactly zero to make progress extremely slow.
- **Long-Lived Connection:** Persistently tiny receive windows can keep a connection alive while allowing only limited forward progress.
- **Implementation Variance:** TCP implementations contain algorithms intended to avoid inefficient tiny transmissions, so the exact packet behavior is implementation-dependent.
- **Resource Consequence:** Connections that make insufficient progress can occupy scarce state for a long time.
- **Backend Implication:** Connection count alone is not enough to characterize load.
    - Connection **progress**, buffered bytes, deadlines, and per-client limits also matter.

## Nagle's Algorithm

Nagle's algorithm reduces the number of very small TCP segments produced by applications that repeatedly write tiny amounts of data. The historical problem was especially visible in interactive applications where a one-byte payload could otherwise carry tens of bytes of TCP/IP headers.

- **Purpose:** Reduce inefficient streams of tiny TCP segments.
- **No Outstanding Data:** If there is no unacknowledged data in flight, TCP can send new small data immediately.
- **Outstanding Data:** While unacknowledged data exists, additional small writes can be buffered.
    - Transmission can resume when enough data accumulates for a full-sized segment or the outstanding data is acknowledged.
- **Relevant Size Boundary:** The size boundary is the [Maximum Segment Size (MSS)](../02%20Protocols/05%20TCP.md#Maximum%20Segment%20Size%20%28MSS%29).
- **Latency Trade-off:** Because acknowledgments depend on network timing and the peer's ACK policy, Nagle's algorithm can introduce latency that is difficult for an application to predict.

### `TCP_NODELAY`

- **Behavior:** `TCP_NODELAY` disables Nagle's algorithm for a TCP socket.
- **When It Helps:** Applications that prioritize latency for small writes often enable it.
- **Trade-off:** The application accepts the possibility of more small TCP segments in exchange for avoiding Nagle-induced waiting.
- **What It Does Not Bypass:** Disabling Nagle does not remove TCP's other constraints.
    - Flow control, congestion control, socket-buffer capacity, and the network itself can still delay a write after the application submits its bytes.

> [!example] TLS Handshakes and Delayed Acknowledgments
> A TLS implementation can emit related handshake records through several small TCP writes. After the first sub-MSS segment is sent, Nagle's algorithm can buffer a following small write until the first segment is acknowledged. If the peer uses delayed acknowledgments while waiting for more data, the handshake can stall even though both endpoints are otherwise ready to continue.
>
> `TCP_NODELAY` allows the subsequent write to be transmitted without waiting for that acknowledgment, which can avoid this latency-sensitive interaction. It does not make TLS intrinsically faster and can increase the number of small segments.
<!-- -->
> [!example] cURL's Default
> cURL enabled `TCP_NODELAY` by default in 2016. This choice favors prompt progress in interactive transfers while accepting that some workloads can produce more small TCP segments.
