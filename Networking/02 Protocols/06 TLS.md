# Transport Layer Security (TLS)

- **Definition:** TLS stands for Transport Layer Security.    
- **The OSI Debate:** The exact layer TLS occupies in the OSI model is arguable. Some classify it as Layer 5 (Session) because it establishes a stateful connection. Others align it closer to Layer 4 (Transport) because it strictly follows the TCP handshake, while practically, it acts as a secure wrapper for Layer 7 application protocols (e.g., securing HTTP to create HTTPS).
- **The Goal:** During the TLS handshake, both endpoints securely negotiate and agree upon the exact same shared key so they can encrypt all subsequent messages.

> [!note] Cryptography boundary
> TLS uses algorithm families such as RSA, Diffie-Hellman, and elliptic-curve systems in a protocol-specific way. For the general properties of [encryption](../../Security/03%20Cryptography%20and%20Data%20Protection/02%20Encryption.md), [cryptography](../../Security/03%20Cryptography%20and%20Data%20Protection/01%20Cryptography.md), and [digital certificates and PKI](../../Security/03%20Cryptography%20and%20Data%20Protection/04%20Digital%20Certificates%20and%20PKI.md), see the Security notes. The focus here is how TLS assembles those pieces into a handshake and a secure channel.

## Why TLS Requires Two Types of Cryptography

- **Symmetric for Payload (Speed):** We encrypt the actual data payloads with symmetric key algorithms because they are vastly faster than asymmetric ones. Symmetric encryption often relies on highly efficient bit-wise operations (like `XOR`) between the content and the key, whereas asymmetric encryption requires computationally expensive, exponential mathematics.
- **Asymmetric for Key Exchange (Security):** To use symmetric encryption, both the client and the server must know the exact same key. TLS uses asymmetric cryptography (Public Key Infrastructure) specifically to securely exchange this key over an open network. Therefore, two separate encryption algorithms are in play: one to safely exchange the key, and a faster one to encrypt the actual data.
- **Additional Features:** Beyond encryption, TLS authenticates the server's identity and supports advanced extensions like [Server Name Indication (SNI)](#Server%20Name%20Indication%20(SNI)), pre-shared keys, and 0-RTT (Zero Round Trip Time). 

## TLS Versions

### TLS 1.2 (The RSA Key Exchange)

In legacy TLS 1.2 configurations, the server relies on a static pair of public and private keys for the handshake. The important point here is not RSA as a standalone algorithm family, but the specific way TLS used RSA to protect handshake material.

1. The client initiates the connection by sending a "hello" message.
2. The server responds with its public key, which is cryptographically wrapped inside a Certificate. This certificate guarantees the server's identity and prevents attackers from intercepting the traffic and substituting their own public key.
3. The client uses the server's public key to encrypt the mathematical material needed to generate the symmetric key, and sends this payload to the server.
4. The server uses its closely guarded private key to decrypt the payload and derive the symmetric key.
5. The server confirms the exchange, and actual data encryption begins.

**The Vulnerability (Lack of Forward Secrecy):** The major flaw in the RSA model is that the server's private key rarely changes. Because many servers (or hostile actors) store network transactions, the encrypted data remains vulnerable indefinitely. If the server's static private key is ever leaked in the future (e.g., through a library bug), an attacker can retroactively decrypt years of recorded past traffic. While changing the private key regularly lessens the harm, it remains a structural weakness.

### TLS 1.3 (The Modern Standard)

TLS 1.3 drastically speeds up the connection by strictly using Diffie-Hellman-style key agreement and dropping the vulnerable RSA key exchange.

1. The client initiates the handshake and immediately sends its public key alongside the mathematical combination of its private key and the public key (its Diffie-Hellman share).
2. The server receives this, combines the client's mixture with its own private key, and instantly derives the symmetric key.
3. The server then sends back its own combination (its share) and its Certificate, proving its identity to prevent interception.
4. The client receives the server's share, combines it with its private key, and derives the exact same symmetric key.

