# Cryptography and Data Protection

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

This is the most fundamental distinction in Information Security. 

| **Feature** | **Symmetric Encryption** | **Asymmetric Encryption** |
| ------------ | ------------------------------------------- | ------------------------------------------------------------ |
| **Keys** | One shared secret key used for both encryption and decryption. | A pair of keys: a **Public Key** (widely distributed) and a **Private Key** (kept secret). |
| **Speed** | Very fast and highly effective. | Slower (computationally expensive). |
| **Security** | Less secure, as the key must be shared between parties, increasing the risk of compromise. | More secure, as the private key never needs to be shared. |
| **Use Case** | **Data at Rest** (Hard drives, databases). | **Key Exchange**, SSL/TLS, and Digital Signatures. |
| **Analogy** | A safe with one key that both parties have. | A mailbox where anyone can drop a letter (Public), but only you can open it (Private). |

> **Tech Note:** In the real world, we use **Hybrid Encryption**. We use Asymmetric encryption to securely exchange a secret key, and then use Symmetric encryption for the actual communication because it is much faster.

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

## 6. Digital Certificates

A digital certificate is an electronic document containing identity information about a person, company, or institution. It functions as an electronic ID card, allowing for secure digital transactions, user authentication in systems, electronic signing of documents, and sending encrypted messages.

* **Certificate Authority (CA):** Certificates are issued by a trusted Certificate Authority, which attests to the authenticity of the holder's identity through a digital signature. 
* **The Issuance Process:** The CA rigorously verifies the identity of the applicant using personal identification documents and proof of address. Once verified, the CA issues the digital certificate.
* **Storage:** Certificates can be stored on physical devices (like USB tokens or smart cards) or installed directly onto a computer.
* **Use Cases:** Widely adopted in e-commerce, banking, e-government, and healthcare to guarantee data authenticity and integrity.