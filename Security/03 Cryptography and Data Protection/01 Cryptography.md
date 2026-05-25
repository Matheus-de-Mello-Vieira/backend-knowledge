# Cryptography

## 1. Classic Cryptography and Core Concepts
At its simplest, cryptography is the science that studies techniques to transform data into codes that can only be deciphered by someone who possesses the correct access key. 

The word originates from Greek:
* **Kryptós (crypto):** secret.
* **gráphein (graphy):** writing.

### **Cryptography vs. Steganography:**
Cryptography involves more elaborate techniques than steganography. In steganography, there is no data treatment; the goal is simply to hide the data so well that it cannot be found. Cryptography, on the other hand, does not worry about hiding the data. Instead, it transforms it so that even if it is found or intercepted, it cannot be deciphered without the key.

The true strength of cryptography lies entirely in the strength of its key. However, this is also its primary fragility: if the key is discovered, decryption becomes a simple process, revealing the information in its pure format.

### **The Components of Cryptography:**
* **Plaintext (Mensagem limpa):** The readable message before it is encrypted.
* **Cryptographic Technique:** The specific method or algorithm used to encrypt.
* **Key:** The agent utilized by the technique to encrypt and decrypt the data.
* **Ciphertext (Mensagem criptografada):** The encrypted, unreadable message sent from the sender to the receiver.

### **Historical vs. Computational Examples:**
* **Non-computational:** Writing, languages (understood only by those who know them), and the Enigma Machine.
* **Computational Algorithms:** Digital certification, DES (Data Encryption Standard), 3DES, and Blowfish.

## 2. Symmetric vs. Asymmetric Encryption

This is the most fundamental distinction in Information Security. In modern systems, we rarely choose just one; instead, we use a **Hybrid Encryption** approach. We use Asymmetric encryption to safely exchange a secret key across the network, and then use Symmetric encryption for the actual data transfer because it is significantly more efficient.

| **Feature**                | **Symmetric Encryption**                                     | **Asymmetric Encryption**                                    |
| -------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Keys**                   | Uses **one shared secret key** for both encryption and decryption. | Uses a **pair of keys**: one **Public** and one **Private**. |
| **Mathematical Mechanism** | Performs simple **bit-wise XOR operations** on the content and the key. | Relies on complex **exponential mathematical operations**.   |
| **Speed**                  | **Very fast** due to its low computational overhead.         | **Much slower** and more computationally expensive.          |
| **Security Foundation**    | Both client and server **must possess the exact same key**.  | Both parties can have their own unique public keys.          |
| **Key Generation**         | N/A                                                          | You can generate a public key using a private one, but you **cannot** derive a private key from a public one. |
| **Primary Use Case**       | **Data at Rest** (hard drives/databases) and bulk data transmission. | **Key Exchange**, SSL/TLS handshakes, and Digital Signatures. |

### **The Logic of Asymmetric Key Pairs**

The security goal of an asymmetric system changes depending on which key is used for encryption:

- **Encrypt with Public $\rightarrow$ Decrypt with Private:**
  -  **Goal:** Confidentiality and Receiver Authenticity.
  - **Logic:** Since only the owner of the Private Key can decrypt the message, the sender is guaranteed that only the intended authorized party can access the data.
- **Encrypt with Private $\rightarrow$ Decrypt with Public:**
  -  **Goal:** Sender Authenticity and Integrity (Digital Signature).
  - **Logic:** Since only the corresponding Public Key can decrypt it, the receiver is certain that only the owner of the Private Key could have signed the document. This ensures nobody has tampered with the content during transit.

### Common Encryption Algorithms

#### **Symmetric Algorithms**

- **AES (Advanced Encryption Standard):** The current global standard. **AES-256** is approved for top-secret data. It is incredibly fast on hardware with AES-NI acceleration.
- **ChaCha20:** A modern stream cipher that is often faster than AES on devices without hardware acceleration (mobile/IoT) and is highly resistant to certain side-channel attacks.
- **DES / 3DES:** Older computational algorithms. DES is insecure; 3DES is an evolution that applies DES three times but is mostly replaced by AES.

