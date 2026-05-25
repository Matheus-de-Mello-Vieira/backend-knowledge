## IPsec (Internet Protocol Security)

IPsec is a standardized framework of open protocols developed by the Internet Engineering Task Force (IETF) to secure communications over IP networks. Operating at the Network Layer (Layer 3 of the OSI model), it provides cryptographic security services—including data confidentiality, data integrity, origin authentication, and anti-replay protection—for all traffic passing across the network boundary, completely independent of the applications using it.

### The Three Core Pillars of IPsec

IPsec relies on three fundamental sub-protocols to establish, manage, and protect network traffic:

- **ESP (Encapsulating Security Payload - RFC 4303):** The primary protocol used when data privacy is required. ESP encrypts the payload of the IP packet (and can also encrypt the original IP header depending on the mode). While its main job is confidentiality, it also provides data origin authentication, integrity verification, and anti-replay protection.
- **AH (Authentication Header - RFC 4302):** A protocol designed strictly for integrity and authentication. It creates a cryptographic checksum over the payload _and_ the immutable fields of the IP header, proving the packet was not altered in transit. **Crucially, AH does not provide encryption.** Because it hashes the external IP header, AH is natively incompatible with Network Address Translation (NAT), which modifies header IP addresses.
- **IKE (Internet Key Exchange - IKEv1 / IKEv2):** The control plane protocol. Before any encrypted data can flow, the two network endpoints must trust each other and agree on how to encrypt the data. IKE automates this by handling mutual authentication (via pre-shared keys or digital certificates), performing a [Diffie-Hellman](06%20TLS.md#Diffie-Hellman) key exchange to establish symmetric encryption keys, and negotiating the parameters of the connection.

### Security Associations (SAs)

A fundamental concept to general IPsec is the **Security Association (SA)**.

- An SA is a one-way (unidirectional) logical agreement between two endpoints that defines the exact cryptographic parameters (ciphers, hashing algorithms, keys, and lifetimes) used to protect communication.
- Because an SA is strictly one-way, a standard bidirectional conversation between two hosts requires **two distinct SAs** (one for inbound traffic and one for outbound traffic).
- Each SA is uniquely tracked by a 32-bit number called the **Security Parameter Index (SPI)**, which is injected directly into the AH or ESP header of every packet so the receiving device knows instantly which cryptographic keys to use for decryption.

### Modes of Operation

IPsec can package and route data packets using two entirely different structural modes:

#### 1. Transport Mode (Host-to-Host)

- **How it works:** IPsec encrypts or authenticates only the _payload_ (the data inside) of the original IP packet. The original IP routing header is left completely intact on the outside.
- **Use Case:** Typically deployed for end-to-end communication directly between two specific servers or workstations on a local network. Because the original routing header is visible, routers can easily inspect the source and destination IPs to forward the packet normally.
#### 2. Tunnel Mode (Gateway-to-Gateway)

- **How it works:** The _entire_ original [IP packet](03%20Internet%20Protocol.md#Anatomy%20of%20the%20IP%20packet) (the data payload plus the internal source/destination IP header) is encrypted and fully encapsulated inside a brand-new, outer IP packet. This outer packet receives a new routing header with different source and destination IPs (typically the IPs of the VPN gateways).
- **Use Case:** The architectural foundation of Virtual Private Networks (VPNs). It is used to connect two distant corporate offices over the untrusted public internet (Site-to-Site) or to connect a remote worker's laptop to a corporate firewall. It completely hides the internal network topology from anyone eavesdropping on the transit network.

### Architectural Agnosticism

Unlike application-layer security (such as HTTPS/TLS), which must be built into web browsers and web servers individually, IPsec is completely transparent to applications. Because it operates at Layer 3, an email client, a database query, or a legacy custom software binary can transmit data across an IPsec tunnel without needing any awareness that the underlying traffic is being encrypted and protected.