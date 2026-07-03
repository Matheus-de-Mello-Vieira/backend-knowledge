# Transport Layer Security (TLS)

- **Definition:** TLS stands for Transport Layer Security.    
- **The OSI Debate:** The exact layer TLS occupies in the OSI model is arguable. Some classify it as Layer 5 (Session) because it establishes a stateful connection. Others align it closer to Layer 4 (Transport) because it strictly follows the TCP handshake, while practically, it acts as a secure wrapper for Layer 7 application protocols (e.g., securing HTTP to create HTTPS).
- **The Goal:** During the TLS handshake, both endpoints securely negotiate and agree upon the exact same shared key so they can encrypt all subsequent messages.

> **Note on Cryptography:** TLS relies heavily on Symmetric/Asymmetric encryption and Public Key Infrastructure (PKI). For the mathematical theory behind these algorithms and how Trust Chains work, see [Cryptography](https://www.google.com/search?q=../../Security/03%2520Cryptography%2520and%2520Data%2520Protection/01%2520Cryptography.md).

## Why TLS Requires Two Types of Cryptography

- **Symmetric for Payload (Speed):** We encrypt the actual data payloads with symmetric key algorithms because they are vastly faster than asymmetric ones. Symmetric encryption often relies on highly efficient bit-wise operations (like `XOR`) between the content and the key, whereas asymmetric encryption requires computationally expensive, exponential mathematics.
- **Asymmetric for Key Exchange (Security):** To use symmetric encryption, both the client and the server must know the exact same key. TLS uses asymmetric cryptography (Public Key Infrastructure) specifically to securely exchange this key over an open network. Therefore, two separate encryption algorithms are in play: one to safely exchange the key, and a faster one to encrypt the actual data.
- **Additional Features:** Beyond encryption, TLS authenticates the server's identity and supports advanced extensions like [Server Name Indication (SNI)](#Server%20Name%20Indication%20(SNI)), pre-shared keys, and 0-RTT (Zero Round Trip Time). 

## TLS Versions

### TLS 1.2 (The RSA Key Exchange)

In legacy TLS 1.2 configurations, the server relies on a static pair of public and private keys for the handshake.

1. The client initiates the connection by sending a "hello" message.
2. The server responds with its public key, which is cryptographically wrapped inside a Certificate. This certificate guarantees the server's identity and prevents attackers from intercepting the traffic and substituting their own public key.
3. The client uses the server's public key to encrypt the mathematical material needed to generate the symmetric key, and sends this payload to the server.
4. The server uses its closely guarded private key to decrypt the payload and derive the symmetric key.
5. The server confirms the exchange, and actual data encryption begins.

**The Vulnerability (Lack of Forward Secrecy):** The major flaw in the RSA model is that the server's private key rarely changes. Because many servers (or hostile actors) store network transactions, the encrypted data remains vulnerable indefinitely. If the server's static private key is ever leaked in the future (e.g., through a library bug), an attacker can retroactively decrypt years of recorded past traffic. While changing the private key regularly lessens the harm, it remains a structural weakness.

### TLS 1.3 (The Modern Standard)

TLS 1.3 drastically speeds up the connection by strictly using the Diffie-Hellman algorithm and dropping the vulnerable RSA key exchange.

1. The client initiates the handshake and immediately sends its public key alongside the mathematical combination of its private key and the public key (its Diffie-Hellman share).
2. The server receives this, combines the client's mixture with its own private key, and instantly derives the symmetric key.
3. The server then sends back its own combination (its share) and its Certificate, proving its identity to prevent interception.
4. The client receives the server's share, combines it with its private key, and derives the exact same symmetric key.

## Advanced TLS Mechanisms & Features
### Diffie-Hellman (Solving the RSA Problem)

To solve the retroactive decryption problem, the Diffie-Hellman algorithm allows both sides to mathematically derive a shared symmetric key without ever actually transmitting the final key itself.

- Both sides agree on a public key base and modulus, while keeping their own generated private keys secret.
- **The Math:** They combine the public components with their secret private key. Because this combination utilizes discrete logarithms—e.g., $g^x \pmod{n}$, where $g$ and $n$ come from the public key and $x$ is the private key—the resulting value is mathematically "unbreakable" and entirely safe to share over the network.
- The other side does the exact same process with their private key $y$, yielding $g^y \pmod{n}$, and sends it over.
- Because the combination algorithm is associative, when each side mathematically combines the received mixture with their own private key, they both arrive at the exact same shared value: $(g^x \pmod{n})^y = (g^y \pmod{n})^x = g^{xy} \pmod{n}$.
- This resulting value is used as the symmetric key. Because no static master key was used to encrypt the exchange, past traffic cannot be decrypted even if a key is compromised later.
### Perfect Forward Secrecy (PFS)

Perfect Forward Secrecy (often simply called Forward Secrecy) is a cryptographic feature designed to ensure that even if a server's long-term master private key is compromised in the future, past encrypted communications remain entirely secure.
    
- **The RSA Failure:** As noted in the TLS 1.2 section, traditional RSA key exchange inherently lacks PFS. Because the same static private key is used to negotiate the symmetric key for every session, a future key leak allows attackers to retroactively decrypt years of recorded historical traffic.
- **The Ephemeral Solution (DHE / ECDHE):** PFS is achieved by generating unique, temporary (ephemeral) session keys for every single connection. Modern TLS implementations achieve this using **Ephemeral Diffie-Hellman (DHE)** or **Elliptic Curve Ephemeral Diffie-Hellman (ECDHE)**.
- **How It Works:**
	* Instead of relying on the server's static private key to establish the symmetric key, both the client and server generate brand new, disposable Diffie-Hellman private variables for that specific handshake.
    - The server's master private key is still used, but _only_ to digitally sign the exchange (proving the server's identity), not to encrypt the data.
    - Once the session ends, both the client and the server completely destroy and discard those temporary Diffie-Hellman variables from their memory.