#### **Asymmetric Algorithms**

- **RSA:** Traditionally used for handshakes and digital signatures. It relies on the difficulty of factoring large prime numbers.
- **ECC (Elliptic Curve Cryptography):** A modern alternative to RSA. A 256-bit ECC key provides security equivalent to a 3072-bit RSA key, making it much more efficient for mobile devices and high-traffic servers.
- **Diffie-Hellman (DH):** A key exchange protocol where two parties establish a shared secret over an insecure channel using their own private keys and a common public key.

## 3. The States of Encryption
Data must be protected differently depending on its current state:

* **Encryption in Transit:** Protects data moving through a network (e.g., **TLS/SSL** for web traffic). This prevents eavesdropping and data tampering during transmission between a web browser and a server, and is also used in instant messaging and emails.
* **Encryption at Rest (File Encryption):** Protects data stored on physical media. File encryption encodes confidential information to protect it from unauthorized access using a secret key or encryption algorithm. Decoding the files can only be done with the correct key or password, making it a critical defense for privacy.
* **End-to-End Encryption (E2EE):** If Alice sends a message without E2EE, the middleman (Cloud) can read it. With E2EE, the communication is encrypted with Bob's Public Key on Alice's phone and can only be decrypted by Bob's Private Key on his laptop.

## 4. Hashing: The "One-Way" Trap

Many people confuse Hashing with Encryption, but they are **not** the same thing.

* **Encryption** is a two-way street (Plaintext <-> Ciphertext) designed to ensure **Confidentiality**.
* **Hashing** is a one-way mathematical function (Data -> Fingerprint) designed to ensure **Integrity** and authenticity. You cannot "un-hash" a value.

### **How Hash Algorithms Work:**
Math is closely related to cryptography. A hash algorithm converts input data of *variable* size into a *fixed-size* sequence of alphanumeric characters (often represented in hexadecimal), called a hash or digest. Didactically, it relates to basic mathematical functions (injective, surjective, and bijective).

* **Uniqueness:** The main property of a hash is that two different sets of input data will *always* generate different hash values. Furthermore, any minor alteration to the input data will produce a completely different hash value.
* **Data Verification:** When a large file is transmitted over the internet, the recipient can quickly and efficiently verify if the file was corrupted by comparing the hash of the downloaded file with the original hash provided by the sender.
* **Password Storage:** We encrypt messages, but we *hash* passwords. If a database leaks, attackers only see the hash fingerprints, not the actual passwords.

### **Common Hash Algorithms:**

#### **Obsolete/Vulnerable Algorithms**

These algorithms have been cryptographically broken due to collision vulnerabilities, meaning attackers can intentionally create two different inputs that produce the exact same hash output.

- **MD5 (Message Digest 5):**
  - **Background:** Created in 1991 by MIT Professor Ronald Rivest. It uses the Merkle-Damgård construction and produces a 128-bit (16-byte) hash value, which is typically represented as a sequence of 32 hexadecimal digits.
  - **Vulnerabilities:** MD5 is considered catastrophically vulnerable and cryptographically broken. Current collision-finding techniques are so advanced that an attacker can create two different files with the exact same prefix that generate identical MD5 checksums within seconds using off-the-shelf hardware.
  - **Impact:** In 2008, the CMU Software Engineering Institute formally concluded that MD5 was "unsuitable for further use". Its weaknesses were famously exploited in the wild by the Flame malware in 2012.
