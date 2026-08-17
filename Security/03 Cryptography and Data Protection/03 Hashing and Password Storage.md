# Hashing and Password Storage

A hash function maps input data to a fixed-size digest. Unlike encryption, the goal is not to recover the original message later; the goal is to generate a compact fingerprint that can be recomputed and compared.

That design is useful for integrity checks, signatures, message authentication, and password verification. It also creates a frequent source of confusion: if a team stores password hashes, the system is not supposed to decrypt them later. Verification works by recomputing the same function on the login attempt and checking whether the digest matches.

Hashing becomes dangerous when people reuse the wrong kind of hash for the wrong job. Fast general-purpose hashes are good for integrity and protocol building, but they are the wrong tool for password storage because attackers can test guesses too cheaply.

## Hashing vs. Encryption

Hashing and encryption answer different security questions.

- **Encryption:** "How can authorized parties recover the original plaintext later?"
- **Hashing:** "How can the system recognize or verify data later without storing the original value in recoverable form?"

A useful mental model is the difference between a **locked box** and a **fingerprint**:

- A locked box hides the original item but lets the owner open it with the key.
- A fingerprint helps recognize whether two things are the same, but it is not meant to reconstruct the original object.

## Hash Properties and Common Uses

Strong hash functions are designed so that:

- The same input always produces the same output.
- Small changes in input produce very different outputs.
- Finding two inputs with the same output should be difficult in practice.
- Reconstructing the original input from the digest alone should be infeasible for real-world attack budgets.

Because hashes produce fixed-size outputs, collisions are theoretically unavoidable. The security question is not whether collisions can exist in the abstract, but whether an attacker can find them cheaply enough to exploit them.

Common uses include:

- **Integrity verification:** Compare the hash of a received file to the expected digest.
- **Digital signatures:** Sign the hash of a message instead of the whole message directly.
- **Message authentication:** Combine a hash with a secret key via HMAC.
- **Password verification:** Store a slow password hash instead of storing the password itself.

## Common Hash Algorithms

Hash selection depends on the job. In this context, the main distinction is between **obsolete hashes** that should no longer be trusted for security-sensitive collision resistance and **modern general-purpose hashes** that remain useful for integrity checks, signatures, and keyed constructions such as HMAC.

### Obsolete or broken for collision resistance

- **MD5:** Cryptographically broken and unsuitable for new security-sensitive uses.
- **SHA-1:** Also broken for collision resistance and deprecated for signatures and certificates.

### Stronger general-purpose hash families

These algorithms are common building blocks for integrity checks, digital signatures, HMAC, and other protocol mechanisms where fast deterministic hashing is useful.

- **SHA-256:** Common choice for integrity verification, signatures, and many protocol constructions.
- **SHA-512:** Larger output and often strong performance on 64-bit systems.
- **SHA-3:** Built on a different internal construction from SHA-2, providing algorithmic diversity.

> [!note] Hash choice depends on context
> A strong general-purpose hash is not automatically a good password hasher. Password storage belongs to a different design problem with different algorithms and cost goals.

## Keyed-Hashing: HMAC

A plain hash can prove that two copies of data are identical, but it cannot prove who generated the hash because anyone can hash public data. **HMAC** (Hash-based Message Authentication Code) adds a shared secret key so only parties with that key can create or verify the authentication tag correctly.

### Why HMAC exists

- **Problem:** Integrity alone does not prevent an attacker from recomputing a fresh hash after tampering with a message.
- **Mechanism:** HMAC mixes the message with a secret key and a standard hash function such as SHA-256.
- **Result:** A verifier who knows the same secret can detect both modification and forgery.

### Typical uses

- **API request signing:** The client signs the HTTP method, URI, timestamp, headers, or body.
- **Token signatures:** Some token formats use HMAC to prove the issuer signed the claims.
- **Internal service authentication:** Two trusted services share a secret and authenticate messages without exposing the secret itself on the wire.

### Practical consequence

HMAC is about **integrity + authenticity**, not confidentiality. It proves that the message came from someone who knows the secret and that the signed fields were not altered after signing.