- **The Result:** If a hacker records your encrypted network traffic today and somehow steals the server's master private key five years from now, the stolen key is completely useless for decryption. The specific, temporary keys used to encrypt that historical session no longer exist anywhere in the world.
### Mutual TLS (mTLS)

- **Standard TLS vs. mTLS:** 
	* In a **Standard TLS** connection, authentication is strictly one-way. The server proves its identity to the client using a certificate. The server, however, has no idea who the client is at the network layer; it relies on application-layer methods (like passwords, API keys, or JWTs) to authenticate the user later.
    - In **Mutual TLS (mTLS)**, authentication is two-way. Both the client _and_ the server must present cryptographic certificates to prove their identities to each other before any data can be transmitted.
- **How It Works (The Handshake Addition):**
    - mTLS modifies the standard handshake process. After the server presents its certificate and public key, it explicitly sends a `CertificateRequest` to the client.
    - The client must respond by sending its own X.509 certificate back to the server.
    - The server verifies the client's certificate against its trusted Certificate Authority (CA). If the certificate is invalid, expired, or missing, the server immediately drops the connection before any application data is ever exchanged.
- **Why Use mTLS?**
    - **Zero Trust Security:** It enforces the philosophy of "never trust, always verify." By requiring cryptographic proof of identity at the network level, you prevent unauthorized devices from even opening a connection to your backend.
    - **Microservices and Backend Communication:** mTLS is the industry standard for securing service-to-service communication (e.g., inside a Kubernetes cluster). Instead of passing API keys back and forth, Microservice A and Microservice B each have their own certificates and securely authenticate each other automatically.
    - **IoT Devices:** For Internet of Things (IoT) ecosystems, embedding a unique client certificate onto a physical device is a far more secure and scalable way to authenticate millions of devices than managing standard passwords.
    - **Protection Against Phishing and Credential Theft:** Because the authentication relies on a cryptographic certificate installed on the client's machine rather than a typed password, mTLS is virtually immune to standard phishing attacks or stolen credentials.

