# Cryptography

Cryptography is the discipline of using mathematical transformations to control who can read data, who can prove authorship, and who can detect tampering. It does not protect information by hiding that communication exists; it protects information by making the captured bytes useless without the right key or verification material.

This matters because modern systems constantly move sensitive state through hostile or semi-trusted environments: browsers talk to servers over public networks, laptops store business data that can be stolen, APIs must prove who sent a request, and services need to trust keys they did not generate locally. Cryptography exists because access control alone is not enough once the data leaves the immediate boundary of a trusted process.

A useful mental model is that cryptography turns raw data into a format whose meaning depends on controlled secrets and controlled verification rules. The data may still be copied, forwarded, intercepted, stored, or replayed, but those actions no longer automatically reveal or legitimize the original information.

## What Cryptography Protects

Cryptography is one of the main tools behind several security goals:

- **Confidentiality:** Unauthorized parties should not be able to read the data.
- **Integrity:** Unauthorized changes should be detectable.
- **Authenticity:** A verifier should be able to check who produced the message or whether the sender possessed the required secret.
- **Non-repudiation:** In some asymmetric systems, a signer cannot easily deny authorship later.

It is important to separate these goals because different cryptographic mechanisms solve different parts of the problem. Encryption protects confidentiality, but it does not automatically prove authorship. A signature proves origin and integrity, but it does not hide the content.

## Core Mental Model

At the minimum, a cryptographic system has four moving parts:

- **Plaintext:** The original readable data.
- **Algorithm:** The transformation rule applied to the data.
- **Key:** The secret, shared secret, or public/private key material that controls the transformation.
- **Protected output:** The resulting ciphertext, digest, signature, or authentication tag.

The key is usually the real control point. A strong algorithm with exposed or poorly managed keys is not meaningfully secure, while a well-chosen algorithm with disciplined key handling can remain useful even in very exposed environments.

Cryptography is also different from **steganography**:

- **Cryptography:** Hides the meaning of the message.
- **Steganography:** Hides the existence of the message.

## Main Cryptographic Jobs

Cryptography is not a single mechanism. It is a family of mechanisms created in response to different constraints.

### Encryption

Encryption exists when authorized parties must recover the original plaintext later.

- **Symmetric encryption:** The same secret key encrypts and decrypts the data. This is efficient enough for disks, databases, files, and ongoing traffic.
- **Asymmetric encryption:** A public/private key pair separates roles such as encryption, decryption, signing, and verification. This is slower, but it solves trust-distribution and key-establishment problems that symmetric encryption alone cannot solve.

The deeper explanation of algorithm families, hybrid encryption, and data-in-transit versus data-at-rest protection lives in [Encryption](02%20Encryption.md).

### Hashing and message authentication

Hashing exists when the system needs a deterministic fingerprint of data rather than a recoverable encrypted copy.

- **Hash functions:** Turn variable-size input into a fixed-size digest for comparison, integrity checking, or higher-level protocol building.
- **HMAC (Hash-based Message Authentication Code):** Adds a shared secret to the hashing process so the verifier can detect tampering and also verify that the sender knew the secret.

This is why password storage uses [hashing rather than reversible encryption](03%20Hashing%20and%20Password%20Storage.md): the system only needs to verify a later guess, not recover the original password itself.

### Digital signatures

Digital signatures exist when the verifier must check who produced a message and whether the message changed after signing.

The usual flow is:

1. The sender computes a digest of the message.
2. The sender signs that digest with a private key.
3. The receiver verifies the signature with the sender's public key.

That design is useful because signing a digest is cheaper and more structured than signing arbitrary large messages directly. The signature does not hide the content; it binds authorship and integrity to the content.

### Key exchange and trust establishment

Cryptographic systems need ways to agree on secrets and ways to trust public keys.

- **Key exchange:** Lets two parties derive or establish shared secret material without sending that secret directly in the clear.
- **Certificates and PKI:** Bind public keys to identities so a verifier can decide whether a key really belongs to a given server, service, device, or person.

The [trust chain and certificate model](04%20Digital%20Certificates%20and%20PKI.md) determine whether a public key can be trusted.

## Why Modern Systems Combine Multiple Mechanisms

Real systems almost never rely on just one primitive because the pressures conflict:

- Bulk traffic needs **speed**.
- Internet-scale trust needs **identity binding**.
- Password verification needs **one-way comparison**.
- Long-lived deployments need **rotation and recovery**.

That is why modern designs are usually hybrid:

1. An asymmetric mechanism authenticates parties or helps establish trust.
2. A shared secret or session key is derived.
3. Symmetric encryption protects the actual data efficiently.
4. Separate hashing or signature mechanisms prove integrity or authorship where needed.

Cryptography therefore behaves less like one lock and more like a toolkit whose pieces are assembled according to the shape of the threat.

## Where Cryptography Fails in Practice

Cryptography is often attacked through the surrounding system rather than through the math itself.

- **Weak key management:** Leaked, lost, reused, or badly generated keys collapse the protection.
- **Wrong primitive for the job:** Fast hashes are poor password hashers; confidentiality tools do not automatically provide authenticity.
- **Implementation mistakes:** Invented constructions, unsafe defaults, truncation issues, or skipped validation steps can break an otherwise sound design.
- **Live-system exposure:** Encryption at rest does not stop malware running on a legitimately unlocked machine from reading the plaintext through normal process access.
- **Trust failures:** A public key is not useful if the receiver cannot verify whose key it is.

This is why cryptography cannot be separated from operations. Key generation, storage, rotation, recovery, and revocation are part of the [key management lifecycle](Key%20Management%20Lifecycle.md), not later administrative details.

## Practical Boundaries

Cryptography is powerful, but it does not replace every other control:

- It does not guarantee **availability**.
- It does not replace **authorization**.
- It does not eliminate the need for **backups**, **filesystem controls**, or **data-loss prevention**.
- It does not automatically make a compromised application trustworthy.

Instead, cryptography narrows what an attacker can do with captured data or forged messages. The rest of the security architecture decides whether the system can use that advantage correctly.