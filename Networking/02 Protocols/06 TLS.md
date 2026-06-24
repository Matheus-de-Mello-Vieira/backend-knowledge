# Transport Layer Security (TLS)

- **Definition:** TLS stands for Transport Layer Security.    
- **The OSI Debate:** The exact layer TLS occupies in the OSI model is arguable. Some classify it as Layer 5 (Session) because it establishes a stateful connection. Others align it closer to Layer 4 (Transport) because it strictly follows the TCP handshake, while practically, it acts as a secure wrapper for Layer 7 application protocols (e.g., securing HTTP to create HTTPS).
- **The Goal:** During the TLS handshake, both endpoints securely negotiate and agree upon the exact same shared key so they can encrypt all subsequent messages.

> **Note on Cryptography:** TLS relies heavily on Symmetric/Asymmetric encryption and Public Key Infrastructure (PKI). For the mathematical theory behind these algorithms and how Trust Chains work, see [Cryptography](https://www.google.com/search?q=../../Security/03%2520Cryptography%2520and%2520Data%2520Protection/01%2520Cryptography.md).

## Why TLS Requires Two Types of Cryptography

- **Symmetric for Payload (Speed):** We encrypt the actual data payloads with symmetric key algorithms because they are vastly faster than asymmetric ones. Symmetric encryption often relies on highly efficient bit-wise operations (like `XOR`) between the content and the key, whereas asymmetric encryption requires computationally expensive, exponential mathematics.
- **Asymmetric for Key Exchange (Security):** To use symmetric encryption, both the client and the server must know the exact same key. TLS uses asymmetric cryptography (Public Key Infrastructure) specifically to securely exchange this key over an open network. Therefore, two separate encryption algorithms are in play: one to safely exchange the key, and a faster one to encrypt the actual data.
- **Additional Features:** Beyond encryption, TLS authenticates the server's identity and supports advanced extensions like SNI (Server Name Indication), pre-shared keys, and 0-RTT (Zero Round Trip Time).

## TLS Versions & Key Exchange Mechanisms

### TLS 1.2 (The RSA Key Exchange)

In legacy TLS 1.2 configurations, the server relies on a static pair of public and private keys for the handshake.

1. The client initiates the connection by sending a "hello" message.
2. The server responds with its public key, which is cryptographically wrapped inside a Certificate. This certificate guarantees the server's identity and prevents attackers from intercepting the traffic and substituting their own public key.
3. The client uses the server's public key to encrypt the mathematical material needed to generate the symmetric key, and sends this payload to the server.
4. The server uses its closely guarded private key to decrypt the payload and derive the symmetric key.
5. The server confirms the exchange, and actual data encryption begins.

**The Vulnerability (Lack of Forward Secrecy):** The major flaw in the RSA model is that the server's private key rarely changes. Because many servers (or hostile actors) store network transactions, the encrypted data remains vulnerable indefinitely. If the server's static private key is ever leaked in the future (e.g., through a library bug), an attacker can retroactively decrypt years of recorded past traffic. While changing the private key regularly lessens the harm, it remains a structural weakness.

### Diffie-Hellman (Solving the RSA Problem)

To solve the retroactive decryption problem, the Diffie-Hellman algorithm allows both sides to mathematically derive a shared symmetric key without ever actually transmitting the final key itself.

- Both sides agree on a public key base and modulus, while keeping their own generated private keys secret.
- **The Math:** They combine the public components with their secret private key. Because this combination utilizes discrete logarithms—e.g., $g^x \pmod{n}$, where $g$ and $n$ come from the public key and $x$ is the private key—the resulting value is mathematically "unbreakable" and entirely safe to share over the network.
- The other side does the exact same process with their private key $y$, yielding $g^y \pmod{n}$, and sends it over.
- Because the combination algorithm is associative, when each side mathematically combines the received mixture with their own private key, they both arrive at the exact same shared value: $(g^x \pmod{n})^y = (g^y \pmod{n})^x = g^{xy} \pmod{n}$.
- This resulting value is used as the symmetric key. Because no static master key was used to encrypt the exchange, past traffic cannot be decrypted even if a key is compromised later.

### TLS 1.3 (The Modern Standard)

TLS 1.3 drastically speeds up the connection by strictly using the Diffie-Hellman algorithm and dropping the vulnerable RSA key exchange.

1. The client initiates the handshake and immediately sends its public key alongside the mathematical combination of its private key and the public key (its Diffie-Hellman share).
2. The server receives this, combines the client's mixture with its own private key, and instantly derives the symmetric key.
3. The server then sends back its own combination (its share) and its Certificate, proving its identity to prevent interception.
4. The client receives the server's share, combines it with its private key, and derives the exact same symmetric key.
### Perfect Forward Secrecy (PFS)

Perfect Forward Secrecy (often simply called Forward Secrecy) is a cryptographic feature designed to ensure that even if a server's long-term master private key is compromised in the future, past encrypted communications remain entirely secure.
    
- **The RSA Failure:** As noted in the TLS 1.2 section, traditional RSA key exchange inherently lacks PFS. Because the same static private key is used to negotiate the symmetric key for every session, a future key leak allows attackers to retroactively decrypt years of recorded historical traffic.
- **The Ephemeral Solution (DHE / ECDHE):** PFS is achieved by generating unique, temporary (ephemeral) session keys for every single connection. Modern TLS implementations achieve this using **Ephemeral Diffie-Hellman (DHE)** or **Elliptic Curve Ephemeral Diffie-Hellman (ECDHE)**.
- **How It Works:**
	* Instead of relying on the server's static private key to establish the symmetric key, both the client and server generate brand new, disposable Diffie-Hellman private variables for that specific handshake.
    - The server's master private key is still used, but _only_ to digitally sign the exchange (proving the server's identity), not to encrypt the data.
    - Once the session ends, both the client and the server completely destroy and discard those temporary Diffie-Hellman variables from their memory.
- **The Result:** If a hacker records your encrypted network traffic today and somehow steals the server's master private key five years from now, the stolen key is completely useless for decryption. The specific, temporary keys used to encrypt that historical session no longer exist anywhere in the world.