### TLS Extensions

- **What Are They?** TLS extensions are essentially extra blocks of metadata appended to the end of the standard `ClientHello` and `ServerHello` messages.
- **The Purpose:** They exist to make the TLS protocol flexible and future-proof. Instead of completely rewriting the core TLS handshake every time engineers invent a new security feature or optimization, they simply create a new "extension." If a server doesn't understand a specific extension a client sends, it safely ignores it and continues the standard handshake.
- **Common Examples:**
    - **ALPN (Application-Layer Protocol Negotiation):** Allows the client and server to agree on which Layer 7 protocol they will use (e.g., HTTP/2 vs HTTP/3) during the TLS handshake, saving an extra network round trip.
    - **Supported Versions:** Allows a client to tell the server, "I support TLS 1.3, but I can fall back to TLS 1.2 if you need me to."
    - **SNI (Server Name Indication)**
### Server Name Indication (SNI)

- **The Problem (The Chicken and the Egg):** In the early days of the web, the TLS handshake always completed _before_ the client sent the HTTP request.
    - If a single server (with a single IP address) hosted multiple different websites, it didn't know which TLS certificate to present to the client during the handshake.
    - The server only finds out which website the client wants when it reads the HTTP `Host` header, but it can't read the HTTP request until the TLS connection is fully established. Because of this, servers were originally limited to hosting only **one HTTPS website per IP address**.
- **The SNI Solution:** Server Name Indication is an extension added to the TLS protocol to solve this exact bottleneck.
    - It allows the client to inject the requested hostname (e.g., `api.example.com`) directly into the initial `ClientHello` message at the very beginning of the TLS handshake.
- **The Result (Virtual Hosting):** Because the server now knows exactly which website the client is looking for right away, it can dynamically select and serve the correct corresponding TLS certificate. This allows millions of distinct HTTPS websites to be hosted on shared IP addresses (a necessity for modern cloud providers and CDNs).
#### Encrypted Client Hello (ECH)

- **The Privacy Leak (Plaintext SNI):** Even though standard SNI solves the routing problem, it creates a privacy issue. Because standard SNI is sent in the initial `ClientHello` message—before the symmetric encryption key is negotiated—it is transmitted entirely in plaintext. Your Internet Service Provider (ISP) or anyone snooping on the network can see exactly _which_ website domain you are visiting.
- **The ECH Solution:** Encrypted Client Hello (ECH) is a modern TLS extension designed to plug this final privacy leak by encrypting the SNI and other sensitive metadata right from the very first packet.
- **How It Works (Inner vs. Outer Hello):** ECH relies heavily on the flexibility of **TLS Extensions** to nest one message inside another, much like putting a locked box inside a standard mailing envelope.
    1. **Key Fetching:** Before initiating the connection, the client securely fetches the server's public ECH key via DNS (using DNS-over-HTTPS so the request isn't snooped).
    2. **The Inner Hello (The Locked Box):** The client builds a complete `ClientHello` message in its memory containing the true SNI (e.g., `secret-api.example.com`). It takes this entire chunk of data and encrypts it using the server's public ECH key. It is now a blob of unreadable binary data.
    3. **The Outer Hello (The Envelope):** The client then builds a second, unencrypted `ClientHello`. For the standard SNI extension, it uses a generic, public-facing hostname (like the name of the CDN, e.g., `cloudflare.com`).
    4. **The Nesting via Extension:** The client takes the encrypted "Inner Hello" from Step 2 and pastes it directly into a special **ECH Extension** attached to the Outer Hello.
- **The Result:** When the packet travels across the internet, observers only see a standard TLS connection to a generic cloud provider. Once the packet reaches the provider's server, the server checks the ECH extension, uses its private key to decrypt the inner message, reads the true SNI, and securely routes your connection.