- **SHA-1 (Secure Hash Algorithm 1):**
  - **Background:** Designed by the United States National Security Agency (NSA) and released in 1995. It takes an input and produces a 160-bit (20-byte) hash value, usually rendered as 40 hexadecimal digits.
  - **Vulnerabilities:** Like MD5, SHA-1 is based on the Merkle-Damgård construction and is vulnerable to collision attacks. In 2017, researchers from Google and the CWI Institute demonstrated a practical collision attack (known as "SHAttered") by successfully generating two completely different PDF documents that produced the exact same SHA-1 hash value.
  - **Impact:** NIST formally deprecated the use of SHA-1 in 2011 and disallowed its use for digital signatures by the end of 2013. By 2017, all major web browser vendors ceased accepting SHA-1 SSL certificates.

#### **Strong/Recommended Algorithms**

These algorithms are currently considered highly secure, offering robust mathematical resistance against brute-force and collision attacks.

- **SHA-2 Family (SHA-256 and SHA-512):**
  - **SHA-256:** Generates a 256-bit hash. It is the industry standard for many applications, including modern SSL certificates, digital signatures, file integrity verification, and blockchain environments like Bitcoin. Architecturally, it generally performs more efficiently on 32-bit systems.
  - **SHA-512:** Generates a longer 512-bit hash. Because of its larger output space, brute-force collision finding becomes exponentially more difficult, making it a strong contender for systems handling extremely sensitive data. Furthermore, because it is designed to process 64-bit words natively, SHA-512 generally outperforms SHA-256 on 64-bit hardware architectures (which are standard in modern servers).
- **SHA-3:**
  - **Background:** Released by NIST on August 5, 2015, SHA-3 is the latest member of the Secure Hash Algorithm standard. It was developed by a team of researchers who designed the broader cryptographic primitive family known as Keccak.
  - **Architectural Difference:** Unlike MD5, SHA-1, and SHA-2, which rely on the older Merkle-Damgård construction, SHA-3 uses a unique mathematical approach called the "sponge construction".
  - **How it Works:** In the sponge construction, input data is "absorbed" into the system's state through XOR operations and block permutations, and then the final hash result is "squeezed" out.
  - **Purpose:** Because of the successful attacks on older algorithms, NIST selected SHA-3 to serve as a highly secure, structurally dissimilar alternative. This ensures that if a foundational flaw is ever discovered in the SHA-2 architecture, SHA-3 can be directly substituted into current applications to maintain security.

### Keyed-Hashing: HMAC

While a standard hash ensures **Integrity**, it does not prove **Authenticity** because anyone with the data can generate the same hash. To solve this, we use **HMAC** (Hash-based Message Authentication Code), which incorporates a **secret key** into the hashing process.

