# HTTP/3

* HTTP over QUIC.
  * QUIC is a transport protocol built on top of UDP.
  * UDP provides datagram delivery, while QUIC implements reliability, streams, congestion control, flow control, security, and connection management.
* HTTP/3 keeps the multiplexed-stream model introduced by HTTP/2, but runs it over QUIC instead of TCP.
  * HTTP/2 provides application-level flow control, while TCP provides transport-level reliability and congestion control.
  * QUIC provides transport-level congestion control itself, plus connection-level and per-stream flow control.

## Streams

Because HTTP/2 runs over TCP, all streams share the same ordered TCP byte stream. If a TCP segment is lost, later bytes cannot be delivered to HTTP/2 until the missing data is retransmitted, temporarily blocking unrelated HTTP/2 streams as well.

HTTP/3 runs over QUIC, where streams are independently ordered. If data for one stream is lost, already-received data from unrelated streams can still be delivered without waiting for the missing data.

QUIC does not retransmit a lost UDP datagram itself. Instead, it detects which QUIC data was lost and sends the missing stream data again in a new QUIC packet.

## CPU Overhead

HTTP/3 usually requires more transport-layer processing in the application than HTTP/2.

HTTP/2 relies on TCP for features such as reliable delivery, acknowledgements, loss recovery, retransmission, congestion control, and ordered byte delivery. QUIC implements these transport features itself and is commonly implemented in userspace, so work traditionally performed by the operating system's TCP stack is instead performed by the QUIC implementation.

For incoming traffic, HTTP/3 and QUIC may need to perform work such as:

* QUIC packet parsing and packet-number tracking.
* Acknowledgement processing and loss detection.
* Retransmission decisions and congestion-control updates.
* Connection-level and stream-level flow control.
* QUIC stream reassembly and state management.
* Packet authentication/decryption and QUIC header protection.
* HTTP/3 frame parsing.
* QPACK header compression/decompression.

Encryption alone is not what distinguishes QUIC's CPU cost, because HTTP/2 on the public web also normally uses TLS. The additional cost comes largely from combining secure packet processing with transport-state management inside the QUIC implementation.

### CPU Cost vs Latency

Higher CPU overhead does not necessarily mean worse application performance. QUIC can perform more protocol work while still reducing user-visible latency through independent streams under packet loss, integrated TLS/QUIC connection establishment, connection resumption, and connection migration.

## Pros and Cons

### Pros

* QUIC has many other benefits.
* Integrates connection setup and TLS negotiation, reducing connection-establishment latency.
* Provides transport-level congestion control.
* Provides flow control both per connection and per stream.
* Connection migration.
  * QUIC packets carry a `Connection ID` that identifies the connection independently from the client's IP address and port.
  * This allows a connection to survive network-address changes, such as switching from Wi-Fi to cellular networking.

### Cons

* **Higher CPU overhead:** HTTP/3 requires HTTP/3 and QPACK processing in addition to QUIC packet protection, stream management, acknowledgements, loss recovery, congestion control, and flow control.
* UDP could be blocked on some firewalls or networks.
* **IP fragmentation should be avoided:** QUIC implementations try to use appropriately sized UDP datagrams and path-MTU discovery so packets do not depend on IP fragmentation.
* **Connection ID privacy:** Connection IDs are intentionally visible so routing and connection migration can work. Knowing a Connection ID does not allow an attacker to inject valid application data because QUIC packets are cryptographically authenticated, but poorly designed Connection IDs can create privacy or linkability concerns.