## Mathematical Foundations of Public Key Cryptography

Public key cryptography relies on mathematical "trapdoors"—functions that are incredibly fast for a computer to calculate in one direction, but practically impossible to reverse-engineer without the secret key. This security is built using two distinct mathematical models: prime numbers and elliptic curves.

### Traditional Public Key Models (Primes & Modular Arithmetic)

Before elliptic curves were widely adopted, asymmetric cryptography relied entirely on the unique properties of massive prime numbers. This model is dominated by two primary algorithms: **RSA** (often used for identity/certificates) and standard **Diffie-Hellman** (used for key exchange). Both build their trapdoors using different prime-based techniques.

- **1. RSA and the Integer Factorization Trapdoor:** RSA relies on the mathematical principle that multiplying two numbers is easy, but un-multiplying (factoring) them is incredibly hard.
    - **The Math:** A computer generates two distinct, absolutely massive prime numbers, $p$ and $q$ (often hundreds of digits long). These original primes are kept fiercely guarded as the **Private Key**.
    - **The Public Key:** The computer multiplies these primes together to create a giant composite number, $n$ ($n = p \times q$). This massive number $n$ becomes the core of the **Public Key**.
    - **The Trapdoor:** A CPU can multiply $p$ and $q$ to find $n$ in a fraction of a millisecond. However, if a hacker intercepts $n$ and wants to reverse-engineer the private key, there is no formula to easily split $n$ back into $p$ and $q$. The only way to find the original primes is through trial division, which would take supercomputers thousands of years.
- **2. Standard Diffie-Hellman and the Discrete Logarithm Trapdoor:** Diffie-Hellman uses prime numbers differently, relying on modular arithmetic ("clock math" where numbers wrap around a maximum limit) to scramble data.
    - **The Equation:** The formula is $g^x \pmod{p} = Y$. Here, $g$ (the base) and $p$ (a massive prime modulus) are public. Your randomly generated number $x$ is the **Private Key**, and the resulting scramble $Y$ is the **Public Key**.
    - **The Trapdoor:** Because the numbers constantly wrap around the massive prime "clock" as they are exponentially multiplied, the result $Y$ jumps around chaotically. It is computationally trivial to calculate $Y$ going forward, but mathematically impossible to use standard algebra or logarithms to reverse-engineer $x$ from $Y$.
        
> [!note ]The Limitation of Primes
 > Over the decades, mathematicians invented brilliant algorithms (like the _General Number Field Sieve_) that act as shortcuts to factor prime numbers and solve discrete logarithms much faster than blindly guessing. To stay ahead of these shortcuts, RSA keys had to balloon to massive sizes (e.g., 3072-bit or 4096-bit). Processing these massive numbers requires heavy CPU cycles and memory bandwidth, which slows down handshakes and drains device batteries.

### Elliptic Curve Cryptography (ECC)

To solve the performance bottlenecks of prime number cryptography, modern TLS implementations overwhelmingly use **ECDHE** (Elliptic Curve Diffie-Hellman Ephemeral). ECC replaces massive primes with algebraic geometry, offering a much more efficient trapdoor.

- **The ECC Solution (The Math):** Instead of prime numbers, ECC relies on the geometry of elliptic curves graphed over finite fields. The curve is typically defined by a symmetric equation like $y^2 = x^3 + ax + b$.
    - **Don't mistake it for an ellipse:** Despite the name, elliptic curves are not ovals or egg-shaped. The name is a historical quirk derived from the "elliptic integrals" astronomers once used to calculate planetary orbits. Graphically, they feature perfect horizontal symmetry and often look like a sweeping, open curve, sometimes accompanied by a separate teardrop-shaped loop.
    - **It has a special property where lines intersect three times:** Because the curve is a cubic equation (degree 3), it possesses a unique algebraic property governed by Bézout’s Theorem. Any straight, continuous line drawn across the graph is mathematically guaranteed to intersect the curve in exactly three places. If a tangent line is drawn, the point of tangency algebraically counts as two intersections (a "double root"), forcing the line to hit the curve at one final, deterministic third point.
