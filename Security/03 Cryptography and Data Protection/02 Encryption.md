# Encryption

Encryption converts readable data into ciphertext so unauthorized parties cannot understand it. The protected output is still visible, transferable, and storable; what changes is that the meaning becomes unavailable without the right key.

This exists because networks, disks, cloud services, and endpoints are all places where attackers may observe or steal data. Encryption answers that pressure by making exposure alone insufficient. A packet sniffer, a stolen laptop, or a copied database is far less useful when the attacker cannot turn the captured bytes back into the original message.

The central design split is between **symmetric encryption**, which is fast and good at protecting large volumes of data, and **asymmetric encryption**, which is slower but solves trust and key-distribution problems. Modern systems usually combine both.

## Core Concepts

Cryptography and steganography solve different problems:

- **Cryptography:** Hides the meaning of the message.
- **Steganography:** Hides the existence of the message.

Every encryption flow starts from the same basic model:

- **Plaintext:** The original data.
- **Algorithm:** The mathematical transformation.
- **Key:** The secret or key pair that controls the transformation.
- **Ciphertext:** The protected output.

The algorithm matters, but operational security often collapses around the key. A strong cipher with weak key handling becomes an expensive illusion.

## Symmetric and Asymmetric Encryption

Symmetric and asymmetric systems were shaped by different constraints.

- **Symmetric encryption** exists because bulk data protection must be fast enough for disks, databases, and live traffic.
- **Asymmetric encryption** exists because sharing one secret with every participant does not scale well when the parties have never met or need identity proof.

### Symmetric encryption

Symmetric encryption uses the **same secret key** for encryption and decryption.

- **Why it matters:** It is computationally efficient and therefore suitable for large files, storage encryption, and session traffic.
- **Constraint:** Everyone who needs to decrypt must somehow obtain the same secret key securely.
- **Failure mode:** If the shared key leaks, every ciphertext protected by that key becomes readable.

Common symmetric algorithms:

- **AES (Advanced Encryption Standard):** The standard choice for many systems, especially when hardware acceleration such as AES-NI is available.
- **ChaCha20:** Often attractive on mobile or IoT hardware where AES acceleration may be absent.
- **DES / 3DES:** Historical algorithms kept mainly for context; DES is insecure and 3DES has largely been replaced.

### Asymmetric encryption

Asymmetric encryption uses a **public/private key pair**.

- **Public key:** Safe to distribute widely.
- **Private key:** Must remain secret to its owner.

This separation changes what the system can prove and what problem it can solve operationally:

- **Encrypt with the recipient's public key:** Only the matching private key can decrypt, so the goal is confidentiality.
- **Sign with the sender's private key:** Anyone with the public key can verify the signature, so the goal is authenticity, integrity, and often non-repudiation.

The important boundary is that asymmetric cryptography is often **part of a secure-channel setup**, not the mechanism that carries the full application payload for the rest of the session.

- **Why that distinction matters:** A reader might infer that HTTPS or TLS keeps using public-key operations on every message. In practice, modern secure transports use asymmetric cryptography mainly to authenticate parties, validate certificates, sign handshake data, or establish shared secret material.
- **What follows from that design:** Once the handshake finishes, the connection usually switches to symmetric encryption for the actual traffic because symmetric ciphers are much faster.

Common asymmetric algorithm families:

- **[RSA](06%20TLS.md#TLS%201.2%20(The%20RSA%20Key%20Exchange)):** Traditionally used for encryption and signatures; security depends on the difficulty of factoring large integers.
- **[Elliptic Curve Cryptography (ECC)](06%20TLS.md#Elliptic%20Curve%20Cryptography%20(ECC)):** Provides comparable security with much smaller keys, which reduces bandwidth and CPU pressure.
- **[Diffie-Hellman (DH)](06%20TLS.md#The%20Diffie-Hellman%20Key%20Exchange):** Used to establish a shared secret over an insecure channel rather than to encrypt bulk data directly. 

TLS is a good example of this division of labor:

- **Certificates and signatures:** The server proves identity using certificate-backed public-key cryptography.
- **Key establishment:** Modern TLS commonly uses ephemeral Diffie-Hellman, often elliptic-curve variants, to derive shared session secrets.
- **Bulk protection afterward:** The negotiated symmetric keys protect the actual application data.


## Hybrid Encryption

Modern secure communication usually follows a hybrid pattern because neither model solves every problem well on its own.

1. The two parties use an asymmetric mechanism to authenticate, exchange public keys, or derive a shared secret.
2. They derive or exchange a symmetric session key.
3. They use the symmetric key to encrypt the actual application data.
4. They rotate or discard the session key when the session ends.

**Why the split exists:** Asymmetric operations are relatively expensive, while symmetric operations are fast enough to protect large streams of data continuously.

One of the clearest real-world examples is [TLS](../../Networking/02%20Protocols/06%20TLS.md): public-key cryptography authenticates the peer and helps establish shared secret material, then symmetric ciphers protect the rest of the connection.

## Encryption States

The same cryptographic primitive behaves differently depending on where the data sits in the system.

### Encryption in transit

Encryption in transit protects data moving across a network, such as browser-to-server traffic over TLS.

- **Problem:** Intermediaries can observe or tamper with packets.
- **Mechanism:** The communicating parties establish shared cryptographic state before sending the protected payload.
- **Practical consequence:** Sniffing the network should not reveal the plaintext if the handshake and certificate validation succeed.

### Encryption at rest

Encryption at rest protects stored data such as disks, databases, backups, and individual files.

- **Problem:** Attackers may steal storage media, copy database files, or gain offline access to a device.
- **Mechanism:** The stored bytes remain encrypted until an authorized component with the right key decrypts them.
- **Practical consequence:** Physical theft and offline disk access become less useful to the attacker, though a live compromised system may still access the decrypted data.

[Storage-layer controls around permissions, backups, and operational handling](File%20and%20Filesystem%20Security.md) still matter alongside encryption at rest.

### End-to-end encryption

End-to-end encryption (E2EE) is stronger than ordinary transport encryption because the service in the middle is not supposed to hold the plaintext.

- **Problem:** A provider may forward messages correctly while still being able to read them.
- **Mechanism:** The sender encrypts to the recipient's key before the provider handles the message.
- **Practical consequence:** The provider can relay ciphertext without gaining the power to read message contents.

## Trade-offs and Failure Modes

Encryption is powerful but narrow. It solves some problems directly and leaves others untouched.

- **Encryption does not guarantee availability:** A perfectly encrypted service can still be offline or blocked by a firewall policy.
- **Encryption does not replace authentication:** Confidential transport does not prove the remote party is authorized unless the surrounding protocol validates identity properly.
- **Encryption does not fix key mismanagement:** Lost, leaked, or weakly generated keys defeat the whole design.
- **Encryption at rest does not fully protect a live compromised host:** If malware gains access after the system decrypts the data legitimately, the attacker can often read the plaintext through the running process.

[Identity binding](04%20Digital%20Certificates%20and%20PKI.md) and [key handling](Key%20Management%20Lifecycle.md) remain separate responsibilities around any encryption system.
