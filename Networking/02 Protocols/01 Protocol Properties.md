# Protocol Properties

## What is a Protocol?
A protocol is a standardized system of rules that allows two or more parties to communicate effectively. 

* **Design Intent:** Every protocol is engineered with specific properties to solve a particular communication challenge.
* **Evolutionary Context:** Protocols are often products of their time. A protocol designed decades ago may not account for modern security needs or high-latency environments, leading to the development of newer versions (e.g., the transition from HTTP/1.1 to HTTP/3).

## Key Properties of Protocols

### 1. Data Format
Defines how information is encoded for transmission.
* **Text-Based:** Human-readable formats.
    * **Plain Text:** Simple ASCII/UTF-8 strings.
    * **Structured:** JSON, XML.
* **Binary:** Optimized for machine processing and bandwidth efficiency.
    * **Protobuf:** Google’s language-neutral, extensible mechanism for serializing structured data.
    * **RESP (REdis Serialization Protocol):** A fast, simple protocol used by Redis and other client-server architectures.
    * **HTTP/2 & HTTP/3:** Unlike HTTP/1.1, these modern versions use binary framing for efficiency.

### 2. Transfer Mode
Defines how data is segmented and delivered.
* **Message-Based:** Data is sent in discrete units with defined boundaries (start and end).
    * **Examples:** UDP, HTTP/1.1.
* **Stream-Based:** Data is treated as a continuous flow of bytes without inherent boundaries.
    * **TCP:** Because TCP is a stream, high-level protocols (like HTTP) must implement logic to parse the stream back into distinct messages.
    * **WebRTC:** Optimized for streaming real-time media like audio and video.

### 3. Addressing
The mechanism used to identify the source and destination of data.
* **Physical:** MAC Addresses (Layer 2).
* **Logical:** IP Addresses (Layer 3).
* **Human-Readable:** DNS (maps names to IP addresses).

### 4. Directionality and Duplexing
Defines the flow of data between parties.
* **Unidirectional (Simplex):** Data flows in one direction only.
* **Half-Duplex:** Data can flow in both directions, but only one party can send at a time (e.g., traditional walkie-talkies).
* **Full-Duplex:** Data flows in both directions simultaneously (e.g., TCP, WebSockets).
    * *Note:* While standard HTTP is request-response, modern implementations like HTTP/2 allow for multiplexing.

### 5. State Management
* **Stateless:** Each request is independent and contains all the information needed to fulfill it (e.g., UDP, standard HTTP).
* **Stateful:** The protocol remembers previous interactions and maintains a session context (e.g., TCP handshakes, gRPC, Apache Thrift).

### 6. Flow and Congestion Control
Mechanisms to ensure the network or receiver isn't overwhelmed.
* **TCP:** Robust control; it slows down transmission if it detects packet loss or network congestion.
* **UDP:** No built-in control; it sends data as fast as the application allows, regardless of network health.

### 7. Error Management
* **Error Codes:** Explicit signals (like HTTP 404 or TCP RST) indicating what went wrong.
* **Reliability Logic:** Mechanisms like **Retries**, **Timeouts**, and **Checksums** to ensure data integrity and delivery.

### 8. Routing and Intermediaries
Defines how data traverses through various nodes.
* **Proxies:** Act as intermediaries for requests (often for security or caching).
* **Gateways:** Connect different networks or translate between different protocol types.