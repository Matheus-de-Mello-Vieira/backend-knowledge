# Comprehensive Notes: Network Communication Models

## Why Do We Need Communication Models?

Network models define conceptual guidelines that allow for the creation of universal, compatible networks, even when physical components and software are developed by entirely different companies or use different programming languages. They provide several critical benefits:

- **Agnostic Applications:** Without standard models, applications would need to be rewritten for every underlying network medium (e.g., different versions for Wi-Fi, Ethernet, LTE, or fiber).
- **Network Equipment Management:** Standardization makes upgrading and managing hardware significantly easier.
- **Decoupled Innovation:** Innovations can occur within a specific layer without breaking or affecting the rest of the model's functionality.
- **Modular Programming:** Prevents changes in one layer from disrupting other layers, which dramatically increases the speed and agility of software development.

## The OSI (Open Systems Interconnection) Model

The OSI model is a hierarchical structure built to support network design. It is not a protocol itself, but rather an archetype used to build and describe flexible network architectures.

- **Core Concepts:** Its three central pillars are services, interfaces, and protocols.
- **Flexibility:** You can freely swap out a protocol as long as the new one continues to provide the requested service to the layer above it without needing to alter upper-layer software.
- **Evolution:** The OSI model started by identifying network problems and progressively adding layers to fix them when errors were identified, eventually resulting in its famous 7-layer structure.

### The 7 Layers of OSI

The layers operate interdependently; each layer relies on the one below it, and a failure to transfer information from one layer to the next will break the entire chain.

- **Layer 7 - Application:** Allows end-users and software to access the network, providing user interfaces and supporting services like email and shared data management. Typically utilizes protocols like HTTP, FTP, and gRPC. Backend engineers usually rely on libraries to abstract this layer.
- **Layer 6 - Presentation:** Handles encoding and serialization. It transforms data into a binary format (e.g., serializing JSON to flat byte strings for transmission, or deserializing it back for the application to consume).
- **Layer 5 - Session:** Establishes, maintains, and synchronizes dialogs and interactions between communicating systems. Manages connection establishment (like TLS) and stateful protocols. A stateless protocol does not really depend on session state here. While seemingly simple, some proxies (like Linkerd) build logic exclusively on this layer.
- **Layer 4 - Transport:** Ensures end-to-end, process-to-process delivery (a process being a program running on a host). It ensures the message arrives in its entirety by utilizing mechanisms to detect transmission errors. This layer manages ports and uses protocols like TCP and UDP. At this layer, TCP sends **segments** and UDP sends **datagrams**.
- **Layer 3 - Network:** Responsible for sending **packets** from their origin to their destination across multiple different networks or links. This layer relies strictly on IP addresses and routing; ports and transport concepts are irrelevant here. (Note: A network layer is technically unnecessary if two systems are communicating on the exact same local network link).
- **Layer 2 - Data Link:** Encodes data provided by the upper layers into a format suitable for raw transmission. It operates close to the physical medium, packaging data into **frames** and routing them using MAC addresses (e.g., Ethernet frames).
- **Layer 1 - Physical:** Transports a raw stream of bits (0s and 1s without any interpretation) over physical media. It dictates the electrical, mechanical, and interface specifications. Data is encoded into electrical signals (Ethernet/bare metal), optical light (fiber), or radio waves (Wi-Fi).

## The TCP/IP Model

While the OSI model is highly adaptable, it began to struggle as networks evolved to use new media like satellites and radio, expanding geographically into massive sub-networks. TCP/IP was developed as a simpler, more robust alternative.

- **Resiliency Origin:** Born from the ARPANET military project, TCP/IP was explicitly designed to withstand the loss of subnet hardware (fearing that a network attack could destroy network switches and routers).
- **Design Philosophy:** Unlike OSI, TCP/IP first identified exactly what the internet needed, and then formed a model and layers specifically around those operational needs. Originally, it did not clearly distinguish between services, interfaces, and protocols.

### The 4 Layers of TCP/IP