- **Mechanism:** HMAC combines a cryptographic hash function (like SHA-256) with a secret key known only to the sender and the receiver.
- **Security Tenets:** Unlike simple hashing, HMAC addresses both **Integrity** (the message hasn't changed) and **Authenticity** (the message must have come from someone with the secret key).
- **Use Case:** HMAC is commonly used in API authentication and **JSON Web Tokens (JWTs)**. Even if an attacker intercepts the message and modifies it, they cannot generate a valid HMAC to match the changes because they lack the secret key.
- **Comparison:**
  - **Standard Hash:** Integrity only (detects accidental corruption).
  - **HMAC:** Integrity + Authenticity (detects malicious tampering and verifies the sender).

## 5. Applications of Asymmetric Cryptography

In an asymmetric system (Public/Private key pair), the logic changes entirely depending on your security goal:

**A. For Confidentiality (Encryption)**
* **Action:** You encrypt data using the **recipient's Public Key**.
* **Result:** Only the recipient can decrypt it with their **Private Key**.
* **Goal:** Ensuring that only authorized parties can read the data.

**B. For Authenticity & Non-repudiation (Digital Signatures)**

* **Action:** You "encrypt" (sign) a hash of a message using **your own Private Key**.
* **Result:** Anyone can verify the signature using your **Public Key**.
* **Goal:** Proving that you are the true author (**Authenticity**) and providing undeniable proof of the transaction (**Non-repudiation**).

## 6. Digital Certificates and PKI

A primary challenge in secure communications is proving authenticity—for example, proving that a website name actually belongs to the legitimate owner. To solve this, we use Digital Certificates and a Public Key Infrastructure (PKI).

A digital certificate is an electronic document containing identity information about a person, company, or institution. It functions as an electronic ID card, allowing for secure digital transactions, user authentication in systems, electronic signing of documents, and sending encrypted messages. Today, the universal standard for these certificates is **X.509**.

### **The Certificate Creation Process**
The lifecycle of creating a trusted certificate generally follows these steps:
1. **Generate a Key Pair:** The applicant generates a pair of public and private keys.
2. **Identity Verification:** A trusted third party, known as a Certificate Authority (CA), rigorously verifies the identity of the applicant using personal identification documents and proof of address.
3. **Draft the Certificate:** The applicant's public key is placed into the certificate document along with their identity information.
4. **Sign the Certificate:** The CA signs the certificate using its own private key, officially attesting to the authenticity of the holder's identity.

### **The Trust Chain**
Certificates can sign "other certificates," which creates a hierarchical **Trust Chain**. Every certificate has an "Issuer Name" that dictates exactly who issued and signed it.

* **Root Certificates:** Ultimately, every trust chain leads back to a Root Certificate. Root certificates are always "self-signed" and are implicitly trusted by everyone.
* **Certificate Stores:** These trusted root certificates are pre-installed in a big list within the Operating System's root certificate store. However, some systems (like web browsers) maintain their own independent certificate stores so they do not have to rely solely on the OS's list.
* **Self-Signed Certificates (Untrusted):** Anyone can create a self-signed certificate (where the private key signing the cert belongs to the public key inside it). Unless it is a recognized Root Certificate, a self-signed certificate is usually untrusted by default and is primarily used only for local development or testing.

### **The Validation Process**
When a client (like a browser) receives a certificate, it must determine if it can trust it. It does this by evaluating the trust chain recursively:

```mermaid
flowchart LR
    A([Start: Receive Certificate]) --> B{Is the certificate<br>a Root?}
    B -- Yes --> C([Trusted!])
    B -- No --> D[Look for the certificate of<br>the issuer that signed it]
    D -. Repeats recursively .-> B
```

> **Network Engineering Note:** During a connection, servers will often send the **full chain** of certificates to the client. This is because clients might not have all the intermediate certificate authorities cached in their local store. By sending the full chain, the server ensures it can support more clients and establish trust seamlessly, even though it requires transferring slightly more data during the handshake.

## 7. Key Management Lifecycle

Effective cryptographic security depends not only on strong algorithms but also on proper management of cryptographic keys throughout their entire lifecycle. Poor key management can render even the strongest encryption useless.

### **Key Generation**
The foundation of cryptographic security begins with proper key generation:

- **Entropy Requirements:** Keys must be generated using cryptographically secure random number generators (CSRNGs) with sufficient entropy.
- **Key Length Standards:** Follow current industry standards for key lengths (e.g., AES-256, RSA-3072, ECC-256).
- **Hardware Security Modules (HSMs):** For high-security environments, key generation should occur within tamper-resistant hardware.
- **Initial Distribution:** Secure delivery of keys to authorized parties using out-of-band methods or pre-established secure channels.

### **Key Storage and Protection**
Protecting keys when not in active use is critical to maintaining security:

- **Key Escrow:** Secure backup of keys to prevent data loss while maintaining access controls.
- **Access Controls:** Strict authentication and authorization for key access, following the principle of least privilege.
- **Physical Security:** Secure storage locations with appropriate environmental and access controls.
- **Encryption at Rest:** Keys should be encrypted when stored, using separate key-encryption-keys (KEKs).

### **Key Distribution and Exchange**
Secure methods for sharing keys between authorized parties:

- **Key Exchange Protocols:** Use established protocols like Diffie-Hellman for secure key establishment.
- **Certificate-Based Distribution:** Leveraging PKI infrastructure for secure key distribution.
- **Key Wrapping:** Encrypting keys with other keys for secure transport and storage.
- **Out-of-Band Verification:** Confirming key integrity through separate communication channels.

### **Key Usage and Monitoring**
Proper management during the active use phase:

- **Usage Policies:** Clear policies defining when, how, and by whom keys may be used.
- **Audit Logging:** Comprehensive logging of all key usage activities for security monitoring and compliance.
- **Performance Monitoring:** Tracking key usage patterns to identify potential security issues or system problems.
- **Separation of Duties:** Multiple people required for sensitive key operations to prevent insider threats.

### **Key Rotation and Renewal**
Regular replacement of cryptographic keys to maintain security:

- **Rotation Schedules:** Predetermined schedules for key replacement based on security policies and risk assessment.
- **Automatic Rotation:** Automated systems that handle routine key rotation without service disruption.
- **Emergency Rotation:** Procedures for immediate key replacement in case of suspected compromise.
- **Backward Compatibility:** Managing transitions to new keys while maintaining access to data encrypted with old keys.

### **Key Revocation and Destruction**
Secure termination of key lifecycle:

- **Revocation Procedures:** Immediate invalidation of compromised or no-longer-needed keys.
- **Certificate Revocation Lists (CRLs):** Public lists of revoked certificates for PKI environments.
- **Secure Deletion:** Cryptographically secure methods for destroying key material to prevent recovery.
- **Audit Trails:** Maintaining records of key destruction for compliance and forensic purposes.

### **Backup and Recovery**
Ensuring business continuity while maintaining security:

- **Recovery Procedures:** Well-documented processes for key recovery in case of loss or corruption.
- **Split Knowledge:** Dividing key recovery authority among multiple trusted individuals.
- **Geographic Distribution:** Storing key backups in multiple secure locations to prevent single points of failure.
- **Regular Testing:** Periodic testing of backup and recovery procedures to ensure they work when needed.

### **Compliance and Governance**
Meeting regulatory and organizational requirements:

- **Policy Framework:** Comprehensive key management policies aligned with organizational security requirements.
- **Regulatory Compliance:** Adherence to industry standards (FIPS 140-2, Common Criteria) and regulatory requirements.
- **Risk Assessment:** Regular evaluation of key management risks and implementation of appropriate controls.
- **Training and Awareness:** Ensuring personnel understand their key management responsibilities and procedures.

Key management is often considered the most challenging aspect of implementing cryptographic solutions, requiring careful balance between security, usability, and operational requirements.

## Implementation Examples

Cryptographic concepts are implemented across different platforms and environments:

**Platform-Specific Implementations:**
- **Windows:** [BitLocker](Windows%20Security.md#BitLocker%20Drive%20Encryption%20Integration) - Windows encryption technologies and certificate management 
- **Linux:** [SSH and LUKS](../05%20Architecture%20and%20Infrastructure%20Security/Linux%20Endpoint%20Security.md#SSH%20%28Secure%20Shell%29%20Protection) - SSH key management and disk encryption
- **Cloud Services:** Cloud-native key management services and hardware security modules

**Authentication Integration:**
- [HMAC Authentication](../02%20Identity%20and%20Access/01%20Authentication.md#HMAC) - Using cryptographic signatures for API security
- [JWT Tokens](../02%20Identity%20and%20Access/01%20Authentication.md#JSON%20Web%20Tokens%20%28JWT%29) - Digital signatures for stateless authentication
- [Digital Certificates](../05%20Architecture%20and%20Infrastructure%20Security/02%20Endpoint%20Security.md) - PKI implementation in endpoint security

**Related Security Frameworks:**
- [Zero Trust Architecture](../02%20Identity%20and%20Access/03%20Zero%20Trust%20Architecture.md) - Identity-centric security requiring strong cryptographic foundations