- **The Trapdoor (The "Billiard" Function):** ECC works like a cryptographic game of billiards on this graph.
    1. Both sides agree on a standard starting point on the curve (the generator point).
    2. A device generates a massive random number, $n$, which becomes the **private key**.
    3. The device mathematically doubles the point $n$ times using the curve's unique tangent property. By drawing a tangent line at the point, the math is forced to find a deterministic third intersecting point. The device reflects that third point across the x-axis to get a new point, and repeats this tangent-bouncing process $n$ times.
    4. The final resting coordinate on the curve becomes the **public key**.
- **Why It Is Unbreakable:** This "bouncing" process is computationally easy to execute forward. However, if a hacker intercepts the public key (the final coordinate) and knows the starting point, there is no mathematical shortcut to figure out how many times you bounced ($n$). The only way to reverse-engineer the private key is to guess and check every single bounce, which would take modern computers millions of years.
- **Why It Wins (Efficiency):** Because mathematicians have not found any clever shortcuts to reverse this geometric curve problem, ECC provides the exact same level of security with a fraction of the key size. A **256-bit ECC key** offers roughly equivalent cryptographic strength to a massive **3072-bit RSA key**. This low overhead is what makes robust encryption possible for both high-traffic cloud servers and low-power IoT devices.
- **Common Curves:** During the TLS handshake, endpoints must agree on the exact mathematical curve they will use to derive their keys. Standard, heavily vetted curves include **Curve25519** and **NIST P-256**.

## Advanced TLS Mechanisms & Features

The sections below keep the protocol-level focus: they describe why TLS uses these mechanisms and what changes in the handshake when it does. The broader algorithm families still belong in the Encryption and Cryptography notes.

### The Diffie-Hellman Key Exchange

To solve the retroactive decryption problem inherent in static RSA key exchanges, the Diffie-Hellman algorithm allows both sides to mathematically derive a shared symmetric key without ever actually transmitting the final key itself.

While the underlying mathematical trapdoors (discrete logarithms and elliptic curves) are detailed in [Mathematical Foundations of Public Key Cryptography](#Mathematical%20Foundations%20of%20Public%20Key%20Cryptography), the Diffie-Hellman protocol is the actual mechanism that leverages those trapdoors to allow two parties to securely negotiate that shared key over a fully monitored network.

- **The Goal:** Alice and Bob need to generate the exact same symmetric key, but they can only communicate over a channel where a hacker is listening to every word.
- **The Protocol Steps:**
    1. **Public Agreement:** Both sides openly agree on the public mathematical base (either a massive prime modulus $p$ and base $g$, or a specific Elliptic Curve like Curve25519). The hacker sees this.
    2. **Private Generation:** Alice generates a secret private key ($x$). Bob generates his own secret private key ($y$).
    3. **Applying the Trapdoor:** Alice uses the agreed-upon math to combine the public base with her private key $x$, creating her **Public Key**. Bob does the same with his private key $y$ to create his **Public Key**.
    4. **The Exchange:** Alice and Bob send their Public Keys to each other across the open internet. The hacker intercepts both Public Keys.
    5. **The Magic (Associativity):** The core brilliance of Diffie-Hellman is the associative property of the underlying math.
        - Alice takes Bob's Public Key and mathematically combines it with her Private Key ($x$).
        - Bob takes Alice's Public Key and mathematically combines it with his Private Key ($y$).
        - Because of how the math works—e.g., $(g^y)^x = (g^x)^y = g^{xy}$—**both Alice and Bob arrive at the exact same final value.**
- **The Result:** That final shared value becomes the symmetric encryption key. Even though the hacker saw the public bases and intercepted both Public Keys in transit, they cannot combine the two Public Keys to find the final value. Because the mathematical trapdoors (curves or primes) prevent the hacker from reverse-engineering either of the private keys ($x$ or $y$), the shared symmetric key is perfectly secure.
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
