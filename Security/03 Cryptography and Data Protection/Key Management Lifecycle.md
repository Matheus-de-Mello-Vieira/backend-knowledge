# Key Management Lifecycle

Cryptographic algorithms protect data only as long as the keys remain trustworthy. In real systems, key management is the operational discipline that decides whether encryption, signatures, and certificates remain useful after deployment.

This note focuses on the lifecycle of the key material itself: where it comes from, where it is stored, who controls it, how it moves, when it is replaced, and how it is retired. Those state transitions are usually the real bottleneck in cryptographic systems.

The hard constraint is simple: keys must be available to authorized processes when needed and unavailable to everyone else all the time. Meeting both goals simultaneously is what makes key management difficult.

## Key Generation

Security starts at generation time.

- **Entropy requirements:** Keys must come from cryptographically secure random number generators.
- **Key length choices:** Use contemporary length standards appropriate to the algorithm family.
- **High-assurance generation:** Sensitive environments may generate keys inside hardware security modules (HSMs) rather than in general-purpose application memory.
- **Initial distribution problem:** Even the first delivery of a key must already happen through a trusted path.

If the randomness is weak or predictable, every later control inherits that weakness.

## Key Storage and Protection

Stored keys are high-value targets because stealing one key can expose large volumes of protected data.

- **Access controls:** Limit which users, services, and systems can read or use the key.
- **Encryption at rest:** Protect stored keys with separate key-encryption keys (KEKs) or hardware-backed storage.
- **Physical security:** Sensitive key stores need host, device, and facility protections as well as logical protections.
- **Key escrow:** Some environments keep recoverable copies under strict controls to avoid irreversible data loss.

The core trade-off is that keys must be recoverable enough for operations but not so widely copied that compromise becomes easy.

## Key Distribution and Exchange

A key has no operational value until the right party can use it.

- **Key exchange protocols:** Mechanisms such as Diffie-Hellman help establish shared secrets without sending those secrets directly.
- **Certificate-based distribution:** PKI helps distribute trustworthy public keys at scale.
- **Key wrapping:** One key encrypts another key for transport or storage.
- **Out-of-band verification:** A separate trusted channel can confirm that the receiving party really obtained the intended key.

Distribution is often the point where a seemingly simple cryptographic design becomes a system-design problem.

## Key Usage and Monitoring

Once a key is active, the organization must control how and when it is used.

- **Usage policies:** Define which systems and operations may use the key.
- **Audit logging:** Record key use for monitoring, investigation, and compliance.
- **Separation of duties:** Spread sensitive operations across multiple people or systems to reduce insider risk.
- **Behavior monitoring:** Unusual usage volume or timing may indicate compromise.

## Key Rotation and Renewal

Keys should not remain valid forever.

- **Scheduled rotation:** Replace keys on a fixed schedule or according to policy.
- **Emergency rotation:** Replace keys immediately when compromise is suspected.
- **Transition handling:** Keep enough compatibility to read old data or validate earlier signatures while moving new operations to fresh keys.

Rotation solves one problem by creating another: every dependent system must learn the new key without breaking availability.

## Key Revocation and Destruction

When a key should no longer be trusted, the system needs a clean termination path.

- **Revocation:** Mark the key or certificate as no longer valid.
- **Secure deletion:** Destroy stored key material so it cannot be recovered later.
- **Audit trail:** Preserve evidence that revocation or destruction actually happened.

In PKI environments, certificate revocation lists (CRLs) and similar mechanisms help distribute that invalidation state.

## Backup and Recovery

Key backup is different from ordinary data backup. Losing a business document is an availability problem; losing the only decryption key may make the protected data permanently unreadable.

- **Recovery procedures:** Document how authorized staff recover lost or corrupted keys.
- **Split knowledge:** Divide recovery authority among multiple trusted individuals.
- **Geographic distribution:** Avoid storing every recovery copy in one physical location.
- **Regular testing:** A recovery plan that is never rehearsed may fail when the key is actually needed.

> [!warning] Key recovery changes the threat model
> Every backup copy or escrow path that improves recoverability also creates another place an attacker may try to steal the key. Recovery planning must therefore be protected as carefully as primary key storage.

## Compliance and Governance

Cryptographic state is often subject to policy, audit, and external requirements.

- **Policy framework:** Define who owns the keys, who approves their use, and how incidents are escalated.
- **Regulatory alignment:** Some environments must satisfy standards or industry mandates for handling key material.
- **Training and awareness:** People who operate the system need to understand both the mechanism and the failure modes.
- **Risk assessment:** Revisit the design when infrastructure, personnel, or threat models change.

Key management sits at the boundary between math and operations. Strong algorithms matter, but the surrounding lifecycle usually determines whether the system stays secure under real administrative pressure.