- **Application Layer:** Manages high-level communication protocols like HTTP, DNS, FTP, and POP. TCP/IP merged OSI's Session and Presentation layers into the Application layer because they were deemed unnecessary and of little use on their own.
- **Transport Layer:** Synchronizes connections and determines data transfers between participating hosts. It utilizes the TCP (Transmission Control Protocol) and UDP (User Datagram Protocol).
- **Internet Layer:** Solves the problem of interconnecting different networks by allowing hosts to inject packets destined for various external networks. It provides only two services: sending and receiving IP packets.
- **Network Access Layer:** Handles physical device connectivity. This single layer executes all the functions of both the Data Link and Physical layers from the OSI model.

## OSI vs. TCP/IP: Key Differences

| **Feature**                | **OSI Model**                                                | **TCP/IP Model**                                             |
| -------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Layer Count**            | 7 Layers.                                                    | 4 Layers.                                                    |
| **Adaptability**           | Highly adaptable; not built around a specific network.       | Built specifically around Internet standards.                |
| **Network/Internet Layer** | Supports both connection-oriented and connectionless communication. | Supports **only** connectionless communication (only IP).    |
| **Transport Layer**        | Supports **only** connection-oriented communication.         | Supports both connection-oriented (TCP) and connectionless (UDP) communication. |
| **General Complexity**     | Complex, but decomposes network communication into very granular pieces. | Appears simpler, but possesses its own high degree of functional complexity. |

## 5. Practical Example: The Lifecycle of a Request

Here is how the OSI layers execute a standard POST request sent from a computer to an HTTPS webpage:

**Sending the Request (Down the Stack):**

1. **Layer 7:** Application initiates a POST request containing JSON data to an HTTPS server.
2. **Layer 6:** The JSON is serialized into flat byte strings.
3. **Layer 5:** The system requests the establishment of a TCP/TLS connection.
4. **Layer 4:** A SYN request is generated and targeted at port 443.
5. **Layer 3:** The SYN request is placed into an IP packet, and source/destination IP addresses are added.
6. **Layer 2:** Packets are placed into a single frame, and source/destination MAC addresses are added.
7. **Layer 1:** The frame becomes a string of bits, converted into a physical signal (radio for Wi-Fi, electrical for Ethernet, or light for fiber).

**Receiving the Request (Up the Stack):**

The receiving computer processes this in reverse (Layer 1 up to Layer 7).

- At **Layer 4**, TCP manages flow control, congestion control, and any necessary retransmissions.
- If the system is simply processing a TCP three-way handshake (a SYN segment), the receiver may stop at **Layer 4/5** to establish the state machine responsible for managing the connection, only proceeding to Layer 7 once the handshake is complete and application data is ready.

## Real-World Devices & Network Layers

Professionally, **Backend Engineers** primarily worry about Layers 4 and 7, while **DevOps Engineers** frequently manage Layers 2 and 3. Hardware and network systems stop processing at the lowest layer necessary to do their job:

- **Switches (Layer 2):** They stop at the Data Link layer because they forward frames based exclusively on MAC addresses.
- **Routers & VPNs (Layer 3):** They operate at the Network layer, acting as intermediate devices that define and distribute packets based entirely on IP routes and addresses.
- **Transparent Firewalls & Proxies (Layer 4):** They block or forward traffic based solely on IP addresses and ports. (They are "transparent" because they deal with raw IP/Ports and do not undergo encryption overhead). *Note: Some advanced firewalls look at Layer 7 to judge blocking.*
- **Layer 7 Load Balancers / CDNs:** These proxies look at application data (like Nginx forwarding traffic based on an HTTP route). Because Layer 7 data is normally encrypted, the proxy must terminate the connection, decrypt the data, and remake the request to the backend server, making Layer 7 proxies slower than Layer 4 proxies.

## Shortcomings of the OSI Model

- The OSI model has many layers, which makes it more precise but also harder to reason about quickly.
- In practice, it is not always obvious which layer should own a given concern.
- A common simplification is to mentally collapse Layers 5, 6, and 7 into a single application-facing layer.
- This is one reason the TCP/IP model feels simpler in practice.