A [protocol-oriented example](../02%20Identity%20and%20Access/01%20Authentication.md#HMAC) appears in authentication flows that use HMAC.

## Password Hashing Threat Model

Password storage is shaped by one hard fact: people choose weak, reusable, predictable passwords. If the database leaks, the attacker can work offline and test guesses as quickly as the stored format allows.

The defender's goal is therefore not to make guessing mathematically impossible. The goal is to make every guess expensive, isolated, and difficult to reuse across accounts.

### What the system must store

A password-verification system needs enough state to replay the same check later without storing the password itself.

1. The user chooses a password.
2. The system generates a random salt.
3. The system runs a password-hashing algorithm with the password, the salt, and cost parameters.
4. The system stores the resulting digest together with the salt and the cost configuration.
5. At login time, the system recomputes the same algorithm on the submitted password and compares the result.

The password is never decrypted. Verification succeeds because the function is deterministic when given the same password, salt, and parameters.

### Slow hashing

Password storage is a different problem from file integrity or message signing. A login system does not need to hash billions of candidate passwords cheaply; it needs to make each password guess costly when an attacker steals the database and starts guessing offline.

That requirement changes the algorithm choice completely. General-purpose hashes such as MD5, SHA-1, SHA-256, and SHA-512 were built to be fast, so they are the wrong tool for password storage even when the hash itself is still cryptographically strong for other jobs.

A **password hashing algorithm** intentionally consumes noticeable CPU time, memory, or both for every guess.

- **`bcrypt`:** CPU-hard with a tunable work factor.
- **`scrypt`:** Adds significant memory pressure, making parallel cracking hardware less efficient.
- **`Argon2`:** Modern design with tunable time, memory, and parallelism parameters.
- **`PBKDF2`:** Widely supported and tunable, but more GPU-friendly than memory-hard designs.

The trade-off is intentional:

- **Defenders:** Pay the cost during registration and login.
- **Attackers:** Must pay roughly that cost for every offline guess.

### Dictionary attacks

A dictionary attack targets the part of the problem humans make easy: password choice. Instead of exploring the full password space, the attacker tests a curated list of likely guesses such as common passwords, leaked credentials, names, keyboard patterns, and predictable substitutions.

- **How it works:** During the attack, the software takes a word from the list, hashes it, and checks if it matches the stolen hash. If it fails, it moves to the next word.
- **The Math:** The hashing is usually calculated dynamically, right then and there.
- **The Scope:** It only checks likely, human-created inputs. If a password is `Tr0ub4dor&3`, a dictionary attack will likely miss it because it isn't in the word list.

### Rainbow table attacks

A rainbow table attack targets fast, unsalted password storage from a different angle. Instead of hashing each guess during the breach, the attacker reuses a large precomputed structure that maps many possible passwords to their corresponding hashes.

- **How it works:** Instead of calculating hashes during the attack, the attacker uses a massive, pre-generated file that contains the hashes for _every possible combination_ of characters up to a certain length (e.g., every possible 1-to-8 character password, whether it's an English word or gibberish like `xQ9$bZ`).    
- **The Scope:** It is extremely fast and will crack complex, random passwords, but it is limited by length. If the table was only built for up to 8 characters, a 9-character password is completely safe from it.
- **The Math:** To avoid taking up petabytes of hard drive space, a rainbow table doesn't just store a flat list of `plain-text = hash`. Instead, it compresses the data using mathematical "chains."
	- It hashes a starting password, then uses a "reduction function" to scramble that hash back into a new, random plaintext password, hashes _that_, reduces it again, and repeats this thousands of times.
	- The table saves space by only storing the very first password and the very final hash of the chain.
	- To prevent different chains from accidentally generating the same intermediate password and merging together (which would waste space), the algorithm uses a _different_ reduction function for every single step in the chain. This sequence of constantly changing functions—step 1, step 2, step 3—is the "spectrum" or "rainbow" of colors that gives the technique its name.

### Salting

A **salt** is a unique random value generated per password and stored alongside the resulting hash.

#### Why salting matters

- **Without salt:** One precomputed strategy can attack every record using the same hash format.
- **With salt:** Each account becomes a separate cracking problem because the attacker must include that account's salt in every guess.

The salt does not need to be secret. Its job is not secrecy; its job is to destroy cross-account reuse of the same cracking work.

#### Salt length and collision pressure

If salts were short, many users would eventually share the same salt, which would let the attacker attack those users in batches again. Long salts prevent that grouping effect.

The current notes use **128-bit salts** as the practical example. That space is so large that even enormous user populations are extraordinarily unlikely to collide, which keeps each account isolated.

### Pepper

A **pepper** is an additional secret used during password hashing but stored outside the database, such as in application configuration, a secret manager, or a hardware security module.

#### What problem peppering changes

- **Database-only breach:** The attacker gets salts and password hashes, but not the extra secret.
- **Database + secret-store breach:** The pepper no longer helps, and the attacker falls back to ordinary offline guessing against the password hashes.

Peppering is therefore a defense-in-depth measure, not a replacement for salts or slow password hashing.

#### Operational trade-off

If the organization loses the pepper and has no recovery path, it can no longer verify anyone's password. Peppering shifts part of the risk from database theft to secret-management reliability.

### Implementations of Salt and Pepper

#### Why naive concatenation is risky

A construction such as `hash(pepper + password + salt)` looks simple but creates avoidable problems.

- **Length-extension risk:** Some ordinary hash constructions do not make naive secret-prefix hashing safe.
- **Algorithm input limits:** `bcrypt` truncates long inputs, so prepending a pepper can silently discard part of the user's password.
- **Boundary ambiguity:** Simple concatenation can blur where one field ends and another begins.

#### Post-Hash Encryption Pattern

Here is an example formula representing the post-hash encryption pattern:

`AES_GCM(key=pepper, plaintext=bcrypt(password, salt))`

In this approach, the system first hashes the user's password using a standard algorithm like `bcrypt`. Then, it treats that resulting hash string as plain text and encrypts it using a robust symmetric encryption algorithm (such as AES-256-GCM) before storing it in the database. The `external_key` acts as a pepper and is managed securely in a Key Management Service (KMS) or Hardware Security Module (HSM), completely separate from the database.

**Pros of Post-Hash Encryption:**

- **Seamless Key Rotation:** Because the outer layer is standard two-way encryption, you can decrypt the hashes and re-encrypt them with a new key at any time without needing the user's plain text password.
- **Database Isolation:** If an attacker breaches the database, they only acquire encrypted blobs. Without the external key, they cannot begin an offline guessing attack because they cannot access the underlying `bcrypt` hashes.

**Cons of Post-Hash Encryption:**

- **Algorithm Input Limits:** Because `bcrypt` is applied directly to the password first, this pattern does not solve `bcrypt`'s known structural limitation where it truncates any password longer than 72 bytes.

#### Pre-Hash HMAC Pattern

The formula `bcrypt(HMAC(key=pepper, message=password), salt)` represents a highly secure method for preparing passwords before they are stored.

Instead of hashing the plain text password directly, the application first computes an HMAC (Hash-based Message Authentication Code, typically using SHA-256) of the user's password. It combines the password with a secret cryptographic key (the "pepper"). This pepper is kept strictly on the application server or in a KMS, never in the database. The resulting HMAC string is then passed into `bcrypt` alongside a uniquely generated `salt` to create the final record stored in the database.

**Pros of Pre-Hash HMAC:**

- **Bypasses bcrypt length limits:** By using HMAC-SHA256 first, the input to `bcrypt` is always normalized to a fixed, safe size (32 bytes). This completely avoids the `bcrypt` 72-byte truncation issue, allowing users to safely use passphrases of any length.
- **Neutralizes database leaks:** Just like post-hash encryption, if an attacker breaches the database, they only acquire the hashes. Because they do not have the pepper, they cannot generate the required HMAC input to mount an offline dictionary or brute-force attack.

**Cons of Pre-Hash HMAC:**

- **Complex Key Rotation:** Because the pepper is mixed in _before_ the irreversible `bcrypt` hash is applied, you cannot simply decrypt and update the database if the pepper needs to be rotated. You would have to retain the old pepper to verify existing users, wait for them to log in, and then re-hash their password with the new pepper upon a successful authentication.